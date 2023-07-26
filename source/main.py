import json
import os
from fire import Fire
from decimal import Decimal

from my_logger import logger
from toolkits import utc_to_cet, decimalize
from utils import (
    DegiroConnection,
    TradingOperator,
    ProductConsumer,
)
from models import TradingAnalyzor, LivermoreTradingRule


def update_prod_meta(operator, consumer):
    consumer.subscribe(operator.prod_meta["vwd_id"])
    last_price = decimalize(
        consumer.realtime_dict.get("LastPrice")
        or operator.prod_meta["close_price"]
    )
    datetime = utc_to_cet(consumer.realtime_dict["response_datetime"])

    operator.prod_meta.update(
        {"last_price": last_price, "response_datetime": datetime}
    )
    operator.prod_meta.update(
        {
            "last_price_in_euro": decimalize(
                operator.prod_meta["last_price"]
                / operator.prod_meta["fx_rate"]
            )
        }
    )


def check_annabel_toy():
    if os.getenv("annabel_toy") and os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS"
    ):  # noqa
        pass
    else:
        logger.error("ENV var: annabel toy doesn't exit. Process will stop")
        raise SystemExit


def main(stock_name, code, ratio_checkpoint="0.1"):
    logger.info(f"Start automatic trading for the stock: {stock_name}")
    check_annabel_toy()

    with open("config/config.json") as config_file:
        config_dict = json.load(config_file)

    with DegiroConnection(config_dict) as trading_api:
        trading_operator = TradingOperator(stock_name, code, trading_api)
        prod_consumer = ProductConsumer(config_dict["user_token"])
        # prod_consumer._get_chart(trading_operator.prod)

        update_prod_meta(trading_operator, prod_consumer)
        trading_operator.check_pending_order()

        pre_analysis = TradingAnalyzor()
        pre_analysis.analyze_capacity(trading_operator.prod_meta)
        pre_analysis.act_on_capacity()
        trading_operator.prod_meta.update(
            {
                "cashable": pre_analysis.cashable,
                "capacity": pre_analysis.capacity,
            }
        )

        logger.info(f"👉👉 Meta before livermore: {trading_operator.prod_meta}")
        livermore = LivermoreTradingRule(
            trading_operator.prod_meta, Decimal(str(ratio_checkpoint))
        )
        livermore.analyze()
        trading_operator.prod_meta.update(
            {
                "cashable": livermore.cashable,
                "capacity": livermore.capacity,
            }
        )
        logger.info(f"👉👉 Meta after livermore: {trading_operator.prod_meta}")

        # livermore.review_decision(trading_operator.prod_meta)
        # livermore.act_on_capacity(trading_operator)


if __name__ == "__main__":
    try:
        Fire(main)
    except Exception as err:
        raise err
