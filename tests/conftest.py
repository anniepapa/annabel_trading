import pytest
from google.protobuf.struct_pb2 import Struct, ListValue

from utils import ProductConsumer
from models import LivermoreTradingRule


@pytest.fixture
def fake_from_to_date():
    return {
        "from_year": 2022,
        "to_year": 2022,
        "from_mon": 7,
        "to_mon": 7,
        "from_day": 18,
        "to_day": 19,
    }


@pytest.fixture
def fake_product():
    product = ProductConsumer()
    product.realtime_dict = {
        "956683606": {
            "response_datetime": "2023-06-18T13:32:37.939421Z",
            "request_duration": 1.418968,
            "vwd_id": "956683606",
            "LastPrice": 44.92,
            "LowPrice": 43.89,
            "LastDate": 1686866400.0,
            "HighPrice": 45.02,
        }
    }

    return product


@pytest.fixture
def fake_acccount_overview():
    fake_account_overview_origin = [
        {
            "balance": {
                "unsettledCash": 30,
                "total": 30.27,
                "flatexCash": 0.27,
            },
            "change": 30,
            "currency": "EUR",
            "date": "2023-06-15T16:09:07+02:00",
            "description": "Reservation iDEAL / Sofort Deposit",
            "id": 1730366149,
            "type": "CASH_TRANSACTION",
            "valueDate": "2023-06-15T16:09:07+02:00",
        },
        {
            "balance": {"unsettledCash": -43.68, "total": -43.68},
            "change": -43.68,
            "currency": "SEK",
            "date": "2023-06-15T16:11:58+02:00",
            "description": "Koop 1 @ 43,68 SEK",
            "id": 393047611,
            "orderId": "610319aa-d358-4e92-8ce0-6c8d83c4452f",
            "productId": 20209472,
            "type": "TRANSACTION",
            "valueDate": "2023-06-15T16:11:58+02:00",
        },
        {
            "balance": {"unsettledCash": 1.6, "total": 1.6},
            "currency": "EUR",
            "date": "2023-06-16T12:49:23+02:00",
            "description": "Overboeking van uw geldrekening bij flatexDEGIRO Bank 0,27 EUR",  # noqa
            "id": 1731629923,
            "type": "FLATEX_CASH_SWEEP",
            "valueDate": "2023-06-15T23:59:59+02:00",
        },
    ]

    account_overview = Struct()
    account_overview_items = ListValue()

    account_overview_items.extend(fake_account_overview_origin)
    account_overview.update({"cashMovements": account_overview_items})

    return account_overview


@pytest.fixture
def fake_livermore():
    livermore = LivermoreTradingRule()
    return livermore
