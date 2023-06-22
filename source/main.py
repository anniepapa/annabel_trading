import json

from my_logger import logger
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

        raw_account_cash_movements = trading_operator.get_history(
            "account",
            from_year=2023,
            to_year=2023,
            from_mon=6,
            to_mon=6,
            from_day=13,
            to_day=21,
        )
        # account_overview = trading_operator.get_account_overview(
        #     raw_account_cash_movements
        # )

        logger.info(raw_account_cash_movements)

        # for item in raw_account_cash_movements["cashMovements"]:
        #     print(type(item))

        prd = trading_operator.get_products_from_str("volvo")
        logger.info(prd)

        trading_operator.price_down_20_percent = True
        trading_operator.order_created = True
        trading_operator.order_confirmed = True

        return trading_operator


if __name__ == "__main__":
    main()
