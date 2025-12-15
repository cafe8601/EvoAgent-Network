"""
HAES Tracer - 실행 추적 시스템

Agent와 Skill 실행을 추적하고 분석하는 트레이서
17-observability/langsmith, phoenix SKILL 기반

Features:
- 계층적 트레이스 구조 (Trace → Span)
- 실행 컨텍스트 자동 수집
- 비동기 지원
"""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from contextlib import contextmanager, asynccontextmanager
from loguru import logger


class SpanKind(Enum):
    """스팬 유형"""
    CHAT = "chat"           # 전체 채팅 요청
    ROUTING = "routing"     # 라우팅 결정
    SKILL_LOAD = "skill"    # SKILL 로드
    AGENT_CALL = "agent"    # 에이전트 호출
    LLM_CALL = "llm"        # LLM API 호출
    MEMORY = "memory"       # 메모리 접근
    TOOL = "tool"           # 도구 실행
    SEARCH = "search"       # 웹 검색


class SpanStatus(Enum):
    """스팬 상태"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class Span:
    """
    실행 단위 (Span)
    
    하나의 작업 단위를 나타내며, 시작/종료 시간, 상태 등을 추적
    """
    span_id: str
    name: str
    kind: SpanKind
    parent_id: Optional[str] = None
    trace_id: Optional[str] = None
    
    # 시간
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # 상태
    status: SpanStatus = SpanStatus.PENDING
    error: Optional[str] = None
    
    # 데이터
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # 자식 스팬
    children: List["Span"] = field(default_factory=list)
    
    def start(self) -> "Span":
        """스팬 시작"""
        self.status = SpanStatus.RUNNING
        self.start_time = time.time()
        return self
    
    def end(self, outputs: Optional[Dict] = None, error: Optional[str] = None) -> "Span":
        """스팬 종료"""
        self.end_time = time.time()
        if outputs:
            self.outputs.update(outputs)
        if error:
            self.status = SpanStatus.ERROR
            self.error = error
        else:
            self.status = SpanStatus.SUCCESS
        return self
    
    @property
    def duration_ms(self) -> float:
        """실행 시간 (ms)"""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return (time.time() - self.start_time) * 1000
    
    def add_attribute(self, key: str, value: Any) -> None:
        """속성 추가"""
        self.attributes[key] = value
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return {
            "span_id": self.span_id,
            "name": self.name,
            "kind": self.kind.value,
            "parent_id": self.parent_id,
            "trace_id": self.trace_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "error": self.error,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "attributes": self.attributes,
            "children_count": len(self.children),
        }


@dataclass
class Trace:
    """
    실행 추적 (Trace)
    
    하나의 요청에 대한 전체 실행 흐름을 나타냄
    """
    trace_id: str
    name: str
    
    # 시간
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # 상태
    status: SpanStatus = SpanStatus.PENDING
    
    # 루트 스팬
    root_span: Optional[Span] = None
    
    # 모든 스팬 (flat list)
    spans: List[Span] = field(default_factory=list)
    
    # 메타데이터
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def end(self, status: Optional[SpanStatus] = None) -> "Trace":
        """트레이스 종료"""
        self.end_time = time.time()
        self.status = status or SpanStatus.SUCCESS
        return self
    
    @property
    def duration_ms(self) -> float:
        """전체 실행 시간 (ms)"""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return (time.time() - self.start_time) * 1000
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "total_spans": len(self.spans),
            "metadata": self.metadata,
            "spans": [s.to_dict() for s in self.spans],
        }
    
    def get_stats(self) -> Dict:
        """트레이스 통계"""
        span_by_kind = {}
        total_duration = 0
        error_count = 0
        
        for span in self.spans:
            kind = span.kind.value
            if kind not in span_by_kind:
                span_by_kind[kind] = {"count": 0, "duration_ms": 0}
            span_by_kind[kind]["count"] += 1
            span_by_kind[kind]["duration_ms"] += span.duration_ms
            total_duration += span.duration_ms
            if span.status == SpanStatus.ERROR:
                error_count += 1
        
        return {
            "total_spans": len(self.spans),
            "total_duration_ms": self.duration_ms,
            "error_count": error_count,
            "span_breakdown": span_by_kind,
        }


class HAESTracer:
    """
    HAES 트레이서
    
    시스템 전체의 실행을 추적하고 분석
    
    사용 예시:
        tracer = HAESTracer()
        
        with tracer.trace("chat_request") as t:
            with tracer.span("routing", SpanKind.ROUTING) as s:
                # 라우팅 로직
                s.add_attribute("query", query)
    """
    
    def __init__(self, max_traces: int = 1000):
        """
        Args:
            max_traces: 유지할 최대 트레이스 수
        """
        self.max_traces = max_traces
        self._traces: List[Trace] = []
        self._current_trace: Optional[Trace] = None
        self._current_span: Optional[Span] = None
        self._span_stack: List[Span] = []
        
        # 콜백
        self._on_trace_end: List[Callable[[Trace], None]] = []
        self._on_span_end: List[Callable[[Span], None]] = []
        
        logger.info("HAESTracer initialized")
    
    @contextmanager
    def trace(self, name: str, metadata: Optional[Dict] = None):
        """
        트레이스 컨텍스트 매니저
        
        Args:
            name: 트레이스 이름
            metadata: 메타데이터
        """
        trace_id = str(uuid.uuid4())[:8]
        trace = Trace(
            trace_id=trace_id,
            name=name,
            metadata=metadata or {},
        )
        
        self._current_trace = trace
        self._traces.append(trace)
        
        # 최대 개수 제한
        if len(self._traces) > self.max_traces:
            self._traces = self._traces[-self.max_traces:]
        
        try:
            yield trace
            trace.end(SpanStatus.SUCCESS)
        except Exception as e:
            trace.end(SpanStatus.ERROR)
            raise
        finally:
            self._current_trace = None
            for callback in self._on_trace_end:
                try:
                    callback(trace)
                except Exception as e:
                    logger.error(f"Trace callback error: {e}")
    
    @contextmanager
    def span(
        self,
        name: str,
        kind: SpanKind,
        inputs: Optional[Dict] = None,
        attributes: Optional[Dict] = None,
    ):
        """
        스팬 컨텍스트 매니저
        
        Args:
            name: 스팬 이름
            kind: 스팬 유형
            inputs: 입력 데이터
            attributes: 속성
        """
        span_id = str(uuid.uuid4())[:8]
        parent_id = self._current_span.span_id if self._current_span else None
        trace_id = self._current_trace.trace_id if self._current_trace else None
        
        span = Span(
            span_id=span_id,
            name=name,
            kind=kind,
            parent_id=parent_id,
            trace_id=trace_id,
            inputs=inputs or {},
            attributes=attributes or {},
        )
        span.start()
        
        # 스팬 스택 관리
        if self._current_span:
            self._current_span.children.append(span)
        self._span_stack.append(span)
        self._current_span = span
        
        # 트레이스에 추가
        if self._current_trace:
            self._current_trace.spans.append(span)
            if not self._current_trace.root_span:
                self._current_trace.root_span = span
        
        try:
            yield span
            span.end()
        except Exception as e:
            span.end(error=str(e))
            raise
        finally:
            self._span_stack.pop()
            self._current_span = self._span_stack[-1] if self._span_stack else None
            for callback in self._on_span_end:
                try:
                    callback(span)
                except Exception as e:
                    logger.error(f"Span callback error: {e}")
    
    @asynccontextmanager
    async def async_trace(self, name: str, metadata: Optional[Dict] = None):
        """비동기 트레이스 컨텍스트"""
        with self.trace(name, metadata) as t:
            yield t
    
    @asynccontextmanager
    async def async_span(
        self,
        name: str,
        kind: SpanKind,
        inputs: Optional[Dict] = None,
        attributes: Optional[Dict] = None,
    ):
        """비동기 스팬 컨텍스트"""
        with self.span(name, kind, inputs, attributes) as s:
            yield s
    
    def record_span(
        self,
        name: str,
        kind: SpanKind,
        inputs: Dict,
        outputs: Dict,
        duration_ms: float,
        error: Optional[str] = None,
    ) -> Span:
        """
        완료된 스팬 직접 기록
        
        이미 완료된 작업을 기록할 때 사용
        """
        span = Span(
            span_id=str(uuid.uuid4())[:8],
            name=name,
            kind=kind,
            trace_id=self._current_trace.trace_id if self._current_trace else None,
            inputs=inputs,
            outputs=outputs,
            status=SpanStatus.ERROR if error else SpanStatus.SUCCESS,
            error=error,
        )
        span.start_time = time.time() - duration_ms / 1000
        span.end_time = time.time()
        
        if self._current_trace:
            self._current_trace.spans.append(span)
        
        return span
    
    def on_trace_end(self, callback: Callable[[Trace], None]) -> None:
        """트레이스 종료 콜백 등록"""
        self._on_trace_end.append(callback)
    
    def on_span_end(self, callback: Callable[[Span], None]) -> None:
        """스팬 종료 콜백 등록"""
        self._on_span_end.append(callback)
    
    def get_traces(self, limit: int = 100, offset: int = 0) -> List[Trace]:
        """트레이스 목록"""
        return self._traces[-(limit + offset):-offset or None][::-1]
    
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """트레이스 조회"""
        for trace in self._traces:
            if trace.trace_id == trace_id:
                return trace
        return None
    
    def get_recent_spans(self, kind: Optional[SpanKind] = None, limit: int = 50) -> List[Span]:
        """최근 스팬 조회"""
        all_spans = []
        for trace in self._traces[::-1]:
            for span in trace.spans:
                if kind is None or span.kind == kind:
                    all_spans.append(span)
                    if len(all_spans) >= limit:
                        return all_spans
        return all_spans
    
    def get_stats(self) -> Dict:
        """전체 트레이싱 통계"""
        total_spans = 0
        span_by_kind = {}
        error_count = 0
        total_duration = 0
        
        for trace in self._traces:
            for span in trace.spans:
                total_spans += 1
                kind = span.kind.value
                if kind not in span_by_kind:
                    span_by_kind[kind] = {"count": 0, "duration_ms": 0, "errors": 0}
                span_by_kind[kind]["count"] += 1
                span_by_kind[kind]["duration_ms"] += span.duration_ms
                if span.status == SpanStatus.ERROR:
                    span_by_kind[kind]["errors"] += 1
                    error_count += 1
                total_duration += span.duration_ms
        
        return {
            "total_traces": len(self._traces),
            "total_spans": total_spans,
            "error_count": error_count,
            "error_rate": error_count / total_spans if total_spans else 0,
            "avg_duration_ms": total_duration / total_spans if total_spans else 0,
            "span_breakdown": span_by_kind,
        }
    
    def clear(self) -> None:
        """트레이스 초기화"""
        self._traces.clear()
        self._current_trace = None
        self._current_span = None
        self._span_stack.clear()


# 전역 트레이서
_global_tracer: Optional[HAESTracer] = None


def get_tracer() -> HAESTracer:
    """전역 트레이서 반환"""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = HAESTracer()
    return _global_tracer


def set_tracer(tracer: HAESTracer) -> None:
    """전역 트레이서 설정"""
    global _global_tracer
    _global_tracer = tracer
