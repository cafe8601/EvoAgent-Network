"""
HAES API Server - FastAPI 기반 Web API

REST API로 HAES 시스템에 접근
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

from haes import HybridAISystem, Config
from haes.llm import OpenAIClient


# ===============================
# Pydantic Models
# ===============================

class ChatRequest(BaseModel):
    """채팅 요청"""
    query: str = Field(..., description="사용자 질문", min_length=1)
    
class ChatResponse(BaseModel):
    """채팅 응답"""
    response: str = Field(..., description="AI 응답")
    mode: str = Field(..., description="실행 모드")
    skills_used: List[str] = Field(default=[], description="사용된 SKILL")
    agents_used: List[str] = Field(default=[], description="사용된 에이전트")
    execution_time: float = Field(..., description="실행 시간 (초)")
    cost_estimate: str = Field(default="", description="예상 비용")

class FeedbackRequest(BaseModel):
    """피드백 요청"""
    score: int = Field(..., ge=1, le=5, description="평가 점수 (1-5)")
    comment: str = Field(default="", description="추가 의견")

class FeedbackResponse(BaseModel):
    """피드백 응답"""
    success: bool
    message: str

class StatsResponse(BaseModel):
    """시스템 통계"""
    skills_indexed: int
    agents_loaded: int
    feedbacks_count: int
    learned_patterns: int
    history_length: int
    # 3계층 메모리
    session_memory: int = 0
    short_term_memory: int = 0
    long_term_memory: int = 0

class HealthResponse(BaseModel):
    """헬스 체크"""
    status: str
    version: str
    models: dict


# ===============================
# Global State
# ===============================

system: Optional[HybridAISystem] = None
llm_client: Optional[OpenAIClient] = None


# ===============================
# Lifespan (시작/종료)
# ===============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행"""
    global system, llm_client
    
    print("🚀 HAES API Server 시작...")
    
    # OpenAI 클라이언트 초기화
    try:
        llm_client = OpenAIClient(
            routing_model=os.getenv("ROUTING_MODEL", "gpt-5-mini"),
            main_model=os.getenv("MAIN_MODEL", "gpt-5.1"),
        )
        print(f"✅ OpenAI 연결: {llm_client.main_model}")
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
        persist_dir=Path(__file__).parent / "api_vectordb",
    )
    
    # 시스템 초기화
    system = HybridAISystem(config=config, llm_client=llm_client)
    stats = system.initialize()
    print(f"✅ 초기화 완료: {stats['skills_indexed']}개 SKILL, {stats['agents_loaded']}개 에이전트")
    
    yield
    
    # 종료
    print("👋 HAES API Server 종료...")


# ===============================
# FastAPI App
# ===============================

app = FastAPI(
    title="HAES API",
    description="Hybrid AI Evolution System - 93개 SKILL + 449개 에이전트 통합 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 정적 파일 (static 폴더가 있는 경우)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# ===============================
# Endpoints
# ===============================

@app.get("/", tags=["Root"])
async def root():
    """웹 UI 반환"""
    index_file = Path(__file__).parent / "static" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    return {
        "name": "HAES API",
        "description": "Hybrid AI Evolution System",
        "version": "1.0.0",
        "docs": "/docs",
        "ui": "/static/index.html",
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """헬스 체크"""
    return HealthResponse(
        status="healthy" if system else "initializing",
        version="1.0.0",
        models={
            "routing": llm_client.routing_model if llm_client else "none",
            "main": llm_client.main_model if llm_client else "none",
        }
    )


@app.get("/stats", response_model=StatsResponse, tags=["System"])
async def get_stats():
    """시스템 통계"""
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    stats = system.get_stats()
    memory_stats = stats.get("memory", {"session": 0, "short_term": 0, "long_term": 0})
    
    return StatsResponse(
        skills_indexed=stats["skill_store"]["total_skills"],
        agents_loaded=stats["agent_pool"]["total_agents"],
        feedbacks_count=stats["feedback"]["total"],
        learned_patterns=stats["evolution"]["learned_patterns_count"],
        history_length=stats["history_length"],
        session_memory=memory_stats.get("session", 0),
        short_term_memory=memory_stats.get("short_term", 0),
        long_term_memory=memory_stats.get("long_term", 0),
    )


@app.get("/skills", tags=["Skills"])
async def get_skills():
    """SKILL 목록"""
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    skills = system.skill_store.list_all_skills()
    return {
        "count": len(skills),
        "skills": [
            {"id": s.skill_id, "name": s.name, "description": s.description}
            for s in skills
        ]
    }


@app.get("/skills/index", tags=["Skills"])
async def get_skill_index():
    """압축 SKILL 인덱스"""
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return {"index": system.get_compressed_index()}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    AI 채팅
    
    쿼리를 분석하고 적절한 SKILL과 에이전트를 선택하여 응답 생성
    """
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        result = await system.chat(request.query)
        
        return ChatResponse(
            response=result.response,
            mode=result.mode,
            skills_used=result.skills_used,
            agents_used=result.agents_used,
            execution_time=result.execution_time,
            cost_estimate=result.cost_estimate or "",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_feedback(request: FeedbackRequest):
    """
    피드백 제출
    
    마지막 응답에 대한 평가
    """
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        system.feedback(score=request.score, comment=request.comment)
        return FeedbackResponse(
            success=True,
            message=f"피드백 저장 완료: {request.score}점"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/history", tags=["Chat"])
async def get_history():
    """대화 히스토리"""
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return {
        "count": len(system.history) // 2,
        "history": system.history[-20:]  # 최근 20개
    }


@app.delete("/history", tags=["Chat"])
async def clear_history():
    """대화 히스토리 초기화"""
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    system.history.clear()
    return {"message": "히스토리가 초기화되었습니다."}


# ===============================
# Run Server
# ===============================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
