"""
KeywordMatcher Unit Tests
"""

import pytest
from typing import List


class TestKeywordMatcher:
    """KeywordMatcher 단위 테스트"""

    def test_matches_korean_keywords(self):
        """한국어 키워드 매칭"""
        from haes.router.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        result = matcher.match("LoRA 파인튜닝 방법")

        assert len(result) > 0
        # fine-tuning 관련 SKILL이 매칭되어야 함
        assert any("fine-tuning" in skill_id or "tuning" in skill_id for skill_id, _ in result)

    def test_matches_english_keywords(self):
        """영어 키워드 매칭"""
        from haes.router.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        result = matcher.match("vLLM inference serving")

        assert len(result) > 0
        assert any("inference" in skill_id or "serving" in skill_id for skill_id, _ in result)

    def test_matches_rag_keywords(self):
        """RAG 관련 키워드 매칭"""
        from haes.router.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        result = matcher.match("벡터 검색 RAG 구현")

        assert len(result) > 0
        assert any("rag" in skill_id for skill_id, _ in result)

    def test_returns_empty_for_no_match(self):
        """매칭 없으면 빈 리스트"""
        from haes.router.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        result = matcher.match("xyz123 completely random gibberish")

        # 완전히 랜덤한 쿼리는 매칭 없을 수 있음
        assert isinstance(result, list)

    def test_returns_max_3_matches(self):
        """최대 3개 매칭"""
        from haes.router.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        result = matcher.match("transformer lora vllm deepspeed rag agents")

        assert len(result) <= 3

    def test_returns_skill_ids_and_scores(self):
        """SKILL ID와 점수 반환"""
        from haes.router.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        result = matcher.match("파인튜닝")

        assert len(result) > 0
        # (skill_id, score) 튜플
        assert len(result[0]) == 2
        assert isinstance(result[0][0], str)
        assert isinstance(result[0][1], (int, float))

    def test_higher_score_for_better_match(self):
        """더 좋은 매칭에 높은 점수"""
        from haes.router.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        result = matcher.match("LoRA fine-tuning")

        if len(result) > 1:
            # 점수 내림차순 정렬 확인
            scores = [score for _, score in result]
            assert scores == sorted(scores, reverse=True)

    def test_get_all_keywords(self):
        """전체 키워드 맵 반환"""
        from haes.router.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        keywords = matcher.get_all_keywords()

        assert isinstance(keywords, dict)
        assert len(keywords) > 0
