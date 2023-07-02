import pytest
from my_logger import logger
from utils import BaseRequestOnDate, sort_dict_string_content


class TestBaseRequestOnDate:
    @pytest.fixture
    def test_subclass_factory_creates_different_objects(
        self, fake_from_to_date
    ):
        history_1 = BaseRequestOnDate.create("account", **fake_from_to_date)
        history_2 = BaseRequestOnDate.create("account", **fake_from_to_date)

        logger.info(f"{history_1.request}, {history_2.request}")

        assert id(history_1) != id(history_2)
        assert history_1.request == history_2.request

        return history_1

    def test_sort_dict_string_content(
        self, fake_account_cash_movements_report
    ):
        actual_sorted_content = sort_dict_string_content(
            fake_account_cash_movements_report
        )

        expected_sorted_content = [
            {
                "": "1,60",
                "Datum": "19-06-2023",
                "FX": "",
                "ISIN": "",
                "Mutatie": "",
                "Omschrijving": "Overboeking van uw geldrekening bij flatexDEGIRO Bank 28,4 EUR",  # noqa
                "Order Id": "",
                "Product": "",
                "Saldo": "EUR",
                "Tijd": "16:50",
                "Valutadatum": "19-06-2023",
            },
            {
                "": "30,00",
                "Datum": "19-06-2023",
                "FX": "",
                "ISIN": "NLFLATEXACNT",
                "Mutatie": "EUR",
                "Omschrijving": "Degiro Cash Sweep Transfer",
                "Order Id": "",
                "Product": "FLATEX EURO BANKACCOUNT",
                "Saldo": "EUR",
                "Tijd": "16:50",
                "Valutadatum": "19-06-2023",
            },
            {
                "": "-28,40",
                "Datum": "17-06-2023",
                "FX": "",
                "ISIN": "",
                "Mutatie": "EUR",
                "Omschrijving": "Reservation iDEAL / Sofort Deposit",
                "Order Id": "",
                "Product": "",
                "Saldo": "EUR",
                "Tijd": "04:51",
                "Valutadatum": "16-06-2023",
            },
        ]

        assert actual_sorted_content[:3] == expected_sorted_content

    def test_get_account_cash_total(
        self,
        fake_acccount_overview,
        test_subclass_factory_creates_different_objects,
    ):
        actual_overview = test_subclass_factory_creates_different_objects._get_movements_from_account_overview(  # noqa
            fake_acccount_overview
        )

        expected_overview = [
            {
                "value_date": "2023-06-15T23:59:59+02:00",
                "balance": 1.6,
                "description": "Overboeking van uw geldrekening bij flatexDEGIRO Bank 0,27 EUR",  # noqa
                "type": "FLATEX_CASH_SWEEP",
            },
            {
                "value_date": "2023-06-15T16:11:58+02:00",
                "balance": -43.68,
                "description": "Koop 1 @ 43,68 SEK",
                "type": "TRANSACTION",
            },
            {
                "value_date": "2023-06-15T16:09:07+02:00",
                "balance": 30.27,
                "description": "Reservation iDEAL / Sofort Deposit",
                "type": "CASH_TRANSACTION",
            },
        ]

        assert actual_overview == expected_overview
