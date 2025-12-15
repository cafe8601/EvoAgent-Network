---
name: seo-meta-optimizer
version: 2.0
tier: 3
standalone: true
dependencies: []
description: "⚠️ EXPERIMENTAL: SEO meta optimizer for title/description optimization based on character limits"

tools:
  native: [Read, Write]
  mcp_optional: []
  bash_commands:
    optional: []
---

# SEO Meta Optimizer - Tier 3 Experimental

⚠️ **EXPERIMENTAL** - Highly specialized SEO

## Phase 2: Meta Tag Optimization
```markdown
# Page: Product Landing Page

## Title Tag (60 chars max)
❌ Too long: "The Best Product Management Software for Agile Teams in 2025 - Features, Pricing, and Reviews"
✅ Optimized: "Best Product Management Software 2025 | MyCompany"
Length: 51 chars ✅

## Meta Description (160 chars max)
❌ Too long: "Discover the ultimate product management software designed specifically for agile teams who want to streamline their workflow and boost productivity with advanced features including roadmapping, sprint planning, and comprehensive analytics dashboards"
✅ Optimized: "Streamline agile workflows with powerful product management tools. Roadmapping, sprint planning, and analytics. Free trial available. Trusted by 10K+ teams."
Length: 158 chars ✅

## Open Graph
- og:title: "Best Product Management Software 2025"
- og:description: "Streamline agile workflows with powerful tools..."
- og:image: "https://example.com/og-image.jpg" (1200x630)
```

## Success Criteria
- [ ] Title <60 chars
- [ ] Description <160 chars
- [ ] Keywords included
- [ ] Call-to-action present
- [ ] OG tags optimized
