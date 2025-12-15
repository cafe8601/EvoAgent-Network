# Project Constitution

> **Version**: 1.0  
> **Status**: Active  
> **Effective Date**: [YYYY-MM-DD]  
> **Last Updated**: [YYYY-MM-DD]

---

## Preamble

This Constitution establishes the architectural principles and engineering practices for [PROJECT NAME]. These principles are designed to:

1. **Prevent Over-Engineering**: Resist the temptation to build for imaginary future requirements
2. **Maintain Simplicity**: Keep systems understandable and maintainable
3. **Ensure Quality**: Enforce practices that lead to reliable, testable code
4. **Enable Autonomy**: Provide clear constraints that enable confident decision-making

**Constitutional Authority**: These articles are binding. Violations require explicit justification and must be tracked in the Complexity Register.

---

## Article I: Library-First Principle

### The Principle
**Every feature MUST begin as a standalone library.**

### Rationale
- Libraries enforce modularity and single responsibility
- Libraries are reusable across different contexts
- Libraries enable isolated testing
- Libraries prevent tight coupling to specific frameworks

### Requirements
1. All business logic resides in library modules
2. Libraries have no dependencies on presentation layers
3. Libraries export clean, documented APIs
4. Libraries are framework-agnostic

### Compliance Check
- [ ] Feature implemented as library first?
- [ ] Business logic isolated from framework code?
- [ ] Library API is clean and documented?

### Violations
Violations require justification:

| Feature | Violation | Justification | Alternative Considered |
|---------|-----------|---------------|------------------------|
| [Name]  | [Why not library] | [Business reason] | [Why rejected] |

---

## Article II: CLI Interface Mandate

### The Principle
**Every library MUST provide a Command Line Interface (CLI).**

### Rationale
- CLIs force libraries to have clean, text-based APIs
- CLIs enable automation and scripting
- CLIs support testing through stdin/stdout
- CLIs provide universal access without GUI dependencies

### Requirements
1. CLI accepts input via stdin or arguments
2. CLI outputs results via stdout
3. CLI errors go to stderr
4. CLI supports JSON output format (`--json` flag)
5. CLI provides help text (`--help` flag)

### Compliance Check
- [ ] CLI interface implemented?
- [ ] Stdin/stdout/stderr properly used?
- [ ] JSON output supported?
- [ ] Help text available?

### Example
```bash
# Text input/output
echo "process this" | mycli command

# JSON input/output
echo '{"data": "value"}' | mycli command --json

# Help
mycli command --help
```

### Violations
| Feature | Violation | Justification | Alternative Considered |
|---------|-----------|---------------|------------------------|
| [Name]  | [No CLI]  | [Reason]      | [Why rejected] |

---

## Article III: Test-First Imperative (NON-NEGOTIABLE)

### The Principle
**Tests MUST be written BEFORE implementation. No exceptions.**

### Rationale
- Test-first ensures requirements are clear
- Test-first prevents implementation bias
- Test-first creates executable specifications
- Test-first enables confident refactoring

### The Sacred Sequence
```
1. Write Test
   └─> User Reviews & Approves Test
       └─> Run Test (Expect RED - failure)
           └─> Implement Minimum Code
               └─> Run Test (Expect GREEN - pass)
                   └─> Refactor (if needed)
                       └─> Run Test (Still GREEN)
```

### Requirements
1. **User Approval**: User must review and approve tests before implementation
2. **RED Phase**: Tests must fail initially (proves they test something)
3. **GREEN Phase**: Implementation must pass all tests
4. **REFACTOR Phase**: Improvements must not break tests
5. **Coverage**: Minimum 80% code coverage
6. **Types of Tests**:
   - Unit tests for library code
   - Contract tests for APIs
   - Integration tests for end-to-end flows

### Compliance Check
- [ ] Tests written before implementation?
- [ ] User approved tests?
- [ ] RED phase confirmed (tests failed initially)?
- [ ] GREEN phase confirmed (tests pass now)?
- [ ] Coverage > 80%?

### This Article is NON-NEGOTIABLE
No justifications accepted. No violations tracked. 
**If tests aren't written first, the code doesn't exist.**

---

## Article IV: [Reserved for Project-Specific Principle]

### The Principle
[Define a principle specific to your project's domain]

### Rationale
[Why this principle matters for your project]

### Requirements
[Specific requirements]

### Compliance Check
[Checklist items]

---

## Article V: [Reserved for Project-Specific Principle]

### The Principle
[Define another project-specific principle]

---

## Article VI: [Reserved for Project-Specific Principle]

### The Principle
[Define another project-specific principle]

---

## Article VII: Simplicity Gate

### The Principle
**Maximum 3 projects per solution. No future-proofing.**

### Rationale
- More projects = more complexity
- Future requirements are often wrong
- YAGNI (You Aren't Gonna Need It)
- Optimize for current needs, not imagined futures

### Requirements
1. **Project Limit**: ≤3 projects total
2. **No Speculative Features**: Build only what's needed now
3. **No "Maybe Later" Code**: Remove TODO placeholders
4. **No Generic Frameworks**: Solve specific problems

### Project Count
**Current**: [X] / 3 projects

**Projects**:
1. [Project 1 Name] - [Purpose]
2. [Project 2 Name] - [Purpose]
3. [Project 3 Name] - [Purpose]

### Compliance Check
- [ ] Using ≤3 projects?
- [ ] No speculative features?
- [ ] No "just in case" code?
- [ ] Solving actual, current problems?

### Violations
| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 4th project | [Reason] | [Why 3 projects insufficient] |
| Future-proofing | [Reason] | [Why current need insufficient] |

---

## Article VIII: Anti-Abstraction Gate

### The Principle
**Use frameworks directly. No abstraction layers. Single model representation.**

### Rationale
- Abstractions hide complexity, not eliminate it
- Wrapper libraries add maintenance burden
- Multiple models create synchronization problems
- Direct framework usage is more maintainable

### Requirements
1. **No Framework Wrappers**: Use Express/Django/etc. directly
2. **Single Model**: One representation of domain objects
3. **No Mapping Layers**: No DTO ↔ Entity ↔ ViewModel chains
4. **No "Future-Proof" Abstractions**: Don't abstract for framework swaps

### Common Violations to Avoid
```typescript
// ❌ BAD: Wrapper abstraction
class MyDatabaseWrapper {
  query() { /* wraps underlying ORM */ }
}

// ✅ GOOD: Direct framework usage
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

// ❌ BAD: Multiple model representations
interface UserDTO { }      // API layer
interface UserEntity { }   // Database layer  
interface UserModel { }    // Business layer

// ✅ GOOD: Single model
interface User { }  // Used everywhere
```

### Compliance Check
- [ ] Using frameworks directly (no wrappers)?
- [ ] Single model representation?
- [ ] No unnecessary mapping layers?
- [ ] No "future-proof" abstractions?

### Violations
| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Framework wrapper | [Reason] | [Why direct usage insufficient] |
| Multiple models | [Reason] | [Why single model insufficient] |

---

## Article IX: Integration-First Testing

### The Principle
**Test with real systems first. Mock only when necessary.**

### Rationale
- Integration tests catch real problems
- Mocks can hide integration issues
- Real databases/services are more reliable tests
- Contract tests ensure API compatibility

### Requirements
1. **Contract Tests**: Define and test API contracts first
2. **Real Systems**: Use actual databases, not in-memory
3. **Test Databases**: Separate test instances, not mocks
4. **Mock Last Resort**: Mock only external APIs you don't control

### Test Hierarchy (Preference Order)
```
1. Integration Tests (Real DB, Real Services)
   └─> Most valuable, test actual behavior

2. Contract Tests (Real API Calls, Schema Validation)
   └─> Ensure API compatibility

3. Unit Tests (Isolated Logic)
   └─> Fast feedback, but limited scope

4. Mocked Tests (Only when unavoidable)
   └─> Least reliable, use sparingly
```

### Compliance Check
- [ ] Contracts defined (OpenAPI, GraphQL schema, etc.)?
- [ ] Contract tests written?
- [ ] Integration tests use real database?
- [ ] Mocking minimized?

### Example Setup
```typescript
// ✅ GOOD: Integration test with real DB
beforeAll(async () => {
  // Spin up actual test database
  await setupTestDatabase();
});

it('should create user in real database', async () => {
  const user = await createUser({ name: 'Test' });
  const dbUser = await db.users.findUnique({ where: { id: user.id } });
  expect(dbUser.name).toBe('Test');
});

// ✅ GOOD: Contract test
it('should match OpenAPI schema', async () => {
  const response = await request(app).post('/api/users').send(validUser);
  expect(response.body).toMatchSchema(userSchema);
});

// ⚠️ ACCEPTABLE: Mock external API
it('should handle external API failure', async () => {
  // Mock Stripe API (external service we don't control)
  mockStripe.charge.mockRejectedValue(new Error('Payment failed'));
});
```

### Violations
| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Mocking internal service | [Reason] | [Why real service insufficient] |

---

## Complexity Register

Track all Constitutional violations here. Every violation requires:
1. **What**: Which article was violated
2. **Why**: Business justification
3. **Alternative**: What simpler approach was considered and why rejected

| Article | Feature | Violation | Justification | Alternative Rejected | Date |
|---------|---------|-----------|---------------|---------------------|------|
| VII     | [Feature] | 4th project added | [Reason] | [Why 3 insufficient] | [Date] |
| VIII    | [Feature] | Added mapper layer | [Reason] | [Why single model insufficient] | [Date] |

**Complexity Score**: [Low/Medium/High/Critical]

### Scoring
- **Low**: 0-1 violations
- **Medium**: 2-3 violations
- **High**: 4-5 violations  
- **Critical**: 6+ violations (⚠️ Architecture review required)

---

## Amendment Process

### How to Amend
1. Propose amendment with clear rationale
2. Team discussion and vote
3. Document in version history
4. Update effective date

### Version History

| Version | Date | Changes | Rationale |
|---------|------|---------|-----------|
| 1.0     | [Date] | Initial constitution | - |

---

## Enforcement

### Review Process
1. **Pre-Implementation**: Check plan against Constitution
2. **During Implementation**: Verify compliance in code reviews
3. **Post-Implementation**: Audit Complexity Register

### Code Review Checklist
- [ ] Article I: Library-first approach followed?
- [ ] Article II: CLI interface provided?
- [ ] Article III: Tests written first? User approved?
- [ ] Article VII: Project count ≤3? No future-proofing?
- [ ] Article VIII: Direct framework usage? Single model?
- [ ] Article IX: Integration tests? Real systems?

### Violations Require
1. Explicit acknowledgment in code review
2. Entry in Complexity Register
3. Justification documented
4. Alternative approaches documented

---

## Appendix: Rationale for Each Article

### Why Library-First (Article I)?
Prevents business logic from becoming entangled with presentation concerns. Forces modularity.

### Why CLI Interface (Article II)?
Universal access. Enables automation. Forces clean APIs. Supports testing.

### Why Test-First (Article III)?
Ensures requirements are clear before coding. Creates executable specifications. Enables confident refactoring.

### Why Simplicity (Article VII)?
Complexity is the enemy of maintainability. YAGNI prevents over-engineering.

### Why Anti-Abstraction (Article VIII)?
Abstractions have a cost. They should solve actual problems, not theoretical ones.

### Why Integration-First Testing (Article IX)?
Integration tests catch real problems that unit tests miss. Real systems are more reliable tests than mocks.

---

**This Constitution is a living document. It evolves with the project, but changes require deliberate consideration and team consensus.**
