"""
HAES Test Configuration

pytest 픽스처 및 공통 테스트 유틸리티
"""

import pytest
from pathlib import Path
from typing import Generator

from haes.config import Config
from haes.models.skill import Skill
from haes.models.agent import Agent
from haes.models.execution import ExecutionResult
from haes.models.feedback import Feedback


# ============================================================
# Path Fixtures
# ============================================================

@pytest.fixture
def fixtures_path() -> Path:
    """테스트 픽스처 경로"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_skills_path(fixtures_path: Path) -> Path:
    """샘플 SKILL 경로"""
    return fixtures_path / "sample_skills"


@pytest.fixture
def sample_agents_path(fixtures_path: Path) -> Path:
    """샘플 Agent 경로"""
    return fixtures_path / "sample_agents"


# ============================================================
# Model Fixtures
# ============================================================

@pytest.fixture
def sample_skill() -> Skill:
    """샘플 SKILL"""
    return Skill(
        skill_id="test-skill",
        name="test-skill",
        description="Test skill for unit tests",
        tags=["test", "unit", "sample"],
        content="# Test SKILL\n\nThis is a test skill content.",
        path="/tmp/test-skill/SKILL.md",
        version="1.0.0",
        author="Test Author",
        dependencies=[],
    )


@pytest.fixture
def sample_agent() -> Agent:
    """샘플 Agent"""
    return Agent(
        agent_id="test-agent",
        tier="tier1-core",
        name="test-agent",
        description="Test agent for unit tests",
        system_prompt="You are a test agent. Respond briefly.",
        version="1.0",
        standalone=True,
        tools=["Read", "Write"],
    )


@pytest.fixture
def sample_execution_result() -> ExecutionResult:
    """샘플 실행 결과"""
    return ExecutionResult(
        mode="skill_only",
        response="This is a test response.",
        skills_used=["test-skill"],
        agents_used=[],
        query="Test query",
        cost_estimate="$0.01",
        execution_time=1.5,
    )


@pytest.fixture
def sample_feedback() -> Feedback:
    """샘플 피드백"""
    return Feedback(
        query="Test query",
        skills_used=["test-skill"],
        score=5,
        comment="Great response!",
        mode="skill_only",
        agents_used=[],
    )


# ============================================================
# Config Fixtures
# ============================================================

@pytest.fixture
def test_config(tmp_path: Path, sample_skills_path: Path, sample_agents_path: Path) -> Config:
    """테스트용 설정"""
    return Config(
        skills_path=sample_skills_path,
        agents_path=sample_agents_path,
        persist_dir=tmp_path / "vectordb",
        openai_api_key="test-key",
        anthropic_api_key="test-key",
    )


# ============================================================
# Mock Fixtures
# ============================================================

class MockLLMClient:
    """Mock LLM Client for testing"""
    
    async def chat(self, messages: list, model: str = "test") -> str:
        """Mock chat completion"""
        return "Mock LLM response"
    
    async def embed(self, text: str) -> list:
        """Mock embedding"""
        return [0.0] * 1536  # OpenAI embedding size


@pytest.fixture
def mock_llm_client() -> MockLLMClient:
    """Mock LLM 클라이언트"""
    return MockLLMClient()
