# Design Decision Framework

## Overview

This framework provides structured decision trees for common frontend design choices. Each decision includes trade-offs, context considerations, and implementation guidance.

---

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

## When to Choose What

### Choose Tailwind When:
- ✅ Rapid prototyping or MVP
- ✅ Team is familiar with utility-first
- ✅ Design is flexible/iterating
- ✅ Performance is important
- ❌ Strict custom design system exists
- ❌ Team prefers traditional CSS
- ❌ Complex component state styling

### Choose CSS Modules When:
- ✅ Traditional CSS knowledge
- ✅ Need scoped styles without runtime
- ✅ Large team with style conflicts
- ✅ Gradual migration from legacy CSS
- ❌ Heavy dynamic theming needed
- ❌ Want colocation with JS logic

### Choose CSS-in-JS When:
- ✅ React-heavy applications
- ✅ Complex theme switching
- ✅ Style logic tied to component state
- ✅ Type-safe styling needed
- ❌ SSR performance is critical
- ❌ Bundle size is a concern
- ❌ Team prefers CSS syntax

### Choose Vanilla CSS When:
- ✅ Maximum performance needed
- ✅ Simple static sites
- ✅ Library/package development
- ✅ Full CSS custom properties support
- ❌ Team discipline is inconsistent
- ❌ Need scoping guarantees
- ❌ Complex application architecture

---

## Design Token Scale Selection

```
PROJECT COMPLEXITY?
│
├─ Simple (Portfolio, Blog, Landing)
│   └─ MINIMAL (10-20 tokens)
│       - 6 colors (primary, secondary, bg, text, success, error)
│       - 6 spacing values (xs, sm, md, lg, xl, 2xl)
│       - 2 font families (sans, mono)
│       - 3 radii (sm, md, full)
│
├─ Standard (SaaS, E-commerce, Dashboard)
│   └─ STANDARD (50-100 tokens)
│       - Full color palette (gray, primary, semantic)
│       - Complete spacing scale (0-48)
│       - Typography scale with weights
│       - Shadow scale
│       - Animation presets
│
└─ Enterprise (Design System, Multi-Product)
    └─ ENTERPRISE (200+ tokens)
        - Tier 1: Primitives (raw values)
        - Tier 2: Semantic (intent-based)
        - Tier 3: Component (specific)
        - Theme variants
        - Mode tokens (light/dark)
```

---

## Component Library Strategy

```
STARTING POINT?
│
├─ Building from Scratch
│   ├─ Need full control → Radix Primitives + custom styles
│   ├─ Standard look OK → shadcn/ui (copy-paste)
│   └─ Maximum a11y → React Aria + custom styles
│
├─ Using Existing Library
│   ├─ Material-like → Material UI (MUI)
│   ├─ Highly customizable → Chakra UI
│   ├─ Enterprise-ready → Ant Design
│   └─ Minimal + accessible → Radix UI
│
└─ Extending Existing
    ├─ Light customization → Theme overrides
    ├─ Medium customization → Component wrappers
    └─ Heavy customization → Consider building own
```

### Library Selection Criteria

| Library | Best For | Trade-offs |
|---------|----------|------------|
| **Radix UI** | Custom designs, a11y-first | Requires styling work |
| **shadcn/ui** | Quick start, Tailwind users | Limited components |
| **Material UI** | Google-like design, enterprise | Large bundle, opinionated |
| **Chakra UI** | Balance of customization | Runtime performance |
| **Ant Design** | Data-heavy dashboards | Large, specific aesthetic |
| **Headless UI** | Tailwind + accessibility | Limited components |

---

## Animation Strategy Decision

```
ANIMATION TYPE?
│
├─ Simple Transitions (hover, focus)
│   └─ CSS Only
│       transition: all 200ms ease;
│
├─ Enter/Exit Animations
│   ├─ CSS capable → CSS @keyframes + classes
│   └─ Need orchestration → anime.js or GSAP
│
├─ Gesture-Based (drag, swipe)
│   ├─ React → Framer Motion
│   ├─ Vue → Motion One
│   └─ Vanilla → GSAP or anime.js
│
├─ Physics-Based (springs, momentum)
│   ├─ React → React Spring or Framer Motion
│   └─ Other → GSAP or Motion One
│
├─ SVG Animation
│   └─ GSAP (best SVG support)
│
└─ Complex Sequences
    ├─ Timeline-based → GSAP
    └─ Declarative → anime.js v4
```

### Animation Library Comparison

| Library | Size | Features | Best For |
|---------|------|----------|----------|
| **CSS** | 0KB | Transitions, keyframes | Simple states |
| **anime.js** | 17KB | Timeline, morphing, stagger | General web |
| **GSAP** | 63KB+ | Full-featured, plugins | Complex, SVG |
| **Framer Motion** | 35KB | Gestures, layout | React apps |
| **Motion One** | 15KB | Modern, performant | Minimal bundle |
| **React Spring** | 25KB | Physics-based | Natural feel |

---

## Responsive Strategy Decision

```
LAYOUT REQUIREMENTS?
│
├─ Component-Level Responsiveness
│   └─ Container Queries
│       @container (min-width: 400px) { ... }
│
├─ Page-Level Responsiveness
│   └─ Media Queries (viewport-based)
│       @media (min-width: 768px) { ... }
│
├─ Content-Aware Sizing
│   └─ clamp() + fluid typography
│       font-size: clamp(1rem, 2vw + 0.5rem, 1.5rem);
│
└─ Mixed Approach (Most Common)
    ├─ Container queries for components
    ├─ Media queries for layout
    └─ Fluid sizing for typography
```

### Breakpoint Strategy

**Mobile-First (Recommended)**
```css
/* Base: Mobile */
.element { ... }

/* Tablet and up */
@media (min-width: 768px) { ... }

/* Desktop and up */
@media (min-width: 1024px) { ... }

/* Wide and up */
@media (min-width: 1280px) { ... }
```

**Container-First (Modern)**
```css
.component-container {
  container-type: inline-size;
}

.component {
  /* Mobile default */
}

@container (min-width: 400px) {
  .component { /* Larger */ }
}

@container (min-width: 600px) {
  .component { /* Even larger */ }
}
```

---

## Dark Mode Strategy Decision

```
DARK MODE REQUIREMENT?
│
├─ Not Needed
│   └─ Skip implementation
│
├─ System Preference Only
│   └─ CSS prefers-color-scheme
│       @media (prefers-color-scheme: dark) { ... }
│
├─ User Toggle (Persist Choice)
│   └─ CSS + JavaScript
│       [data-theme="dark"] { ... }
│       localStorage for persistence
│
└─ Multiple Themes
    └─ CSS Custom Properties + Theme Provider
        Multiple [data-theme="X"] variants
```

### Dark Mode Implementation Patterns

**CSS-Only (System Preference)**
```css
:root {
  --bg: white;
  --text: black;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a1a;
    --text: #f0f0f0;
  }
}
```

**Toggle with Override**
```css
:root {
  --bg: white;
  --text: black;
}

[data-theme="dark"] {
  --bg: #1a1a1a;
  --text: #f0f0f0;
}

/* Respect system when no preference set */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #1a1a1a;
    --text: #f0f0f0;
  }
}
```

---

## Typography Scale Decision

```
CONTENT TYPE?
│
├─ Marketing/Editorial
│   └─ Dramatic Scale
│       Hero: 4-8rem
│       Ratio: 1.414+ (augmented fourth)
│
├─ Application/Dashboard
│   └─ Compact Scale
│       Hero: 2-3rem
│       Ratio: 1.2-1.25 (minor third)
│
├─ Documentation/Content
│   └─ Readable Scale
│       Hero: 2.5-4rem
│       Ratio: 1.25-1.333 (major third)
│
└─ Mixed (Most Sites)
    └─ Fluid Scale
        Hero: clamp(2rem, 5vw, 4rem)
        Body: clamp(1rem, 1.5vw, 1.125rem)
```

### Type Scale Ratios

| Ratio | Name | Vibe | Best For |
|-------|------|------|----------|
| 1.067 | Minor Second | Tight | Dense UI |
| 1.125 | Major Second | Subtle | Apps, dashboards |
| 1.2 | Minor Third | Moderate | General purpose |
| 1.25 | Major Third | Balanced | Most websites |
| 1.333 | Perfect Fourth | Clear | Editorial |
| 1.414 | Augmented Fourth | Dramatic | Marketing |
| 1.5 | Perfect Fifth | Bold | Landing pages |
| 1.618 | Golden Ratio | Grand | Luxury, art |

---

## Quick Decision Cheat Sheet

| Question | Quick Answer |
|----------|--------------|
| CSS approach for MVP? | Tailwind |
| CSS approach for enterprise? | CSS Modules + design tokens |
| Need dynamic themes? | CSS-in-JS or CSS custom properties |
| Animation for React? | Framer Motion |
| Animation for vanilla? | anime.js or CSS |
| Token scale for small project? | Minimal (10-20) |
| Token scale for design system? | Enterprise (200+) |
| Component library with customization? | Radix + custom styles |
| Component library for speed? | shadcn/ui |
| Dark mode implementation? | CSS custom properties + data-theme |

---

**Version:** 1.0
**Last Updated:** 2025
