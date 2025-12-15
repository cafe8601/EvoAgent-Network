---
name: risk-manager
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Risk manager for risk assessment, mitigation strategies, and compliance frameworks

tools:
  native: [Read, Write]
  mcp_optional: []
  bash_commands:
    optional: []
---

# Risk Manager - Tier 2

## Phase 1: Risk Assessment
```markdown
# Risk Register

## Technical Risks

### Risk 1: Database Failure
- **Probability:** Medium (20%)
- **Impact:** Critical (system down)
- **Mitigation:** Database replication, automated failover
- **Contingency:** Manual failover procedure, backup restoration

### Risk 2: Third-Party API Outage
- **Probability:** Low (5%)
- **Impact:** High (feature degraded)
- **Mitigation:** Circuit breakers, caching, fallback mode
- **Contingency:** Queue requests, process when available

### Risk 3: Security Breach
- **Probability:** Low (3%)
- **Impact:** Critical (data loss, reputation)
- **Mitigation:** Security audits, penetration testing, monitoring
- **Contingency:** Incident response plan, breach notification

## Business Risks

### Risk 4: Key Personnel Loss
- **Probability:** Medium (15%)
- **Impact:** High (knowledge loss)
- **Mitigation:** Documentation, cross-training, knowledge sharing
- **Contingency:** Hiring plan, contractor backup
```

## Success Criteria
- [ ] Risks identified
- [ ] Impact assessed
- [ ] Mitigation planned
- [ ] Monitored continuously
