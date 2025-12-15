---
name: crypto-exchange-integration-ccxt
description: Expert guidance for cryptocurrency exchange API integration using CCXT unified library for trading bots and market data access
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, Cryptocurrency, Exchange API, Market Data, Order Execution, Python, JavaScript, Unified API]
dependencies: [ccxt>=4.0.0, pandas>=1.4.0, aiohttp>=3.8.0]
---

# CCXT: Unified Cryptocurrency Exchange Library

## Quick Start

### Installation
```bash
# Python
pip install ccxt

# With async support
pip install ccxt aiohttp

# Node.js
npm install ccxt
```

### Connect to Exchange
```python
import ccxt

# Public API (no authentication)
exchange = ccxt.binance()

# Private API (with authentication)
exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',  # 'spot', 'future', 'margin'
    }
})

# Testnet/Sandbox
exchange = ccxt.binance({
    'apiKey': 'YOUR_TESTNET_KEY',
    'secret': 'YOUR_TESTNET_SECRET',
    'enableRateLimit': True,
    'sandbox': True,
})
```

### Fetch Market Data
```python
# Get all markets
markets = exchange.load_markets()

# Get ticker
ticker = exchange.fetch_ticker('BTC/USDT')
print(f"BTC Price: ${ticker['last']:,.2f}")

# Get OHLCV candles
ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)
# Returns: [[timestamp, open, high, low, close, volume], ...]

# Get order book
orderbook = exchange.fetch_order_book('BTC/USDT', limit=10)
print(f"Best Bid: {orderbook['bids'][0][0]}")
print(f"Best Ask: {orderbook['asks'][0][0]}")
```

## Core Concepts

### Unified API Structure
```
CCXT Unified Methods:
├── Market Data (Public)
│   ├── fetch_markets(): Available trading pairs
│   ├── fetch_ticker(): Price, volume, 24h change
│   ├── fetch_order_book(): Bid/ask depth
│   ├── fetch_ohlcv(): Candlestick data
│   └── fetch_trades(): Recent trades
├── Account (Private)
│   ├── fetch_balance(): Account balances
│   ├── fetch_open_orders(): Pending orders
│   ├── fetch_closed_orders(): Completed orders
│   └── fetch_my_trades(): Trade history
└── Trading (Private)
    ├── create_order(): Place order
    ├── cancel_order(): Cancel order
    └── edit_order(): Modify order
```

### Market Symbol Format
```python
# Standard format: BASE/QUOTE
spot = 'BTC/USDT'           # Spot market
future = 'BTC/USDT:USDT'    # Linear perpetual (USDT-margined)
inverse = 'BTC/USD:BTC'     # Inverse perpetual (coin-margined)
dated = 'BTC/USD:BTC-231229'  # Futures with expiry

# Check market type
market = exchange.market('BTC/USDT')
print(market['type'])    # 'spot', 'swap', 'future'
print(market['linear'])  # True for linear, False for inverse
```

### Order Types and Parameters
```python
# Market order
order = exchange.create_order(
    symbol='BTC/USDT',
    type='market',
    side='buy',
    amount=0.001
)

# Limit order
order = exchange.create_order(
    symbol='BTC/USDT',
    type='limit',
    side='buy',
    amount=0.001,
    price=40000
)

# Stop-loss order
order = exchange.create_order(
    symbol='BTC/USDT',
    type='stop_market',
    side='sell',
    amount=0.001,
    params={
        'stopPrice': 39000
    }
)

# Take-profit limit
order = exchange.create_order(
    symbol='BTC/USDT',
    type='take_profit_limit',
    side='sell',
    amount=0.001,
    price=42000,
    params={
        'stopPrice': 41900
    }
)
```

## Common Workflows

### Workflow 1: Multi-Exchange Arbitrage Scanner

**Objective**: Monitor price differences across exchanges

```python
import ccxt
import asyncio

async def create_exchange(exchange_id, config=None):
    exchange_class = getattr(ccxt.async_support, exchange_id)
    exchange = exchange_class(config or {'enableRateLimit': True})
    await exchange.load_markets()
    return exchange

async def fetch_ticker_safe(exchange, symbol):
    try:
        if symbol in exchange.markets:
            ticker = await exchange.fetch_ticker(symbol)
            return exchange.id, ticker['last'], ticker['bid'], ticker['ask']
    except Exception as e:
        return exchange.id, None, None, None
    return exchange.id, None, None, None

async def scan_arbitrage(symbols, exchanges):
    """Scan for arbitrage opportunities across exchanges"""
    opportunities = []

    for symbol in symbols:
        tasks = [fetch_ticker_safe(ex, symbol) for ex in exchanges]
        results = await asyncio.gather(*tasks)

        # Filter valid results
        valid = [(r[0], r[1], r[2], r[3]) for r in results if r[1] is not None]

        if len(valid) >= 2:
            # Find best bid (sell) and best ask (buy)
            best_bid = max(valid, key=lambda x: x[2] or 0)
            best_ask = min(valid, key=lambda x: x[3] or float('inf'))

            if best_bid[2] and best_ask[3]:
                spread_pct = (best_bid[2] - best_ask[3]) / best_ask[3] * 100

                if spread_pct > 0.1:  # Minimum 0.1% profit threshold
                    opportunities.append({
                        'symbol': symbol,
                        'buy_exchange': best_ask[0],
                        'buy_price': best_ask[3],
                        'sell_exchange': best_bid[0],
                        'sell_price': best_bid[2],
                        'spread_pct': spread_pct
                    })

    return opportunities

async def main():
    exchanges = [
        await create_exchange('binance'),
        await create_exchange('kraken'),
        await create_exchange('coinbasepro'),
    ]

    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']

    try:
        opportunities = await scan_arbitrage(symbols, exchanges)
        for opp in sorted(opportunities, key=lambda x: x['spread_pct'], reverse=True):
            print(f"{opp['symbol']}: Buy {opp['buy_exchange']} @ {opp['buy_price']:.2f}, "
                  f"Sell {opp['sell_exchange']} @ {opp['sell_price']:.2f} = {opp['spread_pct']:.2f}%")
    finally:
        await asyncio.gather(*[ex.close() for ex in exchanges])

asyncio.run(main())
```

**Checklist**:
- [ ] Enable rate limiting on all exchanges
- [ ] Handle network errors gracefully
- [ ] Consider trading fees in profit calculation
- [ ] Account for withdrawal fees and times
- [ ] Close exchange connections properly

### Workflow 2: Automated Trading Bot Framework

**Objective**: Build a production-ready trading bot

```python
import ccxt
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TradingBot')

@dataclass
class TradeSignal:
    symbol: str
    side: str  # 'buy' or 'sell'
    amount: float
    price: Optional[float] = None
    order_type: str = 'market'

class TradingBot:
    def __init__(self, exchange_id: str, api_key: str, secret: str,
                 sandbox: bool = True):
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'sandbox': sandbox,
        })
        self.exchange.load_markets()
        self.orders = []
        self.positions = {}

    def get_balance(self, currency: str = 'USDT') -> float:
        balance = self.exchange.fetch_balance()
        return balance['free'].get(currency, 0)

    def calculate_position_size(self, symbol: str, risk_pct: float = 0.02) -> float:
        """Calculate position size based on risk percentage"""
        balance = self.get_balance()
        ticker = self.exchange.fetch_ticker(symbol)
        price = ticker['last']

        # Risk-based position sizing
        risk_amount = balance * risk_pct
        position_value = risk_amount / 0.02  # Assuming 2% stop loss
        amount = position_value / price

        # Round to market precision
        market = self.exchange.market(symbol)
        amount = self.exchange.amount_to_precision(symbol, amount)
        return float(amount)

    def execute_signal(self, signal: TradeSignal) -> dict:
        """Execute a trade signal"""
        try:
            logger.info(f"Executing {signal.side} {signal.amount} {signal.symbol}")

            if signal.order_type == 'market':
                order = self.exchange.create_market_order(
                    symbol=signal.symbol,
                    side=signal.side,
                    amount=signal.amount
                )
            else:
                order = self.exchange.create_limit_order(
                    symbol=signal.symbol,
                    side=signal.side,
                    amount=signal.amount,
                    price=signal.price
                )

            self.orders.append(order)
            logger.info(f"Order executed: {order['id']} - Status: {order['status']}")
            return order

        except ccxt.InsufficientFunds as e:
            logger.error(f"Insufficient funds: {e}")
            raise
        except ccxt.InvalidOrder as e:
            logger.error(f"Invalid order: {e}")
            raise
        except ccxt.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise

    def set_stop_loss(self, symbol: str, side: str, amount: float,
                      stop_price: float) -> dict:
        """Set stop-loss order"""
        opposite_side = 'sell' if side == 'buy' else 'buy'
        return self.exchange.create_order(
            symbol=symbol,
            type='stop_market',
            side=opposite_side,
            amount=amount,
            params={'stopPrice': stop_price}
        )

    def get_open_positions(self) -> list:
        """Get current open positions (for futures)"""
        if self.exchange.has['fetchPositions']:
            return self.exchange.fetch_positions()
        return []

# Usage
bot = TradingBot('binance', 'api_key', 'secret', sandbox=True)
signal = TradeSignal(symbol='BTC/USDT', side='buy', amount=0.001)
order = bot.execute_signal(signal)
```

### Workflow 3: Historical Data Collection

**Objective**: Collect and store OHLCV data for backtesting

```python
import ccxt
import pandas as pd
from datetime import datetime, timedelta
import time

class OHLCVCollector:
    def __init__(self, exchange_id: str):
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({'enableRateLimit': True})
        self.exchange.load_markets()

    def fetch_all_ohlcv(self, symbol: str, timeframe: str,
                        since: datetime, until: datetime = None) -> pd.DataFrame:
        """Fetch complete OHLCV history with pagination"""
        if until is None:
            until = datetime.now()

        since_ts = int(since.timestamp() * 1000)
        until_ts = int(until.timestamp() * 1000)

        all_candles = []
        current_since = since_ts

        # Calculate milliseconds per candle
        timeframe_ms = self.exchange.parse_timeframe(timeframe) * 1000

        while current_since < until_ts:
            try:
                candles = self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=current_since,
                    limit=1000
                )

                if not candles:
                    break

                all_candles.extend(candles)
                current_since = candles[-1][0] + timeframe_ms

                # Progress logging
                progress = (current_since - since_ts) / (until_ts - since_ts) * 100
                print(f"Progress: {progress:.1f}% - Fetched {len(all_candles)} candles")

                # Rate limiting handled by ccxt
                time.sleep(self.exchange.rateLimit / 1000)

            except ccxt.NetworkError as e:
                print(f"Network error, retrying: {e}")
                time.sleep(5)
            except ccxt.ExchangeError as e:
                print(f"Exchange error: {e}")
                break

        # Convert to DataFrame
        df = pd.DataFrame(
            all_candles,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df[~df.index.duplicated(keep='first')]

        return df

    def save_to_csv(self, df: pd.DataFrame, filename: str):
        df.to_csv(filename)
        print(f"Saved {len(df)} candles to {filename}")

# Usage
collector = OHLCVCollector('binance')
df = collector.fetch_all_ohlcv(
    symbol='BTC/USDT',
    timeframe='1h',
    since=datetime(2023, 1, 1),
    until=datetime(2024, 1, 1)
)
collector.save_to_csv(df, 'btc_usdt_1h_2023.csv')
```

## When to Use vs Alternatives

| Scenario | Best Choice | Rationale |
|----------|-------------|-----------|
| Multi-exchange trading | **CCXT** | Unified API across 100+ exchanges |
| Single exchange bot | Exchange SDK | Native SDK may have more features |
| CEX + DEX integration | CCXT + Web3 | CCXT for CEX, Web3.py for DEX |
| Historical data only | CCXT or Tardis | Tardis.dev for institutional-grade data |
| HFT/low latency | FIX Protocol | CCXT adds latency overhead |
| Crypto market research | **CCXT** | Easy data access across exchanges |

## Common Issues & Solutions

### Issue 1: Rate Limiting Errors
```python
# Problem: Too many requests
# Solution: Enable rate limiting and add delays

exchange = ccxt.binance({
    'enableRateLimit': True,  # Required
    'rateLimit': 1200,        # Custom limit (ms)
})

# For batch operations
for symbol in symbols:
    ticker = exchange.fetch_ticker(symbol)
    time.sleep(exchange.rateLimit / 1000)  # Explicit delay
```

### Issue 2: Authentication Failures
```python
# Problem: Invalid signature/timestamp
# Solution: Sync time and check credentials

# Enable time sync
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret,
    'options': {
        'adjustForTimeDifference': True,  # Auto-sync time
    }
})

# Or manually sync
exchange.load_time_difference()
```

### Issue 3: Order Precision Errors
```python
# Problem: Amount/price precision rejected
# Solution: Use exchange precision methods

market = exchange.market('BTC/USDT')

# Correct precision
amount = exchange.amount_to_precision('BTC/USDT', 0.00123456789)
price = exchange.price_to_precision('BTC/USDT', 42000.123456)

# Check minimum order size
min_amount = market['limits']['amount']['min']
min_cost = market['limits']['cost']['min']
```

### Issue 4: Async Connection Management
```python
# Problem: Connection leaks in async
# Solution: Proper cleanup with context manager

import ccxt.async_support as ccxt_async
import asyncio

async def main():
    exchange = ccxt_async.binance({'enableRateLimit': True})
    try:
        markets = await exchange.load_markets()
        ticker = await exchange.fetch_ticker('BTC/USDT')
    finally:
        await exchange.close()  # Always close!

asyncio.run(main())
```

## Advanced Topics

### WebSocket Streams (Real-time Data)
```python
# Many exchanges support WebSocket via CCXT Pro (paid)
# Alternative: Use exchange-specific WebSocket

from binance import ThreadedWebsocketManager

twm = ThreadedWebsocketManager(api_key='key', api_secret='secret')
twm.start()

def handle_socket_message(msg):
    print(f"Price: {msg['p']}")

twm.start_symbol_ticker_socket(callback=handle_socket_message, symbol='BTCUSDT')
```

### Exchange-Specific Parameters
```python
# Binance futures: set leverage
exchange.set_leverage(10, 'BTC/USDT')

# Binance futures: set margin mode
exchange.set_margin_mode('isolated', 'BTC/USDT')

# Bybit: position mode
exchange.set_position_mode(hedged=True, symbol='BTC/USDT')

# Kraken: add order flags
order = exchange.create_order(
    'BTC/USD', 'limit', 'buy', 0.01, 40000,
    params={'oflags': 'post'}  # Post-only order
)
```

## Best Practices Checklist

- [ ] Always enable `enableRateLimit: True`
- [ ] Use sandbox/testnet for development
- [ ] Store API keys in environment variables
- [ ] Implement proper error handling for all API calls
- [ ] Use `amount_to_precision` and `price_to_precision`
- [ ] Close async connections properly
- [ ] Check `exchange.has` before using methods
- [ ] Log all trades for debugging
- [ ] Implement retry logic for network errors
- [ ] Monitor account balance before orders

## Resources

- **Official Docs**: https://docs.ccxt.com/
- **GitHub**: https://github.com/ccxt/ccxt
- **Exchange Support**: https://github.com/ccxt/ccxt/wiki/Exchanges
- **CCXT Pro (WebSocket)**: https://ccxt.pro/

See [references/exchanges.md](references/exchanges.md) for exchange-specific guides.
See [references/async.md](references/async.md) for async patterns.
