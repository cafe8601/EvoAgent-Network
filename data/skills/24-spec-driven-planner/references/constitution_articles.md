# Constitutional Articles: Deep Dive

This document provides comprehensive explanation of each Constitutional article, including rationale, examples, and common pitfalls.

---

## Article I: Library-First Principle

### Core Concept
Every feature must begin as a standalone library. Business logic belongs in libraries, not in presentation layers.

### Why This Matters

**Problem Without Library-First**:
```typescript
// ❌ BAD: Business logic in API controller
app.post('/users', async (req, res) => {
  // Validation logic here
  if (!req.body.email || !req.body.email.includes('@')) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  
  // Business logic here
  const user = {
    id: generateId(),
    email: req.body.email,
    createdAt: new Date()
  };
  
  // Database logic here
  await db.users.insert(user);
  
  res.json(user);
});
```

**Problems**:
- Cannot test business logic without HTTP server
- Cannot reuse logic in CLI, workers, or other contexts
- Business rules scattered across routes
- Hard to maintain

**Solution With Library-First**:
```typescript
// ✅ GOOD: Business logic in library
// src/lib/users/UserService.ts
export class UserService {
  async createUser(data: CreateUserInput): Promise<User> {
    // All business logic here
    validateEmail(data.email);
    const user = {
      id: generateId(),
      email: data.email,
      createdAt: new Date()
    };
    return await this.repository.save(user);
  }
}

// src/api/routes/users.ts
app.post('/users', async (req, res) => {
  // Controller just coordinates
  const user = await userService.createUser(req.body);
  res.json(user);
});

// src/cli/commands/create-user.ts
// CLI can use same library
const user = await userService.createUser({ email: args.email });
console.log(JSON.stringify(user));
```

### Benefits
1. **Testability**: Test business logic directly, no HTTP overhead
2. **Reusability**: Same code works in API, CLI, workers, scripts
3. **Maintainability**: Business rules in one place
4. **Portability**: Easy to migrate between frameworks

### Common Violations

#### Violation 1: Logic in Controllers
**Symptom**: Controllers have more than 10 lines  
**Fix**: Extract to service layer

#### Violation 2: Logic in Routes
**Symptom**: Route handlers contain if/else logic  
**Fix**: Move to library

#### Violation 3: Direct Database Access in Controllers
**Symptom**: Controllers use ORM directly  
**Fix**: Use repository pattern in library

### Migration Strategy
If you have existing code with mixed concerns:
1. Create library module
2. Extract business logic to library
3. Make controllers/routes thin wrappers
4. Add tests for library
5. Refactor incrementally

---

## Article II: CLI Interface Mandate

### Core Concept
Every library must provide a command-line interface. This forces clean, text-based APIs.

### Why This Matters

**The Unix Philosophy**:
> "Write programs that do one thing well. Write programs to work together. Write programs to handle text streams, because that is a universal interface."

### Requirements Breakdown

#### 1. Stdin/Stdout/Stderr
```bash
# ✅ GOOD: Standard streams
echo '{"email": "user@example.com"}' | mycli create-user

# Output to stdout (data)
{"id": "123", "email": "user@example.com"}

# Errors to stderr
mycli create-user --invalid
# stderr: Error: Missing required field: email
```

#### 2. JSON Support
```bash
# Text mode (human-readable)
mycli get-user 123
User: user@example.com
Created: 2024-01-01

# JSON mode (machine-readable)
mycli get-user 123 --json
{"id":"123","email":"user@example.com","createdAt":"2024-01-01"}
```

#### 3. Help Text
```bash
mycli create-user --help

Usage: mycli create-user [OPTIONS]

Create a new user account

Options:
  --email TEXT     User email address [required]
  --name TEXT      User display name
  --json           Output in JSON format
  --help           Show this message and exit

Examples:
  mycli create-user --email user@example.com --name "John Doe"
  echo '{"email":"user@example.com"}' | mycli create-user
```

### Implementation Pattern

```typescript
// src/cli/commands/create-user.ts
import { UserService } from '../../lib/users/UserService';
import yargs from 'yargs';

interface CreateUserArgs {
  email?: string;
  name?: string;
  json?: boolean;
}

async function main() {
  const argv = yargs
    .option('email', { type: 'string', description: 'User email' })
    .option('name', { type: 'string', description: 'User name' })
    .option('json', { type: 'boolean', description: 'JSON output' })
    .parseSync() as CreateUserArgs;

  // Read from stdin if no email provided
  let input: CreateUserInput;
  if (!argv.email) {
    const stdin = await readStdin();
    input = JSON.parse(stdin);
  } else {
    input = { email: argv.email, name: argv.name };
  }

  // Call library
  const userService = new UserService();
  const user = await userService.createUser(input);

  // Output
  if (argv.json) {
    console.log(JSON.stringify(user));
  } else {
    console.log(`User created: ${user.email}`);
    console.log(`ID: ${user.id}`);
  }
}

main().catch(err => {
  console.error(err.message);
  process.exit(1);
});
```

### Benefits
1. **Automation**: Easy to script and automate
2. **Testing**: Can test via stdin/stdout
3. **Universal**: Works in any environment
4. **Composition**: Pipe commands together

### Composition Example
```bash
# Get user, extract email, send welcome email
mycli get-user 123 --json | \
  jq -r '.email' | \
  mycli send-welcome-email
```

---

## Article III: Test-First Imperative

### Core Concept
Tests must be written before implementation. No exceptions.

### The RED-GREEN-REFACTOR Cycle

```
┌─────────────────────────────────────────┐
│ 1. RED: Write Failing Test             │
│    - User reviews test                  │
│    - User approves                      │
│    - Run test, confirm it FAILS         │
└───────────┬─────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│ 2. GREEN: Make Test Pass                │
│    - Write minimum code                 │
│    - Run test, confirm it PASSES        │
└───────────┬─────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│ 3. REFACTOR: Improve Code               │
│    - Remove duplication                 │
│    - Improve naming                     │
│    - Run tests, confirm still GREEN     │
└─────────────────────────────────────────┘
```

### Why User Approval?

**Problem**: AI/developers might misunderstand requirements  
**Solution**: User reviews tests before implementation

**User Approval Checklist**:
- [ ] Test scenarios match my understanding?
- [ ] Edge cases covered?
- [ ] Error cases handled?
- [ ] Test is comprehensive enough?

### Example: Test-First Flow

#### Step 1: Write Test (RED Phase)
```typescript
// tests/unit/UserService.test.ts
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid email', async () => {
      // Arrange
      const service = new UserService(mockRepository);
      const input = { email: 'test@example.com' };
      
      // Act
      const result = await service.createUser(input);
      
      // Assert
      expect(result).toHaveProperty('id');
      expect(result.email).toBe('test@example.com');
      expect(result.createdAt).toBeInstanceOf(Date);
    });
    
    it('should throw error for invalid email', async () => {
      // Arrange
      const service = new UserService(mockRepository);
      const input = { email: 'invalid' };
      
      // Act & Assert
      await expect(service.createUser(input))
        .rejects
        .toThrow('Invalid email format');
    });
    
    it('should throw error for duplicate email', async () => {
      // Arrange
      const service = new UserService(mockRepository);
      mockRepository.findByEmail.mockResolvedValue({ existing: 'user' });
      const input = { email: 'existing@example.com' };
      
      // Act & Assert
      await expect(service.createUser(input))
        .rejects
        .toThrow('Email already exists');
    });
  });
});
```

**📋 User Review**: 
"Yes, these tests cover: valid email, invalid format, and duplicates. Approved!"

**Run Tests**:
```bash
npm test
# ❌ FAIL: UserService is not defined
# ✅ GOOD: Tests fail for right reason (not implemented yet)
```

#### Step 2: Implement (GREEN Phase)
```typescript
// src/lib/users/UserService.ts
export class UserService {
  constructor(private repository: UserRepository) {}
  
  async createUser(input: CreateUserInput): Promise<User> {
    // Validate email
    if (!this.isValidEmail(input.email)) {
      throw new Error('Invalid email format');
    }
    
    // Check for duplicates
    const existing = await this.repository.findByEmail(input.email);
    if (existing) {
      throw new Error('Email already exists');
    }
    
    // Create user
    const user = {
      id: generateId(),
      email: input.email,
      createdAt: new Date()
    };
    
    return await this.repository.save(user);
  }
  
  private isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}
```

**Run Tests**:
```bash
npm test
# ✅ PASS: All tests pass!
```

#### Step 3: Refactor (Still GREEN)
```typescript
// Improve: Extract email validation
export class UserService {
  async createUser(input: CreateUserInput): Promise<User> {
    this.validateInput(input);
    await this.checkDuplicates(input.email);
    return await this.createNewUser(input);
  }
  
  private validateInput(input: CreateUserInput): void {
    if (!EmailValidator.isValid(input.email)) {
      throw new Error('Invalid email format');
    }
  }
  
  private async checkDuplicates(email: string): Promise<void> {
    const existing = await this.repository.findByEmail(email);
    if (existing) {
      throw new Error('Email already exists');
    }
  }
  
  private async createNewUser(input: CreateUserInput): Promise<User> {
    const user = {
      id: generateId(),
      email: input.email,
      createdAt: new Date()
    };
    return await this.repository.save(user);
  }
}
```

**Run Tests Again**:
```bash
npm test
# ✅ PASS: All tests still pass after refactor!
```

### Common Pitfalls

#### Pitfall 1: Implementation Bias
**Problem**: Writing tests after code means tests are biased toward implementation  
**Solution**: Write tests first, based only on requirements

#### Pitfall 2: Testing Implementation Details
**Problem**: Tests that break when refactoring  
**Solution**: Test behavior, not implementation

```typescript
// ❌ BAD: Testing implementation details
it('should call validateEmail method', () => {
  const spy = jest.spyOn(service, 'validateEmail');
  await service.createUser(input);
  expect(spy).toHaveBeenCalled();
});

// ✅ GOOD: Testing behavior
it('should reject invalid email', () => {
  await expect(service.createUser({ email: 'invalid' }))
    .rejects.toThrow('Invalid email');
});
```

#### Pitfall 3: Skipping User Approval
**Problem**: Building wrong thing efficiently  
**Solution**: Always get user approval on tests first

### Test Coverage Requirements
- **Minimum**: 80% code coverage
- **Target**: 90%+ code coverage
- **Focus**: All business logic paths covered

---

## Article VII: Simplicity Gate

### Core Concept
Maximum 3 projects. No future-proofing.

### Why 3 Projects?

**The Complexity Curve**:
```
Complexity
    │
    │           ┌──────────────
    │         ┌─┘
    │       ┌─┘
    │     ┌─┘
    │   ┌─┘
    │ ┌─┘
    │─┘
    └──────────────────────── Projects
       1  2  3  4  5  6  7  8
```

**Sweet Spot**: 1-3 projects
- **1 project**: Ideal for small features
- **2 projects**: Good for separation of concerns (lib + api)
- **3 projects**: Acceptable for complex systems (lib + api + worker)
- **4+ projects**: Usually over-engineered

### Typical 3-Project Structure

```
1. Core Library (src/lib/)
   - Business logic
   - Domain models
   - Services
   
2. API Server (src/api/)
   - HTTP routes
   - Controllers
   - Middleware
   
3. Worker/Jobs (src/worker/)
   - Background tasks
   - Scheduled jobs
   - Event processors
```

### YAGNI: You Aren't Gonna Need It

#### Examples of Future-Proofing to Avoid

**❌ BAD: Building for "maybe later"**
```typescript
// Don't build plugin system if you have no plugins
interface Plugin {
  name: string;
  version: string;
  init(): void;
  destroy(): void;
}

class PluginManager {
  private plugins: Map<string, Plugin> = new Map();
  
  register(plugin: Plugin) { /*...*/ }
  load(name: string) { /*...*/ }
  unload(name: string) { /*...*/ }
  // ... 200 lines of plugin infrastructure
}

// Current usage:
// manager.register(onlyPlugin); // Only 1 plugin!
```

**✅ GOOD: Solve current problem**
```typescript
// Just use the functionality directly
import { onlyFeature } from './feature';

// When you actually need plugins, THEN build plugin system
```

**❌ BAD: Generic frameworks**
```typescript
// Don't build your own ORM
class MyORM {
  query(sql: string) { /*...*/ }
  insert(table: string, data: any) { /*...*/ }
  update(table: string, id: string, data: any) { /*...*/ }
  // ... 500 lines reinventing Prisma/TypeORM
}
```

**✅ GOOD: Use existing solutions**
```typescript
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();
```

### When to Add 4th Project?

**Legitimate Reasons**:
1. **Regulatory Isolation**: Compliance requires separation
2. **Team Boundaries**: Different teams own different systems
3. **Deployment Isolation**: Truly independent deployment needs
4. **Technology Boundaries**: Different tech stacks required

**Must Document**:
- Why 3 projects insufficient?
- What simpler approach was considered?
- Why was simpler approach rejected?

---

## Article VIII: Anti-Abstraction Gate

### Core Concept
Use frameworks directly. No abstraction layers. Single model representation.

### The Abstraction Trap

**❌ BAD: Repository Pattern Overuse**
```typescript
// Too many layers!
interface IUserRepository {
  findById(id: string): Promise<User>;
  save(user: User): Promise<void>;
}

class PrismaUserRepository implements IUserRepository {
  async findById(id: string): Promise<User> {
    const dbUser = await prisma.user.findUnique({ where: { id } });
    return this.toUser(dbUser); // Extra mapping
  }
  
  async save(user: User): Promise<void> {
    const dbUser = this.toDbUser(user); // Extra mapping
    await prisma.user.create({ data: dbUser });
  }
  
  private toUser(db: DbUser): User { /*...*/ }
  private toDbUser(user: User): DbUser { /*...*/ }
}

// Usage (with interface!)
const repository: IUserRepository = new PrismaUserRepository();
```

**Problems**:
- Interface adds no value (only 1 implementation)
- Mapping functions duplicate work
- More code to maintain
- Harder to understand

**✅ GOOD: Direct Framework Usage**
```typescript
// Just use Prisma directly
import { PrismaClient } from '@prisma/client';

class UserService {
  constructor(private prisma: PrismaClient) {}
  
  async getUserById(id: string): Promise<User> {
    return await this.prisma.user.findUnique({ where: { id } });
  }
  
  async createUser(data: CreateUserInput): Promise<User> {
    return await this.prisma.user.create({ data });
  }
}
```

### Single Model Principle

**❌ BAD: Multiple Models**
```typescript
// Database layer
interface UserEntity {
  user_id: string;
  email_address: string;
  created_timestamp: Date;
}

// Business layer
interface User {
  id: string;
  email: string;
  createdAt: Date;
}

// API layer
interface UserDTO {
  userId: string;
  email: string;
  created: string;
}

// Need 2 mapping functions!
function entityToUser(entity: UserEntity): User { /*...*/ }
function userToDTO(user: User): UserDTO { /*...*/ }
```

**✅ GOOD: Single Model**
```typescript
// One model used everywhere
interface User {
  id: string;
  email: string;
  createdAt: Date;
}

// Database: Uses same model (via Prisma schema)
// Business: Uses same model
// API: Uses same model (with JSON serialization)
```

### When Abstraction is Justified

**Legitimate Use Cases**:
1. **External APIs**: Isolate from third-party changes
2. **Multiple Implementations**: Actually have >1 implementation
3. **Testing**: Need to mock external dependencies

**Example**: Wrapping External API
```typescript
// ✅ GOOD: Abstract external API you don't control
interface PaymentProvider {
  charge(amount: number, token: string): Promise<ChargeResult>;
}

class StripeProvider implements PaymentProvider {
  async charge(amount: number, token: string) {
    // Stripe-specific implementation
    return await stripe.charges.create({ amount, source: token });
  }
}

class PayPalProvider implements PaymentProvider {
  async charge(amount: number, token: string) {
    // PayPal-specific implementation
    return await paypal.payment.create({ amount, token });
  }
}

// Justification: Multiple real implementations exist
```

---

## Article IX: Integration-First Testing

### Core Concept
Test with real systems first. Mock only when necessary.

### The Testing Pyramid (Inverted!)

Traditional pyramid says:
```
      /\
     /  \    Few integration tests
    /____\
   /      \   
  /  Unit  \  Many unit tests
 /__________\
```

We prefer:
```
 __________
|          |  Many integration tests (real systems)
|__________|
   \      /
    \____/    Some unit tests
     \  /
      \/      Few mocked tests
```

### Why Integration-First?

**Real Example: The Mock Trap**
```typescript
// ❌ BAD: Mocked test (gives false confidence)
it('should create user', async () => {
  const mockDb = {
    users: {
      create: jest.fn().mockResolvedValue({ id: '123' })
    }
  };
  
  const service = new UserService(mockDb as any);
  const result = await service.createUser({ email: 'test@example.com' });
  
  expect(result.id).toBe('123');
  expect(mockDb.users.create).toHaveBeenCalled();
});

// ✅ Test passes!
// ❌ Production breaks: Real DB has different schema!
```

**✅ GOOD: Integration test (catches real issues)**
```typescript
it('should create user in real database', async () => {
  // Use real test database
  const service = new UserService(testPrisma);
  
  const result = await service.createUser({
    email: 'test@example.com'
  });
  
  // Verify in actual database
  const dbUser = await testPrisma.user.findUnique({
    where: { id: result.id }
  });
  
  expect(dbUser.email).toBe('test@example.com');
  expect(dbUser.createdAt).toBeInstanceOf(Date);
});

// If schema changes, test breaks immediately!
```

### Setting Up Test Databases

**PostgreSQL Example**:
```typescript
// tests/setup.ts
import { PrismaClient } from '@prisma/client';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function setupTestDatabase(): Promise<PrismaClient> {
  // Create test database
  await execAsync('createdb myapp_test');
  
  // Run migrations
  process.env.DATABASE_URL = 'postgresql://localhost/myapp_test';
  await execAsync('npx prisma migrate deploy');
  
  // Return Prisma client
  const prisma = new PrismaClient();
  await prisma.$connect();
  
  return prisma;
}

export async function teardownTestDatabase(prisma: PrismaClient) {
  await prisma.$disconnect();
  await execAsync('dropdb myapp_test');
}

// tests/integration/users.test.ts
describe('User Integration Tests', () => {
  let prisma: PrismaClient;
  
  beforeAll(async () => {
    prisma = await setupTestDatabase();
  });
  
  afterAll(async () => {
    await teardownTestDatabase(prisma);
  });
  
  beforeEach(async () => {
    // Clean database between tests
    await prisma.user.deleteMany();
  });
  
  it('should create and retrieve user', async () => {
    // Test with real database
  });
});
```

### Contract Testing

**OpenAPI Contract Test**:
```typescript
import { OpenAPIValidator } from 'express-openapi-validator';

describe('API Contract Tests', () => {
  it('should match OpenAPI spec', async () => {
    // Load OpenAPI spec
    const spec = await loadOpenAPISpec('./contracts/openapi.json');
    
    // Make real API request
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com' });
    
    // Validate against contract
    expect(response.status).toBe(201);
    expect(response.body).toMatchSchema(spec.components.schemas.User);
  });
  
  it('should return 400 for invalid input', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'invalid' }); // Invalid email
    
    expect(response.status).toBe(400);
    expect(response.body).toMatchSchema(spec.components.schemas.Error);
  });
});
```

### When to Mock

**Acceptable Mocking**:
1. **External APIs**: Third-party services (Stripe, SendGrid)
2. **Slow Operations**: File uploads, video processing
3. **Expensive Resources**: SMS sending, cloud services

**Example: Mocking External API**
```typescript
// ✅ GOOD: Mock external service
describe('Payment Processing', () => {
  it('should handle Stripe failures gracefully', async () => {
    // Mock Stripe (external service we don't control)
    jest.spyOn(stripe.charges, 'create')
      .mockRejectedValue(new Error('Card declined'));
    
    // Test error handling
    await expect(paymentService.charge(100, 'token'))
      .rejects
      .toThrow('Payment failed');
  });
});

// ✅ GOOD: Use real Stripe in integration tests
describe('Payment Integration', () => {
  it('should charge card successfully', async () => {
    // Use Stripe test mode with real API calls
    const result = await paymentService.charge(100, 'tok_visa');
    expect(result.status).toBe('succeeded');
  });
});
```

### Test Organization

```
tests/
├── unit/              # Fast, isolated tests
│   └── utils/
│       └── validators.test.ts
├── integration/       # Real database, real services
│   ├── users.test.ts
│   └── payments.test.ts
├── contracts/         # API schema validation
│   └── api.contract.test.ts
└── e2e/              # Full system tests
    └── user-flow.test.ts
```

---

## Summary: The 9 Articles

| Article | Principle | Key Requirement | Non-Negotiable? |
|---------|-----------|-----------------|-----------------|
| I       | Library-First | Business logic in libraries | No |
| II      | CLI Interface | Every library has CLI | No |
| III     | Test-First | Tests before code | **YES** |
| IV-VI   | [Project-Specific] | Varies by project | Varies |
| VII     | Simplicity | ≤3 projects, no future-proofing | No |
| VIII    | Anti-Abstraction | Direct framework usage | No |
| IX      | Integration-First | Real systems over mocks | No |

**Only Article III is absolutely non-negotiable.**

All other articles can be violated with proper justification and documentation in the Complexity Register.
