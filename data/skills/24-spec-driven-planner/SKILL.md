---
name: spec-driven-planner
description: Specification-first development methodology for structured requirement gathering, architectural design, and task decomposition. Guides through Assess → Specify → Research → Plan → Tasks workflow phases. Use when starting new features, planning complex implementations, creating technical specifications, or establishing development standards. Covers brainstorming techniques, spec templates, plan review, and multi-model consultation.
version: 2.0.0
author: Orchestra Research
license: MIT
tags: [Planning, Specification, Requirements, Architecture, Task-Decomposition, Development-Methodology]
dependencies: []
---

# Spec-Driven Planner Skill

> **Version**: 2.0
> **Category**: Development Methodology & Project Planning
> **Difficulty**: ⭐⭐⭐⭐ (Advanced)
> **Scope**: **Planning Only** (Assess → Specify → Research → Plan → Tasks)

---

## 🎯 Overview

**Spec-Driven Development (SDD)** is a specification-first methodology where documentation drives implementation. This skill focuses on the **planning phases** of SDD — guiding teams through structured requirement gathering, architectural design, and task decomposition.

**Core Philosophy**: **Plan First, Code Second** — Every development task begins with a detailed specification that acts as a contract between intent and implementation.

### ⚠️ Scope Clarification

**This skill covers:**
```
┌─────────┐   ┌─────────┐   ┌──────────┐   ┌────────┐   ┌─────────┐
│  Assess │ → │ Specify │ → │ Research │ → │  Plan  │ → │  Tasks  │  ✅ THIS SKILL
└─────────┘   └─────────┘   └──────────┘   └────────┘   └─────────┘
```

**Implementation is handled by other skills:**
```
┌───────────┐   ┌──────────┐   ┌─────────┐
│ Implement │ → │ Validate │ → │ Operate │  → Other Skills (TDD, DevOps, etc.)
└───────────┘   └──────────┘   └─────────┘
```

---

## 📋 Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Core Concepts](#core-concepts)
3. [SDD Workflow Phases](#sdd-workflow-phases)
4. [Brainstorming & Discovery](#brainstorming--discovery)
5. [Specification Creation](#specification-creation)
6. [Implementation Planning](#implementation-planning)
7. [Task Decomposition](#task-decomposition)
8. [Plan Review & Multi-Model Consultation](#plan-review--multi-model-consultation)
9. [Templates & Formats](#templates--formats)
10. [Best Practices](#best-practices)
11. [Integration & Tools](#integration--tools)

---

## When to Use This Skill

### ✅ Use For:
- **New feature development** requiring structured requirements
- **Complex refactoring** across multiple files
- **API integrations** or external service connections
- **Architecture changes** or system redesigns
- **Large codebases** where context drift is a risk
- **Multi-team initiatives** requiring clear specifications
- **High-risk projects** where precision is critical

### ❌ Do NOT Use For:
- Simple one-file changes or minor bug fixes
- Trivial modifications or formatting changes
- Exploratory prototyping or quick experiments
- Changes under 30 minutes of estimated work

---

## Core Concepts

### 1. Specification-First Development
```
Specification (WHAT & WHY) → Plan (HOW) → Tasks (Execution Units) → Implementation (Code)
```

### 2. Atomic Tasks
Each task represents a **single, focused change** to one or few files. Benefits:
- **Precise dependency tracking**: File-level dependencies are explicit
- **Granular progress monitoring**: Each task = verifiable progress
- **Parallel implementation**: Independent tasks run simultaneously
- **Easy rollback**: Changes can be reverted at file level

### 3. Test-First Imperative
```
Write Test → User Reviews & Approves → RED (Expect Failure) → Implement Minimum Code → GREEN (Pass) → Refactor
```

### 4. Key Benefits
- Reduces hallucinated APIs and misread intent
- Prevents breaking existing functionality
- Provides clear verification criteria
- Creates auditable development process
- Early feedback checkpoint reduces rework

---

## SDD Workflow Phases (This Skill's Scope)

This skill covers the **5 planning phases** of SDD:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SPEC-DRIVEN PLANNER SCOPE                           │
├─────────┬─────────┬──────────┬────────┬─────────┐                      │
│  Assess │ Specify │ Research │  Plan  │  Tasks  │ → Ready for Implement
│    ↓    │    ↓    │    ↓     │   ↓    │    ↓    │                      │
│Assessed │Specified│Researched│Planned │ Tasked  │                      │
└─────────┴─────────┴──────────┴────────┴─────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  Handoff to Implementation    │
                    │  Skills (TDD, DevOps, etc.)   │
                    └───────────────────────────────┘
```

### Phase Descriptions

| Phase | Purpose | Key Outputs | Status |
|-------|---------|-------------|--------|
| **1. Assess** | Evaluate if SDD is appropriate | Assessment report, recommendation | ✅ This Skill |
| **2. Specify** | Create product requirements | PRD, user stories, acceptance criteria | ✅ This Skill |
| **3. Research** | Technical research & validation | Technology recommendations, feasibility | ✅ This Skill |
| **4. Plan** | Architecture & implementation plan | ADRs, platform design, contracts | ✅ This Skill |
| **5. Tasks** | Break down into executable tasks | tasks.md, JSON spec file | ✅ This Skill |
| 6. Implement | Execute the plan | Source code, tests | ❌ Other Skills |
| 7. Validate | Quality assurance & security | QA report, coverage | ❌ Other Skills |
| 8. Operate | Deploy and maintain | Runbooks, dashboards | ❌ Other Skills |

---

## Brainstorming & Discovery

### Facilitation Techniques

#### 1. Story Mapping
Visualize user journey and identify features that deliver value at each step.

```
Step 1: Define User Activities (horizontal backbone)
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Discover     │ Browse       │ Purchase     │ Receive      │
│ Products     │ & Compare    │ & Checkout   │ & Review     │
└──────────────┴──────────────┴──────────────┴──────────────┘

Step 2: Break down into User Tasks (vertical slices)
Step 3: Prioritize by Walking Skeleton (MVP = top row)
```

#### 2. Event Storming
Discover domain events and business processes through collaborative modeling.

```markdown
1. Identify Domain Events (orange) → OrderPlaced, PaymentProcessed
2. Identify Commands (blue) → PlaceOrder, ProcessPayment
3. Identify Aggregates (yellow) → Order, Payment
4. Identify External Systems (pink) → PaymentGateway, ShippingProvider
5. Identify Policies (purple) → WHEN OrderPlaced THEN ProcessPayment
```

#### 3. Impact Mapping
Connect business goals to features through user impact.

```
GOAL: Increase revenue by 20%
├─ WHY? (Impact): Increase conversion rate
│  ├─ WHO? (Actors): New visitors, Returning customers
│  ├─ HOW? (Features): 1-click purchase, recommendations
│  └─ WHAT? (Deliverables): US-001, US-002, US-003
```

### Prioritization Frameworks

#### MoSCoW Method
| Category | Description | Example |
|----------|-------------|---------|
| **Must Have** | Critical for launch | User login, checkout |
| **Should Have** | Important but not critical | Reviews, wishlist |
| **Could Have** | Nice to have | Social login, filters |
| **Won't Have** | Explicitly deferred | Mobile app, subscriptions |

#### RICE Score
```
RICE = (Reach × Impact × Confidence) / Effort

Example:
- Reach: 5000 users/month
- Impact: High (3/3)
- Confidence: 80%
- Effort: 4 person-weeks
RICE = (5000 × 3 × 0.8) / 4 = 3000
```

#### Kano Model
- **Basic Needs**: Expected features (absence = dissatisfaction)
- **Performance Needs**: More is better (linear satisfaction)
- **Excitement Needs**: Delighters (presence = wow)

---

## Specification Creation

### Staged Planning (Recommended)

For complex features, create specifications in two stages:

#### Stage 1: High-Level Phase Planning

```markdown
# High-Level Plan: [Feature Name]

## Overview
Brief description of what this change accomplishes and why.

## Proposed Phases

### Phase 1: [Phase Name]
**Purpose**: What this phase accomplishes
**Dependencies**: What must exist before starting
**Risk Level**: Low/Medium/High
**Estimated Files Affected**: 3-5 files

### Phase 2: [Phase Name]
[...]

## Implementation Order
1. Phase X (must complete first)
2. Phase Y (depends on X)

## Questions for Review
- Any concerns about this approach?
```

**User reviews and approves before detailed planning.**

#### Stage 2: Detailed Task Breakdown (After Approval)

### EARS Requirements Format

Easy Approach to Requirements Syntax:

| Type | Template | Example |
|------|----------|---------|
| **Ubiquitous** | The system SHALL [req] | System SHALL validate all inputs |
| **Event-Driven** | WHEN [trigger] THEN system SHALL [response] | WHEN user clicks submit THEN validate form |
| **State-Driven** | WHILE [state] system SHALL [req] | WHILE processing THEN show loading |
| **Conditional** | IF [condition] THEN system SHALL [req] | IF admin THEN show management panel |
| **Optional** | WHERE [feature] system SHALL [req] | WHERE premium THEN enable analytics |

### Systematic Questioning

1. **Core Functionality**: What is the primary purpose? What problem does it solve?
2. **Event-Driven**: What user actions trigger this? What system events are involved?
3. **State-Driven**: Are there different states or modes?
4. **Conditional**: Different behaviors for different users/roles?
5. **Performance**: Response time requirements? Expected load?
6. **Security**: What data needs protection? Who should have access?
7. **Error Handling**: What can go wrong? How should errors be handled?
8. **Edge Cases**: What are the boundary conditions?

---

## Implementation Planning

### Pre-Flight Constitutional Check

Before planning, verify project principles:

```markdown
### Article I: Library-First Principle
- [ ] Feature implemented as library first?
- [ ] Business logic isolated from framework code?

### Article III: Test-First Imperative
- [ ] Tests will be written before implementation?
- [ ] RED-GREEN-REFACTOR commitment?

### Article VII: Simplicity Gate
- [ ] Using ≤3 projects?
- [ ] No future-proofing or speculative features?

### Article VIII: Anti-Abstraction Gate
- [ ] Using frameworks directly (no wrappers)?
- [ ] Single model representation?

### Article IX: Integration-First Testing
- [ ] Contracts defined?
- [ ] Integration tests use real database?
```

### Technology Selection Template

```markdown
### Technology Stack

**Language/Runtime**: TypeScript/Node.js 20+
- Rationale: Team expertise, large ecosystem
- Alternatives Considered: Go (rejected - unfamiliarity)

**Framework**: Express.js 4.x
- Rationale: Mature, well-documented
- Alternatives: Fastify (rejected - unnecessary complexity)

**Database**: PostgreSQL 15+
- Rationale: ACID compliance, JSON support
- Alternatives: MongoDB (rejected - need ACID)
```

### Data Model Design

```markdown
#### Table: messages
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| room_id | UUID | NOT NULL, FK rooms(id) |
| content | TEXT | NOT NULL, CHECK(length ≤ 2000) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Indexes**: (room_id, created_at DESC)
**Rationale**: UUID for distributed safety, cascading deletes
```

---

## Task Decomposition

### Hierarchy Levels

```
[Spec] Feature Name (0/total tasks, 0%) {#spec-root}
│
├─ [Phase] Phase Name (0/phase_tasks) {#phase-N}
│   │
│   ├─ [Group] File Modifications (0/tasks) {#phase-N-files}
│   │   │
│   │   ├─ [Task] path/to/file.ext [pending] {#task-N-M}
│   │   │   ├─ [Subtask] Specific change [pending] {#task-N-M-P}
│   │   │   └─ [Subtask] Another change [pending] {#task-N-M-Q}
│   │   │
│   │   └─ [Task] another/file.ext [pending] [depends: task-N-M] {#task-N-R}
│   │
│   └─ [Group] Verification [blocked-by: phase-N-files] {#phase-N-verify}
│       ├─ [Verify] Tests pass [pending] [auto] {#verify-N-1}
│       └─ [Verify] Implementation fidelity [pending] [fidelity] {#verify-N-2}
```

### Dependency Types

| Type | Notation | Description |
|------|----------|-------------|
| **Hard** | `[blocked-by: task-id]` | Cannot start until dependency completes |
| **Soft** | `[depends: task-id]` | Recommended order but not required |
| **Blocks** | `[blocks: task-id]` | This task blocks others |
| **Parallel** | `[parallel-safe]` | No dependencies, can run simultaneously |

### Task Categories

| Category | When to Use | file_path Required? |
|----------|-------------|---------------------|
| `investigation` | Analyzing existing code | No |
| `implementation` | Creating new functionality | Yes |
| `refactoring` | Improving code structure | Yes |
| `decision` | Architectural choices | No |
| `research` | External learning | No |

### JSON Spec Structure

```json
{
  "spec_id": "user-auth-2025-01-15-001",
  "generated": "2025-01-15T10:00:00Z",
  "last_updated": "2025-01-15T10:00:00Z",
  
  "hierarchy": {
    "spec-root": {
      "type": "spec",
      "title": "User Authentication",
      "status": "pending",
      "parent": null,
      "children": ["phase-1", "phase-2"],
      "total_tasks": 24,
      "completed_tasks": 0,
      "metadata": {}
    },
    
    "phase-1": {
      "type": "phase",
      "title": "Database Schema",
      "status": "pending",
      "parent": "spec-root",
      "children": ["phase-1-files", "phase-1-verify"],
      "total_tasks": 8,
      "completed_tasks": 0,
      "metadata": {}
    },
    
    "task-1-1": {
      "type": "task",
      "title": "db/migrations/001_add_users.sql",
      "status": "pending",
      "parent": "phase-1-files",
      "children": ["task-1-1-1", "task-1-1-2"],
      "dependencies": {
        "blocks": ["task-1-2"],
        "blocked_by": [],
        "depends": []
      },
      "total_tasks": 2,
      "completed_tasks": 0,
      "metadata": {
        "file_path": "db/migrations/001_add_users.sql",
        "task_category": "implementation",
        "estimated_hours": 1
      }
    },
    
    "verify-1-1": {
      "type": "verify",
      "title": "Migration runs without errors",
      "status": "pending",
      "parent": "phase-1-verify",
      "children": [],
      "metadata": {
        "verification_type": "auto",
        "command": "npm run migrate",
        "expected": "Migration completes successfully"
      }
    }
  }
}
```

---

## Plan Review & Multi-Model Consultation

### When to Request Review

| Situation | Action |
|-----------|--------|
| Draft spec ready for approval | Full review |
| Security-critical area | Security review |
| Feasibility questions | Feasibility review |
| Major architectural novelty | Full review |
| Lightweight, low-risk spec | Skip review |

### Review Types

| Type | Models | Duration | Focus |
|------|--------|----------|-------|
| **quick** | 2 | 10-15 min | Completeness, Clarity |
| **full** | 3-4 | 20-30 min | All 6 dimensions |
| **security** | 2-3 | 15-20 min | Auth, data, API security |
| **feasibility** | 2-3 | 10-15 min | Estimates, dependencies |

### Review Dimensions

1. **Completeness**: All sections present, sufficient detail
2. **Clarity**: Unambiguous descriptions, specific criteria
3. **Feasibility**: Realistic estimates, achievable dependencies
4. **Architecture**: Sound design, proper abstractions
5. **Risk Management**: Risks identified, edge cases covered
6. **Verification**: Comprehensive testing plan

### Feedback Categories

| Category | Examples |
|----------|----------|
| **Missing Information** | "Task lacks acceptance criteria" |
| **Design Concerns** | "Tight coupling may hinder testing" |
| **Risk Flags** | "Admin endpoints lack auth checks" |
| **Feasibility Questions** | "Estimate seems low for OAuth integration" |
| **Enhancement Suggestions** | "Consider adding health check endpoints" |
| **Clarification Requests** | "What does 'performant' mean specifically?" |

---

## Templates & Formats

### Specification Template
```markdown
# Feature Specification: [FEATURE NAME]

**Feature ID**: `NNN-feature-name`
**Created**: [DATE]
**Status**: Draft

## User Scenarios & Testing

### User Story 1 - [제목] (Priority: P1)
[사용자 여정 설명]

**Why this priority**: [우선순위 이유]
**Independent Test**: [독립 테스트 방법]

**Acceptance Scenarios**:
1. **Given** [초기 상태], **When** [행동], **Then** [예상 결과]

## Requirements

### Functional Requirements
- **FR-001**: System MUST [구체적 기능]
- **FR-002**: [NEEDS CLARIFICATION: 불명확한 부분]

### Non-Functional Requirements
- **NFR-001**: Response time p95 < 200ms

## Success Criteria
- **SC-001**: [측정 가능한 지표]
```

### Implementation Plan Template
```markdown
# Implementation Plan: [FEATURE]

**Feature ID**: `NNN-feature-name` | **Date**: [DATE]

## Summary
[요구사항 + 기술 접근법 요약]

## Technical Context
- **Language**: TypeScript 5.0
- **Framework**: Express.js
- **Database**: PostgreSQL
- **Testing**: Jest

## Project Structure
```
src/
├── models/
├── services/
└── api/
tests/
├── unit/
└── integration/
```

## Implementation Phases
1. Setup: 프로젝트 초기화
2. Foundational: 공통 인프라
3. User Story 1 (P1): MVP 핵심
4. Polish: 문서화, 최적화
```

### Task List Template
```markdown
# Tasks: [FEATURE NAME]

## Phase 1: Setup
- [ ] T001 프로젝트 구조 생성
- [ ] T002 [P] 의존성 설치

## Phase 2: Foundational
- [ ] T003 데이터베이스 스키마 설정
- [ ] T004 [P] API 라우팅 설정

**Checkpoint**: Foundation 완료

## Phase 3: User Story 1 (P1) 🎯 MVP
- [ ] T005 [P] [US1] Model 생성 in src/models/
- [ ] T006 [US1] Service 구현 in src/services/
- [ ] T007 [US1] Endpoint 구현 in src/api/

**Checkpoint**: US1 독립 테스트 가능
```

---

## Best Practices

### Specification Quality
| Do | Don't |
|----|-------|
| Be specific: "Add error handling to API calls" | Vague: "Improve error handling" |
| Include examples | Leave details abstract |
| Think ahead: maintenance, testing | Skip verification planning |
| Base on codebase exploration | Guess at patterns |

### Common Pitfalls

❌ **Skipping codebase analysis** → Incorrect assumptions  
❌ **Vague specifications** → "Improve performance" is not actionable  
❌ **Premature optimization** → Don't add unplanned features  
❌ **Verification shortcuts** → Every step matters  
❌ **Spec drift** → Keep spec updated with changes  
❌ **Over-engineering** → Match complexity to requirements  

### Task Sizing Guidelines

| Complexity | Phases | Tasks | Verification |
|------------|--------|-------|--------------|
| **Short** (<5 files) | 1-2 | 3-8 | 1-2 per phase |
| **Medium** (5-15 files) | 2-4 | 10-25 | 2-4 per phase |
| **Large** (>15 files) | 4-6 | 25-50 | 3-5 per phase |

**Rule of Thumb**: Each task/subtask should be completable in < 30 minutes.

---

## Integration & Tools

### Directory Structure
```
project/
├── .sdd/                     # SDD working directory
│   └── specs/
│       └── NNN-feature/
│           ├── spec.md       # Feature specification
│           ├── plan.md       # Implementation plan
│           ├── tasks.md      # Task breakdown
│           ├── data-model.md # Data model
│           └── contracts/    # API contracts
├── memory/
│   └── constitution.md       # Project principles
├── docs/plans/               # Execution plans
├── src/                      # Source code
└── tests/                    # Tests
```

### Related Skills
- **25-multi-agent-system**: For autonomous planning with multiple agents
- **23-frontend-design-architect**: For UI/UX specifications
- **26-investment-trading-systems**: For financial system planning

### Core References
- `references/workflow_guide.md`: Complete workflow walkthrough
- `references/constitution_articles.md`: Project principle articles
- `assets/constitution.md`: Constitution template
- `assets/spec-template.md`: Specification template
- `assets/plan-template.md`: Plan template
- `assets/tasks-template.md`: Task template

---

## 🚀 Quick Start

### 1. Assess (5 min)
```
"이 기능에 SDD가 필요한가?"
```
- Is this feature complex enough for SDD?
- Multiple files? Multiple teams? High risk?
- **Output**: Go/No-Go decision

### 2. Specify (30-60 min)
```
"specify: [기능 설명]"
```
- Define user stories with priorities (P1, P2, P3)
- Write EARS requirements
- Identify success criteria
- **Output**: `spec.md`

### 3. Research (15-45 min)
```
"research: [기술 주제]"
```
- Technical feasibility analysis
- Technology evaluation
- Competitive analysis (if applicable)
- **Output**: `research.md`

### 4. Plan (30-60 min)
```
"plan: [기술 스택]"
```
- Constitutional pre-flight check
- Technology selection with rationale
- Data model design
- API contracts
- **Output**: `plan.md`, `data-model.md`, `contracts/`

### 5. Tasks (20-30 min)
```
"tasks"
```
- Break down into atomic tasks
- Define dependencies (blocked-by, depends, parallel-safe)
- Add verification steps
- **Output**: `tasks.md` or JSON spec file

### 6. Review (Optional, 15-30 min)
```
"review: [spec-id]"
```
- Multi-model consultation
- Address feedback
- Get approval
- **Output**: Review report

---

## 🔄 Handoff to Implementation

Once planning is complete, hand off to implementation skills:

| Output | Next Skill | Purpose |
|--------|------------|----------|
| `tasks.md` | TDD/Implementation Skill | Execute with test-first approach |
| `contracts/` | API Development Skill | Implement API endpoints |
| `data-model.md` | Database Skill | Create migrations |
| `plan.md` | Architecture Skill | Validate implementation alignment |

**Handoff Checklist:**
- [ ] All `[NEEDS CLARIFICATION]` resolved
- [ ] All phases have verification steps
- [ ] Dependencies are clear
- [ ] Estimates are reasonable
- [ ] Review feedback addressed (if applicable)

---

## 📚 References

- [User Story Mapping - Jeff Patton](https://www.jpattonassociates.com/user-story-mapping/)
- [Impact Mapping - Gojko Adzic](https://www.impactmapping.org/)
- [EARS Requirements Syntax](https://www.iaria.org/conferences2012/filesQRS12/Tutorial%20Easy%20Approach%20to%20Requirements%20Syntax.pdf)
- [Design Sprint - Google Ventures](https://www.gv.com/sprint/)

---

**Remember**: This skill produces the **blueprint** for development. The time spent on specification pays exponential dividends in implementation quality. Hand off clean, complete plans to implementation skills.
