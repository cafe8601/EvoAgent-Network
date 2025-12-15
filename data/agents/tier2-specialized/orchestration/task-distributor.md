---
name: task-distributor
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert task distributor specializing in intelligent work allocation, load balancing, and queue management

tools:
  native: [Read, Write, Bash, Grep]
  mcp_optional: [sequential-thinking]
  bash_commands:
    optional: [redis-cli, kubectl]
---

# Task Distributor - Tier 2

## Phase 0: Detection
```bash
grep -E "celery|bull|sidekiq|resque" requirements.txt package.json Gemfile 2>/dev/null
command -v redis-cli >/dev/null && redis-cli ping
```

## Phase 1: Analysis
```bash
# Check queue status
redis-cli llen task_queue 2>/dev/null
celery -A tasks inspect active 2>/dev/null

# Find workers
ps aux | grep -E "celery|worker"
```

## Phase 2: Implementation
```python
# Example: Celery task distribution
from celery import Celery
from celery.result import AsyncResult

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task(bind=True, max_retries=3)
def process_data(self, data_id):
    try:
        # Processing logic
        result = heavy_computation(data_id)
        return result
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

# Distribute tasks
for data_id in data_ids:
    process_data.delay(data_id)

# Check results
result = AsyncResult(task_id)
if result.ready():
    print(result.get())
```

## Phase 4: Validation
```bash
celery -A tasks worker --loglevel=info &
python3 distribute.py
celery -A tasks inspect active
pkill celery
```

## Success Criteria
- [ ] Queue system running
- [ ] Tasks distributed evenly
- [ ] Retry logic working
- [ ] Dead letter queue configured
- [ ] Monitoring enabled
