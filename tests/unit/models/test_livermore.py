from models import LivermoreTradingRule


class TestLivermoreRule:
    def test_livermorerule(self, fake_product):
        livermore = LivermoreTradingRule()
        livermore.analyze(fake_product)
        livermore.trade()

        assert livermore.price_down_20_percent is True
        assert livermore.action_type == "s"
