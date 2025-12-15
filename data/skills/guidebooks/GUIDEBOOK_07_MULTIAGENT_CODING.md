# 🤖 Part 7: 학습 기반 멀티에이전트 코딩 시스템

> **"AI 에이전트 팀으로 소프트웨어 개발 자동화"**
>
> 이 가이드북은 **비용/속도/실용성**을 중심으로 멀티에이전트 시스템을 활용한 실전 코딩 워크플로우를 제공합니다.
> Claude Code 환경에 최적화되어 있으며, CrewAI/LangGraph 구현 패턴도 포함합니다.

---

## 📑 목차

### 🎯 핵심 개념
- [비용/속도/실용성 삼각형](#비용속도실용성-삼각형)
- [명확도 기반 판단 가이드라인](#명확도-기반-판단-가이드라인)
- [언제 멀티에이전트를 사용하는가?](#언제-멀티에이전트를-사용하는가)

### 🏗️ 패턴별 워크플로우
- [Pattern A: Sequential Pipeline](#pattern-a-sequential-pipeline)
- [Pattern B: Hierarchical (Manager-Worker)](#pattern-b-hierarchical-manager-worker)
- [Pattern C: Peer Collaboration](#pattern-c-peer-collaboration)
- [Pattern D: Agent Swarm](#pattern-d-agent-swarm)

### 💻 실전 코딩 시나리오
- [시나리오 1: Big Three 풀스택 개발](#시나리오-1-big-three-풀스택-개발-)
- [시나리오 2: 레거시 코드 마이그레이션](#시나리오-2-레거시-코드-마이그레이션-)
- [시나리오 3: 버그 조사 및 수정](#시나리오-3-버그-조사-및-수정-)
- [시나리오 4: 코드 리뷰 자동화](#시나리오-4-코드-리뷰-자동화-)
- [시나리오 5: 테스트 커버리지 증가](#시나리오-5-테스트-커버리지-증가-)
- [시나리오 6: API 설계 및 구현](#시나리오-6-api-설계-및-구현-)
- [시나리오 7: 성능 최적화](#시나리오-7-성능-최적화-)
- [시나리오 8: 보안 감사](#시나리오-8-보안-감사-)
- [시나리오 9: 문서화 자동화](#시나리오-9-문서화-자동화-)
- [시나리오 10: CI/CD 파이프라인 통합](#시나리오-10-cicd-파이프라인-통합-)

### 💰 비용 최적화 전략
- [모델 티어링](#모델-티어링)
- [파일 기반 위임](#파일-기반-위임)
- [4-Message 병렬 패턴](#4-message-병렬-패턴)

---

## 🎯 핵심 개념

### 비용/속도/실용성 삼각형

```
                    💰 비용 최적화
                        /\
                       /  \
                      /    \
                     /  🎯  \
                    / 균형점  \
                   /          \
                  /____________\
         ⚡ 속도 극대화    🛠️ 실용성 우선
```

| 원칙 | 목표 | 달성 방법 |
|------|------|----------|
| **💰 비용 최적화** | LLM 호출 최소화 | 명확도 판단 + 단일 에이전트 우선 |
| **⚡ 속도 극대화** | 3-5x 빠른 실행 | 4-Message 병렬 패턴 |
| **🛠️ 실용성 우선** | 즉시 적용 가능 | 사전 질문 + 파일 기반 위임 |

---

### 명확도 기반 판단 가이드라인

**핵심**: 에이전트 스폰 전 **명확도 체크**로 불필요한 비용 방지

```
요청 도착
│
├─ 1. 컨텍스트 확인 (필요시)
│   └─ 프로젝트 구조, 이전 작업 파악 (Read, Grep, Serena memory)
│
├─ 2. 명확도 판단
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

#### 명확도 체크리스트

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

---

### 언제 멀티에이전트를 사용하는가?

#### ✅ 멀티에이전트 적합

| 상황 | 이유 | 권장 패턴 |
|------|------|----------|
| 병렬 가능한 독립 작업 | 3-5x 속도 향상 | Hierarchical |
| 전문성이 다른 작업 | 역할 분리로 품질 향상 | Sequential |
| 검토/검증 필요 | 다중 관점 확보 | Peer Collaboration |
| 다양한 솔루션 탐색 | 최선의 선택 | Swarm |

#### ❌ 멀티에이전트 부적합

| 상황 | 이유 | 대안 |
|------|------|------|
| 단일 에이전트로 충분 | 불필요한 비용 | 단일 에이전트 |
| 작업이 단순/선형 | 조정 오버헤드 > 이점 | 단순 프롬프트 |
| 디버깅 경험 부족 | 유지보수 어려움 | 단일 + 반복 |
| 작업 간 강한 의존성 | 병렬화 불가 | Sequential |

---

## 🏗️ 패턴별 워크플로우

### Pattern A: Sequential Pipeline

**사용 시점**: 각 단계가 이전 결과에 의존

```
Request → Analyst → Designer → Developer → Reviewer → Output
```

**비용**: N 에이전트 = N LLM 호출 (순차)
**속도**: 병렬화 불가 (의존성)
**장점**: 디버깅 용이, 명확한 흐름

```python
# [21-multiagent] Sequential Pipeline 구현
workflow = [
    ("analyst", "Analyze requirements and create spec"),
    ("designer", "Design architecture based on spec"),
    ("developer", "Implement according to design"),
    ("reviewer", "Review and suggest improvements")
]

context = initial_request
for agent_name, task in workflow:
    result = agents[agent_name].execute(task, context)
    context = result  # 다음 에이전트에 전달
```

---

### Pattern B: Hierarchical (Manager-Worker)

**사용 시점**: 병렬 처리 가능한 독립적 하위작업

```
              Manager Agent
              /     |     \
    Worker 1   Worker 2   Worker 3
    (Backend)  (Frontend) (Testing)
              \     |     /
              Aggregator Agent
```

**비용**: N Workers + 2 (Manager + Aggregator)
**속도**: ⚡ **3-5x 빠름** (병렬 실행)
**장점**: 대규모 작업 분해에 효과적

```python
# [21-multiagent] Hierarchical Pattern - 4-Message 구현
# Message 1: 준비 (Bash만)
await write_file("ai-docs/task-spec.md", requirements)

# Message 2: 병렬 실행 (Task만)
results = await asyncio.gather(
    Task(agent="backend-developer", prompt="Read ai-docs/task-spec.md, implement API"),
    Task(agent="frontend-developer", prompt="Read ai-docs/task-spec.md, implement UI"),
    Task(agent="test-engineer", prompt="Read ai-docs/task-spec.md, write tests")
)

# Message 3: 통합
await Task(agent="integrator", prompt="Combine results from all workers")

# Message 4: 결과
return final_output
```

---

### Pattern C: Peer Collaboration

**사용 시점**: 여러 관점으로 품질 향상, 검토 필요

```
Coder ↔ Reviewer ↔ Tester
  ↓        ↓        ↓
      Consensus
```

**비용**: ⚠️ 높음 (여러 LLM 호출 + 반복)
**속도**: 합의까지 반복 필요
**장점**: 고품질 산출물

```python
# [21-multiagent] Peer Collaboration 구현
MAX_ROUNDS = 3

for round in range(MAX_ROUNDS):
    code = coder.execute(task, feedback)
    review = reviewer.execute(f"Review: {code}")
    test_result = tester.execute(f"Test: {code}")

    if review.approved and test_result.passed:
        break

    feedback = f"Review: {review.feedback}\nTests: {test_result.failures}"
```

---

### Pattern D: Agent Swarm

**사용 시점**: 다양한 솔루션 탐색, 창의적 문제 해결

```
Agent 1 → Solution A
Agent 2 → Solution B    →  Selector  →  Best Solution
Agent 3 → Solution C
```

**비용**: ⚠️ 매우 높음 (N 에이전트)
**속도**: 병렬 (빠름)
**장점**: 다양한 접근법 비교

```python
# [21-multiagent] Swarm Pattern 구현
solutions = await asyncio.gather(
    Task(agent="approach-a", prompt=f"Solve with functional style: {problem}"),
    Task(agent="approach-b", prompt=f"Solve with OOP style: {problem}"),
    Task(agent="approach-c", prompt=f"Solve with reactive style: {problem}")
)

best = await Task(
    agent="selector",
    prompt=f"Compare solutions and select best: {solutions}"
)
```

---

## 💻 실전 코딩 시나리오

### 시나리오 1: Big Three 풀스택 개발 🚀

**목표**: 처음부터 풀스택 앱을 멀티에이전트로 개발

```
요구사항 분석 → 설계 → 병렬 구현 → 통합 테스트 → 배포

1. [21-multiagent] 명확도 체크 및 요구사항 정리
   - 사용자 요청이 모호하면 질문 (에이전트 스폰 전!)
   - 명확한 요구사항을 ai-docs/requirements.md에 작성

2. [21-multiagent] 아키텍트 에이전트 (단일)
   - API 스키마 설계 → ai-docs/api-spec.md
   - DB 스키마 설계 → ai-docs/db-schema.md
   - UI 컴포넌트 구조 → ai-docs/ui-structure.md

3. [21-multiagent] Big Three 병렬 실행 (4-Message 패턴)

   Message 1 (Bash): 디렉토리 준비
   mkdir -p src/{api,db,ui}

   Message 2 (Task 병렬):
   - BackendDeveloper: API + DB 구현 (ai-docs/api-spec.md 참조)
   - FrontendDeveloper: UI 구현 (ai-docs/ui-structure.md 참조)
   - TestEngineer: E2E 테스트 작성

   Message 3 (Task): Integrator가 통합 검증

   Message 4: 결과 요약

4. [17-observability] 배포 및 모니터링
   - Vercel/Railway로 배포
   - 에러 트래킹 설정
```

**비용 분석**:
```
에이전트별 비용:
- Architect (sonnet): $0.05
- Backend (sonnet): $0.05
- Frontend (sonnet): $0.05
- TestEngineer (haiku): $0.01
- Integrator (sonnet): $0.03
─────────────────────────
총 비용: ~$0.19
속도: 15분 (순차 시 45분 → 3x 향상)
```

---

### 시나리오 2: 레거시 코드 마이그레이션 🏚️

**목표**: 구형 코드를 현대적 스택으로 안전하게 마이그레이션

```
분석 → 리스크 평가 → 계획 → 단계별 실행 → 검증

1. [21-multiagent] CodeArcheologist (분석 에이전트)
   - 기존 코드베이스 구조 파악
   - 의존성 그래프 생성
   - 기술 부채 목록화
   → ai-docs/codebase-analysis.md

2. [21-multiagent] RiskAnalyzer (리스크 평가)
   - 마이그레이션 리스크 점수화
   - 영향 범위 분석
   - 롤백 전략 수립
   → ai-docs/risk-assessment.md

3. [21-multiagent] MigrationPlanner (계획 수립)
   - 단계별 마이그레이션 계획 (Phase 1, 2, 3...)
   - 각 단계별 테스트 기준
   - 하위 호환성 전략
   → ai-docs/migration-plan.md

4. [21-multiagent] 단계별 실행 (Sequential Pipeline)
   Phase 1: 의존성 업데이트
   Phase 2: 코어 로직 마이그레이션
   Phase 3: UI 레이어 마이그레이션
   Phase 4: 통합 테스트

5. [11-evaluation] 검증
   - 기존 테스트 통과 확인
   - 성능 벤치마크 비교
   - 사용자 수용 테스트
```

**에이전트 구성**:
```python
migration_team = {
    "archeologist": Agent(role="Legacy code analyst"),
    "risk_analyst": Agent(role="Risk assessor"),
    "planner": Agent(role="Migration strategist"),
    "implementer": Agent(role="Migration executor"),
    "validator": Agent(role="Quality assurer")
}
```

---

### 시나리오 3: 버그 조사 및 수정 🔍

**목표**: 복잡한 버그를 체계적으로 조사하고 수정

```
증상 수집 → 증거 분석 → 가설 생성 → 검증 → 수정

1. [21-multiagent] BugDetective (증거 수집)
   - 스택트레이스 분석
   - 로그 패턴 검색
   - 재현 조건 정리
   → ai-docs/bug-evidence.md

2. [21-multiagent] CodeAnalyzer (코드 분석)
   - 관련 코드 경로 추적
   - 최근 변경사항 검토 (git diff)
   - 의존성 체크
   → ai-docs/code-analysis.md

3. [21-multiagent] HypothesisGenerator (가설 생성)
   - 수집된 증거 기반 원인 가설 3-5개 제시
   - 각 가설별 검증 방법 제안
   → ai-docs/hypotheses.md

4. [21-multiagent] Verifier (가설 검증)
   - 가설별 테스트 코드 작성
   - 실행하여 원인 확정
   → ai-docs/verification-result.md

5. [21-multiagent] Fixer (수정)
   - 확정된 원인에 대한 수정 코드 작성
   - 회귀 테스트 추가
   - PR 생성
```

**실용적 팁**:
```markdown
❌ 잘못된 접근:
"버그 있어요, 고쳐주세요" → 바로 에이전트 스폰

✅ 올바른 접근:
"버그 있어요" → "어떤 증상인가요? 에러 메시지는?" 질문
→ 구체적 정보 수집 후 에이전트 스폰
```

---

### 시나리오 4: 코드 리뷰 자동화 🔍

**목표**: PR에 대한 다중 관점 자동 코드 리뷰

```
PR 생성 → 코드 분석 → 다중 관점 리뷰 → 통합 피드백

1. [14-agents] GitHub API 연동
   - PR 내용 파싱
   - 변경된 파일 추출
   - 컨텍스트 정보 수집

2. [21-multiagent] 리뷰어 에이전트 팀 (병렬)

   - SecurityGuard: 보안 취약점 점검
     └─ SQL Injection, XSS, 인증 우회 등

   - StyleCop: 코딩 컨벤션 확인
     └─ 린트 규칙, 네이밍, 포맷팅

   - PerformanceGuru: 성능 분석
     └─ 알고리즘 복잡도, N+1 쿼리, 메모리 누수

   - TestArchitect: 테스트 검토
     └─ 커버리지, 엣지 케이스, 모킹 적절성

   - ArchitectureReviewer: 설계 원칙 검토
     └─ SOLID, DRY, 의존성 방향

3. [21-multiagent] ReviewAggregator (통합)
   - 중복 지적 통합
   - 중요도별 분류 (Blocker > Critical > Minor)
   - 최종 리뷰 코멘트 생성

4. [14-agents] GitHub API로 코멘트 작성
   - 라인별 코멘트
   - 전체 요약 코멘트
```

**비용 최적화 팁**:
```python
# 모델 티어링으로 비용 절감
reviewers = {
    "security": Agent(model="opus"),     # 보안은 정확도 중요
    "style": Agent(model="haiku"),       # 스타일은 간단
    "performance": Agent(model="sonnet"), # 균형
    "test": Agent(model="haiku"),        # 패턴 매칭 중심
    "architecture": Agent(model="sonnet") # 분석 필요
}
```

---

### 시나리오 5: 테스트 커버리지 증가 🧪

**목표**: 기존 코드의 테스트 커버리지를 체계적으로 높임

```
커버리지 분석 → 우선순위화 → 테스트 생성 → 검증

1. [11-evaluation] 현재 커버리지 측정
   - pytest --cov / jest --coverage 실행
   - 미커버 라인/브랜치 목록화
   → ai-docs/coverage-report.md

2. [21-multiagent] PriorityAnalyzer
   - 비즈니스 중요도 기반 우선순위
   - 복잡도 높은 함수 우선
   - 버그 이력 있는 코드 우선
   → ai-docs/test-priorities.md

3. [21-multiagent] 테스트 생성 팀 (병렬)

   - UnitTestWriter: 단위 테스트 작성
   - IntegrationTestWriter: 통합 테스트 작성
   - EdgeCaseExplorer: 엣지 케이스 발굴

4. [11-evaluation] 테스트 실행 및 검증
   - 모든 테스트 통과 확인
   - 커버리지 증가량 측정
   - 플레이키 테스트 제거
```

**실전 명령어**:
```bash
# 커버리지 리포트 생성
pytest --cov=src --cov-report=html

# 미커버 함수 목록
grep -r "def " src/ | xargs -I {} sh -c 'coverage report --include={} | grep "0%"'
```

---

### 시나리오 6: API 설계 및 구현 🔌

**목표**: RESTful/GraphQL API를 체계적으로 설계하고 구현

```
요구사항 → 스키마 설계 → 구현 → 문서화 → 테스트

1. [21-multiagent] APIArchitect (설계)
   - 리소스 식별 및 관계 정의
   - 엔드포인트 설계 (REST) 또는 스키마 (GraphQL)
   - 인증/권한 전략
   → ai-docs/api-design.md

2. [21-multiagent] 구현 팀 (병렬)

   - RouteImplementer: 라우트/컨트롤러 구현
   - ServiceImplementer: 비즈니스 로직
   - DBImplementer: 데이터 레이어
   - AuthImplementer: 인증/권한 미들웨어

3. [16-prompt-engineering] OpenAPI/GraphQL 스키마 생성
   - Instructor로 타입 안전한 스키마
   - 자동 문서화 (Swagger UI)

4. [21-multiagent] APITester (테스트)
   - 엔드포인트별 테스트
   - 인증 플로우 테스트
   - 에러 케이스 테스트
```

---

### 시나리오 7: 성능 최적화 ⚡

**목표**: 애플리케이션 성능 병목을 찾아 최적화

```
프로파일링 → 병목 분석 → 최적화 → 벤치마크

1. [17-observability] 프로파일링 실행
   - CPU: cProfile, py-spy
   - 메모리: memory_profiler
   - DB: EXPLAIN ANALYZE
   → ai-docs/profile-results.md

2. [21-multiagent] BottleneckAnalyzer (분석)
   - 핫스팟 식별
   - 알고리즘 복잡도 분석
   - I/O 바운드 vs CPU 바운드 분류

3. [21-multiagent] 최적화 팀 (전문화)

   - AlgorithmOptimizer: O(n²) → O(n log n) 등
   - CacheOptimizer: 캐싱 전략 적용
   - QueryOptimizer: DB 쿼리 최적화
   - AsyncOptimizer: 비동기/병렬화

4. [11-evaluation] 벤치마크
   - Before/After 성능 비교
   - 메모리 사용량 비교
   - 응답 시간 측정
```

**실전 도구**:
```python
# CPU 프로파일링
import cProfile
cProfile.run('main()', sort='cumtime')

# 메모리 프로파일링
from memory_profiler import profile
@profile
def my_function(): ...

# DB 쿼리 분석
EXPLAIN ANALYZE SELECT ...
```

---

### 시나리오 8: 보안 감사 🔒

**목표**: 코드베이스의 보안 취약점 탐지 및 수정

```
스캔 → 분석 → 수정 → 검증

1. [07-safety-alignment] 자동화 스캔
   - bandit (Python), npm audit (JS)
   - SAST 도구 (Semgrep, CodeQL)
   → ai-docs/scan-results.md

2. [21-multiagent] 보안 분석 팀 (병렬)

   - InjectionAnalyst: SQL/Command/XSS 인젝션
   - AuthAnalyst: 인증/세션 취약점
   - CryptoAnalyst: 암호화 관련 문제
   - ConfigAnalyst: 설정/시크릿 노출

3. [21-multiagent] SecurityFixer
   - 취약점별 수정 코드 작성
   - 안전한 패턴으로 대체
   - 입력 검증 강화

4. [11-evaluation] 재스캔 및 침투 테스트
   - 수정 후 재스캔
   - OWASP ZAP으로 동적 테스트
```

**OWASP Top 10 체크리스트**:
```markdown
□ A01:2021 - Broken Access Control
□ A02:2021 - Cryptographic Failures
□ A03:2021 - Injection
□ A04:2021 - Insecure Design
□ A05:2021 - Security Misconfiguration
□ A06:2021 - Vulnerable Components
□ A07:2021 - Authentication Failures
□ A08:2021 - Data Integrity Failures
□ A09:2021 - Logging Failures
□ A10:2021 - SSRF
```

---

### 시나리오 9: 문서화 자동화 📚

**목표**: 코드베이스 문서를 자동으로 생성하고 유지

```
코드 분석 → 문서 생성 → 예제 추가 → 배포

1. [21-multiagent] CodeAnalyzer (구조 파악)
   - 모듈/클래스/함수 추출
   - 의존성 그래프 생성
   - 공개 API 식별

2. [21-multiagent] 문서 생성 팀 (병렬)

   - APIDocWriter: API 레퍼런스 생성
   - TutorialWriter: 사용법 튜토리얼
   - ExampleWriter: 코드 예제 작성
   - ArchitectureDocWriter: 아키텍처 문서

3. [16-prompt-engineering] 구조화된 출력
   - Markdown/RST 형식
   - 타입 정보 포함
   - 링크 자동 생성

4. [09-infrastructure] 문서 배포
   - MkDocs/Sphinx 빌드
   - GitHub Pages/ReadTheDocs 배포
   - CI/CD 연동
```

---

### 시나리오 10: CI/CD 파이프라인 통합 🔄

**목표**: AI 코드 리뷰를 CI/CD 파이프라인에 통합

```
PR 트리거 → AI 분석 → 자동 피드백 → 승인 게이트

1. [09-infrastructure] GitHub Actions 설정

   on: [pull_request]

   jobs:
     ai-review:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: AI Code Review
           run: python scripts/ai_review.py

2. [21-multiagent] 리뷰 파이프라인

   parallel_reviews:
     - security_check (필수)
     - style_check (권고)
     - performance_check (권고)
     - test_coverage_check (필수)

3. [14-agents] 자동 피드백
   - GitHub Check API로 결과 보고
   - 라인별 코멘트 자동 추가
   - Approve/Request Changes 자동화

4. [17-observability] 대시보드
   - 리뷰 통계 (승인율, 이슈 유형 등)
   - 비용 추적
   - 품질 트렌드
```

**GitHub Actions 예제**:
```yaml
name: AI Code Review

on:
  pull_request:
    branches: [main]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get changed files
        id: changed-files
        run: |
          echo "files=$(git diff --name-only origin/main...HEAD | tr '\n' ' ')" >> $GITHUB_OUTPUT

      - name: AI Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/ai_review.py ${{ steps.changed-files.outputs.files }}

      - name: Post Review Comments
        uses: actions/github-script@v7
        with:
          script: |
            // Post AI review comments to PR
```

---

## 💰 비용 최적화 전략

### 모델 티어링

```python
# 작업 복잡도에 따른 모델 선택
MODEL_TIERS = {
    "simple": "claude-3-haiku-20240307",    # $0.25/1M tokens
    "balanced": "claude-3-5-sonnet-20241022", # $3/1M tokens
    "complex": "claude-3-opus-20240229"       # $15/1M tokens
}

def select_model(task_complexity: str) -> str:
    """작업 복잡도에 따른 모델 자동 선택"""
    complexity_map = {
        "style_check": "simple",
        "code_generation": "balanced",
        "architecture_design": "complex",
        "security_audit": "complex",
        "documentation": "simple",
        "test_generation": "balanced"
    }
    tier = complexity_map.get(task_complexity, "balanced")
    return MODEL_TIERS[tier]
```

**비용 비교 (10만 토큰 기준)**:
| 티어 | 모델 | 비용 | 적합한 작업 |
|------|------|------|------------|
| Simple | Haiku | $0.025 | 스타일 체크, 문서화, 단순 분석 |
| Balanced | Sonnet | $0.30 | 코드 생성, 테스트 작성, 리뷰 |
| Complex | Opus | $1.50 | 아키텍처, 보안 감사, 복잡한 디버깅 |

---

### 파일 기반 위임

**핵심**: 오케스트레이터 컨텍스트 오염 방지 → 50-80% 토큰 절약

```python
# ❌ 잘못됨 - 인라인 지시 (컨텍스트 오염)
Task(
    agent="architect",
    prompt=f"""
    Here are the detailed requirements (500 lines):
    {huge_requirements_text}

    Please analyze and create architecture.
    """  # 오케스트레이터 컨텍스트에 500줄 추가됨
)

# ✅ 올바름 - 파일 기반 (컨텍스트 절약)
await write_file("ai-docs/requirements.md", huge_requirements_text)

Task(
    agent="architect",
    prompt="""
    Read requirements from: ai-docs/requirements.md
    Create architecture plan.
    Write output to: ai-docs/architecture.md
    Return brief summary only (2-3 sentences).
    """  # 오케스트레이터 컨텍스트에 5줄만 추가
)
```

**컨텍스트 사용량 비교**:
```
인라인 방식:
  - 요구사항: 5,000 tokens
  - 결과: 3,000 tokens
  - 오케스트레이터 컨텍스트: 8,000 tokens

파일 기반:
  - 프롬프트: 100 tokens
  - 요약 반환: 50 tokens
  - 오케스트레이터 컨텍스트: 150 tokens

절감: 8,000 → 150 = 98% 감소!
```

---

### 4-Message 병렬 패턴

**핵심**: Claude Code에서 진정한 병렬 실행을 위해 도구 유형 분리

```
Message 1: 준비 (Bash만)
  - 디렉토리 생성
  - 컨텍스트 파일 작성
  - ❌ Task 금지, ❌ TodoWrite 금지

Message 2: 병렬 실행 (Task만)
  - 모든 에이전트를 단일 메시지에서 시작
  - Task 도구만 사용
  - 모든 Task가 동시 실행됨 ✅

Message 3: 통합 (Task만)
  - 통합 에이전트 시작
  - 선행 Task 완료 후 트리거

Message 4: 결과 제시
  - 사용자에게 최종 결과 표시
```

**안티패턴 (순차 실행됨)**:
```python
# ❌ 도구 유형 혼합 = 병렬화 파괴
await TodoWrite({...})  # Tool 1
await Task({...})       # Tool 2 - TodoWrite 대기
await Bash({...})       # Tool 3 - Task 대기
await Task({...})       # Tool 4 - Bash 대기
```

**올바른 패턴 (병렬 실행됨)**:
```python
# ✅ 같은 유형의 도구만 한 메시지에
await Task({...})  # Task 1 ─┐
await Task({...})  # Task 2 ─┼─ 동시 실행!
await Task({...})  # Task 3 ─┘
```

---

## 📊 Quick Reference: 시나리오별 선택 가이드

| 시나리오 | 권장 패턴 | 에이전트 수 | 예상 비용 | 예상 시간 |
|----------|----------|-----------|----------|----------|
| 풀스택 앱 개발 | Hierarchical | 4-5 | $0.19 | 15분 |
| 레거시 마이그레이션 | Sequential | 5 | $0.25 | 30분 |
| 버그 조사 | Sequential | 5 | $0.15 | 10분 |
| 코드 리뷰 | Hierarchical | 5-6 | $0.10 | 2분 |
| 테스트 생성 | Hierarchical | 3-4 | $0.08 | 5분 |
| API 설계 | Sequential | 4 | $0.12 | 10분 |
| 성능 최적화 | Sequential | 4 | $0.15 | 15분 |
| 보안 감사 | Hierarchical | 4 | $0.20 | 10분 |
| 문서화 | Hierarchical | 4 | $0.06 | 5분 |
| CI/CD 통합 | - | 파이프라인 | PR당 $0.05 | 1분 |

---

## 🔗 관련 스킬

| 기능 | 스킬 경로 |
|------|-----------|
| 멀티에이전트 핵심 | `21-multiagent-learning-system/` |
| 블록체인 보안 | `22-blockchain-agent-security/` |
| 프론트엔드 설계 | `23-frontend-design-architect/` |
| 백엔드 아키텍처 | `25-backend-architect/` |
| RAG 구현 | `15-rag/` |
| 프롬프트 엔지니어링 | `16-prompt-engineering/instructor/` |
| 평가 | `11-evaluation/lm-evaluation-harness/` |
| MLOps | `13-mlops/` |

---

**Version:** 1.0.0
**Dependencies:** 21-multiagent-learning-system, 14-agents, 17-observability
**Complexity:** Intermediate to Advanced
**Output:** 비용/속도 최적화된 AI 에이전트 기반 소프트웨어 개발 파이프라인
