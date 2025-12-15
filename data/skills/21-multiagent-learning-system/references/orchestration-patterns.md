# Claude Code 멀티에이전트 오케스트레이션 패턴

Claude Code Task tool에서 **실제로 작동하는** 오케스트레이션 패턴입니다.

---

## Claude Code Task Tool 실제 동작

### Task Tool의 실제 API

```yaml
Task tool parameters:
  subagent_type: string (필수) - 에이전트 유형
  prompt: string (필수) - 에이전트에게 전달할 지시
  description: string (필수) - 3-5 단어 설명
  run_in_background: boolean - 백그라운드 실행 여부
  model: "sonnet" | "opus" | "haiku" - 모델 선택
```

### 실제 가능한 것 vs 불가능한 것

| 가능 ✅ | 불가능 ❌ |
|---------|----------|
| 여러 Task를 한 메시지에 호출 (병렬) | 에이전트 간 직접 통신 |
| run_in_background로 백그라운드 실행 | 동적 에이전트 풀 관리 |
| AgentOutputTool로 결과 수집 | Auto-scaling API |
| 파일로 컨텍스트 공유 | 에이전트 상태 모니터링 API |
| 오케스트레이터가 결과 종합 | 로드 밸런싱 API |

---

## 병렬 실행 패턴 (실제 작동)

### 패턴 1: 단일 메시지 병렬 호출

**핵심**: 한 메시지에 여러 Task tool을 포함하면 병렬 실행됩니다.

```markdown
# 오케스트레이터가 한 번의 응답에서 여러 Task 호출:

[Task 1: backend-architect - API 설계 검토]
[Task 2: security-engineer - 보안 취약점 분석]
[Task 3: quality-engineer - 테스트 커버리지 검토]

→ 3개 에이전트가 동시에 실행됨
→ 모든 결과가 한번에 반환됨
```

### 패턴 2: 백그라운드 실행 + 결과 수집

```markdown
# Step 1: 백그라운드로 에이전트 실행
[Task: run_in_background=true] → agent_id 반환

# Step 2: 다른 작업 수행 (병렬로)
[직접 파일 읽기, 분석 등]

# Step 3: 결과 수집
[AgentOutputTool: agent_id로 결과 조회]
```

---

## 도구 선택 가이드라인 (오케스트레이터용)

### 언제 Task를 사용하는가?

```
Task 사용 ✅:
├─ 복잡한 분석 (3단계 이상)
├─ 전문 도메인 지식 필요
├─ 병렬 실행으로 시간 절약 가능
└─ 독립적인 서브태스크

Task 사용하지 않음 ❌:
├─ 단순 파일 읽기 → Read tool
├─ 간단한 검색 → Grep/Glob tool
├─ 1-2줄 수정 → Edit tool
└─ 단순 명령 실행 → Bash tool
```

### 도구 선택 우선순위

```
1순위: 전문 도구 (Read, Edit, Grep, Glob)
       → 빠름, 정확, 컨텍스트 효율적

2순위: Bash
       → 시스템 명령이 필요할 때만

3순위: Task (Agent Delegation)
       → 복잡한 분석, 전문 지식 필요시
       → 병렬 실행 이점이 있을 때
```

---

## 파일 기반 컨텍스트 공유 (핵심 패턴)

### 왜 파일 기반인가?

```
에이전트 간 직접 통신 불가능
→ 파일 시스템을 "공유 메모리"로 사용

장점:
- 컨텍스트 오염 방지 (프롬프트에 긴 내용 안 넣음)
- 결과 영속성 (세션 간 유지)
- 추적 가능 (파일로 남음)
```

### 실용적 워크플로우

```markdown
## Phase 1: 준비 (오케스트레이터)
1. mkdir -p ai-docs
2. Write: ai-docs/requirements.md (요구사항)
3. Write: ai-docs/context.md (분석할 코드/데이터)

## Phase 2: 병렬 분석 (에이전트들)
[Task 1] "Read ai-docs/context.md, write analysis to ai-docs/arch-review.md"
[Task 2] "Read ai-docs/context.md, write analysis to ai-docs/security-review.md"
[Task 3] "Read ai-docs/context.md, write analysis to ai-docs/perf-review.md"

## Phase 3: 통합 (오케스트레이터 또는 통합 에이전트)
Read: ai-docs/arch-review.md, security-review.md, perf-review.md
→ 종합 분석 수행
→ Write: ai-docs/final-report.md

## Phase 4: 정리
rm -rf ai-docs (필요시)
```

---

## 메시지 구조 최적화

### 병렬화 보장 규칙

```
❌ 잘못된 패턴 (병렬화 깨짐):
Message 1에서:
  - Bash 호출
  - Task 호출  ← 순차 실행됨
  - Task 호출  ← 순차 실행됨

✅ 올바른 패턴:
Message 1: 준비 작업만
  - Bash (mkdir, 환경 설정)
  - Write (컨텍스트 파일 생성)

Message 2: Task만
  - Task 1 ┐
  - Task 2 ├─ 병렬 실행!
  - Task 3 ┘

Message 3: 결과 처리
  - Read (결과 파일들)
  - 종합 분석
```

### 4-Message 패턴 (실전용)

```markdown
## Message 1: Setup
- 작업 디렉토리 생성
- 컨텍스트 파일 작성
- 에이전트에게 전달할 지시사항 파일 작성

## Message 2: Parallel Execution
- 여러 Task 동시 호출
- 각 에이전트는 파일 읽기 → 분석 → 파일 쓰기

## Message 3: Consolidation
- 결과 파일들 읽기
- 통합 분석 수행 (직접 또는 consolidator 에이전트)

## Message 4: Delivery
- 최종 결과 사용자에게 전달
- 임시 파일 정리
```

---

## 품질 게이트 (오케스트레이터 판단 기준)

### 단계 전환 전 체크리스트

에이전트 결과를 받은 후, 다음 단계로 넘어가기 전:

```markdown
□ 결과가 요청한 형식에 맞는가?
□ 필수 섹션이 모두 포함되어 있는가?
□ 명백한 오류나 모순이 없는가?
□ 다음 단계에 필요한 정보가 충분한가?

→ 모두 통과: 다음 단계 진행
→ 실패: 에이전트에게 피드백과 함께 재요청
```

### 재시도 패턴

```markdown
attempt = 1
max_attempts = 3

while attempt <= max_attempts:
    result = Task(agent, prompt)

    if quality_check(result):
        break  # 성공
    else:
        prompt = f"""
        이전 결과가 다음 이유로 부족합니다:
        {feedback}

        다시 시도해주세요. 특히 {specific_improvement}에 집중하세요.
        """
        attempt += 1

if attempt > max_attempts:
    # 폴백: 다른 에이전트 또는 수동 처리
```

---

## 에이전트 선택 가이드라인

### 사용 가능한 에이전트 유형 (Claude Code 내장)

```yaml
general-purpose: 범용 작업, 코드 검색, 멀티스텝 태스크
Explore: 코드베이스 탐색 (빠름)
Plan: 구현 계획 설계

backend-architect: 백엔드 시스템 설계
frontend-architect: 프론트엔드 UI 설계
system-architect: 시스템 아키텍처 설계

security-engineer: 보안 취약점 분석
quality-engineer: 테스트 전략, 품질 보증
performance-engineer: 성능 최적화

python-expert: Python 코드 전문가
refactoring-expert: 리팩토링, 기술 부채 감소

deep-research-agent: 종합 리서치
requirements-analyst: 요구사항 분석
technical-writer: 기술 문서 작성
```

### 태스크별 에이전트 매칭

```markdown
| 태스크 유형 | 권장 에이전트 |
|-------------|---------------|
| API 설계 검토 | backend-architect |
| UI 컴포넌트 설계 | frontend-architect |
| 보안 감사 | security-engineer |
| 코드 품질 검토 | quality-engineer |
| 성능 병목 분석 | performance-engineer |
| 코드베이스 탐색 | Explore (quick) |
| 구현 계획 | Plan |
| 심층 조사 | deep-research-agent |
```

---

## 안티패턴 (피해야 할 것)

### 1. 과도한 에이전트 사용

```markdown
❌ 나쁨:
for file in files:
    Task("Read and analyze {file}")  # 파일마다 에이전트!

✅ 좋음:
for file in files:
    Read(file)  # 직접 읽기
# 한번에 분석
Task("Analyze all these files: {summary}")
```

### 2. 인라인 컨텍스트 오염

```markdown
❌ 나쁨:
Task(prompt=f"Analyze this 5000-line code: {huge_code}")
# → 프롬프트가 거대해짐, 비효율적

✅ 좋음:
Write("ai-docs/code.md", huge_code)
Task(prompt="Read ai-docs/code.md and analyze. Return 2-3 sentence summary.")
# → 프롬프트 작음, 결과도 간결
```

### 3. 순차 실행 강제

```markdown
❌ 나쁨:
result1 = Task(agent1, task1)
result2 = Task(agent2, task2)  # 의존성 없는데 순차 실행
result3 = Task(agent3, task3)

✅ 좋음 (의존성 없으면):
# 한 메시지에서 병렬 호출
[Task agent1], [Task agent2], [Task agent3]
```

### 4. 품질 검증 누락

```markdown
❌ 나쁨:
result = Task(agent, task)
# 바로 다음 단계로...

✅ 좋음:
result = Task(agent, task)
# 결과 검증
if not meets_quality_bar(result):
    result = Task(agent, f"Improve: {feedback}")
```

---

## 실전 워크플로우 예시

### 코드 리뷰 워크플로우

```markdown
## 1. 준비
mkdir -p ai-docs
Write: ai-docs/code-to-review.md (대상 코드)

## 2. 병렬 분석 (한 메시지)
[Task: backend-architect] "Review architecture in ai-docs/code-to-review.md"
[Task: security-engineer] "Security audit of ai-docs/code-to-review.md"
[Task: quality-engineer] "Test coverage analysis of ai-docs/code-to-review.md"

## 3. 결과 수집
Read: 각 에이전트의 분석 결과

## 4. 종합 리뷰 작성
오케스트레이터가 모든 결과를 종합하여:
- 주요 발견사항
- 우선순위별 개선 권고
- 즉시 조치 필요 항목
```

### 기능 구현 워크플로우

```markdown
## 1. 요구사항 분석
[Task: requirements-analyst] "Clarify requirements for {feature}"

## 2. 설계 (병렬)
[Task: backend-architect] "Design backend for {feature}"
[Task: frontend-architect] "Design UI for {feature}"

## 3. 설계 검토
오케스트레이터가 두 설계의 일관성 검토
필요시 조정 요청

## 4. 구현 (병렬 가능한 부분)
직접 코드 작성 또는 에이전트 위임

## 5. 품질 검증
[Task: quality-engineer] "Review implementation"
[Task: security-engineer] "Security check"
```

---

## Quick Reference

```yaml
병렬 실행: 한 메시지에 여러 Task 포함
컨텍스트 공유: 파일 시스템 사용 (ai-docs/)
품질 게이트: 결과 검증 → 필요시 재요청
에이전트 선택: 태스크 복잡도와 도메인에 맞춰

도구 우선순위:
  1. Read/Edit/Write (파일 직접 조작)
  2. Grep/Glob (검색)
  3. Bash (시스템 명령)
  4. Task (복잡한 분석, 전문 지식)

피해야 할 것:
  - 단순 작업에 Task 사용
  - 프롬프트에 긴 컨텍스트 포함
  - 의존성 없는 Task 순차 실행
  - 결과 검증 없이 진행
```
