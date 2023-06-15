from degiro_connector.trading.models.trading_pb2 import Order  # noqa


class TradingManager:
    def __init__(self) -> None:
        pass

    @staticmethod
    def make_an_order_buy(name):
        print("Ahhhh, a static method")
        order_is_bought = True
        return order_is_bought
        # SETUP ORDER
        # order = Order(
        #     action=Order.Action.BUY,
        #     order_type=Order.OrderType.LIMIT,
        #     price=10,
        #     product_id=71981,
        #     size=1,
        #     time_type=Order.TimeType.GOOD_TILL_DAY,
        # )
