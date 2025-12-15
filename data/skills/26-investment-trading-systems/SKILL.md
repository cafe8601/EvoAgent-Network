---
name: investment-trading-systems
description: Comprehensive investment and trading skill covering multiple trading styles (day trading, swing trading, position trading, algorithmic trading), asset classes (stocks, forex, crypto, commodities), and strategies (technical analysis, statistical arbitrage, autonomous trading). Integrates full trading lifecycle from market analysis → strategy development → risk management → execution → performance monitoring.
version: 1.0.0
author: AI Research Skills
license: MIT
tags: [Investment, Trading, Algorithmic-Trading, Risk-Management, Portfolio-Management, Technical-Analysis, Statistical-Arbitrage, Forex, Stocks, Crypto]
dependencies: [yfinance, pandas, numpy, alpaca-py, ib_insync, ta-lib, statsmodels, crewai]
---

# Investment & Trading Systems v1.0

**모든 자산 클래스와 트레이딩 스타일을 위한 포괄적 투자 시스템 스킬**

---

## 핵심 철학: Risk-First, Data-Driven, Systematic

| 원칙 | 설명 | 적용 방법 |
|------|------|----------|
| **💰 리스크 우선** | 수익보다 자본 보존 우선 | 포지션당 1-2% 리스크, 일일 손실 제한 |
| **📊 데이터 기반** | 감정 배제, 통계적 판단 | 백테스트 필수, 최소 2년 데이터 |
| **🔄 체계적 접근** | 규칙 기반 진입/청산 | 트레이딩 플랜 문서화, 일관된 실행 |

---

## 📋 Trading Lifecycle Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        TRADING LIFECYCLE                                      │
│                                                                              │
│  1. MARKET ANALYSIS        2. STRATEGY DEVELOPMENT      3. RISK MANAGEMENT  │
│  ├─ Technical Indicators   ├─ Trading Plan              ├─ Position Sizing   │
│  ├─ Chart Patterns         ├─ Entry/Exit Rules          ├─ Stop-Loss Rules   │
│  ├─ Multi-Timeframe        ├─ Backtesting               ├─ Portfolio Limits  │
│  └─ Fundamental Data       └─ Optimization              └─ Drawdown Limits   │
│           ↓                         ↓                           ↓            │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                    4. TRADE EXECUTION                                  │   │
│  │    Manual Trading → Semi-Automated → Fully Autonomous                  │   │
│  │    [Alpaca Paper] → [IBKR Demo] → [Live Trading]                       │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│           ↓                                                                  │
│  5. PERFORMANCE MONITORING      6. CONTINUOUS IMPROVEMENT                    │
│  ├─ P&L Tracking                ├─ Trade Journal Review                     │
│  ├─ Risk Metrics (Sharpe)       ├─ Strategy Refinement                      │
│  └─ Benchmark Comparison        └─ Psychological Discipline                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Trading Styles Matrix

| 스타일 | 보유 기간 | 하루 거래 수 | 시간 요구 | 적합 대상 |
|--------|----------|-------------|----------|-----------|
| **Day Trading** | 1일 이내 | 5-20회 | Full-time | 전업 트레이더, 빠른 판단력 |
| **Swing Trading** | 2-10일 | 2-5회/주 | Part-time | 직장인, 중기 트렌드 추종 |
| **Position Trading** | 주~월 | 1-4회/월 | Low | 장기 투자자, 펀더멘털 분석 |
| **Algorithmic** | 자동 | 자동 | Setup only | 개발자, 시스템 트레이더 |

---

## 📊 Asset Classes & Strategies

### 1. Stocks (주식)

#### 기술적 분석 (Technical Analysis)
```python
# 핵심 지표 조합
indicators = {
    "RSI": {"period": 14, "overbought": 70, "oversold": 30},
    "MACD": {"fast": 12, "slow": 26, "signal": 9},
    "Bollinger_Bands": {"period": 20, "std_dev": 2},
    "Moving_Averages": {"SMA_20": 20, "SMA_50": 50, "SMA_200": 200}
}

# 매수 신호 조건
buy_signal = (
    RSI < 30 and                    # 과매도
    MACD_histogram > 0 and          # MACD 상승
    price > SMA_50                  # 중기 상승 트렌드
)

# 매도 신호 조건
sell_signal = (
    RSI > 70 and                    # 과매수
    MACD_histogram < 0 and          # MACD 하락
    price < SMA_50                  # 중기 하락 트렌드
)
```

#### 통계적 차익거래 (Pair Trading)
```python
# 페어 선정 기준
pair_criteria = {
    "min_correlation": 0.70,        # 최소 상관관계
    "cointegration_pvalue": 0.05,   # 공적분 p-value < 0.05
    "half_life_days": 60,           # 평균 회귀 반감기 < 60일
    "sector": "same"                # 동일 섹터 우선
}

# Z-Score 기반 진입/청산
entry_zscore = 2.0    # |Z| > 2.0 진입
exit_zscore = 0.0     # Z → 0 청산
stop_zscore = 3.0     # |Z| > 3.0 손절
```

### 2. Forex (외환)

#### EUR/CAD 전략 예시 (70-80% 승률)
```python
# Mean Reversion Strategy
class ForexMeanReversion:
    def __init__(self):
        self.pair = "EURCAD"
        self.timeframe = "15min"
        self.win_rate = 0.72  # 백테스트 결과
    
    def entry_signal(self, df):
        # 볼린저 밴드 + RSI 조합
        upper, middle, lower = self.bollinger_bands(df, period=20)
        rsi = self.calculate_rsi(df, period=14)
        
        # 매수: 하단 밴드 + RSI 과매도
        buy = (df['close'] <= lower) & (rsi < 30)
        # 매도: 상단 밴드 + RSI 과매수
        sell = (df['close'] >= upper) & (rsi > 70)
        
        return buy, sell

# Oil Correlation Strategy
class OilCorrelationStrategy:
    """CAD는 원유 가격과 상관관계 → 유가 급변 시 EUR/CAD 역방향 거래"""
    
    def entry_signal(self, oil_change_pct, eurcad_data):
        if abs(oil_change_pct) > 2:  # 유가 2% 이상 변동
            if oil_change_pct > 0:
                return "SELL_EURCAD"  # 유가 상승 → CAD 강세 → EUR/CAD 하락
            else:
                return "BUY_EURCAD"   # 유가 하락 → CAD 약세 → EUR/CAD 상승
```

### 3. Crypto (암호화폐)

#### NautilusTrader 활용
```python
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.model import OrderSide, TimeInForce

class CryptoMomentumStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.bar_type = config.bar_type
        self.fast_ema = None
        self.slow_ema = None
    
    def on_start(self):
        self.subscribe_bars(self.bar_type)
        self.register_indicator_for_bars(self.bar_type, self.fast_ema)
        self.register_indicator_for_bars(self.bar_type, self.slow_ema)
    
    def on_bar(self, bar):
        if self.fast_ema.value > self.slow_ema.value:
            self.buy_market()
        elif self.fast_ema.value < self.slow_ema.value:
            self.sell_market()
```

---

## 💼 Portfolio Management

### Asset Allocation by Risk Profile

| 프로필 | 주식 | 채권 | 현금 | 대안투자 | 특징 |
|--------|------|------|------|----------|------|
| **Conservative** | 30% | 50% | 15% | 5% | 자본 보존, 인컴 중심 |
| **Moderate** | 50% | 35% | 10% | 5% | 균형 성장 + 인컴 |
| **Growth** | 70% | 20% | 5% | 5% | 장기 성장 중심 |
| **Aggressive** | 85% | 5% | 5% | 5% | 최대 성장, 고위험 감수 |

### Diversification Rules

```python
DIVERSIFICATION_RULES = {
    "max_single_position": 0.15,      # 단일 포지션 최대 15%
    "max_sector_weight": 0.30,        # 단일 섹터 최대 30%
    "min_positions": 10,              # 최소 10개 종목
    "max_correlation": 0.80,          # 상관관계 0.8 이상 경고
    "min_cash_reserve": 0.10,         # 최소 현금 10%
}

def check_diversification(portfolio):
    """포트폴리오 분산도 검사"""
    violations = []
    
    # HHI 집중도 지수
    hhi = sum((pos_weight ** 2) for pos_weight in portfolio.weights)
    if hhi > 0.15:  # HHI > 0.15는 집중 위험
        violations.append(f"HHI concentration: {hhi:.2f}")
    
    return violations
```

---

## ⚠️ Risk Management Framework

### Position Sizing (포지션 사이징)

```python
def calculate_position_size(
    account_balance: float,
    risk_per_trade: float,  # 1-2% 권장
    entry_price: float,
    stop_loss_price: float
) -> int:
    """
    리스크 기반 포지션 사이징
    
    예시:
    - 계좌: $50,000
    - 리스크: 1% = $500
    - 진입: $100, 손절: $98 (리스크 $2/주)
    - 포지션: $500 / $2 = 250주
    """
    risk_amount = account_balance * risk_per_trade
    risk_per_share = abs(entry_price - stop_loss_price)
    shares = int(risk_amount / risk_per_share)
    
    return shares
```

### 3-Way Risk Debate (TradingAgents 패턴)

```python
class RiskEvaluator:
    """보수/공격/중립 3자 토론 기반 리스크 평가"""
    
    def evaluate_trade(self, trade_proposal):
        # 1. Conservative View
        conservative = self.conservative_debator.assess(trade_proposal)
        # → 손실 가능성, 낮은 포지션 사이즈 권장
        
        # 2. Aggressive View
        aggressive = self.aggressive_debator.assess(trade_proposal)
        # → 기회비용, 더 큰 포지션 권장
        
        # 3. Neutral View
        neutral = self.neutral_debator.assess(trade_proposal)
        # → 데이터 기반 중립적 분석
        
        # Final Decision
        return self.risk_manager.decide(conservative, aggressive, neutral)
```

### Hard Limits (절대 규칙)

```python
HARD_LIMITS = {
    "max_daily_loss_pct": 0.05,       # 일일 최대 손실 5%
    "max_drawdown_pct": 0.15,         # 최대 낙폭 15%
    "max_position_pct": 0.20,         # 단일 포지션 최대 20%
    "max_daily_trades": 20,           # 일일 최대 거래 횟수
    "min_risk_reward": 2.0,           # 최소 손익비 2:1
    "always_use_stop_loss": True,     # 항상 손절 설정
}

def check_hard_limits_before_trade(trade, portfolio):
    if portfolio.daily_loss > HARD_LIMITS["max_daily_loss_pct"]:
        return {"approved": False, "reason": "Daily loss limit exceeded"}
    
    if not trade.stop_loss:
        return {"approved": False, "reason": "Stop loss required"}
    
    # ... 기타 검사
    
    return {"approved": True}
```

---

## 🤖 Autonomous Trading System

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   AUTONOMOUS TRADING LOOP                        │
│                                                                  │
│  9:00 AM: Pre-Market Screening (NASDAQ 100)                     │
│     ↓                                                            │
│  9:30 AM: Market Open → Multi-Model Analysis (5 AI models)       │
│     ↓                                                            │
│  Consensus (>70%) → Risk Check → Execute Trade (Alpaca Paper)   │
│     ↓                                                            │
│  Real-time Telegram Notifications                                │
│     ↓                                                            │
│  4:00 PM: Daily P&L Summary, Model Leaderboard                  │
└─────────────────────────────────────────────────────────────────┘
```

### Stock Screening Criteria

```python
SCREENING_CRITERIA = {
    "min_volume": 1_000_000,          # 최소 일 거래량 100만주
    "min_price_change_pct": 2.0,      # 최소 가격 변동 2%
    "max_positions": 10,              # 최대 분석 대상 10개
    "has_news_catalyst": True,        # 뉴스 이벤트 우선
}

def calculate_opportunity_score(stock_data):
    """기회 점수 계산"""
    return (
        abs(stock_data["price_change_pct"]) * 0.4 +
        (stock_data["volume"] / 10_000_000) * 0.3 +
        (10 if stock_data["has_news"] else 0) * 0.3
    )
```

### Multi-Model Consensus

```python
async def run_multi_model_analysis(ticker: str) -> dict:
    """5개 AI 모델 병렬 분석"""
    
    results = await asyncio.gather(
        claude_agent.analyze(ticker),
        gpt4_agent.analyze(ticker),
        gemini_agent.analyze(ticker),
        deepseek_agent.analyze(ticker),
        qwen_agent.analyze(ticker),
    )
    
    # 합의 계산
    decisions = [r["decision"] for r in results]  # BUY, SELL, HOLD
    consensus_level = max(decisions.count(d)/len(decisions) for d in set(decisions))
    majority_decision = max(set(decisions), key=decisions.count)
    
    return {
        "ticker": ticker,
        "majority_decision": majority_decision,
        "consensus_level": consensus_level,
        "high_consensus": consensus_level >= 0.70
    }
```

---

## 📈 Performance Monitoring

### Key Metrics

| 지표 | 설명 | 목표 |
|------|------|------|
| **Sharpe Ratio** | 위험 조정 수익률 | > 1.5 |
| **Max Drawdown** | 최대 낙폭 | < 15% |
| **Win Rate** | 승률 | > 55% |
| **Profit Factor** | 총이익/총손실 | > 1.5 |
| **Alpha** | 벤치마크 초과 수익 | > 3% |
| **Expectancy** | 거래당 기대 수익 | > $50 |

### Trade Journal Template

```markdown
## Trade Record

**Date**: 2025-12-08
**Symbol**: NVDA
**Strategy**: Momentum Breakout
**Market Condition**: Bullish

### Entry
- Price: $145.50
- Shares: 100
- Stop Loss: $142.00 (2.4% risk)
- Target: $155.00 (6.5% reward)
- R:R Ratio: 2.7:1

### Exit
- Price: $153.20
- Reason: Trailing stop triggered
- P&L: +$770 (+5.3%)

### Review
- **Executed Plan?** Yes
- **Emotional State**: Calm, followed rules
- **Lesson**: Good entry timing, could have held longer
- **Grade**: A-
```

---

## 🔧 Integration: Brokers & Tools

### Alpaca (Paper Trading)

```python
from alpaca.trading.client import TradingClient

# Paper Trading (포트 설정)
client = TradingClient(
    api_key=os.getenv("ALPACA_API_KEY"),
    secret_key=os.getenv("ALPACA_SECRET_KEY"),
    paper=True  # 페이퍼 트레이딩
)

# 주문 실행
order = client.submit_order(
    symbol="AAPL",
    qty=10,
    side="buy",
    type="market",
    time_in_force="day"
)
```

### Interactive Brokers (IBKR)

```python
from ib_insync import IB, Forex, MarketOrder

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Paper: 7497, Live: 7496

# EUR/CAD 거래
eurcad = Forex('EURCAD')
ib.qualifyContracts(eurcad)

# 주문
order = MarketOrder('BUY', 20000)
trade = ib.placeOrder(eurcad, order)
```

### NautilusTrader (High-Performance)

```python
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.adapters.binance import BinanceDataClientConfig

config = TradingNodeConfig(
    data_clients={
        "BINANCE": BinanceDataClientConfig(
            api_key="YOUR_KEY",
            api_secret="YOUR_SECRET",
            testnet=True
        )
    }
)
```

---

## 🚫 Common Mistakes to Avoid

| ❌ 실수 | 💡 해결책 |
|--------|----------|
| 손절 없이 거래 | **항상** 손절 설정 (예외 없음) |
| 과도한 레버리지 | 1-2% 리스크 규칙 엄수 |
| 복수 거래 (Revenge Trading) | 일일 손실 제한 도달 시 거래 중지 |
| 손절선 이동 | 절대 손절을 불리하게 이동하지 않음 |
| 평균 매수 (Averaging Down) | 손실 포지션에 추가 매수 금지 |
| 계획 없는 거래 | 트레이딩 플랜 문서화 필수 |
| 백테스트 없는 전략 | 최소 2년 데이터로 검증 |
| 실거래 전 충분한 테스트 부재 | 페이퍼 트레이딩 1개월 필수 |

---

## 🚀 Quick Start: Build a Bot Now

사용자가 "트레이딩 봇을 만들어줘"라고 요청하면, 아래 워크플로우를 따르세요:

1. **템플릿 로드**: `references/complete-system-example.md`의 `main_bot.py` 구조를 기본으로 사용합니다.
2. **전략 선택**: `references/trading-strategies.md`에서 사용자의 성향에 맞는 전략(예: MACD, RSI)을 선택하여 `strategies/` 모듈로 구현합니다.
3. **브로커 연결**: `references/broker-integration.md`를 참조하여 Alpaca/IBKR 중 하나를 선택하고 연결 코드를 작성합니다.
4. **리스크 설정**: `references/risk-management-framework.md`의 `RiskManager` 클래스를 통합하여 안전장치를 마련합니다.

**명령어 예시:**
> "User wants a BTC momentum bot."
> -> *Agent Action*: Load `complete-system-example.md`, replace `Strategy` class with `MomentumStrategy` from `trading-strategies.md`, and configure for Crypto context.

---

## 📚 Quick Start Checklist

### Beginner (초보자)
- [ ] 리스크: 거래당 0.5%
- [ ] 스타일: 스윙 트레이딩
- [ ] 일일 손실 제한: -1.5%
- [ ] 최소 손익비: 3:1
- [ ] 페이퍼 트레이딩: 3개월

### Experienced (경험자)
- [ ] 리스크: 거래당 1-2%
- [ ] 스타일: 자유 선택
- [ ] 일일 손실 제한: -3%
- [ ] 최소 손익비: 2:1
- [ ] 자동화 시스템 구축

---

## 📎 Resource References

### 핵심 참조 파일

| 파일 | 설명 |
|------|------|
| `references/complete-system-example.md` | **[NEW]** 통합 실행 가능한 봇(`main.py`) 전체 소스코드 |
| `references/trading-strategies.md` | 전략별 상세 구현 가이드 |
| `references/risk-management-framework.md` | 리스크 관리 프레임워크 |
| `references/broker-integration.md` | 브로커 연동 가이드 |
| `references/backtesting-guide.md` | 백테스트 방법론 |

### 관련 스킬

- `stock-analyzer` - 기술적 분석 지표
- `pair-trade-screener` - 통계적 차익거래
- `portfolio-manager` - 포트폴리오 관리
- `market-analysis` - 시장 분석
- `risk-assessment` - 리스크 평가
- `autonomous-trading` - 자율 트레이딩

---

## ⚠️ Disclaimer

**이 스킬은 교육 및 정보 제공 목적입니다. 투자 조언이 아닙니다.**

- 트레이딩은 상당한 자본 손실 위험이 있습니다
- 과거 성과는 미래 수익을 보장하지 않습니다
- 실거래 전 반드시 페이퍼 트레이딩으로 검증하세요
- 감당할 수 있는 자금만으로 거래하세요
- 필요시 전문 금융 상담사와 상담하세요

---

**Version:** 1.0.0
**Dependencies:** yfinance, alpaca-py, ib_insync, nautilus_trader, pandas, numpy, ta-lib, statsmodels
**Complexity:** Advanced
**Output:** 체계적인 투자/트레이딩 시스템 구축
