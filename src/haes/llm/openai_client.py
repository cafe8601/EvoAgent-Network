"""
OpenAI LLM Client

GPT-5-mini (라우팅) 및 GPT-5.1 (메인) 모델 지원
"""

import os
from typing import List, Dict, Any, Optional
from loguru import logger

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed. Run: pip install openai")


class OpenAIClient:
    """
    OpenAI API 클라이언트
    
    GPT-5-mini: 빠른 라우팅 결정
    GPT-5.1: 상세한 메인 응답
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        routing_model: str = "gpt-5-mini",
        main_model: str = "gpt-5.1",
    ):
        """
        OpenAI 클라이언트 초기화

        Args:
            api_key: OpenAI API 키 (None이면 환경 변수에서 로드)
            routing_model: 라우팅용 모델
            main_model: 메인 응답용 모델
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed")

        # API 키 로드 (환경 변수 우선)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found")

        self.routing_model = routing_model
        self.main_model = main_model

        # AsyncOpenAI 클라이언트
        self.client = AsyncOpenAI(api_key=self.api_key)

        logger.info(f"OpenAI client initialized: routing={routing_model}, main={main_model}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        채팅 완성 요청

        Args:
            messages: 메시지 리스트 [{"role": "...", "content": "..."}]
            model: 사용할 모델 (None이면 main_model)
            temperature: 온도
            max_tokens: 최대 토큰

        Returns:
            응답 텍스트
        """
        model = model or self.main_model

        try:
            # gpt-5-mini는 temperature=1만 지원
            if "mini" in model.lower():
                temperature = 1.0
            
            # GPT-5 시리즈는 max_completion_tokens 사용
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,  # GPT-5 호환
            )

            content = response.choices[0].message.content
            logger.debug(f"OpenAI response: model={model}, tokens={response.usage.total_tokens}")

            return content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def route(
        self,
        query: str,
        skill_index: str,
    ) -> Dict[str, Any]:
        """
        라우팅 결정 (빠른 모델 사용)

        Args:
            query: 사용자 쿼리
            skill_index: 압축된 SKILL 인덱스

        Returns:
            라우팅 결정 딕셔너리
        """
        # SKILL 인덱스를 간략화 (토큰 절약)
        skill_summary = skill_index[:2000] if len(skill_index) > 2000 else skill_index
        
        system_prompt = f"""You are a routing expert. Analyze the query and return ONLY a JSON object.

Available SKILLs: {skill_summary}

Modes:
- skill_only: simple question
- skill_agent: implementation request
- parallel: multiple independent tasks
- multi_agent: sequential collaboration

RESPOND WITH ONLY THIS JSON FORMAT (no explanation):
{{"mode": "skill_only", "skills": ["skill-id"], "reason": "brief reason"}}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        # gpt-5-mini는 temperature를 지원하지 않음
        response = await self.chat(
            messages=messages,
            model=self.routing_model,
            temperature=1.0,  # gpt-5-mini 기본값
            max_tokens=256,
        )

        # JSON 파싱 시도
        try:
            import json
            import re
            
            # JSON 블록 추출 (여러 방법 시도)
            json_str = response
            
            # 방법 1: ```json ... ``` 블록
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            # 방법 2: ``` ... ``` 블록
            elif "```" in response:
                parts = response.split("```")
                if len(parts) >= 2:
                    json_str = parts[1]
            # 방법 3: { ... } 패턴 직접 추출
            else:
                json_match = re.search(r'\{[^{}]*"mode"[^{}]*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
            
            return json.loads(json_str.strip())
        except Exception as e:
            logger.warning(f"Failed to parse routing response: {e}")
            return {"mode": "skill_only", "skills": [], "reason": "Parse error"}

    async def generate_with_skill(
        self,
        query: str,
        skill_content: str,
        agent_prompt: Optional[str] = None,
        use_lite_model: bool = False,
    ) -> str:
        """
        SKILL 컨텍스트와 함께 응답 생성

        Args:
            query: 사용자 쿼리
            skill_content: SKILL 내용 (웹 검색 결과 포함 가능)
            agent_prompt: 에이전트 시스템 프롬프트 (선택)
            use_lite_model: True면 gpt-5-mini (저렴), False면 gpt-5.1 (고품질)

        Returns:
            생성된 응답
        """
        # 컨텍스트 유형 확인
        has_web_search = "웹 검색 결과" in skill_content or "Web Search" in skill_content
        has_memory = "최근 관련 대화" in skill_content or "장기 기억" in skill_content
        
        # 기본 시스템 프롬프트 - 메모리 기능 강조
        base_prompt = """당신은 지속적인 기억력을 가진 AI 전문가 HAES입니다.

**핵심 능력**:
1. 장기 기억: 사용자가 이전에 말한 중요한 정보(주소, 선호도, 이름 등)를 기억합니다.
2. 단기 기억: 최근 대화 내용을 참조합니다.
3. 웹 검색: 최신 정보가 필요할 때 실시간 검색합니다.

**중요**: 아래 "참고 자료"에 이전 대화나 기억된 정보가 있다면,
반드시 이를 활용하여 "이전에 말씀하신 것처럼..." 또는 "기억하고 있습니다..." 형식으로 답변하세요.
사용자에게 "기억할 수 없다"고 말하지 마세요. 메모리에 정보가 있으면 기억합니다."""

        if has_web_search and has_memory:
            base_prompt = """당신은 기억력과 실시간 검색 능력을 가진 AI 전문가 HAES입니다.

**핵심 능력**:
1. 장기 기억: 사용자가 이전에 말한 정보를 기억합니다.
2. 실시간 검색: 최신 정보를 웹에서 검색합니다.

**중요**: 
- 이전 대화 기억이 있으면 "기억하고 있습니다"라고 언급하세요.
- 웹 검색 결과는 "검색 결과에 따르면..."으로 인용하세요.
- 절대로 "기억할 수 없다"고 말하지 마세요."""

        elif has_web_search:
            base_prompt = """당신은 실시간 웹 검색 기능이 있는 AI 전문가 HAES입니다.

아래 "참고 자료"에 방금 검색된 실시간 웹 검색 결과가 있습니다.
- "검색 결과에 따르면..." 형식으로 인용하세요.
- 검색 결과의 출처(URL)도 언급하세요."""

        elif has_memory:
            base_prompt = """당신은 지속적인 기억력을 가진 AI 전문가 HAES입니다.

아래 "참고 자료"에 이전 대화나 기억된 정보가 있습니다.
- "기억하고 있습니다", "이전에 말씀하신 것처럼..." 형식으로 답변하세요.
- 절대로 "기억할 수 없다", "새로 시작하면 잊는다"고 말하지 마세요.
- 메모리 시스템이 당신의 기억을 유지합니다."""

        system = agent_prompt or base_prompt
        
        if skill_content:
            system += f"\n\n## 참고 자료:\n{skill_content}"

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ]

        # 모델 선택: use_lite_model이 True면 gpt-5-mini, 아니면 gpt-5.1
        model = self.routing_model if use_lite_model else self.main_model
        
        return await self.chat(messages=messages, model=model)

    async def test_connection(self) -> bool:
        """
        API 연결 테스트

        Returns:
            연결 성공 여부
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.routing_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_completion_tokens=10,  # GPT-5 호환
            )
            logger.info("OpenAI connection test: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False


def get_client(
    api_key: Optional[str] = None,
    routing_model: str = "gpt-5-mini",
    main_model: str = "gpt-5.1",
) -> OpenAIClient:
    """
    OpenAI 클라이언트 생성 헬퍼

    Args:
        api_key: API 키 (None이면 환경 변수)
        routing_model: 라우팅 모델
        main_model: 메인 모델

    Returns:
        OpenAIClient 인스턴스
    """
    return OpenAIClient(
        api_key=api_key,
        routing_model=routing_model,
        main_model=main_model,
    )
