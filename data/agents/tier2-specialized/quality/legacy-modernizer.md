---
name: legacy-modernizer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert legacy system modernizer specializing in incremental migration, risk-free modernization, and business continuity

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7, sequential-thinking]
  bash_commands:
    optional: [git]
---

# Legacy Modernizer - Tier 2

## Phase 0: Assessment
```bash
# Find legacy code indicators
grep -r "var \|function(" . --include="*.js" | wc -l
find . -name "*.py" -exec head -1 {} \; | grep -v "#!/usr/bin/env python3" | wc -l

# Check dependencies
npm outdated 2>/dev/null
pip list --outdated 2>/dev/null
```

## Phase 1: Analysis
```bash
# Find oldest files
find . -name "*.{js,py}" -printf '%T+ %p\n' | sort | head -20

# Check for deprecated patterns
grep -r "var \|Promise.*then\|callback" . --include="*.js"
```

## Phase 2: Modernization Strategy
```markdown
# Modernization Roadmap

## Assessment
- Legacy: ES5 JavaScript, callback-based
- Target: ES2023+, async/await, TypeScript
- Risk: High (production system)

## Incremental Approach
### Phase 1: Safety Net (2 weeks)
- Add comprehensive tests
- Setup CI/CD
- Create staging environment

### Phase 2: Tool Update (2 weeks)
- Update build tools
- Migrate to modern bundler
- Add linting/formatting

### Phase 3: Code Migration (4 weeks)
- Convert callbacks → Promises → async/await
- Add TypeScript gradually
- Refactor module by module

### Phase 4: Validation (2 weeks)
- Performance testing
- Security audit
- User acceptance testing
```

## Success Criteria
- [ ] Tests cover legacy code
- [ ] Migration incremental
- [ ] No downtime
- [ ] Business continuity maintained
- [ ] Modern patterns adopted
