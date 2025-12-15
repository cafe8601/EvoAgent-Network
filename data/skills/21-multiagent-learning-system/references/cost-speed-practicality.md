# Cost-Speed-Practicality Guide for Multi-Agent Systems

## Overview

멀티에이전트 시스템의 비용, 속도, 실용성 최적화를 위한 포괄적인 가이드입니다.

---

## Part 1: 비용 최적화 (Cost Optimization)

### 1.1 LLM 호출 비용 계산

| 모델 | 입력 비용 (1M tokens) | 출력 비용 (1M tokens) | 에이전트 호출당 예상 비용 |
|------|---------------------|---------------------|----------------------|
| Claude 3.5 Sonnet | $3 | $15 | ~$0.02-0.10 |
| Claude 3 Opus | $15 | $75 | ~$0.10-0.50 |
| GPT-4 Turbo | $10 | $30 | ~$0.05-0.20 |
| GPT-4o | $5 | $15 | ~$0.03-0.15 |
| Gemini 1.5 Pro | $3.50 | $10.50 | ~$0.02-0.08 |
| Gemini 1.5 Flash | $0.35 | $0.53 | ~$0.002-0.01 |

### 1.2 멀티에이전트 비용 공식

```
총 비용 = Σ (에이전트_i × 호출_횟수_i × 평균_토큰_i × 토큰_비용)

예시: 3-에이전트 파이프라인 (Claude 3.5 Sonnet)
- Researcher: 1회 × 5k tokens = ~$0.03
- Analyst: 1회 × 8k tokens = ~$0.05
- Writer: 1회 × 10k tokens = ~$0.07
-----------------------------------
총 비용: ~$0.15/실행
```

### 1.3 비용 절감 전략

#### 전략 1: 모델 티어링

```python
# 비용 최적화 모델 선택
def select_model_for_task(task_type: str) -> str:
    if task_type in ["simple_query", "classification"]:
        return "gemini-1.5-flash"  # 가장 저렴
    elif task_type in ["code_generation", "analysis"]:
        return "claude-3-5-sonnet"  # 균형
    elif task_type in ["complex_reasoning", "critical_decision"]:
        return "claude-3-opus"  # 고품질 필요시만
```

#### 전략 2: 캐싱

```python
import hashlib
from functools import lru_cache

# 동일 프롬프트에 대한 응답 캐싱
@lru_cache(maxsize=1000)
def cached_agent_call(prompt_hash: str, agent_id: str):
    return agent.execute(prompt)

def execute_with_cache(prompt: str, agent_id: str):
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    return cached_agent_call(prompt_hash, agent_id)
```

#### 전략 3: 조기 종료

```python
# 충분한 품질 도달 시 조기 종료
def iterative_improvement(agent, task, max_iterations=5):
    result = agent.execute(task)
    
    for i in range(max_iterations):
        quality_score = evaluate_quality(result)
        
        if quality_score >= 0.9:  # 90% 품질이면 충분
            return result  # 조기 종료로 비용 절감
        
        result = agent.improve(result)
    
    return result
```

### 1.4 비용 추적 대시보드

```python
class CostTracker:
    def __init__(self):
        self.costs = []
        self.daily_budget = 10.0  # $10/day
    
    def record(self, agent_id: str, tokens_in: int, tokens_out: int, model: str):
        cost = self._calculate_cost(tokens_in, tokens_out, model)
        self.costs.append({
            "timestamp": datetime.now(),
            "agent": agent_id,
            "cost": cost
        })
        
        self._check_budget_alert()
    
    def _check_budget_alert(self):
        today_cost = sum(c["cost"] for c in self.costs 
                        if c["timestamp"].date() == date.today())
        
        if today_cost > self.daily_budget * 0.8:
            alert(f"⚠️ 일일 예산의 80% 사용: ${today_cost:.2f}")
```

---

## Part 2: 속도 최적화 (Speed Optimization)

### 2.1 병렬화 벤치마크

| 패턴 | 3 에이전트 | 5 에이전트 | 속도 향상 |
|------|----------|----------|----------|
| 순차 실행 | 30초 | 50초 | 1x (기준) |
| 병렬 실행 | 12초 | 15초 | **3-5x** |

### 2.2 4-Message 병렬 패턴 상세

```python
# Message 1: 준비 (Bash만)
await Bash("mkdir -p ai-docs")
await Bash("echo 'context' > ai-docs/context.md")
# ❌ Task 호출 금지 - 병렬화 파괴

# Message 2: 병렬 실행 (Task만)
# 모든 Task가 동시에 실행됨!
results = await asyncio.gather(
    Task(agent="researcher", prompt="Research topic A"),
    Task(agent="analyst", prompt="Analyze data B"),
    Task(agent="reviewer", prompt="Review code C"),
)
# 3개 에이전트가 동시 실행 = 3x 속도 향상

# Message 3: 통합
consolidated = await Task(
    agent="consolidator",
    prompt="Consolidate results from ai-docs/*.md"
)

# Message 4: 결과 제시
print(f"Completed: {consolidated}")
```

### 2.3 지연 분석 및 최적화

```python
import time
from dataclasses import dataclass

@dataclass
class LatencyMetrics:
    agent_execution: float  # 에이전트 실행 시간
    handoff_delay: float    # 에이전트 간 전환 시간
    queue_wait: float       # 대기열 대기 시간
    network_latency: float  # 네트워크 지연

def analyze_workflow_latency(workflow_id: str) -> LatencyMetrics:
    events = get_workflow_events(workflow_id)
    
    # 병목 지점 식별
    bottlenecks = identify_bottlenecks(events)
    
    if bottlenecks:
        print(f"🔴 병목 발견:")
        for b in bottlenecks:
            print(f"  - {b.agent}: {b.delay}s (예상: {b.expected}s)")
    
    return calculate_metrics(events)
```

### 2.4 비동기 에이전트 풀

```python
import asyncio
from asyncio import Semaphore

class AsyncAgentPool:
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = Semaphore(max_concurrent)
        self.agents = {}
    
    async def execute_parallel(self, tasks: list) -> list:
        async def run_with_limit(task):
            async with self.semaphore:
                return await self._execute(task)
        
        # 모든 태스크 동시 실행 (최대 5개)
        return await asyncio.gather(
            *[run_with_limit(t) for t in tasks]
        )
    
    async def _execute(self, task):
        agent = self.agents.get(task.agent_id)
        return await agent.execute(task.prompt)
```

---

## Part 3: 실용성 최적화 (Practicality)

### 3.1 점진적 복잡성 도입

```
Level 0: 단일 에이전트
         ↓ 한계 도달 시
Level 1: 2-에이전트 파이프라인 (실행자 + 검토자)
         ↓ 품질 요구 증가 시
Level 2: 전문화된 팀 (3-4 에이전트)
         ↓ 복잡한 워크플로우 필요 시
Level 3: 동적 오케스트레이션 (5+ 에이전트)
```

### 3.2 최소 실행 가능 멀티에이전트 (MVMA)

```python
# 가장 단순한 멀티에이전트 패턴
class MinimalMultiAgent:
    def __init__(self):
        self.executor = Agent(name="executor")
        self.reviewer = Agent(name="reviewer")
    
    def execute(self, task: str) -> str:
        # Step 1: 실행
        result = self.executor.run(task)
        
        # Step 2: 검토
        review = self.reviewer.run(f"Review: {result}")
        
        # Step 3: 검토 반영 여부 결정
        if "PASS" in review:
            return result
        else:
            # 피드백 반영하여 재실행
            return self.executor.run(f"{task}\n\nFeedback: {review}")
```

### 3.3 에이전트 요구사항 체크리스트

```
□ 이 작업에 정말 멀티에이전트가 필요한가?
  □ 단일 에이전트로 시도해봤는가?
  □ 단일 에이전트의 한계가 명확한가?

□ 에이전트 수를 최소화했는가?
  □ 각 에이전트의 역할이 명확한가?
  □ 역할 중복이 없는가?

□ 비용을 계산했는가?
  □ 예상 LLM 호출 횟수는?
  □ 일일/월간 비용 예산 내인가?

□ 실패 처리를 고려했는가?
  □ 한 에이전트 실패 시 전체가 실패하는가?
  □ 재시도/폴백 전략이 있는가?

□ 디버깅 가능한가?
  □ 각 에이전트의 입출력을 로깅하는가?
  □ 문제 발생 시 추적 가능한가?
```

### 3.4 워크플로우 템플릿

#### 템플릿 1: 코드 생성 + 검토

```python
class CodeGenWorkflow:
    """가장 일반적인 2-에이전트 패턴"""
    
    def execute(self, requirement: str) -> dict:
        # 1. 코드 생성
        code = self.coder.generate(requirement)
        
        # 2. 검토
        review = self.reviewer.review(code)
        
        # 3. 수정 필요시 반복 (최대 3회)
        for i in range(3):
            if review.score >= 0.9:
                break
            code = self.coder.improve(code, review.feedback)
            review = self.reviewer.review(code)
        
        return {"code": code, "review": review, "iterations": i + 1}
```

#### 템플릿 2: 병렬 검증

```python
class ParallelValidationWorkflow:
    """3개 관점에서 동시 검증"""
    
    async def execute(self, artifact: str) -> dict:
        # 병렬 검증 (3x 속도 향상)
        results = await asyncio.gather(
            self.security_reviewer.check(artifact),
            self.performance_tester.test(artifact),
            self.code_quality_checker.analyze(artifact),
        )
        
        # 통합
        return {
            "security": results[0],
            "performance": results[1],
            "quality": results[2],
            "overall_pass": all(r.passed for r in results)
        }
```

#### 템플릿 3: 연구 파이프라인

```python
class ResearchPipeline:
    """순차 연구 워크플로우"""
    
    def execute(self, topic: str) -> dict:
        # Sequential: 각 단계가 이전 결과에 의존
        
        # 1. 자료 수집
        sources = self.researcher.gather(topic)
        
        # 2. 분석
        analysis = self.analyst.analyze(sources)
        
        # 3. 보고서 작성
        report = self.writer.write(analysis)
        
        # 4. 편집
        final = self.editor.polish(report)
        
        return {"report": final, "sources": sources}
```

---

## Part 4: 문제 해결 (Troubleshooting)

### 4.1 비용 폭증

**증상**: 예상보다 훨씬 높은 비용
**원인**: 무한 루프, 과도한 반복, 큰 컨텍스트
**해결**:
```python
# 비용 안전장치
MAX_ITERATIONS = 5
MAX_TOKENS_PER_CALL = 10000
DAILY_BUDGET = 10.0

def safe_execute(agent, task):
    if daily_cost() > DAILY_BUDGET:
        raise BudgetExceeded("일일 예산 초과")
    
    return agent.execute(task, max_tokens=MAX_TOKENS_PER_CALL)
```

### 4.2 속도 저하

**증상**: 병렬 실행인데 순차처럼 느림
**원인**: 도구 유형 혼합, 의존성 대기
**해결**:
```python
# ❌ 잘못된 병렬화
await TodoWrite(...)  # 이것이
await Task(...)       # 순차 실행을
await Task(...)       # 강제함

# ✅ 올바른 병렬화
await Bash("mkdir -p workspace")  # Message 1
# --- 메시지 경계 ---
await asyncio.gather(              # Message 2
    Task(...), Task(...), Task(...)
)
```

### 4.3 컨텍스트 오버플로우

**증상**: 에이전트가 이전 컨텍스트를 잊음
**원인**: 컨텍스트 윈도우 초과
**해결**:
```python
# 파일 기반 위임
write("ai-docs/context.md", large_context)
Task(agent, "Read ai-docs/context.md and summarize")

# 요약 반환
return "Summary: 3 key points. Details in ai-docs/full-report.md"
```

### 4.4 에이전트 선택 오류

**증상**: 잘못된 에이전트가 작업 수행
**원인**: 키워드 매칭 실패
**해결**:
```python
# 명시적 에이전트 지정
def route_task(task: str, explicit_agent: str = None):
    if explicit_agent:
        return explicit_agent
    
    # 폴백: 키워드 기반
    return keyword_based_selection(task)
```

---

## Part 5: 모범 사례 요약

### DO ✅

1. **단일 에이전트로 시작** - 복잡성은 나중에 추가
2. **병렬 실행 활용** - 독립 작업은 동시 실행
3. **파일 기반 위임** - 컨텍스트 오염 방지
4. **비용 추적** - 예산 초과 방지
5. **간략한 요약 반환** - 2-5문장으로 제한
6. **명시적 역할 정의** - 각 에이전트의 책임 명확화

### DON'T ❌

1. **에이전트 과다** - 2-3개로 시작
2. **도구 유형 혼합** - 병렬화 파괴
3. **인라인 긴 지시** - 컨텍스트 오염
4. **무한 반복** - 비용 폭증
5. **실패 처리 누락** - 전체 시스템 실패
6. **과도한 설계** - YAGNI 원칙 적용

---

## 빠른 참조: 비용 × 속도 × 실용성 매트릭스

| 시나리오 | 권장 패턴 | 비용 | 속도 | 복잡도 |
|---------|----------|------|------|--------|
| 간단한 작업 | 단일 에이전트 | $ | ⭐⭐⭐ | 낮음 |
| 코드 + 검토 | 2-에이전트 파이프라인 | $$ | ⭐⭐⭐ | 낮음 |
| 다중 검증 | 병렬 검증 | $$$ | ⭐⭐⭐⭐⭐ | 중간 |
| 연구 파이프라인 | 순차 전문화 | $$$ | ⭐⭐ | 중간 |
| 복잡한 시스템 | 동적 오케스트레이션 | $$$$ | ⭐⭐⭐⭐ | 높음 |
