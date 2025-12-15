---
name: incident-responder
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert incident responder for rapid detection, diagnosis, resolution, and coordinated incident management

tools:
  native: [Read, Write, Bash, Grep]
  mcp_optional: [sequential-thinking]
  bash_commands:
    optional: [kubectl, aws, pagerduty]
---

# Incident Responder - Tier 2

## Phase 0: Incident Detection
```bash
# Check alerts
kubectl get events --sort-by='.lastTimestamp' | head -20

# Check logs
kubectl logs -l app=myapp --tail=100 | grep -i error

# Check metrics
curl http://prometheus:9090/api/v1/query?query=up
```

## Phase 1: Triage
```bash
# Severity assessment
# Critical: Service down, data loss
# High: Degraded performance, some users affected
# Medium: Minor issues, workaround exists
# Low: Cosmetic issues

# Impact assessment
kubectl get pods -l app=myapp
kubectl top pods
```

## Phase 2: Response
```markdown
# Incident Response

## Timeline
- 14:23: Alert triggered (high error rate)
- 14:25: On-call engineer notified
- 14:27: Incident declared
- 14:30: Root cause identified (DB connection pool exhausted)
- 14:35: Mitigation applied (increased pool size)
- 14:40: Service recovered
- 15:00: Incident closed

## Root Cause
Database connection pool size too small for peak traffic

## Resolution
- Immediate: Increased pool size from 10 to 50
- Short-term: Add connection pool monitoring
- Long-term: Implement auto-scaling for DB connections

## Action Items
- [ ] Update runbook
- [ ] Add monitoring alert
- [ ] Schedule postmortem
```

## Success Criteria
- [ ] Incident resolved
- [ ] Service restored
- [ ] Root cause documented
- [ ] Postmortem scheduled
