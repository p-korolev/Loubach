import yfinance as yf
import pandas as pd

from pathlib import Path
from typing import Union, Optional
from datetime import datetime

from loubach.error import *
from loubach.types.priceable import Priceable
from loubach.types.time import Period, Interval

class Load:
    def __init__(self,
                 tick: str,
                 instrument_type: Union[Priceable, str],
                 start: Optional[Union[datetime, str]] = None,
                 end: Optional[Union[datetime, str]] = None,
                 period: Optional[Union[Period, str]] = None,
                 interval: Union[Interval, str] = Interval.DAY):
        '''
        Loads data using yahoo finance api based on given start-end times or period. Quotes can be broken down by given interval.

        :param type: Priceable type (i.e.: Equity)
        :param tick: Ticker symbol as string for priceable asset
        :param start: History lookback start time as datetime or string 'YYYY-MM-DD'
        :param end: History lookback end time as datetime or string 'YYYY-MM-DD'
        :param period: Period for data lookback
        :param interval: Interval to split quotes by during lookback period

        **Examples**

        >>> from loubach.types.priceable import Priceable
        >>> from loubach.types.time import Period, Interval
        >>> load = Load(tick='aapl', instrument_type=Priceable.EQUITY, period=Period.MONTH, interval=Interval.DAY)
        >>> # alternatively, using start, end parameters:
        >>> alt_load = Load(tick='aapl', instrument_type=Priceable.EQUITY, start='2025-01-01', end='2025-09-10', interval=Interval.HOUR)
        '''
        # type param check
        if isinstance(instrument_type, str):
            try:
                valid_type = Priceable(instrument_type)
            except NonPriceableType:
                raise NonPriceableType
        elif not isinstance(type, Priceable):
            raise TypeError(f"type must be a Priceable or str, not {type(instrument_type).__name__}")
        
        # period param checks
        if period != None:
            if start!=None or end!=None:
                raise DatesAndPeriodEntered
            if isinstance(period, str):
                try:
                    valid_period = Period(period)
                except PeriodError:
                    raise PeriodError
            elif not isinstance(period, Period):
                raise TypeError(f"period must be of type Period or str, not {type(period).__name__}")
        
        # interval param check
        if isinstance(interval, str):
            try:
                valid_interval = Interval(interval)
            except IntervalError:
                raise IntervalError
        elif not isinstance(period, Period):
            raise TypeError(f"interval must be of type Interval or str, not {type(interval).__name__}")
        
        # try load
        if start!=None and end!=None:
            self.core = yf.Ticker(ticker=tick).history(start=start, end=end, interval=str(valid_interval)).drop(columns=["Dividends", "Stock Splits"])
        else:
            self.core = yf.Ticker(ticker=tick).history(period=str(valid_period), interval=str(valid_interval)).drop(columns=["Dividends", "Stock Splits"])
        self.priceable_type = instrument_type
        self.lookback = period
        self.q_interval = interval
        if self.core.empty:
            raise YFLoadError

    def download_csv(self, save_folder: Union[Path, str], file_name: str) -> None:
        '''
        Saves loaded core data frame as a csv to specified folder under specified file name.

        :param save_folder: Folder path
        :param file_name: Name to save file as
        '''
        folder = save_folder
        if ".csv" not in file_name:
            file_name += ".csv"
        if isinstance(save_folder, str):
            try:
                folder = Path(save_folder)
            except Exception:
                raise Exception("Could not convert string path into type Path.")
        if not folder.exists():
            raise Exception("Folder path does not exist.")
        final = folder/file_name
        self.core.to_csv(final)

    def get_core(self) -> pd.DataFrame:
        return self.core
    
    #def reload