"""
HybridRouter Unit Tests
"""

import pytest
from haes.models.routing import ExecutionMode


class TestHybridRouter:
    """HybridRouter 단위 테스트"""

    @pytest.mark.asyncio
    async def test_simple_query_routes_skill_only(self, sample_skills_path, tmp_path):
        """단순 질문은 SKILL_ONLY"""
        from haes.router.hybrid_router import HybridRouter
        from haes.stores.skill_store import SkillStore

        skill_store = SkillStore(str(sample_skills_path), str(tmp_path / "vectordb"))
        skill_store.index_all_skills()

        router = HybridRouter(skill_store=skill_store)
        decision = await router.route("LoRA가 뭐야?")

        assert decision.mode == ExecutionMode.SKILL_ONLY
        assert len(decision.skills) > 0

    @pytest.mark.asyncio
    async def test_technical_query_routes_skill_agent(self, sample_skills_path, tmp_path):
        """기술적 구현 요청은 SKILL_AGENT"""
        from haes.router.hybrid_router import HybridRouter
        from haes.stores.skill_store import SkillStore

        skill_store = SkillStore(str(sample_skills_path), str(tmp_path / "vectordb"))
        skill_store.index_all_skills()

        router = HybridRouter(skill_store=skill_store)
        # 구현 키워드 명확히 추가
        decision = await router.route("vLLM으로 70B 모델 서빙 구현하고 설정해줘")

        # SKILL_AGENT 또는 그 이상
        assert decision.mode in [
            ExecutionMode.SKILL_AGENT,
            ExecutionMode.MULTI_AGENT,
            ExecutionMode.PARALLEL,
        ]

    @pytest.mark.asyncio
    async def test_multiple_tasks_routes_parallel(self, sample_skills_path, tmp_path):
        """복수 독립 작업은 PARALLEL"""
        from haes.router.hybrid_router import HybridRouter
        from haes.stores.skill_store import SkillStore

        skill_store = SkillStore(str(sample_skills_path), str(tmp_path / "vectordb"))
        skill_store.index_all_skills()

        router = HybridRouter(skill_store=skill_store)
        # "하고" 정확히 2번 사용 = 3개 작업
        decision = await router.route(
            "API 만들어 하고 테스트 작성 하고 문서화도 해"
        )

        assert decision.mode == ExecutionMode.PARALLEL

    @pytest.mark.asyncio
    async def test_collaboration_routes_multi_agent(self, sample_skills_path, tmp_path):
        """협업 필요 시 MULTI_AGENT"""
        from haes.router.hybrid_router import HybridRouter
        from haes.stores.skill_store import SkillStore

        skill_store = SkillStore(str(sample_skills_path), str(tmp_path / "vectordb"))
        skill_store.index_all_skills()

        router = HybridRouter(skill_store=skill_store)
        decision = await router.route(
            "시스템 설계하고 보안 검토해줘"
        )

        assert decision.mode == ExecutionMode.MULTI_AGENT

    @pytest.mark.asyncio
    async def test_decision_includes_skills(self, sample_skills_path, tmp_path):
        """결정에 SKILL ID 포함"""
        from haes.router.hybrid_router import HybridRouter
        from haes.stores.skill_store import SkillStore

        skill_store = SkillStore(str(sample_skills_path), str(tmp_path / "vectordb"))
        skill_store.index_all_skills()

        router = HybridRouter(skill_store=skill_store)
        decision = await router.route("파인튜닝 방법 알려줘")

        assert len(decision.skills) > 0

    @pytest.mark.asyncio
    async def test_decision_has_confidence(self, sample_skills_path, tmp_path):
        """결정에 신뢰도 포함"""
        from haes.router.hybrid_router import HybridRouter
        from haes.stores.skill_store import SkillStore

        skill_store = SkillStore(str(sample_skills_path), str(tmp_path / "vectordb"))
        skill_store.index_all_skills()

        router = HybridRouter(skill_store=skill_store)
        decision = await router.route("테스트 쿼리")

        assert 0 <= decision.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_decision_has_reason(self, sample_skills_path, tmp_path):
        """결정에 이유 포함"""
        from haes.router.hybrid_router import HybridRouter
        from haes.stores.skill_store import SkillStore

        skill_store = SkillStore(str(sample_skills_path), str(tmp_path / "vectordb"))
        skill_store.index_all_skills()

        router = HybridRouter(skill_store=skill_store)
        decision = await router.route("LoRA 파인튜닝")

        assert decision.reason != ""

    @pytest.mark.asyncio
    async def test_analyze_complexity(self, sample_skills_path, tmp_path):
        """복잡도 분석 테스트"""
        from haes.router.hybrid_router import HybridRouter
        from haes.stores.skill_store import SkillStore

        skill_store = SkillStore(str(sample_skills_path), str(tmp_path / "vectordb"))
        skill_store.index_all_skills()

        router = HybridRouter(skill_store=skill_store)

        # 단순 질문
        simple = router._analyze_complexity("LoRA가 뭐야?")
        assert simple.score < 0.3

        # 복잡한 작업 - 더 명확하게
        complex_q = router._analyze_complexity(
            "시스템 설계하고 구현하고 테스트하고 배포까지 해줘"
        )
        # 구현(0.35) + 병렬 3회(0.65) = 1.0
        assert complex_q.score >= 0.5
