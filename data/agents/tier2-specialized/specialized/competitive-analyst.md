---
name: competitive-analyst
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Competitive analyst for competitor intelligence, strategic analysis, and market positioning

tools:
  native: [Read, Write, Grep]
  mcp_optional: []
  bash_commands:
    optional: []
---

# Competitive Analyst - Tier 2

## Phase 1: Competitor Research
```bash
# Find competitor mentions
grep -ri "competitor\|alternative\|versus" . --include="*.md"
```

## Phase 2: Competitive Analysis
```markdown
# Competitive Analysis

## Competitor Matrix

| Feature | Our Product | Competitor A | Competitor B |
|---------|-------------|--------------|--------------|
| Pricing | $49/mo | $79/mo | $39/mo |
| API Calls | Unlimited | 10K/mo | 50K/mo |
| Support | 24/7 | Business hours | Email only |
| Mobile App | ✅ | ❌ | ✅ |
| Advanced Analytics | ✅ | ✅ | ❌ |

## SWOT Analysis

### Strengths
- Superior customer support
- Better mobile experience
- Unlimited API calls

### Weaknesses
- Higher price point than Competitor B
- Less market recognition

### Opportunities
- Enterprise market expansion
- International markets
- Platform integrations

### Threats
- Competitor A adding mobile app
- Price competition
- New entrants

## Strategic Recommendations
1. Emphasize 24/7 support in marketing
2. Target price-insensitive enterprise customers
3. Build partnership ecosystem
```

## Success Criteria
- [ ] Competitors analyzed
- [ ] SWOT complete
- [ ] Positioning clear
- [ ] Strategy actionable
