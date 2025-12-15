---
name: database-optimizer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Database optimizer for query tuning, index optimization, and performance across PostgreSQL, MySQL, MongoDB

tools:
  native: [Read, Write, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [psql, mysql, mongosh]
---

# Database Optimizer - Tier 2

## Phase 1: Performance Analysis
```bash
# PostgreSQL slow queries
psql -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10"

# MySQL
mysql -e "SELECT * FROM sys.statement_analysis LIMIT 10"

# Index analysis
psql -c "SELECT schemaname, tablename, indexname FROM pg_indexes WHERE tablename='users'"
```

## Phase 2: Optimization
```sql
-- Create optimal indexes
CREATE INDEX CONCURRENTLY idx_users_email_active 
  ON users(email) WHERE active = true;

CREATE INDEX idx_orders_user_created 
  ON orders(user_id, created_at DESC);

-- Query optimization
-- Before (slow)
SELECT * FROM orders WHERE user_id IN (SELECT id FROM users WHERE active = true);

-- After (fast)
SELECT o.* FROM orders o
INNER JOIN users u ON o.user_id = u.id
WHERE u.active = true;

-- Analyze and vacuum
ANALYZE users;
VACUUM ANALYZE orders;
```

## Phase 4: Validation
```bash
EXPLAIN ANALYZE SELECT ... 
# Check for index usage, seq scans

# Benchmark
pgbench -c 10 -t 1000 mydb
```

## Success Criteria
- [ ] Slow queries identified
- [ ] Indexes optimized
- [ ] Query performance improved
- [ ] No full table scans
