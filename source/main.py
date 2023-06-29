import json
import fire

from my_logger import logger
from toolkits import utc_to_cet, decimalize
from utils import (
    DegiroConnection,
    TradingOperator,
    ProductConsumer,
)
from models import TradingAnalyzor


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


def main(stock_name):
    logger.info(f"Start automatic trading for the stock: {stock_name}")

    with open("config/config.json") as config_file:
        config_dict = json.load(config_file)

    with DegiroConnection(config_dict) as trading_api:
        trading_operator = TradingOperator(trading_api)
        trading_operator.initiate_prod_meta_from_str(stock_name)
        prod_consumer = ProductConsumer(config_dict["user_token"])

        update_prod_meta(trading_operator, prod_consumer)
        logger.info(trading_operator.prod_meta)

        analyzor = TradingAnalyzor()
        analyzor.analyze_capacity(**trading_operator.prod_meta)
        analyzor.act_on_capacity()
        logger.info(analyzor.cashable_state)

        analyzor.price_down_20_percent = True
        analyzor.order_created = True
        analyzor.order_confirmed = True

        return trading_operator


if __name__ == "__main__":
    fire.Fire(main)
