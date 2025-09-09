# formalized time ranges based on YFinance passable string times

from enum import Enum 

class Interval(str, Enum):
    MINUTE = '1m'
    TWO_MINUTE = '2m'
    FIVE_MINUTE = '5m'
    HOUR = '1h'
    DAY = '1d'
    FIVE_DAY = '5d'
    WEEK = '7d'
    MONTH = '1mo'
    THREE_MONTH = '3mo'

    def __str__(self):
        return self.value

class Period(str, Enum):
    DAY = '1d'
    FIVE_DAY = '5d'
    MONTH = '1mo'
    THREE_MONTH = '3mo'
    SIX_MONTH = '6mo'
    YEAR = '1y'
    TWO_YEAR = '2y'
    FIVE_YEAR = '5y'
    TEN_YEAR = '10y'
    YTD = 'ytd'
    MAX = 'max'

    def __str__(self):
        return self.value

