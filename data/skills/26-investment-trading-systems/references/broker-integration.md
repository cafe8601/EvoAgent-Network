# Broker Integration Guide

다양한 브로커 API와 통합하는 방법에 대한 상세 가이드입니다.

---

## Broker Overview

| 브로커 | 시장 | API 타입 | 수수료 | Paper Trading | 특징 |
|--------|------|---------|--------|---------------|------|
| **Alpaca** | US Stocks | REST/WebSocket | 무료 | ✅ | 초보자 친화적 |
| **Interactive Brokers** | 글로벌 | IB API/TWS | 낮음 | ✅ (Demo) | 전문가급 기능 |
| **NautilusTrader** | 멀티 | Python Native | 플랫폼 무료 | ✅ | 고성능 백테스트 |
| **OKX** | Crypto | REST/WebSocket | 낮음 | ✅ (Testnet) | 파생상품 지원 |

---

## Part 1: Alpaca Integration (US Stocks)

### 1.1 설정 및 인증

```bash
# 설치
pip install alpaca-py

# 환경 변수 설정 (.env)
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
ALPACA_PAPER=true  # Paper Trading 모드
```

```python
import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

class AlpacaTrader:
    def __init__(self, paper: bool = True):
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        
        # Trading Client
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=paper
        )
        
        # Data Client
        self.data_client = StockHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.secret_key
        )
    
    def get_account(self) -> dict:
        """계좌 정보 조회"""
        account = self.trading_client.get_account()
        return {
            "equity": float(account.equity),
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value),
            "pattern_day_trader": account.pattern_day_trader,
            "trading_blocked": account.trading_blocked
        }
    
    def get_positions(self) -> list:
        """보유 포지션 조회"""
        positions = self.trading_client.get_all_positions()
        return [
            {
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "avg_entry_price": float(pos.avg_entry_price),
                "current_price": float(pos.current_price),
                "market_value": float(pos.market_value),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc)
            }
            for pos in positions
        ]
```

### 1.2 주문 실행

```python
class AlpacaOrderManager:
    def __init__(self, trading_client):
        self.client = trading_client
    
    def market_order(self, symbol: str, qty: int, side: str) -> dict:
        """시장가 주문"""
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        
        order = self.client.submit_order(order_data)
        return self._format_order(order)
    
    def limit_order(self, symbol: str, qty: int, side: str, 
                    limit_price: float) -> dict:
        """지정가 주문"""
        order_data = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL,
            time_in_force=TimeInForce.GTC,  # Good Till Cancelled
            limit_price=limit_price
        )
        
        order = self.client.submit_order(order_data)
        return self._format_order(order)
    
    def bracket_order(self, symbol: str, qty: int, side: str,
                      take_profit: float, stop_loss: float) -> dict:
        """브라켓 주문 (진입 + 익절 + 손절)"""
        from alpaca.trading.requests import TakeProfitRequest, StopLossRequest
        
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
            order_class="bracket",
            take_profit=TakeProfitRequest(limit_price=take_profit),
            stop_loss=StopLossRequest(stop_price=stop_loss)
        )
        
        order = self.client.submit_order(order_data)
        return self._format_order(order)
    
    def cancel_order(self, order_id: str) -> bool:
        """주문 취소"""
        try:
            self.client.cancel_order_by_id(order_id)
            return True
        except Exception as e:
            print(f"Cancel failed: {e}")
            return False
    
    def _format_order(self, order) -> dict:
        return {
            "id": str(order.id),
            "symbol": order.symbol,
            "qty": float(order.qty),
            "side": order.side.value,
            "type": order.type.value,
            "status": order.status.value,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None
        }
```

### 1.3 실시간 데이터 스트리밍

```python
from alpaca.data.live import StockDataStream

class AlpacaStreamHandler:
    def __init__(self, api_key: str, secret_key: str):
        self.stream = StockDataStream(api_key, secret_key)
        self.callbacks = {}
    
    async def on_bar(self, bar):
        """봉 데이터 수신 콜백"""
        data = {
            "symbol": bar.symbol,
            "timestamp": bar.timestamp,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume
        }
        
        if "bar" in self.callbacks:
            await self.callbacks["bar"](data)
    
    async def on_trade(self, trade):
        """체결 데이터 수신 콜백"""
        data = {
            "symbol": trade.symbol,
            "price": trade.price,
            "size": trade.size,
            "timestamp": trade.timestamp
        }
        
        if "trade" in self.callbacks:
            await self.callbacks["trade"](data)
    
    def subscribe_bars(self, symbols: list):
        """봉 데이터 구독"""
        self.stream.subscribe_bars(self.on_bar, *symbols)
    
    def subscribe_trades(self, symbols: list):
        """체결 데이터 구독"""
        self.stream.subscribe_trades(self.on_trade, *symbols)
    
    def run(self):
        """스트림 시작"""
        self.stream.run()
```

---

## Part 2: Interactive Brokers (IBKR) Integration

### 2.1 설정

```bash
# 설치
pip install ib_insync

# TWS 또는 IB Gateway 실행 필요
# Paper Trading Port: 7497
# Live Trading Port: 7496
```

```python
from ib_insync import IB, Stock, Forex, Future, Option
from ib_insync import MarketOrder, LimitOrder, StopOrder, StopLimitOrder

class IBKRTrader:
    def __init__(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 1):
        """
        port: 7497 = Paper Trading, 7496 = Live Trading
        """
        self.ib = IB()
        self.host = host
        self.port = port
        self.client_id = client_id
    
    def connect(self):
        """IB 연결"""
        self.ib.connect(self.host, self.port, clientId=self.client_id)
        return self.ib.isConnected()
    
    def disconnect(self):
        """연결 해제"""
        self.ib.disconnect()
    
    def get_account_summary(self) -> dict:
        """계좌 요약"""
        summary = self.ib.accountSummary()
        result = {}
        for item in summary:
            result[item.tag] = {
                "value": item.value,
                "currency": item.currency
            }
        return result
    
    def get_positions(self) -> list:
        """포지션 조회"""
        positions = self.ib.positions()
        return [
            {
                "account": pos.account,
                "contract": pos.contract.symbol,
                "position": pos.position,
                "avg_cost": pos.avgCost
            }
            for pos in positions
        ]
```

### 2.2 다양한 자산 클래스 주문

```python
class IBKRContractFactory:
    @staticmethod
    def stock(symbol: str, exchange: str = "SMART", currency: str = "USD"):
        """주식 계약"""
        return Stock(symbol, exchange, currency)
    
    @staticmethod
    def forex(pair: str):
        """외환 계약 (예: EURUSD, GBPUSD)"""
        return Forex(pair)
    
    @staticmethod
    def future(symbol: str, exchange: str, expiry: str):
        """선물 계약"""
        return Future(symbol, expiry, exchange)
    
    @staticmethod
    def option(symbol: str, expiry: str, strike: float, right: str):
        """옵션 계약 (right: 'C' for Call, 'P' for Put)"""
        return Option(symbol, expiry, strike, right, "SMART")


class IBKROrderManager:
    def __init__(self, ib: IB):
        self.ib = ib
    
    def place_market_order(self, contract, quantity: float, action: str) -> dict:
        """시장가 주문"""
        order = MarketOrder(action, quantity)  # action: 'BUY' or 'SELL'
        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(1)  # 체결 대기
        return self._format_trade(trade)
    
    def place_limit_order(self, contract, quantity: float, action: str, 
                          limit_price: float) -> dict:
        """지정가 주문"""
        order = LimitOrder(action, quantity, limit_price)
        trade = self.ib.placeOrder(contract, order)
        return self._format_trade(trade)
    
    def place_stop_order(self, contract, quantity: float, action: str,
                         stop_price: float) -> dict:
        """손절 주문"""
        order = StopOrder(action, quantity, stop_price)
        trade = self.ib.placeOrder(contract, order)
        return self._format_trade(trade)
    
    def place_bracket_order(self, contract, quantity: float, action: str,
                            entry_price: float, take_profit: float, 
                            stop_loss: float) -> list:
        """브라켓 주문"""
        bracket = self.ib.bracketOrder(
            action, quantity, entry_price, take_profit, stop_loss
        )
        
        trades = []
        for order in bracket:
            trade = self.ib.placeOrder(contract, order)
            trades.append(self._format_trade(trade))
        
        return trades
    
    def _format_trade(self, trade) -> dict:
        return {
            "order_id": trade.order.orderId,
            "contract": trade.contract.symbol,
            "action": trade.order.action,
            "quantity": trade.order.totalQuantity,
            "order_type": trade.order.orderType,
            "status": trade.orderStatus.status,
            "filled": trade.orderStatus.filled,
            "avg_fill_price": trade.orderStatus.avgFillPrice
        }
```

### 2.3 Forex 거래 예시 (EUR/CAD)

```python
class ForexTrader:
    def __init__(self, ib: IB):
        self.ib = ib
        self.order_manager = IBKROrderManager(ib)
    
    def trade_eurcad(self, action: str, units: int, 
                     take_profit: float = None, stop_loss: float = None):
        """EUR/CAD 거래"""
        
        # 계약 생성
        eurcad = Forex("EURCAD")
        self.ib.qualifyContracts(eurcad)
        
        # 현재가 조회
        ticker = self.ib.reqMktData(eurcad)
        self.ib.sleep(2)
        current_price = ticker.marketPrice()
        
        if take_profit and stop_loss:
            # 브라켓 주문
            return self.order_manager.place_bracket_order(
                eurcad, units, action, current_price, take_profit, stop_loss
            )
        else:
            # 시장가 주문
            return self.order_manager.place_market_order(eurcad, units, action)
    
    def get_eurcad_quote(self) -> dict:
        """EUR/CAD 시세 조회"""
        eurcad = Forex("EURCAD")
        self.ib.qualifyContracts(eurcad)
        
        ticker = self.ib.reqMktData(eurcad)
        self.ib.sleep(2)
        
        return {
            "symbol": "EURCAD",
            "bid": ticker.bid,
            "ask": ticker.ask,
            "last": ticker.last,
            "spread": ticker.ask - ticker.bid if ticker.ask and ticker.bid else None
        }
```

---

## Part 3: NautilusTrader Integration

### 3.1 설정

```bash
pip install nautilus_trader
```

### 3.2 전략 구현

```python
from nautilus_trader.config import StrategyConfig
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.model import Position
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.indicators.average.ema import ExponentialMovingAverage


class EMACrossoverConfig(StrategyConfig):
    instrument_id: str
    bar_type: str
    fast_ema_period: int = 10
    slow_ema_period: int = 20
    trade_size: float = 1.0


class EMACrossoverStrategy(Strategy):
    """EMA 크로스오버 전략"""
    
    def __init__(self, config: EMACrossoverConfig):
        super().__init__(config)
        
        # 지표 초기화
        self.fast_ema = ExponentialMovingAverage(config.fast_ema_period)
        self.slow_ema = ExponentialMovingAverage(config.slow_ema_period)
        
        # 설정
        self.instrument_id = InstrumentId.from_str(config.instrument_id)
        self.trade_size = config.trade_size
    
    def on_start(self):
        """전략 시작 시"""
        # 데이터 구독
        self.subscribe_bars(self.bar_type)
        
        # 지표 등록
        self.register_indicator_for_bars(self.bar_type, self.fast_ema)
        self.register_indicator_for_bars(self.bar_type, self.slow_ema)
        
        self.log.info("Strategy started")
    
    def on_bar(self, bar):
        """봉 데이터 수신 시"""
        
        # 지표 준비 확인
        if not self.fast_ema.initialized or not self.slow_ema.initialized:
            return
        
        # 현재 포지션 확인
        position = self.portfolio.net_position(self.instrument_id)
        
        # 신호 생성
        if self.fast_ema.value > self.slow_ema.value:
            # 골든 크로스 → 매수
            if position <= 0:
                self.buy_market()
        
        elif self.fast_ema.value < self.slow_ema.value:
            # 데드 크로스 → 매도
            if position >= 0:
                self.sell_market()
    
    def buy_market(self):
        """시장가 매수"""
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.trade_size,
            time_in_force=TimeInForce.IOC
        )
        self.submit_order(order)
        self.log.info(f"BUY order submitted: {order}")
    
    def sell_market(self):
        """시장가 매도"""
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.SELL,
            quantity=self.trade_size,
            time_in_force=TimeInForce.IOC
        )
        self.submit_order(order)
        self.log.info(f"SELL order submitted: {order}")
    
    def on_order_filled(self, event):
        """주문 체결 시"""
        self.log.info(f"Order filled: {event}")
    
    def on_stop(self):
        """전략 종료 시"""
        self.log.info("Strategy stopped")
```

### 3.3 백테스트 실행

```python
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.identifiers import Venue

def run_backtest():
    # 엔진 설정
    config = BacktestEngineConfig(
        trader_id="BACKTESTER-001",
        log_level="INFO"
    )
    
    engine = BacktestEngine(config=config)
    
    # 거래소 추가
    venue = Venue("BINANCE")
    engine.add_venue(
        venue=venue,
        oms_type="HEDGING",
        account_type="MARGIN",
        base_currency=USD,
        starting_balances=[100_000 * USD]
    )
    
    # 전략 추가
    strategy_config = EMACrossoverConfig(
        instrument_id="BTCUSDT.BINANCE",
        bar_type="BTCUSDT.BINANCE-1-HOUR-LAST-EXTERNAL",
        fast_ema_period=10,
        slow_ema_period=20,
        trade_size=0.01
    )
    
    strategy = EMACrossoverStrategy(config=strategy_config)
    engine.add_strategy(strategy)
    
    # 데이터 로드 및 실행
    engine.run()
    
    # 결과
    return engine.trader.generate_order_fills_report()
```

---

## Part 4: OKX Crypto Integration

### 4.1 설정

```bash
pip install python-okx
```

```python
import okx.Trade as Trade
import okx.Account as Account
import okx.MarketData as MarketData

class OKXTrader:
    def __init__(self, api_key: str, secret_key: str, passphrase: str, 
                 testnet: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.testnet = testnet
        
        flag = "1" if testnet else "0"  # 1: Demo, 0: Live
        
        self.trade_api = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
        self.account_api = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
        self.market_api = MarketData.MarketAPI(flag=flag)
    
    def get_account_balance(self) -> dict:
        """계좌 잔고 조회"""
        result = self.account_api.get_account_balance()
        if result["code"] == "0":
            return result["data"]
        raise Exception(f"API Error: {result['msg']}")
    
    def get_positions(self) -> list:
        """포지션 조회"""
        result = self.account_api.get_positions()
        if result["code"] == "0":
            return result["data"]
        raise Exception(f"API Error: {result['msg']}")
    
    def place_order(self, inst_id: str, td_mode: str, side: str, 
                    sz: str, ord_type: str = "market", 
                    px: str = None) -> dict:
        """
        주문 실행
        
        Args:
            inst_id: 상품 ID (예: "BTC-USDT")
            td_mode: 거래 모드 ("cash", "cross", "isolated")
            side: "buy" or "sell"
            sz: 수량
            ord_type: "market", "limit", "post_only" 등
            px: 지정가 (limit 주문 시)
        """
        result = self.trade_api.place_order(
            instId=inst_id,
            tdMode=td_mode,
            side=side,
            sz=sz,
            ordType=ord_type,
            px=px
        )
        
        if result["code"] == "0":
            return result["data"][0]
        raise Exception(f"Order failed: {result['msg']}")
    
    def get_ticker(self, inst_id: str) -> dict:
        """시세 조회"""
        result = self.market_api.get_ticker(instId=inst_id)
        if result["code"] == "0":
            return result["data"][0]
        raise Exception(f"API Error: {result['msg']}")
```

### 4.2 Perpetual Swap 거래

```python
class OKXPerpetualTrader:
    def __init__(self, okx_trader: OKXTrader):
        self.trader = okx_trader
    
    def open_long(self, symbol: str, size: str, leverage: int = 10) -> dict:
        """롱 포지션 오픈"""
        # 레버리지 설정
        self.trader.account_api.set_leverage(
            lever=str(leverage),
            mgnMode="cross",
            instId=f"{symbol}-USDT-SWAP"
        )
        
        # 롱 주문
        return self.trader.place_order(
            inst_id=f"{symbol}-USDT-SWAP",
            td_mode="cross",
            side="buy",
            sz=size,
            ord_type="market"
        )
    
    def open_short(self, symbol: str, size: str, leverage: int = 10) -> dict:
        """숏 포지션 오픈"""
        self.trader.account_api.set_leverage(
            lever=str(leverage),
            mgnMode="cross",
            instId=f"{symbol}-USDT-SWAP"
        )
        
        return self.trader.place_order(
            inst_id=f"{symbol}-USDT-SWAP",
            td_mode="cross",
            side="sell",
            sz=size,
            ord_type="market"
        )
    
    def close_position(self, symbol: str, side: str, size: str) -> dict:
        """포지션 청산"""
        close_side = "sell" if side == "long" else "buy"
        
        return self.trader.place_order(
            inst_id=f"{symbol}-USDT-SWAP",
            td_mode="cross",
            side=close_side,
            sz=size,
            ord_type="market"
        )
```

---

## Part 5: Unified Broker Interface

### 5.1 Abstract Interface

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class OrderResult:
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: Optional[float]
    status: str
    filled_qty: float
    avg_fill_price: Optional[float]

@dataclass
class Position:
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float

@dataclass
class AccountInfo:
    equity: float
    cash: float
    buying_power: float
    margin_used: float


class BrokerInterface(ABC):
    """통합 브로커 인터페이스"""
    
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def get_account(self) -> AccountInfo:
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        pass
    
    @abstractmethod
    def market_order(self, symbol: str, qty: float, side: str) -> OrderResult:
        pass
    
    @abstractmethod
    def limit_order(self, symbol: str, qty: float, side: str, 
                    price: float) -> OrderResult:
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_quote(self, symbol: str) -> dict:
        pass
```

### 5.2 Implementation Factory

```python
class BrokerFactory:
    @staticmethod
    def create(broker_type: str, config: dict) -> BrokerInterface:
        """브로커 인스턴스 생성"""
        
        if broker_type == "alpaca":
            return AlpacaBrokerAdapter(
                api_key=config["api_key"],
                secret_key=config["secret_key"],
                paper=config.get("paper", True)
            )
        
        elif broker_type == "ibkr":
            return IBKRBrokerAdapter(
                host=config.get("host", "127.0.0.1"),
                port=config.get("port", 7497),
                client_id=config.get("client_id", 1)
            )
        
        elif broker_type == "okx":
            return OKXBrokerAdapter(
                api_key=config["api_key"],
                secret_key=config["secret_key"],
                passphrase=config["passphrase"],
                testnet=config.get("testnet", True)
            )
        
        else:
            raise ValueError(f"Unknown broker type: {broker_type}")


# 사용 예시
config = {
    "api_key": "your_key",
    "secret_key": "your_secret",
    "paper": True
}

broker = BrokerFactory.create("alpaca", config)
broker.connect()

# 계좌 정보
account = broker.get_account()
print(f"Equity: ${account.equity:,.2f}")

# 주문 실행
order = broker.market_order("AAPL", 10, "BUY")
print(f"Order ID: {order.order_id}, Status: {order.status}")
```

---

## Part 6: Telegram Notifications

### 6.1 설정

```python
import os
import requests
from typing import Optional

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """메시지 전송"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def send_trade_alert(self, action: str, symbol: str, qty: int, 
                         price: float, pnl: Optional[float] = None):
        """거래 알림"""
        emoji = "🟢" if action == "BUY" else "🔴"
        
        message = f"""
{emoji} <b>Trade Executed</b>

<b>Action:</b> {action}
<b>Symbol:</b> {symbol}
<b>Quantity:</b> {qty}
<b>Price:</b> ${price:.2f}
"""
        
        if pnl is not None:
            pnl_emoji = "📈" if pnl >= 0 else "📉"
            message += f"\n{pnl_emoji} <b>P&L:</b> ${pnl:+.2f}"
        
        self.send_message(message)
    
    def send_daily_summary(self, summary: dict):
        """일일 요약"""
        message = f"""
📊 <b>Daily Trading Summary</b>

💰 <b>P&L:</b> ${summary['pnl']:+,.2f} ({summary['pnl_pct']:+.2f}%)
📈 <b>Trades:</b> {summary['num_trades']}
✅ <b>Win Rate:</b> {summary['win_rate']:.1%}

<b>Best Trade:</b> {summary['best_trade']['symbol']} (${summary['best_trade']['pnl']:+.2f})
<b>Worst Trade:</b> {summary['worst_trade']['symbol']} (${summary['worst_trade']['pnl']:+.2f})

<b>Portfolio Value:</b> ${summary['portfolio_value']:,.2f}
"""
        self.send_message(message)
    
    def send_kill_switch_alert(self, reason: str):
        """킬 스위치 알림"""
        message = f"""
🚨 <b>KILL SWITCH ACTIVATED</b> 🚨

<b>Reason:</b> {reason}

⚠️ All trading has been stopped
📋 Manual review required
"""
        self.send_message(message)
```

---

## 환경 변수 설정 (.env)

```bash
# === Alpaca ===
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
ALPACA_PAPER=true

# === Interactive Brokers ===
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
IBKR_CLIENT_ID=1

# === OKX ===
OKX_API_KEY=your_okx_api_key
OKX_API_SECRET=your_okx_secret_key
OKX_API_PASSPHRASE=your_passphrase
OKX_TESTNET=true

# === NautilusTrader ===
TARDIS_API_KEY=your_tardis_key

# === Telegram ===
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## 브로커 선택 가이드

| 사용 사례 | 권장 브로커 | 이유 |
|----------|------------|------|
| 초보자 학습 | Alpaca Paper | 무료, 쉬운 API |
| US Stocks 실거래 | Alpaca/IBKR | 낮은 수수료 |
| Forex 거래 | IBKR | 글로벌 커버리지 |
| Crypto Spot | OKX | 다양한 페어 |
| Crypto Futures | OKX | 파생상품 지원 |
| 고성능 백테스트 | NautilusTrader | Rust 기반 성능 |
| 멀티 자산 | IBKR | 모든 자산 클래스 |
