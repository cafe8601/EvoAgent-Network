"""
HybridAISystem - 메인 시스템

SKILL + Agent 통합 하이브리드 AI 시스템
"""

import asyncio
import time
from typing import List, Optional, Any, Dict
from loguru import logger

from haes.config import Config
from haes.models.routing import ExecutionMode, RoutingDecision
from haes.models.execution import ExecutionResult
from haes.models.feedback import Feedback
from haes.stores.skill_store import SkillStore
from haes.stores.agent_pool import AgentPool
from haes.stores.feedback_store import FeedbackStore
from haes.router.hybrid_router import HybridRouter
from haes.evolution.evolution_engine import EvolutionEngine
from haes.tools.web_search import WebSearchTool, get_search_tool
from haes.memory.agent_memory import AgentMemory, get_memory


class HybridAISystem:
    """
    Hybrid AI Evolution System (HAES)
    
    63개 SKILL + 159개 에이전트 통합 시스템
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        llm_client: Optional[Any] = None,
    ):
        """
        HybridAISystem 초기화

        Args:
            config: 시스템 설정
            llm_client: LLM 클라이언트 (없으면 Mock 사용)
        """
        self.config = config or Config()
        self.llm_client = llm_client

        # 저장소 초기화
        self.skill_store = SkillStore(
            skills_path=str(self.config.skills_path),
            persist_dir=str(self.config.persist_dir),
        )

        self.agent_pool = AgentPool(
            agents_path=str(self.config.agents_path),
        )

        self.feedback_store = FeedbackStore()

        # 진화 엔진 초기화
        self.evolution = EvolutionEngine()

        # 라우터 초기화
        self.router = HybridRouter(
            skill_store=self.skill_store,
            llm_client=llm_client,
        )

        # 대화 히스토리
        self.history: List[Dict] = []

        # 마지막 결과 (피드백용)
        self._last_result: Optional[ExecutionResult] = None

        # 웹 검색 도구
        self.search_tool = get_search_tool()

        # 3계층 메모리 시스템 (28-agent-memory SKILL 기반)
        self.memory = get_memory()

        # 검색 트리거 키워드
        self._search_keywords = [
            "최신", "latest", "뉴스", "news", "오늘", "today",
            "현재", "current", "2024", "2025", "트렌드", "trend",
            "출시", "release", "발표", "announce", "가격", "price",
            "주가", "stock", "환율", "exchange", "날씨", "weather",
            "검색", "search", "찾아줘", "find",
        ]

        logger.info("HybridAISystem initialized with 3-layer memory")

    def initialize(self) -> Dict[str, int]:
        """
        시스템 초기화 (인덱싱)

        Returns:
            초기화 통계
        """
        skill_count = self.skill_store.index_all_skills()
        agent_count = self.agent_pool.load_all_agents()

        logger.info(f"Initialized: {skill_count} skills, {agent_count} agents")

        return {
            "skills_indexed": skill_count,
            "agents_loaded": agent_count,
        }

    def _needs_web_search(self, query: str) -> bool:
        """
        웹 검색이 필요한지 확인

        Args:
            query: 사용자 쿼리

        Returns:
            검색 필요 여부
        """
        query_lower = query.lower()
        return any(kw in query_lower for kw in self._search_keywords)

    async def chat(self, query: str) -> ExecutionResult:
        """
        사용자 쿼리 처리

        Args:
            query: 사용자 질문

        Returns:
            ExecutionResult
        """
        start_time = time.time()

        # 1. Evolution 힌트 확인
        hints = self.evolution.get_routing_hints(query)
        
        # 2. 라우팅 결정 (힌트 우선 또는 라우터)
        if hints["confidence"] > 0.8:
            # 학습된 패턴 사용
            decision = RoutingDecision(
                mode=ExecutionMode(hints["suggested_mode"]) if hints["suggested_mode"] else ExecutionMode.SKILL_ONLY,
                skills=hints["suggested_skills"],
                agents=hints.get("suggested_agents", []),
                reason=f"학습된 패턴 사용 (신뢰도: {hints['confidence']:.2f})",
                confidence=hints["confidence"],
            )
        else:
            decision = await self.router.route(query)

        # 3. 장기 메모리에서 관련 컨텍스트 가져오기
        memory_context = self.memory.get_long_term_context(query)
        if memory_context:
            logger.debug(f"Long-term memory context loaded")

        # 4. 실행
        result = await self._execute(decision, query)

        # 5. 실행 시간 기록
        result.execution_time = time.time() - start_time

        # 6. 히스토리 업데이트
        self._update_history(query, result)

        # 7. 메모리에 저장
        self.memory.add_to_session("user", query)
        self.memory.add_to_session("assistant", result.response, {
            "mode": result.mode,
            "skills": result.skills_used,
        })

        # 8. 마지막 결과 저장
        self._last_result = result

        logger.info(f"Chat completed: mode={result.mode}, time={result.execution_time:.2f}s")

        return result

    async def _execute(
        self,
        decision: RoutingDecision,
        query: str,
    ) -> ExecutionResult:
        """
        라우팅 결정에 따른 실행

        Args:
            decision: 라우팅 결정
            query: 사용자 쿼리

        Returns:
            ExecutionResult
        """
        if decision.mode == ExecutionMode.SKILL_ONLY:
            return await self._execute_skill_only(query, decision)
        elif decision.mode == ExecutionMode.SKILL_AGENT:
            return await self._execute_skill_agent(query, decision)
        elif decision.mode == ExecutionMode.PARALLEL:
            return await self._execute_parallel(query, decision)
        else:  # MULTI_AGENT
            return await self._execute_multi_agent(query, decision)

    async def _execute_skill_only(
        self,
        query: str,
        decision: RoutingDecision,
    ) -> ExecutionResult:
        """SKILL_ONLY 모드 실행"""
        # SKILL 내용 로드
        skill_content = ""
        if decision.skills:
            skill_content = self.skill_store.load(decision.skills)

        # 1. 장기 메모리에서 관련 컨텍스트 가져오기
        memory_context = self.memory.get_long_term_context(query)
        if memory_context:
            skill_content = memory_context + "\n\n" + skill_content
            logger.info(f"장기 메모리 컨텍스트 주입됨")

        # 2. 단기 메모리에서 관련 대화 가져오기
        short_memories = self.memory.search_short_term(query, limit=2)
        if short_memories:
            short_context = "\n\n## 최근 관련 대화:\n"
            for mem in short_memories:
                short_context += f"- Q: {mem.query[:100]}...\n  A: {mem.content[:200]}...\n"
            skill_content = short_context + "\n" + skill_content
            logger.info(f"단기 메모리 {len(short_memories)}개 주입됨")

        # 3. 웹 검색 필요 여부 확인
        search_context = ""
        if self._needs_web_search(query):
            logger.info(f"웹 검색 실행: {query}")
            search_results = await self.search_tool.search(query, max_results=3)
            if search_results:
                search_context = "\n\n## 웹 검색 결과:\n" + self.search_tool.format_results(search_results)
                skill_content += search_context

        # 4. 복잡도에 따른 모델 선택
        # 복잡도 점수가 낮고(0.3 이하), SKILL이 없거나 적으면 gpt-5-mini 사용
        complexity_score = decision.complexity.score if decision.complexity else 0.5
        use_lite = (
            complexity_score <= 0.3 and 
            len(decision.skills) <= 1 and 
            not search_context  # 웹 검색이 필요한 경우는 고품질 모델 사용
        )
        
        if use_lite:
            logger.info(f"단순 질문 (복잡도={complexity_score:.2f}) → gpt-5-mini 사용 (비용 절감)")

        # LLM 호출 (또는 Mock)
        if self.llm_client:
            response = await self._call_llm(query, skill_content, use_lite_model=use_lite)
        else:
            response = self._mock_response(query, decision.skills)

        # 검색 결과 포함 여부 표시
        skills_used = decision.skills.copy() if decision.skills else []
        if search_context:
            skills_used.append("27-web-search")

        # 사용된 모델 정보 포함
        cost_estimate = "~$0.001" if use_lite else "~$0.01"

        return ExecutionResult(
            mode="skill_only",
            response=response,
            skills_used=skills_used,
            agents_used=[],
            query=query,
            cost_estimate=cost_estimate,
        )

    async def _execute_skill_agent(
        self,
        query: str,
        decision: RoutingDecision,
    ) -> ExecutionResult:
        """SKILL_AGENT 모드 실행"""
        # SKILL 내용 로드
        skill_content = ""
        if decision.skills:
            skill_content = self.skill_store.load(decision.skills)

        # 에이전트 시스템 프롬프트
        agent_prompt = ""
        if decision.agents:
            agent = self.agent_pool.get(decision.agents[0])
            if agent:
                agent_prompt = agent.system_prompt

        # LLM 호출
        if self.llm_client:
            response = await self._call_llm_with_agent(query, skill_content, agent_prompt)
        else:
            response = self._mock_response(query, decision.skills, decision.agents)

        return ExecutionResult(
            mode="skill_agent",
            response=response,
            skills_used=decision.skills,
            agents_used=decision.agents,
            query=query,
            cost_estimate="~$0.05",
        )

    async def _execute_parallel(
        self,
        query: str,
        decision: RoutingDecision,
    ) -> ExecutionResult:
        """PARALLEL 모드 실행"""
        # 각 에이전트별 태스크 생성
        tasks = []
        for agent_id in decision.agents:
            agent = self.agent_pool.get(agent_id)
            if agent:
                tasks.append(self._run_agent_task(query, agent))

        # 병렬 실행
        if tasks:
            sub_results = await asyncio.gather(*tasks, return_exceptions=True)
            responses = [r for r in sub_results if isinstance(r, str)]
            response = "\n\n---\n\n".join(responses)
        else:
            response = self._mock_response(query, decision.skills, decision.agents)

        return ExecutionResult(
            mode="parallel",
            response=response,
            skills_used=decision.skills,
            agents_used=decision.agents,
            query=query,
            cost_estimate="~$0.15",
            sub_results=list(sub_results) if tasks else [],
        )

    async def _execute_multi_agent(
        self,
        query: str,
        decision: RoutingDecision,
    ) -> ExecutionResult:
        """MULTI_AGENT 모드 실행"""
        # 순차 실행
        responses = []
        context = query

        for agent_id in decision.agents:
            agent = self.agent_pool.get(agent_id)
            if agent:
                if self.llm_client:
                    result = await self._call_llm_with_agent(context, "", agent.system_prompt)
                else:
                    result = f"[{agent_id}] 처리 결과"
                responses.append(f"## {agent.name}\n\n{result}")
                context = result  # 다음 에이전트에게 전달

        response = "\n\n".join(responses)

        return ExecutionResult(
            mode="multi_agent",
            response=response,
            skills_used=decision.skills,
            agents_used=decision.agents,
            query=query,
            cost_estimate="~$0.20",
            sub_results=responses,
        )

    async def _run_agent_task(self, query: str, agent: Any) -> str:
        """단일 에이전트 태스크 실행"""
        if self.llm_client:
            return await self._call_llm_with_agent(query, "", agent.system_prompt)
        return f"[{agent.agent_id}] 처리 완료"

    async def _call_llm(
        self,
        query: str,
        skill_content: str,
        use_lite_model: bool = False,
    ) -> str:
        """
        LLM 호출
        
        Args:
            query: 사용자 쿼리
            skill_content: SKILL 컨텍스트
            use_lite_model: True면 gpt-5-mini, False면 gpt-5.1
        """
        if self.llm_client:
            # 실제 OpenAI API 호출
            return await self.llm_client.generate_with_skill(
                query=query,
                skill_content=skill_content,
                use_lite_model=use_lite_model,
            )
        
        # Mock 응답
        return f"응답: {query}"

    async def _call_llm_with_agent(
        self,
        query: str,
        skill_content: str,
        agent_prompt: str,
    ) -> str:
        """에이전트와 함께 LLM 호출"""
        if self.llm_client:
            # 실제 OpenAI API 호출
            return await self.llm_client.generate_with_skill(
                query=query,
                skill_content=skill_content,
                agent_prompt=agent_prompt,
            )
        
        # Mock 응답
        return f"에이전트 응답: {query}"

    def _mock_response(
        self,
        query: str,
        skills: List[str],
        agents: Optional[List[str]] = None,
    ) -> str:
        """Mock 응답 생성 (테스트용)"""
        skill_info = ", ".join(skills) if skills else "없음"
        agent_info = ", ".join(agents) if agents else "없음"

        return f"""## 응답

**질문**: {query}

**사용된 SKILL**: {skill_info}
**사용된 에이전트**: {agent_info}

이것은 테스트용 Mock 응답입니다.
실제 LLM 클라이언트가 설정되면 실제 응답이 생성됩니다.
"""

    def _update_history(self, query: str, result: ExecutionResult) -> None:
        """대화 히스토리 업데이트"""
        self.history.append({
            "role": "user",
            "content": query,
        })
        self.history.append({
            "role": "assistant",
            "content": result.response,
            "metadata": {
                "mode": result.mode,
                "skills": result.skills_used,
                "agents": result.agents_used,
            },
        })

        # 히스토리 제한 (최근 20개)
        if len(self.history) > 40:
            self.history = self.history[-40:]

    def feedback(self, score: int, comment: str = "") -> Feedback:
        """
        사용자 피드백 수집

        Args:
            score: 평가 점수 (1-5)
            comment: 추가 의견

        Returns:
            Feedback 객체
        """
        if not self._last_result:
            raise ValueError("No previous result to provide feedback for")

        feedback = self.feedback_store.record(
            query=self._last_result.query,
            skills=self._last_result.skills_used,
            score=score,
            comment=comment,
            mode=self._last_result.mode,
            agents=self._last_result.agents_used,
        )

        # Evolution 엔진에도 피드백 전달
        improvement = self.evolution.record_feedback(
            result=self._last_result,
            feedback=comment,
            score=score,
        )

        if improvement:
            logger.warning(f"Improvement needed: {improvement}")

        # 단기 메모리에 저장 (점수와 함께)
        self.memory.save_short_term(
            query=self._last_result.query,
            response=self._last_result.response,
            mode=self._last_result.mode,
            skills=self._last_result.skills_used,
            score=float(score),
        )

        logger.info(f"Feedback recorded: score={score}")

        return feedback

    def get_stats(self) -> Dict[str, Any]:
        """시스템 통계 반환"""
        return {
            "skill_store": self.skill_store.get_stats(),
            "agent_pool": self.agent_pool.get_stats(),
            "feedback": self.feedback_store.get_stats(),
            "evolution": self.evolution.get_stats(),
            "memory": self.memory.get_stats(),
            "history_length": len(self.history),
        }

    def get_compressed_index(self) -> str:
        """압축 SKILL 인덱스 반환"""
        return self.skill_store.get_compressed_index()
