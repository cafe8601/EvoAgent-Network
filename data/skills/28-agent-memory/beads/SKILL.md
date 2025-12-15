---
name: beads-agent-memory
description: Git-backed issue tracker providing persistent memory for AI coding agents. Use when agents need to track long-horizon tasks across sessions, coordinate multi-agent workflows, or maintain context after compaction. Replaces markdown TODOs with structured dependency-aware task management.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Agent Memory, Issue Tracking, Task Management, Multi-Agent, Git, Long-Horizon Planning, Claude Code]
dependencies: [bd>=0.20.1]
---

# Beads - Memory Upgrade for AI Coding Agents

Git-backed issue tracker designed for AI coding agents to maintain persistent memory across sessions.

## When to Use Beads

**Use Beads when:**
- AI agents lose context between sessions (compaction resets)
- Tracking long-horizon tasks spanning multiple coding sessions
- Multi-agent coordination needs shared task visibility
- Replacing scattered markdown TODOs with structured tracking
- Need dependency-aware task prioritization (`bd ready`)

**Key features:**
- **Persistent memory**: Tasks survive session resets and compaction
- **Dependency graph**: 4 relationship types (blocks, related, parent-child, discovered-from)
- **Git-native**: JSONL stored in repo, no external server needed
- **Agent-optimized**: JSON output, CLI interface, MCP server available
- **Multi-agent sync**: Agent Mail enables <100ms coordination

**Use alternatives instead:**
- **LangGraph checkpoints**: For conversation state persistence (see `14-agents/langchain`)
- **Jira/Linear**: For human-centric project management
- **Simple TODOs**: For single-session, low-complexity tasks

## Quick Start

### Installation

```bash
# npm (recommended)
npm install -g @beads/bd

# macOS/Linux shell script
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash

# Homebrew
brew tap steveyegge/beads && brew install bd
```

**Requirements**: Linux needs glibc 2.32+ (Ubuntu 22.04+, Debian 11+). macOS/Windows work without restrictions.

### Initialize in Project

```bash
cd your-project
bd init              # Standard setup
bd init --quiet      # Non-interactive (for agents)
bd init --stealth    # Local-only, hidden from team
```

### Add to CLAUDE.md

```markdown
## Issue Tracking with Beads

This project uses `bd` (beads) for ALL task tracking.
Do NOT use markdown TODOs - use bd commands instead.

### Quick Reference
- `bd ready --json` - Find next task to work on
- `bd create "title" -d "description" -p 1 -t bug` - Create issue
- `bd update <id> --status in_progress` - Update status
- `bd close <id> --reason "completed"` - Close issue
- `bd dep add <new> <parent> --type discovered-from` - Link work
```

## Core Workflow

### 1. Finding Work (Agent Start)

```bash
# Get highest priority unblocked task
bd ready --json

# Output:
{
  "issues": [
    {
      "id": "bd-a1b2",
      "title": "Implement authentication",
      "priority": 0,
      "status": "open",
      "blockers": []
    }
  ]
}

# Pick and start work
bd update bd-a1b2 --status in_progress --json
```

### 2. Creating Issues

```bash
# Basic issue
bd create "Fix memory leak in training loop" --json

# With full metadata
bd create "Add unit tests for auth module" \
  -d "Cover login, logout, token refresh flows" \
  -p 1 \
  -t task \
  --label testing \
  --json

# Output: {"id": "bd-c3d4", "title": "Add unit tests..."}
```

### 3. Managing Dependencies

```bash
# Issue B blocks Issue A (A can't start until B is done)
bd dep add bd-a1b2 bd-c3d4

# Link discovered work to parent task
bd dep add bd-new bd-parent --type discovered-from

# View dependency tree
bd dep tree bd-a1b2

# Check for circular dependencies
bd dep cycles
```

**Dependency Types:**
| Type | Meaning | Use Case |
|------|---------|----------|
| `blocks` | Must complete first | Sequential tasks |
| `related` | Informational link | Cross-references |
| `parent-child` | Hierarchical | Epic → Stories |
| `discovered-from` | Found during work | Bug found while coding |

### 4. Closing Work

```bash
# Close with reason
bd close bd-a1b2 --reason "Implemented in commit abc123" --json

# Close multiple
bd close bd-a1b2 bd-c3d4 --reason "Batch completion"
```

### 5. Session End Protocol ("Landing the Plane")

```bash
# 1. Review in-progress work
bd list --status in_progress

# 2. Update or close completed items
bd close bd-a1b2 --reason "Completed"
bd update bd-c3d4 --status blocked --json

# 3. File any discovered work
bd create "TODO: Refactor auth module" -t task -p 2

# 4. Sync to git
bd sync

# 5. Verify clean state
bd list --status in_progress  # Should be empty or documented
```

## Multi-Agent Coordination

### Agent Mail (Real-time Sync)

Enable <100ms sync between multiple agents:

```bash
# Enable Agent Mail
bd config set agent_mail.enabled true

# Agent 1 creates issue
bd create "Task A" --json
# → Immediately visible to Agent 2

# Agent 2 checks for work
bd ready --json  # Sees Task A instantly
```

### Preventing Conflicts

Hash-based IDs (e.g., `bd-a1b2`) prevent merge conflicts:

```bash
# Agent 1 on branch feature-a
bd create "Feature A task" --json  # Gets bd-x1y2

# Agent 2 on branch feature-b
bd create "Feature B task" --json  # Gets bd-z3w4

# Both merge to main - no ID conflicts!
git checkout main
git merge feature-a feature-b  # Clean merge
```

## Integration Patterns

### With LangChain Agents

```python
from langchain.tools import tool
import subprocess
import json

@tool
def beads_ready() -> str:
    """Get the next highest-priority unblocked task."""
    result = subprocess.run(
        ["bd", "ready", "--json"],
        capture_output=True, text=True
    )
    return result.stdout

@tool
def beads_create(title: str, description: str = "", priority: int = 1) -> str:
    """Create a new issue in the task tracker."""
    cmd = ["bd", "create", title, "--json"]
    if description:
        cmd.extend(["-d", description])
    cmd.extend(["-p", str(priority)])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

@tool
def beads_close(issue_id: str, reason: str) -> str:
    """Close an issue with a reason."""
    result = subprocess.run(
        ["bd", "close", issue_id, "--reason", reason, "--json"],
        capture_output=True, text=True
    )
    return result.stdout

# Add to agent
agent = create_agent(
    model=llm,
    tools=[beads_ready, beads_create, beads_close],
    system_prompt="Use beads tools to track all work. Check bd ready at session start."
)
```

### With Multi-Agent Systems

```python
# Formation Analysis Agent (from 21-multiagent-learning-system)
class FormationAgent:
    def __init__(self):
        self.agent_id = "formation-analyzer"

    def on_task_complete(self, analysis_result):
        # File discovered issues
        if analysis_result.anomalies:
            subprocess.run([
                "bd", "create",
                f"Anomaly detected: {analysis_result.anomalies[0]}",
                "-t", "bug",
                "-p", "0",
                "--json"
            ])

    def get_next_task(self):
        result = subprocess.run(
            ["bd", "ready", "--json", "--assignee", self.agent_id],
            capture_output=True, text=True
        )
        tasks = json.loads(result.stdout)
        return tasks.get("issues", [])
```

### With Daytona Sandboxes

```python
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams
import subprocess

# Execute beads commands in sandbox
sandbox = daytona.create(CreateSandboxFromSnapshotParams(language="python"))

# Install beads in sandbox
sandbox.process.exec("npm install -g @beads/bd")
sandbox.process.exec("cd /workspace && bd init --quiet")

# Agent workflow in sandbox
result = sandbox.process.exec("bd ready --json")
tasks = json.loads(result.result)

# Work on task...

# Close when done
sandbox.process.exec(f"bd close {task_id} --reason 'Completed in sandbox'")
```

## Memory Compaction

Reduce context window usage by summarizing old issues:

```bash
# Analyze what can be compacted
bd compact --analyze --json

# Output:
{
  "compactable": 45,
  "total_issues": 120,
  "estimated_reduction": "35%"
}

# Run compaction (summarizes closed issues older than 30 days)
bd compact --execute

# Custom threshold
bd compact --older-than 14d --execute
```

## Common Commands Reference

| Command | Purpose | Agent Use |
|---------|---------|-----------|
| `bd ready --json` | Find unblocked work | Session start |
| `bd create "title" --json` | Create issue | Discovered work |
| `bd update <id> --status X` | Update status | Progress tracking |
| `bd close <id> --reason "X"` | Complete issue | Task done |
| `bd dep add <a> <b>` | Add dependency | Link work |
| `bd list --status open` | List issues | Overview |
| `bd show <id>` | Issue details | Deep dive |
| `bd sync` | Force git sync | Session end |
| `bd doctor` | Health check | Troubleshooting |

## Best Practices

1. **Always use `--json`** for programmatic access
2. **Link discovered work** with `--type discovered-from`
3. **Check `bd ready`** at session start, not `bd list`
4. **Run `bd sync`** before session end
5. **Use priorities** (0=critical, 1=high, 2=normal, 3=low)
6. **File issues proactively** - don't rely on memory

## Common Issues

| Issue | Solution |
|-------|----------|
| `bd: command not found` | Run installation command, check PATH |
| Sync conflicts | `bd doctor` then `bd sync --force` |
| glibc errors (Linux) | Upgrade to Ubuntu 22.04+ or build from source |
| Stale daemon | `bd daemons killall` then retry |

## Project Status

- **Maturity**: Alpha (API may change before v1.0)
- **Stars**: 4,400+ ⭐
- **License**: MIT
- **Author**: Steve Yegge

## References

- **[API Reference](references/api-reference.md)** - Complete command documentation
- **[Workflows](references/workflows.md)** - Agent integration patterns
- **[Troubleshooting](references/troubleshooting.md)** - Common issues and solutions

## Resources

- **GitHub**: https://github.com/steveyegge/beads
- **Medium**: https://steve-yegge.medium.com/introducing-beads-a-coding-agent-memory-system-637d7d92514a
- **MCP Server**: `integrations/beads-mcp/` in repo
- **VS Code Extension**: vscode-beads
