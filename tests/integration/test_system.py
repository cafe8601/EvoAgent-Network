"""
HybridAISystem Integration Tests
"""

import pytest
from pathlib import Path


class TestHybridAISystemIntegration:
    """HybridAISystem 통합 테스트"""

    @pytest.mark.asyncio
    async def test_init_and_initialize(self, sample_skills_path, sample_agents_path, tmp_path):
        """시스템 초기화 테스트"""
        from haes.system import HybridAISystem
        from haes.config import Config

        config = Config(
            skills_path=sample_skills_path,
            agents_path=sample_agents_path,
            persist_dir=tmp_path / "vectordb",
        )

        system = HybridAISystem(config=config)
        stats = system.initialize()

        assert stats["skills_indexed"] == 3
        assert stats["agents_loaded"] >= 3

    @pytest.mark.asyncio
    async def test_chat_skill_only(self, sample_skills_path, sample_agents_path, tmp_path):
        """SKILL_ONLY 모드 채팅 테스트"""
        from haes.system import HybridAISystem
        from haes.config import Config

        config = Config(
            skills_path=sample_skills_path,
            agents_path=sample_agents_path,
            persist_dir=tmp_path / "vectordb",
        )

        system = HybridAISystem(config=config)
        system.initialize()

        result = await system.chat("LoRA가 뭐야?")

        assert result.mode == "skill_only"
        assert result.response is not None
        assert result.execution_time > 0

    @pytest.mark.asyncio
    async def test_chat_includes_skills(self, sample_skills_path, sample_agents_path, tmp_path):
        """채팅 결과에 SKILL 포함 확인"""
        from haes.system import HybridAISystem
        from haes.config import Config

        config = Config(
            skills_path=sample_skills_path,
            agents_path=sample_agents_path,
            persist_dir=tmp_path / "vectordb",
        )

        system = HybridAISystem(config=config)
        system.initialize()

        result = await system.chat("파인튜닝 방법")

        # fine-tuning 관련 SKILL이 포함되어야 함
        assert len(result.skills_used) > 0

    @pytest.mark.asyncio
    async def test_feedback_recording(self, sample_skills_path, sample_agents_path, tmp_path):
        """피드백 기록 테스트"""
        from haes.system import HybridAISystem
        from haes.config import Config

        config = Config(
            skills_path=sample_skills_path,
            agents_path=sample_agents_path,
            persist_dir=tmp_path / "vectordb",
        )

        system = HybridAISystem(config=config)
        system.initialize()

        await system.chat("RAG 시스템 만들어줘")
        feedback = system.feedback(score=5, comment="좋은 답변!")

        assert feedback.score == 5
        assert feedback.comment == "좋은 답변!"

    @pytest.mark.asyncio
    async def test_history_tracking(self, sample_skills_path, sample_agents_path, tmp_path):
        """대화 히스토리 추적 테스트"""
        from haes.system import HybridAISystem
        from haes.config import Config

        config = Config(
            skills_path=sample_skills_path,
            agents_path=sample_agents_path,
            persist_dir=tmp_path / "vectordb",
        )

        system = HybridAISystem(config=config)
        system.initialize()

        await system.chat("질문 1")
        await system.chat("질문 2")

        assert len(system.history) == 4  # 2 질문 + 2 응답

    @pytest.mark.asyncio
    async def test_get_stats(self, sample_skills_path, sample_agents_path, tmp_path):
        """시스템 통계 조회 테스트"""
        from haes.system import HybridAISystem
        from haes.config import Config

        config = Config(
            skills_path=sample_skills_path,
            agents_path=sample_agents_path,
            persist_dir=tmp_path / "vectordb",
        )

        system = HybridAISystem(config=config)
        system.initialize()

        stats = system.get_stats()

        assert "skill_store" in stats
        assert "agent_pool" in stats
        assert "feedback" in stats

    @pytest.mark.asyncio
    async def test_compressed_index(self, sample_skills_path, sample_agents_path, tmp_path):
        """압축 인덱스 조회 테스트"""
        from haes.system import HybridAISystem
        from haes.config import Config

        config = Config(
            skills_path=sample_skills_path,
            agents_path=sample_agents_path,
            persist_dir=tmp_path / "vectordb",
        )

        system = HybridAISystem(config=config)
        system.initialize()

        index = system.get_compressed_index()

        assert isinstance(index, str)
        assert "sample-fine-tuning" in index
