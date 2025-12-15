"""
Spec-Driven Task Planner - 복잡한 요청 작업 분해

24-spec-driven-planner SKILL 기반 구현

복잡한 요청을 분석하고:
1. Assess: SDD 필요 여부 판단
2. Specify: 요구사항 정의
3. Plan: 기술 계획 수립
4. Tasks: 실행 가능한 태스크로 분해
5. Workflow: 적합한 워크플로우 선택
6. Agents: 필요한 에이전트 할당

작동 기준:
- 복잡도 >= 0.5: 스펙 기반 계획 활성화
- 복잡도 < 0.5: 기존 라우팅 사용
"""

import json
import hashlib
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger


class WorkflowType(Enum):
    """워크플로우 유형"""
    SIMPLE_QUERY = "simple_query"        # 단순 질문 - 즉시 응답
    SKILL_LOOKUP = "skill_lookup"        # 스킬 조회 - SKILL 기반 응답
    SINGLE_TASK = "single_task"          # 단일 작업 - 한 에이전트
    SEQUENTIAL = "sequential"            # 순차 실행 - 에이전트 체인
    PARALLEL = "parallel"                # 병렬 실행 - 동시 작업
    SPEC_DRIVEN = "spec_driven"          # 스펙 기반 - 전체 계획 수립


class TaskStatus(Enum):
    """태스크 상태"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class TaskCategory(Enum):
    """태스크 카테고리"""
    INVESTIGATION = "investigation"      # 분석/조사
    IMPLEMENTATION = "implementation"    # 구현
    REFACTORING = "refactoring"         # 리팩토링
    TESTING = "testing"                  # 테스트
    DOCUMENTATION = "documentation"      # 문서화
    DECISION = "decision"                # 의사결정
    RESEARCH = "research"                # 리서치


@dataclass
class Task:
    """실행 가능한 태스크"""
    id: str
    title: str
    description: str
    category: TaskCategory
    status: TaskStatus = TaskStatus.PENDING
    agent_id: Optional[str] = None
    skill_ids: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)
    estimated_minutes: int = 15
    priority: int = 1  # 1=높음, 2=보통, 3=낮음
    output: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "status": self.status.value,
            "agent_id": self.agent_id,
            "skill_ids": self.skill_ids,
            "dependencies": self.dependencies,
            "blocked_by": self.blocked_by,
            "estimated_minutes": self.estimated_minutes,
            "priority": self.priority,
            "output": self.output,
        }


@dataclass
class Phase:
    """실행 단계"""
    id: str
    name: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    @property
    def total_tasks(self) -> int:
        return len(self.tasks)
    
    @property
    def completed_tasks(self) -> int:
        return sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
    
    @property
    def progress(self) -> float:
        if not self.tasks:
            return 0.0
        return self.completed_tasks / self.total_tasks
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": [t.to_dict() for t in self.tasks],
            "dependencies": self.dependencies,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "progress": self.progress,
        }


@dataclass
class ExecutionPlan:
    """실행 계획"""
    id: str
    query: str
    workflow: WorkflowType
    phases: List[Phase] = field(default_factory=list)
    selected_agents: List[str] = field(default_factory=list)
    selected_skills: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    estimated_time_minutes: int = 0
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        hash_input = f"{self.query[:50]}_{self.created_at}"
        return f"plan-{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"
    
    @property
    def total_tasks(self) -> int:
        return sum(p.total_tasks for p in self.phases)
    
    @property
    def completed_tasks(self) -> int:
        return sum(p.completed_tasks for p in self.phases)
    
    @property
    def progress(self) -> float:
        if not self.phases:
            return 0.0
        total = self.total_tasks
        if total == 0:
            return 0.0
        return self.completed_tasks / total
    
    def get_next_tasks(self) -> List[Task]:
        """실행 가능한 다음 태스크 반환"""
        ready_tasks = []
        completed_ids = {t.id for p in self.phases for t in p.tasks 
                        if t.status == TaskStatus.COMPLETED}
        
        for phase in self.phases:
            for task in phase.tasks:
                if task.status != TaskStatus.PENDING:
                    continue
                
                # 의존성 확인
                deps_satisfied = all(dep in completed_ids for dep in task.blocked_by)
                if deps_satisfied:
                    ready_tasks.append(task)
        
        # 우선순위 정렬
        ready_tasks.sort(key=lambda t: (t.priority, t.estimated_minutes))
        return ready_tasks
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query": self.query,
            "workflow": self.workflow.value,
            "phases": [p.to_dict() for p in self.phases],
            "selected_agents": self.selected_agents,
            "selected_skills": self.selected_skills,
            "complexity_score": self.complexity_score,
            "estimated_time_minutes": self.estimated_time_minutes,
            "created_at": self.created_at,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "progress": self.progress,
        }


class SpecDrivenPlanner:
    """
    스펙 기반 태스크 플래너
    
    복잡한 요청을 분석하고 실행 계획 수립
    
    사용 예시:
        planner = SpecDrivenPlanner(skill_store, agent_pool)
        
        # 계획 생성
        plan = await planner.create_plan(
            query="RAG 시스템 구축하고 API 만들고 테스트까지 해줘",
            complexity_score=0.7
        )
        
        # 다음 실행할 태스크 가져오기
        next_tasks = plan.get_next_tasks()
        
        # 워크플로우 유형 확인
        print(f"Workflow: {plan.workflow.value}")
    """
    
    # 워크플로우 선택 임계값
    THRESHOLDS = {
        "simple_query": 0.2,     # 복잡도 0~0.2: 단순 질문
        "skill_lookup": 0.35,   # 복잡도 0.2~0.35: 스킬 조회
        "single_task": 0.5,     # 복잡도 0.35~0.5: 단일 작업
        "multi_task": 0.7,      # 복잡도 0.5~0.7: 다중 작업
        "spec_driven": 1.0,     # 복잡도 0.7~1.0: 스펙 기반 계획
    }
    
    # 에이전트 역할 매핑
    AGENT_ROLES = {
        "architect": ["system-architect", "solution-architect", "api-designer"],
        "backend": ["backend-developer", "api-developer", "python-pro"],
        "frontend": ["frontend-developer", "ui-designer", "react-developer"],
        "data": ["data-analyst", "data-scientist", "ml-engineer"],
        "devops": ["devops-engineer", "sre-engineer", "deployment-engineer"],
        "qa": ["qa-expert", "test-engineer", "security-reviewer"],
        "docs": ["tech-writer", "documentation-engineer", "api-documenter"],
    }
    
    # 태스크 키워드 매핑
    TASK_KEYWORDS = {
        TaskCategory.INVESTIGATION: ["분석", "조사", "확인", "검토", "살펴", "analyze"],
        TaskCategory.IMPLEMENTATION: ["구현", "만들", "작성", "개발", "build", "create"],
        TaskCategory.REFACTORING: ["리팩", "개선", "최적화", "수정", "refactor"],
        TaskCategory.TESTING: ["테스트", "검증", "확인", "test", "verify"],
        TaskCategory.DOCUMENTATION: ["문서", "doc", "README", "설명"],
        TaskCategory.RESEARCH: ["연구", "찾아", "search", "research"],
        TaskCategory.DECISION: ["선택", "결정", "decide", "choose"],
    }
    
    def __init__(
        self,
        skill_store: Optional[Any] = None,
        agent_pool: Optional[Any] = None,
        llm_client: Optional[Any] = None,
    ):
        self.skill_store = skill_store
        self.agent_pool = agent_pool
        self.llm_client = llm_client
        self._plans: Dict[str, ExecutionPlan] = {}
    
    async def create_plan(
        self,
        query: str,
        complexity_score: float,
        matched_skills: Optional[List[str]] = None,
        is_parallel: bool = False,
        is_collaborative: bool = False,
    ) -> ExecutionPlan:
        """
        실행 계획 생성
        
        Args:
            query: 사용자 요청
            complexity_score: 복잡도 점수 (0~1)
            matched_skills: 매칭된 스킬 목록
            is_parallel: 병렬 실행 가능 여부
            is_collaborative: 협업 필요 여부
        
        Returns:
            ExecutionPlan
        """
        matched_skills = matched_skills or []
        
        # 1. 워크플로우 선택
        workflow = self._select_workflow(
            complexity_score, is_parallel, is_collaborative
        )
        
        logger.info(f"Selected workflow: {workflow.value} (complexity={complexity_score:.2f})")
        
        # 2. 요청 분해 (태스크 추출)
        tasks = self._extract_tasks(query, matched_skills)
        
        # 3. 에이전트 할당
        agents = self._assign_agents(tasks, query)
        
        # 4. 단계 구성
        phases = self._create_phases(tasks, workflow)
        
        # 5. 의존성 분석
        self._analyze_dependencies(phases)
        
        # 6. 시간 추정
        estimated_time = sum(t.estimated_minutes for p in phases for t in p.tasks)
        
        # 7. 계획 생성
        plan = ExecutionPlan(
            id="",
            query=query,
            workflow=workflow,
            phases=phases,
            selected_agents=agents,
            selected_skills=matched_skills,
            complexity_score=complexity_score,
            estimated_time_minutes=estimated_time,
        )
        
        # 캐시 저장
        self._plans[plan.id] = plan
        
        logger.info(
            f"Plan created: {plan.id} | "
            f"{plan.total_tasks} tasks | "
            f"~{estimated_time} min | "
            f"Agents: {agents}"
        )
        
        return plan
    
    def _select_workflow(
        self,
        complexity: float,
        is_parallel: bool,
        is_collaborative: bool,
    ) -> WorkflowType:
        """워크플로우 선택"""
        # 병렬 실행 가능
        if is_parallel and complexity >= 0.5:
            return WorkflowType.PARALLEL
        
        # 협업 필요
        if is_collaborative and complexity >= 0.5:
            return WorkflowType.SEQUENTIAL
        
        # 복잡도 기반 선택
        if complexity >= self.THRESHOLDS["multi_task"]:
            return WorkflowType.SPEC_DRIVEN
        elif complexity >= self.THRESHOLDS["single_task"]:
            return WorkflowType.SEQUENTIAL
        elif complexity >= self.THRESHOLDS["skill_lookup"]:
            return WorkflowType.SINGLE_TASK
        elif complexity >= self.THRESHOLDS["simple_query"]:
            return WorkflowType.SKILL_LOOKUP
        else:
            return WorkflowType.SIMPLE_QUERY
    
    def _extract_tasks(
        self,
        query: str,
        skills: List[str],
    ) -> List[Task]:
        """요청에서 태스크 추출"""
        tasks = []
        query_lower = query.lower()
        
        # 연결어로 분리 ("하고", "그리고", "다음에")
        delimiters = ["하고", "그리고", "그 다음", "그다음", "다음에", "그 후", "후에", " and ", ", "]
        segments = [query]
        
        for delim in delimiters:
            new_segments = []
            for segment in segments:
                parts = segment.split(delim)
                new_segments.extend([p.strip() for p in parts if p.strip()])
            segments = new_segments
        
        # 각 세그먼트를 태스크로 변환
        for i, segment in enumerate(segments):
            category = self._detect_category(segment)
            skill_ids = [s for s in skills if any(
                kw in segment.lower() for kw in s.split("-")
            )] or skills[:1]
            
            task = Task(
                id=f"task-{i+1}",
                title=segment[:100],
                description=segment,
                category=category,
                skill_ids=skill_ids,
                estimated_minutes=self._estimate_time(segment, category),
                priority=1 if i == 0 else 2,
            )
            tasks.append(task)
        
        # 태스크가 없으면 기본 태스크 생성
        if not tasks:
            tasks.append(Task(
                id="task-1",
                title=query[:100],
                description=query,
                category=TaskCategory.INVESTIGATION,
                skill_ids=skills,
                estimated_minutes=15,
            ))
        
        return tasks
    
    def _detect_category(self, text: str) -> TaskCategory:
        """텍스트에서 태스크 카테고리 감지"""
        text_lower = text.lower()
        
        for category, keywords in self.TASK_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return category
        
        return TaskCategory.IMPLEMENTATION
    
    def _estimate_time(self, text: str, category: TaskCategory) -> int:
        """태스크 시간 추정 (분)"""
        base_times = {
            TaskCategory.INVESTIGATION: 10,
            TaskCategory.IMPLEMENTATION: 30,
            TaskCategory.REFACTORING: 20,
            TaskCategory.TESTING: 15,
            TaskCategory.DOCUMENTATION: 15,
            TaskCategory.RESEARCH: 20,
            TaskCategory.DECISION: 5,
        }
        
        base = base_times.get(category, 15)
        
        # 텍스트 길이에 따른 조정
        if len(text) > 100:
            base = int(base * 1.5)
        
        return base
    
    def _assign_agents(self, tasks: List[Task], query: str) -> List[str]:
        """태스크에 에이전트 할당"""
        assigned = []
        query_lower = query.lower()
        
        for task in tasks:
            agent = self._find_best_agent(task, query_lower)
            if agent:
                task.agent_id = agent
                if agent not in assigned:
                    assigned.append(agent)
        
        return assigned
    
    def _find_best_agent(self, task: Task, query: str) -> Optional[str]:
        """태스크에 가장 적합한 에이전트 찾기"""
        # 카테고리 기반 역할 매핑
        category_roles = {
            TaskCategory.INVESTIGATION: "architect",
            TaskCategory.IMPLEMENTATION: "backend",
            TaskCategory.REFACTORING: "backend",
            TaskCategory.TESTING: "qa",
            TaskCategory.DOCUMENTATION: "docs",
            TaskCategory.RESEARCH: "architect",
            TaskCategory.DECISION: "architect",
        }
        
        # 키워드 기반 역할 탐지
        role = category_roles.get(task.category, "backend")
        
        # 쿼리 기반 역할 오버라이드
        if any(kw in query for kw in ["frontend", "ui", "프론트", "화면"]):
            role = "frontend"
        elif any(kw in query for kw in ["ml", "ai", "머신러닝", "모델"]):
            role = "data"
        elif any(kw in query for kw in ["deploy", "배포", "ci/cd", "인프라"]):
            role = "devops"
        
        # 에이전트 선택
        candidates = self.AGENT_ROLES.get(role, ["backend-developer"])
        return candidates[0] if candidates else "backend-developer"
    
    def _create_phases(
        self,
        tasks: List[Task],
        workflow: WorkflowType,
    ) -> List[Phase]:
        """태스크를 단계로 구성"""
        if workflow == WorkflowType.SIMPLE_QUERY:
            # 단일 단계
            return [Phase(
                id="phase-1",
                name="즉시 응답",
                description="단순 질문 처리",
                tasks=tasks,
            )]
        
        if workflow == WorkflowType.PARALLEL:
            # 모든 태스크 병렬
            return [Phase(
                id="phase-1",
                name="병렬 실행",
                description="독립 태스크 동시 실행",
                tasks=tasks,
            )]
        
        if workflow in (WorkflowType.SEQUENTIAL, WorkflowType.SPEC_DRIVEN):
            # 카테고리별 단계 분리
            phases = []
            
            # 조사/분석 단계
            investigation = [t for t in tasks if t.category in (
                TaskCategory.INVESTIGATION, TaskCategory.RESEARCH, TaskCategory.DECISION
            )]
            if investigation:
                phases.append(Phase(
                    id="phase-1",
                    name="분석 단계",
                    description="요구사항 분석 및 조사",
                    tasks=investigation,
                ))
            
            # 구현 단계
            implementation = [t for t in tasks if t.category in (
                TaskCategory.IMPLEMENTATION, TaskCategory.REFACTORING
            )]
            if implementation:
                phases.append(Phase(
                    id=f"phase-{len(phases)+1}",
                    name="구현 단계",
                    description="핵심 기능 구현",
                    tasks=implementation,
                    dependencies=[phases[-1].id] if phases else [],
                ))
            
            # 검증 단계
            testing = [t for t in tasks if t.category in (
                TaskCategory.TESTING, TaskCategory.DOCUMENTATION
            )]
            if testing:
                phases.append(Phase(
                    id=f"phase-{len(phases)+1}",
                    name="검증 단계",
                    description="테스트 및 문서화",
                    tasks=testing,
                    dependencies=[phases[-1].id] if phases else [],
                ))
            
            # 남은 태스크
            remaining = [t for t in tasks if not any(t in p.tasks for p in phases)]
            if remaining:
                phases.append(Phase(
                    id=f"phase-{len(phases)+1}",
                    name="추가 작업",
                    description="기타 태스크",
                    tasks=remaining,
                ))
            
            return phases if phases else [Phase(
                id="phase-1",
                name="실행",
                description="태스크 실행",
                tasks=tasks,
            )]
        
        # 기본: 단일 단계
        return [Phase(
            id="phase-1",
            name="실행",
            description="태스크 실행",
            tasks=tasks,
        )]
    
    def _analyze_dependencies(self, phases: List[Phase]):
        """태스크 의존성 분석 및 설정"""
        for i, phase in enumerate(phases):
            # 이전 단계의 마지막 태스크에 의존
            if i > 0 and phases[i-1].tasks:
                prev_task_ids = [t.id for t in phases[i-1].tasks]
                for task in phase.tasks:
                    if not task.blocked_by:
                        # 이전 단계 완료 후 시작
                        task.blocked_by = prev_task_ids
    
    def get_plan(self, plan_id: str) -> Optional[ExecutionPlan]:
        """계획 조회"""
        return self._plans.get(plan_id)
    
    def get_execution_summary(self, plan: ExecutionPlan) -> str:
        """실행 계획 요약 생성"""
        lines = [
            f"# 실행 계획: {plan.id}",
            f"",
            f"**요청**: {plan.query[:100]}...",
            f"**워크플로우**: {plan.workflow.value}",
            f"**복잡도**: {plan.complexity_score:.2f}",
            f"**예상 시간**: ~{plan.estimated_time_minutes}분",
            f"**진행률**: {plan.progress*100:.0f}% ({plan.completed_tasks}/{plan.total_tasks})",
            f"",
            f"## 단계",
        ]
        
        for phase in plan.phases:
            lines.append(f"")
            lines.append(f"### {phase.name} ({phase.completed_tasks}/{phase.total_tasks})")
            lines.append(f"{phase.description}")
            lines.append(f"")
            
            for task in phase.tasks:
                status_icon = {
                    TaskStatus.COMPLETED: "✅",
                    TaskStatus.IN_PROGRESS: "🔄",
                    TaskStatus.BLOCKED: "🔒",
                    TaskStatus.FAILED: "❌",
                    TaskStatus.PENDING: "⬜",
                }[task.status]
                
                agent = f" [{task.agent_id}]" if task.agent_id else ""
                lines.append(f"- {status_icon} {task.title}{agent}")
        
        lines.append(f"")
        lines.append(f"## 에이전트")
        for agent in plan.selected_agents:
            lines.append(f"- {agent}")
        
        return "\n".join(lines)


# 글로벌 플래너 인스턴스
_planner: Optional[SpecDrivenPlanner] = None


def get_planner() -> SpecDrivenPlanner:
    """글로벌 플래너 반환"""
    global _planner
    if _planner is None:
        _planner = SpecDrivenPlanner()
    return _planner
