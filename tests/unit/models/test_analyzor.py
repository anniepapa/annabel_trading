import pytest


class TestTradingAnalyzor:
    def test_analyze_capacity(self, fake_analyzor, target_meta):
        fake_analyzor.analyze_capacity(target_meta)
        assert fake_analyzor.capacity == 26
        fake_analyzor.act_on_capacity()

    @pytest.fixture
    def test_analyze_insufficient_capacity(
        self, fake_analyzor, target_meta_negative
    ):
        fake_analyzor.analyze_capacity(target_meta_negative)
        assert fake_analyzor.capacity < 1

        return fake_analyzor

    def test_act_on_analysis(self, test_analyze_insufficient_capacity):
        test_analyze_insufficient_capacity.act_on_capacity()
        assert test_analyze_insufficient_capacity.cashable_state is False
