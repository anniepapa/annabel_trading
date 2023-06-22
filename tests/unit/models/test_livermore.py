class TestLivermoreRule:
    def test_livermorerule_analyze_product_price(
        self, fake_livermore, fake_product
    ):
        fake_livermore.analyze_price(fake_product)

        assert fake_livermore.price_down_20_percent is True
        assert fake_livermore.match_sell is True
        assert fake_livermore.match_buy is False
