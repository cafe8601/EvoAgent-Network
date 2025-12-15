# Claude Code 에이전트 조정 패턴

Claude Code 환경에서 **실제로 구현 가능한** 에이전트 조정 패턴입니다.

> **핵심**: Claude Code는 에이전트 간 직접 통신을 지원하지 않습니다.
> 모든 조정은 **오케스트레이터(메인 Claude)**가 수행합니다.

---

## Claude Code의 조정 모델

### 실제 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    오케스트레이터                            │
│                   (메인 Claude)                             │
│                                                             │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐                   │
│   │ Task 1  │  │ Task 2  │  │ Task 3  │  ← 병렬 호출      │
│   └────┬────┘  └────┬────┘  └────┬────┘                   │
│        │            │            │                         │
│        ▼            ▼            ▼                         │
│   [결과 1]     [결과 2]     [결과 3]                       │
│        │            │            │                         │
│        └────────────┼────────────┘                         │
│                     ▼                                       │
│              오케스트레이터가                               │
│              결과 종합 & 다음 결정                          │
└─────────────────────────────────────────────────────────────┘
```

### 에이전트는 서로 모름

```
에이전트 A ──X──▶ 에이전트 B  (직접 통신 불가)

에이전트 A ──▶ 파일 ──▶ 에이전트 B  (파일로 간접 공유)
              ↑
         오케스트레이터가 관리
```

---

## 위임 패턴 (Delegation)

### 패턴 1: 직접 위임

오케스트레이터가 특정 에이전트를 지정하여 작업 할당:

```markdown
## 오케스트레이터 판단 기준

"이 작업은 보안 분석이 필요하다"
→ security-engineer 에이전트 선택

"이 작업은 API 설계가 필요하다"
→ backend-architect 에이전트 선택

## 실행
[Task: subagent_type="security-engineer", prompt="분석 요청"]
```

### 패턴 2: 능력 기반 위임

오케스트레이터가 작업 요구사항을 분석하여 적합한 에이전트 선택:

```markdown
## 오케스트레이터 판단 프로세스

작업: "React 컴포넌트의 성능 최적화"

필요 능력 분석:
- React 지식 → frontend-architect
- 성능 분석 → performance-engineer

결정: 두 에이전트 병렬 호출 또는 순차 호출

## 실행 옵션

옵션 A: 병렬 (독립적 관점)
[Task: frontend-architect] "React 구조 관점에서 분석"
[Task: performance-engineer] "성능 관점에서 분석"

옵션 B: 순차 (의존적)
[Task: performance-engineer] "병목 식별"
→ 결과 기반으로
[Task: frontend-architect] "식별된 병목 해결 방안"
```

### 패턴 3: 부하 고려 위임 (수동)

Claude Code에는 자동 로드 밸런싱이 없음. 오케스트레이터가 판단:

```markdown
## 오케스트레이터 고려사항

"이미 3개 에이전트가 실행 중"
"추가 에이전트 호출 시 응답 지연 가능"

결정:
- 긴급하면: 추가 호출
- 아니면: 현재 에이전트 결과 대기 후 진행
```

---

## 핸드오프 패턴 (Handoff)

### 패턴 1: 순차 핸드오프

한 에이전트의 결과를 다음 에이전트의 입력으로 사용:

```markdown
## 워크플로우

Step 1: 요구사항 분석
[Task: requirements-analyst]
"요구사항을 분석하고 ai-docs/requirements.md에 작성"

Step 2: 오케스트레이터가 결과 확인
Read: ai-docs/requirements.md
→ 품질 검증

Step 3: 설계
[Task: backend-architect]
"ai-docs/requirements.md를 읽고 API 설계를 ai-docs/api-design.md에 작성"

Step 4: 구현
[Task: python-expert]
"ai-docs/api-design.md를 읽고 구현"
```

### 패턴 2: 조건부 핸드오프

결과에 따라 다른 에이전트로 라우팅:

```markdown
## 오케스트레이터 판단

Step 1: 초기 분석
[Task: general-purpose] "문제 유형 분류"

Step 2: 결과에 따른 라우팅
결과가 "보안 이슈"면:
    → [Task: security-engineer]
결과가 "성능 이슈"면:
    → [Task: performance-engineer]
결과가 "설계 이슈"면:
    → [Task: backend-architect]
```

### 패턴 3: 폴백 핸드오프

실패 시 대안 에이전트로:

```markdown
## 오케스트레이터 로직

attempt = 1
while attempt <= 3:
    result = [Task: python-expert] "구현"

    if result가 충분하면:
        break
    else:
        # 피드백과 함께 재시도
        [Task: python-expert] "개선 요청: {feedback}"
        attempt += 1

if 여전히 실패:
    # 다른 에이전트 시도
    [Task: backend-architect] "설계 검토 후 구현 가이드"
```

---

## 동기화 패턴 (Synchronization)

### 패턴 1: 자연 동기화

한 메시지에서 여러 Task 호출 → 모든 결과가 한번에 반환:

```markdown
## 병렬 호출 (한 메시지)
[Task: agent-1] "작업 A"
[Task: agent-2] "작업 B"
[Task: agent-3] "작업 C"

## 결과
모든 에이전트 완료 후 결과가 한번에 반환됨
→ 자연스러운 "배리어" 동기화
```

### 패턴 2: 백그라운드 + 폴링

긴 작업은 백그라운드로:

```markdown
## Step 1: 백그라운드 실행
[Task: run_in_background=true] → agent_id 반환

## Step 2: 다른 작업 수행
[직접 파일 읽기, 분석 등]

## Step 3: 결과 확인
[AgentOutputTool: agent_id, block=false]
→ 아직 실행 중이면 다른 작업 계속
→ 완료되면 결과 처리

## Step 4: 필요시 대기
[AgentOutputTool: agent_id, block=true]
→ 완료될 때까지 대기
```

### 패턴 3: 단계적 동기화

복잡한 워크플로우를 단계로 나눔:

```markdown
## Phase 1: 분석 (병렬)
[Task: analyst-1], [Task: analyst-2], [Task: analyst-3]
→ 모든 분석 완료 대기

## Phase 2: 통합 (단일)
오케스트레이터가 결과 검토
→ 불일치 있으면 추가 분석 요청

## Phase 3: 실행 (병렬)
[Task: implementer-1], [Task: implementer-2]
→ 구현 완료 대기

## Phase 4: 검증 (단일)
[Task: quality-engineer] "전체 검증"
```

---

## 통신 패턴 (Communication)

### 유일한 통신 방법: 파일 시스템

```
에이전트 A ──write──▶ 파일 ──read──▶ 에이전트 B
```

### 패턴 1: 작업 디렉토리 규약

```markdown
## 디렉토리 구조
ai-docs/
├── input/           # 에이전트 입력
│   ├── requirements.md
│   └── context.md
├── output/          # 에이전트 출력
│   ├── agent-1-result.md
│   ├── agent-2-result.md
│   └── agent-3-result.md
└── final/           # 최종 결과
    └── report.md

## 규약
- 에이전트는 input/ 읽기, output/에 자기 결과 쓰기
- 오케스트레이터가 output/ 읽어서 종합
- 최종 결과는 final/에
```

### 패턴 2: 구조화된 출력 형식

에이전트 결과의 일관성을 위해:

```markdown
## 에이전트에게 지시할 출력 형식

"분석 결과를 다음 형식으로 작성하세요:

# 분석 결과

## 요약
[2-3문장 핵심 요약]

## 발견사항
1. [발견 1]
2. [발견 2]

## 권고사항
- [권고 1]
- [권고 2]

## 확신도
[높음/중간/낮음] - [이유]
"
```

### 패턴 3: 에이전트 간 참조

한 에이전트가 다른 에이전트 결과를 참조:

```markdown
## Step 1
[Task: security-engineer]
"보안 분석하고 ai-docs/security-review.md에 작성"

## Step 2
[Task: backend-architect]
"ai-docs/security-review.md를 읽고,
보안 요구사항을 반영한 API 설계를 작성"
```

---

## 충돌 해결 (Conflict Resolution)

### 언제 충돌이 발생하는가?

```
에이전트 A: "이 방식으로 구현해야 합니다"
에이전트 B: "아니요, 저 방식이 더 좋습니다"

→ 오케스트레이터가 판단해야 함
```

### 패턴 1: 우선순위 기반

```markdown
## 오케스트레이터 판단 기준

보안 vs 성능 충돌 시:
→ 보안 우선 (security-engineer 의견 채택)

설계 vs 구현 충돌 시:
→ 설계 우선 (architect 의견 채택)

## 우선순위 예시
1. security-engineer (보안 관련)
2. architect (설계 관련)
3. performance-engineer (성능 관련)
4. developer (구현 관련)
```

### 패턴 2: 근거 기반

```markdown
## 에이전트에게 요청

"의견 제시 시 반드시 근거를 포함하세요:
- 왜 이 방식인가?
- 대안은 무엇이고 왜 선택하지 않았는가?
- 트레이드오프는?"

## 오케스트레이터 판단

근거가 더 강한 쪽 채택
또는
두 의견을 종합한 절충안 도출
```

### 패턴 3: 추가 검토 요청

```markdown
## 충돌 발생 시

Step 1: 충돌 식별
"Agent A와 Agent B의 의견이 다름"

Step 2: 제3 에이전트에게 검토 요청
[Task: system-architect]
"두 의견을 검토하고 어떤 것이 더 적합한지 판단:
- 의견 A: [내용]
- 의견 B: [내용]
- 맥락: [프로젝트 상황]"

Step 3: 최종 결정
오케스트레이터가 제3 의견을 참고하여 결정
```

### 패턴 4: 사용자 에스컬레이션

```markdown
## 오케스트레이터 판단

"이 결정은 비즈니스 영향이 크고,
기술적으로만 판단하기 어려움"

→ 사용자에게 질문

[AskUserQuestion]
"두 가지 접근 방식이 있습니다:
A: [설명] - 장점/단점
B: [설명] - 장점/단점

어떤 방향을 선호하시나요?"
```

---

## 상태 관리 (State Management)

### Claude Code에서의 상태

```
세션 내: 오케스트레이터가 컨텍스트로 유지
세션 간: 파일 시스템 또는 Serena 메모리
```

### 패턴 1: 파일 기반 상태

```markdown
## 상태 파일 예시: ai-docs/workflow-state.md

# Workflow State

## Current Phase
implementation

## Completed Steps
- [x] requirements analysis
- [x] design
- [ ] implementation
- [ ] testing

## Key Decisions
- API style: REST (security-engineer 권고)
- Database: PostgreSQL (backend-architect 권고)

## Pending Issues
- Performance concern in module X
```

### 패턴 2: Serena 메모리 활용

```markdown
## 장기 상태 저장

[mcp__serena__write_memory]
memory_file_name: "project-context"
content: "프로젝트 상태 및 결정사항..."

## 다음 세션에서 복원

[mcp__serena__read_memory]
memory_file_name: "project-context"
```

### 패턴 3: 체크포인트

```markdown
## 주요 마일스톤마다 저장

Phase 1 완료 후:
Write: ai-docs/checkpoint-phase1.md
내용: 분석 결과 요약, 주요 결정, 다음 단계

Phase 2 완료 후:
Write: ai-docs/checkpoint-phase2.md
내용: 설계 결과 요약, 변경사항, 다음 단계

## 세션 재개 시
Read: 최신 checkpoint 파일
→ 컨텍스트 복원
```

---

## 실전 체크리스트

### 에이전트 호출 전

```markdown
□ 이 작업에 에이전트가 정말 필요한가? (단순 작업은 직접)
□ 어떤 에이전트가 적합한가?
□ 병렬 실행 가능한가? (의존성 확인)
□ 입력 컨텍스트가 준비되었는가? (파일)
□ 출력 형식을 명시했는가?
```

### 결과 받은 후

```markdown
□ 요청한 형식에 맞는가?
□ 필수 내용이 포함되어 있는가?
□ 다른 에이전트 결과와 충돌이 있는가?
□ 다음 단계에 충분한 정보인가?
□ 품질 기준을 충족하는가?
```

### 충돌 발생 시

```markdown
□ 충돌의 본질은 무엇인가?
□ 우선순위 규칙으로 해결 가능한가?
□ 근거를 비교하여 판단 가능한가?
□ 제3 의견이 필요한가?
□ 사용자 결정이 필요한가?
```

---

## Quick Reference

```yaml
위임:
  직접: 특정 에이전트 지정
  능력기반: 요구 능력 분석 → 에이전트 선택
  오케스트레이터가 모든 결정

핸드오프:
  순차: A 결과 → B 입력
  조건부: 결과에 따라 다른 에이전트
  폴백: 실패 시 대안 에이전트

동기화:
  자연: 한 메시지 병렬 호출 → 동시 반환
  백그라운드: run_in_background + AgentOutputTool
  단계적: Phase 단위로 나눔

통신:
  유일한 방법: 파일 시스템
  규약: input/, output/, final/ 디렉토리
  형식: 구조화된 출력 지시

충돌 해결:
  우선순위: 보안 > 설계 > 성능 > 구현
  근거 기반: 더 강한 근거 채택
  제3 검토: 추가 에이전트 의견
  에스컬레이션: 사용자 결정 요청

상태:
  세션 내: 오케스트레이터 컨텍스트
  세션 간: 파일 또는 Serena 메모리
```
