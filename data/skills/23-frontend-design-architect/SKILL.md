---
name: frontend-design-architect
description: Provides comprehensive guidance for frontend design architecture AND creative implementation. Covers CSS methodology selection, three-tier design tokens, component anatomy, responsive strategies, accessibility patterns, AND distinctive aesthetic direction to avoid generic AI-generated designs. Use when architecting design systems, building components, creating landing pages, or implementing production-grade UI with memorable visual identity.
version: 1.1.0
author: Orchestra Research
license: MIT
tags: [Frontend, Design-System, CSS, Design-Tokens, Accessibility, Responsive, Animation, Creative-Design, UI-Aesthetics]
dependencies: []
---

# Frontend Design Architect

## Overview

Architect scalable, maintainable frontend design systems using modern CSS patterns, design tokens, and accessibility-first principles. This skill provides decision frameworks for technology selection, token architecture, and component design.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  FRONTEND DESIGN ARCHITECTURE                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. CSS Strategy      →  2. Token Architecture →  3. Component Design       │
│     Methodology           Three-tier System        Anatomy & States          │
│                                                                              │
│  4. Responsive        →  5. Accessibility      →  6. Performance            │
│     Mobile-first          WCAG 2.1 AA             Animation & Loading        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## When to Use This Skill

**Trigger this skill when:**
- Architecting new frontend design systems
- Selecting CSS methodologies (Tailwind, CSS Modules, CSS-in-JS)
- Implementing design token systems
- Building reusable component libraries
- Establishing responsive design strategies
- Implementing accessibility (WCAG compliance)
- Optimizing CSS performance and animations
- Migrating between CSS approaches

## CSS Architecture Decision Tree

```
PROJECT TYPE?
│
├─ Marketing/Landing Pages
│   ├─ Simple (1-5 pages) → Vanilla CSS or Tailwind
│   ├─ Medium (5-20 pages) → Tailwind with @apply
│   └─ Complex (20+ pages) → CSS Modules or Tailwind
│
├─ Web Application (SaaS/Dashboard)
│   ├─ Small team (1-3 devs) → Tailwind or CSS Modules
│   ├─ Medium team (4-10) → CSS Modules with tokens
│   └─ Large team (10+) → Design system with CSS-in-JS or CSS Modules
│
├─ Component Library
│   ├─ Internal → CSS Modules + tokens
│   └─ Public/OSS → Vanilla CSS (no runtime)
│
└─ E-commerce
    ├─ Standard → Tailwind (fast development)
    └─ Custom brand → CSS Modules with design tokens
```

## Approach Comparison Matrix

| Factor | Tailwind | CSS Modules | CSS-in-JS | Vanilla CSS |
|--------|----------|-------------|-----------|-------------|
| **Learning Curve** | Medium | Low | Medium | Low |
| **Bundle Size** | Small (purged) | Small | Medium-Large | Smallest |
| **Runtime Cost** | None | None | Yes | None |
| **Type Safety** | Partial | No | Yes | No |
| **Dynamic Theming** | Limited | Limited | Excellent | Good (vars) |
| **Team Scale** | Any | Any | Medium+ | Small |
| **Refactoring** | Hard | Medium | Easy | Hard |

## Three-Tier Token Architecture

```
┌─────────────────────────────────────────────────────────┐
│  TIER 3: COMPONENT TOKENS                               │
│  button-primary-bg, card-shadow, input-border-focus     │
│  └─ References semantic tokens                          │
├─────────────────────────────────────────────────────────┤
│  TIER 2: SEMANTIC TOKENS                                │
│  color-action-primary, space-component-gap, radius-md   │
│  └─ References primitive tokens                         │
├─────────────────────────────────────────────────────────┤
│  TIER 1: PRIMITIVE TOKENS                               │
│  blue-500, space-16, radius-8                           │
│  └─ Raw values with no references                       │
└─────────────────────────────────────────────────────────┘
```

### Token Scale Selection

| Complexity | Token Count | Use Case |
|------------|-------------|----------|
| **Minimal** | 10-20 | Portfolio, Blog, Landing |
| **Standard** | 50-100 | SaaS, E-commerce, Dashboard |
| **Enterprise** | 200+ | Design system, Multi-brand |

## Quick Start: Design Token System

### Primitive Tokens (Tier 1)

```css
:root {
  /* Color Primitives */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-500: #6b7280;
  --gray-900: #111827;

  --blue-500: #3b82f6;
  --blue-600: #2563eb;

  /* Space Primitives (4px grid) */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-4: 1rem;     /* 16px */
  --space-6: 1.5rem;   /* 24px */

  /* Radius Primitives */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
}
```

### Semantic Tokens (Tier 2)

```css
:root {
  /* Color Semantics */
  --color-bg-primary: var(--gray-50);
  --color-bg-secondary: var(--gray-100);
  --color-text-primary: var(--gray-900);
  --color-text-secondary: var(--gray-500);
  --color-action-primary: var(--blue-500);
  --color-action-primary-hover: var(--blue-600);

  /* Space Semantics */
  --space-component-padding: var(--space-4);
  --space-component-gap: var(--space-2);
  --space-section-padding: var(--space-6);
}
```

### Component Tokens (Tier 3)

```css
:root {
  /* Button Tokens */
  --button-bg: var(--color-action-primary);
  --button-bg-hover: var(--color-action-primary-hover);
  --button-text: white;
  --button-padding-x: var(--space-4);
  --button-padding-y: var(--space-2);
  --button-radius: var(--radius-md);

  /* Card Tokens */
  --card-bg: var(--color-bg-primary);
  --card-padding: var(--space-component-padding);
  --card-radius: var(--radius-lg);
  --card-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
```

## Component Anatomy

### Button Component States

```css
.button {
  /* Base */
  background: var(--button-bg);
  color: var(--button-text);
  padding: var(--button-padding-y) var(--button-padding-x);
  border-radius: var(--button-radius);
  transition: background 150ms ease;
}

/* States */
.button:hover { background: var(--button-bg-hover); }
.button:focus-visible {
  outline: 2px solid var(--color-action-primary);
  outline-offset: 2px;
}
.button:active { transform: scale(0.98); }
.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

## Responsive Strategy

### Mobile-First Breakpoints

```css
/* Base: Mobile (< 640px) */
.container { padding: var(--space-4); }

/* Tablet (≥ 640px) */
@media (min-width: 640px) {
  .container { padding: var(--space-6); }
}

/* Desktop (≥ 1024px) */
@media (min-width: 1024px) {
  .container { padding: var(--space-8); }
}

/* Wide (≥ 1280px) */
@media (min-width: 1280px) {
  .container { max-width: 1200px; margin: 0 auto; }
}
```

### Container Queries (Modern)

```css
.card-container { container-type: inline-size; }

@container (min-width: 400px) {
  .card { flex-direction: row; }
}
```

## Accessibility Checklist

### Color & Contrast
- [ ] Text contrast ≥ 4.5:1 (WCAG AA)
- [ ] Large text contrast ≥ 3:1
- [ ] UI components contrast ≥ 3:1
- [ ] Don't rely on color alone for meaning

### Focus Management
- [ ] Visible focus indicators (2px outline minimum)
- [ ] Focus order matches visual order
- [ ] Skip links for navigation
- [ ] Focus trap in modals

### Motion & Animation
- [ ] Respect `prefers-reduced-motion`
- [ ] Animations < 5 seconds or controllable
- [ ] No flashing > 3 times/second

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Creative Design Principles

**Goal**: Create distinctive, production-grade interfaces that avoid generic "AI slop" aesthetics.

### Aesthetic Direction Selection

Before coding, commit to a **BOLD aesthetic direction**:

| Direction | Characteristics | Use When |
|-----------|-----------------|----------|
| **Minimal Modern** | White space, typography-focused, subtle shadows | SaaS, Fintech, Healthcare |
| **Bold Expressive** | Strong colors, dramatic type, glow effects | Agencies, Startups, Gaming |
| **Editorial** | Magazine-style, asymmetric layouts, serif fonts | Media, Publishing, Luxury |
| **Brutalist** | Raw, unconventional, grid-breaking | Creative studios, Art |
| **Organic Natural** | Soft curves, earth tones, flowing shapes | Wellness, Food, Eco |

### AI Slop Avoidance Checklist

**NEVER use these generic patterns:**
- ❌ Purple-blue gradients on white backgrounds
- ❌ Inter/Roboto/Arial as primary fonts
- ❌ Everything centered symmetrically
- ❌ Rainbow color palettes (different color per section)
- ❌ Pill-shaped buttons everywhere (`rounded-full`)
- ❌ Heavy drop shadows on every element
- ❌ Stock photos of people high-fiving

**ALWAYS do these instead:**
- ✅ Choose 1-2 distinctive fonts (see presets for suggestions)
- ✅ Use asymmetric layouts (60/40, 70/30 splits)
- ✅ Limit to 1 brand color + 1 accent color
- ✅ Use subtle radius (`rounded-lg` max, not `rounded-full`)
- ✅ Apply generous white space (80-128px section padding)
- ✅ Create one memorable visual moment per page

### Quick Aesthetic Application

```
1. Select preset: assets/presets/{aesthetic-name}.json
2. Apply tokens: Copy color, typography, spacing values
3. Follow principles: Check designPrinciples array in preset
4. Validate: Run through AI Slop Avoidance Checklist
```

→ [`references/creative-aesthetics.md`](references/creative-aesthetics.md) - Full aesthetic guide with examples
→ [`references/landing-page-excellence.md`](references/landing-page-excellence.md) - Landing page patterns

## Animation Performance

### CSS vs JavaScript Animation

| Use CSS For | Use JavaScript For |
|-------------|-------------------|
| Simple transitions | Complex sequences |
| Hover/focus states | Physics-based motion |
| Loading indicators | Scroll-triggered |
| Entry animations | Interactive gestures |

### GPU-Accelerated Properties

```css
/* Fast (GPU) - Use these */
.animate-fast {
  transform: translateX(100px);
  opacity: 0.5;
}

/* Slow (Layout) - Avoid animating */
.animate-slow {
  width: 200px;    /* Triggers layout */
  height: 100px;   /* Triggers layout */
  top: 50px;       /* Triggers layout */
}

/* Promote to GPU layer */
.gpu-layer {
  will-change: transform;
  transform: translateZ(0);
}
```

## Design Audit Checklist

### Visual Consistency
- [ ] Color palette follows token system
- [ ] Typography uses defined scale
- [ ] Spacing follows grid (4px/8px)
- [ ] Border radius is consistent
- [ ] Shadows follow elevation system

### Component Quality
- [ ] All interactive states defined
- [ ] Loading states implemented
- [ ] Error states designed
- [ ] Empty states considered
- [ ] Responsive behavior tested

### Performance
- [ ] CSS bundle < 50KB (gzipped)
- [ ] No unused CSS in production
- [ ] Critical CSS inlined
- [ ] Fonts optimized (subset, preload)
- [ ] Images use modern formats

## References

→ [`references/design-decision-framework.md`](references/design-decision-framework.md) - CSS methodology selection
→ [`references/token-architecture.md`](references/token-architecture.md) - Token system patterns
→ [`references/component-anatomy.md`](references/component-anatomy.md) - Component design patterns
→ [`references/responsive-strategy.md`](references/responsive-strategy.md) - Responsive design
→ [`references/accessibility-patterns.md`](references/accessibility-patterns.md) - WCAG compliance
→ [`references/animation-performance.md`](references/animation-performance.md) - Animation optimization
→ [`references/css-architecture-guide.md`](references/css-architecture-guide.md) - CSS organization
→ [`references/modern-css-features.md`](references/modern-css-features.md) - Modern CSS capabilities
→ [`references/landing-page-excellence.md`](references/landing-page-excellence.md) - Landing page patterns
→ [`references/design-audit-checklist.md`](references/design-audit-checklist.md) - Quality validation
→ [`references/migration-guides.md`](references/migration-guides.md) - Migration strategies

### Assets

→ [`assets/tokens/`](assets/tokens/) - Token JSON files (minimal, standard, enterprise)
→ [`assets/presets/`](assets/presets/) - Design presets (minimal-modern, professional-trust, etc.)
→ [`assets/components/`](assets/components/) - Component templates (React, Vue, Svelte)

**Related Skills:**
- `25-backend-architect` - Backend system integration
- `24-spec-driven-planner` - Specification development

---

**Version:** 1.0.0
**Complexity:** Intermediate-Advanced
**Output:** Scalable frontend design system architecture
