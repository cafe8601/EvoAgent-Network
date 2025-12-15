---
name: {agent-name}
version: 2.0
tier: 2
standalone: true
dependencies:
  tier1: []  # Optional Tier 1 agents this works with
description: {Specialized capability description}

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: []
  bash_commands:
    required: []
    optional: []

metrics:
  primary_goal: {measurable_metric}
  quality_threshold: {percentage_or_value}
  performance_target: {latency_or_throughput}
---

# {Agent Name} - Tier 2 Specialized Agent

{Brief description of specialized functionality}

## Quick Start

### 1. Information Gathering
```bash
# Discover relevant files and patterns
{specific_grep_or_find_commands}
```

### 2. Core Logic
```python
if {condition}:
    {action}
else:
    {fallback}
```

### 3. Implementation
- Use {specific_tool} for {purpose}
- Apply {pattern} when {condition}

### 4. Validation
```bash
{validation_command}
```

## Fallback Strategy
- Primary: {approach}
- Fallback: {alternative}

## Integration
- Works with: {tier1_agent_names}
- Output format: {description}

## Success Criteria
- [ ] {criterion_1}
- [ ] {criterion_2}
- [ ] {criterion_3}
