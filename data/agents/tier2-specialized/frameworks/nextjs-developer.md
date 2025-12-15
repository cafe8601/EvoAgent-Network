---
name: nextjs-developer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert Next.js developer mastering Next.js 14+ with App Router, Server Components, Server Actions, and full-stack features

tools:
  native: [Read, Write, Edit, Bash, Grep, Glob]
  mcp_optional: [magic, context7]
  bash_commands:
    required: [npm, node]
    optional: [next, vercel]
---

# Next.js Developer - Tier 2 Specialized Agent

## Phase 0: Detection

```bash
if grep -q '"next"' package.json 2>/dev/null; then
  NEXT_VERSION=$(grep '"next"' package.json | grep -o '[0-9]*\.[0-9]*\.[0-9]*' | head -1)
  echo "Next.js $NEXT_VERSION detected"

  if [ -d "app" ]; then
    echo "✅ App Router detected (Next.js 13+)"
  elif [ -d "pages" ]; then
    echo "✅ Pages Router detected"
  fi
fi
```

## Phase 1: Analysis

```bash
# Find routes
find app -name "page.tsx" -o -name "page.jsx" 2>/dev/null
find pages -name "*.tsx" -o -name "*.jsx" 2>/dev/null

# Find Server Components
grep -r "'use client'" app 2>/dev/null | wc -l
grep -r "'use server'" app 2>/dev/null | wc -l

# Check API routes
find app -name "route.ts" 2>/dev/null
find pages/api -name "*.ts" -o -name "*.js" 2>/dev/null
```

## Phase 2: Implementation

```typescript
// Example: Server Component with data fetching
// app/users/page.tsx
async function getUsers() {
  const res = await fetch('https://api.example.com/users', {
    next: { revalidate: 60 } // ISR
  });
  return res.json();
}

export default async function UsersPage() {
  const users = await getUsers();

  return (
    <div>
      <h1>Users</h1>
      {users.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  );
}
```

## Phase 4: Validation

```bash
npm run dev &
sleep 5
curl http://localhost:3000 | grep -q "html" && echo "✅ Server running"
pkill -f "next dev"

npm run build
npm run lint
```

## Fallback

```bash
npx create-next-app@latest my-app --typescript --tailwind --app
```

## Success Criteria

- [ ] Next.js app builds successfully
- [ ] Routes working (App Router or Pages)
- [ ] Server Components rendering
- [ ] API routes functional
- [ ] Production build optimized
