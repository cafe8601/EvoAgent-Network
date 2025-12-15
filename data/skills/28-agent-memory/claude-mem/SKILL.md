---
name: claude-mem-session-memory
description: Claude Code plugin providing persistent observation memory across sessions. Use when agents need to maintain context beyond ~50 tool uses, search past work history, or implement progressive disclosure memory patterns. Captures tool executions and generates AI-compressed summaries.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Agent Memory, Session Memory, Observation Memory, Claude Code, Context Compression, Vector Search]
dependencies: [node>=18.0.0, claude-code-plugin-support]
---

# Claude-Mem - Observation Memory for Claude Code

Persistent memory plugin that captures tool usage, compresses context with AI, and injects relevant history into future sessions.

## When to Use Claude-Mem

**Use Claude-Mem when:**
- Sessions hit context limits (~50 tool uses)
- Need to search past work with natural language ("what did I do with auth?")
- Working solo with detailed session history requirements
- Want automatic observation capture without manual logging
- Implementing progressive disclosure memory patterns

**Key features:**
- **Automatic capture**: Hooks into Claude Code lifecycle (SessionStart, PostToolUse, SessionEnd)
- **AI compression**: Uses Claude Agent SDK to generate ~500 token observations
- **Hybrid search**: SQLite FTS5 + Chroma vector DB for semantic queries
- **Progressive disclosure**: Layer 1 (index) → Layer 2 (details) → Layer 3 (full transcript)
- **mem-search skill**: Natural language queries auto-invoked by Claude

**Metrics:**
- **Token savings**: ~2,250 tokens per session vs raw injection
- **Endless Mode**: ~95% context reduction, ~20x more tool uses
- **Storage**: ~500 tokens per observation (compressed)

**Use alternatives instead:**
- **Grov**: For team collaboration and reasoning-focused memory (see `28-agent-memory/grov`)
- **Beads**: For task/issue tracking, not session memory (see `28-agent-memory/beads`)
- **MCP Memory Server**: For simple key-value memory without compression
- **Manual CLAUDE.md**: For static project context, not dynamic session history

## Quick Start

### Installation

```bash
# In Claude Code
> /plugin marketplace add thedotmack/claude-mem
> /plugin install claude-mem
```

**Requirements**: Node.js 18+, Claude Code with plugin support

### Verify Installation

```bash
# Check worker is running
curl http://localhost:37777/health

# View web UI
open http://localhost:37777
```

### Basic Usage

Once installed, claude-mem works automatically:

```
Session 1: You work on auth module
↓
claude-mem captures: "Modified auth/login.ts, added JWT validation"
↓
Session 2: You ask about auth
↓
Claude auto-searches memory and finds relevant context
```

## Core Architecture

### Memory Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Session Start → Inject recent observations as context       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Tool Executions → Capture observations (Read, Write, etc.)  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Worker Processes → Extract learnings via Claude Agent SDK   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Session Ends → Generate summary, ready for next session     │
└─────────────────────────────────────────────────────────────┘
```

### Progressive Disclosure Layers

| Layer | Content | Token Cost | Access Method |
|-------|---------|------------|---------------|
| Layer 1 | Index (what exists) | ~100 tokens | Auto-inject at session start |
| Layer 2 | Details (narratives) | ~500 tokens | On-demand via mem-search |
| Layer 3 | Full transcript | Variable | Explicit request only |

### Storage Structure

```
~/.claude-mem/
├── memory.db          # SQLite with FTS5
├── chroma/            # Vector embeddings
├── transcripts/       # Full session logs
└── config.json        # User settings
```

## mem-search Skill

Claude automatically invokes mem-search when asked about past work:

```
User: "What did I do with the authentication module last week?"

Claude: [auto-invokes mem-search]
→ Searches observations by file path, time, concepts
→ Returns relevant context with progressive disclosure
```

### Search Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| `observations` | Search all observations | "auth module changes" |
| `sessions` | Find specific sessions | "yesterday's work" |
| `file_refs` | Search by file path | "src/auth/*.ts" |
| `concepts` | Search by tagged concepts | "discovery", "problem-solution" |
| `prompts` | Search user prompts | "fix bug" queries |

### Manual Search

```bash
# Via CLI
claude-mem search "authentication changes"

# Via API
curl "http://localhost:37777/search?q=auth&limit=10"
```

## Endless Mode (Beta)

Experimental feature for extended sessions:

```bash
# Enable in config
claude-mem config set endless_mode true
```

**How it works:**
1. Compresses tool outputs into ~500 token observations
2. Preserves full transcripts on disk
3. Allows ~20x more tool uses before context exhaustion

**Trade-offs:**
| Benefit | Cost |
|---------|------|
| ~95% token reduction | 60-90s latency per tool |
| Extended sessions | Experimental stability |
| Full transcript backup | Higher API usage |

## Privacy Controls

### Exclude Sensitive Content

```markdown
<!-- In your code or prompts -->
<private>
API_KEY=sk-secret-key
DATABASE_PASSWORD=mysecret
</private>
```

Content wrapped in `<private>` tags is never stored.

### Configuration

```bash
# Disable specific hooks
claude-mem config set capture_tool_outputs false

# Set retention period
claude-mem config set retention_days 30

# Clear all memory
claude-mem clear --confirm
```

## Integration Patterns

### With Grov (Hybrid Setup)

Use claude-mem for search, Grov for team context:

```bash
# Grov: Team context injection (enabled)
grov proxy

# claude-mem: Disable auto-inject, use search only
claude-mem config set auto_inject false
```

Now:
- Grov injects team reasoning at session start
- claude-mem provides on-demand search for detailed history

### With LangChain Agents

```python
from langchain.tools import tool
import requests

@tool
def search_memory(query: str) -> str:
    """Search past work sessions for relevant context."""
    response = requests.get(
        "http://localhost:37777/search",
        params={"q": query, "limit": 5}
    )
    return response.json()

# Add to agent tools
agent = create_agent(
    tools=[search_memory, ...],
    system_prompt="Use search_memory to find past work context."
)
```

### General Agent Memory Pattern

Apply claude-mem's architecture to any agent:

```python
class ObservationMemory:
    """claude-mem pattern for general agents."""

    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self.vector_store = ChromaDB(db_path + "/chroma")

    def capture_observation(self, tool_name: str, output: str):
        """Capture and compress tool output."""
        compressed = self.compress_with_llm(output)
        self.db.execute(
            "INSERT INTO observations (tool, content, embedding) VALUES (?, ?, ?)",
            (tool_name, compressed, self.embed(compressed))
        )

    def search(self, query: str, limit: int = 5) -> list:
        """Hybrid search: FTS + vector similarity."""
        fts_results = self.db.execute(
            "SELECT * FROM observations WHERE content MATCH ?", (query,)
        ).fetchall()

        vector_results = self.vector_store.similarity_search(query, k=limit)

        return self.merge_and_rank(fts_results, vector_results)

    def get_context_for_session(self, max_tokens: int = 2000) -> str:
        """Progressive disclosure: return index first."""
        recent = self.db.execute(
            "SELECT tool, substr(content, 1, 100) FROM observations ORDER BY created DESC LIMIT 10"
        ).fetchall()
        return self.format_as_index(recent)
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Worker not running | `claude-mem start` or check PM2: `pm2 status` |
| No observations captured | Verify hooks: `/plugin status claude-mem` |
| Search returns nothing | Check retention: `claude-mem config get retention_days` |
| High latency | Disable Endless Mode or reduce observation frequency |
| Memory growing large | Run `claude-mem compact` to summarize old sessions |

## Configuration Reference

```bash
# View all settings
claude-mem config list

# Key settings
claude-mem config set auto_inject true          # Inject at session start
claude-mem config set capture_tool_outputs true # Capture tool results
claude-mem config set retention_days 30         # Keep for 30 days
claude-mem config set endless_mode false        # Disable beta feature
claude-mem config set max_inject_tokens 2000    # Limit injection size
```

## Project Status

- **Version**: 6.5.0
- **Stars**: 3.6k+
- **Maturity**: Stable (production-ready for core features)
- **Endless Mode**: Beta (experimental)
- **License**: MIT

## References

- **[API Reference](references/api-reference.md)** - HTTP endpoints and CLI commands
- **[Integration Patterns](references/integration-patterns.md)** - Framework-specific guides
- **[Troubleshooting](references/troubleshooting.md)** - Common issues and solutions

## Resources

- **GitHub**: https://github.com/thedotmack/claude-mem
- **Plugin Marketplace**: `thedotmack/claude-mem`
- **Web UI**: http://localhost:37777 (after installation)
