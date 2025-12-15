---
name: tdd-orchestrator
version: 2.0
tier: 2
standalone: true
dependencies: []
description: TDD orchestrator for test-driven development discipline, red-green-refactor workflow, and comprehensive testing

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [npm, pytest, go]
---

# TDD Orchestrator - Tier 2

## Phase 0: TDD Setup
```bash
# Check test framework
ls package.json requirements.txt go.mod 2>/dev/null
grep -E "jest|pytest|testing" package.json requirements.txt 2>/dev/null
```

## Phase 1: Red-Green-Refactor
```markdown
# TDD Workflow

## Red: Write Failing Test
\`\`\`javascript
test('adds two numbers', () => {
  expect(add(2, 3)).toBe(5);  // Fails: add not implemented
});
\`\`\`

## Green: Make It Pass
\`\`\`javascript
function add(a, b) {
  return a + b;  // Simplest implementation
}
\`\`\`

## Refactor: Improve
\`\`\`javascript
const add = (a: number, b: number): number => a + b;
\`\`\`
```

## Phase 4: Validation
```bash
# Run tests continuously
npm test -- --watch
# or
pytest --watch
```

## Success Criteria
- [ ] Test-first approach
- [ ] All tests passing
- [ ] Coverage >80%
- [ ] Code refactored
- [ ] Red-green-refactor followed
