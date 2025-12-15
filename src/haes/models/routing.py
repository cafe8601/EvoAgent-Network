"""
Routing Data Models

라우팅 결정 관련 데이터 모델
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ExecutionMode(Enum):
    """실행 모드"""

    SKILL_ONLY = "skill_only"
    """단순 지식 조회 - SKILL만 사용"""

    SKILL_AGENT = "skill_agent"
    """SKILL + 단일 전문 에이전트"""

    PARALLEL = "parallel"
    """병렬 다중 작업 실행"""

    MULTI_AGENT = "multi_agent"
    """다중 에이전트 순차 협업"""


@dataclass
class ComplexityAnalysis:
    """복잡도 분석 결과"""

    score: float
    """복잡도 점수 (0.0 ~ 1.0)"""

    is_parallel: bool
    """병렬 실행 가능 여부"""

    is_collaborative: bool
    """협업 필요 여부"""

    indicators: dict = field(default_factory=dict)
    """분석 지표"""


@dataclass
class RoutingDecision:
    """라우팅 결정 결과"""

    mode: ExecutionMode
    """선택된 실행 모드"""

    skills: List[str]
    """선택된 SKILL ID 목록"""

    agents: List[str]
    """선택된 에이전트 ID 목록"""

    reason: str
    """선택 이유"""

    confidence: float
    """라우팅 신뢰도 (0.0 ~ 1.0)"""

    complexity: Optional[ComplexityAnalysis] = None
    """복잡도 분석 결과"""

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "mode": self.mode.value,
            "skills": self.skills,
            "agents": self.agents,
            "reason": self.reason,
            "confidence": self.confidence,
            "complexity": self.complexity.__dict__ if self.complexity else None,
        }

    def get_summary(self) -> str:
        """라우팅 결정 요약"""
        return (
            f"Mode: {self.mode.value}, "
            f"Skills: {self.skills}, "
            f"Agents: {self.agents}, "
            f"Confidence: {self.confidence:.2f}"
        )
