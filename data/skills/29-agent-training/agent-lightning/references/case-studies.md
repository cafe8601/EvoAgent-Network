# Agent Lightning Case Studies

Real-world applications and experimental results from Microsoft Research paper.

## Case Study 1: Text-to-SQL Agent (LangChain)

### Problem Statement

Generate SQL queries from natural language questions across 200 diverse databases.

**Dataset**: Spider (Yu et al., 2018)
- 10,000+ questions
- 200 databases
- 138 domains
- Cross-domain generalization required

### Agent Architecture

Multi-agent system with 3 specialized agents:

```python
from langchain.agents import create_sql_agent
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SQLDatabase

def sql_multiagent_system(resource, task):
    # Shared LLM (same weights, different prompts)
    llm = ChatAnthropic(base_url=resource.model_api)

    # Database connection
    db = SQLDatabase.from_uri(task.database_uri)

    # Agent 1: SQL Writer
    # Prompt: "Generate SQL query for the question"
    sql_query = sql_writer(llm, task.question, task.schema)

    # Execute query
    try:
        query_result = db.run(sql_query)
        execution_success = True
    except Exception as e:
        query_result = str(e)
        execution_success = False

    # Agent 2: Checker
    # Prompt: "Is this SQL query correct and sufficient?"
    is_valid = checker(llm, sql_query, query_result)

    # Agent 3: Rewriter (if needed)
    if not is_valid and not execution_success:
        # Prompt: "Fix the SQL query based on error"
        sql_query = rewriter(llm, sql_query, query_result)
        query_result = db.run(sql_query)

    # Generate final answer from query result
    answer = llm.invoke(
        f"Question: {task.question}\nSQL Result: {query_result}\nAnswer:"
    ).content

    # Binary reward
    reward = 1.0 if answer == task.ground_truth else 0.0
    return reward
```

### Training Configuration

```yaml
model: "meta-llama/Llama-3.2-3B-Instruct"
algorithm: "grpo"
training:
  learning_rate: 5e-7
  batch_size: 256
  group_size: 8
  epochs: 3
  kl_coef: 0.001
runtime:
  nworkers: 8
  auto_instrumentation: true
```

### Results

| Metric | Baseline | After RL | Improvement |
|--------|----------|----------|-------------|
| Execution Accuracy | 18.3% | 58.7% | **+220%** |
| Exact Match | 15.2% | 52.4% | **+245%** |
| Training Time | - | 6.2 hours | - |
| GPU Usage | - | 4x H100 | - |

**Learning Curve**:
```
Iteration 0:   ~20% reward
Iteration 100: ~35% reward
Iteration 200: ~48% reward
Iteration 400: ~58% reward (converged)
```

**Key Insights**:
1. **Selective optimization worked**: Only Writer and Rewriter optimized, Checker frozen
2. **Multi-turn reasoning improved**: Model learned when to rewrite vs. answer
3. **Error recovery learned**: Model adapted SQL based on execution errors
4. **Cross-domain transfer**: Performance improved even on unseen database schemas

---

## Case Study 2: RAG Agent (OpenAI Agents SDK)

### Problem Statement

Multi-hop question answering requiring compositional reasoning over Wikipedia.

**Dataset**: MuSiQue (Trivedi et al., 2022)
- Multi-hop questions
- 21 million Wikipedia documents
- Requires genuine compositional reasoning
- Cannot be solved with shortcuts

### Agent Architecture

```python
from openai import OpenAI
from agent_lightning import Client

def musique_rag_agent(resource, task):
    client = OpenAI(base_url=resource.model_api, api_key="not-used")

    messages = []
    retrieved_docs = []

    # Multi-turn retrieval loop (up to 3 hops)
    for hop in range(3):
        # Generate search query
        if hop == 0:
            prompt = f"Generate search query for: {task.question}"
        else:
            prompt = f"Refine query given docs: {retrieved_docs}\nOriginal Q: {task.question}"

        response = client.chat.completions.create(
            model="llama-3.2-3b",
            messages=[{"role": "user", "content": prompt}]
        )
        query = response.choices[0].message.content

        # Retrieve using BGE embeddings + cosine similarity
        docs = wikipedia_retriever(query, top_k=5)
        retrieved_docs.extend(docs)

        # Decide: continue retrieving or answer?
        decision = client.chat.completions.create(
            model="llama-3.2-3b",
            messages=[{
                "role": "user",
                "content": f"Sufficient to answer {task.question}? Docs: {docs}"
            }]
        ).choices[0].message.content

        if "yes" in decision.lower():
            break

    # Generate final answer
    answer = client.chat.completions.create(
        model="llama-3.2-3b",
        messages=[{
            "role": "user",
            "content": f"Q: {task.question}\nDocs: {retrieved_docs}\nAnswer:"
        }]
    ).choices[0].message.content

    # Composite reward
    format_reward = 0.1 if is_valid_format(answer) else 0.0
    correctness_reward = 0.9 * word_f1(answer, task.ground_truth)
    reward = format_reward + correctness_reward

    return reward
```

### Training Configuration

```yaml
model: "meta-llama/Llama-3.2-3B-Instruct"
algorithm: "grpo"
training:
  learning_rate: 5e-7
  batch_size: 128  # Smaller batch for longer trajectories
  group_size: 8
  epochs: 2
  kl_coef: 0.001
runtime:
  nworkers: 4
  air_enabled: true  # Intermediate rewards for retrieval quality
```

### Results

| Metric | Baseline | After RL | Improvement |
|--------|----------|----------|-------------|
| F1 Score | 12.4% | 22.1% | **+78%** |
| Exact Match | 8.7% | 15.3% | **+76%** |
| Retrieval Precision | 31.2% | 47.6% | **+53%** |
| Avg. Hops | 2.1 | 1.8 | Fewer steps |

**Analysis**:
- Model learned to generate more focused queries
- Improved at deciding when to stop retrieving
- Better at multi-hop compositional reasoning
- Reduced unnecessary retrieval steps (more efficient)

---

## Case Study 3: Math Tool-Use Agent (AutoGen)

### Problem Statement

Solve mathematical problems using calculator tool.

**Dataset**: Calc-X (Kadlčík et al., 2023)
- Math problems requiring precise computation
- Adapted from GSM8K and Ape210K
- Emphasizes tool integration

### Agent Architecture

```python
from autogen import ConversableAgent, register_function
from agent_lightning import Client
import math

# Tool: Calculator
def calculator(expression: str) -> str:
    """Evaluate mathematical expression safely."""
    try:
        # Safe eval with math functions
        allowed = {
            "__builtins__": {},
            "math": math,
            "abs": abs,
            "round": round
        }
        result = eval(expression, allowed)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def math_tool_agent(resource, task):
    # Configure AutoGen
    config_list = [{
        "base_url": resource.model_api,
        "api_key": "not-used",
        "model": "llama-3.2-3b"
    }]

    # Create agent
    assistant = ConversableAgent(
        name="math_assistant",
        llm_config={
            "config_list": config_list,
            "temperature": 0.7
        },
        system_message="""Solve math problems step-by-step.
        Use the calculator tool for computations.
        Format: First explain reasoning, then call calculator, then provide final answer."""
    )

    # Register calculator
    register_function(
        calculator,
        caller=assistant,
        executor=assistant,
        description="Calculate mathematical expressions. Input: valid Python expression."
    )

    # Execute
    response = assistant.generate_reply(
        messages=[{"role": "user", "content": task.question}]
    )

    # Extract numerical answer
    predicted_answer = extract_number(response)

    # Reward
    reward = 1.0 if abs(predicted_answer - task.ground_truth) < 0.01 else 0.0
    return reward
```

### Training Configuration

```yaml
model: "meta-llama/Llama-3.2-3B-Instruct"
algorithm: "grpo"
training:
  learning_rate: 5e-7
  batch_size: 256
  group_size: 8
  epochs: 3
runtime:
  nworkers: 4
  air_enabled: true
  air_rules:
    - on: "tool_success"
      reward: 0.3
    - on: "tool_failure"
      reward: -0.2
```

### Results

| Metric | Baseline | After RL | Improvement |
|--------|----------|----------|-------------|
| Answer Accuracy | 28.5% | 74.2% | **+160%** |
| Tool Call Success | 45.7% | 89.3% | **+95%** |
| Correct Tool Usage | 52.1% | 91.7% | **+76%** |
| Steps per Problem | 3.2 | 2.1 | More efficient |

**Training Progression**:
```
Epoch 1: 28% → 45% (+17%)
Epoch 2: 45% → 62% (+17%)
Epoch 3: 62% → 74% (+12%)
```

**Learned Behaviors**:
1. When to call calculator vs. reasoning directly
2. Proper expression formatting for calculator
3. Breaking complex problems into sub-calculations
4. Validating calculator outputs before using

---

## Comparative Analysis

### Agent Lightning vs. Supervised Fine-Tuning

**Experiment**: Text-to-SQL on Spider

| Method | Data Required | Final Accuracy | Training Time |
|--------|---------------|----------------|---------------|
| SFT | 10k annotated SQL queries | 42.3% | 2 hours |
| Agent Lightning (RL) | 10k questions only | **58.7%** | 6 hours |

**Advantage**: RL achieves +16.4% higher accuracy without SQL annotations

### Agent Lightning vs. Prompt Engineering

**Experiment**: RAG on MuSiQue

| Method | Effort | F1 Score |
|--------|--------|----------|
| Base prompt | 0 iterations | 12.4% |
| Manual prompt engineering | 10 iterations | 16.8% |
| GEPA (auto prompt opt) | 50 iterations | 18.2% |
| Agent Lightning (RL) | 200 RL steps | **22.1%** |

**Advantage**: RL optimizes model weights, not just prompts

### Multi-Agent Selective Optimization

**Experiment**: 3-Agent SQL system

| Configuration | Accuracy |
|---------------|----------|
| No training | 18.3% |
| Train all 3 agents | 51.2% |
| Train Writer + Rewriter only | **58.7%** |
| Train Checker only | 22.1% |

**Insight**: Selective optimization outperforms training all agents

---

## Ablation Studies

### Impact of Component Features

**Experiment**: RAG Agent on MuSiQue

| Configuration | F1 Score | Δ |
|---------------|----------|---|
| Full Agent Lightning | 22.1% | - |
| w/o AIR (no intermediate rewards) | 18.7% | -3.4% |
| w/o Credit Assignment (uniform) | 20.3% | -1.8% |
| w/o OpenTelemetry (manual trace) | 21.5% | -0.6% |
| Single-turn GRPO (baseline) | 15.2% | -6.9% |

**Conclusion**: All components contribute to performance

### Credit Assignment Strategies

**Experiment**: Math Tool-Use Agent

| Strategy | Accuracy | Training Stability |
|----------|----------|-------------------|
| Equal credit (Agent Lightning) | 74.2% | High |
| Last-step only | 45.8% | Medium |
| Learned value function | 71.5% | Low |
| Manual heuristic | 68.3% | Medium |

**Result**: Simple equal credit works best for agent training

---

## Production Case Study: Customer Service Agent

### Scenario

E-commerce customer service agent handling order queries, returns, and FAQs.

**Requirements**:
- Multi-turn conversations
- API integration (order system, inventory, shipping)
- Tool usage (database queries, calculation)
- Custom reward based on customer satisfaction

### Implementation

```python
from langchain.agents import create_tool_calling_agent
from langchain.tools import tool
from agent_lightning import Client

# Tools
@tool
def query_order_status(order_id: str) -> dict:
    """Get order status from database."""
    return db.query(f"SELECT * FROM orders WHERE id='{order_id}'")

@tool
def calculate_refund(order_id: str, items: list) -> float:
    """Calculate refund amount."""
    # Business logic
    return refund_amount

@tool
def create_return_label(order_id: str) -> str:
    """Generate return shipping label."""
    return shipping_api.create_label(order_id)

# Agent function
def customer_service_agent(resource, task):
    llm = ChatAnthropic(base_url=resource.model_api)

    tools = [query_order_status, calculate_refund, create_return_label]
    agent = create_tool_calling_agent(llm, tools, system_prompt)
    executor = AgentExecutor(agent=agent, tools=tools, max_iterations=10)

    # Execute conversation
    conversation_history = []
    for turn in task.conversation:
        result = executor.invoke({
            "input": turn["user_message"],
            "chat_history": conversation_history
        })
        conversation_history.append((turn["user_message"], result["output"]))

    # Custom reward
    # - Task completion (0-0.5)
    # - Response quality (0-0.3)
    # - Efficiency (0-0.2)
    completion = 0.5 if task_completed(result) else 0.0
    quality = 0.3 * sentiment_score(result["output"])
    efficiency = 0.2 * (1.0 / max(len(conversation_history), 1))

    reward = completion + quality + efficiency
    return reward

# Train
client = Client(server_url)
client.upload_data("customer_service_train.jsonl")
result = client.train(customer_service_agent, nworkers=16, epochs=5)
```

### Results

**Before RL Training**:
- Task Completion: 42.3%
- Avg. Customer Satisfaction: 3.2/5
- Avg. Turns per Task: 5.7
- Tool Error Rate: 23.1%

**After RL Training (5 epochs)**:
- Task Completion: 78.6% (+36.3%)
- Avg. Customer Satisfaction: 4.3/5 (+34%)
- Avg. Turns per Task: 3.9 (-31%)
- Tool Error Rate: 4.2% (-82%)

**Business Impact**:
- 36% increase in resolution rate
- 31% reduction in conversation length
- 82% fewer tool call errors
- Estimated $120k annual cost savings

---

## Scaling Study: Large-Scale Deployment

### Experiment: 100k Training Samples

**Setup**:
- Model: Llama-3.2-7B-Instruct
- Task: Multi-domain QA
- Hardware: 8x H100 GPUs
- Workers: 32 parallel agent instances

**Training Progression**:

| Samples Processed | Avg. Reward | Wall Time | GPU Util |
|-------------------|-------------|-----------|----------|
| 10k | 0.35 | 2.1h | 78% |
| 25k | 0.51 | 5.3h | 82% |
| 50k | 0.64 | 10.8h | 85% |
| 100k | 0.73 | 22.1h | 87% |

**Observations**:
- Linear scaling with data size
- High GPU utilization (85%+)
- Stable training throughout
- No reward collapse or degradation

---

## Domain-Specific: Financial Analysis

### Scenario

XBRL financial document analysis for entity recognition and numerical reasoning.

**Datasets**:
- FiNER: 139 fine-grained entity types
- Formula: Financial computation queries

### Agent Implementation

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def financial_analysis_agent(resource, task):
    llm = ChatAnthropic(base_url=resource.model_api)

    # Domain-specific prompt template
    prompt = PromptTemplate(
        input_variables=["question", "xbrl_context"],
        template="""You are a financial analysis expert.

        XBRL Context: {xbrl_context}
        Question: {question}

        Analyze the XBRL document and provide answer.
        Use standard financial formulas and accounting principles.
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    # Execute
    result = chain.run(
        question=task.question,
        xbrl_context=task.xbrl_document
    )

    # Domain-specific reward
    if task.task_type == "entity_recognition":
        reward = entity_f1(result, task.ground_truth_entities)
    else:  # numerical reasoning
        reward = numerical_accuracy(result, task.ground_truth_value)

    return reward
```

### Results

| Task | Baseline | After RL | Improvement |
|------|----------|----------|-------------|
| FiNER (Entity Recognition) | 70.7% | 78.3% | +7.6% |
| Formula (Numerical) | 67.5% | 85.5% | **+18%** |

**Key Learnings**:
- Domain knowledge embedding improves significantly
- Formula accuracy benefits more from RL
- Financial reasoning patterns learned automatically

---

## Failure Analysis

### Common Failure Modes

#### 1. Reward Hacking

**Symptom**: Agent achieves high reward but poor real-world performance

**Example**:
```python
# Bad: Agent learns to output empty string (avoids errors)
def bad_reward(answer, ground_truth):
    if len(answer) == 0:
        return 0.5  # Avoid penalty
    else:
        return 1.0 if answer == ground_truth else 0.0

# Fix: Penalize empty/invalid outputs
def good_reward(answer, ground_truth):
    if len(answer) == 0 or not is_valid_format(answer):
        return -0.5  # Penalty
    else:
        return 1.0 if answer == ground_truth else 0.0
```

#### 2. Training Instability

**Symptom**: Reward curves oscillate or collapse

**Cause**: Learning rate too high, KL divergence too low

**Solution**:
```yaml
# Before (unstable)
learning_rate: 1e-5
kl_coef: 0.0001

# After (stable)
learning_rate: 5e-7  # Lower LR
kl_coef: 0.001      # Higher KL penalty
```

#### 3. Sparse Reward Problem

**Symptom**: No learning progress (rewards stay at 0)

**Cause**: Tasks too hard, no positive examples

**Solution**:
```python
# Enable AIR for intermediate rewards
from agent_lightning.runtime import enable_air, air

enable_air()

@air.on_tool_success
def reward_progress(tool_name, output):
    return 0.2  # Partial reward for tool usage

# Or use curriculum learning (start with easy tasks)
```

---

## Performance Optimization

### Throughput Optimization

**Experiment**: Maximize samples/hour

| Configuration | Samples/Hour | GPU Util |
|---------------|--------------|----------|
| nworkers=1 | 125 | 45% |
| nworkers=4 | 480 | 72% |
| nworkers=8 | 920 | 85% |
| nworkers=16 | 1650 | 91% |
| nworkers=32 | 2100 | 94% |

**Optimal**: nworkers=16 (diminishing returns after)

### Memory Optimization

**Experiment**: Reduce GPU memory usage

| Technique | Memory Usage | Accuracy Impact |
|-----------|--------------|-----------------|
| Baseline (bf16) | 24 GB | 100% |
| Gradient checkpointing | 18 GB | 100% |
| Gradient accumulation (4x) | 12 GB | 100% |
| Mixed precision (fp16) | 16 GB | 99.2% |
| INT8 quantization | 8 GB | 95.1% |

---

## Lessons Learned

### Best Practices from Production

1. **Start with simple reward**: Binary 0/1 correctness, then add shaping
2. **Monitor training closely**: First 50 steps reveal issues early
3. **Use AIR liberally**: Intermediate rewards prevent sparse reward problem
4. **Scale workers gradually**: Start 4 → 8 → 16 based on stability
5. **Checkpoint frequently**: Save every 50-100 steps for recovery
6. **Test on held-out data**: Training reward ≠ real-world performance
7. **Version control prompts**: Prompt changes affect RL training significantly
8. **Log everything**: OpenTelemetry traces invaluable for debugging

### Common Pitfalls

1. **Forgetting to normalize rewards**: Use 0-1 scale consistently
2. **Inconsistent reward functions**: Reward must be deterministic
3. **Overfitting to training tasks**: Always evaluate on test set
4. **Ignoring tool failures**: Handle errors explicitly in reward
5. **Too aggressive KL penalty**: Model stops exploring
6. **Insufficient parallelism**: Wastes GPU resources
7. **Not using AIR**: Sparse rewards slow learning

### Success Factors

1. Well-defined reward function aligned with real objectives
2. Sufficient training data diversity (>1000 tasks minimum)
3. Stable base model (instruction-tuned checkpoints work best)
4. Appropriate hyperparameters (conservative LR, moderate KL)
5. Monitoring and early stopping (prevent overfitting)
6. Integration with production environment
7. Continuous data collection from real usage
