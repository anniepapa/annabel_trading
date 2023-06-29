from decimal import Decimal
from datetime import datetime, timedelta

import degiro_connector.core.helpers.pb_handler as payload_handler
from degiro_connector.trading.models.trading_pb2 import (  # noqa
    ProductSearch,
    ProductsInfo,
    Order,
)

from utils import BaseRequestOnDate
from my_logger import logger
from toolkits import decimalize, get_last_valuta_balance


class TradingOperator:
    __slots__ = (
        "trading_api",
        "order_created",
        "order_confirmed",
        # "config",
        # "client_details",
        "account_info",
        "prod_meta",
    )

    def __init__(self, trading_api=None):
        self.trading_api = trading_api

        self.order_created = False
        self.order_confirmed = False

        # self.config = self._get_config()
        # self.client_details = self._get_client_details()
        self.account_info = self._get_account_info()

        self.prod_meta = {}

    def initiate_prod_meta_from_str(self, keyword):
        """
        example: 'vOvlVO cAr'
        """
        request = ProductSearch.RequestLookup(
            search_text=keyword,
            limit=10,
            offset=0,
            product_type_id=1,
        )

        products = self.trading_api.product_search(request=request)
        prods = payload_handler.message_to_dict(message=products)["products"]
        prod = prods[0]

        if len(prods) > 1:
            logger.warning(
                f"{keyword} is not unique, multiple products are retrived"
            )

        self.prod_meta = {
            "name": prod["name"],
            "id": prod["id"],
            "vwd_id": prod["vwdId"],
            "stock_currency": prod["currency"],
            "close_price": prod["closePrice"],
            "close_price_date": prod["closePriceDate"],
            "trans_fee": Decimal(4.9),
            "last_balance": self._get_last_balance_via_account_overview(),
        }

        self.prod_meta.update({"fx_rate": self._get_fx_rate()})

    def make_an_order(self, product_id, price, size, action_type="B"):
        action = self._decide_action(action_type)

        order = Order(
            action=action,
            order_type=Order.OrderType.LIMIT,
            price=price,
            product_id=product_id,
            size=size,
            time_type=Order.TimeType.GOOD_TILL_DAY,
        )

        # FETCH CHECKING_RESPONSE
        checking_response = self.trading_api.check_order(order=order)

        if checking_response:
            self.order_created = True

            # EXTRACT CONFIRMATION_ID
            confirmation_id = checking_response.confirmation_id

            # SEND CONFIRMATION
            confirmation_response = self.trading_api.confirm_order(
                confirmation_id=confirmation_id,
                order=order,
            )

            self.order_confirmed = (
                True
                if confirmation_response
                else logger.error("order not confirmed")
            )  # noqa

        else:
            logger.critical("failed ordering")

    def get_history_response(self, type_of_hist, **kwargs):
        """Response of request of history / cash report

        Args:
            type_of_hist (_type_): _description_

        Returns:
            _type_: request object with attribute: .history or .content
            .content is only for the type: "cash"
        """
        request = BaseRequestOnDate.create(type_of_hist, **kwargs)
        request.get_response(api=self.trading_api)

        return request

    def get_products_from_ids(self, list_of_ids):
        """_summary_
        e.g: '20209472'

        Args:
            list_of_ids (_type_): _description_

        Returns:
            _type_: _description_
        """
        request = ProductsInfo.Request()
        request.products.extend(list_of_ids)

        products = self.trading_api.get_products_info(
            request=request,
            raw=True,
        )

        return products["data"].values()

    def _get_fx_rate(self):
        fx_code = "EUR" + self.prod_meta["stock_currency"]
        fx_rates = self.account_info["currencyPairs"]
        return decimalize(fx_rates[fx_code]["price"])

    def _get_config(self):
        config_table = self.trading_api.get_config()
        return config_table

    def _get_client_details(self):
        client_details_table = self.trading_api.get_client_details()
        return client_details_table

    def _get_account_info(self):
        account_info_table = self.trading_api.get_account_info()
        return account_info_table["data"]

    def _get_last_balance_via_account_overview(self):
        account_overview = self.__get_last_balance_record("account")

        cash_movements = self.get_movements_from_account_overview(
            account_overview["cashMovements"]
        )

        last_balance = get_last_valuta_balance(cash_movements)

        return decimalize(last_balance)

    def _get_last_balance_via_cash_report(self):
        content_exists = self.__get_last_balance_record("cash")

        content_of_last_balance = get_last_valuta_balance(
            content_exists, key_name="Omschrijving"
        )

        return decimalize(content_of_last_balance.replace(",", "."))

    def __get_last_balance_record(self, type_name):
        today = datetime.now()
        to_year, to_mon, to_day = today.year, today.month, today.day
        cash_movements = []
        d = 0

        while not cash_movements:
            prev_day = today - timedelta(days=d)
            from_year, from_mon, from_day = (
                prev_day.year,
                prev_day.month,
                prev_day.day,
            )
            cash_movements = self.get_history_response(
                type_name,
                from_year=from_year,
                to_year=to_year,
                from_mon=from_mon,
                to_mon=to_mon,
                from_day=from_day,
                to_day=to_day,
            ).history

            d += 1

        logger.info(
            f"Last cash movements(balance) was on {today-timedelta(days=d-1)}"
        )
        return cash_movements

    @staticmethod
    def get_movements_from_account_overview(raw_cash_movements):
        account_overview = []

        for item in raw_cash_movements:
            account_overview.append(
                {
                    "value_date": item["valueDate"],
                    "balance": item["balance"]["total"],
                    "type": item["type"],
                    "description": item["description"],
                }
            )

        return sorted(
            account_overview, key=lambda x: x["value_date"], reverse=True
        )

    @staticmethod
    def _decide_action(action_type):
        action_type = action_type.lower()

        if action_type in ("b", "buy"):
            return Order.Action.BUY

        elif action_type in ("s", "sell"):
            return Order.Action.SELL

        else:
            logger.warning(
                f"{action_type} is unclear. It must be either B or S. "
                f"Trading app will exit."
            )
            raise
