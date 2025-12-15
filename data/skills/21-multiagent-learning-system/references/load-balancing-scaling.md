# Claude Code 효율적 에이전트 활용 가이드

Claude Code 환경에서 **에이전트를 효율적으로 활용하는** 실용적 가이드입니다.

> **주의**: Claude Code에는 자동 로드 밸런싱이나 오토스케일링 API가 없습니다.
> 모든 최적화는 **오케스트레이터의 판단**으로 이루어집니다.

---

## Claude Code의 제약사항

### 없는 것 (API 미지원)

```
❌ 자동 로드 밸런싱
❌ 에이전트 풀 관리 API
❌ 오토스케일링
❌ 에이전트 상태 모니터링 API
❌ 동적 에이전트 생성/삭제
❌ 부하 메트릭 조회
```

### 있는 것 (활용 가능)

```
✅ 병렬 Task 호출 (한 메시지에 여러 Task)
✅ 백그라운드 실행 (run_in_background)
✅ AgentOutputTool (결과 수집)
✅ 다양한 에이전트 유형 선택
✅ 모델 선택 (opus/sonnet/haiku)
```

---

## 효율적 에이전트 활용 전략

### 전략 1: 병렬화로 처리량 증가

```markdown
## 상황
5개 파일을 각각 분석해야 함

## 비효율적 (순차)
[Task] file1 분석 → 대기 → 결과
[Task] file2 분석 → 대기 → 결과
[Task] file3 분석 → 대기 → 결과
...
총 시간: 5 × T

## 효율적 (병렬)
한 메시지에서:
[Task] file1 분석
[Task] file2 분석
[Task] file3 분석
[Task] file4 분석
[Task] file5 분석
→ 모든 결과 한번에 반환
총 시간: ~T (병렬이므로)
```

### 전략 2: 적절한 모델 선택

```markdown
## 모델별 특성
opus:   가장 정확, 가장 비쌈, 가장 느림
sonnet: 균형잡힌 성능/비용
haiku:  가장 빠름, 가장 저렴, 단순 작업용

## 작업별 권장

복잡한 아키텍처 설계:
→ model="opus"

일반적인 코드 분석:
→ model="sonnet" (기본값)

단순 형식 변환, 검증:
→ model="haiku"

## 예시
[Task: subagent_type="backend-architect", model="opus"]
"중요한 시스템 설계"

[Task: subagent_type="Explore", model="haiku"]
"파일 목록 확인"
```

### 전략 3: Task vs 직접 실행 판단

```markdown
## 판단 기준

작업 복잡도 낮음 + 빠른 실행 필요:
→ 직접 실행 (Read, Grep, Bash)

작업 복잡도 높음 + 전문 지식 필요:
→ Task 사용

병렬 실행 이점 있음:
→ Task 사용

## 구체적 예시

파일 내용 확인:
❌ [Task: Explore] "파일 읽어줘"
✅ Read(file_path)

패턴 검색:
❌ [Task: general-purpose] "코드에서 TODO 찾아줘"
✅ Grep(pattern="TODO")

복잡한 보안 분석:
✅ [Task: security-engineer] "취약점 분석"
```

---

## 에이전트 선택 최적화

### 작업 복잡도별 권장

```markdown
## 복잡도: 낮음 (직접 실행)
- 파일 읽기/쓰기
- 단순 검색
- 명령어 실행

## 복잡도: 중간 (가벼운 에이전트)
- 코드베이스 탐색 → Explore (model="haiku")
- 간단한 계획 → Plan

## 복잡도: 높음 (전문 에이전트)
- 아키텍처 설계 → backend-architect, system-architect
- 보안 분석 → security-engineer
- 성능 최적화 → performance-engineer

## 복잡도: 매우 높음 (opus 모델)
- 중요한 설계 결정
- 복잡한 트레이드오프 분석
- 여러 도메인 걸친 통합 분석
```

### 에이전트 유형별 비용/속도

```markdown
| 에이전트 유형 | 속도 | 비용 | 적합한 작업 |
|--------------|------|------|-------------|
| Explore (haiku) | 빠름 | 낮음 | 파일 탐색, 구조 파악 |
| general-purpose | 중간 | 중간 | 범용 작업 |
| 전문가 (sonnet) | 중간 | 중간 | 도메인별 분석 |
| 전문가 (opus) | 느림 | 높음 | 중요 결정 |
```

---

## 워크로드 분산 패턴

### 패턴 1: 수평 분할

큰 작업을 독립적인 부분으로 나눔:

```markdown
## 상황
10개 모듈의 코드 리뷰 필요

## 분할 전략
모듈 단위로 분할하여 병렬 처리

## 실행
Message 1에서:
[Task: quality-engineer] "modules/auth 리뷰"
[Task: quality-engineer] "modules/api 리뷰"
[Task: quality-engineer] "modules/db 리뷰"
... (병렬)

## 결과 통합
오케스트레이터가 모든 리뷰 결과 종합
```

### 패턴 2: 관점별 분할

동일 대상을 다른 관점에서 분석:

```markdown
## 상황
새 API 설계 검토 필요

## 분할 전략
관점별로 다른 전문가 에이전트 활용

## 실행 (병렬)
[Task: backend-architect] "구조 및 확장성 관점"
[Task: security-engineer] "보안 관점"
[Task: performance-engineer] "성능 관점"

## 결과 통합
세 관점을 종합한 최종 검토 보고서
```

### 패턴 3: 파이프라인 분할

순차적 의존성이 있는 작업:

```markdown
## 상황
요구사항 → 설계 → 구현 → 테스트

## 주의
이 경우 병렬화 불가 (의존성)

## 최적화 전략
각 단계 내에서 병렬화

Step 1: 요구사항 분석 (단일)
[Task: requirements-analyst]

Step 2: 설계 (병렬 가능)
[Task: backend-architect] "백엔드 설계"
[Task: frontend-architect] "프론트엔드 설계"

Step 3: 구현 (병렬 가능, 설계 완료 후)
[Task: python-expert] "백엔드 구현"
[Task: frontend-architect] "프론트엔드 구현"

Step 4: 테스트 (병렬 가능)
[Task: quality-engineer] "단위 테스트"
[Task: quality-engineer] "통합 테스트"
```

---

## 비용/시간 최적화

### 빠른 피드백이 필요할 때

```markdown
## 전략: 가벼운 에이전트 먼저

Step 1: 빠른 초기 분석
[Task: Explore, model="haiku"]
"코드 구조 빠르게 파악"

Step 2: 필요한 부분만 심층 분석
[Task: security-engineer, model="sonnet"]
"식별된 위험 영역만 상세 분석"
```

### 비용 최소화가 필요할 때

```markdown
## 전략: 직접 실행 최대화

Step 1: 정보 수집 (직접)
Read, Grep, Glob으로 필요한 정보 수집

Step 2: 핵심 분석만 에이전트
수집된 정보 기반으로 핵심 질문만 에이전트에게

Step 3: 후처리 (직접)
에이전트 결과를 바탕으로 직접 정리/구현
```

### 품질 최대화가 필요할 때

```markdown
## 전략: 다중 검토

Step 1: 주 분석
[Task: backend-architect, model="opus"]
"중요 시스템 설계"

Step 2: 교차 검토 (병렬)
[Task: security-engineer] "보안 검토"
[Task: performance-engineer] "성능 검토"

Step 3: 품질 게이트
모든 검토 통과해야 진행
```

---

## 실패 대응 전략

### 에이전트 결과 불충분 시

```markdown
## 1차: 피드백과 함께 재요청
[Task: 동일 에이전트]
"이전 결과가 {부족한 점}. {구체적 개선 요청}"

## 2차: 다른 에이전트 시도
[Task: 더 전문화된 에이전트]

## 3차: 작업 분할
큰 작업을 작은 단위로 나눠서 재시도

## 최종: 직접 처리
에이전트 결과를 참고하여 오케스트레이터가 직접
```

### 타임아웃 대응

```markdown
## 백그라운드 실행 활용

긴 작업 예상 시:
[Task: run_in_background=true]

다른 작업 수행하면서:
[AgentOutputTool: block=false] → 상태 확인

결과 필요할 때:
[AgentOutputTool: block=true] → 대기
```

---

## 리소스 효율성 체크리스트

### 에이전트 호출 전

```markdown
□ 직접 실행으로 가능한 작업인가?
□ 가장 적합한 에이전트 유형은?
□ 적절한 모델 선택했는가? (haiku/sonnet/opus)
□ 병렬 실행 가능한 부분이 있는가?
□ 프롬프트가 명확하고 간결한가?
```

### 여러 에이전트 필요 시

```markdown
□ 독립적인 작업은 병렬로 실행하는가?
□ 의존적인 작업만 순차로 실행하는가?
□ 동일 에이전트 유형 중복 호출이 없는가?
□ 작업 분할이 효율적인가?
```

### 결과 처리 시

```markdown
□ 모든 결과를 적절히 활용하는가?
□ 실패한 작업에 대한 대응이 있는가?
□ 결과 통합이 효율적인가?
□ 불필요한 추가 호출을 피하는가?
```

---

## 실전 예시

### 예시 1: 효율적인 코드 리뷰

```markdown
## 비효율적
[Task: quality-engineer] "전체 코드베이스 리뷰"
→ 너무 큰 범위, 시간 오래 걸림

## 효율적

Step 1: 변경된 파일 식별 (직접)
git diff --name-only

Step 2: 파일별 병렬 리뷰
[Task: quality-engineer] "src/auth.py 리뷰"
[Task: quality-engineer] "src/api.py 리뷰"
[Task: security-engineer] "src/crypto.py 리뷰"

Step 3: 결과 통합
오케스트레이터가 종합
```

### 예시 2: 효율적인 버그 조사

```markdown
## 비효율적
[Task: general-purpose] "버그 원인 찾아줘"
→ 범위가 넓어 비효율적

## 효율적

Step 1: 로그 분석 (직접)
Grep(pattern="error|exception")

Step 2: 관련 코드 읽기 (직접)
Read(suspect_files)

Step 3: 집중 분석 (에이전트)
[Task: backend-architect]
"이 코드의 {특정 부분}에서 {특정 증상}의 원인 분석"
```

### 예시 3: 효율적인 기능 구현

```markdown
## 설계 단계 (opus 가치 있음)
[Task: backend-architect, model="opus"]
"중요한 아키텍처 결정"

## 구현 단계 (sonnet 충분)
[Task: python-expert]
"설계에 따른 구현"

## 검증 단계 (haiku로 빠르게)
[Task: Explore, model="haiku"]
"구현 결과 빠른 검증"
```

---

## Quick Reference

```yaml
모델 선택:
  opus: 중요 결정, 복잡한 분석
  sonnet: 일반 작업 (기본)
  haiku: 단순 작업, 빠른 피드백

효율성 원칙:
  1. 직접 실행 가능하면 Task 안 씀
  2. 병렬 가능하면 한 메시지에 여러 Task
  3. 작업 크기에 맞는 모델 선택
  4. 큰 작업은 분할하여 병렬화

비용 최적화:
  - 정보 수집: 직접 (Read, Grep)
  - 핵심 분석: 에이전트
  - 후처리: 직접

시간 최적화:
  - 독립 작업: 병렬
  - 의존 작업: 순차 (각 단계 내 병렬화)
  - 긴 작업: 백그라운드

실패 대응:
  1. 피드백 재요청
  2. 다른 에이전트
  3. 작업 분할
  4. 직접 처리
```
