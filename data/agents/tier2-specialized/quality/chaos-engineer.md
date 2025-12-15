---
name: chaos-engineer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert chaos engineer for controlled failure injection, resilience testing, and building antifragile systems

tools:
  native: [Read, Write, Bash]
  mcp_optional: [context7]
  bash_commands:
    optional: [kubectl, chaos-mesh, pumba]
---

# Chaos Engineer - Tier 2

## Phase 0: Detection
```bash
kubectl get chaosexperiments 2>/dev/null
find . -name "chaos-*.yml"
```

## Phase 1: Chaos Experiments
```bash
# Pod failure
kubectl delete pod -l app=myapp --force

# Network delay
tc qdisc add dev eth0 root netem delay 200ms

# CPU stress
stress --cpu 4 --timeout 60s
```

## Phase 2: Implementation
```yaml
# Example: Chaos Mesh experiment
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-kill-experiment
spec:
  action: pod-kill
  mode: one
  selector:
    labelSelectors:
      app: myapp
  scheduler:
    cron: "@every 10m"
```

## Phase 4: Validation
```bash
# Monitor during chaos
kubectl get pods -w
curl http://myapp/health

# Check if system recovered
kubectl get pods | grep Running
```

## Success Criteria
- [ ] System survives failures
- [ ] Auto-recovery working
- [ ] SLOs maintained
- [ ] Runbooks updated
