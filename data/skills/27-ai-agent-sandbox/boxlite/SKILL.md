---
name: boxlite-local-sandbox
description: Local hardware-isolated sandbox for AI agent code execution. Use when agents need secure local execution without cloud dependencies, desktop GUI automation, or AGPL-free licensing.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [AI Sandbox, Local Execution, Hardware Isolation, Desktop Automation, MicroVM]
dependencies: [boxlite>=0.1.0, python>=3.10]
---

# BoxLite Local Sandbox

Embedded virtual machine runtime for secure local code execution with hardware-level isolation.

## When to Use BoxLite

**Use BoxLite when:**
- Need secure local execution without cloud/network dependencies
- Desktop GUI automation required (browser, apps, screenshots)
- AGPL license restrictions apply (BoxLite: Apache 2.0)
- Cost-sensitive environments (no API fees)
- Offline/air-gapped environments (security-sensitive)
- Hardware-level isolation stronger than containers needed

**Key features:**
- **Hardware isolation**: Each Box runs independent kernel (not shared like Docker)
- **No daemon required**: Library embeds directly in application
- **OCI compatible**: Use Docker images directly
- **Three Box types**: SimpleBox, ComputerBox, InteractiveBox
- **Desktop automation**: Mouse, keyboard, screenshots (ComputerBox)

**Use Daytona instead when:**
- Cloud-native serverless architecture needed
- Horizontal scaling across multiple nodes
- Official LangChain integration preferred
- Windows support required
- Team collaboration features needed

**Platform requirements:**
- macOS: Apple Silicon, macOS 12+
- Linux: x86_64 or ARM64 with KVM enabled
- Windows: Not supported

## Quick Start

### Installation

```bash
pip install boxlite
```

### Basic Code Execution (SimpleBox)

```python
import asyncio
import boxlite

async def main():
    async with boxlite.SimpleBox(image="python:slim") as box:
        # Execute Python code in isolated VM
        result = await box.exec("python3", "-c", "print('Hello from BoxLite!')")
        print(result.stdout)

asyncio.run(main())
```

### Desktop Automation (ComputerBox)

```python
import asyncio
import boxlite

async def main():
    async with boxlite.ComputerBox(cpu=2, memory=2048) as desktop:
        await desktop.wait_until_ready()

        # GUI automation
        await desktop.mouse_move(100, 100)
        await desktop.left_click()
        await desktop.type("Hello World!")

        # Take screenshot
        screenshot = await desktop.screenshot()
        with open("screen.png", "wb") as f:
            f.write(screenshot)

asyncio.run(main())
```

### Interactive Shell (InteractiveBox)

```python
import asyncio
from boxlite import InteractiveBox

async def main():
    async with InteractiveBox(image="alpine:latest") as box:
        # Interactive terminal session (like docker exec -it)
        await box.wait()

asyncio.run(main())
```

## AI Agent Integration

### Safe Code Executor Pattern

```python
import asyncio
from dataclasses import dataclass
from typing import Optional
import boxlite

@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: Optional[str]

class BoxLiteCodeExecutor:
    """Execute AI-generated code safely in local sandbox."""

    def __init__(self, image: str = "python:slim"):
        self.image = image
        self._box = None

    async def __aenter__(self):
        self._box = await boxlite.SimpleBox(image=self.image).__aenter__()
        return self

    async def __aexit__(self, *args):
        if self._box:
            await self._box.__aexit__(*args)

    async def execute(self, code: str) -> ExecutionResult:
        """Execute code and return structured result."""
        try:
            # Write code to file
            await self._box.exec("sh", "-c", f"cat > /tmp/script.py << 'EOF'\n{code}\nEOF")

            # Execute
            result = await self._box.exec("python3", "/tmp/script.py")

            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None
            )
        except Exception as e:
            return ExecutionResult(success=False, output="", error=str(e))

# Usage with AI agent
async def main():
    async with BoxLiteCodeExecutor() as executor:
        # AI generates this code
        ai_code = """
import math
result = sum(math.factorial(i) for i in range(10))
print(f"Sum of factorials 0-9: {result}")
"""
        result = await executor.execute(ai_code)
        print(result.output)  # Sum of factorials 0-9: 409113

asyncio.run(main())
```

### LangChain Custom Tool

```python
from langchain.tools import BaseTool
from typing import Optional
from pydantic import Field
import asyncio
import boxlite

class BoxLitePythonTool(BaseTool):
    name: str = "boxlite_python"
    description: str = "Execute Python code in secure local sandbox. Input: valid Python code."
    _box: Optional[object] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _setup_box(self):
        if not self._box:
            self._box = await boxlite.SimpleBox(image="python:slim").__aenter__()

    def _run(self, code: str) -> str:
        return asyncio.run(self._arun(code))

    async def _arun(self, code: str) -> str:
        await self._setup_box()
        result = await self._box.exec(
            "python3", "-c", code
        )
        if result.returncode == 0:
            return result.stdout
        return f"Error: {result.stderr}"

    def cleanup(self):
        if self._box:
            asyncio.run(self._box.__aexit__(None, None, None))
```

### Multi-Agent Browser Automation

```python
import asyncio
import boxlite

class BrowserAutomationAgent:
    """AI agent with browser automation capability."""

    def __init__(self):
        self._desktop = None

    async def setup(self):
        self._desktop = await boxlite.ComputerBox(
            cpu=2,
            memory=4096,
            image="ubuntu-desktop:latest"  # Custom desktop image
        ).__aenter__()
        await self._desktop.wait_until_ready()

    async def navigate_and_extract(self, url: str, selector: str) -> dict:
        """Navigate to URL and extract content."""
        # Open browser
        await self._desktop.exec("firefox", url)
        await asyncio.sleep(3)  # Wait for page load

        # Take screenshot for visual analysis
        screenshot = await self._desktop.screenshot()

        # Execute extraction script
        result = await self._desktop.exec(
            "python3", "-c", f"""
import subprocess
result = subprocess.run(['curl', '-s', '{url}'], capture_output=True, text=True)
print(result.stdout[:1000])
"""
        )

        return {
            "screenshot": screenshot,
            "content": result.stdout,
            "url": url
        }

    async def cleanup(self):
        if self._desktop:
            await self._desktop.__aexit__(None, None, None)
```

## Box Types Comparison

| Feature | SimpleBox | ComputerBox | InteractiveBox |
|---------|-----------|-------------|----------------|
| **Use Case** | Code execution | Desktop GUI | Terminal session |
| **Speed** | Fastest | Moderate | Fast |
| **GUI** | No | Yes | No |
| **Mouse/Keyboard** | No | Yes | No |
| **Screenshots** | No | Yes | No |
| **Interactive** | No | No | Yes |
| **AI Agent** | Code interpreter | Browser automation | Exploratory dev |

## BoxLite vs Daytona Decision Guide

```
Need cloud scalability?
├── Yes → Daytona
└── No → Continue

Need official LangChain integration?
├── Yes → Daytona
└── No → Continue

AGPL license restriction?
├── Yes → BoxLite (Apache 2.0)
└── No → Continue

Need desktop/GUI automation?
├── Yes → BoxLite (ComputerBox)
└── No → Continue

Offline/air-gapped environment?
├── Yes → BoxLite
└── No → Continue

Cost-sensitive (no API fees)?
├── Yes → BoxLite
└── No → Either works
```

## Configuration Options

```python
import boxlite

# Resource configuration
async with boxlite.SimpleBox(
    image="python:3.11-slim",
    cpu=2,              # CPU cores
    memory=2048,        # MB RAM
    disk_size=10240,    # MB disk
) as box:
    pass

# Environment variables
async with boxlite.SimpleBox(image="python:slim") as box:
    result = await box.exec(
        "python3", "-c", "import os; print(os.environ.get('MY_VAR'))",
        env={"MY_VAR": "hello"}
    )

# Mount host directory (read-only)
async with boxlite.SimpleBox(
    image="python:slim",
    mounts=[("/host/data", "/data", "ro")]
) as box:
    result = await box.exec("ls", "-la", "/data")
```

## Error Handling

```python
import asyncio
import boxlite
from dataclasses import dataclass
from typing import Optional

@dataclass
class SafeResult:
    success: bool
    output: str
    error: Optional[str]
    retries: int

async def execute_with_retry(
    box,
    command: list[str],
    max_retries: int = 3
) -> SafeResult:
    """Execute with retry and structured error handling."""

    for attempt in range(max_retries):
        try:
            result = await box.exec(*command)

            return SafeResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                retries=attempt
            )
        except Exception as e:
            if attempt == max_retries - 1:
                return SafeResult(
                    success=False,
                    output="",
                    error=f"Failed after {max_retries} attempts: {e}",
                    retries=attempt + 1
                )
            await asyncio.sleep(0.5 * (attempt + 1))
```

## Common Issues

| Issue | Solution |
|-------|----------|
| KVM not available (Linux) | Enable KVM: `sudo modprobe kvm` and add user to kvm group |
| Slow first start | Image download on first run; subsequent starts are fast (layer caching) |
| Memory errors | Increase memory: `memory=4096` |
| Permission denied | Check KVM permissions on Linux |
| Image not found | Use full image name: `docker.io/library/python:slim` |

## Security Considerations

- **Hardware isolation**: Each Box has independent kernel (VM, not container)
- **No host access**: Code cannot escape to host system
- **Network isolation**: Configurable network access per Box
- **Resource limits**: CPU/memory/disk strictly enforced
- **Ephemeral by default**: Box destroyed on exit unless persisted

## Maturity Notice

BoxLite is a new project (as of 2024). Consider:
- API may change in minor versions
- Community and ecosystem still growing
- For production, test thoroughly with your use cases
- Monitor GitHub for updates and issues

## References

- **[API Reference](references/api-reference.md)** - Complete SDK API documentation
- **[ComputerBox Guide](references/computerbox-guide.md)** - Desktop automation details
- **[Integration Patterns](references/integration-patterns.md)** - LangChain, CrewAI, agent patterns

## Resources

- **GitHub**: https://github.com/boxlite-labs/boxlite
- **Python Examples**: https://github.com/boxlite-labs/boxlite-python-examples
- **PyTorch Korea Article**: https://discuss.pytorch.kr/t/boxlite-ai-no-daemon-no-dependencies/8415
