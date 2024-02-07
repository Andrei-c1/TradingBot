import alpaca_trade_api as tradeapi
from robot.portfolio import Portfolio
class PyRobot():

    def __init__(self, key: str, secretKey: str, baseUrl: str) -> None:
        self.api = tradeapi.REST(key,
                                 secretKey,
                                 baseUrl)
        self.trades : dict = {}
        self.historical_prices : dict = {}
        self.stock_frame = None


    def get_account(self) :
        return self.api.get_account()

    def create_porfolio(self):
        #initialize a new portfolio obj
        self.portolio = portfolio.Portfolio("xx")

    def create_trade(self):
        pass

    def get_current_quotes(self):
        pass

    def get_historical_price(self):
        pass
