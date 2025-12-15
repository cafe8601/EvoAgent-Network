# Beads Troubleshooting Guide

Common issues and solutions for Beads usage.

## Installation Issues

### bd: command not found

**Symptoms:**
```bash
bd: command not found
# or
zsh: command not found: bd
```

**Solutions:**

1. **Check installation:**
   ```bash
   which bd
   npm list -g @beads/bd
   ```

2. **Reinstall:**
   ```bash
   # npm
   npm install -g @beads/bd

   # Or curl
   curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
   ```

3. **Add to PATH (if installed but not found):**
   ```bash
   # Find installation location
   npm root -g

   # Add to PATH in ~/.bashrc or ~/.zshrc
   export PATH="$PATH:$(npm root -g)/../bin"

   # Reload
   source ~/.bashrc
   ```

### glibc version error (Linux)

**Symptoms:**
```
/lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.32' not found
```

**Cause:** Beads requires glibc 2.32+ (Ubuntu 22.04+, Debian 11+)

**Solutions:**

1. **Upgrade OS (recommended):**
   ```bash
   # Check current glibc version
   ldd --version

   # Upgrade to Ubuntu 22.04+
   sudo do-release-upgrade
   ```

2. **Build from source (alternative):**
   ```bash
   # Install Go 1.21+
   sudo snap install go --classic

   # Clone and build
   git clone https://github.com/steveyegge/beads.git
   cd beads
   go build -o bd ./cmd/bd
   sudo mv bd /usr/local/bin/
   ```

3. **Use Docker:**
   ```dockerfile
   FROM ubuntu:22.04
   RUN apt-get update && apt-get install -y nodejs npm
   RUN npm install -g @beads/bd
   ```

### npm permission errors

**Symptoms:**
```
EACCES: permission denied
npm ERR! Error: EACCES
```

**Solutions:**

1. **Use npx (no global install):**
   ```bash
   npx @beads/bd init
   npx @beads/bd ready --json
   ```

2. **Fix npm permissions:**
   ```bash
   mkdir ~/.npm-global
   npm config set prefix '~/.npm-global'
   echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
   source ~/.bashrc
   npm install -g @beads/bd
   ```

## Initialization Issues

### bd init fails

**Symptoms:**
```
Error: Not a git repository
Error: Failed to initialize database
```

**Solutions:**

1. **Initialize git first:**
   ```bash
   git init
   bd init
   ```

2. **Check permissions:**
   ```bash
   ls -la .beads/
   # Should be writable by current user
   ```

3. **Force reinitialize:**
   ```bash
   rm -rf .beads/
   bd init --quiet
   ```

### Stealth mode not working

**Symptoms:**
- Beads files appearing in git status
- Team members seeing .beads/ directory

**Solutions:**

1. **Verify stealth setup:**
   ```bash
   cat ~/.gitignore_global | grep beads
   # Should show: .beads/
   ```

2. **Manually add to global gitignore:**
   ```bash
   echo ".beads/" >> ~/.gitignore_global
   git config --global core.excludesfile ~/.gitignore_global
   ```

3. **Remove from git if already tracked:**
   ```bash
   git rm -r --cached .beads/
   echo ".beads/" >> .gitignore
   git commit -m "Remove beads from tracking"
   ```

## Sync Issues

### Sync conflicts

**Symptoms:**
```
Error: Merge conflict in .beads/issues.jsonl
CONFLICT (content): Merge conflict
```

**Solutions:**

1. **Let Beads handle it:**
   ```bash
   bd sync --force
   ```

2. **Manual resolution:**
   ```bash
   # Accept all remote changes
   git checkout --theirs .beads/issues.jsonl
   bd sync

   # Or accept local changes
   git checkout --ours .beads/issues.jsonl
   bd sync
   ```

3. **Rebuild from JSONL:**
   ```bash
   rm .beads/beads.db
   bd sync --pull-only
   ```

### Changes not syncing

**Symptoms:**
- Created issues not appearing in git
- Changes lost after pull

**Solutions:**

1. **Force export:**
   ```bash
   bd sync --push-only
   git add .beads/issues.jsonl
   git commit -m "beads: manual sync"
   ```

2. **Check daemon:**
   ```bash
   bd daemons health
   # If unhealthy:
   bd daemons killall
   bd sync
   ```

3. **Verify auto-export config:**
   ```bash
   bd config get sync.auto_export
   # Should be true
   bd config set sync.auto_export true
   ```

### Database corruption

**Symptoms:**
```
Error: database is locked
Error: database disk image is malformed
```

**Solutions:**

1. **Rebuild from JSONL:**
   ```bash
   rm .beads/beads.db
   bd doctor --fix
   ```

2. **Full reset:**
   ```bash
   # Backup JSONL first
   cp .beads/issues.jsonl /tmp/beads-backup.jsonl

   # Reset
   rm -rf .beads/
   bd init --quiet

   # Restore
   bd import -i /tmp/beads-backup.jsonl
   ```

## Command Issues

### bd ready returns empty

**Symptoms:**
```bash
bd ready --json
# Returns: {"issues": [], "total_ready": 0}
```

**Causes & Solutions:**

1. **All issues have blockers:**
   ```bash
   # Check blocked issues
   bd blocked --json

   # View dependency tree
   bd dep tree <issue-id>

   # Remove circular dependency if found
   bd dep cycles
   bd dep remove <issue-a> <issue-b>
   ```

2. **All issues closed:**
   ```bash
   bd list --status open --json
   # If empty, create new work or reopen
   bd create "New task" --json
   ```

3. **Filter too restrictive:**
   ```bash
   # Remove assignee filter
   bd ready --json  # Without --assignee

   # Check all statuses
   bd list --json
   ```

### bd create fails

**Symptoms:**
```
Error: invalid argument
Error: title is required
```

**Solutions:**

1. **Quote title properly:**
   ```bash
   # Wrong
   bd create Fix the bug --json

   # Correct
   bd create "Fix the bug" --json
   ```

2. **Escape special characters:**
   ```bash
   bd create "Fix: \"quoted\" text" --json
   bd create 'Fix: $variable issue' --json
   ```

3. **Check flag syntax:**
   ```bash
   # Wrong
   bd create "Title" -description "desc"

   # Correct
   bd create "Title" -d "desc" --json
   bd create "Title" --description "desc" --json
   ```

### Circular dependency error

**Symptoms:**
```
Error: circular dependency detected
Cannot add dependency: would create cycle
```

**Solutions:**

1. **Find the cycle:**
   ```bash
   bd dep cycles --json
   ```

2. **Remove problematic dependency:**
   ```bash
   bd dep remove <issue-a> <issue-b>
   ```

3. **Restructure dependencies:**
   ```bash
   # Instead of A → B → C → A
   # Create parent issue P
   bd create "Parent task" -t epic --json
   bd dep add A P --type parent-child
   bd dep add B P --type parent-child
   bd dep add C P --type parent-child
   ```

## Daemon Issues

### Daemon not starting

**Symptoms:**
```
Error: failed to connect to daemon
Error: daemon socket not found
```

**Solutions:**

1. **Check daemon status:**
   ```bash
   bd daemons list
   bd daemons health
   ```

2. **Kill and restart:**
   ```bash
   bd daemons killall
   # Next command will restart daemon
   bd list --json
   ```

3. **Check socket permissions:**
   ```bash
   ls -la /tmp/beads-*
   # Remove stale sockets
   rm /tmp/beads-*.sock
   ```

### Daemon version mismatch

**Symptoms:**
```
Warning: daemon version mismatch
```

**Solutions:**

```bash
# After upgrading bd
bd daemons health  # Shows mismatch
bd daemons killall
bd list --json     # Starts new daemon
bd daemons health  # Should be healthy now
```

### High CPU usage from daemon

**Symptoms:**
- `bd` process consuming high CPU
- System slowdown

**Solutions:**

1. **Increase poll interval:**
   ```bash
   bd config set agent_mail.poll_interval_ms 1000  # 1 second
   bd daemons killall
   ```

2. **Disable Agent Mail if not needed:**
   ```bash
   bd config set agent_mail.enabled false
   bd daemons killall
   ```

## Performance Issues

### Slow queries on large databases

**Symptoms:**
- `bd list` takes several seconds
- `bd ready` timeout

**Solutions:**

1. **Compact old issues:**
   ```bash
   bd compact --analyze --json
   bd compact --older-than 30d --execute
   ```

2. **Use filters:**
   ```bash
   # Instead of
   bd list --json

   # Use
   bd list --status open --limit 50 --json
   ```

3. **Rebuild index:**
   ```bash
   rm .beads/beads.db
   bd sync --pull-only
   ```

### Large JSONL file

**Symptoms:**
- `.beads/issues.jsonl` > 10MB
- Slow git operations

**Solutions:**

1. **Run compaction:**
   ```bash
   bd compact --execute
   ```

2. **Archive old issues:**
   ```bash
   bd export -o archive-$(date +%Y%m).json --status closed
   # Then compact
   bd compact --execute
   ```

## JSON Output Issues

### Invalid JSON output

**Symptoms:**
```
json.decoder.JSONDecodeError
Unexpected token
```

**Solutions:**

1. **Ensure --json flag:**
   ```bash
   # Wrong - mixed output
   bd list

   # Correct - pure JSON
   bd list --json
   ```

2. **Capture only stdout:**
   ```python
   result = subprocess.run(
       ["bd", "list", "--json"],
       capture_output=True,
       text=True
   )
   # Use result.stdout, not result.stderr
   data = json.loads(result.stdout)
   ```

3. **Check for error messages:**
   ```bash
   bd list --json 2>/dev/null
   ```

### Empty JSON response

**Symptoms:**
```bash
bd show bd-xxxx --json
# Returns: {}
```

**Solutions:**

1. **Verify issue exists:**
   ```bash
   bd list --json | grep "bd-xxxx"
   ```

2. **Check ID format:**
   ```bash
   # Correct format: bd-xxxx or bd-xxxxx
   bd show bd-a1b2 --json

   # Not just the hash
   bd show a1b2 --json  # Wrong
   ```

## Migration Issues

### Migrating from sequential IDs

**Symptoms:**
- Old issues with numeric IDs not working
- ID conflicts after upgrade

**Solutions:**

```bash
# Run migration
bd migrate --json

# Verify
bd list --json
# All IDs should be hash-based (bd-xxxx)
```

### Importing from other systems

**Solutions:**

1. **From GitHub Issues:**
   ```bash
   # Export from GitHub
   gh issue list --json number,title,body,state > gh-issues.json

   # Convert and import (custom script needed)
   python convert_gh_to_beads.py gh-issues.json > beads-import.jsonl
   bd import -i beads-import.jsonl
   ```

2. **From markdown TODOs:**
   ```bash
   # Create issues from TODOs
   grep -rn "TODO:" src/ | while read line; do
     file=$(echo $line | cut -d: -f1)
     todo=$(echo $line | cut -d: -f3-)
     bd create "$todo" -d "Found in $file" -t task --json
   done
   ```

## Getting Help

### Built-in help

```bash
bd --help
bd <command> --help
bd create --help
```

### Health check

```bash
bd doctor --verbose
```

### Debug logging

```bash
# Enable verbose output
BD_DEBUG=1 bd list --json

# Check daemon logs
bd daemons logs --lines 100
```

### Community resources

- **GitHub Issues**: https://github.com/steveyegge/beads/issues
- **Discussions**: https://github.com/steveyegge/beads/discussions
- **Discord**: Check README for invite link

### Reporting bugs

When reporting issues, include:

```bash
# Version info
bd --version

# System info
uname -a
node --version
npm --version

# Doctor output
bd doctor --json

# Relevant logs
bd daemons logs --lines 50
```
