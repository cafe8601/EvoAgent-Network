# Database Patterns

Database design, optimization, and migration strategies for production systems (2025).

## Database Selection

| Use Case | Database | Key Feature |
|----------|----------|-------------|
| ACID transactions | PostgreSQL | Reliability, JSON, full-text search |
| Flexible schema | MongoDB | Document model, horizontal scaling |
| Caching/Sessions | Redis | Sub-ms latency, pub/sub, streams |
| Full-text search | Elasticsearch | Inverted index, analytics |
| Time-series | TimescaleDB | Compression, continuous aggregates |
| Graph queries | Neo4j | Relationship traversal |
| Wide column | Cassandra | Write throughput, availability |

## Schema Design

### Normalization Levels

```sql
-- 1NF: Atomic values, no repeating groups
-- ❌ Bad
CREATE TABLE orders (
  id INT PRIMARY KEY,
  products TEXT  -- "product1,product2,product3"
);

-- ✅ Good (1NF)
CREATE TABLE orders (id INT PRIMARY KEY);
CREATE TABLE order_items (
  order_id INT REFERENCES orders(id),
  product_id INT REFERENCES products(id),
  quantity INT,
  PRIMARY KEY (order_id, product_id)
);

-- 2NF: 1NF + no partial dependencies
-- 3NF: 2NF + no transitive dependencies
```

### Denormalization for Performance

```sql
-- Read-heavy: Denormalize to reduce JOINs
CREATE TABLE order_summaries (
  order_id INT PRIMARY KEY,
  customer_name VARCHAR(100),    -- Denormalized from customers
  total_items INT,               -- Calculated aggregate
  total_amount DECIMAL(10,2),    -- Calculated aggregate
  last_updated TIMESTAMP
);

-- Use triggers to maintain consistency
CREATE FUNCTION update_order_summary() RETURNS TRIGGER AS $$
BEGIN
  UPDATE order_summaries
  SET total_items = (SELECT COUNT(*) FROM order_items WHERE order_id = NEW.order_id),
      total_amount = (SELECT SUM(quantity * price) FROM order_items WHERE order_id = NEW.order_id),
      last_updated = NOW()
  WHERE order_id = NEW.order_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER order_items_change
AFTER INSERT OR UPDATE OR DELETE ON order_items
FOR EACH ROW EXECUTE FUNCTION update_order_summary();
```

### PostgreSQL Data Types

```sql
-- UUID primary keys
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- JSON/JSONB for flexible data
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  metadata JSONB DEFAULT '{}',
  -- Index for JSON queries
  CONSTRAINT valid_metadata CHECK (jsonb_typeof(metadata) = 'object')
);

-- Create GIN index for JSONB
CREATE INDEX idx_products_metadata ON products USING GIN (metadata);

-- Array types
CREATE TABLE articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for array queries
CREATE INDEX idx_articles_tags ON articles USING GIN (tags);

-- Enum types
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status order_status DEFAULT 'pending'
);
```

## Indexing Strategies

### Index Types

```sql
-- B-tree (default): Equality and range queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_created ON orders(created_at DESC);

-- Hash: Equality only (faster for exact match)
CREATE INDEX idx_users_id_hash ON users USING HASH (id);

-- GIN: Arrays, JSONB, full-text
CREATE INDEX idx_products_tags ON products USING GIN (tags);
CREATE INDEX idx_products_search ON products USING GIN (to_tsvector('english', name || ' ' || description));

-- GiST: Geometric, range types
CREATE INDEX idx_events_time ON events USING GIST (tstzrange(start_time, end_time));

-- BRIN: Large tables with natural ordering
CREATE INDEX idx_logs_created ON logs USING BRIN (created_at);

-- Partial indexes
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;

-- Composite indexes
CREATE INDEX idx_orders_user_status ON orders(user_id, status, created_at DESC);
```

### Index Optimization

```sql
-- Analyze index usage
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT
  schemaname || '.' || relname AS table,
  indexrelname AS index,
  pg_size_pretty(pg_relation_size(indexrelid)) AS size,
  idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Analyze query plans
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders
WHERE user_id = '123'
AND status = 'pending'
ORDER BY created_at DESC
LIMIT 10;
```

### Covering Indexes (Include)

```sql
-- Avoid table lookup for frequently queried columns
CREATE INDEX idx_orders_covering ON orders(user_id, status)
INCLUDE (total_amount, created_at);

-- Query can be answered from index alone
SELECT total_amount, created_at
FROM orders
WHERE user_id = '123' AND status = 'pending';
```

## Query Optimization

### Common Patterns

```sql
-- Pagination with cursor (better than OFFSET)
SELECT * FROM products
WHERE id > :last_id
ORDER BY id
LIMIT 20;

-- Avoid SELECT *
SELECT id, name, price FROM products WHERE category_id = :id;

-- Use EXISTS instead of COUNT for existence check
-- ❌ Slow
SELECT COUNT(*) FROM orders WHERE user_id = :id;

-- ✅ Fast
SELECT EXISTS(SELECT 1 FROM orders WHERE user_id = :id);

-- Batch inserts
INSERT INTO products (name, price, category_id)
VALUES
  ('Product 1', 10.00, 1),
  ('Product 2', 20.00, 1),
  ('Product 3', 30.00, 2)
ON CONFLICT (name) DO UPDATE SET price = EXCLUDED.price;

-- Use CTEs for complex queries
WITH active_users AS (
  SELECT id, email FROM users WHERE last_login > NOW() - INTERVAL '30 days'
),
user_orders AS (
  SELECT user_id, COUNT(*) as order_count, SUM(total) as total_spent
  FROM orders
  WHERE user_id IN (SELECT id FROM active_users)
  GROUP BY user_id
)
SELECT u.email, uo.order_count, uo.total_spent
FROM active_users u
JOIN user_orders uo ON u.id = uo.user_id
ORDER BY uo.total_spent DESC;
```

### N+1 Query Prevention

```typescript
// ❌ N+1 Problem
const users = await prisma.user.findMany();
for (const user of users) {
  const orders = await prisma.order.findMany({
    where: { userId: user.id }
  });
  // Results in N+1 queries
}

// ✅ Eager loading with include
const users = await prisma.user.findMany({
  include: {
    orders: true
  }
});

// ✅ Or use DataLoader for GraphQL
const userLoader = new DataLoader(async (userIds: string[]) => {
  const users = await prisma.user.findMany({
    where: { id: { in: userIds } }
  });
  return userIds.map(id => users.find(u => u.id === id));
});
```

## Transactions

### ACID Properties

```typescript
// Prisma transaction
const transfer = await prisma.$transaction(async (tx) => {
  // Debit from source
  const source = await tx.account.update({
    where: { id: sourceId },
    data: { balance: { decrement: amount } }
  });

  if (source.balance < 0) {
    throw new Error('Insufficient funds');
  }

  // Credit to destination
  const dest = await tx.account.update({
    where: { id: destId },
    data: { balance: { increment: amount } }
  });

  // Create transfer record
  return tx.transfer.create({
    data: { sourceId, destId, amount }
  });
});
```

### Isolation Levels

```sql
-- Read Committed (default): Prevents dirty reads
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Repeatable Read: Prevents non-repeatable reads
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Serializable: Strictest, prevents phantom reads
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

### Optimistic Locking

```typescript
// Using version column
const product = await prisma.product.findUnique({
  where: { id: productId }
});

// Update with version check
const updated = await prisma.product.updateMany({
  where: {
    id: productId,
    version: product.version  // Check version hasn't changed
  },
  data: {
    stock: product.stock - 1,
    version: { increment: 1 }
  }
});

if (updated.count === 0) {
  throw new Error('Concurrent modification detected');
}
```

### Pessimistic Locking

```sql
-- Lock row for update
SELECT * FROM products WHERE id = :id FOR UPDATE;

-- Lock with NOWAIT (fail fast)
SELECT * FROM products WHERE id = :id FOR UPDATE NOWAIT;

-- Skip locked rows (queue processing)
SELECT * FROM jobs
WHERE status = 'pending'
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;
```

## Migration Strategies

### Zero-Downtime Migrations

```sql
-- Phase 1: Add new column (nullable)
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Phase 2: Backfill data (in batches)
UPDATE users SET phone = '+1' || legacy_phone
WHERE id BETWEEN 1 AND 10000;

-- Phase 3: Add constraint
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;

-- Phase 4: Drop old column (after code deployed)
ALTER TABLE users DROP COLUMN legacy_phone;
```

### Online Schema Changes

```sql
-- PostgreSQL: Concurrent index creation
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Add foreign key in steps
-- 1. Create constraint without validation
ALTER TABLE orders
ADD CONSTRAINT fk_orders_user
FOREIGN KEY (user_id) REFERENCES users(id)
NOT VALID;

-- 2. Validate separately (less lock time)
ALTER TABLE orders VALIDATE CONSTRAINT fk_orders_user;
```

### Migration Tools

```typescript
// Prisma migration
// prisma/migrations/20240115_add_phone/migration.sql

/*
  1. Add nullable column
  2. Backfill data
  3. Add NOT NULL constraint
*/

-- 1. Add nullable column
ALTER TABLE "users" ADD COLUMN "phone" VARCHAR(20);

-- 2. Backfill (run separately via script)
-- UPDATE users SET phone = '+1' || legacy_phone WHERE phone IS NULL;

-- 3. Make NOT NULL (after backfill complete)
-- ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
```

## Connection Pooling

### PgBouncer Configuration

```ini
# pgbouncer.ini
[databases]
myapp = host=localhost port=5432 dbname=myapp

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Pool settings
pool_mode = transaction
default_pool_size = 20
max_client_conn = 1000
min_pool_size = 5

# Timeouts
server_connect_timeout = 10
server_idle_timeout = 600
client_idle_timeout = 0
```

### Application-Level Pooling

```typescript
// Prisma connection pooling
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL + '?connection_limit=20&pool_timeout=10'
    }
  }
});

// TypeORM pooling
const dataSource = new DataSource({
  type: 'postgres',
  url: process.env.DATABASE_URL,
  poolSize: 20,
  extra: {
    max: 20,
    min: 5,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 10000,
  }
});
```

## Caching Patterns

### Query Result Caching

```typescript
// Redis cache wrapper
async function cachedQuery<T>(
  key: string,
  queryFn: () => Promise<T>,
  ttlSeconds: number = 300
): Promise<T> {
  // Try cache first
  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached);
  }

  // Execute query
  const result = await queryFn();

  // Cache result
  await redis.setex(key, ttlSeconds, JSON.stringify(result));

  return result;
}

// Usage
const user = await cachedQuery(
  `user:${userId}`,
  () => prisma.user.findUnique({ where: { id: userId } }),
  600  // 10 minutes
);
```

### Cache Invalidation

```typescript
// Write-through cache
async function updateUser(id: string, data: UpdateUserDto) {
  // Update database
  const user = await prisma.user.update({
    where: { id },
    data
  });

  // Update cache
  await redis.setex(`user:${id}`, 600, JSON.stringify(user));

  // Invalidate related caches
  await redis.del(`user:${id}:orders`);

  return user;
}

// Cache-aside with invalidation
async function deleteUser(id: string) {
  await prisma.user.delete({ where: { id } });
  await redis.del([`user:${id}`, `user:${id}:*`]);
}
```

## Replication & Sharding

### Read Replicas

```typescript
// Prisma with read replicas
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL
    }
  }
});

// Read replica client
const readPrisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.READ_REPLICA_URL
    }
  }
});

// Route reads to replica
async function getUser(id: string) {
  return readPrisma.user.findUnique({ where: { id } });
}

// Route writes to primary
async function updateUser(id: string, data: any) {
  return prisma.user.update({ where: { id }, data });
}
```

### Horizontal Sharding

```typescript
// Shard routing by user ID
function getShardId(userId: string): number {
  const hash = crypto.createHash('md5').update(userId).digest('hex');
  return parseInt(hash.substring(0, 8), 16) % NUM_SHARDS;
}

function getShardConnection(shardId: number): PrismaClient {
  return shardConnections[shardId];
}

// Usage
const shardId = getShardId(userId);
const prisma = getShardConnection(shardId);
const user = await prisma.user.findUnique({ where: { id: userId } });
```

## Best Practices Checklist

- [ ] Primary keys are UUIDs or auto-increment
- [ ] Proper indexes on frequently queried columns
- [ ] Foreign keys enforce referential integrity
- [ ] Timestamps use TIMESTAMPTZ
- [ ] Large text in separate table (vertical partitioning)
- [ ] Connection pooling configured
- [ ] Slow query logging enabled
- [ ] Backups automated and tested
- [ ] Migrations are reversible
- [ ] Read replicas for read-heavy workloads

## Resources

- PostgreSQL Docs: https://www.postgresql.org/docs/
- Database Indexing: https://use-the-index-luke.com/
- Prisma: https://www.prisma.io/docs/
