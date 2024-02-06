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

    def add_take_profit(self,profit_size: float, percentage: bool = False) -> bool:

        if not self._trigger_added:
            self._convert_to_trigger()

        price = self.grab_price()

        # Calculate the new price.
        if percentage:
            adjustment = 1.0 + profit_size
            new_price = self._calculate_new_price(
                price=price,
                adjustment=adjustment,
                percentage=True
            )
        else:
            adjustment = profit_size
            new_price = self._calculate_new_price(
                price=price,
                adjustment=adjustment,
                percentage=False
            )

        # Build the order.
        take_profit_order = {
            "orderType": "LIMIT",
            "session": "NORMAL",
            "price": new_price,
            "duration": "DAY",
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

        # Add the order.
        self.take_profit_order = take_profit_order
        self.order['childOrderStrategies'].append(self.take_profit_order)

        return True

    def _convert_to_triger(self):

        if self.order and not self._triggered_added:
            self.order['orderStrategyType'] = 'TRIGGER'

            # Trigger orders will have child strategies, so initalize that list.
            self.order['childOrderStrategies'] = []

            # Update the state.
            self._triggered_added = True

    def modify_session(self, session: str) -> None:

        if session in ['am', 'pm', 'normal', 'seamless']:
            self.order['session'] = session.upper()
        else:
            raise ValueError(
                'Invalid session, choose either am, pm, normal, or seamless')

    @property
    def order_response(self) -> dict:

        return self._order_response

    @order_response.setter
    def order_response(self, order_response_dict: dict) -> None:

        self._order_response = order_response_dict

    def _generate_order_id(self) -> str:

        # If we have an order, then generate it.
        if self.order:

            order_id = "{symbol}_{side}_{enter_or_exit}_{timestamp}"

            order_id = order_id.format(
                symbol=self.symbol,
                side=self.side,
                enter_or_exit=self.enter_or_exit,
                timestamp=datetime.now().timestamp()
            )

            return order_id

        else:
            return ""

    def add_leg(self, order_leg_id: int, symbol: str, quantity: int, asset_type: str, sub_asset_type: str = None) -> \
    List[dict]:

        # Define the leg.
        leg = {}
        leg['instrument']['symbol'] = symbol
        leg['instrument']['assetType'] = asset_type
        leg['quantity'] = quantity

        if sub_asset_type:
            leg['instrument']['subAssetType'] = sub_asset_type

        # If 0, call instrument.
        if order_leg_id == 0:
            self.instrument(
                symbol=symbol,
                asset_type=asset_type,
                quantity=quantity,
                sub_asset_type=sub_asset_type,
                order_leg_id=0
            )
        else:
            # Insert it.
            order_leg_colleciton: list = self.order['orderLegCollection']
            order_leg_colleciton.insert(order_leg_id, leg)

        return self.order['orderLegCollection']

    @property
    def number_of_legs(self) -> int:

        return len(self.order['orderLegCollection'])
