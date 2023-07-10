from decimal import Decimal

from my_logger import logger
from toolkits import decimalize
from models import TradingAnalyzor


class LivermoreTradingRule(TradingAnalyzor):
    """_summary_
    仓位(position): 是指投资人实际投资和实有投资资金的比例
    """

    __slot__ = (
        "initial_position",
        "ratio_checkpoint",
        "ratio_diff",
        "state",
        "prod_meta",
        "cashable",
        "capacity",
    )

    def __init__(self, prod_meta, ratio_checkpoint=Decimal("0.1")) -> None:
        self.initial_position = decimalize(
            Decimal("0.2") * prod_meta["cashable"]
        )
        self.ratio_checkpoint = ratio_checkpoint

        self.ratio_diff = 0
        self.state = None
        self.prod_meta = {
            **prod_meta,
            **{"last_balance": self.initial_position},
        }

        self.cashable = 0
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

        last_price_in_euro = abs(self.prod_meta["last_price_in_euro"])

        diff = last_price_in_euro - last_buy_price_in_last_fx_rate
        self.ratio_diff = decimalize(diff / last_buy_in_base_currency)

        logger.info(
            f"{self.ratio_diff} on diff: {diff}, from {last_price_in_euro} - "
            f"{last_buy_price_in_last_fx_rate} / {last_buy_in_base_currency}"
        )

        if self.ratio_diff >= self.ratio_checkpoint:
            self.state = 1

        elif self.ratio_diff <= -self.ratio_checkpoint:
            self.state = -1

        else:
            None

    def analyze(self):
        ratio_str = self.ratio_checkpoint * 100
        self.analyze_trend()
        self.analyze_capacity(self.prod_meta)

        if self.state == 1:
            logger.info(
                f"💹 Livermore: The last price of {self.prod_meta['name']} "
                f"has 🚀: {self.ratio_diff*100}% up against the checkpoint: "
                f"{ratio_str}%. Time to buy 20% more. "
                f"Max to add: {self.capacity} base on 20% cashable position."
            )

        elif self.state == -1:
            logger.info(
                f"🈹 Livermore: The last price of {self.prod_meta['name']} "
                f"has 💥: {self.ratio_diff*100}% down against the "
                f"checkpoint: {ratio_str}%. Time to sell all."
            )

        else:
            logger.info(
                f"🧭 Livermore: Price change of {self.prod_meta['name']}: "
                f"{self.ratio_diff*100}% against the checkpoint: "
                f"{ratio_str}%. No pivot point, hold it for now."
            )

    # @TODO @WIP
    def act_on_capacity(self, trading_operator):
        """To buy or sell base on state and capacity

        Args:
            trading_operator (_type_): _description_
        """
        if self.state == 1 and self.capacity >= 1:
            logger.info(
                f"🤖 Annabel is ordering {self.capacity}: "
                f"{self.prod_meta['name']} on position: "
                f"{self.prod_meta['last_price_in_euro']} base on "
                f"cashable balance: {self.prod_meta['cashable']} "
                f"from the 20% position of the last balance: "
                f"{self.prod_meta['last_balance']}"
            )
            trading_operator.order(action_type="B")

        elif self.state == -1:
            logger.info(
                f"🤖 ☢ Seriously, time to sell all "
                f" {self.prod_meta['hold_qty']} {self.prod_meta['name']}"
            )
            trading_operator.order(action_type="S")

        else:
            logger.info(
                f"🤖 Either insufficient capacity or no inflection point... "
                f"hold {self.prod_meta['name']} and wait."
            )
