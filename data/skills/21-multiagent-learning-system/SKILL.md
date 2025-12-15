---
name: multiagent-learning-system
description: Claude Code 환경에서 **실제로 작동하는** 멀티에이전트 오케스트레이션 가이드. 명확도 기반 판단으로 불필요한 에이전트 스폰 방지, 4가지 패턴(Sequential/Hierarchical/Peer/Swarm), 4-Message 병렬 실행, 파일 기반 위임 제공. CrewAI/LangGraph 참조 구현 포함.
version: 3.0.0
author: Orchestra Research
license: MIT
tags: [Multi-Agent, Orchestration, Cost-Optimization, Speed, Parallel-Execution, Learning System]
dependencies: [claude-agent-sdk>=0.1.0, anthropic>=0.30.0, crewai>=0.1.0, langgraph>=0.1.0]
---

# Multi-Agent Learning System v3.0

**비용, 속도, 실용성 중심**의 프로덕션급 멀티에이전트 오케스트레이션 플랫폼

## 핵심 원칙: 비용 × 속도 × 실용성

| 원칙 | 목표 | 달성 방법 |
|------|------|----------|
| **💰 비용 최적화** | LLM 호출 최소화 | 명확도 판단 + 단일 에이전트 우선 |
| **⚡ 속도 극대화** | 3-5x 빠른 실행 | 4-Message 병렬 패턴 (Claude Code) |
| **🎯 실용성 우선** | 즉시 적용 가능 | 명확도 체크 후 판단, 사전 질문 |

---

## 🧠 오케스트레이터 판단 가이드라인

**핵심**: 에이전트 스폰 전 **명확도 체크**로 불필요한 비용 방지

```
요청 도착
│
├─ 1. 컨텍스트 확인 (필요시)
│   └─ 프로젝트 구조, 이전 작업 파악 (Read, Serena memory)
│
├─ 2. 명확도 판단 (오케스트레이터가 직접)
│   │
│   ├─ 🟢 명확한 단일 작업?
│   │   예: "auth.js의 validateToken 함수 수정"
│   │   → 직접 실행 (Task 불필요)
│   │
│   ├─ 🟡 복잡하지만 이해 가능?
│   │   예: "로그인 시스템 구현해줘"
│   │   → Task 에이전트 위임 or 단계별 실행
│   │
│   └─ 🔴 불명확/모호?
│       예: "고쳐줘", "개선해줘"
│       → 사용자에게 질문 (에이전트 스폰 전!)
│
└─ 3. 실행 전략 선택
    ├─ 단순: 도구 직접 사용 (Read, Edit, Bash)
    ├─ 복잡 단일: Task 에이전트 1개
    └─ 복잡 병렬: 4-Message 패턴 (여러 Task)
```

### 💰 판단 가이드라인 효과

| 상황 | 잘못된 접근 | 올바른 접근 | 절감 |
|------|-----------|------------|------|
| "auth.js 수정" | Task 에이전트 스폰 | Edit 도구 직접 사용 | 1 LLM 호출 |
| "고쳐줘" | 추측해서 에이전트 스폰 | "무엇을 고칠까요?" 질문 | 2-5 LLM 호출 |
| "시스템 설계" | 바로 구현 시작 | 먼저 계획 후 병렬 실행 | 재작업 방지 |

### 명확도 체크리스트

```markdown
에이전트 스폰 전 자문:

□ 무엇을 해야 하는지 명확한가?
  - YES → 직접 실행 가능
  - NO → 질문하거나 컨텍스트 확인

□ 단일 작업인가, 여러 작업인가?
  - 단일 → 도구 직접 사용 or Task 1개
  - 여러 → 4-Message 병렬 패턴

□ 대상 파일/컴포넌트가 특정되었나?
  - YES → 바로 작업
  - NO → 먼저 파악 (Grep, Glob, Read)

□ 이전 작업과 연관있나?
  - YES → 컨텍스트 연결
  - NO → 새로 시작
```

### 실용적 예시

```python
# ❌ 과도한 설계 - 모든 요청에 에이전트 스폰
user_request = "버튼 색상 빨간색으로 변경"
Task(agent="ui-developer", prompt=user_request)  # 불필요!

# ✅ 현실적 - 단순 작업은 직접 처리
user_request = "버튼 색상 빨간색으로 변경"
# → Grep으로 버튼 찾기 → Edit으로 직접 수정

# ✅ 복잡한 작업만 위임
user_request = "결제 시스템 전체 구현"
Task(agent="backend-architect", prompt=user_request)  # 적절!
```

---

## 📊 Decision Framework: 단일 vs 멀티에이전트

```
작업 복잡도?
│
├─ 단순, 선형 → 🔵 단일 에이전트 (비용 최소)
│
├─ 복잡, 전문성 필요?
│  │
│  ├─ 순차적 단계 → Sequential Pipeline
│  ├─ 병렬 하위작업 → Hierarchical (3-5x 속도)
│  ├─ 검토 필요 → Peer Collaboration
│  └─ 솔루션 탐색 → Swarm Pattern
│
└─ 불확실 → 🔵 단일 에이전트로 시작, 필요시 멀티로 리팩터링
```

### ⚠️ 멀티에이전트 사용하지 말아야 할 때

| 상황 | 이유 | 대안 |
|------|------|------|
| 단일 에이전트가 처리 가능 | 불필요한 비용 | 단일 에이전트 |
| 작업이 단순하고 선형 | 조정 오버헤드 > 이점 | 단순 프롬프트 |
| 팀에 멀티에이전트 디버깅 경험 부족 | 유지보수 어려움 | 단일 에이전트 + 반복 |

---

## 🏗️ 4가지 멀티에이전트 패턴

### Pattern 1: Sequential Pipeline (순차 파이프라인)

**사용 시점**: 각 단계가 이전 결과에 의존

```
User Query → Researcher → Analyst → Writer → Editor → Output
```

**비용**: N 에이전트 = N LLM 호출 (순차)
**속도**: 병렬화 불가능 (의존성)
**실용성**: ⭐⭐⭐⭐⭐ 디버깅 용이, 명확한 흐름

```python
# CrewAI 구현
from crewai import Agent, Task, Crew

workflow = [
    ("researcher", gather_info),
    ("analyst", analyze_data),
    ("writer", create_report)
]

for agent_name, task in workflow:
    result = agents[agent_name].execute(task, context)
    context.update(result)  # 다음 에이전트에 전달
```

---

### Pattern 2: Hierarchical (Manager-Worker)

**사용 시점**: 병렬 처리 가능한 독립적 하위작업

```
              Manager Agent
              /     |     \
    Worker 1   Worker 2   Worker 3
    (Search)   (Analyze)  (Summarize)
              \     |     /
              Aggregator Agent
```

**비용**: N Workers + 2 (Manager + Aggregator)
**속도**: ⚡ **3-5x 빠름** (병렬 실행)
**실용성**: ⭐⭐⭐⭐ 조정 로직 필요

---

### Pattern 3: Peer Collaboration (라운드 테이블)

**사용 시점**: 여러 관점으로 품질 향상

```
Coder ↔ Reviewer ↔ Tester
  ↓        ↓        ↓
      Consensus
```

**비용**: ⚠️ 높음 (여러 LLM 호출 + 반복)
**속도**: 합의까지 반복 필요
**실용성**: ⭐⭐⭐ 고품질 필요시만 사용

---

### Pattern 4: Agent Swarm (에이전트 군집)

**사용 시점**: 다양한 솔루션 탐색

```
Agent 1 → Candidate Solution 1
Agent 2 → Candidate Solution 2
Agent 3 → Candidate Solution 3
   ↓
Selector (최선 선택)
```

**비용**: ⚠️ 매우 높음 (N 에이전트)
**속도**: 병렬 (빠름)
**실용성**: ⭐⭐ 창의적 브레인스토밍에만

---

## ⚡ 4-Message 병렬 실행 패턴 (3-5x 속도 향상)

**핵심**: 진정한 병렬 실행을 위해 **도구 유형을 분리**

> **참고**: 이 패턴은 Claude Code 환경 전용입니다.
> 다른 AI IDE(Cursor, Gemini CLI 등)에서는 순차 실행이 더 안정적입니다.

```
Message 1: 준비 (Bash만)
  - 작업 디렉토리 생성
  - 입력 검증
  - 컨텍스트 파일 작성
  - ❌ Task 호출 금지, ❌ TodoWrite 금지

Message 2: 병렬 실행 (Task만)
  - 모든 에이전트를 단일 메시지에서 시작
  - Task 도구만 사용
  - 모든 Task가 동시 실행됨 ✅

Message 3: 통합 (Task만)
  - 통합 에이전트 시작
  - N개 에이전트 완료 시 자동 트리거

Message 4: 결과 제시
  - 사용자에게 최종 결과 표시
```

### ❌ 안티패턴: 도구 유형 혼합 = 병렬화 파괴

```python
# ❌ 잘못됨 - 순차 실행됨:
await TodoWrite({...})  # Tool 1
await Task({...})       # Tool 2 - TodoWrite 대기
await Bash({...})       # Tool 3 - Task 대기
await Task({...})       # Tool 4 - Bash 대기

# ✅ 올바름 - 병렬 실행됨:
await Task({...})  # Task 1 ─┐
await Task({...})  # Task 2 ─┼─ 동시 실행!
await Task({...})  # Task 3 ─┘
```

---

## 💰 비용 최적화 전략

### 1. 에이전트별 토큰 추적

```python
class TrackedAgent(Agent):
    def execute(self, task, context):
        start = time.time()
        result = super().execute(task, context)
        
        metrics.record({
            "agent": self.name,
            "tokens": result.token_count,
            "cost": result.cost,  # 💰 비용 추적
            "duration": time.time() - start
        })
        return result
```

### 2. 컨텍스트 예산 관리

```
컨텍스트 예산: ~200k 토큰

현재 사용량:
  - 시스템 프롬프트: 10k
  - 스킬 콘텐츠: 10k
  - 대화 이력: 20k
  ─────────────────
  사용 중: 40k
  남은 것: 160k

위임 임계값: 작업이 >30k 토큰 소비 예상 시 → 위임
```

### 3. 파일 기반 위임 (50-80% 컨텍스트 절약)

```python
# ✅ 올바름 - 파일 기반:
# Step 1: 지시사항을 파일에 작성
write("ai-docs/requirements.md", detailed_requirements)

# Step 2: 파일 참조로 에이전트 호출
Task(
    agent="architect",
    prompt="Read ai-docs/requirements.md and create plan."
)

# Step 3: 에이전트는 간략한 요약만 반환
return "Plan complete. See ai-docs/architecture.md"

# ❌ 잘못됨 - 인라인 지시 (컨텍스트 오염):
Task(
    agent="architect",
    prompt="[500줄의 상세 요구사항...]"  # 오케스트레이터 컨텍스트 오염
)
```

### 4. 출력 크기별 전략

| 출력 크기 | 전략 |
|----------|------|
| < 1k 토큰 | 오케스트레이터에서 직접 실행 |
| 1k - 10k | 요약 반환으로 위임 |
| 10k - 30k | 파일 기반 출력으로 위임 |
| > 30k | 멀티에이전트 분해 |

---

## 🛠️ 실용적 구현 패턴

### CrewAI 구현 (역할 기반 팀)

```python
from crewai import Agent, Task, Crew

# 전문화된 에이전트 정의
researcher = Agent(
    role="Research Specialist",
    goal="Gather comprehensive information on {topic}",
    backstory="Expert researcher with 10 years experience",
    tools=[search_tool, scrape_tool]
)

analyst = Agent(
    role="Data Analyst",
    goal="Synthesize research findings into insights",
    tools=[analysis_tool]
)

# 의존성과 함께 태스크 정의
research_task = Task(
    description="Research {topic} thoroughly",
    agent=researcher,
    expected_output="Comprehensive research findings"
)

analysis_task = Task(
    description="Analyze research findings",
    agent=analyst,
    context=[research_task],  # 의존성 명시
    expected_output="Key insights and trends"
)

# Crew 생성 및 실행
crew = Crew(
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
    verbose=True
)

result = crew.kickoff(inputs={"topic": "AI market trends"})
```

### LangGraph 구현 (상태 머신)

```python
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    input: str
    research: str
    analysis: str
    output: str

def research_node(state):
    research = researcher_agent.run(state["input"])
    return {"research": research}

def analysis_node(state):
    analysis = analyst_agent.run(state["research"])
    return {"analysis": analysis}

# 그래프 구축
workflow = StateGraph(AgentState)
workflow.add_node("research", research_node)
workflow.add_node("analysis", analysis_node)

workflow.set_entry_point("research")
workflow.add_edge("research", "analysis")
workflow.add_edge("analysis", END)

app = workflow.compile()
result = app.invoke({"input": "Analyze AI market"})
```

---

## 📋 에이전트 선택 매트릭스

| 작업 유형 | 주요 에이전트 | 보조 에이전트 | 외부 옵션 |
|----------|-------------|--------------|----------|
| API 구현 | backend-developer | api-architect | - |
| UI 구현 | ui-developer | designer | codex |
| 테스팅 | test-architect | ui-manual-tester | - |
| 코드 리뷰 | senior-code-reviewer | - | grok, gemini |
| 아키텍처 | api-architect | - | - |
| 버그 조사 | codebase-detective | test-architect | - |

### 키워드 기반 자동 선택

```python
def select_agents(request: str) -> list:
    if any(kw in request for kw in ["API", "endpoint", "backend"]):
        return ["api-architect", "backend-developer"]
    elif any(kw in request for kw in ["UI", "component", "design"]):
        return ["designer", "ui-developer"]
    elif any(kw in request for kw in ["test", "coverage"]):
        return ["test-architect"]
    elif any(kw in request for kw in ["review", "validate"]):
        return ["senior-code-reviewer"]
    else:
        return ["generalist"]  # 기본 폴백
```

---

## 🚫 멀티에이전트 실수 Top 6

| 실수 | 결과 | 해결책 |
|------|------|--------|
| ❌ 에이전트 과다 | 비용 폭증 | 2-3개로 시작, 필요시만 추가 |
| ❌ 불명확한 책임 | 중복/누락 | 명시적 역할 정의 |
| ❌ 실패 처리 없음 | 전체 시스템 실패 | 재시도, 폴백, 스킵 |
| ❌ 동기 병목 | 속도 저하 | 독립 에이전트 병렬화 |
| ❌ 비용 무시 | 예산 초과 | N 에이전트 = N× LLM 비용 |
| ❌ 과도한 설계 | 유지보수 어려움 | 단일 에이전트로 충분한 경우 많음 |

---

## 📊 모니터링 & 디버깅

```python
# 에이전트 실행 추적
class TrackedAgent(Agent):
    def execute(self, task, context):
        start = time.time()
        logger.info(f"{self.name} 시작: {task}")
        
        result = super().execute(task, context)
        
        duration = time.time() - start
        logger.info(f"{self.name} 완료: {duration}s")
        
        metrics.record({
            "agent": self.name,
            "task": task,
            "duration": duration,
            "tokens": result.token_count,
            "cost": result.cost
        })
        
        return result
```

**핵심 메트릭**:
- 에이전트 실행 시간
- 에이전트당 토큰 사용량 💰
- 성공/실패율
- 핸드오프 지연
- 전체 워크플로우 시간

---

## 🎯 Quick Start (2분 셋업)

```python
# 최소 구현 - 단일 에이전트로 시작
from multiagent import SimpleAgent

agent = SimpleAgent(
    name="fullstack-developer",
    model="claude-3-5-sonnet-20241022"
)

result = agent.execute("Build REST API with auth")

# 필요시 멀티에이전트로 확장
if needs_review:
    reviewer = SimpleAgent(name="code-reviewer")
    review = reviewer.execute(f"Review: {result}")
```

---

## 🔧 Claude Code Tool Selection Hierarchy

Claude Code 환경에서 도구 선택 우선순위:

```
1. Task (Agent Delegation) → 복잡한 멀티스텝, 전문화된 분석
2. Bash (Shell Commands)   → 시스템 명령, 파일 시스템
3. Read/Write/Edit         → 파일 직접 조작
4. Grep/Glob               → 코드베이스 탐색
```

**Task 사용 적합**: 복잡한 분석, 전문 도메인, 병렬 실행 이점, 컨텍스트 격리
**Task 부적합**: 단순 파일 읽기(→Read), 빠른 명령(→Bash), 패턴 검색(→Grep)

→ 상세 오케스트레이션 패턴: [`references/orchestration-patterns.md`](references/orchestration-patterns.md)

---

## 🔗 Coordination & Efficiency (Claude Code 환경)

> **중요**: Claude Code에는 자동 로드 밸런싱/오토스케일링 API가 없습니다.
> 모든 조정은 **오케스트레이터의 판단**으로 이루어집니다.

### 실용적 조정 패턴
- **위임**: 복잡도/전문성 기반으로 Task 사용 여부 결정
- **핸드오프**: 파일 시스템 기반 컨텍스트 전달
- **동기화**: 단일 메시지 병렬 호출로 자연스럽게 처리
- **통신**: 파일 기반 (에이전트 간 직접 통신 불가)

→ 상세: [`references/coordination-primitives.md`](references/coordination-primitives.md)

### 충돌 해결 (오케스트레이터 판단)
- **우선순위**: 보안 > 설계 > 성능 > 구현
- **근거 기반**: 더 구체적인 근거를 제시한 에이전트 채택
- **에스컬레이션**: 비즈니스 결정은 사용자에게 질문

### 효율적 에이전트 활용
- **모델 선택**: opus(복잡) / sonnet(일반) / haiku(단순)
- **병렬화**: 독립 작업은 한 메시지에 여러 Task
- **직접 실행**: 단순 작업(Read, Grep)은 Task 불필요

→ 상세: [`references/load-balancing-scaling.md`](references/load-balancing-scaling.md)

---

## 📚 참조

**Core Levels**:
→ [`levels/L2.md`](levels/L2.md) - 상세 구현 패턴 (Memory, Learning, Workflow)
→ [`levels/L3.md`](levels/L3.md) - 고급 오케스트레이션 (Security, Circuit Breaker, Production)

**Reference Documentation**:
→ [`references/orchestration-patterns.md`](references/orchestration-patterns.md) - Claude Code 오케스트레이션
→ [`references/coordination-primitives.md`](references/coordination-primitives.md) - 조율, 통신, 충돌 해결
→ [`references/load-balancing-scaling.md`](references/load-balancing-scaling.md) - 부하 분산, 오토스케일링
→ [`references/practical-workflows.md`](references/practical-workflows.md) - 실용적 워크플로우 예제
→ [`references/cost-speed-practicality.md`](references/cost-speed-practicality.md) - 비용/속도/실용성 가이드

**관련 스킬**:
- `rag-implementer` - 지식 기반 에이전트
- `api-designer` - 에이전트 통신 API

---

**Version:** 3.0.0
**Dependencies:** crewai, langgraph, anthropic, claude-agent-sdk
**Complexity:** Advanced
**Output:** Smart Routing + 비용 최적화된 멀티에이전트 시스템
