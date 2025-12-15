# API Design Checklist

Comprehensive checklist for designing and validating REST, GraphQL, and gRPC APIs.

## REST API Checklist

### Resource Design
- [ ] Resources are nouns (plural): `/users`, `/products`, `/orders`
- [ ] No verbs in URLs: `/users` not `/getUsers`
- [ ] Hierarchical relationships: `/users/{id}/orders`
- [ ] Consistent naming convention (kebab-case or snake_case)
- [ ] API versioning implemented: `/api/v1/...`

### HTTP Methods
- [ ] GET for reading (no side effects)
- [ ] POST for creating new resources
- [ ] PUT for full resource replacement
- [ ] PATCH for partial updates
- [ ] DELETE for removing resources
- [ ] HEAD for checking resource existence
- [ ] OPTIONS for CORS preflight

### Status Codes
- [ ] 200 OK for successful GET/PUT/PATCH
- [ ] 201 Created for successful POST (with Location header)
- [ ] 204 No Content for successful DELETE
- [ ] 400 Bad Request for malformed requests
- [ ] 401 Unauthorized for authentication errors
- [ ] 403 Forbidden for authorization errors
- [ ] 404 Not Found for missing resources
- [ ] 409 Conflict for resource conflicts
- [ ] 422 Unprocessable Entity for validation errors
- [ ] 429 Too Many Requests for rate limiting
- [ ] 500 Internal Server Error for server failures

### Request/Response Format
- [ ] Consistent JSON structure for responses
- [ ] Error responses include error code and message
- [ ] Validation errors include field-level details
- [ ] Collection responses include pagination metadata
- [ ] Date/time in ISO 8601 format with timezone
- [ ] IDs as strings (UUIDs preferred)

### Pagination
- [ ] Pagination implemented for all list endpoints
- [ ] Cursor-based pagination for large datasets
- [ ] Page size limits enforced
- [ ] Meta includes total count and hasMore
- [ ] Links include self, next, prev URLs

### Filtering & Sorting
- [ ] Filter parameters are consistent
- [ ] Sort parameter supports multiple fields
- [ ] Sort direction indicated (- prefix or asc/desc)
- [ ] Field selection supported (?fields=id,name)

### Security
- [ ] Authentication required on protected endpoints
- [ ] Authorization checked at resource level
- [ ] Rate limiting configured per endpoint
- [ ] Input validation on all endpoints
- [ ] Output encoding for XSS prevention
- [ ] CORS properly configured

### Documentation
- [ ] OpenAPI/Swagger specification complete
- [ ] All endpoints documented
- [ ] Request/response examples provided
- [ ] Error responses documented
- [ ] Authentication methods documented

---

## GraphQL API Checklist

### Schema Design
- [ ] Types use PascalCase
- [ ] Fields use camelCase
- [ ] Clear type descriptions
- [ ] Non-nullable fields marked with `!`
- [ ] Connections use Relay specification
- [ ] Input types for mutations
- [ ] Payload types for mutation results

### Queries
- [ ] Query fields are nouns
- [ ] List queries return connections
- [ ] Filtering via input arguments
- [ ] Pagination via first/after, last/before

### Mutations
- [ ] Mutations use verb naming
- [ ] Input wrapped in `input` argument
- [ ] Return payload with entity and errors
- [ ] Idempotency keys for retries

### Performance
- [ ] DataLoader implemented for N+1 prevention
- [ ] Query complexity limits set
- [ ] Query depth limits configured
- [ ] Batch requests supported
- [ ] Persisted queries for production

### Security
- [ ] Authentication integrated
- [ ] Field-level authorization
- [ ] Rate limiting on complexity
- [ ] Introspection disabled in production
- [ ] Input validation on all resolvers

---

## gRPC API Checklist

### Proto Design
- [ ] Package versioned: `package api.v1`
- [ ] Service names are PascalCase
- [ ] RPC methods are PascalCase
- [ ] Message names are PascalCase
- [ ] Field names are snake_case
- [ ] Field numbers never reused

### Message Design
- [ ] Request/Response pairs for each RPC
- [ ] Wrapper messages for single values
- [ ] Oneof for mutually exclusive fields
- [ ] Repeated for arrays
- [ ] Maps for key-value pairs

### Error Handling
- [ ] Status codes follow gRPC conventions
- [ ] Error details in Status.details
- [ ] Retry policies configured
- [ ] Deadlines set on clients

### Streaming
- [ ] Unary for simple request/response
- [ ] Server streaming for large responses
- [ ] Client streaming for uploads
- [ ] Bidirectional for real-time

### Security
- [ ] TLS for all connections
- [ ] Authentication metadata
- [ ] Authorization interceptors
- [ ] Rate limiting

---

## Common Checks

### Performance
- [ ] Response times < 200ms p95
- [ ] Caching headers set appropriately
- [ ] Compression enabled (gzip/brotli)
- [ ] Connection pooling configured
- [ ] Database queries optimized

### Reliability
- [ ] Retries with exponential backoff
- [ ] Circuit breakers for dependencies
- [ ] Timeouts configured
- [ ] Health check endpoints
- [ ] Graceful degradation

### Observability
- [ ] Request logging
- [ ] Metrics collection
- [ ] Distributed tracing
- [ ] Error tracking
- [ ] Alerting configured

### Testing
- [ ] Unit tests for handlers
- [ ] Integration tests for API contracts
- [ ] Load tests for performance
- [ ] Security tests (OWASP)
- [ ] Contract tests for consumers
