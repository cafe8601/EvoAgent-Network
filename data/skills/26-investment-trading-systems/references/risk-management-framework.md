# Risk Management Framework

트레이딩의 가장 중요한 요소인 리스크 관리에 대한 종합 가이드입니다.

---

## 핵심 원칙: "생존이 수익보다 우선"

> 💡 **Rule #1**: Never lose more than you can afford
> 
> 💡 **Rule #2**: Never forget Rule #1

---

## Part 1: Position Sizing (포지션 사이징)

### 1.1 Fixed Percentage Risk Model (고정 비율 리스크)

**가장 권장되는 방법**: 거래당 계좌의 1-2%만 리스크

```python
class FixedPercentageRisk:
    def __init__(self, risk_per_trade: float = 0.01):
        """
        risk_per_trade: 0.01 = 1%, 0.02 = 2%
        """
        self.risk_per_trade = risk_per_trade
    
    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float
    ) -> dict:
        """
        예시:
        - 계좌: $100,000
        - 리스크: 1% = $1,000
        - 진입: $50, 손절: $48
        - 주당 리스크: $2
        - 포지션: 500주
        """
        risk_amount = account_balance * self.risk_per_trade
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            raise ValueError("Stop loss cannot be at entry price")
        
        shares = int(risk_amount / risk_per_share)
        position_value = shares * entry_price
        position_pct = position_value / account_balance
        
        return {
            "shares": shares,
            "risk_amount": risk_amount,
            "risk_per_share": risk_per_share,
            "position_value": position_value,
            "position_pct": position_pct,
            "max_loss": shares * risk_per_share
        }
```

**예시 계산**:

| 항목 | 값 |
|------|-----|
| 계좌 잔고 | $50,000 |
| 리스크 비율 | 1% |
| 최대 리스크 금액 | $500 |
| 진입가 | $100 |
| 손절가 | $97 |
| 주당 리스크 | $3 |
| **포지션 크기** | **166주** |
| 포지션 가치 | $16,600 (33%) |

### 1.2 Kelly Criterion (켈리 기준)

**수학적으로 최적의 베팅 크기** - 단, 풀 켈리는 너무 공격적

```python
class KellyCriterion:
    def calculate_kelly(
        self,
        win_rate: float,      # 승률 (0.55 = 55%)
        avg_win: float,       # 평균 이익
        avg_loss: float       # 평균 손실 (양수로 입력)
    ) -> dict:
        """
        Kelly % = (Win Rate × Avg Win - Loss Rate × Avg Loss) / Avg Win
        
        예시:
        - 승률: 55%
        - 평균 이익: $200
        - 평균 손실: $100
        - Kelly = (0.55 × 200 - 0.45 × 100) / 200 = 32.5%
        """
        loss_rate = 1 - win_rate
        kelly_full = (win_rate * avg_win - loss_rate * avg_loss) / avg_win
        
        # 안전한 분수 켈리
        kelly_half = kelly_full * 0.50
        kelly_quarter = kelly_full * 0.25
        
        return {
            "kelly_full": kelly_full,
            "kelly_half": kelly_half,        # 권장
            "kelly_quarter": kelly_quarter,  # 보수적
            "recommendation": "Use quarter or half Kelly for safety"
        }
```

**켈리 사용 지침**:
- ⚠️ 풀 켈리는 사용하지 마세요 (너무 공격적)
- ✅ 1/4 켈리 권장 (Quarter Kelly)
- ✅ 최대 1/2 켈리까지만 (Half Kelly)

### 1.3 Volatility-Adjusted Sizing (변동성 조정)

```python
class VolatilityAdjustedSizing:
    def __init__(self, atr_multiplier: float = 2.0, target_risk_pct: float = 0.01):
        self.atr_multiplier = atr_multiplier
        self.target_risk_pct = target_risk_pct
    
    def calculate_position(
        self,
        account_balance: float,
        entry_price: float,
        atr: float  # Average True Range
    ) -> dict:
        """
        ATR 기반 동적 포지션 사이징
        - ATR이 높으면 → 포지션 줄임
        - ATR이 낮으면 → 포지션 늘림
        """
        # ATR 기반 손절 거리
        stop_distance = atr * self.atr_multiplier
        stop_loss = entry_price - stop_distance
        
        # 리스크 금액
        risk_amount = account_balance * self.target_risk_pct
        
        # 포지션 계산
        shares = int(risk_amount / stop_distance)
        
        return {
            "shares": shares,
            "stop_loss": stop_loss,
            "stop_distance": stop_distance,
            "atr": atr,
            "risk_amount": risk_amount
        }
```

---

## Part 2: Stop Loss Strategies (손절 전략)

### 2.1 Stop Loss Types

```python
class StopLossTypes:
    
    @staticmethod
    def fixed_percentage(entry_price: float, pct: float = 0.02) -> float:
        """고정 비율 손절 (예: 진입가의 2%)"""
        return entry_price * (1 - pct)
    
    @staticmethod
    def atr_based(entry_price: float, atr: float, multiplier: float = 2.0) -> float:
        """ATR 기반 동적 손절"""
        return entry_price - (atr * multiplier)
    
    @staticmethod
    def support_level(support_price: float, buffer_pct: float = 0.005) -> float:
        """지지선 아래 손절"""
        return support_price * (1 - buffer_pct)
    
    @staticmethod
    def swing_low(recent_low: float, buffer_pct: float = 0.01) -> float:
        """최근 저점 아래 손절"""
        return recent_low * (1 - buffer_pct)
```

### 2.2 Trailing Stop Implementation

```python
class TrailingStopManager:
    def __init__(self, initial_stop: float, trail_method: str = "percentage"):
        self.initial_stop = initial_stop
        self.current_stop = initial_stop
        self.highest_price = None
        self.trail_method = trail_method
    
    def update(self, current_price: float, atr: float = None) -> dict:
        """가격 업데이트 시 호출"""
        
        # 최고가 갱신
        if self.highest_price is None or current_price > self.highest_price:
            self.highest_price = current_price
        
        # 트레일링 손절 계산
        if self.trail_method == "percentage":
            new_stop = self.highest_price * 0.97  # 3% 트레일
        elif self.trail_method == "atr":
            new_stop = self.highest_price - (atr * 2.0)  # 2 ATR 트레일
        elif self.trail_method == "chandelier":
            new_stop = self.highest_price - (atr * 3.0)  # 3 ATR (Chandelier Exit)
        else:
            new_stop = self.current_stop
        
        # 손절은 상향만 가능 (절대 하향 금지!)
        if new_stop > self.current_stop:
            self.current_stop = new_stop
        
        # 손절 도달 확인
        triggered = current_price <= self.current_stop
        
        return {
            "current_stop": self.current_stop,
            "highest_price": self.highest_price,
            "current_price": current_price,
            "triggered": triggered,
            "profit_locked": (self.current_stop - self.initial_stop) if self.current_stop > self.initial_stop else 0
        }
```

### 2.3 Break-Even Stop

```python
class BreakEvenStop:
    def __init__(self, entry_price: float, trigger_profit_pct: float = 0.02):
        """
        일정 수익 도달 시 손절을 본전으로 이동
        예: 2% 수익 시 → 손절을 진입가로 이동
        """
        self.entry_price = entry_price
        self.trigger_price = entry_price * (1 + trigger_profit_pct)
        self.break_even_set = False
    
    def check_and_update(self, current_price: float, current_stop: float) -> float:
        """손절 업데이트 확인"""
        
        if not self.break_even_set and current_price >= self.trigger_price:
            # 트리거 도달 → 손절을 본전으로
            self.break_even_set = True
            return self.entry_price + 0.01  # 약간의 이익 확보
        
        return current_stop
```

---

## Part 3: Portfolio Risk Limits

### 3.1 Hard Limits Configuration

```python
PORTFOLIO_LIMITS = {
    # === 포지션 관련 ===
    "max_single_position_pct": 0.20,      # 단일 포지션 최대 20%
    "max_correlated_exposure_pct": 0.40,  # 상관 자산 최대 40%
    "max_sector_pct": 0.30,               # 단일 섹터 최대 30%
    
    # === 손실 관련 ===
    "max_daily_loss_pct": 0.03,           # 일일 최대 손실 3%
    "max_weekly_loss_pct": 0.05,          # 주간 최대 손실 5%
    "max_drawdown_pct": 0.15,             # 최대 낙폭 15%
    
    # === 거래 관련 ===
    "max_daily_trades": 10,               # 일일 최대 거래 횟수
    "max_open_positions": 15,             # 최대 오픈 포지션 수
    "min_risk_reward_ratio": 2.0,         # 최소 손익비
    
    # === 현금 관련 ===
    "min_cash_reserve_pct": 0.10,         # 최소 현금 보유 10%
    "max_margin_usage_pct": 0.50,         # 마진 최대 사용 50%
}

class PortfolioRiskChecker:
    def __init__(self, limits: dict = PORTFOLIO_LIMITS):
        self.limits = limits
    
    def check_new_trade(self, portfolio: dict, new_trade: dict) -> dict:
        """신규 거래 전 리스크 체크"""
        violations = []
        warnings = []
        
        # 1. 단일 포지션 한도
        new_position_pct = new_trade["value"] / portfolio["total_value"]
        if new_position_pct > self.limits["max_single_position_pct"]:
            violations.append(f"Position size {new_position_pct:.1%} exceeds {self.limits['max_single_position_pct']:.1%}")
        
        # 2. 일일 손실 한도
        if portfolio["daily_pnl_pct"] < -self.limits["max_daily_loss_pct"]:
            violations.append("Daily loss limit exceeded - STOP TRADING")
        
        # 3. 최대 낙폭
        if portfolio["current_drawdown"] > self.limits["max_drawdown_pct"]:
            violations.append("Maximum drawdown exceeded - REDUCE EXPOSURE")
        
        # 4. 현금 보유량
        cash_after = portfolio["cash"] - new_trade["value"]
        cash_pct_after = cash_after / portfolio["total_value"]
        if cash_pct_after < self.limits["min_cash_reserve_pct"]:
            warnings.append(f"Cash will drop to {cash_pct_after:.1%}")
        
        # 5. 오픈 포지션 수
        if len(portfolio["positions"]) >= self.limits["max_open_positions"]:
            violations.append("Maximum open positions reached")
        
        return {
            "approved": len(violations) == 0,
            "violations": violations,
            "warnings": warnings
        }
```

### 3.2 Concentration Risk Monitoring

```python
class ConcentrationMonitor:
    def analyze_concentration(self, portfolio: dict) -> dict:
        """포트폴리오 집중도 분석"""
        
        positions = portfolio["positions"]
        total_value = portfolio["total_value"]
        
        # 개별 포지션 가중치
        weights = {
            ticker: pos["value"] / total_value 
            for ticker, pos in positions.items()
        }
        
        # HHI (Herfindahl-Hirschman Index)
        hhi = sum(w ** 2 for w in weights.values())
        
        # 상위 집중도
        sorted_weights = sorted(weights.values(), reverse=True)
        top_3_weight = sum(sorted_weights[:3]) if len(sorted_weights) >= 3 else sum(sorted_weights)
        top_5_weight = sum(sorted_weights[:5]) if len(sorted_weights) >= 5 else sum(sorted_weights)
        
        # 집중도 등급
        if hhi < 0.10:
            concentration_grade = "Well Diversified"
        elif hhi < 0.18:
            concentration_grade = "Moderately Concentrated"
        elif hhi < 0.25:
            concentration_grade = "Concentrated"
        else:
            concentration_grade = "Highly Concentrated - REDUCE"
        
        return {
            "hhi": hhi,
            "top_3_weight": top_3_weight,
            "top_5_weight": top_5_weight,
            "num_positions": len(positions),
            "concentration_grade": concentration_grade,
            "largest_position": max(weights.items(), key=lambda x: x[1]) if weights else None
        }
```

---

## Part 4: Drawdown Management

### 4.1 Drawdown Calculator

```python
class DrawdownCalculator:
    def __init__(self):
        self.peak_equity = None
        self.trough_equity = None
        self.peak_date = None
        self.trough_date = None
    
    def update(self, equity: float, date) -> dict:
        """자본 업데이트 시 낙폭 계산"""
        
        # 최고점 갱신
        if self.peak_equity is None or equity > self.peak_equity:
            self.peak_equity = equity
            self.peak_date = date
            self.trough_equity = equity
            self.trough_date = date
        
        # 최저점 갱신 (현재 낙폭 구간 내)
        if equity < self.trough_equity:
            self.trough_equity = equity
            self.trough_date = date
        
        # 현재 낙폭
        current_drawdown = (self.peak_equity - equity) / self.peak_equity
        max_drawdown = (self.peak_equity - self.trough_equity) / self.peak_equity
        
        return {
            "current_equity": equity,
            "peak_equity": self.peak_equity,
            "trough_equity": self.trough_equity,
            "current_drawdown": current_drawdown,
            "max_drawdown": max_drawdown,
            "drawdown_duration_days": (date - self.peak_date).days if date != self.peak_date else 0
        }
    
    def get_recovery_progress(self, current_equity: float) -> float:
        """회복 진행률 (0% = 저점, 100% = 고점 회복)"""
        if self.peak_equity == self.trough_equity:
            return 100.0
        
        recovery = (current_equity - self.trough_equity) / (self.peak_equity - self.trough_equity)
        return min(max(recovery * 100, 0), 100)
```

### 4.2 Drawdown Response Protocol

```python
DRAWDOWN_RESPONSE_PROTOCOL = {
    "level_1": {
        "threshold": 0.05,  # 5% 낙폭
        "action": "Reduce position sizes by 25%",
        "alert": "Warning: Drawdown reaching 5%"
    },
    "level_2": {
        "threshold": 0.10,  # 10% 낙폭
        "action": "Reduce position sizes by 50%, No new positions",
        "alert": "Caution: Significant drawdown at 10%"
    },
    "level_3": {
        "threshold": 0.15,  # 15% 낙폭
        "action": "Close 50% of positions, Review strategy",
        "alert": "Critical: Major drawdown at 15%"
    },
    "level_4": {
        "threshold": 0.20,  # 20% 낙폭
        "action": "STOP TRADING, Close all positions, Full review required",
        "alert": "EMERGENCY: Maximum drawdown exceeded"
    }
}

class DrawdownResponseManager:
    def __init__(self, protocol: dict = DRAWDOWN_RESPONSE_PROTOCOL):
        self.protocol = protocol
    
    def get_response(self, current_drawdown: float) -> dict:
        """현재 낙폭에 따른 대응 조치"""
        
        response = {
            "level": 0,
            "action": "Continue normal trading",
            "position_size_multiplier": 1.0,
            "new_positions_allowed": True
        }
        
        for level, config in self.protocol.items():
            if current_drawdown >= config["threshold"]:
                if level == "level_1":
                    response.update({
                        "level": 1, "position_size_multiplier": 0.75,
                        "action": config["action"], "alert": config["alert"]
                    })
                elif level == "level_2":
                    response.update({
                        "level": 2, "position_size_multiplier": 0.50,
                        "new_positions_allowed": False,
                        "action": config["action"], "alert": config["alert"]
                    })
                elif level == "level_3":
                    response.update({
                        "level": 3, "position_size_multiplier": 0.25,
                        "new_positions_allowed": False, "close_existing": 0.50,
                        "action": config["action"], "alert": config["alert"]
                    })
                elif level == "level_4":
                    response.update({
                        "level": 4, "position_size_multiplier": 0,
                        "new_positions_allowed": False, "stop_trading": True,
                        "action": config["action"], "alert": config["alert"]
                    })
        
        return response
```

---

## Part 5: Risk/Reward Analysis

### 5.1 Risk/Reward Calculator

```python
class RiskRewardCalculator:
    def calculate(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        direction: str = "long"
    ) -> dict:
        """손익비 계산"""
        
        if direction == "long":
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
        else:
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
        
        if risk <= 0:
            raise ValueError("Risk must be positive (stop loss below entry for long)")
        
        rr_ratio = reward / risk
        
        # 필요 승률 계산 (손익분기점)
        breakeven_winrate = 1 / (1 + rr_ratio)
        
        return {
            "risk_per_share": risk,
            "reward_per_share": reward,
            "risk_reward_ratio": rr_ratio,
            "breakeven_winrate": breakeven_winrate,
            "recommendation": "Good" if rr_ratio >= 2.0 else ("Marginal" if rr_ratio >= 1.5 else "Poor")
        }
    
    def calculate_expectancy(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> dict:
        """기대값 계산"""
        
        loss_rate = 1 - win_rate
        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        expectancy_per_dollar = expectancy / avg_loss
        
        return {
            "expectancy": expectancy,
            "expectancy_per_dollar_risked": expectancy_per_dollar,
            "profitable": expectancy > 0,
            "edge_strength": "Strong" if expectancy_per_dollar > 0.5 else ("Moderate" if expectancy_per_dollar > 0.2 else "Weak")
        }
```

### 5.2 Required Win Rate Table

| R:R Ratio | 필요 승률 | 해석 |
|-----------|----------|------|
| 1:1 | 50% | 손익분기 (거래 비용 제외) |
| 1.5:1 | 40% | 괜찮음 |
| 2:1 | 33% | 좋음 (권장) |
| 3:1 | 25% | 우수 |
| 4:1 | 20% | 탁월 |
| 5:1 | 17% | 최상 |

---

## Part 6: 3-Way Risk Debate System

### 6.1 TradingAgents Pattern Implementation

```python
class ConservativeDebator:
    """보수적 관점: 리스크 최소화, 자본 보존"""
    
    def assess(self, trade_proposal: dict, portfolio: dict, market_data: dict) -> dict:
        concerns = []
        risk_score = 0
        
        # 포지션 크기 우려
        position_pct = trade_proposal["value"] / portfolio["total_value"]
        if position_pct > 0.10:
            concerns.append(f"Position size {position_pct:.1%} is too large")
            risk_score += 20
        
        # 변동성 우려
        if market_data["volatility_level"] == "High":
            concerns.append("High market volatility increases risk")
            risk_score += 25
        
        # 집중도 우려
        if portfolio["concentration"]["hhi"] > 0.15:
            concerns.append("Portfolio already concentrated")
            risk_score += 15
        
        # 낙폭 우려
        if portfolio["current_drawdown"] > 0.05:
            concerns.append("Currently in drawdown - avoid adding risk")
            risk_score += 30
        
        return {
            "perspective": "conservative",
            "recommendation": "REDUCE" if risk_score > 40 else "PROCEED_CAUTIOUSLY",
            "concerns": concerns,
            "risk_score": risk_score,
            "suggested_size_multiplier": 0.5 if risk_score > 30 else 0.75
        }


class AggressiveDebator:
    """공격적 관점: 기회 추구, 성장 중심"""
    
    def assess(self, trade_proposal: dict, portfolio: dict, market_data: dict) -> dict:
        opportunities = []
        opportunity_score = 0
        
        # 현금 활용
        cash_pct = portfolio["cash"] / portfolio["total_value"]
        if cash_pct > 0.30:
            opportunities.append(f"Excess cash {cash_pct:.1%} - opportunity cost")
            opportunity_score += 20
        
        # 강한 신호
        if trade_proposal.get("signal_strength") == "strong":
            opportunities.append("Strong buy signal - capitalize on opportunity")
            opportunity_score += 25
        
        # 추세 정렬
        if market_data.get("trend_aligned"):
            opportunities.append("Trade aligned with market trend")
            opportunity_score += 15
        
        # 낮은 분산
        if portfolio["num_positions"] < 5:
            opportunities.append("Portfolio under-diversified - add positions")
            opportunity_score += 10
        
        return {
            "perspective": "aggressive",
            "recommendation": "INCREASE" if opportunity_score > 40 else "PROCEED",
            "opportunities": opportunities,
            "opportunity_score": opportunity_score,
            "suggested_size_multiplier": 1.5 if opportunity_score > 40 else 1.25
        }


class NeutralDebator:
    """중립적 관점: 데이터 기반, 균형 잡힌 분석"""
    
    def assess(self, trade_proposal: dict, portfolio: dict, market_data: dict) -> dict:
        analysis = []
        
        # 포지션 사이징 계산
        optimal_size = self._calculate_optimal_size(trade_proposal, portfolio, market_data)
        
        # R:R 분석
        rr_ratio = trade_proposal.get("risk_reward_ratio", 0)
        if rr_ratio >= 2.0:
            analysis.append(f"R:R ratio {rr_ratio:.1f} meets minimum threshold")
        else:
            analysis.append(f"R:R ratio {rr_ratio:.1f} below 2:1 minimum")
        
        # 시장 환경 분석
        market_assessment = self._assess_market_conditions(market_data)
        analysis.append(market_assessment)
        
        return {
            "perspective": "neutral",
            "recommendation": "OPTIMAL_SIZE",
            "analysis": analysis,
            "suggested_shares": optimal_size["shares"],
            "suggested_size_multiplier": 1.0,
            "reasoning": "Balanced approach based on quantitative analysis"
        }
    
    def _calculate_optimal_size(self, trade, portfolio, market):
        # ATR 기반 최적 사이즈
        atr = market.get("atr", trade["entry_price"] * 0.02)
        risk_amount = portfolio["total_value"] * 0.01
        stop_distance = atr * 2
        shares = int(risk_amount / stop_distance)
        return {"shares": shares, "value": shares * trade["entry_price"]}
    
    def _assess_market_conditions(self, market_data):
        vol = market_data.get("volatility_level", "Medium")
        trend = market_data.get("trend", "Neutral")
        return f"Market: {trend} trend, {vol} volatility"


class RiskManager:
    """최종 결정권자: 3가지 관점을 종합하여 결정"""
    
    def __init__(self):
        self.conservative = ConservativeDebator()
        self.aggressive = AggressiveDebator()
        self.neutral = NeutralDebator()
    
    def evaluate_trade(self, trade_proposal: dict, portfolio: dict, market_data: dict) -> dict:
        # 3자 토론
        c_view = self.conservative.assess(trade_proposal, portfolio, market_data)
        a_view = self.aggressive.assess(trade_proposal, portfolio, market_data)
        n_view = self.neutral.assess(trade_proposal, portfolio, market_data)
        
        # 리스크 점수 기반 가중 평균
        risk_weight = c_view["risk_score"] / 100
        opp_weight = a_view["opportunity_score"] / 100
        
        # 기본은 중립 관점
        final_multiplier = n_view["suggested_size_multiplier"]
        
        # 리스크가 높으면 보수적 관점 가중
        if risk_weight > 0.5:
            final_multiplier = min(final_multiplier, c_view["suggested_size_multiplier"])
        
        # 기회가 높으면 공격적 관점 반영 (단, 리스크 제한 내에서)
        if opp_weight > 0.5 and risk_weight < 0.3:
            final_multiplier = max(final_multiplier, min(a_view["suggested_size_multiplier"], 1.25))
        
        # 최종 결정
        final_shares = int(n_view["suggested_shares"] * final_multiplier)
        
        approved = (
            c_view["risk_score"] < 60 and
            final_shares > 0 and
            trade_proposal.get("risk_reward_ratio", 0) >= 1.5
        )
        
        return {
            "approved": approved,
            "final_shares": final_shares if approved else 0,
            "final_multiplier": final_multiplier,
            "debate_summary": {
                "conservative": c_view,
                "aggressive": a_view,
                "neutral": n_view
            },
            "reasoning": self._generate_reasoning(c_view, a_view, n_view, approved)
        }
    
    def _generate_reasoning(self, c, a, n, approved):
        if not approved:
            return f"Rejected: {', '.join(c['concerns'])}"
        
        return f"Approved with {n['suggested_shares']} shares. " \
               f"Risks: {len(c['concerns'])} concerns. " \
               f"Opportunities: {len(a['opportunities'])} identified."
```

---

## Part 7: Emergency Protocols

### 7.1 Kill Switch Implementation

```python
class TradingKillSwitch:
    def __init__(self, config: dict):
        self.max_daily_loss = config.get("max_daily_loss_pct", 0.05)
        self.max_drawdown = config.get("max_drawdown_pct", 0.20)
        self.max_consecutive_losses = config.get("max_consecutive_losses", 5)
        self.is_active = True
    
    def check_kill_conditions(self, portfolio: dict, trade_history: list) -> dict:
        """킬 스위치 조건 확인"""
        
        kill_reasons = []
        
        # 1. 일일 손실 한도
        if abs(portfolio["daily_pnl_pct"]) > self.max_daily_loss:
            kill_reasons.append(f"Daily loss {portfolio['daily_pnl_pct']:.1%} exceeded limit")
        
        # 2. 최대 낙폭
        if portfolio["current_drawdown"] > self.max_drawdown:
            kill_reasons.append(f"Drawdown {portfolio['current_drawdown']:.1%} exceeded limit")
        
        # 3. 연속 손실
        consecutive_losses = self._count_consecutive_losses(trade_history)
        if consecutive_losses >= self.max_consecutive_losses:
            kill_reasons.append(f"{consecutive_losses} consecutive losses")
        
        if kill_reasons:
            self.is_active = False
            return {
                "kill_switch_triggered": True,
                "reasons": kill_reasons,
                "action": "STOP ALL TRADING IMMEDIATELY",
                "next_steps": [
                    "1. Close all open positions",
                    "2. Review all recent trades",
                    "3. Identify systemic issues",
                    "4. Take minimum 24h break",
                    "5. Restart with 50% position sizing"
                ]
            }
        
        return {"kill_switch_triggered": False, "is_active": True}
    
    def _count_consecutive_losses(self, trade_history: list) -> int:
        count = 0
        for trade in reversed(trade_history):
            if trade["pnl"] < 0:
                count += 1
            else:
                break
        return count
```

### 7.2 Recovery Protocol

```
=== 낙폭 회복 프로토콜 ===

Phase 1: 안정화 (1-3일)
- 모든 거래 중지
- 현재 포지션 검토
- 고위험 포지션 청산

Phase 2: 분석 (3-7일)
- 최근 50 거래 분석
- 패턴 및 실수 파악
- 전략 수정 사항 도출

Phase 3: 재진입 (7-14일)
- 50% 포지션 사이즈로 재개
- 낮은 리스크 거래만 진행
- 일일 검토 필수

Phase 4: 정상화 (14일+)
- 성과 확인 후 점진적 증가
- 100% 규모 복귀까지 최소 1개월
- 지속적 모니터링
```

---

## 체크리스트: 거래 전 리스크 확인

### 진입 전 필수 확인 항목

- [ ] **포지션 사이징**: 1-2% 리스크 규칙 준수
- [ ] **손절가 설정**: 진입 전 손절가 결정
- [ ] **손익비**: 최소 2:1 이상
- [ ] **일일 손실**: 일일 손실 한도 미도달
- [ ] **집중도**: 단일 포지션 20% 이하
- [ ] **현금 보유**: 최소 10% 현금 유지
- [ ] **감정 상태**: 냉정하고 객관적인 상태

### 거래 후 확인 항목

- [ ] **손절 설정 확인**: 주문이 올바르게 설정됨
- [ ] **기록**: 트레이딩 저널에 기록
- [ ] **포트폴리오 업데이트**: 집중도 재계산
- [ ] **알림 설정**: 가격 알림 설정
