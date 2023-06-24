from utils import TradingOperator


class TestTradingOperator:
    def test_get_account_cash_total(self, fake_acccount_overview):
        actual_overview = TradingOperator.get_account_overview(
            fake_acccount_overview
        )
        expected_overview = {
            "2023-06-16T12:49:23+02:00_1731629923.0_EUR": {
                "value_date": "2023-06-15T23:59:59+02:00",
                "balance": 1.6,
                "description": "Overboeking van uw geldrekening bij flatexDEGIRO Bank 0,27 EUR",  # noqa
                "type": "FLATEX_CASH_SWEEP",
            },
            "2023-06-15T16:09:07+02:00_1730366149.0_EUR": {
                "value_date": "2023-06-15T16:09:07+02:00",
                "balance": 30.27,
                "description": "Reservation iDEAL / Sofort Deposit",
                "type": "CASH_TRANSACTION",
            },
            "2023-06-15T16:11:58+02:00_393047611.0_SEK": {
                "value_date": "2023-06-15T16:11:58+02:00",
                "balance": -43.68,
                "description": "Koop 1 @ 43,68 SEK",
                "type": "TRANSACTION",
            },
        }

        assert actual_overview == expected_overview
