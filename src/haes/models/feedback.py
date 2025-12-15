"""
Feedback Data Models

피드백 관련 데이터 모델
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Feedback:
    """사용자 피드백"""

    query: str
    """원래 질문"""

    skills_used: List[str]
    """사용된 SKILL 목록"""

    score: int
    """평가 점수 (1-5)"""

    comment: str = ""
    """추가 의견"""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    """피드백 시간"""

    mode: str = ""
    """사용된 실행 모드"""

    agents_used: List[str] = field(default_factory=list)
    """사용된 에이전트 목록"""

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "query": self.query,
            "skills_used": self.skills_used,
            "score": self.score,
            "comment": self.comment,
            "timestamp": self.timestamp,
            "mode": self.mode,
            "agents_used": self.agents_used,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Feedback":
        """딕셔너리에서 생성"""
        return cls(
            query=data["query"],
            skills_used=data["skills_used"],
            score=data["score"],
            comment=data.get("comment", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            mode=data.get("mode", ""),
            agents_used=data.get("agents_used", []),
        )

    @property
    def is_positive(self) -> bool:
        """긍정적 피드백 여부"""
        return self.score >= 4

    @property
    def is_negative(self) -> bool:
        """부정적 피드백 여부"""
        return self.score <= 2


@dataclass
class LearnedPattern:
    """학습된 패턴"""

    query_pattern: str
    """질문 패턴"""

    skills: List[str]
    """연관된 SKILL 목록"""

    mode: str
    """권장 실행 모드"""

    success_rate: float
    """성공률"""

    sample_size: int
    """샘플 수"""

    learned_at: str = field(default_factory=lambda: datetime.now().isoformat())
    """학습 시간"""

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "query_pattern": self.query_pattern,
            "skills": self.skills,
            "mode": self.mode,
            "success_rate": self.success_rate,
            "sample_size": self.sample_size,
            "learned_at": self.learned_at,
        }

    @property
    def is_reliable(self) -> bool:
        """신뢰할 수 있는 패턴인지"""
        return self.success_rate >= 0.8 and self.sample_size >= 5
