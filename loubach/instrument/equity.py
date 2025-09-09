import pandas as pd
import yfinance as yf

from typing import Union, Optional, List

from loubach.data.load import Load
from loubach.types.priceable import Priceable
from loubach.types.time import Period, Interval

class Equity():
    def __init__(self, tick: Optional[str] = None, company_name: Optional[str] = None) -> None:
        '''
        Initialize stock object by entering etiher the company's publically traded stock ticker symbol, or name of company.

        :param tick: Ticker symbol
        :param company_name: Name of the company (enter only if ticker is left None)

        **Examples** 

        >>> AAPL = Equity(tick="AAPL")
        >>> # Load AAPL through company name
        >>> AAPL = Equity(company_name="Apple")
        '''
        # parameter checks
        if (tick!=None and company_name!=None):
            raise ValueError(
                "Expected either tick parameter or company_name parameter to be provided, not both."
                )
        if (tick==None and company_name==None):
            raise ValueError(
                "Either tick or company_name must be provided."
            )
        
        # initialize connection (check loadable)
        if tick!=None:
            try:
                self.tick = tick
                self.connection = yf.Ticker(tick) # check if yf loadable
            except:
                raise ValueError("tick is invalid or does not exist.")
        if company_name!=None:
            try:
                tick = search_tick(company_name=company_name)
                self.connection = yf.Ticker(tick)
            except:
                raise ValueError("Company does not have a publically traded stock or input is invalid.")
        
        # quote data has not been loaded at init time
        self.loaded = False

    def history(self, period: Union[Period, str] = Period.MONTH, interval: Union[Interval, str] = Interval.DAY) -> pd.DataFrame:
        try:
            self.load = Load(type=Priceable.EQUITY, tick=self.tick, period=period, interval=interval)
            self.loaded = True
        except:
            raise Exception("Cannot load quote history. Check parameters.")
        return self.load.core 

    def __repr__(self):
        return self.tick, self.connection.info.get("currentPrice")

# helper query to search yahoo finance endpoints for tick given company name
import requests
def search_tick(company_name: Union[List, str]) -> Union[List, str]:
    '''
    Return tick symbol(s) of inputted company name(s).

    :param company_name: Name of public company.

    **Examples**
    
    >>> search_tick("Apple Inc.")
    "AAPL"

    >>> search_tick("Apple")
    "AAPL"

    >>> search_tick(["Apple", "Tesla"])
    ["AAPL", "TSLA"]
    '''
    
    if isinstance(company_name, List):
        result = []
        for company in company_name:
            url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company}"
            response = requests.get(url).json()
            for result in response.get("quotes", []):
                if result.get("quoteType")=="EQUITY":
                    result.append(result.get("symbol"))
            result.append("")
    if isinstance(company_name, str):
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}"
        response = requests.get(url).json()
        for result in response.get("quotes", []):
            if result.get("quoteType")=="EQUITY":
                return result.get("symbol")
        return None 
    else: 
        raise TypeError("Expected company_name to be a list or individual string")

    
