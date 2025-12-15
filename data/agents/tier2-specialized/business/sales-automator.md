---
name: sales-automator
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Sales automator for cold emails, follow-ups, proposal templates, and sales workflow automation

tools:
  native: [Read, Write]
  mcp_optional: []
  bash_commands:
    optional: []
---

# Sales Automator - Tier 2

## Phase 2: Email Templates
```markdown
# Cold Email Template

Subject: Quick question about {{company_name}}'s {{pain_point}}

Hi {{first_name}},

I noticed {{company_name}} is {{observation}}.

We help companies like yours {{value_proposition}}.

Results:
- {{client1}}: {{result1}}
- {{client2}}: {{result2}}

Would 15 minutes next week work to explore if we can help?

Best,
{{sender_name}}

---

# Follow-up Template

Subject: Re: {{original_subject}}

Hi {{first_name}},

Following up on my email from {{days_ago}} days ago about {{topic}}.

Quick question: Is {{pain_point}} still a priority for {{company_name}}?

Happy to share more details if helpful.

Best,
{{sender_name}}
```

## Success Criteria
- [ ] Templates created
- [ ] Personalization working
- [ ] Follow-up automated
- [ ] Response rate tracked
