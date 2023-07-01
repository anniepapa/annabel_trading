import pytest
from google.protobuf.struct_pb2 import Struct, ListValue
from decimal import Decimal

from utils import ProductConsumer
from models import TradingAnalyzor, LivermoreTradingRule


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
            "balance": {"unsettledCash": 1.6, "total": 1.6},
            "currency": "EUR",
            "date": "2023-06-16T12:49:23+02:00",
            "description": "Overboeking van uw geldrekening bij flatexDEGIRO Bank 0,27 EUR",  # noqa
            "id": 1731629923,
            "type": "FLATEX_CASH_SWEEP",
            "valueDate": "2023-06-15T23:59:59+02:00",
        },
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
    ]

    account_overview = Struct()
    account_overview_items = ListValue()

    account_overview_items.extend(fake_account_overview_origin)
    account_overview.update({"cashMovements": account_overview_items})

    return account_overview["cashMovements"]


@pytest.fixture
def fake_account_cash_movements_report():
    return 'Datum,Tijd,Valutadatum,Product,ISIN,Omschrijving,FX,Mutatie,,Saldo,,Order Id\n19-06-2023,16:50,19-06-2023,,,"Overboeking van uw geldrekening bij flatexDEGIRO Bank 28,4 EUR",,,,EUR,"1,60",\n19-06-2023,16:50,19-06-2023,FLATEX EURO BANKACCOUNT,NLFLATEXACNT,Degiro Cash Sweep Transfer,,EUR,"28,40",EUR,"30,00",\n17-06-2023,04:51,16-06-2023,,,iDEAL Deposit,,EUR,"30,00",EUR,"1,60",\n17-06-2023,04:51,16-06-2023,,,Reservation iDEAL / Sofort Deposit,,EUR,"-30,00",EUR,"-28,40",\n16-06-2023,12:49,15-06-2023,,,"Overboeking van uw geldrekening bij flatexDEGIRO Bank 0,27 EUR",,,,EUR,"1,60",\n16-06-2023,12:49,15-06-2023,FLATEX EURO BANKACCOUNT,NLFLATEXACNT,Degiro Cash Sweep Transfer,,EUR,"0,27",EUR,"1,87",\n15-06-2023,16:40,15-06-2023,VOLVO CAR AB,SE0016844831,Valuta Creditering,"11,5544",SEK,"174,32",SEK,"0,00",02e4ac99-e8e8-4a32-8c95-d38a2ea33fe9\n15-06-2023,16:40,15-06-2023,VOLVO CAR AB,SE0016844831,Valuta Debitering,,EUR,"-15,09",EUR,"1,60",02e4ac99-e8e8-4a32-8c95-d38a2ea33fe9\n15-06-2023,16:40,15-06-2023,VOLVO CAR AB,SE0016844831,DEGIRO Transactiekosten en/of kosten van derden,,EUR,"-4,90",EUR,"16,69",02e4ac99-e8e8-4a32-8c95-d38a2ea33fe9\n15-06-2023,16:40,15-06-2023,VOLVO CAR AB,SE0016844831,"Koop 4 @ 43,58 SEK",,SEK,"-174,32",SEK,"-174,32",02e4ac99-e8e8-4a32-8c95-d38a2ea33fe9\n15-06-2023,16:11,15-06-2023,VOLVO CAR AB,SE0016844831,Valuta Creditering,"11,5631",SEK,"43,68",SEK,"0,00",610319aa-d358-4e92-8ce0-6c8d83c4452f\n15-06-2023,16:11,15-06-2023,VOLVO CAR AB,SE0016844831,Valuta Debitering,,EUR,"-3,78",EUR,"21,59",610319aa-d358-4e92-8ce0-6c8d83c4452f\n15-06-2023,16:11,15-06-2023,VOLVO CAR AB,SE0016844831,DEGIRO Transactiekosten en/of kosten van derden,,EUR,"-4,90",EUR,"25,37",610319aa-d358-4e92-8ce0-6c8d83c4452f\n15-06-2023,16:11,15-06-2023,VOLVO CAR AB,SE0016844831,"Koop 1 @ 43,68 SEK",,SEK,"-43,68",SEK,"-43,68",610319aa-d358-4e92-8ce0-6c8d83c4452f\n15-06-2023,16:09,15-06-2023,,,Reservation iDEAL / Sofort Deposit,,EUR,"30,00",EUR,"30,27",\n'  # noqa


@pytest.fixture
def fake_cash_movements_ideal_deposit_positive():
    return [
        {
            "value_date": "2023-06-29T23:59:59+02:00",
            "balance": 138.92,
            "type": "CASH_TRANSACTION",
            "description": "iDEAL Deposit",
        },
        {
            "value_date": "2023-06-29T23:59:59+02:00",
            "balance": -121.08,
            "type": "CASH_TRANSACTION",
            "description": "Reservation iDEAL / Sofort Deposit",
        },
    ]


@pytest.fixture
def fake_cash_movements_valuta_debitering_positive():
    return [
        {
            "value_date": "2023-06-29T17:19:37+02:00",
            "balance": 138.92,
            "type": "FLATEX_CASH_SWEEP",
            "description": "Overboeking van uw geldrekening bij flatexDEGIRO Bank 33 EUR",  # noqa
        },
        {
            "value_date": "2023-06-29T17:19:37+02:00",
            "balance": 171.92,
            "type": "FLATEX_CASH_SWEEP",
            "description": "Degiro Cash Sweep Transfer",
        },
        {
            "value_date": "2023-06-29T16:07:46+02:00",
            "balance": 0.0,
            "type": "CASH_TRANSACTION",
            "description": "Valuta Creditering",
        },
        {
            "value_date": "2023-06-29T16:07:46+02:00",
            "balance": 138.92,
            "type": "CASH_TRANSACTION",
            "description": "Valuta Debitering",
        },
        {
            "value_date": "2023-06-29T16:07:46+02:00",
            "balance": 375.0,
            "type": "CASH_TRANSACTION",
            "description": "DEGIRO Transactiekosten en/of kosten van derden",
        },
        {
            "value_date": "2023-06-29T16:07:46+02:00",
            "balance": -256.0,
            "type": "TRANSACTION",
            "description": "Koop 1 @ 256 USD",
        },
        {
            "value_date": "2023-06-29T06:47:45+02:00",
            "balance": 377.0,
            "type": "CASH_TRANSACTION",
            "description": "Reservation iDEAL / Sofort Deposit",
        },
        {
            "value_date": "2023-06-28T23:59:59+02:00",
            "balance": 377.0,
            "type": "FLATEX_CASH_SWEEP",
            "description": "Overboeking van uw geldrekening bij flatexDEGIRO Bank 1,6 EUR",  # noqa
        },
        {
            "value_date": "2023-06-28T23:59:59+02:00",
            "balance": 378.6,
            "type": "FLATEX_CASH_SWEEP",
            "description": "Degiro Cash Sweep Transfer",
        },
        {
            "value_date": "2023-06-28T23:59:59+02:00",
            "balance": 117.0,
            "type": "CASH_TRANSACTION",
            "description": "iDEAL Deposit",
        },
        {
            "value_date": "2023-06-28T23:59:59+02:00",
            "balance": -33.0,
            "type": "CASH_TRANSACTION",
            "description": "Reservation iDEAL / Sofort Deposit",
        },
    ]


@pytest.fixture
def target_meta():
    return {
        "name": "VOLVO CAR AB",
        "id": 20209472,
        "vwd_id": 956683606,
        "stock_currency": "SEK",
        "close_price": 42.76,
        "close_price_date": "2023-06-23",
        "last_price": 42.77,
        "fx_rate": 11.5833,
        "trans_fee": 4.9,
        "last_balance": 100,
    }


@pytest.fixture
def target_meta_negative():
    return {
        "name": "VOLVO CAR AB",
        "id": 20209472,
        "vwd_id": 956683606,
        "stock_currency": "SEK",
        "close_price": 42.76,
        "close_price_date": "2023-06-23",
        "last_price": 42.77,
        "fx_rate": 11.5833,
        "trans_fee": 4.9,
        "last_balance": 7.99,
    }


@pytest.fixture
def fake_analyzor():
    return TradingAnalyzor()


@pytest.fixture
def fake_prod_meta():
    return {
        "name": "Volvo Car AB",
        "id": "20209472",
        "vwd_id": "956683606",
        "stock_currency": "SEK",
        "close_price": 42.76,
        "close_price_date": "2023-06-29",
        "trans_fee": Decimal("4.9001"),
        "last_balance": Decimal("138.9200"),
        "fx_rate": Decimal("11.8064"),
        "code": "volcar_b",
        "last_price": Decimal("42.7701"),
        "response_datetime": "2023-06-30T17:20:27",
        "cashable": Decimal("133.6857"),
        "last_price_in_euro": Decimal("3.795"),
    }


@pytest.fixture
def fake_livermore(fake_prod_meta):
    return LivermoreTradingRule(fake_prod_meta)


@pytest.fixture
def fake_up():
    # Volcar_b
    return {
        "buy": [
            {"datetime": "2023-06-30T13:12:35", "price_in_euro": "3.4500"},
            {"datetime": "2023-06-30T13:12:32", "price_in_euro": "2.5000"},
        ],
        "sell": [
            {"datetime": "2023-06-30T13:13:32", "price_in_euro": "4.8500"},
        ],
    }


@pytest.fixture
def fake_down():
    return {
        "buy": [
            {"datetime": "2023-06-30T13:12:35", "price_in_euro": "4.2167"},
            {"datetime": "2023-06-30T13:12:32", "price_in_euro": "4.8500"},
            {"datetime": "2023-06-30T13:12:31", "price_in_euro": "3.7500"},
        ],
        "sell": [],
    }
