# CSS Architecture Guide

## Overview

This guide covers CSS architecture patterns, methodologies, and modern practices for scalable frontend development.

---

## CSS Methodologies

### BEM (Block Element Modifier)

**Pattern:** `block__element--modifier`

```css
/* Block */
.card { }

/* Element */
.card__header { }
.card__body { }
.card__footer { }

/* Modifier */
.card--featured { }
.card--compact { }
.card__header--sticky { }
```

**Pros:**
- Clear relationship between elements
- Self-documenting class names
- Low specificity (single class)
- Works with any tooling

**Cons:**
- Verbose class names
- Can lead to long HTML
- No automatic scoping

**Best For:** Large teams, legacy projects, vanilla CSS

---

### CSS Modules

**Pattern:** Scoped classes with hash suffixes

```css
/* Button.module.css */
.button {
  padding: 12px 24px;
}

.primary {
  background: blue;
}

.secondary {
  background: gray;
}
```

```jsx
import styles from './Button.module.css';

<button className={`${styles.button} ${styles.primary}`}>
  Click me
</button>
```

**Output:** `button_a3x7f primary_b2y8g`

**Pros:**
- Automatic scoping
- Standard CSS syntax
- Zero runtime
- Easy migration from BEM

**Cons:**
- Multiple files per component
- No dynamic styling
- Class name concatenation

**Best For:** React/Vue apps, gradual migration, performance focus

---

### Utility-First (Tailwind CSS)

**Pattern:** Single-purpose utility classes

```html
<button class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600
               transition-colors duration-200 font-medium">
  Click me
</button>
```

**With @apply for extraction:**
```css
.btn-primary {
  @apply px-4 py-2 bg-blue-500 text-white rounded-lg
         hover:bg-blue-600 transition-colors duration-200 font-medium;
}
```

**Pros:**
- Rapid development
- Consistent design constraints
- Small production bundles (purging)
- Design system in config

**Cons:**
- Verbose HTML
- Learning curve
- Can encourage design inconsistency
- Hard to read complex components

**Best For:** Startups, prototypes, small teams, design flexibility

---

### CSS-in-JS (Styled Components, Emotion)

**Pattern:** JavaScript-defined styles

```jsx
// Styled Components
import styled from 'styled-components';

const Button = styled.button`
  padding: 12px 24px;
  background: ${props => props.primary ? 'blue' : 'gray'};
  color: white;
  border-radius: 8px;

  &:hover {
    background: ${props => props.primary ? 'darkblue' : 'darkgray'};
  }
`;

<Button primary>Click me</Button>
```

**Pros:**
- Dynamic styling based on props
- Automatic scoping
- Colocated with component
- Type-safe with TypeScript
- No dead code

**Cons:**
- Runtime performance cost
- SSR complexity
- Larger bundles
- Different mental model

**Best For:** React apps, complex theming, dynamic UIs

---

## Modern CSS Features

### CSS Custom Properties

```css
:root {
  /* Global tokens */
  --color-primary: hsl(210, 100%, 50%);
  --spacing-md: 1rem;
  --radius-md: 0.5rem;
}

.button {
  /* Component-level defaults */
  --button-bg: var(--color-primary);
  --button-padding: var(--spacing-md);

  background: var(--button-bg);
  padding: var(--button-padding);
}

/* Override at usage */
.button.secondary {
  --button-bg: transparent;
}
```

### CSS Nesting (Native)

```css
.card {
  padding: 1rem;

  & .header {
    font-weight: bold;
  }

  & .body {
    color: gray;
  }

  &:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }

  &.featured {
    border: 2px solid gold;
  }
}
```

### Container Queries

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

.card {
  display: flex;
  flex-direction: column;
}

@container card (min-width: 400px) {
  .card {
    flex-direction: row;
  }
}

@container card (min-width: 600px) {
  .card {
    gap: 2rem;
  }
}
```

### @layer for Cascade Control

```css
/* Define layer order - later = higher priority */
@layer reset, tokens, base, components, utilities;

@layer reset {
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
  }
}

@layer tokens {
  :root {
    --color-primary: blue;
  }
}

@layer base {
  body {
    font-family: system-ui;
    line-height: 1.5;
  }
}

@layer components {
  .button {
    padding: 12px 24px;
  }
}

@layer utilities {
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    clip: rect(0, 0, 0, 0);
  }
}
```

### :has() Selector

```css
/* Style parent based on child */
.form-group:has(input:focus) {
  border-color: blue;
}

/* Card with image gets different padding */
.card:has(> img) {
  padding: 0;
}

/* Required field label */
label:has(+ input:required)::after {
  content: " *";
  color: red;
}

/* Navigation with current page */
.nav-item:has([aria-current="page"]) {
  font-weight: bold;
}
```

---

## File Organization

### Feature-Based (Recommended)

```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.module.css
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   ├── Card/
│   │   ├── Card.tsx
│   │   ├── Card.module.css
│   │   └── index.ts
│   └── index.ts
├── styles/
│   ├── tokens/
│   │   ├── colors.css
│   │   ├── spacing.css
│   │   ├── typography.css
│   │   └── index.css
│   ├── base/
│   │   ├── reset.css
│   │   └── global.css
│   └── utilities/
│       └── helpers.css
└── App.tsx
```

### Layer-Based

```
src/
├── styles/
│   ├── 0-tokens/           # Design tokens
│   │   ├── colors.css
│   │   ├── spacing.css
│   │   └── typography.css
│   ├── 1-reset/            # CSS reset
│   │   └── reset.css
│   ├── 2-base/             # Element styles
│   │   ├── typography.css
│   │   └── links.css
│   ├── 3-components/       # Component styles
│   │   ├── button.css
│   │   └── card.css
│   ├── 4-layouts/          # Layout patterns
│   │   ├── grid.css
│   │   └── container.css
│   ├── 5-pages/            # Page-specific
│   │   └── home.css
│   └── 6-utilities/        # Utility classes
│       └── helpers.css
└── components/
```

---

## CSS Reset Recommendations

### Modern Minimal Reset

```css
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  /* Prevent font size inflation on mobile */
  -moz-text-size-adjust: none;
  -webkit-text-size-adjust: none;
  text-size-adjust: none;
}

body {
  min-height: 100vh;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

img,
picture,
video,
canvas,
svg {
  display: block;
  max-width: 100%;
}

input,
button,
textarea,
select {
  font: inherit;
}

p,
h1,
h2,
h3,
h4,
h5,
h6 {
  overflow-wrap: break-word;
}

/* Remove list styles for lists with role="list" */
ul[role="list"],
ol[role="list"] {
  list-style: none;
}
```

---

## Performance Best Practices

### Selector Efficiency

```css
/* ❌ Slow - deep nesting, universal selectors */
.header .nav .list .item .link * { }

/* ✅ Fast - single class, shallow nesting */
.nav-link { }

/* ❌ Avoid - attribute selectors are slower */
[class^="btn-"] { }

/* ✅ Better - explicit class */
.btn { }
```

### Critical CSS

```html
<head>
  <!-- Critical CSS inline for above-fold content -->
  <style>
    /* Reset + above-fold styles */
    .hero { ... }
    .nav { ... }
  </style>

  <!-- Non-critical CSS deferred -->
  <link rel="preload" href="styles.css" as="style"
        onload="this.onload=null;this.rel='stylesheet'">
  <noscript>
    <link rel="stylesheet" href="styles.css">
  </noscript>
</head>
```

### Reduce Unused CSS

```bash
# PurgeCSS configuration (Tailwind built-in)
# tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    './public/index.html',
  ],
}
```

---

## Architecture Patterns Summary

| Pattern | Scoping | Runtime | Dynamic | Complexity |
|---------|---------|---------|---------|------------|
| BEM | Manual | None | No | Low |
| CSS Modules | Auto | None | No | Low |
| Tailwind | Via purge | None | Limited | Medium |
| CSS-in-JS | Auto | Yes | Yes | Medium |
| CSS Custom Props | Via cascade | None | Yes | Low |

**Recommendation by Project Type:**

| Project | Recommended Approach |
|---------|---------------------|
| Marketing site | Tailwind or vanilla CSS |
| Blog/content | Vanilla CSS with tokens |
| SaaS/App | CSS Modules + tokens |
| Design system | CSS Modules + comprehensive tokens |
| Component library | Vanilla CSS (no dependencies) |
| Quick prototype | Tailwind |

---

**Version:** 1.0
**Last Updated:** 2025
