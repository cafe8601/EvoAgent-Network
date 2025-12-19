"""
HAES Custom Exceptions

시스템 전체에서 사용하는 커스텀 예외 클래스
구체적인 에러 타입 분류 및 일관된 에러 핸들링 지원
"""

from typing import Optional, Dict, Any


class HAESError(Exception):
    """HAES 기본 예외 클래스"""

    def __init__(
        self,
        message: str,
        code: str = "HAES_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """예외를 딕셔너리로 변환 (API 응답용)"""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


# =========================================================================
# 시스템 관련 예외
# =========================================================================


class SystemNotInitializedError(HAESError):
    """시스템이 초기화되지 않음"""

    def __init__(self, component: str = "system"):
        super().__init__(
            message=f"System component not initialized: {component}",
            code="SYSTEM_NOT_INITIALIZED",
            details={"component": component},
        )


class ConfigurationError(HAESError):
    """설정 오류"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            details={"config_key": config_key} if config_key else {},
        )


# =========================================================================
# 라우팅 관련 예외
# =========================================================================


class RoutingError(HAESError):
    """라우팅 오류 기본 클래스"""

    def __init__(
        self,
        message: str,
        code: str = "ROUTING_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class NoSkillMatchError(RoutingError):
    """쿼리에 매칭되는 스킬 없음"""

    def __init__(self, query: str):
        super().__init__(
            message=f"No matching skill found for query: {query[:100]}",
            code="NO_SKILL_MATCH",
            details={"query": query[:200]},
        )


class RoutingConfidenceLowError(RoutingError):
    """라우팅 신뢰도가 낮음"""

    def __init__(self, confidence: float, threshold: float, query: str):
        super().__init__(
            message=f"Routing confidence too low: {confidence:.2f} < {threshold:.2f}",
            code="ROUTING_CONFIDENCE_LOW",
            details={
                "confidence": confidence,
                "threshold": threshold,
                "query": query[:200],
            },
        )


# =========================================================================
# 스킬/에이전트 관련 예외
# =========================================================================


class SkillError(HAESError):
    """스킬 관련 오류 기본 클래스"""

    def __init__(
        self,
        message: str,
        code: str = "SKILL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class SkillNotFoundError(SkillError):
    """스킬을 찾을 수 없음"""

    def __init__(self, skill_id: str):
        super().__init__(
            message=f"Skill not found: {skill_id}",
            code="SKILL_NOT_FOUND",
            details={"skill_id": skill_id},
        )


class SkillLoadError(SkillError):
    """스킬 로드 실패"""

    def __init__(self, skill_id: str, reason: str):
        super().__init__(
            message=f"Failed to load skill {skill_id}: {reason}",
            code="SKILL_LOAD_ERROR",
            details={"skill_id": skill_id, "reason": reason},
        )


class AgentError(HAESError):
    """에이전트 관련 오류 기본 클래스"""

    def __init__(
        self,
        message: str,
        code: str = "AGENT_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class AgentNotFoundError(AgentError):
    """에이전트를 찾을 수 없음"""

    def __init__(self, agent_id: str):
        super().__init__(
            message=f"Agent not found: {agent_id}",
            code="AGENT_NOT_FOUND",
            details={"agent_id": agent_id},
        )


class AgentExecutionError(AgentError):
    """에이전트 실행 오류"""

    def __init__(self, agent_id: str, reason: str):
        super().__init__(
            message=f"Agent execution failed: {agent_id} - {reason}",
            code="AGENT_EXECUTION_ERROR",
            details={"agent_id": agent_id, "reason": reason},
        )


# =========================================================================
# LLM 관련 예외
# =========================================================================


class LLMError(HAESError):
    """LLM 관련 오류 기본 클래스"""

    def __init__(
        self,
        message: str,
        code: str = "LLM_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class LLMConnectionError(LLMError):
    """LLM 연결 오류"""

    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"Failed to connect to LLM provider {provider}: {reason}",
            code="LLM_CONNECTION_ERROR",
            details={"provider": provider, "reason": reason},
        )


class LLMRateLimitError(LLMError):
    """LLM 속도 제한"""

    def __init__(self, provider: str, retry_after: Optional[int] = None):
        super().__init__(
            message=f"Rate limit exceeded for {provider}",
            code="LLM_RATE_LIMIT",
            details={"provider": provider, "retry_after": retry_after},
        )


class LLMTimeoutError(LLMError):
    """LLM 타임아웃"""

    def __init__(self, provider: str, timeout_seconds: float):
        super().__init__(
            message=f"LLM request timed out after {timeout_seconds}s",
            code="LLM_TIMEOUT",
            details={"provider": provider, "timeout_seconds": timeout_seconds},
        )


class LLMResponseError(LLMError):
    """LLM 응답 오류"""

    def __init__(self, provider: str, reason: str, raw_response: Optional[str] = None):
        super().__init__(
            message=f"Invalid LLM response from {provider}: {reason}",
            code="LLM_RESPONSE_ERROR",
            details={
                "provider": provider,
                "reason": reason,
                "raw_response": raw_response[:500] if raw_response else None,
            },
        )


# =========================================================================
# RAG 관련 예외
# =========================================================================


class RAGError(HAESError):
    """RAG 관련 오류 기본 클래스"""

    def __init__(
        self,
        message: str,
        code: str = "RAG_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class RAGIndexError(RAGError):
    """RAG 인덱싱 오류"""

    def __init__(self, reason: str, document_id: Optional[str] = None):
        super().__init__(
            message=f"RAG indexing failed: {reason}",
            code="RAG_INDEX_ERROR",
            details={"reason": reason, "document_id": document_id},
        )


class RAGSearchError(RAGError):
    """RAG 검색 오류"""

    def __init__(self, reason: str, query: Optional[str] = None):
        super().__init__(
            message=f"RAG search failed: {reason}",
            code="RAG_SEARCH_ERROR",
            details={"reason": reason, "query": query[:200] if query else None},
        )


# =========================================================================
# 보안 관련 예외
# =========================================================================


class SecurityError(HAESError):
    """보안 관련 오류 기본 클래스"""

    def __init__(
        self,
        message: str,
        code: str = "SECURITY_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class PromptInjectionError(SecurityError):
    """프롬프트 인젝션 감지"""

    def __init__(self, query: str, risk_score: float):
        super().__init__(
            message="Potential prompt injection detected",
            code="PROMPT_INJECTION",
            details={
                "risk_score": risk_score,
                "query_preview": query[:100] + "..." if len(query) > 100 else query,
            },
        )


class RateLimitExceededError(SecurityError):
    """요청 속도 제한 초과"""

    def __init__(self, limit: int, window_seconds: int, retry_after: int):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window_seconds}s",
            code="RATE_LIMIT_EXCEEDED",
            details={
                "limit": limit,
                "window_seconds": window_seconds,
                "retry_after": retry_after,
            },
        )


# =========================================================================
# 피드백/진화 관련 예외
# =========================================================================


class FeedbackError(HAESError):
    """피드백 관련 오류"""

    def __init__(
        self,
        message: str,
        code: str = "FEEDBACK_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class NoRecentChatError(FeedbackError):
    """최근 채팅 없음 (피드백 제출 불가)"""

    def __init__(self):
        super().__init__(
            message="No recent chat to provide feedback for",
            code="NO_RECENT_CHAT",
        )


class InvalidFeedbackScoreError(FeedbackError):
    """잘못된 피드백 점수"""

    def __init__(self, score: int, min_score: int = 1, max_score: int = 5):
        super().__init__(
            message=f"Invalid feedback score: {score}. Must be between {min_score} and {max_score}",
            code="INVALID_FEEDBACK_SCORE",
            details={"score": score, "min": min_score, "max": max_score},
        )


# =========================================================================
# 영속성 관련 예외
# =========================================================================


class PersistenceError(HAESError):
    """영속성 관련 오류 기본 클래스"""

    def __init__(
        self,
        message: str,
        code: str = "PERSISTENCE_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class DataSaveError(PersistenceError):
    """데이터 저장 오류"""

    def __init__(self, filepath: str, reason: str):
        super().__init__(
            message=f"Failed to save data to {filepath}: {reason}",
            code="DATA_SAVE_ERROR",
            details={"filepath": filepath, "reason": reason},
        )


class DataLoadError(PersistenceError):
    """데이터 로드 오류"""

    def __init__(self, filepath: str, reason: str):
        super().__init__(
            message=f"Failed to load data from {filepath}: {reason}",
            code="DATA_LOAD_ERROR",
            details={"filepath": filepath, "reason": reason},
        )


class DataCorruptedError(PersistenceError):
    """데이터 손상"""

    def __init__(self, filepath: str, reason: str):
        super().__init__(
            message=f"Data file corrupted: {filepath}",
            code="DATA_CORRUPTED",
            details={"filepath": filepath, "reason": reason},
        )
