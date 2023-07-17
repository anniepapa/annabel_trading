import sys
from datetime import datetime, timedelta
from decimal import Decimal

from google.cloud import firestore
import degiro_connector.core.helpers.pb_handler as payload_handler
from degiro_connector.trading.models.trading_pb2 import (  # noqa
    ProductSearch,
    ProductsInfo,
    Order,
    Update,
)

from utils import BaseRequestOnDate
from my_logger import logger
from toolkits import decimalize, get_last_valuta_balance


class TradingOperator:
    __slots__ = (
        "trading_api",
        "keyword",
        "code",
        "order_created",
        "order_confirmed",
        # "config",
        # "client_details",
        "account_info",
        "product_id",
        "prod",
        "prod_meta",
        "updates",
        "portfolio",
        "doc_price",
    )

    def __init__(self, keyword, code, trading_api=None):
        self.trading_api = trading_api
        self.keyword = keyword
        self.code = code.lower().replace(" ", "_")

        self.order_created = False
        self.order_confirmed = False

        # self.config = self._get_config()
        # self.client_details = self._get_client_details()
        self.account_info = self._get_account_info()
        self.product_id = None
        self.prod = None
        self.prod_meta = self.initiate_prod_meta_from_str()
        self.updates = self._get_pending_order()
        self.portfolio = None
        self.doc_price = None

        self.prod_meta.update(
            {
                "fx_rate": self._get_fx_rate(self.prod_meta["stock_currency"]),
                "code": self.code.replace(" ", "_"),
                "hold_qty": self._get_hold_qty(),
                "last_balance": self._get_last_balance_via_updates(),
            }
        )
        self._get_last_transaction_price()

    def initiate_prod_meta_from_str(self):
        """
        example: 'vOvlVO cAr', 'volcar b'
        """
        request = ProductSearch.RequestLookup(
            search_text=self.keyword,
            limit=10,
            offset=0,
            product_type_id=1,
        )

        products = self.trading_api.product_search(request=request)
        prods = payload_handler.message_to_dict(message=products)["products"]

        for prod in prods:
            if prod["symbol"].lower().replace(" ", "_") == self.code:
                logger.info(
                    f"Product matches {self.keyword} and {self.code}: {prod}"
                )
                self.prod = prod
                prod_meta = {
                    "name": prod["name"],
                    "id": str(prod["id"]),
                    "vwd_id": prod["vwdId"],
                    "stock_currency": prod["currency"],
                    "close_price": decimalize(prod["closePrice"], prec=".01"),
                    "close_price_date": prod["closePriceDate"],
                }
                break
        else:
            logger.error(f"{prod['symbol']} and {self.code} has no match")
            sys.exit()

        return prod_meta

    def check_hold_status(self):
        db = firestore.Client(project="avian-volt-391821")
        self.doc_price = db.collection(self.prod_meta["code"])

        if not self.prod_meta["hold_qty"]:
            self._store_the_last_price()
            sold_hist = self.__get_last_records("transaction", buysell="S")[0]
            sold_price = decimalize(sold_hist["price"])
            last_price = self.prod_meta["last_price"]

            diff = abs(Decimal(last_price)) - abs(Decimal(sold_price))
            ratio = decimalize(diff / Decimal(Decimal(last_price)))

            logger.warning(
                f"🎈🎈 Zero hold of {self.prod_meta['name']}. "
                f"The last price you sold: {sold_price}. "
                f"Annabel finds the last price of today: "
                f"{last_price}. The diff since last "
                f"sold: {ratio*100}% on {sold_hist['date']}."
            )

            if not self.check_pending_order():
                self._self_order()

            raise SystemExit

        self._store_the_highest_price()

    def check_pending_order(self):
        for order in self.updates["orders"]["values"]:
            if str(order["product_id"]) == self.prod_meta["id"]:
                logger.info(f"{order['product']} has a pending order: {order}")
                self._check_pending_price(self, order)
                return True
        else:
            return False

    def _check_pending_price(self, order):
        if order["action"]:  # Sell
            # TODO
            pass
            # if self.prod_meta["last_price"] < Decimal(order["stop_price"]):

            # else:
            #     logger.warning(
            #         f"last price: {self.prod_meta['last_price']} is higher "
            #         f"than your trigger price: {order['stop_price']}")

        else:  # Buy
            if self.prod_meta["last_price"] < Decimal(order["stop_price"]):
                logger.info(
                    f"🕵️‍♀️ last price: {self.prod_meta['last_price']} is "
                    f"lower than the trigger price: {order['stop_price']} "
                    f"of pending BUY order. Existing order will be deleted. "
                    f"A new order will be created with the last price."
                )
                self.trading_api.delete_order(order_id=order["id"])
                self.order(action_type="B")
            else:
                logger.warning(
                    f"last price: {self.prod_meta['last_price']} is higher "
                    f"than your trigger price: {order['stop_price']}"
                )

    def _self_order(self):
        minor_position = Decimal("0.15") * self.prod_meta["last_balance"]
        last_price = self.prod_meta["last_price_in_euro"]
        if minor_position > last_price:
            logger.info(
                f"Zero hold, no pending order. We will purchase 1 stock "
                f"using the last price (euro): {last_price}"
            )
            self.prod_meta["capacity"] = 1
            self.order(action_type="B")
        else:
            logger.warning(
                f"Zero hold, no pending order, also insufficient "
                f"20% cashable: {minor_position} to buy 1 {last_price}. \n"
                f"🎈🎈 Annabel will do nothing and exit."
            )

    def order(self, action_type):
        """stop limit BUY:  # noqa
            In a stop-limit buy order, the stop price should be set below the limit price.
            In addition, on degiro, seems stop price has to higher than the last price. Example:

            - last price: $24,70
            - stop price (minimal valid value): $24.71
            - limit sell (minimal valid value): $24.72

            This ensures that the order is triggered when the stock price falls to or below
                the stop price, and the subsequent limit order is executed at the specified
                limit price or better.

            stop limit SELL:
            - last price: $274,32
            - stop price (minimal valid value, equal or lower is allowed): $274,32 / 33
            - limit buy (minimal valid value, must lower than stop price): $274,31 / 32

            action: 1 == sell
            action: 0 == buy

        Args:
            action_type (str): _description_.
        """
        if abs(self.prod_meta["last_price"]) >= 1:
            stop_diff, price_diff = Decimal("0.01"), Decimal("0.02")
        else:
            stop_diff, price_diff = Decimal("0.001"), Decimal("0.002")

        if action_type == "B":
            action = Order.Action.BUY
            stop_price = self.prod_meta["last_price"] + stop_diff
            price = self.prod_meta["last_price"] + price_diff
            size = self.prod_meta["capacity"]

        else:
            action = Order.Action.SELL
            stop_price = self.prod_meta["last_price"] - stop_diff
            price = self.prod_meta["last_price"] - price_diff
            size = self.prod_meta["hold_qty"]

        logger.info(
            f"🤖 Annabel is ordering: {action_type} for {size}: "
            f"{self.prod_meta['name']} on {price} triggered on stop price: "
            f"{stop_price} base on last price: {self.prod_meta['last_price']}"
        )

        order = Order(
            action=action,
            order_type=Order.OrderType.STOP_LIMIT,
            stop_price=decimalize(stop_price, prec=".0001"),
            price=decimalize(price, prec=".0001"),
            product_id=int(self.prod_meta["id"]),
            size=size,
            time_type=Order.TimeType.GOOD_TILL_DAY,
        )

        # FETCH CHECKING_RESPONSE
        checking_response = self.trading_api.check_order(order=order)

        if checking_response:
            self.order_created = True

            # EXTRACT CONFIRMATION_ID
            confirmation_id = checking_response.confirmation_id

            # SEND CONFIRMATION
            confirmation_response = self.trading_api.confirm_order(
                confirmation_id=confirmation_id,
                order=order,
            )

            self.order_confirmed = (
                True
                if confirmation_response
                else logger.error("order not confirmed")
            )

        else:
            logger.critical("failed ordering")

    def get_history_response(self, type_of_hist, **kwargs):
        """Response of request of history / cash report

        Args:
            type_of_hist (_type_): _description_

        Returns:
            _type_: request object with attribute: .history or .content
            .content is only for the type: "cash"
        """
        request = BaseRequestOnDate.create(type_of_hist, **kwargs)
        request.get_response(api=self.trading_api)

        if not request.history:
            logger.warning(
                f"⚠ {request._HIST_TYPE}: {kwargs} returns empty history."
            )

        return request

    def get_products_from_ids(self, list_of_ids):
        """_summary_
        e.g: '20209472'

        Args:
            list_of_ids (_type_): _description_

        Returns:
            _type_: _description_
        """
        request = ProductsInfo.Request()
        request.products.extend(list_of_ids)

        products = self.trading_api.get_products_info(
            request=request,
            raw=True,
        )

        return products["data"].values()

    def _store_the_last_price(self):
        logger.info(
            "🎨 You don't hold this stock, the last highest price "
            "equals the last price"
        )
        self.doc_price.document("price").set(
            {
                "date": str(datetime.now()),
                "highest_foreign": str(abs(self.prod_meta["last_price"])),
                "highest_euro": str(abs(self.prod_meta["last_price_in_euro"])),
            }
        )

    def _store_the_highest_price(self):
        logger.info(
            "🎨 You hold this stock, the last highest price and last "
            "price will be compared."
        )
        price_info = {}
        for doc in self.doc_price.stream():
            (price_info := doc.to_dict())
            logger.info(f"{doc.id}'s highest price: {price_info}")

        highest_price_today = decimalize(
            price_info.get("highest_foreign") or 0
        )

        if self.prod_meta["last_price"] > highest_price_today:
            self.doc_price.document("price").set(
                {
                    "date": str(datetime.now()),
                    "highest_foreign": str(abs(self.prod_meta["last_price"])),
                    "highest_euro": str(
                        abs(self.prod_meta["last_price_in_euro"])
                    ),
                }
            )
            logger.info(
                f"{self.prod_meta['name']} got a higher price! "
                f"foreign: {self.prod_meta['last_price']}, "
                f"euro: {self.prod_meta['last_price_in_euro']}"
            )

    def _get_fx_rate(self, stock_currency):
        if stock_currency.lower() == "eur":
            return decimalize("1.0")
        else:
            fx_code = "EUR" + stock_currency
            fx_rates = self.account_info["currencyPairs"]
            return decimalize(fx_rates[fx_code]["price"])

    def _get_config(self):
        config_table = self.trading_api.get_config()
        return config_table

    def _get_client_details(self):
        client_details_table = self.trading_api.get_client_details()
        return client_details_table

    def _get_account_info(self):
        account_info_table = self.trading_api.get_account_info()
        return account_info_table["data"]

    def _get_last_balance_via_updates(self):
        last_balance = self.updates["total_portfolio"]["values"][
            "freeSpaceNew"
        ]["EUR"]
        return decimalize(str(last_balance))

    def _get_last_balance_via_account_overview(self):
        cash_movements = self.__get_last_records("account")
        last_balance = get_last_valuta_balance(cash_movements)
        return decimalize(last_balance)

    def _get_last_balance_via_cash_report(self):  # to be tested more
        content_exists = self.__get_last_records("cash")

        content_of_last_balance = get_last_valuta_balance(
            content_exists, key_name="Omschrijving"
        )

        return decimalize(content_of_last_balance.replace(",", "."))

    def _get_last_transaction_price(self):
        self.product_id = self.prod_meta["id"]
        last_trans_details = self.__get_last_records("transaction")[0]

        if self.prod_meta["stock_currency"].lower() == "eur":
            price_in_base_currency = Decimal(last_trans_details["price"])
        else:
            price_in_base_currency = decimalize(
                Decimal(last_trans_details["price"])
                / Decimal(last_trans_details["nettFxRate"] or 1)
            )

        last_transaction = {
            last_trans_details["buysell"].lower(): {
                "transaction_datetime": last_trans_details["date"],
                "price_foreign": decimalize(last_trans_details["price"]),
                "last_buy_fx_rate": decimalize(
                    last_trans_details["nettFxRate"]
                ),
                "price_in_base_currency": price_in_base_currency,
                "quantity": decimalize(last_trans_details["quantity"]),
                "trans_fee_in_euro": decimalize(
                    last_trans_details["feeInBaseCurrency"]
                ),
                "autofx_rate_in_euro": decimalize(
                    last_trans_details["autoFxFeeInBaseCurrency"]
                ),
                "total_fees_in_euro": decimalize(
                    last_trans_details["totalFeesInBaseCurrency"]
                ),
                "total_plus_all_fees_in_euro": decimalize(
                    last_trans_details["totalPlusAllFeesInBaseCurrency"]
                ),
            }
        }

        self.prod_meta.update({"last_transaction_price": last_transaction})

    def _get_pending_order(self):
        request_list = Update.RequestList()
        request_list.values.extend(
            [
                Update.Request(option=Update.Option.ORDERS, last_updated=0),
                Update.Request(option=Update.Option.PORTFOLIO, last_updated=0),
                Update.Request(
                    option=Update.Option.TOTALPORTFOLIO, last_updated=0
                ),
            ]
        )

        update = self.trading_api.get_update(request_list=request_list)
        update_dict = payload_handler.message_to_dict(message=update)
        return update_dict

    def _get_hold_qty(self):
        for portfolio in self.updates["portfolio"]["values"]:
            if portfolio["id"] == self.prod_meta["id"]:
                logger.info(
                    f"{self.prod_meta['name']} has qty: {portfolio['size']}"
                )
                self.portfolio = portfolio
                return abs(int(portfolio["size"]))

    def __get_last_records(self, type_name, buysell="B"):
        today = datetime.now()
        to_year, to_mon, to_day = today.year, today.month, today.day
        history_records, d = [], 0

        while d <= 31 * 12 and not history_records:
            prev_week = today - timedelta(days=d)
            from_year, from_mon, from_day = (
                prev_week.year,
                prev_week.month,
                prev_week.day,
            )
            history_records = self.get_history_response(
                type_name,
                from_year=from_year,
                to_year=to_year,
                from_mon=from_mon,
                to_mon=to_mon,
                from_day=from_day,
                to_day=to_day,
            ).history

            if self.product_id:
                for record in history_records:
                    if (
                        int(record.get("productId")) == int(self.product_id)
                        and record["buysell"] == buysell
                    ):  # noqa
                        history_records = [record]
                        logger.info(
                            f"📆 Last history records of {type_name}: "
                            f"{buysell} exist on {record['date']}"
                        )
                        break

                else:
                    history_records = []

            d += 31

        if not history_records:
            logger.error(
                f"❓❓❓🧐 No any last {type_name} price exist "
                f"for {self.product_id} from the past {d} days. "
                f"Check if you have any transaction previously "
                f"or initiate a new entry manually for {self.keyword}. \n"
                f"🎈🎈 Annabel will exit."
            )
            raise SystemExit

        return history_records
