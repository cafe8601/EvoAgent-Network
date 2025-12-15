# CascadeFlow Cost Optimization Guide

Real-world cost optimization strategies and monitoring best practices.

## Understanding Cost Savings

### Where Savings Come From

**Research findings** (Lemony.ai, Nov 2025):
- 40-70% of text prompts don't need flagship models
- 20-60% of agent/tool calls can use smaller models
- Domain-specific models often outperform general models

**CascadeFlow approach**:
```
1000 queries → 70% drafter (cheap) + 30% verifier (expensive)

Without cascading:
1000 × $0.00625 (GPT-4o) = $6.25

With cascading:
700 × $0.00015 (mini) + 300 × $0.00625 (4o) = $0.105 + $1.875 = $1.98

Savings: $4.27 (68.3%)
```

## Real-World Cost Analysis

### Benchmark Results

**MT-Bench** (Conversational):
```
Baseline (GPT-4o only): $12.50 per 1000 queries
CascadeFlow: $3.88
Savings: $8.62 (69%)
Quality: 96% of GPT-4o performance
```

**GSM8K** (Math):
```
Baseline: $8.75
CascadeFlow: $0.61
Savings: $8.14 (93%)
Quality: 96% of GPT-4o
```

**MMLU** (Knowledge):
```
Baseline: $15.30
CascadeFlow: $7.34
Savings: $7.96 (52%)
Quality: 96% of GPT-4o
```

### Production Case Study

**E-commerce Chatbot** (10,000 queries/day):

**Before CascadeFlow**:
```
Model: GPT-4o ($0.00625 per 1M input)
Daily queries: 10,000
Avg tokens: 500 input + 200 output
Daily cost: $52.50
Monthly cost: $1,575
```

**After CascadeFlow**:
```
Drafter: GPT-4o-mini (70% acceptance)
Verifier: GPT-4o (30% escalation)

Daily cost: $8.93
Monthly cost: $268

Savings: $1,307/month (83%)
Annual savings: $15,684
```

## Cost Optimization Strategies

### Strategy 1: Optimal Drafter Selection

**Test multiple drafters**:
```python
from cascadeflow import ModelConfig, CascadeAgent

# Test candidates
drafters = [
    ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
    ModelConfig(name="claude-3-5-haiku", provider="anthropic", cost=0.00125),
    ModelConfig(name="llama-3.2-3b", provider="groq", cost=0.00005)
]

verifier = ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)

# Evaluate each
results = {}
for drafter in drafters:
    agent = CascadeAgent(models=[drafter, verifier])
    metrics = await agent.evaluate(test_queries)
    results[drafter.name] = {
        "acceptance_rate": metrics.drafter_acceptance,
        "avg_cost": metrics.avg_cost,
        "quality_score": metrics.avg_quality
    }

# Choose best drafter
best = max(results.items(), key=lambda x: x[1]["acceptance_rate"])
print(f"Best drafter: {best[0]} ({best[1]['acceptance_rate']:.1%} acceptance)")
```

### Strategy 2: Threshold Tuning

**Find optimal quality threshold**:

```python
from cascadeflow import CascadeAgent, QualityConfig

thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
results = []

for threshold in thresholds:
    quality_config = QualityConfig(confidence_threshold=threshold)
    agent = CascadeAgent(
        models=[drafter, verifier],
        quality_config=quality_config
    )

    metrics = await agent.evaluate(test_queries)
    results.append({
        "threshold": threshold,
        "cost": metrics.avg_cost,
        "quality": metrics.avg_quality,
        "drafter_pct": metrics.drafter_acceptance
    })

# Analyze trade-off
for r in results:
    print(f"Threshold {r['threshold']}: "
          f"Cost ${r['cost']:.6f}, "
          f"Quality {r['quality']:.2%}, "
          f"Drafter {r['drafter_pct']:.1%}")

# Optimal: Highest quality/cost ratio
```

**Typical findings**:
| Threshold | Drafter % | Cost | Quality |
|-----------|-----------|------|---------|
| 0.5 | 85% | $0.001 | 88% |
| 0.6 | 78% | $0.002 | 92% |
| **0.7** | **68%** | **$0.003** | **96%** ← Optimal |
| 0.8 | 52% | $0.004 | 98% |
| 0.9 | 35% | $0.005 | 99% |

### Strategy 3: Domain-Specific Optimization

```python
# Use specialists for high-volume domains
domain_config = DomainConfig(
    domains={
        "CODE": [
            ModelConfig(name="deepseek-coder", provider="ollama", cost=0.0),  # Free
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
        ],
        "DEFAULT": [
            ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
        ]
    }
)

# If 50% queries are code-related:
# 50% × 100% drafter acceptance (specialist) = 50% free
# 50% × 70% drafter acceptance (general) = 35% cheap
# Total: 85% queries use cheap/free models
```

### Strategy 4: Self-Hosting for High Volume

```python
# High volume (>100k queries/day) → self-host drafter

# Option A: vLLM
# vllm serve llama-3.2-3b (see 12-inference-serving/vllm)
# Cost: ~$200/month GPU instance

agent = CascadeAgent(models=[
    ModelConfig(name="llama-3.2-3b", provider="vllm", cost=0.0),
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
])

# Break-even analysis:
# Cloud drafter: 100k × 0.7 × $0.00015 = $10.50/day = $315/month
# Self-hosted vLLM: $200/month + electricity
# Savings: $115/month
```

### Strategy 5: Caching + Cascading

```python
from cascadeflow import CacheConfig, CascadeAgent

# Combine caching with cascading
cache_config = CacheConfig(
    enabled=True,
    ttl=3600,
    backend="redis",
    redis_url="redis://localhost:6379"
)

agent = CascadeAgent(
    models=[drafter, verifier],
    cache_config=cache_config
)

# Cost savings compound:
# 1. Cache hits: 0 cost (assume 20% hit rate)
# 2. Drafter acceptance: cheap cost (70% of remaining)
# 3. Verifier: expensive cost (30% of remaining)

# Effective costs:
# 20% cache hits: $0.00
# 56% drafter hits: $0.00015
# 24% verifier hits: $0.00625
# Average: $0.002 (vs $0.00625 baseline = 68% savings)
```

## Cost Monitoring

### Built-in Analytics

```python
from cascadeflow import CascadeAgent

agent = CascadeAgent(models=[drafter, verifier])

# Process queries
for query in queries:
    result = await agent.run(query)

# Get analytics
analytics = agent.get_analytics()

print(f"Total queries: {analytics.total_queries}")
print(f"Total cost: ${analytics.total_cost:.4f}")
print(f"Avg cost per query: ${analytics.avg_cost_per_query:.6f}")
print(f"Drafter acceptance: {analytics.drafter_acceptance_rate:.1%}")
print(f"Cost savings vs baseline: {analytics.cost_savings_pct:.1%}")
```

### Per-User Cost Tracking

```python
# Track costs by user
user_costs = {}

for query_batch in query_batches:
    result = await agent.run(query_batch.query, user_id=query_batch.user_id)

    if query_batch.user_id not in user_costs:
        user_costs[query_batch.user_id] = 0
    user_costs[query_batch.user_id] += result.total_cost

# Analyze top spenders
top_users = sorted(user_costs.items(), key=lambda x: x[1], reverse=True)[:10]
for user_id, cost in top_users:
    print(f"User {user_id}: ${cost:.2f}")
```

### Cost Anomaly Detection

```python
from cascadeflow import AnomalyDetector

detector = AnomalyDetector(
    window_size=100,        # Rolling 100 queries
    std_threshold=3.0,      # 3 standard deviations
    on_anomaly=lambda: alert_ops_team()
)

agent = CascadeAgent(
    models=[drafter, verifier],
    anomaly_detector=detector
)

# Alerts when costs spike unexpectedly
# E.g., sudden increase in verifier usage
```

## Budget Management

### Daily Budget Limits

```python
from cascadeflow import BudgetConfig

budget_config = BudgetConfig(
    daily_limit=50.0,      # $50 per day
    on_limit_exceeded=lambda: switch_to_cheap_only_mode(),
    grace_period=0.1       # 10% grace before hard stop
)

agent = CascadeAgent(
    models=[drafter, verifier],
    budget_config=budget_config
)

# Automatically enforces budget
# Near limit: increases drafter acceptance threshold
# At limit: returns error or uses drafter only
```

### Per-User Budgets

```python
from cascadeflow import UserBudget

user_budgets = {
    "user-123": UserBudget(daily=5.0, monthly=100.0),
    "user-456": UserBudget(daily=10.0, monthly=200.0)
}

def enforce_budget(user_id, cost):
    budget = user_budgets[user_id]
    budget.spend(cost)

    if budget.daily_remaining < 0:
        raise BudgetExceededError(f"Daily budget exceeded for {user_id}")

agent = CascadeAgent(
    models=[drafter, verifier],
    on_query_complete=lambda result: enforce_budget(result.user_id, result.total_cost)
)
```

## ROI Calculation

### Calculate Savings

```python
def calculate_roi(baseline_model, cascade_agent, num_queries, avg_tokens):
    # Baseline cost
    baseline_cost_per_1m = 0.00625  # GPT-4o
    baseline_daily = (num_queries * avg_tokens / 1_000_000) * baseline_cost_per_1m
    baseline_monthly = baseline_daily * 30

    # Cascade cost (measured)
    cascade_metrics = cascade_agent.get_analytics()
    cascade_daily = cascade_metrics.total_cost
    cascade_monthly = cascade_daily * 30

    # Savings
    monthly_savings = baseline_monthly - cascade_monthly
    annual_savings = monthly_savings * 12
    savings_pct = (monthly_savings / baseline_monthly) * 100

    return {
        "baseline_monthly": baseline_monthly,
        "cascade_monthly": cascade_monthly,
        "monthly_savings": monthly_savings,
        "annual_savings": annual_savings,
        "savings_percentage": savings_pct
    }

roi = calculate_roi("gpt-4o", agent, num_queries=10000, avg_tokens=500)
print(f"Annual savings: ${roi['annual_savings']:,.2f} ({roi['savings_percentage']:.1f}%)")
```

### Break-Even Analysis for Self-Hosting

```python
def self_hosting_break_even(monthly_queries, avg_tokens):
    # Cloud drafter cost
    cloud_drafter_monthly = (
        monthly_queries * 0.7 * avg_tokens / 1_000_000 * 0.00015
    )

    # Self-hosting costs
    gpu_instance_monthly = 200  # e.g., A10G on AWS
    electricity_monthly = 50
    maintenance_monthly = 100
    self_hosting_monthly = gpu_instance_monthly + electricity_monthly + maintenance_monthly

    break_even_queries = (
        self_hosting_monthly /
        (0.7 * avg_tokens / 1_000_000 * 0.00015)
    )

    if monthly_queries > break_even_queries:
        savings = cloud_drafter_monthly - self_hosting_monthly
        return {"decision": "self_host", "monthly_savings": savings}
    else:
        return {"decision": "cloud", "queries_needed": break_even_queries}

analysis = self_hosting_break_even(monthly_queries=5_000_000, avg_tokens=500)
print(analysis)
```

**Typical break-even**: 2-3 million queries/month

## Cost Forecasting

### Predict Future Costs

```python
from cascadeflow import CostForecaster

forecaster = CostForecaster()

# Historical data
agent.run_queries(past_queries)  # 30 days of data

# Forecast next 30 days
forecast = forecaster.predict(
    historical_data=agent.get_analytics(),
    days_ahead=30,
    growth_rate=1.2  # Expect 20% growth
)

print(f"Forecasted cost: ${forecast.predicted_cost:.2f}")
print(f"Upper bound (95%): ${forecast.upper_bound:.2f}")
print(f"Lower bound (5%): ${forecast.lower_bound:.2f}")
```

### Seasonal Adjustment

```python
# Adjust routing for expected traffic patterns
def get_cascade_for_season():
    if is_holiday_season():
        # Higher traffic → more aggressive cost control
        return CascadeAgent(
            models=[drafter, verifier],
            quality_config=QualityConfig(threshold=0.6)  # Lower threshold
        )
    else:
        # Normal traffic → balanced
        return CascadeAgent(
            models=[drafter, verifier],
            quality_config=QualityConfig(threshold=0.7)
        )
```

## Optimization Patterns

### Pattern 1: Local + Cloud Hybrid

**Setup**:
```python
# Ollama local + OpenAI cloud
agent = CascadeAgent(models=[
    ModelConfig(name="llama3.2:3b", provider="ollama", cost=0.0),
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
])
```

**Cost analysis**:
```
10,000 queries/day
Drafter acceptance: 70%

Costs:
- Drafter: 7,000 × $0.00 = $0.00
- Verifier: 3,000 × $0.00625 × (500/1M) = $9.38

Total: $9.38/day vs $31.25/day baseline
Savings: $21.87/day (70%)
```

### Pattern 2: Multi-Tier Progressive

**Setup**:
```python
agent = CascadeAgent(models=[
    ModelConfig(name="groq-llama", provider="groq", cost=0.00005),      # Tier 1: 60%
    ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),   # Tier 2: 25%
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)         # Tier 3: 15%
])
```

**Cost breakdown**:
```
10,000 queries:
- 6,000 @ $0.00005 = $0.30
- 2,500 @ $0.00015 = $0.38
- 1,500 @ $0.00625 = $9.38

Total: $10.06 vs $62.50 baseline
Savings: $52.44 (84%)
```

### Pattern 3: Domain Specialization

**Setup**:
```python
domain_config = DomainConfig(
    domains={
        "CODE": [
            ModelConfig(name="deepseek-coder", provider="ollama", cost=0.0),
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
        ],
        "DEFAULT": [
            ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
        ]
    }
)

agent = CascadeAgent(domain_config=domain_config)
```

**Cost impact** (50% code queries):
```
Code queries (5,000):
- 90% specialist acceptance: 4,500 × $0.00 = $0.00
- 10% escalation: 500 × $0.00625 × (500/1M) = $1.56

General queries (5,000):
- 70% drafter: 3,500 × $0.00015 × (500/1M) = $0.26
- 30% verifier: 1,500 × $0.00625 × (500/1M) = $4.69

Total: $6.51 vs $31.25
Savings: $24.74 (79%)
```

## Cost Attribution

### Query-Level Attribution

```python
# Track cost per query type
query_costs = {"qa": [], "summarization": [], "translation": []}

for query, query_type in zip(queries, query_types):
    result = await agent.run(query)
    query_costs[query_type].append(result.total_cost)

# Analyze by type
for qtype, costs in query_costs.items():
    avg_cost = sum(costs) / len(costs)
    print(f"{qtype}: ${avg_cost:.6f} avg")
```

### Feature-Level Attribution

```python
# Track cost per application feature
feature_costs = {}

async def feature_query(feature_name, query):
    result = await agent.run(query)

    if feature_name not in feature_costs:
        feature_costs[feature_name] = []
    feature_costs[feature_name].append(result.total_cost)

    return result

# Use in application
await feature_query("chat", "Hello, how are you?")
await feature_query("search", "Find documents about AI")
await feature_query("summarize", "Summarize this article")

# Report by feature
for feature, costs in feature_costs.items():
    total = sum(costs)
    print(f"{feature}: ${total:.4f} ({len(costs)} queries)")
```

## Monitoring Best Practices

### Dashboard Metrics

```python
from cascadeflow import MetricsCollector

collector = MetricsCollector(
    export_interval=60,  # Export every 60s
    prometheus_port=9090
)

agent = CascadeAgent(
    models=[drafter, verifier],
    metrics_collector=collector
)

# Expose Prometheus metrics:
# - cascadeflow_query_total
# - cascadeflow_cost_dollars
# - cascadeflow_drafter_acceptance_rate
# - cascadeflow_latency_ms
# - cascadeflow_quality_score
```

**Grafana Dashboard**:
```
Panel 1: Cost over time (line chart)
Panel 2: Drafter vs Verifier usage (pie chart)
Panel 3: Savings percentage (gauge)
Panel 4: Quality score (line chart)
Panel 5: Top cost users (table)
```

### Alerting Rules

```python
from cascadeflow import AlertConfig

alert_config = AlertConfig(
    rules=[
        # Cost spike
        {
            "metric": "hourly_cost",
            "threshold": 10.0,
            "condition": "greater_than",
            "action": lambda: send_slack("Cost spike detected!")
        },
        # Quality drop
        {
            "metric": "avg_quality",
            "threshold": 0.85,
            "condition": "less_than",
            "action": lambda: send_email("Quality degradation alert")
        },
        # High verifier usage
        {
            "metric": "verifier_usage_pct",
            "threshold": 0.5,
            "condition": "greater_than",
            "action": lambda: investigate_drafter()
        }
    ]
)

agent = CascadeAgent(
    models=[drafter, verifier],
    alert_config=alert_config
)
```

## Cost Optimization Checklist

### Initial Setup
- [ ] Choose appropriate drafter (60-70% acceptance target)
- [ ] Set conservative quality threshold (0.7)
- [ ] Enable cost tracking
- [ ] Test on representative sample (100+ queries)

### First Week
- [ ] Monitor drafter acceptance rate
- [ ] Analyze cost savings percentage
- [ ] Check quality metrics
- [ ] Tune threshold if needed

### Ongoing Optimization
- [ ] Weekly cost review
- [ ] Monthly threshold adjustment
- [ ] Quarterly drafter re-evaluation
- [ ] Track ROI and report savings

### Advanced Optimization
- [ ] Enable domain-specific routing
- [ ] Implement user-tier cascading
- [ ] Add caching layer
- [ ] Consider self-hosting for high volume
- [ ] Set up anomaly detection
- [ ] Implement budget enforcement

## Common Cost Pitfalls

### Pitfall 1: Wrong Drafter

```python
# Bad: Drafter too weak (acceptance < 40%)
agent = CascadeAgent(models=[
    ModelConfig(name="tinyllama-1.1b", cost=0.0),  # Too weak
    ModelConfig(name="gpt-4o", cost=0.00625)
])
# Result: 60% verifier usage = minimal savings

# Good: Appropriately powerful drafter
agent = CascadeAgent(models=[
    ModelConfig(name="gpt-4o-mini", cost=0.00015),  # Right size
    ModelConfig(name="gpt-4o", cost=0.00625)
])
# Result: 70% drafter usage = 68% savings
```

### Pitfall 2: Threshold Too High

```python
# Bad: Threshold 0.9 (drafter rarely accepted)
quality_config = QualityConfig(threshold=0.9)
# Result: 35% drafter usage = only 40% savings

# Good: Threshold 0.7 (balanced)
quality_config = QualityConfig(threshold=0.7)
# Result: 68% drafter usage = 68% savings
```

### Pitfall 3: Not Using Domain Routing

```python
# Bad: Generic cascade for specialized domains
agent = CascadeAgent(models=[generic_drafter, generic_verifier])

# Code queries: 50% drafter acceptance (generic model struggles)
# Savings: Only 30%

# Good: Domain-specific cascade
domain_config = DomainConfig(
    domains={"CODE": [code_specialist, generic_verifier]}
)

# Code queries: 90% specialist acceptance
# Savings: 85%
```

### Pitfall 4: Ignoring Caching

```python
# Bad: No caching for repetitive queries
agent = CascadeAgent(models=[drafter, verifier])

# FAQ queries hit models every time
# Cost: Full cost × query count

# Good: Enable caching
cache_config = CacheConfig(enabled=True, ttl=3600)
agent = CascadeAgent(
    models=[drafter, verifier],
    cache_config=cache_config
)

# Cache hits (20-40%): $0 cost
# Effective savings: 68% + (20-40% × 68%) = 82-95%
```

## Cost Optimization Reports

### Monthly Cost Report

```python
def generate_monthly_report(agent):
    analytics = agent.get_analytics()

    report = f"""
    === CascadeFlow Monthly Cost Report ===

    Total Queries: {analytics.total_queries:,}
    Total Cost: ${analytics.total_cost:.2f}
    Avg Cost/Query: ${analytics.avg_cost_per_query:.6f}

    Model Usage:
    - Drafter: {analytics.drafter_usage:.1%}
    - Verifier: {analytics.verifier_usage:.1%}

    Baseline Cost (GPT-4o): ${analytics.baseline_cost:.2f}
    Savings: ${analytics.total_savings:.2f} ({analytics.savings_pct:.1%})

    Top Cost Queries:
    {format_top_queries(analytics.expensive_queries)}

    Recommendations:
    {generate_recommendations(analytics)}
    """

    return report

# Email monthly report to team
send_email(to="team@company.com", subject="CascadeFlow Monthly Report", body=generate_monthly_report(agent))
```

### Optimization Recommendations

```python
def generate_recommendations(analytics):
    recs = []

    if analytics.drafter_acceptance < 0.6:
        recs.append("⚠️ Low drafter acceptance. Consider lowering quality threshold or using stronger drafter.")

    if analytics.verifier_usage > 0.4:
        recs.append("⚠️ High verifier usage. Investigate query complexity or drafter quality.")

    if analytics.avg_quality < 0.9:
        recs.append("⚠️ Quality below target. Raise threshold or improve drafter.")

    if analytics.total_cost > analytics.budget * 0.9:
        recs.append("⚠️ Approaching budget limit. Review high-cost queries.")

    if not recs:
        recs.append("✅ All metrics healthy. No action needed.")

    return "\n".join(recs)
```
