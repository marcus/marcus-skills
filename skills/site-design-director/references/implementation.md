# Implementation Patterns (Modular CSS)

## CSS Architecture

### File Structure
```
styles/
├── tokens.css          # Design tokens (colors, spacing, type)
├── reset.css           # Minimal reset
├── base.css            # Element defaults (body, headings, links)
├── layout.css          # Grid, containers, spacing utilities
├── components/
│   ├── button.css
│   ├── card.css
│   ├── form.css
│   ├── nav.css
│   └── ...
└── pages/
    ├── home.css
    └── ...
```

### Import Order
```css
/* main.css */
@import 'tokens.css';
@import 'reset.css';
@import 'base.css';
@import 'layout.css';
@import 'components/button.css';
/* ... */
```

---

## Design Tokens

```css
/* tokens.css */
:root {
  /* Colors */
  --color-bg: #ffffff;
  --color-surface: #f9fafb;
  --color-text: #111827;
  --color-text-subtle: #6b7280;
  --color-border: #e5e7eb;
  --color-accent: #2563eb;
  --color-accent-contrast: #ffffff;

  /* Semantic states */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;
  --color-focus-ring: rgba(37, 99, 235, 0.5);

  /* Spacing (8px base) */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-24: 6rem;     /* 96px */

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.5rem;
  --text-2xl: 2rem;
  --text-3xl: 3rem;

  /* Radii */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* Transitions */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --duration-fast: 150ms;
  --duration-normal: 250ms;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f0f0f;
    --color-surface: #1a1a1a;
    --color-text: #f9fafb;
    --color-text-subtle: #9ca3af;
    --color-border: #2d2d2d;
  }
}
```

---

## Layout System

```css
/* layout.css */

/* Container */
.container {
  width: 100%;
  max-width: 1200px;
  margin-inline: auto;
  padding-inline: var(--space-4);
}

@media (min-width: 768px) {
  .container {
    padding-inline: var(--space-8);
  }
}

/* Section spacing */
.section {
  padding-block: var(--space-16);
}

@media (min-width: 768px) {
  .section {
    padding-block: var(--space-24);
  }
}

/* Grid */
.grid {
  display: grid;
  gap: var(--space-6);
}

.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 768px) {
  .grid-2, .grid-3, .grid-4 {
    grid-template-columns: 1fr;
  }
}

/* Asymmetric layouts */
.grid-8-4 {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-8);
}

.grid-sidebar {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: var(--space-8);
}

/* Stack (vertical rhythm) */
.stack > * + * {
  margin-top: var(--space-4);
}

.stack-lg > * + * {
  margin-top: var(--space-8);
}
```

---

## Component Patterns

### Button System
```css
/* components/button.css */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  font-weight: 500;
  line-height: 1.5;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Variants */
.btn-primary {
  background: var(--color-accent);
  color: var(--color-accent-contrast);
}

.btn-primary:hover:not(:disabled) {
  filter: brightness(1.1);
}

.btn-secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border-color: var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-border);
}

.btn-ghost {
  background: transparent;
  color: var(--color-text);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--color-surface);
}

/* Sizes */
.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
}

.btn-lg {
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-base);
}
```

### Form Inputs
```css
/* components/form.css */
.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-base);
  line-height: 1.5;
  color: var(--color-text);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--duration-fast);
}

.input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}

.input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-error {
  border-color: var(--color-danger);
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.3);
}

/* Label */
.label {
  display: block;
  margin-bottom: var(--space-1);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
}

/* Helper/error text */
.input-helper {
  margin-top: var(--space-1);
  font-size: var(--text-xs);
  color: var(--color-text-subtle);
}

.input-error-message {
  margin-top: var(--space-1);
  font-size: var(--text-xs);
  color: var(--color-danger);
}
```

### Card
```css
/* components/card.css */
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.card-body {
  padding: var(--space-6);
}

.card-header {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.card-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border);
  background: var(--color-bg);
}

/* Interactive card */
.card-interactive {
  transition: box-shadow var(--duration-normal) var(--ease-out);
}

.card-interactive:hover {
  box-shadow: var(--shadow-md);
}
```

---

## Animation Patterns

```css
/* Reduced motion respected */
@media (prefers-reduced-motion: no-preference) {
  .fade-in {
    animation: fadeIn var(--duration-normal) var(--ease-out);
  }

  .slide-up {
    animation: slideUp var(--duration-normal) var(--ease-out);
  }

  .stagger > * {
    animation: fadeIn var(--duration-normal) var(--ease-out) backwards;
  }

  .stagger > *:nth-child(1) { animation-delay: 0ms; }
  .stagger > *:nth-child(2) { animation-delay: 50ms; }
  .stagger > *:nth-child(3) { animation-delay: 100ms; }
  .stagger > *:nth-child(4) { animation-delay: 150ms; }
  .stagger > *:nth-child(5) { animation-delay: 200ms; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(1rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## Accessibility Defaults

```css
/* Skip link */
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  padding: var(--space-2) var(--space-4);
  background: var(--color-accent);
  color: var(--color-accent-contrast);
  z-index: 9999;
}

.skip-link:focus {
  top: 0;
}

/* Focus visible (keyboard only) */
:focus:not(:focus-visible) {
  outline: none;
}

:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* Screen reader only */
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
```

---

## Performance Tips

1. **Critical CSS**: Inline above-fold styles in `<head>`
2. **Font loading**: Use `font-display: swap`, preload critical fonts
3. **Animations**: Use `transform` and `opacity` only (GPU-accelerated)
4. **Images**: Use `loading="lazy"`, `srcset`, modern formats (WebP/AVIF)
5. **Container queries**: Use for component-level responsiveness
