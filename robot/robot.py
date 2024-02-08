import pprint
from datetime import datetime
from typing import List, Optional
from robot.helper import Helper

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
        self.trades: dict = {}
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

    def create_trade(self):
        pass

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
