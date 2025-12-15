---
name: ls-securities-options
description: LS Securities (LS증권) xingAPI expert for KOSPI200 options trading system implementation. Covers real-time market data (OH0, OC0, OMG, FC0), options Greeks streaming, order execution (CFOAT series), and complete TR/Real data structure specifications. Designed for high-frequency intraday options trading with low-latency requirements.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, Options, LS-Securities, xingAPI, KOSPI200, Real-time, Korea]
dependencies: []
---

# ls-securities-options

LS Securities (LS증권) xingAPI expert for KOSPI200 options trading system implementation.

## Description

Expert-level knowledge for building production-grade KOSPI200 options trading systems using LS Securities xingAPI. Covers real-time market data (OH0, OC0, OMG, FC0), options Greeks streaming, order execution (CFOAT series), and complete TR/Real data structure specifications. Designed for high-frequency intraday options trading with low-latency requirements.

## Activation Triggers

- LS증권 xingAPI 옵션 시스템
- KOSPI200 옵션 실시간 시세
- 옵션 그릭스 스트리밍 (델타, 감마, 세타, 베가)
- xingAPI Real/TR 데이터 구조
- LS증권 선물옵션 주문 체결
- 옵션호가잔량 OH0
- 옵션체결 OC0, 옵션민감도 OMG

## Level Loading

```yaml
L1_TRIGGER: "Basic xingAPI concepts, Real/TR codes overview"
L2_TRIGGER: "Complete data structures, field specifications"
L3_TRIGGER: "Production system architecture, order management"
```

## L1: Core Concepts (~50 tokens)

### LS증권 xingAPI Real-time Codes

| Real Code | Name | Description | Key Fields |
|-----------|------|-------------|------------|
| **OH0** | KOSPI200옵션호가 | 옵션 호가잔량 | offerho1~5, bidho1~5, offerrem1~5, bidrem1~5 |
| **OC0** | KOSPI200옵션체결 | 옵션 체결 시세 | price, volume, impv, theoryprice, timevalue |
| **OMG** | KOSPI200옵션민감도 | 옵션 Greeks | delt, gama, ceta, vega, rhox |
| **FC0** | KOSPI200선물체결 | 선물 체결 시세 | price, volume, kasis, sbasis, ibasis |

### LS증권 xingAPI TR Codes

| TR Code | Name | Size | Description |
|---------|------|------|-------------|
| **t2301** | 옵션현재가 | - | 옵션 시세 조회 |
| **t8414** | 선물옵션틱차트 | - | 틱봉 데이터 |
| **t8415** | 선물옵션분차트 | - | 분봉 데이터 |
| **CFOAT00100** | 선물옵션정상주문 | - | 신규 주문 |
| **CFOAT00200** | 선물옵션정정주문 | - | 주문 정정 |
| **CFOAT00300** | 선물옵션취소주문 | - | 주문 취소 |
| **C01** | 선물주문체결 | 261 | 체결 통보 |
| **H01** | 선물주문정정취소 | 316 | 정정/취소 통보 |
| **O01** | 선물접수 | 1141 | 주문 접수 상세 |

### COM Object Structure
```python
# Session
XA_Session.XASession → ConnectServer → Login

# Real-time data
XA_Real.XAReal → LoadFromResFile → AdviseRealData

# TR Query
XAQuery.XAQuery → LoadFromResFile → SetFieldData → Request
```

→ Load L2 for complete field specifications
