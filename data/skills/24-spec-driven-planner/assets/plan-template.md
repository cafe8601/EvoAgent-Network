# Implementation Plan: [FEATURE NAME]

> **Feature Number**: [###]  
> **Status**: Planning | In Progress | Complete  
> **Created**: YYYY-MM-DD  
> **Last Updated**: YYYY-MM-DD

---

## Phase -1: Pre-Implementation Gates

### Constitutional Compliance Check

Review against all 9 Constitutional Articles before proceeding.

#### Article I: Library-First Principle
- [ ] **Compliance**: Is this feature starting as a library?
- [ ] **Justification**: [If no, explain why]

#### Article II: CLI Interface Mandate
- [ ] **Compliance**: Does the library have a CLI interface?
- [ ] **Justification**: [If no, explain why]

#### Article III: Test-First Imperative (NON-NEGOTIABLE)
- [ ] **Compliance**: Will tests be written before implementation?
- [ ] **Commitment**: [Confirm Red-Green-Refactor cycle]

#### Article VII: Simplicity Gate
- [ ] **Compliance**: Using ≤3 projects?
- [ ] **Current Count**: [Number of projects]
- [ ] **Justification**: [If >3, explain why simpler approach rejected]

#### Article VIII: Anti-Abstraction Gate
- [ ] **Compliance**: Using framework directly (no wrappers)?
- [ ] **Compliance**: Single model representation (no mapping layers)?
- [ ] **Justification**: [If no, explain architectural necessity]

#### Article IX: Integration-First Gate
- [ ] **Contracts Defined**: [Yes/No]
- [ ] **Contract Tests Written**: [Yes/No]
- [ ] **Integration Tests First**: [Yes/No]

---

### Complexity Tracking

| Constitutional Violation | Why Needed | Simpler Alternative Rejected Because |
|--------------------------|------------|-------------------------------------|
| [If any violations]      | [Reason]   | [Why simpler approach insufficient] |

**Current Complexity Score**: [Low/Medium/High/Critical]

---

## Phase 0: Technical Foundation

### Technology Stack Selection

#### Core Technologies
- **Language/Runtime**: [e.g., TypeScript/Node.js 20+]
  - **Rationale**: [Why chosen]
  - **Alternatives Considered**: [Other options and why rejected]

- **Framework**: [e.g., Express.js 4.x]
  - **Rationale**: [Why chosen]
  - **Alternatives Considered**: [Other options]

- **Database**: [e.g., PostgreSQL 15+]
  - **Rationale**: [Why chosen]
  - **Alternatives Considered**: [Other options]

- **Real-time**: [e.g., WebSocket / SignalR / Socket.io]
  - **Rationale**: [Why chosen]
  - **Alternatives Considered**: [Other options]

#### Supporting Technologies
- **Caching**: [e.g., Redis]
- **Message Queue**: [e.g., RabbitMQ]
- **Monitoring**: [e.g., Sentry]
- **Logging**: [e.g., Winston]

---

### Project Structure

```
[project-name]/
├── src/
│   ├── lib/              # Core library (Article I)
│   │   ├── [feature]/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   └── index.ts
│   ├── cli/              # CLI interface (Article II)
│   │   └── commands/
│   ├── api/              # Optional API layer
│   │   ├── routes/
│   │   ├── controllers/
│   │   └── middleware/
│   └── contracts/        # API contracts (Article IX)
│       ├── openapi.json
│       └── signalr-spec.md
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contracts/
└── docs/
```

---

### Architecture Decisions

#### Decision 1: [Architecture Choice]
**Context**: [What problem are we solving?]  
**Decision**: [What did we decide?]  
**Rationale**: [Why this approach?]  
**Consequences**: [What are the trade-offs?]  
**Constitutional Review**: [Which articles apply?]

#### Decision 2: [Architecture Choice]
**Context**: [Problem context]  
**Decision**: [Decision made]  
**Rationale**: [Reasoning]  
**Consequences**: [Trade-offs]

---

## Phase 1: Data Model Design

### Database Schema

#### Table 1: [table_name]
```sql
CREATE TABLE [table_name] (
  id BIGSERIAL PRIMARY KEY,
  [field1] VARCHAR(255) NOT NULL,
  [field2] JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_[table]_[field] ON [table_name]([field]);
```

**Rationale**: [Why this schema design?]  
**Constraints**: [Business rules enforced]  
**Indexes**: [Performance considerations]

#### Table 2: [table_name]
```sql
-- Schema definition
```

---

### Data Model Classes

#### Model 1: [ModelName]
```typescript
interface [ModelName] {
  id: string;
  [field1]: string;
  [field2]: number;
  createdAt: Date;
  updatedAt: Date;
}
```

**Validation Rules**:
- `field1`: [validation rules]
- `field2`: [validation rules]

**Business Logic**:
- [Rule 1]
- [Rule 2]

---

## Phase 2: API Contracts (Article IX)

### REST API Contract

See `contracts/openapi.json` for full specification.

#### Endpoint 1: [Endpoint Name]
```
POST /api/[resource]
Content-Type: application/json

Request:
{
  "[field]": "value"
}

Response (201 Created):
{
  "id": "uuid",
  "[field]": "value",
  "createdAt": "2024-01-01T00:00:00Z"
}

Response (400 Bad Request):
{
  "error": "Validation failed",
  "details": [...]
}
```

**Contract Tests**:
- [ ] Request schema validation
- [ ] Response schema validation
- [ ] Error case handling

---

### Real-time API Contract

See `contracts/signalr-spec.md` for full specification.

#### Event 1: [EventName]
```typescript
// Server -> Client
hub.on('[EventName]', (data: EventPayload) => {
  // Client handling
});

interface EventPayload {
  [field]: string;
  timestamp: string;
}
```

**Contract Tests**:
- [ ] Event payload validation
- [ ] Connection lifecycle
- [ ] Error handling

---

## Phase 3: Implementation Sequence

### User Story 1: [Story Name] (Priority: P1)

#### Step 1: Write Tests (Article III)
**File**: `tests/integration/[feature].test.ts`
```typescript
describe('[Feature]', () => {
  it('should [expected behavior]', async () => {
    // Arrange
    // Act
    // Assert
  });
});
```

**User Approval Required**: 
- [ ] User has reviewed test cases
- [ ] User confirms test scenarios match requirements

#### Step 2: Run Tests (Expect Failure)
```bash
npm test
# Expected: RED (tests fail)
```

#### Step 3: Implement Minimum Code
**Files to Create**:
- `src/lib/[feature]/models/[Model].ts`
- `src/lib/[feature]/services/[Service].ts`

**Constitutional Check**:
- [ ] No premature abstraction (Article VIII)
- [ ] Direct framework usage (Article VIII)

#### Step 4: Run Tests (Expect Pass)
```bash
npm test
# Expected: GREEN (tests pass)
```

#### Step 5: Refactor (If Needed)
**Refactoring Goals**:
- [ ] Remove duplication
- [ ] Improve naming
- [ ] Simplify logic

**Constitutional Check**:
- [ ] Still using ≤3 projects? (Article VII)
- [ ] No unnecessary abstractions? (Article VIII)

---

### User Story 2: [Story Name] (Priority: P2)

[Repeat structure above]

---

## Phase 4: Integration & Deployment

### Integration Testing Checklist
- [ ] All contract tests pass
- [ ] Integration tests with real database
- [ ] Integration tests with real message queue
- [ ] Load testing completed
- [ ] Security testing completed

### Deployment Prerequisites
- [ ] Environment variables documented
- [ ] Database migrations prepared
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured

---

## Research & Prototyping

Separate detailed technical research into `research.md`.

### Research Areas
1. **[Topic 1]**: See `research.md` section 1
2. **[Topic 2]**: See `research.md` section 2

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [How to mitigate] |
| [Risk 2] | High/Med/Low | High/Med/Low | [How to mitigate] |

---

## Performance Considerations

### Expected Load
- **Concurrent Users**: [number]
- **Requests Per Second**: [number]
- **Data Volume**: [size]

### Optimization Strategy
1. [Strategy 1 - e.g., "Database query optimization"]
2. [Strategy 2 - e.g., "Caching strategy"]
3. [Strategy 3 - e.g., "Connection pooling"]

### Performance Targets
- **API Latency (p95)**: < [X]ms
- **Database Query Time**: < [X]ms
- **Memory Usage**: < [X]MB

---

## Validation Checklist

Before implementation:

- [ ] All Constitutional Gates passed (Phase -1)
- [ ] Technology stack approved
- [ ] Data model designed
- [ ] API contracts defined
- [ ] Contract tests written
- [ ] Implementation sequence clear
- [ ] No complexity violations unaddressed
- [ ] TDD commitment confirmed

---

## Notes & References

- **Specification**: `../spec.md`
- **Research**: `research.md`
- **Data Model**: `data-model.md`
- **Contracts**: `contracts/`
- **Architecture Decisions**: [Links to ADRs]
