import pandas as pd
import numpy as np

from numbers import Real 
from typing import Optional

def bullish(series: pd.Series, n_observable: int, differential: Real, increasing_pct: Optional[Real] = 0.7) -> pd.Series:
    '''
    Returns filtered version of given series that deifnes bullish periods.

    :param series: series of reals
    :param n_observable: number of series values to consider in period
    :param differential: Total % change as float to observe during period
    :param increasing_pct: % of series[i+1]-series[i] > 0
    '''
    bullish_indices = []

    for i in range(len(series) - n_observable + 1):
        window = series.iloc[i:i + n_observable]
        start = window.iloc[0]
        end = window.iloc[-1]

        # Condition 1: Total growth >= d%
        total_growth = (end - start) / start
        if total_growth < differential:
            continue

        # Condition 2: At least 70% of values increase stepwise
        stepwise_growth = sum(window.diff().dropna() > 0)
        if stepwise_growth / (n_observable - 1) < increasing_pct:
            continue

        bullish_indices.extend(window.index)

    # Return filtered series
    return series.loc[bullish_indices]

def price_to_volume(df: pd.DataFrame) -> pd.Series:
    pass