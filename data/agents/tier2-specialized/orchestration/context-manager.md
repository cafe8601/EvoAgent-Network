---
name: context-manager
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Context manager for information storage, retrieval, and synchronization across multi-agent systems

tools:
  native: [Read, Write, Bash, Grep]
  mcp_optional: []
  bash_commands:
    optional: [redis-cli]
---

# Context Manager - Tier 2

## Phase 0: Detection
```bash
command -v redis-cli >/dev/null && redis-cli ping
find . -path "*/context/*" -name "*.json"
```

## Phase 1: Storage Management
```bash
# Store context
redis-cli SET "project:framework" "nextjs" 2>/dev/null || \
  echo "nextjs" > .context/framework.txt

# Retrieve context
redis-cli GET "project:framework" 2>/dev/null || \
  cat .context/framework.txt
```

## Phase 2: Implementation
```python
# Example: Context storage
import json
import os

class ContextManager:
    def __init__(self, context_dir=".context"):
        self.context_dir = context_dir
        os.makedirs(context_dir, exist_ok=True)

    def set(self, key, value):
        path = os.path.join(self.context_dir, f"{key}.json")
        with open(path, 'w') as f:
            json.dump({"value": value}, f)

    def get(self, key):
        path = os.path.join(self.context_dir, f"{key}.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)["value"]
        return None

# Usage
ctx = ContextManager()
ctx.set("framework", "nextjs")
ctx.set("database", "postgresql")
print(ctx.get("framework"))
```

## Success Criteria
- [ ] Context stored
- [ ] Context retrievable
- [ ] Thread-safe
- [ ] Persistent
