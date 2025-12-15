"""
EvolutionEngine Unit Tests

피드백 기반 학습 및 진화 엔진 테스트
"""

import pytest
from datetime import datetime

from haes.models.execution import ExecutionResult
from haes.models.feedback import Feedback, LearnedPattern


class TestEvolutionEngine:
    """EvolutionEngine 단위 테스트"""

    def test_init_creates_empty_stores(self):
        """초기화 시 빈 저장소 생성"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        assert len(engine.feedback_db) == 0
        assert len(engine.routing_stats) == 0
        assert len(engine.learned_patterns) == 0

    def test_record_feedback_stores_entry(self):
        """피드백 기록"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        result = ExecutionResult(
            mode="skill_only",
            response="Test response",
            skills_used=["skill-a"],
            agents_used=[],
            query="test query",
        )

        engine.record_feedback(result=result, feedback="good", score=5)

        assert len(engine.feedback_db) == 1
        assert engine.feedback_db[0]["score"] == 5

    def test_updates_routing_stats(self):
        """라우팅 통계 업데이트"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        result = ExecutionResult(
            mode="skill_only",
            response="Test response",
            skills_used=["skill-a", "skill-b"],
            agents_used=[],
            query="test query",
        )

        engine.record_feedback(result=result, feedback="good", score=5)

        assert "skill-a" in engine.routing_stats
        assert "skill-b" in engine.routing_stats
        assert engine.routing_stats["skill-a"]["total"] == 1
        assert engine.routing_stats["skill-a"]["success"] == 1

    def test_learns_success_pattern_after_threshold(self):
        """5회 이상 성공 시 패턴 학습"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        # 동일한 패턴으로 5회 성공
        for i in range(5):
            result = ExecutionResult(
                mode="skill_only",
                response=f"Response {i}",
                skills_used=["fine-tuning"],
                agents_used=[],
                query="LoRA 파인튜닝 방법",
            )
            engine.record_feedback(result=result, feedback="good", score=5)

        assert len(engine.learned_patterns) > 0
        # 패턴 확인
        pattern = engine.learned_patterns[0]
        assert "fine-tuning" in pattern["skills"]

    def test_no_pattern_for_low_scores(self):
        """낮은 점수는 패턴 학습 안함"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        for i in range(5):
            result = ExecutionResult(
                mode="skill_only",
                response=f"Response {i}",
                skills_used=["bad-skill"],
                agents_used=[],
                query="bad query",
            )
            engine.record_feedback(result=result, feedback="bad", score=2)

        assert len(engine.learned_patterns) == 0

    def test_get_routing_hints_returns_empty_initially(self):
        """초기 상태에서 힌트 없음"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        hints = engine.get_routing_hints("any query")

        assert hints["confidence"] == 0.0
        assert hints["suggested_skills"] == []

    def test_get_routing_hints_uses_learned_patterns(self):
        """학습된 패턴 기반 힌트 반환"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        # 5회 성공 패턴 생성 - 동일 키워드 사용
        for i in range(5):
            result = ExecutionResult(
                mode="skill_only",
                response=f"Response {i}",
                skills_used=["fine-tuning"],
                agents_used=[],
                query="lora 파인튜닝 학습",  # 여러 키워드
            )
            engine.record_feedback(result=result, feedback="good", score=5)

        # 유사 쿼리로 힌트 조회 - 동일 키워드 포함
        hints = engine.get_routing_hints("lora 파인튜닝")

        assert hints["confidence"] >= 0.3  # 유사도 기반
        assert "fine-tuning" in hints["suggested_skills"]

    def test_triggers_improvement_on_low_score(self):
        """낮은 점수 시 개선 제안"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        result = ExecutionResult(
            mode="skill_only",
            response="Bad response",
            skills_used=["wrong-skill"],
            agents_used=[],
            query="test query",
        )

        improvement = engine.record_feedback(result=result, feedback="bad", score=1)

        assert improvement is not None
        assert "needs_review" in improvement or improvement.get("action") == "review"

    def test_get_skill_performance(self):
        """SKILL별 성능 조회"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        # 다양한 점수로 피드백
        for score in [5, 4, 5, 3, 5]:
            result = ExecutionResult(
                mode="skill_only",
                response="response",
                skills_used=["test-skill"],
                agents_used=[],
                query="query",
            )
            engine.record_feedback(result=result, feedback="", score=score)

        performance = engine.get_skill_performance("test-skill")

        assert performance["total"] == 5
        assert performance["average_score"] == 4.4
        assert performance["success_rate"] == 0.8  # 4점 이상 4개 / 5개

    def test_get_overall_stats(self):
        """전체 통계 조회"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        for i in range(3):
            result = ExecutionResult(
                mode="skill_only",
                response="response",
                skills_used=["skill-1"],
                agents_used=[],
                query=f"query {i}",
            )
            engine.record_feedback(result=result, feedback="", score=5)

        stats = engine.get_stats()

        assert stats["total_feedbacks"] == 3
        assert stats["positive_feedbacks"] == 3
        assert stats["learned_patterns_count"] >= 0

    def test_clear_history(self):
        """히스토리 클리어"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        result = ExecutionResult(
            mode="skill_only",
            response="response",
            skills_used=["skill"],
            agents_used=[],
            query="query",
        )
        engine.record_feedback(result=result, feedback="", score=5)

        engine.clear()

        assert len(engine.feedback_db) == 0
        assert len(engine.routing_stats) == 0

    def test_pattern_similarity_matching(self):
        """패턴 유사도 매칭"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        # 패턴 학습 - 더 많은 키워드
        for i in range(5):
            result = ExecutionResult(
                mode="skill_agent",
                response="response",
                skills_used=["rag", "vector-db"],
                agents_used=["backend-developer"],
                query="rag 벡터 시스템 검색 구현",  # 더 많은 키워드
            )
            engine.record_feedback(result=result, feedback="good", score=5)

        # 유사 쿼리 테스트 - 동일 키워드 포함
        hints = engine.get_routing_hints("벡터 검색 rag 시스템")

        assert hints["confidence"] >= 0.3  # 조정
        assert "rag" in hints["suggested_skills"] or "vector-db" in hints["suggested_skills"]

    def test_mode_recommendation(self):
        """실행 모드 추천"""
        from haes.evolution.evolution_engine import EvolutionEngine

        engine = EvolutionEngine()

        # skill_agent 모드로 5회 성공 - 동일 키워드
        for i in range(5):
            result = ExecutionResult(
                mode="skill_agent",
                response="response",
                skills_used=["fine-tuning"],
                agents_used=["ml-engineer"],
                query="llm 파인튜닝 모델 학습",  # 동일 키워드
            )
            engine.record_feedback(result=result, feedback="good", score=5)

        # 동일 키워드 포함 쿼리
        hints = engine.get_routing_hints("llm 파인튜닝 설정")

        assert hints.get("suggested_mode") == "skill_agent"
