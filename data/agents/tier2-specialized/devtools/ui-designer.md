---
name: ui-designer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: UI designer for visual design, component libraries, design tokens, and interface optimization

tools:
  native: [Read, Write]
  mcp_optional: [magic]
  bash_commands:
    optional: []
---

# UI Designer - Tier 2

## Phase 1: Design System
```css
/* Example: Design tokens */
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-secondary: #8B5CF6;
  --color-success: #10B981;
  --color-error: #EF4444;
  --color-gray-50: #F9FAFB;
  --color-gray-900: #111827;

  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'Fira Code', monospace;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-full: 9999px;
}

/* Component: Button */
.button {
  padding: var(--space-sm) var(--space-md);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.button:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
```

## Success Criteria
- [ ] Design system documented
- [ ] Components designed
- [ ] Tokens defined
- [ ] Accessibility considered
- [ ] Responsive layouts
