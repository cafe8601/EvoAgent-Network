# Plan Review Guide: Multi-Model Consultation

This document provides comprehensive guidance on multi-perspective review for SDD specifications.

---

## Overview

Plan Review is the multi-perspective feedback stage for Spec-Driven Development. It convenes multiple AI reviewers to provide structured, actionable feedback across key dimensions before implementation begins.

### Purpose

- Build shared understanding of spec strengths, risks, and improvement opportunities
- Produce categorized feedback organized by type
- Synthesize reviewer perspectives into clear, prioritized insights
- Recommend handoffs to correct downstream skills

**This stage is advisory-only.** The output is a structured feedback report and clear guidance on follow-up work.

---

## When to Request Review

### Do Request Review When:

| Situation | Review Type |
|-----------|-------------|
| Draft spec ready for approval | Full review |
| Security-critical area (auth/data/privacy) | Security review |
| Feasibility questions or aggressive estimates | Feasibility review |
| Major architectural novelty or integration risk | Full review |
| Unsure about confidence level | Quick review |

### Skip Review When:

- Lightweight, low-risk spec (< 5 tasks)
- Well-understood patterns (CRUD operations)
- Trivial bug fixes
- Work already executing (use fidelity-review instead)

---

## Review Types

### Overview Table

| Type | Models | Duration | Dimensions Emphasized |
|------|--------|----------|----------------------|
| **quick** | 2 | 10-15 min | Completeness, Clarity |
| **full** | 3-4 | 20-30 min | All 6 dimensions |
| **security** | 2-3 | 15-20 min | Risk Management |
| **feasibility** | 2-3 | 10-15 min | Feasibility |

### Quick Review

**Focus**: Basic completeness and clarity  
**Best For**: Simple specs, low-risk changes, time pressure

**What it checks:**
- All required sections present
- Tasks clearly described with acceptance criteria
- Dependencies explicitly stated
- Basic verification steps exist
- No obvious gaps or ambiguities

**Skip detailed analysis of:**
- Architecture soundness
- Performance implications
- Security edge cases
- Implementation complexity

### Full Review

**Focus**: Comprehensive analysis across all dimensions  
**Best For**: Complex specs, moderate-to-high risk, cross-team changes

**What it checks:**
- **Completeness**: All sections present, sufficient detail, no gaps
- **Clarity**: Clear descriptions, acceptance criteria, unambiguous language
- **Feasibility**: Realistic estimates, achievable dependencies, proper sizing
- **Architecture**: Sound design, proper abstractions, scalability
- **Risk Management**: Risks identified, edge cases covered, failure modes
- **Verification**: Comprehensive testing plan, verification steps, quality gates

### Security Review

**Focus**: Security vulnerabilities and risks  
**Best For**: Auth/authz, data handling, API security, regulated domains

**What it checks:**
- Authentication and authorization design
- Input validation and sanitization
- Secrets management (API keys, passwords, tokens)
- Access control and principle of least privilege
- Audit logging and monitoring
- Data encryption (at rest, in transit)
- SQL/command injection prevention
- CSRF/XSS protections
- Rate limiting and DoS protection
- Compliance requirements (GDPR, HIPAA, SOC2)

### Feasibility Review

**Focus**: Implementation realism and estimate accuracy  
**Best For**: Tight deadlines, resource constraints, uncertain requirements

**What it checks:**
- Time estimates realistic for each task
- Required skills present in team
- Dependencies actually exist and are accessible
- External APIs/services available and documented
- Performance requirements achievable
- Complexity accurately assessed
- Blockers identified and mitigated
- Resource requirements feasible

---

## Review Dimensions

Every review examines specs across **6 dimensions**:

### 1. Completeness
- All sections present
- Sufficient detail for implementation
- No missing requirements or undefined dependencies
- Acceptance criteria for all tasks

### 2. Clarity
- Clear, unambiguous descriptions
- Specific acceptance criteria
- Well-defined task boundaries
- No vague or confusing language

### 3. Feasibility
- Realistic time estimates
- Achievable dependencies
- Required skills available
- No impossible requirements

### 4. Architecture
- Sound design decisions
- Proper abstractions
- Scalability considerations
- Low coupling, high cohesion

### 5. Risk Management
- Risks identified
- Edge cases covered
- Failure modes addressed
- Mitigation strategies present

### 6. Verification
- Comprehensive test plan
- Verification steps defined
- Quality gates established
- Testing gaps identified

---

## Feedback Categories

Review findings are organized into structured categories:

### Missing Information
Identifies gaps where the spec needs more detail.

**Examples:**
- "Task 2.3 lacks acceptance criteria - unclear when task is complete"
- "Authentication flow missing error handling details"
- "Database migration steps not specified in Phase 3"
- "No rollback strategy defined for deployment tasks"

### Design Concerns
Highlights architectural or design choices that may need reconsideration.

**Examples:**
- "Tight coupling between auth module and user service may hinder testing"
- "Synchronous API calls in task 1.4 could create bottlenecks under load"
- "Consider event-driven pattern instead of polling for real-time updates"
- "Circular dependency between modules A and B needs resolution"

### Risk Flags
Surfaces potential security, performance, or reliability risks.

**Examples:**
- "Admin endpoints lack authentication checks (security risk)"
- "No rate limiting on public API (DoS vulnerability)"
- "Storing passwords in plaintext violates security best practices"
- "Missing input validation could allow SQL injection"
- "No monitoring for critical payment processing flow"

### Feasibility Questions
Raises concerns about estimates, dependencies, or implementation approach.

**Examples:**
- "Task 3.2 estimated at 2 hours but involves complex OAuth integration (likely 6-8 hours)"
- "Phase 2 assumes legacy API has endpoint X - need to verify availability"
- "Database migration in task 4.1 requires DBA access - confirm permissions"
- "Timeline assumes 3 developers but team currently has 2"

### Enhancement Suggestions
Proposes improvements that aren't critical but would strengthen the spec.

**Examples:**
- "Consider adding health check endpoints for monitoring"
- "Could benefit from batch processing for large datasets"
- "Adding retry logic would improve resilience"
- "Documentation task for API endpoints would help future maintenance"

### Clarification Requests
Identifies ambiguous language or unclear requirements.

**Examples:**
- "What does 'performant' mean in acceptance criteria? Need specific metrics"
- "Task 2.1 says 'update user profile' - which fields are in scope?"
- "'Handle errors gracefully' is vague - specify retry strategy, logging, user messaging"
- "Does 'mobile support' include tablets or just phones?"

---

## The Review Workflow

### Phase 1: Preparation

**Before running review, ensure:**

1. **Tool availability**
   - Need at least 1 AI tool installed
   - 2+ tools recommended for multi-model review
   - All 3 tools ideal for comprehensive analysis

2. **Specification ready**
   - Spec must be complete (not draft fragments)
   - JSON format required
   - Frontmatter should include complexity/risk metadata

3. **Select review type**
   - Auto-selected based on spec metadata
   - Or explicitly specify with `--type` flag

### Phase 2: Execute Review

**Multi-model consultation (parallel execution):**

```
Reviewing specification: user-auth-001.json
Using 3 tool(s): gemini, codex, claude

Starting full review...
✓ gemini completed (15.2s)
✓ codex completed (22.5s)
✗ claude timeout (120s)

Review Complete
Execution time: 120.1s
Models responded: 2/3
```

**Automatic error handling:**
- Timeouts → Automatic retries with backoff
- Rate limits → Sequential mode fallback
- Auth failures → Skip tool with clear message
- Parse failures → Use other model responses

### Phase 3: Interpret Results

**Reviewer Consensus:**
- **Strong consensus**: Multiple reviewers identified same issue
- **Diverse perspectives**: Different reviewers raised different concerns
- **Conflicting views**: Reviewers disagree (both perspectives documented)

**Priority Levels:**

| Level | Description | Action |
|-------|-------------|--------|
| **CRITICAL** | Security vulnerabilities, blockers, data loss risks | Address immediately |
| **HIGH** | Design flaws, missing information, quality issues | Address before implementation |
| **MEDIUM** | Improvements, unclear requirements | Consider addressing |
| **LOW** | Nice-to-have enhancements | Note for future |

**Example findings:**

```markdown
📋 Feedback Summary:

### Risk Flags (CRITICAL)
1. Missing authentication on admin endpoints
   Priority: CRITICAL | Flagged by: gemini, codex
   Impact: Unauthorized access to sensitive operations
   Recommendation: Add JWT validation middleware to routes

### Feasibility Questions (HIGH)
2. Time estimates may be unrealistic for Phase 2
   Priority: HIGH | Flagged by: codex
   Impact: Timeline risk - complex OAuth integration underestimated
   Recommendation: Revisit estimates for tasks 2.3-2.5 (suggest +50%)

### Missing Information (MEDIUM)
3. Error handling strategy not defined
   Priority: MEDIUM | Flagged by: gemini
   Impact: Unclear how failures should be handled
   Recommendation: Add error handling details to affected tasks
```

### Phase 4: Synthesize Findings & Recommend Handoffs

1. **Organize feedback by category and priority**
   - Group findings by category
   - Prioritize within each category
   - Note reviewer consensus

2. **Identify the type of downstream work**
   - Structural or architectural redesign
   - Documentation or metadata updates
   - Additional planning or investigation
   - Additional audits (security review, validation)

3. **Capture the feedback summary**
   - Highlight key findings
   - Note areas of consensus and disagreement
   - Return path to JSON report for full context

---

## Error Handling

### Automatic Recovery

| Error Type | Behavior | User Impact |
|------------|----------|-------------|
| Timeout (>120s) | Retry with backoff (2 attempts) | Longer wait |
| Rate limit (429) | Wait + retry, or sequential mode | Slower execution |
| Auth failure (401/403) | Skip tool, continue with others | Reduced confidence |
| Network error | Retry 2x with backoff | Usually recovers |
| Parse failure | Use other model responses | No impact if ≥2 succeed |

### Partial Results

| Scenario | Outcome | Confidence |
|----------|---------|------------|
| 3/3 tools succeed | Full review | High |
| 2/3 tools succeed | Continue with 2 | Medium |
| 1/3 tools succeed | Continue with 1 | Low |
| 0/3 tools succeed | Review fails | Error |

---

## Best Practices

### When to Review

**Always review:**
- High-risk or high-priority specs
- Security-sensitive implementations
- Novel architecture or technology choices
- Before final approval and team commitment

**Consider reviewing:**
- Medium complexity (≥ 10 tasks)
- Cross-team dependencies
- Specs with aggressive timelines
- Unclear or novel requirements

**Skip review:**
- Simple specs (< 5 tasks)
- Well-understood patterns
- Low-risk internal refactorings
- Trivial bug fixes

### Review Quality Tips

1. **Review complete specs, not fragments**
   - All phases defined
   - Tasks described
   - Dependencies stated
   - Verification steps present

2. **Use appropriate review type**
   - Quick: Simple, low-risk
   - Full: Complex, moderate-to-high risk
   - Security: Auth/data handling
   - Feasibility: Tight timelines

3. **Address issues by priority**
   - CRITICAL → Must fix before proceeding
   - HIGH → Should fix, significant impact
   - MEDIUM → Consider, nice-to-have
   - LOW → Note for future

4. **Don't blindly accept all feedback**
   - Consider context and tradeoffs
   - Models may misunderstand requirements
   - Use judgment on disagreements

### Coordinating Follow-Up Work

**Prioritization guide:**

```
CRITICAL findings:
  - Security vulnerabilities
  - Blocking dependencies
  - Data loss risks
  - Compliance violations
  → Address immediately before implementation

HIGH findings:
  - Design flaws
  - Missing information
  - Unrealistic estimates
  - Quality concerns
  → Address before implementation begins

MEDIUM findings:
  - Unclear requirements
  - Missing optimizations
  - Incomplete documentation
  → Consider addressing; may defer with rationale

LOW findings:
  - Nice-to-have improvements
  - Edge case enhancements
  - Future considerations
  → Note for future work; safe to defer
```

---

## Outputs

### Feedback Report (Markdown)

Saved to: `specs/.reviews/<spec-id>-review-<type>.md`

Contents:
- Review metadata (type, tools, duration)
- Executive summary
- Categorized findings with priorities
- Reviewer consensus notes
- Recommended handoffs

### JSON Summary

Saved to: `specs/.reviews/<spec-id>-review-<type>.json`

Contents:
- Feedback categories
- Participating tools
- Issue catalog for orchestration
- Machine-readable format

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Review completed successfully |
| 1 | Review failed (configuration, tool errors) |
| 2 | Critical feedback items found (CI/CD integration) |

---

## Scope Boundaries

### This Skill DOES:
✅ Convene multi-model reviews  
✅ Interrogate assumptions  
✅ Aggregate perspectives  
✅ Categorize feedback by type  
✅ Capture review metadata  
✅ Provide clear guidance for downstream skills  

### This Skill Does NOT:
❌ Edit specifications or apply fixes  
❌ Update spec metadata, journals, or approval status  
❌ Make approval/rejection decisions  
❌ Author execution plans or task breakdowns  
❌ Update journals, statuses, or frontmatter  

---

## Quick Reference

| Action | When |
|--------|------|
| Request `quick` review | Simple, low-risk, time-constrained |
| Request `full` review | Complex, moderate-to-high risk |
| Request `security` review | Auth, data, privacy, compliance |
| Request `feasibility` review | Tight timeline, uncertain scope |
| Skip review | < 5 tasks, well-understood patterns |
