import pandas as pd
import numpy as np
import scipy.stats as sp
import math


from typing import Union, List
from numbers import Real

def average(sample: Union[List[Real], np.ndarray, pd.Series]) -> np.float64:
    '''
    Returns sample mean of a non empty data set.

    :param sample: Non empty array or series of reals
    '''
    return np.mean(sample)

def variance(sample: Union[List[Real], np.ndarray, pd.Series]) -> np.float64:
    '''
    Returns sample variance of a non empty data set.

    :param sample: Non empty array or series of reals
    '''
    return np.var(sample)

def standard_deviation(sample: Union[List[Real], np.ndarray, pd.Series]) -> np.float64:
    '''
    Returns sample standard deviation of a non empty data set.

    :param sample: Non empty array or series of reals
    '''
    # return np.float64(np.std(sample))
    return np.float64(math.sqrt(variance(sample)))

def sup(sample: Union[List[Real], np.ndarray, pd.Series]) -> np.float64:
    '''
    Returns sample max of a non empty data set.

    :param sample: Non empty array or series of reals
    '''
    return np.float64(max(sample))

def inf(sample: Union[List[Real], np.ndarray, pd.Series]) -> np.float64:
    '''
    Returns sample min of a non empty data set.

    :param sample: Non empty array or series of reals
    '''
    return np.float64(min(sample))

def sample_range(sample: Union[List[Real], np.ndarray, pd.Series]) -> np.float64:
    '''
    Returns sample range of a non empty data set.

    :param sample: Non empty array or series of reals
    '''
    return np.float64(sup(sample) - inf(sample))

def frequent(sample: Union[List, np.ndarray, pd.Series]) -> np.float64:
    '''
    Returns sample mode (most frequent value) of a non empty data set.

    :param sample: Non empty array or series of reals
    '''
    return sp.mode(sample).mode
