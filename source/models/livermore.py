"""I would like to pay tribute to Mr. Livermore
from this childish script with full respect and expectation.

Additionally, for my beloved daughters: Annie & Bella
"""

from logger import logger


class LivermoreTradingRule:
    def __init__(self) -> None:
        self.match_buy = False
        self.match_sell = False
        self.price_down_20_percent = False
        self.action_type = None

    def trade(self, trading_api):
        if self.match_buy:
            trading_api.make_an_order(action_type="b")

        else:
            trading_api.make_an_order(action_type="s")

    def analyze(self, product):
        if self.price_down_20_percent:
            self.match_sell = True
        elif self.price_up_20_percent:
            self.match_buy = True
        else:
            logger.info("Inflection point not appear, no action to take")
