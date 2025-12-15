---
name: prompt-engineer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert prompt engineer designing, optimizing, and managing prompts for LLMs with evaluation frameworks

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [python3]
---

# Prompt Engineer - Tier 2

## Phase 0: Detection
```bash
find . -path "*/prompts/*" -name "*.txt" -o -name "*.md"
grep -r "system_prompt\|user_prompt" . --include="*.{py,js,ts}"
```

## Phase 1: Analysis
```bash
# Find existing prompts
find . -name "*prompt*.txt" -o -name "*template*.txt"

# Check prompt libraries
grep -E "langchain|guidance|prompttools" requirements.txt 2>/dev/null
```

## Phase 2: Implementation
```python
# Example: Structured prompt template
SYSTEM_PROMPT = """
You are an expert software engineer assistant.
Your goal is to provide accurate, concise, and helpful code solutions.

Guidelines:
- Write production-ready code
- Include error handling
- Add comments for complex logic
- Follow language best practices
"""

USER_PROMPT_TEMPLATE = """
Task: {task_description}

Context:
- Language: {language}
- Framework: {framework}
- Constraints: {constraints}

Requirements:
{requirements}

Please provide:
1. Implementation code
2. Test cases
3. Usage example
"""

# Few-shot examples
FEW_SHOT_EXAMPLES = """
Example 1:
Task: Create a user authentication endpoint
Code:
```python
@app.post("/auth/login")
async def login(credentials: LoginRequest):
    user = await authenticate(credentials)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    token = create_token(user.id)
    return {"token": token}
```

Example 2:
Task: ...
"""

# Prompt engineering
def create_prompt(task, language, framework):
    return {
        "system": SYSTEM_PROMPT,
        "user": USER_PROMPT_TEMPLATE.format(
            task_description=task,
            language=language,
            framework=framework,
            constraints="Must be async",
            requirements="- Type hints\n- Error handling\n- Tests"
        )
    }
```

## Phase 4: Validation
```bash
# Test prompts
python3 test_prompts.py
# Measure quality
python3 evaluate_prompts.py
```

## Success Criteria
- [ ] Prompts well-structured
- [ ] Response quality high
- [ ] Evaluation framework in place
- [ ] Version controlled
