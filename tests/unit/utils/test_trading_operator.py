from utils import TradingOperator


class TestTradingOperator:
    def test_get_account_cash_total(self, fake_acccount_overview):
        actual_overview = TradingOperator.get_movements_from_account_overview(
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
