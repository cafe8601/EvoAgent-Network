#!/bin/bash
# Agent Validation Script v2.0
# Validates agent files against Tier 1/2 standards

set -e

AGENT_FILE=$1
EXIT_CODE=0

if [ -z "$AGENT_FILE" ]; then
    echo "Usage: $0 <agent-file.md>"
    exit 1
fi

if [ ! -f "$AGENT_FILE" ]; then
    echo "❌ File not found: $AGENT_FILE"
    exit 1
fi

echo "🔍 Validating: $AGENT_FILE"
echo "================================"

# Extract YAML frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/p' "$AGENT_FILE" | sed '1d;$d')

# Function to check field
check_field() {
    local field=$1
    local required=$2

    if echo "$FRONTMATTER" | grep -q "^$field:"; then
        value=$(echo "$FRONTMATTER" | grep "^$field:" | cut -d':' -f2- | xargs)
        echo "✅ $field: $value"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo "❌ Missing required field: $field"
            EXIT_CODE=1
            return 1
        else
            echo "⚠️  Optional field missing: $field"
            return 0
        fi
    fi
}

# 1. Syntax Validation
echo -e "\n📋 Section 1: Syntax Validation"
echo "--------------------------------"

# Check YAML frontmatter exists
if echo "$FRONTMATTER" | grep -q "name:"; then
    echo "✅ Valid YAML frontmatter found"
else
    echo "❌ Invalid or missing YAML frontmatter"
    EXIT_CODE=1
fi

# 2. Required Fields
echo -e "\n📋 Section 2: Required Fields"
echo "--------------------------------"

check_field "name" "true"
check_field "version" "true"
check_field "tier" "true"
check_field "standalone" "true"
check_field "description" "true"

# Check version is 2.0
if echo "$FRONTMATTER" | grep -q "version: 2.0"; then
    echo "✅ Version 2.0 confirmed"
else
    echo "❌ Version must be 2.0"
    EXIT_CODE=1
fi

# Check standalone is true
if echo "$FRONTMATTER" | grep -q "standalone: true"; then
    echo "✅ Standalone mode enabled"
else
    echo "❌ Must be standalone: true"
    EXIT_CODE=1
fi

# 3. Tool Classification
echo -e "\n📋 Section 3: Tool Classification"
echo "--------------------------------"

if grep -q "tools:" "$AGENT_FILE"; then
    echo "✅ Tools section found"

    if grep -q "native:" "$AGENT_FILE"; then
        echo "✅ Native tools declared"
    else
        echo "❌ Missing native tools declaration"
        EXIT_CODE=1
    fi

    if grep -q "mcp_optional:" "$AGENT_FILE"; then
        echo "✅ MCP tools classified as optional"
    fi

    if grep -q "bash_commands:" "$AGENT_FILE"; then
        echo "✅ Bash commands listed"
    fi
else
    echo "❌ No tools section found"
    EXIT_CODE=1
fi

# 4. Execution Logic
echo -e "\n📋 Section 4: Execution Logic"
echo "--------------------------------"

# Check for phases
PHASE_COUNT=$(grep -c "^### Phase" "$AGENT_FILE" || true)
if [ "$PHASE_COUNT" -ge 3 ]; then
    echo "✅ Multi-phase execution found ($PHASE_COUNT phases)"
else
    echo "⚠️  Expected multiple execution phases, found: $PHASE_COUNT"
fi

# Check for native tool usage
if grep -q "Read\|Grep\|Bash" "$AGENT_FILE"; then
    echo "✅ Uses native tools"
else
    echo "❌ Must use native tools for independence"
    EXIT_CODE=1
fi

# Check for conditional logic
if grep -qE "if.*then|if.*:" "$AGENT_FILE"; then
    echo "✅ Conditional logic present"
else
    echo "⚠️  No conditional logic found"
fi

# Check for bash commands
if grep -q '```bash' "$AGENT_FILE"; then
    BASH_COUNT=$(grep -c '```bash' "$AGENT_FILE")
    echo "✅ Concrete bash commands found ($BASH_COUNT blocks)"
else
    echo "⚠️  No bash command examples"
fi

# 5. Fallback Strategy
echo -e "\n📋 Section 5: Fallback Strategy"
echo "--------------------------------"

if grep -qi "fallback" "$AGENT_FILE"; then
    echo "✅ Fallback strategy documented"
else
    echo "❌ Missing fallback strategy"
    EXIT_CODE=1
fi

if grep -qi "unavailable\|not available\|missing" "$AGENT_FILE"; then
    echo "✅ Handles tool unavailability"
else
    echo "⚠️  Should handle tool unavailability"
fi

# 6. Metrics
echo -e "\n📋 Section 6: Metrics & Quality"
echo "--------------------------------"

if grep -q "metrics:" "$AGENT_FILE"; then
    echo "✅ Metrics defined"

    if grep -qE "<[0-9]+ms|>[0-9]+%" "$AGENT_FILE"; then
        echo "✅ Measurable thresholds found"
    else
        echo "⚠️  Metrics should have measurable thresholds"
    fi
else
    echo "⚠️  No metrics defined"
fi

# 7. Independence Check
echo -e "\n📋 Section 7: Independence Check"
echo "--------------------------------"

# Should NOT have context manager dependency
if grep -qi "query context manager\|request_type.*context" "$AGENT_FILE"; then
    echo "❌ Contains context manager dependency (v1.0 pattern)"
    EXIT_CODE=1
else
    echo "✅ No context manager dependency"
fi

# Should NOT have JSON protocol
if grep -q '"requesting_agent"\|"request_type"\|"payload"' "$AGENT_FILE"; then
    echo "❌ Contains JSON protocol (v1.0 pattern)"
    EXIT_CODE=1
else
    echo "✅ No JSON protocol dependency"
fi

# 8. Documentation
echo -e "\n📋 Section 8: Documentation"
echo "--------------------------------"

if grep -q "## Success Criteria\|Success Criteria" "$AGENT_FILE"; then
    echo "✅ Success criteria defined"
else
    echo "⚠️  Success criteria recommended"
fi

if grep -q "## Example\|Example Execution" "$AGENT_FILE"; then
    echo "✅ Usage examples provided"
else
    echo "⚠️  Usage examples recommended"
fi

# Final Result
echo -e "\n================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ VALIDATION PASSED"
    echo "Agent meets Tier $(echo "$FRONTMATTER" | grep "^tier:" | cut -d':' -f2 | xargs) standards"
else
    echo "❌ VALIDATION FAILED"
    echo "Fix issues above before using this agent"
fi

exit $EXIT_CODE
