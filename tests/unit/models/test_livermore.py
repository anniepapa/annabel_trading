from models import LivermoreTradingRule


class TestLivermoreRule:
    def test_livermorerule_analyze(self, fake_product):
        livermore = LivermoreTradingRule()
        livermore.analyze(fake_product)

        assert livermore.price_down_20_percent is True
        assert livermore.match_sell is True
        assert livermore.match_buy is False
