from utils import TradingManager


class TestMakeAnOrder:
    def test_make_an_order_buy(self):
        stock_name = "TESLA"

        order_status = TradingManager.make_an_order_buy(stock_name)

        assert order_status is True
