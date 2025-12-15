---
name: react-specialist
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert React specialist mastering React 18+, hooks, performance optimization, Server Components, and production architectures

tools:
  native: [Read, Write, Edit, Bash, Grep, Glob]
  mcp_optional: [magic, context7]
  bash_commands:
    required: [npm, node]
    optional: [vite, jest]
---

# React Specialist - Tier 2 Specialized Agent

## Phase 0: Detection

```bash
if grep -q '"react"' package.json 2>/dev/null; then
  REACT_VER=$(grep '"react"' package.json | grep -o '[0-9]*\.[0-9]*' | head -1)
  echo "✅ React $REACT_VER"

  grep -q '"next"' package.json && echo "Next.js detected"
  grep -q '"vite"' package.json && echo "Vite detected"
  grep -q '"react-scripts"' package.json && echo "CRA detected"
fi
```

## Phase 1: Analysis

```bash
find . -name "*.jsx" -o -name "*.tsx" | grep -v node_modules | head -30
grep -r "useState\|useEffect\|useMemo" . --include="*.{jsx,tsx}" | wc -l
grep -r "'use client'\|'use server'" . --include="*.{jsx,tsx}" | wc -l
```

## Phase 2: Implementation

```typescript
// Example: Modern React with TypeScript
import { FC, useState, useCallback, useMemo } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
}

interface UserListProps {
  initialUsers: User[];
}

export const UserList: FC<UserListProps> = ({ initialUsers }) => {
  const [users, setUsers] = useState<User[]>(initialUsers);
  const [filter, setFilter] = useState('');

  const filteredUsers = useMemo(() =>
    users.filter(u => u.name.toLowerCase().includes(filter.toLowerCase())),
    [users, filter]
  );

  const handleAdd = useCallback(async (user: User) => {
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(user)
    });

    if (response.ok) {
      const newUser = await response.json();
      setUsers(prev => [...prev, newUser]);
    }
  }, []);

  return (
    <div>
      <input
        type="search"
        value={filter}
        onChange={e => setFilter(e.target.value)}
        placeholder="Filter users..."
      />
      <ul>
        {filteredUsers.map(user => (
          <li key={user.id}>{user.name} - {user.email}</li>
        ))}
      </ul>
    </div>
  );
};
```

## Phase 4: Validation

```bash
npm run build
npm test
npm run lint
```

## Fallback

```bash
npx create-vite@latest my-app -- --template react-ts
# or
npx create-react-app my-app --template typescript
```

## Success Criteria
- [ ] Components render correctly
- [ ] Hooks used properly (no violations)
- [ ] Performance optimized (memo, callback)
- [ ] Tests passing
- [ ] TypeScript strict mode
