# Architecture Patterns

Comprehensive guide to backend architecture patterns for production systems (2025).

## Pattern Selection Guide

| Project Type | Architecture | Complexity | Team Size |
|-------------|--------------|------------|-----------|
| MVP/Startup | Monolith | Low | 1-5 |
| Growing Product | Modular Monolith | Medium | 5-15 |
| Enterprise | Microservices | High | 15+ |
| Complex Domain | Hexagonal/DDD | High | 10+ |

## 3-Layer Architecture (Simple)

```
┌─────────────────────────────────────┐
│  Controller Layer (HTTP handling)   │
│  - Route definitions                │
│  - Request validation               │
│  - Response formatting              │
├─────────────────────────────────────┤
│  Service Layer (Business logic)     │
│  - Business rules                   │
│  - Orchestration                    │
│  - Transaction management           │
├─────────────────────────────────────┤
│  Repository Layer (Data access)     │
│  - Database queries                 │
│  - ORM operations                   │
│  - Data mapping                     │
└─────────────────────────────────────┘
```

**Directory Structure:**
```
src/
├── controllers/
│   ├── UserController.ts
│   └── ProductController.ts
├── services/
│   ├── UserService.ts
│   └── ProductService.ts
├── repositories/
│   ├── UserRepository.ts
│   └── ProductRepository.ts
├── models/
│   ├── User.ts
│   └── Product.ts
└── middleware/
    ├── auth.ts
    └── validation.ts
```

**Implementation Example (TypeScript):**
```typescript
// controllers/UserController.ts
import { Request, Response } from 'express';
import { UserService } from '../services/UserService';
import { createUserSchema } from '../validators/userValidators';

export class UserController {
  constructor(private userService: UserService) {}

  async create(req: Request, res: Response) {
    const validated = createUserSchema.parse(req.body);
    const user = await this.userService.createUser(validated);
    return res.status(201).json(user);
  }
}

// services/UserService.ts
import { UserRepository } from '../repositories/UserRepository';
import { hashPassword } from '../utils/password';

export class UserService {
  constructor(private userRepo: UserRepository) {}

  async createUser(data: CreateUserDTO) {
    const hashedPassword = await hashPassword(data.password);
    return this.userRepo.create({
      ...data,
      password: hashedPassword,
    });
  }
}

// repositories/UserRepository.ts
import { PrismaClient } from '@prisma/client';

export class UserRepository {
  constructor(private prisma: PrismaClient) {}

  async create(data: CreateUserData) {
    return this.prisma.user.create({ data });
  }
}
```

**When to Use:** MVPs, CRUD apps, small teams, unclear domain boundaries

## Clean Architecture

```
┌────────────────────────────────────────────────────┐
│                  Frameworks & Drivers               │
│  (Express, Prisma, Redis, External APIs)            │
│  ┌────────────────────────────────────────────┐   │
│  │           Interface Adapters                │   │
│  │  (Controllers, Presenters, Gateways)        │   │
│  │  ┌────────────────────────────────────┐   │   │
│  │  │          Use Cases                  │   │   │
│  │  │  (Application Business Rules)       │   │   │
│  │  │  ┌────────────────────────────┐   │   │   │
│  │  │  │       Entities              │   │   │   │
│  │  │  │  (Enterprise Business Rules)│   │   │   │
│  │  │  └────────────────────────────┘   │   │   │
│  │  └────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
         Dependencies flow INWARD →
```

**Directory Structure:**
```
src/
├── domain/                  # Entities & business rules
│   ├── entities/
│   │   ├── User.ts
│   │   └── Order.ts
│   ├── value-objects/
│   │   ├── Email.ts
│   │   └── Money.ts
│   └── interfaces/          # Repository interfaces
│       ├── IUserRepository.ts
│       └── IOrderRepository.ts
├── use-cases/               # Application business rules
│   ├── CreateUser.ts
│   ├── ProcessOrder.ts
│   └── SendNotification.ts
├── adapters/                # Interface adapters
│   ├── controllers/
│   │   └── UserController.ts
│   ├── repositories/
│   │   └── PrismaUserRepository.ts
│   └── gateways/
│       └── StripePaymentGateway.ts
└── infrastructure/          # Frameworks & drivers
    ├── database.ts
    ├── config.ts
    └── logging.ts
```

**Key Principles:**
1. Dependencies point inward (outer depends on inner)
2. Inner layers know nothing about outer layers
3. Business logic independent of frameworks
4. Testable without UI, database, or external services

**When to Use:** Testable systems, changing requirements, multiple interfaces

## Hexagonal Architecture (Ports and Adapters)

```
                 ┌─────────────┐
                 │   Primary   │
                 │   Adapters  │
                 │  (REST,CLI) │
                 └──────┬──────┘
                        │
┌───────────────────────┼───────────────────────┐
│                       ▼                       │
│               ┌───────────────┐               │
│               │    Domain     │               │
│  Secondary    │    (Core)     │    Ports      │
│  Adapters ◄───┤   Business    ├───►(Interfaces)│
│  (DB,Queue)   │    Logic      │               │
│               └───────────────┘               │
│                                               │
└───────────────────────────────────────────────┘
```

**Components:**
- **Domain Core:** Business logic with no external dependencies
- **Ports:** Interfaces defining how the core interacts
- **Primary Adapters:** Drive the application (REST, CLI, GraphQL)
- **Secondary Adapters:** Driven by the application (DB, Queue, Email)

**Implementation Example:**
```typescript
// Port (Interface)
interface IPaymentGateway {
  charge(amount: Money, customer: string): Promise<PaymentResult>;
}

// Domain Service
class OrderService {
  constructor(
    private orderRepo: IOrderRepository,
    private paymentGateway: IPaymentGateway
  ) {}

  async placeOrder(order: Order): Promise<OrderResult> {
    if (!order.isValid()) {
      return { success: false, error: 'Invalid order' };
    }

    const payment = await this.paymentGateway.charge(
      order.total,
      order.customerId
    );

    if (!payment.success) {
      return { success: false, error: 'Payment failed' };
    }

    order.markAsPaid();
    await this.orderRepo.save(order);
    return { success: true, order };
  }
}

// Adapter (Implementation)
class StripePaymentAdapter implements IPaymentGateway {
  async charge(amount: Money, customer: string): Promise<PaymentResult> {
    const charge = await stripe.charges.create({
      amount: amount.cents,
      currency: amount.currency,
      customer,
    });
    return { success: true, transactionId: charge.id };
  }
}

// Test Adapter
class MockPaymentAdapter implements IPaymentGateway {
  async charge(): Promise<PaymentResult> {
    return { success: true, transactionId: 'mock-123' };
  }
}
```

**When to Use:** Complex domains, multiple integrations, high testability needs

## Domain-Driven Design (DDD)

### Strategic Patterns

**Bounded Contexts:**
```
┌──────────────────┐    ┌──────────────────┐
│   Sales Context  │    │  Shipping Context│
│                  │    │                  │
│  Order           │    │  Shipment        │
│  Customer        │    │  Package         │
│  Product         │    │  Carrier         │
│                  │    │                  │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────┬───────────────┘
                 │
         ┌───────▼───────┐
         │  Shared Kernel │
         │  (Domain Events)│
         └───────────────┘
```

### Tactical Patterns

**Entities (with identity):**
```typescript
class Order {
  constructor(
    public readonly id: string,
    public readonly customerId: string,
    private _items: OrderItem[] = [],
    private _status: OrderStatus = OrderStatus.PENDING
  ) {}

  addItem(product: Product, quantity: number): void {
    this._items.push(new OrderItem(product, quantity));
    this.recordEvent(new ItemAddedEvent(this.id, product.id, quantity));
  }

  submit(): void {
    if (this._items.length === 0) {
      throw new Error('Cannot submit empty order');
    }
    this._status = OrderStatus.SUBMITTED;
    this.recordEvent(new OrderSubmittedEvent(this.id));
  }
}
```

**Value Objects (immutable):**
```typescript
class Money {
  constructor(
    public readonly amount: number,
    public readonly currency: string
  ) {
    if (amount < 0) throw new Error('Amount cannot be negative');
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Currency mismatch');
    }
    return new Money(this.amount + other.amount, this.currency);
  }

  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }
}
```

**Aggregates (consistency boundaries):**
```typescript
class Customer {
  private _addresses: Address[] = [];

  addAddress(address: Address): void {
    if (this._addresses.length >= 5) {
      throw new Error('Maximum 5 addresses allowed');
    }
    this._addresses.push(address);
  }

  get primaryAddress(): Address | undefined {
    return this._addresses.find(a => a.isPrimary);
  }
}
```

**When to Use:** Complex domains, many business rules, long-term projects

## Microservices Architecture

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  User    │   │ Product  │   │  Order   │   │ Payment  │
│ Service  │   │ Service  │   │ Service  │   │ Service  │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │
  ┌──▼──┐        ┌──▼──┐        ┌──▼──┐        ┌──▼──┐
  │  DB │        │  DB │        │  DB │        │  DB │
  └─────┘        └─────┘        └─────┘        └─────┘
```

### Key Patterns

**API Gateway:**
- Request routing
- Authentication/authorization
- Rate limiting
- Request transformation

**Service Discovery:**
- Dynamic service registration
- Health check integration
- Load balancing

**Circuit Breaker:**
```typescript
import CircuitBreaker from 'opossum';

const breaker = new CircuitBreaker(callService, {
  timeout: 3000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000,
});

breaker.fallback(() => ({ data: 'cached', source: 'fallback' }));
```

**Saga Pattern (Distributed Transactions):**
```
Order Service: Create Order → Publish "OrderCreated"
                                    ↓
Payment Service: Reserve Payment → Publish "PaymentReserved"
                                    ↓
Inventory Service: Reserve Stock → Publish "StockReserved"

If any step fails → Compensating transactions (rollback)
```

**When to Use:** Large teams, clear domain boundaries, independent scaling needs

## Event-Driven Architecture

**Event Sourcing:**
```typescript
// Store events, not current state
const events = [
  { type: 'AccountCreated', userId: '123' },
  { type: 'MoneyDeposited', amount: 1000 },
  { type: 'MoneyWithdrawn', amount: 500 },
];

// Reconstruct state by replaying events
const balance = events.reduce((acc, event) => {
  if (event.type === 'MoneyDeposited') return acc + event.amount;
  if (event.type === 'MoneyWithdrawn') return acc - event.amount;
  return acc;
}, 0);
```

**CQRS (Command Query Responsibility Segregation):**
```
Write Side (Commands):           Read Side (Queries):
CreateOrder                      GetOrderById
UpdateOrder                      GetUserOrders
  ↓                                ↑
┌─────────┐                    ┌─────────┐
│ Write   │ → Events →         │  Read   │
│  DB     │    (sync)          │  DB     │
│(Postgres)                    │(MongoDB)│
└─────────┘                    └─────────┘
```

## Architecture Decision Checklist

- [ ] Clear service/module boundaries defined
- [ ] Dependencies flow inward (or are injected)
- [ ] Business logic is framework-agnostic
- [ ] External dependencies abstracted behind interfaces
- [ ] Unit tests don't require infrastructure
- [ ] Database per service (for microservices)
- [ ] Event-driven communication where appropriate
- [ ] Circuit breakers for external calls
- [ ] Health checks configured
- [ ] Distributed tracing enabled

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Distributed Monolith | Microservices that depend on each other | Clear boundaries, async communication |
| Anemic Domain | Entities with only data, no behavior | Rich domain models |
| Fat Controllers | Business logic in controllers | Delegate to services/use cases |
| Shared Database | Multiple services sharing DB | Database per service |
| Over-Engineering | Complex patterns for simple apps | Start simple, evolve |

## Resources

- Martin Fowler - Microservices: https://martinfowler.com/articles/microservices.html
- Clean Architecture (Robert Martin)
- Domain-Driven Design (Eric Evans)
- Microservices Patterns: https://microservices.io/patterns/
