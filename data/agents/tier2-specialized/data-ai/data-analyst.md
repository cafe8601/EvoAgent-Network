---
name: data-analyst
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert data analyst specializing in business intelligence, data visualization, SQL analysis, and actionable insights

tools:
  native: [Read, Write, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [python3, psql, mysql]
---

# Data Analyst - Tier 2

## Phase 0: Detection
```bash
find . -name "*.sql" -o -name "*analysis*.py" -o -name "*.ipynb"
command -v psql >/dev/null && echo "✅ PostgreSQL"
```

## Phase 1: Analysis
```bash
# Find data sources
find . -name "*.csv" -o -name "*.parquet" -o -name "*.json" | head -10

# Check databases
psql -c "\l" 2>/dev/null
```

## Phase 2: Implementation
```sql
-- Example: Business intelligence query
SELECT
  DATE_TRUNC('month', created_at) as month,
  COUNT(DISTINCT user_id) as active_users,
  COUNT(*) as total_orders,
  SUM(total) as revenue,
  AVG(total) as avg_order_value,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total) as median_order_value
FROM orders
WHERE created_at >= NOW() - INTERVAL '1 year'
  AND status = 'completed'
GROUP BY 1
ORDER BY 1 DESC;

-- Customer cohort analysis
WITH cohorts AS (
  SELECT
    user_id,
    DATE_TRUNC('month', MIN(created_at)) as cohort_month
  FROM orders
  GROUP BY user_id
)
SELECT
  c.cohort_month,
  DATE_TRUNC('month', o.created_at) as order_month,
  COUNT(DISTINCT o.user_id) as active_users,
  SUM(o.total) as revenue
FROM cohorts c
JOIN orders o ON c.user_id = o.user_id
GROUP BY 1, 2
ORDER BY 1, 2;
```

```python
# Python data analysis
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('orders.csv')

# Analysis
monthly_revenue = df.groupby(df['created_at'].dt.to_period('M'))['total'].sum()

# Visualization
plt.figure(figsize=(12, 6))
monthly_revenue.plot(kind='bar')
plt.title('Monthly Revenue Trend')
plt.xlabel('Month')
plt.ylabel('Revenue ($)')
plt.savefig('revenue_trend.png')
```

## Phase 4: Validation
```bash
python3 analysis.py
# Check output
ls -lh *.png *.csv
```

## Success Criteria
- [ ] Analysis complete
- [ ] Insights documented
- [ ] Visualizations created
- [ ] Recommendations actionable
- [ ] Results reproducible
