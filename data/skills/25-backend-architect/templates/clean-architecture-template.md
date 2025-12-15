# Clean Architecture Template

Project structure template for building backend systems with Clean Architecture.

## Directory Structure

```
src/
├── domain/                     # Enterprise Business Rules
│   ├── entities/              # Core business objects
│   │   ├── User.ts
│   │   ├── Order.ts
│   │   └── Product.ts
│   ├── value-objects/         # Immutable value types
│   │   ├── Email.ts
│   │   ├── Money.ts
│   │   └── Address.ts
│   ├── interfaces/            # Repository interfaces
│   │   ├── IUserRepository.ts
│   │   ├── IOrderRepository.ts
│   │   └── IPaymentGateway.ts
│   └── errors/                # Domain-specific errors
│       ├── DomainError.ts
│       └── ValidationError.ts
│
├── use-cases/                  # Application Business Rules
│   ├── users/
│   │   ├── CreateUser.ts
│   │   ├── GetUser.ts
│   │   └── UpdateUser.ts
│   ├── orders/
│   │   ├── CreateOrder.ts
│   │   ├── ProcessOrder.ts
│   │   └── CancelOrder.ts
│   └── shared/
│       └── interfaces/
│           └── UseCase.ts
│
├── adapters/                   # Interface Adapters
│   ├── controllers/           # HTTP controllers
│   │   ├── UserController.ts
│   │   ├── OrderController.ts
│   │   └── dto/
│   │       ├── CreateUserDto.ts
│   │       └── UserResponseDto.ts
│   ├── repositories/          # Database implementations
│   │   ├── PrismaUserRepository.ts
│   │   ├── PrismaOrderRepository.ts
│   │   └── mappers/
│   │       └── UserMapper.ts
│   ├── gateways/              # External service adapters
│   │   ├── StripePaymentGateway.ts
│   │   └── SendGridEmailGateway.ts
│   └── presenters/            # Response formatters
│       └── UserPresenter.ts
│
├── infrastructure/             # Frameworks & Drivers
│   ├── database/
│   │   ├── prisma/
│   │   │   ├── schema.prisma
│   │   │   └── migrations/
│   │   └── connection.ts
│   ├── http/
│   │   ├── server.ts
│   │   ├── routes.ts
│   │   └── middleware/
│   │       ├── auth.ts
│   │       ├── validation.ts
│   │       └── error-handler.ts
│   ├── config/
│   │   ├── index.ts
│   │   └── env.ts
│   ├── logging/
│   │   └── logger.ts
│   └── container/             # Dependency injection
│       └── index.ts
│
├── main.ts                     # Application entry point
└── types/                      # Global types
    └── index.ts

tests/
├── unit/
│   ├── domain/
│   ├── use-cases/
│   └── adapters/
├── integration/
│   ├── api/
│   └── repositories/
├── e2e/
│   └── flows/
└── fixtures/
    ├── factories/
    └── mocks/
```

## Core Files

### Domain Entity

```typescript
// src/domain/entities/User.ts
import { Email } from '../value-objects/Email';

export class User {
  constructor(
    public readonly id: string,
    public readonly email: Email,
    public name: string,
    public readonly createdAt: Date,
    private _isActive: boolean = true
  ) {}

  get isActive(): boolean {
    return this._isActive;
  }

  deactivate(): void {
    if (!this._isActive) {
      throw new Error('User is already inactive');
    }
    this._isActive = false;
  }

  canPlaceOrder(): boolean {
    return this._isActive;
  }

  static create(props: CreateUserProps): User {
    return new User(
      props.id,
      new Email(props.email),
      props.name,
      new Date(),
      true
    );
  }
}
```

### Value Object

```typescript
// src/domain/value-objects/Email.ts
export class Email {
  constructor(public readonly value: string) {
    if (!this.isValid(value)) {
      throw new Error('Invalid email format');
    }
  }

  private isValid(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  equals(other: Email): boolean {
    return this.value === other.value;
  }
}
```

### Repository Interface

```typescript
// src/domain/interfaces/IUserRepository.ts
import { User } from '../entities/User';

export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  save(user: User): Promise<User>;
  delete(id: string): Promise<boolean>;
}
```

### Use Case

```typescript
// src/use-cases/users/CreateUser.ts
import { IUserRepository } from '../../domain/interfaces/IUserRepository';
import { User } from '../../domain/entities/User';
import { v4 as uuid } from 'uuid';

export interface CreateUserInput {
  email: string;
  name: string;
}

export interface CreateUserOutput {
  user: User;
}

export class CreateUserUseCase {
  constructor(private userRepository: IUserRepository) {}

  async execute(input: CreateUserInput): Promise<CreateUserOutput> {
    const existing = await this.userRepository.findByEmail(input.email);
    if (existing) {
      throw new Error('Email already exists');
    }

    const user = User.create({
      id: uuid(),
      email: input.email,
      name: input.name,
    });

    const savedUser = await this.userRepository.save(user);

    return { user: savedUser };
  }
}
```

### Controller

```typescript
// src/adapters/controllers/UserController.ts
import { Request, Response } from 'express';
import { CreateUserUseCase } from '../../use-cases/users/CreateUser';
import { CreateUserDto } from './dto/CreateUserDto';

export class UserController {
  constructor(private createUserUseCase: CreateUserUseCase) {}

  async create(req: Request, res: Response): Promise<Response> {
    const dto = CreateUserDto.parse(req.body);

    const result = await this.createUserUseCase.execute({
      email: dto.email,
      name: dto.name,
    });

    return res.status(201).json({
      data: {
        id: result.user.id,
        email: result.user.email.value,
        name: result.user.name,
      },
    });
  }
}
```

### Repository Implementation

```typescript
// src/adapters/repositories/PrismaUserRepository.ts
import { PrismaClient } from '@prisma/client';
import { IUserRepository } from '../../domain/interfaces/IUserRepository';
import { User } from '../../domain/entities/User';
import { UserMapper } from './mappers/UserMapper';

export class PrismaUserRepository implements IUserRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<User | null> {
    const data = await this.prisma.user.findUnique({ where: { id } });
    return data ? UserMapper.toDomain(data) : null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const data = await this.prisma.user.findUnique({ where: { email } });
    return data ? UserMapper.toDomain(data) : null;
  }

  async save(user: User): Promise<User> {
    const data = UserMapper.toPersistence(user);
    const saved = await this.prisma.user.upsert({
      where: { id: user.id },
      create: data,
      update: data,
    });
    return UserMapper.toDomain(saved);
  }

  async delete(id: string): Promise<boolean> {
    await this.prisma.user.delete({ where: { id } });
    return true;
  }
}
```

### Dependency Injection

```typescript
// src/infrastructure/container/index.ts
import { PrismaClient } from '@prisma/client';
import { PrismaUserRepository } from '../../adapters/repositories/PrismaUserRepository';
import { CreateUserUseCase } from '../../use-cases/users/CreateUser';
import { UserController } from '../../adapters/controllers/UserController';

const prisma = new PrismaClient();

// Repositories
const userRepository = new PrismaUserRepository(prisma);

// Use Cases
const createUserUseCase = new CreateUserUseCase(userRepository);

// Controllers
export const userController = new UserController(createUserUseCase);
```

## Testing

### Unit Test Example

```typescript
// tests/unit/use-cases/CreateUser.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { CreateUserUseCase } from '../../../src/use-cases/users/CreateUser';

describe('CreateUserUseCase', () => {
  let useCase: CreateUserUseCase;
  let mockUserRepo: any;

  beforeEach(() => {
    mockUserRepo = {
      findByEmail: vi.fn(),
      save: vi.fn(),
    };
    useCase = new CreateUserUseCase(mockUserRepo);
  });

  it('should create user when email is unique', async () => {
    mockUserRepo.findByEmail.mockResolvedValue(null);
    mockUserRepo.save.mockImplementation((user) => Promise.resolve(user));

    const result = await useCase.execute({
      email: 'test@example.com',
      name: 'Test User',
    });

    expect(result.user.email.value).toBe('test@example.com');
    expect(mockUserRepo.save).toHaveBeenCalled();
  });

  it('should throw when email exists', async () => {
    mockUserRepo.findByEmail.mockResolvedValue({ id: '123' });

    await expect(
      useCase.execute({ email: 'existing@example.com', name: 'Test' })
    ).rejects.toThrow('Email already exists');
  });
});
```

## Key Principles

1. **Dependencies point inward** - Outer layers depend on inner layers
2. **Domain has no dependencies** - Pure business logic
3. **Use Cases orchestrate** - Coordinate domain objects
4. **Adapters translate** - Convert between layers
5. **Infrastructure is replaceable** - Easy to swap implementations
