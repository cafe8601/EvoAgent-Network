---
name: reference-builder
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Reference builder creating exhaustive technical references and API documentation with searchable materials

tools:
  native: [Read, Write, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: []
---

# Reference Builder - Tier 2

## Phase 1: API Discovery
```bash
grep -r "@api\|@param\|@returns" . --include="*.{js,ts,py}"
find . -name "openapi.yml" -o -name "swagger.json"
```

## Phase 2: Reference Generation
```markdown
# API Reference

## Authentication

### POST /api/auth/login
Authenticates user and returns JWT token.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| email | string | Yes | User email address |
| password | string | Yes | User password |

**Response: 200 OK**
\`\`\`json
{
  "token": "eyJhbGc...",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
\`\`\`

**Errors:**
- 401: Invalid credentials
- 429: Too many requests
- 500: Server error

**Example:**
\`\`\`bash
curl -X POST http://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'
\`\`\`
```

## Success Criteria
- [ ] All endpoints documented
- [ ] Parameters listed
- [ ] Examples included
- [ ] Errors documented
- [ ] Searchable format
