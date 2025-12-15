# Trading Strategies Reference

다양한 트레이딩 전략에 대한 상세 구현 가이드입니다.

---

## Part 1: Technical Analysis Strategies (기술적 분석)

### 1.1 RSI Strategy (Relative Strength Index)

**개요**: RSI는 가격 변동의 속도와 변화를 측정하는 모멘텀 오실레이터입니다.

```python
import talib
import pandas as pd

class RSIStrategy:
    def __init__(self, period=14, overbought=70, oversold=30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        return talib.RSI(prices, timeperiod=self.period)
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df['RSI'] = self.calculate_rsi(df['close'])
        
        # 신호 생성
        df['signal'] = 0
        df.loc[df['RSI'] < self.oversold, 'signal'] = 1      # 매수
        df.loc[df['RSI'] > self.overbought, 'signal'] = -1   # 매도
        
        # 다이버전스 감지
        df['bullish_divergence'] = self._detect_bullish_divergence(df)
        df['bearish_divergence'] = self._detect_bearish_divergence(df)
        
        return df
    
    def _detect_bullish_divergence(self, df):
        """가격은 저점 갱신, RSI는 저점 상승 = 강세 다이버전스"""
        price_lower_low = df['close'] < df['close'].shift(5)
        rsi_higher_low = df['RSI'] > df['RSI'].shift(5)
        return price_lower_low & rsi_higher_low & (df['RSI'] < 40)
    
    def _detect_bearish_divergence(self, df):
        """가격은 고점 갱신, RSI는 고점 하락 = 약세 다이버전스"""
        price_higher_high = df['close'] > df['close'].shift(5)
        rsi_lower_high = df['RSI'] < df['RSI'].shift(5)
        return price_higher_high & rsi_lower_high & (df['RSI'] > 60)
```

**진입 규칙**:
- RSI < 30 → 매수 신호 (과매도)
- RSI > 70 → 매도 신호 (과매수)
- 강세 다이버전스 → 강력 매수 신호
- 약세 다이버전스 → 강력 매도 신호

**리스크 관리**:
- 손절: 진입가 대비 2% 하락
- 익절: RSI가 50 수준에 도달 or 반대 신호

---

### 1.2 MACD Strategy (Moving Average Convergence Divergence)

```python
class MACDStrategy:
    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal_period = signal
    
    def calculate_macd(self, prices: pd.Series) -> tuple:
        macd, signal, histogram = talib.MACD(
            prices,
            fastperiod=self.fast,
            slowperiod=self.slow,
            signalperiod=self.signal_period
        )
        return macd, signal, histogram
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df['MACD'], df['Signal'], df['Histogram'] = self.calculate_macd(df['close'])
        
        # 골든 크로스 / 데드 크로스
        df['golden_cross'] = (df['MACD'] > df['Signal']) & (df['MACD'].shift(1) <= df['Signal'].shift(1))
        df['death_cross'] = (df['MACD'] < df['Signal']) & (df['MACD'].shift(1) >= df['Signal'].shift(1))
        
        # 히스토그램 모멘텀
        df['histogram_rising'] = df['Histogram'] > df['Histogram'].shift(1)
        df['histogram_falling'] = df['Histogram'] < df['Histogram'].shift(1)
        
        return df
```

**핵심 신호**:
| 신호 | 해석 | 강도 |
|------|------|------|
| Golden Cross (MACD > Signal) | 상승 전환 | 중간 |
| Death Cross (MACD < Signal) | 하락 전환 | 중간 |
| Histogram 확대 + Golden Cross | 강한 상승 모멘텀 | 강함 |
| Zero Line 상향 돌파 | 추세 전환 확인 | 강함 |

---

### 1.3 Bollinger Bands Strategy

```python
class BollingerBandsStrategy:
    def __init__(self, period=20, std_dev=2):
        self.period = period
        self.std_dev = std_dev
    
    def calculate_bands(self, prices: pd.Series) -> tuple:
        upper, middle, lower = talib.BBANDS(
            prices,
            timeperiod=self.period,
            nbdevup=self.std_dev,
            nbdevdn=self.std_dev
        )
        return upper, middle, lower
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = self.calculate_bands(df['close'])
        
        # 밴드폭 (변동성 측정)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        
        # 스퀴즈 감지 (변동성 수축 → 폭발 예상)
        df['squeeze'] = df['BB_Width'] < df['BB_Width'].rolling(20).quantile(0.1)
        
        # Mean Reversion 신호
        df['buy_signal'] = df['close'] < df['BB_Lower']   # 하단 밴드 터치 → 매수
        df['sell_signal'] = df['close'] > df['BB_Upper']  # 상단 밴드 터치 → 매도
        
        # Band Walk (강한 추세)
        df['bullish_walk'] = (df['close'] > df['BB_Upper']).rolling(3).sum() >= 3
        df['bearish_walk'] = (df['close'] < df['BB_Lower']).rolling(3).sum() >= 3
        
        return df
```

**전략 유형**:

1. **Mean Reversion (역추세)**
   - 하단 밴드 터치 → 매수, 중간선 도달 → 청산
   - 레인지 마켓에서 효과적

2. **Breakout (추세 추종)**
   - 스퀴즈 후 상단 돌파 → 매수
   - 추세 마켓에서 효과적

3. **Band Walk**
   - 3일 연속 상단 밴드 위 → 강한 상승 추세 확인
   - 추세 따라 포지션 유지

---

## Part 2: Statistical Arbitrage (통계적 차익거래)

### 2.1 Pair Trading Strategy

```python
from statsmodels.tsa.stattools import coint, adfuller
import numpy as np

class PairTradingStrategy:
    def __init__(self, lookback=252, entry_z=2.0, exit_z=0.5, stop_z=3.0):
        self.lookback = lookback
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.stop_z = stop_z
    
    def find_cointegrated_pairs(self, prices_df: pd.DataFrame, p_value_threshold=0.05):
        """공적분 관계 페어 탐색"""
        n = prices_df.shape[1]
        tickers = prices_df.columns
        cointegrated_pairs = []
        
        for i in range(n):
            for j in range(i+1, n):
                stock1 = prices_df.iloc[:, i]
                stock2 = prices_df.iloc[:, j]
                
                # 공적분 테스트
                score, p_value, _ = coint(stock1, stock2)
                
                if p_value < p_value_threshold:
                    # 헤지 비율 계산
                    beta = self._calculate_hedge_ratio(stock1, stock2)
                    
                    # 스프레드 반감기 계산
                    spread = stock1 - beta * stock2
                    half_life = self._calculate_half_life(spread)
                    
                    cointegrated_pairs.append({
                        'stock1': tickers[i],
                        'stock2': tickers[j],
                        'p_value': p_value,
                        'beta': beta,
                        'half_life': half_life,
                        'correlation': stock1.corr(stock2)
                    })
        
        # p-value 기준 정렬
        return sorted(cointegrated_pairs, key=lambda x: x['p_value'])
    
    def _calculate_hedge_ratio(self, stock1, stock2):
        """OLS 기반 헤지 비율"""
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(stock2.values.reshape(-1, 1), stock1.values)
        return model.coef_[0]
    
    def _calculate_half_life(self, spread):
        """평균 회귀 반감기 (AR(1) 기반)"""
        spread_lag = spread.shift(1).dropna()
        spread_ret = spread.diff().dropna()
        spread_lag = spread_lag.iloc[1:]
        
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(spread_lag.values.reshape(-1, 1), spread_ret.values)
        
        half_life = -np.log(2) / model.coef_[0]
        return half_life
    
    def calculate_zscore(self, spread: pd.Series, window=60) -> pd.Series:
        """롤링 Z-Score 계산"""
        mean = spread.rolling(window).mean()
        std = spread.rolling(window).std()
        return (spread - mean) / std
    
    def generate_signals(self, stock1_prices, stock2_prices, beta):
        """거래 신호 생성"""
        spread = stock1_prices - beta * stock2_prices
        zscore = self.calculate_zscore(spread)
        
        signals = pd.DataFrame(index=stock1_prices.index)
        signals['zscore'] = zscore
        signals['position'] = 0
        
        # Long Spread: Z < -entry_z (Stock1 저평가)
        signals.loc[zscore < -self.entry_z, 'position'] = 1
        
        # Short Spread: Z > entry_z (Stock1 고평가)
        signals.loc[zscore > self.entry_z, 'position'] = -1
        
        # Exit: |Z| < exit_z
        signals.loc[abs(zscore) < self.exit_z, 'position'] = 0
        
        # Stop Loss: |Z| > stop_z
        signals.loc[abs(zscore) > self.stop_z, 'position'] = 0
        
        return signals
```

**페어 트레이딩 실행 예시**:

| Z-Score | 포지션 | Stock A | Stock B |
|---------|--------|---------|---------|
| Z < -2.0 | Long Spread | Buy | Sell (beta × 수량) |
| Z > +2.0 | Short Spread | Sell | Buy (beta × 수량) |
| |Z| < 0.5 | Exit | Close | Close |
| |Z| > 3.0 | Stop Loss | Close | Close |

---

## Part 3: Momentum Strategies

### 3.1 Dual Moving Average Crossover

```python
class DualMACrossover:
    def __init__(self, fast_period=20, slow_period=50):
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df['SMA_fast'] = df['close'].rolling(self.fast_period).mean()
        df['SMA_slow'] = df['close'].rolling(self.slow_period).mean()
        
        # 골든/데드 크로스
        df['golden_cross'] = (df['SMA_fast'] > df['SMA_slow']) & \
                             (df['SMA_fast'].shift(1) <= df['SMA_slow'].shift(1))
        df['death_cross'] = (df['SMA_fast'] < df['SMA_slow']) & \
                            (df['SMA_fast'].shift(1) >= df['SMA_slow'].shift(1))
        
        # 트렌드 필터
        df['uptrend'] = df['close'] > df['SMA_slow']
        df['downtrend'] = df['close'] < df['SMA_slow']
        
        return df
```

### 3.2 Rate of Change (ROC) Momentum

```python
class ROCMomentum:
    def __init__(self, roc_period=12, signal_threshold=5):
        self.roc_period = roc_period
        self.signal_threshold = signal_threshold
    
    def calculate_roc(self, prices: pd.Series) -> pd.Series:
        """ROC = (현재가 - N일 전 가격) / N일 전 가격 × 100"""
        return ((prices - prices.shift(self.roc_period)) / 
                prices.shift(self.roc_period)) * 100
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df['ROC'] = self.calculate_roc(df['close'])
        
        # 모멘텀 신호
        df['strong_momentum'] = df['ROC'] > self.signal_threshold
        df['weak_momentum'] = df['ROC'] < -self.signal_threshold
        
        # Zero Line 크로스
        df['bullish_cross'] = (df['ROC'] > 0) & (df['ROC'].shift(1) <= 0)
        df['bearish_cross'] = (df['ROC'] < 0) & (df['ROC'].shift(1) >= 0)
        
        return df
```

---

## Part 4: Volatility-Based Strategies

### 4.1 ATR-Based Position Sizing

```python
class ATRPositionSizing:
    def __init__(self, atr_period=14, risk_factor=2.0):
        self.atr_period = atr_period
        self.risk_factor = risk_factor  # ATR 배수
    
    def calculate_atr(self, df: pd.DataFrame) -> pd.Series:
        return talib.ATR(df['high'], df['low'], df['close'], timeperiod=self.atr_period)
    
    def calculate_stop_loss(self, entry_price: float, atr: float, direction: str) -> float:
        """ATR 기반 동적 손절 계산"""
        stop_distance = atr * self.risk_factor
        
        if direction == 'long':
            return entry_price - stop_distance
        else:
            return entry_price + stop_distance
    
    def calculate_position_size(self, account_balance: float, risk_pct: float,
                                entry_price: float, stop_loss: float) -> int:
        """리스크 금액 기반 포지션 사이징"""
        risk_amount = account_balance * risk_pct
        risk_per_share = abs(entry_price - stop_loss)
        return int(risk_amount / risk_per_share)
```

### 4.2 Volatility Breakout (Range Expansion)

```python
class VolatilityBreakout:
    def __init__(self, lookback=20, expansion_threshold=1.5):
        self.lookback = lookback
        self.expansion_threshold = expansion_threshold
    
    def detect_breakout(self, df: pd.DataFrame) -> pd.DataFrame:
        # 이전 N일 최고/최저
        df['high_n'] = df['high'].rolling(self.lookback).max()
        df['low_n'] = df['low'].rolling(self.lookback).min()
        df['range'] = df['high_n'] - df['low_n']
        
        # 당일 변동폭
        df['today_range'] = df['high'] - df['low']
        
        # 변동성 확장 감지
        df['vol_expansion'] = df['today_range'] > df['range'].shift(1) * self.expansion_threshold
        
        # 돌파 방향
        df['bullish_breakout'] = (df['close'] > df['high_n'].shift(1)) & df['vol_expansion']
        df['bearish_breakout'] = (df['close'] < df['low_n'].shift(1)) & df['vol_expansion']
        
        return df
```

---

## Part 5: Multi-Timeframe Analysis

### 5.1 Timeframe Alignment Strategy

```python
class MultiTimeframeStrategy:
    def __init__(self):
        self.timeframes = ['1D', '4H', '1H']  # 상위 → 하위
    
    def analyze_alignment(self, data_dict: dict) -> dict:
        """
        data_dict: {'1D': df_daily, '4H': df_4h, '1H': df_1h}
        """
        trends = {}
        
        for tf, df in data_dict.items():
            # 각 시간프레임 추세 판단
            sma_50 = df['close'].rolling(50).mean().iloc[-1]
            sma_200 = df['close'].rolling(200).mean().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if current_price > sma_50 > sma_200:
                trends[tf] = 'bullish'
            elif current_price < sma_50 < sma_200:
                trends[tf] = 'bearish'
            else:
                trends[tf] = 'neutral'
        
        # 정렬 여부 판단
        all_bullish = all(t == 'bullish' for t in trends.values())
        all_bearish = all(t == 'bearish' for t in trends.values())
        
        return {
            'trends': trends,
            'aligned': all_bullish or all_bearish,
            'direction': 'bullish' if all_bullish else ('bearish' if all_bearish else 'mixed'),
            'confidence': 'high' if (all_bullish or all_bearish) else 'low'
        }
```

**Multi-Timeframe 규칙**:

1. **상위 시간프레임**: 전체 추세 방향 결정
2. **중간 시간프레임**: 진입 영역 파악
3. **하위 시간프레임**: 정밀 진입 타이밍

| 1D 추세 | 4H 추세 | 1H 신호 | 행동 |
|---------|---------|---------|------|
| Bullish | Bullish | 매수 신호 | ✅ 진입 |
| Bullish | Bearish | 매수 신호 | ⚠️ 대기 (조정 중) |
| Bearish | Bullish | 매수 신호 | ❌ 회피 (역추세) |
| Aligned | Aligned | Aligned | ✅ 높은 확신 |

---

## Part 6: Entry/Exit Techniques

### 6.1 Pullback Entry

```python
class PullbackEntry:
    def __init__(self, trend_ma=50, pullback_ma=20, rsi_oversold=40):
        self.trend_ma = trend_ma
        self.pullback_ma = pullback_ma
        self.rsi_oversold = rsi_oversold
    
    def find_pullback_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        df['SMA_trend'] = df['close'].rolling(self.trend_ma).mean()
        df['SMA_pullback'] = df['close'].rolling(self.pullback_ma).mean()
        df['RSI'] = talib.RSI(df['close'], timeperiod=14)
        
        # 상승 추세 확인
        df['uptrend'] = df['close'] > df['SMA_trend']
        
        # 풀백 감지: 가격이 단기 MA 아래로 하락
        df['pullback'] = df['close'] < df['SMA_pullback']
        
        # RSI 과매도 진입
        df['entry_signal'] = df['uptrend'] & df['pullback'] & (df['RSI'] < self.rsi_oversold)
        
        return df
```

### 6.2 Trailing Stop Implementation

```python
class TrailingStop:
    def __init__(self, initial_stop_pct=0.02, trail_pct=0.015):
        self.initial_stop_pct = initial_stop_pct
        self.trail_pct = trail_pct
    
    def calculate_trailing_stop(self, entry_price: float, highest_price: float,
                                current_stop: float, direction: str) -> float:
        if direction == 'long':
            # 최고가 갱신 시 손절 상향
            new_stop = highest_price * (1 - self.trail_pct)
            return max(current_stop, new_stop)
        else:
            # 최저가 갱신 시 손절 하향
            new_stop = highest_price * (1 + self.trail_pct)
            return min(current_stop, new_stop)
```

---

## 전략 선택 가이드

| 시장 상황 | 권장 전략 | 이유 |
|----------|----------|------|
| 강한 추세 | MA Crossover, Breakout | 추세 따라 이익 극대화 |
| 레인지 (횡보) | Bollinger Mean Reversion, RSI | 과매수/과매도에서 역추세 |
| 높은 변동성 | ATR 기반, 좁은 손절 | 변동성 조절 필요 |
| 낮은 변동성 | Squeeze Breakout | 폭발 전 진입 준비 |
| 섹터 내 종목 | Pair Trading | 시장 중립 수익 |
