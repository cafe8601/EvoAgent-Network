# Spec-Driven Development: Complete Workflow Guide

This guide walks through the entire SDD workflow from idea to tasks, with concrete examples.

---

## Workflow Overview

```
User Idea
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 1: CONSTITUTION                   │
│ Establish project principles            │
└───────────┬─────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│ Phase 2: SPECIFY                        │
│ Convert idea to structured spec         │
│ Output: spec.md                         │
└───────────┬─────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│ Phase 3: PLAN                           │
│ Create technical implementation plan    │
│ Output: plan.md, contracts/, etc.       │
└───────────┬─────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│ Phase 4: TASKS                          │
│ Break down into executable tasks        │
│ Output: tasks.md                        │
└───────────┬─────────────────────────────┘
            │
            ▼
        DONE ✓
    (Ready for implementation)
```

**Key Principle**: We stop at tasks. Implementation is a separate phase.

---

## Phase 1: Constitution (One-Time Setup)

### Purpose
Establish architectural principles that govern ALL future development.

### When to Run
- **Once per project** at the very beginning
- **When changing architecture philosophy**
- **When team agrees on new constraints**

### Example

**User Says**: 
"I want to start a new project for a real-time chat application."

**Action**:
Create `memory/constitution.md` based on template.

**Key Decisions to Make**:

1. **Article I**: Library-First? → **Yes**, all logic in libraries
2. **Article II**: CLI Required? → **Yes**, for automation
3. **Article III**: TDD Required? → **Yes** (non-negotiable)
4. **Article VII**: Max Projects? → **3** (lib + api + worker)
5. **Article VIII**: No Abstractions? → **Yes**, use frameworks directly
6. **Article IX**: Integration Tests? → **Yes**, real database

**Constitutional Gates to Set Up**:
```markdown
### Simplicity Gate
- [ ] Using ≤3 projects?
- [ ] No future-proofing?

### Anti-Abstraction Gate
- [ ] Using framework directly?
- [ ] Single model representation?

### Integration-First Gate
- [ ] Contracts defined?
- [ ] Contract tests written?
```

**Output**: `memory/constitution.md`

---

## Phase 2: Specify

### Purpose
Convert user idea into structured, testable specification.

### Input
User's feature request (can be vague!)

### Output
Complete `spec.md` with:
- User scenarios (P1, P2, P3)
- Requirements (FR-XXX, NFR-XXX)
- Success criteria
- Core entities

### Example Walkthrough

#### Input (Vague User Request)
"I want users to be able to chat in real-time"

#### Step 1: Extract User Scenarios

**Ask Clarifying Questions**:
- Who are the users?
- What's the primary use case?
- What happens when offline?
- Any message history?

**Generate Scenarios**:

```markdown
### P1: Critical Path (Must-Have)

#### Scenario 1: Send and Receive Messages
**As a** logged-in user  
**I want to** send messages that appear instantly for other users  
**So that** I can have real-time conversations

**Acceptance Criteria**:
Given I am logged in to a chat room
  And another user is in the same room
When I send a message "Hello"
Then the other user sees "Hello" within 1 second
  And the message is persisted to history

**Test Cases**:
- [ ] Message appears for recipient within 1 second
- [ ] Message persists after page refresh
- [ ] Message shows sender's name and timestamp
- [ ] Multiple messages maintain order
```

**User Review**: 
"Yes! But also need to show who's typing..."

**Update**:
```markdown
#### Scenario 2: Typing Indicators
**As a** user  
**I want to** see when others are typing  
**So that** I know to wait for their response

**Acceptance Criteria**:
Given another user is in my chat room
When they start typing
Then I see "[Username] is typing..." within 500ms
  And the indicator disappears after 3 seconds of inactivity
```

#### Step 2: Extract Requirements

```markdown
### Functional Requirements

**FR-001**: Real-time Message Delivery
- **Priority**: P1
- **Rationale**: Core feature for chat
- **Dependencies**: None
- **Details**: Messages must be delivered within 1 second via WebSocket

**FR-002**: Message Persistence
- **Priority**: P1
- **Rationale**: Users need message history
- **Dependencies**: None
- **Details**: All messages stored in database with timestamp, sender, content

**FR-003**: Typing Indicators
- **Priority**: P2
- **Rationale**: Improves UX
- **Dependencies**: FR-001 (needs WebSocket)
- **Details**: Broadcast typing events via WebSocket

**FR-004**: User Presence
- **Priority**: P2
- **Rationale**: Show who's online
- **Dependencies**: FR-001
- **[NEEDS CLARIFICATION]**: How long until "away" status?

### Non-Functional Requirements

**NFR-001: Performance**
- Message delivery latency p95 < 1 second
- Support 100 concurrent users per chat room
- Message history loads in < 500ms

**NFR-002: Reliability**
- Messages never lost (persistent storage)
- Automatic reconnection on disconnect
- Message queue for offline users
```

#### Step 3: Define Core Entities

```markdown
### Core Entities

#### Entity 1: Message
**Purpose**: Represents a single chat message  
**Key Attributes**:
- `id`: string (UUID) - Unique identifier
- `roomId`: string - Which chat room
- `userId`: string - Who sent it
- `content`: string - Message text
- `timestamp`: Date - When sent
- `type`: 'text' | 'system' - Message type

**Relationships**:
- Belongs to one User (sender)
- Belongs to one Room

#### Entity 2: Room
**Purpose**: Represents a chat room  
**Key Attributes**:
- `id`: string (UUID)
- `name`: string - Room name
- `createdAt`: Date

**Relationships**:
- Has many Messages
- Has many Users (participants)

#### Entity 3: User
**Purpose**: Represents a user  
**Key Attributes**:
- `id`: string
- `username`: string
- `status`: 'online' | 'away' | 'offline'
- `lastSeen`: Date

**Relationships**:
- Can be in many Rooms
- Can send many Messages
```

#### Step 4: Define Success Criteria

```markdown
### Success Criteria

#### Business Metrics
- User engagement: Average 10+ messages per session
- Feature adoption: 80% of users send messages within first session
- Retention: 60% of users return next day

#### Technical Metrics
- API latency p95 < 200ms
- WebSocket connection success rate > 99%
- Zero message loss
- Test coverage > 80%

#### User Experience Metrics
- Message send to display < 1 second
- Page load time < 2 seconds
- User satisfaction score > 4.5/5
```

#### Step 5: Mark Unclear Items

```markdown
## Open Questions

1. **[NEEDS CLARIFICATION]**: How long until user marked as "away"?
2. **[NEEDS CLARIFICATION]**: Max message length?
3. **[NEEDS CLARIFICATION]**: File attachments supported?
4. **[NEEDS CLARIFICATION]**: Edit/delete messages?
```

**User Resolves**:
- Away after 5 minutes
- Max 2000 characters
- No attachments in v1
- No edit/delete in v1

**Update Spec**: Mark as `[RESOLVED]`

#### Final Validation

```markdown
## Validation Checklist

- [x] No `[NEEDS CLARIFICATION]` markers remain
- [x] All requirements are testable and unambiguous
- [x] User scenarios cover all critical paths
- [x] Success criteria are measurable
- [x] Dependencies are identified
- [x] P1 scenarios have complete acceptance criteria
- [x] Core entities are defined
- [x] Out of scope items are listed
```

**Output**: `specs/001-realtime-chat/spec.md`

---

## Phase 3: Plan

### Purpose
Convert specification into technical implementation plan with architecture decisions.

### Input
- `spec.md` (from Phase 2)
- `memory/constitution.md` (from Phase 1)

### Output
- `plan.md` - Implementation plan
- `contracts/openapi.json` - API contract
- `contracts/websocket-spec.md` - WebSocket contract
- `data-model.md` - Database schema
- `research.md` - Technical research

### Example Walkthrough

#### Step 1: Constitutional Pre-Flight Check

```markdown
## Phase -1: Pre-Implementation Gates

### Article I: Library-First Principle
- [x] **Compliance**: Yes, creating `src/lib/chat/` library
- **Structure**:
  - `lib/chat/MessageService.ts`
  - `lib/chat/RoomService.ts`
  - `lib/chat/PresenceService.ts`

### Article III: Test-First Imperative
- [x] **Compliance**: Tests will be written first
- **Commitment**: RED-GREEN-REFACTOR for all features

### Article VII: Simplicity Gate
- [x] **Compliance**: Using 3 projects
- **Projects**:
  1. Core Library (`src/lib/`)
  2. API Server (`src/api/`)
  3. WebSocket Server (`src/websocket/`)
- **Justification**: Need separate WebSocket process for scalability

### Article VIII: Anti-Abstraction Gate
- [x] **Compliance**: Using Prisma directly (no ORM wrapper)
- [x] **Compliance**: Single `Message` model (no DTO/Entity split)

### Article IX: Integration-First Gate
- [x] **Contracts Defined**: See `contracts/`
- [ ] **Contract Tests Written**: Will be in tasks
```

#### Step 2: Technology Selection

```markdown
### Technology Stack Selection

#### Core Technologies
- **Language/Runtime**: TypeScript/Node.js 20+
  - **Rationale**: Team expertise, large ecosystem
  - **Alternatives Considered**: 
    - Go: Rejected due to team unfamiliarity
    - Python: Rejected due to WebSocket performance

- **Framework**: Express.js 4.x
  - **Rationale**: Mature, well-documented, simple
  - **Alternatives**: Fastify (rejected - unnecessary complexity)

- **Database**: PostgreSQL 15+
  - **Rationale**: ACID compliance, JSON support
  - **Alternatives**: MongoDB (rejected - need ACID for messages)

- **Real-time**: Socket.io 4.x
  - **Rationale**: Automatic reconnection, fallbacks
  - **Alternatives**: 
    - Raw WebSocket: Rejected - need reconnection logic
    - SignalR: Rejected - better Node.js support with Socket.io

- **ORM**: Prisma 5.x
  - **Rationale**: Type-safe, migration management
  - **Alternatives**: TypeORM (rejected - prefer Prisma DX)

#### Supporting Technologies
- **Caching**: Redis (for presence data)
- **Testing**: Jest + Supertest
- **Validation**: Zod (schema validation)
```

#### Step 3: Data Model Design

```markdown
### Database Schema

#### Table 1: messages
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL CHECK (length(content) <= 2000),
  type VARCHAR(20) NOT NULL DEFAULT 'text',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  CONSTRAINT valid_type CHECK (type IN ('text', 'system'))
);

CREATE INDEX idx_messages_room_created ON messages(room_id, created_at DESC);
CREATE INDEX idx_messages_user ON messages(user_id);
```

**Rationale**:
- UUID for distributed system safety
- Cascading deletes for data integrity
- Content length check enforces FR requirement
- Index on (room_id, created_at) for message history queries

#### Table 2: rooms
```sql
CREATE TABLE rooms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE(name)
);
```

#### Table 3: room_participants
```sql
CREATE TABLE room_participants (
  room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  PRIMARY KEY (room_id, user_id)
);

CREATE INDEX idx_participants_user ON room_participants(user_id);
```
```

#### Step 4: API Contracts

```markdown
### REST API Contract

See `contracts/openapi.json` for full specification.

#### POST /api/messages
```json
Request:
{
  "roomId": "uuid",
  "content": "Hello world"
}

Response (201):
{
  "id": "uuid",
  "roomId": "uuid",
  "userId": "uuid",
  "content": "Hello world",
  "timestamp": "2024-01-01T00:00:00Z",
  "type": "text"
}

Response (400):
{
  "error": "Validation failed",
  "details": [
    { "field": "content", "message": "Content too long (max 2000)" }
  ]
}
```

#### GET /api/rooms/:roomId/messages
```json
Query Parameters:
- before: string (ISO timestamp) - Pagination cursor
- limit: number (default: 50, max: 100)

Response (200):
{
  "messages": [
    {
      "id": "uuid",
      "content": "Hello",
      "timestamp": "2024-01-01T00:00:00Z",
      "user": {
        "id": "uuid",
        "username": "john"
      }
    }
  ],
  "hasMore": true,
  "nextCursor": "2024-01-01T00:00:00Z"
}
```

### WebSocket Contract

See `contracts/websocket-spec.md`

#### Events: Client → Server

**join_room**
```typescript
socket.emit('join_room', { roomId: 'uuid' });
```

**send_message**
```typescript
socket.emit('send_message', { 
  roomId: 'uuid', 
  content: 'Hello' 
});
```

**typing_start**
```typescript
socket.emit('typing_start', { roomId: 'uuid' });
```

**typing_stop**
```typescript
socket.emit('typing_stop', { roomId: 'uuid' });
```

#### Events: Server → Client

**message**
```typescript
socket.on('message', (data: {
  id: string;
  roomId: string;
  userId: string;
  username: string;
  content: string;
  timestamp: string;
}) => {
  // Handle new message
});
```

**user_typing**
```typescript
socket.on('user_typing', (data: {
  roomId: string;
  userId: string;
  username: string;
  isTyping: boolean;
}) => {
  // Show/hide typing indicator
});
```

**user_joined**
```typescript
socket.on('user_joined', (data: {
  roomId: string;
  userId: string;
  username: string;
}) => {
  // Update user list
});
```
```

#### Step 5: Implementation Sequence

```markdown
### User Story 1: Send and Receive Messages (P1)

#### Phase 1: Database Setup
1. Create Prisma schema
2. Generate migrations
3. Test migrations

#### Phase 2: Message Service (TDD)
1. Write tests for MessageService
2. User approves tests
3. Implement MessageService
4. Refactor

#### Phase 3: API Endpoints (TDD)
1. Write contract tests
2. User approves
3. Implement POST /api/messages
4. Implement GET /api/rooms/:roomId/messages

#### Phase 4: WebSocket (TDD)
1. Write WebSocket tests
2. User approves
3. Implement send_message handler
4. Implement message broadcast

#### Phase 5: Integration Testing
1. Test end-to-end message flow
2. Load test (100 concurrent users)
```

**Output**: 
- `specs/001-realtime-chat/plan.md`
- `specs/001-realtime-chat/contracts/openapi.json`
- `specs/001-realtime-chat/contracts/websocket-spec.md`

---

## Phase 4: Tasks

### Purpose
Break down implementation plan into executable, ordered tasks.

### Input
- `plan.md`
- `spec.md`
- `memory/constitution.md`

### Output
`tasks.md` with:
- Task breakdown by user story
- TDD workflow for each task
- Dependencies
- Parallel work tracks
- Checkpoints

### Example Walkthrough

#### Step 1: User Story → Task Groups

```markdown
## User Story 1: Send and Receive Messages (P1)

### Phase 1: Setup & Infrastructure `[P]`

#### Task 1.1: Prisma Schema
**File**: `prisma/schema.prisma`  
**Type**: Schema Definition  
**Dependencies**: None  
**Parallel**: Yes `[P]`

**Steps**:
1. Define Message model
2. Define Room model
3. Define User model
4. Add indexes

**Validation**:
- [ ] Schema compiles
- [ ] No TypeScript errors

---

#### Task 1.2: Database Migrations
**File**: `prisma/migrations/001_initial_schema.sql`  
**Type**: Migration  
**Dependencies**: Task 1.1

**Steps**:
1. Run `prisma migrate dev`
2. Test migration up
3. Test migration down
4. Commit migration files

**Validation**:
- [ ] Migration runs successfully
- [ ] Rollback works
- [ ] Tables created with correct schema
```

#### Step 2: TDD Task Breakdown

```markdown
### Phase 2: Message Service (TDD) `[CHECKPOINT]`

#### Task 2.1: Write Message Service Tests
**File**: `tests/unit/MessageService.test.ts`  
**Type**: Test (RED Phase)  
**Dependencies**: Task 1.2

**Test Cases**:
```typescript
describe('MessageService', () => {
  describe('createMessage', () => {
    it('should create message with valid content', async () => {
      const message = await service.createMessage({
        roomId: 'room-1',
        userId: 'user-1',
        content: 'Hello'
      });
      
      expect(message).toHaveProperty('id');
      expect(message.content).toBe('Hello');
      expect(message.timestamp).toBeInstanceOf(Date);
    });
    
    it('should reject content over 2000 characters', async () => {
      const longContent = 'a'.repeat(2001);
      
      await expect(
        service.createMessage({
          roomId: 'room-1',
          userId: 'user-1',
          content: longContent
        })
      ).rejects.toThrow('Content too long');
    });
    
    it('should reject empty content', async () => {
      await expect(
        service.createMessage({
          roomId: 'room-1',
          userId: 'user-1',
          content: ''
        })
      ).rejects.toThrow('Content cannot be empty');
    });
  });
  
  describe('getMessages', () => {
    it('should return messages ordered by timestamp desc', async () => {
      // Seed messages
      await seedMessages([
        { content: 'First', timestamp: '2024-01-01' },
        { content: 'Second', timestamp: '2024-01-02' }
      ]);
      
      const messages = await service.getMessages('room-1');
      
      expect(messages[0].content).toBe('Second');
      expect(messages[1].content).toBe('First');
    });
    
    it('should support pagination', async () => {
      // Seed 100 messages
      await seed100Messages();
      
      const page1 = await service.getMessages('room-1', { limit: 50 });
      expect(page1.messages).toHaveLength(50);
      expect(page1.hasMore).toBe(true);
      
      const page2 = await service.getMessages('room-1', { 
        limit: 50,
        before: page1.nextCursor
      });
      expect(page2.messages).toHaveLength(50);
      expect(page2.hasMore).toBe(false);
    });
  });
});
```

**User Approval Required**:
- [ ] User reviews test scenarios
- [ ] User confirms tests match spec FR-001, FR-002
- [ ] User approves proceeding to implementation

**Validation** (RED Phase):
- [ ] Tests written
- [ ] Tests run and FAIL (MessageService doesn't exist)
- [ ] Failure messages are clear

---

#### Task 2.2: Implement Message Service
**File**: `src/lib/chat/MessageService.ts`  
**Type**: Implementation (GREEN Phase)  
**Dependencies**: Task 2.1 (after user approval)

**Implementation**:
```typescript
import { PrismaClient, Message } from '@prisma/client';

export class MessageService {
  constructor(private prisma: PrismaClient) {}
  
  async createMessage(input: CreateMessageInput): Promise<Message> {
    // Validate content
    if (!input.content || input.content.trim().length === 0) {
      throw new Error('Content cannot be empty');
    }
    
    if (input.content.length > 2000) {
      throw new Error('Content too long (max 2000 characters)');
    }
    
    // Create message
    return await this.prisma.message.create({
      data: {
        roomId: input.roomId,
        userId: input.userId,
        content: input.content.trim(),
        type: 'text'
      }
    });
  }
  
  async getMessages(
    roomId: string, 
    options?: PaginationOptions
  ): Promise<PaginatedMessages> {
    const limit = options?.limit || 50;
    const before = options?.before ? new Date(options.before) : undefined;
    
    const messages = await this.prisma.message.findMany({
      where: {
        roomId,
        ...(before && { createdAt: { lt: before } })
      },
      orderBy: { createdAt: 'desc' },
      take: limit + 1, // +1 to check if there are more
      include: {
        user: {
          select: { id: true, username: true }
        }
      }
    });
    
    const hasMore = messages.length > limit;
    const resultMessages = hasMore ? messages.slice(0, limit) : messages;
    
    return {
      messages: resultMessages,
      hasMore,
      nextCursor: hasMore ? 
        resultMessages[resultMessages.length - 1].createdAt.toISOString() : 
        undefined
    };
  }
}
```

**Constitutional Check**:
- [x] Using Prisma directly (Article VIII)
- [x] Single Message model (Article VIII)
- [x] Part of library (Article I)

**Validation** (GREEN Phase):
- [ ] All tests pass
- [ ] No new failing tests
- [ ] Code coverage > 80%

---

#### Task 2.3: Refactor Message Service
**File**: `src/lib/chat/MessageService.ts`  
**Type**: Refactoring (REFACTOR Phase)  
**Dependencies**: Task 2.2

**Refactoring Goals**:
- [x] Extract validation to separate method
- [x] Improve error messages
- [x] Add JSDoc comments

**Validation**:
- [ ] All tests still pass
- [ ] No new complexity added
- [ ] Code is more readable
```

#### Step 3: Define Parallel Tracks

```markdown
## Parallel Work Tracks

Tasks marked with `[P]` can be worked on simultaneously:

**Track A: Core Services**
- Task 2.1 → Task 2.2 → Task 2.3 (MessageService)
- Task 3.1 → Task 3.2 → Task 3.3 (RoomService)

**Track B: Infrastructure**
- Task 1.1 → Task 1.2 (Database - can run parallel to Track A)

**Track C: API Layer**
- Task 4.1 → Task 4.2 → Task 4.3 (REST API - depends on Track A completion)

**Track D: WebSocket**
- Task 5.1 → Task 5.2 → Task 5.3 (Socket.io - depends on Track A completion)

**Track E: CLI**
- Task 6.1 → Task 6.2 (CLI - can run parallel to Track C/D after Track A)
```

#### Step 4: Add Checkpoints

```markdown
## Checkpoints

### Checkpoint 1: After Phase 2 (Services)
**Before proceeding to API/WebSocket, verify**:
- [ ] All service unit tests pass
- [ ] Code coverage > 80%
- [ ] No Constitutional violations
- [ ] Code review completed
- [ ] User approved service behavior

**Deliverables**:
- MessageService with tests
- RoomService with tests
- PresenceService with tests

---

### Checkpoint 2: After Phase 3 (API)
**Before deploying, verify**:
- [ ] All contract tests pass
- [ ] Integration tests pass with real database
- [ ] Load testing completed (100 concurrent users)
- [ ] OpenAPI spec matches implementation
- [ ] Error handling comprehensive

**Deliverables**:
- REST API with contract tests
- Integration tests
- Load test results

---

### Checkpoint 3: After Phase 4 (WebSocket)
**Before production, verify**:
- [ ] WebSocket tests pass
- [ ] Reconnection logic tested
- [ ] Broadcasting works correctly
- [ ] No memory leaks under load
- [ ] Monitoring in place

**Deliverables**:
- WebSocket server with tests
- Load test results (WebSocket connections)
- Monitoring dashboard
```

**Output**: `specs/001-realtime-chat/tasks.md`

---

## Complete Example: End-to-End

### User Input
"I want to build a real-time chat feature where users can see messages instantly and know when others are typing."

### Phase 1: Constitution (One-Time)
```bash
# Output: memory/constitution.md
# Time: 10 minutes (setup once)
```

Key decisions:
- ≤3 projects
- TDD required
- No abstractions
- Real database in tests

### Phase 2: Specify
```bash
# Output: specs/001-realtime-chat/spec.md
# Time: 15-20 minutes
```

Generated:
- 3 user scenarios (P1: send/receive, P1: history, P2: typing)
- 8 functional requirements
- 4 non-functional requirements
- 3 core entities
- 6 success criteria

### Phase 3: Plan
```bash
# Output: 
# - specs/001-realtime-chat/plan.md
# - specs/001-realtime-chat/contracts/openapi.json
# - specs/001-realtime-chat/contracts/websocket-spec.md
# Time: 20-25 minutes
```

Generated:
- Technology stack (Node.js, Express, Socket.io, Prisma, PostgreSQL)
- Database schema (3 tables, indexes)
- API contracts (REST + WebSocket)
- Implementation sequence
- Constitutional compliance check

### Phase 4: Tasks
```bash
# Output: specs/001-realtime-chat/tasks.md
# Time: 15-20 minutes
```

Generated:
- 25 tasks across 5 phases
- TDD workflow for each task
- 4 parallel work tracks
- 3 checkpoints
- Dependencies mapped

### Total Time
**~60-75 minutes** from idea to executable tasks.

Compare to traditional approach:
- PRD: 2-3 hours
- Design doc: 2-3 hours
- Tech spec: 3-4 hours
- Test plan: 2 hours
- **Total: ~12 hours**

### Savings
**~10 hours saved** (85% reduction)

---

## Best Practices

### 1. Keep Spec Technology-Neutral
Don't mention frameworks in spec. Save for plan.

```markdown
❌ BAD (in spec.md):
"Use Socket.io for real-time updates"

✅ GOOD (in spec.md):
"Messages appear in real-time for all users in room"

✅ THEN (in plan.md):
"Technology: Socket.io 4.x for WebSocket communication"
```

### 2. User Approval is Critical
Never skip user approval on tests.

```markdown
❌ BAD:
- Write tests
- Implement immediately

✅ GOOD:
- Write tests
- **User reviews and approves**
- Run tests (RED)
- Implement
```

### 3. Mark Uncertainties Explicitly
Use `[NEEDS CLARIFICATION]` liberally.

```markdown
**FR-005**: User Presence
- **[NEEDS CLARIFICATION]**: How long until "away" status?
- **[NEEDS CLARIFICATION]**: Show last seen timestamp?
```

### 4. Constitutional Check Before Every Phase
Always verify constitutional compliance.

```markdown
Before Plan:
- [ ] Spec complete?
- [ ] Constitution exists?

Before Tasks:
- [ ] Plan complete?
- [ ] Constitutional gates passed?

Before Implementation:
- [ ] Tasks complete?
- [ ] All checkpoints defined?
```

### 5. Iterate When Needed
Specs aren't perfect on first pass.

```markdown
Iteration triggers:
- User says "actually, I meant..."
- Missing requirements discovered
- Technical constraints found
- Constitutional violation needed

Action:
1. Update spec.md with changes
2. Regenerate plan.md
3. Update tasks.md
4. Document why in Complexity Register (if needed)
```

---

## Common Pitfalls

### Pitfall 1: Jumping to Implementation
**Symptom**: "Let's just start coding!"  
**Problem**: No clear requirements, waste time on wrong thing  
**Solution**: Always complete spec → plan → tasks first

### Pitfall 2: Over-Specifying Technology
**Symptom**: Spec mentions frameworks, libraries  
**Problem**: Locks in technical decisions too early  
**Solution**: Keep spec technology-neutral, choose tech in plan

### Pitfall 3: Skipping User Approval
**Symptom**: Tests written, implementation starts immediately  
**Problem**: Building wrong thing efficiently  
**Solution**: ALWAYS get user approval on tests first

### Pitfall 4: Vague Requirements
**Symptom**: "The system should be fast"  
**Problem**: Can't verify, can't test  
**Solution**: Make measurable: "API p95 latency < 200ms"

### Pitfall 5: Ignoring Constitution
**Symptom**: Adding 4th project, creating abstraction layers  
**Problem**: Complexity creep  
**Solution**: Check constitutional gates, justify violations explicitly

---

## Summary

| Phase | Input | Output | Time | Key Activity |
|-------|-------|--------|------|--------------|
| Constitution | Project idea | constitution.md | 10 min | Set architectural principles |
| Specify | Feature request | spec.md | 15-20 min | Convert to structured requirements |
| Plan | spec.md | plan.md, contracts/ | 20-25 min | Choose tech, design architecture |
| Tasks | plan.md | tasks.md | 15-20 min | Break into executable tasks |

**Total**: 60-75 minutes from idea to ready-to-implement tasks.

**Key Principle**: Stop at tasks. Implementation is separate phase.

**Success Criteria**: Tasks are clear enough that implementation is straightforward.
