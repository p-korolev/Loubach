# Formalize yfinance-load friendly priceable types

from enum import Enum

class Priceable(str, Enum):
    EQUITY      = "equity"
    ETF         = "etf"
    INDEX       = "index"
    CURRENCY    = "currency"
    CRYPTO      = "crypto"
    MUTUAL_FUND = "mutual_fund"
    FUTURE      = "future"
    OPTION      = "option"

    def __str__(self):
        return self.value

    @classmethod
    def all(cls) -> list[str]:
        return [
            cls.EQUITY,
            cls.ETF,
            cls.INDEX,
            cls.CURRENCY,
            cls.CRYPTO,
            cls.MUTUAL_FUND,
            cls.FUTURE,
            cls.OPTION,
        ]

