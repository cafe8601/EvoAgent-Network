# Claude-Mem API Reference

## CLI Commands

### Memory Management

```bash
# Start/stop worker
claude-mem start              # Start PM2 worker
claude-mem stop               # Stop worker
claude-mem restart            # Restart worker

# Search memory
claude-mem search <query>     # Natural language search
claude-mem search "auth" --limit 10 --since 7d

# View sessions
claude-mem sessions           # List all sessions
claude-mem sessions --recent  # Last 10 sessions
claude-mem session <id>       # View specific session

# Maintenance
claude-mem compact            # Compress old observations
claude-mem clear --confirm    # Delete all memory
claude-mem export > backup.json  # Export data
claude-mem import < backup.json  # Import data
```

### Configuration

```bash
# View settings
claude-mem config list
claude-mem config get <key>

# Modify settings
claude-mem config set <key> <value>

# Available keys:
# - auto_inject: bool (inject at session start)
# - capture_tool_outputs: bool (capture tool results)
# - retention_days: int (days to keep observations)
# - endless_mode: bool (experimental compression)
# - max_inject_tokens: int (limit injection size)
# - worker_port: int (HTTP API port, default 37777)
```

## HTTP API

Base URL: `http://localhost:37777`

### Health Check

```bash
GET /health

Response:
{
  "status": "ok",
  "version": "6.5.0",
  "uptime": 3600
}
```

### Search

```bash
GET /search?q=<query>&limit=<n>&since=<duration>

Parameters:
- q: Search query (required)
- limit: Max results (default 10)
- since: Time filter (e.g., "7d", "24h", "1w")
- type: Filter by type ("observation", "session", "prompt")

Response:
{
  "results": [
    {
      "id": "obs_123",
      "type": "observation",
      "content": "Modified auth/login.ts...",
      "tool": "Write",
      "created": "2025-12-10T10:30:00Z",
      "session_id": "sess_456",
      "relevance": 0.95
    }
  ],
  "total": 42
}
```

### Sessions

```bash
GET /sessions
GET /sessions/<id>
GET /sessions/<id>/observations

Response:
{
  "sessions": [
    {
      "id": "sess_456",
      "started": "2025-12-10T09:00:00Z",
      "ended": "2025-12-10T12:00:00Z",
      "summary": "Worked on authentication module...",
      "observation_count": 15
    }
  ]
}
```

### Observations

```bash
GET /observations
GET /observations/<id>
GET /observations?file=<path>

Response:
{
  "observations": [
    {
      "id": "obs_123",
      "tool": "Write",
      "file_path": "src/auth/login.ts",
      "content": "Added JWT validation...",
      "concepts": ["authentication", "security"],
      "created": "2025-12-10T10:30:00Z"
    }
  ]
}
```

## Lifecycle Hooks

Claude-mem uses 6 lifecycle hooks:

### SessionStart

Triggered when Claude Code session begins.

```javascript
// Hook behavior
1. Load recent observations index
2. Calculate injection budget (max_inject_tokens)
3. Inject relevant context into system prompt
```

### UserPromptSubmit

Triggered when user sends a prompt.

```javascript
// Hook behavior
1. Create/update session record
2. Store user prompt for searchability
3. Extract intent for context matching
```

### PostToolUse

Triggered after each tool execution.

```javascript
// Hook behavior
1. Capture tool name, inputs, outputs
2. Queue for compression (async)
3. In Endless Mode: compress immediately, replace output
```

### Stop

Triggered when user interrupts.

```javascript
// Hook behavior
1. Mark current task as interrupted
2. Save partial observation
```

### SessionEnd

Triggered when session closes.

```javascript
// Hook behavior
1. Generate session summary
2. Finalize all pending observations
3. Update session record with end time
```

## Database Schema

### SQLite Tables

```sql
-- Sessions
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  started DATETIME,
  ended DATETIME,
  summary TEXT,
  prompt_count INTEGER,
  observation_count INTEGER
);

-- Observations
CREATE TABLE observations (
  id TEXT PRIMARY KEY,
  session_id TEXT REFERENCES sessions(id),
  tool TEXT,
  file_path TEXT,
  content TEXT,
  raw_output TEXT,
  concepts TEXT,  -- JSON array
  created DATETIME
);

-- FTS index
CREATE VIRTUAL TABLE observations_fts USING fts5(
  content,
  file_path,
  concepts
);

-- User prompts
CREATE TABLE prompts (
  id TEXT PRIMARY KEY,
  session_id TEXT REFERENCES sessions(id),
  content TEXT,
  created DATETIME
);
```

### Chroma Collections

```python
# Vector embeddings for semantic search
collection = chroma.get_or_create_collection("observations")

# Document structure
{
  "id": "obs_123",
  "embedding": [0.1, 0.2, ...],  # 1536 dimensions
  "metadata": {
    "session_id": "sess_456",
    "tool": "Write",
    "file_path": "src/auth/login.ts",
    "created": "2025-12-10T10:30:00Z"
  }
}
```

## mem-search Skill Interface

The mem-search skill is auto-invoked by Claude:

```yaml
# Skill definition
name: mem-search
description: Search past work sessions for relevant context

operations:
  - name: search_observations
    description: Search all captured observations
    parameters:
      query: string
      limit: int (default 5)
      since: string (optional, e.g., "7d")

  - name: search_sessions
    description: Find specific sessions
    parameters:
      query: string
      limit: int (default 5)

  - name: search_by_file
    description: Search by file path pattern
    parameters:
      pattern: string (glob pattern)
      limit: int (default 10)

  - name: search_concepts
    description: Search by concept tags
    parameters:
      concepts: string[] (e.g., ["authentication", "bug-fix"])
      limit: int (default 5)

  - name: get_session_details
    description: Get full details of a session
    parameters:
      session_id: string
      include_observations: bool (default true)
```

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `WORKER_NOT_RUNNING` | PM2 worker stopped | `claude-mem start` |
| `DB_LOCKED` | Database locked by another process | Wait or restart worker |
| `SEARCH_TIMEOUT` | Search took too long | Reduce query complexity |
| `INJECTION_OVERFLOW` | Context too large | Reduce `max_inject_tokens` |
| `CHROMA_ERROR` | Vector DB issue | Check Python/Chroma installation |
