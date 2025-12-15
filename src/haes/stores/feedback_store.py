"""
FeedbackStore - 피드백 저장 및 관리

사용자 피드백 수집 및 분석
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

from haes.models.feedback import Feedback


class FeedbackStore:
    """피드백 저장소"""

    def __init__(self):
        """FeedbackStore 초기화"""
        self._feedbacks: List[Feedback] = []
        logger.info("FeedbackStore initialized")

    def record(
        self,
        query: str,
        skills: List[str],
        score: int,
        comment: str = "",
        mode: str = "",
        agents: Optional[List[str]] = None,
    ) -> Feedback:
        """
        피드백 기록

        Args:
            query: 원래 질문
            skills: 사용된 SKILL 목록
            score: 평가 점수 (1-5)
            comment: 추가 의견
            mode: 사용된 실행 모드
            agents: 사용된 에이전트 목록

        Returns:
            생성된 Feedback 객체
        """
        feedback = Feedback(
            query=query,
            skills_used=skills,
            score=score,
            comment=comment,
            mode=mode,
            agents_used=agents or [],
            timestamp=datetime.now().isoformat(),
        )

        self._feedbacks.append(feedback)
        logger.debug(f"Recorded feedback: score={score}, skills={skills}")

        return feedback

    def all(self) -> List[Feedback]:
        """
        모든 피드백 반환

        Returns:
            전체 피드백 목록
        """
        return self._feedbacks.copy()

    def get_by_skill(self, skill_id: str) -> List[Feedback]:
        """
        SKILL별 피드백 필터링

        Args:
            skill_id: SKILL ID

        Returns:
            해당 SKILL 관련 피드백 목록
        """
        return [
            f for f in self._feedbacks
            if skill_id in f.skills_used
        ]

    def get_positive(self) -> List[Feedback]:
        """
        긍정적 피드백 반환 (4점 이상)

        Returns:
            긍정적 피드백 목록
        """
        return [f for f in self._feedbacks if f.is_positive]

    def get_negative(self) -> List[Feedback]:
        """
        부정적 피드백 반환 (2점 이하)

        Returns:
            부정적 피드백 목록
        """
        return [f for f in self._feedbacks if f.is_negative]

    def get_average_score(self, skill_id: Optional[str] = None) -> float:
        """
        평균 점수 계산

        Args:
            skill_id: SKILL ID (None이면 전체)

        Returns:
            평균 점수
        """
        if skill_id:
            feedbacks = self.get_by_skill(skill_id)
        else:
            feedbacks = self._feedbacks

        if not feedbacks:
            return 0.0

        return sum(f.score for f in feedbacks) / len(feedbacks)

    def get_stats(self) -> Dict[str, Any]:
        """
        피드백 통계 반환

        Returns:
            통계 딕셔너리
        """
        total = len(self._feedbacks)

        if total == 0:
            return {
                "total": 0,
                "average_score": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "skills_coverage": {},
            }

        # SKILL별 피드백 수
        skills_coverage = {}
        for feedback in self._feedbacks:
            for skill in feedback.skills_used:
                skills_coverage[skill] = skills_coverage.get(skill, 0) + 1

        return {
            "total": total,
            "average_score": self.get_average_score(),
            "positive_count": len(self.get_positive()),
            "negative_count": len(self.get_negative()),
            "skills_coverage": skills_coverage,
        }

    def clear(self) -> None:
        """전체 피드백 삭제"""
        self._feedbacks.clear()
        logger.info("All feedbacks cleared")

    def get_recent(self, n: int = 10) -> List[Feedback]:
        """
        최근 N개 피드백 반환

        Args:
            n: 반환할 개수

        Returns:
            최근 피드백 목록
        """
        return self._feedbacks[-n:]
