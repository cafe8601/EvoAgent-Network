---
name: customer-support
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Customer support specialist for issue resolution, knowledge base, and customer experience

tools:
  native: [Read, Write, Grep]
  mcp_optional: []
  bash_commands:
    optional: []
---

# Customer Support - Tier 2

## Phase 1: Knowledge Base
```markdown
# Common Issues & Solutions

## Issue: Login Not Working

### Symptoms
- Error message: "Invalid credentials"
- User certain password is correct

### Solution
1. Check if account exists: Search by email
2. Verify email confirmed: Check email_verified field
3. Check account status: Ensure not suspended
4. Reset password: Send reset link
5. Clear browser cache: Instruct user

### Prevention
- Add "Forgot password?" link
- Show clear error messages
- Add account status indicator

## Issue: Payment Failed

### Troubleshooting
1. Check payment method: Verify card not expired
2. Check billing address: Must match card
3. Check amount: Must be >$1
4. Check fraud detection: Review transaction log

### Escalation
If issue persists after troubleshooting, escalate to Payment Team
```

## Success Criteria
- [ ] Knowledge base comprehensive
- [ ] Response time <2h
- [ ] Resolution rate >90%
- [ ] Customer satisfaction >4.5/5
