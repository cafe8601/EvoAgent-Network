# Animation Performance Guide

## Overview

This guide covers techniques for creating smooth, performant animations that maintain 60fps and respect user preferences.

---

## Performance Fundamentals

### The Rendering Pipeline

```
JavaScript → Style → Layout → Paint → Composite
```

**Goal:** Trigger only the cheapest steps possible.

| Step | Cost | Triggers |
|------|------|----------|
| **Composite** | Cheapest | `transform`, `opacity` |
| **Paint** | Medium | `color`, `background`, `box-shadow` |
| **Layout** | Expensive | `width`, `height`, `margin`, `padding` |

### GPU-Accelerated Properties

```css
/* ✅ CHEAP - Compositor only */
.element {
  transform: translateX(100px);
  transform: scale(1.1);
  transform: rotate(45deg);
  opacity: 0.5;
}

/* ❌ EXPENSIVE - Triggers layout */
.element {
  left: 100px;
  top: 50px;
  width: 200px;
  margin-left: 20px;
}

/* ❌ MEDIUM - Triggers paint */
.element {
  background-color: red;
  box-shadow: 0 0 10px black;
  border-radius: 50%;
}
```

### Will-Change Hint

```css
/* Prepare browser for animation */
.will-animate {
  will-change: transform, opacity;
}

/* Remove after animation */
.done-animating {
  will-change: auto;
}
```

**Caution:** Use sparingly! Too many `will-change` declarations consume memory.

```javascript
// Add before animation
element.style.willChange = 'transform';

// Remove after animation
element.addEventListener('animationend', () => {
  element.style.willChange = 'auto';
});
```

---

## CSS Animation Patterns

### Transitions

```css
/* Basic transition */
.button {
  background: blue;
  transition: background-color 200ms ease;
}

.button:hover {
  background: darkblue;
}

/* Multiple properties */
.card {
  transition:
    transform 300ms cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.15);
}
```

### Keyframe Animations

```css
/* Fade in */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: fadeIn 0.4s ease-out forwards;
}

/* Staggered children */
.stagger > * {
  animation: fadeIn 0.4s ease-out forwards;
  opacity: 0;
}

.stagger > *:nth-child(1) { animation-delay: 0ms; }
.stagger > *:nth-child(2) { animation-delay: 100ms; }
.stagger > *:nth-child(3) { animation-delay: 200ms; }
.stagger > *:nth-child(4) { animation-delay: 300ms; }
```

### Loading Spinner

```css
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(0,0,0,0.1);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Reduced motion alternative */
@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation-duration: 1.5s;
  }
}
```

### Skeleton Loading

```css
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 0%,
    #e0e0e0 50%,
    #f0f0f0 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
```

---

## JavaScript Animation

### RequestAnimationFrame

```javascript
// ✅ Smooth - synced with display refresh
function animate() {
  element.style.transform = `translateX(${x}px)`;
  x += 2;

  if (x < 300) {
    requestAnimationFrame(animate);
  }
}

requestAnimationFrame(animate);

// ❌ Janky - not synced with display
setInterval(() => {
  element.style.transform = `translateX(${x}px)`;
  x += 2;
}, 16);
```

### Web Animations API

```javascript
// Native browser animations
element.animate([
  { transform: 'translateX(0)', opacity: 1 },
  { transform: 'translateX(100px)', opacity: 0 }
], {
  duration: 300,
  easing: 'ease-out',
  fill: 'forwards'
});

// With promises
const animation = element.animate(keyframes, options);
await animation.finished;
// Animation complete
```

### anime.js v4 (Recommended Library)

```javascript
import { animate, createTimeline, stagger, engine } from 'animejs';

// Set time unit once
engine.timeUnit = 's';

// Basic animation
animate('.element', {
  translateX: 100,
  opacity: 0.5,
  duration: 0.3,
  ease: 'outQuad'
});

// Timeline
const tl = createTimeline({
  defaults: {
    duration: 0.4,
    ease: 'outQuad'
  }
});

tl.add('.hero-title', {
    y: [50, 0],
    opacity: [0, 1]
  })
  .add('.hero-subtitle', {
    y: [30, 0],
    opacity: [0, 1]
  }, '-=0.2')
  .add('.hero-cta', {
    scale: [0.9, 1],
    opacity: [0, 1]
  }, '-=0.2');

// Stagger
animate('.card', {
  y: [30, 0],
  opacity: [0, 1],
  delay: stagger(0.1)
});
```

### Framer Motion (React)

```jsx
import { motion, AnimatePresence } from 'framer-motion';

// Basic animation
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  Content
</motion.div>

// Exit animations
<AnimatePresence>
  {isVisible && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      Content
    </motion.div>
  )}
</AnimatePresence>

// Gestures
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  Click me
</motion.button>
```

---

## Scroll Animations

### CSS scroll-driven (Modern)

```css
@keyframes reveal {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.scroll-reveal {
  animation: reveal linear;
  animation-timeline: view();
  animation-range: entry 0% cover 40%;
}
```

### Intersection Observer (Fallback)

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.2,
  rootMargin: '0px 0px -50px 0px'
});

document.querySelectorAll('.animate-on-scroll').forEach(el => {
  observer.observe(el);
});
```

```css
.animate-on-scroll {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.5s, transform 0.5s;
}

.animate-on-scroll.visible {
  opacity: 1;
  transform: translateY(0);
}
```

---

## Reduced Motion

### CSS Implementation

```css
/* Default animations */
.element {
  transition: transform 0.3s, opacity 0.3s;
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

/* Disable for reduced motion preference */
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

/* Or provide alternative */
@media (prefers-reduced-motion: reduce) {
  .element {
    transition: opacity 0.1s; /* Faster, simpler */
  }
}
```

### JavaScript Detection

```javascript
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

// Adjust animation library
if (prefersReducedMotion) {
  // Disable or simplify animations
  engine.timeUnit = 'ms';
  engine.defaults.duration = 0;
} else {
  // Full animations
  engine.timeUnit = 's';
}

// Listen for changes
window.matchMedia('(prefers-reduced-motion: reduce)')
  .addEventListener('change', (e) => {
    // User changed preference
    updateAnimationSettings(e.matches);
  });
```

---

## Easing Functions

### Common Easing

```css
/* Built-in */
transition-timing-function: ease;
transition-timing-function: ease-in;
transition-timing-function: ease-out;
transition-timing-function: ease-in-out;
transition-timing-function: linear;

/* Custom cubic-bezier */
/* Standard */
--ease-standard: cubic-bezier(0.4, 0, 0.2, 1);

/* Deceleration */
--ease-out: cubic-bezier(0, 0, 0.2, 1);

/* Acceleration */
--ease-in: cubic-bezier(0.4, 0, 1, 1);

/* Bounce */
--ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);

/* Elastic */
--ease-elastic: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Easing by Use Case

| Use Case | Easing | CSS |
|----------|--------|-----|
| UI feedback | ease-out | `cubic-bezier(0, 0, 0.2, 1)` |
| Entering | ease-out | `cubic-bezier(0, 0, 0.2, 1)` |
| Exiting | ease-in | `cubic-bezier(0.4, 0, 1, 1)` |
| State change | ease-in-out | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Playful | bounce | `cubic-bezier(0.34, 1.56, 0.64, 1)` |

---

## Performance Debugging

### Chrome DevTools

1. **Performance Tab**
   - Record during animation
   - Look for long tasks (>50ms)
   - Check for layout thrashing

2. **Rendering Panel**
   - Paint flashing: See what's repainting
   - Layer borders: See composited layers
   - FPS meter: Monitor frame rate

3. **Layers Panel**
   - Inspect composited layers
   - Check memory usage

### Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Janky scroll | Layout animation | Use transform |
| Memory spike | Too many layers | Limit will-change |
| Flash on start | Initial render | Use opacity fade |
| Stuck animation | State not reset | Use animation events |

### Checklist

- [ ] Only animating `transform` and `opacity`
- [ ] Using `will-change` sparingly
- [ ] Respecting `prefers-reduced-motion`
- [ ] 60fps in Chrome DevTools
- [ ] No layout thrashing
- [ ] Reasonable memory usage

---

## Animation Timing Guide

| Element Type | Duration | Easing |
|--------------|----------|--------|
| Micro-interaction (button) | 100-200ms | ease-out |
| State change (toggle) | 200-300ms | ease-in-out |
| Enter animation | 300-400ms | ease-out |
| Exit animation | 200-300ms | ease-in |
| Complex sequence | 600-1000ms | custom |
| Loading spinner | infinite | linear |

### Golden Rules

1. **Faster is usually better** - Users don't notice 150ms
2. **Enter slow, exit fast** - Objects arrive gracefully, leave quickly
3. **Consistent timing** - Same animations = same duration
4. **Purpose over decoration** - Every animation should have a reason

---

**Version:** 1.0
**Last Updated:** 2025
