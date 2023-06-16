from utils import TradingOperator


class TestMakeAnOrder:
    def test_make_an_order_buy(self):
        stock_name = "TESLA"

        order_status = TradingOperator.make_an_order_buy(stock_name)

        assert order_status is True
