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

    @classmethod
    def all(cls) -> list[str]:
        return [
            cls.MINUTE,
            cls.TWO_MINUTE,
            cls.FIVE_MINUTE,
            cls.HOUR,
            cls.DAY,
            cls.FIVE_DAY,
            cls.WEEK,
            cls.MONTH,
            cls.THREE_MONTH
        ]

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

    @classmethod
    def all(cls) -> list[str]:
        return [
            cls.DAY,
            cls.FIVE_DAY,
            cls.MONTH,
            cls.THREE_MONTH,
            cls.SIX_MONTH,
            cls.YEAR,
            cls.TWO_YEAR,
            cls.FIVE_YEAR,
            cls.TEN_YEAR,
            cls.YTD,
            cls.MAX
        ]
