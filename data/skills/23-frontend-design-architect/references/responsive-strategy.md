# Responsive Design Strategy Guide

## Overview

This guide covers modern responsive design strategies, including viewport-based, container-based, and hybrid approaches with practical implementation patterns.

---

## Strategy Selection

### Decision Tree

```
RESPONSIVENESS NEEDED FOR?
│
├─ Page/Layout Level
│   └─ Viewport-Based (Media Queries)
│       @media (min-width: 768px) { ... }
│
├─ Component Level (Reusable)
│   └─ Container-Based (Container Queries)
│       @container (min-width: 400px) { ... }
│
├─ Content-Driven Sizing
│   └─ Intrinsic Design (Fluid Units)
│       clamp(), min(), max()
│
└─ Mixed Requirements (Most Common)
    └─ Hybrid Approach
        Media + Container + Fluid
```

---

## Viewport-Based Strategy

### Breakpoint System

```css
/* Mobile-First Breakpoints */
:root {
  --breakpoint-sm: 640px;   /* Large phones */
  --breakpoint-md: 768px;   /* Tablets */
  --breakpoint-lg: 1024px;  /* Small desktops */
  --breakpoint-xl: 1280px;  /* Desktops */
  --breakpoint-2xl: 1536px; /* Wide screens */
}

/* Usage */
/* Base: Mobile */
.element { ... }

/* Small devices and up */
@media (min-width: 640px) { ... }

/* Tablets and up */
@media (min-width: 768px) { ... }

/* Desktops and up */
@media (min-width: 1024px) { ... }

/* Large desktops and up */
@media (min-width: 1280px) { ... }

/* Wide screens and up */
@media (min-width: 1536px) { ... }
```

### Common Patterns

#### Layout Grid

```css
.grid-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .grid-layout {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .grid-layout {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }
}

@media (min-width: 1280px) {
  .grid-layout {
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
  }
}
```

#### Navigation

```css
.nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  padding: 0.75rem;
  background: white;
  border-top: 1px solid var(--color-border);
}

@media (min-width: 768px) {
  .nav {
    position: static;
    border-top: none;
    border-bottom: 1px solid var(--color-border);
    justify-content: flex-start;
    gap: 2rem;
    padding: 1rem 2rem;
  }
}
```

#### Typography Scale

```css
:root {
  --text-base: 1rem;
  --text-heading: 1.5rem;
  --text-hero: 2rem;
}

@media (min-width: 768px) {
  :root {
    --text-base: 1.0625rem;
    --text-heading: 2rem;
    --text-hero: 3rem;
  }
}

@media (min-width: 1280px) {
  :root {
    --text-base: 1.125rem;
    --text-heading: 2.5rem;
    --text-hero: 4rem;
  }
}
```

---

## Container-Based Strategy

### Container Setup

```css
/* Define containers */
.card-container {
  container-type: inline-size;
  container-name: card;
}

.sidebar-container {
  container-type: inline-size;
  container-name: sidebar;
}

.widget-container {
  container-type: inline-size;
  container-name: widget;
}
```

### Component Adaptation

```css
/* Card Component */
.card {
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

@container card (min-width: 300px) {
  .card {
    padding: 1.25rem;
  }
}

@container card (min-width: 400px) {
  .card {
    flex-direction: row;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .card__media {
    flex: 0 0 40%;
  }

  .card__content {
    flex: 1;
  }
}

@container card (min-width: 600px) {
  .card {
    padding: 2rem;
  }

  .card__media {
    flex: 0 0 300px;
  }
}
```

### Container Query Units

```css
/* cqi = 1% of container inline size */
/* cqb = 1% of container block size */

.container {
  container-type: inline-size;
}

.responsive-element {
  /* Fluid sizing based on container */
  font-size: clamp(0.875rem, 3cqi, 1.25rem);
  padding: 4cqi;
  margin-bottom: 2cqi;
}
```

---

## Intrinsic Design Strategy

### Fluid Typography

```css
:root {
  /* clamp(min, preferred, max) */
  --text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
  --text-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
  --text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-lg: clamp(1.125rem, 1rem + 0.625vw, 1.375rem);
  --text-xl: clamp(1.25rem, 1.1rem + 0.75vw, 1.625rem);
  --text-2xl: clamp(1.5rem, 1.25rem + 1.25vw, 2rem);
  --text-3xl: clamp(1.875rem, 1.5rem + 1.875vw, 2.5rem);
  --text-4xl: clamp(2.25rem, 1.75rem + 2.5vw, 3.5rem);
  --text-hero: clamp(2.5rem, 1.5rem + 5vw, 5rem);
}
```

### Fluid Spacing

```css
:root {
  --space-xs: clamp(0.25rem, 0.2rem + 0.25vw, 0.5rem);
  --space-sm: clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem);
  --space-md: clamp(1rem, 0.75rem + 1.25vw, 1.5rem);
  --space-lg: clamp(1.5rem, 1rem + 2.5vw, 2.5rem);
  --space-xl: clamp(2rem, 1.5rem + 2.5vw, 3rem);
  --space-2xl: clamp(3rem, 2rem + 5vw, 5rem);
  --space-section: clamp(4rem, 3rem + 5vw, 8rem);
}
```

### Fluid Container

```css
.container {
  /* Responsive width with clamped margins */
  width: min(100% - 2rem, 1200px);
  margin-inline: auto;
}

/* Alternative with clamp */
.container-alt {
  width: clamp(320px, 90%, 1200px);
  margin-inline: auto;
  padding-inline: clamp(1rem, 3vw, 2rem);
}
```

### Intrinsic Grid

```css
/* Auto-fit: Creates as many columns as will fit */
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr));
  gap: var(--space-md);
}

/* Auto-fill: Creates empty columns if space allows */
.auto-grid-fill {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--space-md);
}
```

---

## Hybrid Approach

### Combining Strategies

```css
/* Container for component-level responsiveness */
.content-area {
  container-type: inline-size;
}

/* Layout with viewport queries */
.page-layout {
  display: grid;
  gap: var(--space-md); /* Fluid spacing */
}

@media (min-width: 768px) {
  .page-layout {
    grid-template-columns: 250px 1fr;
  }
}

@media (min-width: 1280px) {
  .page-layout {
    grid-template-columns: 300px 1fr 300px;
  }
}

/* Component adapts to its container */
.widget {
  padding: 1rem;
}

@container (min-width: 400px) {
  .widget {
    padding: 1.5rem;
    display: grid;
    grid-template-columns: auto 1fr;
  }
}

/* Fluid text regardless of context */
.widget__title {
  font-size: clamp(1rem, 2.5cqi, 1.5rem);
}
```

### Best Practices

| Strategy | Use For | Avoid For |
|----------|---------|-----------|
| **Viewport** | Page layouts, navigation, global changes | Reusable components |
| **Container** | Reusable components, widgets, cards | Global layout changes |
| **Fluid/Intrinsic** | Typography, spacing, sizing | Binary layout changes |
| **Hybrid** | Complex applications | Simple static pages |

---

## Responsive Images

### Srcset and Sizes

```html
<img
  src="image-800.jpg"
  srcset="
    image-400.jpg 400w,
    image-800.jpg 800w,
    image-1200.jpg 1200w,
    image-1600.jpg 1600w
  "
  sizes="
    (min-width: 1280px) 1200px,
    (min-width: 768px) 50vw,
    100vw
  "
  alt="Responsive image"
/>
```

### Picture Element

```html
<picture>
  <!-- Art direction: different crops -->
  <source
    media="(min-width: 1024px)"
    srcset="hero-wide.jpg"
  />
  <source
    media="(min-width: 640px)"
    srcset="hero-medium.jpg"
  />
  <img src="hero-mobile.jpg" alt="Hero image" />
</picture>
```

### CSS Background Images

```css
.hero {
  background-image: url('hero-mobile.jpg');
  background-size: cover;
  background-position: center;
}

@media (min-width: 768px) {
  .hero {
    background-image: url('hero-tablet.jpg');
  }
}

@media (min-width: 1280px) {
  .hero {
    background-image: url('hero-desktop.jpg');
  }
}

/* For retina displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .hero {
    background-image: url('hero-mobile@2x.jpg');
  }
}
```

---

## Responsive Patterns

### Stack to Grid

```css
.stack-to-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 640px) {
  .stack-to-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .stack-to-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### Sidebar Layout

```css
/* Content-first, sidebar appears on larger screens */
.sidebar-layout {
  display: grid;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .sidebar-layout {
    grid-template-columns: 1fr 300px;
  }
}

/* Sidebar first in DOM, but appears right */
.sidebar-layout--reversed {
  display: grid;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .sidebar-layout--reversed {
    grid-template-columns: 300px 1fr;
  }

  .sidebar-layout--reversed .main {
    order: 2;
  }

  .sidebar-layout--reversed .sidebar {
    order: 1;
  }
}
```

### Holy Grail Layout

```css
.holy-grail {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr auto;
}

.holy-grail__body {
  display: grid;
  gap: 1rem;
}

@media (min-width: 768px) {
  .holy-grail__body {
    grid-template-columns: 200px 1fr;
  }
}

@media (min-width: 1024px) {
  .holy-grail__body {
    grid-template-columns: 200px 1fr 200px;
  }
}
```

### Responsive Tables

```css
/* Cards on mobile, table on desktop */
.responsive-table {
  display: block;
}

.responsive-table thead {
  display: none;
}

.responsive-table tr {
  display: block;
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.responsive-table td {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}

.responsive-table td::before {
  content: attr(data-label);
  font-weight: 600;
}

@media (min-width: 768px) {
  .responsive-table {
    display: table;
  }

  .responsive-table thead {
    display: table-header-group;
  }

  .responsive-table tr {
    display: table-row;
    margin-bottom: 0;
    padding: 0;
    border: none;
    border-radius: 0;
  }

  .responsive-table td {
    display: table-cell;
    padding: 1rem;
    border-bottom: 1px solid var(--color-border);
  }

  .responsive-table td::before {
    display: none;
  }
}
```

---

## Testing Responsive Designs

### Viewport Testing

```javascript
// Define test viewports
const viewports = [
  { name: 'mobile', width: 375, height: 667 },
  { name: 'mobile-large', width: 414, height: 896 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'laptop', width: 1366, height: 768 },
  { name: 'desktop', width: 1920, height: 1080 },
];

// Playwright example
for (const viewport of viewports) {
  test(`renders correctly at ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto('/');
    await expect(page).toHaveScreenshot(`home-${viewport.name}.png`);
  });
}
```

### Container Query Testing

```javascript
// Test component at different container sizes
const containerWidths = [300, 400, 500, 600, 800];

for (const width of containerWidths) {
  test(`card adapts at ${width}px container`, async ({ page }) => {
    await page.goto('/components/card');
    await page.$eval('.card-container', (el, w) => {
      el.style.width = `${w}px`;
    }, width);
    await expect(page.locator('.card')).toHaveScreenshot(`card-${width}.png`);
  });
}
```

### Checklist

- [ ] All breakpoints tested
- [ ] Touch targets 44px+ on mobile
- [ ] No horizontal scroll
- [ ] Text readable without zoom
- [ ] Images scale appropriately
- [ ] Forms usable on mobile
- [ ] Navigation accessible at all sizes
- [ ] Modals/dialogs work on mobile
- [ ] Tables readable on mobile
- [ ] Print styles considered

---

## Performance Considerations

### Media Query Order

```css
/* Mobile-first is more performant */
/* ✅ Progressive enhancement */
.element { /* mobile styles */ }
@media (min-width: 768px) { /* tablet styles */ }
@media (min-width: 1024px) { /* desktop styles */ }

/* ❌ Desktop-first requires overrides */
.element { /* desktop styles */ }
@media (max-width: 1023px) { /* tablet styles */ }
@media (max-width: 767px) { /* mobile styles */ }
```

### Reduce Reflows

```css
/* ✅ Use transform for animations */
.element {
  transform: translateX(0);
  transition: transform 0.3s;
}

@media (min-width: 768px) {
  .element {
    transform: translateX(100px);
  }
}

/* ❌ Avoid layout-triggering properties */
.element {
  left: 0;
  transition: left 0.3s;
}

@media (min-width: 768px) {
  .element {
    left: 100px;
  }
}
```

### Container Query Performance

```css
/* Limit container query scope */
.card-list {
  /* Don't make every element a container */
}

.card-container {
  container-type: inline-size;
  /* Only the direct wrapper needs container */
}
```

---

**Version:** 1.0
**Last Updated:** 2025
