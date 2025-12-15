---
name: crypto-trading-bot-freqtrade
description: Expert guidance for building automated cryptocurrency trading bots using Freqtrade with ML strategy integration and backtesting
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, Cryptocurrency, Trading Bot, Machine Learning, Backtesting, Strategy Development, Python]
dependencies: [freqtrade>=2024.1, pandas>=1.4.0, numpy>=1.21.0, scikit-learn>=1.0.0, ta>=0.10.0]
---

# Freqtrade: Cryptocurrency Trading Bot

## Quick Start

### Installation
```bash
# Docker (recommended)
mkdir ft_userdata
cd ft_userdata
docker pull freqtradeorg/freqtrade:stable
docker run --rm -v $(pwd):/freqtrade/user_data freqtradeorg/freqtrade:stable create-userdir --userdir user_data

# From source
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
./setup.sh -i

# Activate environment
source .venv/bin/activate
```

### Configuration
```bash
# Generate config
freqtrade new-config --config user_data/config.json

# Create new strategy
freqtrade new-strategy --strategy MyStrategy --template full
```

### Basic Strategy
```python
# user_data/strategies/my_strategy.py
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
import talib.abstract as ta
from pandas import DataFrame

class MyStrategy(IStrategy):
    # Strategy parameters
    INTERFACE_VERSION = 3

    # ROI table
    minimal_roi = {
        "60": 0.01,   # 1% after 60 minutes
        "30": 0.02,   # 2% after 30 minutes
        "0": 0.04     # 4% immediately
    }

    # Stoploss
    stoploss = -0.10  # 10% stoploss

    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02

    # Timeframe
    timeframe = '5m'

    # Hyperopt parameters
    buy_rsi = IntParameter(20, 40, default=30, space='buy')
    sell_rsi = IntParameter(60, 80, default=70, space='sell')

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Add technical indicators"""
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
        dataframe['sma_50'] = ta.SMA(dataframe, timeperiod=50)
        dataframe['ema_12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_26'] = ta.EMA(dataframe, timeperiod=26)

        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']

        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe)
        dataframe['bb_upper'] = bollinger['upperband']
        dataframe['bb_middle'] = bollinger['middleband']
        dataframe['bb_lower'] = bollinger['lowerband']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Define entry signals"""
        dataframe.loc[
            (
                (dataframe['rsi'] < self.buy_rsi.value) &
                (dataframe['close'] < dataframe['bb_lower']) &
                (dataframe['sma_20'] > dataframe['sma_50']) &
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Define exit signals"""
        dataframe.loc[
            (
                (dataframe['rsi'] > self.sell_rsi.value) |
                (dataframe['close'] > dataframe['bb_upper'])
            ),
            'exit_long'] = 1

        return dataframe
```

### Run Commands
```bash
# Backtest
freqtrade backtesting --strategy MyStrategy --timerange 20230101-20231231

# Hyperparameter optimization
freqtrade hyperopt --strategy MyStrategy --hyperopt-loss SharpeHyperOptLoss --epochs 100

# Dry run (paper trading)
freqtrade trade --strategy MyStrategy --dry-run

# Live trading
freqtrade trade --strategy MyStrategy
```

## Core Concepts

### Strategy Architecture
```
Strategy Lifecycle:
├── bot_start() → Called once at startup
├── populate_indicators() → Add technical indicators
│   └── Called once per pair, cached for efficiency
├── populate_entry_trend() → Define buy signals
│   └── Sets 'enter_long' or 'enter_short' column
├── populate_exit_trend() → Define sell signals
│   └── Sets 'exit_long' or 'exit_short' column
├── custom_entry_price() → Optional custom entry price
├── custom_exit_price() → Optional custom exit price
├── custom_stake_amount() → Optional position sizing
├── custom_stoploss() → Dynamic stoploss
├── confirm_trade_entry() → Final confirmation
└── confirm_trade_exit() → Final exit confirmation
```

### Configuration Structure
```json
{
    "stake_currency": "USDT",
    "stake_amount": "unlimited",
    "tradable_balance_ratio": 0.99,
    "dry_run": true,
    "exchange": {
        "name": "binance",
        "key": "YOUR_API_KEY",
        "secret": "YOUR_SECRET"
    },
    "pairlists": [
        {
            "method": "VolumePairList",
            "number_assets": 20,
            "sort_key": "quoteVolume"
        }
    ],
    "entry_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1
    },
    "exit_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1
    }
}
```

### Hyperopt Search Spaces
```python
from freqtrade.strategy import IntParameter, DecimalParameter, CategoricalParameter

class OptimizedStrategy(IStrategy):
    # Integer parameter
    buy_rsi = IntParameter(15, 45, default=30, space='buy', optimize=True)

    # Decimal parameter
    sell_profit = DecimalParameter(0.01, 0.05, default=0.02, decimals=3, space='sell')

    # Categorical parameter
    buy_trigger = CategoricalParameter(
        ['bb_lower', 'macd_cross', 'rsi_oversold'],
        default='bb_lower', space='buy'
    )

    def populate_entry_trend(self, dataframe, metadata):
        if self.buy_trigger.value == 'bb_lower':
            condition = dataframe['close'] < dataframe['bb_lower']
        elif self.buy_trigger.value == 'macd_cross':
            condition = dataframe['macd'] > dataframe['macdsignal']
        else:
            condition = dataframe['rsi'] < self.buy_rsi.value

        dataframe.loc[condition, 'enter_long'] = 1
        return dataframe
```

## Common Workflows

### Workflow 1: ML-Enhanced Strategy

**Objective**: Integrate machine learning predictions

```python
from freqtrade.strategy import IStrategy
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import talib.abstract as ta

class MLStrategy(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '1h'
    minimal_roi = {"0": 0.1}
    stoploss = -0.05

    # Model paths
    model_path = 'user_data/models/rf_model.pkl'
    scaler_path = 'user_data/models/scaler.pkl'

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.model = None
        self.scaler = None

    def bot_start(self, **kwargs) -> None:
        """Load model at startup"""
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            self.logger.info("ML model loaded successfully")
        except FileNotFoundError:
            self.logger.warning("No model found, training required")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Technical indicators as features
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['sma_ratio'] = dataframe['close'] / ta.SMA(dataframe, timeperiod=20)
        dataframe['bb_width'] = (ta.BBANDS(dataframe)['upperband'] -
                                  ta.BBANDS(dataframe)['lowerband']) / dataframe['close']
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['momentum'] = ta.MOM(dataframe, timeperiod=10)

        # Returns features
        dataframe['return_1h'] = dataframe['close'].pct_change(1)
        dataframe['return_4h'] = dataframe['close'].pct_change(4)
        dataframe['volatility'] = dataframe['return_1h'].rolling(20).std()

        # ML prediction
        if self.model is not None:
            features = ['rsi', 'sma_ratio', 'bb_width', 'atr', 'adx',
                       'momentum', 'return_1h', 'return_4h', 'volatility']
            X = dataframe[features].dropna()

            if len(X) > 0:
                X_scaled = self.scaler.transform(X)
                predictions = self.model.predict_proba(X_scaled)[:, 1]
                dataframe.loc[X.index, 'ml_signal'] = predictions
            else:
                dataframe['ml_signal'] = 0.5
        else:
            dataframe['ml_signal'] = 0.5

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['ml_signal'] > 0.7) &  # High probability
                (dataframe['adx'] > 25) &          # Strong trend
                (dataframe['rsi'] < 70) &          # Not overbought
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['ml_signal'] < 0.3) |  # Low probability
                (dataframe['rsi'] > 80)            # Overbought
            ),
            'exit_long'] = 1
        return dataframe

# Training script (run separately)
def train_model(df, model_path, scaler_path):
    """Train ML model on historical data"""
    features = ['rsi', 'sma_ratio', 'bb_width', 'atr', 'adx',
               'momentum', 'return_1h', 'return_4h', 'volatility']

    # Create target: 1 if price goes up 2% in next 4 hours
    df['target'] = (df['close'].shift(-4) / df['close'] > 1.02).astype(int)

    # Clean data
    df_clean = df[features + ['target']].dropna()
    X = df_clean[features]
    y = df_clean['target']

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_scaled, y)

    # Save
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    return model, scaler
```

**Checklist**:
- [ ] Train model on out-of-sample data
- [ ] Validate model doesn't use future data
- [ ] Test with dry-run before live
- [ ] Monitor model drift
- [ ] Retrain periodically

### Workflow 2: Dynamic Position Sizing

**Objective**: Implement Kelly criterion and risk-based sizing

```python
from freqtrade.strategy import IStrategy
from freqtrade.persistence import Trade
import numpy as np

class DynamicSizingStrategy(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '1h'

    # Base configuration
    minimal_roi = {"0": 0.1}
    stoploss = -0.05

    # Risk parameters
    max_risk_per_trade = 0.02  # 2% of portfolio per trade
    kelly_fraction = 0.25      # Use 25% of Kelly suggestion

    def custom_stake_amount(self, pair: str, current_time,
                           current_rate: float, proposed_stake: float,
                           min_stake: float, max_stake: float,
                           leverage: float, entry_tag: str,
                           side: str, **kwargs) -> float:
        """Dynamic position sizing based on volatility and win rate"""

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return proposed_stake

        # Get ATR for volatility-based sizing
        atr = dataframe['atr'].iloc[-1]
        current_price = dataframe['close'].iloc[-1]
        atr_pct = atr / current_price

        # Calculate Kelly-based size
        win_rate = self.get_win_rate(pair)
        avg_win = self.get_avg_win(pair)
        avg_loss = abs(self.stoploss)

        if avg_loss > 0:
            kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_loss
            kelly = max(0, min(kelly * self.kelly_fraction, 0.5))  # Cap at 50%
        else:
            kelly = 0.1  # Default

        # Risk-based sizing
        portfolio_value = self.wallets.get_total('USDT')
        risk_amount = portfolio_value * self.max_risk_per_trade
        position_size = risk_amount / (atr_pct * 2)  # 2 ATR stop

        # Combine Kelly and risk-based
        final_stake = min(position_size, portfolio_value * kelly)
        final_stake = max(min_stake, min(final_stake, max_stake))

        self.logger.info(f"{pair}: Kelly={kelly:.2%}, ATR={atr_pct:.2%}, Stake={final_stake:.2f}")

        return final_stake

    def get_win_rate(self, pair: str) -> float:
        """Calculate historical win rate for pair"""
        trades = Trade.get_trades_proxy(pair=pair, is_open=False)
        if len(trades) < 10:
            return 0.5  # Default

        wins = sum(1 for t in trades if t.close_profit > 0)
        return wins / len(trades)

    def get_avg_win(self, pair: str) -> float:
        """Calculate average win size"""
        trades = Trade.get_trades_proxy(pair=pair, is_open=False)
        wins = [t.close_profit for t in trades if t.close_profit > 0]
        return np.mean(wins) if wins else 0.02
```

### Workflow 3: Multi-Timeframe Strategy

**Objective**: Combine signals from multiple timeframes

```python
from freqtrade.strategy import IStrategy, merge_informative_pair
import talib.abstract as ta
from pandas import DataFrame

class MultiTimeframeStrategy(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'

    # Additional timeframes
    informative_timeframes = ['15m', '1h', '4h']

    minimal_roi = {"0": 0.05}
    stoploss = -0.03

    def informative_pairs(self):
        """Define additional pairs/timeframes to fetch"""
        pairs = self.dp.current_whitelist()
        informative_pairs = []

        for pair in pairs:
            for tf in self.informative_timeframes:
                informative_pairs.append((pair, tf))

        return informative_pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Main timeframe indicators (5m)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_9'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_21'] = ta.EMA(dataframe, timeperiod=21)

        # Get informative data
        for tf in self.informative_timeframes:
            informative = self.dp.get_pair_dataframe(
                pair=metadata['pair'],
                timeframe=tf
            )

            # Calculate indicators for higher timeframe
            informative[f'rsi_{tf}'] = ta.RSI(informative, timeperiod=14)
            informative[f'sma_20_{tf}'] = ta.SMA(informative, timeperiod=20)
            informative[f'sma_50_{tf}'] = ta.SMA(informative, timeperiod=50)
            informative[f'trend_{tf}'] = (
                informative[f'sma_20_{tf}'] > informative[f'sma_50_{tf}']
            ).astype(int)

            # Merge into main dataframe
            dataframe = merge_informative_pair(
                dataframe, informative, self.timeframe, tf, ffill=True
            )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Entry requires alignment across timeframes"""
        dataframe.loc[
            (
                # 5m: RSI oversold + EMA bullish
                (dataframe['rsi'] < 35) &
                (dataframe['ema_9'] > dataframe['ema_21']) &

                # 15m: Uptrend
                (dataframe['trend_15m'] == 1) &

                # 1h: Uptrend
                (dataframe['trend_1h'] == 1) &

                # 4h: Uptrend
                (dataframe['trend_4h'] == 1) &

                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # 5m exit signal
                (dataframe['rsi'] > 70) |

                # Higher timeframe trend reversal
                (dataframe['trend_1h'] == 0)
            ),
            'exit_long'] = 1

        return dataframe
```

## When to Use vs Alternatives

| Scenario | Best Choice | Rationale |
|----------|-------------|-----------|
| Crypto trading bot | **Freqtrade** | Purpose-built, active community |
| Stock trading | Backtrader | Better stock broker support |
| Research/backtesting only | VectorBT | Much faster |
| Multi-asset portfolio | FinRL | Better for DRL approaches |
| Simple strategies | CCXT + custom | Less overhead |
| Production-grade | **Freqtrade** | Battle-tested, monitoring |

## Common Issues & Solutions

### Issue 1: Insufficient Data for Backtesting
```bash
# Problem: Not enough historical data
# Solution: Download data first

freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT \
    --timeframes 5m 1h --days 365

# For multiple pairs
freqtrade download-data --exchange binance \
    --pairs-file user_data/pairs.json \
    --timeframes 5m 15m 1h 4h 1d --days 730
```

### Issue 2: Strategy Not Trading
```python
# Problem: No trades during backtest
# Solution: Debug entry conditions

def populate_entry_trend(self, dataframe, metadata):
    # Add debug logging
    buy_signals = (
        (dataframe['rsi'] < 30) &
        (dataframe['close'] < dataframe['bb_lower'])
    )
    self.logger.info(f"{metadata['pair']}: Buy signals = {buy_signals.sum()}")

    # Check each condition separately
    self.logger.info(f"RSI < 30: {(dataframe['rsi'] < 30).sum()}")
    self.logger.info(f"Below BB: {(dataframe['close'] < dataframe['bb_lower']).sum()}")

    dataframe.loc[buy_signals, 'enter_long'] = 1
    return dataframe
```

### Issue 3: Hyperopt Not Improving
```bash
# Problem: Hyperopt stuck at local minimum
# Solution: Adjust search space and loss function

# Use different loss functions
freqtrade hyperopt --strategy MyStrategy \
    --hyperopt-loss CalmarHyperOptLoss \
    --epochs 500 \
    --spaces buy sell \
    --random-state 42

# Or multi-objective
freqtrade hyperopt --strategy MyStrategy \
    --hyperopt-loss MaxDrawDownHyperOptLoss \
    --epochs 500
```

### Issue 4: API Rate Limiting
```json
{
    "exchange": {
        "name": "binance",
        "ccxt_config": {
            "enableRateLimit": true,
            "rateLimit": 200
        },
        "ccxt_async_config": {
            "enableRateLimit": true,
            "rateLimit": 200
        }
    }
}
```

## Advanced Topics

### Custom Callbacks and Hooks
```python
from freqtrade.strategy import IStrategy
from freqtrade.persistence import Trade

class CallbackStrategy(IStrategy):
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                           rate: float, time_in_force: str, current_time,
                           entry_tag, side: str, **kwargs) -> bool:
        """Final confirmation before entry"""
        # Check if we already have too many open trades
        open_trades = Trade.get_open_trades()
        if len(open_trades) >= 5:
            return False

        # Check correlation with existing positions
        for trade in open_trades:
            if self.is_correlated(pair, trade.pair):
                return False

        return True

    def confirm_trade_exit(self, pair: str, trade: Trade, order_type: str,
                          amount: float, rate: float, time_in_force: str,
                          exit_reason: str, current_time, **kwargs) -> bool:
        """Final confirmation before exit"""
        # Don't exit if profit is minimal
        if trade.calc_profit_ratio(rate) < 0.005:  # Less than 0.5%
            if exit_reason not in ['force_sell', 'emergency_sell', 'stop_loss']:
                return False

        return True

    def custom_stoploss(self, pair: str, trade: Trade, current_time,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """Dynamic stoploss based on profit"""
        # Trailing stop after 2% profit
        if current_profit > 0.02:
            return max(-0.01, current_profit - 0.02)

        # Tighter stop after 5% profit
        if current_profit > 0.05:
            return max(-0.005, current_profit - 0.01)

        return -0.1  # Default 10% stop
```

### Telegram Integration
```json
{
    "telegram": {
        "enabled": true,
        "token": "YOUR_TELEGRAM_BOT_TOKEN",
        "chat_id": "YOUR_CHAT_ID",
        "notification_settings": {
            "status": "on",
            "buy": "on",
            "sell": "on"
        }
    }
}
```

## Best Practices Checklist

- [ ] Backtest on at least 1 year of data
- [ ] Use hyperopt for parameter optimization
- [ ] Test with dry-run for at least 1 week
- [ ] Set appropriate position sizing
- [ ] Implement proper stoploss
- [ ] Use trailing stops for trend following
- [ ] Download fresh data before backtesting
- [ ] Check exchange-specific requirements
- [ ] Monitor bot via Telegram/API
- [ ] Keep logs for debugging

## Resources

- **Official Docs**: https://www.freqtrade.io/
- **GitHub**: https://github.com/freqtrade/freqtrade
- **Discord**: https://discord.gg/freqtrade
- **Strategy Examples**: https://github.com/freqtrade/freqtrade-strategies

See [references/hyperopt.md](references/hyperopt.md) for optimization guide.
See [references/deployment.md](references/deployment.md) for production setup.
