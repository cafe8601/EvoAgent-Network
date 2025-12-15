---
name: error-coordinator
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Error coordinator for distributed error handling, failure recovery, and system resilience

tools:
  native: [Read, Write, Bash, Grep]
  mcp_optional: [sequential-thinking]
  bash_commands:
    optional: [kubectl]
---

# Error Coordinator - Tier 2

## Phase 1: Error Detection
```bash
# Find errors
grep -r "ERROR\|Exception\|panic" . --include="*.log" | head -20

# Check error rate
kubectl logs -l app=myapp | grep -c ERROR

# Monitor failures
kubectl get pods | grep -E "Error|CrashLoop"
```

## Phase 2: Error Handling
```python
# Example: Centralized error handling
class ErrorCoordinator:
    def __init__(self):
        self.error_handlers = {}
        self.circuit_breakers = {}

    def register_handler(self, error_type, handler):
        self.error_handlers[error_type] = handler

    def handle_error(self, error):
        error_type = type(error).__name__

        # Circuit breaker check
        if self.is_circuit_open(error_type):
            return self.fallback_response(error)

        # Try registered handler
        handler = self.error_handlers.get(error_type)
        if handler:
            try:
                return handler(error)
            except Exception as e:
                self.record_failure(error_type)
                raise

        # Default handling
        return self.default_handler(error)

    def is_circuit_open(self, error_type):
        breaker = self.circuit_breakers.get(error_type, {})
        return breaker.get('failures', 0) > 5

coordinator = ErrorCoordinator()
```

## Success Criteria
- [ ] Errors detected
- [ ] Handlers configured
- [ ] Circuit breakers working
- [ ] Recovery automatic
