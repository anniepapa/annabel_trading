import sys
from datetime import datetime, timedelta
from decimal import Decimal

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
        "keyword",
        "code",
        "order_created",
        "order_confirmed",
        # "config",
        # "client_details",
        "account_info",
        "product_id",
        "prod_meta",
    )

    def __init__(self, keyword, code, trading_api=None):
        self.trading_api = trading_api
        self.keyword = keyword
        self.code = code.lower().replace(" ", "_")

        self.order_created = False
        self.order_confirmed = False

        # self.config = self._get_config()
        # self.client_details = self._get_client_details()
        self.account_info = self._get_account_info()
        self.product_id = None
        self.prod_meta = self.initiate_prod_meta_from_str()

        self.prod_meta.update(
            {
                "fx_rate": self._get_fx_rate(self.prod_meta["stock_currency"]),
                "code": self.code.replace(" ", "_"),
            }
        )
        self._get_last_transaction_price()

    def initiate_prod_meta_from_str(self):
        """
        example: 'vOvlVO cAr', 'volcar b'
        """
        request = ProductSearch.RequestLookup(
            search_text=self.keyword,
            limit=10,
            offset=0,
            product_type_id=1,
        )

        products = self.trading_api.product_search(request=request)
        prods = payload_handler.message_to_dict(message=products)["products"]

        for prod in prods:
            if prod["symbol"].lower().replace(" ", "_") == self.code:
                logger.info(
                    f"Product matches {self.keyword} and {self.code}: {prod}"
                )
                prod_meta = {
                    "name": prod["name"],
                    "id": prod["id"],
                    "vwd_id": prod["vwdId"],
                    "stock_currency": prod["currency"],
                    "close_price": prod["closePrice"],
                    "close_price_date": prod["closePriceDate"],
                    "trans_fee": decimalize(4.9),
                    "last_balance": self._get_last_balance_via_account_overview(),  # noqa
                }
                break
        else:
            logger.error(f"{prod['symbol']} and {self.code} has no match")
            sys.exit()

        return prod_meta

    def order(self, price, size, action_type="B"):
        action = self._decide_action(action_type)

        order = Order(
            action=action,
            order_type=Order.OrderType.STOP_LOSS,
            price=price,
            product_id=self.prod_meta["id"],
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

    def _get_fx_rate(self, stock_currency):
        fx_code = "EUR" + stock_currency
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
        cash_movements = self.__get_last_records("account")
        last_balance = get_last_valuta_balance(cash_movements)
        return decimalize(last_balance)

    def _get_last_balance_via_cash_report(self):  # to be tested more
        content_exists = self.__get_last_records("cash")

        content_of_last_balance = get_last_valuta_balance(
            content_exists, key_name="Omschrijving"
        )

        return decimalize(content_of_last_balance.replace(",", "."))

    def _get_last_transaction_price(self):
        self.product_id = self.prod_meta["id"]
        last_transaction_details = self.__get_last_records("transaction")[0]
        last_transaction = {
            last_transaction_details["buysell"].lower(): {
                "transaction_datetime": last_transaction_details["date"],
                "price_foreign": decimalize(last_transaction_details["price"]),
                "last_buy_fx_rate": decimalize(
                    last_transaction_details["nettFxRate"]
                ),
                "price_in_base_currency": decimalize(
                    Decimal(last_transaction_details["price"])
                    / Decimal(last_transaction_details["nettFxRate"])
                ),
                "quantity": decimalize(last_transaction_details["quantity"]),
                "total_plus_all_fees_in_euro": decimalize(
                    last_transaction_details["totalPlusAllFeesInBaseCurrency"]
                ),
            }
        }

        self.prod_meta.update({"last_transaction_price": last_transaction})

    def __get_last_records(self, type_name):
        today = datetime.now()
        to_year, to_mon, to_day = today.year, today.month, today.day
        history_records, d = [], 0

        while d <= 31 and not history_records:
            prev_week = today - timedelta(days=d)
            from_year, from_mon, from_day = (
                prev_week.year,
                prev_week.month,
                prev_week.day,
            )
            history_records = self.get_history_response(
                type_name,
                from_year=from_year,
                to_year=to_year,
                from_mon=from_mon,
                to_mon=to_mon,
                from_day=from_day,
                to_day=to_day,
            ).history

            if self.product_id:
                for record in history_records:
                    if (
                        int(record.get("productId")) == int(self.product_id)
                        and record["buysell"] == "B"
                    ):  # noqa
                        history_records = [record]
                        logger.info(
                            f"📆 Last history records of {type_name} exist on "
                            f"{record['date']}"
                        )
                        break

                else:
                    history_records = []
                    logger.warning(
                        f"❓❓❓🧐 no any last transaction price can be found "
                        f"for {self.product_id} from the past {d} days."
                    )

            d += 7
        return history_records

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
