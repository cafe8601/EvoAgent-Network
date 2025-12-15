# Accessibility Patterns

## Overview

This guide provides practical accessibility patterns with code examples. Following these patterns ensures WCAG 2.1 AA compliance.

---

## Color & Contrast

### Minimum Contrast Ratios

| Element Type | AA Minimum | AAA Enhanced |
|--------------|------------|--------------|
| Normal text (<18px or <14px bold) | 4.5:1 | 7:1 |
| Large text (≥18px or ≥14px bold) | 3:1 | 4.5:1 |
| UI components & graphics | 3:1 | 3:1 |

### Implementation

```css
:root {
  /* Define colors with contrast in mind */
  --color-text-primary: hsl(220, 13%, 13%);     /* On white: 12.6:1 */
  --color-text-secondary: hsl(220, 9%, 40%);    /* On white: 5.7:1 */
  --color-text-disabled: hsl(220, 9%, 55%);     /* On white: 3.5:1 ⚠️ */

  --color-bg-primary: hsl(0, 0%, 100%);
  --color-bg-secondary: hsl(220, 14%, 96%);
}

/* Ensure contrast for interactive elements */
.button-primary {
  background: hsl(210, 100%, 40%);  /* Dark enough for white text */
  color: white;
}

/* Don't rely on color alone */
.error-input {
  border-color: var(--color-error);
  /* Also add icon or text indicator */
}

.error-input::before {
  content: "⚠";
  margin-right: 0.5em;
}
```

### Testing Tools

- Chrome DevTools → Rendering → Emulate vision deficiencies
- axe DevTools browser extension
- WAVE browser extension
- Contrast ratio: https://webaim.org/resources/contrastchecker/

---

## Focus Management

### Visible Focus States

```css
/* Remove default and add custom */
:focus {
  outline: none;
}

:focus-visible {
  outline: 2px solid var(--color-focus, #005fcc);
  outline-offset: 2px;
}

/* Specific component focus */
.button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(0, 95, 204, 0.2);
}

/* Input focus */
.input:focus-visible {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 95, 204, 0.15);
}

/* Ensure focus visible in dark mode */
@media (prefers-color-scheme: dark) {
  :focus-visible {
    outline-color: var(--color-focus-dark, #66b3ff);
  }
}
```

### Focus Trap for Modals

```javascript
function trapFocus(element) {
  const focusableElements = element.querySelectorAll(
    'a[href], button:not([disabled]), textarea:not([disabled]), ' +
    'input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  );

  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  element.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      if (document.activeElement === firstFocusable) {
        lastFocusable.focus();
        e.preventDefault();
      }
    } else {
      if (document.activeElement === lastFocusable) {
        firstFocusable.focus();
        e.preventDefault();
      }
    }
  });

  // Focus first element on open
  firstFocusable?.focus();
}

// Usage
const modal = document.querySelector('.modal');
trapFocus(modal);
```

### Skip Link

```html
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <nav>...</nav>
  <main id="main-content" tabindex="-1">...</main>
</body>
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary);
  color: white;
  padding: 8px 16px;
  z-index: 100;
  transition: top 0.3s;
}

.skip-link:focus {
  top: 0;
}
```

---

## Keyboard Navigation

### Interactive Element Patterns

```html
<!-- Button: Use native button -->
<button type="button" onclick="handleClick()">
  Click me
</button>

<!-- Don't do this -->
<div onclick="handleClick()">Click me</div>

<!-- If you must use div, add these -->
<div role="button" tabindex="0"
     onclick="handleClick()"
     onkeydown="handleKeyDown(event)">
  Click me
</div>
```

```javascript
function handleKeyDown(event) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    handleClick();
  }
}
```

### Tab Order

```css
/* Visual order doesn't match DOM order - fix with CSS */
.flex-container {
  display: flex;
  flex-direction: row-reverse;
}

/* Better: Don't use CSS to reorder focusable content */
/* Or use tabindex to match visual order (use sparingly) */
```

### Keyboard Shortcuts

```javascript
document.addEventListener('keydown', (e) => {
  // Don't trigger when typing in inputs
  if (e.target.matches('input, textarea, select')) return;

  // Escape to close
  if (e.key === 'Escape') {
    closeModal();
    return;
  }

  // Ctrl/Cmd + K for search
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    openSearch();
  }
});
```

---

## Screen Reader Support

### Semantic HTML

```html
<!-- Use semantic elements -->
<header>
  <nav aria-label="Main navigation">
    <ul role="list">
      <li><a href="/">Home</a></li>
      <li><a href="/about" aria-current="page">About</a></li>
    </ul>
  </nav>
</header>

<main>
  <article>
    <h1>Page Title</h1>
    <p>Content...</p>
  </article>
</main>

<aside aria-label="Related content">
  ...
</aside>

<footer>
  <nav aria-label="Footer navigation">
    ...
  </nav>
</footer>
```

### ARIA Labels

```html
<!-- Icon buttons need labels -->
<button aria-label="Close menu">
  <svg aria-hidden="true">...</svg>
</button>

<!-- Describe complex components -->
<div role="region" aria-label="User profile">
  ...
</div>

<!-- Link purpose -->
<a href="/article-123" aria-label="Read more about accessibility">
  Read more
</a>

<!-- Form labels -->
<label for="email">Email</label>
<input id="email" type="email" aria-describedby="email-hint">
<span id="email-hint">We'll never share your email.</span>
```

### Live Regions

```html
<!-- Announce dynamic updates -->
<div aria-live="polite" aria-atomic="true" class="sr-only">
  <!-- JS updates this with status messages -->
</div>

<!-- Urgent announcements -->
<div role="alert">
  Error: Please fill in required fields.
</div>

<!-- Status updates -->
<div role="status">
  Saving...
</div>
```

```javascript
function announce(message) {
  const announcer = document.querySelector('[aria-live]');
  announcer.textContent = message;

  // Clear after announcement
  setTimeout(() => {
    announcer.textContent = '';
  }, 1000);
}

// Usage
announce('Item added to cart');
```

### Hidden Content

```css
/* Visually hidden but accessible to screen readers */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Can be focused (for skip links) */
.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  margin: 0;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

```html
<!-- Hide decorative images -->
<img src="decorative.jpg" alt="" aria-hidden="true">

<!-- Hide icons that have text labels -->
<button>
  <svg aria-hidden="true">...</svg>
  <span>Save</span>
</button>
```

---

## Motion & Animation

### Respecting User Preferences

```css
/* Default: with animations */
.animate-in {
  animation: fade-in 0.3s ease;
}

/* Reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Or provide alternative, simpler animations */
@media (prefers-reduced-motion: reduce) {
  .animate-in {
    animation: none;
    opacity: 1;
  }
}
```

### JavaScript Detection

```javascript
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

if (prefersReducedMotion) {
  // Use simpler animations or disable
  gsap.globalTimeline.timeScale(0);
} else {
  // Full animations
}
```

---

## Form Accessibility

### Complete Form Pattern

```html
<form aria-label="Contact form">
  <!-- Required field with error -->
  <div class="form-group">
    <label for="name">
      Name
      <span aria-hidden="true" class="required">*</span>
    </label>
    <input
      id="name"
      type="text"
      required
      aria-required="true"
      aria-invalid="true"
      aria-describedby="name-error"
    >
    <span id="name-error" class="error" role="alert">
      Name is required
    </span>
  </div>

  <!-- Field with hint -->
  <div class="form-group">
    <label for="password">Password</label>
    <input
      id="password"
      type="password"
      aria-describedby="password-hint"
    >
    <span id="password-hint" class="hint">
      Must be at least 8 characters
    </span>
  </div>

  <!-- Group related fields -->
  <fieldset>
    <legend>Notification preferences</legend>
    <div>
      <input type="checkbox" id="email-notify" name="notify">
      <label for="email-notify">Email notifications</label>
    </div>
    <div>
      <input type="checkbox" id="sms-notify" name="notify">
      <label for="sms-notify">SMS notifications</label>
    </div>
  </fieldset>

  <button type="submit">Submit</button>
</form>
```

```css
/* Error styling */
input[aria-invalid="true"] {
  border-color: var(--color-error);
}

input[aria-invalid="true"]:focus {
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2);
}

.error {
  color: var(--color-error);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.error::before {
  content: "⚠";
}
```

---

## Component Patterns

### Button

```html
<button
  type="button"
  class="button"
  aria-pressed="false"
>
  Toggle
</button>

<!-- Loading state -->
<button
  type="button"
  class="button"
  aria-busy="true"
  aria-live="polite"
>
  <span class="sr-only">Loading</span>
  <svg class="spinner" aria-hidden="true">...</svg>
</button>

<!-- Disabled with explanation -->
<button
  type="button"
  disabled
  aria-describedby="submit-disabled-reason"
>
  Submit
</button>
<span id="submit-disabled-reason" class="sr-only">
  Please fill in all required fields
</span>
```

### Modal Dialog

```html
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
>
  <h2 id="modal-title">Confirm Action</h2>
  <p id="modal-description">
    Are you sure you want to delete this item?
  </p>
  <div class="modal-actions">
    <button type="button">Cancel</button>
    <button type="button" class="danger">Delete</button>
  </div>
</div>

<!-- Backdrop should not be focusable -->
<div class="modal-backdrop" aria-hidden="true"></div>
```

### Tabs

```html
<div class="tabs">
  <div role="tablist" aria-label="Content sections">
    <button
      role="tab"
      id="tab-1"
      aria-selected="true"
      aria-controls="panel-1"
    >
      Tab 1
    </button>
    <button
      role="tab"
      id="tab-2"
      aria-selected="false"
      aria-controls="panel-2"
      tabindex="-1"
    >
      Tab 2
    </button>
  </div>

  <div
    role="tabpanel"
    id="panel-1"
    aria-labelledby="tab-1"
  >
    Panel 1 content
  </div>
  <div
    role="tabpanel"
    id="panel-2"
    aria-labelledby="tab-2"
    hidden
  >
    Panel 2 content
  </div>
</div>
```

---

## Testing Checklist

### Automated Testing
- [ ] axe-core integration in CI
- [ ] Lighthouse accessibility audit
- [ ] ESLint jsx-a11y plugin

### Manual Testing
- [ ] Keyboard-only navigation (Tab, Enter, Escape, arrows)
- [ ] Screen reader testing (VoiceOver, NVDA, JAWS)
- [ ] Zoom to 200% without horizontal scroll
- [ ] High contrast mode
- [ ] Reduced motion preference

### Quick Audit
- [ ] All images have alt text
- [ ] All form inputs have labels
- [ ] Color contrast meets minimums
- [ ] Focus indicators visible
- [ ] Heading hierarchy correct (h1 → h2 → h3)
- [ ] No empty links/buttons
- [ ] Skip link present

---

**Version:** 1.0
**WCAG Reference:** 2.1 AA
