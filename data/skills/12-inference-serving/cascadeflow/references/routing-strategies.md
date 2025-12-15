# CascadeFlow Routing Strategies

Advanced routing strategies for intelligent model cascading.

## Basic Routing Strategy

### Simple Two-Model Cascade

```python
from cascadeflow import CascadeAgent, ModelConfig

# Drafter → Verifier pattern
agent = CascadeAgent(models=[
    ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
])

result = await agent.run("What is Python?")
```

**Decision flow**:
```
Query → Drafter → Quality Check → Pass? → Return
                                 ↓ Fail
                           Verifier → Return
```

## Multi-Step Cascading

### Three-Tier Cascade

```python
agent = CascadeAgent(models=[
    # Tier 1: Ultra cheap (Groq)
    ModelConfig(name="llama-3.2-3b", provider="groq", cost=0.00005),

    # Tier 2: Mid-range (Haiku)
    ModelConfig(name="claude-3-5-haiku", provider="anthropic", cost=0.00125),

    # Tier 3: Premium (Sonnet)
    ModelConfig(name="claude-3-5-sonnet", provider="anthropic", cost=0.015)
])

# Cascades through all tiers until quality threshold met
```

**Flow**:
```
Query → Groq → Fail → Haiku → Fail → Sonnet → Success
      60%           25%           15%
```

### Custom Cascade Chain

```python
from cascadeflow import CascadeAgent, CascadeConfig

cascade_config = CascadeConfig(
    max_attempts=3,          # Try up to 3 models
    early_stop=True,        # Stop when quality threshold met
    fallback_to_last=True   # Always use last model if all fail
)

agent = CascadeAgent(
    models=[model1, model2, model3],
    cascade_config=cascade_config
)
```

## Domain-Specific Routing

### Automatic Domain Detection

```python
from cascadeflow import CascadeAgent, DomainConfig, ModelConfig

# Define domain-specific models
domain_config = DomainConfig(
    enabled=True,
    auto_detect=True,
    domains={
        "CODE": [
            ModelConfig(name="deepseek-coder-6.7b", provider="ollama", cost=0.0),
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
        ],
        "MATH": [
            ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
            ModelConfig(name="o1-mini", provider="openai", cost=0.015)
        ],
        "MEDICAL": [
            ModelConfig(name="meditron-7b", provider="vllm", cost=0.0),
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
        ],
        "DEFAULT": [
            ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
        ]
    }
)

agent = CascadeAgent(domain_config=domain_config)

# Automatically routes based on detected domain
code_result = await agent.run("Write a Python function to sort a list")
# → Uses CODE domain → deepseek-coder-6.7b

math_result = await agent.run("What is 123 * 456?")
# → Uses MATH domain → gpt-4o-mini
```

### Supported Domains

| Domain | Keywords | Suggested Specialist |
|--------|----------|---------------------|
| `CODE` | code, function, program, debug | deepseek-coder, codellama |
| `MATH` | calculate, equation, solve | gpt-4o-mini, o1-mini |
| `DATA` | analyze, dataset, statistics | gpt-4o-mini |
| `MEDICAL` | diagnosis, treatment, symptom | meditron, med-palm |
| `LEGAL` | contract, law, regulation | gpt-4o, claude-opus |
| `FINANCE` | trading, stock, portfolio | gpt-4o-mini, finbert |
| `CREATIVE` | story, poem, creative | gpt-4o-mini, claude-sonnet |
| `TRANSLATION` | translate, language | gpt-4o-mini, nllb |
| `SUMMARIZATION` | summarize, tldr | gpt-4o-mini, bart |

### Manual Domain Override

```python
# Override auto-detection
result = await agent.run(
    "Explain recursion",
    domain="CODE"  # Force CODE domain routing
)
```

## Quality Validation Strategies

### Length-Based Validation

```python
from cascadeflow import QualityConfig

quality_config = QualityConfig(
    min_length=10,       # Reject responses < 10 chars
    max_length=5000,     # Reject excessively verbose responses
    ideal_length=500,    # Prefer responses ~500 chars
    length_tolerance=0.3 # ±30% tolerance
)

agent = CascadeAgent(
    models=[drafter, verifier],
    quality_config=quality_config
)
```

### Confidence-Based Validation

```python
quality_config = QualityConfig(
    confidence_threshold=0.7,  # Reject if avg logprob confidence < 70%
    use_logprobs=True
)

# Drafter responses with low confidence automatically escalate
agent = CascadeAgent(models=[drafter, verifier], quality_config=quality_config)
```

### Format Validation

```python
quality_config = QualityConfig(
    expect_json=True,           # Expect valid JSON
    json_schema={               # Validate against schema
        "type": "object",
        "properties": {
            "answer": {"type": "string"},
            "confidence": {"type": "number"}
        },
        "required": ["answer"]
    }
)

# Rejects malformed JSON, escalates to verifier
```

### Semantic Similarity Validation

```python
quality_config = QualityConfig(
    semantic_similarity_threshold=0.85,
    semantic_model="sentence-transformers/all-MiniLM-L6-v2",
    semantic_check_enabled=True
)

agent = CascadeAgent(models=[drafter, verifier], quality_config=quality_config)

# Validates answer semantically aligns with question
# Prevents hallucinations and topic drift
```

## Custom Cascade Strategies

### Hybrid Routing (Rule + ML)

```python
from cascadeflow import CascadeAgent, CustomRouter

class HybridRouter(CustomRouter):
    def should_escalate(self, query, draft_response):
        # Rule 1: Length check
        if len(draft_response) < 20:
            return True

        # Rule 2: Keyword check
        if any(word in query.lower() for word in ["urgent", "critical"]):
            return True

        # Rule 3: ML-based quality
        quality_score = self.ml_validator.score(query, draft_response)
        if quality_score < 0.8:
            return True

        return False

agent = CascadeAgent(
    models=[drafter, verifier],
    router=HybridRouter()
)
```

### Adaptive Threshold

```python
from cascadeflow import AdaptiveConfig

adaptive_config = AdaptiveConfig(
    initial_threshold=0.7,
    learning_rate=0.01,
    feedback_window=100  # Adjust every 100 queries
)

agent = CascadeAgent(
    models=[drafter, verifier],
    adaptive_config=adaptive_config
)

# Threshold adapts based on drafter accuracy over time
# If drafter performs well → lower threshold (more acceptance)
# If drafter performs poorly → raise threshold (more escalation)
```

### Latency-Aware Routing

```python
from cascadeflow import LatencyConfig

latency_config = LatencyConfig(
    max_latency_ms=500,          # Max acceptable latency
    prefer_speed_over_cost=True  # Prioritize speed when close
)

agent = CascadeAgent(
    models=[
        ModelConfig(name="groq-llama", provider="groq", cost=0.00005),  # Ultra fast
        ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
    ],
    latency_config=latency_config
)

# Groq as drafter (70ms avg) → extremely fast responses
```

## User-Tier Cascading

### Tier-Based Model Selection

```python
from cascadeflow import UserProfile, TierConfig

# Define tier configurations
tier_configs = {
    "free": TierConfig(
        models=[
            ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015)
        ],
        daily_budget=0.10,  # $0.10 per day
        max_queries=100
    ),
    "pro": TierConfig(
        models=[
            ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
        ],
        daily_budget=5.0,
        max_queries=1000
    ),
    "enterprise": TierConfig(
        models=[
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625),
            ModelConfig(name="o1", provider="openai", cost=0.06)
        ],
        daily_budget=100.0,
        max_queries=10000
    )
}

def get_cascade_for_user(user_tier):
    config = tier_configs[user_tier]
    return CascadeAgent(
        models=config.models,
        budget_config=config.budget_config
    )

# Usage
user = UserProfile(tier="pro", user_id="user-123")
agent = get_cascade_for_user(user.tier)
result = await agent.run(query, user_id=user.user_id)
```

## Reasoning Model Cascading

### With OpenAI o1/o3

```python
from cascadeflow import CascadeAgent, ModelConfig

# Regular → Reasoning cascade
agent = CascadeAgent(models=[
    # Drafter: Fast standard model
    ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),

    # Mid-tier: Standard flagship
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625),

    # Verifier: Reasoning model (expensive)
    ModelConfig(name="o1", provider="openai", cost=0.06)
])

# Most queries use gpt-4o-mini
# Complex reasoning escalates to o1 (rare, expensive)
result = await agent.run("Solve this complex math proof...")
```

### With Claude 3.7 Extended Thinking

```python
agent = CascadeAgent(models=[
    ModelConfig(name="claude-3-5-haiku", provider="anthropic", cost=0.00125),
    ModelConfig(name="claude-3-5-sonnet", provider="anthropic", cost=0.015),
    ModelConfig(
        name="claude-3-7-sonnet",
        provider="anthropic",
        cost=0.03,
        parameters={"thinking": {"type": "enabled", "budget_tokens": 10000}}
    )
])

# Extended thinking only for hardest queries
```

## Edge Device Cascading

### Local First, Cloud Fallback

```python
from cascadeflow import CascadeAgent, ModelConfig

# Edge device cascade
agent = CascadeAgent(models=[
    # Tier 1: On-device model (TinyLlama)
    ModelConfig(
        name="tinyllama:1.1b",
        provider="ollama",
        api_base="http://localhost:11434",
        cost=0.0
    ),
    # Tier 2: Edge server (Llama-3.2-3B)
    ModelConfig(
        name="llama3.2:3b",
        provider="ollama",
        api_base="http://edge-server:11434",
        cost=0.0
    ),
    # Tier 3: Cloud fallback (GPT-4o-mini)
    ModelConfig(
        name="gpt-4o-mini",
        provider="openai",
        cost=0.00015
    )
])

# 80% on-device, 15% edge server, 5% cloud
# Minimizes cloud costs for edge deployments
```

## Cost-Aware Dynamic Routing

### Budget-Constrained Cascading

```python
from cascadeflow import BudgetAwareCascade

cascade = BudgetAwareCascade(
    models=[cheap, mid, expensive],
    budget_limit=10.0,  # $10 daily limit
    budget_window="daily"
)

# As budget depletes, routing becomes more conservative
# Early in day: more verifier usage
# Near limit: mostly drafter, skip verifier
```

### Time-of-Day Routing

```python
import datetime

def get_cascade_for_time():
    hour = datetime.datetime.now().hour

    if 9 <= hour <= 17:  # Business hours
        # More aggressive escalation (users expect quality)
        return CascadeAgent(
            models=[drafter, verifier],
            quality_config=QualityConfig(threshold=0.8)  # Higher threshold
        )
    else:  # Off-hours
        # More conservative (cost-focused)
        return CascadeAgent(
            models=[drafter, verifier],
            quality_config=QualityConfig(threshold=0.6)  # Lower threshold
        )

agent = get_cascade_for_time()
```

## Advanced Quality Strategies

### Multi-Metric Validation

```python
from cascadeflow import QualityConfig, MultiMetricValidator

class CustomValidator(MultiMetricValidator):
    def validate(self, query, response):
        scores = {
            "length": self.validate_length(response),
            "confidence": self.validate_confidence(response),
            "relevance": self.validate_relevance(query, response),
            "factuality": self.validate_facts(response)
        }

        # Weighted score
        total_score = (
            0.3 * scores["length"] +
            0.3 * scores["confidence"] +
            0.2 * scores["relevance"] +
            0.2 * scores["factuality"]
        )

        return total_score > 0.75

quality_config = QualityConfig(
    custom_validator=CustomValidator()
)
```

### Context-Aware Validation

```python
from cascadeflow import ContextAwareConfig

context_config = ContextAwareConfig(
    consider_user_history=True,
    consider_conversation_context=True
)

# Validation considers:
# - User's past query complexity
# - Current conversation topic depth
# - Historical drafter success rate for this user
```

## Routing Policies

### Conservative Policy (Quality First)

```python
from cascadeflow import RoutingPolicy

conservative_policy = RoutingPolicy(
    name="conservative",
    drafter_acceptance_target=0.4,  # Only 40% drafter usage
    quality_threshold=0.85,          # High quality bar
    escalate_on_uncertainty=True    # Escalate on any doubt
)

agent = CascadeAgent(
    models=[drafter, verifier],
    routing_policy=conservative_policy
)

# Use for: Medical, legal, financial domains
# Result: Higher quality, moderate cost savings (~40%)
```

### Aggressive Policy (Cost First)

```python
aggressive_policy = RoutingPolicy(
    name="aggressive",
    drafter_acceptance_target=0.8,  # 80% drafter usage goal
    quality_threshold=0.6,           # Lower quality bar
    escalate_on_uncertainty=False
)

agent = CascadeAgent(
    models=[drafter, verifier],
    routing_policy=aggressive_policy
)

# Use for: General queries, internal tools, low-stakes
# Result: Maximum cost savings (~85%), acceptable quality
```

### Balanced Policy (Default)

```python
balanced_policy = RoutingPolicy(
    name="balanced",
    drafter_acceptance_target=0.65,  # 65% drafter
    quality_threshold=0.7,
    escalate_on_uncertainty=True
)

# Use for: Most production applications
# Result: Good balance (~60-70% savings, high quality)
```

## Query Classification

### ML-Based Classification

```python
from cascadeflow import QueryClassifier

classifier = QueryClassifier(
    model="sentence-transformers/all-MiniLM-L6-v2",
    categories=["simple", "medium", "complex"]
)

# Classify query complexity
complexity = classifier.classify("Explain quantum entanglement")
# → "complex"

# Route based on classification
if complexity == "simple":
    agent = simple_cascade
elif complexity == "medium":
    agent = medium_cascade
else:
    agent = complex_cascade
```

### Rule-Based Classification

```python
def classify_query(query):
    query_lower = query.lower()

    # Simple patterns
    simple_patterns = ["what is", "define", "who is"]
    if any(pattern in query_lower for pattern in simple_patterns):
        return "simple"

    # Complex patterns
    complex_patterns = ["analyze", "compare", "explain why", "prove"]
    if any(pattern in query_lower for pattern in complex_patterns):
        return "complex"

    # Check length
    if len(query.split()) < 10:
        return "simple"
    elif len(query.split()) > 50:
        return "complex"

    return "medium"

# Use in routing
complexity = classify_query(query)
agent = get_cascade_for_complexity(complexity)
```

## Fallback Strategies

### Graceful Degradation

```python
from cascadeflow import FallbackConfig

fallback_config = FallbackConfig(
    on_all_fail="return_last",     # Return last model's output
    retry_with_modified_prompt=True,
    max_retries=2
)

agent = CascadeAgent(
    models=[drafter, verifier],
    fallback_config=fallback_config
)

# If both models fail, returns best attempt
```

### Circuit Breaker Pattern

```python
from cascadeflow import CircuitBreakerConfig

circuit_config = CircuitBreakerConfig(
    failure_threshold=5,    # Open circuit after 5 failures
    timeout=60,            # Wait 60s before retry
    half_open_threshold=2  # Test with 2 requests
)

agent = CascadeAgent(
    models=[drafter, verifier],
    circuit_config=circuit_config
)

# Prevents cascading failures
# Temporarily disables failing models
```

## Performance Optimization

### Parallel Validation

```python
from cascadeflow import ParallelConfig

parallel_config = ParallelConfig(
    validate_while_drafting=True,  # Overlap validation with generation
    prefetch_verifier=True,        # Warm up verifier connection
    cache_validations=True         # Cache validation results
)

agent = CascadeAgent(
    models=[drafter, verifier],
    parallel_config=parallel_config
)

# Reduces total latency by 20-40%
```

### Caching Integration

```python
from cascadeflow import CacheConfig

cache_config = CacheConfig(
    enabled=True,
    ttl=3600,  # 1 hour
    cache_backend="redis",
    redis_url="redis://localhost:6379"
)

agent = CascadeAgent(
    models=[drafter, verifier],
    cache_config=cache_config
)

# Identical queries return cached results
# Combined with cascading = maximum savings
```

## Monitoring and Analytics

### Real-Time Metrics

```python
from cascadeflow import MetricsConfig

metrics_config = MetricsConfig(
    track_costs=True,
    track_latency=True,
    track_quality=True,
    track_escalation_rate=True,
    export_to_prometheus=True
)

agent = CascadeAgent(
    models=[drafter, verifier],
    metrics_config=metrics_config
)

# Access metrics
metrics = agent.get_metrics()
print(f"Drafter acceptance: {metrics.drafter_acceptance_rate}")
print(f"Average cost: ${metrics.avg_cost_per_query:.6f}")
print(f"P95 latency: {metrics.p95_latency_ms}ms")
```

### OpenTelemetry Export

```python
from cascadeflow import TelemetryConfig

telemetry_config = TelemetryConfig(
    enabled=True,
    export_traces=True,
    export_metrics=True,
    otlp_endpoint="http://localhost:4318"
)

agent = CascadeAgent(
    models=[drafter, verifier],
    telemetry_config=telemetry_config
)

# Exports to Jaeger, Grafana, DataDog, etc.
```

## Best Practices

### 1. Drafter Selection

**Good drafters** (60-70% acceptance):
- gpt-4o-mini (general)
- claude-3-5-haiku (balanced)
- groq-llama-3.2-3b (ultra fast)
- deepseek-coder-6.7b (code)

**Poor drafters** (<40% acceptance):
- tinyllama-1.1b (too weak)
- gpt-3.5-turbo (outdated)

### 2. Threshold Tuning

```python
# Start conservative
quality_config = QualityConfig(threshold=0.8)

# Monitor drafter acceptance rate
# Target: 60-70% acceptance

# If <60%: Lower threshold (0.75 → 0.7)
# If >80%: Raise threshold (0.7 → 0.75)
```

### 3. Domain Matching

Use domain-specific models when possible:

```python
# Good: Domain specialist as drafter
CODE: deepseek-coder → gpt-4o
MATH: gpt-4o-mini → o1-mini
MEDICAL: meditron → gpt-4o

# Bad: Generic drafter for specialized domain
CODE: gpt-4o-mini → gpt-4o  # Misses specialist advantage
```

### 4. Cost Monitoring

```python
# Set up alerts
from cascadeflow import CostAlert

alert_config = CostAlert(
    daily_threshold=50.0,
    hourly_threshold=5.0,
    on_threshold_exceeded=lambda: send_alert()
)

agent = CascadeAgent(
    models=[drafter, verifier],
    alert_config=alert_config
)
```

### 5. Quality Validation Trade-offs

| Validation Type | Latency | Cost | Accuracy |
|-----------------|---------|------|----------|
| Length only | +0.1ms | Free | 85% |
| + Confidence | +0.5ms | Free | 90% |
| + Format | +1ms | Free | 93% |
| + Semantic | +50ms | ~80MB model | 96% |

**Recommendation**: Start with Length + Confidence, add Semantic only if needed
