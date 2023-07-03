"""I would like to pay tribute to Mr. Livermore
from this childish script with full respect and expectation.

I would also learn and combine livermore with RSI divergence indicator after
livermore module is deployed

Additionally, for my beloved daughters: Annie & Bella
"""
from decimal import Decimal

from my_logger import logger
from toolkits import decimalize
from models import TradingAnalyzor


class LivermoreTradingRule(TradingAnalyzor):
    """_summary_
    仓位(position): 是指投资人实际投资和实有投资资金的比例
    """

    def __init__(self, prod_meta) -> None:
        self.initial_position = decimalize(
            Decimal("0.2") * prod_meta["cashable"]
        )

        self.ratio_diff = 0
        self.state = None
        self.prod_meta = {
            **prod_meta,
            **{"last_balance": self.initial_position},
        }

        self.capacity = 0

    def analyze_trend(self):
        last_buy_price = abs(
            self.prod_meta["last_transaction_price"]["b"]["price_foreign"]
        )
        last_buy_in_base_currency = abs(
            self.prod_meta["last_transaction_price"]["b"][
                "price_in_base_currency"
            ]
        )
        last_buy_price_in_last_fx_rate = decimalize(
            last_buy_price / self.prod_meta["fx_rate"]
        )

        # self.last_sell_price = Decimal(self.pivot_hist["sell"][0]["price_foreign"])   # noqa
        last_price_in_euro = abs(self.prod_meta["last_price_in_euro"])

        diff = last_price_in_euro - last_buy_price_in_last_fx_rate
        self.ratio_diff = decimalize(diff / last_buy_in_base_currency)

        logger.debug(
            f"{self.ratio_diff} on diff: {diff}, from {last_price_in_euro} - "
            f"{last_buy_price_in_last_fx_rate}  / "
            f"{last_buy_in_base_currency}"
        )

        if self.ratio_diff >= Decimal("0.08"):
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
                f"💹 Livermore: The last price of {self.prod_meta['name']} "
                f"has 🚀: {self.ratio_diff*100}% up. Time to buy 20% more. "
                f"Max to add: {self.capacity} base on 20% cashable position."
            )

        elif self.state == -1:
            logger.info(
                f"🈹 Livermore: The last price of {self.prod_meta['name']} "
                f"has 💥: {self.ratio_diff*100}% down. Time to sell all."
            )

        else:
            logger.info(
                f"🧭 Livermore: Price change: {self.ratio_diff*100}%. "
                f"Not any pivot point yet, would hold it for now"
            )

    def act_on_capacity(self, trading_operator):
        if self.state == 1 and self.capacity > 0:
            trading_operator.order(
                self.prod_meta["last_price_in_euro"],
                self.capacity,
                action_type="B",
            )

        elif self.state == -1:
            trading_operator.order("S")

        else:
            logger.info("No action, would hold and wait.")
