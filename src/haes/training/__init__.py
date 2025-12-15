"""
HAES 자동 훈련 시스템 (Sandbox-based Training)

샌드박스 환경에서 시스템을 자동으로 훈련하여 능력 향상

훈련 방식:
1. 합성 데이터 생성: 다양한 쿼리-응답 쌍 생성
2. 자동 평가: LLM 기반 응답 품질 평가
3. 패턴 학습: 성공 패턴을 Evolution Engine에 전달
4. 라우팅 최적화: 스킬/에이전트 매핑 개선
5. A/B 테스트: 여러 전략 비교

학습 데이터 저장: SQLite (영구)
"""

import os
import json
import sqlite3
import asyncio
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from loguru import logger


@dataclass
class TrainingExample:
    """훈련 예제"""
    id: str
    query: str
    expected_skills: List[str]
    expected_mode: str
    difficulty: str = "medium"  # easy, medium, hard
    category: str = "general"
    tags: List[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """평가 결과"""
    example_id: str
    score: float  # 0-5
    response_quality: float  # 0-1
    skill_match: float  # 0-1
    mode_match: bool
    execution_time_ms: float
    response_preview: str
    feedback: str


@dataclass
class TrainingSession:
    """훈련 세션"""
    id: str
    started_at: str
    completed_at: Optional[str] = None
    total_examples: int = 0
    evaluated: int = 0
    success_count: int = 0
    average_score: float = 0.0
    patterns_learned: int = 0
    status: str = "running"


class SyntheticDataGenerator:
    """
    합성 훈련 데이터 생성기
    
    다양한 난이도와 카테고리의 쿼리 생성
    """
    
    # 카테고리별 쿼리 템플릿
    TEMPLATES = {
        "simple_question": [
            "{topic}가 뭐야?",
            "{topic} 설명해줘",
            "{topic}이 뭔가요?",
            "What is {topic}?",
            "{topic}에 대해 알려줘",
        ],
        "implementation": [
            "{topic} 구현해줘",
            "{topic} 만들어줘",
            "{topic} 코드 작성해줘",
            "Implement {topic}",
            "{topic} 개발해줘",
        ],
        "multi_task": [
            "{topic1} 구현하고 {topic2} 테스트해줘",
            "{topic1} 만들고 {topic2} 문서화해줘",
            "{topic1} 설계하고 {topic2} 구현하고 {topic3} 검증해줘",
        ],
        "comparison": [
            "{topic1}와 {topic2} 비교해줘",
            "{topic1} vs {topic2} 차이점",
            "{topic1}하고 {topic2} 뭐가 더 좋아?",
        ],
    }
    
    # 토픽별 관련 스킬
    TOPICS = {
        "LoRA": ["03-fine-tuning", "11-fine-tuning"],
        "RAG": ["15-rag", "chroma", "sentence-transformers"],
        "LangChain": ["14-agents", "langchain"],
        "파인튜닝": ["03-fine-tuning", "11-fine-tuning"],
        "추론": ["12-inference-serving", "vllm"],
        "모니터링": ["17-observability", "langsmith"],
        "에이전트": ["14-agents", "crewai", "langgraph"],
        "프롬프트": ["16-prompt-engineering", "dspy"],
        "벡터DB": ["15-rag", "chroma", "qdrant"],
        "배포": ["09-infrastructure", "modal"],
    }
    
    def generate_examples(self, count: int = 50) -> List[TrainingExample]:
        """훈련 예제 생성"""
        examples = []
        
        for i in range(count):
            category = random.choice(list(self.TEMPLATES.keys()))
            templates = self.TEMPLATES[category]
            template = random.choice(templates)
            
            # 토픽 선택
            topics = list(self.TOPICS.keys())
            
            if "{topic1}" in template and "{topic2}" in template:
                selected = random.sample(topics, min(3, len(topics)))
                query = template.format(
                    topic1=selected[0],
                    topic2=selected[1],
                    topic3=selected[2] if len(selected) > 2 else selected[0],
                )
                expected_skills = []
                for t in selected[:2]:
                    expected_skills.extend(self.TOPICS.get(t, []))
            else:
                topic = random.choice(topics)
                query = template.format(topic=topic)
                expected_skills = self.TOPICS.get(topic, [])
            
            # 난이도 및 모드 결정
            if category == "simple_question":
                difficulty = "easy"
                expected_mode = "skill_only"
            elif category == "implementation":
                difficulty = "medium"
                expected_mode = "skill_agent"
            elif category == "multi_task":
                difficulty = "hard"
                expected_mode = "parallel" if "하고" in query else "multi_agent"
            else:
                difficulty = "medium"
                expected_mode = "skill_only"
            
            examples.append(TrainingExample(
                id=f"train-{i+1:04d}",
                query=query,
                expected_skills=list(set(expected_skills))[:3],
                expected_mode=expected_mode,
                difficulty=difficulty,
                category=category,
                tags=[category, difficulty],
            ))
        
        return examples


class AutoEvaluator:
    """
    자동 평가기
    
    LLM을 사용하여 응답 품질 자동 평가
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client
    
    async def evaluate(
        self,
        example: TrainingExample,
        response: str,
        skills_used: List[str],
        mode_used: str,
        execution_time_ms: float,
    ) -> EvaluationResult:
        """응답 평가"""
        # 스킬 매칭 점수
        if example.expected_skills and skills_used:
            matched = sum(1 for s in example.expected_skills if any(
                exp in s or s in exp for exp in skills_used
            ))
            skill_match = matched / len(example.expected_skills)
        else:
            skill_match = 0.5  # 기본값
        
        # 모드 매칭
        mode_match = mode_used == example.expected_mode
        
        # 응답 품질 평가 (길이 기반 휴리스틱)
        response_length = len(response)
        if example.difficulty == "easy":
            ideal_length = 500
        elif example.difficulty == "hard":
            ideal_length = 2000
        else:
            ideal_length = 1000
        
        length_score = min(response_length / ideal_length, 1.0)
        
        # LLM 기반 평가 (있는 경우)
        if self.llm_client:
            try:
                llm_score = await self._llm_evaluate(example.query, response)
                response_quality = (length_score + llm_score) / 2
            except:
                response_quality = length_score
        else:
            response_quality = length_score
        
        # 종합 점수 (0-5)
        score = (
            skill_match * 2.0 +           # 스킬 매칭 40%
            (1.0 if mode_match else 0.5) * 1.0 +  # 모드 매칭 20%
            response_quality * 2.0         # 응답 품질 40%
        )
        
        # 피드백 생성
        feedback = self._generate_feedback(skill_match, mode_match, response_quality)
        
        return EvaluationResult(
            example_id=example.id,
            score=score,
            response_quality=response_quality,
            skill_match=skill_match,
            mode_match=mode_match,
            execution_time_ms=execution_time_ms,
            response_preview=response[:200],
            feedback=feedback,
        )
    
    async def _llm_evaluate(self, query: str, response: str) -> float:
        """LLM 기반 평가 (0-1)"""
        # 간단한 휴리스틱 (실제로는 LLM 호출)
        # 응답에 코드나 예시가 있으면 높은 점수
        has_code = "```" in response
        has_example = "예" in response or "example" in response.lower()
        has_list = "- " in response or "1." in response
        
        score = 0.5
        if has_code:
            score += 0.2
        if has_example:
            score += 0.15
        if has_list:
            score += 0.15
        
        return min(score, 1.0)
    
    def _generate_feedback(
        self,
        skill_match: float,
        mode_match: bool,
        response_quality: float,
    ) -> str:
        """피드백 텍스트 생성"""
        parts = []
        
        if skill_match < 0.5:
            parts.append("스킬 매칭 개선 필요")
        elif skill_match >= 0.8:
            parts.append("스킬 매칭 우수")
        
        if not mode_match:
            parts.append("실행 모드 조정 권장")
        
        if response_quality < 0.5:
            parts.append("응답 품질 개선 필요")
        elif response_quality >= 0.8:
            parts.append("응답 품질 우수")
        
        return " | ".join(parts) if parts else "적정 수준"


class TrainingPersistence:
    """
    훈련 데이터 영구 저장 (SQLite)
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path.home() / ".haes" / "training.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """DB 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 훈련 세션 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_sessions (
                id TEXT PRIMARY KEY,
                started_at TEXT,
                completed_at TEXT,
                total_examples INTEGER,
                evaluated INTEGER,
                success_count INTEGER,
                average_score REAL,
                patterns_learned INTEGER,
                status TEXT
            )
        """)
        
        # 평가 결과 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                example_id TEXT,
                query TEXT,
                score REAL,
                response_quality REAL,
                skill_match REAL,
                mode_match INTEGER,
                execution_time_ms REAL,
                response_preview TEXT,
                feedback TEXT,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES training_sessions(id)
            )
        """)
        
        # 학습된 패턴 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                pattern_key TEXT,
                skills TEXT,
                mode TEXT,
                keywords TEXT,
                success_rate REAL,
                sample_count INTEGER,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES training_sessions(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_session(self, session: TrainingSession):
        """세션 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO training_sessions
            (id, started_at, completed_at, total_examples, evaluated,
             success_count, average_score, patterns_learned, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.id,
            session.started_at,
            session.completed_at,
            session.total_examples,
            session.evaluated,
            session.success_count,
            session.average_score,
            session.patterns_learned,
            session.status,
        ))
        
        conn.commit()
        conn.close()
    
    def save_evaluation(self, session_id: str, result: EvaluationResult, query: str):
        """평가 결과 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO evaluation_results
            (session_id, example_id, query, score, response_quality,
             skill_match, mode_match, execution_time_ms, response_preview,
             feedback, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            result.example_id,
            query,
            result.score,
            result.response_quality,
            result.skill_match,
            1 if result.mode_match else 0,
            result.execution_time_ms,
            result.response_preview,
            result.feedback,
            datetime.now().isoformat(),
        ))
        
        conn.commit()
        conn.close()
    
    def save_pattern(self, session_id: str, pattern: Dict[str, Any]):
        """패턴 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO learned_patterns
            (session_id, pattern_key, skills, mode, keywords,
             success_rate, sample_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            pattern.get("pattern_key", ""),
            json.dumps(pattern.get("skills", [])),
            pattern.get("mode", ""),
            json.dumps(list(pattern.get("keywords", []))),
            pattern.get("success_rate", 0.0),
            pattern.get("sample_count", 0),
            datetime.now().isoformat(),
        ))
        
        conn.commit()
        conn.close()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """훈련 통계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM training_sessions")
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM evaluation_results")
        total_evaluations = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(score) FROM evaluation_results")
        avg_score = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT COUNT(*) FROM learned_patterns")
        total_patterns = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_sessions": total_sessions,
            "total_evaluations": total_evaluations,
            "average_score": round(avg_score, 2),
            "total_patterns": total_patterns,
        }


class SandboxTrainer:
    """
    샌드박스 기반 자동 훈련기
    
    사용 예시:
        trainer = SandboxTrainer(haes_api_url="http://localhost:8080")
        
        # 훈련 실행 (50개 예제)
        session = await trainer.train(num_examples=50)
        
        # 결과 확인
        print(f"평균 점수: {session.average_score:.2f}")
        print(f"학습된 패턴: {session.patterns_learned}")
    """
    
    def __init__(
        self,
        haes_api_url: str = "http://localhost:8080",
        llm_client: Optional[Any] = None,
    ):
        self.api_url = haes_api_url
        self.data_generator = SyntheticDataGenerator()
        self.evaluator = AutoEvaluator(llm_client)
        self.persistence = TrainingPersistence()
        self._session: Optional[TrainingSession] = None
    
    async def train(
        self,
        num_examples: int = 50,
        difficulty: Optional[str] = None,
        category: Optional[str] = None,
    ) -> TrainingSession:
        """
        훈련 실행
        
        Args:
            num_examples: 훈련 예제 수
            difficulty: 난이도 필터 (easy, medium, hard)
            category: 카테고리 필터
        
        Returns:
            TrainingSession
        """
        import aiohttp
        
        # 세션 생성
        session_id = f"train-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self._session = TrainingSession(
            id=session_id,
            started_at=datetime.now().isoformat(),
            total_examples=num_examples,
        )
        
        logger.info(f"Training session started: {session_id}")
        
        # 예제 생성
        examples = self.data_generator.generate_examples(num_examples)
        
        # 필터 적용
        if difficulty:
            examples = [e for e in examples if e.difficulty == difficulty]
        if category:
            examples = [e for e in examples if e.category == category]
        
        self._session.total_examples = len(examples)
        
        # 훈련 실행
        scores = []
        success_count = 0
        
        async with aiohttp.ClientSession() as http:
            for i, example in enumerate(examples):
                try:
                    # HAES API 호출
                    start_time = datetime.now()
                    
                    async with http.post(
                        f"{self.api_url}/api/chat",
                        json={"query": example.query},
                        timeout=aiohttp.ClientTimeout(total=120),
                    ) as resp:
                        if resp.status != 200:
                            logger.warning(f"API error for {example.id}: {resp.status}")
                            continue
                        
                        data = await resp.json()
                    
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    # 평가
                    result = await self.evaluator.evaluate(
                        example=example,
                        response=data.get("response", ""),
                        skills_used=data.get("skills_used", []),
                        mode_used=data.get("mode", ""),
                        execution_time_ms=execution_time,
                    )
                    
                    # 저장
                    self.persistence.save_evaluation(session_id, result, example.query)
                    
                    scores.append(result.score)
                    if result.score >= 4.0:
                        success_count += 1
                    
                    self._session.evaluated += 1
                    
                    # 진행 상황 로깅
                    if (i + 1) % 10 == 0:
                        logger.info(f"Progress: {i+1}/{len(examples)} | Avg Score: {sum(scores)/len(scores):.2f}")
                    
                    # 피드백을 Evolution Engine에 전달
                    await self._send_feedback_to_evolution(
                        http, example, result, data
                    )
                    
                except Exception as e:
                    logger.error(f"Training error for {example.id}: {e}")
                    continue
        
        # 세션 완료
        self._session.completed_at = datetime.now().isoformat()
        self._session.success_count = success_count
        self._session.average_score = sum(scores) / len(scores) if scores else 0.0
        self._session.status = "completed"
        
        # 학습된 패턴 수 확인
        patterns = await self._get_learned_patterns_count()
        self._session.patterns_learned = patterns
        
        # 저장
        self.persistence.save_session(self._session)
        
        logger.info(
            f"Training completed: {session_id} | "
            f"Score: {self._session.average_score:.2f} | "
            f"Success: {success_count}/{len(examples)} | "
            f"Patterns: {patterns}"
        )
        
        return self._session
    
    async def _send_feedback_to_evolution(
        self,
        http: Any,
        example: TrainingExample,
        result: EvaluationResult,
        response_data: Dict[str, Any],
    ):
        """Evolution Engine에 피드백 전송"""
        try:
            # 점수를 1-5 정수로 변환
            score = min(5, max(1, round(result.score)))
            
            await http.post(
                f"{self.api_url}/api/feedback",
                json={
                    "score": score,
                    "comment": result.feedback,
                },
                timeout=aiohttp.ClientTimeout(total=10),
            )
        except:
            pass  # 피드백 실패는 무시
    
    async def _get_learned_patterns_count(self) -> int:
        """학습된 패턴 수 조회"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as http:
                async with http.get(
                    f"{self.api_url}/api/evolution/stats",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("learned_patterns_count", 0)
        except:
            pass
        
        return 0
    
    def get_training_stats(self) -> Dict[str, Any]:
        """훈련 통계 조회"""
        return self.persistence.get_session_stats()


# 편의 함수
async def run_training(
    num_examples: int = 50,
    api_url: str = "http://localhost:8080",
) -> TrainingSession:
    """
    HAES 시스템 훈련 실행
    
    Args:
        num_examples: 훈련 예제 수
        api_url: HAES API URL
    
    Returns:
        TrainingSession
    """
    trainer = SandboxTrainer(haes_api_url=api_url)
    return await trainer.train(num_examples=num_examples)


# 간단한 테스트
if __name__ == "__main__":
    async def test():
        print("=" * 60)
        print("HAES 자동 훈련 시스템 테스트")
        print("=" * 60)
        
        # 데이터 생성기 테스트
        generator = SyntheticDataGenerator()
        examples = generator.generate_examples(10)
        
        print(f"\n생성된 훈련 예제: {len(examples)}개")
        for ex in examples[:3]:
            print(f"  - {ex.query[:50]}...")
            print(f"    Skills: {ex.expected_skills}, Mode: {ex.expected_mode}")
        
        # 저장소 테스트
        persistence = TrainingPersistence()
        stats = persistence.get_session_stats()
        print(f"\n훈련 통계: {stats}")
        
        print("\n✅ 테스트 완료!")
    
    asyncio.run(test())
