from toolkits import utc_to_cet, get_last_valuta_balance


class TestToolkits:
    def test_utc_to_cet(self):
        actual_cet = utc_to_cet("2023-06-26T12:50:01.718021Z")
        assert actual_cet == "2023-06-26T14:50:01"

    def test_get_last_valuta_balance_ideal_deposit_positive(
        self, fake_cash_movements_ideal_deposit_positive
    ):
        actual_last_balance = str(
            get_last_valuta_balance(fake_cash_movements_ideal_deposit_positive)
        )
        expected_last_balance = "138.92"

        assert actual_last_balance == expected_last_balance

    def test_get_last_valuta_balance_valuta_debitering_positive(
        self, fake_cash_movements_valuta_debitering_positive
    ):
        actual_last_balance = str(
            get_last_valuta_balance(
                fake_cash_movements_valuta_debitering_positive
            )
        )
        expected_last_balance = "138.92"

        assert actual_last_balance == expected_last_balance
