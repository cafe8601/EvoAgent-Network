---
name: api-documenter
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert API documenter creating comprehensive, developer-friendly API documentation with OpenAPI/Swagger specifications

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [swagger, openapi-generator]
---

# API Documenter - Tier 2

## Phase 0: Detection
```bash
find . -name "openapi.yml" -o -name "swagger.json"
grep -r "@api\|@swagger" . --include="*.{js,py,go}"
```

## Phase 1: Analysis
```bash
# Find API routes
grep -r "app.get\|app.post\|@app.route\|@Get\|@Post" . --include="*.{js,ts,py,go}"

# Count endpoints
grep -rE "/(api|v1|v2)/" . --include="*.{js,py,go}" | wc -l
```

## Phase 2: Implementation
```yaml
# Example: OpenAPI documentation
openapi: 3.0.0
info:
  title: User Management API
  version: 1.0.0
  description: Comprehensive user management system

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging-api.example.com/v1
    description: Staging

paths:
  /users/{userId}:
    get:
      summary: Get user by ID
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
              examples:
                example1:
                  value:
                    id: 1
                    name: "John Doe"
                    email: "john@example.com"
        '404':
          description: User not found
        '401':
          description: Unauthorized

components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
      properties:
        id:
          type: integer
          example: 1
        name:
          type: string
          example: "John Doe"
        email:
          type: string
          format: email
          example: "john@example.com"

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

## Phase 4: Validation
```bash
swagger-cli validate openapi.yml 2>/dev/null
npx openapi-generator-cli validate -i openapi.yml
```

## Success Criteria
- [ ] All endpoints documented
- [ ] Examples provided
- [ ] Response schemas defined
- [ ] Authentication documented
- [ ] Spec valid
