# CSS Migration Guides

## Overview

This guide provides step-by-step migration patterns for moving between CSS architectures and adopting modern CSS features.

---

## BEM to CSS Modules

### Before (BEM)

```css
/* styles/button.css */
.button { }
.button--primary { }
.button--secondary { }
.button__icon { }
.button__label { }
.button--loading { }
```

```html
<button class="button button--primary button--loading">
  <span class="button__icon">...</span>
  <span class="button__label">Submit</span>
</button>
```

### After (CSS Modules)

```css
/* Button.module.css */
.button { }
.primary { }
.secondary { }
.icon { }
.label { }
.loading { }
```

```jsx
import styles from './Button.module.css';
import clsx from 'clsx';

<button className={clsx(
  styles.button,
  styles.primary,
  isLoading && styles.loading
)}>
  <span className={styles.icon}>...</span>
  <span className={styles.label}>Submit</span>
</button>
```

### Migration Steps

1. **Create module file**: Rename `component.css` to `Component.module.css`

2. **Simplify class names**:
   ```css
   /* Before */
   .button__icon { }

   /* After */
   .icon { }
   ```

3. **Update imports**:
   ```jsx
   // Before
   import './styles/button.css';

   // After
   import styles from './Button.module.css';
   ```

4. **Replace class strings**:
   ```jsx
   // Before
   className="button button--primary"

   // After
   className={`${styles.button} ${styles.primary}`}
   ```

5. **Use clsx for conditionals** (optional):
   ```jsx
   className={clsx(styles.button, {
     [styles.primary]: variant === 'primary',
     [styles.loading]: isLoading
   })}
   ```

---

## CSS to Tailwind

### Before (Vanilla CSS)

```css
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 1.5rem;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.card__title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.card__description {
  color: #6b7280;
  font-size: 0.875rem;
}
```

### After (Tailwind)

```html
<div class="bg-white rounded-lg shadow-sm hover:shadow-md p-6 transition-shadow">
  <h3 class="text-xl font-semibold mb-2">Title</h3>
  <p class="text-gray-500 text-sm">Description</p>
</div>
```

### Migration Strategy

#### Step 1: Map CSS to Utilities

| CSS Property | Tailwind Class |
|--------------|----------------|
| `background: white` | `bg-white` |
| `border-radius: 8px` | `rounded-lg` |
| `box-shadow: ...` | `shadow-sm` |
| `padding: 1.5rem` | `p-6` |
| `font-size: 1.25rem` | `text-xl` |
| `font-weight: 600` | `font-semibold` |
| `margin-bottom: 0.5rem` | `mb-2` |
| `color: #6b7280` | `text-gray-500` |

#### Step 2: Configure Theme (if needed)

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        // Map existing color palette
        'brand': {
          500: '#your-brand-color',
        }
      },
      spacing: {
        // Custom spacing if needed
      }
    }
  }
}
```

#### Step 3: Extract Repeated Patterns

```css
/* For highly reused patterns */
@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-lg
           hover:bg-blue-700 transition-colors font-medium;
  }

  .card {
    @apply bg-white rounded-lg shadow-sm hover:shadow-md
           p-6 transition-shadow;
  }
}
```

---

## Tailwind to CSS Modules

### Before (Tailwind)

```html
<button class="px-4 py-2 bg-blue-600 text-white rounded-lg
               hover:bg-blue-700 focus:ring-2 focus:ring-blue-500
               focus:ring-offset-2 disabled:opacity-50
               transition-colors font-medium">
  Submit
</button>
```

### After (CSS Modules)

```css
/* Button.module.css */
.button {
  padding: 0.5rem 1rem;
  background-color: #2563eb;
  color: white;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: background-color 0.15s, box-shadow 0.15s;
}

.button:hover {
  background-color: #1d4ed8;
}

.button:focus {
  outline: none;
  box-shadow: 0 0 0 2px white, 0 0 0 4px #3b82f6;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Migration Steps

1. **Create mapping reference**:
   Document Tailwind classes used and their CSS equivalents

2. **Extract to CSS file**:
   Convert utility classes to semantic CSS

3. **Use design tokens**:
   ```css
   .button {
     padding: var(--space-2) var(--space-4);
     background-color: var(--color-primary);
     border-radius: var(--radius-md);
   }
   ```

4. **Update component**:
   ```jsx
   // Before
   className="px-4 py-2 bg-blue-600..."

   // After
   className={styles.button}
   ```

---

## CSS-in-JS to CSS Modules

### Before (Styled Components)

```jsx
import styled from 'styled-components';

const Button = styled.button`
  padding: ${props => props.size === 'lg' ? '1rem 2rem' : '0.5rem 1rem'};
  background: ${props => props.variant === 'primary'
    ? props.theme.colors.primary
    : 'transparent'};
  color: ${props => props.variant === 'primary'
    ? 'white'
    : props.theme.colors.primary};
  border: 2px solid ${props => props.theme.colors.primary};
  border-radius: ${props => props.theme.radii.md};

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
    border-color: ${props => props.theme.colors.primaryDark};
    color: white;
  }
`;

<Button variant="primary" size="lg">Submit</Button>
```

### After (CSS Modules)

```css
/* Button.module.css */
.button {
  --button-padding: 0.5rem 1rem;

  padding: var(--button-padding);
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-md);
  transition: all 0.2s;
}

/* Variants */
.primary {
  background: var(--color-primary);
  color: white;
}

.secondary {
  background: transparent;
  color: var(--color-primary);
}

/* Sizes */
.lg {
  --button-padding: 1rem 2rem;
}

/* States */
.button:hover {
  background: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
  color: white;
}
```

```jsx
import styles from './Button.module.css';
import clsx from 'clsx';

function Button({ variant = 'primary', size = 'md', children }) {
  return (
    <button className={clsx(
      styles.button,
      styles[variant],
      size === 'lg' && styles.lg
    )}>
      {children}
    </button>
  );
}
```

### Migration Considerations

| CSS-in-JS Feature | CSS Modules Alternative |
|-------------------|-------------------------|
| `props => ...` | CSS custom properties + data attributes |
| `theme.colors.x` | CSS variables `var(--color-x)` |
| `${props.theme.x}` | `var(--x)` |
| Dynamic values | CSS custom properties via JS |
| Nested `&:hover` | Regular `:hover` selectors |

---

## Adding Container Queries

### Before (Media Queries Only)

```css
.card {
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

@media (min-width: 600px) {
  .card {
    flex-direction: row;
    padding: 1.5rem;
  }
}
```

### After (Container Queries)

```css
/* Parent container */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* Component adapts to container, not viewport */
.card {
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

@container card (min-width: 400px) {
  .card {
    flex-direction: row;
    padding: 1.5rem;
  }
}

@container card (min-width: 600px) {
  .card {
    gap: 2rem;
    padding: 2rem;
  }
}
```

### Migration Steps

1. **Identify component-level breakpoints**:
   Find components that should adapt based on their container

2. **Add container to parent**:
   ```css
   .parent {
     container-type: inline-size;
   }
   ```

3. **Convert media queries to container queries**:
   ```css
   /* Before */
   @media (min-width: 600px) { ... }

   /* After */
   @container (min-width: 400px) { ... }
   ```

4. **Add fallback for older browsers** (if needed):
   ```css
   @supports (container-type: inline-size) {
     .parent {
       container-type: inline-size;
     }
   }
   ```

---

## Adopting CSS Nesting

### Before (Flat CSS)

```css
.nav {
  display: flex;
  gap: 1rem;
}

.nav .item {
  padding: 0.5rem 1rem;
}

.nav .item:hover {
  background: var(--color-bg-hover);
}

.nav .item.active {
  font-weight: bold;
}

.nav .item a {
  color: inherit;
  text-decoration: none;
}

@media (max-width: 768px) {
  .nav {
    flex-direction: column;
  }
}
```

### After (Nested CSS)

```css
.nav {
  display: flex;
  gap: 1rem;

  & .item {
    padding: 0.5rem 1rem;

    &:hover {
      background: var(--color-bg-hover);
    }

    &.active {
      font-weight: bold;
    }

    & a {
      color: inherit;
      text-decoration: none;
    }
  }

  @media (max-width: 768px) {
    flex-direction: column;
  }
}
```

### Migration Rules

1. **Child selectors**: Use `& .child`
2. **Pseudo-classes**: Use `&:hover`, `&:focus`
3. **Modifiers**: Use `&.modifier`
4. **Media queries**: Nest directly inside selector
5. **Pseudo-elements**: Use `&::before`, `&::after`

---

## Adopting CSS Layers

### Before (Specificity Conflicts)

```css
/* Often leads to specificity wars */
.button { /* base styles */ }
.button.primary { /* variant */ }
.card .button { /* context override - higher specificity! */ }
button.button { /* reset override */ }
```

### After (CSS Layers)

```css
/* Explicit cascade control */
@layer reset, base, components, utilities;

@layer reset {
  button {
    appearance: none;
    border: none;
    font: inherit;
  }
}

@layer base {
  .button {
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
  }
}

@layer components {
  .button.primary {
    background: var(--color-primary);
    color: white;
  }

  .card .button {
    /* No longer wins by specificity */
    /* Wins by layer order instead */
  }
}

@layer utilities {
  .mt-4 { margin-top: 1rem; }
}
```

### Layer Order Strategy

```
1. reset       (lowest priority)
2. tokens
3. base
4. layouts
5. components
6. utilities   (highest priority)
```

---

## Token Migration

### Before (Hardcoded Values)

```css
.card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.card-title {
  font-size: 20px;
  color: #111827;
  margin-bottom: 8px;
}
```

### After (Design Tokens)

```css
:root {
  /* Primitives */
  --gray-200: #e5e7eb;
  --gray-900: #111827;
  --radius-lg: 0.5rem;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);

  /* Semantics */
  --color-bg-card: white;
  --color-border: var(--gray-200);
  --color-text-primary: var(--gray-900);
  --space-6: 1.5rem;
  --space-2: 0.5rem;
  --text-xl: 1.25rem;
}

.card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.card-title {
  font-size: var(--text-xl);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}
```

### Migration Process

1. **Audit existing values**: Extract all hardcoded colors, sizes, spacing
2. **Create primitive tokens**: Raw values with descriptive names
3. **Create semantic tokens**: Purpose-based references to primitives
4. **Replace hardcoded values**: Systematically replace with `var(--token)`
5. **Validate dark mode**: Ensure tokens work in all themes

---

## Migration Checklist

### Before Starting

- [ ] Document current architecture
- [ ] Identify pain points
- [ ] Define target architecture
- [ ] Create migration plan with phases
- [ ] Set up parallel infrastructure

### During Migration

- [ ] Migrate incrementally (file by file)
- [ ] Maintain backwards compatibility
- [ ] Test each migrated component
- [ ] Update documentation
- [ ] Review with team

### After Completion

- [ ] Remove deprecated code
- [ ] Update build configuration
- [ ] Document new patterns
- [ ] Train team on new approach
- [ ] Monitor for issues

---

**Version:** 1.0
**Last Updated:** 2025
