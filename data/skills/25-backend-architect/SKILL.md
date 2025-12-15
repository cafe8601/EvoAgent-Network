---
name: backend-architect
description: Provides comprehensive guidance for designing and building production-ready backend systems with modern architectures (Clean, Hexagonal, DDD), APIs (REST, GraphQL, gRPC), security best practices (OWASP 2025), performance optimization, microservices patterns (Service Discovery, Event Bus, Circuit Breaker, Saga), and DevOps deployment. Use when architecting new backend systems, selecting technology stacks, implementing authentication, designing APIs, optimizing database queries, setting up microservices with event-driven architecture, or establishing backend development standards.
version: 1.1.0
author: Orchestra Research
license: MIT
tags: [Backend, Architecture, API Design, Security, DevOps, Microservices]
dependencies: []
---

# Backend Architect

## Overview

Design and build production-ready backend systems using modern architectures, security best practices, and proven patterns. This skill provides decision frameworks for architecture selection, technology stack choices, and implementation strategies.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BACKEND DEVELOPMENT LIFECYCLE                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Architecture    →  2. API Design    →  3. Security    →  4. Performance │
│     Selection           & Validation        Implementation    Optimization   │
│                                                                              │
│  5. Database        →  6. Testing       →  7. Deployment  →  8. Monitoring  │
│     Design              Strategy            & DevOps          & Observability│
└─────────────────────────────────────────────────────────────────────────────┘
```

## When to Use This Skill

**Trigger this skill when:**
- Designing new backend systems from scratch
- Selecting technology stacks for projects
- Implementing authentication/authorization systems
- Designing RESTful, GraphQL, or gRPC APIs
- Optimizing database queries and schemas
- Setting up microservices architecture
- Implementing caching and performance optimization
- Establishing security best practices (OWASP)
- Setting up CI/CD pipelines and deployment strategies
- Refactoring legacy systems for maintainability

## Architecture Decision Framework

### Quick Decision Matrix

| Project Complexity | Architecture | API Style | Database | Duration |
|-------------------|--------------|-----------|----------|----------|
| Simple CRUD | 3-Layer | REST | PostgreSQL | 2-4 weeks |
| Moderate (Auth+Cache) | Clean Architecture | REST/GraphQL | PostgreSQL + Redis | 4-8 weeks |
| Complex (AI/Real-time) | Hexagonal/DDD | gRPC + WebSocket | PostgreSQL + Redis + Queue | 8-16 weeks |
| Enterprise | Microservices | gRPC Internal, REST External | Polyglot | 16+ weeks |

### Architecture Selection Flowchart

```
Start: What's your project scale?
│
├─ Small team (<5), MVP, unclear domain
│   └─ → Monolith with 3-Layer Architecture
│
├─ Medium team (5-15), clear domains
│   └─ → Modular Monolith with Clean Architecture
│
├─ Large team (15+), independent scaling needed
│   └─ → Microservices with DDD
│
└─ Performance-critical, complex transactions
    └─ → Hexagonal Architecture with Event Sourcing
```

**See:** `references/architecture-patterns.md` for detailed patterns

## Technology Selection Guide

### Language Selection

| Need | Choose | Reasoning |
|------|--------|-----------|
| Full-stack TypeScript | Node.js + NestJS | Shared types, unified tooling |
| Data/ML integration | Python + FastAPI | Ecosystem, async support |
| High concurrency | Go + Gin | Goroutines, low memory |
| Maximum performance | Rust + Axum | Zero-cost abstractions |

### Database Selection

| Use Case | Database | Key Feature |
|----------|----------|-------------|
| ACID transactions | PostgreSQL | Reliability, JSON support |
| Flexible schema | MongoDB | Document model, scaling |
| Caching/Sessions | Redis | Sub-ms latency, pub/sub |
| Full-text search | Elasticsearch | Inverted index, analytics |
| Time-series data | TimescaleDB | Compression, partitioning |

### API Style Selection

| Scenario | Style | Reason |
|----------|-------|--------|
| Public APIs | REST | Universal compatibility |
| Complex queries | GraphQL | Flexible data fetching |
| Internal services | gRPC | Performance, type safety |
| Real-time updates | WebSocket | Bidirectional communication |

**See:** `references/technology-stack.md` for benchmarks and comparisons

## Core Workflows

### Workflow 1: API Design

```
1. Define Resources    →  2. Design Endpoints  →  3. Add Validation
   - Entity modeling       - REST conventions      - Zod/Joi schemas
   - Relationships         - HTTP methods          - Input sanitization
   - Versioning            - Status codes          - Error responses
        ↓                        ↓                       ↓
4. Authentication      →  5. Rate Limiting     →  6. Documentation
   - JWT/OAuth 2.1         - Per-user limits       - OpenAPI/Swagger
   - RBAC/ABAC             - Sliding window        - Examples
   - Refresh tokens        - Graceful degradation  - Versioning
```

**Checklist:**
- [ ] Resources follow noun conventions (`/users`, not `/getUsers`)
- [ ] HTTP methods match operations (GET read, POST create, etc.)
- [ ] Status codes are meaningful (201 Created, 422 Validation Error)
- [ ] All inputs validated with schemas
- [ ] Authentication on protected routes
- [ ] Rate limiting configured
- [ ] OpenAPI documentation generated

**See:** `references/api-design.md` for complete patterns

### Workflow 2: Security Implementation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SECURITY LAYERS (Defense in Depth)                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  Layer 1: Network        - TLS 1.3, Security Headers, WAF                   │
│  Layer 2: Authentication - OAuth 2.1 + PKCE, JWT, Argon2id                  │
│  Layer 3: Authorization  - RBAC, Resource-level permissions                 │
│  Layer 4: Input          - Parameterized queries, Zod validation            │
│  Layer 5: Data           - Encryption at rest, Field-level encryption       │
│  Layer 6: Monitoring     - Logging, Anomaly detection, Audit trails         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**OWASP Top 10 (2025) Quick Mitigations:**

| Vulnerability | Mitigation | Implementation |
|--------------|------------|----------------|
| Broken Access Control | RBAC + Resource checks | Deny by default |
| Cryptographic Failures | Argon2id, TLS 1.3 | Never bcrypt (2025) |
| Injection | Parameterized queries | 98% reduction |
| Insecure Design | Threat modeling | Design phase |
| Security Misconfig | Security headers | Helmet.js |

**See:** `references/security-guide.md` for OWASP compliance

### Workflow 3: Performance Optimization

```
Baseline Measurement
        ↓
┌───────┴───────┐
│   Identify    │
│  Bottlenecks  │
└───────┬───────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│  Optimization Strategies                                       │
├─────────────────┬─────────────────┬─────────────────┬─────────┤
│  Caching        │  Database       │  Application    │  Infra  │
│  Redis: 90%     │  Indexes: 30%   │  Async/Await    │  CDN    │
│  DB load ↓      │  I/O ↓          │  Connection pool│  LB     │
└─────────────────┴─────────────────┴─────────────────┴─────────┘
        ↓
Measure & Iterate
```

**Key Metrics:**
- API p95 latency: < 200ms
- Database query time: < 50ms
- Cache hit rate: > 90%
- Error rate: < 0.1%

**See:** `references/performance-optimization.md` for strategies

## Architecture Patterns Reference

### 3-Layer Architecture (Simple)

```
┌─────────────────────────────────────┐
│  Controller Layer (HTTP handling)   │
├─────────────────────────────────────┤
│  Service Layer (Business logic)     │
├─────────────────────────────────────┤
│  Repository Layer (Data access)     │
└─────────────────────────────────────┘
```

**Use for:** MVPs, CRUD apps, small teams

### Clean Architecture (Moderate)

```
┌────────────────────────────────────────────────────┐
│                  Frameworks & Drivers               │
│  ┌────────────────────────────────────────────┐   │
│  │           Interface Adapters                │   │
│  │  ┌────────────────────────────────────┐   │   │
│  │  │          Use Cases                  │   │   │
│  │  │  ┌────────────────────────────┐   │   │   │
│  │  │  │       Entities              │   │   │   │
│  │  │  └────────────────────────────┘   │   │   │
│  │  └────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
         Dependencies flow INWARD →
```

**Use for:** Testable systems, changing requirements

### Hexagonal Architecture (Complex)

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

**Use for:** Complex domains, multiple integrations

**See:** `references/architecture-patterns.md` for implementations

## Microservices Key Patterns

마이크로서비스 구축 시 필수적인 패턴들:

| Pattern | Purpose | Implementation |
|---------|---------|----------------|
| **Service Discovery** | 서비스 위치 동적 검색 | Consul, etcd, Kubernetes DNS |
| **Event Bus** | 비동기 통신 | RabbitMQ, Kafka, Redis Pub/Sub |
| **Circuit Breaker** | 장애 전파 방지 | Opossum, pybreaker |
| **Saga** | 분산 트랜잭션 | Orchestration/Choreography |
| **API Gateway** | 진입점 통합 | Kong, Envoy, Custom |

### Quick Example: Circuit Breaker

```typescript
import CircuitBreaker from 'opossum';

const breaker = new CircuitBreaker(callExternalService, {
  timeout: 3000,              // 3초 타임아웃
  errorThresholdPercentage: 50, // 50% 실패시 open
  resetTimeout: 30000,         // 30초 후 재시도
});

breaker.fallback(() => ({ error: 'Service unavailable' }));
const result = await breaker.fire(requestData);
```

### Quick Example: Event Bus (RabbitMQ)

```typescript
// 이벤트 발행
await eventBus.publish('order.created', {
  orderId: '123',
  customerId: 'cust-456'
});

// 이벤트 구독
await eventBus.subscribe('order.*', async (event) => {
  console.log(`Received: ${event.type}`, event.data);
});
```

**See:** `references/microservices-patterns.md` for complete implementations

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

- [ ] Initialize project with selected framework
- [ ] Set up TypeScript/linting configuration
- [ ] Configure environment management
- [ ] Set up database with migrations
- [ ] Implement health check endpoint
- [ ] Configure logging and error handling

### Phase 2: Authentication (Week 2-3)

- [ ] Implement password hashing (Argon2id)
- [ ] Create JWT token generation/validation
- [ ] Set up OAuth 2.1 with PKCE (if needed)
- [ ] Implement refresh token rotation
- [ ] Add rate limiting on auth endpoints
- [ ] Create auth middleware

### Phase 3: Core Features (Week 3-6)

- [ ] Implement business entities
- [ ] Create CRUD endpoints
- [ ] Add input validation (Zod)
- [ ] Implement authorization (RBAC)
- [ ] Add pagination and filtering
- [ ] Set up error responses

### Phase 4: Advanced Features (Week 6-8)

- [ ] Implement caching (Redis)
- [ ] Add background jobs (Queue)
- [ ] Set up WebSocket (if needed)
- [ ] Integrate external services
- [ ] Add file upload handling
- [ ] Implement search functionality

### Phase 5: Quality & Performance (Week 8-10)

- [ ] Write unit tests (70% coverage)
- [ ] Write integration tests (20% coverage)
- [ ] Add E2E tests (10% coverage)
- [ ] Performance optimization
- [ ] Security audit (OWASP checklist)
- [ ] Load testing

### Phase 6: Deployment (Week 10-12)

- [ ] Dockerize application
- [ ] Set up CI/CD pipeline
- [ ] Configure staging environment
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure alerting
- [ ] Production deployment

**See:** `checklists/` for detailed implementation checklists

## Testing Strategy

### Testing Pyramid (70-20-10)

```
        ┌─────┐
       ╱       ╲
      ╱   E2E   ╲     10% - User journeys
     ╱   Tests   ╲
    ╱─────────────╲
   ╱  Integration  ╲   20% - API contracts
  ╱     Tests       ╲
 ╱───────────────────╲
╱    Unit Tests       ╲  70% - Business logic
╲─────────────────────╱
```

**Framework Recommendations:**
- Unit: Vitest (50% faster than Jest), pytest
- Integration: Supertest, httpx
- E2E: Playwright, Cypress
- Load: k6, Artillery

**See:** `references/testing-strategies.md` for patterns

## Best Practices (2025)

### Security
- **Passwords:** Argon2id (not bcrypt)
- **Auth:** OAuth 2.1 + PKCE
- **Queries:** Parameterized (98% injection reduction)
- **Headers:** Helmet.js for security headers
- **Rate limiting:** Per-user, per-endpoint

### Performance
- **Caching:** Redis (90% DB load reduction)
- **Indexes:** Proper indexing (30% I/O reduction)
- **CDN:** Static assets (50%+ latency cut)
- **Pooling:** Connection pooling enabled

### DevOps
- **Deployments:** Blue-green/canary
- **Feature flags:** 90% fewer failures
- **Kubernetes:** 84% adoption rate
- **Monitoring:** Prometheus + Grafana
- **Tracing:** OpenTelemetry

### Code Quality
- **TypeScript:** Strict mode enabled
- **Linting:** ESLint + Prettier
- **Testing:** 70-20-10 pyramid
- **CI:** Pre-commit hooks, automated tests

## Reference Documentation

| Topic | File | Content |
|-------|------|---------|
| Architecture Patterns | `references/architecture-patterns.md` | Clean, Hexagonal, DDD, Microservices |
| **Microservices Patterns** | `references/microservices-patterns.md` | **Service Discovery, Event Bus, Saga, Circuit Breaker** |
| API Design | `references/api-design.md` | REST, GraphQL, gRPC patterns |
| Security | `references/security-guide.md` | OWASP 2025, Auth, Encryption |
| Performance | `references/performance-optimization.md` | Caching, Scaling, Optimization |
| Database | `references/database-patterns.md` | Schema design, Indexing, Migrations |
| Testing | `references/testing-strategies.md` | Unit, Integration, E2E, Load |
| DevOps | `references/devops-deployment.md` | Docker, K8s, CI/CD |
| Technology | `references/technology-stack.md` | Language/Framework comparisons |

## Templates

| Template | Location | Use Case |
|----------|----------|----------|
| Clean Architecture | `templates/clean-architecture/` | Testable, maintainable systems |
| Layered Architecture | `templates/layered-architecture/` | Standard CRUD applications |
| Microservices | `templates/microservices/` | Distributed systems |

## Checklists

| Checklist | Location | Purpose |
|-----------|----------|---------|
| API Design | `checklists/api-design-checklist.md` | REST/GraphQL validation |
| Security | `checklists/security-checklist.md` | OWASP compliance |
| Deployment | `checklists/deployment-checklist.md` | Production readiness |

---

**This skill provides comprehensive guidance for building production-ready backend systems. Start with architecture selection, follow implementation phases, and use reference documentation for detailed patterns.**
