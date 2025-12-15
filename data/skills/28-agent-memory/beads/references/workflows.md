# Beads Agent Workflows

Practical workflow patterns for AI coding agents using Beads.

## Session Lifecycle Workflow

### Session Start Protocol

```bash
#!/bin/bash
# Agent session initialization

# 1. Sync from remote
git pull
bd sync --pull-only

# 2. Check for assigned work
bd ready --assignee "$AGENT_ID" --json

# 3. If no assigned work, get highest priority
bd ready --sort priority --limit 3 --json

# 4. Pick task and mark in progress
bd update "$TASK_ID" --status in_progress --assignee "$AGENT_ID" --json
```

**Agent prompt addition:**
```markdown
At session start:
1. Run `bd sync` to get latest issues
2. Run `bd ready --json` to find work
3. Pick highest priority unblocked task
4. Run `bd update <id> --status in_progress` before starting
```

### During Work Protocol

```bash
# When discovering new work
bd create "Found: memory leak in auth module" \
  -t bug \
  -p 1 \
  --json

# Link to current task
bd dep add "$NEW_ISSUE" "$CURRENT_TASK" --type discovered-from

# When blocked
bd update "$CURRENT_TASK" --status blocked --json
bd dep add "$CURRENT_TASK" "$BLOCKER_ID"

# Progress notes (update description)
bd update "$CURRENT_TASK" \
  -d "Progress: Completed auth flow, working on tests" \
  --json
```

### Session End Protocol ("Landing the Plane")

```bash
#!/bin/bash
# Agent session cleanup

# 1. List in-progress work
IN_PROGRESS=$(bd list --status in_progress --json)

# 2. For each in-progress item:
#    - Close if complete
#    - Update status if not
#    - Add notes about current state

# 3. File any remaining discovered work
# (Don't leave TODOs in code!)

# 4. Sync to git
bd sync
git add .beads/
git commit -m "beads: session checkpoint"
git push

# 5. Verify clean state
bd list --status in_progress --json
# Should return empty or documented items
```

**CLAUDE.md addition:**
```markdown
## Session End ("Land the Plane")

When ending session or context is getting full:
1. `bd list --status in_progress` - review open work
2. Close completed: `bd close <id> --reason "Done"`
3. Update incomplete: `bd update <id> -d "Stopped at: X"`
4. File discovered work: `bd create "TODO: Y" -t task`
5. `bd sync` - commit to git
6. Verify: `bd list --status in_progress` should be minimal
```

## Multi-Agent Coordination

### Agent Role Assignment

```yaml
# Example: 3-agent system
agents:
  analyzer:
    id: "agent-analyzer"
    types: [bug, investigation]
    priorities: [0, 1]

  implementer:
    id: "agent-implementer"
    types: [feature, task]
    priorities: [1, 2]

  tester:
    id: "agent-tester"
    types: [test, qa]
    priorities: [2, 3]
```

**Each agent queries their work:**
```bash
# Analyzer agent
bd ready --type bug --type investigation --assignee agent-analyzer --json

# Implementer agent
bd ready --type feature --type task --assignee agent-implementer --json

# Tester agent
bd ready --type test --type qa --assignee agent-tester --json
```

### Handoff Between Agents

```bash
# Implementer completes feature
bd close bd-feat1 --reason "Implementation complete"

# Create test task for tester
bd create "Test: OAuth integration" \
  -t test \
  -a agent-tester \
  --blocked-by bd-feat1 \
  --json

# Tester picks up automatically via bd ready
```

### Agent Mail Real-time Sync

```bash
# Enable Agent Mail for instant sync
bd config set agent_mail.enabled true
bd config set agent_mail.poll_interval_ms 100

# Agent 1 creates urgent issue
bd create "CRITICAL: Production down" -p 0 --json

# Agent 2 sees it immediately (< 100ms)
bd ready --priority 0 --json
```

## Dependency-Driven Development

### Epic Breakdown Pattern

```bash
# 1. Create epic
bd create "User Authentication System" -t epic -p 1 --json
# Returns: bd-auth

# 2. Create child tasks
bd create "Design auth flow" --parent bd-auth --json       # bd-auth.1
bd create "Implement login" --parent bd-auth --json        # bd-auth.2
bd create "Implement logout" --parent bd-auth --json       # bd-auth.3
bd create "Add OAuth" --parent bd-auth --json              # bd-auth.4
bd create "Write tests" --parent bd-auth --json            # bd-auth.5

# 3. Set dependencies
bd dep add bd-auth.2 bd-auth.1  # login blocked by design
bd dep add bd-auth.3 bd-auth.1  # logout blocked by design
bd dep add bd-auth.4 bd-auth.2  # OAuth blocked by login
bd dep add bd-auth.5 bd-auth.4  # tests blocked by OAuth

# 4. Query ready work
bd ready --json
# Only bd-auth.1 (Design) is ready - others are blocked
```

### Discovered Work Pattern

```bash
# Working on feature
bd update bd-feat1 --status in_progress

# Find a bug while coding
bd create "Bug: null pointer in user validation" \
  -t bug \
  -p 0 \
  --json
# Returns: bd-bug1

# Link to parent work
bd dep add bd-bug1 bd-feat1 --type discovered-from

# Decide: fix now or later?
# Option A: Fix now (blocks feature)
bd dep add bd-feat1 bd-bug1  # Feature blocked by bug

# Option B: Fix later (independent)
# No additional dependency needed
```

### Blocking Chain Resolution

```bash
# View what's blocking your work
bd dep tree bd-target --direction up --json

# Output shows chain:
# bd-target
#   └── blocked by: bd-step3
#       └── blocked by: bd-step2
#           └── blocked by: bd-step1 (ready!)

# Work on bd-step1 first
bd update bd-step1 --status in_progress
```

## Integration Workflows

### LangChain Agent Integration

```python
import subprocess
import json
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor

@tool
def bd_ready(sort: str = "hybrid", limit: int = 5) -> str:
    """Find ready (unblocked) work. Returns highest priority tasks."""
    result = subprocess.run(
        ["bd", "ready", "--sort", sort, "--limit", str(limit), "--json"],
        capture_output=True, text=True
    )
    return result.stdout

@tool
def bd_create(title: str, description: str = "", priority: int = 2,
              issue_type: str = "task") -> str:
    """Create a new issue. Priority: 0=critical, 1=high, 2=normal, 3=low."""
    cmd = ["bd", "create", title, "-p", str(priority), "-t", issue_type, "--json"]
    if description:
        cmd.extend(["-d", description])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

@tool
def bd_update(issue_id: str, status: str = None, description: str = None) -> str:
    """Update an issue. Status: open, in_progress, blocked, closed."""
    cmd = ["bd", "update", issue_id, "--json"]
    if status:
        cmd.extend(["--status", status])
    if description:
        cmd.extend(["-d", description])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

@tool
def bd_close(issue_id: str, reason: str) -> str:
    """Close an issue with a reason."""
    result = subprocess.run(
        ["bd", "close", issue_id, "--reason", reason, "--json"],
        capture_output=True, text=True
    )
    return result.stdout

@tool
def bd_dep_add(issue_id: str, blocker_id: str, dep_type: str = "blocks") -> str:
    """Add dependency. Types: blocks, related, parent-child, discovered-from."""
    result = subprocess.run(
        ["bd", "dep", "add", issue_id, blocker_id, "--type", dep_type, "--json"],
        capture_output=True, text=True
    )
    return result.stdout

# Create agent with tools
tools = [bd_ready, bd_create, bd_update, bd_close, bd_dep_add]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Agent workflow
result = executor.invoke({
    "input": "Check for work, pick the highest priority task, and start working on it"
})
```

### Python Wrapper Class

```python
import subprocess
import json
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BeadsIssue:
    id: str
    title: str
    status: str
    priority: int
    type: str
    description: Optional[str] = None
    labels: List[str] = None
    blockers: List[str] = None

class BeadsClient:
    """Python wrapper for Beads CLI."""

    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id

    def _run(self, args: List[str]) -> dict:
        """Run bd command and return JSON output."""
        cmd = ["bd"] + args + ["--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"bd error: {result.stderr}")
        return json.loads(result.stdout) if result.stdout else {}

    def ready(self, limit: int = 5, sort: str = "hybrid") -> List[BeadsIssue]:
        """Get ready (unblocked) work."""
        args = ["ready", "--limit", str(limit), "--sort", sort]
        if self.agent_id:
            args.extend(["--assignee", self.agent_id])
        data = self._run(args)
        return [BeadsIssue(**issue) for issue in data.get("issues", [])]

    def create(self, title: str, description: str = None,
               priority: int = 2, issue_type: str = "task",
               labels: List[str] = None) -> BeadsIssue:
        """Create a new issue."""
        args = ["create", title, "-p", str(priority), "-t", issue_type]
        if description:
            args.extend(["-d", description])
        if labels:
            for label in labels:
                args.extend(["-l", label])
        if self.agent_id:
            args.extend(["-a", self.agent_id])
        data = self._run(args)
        return BeadsIssue(**data)

    def update(self, issue_id: str, status: str = None,
               description: str = None, priority: int = None) -> BeadsIssue:
        """Update an issue."""
        args = ["update", issue_id]
        if status:
            args.extend(["--status", status])
        if description:
            args.extend(["-d", description])
        if priority is not None:
            args.extend(["-p", str(priority)])
        data = self._run(args)
        return BeadsIssue(**data)

    def close(self, issue_id: str, reason: str) -> BeadsIssue:
        """Close an issue."""
        data = self._run(["close", issue_id, "--reason", reason])
        return BeadsIssue(**data)

    def add_dependency(self, issue_id: str, blocker_id: str,
                       dep_type: str = "blocks") -> None:
        """Add a dependency between issues."""
        self._run(["dep", "add", issue_id, blocker_id, "--type", dep_type])

    def sync(self) -> None:
        """Sync with git."""
        self._run(["sync"])

    def list_issues(self, status: str = None, priority: int = None,
                    issue_type: str = None) -> List[BeadsIssue]:
        """List issues with filters."""
        args = ["list"]
        if status:
            args.extend(["--status", status])
        if priority is not None:
            args.extend(["--priority", str(priority)])
        if issue_type:
            args.extend(["--type", issue_type])
        data = self._run(args)
        return [BeadsIssue(**issue) for issue in data.get("issues", [])]

# Usage
client = BeadsClient(agent_id="my-agent")

# Session start
tasks = client.ready()
if tasks:
    current = tasks[0]
    client.update(current.id, status="in_progress")

# During work
bug = client.create(
    "Found: memory leak",
    description="In auth module line 45",
    priority=1,
    issue_type="bug"
)
client.add_dependency(bug.id, current.id, dep_type="discovered-from")

# Session end
client.close(current.id, reason="Completed implementation")
client.sync()
```

### MCP Server Integration

Beads includes an MCP server (`beads-mcp`) for direct Claude integration:

```bash
# Install MCP server
cd /path/to/beads/integrations/beads-mcp
pip install -e .

# Configure in Claude Desktop
# Add to claude_desktop_config.json:
{
  "mcpServers": {
    "beads": {
      "command": "python",
      "args": ["-m", "beads_mcp"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

**Available MCP tools:**
- `beads_ready` - Find ready work
- `beads_create` - Create issue
- `beads_update` - Update issue
- `beads_close` - Close issue
- `beads_list` - List issues
- `beads_dep_add` - Add dependency

## Research Workflow

### Hypothesis Tracking

```bash
# Create research hypothesis
bd create "Hypothesis: LoRA rank 16 outperforms rank 8 on small datasets" \
  -t epic \
  -p 1 \
  -l hypothesis \
  --json
# Returns: bd-hyp1

# Create experiment tasks
bd create "Experiment: Train with rank 8" --parent bd-hyp1 --json
bd create "Experiment: Train with rank 16" --parent bd-hyp1 --json
bd create "Analysis: Compare results" --parent bd-hyp1 --json

# Set dependencies
bd dep add bd-hyp1.3 bd-hyp1.1  # Analysis blocked by rank-8
bd dep add bd-hyp1.3 bd-hyp1.2  # Analysis blocked by rank-16
```

### Experiment Session

```bash
# Start experiment
bd update bd-hyp1.1 --status in_progress

# Log findings during experiment
bd update bd-hyp1.1 \
  -d "Results: Loss 0.23, Accuracy 87.5%, Training time 2h"

# Complete experiment
bd close bd-hyp1.1 --reason "Completed. Results logged in description."

# Check what's unblocked
bd ready --json
# Now bd-hyp1.2 or bd-hyp1.3 might be ready
```

### Literature Review Tracking

```bash
# Track papers to read
bd create "Review: Attention Is All You Need" -t task -l literature --json
bd create "Review: BERT paper" -t task -l literature --json
bd create "Review: GPT-3 paper" -t task -l literature --json

# Set reading order dependencies
bd dep add bd-bert bd-attention  # BERT builds on Attention
bd dep add bd-gpt3 bd-bert       # GPT-3 builds on BERT

# Query unread papers
bd list --status open --label literature --json
```

## CI/CD Integration

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Export beads to JSONL before commit
bd sync --push-only

# Check for in-progress items that should be updated
IN_PROGRESS=$(bd list --status in_progress --json | jq '.issues | length')
if [ "$IN_PROGRESS" -gt 5 ]; then
    echo "Warning: $IN_PROGRESS issues still in progress"
    echo "Consider updating or closing some before commit"
fi
```

### GitHub Actions Integration

```yaml
# .github/workflows/beads-sync.yml
name: Beads Sync

on:
  push:
    paths:
      - '.beads/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Beads
        run: npm install -g @beads/bd

      - name: Validate Beads DB
        run: bd doctor --json

      - name: Check for cycles
        run: |
          CYCLES=$(bd dep cycles --json | jq '.cycles | length')
          if [ "$CYCLES" -gt 0 ]; then
            echo "Error: Circular dependencies detected"
            bd dep cycles
            exit 1
          fi
```

## Best Practices Checklist

### Session Start
- [ ] `git pull` to get latest
- [ ] `bd sync` to import changes
- [ ] `bd ready --json` to find work
- [ ] `bd update <id> --status in_progress` before starting

### During Work
- [ ] File discovered work immediately with `bd create`
- [ ] Link discoveries with `--type discovered-from`
- [ ] Update status when blocked
- [ ] Use priorities consistently (0=critical → 3=low)

### Session End
- [ ] Review: `bd list --status in_progress`
- [ ] Close completed work with reasons
- [ ] Update incomplete work with notes
- [ ] `bd sync` to export
- [ ] `git commit` and `git push`
- [ ] Verify: minimal in-progress items
