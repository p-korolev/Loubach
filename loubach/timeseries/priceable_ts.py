# under development

import mplfinance as mpl
import pandas as pd

from typing import Union, Optional, List
from datetime import datetime
from numbers import Real 

from loubach.error import *
from loubach.instrument.instrument import Instrument
from loubach.types.time import Period, Interval

from loubach.math import technicals

class PriceTimeSeries:
    def __init__(self, prices: pd.DataFrame):
        self.core_data = prices
        self.included = []
    
    def display(self, type: Optional[str] = 'line', style: Optional[str] = 'yahoo'):
        if self.include==[]:
            mpl.plot(self.core_data, type=type, style=style)
        else:
            mpl.plot(self.core_data, addplot=self.included, type=type, style=style)
    
    def include(self, *series: pd.Series):
        for s in series:
            self.included.append(mpl.make_addplot(s))

class SinglePricePlot(PriceTimeSeries):
    def __init__(self, 
                 priceable: Instrument,
                 start: Optional[Union[datetime, str]] = None,
                 end: Optional[Union[datetime, str]] = None,
                 period: Optional[Union[Period, str]] = None,
                 interval: Optional[Union[Interval, str]] = None,
                 techs: Optional[List[str]] = None
                 ):
        '''
        Plot price series of a given priceable instrument with all available technicals from loubach.math.technicals.

        :param priceable: Priceable instrument
        :param start: Optional start date for data lookback
        :param end: Optional end date for data lookback
        :param period: Optional period for data lookback
        :param interval: Optional interval to use for interval between quotes during lookback
        :param techs: technical as string from list of available technicals (see loubach.math.technicals). Example: ['sma', 'rsi']
        '''
        core_frame = priceable.history(start=start, end=end, period=period, interval=interval)
        super().__init__(prices=core_frame)
        if techs!=None:
            for t in techs:
                if t=='sma':
                    self.include(technicals.simple_moving_average(core_frame['Close']))
                if t=='rsi':
                    self.include(technicals.rsi(data=core_frame['Close']))

# testing
# spp_aapl = SinglePricePlot(priceable=Instrument(tick='AAPL'), period='1mo', interval='1h', techs=['sma', 'rsi'])
# spp_aapl.display()