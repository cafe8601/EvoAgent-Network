# 🤖 Part 5: 도메인 스페셜리스트 (Specialists)

> **"특정 영역의 마스터: 트레이딩부터 블록체인, 풀스택 개발까지"**
>
> 이 가이드북은 특정 도메인에 깊이 특화된 고급 스킬들을 다룹니다. 금융(20, 26), 멀티에이전트(21), 블록체인(22), 그리고 웹 개발 아키텍처(23, 24, 25)를 포함합니다.

---

## 📑 목차
- [20. Trading (알고리즘 트레이딩)](#20-trading-알고리즘-트레이딩)
- [21. Multi-Agent Learning System (멀티에이전트 시스템)](#21-multi-agent-learning-system-멀티에이전트-학습-시스템)
- [22. Blockchain Agent Security (블록체인 보안)](#22-blockchain-agent-security-블록체인-에이전트-보안)
- [23. Frontend Design Architect (프론트엔드)](#23-frontend-design-architect-프론트엔드-디자인-아키텍트)
- [24. Spec-Driven Planner (명세 주도 개발)](#24-spec-driven-planner-명세-주도-개발)
- [25. Backend Architect (백엔드)](#25-backend-architect-백엔드-아키텍트)
- [26. Investment & Trading Systems (종합 투자 시스템)](#26-investment--trading-systems-종합-투자-시스템)
- [⬅️ 메인으로 돌아가기](./GUIDEBOOK_INDEX.md)

---

## 20. Trading (알고리즘 트레이딩)

### 📖 설명
암호화폐 및 주식 시장에서 알고리즘 트레이딩, 백테스팅, 강화학습 기반 트레이딩을 수행하기 위한 기술입니다.

### 🎯 언제 사용하나요?
- 트레이딩 전략(이동평균, RSI 등)을 과거 데이터로 검증(백테스트)할 때
- 거래소 API(Binance, Upbit, Alpaca)를 연동하여 자동 매매를 할 때
- 강화학습(RL) 에이전트가 스스로 트레이딩을 학습하게 할 때
- 한국 시장(키움, LS증권)에 특화된 매매 시스템을 구축할 때

### 📦 핵심 도구

**🌍 글로벌 트레이딩:**
| 도구 | 설명 | 용도 |
|------|------|------|
| **Backtrader** | 파이썬 이벤트 기반 백테스팅 | 전략 검증의 표준 |
| **VectorBT** | 고성능 벡터화 백테스팅 | 초고속 파라미터 최적화 |
| **CCXT** | 100+ 암호화폐 거래소 통합 | 표준화된 거래소 API |
| **FinRL** | 금융 강화학습 프레임워크 | PPO, DQN 등 RL 에이전트 학습 |
| **Freqtrade** | 암호화폐 자동매매 봇 | ML 시그널 통합, 하이퍼옵트 |

**🇰🇷 한국 시장 특화:**
| 도구 | 설명 | 용도 |
|------|------|------|
| **키움 OpenAPI+** | 국내 1위 증권사 API | 주식/선물/옵션 실시간 매매 |
| **LS증권 xingAPI** | LS증권 실시간 데이터/주문 | 옵션 그릭스 스트리밍, 저지연 매매 |
| **KOSPI200 Derivatives** | 선물/옵션/위클리옵션 전문 | ATM/OTM 전략, Greeks 헤지 |
| **Options Backtesting** | 옵션 전략 백테스팅 엔진 | Grid/GA 최적화, 멀티레그 전략 |
| **Realtime Trading System** | 멀티프로세스 아키텍처 | Receiver→Strategy→Trader 파이프라인 |

**📊 LS증권 xingAPI Real-time Codes:**
| Real Code | 설명 | 주요 필드 |
|-----------|------|----------|
| **OH0** | 옵션 5단계 호가잔량 | offerho1~5, bidho1~5 |
| **OC0** | 옵션 체결 (IV, 이론가) | price, impv, theoryprice |
| **OMG** | 옵션 그릭스 | delt, gama, ceta, vega, rhox |
| **FC0** | 선물 체결 (베이시스) | price, kasis, sbasis |

### 💡 사용 예시 프롬프트

```markdown
🔹 시나리오 1: 백테스팅
"Backtrader로 골든크로스(SMA 20/50) 전략을 구현하고
지난 2년치 비트코인 1시간 봉 데이터로 백테스트를 돌려줘."

🔹 시나리오 2: 초고속 파라미터 최적화
"VectorBT를 사용해서 RSI 기간(10~30)과 매수/매도 임계값의
모든 조합을 그리드 서치로 테스트하고, 최적의 파라미터를 찾아줘."

🔹 시나리오 3: 강화학습 에이전트
"FinRL 라이브러리로 다우존스 30 종목을 포트폴리오로 구성하여
자동으로 리밸런싱하는 A2C 에이전트를 학습시켜줘."

🔹 시나리오 4: 실시간 차익거래
"CCXT로 바이낸스와 코인베이스의 BTC 가격을 실시간 모니터링하다가
1% 이상 차이가 나면 알림을 보내는 봇을 만들어줘."

🔹 시나리오 5: 키움 OpenAPI+ 옵션 자동매매 🇰🇷
"키움 OpenAPI+로 KOSPI200 옵션 ATM 콜/풋을 실시간 수신하고
6단계 분할익절 + 추적손절 전략을 구현해줘."

🔹 시나리오 6: LS증권 그릭스 기반 트레이딩 🇰🇷
"LS증권 xingAPI로 OMG(옵션 그릭스)를 스트리밍 수신하고,
델타 중립 스프레드 진입 전략을 구현해줘. OH0 호가와 OC0 체결도 연동해줘."

🔹 시나리오 7: 위클리옵션 세타 수익 전략 🇰🇷
"위클리옵션 만기 2-3일 전에 진입하여 세타(시간가치) 수익을 얻는 전략을
백테스팅하고, 만기일 자동 청산 로직도 추가해줘."

🔹 시나리오 8: 멀티프로세스 실시간 매매 시스템 🇰🇷
"Receiver→Strategy→Trader 파이프라인으로 멀티프로세스 기반
KOSPI200 선물옵션 자동매매 시스템을 구축해줘. Telegram 알림도 포함해줘."
```

---

## 21. Multi-Agent Learning System (멀티에이전트 학습 시스템)

### 📖 설명
수십~수백 개의 전문 에이전트가 협력하고, 실행 결과를 학습하여 스스로 발전하는 오케스트레이션 시스템입니다. 154+ 에이전트 풀과 3-Tier 메모리 시스템을 포함합니다.

### 🎯 언제 사용하나요?
- 복잡한 프로젝트를 기획, 디자인, 개발, 테스트 에이전트로 분업화할 때
- 에이전트의 이전 성공/실패 경험을 기억하고 다음 작업에 반영하고 싶을 때
- 수많은 전문 에이전트 중 가장 적합한 전문가를 자동으로 선발(Routing)할 때
- 중앙화된 기억(Memory) 저장소를 구축하여 에이전트 간 맥락을 공유할 때

### 📦 핵심 도구
| 컴포넌트 | 역할 |
|----------|------|
| **AgentPoolManager** | 154+ 전문 에이전트의 생명주기 관리 |
| **IntelligentRouter** | 작업 내용을 분석해 최적의 에이전트 연결 |
| **LearningManager** | 실행 결과와 피드백을 학습하여 라우팅 개선 |
| **MemoryManager** | 단기/장기/에피소드 메모리 통합 관리 |

### 💡 사용 예시 프롬프트

```markdown
🔹 시나리오 1: 지능형 라우팅
"사용자의 요청이 '웹사이트 속도 개선'일 때, Agent Pool에서
FrontendExpert, PerformanceEngineer 에이전트를 자동 선발하는 로직을 보여줘."

🔹 시나리오 2: 경험 학습
"LearningManager를 통해 에이전트가 코드 리뷰를 수행한 후,
사용자의 피드백(좋음/나쁨)을 저장하고 다음 리뷰 품질을 높이는 방법을 구현해줘."

🔹 시나리오 3: 3-Tier 메모리
"MemoryManager를 사용하여 현재 대화(Short-term)와
프로젝트 전체 문맥(Long-term)을 에이전트가 동시에 참조하도록 설정해줘."
```

---

## 22. Blockchain Agent Security (블록체인 에이전트 보안)

### 📖 설명
AI 에이전트의 신원을 블록체인(DID)에 등록하고, 평판(Reputation)을 온체인으로 관리하며, 작업 수행 자격을 검증하는 보안 기술입니다. ZK Proof를 통해 프라이버시를 보호하면서 자격을 증명하고, LayerZero를 통해 크로스체인 신원을 동기화합니다.

### 🎯 언제 사용하나요?
- 여러 회사의 에이전트가 서로 신뢰하고 협업해야 할 때
- 에이전트의 위변조를 방지하고 고유한 ID를 부여하고 싶을 때
- 에이전트의 작업 이력을 투명하게 기록하여 평판 시스템을 만들 때
- 금융 거래를 수행하는 에이전트에게 높은 보안 수준의 자격을 부여할 때
- 여러 체인(Ethereum, Arbitrum, Base)에서 동일한 에이전트 신원을 사용할 때

### 📦 핵심 도구

**🔐 신원 및 자격 관리:**
| 도구/개념 | 설명 |
|-----------|------|
| **DID (Decentralized Identity)** | 탈중앙화 신원 증명 (ERC-725 기반) |
| **AgentIdentityRegistry** | 에이전트 DID 등록 스마트 컨트랙트 |
| **AgentReputationSystem** | 카테고리별 평판 점수 및 슬래싱 |
| **AgentCredentialVerifier** | ZK 기반 자격 검증 컨트랙트 |

**🔗 크로스체인 및 ZK:**
| 도구 | 설명 |
|------|------|
| **Circom** | ZK 회로 정의 언어 (영지식 증명 생성) |
| **snarkjs** | Groth16 증명 생성/검증 라이브러리 |
| **LayerZero V2** | 크로스체인 메시지 프로토콜 |
| **CrossChainAgentBridge** | 멀티체인 신원 동기화 컨트랙트 |

**🛡️ 보안 패턴:**
| 패턴 | 설명 |
|------|------|
| **Circuit Breaker** | 연속 실패 시 자동 차단 (CLOSED → OPEN → HALF_OPEN) |
| **Timelock Multi-Sig** | 중요 업그레이드에 대한 시간 지연 다중 서명 |
| **Slashing Mechanism** | 위반 시 스테이크 차감 (MINOR 5% → CRITICAL 50%) |

### 🔧 ZK Circuit 예시 (Circom)

에이전트가 **자격 정보를 공개하지 않고** 특정 신뢰 수준을 만족함을 증명하는 회로:

```circom
// AgentCapabilityProof.circom
template AgentCapabilityProof() {
    signal input nullifier;           // Public: 재사용 방지
    signal input capabilityCommitment; // Public: 자격 커밋먼트
    signal input minTrustLevel;        // Public: 최소 신뢰 수준
    
    signal input agentId;              // Private: 에이전트 ID
    signal input trustLevel;           // Private: 실제 신뢰 수준
    signal input credentialSecret;     // Private: 비밀 키
    
    // 신뢰 수준이 최소 요구치 이상인지 검증
    component trustCheck = GreaterEqThan(8);
    trustCheck.in[0] <== trustLevel;
    trustCheck.in[1] <== minTrustLevel;
    trustCheck.out === 1;
}
```

### 💡 사용 예시 프롬프트

```markdown
🔹 시나리오 1: 에이전트 신원 등록
"Ethereum 테스트넷에 AgentIdentityRegistry 컨트랙트를 배포하고,
내 에이전트의 DID를 등록하는 과정을 보여줘. 복구 주소도 설정해줘."

🔹 시나리오 2: 평판 기반 작업 할당
"에이전트의 온체인 평판 점수가 100점 이상인 경우에만
중요한 금융 분석 작업을 할당하는 스마트 컨트랙트 로직을 작성해줘."

🔹 시나리오 3: ZK 자격 증명
"Circom으로 에이전트 자격 증명 회로를 작성하고,
snarkjs로 증명을 생성한 후 온체인에서 검증하는 전체 플로우를 구현해줘."

🔹 시나리오 4: 크로스체인 신원 동기화
"LayerZero V2를 사용하여 Ethereum의 에이전트 평판을
Arbitrum과 Base에 동기화하는 CrossChainAgentBridge를 구현해줘."

🔹 시나리오 5: Circuit Breaker 패턴
"에이전트가 5회 연속 실패하면 자동으로 차단되고,
1시간 후 HALF_OPEN 상태로 전환되는 CircuitBreaker 컨트랙트를 작성해줘."
```

---

## 23. Frontend Design Architect (프론트엔드 디자인 아키텍트)

### 📖 설명
대규모 웹 애플리케이션의 디자인 시스템, CSS 아키텍처, 컴포넌트 설계를 전문적으로 수행하는 스킬입니다. 심미성과 유지보수성을 모두 잡습니다.

### 🎯 언제 사용하나요?
- 일관된 브랜드 경험을 위한 디자인 시스템(Design Tokens)을 구축할 때
- Tailwind CSS, Styled Components 등을 체계적으로 도입할 때
- 웹 접근성(A11y)과 반응형 디자인을 고려한 컴포넌트를 설계할 때
- 프론트엔드 성능 최적화(Lighthouse 점수 개선)가 필요할 때

### 📦 핵심 도구
| 도구 | 설명 |
|------|------|
| **Design Tokens** | 색상, 간격, 폰트 등을 변수화하여 관리 |
| **Atomic Design** | Atom -> Molecule -> Organism 구조론 |
| **Storybook** | 컴포넌트 문서화 및 테스트 도구 |
| **Tailwind CSS** | 유틸리티 퍼스트 CSS 프레임워크 |

### 💡 사용 예시 프롬프트

```markdown
🔹 시나리오 1: 디자인 토큰 시스템
"Figma 디자인 토큰(JSON)을 자동으로 CSS 변수나
Tailwind 설정 파일로 변환하는 파이프라인을 구축해줘."

🔹 시나리오 2: 아토믹 디자인 적용
"쇼핑몰의 '상품 카드' UI를 Atomic Design 원칙에 따라
Atom(이미지, 텍스트), Molecule(카드 본체)로 분해해서 React로 구현해줘."

🔹 시나리오 3: 접근성 개선
"WCAG 2.1 기준을 만족하도록 색상 명도비를 검사하고,
스크린 리더가 읽기 좋은 시멘틱 마크업으로 리팩토링하는 팁을 알려줘."
```

---

## 24. Spec-Driven Planner (명세 주도 개발)

### 📖 설명
"생각하고 코딩한다"는 철학 아래, 개발 전 명세(Spec)와 계획(Plan)을 완벽하게 수립하는 방법론입니다. GitHub Spec Kit을 기반으로 합니다.

### 🎯 언제 사용하나요?
- 복잡한 기능을 구현하기 전, 요구사항을 명확히 정리하고 싶을 때
- `spec.md`, `plan.md`, `tasks.md` 문서를 통해 체계적으로 개발할 때
- AI 에이전트에게 명확한 지시를 내리기 위해 컨텍스트를 문서화할 때
- 팀원 간의 커뮤니케이션 비용을 줄이고 싶을 때

### 📦 핵심 구성요소
| 파일 | 역할 |
|------|------|
| **constitution.md** | 프로젝트의 핵심 원칙과 절대 타협하지 않는 규칙 |
| **spec.md** | 기능의 상세 요구사항, 엣지 케이스, 데이터 구조 정의 |
| **plan.md** | 구현 단계(Phase)와 검증 계획 수립 |
| **tasks.md** | 개발자가 실행할 구체적인 투두 리스트 |

### 💡 사용 예시 프롬프트

```markdown
🔹 시나리오 1: Spec 작성
"새로운 '사용자 알림 센터' 기능을 위한 spec.md를 작성해줘.
기능 요구사항, 데이터베이스 스키마, 발생 가능한 에러 케이스를 포함해줘."

🔹 시나리오 2: Plan 수립
"작성된 spec.md를 바탕으로, 프론트엔드와 백엔드를 나누어 개발하는
단계별 plan.md를 만들어줘. 각 단계의 완료 조건도 명시해줘."

🔹 시나리오 3: Task 분해
"plan.md의 첫 번째 단계인 'API 개발'을
구체적인 단위 작업(tasks.md)으로 잘게 쪼개줘. (예: [ ] DB 마이그레이션 생성)"
```

---

## 25. Backend Architect (백엔드 아키텍트)

### 📖 설명
프로덕션급 백엔드 시스템을 설계하고 구현합니다. Clean Architecture부터 보안, 배포, API 설계까지 백엔드의 모든 것을 다룹니다.

### 🎯 언제 사용하나요?
- 유지보수가 쉬운 클린 아키텍처(Layered Architecture)를 도입할 때
- REST API, GraphQL, gRPC 등 적절한 API 통신 방식을 설계할 때
- OWASP Top 10 보안 취약점을 예방하는 코드를 작성할 때
- 대규모 트래픽을 처리하기 위한 데이터베이스 설계 및 캐싱 전략이 필요할 때

### 📦 핵심 도구
| 도구/패턴 | 설명 |
|-----------|------|
| **Clean Architecture** | 도메인 중심의 의존성 역전 설계 |
| **FastAPI / NestJS** | 현대적인 백엔드 프레임워크 |
| **PostgreSQL / Redis** | 신뢰성 높은 DB 및 캐시 |
| **Docker / K8s** | 컨테이너 기반 배포 |

### 💡 사용 예시 프롬프트

```markdown
🔹 시나리오 1: 클린 아키텍처 설계
"주문 처리 시스템을 Clean Architecture로 설계해줘.
Entity, Usecase, Controller, Repository 계층의 역할과 코드를 예시로 보여줘."

🔹 시나리오 2: API 보안 강화
"JWT 인증 방식에 Refresh Token Rotation을 적용하고,
API Rate Limiting을 추가하여 보안을 강화하는 로직을 구현해줘."

🔹 시나리오 3: DB 최적화
"수백만 건의 주문 데이터에서 특정 기간의 매출을 빠르게 조회하기 위한
인덱스 설계 전략과 파티셔닝 적용 방법을 알려줘."
```

---

## 26. Investment & Trading Systems (종합 투자 시스템)

### 📖 설명
단순 트레이딩을 넘어, 자산 배분(Asset Allocation), 리스크 관리(Risk Management), 다양한 자산군(주식, 외환, 코인)을 아우르는 종합 투자 시스템입니다. 자율 트레이딩 루프와 Multi-Model AI 합의 메커니즘을 통해 객관적인 매매 결정을 도출합니다.

### 🎯 언제 사용하나요?
- 단타 매매가 아닌 중장기 포트폴리오를 구성하고 관리할 때
- 주식, 채권, 현금 등 자산 배분 전략(All Weather 등)을 구현할 때
- 상관관계 분석을 통해 통계적 차익거래(Pair Trading)를 할 때
- 엄격한 리스크 관리 원칙(손절, 포지션 사이징)을 시스템에 적용할 때
- 다수의 AI 모델 합의를 통해 감정 배제된 매매 결정을 내릴 때

### 📦 핵심 도구

**🏦 트레이딩 플랫폼:**
| 도구 | 설명 |
|------|------|
| **NautilusTrader** | 고성능 이벤트 중심 트레이딩 플랫폼 (Rust 코어) |
| **Alpaca** | 미국 주식 Paper/Live 트레이딩 API (수수료 무료) |
| **Interactive Brokers (IBKR)** | 글로벌 선물/옵션/외환 브로커 (ib_insync) |

**📊 리스크 관리:**
| 지표 | 설명 | 목표 |
|------|------|------|
| **Sharpe Ratio** | 위험 조정 수익률 | > 1.5 |
| **Max Drawdown (MDD)** | 최대 낙폭 | < 15% |
| **Win Rate** | 승률 | > 55% |
| **Profit Factor** | 총이익/총손실 | > 1.5 |
| **거래당 리스크** | 포지션 사이징 기준 | 1-2% |

**🤖 자율 트레이딩 루프:**
```
┌─────────────────────────────────────────────────────────────┐
│                 AUTONOMOUS TRADING LOOP                      │
│                                                             │
│  09:00 AM: Pre-Market Screening (NASDAQ 100)                │
│     ↓                                                        │
│  09:30 AM: Multi-Model Analysis (5 AI models)               │
│     ↓                                                        │
│  Consensus (>70%) → Risk Check → Execute (Alpaca Paper)     │
│     ↓                                                        │
│  Real-time Telegram Notifications                            │
│     ↓                                                        │
│  04:00 PM: Daily P&L Summary, Model Leaderboard             │
└─────────────────────────────────────────────────────────────┘
```

**🧠 Multi-Model Consensus (5 AI 합의):**
```python
async def run_multi_model_analysis(ticker: str) -> dict:
    results = await asyncio.gather(
        claude_agent.analyze(ticker),
        gpt4_agent.analyze(ticker),
        gemini_agent.analyze(ticker),
        deepseek_agent.analyze(ticker),
        qwen_agent.analyze(ticker),
    )
    
    decisions = [r["decision"] for r in results]  # BUY, SELL, HOLD
    consensus_level = max(decisions.count(d)/len(decisions) for d in set(decisions))
    
    return {
        "ticker": ticker,
        "majority_decision": max(set(decisions), key=decisions.count),
        "consensus_level": consensus_level,
        "high_consensus": consensus_level >= 0.70  # 70% 이상 합의 시 실행
    }
```

### 💡 사용 예시 프롬프트

```markdown
🔹 시나리오 1: 포트폴리오 구성
"안정적 성장을 위한 'Moderate' 성향의 포트폴리오(주식 50, 채권 35, 현금 15)를
구성하고, 리밸런싱 규칙을 코드로 구현해줘."

🔹 시나리오 2: 통계적 차익거래 (Pair Trading)
"코카콜라(KO)와 펩시(PEP)의 주가 상관관계를 분석하고,
괴리율이 Z-score 2.0 이상 벌어졌을 때 진입하는 페어 트레이딩 전략을 만들어줘."

🔹 시나리오 3: 리스크 기반 포지션 사이징
"계좌 잔고가 $50,000이고 거래당 리스크를 1%로 제한할 때,
진입가와 손절가를 기준으로 몇 주를 매수해야 하는지 계산하는 함수를 짜줘."

🔹 시나리오 4: Multi-Model 자율 트레이딩
"Claude, GPT-4, Gemini, DeepSeek, Qwen 5개 모델이 동시에 분석하고,
70% 이상 합의된 경우에만 Alpaca Paper Trading으로 주문을 실행하는
자율 트레이딩 루프를 구현해줘. Telegram 알림도 추가해줘."

🔹 시나리오 5: 3-Way 리스크 토론
"Conservative, Aggressive, Neutral 세 관점의 에이전트가 각각 리스크를 평가하고,
최종 포지션 사이즈를 결정하는 3-Way Debate 패턴을 구현해줘."
```
