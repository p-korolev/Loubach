import pandas as pd
import numpy as np

from typing import Optional, Union, List

from loubach.instrument.instrument import Instrument
from loubach.instrument.equity import Equity
from loubach.portfolio.holding import Holding
from loubach.instrument.other import *

class Portfolio:
    def __init__(self, *holding: Optional[Holding], name: Optional[str] = None):
        self.name = name
        self.holdings = [h for h in holding]
        self.holdings_count = len(self.holdings)

    def isempty(self):
        return self.holdings_count==0
    
    def current_value(self):
        '''
        Returns the current value of the portfolio, using the most recent quote date available from Yahoo Finance.

        **Examples**

        >>> from loubach.portfolio.holding import Holding
        >>> h1 = Holding(instrument=Instrument(tick='AAPL'), quantity=10)
        >>> h2 = Holding(instrument=Instrument(tick='CVX'), quantity=14)
        >>> p = Portfolio(h1, h2)
        >>> p.current_value()
        4706.25
        '''
        total = 0
        for h in self.holdings:
            total += h.current_value()
        return total
    
    def portfolio_value_history(self, interval: Optional[Union[Interval, str]] = Interval.DAY, align_tz: Optional[str]="America/New_York", union_index: bool=True) -> pd.Series:
        """
        Sum value series across holdings to a single portfolio value series.
        
        :param interval: Interval to slice portfolio value by during complete lookback. Slices instrument quotes from each Holding by the same interval.
        :param align_tz: Time zone for time index
        :param union_index: True/False for outer/inner joins for each pd.Series of Holding.value_history()
        """
        series_list = []
        for h in self.holdings:
            vs = h.value_history(interval=interval)
            series_list.append(vs)

        if not series_list:
            return pd.Series(dtype="float64", name="portfolio_value")

        how = "outer" if union_index else "inner"
        mat = pd.concat(series_list, axis=1, join=how)

        # Filling for purchase date before: 0, else NA
        mat = mat.ffill().fillna(0.0)

        total = mat.sum(axis=1)
        total.name = "portfolio_value"
        return total
