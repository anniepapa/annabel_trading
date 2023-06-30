"""I would like to pay tribute to Mr. Livermore
from this childish script with full respect and expectation.

I would also learn and combine livermore with RSI divergence indicator after
livermore module is deployed

Additionally, for my beloved daughters: Annie & Bella
"""
import json
from pathlib import Path
from decimal import Decimal

from my_logger import logger
from toolkits import decimalize


class LivermoreTradingRule:
    """_summary_
    仓位(position): 是指投资人实际投资和实有投资资金的比例
    """

    def __init__(self, prod_meta) -> None:
        self.get_account_latest_cash_total = 0
        self.match_buy = False
        self.match_sell = False
        self.price_down_20_percent = True  # TODO, placeholder for testing

        self.initial_position = decimalize(
            Decimal(0.2) * prod_meta["cashable"]
        )
        self.pivot_hist = self._get_pivot_hist(prod_meta["code"])
        self.last_price_in_euro = prod_meta["last_price_in_euro"]

        self.up_ratio = 0
        self.down_ratio = 0
        self.state = None
        self.new_position = {**prod_meta, **{"balance": self.initial_position}}
        self.capacity = 0

    def analyze_trend(self):
        self.last_buy_price = Decimal(
            self.pivot_hist["buy"][0]["price_in_euro"]
        )
        # self.last_sell_price = Decimal(self.pivot_hist["sell"][0]["price_in_euro"])   # noqa

        ratio = decimalize(
            (self.last_price_in_euro - self.last_buy_price)
            / self.last_buy_price
        )
        if ratio >= Decimal("0.1"):
            self.up_ratio, self.state = ratio, 1
            logger.info(
                f"💹The last price of {self.new_position['name']} "
                f"has 🚀: {ratio*100}% up. Time to buy 20% more."
            )
        elif ratio <= Decimal("-0.1"):
            self.down_ratio, self.state = ratio, -1
            logger.info(
                f"🈹The last price of {self.new_position['name']} "
                f"has 💥: {ratio*100}% down. Time to sell all."
            )
        else:
            logger.info(
                f"🧭The last price of {self.new_position['name']} "
                f"has {ratio*100}% price diff. Hold it for now."
            )

    def analyze_capacity(self, analyzor):
        if self.state == 1:
            self.capacity = analyzor.analyze_capacity(**self.new_position)

        elif self.state == -1:
            logger.info("All stocks will be sold.")

        else:
            logger.info("Not any pivot point yet, will hold for now")

    def analyze_price(self, product, position=None):
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

    @staticmethod
    def _get_pivot_hist(code):
        with open(Path(__file__).parents[1] / "pivot_hist.json") as pivot_hist:
            hist = json.load(pivot_hist)[code]

            if hist.get("buy"):
                hist["buy"] = sorted(
                    hist["buy"], key=lambda x: x["datetime"], reverse=True
                )

            if hist.get("sell"):
                hist["sell"] = sorted(
                    hist["sell"], key=lambda x: x["datetime"], reverse=True
                )

            return hist
