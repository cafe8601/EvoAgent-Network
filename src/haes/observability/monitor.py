"""
HAES System Monitor - 시스템 모니터링

실시간 이벤트 스트리밍 및 상태 감시
17-observability SKILL 기반
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, AsyncGenerator
from enum import Enum
from loguru import logger

from haes.observability.tracer import HAESTracer, Trace, Span, SpanKind, SpanStatus, get_tracer
from haes.observability.metrics import MetricsCollector, get_metrics


class EventType(Enum):
    """이벤트 유형"""
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    CHAT_START = "chat_start"
    CHAT_END = "chat_end"
    ROUTING_DECISION = "routing_decision"
    SKILL_LOAD = "skill_load"
    AGENT_CALL = "agent_call"
    LLM_CALL = "llm_call"
    FEEDBACK = "feedback"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class MonitorEvent:
    """모니터 이벤트"""
    event_id: str
    event_type: EventType
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "data": self.data,
            "severity": self.severity,
        }
    
    def to_sse(self) -> str:
        """Server-Sent Events 형식"""
        import json
        return f"data: {json.dumps(self.to_dict())}\n\n"


class SystemMonitor:
    """
    시스템 모니터
    
    실시간 이벤트 스트리밍 및 시스템 상태 감시
    
    기능:
    - 실시간 이벤트 스트리밍 (SSE)
    - 시스템 상태 모니터링
    - 알림 및 경고
    """
    
    def __init__(
        self,
        tracer: Optional[HAESTracer] = None,
        metrics: Optional[MetricsCollector] = None,
        max_events: int = 500,
    ):
        """
        Args:
            tracer: 트레이서 (없으면 전역 사용)
            metrics: 메트릭 수집기 (없으면 전역 사용)
            max_events: 유지할 최대 이벤트 수
        """
        self.tracer = tracer or get_tracer()
        self.metrics = metrics or get_metrics()
        self.max_events = max_events
        
        self._events: List[MonitorEvent] = []
        self._event_counter = 0
        self._subscribers: List[asyncio.Queue] = []
        self._running = False
        
        # 트레이서 콜백 등록
        self._setup_tracer_callbacks()
        
        logger.info("SystemMonitor initialized")
    
    def _setup_tracer_callbacks(self) -> None:
        """트레이서 콜백 설정"""
        def on_trace_end(trace: Trace):
            self._emit_event(
                EventType.CHAT_END,
                {
                    "trace_id": trace.trace_id,
                    "name": trace.name,
                    "duration_ms": trace.duration_ms,
                    "total_spans": len(trace.spans),
                    "status": trace.status.value,
                },
                severity="info" if trace.status == SpanStatus.SUCCESS else "error",
            )
        
        def on_span_end(span: Span):
            event_map = {
                SpanKind.ROUTING: EventType.ROUTING_DECISION,
                SpanKind.SKILL_LOAD: EventType.SKILL_LOAD,
                SpanKind.AGENT_CALL: EventType.AGENT_CALL,
                SpanKind.LLM_CALL: EventType.LLM_CALL,
            }
            
            event_type = event_map.get(span.kind)
            if event_type:
                self._emit_event(
                    event_type,
                    {
                        "span_id": span.span_id,
                        "name": span.name,
                        "duration_ms": span.duration_ms,
                        "status": span.status.value,
                        "inputs": span.inputs,
                        "outputs": span.outputs,
                    },
                    severity="info" if span.status == SpanStatus.SUCCESS else "error",
                )
        
        self.tracer.on_trace_end(on_trace_end)
        self.tracer.on_span_end(on_span_end)
    
    def _emit_event(
        self,
        event_type: EventType,
        data: Dict,
        severity: str = "info",
    ) -> MonitorEvent:
        """이벤트 발생"""
        self._event_counter += 1
        event = MonitorEvent(
            event_id=f"evt_{self._event_counter:06d}",
            event_type=event_type,
            data=data,
            severity=severity,
        )
        
        self._events.append(event)
        
        # 최대 개수 제한
        if len(self._events) > self.max_events:
            self._events = self._events[-self.max_events:]
        
        # 구독자에게 알림
        for queue in self._subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass
        
        return event
    
    def emit(
        self,
        event_type: EventType,
        data: Dict,
        severity: str = "info",
    ) -> MonitorEvent:
        """외부에서 이벤트 발생"""
        return self._emit_event(event_type, data, severity)
    
    def emit_info(self, message: str, data: Optional[Dict] = None) -> MonitorEvent:
        """정보 이벤트"""
        return self._emit_event(EventType.INFO, {"message": message, **(data or {})}, "info")
    
    def emit_warning(self, message: str, data: Optional[Dict] = None) -> MonitorEvent:
        """경고 이벤트"""
        return self._emit_event(EventType.WARNING, {"message": message, **(data or {})}, "warning")
    
    def emit_error(self, message: str, error: Optional[str] = None, data: Optional[Dict] = None) -> MonitorEvent:
        """에러 이벤트"""
        return self._emit_event(
            EventType.ERROR,
            {"message": message, "error": error, **(data or {})},
            "error",
        )
    
    def emit_chat_start(self, query: str, trace_id: str) -> MonitorEvent:
        """채팅 시작 이벤트"""
        return self._emit_event(
            EventType.CHAT_START,
            {"query": query[:200], "trace_id": trace_id},
            "info",
        )
    
    def emit_feedback(self, score: int, mode: str, query: str) -> MonitorEvent:
        """피드백 이벤트"""
        self.metrics.record_feedback(score, mode)
        return self._emit_event(
            EventType.FEEDBACK,
            {"score": score, "mode": mode, "query": query[:100]},
            "info",
        )
    
    async def subscribe(self) -> AsyncGenerator[MonitorEvent, None]:
        """이벤트 스트림 구독"""
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.append(queue)
        
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self._subscribers.remove(queue)
    
    async def stream_events(self) -> AsyncGenerator[str, None]:
        """SSE 이벤트 스트림"""
        async for event in self.subscribe():
            yield event.to_sse()
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        severity: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[MonitorEvent]:
        """이벤트 조회"""
        events = self._events
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        return events[-(limit + offset):-offset or None][::-1]
    
    def get_status(self) -> Dict:
        """시스템 상태 조회"""
        tracer_stats = self.tracer.get_stats()
        metrics_stats = self.metrics.get_stats()
        dashboard = self.metrics.get_dashboard_data()
        
        # 최근 에러
        recent_errors = self.get_events(severity="error", limit=5)
        
        # 상태 계산
        error_rate = tracer_stats.get("error_rate", 0)
        if error_rate > 0.1:
            status = "degraded"
        elif error_rate > 0.3:
            status = "critical"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "timestamp": time.time(),
            "uptime_seconds": time.time() - (self._events[0].timestamp if self._events else time.time()),
            "tracer": tracer_stats,
            "metrics": dashboard["overview"],
            "recent_errors": [e.to_dict() for e in recent_errors],
            "subscribers_count": len(self._subscribers),
            "total_events": len(self._events),
        }
    
    def get_live_dashboard(self) -> Dict:
        """실시간 대시보드 데이터"""
        status = self.get_status()
        tracer_stats = self.tracer.get_stats()
        recent_traces = self.tracer.get_traces(limit=10)
        
        # 최근 스팬별 통계
        span_breakdown = tracer_stats.get("span_breakdown", {})
        
        return {
            "status": status["status"],
            "overview": status["metrics"],
            "span_breakdown": span_breakdown,
            "recent_traces": [
                {
                    "trace_id": t.trace_id,
                    "name": t.name,
                    "duration_ms": round(t.duration_ms, 2),
                    "status": t.status.value,
                    "spans_count": len(t.spans),
                    "timestamp": t.start_time,
                }
                for t in recent_traces
            ],
            "recent_events": [e.to_dict() for e in self.get_events(limit=20)],
        }
    
    def get_skill_stats(self) -> Dict:
        """스킬별 통계"""
        result = {}
        
        for span in self.tracer.get_recent_spans(SpanKind.SKILL_LOAD, limit=100):
            skill_id = span.inputs.get("skill_id", "unknown")
            if skill_id not in result:
                result[skill_id] = {
                    "count": 0,
                    "total_duration_ms": 0,
                    "avg_duration_ms": 0,
                    "errors": 0,
                }
            result[skill_id]["count"] += 1
            result[skill_id]["total_duration_ms"] += span.duration_ms
            if span.status == SpanStatus.ERROR:
                result[skill_id]["errors"] += 1
        
        # 평균 계산
        for skill_id, stats in result.items():
            if stats["count"] > 0:
                stats["avg_duration_ms"] = round(stats["total_duration_ms"] / stats["count"], 2)
        
        return result
    
    def get_agent_stats(self) -> Dict:
        """에이전트별 통계"""
        result = {}
        
        for span in self.tracer.get_recent_spans(SpanKind.AGENT_CALL, limit=100):
            agent_id = span.inputs.get("agent_id", "unknown")
            if agent_id not in result:
                result[agent_id] = {
                    "count": 0,
                    "total_duration_ms": 0,
                    "avg_duration_ms": 0,
                    "errors": 0,
                }
            result[agent_id]["count"] += 1
            result[agent_id]["total_duration_ms"] += span.duration_ms
            if span.status == SpanStatus.ERROR:
                result[agent_id]["errors"] += 1
        
        # 평균 계산
        for agent_id, stats in result.items():
            if stats["count"] > 0:
                stats["avg_duration_ms"] = round(stats["total_duration_ms"] / stats["count"], 2)
        
        return result
    
    def clear(self) -> None:
        """이벤트 초기화"""
        self._events.clear()
        self._event_counter = 0


# 전역 모니터
_global_monitor: Optional[SystemMonitor] = None


def get_monitor() -> SystemMonitor:
    """전역 모니터 반환"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = SystemMonitor()
    return _global_monitor


def set_monitor(monitor: SystemMonitor) -> None:
    """전역 모니터 설정"""
    global _global_monitor
    _global_monitor = monitor
