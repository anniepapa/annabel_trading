from utils import BaseRequestOnDate


class TestBaseRequestOnDate:
    def test_subclass_factory_creates_different_objects(
        self, fake_from_to_date
    ):
        history_1 = BaseRequestOnDate.create("order", **fake_from_to_date)
        history_2 = BaseRequestOnDate.create("order", **fake_from_to_date)

        assert id(history_1.request) != id(history_2.request)
