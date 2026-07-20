import matplotlib.pyplot as plt
import mplfinance as mpl
import pandas as pd

from typing import Union, Optional, List, Tuple
from datetime import datetime

from loubach.error import *
from loubach.instrument.instrument import Instrument
from loubach.portfolio.portfolio import Portfolio
from loubach.types.time import Period, Interval
from loubach.math import technicals

_SUPPORTED_TECHS = {"sma", "ema", "rsi"}


class TimeSeriesPlot:
    '''
    Base plotting engine for a single time series (price series or portfolio value series) with
    optional overlays (moving averages, RSI, other series, etc).
    '''
    def __init__(self, core: pd.Series, label: Optional[str] = None):
        '''
        :param core: Series to use as the primary plotted line
        :param label: Legend label for the core series (defaults to core.name)
        '''
        self.core_data = core
        self.label = label or core.name or "series"
        self.included: List[Tuple[pd.Series, str]] = []

    def include(self, data: pd.Series, label: Optional[str] = None) -> None:
        '''
        Adds an overlay series to be plotted alongside the core series on the same axis.

        :param data: Series to overlay (e.g. an SMA, EMA, or another instrument's price series)
        :param label: Legend label for the overlay (defaults to data.name)

        **Examples**

        >>> plot.include(sma_series, label='SMA(20)')
        '''
        self.included.append((data, label or data.name or "overlay"))

    def clear_overlays(self) -> None:
        '''Removes all included overlays, leaving only the core series.'''
        self.included = []

    def display(self, title: Optional[str] = None, figsize: Tuple[int, int] = (12, 6)):
        '''
        Plots the core series with any included overlays on a shared axis.

        :param title: Optional plot title (defaults to the core series label)
        :param figsize: Figure size passed to matplotlib

        **Examples**

        >>> plot.display(title='AAPL Close with SMA/RSI')
        '''
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(self.core_data.index, self.core_data.values, label=self.label, linewidth=1.6)
        for overlay, overlay_label in self.included:
            ax.plot(overlay.index, overlay.values, label=overlay_label, linewidth=1.0, alpha=0.85)
        ax.set_title(title or self.label)
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        plt.show()
        return fig, ax


class SinglePricePlot(TimeSeriesPlot):
    '''
    Plots a single priceable instrument's price series, with optional technical overlays.
    '''
    def __init__(self,
                 priceable: Instrument,
                 start: Optional[Union[datetime, str]] = None,
                 end: Optional[Union[datetime, str]] = None,
                 period: Optional[Union[Period, str]] = None,
                 interval: Optional[Union[Interval, str]] = Interval.DAY,
                 qtime_pref: str = "Close",
                 techs: Optional[List[str]] = None):
        '''
        :param priceable: Priceable instrument to plot
        :param start: Optional start date for data lookback
        :param end: Optional end date for data lookback
        :param period: Optional period for data lookback (alternative to start/end)
        :param interval: Interval between quotes during lookback (Interval.DAY by default)
        :param qtime_pref: Which OHLC column to plot as the core series ("Close" by default)
        :param techs: List of technical overlays to include, drawn from {'sma', 'ema', 'rsi'}

        **Examples**

        >>> from loubach.instrument.equity import Equity
        >>> spp = SinglePricePlot(priceable=Equity(tick='AAPL'), period='1mo', techs=['sma', 'rsi'])
        >>> spp.display()
        '''
        self.ohlc = priceable.history(start=start, end=end, period=period, interval=interval)
        price_series = self.ohlc[qtime_pref].copy()
        price_series.name = getattr(priceable, "tick", qtime_pref)
        super().__init__(core=price_series, label=price_series.name)

        for t in (techs or []):
            if t not in _SUPPORTED_TECHS:
                raise UnsupportedTechnicalError(tech=t, supported=_SUPPORTED_TECHS)
            if t == "sma":
                self.include(technicals.simple_moving_average(price_series), label="SMA")
            elif t == "ema":
                self.include(technicals.ema(price_series), label="EMA")
            elif t == "rsi":
                self.include(technicals.rsi(price_series), label="RSI")

    def candles(self, style: str = "yahoo", volume: bool = True) -> None:
        '''
        Renders a full OHLC candlestick chart via mplfinance. Independent of display() and any
        included overlays, since mplfinance manages its own addplot pipeline.

        :param style: mplfinance style name
        :param volume: Whether to include a volume subplot

        **Examples**

        >>> spp.candles(style='charles')
        '''
        mpl.plot(self.ohlc, type="candle", style=style, volume=volume, title=self.label)


class PortfolioPlot(TimeSeriesPlot):
    '''
    Plots a Portfolio's aggregate value over time, with optional per-holding overlays, technical
    overlays, and drawdown visualization.
    '''
    def __init__(self,
                 portfolio: Portfolio,
                 interval: Optional[Union[Interval, str]] = Interval.DAY,
                 techs: Optional[List[str]] = None,
                 show_holdings: bool = False):
        '''
        :param portfolio: Portfolio to plot
        :param interval: Interval used to build the underlying value history
        :param techs: List of technical overlays to include, drawn from {'sma', 'ema'}
        :param show_holdings: If True, overlays each individual holding's value history alongside the total

        **Examples**

        >>> from loubach.portfolio.portfolio import Portfolio
        >>> pp = PortfolioPlot(portfolio=my_portfolio, techs=['sma'], show_holdings=True)
        >>> pp.display()
        >>> pp.display_with_drawdown()
        '''
        value_series = portfolio.portfolio_value_history(interval=interval)
        value_series.name = portfolio.name or "Portfolio Value"
        super().__init__(core=value_series, label=value_series.name)
        self.portfolio = portfolio

        for t in (techs or []):
            if t not in {"sma", "ema"}:
                raise UnsupportedTechnicalError(tech=t, supported={"sma", "ema"})
            if t == "sma":
                self.include(technicals.simple_moving_average(value_series), label="SMA")
            elif t == "ema":
                self.include(technicals.ema(value_series), label="EMA")

        if show_holdings:
            for h in portfolio.holdings:
                hist = h.value_history(interval=interval)
                hist.name = h.get_instrument_ticker()
                self.include(hist, label=hist.name)

    def drawdown(self) -> pd.Series:
        '''
        Returns the portfolio's drawdown series: percent decline from the running peak value at each point.

        **Examples**

        >>> pp.drawdown().min()
        -0.14
        '''
        running_max = self.core_data.cummax()
        return (self.core_data - running_max) / running_max

    def display_with_drawdown(self, figsize: Tuple[int, int] = (12, 8)):
        '''
        Plots portfolio value (with any included overlays) on top and drawdown on a shared-x
        subplot below, mirroring the layout used by most portfolio tearsheets.

        :param figsize: Figure size passed to matplotlib

        **Examples**

        >>> pp.display_with_drawdown()
        '''
        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=figsize, sharex=True, gridspec_kw={"height_ratios": [3, 1]}
        )
        ax1.plot(self.core_data.index, self.core_data.values, label=self.label, linewidth=1.6)
        for overlay, overlay_label in self.included:
            ax1.plot(overlay.index, overlay.values, label=overlay_label, linewidth=1.0, alpha=0.85)
        ax1.set_title(self.label)
        ax1.legend()
        ax1.grid(alpha=0.3)

        dd = self.drawdown()
        ax2.fill_between(dd.index, dd.values, 0, color="red", alpha=0.3)
        ax2.set_ylabel("Drawdown")
        ax2.grid(alpha=0.3)

        fig.tight_layout()
        plt.show()
        return fig, (ax1, ax2)
