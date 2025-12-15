# Implementation Plan: Hybrid AI Evolution System (HAES)

> **Feature Number**: 001  
> **Status**: Planning  
> **Created**: 2025-12-14  
> **Last Updated**: 2025-12-14

---

## Phase -1: Pre-Implementation Gates

### Constitutional Compliance Check

#### Article I: Library-First Principle
- [x] **Compliance**: 핵심 로직을 `haes/` 라이브러리로 구현
- **Justification**: CLI, API, Web 모두 동일 라이브러리 사용

#### Article III: Test-First Imperative (NON-NEGOTIABLE)
- [x] **Compliance**: pytest 기반 TDD 적용
- **Commitment**: RED-GREEN-REFACTOR 사이클 준수

#### Article VII: Simplicity Gate
- [x] **Compliance**: 3개 프로젝트 미만
- **Current Count**: 1 (haes 단일 패키지)

#### Article VIII: Anti-Abstraction Gate
- [x] **Compliance**: LangChain/ChromaDB 직접 사용 (래퍼 없음)
- [x] **Compliance**: 단일 모델 표현

#### Article IX: Integration-First Gate
- [x] **Contracts Defined**: 스펙에 정의됨
- [ ] **Contract Tests Written**: Task에서 작성
- [ ] **Integration Tests First**: Task에서 작성

---

### Complexity Tracking

| Constitutional Violation | Why Needed | Simpler Alternative Rejected Because |
|--------------------------|------------|--------------------------------------|
| None                     | -          | -                                    |

**Current Complexity Score**: Medium

---

## Phase 0: Technical Foundation

### Technology Stack Selection

#### Core Technologies

- **Language/Runtime**: Python 3.10+
  - **Rationale**: AI/ML 생태계 지원, LangChain 호환성
  - **Alternatives Considered**: TypeScript (rejected - Python이 AI 도구 지원 우수)

- **Vector Database**: ChromaDB
  - **Rationale**: 로컬 우선, 쉬운 설정, 영구 저장 지원
  - **Alternatives Considered**: FAISS (rejected - 메타데이터 관리 불편), Pinecone (rejected - 클라우드 의존)

- **Embeddings**: OpenAI text-embedding-3-small
  - **Rationale**: 고품질, 비용 효율적
  - **Alternatives Considered**: Sentence-Transformers (rejected - GPU 필요)

- **LLM Router**: Claude Haiku
  - **Rationale**: 빠름 (~200ms), 저렴 ($0.25/1M 토큰)
  - **Alternatives Considered**: GPT-4o-mini (비슷한 성능)

- **Main LLM**: Claude Sonnet / GPT-4
  - **Rationale**: 고품질 응답
  - **Alternatives Considered**: 로컬 LLM (rejected - 품질 제약)

#### Supporting Technologies
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Async**: asyncio, aiohttp
- **Logging**: loguru
- **Configuration**: pydantic-settings
- **CLI**: typer (향후)

---

### Project Structure

```
ai-evolv-system/
├── .sdd/                           # SDD 문서
│   └── specs/
│       └── 001-hybrid-ai-system/
│           ├── spec.md
│           ├── plan.md
│           └── tasks.md
├── docs/                           # 사용자 문서
│   ├── README.md
│   ├── architecture.md
│   └── api-reference.md
├── src/
│   └── haes/                       # 핵심 라이브러리
│       ├── __init__.py
│       ├── config.py               # 설정 관리
│       ├── models/                 # 데이터 모델
│       │   ├── __init__.py
│       │   ├── skill.py
│       │   ├── agent.py
│       │   ├── routing.py
│       │   └── feedback.py
│       ├── stores/                 # 저장소
│       │   ├── __init__.py
│       │   ├── skill_store.py      # SKILL 저장 및 검색
│       │   ├── agent_pool.py       # Agent 풀 관리
│       │   └── feedback_store.py   # 피드백 저장
│       ├── router/                 # 라우팅 엔진
│       │   ├── __init__.py
│       │   ├── hybrid_router.py    # 하이브리드 라우터
│       │   ├── keyword_matcher.py  # 키워드 기반 매칭
│       │   └── llm_router.py       # LLM 기반 라우팅
│       ├── executor/               # 실행 엔진
│       │   ├── __init__.py
│       │   ├── hybrid_executor.py  # 4개 모드 실행
│       │   ├── skill_only.py       # SKILL_ONLY 실행기
│       │   ├── skill_agent.py      # SKILL_AGENT 실행기
│       │   ├── parallel.py         # PARALLEL 실행기
│       │   └── multi_agent.py      # MULTI_AGENT 실행기
│       ├── evolution/              # 진화 엔진
│       │   ├── __init__.py
│       │   └── evolution_engine.py # 피드백 학습
│       └── system.py               # HybridAISystem 메인 클래스
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # pytest 픽스처
│   ├── unit/
│   │   ├── test_skill_store.py
│   │   ├── test_agent_pool.py
│   │   ├── test_router.py
│   │   └── test_executor.py
│   ├── integration/
│   │   ├── test_system.py
│   │   └── test_evolution.py
│   └── fixtures/
│       ├── sample_skills/
│       └── sample_agents/
├── scripts/
│   ├── setup_vectordb.py           # Vector DB 초기화
│   └── validate_skills.py          # SKILL 검증
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

### Architecture Decisions

#### Decision 1: Hybrid Routing Strategy
**Context**: SKILL 선택을 위한 라우팅 방식 결정  
**Decision**: 키워드 매칭 우선 + LLM 폴백  
**Rationale**: 빠르고 예측 가능한 키워드 매칭으로 90% 처리, 애매한 경우만 LLM 사용  
**Consequences**: 키워드 매핑 유지 필요, 하지만 비용/속도 최적화  

#### Decision 2: Async-First Design
**Context**: 병렬 실행 모드 지원  
**Decision**: 전체 시스템 async/await 기반  
**Rationale**: PARALLEL 모드에서 asyncio.gather로 동시 실행  
**Consequences**: 모든 I/O 호출 비동기화 필요

#### Decision 3: Evolution as Separate Module
**Context**: 피드백 기반 학습 구현  
**Decision**: EvolutionEngine을 독립 모듈로 분리  
**Rationale**: 핵심 실행과 진화 로직 분리, 선택적 활성화 가능  
**Consequences**: 의존성 주입으로 연결

---

## Phase 1: Data Layer

### 1.1 SKILL Store 설계

```python
# src/haes/stores/skill_store.py

from dataclasses import dataclass
from typing import List, Optional
from chromadb import PersistentClient
from chromadb.utils import embedding_functions

@dataclass
class Skill:
    skill_id: str           # "03-fine-tuning"
    name: str               # "axolotl-fine-tuning"
    description: str        # YAML에서 추출
    tags: List[str]         # ["Post-Training", "LoRA"]
    content: str            # SKILL.md 전체
    path: str               # 파일 경로

class SkillStore:
    def __init__(self, skills_path: str, persist_dir: str = "./skill_vectordb"):
        self.skills_path = Path(skills_path)
        self.persist_dir = persist_dir
        self.cache: dict[str, str] = {}
        self._init_vectordb()
        
    def _init_vectordb(self):
        """Vector DB 초기화 또는 로드"""
        self.client = PersistentClient(path=self.persist_dir)
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            model_name="text-embedding-3-small"
        )
        self.collection = self.client.get_or_create_collection(
            name="skills",
            embedding_function=self.embedding_fn
        )
        
    def index_all_skills(self) -> int:
        """모든 SKILL 인덱싱 (초기화 시 1회)"""
        # SKILL.md 파일들 로드 → 벡터화 → 저장
        
    def search(self, query: str, k: int = 3) -> List[Skill]:
        """의미 기반 SKILL 검색"""
        
    def load(self, skill_ids: List[str]) -> str:
        """SKILL 내용 로드 (캐싱 적용)"""
        
    def get_compressed_index(self) -> str:
        """압축 인덱스 반환 (~2000 토큰)"""
```

### 1.2 Agent Pool 설계

```python
# src/haes/stores/agent_pool.py

@dataclass
class Agent:
    agent_id: str           # "backend-developer"
    tier: str               # "tier1-core"
    name: str               # YAML name
    description: str        # YAML description
    system_prompt: str      # 전체 내용
    
class AgentPool:
    def __init__(self, agents_dir: str = ".claude/agents"):
        self.agents_dir = Path(agents_dir)
        self.agents: dict[str, Agent] = {}
        self._load_all_agents()
        
    def _load_all_agents(self):
        """3-Tier 구조에서 모든 에이전트 로드"""
        for tier in ["tier1-core", "tier2-specialized", "tier3-experimental"]:
            self._load_from_tier(tier)
            
    def get(self, agent_id: str) -> Optional[Agent]:
        """에이전트 조회"""
        
    def list_by_tier(self, tier: str) -> List[Agent]:
        """Tier별 에이전트 목록"""
        
    def select_for_task(self, task_description: str) -> str:
        """작업에 적합한 에이전트 선택"""
```

### 1.3 압축 SKILL 인덱스

```python
# src/haes/stores/skill_store.py

SKILL_INDEX_TEMPLATE = """ID|키워드|설명
01-model-architecture|transformer,llama,mamba|모델 아키텍처
02-tokenization|tokenizer,bpe,sentencepiece|토크나이저
03-fine-tuning|axolotl,peft,lora,qlora|파인튜닝
05-data-processing|dedup,filtering,ray|데이터 처리
06-post-training|dpo,rlhf,grpo,ppo|포스트 트레이닝
07-safety-alignment|guardrails,redteaming|안전성
08-distributed-training|deepspeed,fsdp,ddp|분산 학습
10-optimization|quantization,pruning|최적화
11-evaluation|lm-eval,benchmark|평가
12-inference-serving|vllm,tgi,triton|추론 서빙
13-mlops|wandb,mlflow|MLOps
14-agents|crewai,langchain|에이전트
15-rag|chroma,faiss,retrieval|RAG
16-prompt-engineering|dspy,instructor|프롬프트
17-observability|logging,tracing|관측성
18-multimodal|clip,whisper,llava|멀티모달
19-emerging-techniques|moe,ssm|신기술
20-trading|ta-lib,vectorbt|트레이딩
"""
```

---

## Phase 2: Router Design

### 2.1 Hybrid Router

```python
# src/haes/router/hybrid_router.py

from enum import Enum
from dataclasses import dataclass

class ExecutionMode(Enum):
    SKILL_ONLY = "skill_only"      # 단순 지식 조회
    SKILL_AGENT = "skill_agent"    # SKILL + 단일 에이전트
    MULTI_AGENT = "multi_agent"    # 다중 에이전트 협업
    PARALLEL = "parallel"          # 병렬 실행

@dataclass
class RoutingDecision:
    mode: ExecutionMode
    skills: List[str]
    agents: List[str]
    reason: str
    confidence: float

class HybridRouter:
    def __init__(self, skill_store: SkillStore, llm_client):
        self.skill_store = skill_store
        self.llm = llm_client
        self.keyword_matcher = KeywordMatcher()
        
    async def route(self, query: str) -> RoutingDecision:
        # 1. 복잡도 분석
        complexity = self._analyze_complexity(query)
        
        # 2. 키워드 기반 빠른 매칭
        keyword_skills = self.keyword_matcher.match(query)
        
        # 3. 실행 모드 결정
        if complexity["score"] < 0.3:
            return self._decide_skill_only(keyword_skills, query)
        elif complexity["score"] < 0.6:
            return self._decide_skill_agent(keyword_skills, query)
        elif complexity["is_parallel"]:
            return self._decide_parallel(query)
        else:
            return self._decide_multi_agent(query)
```

### 2.2 Keyword Matcher

```python
KEYWORD_MAP = {
    "03-fine-tuning": ["파인튜닝", "fine-tuning", "lora", "qlora", "axolotl", "학습"],
    "12-inference-serving": ["추론", "서빙", "vllm", "배포", "inference", "serving"],
    "14-agents": ["에이전트", "agent", "langchain", "crewai"],
    "15-rag": ["rag", "검색", "retrieval", "벡터", "임베딩"],
    "08-distributed-training": ["분산", "학습", "deepspeed", "fsdp"],
    # ... 전체 SKILL 매핑
}
```

---

## Phase 3: Executor Design

### 3.1 Hybrid Executor

```python
# src/haes/executor/hybrid_executor.py

class HybridExecutor:
    def __init__(self, skill_store, agent_pool, llm_client):
        self.skill_store = skill_store
        self.agent_pool = agent_pool
        self.llm = llm_client
        
    async def execute(self, decision: RoutingDecision, query: str) -> ExecutionResult:
        if decision.mode == ExecutionMode.SKILL_ONLY:
            return await self._execute_skill_only(query, decision.skills)
        elif decision.mode == ExecutionMode.SKILL_AGENT:
            return await self._execute_skill_agent(query, decision.skills, decision.agents[0])
        elif decision.mode == ExecutionMode.PARALLEL:
            return await self._execute_parallel(query, decision.skills, decision.agents)
        else:
            return await self._execute_multi_agent(query, decision.skills, decision.agents)
```

### 3.2 Execution Modes

| Mode | LLM Calls | Expected Time | Cost |
|------|-----------|---------------|------|
| SKILL_ONLY | 1 (Sonnet) | ~2s | ~$0.01 |
| SKILL_AGENT | 1 (Sonnet + Agent Prompt) | ~10s | ~$0.05 |
| PARALLEL | N (동시) | ~15s | ~$0.15 |
| MULTI_AGENT | N (순차) | ~30s | ~$0.20 |

---

## Phase 4: Evolution Engine

### 4.1 Feedback Collection

```python
# src/haes/evolution/evolution_engine.py

class EvolutionEngine:
    def __init__(self, skill_store: SkillStore):
        self.skill_store = skill_store
        self.feedback_db: List[dict] = []
        self.routing_stats: dict = {}
        self.learned_patterns: List[dict] = []
        
    def record_feedback(self, result: ExecutionResult, feedback: str, score: int):
        """피드백 기록 및 학습 트리거"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "query": result.query,
            "mode": result.mode,
            "skills_used": result.skills_used,
            "feedback": feedback,
            "score": score
        }
        self.feedback_db.append(record)
        self._update_routing_stats(record)
        
        if score >= 4:
            self._learn_success_pattern(record)
        elif score <= 2:
            self._trigger_improvement(record)
```

### 4.2 Quality Gates

```python
def should_update_skill(pattern: dict) -> bool:
    return (
        pattern["success_rate"] > 0.8 and   # 80% 이상 성공
        pattern["sample_size"] >= 5 and      # 최소 5회 검증
        not is_duplicate(pattern)             # 중복 아님
    )
```

---

## Phase 5: Main System

### 5.1 HybridAISystem

```python
# src/haes/system.py

class HybridAISystem:
    def __init__(self, config: Config):
        self.skill_store = SkillStore(config.skills_path)
        self.agent_pool = AgentPool(config.agents_path)
        self.router = HybridRouter(self.skill_store, config.routing_llm)
        self.executor = HybridExecutor(self.skill_store, self.agent_pool, config.main_llm)
        self.evolution = EvolutionEngine(self.skill_store)
        self.history: List[dict] = []
        
    async def chat(self, query: str) -> ExecutionResult:
        # 1. 진화 엔진에서 힌트 확인
        hints = self.evolution.get_routing_hints(query)
        
        # 2. 라우팅 결정
        if hints["confidence"] > 0.85:
            decision = self._use_learned_pattern(hints)
        else:
            decision = await self.router.route(query)
            
        # 3. 실행
        result = await self.executor.execute(decision, query)
        
        # 4. 히스토리 업데이트
        self._update_history(query, result)
        
        return result
        
    def feedback(self, feedback_text: str, score: int):
        """사용자 피드백 수집"""
        if self.last_result:
            self.evolution.record_feedback(self.last_result, feedback_text, score)
```

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| 라우팅 부정확 | Medium | High | 다단계 검증 (키워드 + LLM) |
| Vector DB 초기화 시간 | Low | Medium | 영구 저장 + 캐싱 |
| LLM API 비용 초과 | Medium | Low | Haiku 라우팅, 사용량 모니터링 |
| SKILL 증가로 검색 느려짐 | Low | Low | 압축 인덱스 사용 |

---

## Performance Considerations

### Expected Load
- **Concurrent Users**: 1-10 (로컬 사용)
- **Requests Per Minute**: ~20
- **SKILL Count**: 63개 (확장 가능)

### Optimization Strategy
1. Vector DB 영구 저장 (재시작 시 재인덱싱 불필요)
2. SKILL 컨텐츠 캐싱 (메모리)
3. Async I/O로 병렬 처리

### Performance Targets
- **Routing Latency (p95)**: < 500ms
- **SKILL_ONLY Response (p95)**: < 3s
- **Vector Search (p95)**: < 200ms

---

## Validation Checklist

Before implementation:

- [x] All Constitutional Gates passed (Phase -1)
- [x] Technology stack approved
- [x] Data model designed
- [x] Architecture decisions documented
- [ ] Contract tests written (tasks.md에서)
- [x] Implementation sequence clear
- [x] No complexity violations
- [x] TDD commitment confirmed

---

## Notes & References

- **Specification**: `spec.md`
- **Tasks**: `tasks.md`
- **SKILL Source**: `/home/cafe99/anti-gravity-project/AI-research-SKILLs/`
- **Agent Source**: `/home/cafe99/anti-gravity-project/.claude/agents/`
