import degiro_connector.core.helpers.pb_handler as payload_handler
from degiro_connector.trading.models.trading_pb2 import (  # noqa
    ProductSearch,
    ProductsInfo,
    Order,
)

from utils import BaseRequestOnDate
from my_logger import logger


class TradingOperator:
    def __init__(self, trading_api=None):
        self.trading_api = trading_api

        self.order_created = False
        self.order_confirmed = False

        self.config = self._get_config()
        self.client_details = self._get_client_details()
        self.account_info = self._get_account_info()

        self.target_product = None

    def operate(self, ruled_product):
        self.target_product = ruled_product

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

    def get_products_from_str(self, keyword):
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
        products_dict = payload_handler.message_to_dict(message=products)
        return products_dict

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

    def _get_config(self):
        config_table = self.trading_api.get_config()
        return config_table

    def _get_client_details(self):
        client_details_table = self.trading_api.get_client_details()
        return client_details_table

    def _get_account_info(self):
        account_info_table = self.trading_api.get_account_info()
        return account_info_table

    @staticmethod
    def get_account_overview(raw_cash_movements):
        account_overview = {}

        for item in raw_cash_movements:
            movement_id = "_".join(
                (item["date"], str(item["id"]), item["currency"])
            )
            account_overview[movement_id] = {
                "value_date": item["valueDate"],
                "balance": item["balance"]["total"],
                "type": item["type"],
                "description": item["description"],
            }

        account_overview = sorted(
            account_overview.items(), key=lambda x: x[0], reverse=True
        )
        return dict(account_overview)

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

    @staticmethod
    def make_an_order_buy(name):
        logger.info("Ahhhh, a static method")
        order_is_bought = True
        return order_is_bought
