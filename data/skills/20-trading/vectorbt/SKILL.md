---
name: vectorized-backtesting-vectorbt
description: Expert guidance for high-performance vectorized backtesting and portfolio optimization using VectorBT for rapid strategy iteration
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, Backtesting, Vectorization, Performance, Portfolio Optimization, NumPy, Python, Technical Analysis]
dependencies: [vectorbt>=0.26.0, pandas>=1.4.0, numpy>=1.21.0, numba>=0.56.0, plotly>=5.0.0]
---

# VectorBT: High-Performance Vectorized Backtesting

## Quick Start

### Installation
```bash
pip install vectorbt

# With all extras (recommended)
pip install "vectorbt[full]"

# For GPU acceleration (optional)
pip install cupy-cuda11x  # Match CUDA version
```

### Minimal Example
```python
import vectorbt as vbt
import numpy as np

# Download data
btc_price = vbt.YFData.download('BTC-USD', start='2020-01-01', end='2024-01-01').get('Close')

# Simple SMA crossover strategy
fast_ma = vbt.MA.run(btc_price, window=10)
slow_ma = vbt.MA.run(btc_price, window=50)

# Generate signals
entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

# Run backtest
portfolio = vbt.Portfolio.from_signals(
    btc_price,
    entries=entries,
    exits=exits,
    init_cash=10000,
    fees=0.001
)

# Results
print(f"Total Return: {portfolio.total_return():.2%}")
print(f"Sharpe Ratio: {portfolio.sharpe_ratio():.2f}")
print(f"Max Drawdown: {portfolio.max_drawdown():.2%}")

# Visualize
portfolio.plot().show()
```

## Core Concepts

### Vectorization Philosophy
```
Traditional (Event-Driven):
  for bar in data:        # O(n) iterations
      process(bar)        # Sequential, slow

VectorBT (Vectorized):
  signals = data > threshold  # O(1) operation
  result = np.where(signals)  # NumPy broadcasting
  # 100-1000x faster for large datasets
```

### Data Structures
```python
# Price data as pandas Series/DataFrame
import pandas as pd
close = pd.Series([100, 102, 98, 105, 103])

# Signals as boolean arrays
entries = np.array([True, False, False, True, False])
exits = np.array([False, False, True, False, True])

# VectorBT accessories (computed indicators)
rsi = vbt.RSI.run(close, window=14)
print(rsi.rsi)  # Access indicator values
```

### Signal Generation
```python
# Boolean crossover signals
entries = fast_ma.ma_crossed_above(slow_ma)  # Returns boolean array
exits = fast_ma.ma_crossed_below(slow_ma)

# Threshold-based signals
entries = rsi.rsi_below(30)  # RSI < 30
exits = rsi.rsi_above(70)    # RSI > 70

# Combined signals (vectorized AND/OR)
entries = (rsi.rsi_below(30)) & (close > slow_ma.ma)
exits = (rsi.rsi_above(70)) | (close < slow_ma.ma)
```

## Common Workflows

### Workflow 1: Parameter Optimization (Grid Search)

**Objective**: Find optimal indicator parameters

```python
import vectorbt as vbt
import numpy as np

# Download data
price = vbt.YFData.download('SPY', start='2015-01-01', end='2024-01-01').get('Close')

# Define parameter ranges
fast_windows = np.arange(5, 50, 5)    # [5, 10, 15, ..., 45]
slow_windows = np.arange(20, 200, 10)  # [20, 30, 40, ..., 190]

# Run all combinations at once (vectorized!)
fast_ma, slow_ma = vbt.MA.run_combs(
    price,
    window=fast_windows,
    r=2,  # Combinations of 2
    short_names=['fast', 'slow']
)

# Generate signals for all combinations
entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

# Backtest all combinations simultaneously
portfolio = vbt.Portfolio.from_signals(
    price,
    entries=entries,
    exits=exits,
    init_cash=10000,
    fees=0.001
)

# Find best parameters by Sharpe ratio
sharpe = portfolio.sharpe_ratio()
best_idx = sharpe.idxmax()
print(f"Best Parameters: {best_idx}")
print(f"Best Sharpe: {sharpe[best_idx]:.2f}")

# Heatmap visualization
sharpe_matrix = sharpe.unstack()
sharpe_matrix.vbt.heatmap(
    title='Sharpe Ratio by MA Parameters',
    xaxis_title='Slow MA',
    yaxis_title='Fast MA'
).show()
```

**Checklist**:
- [ ] Use `run_combs` for parameter combinations
- [ ] Keep parameter ranges reasonable (avoid overfitting)
- [ ] Validate with out-of-sample data
- [ ] Use multiple metrics (Sharpe, Sortino, Max DD)
- [ ] Consider transaction costs

### Workflow 2: Multi-Asset Portfolio Analysis

**Objective**: Analyze portfolio with multiple assets

```python
import vectorbt as vbt
import numpy as np

# Download multiple assets
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
prices = vbt.YFData.download(symbols, start='2020-01-01', end='2024-01-01').get('Close')

# Calculate RSI for all assets
rsi = vbt.RSI.run(prices, window=14)

# Entry: RSI < 30 (oversold)
# Exit: RSI > 70 (overbought)
entries = rsi.rsi_below(30)
exits = rsi.rsi_above(70)

# Portfolio with equal weights
portfolio = vbt.Portfolio.from_signals(
    prices,
    entries=entries,
    exits=exits,
    init_cash=100000,
    fees=0.001,
    size=0.2,  # 20% per position
    size_type='targetpercent',
    group_by=True,  # Treat as single portfolio
    cash_sharing=True  # Share cash across assets
)

# Portfolio metrics
print(portfolio.stats())

# Per-asset returns
asset_returns = portfolio.total_return()
print("\nPer-Asset Returns:")
print(asset_returns)

# Correlation analysis
returns = prices.pct_change().dropna()
correlation = returns.corr()
correlation.vbt.heatmap(title='Asset Correlation').show()

# Drawdown analysis
portfolio.drawdowns.plot().show()
```

### Workflow 3: Walk-Forward Optimization

**Objective**: Robust optimization with rolling windows

```python
import vectorbt as vbt
import numpy as np
import pandas as pd

def walk_forward_optimize(price, fast_range, slow_range,
                          train_period='252D', test_period='63D'):
    """Walk-forward optimization with rolling windows"""
    results = []

    # Create date ranges
    total_days = len(price)
    train_days = pd.Timedelta(train_period).days
    test_days = pd.Timedelta(test_period).days

    start_idx = 0
    while start_idx + train_days + test_days <= total_days:
        train_end = start_idx + train_days
        test_end = train_end + test_days

        train_price = price.iloc[start_idx:train_end]
        test_price = price.iloc[train_end:test_end]

        # Optimize on training data
        best_fast, best_slow, train_sharpe = optimize_params(
            train_price, fast_range, slow_range
        )

        # Test on out-of-sample data
        test_sharpe, test_return = test_params(
            test_price, best_fast, best_slow
        )

        results.append({
            'train_start': price.index[start_idx],
            'train_end': price.index[train_end],
            'test_end': price.index[test_end],
            'best_fast': best_fast,
            'best_slow': best_slow,
            'train_sharpe': train_sharpe,
            'test_sharpe': test_sharpe,
            'test_return': test_return
        })

        start_idx = train_end  # Roll forward

    return pd.DataFrame(results)

def optimize_params(price, fast_range, slow_range):
    """Find best parameters on training data"""
    fast_ma = vbt.MA.run(price, window=fast_range)
    slow_ma = vbt.MA.run(price, window=slow_range)

    # All combinations
    entries_list = []
    exits_list = []
    params = []

    for f in fast_range:
        for s in slow_range:
            if f < s:
                fast = vbt.MA.run(price, window=f)
                slow = vbt.MA.run(price, window=s)
                entries_list.append(fast.ma_crossed_above(slow))
                exits_list.append(fast.ma_crossed_below(slow))
                params.append((f, s))

    if not params:
        return fast_range[0], slow_range[0], 0

    entries = pd.concat(entries_list, axis=1)
    exits = pd.concat(exits_list, axis=1)

    pf = vbt.Portfolio.from_signals(price, entries, exits, fees=0.001)
    sharpes = pf.sharpe_ratio()

    best_idx = sharpes.argmax()
    return params[best_idx][0], params[best_idx][1], sharpes.iloc[best_idx]

def test_params(price, fast, slow):
    """Test parameters on out-of-sample data"""
    fast_ma = vbt.MA.run(price, window=fast)
    slow_ma = vbt.MA.run(price, window=slow)

    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    pf = vbt.Portfolio.from_signals(price, entries, exits, fees=0.001)
    return pf.sharpe_ratio(), pf.total_return()

# Run walk-forward
price = vbt.YFData.download('SPY', start='2015-01-01').get('Close')
results = walk_forward_optimize(
    price,
    fast_range=np.arange(5, 30, 5),
    slow_range=np.arange(20, 100, 10)
)
print(results)
print(f"\nAverage OOS Sharpe: {results['test_sharpe'].mean():.2f}")
```

### Workflow 4: Custom Indicator Development

**Objective**: Create optimized custom indicators

```python
import vectorbt as vbt
import numpy as np
from numba import njit

# Numba-optimized indicator function
@njit
def keltner_channel_nb(high, low, close, atr_period, atr_mult, ma_period):
    """Keltner Channel with Numba acceleration"""
    n = len(close)

    # Calculate EMA (basis)
    ema = np.empty(n)
    alpha = 2 / (ma_period + 1)
    ema[0] = close[0]
    for i in range(1, n):
        ema[i] = alpha * close[i] + (1 - alpha) * ema[i-1]

    # Calculate ATR
    tr = np.empty(n)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(high[i] - low[i],
                    abs(high[i] - close[i-1]),
                    abs(low[i] - close[i-1]))

    atr = np.empty(n)
    atr[:atr_period] = np.nan
    atr[atr_period-1] = np.mean(tr[:atr_period])
    for i in range(atr_period, n):
        atr[i] = (atr[i-1] * (atr_period-1) + tr[i]) / atr_period

    # Calculate bands
    upper = ema + atr * atr_mult
    lower = ema - atr * atr_mult

    return ema, upper, lower

# Create VectorBT indicator factory
KeltnerChannel = vbt.IndicatorFactory(
    class_name='KeltnerChannel',
    short_name='kc',
    input_names=['high', 'low', 'close'],
    param_names=['atr_period', 'atr_mult', 'ma_period'],
    output_names=['basis', 'upper', 'lower']
).from_apply_func(
    keltner_channel_nb,
    atr_period=20,
    atr_mult=2.0,
    ma_period=20
)

# Use the custom indicator
data = vbt.YFData.download('SPY', start='2020-01-01')
kc = KeltnerChannel.run(
    data.get('High'),
    data.get('Low'),
    data.get('Close'),
    atr_period=20,
    atr_mult=[1.5, 2.0, 2.5],  # Test multiple multipliers
    ma_period=20
)

# Generate signals: buy at lower band, sell at upper band
entries = data.get('Close') < kc.lower
exits = data.get('Close') > kc.upper

# Backtest
pf = vbt.Portfolio.from_signals(
    data.get('Close'),
    entries=entries,
    exits=exits,
    fees=0.001
)

print(pf.stats())
```

## When to Use vs Alternatives

| Scenario | Best Choice | Rationale |
|----------|-------------|-----------|
| Rapid parameter optimization | **VectorBT** | 100-1000x faster than event-driven |
| Complex order types | Backtrader | VectorBT has limited order support |
| Live trading | Backtrader/Freqtrade | VectorBT is backtesting-focused |
| Portfolio analytics | **VectorBT** | Excellent visualization & metrics |
| Machine learning integration | **VectorBT** | NumPy-native, works with sklearn |
| Low-level customization | Backtrader | More granular control |

## Common Issues & Solutions

### Issue 1: Memory Errors with Large Datasets
```python
# Problem: Out of memory with many parameter combinations
# Solution: Use chunked processing

def chunked_optimization(price, param_ranges, chunk_size=100):
    """Process parameter combinations in chunks"""
    all_params = list(itertools.product(*param_ranges))
    results = []

    for i in range(0, len(all_params), chunk_size):
        chunk = all_params[i:i+chunk_size]
        # Process chunk...
        results.append(chunk_result)

    return pd.concat(results)

# Or use numba mode for memory efficiency
vbt.settings.array.wrapper['freq'] = 'D'
vbt.settings.portfolio['init_cash'] = 10000
```

### Issue 2: Slow Custom Indicators
```python
# Problem: Python loops are slow
# Solution: Use @njit decorator

from numba import njit

@njit  # Just-In-Time compilation
def fast_custom_indicator(close, period):
    n = len(close)
    result = np.empty(n)
    for i in range(period, n):
        result[i] = np.mean(close[i-period:i])
    return result

# 10-100x speedup with Numba
```

### Issue 3: Signal Alignment Issues
```python
# Problem: Entries and exits don't align with price data
# Solution: Ensure same index/shape

entries = pd.Series(entries_array, index=price.index)
exits = pd.Series(exits_array, index=price.index)

# Or use vbt.Signals for automatic alignment
entries = vbt.signals.clean(entries)
exits = vbt.signals.clean(exits, entries)  # Cleans relative to entries
```

### Issue 4: Incorrect Sharpe Calculation
```python
# Problem: Sharpe ratio seems wrong
# Solution: Check frequency settings

portfolio = vbt.Portfolio.from_signals(
    price,
    entries=entries,
    exits=exits,
    freq='D'  # Explicitly set frequency
)

# Annualized Sharpe (assumes daily data)
sharpe = portfolio.sharpe_ratio()

# Or calculate manually
returns = portfolio.returns()
sharpe_manual = returns.mean() / returns.std() * np.sqrt(252)
```

## Advanced Topics

### GPU Acceleration with CuPy
```python
import cupy as cp
import vectorbt as vbt

# Move data to GPU
price_gpu = cp.array(price.values)

# Run computations on GPU
@njit
def gpu_strategy(price):
    # Numba + CuPy for GPU computation
    pass

# Note: Limited GPU support in VectorBT
# Consider PyTorch/JAX for heavy GPU workloads
```

### Integration with Machine Learning
```python
import vectorbt as vbt
from sklearn.ensemble import RandomForestClassifier

# Prepare features
price = vbt.YFData.download('SPY', start='2015-01-01').get('Close')
returns = price.pct_change()

# Feature engineering
features = pd.DataFrame({
    'rsi': vbt.RSI.run(price).rsi,
    'ma_ratio': price / vbt.MA.run(price, window=20).ma,
    'volatility': returns.rolling(20).std(),
    'momentum': returns.rolling(10).sum()
}).dropna()

# Labels: 1 if next day is up
labels = (returns.shift(-1) > 0).astype(int)[features.index]

# Train model
X_train, X_test = features[:-252], features[-252:]
y_train, y_test = labels[:-252], labels[-252:]

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Generate signals from predictions
predictions = model.predict(X_test)
entries = pd.Series(predictions == 1, index=X_test.index)
exits = pd.Series(predictions == 0, index=X_test.index)

# Backtest ML strategy
pf = vbt.Portfolio.from_signals(
    price[X_test.index],
    entries=entries,
    exits=exits
)
print(pf.stats())
```

## Best Practices Checklist

- [ ] Use vectorized operations (avoid Python loops)
- [ ] Apply `@njit` decorator for custom functions
- [ ] Set explicit data frequency with `freq` parameter
- [ ] Include realistic transaction costs
- [ ] Validate with out-of-sample testing
- [ ] Check for look-ahead bias in signals
- [ ] Use `vbt.signals.clean()` for signal hygiene
- [ ] Monitor memory usage with large parameter spaces
- [ ] Combine with walk-forward analysis
- [ ] Document parameter sensitivity

## Resources

- **Official Docs**: https://vectorbt.dev/
- **GitHub**: https://github.com/polakowo/vectorbt
- **Tutorials**: https://vectorbt.dev/tutorials/
- **API Reference**: https://vectorbt.dev/api/

See [references/indicators.md](references/indicators.md) for built-in indicators.
See [references/portfolio.md](references/portfolio.md) for portfolio analysis.
See [references/optimization.md](references/optimization.md) for advanced optimization.
