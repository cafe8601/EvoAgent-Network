# Performance Optimization

Strategies for optimizing backend performance including caching, database tuning, and infrastructure scaling (2025).

## Performance Metrics

### Key Metrics (SLOs)

| Metric | Target | Critical |
|--------|--------|----------|
| API p50 latency | < 50ms | < 100ms |
| API p95 latency | < 200ms | < 500ms |
| API p99 latency | < 500ms | < 1000ms |
| Error rate | < 0.1% | < 1% |
| Availability | 99.9% | 99% |
| Cache hit rate | > 90% | > 80% |

### Measurement Tools

```typescript
// Custom metrics with Prometheus
import { Counter, Histogram, Registry } from 'prom-client';

const registry = new Registry();

const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
  registers: [registry],
});

const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
  registers: [registry],
});

// Express middleware
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const labels = {
      method: req.method,
      route: req.route?.path || req.path,
      status_code: res.statusCode,
    };

    httpRequestDuration.observe(labels, duration);
    httpRequestsTotal.inc(labels);
  });

  next();
});
```

## Caching Strategies

### Cache Hierarchy

```
Request → Application Cache (in-memory) → Redis → Database
            ~1μs latency              ~1ms        ~10-100ms
```

### Redis Caching Patterns

```typescript
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

// Cache-Aside Pattern
async function getUserWithCache(userId: string): Promise<User> {
  const cacheKey = `user:${userId}`;

  // Try cache first
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }

  // Fetch from database
  const user = await prisma.user.findUnique({
    where: { id: userId },
    include: { profile: true },
  });

  if (user) {
    // Cache with TTL
    await redis.setex(cacheKey, 3600, JSON.stringify(user));
  }

  return user;
}

// Write-Through Pattern
async function updateUser(userId: string, data: UpdateUserDto): Promise<User> {
  const user = await prisma.user.update({
    where: { id: userId },
    data,
  });

  // Update cache immediately
  await redis.setex(`user:${userId}`, 3600, JSON.stringify(user));

  return user;
}

// Cache Invalidation
async function deleteUser(userId: string): Promise<void> {
  await prisma.user.delete({ where: { id: userId } });

  // Delete from cache
  await redis.del(`user:${userId}`);

  // Invalidate related caches
  await redis.del(`user:${userId}:orders`);
  await redis.del(`user:${userId}:preferences`);
}
```

### Cache Stampede Prevention

```typescript
// Probabilistic early recomputation
async function getWithEarlyRecompute<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl: number,
  beta: number = 1  // Higher = more aggressive early recompute
): Promise<T> {
  const cached = await redis.get(key);

  if (cached) {
    const { value, expiry, delta } = JSON.parse(cached);
    const now = Date.now();

    // Probabilistic early recompute
    const random = Math.random();
    const xFetch = delta * beta * Math.log(random);

    if (now - xFetch < expiry) {
      return value;
    }
  }

  const start = Date.now();
  const value = await fetchFn();
  const delta = Date.now() - start;

  await redis.setex(key, ttl, JSON.stringify({
    value,
    expiry: Date.now() + ttl * 1000,
    delta,
  }));

  return value;
}

// Lock-based stampede prevention
async function getWithLock<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl: number
): Promise<T> {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const lockKey = `lock:${key}`;
  const acquired = await redis.set(lockKey, '1', 'NX', 'EX', 10);

  if (!acquired) {
    // Wait and retry
    await new Promise(r => setTimeout(r, 100));
    return getWithLock(key, fetchFn, ttl);
  }

  try {
    const value = await fetchFn();
    await redis.setex(key, ttl, JSON.stringify(value));
    return value;
  } finally {
    await redis.del(lockKey);
  }
}
```

### In-Memory Caching

```typescript
// LRU Cache for hot data
import { LRUCache } from 'lru-cache';

const localCache = new LRUCache<string, any>({
  max: 1000,          // Max items
  maxSize: 50000000,  // 50MB max size
  sizeCalculation: (value) => JSON.stringify(value).length,
  ttl: 1000 * 60 * 5, // 5 minutes
});

// Multi-tier caching
async function getUser(userId: string): Promise<User> {
  // L1: In-memory cache
  const l1Key = `user:${userId}`;
  const l1Cached = localCache.get(l1Key);
  if (l1Cached) return l1Cached;

  // L2: Redis cache
  const l2Cached = await redis.get(l1Key);
  if (l2Cached) {
    const user = JSON.parse(l2Cached);
    localCache.set(l1Key, user);
    return user;
  }

  // L3: Database
  const user = await prisma.user.findUnique({
    where: { id: userId },
  });

  if (user) {
    localCache.set(l1Key, user);
    await redis.setex(l1Key, 3600, JSON.stringify(user));
  }

  return user;
}
```

## Database Optimization

### Query Optimization

```sql
-- Identify slow queries
SELECT
  query,
  calls,
  total_time / 1000 as total_seconds,
  mean_time / 1000 as mean_seconds,
  rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 20;

-- Missing indexes
SELECT
  schemaname,
  tablename,
  seq_scan,
  seq_tup_read,
  idx_scan,
  idx_tup_fetch,
  seq_tup_read / NULLIF(seq_scan, 0) as avg_seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 10;
```

### Connection Pooling

```typescript
// Prisma with connection pooling
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: `${process.env.DATABASE_URL}?connection_limit=20&pool_timeout=10`,
    },
  },
});

// PgBouncer for external pooling
// DATABASE_URL=postgres://user:pass@pgbouncer:6432/db?pgbouncer=true
```

### Read Replicas

```typescript
// Route reads to replica
const readPrisma = new PrismaClient({
  datasources: {
    db: { url: process.env.READ_REPLICA_URL },
  },
});

const writePrisma = new PrismaClient({
  datasources: {
    db: { url: process.env.DATABASE_URL },
  },
});

async function getUsers() {
  return readPrisma.user.findMany();  // Read from replica
}

async function createUser(data: CreateUserDto) {
  return writePrisma.user.create({ data });  // Write to primary
}
```

## Async Processing

### Message Queues

```typescript
// BullMQ for job processing
import { Queue, Worker } from 'bullmq';

const connection = { host: 'localhost', port: 6379 };

// Producer
const emailQueue = new Queue('emails', { connection });

async function sendWelcomeEmail(userId: string) {
  await emailQueue.add('welcome', { userId }, {
    attempts: 3,
    backoff: { type: 'exponential', delay: 1000 },
  });
}

// Consumer
const worker = new Worker('emails', async (job) => {
  if (job.name === 'welcome') {
    const { userId } = job.data;
    const user = await prisma.user.findUnique({ where: { id: userId } });
    await sendEmail(user.email, 'Welcome!', welcomeTemplate(user));
  }
}, { connection, concurrency: 5 });

worker.on('failed', (job, err) => {
  console.error(`Job ${job.id} failed:`, err);
});
```

### Event-Driven Architecture

```typescript
// Event emitter pattern
import { EventEmitter } from 'events';

class DomainEvents extends EventEmitter {
  private static instance: DomainEvents;

  static getInstance(): DomainEvents {
    if (!DomainEvents.instance) {
      DomainEvents.instance = new DomainEvents();
    }
    return DomainEvents.instance;
  }
}

const events = DomainEvents.getInstance();

// Register handlers
events.on('user.created', async (user: User) => {
  await emailQueue.add('welcome', { userId: user.id });
  await analyticsService.track('user_signup', { userId: user.id });
});

events.on('order.completed', async (order: Order) => {
  await inventoryService.decrementStock(order.items);
  await notificationService.notifyCustomer(order);
});

// Emit events
async function createUser(data: CreateUserDto) {
  const user = await prisma.user.create({ data });
  events.emit('user.created', user);
  return user;
}
```

## API Optimization

### Response Compression

```typescript
import compression from 'compression';

app.use(compression({
  filter: (req, res) => {
    if (req.headers['x-no-compression']) return false;
    return compression.filter(req, res);
  },
  level: 6,  // Balance between speed and compression
  threshold: 1024,  // Only compress > 1KB
}));
```

### HTTP/2 and Keep-Alive

```typescript
import http2 from 'http2';
import fs from 'fs';

const server = http2.createSecureServer({
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.crt'),
  allowHTTP1: true,  // Fallback for older clients
});

server.on('request', app);
server.listen(443);
```

### API Response Optimization

```typescript
// Selective field projection
app.get('/users/:id', async (req, res) => {
  const fields = req.query.fields?.split(',') || ['id', 'name', 'email'];

  const select = fields.reduce((acc, field) => {
    acc[field] = true;
    return acc;
  }, {} as Record<string, boolean>);

  const user = await prisma.user.findUnique({
    where: { id: req.params.id },
    select,
  });

  res.json({ data: user });
});

// Batch requests
app.post('/batch', async (req, res) => {
  const { requests } = req.body;

  const results = await Promise.all(
    requests.map(async (request: BatchRequest) => {
      try {
        const result = await processRequest(request);
        return { success: true, data: result };
      } catch (error) {
        return { success: false, error: error.message };
      }
    })
  );

  res.json({ results });
});
```

## Infrastructure Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
```

### Load Balancing

```nginx
# nginx.conf
upstream api_servers {
    least_conn;  # Load balance by least connections
    server api:3000 weight=5;
    server api:3001 weight=5;
    server api:3002 weight=5;
    keepalive 32;
}

server {
    listen 80;

    location / {
        proxy_pass http://api_servers;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # Timeouts
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check endpoint (no load balancing)
    location /health {
        proxy_pass http://api_servers;
    }
}
```

### Auto-Scaling (Kubernetes)

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: 1000
```

## Performance Monitoring

### Application Performance Monitoring

```typescript
// OpenTelemetry setup
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: 'http://jaeger:4318/v1/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

// Custom spans
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('my-service');

async function processOrder(orderId: string) {
  return tracer.startActiveSpan('processOrder', async (span) => {
    span.setAttribute('order.id', orderId);

    try {
      const order = await fetchOrder(orderId);
      await processPayment(order);
      await updateInventory(order);

      span.setStatus({ code: SpanStatusCode.OK });
      return order;
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      span.recordException(error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

### Performance Dashboard

```typescript
// Grafana dashboard JSON
{
  "panels": [
    {
      "title": "Request Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(http_requests_total[5m])",
          "legendFormat": "{{method}} {{route}}"
        }
      ]
    },
    {
      "title": "Response Time P95",
      "type": "graph",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
          "legendFormat": "p95"
        }
      ]
    },
    {
      "title": "Error Rate",
      "type": "singlestat",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{status_code=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100"
        }
      ]
    }
  ]
}
```

## Optimization Checklist

### Quick Wins (Immediate Impact)
- [ ] Enable response compression (gzip/brotli)
- [ ] Add database indexes for frequent queries
- [ ] Implement Redis caching for hot data
- [ ] Enable connection pooling
- [ ] Set appropriate HTTP cache headers

### Medium Effort (Significant Impact)
- [ ] Async processing for non-critical operations
- [ ] Read replicas for read-heavy workloads
- [ ] Query optimization (N+1, projections)
- [ ] CDN for static assets
- [ ] API response pagination

### High Effort (Long-term Scalability)
- [ ] Horizontal scaling with load balancing
- [ ] Database sharding strategy
- [ ] Event-driven architecture
- [ ] Service decomposition (if needed)
- [ ] Full observability stack

## Performance Targets

| Metric | Bronze | Silver | Gold |
|--------|--------|--------|------|
| p95 Latency | < 500ms | < 200ms | < 100ms |
| Error Rate | < 1% | < 0.1% | < 0.01% |
| Cache Hit | > 80% | > 90% | > 95% |
| Availability | 99% | 99.9% | 99.99% |
| RPS/Instance | 100 | 500 | 1000 |

## Resources

- Web Performance: https://web.dev/performance/
- PostgreSQL Tuning: https://postgresqlco.nf/
- Redis Best Practices: https://redis.io/docs/management/optimization/
- OpenTelemetry: https://opentelemetry.io/docs/
