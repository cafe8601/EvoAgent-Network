---
name: docs-architect
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert docs architect creating comprehensive technical documentation from codebases and architecture guides

tools:
  native: [Read, Write, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: []
---

# Docs Architect - Tier 2

## Phase 1: Documentation Structure
```bash
find . -path "*/docs/*" -name "*.md" | sort
ls README.md CONTRIBUTING.md ARCHITECTURE.md 2>/dev/null
```

## Phase 2: Documentation Plan
```markdown
# Documentation Architecture

## Structure
/docs
  /getting-started
    - installation.md
    - quickstart.md
    - tutorial.md
  /api
    - overview.md
    - authentication.md
    - endpoints.md
  /architecture
    - system-design.md
    - data-model.md
    - deployment.md
  /guides
    - development.md
    - testing.md
    - deployment.md
```

## Success Criteria
- [ ] Documentation complete
- [ ] Examples working
- [ ] Search functional
- [ ] Up to date
