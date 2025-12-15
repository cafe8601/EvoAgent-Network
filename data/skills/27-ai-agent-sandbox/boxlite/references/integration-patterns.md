# BoxLite Integration Patterns

Patterns for integrating BoxLite with AI agent frameworks and multi-agent systems.

## LangChain Integration

### Custom Tool Implementation

```python
from langchain.tools import BaseTool
from langchain.pydantic_v1 import Field
from typing import Optional, Type
from pydantic import BaseModel
import asyncio
import boxlite

class PythonCodeInput(BaseModel):
    code: str = Field(description="Python code to execute")

class BoxLitePythonTool(BaseTool):
    """Execute Python code in secure local sandbox."""

    name: str = "boxlite_python_executor"
    description: str = """Execute Python code in a secure, isolated local sandbox.
    Use this when you need to run Python code safely.
    Input should be valid Python code as a string.
    Returns stdout on success, error message on failure."""

    args_schema: Type[BaseModel] = PythonCodeInput
    _box: Optional[object] = None
    _loop: Optional[object] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._loop = asyncio.new_event_loop()

    async def _ensure_box(self):
        if self._box is None:
            self._box = await boxlite.SimpleBox(
                image="python:3.11-slim",
                cpu=2,
                memory=1024
            ).__aenter__()
            # Pre-install common packages
            await self._box.exec("pip", "install", "numpy", "pandas", "requests")

    def _run(self, code: str) -> str:
        return self._loop.run_until_complete(self._arun(code))

    async def _arun(self, code: str) -> str:
        await self._ensure_box()

        # Write code to file
        await self._box.write_file("/tmp/script.py", code)

        # Execute
        result = await self._box.exec("python3", "/tmp/script.py")

        if result.returncode == 0:
            return result.stdout if result.stdout else "Code executed successfully (no output)"
        else:
            return f"Error (exit code {result.returncode}):\n{result.stderr}"

    def cleanup(self):
        """Call this when done to release resources."""
        if self._box:
            self._loop.run_until_complete(
                self._box.__aexit__(None, None, None)
            )
            self._box = None


# Usage with LangChain Agent
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

def create_code_agent():
    tool = BoxLitePythonTool()

    llm = ChatOpenAI(model="gpt-4")

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful coding assistant.
        Use the boxlite_python_executor tool to run Python code when needed.
        Always show the code you're running and explain the results."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    agent = create_tool_calling_agent(llm, [tool], prompt)
    executor = AgentExecutor(agent=agent, tools=[tool], verbose=True)

    return executor, tool

# Usage
executor, tool = create_code_agent()
try:
    result = executor.invoke({
        "input": "Calculate the first 10 prime numbers"
    })
    print(result["output"])
finally:
    tool.cleanup()
```

### Async LangChain Tool

```python
from langchain.tools import BaseTool
import boxlite

class AsyncBoxLiteTool(BaseTool):
    """Async-first BoxLite tool for LangChain."""

    name: str = "async_python_sandbox"
    description: str = "Execute Python code asynchronously in isolated sandbox"

    async def _arun(self, code: str) -> str:
        async with boxlite.SimpleBox(image="python:slim") as box:
            result = await box.exec("python3", "-c", code)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"

    def _run(self, code: str) -> str:
        import asyncio
        return asyncio.run(self._arun(code))
```

## CrewAI Integration

### Custom Tool for CrewAI

```python
from crewai.tools import BaseTool
import asyncio
import boxlite

class BoxLiteCodeTool(BaseTool):
    name: str = "Secure Code Executor"
    description: str = """Execute Python code in a secure local sandbox.
    Use for data analysis, calculations, file processing.
    Input: Python code string. Output: execution result."""

    def _run(self, code: str) -> str:
        return asyncio.run(self._execute(code))

    async def _execute(self, code: str) -> str:
        async with boxlite.SimpleBox(
            image="python:3.11-slim",
            memory=2048
        ) as box:
            # Install dependencies if needed
            if "pandas" in code:
                await box.exec("pip", "install", "pandas")
            if "numpy" in code:
                await box.exec("pip", "install", "numpy")

            # Write and execute
            await box.write_file("/tmp/code.py", code)
            result = await box.exec("python3", "/tmp/code.py")

            if result.returncode == 0:
                return result.stdout
            return f"Execution failed:\n{result.stderr}"


# Usage with CrewAI
from crewai import Agent, Task, Crew

data_analyst = Agent(
    role="Data Analyst",
    goal="Analyze data using Python code",
    backstory="Expert data analyst who writes clean, efficient Python code",
    tools=[BoxLiteCodeTool()],
    verbose=True
)

analysis_task = Task(
    description="Analyze the sales data and calculate monthly averages",
    expected_output="Summary statistics with monthly breakdown",
    agent=data_analyst
)

crew = Crew(
    agents=[data_analyst],
    tasks=[analysis_task]
)

result = crew.kickoff()
```

### Browser Automation Tool for CrewAI

```python
from crewai.tools import BaseTool
import asyncio
import boxlite
import base64

class BoxLiteBrowserTool(BaseTool):
    name: str = "Browser Automation"
    description: str = """Automate web browser for research and data collection.
    Input: URL to visit. Output: Screenshot (base64) and page content."""

    def _run(self, url: str) -> dict:
        return asyncio.run(self._browse(url))

    async def _browse(self, url: str) -> dict:
        async with boxlite.ComputerBox(
            cpu=2,
            memory=4096
        ) as desktop:
            await desktop.wait_until_ready()

            # Open browser
            await desktop.exec("firefox", url)
            await asyncio.sleep(5)

            # Capture screenshot
            screenshot = await desktop.screenshot()

            # Get page source via curl
            result = await desktop.exec("curl", "-s", url)

            return {
                "url": url,
                "screenshot_b64": base64.b64encode(screenshot).decode(),
                "content_preview": result.stdout[:2000] if result.stdout else ""
            }
```

## AutoGen Integration

### AssistantAgent with BoxLite

```python
from autogen import AssistantAgent, UserProxyAgent
import asyncio
import boxlite

def boxlite_executor(code: str) -> str:
    """Execute code in BoxLite sandbox."""

    async def run():
        async with boxlite.SimpleBox(image="python:slim") as box:
            await box.write_file("/tmp/code.py", code)
            result = await box.exec("python3", "/tmp/code.py")
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"

    return asyncio.run(run())

# Configure AutoGen to use BoxLite
code_execution_config = {
    "work_dir": "/tmp",
    "use_docker": False,  # We use BoxLite instead
}

assistant = AssistantAgent(
    name="coding_assistant",
    llm_config={"model": "gpt-4"},
    system_message="""You are a helpful coding assistant.
    When you need to execute code, wrap it in ```python blocks.
    The code will be executed in a secure sandbox."""
)

user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config=code_execution_config,
)

# Override code execution
original_execute = user_proxy.execute_code_blocks

def custom_execute(code_blocks, **kwargs):
    results = []
    for lang, code in code_blocks:
        if lang.lower() == "python":
            result = boxlite_executor(code)
            results.append((0, result))
        else:
            results.append((1, f"Unsupported language: {lang}"))
    return results

user_proxy.execute_code_blocks = custom_execute
```

## Multi-Agent System Integration

### Parallel Agent Execution

```python
import asyncio
import boxlite
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class AgentTask:
    agent_id: str
    code: str
    dependencies: list[str] = None

class MultiAgentExecutor:
    """Execute multiple agent tasks in parallel isolated sandboxes."""

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_task(self, task: AgentTask) -> dict:
        async with self.semaphore:
            async with boxlite.SimpleBox(
                image="python:3.11-slim",
                cpu=1,
                memory=1024
            ) as box:
                # Install task-specific dependencies
                if task.dependencies:
                    for dep in task.dependencies:
                        await box.exec("pip", "install", dep)

                # Execute code
                await box.write_file("/tmp/task.py", task.code)
                result = await box.exec("python3", "/tmp/task.py")

                return {
                    "agent_id": task.agent_id,
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None
                }

    async def execute_all(self, tasks: list[AgentTask]) -> list[dict]:
        """Execute all tasks concurrently."""
        coroutines = [self.execute_task(task) for task in tasks]
        return await asyncio.gather(*coroutines)


# Usage
async def main():
    executor = MultiAgentExecutor(max_concurrent=3)

    tasks = [
        AgentTask(
            agent_id="analyst_1",
            code="import numpy as np; print(np.mean([1,2,3,4,5]))",
            dependencies=["numpy"]
        ),
        AgentTask(
            agent_id="analyst_2",
            code="import pandas as pd; print(pd.Series([1,2,3]).sum())",
            dependencies=["pandas"]
        ),
        AgentTask(
            agent_id="analyst_3",
            code="print(sum(range(100)))"
        ),
    ]

    results = await executor.execute_all(tasks)
    for r in results:
        print(f"{r['agent_id']}: {r['output']}")

asyncio.run(main())
```

### Agent with Persistent Sandbox

```python
import asyncio
import boxlite

class PersistentSandboxAgent:
    """Agent with long-lived sandbox for stateful operations."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._box = None
        self._history = []

    async def start(self):
        """Initialize sandbox."""
        self._box = await boxlite.SimpleBox(
            image="python:3.11-slim",
            cpu=2,
            memory=2048
        ).__aenter__()

        # Setup environment
        await self._box.exec("pip", "install", "numpy", "pandas", "scikit-learn")
        await self._box.exec("mkdir", "-p", "/workspace")

    async def execute(self, code: str) -> dict:
        """Execute code in persistent sandbox."""
        if not self._box:
            await self.start()

        # Track execution history
        self._history.append(code)

        # Execute
        await self._box.write_file("/workspace/current.py", code)
        result = await self._box.exec("python3", "/workspace/current.py")

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "history_length": len(self._history)
        }

    async def save_state(self, filename: str):
        """Save current Python state for later."""
        await self._box.write_file(f"/workspace/{filename}", "\n".join(self._history))

    async def load_data(self, name: str, data: str):
        """Load data into sandbox."""
        await self._box.write_file(f"/workspace/{name}", data)

    async def get_file(self, path: str) -> bytes:
        """Retrieve file from sandbox."""
        return await self._box.read_file(path)

    async def stop(self):
        """Cleanup sandbox."""
        if self._box:
            await self._box.__aexit__(None, None, None)
            self._box = None


# Usage
async def main():
    agent = PersistentSandboxAgent("data_agent_1")

    try:
        await agent.start()

        # Load data
        await agent.load_data("data.csv", "a,b,c\n1,2,3\n4,5,6")

        # Execute analysis (state persists)
        r1 = await agent.execute("""
import pandas as pd
df = pd.read_csv('/workspace/data.csv')
print(df.head())
""")
        print(r1["output"])

        # Continue with same state
        r2 = await agent.execute("""
print(f"DataFrame shape: {df.shape}")
print(f"Sum of column a: {df['a'].sum()}")
""")
        print(r2["output"])

    finally:
        await agent.stop()

asyncio.run(main())
```

## Error Handling Patterns

### Retry with Backoff

```python
import asyncio
import boxlite
from typing import TypeVar, Callable

T = TypeVar('T')

async def with_retry(
    func: Callable[[], T],
    max_retries: int = 3,
    initial_delay: float = 0.5
) -> T:
    """Execute with exponential backoff retry."""
    last_error = None

    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                await asyncio.sleep(delay)

    raise last_error


async def safe_execute(code: str) -> dict:
    async def _execute():
        async with boxlite.SimpleBox(image="python:slim") as box:
            result = await box.exec("python3", "-c", code)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            return {"success": True, "output": result.stdout}

    try:
        return await with_retry(_execute)
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Timeout Handling

```python
import asyncio
import boxlite

async def execute_with_timeout(code: str, timeout_sec: float = 30.0) -> dict:
    """Execute code with timeout."""
    async def _run():
        async with boxlite.SimpleBox(image="python:slim") as box:
            result = await box.exec("python3", "-c", code)
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }

    try:
        return await asyncio.wait_for(_run(), timeout=timeout_sec)
    except asyncio.TimeoutError:
        return {
            "success": False,
            "output": "",
            "error": f"Execution timed out after {timeout_sec}s"
        }
```

## Resource Management

### Context Manager Pattern

```python
from contextlib import asynccontextmanager
import boxlite

@asynccontextmanager
async def managed_sandbox(
    image: str = "python:slim",
    install: list[str] = None
):
    """Managed sandbox with automatic cleanup."""
    box = await boxlite.SimpleBox(image=image).__aenter__()

    try:
        # Install dependencies
        if install:
            for pkg in install:
                await box.exec("pip", "install", pkg)

        yield box
    finally:
        await box.__aexit__(None, None, None)


# Usage
async def main():
    async with managed_sandbox(install=["numpy", "pandas"]) as box:
        result = await box.exec("python3", "-c", "import numpy; print(numpy.__version__)")
        print(result.stdout)
```

### Resource Pool

```python
import asyncio
import boxlite
from typing import Optional

class SandboxPool:
    """Pool of reusable sandboxes."""

    def __init__(self, size: int = 5, image: str = "python:slim"):
        self.size = size
        self.image = image
        self._available: asyncio.Queue = asyncio.Queue()
        self._all: list = []
        self._initialized = False

    async def initialize(self):
        """Pre-create sandbox pool."""
        for _ in range(self.size):
            box = await boxlite.SimpleBox(image=self.image).__aenter__()
            self._all.append(box)
            await self._available.put(box)
        self._initialized = True

    async def acquire(self) -> object:
        """Get sandbox from pool."""
        if not self._initialized:
            await self.initialize()
        return await self._available.get()

    async def release(self, box: object):
        """Return sandbox to pool."""
        await self._available.put(box)

    async def cleanup(self):
        """Destroy all sandboxes."""
        for box in self._all:
            await box.__aexit__(None, None, None)
        self._all.clear()


# Usage
async def main():
    pool = SandboxPool(size=3)

    async def worker(task_id: int, code: str):
        box = await pool.acquire()
        try:
            result = await box.exec("python3", "-c", code)
            return f"Task {task_id}: {result.stdout}"
        finally:
            await pool.release(box)

    try:
        tasks = [
            worker(i, f"print({i} * {i})")
            for i in range(10)
        ]
        results = await asyncio.gather(*tasks)
        for r in results:
            print(r)
    finally:
        await pool.cleanup()

asyncio.run(main())
```
