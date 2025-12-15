"""
FeedbackStore Unit Tests
"""

import pytest
from pathlib import Path

from haes.models.feedback import Feedback


class TestFeedbackStore:
    """FeedbackStore 단위 테스트"""

    def test_init_creates_empty_store(self):
        """초기화 시 빈 저장소 생성"""
        from haes.stores.feedback_store import FeedbackStore

        store = FeedbackStore()

        assert len(store.all()) == 0

    def test_record_saves_feedback(self):
        """피드백이 저장되어야 함"""
        from haes.stores.feedback_store import FeedbackStore

        store = FeedbackStore()

        store.record(
            query="test query",
            skills=["skill-a"],
            score=5,
            comment="Great!",
        )

        assert len(store.all()) == 1

    def test_record_multiple_feedbacks(self):
        """여러 피드백 저장"""
        from haes.stores.feedback_store import FeedbackStore

        store = FeedbackStore()

        store.record(query="q1", skills=["s1"], score=5)
        store.record(query="q2", skills=["s2"], score=3)
        store.record(query="q3", skills=["s3"], score=4)

        assert len(store.all()) == 3

    def test_get_by_skill_filters_correctly(self):
        """SKILL별 피드백 필터링"""
        from haes.stores.feedback_store import FeedbackStore

        store = FeedbackStore()

        store.record(query="q1", skills=["skill-a"], score=5)
        store.record(query="q2", skills=["skill-b"], score=3)
        store.record(query="q3", skills=["skill-a", "skill-c"], score=4)

        results = store.get_by_skill("skill-a")

        assert len(results) == 2

    def test_get_positive_feedbacks(self):
        """긍정적 피드백만 필터링 (4점 이상)"""
        from haes.stores.feedback_store import FeedbackStore

        store = FeedbackStore()

        store.record(query="q1", skills=["s1"], score=5)
        store.record(query="q2", skills=["s2"], score=3)
        store.record(query="q3", skills=["s3"], score=4)
        store.record(query="q4", skills=["s4"], score=2)

        results = store.get_positive()

        assert len(results) == 2
        assert all(f.score >= 4 for f in results)

    def test_get_negative_feedbacks(self):
        """부정적 피드백만 필터링 (2점 이하)"""
        from haes.stores.feedback_store import FeedbackStore

        store = FeedbackStore()

        store.record(query="q1", skills=["s1"], score=5)
        store.record(query="q2", skills=["s2"], score=2)
        store.record(query="q3", skills=["s3"], score=1)

        results = store.get_negative()

        assert len(results) == 2
        assert all(f.score <= 2 for f in results)

    def test_get_average_score_by_skill(self):
        """SKILL별 평균 점수"""
        from haes.stores.feedback_store import FeedbackStore

        store = FeedbackStore()

        store.record(query="q1", skills=["skill-a"], score=5)
        store.record(query="q2", skills=["skill-a"], score=4)
        store.record(query="q3", skills=["skill-a"], score=3)

        avg = store.get_average_score("skill-a")

        assert avg == 4.0

    def test_get_stats(self):
        """통계 반환"""
        from haes.stores.feedback_store import FeedbackStore

        store = FeedbackStore()

        store.record(query="q1", skills=["s1"], score=5)
        store.record(query="q2", skills=["s2"], score=3)

        stats = store.get_stats()

        assert stats["total"] == 2
        assert "average_score" in stats

    def test_clear_removes_all(self):
        """전체 삭제"""
        from haes.stores.feedback_store import FeedbackStore

        store = FeedbackStore()

        store.record(query="q1", skills=["s1"], score=5)
        store.record(query="q2", skills=["s2"], score=3)

        store.clear()

        assert len(store.all()) == 0
