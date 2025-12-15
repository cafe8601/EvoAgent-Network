# Agent Lightning API Reference

Complete API documentation for Agent Lightning framework.

## Client API

### Client Class

Primary interface for interacting with Lightning Server.

```python
from agent_lightning import Client

client = Client(
    server_url: str,              # Lightning Server URL
    timeout: int = 300,           # Request timeout in seconds
    max_retries: int = 3,         # Max retry attempts
    verify_ssl: bool = True       # SSL verification
)
```

**Methods:**

#### upload_data()

Upload training and test datasets.

```python
client.upload_data(
    train_file: str,              # Path to training JSONL file
    test_file: str = None,        # Optional test file
    data_id: str = None          # Optional custom data ID
) -> str  # Returns data_id
```

**Data Format (JSONL):**
```json
{"question": "What is 2+2?", "ground_truth": "4", "context": "..."}
{"question": "Capital of France?", "ground_truth": "Paris"}
```

**Supported fields**:
- `question` (required): Task input
- `ground_truth` (optional): Reference answer for evaluation
- Any custom fields accessible in `task` object

#### train()

Start RL training with agent function.

```python
client.train(
    agent_func: Callable[[Resource, Task], float],  # Agent function
    nworkers: int = -1,           # Number of parallel workers (-1 = auto)
    epochs: int = 1,              # Training epochs
    batch_size: int = 32,         # Batch size per update
    data_id: str = None,          # Use pre-uploaded data
    checkpoint_dir: str = None,   # Save checkpoints
    eval_interval: int = 50       # Evaluate every N steps
) -> TrainingResult
```

**Agent Function Signature:**
```python
def agent_func(resource: Resource, task: Task) -> float:
    """
    Args:
        resource: Contains model_api endpoint and metadata
        task: Task data loaded from JSONL
    Returns:
        reward: Scalar reward (higher = better)
    """
    # Your agent logic
    return reward
```

#### evaluate()

Evaluate trained model on test set.

```python
client.evaluate(
    agent_func: Callable,
    test_file: str = None,
    checkpoint: str = None,
    nworkers: int = 4
) -> EvalResult
```

#### download_model()

Download trained model weights.

```python
client.download_model(
    output_dir: str,
    checkpoint: str = "latest",
    format: str = "huggingface"  # or "onnx", "safetensors"
)
```

## Resource Object

Passed to agent function during execution.

```python
class Resource:
    model_api: str        # Lightning Server endpoint URL
    model_name: str       # Model identifier
    task_id: str          # Current task ID
    worker_id: int        # Worker process ID
    metadata: dict        # Custom metadata
```

**Usage:**
```python
def my_agent(resource, task):
    # Use model_api for LLM calls
    llm = ChatAnthropic(base_url=resource.model_api)

    # Access metadata
    if resource.metadata.get("use_cot"):
        prompt = f"Think step by step: {task.question}"
    else:
        prompt = task.question

    response = llm.invoke(prompt)
    return evaluate(response)
```

## Task Object

Contains data from uploaded JSONL file.

```python
class Task:
    # Standard fields
    question: str         # Task input (if present in JSONL)
    ground_truth: Any     # Reference answer (if present)

    # Access custom fields via attribute or dict
    task.custom_field
    task["custom_field"]
```

**Example:**
```python
# JSONL:
# {"question": "Q", "ground_truth": "A", "schema": {...}, "difficulty": 3}

def agent(resource, task):
    print(task.question)      # "Q"
    print(task.ground_truth)  # "A"
    print(task.schema)        # {...}
    print(task.difficulty)    # 3
```

## Training Configuration

### Server Configuration

```python
# server_config.yaml
model:
  path: "meta-llama/Llama-3.2-3B-Instruct"
  dtype: "bfloat16"
  tensor_parallel: 4

algorithm:
  name: "grpo"
  learning_rate: 5e-7
  kl_coef: 0.001
  clip_range: 0.2
  entropy_coef: 0.01
  group_size: 8

runtime:
  max_seq_len: 4096
  batch_size: 256
  gradient_accumulation: 4
  checkpoint_interval: 100
```

### RL Algorithms

| Algorithm | Description | Use Case |
|-----------|-------------|----------|
| `grpo` | Group Relative Policy Optimization | Default, no critic needed |
| `ppo` | Proximal Policy Optimization | When you have value function |
| `reinforce++` | REINFORCE with baseline | Simplest, good for small tasks |

**GRPO Configuration:**
```python
grpo_config = {
    "group_size": 8,           # Sample 8 trajectories per task
    "kl_coef": 0.001,         # KL divergence coefficient
    "clip_range": 0.2,        # PPO clipping
    "entropy_coef": 0.01      # Exploration bonus
}
```

**PPO Configuration:**
```python
ppo_config = {
    "critic_lr": 1e-5,        # Critic learning rate
    "actor_lr": 5e-7,         # Actor learning rate
    "gae_lambda": 0.95,       # GAE parameter
    "value_clip": 0.2         # Value clipping
}
```

## Runtime API

### Auto-Instrumentation

```python
from agent_lightning.runtime import auto_instrument, set_config

# Enable automatic trajectory collection
auto_instrument(
    trace_llm_calls=True,      # Trace all LLM calls
    trace_tool_calls=True,     # Trace tool executions
    trace_context=True         # Capture full context
)

# Configure runtime
set_config({
    "air_enabled": True,       # Automatic Intermediate Rewarding
    "max_retries": 3,         # Retry failed calls
    "timeout": 60             # Call timeout
})
```

### Automatic Intermediate Rewarding (AIR)

```python
from agent_lightning.runtime import air

# Define custom AIR rules
@air.on_tool_success
def reward_tool_success(tool_name, output):
    """Assign +0.3 reward when tool succeeds."""
    return 0.3

@air.on_tool_failure
def penalize_tool_failure(tool_name, error):
    """Assign -0.2 penalty when tool fails."""
    return -0.2

@air.on_code_execution
def reward_code_exec(code, result, exit_code):
    """Custom reward based on code execution."""
    if exit_code == 0:
        return 0.5
    else:
        return -0.1
```

## Transition Data Format

Internal data structure for RL training:

```python
class Transition:
    input: str           # LLM input/prompt
    output: str          # LLM generated output
    reward: float        # Assigned reward
    metadata: dict       # Additional info

    # Example
    {
        "input": "Question: What is 2+2?\nAnswer:",
        "output": "4",
        "reward": 1.0,
        "metadata": {
            "model": "llama-3.2-3b",
            "temperature": 0.7,
            "tool_calls": []
        }
    }
```

## Trajectory Format

```python
class Trajectory:
    task_id: str
    transitions: List[Transition]
    total_reward: float
    metadata: dict

# Example trajectory (RAG agent)
{
    "task_id": "task-001",
    "transitions": [
        {
            "input": "Generate query for: Capital of France?",
            "output": "France capital city",
            "reward": 0.5  # Intermediate
        },
        {
            "input": "Question: Capital of France?\nDocs: Paris is...",
            "output": "Paris",
            "reward": 1.0  # Final
        }
    ],
    "total_reward": 1.5,
    "metadata": {"num_steps": 2}
}
```

## Training Result

```python
class TrainingResult:
    final_reward: float           # Final average reward
    train_rewards: List[float]    # Reward curve (training)
    test_rewards: List[float]     # Reward curve (test)
    checkpoints: List[str]        # Saved checkpoint paths
    total_steps: int              # Training steps
    total_time: float             # Training time (seconds)
```

**Usage:**
```python
result = client.train(my_agent, nworkers=8)

print(f"Final reward: {result.final_reward}")
print(f"Training time: {result.total_time / 3600:.2f} hours")
print(f"Best checkpoint: {result.checkpoints[-1]}")
```

## Error Handling

```python
from agent_lightning.exceptions import (
    ServerConnectionError,
    TrainingError,
    DataUploadError,
    InvalidConfigError
)

try:
    client = Client(server_url)
    client.upload_data("train.jsonl")
    result = client.train(my_agent)
except ServerConnectionError:
    print("Cannot connect to Lightning Server")
except DataUploadError as e:
    print(f"Data upload failed: {e}")
except TrainingError as e:
    print(f"Training error: {e}")
```

## Environment Variables

```bash
# Server configuration
export AGENT_LIGHTNING_SERVER_URL="http://localhost:8000"
export AGENT_LIGHTNING_API_KEY="optional-api-key"

# Model configuration
export LIGHTNING_MODEL_PATH="meta-llama/Llama-3.2-3B-Instruct"
export LIGHTNING_DEVICE="cuda"

# Training configuration
export LIGHTNING_RL_ALGORITHM="grpo"
export LIGHTNING_BATCH_SIZE="256"
export LIGHTNING_LEARNING_RATE="5e-7"

# Runtime configuration
export LIGHTNING_ENABLE_AIR="true"
export LIGHTNING_MAX_RETRIES="3"
```

## CLI Commands

```bash
# Start Lightning Server
agent-lightning server start \
    --model meta-llama/Llama-3.2-3B-Instruct \
    --gpus 4 \
    --port 8000 \
    --algorithm grpo

# Upload data
agent-lightning data upload \
    --train train.jsonl \
    --test test.jsonl \
    --data-id my-dataset

# Start training
agent-lightning train \
    --agent-script my_agent.py \
    --data-id my-dataset \
    --nworkers 8 \
    --epochs 3

# Evaluate model
agent-lightning evaluate \
    --agent-script my_agent.py \
    --checkpoint checkpoints/latest \
    --test test.jsonl

# Download model
agent-lightning model download \
    --checkpoint checkpoints/step-1000 \
    --output trained_model/
```

## Advanced: Multi-LLM Training

When multiple different LLMs need joint optimization:

```python
# Not fully supported yet - use independent training
def agent_with_multi_llm(resource, task):
    # LLM 1: Query generator (Llama-3.2-3B)
    query_llm = ChatAnthropic(base_url=resource.model_api_1)
    query = query_llm.invoke(task.question)

    # LLM 2: Answer generator (Qwen2.5-7B)
    answer_llm = ChatAnthropic(base_url=resource.model_api_2)
    answer = answer_llm.invoke(query)

    return evaluate(answer)

# Future: Multi-agent RL support planned
```
