"""
Agent Data Model

전문 에이전트를 표현하는 데이터 모델
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Agent:
    """전문 에이전트 표현"""

    agent_id: str
    """에이전트 고유 식별자 (예: "backend-developer")"""

    tier: str
    """품질 등급 (tier1-core, tier2-specialized, tier3-experimental)"""

    name: str
    """에이전트 이름"""

    description: str
    """에이전트 설명"""

    system_prompt: str
    """에이전트의 시스템 프롬프트 (전체 .md 파일 내용)"""

    version: str = "1.0"
    """에이전트 버전"""

    standalone: bool = True
    """독립 실행 가능 여부"""

    tools: List[str] = field(default_factory=list)
    """사용 가능한 도구 목록"""

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "agent_id": self.agent_id,
            "tier": self.tier,
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "version": self.version,
            "standalone": self.standalone,
            "tools": self.tools,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        """딕셔너리에서 생성"""
        return cls(
            agent_id=data["agent_id"],
            tier=data["tier"],
            name=data["name"],
            description=data.get("description", ""),
            system_prompt=data["system_prompt"],
            version=data.get("version", "1.0"),
            standalone=data.get("standalone", True),
            tools=data.get("tools", []),
        )

    def is_tier1(self) -> bool:
        """Tier 1 에이전트 여부"""
        return self.tier == "tier1-core"

    def get_summary(self) -> str:
        """에이전트 요약"""
        return f"{self.agent_id} ({self.tier}): {self.description[:100]}"
