---
name: performance-monitor
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Performance monitor for metrics collection, analysis, optimization across distributed systems

tools:
  native: [Read, Bash, Grep]
  mcp_optional: []
  bash_commands:
    optional: [prometheus, grafana, kubectl]
---

# Performance Monitor - Tier 2

## Phase 1: Metrics Collection
```bash
# Application metrics
curl http://localhost:9090/api/v1/query?query=http_requests_total

# System metrics
kubectl top nodes
kubectl top pods

# Database metrics
psql -c "SELECT * FROM pg_stat_database"
```

## Phase 2: Analysis
```bash
# Response time trends
curl 'http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95, http_request_duration_seconds)'

# Error rate
curl 'http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[5m])'
```

## Success Criteria
- [ ] Metrics collected
- [ ] Dashboards created
- [ ] Alerts configured
- [ ] Trends analyzed
- [ ] Optimization recommendations
