import pprint

import alpaca_trade_api as tradeapi
#from robot.robot import PyRobot
from robot.robot import PyRobot


from robot import config


class Account:
    def __init__(self) -> None:
        pass


robotOne = PyRobot(config.ALPACA_API_KEY, config.ALPACA_API_SECRET_KEY, config.APCA_API_BASE_URL, config.ACCOUNT_NUMBER)

acc = robotOne.get_account()
print(acc)
#print("CASH = " + acc.__getattr__('cash'))

#Create new porfolio
robotOne_porfolio = robotOne.create_porfolio()

#add positions
multi_position = [
    {
        'asset_type': 'equity',
        'quantity': 2,
        'purchase_price':4.00,
        'symbol': 'TSLA',
        'purchase_date': '2020-01-31'
    },
{
        'asset_type': 'equity',
        'quantity': 2,
        'purchase_price':4.00,
        'symbol': 'SQ',
        'purchase_date': '2020-01-31'
    }
]

#add position to the porfolio
new_position = robotOne_porfolio.add_positions(positions=multi_position)
pprint.pprint(new_position)

#add single position
robotOne.portolio.add_position(
    symbol = 'MSFT',
    quantity=10,
    purchase_price=10.00,
    asset_type='equity',
    purchase_date='2020-04-01'
)

pprint.pprint(robotOne.portolio.positions)
print("================")
print(robotOne.regular_market_open)

