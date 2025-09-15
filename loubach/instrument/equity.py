import pandas as pd
import yfinance as yf

from typing import Union, Optional, List
from numbers import Real

from loubach.error import *
from loubach.instrument.instrument import Instrument
from loubach.data.load import Load
from loubach.types.priceable import Priceable
from loubach.types.time import Period, Interval

class Equity(Instrument):

    INSTRUMENT_TYPE = "equity"

    def __init__(self, tick: Optional[str] = None, company_name: Optional[str] = None) -> None:
        '''
        Initialize stock object by entering etiher the company's publically traded stock ticker symbol, or name of company.

        :param tick: Ticker symbol
        :param company_name: Name of the company (enter only if ticker is left None)

        **Examples** 
        
        >>> # Load AAPL by ticker
        >>> AAPL = Equity(tick="AAPL")
        >>> # Load AAPL by company name
        >>> AAPL = Equity(company_name="Apple")
        '''
        # parameter checks
        if company_name!=None and tick!=None:
            raise TickCompanyParameterOverload
        
        if company_name!=None:
            cticker = search_tick(company_name=company_name)
            if cticker==None:
                raise TickSearchError
            super().__init__(tick=cticker)

        if tick!=None:
            super().__init__(tick=tick)
        
        if self.priceable_type != Equity.INSTRUMENT_TYPE:
            raise InstrumentTypeError(desired=Equity.INSTRUMENT_TYPE, given=self.priceable_type.lower())
    
    def __repr__(self):
        return self.tick, self.current_price()
    
    def current_price(self) -> Real:
        return self.connection.info.get("currentPrice")

# helper query to search yahoo finance endpoints for tick given company name
import requests
def search_tick(*company: Union[List, str]) -> Union[List, str]:
    '''
    Return tick symbol(s) of inputted company name(s).

    :param company_name: Name of public company as string

    **Examples**
    
    >>> search_tick("Apple Inc.")
    "AAPL"

    >>> search_tick(["Apple", "Tesla"])
    ["AAPL", "TSLA"]
    '''
    
    ticks = []
    for c in company:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={c}"
        response = requests.get(url).json()
        for result in response.get("quotes", []):
            if result.get("quoteType")==Priceable.EQUITY.upper():
                ticks.append(result.get("symbol"))
        ticks.append("")
    if len(ticks)==1:
        return ticks[0]
    return ticks
    