"""I would like to pay tribute to Mr. Livermore # noqa
from this childish script with full respect and expectation.

I would also learn and combine livermore with RSI divergence indicator after livermore module is deployed

Additionally, for my beloved daughters: Annie & Bella
"""

from logger import logger


class LivermoreTradingRule:
    """_summary_
    仓位(position): 是指投资人实际投资和实有投资资金的比例
    """

    def __init__(self) -> None:
        self.match_buy = False
        self.match_sell = False
        self.price_down_20_percent = True  # TODO, placeholder for testing

    def analyze(self, product, position=None):
        if self.price_down_20_percent:
            self.match_sell = True
        elif self.price_up_20_percent:
            self.match_buy = True
        else:
            logger.info("Pivot point not appear, no action to take")

    def trade(self, trading_api):
        if self.match_buy:
            trading_api.make_an_order(action_type="b")

        else:
            trading_api.make_an_order(action_type="s")
