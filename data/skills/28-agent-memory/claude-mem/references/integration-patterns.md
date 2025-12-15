# Claude-Mem Integration Patterns

## Framework Integration

### LangChain

```python
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_tool_calling_agent, AgentExecutor
import requests

@tool
def search_memory(query: str, limit: int = 5) -> str:
    """Search past work sessions for relevant context.

    Use this to find:
    - Previous code changes
    - Past debugging sessions
    - Historical context about files
    """
    response = requests.get(
        "http://localhost:37777/search",
        params={"q": query, "limit": limit}
    )
    if response.status_code == 200:
        results = response.json().get("results", [])
        return "\n".join([r["content"] for r in results])
    return "No results found"

@tool
def get_recent_sessions(limit: int = 5) -> str:
    """Get summaries of recent work sessions."""
    response = requests.get(
        "http://localhost:37777/sessions",
        params={"limit": limit}
    )
    if response.status_code == 200:
        sessions = response.json().get("sessions", [])
        return "\n".join([
            f"[{s['started']}] {s['summary']}"
            for s in sessions
        ])
    return "No sessions found"

# Create agent with memory tools
llm = ChatAnthropic(model="claude-sonnet-4-20250514")
tools = [search_memory, get_recent_sessions]

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# Agent automatically uses memory when relevant
result = executor.invoke({
    "input": "Fix the auth bug we discussed yesterday"
})
```

### OpenAI Agents SDK

```python
from agents import Agent, Runner
import requests

def search_memory(query: str) -> str:
    """Search past work sessions."""
    response = requests.get(
        "http://localhost:37777/search",
        params={"q": query, "limit": 5}
    )
    return response.json()

agent = Agent(
    name="code_assistant",
    model="claude-sonnet-4-20250514",
    tools=[search_memory],
    instructions="""You are a code assistant with access to past work history.
    Use search_memory to find relevant context before making changes."""
)

runner = Runner()
result = runner.run(agent, "Continue working on the auth module")
```

### AutoGen

```python
from autogen import ConversableAgent, UserProxyAgent
import requests

def search_memory_func(query: str) -> str:
    response = requests.get(
        "http://localhost:37777/search",
        params={"q": query, "limit": 5}
    )
    return str(response.json().get("results", []))

assistant = ConversableAgent(
    name="assistant",
    llm_config={"model": "claude-sonnet-4-20250514"},
    system_message="Search memory before making code changes."
)

# Register function
assistant.register_function(
    function_map={"search_memory": search_memory_func}
)

user_proxy = UserProxyAgent(name="user")
user_proxy.initiate_chat(
    assistant,
    message="What did we change in the auth module?"
)
```

## Hybrid Memory Patterns

### claude-mem + Grov

Combine observation memory with reasoning memory:

```bash
# Setup: Grov handles team context, claude-mem handles search

# 1. Configure claude-mem to disable auto-inject
claude-mem config set auto_inject false

# 2. Start Grov proxy for team context
grov proxy

# 3. Use claude-mem only for search
# Claude can still invoke mem-search skill manually
```

**When to use each:**

| Scenario | Primary Tool | Secondary Tool |
|----------|--------------|----------------|
| Team project, need shared reasoning | Grov | claude-mem (search) |
| Solo project, detailed history | claude-mem | - |
| Need to find specific past changes | claude-mem | - |
| Prevent AI drift | Grov | - |

### claude-mem + Beads

Combine session memory with task tracking:

```python
import subprocess
import requests

class HybridMemory:
    """Combine claude-mem (what happened) with beads (what to do)."""

    def get_context_for_task(self, task_id: str) -> dict:
        # Get task from beads
        result = subprocess.run(
            ["bd", "show", task_id, "--json"],
            capture_output=True, text=True
        )
        task = json.loads(result.stdout)

        # Search related memory
        memory_response = requests.get(
            "http://localhost:37777/search",
            params={"q": task["title"], "limit": 3}
        )

        return {
            "task": task,
            "related_history": memory_response.json().get("results", [])
        }

    def complete_task_with_memory(self, task_id: str, summary: str):
        # Close task in beads
        subprocess.run([
            "bd", "close", task_id,
            "--reason", summary,
            "--json"
        ])

        # Memory is automatically captured by claude-mem hooks
```

## General Agent Memory Implementation

### Progressive Disclosure Pattern

Implement claude-mem's token-efficient memory pattern:

```python
from dataclasses import dataclass
from typing import List, Optional
import sqlite3

@dataclass
class MemoryLayer:
    """Progressive disclosure memory layer."""
    level: int
    content: str
    token_count: int
    full_content: Optional[str] = None

class ProgressiveMemory:
    """
    Layer 1: Index (~100 tokens) - What exists
    Layer 2: Summary (~500 tokens) - Key details
    Layer 3: Full content (variable) - Complete data
    """

    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                layer1_index TEXT,
                layer2_summary TEXT,
                layer3_full TEXT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_created ON memories(created);
        """)

    def store(self, content: str, compress_fn) -> str:
        """Store with automatic compression into layers."""
        memory_id = self._generate_id()

        # Layer 3: Full content
        layer3 = content

        # Layer 2: AI-compressed summary
        layer2 = compress_fn(content, max_tokens=500)

        # Layer 1: Index entry
        layer1 = compress_fn(layer2, max_tokens=100)

        self.db.execute("""
            INSERT INTO memories (id, layer1_index, layer2_summary, layer3_full)
            VALUES (?, ?, ?, ?)
        """, (memory_id, layer1, layer2, layer3))
        self.db.commit()

        return memory_id

    def get_context(self, max_tokens: int = 2000) -> List[MemoryLayer]:
        """Get memory with progressive disclosure."""
        memories = []
        token_budget = max_tokens

        # Start with Layer 1 (indexes)
        rows = self.db.execute("""
            SELECT id, layer1_index, layer2_summary, layer3_full
            FROM memories ORDER BY created DESC LIMIT 20
        """).fetchall()

        for row in rows:
            id_, l1, l2, l3 = row
            l1_tokens = len(l1.split()) * 1.3  # Rough estimate

            if token_budget >= l1_tokens:
                # Can fit at least index
                layer = MemoryLayer(
                    level=1,
                    content=l1,
                    token_count=int(l1_tokens),
                    full_content=l3
                )
                memories.append(layer)
                token_budget -= l1_tokens

        return memories

    def expand(self, memory: MemoryLayer, level: int = 2) -> MemoryLayer:
        """Expand memory to deeper level (on-demand)."""
        if level == 2:
            # Fetch summary
            row = self.db.execute(
                "SELECT layer2_summary FROM memories WHERE layer1_index = ?",
                (memory.content,)
            ).fetchone()
            return MemoryLayer(
                level=2,
                content=row[0] if row else memory.content,
                token_count=len(row[0].split()) * 1.3 if row else memory.token_count
            )
        elif level == 3:
            return MemoryLayer(
                level=3,
                content=memory.full_content,
                token_count=len(memory.full_content.split()) * 1.3
            )
        return memory
```

### Observation Compression Pattern

```python
from anthropic import Anthropic

class ObservationCompressor:
    """Compress tool outputs into observations (claude-mem style)."""

    def __init__(self, model: str = "claude-haiku-3"):
        self.client = Anthropic()
        self.model = model

    def compress(self, tool_name: str, tool_output: str, max_tokens: int = 500) -> str:
        """Compress tool output into observation."""
        prompt = f"""Compress this {tool_name} output into a concise observation.

Focus on:
- What changed or was discovered
- Key file paths and line numbers
- Important decisions or patterns
- Anything useful for future reference

Tool output:
{tool_output}

Observation (max {max_tokens} tokens):"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def extract_concepts(self, observation: str) -> List[str]:
        """Extract searchable concepts from observation."""
        prompt = f"""Extract 2-5 concept tags from this observation.

Categories: discovery, problem-solution, pattern, refactor, bug-fix, feature, config

Observation:
{observation}

Tags (comma-separated):"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )

        return [t.strip() for t in response.content[0].text.split(",")]
```

### Hybrid Search Pattern

```python
import chromadb
import sqlite3
from typing import List, Dict

class HybridSearch:
    """FTS + Vector search (claude-mem style)."""

    def __init__(self, db_path: str):
        self.sqlite = sqlite3.connect(db_path)
        self.chroma = chromadb.PersistentClient(path=db_path + "/chroma")
        self.collection = self.chroma.get_or_create_collection("observations")

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Hybrid search combining FTS and vector similarity."""

        # FTS search (keyword matching)
        fts_results = self.sqlite.execute("""
            SELECT id, content, rank
            FROM observations_fts
            WHERE content MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit)).fetchall()

        # Vector search (semantic similarity)
        vector_results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )

        # Merge and deduplicate
        seen_ids = set()
        merged = []

        # Interleave results (alternating FTS and vector)
        fts_iter = iter(fts_results)
        vec_iter = iter(zip(
            vector_results["ids"][0],
            vector_results["documents"][0],
            vector_results["distances"][0]
        ))

        while len(merged) < limit:
            # Add FTS result
            try:
                fts = next(fts_iter)
                if fts[0] not in seen_ids:
                    merged.append({
                        "id": fts[0],
                        "content": fts[1],
                        "source": "fts",
                        "score": -fts[2]  # Negative rank = better
                    })
                    seen_ids.add(fts[0])
            except StopIteration:
                pass

            # Add vector result
            try:
                vec = next(vec_iter)
                if vec[0] not in seen_ids:
                    merged.append({
                        "id": vec[0],
                        "content": vec[1],
                        "source": "vector",
                        "score": 1 - vec[2]  # Distance to similarity
                    })
                    seen_ids.add(vec[0])
            except StopIteration:
                pass

            if not fts_results and not vector_results["ids"][0]:
                break

        return merged[:limit]
```

## Performance Optimization

### Batch Observation Processing

```python
import asyncio
from collections import deque

class ObservationQueue:
    """Async queue for batch processing observations."""

    def __init__(self, batch_size: int = 10, flush_interval: float = 5.0):
        self.queue = deque()
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.compressor = ObservationCompressor()

    async def add(self, tool_name: str, output: str):
        """Add observation to queue."""
        self.queue.append((tool_name, output))

        if len(self.queue) >= self.batch_size:
            await self.flush()

    async def flush(self):
        """Process queued observations in batch."""
        batch = []
        while self.queue and len(batch) < self.batch_size:
            batch.append(self.queue.popleft())

        # Parallel compression
        tasks = [
            asyncio.to_thread(
                self.compressor.compress, tool, output
            )
            for tool, output in batch
        ]

        compressed = await asyncio.gather(*tasks)

        # Batch insert to database
        # ...
```

### Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedMemory:
    """Memory with LRU cache for frequent queries."""

    def __init__(self, memory: ProgressiveMemory):
        self.memory = memory
        self.cache_ttl = timedelta(minutes=5)
        self.cache_time = {}

    @lru_cache(maxsize=100)
    def search_cached(self, query: str, limit: int = 5) -> tuple:
        """Cached search results."""
        results = self.memory.search(query, limit)
        return tuple(results)  # Convert to hashable

    def search(self, query: str, limit: int = 5) -> list:
        """Search with cache invalidation."""
        cache_key = (query, limit)

        if cache_key in self.cache_time:
            if datetime.now() - self.cache_time[cache_key] > self.cache_ttl:
                # Invalidate
                self.search_cached.cache_clear()

        self.cache_time[cache_key] = datetime.now()
        return list(self.search_cached(query, limit))
```
