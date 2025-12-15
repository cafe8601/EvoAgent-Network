---
name: algorithmic-backtesting-backtrader
description: Expert guidance for building and backtesting trading strategies using Backtrader framework with live trading integration
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, Backtesting, Algorithmic Trading, Strategy Development, Live Trading, Python, Technical Analysis]
dependencies: [backtrader>=1.9.78, matplotlib>=3.5.0, pandas>=1.4.0, numpy>=1.21.0]
---

# Backtrader: Algorithmic Trading & Backtesting

## Quick Start

### Environment Setup
```bash
pip install backtrader matplotlib pandas numpy
# For interactive plotting
pip install backtrader[plotting]
# For live trading with Interactive Brokers
pip install backtrader[ib]
```

### Minimal Strategy Example
```python
import backtrader as bt
import datetime

class SMAStrategy(bt.Strategy):
    params = (
        ('sma_period', 20),
        ('stake', 10),
    )

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.sma_period)
        self.order = None

    def next(self):
        if self.order:
            return  # Pending order exists

        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.order = self.buy(size=self.params.stake)
        else:
            if self.data.close[0] < self.sma[0]:
                self.order = self.sell(size=self.params.stake)

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None

# Run backtest
cerebro = bt.Cerebro()
cerebro.addstrategy(SMAStrategy)

# Add data feed
data = bt.feeds.YahooFinanceData(
    dataname='AAPL',
    fromdate=datetime.datetime(2020, 1, 1),
    todate=datetime.datetime(2023, 12, 31)
)
cerebro.adddata(data)

# Set initial capital
cerebro.broker.setcash(100000.0)

# Add analyzers
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

print(f'Starting Portfolio: ${cerebro.broker.getvalue():,.2f}')
results = cerebro.run()
print(f'Final Portfolio: ${cerebro.broker.getvalue():,.2f}')
cerebro.plot()
```

## Core Concepts

### Strategy Architecture
```
Strategy Components:
├── __init__(): Indicator setup (run once)
├── prenext(): Called before data maturity
├── next(): Main trading logic (called per bar)
├── notify_order(): Order status updates
├── notify_trade(): Trade completion events
└── stop(): Called at end of backtest
```

### Data Feed Line Indexing
```python
# Current bar
self.data.close[0]

# Previous bar
self.data.close[-1]

# Two bars ago
self.data.close[-2]

# Access by line name
self.data.lines.close[0]
self.data_close[0]  # Shortcut
```

### Order Types
```python
# Market order (default)
self.buy(size=100)
self.sell(size=100)

# Limit order
self.buy(size=100, exectype=bt.Order.Limit, price=150.0)

# Stop order
self.sell(size=100, exectype=bt.Order.Stop, price=145.0)

# Stop-Limit order
self.buy(size=100, exectype=bt.Order.StopLimit, price=155.0, plimit=156.0)

# Bracket order (entry + stop-loss + take-profit)
self.buy_bracket(
    size=100,
    price=150.0,           # Entry
    stopprice=145.0,       # Stop-loss
    stopexec=bt.Order.Stop,
    limitprice=160.0       # Take-profit
)
```

## Common Workflows

### Workflow 1: Multi-Indicator Strategy Development

**Objective**: Build crossover strategy with multiple confirmations

```python
class MultiIndicatorStrategy(bt.Strategy):
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
    )

    def __init__(self):
        # Moving average crossover
        self.fast_sma = bt.indicators.SMA(period=self.p.fast_period)
        self.slow_sma = bt.indicators.SMA(period=self.p.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)

        # RSI filter
        self.rsi = bt.indicators.RSI(period=self.p.rsi_period)

        # ATR for position sizing
        self.atr = bt.indicators.ATR(period=14)

    def next(self):
        if not self.position:
            # Long: MA crossover up + RSI not overbought
            if self.crossover[0] > 0 and self.rsi[0] < self.p.rsi_overbought:
                size = self.calculate_position_size()
                self.buy(size=size)
        else:
            # Exit: MA crossover down OR RSI overbought
            if self.crossover[0] < 0 or self.rsi[0] > self.p.rsi_overbought:
                self.close()

    def calculate_position_size(self):
        """Risk-based position sizing"""
        risk_per_trade = 0.02  # 2% risk
        account_value = self.broker.getvalue()
        risk_amount = account_value * risk_per_trade
        stop_distance = self.atr[0] * 2
        return int(risk_amount / stop_distance)
```

**Checklist**:
- [ ] Define all indicators in `__init__`
- [ ] Use `.p.` or `.params.` for parameter access
- [ ] Implement position sizing logic
- [ ] Add entry/exit confirmations
- [ ] Test with notify_order for order tracking

### Workflow 2: Multi-Asset Portfolio Strategy

**Objective**: Trade multiple instruments with correlation-based allocation

```python
class PortfolioStrategy(bt.Strategy):
    params = (
        ('rebalance_days', 30),
        ('momentum_period', 20),
    )

    def __init__(self):
        self.indicators = {}
        for d in self.datas:
            self.indicators[d._name] = {
                'momentum': bt.indicators.Momentum(d.close, period=self.p.momentum_period),
                'sma': bt.indicators.SMA(d.close, period=50),
            }
        self.rebalance_counter = 0

    def next(self):
        self.rebalance_counter += 1
        if self.rebalance_counter < self.p.rebalance_days:
            return

        self.rebalance_counter = 0
        self.rebalance()

    def rebalance(self):
        # Rank assets by momentum
        rankings = []
        for d in self.datas:
            if len(d) > self.p.momentum_period:
                mom = self.indicators[d._name]['momentum'][0]
                rankings.append((d, mom))

        rankings.sort(key=lambda x: x[1], reverse=True)

        # Allocate to top performers
        top_n = min(3, len(rankings))
        allocation = 0.9 / top_n if top_n > 0 else 0

        # Close positions not in top
        for d, _ in rankings[top_n:]:
            if self.getposition(d).size != 0:
                self.close(data=d)

        # Allocate to top performers
        for d, _ in rankings[:top_n]:
            target_value = self.broker.getvalue() * allocation
            current_value = self.getposition(d).size * d.close[0]
            diff = target_value - current_value
            if abs(diff) > d.close[0]:
                if diff > 0:
                    self.buy(data=d, size=int(diff / d.close[0]))
                else:
                    self.sell(data=d, size=int(abs(diff) / d.close[0]))

# Add multiple data feeds
cerebro = bt.Cerebro()
cerebro.addstrategy(PortfolioStrategy)

for symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN']:
    data = bt.feeds.YahooFinanceData(
        dataname=symbol,
        fromdate=datetime.datetime(2020, 1, 1),
        todate=datetime.datetime(2023, 12, 31)
    )
    cerebro.adddata(data, name=symbol)
```

### Workflow 3: Walk-Forward Optimization

**Objective**: Avoid overfitting with out-of-sample validation

```python
import backtrader as bt
from datetime import datetime, timedelta

def walk_forward_analysis(strategy_class, data_feed, params_grid,
                          in_sample_days=252, out_sample_days=63):
    """Walk-forward optimization with rolling windows"""
    results = []
    start_date = data_feed.fromdate
    end_date = data_feed.todate

    current_date = start_date
    while current_date + timedelta(days=in_sample_days + out_sample_days) <= end_date:
        in_sample_end = current_date + timedelta(days=in_sample_days)
        out_sample_end = in_sample_end + timedelta(days=out_sample_days)

        # In-sample optimization
        best_params = optimize_in_sample(
            strategy_class, data_feed, params_grid,
            current_date, in_sample_end
        )

        # Out-of-sample test
        oos_result = test_out_of_sample(
            strategy_class, data_feed, best_params,
            in_sample_end, out_sample_end
        )

        results.append({
            'period': (current_date, out_sample_end),
            'best_params': best_params,
            'oos_sharpe': oos_result['sharpe'],
            'oos_return': oos_result['return']
        })

        current_date = in_sample_end

    return results

def optimize_in_sample(strategy_class, data_feed, params_grid,
                       start_date, end_date):
    """Grid search optimization on in-sample data"""
    best_sharpe = float('-inf')
    best_params = None

    for params in params_grid:
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class, **params)

        data = bt.feeds.YahooFinanceData(
            dataname=data_feed.dataname,
            fromdate=start_date,
            todate=end_date
        )
        cerebro.adddata(data)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

        results = cerebro.run()
        sharpe = results[0].analyzers.sharpe.get_analysis().get('sharperatio', 0)

        if sharpe and sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = params

    return best_params
```

## When to Use vs Alternatives

| Scenario | Best Choice | Rationale |
|----------|-------------|-----------|
| Python-based backtesting | **Backtrader** | Flexible, event-driven, excellent documentation |
| Vectorized fast backtesting | VectorBT | 100x faster for simple strategies |
| Crypto trading bot | Freqtrade | Built-in exchange support, ML integration |
| Institutional-grade research | Zipline/QuantConnect | Better for complex portfolios |
| Live trading (stocks) | **Backtrader + IB** | Native Interactive Brokers integration |
| Quick prototyping | **Backtrader** | Minimal boilerplate, rapid iteration |

## Common Issues & Solutions

### Issue 1: Data Feed Not Aligning
```python
# Problem: Multiple data feeds have different lengths
# Solution: Use cerebro.adddata with timeframe alignment

data1 = bt.feeds.GenericCSVData(
    dataname='stock1.csv',
    dtformat='%Y-%m-%d',
    timeframe=bt.TimeFrame.Days,
    compression=1
)
data2 = bt.feeds.GenericCSVData(
    dataname='stock2.csv',
    dtformat='%Y-%m-%d',
    timeframe=bt.TimeFrame.Days,
    compression=1
)

cerebro.adddata(data1, name='stock1')
cerebro.adddata(data2, name='stock2')

# In strategy, check data availability
def next(self):
    for d in self.datas:
        if len(d) < self.p.lookback:
            return  # Skip until all data mature
```

### Issue 2: Order Not Executing
```python
# Problem: Orders pending but never executed
# Solution: Check for sufficient cash and commission settings

cerebro.broker.setcash(100000.0)
cerebro.broker.setcommission(commission=0.001)  # 0.1%

# Enable cheat-on-close for market orders at close price
cerebro.broker.set_coc(True)

# Or enable cheat-on-open for market orders at open price
cerebro.broker.set_coo(True)
```

### Issue 3: Indicator Warmup Period
```python
# Problem: Indicators need warmup, causing errors
# Solution: Use prenext or check indicator maturity

def __init__(self):
    self.sma50 = bt.indicators.SMA(period=50)
    self.sma200 = bt.indicators.SMA(period=200)

def prenext(self):
    # Called until all indicators are ready
    pass

def next(self):
    # Called only when all indicators have values
    # Alternatively, explicit check:
    if len(self) < 200:
        return
```

### Issue 4: Memory Issues with Large Datasets
```python
# Problem: Out of memory with large backtests
# Solution: Use preload=False and runonce=False

cerebro = bt.Cerebro(stdstats=False, preload=False, runonce=False)

# Reduce memory by limiting stored data
data = bt.feeds.GenericCSVData(
    dataname='large_data.csv',
    preload=False
)
```

## Advanced Topics

### Custom Indicator Development
```python
class VolumeWeightedMACD(bt.Indicator):
    lines = ('vwmacd', 'signal', 'histogram')
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
    )

    def __init__(self):
        # Volume-weighted prices
        vwp = self.data.close * self.data.volume

        fast_vw = bt.indicators.EMA(vwp, period=self.p.fast_period)
        slow_vw = bt.indicators.EMA(vwp, period=self.p.slow_period)
        fast_vol = bt.indicators.EMA(self.data.volume, period=self.p.fast_period)
        slow_vol = bt.indicators.EMA(self.data.volume, period=self.p.slow_period)

        fast_vwma = fast_vw / fast_vol
        slow_vwma = slow_vw / slow_vol

        self.lines.vwmacd = fast_vwma - slow_vwma
        self.lines.signal = bt.indicators.EMA(self.l.vwmacd, period=self.p.signal_period)
        self.lines.histogram = self.l.vwmacd - self.l.signal
```

### Live Trading with Interactive Brokers
```python
from backtrader.stores import IBStore

# Connect to IB Gateway/TWS
store = IBStore(host='127.0.0.1', port=7497, clientId=1)

# Create cerebro with live broker
cerebro = bt.Cerebro()
cerebro.setbroker(store.getbroker())

# Live data feed
data = store.getdata(
    dataname='AAPL-STK-SMART-USD',
    timeframe=bt.TimeFrame.Minutes,
    compression=1,
    historical=True
)
cerebro.adddata(data)
cerebro.addstrategy(SMAStrategy)

# Run live
cerebro.run()
```

## Performance Analysis

### Key Metrics Extraction
```python
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe',
                    timeframe=bt.TimeFrame.Days, annualize=True)
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

results = cerebro.run()
strat = results[0]

# Extract metrics
print(f"Sharpe Ratio: {strat.analyzers.sharpe.get_analysis()['sharperatio']:.2f}")
print(f"Max Drawdown: {strat.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
print(f"Total Trades: {strat.analyzers.trades.get_analysis()['total']['total']}")
print(f"SQN: {strat.analyzers.sqn.get_analysis()['sqn']:.2f}")
```

## Best Practices Checklist

- [ ] Define all indicators in `__init__`, not in `next`
- [ ] Use `params` tuple for strategy parameters
- [ ] Implement proper order management with `notify_order`
- [ ] Add position sizing based on risk management
- [ ] Use analyzers for performance metrics
- [ ] Test with commission and slippage settings
- [ ] Validate with walk-forward optimization
- [ ] Log trades for debugging
- [ ] Handle data gaps and missing values
- [ ] Use `prenext` for warmup period handling

## Resources

- **Official Docs**: https://www.backtrader.com/docu/
- **Community**: https://community.backtrader.com/
- **GitHub**: https://github.com/mementum/backtrader
- **Quickstart Guide**: https://www.backtrader.com/docu/quickstart/quickstart/

See [references/api.md](references/api.md) for complete API reference.
See [references/indicators.md](references/indicators.md) for built-in indicators.
See [references/live-trading.md](references/live-trading.md) for broker integration.
