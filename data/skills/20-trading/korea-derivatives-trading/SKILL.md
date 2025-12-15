---
name: korea-derivatives-trading
description: Korean derivatives (futures, options, weekly options) trading expert for KOSPI200 derivatives on KRX market. Covers KOSPI200 futures (선물), options (옵션), weekly options (위클리옵션), mini derivatives, ATM/OTM/ITM strategies, Greeks management (델타, 감마, 베가, 세타), multi-level profit taking, trailing stop loss, and time-based position management.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, Derivatives, KOSPI200, Futures, Options, Greeks, Korea]
dependencies: []
---

# korea-derivatives-trading

Korean derivatives (futures, options, weekly options) trading expert for KOSPI200 derivatives.

## Description

Expert-level knowledge for trading Korean derivatives on KRX market. Covers KOSPI200 futures (선물), KOSPI200 options (옵션), weekly options (위클리옵션), and mini derivatives. Includes ATM/OTM/ITM strategies, Greeks management, multi-level profit taking, trailing stop loss, and time-based position management.

## Activation Triggers

- KOSPI200 futures/options trading
- 선물옵션 매매 시스템
- 위클리옵션 트레이딩
- Options Greeks (델타, 감마, 베가, 세타)
- ATM/OTM/ITM strategy
- 익절/손절 전략
- 만기일 포지션 관리
- 옵션 스프레드 전략

## Level Loading

```yaml
L1_TRIGGER: "Basic derivatives concepts, contract specs"
L2_TRIGGER: "Trading strategies, profit/loss management"
L3_TRIGGER: "Advanced strategies, Greeks hedging, production systems"
```

## L1: Core Concepts (~50 tokens)

### KOSPI200 Derivatives Contract Specs

| Product | Code Pattern | Multiplier | Tick Size | Tick Value |
|---------|--------------|------------|-----------|------------|
| KOSPI200 Futures | 101S6000 | 250,000원 | 0.05pt | 12,500원 |
| KOSPI200 Options | 201S6350 | 250,000원 | 0.01pt | 2,500원 |
| Mini Futures | 105S6000 | 50,000원 | 0.05pt | 2,500원 |
| Weekly Options | 209S6350 | 250,000원 | 0.01pt | 2,500원 |

### Option Code Structure
```
2 01 S 6 350
│ │  │ │ └─── 행사가 (350.00 = 35000/100)
│ │  │ └───── 월물 (1~9=1~9월, A,B,C=10,11,12월)
│ │  └─────── 콜/풋 (S=Call, T=Put)
│ └────────── 상품코드 (01=옵션, 09=위클리)
└──────────── 파생상품 (2=KOSPI200)
```

### Trading Hours (KST)
- **정규장**: 09:00 - 15:45
- **야간장**: 18:00 - 05:00 (다음날)
- **만기일**: 09:00 - 15:20 (옵션 최종거래)

### Key APIs
```python
# ATM 행사가 조회
atm = kiwoom.get_option_atm()  # Returns "350.00"

# 행사가 리스트
strikes = kiwoom.get_act_price_list()  # Returns "345.00;347.50;350.00;352.50;355.00"

# 옵션 코드 조회
code = kiwoom.get_option_code(month="6", strike=35000, option_type="2")  # Call
```

→ Load L2 for trading strategies
