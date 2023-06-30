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


def main(stock_name, code):
    logger.info(f"Start automatic trading for the stock: {stock_name}")

    with open("config/config.json") as config_file:
        config_dict = json.load(config_file)

    with DegiroConnection(config_dict) as trading_api:
        trading_operator = TradingOperator(trading_api)
        trading_operator.initiate_prod_meta_from_str(stock_name, code)

        prod_consumer = ProductConsumer(config_dict["user_token"])
        update_prod_meta(trading_operator, prod_consumer)

        analyzor = TradingAnalyzor()
        analyzor.analyze_capacity(**trading_operator.prod_meta)
        analyzor.act_on_capacity()

        trading_operator.prod_meta.update(
            {
                "cashable": analyzor.cashable,
                "last_price_in_euro": analyzor.stock_price_in_euro,
            }
        )
        logger.info(trading_operator.prod_meta)

        analyzor.price_down_20_percent = True
        analyzor.order_created = True
        analyzor.order_confirmed = True

    livermore = LivermoreTradingRule(trading_operator.prod_meta)
    livermore.analyze_trend()
    print(livermore.initial_position)


if __name__ == "__main__":
    Fire(main)
