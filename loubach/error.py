from typing import Optional

from loubach.types.time import Period, Interval
from loubach.types.priceable import Priceable

class TickerUnavailable(Exception):
    def __init__(self, tick: Optional[str]):
        if tick == None:
            super().__init__("Ticker does not exist or cannot be loaded at this time.")
        else:
            super().__init__(f"Ticker {tick} does not exist or cannot be loaded at this time.")

class PeriodError(Exception):
    def __init__(self):
        super().__init__(f"The chosen period is not a valid period. Choose from: \n {Period.all()}")

class IntervalError(Exception):
    def __init__(self):
        super().__init__(f"The chosen interval is not a valid interval. Choose from: \n {Interval.all()}")

class TickerNotPriceableError(Exception):
    def __init__(self):
        super().__init__("Ticker is not a priceable instrument.")

class NonPriceableType(Exception):
    def __init__(self):
        super().__init__("Instrument type is not priceable.")

class YFLoadError(Exception):
    def __init__(self):
        super().__init__("Cannot currently load instrument data.")

class DatesPeriodEntered(Exception):
    def __init__(self):
        super().__init__("Must either pass a period OR start-end dates, not both!")

class TickCompanyParameterOverload(Exception):
    def __init__(self):
        super().__init__("Must enter either a ticker or company name, not both.")

class TickSearchError(Exception):
    def __init__(self):
        super().__init__("Cannot match given company name with a ticker.")

class InstrumentTypeError(Exception):
    def __init__(self, desired: str, given: str):
        super().__init__(f"Expected to build an instrument of type {desired}, but given ticker/company is an instrument of type {given}")