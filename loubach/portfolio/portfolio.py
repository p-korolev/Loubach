import pandas as pd
import numpy as np

from typing import Optional, Union, List, Dict
from numbers import Real

from loubach.instrument.instrument import Instrument
from loubach.instrument.equity import Equity
from loubach.portfolio.holding import Holding
from loubach.instrument.other import *
from loubach.types.sector import SectorName
from loubach.types.time import Interval
from loubach.math import series, technicals, stats
from loubach.error import *


class Portfolio:
    '''
    A mutable collection of Holdings. Supports value tracking, return/risk analysis, and sector allocation.
    '''
    def __init__(self, *holding: Optional[Holding], name: Optional[str] = None):
        '''
        Initialize a portfolio from zero or more Holdings.

        :param holding: Holding objects to seed the portfolio with
        :param name: Optional display name for the portfolio

        **Examples**

        >>> from loubach.instrument.equity import Equity
        >>> from loubach.portfolio.holding import Holding
        >>> h1 = Holding(instrument=Equity(tick='AAPL'), quantity=10)
        >>> h2 = Holding(instrument=Equity(tick='CVX'), quantity=14)
        >>> p = Portfolio(h1, h2, name='Core Book')
        '''
        self.name = name
        self.holdings: List[Holding] = [h for h in holding]

    @property
    def holdings_count(self) -> int:
        return len(self.holdings)

    def isempty(self) -> bool:
        return self.holdings_count == 0

    def add_holding(self, holding: Holding) -> None:
        '''
        Adds a Holding to the portfolio. If a Holding on the same ticker already exists, raise DuplicateHoldingError.

        :param holding: Holding object to add

        **Examples**

        >>> p = Portfolio()
        >>> p.add_holding(Holding(instrument=Equity(tick='MSFT'), quantity=5))
        '''
        if any(h.get_instrument_ticker() == holding.get_instrument_ticker() for h in self.holdings):
            raise DuplicateHoldingError(tick=holding.get_instrument_ticker())
        self.holdings.append(holding)

    def remove_holding(self, tick: str) -> Holding:
        '''
        Removes and returns the Holding matching the given ticker. Raises HoldingNotFoundError if no match exists.

        :param tick: Ticker symbol of the holding to remove

        **Examples**

        >>> p.remove_holding('MSFT')
        '''
        for i, h in enumerate(self.holdings):
            if h.get_instrument_ticker() == tick:
                return self.holdings.pop(i)
        raise HoldingNotFoundError(tick=tick)

    def get_holding(self, tick: str) -> Holding:
        '''
        Returns the Holding matching the given ticker without removing it. Raises HoldingNotFoundError if no match exists.

        :param tick: Ticker symbol of the holding to fetch
        '''
        for h in self.holdings:
            if h.get_instrument_ticker() == tick:
                return h
        raise HoldingNotFoundError(tick=tick)

    def current_value(self) -> Real:
        '''
        Returns the current total value of the portfolio, using the most recent quote available for each holding.

        **Examples**

        >>> p.current_value()
        4706.25
        '''
        if self.isempty():
            raise EmptyPortfolioError
        return sum(h.current_value() for h in self.holdings)

    def weights(self) -> Dict[str, float]:
        '''
        Returns each holding's current share of total portfolio value, keyed by ticker.

        **Examples**

        >>> p.weights()
        {'AAPL': 0.62, 'CVX': 0.38}
        '''
        if self.isempty():
            raise EmptyPortfolioError
        total = self.current_value()
        return {h.get_instrument_ticker(): h.current_value() / total for h in self.holdings}

    def sector_allocation(self) -> Dict[str, float]:
        '''
        Returns the portfolio's current value broken down by sector, as a fraction of total value per sector.
        Sector is pulled from each instrument's underlying Yahoo Finance data; instruments without a resolvable
        sector are grouped under "Unknown".

        **Examples**

        >>> p.sector_allocation()
        {'Technology': 0.62, 'Energy': 0.38}
        '''
        if self.isempty():
            raise EmptyPortfolioError
        total = self.current_value()
        allocation: Dict[str, float] = {}
        for h in self.holdings:
            sector = h.instrument.sector()
            allocation[sector] = allocation.get(sector, 0.0) + (h.current_value() / total)
        return allocation

    def portfolio_value_history(self, interval: Optional[Union[Interval, str]] = Interval.DAY, union_index: bool = True) -> pd.Series:
        '''
        Sums value series across holdings into a single portfolio value series.

        :param interval: Interval to slice portfolio value by during complete lookback
        :param union_index: True/False for outer/inner joins for each Holding's value_history()

        **Examples**

        >>> p.portfolio_value_history()
        '''
        if self.isempty():
            raise EmptyPortfolioError
        series_list = [h.value_history(interval=interval) for h in self.holdings]

        how = "outer" if union_index else "inner"
        mat = pd.concat(series_list, axis=1, join=how)
        mat = mat.ffill().fillna(0.0)

        total = mat.sum(axis=1)
        total.name = "portfolio_value"
        return total

    def returns(self, interval: Optional[Union[Interval, str]] = Interval.DAY) -> pd.Series:
        '''
        Returns the period-over-period percent change of portfolio value.

        :param interval: Interval used to build the underlying value history

        **Examples**

        >>> p.returns()
        '''
        return series.change(self.portfolio_value_history(interval=interval)).dropna()

    def total_return(self, interval: Optional[Union[Interval, str]] = Interval.DAY) -> float:
        '''
        Returns the cumulative percent change in portfolio value from the start to the end of its history.

        :param interval: Interval used to build the underlying value history
        '''
        history = self.portfolio_value_history(interval=interval)
        if history.empty or history.iloc[0] == 0:
            raise OperationOnSeriesError
        return (history.iloc[-1] / history.iloc[0]) - 1

    def annualized_return(self, interval: Optional[Union[Interval, str]] = Interval.DAY, trading_periods: int = 252) -> float:
        '''
        Returns the annualized return of the portfolio, assuming daily compounding across trading_periods per year.

        :param interval: Interval used to build the underlying value history
        :param trading_periods: Number of periods per year to annualize against (default 252 trading days)
        '''
        history = self.portfolio_value_history(interval=interval)
        n = len(history)
        if n < 2:
            raise OperationOnSeriesError
        total = self.total_return(interval=interval)
        return (1 + total) ** (trading_periods / n) - 1

    def volatility(self, interval: Optional[Union[Interval, str]] = Interval.DAY, trading_periods: int = 252) -> float:
        '''
        Returns annualized volatility of portfolio returns (standard deviation of returns, scaled by sqrt(trading_periods)).

        :param interval: Interval used to build the underlying value history
        :param trading_periods: Number of periods per year used for annualizing (default 252 trading days)
        '''
        r = self.returns(interval=interval)
        if r.empty:
            raise OperationOnSeriesError
        return stats.standard_deviation(r) * np.sqrt(trading_periods)

    def sharpe_ratio(self, risk_free_rate: float = 0.0, interval: Optional[Union[Interval, str]] = Interval.DAY, trading_periods: int = 252) -> float:
        '''
        Returns the annualized Sharpe ratio of the portfolio.

        :param risk_free_rate: Annualized risk-free rate to subtract from the portfolio's return (default 0.0)
        :param interval: Interval used to build the underlying value history
        :param trading_periods: Number of periods per year used for annualizing (default 252 trading days)

        **Examples**

        >>> p.sharpe_ratio(risk_free_rate=0.04)
        1.12
        '''
        vol = self.volatility(interval=interval, trading_periods=trading_periods)
        if vol == 0:
            raise OperationOnSeriesError
        ann_return = self.annualized_return(interval=interval, trading_periods=trading_periods)
        return (ann_return - risk_free_rate) / vol

    def summary(self) -> dict:
        '''
        Returns a snapshot dict of the portfolio: name, holding count, current value, and weights.
        Useful for quick inspection without pulling full history.

        **Examples**

        >>> p.summary()
        {'name': 'Core Book', 'holdings': 2, 'value': 4706.25, 'weights': {'AAPL': 0.62, 'CVX': 0.38}}
        '''
        if self.isempty():
            return {"name": self.name, "holdings": 0, "value": 0.0, "weights": {}}
        return {
            "name": self.name,
            "holdings": self.holdings_count,
            "value": self.current_value(),
            "weights": self.weights(),
        }

    def __repr__(self) -> str:
        return f"Portfolio(name={self.name!r}, holdings={self.holdings_count})"

    def __str__(self) -> str:
        if self.isempty():
            return f"{self.name or 'Portfolio'}: empty"
        tickers = ", ".join(h.get_instrument_ticker() for h in self.holdings)
        return f"{self.name or 'Portfolio'}: {self.holdings_count} holdings ({tickers}), value={self.current_value():.2f}"
