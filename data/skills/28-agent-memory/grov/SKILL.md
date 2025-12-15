---
name: grov-reasoning-memory
description: Proxy-based reasoning memory for Claude Code that captures WHY decisions were made and enables team synchronization. Use when teams need shared learning, AI drift prevention is critical, or reasoning traces matter more than detailed logs. Early stage (v0.5.x).
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Agent Memory, Reasoning Memory, Team Sync, Anti-Drift, Claude Code, Proxy Server]
dependencies: [node>=18.0.0, anthropic-api-key-optional]
---

# Grov - Reasoning Memory for Claude Code

Proxy server that captures reasoning from Claude Code sessions and injects it into future sessions. Focus on WHY, not just WHAT.

## When to Use Grov

**Use Grov when:**
- Teams need shared AI learning across members
- Preventing AI drift from task objectives is critical
- Reasoning/architectural decisions matter more than detailed logs
- Want to skip redundant codebase exploration in future sessions
- Need cost savings via extended cache (keep-alive)

**Key features:**
- **Reasoning capture**: Stores WHY decisions were made, not just actions
- **Team sync**: Cloud dashboard for sharing learnings across team
- **Anti-drift detection**: Claude Haiku monitors if AI strays from objectives
- **Extended cache**: Keep Anthropic's prompt cache alive (~$0.002/request)
- **File-path matching**: Injects context relevant to files being worked on

**Metrics:**
- **Time saved**: 10+ minutes per session (skip exploration)
- **Token reduction**: ~7% less exploration overhead
- **Cache savings**: Extended from 5min to indefinite

**Use alternatives instead:**
- **claude-mem**: For detailed observation logs and search (see `28-agent-memory/claude-mem`)
- **Beads**: For task/issue tracking (see `28-agent-memory/beads`)
- **MCP Memory Server**: For simple key-value storage

**Project Status:** Early Stage (v0.5.2, 93 stars)

## Quick Start

### Installation

```bash
npm install -g grov
```

**Requirements**: Node.js 18+, Claude Code

### Initialize

```bash
# One-time setup (configures ANTHROPIC_BASE_URL)
grov init
```

This modifies your Claude Code config to route API calls through Grov proxy.

### Start Proxy

```bash
# Start the proxy server (required for memory)
grov proxy

# In another terminal, use Claude Code normally
claude
```

### Verify

```bash
# Check status
grov status

# View captured memories
grov tasks
```

## Core Architecture

### How Grov Works

```
┌─────────────────────────────────────────────────────────────┐
│  Claude Code                                                 │
│  (ANTHROPIC_BASE_URL=http://127.0.0.1:8080)                │
└─────────────────────────────────────────────────────────────┘
                              ↓ API calls
┌─────────────────────────────────────────────────────────────┐
│  Grov Proxy (port 8080)                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Intent      │  │ Reasoning   │  │ Anti-Drift  │        │
│  │ Extraction  │  │ Capture     │  │ Detection   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Anthropic API                                               │
└─────────────────────────────────────────────────────────────┘
```

### Memory Flow

```
Session 1: Claude learns about your auth system
           ↓
grov captures: "Auth tokens refresh in middleware/token.ts:45,
               using 15-min window to handle long forms"
           ↓
Session 2: User asks about related feature
           ↓
grov injects: Previous context about auth
           ↓
Claude skips exploration, reads files directly
```

### What Grov Captures

| Category | Examples |
|----------|----------|
| **Reasoning** | "Extended token refresh because users were getting logged out during long forms" |
| **File Paths** | `session.ts`, `token.ts`, `middleware/*.ts` |
| **Decisions** | "Changed from 5min to 15min window" |
| **Task Status** | Completed, in-progress, blocked |

### What Grov Injects

```
VERIFIED CONTEXT FROM PREVIOUS SESSIONS:

[Task: Fix auth logout bug]
- Files: session.ts, token.ts
- Extended token refresh window from 5min to 15min
- Reason: Users were getting logged out during long forms

YOU MAY SKIP EXPLORE AGENTS for files mentioned above.
```

## Anti-Drift Detection

Grov monitors Claude's actual actions (not user prompts) to detect drift:

### How It Works

```python
# Grov uses Claude Haiku to score alignment (1-10)
alignment_score = haiku.evaluate(
    user_intent=initial_prompt,
    claude_actions=recent_tool_calls
)

if alignment_score < 5:
    # Intervention levels: nudge → correct → intervene → halt
    inject_correction(level="nudge")
```

### Intervention Levels

| Level | Score | Action |
|-------|-------|--------|
| Normal | 8-10 | No intervention |
| Nudge | 5-7 | Gentle reminder in next prompt |
| Correct | 3-4 | Explicit redirection |
| Intervene | 1-2 | Strong course correction |
| Halt | 0 | Stop and wait for user |

### Configuration

```bash
# Enable/disable drift detection (requires Anthropic API key)
grov config set drift_detection true

# Set intervention threshold
grov config set drift_threshold 5
```

## Team Synchronization

### Cloud Dashboard

```bash
# Login with GitHub
grov login

# Sync memories to team
grov sync

# View team dashboard
open https://app.grov.dev
```

### Dashboard Features

| Feature | Description |
|---------|-------------|
| Browse reasoning | Search all team members' captured insights |
| Semantic search | Find relevant context by meaning |
| Track learnings | See who learned what, when |
| Auto-sync | Memories shared when sessions complete |

### Privacy Controls

```bash
# Local-only mode (no cloud sync)
grov config set cloud_sync false

# Exclude sensitive paths
grov config set exclude_paths "secrets/,*.env"
```

## Extended Cache

Keep Anthropic's prompt cache alive longer than the default 5 minutes:

```bash
# Enable extended cache (experimental)
grov config set extended_cache true

# Cost: ~$0.002 per keep-alive request (every 4 minutes)
```

### How It Works

1. Grov sends small keep-alive requests during idle periods
2. Anthropic's cache remains warm
3. Next real request gets cache benefits

### When to Use

- Long coding sessions with breaks
- Expensive system prompts that benefit from caching
- Team members working on same codebase

## Integration Patterns

### With claude-mem (Hybrid Setup)

Use Grov for team context, claude-mem for detailed search:

```bash
# Grov: Team reasoning injection (enabled)
grov proxy

# claude-mem: Disable auto-inject, search only
claude-mem config set auto_inject false
```

**Result:**
- Session starts with team reasoning from Grov
- Detailed history searchable via claude-mem's mem-search

### General Agent Reasoning Pattern

Apply Grov's reasoning capture to any agent:

```python
class ReasoningMemory:
    """Grov-style reasoning capture for general agents."""

    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS reasoning (
                id TEXT PRIMARY KEY,
                task TEXT,
                files TEXT,  -- JSON array
                reasoning TEXT,
                decision TEXT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def capture(self, task: str, files: list, reasoning: str, decision: str):
        """Capture reasoning trace."""
        self.db.execute("""
            INSERT INTO reasoning (id, task, files, reasoning, decision)
            VALUES (?, ?, ?, ?, ?)
        """, (
            self._generate_id(),
            task,
            json.dumps(files),
            reasoning,
            decision
        ))
        self.db.commit()

    def get_context_for_files(self, file_paths: list) -> str:
        """Get relevant reasoning for files being touched."""
        context_parts = []

        for path in file_paths:
            rows = self.db.execute("""
                SELECT task, reasoning, decision
                FROM reasoning
                WHERE files LIKE ?
                ORDER BY created DESC
                LIMIT 3
            """, (f'%{path}%',)).fetchall()

            for task, reasoning, decision in rows:
                context_parts.append(
                    f"[{task}]\n- Reasoning: {reasoning}\n- Decision: {decision}"
                )

        return "\n\n".join(context_parts)
```

### Anti-Drift Pattern

```python
from anthropic import Anthropic

class DriftDetector:
    """Grov-style drift detection for agents."""

    def __init__(self):
        self.client = Anthropic()
        self.initial_intent = None

    def set_intent(self, user_prompt: str):
        """Store initial user intent."""
        self.initial_intent = user_prompt

    def check_alignment(self, recent_actions: list) -> dict:
        """Check if agent is aligned with intent."""
        prompt = f"""Score alignment (1-10) between user intent and agent actions.

User Intent: {self.initial_intent}

Recent Actions:
{json.dumps(recent_actions, indent=2)}

Respond with JSON:
{{"score": <1-10>, "assessment": "<brief explanation>", "suggestion": "<if score < 7>"}}"""

        response = self.client.messages.create(
            model="claude-haiku-3",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)

    def get_intervention(self, score: int) -> str:
        """Get intervention message based on score."""
        if score >= 8:
            return None
        elif score >= 5:
            return "Reminder: Focus on the original task."
        elif score >= 3:
            return "You appear to be drifting. Return to: " + self.initial_intent
        else:
            return "STOP. You have significantly drifted. Original task: " + self.initial_intent
```

## CLI Reference

```bash
# Core commands
grov init              # One-time setup
grov proxy             # Start proxy server (required)
grov status            # Show system status
grov tasks             # Show captured tasks

# Cloud commands
grov login             # GitHub authentication
grov sync              # Sync to team dashboard
grov logout            # Disconnect from cloud

# Configuration
grov config set <key> <value>
grov config get <key>
grov config list

# Available config keys:
# - drift_detection: bool
# - drift_threshold: int (1-10)
# - extended_cache: bool
# - cloud_sync: bool
# - exclude_paths: string (comma-separated)

# Maintenance
grov disable           # Disable grov (restore direct API)
grov enable            # Re-enable grov
grov clear             # Clear local memory
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Proxy not intercepting | Check `ANTHROPIC_BASE_URL` in Claude config |
| No reasoning captured | Ensure `grov proxy` is running |
| Drift detection disabled | Set `ANTHROPIC_API_KEY` for Haiku access |
| Cloud sync failing | Run `grov login` and re-authenticate |
| Cache not extending | Enable: `grov config set extended_cache true` |

## Limitations (v0.5.x)

| Feature | Status |
|---------|--------|
| Reasoning capture | ✅ Working |
| Team sync | ✅ Working |
| Anti-drift | ✅ Working (needs API key) |
| Extended cache | ⚠️ Experimental |
| Semantic search | ❌ Roadmap |
| VS Code extension | ❌ Roadmap |

## Project Status

- **Version**: 0.5.2
- **Stars**: 93
- **Maturity**: Early Stage (core features working, some roadmap items pending)
- **License**: Apache 2.0

## References

- **[API Reference](references/api-reference.md)** - CLI and config documentation
- **[Integration Patterns](references/integration-patterns.md)** - Framework-specific guides

## Resources

- **GitHub**: https://github.com/TonyStef/Grov
- **Cloud Dashboard**: https://app.grov.dev
- **Hacker News**: https://news.ycombinator.com/item?id=46126066
