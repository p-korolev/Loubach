import pandas as pd
import numpy as np
import math

from typing import Union, List, Optional
from numbers import Real

from loubach.error import *
from loubach.math import series

def simple_moving_average(data: pd.Series, window: Optional[int] = 7) -> pd.Series:
    '''
    Returns simple moving average based on specified window period as type pd.Series.

    Will front fill if series contains NA values.

    :param data: Series of reals
    :param window: Period cycle for moving average. Defines how many observations to aggregate (average) at each step

    **Usage**
    
    Getting a moving average for a stock prices series for plotting.

    **Examples**

    >>> from loubach.equity import Equity
    >>> from loubach.types import Period
    >>> closing = Equity(tick='AAPL').price(period=Period.MONTH)
    >>> simple_moving_average(data=closing, window=3)
    Date
    2025-05-28 00:00:00-04:00           NaN
    2025-05-29 00:00:00-04:00           NaN
    2025-05-30 00:00:00-04:00    200.406667
    2025-06-02 00:00:00-04:00    200.833333
    2025-06-03 00:00:00-04:00    201.940002
    2025-06-04 00:00:00-04:00    202.596670
    2025-06-05 00:00:00-04:00    202.240005
    ...
    2025-06-26 00:00:00-04:00    200.953334
    2025-06-27 00:00:00-04:00    201.213333
    Name: Close, dtype: float64
    '''
    return series.fill(series=data, filling_type='ffill').rolling(window).mean()

def ema(data: pd.Series, lookback: int = 12, adjust: bool = False) -> pd.Series:
    '''
    Returns exponential moving average of a series of reals.

    :param data: Series of reals
    :param lookback: Lookback period span
    :param adjust: Adjustable pass through for Pandas

    **Usage**

    Plotting exponential moving average against a stock's open prices for time series.

    **Examples**

    >>> from loubach.instrument.equity import Equity
    >>> from loubach.types import Period
    >>> closing = Equity(tick='AAPL').price(period=Period.MONTH)
    >>> ema(data=closing, lookback=12)
    Date
    2025-05-28 00:00:00-04:00    200.419998
    2025-05-29 00:00:00-04:00    200.347690
    2025-05-30 00:00:00-04:00    200.424970
    2025-06-02 00:00:00-04:00    200.621128
    2025-06-03 00:00:00-04:00    201.028647
    2025-06-04 00:00:00-04:00    201.304241
    2025-06-05 00:00:00-04:00    201.200512
    ...
    2025-06-25 00:00:00-04:00    199.974783
    2025-06-26 00:00:00-04:00    200.132509
    2025-06-27 00:00:00-04:00    200.278277
    Name: Close, dtype: float64
    '''
    return data.ewm(span=lookback, adjust=adjust).mean()

def rolling_volatility(data: pd.Series, window: Optional[int] = 21) -> pd.Series:
    '''
    Calculates annualized rolling volatility from a series of closing prices.

    :param close_prices: A pandas Series of asset closing prices indexed by date.
    :param window: The rolling window size in days used to compute standard deviation. Default is 21 (approx. one trading month).
    '''
    return data.pct_change().rolling(window=window).std()*np.sqrt(252)

def rolling_var(data: pd.Series, window: Optional[int] = 21) -> pd.Series:
    '''
    Calculates rolling variance of daily returns over a specified window.

    :param close_prices: A pandas Series of asset closing prices indexed by date.
    :param window: The number of periods used to compute rolling variance. Default is 21 (approx. one trading month).
    '''
    return data.pct_change().rolling(window=window).var()

def rsi(data: pd.Series, period: int = 14) -> pd.Series:
    '''
    Returns relative strength index over a given period as series.

    :param data: Series of reals
    :param period: Lookback window for Relative Strenght Index

    **Usage**

    Plotting an RSI against a stock's price forr time series. 

    **Examples**

    >>> from loubach.instrument.equity import Equity
    >>> from loubach.types import Period
    >>> closing = Equity(tick='AAPL').price(period=Period.MONTH)
    >>> rsi(data=closing, period=7)
    Date
    2025-05-28 00:00:00-04:00          NaN
    2025-05-29 00:00:00-04:00     0.000000
    2025-05-30 00:00:00-04:00    24.193687
    2025-06-02 00:00:00-04:00    40.148486
    2025-06-03 00:00:00-04:00    58.823756
    2025-06-04 00:00:00-04:00    53.266034
    2025-06-05 00:00:00-04:00    34.668345
    ...
    2025-06-25 00:00:00-04:00    56.876480
    2025-06-26 00:00:00-04:00    53.967379
    2025-06-27 00:00:00-04:00    54.356483
    Name: Close, dtype: float64
    '''
    gain = data.diff().clip(lower=0)
    loss = -(data.diff().clip(upper=0))

    # use Wilder's smoothed moving averages
    alpha = 1/period 
    avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
    avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()
    return 100 - (100/(1+(avg_gain/avg_loss)))

def macd_frame(data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_span: int = 9) -> pd.DataFrame:
    '''
    General moving average convergence divergence information scope. Returns dataframe containing columns for:
        "macd": fast EMA - slow EMA
        "signal": EMA(MACD)
        "hist": macd - signal

    :param data: quantitative series data.
    :param fast_period: period span for shorter EMA.
    :param slow_period: period span for longer EMA.
    :param signal_span: period span for the signal line.

    **Usage** 

    Pulling all required moving average con/div data, or returing individual columns as a series for time series plotting.

    **Examples**

    >>> from loubach.instrument.equity import Equity
    >>> from loubach.types import Period
    >>> closing = Equity(tick='AAPL').price(period=Period.MONTH)
    >>> macd_frame(data=closing)
                                macd    signal      hist
    Date
    2025-05-28 00:00:00-04:00  0.000000  0.000000  0.000000
    2025-05-29 00:00:00-04:00 -0.037493 -0.007499 -0.029994
    2025-05-30 00:00:00-04:00  0.005355 -0.004928  0.010283
    2025-06-02 00:00:00-04:00  0.106670  0.017392  0.089278
    2025-06-03 00:00:00-04:00  0.310075  0.075928  0.234147
    2025-06-04 00:00:00-04:00  0.430007  0.146744  0.283263
    2025-06-05 00:00:00-04:00  0.344369  0.186269  0.158100
    ...
    2025-06-25 00:00:00-04:00 -0.172773 -0.325501  0.152728
    2025-06-26 00:00:00-04:00 -0.078191 -0.276039  0.197848
    2025-06-27 00:00:00-04:00  0.003184 -0.220194  0.223379
    '''
    macd_line = (data.ewm(span=fast_period, adjust=False).mean()) - (data.ewm(span=slow_period, adjust=False).mean())
    signal_line = macd_line.ewm(span=signal_span, adjust=False).mean()
    hist = macd_line - signal_line

    return pd.DataFrame(
        {"macd": macd_line, 
         "signal": signal_line, 
         "hist": hist},
        index=data.index
    )

def macd(data: pd.Series, fast_period: int = 12, slow_period: int = 26) -> pd.Series:
    '''
    Returns the moving average convergence divergence as a Series or PairedSet depending on data input type.

    :param data: series or paired set price/returns data.
    :param fast_period: period for short-span EMA.
    :param slow_period: period for long-span EMA.
    
    **Usage**

    Pulling moving average con/div values to plot macd line against stock prices or returns.

    **Examples**

    >>> from loubach.instrument.equity import Equity
    >>> from loubach.types import Period
    >>> closing = Equity(tick='AAPL').price(period=Period.MONTH)
    >>> macd(data=closing) 
    Date
    2025-05-28 00:00:00-04:00  0.000000
    2025-05-29 00:00:00-04:00 -0.037493
    2025-05-30 00:00:00-04:00  0.005355
    2025-06-02 00:00:00-04:00  0.106670
    2025-06-03 00:00:00-04:00  0.310075
    2025-06-04 00:00:00-04:00  0.430007
    2025-06-05 00:00:00-04:00  0.344369
    ...
    2025-06-25 00:00:00-04:00 -0.172773
    2025-06-26 00:00:00-04:00 -0.078191
    2025-06-27 00:00:00-04:00  0.003184
    Name: macd, dtype: float64
    '''
    return (data.ewm(span=fast_period, adjust=False).mean()) - (data.ewm(span=slow_period, adjust=False).mean())

def macd_signal(data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_span: int = 9) -> pd.Series:
    '''
    Returns the moving average convergence divergence signal as a Series or PairedSet depending on data input type.

    :param data: series or paired set price/returns data.
    :param fast_period: period for short-span EMA.
    :param slow_period: period for long-span EMA.
    :param signal_span: period for signal line.
    
    **Usage**

    Pulling moving average con/div signal to plot against stock prices or returns.

    **Examples**

    >>> from loubach.instrument.equity import Equity
    >>> from loubach.types import Period
    >>> closing = Equity(tick='AAPL').price(period=Period.MONTH)
    >>> macd_signal(data=closing)
    Date
    2025-05-28 00:00:00-04:00  0.000000
    2025-05-29 00:00:00-04:00 -0.007499
    2025-05-30 00:00:00-04:00 -0.004928
    2025-06-02 00:00:00-04:00  0.017392
    2025-06-03 00:00:00-04:00  0.075928
    2025-06-04 00:00:00-04:00  0.146744
    2025-06-05 00:00:00-04:00  0.186269
    ...
    2025-06-25 00:00:00-04:00 -0.325501
    2025-06-26 00:00:00-04:00 -0.276039
    2025-06-27 00:00:00-04:00 -0.220194
    Name: signal, dtype: float64
    '''
    m = macd(data=data, fast_period=fast_period, slow_period=slow_period)
    return m.ewm(span=signal_span, adjust=False).mean()

def macd_hist(data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_span: int = 9) -> pd.Series:
    '''
    Returns macd minus signal as a Series or PairedSet depending on data input type.

    :param data: series or paired set price/returns data.
    :param fast_period: period for short-span EMA.
    :param slow_period: period for long-span EMA.
    :param signal_span: period for signal line.
    
    **Usage**

    Pulling macd, signal difference series to plot against stock prices or returns.

    **Examples**

    >>> from loubach.instrument.equity import Equity
    >>> from loubach.types import Period
    >>> closing = Equity(tick='AAPL').price(period=Period.MONTH)
    >>> macd_hist(data=closing)
    Date
    2025-05-28 00:00:00-04:00    0.000000
    2025-05-29 00:00:00-04:00   -0.029994
    2025-05-30 00:00:00-04:00    0.010283
    2025-06-02 00:00:00-04:00    0.089278
    2025-06-03 00:00:00-04:00    0.234147
    2025-06-04 00:00:00-04:00    0.283263
    2025-06-05 00:00:00-04:00    0.158100
    ...
    2025-06-25 00:00:00-04:00    0.152728
    2025-06-26 00:00:00-04:00    0.197848
    2025-06-27 00:00:00-04:00    0.223379
    Name: hist, dtype: float64
    '''
    return macd(data=data, fast_period=fast_period, slow_period=slow_period) - macd_signal(data=data, fast_period=fast_period, slow_period=slow_period, signal_span=signal_span)

