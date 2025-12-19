"""
EvolutionEngine Unit Tests

피드백 기반 학습 및 진화 엔진 테스트
영속성 기능 테스트 포함
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from haes.models.execution import ExecutionResult
from haes.models.feedback import Feedback, LearnedPattern


class TestEvolutionEngine:
    """EvolutionEngine 단위 테스트"""

    @pytest.fixture(autouse=True)
    def setup_isolated_engine(self, tmp_path):
        """각 테스트에 격리된 엔진 생성"""
        self.test_dir = tmp_path / "evolution_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def _create_engine(self):
        """격리된 EvolutionEngine 인스턴스 생성"""
        from haes.evolution.evolution_engine import EvolutionEngine
        engine = EvolutionEngine(persist_dir=str(self.test_dir), auto_load=False)
        engine.set_auto_save(False)  # 테스트 격리를 위해 자동 저장 비활성화
        return engine

    def test_init_creates_empty_stores(self):
        """초기화 시 빈 저장소 생성"""
        engine = self._create_engine()

        assert len(engine.feedback_db) == 0
        assert len(engine.routing_stats) == 0
        assert len(engine.learned_patterns) == 0

    def test_record_feedback_stores_entry(self):
        """피드백 기록"""
        engine = self._create_engine()

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
        engine = self._create_engine()

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
        engine = self._create_engine()

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
        engine = self._create_engine()

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
        engine = self._create_engine()

        hints = engine.get_routing_hints("any query")

        assert hints["confidence"] == 0.0
        assert hints["suggested_skills"] == []

    def test_get_routing_hints_uses_learned_patterns(self):
        """학습된 패턴 기반 힌트 반환"""
        engine = self._create_engine()

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
        engine = self._create_engine()

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
        engine = self._create_engine()

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
        engine = self._create_engine()

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
        engine = self._create_engine()

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
        engine = self._create_engine()

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
        engine = self._create_engine()

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


class TestEvolutionEnginePersistence:
    """EvolutionEngine 영속성 테스트"""

    def test_save_and_load_json(self, tmp_path):
        """JSON 저장 및 로드"""
        from haes.evolution.evolution_engine import EvolutionEngine

        persist_dir = tmp_path / "evolution"
        engine = EvolutionEngine(persist_dir=str(persist_dir), auto_load=False)

        # 데이터 추가
        result = ExecutionResult(
            mode="skill_only",
            response="Test response",
            skills_used=["test-skill"],
            agents_used=[],
            query="test query",
        )
        engine.set_auto_save(False)  # 수동 저장 모드
        engine.record_feedback(result=result, feedback="good", score=5)

        # 저장
        assert engine.save() is True

        # 파일 존재 확인
        assert (persist_dir / "evolution_state.json").exists()

        # 새 엔진에서 로드
        engine2 = EvolutionEngine(persist_dir=str(persist_dir), auto_load=True)

        assert len(engine2.feedback_db) == 1
        assert engine2.feedback_db[0]["score"] == 5

    def test_save_creates_directory(self, tmp_path):
        """저장 시 디렉토리 자동 생성"""
        from haes.evolution.evolution_engine import EvolutionEngine

        persist_dir = tmp_path / "nested" / "path" / "evolution"
        engine = EvolutionEngine(persist_dir=str(persist_dir), auto_load=False)

        assert persist_dir.exists()

    def test_load_missing_file_returns_false(self, tmp_path):
        """파일 없을 때 False 반환"""
        from haes.evolution.evolution_engine import EvolutionEngine

        persist_dir = tmp_path / "empty"
        engine = EvolutionEngine(persist_dir=str(persist_dir), auto_load=False)

        assert engine.load() is False

    def test_serialize_deserialize_patterns(self, tmp_path):
        """패턴 직렬화/역직렬화 (set ↔ list 변환)"""
        from haes.evolution.evolution_engine import EvolutionEngine

        persist_dir = tmp_path / "evolution"
        engine = EvolutionEngine(persist_dir=str(persist_dir), auto_load=False)
        engine.set_auto_save(False)

        # 학습 패턴 생성 (5회 성공 필요)
        for i in range(5):
            result = ExecutionResult(
                mode="skill_only",
                response=f"Response {i}",
                skills_used=["pattern-skill"],
                agents_used=[],
                query="패턴 테스트 쿼리",
            )
            engine.record_feedback(result=result, feedback="good", score=5)

        assert len(engine.learned_patterns) > 0

        # 저장
        engine.save()

        # 새 엔진에서 로드
        engine2 = EvolutionEngine(persist_dir=str(persist_dir), auto_load=True)

        # 패턴 복원 확인
        assert len(engine2.learned_patterns) > 0
        pattern = engine2.learned_patterns[0]
        assert isinstance(pattern["query_keywords"], set)  # set으로 복원됨

    def test_backup_creates_timestamped_file(self, tmp_path):
        """백업 시 타임스탬프 파일 생성"""
        from haes.evolution.evolution_engine import EvolutionEngine

        persist_dir = tmp_path / "evolution"
        engine = EvolutionEngine(persist_dir=str(persist_dir), auto_load=False)

        result = ExecutionResult(
            mode="skill_only",
            response="response",
            skills_used=["skill"],
            agents_used=[],
            query="query",
        )
        engine.set_auto_save(False)
        engine.record_feedback(result=result, feedback="", score=5)

        # 백업
        backup_file = engine.backup()

        assert backup_file is not None
        assert backup_file.exists()
        assert "evolution_state_" in backup_file.name

    def test_restore_from_backup(self, tmp_path):
        """백업에서 복원"""
        from haes.evolution.evolution_engine import EvolutionEngine

        persist_dir = tmp_path / "evolution"
        engine = EvolutionEngine(persist_dir=str(persist_dir), auto_load=False)
        engine.set_auto_save(False)

        # 데이터 추가
        result = ExecutionResult(
            mode="skill_only",
            response="response",
            skills_used=["backup-skill"],
            agents_used=[],
            query="backup query",
        )
        engine.record_feedback(result=result, feedback="", score=5)

        # 백업
        backup_file = engine.backup()

        # 데이터 변경
        engine.clear()
        assert len(engine.feedback_db) == 0

        # 백업에서 복원
        assert engine.restore_from_backup(backup_file) is True
        assert len(engine.feedback_db) == 1
        assert engine.feedback_db[0]["skills_used"] == ["backup-skill"]

    def test_auto_save_mode(self, tmp_path):
        """자동 저장 모드"""
        from haes.evolution.evolution_engine import EvolutionEngine

        persist_dir = tmp_path / "evolution"
        engine = EvolutionEngine(persist_dir=str(persist_dir), auto_load=False)
        engine.set_auto_save(True)  # 자동 저장 활성화

        result = ExecutionResult(
            mode="skill_only",
            response="response",
            skills_used=["auto-save-skill"],
            agents_used=[],
            query="query",
        )
        engine.record_feedback(result=result, feedback="", score=5)

        # 파일 자동 생성됨
        assert (persist_dir / "evolution_state.json").exists()

    def test_is_dirty_flag(self, tmp_path):
        """변경 추적 플래그"""
        from haes.evolution.evolution_engine import EvolutionEngine

        persist_dir = tmp_path / "evolution"
        engine = EvolutionEngine(persist_dir=str(persist_dir), auto_load=False)
        engine.set_auto_save(False)

        assert engine.is_dirty() is False

        result = ExecutionResult(
            mode="skill_only",
            response="response",
            skills_used=["skill"],
            agents_used=[],
            query="query",
        )
        engine.record_feedback(result=result, feedback="", score=5)

        assert engine.is_dirty() is True

        engine.save()
        assert engine.is_dirty() is False

    def test_version_in_saved_data(self, tmp_path):
        """저장된 데이터에 버전 포함"""
        from haes.evolution.evolution_engine import EvolutionEngine

        persist_dir = tmp_path / "evolution"
        engine = EvolutionEngine(persist_dir=str(persist_dir), auto_load=False)
        engine.save()

        # 파일 직접 읽기
        with open(persist_dir / "evolution_state.json", "r") as f:
            data = json.load(f)

        assert "version" in data
        assert data["version"] == "1.0"
        assert "saved_at" in data
        assert "stats" in data
