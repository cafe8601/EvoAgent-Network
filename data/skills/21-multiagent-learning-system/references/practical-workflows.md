# Practical Workflow Examples

실제 프로덕션에서 사용 가능한 멀티에이전트 워크플로우 예제 모음입니다.

---

## Example 1: 병렬 코드 리뷰 (3-5x 속도 향상)

**시나리오**: 여러 AI 모델로 코드를 동시 검토하여 합의 기반 피드백 생성

```python
import asyncio
from dataclasses import dataclass

@dataclass
class ReviewResult:
    model: str
    issues: list
    score: float
    recommendations: list

class ParallelCodeReview:
    """
    3개 모델이 동시에 코드 리뷰
    - Claude: 아키텍처 + 베스트 프랙티스
    - GPT-4: 보안 + 엣지 케이스
    - Gemini: 성능 + 최적화
    """
    
    async def review(self, code: str) -> dict:
        # Message 1: 준비
        context_file = "ai-docs/code-to-review.md"
        await self.write_context(context_file, code)
        
        # Message 2: 병렬 실행 (핵심!)
        reviews = await asyncio.gather(
            self.claude_review(context_file),
            self.gpt4_review(context_file),
            self.gemini_review(context_file),
        )
        
        # Message 3: 합의 분석
        consensus = self.analyze_consensus(reviews)
        
        # Message 4: 결과 정리
        return {
            "individual_reviews": reviews,
            "consensus_issues": consensus.unanimous_issues,
            "priority_fixes": consensus.prioritized_fixes,
            "overall_score": consensus.average_score,
            "speedup": "3x (15min → 5min)"
        }
    
    async def claude_review(self, file: str) -> ReviewResult:
        prompt = f"""
        Review code in {file} for:
        1. Architecture patterns
        2. Best practices
        3. Maintainability
        
        Return JSON: {{"issues": [...], "score": 0-10, "recommendations": [...]}}
        """
        result = await self.agents["claude"].execute(prompt)
        return ReviewResult(model="claude", **result)
    
    async def gpt4_review(self, file: str) -> ReviewResult:
        prompt = f"""
        Security-focused review of {file}:
        1. Input validation
        2. SQL injection risks
        3. Authentication issues
        4. Edge cases
        """
        result = await self.agents["gpt4"].execute(prompt)
        return ReviewResult(model="gpt4", **result)
    
    async def gemini_review(self, file: str) -> ReviewResult:
        prompt = f"""
        Performance review of {file}:
        1. Algorithm complexity
        2. Memory usage
        3. Optimization opportunities
        """
        result = await self.agents["gemini"].execute(prompt)
        return ReviewResult(model="gemini", **result)
    
    def analyze_consensus(self, reviews: list) -> dict:
        """3개 모델의 합의 분석"""
        all_issues = []
        for r in reviews:
            all_issues.extend(r.issues)
        
        # 2개 이상 모델이 지적한 이슈 = 우선 수정
        issue_counts = {}
        for issue in all_issues:
            key = issue.get("type", str(issue))
            issue_counts[key] = issue_counts.get(key, 0) + 1
        
        unanimous = [k for k, v in issue_counts.items() if v >= 2]
        
        return {
            "unanimous_issues": unanimous,
            "prioritized_fixes": unanimous[:5],  # Top 5
            "average_score": sum(r.score for r in reviews) / len(reviews)
        }

# 사용 예시
async def main():
    reviewer = ParallelCodeReview()
    
    code = open("src/auth.py").read()
    result = await reviewer.review(code)
    
    print(f"✅ 리뷰 완료 ({result['speedup']})")
    print(f"전체 점수: {result['overall_score']}/10")
    print(f"합의된 이슈: {len(result['consensus_issues'])}개")
```

**비용 분석**:
- 순차 실행: 3 모델 × 10초 = 30초
- 병렬 실행: max(10초, 10초, 10초) = 10초
- **속도 향상: 3x**
- **비용: 동일** (호출 횟수 같음)

---

## Example 2: 비용 최적화된 순차 파이프라인

**시나리오**: 연구 보고서 생성 (데이터 → 분석 → 작성 → 편집)

```python
class CostOptimizedResearchPipeline:
    """
    비용 최적화된 연구 파이프라인
    - 저렴한 모델로 초안 생성
    - 고급 모델은 최종 검토에만 사용
    """
    
    def __init__(self):
        # 모델 티어링으로 비용 최적화
        self.models = {
            "fast": "gemini-1.5-flash",     # $0.002/call
            "balanced": "claude-3-5-sonnet", # $0.05/call
            "premium": "claude-3-opus"       # $0.30/call
        }
    
    def execute(self, topic: str) -> dict:
        costs = []
        
        # Step 1: 자료 수집 (저렴한 모델로 충분)
        sources = self._research(topic)
        costs.append({"step": "research", "model": "fast", "cost": 0.002})
        
        # Step 2: 분석 (균형 모델)
        analysis = self._analyze(sources)
        costs.append({"step": "analyze", "model": "balanced", "cost": 0.05})
        
        # Step 3: 초안 작성 (저렴한 모델)
        draft = self._write_draft(analysis)
        costs.append({"step": "draft", "model": "fast", "cost": 0.002})
        
        # Step 4: 최종 편집 (프리미엄 - 품질 중요)
        final = self._polish(draft)
        costs.append({"step": "polish", "model": "premium", "cost": 0.30})
        
        total_cost = sum(c["cost"] for c in costs)
        
        return {
            "report": final,
            "costs": costs,
            "total_cost": f"${total_cost:.3f}",
            "comparison": f"전체 프리미엄 사용 시: $1.20 → 실제: ${total_cost:.3f} (75% 절감)"
        }
    
    def _research(self, topic: str) -> list:
        """빠른 모델로 자료 수집"""
        return self.agents[self.models["fast"]].execute(
            f"Research {topic}. Return list of key findings."
        )
    
    def _analyze(self, sources: list) -> dict:
        """균형 모델로 심층 분석"""
        return self.agents[self.models["balanced"]].execute(
            f"Analyze these findings and identify patterns: {sources}"
        )
    
    def _write_draft(self, analysis: dict) -> str:
        """빠른 모델로 초안"""
        return self.agents[self.models["fast"]].execute(
            f"Write report draft based on: {analysis}"
        )
    
    def _polish(self, draft: str) -> str:
        """프리미엄 모델로 최종 편집"""
        return self.agents[self.models["premium"]].execute(
            f"Polish and finalize this report: {draft}"
        )

# 사용 예시
pipeline = CostOptimizedResearchPipeline()
result = pipeline.execute("AI market trends 2025")

print(f"💰 총 비용: {result['total_cost']}")
print(f"📊 {result['comparison']}")
```

**비용 비교**:
| 전략 | 비용 | 품질 |
|------|------|------|
| 전체 프리미엄 | $1.20 | ⭐⭐⭐⭐⭐ |
| 모델 티어링 | $0.35 | ⭐⭐⭐⭐ (충분) |
| **절감율** | **71%** | - |

---

## Example 3: 파일 기반 위임 (컨텍스트 50-80% 절약)

**시나리오**: 대규모 코드베이스 리팩터링

```python
class FileBasedDelegation:
    """
    대규모 작업에서 컨텍스트 오염 방지
    - 지시사항을 파일로 전달
    - 결과도 파일로 반환
    - 오케스트레이터 컨텍스트 최소화
    """
    
    async def refactor_codebase(self, requirements: str) -> dict:
        # Step 1: 지시사항을 파일에 작성
        await self.write_file(
            "ai-docs/refactor-requirements.md",
            requirements  # 1000줄 상세 요구사항
        )
        
        # Step 2: 아키텍처 에이전트 호출 (간략한 프롬프트만)
        await self.task(
            agent="architect",
            prompt="""
            Read requirements from: ai-docs/refactor-requirements.md
            Create architecture plan.
            Write plan to: ai-docs/architecture-plan.md
            Return brief summary only (2-3 sentences).
            """
        )
        # 반환: "Architecture plan complete. 3-phase migration 
        #        with backward compatibility. See ai-docs/architecture-plan.md"
        
        # Step 3: 구현 에이전트들 (병렬)
        await asyncio.gather(
            self.task(
                agent="backend-developer",
                prompt="""
                Read plan: ai-docs/architecture-plan.md
                Implement Phase 1 (API layer).
                Output: src/api/
                Summary to: ai-docs/phase1-summary.md
                """
            ),
            self.task(
                agent="frontend-developer",
                prompt="""
                Read plan: ai-docs/architecture-plan.md
                Implement Phase 1 (UI layer).
                Output: src/ui/
                Summary to: ai-docs/phase1-ui-summary.md
                """
            ),
        )
        
        # Step 4: 통합 검토
        final = await self.task(
            agent="senior-reviewer",
            prompt="""
            Review all summaries in ai-docs/*-summary.md
            Consolidate into final report: ai-docs/final-report.md
            """
        )
        
        return {
            "status": "complete",
            "report": "ai-docs/final-report.md",
            "context_saved": "~80% (파일 기반 위임)"
        }

# 컨텍스트 사용량 비교
"""
인라인 지시 방식:
  - 요구사항: 5,000 tokens
  - 아키텍처 계획: 3,000 tokens
  - 각 에이전트 결과: 2,000 tokens × 3
  - 오케스트레이터 컨텍스트: ~14,000 tokens

파일 기반 방식:
  - 프롬프트: 100 tokens × 4
  - 요약 반환: 50 tokens × 4
  - 오케스트레이터 컨텍스트: ~600 tokens
  
절감: 14,000 → 600 = 96% 감소!
"""
```

---

## Example 4: 적응형 에이전트 전환

**시나리오**: 사용자 선호도에 따른 속도/품질 트레이드오프

```python
class AdaptiveAgentSwitching:
    """
    사용자 상황에 따라 에이전트 구성 변경
    - 급한 경우: 빠른 단일 에이전트
    - 중요한 경우: 다중 에이전트 검증
    """
    
    def execute(self, task: str, mode: str = "balanced") -> dict:
        if mode == "fast":
            return self._fast_mode(task)
        elif mode == "quality":
            return self._quality_mode(task)
        else:
            return self._balanced_mode(task)
    
    def _fast_mode(self, task: str) -> dict:
        """
        속도 우선: 단일 에이전트
        - 비용: $
        - 시간: 10초
        - 품질: ⭐⭐⭐
        """
        result = self.agents["fast-generalist"].execute(task)
        return {
            "result": result,
            "mode": "fast",
            "time": "~10s",
            "cost": "$0.01"
        }
    
    async def _quality_mode(self, task: str) -> dict:
        """
        품질 우선: 3-에이전트 병렬 검증
        - 비용: $$$
        - 시간: 15초 (병렬)
        - 품질: ⭐⭐⭐⭐⭐
        """
        results = await asyncio.gather(
            self.agents["claude-coder"].execute(task),
            self.agents["gpt4-reviewer"].execute(task),
            self.agents["gemini-tester"].execute(task),
        )
        
        consensus = self._find_consensus(results)
        
        return {
            "result": consensus,
            "mode": "quality",
            "time": "~15s",
            "cost": "$0.15",
            "validation": "3-model consensus"
        }
    
    def _balanced_mode(self, task: str) -> dict:
        """
        균형: 2-에이전트 (실행 + 검토)
        - 비용: $$
        - 시간: 20초 (순차)
        - 품질: ⭐⭐⭐⭐
        """
        # 실행
        result = self.agents["coder"].execute(task)
        
        # 검토
        review = self.agents["reviewer"].execute(f"Review: {result}")
        
        if review.score >= 0.8:
            return {"result": result, "mode": "balanced"}
        else:
            # 피드백 반영
            improved = self.agents["coder"].execute(
                f"{task}\n\nAddress: {review.feedback}"
            )
            return {"result": improved, "mode": "balanced", "iterations": 2}

# 사용 예시
agent = AdaptiveAgentSwitching()

# 급한 버그 수정
quick_fix = agent.execute("Fix null pointer in auth.py", mode="fast")

# 중요한 프로덕션 코드
critical_code = agent.execute("Implement payment processing", mode="quality")

# 일반 작업
normal_task = agent.execute("Add logging to service", mode="balanced")
```

---

## Example 5: 과학 연구 자동화 (Denario 패턴)

**시나리오**: 데이터에서 논문까지 자동화

```python
class ResearchAutomation:
    """
    Denario 스타일 연구 자동화
    - 데이터 설명 → 아이디어 생성 → 방법론 → 결과 → 논문
    """
    
    def run_research(self, data_description: str) -> dict:
        stages = []
        
        # Stage 1: 아이디어 생성
        idea = self.idea_agent.execute(
            f"Generate research hypothesis from: {data_description}"
        )
        stages.append({"stage": "idea", "output": idea})
        
        # Stage 2: 방법론 개발
        method = self.method_agent.execute(
            f"Develop methodology to test: {idea}"
        )
        stages.append({"stage": "method", "output": method})
        
        # Stage 3: 실험 실행 (코드 생성 + 실행)
        code = self.coder_agent.execute(
            f"Write analysis code for: {method}"
        )
        results = self.executor_agent.execute(code)
        stages.append({"stage": "results", "output": results})
        
        # Stage 4: 논문 작성
        paper = self.writer_agent.execute(f"""
        Write LaTeX paper:
        - Hypothesis: {idea}
        - Methodology: {method}
        - Results: {results}
        Format: APS journal style
        """)
        stages.append({"stage": "paper", "output": paper})
        
        return {
            "stages": stages,
            "final_paper": paper,
            "total_agents": 5,
            "estimated_cost": "$0.50"
        }

# 사용 예시
researcher = ResearchAutomation()
result = researcher.run_research("""
Available data: Time-series stock prices (5 years, 500 stocks)
Tools: pandas, sklearn, matplotlib
Goal: Identify predictive patterns
""")

print(f"📄 논문 생성 완료: {len(result['final_paper'])} characters")
```

---

## Quick Reference: 워크플로우 선택 가이드

| 상황 | 권장 워크플로우 | 예상 비용 | 예상 시간 |
|------|---------------|----------|----------|
| 간단한 코드 작성 | 단일 에이전트 | $0.05 | 10초 |
| 코드 + 리뷰 | 2-에이전트 파이프라인 | $0.10 | 25초 |
| 다중 모델 검증 | 병렬 검증 | $0.15 | 12초 |
| 연구 보고서 | 순차 파이프라인 | $0.35 | 60초 |
| 대규모 리팩터링 | 파일 기반 위임 | $0.50 | 5분 |
| 과학 논문 생성 | Denario 패턴 | $0.50 | 3분 |
