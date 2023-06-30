from degiro_connector.trading.models.trading_pb2 import (  # noqa
    OrdersHistory,
    TransactionsHistory,
    AccountOverview,
    CashAccountReport,
)

from my_logger import logger
from toolkits import sort_dict_string_content


class BaseRequestOnDate:
    """A factory with init_subclass to instantiate
    various type of object base on date
    """

    subclasses = {}
    __slots__ = ("request", "history")

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls._HIST_TYPE] = cls

    def __init__(self) -> None:
        self.request = None

    @classmethod
    def create(cls, hist_type, **params):
        if hist_type not in cls.subclasses:
            raise ValueError(f"{hist_type} not exist")

        cls = cls.subclasses[hist_type]
        request_object = cls()
        request_object._prepare_request(**params)

        return request_object

    def _prepare_request(self, **params):
        from_date = self.request_type.Date(
            year=params["from_year"],
            month=params["from_mon"],
            day=params["from_day"],
        )

        to_date = self.request_type.Date(
            year=params["to_year"],
            month=params["to_mon"],
            day=params["to_day"],
        )

        self.request = self.request_type(from_date=from_date, to_date=to_date)


class RequestOrdersHistory(BaseRequestOnDate):
    _HIST_TYPE = "order"
    request_type = OrdersHistory.Request

    def get_response(self, api):
        history = api.get_orders_history(
            request=self.request,
            raw=False,
        )

        self.history = [dict(order) for order in history.values]


class RequestTransactionsHistory(BaseRequestOnDate):
    _HIST_TYPE = "transaction"
    request_type = TransactionsHistory.Request

    def get_response(self, api):
        history = api.get_transactions_history(
            request=self.request,
            raw=False,
        )

        self.history = [dict(order) for order in history.values]


class RequestAccountHistoryOverview(BaseRequestOnDate):
    _HIST_TYPE = "account"
    request_type = AccountOverview.Request

    def get_response(self, api):
        history = api.get_account_overview(
            request=self.request,
            raw=False,
        )

        self.history = history.values

        if not self.history:
            logger.error(
                f"{self._HIST_TYPE}: {self.request} returns empty history"
            )
            self.history = []


class RequestCashAccountReport(BaseRequestOnDate):
    _HIST_TYPE = "cash"
    request_type = CashAccountReport.Request

    def __init__(self) -> None:
        super().__init__()
        self.format = None

    def get_response(self, api):
        report = api.get_cash_account_report(
            request=self.request,
            raw=False,
        )

        self.format = report.Format.Name(report.format)
        self.history = sort_dict_string_content(report.content)
