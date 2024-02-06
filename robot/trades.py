from datetime import datetime

from typing import List
from typing import Union
from typing import Optional


class Trade():

    def __init__(self):

        self.order = {}
        self.trade_id = ""
        # long or short
        self.side = ""
        self.side_opposite = ""
        self.enter_or_exit = ""
        self.enter_or_exit_opposite = ""
        # from api
        self._order_response = {}
        self._trigger_added = False
        self._multi_leg = False

    def new_trade(self, trade_id: str, order_type: str, side: str, enter_or_exit: str, price: float = 0.0,
                  stop_limit_price: float = 0.0) -> dict:

        self.trade_id = trade_id

        self.order_types = {
            'mkt': 'MARKET',
            'lmt': 'LIMIT',
            'stop': 'STOP',
            'stop_lmt': 'STOP_LIMIT',
            'trailing_stop': 'TRAILING_STOP'
        }

        self.order_instructions = {
            'enter': {
                'long': 'BUY',
                'short': 'SELL_SHORT'
            },
            'exit': {
                'long': 'SELL',
                'short': 'BUY_TO_COVER'
            }
        }

        self.order = {
            "orderStrategyType": "SINGLE",
            "orderType": self.order_types[order_type],
            "session": "NORMAL",
            "duration": "DAY",
            "orderLegCollection": [
                {
                    "instruction": self.order_instructions[enter_or_exit][side],
                    "quantity": 0,
                    "instrument": {
                        "symbol": None,
                        "assetType": None
                    }
                }
            ]
        }

        if self.order['orderType'] == 'STOP':
            self.order['stopPrice'] = price

        elif self.order['orderType'] == 'LIMIT':
            self.order['price'] = price

        elif self.order['orderType'] == 'STOP_LIMIT':
            self.order['stopPrice'] = price
            self.order['price'] = stop_limit_price

        elif self.order['orderType'] == 'TRAILING_STOP':
            self.order['stopPriceLinkBasis'] = ""
            self.order['stopPriceLinkBasis'] = ""
            self.order['stopOffset'] = 0.00
            self.order['stopType'] = 'STANDARD'

        self.enter_or_exit = enter_or_exit
        self.side = side
        self.order_types = order_type
        self.price = price

        if order_type == 'stop':
            self.stop_price = price
        elif order_type == 'stop-lmt':
            self.stop_price = price
            self.stop_limit_price = stop_limit_price
        else:
            self.stop_price = 0.0

            # Set the enter or exit state.
        if self.enter_or_exit == 'enter':
            self.enter_or_exit_opposite = 'exit'
        if self.enter_or_exit == 'exit':
            self.enter_or_exit_opposite = 'enter'

            # Set the side state.
        if self.side == 'long':
            self.side_opposite = 'short'
        if self.side == 'short':
            self.side_opposite = 'long'

    def instrument(self, symbol: str, quantity: int, asset_type: str, sub_asset_type: str = None,
                   order_leg_id: int = 0) -> dict:

        leg = self.order['orderLegCollection'][order_leg_id]

        leg['instrumetn']['symbol'] = symbol
        leg['instrumet']['assetType'] = asset_type
        leg['quantity'] = quantity

        self.order_size = quantity
        self.symbol = symbol
        self.asset_type = asset_type

        return leg

    def good_till_cancel(self, cancel_time: datetime) -> None:

        self.order['duration'] = 'GOOD_TILL_CANCEL'
        self.order['cancelTime'] = cancel_time.isoformat()

    def modify_side(self, side: Optional[str], order_leg_id: int = 0) -> None:

        if side and side not in ['buy', 'sell', 'sell_shot', 'buy_to_cover']:
            raise ValueError("You passed though an invalid side")

        if side:
            self.order['orderLegCollection'][order_leg_id]['instructions'] = side.upper()
        else:
            self.order['orderLegCollection'][order_leg_id]['instructions'] = self.order_instructions[self.enter_or_exit_opposite][self.side_opposite]

    def add_box_range(self, profit_size: float = 0.00, stop_size: float = 0.00,
                      stop_percentage: bool = False, profit_percentage: bool = False,
                      stop_limit: bool = False, make_one_cancels_other: bool = True,
                      limit_size: float = 0.00, limit_percentage: bool = False):

        if not self._triggered_added:
            self._convert_to_trigger()

        # Add a take profit Limit order.
        self.add_take_profit(
            profit_size=profit_size,
            percentage=profit_percentage
        )

        if not stop_limit:
            self.add_stop_loss(stop_size=profit_size,
                                percentage=profit_percentage)


    def add_stop_loss(self,stop_size: float, percentage: bool=False) -> bool:

        if not self._trigger_added:
            self._convert_to_trugger()

        if self.order_type == 'mkt':
            pass
        elif self.order_type == 'lmt':
            price = self.price

        if percentage:
            adjustment = 1.0 - stop_size
            new_price = self._calculate_new_price(price=price, adjustment=adjustment,percentage=True)
        else:
            adjustment = -stop_size
            new_price = self._calculate_new_price(price=price, adjustment=adjustment,percentage=False)

        stop_loss_order = {
            "orderType": "STOP",
            "session": "NORMAL",
            "duration": "DAY",
            "stopPrice": new_price,
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": self.order_instructions[self.enter_or_exit_opposite][self.side],
                    "quantity": self.order_size,
                    "instrument": {
                        "symbol": self.symbol,
                        "assetType": self.asset_type
                    }
                }
            ]
        }

        self.stop_loss_order = stop_loss_order
        self.order['childOrderStrategies'].append(self.stop_loss_order)

        return True

    def add_stop_limit(self, stop_size: float, limit_size: float, stop_percentage: bool = False,
                       limit_percentage: bool = False):


        # Check to see if there is a trigger.
        if not self._triggered_added:
            self._convert_to_trigger()

        price = self.grab_price()

        # Calculate the Stop Price.
        if stop_percentage:
            adjustment = 1.0 - stop_size
            stop_price = self._calculate_new_price(
                price=price,
                adjustment=adjustment,
                percentage=True
            )
        else:
            adjustment = -stop_size
            stop_price = self._calculate_new_price(
                price=price,
                adjustment=adjustment,
                percentage=False
            )

        # Calculate the Limit Price.
        if limit_percentage:
            adjustment = 1.0 - limit_size
            limit_price = self._calculate_new_price(
                price=price,
                adjustment=adjustment,
                percentage=True
            )
        else:
            adjustment = -limit_size
            limit_price = self._calculate_new_price(
                price=price,
                adjustment=adjustment,
                percentage=False
            )

        # Add the order.
        stop_limit_order = {
            "orderType": "STOP_LIMIT",
            "session": "NORMAL",
            "duration": "DAY",
            "price": limit_price,
            "stopPrice": stop_price,
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": self.order_instructions[self.enter_or_exit_opposite][self.side],
                    "quantity": self.order_size,
                    "instrument": {
                        "symbol": self.symbol,
                        "assetType": self.asset_type
                    }
                }
            ]
        }

        self.stop_limit_order = stop_limit_order
        self.order['childOrderStrategies'].append(self.stop_limit_order)

        return True

    def _calculate_new_price(self, price: float, adjustment: float, percentage: bool) -> float:

        if percentage:
            new_price = price * adjustment
        else:
            new_price = price + adjustment

        # For orders below $1.00, can only have 4 decimal places.
        if new_price < 1:
            new_price = round(new_price, 4)

        # For orders above $1.00, can only have 2 decimal places.
        else:
            new_price = round(new_price, 2)

        return new_price