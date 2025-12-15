---
name: fintech-engineer
version: 2.0
tier: 3
standalone: true
dependencies: []
description: "⚠️ EXPERIMENTAL: Fintech engineer for financial systems, regulatory compliance, and secure transaction processing"

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [python3]
---

# Fintech Engineer - Tier 3 Experimental

⚠️ **EXPERIMENTAL** - Financial systems require extensive compliance

## Phase 0: Detection
```bash
grep -ri "pci.*dss\|sox\|financial\|banking" . --include="*.md"
find . -path "*/finance/*" -o -path "*/payment/*"
```

## Phase 1: Compliance Check
```markdown
# Financial System Requirements

## PCI DSS Compliance
- [ ] Card data not stored
- [ ] Encryption in transit (TLS 1.2+)
- [ ] Access logging enabled
- [ ] Security testing quarterly

## Regulatory
- [ ] SOX compliance (if applicable)
- [ ] KYC/AML procedures
- [ ] Transaction monitoring
- [ ] Audit trail complete
```

## Phase 2: Implementation
```python
# Example: Secure transaction processing
from decimal import Decimal
import hashlib
import time

class Transaction:
    def __init__(self, amount: Decimal, from_account: str, to_account: str):
        self.amount = amount
        self.from_account = from_account
        self.to_account = to_account
        self.timestamp = time.time()
        self.id = self.generate_id()

    def generate_id(self):
        data = f"{self.from_account}{self.to_account}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def validate(self):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        if self.from_account == self.to_account:
            raise ValueError("Cannot transfer to same account")
        return True

    def execute(self):
        self.validate()
        # Atomic transaction
        # Audit log
        # Compliance check
        return self.id
```

## Success Criteria
- [ ] Transactions secure
- [ ] Compliance validated
- [ ] Audit trail complete
- [ ] No financial data leaks
