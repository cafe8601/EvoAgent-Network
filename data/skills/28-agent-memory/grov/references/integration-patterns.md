# Grov Integration Patterns

## Hybrid Memory Setups

### Grov + claude-mem (Recommended for Teams)

Combine Grov's reasoning focus with claude-mem's detailed search:

```bash
# Terminal 1: Start Grov proxy
grov proxy

# Terminal 2: Configure claude-mem for search-only
claude-mem config set auto_inject false

# Now:
# - Grov injects team reasoning at session start
# - claude-mem provides on-demand search for details
```

**When to use each:**

| Need | Tool |
|------|------|
| "Why did we change auth?" | Grov (reasoning) |
| "What exact files did I edit yesterday?" | claude-mem (search) |
| Team shared learning | Grov (cloud sync) |
| Personal work history | claude-mem |
| Prevent AI drift | Grov |

### Grov + Beads (Task + Memory)

Combine task tracking with reasoning memory:

```bash
# Both can run simultaneously
grov proxy &
# Beads tracks tasks, Grov captures reasoning

# When starting a task
bd update bd-123 --status in_progress
# Claude works, Grov captures reasoning

# When done
bd close bd-123 --reason "Fixed auth bug by extending token refresh"
# Both systems have complementary records
```

## General Agent Patterns

### Reasoning Memory for Any Agent

Apply Grov's reasoning capture pattern:

```python
from dataclasses import dataclass
from typing import List, Optional
import sqlite3
import json

@dataclass
class ReasoningTrace:
    task: str
    files: List[str]
    reasoning: str
    decision: str
    status: str = "completed"

class ReasoningMemory:
    """Grov-style reasoning memory for general agents."""

    def __init__(self, db_path: str = "reasoning.db"):
        self.db = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS reasoning (
                id TEXT PRIMARY KEY,
                task TEXT NOT NULL,
                files TEXT,
                reasoning TEXT,
                decision TEXT,
                status TEXT DEFAULT 'completed',
                created DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_files ON reasoning(files);
        """)

    def capture(self, trace: ReasoningTrace) -> str:
        """Capture a reasoning trace."""
        trace_id = f"trace_{int(time.time() * 1000)}"
        self.db.execute("""
            INSERT INTO reasoning (id, task, files, reasoning, decision, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            trace_id,
            trace.task,
            json.dumps(trace.files),
            trace.reasoning,
            trace.decision,
            trace.status
        ))
        self.db.commit()
        return trace_id

    def get_context_for_files(self, files: List[str], limit: int = 5) -> str:
        """Get relevant reasoning for files being worked on."""
        context_parts = []

        for file_path in files:
            rows = self.db.execute("""
                SELECT task, reasoning, decision
                FROM reasoning
                WHERE files LIKE ?
                ORDER BY created DESC
                LIMIT ?
            """, (f'%{file_path}%', limit)).fetchall()

            for task, reasoning, decision in rows:
                context_parts.append(f"""[Task: {task}]
- Files: {file_path}
- Reasoning: {reasoning}
- Decision: {decision}""")

        if context_parts:
            return f"""VERIFIED CONTEXT FROM PREVIOUS SESSIONS:

{chr(10).join(context_parts)}

YOU MAY SKIP exploration for files mentioned above."""
        return ""

    def extract_reasoning(self, llm_response: str, task: str, files: List[str]) -> ReasoningTrace:
        """Extract reasoning from LLM response."""
        # Use a smaller model to extract reasoning
        extraction_prompt = f"""Extract the key reasoning from this response:

Task: {task}
Response: {llm_response}

Return JSON:
{{"reasoning": "<why this approach>", "decision": "<what was decided>"}}"""

        # Call extraction model (e.g., Haiku)
        result = self.extract_model.invoke(extraction_prompt)
        data = json.loads(result)

        return ReasoningTrace(
            task=task,
            files=files,
            reasoning=data["reasoning"],
            decision=data["decision"]
        )
```

### Anti-Drift Pattern

```python
from anthropic import Anthropic
from typing import Dict, Optional
import json

class DriftDetector:
    """Grov-style anti-drift for any agent."""

    INTERVENTIONS = {
        (8, 10): None,  # Normal
        (5, 7): "gentle_reminder",
        (3, 4): "explicit_redirect",
        (1, 2): "strong_correction",
        (0, 0): "halt"
    }

    def __init__(self, threshold: int = 5):
        self.client = Anthropic()
        self.threshold = threshold
        self.intent = None
        self.history = []

    def set_intent(self, intent: str):
        """Store the user's original intent."""
        self.intent = intent
        self.history = []

    def check(self, recent_actions: list) -> Dict:
        """Check alignment and get intervention if needed."""
        if not self.intent:
            return {"score": 10, "intervention": None}

        prompt = f"""Evaluate alignment between intent and actions.

Original Intent: {self.intent}

Recent Actions:
{json.dumps(recent_actions, indent=2)}

Score 1-10 where:
- 10: Perfectly aligned
- 7-9: On track with minor deviations
- 4-6: Some drift, may need guidance
- 1-3: Significant drift
- 0: Completely off track

Respond with JSON only:
{{"score": <int>, "assessment": "<brief>", "suggestion": "<if score < 7>"}}"""

        response = self.client.messages.create(
            model="claude-haiku-3",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        result = json.loads(response.content[0].text)
        self.history.append(result)

        # Determine intervention
        score = result["score"]
        intervention = None

        for (low, high), action in self.INTERVENTIONS.items():
            if low <= score <= high:
                intervention = action
                break

        if intervention and score < self.threshold:
            result["intervention"] = self._get_intervention_message(
                intervention, result.get("suggestion", "")
            )
        else:
            result["intervention"] = None

        return result

    def _get_intervention_message(self, level: str, suggestion: str) -> str:
        messages = {
            "gentle_reminder": f"Reminder: Stay focused on the original task. {suggestion}",
            "explicit_redirect": f"You appear to be drifting. Original task: {self.intent}. {suggestion}",
            "strong_correction": f"STOP. Significant drift detected. Return to: {self.intent}",
            "halt": f"HALTED. You have completely drifted from: {self.intent}. Awaiting user guidance."
        }
        return messages.get(level, "")
```

### Team Sync Pattern

```python
import requests
from typing import List, Dict
import json

class TeamMemorySync:
    """Grov-style team synchronization."""

    def __init__(self, api_url: str, team_token: str):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {team_token}"}
        self.local_memory = ReasoningMemory()

    def sync_to_team(self) -> Dict:
        """Push local memories to team dashboard."""
        # Get unsynced memories
        unsynced = self.local_memory.db.execute("""
            SELECT id, task, files, reasoning, decision
            FROM reasoning
            WHERE synced = FALSE
        """).fetchall()

        if not unsynced:
            return {"synced": 0}

        memories = [
            {
                "id": row[0],
                "task": row[1],
                "files": json.loads(row[2]),
                "reasoning": row[3],
                "decision": row[4]
            }
            for row in unsynced
        ]

        response = requests.post(
            f"{self.api_url}/sync",
            headers=self.headers,
            json={"memories": memories}
        )

        if response.ok:
            # Mark as synced
            ids = [m["id"] for m in memories]
            self.local_memory.db.execute(
                f"UPDATE reasoning SET synced = TRUE WHERE id IN ({','.join('?' * len(ids))})",
                ids
            )
            self.local_memory.db.commit()

        return response.json()

    def pull_from_team(self, query: str = None, limit: int = 10) -> List[Dict]:
        """Pull relevant memories from team."""
        params = {"limit": limit}
        if query:
            params["q"] = query

        response = requests.get(
            f"{self.api_url}/memories",
            headers=self.headers,
            params=params
        )

        return response.json().get("memories", [])

    def get_team_context(self, files: List[str]) -> str:
        """Get team context for files."""
        # Search team memories by file paths
        memories = self.pull_from_team(
            query=" OR ".join(files),
            limit=5
        )

        if not memories:
            return ""

        context_parts = []
        for mem in memories:
            context_parts.append(f"""[{mem['author']}] {mem['task']}
- Reasoning: {mem['reasoning']}
- Decision: {mem['decision']}""")

        return f"""TEAM CONTEXT:

{chr(10).join(context_parts)}"""
```

### Extended Cache Pattern

```python
import asyncio
import aiohttp
from datetime import datetime, timedelta

class CacheKeepAlive:
    """Grov-style extended cache for Anthropic API."""

    def __init__(
        self,
        api_key: str,
        interval_seconds: int = 240,  # 4 minutes (cache expires at 5)
        cost_per_request: float = 0.002
    ):
        self.api_key = api_key
        self.interval = interval_seconds
        self.cost_per_request = cost_per_request
        self.running = False
        self.total_cost = 0.0
        self.keep_alive_count = 0

    async def start(self, system_prompt: str):
        """Start keep-alive loop."""
        self.running = True
        self.system_prompt = system_prompt

        while self.running:
            await asyncio.sleep(self.interval)

            if self.running:
                await self._send_keepalive()

    async def stop(self):
        """Stop keep-alive loop."""
        self.running = False

    async def _send_keepalive(self):
        """Send minimal request to keep cache warm."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-haiku-3",
                    "max_tokens": 1,
                    "system": self.system_prompt,  # Same system = cache hit
                    "messages": [{"role": "user", "content": "."}]
                }
            ) as response:
                if response.ok:
                    self.keep_alive_count += 1
                    self.total_cost += self.cost_per_request

    def get_stats(self) -> dict:
        return {
            "keep_alive_count": self.keep_alive_count,
            "total_cost": f"${self.total_cost:.4f}",
            "running": self.running
        }
```

## LangChain Integration

```python
from langchain.callbacks.base import BaseCallbackHandler
from langchain_anthropic import ChatAnthropic

class GrovCallbackHandler(BaseCallbackHandler):
    """Integrate Grov patterns with LangChain."""

    def __init__(self, reasoning_memory: ReasoningMemory, drift_detector: DriftDetector):
        self.memory = reasoning_memory
        self.drift = drift_detector
        self.current_task = None
        self.current_files = []
        self.tool_calls = []

    def on_chain_start(self, serialized, inputs, **kwargs):
        """Capture intent at chain start."""
        if "input" in inputs:
            self.current_task = inputs["input"]
            self.drift.set_intent(self.current_task)

    def on_tool_end(self, output, **kwargs):
        """Track tool usage for drift detection."""
        self.tool_calls.append({
            "tool": kwargs.get("name", "unknown"),
            "output_preview": str(output)[:200]
        })

        # Check drift every 5 tool calls
        if len(self.tool_calls) % 5 == 0:
            result = self.drift.check(self.tool_calls[-10:])
            if result["intervention"]:
                # Inject correction (implementation depends on chain setup)
                print(f"[DRIFT ALERT] {result['intervention']}")

    def on_chain_end(self, outputs, **kwargs):
        """Capture reasoning at chain end."""
        if self.current_task and outputs:
            trace = self.memory.extract_reasoning(
                str(outputs),
                self.current_task,
                self.current_files
            )
            self.memory.capture(trace)

# Usage
memory = ReasoningMemory()
drift = DriftDetector()
handler = GrovCallbackHandler(memory, drift)

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    callbacks=[handler]
)
```

## Best Practices

### When to Capture Reasoning

1. **After significant decisions**: Architecture changes, algorithm choices
2. **After debugging sessions**: Root cause findings
3. **After refactoring**: Why the new structure is better
4. **After configuration changes**: Why specific values were chosen

### Drift Detection Tuning

| Project Type | Threshold | Intervention Style |
|--------------|-----------|-------------------|
| Bug fixes | 7 | Strict (low tolerance for drift) |
| Exploration | 4 | Loose (allow some tangents) |
| Feature dev | 5 | Moderate |
| Refactoring | 6 | Moderate-strict |

### Team Sync Guidelines

1. **Sync meaningful reasoning**, not trivial changes
2. **Review team context** before injecting (may be outdated)
3. **Use semantic search** to find relevant team knowledge
4. **Respect privacy settings** for sensitive projects
