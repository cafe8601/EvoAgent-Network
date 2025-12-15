# BoxLite API Reference

Complete API documentation for BoxLite Python SDK.

## Installation

```bash
pip install boxlite
```

**Requirements:**
- Python 3.10+
- macOS (Apple Silicon, macOS 12+) or Linux (x86_64/ARM64 with KVM)

## Core Classes

### SimpleBox

Lightweight box for command execution without GUI.

```python
class SimpleBox:
    def __init__(
        self,
        image: str = "alpine:latest",
        cpu: int = 1,
        memory: int = 512,  # MB
        disk_size: int = 5120,  # MB
        mounts: list[tuple[str, str, str]] = None,  # [(host, guest, mode)]
        env: dict[str, str] = None
    )
```

**Methods:**

```python
async def exec(
    self,
    *args: str,
    env: dict[str, str] = None,
    cwd: str = None,
    timeout: float = None
) -> ExecResult:
    """Execute command in box."""

async def write_file(
    self,
    path: str,
    content: bytes | str
) -> None:
    """Write file to box filesystem."""

async def read_file(
    self,
    path: str
) -> bytes:
    """Read file from box filesystem."""

async def __aenter__(self) -> SimpleBox:
    """Async context manager entry."""

async def __aexit__(self, *args) -> None:
    """Async context manager exit (cleanup)."""
```

**Example:**

```python
import asyncio
import boxlite

async def main():
    async with boxlite.SimpleBox(
        image="python:3.11-slim",
        cpu=2,
        memory=1024
    ) as box:
        # Execute command
        result = await box.exec("python3", "-c", "print(1+1)")
        print(result.stdout)  # "2\n"

        # Write file
        await box.write_file("/tmp/data.txt", "hello world")

        # Read file
        content = await box.read_file("/tmp/data.txt")
        print(content)  # b"hello world"

asyncio.run(main())
```

### ComputerBox

Full desktop environment with GUI automation capabilities.

```python
class ComputerBox:
    def __init__(
        self,
        image: str = "ubuntu-desktop:latest",
        cpu: int = 2,
        memory: int = 2048,  # MB
        disk_size: int = 20480,  # MB
        display_width: int = 1280,
        display_height: int = 720
    )
```

**Methods:**

```python
async def wait_until_ready(
    self,
    timeout: float = 60.0
) -> None:
    """Wait for desktop environment to be ready."""

async def mouse_move(
    self,
    x: int,
    y: int
) -> None:
    """Move mouse to absolute position."""

async def left_click(self) -> None:
    """Perform left mouse click at current position."""

async def right_click(self) -> None:
    """Perform right mouse click at current position."""

async def double_click(self) -> None:
    """Perform double left click at current position."""

async def type(
    self,
    text: str,
    delay_ms: int = 50
) -> None:
    """Type text with optional delay between keystrokes."""

async def key(
    self,
    key_name: str
) -> None:
    """Press special key (Enter, Tab, Escape, etc.)."""

async def hotkey(
    self,
    *keys: str
) -> None:
    """Press key combination (e.g., hotkey('ctrl', 'c'))."""

async def screenshot(self) -> bytes:
    """Capture current screen as PNG."""

async def exec(
    self,
    *args: str,
    env: dict[str, str] = None
) -> ExecResult:
    """Execute command in desktop environment."""
```

**Example:**

```python
import asyncio
import boxlite

async def main():
    async with boxlite.ComputerBox(
        cpu=2,
        memory=4096,
        display_width=1920,
        display_height=1080
    ) as desktop:
        await desktop.wait_until_ready()

        # Open terminal
        await desktop.hotkey("ctrl", "alt", "t")
        await asyncio.sleep(1)

        # Type command
        await desktop.type("echo 'Hello from BoxLite!'")
        await desktop.key("Enter")

        # Take screenshot
        screenshot = await desktop.screenshot()
        with open("result.png", "wb") as f:
            f.write(screenshot)

asyncio.run(main())
```

### InteractiveBox

Interactive terminal session similar to `docker exec -it`.

```python
class InteractiveBox:
    def __init__(
        self,
        image: str = "alpine:latest",
        cpu: int = 1,
        memory: int = 512
    )
```

**Methods:**

```python
async def wait(self) -> None:
    """Wait for user interaction to complete."""

async def send(
    self,
    data: str
) -> None:
    """Send input to interactive session."""

async def recv(
    self,
    timeout: float = None
) -> str:
    """Receive output from interactive session."""
```

**Example:**

```python
import asyncio
from boxlite import InteractiveBox

async def main():
    async with InteractiveBox(image="python:slim") as box:
        # Start Python REPL
        await box.send("python3\n")
        output = await box.recv(timeout=5)
        print(output)

        # Execute in REPL
        await box.send("print('Hello!')\n")
        output = await box.recv(timeout=5)
        print(output)

asyncio.run(main())
```

## Data Classes

### ExecResult

Result of command execution.

```python
@dataclass
class ExecResult:
    returncode: int
    stdout: str
    stderr: str
```

## Low-Level API

### BoxliteRuntime

Direct access to runtime for advanced use cases.

```python
from boxlite import BoxliteRuntime, BoxOptions, RootfsSpec

# Initialize runtime
runtime = BoxliteRuntime.default_runtime()

# Create box with options
options = BoxOptions(
    rootfs=RootfsSpec.Image("alpine:latest"),
    vcpu_count=2,
    mem_size_mib=1024,
    network_enabled=True
)

# Create and manage box
box_id, litebox = runtime.create(options)

# Execute command
result = litebox.exec(["echo", "hello"])

# Cleanup
litebox.destroy()
```

### BoxOptions

```python
@dataclass
class BoxOptions:
    rootfs: RootfsSpec
    vcpu_count: int = 1
    mem_size_mib: int = 512
    disk_size_mib: int = 5120
    network_enabled: bool = True
    kernel_path: str = None  # Custom kernel
    init_path: str = None    # Custom init
```

### RootfsSpec

```python
class RootfsSpec:
    @staticmethod
    def Image(name: str) -> RootfsSpec:
        """Use OCI image as rootfs."""

    @staticmethod
    def Path(path: str) -> RootfsSpec:
        """Use local directory as rootfs."""

    @staticmethod
    def Qcow2(path: str) -> RootfsSpec:
        """Use QCOW2 disk image as rootfs."""
```

## Environment Variables

```bash
# Logging level
export BOXLITE_LOG_LEVEL=debug  # debug, info, warn, error

# Custom kernel path
export BOXLITE_KERNEL_PATH=/path/to/vmlinux

# Image cache directory
export BOXLITE_CACHE_DIR=/path/to/cache
```

## Error Types

```python
class BoxliteError(Exception):
    """Base exception for BoxLite errors."""

class ImageNotFoundError(BoxliteError):
    """Raised when container image not found."""

class RuntimeError(BoxliteError):
    """Raised when runtime operation fails."""

class TimeoutError(BoxliteError):
    """Raised when operation times out."""

class PermissionError(BoxliteError):
    """Raised when KVM/hypervisor access denied."""
```

## Best Practices

### Resource Management

```python
# Always use async context manager
async with boxlite.SimpleBox(image="python:slim") as box:
    # Box automatically cleaned up on exit
    pass

# Or manual cleanup
box = boxlite.SimpleBox(image="python:slim")
try:
    await box.__aenter__()
    # ... use box
finally:
    await box.__aexit__(None, None, None)
```

### Concurrent Execution

```python
import asyncio
import boxlite

async def run_in_box(code: str, box_id: int):
    async with boxlite.SimpleBox(image="python:slim") as box:
        result = await box.exec("python3", "-c", code)
        return f"Box {box_id}: {result.stdout}"

async def main():
    codes = [
        "print(1+1)",
        "print(2*2)",
        "print(3**3)"
    ]

    # Run concurrently
    tasks = [run_in_box(code, i) for i, code in enumerate(codes)]
    results = await asyncio.gather(*tasks)

    for r in results:
        print(r)

asyncio.run(main())
```

### Image Caching

```python
# First run downloads image (slow)
async with boxlite.SimpleBox(image="python:3.11-slim") as box:
    pass

# Subsequent runs use cached layers (fast)
async with boxlite.SimpleBox(image="python:3.11-slim") as box:
    pass
```
