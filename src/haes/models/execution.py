"""
Execution Data Models

실행 결과 관련 데이터 모델
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any


@dataclass
class ExecutionResult:
    """실행 결과"""

    mode: str
    """사용된 실행 모드"""

    response: str
    """생성된 응답"""

    skills_used: List[str]
    """사용된 SKILL ID 목록"""

    agents_used: List[str]
    """사용된 에이전트 ID 목록"""

    query: str
    """원래 질문"""

    cost_estimate: str = "unknown"
    """예상 비용"""

    execution_time: float = 0.0
    """실행 시간 (초)"""

    sub_results: List[Any] = field(default_factory=list)
    """병렬/협업 모드에서의 개별 결과"""

    metadata: dict = field(default_factory=dict)
    """추가 메타데이터"""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    """실행 시간"""

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "mode": self.mode,
            "response": self.response,
            "skills_used": self.skills_used,
            "agents_used": self.agents_used,
            "query": self.query,
            "cost_estimate": self.cost_estimate,
            "execution_time": self.execution_time,
            "sub_results": [
                r.to_dict() if hasattr(r, "to_dict") else r for r in self.sub_results
            ],
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    def get_summary(self) -> str:
        """실행 결과 요약"""
        return (
            f"Mode: {self.mode}, "
            f"Skills: {self.skills_used}, "
            f"Agents: {self.agents_used}, "
            f"Time: {self.execution_time:.2f}s, "
            f"Cost: {self.cost_estimate}"
        )

    @property
    def success(self) -> bool:
        """성공 여부"""
        return bool(self.response)
