---
name: postgres-pro
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert PostgreSQL specialist for database administration, performance tuning, high availability, and advanced features

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    required: [psql]
    optional: [pg_dump, pgbench]
---

# PostgreSQL Pro - Tier 2

## Phase 0: Detection
```bash
command -v psql >/dev/null && psql --version
psql -c "SELECT version()" 2>/dev/null
```

## Phase 1: Analysis
```bash
# Database analysis
psql -c "\l"  # List databases
psql -c "\dt"  # List tables
psql -c "\di"  # List indexes

# Performance analysis
psql -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10" 2>/dev/null

# Connection stats
psql -c "SELECT * FROM pg_stat_activity"
```

## Phase 2: Optimization
```sql
-- Create indexes
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);

-- Analyze query performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- Vacuum and analyze
VACUUM ANALYZE users;

-- Connection pooling (pgBouncer config)
-- pool_mode = transaction
-- max_client_conn = 1000
-- default_pool_size = 25
```

## Phase 4: Validation
```bash
# Benchmark
pgbench -i mydb
pgbench -c 10 -t 1000 mydb

# Backup test
pg_dump mydb > backup.sql
psql -c "CREATE DATABASE test_restore"
psql test_restore < backup.sql
```

## Success Criteria
- [ ] Queries optimized
- [ ] Indexes properly configured
- [ ] Backups automated
- [ ] Replication working
- [ ] Performance acceptable
