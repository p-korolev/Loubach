import pandas as pd

from datetime import datetime
from typing import Union, Optional, List
from numbers import Real

from loubach.instrument.instrument import Instrument
from loubach.instrument.equity import Equity
from loubach.types.qtime import QuoteTiming
from loubach.instrument.other import *

from loubach.error import *

class Holding:
    '''
    Capture a holding of a particular priceable instrument.
    '''
    def __init__(self, instrument: Instrument, quantity: Real, purchase_date: Optional[Union[datetime, str]] = 'current'):
        '''
        Initialize a holding of a priceable instrument.

        :param instrument: Instrument object for the priceable to hold
        :param quantity: number of shares of instrument to hold
        :param purchase_date: Optional date of instrument purchase

        **Examples**

        >>> from loubach.instrument.equity import Equity
        >>> CVX = Equity(tick='CVX')
        >>> hold_cvx = Holding(instrument = CVX, quantity = 100)
        >>> print(hold_cvx)
        {'tick': 'CVX', 'priceAtPurchase': 156.13, 'quantity': 100} Holding Date: 2025-09-19 12:44:32.751684
        '''
        self.instrument = instrument
        self.quantity = quantity
        self.purchase_date = purchase_date
        self.currency = instrument.currency()
        self.tick = instrument.tick
        if purchase_date == "current":
            self.price = instrument.current_price()
        else:
            self.price = instrument.get_price_at(time = purchase_date)
    
    def value_at_purchase(self) -> Real:
        return self.quantity*self.price
    
    def current_value(self) -> Real:
        return self.quantity*(self.instrument.current_price())

    def get_instrument_ticker(self):
        return self.tick
    
    def __repr__(self) -> dict:
        return dict(tick=self.tick, priceAtPurchase = self.price, quantity = self.quantity)
    
    def __str__(self) -> str:
        return f"{self.__repr__()} Holding Date: {datetime.now()}"
    
    def get_type(self) -> Priceable:
        return self.instrument.priceable_type

    def currency(self) -> str:
        return self.currency

    def value_history(self, interval: Optional[Union[Interval, str]] = Interval.DAY) -> pd.Series:
        return self.instrument.price(qtime_pref=QuoteTiming.CLOSE, start=self.purchase_date, end=None, interval = interval)*self.quantity
    