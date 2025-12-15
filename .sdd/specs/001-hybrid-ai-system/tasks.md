# Tasks: Hybrid AI Evolution System (HAES)

> **Feature Number**: 001  
> **Status**: ✅ Complete  
> **Created**: 2025-12-14  
> **Last Updated**: 2025-12-14

---

## Task Execution Rules

### Test-Driven Development (Article III - NON-NEGOTIABLE)

**EVERY implementation task MUST follow this sequence**:

1. **Write Test** → User reviews and approves
2. **Run Test** → Confirm it FAILS (RED)
3. **Implement** → Write minimum code to pass
4. **Run Test** → Confirm it PASSES (GREEN)
5. **Refactor** → Improve without breaking tests

**NO IMPLEMENTATION without prior test approval.**

---

## Progress Overview

```
[Spec] HAES (45/45 tasks, 100%) ✅ {#spec-root}
│
├─ [Phase] 1. Setup & Infrastructure (8/8) ✅ {#phase-1}
├─ [Phase] 2. Data Layer (6/6) ✅ {#phase-2}
├─ [Phase] 3. Router Engine (4/4) ✅ {#phase-3}
├─ [Phase] 4. Executor Engine (4/4) ✅ {#phase-4}
├─ [Phase] 5. Evolution Engine (2/2) ✅ {#phase-5}
├─ [Phase] 6. Integration & Testing (4/4) ✅ {#phase-6}
└─ [Bonus] Web API (FastAPI) ✅ {#bonus-api}
```

**테스트 현황**: 69개 테스트 통과 ✅

**구현 완료 모듈**:
- SkillStore (SKILL 로드, 인덱싱, 검색)
- AgentPool (에이전트 로드, 선택)
- FeedbackStore (피드백 저장)
- KeywordMatcher (키워드 매칭)
- HybridRouter (하이브리드 라우팅: 키워드 → gpt-5-mini → gpt-5.1)
- EvolutionEngine (패턴 학습)
- HybridAISystem (통합 시스템)
- OpenAIClient (GPT-5 모델 연동)
- FastAPI Web API (REST 엔드포인트)
- CLI (대화형 인터페이스)

---

## Phase 1: Setup & Infrastructure `[P]`

> **Estimated Effort**: Small  
> **Dependencies**: None  
> **Parallel**: Yes

### Task 1.1: Project Initialization
**File**: `pyproject.toml`, `requirements.txt`  
**Type**: Setup  
**Dependencies**: None  
**Parallel**: Yes `[P]`

**Steps**:
1. pyproject.toml 생성 (패키지 메타데이터)
2. requirements.txt 생성 (의존성)
3. src/haes/__init__.py 생성
4. tests/__init__.py, tests/conftest.py 생성

**Required Dependencies**:
```
chromadb>=0.4.0
openai>=1.0.0
anthropic>=0.7.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
loguru>=0.7.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
aiohttp>=3.9.0
PyYAML>=6.0.0
```

**Validation**:
- [ ] `pip install -e .` 성공
- [ ] `pytest --version` 실행 확인
- [ ] 디렉토리 구조 생성 완료

---

### Task 1.2: Configuration Module
**File**: `src/haes/config.py`  
**Type**: Implementation  
**Dependencies**: Task 1.1

**Steps**:
1. pydantic-settings 기반 Config 클래스
2. 환경 변수 지원 (OPENAI_API_KEY, ANTHROPIC_API_KEY)
3. 경로 설정 (skills_path, agents_path, persist_dir)

**Implementation**:
```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Config(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Paths
    skills_path: Path = Path("AI-research-SKILLs")
    agents_path: Path = Path(".claude/agents")
    persist_dir: Path = Path("./skill_vectordb")
    
    # Models
    routing_model: str = "claude-3-5-haiku-latest"
    main_model: str = "claude-3-5-sonnet-latest"
    embedding_model: str = "text-embedding-3-small"
    
    class Config:
        env_file = ".env"
```

**Validation**:
- [ ] Config 로드 테스트
- [ ] 환경 변수 오버라이드 테스트

---

### Task 1.3: Data Models
**File**: `src/haes/models/`  
**Type**: Implementation  
**Dependencies**: Task 1.1  
**Parallel**: Yes `[P]`

**Files to Create**:
- `src/haes/models/__init__.py`
- `src/haes/models/skill.py`
- `src/haes/models/agent.py`
- `src/haes/models/routing.py`
- `src/haes/models/execution.py`
- `src/haes/models/feedback.py`

**Models**:
```python
# skill.py
@dataclass
class Skill:
    skill_id: str
    name: str
    description: str
    tags: List[str]
    content: str
    path: str

# agent.py
@dataclass
class Agent:
    agent_id: str
    tier: str
    name: str
    description: str
    system_prompt: str

# routing.py
class ExecutionMode(Enum):
    SKILL_ONLY = "skill_only"
    SKILL_AGENT = "skill_agent"
    PARALLEL = "parallel"
    MULTI_AGENT = "multi_agent"

@dataclass
class RoutingDecision:
    mode: ExecutionMode
    skills: List[str]
    agents: List[str]
    reason: str
    confidence: float

# execution.py
@dataclass
class ExecutionResult:
    mode: str
    response: str
    skills_used: List[str]
    agents_used: List[str]
    cost_estimate: str
    execution_time: float
    query: str

# feedback.py
@dataclass
class Feedback:
    query: str
    skills_used: List[str]
    score: int
    comment: str
    timestamp: str
```

**Validation**:
- [ ] 모든 모델 import 성공
- [ ] dataclass 직렬화 테스트

---

### Task 1.4: Test Fixtures
**File**: `tests/fixtures/`, `tests/conftest.py`  
**Type**: Test Infrastructure  
**Dependencies**: Task 1.1, Task 1.3

**Steps**:
1. 샘플 SKILL 파일 생성 (3개)
2. 샘플 Agent 파일 생성 (3개)
3. pytest 픽스처 정의

**Fixtures**:
```python
# tests/conftest.py

@pytest.fixture
def sample_skill():
    return Skill(
        skill_id="test-skill",
        name="test-skill",
        description="Test skill for unit tests",
        tags=["test", "unit"],
        content="# Test SKILL\n\nTest content.",
        path="/tmp/test-skill/SKILL.md"
    )

@pytest.fixture
def sample_agent():
    return Agent(
        agent_id="test-agent",
        tier="tier1-core",
        name="test-agent",
        description="Test agent",
        system_prompt="You are a test agent."
    )

@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing without API calls"""
    pass
```

**Validation**:
- [ ] `pytest tests/` 실행 시 픽스처 로드 확인
- [ ] 샘플 파일 존재 확인

---

### [CHECKPOINT 1]: Phase 1 완료 검증

- [ ] 프로젝트 구조 생성 완료
- [ ] 의존성 설치 성공
- [ ] Config 모듈 작동
- [ ] 모든 데이터 모델 정의됨
- [ ] pytest 픽스처 작동

---

## Phase 2: Data Layer (TDD)

> **Estimated Effort**: Medium  
> **Dependencies**: Phase 1  
> **Critical**: Vector DB 및 SKILL 로딩

### Task 2.1: Write SkillStore Tests (RED)
**File**: `tests/unit/test_skill_store.py`  
**Type**: Test  
**Dependencies**: Task 1.4

**Test Cases**:
```python
class TestSkillStore:
    def test_init_creates_vectordb(self, tmp_path):
        """Vector DB가 초기화되어야 함"""
        store = SkillStore(skills_path="fixtures", persist_dir=str(tmp_path))
        assert store.collection is not None
        
    def test_index_skill_adds_to_vectordb(self, sample_skill, skill_store):
        """SKILL 인덱싱이 Vector DB에 추가되어야 함"""
        skill_store.index_skill(sample_skill)
        results = skill_store.search("test", k=1)
        assert len(results) == 1
        
    def test_search_returns_relevant_skills(self, skill_store):
        """검색어에 관련된 SKILL이 반환되어야 함"""
        results = skill_store.search("fine-tuning lora", k=3)
        assert any("fine-tuning" in r.skill_id for r in results)
        
    def test_load_returns_skill_content(self, skill_store):
        """SKILL ID로 내용을 로드해야 함"""
        content = skill_store.load(["03-fine-tuning"])
        assert "LoRA" in content or "파인튜닝" in content
        
    def test_load_uses_cache(self, skill_store):
        """두 번째 로드는 캐시를 사용해야 함"""
        skill_store.load(["03-fine-tuning"])
        skill_store.load(["03-fine-tuning"])  # cache hit
        assert "03-fine-tuning" in skill_store.cache
        
    def test_get_compressed_index_returns_string(self, skill_store):
        """압축 인덱스가 문자열로 반환되어야 함"""
        index = skill_store.get_compressed_index()
        assert isinstance(index, str)
        assert "fine-tuning" in index
```

**User Approval Required**:
- [ ] User reviews test scenarios
- [ ] User confirms tests match requirements
- [ ] User approves proceeding to implementation

**Validation** (RED Phase):
- [ ] Tests written
- [ ] Tests run and FAIL (as expected)
- [ ] Failure messages are clear

---

### Task 2.2: Implement SkillStore (GREEN)
**File**: `src/haes/stores/skill_store.py`  
**Type**: Implementation  
**Dependencies**: Task 2.1 (after user approval)

**Implementation Steps**:
1. ChromaDB PersistentClient 초기화
2. SKILL.md 파싱 (YAML frontmatter + content)
3. Vector 인덱싱 로직
4. 검색 및 로드 메서드
5. 캐싱 로직
6. 압축 인덱스 생성

**Key Methods**:
```python
class SkillStore:
    def __init__(self, skills_path: str, persist_dir: str):
        ...
    
    def _parse_skill_file(self, path: Path) -> Skill:
        """YAML frontmatter 파싱"""
        ...
    
    def index_all_skills(self) -> int:
        """모든 SKILL 인덱싱"""
        ...
    
    def search(self, query: str, k: int = 3) -> List[Skill]:
        """의미 기반 검색"""
        ...
    
    def load(self, skill_ids: List[str]) -> str:
        """SKILL 내용 로드 (캐싱)"""
        ...
    
    def get_compressed_index(self) -> str:
        """라우팅용 압축 인덱스"""
        ...
```

**Validation** (GREEN Phase):
- [ ] All tests pass
- [ ] No new failing tests
- [ ] Code coverage > 80%

---

### Task 2.3: Write AgentPool Tests (RED)
**File**: `tests/unit/test_agent_pool.py`  
**Type**: Test  
**Dependencies**: Task 1.4

**Test Cases**:
```python
class TestAgentPool:
    def test_loads_tier1_agents(self, agent_pool):
        """Tier1 에이전트가 로드되어야 함"""
        agents = agent_pool.list_by_tier("tier1-core")
        assert len(agents) > 0
        
    def test_get_returns_agent_by_id(self, agent_pool):
        """에이전트 ID로 조회해야 함"""
        agent = agent_pool.get("backend-developer")
        assert agent is not None
        assert agent.tier == "tier1-core"
        
    def test_get_returns_none_for_unknown(self, agent_pool):
        """없는 에이전트는 None 반환"""
        agent = agent_pool.get("nonexistent-agent")
        assert agent is None
        
    def test_loads_all_tiers(self, agent_pool):
        """모든 Tier에서 에이전트 로드"""
        all_agents = agent_pool.list_all()
        assert len(all_agents) >= 20  # Tier1만 20개
```

---

### Task 2.4: Implement AgentPool (GREEN)
**File**: `src/haes/stores/agent_pool.py`  
**Type**: Implementation  
**Dependencies**: Task 2.3

**Implementation Steps**:
1. 3개 Tier 디렉토리 순회
2. .md 파일 파싱 (YAML frontmatter)
3. Agent 객체 생성 및 저장
4. 조회 메서드 구현

---

### Task 2.5: Write FeedbackStore Tests (RED)
**File**: `tests/unit/test_feedback_store.py`  
**Type**: Test  
**Dependencies**: Task 1.4

**Test Cases**:
```python
class TestFeedbackStore:
    def test_record_saves_feedback(self, feedback_store):
        """피드백이 저장되어야 함"""
        feedback_store.record(query="test", skills=["test"], score=5)
        assert len(feedback_store.all()) == 1
        
    def test_get_by_skill_filters_correctly(self, feedback_store):
        """SKILL별 피드백 필터링"""
        feedback_store.record(query="q1", skills=["skill-a"], score=5)
        feedback_store.record(query="q2", skills=["skill-b"], score=3)
        results = feedback_store.get_by_skill("skill-a")
        assert len(results) == 1
```

---

### Task 2.6: Implement FeedbackStore (GREEN)
**File**: `src/haes/stores/feedback_store.py`  
**Type**: Implementation  
**Dependencies**: Task 2.5

---

### [CHECKPOINT 2]: Phase 2 완료 검증

- [ ] SkillStore 모든 테스트 통과
- [ ] AgentPool 모든 테스트 통과
- [ ] FeedbackStore 모든 테스트 통과
- [ ] Vector DB 영구 저장 확인
- [ ] 실제 SKILL 파일 로드 테스트

---

## Phase 3: Router Engine (TDD)

> **Estimated Effort**: Medium  
> **Dependencies**: Phase 2

### Task 3.1: Write KeywordMatcher Tests (RED)
**File**: `tests/unit/test_keyword_matcher.py`  
**Type**: Test

**Test Cases**:
```python
class TestKeywordMatcher:
    def test_matches_korean_keywords(self, matcher):
        """한국어 키워드 매칭"""
        result = matcher.match("LoRA 파인튜닝 방법")
        assert "03-fine-tuning" in result
        
    def test_matches_english_keywords(self, matcher):
        """영어 키워드 매칭"""
        result = matcher.match("vLLM inference serving")
        assert "12-inference-serving" in result
        
    def test_returns_empty_for_no_match(self, matcher):
        """매칭 없으면 빈 리스트"""
        result = matcher.match("random unrelated query")
        assert result == []
        
    def test_returns_max_3_matches(self, matcher):
        """최대 3개 매칭"""
        result = matcher.match("transformer lora vllm deepspeed")
        assert len(result) <= 3
```

---

### Task 3.2: Implement KeywordMatcher (GREEN)
**File**: `src/haes/router/keyword_matcher.py`  
**Type**: Implementation  
**Dependencies**: Task 3.1

---

### Task 3.3: Write HybridRouter Tests (RED)
**File**: `tests/unit/test_router.py`  
**Type**: Test

**Test Cases**:
```python
class TestHybridRouter:
    @pytest.mark.asyncio
    async def test_simple_query_routes_skill_only(self, router):
        """단순 질문은 SKILL_ONLY"""
        decision = await router.route("LoRA가 뭐야?")
        assert decision.mode == ExecutionMode.SKILL_ONLY
        
    @pytest.mark.asyncio
    async def test_technical_query_routes_skill_agent(self, router):
        """기술적 구현 요청은 SKILL_AGENT"""
        decision = await router.route("vLLM으로 70B 모델 서빙 설정해줘")
        assert decision.mode == ExecutionMode.SKILL_AGENT
        
    @pytest.mark.asyncio
    async def test_multiple_tasks_routes_parallel(self, router):
        """복수 독립 작업은 PARALLEL"""
        decision = await router.route("API 만들고 테스트 작성하고 문서화해줘")
        assert decision.mode == ExecutionMode.PARALLEL
        
    @pytest.mark.asyncio
    async def test_collaboration_routes_multi_agent(self, router):
        """협업 필요 시 MULTI_AGENT"""
        decision = await router.route("시스템 설계하고 보안 검토해줘")
        assert decision.mode == ExecutionMode.MULTI_AGENT
        
    @pytest.mark.asyncio
    async def test_decision_includes_skills(self, router):
        """결정에 SKILL ID 포함"""
        decision = await router.route("파인튜닝 방법")
        assert len(decision.skills) > 0
        
    @pytest.mark.asyncio
    async def test_decision_has_confidence(self, router):
        """결정에 신뢰도 포함"""
        decision = await router.route("test query")
        assert 0 <= decision.confidence <= 1
```

---

### Task 3.4: Implement HybridRouter (GREEN)
**File**: `src/haes/router/hybrid_router.py`  
**Type**: Implementation  
**Dependencies**: Task 3.3

**Implementation**:
- 복잡도 분석기 (_analyze_complexity)
- 키워드 매칭 우선 적용
- LLM 라우팅 폴백 (Haiku)
- 4가지 모드 결정 로직

---

### [CHECKPOINT 3]: Phase 3 완료 검증

- [ ] KeywordMatcher 테스트 통과
- [ ] HybridRouter 테스트 통과
- [ ] 4가지 모드 정확히 분류
- [ ] 라우팅 지연 시간 < 500ms

---

## Phase 4: Executor Engine (TDD)

> **Estimated Effort**: Large  
> **Dependencies**: Phase 2, Phase 3

### Task 4.1: Write SkillOnlyExecutor Tests (RED)
**File**: `tests/unit/test_executor.py`  
**Type**: Test

**Test Cases**:
```python
class TestSkillOnlyExecutor:
    @pytest.mark.asyncio
    async def test_loads_skills_and_calls_llm(self, executor, mock_llm):
        """SKILL 로드 후 LLM 호출"""
        result = await executor.execute_skill_only(
            "LoRA 설명해줘",
            skills=["03-fine-tuning"]
        )
        assert result.response is not None
        assert result.mode == "skill_only"
        
    @pytest.mark.asyncio
    async def test_includes_skill_context(self, executor, mock_llm):
        """SKILL 내용이 LLM 컨텍스트에 포함"""
        # mock_llm에서 system prompt 확인
        pass
```

---

### Task 4.2: Implement SkillOnlyExecutor (GREEN)
**File**: `src/haes/executor/skill_only.py`  
**Type**: Implementation

---

### Task 4.3: Write SkillAgentExecutor Tests (RED)
**File**: `tests/unit/test_executor.py`  
**Type**: Test

---

### Task 4.4: Implement SkillAgentExecutor (GREEN)
**File**: `src/haes/executor/skill_agent.py`  
**Type**: Implementation

---

### Task 4.5: Write ParallelExecutor Tests (RED)
**File**: `tests/unit/test_executor.py`  
**Type**: Test

**Test Cases**:
```python
class TestParallelExecutor:
    @pytest.mark.asyncio
    async def test_executes_tasks_concurrently(self, executor):
        """작업이 동시에 실행됨"""
        start = time.time()
        result = await executor.execute_parallel(
            "API 만들고 테스트 작성하고 문서화해줘",
            agents=["backend-dev", "qa-expert", "tech-writer"]
        )
        elapsed = time.time() - start
        # 순차 실행보다 빠름
        assert elapsed < 20  # 순차면 30초 이상
        
    @pytest.mark.asyncio
    async def test_integrates_results(self, executor):
        """결과가 통합됨"""
        result = await executor.execute_parallel(...)
        assert len(result.sub_results) == 3
        assert result.response  # 통합된 응답
```

---

### Task 4.6: Implement ParallelExecutor (GREEN)
**File**: `src/haes/executor/parallel.py`  
**Type**: Implementation

**Key**: `asyncio.gather(*tasks)`

---

### Task 4.7: Write MultiAgentExecutor Tests (RED)
**File**: `tests/unit/test_executor.py`  
**Type**: Test

---

### Task 4.8: Implement MultiAgentExecutor (GREEN)
**File**: `src/haes/executor/multi_agent.py`  
**Type**: Implementation

---

### Task 4.9: Implement HybridExecutor (Integration)
**File**: `src/haes/executor/hybrid_executor.py`  
**Type**: Implementation

**모든 실행기 통합**:
```python
class HybridExecutor:
    async def execute(self, decision: RoutingDecision, query: str):
        if decision.mode == ExecutionMode.SKILL_ONLY:
            return await self.skill_only.execute(query, decision.skills)
        elif decision.mode == ExecutionMode.SKILL_AGENT:
            return await self.skill_agent.execute(query, decision.skills, decision.agents[0])
        elif decision.mode == ExecutionMode.PARALLEL:
            return await self.parallel.execute(query, decision.skills, decision.agents)
        else:
            return await self.multi_agent.execute(query, decision.skills, decision.agents)
```

---

### [CHECKPOINT 4]: Phase 4 완료 검증

- [ ] 4가지 실행기 모두 테스트 통과
- [ ] HybridExecutor 통합 테스트 통과
- [ ] 병렬 실행 성능 확인

---

## Phase 5: Evolution Engine

> **Estimated Effort**: Medium  
> **Dependencies**: Phase 2

### Task 5.1: Write EvolutionEngine Tests (RED)
**File**: `tests/unit/test_evolution.py`  
**Type**: Test

**Test Cases**:
```python
class TestEvolutionEngine:
    def test_records_feedback(self, evolution):
        """피드백 기록"""
        evolution.record_feedback(
            result=ExecutionResult(query="test", skills_used=["s1"], ...),
            feedback="good",
            score=5
        )
        assert len(evolution.feedback_db) == 1
        
    def test_updates_routing_stats(self, evolution):
        """라우팅 통계 업데이트"""
        evolution.record_feedback(...)
        assert "s1" in evolution.routing_stats
        
    def test_learns_success_pattern(self, evolution):
        """성공 패턴 학습"""
        for _ in range(5):
            evolution.record_feedback(result=..., score=5)
        assert len(evolution.learned_patterns) > 0
        
    def test_triggers_improvement_on_low_score(self, evolution):
        """낮은 점수 시 개선 트리거"""
        result = evolution.record_feedback(result=..., score=2)
        # suggestion 반환 확인
        
    def test_get_routing_hints_returns_learned_pattern(self, evolution):
        """학습된 패턴 힌트 반환"""
        # 충분한 성공 패턴 후
        hints = evolution.get_routing_hints("similar query")
        assert hints["confidence"] > 0.8
```

---

### Task 5.2: Implement EvolutionEngine (GREEN)
**File**: `src/haes/evolution/evolution_engine.py`  
**Type**: Implementation

---

### [CHECKPOINT 5]: Phase 5 완료 검증

- [ ] 피드백 수집 동작
- [ ] 라우팅 통계 업데이트
- [ ] 성공 패턴 학습
- [ ] 힌트 기반 라우팅

---

## Phase 6: Integration & Testing

> **Estimated Effort**: Medium  
> **Dependencies**: Phase 1-5

### Task 6.1: Implement HybridAISystem
**File**: `src/haes/system.py`  
**Type**: Implementation

**통합 클래스**:
```python
class HybridAISystem:
    def __init__(self, config: Config):
        self.skill_store = SkillStore(config.skills_path, config.persist_dir)
        self.agent_pool = AgentPool(config.agents_path)
        self.router = HybridRouter(self.skill_store, ...)
        self.executor = HybridExecutor(self.skill_store, self.agent_pool, ...)
        self.evolution = EvolutionEngine(self.skill_store)
        
    async def chat(self, query: str) -> ExecutionResult:
        ...
        
    def feedback(self, feedback_text: str, score: int):
        ...
```

---

### Task 6.2: Write Integration Tests
**File**: `tests/integration/test_system.py`  
**Type**: Integration Test

**Test Cases**:
```python
class TestHybridAISystemIntegration:
    @pytest.mark.asyncio
    async def test_end_to_end_skill_only(self):
        """SKILL_ONLY 전체 흐름"""
        system = HybridAISystem(test_config)
        result = await system.chat("LoRA가 뭐야?")
        assert result.mode == "skill_only"
        assert len(result.skills_used) > 0
        
    @pytest.mark.asyncio
    async def test_feedback_affects_routing(self):
        """피드백이 라우팅에 영향"""
        system = HybridAISystem(test_config)
        # 동일 쿼리 반복 + 피드백
        for _ in range(5):
            result = await system.chat("LoRA 파인튜닝")
            system.feedback("좋아요", 5)
        # 이후 힌트 기반 라우팅 확인
```

---

### Task 6.3: Performance Testing
**File**: `tests/performance/test_performance.py`  
**Type**: Performance Test

**Tests**:
- 라우팅 지연 시간 < 500ms
- SKILL_ONLY 응답 < 3s
- Vector 검색 < 200ms

---

### Task 6.4: Documentation
**File**: `README.md`, `docs/`  
**Type**: Documentation

**Contents**:
- 설치 방법
- 빠른 시작
- API 레퍼런스
- 아키텍처 설명

---

### [FINAL CHECKPOINT]: 전체 완료 검증

- [ ] 모든 단위 테스트 통과
- [ ] 모든 통합 테스트 통과
- [ ] 성능 목표 달성
- [ ] 문서화 완료
- [ ] 실제 SKILL/Agent로 동작 확인

---

## Task Progress Tracking

| Task ID | Description | Status | Dependencies | Notes |
|---------|-------------|--------|--------------|-------|
| 1.1 | Project Setup | ☐ Not Started | - | - |
| 1.2 | Config Module | ☐ Not Started | 1.1 | - |
| 1.3 | Data Models | ☐ Not Started | 1.1 | Parallel |
| 1.4 | Test Fixtures | ☐ Not Started | 1.1, 1.3 | - |
| 2.1 | SkillStore Tests | ☐ Not Started | 1.4 | User approval |
| 2.2 | SkillStore Impl | ☐ Not Started | 2.1 | - |
| 2.3 | AgentPool Tests | ☐ Not Started | 1.4 | - |
| 2.4 | AgentPool Impl | ☐ Not Started | 2.3 | - |
| 2.5 | FeedbackStore Tests | ☐ Not Started | 1.4 | - |
| 2.6 | FeedbackStore Impl | ☐ Not Started | 2.5 | - |
| 3.1 | KeywordMatcher Tests | ☐ Not Started | 2.2 | - |
| 3.2 | KeywordMatcher Impl | ☐ Not Started | 3.1 | - |
| 3.3 | HybridRouter Tests | ☐ Not Started | 3.2 | - |
| 3.4 | HybridRouter Impl | ☐ Not Started | 3.3 | - |
| 4.1-4.9 | Executor Engine | ☐ Not Started | 3.4 | - |
| 5.1-5.2 | Evolution Engine | ☐ Not Started | 2.6 | - |
| 6.1-6.4 | Integration | ☐ Not Started | All | - |

**Status Legend**:
- ☐ Not Started
- ◐ In Progress
- ◕ In Review
- ☑ Complete
- ☒ Blocked

---

## Definition of Done

### For Test Tasks
- [ ] Tests written and reviewed
- [ ] User has approved test scenarios
- [ ] Tests run and fail (RED phase confirmed)
- [ ] Test coverage is comprehensive

### For Implementation Tasks
- [ ] Code written to pass tests
- [ ] All tests pass (GREEN phase confirmed)
- [ ] Code review completed
- [ ] No complexity violations

---

## Notes & References

- **Specification**: `spec.md`
- **Implementation Plan**: `plan.md`
- **SKILL Source**: `/home/cafe99/anti-gravity-project/AI-research-SKILLs/`
- **Agent Source**: `/home/cafe99/anti-gravity-project/.claude/agents/`
