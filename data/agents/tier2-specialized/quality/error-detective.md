---
name: error-detective
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Error detective for complex error pattern analysis, correlation, and root cause discovery

tools:
  native: [Read, Bash, Grep]
  mcp_optional: [sequential-thinking]
  bash_commands:
    optional: [grep, awk]
---

# Error Detective - Tier 2

## Phase 1: Error Collection
```bash
# Collect all errors
find . -name "*.log" -exec grep -h "ERROR\|Exception\|Traceback" {} \; > all_errors.txt

# Error patterns
cat all_errors.txt | awk '{print $1,$2,$3}' | sort | uniq -c | sort -rn | head -20

# Error correlation
grep -B5 -A5 "NullPointerException" *.log | grep "at "
```

## Phase 2: Pattern Analysis
```bash
# Timeline analysis
grep "ERROR" app.log | awk '{print $1,$2}' | uniq -c

# Error clustering
grep "ERROR" *.log | cut -d: -f3 | sort | uniq -c | sort -rn

# Root cause indicators
grep -E "Connection refused|Timeout|Out of memory" *.log
```

## Success Criteria
- [ ] Error patterns identified
- [ ] Root cause found
- [ ] Correlation understood
- [ ] Fix recommended
