---
name: realtime-trading-system
description: Real-time automated trading system architecture expert for multi-process, queue-based trading implementations. Covers multi-process architecture (Receiver → Strategy → Trader), queue-based IPC, PyQt5 GUI integration, technical indicator calculation, order state management, and fault-tolerant system design. Applicable to Korean securities, crypto exchanges, and global markets.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Trading, Real-time, Architecture, Multi-process, Queue, Automation, Low-latency]
dependencies: []
---

# realtime-trading-system

Real-time automated trading system architecture expert for multi-process, queue-based trading implementations.

## Description

Expert-level knowledge for building production-grade real-time trading systems. Covers multi-process architecture (Receiver → Strategy → Trader), queue-based IPC, PyQt5 GUI integration, technical indicator calculation, order state management, and fault-tolerant system design. Applicable to Korean securities, crypto exchanges, and global markets.

## Activation Triggers

- 실시간 자동매매 시스템
- Multi-process trading architecture
- Queue-based IPC for trading
- PyQt5 trading GUI
- Real-time signal processing
- Order management system
- Trading bot architecture
- Low-latency trading system

## Level Loading

```yaml
L1_TRIGGER: "Basic architecture, process separation"
L2_TRIGGER: "Queue patterns, signal flow, order management"
L3_TRIGGER: "Fault tolerance, performance optimization, production deployment"
```

## L1: Core Concepts (~50 tokens)

### Multi-Process Architecture Pattern
```
┌─────────────────────────────────────────────────────────────────┐
│                        MAIN PROCESS (GUI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ windowQ  │  │ Position │  │  P&L     │  │  Logs    │        │
│  │ Consumer │  │  Table   │  │ Display  │  │  Panel   │        │
│  └────▲─────┘  └──────────┘  └──────────┘  └──────────┘        │
└───────│─────────────────────────────────────────────────────────┘
        │
        │ windowQ (display updates)
        │
┌───────│─────────────────────────────────────────────────────────┐
│       │            SUB-PROCESSES                                 │
│  ┌────┴─────┐  receiverQ   ┌──────────┐  traderQ  ┌──────────┐ │
│  │ RECEIVER │─────────────►│ STRATEGY │─────────►│  TRADER  │ │
│  │ Process  │              │  Process │◄─────────│  Process │ │
│  └──────────┘              └──────────┘ strategyQ └──────────┘ │
│       │                          │                      │       │
│       │ teleQ                    │ teleQ               │ teleQ  │
│       ▼                          ▼                      ▼       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    TELEGRAM BOT Process                      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Process Responsibilities
| Process | Role | Input Queue | Output Queue |
|---------|------|-------------|--------------|
| Receiver | Market data subscription | - | receiverQ, windowQ |
| Strategy | Signal generation | receiverQ, strategyQ | traderQ, windowQ, teleQ |
| Trader | Order execution | traderQ | strategyQ, windowQ, teleQ |
| Telegram | Notifications | teleQ | - |
| GUI | Display & control | windowQ | All processes |

### Queue Types
```python
from multiprocessing import Queue

# Standard queues
windowQ = Queue()     # GUI display updates
receiverQ = Queue()   # Market data → Strategy
traderQ = Queue()     # Strategy → Trader (orders)
strategyQ = Queue()   # Trader → Strategy (fills)
teleQ = Queue()       # All → Telegram notifications
queryQ = Queue()      # TR/API query requests
```

→ Load L2 for implementation patterns
