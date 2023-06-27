import math
from decimal import Decimal

from my_logger import logger
from toolkits import decimalize


class TradingAnalyzor:
    __slot__ = (
        "stock_name",
        "balance",
        "last_price",
        "capacity",
        "cashable",
        "stock_price_in_euro",
        "cashable_state",
    )

    def __init__(self) -> None:
        self.stock_name = None
        self.balance = 0
        self.capacity = 0
        self.cashable = 0
        self.stock_price_in_euro = 0
        self.cashable_state = False

    def analyze_capacity(self, **kwarg):
        """_summary_
        Fee: 4.9 euro
        AutoFX Fee: 0.25% * total amount of transaction

        equation:   cashable <= last_balance - trans_fee - 0.0025*cashable
                    cashable <= (last_balance - trans_fee) / 1.0025
        """
        self.stock_name = kwarg["name"]
        self.balance = kwarg["last_balance"]
        self.last_price = kwarg["last_price"]

        trans_fee = kwarg["trans_fee"]
        fx_rate = kwarg["fx_rate"]

        self.cashable = Decimal(self.balance - trans_fee) / Decimal(1.0025)
        self.stock_price_in_euro = Decimal(self.last_price / fx_rate)

        capacity = decimalize(
            self.cashable / self.stock_price_in_euro, ".0001"
        )
        self.capacity = math.floor(capacity)

    def analyze_price_movements(self):
        pass

    def act_on_capacity(self):
        if self.capacity < 1:
            logger.critical(
                f"Cashable: ⛔ \n"
                f"Insufficient balance to buy 1 {self.stock_name}. "
                f"Last price of 1 stock: {self.stock_price_in_euro} "
                f"({self.last_price}). "
                f"Balance: {self.balance}. Cashable: {self.cashable}"
            )

        else:
            logger.info(
                f"Cashable: ✅ \n"
                f"Capacity: can order max {self.capacity} {self.stock_name}. "
                f"Last price of 1 stock: {self.stock_price_in_euro} "
                f"({self.last_price}). "
                f"Balance: {self.balance}. Cashable: {self.cashable}"
            )

            self.cashable_state = True
