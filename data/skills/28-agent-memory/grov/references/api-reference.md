# Grov API Reference

## CLI Commands

### Core Commands

```bash
# Initialize grov (one-time setup)
grov init
# Sets ANTHROPIC_BASE_URL=http://127.0.0.1:8080 in Claude config

# Start proxy server (required for memory capture)
grov proxy
# Options:
#   --port <port>     Proxy port (default: 8080)
#   --verbose         Enable debug logging
#   --no-drift        Disable drift detection

# Check system status
grov status
# Shows: proxy status, memory count, cloud sync status

# View captured tasks/reasoning
grov tasks
# Options:
#   --json            Output as JSON
#   --limit <n>       Limit results
#   --since <date>    Filter by date
```

### Cloud Commands

```bash
# Authenticate with GitHub
grov login
# Opens browser for GitHub OAuth

# Sync memories to team dashboard
grov sync
# Options:
#   --force           Override conflicts
#   --dry-run         Preview what would sync

# Disconnect from cloud
grov logout

# View sync status
grov sync status
```

### Configuration

```bash
# Set configuration value
grov config set <key> <value>

# Get configuration value
grov config get <key>

# List all configuration
grov config list

# Reset to defaults
grov config reset
```

### Configuration Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `drift_detection` | bool | true | Enable anti-drift monitoring |
| `drift_threshold` | int | 5 | Intervention threshold (1-10) |
| `extended_cache` | bool | false | Keep Anthropic cache alive |
| `cache_interval` | int | 240 | Keep-alive interval (seconds) |
| `cloud_sync` | bool | true | Enable team synchronization |
| `exclude_paths` | string | "" | Comma-separated paths to exclude |
| `proxy_port` | int | 8080 | Local proxy port |
| `log_level` | string | "info" | Logging verbosity |

### Maintenance Commands

```bash
# Disable grov (restore direct API access)
grov disable

# Re-enable grov
grov enable

# Clear local memory
grov clear
# Options:
#   --confirm         Skip confirmation prompt
#   --older-than <n>d Clear entries older than n days

# Export memories
grov export > backup.json

# Import memories
grov import < backup.json
```

## Proxy API

When `grov proxy` is running, it exposes internal APIs:

### Health Check

```bash
GET http://127.0.0.1:8080/grov/health

Response:
{
  "status": "ok",
  "version": "0.5.2",
  "uptime": 3600,
  "memories": 42,
  "drift_detection": true
}
```

### Get Memories

```bash
GET http://127.0.0.1:8080/grov/memories

Query params:
- limit: int (default 10)
- since: ISO date
- files: comma-separated file paths

Response:
{
  "memories": [
    {
      "id": "mem_123",
      "task": "Fix auth logout bug",
      "files": ["session.ts", "token.ts"],
      "reasoning": "Extended token refresh because...",
      "decision": "Changed from 5min to 15min",
      "created": "2025-12-10T10:30:00Z"
    }
  ]
}
```

### Get Context for Files

```bash
GET http://127.0.0.1:8080/grov/context?files=session.ts,token.ts

Response:
{
  "context": "VERIFIED CONTEXT FROM PREVIOUS SESSIONS:\n\n[Task: Fix auth...]",
  "memories_used": 3
}
```

### Drift Status

```bash
GET http://127.0.0.1:8080/grov/drift

Response:
{
  "enabled": true,
  "current_intent": "Fix the auth logout bug",
  "recent_score": 8,
  "intervention_level": "none",
  "history": [
    {"time": "10:30:00", "score": 9},
    {"time": "10:35:00", "score": 8}
  ]
}
```

## Database Schema

Grov stores data in SQLite (`~/.grov/memory.db`):

```sql
-- Tasks/Memories
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    task TEXT NOT NULL,
    files TEXT,  -- JSON array
    reasoning TEXT,
    decision TEXT,
    status TEXT DEFAULT 'completed',  -- completed, in_progress, blocked
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    synced BOOLEAN DEFAULT FALSE
);

-- Index for file-based lookups
CREATE INDEX idx_files ON memories(files);
CREATE INDEX idx_created ON memories(created);

-- Session tracking
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    intent TEXT,
    started DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended DATETIME,
    memory_count INTEGER DEFAULT 0
);

-- Drift history
CREATE TABLE drift_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id),
    score INTEGER,
    assessment TEXT,
    intervention TEXT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Cloud API

Team dashboard API (requires authentication):

### Sync Memories

```bash
POST https://api.grov.dev/v1/sync
Authorization: Bearer <token>
Content-Type: application/json

{
  "memories": [
    {
      "id": "mem_123",
      "task": "...",
      "files": ["..."],
      "reasoning": "...",
      "decision": "..."
    }
  ]
}

Response:
{
  "synced": 5,
  "conflicts": 0
}
```

### Search Team Memories

```bash
GET https://api.grov.dev/v1/search?q=<query>
Authorization: Bearer <token>

Response:
{
  "results": [
    {
      "id": "mem_456",
      "task": "...",
      "author": "teammate@github",
      "relevance": 0.95
    }
  ]
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Required for drift detection (uses Haiku) |
| `GROV_TOKEN` | Cloud dashboard auth token |
| `GROV_PROXY_PORT` | Override default proxy port |
| `GROV_LOG_LEVEL` | Logging verbosity (debug/info/warn/error) |
| `GROV_DATA_DIR` | Custom data directory (default: ~/.grov) |

## Proxy Behavior

### Request Interception

1. Claude Code sends request to `http://127.0.0.1:8080`
2. Grov extracts intent from first user message
3. Request forwarded to `https://api.anthropic.com`
4. Response intercepted for reasoning extraction
5. Reasoning stored in local database
6. Response returned to Claude Code

### Context Injection

On new sessions:

1. Grov detects session start
2. Checks files mentioned in initial prompt
3. Queries database for relevant memories
4. Prepends context to system message:

```
VERIFIED CONTEXT FROM PREVIOUS SESSIONS:
[Previous task and reasoning...]

YOU MAY SKIP EXPLORE AGENTS for files mentioned above.

---
[Original system message continues...]
```

### Drift Detection Flow

1. Every N tool calls, extract recent actions
2. Send to Claude Haiku with original intent
3. Receive alignment score (1-10)
4. If below threshold, inject correction:

```
[GROV DRIFT ALERT]
Your recent actions appear to be drifting from the original task.
Original intent: "Fix the auth logout bug"
Please refocus on the original objective.
```
