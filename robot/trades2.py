import pprint
from datetime import datetime
from alpaca_trade_api.entity import Order
import alpaca_trade_api as tradeapi

from typing import List
from typing import Union
from typing import Optional


class Trade2():

    def __init__(self, key: str, secretKey: str, baseUrl: str, account_number: str):

        self.api = tradeapi.REST(key,
                                 secretKey,
                                 baseUrl)

        self.order = {}
        self.trade_id = ""
        # long or short
        self.side = ""
        self.side_opposite = ""
        # self.enter_or_exit = ""
        # self.enter_or_exit_opposite = ""
        # from api
        self._order_response = None
        self._trigger_added = False
        self._multi_leg = False

    def create_trade(self, trade_id: str, order_type: str, side: str, symbol: str, qty: int,
                     price: int = 0, stop_limit_price: int = 0, trail_percentace: int = 0) -> dict:

        self.trade_id = trade_id
        self.order['order_type'] = order_type
        self.order['symbol'] = symbol
        self.order['side'] = side

        if side == 'buy':
            self.side = side
            self.side_opposite = 'sell'

        if side == 'sell':
            self.side = side
            self.side_opposite = 'buy'

        if self.order['order_type'] == 'market':
            o = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                client_order_id=trade_id
            )
            self.order['response'] = o

        if self.order['order_type'] == 'limit':
            self.order['limit_price'] = price
            o = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                limit_price=str(price),
                client_order_id=trade_id
            )
            self.order['response'] = o

        if self.order['order_type'] == 'stop':
            self.order['stop_price'] = price
            o = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                stop_price=str(price),
                client_order_id=trade_id
            )
            self.order['response'] = o

        if self.order['order_type'] == 'stop_limit':
            self.order['stop_price'] = price
            self.order['limit_price'] = stop_limit_price
            o = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                stop_price=str(price),
                limit_price=str(stop_limit_price),
                client_order_id=trade_id
            )
            self.order['response'] = o

        if self.order['order_type'] == 'trailing_stop':
            self.order['trail_percent'] = trail_percentace
            o = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                trail_percent=str(trail_percentace),
                client_order_id=trade_id
            )
            self.order['response'] = o

        pprint.pprint(self.order)
        return self.order
