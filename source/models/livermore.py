from decimal import Decimal

from google.cloud import firestore

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
        "ratio_diff_buy",
        "ratio_diff_sell",
        "state",
        "prod_meta",
        "cashable",
        "capacity",
        "checkpoint_up",
        "checkpoint_down",
    )

    def __init__(self, prod_meta, ratio_checkpoint=Decimal("0.1")) -> None:
        self.initial_position = decimalize(
            Decimal("0.2") * prod_meta["cashable"]
        )
        self.ratio_checkpoint = ratio_checkpoint

        self.ratio_diff_buy = 0
        self.ratio_diff_sell = 0

        self.state = None
        self.prod_meta = {
            **prod_meta,
            **{"last_balance": self.initial_position},
        }

        self.cashable = 0
        self.capacity = 0

        self.checkpoint_up = None
        self.checkpoint_down = None

    def _get_ratio_diff_buy(self, last_price_in_euro):
        last_buy_price = abs(
            self.prod_meta["last_transaction_price"]["b"]["price_foreign"]
        )

        last_buy_price_in_last_fx_rate = decimalize(
            last_buy_price / self.prod_meta["fx_rate"]
        )

        diff_buy = self.prod_meta["last_price"] - last_buy_price

        logger.info(
            f"diff buy: {diff_buy} between last price (foreign): "
            f"{self.prod_meta['last_price']}(euro: {last_price_in_euro}) "
            f"and the last buy price (foreign): {last_buy_price}."
            f"(euro: {last_buy_price_in_last_fx_rate})"
        )

        return decimalize(diff_buy / last_buy_price)

    def _get_ratio_diff_sell(self, last_price_in_euro):
        db = firestore.Client(project="avian-volt-391821")
        doc_price = db.collection(self.prod_meta["code"])
        price_info = {}
        for doc in doc_price.stream():
            (price_info := doc.to_dict())
            logger.info(f"highest price: {price_info}")

        highest_foreign = decimalize(price_info.get("highest_foreign") or 0)
        highest_euro = decimalize(price_info.get("highest_euro") or 0)

        diff_sell = self.prod_meta["last_price"] - highest_foreign

        logger.info(
            f"diff sell: {diff_sell} between last price (foreign): "
            f"{self.prod_meta['last_price']}(euro: {last_price_in_euro}) "
            f"and the highest of today (foreign): "
            f"{price_info.get('highest_foreign') or 0}"
            f"(euro: {highest_euro})."
        )

        return decimalize(diff_sell / highest_foreign)

    def analyze_trend(self):
        self.checkpoint_up = self.ratio_checkpoint - Decimal("0.015")
        self.checkpoint_down = -self.ratio_checkpoint + Decimal("0.01")

        last_price_in_euro = abs(self.prod_meta["last_price_in_euro"])

        self.ratio_diff_buy = self._get_ratio_diff_buy(last_price_in_euro)
        self.ratio_diff_sell = self._get_ratio_diff_sell(last_price_in_euro)

        if self.ratio_diff_buy >= self.checkpoint_up:
            self.state = 1

        elif self.ratio_diff_sell <= self.checkpoint_down:
            self.state = -1

        else:
            None

    def analyze(self):
        self.analyze_capacity(self.prod_meta)
        self.analyze_trend()

        if self.state == 1:
            logger.info(
                f"💹 Livermore: The last price of {self.prod_meta['name']} "
                f"has 🚀: {self.ratio_diff_buy*100}% up against the "
                f"checkpoint: {self.checkpoint_up*100}%. Time to buy 20% more. "  # noqa
                f"Max to add: {self.capacity} base on 20% cashable position."
            )

        elif self.state == -1:
            logger.info(
                f"🈹 Livermore: The last price of {self.prod_meta['name']} "
                f"has 💥: {self.ratio_diff_sell*100}% down against the "
                f"checkpoint: {self.checkpoint_down*100}%. Time to sell all."
            )

        else:
            logger.info(
                f"🧭 Livermore: Price change of {self.prod_meta['name']}: "
                f"{self.ratio_diff_sell*100}% ~ {self.ratio_diff_buy*100}% "
                f"against the checkpoint: {self.checkpoint_down*100}% ~ "
                f"{self.checkpoint_up*100}%. No pivot point, hold it for now."
            )

    def review_decision(self, meta):
        trans_fee = abs(
            meta["last_transaction_price"]["b"]["trans_fee_in_euro"]
        )
        autofx_fee = abs(
            meta["last_transaction_price"]["b"]["autofx_rate_in_euro"]
        )
        qty = meta["hold_qty"]

        last_buy_price = abs(
            meta["last_transaction_price"]["b"]["price_foreign"]
        )
        last_buy_price_in_euro = decimalize(last_buy_price / meta["fx_rate"])
        last_price_in_euro = meta["last_price_in_euro"]

        earns = (last_price_in_euro - last_buy_price_in_euro) * qty
        fees = decimalize(trans_fee + autofx_fee)
        net = decimalize(earns - fees * 2)
        percent = earns / last_price_in_euro

        logger.info(
            f"✍✍ Earning: {earns}, needs to pay: {fees*2}. Net: {net}. "
            f"{net} / last price in euro: {last_price_in_euro} ==> {percent}"
        )

        if self.state not in (1, -1) and self.prod_meta.get("sell_order"):
            logger.info(
                "🧛‍♂️ Calm down, each sell costs money...livermore says "
                "hold it, the existing SELL order will be deleted."
            )
            self.trading_api.delete_order(
                order_id=self.prod_meta["sell_order"]["id"]
            )

        if self.ratio_diff_sell < 0 and net > 0:
            logger.info(
                f"🎃 It's down with ratio diff sell: {self.ratio_diff_sell} "
                f"but earned: {net}. Sell it to earn some."
            )
            self.state = -1

        elif self.state == 1 and net <= 0:
            logger.info(
                f"🎃 It's up with ratio diff sell: {self.ratio_diff_sell} "
                f"but earned: {net} < {fees} to pay. Hold it before a new buy"
            )

        else:
            pass

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
