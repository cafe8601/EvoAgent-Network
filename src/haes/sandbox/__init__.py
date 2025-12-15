"""
HAES Agent Sandbox - AI 에이전트 테스트 및 훈련 환경

27-ai-agent-sandbox SKILL 기반 구현

현실적인 선택:
1. Docker 기반 로컬 샌드박스 (기본) - 무료, 안정적
2. Daytona 통합 (선택) - 클라우드 기반, API 키 필요
3. BoxLite 통합 (선택) - 로컬 하드웨어 격리, 실험적

용도:
- AI 에이전트가 생성한 코드 안전 실행
- HAES 시스템 테스트 자동화
- 스킬/에이전트 성능 평가
- 프롬프트 최적화 훈련
"""

import os
import asyncio
import subprocess
import tempfile
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from loguru import logger


@dataclass
class ExecutionResult:
    """코드 실행 결과"""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: float = 0
    sandbox_type: str = "docker"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestCase:
    """테스트 케이스"""
    id: str
    name: str
    input_query: str
    expected_skills: List[str] = field(default_factory=list)
    expected_agents: List[str] = field(default_factory=list)
    validation_code: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """테스트 결과"""
    test_id: str
    passed: bool
    execution_time_ms: float
    response: str
    skills_used: List[str]
    agents_used: List[str]
    validation_output: Optional[str] = None
    error: Optional[str] = None


class SandboxExecutor(ABC):
    """샌드박스 실행기 추상 클래스"""
    
    @abstractmethod
    async def execute(self, code: str, language: str = "python") -> ExecutionResult:
        """코드 실행"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """리소스 정리"""
        pass


class DockerSandbox(SandboxExecutor):
    """
    Docker 기반 샌드박스 (가장 현실적인 선택)
    
    안정적이고, 무료이며, 대부분 환경에서 동작
    
    사용 예시:
        async with DockerSandbox() as sandbox:
            result = await sandbox.execute("print('Hello!')")
            print(result.output)
    """
    
    def __init__(
        self,
        image: str = "python:3.11-slim",
        timeout: int = 30,
        memory_limit: str = "512m",
        cpu_limit: float = 1.0,
    ):
        self.image = image
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self._container_id: Optional[str] = None
    
    async def __aenter__(self):
        await self._ensure_image()
        return self
    
    async def __aexit__(self, *args):
        await self.cleanup()
    
    async def _ensure_image(self):
        """이미지 확인 및 풀"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker", "image", "inspect", self.image,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()
            
            if proc.returncode != 0:
                logger.info(f"Pulling Docker image: {self.image}")
                proc = await asyncio.create_subprocess_exec(
                    "docker", "pull", self.image,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.wait()
        except Exception as e:
            logger.warning(f"Docker image check failed: {e}")
    
    async def execute(self, code: str, language: str = "python") -> ExecutionResult:
        """
        Docker 컨테이너에서 코드 실행
        
        Args:
            code: 실행할 코드
            language: 언어 (python, node, bash)
        
        Returns:
            ExecutionResult
        """
        start_time = datetime.now()
        
        try:
            # 임시 파일에 코드 작성
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False
            ) as f:
                f.write(code)
                temp_file = f.name
            
            # 실행 명령 구성
            if language == "python":
                cmd = ["python3", "/code/script.py"]
            elif language == "node":
                cmd = ["node", "/code/script.js"]
            else:
                cmd = ["bash", "/code/script.sh"]
            
            # Docker 실행
            docker_cmd = [
                "docker", "run", "--rm",
                "--memory", self.memory_limit,
                f"--cpus={self.cpu_limit}",
                "--network", "none",  # 네트워크 격리
                "-v", f"{temp_file}:/code/script.py:ro",
                self.image,
            ] + cmd
            
            proc = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Execution timeout ({self.timeout}s)",
                    execution_time_ms=self.timeout * 1000,
                    sandbox_type="docker",
                )
            
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return ExecutionResult(
                success=proc.returncode == 0,
                output=stdout.decode('utf-8', errors='replace'),
                error=stderr.decode('utf-8', errors='replace') if proc.returncode != 0 else None,
                execution_time_ms=elapsed_ms,
                sandbox_type="docker",
            )
            
        except FileNotFoundError:
            return ExecutionResult(
                success=False,
                output="",
                error="Docker not installed. Please install Docker first.",
                sandbox_type="docker",
            )
        except Exception as e:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time_ms=elapsed_ms,
                sandbox_type="docker",
            )
        finally:
            # 임시 파일 삭제
            try:
                Path(temp_file).unlink()
            except:
                pass
    
    async def cleanup(self):
        """컨테이너 정리"""
        pass  # --rm 플래그로 자동 삭제


class DaytonaSandbox(SandboxExecutor):
    """
    Daytona 클라우드 샌드박스
    
    API Key 필요 (https://app.daytona.io)
    
    사용 예시:
        sandbox = DaytonaSandbox(api_key="your-key")
        result = await sandbox.execute("print('Hello!')")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        target: str = "us",
    ):
        self.api_key = api_key or os.getenv("DAYTONA_API_KEY")
        self.target = target
        self._daytona = None
        self._sandbox = None
        
        if not self.api_key:
            logger.warning("DAYTONA_API_KEY not set. Daytona sandbox disabled.")
    
    async def __aenter__(self):
        if self.api_key:
            await self._setup()
        return self
    
    async def __aexit__(self, *args):
        await self.cleanup()
    
    async def _setup(self):
        """Daytona 샌드박스 생성"""
        try:
            from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams
            
            config = DaytonaConfig(api_key=self.api_key, target=self.target)
            self._daytona = Daytona(config)
            self._sandbox = self._daytona.create(
                CreateSandboxFromSnapshotParams(language="python")
            )
            logger.info("Daytona sandbox created")
        except ImportError:
            logger.warning("Daytona SDK not installed. Run: pip install daytona")
        except Exception as e:
            logger.error(f"Daytona setup failed: {e}")
    
    async def execute(self, code: str, language: str = "python") -> ExecutionResult:
        """Daytona에서 코드 실행"""
        if not self._sandbox:
            return ExecutionResult(
                success=False,
                output="",
                error="Daytona sandbox not available",
                sandbox_type="daytona",
            )
        
        start_time = datetime.now()
        
        try:
            result = self._sandbox.process.code_run(code)
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return ExecutionResult(
                success=result.exit_code == 0,
                output=result.result or "",
                error=result.stderr if result.exit_code != 0 else None,
                execution_time_ms=elapsed_ms,
                sandbox_type="daytona",
            )
        except Exception as e:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time_ms=elapsed_ms,
                sandbox_type="daytona",
            )
    
    async def cleanup(self):
        """Daytona 샌드박스 삭제"""
        if self._sandbox:
            try:
                self._sandbox.delete()
                logger.info("Daytona sandbox deleted")
            except:
                pass
            self._sandbox = None


class LocalSandbox(SandboxExecutor):
    """
    로컬 프로세스 샌드박스 (제한된 격리)
    
    Docker 없이 빠른 테스트용
    주의: 완전한 격리 아님!
    
    사용 예시:
        sandbox = LocalSandbox()
        result = await sandbox.execute("print('Hello!')")
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        pass
    
    async def execute(self, code: str, language: str = "python") -> ExecutionResult:
        """로컬에서 코드 실행 (제한된 격리)"""
        start_time = datetime.now()
        
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False
            ) as f:
                f.write(code)
                temp_file = f.name
            
            proc = await asyncio.create_subprocess_exec(
                "python3", temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Timeout ({self.timeout}s)",
                    execution_time_ms=self.timeout * 1000,
                    sandbox_type="local",
                )
            
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return ExecutionResult(
                success=proc.returncode == 0,
                output=stdout.decode('utf-8', errors='replace'),
                error=stderr.decode('utf-8', errors='replace') if proc.returncode != 0 else None,
                execution_time_ms=elapsed_ms,
                sandbox_type="local",
            )
        except Exception as e:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time_ms=elapsed_ms,
                sandbox_type="local",
            )
        finally:
            try:
                Path(temp_file).unlink()
            except:
                pass
    
    async def cleanup(self):
        pass


class HAESTestRunner:
    """
    HAES 시스템 테스트 러너
    
    에이전트/스킬 동작 테스트 및 평가
    
    사용 예시:
        runner = HAESTestRunner()
        
        # 테스트 케이스 추가
        runner.add_test(TestCase(
            id="test-1",
            name="LoRA fine-tuning query",
            input_query="LoRA 파인튜닝 방법 설명해줘",
            expected_skills=["11-fine-tuning"],
            tags=["ml", "fine-tuning"]
        ))
        
        # 테스트 실행
        results = await runner.run_all()
        runner.print_report(results)
    """
    
    def __init__(
        self,
        haes_api_url: str = "http://localhost:8080",
        sandbox: Optional[SandboxExecutor] = None,
    ):
        self.api_url = haes_api_url
        self.sandbox = sandbox or LocalSandbox()
        self.tests: List[TestCase] = []
    
    def add_test(self, test: TestCase):
        """테스트 케이스 추가"""
        self.tests.append(test)
    
    def load_tests_from_file(self, filepath: str):
        """JSON 파일에서 테스트 로드"""
        with open(filepath) as f:
            data = json.load(f)
        
        for t in data.get("tests", []):
            self.tests.append(TestCase(**t))
    
    async def run_test(self, test: TestCase) -> TestResult:
        """단일 테스트 실행"""
        import aiohttp
        
        start_time = datetime.now()
        
        try:
            async with aiohttp.ClientSession() as session:
                # HAES 채팅 API 호출
                async with session.post(
                    f"{self.api_url}/api/chat",
                    json={"query": test.input_query},
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status != 200:
                        return TestResult(
                            test_id=test.id,
                            passed=False,
                            execution_time_ms=0,
                            response="",
                            skills_used=[],
                            agents_used=[],
                            error=f"API error: {resp.status}",
                        )
                    
                    data = await resp.json()
            
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # 스킬/에이전트 매칭 확인
            skills_used = data.get("skills_used", [])
            agents_used = data.get("agents_used", [])
            
            skills_match = (
                not test.expected_skills or
                any(s in skills_used for s in test.expected_skills)
            )
            agents_match = (
                not test.expected_agents or
                any(a in agents_used for a in test.expected_agents)
            )
            
            # 검증 코드 실행 (있는 경우)
            validation_output = None
            if test.validation_code:
                code = test.validation_code.replace("{response}", data["response"])
                result = await self.sandbox.execute(code)
                validation_output = result.output
                # 검증 코드가 "PASS" 출력 시 통과
                skills_match = skills_match and "PASS" in result.output
            
            return TestResult(
                test_id=test.id,
                passed=skills_match and agents_match,
                execution_time_ms=elapsed_ms,
                response=data["response"][:500],  # 500자 제한
                skills_used=skills_used,
                agents_used=agents_used,
                validation_output=validation_output,
            )
            
        except Exception as e:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return TestResult(
                test_id=test.id,
                passed=False,
                execution_time_ms=elapsed_ms,
                response="",
                skills_used=[],
                agents_used=[],
                error=str(e),
            )
    
    async def run_all(self, tags: Optional[List[str]] = None) -> List[TestResult]:
        """모든 테스트 실행"""
        tests_to_run = self.tests
        
        if tags:
            tests_to_run = [
                t for t in self.tests
                if any(tag in t.tags for tag in tags)
            ]
        
        results = []
        for test in tests_to_run:
            logger.info(f"Running test: {test.name}")
            result = await self.run_test(test)
            results.append(result)
            
            status = "✅ PASS" if result.passed else "❌ FAIL"
            logger.info(f"  {status} ({result.execution_time_ms:.0f}ms)")
        
        return results
    
    def print_report(self, results: List[TestResult]):
        """결과 보고서 출력"""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        
        print("\n" + "=" * 60)
        print("HAES Test Report")
        print("=" * 60)
        print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
        print(f"Success Rate: {passed/total*100:.1f}%\n")
        
        for r in results:
            status = "✅" if r.passed else "❌"
            print(f"{status} {r.test_id}: {r.execution_time_ms:.0f}ms")
            if not r.passed and r.error:
                print(f"   Error: {r.error}")
        
        print("=" * 60)


class PromptOptimizer:
    """
    프롬프트 최적화 도구
    
    다양한 프롬프트 변형을 테스트하고 최적의 프롬프트 찾기
    
    사용 예시:
        optimizer = PromptOptimizer()
        
        # 프롬프트 변형 추가
        optimizer.add_variant("base", "LoRA 파인튜닝 방법")
        optimizer.add_variant("detailed", "LoRA를 사용한 LLM 파인튜닝 방법을 단계별로 설명해줘")
        optimizer.add_variant("ko_simple", "LoRA 파인튜닝이 뭐야?")
        
        # 평가 실행
        results = await optimizer.evaluate_all()
        best = optimizer.get_best_variant(results)
    """
    
    def __init__(
        self,
        haes_api_url: str = "http://localhost:8080",
        evaluation_criteria: Optional[Dict[str, float]] = None,
    ):
        self.api_url = haes_api_url
        self.variants: Dict[str, str] = {}
        self.criteria = evaluation_criteria or {
            "response_length": 0.2,
            "execution_time": 0.3,
            "skill_match": 0.5,
        }
    
    def add_variant(self, name: str, prompt: str):
        """프롬프트 변형 추가"""
        self.variants[name] = prompt
    
    async def evaluate_variant(
        self,
        name: str,
        expected_skills: Optional[List[str]] = None,
        num_runs: int = 1,
    ) -> Dict[str, Any]:
        """단일 변형 평가"""
        import aiohttp
        
        prompt = self.variants[name]
        results = []
        
        for _ in range(num_runs):
            start = datetime.now()
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.api_url}/api/chat",
                        json={"query": prompt},
                        timeout=aiohttp.ClientTimeout(total=60),
                    ) as resp:
                        data = await resp.json()
                
                elapsed = (datetime.now() - start).total_seconds() * 1000
                
                # 스코어 계산
                skill_match = 0.0
                if expected_skills:
                    matched = sum(
                        1 for s in expected_skills
                        if any(s in used for used in data.get("skills_used", []))
                    )
                    skill_match = matched / len(expected_skills)
                
                results.append({
                    "success": True,
                    "response_length": len(data.get("response", "")),
                    "execution_time": elapsed,
                    "skill_match": skill_match,
                    "skills_used": data.get("skills_used", []),
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                })
        
        # 평균 계산
        successes = [r for r in results if r.get("success")]
        if not successes:
            return {"name": name, "score": 0, "error": "All runs failed"}
        
        avg_length = sum(r["response_length"] for r in successes) / len(successes)
        avg_time = sum(r["execution_time"] for r in successes) / len(successes)
        avg_skill = sum(r["skill_match"] for r in successes) / len(successes)
        
        # 정규화 스코어
        score = (
            self.criteria["response_length"] * min(avg_length / 1000, 1.0) +
            self.criteria["execution_time"] * max(0, 1 - avg_time / 30000) +
            self.criteria["skill_match"] * avg_skill
        )
        
        return {
            "name": name,
            "prompt": prompt,
            "score": score,
            "avg_response_length": avg_length,
            "avg_execution_time_ms": avg_time,
            "avg_skill_match": avg_skill,
            "num_runs": num_runs,
        }
    
    async def evaluate_all(
        self,
        expected_skills: Optional[List[str]] = None,
        num_runs: int = 1,
    ) -> List[Dict[str, Any]]:
        """모든 변형 평가"""
        results = []
        
        for name in self.variants:
            logger.info(f"Evaluating variant: {name}")
            result = await self.evaluate_variant(name, expected_skills, num_runs)
            results.append(result)
        
        # 점수순 정렬
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results
    
    def get_best_variant(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """최고 점수 변형 반환"""
        return results[0] if results else {}


# 편의 함수
async def run_code_safe(
    code: str,
    sandbox_type: str = "local",
    **kwargs,
) -> ExecutionResult:
    """
    안전하게 코드 실행
    
    Args:
        code: 실행할 코드
        sandbox_type: "local", "docker", "daytona"
    
    Returns:
        ExecutionResult
    """
    if sandbox_type == "docker":
        async with DockerSandbox(**kwargs) as sandbox:
            return await sandbox.execute(code)
    elif sandbox_type == "daytona":
        sandbox = DaytonaSandbox(**kwargs)
        async with sandbox:
            return await sandbox.execute(code)
    else:
        sandbox = LocalSandbox(**kwargs)
        return await sandbox.execute(code)


# 간단한 테스트
if __name__ == "__main__":
    async def test():
        # 로컬 샌드박스 테스트
        sandbox = LocalSandbox()
        result = await sandbox.execute("print('Hello from sandbox!')")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}")
        print(f"Time: {result.execution_time_ms:.0f}ms")
    
    asyncio.run(test())
