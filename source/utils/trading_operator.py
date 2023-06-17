import json

import degiro_connector.core.helpers.pb_handler as payload_handler
from degiro_connector.trading.models.trading_pb2 import (  # noqa
    OrdersHistory,
    TransactionsHistory,
    ProductSearch,
    ProductsInfo,
    Order,
)
from logger import logger


def pretty_table(target_table):
    return json.dumps(
        target_table,
        sort_keys=True,
        indent=4,
    )


class TradingOperator:
    def __init__(self, trading_api=None):
        self.trading_api = trading_api

        self.price_down_20_percent = False
        self.order_created = False
        self.order_confirmed = False

        self.config = self._get_config()
        self.client_details = self._get_client_details()
        self.account_info = self._get_account_info()

    def make_an_order(self, product_id, price, size):
        order = Order(
            action=Order.Action.BUY,
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

    def get_history(
        self, from_year, to_year, from_mon, to_mon, from_day, to_day
    ):
        from_date = OrdersHistory.Request.Date(
            year=from_year, month=from_mon, day=from_day
        )
        to_date = OrdersHistory.Request.Date(
            year=to_year, month=to_mon, day=to_day
        )
        request = OrdersHistory.Request(from_date=from_date, to_date=to_date)

        orders_history = self.trading_api.get_orders_history(
            request=request,
            raw=False,
        )

        return [dict(order) for order in orders_history.values]

    def get_transactions_history(
        self, from_year, to_year, from_mon, to_mon, from_day, to_day
    ):
        from_date = TransactionsHistory.Request.Date(
            year=from_year, month=from_mon, day=from_day
        )
        to_date = TransactionsHistory.Request.Date(
            year=to_year, month=to_mon, day=to_day
        )
        request = TransactionsHistory.Request(
            from_date=from_date, to_date=to_date
        )

        transactions_history = self.trading_api.get_transactions_history(
            request=request,
            raw=False,
        )

        return [
            dict(transaction) for transaction in transactions_history.values
        ]

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
        return pretty_table(products_dict)

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
        return pretty_table(config_table)

    def _get_client_details(self):
        client_details_table = self.trading_api.get_client_details()
        return pretty_table(client_details_table)

    def _get_account_info(self):
        account_info_table = self.trading_api.get_account_info()
        return pretty_table(account_info_table)

    @staticmethod
    def make_an_order_buy(name):
        logger.info("Ahhhh, a static method")
        order_is_bought = True
        return order_is_bought
