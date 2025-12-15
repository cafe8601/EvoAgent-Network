# Design Token Architecture Guide

## Overview

This guide covers design token architecture patterns, from simple single-tier systems to complex enterprise multi-tier implementations with theming.

---

## Token Tiers

### Three-Tier Architecture

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

### Tier Definitions

| Tier | Purpose | Naming | Example |
|------|---------|--------|---------|
| **Primitive** | Raw values | Descriptive | `--blue-500: #3b82f6` |
| **Semantic** | Intent-based | Purposeful | `--color-primary: var(--blue-500)` |
| **Component** | Component-specific | Scoped | `--button-bg: var(--color-primary)` |

---

## Primitive Tokens (Tier 1)

### Color Primitives

```css
:root {
  /* Gray Scale */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  --gray-950: #030712;

  /* Primary Scale (Blue) */
  --blue-50: #eff6ff;
  --blue-100: #dbeafe;
  --blue-200: #bfdbfe;
  --blue-300: #93c5fd;
  --blue-400: #60a5fa;
  --blue-500: #3b82f6;
  --blue-600: #2563eb;
  --blue-700: #1d4ed8;
  --blue-800: #1e40af;
  --blue-900: #1e3a8a;
  --blue-950: #172554;

  /* Semantic Colors */
  --green-500: #22c55e;
  --green-600: #16a34a;
  --red-500: #ef4444;
  --red-600: #dc2626;
  --yellow-500: #eab308;
  --yellow-600: #ca8a04;
}
```

### Space Primitives

```css
:root {
  /* Base: 4px grid */
  --space-0: 0;
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
  --space-32: 8rem;     /* 128px */
}
```

### Typography Primitives

```css
:root {
  /* Font Families */
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-serif: Georgia, Cambria, 'Times New Roman', Times, serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */
  --text-5xl: 3rem;       /* 48px */
  --text-6xl: 3.75rem;    /* 60px */

  /* Font Weights */
  --font-thin: 100;
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  --font-extrabold: 800;

  /* Line Heights */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;

  /* Letter Spacing */
  --tracking-tighter: -0.05em;
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
  --tracking-widest: 0.1em;
}
```

### Other Primitives

```css
:root {
  /* Border Radius */
  --radius-none: 0;
  --radius-sm: 0.125rem;  /* 2px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  --radius-2xl: 1rem;     /* 16px */
  --radius-3xl: 1.5rem;   /* 24px */
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
  --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);

  /* Z-Index */
  --z-0: 0;
  --z-10: 10;
  --z-20: 20;
  --z-30: 30;
  --z-40: 40;
  --z-50: 50;

  /* Transitions */
  --duration-75: 75ms;
  --duration-100: 100ms;
  --duration-150: 150ms;
  --duration-200: 200ms;
  --duration-300: 300ms;
  --duration-500: 500ms;
  --duration-700: 700ms;
  --duration-1000: 1000ms;

  --ease-linear: linear;
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## Semantic Tokens (Tier 2)

### Color Semantics

```css
:root {
  /* Background */
  --color-bg-primary: var(--gray-50);
  --color-bg-secondary: var(--gray-100);
  --color-bg-tertiary: var(--gray-200);
  --color-bg-inverse: var(--gray-900);
  --color-bg-elevated: white;

  /* Text */
  --color-text-primary: var(--gray-900);
  --color-text-secondary: var(--gray-600);
  --color-text-tertiary: var(--gray-500);
  --color-text-inverse: white;
  --color-text-disabled: var(--gray-400);

  /* Border */
  --color-border-default: var(--gray-200);
  --color-border-strong: var(--gray-300);
  --color-border-focus: var(--blue-500);

  /* Action */
  --color-action-primary: var(--blue-600);
  --color-action-primary-hover: var(--blue-700);
  --color-action-primary-active: var(--blue-800);
  --color-action-secondary: var(--gray-100);
  --color-action-secondary-hover: var(--gray-200);

  /* Status */
  --color-success: var(--green-500);
  --color-success-bg: var(--green-50);
  --color-warning: var(--yellow-500);
  --color-warning-bg: var(--yellow-50);
  --color-error: var(--red-500);
  --color-error-bg: var(--red-50);
  --color-info: var(--blue-500);
  --color-info-bg: var(--blue-50);
}
```

### Spacing Semantics

```css
:root {
  /* Component Spacing */
  --space-component-xs: var(--space-1);
  --space-component-sm: var(--space-2);
  --space-component-md: var(--space-3);
  --space-component-lg: var(--space-4);
  --space-component-xl: var(--space-6);

  /* Layout Spacing */
  --space-layout-xs: var(--space-4);
  --space-layout-sm: var(--space-6);
  --space-layout-md: var(--space-8);
  --space-layout-lg: var(--space-12);
  --space-layout-xl: var(--space-16);
  --space-layout-2xl: var(--space-24);

  /* Gap */
  --gap-xs: var(--space-1);
  --gap-sm: var(--space-2);
  --gap-md: var(--space-4);
  --gap-lg: var(--space-6);
  --gap-xl: var(--space-8);
}
```

### Typography Semantics

```css
:root {
  /* Font Family */
  --font-body: var(--font-sans);
  --font-heading: var(--font-sans);
  --font-code: var(--font-mono);

  /* Body Text */
  --text-body-sm: var(--text-sm);
  --text-body-md: var(--text-base);
  --text-body-lg: var(--text-lg);

  /* Headings */
  --text-heading-sm: var(--text-lg);
  --text-heading-md: var(--text-xl);
  --text-heading-lg: var(--text-2xl);
  --text-heading-xl: var(--text-3xl);
  --text-heading-2xl: var(--text-4xl);
  --text-heading-hero: var(--text-5xl);

  /* Line Height */
  --leading-body: var(--leading-relaxed);
  --leading-heading: var(--leading-tight);
}
```

---

## Component Tokens (Tier 3)

### Button Tokens

```css
:root {
  /* Size Tokens */
  --button-height-sm: 2rem;      /* 32px */
  --button-height-md: 2.5rem;    /* 40px */
  --button-height-lg: 3rem;      /* 48px */

  --button-padding-sm: var(--space-2) var(--space-3);
  --button-padding-md: var(--space-2) var(--space-4);
  --button-padding-lg: var(--space-3) var(--space-6);

  --button-gap: var(--space-2);
  --button-radius: var(--radius-md);

  /* Typography */
  --button-font-size-sm: var(--text-sm);
  --button-font-size-md: var(--text-sm);
  --button-font-size-lg: var(--text-base);
  --button-font-weight: var(--font-medium);

  /* Primary Variant */
  --button-primary-bg: var(--color-action-primary);
  --button-primary-bg-hover: var(--color-action-primary-hover);
  --button-primary-bg-active: var(--color-action-primary-active);
  --button-primary-color: var(--color-text-inverse);

  /* Secondary Variant */
  --button-secondary-bg: var(--color-action-secondary);
  --button-secondary-bg-hover: var(--color-action-secondary-hover);
  --button-secondary-color: var(--color-text-primary);

  /* Ghost Variant */
  --button-ghost-bg: transparent;
  --button-ghost-bg-hover: var(--color-action-secondary);
  --button-ghost-color: var(--color-text-primary);

  /* Transition */
  --button-transition: all var(--duration-150) var(--ease-out);
}
```

### Input Tokens

```css
:root {
  /* Size */
  --input-height-sm: 2rem;
  --input-height-md: 2.5rem;
  --input-height-lg: 3rem;

  --input-padding-x: var(--space-3);
  --input-padding-y: var(--space-2);

  /* Visual */
  --input-bg: white;
  --input-bg-disabled: var(--color-bg-secondary);
  --input-border: var(--color-border-default);
  --input-border-hover: var(--color-border-strong);
  --input-border-focus: var(--color-border-focus);
  --input-border-error: var(--color-error);
  --input-radius: var(--radius-md);

  /* Typography */
  --input-font-size: var(--text-body-md);
  --input-color: var(--color-text-primary);
  --input-placeholder: var(--color-text-tertiary);

  /* Focus Ring */
  --input-focus-ring: 0 0 0 3px rgba(59, 130, 246, 0.15);
  --input-error-ring: 0 0 0 3px rgba(239, 68, 68, 0.15);
}
```

### Card Tokens

```css
:root {
  --card-padding-sm: var(--space-4);
  --card-padding-md: var(--space-6);
  --card-padding-lg: var(--space-8);

  --card-bg: var(--color-bg-elevated);
  --card-border: var(--color-border-default);
  --card-radius: var(--radius-xl);
  --card-shadow: var(--shadow-md);
  --card-shadow-hover: var(--shadow-lg);

  --card-header-gap: var(--space-1);
  --card-section-gap: var(--space-4);
}
```

---

## Theming with Tokens

### Light/Dark Mode

```css
/* Light Mode (Default) */
:root {
  --color-bg-primary: var(--gray-50);
  --color-bg-secondary: var(--gray-100);
  --color-bg-elevated: white;
  --color-text-primary: var(--gray-900);
  --color-text-secondary: var(--gray-600);
  --color-border-default: var(--gray-200);
}

/* Dark Mode */
[data-theme="dark"] {
  --color-bg-primary: var(--gray-900);
  --color-bg-secondary: var(--gray-800);
  --color-bg-elevated: var(--gray-800);
  --color-text-primary: var(--gray-50);
  --color-text-secondary: var(--gray-400);
  --color-border-default: var(--gray-700);
}

/* System Preference */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --color-bg-primary: var(--gray-900);
    --color-bg-secondary: var(--gray-800);
    --color-bg-elevated: var(--gray-800);
    --color-text-primary: var(--gray-50);
    --color-text-secondary: var(--gray-400);
    --color-border-default: var(--gray-700);
  }
}
```

### Brand Theming

```css
/* Default Brand */
:root {
  --brand-50: var(--blue-50);
  --brand-100: var(--blue-100);
  --brand-500: var(--blue-500);
  --brand-600: var(--blue-600);
  --brand-700: var(--blue-700);

  --color-action-primary: var(--brand-600);
  --color-action-primary-hover: var(--brand-700);
}

/* Alternative Brand */
[data-brand="purple"] {
  --brand-50: #faf5ff;
  --brand-100: #f3e8ff;
  --brand-500: #a855f7;
  --brand-600: #9333ea;
  --brand-700: #7e22ce;
}

[data-brand="green"] {
  --brand-50: #f0fdf4;
  --brand-100: #dcfce7;
  --brand-500: #22c55e;
  --brand-600: #16a34a;
  --brand-700: #15803d;
}
```

---

## Token File Format

### JSON Format

```json
{
  "color": {
    "primitive": {
      "gray": {
        "50": { "value": "#f9fafb" },
        "100": { "value": "#f3f4f6" },
        "900": { "value": "#111827" }
      },
      "blue": {
        "500": { "value": "#3b82f6" },
        "600": { "value": "#2563eb" }
      }
    },
    "semantic": {
      "bg": {
        "primary": { "value": "{color.primitive.gray.50}" },
        "secondary": { "value": "{color.primitive.gray.100}" }
      },
      "text": {
        "primary": { "value": "{color.primitive.gray.900}" }
      },
      "action": {
        "primary": { "value": "{color.primitive.blue.600}" }
      }
    },
    "component": {
      "button": {
        "primary": {
          "bg": { "value": "{color.semantic.action.primary}" },
          "color": { "value": "#ffffff" }
        }
      }
    }
  }
}
```

### CSS Output

```css
/* Generated from tokens.json */
:root {
  /* Primitives */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-900: #111827;
  --color-blue-500: #3b82f6;
  --color-blue-600: #2563eb;

  /* Semantics */
  --color-bg-primary: var(--color-gray-50);
  --color-bg-secondary: var(--color-gray-100);
  --color-text-primary: var(--color-gray-900);
  --color-action-primary: var(--color-blue-600);

  /* Components */
  --button-primary-bg: var(--color-action-primary);
  --button-primary-color: #ffffff;
}
```

---

## Scaling Tokens

### Minimal (10-20 tokens)

Best for: MVPs, prototypes, landing pages

```css
:root {
  --color-primary: #3b82f6;
  --color-secondary: #6b7280;
  --color-success: #22c55e;
  --color-error: #ef4444;
  --color-bg: #ffffff;
  --color-text: #111827;

  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 2rem;

  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-full: 9999px;

  --font-sans: system-ui, sans-serif;
}
```

### Standard (50-100 tokens)

Best for: Web apps, SaaS, e-commerce

```css
/* See Semantic Tokens section above */
```

### Enterprise (200+ tokens)

Best for: Design systems, multi-product, white-label

```css
/* Full three-tier architecture */
/* See all sections above */
```

---

## Token Naming Conventions

### Pattern

```
--{category}-{property}-{variant}-{state}
```

### Examples

| Token | Breakdown |
|-------|-----------|
| `--color-text-primary` | category-property-variant |
| `--button-bg-hover` | component-property-state |
| `--space-layout-lg` | category-context-size |
| `--text-heading-2xl` | category-variant-size |

### Categories

- **color**: Colors and gradients
- **space**: Margins, paddings, gaps
- **text**: Font sizes, families
- **font**: Font weights, line heights
- **radius**: Border radii
- **shadow**: Box shadows
- **z**: Z-index values
- **duration**: Animation durations
- **ease**: Easing functions

---

**Version:** 1.0
**Last Updated:** 2025
