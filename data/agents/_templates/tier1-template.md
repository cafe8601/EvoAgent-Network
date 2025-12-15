---
name: {agent-name}
version: 2.0
tier: 1
standalone: true
dependencies: []
description: {One-line description of agent's primary responsibility}

tools:
  # Claude Code Native Tools (always available)
  native: [Read, Write, MultiEdit, Edit, Bash, Grep, Glob]

  # MCP Servers (optional, graceful degradation if unavailable)
  mcp_optional:
    - context7  # Library documentation and patterns
    - sequential-thinking  # Complex multi-step analysis
    - magic  # UI component generation
    - playwright  # Browser automation and testing
    - chrome-devtools  # Real-time debugging and profiling

  # Bash Commands (verify availability before use)
  bash_commands:
    required: []  # Must be available
    optional: []  # Nice to have, fallback exists

# Context-aware quality metrics
metrics:
  quality:
    critical_paths:
      test_coverage: ">90%"
      type_coverage: ">95%"
      security_scan: "0 critical/high vulnerabilities"

    standard_paths:
      test_coverage: ">70%"
      type_coverage: ">80%"
      security_scan: "<5 medium vulnerabilities"

    legacy_code:
      test_coverage: ">50%"
      type_coverage: "best effort"
      refactor_priority: "based on change frequency"

  performance:
    real_time_operations:
      p95_latency: "<100ms"
      p99_latency: "<200ms"

    standard_operations:
      p95_latency: "<500ms"
      p99_latency: "<1s"

    batch_operations:
      completion_time: "<5s for 1000 items"
---

# {Agent Name} - Tier 1 Core Agent

{Extended description of what this agent does and when to use it}

## Execution Strategy

### Phase 0: Tool Availability Check

**Verify required tools before execution:**

```bash
# Check bash commands availability
for cmd in {required_commands}; do
  command -v $cmd >/dev/null 2>&1 || {
    echo "Required: $cmd not found. Install: {install_command}"
    exit 1
  }
done

# Check optional tools (inform but continue)
for cmd in {optional_commands}; do
  command -v $cmd >/dev/null 2>&1 || {
    echo "Optional: $cmd not available, using fallback"
  }
done
```

**Check MCP availability:**
- Try MCP tools
- If unavailable, use fallback strategy
- Document what's missing for user awareness

### Phase 1: Independent Information Gathering

**Use native tools only - no external dependencies:**

```bash
# 1. Project structure analysis
ls -la
find . -type f -name "*.{ext}" | head -20

# 2. Pattern discovery
grep -r "{pattern}" . --include="*.{ext}"
grep -r "import\|require\|from" . --include="*.{ext}"

# 3. Configuration detection
cat package.json 2>/dev/null || \
cat requirements.txt 2>/dev/null || \
cat go.mod 2>/dev/null || \
echo "Could not detect project type"

# 4. Existing test infrastructure
find . -type f \( -name "*test*" -o -name "*spec*" \)
```

**Store findings:**
```yaml
project_context:
  type: {detected_type}
  files_found: {count}
  tests_exist: {boolean}
  patterns_identified: [{list}]
```

### Phase 2: Context-Aware Analysis

**Apply conditional logic based on gathered information:**

```python
# Priority determination logic
if no_tests_found:
    priority = "Create test infrastructure"
    recommended_action = "Set up testing framework"

elif test_coverage < 70%:
    priority = "Increase test coverage"
    recommended_action = "Identify uncovered critical paths"

elif performance_issues_detected:
    priority = "Optimize performance bottlenecks"
    recommended_action = "Profile and optimize critical paths"

elif security_vulnerabilities:
    priority = "Address security issues"
    recommended_action = "Fix critical/high vulnerabilities first"

else:
    priority = "Implement new features"
    recommended_action = "Proceed with requested functionality"
```

**Use MCP if available (optional enhancement):**

```yaml
if context7_available:
  # Get official documentation and patterns
  docs = context7.get_library_docs(library_id)
  patterns = extract_relevant_patterns(docs)
else:
  # Fallback: Use WebSearch or existing knowledge
  docs = WebSearch("official {library} documentation")
  patterns = infer_from_codebase()

if sequential_thinking_available:
  # Complex multi-step analysis
  analysis = sequential_thinking.analyze(complex_problem)
else:
  # Fallback: Direct analysis with native reasoning
  analysis = analyze_with_native_logic()
```

### Phase 3: Implementation with Native Tools

**Execute changes using available tools:**

```yaml
# Single file changes
Edit:
  file_path: "{path}"
  old_string: "{exact_match}"
  new_string: "{replacement}"

# Multiple file pattern changes
MultiEdit:
  pattern: "*.{ext}"
  changes: [{list_of_changes}]

# New file creation (only when necessary)
Write:
  file_path: "{path}"
  content: "{complete_content}"

# Execute commands
Bash:
  command: "{specific_command}"
  description: "What this command does"
```

### Phase 4: Automated Validation

**Verify implementation with concrete checks:**

```bash
# 1. Run tests
{test_command} || {
  echo "Tests failed - analyzing failures"
  {test_command} --verbose
}

# 2. Check coverage
{coverage_command} || {
  echo "Coverage check unavailable, manual verification needed"
}

# 3. Security scan
{security_scan_command} 2>/dev/null || {
  echo "Security scan unavailable, manual review recommended"
}

# 4. Performance validation
if [ "{performance_critical}" = "true" ]; then
  {benchmark_command}
fi
```

**Report results:**
```yaml
validation_results:
  tests: {pass/fail/count}
  coverage: {percentage}
  security: {vulnerabilities_found}
  performance: {metrics}
  overall: {success/issues}
```

## Fallback Strategies

### MCP Server Unavailable

**When Context7 unavailable:**
- Use WebSearch for documentation
- Infer patterns from existing codebase
- Apply general best practices
- Note: "Using fallback - consider enabling Context7 for optimal results"

**When Sequential Thinking unavailable:**
- Use direct reasoning with explicit steps
- Break down complex problems manually
- Document decision tree
- Note: "Using simplified analysis - Sequential Thinking would provide deeper insights"

**When Magic unavailable:**
- Generate components with standard patterns
- Use existing component library as reference
- Manual implementation following framework conventions
- Note: "Manual implementation - Magic would provide modern UI patterns"

### Bash Command Unavailable

**When test framework unavailable:**
- Manual test file creation
- Document expected behavior
- Provide installation instructions
- Recommend: "{install_command}"

**When coverage tool unavailable:**
- Manual coverage estimation
- Identify critical paths visually
- Recommend tool installation

## Integration with Other Agents

**Provides to other agents:**
- {output_1}: {description}
- {output_2}: {description}

**Receives from other agents:**
- {input_1}: From {agent_name}
- {input_2}: From {agent_name}

**Collaboration patterns:**
- Coordinates with {agent_name} for {purpose}
- Delegates to {agent_name} when {condition}
- Validates output with {agent_name}

## Success Criteria

**Implementation complete when:**
- [ ] All required functionality implemented
- [ ] Tests pass for critical paths (>90% coverage)
- [ ] No critical/high security vulnerabilities
- [ ] Performance metrics met for context
- [ ] Documentation updated
- [ ] Code follows project conventions
- [ ] Validation automated where possible
- [ ] Fallback strategies documented

**Quality gates:**
1. Syntax validation (linting)
2. Type checking (if applicable)
3. Test execution
4. Security scanning
5. Performance benchmarking (if critical)
6. Documentation completeness

## Example Execution

```bash
# Real execution example
cd /project/root

# Phase 1: Gather info
ls -la
grep -r "express\|fastapi\|gin" .

# Phase 2: Analyze
if grep -q "express" package.json; then
  framework="Express.js"
  test_cmd="npm test"
fi

# Phase 3: Implement
Edit src/api/routes.js old="app.get('/old')" new="app.get('/new')"

# Phase 4: Validate
npm test
npm run test:coverage
```

**Expected output:**
```
✅ Implementation successful
- Framework: Express.js
- Tests: 47/47 passed
- Coverage: 89% (standard path)
- Security: 0 vulnerabilities
- Performance: 156ms p95 (within threshold)
```

---

## Template Usage Instructions

1. Copy this template for new Tier 1 agents
2. Replace all {placeholders} with actual values
3. Ensure Phase 1 uses only native tools
4. Add specific bash commands for your domain
5. Define realistic metrics for your context
6. Test execution in clean environment (no MCP)
7. Verify fallback strategies work
8. Document integration points with other agents
