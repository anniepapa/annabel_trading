import pytest
from .utils import ProductConsumer


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
