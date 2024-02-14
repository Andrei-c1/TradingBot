import pprint
from datetime import datetime, timedelta, timezone
import random
from typing import List, Optional
import time as time_true

import pytz

from robot import config
from robot.helper import Helper
from robot.trades import Trade2

import alpaca_trade_api as tradeapi
from alpaca_trade_api.entity import Bar

from alpaca_trade_api.entity_v2 import QuotesV2
from alpaca_trade_api import TimeFrame
from alpaca_trade_api import TimeFrameUnit

from robot.portfolio import Portfolio
from robot.stock_frame import StockFrame


class PyRobot():

    def __init__(self, key: str, secretKey: str, baseUrl: str, account_number: str) -> None:
        self.api = tradeapi.REST(key,
                                 secretKey,
                                 baseUrl)
        self.trades_to_execute: dict = {}
        self.historical_prices: dict = {}
        self.stock_frame = None
        self.account_numer = account_number
        print(type(self.api))

    def get_account(self):
        return self.api.get_account()

    def create_porfolio(self) -> Portfolio:
        # initialize a new portfolio obj
        self.portolio = Portfolio(self.account_numer)
        # assiagn the client
        self.portolio.api_client = self.api
        return self.portolio

    def create_trade_to_exectue(self, trade_id: str, order_type: str, side: str, symbol: str, qty: int,
                                price: int = 0, stop_limit_price: int = 0, trail_percentace: int = 0) -> None:

        trade_to_exectue = {}
        trade_to_exectue['trade_id'] = trade_id
        trade_to_exectue['order_type'] = order_type
        trade_to_exectue['side'] = side
        trade_to_exectue['sybmol'] = symbol
        trade_to_exectue['qty'] = qty
        trade_to_exectue['price'] = price
        trade_to_exectue['stop_limit_price'] = stop_limit_price
        trade_to_exectue['trail_percentace'] = trail_percentace

        self.trades_to_execute[trade_id] = trade_to_exectue

    def execute_trade(self, trade: dict):

        ex_trade = Trade2(config.ALPACA_API_KEY, config.ALPACA_API_SECRET_KEY, config.APCA_API_BASE_URL,
                          config.ACCOUNT_NUMBER)

        ex_trade.create_trade(
            trade_id=f"gcos_{random.randrange(100000000)}",
            order_type=trade['order_type'],
            side=trade['side'],
            symbol=trade['sybmol'],
            qty=trade['qty'],
            price=trade['price'],
            stop_limit_price=trade['stop_limit_price'],
            trail_percentace=trade['trail_percentace']

        )

        # initialazi a nre trade obj
        # trade = Trade2(config.ALPACA_API_KEY, config.ALPACA_API_SECRET_KEY, config.APCA_API_BASE_URL, config.ACCOUNT_NUMBER)
        #
        # #create a new trade
        # trade.create_trade(
        #     trade_id=trade_id,
        #     order_type=order_type,
        #     side=side,
        #     symbol=symbol,
        #     qty=qty,
        #     trail_percentace=trail_percentace,
        #     price=price,
        #     stop_limit_price=stop_limit_price
        # )
        #
        # #dictonary for trade, collection of trade obj
        # self.trades[trade_id] = trade
        # return trade

    def create_stock_frame(self, data: List[dict]) -> StockFrame:

        self.stock_frame = StockFrame(data=data)
        return self.stock_frame

    def get_current_quotes(self) -> QuotesV2:
        # return all the keys in posiosnt
        symbols = self.portolio.positions.keys()
        quotes = self.api.get_quotes(symbol=list(symbols))

        return quotes

    def get_historical_price(self, start: str, end: str, bar_size: int = 1, bar_time: str = 'Min',
                             symbols: Optional[List[str]] = None) -> dict:

        self._bar_size = bar_size
        self._bar_time = bar_time

        time_frame = TimeFrame(bar_size, TimeFrameUnit(bar_time))

        new_prices = []

        if not symbols:
            symbols = self.portolio.positions

        for symbol in symbols:
            hystorical_price_response = self.api.get_bars(
                symbol=symbols,
                timeframe=time_frame,
                start=str(start),
                end=str(end)
            )

            self.historical_prices[symbol] = {}
            self.historical_prices[symbol]['candels'] = hystorical_price_response.__dict__['_raw']

            for candle in hystorical_price_response.__dict__['_raw']:
                new_price_mini_dict = {}
                new_price_mini_dict['symbol'] = symbol
                new_price_mini_dict['open'] = candle['o']
                new_price_mini_dict['close'] = candle['c']
                new_price_mini_dict['high'] = candle['h']
                new_price_mini_dict['low'] = candle['l']
                new_price_mini_dict['volume'] = candle['v']
                new_price_mini_dict['datetime'] = Helper.get_date_object(candle['t'])
                new_prices.append(new_price_mini_dict)

        self.historical_prices['aggregated'] = new_prices
        # pprint.pprint(self.historical_prices['aggregated'])

        return self.historical_prices

    def get_latest_bar(self, symbols: List[str]) -> List[dict]:
        bar_size = self._bar_size
        bar_time = self._bar_time
        print(bar_size, bar_time)

        time_frame = TimeFrame(bar_size, TimeFrameUnit(bar_time))

        latest = []

        end_date = datetime.today() - timedelta(days=1)
        end_date = end_date.replace(tzinfo=pytz.UTC)
        start_date = end_date - timedelta(days=30)
        start_date = start_date.replace(tzinfo=pytz.UTC)

        for symbol in symbols:
            print(symbol)
            hystorical_price_response = self.api.get_bars(
                symbol=symbol,
                timeframe=time_frame,
                start=str(start_date.isoformat()),
                end=str(end_date.isoformat()),
            )

            for candle in hystorical_price_response.__dict__['_raw'][-1:]:
                new_price_mini_dict = {}
                new_price_mini_dict['symbol'] = symbol
                new_price_mini_dict['open'] = candle['o']
                new_price_mini_dict['close'] = candle['c']
                new_price_mini_dict['high'] = candle['h']
                new_price_mini_dict['low'] = candle['l']
                new_price_mini_dict['volume'] = candle['v']
                new_price_mini_dict['datetime'] = Helper.get_date_object(candle['t'])
                latest.append(new_price_mini_dict)

        return latest

    def wait_till_next_bar(self):

        # To Do: working solution

        # last_bar_time = latest_bar_time.replace(tzinfo=timezone.utc)
        # print(last_bar_time)
        # next_bar_time = last_bar_time + timedelta(seconds=60)
        # print(next_bar_time)
        # curr_bar_time = datetime.now(tz=timezone.utc) - timedelta(days=1)
        # print(curr_bar_time)
        #
        # last_bar_timestamp = int(last_bar_time.timestamp())
        # print(last_bar_timestamp)
        # print(datetime.utcfromtimestamp(last_bar_timestamp))
        # next_bar_timestamp = int(next_bar_time.timestamp())
        # print(next_bar_timestamp)
        # print(datetime.utcfromtimestamp(next_bar_timestamp))
        # curr_bar_timestamp = int(curr_bar_time.timestamp())
        # print(curr_bar_timestamp)
        # print(datetime.utcfromtimestamp(curr_bar_timestamp))
        #
        # time_to_wait_now = next_bar_timestamp - curr_bar_timestamp
        #
        # if time_to_wait_now < 0:
        #     time_to_wait_now = 0
        #
        # print("Sleep Time: {seconds}".format(seconds=time_to_wait_now))
        # print("-" * 80)
        # print('')

        time_true.sleep(62)

    @property
    def pre_market_open(self) -> bool:

        pre_market_start_time = datetime.utcnow().replace(
            hour=8,
            minute=00,
            second=00
        ).timestamp()

        market_start_time = datetime.utcnow().replace(
            hour=13,
            minute=30,
            second=00
        ).timestamp()

        right_now = datetime.utcnow().timestamp()

        if market_start_time >= right_now >= pre_market_start_time:
            return True
        else:
            return False

    @property
    def post_market_open(self):

        post_market_end_time = datetime.utcnow().replace(
            hour=00,
            minute=00,
            second=00
        ).timestamp()

        market_end_time = datetime.utcnow().replace(
            hour=20,
            minute=00,
            second=00
        ).timestamp()

        right_now = datetime.utcnow().timestamp()

        if post_market_end_time >= right_now >= market_end_time:
            return True
        else:
            return False

    @property
    def regular_market_open(self):

        market_start_time = datetime.utcnow().replace(
            hour=13,
            minute=30,
            second=00
        ).timestamp()

        market_end_time = datetime.utcnow().replace(
            hour=20,
            minute=00,
            second=00
        ).timestamp()

        right_now = datetime.utcnow().timestamp()

        if market_end_time >= right_now >= market_start_time:
            return True
        else:
            return False
