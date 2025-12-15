# Tasks: [FEATURE NAME]

> **Feature Number**: [###]  
> **Status**: Not Started | In Progress | Complete  
> **Created**: YYYY-MM-DD  
> **Last Updated**: YYYY-MM-DD

---

## Task Execution Rules

### Test-Driven Development (Article III - NON-NEGOTIABLE)

**EVERY implementation task MUST follow this sequence**:

1. **Write Test** → User reviews and approves
2. **Run Test** → Confirm it FAILS (RED)
3. **Implement** → Write minimum code to pass
4. **Run Test** → Confirm it PASSES (GREEN)
5. **Refactor** → Improve without breaking tests

**NO IMPLEMENTATION without prior test approval.**

---

### Task Dependencies

- **Sequential**: Task B requires Task A completion
- **Parallel**: Tasks can run simultaneously `[P]`
- **Checkpoint**: Validation point before continuing `[CHECKPOINT]`

---

## User Story 1: [Story Name] (Priority: P1)

> **From Spec**: [Reference to spec.md user scenario]  
> **Estimated Effort**: [Small/Medium/Large]  
> **Dependencies**: [None / Task IDs]

---

### Phase 1: Setup & Infrastructure `[P]`

#### Task 1.1: Database Schema
**File**: `migrations/001_create_[table].sql`  
**Type**: Schema Definition  
**Dependencies**: None  
**Parallel**: Yes `[P]`

**Steps**:
1. Create migration file
2. Define table schema
3. Add indexes
4. Test migration up/down

**Validation**:
- [ ] Migration runs successfully
- [ ] Rollback works
- [ ] Indexes created

---

#### Task 1.2: Data Model Class
**File**: `src/lib/[feature]/models/[Model].ts`  
**Type**: Model Definition  
**Dependencies**: Task 1.1  

**Steps**:
1. Define TypeScript interface
2. Add validation rules
3. Export model

**Validation**:
- [ ] Type definitions complete
- [ ] Validation logic added
- [ ] No compilation errors

---

### Phase 2: Core Logic (TDD) `[CHECKPOINT]`

#### Task 2.1: Write Service Tests
**File**: `tests/unit/[Service].test.ts`  
**Type**: Test (RED Phase)  
**Dependencies**: Task 1.2  

**Test Cases**:
```typescript
describe('[ServiceName]', () => {
  describe('method1', () => {
    it('should [expected behavior] when [condition]', async () => {
      // Arrange
      const input = [...];
      
      // Act
      const result = await service.method1(input);
      
      // Assert
      expect(result).toEqual([...]);
    });
    
    it('should throw error when [invalid condition]', async () => {
      // Arrange & Act & Assert
      await expect(service.method1(invalid)).rejects.toThrow();
    });
  });
});
```

**User Approval Required**:
- [ ] User reviews test scenarios
- [ ] User confirms tests match requirements
- [ ] User approves proceeding to implementation

**Validation** (RED Phase):
- [ ] Tests written
- [ ] Tests run and FAIL (as expected)
- [ ] Failure messages are clear

---

#### Task 2.2: Implement Service
**File**: `src/lib/[feature]/services/[Service].ts`  
**Type**: Implementation (GREEN Phase)  
**Dependencies**: Task 2.1 (after user approval)  

**Implementation Steps**:
1. Create service class
2. Implement methods to pass tests
3. Add error handling
4. Add logging

**Constitutional Check**:
- [ ] No premature abstraction (Article VIII)
- [ ] Direct framework usage (Article VIII)
- [ ] Single responsibility

**Validation** (GREEN Phase):
- [ ] All tests pass
- [ ] No new failing tests
- [ ] Code coverage > 80%

---

#### Task 2.3: Refactor Service
**File**: `src/lib/[feature]/services/[Service].ts`  
**Type**: Refactoring (REFACTOR Phase)  
**Dependencies**: Task 2.2  

**Refactoring Goals**:
- [ ] Remove code duplication
- [ ] Improve variable naming
- [ ] Simplify complex logic
- [ ] Add code comments

**Validation**:
- [ ] All tests still pass
- [ ] No new complexity introduced
- [ ] Code is more readable

---

### Phase 3: API Layer (TDD) `[CHECKPOINT]`

#### Task 3.1: Write Contract Tests
**File**: `tests/contracts/[endpoint].contract.test.ts`  
**Type**: Test (RED Phase)  
**Dependencies**: Task 2.3  

**Contract Tests**:
```typescript
describe('[Endpoint] Contract', () => {
  it('should match OpenAPI schema for valid request', async () => {
    // Arrange
    const validRequest = {...};
    
    // Act
    const response = await request(app)
      .post('/api/[resource]')
      .send(validRequest);
    
    // Assert
    expect(response.status).toBe(201);
    expect(response.body).toMatchSchema(expectedSchema);
  });
  
  it('should return 400 for invalid request', async () => {
    // Test schema validation
  });
});
```

**User Approval Required**:
- [ ] User reviews API contract tests
- [ ] User confirms tests match spec
- [ ] User approves implementation

**Validation** (RED Phase):
- [ ] Contract tests written
- [ ] Tests FAIL (no endpoint exists yet)

---

#### Task 3.2: Implement API Endpoint
**File**: `src/api/routes/[resource].ts`  
**Type**: Implementation (GREEN Phase)  
**Dependencies**: Task 3.1 (after user approval)  

**Implementation Steps**:
1. Create route handler
2. Add input validation (Joi/Zod)
3. Call service layer
4. Format response
5. Add error handling

**Files to Create**:
- `src/api/routes/[resource].ts` - Route definitions
- `src/api/controllers/[Resource]Controller.ts` - Request handlers
- `src/api/validators/[resource].validator.ts` - Input validation

**Constitutional Check**:
- [ ] Using ≤3 projects? (Article VII)
- [ ] No abstraction layers? (Article VIII)

**Validation** (GREEN Phase):
- [ ] All contract tests pass
- [ ] All unit tests still pass
- [ ] OpenAPI spec matches implementation

---

#### Task 3.3: Refactor API Layer
**File**: Multiple API files  
**Type**: Refactoring (REFACTOR Phase)  
**Dependencies**: Task 3.2  

**Refactoring Goals**:
- [ ] Extract common middleware
- [ ] Improve error messages
- [ ] Add request/response logging

---

### Phase 4: Integration Testing `[CHECKPOINT]`

#### Task 4.1: Write Integration Tests
**File**: `tests/integration/[feature].integration.test.ts`  
**Type**: Test (Integration)  
**Dependencies**: Task 3.3  

**Integration Test Scenarios**:
```typescript
describe('[Feature] Integration', () => {
  beforeAll(async () => {
    // Setup real database
    await setupTestDatabase();
  });
  
  it('should complete end-to-end flow', async () => {
    // Arrange: Setup test data in real DB
    const testData = await seedTestData();
    
    // Act: Make real API calls
    const response = await request(app)
      .post('/api/[resource]')
      .send(testData);
    
    // Assert: Verify database state
    const dbRecord = await db.query('SELECT * FROM [table] WHERE id = $1', [response.body.id]);
    expect(dbRecord).toMatchObject(expectedRecord);
  });
});
```

**Validation**:
- [ ] Integration tests pass with real database
- [ ] Integration tests pass with real services
- [ ] No mocking used (Article IX preference)

---

#### Task 4.2: Load Testing
**File**: `tests/load/[feature].load.test.ts`  
**Type**: Performance Test  
**Dependencies**: Task 4.1  

**Load Test Scenarios**:
- Concurrent users: [number]
- Requests per second: [number]
- Duration: [time]

**Performance Targets**:
- [ ] API latency p95 < [X]ms
- [ ] No errors under load
- [ ] Memory usage stable

---

### Phase 5: CLI Interface (Article II) `[P]`

#### Task 5.1: Write CLI Tests
**File**: `tests/cli/[command].cli.test.ts`  
**Type**: Test (RED Phase)  
**Dependencies**: Task 2.3  
**Parallel**: Yes (can run parallel to API work) `[P]`

**CLI Test Cases**:
```typescript
describe('CLI: [command]', () => {
  it('should process stdin and output to stdout', async () => {
    // Arrange
    const input = 'test input';
    
    // Act
    const result = await runCLI('[command]', { stdin: input });
    
    // Assert
    expect(result.stdout).toContain('expected output');
    expect(result.exitCode).toBe(0);
  });
  
  it('should output JSON when --json flag used', async () => {
    // Test JSON output format
  });
});
```

**User Approval Required**:
- [ ] User reviews CLI behavior
- [ ] User approves CLI interface design

---

#### Task 5.2: Implement CLI
**File**: `src/cli/commands/[command].ts`  
**Type**: Implementation (GREEN Phase)  
**Dependencies**: Task 5.1 (after user approval)  

**Implementation Steps**:
1. Create CLI command handler
2. Parse stdin/arguments
3. Call library functions
4. Output to stdout/stderr
5. Support JSON format

**Constitutional Check**:
- [ ] CLI calls library code (Article II)
- [ ] No business logic in CLI layer

---

## Parallel Work Tracks

Tasks marked with `[P]` can be worked on simultaneously:

**Track A: Core Logic**
- Task 2.1 → Task 2.2 → Task 2.3

**Track B: Database**
- Task 1.1 (parallel)

**Track C: CLI**
- Task 5.1 → Task 5.2 (parallel to Track A after Task 2.3)

---

## Checkpoints

Before proceeding past each checkpoint, verify:

### Checkpoint 1: After Phase 2 (Core Logic)
- [ ] All unit tests pass
- [ ] Service layer complete
- [ ] No Constitutional violations
- [ ] Code review completed

### Checkpoint 2: After Phase 3 (API Layer)
- [ ] All contract tests pass
- [ ] API matches OpenAPI spec
- [ ] Integration tests pass
- [ ] Load testing completed

### Checkpoint 3: After Phase 5 (CLI)
- [ ] CLI tests pass
- [ ] CLI documented
- [ ] Help text clear

---

## User Story 2: [Story Name] (Priority: P2)

> **From Spec**: [Reference]  
> **Estimated Effort**: [Size]  
> **Dependencies**: [User Story 1 / Specific Tasks]

[Repeat task breakdown structure]

---

## User Story 3: [Story Name] (Priority: P3)

[Repeat task breakdown structure]

---

## Definition of Done

A task is "done" when:

### For Test Tasks
- [ ] Tests written and reviewed
- [ ] User has approved test scenarios
- [ ] Tests run and fail (RED phase confirmed)
- [ ] Test coverage is comprehensive

### For Implementation Tasks
- [ ] Code written to pass tests
- [ ] All tests pass (GREEN phase confirmed)
- [ ] Code review completed
- [ ] Documentation updated
- [ ] No Constitutional violations

### For Refactoring Tasks
- [ ] Code improved
- [ ] All tests still pass
- [ ] No new complexity introduced
- [ ] Team reviewed changes

---

## Task Progress Tracking

| Task ID | Description | Status | Assignee | Notes |
|---------|-------------|--------|----------|-------|
| 1.1     | Database Schema | ☐ Not Started | - | - |
| 1.2     | Data Model | ☐ Not Started | - | Depends on 1.1 |
| 2.1     | Service Tests | ☐ Not Started | - | User approval needed |
| 2.2     | Service Implementation | ☐ Not Started | - | After 2.1 approval |
| 2.3     | Service Refactor | ☐ Not Started | - | After 2.2 |
| 3.1     | Contract Tests | ☐ Not Started | - | User approval needed |
| 3.2     | API Implementation | ☐ Not Started | - | After 3.1 approval |
| 3.3     | API Refactor | ☐ Not Started | - | After 3.2 |
| 4.1     | Integration Tests | ☐ Not Started | - | - |
| 4.2     | Load Testing | ☐ Not Started | - | - |
| 5.1     | CLI Tests | ☐ Not Started | - | Parallel to 2.x `[P]` |
| 5.2     | CLI Implementation | ☐ Not Started | - | After 5.1 approval |

**Status Legend**:
- ☐ Not Started
- ◐ In Progress
- ◕ In Review
- ☑ Complete
- ☒ Blocked

---

## Notes & References

- **Specification**: `../spec.md`
- **Implementation Plan**: `../plan.md`
- **Contracts**: `../contracts/`
- **Progress Updates**: [Link to project board]
