---
name: daytona-ai-sandbox
description: Secure sandbox infrastructure for executing AI-generated code. Use when AI agents need to safely run dynamically generated Python/TypeScript code, implement code interpreters, or build automated code execution pipelines.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [AI Sandbox, Code Execution, Agent Infrastructure, Security, LangChain, Isolation]
dependencies: [daytona>=0.21.0]
---

# Daytona AI Sandbox

Secure infrastructure for running AI-generated code in isolated sandbox environments.

## When to Use Daytona

**Use Daytona when:**
- AI agents generate code that needs execution (LangChain, CrewAI, AutoGPT)
- Building code interpreters or playgrounds
- Running untrusted or dynamically generated code safely
- Need isolated execution with file system access
- Implementing automated code testing pipelines

**Key features:**
- **90ms sandbox creation**: Near-instant isolated environments
- **Multi-language support**: Python, TypeScript, JavaScript
- **Complete isolation**: Code cannot access host infrastructure
- **Persistence**: File system and state maintained across calls
- **SDK options**: Python (sync/async) and TypeScript

**Use alternatives instead:**
- **Modal**: For GPU workloads and ML inference (see `09-infrastructure/modal`)
- **E2B**: Alternative sandbox provider with similar features
- **Docker**: When you need full container control
- **Local execution**: For trusted code without isolation needs

## Quick Start

### Prerequisites

1. Create account at https://app.daytona.io
2. Generate API key at Dashboard → Keys
3. Install SDK: `pip install daytona`

### Basic Code Execution

```python
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams

# Initialize client
config = DaytonaConfig(api_key="your-api-key", target="us")
daytona = Daytona(config)

# Create sandbox and execute code
sandbox = daytona.create(CreateSandboxFromSnapshotParams(language="python"))

try:
    result = sandbox.process.code_run("""
import pandas as pd
data = {'player': ['Kim', 'Lee', 'Park'], 'goals': [5, 3, 7]}
df = pd.DataFrame(data)
print(df.to_string())
""")
    print(result.result)  # Output: DataFrame string
finally:
    sandbox.delete()  # Always cleanup
```

### AI Agent Integration Pattern

```python
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams

class SafeCodeExecutor:
    """Execute AI-generated code safely in Daytona sandbox."""

    def __init__(self, api_key: str):
        self.daytona = Daytona(DaytonaConfig(api_key=api_key, target="us"))
        self.sandbox = None

    def __enter__(self):
        self.sandbox = self.daytona.create(
            CreateSandboxFromSnapshotParams(language="python")
        )
        return self

    def __exit__(self, *args):
        if self.sandbox:
            self.sandbox.delete()

    def execute(self, code: str, timeout: int = 30) -> dict:
        """Execute code and return result with error handling."""
        try:
            result = self.sandbox.process.code_run(code)
            return {
                "success": result.exit_code == 0,
                "output": result.result,
                "error": result.stderr if result.exit_code != 0 else None
            }
        except Exception as e:
            return {"success": False, "output": None, "error": str(e)}

# Usage
with SafeCodeExecutor(api_key="your-key") as executor:
    # AI generates this code dynamically
    ai_generated_code = """
result = sum(range(1, 101))
print(f"Sum 1-100: {result}")
"""
    output = executor.execute(ai_generated_code)
    print(output)  # {"success": True, "output": "Sum 1-100: 5050", "error": None}
```

## Core Operations

### Code Execution

```python
# Simple execution
result = sandbox.process.code_run("print('Hello')")

# With dependencies (install first)
sandbox.process.exec("pip install numpy pandas")
result = sandbox.process.code_run("""
import numpy as np
print(np.mean([1, 2, 3, 4, 5]))
""")
```

### File Operations

```python
# Write file to sandbox
sandbox.fs.write("/workspace/data.json", '{"key": "value"}')

# Read file from sandbox
content = sandbox.fs.read("/workspace/data.json")

# List files
files = sandbox.fs.list("/workspace")
```

### Shell Commands

```python
# Execute shell command
result = sandbox.process.exec("ls -la /workspace")
print(result.result)

# With environment variables
result = sandbox.process.exec(
    "echo $MY_VAR",
    env={"MY_VAR": "hello"}
)
```

## LangChain Integration

### Using DaytonaDataAnalysisTool

```python
# pip install langchain-daytona-data-analysis
from langchain_daytona_data_analysis import DaytonaDataAnalysisTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# Initialize tool
daytona_tool = DaytonaDataAnalysisTool(
    daytona_api_key="your-daytona-key"
)

# Create agent with tool
llm = ChatOpenAI(model="gpt-4")
tools = [daytona_tool]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a data analyst. Use the Daytona tool to execute Python code for analysis."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# Run analysis
result = executor.invoke({
    "input": "Calculate the mean and standard deviation of [10, 20, 30, 40, 50]"
})
```

### Custom LangChain Tool

```python
from langchain.tools import BaseTool
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams
from typing import Optional
from pydantic import Field

class DaytonaPythonTool(BaseTool):
    name: str = "python_executor"
    description: str = "Execute Python code in a secure sandbox. Input should be valid Python code."
    daytona: Optional[Daytona] = Field(default=None, exclude=True)
    sandbox: Optional[object] = Field(default=None, exclude=True)

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.daytona = Daytona(DaytonaConfig(api_key=api_key, target="us"))
        self.sandbox = self.daytona.create(
            CreateSandboxFromSnapshotParams(language="python")
        )

    def _run(self, code: str) -> str:
        result = self.sandbox.process.code_run(code)
        if result.exit_code == 0:
            return result.result
        return f"Error: {result.stderr}"

    def cleanup(self):
        if self.sandbox:
            self.sandbox.delete()
```

## Multi-Agent System Integration

Integration with `21-multiagent-learning-system` for sports analytics:

```python
# Formation analysis agent with safe code execution
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams

class TacticalAnalysisExecutor:
    """Execute tactical analysis code generated by AI agents."""

    def __init__(self, api_key: str):
        self.daytona = Daytona(DaytonaConfig(api_key=api_key))
        self._sandbox = None

    @property
    def sandbox(self):
        if not self._sandbox:
            self._sandbox = self.daytona.create(
                CreateSandboxFromSnapshotParams(language="python")
            )
            # Pre-install analysis dependencies
            self._sandbox.process.exec("pip install pandas numpy scipy")
        return self._sandbox

    def analyze_formation(self, player_positions: list) -> dict:
        """Execute formation analysis code."""
        code = f'''
import json
import numpy as np
from scipy.spatial import ConvexHull

positions = {player_positions}
points = np.array([(p["x"], p["y"]) for p in positions])

# Calculate formation metrics
centroid = points.mean(axis=0)
spread = points.std(axis=0)
hull = ConvexHull(points)
compactness = hull.area

result = {{
    "centroid": {{"x": float(centroid[0]), "y": float(centroid[1])}},
    "spread": {{"x": float(spread[0]), "y": float(spread[1])}},
    "compactness": float(compactness),
    "formation_width": float(points[:, 0].max() - points[:, 0].min()),
    "formation_depth": float(points[:, 1].max() - points[:, 1].min())
}}
print(json.dumps(result))
'''
        result = self.sandbox.process.code_run(code)
        if result.exit_code == 0:
            import json
            return json.loads(result.result)
        raise RuntimeError(f"Analysis failed: {result.stderr}")

    def cleanup(self):
        if self._sandbox:
            self._sandbox.delete()
            self._sandbox = None
```

## Error Handling & Best Practices

### Robust Execution Pattern

```python
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: Optional[str]
    execution_time_ms: float

def execute_with_retry(
    sandbox,
    code: str,
    max_retries: int = 3,
    timeout_ms: int = 30000
) -> ExecutionResult:
    """Execute code with retry logic and timeout."""

    for attempt in range(max_retries):
        start = time.time()
        try:
            result = sandbox.process.code_run(code)
            elapsed = (time.time() - start) * 1000

            return ExecutionResult(
                success=result.exit_code == 0,
                output=result.result or "",
                error=result.stderr if result.exit_code != 0 else None,
                execution_time_ms=elapsed
            )
        except Exception as e:
            if attempt == max_retries - 1:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Failed after {max_retries} attempts: {str(e)}",
                    execution_time_ms=(time.time() - start) * 1000
                )
            time.sleep(0.5 * (attempt + 1))  # Exponential backoff
```

### Resource Management

```python
from contextlib import contextmanager

@contextmanager
def managed_sandbox(api_key: str, language: str = "python"):
    """Context manager for automatic sandbox cleanup."""
    daytona = Daytona(DaytonaConfig(api_key=api_key, target="us"))
    sandbox = daytona.create(CreateSandboxFromSnapshotParams(language=language))

    try:
        yield sandbox
    finally:
        try:
            sandbox.delete()
        except Exception:
            pass  # Log but don't raise on cleanup failure

# Usage
with managed_sandbox("your-key") as sandbox:
    result = sandbox.process.code_run("print('safe execution')")
```

## Configuration

### Environment Variables

```bash
export DAYTONA_API_KEY="your-api-key"
export DAYTONA_TARGET="us"  # or "eu"
```

### SDK Configuration Options

```python
from daytona import DaytonaConfig, Resources

config = DaytonaConfig(
    api_key="your-key",
    target="us",  # Region: "us" or "eu"
)

# Resource configuration for sandbox
resources = Resources(
    cpu=2,      # CPU cores
    memory=4,   # GB RAM
    disk=20     # GB storage
)
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Sandbox creation timeout | Check network, increase timeout, verify API key |
| Import errors | Install dependencies first: `sandbox.process.exec("pip install pkg")` |
| File not found | Use absolute paths from `/workspace/` |
| Memory errors | Request larger sandbox: `Resources(memory=8)` |
| Rate limiting | Implement exponential backoff, batch operations |

## Security Considerations

- **AGPL-3.0 License**: Network service usage may require source disclosure
- **API Key Security**: Never commit keys; use environment variables
- **Input Validation**: Sanitize code before execution
- **Resource Limits**: Set appropriate timeouts and memory limits
- **Network Isolation**: Sandboxes are isolated from your infrastructure

## References

- **[API Reference](references/api-reference.md)** - Complete SDK API documentation
- **[Integration Patterns](references/integration-patterns.md)** - LangChain, CrewAI, agent patterns
- **[Troubleshooting](references/troubleshooting.md)** - Common issues and solutions

## Resources

- **Documentation**: https://www.daytona.io/docs
- **Python SDK**: https://github.com/daytonaio/daytona/tree/main/examples/python
- **TypeScript SDK**: https://github.com/daytonaio/daytona/tree/main/examples/typescript
- **LangChain Integration**: https://docs.langchain.com/oss/python/integrations/tools/daytona_data_analysis
