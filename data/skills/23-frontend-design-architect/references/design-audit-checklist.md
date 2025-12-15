# Design Audit Checklist

## Overview

This checklist provides a systematic approach to auditing frontend designs for quality, accessibility, performance, and consistency.

---

## Visual Design Audit

### Color System

- [ ] **Contrast ratios meet WCAG standards**
  - [ ] Normal text: 4.5:1 minimum (AA)
  - [ ] Large text: 3:1 minimum (AA)
  - [ ] UI components: 3:1 minimum
  - [ ] Focus indicators: 3:1 minimum

- [ ] **Color usage is purposeful**
  - [ ] Primary color used for key actions
  - [ ] Semantic colors (success, warning, error) applied correctly
  - [ ] Color not sole indicator of meaning

- [ ] **Color palette is consistent**
  - [ ] Limited to defined palette (no rogue colors)
  - [ ] Proper color tokens used throughout
  - [ ] Dark mode colors defined and tested

### Typography

- [ ] **Type scale is systematic**
  - [ ] Defined font sizes with clear hierarchy
  - [ ] Consistent heading levels (h1 > h2 > h3)
  - [ ] No arbitrary font sizes

- [ ] **Readability optimized**
  - [ ] Body text 16px minimum
  - [ ] Line height 1.4-1.6 for body text
  - [ ] Line length 45-75 characters
  - [ ] Sufficient paragraph spacing

- [ ] **Font loading optimized**
  - [ ] Font display: swap or optional
  - [ ] Preload critical fonts
  - [ ] Fallback fonts specified
  - [ ] Maximum 2-3 font families

### Spacing

- [ ] **Spacing scale is consistent**
  - [ ] Uses defined spacing tokens
  - [ ] No magic numbers (12px, 17px, etc.)
  - [ ] Logical spacing relationships

- [ ] **Whitespace is purposeful**
  - [ ] Adequate breathing room
  - [ ] Content groups visually distinct
  - [ ] Visual hierarchy supported

### Layout

- [ ] **Grid system applied consistently**
  - [ ] Aligned to grid structure
  - [ ] Consistent gutters
  - [ ] Proper container widths

- [ ] **Responsive behavior defined**
  - [ ] All breakpoints tested
  - [ ] No horizontal scroll
  - [ ] Content reflows appropriately

---

## Component Quality Audit

### Consistency

- [ ] **Components match design system**
  - [ ] Buttons follow defined patterns
  - [ ] Form inputs consistent
  - [ ] Cards use standard structure
  - [ ] Icons from approved set

- [ ] **Variants documented**
  - [ ] Size variants (sm, md, lg)
  - [ ] State variants (default, hover, active, disabled)
  - [ ] Theme variants (primary, secondary, ghost)

### States

- [ ] **All interactive states defined**
  - [ ] Default state
  - [ ] Hover state
  - [ ] Focus state (visible focus ring)
  - [ ] Active/pressed state
  - [ ] Disabled state
  - [ ] Loading state (if applicable)
  - [ ] Error state (if applicable)

- [ ] **State transitions smooth**
  - [ ] Appropriate transition timing (150-300ms)
  - [ ] No jarring changes
  - [ ] Consistent easing functions

### Content

- [ ] **Edge cases handled**
  - [ ] Empty states designed
  - [ ] Loading states designed
  - [ ] Error states designed
  - [ ] Long text truncation handled
  - [ ] Extreme content tested

---

## Accessibility Audit

### Keyboard Navigation

- [ ] **All interactive elements keyboard accessible**
  - [ ] Buttons, links, inputs focusable
  - [ ] Tab order logical
  - [ ] No keyboard traps
  - [ ] Skip link present

- [ ] **Focus management correct**
  - [ ] Focus visible on all elements
  - [ ] Focus moves correctly in modals
  - [ ] Focus restored when modals close

### Screen Readers

- [ ] **Semantic HTML used**
  - [ ] Proper heading hierarchy
  - [ ] Landmarks present (nav, main, footer)
  - [ ] Lists use ul/ol/dl
  - [ ] Tables have headers

- [ ] **ARIA used correctly**
  - [ ] ARIA labels for icon buttons
  - [ ] ARIA-live for dynamic content
  - [ ] ARIA-expanded for toggles
  - [ ] ARIA-current for navigation

- [ ] **Images accessible**
  - [ ] Alt text present and meaningful
  - [ ] Decorative images hidden (alt="")
  - [ ] Complex images have descriptions

### Motion

- [ ] **Reduced motion respected**
  - [ ] prefers-reduced-motion query used
  - [ ] Essential animations only
  - [ ] No auto-playing content

### Forms

- [ ] **Form inputs accessible**
  - [ ] Labels associated with inputs
  - [ ] Error messages announced
  - [ ] Required fields indicated
  - [ ] Instructions provided

---

## Performance Audit

### Loading

- [ ] **Critical rendering path optimized**
  - [ ] Critical CSS inlined or preloaded
  - [ ] Above-fold content loads fast
  - [ ] LCP under 2.5 seconds

- [ ] **Assets optimized**
  - [ ] Images compressed and sized
  - [ ] Modern formats (WebP, AVIF)
  - [ ] Lazy loading implemented
  - [ ] Fonts subset

### Runtime

- [ ] **Layout shifts minimized**
  - [ ] CLS under 0.1
  - [ ] Image dimensions specified
  - [ ] Font display optimized
  - [ ] No late-loading content shifts

- [ ] **Interactions responsive**
  - [ ] FID under 100ms
  - [ ] INP under 200ms
  - [ ] No janky animations

### CSS Performance

- [ ] **CSS optimized**
  - [ ] No unused CSS in critical path
  - [ ] Selectors reasonably specific
  - [ ] Animations use transform/opacity
  - [ ] will-change used sparingly

---

## Code Quality Audit

### CSS Architecture

- [ ] **Methodology followed**
  - [ ] Consistent naming convention (BEM, etc.)
  - [ ] Logical file organization
  - [ ] Appropriate specificity levels
  - [ ] No !important abuse

- [ ] **Modern features used appropriately**
  - [ ] CSS variables for tokens
  - [ ] Container queries where beneficial
  - [ ] Logical properties for i18n
  - [ ] Feature queries for fallbacks

### Maintainability

- [ ] **Code documented**
  - [ ] Component documentation
  - [ ] Design decisions recorded
  - [ ] Token usage explained

- [ ] **Patterns consistent**
  - [ ] Similar problems solved similarly
  - [ ] Reusable components extracted
  - [ ] No copy-paste duplication

---

## Cross-Browser Audit

### Browser Support

- [ ] **Target browsers tested**
  - [ ] Chrome (latest 2 versions)
  - [ ] Firefox (latest 2 versions)
  - [ ] Safari (latest 2 versions)
  - [ ] Edge (latest 2 versions)

- [ ] **Mobile browsers tested**
  - [ ] iOS Safari
  - [ ] Chrome for Android
  - [ ] Samsung Internet

### Progressive Enhancement

- [ ] **Fallbacks provided**
  - [ ] @supports for new features
  - [ ] Fallback fonts specified
  - [ ] Core functionality works without JS

---

## Token Audit

### Design Token Coverage

- [ ] **Colors tokenized**
  - [ ] No hex codes in components
  - [ ] All colors reference tokens
  - [ ] Semantic names used

- [ ] **Spacing tokenized**
  - [ ] No magic numbers
  - [ ] Consistent spacing scale
  - [ ] Tokens used for margins/padding

- [ ] **Typography tokenized**
  - [ ] Font sizes from scale
  - [ ] Line heights defined
  - [ ] Font weights consistent

- [ ] **Other values tokenized**
  - [ ] Border radii
  - [ ] Shadows
  - [ ] Z-indices
  - [ ] Transitions

### Token Organization

- [ ] **Token tiers appropriate**
  - [ ] Primitives for raw values
  - [ ] Semantics for meaning
  - [ ] Components for specifics

---

## Dark Mode Audit

### Implementation

- [ ] **All tokens have dark variants**
  - [ ] Background colors
  - [ ] Text colors
  - [ ] Border colors
  - [ ] Shadow adjustments

- [ ] **System preference respected**
  - [ ] prefers-color-scheme works
  - [ ] User toggle overrides system
  - [ ] Preference persisted

### Visual Quality

- [ ] **Dark mode visually correct**
  - [ ] Sufficient contrast
  - [ ] No pure white/black
  - [ ] Images appropriate for dark bg
  - [ ] Focus indicators visible

---

## Animation Audit

### Performance

- [ ] **Animations performant**
  - [ ] Only transform/opacity animated
  - [ ] 60fps maintained
  - [ ] will-change used correctly

### Purpose

- [ ] **Animations meaningful**
  - [ ] Guide user attention
  - [ ] Provide feedback
  - [ ] Show relationships
  - [ ] No decorative-only animations

### Timing

- [ ] **Timing appropriate**
  - [ ] Micro-interactions: 100-200ms
  - [ ] State changes: 200-300ms
  - [ ] Enter animations: 300-400ms
  - [ ] Exit animations: 200-300ms

---

## Responsive Audit

### Breakpoints

- [ ] **All breakpoints tested**
  - [ ] 320px (small mobile)
  - [ ] 375px (iPhone)
  - [ ] 768px (tablet)
  - [ ] 1024px (small desktop)
  - [ ] 1280px (desktop)
  - [ ] 1920px (wide)

### Touch Targets

- [ ] **Touch targets adequate**
  - [ ] Minimum 44x44px
  - [ ] Adequate spacing between targets
  - [ ] Touch feedback provided

### Content

- [ ] **Content adapts appropriately**
  - [ ] Images scale/crop correctly
  - [ ] Text remains readable
  - [ ] Tables become scrollable/cards
  - [ ] Forms remain usable

---

## Quick Audit Scoring

### Scoring Guide

| Category | Weight | Score (1-5) |
|----------|--------|-------------|
| Visual Consistency | 15% | ___ |
| Component Quality | 15% | ___ |
| Accessibility | 25% | ___ |
| Performance | 15% | ___ |
| Code Quality | 10% | ___ |
| Browser Support | 10% | ___ |
| Responsiveness | 10% | ___ |

### Rating Scale

- **5**: Excellent - No issues
- **4**: Good - Minor issues
- **3**: Acceptable - Some issues
- **2**: Poor - Significant issues
- **1**: Critical - Fundamental problems

### Overall Score Interpretation

- **4.5-5.0**: Production ready
- **4.0-4.4**: Minor polish needed
- **3.5-3.9**: Moderate improvements needed
- **3.0-3.4**: Significant work required
- **Below 3.0**: Major rework needed

---

## Audit Report Template

```markdown
# Design Audit Report

**Project:** [Project Name]
**Date:** [Date]
**Auditor:** [Name]

## Executive Summary
[Brief overview of findings]

## Scores

| Category | Score | Notes |
|----------|-------|-------|
| Visual Consistency | X/5 | |
| Component Quality | X/5 | |
| Accessibility | X/5 | |
| Performance | X/5 | |
| Code Quality | X/5 | |
| Browser Support | X/5 | |
| Responsiveness | X/5 | |
| **Overall** | **X/5** | |

## Critical Issues
1. [Issue 1]
2. [Issue 2]

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

## Next Steps
- [ ] [Action item 1]
- [ ] [Action item 2]
```

---

**Version:** 1.0
**Last Updated:** 2025
