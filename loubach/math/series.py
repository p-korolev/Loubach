'''
Module for series processing. Includes basic series arithmetic, fill functionality, and normalization.
'''

import pandas as pd
import numpy as np

from typing import Union, Optional, List
from numbers import Real

from loubach.error import *

def get_series_values(series: pd.Series) -> List:
    '''
    Returns series values.
    '''
    return series.to_numpy()

def get_series_index(series: pd.Series) -> List:
    '''
    Returns series index.
    '''
    return series.index.to_numpy()

def fill(series: pd.Series, filling_type: str = 'ffill') -> pd.Series:
    '''
    Return a series with all values filled using the following filling rules:
        1. If filling_type is ffill, fill NaN value using previous cell value. If first item is NaN, fill it using series mean.
        2. If filling_type is bfill, fill NaN value using next cell value. If last item is NaN, fill it using series mean.
    
    **Usage**
    
    Cleaning large series without harming series mean or variance.
    '''
    series_copy = series.copy()
    mean_series = series.mean(skipna=True)
    # back-filling option selected
    if filling_type=='bfill':
        if pd.isna(series_copy.iloc[-1]):
            series_copy.ilioc[-1] = mean_series
            return series_copy.bfill()   
    # front fill, use series mean if first value NaN
    if pd.isna(series_copy.iloc[0]):
        series_copy.iloc[0] = mean_series
    return series_copy.ffill()

def normalize_series(series: pd.Series, normalization_method: Optional[str] = 'm') -> pd.Series:
    '''
    Return normalized series where values range from [0,1] inclusive using minmax method. If 'z' is specified as normalization_method, use z-score method.

    :param series: Pandas series
    :param normalization_method: Optional parameter. Indicate 'z' to use z-score normalization as the normalization method. 

    **Usage**

    Normalizing a series before using for ML models.

    **Examples**

    >>> test_series = pd.Series([98.0, 100.33, 101, 105.4, 110.12, 109.2], index=pd.date_range("2024-01-01", periods=6, freq="D"))
    >>> print(test_series)
    2024-01-01     98.00
    2024-01-02    100.33
    2024-01-03    101.00
    2024-01-04    105.40
    2024-01-05    110.12
    2024-01-06    109.20

    >>> print(normalize_series(test_series))
    2024-01-01    0.000000
    2024-01-02    0.192244
    2024-01-03    0.247525
    2024-01-04    0.610561
    2024-01-05    1.000000
    2024-01-06    0.924092

    >>> print(normalize_series(test_series, normalization_method='z'))
    2024-01-01   -1.202038
    2024-01-02   -0.735894
    2024-01-03   -0.601852
    2024-01-04    0.278419
    2024-01-05    1.222711
    2024-01-06    1.038654
    '''
    if series.empty: 
        return None 
    if normalization_method=='z':
        try:
            return (series - series.mean())/series.std()
        except: 
            raise ValueError("Try filling series")
    if normalization_method in ['minmax', 'mm', 'm']:
        try:
            return (series-series.min())/(series.max()-series.min())
        except: 
            raise OperationOnSeriesError
    else:
        raise SeriesNormalizationMethodError

def scale(series: pd.Series, initial: Real = 100) -> pd.Series:
    return (series/series.iloc[0])*initial
    
def add(first: pd.Series, second: pd.Series) -> pd.Series:
    return first + second

def subtract(first: pd.Series, second: pd.Series) -> pd.Series:
    return first - second

def log(series: pd.Series) -> pd.Series:
    return np.log(series)

