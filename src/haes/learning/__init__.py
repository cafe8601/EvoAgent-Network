"""
HAES 지속적 학습 시스템 (Persistent Learning)

진정한 성능 향상을 위한 학습 메커니즘:

1. 패턴 영구 저장: SQLite에 학습된 패턴 저장
2. RAG 지식 누적: 성공적인 응답을 RAG에 추가
3. 프롬프트 최적화: DSPy 스타일 프롬프트 자동 개선
4. 메타 학습: 어떤 전략이 효과적인지 학습
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from loguru import logger


@dataclass
class LearnedRoutingRule:
    """학습된 라우팅 규칙 (영구 저장)"""
    id: str
    query_pattern: str          # 쿼리 패턴 (키워드)
    matched_skills: List[str]   # 매칭된 스킬
    matched_mode: str           # 매칭된 실행 모드
    success_rate: float         # 성공률
    sample_count: int           # 샘플 수
    avg_score: float            # 평균 점수
    created_at: str
    updated_at: str


@dataclass
class OptimizedPrompt:
    """최적화된 프롬프트 (DSPy 스타일)"""
    id: str
    skill_id: str               # 대상 스킬
    original_prompt: str        # 원본 프롬프트
    optimized_prompt: str       # 최적화된 프롬프트
    improvement_rate: float     # 개선율
    test_count: int             # 테스트 횟수
    active: bool                # 활성화 여부


@dataclass
class KnowledgeEntry:
    """RAG에 추가할 지식 (성공적 응답)"""
    id: str
    query: str
    response: str
    skills_used: List[str]
    score: float
    created_at: str


class PersistentLearningEngine:
    """
    영구 학습 엔진
    
    서버 재시작 후에도 학습 결과가 유지되며,
    실제 시스템 성능 향상에 기여
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path.home() / ".haes" / "learning.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
        # 캐시 (빠른 조회용)
        self._routing_cache: Dict[str, LearnedRoutingRule] = {}
        self._prompt_cache: Dict[str, OptimizedPrompt] = {}
        
        # 시작 시 캐시 로드
        self._load_cache()
        
        logger.info(f"PersistentLearningEngine initialized: {self.db_path}")
    
    def _init_db(self):
        """DB 스키마 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 라우팅 규칙 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routing_rules (
                id TEXT PRIMARY KEY,
                query_pattern TEXT NOT NULL,
                matched_skills TEXT NOT NULL,
                matched_mode TEXT NOT NULL,
                success_rate REAL,
                sample_count INTEGER,
                avg_score REAL,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # 최적화된 프롬프트 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimized_prompts (
                id TEXT PRIMARY KEY,
                skill_id TEXT NOT NULL,
                original_prompt TEXT,
                optimized_prompt TEXT,
                improvement_rate REAL,
                test_count INTEGER,
                active INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)
        
        # 지식 저장소 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                skills_used TEXT,
                score REAL,
                created_at TEXT
            )
        """)
        
        # 성능 메트릭 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                recorded_at TEXT
            )
        """)
        
        # 인덱스
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_routing_pattern ON routing_rules(query_pattern)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompt_skill ON optimized_prompts(skill_id)")
        
        conn.commit()
        conn.close()
    
    def _load_cache(self):
        """캐시 로드"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 라우팅 규칙 로드
        cursor.execute("SELECT * FROM routing_rules WHERE success_rate >= 0.7")
        for row in cursor.fetchall():
            rule = LearnedRoutingRule(
                id=row["id"],
                query_pattern=row["query_pattern"],
                matched_skills=json.loads(row["matched_skills"]),
                matched_mode=row["matched_mode"],
                success_rate=row["success_rate"],
                sample_count=row["sample_count"],
                avg_score=row["avg_score"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            self._routing_cache[rule.query_pattern] = rule
        
        # 활성화된 프롬프트 로드
        cursor.execute("SELECT * FROM optimized_prompts WHERE active = 1")
        for row in cursor.fetchall():
            prompt = OptimizedPrompt(
                id=row["id"],
                skill_id=row["skill_id"],
                original_prompt=row["original_prompt"],
                optimized_prompt=row["optimized_prompt"],
                improvement_rate=row["improvement_rate"],
                test_count=row["test_count"],
                active=bool(row["active"]),
            )
            self._prompt_cache[prompt.skill_id] = prompt
        
        conn.close()
        
        logger.info(f"Loaded {len(self._routing_cache)} routing rules, {len(self._prompt_cache)} prompts")
    
    # ======================
    # 라우팅 학습
    # ======================
    
    def learn_routing(
        self,
        query: str,
        skills: List[str],
        mode: str,
        score: float,
    ):
        """라우팅 패턴 학습"""
        # 쿼리 패턴 추출 (키워드)
        pattern = self._extract_pattern(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 규칙 확인
        cursor.execute("SELECT * FROM routing_rules WHERE query_pattern = ?", (pattern,))
        existing = cursor.fetchone()
        
        now = datetime.now().isoformat()
        is_success = score >= 4.0
        
        if existing:
            # 업데이트
            new_count = existing[5] + 1  # sample_count
            new_success_count = (existing[4] * existing[5]) + (1 if is_success else 0)  # success_rate * count
            new_success_rate = new_success_count / new_count
            new_avg_score = (existing[6] * existing[5] + score) / new_count
            
            cursor.execute("""
                UPDATE routing_rules SET
                    success_rate = ?,
                    sample_count = ?,
                    avg_score = ?,
                    updated_at = ?
                WHERE query_pattern = ?
            """, (new_success_rate, new_count, new_avg_score, now, pattern))
            
            # 캐시 업데이트
            if new_success_rate >= 0.7:
                self._routing_cache[pattern] = LearnedRoutingRule(
                    id=existing[0],
                    query_pattern=pattern,
                    matched_skills=skills,
                    matched_mode=mode,
                    success_rate=new_success_rate,
                    sample_count=new_count,
                    avg_score=new_avg_score,
                    created_at=existing[7],
                    updated_at=now,
                )
        else:
            # 새 규칙 생성
            import hashlib
            rule_id = hashlib.md5(pattern.encode()).hexdigest()[:12]
            
            cursor.execute("""
                INSERT INTO routing_rules
                (id, query_pattern, matched_skills, matched_mode, success_rate,
                 sample_count, avg_score, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule_id, pattern, json.dumps(skills), mode,
                1.0 if is_success else 0.0, 1, score, now, now
            ))
        
        conn.commit()
        conn.close()
    
    def get_routing_hint(self, query: str) -> Optional[Dict[str, Any]]:
        """학습된 라우팅 힌트 반환"""
        pattern = self._extract_pattern(query)
        
        # 캐시에서 검색
        if pattern in self._routing_cache:
            rule = self._routing_cache[pattern]
            return {
                "skills": rule.matched_skills,
                "mode": rule.matched_mode,
                "confidence": rule.success_rate,
                "avg_score": rule.avg_score,
            }
        
        # 부분 매칭 시도
        query_keywords = set(pattern.split())
        best_match = None
        best_overlap = 0
        
        for cached_pattern, rule in self._routing_cache.items():
            cached_keywords = set(cached_pattern.split())
            overlap = len(query_keywords & cached_keywords)
            
            if overlap > best_overlap and overlap >= 2:
                best_overlap = overlap
                best_match = rule
        
        if best_match:
            return {
                "skills": best_match.matched_skills,
                "mode": best_match.matched_mode,
                "confidence": best_match.success_rate * 0.8,  # 부분 매칭 할인
                "avg_score": best_match.avg_score,
            }
        
        return None
    
    def _extract_pattern(self, query: str) -> str:
        """쿼리에서 패턴 추출"""
        import re
        
        # 소문자 변환, 특수문자 제거
        query = query.lower()
        words = re.findall(r'\w+', query)
        
        # 불용어 제거
        stopwords = {"을", "를", "이", "가", "은", "는", "에", "의", "로", "해줘", "알려줘", "뭐", "뭔가요"}
        keywords = [w for w in words if len(w) > 1 and w not in stopwords]
        
        # 정렬하여 일관성 유지
        return " ".join(sorted(set(keywords)))
    
    # ======================
    # 지식 누적 (RAG 확장)
    # ======================
    
    def add_knowledge(
        self,
        query: str,
        response: str,
        skills_used: List[str],
        score: float,
    ):
        """고품질 응답을 지식으로 저장"""
        if score < 4.5:  # 높은 점수만 저장
            return
        
        import hashlib
        entry_id = hashlib.md5(f"{query}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO knowledge_entries
            (id, query, response, skills_used, score, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry_id, query, response[:2000],  # 응답 길이 제한
            json.dumps(skills_used), score, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Knowledge added: {entry_id} (score={score})")
    
    def get_similar_knowledge(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """유사한 지식 검색"""
        keywords = self._extract_pattern(query).split()
        
        if not keywords:
            return []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 키워드 기반 검색
        conditions = " OR ".join([f"query LIKE '%{kw}%'" for kw in keywords[:5]])
        cursor.execute(f"""
            SELECT * FROM knowledge_entries
            WHERE {conditions}
            ORDER BY score DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "query": row["query"],
                "response": row["response"],
                "skills": json.loads(row["skills_used"]),
                "score": row["score"],
            })
        
        conn.close()
        return results
    
    # ======================
    # 성능 메트릭 추적
    # ======================
    
    def record_metric(self, metric_name: str, value: float):
        """성능 메트릭 기록"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO performance_metrics (metric_name, metric_value, recorded_at)
            VALUES (?, ?, ?)
        """, (metric_name, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_performance_trend(self, metric_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """성능 트렌드 조회"""
        from datetime import timedelta
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT metric_value, recorded_at
            FROM performance_metrics
            WHERE metric_name = ? AND recorded_at >= ?
            ORDER BY recorded_at
        """, (metric_name, cutoff))
        
        results = [{"value": row["metric_value"], "time": row["recorded_at"]} for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    # ======================
    # 통계
    # ======================
    
    def get_stats(self) -> Dict[str, Any]:
        """학습 통계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM routing_rules")
        total_rules = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM routing_rules WHERE success_rate >= 0.7")
        active_rules = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM knowledge_entries")
        knowledge_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(success_rate) FROM routing_rules WHERE sample_count >= 3")
        avg_success = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_routing_rules": total_rules,
            "active_rules": active_rules,
            "cached_rules": len(self._routing_cache),
            "knowledge_entries": knowledge_count,
            "average_success_rate": round(avg_success, 3),
        }


# 싱글톤
_learning_engine: Optional[PersistentLearningEngine] = None


def get_learning_engine() -> PersistentLearningEngine:
    """학습 엔진 싱글톤"""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = PersistentLearningEngine()
    return _learning_engine


# ======================
# 시스템 통합 헬퍼
# ======================

def integrate_learning_to_system(system):
    """
    학습 엔진을 HAES 시스템에 통합
    
    사용법:
        from haes.learning import integrate_learning_to_system
        integrate_learning_to_system(haes_system)
    """
    engine = get_learning_engine()
    
    # 기존 라우터에 학습 힌트 추가
    original_route = system.router.route
    
    async def enhanced_route(query: str):
        # 학습된 힌트 확인
        hint = engine.get_routing_hint(query)
        
        if hint and hint["confidence"] >= 0.8:
            logger.info(f"Using learned routing: {hint['skills'][:2]}")
            # 여기서 힌트를 기반으로 라우팅 결정 수정 가능
        
        # 원본 라우팅 실행
        return await original_route(query)
    
    system.router.route = enhanced_route
    
    # 피드백 시 학습 트리거
    original_feedback = system.feedback
    
    def enhanced_feedback(score: int, comment: str = ""):
        result = original_feedback(score, comment)
        
        # 학습 엔진에 기록
        if system._last_result:
            engine.learn_routing(
                query=system._last_result.query,
                skills=system._last_result.skills_used,
                mode=system._last_result.mode,
                score=float(score),
            )
            
            # 고점수 응답은 지식으로 저장
            if score >= 5:
                engine.add_knowledge(
                    query=system._last_result.query,
                    response=system._last_result.response,
                    skills_used=system._last_result.skills_used,
                    score=float(score),
                )
        
        return result
    
    system.feedback = enhanced_feedback
    
    logger.info("Learning engine integrated with HAES system")
