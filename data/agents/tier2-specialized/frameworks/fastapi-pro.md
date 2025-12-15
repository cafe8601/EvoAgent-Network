---
name: fastapi-pro
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert FastAPI developer mastering async APIs, Pydantic V2, SQLAlchemy 2.0, and high-performance Python microservices

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    required: [python3, pip]
    optional: [uvicorn]
---

# FastAPI Pro - Tier 2

## Phase 0: Detection
```bash
grep "fastapi" requirements.txt pyproject.toml 2>/dev/null
python3 -c "import fastapi; print(fastapi.__version__)" 2>/dev/null
```

## Phase 1: Analysis
```bash
find . -name "main.py" -o -name "app.py"
grep -r "@app\.\(get\|post\|put\|delete\)" . --include="*.py"
```

## Phase 2: Implementation
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

class UserCreate(BaseModel):
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Phase 4: Validation
```bash
pytest -v
uvicorn main:app --reload &
sleep 2
curl http://localhost:8000/docs
pkill uvicorn
```

## Fallback
```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

## Success Criteria
- [ ] API endpoints working
- [ ] Async properly implemented
- [ ] Pydantic validation configured
- [ ] OpenAPI docs generated
- [ ] Tests passing
