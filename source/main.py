import json
from trading_manager import TradingManager


def pretty_table(target_table):
    return json.dumps(
        target_table,
        sort_keys=True,
        indent=4,
    )


def main():
    with open("config/config.json") as config_file:
        config_dict = json.load(config_file)

    with TradingManager(config_dict) as trading_api:
        # config_table = trading_api.get_config()
        client_details_table = trading_api.get_client_details()

        prettied_table = pretty_table(client_details_table)
        print(prettied_table)


if __name__ == "__main__":
    main()
