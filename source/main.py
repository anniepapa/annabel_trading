import json

# from logger import logger
from utils import DegiroConnection, TradingOperator


def main():
    with open("config/config.json") as config_file:
        config_dict = json.load(config_file)

    with DegiroConnection(config_dict) as trading_api:
        trading_operator = TradingOperator(trading_api)

        trading_operator.price_down_20_percent = True
        trading_operator.order_created = True
        trading_operator.order_confirmed = True

        return trading_operator


if __name__ == "__main__":
    main()
