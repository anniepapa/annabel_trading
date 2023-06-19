import pytest
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
def fake_livermore():
    livermore = LivermoreTradingRule()
    return livermore
