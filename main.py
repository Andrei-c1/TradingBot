import operator
import random
from datetime import datetime
from datetime import timezone
from datetime import timedelta

import pandas as pd

from robot.helper import Helper
from robot.indicator import Indicator

import pprint

import alpaca_trade_api as tradeapi
import pytz

# from robot.robot import PyRobot
from robot.robot import PyRobot
from alpaca_trade_api import TimeFrameUnit

from robot import config

robotOne = PyRobot(config.ALPACA_API_KEY, config.ALPACA_API_SECRET_KEY, config.APCA_API_BASE_URL, config.ACCOUNT_NUMBER)

acc = robotOne.get_account()
print(acc)
# print("CASH = " + acc.__getattr__('cash'))

# Create new porfolio
robotOne_porfolio = robotOne.create_porfolio()

# add positions
# multi_position = [
#     {
#         'asset_type': 'equity',
#         'quantity': 2,
#         'purchase_price': 4.00,
#         'symbol': 'TSLA',
#         'purchase_date': '2020-01-31'
#     },
#     {
#         'asset_type': 'equity',
#         'quantity': 2,
#         'purchase_price': 4.00,
#         'symbol': 'SQ',
#         'purchase_date': '2020-01-31'
#     }
# ]
#
# # add position to the porfolio
# new_position = robotOne_porfolio.add_positions(positions=multi_position)
# pprint.pprint(new_position)


# pprint.pprint(robotOne.portolio.positions)
# print("================")
# print(robotOne.regular_market_open)

end_date = datetime.today() - timedelta(days=1)
end_date = end_date.replace(tzinfo=pytz.UTC)
start_date = end_date - timedelta(days=5)
start_date = start_date.replace(tzinfo=pytz.UTC)

historical_prices = robotOne.get_historical_price(
    start=str(start_date.isoformat()),
    end=str(end_date.isoformat()),
    symbols=['TSLA']
)

# convert de data into a stockFram

stock_frame = robotOne.create_stock_frame(data=historical_prices['aggregated'])

# Print the head of the stockframe
pprint.pprint(stock_frame.frame)


symbol = "TSLA"
qty = 1

robotOne.create_trade_to_exectue("1","market",symbol=symbol,qty=qty,side='buy')


indicator_client = Indicator(stock_frame)

indicator_client.rsi(period=14)

indicator_client.sma(period=200)

indicator_client.ema(period=50)

indicator_client.set_indicator_signals(
    indicator='rsi',
    buy=50.0,
    sell=20.0,
    condition_buy=operator.ge,
    condition_sell=operator.le
)


while True:
    latest_bar = robotOne.get_latest_bar(['TSLA'])

    stock_frame.add_rows(latest_bar)

    indicator_client.refresh()

    signals = indicator_client.check_signals()

    buys: pd.Series = signals['buys']

    if not buys.empty:
        robotOne.execute_trade(robotOne.trades_to_execute["1"])
        break

    robotOne.wait_till_next_bar()


