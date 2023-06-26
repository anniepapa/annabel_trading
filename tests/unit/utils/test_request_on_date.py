from my_logger import logger
from utils import BaseRequestOnDate, sort_dict_string_content


class TestBaseRequestOnDate:
    def test_subclass_factory_creates_different_objects(
        self, fake_from_to_date
    ):
        history_1 = BaseRequestOnDate.create("order", **fake_from_to_date)
        history_2 = BaseRequestOnDate.create("order", **fake_from_to_date)

        logger.info(f"{history_1.request}, {history_2.request}")

        assert id(history_1) != id(history_2)
        assert history_1.request == history_2.request

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
