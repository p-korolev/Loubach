import yfinance as yf
import pandas as pd

from pathlib import Path
from typing import Union 

from loubach.types.priceable import Priceable
from loubach.types.time import Period, Interval

class Load:
    def __init__(self,
                 type: Union[Priceable, str],
                 tick: str,
                 period: Union[Period, str] = Period.MONTH,
                 interval: Union[Interval, str] = Interval.DAY):
        '''
        Loads data using yahoo finance api based on given period/interval.

        :param type: Priceable type (i.e.: Equity)
        :param tick: Ticker symbol as string for priceable asset
        :param period: Period for data lookback
        :param interval: Interval to split quotes by during lookback period

        **Examples**

        >>> load = Load(type=Priceable.EQUITY, tick='aapl', period=Period.MONTH, interval=Interval.DAY)
        '''
        # type param check
        if isinstance(type, str):
            try:
                valid_type = Priceable(type)
            except ValueError:
                raise ValueError("This type is not priceable.")
        elif not isinstance(type, Priceable):
            raise TypeError(f"type must be a Priceable or str, not {type(type).__name__}")
        
        # period, interval params check
        if isinstance(period, str):
            try:
                valid_period = Period(period)
            except ValueError:
                raise ValueError("Period is not a valid period.")
        elif not isinstance(period, Period):
            raise TypeError(f"period must be of type Period or str, not {type(period).__name__}")
        if isinstance(interval, str):
            try:
                valid_interval = Interval(interval)
            except ValueError:
                raise ValueError("Interval is not a valid interval.")
        elif not isinstance(period, Period):
            raise TypeError(f"interval must be of type Interval or str, not {type(interval).__name__}")
        
        # try load
        try:
            self.core = yf.Ticker(ticker=tick).history(period=str(valid_period), interval=str(valid_interval))
            self.priceable_type = type
            self.lookback = period
            self.q_interval = interval
        except:
            raise Exception("Cannot load data.")

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