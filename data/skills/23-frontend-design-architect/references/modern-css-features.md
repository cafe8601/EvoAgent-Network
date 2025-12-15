# Modern CSS Features Guide

## Overview

This guide covers CSS features with strong browser support in 2025 that improve developer experience and enable new design patterns.

---

## CSS Custom Properties (Variables)

### Basic Usage

```css
:root {
  /* Define at root for global access */
  --color-primary: hsl(210, 100%, 50%);
  --spacing-md: 1rem;
}

.button {
  /* Use with fallback */
  background: var(--color-primary, blue);
  padding: var(--spacing-md);
}
```

### Scoped Variables

```css
.card {
  /* Component-level defaults */
  --card-padding: 1.5rem;
  --card-radius: 0.5rem;
  --card-shadow: 0 2px 4px rgba(0,0,0,0.1);

  padding: var(--card-padding);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

/* Override for specific variant */
.card.compact {
  --card-padding: 0.75rem;
}

.card.elevated {
  --card-shadow: 0 8px 16px rgba(0,0,0,0.15);
}
```

### Dynamic Values with JavaScript

```css
.progress-bar {
  width: calc(var(--progress, 0) * 1%);
  transition: width 0.3s ease;
}
```

```javascript
element.style.setProperty('--progress', 75);
```

### Responsive Variables

```css
:root {
  --container-width: 100%;
}

@media (min-width: 768px) {
  :root {
    --container-width: 720px;
  }
}

@media (min-width: 1024px) {
  :root {
    --container-width: 960px;
  }
}

.container {
  max-width: var(--container-width);
}
```

---

## Container Queries

### Basic Setup

```css
/* Define container */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* Query the container */
.card {
  padding: 1rem;
}

@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: auto 1fr;
    padding: 1.5rem;
  }
}

@container card (min-width: 600px) {
  .card {
    padding: 2rem;
    gap: 2rem;
  }
}
```

### Use Cases

```css
/* Sidebar widget that adapts */
.widget-container {
  container-type: inline-size;
}

.widget {
  display: flex;
  flex-direction: column;
}

@container (min-width: 300px) {
  .widget {
    flex-direction: row;
  }
}

/* Grid that adapts to card container */
.products-container {
  container-type: inline-size;
}

.product-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@container (min-width: 500px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@container (min-width: 800px) {
  .product-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### Container Query Units

```css
/* cqi = 1% of container inline size */
/* cqb = 1% of container block size */
/* cqw/cqh = width/height */
/* cqmin/cqmax = smaller/larger dimension */

.container {
  container-type: inline-size;
}

.responsive-text {
  font-size: clamp(1rem, 3cqi, 2rem);
  padding: 5cqi;
}
```

---

## CSS Nesting (Native)

### Basic Nesting

```css
.card {
  padding: 1rem;
  background: white;

  /* Nested element */
  & .title {
    font-size: 1.25rem;
    font-weight: bold;
  }

  & .content {
    color: gray;
  }

  /* Nested state */
  &:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }

  /* Nested modifier */
  &.featured {
    border: 2px solid gold;
  }
}
```

### Complex Nesting

```css
.nav {
  display: flex;

  & .item {
    padding: 0.5rem 1rem;

    & a {
      text-decoration: none;
      color: inherit;

      &:hover {
        color: var(--color-primary);
      }

      &[aria-current="page"] {
        font-weight: bold;
      }
    }
  }

  /* Media query inside selector */
  @media (max-width: 768px) {
    flex-direction: column;

    & .item {
      padding: 1rem;
    }
  }
}
```

### @ Rules Nesting

```css
.component {
  color: black;

  @media (prefers-color-scheme: dark) {
    color: white;
  }

  @supports (container-type: inline-size) {
    container-type: inline-size;
  }

  @layer components {
    /* Layer-specific styles */
  }
}
```

---

## :has() Selector

### Parent Selection

```css
/* Style parent when child has focus */
.form-group:has(input:focus) {
  background: var(--color-highlight);
}

/* Style card when it contains an image */
.card:has(> img) {
  padding: 0;

  & > img {
    border-radius: inherit;
  }
}

/* Navigation item containing current page */
.nav-item:has([aria-current="page"]) {
  background: var(--color-active);
}
```

### Sibling Selection

```css
/* Label when sibling input is required */
label:has(+ input:required)::after {
  content: " *";
  color: red;
}

/* Form valid state */
form:has(input:invalid) button[type="submit"] {
  opacity: 0.5;
  pointer-events: none;
}
```

### Complex Conditions

```css
/* Card with both image AND badge */
.card:has(img):has(.badge) {
  /* Special styling */
}

/* Any element that doesn't have children */
.container > *:not(:has(*)) {
  /* Leaf node styling */
}

/* Rows that contain a checkbox that's checked */
tr:has(input[type="checkbox"]:checked) {
  background: var(--color-selected);
}
```

---

## @layer (Cascade Layers)

### Basic Layer Order

```css
/* Define layer order - later = higher priority */
@layer reset, base, components, utilities;

@layer reset {
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
}

@layer base {
  body {
    font-family: system-ui;
    line-height: 1.5;
  }

  a {
    color: var(--color-link);
  }
}

@layer components {
  .button {
    /* Component styles */
  }

  .card {
    /* Component styles */
  }
}

@layer utilities {
  .sr-only { /* ... */ }
  .text-center { text-align: center; }
}
```

### Importing with Layers

```css
/* Import reset into specific layer */
@import url('reset.css') layer(reset);
@import url('base.css') layer(base);
@import url('components.css') layer(components);
@import url('utilities.css') layer(utilities);
```

### Nested Layers

```css
@layer components {
  @layer buttons {
    .btn { /* ... */ }
  }

  @layer cards {
    .card { /* ... */ }
  }
}

/* Reference nested layer */
@layer components.buttons {
  .btn-primary { /* ... */ }
}
```

---

## View Transitions API

### Basic Page Transitions

```css
/* Enable for same-document navigation */
@view-transition {
  navigation: auto;
}

/* Customize the transition */
::view-transition-old(root) {
  animation: fade-out 0.3s ease;
}

::view-transition-new(root) {
  animation: fade-in 0.3s ease;
}

@keyframes fade-out {
  to { opacity: 0; }
}

@keyframes fade-in {
  from { opacity: 0; }
}
```

### Named Transitions

```css
/* Give elements transition names */
.page-title {
  view-transition-name: title;
}

.hero-image {
  view-transition-name: hero;
}

/* Style specific transitions */
::view-transition-old(title) {
  animation: slide-out-left 0.3s ease;
}

::view-transition-new(title) {
  animation: slide-in-right 0.3s ease;
}

::view-transition-old(hero) {
  animation: scale-down 0.4s ease;
}

::view-transition-new(hero) {
  animation: scale-up 0.4s ease;
}
```

### JavaScript Control

```javascript
// Trigger transition programmatically
document.startViewTransition(() => {
  // Update DOM
  updateContent();
});

// With async content
document.startViewTransition(async () => {
  const data = await fetchData();
  renderContent(data);
});
```

---

## Subgrid

### Basic Subgrid

```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.grid-item {
  display: grid;
  /* Inherit parent's column tracks */
  grid-template-columns: subgrid;
  /* Span 3 columns of parent */
  grid-column: span 3;
}
```

### Card Grid Alignment

```css
/* Parent grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

/* Card with internal alignment */
.card {
  display: grid;
  grid-template-rows: auto 1fr auto;
  /* If parent was explicit, could use subgrid for rows */
}

/* With explicit parent for subgrid */
.explicit-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto 1fr auto auto;
  gap: 1rem 2rem;
}

.explicit-grid .card {
  display: grid;
  grid-template-rows: subgrid;
  grid-row: span 4;
}
```

---

## :where() and :is()

### :is() - Matches Any

```css
/* Before */
header a:hover,
nav a:hover,
footer a:hover {
  color: var(--color-link-hover);
}

/* After */
:is(header, nav, footer) a:hover {
  color: var(--color-link-hover);
}

/* Complex selectors */
:is(h1, h2, h3):is(:first-child, .intro) {
  margin-top: 0;
}
```

### :where() - Zero Specificity

```css
/* Base styles with zero specificity - easy to override */
:where(.button) {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
}

/* Can be overridden with single class */
.my-button {
  padding: 1rem 2rem; /* Will win */
}
```

### Practical Use Cases

```css
/* Reset with zero specificity */
:where(ul, ol) {
  list-style: none;
  padding: 0;
}

/* Easy override */
.styled-list {
  list-style: disc;
  padding-left: 2rem;
}

/* Simplify selectors */
:where(article, section, aside) :is(h1, h2, h3) {
  margin-top: 1.5em;
}
```

---

## clamp() and Fluid Values

### Fluid Typography

```css
:root {
  /* clamp(minimum, preferred, maximum) */
  --font-size-sm: clamp(0.8rem, 0.5vw + 0.7rem, 0.875rem);
  --font-size-base: clamp(1rem, 0.5vw + 0.85rem, 1.125rem);
  --font-size-lg: clamp(1.25rem, 1vw + 1rem, 1.5rem);
  --font-size-xl: clamp(1.5rem, 2vw + 1rem, 2rem);
  --font-size-2xl: clamp(2rem, 3vw + 1rem, 3rem);
  --font-size-hero: clamp(2.5rem, 6vw + 1rem, 5rem);
}

body {
  font-size: var(--font-size-base);
}

h1 {
  font-size: var(--font-size-hero);
}
```

### Fluid Spacing

```css
:root {
  --space-xs: clamp(0.25rem, 0.5vw, 0.5rem);
  --space-sm: clamp(0.5rem, 1vw, 1rem);
  --space-md: clamp(1rem, 2vw, 1.5rem);
  --space-lg: clamp(1.5rem, 3vw, 2.5rem);
  --space-xl: clamp(2rem, 5vw, 4rem);
  --space-section: clamp(3rem, 8vw, 6rem);
}

section {
  padding-block: var(--space-section);
}

.card {
  padding: var(--space-md);
  gap: var(--space-sm);
}
```

### Fluid Container

```css
.container {
  width: min(100% - 2rem, 1200px);
  margin-inline: auto;
}

/* Or with clamp */
.container {
  width: clamp(320px, 90%, 1200px);
  margin-inline: auto;
}
```

---

## Browser Support (2025)

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Custom Properties | ✅ | ✅ | ✅ | ✅ |
| Container Queries | ✅ | ✅ | ✅ | ✅ |
| CSS Nesting | ✅ | ✅ | ✅ | ✅ |
| :has() | ✅ | ✅ | ✅ | ✅ |
| @layer | ✅ | ✅ | ✅ | ✅ |
| View Transitions | ✅ | 🔄 | 🔄 | ✅ |
| Subgrid | ✅ | ✅ | ✅ | ✅ |
| :is() / :where() | ✅ | ✅ | ✅ | ✅ |
| clamp() | ✅ | ✅ | ✅ | ✅ |

✅ = Full support | 🔄 = Partial/in progress

---

**Version:** 1.0
**Last Updated:** 2025
