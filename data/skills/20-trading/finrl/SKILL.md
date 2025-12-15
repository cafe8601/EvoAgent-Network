---
name: reinforcement-learning-trading-finrl
description: Expert guidance for deep reinforcement learning in quantitative trading using FinRL framework for AI-powered portfolio management
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, Reinforcement Learning, Deep Learning, Portfolio Optimization, AI Trading, DRL, PPO, A2C, DDPG]
dependencies: [finrl>=0.3.6, stable-baselines3>=2.0.0, gymnasium>=0.28.0, torch>=2.0.0, pandas>=1.4.0]
---

# FinRL: Deep Reinforcement Learning for Trading

## Quick Start

### Installation
```bash
# Basic installation
pip install finrl

# With all extras
pip install "finrl[all]"

# From source (recommended)
git clone https://github.com/AI4Finance-Foundation/FinRL.git
cd FinRL
pip install -e .
```

### Minimal Example
```python
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.agents.stablebaselines3.models import DRLAgent
from finrl.meta.data_processor import DataProcessor
import pandas as pd

# 1. Download and process data
dp = DataProcessor(data_source='yahoofinance')
df = dp.download_data(
    ticker_list=['AAPL', 'MSFT', 'GOOGL'],
    start_date='2020-01-01',
    end_date='2023-01-01',
    time_interval='1D'
)
df = dp.clean_data(df)
df = dp.add_technical_indicator(df, tech_indicator_list=['macd', 'rsi_30', 'cci_30', 'dx_30'])
df = dp.add_vix(df)

# 2. Split data
train = df[(df['date'] >= '2020-01-01') & (df['date'] < '2022-01-01')]
trade = df[(df['date'] >= '2022-01-01') & (df['date'] < '2023-01-01')]

# 3. Create environment
stock_dimension = len(train.tic.unique())
state_space = 1 + 2*stock_dimension + len(['macd', 'rsi_30', 'cci_30', 'dx_30'])*stock_dimension

env_kwargs = {
    "hmax": 100,
    "initial_amount": 1000000,
    "buy_cost_pct": 0.001,
    "sell_cost_pct": 0.001,
    "state_space": state_space,
    "stock_dim": stock_dimension,
    "tech_indicator_list": ['macd', 'rsi_30', 'cci_30', 'dx_30'],
    "action_space": stock_dimension,
    "reward_scaling": 1e-4
}

env_train = StockTradingEnv(df=train, **env_kwargs)

# 4. Train agent
agent = DRLAgent(env=env_train)
model_ppo = agent.get_model("ppo")
trained_ppo = agent.train_model(model=model_ppo, total_timesteps=50000)

# 5. Trade
env_trade = StockTradingEnv(df=trade, **env_kwargs)
df_account_value, df_actions = DRLAgent.DRL_prediction(model=trained_ppo, environment=env_trade)

# 6. Evaluate
from finrl.plot import backtest_stats
print(backtest_stats(df_account_value))
```

## Core Concepts

### FinRL Architecture
```
FinRL Framework:
├── Data Layer
│   ├── DataProcessor (Yahoo, Alpaca, Binance, etc.)
│   ├── FeatureEngineer (technical indicators)
│   └── DataCleaner (missing values, outliers)
├── Environment Layer
│   ├── StockTradingEnv (discrete/continuous actions)
│   ├── PortfolioAllocationEnv (portfolio weights)
│   └── CryptoEnv (cryptocurrency trading)
├── Agent Layer (DRL Algorithms)
│   ├── A2C (Advantage Actor-Critic)
│   ├── PPO (Proximal Policy Optimization)
│   ├── DDPG (Deep Deterministic Policy Gradient)
│   ├── SAC (Soft Actor-Critic)
│   └── TD3 (Twin Delayed DDPG)
└── Evaluation Layer
    ├── Backtesting metrics
    ├── Risk analysis
    └── Visualization
```

### State Space Design
```python
# State composition for trading environment
state = [
    cash_balance,           # 1 dimension
    stock_holdings,         # n stocks
    stock_prices,           # n stocks
    technical_indicators    # n stocks × m indicators
]

# Example: 3 stocks, 4 indicators
# state_space = 1 + 3 + 3 + (3 × 4) = 19

state_space = (
    1 +                               # Cash
    2 * stock_dimension +             # Holdings + Prices
    len(tech_indicators) * stock_dimension  # Technical features
)
```

### Action Space
```python
# Discrete actions: Buy/Sell fixed amounts
action_space = 3 * stock_dimension  # Sell, Hold, Buy for each stock

# Continuous actions: Portfolio weights
action_space = stock_dimension  # Weight allocation [0, 1] per stock

# Continuous with position sizing
# action in [-hmax, hmax] per stock
# Negative = sell, Positive = buy
```

### Reward Functions
```python
# Portfolio value change (default)
reward = (new_portfolio_value - old_portfolio_value) * reward_scaling

# Sharpe ratio-based
reward = (returns - risk_free_rate) / volatility

# Risk-adjusted return
reward = returns - lambda * drawdown

# Custom reward
class CustomTradingEnv(StockTradingEnv):
    def _calculate_reward(self):
        returns = self.portfolio_return()
        max_dd = self.max_drawdown()
        return returns - 0.5 * max_dd  # Penalize drawdown
```

## Common Workflows

### Workflow 1: Multi-Algorithm Ensemble Strategy

**Objective**: Combine multiple DRL agents for robust trading

```python
from finrl.agents.stablebaselines3.models import DRLAgent
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
import numpy as np

class EnsembleDRLAgent:
    def __init__(self, env_train, algorithms=['a2c', 'ppo', 'ddpg']):
        self.algorithms = algorithms
        self.models = {}
        self.env_train = env_train

    def train_all(self, timesteps_dict=None):
        """Train all algorithms"""
        if timesteps_dict is None:
            timesteps_dict = {alg: 50000 for alg in self.algorithms}

        for alg in self.algorithms:
            print(f"Training {alg.upper()}...")
            agent = DRLAgent(env=self.env_train)
            model = agent.get_model(alg)
            self.models[alg] = agent.train_model(
                model=model,
                total_timesteps=timesteps_dict[alg]
            )

        return self.models

    def ensemble_predict(self, env_trade, method='voting'):
        """Ensemble prediction from multiple models"""
        all_actions = {}

        for alg, model in self.models.items():
            _, actions = DRLAgent.DRL_prediction(
                model=model,
                environment=env_trade
            )
            all_actions[alg] = actions['actions'].values

        if method == 'voting':
            # Majority voting for direction
            directions = np.sign(list(all_actions.values()))
            ensemble_actions = np.sign(np.sum(directions, axis=0))

        elif method == 'averaging':
            # Average of all actions
            ensemble_actions = np.mean(list(all_actions.values()), axis=0)

        elif method == 'weighted':
            # Weighted by historical performance
            weights = self.calculate_weights(env_trade)
            ensemble_actions = sum(
                w * all_actions[alg]
                for alg, w in weights.items()
            )

        return ensemble_actions

    def calculate_weights(self, env_val):
        """Calculate weights based on validation performance"""
        sharpe_ratios = {}
        for alg, model in self.models.items():
            account_value, _ = DRLAgent.DRL_prediction(model, env_val)
            returns = account_value['account_value'].pct_change().dropna()
            sharpe = returns.mean() / returns.std() * np.sqrt(252)
            sharpe_ratios[alg] = max(sharpe, 0.01)  # Minimum weight

        total = sum(sharpe_ratios.values())
        return {alg: s/total for alg, s in sharpe_ratios.items()}

# Usage
ensemble = EnsembleDRLAgent(env_train, ['a2c', 'ppo', 'ddpg', 'sac'])
models = ensemble.train_all()
ensemble_actions = ensemble.ensemble_predict(env_trade, method='weighted')
```

**Checklist**:
- [ ] Train each algorithm with appropriate hyperparameters
- [ ] Use validation set for weight calculation
- [ ] Test ensemble on out-of-sample data
- [ ] Compare ensemble vs individual performance
- [ ] Monitor computational resources

### Workflow 2: Feature Engineering for DRL

**Objective**: Create informative state features

```python
from finrl.meta.data_processor import DataProcessor
import pandas as pd
import numpy as np

class AdvancedFeatureEngineer:
    def __init__(self, df):
        self.df = df.copy()

    def add_technical_indicators(self):
        """Add comprehensive technical indicators"""
        import talib

        for tic in self.df['tic'].unique():
            mask = self.df['tic'] == tic
            close = self.df.loc[mask, 'close'].values
            high = self.df.loc[mask, 'high'].values
            low = self.df.loc[mask, 'low'].values
            volume = self.df.loc[mask, 'volume'].values

            # Trend
            self.df.loc[mask, 'sma_20'] = talib.SMA(close, 20)
            self.df.loc[mask, 'ema_20'] = talib.EMA(close, 20)

            # Momentum
            self.df.loc[mask, 'rsi_14'] = talib.RSI(close, 14)
            macd, signal, hist = talib.MACD(close, 12, 26, 9)
            self.df.loc[mask, 'macd'] = macd
            self.df.loc[mask, 'macd_signal'] = signal

            # Volatility
            self.df.loc[mask, 'atr_14'] = talib.ATR(high, low, close, 14)
            upper, middle, lower = talib.BBANDS(close, 20)
            self.df.loc[mask, 'bb_width'] = (upper - lower) / middle

            # Volume
            self.df.loc[mask, 'obv'] = talib.OBV(close, volume)

        return self

    def add_market_indicators(self):
        """Add market-wide indicators (VIX, etc.)"""
        import yfinance as yf

        vix = yf.download('^VIX', start=self.df['date'].min(),
                          end=self.df['date'].max())['Close']
        vix_df = pd.DataFrame({'date': vix.index, 'vix': vix.values})
        self.df = self.df.merge(vix_df, on='date', how='left')

        return self

    def add_sentiment_features(self, sentiment_df=None):
        """Add sentiment scores if available"""
        if sentiment_df is not None:
            self.df = self.df.merge(
                sentiment_df[['date', 'tic', 'sentiment']],
                on=['date', 'tic'],
                how='left'
            )
            self.df['sentiment'].fillna(0, inplace=True)

        return self

    def add_returns_features(self):
        """Add return-based features"""
        for tic in self.df['tic'].unique():
            mask = self.df['tic'] == tic

            # Returns
            self.df.loc[mask, 'return_1d'] = self.df.loc[mask, 'close'].pct_change(1)
            self.df.loc[mask, 'return_5d'] = self.df.loc[mask, 'close'].pct_change(5)
            self.df.loc[mask, 'return_20d'] = self.df.loc[mask, 'close'].pct_change(20)

            # Volatility
            self.df.loc[mask, 'volatility_20d'] = (
                self.df.loc[mask, 'return_1d'].rolling(20).std()
            )

        return self

    def normalize_features(self, feature_cols):
        """Normalize features for DRL training"""
        for col in feature_cols:
            mean = self.df[col].mean()
            std = self.df[col].std()
            self.df[f'{col}_norm'] = (self.df[col] - mean) / (std + 1e-8)

        return self

    def get_dataframe(self):
        """Return processed dataframe"""
        self.df.dropna(inplace=True)
        return self.df

# Usage
df = DataProcessor('yahoofinance').download_data(
    ticker_list=['AAPL', 'MSFT', 'GOOGL'],
    start_date='2018-01-01',
    end_date='2023-01-01'
)

fe = AdvancedFeatureEngineer(df)
df_features = (fe
    .add_technical_indicators()
    .add_market_indicators()
    .add_returns_features()
    .normalize_features(['rsi_14', 'macd', 'bb_width'])
    .get_dataframe())
```

### Workflow 3: Hyperparameter Tuning

**Objective**: Optimize DRL agent hyperparameters

```python
import optuna
from finrl.agents.stablebaselines3.models import DRLAgent
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv

class DRLHyperparameterTuner:
    def __init__(self, env_train, env_val, algorithm='ppo'):
        self.env_train = env_train
        self.env_val = env_val
        self.algorithm = algorithm

    def objective(self, trial):
        """Optuna objective function"""
        # Sample hyperparameters
        if self.algorithm == 'ppo':
            model_kwargs = {
                'n_steps': trial.suggest_int('n_steps', 256, 4096, step=256),
                'learning_rate': trial.suggest_float('lr', 1e-5, 1e-3, log=True),
                'batch_size': trial.suggest_int('batch_size', 32, 512, step=32),
                'n_epochs': trial.suggest_int('n_epochs', 3, 20),
                'gamma': trial.suggest_float('gamma', 0.9, 0.9999),
                'gae_lambda': trial.suggest_float('gae_lambda', 0.9, 0.99),
                'clip_range': trial.suggest_float('clip_range', 0.1, 0.4),
                'ent_coef': trial.suggest_float('ent_coef', 1e-8, 1e-2, log=True),
            }
        elif self.algorithm == 'ddpg':
            model_kwargs = {
                'learning_rate': trial.suggest_float('lr', 1e-5, 1e-3, log=True),
                'buffer_size': trial.suggest_int('buffer_size', 10000, 1000000),
                'batch_size': trial.suggest_int('batch_size', 64, 512, step=64),
                'tau': trial.suggest_float('tau', 0.001, 0.1),
                'gamma': trial.suggest_float('gamma', 0.9, 0.9999),
            }

        # Train model
        agent = DRLAgent(env=self.env_train)
        model = agent.get_model(self.algorithm, model_kwargs=model_kwargs)
        trained_model = agent.train_model(model=model, total_timesteps=20000)

        # Evaluate on validation set
        account_value, _ = DRLAgent.DRL_prediction(
            model=trained_model,
            environment=self.env_val
        )

        # Calculate Sharpe ratio
        returns = account_value['account_value'].pct_change().dropna()
        sharpe = returns.mean() / returns.std() * np.sqrt(252)

        return sharpe

    def optimize(self, n_trials=100):
        """Run hyperparameter optimization"""
        study = optuna.create_study(direction='maximize')
        study.optimize(self.objective, n_trials=n_trials, n_jobs=1)

        print(f"Best Sharpe: {study.best_value:.4f}")
        print(f"Best params: {study.best_params}")

        return study.best_params

# Usage
tuner = DRLHyperparameterTuner(env_train, env_val, algorithm='ppo')
best_params = tuner.optimize(n_trials=50)

# Train final model with best params
agent = DRLAgent(env=env_train)
final_model = agent.get_model('ppo', model_kwargs=best_params)
final_model = agent.train_model(final_model, total_timesteps=100000)
```

## When to Use vs Alternatives

| Scenario | Best Choice | Rationale |
|----------|-------------|-----------|
| End-to-end DRL trading | **FinRL** | Complete framework with data, env, agents |
| Custom RL research | Stable-Baselines3 | More flexibility, better docs |
| Production deployment | Ray RLlib | Better scaling, distributed training |
| Simple strategies | Backtrader/VectorBT | DRL overkill for simple rules |
| Crypto DRL trading | **FinRL** | Built-in crypto data sources |
| Portfolio allocation | **FinRL** | Purpose-built environments |

## Common Issues & Solutions

### Issue 1: Training Instability
```python
# Problem: Reward variance causes unstable training
# Solution: Reward scaling and clipping

env_kwargs = {
    "reward_scaling": 1e-4,  # Scale down large rewards
}

# Or implement reward clipping
class StableRewardEnv(StockTradingEnv):
    def step(self, actions):
        obs, reward, done, truncated, info = super().step(actions)
        reward = np.clip(reward, -1, 1)  # Clip extreme rewards
        return obs, reward, done, truncated, info
```

### Issue 2: Data Leakage
```python
# Problem: Using future information in features
# Solution: Strict train/validation/test split

# Time-series split (NO shuffle)
train = df[df['date'] < '2021-01-01']
val = df[(df['date'] >= '2021-01-01') & (df['date'] < '2022-01-01')]
test = df[df['date'] >= '2022-01-01']

# Indicators calculated BEFORE split
df = dp.add_technical_indicator(df, tech_list)  # On full data

# Then split
train = df[df['date'] < '2021-01-01']
```

### Issue 3: Overfitting to Market Regime
```python
# Problem: Agent overfits to bull/bear market
# Solution: Train on diverse market conditions

# Include multiple market regimes in training
train_periods = [
    ('2015-01-01', '2016-01-01'),  # Normal
    ('2018-01-01', '2019-01-01'),  # Volatility
    ('2020-01-01', '2021-01-01'),  # COVID crash + recovery
]

# Or use data augmentation
def augment_data(df):
    # Add noise to prices
    df_aug = df.copy()
    noise = np.random.normal(0, 0.01, len(df))
    df_aug['close'] = df['close'] * (1 + noise)
    return pd.concat([df, df_aug])
```

### Issue 4: Slow Training
```python
# Problem: Training takes too long
# Solution: Optimize environment and use GPU

# Use vectorized environments
from stable_baselines3.common.vec_env import SubprocVecEnv

def make_env():
    return StockTradingEnv(df=train, **env_kwargs)

env = SubprocVecEnv([make_env for _ in range(4)])  # 4 parallel envs

# Enable GPU
model = PPO('MlpPolicy', env, device='cuda')
```

## Advanced Topics

### Custom Reward Shaping
```python
class ShapedRewardEnv(StockTradingEnv):
    def __init__(self, *args, risk_aversion=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.risk_aversion = risk_aversion

    def _calculate_reward(self):
        # Base return
        returns = (self.portfolio_value - self.prev_portfolio_value) / self.prev_portfolio_value

        # Drawdown penalty
        if self.portfolio_value < self.peak_value:
            drawdown = (self.peak_value - self.portfolio_value) / self.peak_value
            returns -= self.risk_aversion * drawdown

        # Holding penalty (encourage trading)
        holding_penalty = 0.0001 * np.sum(self.state[1:self.stock_dim+1] > 0)

        return returns - holding_penalty
```

### Multi-Objective RL
```python
from stable_baselines3 import PPO
import torch

class MultiObjectivePPO(PPO):
    def __init__(self, *args, return_weight=0.5, risk_weight=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.return_weight = return_weight
        self.risk_weight = risk_weight

    def _get_reward(self, obs, action, env):
        # Return component
        return_reward = env.get_return()

        # Risk component (negative of volatility)
        risk_reward = -env.get_volatility()

        return self.return_weight * return_reward + self.risk_weight * risk_reward
```

## Best Practices Checklist

- [ ] Use proper train/validation/test time splits
- [ ] Scale rewards appropriately (1e-4 to 1e-3)
- [ ] Include transaction costs in simulation
- [ ] Train on diverse market conditions
- [ ] Validate hyperparameters on validation set
- [ ] Use ensemble methods for robustness
- [ ] Monitor for overfitting (train vs test gap)
- [ ] Include market indicators (VIX, etc.)
- [ ] Normalize state features
- [ ] Test with realistic constraints (position limits)

## Resources

- **Official Docs**: https://finrl.readthedocs.io/
- **GitHub**: https://github.com/AI4Finance-Foundation/FinRL
- **Tutorials**: https://github.com/AI4Finance-Foundation/FinRL-Tutorials
- **Paper**: "FinRL: Deep Reinforcement Learning Framework for Automated Stock Trading"

See [references/algorithms.md](references/algorithms.md) for DRL algorithm details.
See [references/environments.md](references/environments.md) for custom environments.
