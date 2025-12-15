# Claude Code Agent System v2.0

Production-ready, independently executable AI agents with realistic metrics and comprehensive fallback strategies.

## 🎯 Overview

**159 specialized agents** organized in 3-tier architecture for software development, infrastructure, data science, and business operations.

### Key Features
- ✅ **100% Standalone** - No external dependencies required
- ✅ **Realistic Metrics** - Context-aware quality targets
- ✅ **Graceful Degradation** - Works without MCP servers
- ✅ **Concrete Logic** - Actual bash commands and conditionals
- ✅ **Automated Validation** - Built-in quality checks

---

## 📊 Quick Stats

| Metric | Count | Status |
|--------|-------|--------|
| Total Agents | 159 | Organized |
| Tier 1 (Core) | 20 | 1/20 Complete |
| Tier 2 (Specialized) | 60 | Pending |
| Tier 3 (Experimental) | 60 | Pending |
| v1.0 Backup | 159 | Archived |

---

## 🚀 Quick Start

### Basic Usage

```bash
# Use Tier 1 agent (fully independent)
invoke_agent("tier1-core/backend-developer")

# → Works with native tools only
# → Uses MCP if available (optional)
# → Graceful fallback if missing
```

### Validate Agent

```bash
~/.claude/agents/_templates/validate-agent.sh \
  tier1-core/backend-developer.md

# Output:
✅ VALIDATION PASSED
Agent meets Tier 1 standards
```

---

## 📁 Directory Structure

```
~/.claude/agents/
├── tier1-core/           # 20 essential
│   └── backend-developer.md ✅
├── tier2-specialized/    # 60 experts
├── tier3-experimental/   # 60 optional
├── _templates/          # Templates & tools
├── _deprecated/         # v1.0 backup
├── README.md
└── MIGRATION_GUIDE.md
```

---

## 🎯 Example Output

```yaml
✅ Backend Complete

Tests: 58/58 passed
Coverage: 89% (>70% threshold)
Security: 0 vulnerabilities
Performance: 187ms p95 (<500ms)
API Docs: OpenAPI generated
```

---

## 📚 Documentation

- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Complete v1→v2 migration
- **Templates** - Agent creation templates
- **Each Agent** - Built-in documentation

---

## 🔄 Status

### Complete ✅
- v2.0 architecture designed
- Templates created
- Backend-developer migrated
- Validation automated

### In Progress 🚧
- 19 Tier 1 agents
- Tier 2/3 organization

---

**For full details:** See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

**Version:** 2.0.0 | **Updated:** Oct 2, 2025
