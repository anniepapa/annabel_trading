import json
from utils import DegiroConnection

import degiro_connector.core.helpers.pb_handler as payload_handler
from degiro_connector.trading.models.trading_pb2 import (  # noqa
    OrdersHistory,
    TransactionsHistory,
    ProductSearch,
    ProductsInfo,
    Order,
)


def pretty_table(target_table):
    return json.dumps(
        target_table,
        sort_keys=True,
        indent=4,
    )


def main():
    with open("config/config.json") as config_file:
        config_dict = json.load(config_file)

    with DegiroConnection(config_dict) as trading_api:
        config_table = trading_api.get_config()
        client_details_table = trading_api.get_client_details()
        account_info_table = trading_api.get_account_info()

        prettied_config = pretty_table(config_table)
        prettied_client_details = pretty_table(client_details_table)
        prettied_account_info = pretty_table(account_info_table)

        print(f"config: {prettied_config}")
        print(f"client details: {prettied_client_details}")
        print(f"account info: {prettied_account_info}")

        # SETUP REQUEST
        from_date = OrdersHistory.Request.Date(year=2022, month=7, day=19)
        to_date = OrdersHistory.Request.Date(year=2022, month=7, day=19)
        request = OrdersHistory.Request(from_date=from_date, to_date=to_date)

        # FETCH DATA
        transactions_history = trading_api.get_orders_history(
            request=request,
            raw=False,
        )

        # DISPLAY TRANSACTIONS
        for transaction in transactions_history.values:
            print(dict(transaction))

        # SETUP REQUEST
        request = ProductSearch.RequestLookup(
            search_text="Volvo Car AB",
            limit=10,
            offset=0,
            product_type_id=1,
        )

        # FETCH DATA
        products_lookup = trading_api.product_search(request=request)
        products_lookup_dict = payload_handler.message_to_dict(
            message=products_lookup
        )
        pretty_json = json.dumps(
            products_lookup_dict, sort_keys=True, indent=4
        )
        print(pretty_json)

        # SETUP REQUEST
        request = ProductsInfo.Request()
        request.products.extend([887766, 21742396])

        # FETCH DATA
        products_info = trading_api.get_products_info(
            request=request,
            raw=True,
        )
        print(products_info)

        # order = Order(
        #     action=Order.Action.BUY,
        #     order_type=Order.OrderType.LIMIT,
        #     price=43.58,
        #     product_id=20209472,
        #     size=4,
        #     time_type=Order.TimeType.GOOD_TILL_DAY,
        # )

        # # FETCH CHECKING_RESPONSE
        # checking_response = trading_api.check_order(order=order)

        # # EXTRACT CONFIRMATION_ID
        # confirmation_id = checking_response.confirmation_id

        # # SEND CONFIRMATION
        # confirmation_response = trading_api.confirm_order(
        #     confirmation_id=confirmation_id,
        #     order=order,
        # )
        # print(confirmation_response)


if __name__ == "__main__":
    main()
