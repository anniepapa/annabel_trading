from logger import logger

from degiro_connector.quotecast.models.quotecast_pb2 import Quotecast
from degiro_connector.quotecast.models.quotecast_parser import QuotecastParser
from degiro_connector.quotecast.api import API as QuotecastAPI


class FinancialProductConsumer:
    def __init__(self, user_token):
        self.quotecast_api = self._connect(user_token)
        self.realtime_dict = None
        self.realtime_df = None

    def subscribe(self, *vwdids):
        """_summary_

        Args:
            list_of_vwdid (_type_): _description_
            e.g: vwdId of VOLVO CAR AB: '956683606'

        Returns:
            _type_: _description_
        """
        quotecast_parser = QuotecastParser()
        request = Quotecast.Request()

        for vwdid in vwdids:
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
            f"vwdIds: {vwdids} have been subscribed by {self.quotecast_api}"
        )

        # ticker_dict = self.quotecast_api.fetch_metrics(
        #     request=request,
        # )

        quotecast_parser.put_quotecast(
            quotecast=self.quotecast_api.fetch_data()
        )
        self.realtime_dict = quotecast_parser.ticker_dict
        self.realtime_df = quotecast_parser.ticker_df

        logger.info(f"The price of {vwdids} have been fetched")

    def _connect(self, user_token):
        quotecast_api = QuotecastAPI(user_token=user_token)
        quotecast_api.connect()
        logger.info(f"Product consumer: {quotecast_api} is connected")
        return quotecast_api
