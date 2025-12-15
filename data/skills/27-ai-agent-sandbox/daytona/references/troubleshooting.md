# Daytona Troubleshooting Guide

Common issues and solutions for Daytona SDK usage.

## Authentication Errors

### Invalid API Key

**Symptoms:**
```
AuthenticationError: Invalid API key
daytona.exceptions.AuthenticationError: 401 Unauthorized
```

**Solutions:**
1. Verify API key at https://app.daytona.io/dashboard/keys
2. Check environment variable is set:
   ```bash
   echo $DAYTONA_API_KEY
   ```
3. Ensure no leading/trailing whitespace in key
4. Regenerate key if expired

```python
import os
from daytona import Daytona, DaytonaConfig

# Correct pattern
api_key = os.environ.get("DAYTONA_API_KEY")
if not api_key:
    raise ValueError("DAYTONA_API_KEY environment variable not set")

config = DaytonaConfig(api_key=api_key.strip())
```

## Sandbox Creation Issues

### Creation Timeout

**Symptoms:**
```
TimeoutError: Sandbox creation timed out after 120 seconds
```

**Solutions:**
1. Increase timeout:
   ```python
   sandbox = daytona.create(params, timeout=300)  # 5 minutes
   ```
2. Use simpler base image
3. Check Daytona service status: https://status.daytona.io
4. Use snapshot for faster startup:
   ```python
   # Pre-create snapshot with dependencies
   daytona.snapshot.create(CreateSnapshotParams(
       name="my-snapshot",
       image=Image.debian_slim("3.12")
   ))

   # Use snapshot for instant startup
   sandbox = daytona.create(CreateSandboxFromSnapshotParams(
       snapshot="my-snapshot"
   ))
   ```

### Resource Limits Exceeded

**Symptoms:**
```
ResourceError: Concurrent sandbox limit exceeded
ResourceError: Memory allocation failed
```

**Solutions:**
1. Delete unused sandboxes:
   ```python
   for sandbox in daytona.list():
       if should_cleanup(sandbox):
           sandbox.delete()
   ```
2. Use sandbox pooling instead of creating new ones
3. Contact support to increase limits

### Region Selection

**Symptoms:**
```
Connection timeout to sandbox
High latency in sandbox operations
```

**Solutions:**
Choose closer region:
```python
# For US-based users
config = DaytonaConfig(api_key=key, target="us")

# For EU-based users
config = DaytonaConfig(api_key=key, target="eu")
```

## Code Execution Issues

### Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'pandas'
ImportError: cannot import name 'X' from 'Y'
```

**Solutions:**
Install dependencies before execution:
```python
# Install first
sandbox.process.exec("pip install pandas numpy scipy")

# Then execute
result = sandbox.process.code_run("""
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3]})
print(df)
""")
```

For complex dependencies:
```python
# Create snapshot with pre-installed packages
from daytona import CreateSnapshotParams, Image

image = Image.from_dockerfile("""
FROM python:3.12-slim
RUN pip install pandas numpy scipy scikit-learn matplotlib seaborn
WORKDIR /workspace
""")

daytona.snapshot.create(CreateSnapshotParams(
    name="data-science-env",
    image=image,
    resources=Resources(cpu=2, memory=4, disk=10)
))
```

### Timeout During Execution

**Symptoms:**
```
TimeoutError: Code execution timed out
Process killed after timeout
```

**Solutions:**
1. Increase execution timeout (if supported)
2. Break long operations into chunks
3. Use background sessions for long-running tasks:
   ```python
   # Start background process
   session = sandbox.process.create_session(
       session_id="long-task",
       command="python long_script.py"
   )

   # Check status periodically
   import time
   while True:
       session = sandbox.process.get_session("long-task")
       if session.status != "running":
           break
       time.sleep(5)
   ```

### Memory Errors

**Symptoms:**
```
MemoryError: Unable to allocate array
Killed (OOM)
```

**Solutions:**
1. Request more memory:
   ```python
   sandbox = daytona.create(CreateSandboxFromImageParams(
       image=Image.debian_slim("3.12"),
       resources=Resources(cpu=2, memory=8, disk=20)
   ))
   ```
2. Process data in chunks:
   ```python
   code = """
   import pandas as pd

   # Process in chunks instead of loading all at once
   chunks = pd.read_csv('large_file.csv', chunksize=10000)
   results = []
   for chunk in chunks:
       result = process_chunk(chunk)
       results.append(result)
   """
   ```

## File System Issues

### File Not Found

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory
```

**Solutions:**
1. Use absolute paths from `/workspace/`:
   ```python
   # Wrong
   sandbox.fs.write("data.json", content)

   # Correct
   sandbox.fs.write("/workspace/data.json", content)
   ```
2. Create directories first:
   ```python
   sandbox.fs.mkdir("/workspace/output")
   sandbox.fs.write("/workspace/output/result.json", content)
   ```
3. Verify file exists:
   ```python
   if sandbox.fs.exists("/workspace/config.yaml"):
       content = sandbox.fs.read("/workspace/config.yaml")
   ```

### Permission Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
Work within `/workspace/` directory (user has full access):
```python
# This works
sandbox.fs.write("/workspace/output.txt", "data")

# This may fail
sandbox.fs.write("/etc/config", "data")  # System directory
```

## Network Issues

### Connection Timeout

**Symptoms:**
```
ConnectionError: Failed to connect to sandbox
requests.exceptions.Timeout
```

**Solutions:**
1. Check internet connectivity
2. Verify firewall settings
3. Use exponential backoff:
   ```python
   import time

   def execute_with_retry(sandbox, code, max_retries=3):
       for attempt in range(max_retries):
           try:
               return sandbox.process.code_run(code)
           except ConnectionError:
               if attempt < max_retries - 1:
                   time.sleep(2 ** attempt)
               else:
                   raise
   ```

### Rate Limiting

**Symptoms:**
```
RateLimitError: Too many requests
HTTP 429: Rate limit exceeded
```

**Solutions:**
1. Implement rate limiting in your code:
   ```python
   from ratelimit import limits, sleep_and_retry

   @sleep_and_retry
   @limits(calls=100, period=60)  # 100 calls per minute
   def execute_code(sandbox, code):
       return sandbox.process.code_run(code)
   ```
2. Use sandbox pooling instead of creating/deleting frequently
3. Batch operations where possible

## Cleanup Issues

### Orphaned Sandboxes

**Symptoms:**
- Hitting sandbox limits
- Unexpected charges
- `ResourceError: Concurrent sandbox limit exceeded`

**Solutions:**
1. Always use context managers:
   ```python
   from contextlib import contextmanager

   @contextmanager
   def managed_sandbox(daytona):
       sandbox = daytona.create(CreateSandboxFromSnapshotParams(language="python"))
       try:
           yield sandbox
       finally:
           try:
               sandbox.delete()
           except:
               pass

   # Usage
   with managed_sandbox(daytona) as sandbox:
       result = sandbox.process.code_run("print('safe')")
   ```

2. Cleanup script for orphaned sandboxes:
   ```python
   def cleanup_all_sandboxes(daytona):
       for sandbox in daytona.list():
           try:
               sandbox.delete()
               print(f"Deleted: {sandbox.id}")
           except Exception as e:
               print(f"Failed to delete {sandbox.id}: {e}")
   ```

3. Use atexit handler:
   ```python
   import atexit

   sandboxes_to_cleanup = []

   def cleanup_on_exit():
       for sandbox in sandboxes_to_cleanup:
           try:
               sandbox.delete()
           except:
               pass

   atexit.register(cleanup_on_exit)
   ```

### Deletion Fails

**Symptoms:**
```
DaytonaError: Failed to delete sandbox
Sandbox not found
```

**Solutions:**
Ignore errors on cleanup:
```python
def safe_delete(sandbox):
    try:
        sandbox.delete()
    except Exception as e:
        print(f"Warning: cleanup failed: {e}")
        # Continue - sandbox may already be deleted or will auto-cleanup
```

## SDK Version Issues

### Breaking Changes After Update

**Symptoms:**
```
AttributeError: 'Daytona' object has no attribute 'create_image'
TypeError: create() got unexpected keyword argument
```

**Solutions:**
Check SDK version and migrate:
```bash
pip show daytona  # Check version
```

**v0.20.x → v0.21.x Migration:**
```python
# Old (v0.20.x)
from daytona import CreateSandboxParams
sandbox = daytona.create(CreateSandboxParams(language="python"))

# New (v0.21.x)
from daytona import CreateSandboxFromSnapshotParams
sandbox = daytona.create(CreateSandboxFromSnapshotParams(language="python"))
```

See [Migration Guide](https://www.daytona.io/dotfiles/updates/daytona-sdk-v0-21-0-breaking-changes-migration-guide) for complete changes.

## Debugging Tips

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('daytona').setLevel(logging.DEBUG)
```

### Inspect Sandbox State

```python
sandbox = daytona.get(sandbox_id)
sandbox.refresh_data()

print(f"State: {sandbox.state}")
print(f"ID: {sandbox.id}")
print(f"Domain: {sandbox.runner_domain}")
```

### Test Execution Locally

```python
def test_code_locally(code: str):
    """Test code locally before sending to Daytona."""
    import subprocess
    result = subprocess.run(
        ["python", "-c", code],
        capture_output=True,
        text=True,
        timeout=30
    )
    print(f"Exit code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")

# Test first
test_code_locally("print('Hello')")

# Then run in Daytona
result = sandbox.process.code_run("print('Hello')")
```

## Getting Help

1. **Documentation**: https://www.daytona.io/docs
2. **GitHub Issues**: https://github.com/daytonaio/daytona/issues
3. **Discord**: https://discord.gg/daytona
4. **Email Support**: support@daytona.io

When reporting issues, include:
- SDK version (`pip show daytona`)
- Python version
- Full error traceback
- Minimal reproduction code
