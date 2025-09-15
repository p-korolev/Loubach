# formalized quote timing
# OHLC: Open, High, Low, Close

from enum import Enum

class QuoteTiming(str, Enum):
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"

    def __str__(self):
        return self.value

    @classmethod
    def all(cls) -> list[str]:
        return [
            cls.OPEN,
            cls.HIGH,
            cls.LOW,
            cls.CLOSE
        ]

