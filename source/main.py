import json
from fire import Fire

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
        or consumer.realtime_dict.get("AskPrice")
    )
    datetime = utc_to_cet(consumer.realtime_dict["response_datetime"])

    operator.prod_meta.update(
        {"last_price": last_price, "response_datetime": datetime}
    )


def main(stock_name, code, ratio_checkpoint="0.1"):
    logger.info(f"Start automatic trading for the stock: {stock_name}")

    with open("config/config.json") as config_file:
        config_dict = json.load(config_file)

    with DegiroConnection(config_dict) as trading_api:
        trading_operator = TradingOperator(stock_name, code, trading_api)
        prod_consumer = ProductConsumer(config_dict["user_token"])
        update_prod_meta(trading_operator, prod_consumer)

        pre_analysis = TradingAnalyzor()
        pre_analysis.analyze_capacity(**trading_operator.prod_meta)
        pre_analysis.act_on_capacity()

        trading_operator.prod_meta.update(
            {
                "cashable": pre_analysis.cashable,
                "last_price_in_euro": pre_analysis.last_price_in_euro,
            }
        )
        logger.info(trading_operator.prod_meta)

        livermore = LivermoreTradingRule(
            trading_operator.prod_meta, decimalize(ratio_checkpoint)
        )
        livermore.analyze()
        # livermore.act_on_capacity(trading_operator)


if __name__ == "__main__":
    Fire(main)
