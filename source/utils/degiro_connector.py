import os
from degiro_connector.trading.api import API
from degiro_connector.trading.models.trading_pb2 import Credentials


class DegiroConnection:
    __slot__ = (
        "trading_api",
        "credentials",
    )

    def __init__(self, config_dict):
        self.trading_api = None
        # SETUP CREDENTIALS
        self.credentials = Credentials(
            username=config_dict["username"],
            password=os.getenv("annabel_toy"),
            int_account=config_dict["int_account"],
            totp_secret_key=config_dict["totp_secret_key"],
        )

    def __enter__(self):
        self.trading_api = API(credentials=self.credentials)
        self.trading_api.connect()
        return self.trading_api

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.trading_api.logout()
