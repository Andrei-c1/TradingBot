import alpaca_trade_api as tradeapi
from robot.robot import PyRobot


from robot import config


class Account:
    def __init__(self) -> None:
        pass


robotOne = PyRobot(config.ALPACA_API_KEY, config.ALPACA_API_SECRET_KEY, config.APCA_API_BASE_URL)

acc = robotOne.get_account()

print(acc)
