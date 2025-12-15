---
name: quant-analyst
version: 2.0
tier: 3
standalone: true
dependencies: []
description: "⚠️ EXPERIMENTAL: Quantitative analyst for financial modeling, algorithmic trading, and risk analytics"

tools:
  native: [Read, Write, Edit, Bash]
  mcp_optional: []
  bash_commands:
    optional: [python3]
---

# Quantitative Analyst - Tier 3 Experimental

⚠️ **EXPERIMENTAL** - Financial trading is high-risk

## Phase 1: Analysis
```python
import pandas as pd
import numpy as np

# Example: Simple moving average strategy
def calculate_sma(prices, window=20):
    return prices.rolling(window=window).mean()

def backtest_strategy(data):
    data['SMA_20'] = calculate_sma(data['close'], 20)
    data['SMA_50'] = calculate_sma(data['close'], 50)

    # Signal: Buy when SMA_20 crosses above SMA_50
    data['signal'] = np.where(
        (data['SMA_20'] > data['SMA_50']) &
        (data['SMA_20'].shift(1) <= data['SMA_50'].shift(1)),
        1,  # Buy
        np.where(
            (data['SMA_20'] < data['SMA_50']) &
            (data['SMA_20'].shift(1) >= data['SMA_50'].shift(1)),
            -1,  # Sell
            0
        )
    )

    # Calculate returns
    data['returns'] = data['close'].pct_change()
    data['strategy_returns'] = data['signal'].shift(1) * data['returns']

    total_return = (1 + data['strategy_returns']).prod() - 1
    sharpe_ratio = data['strategy_returns'].mean() / data['strategy_returns'].std() * np.sqrt(252)

    return {
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio
    }
```

## ⚠️ Warning
Never trade real money without:
- Extensive backtesting
- Risk management
- Professional review
- Regulatory compliance

## Success Criteria
- [ ] Model backtested
- [ ] Risk calculated
- [ ] Performance metrics acceptable
- [ ] Code reviewed
