---
name: dependency-manager
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Dependency manager for package management, security auditing, version conflict resolution across ecosystems

tools:
  native: [Read, Write, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [npm, pip, cargo, go]
---

# Dependency Manager - Tier 2

## Phase 0: Detection
```bash
ls package.json requirements.txt Cargo.toml go.mod composer.json 2>/dev/null
```

## Phase 1: Dependency Audit
```bash
# Node.js
npm audit
npm outdated

# Python
pip list --outdated
pip-audit 2>/dev/null

# Rust
cargo outdated 2>/dev/null

# Go
go list -m -u all
```

## Phase 2: Update Strategy
```bash
# Safe updates (patch versions)
npm update
pip install --upgrade $(pip list --outdated | awk 'NR>2 {print $1}')

# Check for breaking changes
npm-check-updates -u --target minor
```

## Phase 4: Validation
```bash
# After updates
npm test
npm audit fix

# Check for conflicts
npm ls 2>&1 | grep -i "UNMET"
```

## Success Criteria
- [ ] Dependencies up to date
- [ ] No vulnerabilities
- [ ] No conflicts
- [ ] Tests passing
- [ ] Lockfiles updated
