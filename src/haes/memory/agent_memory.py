"""
Agent Memory System - 3계층 메모리 시스템

28-agent-memory SKILL 기반:
- 세션 메모리 (Working Memory): 현재 대화 컨텍스트
- 단기 메모리 (Observations): 최근 세션 히스토리 (claude-mem 스타일)
- 장기 메모리 (Reasoning): 핵심 결정/패턴 (grov 스타일)
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from loguru import logger


@dataclass
class MemoryEntry:
    """메모리 항목"""
    id: str
    timestamp: str
    content: str
    memory_type: str  # "session", "short", "long"
    query: Optional[str] = None
    mode: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    score: Optional[float] = None  # 중요도 (피드백 점수)
    tags: List[str] = field(default_factory=list)


class AgentMemory:
    """
    3계층 에이전트 메모리 시스템
    
    Layer 1: Working Memory (세션) - 현재 대화
    Layer 2: Short-term (단기) - 최근 세션 요약 (sqlite)
    Layer 3: Long-term (장기) - 핵심 결정/패턴 (sqlite)
    """
    
    # 토큰 할당
    TOKEN_LIMITS = {
        "session": 4000,   # 세션 메모리
        "short": 1500,     # 단기 메모리
        "long": 1000,      # 장기 메모리
    }
    
    # 단기 → 장기 승격 임계값
    PROMOTION_THRESHOLD = 4.0  # 4점 이상 피드백 시 장기 기억으로
    
    # 단기 메모리 유지 기간
    SHORT_TERM_DAYS = 7
    
    def __init__(self, db_path: Optional[str] = None):
        """
        초기화
        
        Args:
            db_path: SQLite DB 경로
        """
        self.db_path = db_path or str(Path.home() / ".haes" / "memory.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._init_db()
        
        # 세션 메모리 (인메모리)
        self.session_memory: List[Dict] = []
        
        logger.info(f"AgentMemory initialized: {self.db_path}")
    
    def _init_db(self):
        """DB 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 메모리 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                content TEXT,
                memory_type TEXT,
                query TEXT,
                mode TEXT,
                skills TEXT,
                score REAL,
                tags TEXT
            )
        """)
        
        # 인덱스
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
        
        conn.commit()
        conn.close()
    
    # ================================
    # Layer 1: 세션 메모리 (Working Memory)
    # ================================
    
    def add_to_session(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        세션 메모리에 추가
        
        Args:
            role: "user" 또는 "assistant"
            content: 내용
            metadata: 추가 정보 (mode, skills 등)
        """
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            entry["metadata"] = metadata
        
        self.session_memory.append(entry)
        
        # 토큰 제한 관리 (간단히 최근 N개만 유지)
        max_entries = 20
        if len(self.session_memory) > max_entries:
            self.session_memory = self.session_memory[-max_entries:]
    
    def get_session_context(self) -> List[Dict]:
        """세션 컨텍스트 반환"""
        return self.session_memory.copy()
    
    def clear_session(self):
        """세션 메모리 초기화"""
        self.session_memory.clear()
    
    # ================================
    # Layer 2: 단기 메모리 (Observations)
    # ================================
    
    def save_short_term(
        self,
        query: str,
        response: str,
        mode: str,
        skills: List[str],
        score: Optional[float] = None,
    ):
        """
        단기 메모리에 저장 (claude-mem 스타일)
        
        Args:
            query: 사용자 질문
            response: AI 응답 요약
            mode: 실행 모드
            skills: 사용된 SKILL
            score: 피드백 점수 (있으면)
        """
        # 응답 요약 (첫 500자)
        summary = response[:500] if len(response) > 500 else response
        
        entry = MemoryEntry(
            id=self._generate_id(query),
            timestamp=datetime.now().isoformat(),
            content=summary,
            memory_type="short",
            query=query,
            mode=mode,
            skills=skills,
            score=score,
            tags=self._extract_tags(query + " " + response),
        )
        
        self._save_entry(entry)
        
        # 고점수면 장기 메모리로 승격
        if score and score >= self.PROMOTION_THRESHOLD:
            self._promote_to_long_term(entry)
        
        # 오래된 단기 메모리 정리
        self._cleanup_old_memories()
    
    def search_short_term(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """
        단기 메모리 검색
        
        Args:
            query: 검색 쿼리
            limit: 최대 결과 수
            
        Returns:
            관련 메모리 항목
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # FTS 검색 (간단 구현)
        keywords = query.lower().split()
        conditions = " OR ".join([f"content LIKE '%{kw}%'" for kw in keywords])
        
        cursor.execute(f"""
            SELECT * FROM memories 
            WHERE memory_type = 'short' 
            AND ({conditions})
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = [self._row_to_entry(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    # ================================
    # Layer 3: 장기 메모리 (Reasoning)
    # ================================
    
    def save_long_term(
        self,
        content: str,
        query: str,
        tags: List[str],
        reasoning: Optional[str] = None,
    ):
        """
        장기 메모리에 저장 (grov 스타일)
        
        핵심 결정, 패턴, 중요 인사이트 저장
        
        Args:
            content: 핵심 내용
            query: 원본 질문
            tags: 태그
            reasoning: 결정 이유
        """
        full_content = content
        if reasoning:
            full_content = f"**결정**: {content}\n**이유**: {reasoning}"
        
        entry = MemoryEntry(
            id=self._generate_id(content),
            timestamp=datetime.now().isoformat(),
            content=full_content,
            memory_type="long",
            query=query,
            tags=tags,
            score=5.0,  # 장기 메모리는 항상 중요
        )
        
        self._save_entry(entry)
    
    def get_long_term_context(self, query: str, limit: int = 3) -> str:
        """
        장기 메모리에서 관련 컨텍스트 가져오기
        
        Args:
            query: 현재 쿼리
            limit: 최대 항목 수
            
        Returns:
            포맷된 컨텍스트
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 먼저 키워드 검색
        keywords = query.lower().split()
        conditions = " OR ".join([f"content LIKE '%{kw}%' OR query LIKE '%{kw}%' OR tags LIKE '%{kw}%'" for kw in keywords])
        
        cursor.execute(f"""
            SELECT * FROM memories 
            WHERE memory_type = 'long' 
            AND ({conditions})
            ORDER BY score DESC, timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = list(cursor.fetchall())
        
        # 키워드 검색 결과가 부족하면 최근 장기 기억도 추가
        if len(results) < limit:
            cursor.execute("""
                SELECT * FROM memories 
                WHERE memory_type = 'long'
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit - len(results),))
            
            recent = cursor.fetchall()
            existing_ids = {r['id'] for r in results}
            for r in recent:
                if r['id'] not in existing_ids:
                    results.append(r)
        
        conn.close()
        
        if not results:
            return ""
        
        context_parts = ["## 관련 장기 기억:"]
        for row in results:
            query_part = f"(Q: {row['query'][:50]})" if row['query'] else ""
            context_parts.append(f"- {query_part} {row['content'][:300]}...")
        
        return "\n".join(context_parts)
    
    # ================================
    # Progressive Disclosure (토큰 최적화)
    # ================================
    
    def get_optimal_context(
        self,
        query: str,
        max_tokens: int = 6500,
    ) -> Dict[str, str]:
        """
        최적화된 컨텍스트 반환 (Progressive Disclosure)
        
        토큰 예산에 맞게 3계층 메모리 조합
        
        Args:
            query: 현재 쿼리
            max_tokens: 최대 토큰 수
            
        Returns:
            계층별 컨텍스트
        """
        context = {
            "session": "",
            "short_term": "",
            "long_term": "",
        }
        
        # 1. 장기 메모리 (가장 중요)
        if max_tokens >= 1000:
            context["long_term"] = self.get_long_term_context(query)
        
        # 2. 단기 메모리 (관련성 높은 것만)
        if max_tokens >= 2500:
            short_results = self.search_short_term(query, limit=3)
            if short_results:
                parts = ["## 최근 관련 대화:"]
                for r in short_results:
                    parts.append(f"- Q: {r.query[:50]}... → {r.content[:100]}...")
                context["short_term"] = "\n".join(parts)
        
        # 3. 세션 메모리 (현재 대화)
        if max_tokens >= 4000:
            session = self.get_session_context()
            if session:
                parts = ["## 현재 세션:"]
                for s in session[-5:]:  # 최근 5개만
                    role = s.get("role", "unknown")
                    content = s.get("content", "")[:100]
                    parts.append(f"- [{role}]: {content}...")
                context["session"] = "\n".join(parts)
        
        return context
    
    # ================================
    # 헬퍼 메서드
    # ================================
    
    def _generate_id(self, content: str) -> str:
        """ID 생성"""
        return hashlib.md5(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
    
    def _extract_tags(self, text: str) -> List[str]:
        """태그 추출 (간단 구현)"""
        # 주요 키워드 추출
        keywords = ["LoRA", "RAG", "파인튜닝", "추론", "배포", "API", 
                   "GPT", "Claude", "검색", "메모리", "에이전트"]
        tags = []
        text_lower = text.lower()
        for kw in keywords:
            if kw.lower() in text_lower:
                tags.append(kw)
        return tags[:5]  # 최대 5개
    
    def _save_entry(self, entry: MemoryEntry):
        """DB에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (id, timestamp, content, memory_type, query, mode, skills, score, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.id,
            entry.timestamp,
            entry.content,
            entry.memory_type,
            entry.query,
            entry.mode,
            json.dumps(entry.skills) if entry.skills else "[]",
            entry.score,
            json.dumps(entry.tags) if entry.tags else "[]",
        ))
        
        conn.commit()
        conn.close()
    
    def _row_to_entry(self, row: sqlite3.Row) -> MemoryEntry:
        """DB 행을 MemoryEntry로 변환"""
        return MemoryEntry(
            id=row["id"],
            timestamp=row["timestamp"],
            content=row["content"],
            memory_type=row["memory_type"],
            query=row["query"],
            mode=row["mode"],
            skills=json.loads(row["skills"]) if row["skills"] else [],
            score=row["score"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
        )
    
    def _promote_to_long_term(self, entry: MemoryEntry):
        """단기 → 장기 메모리 승격"""
        self.save_long_term(
            content=entry.content,
            query=entry.query or "",
            tags=entry.tags,
        )
        logger.info(f"Memory promoted to long-term: {entry.id}")
    
    def _cleanup_old_memories(self):
        """오래된 단기 메모리 정리"""
        cutoff = (datetime.now() - timedelta(days=self.SHORT_TERM_DAYS)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM memories 
            WHERE memory_type = 'short' 
            AND timestamp < ?
        """, (cutoff,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logger.debug(f"Cleaned up {deleted} old short-term memories")
    
    def get_stats(self) -> Dict[str, int]:
        """메모리 통계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
        stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "session": len(self.session_memory),
            "short_term": stats.get("short", 0),
            "long_term": stats.get("long", 0),
        }


# 싱글톤
_memory: Optional[AgentMemory] = None

def get_memory() -> AgentMemory:
    """메모리 싱글톤 반환"""
    global _memory
    if _memory is None:
        _memory = AgentMemory()
    return _memory
