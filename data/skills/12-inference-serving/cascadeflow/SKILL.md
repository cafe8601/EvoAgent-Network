---
name: cascadeflow-model-routing
description: Intelligent LLM model cascading for cost optimization through speculative execution and quality validation. Use when API costs are high and queries have variable complexity. Routes simple queries to cheap models (gpt-4o-mini, Haiku), escalates complex queries to flagship models (GPT-4o, Opus) only when needed. Achieves 40-85% cost reduction with 96% quality retention.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Model Routing, Cost Optimization, Inference, Speculative Execution, Multi-Provider, LangChain, vLLM, Ollama]
dependencies: [cascadeflow>=0.1.0]
---

# CascadeFlow - Intelligent Model Routing for Cost Optimization

Cut AI API costs by 40-85% through intelligent model cascading with quality validation.

## When to Use CascadeFlow

**Use CascadeFlow when:**
- AI API costs are significant and growing
- Queries have variable complexity (simple + complex mixed)
- Want to optimize cost without sacrificing quality
- Using multiple model providers (OpenAI, Anthropic, Groq, etc.)
- Need per-user budget enforcement

**Key features:**
- **40-85% cost savings**: Proven in production
- **2-10x faster**: Small models <50ms vs 500-2000ms
- **<2ms overhead**: Negligible framework latency
- **96% quality retention**: Maintains flagship-level performance
- **3-line integration**: Zero refactoring needed

**Benchmarks**:
| Dataset | Cost Reduction | Quality vs GPT-4o |
|---------|----------------|-------------------|
| MT-Bench | 69% | 96% |
| GSM8K | 93% | 96% |
| MMLU | 52% | 96% |

**Use alternatives instead:**
- **vLLM** (`12-inference-serving/vllm`): Self-host for maximum control
- **Prompt caching**: When queries reuse same context
- **Fine-tuning**: When domain-specific and budget allows
- **Single model**: All queries need flagship reasoning

## Quick Start

### Installation

```bash
# Python (all features)
pip install cascadeflow[all]

# TypeScript
npm install @cascadeflow/core

# LangChain integration
pip install cascadeflow[langchain]
```

### Basic Usage

```python
from cascadeflow import CascadeAgent, ModelConfig

# Define cascade: cheap → expensive
agent = CascadeAgent(models=[
    ModelConfig(
        name="gpt-4o-mini",
        provider="openai",
        cost=0.00015  # $0.15/1M tokens
    ),
    ModelConfig(
        name="gpt-4o",
        provider="openai",
        cost=0.00625  # $6.25/1M tokens
    )
])

# Run - automatically routes to optimal model
result = await agent.run("What is the capital of France?")

print(f"Answer: {result.content}")
print(f"Model: {result.model_used}")    # gpt-4o-mini
print(f"Cost: ${result.total_cost:.6f}")  # $0.000007
print(f"Saved: {result.cost_savings_pct}%")  # 94%
```

### Using Presets

```python
from cascadeflow import CascadeAgent, PRESET_ULTRA_FAST

# Pre-configured for maximum speed + savings
agent = CascadeAgent(preset=PRESET_ULTRA_FAST)
result = await agent.run("Explain quantum computing")
```

**Presets**:
- `PRESET_ULTRA_FAST`: GPT-4o-mini → GPT-4o
- `PRESET_BALANCED`: Haiku → Sonnet
- `PRESET_COST_OPTIMIZED`: Groq → GPT-4o

## How It Works

### Speculative Execution with Quality Validation

```
Query: "What is 2+2?"
    ↓
┌─────────────────────┐
│ Drafter (GPT-4o-mini)│ → Fast, cheap
│ Response: "4"       │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Quality Validator   │
│ - Length: ✓         │
│ - Confidence: 95% ✓ │
│ - Format: ✓         │
└─────────────────────┘
    ↓
Return "4" (cost: $0.000007, 70ms)

────────────────────────────────

Query: "Explain quantum entanglement"
    ↓
┌─────────────────────┐
│ Drafter (GPT-4o-mini)│
│ Response: (vague)   │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Quality Validator   │
│ - Confidence: 45% ✗ │ → Failed
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Verifier (GPT-4o)   │ → Escalate
│ Response: (detailed)│
└─────────────────────┘
    ↓
Return detailed answer (cost: $0.000156, 850ms)
```

## Integration Patterns

### With vLLM (Self-Hosted)

```python
# vLLM server (see 12-inference-serving/vllm)
# vllm serve llama-3.2-3b --port 8000

from cascadeflow import CascadeAgent, ModelConfig

agent = CascadeAgent(models=[
    # Free self-hosted drafter
    ModelConfig(
        name="llama-3.2-3b",
        provider="vllm",
        api_base="http://localhost:8000/v1",
        cost=0.0
    ),
    # Paid cloud verifier
    ModelConfig(
        name="gpt-4o",
        provider="openai",
        cost=0.00625
    )
])

# 70% free local, 30% paid cloud
```

### With Ollama (Local Models)

```bash
ollama pull llama3.2:3b
ollama serve
```

```python
agent = CascadeAgent(models=[
    ModelConfig(
        name="llama3.2:3b",
        provider="ollama",
        api_base="http://localhost:11434",
        cost=0.0
    ),
    ModelConfig(
        name="gpt-4o",
        provider="openai",
        cost=0.00625
    )
])

# Local-first, cloud fallback
```

### With LangChain

```python
from cascadeflow.langchain import CascadeChatModel
from langchain.chains import LLMChain

# Create cascade LLM
llm = CascadeChatModel(
    drafter="gpt-4o-mini",
    verifier="gpt-4o",
    provider="openai"
)

# Use in chains
chain = LLMChain(llm=llm, prompt=prompt_template)
result = chain.run(input="Translate to Spanish: Hello")

# Automatic cascading in LangChain workflows
```

## Domain-Specific Routing

```python
from cascadeflow import DomainConfig, ModelConfig

domain_config = DomainConfig(
    enabled=True,
    domains={
        "CODE": [
            ModelConfig(name="deepseek-coder", provider="ollama", cost=0.0),
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
        ],
        "MATH": [
            ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
            ModelConfig(name="o1-mini", provider="openai", cost=0.015)
        ],
        "DEFAULT": [
            ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
            ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
        ]
    }
)

agent = CascadeAgent(domain_config=domain_config)

# Auto-routes based on detected domain
code_result = await agent.run("Write Python function")  # → CODE domain
math_result = await agent.run("Calculate 123*456")      # → MATH domain
```

**Supported domains**: CODE, MATH, DATA, MEDICAL, LEGAL, FINANCE, CREATIVE, TRANSLATION, SUMMARIZATION

## Advanced Features

### Quality Validation

```python
from cascadeflow import QualityConfig

quality_config = QualityConfig(
    min_length=10,              # Minimum chars
    max_length=5000,            # Maximum chars
    confidence_threshold=0.7,   # Logprob confidence
    semantic_similarity=0.85    # Optional: ML-based
)

agent = CascadeAgent(
    models=[drafter, verifier],
    quality_config=quality_config
)
```

### Budget Enforcement

```python
from cascadeflow import BudgetConfig

budget_config = BudgetConfig(
    daily_limit=10.0,   # $10/day
    monthly_limit=200.0,
    on_limit_exceeded=lambda: notify_admin()
)

agent = CascadeAgent(
    models=[drafter, verifier],
    budget_config=budget_config
)
```

### Cost Tracking

```python
agent = CascadeAgent(models=[drafter, verifier])

# Run queries
for query in queries:
    result = await agent.run(query)

# Analytics
analytics = agent.get_analytics()
print(f"Total cost: ${analytics.total_cost:.4f}")
print(f"Drafter usage: {analytics.drafter_acceptance_rate:.1%}")
print(f"Savings: {analytics.cost_savings_pct:.1%}")
```

## Multi-Provider Cascading

### Cloud + Local Hybrid

```python
agent = CascadeAgent(models=[
    # Local Ollama (free)
    ModelConfig(name="llama3.2:3b", provider="ollama", cost=0.0),

    # Cloud backup (paid)
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
])

# 70% free local processing
# 30% paid cloud for complex queries
```

### Multi-Provider

```python
agent = CascadeAgent(models=[
    # Groq (ultra fast, cheap)
    ModelConfig(name="llama-3.2-3b", provider="groq", cost=0.00005),

    # Anthropic (balanced)
    ModelConfig(name="claude-3-5-haiku", provider="anthropic", cost=0.00125),

    # OpenAI (premium)
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
])

# Cascades through all 3 tiers if needed
```

## Tool Calling Support

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for city",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}}
        }
    }
}]

agent = CascadeAgent(models=[drafter, verifier])

result = await agent.run(
    "What's the weather in Tokyo?",
    tools=tools
)

# Tool calls cascade automatically
```

## Production Deployment

### FastAPI Integration

```python
from fastapi import FastAPI
from cascadeflow import CascadeAgent, ModelConfig

app = FastAPI()

agent = CascadeAgent(models=[
    ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
])

@app.post("/query")
async def query_endpoint(question: str):
    result = await agent.run(question)
    return {
        "answer": result.content,
        "model": result.model_used,
        "cost": result.total_cost
    }
```

### Streaming

```python
agent = CascadeAgent(models=[drafter, verifier])

# Stream responses
async for chunk in agent.stream("Write a poem"):
    print(chunk.content, end="", flush=True)
```

## Best Practices

1. **Choose appropriate drafter**: Should handle 60-70% of queries
2. **Start with threshold 0.7**: Adjust based on acceptance rate
3. **Enable domain routing**: Significant savings for specialized queries
4. **Monitor metrics**: Track drafter acceptance and cost
5. **Combine with caching**: Cache + cascade = maximum savings
6. **Test before production**: Validate on representative queries
7. **Set budget limits**: Prevent surprise costs

## Common Issues

| Issue | Solution |
|-------|----------|
| High verifier usage (>50%) | Lower quality threshold or use better drafter |
| Still expensive | Verify cost config, check drafter is cheaper |
| Quality drop | Enable semantic validation, raise threshold |
| GPT-5 streaming error | Requires org verification (or use non-streaming) |
| Import error | Install with `pip install cascadeflow[all]` |

## Cost Comparison Example

**Before**:
```python
# All queries use GPT-4o
cost_per_1k_queries = $6.25
monthly_cost (100k queries) = $625
```

**After**:
```python
# 70% GPT-4o-mini, 30% GPT-4o
cost_per_1k_queries = $1.98
monthly_cost = $198

Savings: $427/month (68%)
Annual: $5,124
```

## Integration with Other Skills

### With vLLM
See "With vLLM (Self-Hosted)" section above - vLLM as free drafter, cloud as verifier

### With LangChain
See "With LangChain" section - use `CascadeChatModel` in any LangChain chain

### With Daytona Sandbox

```python
from daytona import Daytona
from cascadeflow import CascadeAgent

# Generate code with cascading
agent = CascadeAgent(models=[drafter, verifier])
code_result = await agent.run("Generate Python to parse JSON")

# Execute in sandbox
sandbox = daytona.create(...)
exec_result = sandbox.process.code_run(code_result.content)
```

## References

- **[Routing Strategies](references/routing-strategies.md)** - Domain detection, quality validation, escalation policies
- **[Provider Integration](references/provider-integration.md)** - OpenAI, Anthropic, Groq, Ollama, vLLM setup
- **[Cost Optimization](references/cost-optimization.md)** - Real-world savings, monitoring, ROI analysis

## Resources

- **GitHub**: https://github.com/lemony-ai/cascadeflow
- **Docs**: https://docs.lemony.ai
- **License**: MIT
- **Company**: Lemony.ai (NYC + Zurich)
