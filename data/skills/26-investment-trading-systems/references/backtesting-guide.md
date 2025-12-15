# Backtesting Guide

트레이딩 전략 검증을 위한 백테스팅 방법론 가이드입니다.

---

## Why Backtesting?

> "신뢰할 수 없는 백테스트 결과보다 더 나쁜 것은 백테스트 없이 실거래하는 것입니다."

### 백테스팅의 목적

1. **전략 검증**: 과거 데이터에서 전략이 수익성이 있는지 확인
2. **파라미터 최적화**: 최적의 지표 설정값 탐색
3. **리스크 이해**: 최대 낙폭, 연속 손실 등 위험 파악
4. **자신감 구축**: 실거래 전 전략에 대한 확신 획득
5. **기대 수익 설정**: 현실적인 성과 기대치 설정

---

## Part 1: Backtesting Framework

### 1.1 Basic Backtest Engine

```python
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Callable
from datetime import datetime

@dataclass
class Trade:
    entry_date: datetime
    entry_price: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    quantity: int = 1
    side: str = "long"  # "long" or "short"
    pnl: float = 0.0
    pnl_pct: float = 0.0
    
    def close(self, exit_date: datetime, exit_price: float):
        self.exit_date = exit_date
        self.exit_price = exit_price
        
        if self.side == "long":
            self.pnl = (exit_price - self.entry_price) * self.quantity
            self.pnl_pct = (exit_price - self.entry_price) / self.entry_price
        else:
            self.pnl = (self.entry_price - exit_price) * self.quantity
            self.pnl_pct = (self.entry_price - exit_price) / self.entry_price


@dataclass
class BacktestResult:
    trades: List[Trade] = field(default_factory=list)
    equity_curve: pd.Series = None
    metrics: dict = field(default_factory=dict)
    
    def calculate_metrics(self, initial_capital: float):
        if not self.trades:
            return
        
        closed_trades = [t for t in self.trades if t.exit_date is not None]
        
        if not closed_trades:
            return
        
        # 기본 통계
        total_pnl = sum(t.pnl for t in closed_trades)
        winning_trades = [t for t in closed_trades if t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl < 0]
        
        self.metrics = {
            # === 수익 지표 ===
            "total_return": total_pnl,
            "total_return_pct": total_pnl / initial_capital * 100,
            
            # === 거래 통계 ===
            "total_trades": len(closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(closed_trades) if closed_trades else 0,
            
            # === 손익 분석 ===
            "avg_win": np.mean([t.pnl for t in winning_trades]) if winning_trades else 0,
            "avg_loss": np.mean([t.pnl for t in losing_trades]) if losing_trades else 0,
            "largest_win": max([t.pnl for t in winning_trades]) if winning_trades else 0,
            "largest_loss": min([t.pnl for t in losing_trades]) if losing_trades else 0,
            
            # === 리스크 지표 ===
            "profit_factor": (
                abs(sum(t.pnl for t in winning_trades)) / 
                abs(sum(t.pnl for t in losing_trades))
            ) if losing_trades else float('inf'),
            
            "expectancy": total_pnl / len(closed_trades),
        }
        
        # 최대 낙폭 계산
        if self.equity_curve is not None:
            self.metrics["max_drawdown"] = self._calculate_max_drawdown()
            self.metrics["sharpe_ratio"] = self._calculate_sharpe()
    
    def _calculate_max_drawdown(self) -> float:
        peak = self.equity_curve.expanding().max()
        drawdown = (self.equity_curve - peak) / peak
        return abs(drawdown.min())
    
    def _calculate_sharpe(self, risk_free_rate: float = 0.0) -> float:
        returns = self.equity_curve.pct_change().dropna()
        excess_returns = returns - risk_free_rate / 252
        
        if returns.std() == 0:
            return 0
        
        return np.sqrt(252) * excess_returns.mean() / returns.std()


class BacktestEngine:
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = None
        self.trades: List[Trade] = []
        self.equity_history = []
    
    def run(self, data: pd.DataFrame, strategy: Callable) -> BacktestResult:
        """
        백테스트 실행
        
        Args:
            data: OHLCV 데이터프레임 (columns: open, high, low, close, volume)
            strategy: 신호 생성 함수 (data, index) -> "BUY", "SELL", or "HOLD"
        """
        self.capital = self.initial_capital
        self.position = None
        self.trades = []
        self.equity_history = []
        
        for i in range(len(data)):
            current_bar = data.iloc[i]
            current_date = data.index[i]
            
            # 전략 신호 생성
            signal = strategy(data.iloc[:i+1], i)
            
            # 신호 처리
            if signal == "BUY" and self.position is None:
                self._open_position(current_date, current_bar['close'], "long")
            
            elif signal == "SELL" and self.position is not None:
                self._close_position(current_date, current_bar['close'])
            
            # 자산 기록
            current_equity = self._calculate_equity(current_bar['close'])
            self.equity_history.append({
                "date": current_date,
                "equity": current_equity
            })
        
        # 마지막 포지션 청산
        if self.position is not None:
            self._close_position(data.index[-1], data.iloc[-1]['close'])
        
        # 결과 생성
        result = BacktestResult(
            trades=self.trades,
            equity_curve=pd.Series(
                [e["equity"] for e in self.equity_history],
                index=[e["date"] for e in self.equity_history]
            )
        )
        result.calculate_metrics(self.initial_capital)
        
        return result
    
    def _open_position(self, date, price, side):
        # 포지션 크기 계산 (전체 자본의 95% 사용)
        position_value = self.capital * 0.95
        quantity = int(position_value / price)
        
        if quantity > 0:
            self.position = Trade(
                entry_date=date,
                entry_price=price,
                quantity=quantity,
                side=side
            )
            self.capital -= quantity * price
    
    def _close_position(self, date, price):
        if self.position is None:
            return
        
        self.position.close(date, price)
        self.capital += self.position.quantity * price + self.position.pnl
        self.trades.append(self.position)
        self.position = None
    
    def _calculate_equity(self, current_price):
        equity = self.capital
        if self.position is not None:
            if self.position.side == "long":
                equity += self.position.quantity * current_price
            else:
                equity += self.position.quantity * (2 * self.position.entry_price - current_price)
        return equity
```

### 1.2 Strategy Example

```python
def sma_crossover_strategy(data: pd.DataFrame, index: int) -> str:
    """
    SMA 크로스오버 전략
    - 20일 SMA > 50일 SMA → BUY
    - 20일 SMA < 50일 SMA → SELL
    """
    if index < 50:  # 충분한 데이터 필요
        return "HOLD"
    
    close_prices = data['close']
    sma_20 = close_prices.rolling(20).mean().iloc[-1]
    sma_50 = close_prices.rolling(50).mean().iloc[-1]
    
    sma_20_prev = close_prices.rolling(20).mean().iloc[-2]
    sma_50_prev = close_prices.rolling(50).mean().iloc[-2]
    
    # 골든 크로스
    if sma_20 > sma_50 and sma_20_prev <= sma_50_prev:
        return "BUY"
    
    # 데드 크로스
    if sma_20 < sma_50 and sma_20_prev >= sma_50_prev:
        return "SELL"
    
    return "HOLD"


# 사용 예시
import yfinance as yf

# 데이터 다운로드
data = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
data.columns = data.columns.str.lower()

# 백테스트 실행
engine = BacktestEngine(initial_capital=100000)
result = engine.run(data, sma_crossover_strategy)

# 결과 출력
print("=== Backtest Results ===")
for key, value in result.metrics.items():
    if isinstance(value, float):
        print(f"{key}: {value:.4f}")
    else:
        print(f"{key}: {value}")
```

---

## Part 2: Advanced Backtesting

### 2.1 Walk-Forward Optimization

```python
from sklearn.model_selection import TimeSeriesSplit

class WalkForwardOptimizer:
    """
    Walk-Forward Optimization
    - 과적합 방지를 위한 순차적 최적화
    - In-Sample: 파라미터 최적화
    - Out-of-Sample: 검증
    """
    
    def __init__(self, n_splits: int = 5, train_ratio: float = 0.8):
        self.n_splits = n_splits
        self.train_ratio = train_ratio
    
    def optimize(self, data: pd.DataFrame, strategy_class, 
                 param_grid: dict) -> dict:
        """
        Walk-Forward 최적화 실행
        
        Args:
            data: 전체 데이터
            strategy_class: 전략 클래스
            param_grid: 파라미터 탐색 범위
        """
        n = len(data)
        fold_size = n // self.n_splits
        
        all_results = []
        
        for fold in range(self.n_splits):
            # 데이터 분할
            start_idx = fold * fold_size
            end_idx = (fold + 1) * fold_size if fold < self.n_splits - 1 else n
            
            fold_data = data.iloc[start_idx:end_idx]
            train_size = int(len(fold_data) * self.train_ratio)
            
            train_data = fold_data.iloc[:train_size]
            test_data = fold_data.iloc[train_size:]
            
            # In-Sample 최적화
            best_params, best_is_score = self._grid_search(
                train_data, strategy_class, param_grid
            )
            
            # Out-of-Sample 검증
            oos_result = self._evaluate(test_data, strategy_class, best_params)
            
            all_results.append({
                "fold": fold,
                "best_params": best_params,
                "in_sample_sharpe": best_is_score,
                "out_of_sample_sharpe": oos_result["sharpe_ratio"],
                "out_of_sample_return": oos_result["total_return_pct"]
            })
        
        return {
            "fold_results": all_results,
            "avg_oos_sharpe": np.mean([r["out_of_sample_sharpe"] for r in all_results]),
            "avg_oos_return": np.mean([r["out_of_sample_return"] for r in all_results]),
            "consistency": self._calculate_consistency(all_results)
        }
    
    def _grid_search(self, data, strategy_class, param_grid):
        """그리드 서치로 최적 파라미터 탐색"""
        from itertools import product
        
        best_score = -float('inf')
        best_params = None
        
        # 모든 파라미터 조합 생성
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        for values in product(*param_values):
            params = dict(zip(param_names, values))
            
            # 전략 생성 및 백테스트
            strategy = strategy_class(**params)
            engine = BacktestEngine()
            result = engine.run(data, strategy.generate_signal)
            
            score = result.metrics.get("sharpe_ratio", 0)
            
            if score > best_score:
                best_score = score
                best_params = params
        
        return best_params, best_score
    
    def _evaluate(self, data, strategy_class, params):
        """파라미터로 평가"""
        strategy = strategy_class(**params)
        engine = BacktestEngine()
        result = engine.run(data, strategy.generate_signal)
        return result.metrics
    
    def _calculate_consistency(self, results):
        """OOS 성과 일관성 측정"""
        oos_sharpes = [r["out_of_sample_sharpe"] for r in results]
        positive_folds = sum(1 for s in oos_sharpes if s > 0)
        return positive_folds / len(results)
```

### 2.2 Monte Carlo Simulation

```python
class MonteCarloSimulator:
    """
    Monte Carlo 시뮬레이션
    - 거래 순서 무작위화로 운의 영향 측정
    - 최악/최선의 시나리오 파악
    """
    
    def __init__(self, n_simulations: int = 1000):
        self.n_simulations = n_simulations
    
    def simulate(self, trades: List[Trade], initial_capital: float) -> dict:
        """
        거래 순서를 무작위로 섞어 다양한 자산 곡선 생성
        """
        pnls = [t.pnl for t in trades]
        
        simulation_results = []
        
        for _ in range(self.n_simulations):
            # 거래 순서 무작위화
            shuffled_pnls = np.random.permutation(pnls)
            
            # 자산 곡선 생성
            equity = initial_capital
            equity_curve = [equity]
            
            for pnl in shuffled_pnls:
                equity += pnl
                equity_curve.append(equity)
            
            # 지표 계산
            max_drawdown = self._calculate_max_drawdown(equity_curve)
            final_equity = equity_curve[-1]
            total_return = (final_equity - initial_capital) / initial_capital
            
            simulation_results.append({
                "final_equity": final_equity,
                "total_return": total_return,
                "max_drawdown": max_drawdown
            })
        
        # 결과 분석
        returns = [r["total_return"] for r in simulation_results]
        drawdowns = [r["max_drawdown"] for r in simulation_results]
        
        return {
            "num_simulations": self.n_simulations,
            "return_distribution": {
                "mean": np.mean(returns),
                "std": np.std(returns),
                "percentile_5": np.percentile(returns, 5),
                "percentile_25": np.percentile(returns, 25),
                "percentile_50": np.percentile(returns, 50),
                "percentile_75": np.percentile(returns, 75),
                "percentile_95": np.percentile(returns, 95)
            },
            "drawdown_distribution": {
                "mean": np.mean(drawdowns),
                "worst_case": max(drawdowns),
                "percentile_95": np.percentile(drawdowns, 95)
            },
            "probability_of_profit": sum(1 for r in returns if r > 0) / len(returns),
            "probability_of_ruin": sum(1 for r in simulation_results 
                                       if r["final_equity"] < initial_capital * 0.5) / len(simulation_results)
        }
    
    def _calculate_max_drawdown(self, equity_curve):
        peak = equity_curve[0]
        max_dd = 0
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
```

---

## Part 3: Avoiding Backtest Bias

### 3.1 Common Pitfalls

```python
class BacktestBiasChecker:
    """백테스트 편향 검사"""
    
    @staticmethod
    def check_lookahead_bias(strategy_function: str) -> list:
        """
        미래 정보 사용 검사 (Look-Ahead Bias)
        
        Warning Signs:
        - shift(-n) 사용 (미래 데이터 참조)
        - 미래 날짜 필터링
        - 결과 기반 조건문
        """
        warnings = []
        
        if "shift(-" in strategy_function:
            warnings.append("Potential look-ahead bias: shift(-n) detected")
        
        if ".iloc[-1]" in strategy_function and "rolling" not in strategy_function:
            warnings.append("Check if using future data in calculations")
        
        return warnings
    
    @staticmethod
    def check_survivorship_bias(symbols: List[str], start_date: str) -> dict:
        """
        생존자 편향 검사 (Survivorship Bias)
        
        현재 존재하는 기업만 테스트하면 상장폐지된 기업 제외됨
        """
        # 실제로는 과거 지수 구성종목 데이터 필요
        warning = """
        Warning: Survivorship Bias Risk
        - Testing only currently listed stocks excludes delisted companies
        - May overestimate historical returns by 1-2% annually
        - Solution: Use historical index constituents or point-in-time data
        """
        
        return {
            "warning": warning,
            "tested_symbols": len(symbols),
            "recommendation": "Use delisting-adjusted data"
        }
    
    @staticmethod
    def check_overfitting(in_sample_metrics: dict, 
                         out_sample_metrics: dict) -> dict:
        """
        과적합 검사 (Overfitting)
        
        IS와 OOS 성과 차이가 크면 과적합 의심
        """
        is_sharpe = in_sample_metrics.get("sharpe_ratio", 0)
        oos_sharpe = out_sample_metrics.get("sharpe_ratio", 0)
        
        degradation = (is_sharpe - oos_sharpe) / is_sharpe if is_sharpe > 0 else 0
        
        if degradation > 0.5:
            risk_level = "HIGH"
            recommendation = "Reduce parameters, increase data, or simplify strategy"
        elif degradation > 0.25:
            risk_level = "MEDIUM"
            recommendation = "Monitor closely, consider parameter reduction"
        else:
            risk_level = "LOW"
            recommendation = "Strategy appears robust"
        
        return {
            "in_sample_sharpe": is_sharpe,
            "out_sample_sharpe": oos_sharpe,
            "performance_degradation": degradation,
            "overfitting_risk": risk_level,
            "recommendation": recommendation
        }


# 파라미터 수 vs 데이터 포인트 규칙
PARAMETER_RULE = """
📏 Parameter Count Rule of Thumb

데이터 포인트당 최대 1-2개의 최적화 파라미터

예시:
- 5년 일간 데이터 ≈ 1,250 포인트
- 최대 권장 파라미터: 2-4개

경고 신호:
- 파라미터 > 데이터 포인트 / 250 → 과적합 위험
- 파라미터가 많을수록 WFO 검증 필수
"""
```

### 3.2 Realistic Assumptions

```python
class RealisticBacktestConfig:
    """현실적인 백테스트 설정"""
    
    # === Transaction Costs ===
    COMMISSION_PER_SHARE = 0.005      # $0.005/주
    COMMISSION_MINIMUM = 1.00          # 최소 $1
    COMMISSION_MAXIMUM = None          # 최대 없음
    
    # === Slippage ===
    SLIPPAGE_PCT = 0.001              # 0.1% 슬리피지
    SLIPPAGE_TICKS = 1                # 또는 1틱
    
    # === Market Impact ===
    # 대량 주문 시 가격 영향
    MARKET_IMPACT_FACTOR = 0.0001     # 주문 크기 × factor
    
    # === Execution Delays ===
    FILL_DELAY_BARS = 1               # 1봉 지연 체결
    
    def calculate_total_cost(self, price: float, quantity: int, 
                            is_market_order: bool = True) -> float:
        """총 거래 비용 계산"""
        
        # 수수료
        commission = max(
            quantity * self.COMMISSION_PER_SHARE,
            self.COMMISSION_MINIMUM
        )
        
        # 슬리피지
        slippage = price * quantity * self.SLIPPAGE_PCT
        
        # 시장 충격 (대량 주문)
        market_impact = 0
        if is_market_order and quantity > 1000:
            market_impact = price * quantity * self.MARKET_IMPACT_FACTOR * np.sqrt(quantity / 1000)
        
        return commission + slippage + market_impact


class RealisticBacktestEngine(BacktestEngine):
    """현실적 비용을 반영한 백테스트 엔진"""
    
    def __init__(self, initial_capital: float = 100000, 
                 config: RealisticBacktestConfig = None):
        super().__init__(initial_capital)
        self.config = config or RealisticBacktestConfig()
        self.total_costs = 0
    
    def _open_position(self, date, price, side):
        position_value = self.capital * 0.95
        quantity = int(position_value / price)
        
        if quantity > 0:
            # 슬리피지 적용
            adjusted_price = price * (1 + self.config.SLIPPAGE_PCT)
            
            # 비용 계산
            cost = self.config.calculate_total_cost(adjusted_price, quantity)
            self.total_costs += cost
            
            self.position = Trade(
                entry_date=date,
                entry_price=adjusted_price,
                quantity=quantity,
                side=side
            )
            self.capital -= quantity * adjusted_price + cost
    
    def _close_position(self, date, price):
        if self.position is None:
            return
        
        # 슬리피지 적용 (매도 시 불리한 방향)
        if self.position.side == "long":
            adjusted_price = price * (1 - self.config.SLIPPAGE_PCT)
        else:
            adjusted_price = price * (1 + self.config.SLIPPAGE_PCT)
        
        # 비용 계산
        cost = self.config.calculate_total_cost(adjusted_price, self.position.quantity)
        self.total_costs += cost
        
        self.position.close(date, adjusted_price)
        receive_amount = self.position.quantity * adjusted_price - cost
        self.capital += receive_amount
        self.trades.append(self.position)
        self.position = None
```

---

## Part 4: Performance Metrics Deep Dive

### 4.1 Comprehensive Metrics Calculator

```python
class PerformanceMetrics:
    """종합 성과 지표 계산"""
    
    @staticmethod
    def calculate_all(trades: List[Trade], equity_curve: pd.Series,
                     initial_capital: float, risk_free_rate: float = 0.04) -> dict:
        """모든 성과 지표 계산"""
        
        closed_trades = [t for t in trades if t.exit_date]
        
        if not closed_trades:
            return {}
        
        returns = equity_curve.pct_change().dropna()
        pnls = [t.pnl for t in closed_trades]
        
        # === 수익 지표 ===
        total_return = (equity_curve.iloc[-1] - initial_capital) / initial_capital
        cagr = PerformanceMetrics.calculate_cagr(equity_curve, initial_capital)
        
        # === 리스크 조정 수익 ===
        sharpe = PerformanceMetrics.calculate_sharpe(returns, risk_free_rate)
        sortino = PerformanceMetrics.calculate_sortino(returns, risk_free_rate)
        calmar = PerformanceMetrics.calculate_calmar(cagr, equity_curve)
        
        # === 낙폭 분석 ===
        max_dd, max_dd_duration = PerformanceMetrics.calculate_max_drawdown(equity_curve)
        
        # === 거래 통계 ===
        winning = [t for t in closed_trades if t.pnl > 0]
        losing = [t for t in closed_trades if t.pnl < 0]
        
        win_rate = len(winning) / len(closed_trades) if closed_trades else 0
        profit_factor = (
            sum(t.pnl for t in winning) / abs(sum(t.pnl for t in losing))
            if losing else float('inf')
        )
        
        # === 연속 거래 분석 ===
        max_consecutive_wins = PerformanceMetrics.max_consecutive(pnls, positive=True)
        max_consecutive_losses = PerformanceMetrics.max_consecutive(pnls, positive=False)
        
        return {
            # 수익
            "total_return_pct": total_return * 100,
            "cagr_pct": cagr * 100,
            
            # 리스크 조정
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "calmar_ratio": calmar,
            
            # 낙폭
            "max_drawdown_pct": max_dd * 100,
            "max_drawdown_duration_days": max_dd_duration,
            
            # 거래
            "total_trades": len(closed_trades),
            "win_rate_pct": win_rate * 100,
            "profit_factor": profit_factor,
            "expectancy": np.mean(pnls),
            "avg_win": np.mean([t.pnl for t in winning]) if winning else 0,
            "avg_loss": np.mean([t.pnl for t in losing]) if losing else 0,
            
            # 연속
            "max_consecutive_wins": max_consecutive_wins,
            "max_consecutive_losses": max_consecutive_losses,
            
            # 분포
            "pnl_std": np.std(pnls),
            "skewness": PerformanceMetrics.calculate_skewness(pnls),
            "kurtosis": PerformanceMetrics.calculate_kurtosis(pnls)
        }
    
    @staticmethod
    def calculate_cagr(equity_curve: pd.Series, initial_capital: float) -> float:
        """CAGR (Compound Annual Growth Rate)"""
        years = (equity_curve.index[-1] - equity_curve.index[0]).days / 365.25
        final_value = equity_curve.iloc[-1]
        
        if years <= 0 or initial_capital <= 0:
            return 0
        
        return (final_value / initial_capital) ** (1 / years) - 1
    
    @staticmethod
    def calculate_sharpe(returns: pd.Series, risk_free_rate: float = 0.04) -> float:
        """Sharpe Ratio"""
        if returns.std() == 0:
            return 0
        
        excess_returns = returns - risk_free_rate / 252
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    @staticmethod
    def calculate_sortino(returns: pd.Series, risk_free_rate: float = 0.04) -> float:
        """Sortino Ratio (하방 변동성만 고려)"""
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        excess_returns = returns.mean() - risk_free_rate / 252
        return np.sqrt(252) * excess_returns / downside_returns.std()
    
    @staticmethod
    def calculate_calmar(cagr: float, equity_curve: pd.Series) -> float:
        """Calmar Ratio (CAGR / Max Drawdown)"""
        max_dd, _ = PerformanceMetrics.calculate_max_drawdown(equity_curve)
        
        if max_dd == 0:
            return 0
        
        return cagr / max_dd
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> tuple:
        """최대 낙폭 및 기간"""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        
        max_dd = abs(drawdown.min())
        
        # 낙폭 기간 계산
        in_drawdown = drawdown < 0
        
        if not in_drawdown.any():
            return max_dd, 0
        
        # 가장 긴 낙폭 기간
        duration = 0
        current_duration = 0
        
        for is_dd in in_drawdown:
            if is_dd:
                current_duration += 1
                duration = max(duration, current_duration)
            else:
                current_duration = 0
        
        return max_dd, duration
    
    @staticmethod
    def max_consecutive(pnls: list, positive: bool = True) -> int:
        """연속 승/패 계산"""
        max_streak = 0
        current_streak = 0
        
        for pnl in pnls:
            if (positive and pnl > 0) or (not positive and pnl < 0):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    @staticmethod
    def calculate_skewness(data: list) -> float:
        """왜도 (Skewness)"""
        from scipy.stats import skew
        return skew(data) if len(data) > 2 else 0
    
    @staticmethod
    def calculate_kurtosis(data: list) -> float:
        """첨도 (Kurtosis)"""
        from scipy.stats import kurtosis
        return kurtosis(data) if len(data) > 3 else 0
```

### 4.2 Performance Benchmarks

```python
PERFORMANCE_BENCHMARKS = {
    # === 리스크 조정 수익 ===
    "sharpe_ratio": {
        "excellent": 2.0,
        "good": 1.0,
        "acceptable": 0.5,
        "poor": 0.0
    },
    
    "sortino_ratio": {
        "excellent": 3.0,
        "good": 2.0,
        "acceptable": 1.0,
        "poor": 0.0
    },
    
    # === 낙폭 ===
    "max_drawdown": {
        "excellent": 0.10,  # < 10%
        "good": 0.20,       # < 20%
        "acceptable": 0.30, # < 30%
        "poor": 0.50        # > 50%
    },
    
    # === 거래 통계 ===
    "win_rate": {
        "day_trading": 0.55,    # 55%+ for day trading
        "swing_trading": 0.45,  # 45%+ for swing trading
        "trend_following": 0.35 # 35%+ for trend following
    },
    
    "profit_factor": {
        "excellent": 2.0,
        "good": 1.5,
        "acceptable": 1.2,
        "breakeven": 1.0
    }
}


def evaluate_strategy(metrics: dict) -> dict:
    """전략 등급 평가"""
    
    grades = {}
    
    # Sharpe Ratio
    sharpe = metrics.get("sharpe_ratio", 0)
    if sharpe >= 2.0:
        grades["sharpe"] = "A"
    elif sharpe >= 1.0:
        grades["sharpe"] = "B"
    elif sharpe >= 0.5:
        grades["sharpe"] = "C"
    else:
        grades["sharpe"] = "F"
    
    # Max Drawdown
    max_dd = metrics.get("max_drawdown_pct", 100) / 100
    if max_dd <= 0.10:
        grades["drawdown"] = "A"
    elif max_dd <= 0.20:
        grades["drawdown"] = "B"
    elif max_dd <= 0.30:
        grades["drawdown"] = "C"
    else:
        grades["drawdown"] = "F"
    
    # Profit Factor
    pf = metrics.get("profit_factor", 0)
    if pf >= 2.0:
        grades["profit_factor"] = "A"
    elif pf >= 1.5:
        grades["profit_factor"] = "B"
    elif pf >= 1.2:
        grades["profit_factor"] = "C"
    else:
        grades["profit_factor"] = "F"
    
    # 종합 등급
    grade_values = {"A": 4, "B": 3, "C": 2, "F": 0}
    avg_grade = np.mean([grade_values[g] for g in grades.values()])
    
    if avg_grade >= 3.5:
        overall = "A"
    elif avg_grade >= 2.5:
        overall = "B"
    elif avg_grade >= 1.5:
        overall = "C"
    else:
        overall = "F"
    
    return {
        "individual_grades": grades,
        "overall_grade": overall,
        "recommendation": "Trade Live" if overall in ["A", "B"] else "Refine Strategy"
    }
```

---

## Part 5: Backtest Report Template

```python
def generate_backtest_report(result: BacktestResult, strategy_name: str,
                            initial_capital: float) -> str:
    """백테스트 보고서 생성"""
    
    m = result.metrics
    
    report = f"""
# Backtest Report: {strategy_name}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Initial Capital:** ${initial_capital:,.2f}
**Final Capital:** ${result.equity_curve.iloc[-1]:,.2f}

---

## Summary

| Metric | Value | Grade |
|--------|-------|-------|
| Total Return | {m.get('total_return_pct', 0):.2f}% | |
| CAGR | {m.get('cagr_pct', 0):.2f}% | |
| Sharpe Ratio | {m.get('sharpe_ratio', 0):.2f} | {'✅' if m.get('sharpe_ratio', 0) > 1 else '⚠️'} |
| Sortino Ratio | {m.get('sortino_ratio', 0):.2f} | |
| Max Drawdown | {m.get('max_drawdown_pct', 0):.2f}% | {'✅' if m.get('max_drawdown_pct', 100) < 20 else '⚠️'} |

---

## Trade Statistics

| Metric | Value |
|--------|-------|
| Total Trades | {m.get('total_trades', 0)} |
| Win Rate | {m.get('win_rate_pct', 0):.1f}% |
| Profit Factor | {m.get('profit_factor', 0):.2f} |
| Average Win | ${m.get('avg_win', 0):,.2f} |
| Average Loss | ${m.get('avg_loss', 0):,.2f} |
| Expectancy | ${m.get('expectancy', 0):,.2f} |

---

## Risk Analysis

| Metric | Value |
|--------|-------|
| Max Drawdown Duration | {m.get('max_drawdown_duration_days', 0)} days |
| Max Consecutive Wins | {m.get('max_consecutive_wins', 0)} |
| Max Consecutive Losses | {m.get('max_consecutive_losses', 0)} |
| PnL Std Dev | ${m.get('pnl_std', 0):,.2f} |

---

## Recommendations

{'✅ Strategy meets quality thresholds' if m.get('sharpe_ratio', 0) > 1 and m.get('max_drawdown_pct', 100) < 20 else '⚠️ Strategy needs refinement'}

**Next Steps:**
1. Conduct Walk-Forward Optimization
2. Run Monte Carlo Simulation
3. Paper trade for 1 month before live trading

---

*This report is for informational purposes only. Past performance does not guarantee future results.*
"""
    
    return report
```

---

## 체크리스트: 백테스트 품질

### 필수 확인 항목

- [ ] **데이터 품질**: 최소 2년 데이터, 결측치 확인
- [ ] **미래 정보 배제**: Look-ahead bias 검사
- [ ] **생존자 편향 고려**: 상장폐지 종목 포함 여부
- [ ] **거래 비용 반영**: 수수료, 슬리피지, 시장 충격
- [ ] **현실적 체결**: 지연 및 미체결 고려
- [ ] **아웃 오브 샘플 테스트**: 최소 20% 데이터
- [ ] **Walk-Forward 검증**: 과적합 방지
- [ ] **Monte Carlo 시뮬레이션**: 운의 영향 측정
- [ ] **파라미터 수 제한**: 데이터 대비 적정 파라미터

### 결과 평가 기준

| 지표 | 최소 기준 | 권장 기준 |
|------|----------|----------|
| Sharpe Ratio | > 0.5 | > 1.5 |
| Max Drawdown | < 30% | < 15% |
| Profit Factor | > 1.2 | > 1.5 |
| Win Rate | 전략에 따라 | 손익비와 조합 |
| OOS 성과 유지 | > 50% IS | > 75% IS |
