# Beads CLI API Reference

Complete command reference for the `bd` CLI tool (v0.20.1+).

## Global Flags

All commands support these flags:

| Flag | Description |
|------|-------------|
| `--json` | Output in JSON format (recommended for agents) |
| `--quiet`, `-q` | Suppress non-essential output |
| `--help`, `-h` | Show help for command |
| `--version` | Show bd version |

## Initialization Commands

### bd init

Initialize Beads in a project.

```bash
bd init [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--quiet` | Non-interactive mode (for agents) |
| `--stealth` | Local-only, add to global gitignore |
| `--branch <name>` | Use separate branch for metadata |
| `--contributor` | Contributor mode (read-only sync) |
| `--team` | Team mode with shared settings |

**Examples:**
```bash
bd init                           # Interactive setup
bd init --quiet                   # Agent-friendly
bd init --stealth                 # Personal use, hidden from team
bd init --branch beads-metadata   # Protected branch workflow
```

### bd onboard

Get integration instructions for agents.

```bash
bd onboard [--json]
```

Returns setup instructions including AGENTS.md content to add.

## Issue Management

### bd create

Create a new issue.

```bash
bd create <title> [flags]
```

**Flags:**
| Flag | Short | Description |
|------|-------|-------------|
| `--description` | `-d` | Issue description |
| `--priority` | `-p` | Priority (0=critical, 1=high, 2=normal, 3=low) |
| `--type` | `-t` | Type: bug, task, feature, epic |
| `--label` | `-l` | Add label (repeatable) |
| `--assignee` | `-a` | Assign to user/agent |
| `--parent` | | Parent issue ID |
| `--blocks` | | Issue this blocks |
| `--blocked-by` | | Issue blocking this |

**Examples:**
```bash
# Simple issue
bd create "Fix login bug" --json

# Full metadata
bd create "Implement OAuth" \
  -d "Support Google and GitHub OAuth providers" \
  -p 1 \
  -t feature \
  -l backend \
  -l auth \
  --json

# With dependency
bd create "Add OAuth tests" \
  --blocked-by bd-a1b2 \
  --json

# Child issue
bd create "OAuth error handling" \
  --parent bd-a1b2 \
  --json
```

**Output (JSON):**
```json
{
  "id": "bd-c3d4",
  "title": "Fix login bug",
  "status": "open",
  "priority": 2,
  "type": "task",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### bd list

List issues with filtering.

```bash
bd list [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--status` | Filter by status: open, in_progress, blocked, closed |
| `--priority` | Filter by priority (0-3) |
| `--type` | Filter by type |
| `--label` | Filter by label |
| `--assignee` | Filter by assignee |
| `--created-after` | Issues created after date |
| `--created-before` | Issues created before date |
| `--limit` | Max results (default: 50) |
| `--sort` | Sort by: priority, created, updated |

**Examples:**
```bash
# All open issues
bd list --status open --json

# High priority bugs
bd list --status open --priority 0 --type bug --json

# Recent issues
bd list --created-after 2025-01-01 --sort created --json
```

### bd show

Show issue details.

```bash
bd show <issue-id> [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--include-history` | Include change history |
| `--include-deps` | Include dependency details |

**Example:**
```bash
bd show bd-a1b2 --include-deps --json
```

**Output:**
```json
{
  "id": "bd-a1b2",
  "title": "Implement OAuth",
  "description": "Support Google and GitHub OAuth providers",
  "status": "in_progress",
  "priority": 1,
  "type": "feature",
  "labels": ["backend", "auth"],
  "assignee": "agent-1",
  "created_at": "2025-01-10T09:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z",
  "dependencies": {
    "blocks": ["bd-c3d4"],
    "blocked_by": [],
    "related": ["bd-e5f6"],
    "children": ["bd-a1b2.1", "bd-a1b2.2"]
  }
}
```

### bd update

Update an issue.

```bash
bd update <issue-id> [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--status` | New status |
| `--priority` | New priority |
| `--title` | New title |
| `--description` | New description |
| `--assignee` | New assignee |
| `--add-label` | Add label |
| `--remove-label` | Remove label |

**Examples:**
```bash
# Start work
bd update bd-a1b2 --status in_progress --json

# Change priority
bd update bd-a1b2 --priority 0 --json

# Add label
bd update bd-a1b2 --add-label urgent --json
```

### bd close

Close an issue.

```bash
bd close <issue-id> [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--reason` | Closing reason (required) |
| `--resolution` | Resolution type: completed, wontfix, duplicate |

**Examples:**
```bash
bd close bd-a1b2 --reason "Implemented in PR #123" --json

bd close bd-c3d4 --reason "Duplicate of bd-a1b2" --resolution duplicate --json
```

## Work Discovery

### bd ready

Find issues ready to work on (no blockers).

```bash
bd ready [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--sort` | Sort by: priority, oldest, hybrid (default: hybrid) |
| `--assignee` | Filter by assignee |
| `--type` | Filter by type |
| `--limit` | Max results (default: 10) |

**Example:**
```bash
bd ready --sort priority --limit 5 --json
```

**Output:**
```json
{
  "issues": [
    {
      "id": "bd-a1b2",
      "title": "Critical security fix",
      "priority": 0,
      "status": "open",
      "type": "bug",
      "blockers": [],
      "age_days": 2
    },
    {
      "id": "bd-c3d4",
      "title": "Add user dashboard",
      "priority": 1,
      "status": "open",
      "type": "feature",
      "blockers": [],
      "age_days": 5
    }
  ],
  "total_ready": 12
}
```

### bd blocked

List blocked issues and their blockers.

```bash
bd blocked [flags]
```

**Example:**
```bash
bd blocked --json
```

**Output:**
```json
{
  "blocked_issues": [
    {
      "id": "bd-e5f6",
      "title": "Deploy to production",
      "blocked_by": [
        {"id": "bd-a1b2", "title": "Critical security fix", "status": "in_progress"},
        {"id": "bd-c3d4", "title": "Add user dashboard", "status": "open"}
      ]
    }
  ]
}
```

## Dependency Management

### bd dep add

Add a dependency between issues.

```bash
bd dep add <issue-id> <dependency-id> [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--type` | Dependency type: blocks, related, parent-child, discovered-from |

**Default**: `blocks` (second issue blocks first)

**Examples:**
```bash
# bd-c3d4 blocks bd-a1b2 (can't start a1b2 until c3d4 is done)
bd dep add bd-a1b2 bd-c3d4

# Link discovered work to source
bd dep add bd-new bd-parent --type discovered-from

# Just a reference link
bd dep add bd-a1b2 bd-e5f6 --type related
```

### bd dep remove

Remove a dependency.

```bash
bd dep remove <issue-id> <dependency-id>
```

### bd dep tree

Visualize dependency tree.

```bash
bd dep tree <issue-id> [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--depth` | Max depth (default: 5) |
| `--direction` | up, down, or both (default: both) |

**Example:**
```bash
bd dep tree bd-a1b2 --depth 3 --json
```

### bd dep cycles

Detect circular dependencies.

```bash
bd dep cycles [--json]
```

## Labels

### bd label add

Add a label to an issue.

```bash
bd label add <issue-id> <label>
```

### bd label remove

Remove a label from an issue.

```bash
bd label remove <issue-id> <label>
```

### bd label list

List all labels in use.

```bash
bd label list [--json]
```

## Configuration

### bd config get

Get a configuration value.

```bash
bd config get <key>
```

### bd config set

Set a configuration value.

```bash
bd config set <key> <value>
```

**Common keys:**
| Key | Description | Default |
|-----|-------------|---------|
| `agent_mail.enabled` | Enable Agent Mail sync | false |
| `sync.auto_export` | Auto-export on changes | true |
| `sync.debounce_ms` | Export debounce time | 5000 |
| `compact.threshold_days` | Days before compaction eligible | 30 |

### bd config list

List all configuration.

```bash
bd config list [--json]
```

## Sync & Maintenance

### bd sync

Force synchronization with git.

```bash
bd sync [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--force` | Force sync even with conflicts |
| `--pull-only` | Only import from git, don't export |
| `--push-only` | Only export to git, don't import |

### bd compact

Compact old closed issues.

```bash
bd compact [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--analyze` | Show what would be compacted |
| `--execute` | Actually perform compaction |
| `--older-than` | Age threshold (e.g., 30d, 2w) |
| `--dry-run` | Preview changes |

**Example:**
```bash
# Check compaction potential
bd compact --analyze --json

# Execute compaction
bd compact --older-than 14d --execute
```

### bd doctor

Health check and repair.

```bash
bd doctor [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--fix` | Attempt to fix issues |
| `--verbose` | Detailed output |

### bd export

Export issues to file.

```bash
bd export -o <filename> [flags]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--format` | json, jsonl, csv |
| `--status` | Filter by status |

### bd import

Import issues from file.

```bash
bd import -i <filename> [flags]
```

## Daemon Management

### bd daemons list

List running daemons.

```bash
bd daemons list [--json]
```

### bd daemons health

Check daemon health.

```bash
bd daemons health [--json]
```

### bd daemons logs

View daemon logs.

```bash
bd daemons logs [--follow] [--lines <n>]
```

### bd daemons killall

Stop all daemons.

```bash
bd daemons killall
```

## Hash-Based ID System (v0.20.1+)

IDs use progressive-length hashes to prevent collisions:

| Database Size | ID Length | Example |
|---------------|-----------|---------|
| 0-500 | 4 chars | `bd-a1b2` |
| 500-1500 | 5 chars | `bd-f14c3` |
| 1500+ | 6 chars | `bd-3e7a5b` |

**Child issues** use dot notation: `bd-a1b2.1`, `bd-a1b2.2`

## Status Values

| Status | Description |
|--------|-------------|
| `open` | Not started |
| `in_progress` | Currently being worked on |
| `blocked` | Waiting on dependencies |
| `closed` | Completed |

## Priority Values

| Priority | Meaning |
|----------|---------|
| 0 | Critical - immediate attention |
| 1 | High - important |
| 2 | Normal - standard priority (default) |
| 3 | Low - when time permits |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Issue not found |
| 4 | Sync error |
| 5 | Configuration error |
