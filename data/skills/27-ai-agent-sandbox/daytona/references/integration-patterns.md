# Daytona Integration Patterns

Practical integration patterns for AI agent frameworks and production systems.

## LangChain Integration

### Official Tool: DaytonaDataAnalysisTool

```bash
pip install langchain-daytona-data-analysis
```

```python
from langchain_daytona_data_analysis import DaytonaDataAnalysisTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# Initialize tool
tool = DaytonaDataAnalysisTool(
    daytona_api_key="your-key",
    # Optional: callback for processing results
    on_result=lambda r: print(f"Execution result: {r}")
)

# Build agent
llm = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a data analyst. Execute Python code to analyze data."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, [tool], prompt)
executor = AgentExecutor(agent=agent, tools=[tool], verbose=True)

# Run
result = executor.invoke({
    "input": "Load this CSV and show summary statistics: https://example.com/data.csv"
})
```

### Custom LangChain Tool

For more control, create a custom tool:

```python
from langchain.tools import BaseTool
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams
from pydantic import Field
from typing import Optional, Type
from pydantic import BaseModel

class CodeInput(BaseModel):
    code: str = Field(description="Python code to execute")

class DaytonaPythonExecutor(BaseTool):
    name: str = "python_sandbox"
    description: str = """Execute Python code in a secure isolated sandbox.
    Use for data analysis, calculations, file processing, or any Python task.
    Input should be valid Python code as a string."""
    args_schema: Type[BaseModel] = CodeInput

    api_key: str = Field(exclude=True)
    _daytona: Optional[Daytona] = None
    _sandbox: Optional[object] = None

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _ensure_sandbox(self):
        if not self._daytona:
            self._daytona = Daytona(DaytonaConfig(api_key=self.api_key))
        if not self._sandbox:
            self._sandbox = self._daytona.create(
                CreateSandboxFromSnapshotParams(language="python")
            )
            # Pre-install common packages
            self._sandbox.process.exec("pip install pandas numpy matplotlib seaborn")
        return self._sandbox

    def _run(self, code: str) -> str:
        sandbox = self._ensure_sandbox()
        result = sandbox.process.code_run(code)

        if result.exit_code == 0:
            return result.result if result.result else "Code executed successfully (no output)"
        return f"Error (exit code {result.exit_code}): {result.stderr}"

    async def _arun(self, code: str) -> str:
        return self._run(code)

    def cleanup(self):
        if self._sandbox:
            self._sandbox.delete()
            self._sandbox = None

# Usage with agent
tool = DaytonaPythonExecutor(api_key="your-key")
# ... use with AgentExecutor
# Remember to call tool.cleanup() when done
```

### ReAct Agent Pattern

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Tool setup (using custom tool from above)
daytona_tool = DaytonaPythonExecutor(api_key="your-key")

# ReAct prompt
react_prompt = PromptTemplate.from_template("""
Answer the following questions as best you can using the available tools.

You have access to:
{tools}

Use the following format:

Question: the input question
Thought: think about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer

Question: {input}
{agent_scratchpad}
""")

llm = ChatOpenAI(model="gpt-4o", temperature=0)
agent = create_react_agent(llm, [daytona_tool], react_prompt)
executor = AgentExecutor(agent=agent, tools=[daytona_tool], verbose=True)

result = executor.invoke({
    "input": "Calculate the compound interest on $10000 at 5% for 10 years"
})
```

## CrewAI Integration

### Daytona Tool for CrewAI

```python
from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams

class DaytonaCodeTool(BaseTool):
    name: str = "Code Executor"
    description: str = "Execute Python code in a secure sandbox environment"

    def __init__(self, api_key: str):
        super().__init__()
        self._daytona = Daytona(DaytonaConfig(api_key=api_key))
        self._sandbox = None

    def _ensure_sandbox(self):
        if not self._sandbox:
            self._sandbox = self._daytona.create(
                CreateSandboxFromSnapshotParams(language="python")
            )
        return self._sandbox

    def _run(self, code: str) -> str:
        sandbox = self._ensure_sandbox()
        result = sandbox.process.code_run(code)
        return result.result if result.exit_code == 0 else f"Error: {result.stderr}"

# Create specialized agents
code_tool = DaytonaCodeTool(api_key="your-key")

data_analyst = Agent(
    role="Data Analyst",
    goal="Analyze data and generate insights",
    backstory="Expert in statistical analysis and Python programming",
    tools=[code_tool],
    verbose=True
)

task = Task(
    description="Analyze the correlation between temperature and ice cream sales",
    expected_output="Statistical analysis with correlation coefficient",
    agent=data_analyst
)

crew = Crew(agents=[data_analyst], tasks=[task])
result = crew.kickoff()
```

## Multi-Agent Sports Analytics Pattern

Integration with `21-multiagent-learning-system` for real-time sports analysis:

```python
from dataclasses import dataclass
from typing import List, Dict, Any
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams
import json

@dataclass
class PlayerPosition:
    player_id: str
    team: str
    x: float
    y: float
    timestamp: float

class TacticalAnalysisSandbox:
    """Sandbox for running tactical analysis code generated by AI agents."""

    def __init__(self, api_key: str):
        self.daytona = Daytona(DaytonaConfig(api_key=api_key))
        self._sandbox = None

    def _get_sandbox(self):
        if not self._sandbox:
            self._sandbox = self.daytona.create(
                CreateSandboxFromSnapshotParams(language="python")
            )
            # Install analysis dependencies
            self._sandbox.process.exec(
                "pip install pandas numpy scipy scikit-learn matplotlib"
            )
        return self._sandbox

    def analyze_formation(self, positions: List[PlayerPosition]) -> Dict[str, Any]:
        """Analyze team formation from player positions."""
        sandbox = self._get_sandbox()

        # Convert positions to JSON for injection
        pos_data = [
            {"player_id": p.player_id, "team": p.team, "x": p.x, "y": p.y}
            for p in positions
        ]

        code = f'''
import json
import numpy as np
from scipy.spatial import ConvexHull, distance
from sklearn.cluster import KMeans

positions = {json.dumps(pos_data)}

# Separate teams
team_a = [p for p in positions if p["team"] == "A"]
team_b = [p for p in positions if p["team"] == "B"]

def analyze_team(players):
    if len(players) < 3:
        return {{"error": "Not enough players"}}

    points = np.array([(p["x"], p["y"]) for p in players])

    # Centroid
    centroid = points.mean(axis=0)

    # Compactness (convex hull area)
    hull = ConvexHull(points)
    compactness = hull.area

    # Formation width and depth
    width = points[:, 0].max() - points[:, 0].min()
    depth = points[:, 1].max() - points[:, 1].min()

    # Line detection (defense, midfield, attack)
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(points[:, 1].reshape(-1, 1))  # Cluster by Y position
    lines = sorted(kmeans.cluster_centers_.flatten())

    return {{
        "centroid": {{"x": float(centroid[0]), "y": float(centroid[1])}},
        "compactness": float(compactness),
        "width": float(width),
        "depth": float(depth),
        "lines": [float(l) for l in lines]
    }}

result = {{
    "team_a": analyze_team(team_a),
    "team_b": analyze_team(team_b)
}}
print(json.dumps(result))
'''

        result = sandbox.process.code_run(code)
        if result.exit_code == 0:
            return json.loads(result.result)
        raise RuntimeError(f"Analysis failed: {result.stderr}")

    def detect_formation_change(
        self,
        before: List[PlayerPosition],
        after: List[PlayerPosition]
    ) -> Dict[str, Any]:
        """Detect if formation has changed between two frames."""
        sandbox = self._get_sandbox()

        before_data = [{"x": p.x, "y": p.y, "team": p.team} for p in before]
        after_data = [{"x": p.x, "y": p.y, "team": p.team} for p in after]

        code = f'''
import json
import numpy as np
from scipy.spatial import procrustes

before = {json.dumps(before_data)}
after = {json.dumps(after_data)}

def get_team_points(data, team):
    return np.array([(p["x"], p["y"]) for p in data if p["team"] == team])

def formation_similarity(pts1, pts2):
    if len(pts1) != len(pts2) or len(pts1) < 3:
        return 0.0
    # Procrustes analysis for shape similarity
    _, _, disparity = procrustes(pts1, pts2)
    return 1.0 - min(disparity, 1.0)

result = {{}}
for team in ["A", "B"]:
    pts_before = get_team_points(before, team)
    pts_after = get_team_points(after, team)
    similarity = formation_similarity(pts_before, pts_after)
    result[team] = {{
        "similarity": float(similarity),
        "changed": similarity < 0.85
    }}

print(json.dumps(result))
'''

        result = sandbox.process.code_run(code)
        if result.exit_code == 0:
            return json.loads(result.result)
        raise RuntimeError(f"Detection failed: {result.stderr}")

    def cleanup(self):
        if self._sandbox:
            self._sandbox.delete()
            self._sandbox = None
```

## Async Batch Processing

For processing multiple requests efficiently:

```python
import asyncio
from daytona import AsyncDaytona, DaytonaConfig, CreateSandboxFromSnapshotParams
from typing import List, Dict

class AsyncCodeProcessor:
    def __init__(self, api_key: str, max_concurrent: int = 5):
        self.config = DaytonaConfig(api_key=api_key)
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_single(self, code: str) -> Dict:
        async with self.semaphore:
            daytona = AsyncDaytona(self.config)
            sandbox = await daytona.create(
                CreateSandboxFromSnapshotParams(language="python")
            )
            try:
                result = await sandbox.process.code_run(code)
                return {
                    "success": result.exit_code == 0,
                    "output": result.result,
                    "error": result.stderr if result.exit_code != 0 else None
                }
            finally:
                await sandbox.delete()

    async def execute_batch(self, codes: List[str]) -> List[Dict]:
        tasks = [self.execute_single(code) for code in codes]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Usage
async def main():
    processor = AsyncCodeProcessor(api_key="your-key", max_concurrent=3)

    codes = [
        "print(sum(range(100)))",
        "print([x**2 for x in range(10)])",
        "import math; print(math.pi)",
    ]

    results = await processor.execute_batch(codes)
    for i, result in enumerate(results):
        print(f"Code {i}: {result}")

asyncio.run(main())
```

## Persistent Sandbox Pool

For high-frequency execution without cold starts:

```python
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams
from queue import Queue
from threading import Lock
import atexit

class SandboxPool:
    def __init__(self, api_key: str, pool_size: int = 3):
        self.daytona = Daytona(DaytonaConfig(api_key=api_key))
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()
        self._initialize_pool(pool_size)
        atexit.register(self.cleanup)

    def _initialize_pool(self, size: int):
        for _ in range(size):
            sandbox = self.daytona.create(
                CreateSandboxFromSnapshotParams(language="python")
            )
            self.pool.put(sandbox)

    def acquire(self):
        return self.pool.get()

    def release(self, sandbox):
        self.pool.put(sandbox)

    def execute(self, code: str) -> dict:
        sandbox = self.acquire()
        try:
            result = sandbox.process.code_run(code)
            return {
                "success": result.exit_code == 0,
                "output": result.result,
                "error": result.stderr if result.exit_code != 0 else None
            }
        finally:
            self.release(sandbox)

    def cleanup(self):
        while not self.pool.empty():
            sandbox = self.pool.get()
            try:
                sandbox.delete()
            except:
                pass

# Usage
pool = SandboxPool(api_key="your-key", pool_size=3)

# Fast execution (no cold start after pool init)
result = pool.execute("print('Hello from pool!')")
```

## Web API Integration

FastAPI server with Daytona execution:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams
from contextlib import asynccontextmanager

class ExecuteRequest(BaseModel):
    code: str
    language: str = "python"

class ExecuteResponse(BaseModel):
    success: bool
    output: str | None
    error: str | None

# Global pool (initialized at startup)
sandbox_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global sandbox_pool
    # Startup: initialize sandbox pool
    sandbox_pool = SandboxPool(api_key="your-key", pool_size=3)
    yield
    # Shutdown: cleanup
    sandbox_pool.cleanup()

app = FastAPI(lifespan=lifespan)

@app.post("/execute", response_model=ExecuteResponse)
async def execute_code(request: ExecuteRequest):
    if not sandbox_pool:
        raise HTTPException(status_code=503, detail="Service not ready")

    result = sandbox_pool.execute(request.code)
    return ExecuteResponse(**result)
```

## Error Recovery Pattern

```python
from dataclasses import dataclass
from typing import Optional, Callable
import time

@dataclass
class RetryConfig:
    max_retries: int = 3
    initial_delay: float = 0.5
    max_delay: float = 10.0
    exponential_base: float = 2.0

class ResilientExecutor:
    def __init__(
        self,
        api_key: str,
        retry_config: RetryConfig = RetryConfig(),
        on_retry: Optional[Callable] = None
    ):
        self.daytona = Daytona(DaytonaConfig(api_key=api_key))
        self.config = retry_config
        self.on_retry = on_retry
        self._sandbox = None

    def _get_sandbox(self, force_new: bool = False):
        if force_new and self._sandbox:
            try:
                self._sandbox.delete()
            except:
                pass
            self._sandbox = None

        if not self._sandbox:
            self._sandbox = self.daytona.create(
                CreateSandboxFromSnapshotParams(language="python")
            )
        return self._sandbox

    def execute(self, code: str) -> dict:
        last_error = None
        delay = self.config.initial_delay

        for attempt in range(self.config.max_retries):
            try:
                # Force new sandbox on retry
                sandbox = self._get_sandbox(force_new=attempt > 0)
                result = sandbox.process.code_run(code)

                return {
                    "success": result.exit_code == 0,
                    "output": result.result,
                    "error": result.stderr if result.exit_code != 0 else None,
                    "attempts": attempt + 1
                }

            except Exception as e:
                last_error = e
                if self.on_retry:
                    self.on_retry(attempt, e)

                if attempt < self.config.max_retries - 1:
                    time.sleep(delay)
                    delay = min(
                        delay * self.config.exponential_base,
                        self.config.max_delay
                    )

        return {
            "success": False,
            "output": None,
            "error": f"Failed after {self.config.max_retries} attempts: {last_error}",
            "attempts": self.config.max_retries
        }

    def cleanup(self):
        if self._sandbox:
            try:
                self._sandbox.delete()
            except:
                pass
            self._sandbox = None
```
