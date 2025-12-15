# Claude-Mem Troubleshooting

## Common Issues

### Worker Not Running

**Symptoms:**
- `curl http://localhost:37777/health` fails
- Search returns nothing
- No observations captured

**Solutions:**

```bash
# Check PM2 status
pm2 status

# If not running, start manually
claude-mem start

# If PM2 not found
npm install -g pm2
claude-mem start

# Check logs for errors
pm2 logs claude-mem

# Force restart
claude-mem restart
```

### Plugin Not Capturing Observations

**Symptoms:**
- Worker running but no new observations
- Sessions not being created

**Solutions:**

```bash
# Verify plugin is installed
/plugin status claude-mem

# Re-install if needed
/plugin uninstall claude-mem
/plugin install claude-mem

# Check hooks are registered
cat ~/.claude-mem/hooks.json

# Enable verbose logging
claude-mem config set debug true
claude-mem restart
```

### Search Returns No Results

**Symptoms:**
- Search queries return empty
- mem-search skill says "no results"

**Solutions:**

```bash
# Check database has data
sqlite3 ~/.claude-mem/memory.db "SELECT COUNT(*) FROM observations"

# Check retention settings
claude-mem config get retention_days
# If too short, increase:
claude-mem config set retention_days 30

# Rebuild FTS index
claude-mem rebuild-index

# Check Chroma is working
python -c "import chromadb; print('OK')"
```

### High Latency

**Symptoms:**
- Slow session starts
- Long delays after tool executions
- Endless Mode causing 60-90s delays

**Solutions:**

```bash
# Disable Endless Mode if enabled
claude-mem config set endless_mode false

# Reduce injection size
claude-mem config set max_inject_tokens 1000

# Compact old observations
claude-mem compact --older-than 7d

# Check worker CPU usage
pm2 monit
```

### Memory Growing Too Large

**Symptoms:**
- Disk usage increasing
- Database queries slowing down

**Solutions:**

```bash
# Check sizes
du -sh ~/.claude-mem/

# Compact old data
claude-mem compact --older-than 30d

# Set automatic retention
claude-mem config set retention_days 30
claude-mem config set auto_compact true

# Manual cleanup
claude-mem clear --older-than 60d --confirm
```

### Chroma/Vector Search Issues

**Symptoms:**
- Semantic search not working
- Error messages about embeddings

**Solutions:**

```bash
# Check Python version (needs 3.10+)
python --version

# Reinstall Chroma
pip uninstall chromadb
pip install chromadb

# Reset vector database
rm -rf ~/.claude-mem/chroma
claude-mem restart
# Observations will be re-embedded on next search
```

### Context Injection Too Large

**Symptoms:**
- Session start takes long
- "Context overflow" warnings

**Solutions:**

```bash
# Reduce injection tokens
claude-mem config set max_inject_tokens 1500

# Use index-only injection
claude-mem config set inject_level 1  # Layer 1 only

# Disable auto-inject, use search only
claude-mem config set auto_inject false
```

### Hooks Not Firing

**Symptoms:**
- Observations not captured
- Sessions not created

**Solutions:**

```bash
# Check Claude Code hooks directory
ls ~/.config/claude/hooks/

# Verify hook scripts exist
cat ~/.config/claude/hooks/PostToolUse.sh

# Re-register hooks
/plugin uninstall claude-mem
/plugin install claude-mem

# Manual hook test
~/.config/claude/hooks/PostToolUse.sh
```

## Error Messages

### `ECONNREFUSED 127.0.0.1:37777`

Worker not running. Start with `claude-mem start`.

### `SQLITE_BUSY: database is locked`

Another process has the database open.

```bash
# Kill any stale processes
pkill -f "claude-mem"

# Force unlock (use with caution)
sqlite3 ~/.claude-mem/memory.db ".tables"

# Restart worker
claude-mem restart
```

### `ChromaDB: collection not found`

Vector database needs initialization.

```bash
# Reset Chroma
rm -rf ~/.claude-mem/chroma
claude-mem restart
```

### `Agent SDK error: rate limited`

Too many compression requests.

```bash
# Reduce observation frequency
claude-mem config set observation_interval 5  # Every 5 tool uses

# Use local compression (no API calls)
claude-mem config set local_compression true
```

### `Memory injection overflow`

Context too large for injection.

```bash
claude-mem config set max_inject_tokens 1000
claude-mem config set inject_level 1
```

## Performance Tuning

### For Large Projects

```bash
# Increase batch size for efficiency
claude-mem config set batch_size 20

# Use async compression
claude-mem config set async_compression true

# Set per-project databases
claude-mem config set project_isolation true
```

### For Limited Resources

```bash
# Reduce memory usage
claude-mem config set max_cache_size 50  # MB

# Disable vector search
claude-mem config set vector_search false

# Use lightweight compression
claude-mem config set compression_model "claude-haiku"
```

### For Team Usage

```bash
# Enable team sync (with Grov)
claude-mem config set auto_inject false

# Export for sharing
claude-mem export --sessions-only > team_context.json
```

## Diagnostic Commands

```bash
# Full status report
claude-mem status --verbose

# Database statistics
claude-mem stats

# Check configuration
claude-mem config list

# View recent logs
claude-mem logs --lines 100

# Test search
claude-mem test-search "auth"

# Benchmark performance
claude-mem benchmark
```

## Getting Help

1. Check logs: `pm2 logs claude-mem`
2. Enable debug: `claude-mem config set debug true`
3. GitHub Issues: https://github.com/thedotmack/claude-mem/issues
4. Web UI diagnostics: http://localhost:37777/diagnostics
