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
from models import TradingAnalyzor


class LivermoreTradingRule(TradingAnalyzor):
    """_summary_
    仓位(position): 是指投资人实际投资和实有投资资金的比例
    """

    def __init__(self, prod_meta) -> None:
        self.get_account_latest_cash_total = 0
        self.match_buy = False
        self.match_sell = False
        self.price_down_20_percent = True  # TODO, placeholder for testing

        self.initial_position = decimalize(
            Decimal("0.2") * prod_meta["cashable"]
        )
        self.pivot_hist = self._get_pivot_hist(prod_meta["code"])
        self.last_price_in_euro = prod_meta["last_price_in_euro"]

        self.ratio_diff = 0
        self.state = None
        self.prod_meta = {
            **prod_meta,
            **{"last_balance": self.initial_position},
        }
        self.capacity = 0

    def analyze_trend(self):
        self.last_buy_price = Decimal(
            self.pivot_hist["buy"][0]["price_in_euro"]
        )
        # self.last_sell_price = Decimal(self.pivot_hist["sell"][0]["price_in_euro"])   # noqa

        self.ratio_diff = decimalize(
            (self.last_price_in_euro - self.last_buy_price)
            / self.last_buy_price
        )
        if self.ratio_diff >= Decimal("0.1"):
            self.state = 1

        elif self.ratio_diff <= Decimal("-0.1"):
            self.state = -1

        else:
            None

    def analyze(self):
        self.analyze_trend()

        if self.state == 1:
            self.analyze_capacity(**self.prod_meta)

            logger.info(
                f"💹The last price of {self.prod_meta['name']} "
                f"has 🚀: {self.ratio_diff*100}% up. Time to buy 20% more. "
                f"Max to add: {self.capacity} base on 20% cashable position."
            )

        elif self.state == -1:
            logger.info(
                f"🈹The last price of {self.prod_meta['name']} "
                f"has 💥: {self.ratio_diff*100}% down. Time to sell all."
            )

        else:
            logger.info(
                f"🧭 Price change: {self.ratio_diff*100}%. "
                f"Not any pivot point yet, will hold for now"
            )

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
