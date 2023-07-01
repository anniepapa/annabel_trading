""" # noqa
The "Livermore Rule" you mentioned is indeed associated with a pyramiding strategy.
It is named after Jesse Livermore, a famous trader from the early 20th century.
Jesse Livermore was known for his successful trading career and his insights into market dynamics.
The Livermore Rule or Livermore Pyramiding Rule refers to a strategy of adding to winning positions as 
    the price moves in a favorable direction. The idea is to increase the position size and 
    leverage potential profits during strong trends. Livermore would add to his winning trades in 
    increments, allowing him to maximize his gains during significant market moves.

Livermore's approach to pyramiding involved the following principles:
- Initial Position: Enter the market with a smaller initial position size.
- Confirmation of Strength: Only add to the position if the stock's price confirms the expected trend. 
    Livermore emphasized the importance of waiting for confirmation before increasing the position size.
- Incremental Increases: Add to the position in stages or increments as the price continues to move 
    favorably. Each addition to the position is based on specific price levels or predetermined criteria.
- Trailing Stop-Loss: Use a trailing stop-loss order to protect profits and manage risk. Livermore would 
    adjust his stop-loss level as the position increased to protect against substantial reversals.
- Flexibility: Livermore understood the importance of adapting to changing market conditions. He would 
    exit the position if the market showed signs of a reversal or if his stop-loss order was triggered.

Livermore's pyramiding strategy aimed to capitalize on major market moves while managing risk through the 
    use of trailing stop-loss orders. It allowed him to maximize profits during trending markets and 
    scale back exposure during potential reversals.
It's worth noting that while the Livermore Rule can be a profitable strategy during strong trends, 
    it also carries risks. Adding to positions increases your exposure and can lead to larger losses if 
    the market turns against you. Risk management, including the use of stop-loss orders, is crucial when 
    implementing a pyramiding strategy.
"""
from decimal import Decimal


class TestLivermoreRule:
    def test_analyze_trend_up(self, fake_livermore, fake_up):
        fake_livermore.pivot_hist = fake_up
        fake_livermore.analyze_trend()
        assert fake_livermore.ratio_diff >= Decimal("0.1")
        assert fake_livermore.state == 1

    def test_analyze_trend_down(self, fake_livermore, fake_down):
        fake_livermore.pivot_hist = fake_down
        fake_livermore.analyze_trend()
        assert fake_livermore.ratio_diff <= Decimal("-0.1")
        assert fake_livermore.state == -1

    # def test_livermorerule_analyze_product_price(
    #     self, fake_livermore, fake_product
    # ):
    #     fake_livermore.analyze_price(fake_product)

    #     assert fake_livermore.price_down_20_percent is True
    #     assert fake_livermore.match_sell is True
    #     assert fake_livermore.match_buy is False
