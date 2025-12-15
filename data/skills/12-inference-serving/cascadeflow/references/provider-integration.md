# CascadeFlow Provider Integration Guide

Complete guide for integrating CascadeFlow with various AI providers.

## OpenAI

### Basic Setup

```python
from cascadeflow import CascadeAgent, ModelConfig
import os

agent = CascadeAgent(models=[
    ModelConfig(
        name="gpt-4o-mini",
        provider="openai",
        api_key=os.environ["OPENAI_API_KEY"],
        cost=0.00015  # $0.15 per 1M input tokens
    ),
    ModelConfig(
        name="gpt-4o",
        provider="openai",
        api_key=os.environ["OPENAI_API_KEY"],
        cost=0.00625  # $6.25 per 1M input tokens
    )
])
```

### OpenAI Reasoning Models

```python
# o1-mini → o1 cascade
agent = CascadeAgent(models=[
    ModelConfig(name="o1-mini", provider="openai", cost=0.015),
    ModelConfig(name="o1", provider="openai", cost=0.06)
])

# o3-mini → o3 (when available)
agent = CascadeAgent(models=[
    ModelConfig(name="o3-mini", provider="openai", cost=0.02),
    ModelConfig(name="o3", provider="openai", cost=0.08)
])
```

### OpenAI Streaming

```python
agent = CascadeAgent(models=[
    ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
])

# Stream responses
async for chunk in agent.stream("Write a story"):
    print(chunk.content, end="")

# Cost available after stream completes
print(f"\nCost: ${chunk.total_cost:.6f}")
```

**Note**: GPT-5 streaming requires organization verification (~15 min). Non-streaming works for all users.

## Anthropic

### Claude Models

```python
from cascadeflow import CascadeAgent, ModelConfig

agent = CascadeAgent(models=[
    # Haiku (fast, cheap)
    ModelConfig(
        name="claude-3-5-haiku-20241022",
        provider="anthropic",
        api_key=os.environ["ANTHROPIC_API_KEY"],
        cost=0.00125
    ),
    # Sonnet (powerful)
    ModelConfig(
        name="claude-3-5-sonnet-20241022",
        provider="anthropic",
        api_key=os.environ["ANTHROPIC_API_KEY"],
        cost=0.015
    )
])
```

### Claude Extended Thinking

```python
# Haiku → Sonnet with extended thinking
agent = CascadeAgent(models=[
    ModelConfig(name="claude-3-5-haiku", provider="anthropic", cost=0.00125),
    ModelConfig(
        name="claude-3-7-sonnet",
        provider="anthropic",
        cost=0.03,
        parameters={
            "thinking": {
                "type": "enabled",
                "budget_tokens": 10000
            }
        }
    )
])

# Extended thinking only activated for complex queries
```

## Groq (Ultra-Fast Inference)

### Groq as Drafter

```python
agent = CascadeAgent(models=[
    # Groq: 70ms average latency
    ModelConfig(
        name="llama-3.2-3b-preview",
        provider="groq",
        api_key=os.environ["GROQ_API_KEY"],
        cost=0.00005  # Very cheap
    ),
    # OpenAI: Fallback for quality
    ModelConfig(
        name="gpt-4o",
        provider="openai",
        cost=0.00625
    )
])

# Ultra-fast responses for simple queries
# Quality fallback for complex
```

## Ollama (Local Models)

### Basic Ollama Setup

```bash
# Start Ollama
ollama serve

# Pull models
ollama pull llama3.2:3b
ollama pull llama3.2:1b
```

```python
from cascadeflow import CascadeAgent, ModelConfig

# Local Ollama cascade
agent = CascadeAgent(models=[
    ModelConfig(
        name="llama3.2:1b",
        provider="ollama",
        api_base="http://localhost:11434",
        cost=0.0  # Free (self-hosted)
    ),
    ModelConfig(
        name="llama3.2:3b",
        provider="ollama",
        api_base="http://localhost:11434",
        cost=0.0
    )
])

# Both free - cascade based on quality, not cost
```

### Ollama + Cloud Hybrid

```python
# Local drafter, cloud verifier
agent = CascadeAgent(models=[
    # Ollama (free, local)
    ModelConfig(
        name="llama3.2:3b",
        provider="ollama",
        api_base="http://localhost:11434",
        cost=0.0
    ),
    # OpenAI (paid, cloud)
    ModelConfig(
        name="gpt-4o",
        provider="openai",
        api_key=openai_key,
        cost=0.00625
    )
])

# 70% free local processing
# 30% paid cloud for complex queries
```

### Multi-Instance Ollama

```python
# Separate Ollama instances for drafter/verifier
agent = CascadeAgent(models=[
    ModelConfig(
        name="llama3.2:3b",
        provider="ollama",
        api_base="http://ollama-drafter:11434",  # Dedicated instance
        cost=0.0
    ),
    ModelConfig(
        name="qwen2.5:7b",
        provider="ollama",
        api_base="http://ollama-verifier:11434",  # Separate instance
        cost=0.0
    )
])
```

## vLLM (Self-Hosted Serving)

### vLLM Integration

```bash
# Start vLLM server (see 12-inference-serving/vllm/SKILL.md)
vllm serve meta-llama/Llama-3.2-3B-Instruct \
    --dtype bfloat16 \
    --max-model-len 4096 \
    --port 8000
```

```python
from cascadeflow import CascadeAgent, ModelConfig

# vLLM drafter, cloud verifier
agent = CascadeAgent(models=[
    ModelConfig(
        name="llama-3.2-3b",
        provider="vllm",
        api_base="http://localhost:8000/v1",
        api_key="not-needed",
        cost=0.0  # Self-hosted
    ),
    ModelConfig(
        name="gpt-4o",
        provider="openai",
        api_key=openai_key,
        cost=0.00625
    )
])

# Self-hosted for 70% queries (free)
# Cloud for 30% complex queries
```

### Multi-Instance vLLM

```python
# Run multiple vLLM instances with different models
# Instance 1: vllm serve llama-3.2-3b --port 8000
# Instance 2: vllm serve qwen2.5-7b --port 8001

agent = CascadeAgent(models=[
    ModelConfig(
        name="llama-3.2-3b",
        provider="vllm",
        api_base="http://localhost:8000/v1",
        cost=0.0
    ),
    ModelConfig(
        name="qwen2.5-7b",
        provider="vllm",
        api_base="http://localhost:8001/v1",
        cost=0.0
    )
])
```

## Together AI

```python
agent = CascadeAgent(models=[
    ModelConfig(
        name="meta-llama/Meta-Llama-3.2-3B-Instruct-Turbo",
        provider="together",
        api_key=os.environ["TOGETHER_API_KEY"],
        cost=0.00006
    ),
    ModelConfig(
        name="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        provider="together",
        api_key=os.environ["TOGETHER_API_KEY"],
        cost=0.00088
    )
])
```

## HuggingFace Inference

```python
agent = CascadeAgent(models=[
    ModelConfig(
        name="meta-llama/Llama-3.2-3B-Instruct",
        provider="huggingface",
        api_key=os.environ["HF_API_KEY"],
        cost=0.0  # Serverless tier often free
    ),
    ModelConfig(
        name="gpt-4o",
        provider="openai",
        cost=0.00625
    )
])
```

## LiteLLM (100+ Providers)

### Using LiteLLM Proxy

```bash
# Install LiteLLM
pip install 'litellm[proxy]'

# Start proxy
litellm --model gpt-4o-mini --model gpt-4o

# Proxy runs on http://localhost:4000
```

```python
from cascadeflow import CascadeAgent, ModelConfig

# Use LiteLLM proxy for unified interface
agent = CascadeAgent(models=[
    ModelConfig(
        name="gpt-4o-mini",
        provider="litellm",
        api_base="http://localhost:4000",
        cost=0.00015
    ),
    ModelConfig(
        name="gpt-4o",
        provider="litellm",
        api_base="http://localhost:4000",
        cost=0.00625
    )
])
```

### LiteLLM for Exotic Providers

```python
# Access 100+ providers through LiteLLM
# Bedrock, Azure, Vertex AI, Cohere, etc.

agent = CascadeAgent(models=[
    ModelConfig(
        name="bedrock/amazon.titan-text-express-v1",
        provider="litellm",
        cost=0.0002
    ),
    ModelConfig(
        name="azure/gpt-4o",
        provider="litellm",
        cost=0.00625
    )
])
```

## Provider-Specific Features

### OpenAI Structured Outputs

```python
from pydantic import BaseModel

class Answer(BaseModel):
    answer: str
    confidence: float
    sources: list[str]

agent = CascadeAgent(models=[
    ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
])

result = await agent.run(
    "Who won the 2024 World Series?",
    response_format=Answer
)

# Both drafter and verifier return structured output
```

### Anthropic Prompt Caching

```python
# Use with cascadeflow for maximum savings
agent = CascadeAgent(models=[
    ModelConfig(
        name="claude-3-5-haiku",
        provider="anthropic",
        cost=0.00125,
        cache_control=True  # Enable prompt caching
    ),
    ModelConfig(
        name="claude-3-5-sonnet",
        provider="anthropic",
        cost=0.015,
        cache_control=True
    )
])

# Combine caching + cascading = 90%+ savings
```

## Error Handling

### Provider Fallback

```python
from cascadeflow import CascadeAgent, ErrorConfig

error_config = ErrorConfig(
    retry_on_error=True,
    max_retries=3,
    fallback_on_provider_error=True
)

agent = CascadeAgent(
    models=[
        ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
        ModelConfig(name="claude-3-5-haiku", provider="anthropic", cost=0.00125),  # Fallback
        ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
    ],
    error_config=error_config
)

# If OpenAI fails, tries Anthropic automatically
```

### Rate Limit Handling

```python
from cascadeflow import RateLimitConfig

rate_limit_config = RateLimitConfig(
    enabled=True,
    requests_per_minute=100,
    on_rate_limit="wait",  # or "skip", "fallback"
    backoff_strategy="exponential"
)

agent = CascadeAgent(
    models=[drafter, verifier],
    rate_limit_config=rate_limit_config
)
```

## Multi-Region Deployment

### Geographic Routing

```python
from cascadeflow import CascadeAgent, ModelConfig

# US users
us_agent = CascadeAgent(models=[
    ModelConfig(
        name="gpt-4o-mini",
        provider="openai",
        api_base="https://api.openai.com/v1",  # US endpoint
        cost=0.00015
    ),
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
])

# EU users (GDPR compliance)
eu_agent = CascadeAgent(models=[
    ModelConfig(
        name="claude-3-5-haiku",
        provider="anthropic",
        api_base="https://api.anthropic.com/v1",  # EU data residency
        cost=0.00125
    ),
    ModelConfig(name="claude-3-5-sonnet", provider="anthropic", cost=0.015)
])

# Route based on user location
agent = us_agent if user.region == "US" else eu_agent
```

## Provider Cost Reference

### Cost Comparison (Per 1M Input Tokens)

| Provider | Model | Cost | Speed | Use As |
|----------|-------|------|-------|--------|
| **Groq** | llama-3.2-3b | $0.00005 | ⚡⚡⚡ | Ultra-fast drafter |
| **OpenAI** | gpt-4o-mini | $0.00015 | ⚡⚡ | General drafter |
| **Anthropic** | claude-3-5-haiku | $0.00125 | ⚡⚡ | Balanced drafter |
| **Together** | llama-3.2-3b | $0.00006 | ⚡⚡⚡ | Fast drafter |
| **Ollama** | llama3.2:3b | $0.00000 | ⚡ | Free local drafter |
| **vLLM** | llama-3.2-3b | $0.00000 | ⚡⚡ | Free self-hosted |
| **OpenAI** | gpt-4o | $0.00625 | ⚡ | Verifier |
| **Anthropic** | claude-3-5-sonnet | $0.01500 | ⚡ | Premium verifier |
| **OpenAI** | o1 | $0.06000 | 🐌 | Reasoning verifier |

### Output Pricing

| Provider | Model | Output Cost (per 1M tokens) |
|----------|-------|----------------------------|
| OpenAI | gpt-4o-mini | $0.00060 |
| OpenAI | gpt-4o | $0.01875 |
| Anthropic | haiku | $0.00625 |
| Anthropic | sonnet | $0.07500 |
| Groq | llama-3.2-3b | $0.00005 |

**Note**: Output tokens typically 2-4x input cost

## Provider-Specific Configuration

### OpenAI Advanced Options

```python
agent = CascadeAgent(models=[
    ModelConfig(
        name="gpt-4o-mini",
        provider="openai",
        cost=0.00015,
        parameters={
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "logprobs": True,  # Enable for confidence scoring
            "top_logprobs": 3
        }
    )
])
```

### Anthropic Advanced Options

```python
agent = CascadeAgent(models=[
    ModelConfig(
        name="claude-3-5-haiku",
        provider="anthropic",
        cost=0.00125,
        parameters={
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_tokens": 1024
        }
    )
])
```

### Groq Optimization

```python
# Groq optimized for speed
agent = CascadeAgent(models=[
    ModelConfig(
        name="llama-3.2-3b-preview",
        provider="groq",
        cost=0.00005,
        parameters={
            "temperature": 0.5,  # Lower for consistency
            "max_tokens": 512    # Limit for speed
        }
    )
])
```

## Authentication Patterns

### Environment Variables

```python
import os

# Set API keys
os.environ["OPENAI_API_KEY"] = "sk-..."
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
os.environ["GROQ_API_KEY"] = "gsk_..."

# CascadeFlow auto-detects from environment
agent = CascadeAgent(models=[
    ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
    ModelConfig(name="claude-3-5-haiku", provider="anthropic", cost=0.00125)
])
# No explicit api_key needed
```

### Explicit API Keys

```python
agent = CascadeAgent(models=[
    ModelConfig(
        name="gpt-4o-mini",
        provider="openai",
        api_key="sk-proj-...",  # Explicit key
        cost=0.00015
    )
])
```

### Key Rotation

```python
from cascadeflow import KeyRotationConfig

# Rotate between multiple API keys
key_config = KeyRotationConfig(
    keys=["sk-proj-key1", "sk-proj-key2", "sk-proj-key3"],
    strategy="round_robin"  # or "least_used", "random"
)

agent = CascadeAgent(
    models=[
        ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            key_rotation=key_config,
            cost=0.00015
        )
    ]
)
```

## Provider Availability

### Health Check

```python
from cascadeflow import ProviderHealthCheck

# Check provider status before cascading
health = ProviderHealthCheck(
    check_interval=60,  # Check every 60s
    timeout=5           # 5s timeout
)

agent = CascadeAgent(
    models=[drafter, verifier],
    health_check=health
)

# Automatically skips unhealthy providers
```

### Auto-Failover

```python
# Multiple providers for same tier
agent = CascadeAgent(models=[
    # Drafter tier - multiple providers
    [
        ModelConfig(name="gpt-4o-mini", provider="openai", cost=0.00015),
        ModelConfig(name="claude-3-5-haiku", provider="anthropic", cost=0.00125)
    ],
    # Verifier tier
    ModelConfig(name="gpt-4o", provider="openai", cost=0.00625)
])

# If OpenAI drafter fails → tries Anthropic drafter
```

## TypeScript Provider Integration

### OpenAI (TypeScript)

```typescript
import { CascadeAgent, ModelConfig } from "@cascadeflow/core";

const agent = new CascadeAgent({
  models: [
    {
      name: "gpt-4o-mini",
      provider: "openai",
      apiKey: process.env.OPENAI_API_KEY,
      cost: 0.00015
    },
    {
      name: "gpt-4o",
      provider: "openai",
      apiKey: process.env.OPENAI_API_KEY,
      cost: 0.00625
    }
  ]
});

const result = await agent.run("What is TypeScript?");
console.log(`Cost: $${result.totalCost}`);
```

### Anthropic (TypeScript)

```typescript
const agent = new CascadeAgent({
  models: [
    {
      name: "claude-3-5-haiku-20241022",
      provider: "anthropic",
      apiKey: process.env.ANTHROPIC_API_KEY,
      cost: 0.00125
    },
    {
      name: "claude-3-5-sonnet-20241022",
      provider: "anthropic",
      apiKey: process.env.ANTHROPIC_API_KEY,
      cost: 0.015
    }
  ]
});
```

### Vercel Edge Runtime

```typescript
// Edge-compatible cascading
import { CascadeAgent } from "@cascadeflow/core/edge";

export const runtime = "edge";

export default async function handler(req: Request) {
  const agent = new CascadeAgent({
    models: [
      { name: "gpt-4o-mini", provider: "openai", cost: 0.00015 },
      { name: "gpt-4o", provider: "openai", cost: 0.00625 }
    ]
  });

  const { question } = await req.json();
  const result = await agent.run(question);

  return Response.json({
    answer: result.content,
    cost: result.totalCost
  });
}
```

## Custom Provider Integration

### Add New Provider

```python
from cascadeflow.providers import BaseProvider

class CustomProvider(BaseProvider):
    def __init__(self, api_key, api_base):
        self.api_key = api_key
        self.api_base = api_base

    async def generate(self, messages, **kwargs):
        # Your custom API call
        response = await self.call_api(messages)
        return response

    def calculate_cost(self, usage):
        # Your custom cost calculation
        return usage.input_tokens * self.input_cost + \
               usage.output_tokens * self.output_cost

# Register
from cascadeflow import register_provider

register_provider("my_provider", CustomProvider)

# Use
agent = CascadeAgent(models=[
    ModelConfig(
        name="my-model",
        provider="my_provider",
        api_key="...",
        cost=0.001
    )
])
```

## Troubleshooting

### Provider Connection Issues

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check provider connectivity
from cascadeflow import test_provider_connection

test_provider_connection("openai", api_key=openai_key)
test_provider_connection("anthropic", api_key=anthropic_key)
```

### API Key Issues

```python
# Verify API keys
from cascadeflow import validate_api_key

valid = validate_api_key("openai", api_key)
if not valid:
    print("Invalid OpenAI API key")
```

### Cost Tracking Issues

```python
# Ensure cost is set correctly
agent = CascadeAgent(models=[
    ModelConfig(
        name="gpt-4o-mini",
        provider="openai",
        cost=0.00015  # Must match actual pricing
    )
])

# Verify calculated costs
result = await agent.run("test")
print(f"Input tokens: {result.usage.input_tokens}")
print(f"Output tokens: {result.usage.output_tokens}")
print(f"Calculated cost: ${result.total_cost:.6f}")
```
