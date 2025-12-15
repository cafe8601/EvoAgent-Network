"""
HAES Observability API - 모니터링 API 엔드포인트

Agent/Skill 모니터링 대시보드를 위한 REST API
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

from loguru import logger

from haes import HybridAISystem, Config
from haes.llm import OpenAIClient
from haes.observability.tracer import HAESTracer, get_tracer, SpanKind
from haes.observability.metrics import MetricsCollector, get_metrics
from haes.observability.monitor import SystemMonitor, EventType, get_monitor


# ===============================
# Pydantic Models
# ===============================

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    response: str
    mode: str
    skills_used: List[str] = []
    agents_used: List[str] = []
    execution_time: float
    cost_estimate: str = ""
    trace_id: str = ""

class FeedbackRequest(BaseModel):
    score: int = Field(..., ge=1, le=5)
    comment: str = ""

class DashboardOverview(BaseModel):
    """대시보드 개요"""
    status: str
    total_requests: int
    hourly_requests: int
    avg_duration_ms: float
    avg_feedback_score: float
    error_rate_pct: float

class TraceInfo(BaseModel):
    """트레이스 정보"""
    trace_id: str
    name: str
    duration_ms: float
    status: str
    spans_count: int
    timestamp: float


# ===============================
# Global State
# ===============================

system: Optional[HybridAISystem] = None
llm_client: Optional[OpenAIClient] = None
tracer: Optional[HAESTracer] = None
metrics: Optional[MetricsCollector] = None
monitor: Optional[SystemMonitor] = None


# ===============================
# Lifespan
# ===============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global system, llm_client, tracer, metrics, monitor
    
    print("🚀 HAES Observability Server 시작...")
    
    # Observability 컴포넌트 초기화
    tracer = get_tracer()
    metrics = get_metrics()
    monitor = get_monitor()
    
    # OpenAI 클라이언트
    try:
        llm_client = OpenAIClient(
            routing_model=os.getenv("ROUTING_MODEL", "gpt-4o-mini"),
            main_model=os.getenv("MAIN_MODEL", "gpt-4o"),
        )
        print(f"✅ OpenAI 연결됨")
    except Exception as e:
        print(f"⚠️ OpenAI 연결 실패: {e}")
        llm_client = None
    
    # 시스템 설정
    project_root = Path("/home/cafe99/anti-gravity-project")
    skills_path = project_root / "AI-research-SKILLs"
    agents_path = project_root / ".claude" / "agents"
    
    if not skills_path.exists():
        skills_path = Path(__file__).parent / "tests" / "fixtures" / "sample_skills"
        agents_path = Path(__file__).parent / "tests" / "fixtures" / "sample_agents"
    
    config = Config(
        skills_path=skills_path,
        agents_path=agents_path,
        persist_dir=Path(__file__).parent / "obs_vectordb",
    )
    
    # 시스템 초기화
    system = HybridAISystem(config=config, llm_client=llm_client)
    stats = system.initialize()
    
    monitor.emit_info("시스템 시작됨", {
        "skills": stats["skills_indexed"],
        "agents": stats["agents_loaded"],
    })
    
    print(f"✅ 초기화 완료: {stats['skills_indexed']}개 SKILL, {stats['agents_loaded']}개 에이전트")
    print(f"📊 대시보드: http://localhost:8080/dashboard")
    
    yield
    
    monitor.emit_info("시스템 종료됨")
    print("👋 HAES Observability Server 종료...")


# ===============================
# FastAPI App
# ===============================

app = FastAPI(
    title="HAES Observability API",
    description="Agent/Skill 모니터링 시스템",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===============================
# Dashboard UI
# ===============================

@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 - 대시보드로 리다이렉트"""
    return """
    <html>
        <head><meta http-equiv="refresh" content="0; url=/dashboard"></head>
        <body><a href="/dashboard">Go to Dashboard</a></body>
    </html>
    """

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """모니터링 대시보드"""
    dashboard_path = Path(__file__).parent / "static" / "observability_dashboard.html"
    if dashboard_path.exists():
        return FileResponse(str(dashboard_path), media_type="text/html")
    return HTMLResponse(get_embedded_dashboard())


# ===============================
# Chat Endpoints (with tracing)
# ===============================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """채팅 (트레이싱 포함)"""
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    with tracer.trace("chat_request", {"query": request.query[:100]}) as t:
        monitor.emit_chat_start(request.query, t.trace_id)
        
        try:
            with tracer.span("execute_chat", SpanKind.CHAT, {"query": request.query}):
                result = await system.chat(request.query)
            
            # 메트릭 기록
            metrics.record_request(
                mode=result.mode,
                duration_ms=result.execution_time * 1000,
                skills=result.skills_used,
                agents=result.agents_used,
                success=True,
            )
            
            return ChatResponse(
                response=result.response,
                mode=result.mode,
                skills_used=result.skills_used,
                agents_used=result.agents_used,
                execution_time=result.execution_time,
                cost_estimate=result.cost_estimate or "",
                trace_id=t.trace_id,
            )
        except Exception as e:
            monitor.emit_error("채팅 처리 실패", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback")
async def feedback(request: FeedbackRequest):
    """피드백 제출"""
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        fb = system.feedback(score=request.score, comment=request.comment)
        monitor.emit_feedback(request.score, fb.mode, fb.query)
        return {"success": True, "message": f"피드백 저장: {request.score}점"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===============================
# Observability Endpoints
# ===============================

@app.get("/api/status")
async def get_status():
    """시스템 상태"""
    return monitor.get_status()


@app.get("/api/stats")
async def get_stats():
    """시스템 전체 통계 (시스템 + 메모리 + RAG)"""
    stats = {}
    
    # 시스템 통계
    if system:
        sys_stats = system.get_stats()
        stats.update({
            "skills_indexed": sys_stats.get("skill_store", {}).get("total_skills", 0),
            "agents_loaded": sys_stats.get("agent_pool", {}).get("total_agents", 0),
            "feedbacks_count": sys_stats.get("feedback", {}).get("total", 0),
            "history_length": sys_stats.get("history_length", 0),
        })
        
        # 메모리 통계
        memory_stats = sys_stats.get("memory", {})
        stats.update({
            "session_memory": memory_stats.get("session", 0),
            "short_term_memory": memory_stats.get("short_term", 0),
            "long_term_memory": memory_stats.get("long_term", 0),
        })
    
    # RAG 통계
    try:
        rag = get_hybrid_rag()
        if rag:
            rag_stats = rag.get_stats()
            stats["rag_documents"] = rag_stats.get("personal", {}).get("document_count", 0)
            stats["rag_enabled"] = rag_stats.get("personal_enabled", False)
    except:
        stats["rag_enabled"] = False
    
    return stats


@app.get("/api/dashboard")
async def get_dashboard_data():
    """대시보드 데이터"""
    return monitor.get_live_dashboard()


@app.get("/api/traces")
async def get_traces(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """트레이스 목록"""
    traces = tracer.get_traces(limit, offset)
    return {
        "count": len(traces),
        "traces": [t.to_dict() for t in traces],
    }


@app.get("/api/traces/{trace_id}")
async def get_trace(trace_id: str):
    """트레이스 상세"""
    trace = tracer.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace.to_dict()


@app.get("/api/spans")
async def get_spans(
    kind: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
):
    """스팬 목록"""
    span_kind = None
    if kind:
        try:
            span_kind = SpanKind(kind)
        except ValueError:
            pass
    
    spans = tracer.get_recent_spans(span_kind, limit)
    return {
        "count": len(spans),
        "spans": [s.to_dict() for s in spans],
    }


@app.get("/api/events")
async def get_events(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
):
    """이벤트 목록"""
    evt_type = None
    if event_type:
        try:
            evt_type = EventType(event_type)
        except ValueError:
            pass
    
    events = monitor.get_events(evt_type, severity, limit)
    return {
        "count": len(events),
        "events": [e.to_dict() for e in events],
    }


@app.get("/api/events/stream")
async def stream_events():
    """SSE 이벤트 스트림"""
    async def event_generator():
        async for event_str in monitor.stream_events():
            yield event_str
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/metrics")
async def get_metrics_data():
    """메트릭 데이터"""
    return metrics.get_dashboard_data()


@app.get("/api/skills/stats")
async def get_skill_stats():
    """스킬별 통계"""
    return monitor.get_skill_stats()


@app.get("/api/agents/stats")
async def get_agent_stats():
    """에이전트별 통계"""
    return monitor.get_agent_stats()


@app.get("/api/skills")
async def get_skills():
    """SKILL 목록"""
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    skills = system.skill_store.list_all()
    return {
        "count": len(skills),
        "skills": [
            {"id": s.skill_id, "name": s.name, "description": s.description}
            for s in skills
        ],
    }


# ===============================
# RAG API Endpoints
# ===============================

# RAG 시스템 상태
_rag_initialized = False
_hybrid_rag = None


def get_rag():
    """RAG 시스템 초기화 및 반환"""
    global _rag_initialized, _hybrid_rag
    
    if not _rag_initialized:
        try:
            from haes.rag import HybridRAG
            
            _hybrid_rag = HybridRAG(
                personal_persist_dir=str(Path(__file__).parent / "personal_rag_db"),
                google_api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
                enable_personal=True,
                enable_shared=bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")),
            )
            _rag_initialized = True
        except Exception as e:
            logger.warning(f"RAG initialization failed: {e}")
            _rag_initialized = True  # 재시도 방지
    
    return _hybrid_rag


# Pydantic Models for RAG
class RAGDocumentRequest(BaseModel):
    content: str = Field(..., min_length=1)
    metadata: Optional[dict] = None
    doc_id: Optional[str] = None


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(5, ge=1, le=50)
    rag_type: str = "hybrid"  # "personal", "shared", "hybrid"
    filter: Optional[dict] = None


@app.get("/api/rag/status")
async def rag_status():
    """RAG 시스템 상태"""
    rag = get_rag()
    if not rag:
        return {
            "status": "unavailable",
            "message": "RAG system not initialized",
            "personal_enabled": False,
            "shared_enabled": False,
        }
    
    return {
        "status": "available",
        **rag.get_stats(),
    }


@app.post("/api/rag/personal/add")
async def rag_add_personal_document(request: RAGDocumentRequest):
    """개인용 RAG에 문서 추가"""
    rag = get_rag()
    if not rag or not rag.personal:
        raise HTTPException(status_code=503, detail="Personal RAG not available")
    
    doc_id = rag.add_personal_document(
        content=request.content,
        metadata=request.metadata,
        doc_id=request.doc_id,
    )
    
    if doc_id:
        return {"success": True, "doc_id": doc_id}
    raise HTTPException(status_code=500, detail="Failed to add document")


@app.get("/api/rag/personal/documents")
async def rag_list_personal_documents(
    limit: int = Query(50, ge=1, le=200),
):
    """개인 문서 목록"""
    rag = get_rag()
    if not rag or not rag.personal:
        raise HTTPException(status_code=503, detail="Personal RAG not available")
    
    docs = rag.list_personal_documents(limit=limit)
    return {
        "count": len(docs),
        "documents": docs,
    }


@app.delete("/api/rag/personal/documents/{doc_id}")
async def rag_delete_personal_document(doc_id: str):
    """개인 문서 삭제"""
    rag = get_rag()
    if not rag or not rag.personal:
        raise HTTPException(status_code=503, detail="Personal RAG not available")
    
    if rag.delete_personal_document(doc_id):
        return {"success": True, "deleted": doc_id}
    raise HTTPException(status_code=404, detail="Document not found")


@app.post("/api/rag/search")
async def rag_search(request: RAGSearchRequest):
    """RAG 검색 (하이브리드)"""
    rag = get_rag()
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    from haes.rag import RAGType
    
    rag_type_map = {
        "personal": RAGType.PERSONAL,
        "shared": RAGType.SHARED,
        "hybrid": RAGType.HYBRID,
    }
    
    rag_type = rag_type_map.get(request.rag_type, RAGType.HYBRID)
    
    results = rag.search(
        query=request.query,
        k=request.k,
        rag_type=rag_type,
        personal_filter=request.filter,
    )
    
    return {
        "query": request.query,
        "count": len(results),
        "results": [
            {
                "content": r.content,
                "score": r.score,
                "source": r.source,
                "metadata": r.metadata,
                "doc_id": r.doc_id,
                "file_name": r.file_name,
            }
            for r in results
        ],
    }


@app.get("/api/rag/context")
async def rag_get_context(
    query: str,
    k: int = Query(5, ge=1, le=20),
    max_tokens: int = Query(4000, ge=500, le=16000),
    rag_type: str = "hybrid",
):
    """LLM 컨텍스트용 RAG 검색"""
    rag = get_rag()
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    from haes.rag import RAGType
    
    rag_type_map = {
        "personal": RAGType.PERSONAL,
        "shared": RAGType.SHARED,
        "hybrid": RAGType.HYBRID,
    }
    
    context = rag.get_context(
        query=query,
        k=k,
        rag_type=rag_type_map.get(rag_type, RAGType.HYBRID),
        max_tokens=max_tokens,
    )
    
    return {
        "query": query,
        "context": context,
        "context_length": len(context),
    }


@app.post("/api/rag/index-skills")
async def rag_index_skills():
    """AI-research-SKILLs 인덱싱"""
    rag = get_rag()
    if not rag or not rag.personal:
        raise HTTPException(status_code=503, detail="Personal RAG not available")
    
    from haes.rag.document_processor import DocumentProcessor
    
    skills_path = Path("/home/cafe99/anti-gravity-project/AI-research-SKILLs")
    if not skills_path.exists():
        raise HTTPException(status_code=404, detail="Skills directory not found")
    
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    docs = processor.process_skill_directory(str(skills_path))
    
    total_chunks = 0
    for doc in docs:
        for chunk in doc.chunks:
            rag.add_personal_document(
                content=chunk.content,
                metadata=chunk.metadata,
            )
            total_chunks += 1
    
    return {
        "success": True,
        "documents_processed": len(docs),
        "chunks_indexed": total_chunks,
    }


# ===============================
# Planner API Endpoints
# ===============================

# Planner 인스턴스
_planner = None


def get_planner_instance():
    """플래너 인스턴스 반환"""
    global _planner
    
    if _planner is None:
        try:
            from haes.planner import SpecDrivenPlanner
            
            _planner = SpecDrivenPlanner(
                skill_store=system.skill_store if system else None,
                agent_pool=system.agent_pool if system else None,
                llm_client=llm_client,
            )
            logger.info("SpecDrivenPlanner initialized")
        except Exception as e:
            logger.error(f"Planner initialization failed: {e}")
    
    return _planner


class PlanRequest(BaseModel):
    query: str = Field(..., min_length=1)
    force_complexity: Optional[float] = None  # 복잡도 강제 지정 (테스트용)


@app.post("/api/planner/analyze")
async def analyze_query(request: PlanRequest):
    """
    쿼리 분석 및 실행 계획 생성
    
    복잡도에 따라:
    - 0~0.2: simple_query (즉시 응답)
    - 0.2~0.35: skill_lookup (스킬 조회)
    - 0.35~0.5: single_task (단일 작업)
    - 0.5~0.7: sequential/parallel (다중 작업)
    - 0.7~1.0: spec_driven (전체 계획 수립)
    """
    planner = get_planner_instance()
    if not planner:
        raise HTTPException(status_code=503, detail="Planner not available")
    
    # 라우터로 복잡도 분석
    if system and request.force_complexity is None:
        decision = await system.router.route(request.query)
        complexity = decision.complexity.score if decision.complexity else 0.5
        is_parallel = decision.complexity.is_parallel if decision.complexity else False
        is_collaborative = decision.complexity.is_collaborative if decision.complexity else False
        matched_skills = decision.skills
    else:
        complexity = request.force_complexity or 0.5
        is_parallel = "하고" in request.query or "그리고" in request.query
        is_collaborative = "검토" in request.query or "확인" in request.query
        matched_skills = []
    
    # 계획 생성
    plan = await planner.create_plan(
        query=request.query,
        complexity_score=complexity,
        matched_skills=matched_skills,
        is_parallel=is_parallel,
        is_collaborative=is_collaborative,
    )
    
    return {
        "plan_id": plan.id,
        "query": plan.query,
        "complexity_score": plan.complexity_score,
        "workflow": plan.workflow.value,
        "phases_count": len(plan.phases),
        "total_tasks": plan.total_tasks,
        "estimated_time_minutes": plan.estimated_time_minutes,
        "selected_agents": plan.selected_agents,
        "selected_skills": plan.selected_skills,
        "phases": [p.to_dict() for p in plan.phases],
    }


@app.get("/api/planner/workflows")
async def get_workflows():
    """사용 가능한 워크플로우 목록"""
    from haes.planner import WorkflowType
    
    workflows = [
        {
            "type": "simple_query",
            "name": "단순 질문",
            "description": "즉시 응답하는 간단한 질문",
            "complexity_range": "0.0 ~ 0.2",
            "agents_required": 0,
        },
        {
            "type": "skill_lookup",
            "name": "스킬 조회",
            "description": "SKILL 문서 기반 응답",
            "complexity_range": "0.2 ~ 0.35",
            "agents_required": 0,
        },
        {
            "type": "single_task",
            "name": "단일 작업",
            "description": "한 에이전트가 처리하는 단일 작업",
            "complexity_range": "0.35 ~ 0.5",
            "agents_required": 1,
        },
        {
            "type": "sequential",
            "name": "순차 실행",
            "description": "여러 에이전트가 순서대로 협업",
            "complexity_range": "0.5 ~ 0.7",
            "agents_required": "2+",
        },
        {
            "type": "parallel",
            "name": "병렬 실행",
            "description": "독립 작업을 동시에 실행",
            "complexity_range": "0.5 ~ 0.7",
            "agents_required": "2+",
        },
        {
            "type": "spec_driven",
            "name": "스펙 기반 계획",
            "description": "전체 계획 수립 후 단계별 실행",
            "complexity_range": "0.7 ~ 1.0",
            "agents_required": "3+",
        },
    ]
    
    return {"workflows": workflows}


@app.get("/api/planner/plan/{plan_id}")
async def get_plan(plan_id: str):
    """계획 상세 조회"""
    planner = get_planner_instance()
    if not planner:
        raise HTTPException(status_code=503, detail="Planner not available")
    
    plan = planner.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return plan.to_dict()


@app.get("/api/planner/plan/{plan_id}/summary")
async def get_plan_summary(plan_id: str):
    """계획 요약 (마크다운)"""
    planner = get_planner_instance()
    if not planner:
        raise HTTPException(status_code=503, detail="Planner not available")
    
    plan = planner.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return {
        "plan_id": plan_id,
        "summary": planner.get_execution_summary(plan),
    }


@app.get("/api/planner/plan/{plan_id}/next-tasks")
async def get_next_tasks(plan_id: str):
    """다음 실행 가능한 태스크 목록"""
    planner = get_planner_instance()
    if not planner:
        raise HTTPException(status_code=503, detail="Planner not available")
    
    plan = planner.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    next_tasks = plan.get_next_tasks()
    
    return {
        "plan_id": plan_id,
        "progress": plan.progress,
        "next_tasks": [t.to_dict() for t in next_tasks[:5]],
    }


# ===============================
# Training API Endpoints
# ===============================

# 훈련 관련 글로벌 변수
_trainer = None
_training_task = None


def get_trainer_instance():
    """훈련기 인스턴스 반환"""
    global _trainer
    
    if _trainer is None:
        try:
            from haes.training import SandboxTrainer
            _trainer = SandboxTrainer(
                haes_api_url="http://localhost:8080",
                llm_client=llm_client,
            )
            logger.info("SandboxTrainer initialized")
        except Exception as e:
            logger.error(f"Trainer initialization failed: {e}")
    
    return _trainer


@app.get("/api/training/stats")
async def get_training_stats():
    """훈련 통계 조회"""
    trainer = get_trainer_instance()
    if not trainer:
        return {"error": "Trainer not available", "stats": {}}
    
    stats = trainer.get_training_stats()
    
    # Evolution Engine 통계도 포함
    if system:
        evolution_stats = system.evolution.get_stats()
        stats["evolution"] = evolution_stats
    
    return stats


@app.post("/api/training/generate-examples")
async def generate_training_examples(count: int = Query(20, ge=1, le=100)):
    """훈련 예제 생성 (미리보기)"""
    try:
        from haes.training import SyntheticDataGenerator
        
        generator = SyntheticDataGenerator()
        examples = generator.generate_examples(count)
        
        return {
            "count": len(examples),
            "examples": [
                {
                    "id": ex.id,
                    "query": ex.query,
                    "expected_skills": ex.expected_skills,
                    "expected_mode": ex.expected_mode,
                    "difficulty": ex.difficulty,
                    "category": ex.category,
                }
                for ex in examples
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TrainingRequest(BaseModel):
    num_examples: int = Field(20, ge=5, le=200)
    difficulty: Optional[str] = None  # easy, medium, hard
    category: Optional[str] = None


@app.post("/api/training/start")
async def start_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """
    백그라운드 훈련 시작
    
    훈련 과정:
    1. 합성 데이터 생성
    2. HAES API로 각 쿼리 실행
    3. 응답 자동 평가
    4. Evolution Engine에 피드백 전달
    5. 패턴 학습
    """
    global _training_task
    
    trainer = get_trainer_instance()
    if not trainer:
        raise HTTPException(status_code=503, detail="Trainer not available")
    
    # 이미 훈련 중인지 확인
    if _training_task and not _training_task.done():
        return {
            "status": "already_running",
            "message": "Training is already in progress",
        }
    
    async def run_training():
        try:
            session = await trainer.train(
                num_examples=request.num_examples,
                difficulty=request.difficulty,
                category=request.category,
            )
            logger.info(f"Training completed: {session.id}")
        except Exception as e:
            logger.error(f"Training failed: {e}")
    
    # 백그라운드 태스크로 실행
    _training_task = asyncio.create_task(run_training())
    
    return {
        "status": "started",
        "num_examples": request.num_examples,
        "difficulty": request.difficulty,
        "category": request.category,
        "message": f"Training started with {request.num_examples} examples",
    }


@app.get("/api/training/status")
async def get_training_status():
    """현재 훈련 상태"""
    global _training_task
    
    trainer = get_trainer_instance()
    if not trainer:
        return {"status": "not_available"}
    
    if _training_task is None:
        return {"status": "idle", "message": "No training in progress"}
    
    if _training_task.done():
        try:
            _training_task.result()
            return {"status": "completed", "message": "Training completed"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    # 진행 중인 세션 정보
    if trainer._session:
        session = trainer._session
        return {
            "status": "running",
            "session_id": session.id,
            "progress": f"{session.evaluated}/{session.total_examples}",
            "success_count": session.success_count,
            "average_score": session.average_score,
        }
    
    return {"status": "running", "message": "Training in progress"}


@app.get("/api/evolution/stats")
async def get_evolution_stats():
    """Evolution Engine 통계"""
    if not system:
        return {"error": "System not initialized"}
    
    return system.evolution.get_stats()


@app.get("/api/evolution/patterns")
async def get_learned_patterns():
    """학습된 패턴 목록"""
    if not system:
        return {"patterns": []}
    
    patterns = system.evolution.export_patterns()
    return {
        "count": len(patterns),
        "patterns": patterns,
    }


@app.get("/api/evolution/skill-performance/{skill_id}")
async def get_skill_performance(skill_id: str):
    """SKILL별 성능 통계"""
    if not system:
        return {"error": "System not initialized"}
    
    return system.evolution.get_skill_performance(skill_id)


@app.get("/api/evolution/top-skills")
async def get_top_performing_skills(n: int = Query(10, ge=1, le=50)):
    """상위 성능 SKILL 목록"""
    if not system:
        return {"skills": []}
    
    return {
        "skills": system.evolution.get_top_performing_skills(n)
    }


# ===============================
# Security API Endpoints
# ===============================

# 보안 관련 글로벌 변수
_security_guard = None


def get_security_instance():
    """보안 가드 인스턴스 반환"""
    global _security_guard
    
    if _security_guard is None:
        try:
            from haes.security import SecurityGuard
            _security_guard = SecurityGuard()
            logger.info("SecurityGuard initialized")
        except Exception as e:
            logger.error(f"SecurityGuard initialization failed: {e}")
    
    return _security_guard


@app.get("/api/security/stats")
async def get_security_stats():
    """보안 통계"""
    guard = get_security_instance()
    if not guard:
        return {"error": "Security system not available"}
    
    return guard.get_stats()


@app.get("/api/security/events")
async def get_security_events(limit: int = Query(50, ge=1, le=500)):
    """최근 보안 이벤트"""
    guard = get_security_instance()
    if not guard:
        return {"events": []}
    
    return {
        "count": limit,
        "events": guard.get_recent_events(limit),
    }


class SecurityValidationRequest(BaseModel):
    query: str
    source_ip: Optional[str] = None
    user_id: Optional[str] = None


@app.post("/api/security/validate")
async def validate_input(request: SecurityValidationRequest):
    """입력 보안 검증"""
    guard = get_security_instance()
    if not guard:
        return {"error": "Security system not available"}
    
    result = guard.validate_input(
        query=request.query,
        source_ip=request.source_ip,
        user_id=request.user_id,
    )
    
    return {
        "is_safe": result.is_safe,
        "threat_level": result.threat_level.value,
        "threats_detected": [t.value for t in result.threats_detected],
        "blocked": result.blocked,
        "sanitized_input": result.sanitized_input,
        "details": result.details,
    }


@app.post("/api/security/validate-output")
async def validate_output_endpoint(response: str = Query(...)):
    """출력 보안 검증 (PII 마스킹)"""
    guard = get_security_instance()
    if not guard:
        return {"error": "Security system not available"}
    
    result = guard.validate_output(response)
    
    return {
        "is_safe": result.is_safe,
        "pii_detected": result.details.get("pii", {}),
        "sanitized_output": result.sanitized_input,
    }


@app.get("/api/security/status")
async def get_security_status():
    """보안 시스템 상태"""
    guard = get_security_instance()
    
    if not guard:
        return {
            "status": "unavailable",
            "message": "Security system not initialized",
        }
    
    stats = guard.get_stats()
    
    return {
        "status": "active",
        "features": {
            "prompt_injection_detection": True,
            "jailbreak_detection": True,
            "pii_masking": True,
            "sql_injection_detection": True,
            "toxic_content_filter": True,
            "rate_limiting": True,
            "audit_logging": True,
        },
        "stats": stats,
    }


# ===============================
# Embedded Dashboard HTML
# ===============================


def get_embedded_dashboard() -> str:
    """임베디드 대시보드 HTML"""
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAES Observability Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: #1a1a24;
            --border-color: rgba(255,255,255,0.1);
            --text-primary: #ffffff;
            --text-secondary: #8b8b9a;
            --accent-primary: #6366f1;
            --accent-success: #10b981;
            --accent-warning: #f59e0b;
            --accent-error: #ef4444;
            --gradient-1: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        }
        
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        .app {
            display: flex;
            min-height: 100vh;
        }
        
        /* Sidebar */
        .sidebar {
            width: 260px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            padding: 24px;
            display: flex;
            flex-direction: column;
        }
        
        .logo {
            font-size: 24px;
            font-weight: 700;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 32px;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border-radius: 8px;
            cursor: pointer;
            color: var(--text-secondary);
            transition: all 0.2s;
            margin-bottom: 4px;
        }
        
        .nav-item:hover, .nav-item.active {
            background: var(--bg-card);
            color: var(--text-primary);
        }
        
        .nav-item.active {
            border-left: 3px solid var(--accent-primary);
        }
        
        /* Main Content */
        .main {
            flex: 1;
            padding: 24px 32px;
            overflow-y: auto;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 32px;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 600;
        }
        
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .status-healthy { background: rgba(16,185,129,0.2); color: var(--accent-success); }
        .status-degraded { background: rgba(245,158,11,0.2); color: var(--accent-warning); }
        .status-critical { background: rgba(239,68,68,0.2); color: var(--accent-error); }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 32px;
        }
        
        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
        }
        
        .stat-card .label {
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .stat-card .value {
            font-size: 32px;
            font-weight: 700;
        }
        
        .stat-card .trend {
            font-size: 13px;
            margin-top: 8px;
        }
        
        .trend.up { color: var(--accent-success); }
        .trend.down { color: var(--accent-error); }
        
        /* Charts Section */
        .charts-section {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
            margin-bottom: 32px;
        }
        
        .chart-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
        }
        
        .chart-card h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        
        /* Traces Table */
        .traces-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 32px;
        }
        
        .traces-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .traces-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .traces-table th {
            text-align: left;
            padding: 12px;
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 13px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .traces-table td {
            padding: 14px 12px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .trace-status {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .trace-status.success { background: var(--accent-success); }
        .trace-status.error { background: var(--accent-error); }
        .trace-status.pending { background: var(--accent-warning); }
        
        /* Events Panel */
        .events-panel {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
        }
        
        .event-item {
            display: flex;
            gap: 12px;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .event-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }
        
        .event-icon.info { background: rgba(99,102,241,0.2); }
        .event-icon.warning { background: rgba(245,158,11,0.2); }
        .event-icon.error { background: rgba(239,68,68,0.2); }
        
        .event-content flex: 1; }
        .event-type { font-weight: 500; font-size: 14px; }
        .event-time { color: var(--text-secondary); font-size: 12px; }
        
        /* Chat Test */
        .chat-section {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 32px;
        }
        
        .chat-input-group {
            display: flex;
            gap: 12px;
        }
        
        .chat-input {
            flex: 1;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px 16px;
            color: var(--text-primary);
            font-size: 15px;
        }
        
        .chat-input:focus {
            outline: none;
            border-color: var(--accent-primary);
        }
        
        .chat-btn {
            background: var(--gradient-1);
            border: none;
            border-radius: 8px;
            padding: 14px 24px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
        }
        
        .chat-btn:hover { transform: translateY(-1px); }
        .chat-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        
        .chat-result {
            margin-top: 20px;
            padding: 16px;
            background: var(--bg-secondary);
            border-radius: 8px;
            white-space: pre-wrap;
        }
        
        /* Span Breakdown */
        .breakdown-list {
            list-style: none;
        }
        
        .breakdown-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .breakdown-label {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .breakdown-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }
        
        .dot-chat { background: #6366f1; }
        .dot-routing { background: #8b5cf6; }
        .dot-skill { background: #10b981; }
        .dot-agent { background: #f59e0b; }
        .dot-llm { background: #ef4444; }
        
        @media (max-width: 1200px) {
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .charts-section { grid-template-columns: 1fr; }
        }
        
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .stats-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="app">
        <aside class="sidebar">
            <div class="logo">🔬 HAES</div>
            <nav>
                <div class="nav-item active" onclick="showPanel('dashboard')">
                    <span>📊</span> Dashboard
                </div>
                <div class="nav-item" onclick="showPanel('traces')">
                    <span>🔍</span> Traces
                </div>
                <div class="nav-item" onclick="showPanel('skills')">
                    <span>⚡</span> Skills
                </div>
                <div class="nav-item" onclick="showPanel('agents')">
                    <span>🤖</span> Agents
                </div>
                <div class="nav-item" onclick="showPanel('events')">
                    <span>📝</span> Events
                </div>
            </nav>
        </aside>
        
        <main class="main">
            <div class="header">
                <h1>Agent/Skill Observability</h1>
                <span class="status-badge status-healthy" id="systemStatus">● Healthy</span>
            </div>
            
            <!-- Stats Grid -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="label">Total Requests</div>
                    <div class="value" id="totalRequests">0</div>
                </div>
                <div class="stat-card">
                    <div class="label">Avg Response Time</div>
                    <div class="value" id="avgDuration">0<span style="font-size:16px">ms</span></div>
                </div>
                <div class="stat-card">
                    <div class="label">Avg Feedback Score</div>
                    <div class="value" id="avgFeedback">0<span style="font-size:16px">/5</span></div>
                </div>
                <div class="stat-card">
                    <div class="label">Error Rate</div>
                    <div class="value" id="errorRate">0<span style="font-size:16px">%</span></div>
                </div>
            </div>
            
            <!-- Chat Test Section -->
            <div class="chat-section">
                <h3 style="margin-bottom:16px">🧪 Test Query</h3>
                <div class="chat-input-group">
                    <input type="text" class="chat-input" id="chatInput" 
                           placeholder="Enter a query to test... (e.g., LoRA 파인튜닝 방법)"
                           onkeypress="if(event.key==='Enter') sendChat()">
                    <button class="chat-btn" onclick="sendChat()" id="chatBtn">Send</button>
                </div>
                <div class="chat-result" id="chatResult" style="display:none"></div>
            </div>
            
            <!-- Charts Section -->
            <div class="charts-section">
                <div class="chart-card">
                    <h3>Recent Traces</h3>
                    <table class="traces-table">
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>Trace ID</th>
                                <th>Name</th>
                                <th>Duration</th>
                                <th>Spans</th>
                            </tr>
                        </thead>
                        <tbody id="tracesBody">
                            <tr><td colspan="5" style="color:var(--text-secondary)">No traces yet</td></tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="chart-card">
                    <h3>Span Breakdown</h3>
                    <ul class="breakdown-list" id="spanBreakdown">
                        <li class="breakdown-item">
                            <span class="breakdown-label">
                                <span class="breakdown-dot dot-chat"></span> Chat
                            </span>
                            <span>0</span>
                        </li>
                        <li class="breakdown-item">
                            <span class="breakdown-label">
                                <span class="breakdown-dot dot-routing"></span> Routing
                            </span>
                            <span>0</span>
                        </li>
                        <li class="breakdown-item">
                            <span class="breakdown-label">
                                <span class="breakdown-dot dot-skill"></span> Skill
                            </span>
                            <span>0</span>
                        </li>
                        <li class="breakdown-item">
                            <span class="breakdown-label">
                                <span class="breakdown-dot dot-agent"></span> Agent
                            </span>
                            <span>0</span>
                        </li>
                        <li class="breakdown-item">
                            <span class="breakdown-label">
                                <span class="breakdown-dot dot-llm"></span> LLM
                            </span>
                            <span>0</span>
                        </li>
                    </ul>
                </div>
            </div>
            
            <!-- Events Panel -->
            <div class="events-panel">
                <h3 style="margin-bottom:16px">📡 Live Events</h3>
                <div id="eventsList">
                    <div style="color:var(--text-secondary);padding:20px;text-align:center">
                        Waiting for events...
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <script>
        // Dashboard State
        let dashboardData = null;
        let eventSource = null;
        
        // Fetch Dashboard Data
        async function fetchDashboard() {
            try {
                const res = await fetch('/api/dashboard');
                dashboardData = await res.json();
                updateUI();
            } catch (e) {
                console.error('Failed to fetch dashboard:', e);
            }
        }
        
        // Update UI
        function updateUI() {
            if (!dashboardData) return;
            
            const { overview, span_breakdown, recent_traces, recent_events, status } = dashboardData;
            
            // Status
            const statusEl = document.getElementById('systemStatus');
            statusEl.className = `status-badge status-${status}`;
            statusEl.textContent = `● ${status.charAt(0).toUpperCase() + status.slice(1)}`;
            
            // Stats
            document.getElementById('totalRequests').textContent = overview.total_requests;
            document.getElementById('avgDuration').innerHTML = `${overview.avg_duration_ms}<span style="font-size:16px">ms</span>`;
            document.getElementById('avgFeedback').innerHTML = `${overview.avg_feedback_score}<span style="font-size:16px">/5</span>`;
            document.getElementById('errorRate').innerHTML = `${overview.error_rate_pct}<span style="font-size:16px">%</span>`;
            
            // Traces
            const tracesBody = document.getElementById('tracesBody');
            if (recent_traces.length > 0) {
                tracesBody.innerHTML = recent_traces.slice(0, 10).map(t => `
                    <tr>
                        <td><span class="trace-status ${t.status}"></span>${t.status}</td>
                        <td style="font-family:monospace">${t.trace_id}</td>
                        <td>${t.name}</td>
                        <td>${t.duration_ms.toFixed(1)}ms</td>
                        <td>${t.spans_count}</td>
                    </tr>
                `).join('');
            }
            
            // Span Breakdown
            updateSpanBreakdown(span_breakdown);
            
            // Events
            updateEvents(recent_events);
        }
        
        function updateSpanBreakdown(breakdown) {
            const kindColors = {
                chat: 'dot-chat',
                routing: 'dot-routing',
                skill: 'dot-skill',
                agent: 'dot-agent',
                llm: 'dot-llm',
            };
            
            const list = document.getElementById('spanBreakdown');
            list.innerHTML = Object.entries(breakdown || {}).map(([kind, data]) => `
                <li class="breakdown-item">
                    <span class="breakdown-label">
                        <span class="breakdown-dot ${kindColors[kind] || 'dot-chat'}"></span>
                        ${kind.charAt(0).toUpperCase() + kind.slice(1)}
                    </span>
                    <span>${data.count} (${(data.duration_ms / 1000).toFixed(1)}s)</span>
                </li>
            `).join('') || '<li style="color:var(--text-secondary)">No data</li>';
        }
        
        function updateEvents(events) {
            const list = document.getElementById('eventsList');
            if (!events || events.length === 0) {
                list.innerHTML = '<div style="color:var(--text-secondary);padding:20px;text-align:center">No events yet</div>';
                return;
            }
            
            const icons = {
                info: '💬',
                warning: '⚠️',
                error: '❌',
            };
            
            list.innerHTML = events.slice(0, 15).map(e => `
                <div class="event-item">
                    <div class="event-icon ${e.severity}">${icons[e.severity] || '📌'}</div>
                    <div class="event-content">
                        <div class="event-type">${e.event_type}</div>
                        <div class="event-time">${new Date(e.timestamp * 1000).toLocaleTimeString()}</div>
                    </div>
                </div>
            `).join('');
        }
        
        // Send Chat
        async function sendChat() {
            const input = document.getElementById('chatInput');
            const btn = document.getElementById('chatBtn');
            const result = document.getElementById('chatResult');
            
            const query = input.value.trim();
            if (!query) return;
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            result.style.display = 'block';
            result.textContent = 'Sending query...';
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query }),
                });
                
                const data = await res.json();
                
                if (res.ok) {
                    result.innerHTML = `<strong>Mode:</strong> ${data.mode}
<strong>Trace ID:</strong> ${data.trace_id}
<strong>Skills:</strong> ${data.skills_used.join(', ') || 'None'}
<strong>Duration:</strong> ${data.execution_time.toFixed(2)}s

<strong>Response:</strong>
${data.response}`;
                    fetchDashboard();
                } else {
                    result.textContent = `Error: ${data.detail}`;
                }
            } catch (e) {
                result.textContent = `Error: ${e.message}`;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Send';
            }
        }
        
        // SSE Events
        function connectSSE() {
            eventSource = new EventSource('/api/events/stream');
            
            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log('SSE Event:', data);
                fetchDashboard();
            };
            
            eventSource.onerror = () => {
                console.error('SSE connection error');
                setTimeout(connectSSE, 5000);
            };
        }
        
        // Panel Navigation
        function showPanel(panel) {
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            event.target.closest('.nav-item').classList.add('active');
            // TODO: Switch panels
        }
        
        // Initialize
        fetchDashboard();
        setInterval(fetchDashboard, 5000);
        connectSSE();
    </script>
</body>
</html>
"""


# ===============================
# Run Server
# ===============================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "observability_api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )
