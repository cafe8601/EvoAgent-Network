# Daytona SDK API Reference

Complete API reference for Python SDK v0.21.0+.

## Client Initialization

### DaytonaConfig

```python
from daytona import DaytonaConfig

config = DaytonaConfig(
    api_key: str,           # Required: API key from dashboard
    target: str = "us",     # Region: "us" or "eu"
)
```

### Daytona Client

```python
from daytona import Daytona

daytona = Daytona(config: DaytonaConfig)
```

**Methods:**
| Method | Description |
|--------|-------------|
| `create(params)` | Create a new sandbox |
| `get(sandbox_id)` | Get sandbox by ID |
| `list()` | List all sandboxes |
| `delete(sandbox)` | Delete a sandbox |

## Sandbox Creation

### CreateSandboxFromSnapshotParams

Use when creating from a pre-built snapshot or default language environment.

```python
from daytona import CreateSandboxFromSnapshotParams, Resources

params = CreateSandboxFromSnapshotParams(
    language: str = "python",    # "python", "typescript", "javascript"
    snapshot: str = None,        # Optional: snapshot name
    resources: Resources = None, # Optional: resource config
)

sandbox = daytona.create(params)
```

### CreateSandboxFromImageParams

Use when creating from a custom Docker image.

```python
from daytona import CreateSandboxFromImageParams, Image, Resources

params = CreateSandboxFromImageParams(
    image: Image,                # Required: Image configuration
    language: str = "python",
    resources: Resources = None,
)

sandbox = daytona.create(
    params,
    timeout: int = 120,                    # Timeout in seconds
    on_snapshot_create_logs: callable = None  # Log callback
)
```

### Image Configuration

```python
from daytona import Image

# Pre-built images
image = Image.debian_slim("3.12")  # Python 3.12 on Debian
image = Image.base("node:18")      # Node.js 18

# Custom Dockerfile
image = Image.from_dockerfile("""
FROM python:3.12-slim
RUN pip install pandas numpy scipy
WORKDIR /workspace
""")
```

### Resources Configuration

```python
from daytona import Resources

resources = Resources(
    cpu: int = 1,      # CPU cores (1-8)
    memory: int = 1,   # GB RAM (1-32)
    disk: int = 3,     # GB storage (3-100)
)
```

## Sandbox Object

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | str | Unique sandbox identifier |
| `state` | str | Current state: "started", "stopped", "pending" |
| `auto_stop_interval` | int | Minutes until auto-stop |
| `runner_domain` | str | Sandbox domain |

### Methods

| Method | Description |
|--------|-------------|
| `delete()` | Delete this sandbox |
| `refresh_data()` | Update sandbox properties with latest info |
| `wait_for_sandbox_start()` | Block until sandbox is running |
| `wait_for_sandbox_stop()` | Block until sandbox is stopped |
| `get_user_root_dir()` | Get root directory path |

## Process Module

### sandbox.process

#### code_run()

Execute code in the sandbox interpreter.

```python
result = sandbox.process.code_run(
    code: str,                    # Code to execute
    language: str = None,         # Override language
    env: dict = None,            # Environment variables
    timeout: int = None,         # Timeout in ms
)

# Result object
result.result       # str: stdout output
result.stderr       # str: stderr output
result.exit_code    # int: 0 = success
```

#### exec()

Execute shell command.

```python
result = sandbox.process.exec(
    command: str,                 # Shell command
    cwd: str = None,             # Working directory
    env: dict = None,            # Environment variables
    timeout: int = None,         # Timeout in ms
)

# Result object
result.result       # str: command output
result.exit_code    # int: exit code
```

### Sessions (Background Processes)

```python
# Start background process
session = sandbox.process.create_session(
    session_id: str,
    command: str,
)

# Get session
session = sandbox.process.get_session(session_id)

# List all sessions
sessions = sandbox.process.list_sessions()

# Session properties
session.session_id  # str
session.status      # str: "running", "stopped"
```

## File System Module

### sandbox.fs

| Method | Description |
|--------|-------------|
| `read(path)` | Read file contents |
| `write(path, content)` | Write file |
| `list(path)` | List directory contents |
| `remove(path)` | Delete file or directory |
| `exists(path)` | Check if path exists |
| `mkdir(path)` | Create directory |

```python
# Write file
sandbox.fs.write("/workspace/data.json", '{"key": "value"}')

# Read file
content = sandbox.fs.read("/workspace/data.json")

# List directory
files = sandbox.fs.list("/workspace")
for f in files:
    print(f.name, f.is_directory)

# Check existence
if sandbox.fs.exists("/workspace/config.yaml"):
    config = sandbox.fs.read("/workspace/config.yaml")
```

## Git Module

### sandbox.git

```python
# Clone repository
sandbox.git.clone(
    url: str,              # Repository URL
    path: str,             # Destination path
    branch: str = None,    # Optional branch
)

# Example
sandbox.git.clone(
    "https://github.com/user/repo.git",
    "/workspace/repo"
)
```

## LSP (Language Server Protocol)

### sandbox.create_lsp_server()

```python
lsp = sandbox.create_lsp_server(
    language: str,          # "python", "typescript", etc.
    root_path: str,        # Project root
)

# Search symbols
symbols = lsp.sandbox_symbols("TODO")

# Get diagnostics
diagnostics = lsp.get_diagnostics("/workspace/main.py")
```

## Code Interpreter (Stateful)

Maintains state between executions.

```python
interpreter = sandbox.code_interpreter

# Default context (shared state)
result = interpreter.run("x = 10")
result = interpreter.run("print(x)")  # Outputs: 10

# Named contexts (isolated)
result = interpreter.run("y = 20", context="analysis")
result = interpreter.run("print(y)", context="analysis")

# Delete context
interpreter.delete_context("analysis")
```

## Snapshot Management

### daytona.snapshot

```python
from daytona import CreateSnapshotParams, Image, Resources

# Create snapshot
params = CreateSnapshotParams(
    name: str,                 # Snapshot name
    image: Image,              # Base image
    resources: Resources,      # Resource allocation
)

daytona.snapshot.create(
    params,
    on_logs: callable = None   # Log callback
)

# List snapshots
snapshots = daytona.snapshot.list()

# Get snapshot
snapshot = daytona.snapshot.get("snapshot-name")

# Delete snapshot
daytona.snapshot.delete(snapshot)
```

## Async API

All sync methods have async equivalents with `Async` prefix.

```python
from daytona import AsyncDaytona, DaytonaConfig
import asyncio

async def main():
    config = DaytonaConfig(api_key="your-key")
    daytona = AsyncDaytona(config)

    sandbox = await daytona.create(
        CreateSandboxFromSnapshotParams(language="python")
    )

    try:
        result = await sandbox.process.code_run("print('async!')")
        print(result.result)
    finally:
        await sandbox.delete()

asyncio.run(main())
```

## TypeScript SDK

### Installation

```bash
npm install @daytonaio/sdk
```

### Basic Usage

```typescript
import { Daytona } from '@daytonaio/sdk';

const daytona = new Daytona({ apiKey: 'your-key', target: 'us' });

const sandbox = await daytona.create({ language: 'python' });

try {
  const result = await sandbox.process.codeRun('print("Hello")');
  console.log(result.result);
} finally {
  await sandbox.delete();
}
```

### Key Differences from Python

| Python | TypeScript |
|--------|-----------|
| `code_run()` | `codeRun()` |
| `exit_code` | `exitCode` |
| `sandbox.fs.write()` | `sandbox.fs.write()` |
| `snake_case` | `camelCase` |

## Error Handling

```python
from daytona.exceptions import (
    DaytonaError,          # Base exception
    SandboxError,          # Sandbox operation failed
    TimeoutError,          # Operation timed out
    AuthenticationError,   # Invalid API key
    ResourceError,         # Resource limit exceeded
)

try:
    sandbox = daytona.create(params)
except AuthenticationError:
    print("Invalid API key")
except TimeoutError:
    print("Sandbox creation timed out")
except DaytonaError as e:
    print(f"Daytona error: {e}")
```

## Rate Limits

| Resource | Limit |
|----------|-------|
| Concurrent sandboxes | 10 (default) |
| API requests | 100/minute |
| Sandbox lifetime | 24 hours (default) |

## Version Compatibility

| SDK Version | Breaking Changes |
|-------------|-----------------|
| v0.21.0+ | Snapshots replace images, new param types |
| v0.20.x | Legacy image API |

See [Migration Guide](https://www.daytona.io/dotfiles/updates/daytona-sdk-v0-21-0-breaking-changes-migration-guide) for v0.20.x → v0.21.0 migration.
