import os
from builtins import ConnectionResetError, ConnectionError
from requests.exceptions import HTTPError
from urllib3.exceptions import ProtocolError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
)

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

    @retry(
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(
            (ConnectionError, ConnectionResetError, ProtocolError, HTTPError)
        ),
        wait=wait_fixed(5),
    )
    def __enter__(self):
        self.trading_api = API(credentials=self.credentials)
        self.trading_api.connect()
        return self.trading_api

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.trading_api.logout()
