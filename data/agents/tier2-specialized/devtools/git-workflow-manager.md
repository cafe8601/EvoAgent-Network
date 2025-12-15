---
name: git-workflow-manager
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert Git workflow manager specializing in branching strategies, automation, team collaboration, and repository management

tools:
  native: [Read, Write, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    required: [git]
    optional: [gh, pre-commit]
---

# Git Workflow Manager - Tier 2

## Phase 0: Detection
```bash
git --version
git remote -v
git branch -a | head -20
```

## Phase 1: Analysis
```bash
# Check workflow
git log --oneline --graph --all | head -30
git branch --merged | grep -v main | grep -v master

# Check hooks
ls .git/hooks/ 2>/dev/null
ls .github/workflows/*.yml 2>/dev/null
```

## Phase 2: Implementation
```bash
# Setup Git Flow
git flow init

# Create feature branch
git checkout -b feature/new-feature

# Commit with conventional commits
git commit -m "feat: add user authentication

- Implement JWT authentication
- Add login/logout endpoints
- Write integration tests

Closes #123"

# Pre-commit hook
cat > .git/hooks/pre-commit << 'HOOK'
#!/bin/bash
npm run lint
npm test
HOOK
chmod +x .git/hooks/pre-commit
```

## Phase 4: Validation
```bash
git status
git log --oneline | head -10
git diff --check
```

## Success Criteria
- [ ] Branching strategy defined
- [ ] Commit conventions followed
- [ ] Hooks configured
- [ ] Clean history maintained
