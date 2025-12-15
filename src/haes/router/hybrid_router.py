"""
HybridRouter - 하이브리드 라우팅 엔진

키워드 매칭 우선 + LLM 폴백 방식의 라우팅
"""

import re
from typing import List, Optional, Any
from loguru import logger

from haes.models.routing import ExecutionMode, RoutingDecision, ComplexityAnalysis
from haes.router.keyword_matcher import KeywordMatcher
from haes.stores.skill_store import SkillStore


class HybridRouter:
    """하이브리드 라우터 - 복잡도 기반 실행 모드 결정"""

    # 복잡도 판별 키워드
    COMPLEXITY_INDICATORS = {
        "implementation": [
            "구현", "implement", "만들어", "작성", "build", "create",
            "개발", "develop", "코드"
        ],
        "parallel": [
            "그리고", "하고", "and", "또한", "동시에", "병렬로"
        ],
        "collaboration": [
            "검토", "review", "확인", "validate", "후에", "다음에", "then"
        ],
        "design": [
            "설계", "design", "아키텍처", "architecture", "구조"
        ],
    }

    # 단순 질문 패턴
    SIMPLE_PATTERNS = [
        r"뭐야\??$",
        r"뭔가요\??$",
        r"what is",
        r"알려줘$",
        r"설명해줘$",
        r"explain",
        r"tell me",
    ]

    # 라우팅 신뢰도 임계값
    LLM_ROUTING_THRESHOLD = 0.5  # 이 이하면 LLM 라우팅 사용

    def __init__(
        self,
        skill_store: SkillStore,
        llm_client: Optional[Any] = None,
    ):
        """
        HybridRouter 초기화

        Args:
            skill_store: SKILL 저장소
            llm_client: LLM 클라이언트 (gpt-5-mini 라우팅용)
        """
        self.skill_store = skill_store
        self.llm_client = llm_client
        self.keyword_matcher = KeywordMatcher()

        logger.info("HybridRouter initialized")

    async def route(self, query: str) -> RoutingDecision:
        """
        쿼리 라우팅 (하이브리드 방식)

        1차: 키워드 매칭 (무료, 즉시)
        2차: LLM 라우팅 (gpt-5-mini, 신뢰도 낮을 때만)

        Args:
            query: 사용자 쿼리

        Returns:
            RoutingDecision
        """
        # 1. 복잡도 분석
        complexity = self._analyze_complexity(query)

        # 2. 키워드 기반 SKILL 매칭 (1차 - 무료)
        matched_skills = self.keyword_matcher.match_skill_ids(query, max_results=3)

        # 보조: SkillStore 검색
        if not matched_skills:
            store_results = self.skill_store.search(query, k=3)
            matched_skills = [s.skill_id for s in store_results]

        # 3. 실행 모드 결정 (규칙 기반)
        mode, agents, reason = self._decide_mode(query, complexity, matched_skills)

        # 4. 신뢰도 계산
        confidence = self._calculate_confidence(matched_skills, complexity)

        # 5. LLM 라우팅 폴백 (신뢰도 낮을 때 gpt-5-mini 사용)
        if confidence < self.LLM_ROUTING_THRESHOLD and self.llm_client:
            logger.info(f"Low confidence ({confidence:.2f}), using LLM routing (gpt-5-mini)")
            llm_decision = await self._llm_route(query)
            
            if llm_decision and llm_decision.get("reason") != "Parse error":
                # LLM 결정 사용 (파싱 성공 시)
                llm_skills = llm_decision.get("skills", [])
                # LLM이 SKILL을 못 찾으면 키워드 매칭 결과 사용
                final_skills = llm_skills if llm_skills else matched_skills
                
                return RoutingDecision(
                    mode=ExecutionMode(llm_decision.get("mode", "skill_only")),
                    skills=final_skills,
                    agents=llm_decision.get("agents", agents),
                    reason=f"LLM 라우팅: {llm_decision.get('reason', '')}",
                    confidence=0.8,  # LLM 결정은 높은 신뢰도
                    complexity=complexity,
                )
            else:
                # 파싱 실패 시 키워드 매칭 결과 그대로 사용
                logger.debug("LLM parsing failed, using keyword matching result")

        return RoutingDecision(
            mode=mode,
            skills=matched_skills,
            agents=agents,
            reason=reason,
            confidence=confidence,
            complexity=complexity,
        )

    async def _llm_route(self, query: str) -> Optional[dict]:
        """
        gpt-5-mini를 사용한 LLM 라우팅

        Args:
            query: 사용자 쿼리

        Returns:
            라우팅 결정 딕셔너리 또는 None
        """
        if not self.llm_client:
            return None

        try:
            # 압축 인덱스 사용
            skill_index = self.skill_store.get_compressed_index()
            
            # gpt-5-mini로 라우팅 결정
            result = await self.llm_client.route(query, skill_index)
            logger.debug(f"LLM routing result: {result}")
            
            return result
        except Exception as e:
            logger.warning(f"LLM routing failed: {e}")
            return None


    def _analyze_complexity(self, query: str) -> ComplexityAnalysis:
        """
        쿼리 복잡도 분석

        Args:
            query: 사용자 쿼리

        Returns:
            ComplexityAnalysis
        """
        query_lower = query.lower()

        # 단순 질문 패턴 체크
        is_simple = any(
            re.search(pattern, query_lower)
            for pattern in self.SIMPLE_PATTERNS
        )

        # 복잡도 지표 계산
        indicators = {}
        total_score = 0.0

        for category, keywords in self.COMPLEXITY_INDICATORS.items():
            count = sum(1 for kw in keywords if kw in query_lower)
            indicators[category] = count
            # 각 카테고리 키워드 매칭 시 점수 증가
            total_score += count * 0.15

        # 병렬 작업 체크 - "하고" 패턴 강화
        parallel_count = query_lower.count("하고") + query_lower.count("그리고") + query_lower.count(" and ")
        is_parallel = parallel_count >= 2  # 2번 이상 연결 = 3개 이상 작업

        # 협업 체크 (순차 의존)
        collab_keywords = self.COMPLEXITY_INDICATORS["collaboration"]
        collab_count = sum(1 for kw in collab_keywords if kw in query_lower)
        is_collaborative = collab_count >= 1 and indicators.get("design", 0) > 0

        # 구현/개발 키워드 있으면 추가 점수
        if indicators.get("implementation", 0) > 0:
            total_score += 0.2

        # 병렬 작업 감지되면 점수 증가
        if is_parallel:
            total_score += 0.3

        # 협업 작업 감지되면 점수 증가
        if is_collaborative:
            total_score += 0.3

        # 최종 점수 조정
        if is_simple and not is_parallel and not is_collaborative:
            total_score = min(total_score, 0.25)

        total_score = min(total_score, 1.0)

        return ComplexityAnalysis(
            score=total_score,
            is_parallel=is_parallel,
            is_collaborative=is_collaborative,
            indicators=indicators,
        )

    def _decide_mode(
        self,
        query: str,
        complexity: ComplexityAnalysis,
        skills: List[str],
    ) -> tuple[ExecutionMode, List[str], str]:
        """
        실행 모드 결정

        Args:
            query: 사용자 쿼리
            complexity: 복잡도 분석 결과
            skills: 매칭된 SKILL 목록

        Returns:
            (모드, 에이전트 목록, 이유)
        """
        # 병렬 작업 (3개 이상 독립 작업)
        if complexity.is_parallel:
            agents = self._select_agents_for_parallel(query)
            return (
                ExecutionMode.PARALLEL,
                agents,
                f"병렬 실행 가능한 {len(agents)}개 독립 작업 감지",
            )

        # 협업 필요 (순차 의존성)
        if complexity.is_collaborative:
            agents = self._select_agents_for_collaboration(query)
            return (
                ExecutionMode.MULTI_AGENT,
                agents,
                "순차적 협업이 필요한 작업",
            )

        # 구현 작업 (복잡도 중간)
        if complexity.score >= 0.3:
            agents = self._select_primary_agent(query)
            return (
                ExecutionMode.SKILL_AGENT,
                agents,
                f"기술적 구현 작업 (복잡도: {complexity.score:.2f})",
            )

        # 단순 지식 조회
        return (
            ExecutionMode.SKILL_ONLY,
            [],
            f"단순 지식 조회 (복잡도: {complexity.score:.2f})",
        )

    def _select_agents_for_parallel(self, query: str) -> List[str]:
        """병렬 작업용 에이전트 선택"""
        agents = []
        query_lower = query.lower()

        # 키워드 기반 에이전트 매핑
        agent_keywords = {
            "backend-developer": ["api", "backend", "서버", "데이터베이스"],
            "frontend-developer": ["ui", "frontend", "프론트"],
            "qa-expert": ["test", "테스트", "qa", "검증"],
            "tech-writer": ["문서", "doc", "documentation"],
            "devops-engineer": ["배포", "deploy", "ci/cd"],
        }

        for agent_id, keywords in agent_keywords.items():
            if any(kw in query_lower for kw in keywords):
                agents.append(agent_id)

        # 최소 2개 에이전트
        if len(agents) < 2:
            agents = ["backend-developer", "qa-expert", "tech-writer"]

        return agents[:4]  # 최대 4개

    def _select_agents_for_collaboration(self, query: str) -> List[str]:
        """협업용 에이전트 선택 (순서 중요)"""
        query_lower = query.lower()

        # 협업 패턴
        if "설계" in query_lower and "검토" in query_lower:
            return ["system-architect", "security-reviewer"]

        if "구현" in query_lower and "테스트" in query_lower:
            return ["backend-developer", "qa-expert"]

        # 기본 협업 패턴
        return ["system-architect", "backend-developer"]

    def _select_primary_agent(self, query: str) -> List[str]:
        """주요 작업용 단일 에이전트 선택"""
        query_lower = query.lower()

        # 키워드 기반
        if any(kw in query_lower for kw in ["api", "backend", "서버", "서빙"]):
            return ["backend-developer"]

        if any(kw in query_lower for kw in ["ui", "frontend", "프론트"]):
            return ["frontend-developer"]

        if any(kw in query_lower for kw in ["ml", "ai", "모델", "학습"]):
            return ["ml-engineer"]

        # 기본
        return ["backend-developer"]

    def _calculate_confidence(
        self,
        skills: List[str],
        complexity: ComplexityAnalysis,
    ) -> float:
        """
        라우팅 신뢰도 계산

        Args:
            skills: 매칭된 SKILL 목록
            complexity: 복잡도 분석 결과

        Returns:
            신뢰도 (0.0 ~ 1.0)
        """
        confidence = 0.5  # 기본값

        # SKILL 매칭 있으면 +0.2
        if skills:
            confidence += 0.2

        # 복잡도 분석 지표 있으면 +0.1
        if any(complexity.indicators.values()):
            confidence += 0.1

        # 병렬/협업 패턴 명확하면 +0.1
        if complexity.is_parallel or complexity.is_collaborative:
            confidence += 0.1

        return min(confidence, 1.0)
