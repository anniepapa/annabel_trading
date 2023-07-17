from my_logger import logger

from degiro_connector.quotecast.models.quotecast_pb2 import Quotecast, Chart
from degiro_connector.quotecast.models.quotecast_parser import QuotecastParser
from degiro_connector.quotecast.api import API as QuotecastAPI


class FinancialProductConsumer:
    __slot__ = (
        "quotecast_api",
        "realtime_dict",
        "realtime_df",
    )

    def __init__(self, user_token=None):
        self.quotecast_api = self._connect(user_token)
        self.realtime_dict = None
        self.realtime_df = None

    def subscribe(self, vwdid):
        """_summary_

        Args:
            list_of_vwdid (_type_): _description_
            e.g: vwdId of VOLVO CAR AB: '956683606'

        Returns:
            _type_: _description_
        """
        quotecast_parser = QuotecastParser()
        request = Quotecast.Request()

        request.subscriptions[vwdid].extend(
            [
                "LastDate",
                "LastTime",
                "LastPrice",
                "LastVolume",
                "AskPrice",
                "AskVolume",
                "LowPrice",
                "HighPrice",
                "BidPrice",
                "BidVolume",
            ]
        )

        self.quotecast_api.subscribe(request=request)

        logger.info(
            f"vwdIds: {vwdid} have been subscribed by {self.quotecast_api}"
        )

        quotecast_parser.put_quotecast(
            quotecast=self.quotecast_api.fetch_data()
        )
        self.realtime_dict = quotecast_parser.ticker_dict[vwdid]
        self.realtime_df = quotecast_parser.ticker_df

        logger.info(f"The price of {vwdid} have been fetched")

    def _connect(self, user_token):
        quotecast_api = QuotecastAPI(user_token=user_token)
        quotecast_api.connect()
        logger.info(f"Product consumer: {quotecast_api} is connected")
        return quotecast_api

    def _get_chart(self, prod):
        request = Chart.Request()
        request.culture = "fr-FR"
        request.period = Chart.Interval.P1D
        request.requestid = "1"
        request.resolution = Chart.Interval.P5Y
        request.series.append(f"price:isin:{prod['isin']}")
        request.tz = "Europe/Paris"
        request.override["resolution"] = "P1D"
        request.override["period"] = "P5Y"

        # FETCH DATA
        chart = self.quotecast_api.get_chart(
            request=request,
            raw=True,
        )

        chart = {**chart, **prod}

        # DISPLAY
        logger.info(chart)
