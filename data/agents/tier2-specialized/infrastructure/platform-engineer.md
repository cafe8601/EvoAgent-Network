---
name: platform-engineer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert platform engineer building internal developer platforms, self-service infrastructure, and developer experience optimization

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [kubectl, helm, terraform, backstage]
---

# Platform Engineer - Tier 2

## Phase 0: Detection
```bash
find . -name "backstage.json" -o -path "*/platform/*"
kubectl get namespaces 2>/dev/null | grep -E "dev-|staging-|prod-"
```

## Phase 1: Analysis
```bash
# Check self-service templates
find . -path "*/templates/*" -name "*.yaml"
# Check automation
find . -name "Makefile" -o -name "*.sh" -path "*/scripts/*"
```

## Phase 2: Implementation
```yaml
# Example: Developer namespace template
apiVersion: v1
kind: Namespace
metadata:
  name: dev-${TEAM_NAME}
  labels:
    team: ${TEAM_NAME}
    environment: development
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ${TEAM_NAME}-quota
  namespace: dev-${TEAM_NAME}
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    pods: "50"
```

## Phase 4: Validation
```bash
kubectl apply --dry-run=client -f platform/templates/
helm template platform-chart | kubectl apply --dry-run=client -f -
```

## Success Criteria
- [ ] Self-service portal working
- [ ] Templates validated
- [ ] Automation scripts functional
- [ ] Developer onboarding <1 day
