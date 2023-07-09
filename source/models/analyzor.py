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
        "last_price_in_euro",
        "cashable_state",
    )

    def __init__(self) -> None:
        self.stock_name = None
        self.balance = 0
        self.capacity = 0
        self.cashable = 0
        self.last_price_in_euro = 0
        self.cashable_state = False

    def analyze_capacity(self, prod_meta):
        """_summary_
        Fee: 4.9 euro
        AutoFX Fee: autofx * total amount of transaction

        equation:   cashable <= last_balance - trans_fee - autofx*cashable
                    cashable <= (last_balance - trans_fee) / 1.0025
        """
        self.stock_name = prod_meta["name"]
        self.balance = prod_meta["last_balance"]
        self.last_price = prod_meta["last_price"]

        trans_fee = abs(
            prod_meta["last_transaction_price"]["b"]["trans_fee_in_euro"]
        )
        autofx_fee = abs(
            prod_meta["last_transaction_price"]["b"]["autofx_rate_in_euro"]
        )

        self.cashable = decimalize(
            Decimal(self.balance - trans_fee) / Decimal(1 + autofx_fee)
        )
        logger.debug(
            f"Cashable: {self.cashable} base on "
            f"balance: {self.balance} deduct trans fee then divided "
            f"by autofx_fee: {autofx_fee}"
        )
        capacity = decimalize(self.cashable / prod_meta["last_price_in_euro"])
        self.capacity = math.floor(capacity)

    def act_on_capacity(self):
        if self.capacity < 1:
            logger.critical(
                f"⛔ Uncashable: \n"
                f"Insufficient balance to buy 1 {self.stock_name}. "
                f"Last price of 1 stock: {self.last_price_in_euro} "
                f"({self.last_price}). "
                f"Balance: {self.balance}. Cashable: {self.cashable}"
            )

        else:
            logger.info(
                f"✅ Cashable: \n"
                f"Capacity: can order max {self.capacity} {self.stock_name}. "
                f"Last price of 1 stock: {self.last_price_in_euro} "
                f"({self.last_price}). "
                f"Balance: {self.balance}. Cashable: {self.cashable}"
            )

            self.cashable_state = True
