---
name: technical-analysis-talib
description: Expert guidance for technical analysis using TA-Lib with 150+ indicators for market analysis and trading signal generation
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, Technical Analysis, Indicators, Chart Patterns, Signal Generation, Python, C Library]
dependencies: [TA-Lib>=0.4.28, numpy>=1.21.0, pandas>=1.4.0]
---

# TA-Lib: Technical Analysis Library

## Quick Start

### Installation
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install ta-lib
pip install TA-Lib

# macOS
brew install ta-lib
pip install TA-Lib

# Windows (pre-built wheel)
pip install TA-Lib-binary

# From source
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

### Basic Usage
```python
import talib
import numpy as np
import pandas as pd

# Sample price data
close = np.random.random(100) * 100 + 100  # Random prices
high = close + np.random.random(100) * 2
low = close - np.random.random(100) * 2
open_price = close + (np.random.random(100) - 0.5) * 3
volume = np.random.random(100) * 1000000

# Calculate indicators
sma = talib.SMA(close, timeperiod=20)
ema = talib.EMA(close, timeperiod=20)
rsi = talib.RSI(close, timeperiod=14)
macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

# With pandas DataFrame
df = pd.DataFrame({
    'open': open_price, 'high': high, 'low': low,
    'close': close, 'volume': volume
})
df['sma20'] = talib.SMA(df['close'], timeperiod=20)
df['rsi14'] = talib.RSI(df['close'], timeperiod=14)
```

## Core Concepts

### Indicator Categories
```
TA-Lib Function Groups (150+ indicators):
├── Overlap Studies
│   ├── SMA, EMA, WMA, DEMA, TEMA
│   ├── Bollinger Bands (BBANDS)
│   ├── SAR, SAREXT (Parabolic SAR)
│   └── Hilbert Transform variants
├── Momentum Indicators
│   ├── RSI, STOCH, STOCHRSI
│   ├── MACD, MACDFIX, MACDEXT
│   ├── ADX, ADXR, CCI, MOM
│   ├── Williams %R, ROC, ROCP
│   └── Ultimate Oscillator, Aroon
├── Volume Indicators
│   ├── OBV (On Balance Volume)
│   ├── AD (Chaikin A/D Line)
│   └── ADOSC (Chaikin A/D Oscillator)
├── Volatility Indicators
│   ├── ATR (Average True Range)
│   ├── NATR (Normalized ATR)
│   └── TRANGE (True Range)
├── Pattern Recognition (61 patterns)
│   ├── Candlestick patterns
│   └── CDL* functions (e.g., CDLDOJI, CDLHAMMER)
└── Price Transform
    ├── AVGPRICE, MEDPRICE, TYPPRICE
    └── WCLPRICE
```

### Abstract API vs Function API
```python
import talib
from talib import abstract

# Function API (direct)
sma = talib.SMA(close, timeperiod=20)
macd, signal, hist = talib.MACD(close, 12, 26, 9)

# Abstract API (with dictionary input)
inputs = {
    'open': open_price,
    'high': high,
    'low': low,
    'close': close,
    'volume': volume
}

# Get function info
sma_func = abstract.SMA
print(sma_func.info)
# {'name': 'SMA', 'group': 'Overlap Studies', 'display_name': 'Simple Moving Average', ...}

# Calculate using abstract API
sma = abstract.SMA(inputs, timeperiod=20)
macd = abstract.MACD(inputs, fastperiod=12, slowperiod=26, signalperiod=9)

# Abstract API returns dict for multi-output functions
print(macd.keys())  # ['macd', 'macdsignal', 'macdhist']
```

### Pattern Recognition Output
```python
# Candlestick patterns return:
#  100 = bullish pattern
#    0 = no pattern
# -100 = bearish pattern

pattern = talib.CDLDOJI(open_price, high, low, close)
print(pattern)  # Array of 0, 100, or -100

# All pattern functions
patterns = talib.get_function_groups()['Pattern Recognition']
# ['CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', ...]
```

## Common Workflows

### Workflow 1: Multi-Indicator Signal System

**Objective**: Combine multiple indicators for robust signals

```python
import talib
import numpy as np
import pandas as pd

class MultiIndicatorSignals:
    def __init__(self, df):
        """
        df must have columns: open, high, low, close, volume
        """
        self.df = df.copy()
        self.calculate_indicators()

    def calculate_indicators(self):
        close = self.df['close'].values
        high = self.df['high'].values
        low = self.df['low'].values
        volume = self.df['volume'].values

        # Trend Indicators
        self.df['sma20'] = talib.SMA(close, 20)
        self.df['sma50'] = talib.SMA(close, 50)
        self.df['sma200'] = talib.SMA(close, 200)
        self.df['ema12'] = talib.EMA(close, 12)
        self.df['ema26'] = talib.EMA(close, 26)

        # MACD
        macd, signal, hist = talib.MACD(close, 12, 26, 9)
        self.df['macd'] = macd
        self.df['macd_signal'] = signal
        self.df['macd_hist'] = hist

        # Momentum
        self.df['rsi'] = talib.RSI(close, 14)
        slowk, slowd = talib.STOCH(high, low, close, 14, 3, 0, 3, 0)
        self.df['stoch_k'] = slowk
        self.df['stoch_d'] = slowd

        # Volatility
        self.df['atr'] = talib.ATR(high, low, close, 14)
        upper, middle, lower = talib.BBANDS(close, 20, 2, 2)
        self.df['bb_upper'] = upper
        self.df['bb_middle'] = middle
        self.df['bb_lower'] = lower

        # Volume
        self.df['obv'] = talib.OBV(close, volume)
        self.df['ad'] = talib.AD(high, low, close, volume)

    def generate_signals(self):
        """Generate composite trading signals"""
        signals = pd.DataFrame(index=self.df.index)

        # Trend signal
        signals['trend'] = np.where(
            (self.df['sma20'] > self.df['sma50']) &
            (self.df['sma50'] > self.df['sma200']),
            1, -1
        )

        # MACD signal
        signals['macd'] = np.where(self.df['macd_hist'] > 0, 1, -1)

        # RSI signal
        signals['rsi'] = np.where(
            self.df['rsi'] < 30, 1,  # Oversold - bullish
            np.where(self.df['rsi'] > 70, -1, 0)  # Overbought - bearish
        )

        # Bollinger signal
        signals['bb'] = np.where(
            self.df['close'] < self.df['bb_lower'], 1,
            np.where(self.df['close'] > self.df['bb_upper'], -1, 0)
        )

        # Composite signal (weighted)
        signals['composite'] = (
            signals['trend'] * 0.3 +
            signals['macd'] * 0.3 +
            signals['rsi'] * 0.2 +
            signals['bb'] * 0.2
        )

        # Final signal
        signals['signal'] = np.where(
            signals['composite'] > 0.5, 1,
            np.where(signals['composite'] < -0.5, -1, 0)
        )

        return signals

# Usage
df = pd.DataFrame({
    'open': open_price, 'high': high, 'low': low,
    'close': close, 'volume': volume
})
analyzer = MultiIndicatorSignals(df)
signals = analyzer.generate_signals()
```

**Checklist**:
- [ ] Use at least 3 different indicator categories
- [ ] Weight signals by reliability
- [ ] Handle NaN values from lookback periods
- [ ] Test signal correlation
- [ ] Validate with out-of-sample data

### Workflow 2: Candlestick Pattern Scanner

**Objective**: Scan for all candlestick patterns

```python
import talib
import pandas as pd
import numpy as np

class PatternScanner:
    # All 61 candlestick pattern functions
    PATTERNS = [
        'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE',
        'CDL3OUTSIDE', 'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS',
        'CDLABANDONEDBABY', 'CDLADVANCEBLOCK', 'CDLBELTHOLD',
        'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL',
        'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI',
        'CDLDOJISTAR', 'CDLDRAGONFLYDOJI', 'CDLENGULFING',
        'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLGAPSIDESIDEWHITE',
        'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN',
        'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE', 'CDLHIKKAKE',
        'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS',
        'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING',
        'CDLKICKINGBYLENGTH', 'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI',
        'CDLLONGLINE', 'CDLMARUBOZU', 'CDLMATCHINGLOW',
        'CDLMATHOLD', 'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR',
        'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN',
        'CDLRISEFALL3METHODS', 'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR',
        'CDLSHORTLINE', 'CDLSPINNINGTOP', 'CDLSTALLEDPATTERN',
        'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP',
        'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER',
        'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS'
    ]

    def __init__(self, df):
        self.df = df
        self.open = df['open'].values
        self.high = df['high'].values
        self.low = df['low'].values
        self.close = df['close'].values

    def scan_all_patterns(self):
        """Scan for all candlestick patterns"""
        results = pd.DataFrame(index=self.df.index)

        for pattern_name in self.PATTERNS:
            pattern_func = getattr(talib, pattern_name)
            results[pattern_name] = pattern_func(
                self.open, self.high, self.low, self.close
            )

        return results

    def get_active_patterns(self, index=-1):
        """Get patterns active at specific index"""
        patterns = self.scan_all_patterns()
        active = []

        for col in patterns.columns:
            value = patterns[col].iloc[index]
            if value != 0:
                signal = 'Bullish' if value > 0 else 'Bearish'
                active.append({
                    'pattern': col,
                    'signal': signal,
                    'strength': abs(value)
                })

        return sorted(active, key=lambda x: x['strength'], reverse=True)

    def pattern_statistics(self, forward_returns_periods=[1, 5, 10]):
        """Calculate pattern prediction accuracy"""
        patterns = self.scan_all_patterns()
        stats = {}

        for period in forward_returns_periods:
            forward_returns = self.df['close'].pct_change(period).shift(-period)

            for pattern in self.PATTERNS:
                bullish_mask = patterns[pattern] > 0
                bearish_mask = patterns[pattern] < 0

                if bullish_mask.sum() > 10:  # Minimum occurrences
                    bullish_accuracy = (forward_returns[bullish_mask] > 0).mean()
                    bearish_accuracy = (forward_returns[bearish_mask] < 0).mean()

                    stats[f'{pattern}_{period}d'] = {
                        'bullish_accuracy': bullish_accuracy,
                        'bearish_accuracy': bearish_accuracy,
                        'bullish_count': bullish_mask.sum(),
                        'bearish_count': bearish_mask.sum()
                    }

        return pd.DataFrame(stats).T

# Usage
scanner = PatternScanner(df)
active = scanner.get_active_patterns()
print("Active patterns today:")
for p in active:
    print(f"  {p['pattern']}: {p['signal']} (strength: {p['strength']})")
```

### Workflow 3: Real-Time Indicator Dashboard

**Objective**: Build streaming indicator calculations

```python
import talib
import numpy as np
from collections import deque
from dataclasses import dataclass
from typing import Optional

@dataclass
class OHLCV:
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float

class RealTimeIndicators:
    def __init__(self, lookback=200):
        self.lookback = lookback
        self.data = {
            'open': deque(maxlen=lookback),
            'high': deque(maxlen=lookback),
            'low': deque(maxlen=lookback),
            'close': deque(maxlen=lookback),
            'volume': deque(maxlen=lookback)
        }

    def update(self, candle: OHLCV) -> dict:
        """Update with new candle and return indicators"""
        self.data['open'].append(candle.open)
        self.data['high'].append(candle.high)
        self.data['low'].append(candle.low)
        self.data['close'].append(candle.close)
        self.data['volume'].append(candle.volume)

        if len(self.data['close']) < 30:
            return {}

        # Convert to numpy arrays
        close = np.array(self.data['close'])
        high = np.array(self.data['high'])
        low = np.array(self.data['low'])
        volume = np.array(self.data['volume'])

        # Calculate indicators
        indicators = {}

        # Moving averages
        indicators['sma20'] = talib.SMA(close, 20)[-1]
        indicators['ema20'] = talib.EMA(close, 20)[-1]

        # Momentum
        indicators['rsi'] = talib.RSI(close, 14)[-1]

        # MACD
        macd, signal, hist = talib.MACD(close, 12, 26, 9)
        indicators['macd'] = macd[-1]
        indicators['macd_signal'] = signal[-1]
        indicators['macd_hist'] = hist[-1]

        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(close, 20)
        indicators['bb_upper'] = upper[-1]
        indicators['bb_middle'] = middle[-1]
        indicators['bb_lower'] = lower[-1]
        indicators['bb_pct'] = (close[-1] - lower[-1]) / (upper[-1] - lower[-1])

        # Volatility
        indicators['atr'] = talib.ATR(high, low, close, 14)[-1]

        # Stochastic
        slowk, slowd = talib.STOCH(high, low, close, 14, 3, 0, 3, 0)
        indicators['stoch_k'] = slowk[-1]
        indicators['stoch_d'] = slowd[-1]

        return indicators

    def get_signal(self, indicators: dict) -> str:
        """Generate trading signal from indicators"""
        if not indicators:
            return 'HOLD'

        score = 0

        # RSI
        if indicators.get('rsi', 50) < 30:
            score += 1
        elif indicators.get('rsi', 50) > 70:
            score -= 1

        # MACD
        if indicators.get('macd_hist', 0) > 0:
            score += 1
        else:
            score -= 1

        # Bollinger
        if indicators.get('bb_pct', 0.5) < 0.1:
            score += 1
        elif indicators.get('bb_pct', 0.5) > 0.9:
            score -= 1

        if score >= 2:
            return 'BUY'
        elif score <= -2:
            return 'SELL'
        return 'HOLD'

# Usage in streaming context
rt_indicators = RealTimeIndicators()

# Simulate streaming data
for candle in stream_candles():
    indicators = rt_indicators.update(candle)
    signal = rt_indicators.get_signal(indicators)
    print(f"RSI: {indicators.get('rsi', 'N/A'):.2f}, Signal: {signal}")
```

## When to Use vs Alternatives

| Scenario | Best Choice | Rationale |
|----------|-------------|-----------|
| Standard indicators | **TA-Lib** | Fast C implementation, 150+ functions |
| Custom indicators | pandas-ta or manual | More flexible than TA-Lib |
| Streaming/real-time | **TA-Lib** | Low latency, efficient |
| GPU acceleration | cudf + custom | TA-Lib is CPU-only |
| Pattern recognition | **TA-Lib** | 61 built-in patterns |
| Research/prototyping | pandas-ta | More Pythonic API |

## Common Issues & Solutions

### Issue 1: Installation Failures
```bash
# Problem: TA-Lib not found
# Solution: Install C library first

# Linux
sudo apt-get install build-essential
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/ && ./configure --prefix=/usr && make && sudo make install

# macOS
brew install ta-lib

# Windows: Use pre-built wheel
pip install TA-Lib-binary

# Or conda
conda install -c conda-forge ta-lib
```

### Issue 2: NaN Values in Output
```python
# Problem: Indicators return NaN for early values
# Solution: Handle lookback period

close = np.array([100, 101, 102, 103, 104, 105])
sma = talib.SMA(close, timeperiod=3)
print(sma)  # [nan, nan, 101.0, 102.0, 103.0, 104.0]

# Handle NaN
sma = np.nan_to_num(sma, nan=close[0])  # Fill with first value
# Or
valid_sma = sma[~np.isnan(sma)]  # Remove NaN values
```

### Issue 3: Integer Input Error
```python
# Problem: TA-Lib expects float arrays
# Solution: Convert to float

close_int = np.array([100, 101, 102], dtype=np.int64)
# talib.SMA(close_int, 20)  # May fail

close_float = close_int.astype(np.float64)
sma = talib.SMA(close_float, 20)  # Works
```

### Issue 4: Pandas Series Compatibility
```python
# Problem: TA-Lib returns numpy array, not pandas Series
# Solution: Wrap in Series with index

import pandas as pd

df['close'] = close_series
sma = talib.SMA(df['close'].values, timeperiod=20)

# Preserve index
df['sma20'] = pd.Series(sma, index=df.index)
```

## Advanced Topics

### Stream Functions (Incremental Updates)
```python
# TA-Lib stream functions for single-value updates
# More efficient for real-time data

# Regular API (recalculates entire array)
sma_all = talib.SMA(close_array, 20)

# Stream API (single value, maintains state)
from talib.stream import SMA as stream_SMA

# Note: Stream functions are experimental
# Alternative: maintain rolling window
class StreamSMA:
    def __init__(self, period):
        self.period = period
        self.values = deque(maxlen=period)

    def update(self, value):
        self.values.append(value)
        if len(self.values) == self.period:
            return sum(self.values) / self.period
        return None
```

### Custom Indicator Combinations
```python
def supertrend(high, low, close, period=10, multiplier=3):
    """SuperTrend indicator using TA-Lib components"""
    atr = talib.ATR(high, low, close, period)
    hl2 = (high + low) / 2

    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)

    supertrend = np.zeros_like(close)
    direction = np.ones_like(close)

    for i in range(1, len(close)):
        if close[i] > upper_band[i-1]:
            direction[i] = 1
        elif close[i] < lower_band[i-1]:
            direction[i] = -1
        else:
            direction[i] = direction[i-1]

        if direction[i] == 1:
            supertrend[i] = max(lower_band[i], supertrend[i-1]) if supertrend[i-1] > 0 else lower_band[i]
        else:
            supertrend[i] = min(upper_band[i], supertrend[i-1]) if supertrend[i-1] > 0 else upper_band[i]

    return supertrend, direction
```

## Best Practices Checklist

- [ ] Install C library before Python wrapper
- [ ] Use float64 arrays as input
- [ ] Handle NaN values from lookback periods
- [ ] Preserve DataFrame index when converting
- [ ] Use abstract API for flexibility
- [ ] Validate pattern signals with forward returns
- [ ] Combine multiple indicator categories
- [ ] Test indicator lag and responsiveness
- [ ] Document indicator parameters
- [ ] Optimize for streaming with rolling windows

## Resources

- **Official Docs**: https://ta-lib.github.io/ta-lib-python/
- **Function List**: https://ta-lib.github.io/ta-lib-python/funcs.html
- **GitHub**: https://github.com/TA-Lib/ta-lib-python
- **C Library**: https://ta-lib.org/

See [references/indicators.md](references/indicators.md) for all 150+ indicators.
See [references/patterns.md](references/patterns.md) for candlestick patterns.
