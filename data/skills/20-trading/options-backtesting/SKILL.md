---
name: options-backtesting
description: KOSPI200 Options Strategy Backtesting & Optimization Engine for multi-leg strategies with real-time Greeks. Supports all strategy types (straddle, strangle, spreads, condor, butterfly), pluggable exit conditions, OMG Greeks integration, Grid/Genetic optimization, walk-forward analysis. Designed for tick-level backtesting with accurate slippage modeling.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, Options, Backtesting, KOSPI200, Greeks, Optimization, Strategy]
dependencies: []
---

# options-backtesting

KOSPI200 Options Strategy Backtesting & Optimization Engine for multi-leg strategies with real-time Greeks.

## Description

Production-grade options backtesting framework supporting all strategy types (straddle, strangle, spreads, condor, butterfly). Features pluggable exit conditions, real-time OMG Greeks integration, Grid/Genetic optimization, walk-forward analysis, and strategy templates. Designed for tick-level backtesting with accurate slippage modeling.

## Activation Triggers

- KOSPI200 옵션 백테스팅
- 옵션 전략 최적화
- 스트래들/스트랭글 백테스트
- 멀티레그 옵션 전략
- Greeks 기반 청산 조건
- Grid Search / Genetic Algorithm 최적화
- Walk-forward 분석

## Level Loading

```yaml
L1_TRIGGER: "Strategy templates, basic backtesting concepts"
L2_TRIGGER: "Exit conditions, strategy builder, optimization"
L3_TRIGGER: "Custom strategy implementation, advanced optimization"
```

## L1: Core Concepts (~60 tokens)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    사용자 코드                           │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ 전략 템플릿  │  │ 커스텀 빌더  │  │ 직접 상속 구현  │  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
│         └────────────────┼──────────────────┘           │
│                          ▼                              │
│              ┌─────────────────────┐                    │
│              │ BaseUniversalStrategy│                    │
│              └──────────┬──────────┘                    │
│                         ▼                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │              UniversalOptionBacktestEngine        │  │
│  └──────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    데이터 계층                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
│  │  OC0    │  │  OMG    │  │  FC0    │                 │
│  │옵션체결  │  │옵션민감도│  │선물체결  │                 │
│  └─────────┘  └─────────┘  └─────────┘                 │
└─────────────────────────────────────────────────────────┘
```

### Supported Strategy Types

| Category | Strategies |
|----------|-----------|
| Single Leg | Long Call, Long Put, Short Call, Short Put |
| Straddle/Strangle | Long/Short Straddle, Long/Short Strangle |
| Vertical Spread | Bull Call, Bear Put, Bull Put, Bear Call |
| Complex | Iron Condor, Iron Butterfly, Long/Short Butterfly |
| Calendar | Calendar Spread, Diagonal Spread |

### Quick Start

```python
from backtesting_engine import (
    StrategyTemplateRegistry,
    UniversalOptionBacktestEngine,
)

# 1. 전략 선택 (템플릿 사용)
strategy = StrategyTemplateRegistry.create("long_straddle_conservative")

# 2. 엔진 생성
engine = UniversalOptionBacktestEngine(strategy)

# 3. 백테스트 실행
results = engine.run(market_snapshots)

# 4. 결과 확인
print(f"승률: {results['win_rate']:.1%}")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"MDD: {results['max_drawdown']:.1f}%")
```

### Available Templates

| Template | Description | Key Settings |
|----------|-------------|--------------|
| `long_straddle_conservative` | 보수적 | 10% 손절, R:R 1:1, 15분 보유 |
| `long_straddle_aggressive` | 공격적 | 30% 손절, R:R 1:3, 추적손절 |
| `long_straddle_iv_aware` | IV 인식 | IV 낮을 때 진입, IV Crush 청산 |
| `long_strangle` | 스트랭글 | OTM 콜+풋 매수 |
| `short_straddle` | 숏 스트래들 | IV 높을 때 진입 |
| `iron_condor` | 아이언 콘도르 | 4레그 제한손익 |
| `delta_neutral_straddle` | 델타 중립 | 델타 이탈 시 청산 |

→ Load L2 for exit conditions and optimization

