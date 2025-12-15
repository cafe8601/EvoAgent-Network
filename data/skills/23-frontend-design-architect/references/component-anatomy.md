# Component Anatomy Guide

## Overview

This guide defines the structural patterns and composition principles for building maintainable, scalable UI components.

---

## Component Structure

### Anatomy Layers

```
┌─────────────────────────────────────────────────────────┐
│  CONTAINER (Layout & Positioning)                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │  WRAPPER (Spacing & Alignment)                    │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  CONTENT (Visual & Interactive)             │  │  │
│  │  │  ┌───────┐ ┌─────────────┐ ┌───────────┐   │  │  │
│  │  │  │ SLOT  │ │   SLOT      │ │   SLOT    │   │  │  │
│  │  │  │ start │ │   default   │ │   end     │   │  │  │
│  │  │  └───────┘ └─────────────┘ └───────────┘   │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Purpose | CSS Properties |
|-------|---------|----------------|
| **Container** | External positioning | `position`, `grid-area`, `margin` |
| **Wrapper** | Internal spacing | `padding`, `gap`, `align-items` |
| **Content** | Visual styling | `background`, `border`, `shadow` |
| **Slots** | Content insertion | Flexible content areas |

---

## Button Component Anatomy

### Structure

```html
<button class="button">
  <!-- Start Slot: Icon, Badge -->
  <span class="button__start">
    <svg class="button__icon">...</svg>
  </span>

  <!-- Default Slot: Label -->
  <span class="button__label">
    Click me
  </span>

  <!-- End Slot: Loading, Count -->
  <span class="button__end">
    <span class="button__count">5</span>
  </span>
</button>
```

### CSS Architecture

```css
/* Container Layer */
.button {
  /* Reset */
  appearance: none;
  border: none;
  background: none;
  font: inherit;
  cursor: pointer;

  /* Layout */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--button-gap, 0.5rem);

  /* Sizing */
  height: var(--button-height);
  padding-inline: var(--button-padding-x);

  /* Visual */
  background: var(--button-bg);
  color: var(--button-color);
  border-radius: var(--button-radius);

  /* Typography */
  font-weight: var(--button-font-weight, 500);
  font-size: var(--button-font-size);
  line-height: 1;

  /* Interaction */
  transition: all 0.2s ease;
}

/* Slots */
.button__start,
.button__end {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.button__label {
  flex: 1 1 auto;
  text-align: center;
}

.button__icon {
  width: 1.25em;
  height: 1.25em;
}

/* States */
.button:hover {
  --button-bg: var(--button-bg-hover);
}

.button:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

.button:active {
  transform: scale(0.98);
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

---

## Card Component Anatomy

### Structure

```html
<article class="card">
  <!-- Media Slot -->
  <div class="card__media">
    <img src="..." alt="..." class="card__image" />
    <span class="card__badge">New</span>
  </div>

  <!-- Header Slot -->
  <header class="card__header">
    <h3 class="card__title">Title</h3>
    <p class="card__subtitle">Subtitle</p>
  </header>

  <!-- Body Slot -->
  <div class="card__body">
    <p class="card__description">Content here...</p>
  </div>

  <!-- Footer Slot -->
  <footer class="card__footer">
    <button class="button">Action</button>
  </footer>
</article>
```

### CSS Architecture

```css
/* Container */
.card {
  --card-padding: 1.5rem;
  --card-radius: 0.75rem;
  --card-shadow: 0 1px 3px rgba(0,0,0,0.1);

  display: flex;
  flex-direction: column;
  background: var(--card-bg, white);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

/* Media Slot */
.card__media {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.card__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card__badge {
  position: absolute;
  top: var(--card-padding);
  right: var(--card-padding);
}

/* Content Slots */
.card__header,
.card__body,
.card__footer {
  padding-inline: var(--card-padding);
}

.card__header {
  padding-top: var(--card-padding);
}

.card__body {
  flex: 1;
}

.card__footer {
  padding-bottom: var(--card-padding);
  margin-top: auto;
}

/* Typography */
.card__title {
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.3;
  margin: 0;
}

.card__subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0.25rem 0 0;
}

.card__description {
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}
```

---

## Input Component Anatomy

### Structure

```html
<div class="input-group">
  <!-- Label -->
  <label class="input-group__label" for="email">
    Email
    <span class="input-group__required" aria-hidden="true">*</span>
  </label>

  <!-- Hint -->
  <span class="input-group__hint" id="email-hint">
    We'll never share your email.
  </span>

  <!-- Input Wrapper -->
  <div class="input-group__wrapper">
    <!-- Start Addon -->
    <span class="input-group__addon input-group__addon--start">
      <svg>...</svg>
    </span>

    <!-- Input -->
    <input
      type="email"
      id="email"
      class="input-group__input"
      aria-describedby="email-hint email-error"
      aria-invalid="false"
    />

    <!-- End Addon -->
    <button class="input-group__addon input-group__addon--end">
      <svg>...</svg>
    </button>
  </div>

  <!-- Error -->
  <span class="input-group__error" id="email-error" role="alert">
    Please enter a valid email.
  </span>
</div>
```

### CSS Architecture

```css
/* Container */
.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

/* Label */
.input-group__label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.input-group__required {
  color: var(--color-error);
  margin-left: 0.125rem;
}

/* Hint & Error */
.input-group__hint,
.input-group__error {
  font-size: 0.8125rem;
}

.input-group__hint {
  color: var(--color-text-secondary);
}

.input-group__error {
  color: var(--color-error);
  display: none;
}

.input-group:has([aria-invalid="true"]) .input-group__error {
  display: block;
}

/* Input Wrapper */
.input-group__wrapper {
  display: flex;
  align-items: stretch;
  background: var(--input-bg, white);
  border: 1px solid var(--input-border, #d1d5db);
  border-radius: var(--input-radius, 0.375rem);
  transition: all 0.2s ease;
}

.input-group__wrapper:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.input-group:has([aria-invalid="true"]) .input-group__wrapper {
  border-color: var(--color-error);
}

/* Input */
.input-group__input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.625rem 0.75rem;
  font: inherit;
  color: var(--color-text-primary);
  min-width: 0;
}

.input-group__input:focus {
  outline: none;
}

.input-group__input::placeholder {
  color: var(--color-text-tertiary);
}

/* Addons */
.input-group__addon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.75rem;
  color: var(--color-text-secondary);
}

.input-group__addon--start {
  border-right: 1px solid var(--input-border);
}

.input-group__addon--end {
  border-left: 1px solid var(--input-border);
}
```

---

## Modal Component Anatomy

### Structure

```html
<!-- Backdrop -->
<div class="modal-backdrop" aria-hidden="true"></div>

<!-- Modal -->
<div
  class="modal"
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
>
  <!-- Header -->
  <header class="modal__header">
    <h2 class="modal__title" id="modal-title">Modal Title</h2>
    <button class="modal__close" aria-label="Close modal">
      <svg>...</svg>
    </button>
  </header>

  <!-- Body -->
  <div class="modal__body" id="modal-description">
    <p>Modal content goes here...</p>
  </div>

  <!-- Footer -->
  <footer class="modal__footer">
    <button class="button button--ghost">Cancel</button>
    <button class="button button--primary">Confirm</button>
  </footer>
</div>
```

### CSS Architecture

```css
/* Backdrop */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 100;
}

/* Modal Container */
.modal {
  --modal-width: min(90vw, 500px);
  --modal-padding: 1.5rem;
  --modal-radius: 1rem;

  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);

  width: var(--modal-width);
  max-height: 85vh;

  display: flex;
  flex-direction: column;

  background: var(--modal-bg, white);
  border-radius: var(--modal-radius);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

  z-index: 101;
}

/* Header */
.modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--modal-padding);
  border-bottom: 1px solid var(--color-border);
}

.modal__title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.modal__close {
  appearance: none;
  border: none;
  background: transparent;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.modal__close:hover {
  background: var(--color-bg-secondary);
}

/* Body */
.modal__body {
  flex: 1;
  overflow-y: auto;
  padding: var(--modal-padding);
}

/* Footer */
.modal__footer {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  padding: var(--modal-padding);
  border-top: 1px solid var(--color-border);
}
```

---

## Composition Patterns

### Compound Components

```jsx
// Parent provides context
<Tabs defaultValue="tab1">
  <Tabs.List>
    <Tabs.Trigger value="tab1">Tab 1</Tabs.Trigger>
    <Tabs.Trigger value="tab2">Tab 2</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Panel value="tab1">Content 1</Tabs.Panel>
  <Tabs.Panel value="tab2">Content 2</Tabs.Panel>
</Tabs>
```

### Slot Pattern

```jsx
<Card
  media={<img src="..." alt="..." />}
  header={<h3>Title</h3>}
  footer={<Button>Action</Button>}
>
  Card body content
</Card>
```

### Render Props

```jsx
<Listbox>
  {({ open, selected }) => (
    <>
      <Listbox.Button>
        {selected?.name || 'Select option'}
      </Listbox.Button>
      {open && (
        <Listbox.Options>
          {options.map(option => (
            <Listbox.Option key={option.id} value={option}>
              {option.name}
            </Listbox.Option>
          ))}
        </Listbox.Options>
      )}
    </>
  )}
</Listbox>
```

---

## Size Variants

### Token-Based Sizing

```css
.component {
  /* Size tokens */
  --size-sm: 32px;
  --size-md: 40px;
  --size-lg: 48px;
  --size-xl: 56px;

  /* Padding scale */
  --padding-sm: 0.5rem 0.75rem;
  --padding-md: 0.625rem 1rem;
  --padding-lg: 0.75rem 1.25rem;
  --padding-xl: 1rem 1.5rem;

  /* Font scale */
  --font-sm: 0.8125rem;
  --font-md: 0.875rem;
  --font-lg: 1rem;
  --font-xl: 1.125rem;
}

/* Apply variants */
.button--sm {
  height: var(--size-sm);
  padding: var(--padding-sm);
  font-size: var(--font-sm);
}

.button--md {
  height: var(--size-md);
  padding: var(--padding-md);
  font-size: var(--font-md);
}

.button--lg {
  height: var(--size-lg);
  padding: var(--padding-lg);
  font-size: var(--font-lg);
}
```

---

## State Management

### Interactive States

```css
/* Base */
.component {
  --bg: var(--color-bg);
  --color: var(--color-text);
  --border: var(--color-border);

  background: var(--bg);
  color: var(--color);
  border-color: var(--border);
}

/* Hover */
.component:hover:not(:disabled) {
  --bg: var(--color-bg-hover);
}

/* Focus */
.component:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

/* Active */
.component:active:not(:disabled) {
  --bg: var(--color-bg-active);
  transform: scale(0.98);
}

/* Disabled */
.component:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading */
.component[data-loading="true"] {
  pointer-events: none;
  position: relative;
}

.component[data-loading="true"]::after {
  content: "";
  /* Spinner styles */
}
```

---

## Best Practices

### Naming Conventions

| Pattern | Example | Use Case |
|---------|---------|----------|
| **Block** | `.card` | Component root |
| **Element** | `.card__header` | Component parts |
| **Modifier** | `.card--featured` | Variations |
| **State** | `.card.is-active` | Dynamic states |
| **Utility** | `[data-size="lg"]` | Data attributes |

### Props to CSS

```jsx
// Component props map to CSS custom properties
<Button
  variant="primary"  // → --variant: primary
  size="lg"          // → --size: lg
  rounded={true}     // → --rounded: true
/>
```

```css
.button {
  /* Use props via data attributes or CSS variables */
  border-radius: var(--rounded, var(--radius-default));
}

.button[data-variant="primary"] {
  --bg: var(--color-primary);
  --color: white;
}

.button[data-size="lg"] {
  --height: var(--size-lg);
  --padding: var(--padding-lg);
}
```

---

**Version:** 1.0
**Last Updated:** 2025
