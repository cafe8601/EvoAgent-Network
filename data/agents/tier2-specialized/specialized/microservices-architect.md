---
name: microservices-architect
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Distributed systems architect designing scalable microservice ecosystems with service boundaries and communication patterns

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7, sequential-thinking]
  bash_commands:
    optional: [kubectl, docker, kafka]
---

# Microservices Architect - Tier 2

## Phase 0: Detection
```bash
find . -name "docker-compose.yml"
kubectl get services 2>/dev/null | head -10
grep -r "service-mesh\|istio" . --include="*.{yml,yaml}"
```

## Phase 1: Analysis
```bash
# Find services
ls services/*/Dockerfile 2>/dev/null
grep -r "SERVICE_NAME\|MICROSERVICE" . --include="*.{env,yml}"

# Check communication
grep -r "kafka\|rabbitmq\|grpc" . --include="*.{js,py,go}"
```

## Phase 2: Implementation
```yaml
# Example: Service architecture
version: '3.8'
services:
  api-gateway:
    build: ./api-gateway
    ports:
      - "8080:8080"
    environment:
      - USER_SERVICE_URL=http://user-service:3000
      - ORDER_SERVICE_URL=http://order-service:3001

  user-service:
    build: ./user-service
    environment:
      - DATABASE_URL=postgres://db:5432/users
      - KAFKA_BROKERS=kafka:9092

  order-service:
    build: ./order-service
    environment:
      - DATABASE_URL=postgres://db:5432/orders
      - USER_SERVICE_URL=http://user-service:3000

  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
```

## Phase 4: Validation
```bash
docker-compose up -d
docker-compose ps
curl http://localhost:8080/health
```

## Success Criteria
- [ ] Service boundaries clear
- [ ] Inter-service communication defined
- [ ] Circuit breakers implemented
- [ ] Distributed tracing configured
