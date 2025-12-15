"""
HAES Metrics Collector - 메트릭 수집 시스템

Agent/Skill 성능, 비용, 품질 지표 수집 및 분석
17-observability SKILL 기반
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum
from collections import defaultdict
from loguru import logger


class MetricType(Enum):
    """메트릭 유형"""
    COUNTER = "counter"         # 증가만 가능한 카운터
    GAUGE = "gauge"             # 현재 값
    HISTOGRAM = "histogram"     # 분포
    TIMER = "timer"             # 시간 측정


@dataclass
class Metric:
    """메트릭 데이터"""
    name: str
    type: MetricType
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
        }


@dataclass
class MetricSeries:
    """시계열 메트릭"""
    name: str
    type: MetricType
    values: List[Metric] = field(default_factory=list)
    max_size: int = 1000
    
    def add(self, value: float, labels: Optional[Dict] = None) -> None:
        """값 추가"""
        metric = Metric(
            name=self.name,
            type=self.type,
            value=value,
            labels=labels or {},
        )
        self.values.append(metric)
        
        # 최대 개수 제한
        if len(self.values) > self.max_size:
            self.values = self.values[-self.max_size:]
    
    def get_latest(self, n: int = 1) -> List[Metric]:
        """최근 n개 값"""
        return self.values[-n:]
    
    def get_range(self, start_time: float, end_time: float) -> List[Metric]:
        """시간 범위 조회"""
        return [m for m in self.values if start_time <= m.timestamp <= end_time]
    
    def get_average(self, last_n: Optional[int] = None) -> float:
        """평균값"""
        values = self.values[-last_n:] if last_n else self.values
        if not values:
            return 0.0
        return sum(m.value for m in values) / len(values)
    
    def get_sum(self, last_n: Optional[int] = None) -> float:
        """합계"""
        values = self.values[-last_n:] if last_n else self.values
        return sum(m.value for m in values)
    
    def get_min_max(self, last_n: Optional[int] = None) -> tuple:
        """최소/최대"""
        values = self.values[-last_n:] if last_n else self.values
        if not values:
            return (0.0, 0.0)
        vals = [m.value for m in values]
        return (min(vals), max(vals))


class MetricsCollector:
    """
    메트릭 수집기
    
    다양한 성능/품질 지표 수집 및 분석
    
    수집 메트릭:
    - 실행 횟수 (counter)
    - 응답 시간 (timer)
    - 비용 (gauge)
    - 피드백 점수 (histogram)
    - 에러율 (gauge)
    """
    
    def __init__(self, retention_hours: int = 24):
        """
        Args:
            retention_hours: 데이터 보존 시간
        """
        self.retention_hours = retention_hours
        self._series: Dict[str, MetricSeries] = {}
        self._counters: Dict[str, float] = defaultdict(float)
        
        # 사전 정의 메트릭
        self._init_metrics()
        
        logger.info("MetricsCollector initialized")
    
    def _init_metrics(self) -> None:
        """기본 메트릭 초기화"""
        metrics = [
            # 요청 관련
            ("requests_total", MetricType.COUNTER),
            ("requests_by_mode", MetricType.COUNTER),
            ("request_duration_ms", MetricType.TIMER),
            
            # Skill 관련
            ("skills_used", MetricType.COUNTER),
            ("skill_load_time_ms", MetricType.TIMER),
            
            # Agent 관련
            ("agents_used", MetricType.COUNTER),
            ("agent_call_time_ms", MetricType.TIMER),
            
            # LLM 관련
            ("llm_calls_total", MetricType.COUNTER),
            ("llm_tokens_input", MetricType.COUNTER),
            ("llm_tokens_output", MetricType.COUNTER),
            ("llm_latency_ms", MetricType.TIMER),
            ("llm_cost_usd", MetricType.GAUGE),
            
            # 품질 관련
            ("feedback_score", MetricType.HISTOGRAM),
            ("error_rate", MetricType.GAUGE),
            
            # 시스템 관련
            ("active_traces", MetricType.GAUGE),
            ("memory_usage_mb", MetricType.GAUGE),
        ]
        
        for name, metric_type in metrics:
            self._series[name] = MetricSeries(name, metric_type)
    
    def _get_or_create_series(self, name: str, metric_type: MetricType) -> MetricSeries:
        """시리즈 조회/생성"""
        if name not in self._series:
            self._series[name] = MetricSeries(name, metric_type)
        return self._series[name]
    
    def record(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        메트릭 기록
        
        Args:
            name: 메트릭 이름
            value: 값
            metric_type: 메트릭 유형
            labels: 레이블
        """
        series = self._get_or_create_series(name, metric_type)
        series.add(value, labels)
        
        if metric_type == MetricType.COUNTER:
            key = name
            if labels:
                key += ":" + ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            self._counters[key] += value
    
    def increment(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """카운터 증가"""
        self.record(name, value, MetricType.COUNTER, labels)
    
    def timer(self, name: str, duration_ms: float, labels: Optional[Dict[str, str]] = None) -> None:
        """타이머 기록"""
        self.record(name, duration_ms, MetricType.TIMER, labels)
    
    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """게이지 값 설정"""
        self.record(name, value, MetricType.GAUGE, labels)
    
    # ==================
    # 고수준 기록 메서드
    # ==================
    
    def record_request(
        self,
        mode: str,
        duration_ms: float,
        skills: List[str],
        agents: List[str],
        success: bool = True,
    ) -> None:
        """요청 메트릭 기록"""
        self.increment("requests_total")
        self.increment("requests_by_mode", labels={"mode": mode})
        self.timer("request_duration_ms", duration_ms, labels={"mode": mode})
        
        for skill in skills:
            self.increment("skills_used", labels={"skill": skill})
        
        for agent in agents:
            self.increment("agents_used", labels={"agent": agent})
        
        if not success:
            self.increment("requests_error", labels={"mode": mode})
    
    def record_llm_call(
        self,
        model: str,
        latency_ms: float,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
    ) -> None:
        """LLM 호출 메트릭 기록"""
        labels = {"model": model}
        
        self.increment("llm_calls_total", labels=labels)
        self.timer("llm_latency_ms", latency_ms, labels=labels)
        self.increment("llm_tokens_input", input_tokens, labels=labels)
        self.increment("llm_tokens_output", output_tokens, labels=labels)
        self.gauge("llm_cost_usd", cost_usd, labels=labels)
    
    def record_feedback(self, score: int, mode: str) -> None:
        """피드백 점수 기록"""
        self.record("feedback_score", score, MetricType.HISTOGRAM, labels={"mode": mode})
    
    def record_skill_load(self, skill_id: str, duration_ms: float) -> None:
        """스킬 로드 시간 기록"""
        self.timer("skill_load_time_ms", duration_ms, labels={"skill": skill_id})
    
    def record_agent_call(self, agent_id: str, duration_ms: float, success: bool = True) -> None:
        """에이전트 호출 시간 기록"""
        self.timer("agent_call_time_ms", duration_ms, labels={"agent": agent_id, "success": str(success)})
    
    # ==================
    # 조회 메서드
    # ==================
    
    def get_series(self, name: str) -> Optional[MetricSeries]:
        """시리즈 조회"""
        return self._series.get(name)
    
    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """카운터 값 조회"""
        key = name
        if labels:
            key += ":" + ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return self._counters.get(key, 0.0)
    
    def get_stats(self, last_n: int = 100) -> Dict:
        """전체 통계"""
        stats = {}
        
        for name, series in self._series.items():
            if not series.values:
                continue
            
            stats[name] = {
                "count": len(series.values),
                "latest": series.values[-1].value if series.values else 0,
                "average": series.get_average(last_n),
                "sum": series.get_sum(last_n),
            }
            
            if series.type in (MetricType.TIMER, MetricType.HISTOGRAM):
                min_val, max_val = series.get_min_max(last_n)
                stats[name]["min"] = min_val
                stats[name]["max"] = max_val
        
        return stats
    
    def get_dashboard_data(self) -> Dict:
        """대시보드용 데이터"""
        now = time.time()
        hour_ago = now - 3600
        
        # 시간별 요청 수
        requests_series = self._series.get("requests_total")
        hourly_requests = 0
        if requests_series:
            hourly_data = requests_series.get_range(hour_ago, now)
            hourly_requests = len(hourly_data)
        
        # 평균 응답 시간
        duration_series = self._series.get("request_duration_ms")
        avg_duration = duration_series.get_average(100) if duration_series else 0
        
        # 피드백 점수
        feedback_series = self._series.get("feedback_score")
        avg_feedback = feedback_series.get_average(50) if feedback_series else 0
        
        # 에러율
        total_requests = self.get_counter("requests_total")
        total_errors = self.get_counter("requests_error")
        error_rate = (total_errors / total_requests * 100) if total_requests else 0
        
        return {
            "overview": {
                "total_requests": int(total_requests),
                "hourly_requests": hourly_requests,
                "avg_duration_ms": round(avg_duration, 2),
                "avg_feedback_score": round(avg_feedback, 2),
                "error_rate_pct": round(error_rate, 2),
            },
            "counters": dict(self._counters),
            "timeseries": self._get_timeseries_data(),
        }
    
    def _get_timeseries_data(self, points: int = 60) -> Dict:
        """시계열 차트용 데이터"""
        result = {}
        
        # 주요 메트릭만 시계열로
        for name in ["requests_total", "request_duration_ms", "feedback_score", "llm_latency_ms"]:
            series = self._series.get(name)
            if series and series.values:
                result[name] = [
                    {"timestamp": m.timestamp, "value": m.value}
                    for m in series.get_latest(points)
                ]
        
        return result
    
    def clear(self) -> None:
        """메트릭 초기화"""
        for series in self._series.values():
            series.values.clear()
        self._counters.clear()


# 전역 메트릭 수집기
_global_collector: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """전역 메트릭 수집기 반환"""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector


def set_metrics(collector: MetricsCollector) -> None:
    """전역 메트릭 수집기 설정"""
    global _global_collector
    _global_collector = collector
