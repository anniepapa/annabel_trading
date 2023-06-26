import math

from my_logger import logger


class TradingAnalyzor:
    __slot__ = (
        "capacity",
        "stock_name",
    )

    def __init__(self) -> None:
        self.capacity = 0
        self.stock_name = None

    def analyze_capacity(self, **kwarg):
        latest_balance = kwarg["latest_balance"]
        trans_fee = kwarg["trans_fee"]
        latest_price = kwarg["latest_price"]
        fx_rate = kwarg["fx_rate"]

        capacity = (latest_balance - trans_fee) / (latest_price / fx_rate)
        self.capacity = math.floor(capacity)
        self.stock_name = kwarg["name"]

    def analyze_price_movements(self):
        pass

    def act_on_capacity(self):
        if self.capacity < 1:
            logger.critical(f"Insufficient balance to buy 1 {self.stock_name}")
            return False

        logger.info(
            f"Capacity: able to order max {self.capacity} {self.stock_name}"
        )

        return True
