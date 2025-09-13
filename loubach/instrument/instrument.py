import pandas as pd
import yfinance as yf

from typing import Union, Optional 
from datetime import datetime 

from loubach.error import *
from loubach.types.priceable import Priceable
from loubach.types.time import Period, Interval
from loubach.data.load import Load

class Instrument:
    '''
    Base instrument object. Inherited by Equity, ETF, Index, Future, and other objects for priceables.
    '''
    def __init__(self, tick: Optional[str]):
        '''
        Initialize instrument object by loading tradable ticker. 
        
        The constructor will attempt to make a connection to Yahoo Finance'sendpoints. If the ticker is not loadable through 
        Yahoo Finance, raise TickerUnavailable message. 
        
        Otherwise, check that the ticker is actually priceable, if not, raise TickerNotPriceableError.

        :param tick: Ticker symbol of a priceable instrument
        '''
        self.loaded = False
        self.connection = yf.Ticker(tick)
        if not self.connection.info or "symbol" not in self.connection.info:
            raise TickerUnavailable(tick=tick)
        try:
            self.priceable_type = Priceable(self.connection.info.get("typeDisp").lower())
        except TickerNotPriceableError:
            raise TickerNotPriceableError

        self.tick = tick
        self.priceable = True # extra check for future usage if needed
    
    def history(self,
                start: Optional[Union[datetime, str]] = None,
                end: Optional[Union[datetime, str]] = None,
                period: Optional[Union[Period, str]] = None, 
                interval: Optional[Union[Interval, str]] = Interval.DAY
                ) -> pd.DataFrame:
        '''
        Fetches quote history using either start->end or period as lookback periods. Breaks quotes down by interval if specified.

        :param start: Start date for history lookback.
        :param end: End date for history lookback.
        :param period: Alternative to start-end dates usage. Must be a valid period (check loubach.types.time.Period.all())
        :param interval: Time in between quotes during lookback period (Interval.DAY by default)

        **Examples**

        >>> from loubach.types.time import Period, Interval
        >>> ins = Instrument(tick='aapl')
        >>> ins.history(period=Period.YEAR)
                                            Open        High         Low       Close    Volume
            Date
            2024-09-10 00:00:00-04:00  217.905858  220.453996  215.726000  219.090347  51591000
            2024-09-11 00:00:00-04:00  220.434102  222.056541  216.880633  221.628540  44587100
            2024-09-12 00:00:00-04:00  221.469284  222.514423  218.801706  221.738037  37455600
            2024-09-13 00:00:00-04:00  222.544268  223.002128  220.882006  221.469269  36766600
            2024-09-16 00:00:00-04:00  215.536884  216.213742  212.929026  215.317917  59357400
            ...
            2025-09-04 00:00:00-04:00  238.449997  239.899994  236.740005  239.779999  47549400
            2025-09-05 00:00:00-04:00  240.000000  241.320007  238.490005  239.690002  54870400
            2025-09-08 00:00:00-04:00  239.300003  240.149994  236.339996  237.880005  48999500
            2025-09-09 00:00:00-04:00  237.000000  238.779999  233.360001  234.350006  66153200
            2025-09-10 00:00:00-04:00  232.024994  232.339996  226.240097  226.824997  58031757
        '''
        if start!=None:
            return Load(tick=self.tick, instrument_type=self.priceable_type, start=start, end=end, interval=interval).get_core()
        if start==None and period!=None:
            return Load(tick=self.tick, instrument_type=self.priceable_type, period=period, interval=interval).get_core()
        else:
            raise Exception(
                "Parameters are not passed properly. Check that either start-end dates OR period is provided."
                )

