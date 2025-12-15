# Feature Specification: [FEATURE NAME]

> **Status**: Draft | In Review | Approved | Implemented  
> **Priority**: P1 (Critical) | P2 (High) | P3 (Medium) | P4 (Low)  
> **Estimated Complexity**: Small | Medium | Large | XL  
> **Created**: YYYY-MM-DD  
> **Last Updated**: YYYY-MM-DD

---

## User Scenarios & Testing (REQUIRED)

Priority-based user stories that are independently testable.

### P1: Critical Path (Must-Have)

#### Scenario 1: [Primary User Goal]
**As a** [user type]  
**I want to** [action]  
**So that** [business value]

**Acceptance Criteria** (Given-When-Then format):
```gherkin
Given [initial context]
  And [additional context]
When [action taken]
Then [expected outcome]
  And [additional outcome]
```

**Test Cases**:
- [ ] Test case 1: [description]
- [ ] Test case 2: [description]

---

### P2: Important (Should-Have)

#### Scenario 2: [Secondary User Goal]
**As a** [user type]  
**I want to** [action]  
**So that** [business value]

**Acceptance Criteria**:
```gherkin
Given [context]
When [action]
Then [outcome]
```

---

### P3: Nice-to-Have (Could-Have)

#### Scenario 3: [Enhancement]
**As a** [user type]  
**I want to** [action]  
**So that** [benefit]

---

## Requirements (REQUIRED)

### Functional Requirements

**FR-001**: [Requirement Description]
- **Priority**: P1 | P2 | P3
- **Rationale**: [Why this is needed]
- **Dependencies**: [FR-XXX, FR-YYY, or "None"]
- **[NEEDS CLARIFICATION]**: [If ambiguous, mark here]

**FR-002**: [Requirement Description]
- **Priority**: P1
- **Rationale**: [Why this is needed]
- **Dependencies**: None

**FR-003**: [Requirement Description]
- **Priority**: P2
- **Rationale**: [Why this is needed]
- **Dependencies**: FR-001

---

### Non-Functional Requirements

**NFR-001: Performance**
- [Specific metric, e.g., "API response time < 200ms for 95th percentile"]

**NFR-002: Security**
- [Specific requirement, e.g., "All data encrypted at rest and in transit"]

**NFR-003: Scalability**
- [Specific target, e.g., "Support 10,000 concurrent users"]

**NFR-004: Reliability**
- [Specific SLA, e.g., "99.9% uptime"]

---

### Core Entities

Define the primary domain objects/entities:

#### Entity 1: [Name]
**Purpose**: [What this entity represents]  
**Key Attributes**:
- `attribute1`: [type] - [description]
- `attribute2`: [type] - [description]

**Relationships**:
- [Relationship to other entities]

#### Entity 2: [Name]
**Purpose**: [What this entity represents]  
**Key Attributes**:
- `attribute1`: [type] - [description]

---

## Success Criteria (REQUIRED)

Measurable outcomes that define success. Must be technology-neutral.

### Business Metrics
- **Metric 1**: [e.g., "User engagement increases by 20%"]
- **Metric 2**: [e.g., "Feature adoption rate > 50% within 30 days"]

### Technical Metrics
- **Metric 1**: [e.g., "API latency p95 < 200ms"]
- **Metric 2**: [e.g., "Zero data loss"]
- **Metric 3**: [e.g., "Test coverage > 80%"]

### User Experience Metrics
- **Metric 1**: [e.g., "Task completion time < 30 seconds"]
- **Metric 2**: [e.g., "User satisfaction score > 4.5/5"]

---

## Out of Scope

Explicitly list what is NOT included in this feature:

- [ ] [Out of scope item 1]
- [ ] [Out of scope item 2]
- [ ] [Out of scope item 3]

---

## Assumptions & Dependencies

### Assumptions
1. [Assumption 1 - e.g., "Users have stable internet connection"]
2. [Assumption 2 - e.g., "Users are authenticated via OAuth"]

### External Dependencies
1. [Dependency 1 - e.g., "Third-party API availability"]
2. [Dependency 2 - e.g., "Database migration completed"]

### Internal Dependencies
1. [Dependency 1 - e.g., "Authentication service deployed"]
2. [Dependency 2 - e.g., "Feature flag system available"]

---

## Open Questions

Mark items needing clarification with **[NEEDS CLARIFICATION]**:

1. **[NEEDS CLARIFICATION]**: [Question about requirement]
2. **[NEEDS CLARIFICATION]**: [Question about technical approach]
3. **[RESOLVED]**: [Previously unclear item that's now resolved]

---

## Validation Checklist

Before marking as "Approved", verify:

- [ ] No `[NEEDS CLARIFICATION]` markers remain
- [ ] All requirements are testable and unambiguous
- [ ] User scenarios cover all critical paths
- [ ] Success criteria are measurable
- [ ] Dependencies are identified
- [ ] P1 scenarios have complete acceptance criteria
- [ ] Core entities are defined
- [ ] Out of scope items are listed

---

## Notes & References

- Related Features: [Links to related specs]
- Research: [Links to technical research, competitive analysis]
- Design: [Links to mockups, wireframes, prototypes]
- Discussion: [Links to discussions, RFCs, decision records]
