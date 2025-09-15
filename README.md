# Loubach
### Open-source Python library for quantitative market analysis.
Combines popular quantitative libraries like yfinance, pandas, numpy, ta, seaborn, matplotlib to perform analysis on financial markets.

```bash

pip install loubach

```

**Example Usage**

```python

from loubach.instrument.equity import Equity
from loubach.types.time import Period, Interval

from loubach.timeseries.display import Display
from loubach.math.technicals import sma, ema, rsi
from loubach.math.trend import bullish

# Load equity instrument
AAPL = Equity(tick = "AAPL")

# Get YTD hourly closing prices and some technicals
ytd_closing = AAPL.price(period = Period.YTD, interval = Interval.HOUR)
sma = sma(data = ytd_closing)
bull = bullish(data = ytd_closing, n_observable = 7, differential = 0.68)

# Plot data
Display(primary = ytd_closing, include=[sma, bull]).show()






```
