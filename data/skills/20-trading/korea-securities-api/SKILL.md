---
name: korea-securities-api
description: Korean securities API expert for Kiwoom OpenAPI+ (키움 오픈API+) and LS Securities xingAPI (LS증권 xingAPI) implementation. Covers real-time market data, order execution, and automated trading on KOSPI/KOSDAQ, futures, and options markets. Use when implementing Korean broker API integration.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, API, Kiwoom, LS-Securities, Korea, Automation, Real-time]
dependencies: []
---

# korea-securities-api

Korean securities API expert for Kiwoom OpenAPI+ and LS Securities xingAPI implementation.

## Description

Expert-level knowledge for implementing trading systems using Korean broker APIs. Covers Kiwoom OpenAPI+ (키움 오픈API+) and LS Securities xingAPI (LS증권 xingAPI) for real-time market data, order execution, and automated trading on KOSPI/KOSDAQ, futures, and options markets.

## Activation Triggers

- Korean broker API implementation
- Kiwoom OpenAPI+, 키움 오픈API
- LS Securities xingAPI, LS증권 API
- KRX market data integration
- Korean stock/futures/options trading automation
- TR request implementation
- Real-time 시세 수신
- 자동매매 시스템 개발

## Level Loading

```yaml
L1_TRIGGER: "Basic API concepts, connection setup"
L2_TRIGGER: "TR requests, real-time data, order execution"
L3_TRIGGER: "Advanced patterns, multi-process architecture, production systems"
```

## L1: Core Concepts (~50 tokens)

### Kiwoom OpenAPI+ Architecture
- **OCX Control**: QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')
- **Connection**: CommConnect() → OnEventConnect callback
- **TR Request**: SetInputValue → CommRqData → OnReceiveTrData
- **Real-time**: SetRealReg → OnReceiveRealData
- **Order**: SendOrder/SendOrderFo → OnReceiveChejanData

### LS Securities xingAPI Architecture
- **COM Objects**: XA_Session, XA_Real, XAQuery.XAQuery
- **Connection**: ConnectServer → Login → OnLogin callback
- **TR Request**: SetFieldData → Request → OnReceiveData
- **Real-time**: AdviseRealData → OnReceiveRealData
- **Server**: demo.ls-sec.co.kr (모의) / api.ls-sec.co.kr (실거래)

### Key Differences
| Feature | Kiwoom | LS Securities |
|---------|--------|---------------|
| Interface | ActiveX (QAxWidget) | COM (win32com.client) |
| TR Spec | .enc/.dat files | .res files |
| Auto Login | Manual COM automation | Built-in support |
| Rate Limit | 1 req/200ms (TR), 5/sec (order) | 1 req/200ms |

→ Load L2 for implementation patterns
