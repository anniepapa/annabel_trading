from decimal import Decimal
from toolkits import decimalize

from models import LivermoreTradingRule


def test_livermore_integration(fake_prod_meta):
    fake_livermore = LivermoreTradingRule(fake_prod_meta)
    fake_livermore.analyze()

    new_position = decimalize(Decimal("0.2") * fake_prod_meta["cashable"])

    assert fake_livermore.prod_meta["last_balance"] == new_position
    assert fake_livermore.capacity == 5
