# Technology Stack Guide

Comprehensive technology selection guide with benchmarks and comparisons (2025).

## Language Selection

### Comparison Matrix

| Criteria | Node.js | Python | Go | Rust |
|----------|---------|--------|-----|------|
| Performance | Good | Moderate | Excellent | Excellent |
| Concurrency | Event Loop | GIL (async) | Goroutines | Async/Threads |
| Memory Usage | Moderate | High | Low | Low |
| Startup Time | Fast | Slow | Very Fast | Fast |
| Ecosystem | Excellent | Excellent | Good | Growing |
| Learning Curve | Easy | Easy | Moderate | Steep |
| Type Safety | TypeScript | Optional | Built-in | Built-in |

### When to Choose

**Node.js/TypeScript**
```
✅ Full-stack JavaScript teams
✅ Real-time applications (WebSocket)
✅ Rapid prototyping
✅ JSON-heavy APIs
✅ Existing npm ecosystem usage

❌ CPU-intensive computations
❌ Low-latency requirements (<10ms)
```

**Python**
```
✅ Data science/ML integration
✅ Scripting and automation
✅ Scientific computing
✅ Rapid development
✅ Large existing Python codebase

❌ High-performance requirements
❌ Memory-constrained environments
```

**Go**
```
✅ Microservices architecture
✅ High-concurrency systems
✅ DevOps tools (CLI, infrastructure)
✅ Network services
✅ Container-native applications

❌ Complex business logic (verbose)
❌ Rapid prototyping needs
```

**Rust**
```
✅ Maximum performance critical
✅ Memory safety requirements
✅ Systems programming
✅ WebAssembly targets
✅ Low-level control needed

❌ Rapid development cycles
❌ Small teams/quick MVPs
```

## Framework Selection

### Node.js Frameworks

| Framework | Type | Use Case | Perf (RPS) |
|-----------|------|----------|------------|
| NestJS | Full-featured | Enterprise APIs | ~15K |
| Fastify | Minimal | High-performance | ~30K |
| Express | Minimal | Flexible/Simple | ~10K |
| Hono | Edge-first | Serverless | ~40K |

**NestJS (Recommended for Enterprise)**
```typescript
// Clean architecture out of the box
@Controller('users')
@UseGuards(AuthGuard)
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  @ApiOperation({ summary: 'Create user' })
  async create(@Body() dto: CreateUserDto): Promise<User> {
    return this.usersService.create(dto);
  }
}

// Features: DI, validation, OpenAPI, GraphQL, microservices
```

**Fastify (Performance Focus)**
```typescript
import Fastify from 'fastify';

const app = Fastify({ logger: true });

app.get('/users/:id', {
  schema: {
    params: { type: 'object', properties: { id: { type: 'string' } } },
    response: { 200: { type: 'object', properties: { id: { type: 'string' }, name: { type: 'string' } } } }
  }
}, async (request) => {
  return { id: request.params.id, name: 'John' };
});

// ~2x faster than Express, schema-based validation
```

### Python Frameworks

| Framework | Type | Use Case | Perf (RPS) |
|-----------|------|----------|------------|
| FastAPI | Modern async | APIs, ML serving | ~20K |
| Django | Full-featured | Full apps | ~5K |
| Flask | Minimal | Microservices | ~8K |
| Litestar | High-perf | APIs | ~25K |

**FastAPI (Recommended)**
```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: str
    email: str
    name: str

@app.post("/users", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return await user_service.create(db, user)

# Features: Auto OpenAPI, Pydantic validation, async, type hints
```

### Go Frameworks

| Framework | Type | Use Case | Perf (RPS) |
|-----------|------|----------|------------|
| Gin | Minimal | APIs | ~50K |
| Echo | Feature-rich | APIs | ~45K |
| Fiber | Express-like | Migration | ~60K |
| Chi | Minimal | Microservices | ~40K |

**Gin (Most Popular)**
```go
package main

import (
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    r.GET("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(200, gin.H{"id": id, "name": "John"})
    })

    r.Run(":8080")
}

// Minimal, fast, middleware support
```

## Database Selection

### SQL Databases

| Database | Best For | Max Connections | JSONB |
|----------|----------|-----------------|-------|
| PostgreSQL | General purpose | 100+ | Yes |
| MySQL | High read loads | 150+ | Limited |
| SQLite | Embedded/Edge | Single | No |
| CockroachDB | Distributed | Unlimited | Yes |

**PostgreSQL (Recommended)**
```sql
-- Modern features
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', name)
    ) STORED,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Full-text search index
CREATE INDEX idx_products_search ON products USING GIN (search_vector);

-- JSONB index
CREATE INDEX idx_products_metadata ON products USING GIN (metadata);
```

### NoSQL Databases

| Database | Type | Best For | Scaling |
|----------|------|----------|---------|
| MongoDB | Document | Flexible schema | Horizontal |
| Redis | Key-Value | Caching, sessions | Cluster |
| Elasticsearch | Search | Full-text, logs | Cluster |
| DynamoDB | Document | AWS serverless | Auto |
| Cassandra | Wide column | Time-series | Linear |

**MongoDB (Document Store)**
```typescript
// Flexible schema for evolving data
const productSchema = new Schema({
  name: String,
  price: Number,
  variants: [{
    sku: String,
    attributes: Schema.Types.Mixed  // Flexible attributes
  }],
  metadata: Schema.Types.Mixed
}, { timestamps: true });

// Aggregation pipeline
const results = await Product.aggregate([
  { $match: { category: 'electronics' } },
  { $group: { _id: '$brand', total: { $sum: '$sales' } } },
  { $sort: { total: -1 } }
]);
```

**Redis (Caching)**
```typescript
// Multi-purpose usage
// 1. Caching
await redis.setex('user:123', 3600, JSON.stringify(user));

// 2. Rate limiting
const key = `rate:${ip}`;
const count = await redis.incr(key);
if (count === 1) await redis.expire(key, 60);

// 3. Pub/Sub
redis.publish('orders', JSON.stringify(order));

// 4. Sorted sets (leaderboards)
await redis.zadd('scores', 100, 'player1');
const top10 = await redis.zrevrange('scores', 0, 9, 'WITHSCORES');
```

## ORM Selection

### Node.js ORMs

| ORM | Type | Migrations | Type Safety |
|-----|------|------------|-------------|
| Prisma | Query Builder | Yes | Excellent |
| TypeORM | Active Record/Data Mapper | Yes | Good |
| Drizzle | SQL-like | Yes | Excellent |
| Knex | Query Builder | Yes | Limited |

**Prisma (Recommended)**
```typescript
// schema.prisma
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String
  orders    Order[]
  createdAt DateTime @default(now())
}

// Type-safe queries
const user = await prisma.user.findUnique({
  where: { email: 'user@example.com' },
  include: { orders: true }
});

// user is fully typed with orders included
```

**Drizzle (SQL-like)**
```typescript
import { pgTable, uuid, varchar, timestamp } from 'drizzle-orm/pg-core';

const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).unique().notNull(),
  name: varchar('name', { length: 255 }).notNull(),
  createdAt: timestamp('created_at').defaultNow()
});

// SQL-like queries
const result = await db
  .select()
  .from(users)
  .where(eq(users.email, 'user@example.com'));
```

### Python ORMs

| ORM | Type | Async | Migrations |
|-----|------|-------|------------|
| SQLAlchemy 2.0 | Data Mapper | Yes | Alembic |
| Django ORM | Active Record | Limited | Built-in |
| Tortoise | Active Record | Yes | Built-in |

**SQLAlchemy 2.0**
```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

# Async queries
async with AsyncSession(engine) as session:
    result = await session.execute(
        select(User).where(User.email == "user@example.com")
    )
    user = result.scalar_one_or_none()
```

## Message Queues

| Queue | Protocol | Best For | Ordering |
|-------|----------|----------|----------|
| Redis Streams | Redis | Simple jobs | Per-stream |
| RabbitMQ | AMQP | Complex routing | Per-queue |
| Kafka | Binary | Event streaming | Per-partition |
| SQS | HTTP | AWS serverless | FIFO option |

**BullMQ (Redis-based)**
```typescript
import { Queue, Worker } from 'bullmq';

// Producer
const emailQueue = new Queue('emails', { connection });

await emailQueue.add('welcome', { userId: '123' }, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 1000 },
  removeOnComplete: { count: 1000 },
  removeOnFail: { count: 5000 }
});

// Consumer
const worker = new Worker('emails', async (job) => {
  const { userId } = job.data;
  await sendWelcomeEmail(userId);
}, {
  connection,
  concurrency: 5,
  limiter: { max: 100, duration: 1000 }
});
```

## Authentication

### Comparison

| Method | Use Case | Stateless | Security |
|--------|----------|-----------|----------|
| JWT | APIs, SPAs | Yes | Moderate |
| Session | Traditional web | No | High |
| OAuth 2.1 | Third-party auth | Yes | High |
| API Keys | Service-to-service | Yes | Moderate |

**JWT with Refresh Tokens**
```typescript
// Access token (short-lived)
const accessToken = jwt.sign(
  { userId, role },
  privateKey,
  { algorithm: 'RS256', expiresIn: '15m' }
);

// Refresh token (long-lived, stored in DB)
const refreshToken = crypto.randomBytes(32).toString('hex');
await redis.setex(`refresh:${refreshToken}`, 7 * 24 * 60 * 60, userId);

// Token rotation on refresh
async function refreshTokens(oldRefreshToken: string) {
  const userId = await redis.get(`refresh:${oldRefreshToken}`);
  if (!userId) throw new UnauthorizedException();

  await redis.del(`refresh:${oldRefreshToken}`);  // Invalidate old

  const newAccessToken = generateAccessToken(userId);
  const newRefreshToken = generateRefreshToken();

  await redis.setex(`refresh:${newRefreshToken}`, 7 * 24 * 60 * 60, userId);

  return { accessToken: newAccessToken, refreshToken: newRefreshToken };
}
```

## Validation Libraries

| Library | Language | Schema | Performance |
|---------|----------|--------|-------------|
| Zod | TypeScript | Runtime + Types | Fast |
| Yup | JavaScript | Runtime | Moderate |
| Pydantic | Python | Runtime + Types | Fast |
| Joi | JavaScript | Runtime | Moderate |

**Zod (TypeScript)**
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  email: z.string().email(),
  password: z.string()
    .min(12, 'At least 12 characters')
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[0-9]/, 'Must contain number'),
  age: z.number().int().min(13).max(120).optional(),
  role: z.enum(['user', 'admin']).default('user'),
});

type User = z.infer<typeof UserSchema>;

// Usage
const result = UserSchema.safeParse(input);
if (!result.success) {
  return { errors: result.error.issues };
}
```

## Recommended Stack Combinations

### MVP/Startup Stack
```yaml
runtime: Node.js 20
framework: NestJS or Fastify
database: PostgreSQL (Supabase/Neon)
cache: Redis (Upstash)
orm: Prisma
validation: Zod
auth: Auth0 or Clerk
hosting: Vercel/Railway
```

### Enterprise Stack
```yaml
runtime: Node.js 20 or Go
framework: NestJS
database: PostgreSQL (RDS/Cloud SQL)
cache: Redis Cluster
queue: RabbitMQ or Kafka
orm: Prisma or Drizzle
monitoring: Datadog/New Relic
infrastructure: Kubernetes (EKS/GKE)
```

### High-Performance Stack
```yaml
runtime: Go or Rust
framework: Gin/Actix-web
database: PostgreSQL + Redis
cache: Redis Cluster
queue: Kafka
protocol: gRPC internal, REST external
infrastructure: Kubernetes
```

### ML/Data Stack
```yaml
runtime: Python 3.11+
framework: FastAPI
database: PostgreSQL + MongoDB
cache: Redis
queue: Celery + Redis
ml-serving: Ray Serve
infrastructure: Kubernetes + GPUs
```

## Performance Benchmarks (2025)

### HTTP Framework RPS (Single Core)

| Framework | Language | RPS | Latency p99 |
|-----------|----------|-----|-------------|
| Actix-web | Rust | ~150K | 0.3ms |
| Hyper | Rust | ~140K | 0.4ms |
| Fiber | Go | ~60K | 0.8ms |
| Gin | Go | ~50K | 1.0ms |
| Hono | TS/Bun | ~40K | 1.2ms |
| Fastify | TS/Node | ~30K | 1.5ms |
| FastAPI | Python | ~20K | 2.0ms |
| NestJS | TS/Node | ~15K | 3.0ms |

### Database Query Performance

| Operation | PostgreSQL | MongoDB | Redis |
|-----------|------------|---------|-------|
| Simple SELECT | 0.5ms | 0.8ms | 0.1ms |
| Complex JOIN | 5-50ms | N/A | N/A |
| Index Lookup | 0.3ms | 0.5ms | 0.05ms |
| Write | 1ms | 0.5ms | 0.1ms |

## Decision Checklist

### Choosing a Runtime
- [ ] Team expertise and hiring pool
- [ ] Performance requirements
- [ ] Ecosystem and library availability
- [ ] Type safety needs
- [ ] Deployment environment

### Choosing a Database
- [ ] Data structure (relational vs document)
- [ ] Query complexity (joins, aggregations)
- [ ] Scaling requirements
- [ ] Consistency vs availability trade-offs
- [ ] Existing infrastructure

### Choosing a Framework
- [ ] Project complexity and size
- [ ] Built-in features needed
- [ ] Community and documentation
- [ ] Performance requirements
- [ ] Learning curve for team

## Resources

- TechEmpower Benchmarks: https://www.techempower.com/benchmarks/
- DB-Engines Rankings: https://db-engines.com/en/ranking
- Node.js Frameworks: https://expressjs.com/ | https://nestjs.com/
- Python Frameworks: https://fastapi.tiangolo.com/
