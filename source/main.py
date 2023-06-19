import json

from logger import logger
from utils import (
    DegiroConnection,
    TradingOperator,
    ProductConsumer,
)


def main():
    with open("config/config.json") as config_file:
        config_dict = json.load(config_file)

    product_consumer = ProductConsumer(config_dict["user_token"])
    product_consumer.subscribe("956683606")
    logger.info(product_consumer.realtime_dict)

    with DegiroConnection(config_dict) as trading_api:
        trading_operator = TradingOperator(trading_api)
        prd = trading_operator.get_products_from_str("volvo")
        logger.info(prd)

        trading_operator.price_down_20_percent = True
        trading_operator.order_created = True
        trading_operator.order_confirmed = True

        return trading_operator


if __name__ == "__main__":
    main()
