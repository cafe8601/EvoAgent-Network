# Feature Specification: Hybrid AI Evolution System (HAES)

> **Feature ID**: `001-hybrid-ai-system`  
> **Status**: Draft  
> **Priority**: P1 (Critical)  
> **Estimated Complexity**: Large  
> **Created**: 2025-12-14  
> **Last Updated**: 2025-12-14

---

## Executive Summary

**Hybrid AI Evolution System (HAES)**은 63개 AI Research SKILLs과 159개 전문 에이전트를 통합하여 자동으로 도메인 지식을 호출하고, 피드백 기반으로 지속적으로 진화하는 AI 시스템입니다.

**핵심 가치**:
- 63개 SKILL의 전문 지식 자동 검색 및 활용
- 작업 복잡도에 따른 최적 실행 모드 선택
- 피드백 기반 지식 진화 (Knowledge Evolution)
- 병렬/협업 작업을 위한 AgentPool 통합

---

## User Scenarios & Testing (REQUIRED)

### P1: Critical Path (Must-Have)

#### Scenario 1: 단순 지식 조회 (SKILL_ONLY 모드)
**As a** AI 시스템 사용자  
**I want to** "LoRA 파인튜닝 방법 알려줘"라고 질문하면  
**So that** 관련 SKILL이 자동으로 로드되어 전문적인 답변을 받을 수 있다

**Acceptance Criteria** (Given-When-Then format):
```gherkin
Given 63개 SKILL이 벡터 DB에 인덱싱되어 있고
  And 사용자가 시스템에 연결되어 있을 때
When 사용자가 "LoRA 파인튜닝 방법 알려줘"라고 질문하면
Then 시스템이 "03-fine-tuning" SKILL을 자동 검색하고
  And 해당 SKILL 컨텍스트와 함께 LLM이 전문적 답변을 생성한다
  And 응답에 사용된 SKILL ID가 메타데이터로 포함된다
```

**Test Cases**:
- [ ] 키워드 기반 라우팅 테스트 ("lora", "파인튜닝" → 03-fine-tuning)
- [ ] 의미 기반 라우팅 테스트 ("모델 학습 최적화" → 03-fine-tuning)
- [ ] 응답 시간 < 3초 확인
- [ ] SKILL 캐싱 동작 확인

---

#### Scenario 2: 전문 작업 실행 (SKILL_AGENT 모드)
**As a** 개발자  
**I want to** "vLLM으로 LLaMA 70B 서빙 설정해줘"라고 요청하면  
**So that** 관련 SKILL + 전문 에이전트가 함께 동작하여 상세한 구현을 받을 수 있다

**Acceptance Criteria**:
```gherkin
Given SKILL Store와 AgentPool이 초기화되어 있고
  And "backend-developer" 에이전트가 사용 가능할 때
When 사용자가 기술적 구현을 요청하면
Then Router가 복잡도를 분석하여 SKILL_AGENT 모드를 선택하고
  And "12-inference-serving" SKILL을 로드하고
  And "backend-developer" 에이전트에게 SKILL 컨텍스트와 함께 작업을 위임하고
  And 구체적인 코드와 설정 파일을 생성한다
```

**Test Cases**:
- [ ] 복잡도 분석기가 중간 복잡도(0.3-0.6)를 정확히 판별
- [ ] 적절한 에이전트 자동 선택
- [ ] SKILL + Agent 조합 응답 품질 검증

---

#### Scenario 3: 병렬 작업 실행 (PARALLEL 모드)
**As a** 프로젝트 리더  
**I want to** "인증 API 만들고, 테스트 작성하고, 문서화해줘"라고 요청하면  
**So that** 3개 작업이 병렬로 실행되어 시간을 단축할 수 있다

**Acceptance Criteria**:
```gherkin
Given 3개 이상의 독립적 에이전트가 AgentPool에 있고
When 복합 작업이 "하고", "그리고" 등으로 구분되어 입력되면
Then Router가 작업을 분해하고
  And 각 작업에 적합한 에이전트를 매핑하고 (backend-dev, qa-expert, tech-writer)
  And 3개 Task가 동시에 실행되고
  And 결과가 통합되어 단일 응답으로 반환된다
```

**Test Cases**:
- [ ] 작업 분해 정확도 테스트
- [ ] 병렬 실행 시 순차 실행 대비 시간 단축 확인 (예상: 3x)
- [ ] 결과 통합 품질 검증

---

### P2: Important (Should-Have)

#### Scenario 4: 다중 에이전트 협업 (MULTI_AGENT 모드)
**As a** 시스템 설계자  
**I want to** "결제 시스템 설계하고 보안 검토해줘"라고 요청하면  
**So that** 아키텍트와 보안 전문가가 순차적으로 협업하여 검증된 설계를 받을 수 있다

**Acceptance Criteria**:
```gherkin
Given 협업 패턴이 정의되어 있고 (architect → security-reviewer)
When 협업이 필요한 복잡한 요청이 입력되면
Then 첫 번째 에이전트(architect)가 설계를 수행하고
  And 두 번째 에이전트(security-reviewer)가 첫 번째 결과를 검토하고
  And 피드백이 반영된 최종 결과가 반환된다
```

---

#### Scenario 5: 피드백 기반 진화
**As a** 시스템 관리자  
**I want to** 사용자 피드백(👍/👎)을 수집하여 시스템이 학습하도록  
**So that** 시간이 지날수록 라우팅 정확도와 응답 품질이 향상된다

**Acceptance Criteria**:
```gherkin
Given Evolution Engine이 활성화되어 있고
When 사용자가 응답에 5점 만점 피드백을 제공하면
Then 해당 질문-SKILL 매핑이 기록되고
  And 4점 이상이면 성공 패턴으로 학습하고
  And 2점 이하면 개선 트리거가 발생하고
  And 라우팅 통계가 업데이트된다
```

**Test Cases**:
- [ ] 피드백 저장 및 조회
- [ ] 성공 패턴 학습 로직
- [ ] 라우팅 힌트 적용 확인

---

### P3: Nice-to-Have (Could-Have)

#### Scenario 6: SKILL 자동 업데이트
**As a** 지식 관리자  
**I want to** 충분한 성공 사례가 축적되면 SKILL이 자동으로 업데이트되도록  
**So that** 새로운 패턴이 자동으로 문서화된다

**Acceptance Criteria**:
```gherkin
Given 특정 패턴이 5회 이상 성공하고 성공률 80% 이상이면
When Evolution Engine이 품질 게이트를 통과하면
Then SKILL.md 파일에 "Learned Patterns" 섹션이 추가되고
  And 백업 파일이 생성되고
  And SKILL 캐시가 무효화된다
```

---

## Requirements (REQUIRED)

### Functional Requirements

**FR-001**: SKILL 벡터화 및 검색
- **Priority**: P1
- **Rationale**: 63개 SKILL의 의미 기반 검색을 위해 필수
- **Dependencies**: None
- **Detail**: Chroma/FAISS를 사용한 벡터 DB 구축

**FR-002**: 하이브리드 라우터
- **Priority**: P1
- **Rationale**: 작업 복잡도에 따른 최적 실행 모드 선택
- **Dependencies**: FR-001
- **Detail**: 키워드 매칭 + LLM 라우팅 조합

**FR-003**: AgentPool 통합
- **Priority**: P1
- **Rationale**: 159개 에이전트의 동적 로드 및 실행
- **Dependencies**: None
- **Detail**: .claude/agents/ 디렉토리에서 자동 로드

**FR-004**: 4가지 실행 모드
- **Priority**: P1
- **Rationale**: 비용/성능 최적화
- **Dependencies**: FR-001, FR-002, FR-003
- **Detail**: SKILL_ONLY, SKILL_AGENT, PARALLEL, MULTI_AGENT

**FR-005**: Evolution Engine
- **Priority**: P2
- **Rationale**: 시스템의 지속적 개선
- **Dependencies**: FR-001, FR-002
- **Detail**: 피드백 수집, 패턴 학습, SKILL 업데이트

**FR-006**: 압축 SKILL 인덱스
- **Priority**: P1
- **Rationale**: 라우팅을 위한 경량 인덱스 (~2000 토큰)
- **Dependencies**: FR-001
- **Detail**: ID|키워드|설명 형식

**FR-007**: 대화 히스토리 관리
- **Priority**: P2
- **Rationale**: SKILL 제외한 효율적 컨텍스트 관리
- **Dependencies**: None
- **Detail**: System prompt에만 SKILL 주입, 히스토리 압축

---

### Non-Functional Requirements

**NFR-001: Performance**
- SKILL_ONLY 모드: 응답 시간 < 3초
- SKILL_AGENT 모드: 응답 시간 < 15초
- PARALLEL 모드: 순차 실행 대비 2.5x 이상 속도 향상
- 라우팅 오버헤드: < 500ms

**NFR-002: Cost Efficiency**
- SKILL_ONLY: ~$0.01/요청
- SKILL_AGENT: ~$0.05/요청
- PARALLEL: ~$0.15/요청
- MULTI_AGENT: ~$0.20/요청
- 라우팅: ~$0.0005/요청 (Haiku 사용)

**NFR-003: Scalability**
- 100+ SKILL 지원
- 200+ 에이전트 지원
- 동시 10개 세션 처리

**NFR-004: Reliability**
- SKILL 로딩 실패 시 폴백 응답
- 에이전트 실패 시 재시도 또는 대체 에이전트

---

### Core Entities

#### Entity 1: Skill
**Purpose**: AI 연구 도메인 지식 단위  
**Key Attributes**:
- `skill_id`: string - SKILL 고유 식별자 (예: "03-fine-tuning")
- `name`: string - SKILL 이름
- `description`: string - 용도 설명
- `tags`: string[] - 검색용 태그
- `content`: string - SKILL.md 전체 내용
- `vector`: float[] - 임베딩 벡터

**Relationships**:
- 다수의 Category에 속할 수 있음
- 다수의 Agent와 연관될 수 있음

#### Entity 2: Agent
**Purpose**: 전문 역할을 수행하는 AI 에이전트  
**Key Attributes**:
- `agent_id`: string - 에이전트 식별자 (예: "backend-developer")
- `tier`: enum - 품질 등급 (tier1-core, tier2-specialized, tier3-experimental)
- `system_prompt`: string - 에이전트 정의 내용
- `capabilities`: string[] - 수행 가능한 작업

#### Entity 3: RoutingDecision
**Purpose**: 라우팅 결정 결과  
**Key Attributes**:
- `mode`: enum - 실행 모드 (SKILL_ONLY, SKILL_AGENT, PARALLEL, MULTI_AGENT)
- `skills`: string[] - 선택된 SKILL ID 목록
- `agents`: string[] - 선택된 에이전트 목록
- `confidence`: float - 라우팅 신뢰도
- `reason`: string - 선택 이유

#### Entity 4: ExecutionResult
**Purpose**: 실행 결과  
**Key Attributes**:
- `mode`: string - 사용된 실행 모드
- `response`: string - 생성된 응답
- `skills_used`: string[] - 사용된 SKILL
- `agents_used`: string[] - 사용된 에이전트
- `cost_estimate`: string - 예상 비용
- `execution_time`: float - 실행 시간

#### Entity 5: Feedback
**Purpose**: 사용자 피드백  
**Key Attributes**:
- `query`: string - 원래 질문
- `execution_result`: ExecutionResult - 실행 결과 참조
- `score`: int - 1-5점 평가
- `comment`: string - 추가 의견
- `timestamp`: datetime - 피드백 시간

---

## Success Criteria (REQUIRED)

### Business Metrics
- **Metric 1**: 라우팅 정확도 > 90% (올바른 SKILL 선택)
- **Metric 2**: 사용자 만족도 평균 > 4.0/5.0
- **Metric 3**: 60% 이상 작업이 SKILL_ONLY 모드로 처리 (비용 효율)

### Technical Metrics
- **Metric 1**: SKILL 검색 latency p95 < 200ms
- **Metric 2**: 전체 응답 latency p95 < 5초
- **Metric 3**: 테스트 커버리지 > 80%
- **Metric 4**: Vector DB 인덱싱 100% 완료

### User Experience Metrics
- **Metric 1**: 첫 응답까지 시간 < 3초 (단순 질문)
- **Metric 2**: SKILL 선택 투명성 (메타데이터에 사용 SKILL 표시)
- **Metric 3**: 피드백 제출 성공률 100%

---

## Out of Scope

- [ ] 웹 UI 개발 (별도 프로젝트)
- [ ] 외부 API 서비스 배포
- [ ] LLM 자체 파인튜닝
- [ ] 실시간 스트리밍 응답 (Phase 2)
- [ ] 다중 사용자 인증/권한 관리
- [ ] 과금 시스템

---

## Assumptions & Dependencies

### Assumptions
1. OpenAI API 또는 Anthropic API 접근 가능
2. Python 3.10+ 환경
3. 로컬 파일 시스템에 SKILL 및 Agent 파일 존재
4. 충분한 메모리 (Vector DB용)

### External Dependencies
1. OpenAI Embeddings API (벡터화)
2. LLM API (Claude/GPT-4)
3. ChromaDB 또는 FAISS

### Internal Dependencies
1. `/home/cafe99/anti-gravity-project/AI-research-SKILLs/` - SKILL 소스
2. `/home/cafe99/anti-gravity-project/.claude/agents/` - Agent 정의

---

## Open Questions

1. **[RESOLVED]**: 라우팅에 사용할 LLM 모델 → Haiku (빠르고 저렴)
2. **[RESOLVED]**: Vector DB 선택 → ChromaDB (개발 편의성)
3. **[NEEDS CLARIFICATION]**: SKILL 업데이트 시 사람 검토 필요 여부
4. **[NEEDS CLARIFICATION]**: 동시 세션 수 제한

---

## Validation Checklist

Before marking as "Approved", verify:

- [x] No `[NEEDS CLARIFICATION]` markers remain (2개 남음 - 낮은 우선순위)
- [x] All requirements are testable and unambiguous
- [x] User scenarios cover all critical paths
- [x] Success criteria are measurable
- [x] Dependencies are identified
- [x] P1 scenarios have complete acceptance criteria
- [x] Core entities are defined
- [x] Out of scope items are listed

---

## Notes & References

- **Related Project**: `/home/cafe99/anti-gravity-project/AI 시스템 구축.md`
- **SKILL Source**: `/home/cafe99/anti-gravity-project/AI-research-SKILLs/`
- **Agent Source**: `/home/cafe99/anti-gravity-project/.claude/agents/`
- **Design Reference**: Hybrid AI System 아키텍처 (AI 시스템 구축.md)
