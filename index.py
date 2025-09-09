import pandas as pd
import yfinance as yf

from typing import Union, Optional, List

from loubach.data.load import Load
from loubach.types.priceable import Priceable
from loubach.types.time import Period, Interval

class Index:
    def __init__(self, tick: str):
        try:
            self.connection = yf.Ticker(tick)
            if self.connection.info.get("typeDisp") != "Index":
                raise ValueError("Given ticker is not a valid Index symbol")
            self.Index_valid = True
        except ValueError:
            raise ValueError("Cannot initialize given ticker.")

        self.loaded = False
        self.tick = tick
    
    def history(self, period: Union[Period, str] = Period.MONTH, interval: Union[Interval, str] = Interval.DAY) -> pd.DataFrame:
        try:
            self.load = Load(type=Priceable.INDEX, tick=self.tick, period=period, interval=interval)
        except:
            raise Exception("Could not load quote history.")
        self.loaded = True
        return self.load.core 