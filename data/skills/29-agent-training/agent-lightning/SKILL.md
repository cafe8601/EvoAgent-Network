---
name: agent-lightning-rl-training
description: Reinforcement learning framework enabling RL-based training for ANY AI agent with complete decoupling between agent execution and training. Use when you need to optimize existing agents built with LangChain, OpenAI SDK, AutoGen, or custom code without modification. Supports multi-agent selective optimization and hierarchical RL.
version: 1.0.0
author: Orchestra Research
license: Apache-2.0
tags: [Agent Training, Reinforcement Learning, RL, GRPO, Multi-Agent, LangChain, OpenAI SDK, AutoGen, LLM Training]
dependencies: [agent-lightning, torch>=2.0.0, transformers>=4.40.0]
---

# Agent Lightning - Train ANY AI Agents with RL

Microsoft Research's framework for RL-based training of LLMs in ANY AI agent with ZERO code modifications.

## When to Use Agent Lightning

**Use Agent Lightning when:**
- Need to optimize existing agents via reinforcement learning
- Agents built with LangChain, OpenAI SDK, AutoGen, or custom code
- Want to improve agent performance on private/domain-specific data
- Multi-agent systems requiring selective optimization
- Tool-using agents needing better action policies

**Key features:**
- **Complete decoupling**: Agent execution ↔ RL training fully separated
- **ZERO code modification**: Apply to existing agents transparently
- **Unified data interface**: MDP formulation works with ANY agent
- **Hierarchical RL**: LightningRL algorithm with credit assignment
- **OpenTelemetry integration**: Auto-instrumentation for trajectory collection

**Metrics**:
- **Text-to-SQL**: 18% → 59% (+220% improvement)
- **RAG**: 12% → 22% (+83% improvement)
- **Math QA**: 30% → 75% (+150% improvement)

**Use alternatives instead:**
- **Supervised fine-tuning**: When you have step-by-step annotations
- **Prompt engineering**: For quick improvements without training
- **ACE (Context Engineering)**: For optimizing system prompts (see `14-agents/ace`)
- **Traditional RL**: For single-turn tasks (math, reasoning)

## Quick Start

### Installation

```bash
git clone https://github.com/microsoft/agent-lightning.git
cd agent-lightning && pip install -e .

# Install RL backend
pip install verl-nightly
```

**Requirements**: Python 3.10+, PyTorch 2.0+, CUDA 11.8+

### Basic Training

```python
from agent_lightning import Client

# 1. Define agent function
def my_agent(resource, task):
    """
    resource: Contains model_api endpoint
    task: Data from JSONL (task.question, task.ground_truth, etc.)
    """
    # Use resource.model_api for LLM calls
    answer = your_agent_logic(resource.model_api, task.question)

    # Return scalar reward
    reward = 1.0 if answer == task.ground_truth else 0.0
    return reward

# 2. Train
client = Client("http://localhost:8000")
client.upload_data("train.jsonl", test_file="test.jsonl")
result = client.train(my_agent, nworkers=4)
```

**Data format**:
```json
{"question": "What is 2+2?", "ground_truth": "4"}
```

## Core Architecture

### Training-Agent Disaggregation

```
┌─────────────────────┐         ┌──────────────────────┐
│  Lightning Server   │ ←─API─→ │  Lightning Client    │
│  (GPU cluster)      │         │  (Agent runtime)     │
│  - RL Training      │         │  - Agent execution   │
│  - Model updates    │         │  - Data collection   │
└─────────────────────┘         └──────────────────────┘
```

**Benefits**:
- Agent runs independently (no GPU colocation)
- RL framework is agent-agnostic
- Easy horizontal scaling

### Unified Data Interface (MDP)

Agent execution as Markov Decision Process:

```python
# Trajectory = sequence of transitions
trajectory = [
    (input_1, output_1, reward_1),  # Step 1: Generate query
    (input_2, output_2, reward_2)   # Step 2: Generate answer
]

# Each transition:
# - input: LLM context/prompt
# - output: LLM generated response
# - reward: Quality score
```

### LightningRL Algorithm

Hierarchical RL with credit assignment:

1. **Credit Assignment**: Distribute episode return R across actions
2. **Token Optimization**: Use single-turn RL (GRPO, PPO) on each action

## Framework Integration

### LangChain

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_anthropic import ChatAnthropic

def langchain_agent(resource, task):
    # Use Lightning Server endpoint
    llm = ChatAnthropic(base_url=resource.model_api, api_key="not-used")

    # Your existing agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)

    result = executor.invoke({"input": task.question})
    reward = evaluate(result["output"], task.ground_truth)
    return reward

# Train
client.train(langchain_agent, nworkers=8)
```

### OpenAI Agents SDK

```python
from openai import OpenAI

def openai_agent(resource, task):
    # Use Lightning Server endpoint
    client = OpenAI(base_url=resource.model_api, api_key="not-used")

    # Multi-turn RAG
    query = client.chat.completions.create(
        model="llama-3.2-3b",
        messages=[{"role": "user", "content": f"Query: {task.question}"}]
    ).choices[0].message.content

    docs = retriever.search(query)

    answer = client.chat.completions.create(
        model="llama-3.2-3b",
        messages=[{"role": "user", "content": f"Q: {task.question}\nDocs: {docs}"}]
    ).choices[0].message.content

    reward = compute_f1(answer, task.ground_truth)
    return reward

client.train(openai_agent)
```

### AutoGen

```python
from autogen import ConversableAgent

def autogen_agent(resource, task):
    config_list = [{
        "base_url": resource.model_api,
        "api_key": "not-used",
        "model": "llama-3.2-3b"
    }]

    assistant = ConversableAgent(
        name="assistant",
        llm_config={"config_list": config_list}
    )

    response = assistant.generate_reply(
        messages=[{"role": "user", "content": task.question}]
    )

    reward = evaluate(response, task.ground_truth)
    return reward

client.train(autogen_agent)
```

## Multi-Agent Selective Optimization

Optimize specific agents in multi-agent workflow:

```python
def sql_multiagent(resource, task):
    llm = ChatAnthropic(base_url=resource.model_api)

    # Agent 1: SQL Writer (optimize ✓)
    sql = sql_writer_agent(llm, task.question)

    # Execute
    result = execute_sql(sql)

    # Agent 2: Checker (optimize ✓)
    is_valid = checker_agent(llm, sql, result)

    if not is_valid:
        # Agent 3: Rewriter (optimize ✓)
        sql = rewriter_agent(llm, sql, result)
        result = execute_sql(sql)

    # Answer generator (optimize ✓)
    answer = answer_agent(llm, result)

    reward = 1.0 if answer == task.ground_truth else 0.0
    return reward

# All LLM calls automatically optimized
client.train(sql_multiagent)
```

## Advanced Features

### Automatic Intermediate Rewarding (AIR)

Assign rewards to intermediate steps:

```python
from agent_lightning.runtime import air

# Define reward rules
@air.on_tool_success
def reward_tool_success(tool_name, output):
    return 0.3  # Partial reward

@air.on_tool_failure
def penalize_failure(tool_name, error):
    return -0.2  # Penalty

def agent_with_air(resource, task):
    # AIR automatically assigns intermediate rewards
    # based on tool execution status
    result = my_agent.run(resource.model_api, task)
    final_reward = evaluate(result, task.ground_truth)
    return final_reward
```

### Custom Reward Functions

```python
def agent_with_custom_reward(resource, task):
    result = my_agent.run(resource.model_api, task)

    # Composite reward
    correctness = 1.0 if result.answer == task.ground_truth else 0.0
    efficiency = 1.0 / max(result.num_steps, 1)
    tool_success = result.successful_tools / max(result.total_tools, 1)

    reward = 0.7 * correctness + 0.2 * efficiency + 0.1 * tool_success
    return reward
```

## Server Configuration

### Start Lightning Server

```bash
# Set environment
export LIGHTNING_MODEL_PATH="meta-llama/Llama-3.2-3B-Instruct"
export LIGHTNING_RL_ALGORITHM="grpo"

# Start server
python -m agent_lightning.server \
    --model $LIGHTNING_MODEL_PATH \
    --algorithm $LIGHTNING_RL_ALGORITHM \
    --gpus 4 \
    --port 8000
```

### Training Config

```yaml
# config.yaml
model:
  name: "meta-llama/Llama-3.2-3B-Instruct"

training:
  algorithm: "grpo"
  learning_rate: 5e-7
  batch_size: 256
  group_size: 8
  kl_coef: 0.001
  epochs: 1

runtime:
  nworkers: 8
  auto_instrumentation: true
  air_enabled: true
```

## Integration with Existing Skills

### With 27-ai-agent-sandbox (Daytona)

```python
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams

def code_agent_with_sandbox(resource, task):
    # Create sandbox
    daytona = Daytona(DaytonaConfig(api_key=key))
    sandbox = daytona.create(CreateSandboxFromSnapshotParams(language="python"))

    try:
        # Generate code
        llm = ChatAnthropic(base_url=resource.model_api)
        code = llm.invoke(f"Code for: {task.question}").content

        # Execute in sandbox
        result = sandbox.process.code_run(code)

        # Reward
        exec_reward = 0.3 if result.exit_code == 0 else 0.0
        correct_reward = 0.7 if result.result == task.ground_truth else 0.0
        return exec_reward + correct_reward
    finally:
        sandbox.delete()
```

### With 14-agents/langchain

See Quick Start examples above - Lightning works seamlessly with all LangChain patterns.

### With 28-agent-memory/beads

```python
import subprocess

def agent_with_beads(resource, task):
    # Track in beads
    subprocess.run(["bd", "update", task.beads_id, "--status", "in_progress"])

    # Train agent
    result = my_agent.run(resource.model_api, task)
    reward = evaluate(result, task.ground_truth)

    # Update beads
    if reward > 0.8:
        subprocess.run(["bd", "close", task.beads_id, "--reason", "Solved"])

    return reward
```

## Best Practices

1. **Start small**: 3B-7B models for experiments
2. **Verify baseline**: Test agent without RL first
3. **Meaningful rewards**: Use 0/1 or domain metrics
4. **Monitor curves**: Check reward stability
5. **Enable AIR**: Helps with sparse rewards
6. **Scale gradually**: 4 → 8 → 16 workers
7. **Save checkpoints**: Periodic saves essential
8. **Test separately**: Always use held-out test set

## Common Issues

| Issue | Solution |
|-------|----------|
| Connection timeout | Verify `AGENT_LIGHTNING_SERVER_URL` |
| OOM during training | Reduce `batch_size`, use gradient accumulation |
| Unstable training | Lower `learning_rate`, increase `kl_coef` |
| Rewards always 0 | Check reward function and data quality |
| Agent crashes | Add error handling, enable robust mode |

## Performance Benchmarks

| Task | Framework | Baseline | After RL | Gain |
|------|-----------|----------|----------|------|
| Text-to-SQL | LangChain | 20% | 60% | **+200%** |
| RAG | OpenAI SDK | 12% | 22% | **+83%** |
| Math QA | AutoGen | 30% | 75% | **+150%** |

## References

- **[API Reference](references/api-reference.md)** - Complete API documentation
- **[Integration Patterns](references/integration-patterns.md)** - Framework-specific guides
- **[Case Studies](references/case-studies.md)** - Real-world applications and results

## Resources

- **GitHub**: https://github.com/microsoft/agent-lightning
- **Paper**: arXiv:2508.03680v1 (Microsoft Research, Aug 2025)
- **VeRL Backend**: https://github.com/volcengine/verl
- **Microsoft Research**: https://www.microsoft.com/research
