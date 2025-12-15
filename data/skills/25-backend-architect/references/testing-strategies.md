# Testing Strategies

Comprehensive testing patterns for backend systems including unit, integration, E2E, and load testing (2025).

## Testing Pyramid

```
        ┌─────┐
       ╱       ╲
      ╱   E2E   ╲     10% - User journeys, critical paths
     ╱   Tests   ╲
    ╱─────────────╲
   ╱  Integration  ╲   20% - API contracts, database
  ╱     Tests       ╲
 ╱───────────────────╲
╱    Unit Tests       ╲  70% - Business logic, functions
╲─────────────────────╱
```

## Framework Selection

| Language | Unit Testing | Integration | E2E | Load |
|----------|--------------|-------------|-----|------|
| TypeScript/Node | Vitest (50% faster than Jest) | Supertest | Playwright | k6 |
| Python | pytest | pytest-asyncio + httpx | Playwright | Locust |
| Go | testing + testify | httptest | Playwright | k6 |
| Rust | built-in + rstest | actix_rt::test | Playwright | k6 |

## Unit Testing

### Test Structure (AAA Pattern)

```typescript
// Vitest example
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('OrderService', () => {
  let orderService: OrderService;
  let mockOrderRepo: MockOrderRepository;
  let mockPaymentGateway: MockPaymentGateway;

  beforeEach(() => {
    // Arrange - Set up test fixtures
    mockOrderRepo = new MockOrderRepository();
    mockPaymentGateway = new MockPaymentGateway();
    orderService = new OrderService(mockOrderRepo, mockPaymentGateway);
  });

  describe('placeOrder', () => {
    it('should successfully place order when payment succeeds', async () => {
      // Arrange
      const order = createTestOrder({ total: 100 });
      mockPaymentGateway.charge.mockResolvedValue({ success: true });

      // Act
      const result = await orderService.placeOrder(order);

      // Assert
      expect(result.success).toBe(true);
      expect(result.order.status).toBe('paid');
      expect(mockOrderRepo.save).toHaveBeenCalledWith(order);
    });

    it('should fail when payment is declined', async () => {
      // Arrange
      const order = createTestOrder({ total: 100 });
      mockPaymentGateway.charge.mockResolvedValue({
        success: false,
        error: 'Card declined'
      });

      // Act
      const result = await orderService.placeOrder(order);

      // Assert
      expect(result.success).toBe(false);
      expect(result.error).toBe('Payment failed');
      expect(mockOrderRepo.save).not.toHaveBeenCalled();
    });

    it('should throw for invalid order', async () => {
      // Arrange
      const invalidOrder = createTestOrder({ items: [] });

      // Act & Assert
      await expect(orderService.placeOrder(invalidOrder))
        .rejects.toThrow('Order must have at least one item');
    });
  });
});
```

### Mocking Patterns

```typescript
// Mock with Vitest
import { vi, Mock } from 'vitest';

// Manual mock
const mockUserRepository = {
  findById: vi.fn(),
  save: vi.fn(),
  delete: vi.fn(),
};

// Spy on existing function
const spy = vi.spyOn(userService, 'validateEmail');

// Mock module
vi.mock('../services/email', () => ({
  sendEmail: vi.fn().mockResolvedValue({ sent: true }),
}));

// Mock with implementation
mockUserRepository.findById.mockImplementation(async (id: string) => {
  if (id === 'existing-user') {
    return { id, email: 'test@example.com' };
  }
  return null;
});

// Assert mock calls
expect(mockUserRepository.findById).toHaveBeenCalledTimes(1);
expect(mockUserRepository.findById).toHaveBeenCalledWith('user-123');
```

### Testing Async Code

```typescript
// Async/await
it('should fetch user data', async () => {
  const user = await userService.getUser('123');
  expect(user.name).toBe('John');
});

// Promise rejection
it('should handle not found error', async () => {
  await expect(userService.getUser('invalid'))
    .rejects.toThrow(NotFoundException);
});

// Timeout testing
it('should timeout long operations', async () => {
  vi.useFakeTimers();

  const promise = userService.longOperation();
  vi.advanceTimersByTime(5000);

  await expect(promise).rejects.toThrow('Timeout');

  vi.useRealTimers();
});
```

### Test Fixtures

```typescript
// factories.ts - Test data factories
import { faker } from '@faker-js/faker';

export function createTestUser(overrides: Partial<User> = {}): User {
  return {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    role: 'user',
    createdAt: faker.date.past(),
    isActive: true,
    ...overrides,
  };
}

export function createTestOrder(overrides: Partial<Order> = {}): Order {
  return {
    id: faker.string.uuid(),
    userId: faker.string.uuid(),
    items: [createTestOrderItem()],
    status: 'pending',
    total: faker.number.float({ min: 10, max: 1000, fractionDigits: 2 }),
    createdAt: new Date(),
    ...overrides,
  };
}

// Usage
const user = createTestUser({ role: 'admin' });
const order = createTestOrder({ items: [], total: 0 });
```

## Integration Testing

### API Testing with Supertest

```typescript
// tests/integration/users.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import { app } from '../../src/app';
import { prisma } from '../../src/database';

describe('Users API', () => {
  let authToken: string;

  beforeAll(async () => {
    // Setup test database
    await prisma.$executeRaw`TRUNCATE TABLE users CASCADE`;

    // Create test user and get token
    const response = await request(app)
      .post('/api/auth/register')
      .send({ email: 'test@example.com', password: 'password123' });

    authToken = response.body.token;
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  describe('GET /api/users', () => {
    it('should return paginated users', async () => {
      const response = await request(app)
        .get('/api/users?page=1&limit=10')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.data).toBeInstanceOf(Array);
      expect(response.body.meta).toHaveProperty('total');
      expect(response.body.meta).toHaveProperty('page', 1);
    });

    it('should return 401 without auth token', async () => {
      await request(app)
        .get('/api/users')
        .expect(401);
    });
  });

  describe('POST /api/users', () => {
    it('should create user with valid data', async () => {
      const response = await request(app)
        .post('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          email: 'new@example.com',
          name: 'New User',
          password: 'securepass123',
        })
        .expect(201);

      expect(response.body.data).toHaveProperty('id');
      expect(response.body.data.email).toBe('new@example.com');
    });

    it('should return 422 for invalid email', async () => {
      const response = await request(app)
        .post('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          email: 'invalid-email',
          name: 'Test',
          password: 'password123',
        })
        .expect(422);

      expect(response.body.error.code).toBe('VALIDATION_ERROR');
    });
  });
});
```

### Database Testing

```typescript
// tests/integration/database.test.ts
import { describe, it, expect, beforeEach, afterAll } from 'vitest';
import { PrismaClient } from '@prisma/client';
import { createTestUser } from '../factories';

const prisma = new PrismaClient();

describe('User Repository', () => {
  beforeEach(async () => {
    // Clean up before each test
    await prisma.orderItem.deleteMany();
    await prisma.order.deleteMany();
    await prisma.user.deleteMany();
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  it('should create user with unique email', async () => {
    const userData = createTestUser();

    const user = await prisma.user.create({
      data: userData,
    });

    expect(user.id).toBeDefined();
    expect(user.email).toBe(userData.email);
  });

  it('should enforce unique email constraint', async () => {
    const userData = createTestUser();

    await prisma.user.create({ data: userData });

    await expect(
      prisma.user.create({ data: userData })
    ).rejects.toThrow('Unique constraint');
  });

  it('should cascade delete orders when user is deleted', async () => {
    const user = await prisma.user.create({
      data: createTestUser(),
    });

    await prisma.order.create({
      data: {
        userId: user.id,
        status: 'pending',
        total: 100,
      },
    });

    await prisma.user.delete({ where: { id: user.id } });

    const orders = await prisma.order.findMany({
      where: { userId: user.id },
    });
    expect(orders).toHaveLength(0);
  });
});
```

### Testing with Docker

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  test-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test_db
    ports:
      - "5433:5432"
    tmpfs:
      - /var/lib/postgresql/data  # RAM for speed

  test-redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"
```

```bash
# Run integration tests
docker-compose -f docker-compose.test.yml up -d
DATABASE_URL="postgresql://test:test@localhost:5433/test_db" npm run test:integration
docker-compose -f docker-compose.test.yml down
```

## E2E Testing

### Playwright Setup

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
  webServer: {
    command: 'npm run start:test',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### E2E Test Example

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should allow user to sign up and login', async ({ page }) => {
    // Navigate to signup page
    await page.goto('/signup');

    // Fill signup form
    await page.fill('[data-testid="email"]', 'newuser@example.com');
    await page.fill('[data-testid="password"]', 'securepassword123');
    await page.fill('[data-testid="confirm-password"]', 'securepassword123');
    await page.click('[data-testid="submit"]');

    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="welcome-message"]'))
      .toContainText('Welcome');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[data-testid="email"]', 'wrong@example.com');
    await page.fill('[data-testid="password"]', 'wrongpassword');
    await page.click('[data-testid="submit"]');

    await expect(page.locator('[data-testid="error-message"]'))
      .toContainText('Invalid credentials');
  });
});
```

### API E2E Testing

```typescript
// tests/e2e/api-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Order Flow API', () => {
  let authToken: string;
  let orderId: string;

  test.beforeAll(async ({ request }) => {
    // Login and get token
    const response = await request.post('/api/auth/login', {
      data: { email: 'test@example.com', password: 'password123' },
    });
    const body = await response.json();
    authToken = body.token;
  });

  test('complete order flow', async ({ request }) => {
    // Create order
    const createResponse = await request.post('/api/orders', {
      headers: { Authorization: `Bearer ${authToken}` },
      data: {
        items: [{ productId: 'prod-1', quantity: 2 }],
      },
    });
    expect(createResponse.ok()).toBeTruthy();
    const order = await createResponse.json();
    orderId = order.data.id;

    // Process payment
    const paymentResponse = await request.post(`/api/orders/${orderId}/pay`, {
      headers: { Authorization: `Bearer ${authToken}` },
      data: { paymentMethodId: 'pm_test' },
    });
    expect(paymentResponse.ok()).toBeTruthy();

    // Verify order status
    const getResponse = await request.get(`/api/orders/${orderId}`, {
      headers: { Authorization: `Bearer ${authToken}` },
    });
    const updatedOrder = await getResponse.json();
    expect(updatedOrder.data.status).toBe('paid');
  });
});
```

## Load Testing

### k6 Load Test

```javascript
// load-tests/api.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Ramp up
    { duration: '3m', target: 50 },   // Steady state
    { duration: '1m', target: 100 },  // Peak load
    { duration: '2m', target: 100 },  // Sustained peak
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% under 500ms
    errors: ['rate<0.01'],              // Error rate under 1%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export function setup() {
  // Login and return auth token
  const response = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    email: 'loadtest@example.com',
    password: 'testpassword',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  return { token: response.json().token };
}

export default function (data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  // Test endpoints
  const endpoints = [
    { method: 'GET', url: '/api/users', weight: 40 },
    { method: 'GET', url: '/api/products', weight: 30 },
    { method: 'GET', url: '/api/orders', weight: 20 },
    { method: 'POST', url: '/api/orders', weight: 10, body: {
      items: [{ productId: 'prod-1', quantity: 1 }]
    }},
  ];

  // Weighted random endpoint selection
  const random = Math.random() * 100;
  let cumulative = 0;

  for (const endpoint of endpoints) {
    cumulative += endpoint.weight;
    if (random <= cumulative) {
      const start = Date.now();

      let response;
      if (endpoint.method === 'GET') {
        response = http.get(`${BASE_URL}${endpoint.url}`, { headers });
      } else {
        response = http.post(`${BASE_URL}${endpoint.url}`,
          JSON.stringify(endpoint.body), { headers });
      }

      apiDuration.add(Date.now() - start);

      const success = check(response, {
        'status is 2xx': (r) => r.status >= 200 && r.status < 300,
        'response time < 500ms': (r) => r.timings.duration < 500,
      });

      errorRate.add(!success);
      break;
    }
  }

  sleep(Math.random() * 2 + 1);  // 1-3 second think time
}

export function handleSummary(data) {
  return {
    'load-test-results.json': JSON.stringify(data, null, 2),
  };
}
```

### Running Load Tests

```bash
# Basic run
k6 run load-tests/api.js

# With custom base URL
k6 run -e BASE_URL=https://staging.example.com load-tests/api.js

# Output to cloud dashboard
k6 cloud load-tests/api.js
```

## Test Configuration

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    exclude: ['tests/e2e/**'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
    setupFiles: ['./tests/setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run test:unit -- --coverage
      - uses: codecov/codecov-action@v4

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run db:migrate:test
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test
      - run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

## Best Practices Checklist

### Unit Tests
- [ ] Follow AAA pattern (Arrange, Act, Assert)
- [ ] One assertion per test (ideally)
- [ ] Mock external dependencies
- [ ] Use descriptive test names
- [ ] Test edge cases and error paths
- [ ] Maintain test factories

### Integration Tests
- [ ] Use test database (not production)
- [ ] Clean up after tests
- [ ] Test API contracts
- [ ] Verify database constraints
- [ ] Test authentication flows

### E2E Tests
- [ ] Focus on critical user journeys
- [ ] Use stable selectors (data-testid)
- [ ] Run in CI/CD pipeline
- [ ] Generate screenshots on failure
- [ ] Keep tests independent

### Load Tests
- [ ] Define performance thresholds
- [ ] Simulate realistic user behavior
- [ ] Run against staging environment
- [ ] Monitor during tests
- [ ] Document baseline metrics

## Resources

- Vitest: https://vitest.dev/
- Playwright: https://playwright.dev/
- k6: https://k6.io/docs/
- Testing Library: https://testing-library.com/
