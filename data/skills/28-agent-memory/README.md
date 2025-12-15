# 28-agent-memory - Agent Memory Systems

Tools for giving AI agents persistent memory across sessions.

## Overview

This category contains three complementary memory systems for AI agents:

| Tool | Memory Type | Focus | Maturity |
|------|-------------|-------|----------|
| **[beads](beads/)** | Task Memory | What to do next | Stable (4.4k stars) |
| **[claude-mem](claude-mem/)** | Observation Memory | What was done | Stable (3.6k stars) |
| **[grov](grov/)** | Reasoning Memory | Why it was done | Early (93 stars) |

## Quick Selection Guide

```
┌─────────────────────────────────────────────────────────────┐
│  What problem are you solving?                               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ "Track tasks  │     │ "Search past  │     │ "Share team   │
│  and deps"    │     │  work history"│     │  learnings"   │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
     beads              claude-mem               grov
```

## Comparison Matrix

| Feature | beads | claude-mem | grov |
|---------|-------|------------|------|
| **Primary Use** | Task tracking | Session history | Reasoning capture |
| **Storage** | Git (JSONL) | SQLite + Vector | SQLite |
| **Team Sync** | Git-based | Local only | Cloud dashboard |
| **Search** | Dependency graph | Semantic + FTS | File-path match |
| **Auto-capture** | Manual | Automatic hooks | Automatic proxy |
| **Anti-drift** | No | No | Yes |
| **Token savings** | N/A | ~2,250/session | ~7% reduction |

## Use Case Scenarios

### Solo Developer: Need Session Continuity

**Best choice: claude-mem**

```bash
# Install
/plugin install claude-mem

# Works automatically - no config needed
# Search past work anytime
```

### Team Project: Share Architectural Decisions

**Best choice: grov**

```bash
# Install
npm install -g grov
grov init
grov proxy

# Login for team sync
grov login
```

### Complex Project: Track Dependencies

**Best choice: beads**

```bash
# Install
npm install -g @beads/bd
bd init

# Create tasks with dependencies
bd create "Implement auth" --json
bd dep add bd-new bd-parent
```

### Hybrid: Team + Detailed History

**Best choice: grov + claude-mem**

```bash
# Grov for team reasoning (session start injection)
grov proxy

# claude-mem for search only (disable auto-inject)
claude-mem config set auto_inject false

# Result:
# - Team context injected at start
# - Detailed search available on-demand
```

## Memory Architecture Comparison

### Layer Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Memory Layers                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 4: Task Planning (beads)                             │
│  └── "What should I do next?"                               │
│  └── Dependencies, priorities, blockers                      │
│                                                              │
│  Layer 3: Reasoning (grov)                                  │
│  └── "Why did we make this decision?"                       │
│  └── Architectural choices, trade-offs                       │
│                                                              │
│  Layer 2: Observations (claude-mem)                         │
│  └── "What happened in past sessions?"                      │
│  └── Tool outputs, file changes, session logs               │
│                                                              │
│  Layer 1: Working Memory (Claude's context window)          │
│  └── Current conversation                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Session N-1                    Session N
─────────────────────────────────────────────────────────

beads: Task created    ───────► Task available via `bd ready`
                                  │
grov:  Reasoning       ───────► Context injected at start
       captured                   │
                                  │
claude-mem: Session    ───────► Searchable via mem-search
            summarized            │
                                  ▼
                            Claude works with
                            full context
```

## General Agent Memory Patterns

These tools demonstrate patterns applicable to any AI agent:

### 1. Progressive Disclosure (claude-mem)

```python
# Don't inject all memory at once
# Layer 1: Index (100 tokens) → Layer 2: Summary (500) → Layer 3: Full

def get_context(max_tokens: int) -> str:
    if max_tokens < 500:
        return get_index_only()
    elif max_tokens < 2000:
        return get_summaries()
    else:
        return get_full_context()
```

### 2. Reasoning Extraction (grov)

```python
# Store WHY, not just WHAT
def capture_reasoning(task: str, response: str) -> dict:
    return {
        "task": task,
        "reasoning": extract_why(response),  # Why this approach?
        "decision": extract_what(response),   # What was decided?
        "files": extract_files(response)      # What files touched?
    }
```

### 3. Anti-Drift Detection (grov)

```python
# Monitor agent alignment with original intent
def check_drift(intent: str, recent_actions: list) -> int:
    score = evaluate_alignment(intent, recent_actions)
    if score < threshold:
        inject_correction()
    return score
```

### 4. Task Dependencies (beads)

```python
# Track blocking relationships
def get_next_task() -> Task:
    # Returns highest priority UNBLOCKED task
    return db.query("""
        SELECT * FROM tasks
        WHERE status = 'open'
        AND NOT EXISTS (SELECT 1 FROM deps WHERE blocked_id = tasks.id)
        ORDER BY priority
        LIMIT 1
    """)
```

## Integration Examples

### All Three Together

```bash
# Start Grov proxy for reasoning
grov proxy &

# Configure claude-mem for search-only
claude-mem config set auto_inject false

# Initialize Beads for task tracking
bd init

# Workflow:
# 1. Check next task: bd ready --json
# 2. Grov injects relevant reasoning at session start
# 3. Work on task, claude-mem captures observations
# 4. Search past work: "What did I change in auth?"
# 5. Close task: bd close <id> --reason "Done"
```

### With LangChain

```python
from langchain.tools import tool

@tool
def search_memory(query: str) -> str:
    """Search past work (claude-mem)."""
    return requests.get(f"http://localhost:37777/search?q={query}").json()

@tool
def get_reasoning(files: list) -> str:
    """Get reasoning context (grov)."""
    return requests.get(f"http://localhost:8080/grov/context?files={','.join(files)}").json()

@tool
def get_next_task() -> str:
    """Get next unblocked task (beads)."""
    return subprocess.run(["bd", "ready", "--json"], capture_output=True).stdout
```

## Choosing the Right Tool

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Solo, need history search | claude-mem | Best search, auto-capture |
| Team, share learnings | grov | Cloud sync, team dashboard |
| Complex project, many tasks | beads | Dependency tracking |
| Prevent AI going off-track | grov | Anti-drift detection |
| Token efficiency critical | claude-mem | Progressive disclosure |
| Git-native workflow | beads | JSONL in repo |
| Hybrid team + search | grov + claude-mem | Best of both |

## Resources

- **beads**: https://github.com/steveyegge/beads (4.4k stars)
- **claude-mem**: https://github.com/thedotmack/claude-mem (3.6k stars)
- **grov**: https://github.com/TonyStef/Grov (93 stars)
