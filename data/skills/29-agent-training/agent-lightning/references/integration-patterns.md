# Agent Lightning Integration Patterns

Framework-specific integration guides and real-world patterns.

## LangChain Integration

### Basic ReAct Agent

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from agent_lightning import Client

# Define tools
@tool
def calculator(expression: str) -> str:
    """Evaluate mathematical expression."""
    try:
        return str(eval(expression))
    except:
        return "Error: Invalid expression"

@tool
def search(query: str) -> str:
    """Search for information."""
    # Your search implementation
    return search_results

# Agent function for Lightning
def langchain_react_agent(resource, task):
    # 1. Initialize LLM with Lightning Server
    llm = ChatAnthropic(
        model="claude-sonnet-4-5",
        base_url=resource.model_api,
        api_key="not-used",  # Handled by server
        temperature=0.7
    )

    # 2. Create ReAct prompt
    prompt = PromptTemplate.from_template("""
    Answer the following question using available tools.

    Tools: {tools}
    Tool names: {tool_names}

    Question: {input}
    Thought: {agent_scratchpad}
    """)

    # 3. Create agent
    tools = [calculator, search]
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5
    )

    # 4. Execute
    try:
        result = executor.invoke({"input": task.question})
        answer = result["output"]
    except Exception as e:
        print(f"Agent error: {e}")
        answer = ""

    # 5. Reward
    reward = 1.0 if answer.strip() == task.ground_truth.strip() else 0.0
    return reward

# Train
client = Client("http://localhost:8000")
client.upload_data("train.jsonl", test_file="test.jsonl")
result = client.train(langchain_react_agent, nworkers=8, epochs=3)
```

### LangChain SQL Agent

```python
from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit

def sql_agent_training(resource, task):
    # Initialize LLM
    llm = ChatAnthropic(base_url=resource.model_api)

    # Connect to database
    db = SQLDatabase.from_uri(task.database_uri)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Create SQL agent
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        agent_type="openai-tools",
        verbose=True
    )

    # Execute
    result = agent.invoke({"input": task.question})

    # Reward based on SQL correctness
    predicted_sql = extract_sql(result["output"])
    reward = sql_equivalence(predicted_sql, task.ground_truth_sql)
    return reward

# Training data format
"""
{"question": "How many users?", "database_uri": "sqlite:///db.sqlite", "ground_truth_sql": "SELECT COUNT(*) FROM users"}
"""
```

### LangChain with Memory

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

def conversational_agent(resource, task):
    llm = ChatAnthropic(base_url=resource.model_api)

    # Add memory for multi-turn conversations
    memory = ConversationBufferMemory()

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

    # Multi-turn interaction
    for turn in task.conversation_turns:
        response = conversation.predict(input=turn["user"])
        memory.save_context({"input": turn["user"]}, {"output": response})

    # Evaluate final turn
    reward = evaluate_conversation(memory, task.ground_truth)
    return reward
```

## OpenAI Agents SDK Integration

### Basic Chat Agent

```python
from openai import OpenAI
from agent_lightning import Client

def openai_chat_agent(resource, task):
    client = OpenAI(
        base_url=resource.model_api,
        api_key="not-used"
    )

    # Single-turn interaction
    response = client.chat.completions.create(
        model="llama-3.2-3b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": task.question}
        ],
        temperature=0.7
    )

    answer = response.choices[0].message.content
    reward = evaluate(answer, task.ground_truth)
    return reward
```

### Function Calling Agent

```python
import json

def openai_function_calling_agent(resource, task):
    client = OpenAI(base_url=resource.model_api, api_key="not-used")

    # Define tools as OpenAI functions
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                }
            }
        }
    ]

    # Initial call
    messages = [{"role": "user", "content": task.question}]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools
    )

    # Handle tool calls
    while response.choices[0].finish_reason == "tool_calls":
        tool_call = response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        # Execute tool
        if function_name == "get_weather":
            result = get_weather(**function_args)

        # Add tool result to conversation
        messages.append(response.choices[0].message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })

        # Continue
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools
        )

    answer = response.choices[0].message.content
    reward = evaluate(answer, task.ground_truth)
    return reward
```

### Streaming Agent

```python
def streaming_agent(resource, task):
    client = OpenAI(base_url=resource.model_api, api_key="not-used")

    # Streaming response
    full_response = ""
    stream = client.chat.completions.create(
        model="llama-3.2-3b",
        messages=[{"role": "user", "content": task.question}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content

    reward = evaluate(full_response, task.ground_truth)
    return reward
```

## AutoGen Integration

### Single Agent

```python
from autogen import ConversableAgent
from agent_lightning import Client

def autogen_single_agent(resource, task):
    # Configure with Lightning Server
    config_list = [{
        "base_url": resource.model_api,
        "api_key": "not-used",
        "model": "llama-3.2-3b"
    }]

    # Create agent
    assistant = ConversableAgent(
        name="assistant",
        llm_config={"config_list": config_list},
        system_message="You are a helpful AI assistant."
    )

    # Execute
    response = assistant.generate_reply(
        messages=[{"role": "user", "content": task.question}]
    )

    reward = evaluate(response, task.ground_truth)
    return reward
```

### Multi-Agent Conversation

```python
from autogen import ConversableAgent, GroupChat, GroupChatManager

def autogen_multiagent(resource, task):
    config_list = [{
        "base_url": resource.model_api,
        "api_key": "not-used",
        "model": "llama-3.2-3b"
    }]

    # Create multiple agents
    planner = ConversableAgent(
        name="planner",
        llm_config={"config_list": config_list},
        system_message="You plan solutions step-by-step."
    )

    executor = ConversableAgent(
        name="executor",
        llm_config={"config_list": config_list},
        system_message="You execute the plan and provide results."
    )

    critic = ConversableAgent(
        name="critic",
        llm_config={"config_list": config_list},
        system_message="You review and validate results."
    )

    # Group chat
    group_chat = GroupChat(
        agents=[planner, executor, critic],
        messages=[],
        max_round=5
    )

    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config={"config_list": config_list}
    )

    # Execute
    planner.initiate_chat(
        manager,
        message=task.question
    )

    # Extract final answer
    final_message = group_chat.messages[-1]["content"]
    reward = evaluate(final_message, task.ground_truth)
    return reward
```

## Custom Agent Integration

### From-Scratch Implementation

```python
import requests
from agent_lightning import Client

def custom_rag_agent(resource, task):
    """Completely custom RAG implementation."""

    # Step 1: Generate query using Lightning Server
    query_response = requests.post(
        f"{resource.model_api}/v1/chat/completions",
        json={
            "model": "llama-3.2-3b",
            "messages": [
                {"role": "system", "content": "Generate a search query."},
                {"role": "user", "content": task.question}
            ]
        }
    ).json()

    query = query_response["choices"][0]["message"]["content"]

    # Step 2: Custom retrieval
    documents = my_custom_retriever(query, top_k=5)

    # Step 3: Generate answer
    answer_response = requests.post(
        f"{resource.model_api}/v1/chat/completions",
        json={
            "model": "llama-3.2-3b",
            "messages": [
                {"role": "system", "content": "Answer based on documents."},
                {"role": "user", "content": f"Q: {task.question}\nDocs: {documents}"}
            ]
        }
    ).json()

    answer = answer_response["choices"][0]["message"]["content"]

    # Custom reward
    reward = custom_metric(answer, task.ground_truth)
    return reward

# Train
client = Client(server_url)
client.train(custom_rag_agent)
```

### With External Tools/APIs

```python
def agent_with_external_apis(resource, task):
    """Agent using external APIs and services."""
    from openai import OpenAI

    client = OpenAI(base_url=resource.model_api, api_key="not-used")

    # Step 1: Analyze task
    analysis = client.chat.completions.create(
        model="llama-3.2-3b",
        messages=[{"role": "user", "content": f"Analyze: {task.question}"}]
    ).choices[0].message.content

    # Step 2: Call external API based on analysis
    if "weather" in analysis.lower():
        api_result = requests.get(
            "https://api.weather.com/forecast",
            params={"city": extract_city(task.question)}
        ).json()
    elif "stock" in analysis.lower():
        api_result = get_stock_price(extract_ticker(task.question))
    else:
        api_result = "No API needed"

    # Step 3: Generate final answer
    final_answer = client.chat.completions.create(
        model="llama-3.2-3b",
        messages=[
            {"role": "user", "content": task.question},
            {"role": "assistant", "content": f"Data: {api_result}"}
        ]
    ).choices[0].message.content

    reward = evaluate(final_answer, task.ground_truth)
    return reward
```

## Integration with Other Skills

### With 27-ai-agent-sandbox (Daytona)

```python
from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams
from agent_lightning import Client
from openai import OpenAI

def code_agent_with_sandbox(resource, task):
    # Initialize Daytona sandbox
    daytona = Daytona(DaytonaConfig(api_key=daytona_api_key))
    sandbox = daytona.create(CreateSandboxFromSnapshotParams(language="python"))

    try:
        # Generate code using Lightning Server
        llm = OpenAI(base_url=resource.model_api, api_key="not-used")
        code_response = llm.chat.completions.create(
            model="llama-3.2-3b",
            messages=[{
                "role": "user",
                "content": f"Generate Python code to solve: {task.question}"
            }]
        )
        code = extract_code(code_response.choices[0].message.content)

        # Execute in Daytona sandbox
        exec_result = sandbox.process.code_run(code)

        # Composite reward
        exec_success = 0.3 if exec_result.exit_code == 0 else 0.0
        correctness = 0.7 if exec_result.result == task.ground_truth else 0.0
        reward = exec_success + correctness

        return reward
    finally:
        sandbox.delete()

# Train
client = Client(server_url)
client.train(code_agent_with_sandbox, nworkers=4)
```

### With 14-agents/langchain (LangGraph)

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from agent_lightning import Client

class State:
    question: str
    context: str
    answer: str

def langgraph_agent(resource, task):
    from langchain_anthropic import ChatAnthropic

    llm = ChatAnthropic(base_url=resource.model_api)

    # Define nodes
    def retrieve(state):
        query = llm.invoke(f"Generate query: {state.question}").content
        context = retriever.search(query)
        return {"context": context}

    def generate(state):
        answer = llm.invoke(
            f"Q: {state.question}\nContext: {state.context}\nAnswer:"
        ).content
        return {"answer": answer}

    # Build graph
    graph = StateGraph(State)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    # Compile and run
    app = graph.compile()
    result = app.invoke({"question": task.question})

    reward = evaluate(result["answer"], task.ground_truth)
    return reward
```

### With 28-agent-memory (Beads)

Combine RL training with task tracking:

```python
import subprocess
import json
from agent_lightning import Client

def agent_with_beads_tracking(resource, task):
    # Mark task as in progress
    subprocess.run(["bd", "update", task.beads_id, "--status", "in_progress"])

    # Run agent
    llm = ChatAnthropic(base_url=resource.model_api)
    result = my_agent.run(llm, task)

    # Evaluate
    reward = evaluate(result, task.ground_truth)

    # Update beads based on result
    if reward > 0.8:
        subprocess.run([
            "bd", "close", task.beads_id,
            "--reason", f"Solved with reward {reward}"
        ])
    else:
        subprocess.run([
            "bd", "create", f"Failed: {task.question}",
            "-p", "0", "-t", "bug"
        ])

    return reward
```

## Real-World Patterns

### Pattern 1: Curriculum Learning

Gradually increase task difficulty during training:

```python
def agent_with_curriculum(resource, task):
    llm = ChatAnthropic(base_url=resource.model_api)

    # Adjust based on difficulty
    if task.difficulty == "easy":
        max_steps = 3
        reward_scale = 1.0
    elif task.difficulty == "medium":
        max_steps = 5
        reward_scale = 1.5
    else:  # hard
        max_steps = 10
        reward_scale = 2.0

    # Execute with limits
    result = agent_with_max_steps(llm, task, max_steps)

    # Scale reward by difficulty
    base_reward = evaluate(result, task.ground_truth)
    reward = base_reward * reward_scale
    return reward

# Data with difficulty labels
"""
{"question": "Easy Q", "ground_truth": "A", "difficulty": "easy"}
{"question": "Hard Q", "ground_truth": "A", "difficulty": "hard"}
"""
```

### Pattern 2: Reward Shaping

Custom reward functions for better learning signals:

```python
def agent_with_shaped_reward(resource, task):
    llm = ChatAnthropic(base_url=resource.model_api)

    # Track agent execution
    agent_trace = []

    # Step 1: Query generation
    query = llm.invoke(f"Generate query: {task.question}").content
    agent_trace.append(("query", query))

    # Step 2: Retrieval
    docs = retriever.search(query)
    agent_trace.append(("docs", docs))

    # Step 3: Answer generation
    answer = llm.invoke(f"Answer {task.question} using {docs}").content
    agent_trace.append(("answer", answer))

    # Shaped reward
    rewards = []

    # Reward 1: Query quality (0-0.3)
    query_reward = evaluate_query_relevance(query, task.question)
    rewards.append(0.3 * query_reward)

    # Reward 2: Retrieval quality (0-0.3)
    doc_reward = evaluate_doc_relevance(docs, task.ground_truth)
    rewards.append(0.3 * doc_reward)

    # Reward 3: Answer correctness (0-0.4)
    answer_reward = evaluate_answer(answer, task.ground_truth)
    rewards.append(0.4 * answer_reward)

    total_reward = sum(rewards)
    return total_reward
```

### Pattern 3: Error Recovery

Handle agent failures gracefully:

```python
def robust_agent(resource, task):
    llm = ChatAnthropic(base_url=resource.model_api)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Execute agent
            result = my_agent.run(llm, task)

            # Successful execution
            reward = evaluate(result, task.ground_truth)
            return reward

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                # Retry with modified prompt
                continue
            else:
                # Final attempt failed - assign penalty
                return -0.5  # Negative reward for failure
```

### Pattern 4: Multi-Task Training

Train on diverse tasks simultaneously:

```python
def multi_task_agent(resource, task):
    llm = ChatAnthropic(base_url=resource.model_api)

    # Route based on task type
    if task.task_type == "qa":
        result = qa_agent(llm, task)
    elif task.task_type == "summarization":
        result = summarize_agent(llm, task)
    elif task.task_type == "translation":
        result = translate_agent(llm, task)
    else:
        result = general_agent(llm, task)

    # Task-specific reward
    reward = evaluate_by_type(result, task)
    return reward

# Training data with task types
"""
{"question": "Translate: Hello", "ground_truth": "Bonjour", "task_type": "translation"}
{"question": "Summarize: ...", "ground_truth": "...", "task_type": "summarization"}
"""
```

### Pattern 5: Selective Agent Optimization in Multi-Agent

```python
def selective_multiagent_training(resource, task):
    """
    3 agents: Planner, Executor, Critic
    Only optimize: Planner and Executor (not Critic)
    """
    llm_trainable = ChatAnthropic(base_url=resource.model_api)  # Training
    llm_frozen = ChatAnthropic(model="claude-sonnet-4-5")  # Fixed

    # Agent 1: Planner (OPTIMIZE)
    plan = llm_trainable.invoke(f"Plan for: {task.question}").content

    # Agent 2: Executor (OPTIMIZE)
    execution = llm_trainable.invoke(f"Execute: {plan}").content

    # Agent 3: Critic (FROZEN - don't optimize)
    critique = llm_frozen.invoke(f"Critique: {execution}").content

    # Only Planner and Executor are optimized via RL
    reward = evaluate(execution, task.ground_truth)
    return reward
```

## Integration with RL Frameworks

### VeRL Backend

```python
# Agent Lightning uses VeRL as default RL backend

# Install
pip install verl-nightly

# Server config
lightning_config = {
    "backend": "verl",
    "verl_config": {
        "actor_rollout_ref": {
            "tensor_model_parallel_size": 4,
            "gpu_memory_utilization": 0.4
        },
        "trainer": {
            "total_epochs": 3,
            "save_freq": 100
        }
    }
}
```

### Custom RL Algorithm

```python
# Implement custom RL algorithm
from agent_lightning.algorithms import BaseRLAlgorithm

class CustomRL(BaseRLAlgorithm):
    def compute_advantages(self, trajectories):
        # Your advantage estimation
        pass

    def update_policy(self, advantages):
        # Your policy update
        pass

# Register
client.train(my_agent, algorithm=CustomRL())
```

## Production Deployment

### Save and Deploy Trained Model

```python
# After training
result = client.train(my_agent, nworkers=8)

# Download model
client.download_model(
    output_dir="trained_model",
    checkpoint="latest",
    format="huggingface"
)

# Deploy with vLLM
from vllm import LLM

trained_llm = LLM(model="trained_model", dtype="bfloat16")

# Use in production agent
def production_agent(question):
    response = trained_llm.generate(question)
    return response
```

### Continuous Training Pipeline

```bash
#!/bin/bash
# continuous_training.sh

while true; do
    # Collect new data from production
    python collect_production_data.py --output new_data.jsonl

    # Upload and train
    agent-lightning data upload --train new_data.jsonl --data-id prod-$(date +%Y%m%d)
    agent-lightning train --agent-script agent.py --data-id prod-$(date +%Y%m%d) --epochs 1

    # Evaluate
    agent-lightning evaluate --checkpoint latest --test test.jsonl

    # Deploy if improvement
    python deploy_if_better.py

    # Wait 1 week
    sleep 604800
done
```
