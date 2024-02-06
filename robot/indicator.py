import numpy as np
import pandas as pd
import operator

from typing import List
from typing import Dict
from typing import Union
from typing import Optional
from typing import Tuple
from typing import Any

from stock_frame import StockFrame


class Indicator():

    def __init__(self, price_data_frame: StockFrame) -> None:

        self._stock_frame: StockFrame = price_data_frame
        self._price_group = price_data_frame.symbol_groups
        self._current_indicators = {}
        self._indicator_signals = {}
        self._frame = self._stock_frame.frame

    def set_indicator_signals(self, indicator: str, buy: float, sell: float, condition_buy: Any,
                              condition_sell: Any) -> None:

        # if there is no signal for that indicator set a template
        if indicator not in self._indicator_signals:
            self._indicator_signals[indicator] = {}

        # modify the signal
        self._indicator_signals[indicator]['buy'] = buy
        self._indicator_signals[indicator]['sell'] = sell
        self._indicator_signals[indicator]['buy_operator'] = condition_buy
        self._indicator_signals[indicator]['sell_operator'] = condition_sell

    def get_indicator_signal(self, indicator: Optional[str]) -> Dict:

        if indicator and indicator in self._indicator_signals:
            return self._indicator_signals[indicator]
        else:
            return self._indicator_signals

    @property
    def price_data_frame(self) -> pd.DataFrame:

        return self._frame

    @price_data_frame.setter
    def price_data_frame(self, price_data_frame: pd.DataFrame) -> None:

        self._frame = price_data_frame

    def change_in_price(self) -> pd.DataFrame:

        locals_data = locals()
        del locals_data['self']

        column_name = 'change_in_price'
        self._current_indicators[column_name] = {}
        self._current_indicators[column_name]['args'] = locals_data
        self._current_indicators[column_name]['func'] = self.change_in_price()

        self._frame[column_name] = self._price_group['close'].transform(
            lambda x: x.diff()
        )

    def rsi(self, period: int, method: str = 'wilders') -> pd.DataFrame:

        locals_data = locals()
        del locals_data['self']

        column_name = 'rsi'
        self._current_indicators[column_name] = {}
        self._current_indicators[column_name]['args'] = locals_data
        self._current_indicators[column_name]['func'] = self.rsi()

        if 'change_in_price' not in self._frame.columns:
            self.change_in_price()

        # define the up days
        self._frame['up_day'] = self._price_group['change_in_price'].transform(
            lambda x: np.where(x >= 0, x, 0)
        )

        # define the down days
        self._frame['down_day'] = self._price_group['change_in_price'].transform(
            lambda x: np.where(x < 0, x.abs(), 0)
        )

        self._frame['ewma_up'] = self._price_group['up_day'].transform(
            lambda x: x.ewm(span=period).mean()
        )

        # define the down days
        self._frame['ewma_down'] = self._price_group['down_day'].transform(
            lambda x: x.ewm(span=period).mean()
        )

        relative_strengh = self._frame['ewma_up'] / self._frame['ewma_down']

        relative_strengh_index = 100.0 - (100.0 / (1.0 + relative_strengh))

        # add the rsi indicator to the frame
        self._frame['rsi'] = np.where(relative_strengh_index == 0, 100, 100.0 - (100.0 / (1.0 + relative_strengh)))

        # clean up before sending back
        self._frame.drop(
            labels=['ewma_up', 'ewma_down', 'down_day', 'up_day', 'change_in_price'],
            axis=1,
            inplace=True
        )

        return self._frame

    def sma(self, period: int) -> pd.DataFrame:

        locals_data = locals()
        del locals_data['self']

        column_name = 'sma'
        self._current_indicators[column_name] = {}
        self._current_indicators[column_name]['args'] = locals_data
        self._current_indicators[column_name]['func'] = self.sma()

        # add sma
        self._frame[column_name] = self._price_group['close'].transform(
            lambda x: x.rolling(window=period).mean()
        )

        return self._frame

    def ema(self, period: int, alpha: float = 0.0) -> pd.DataFrame:

        locals_data = locals()
        del locals_data['self']

        column_name = 'ema'
        self._current_indicators[column_name] = {}
        self._current_indicators[column_name]['args'] = locals_data
        self._current_indicators[column_name]['func'] = self.ema()

        # add ema
        self._frame[column_name] = self._price_group['close'].transform(
            lambda x: x.ewm(span=period).mean()
        )

        return self._frame

    def refresh(self):

        # first update the groups
        self._price_group = self._stock_frame.symbol_groups

        # loop throu all the stored indicators
        for indicator in self._current_indicators:
            indicator_arguments = self._current_indicators[indicator]['args']
            indicator_function = self._current_indicators[indicator]['func']

            # update the columns
            indicator_function(**indicator_arguments)

    def check_signals(self) -> Union[pd.DataFrame, None]:

        signals_df = self._stock_frame._check_signals(indicators=self._indicator_signals)

        return signals_df
