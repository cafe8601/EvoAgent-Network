"""
AgentPool Unit Tests

TDD: RED Phase - Write tests first
"""

import pytest
from pathlib import Path

from haes.models.agent import Agent


class TestAgentPool:
    """AgentPool 단위 테스트"""

    def test_init_creates_empty_agents_dict(self, tmp_path: Path):
        """초기화 시 빈 에이전트 딕셔너리가 생성되어야 함"""
        from haes.stores.agent_pool import AgentPool

        agents_path = tmp_path / "agents"
        agents_path.mkdir()

        pool = AgentPool(agents_path=str(agents_path))

        assert pool.agents == {}

    def test_loads_tier1_agents(self, sample_agents_path: Path):
        """Tier1 에이전트가 로드되어야 함"""
        from haes.stores.agent_pool import AgentPool

        pool = AgentPool(agents_path=str(sample_agents_path))
        pool.load_all_agents()

        agents = pool.list_by_tier("tier1-core")
        assert len(agents) >= 2  # test-backend-developer, test-qa-expert

    def test_loads_tier2_agents(self, sample_agents_path: Path):
        """Tier2 에이전트가 로드되어야 함"""
        from haes.stores.agent_pool import AgentPool

        pool = AgentPool(agents_path=str(sample_agents_path))
        pool.load_all_agents()

        agents = pool.list_by_tier("tier2-specialized")
        assert len(agents) >= 1  # test-rust-developer

    def test_get_returns_agent_by_id(self, sample_agents_path: Path):
        """에이전트 ID로 조회해야 함"""
        from haes.stores.agent_pool import AgentPool

        pool = AgentPool(agents_path=str(sample_agents_path))
        pool.load_all_agents()

        agent = pool.get("test-backend-developer")

        assert agent is not None
        assert agent.agent_id == "test-backend-developer"
        assert agent.tier == "tier1-core"

    def test_get_returns_none_for_unknown(self, sample_agents_path: Path):
        """없는 에이전트는 None 반환"""
        from haes.stores.agent_pool import AgentPool

        pool = AgentPool(agents_path=str(sample_agents_path))
        pool.load_all_agents()

        agent = pool.get("nonexistent-agent")

        assert agent is None

    def test_loads_all_tiers(self, sample_agents_path: Path):
        """모든 Tier에서 에이전트 로드"""
        from haes.stores.agent_pool import AgentPool

        pool = AgentPool(agents_path=str(sample_agents_path))
        pool.load_all_agents()

        all_agents = pool.list_all()
        assert len(all_agents) >= 3  # tier1 2개 + tier2 1개

    def test_parses_yaml_frontmatter(self, sample_agents_path: Path):
        """YAML frontmatter를 올바르게 파싱해야 함"""
        from haes.stores.agent_pool import AgentPool

        pool = AgentPool(agents_path=str(sample_agents_path))
        pool.load_all_agents()

        agent = pool.get("test-backend-developer")

        assert agent is not None
        assert agent.version == "1.0"
        assert agent.standalone is True
        assert "API development" in agent.system_prompt

    def test_list_by_tier_filters_correctly(self, sample_agents_path: Path):
        """Tier별 에이전트 필터링이 정확해야 함"""
        from haes.stores.agent_pool import AgentPool

        pool = AgentPool(agents_path=str(sample_agents_path))
        pool.load_all_agents()

        tier1 = pool.list_by_tier("tier1-core")
        tier2 = pool.list_by_tier("tier2-specialized")

        tier1_ids = [a.agent_id for a in tier1]
        tier2_ids = [a.agent_id for a in tier2]

        assert "test-backend-developer" in tier1_ids
        assert "test-rust-developer" in tier2_ids
        assert "test-rust-developer" not in tier1_ids

    def test_get_agent_count(self, sample_agents_path: Path):
        """에이전트 총 개수 반환"""
        from haes.stores.agent_pool import AgentPool

        pool = AgentPool(agents_path=str(sample_agents_path))
        pool.load_all_agents()

        count = pool.get_count()

        assert count >= 3

    def test_select_for_task_returns_agent(self, sample_agents_path: Path):
        """작업에 적합한 에이전트 선택"""
        from haes.stores.agent_pool import AgentPool

        pool = AgentPool(agents_path=str(sample_agents_path))
        pool.load_all_agents()

        agent_id = pool.select_for_task("API development and testing")

        assert agent_id is not None
        # backend-developer 또는 qa-expert 중 하나
        assert agent_id in ["test-backend-developer", "test-qa-expert"]
