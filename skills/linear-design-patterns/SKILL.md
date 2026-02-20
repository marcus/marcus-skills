---
name: linear-design-patterns
description: Linear-inspired design system patterns for building keyboard-first, high-density, dark-first web applications. Use when (1) building a new design system or design tokens inspired by Linear's aesthetic, (2) implementing keyboard-first navigation with command palettes and vim-style shortcuts, (3) designing admin tools, developer tools, or SaaS UIs that prioritize speed and information density, (4) choosing color systems, typography, animation, or feedback patterns for professional/engineering-focused apps, (5) user mentions Linear, Linear-style, or asks for a clean/minimal/keyboard-first design approach.
---

# Linear Design Patterns

Apply Linear's design philosophy to web applications. Covers color, typography, layout, keyboard interaction, animation, feedback, and visual polish.

## Quick Decision Guide

| Decision | Linear's Answer |
|----------|----------------|
| Light or dark default? | Dark-first |
| Color space? | LCH (perceptually uniform) |
| How many theme variables? | 3: base, accent, contrast |
| Font? | Inter + Inter Display for headings |
| Spacing base unit? | 4px |
| Animation duration? | ~200ms, ease-out |
| Confirm or undo? | Undo (except irreversible) |
| Loading spinners? | No — optimistic updates |
| Feedback location? | Inline, next to the action |
| Keyboard support? | Full app control, mouse optional |
| Command palette? | Yes, Cmd+K, fuzzy search, context-aware |
| Navigation shortcuts? | `g` then letter (vim-style) |
| Information density? | High density, low clutter |
| Chrome/decoration? | Minimal — content over chrome |
| Content surface shape? | Sharp edges — no border-radius on data panels |
| Panel separation? | 1px border lines, not gaps or shadows |
| When to elevate? | Only floating overlays (modals, dropdowns, popovers) |

## Core Principles

1. **Keyboard-first, mouse-optional** — every click action has a key equivalent
2. **Dark-first** — dark mode is default, light mode is the variant
3. **Speed is a feature** — 100ms interaction target, optimistic updates, no spinners
4. **Color restraint** — near-monochrome, color only for status/accent
5. **High density, low clutter** — pack information in through alignment, not cramming
6. **Be gentle** — everything comfortable, natural, expected, no surprises

## ⚠️ Common Agent Mistakes — READ THIS FIRST

Agents consistently fail at this design system in the same ways. If you catch yourself doing any of these, stop and fix it immediately.

### Mistake #1: Containers within containers
The most common failure. Agents instinctively wrap content in `.card > .card-body > .card-content` or `.panel > .panel-inner`. **Never do this.** The layout is a flat grid. Visual grouping comes from background colors, borders, and spacing — not from nesting.

**WRONG:**
```html
<div class="stats-row">
  <div class="stat-card">
    <div class="stat-body">
      <h3>Total Requests</h3>
      <p>537,784</p>
    </div>
  </div>
</div>
```

**RIGHT:**
```html
<div class="metric-grid">
  <div class="metric-cell">
    <span class="metric-label">Total Requests</span>
    <span class="metric-value">537,784</span>
  </div>
</div>
```

### Mistake #2: box-shadow on data surfaces
Shadows are ONLY for floating overlays (modals, dropdowns, popovers). Never on tables, cards, panels, grids, or any data surface. Use 1px border lines instead.

### Mistake #3: border-radius on data surfaces
Data grids, table rows, list items, content sections — all get `border-radius: 0`. Rounded corners are ONLY for interactive elements (buttons, pills, badges, inputs) and floating overlays.

### Mistake #4: max-width containers that don't fill the viewport
Content should span the full width of its area. No `max-width: 800px; margin: 0 auto` on page content. The grid fills the space.

### Mistake #5: Using traditional table markup for non-tabular data
Comments, blog posts, activity feeds — these are conversational/content, not spreadsheet data. Render them as styled row lists, not `<table>` elements. Use tables only when the data is genuinely columnar.

### Mistake #6: Bland pages with no color differentiation
Color restraint doesn't mean no color. Use the status color system actively:
- **Badges with colored dots** for status (green=success, amber=warning, red=error)
- **Subtle background tints** for status rows (e.g., `rgba(229, 166, 62, 0.05)` for pending items)
- **Accent color** for active states, links, primary actions
- **Typography hierarchy** (size, weight, opacity) creates visual interest without decoration

## Concrete Patterns

### Metric Grid
```css
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-bottom: 1px solid var(--color-border-strong);
}
.metric-cell {
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  border-right: 1px solid var(--color-border-strong);
}
.metric-cell:last-child { border-right: none; }
```

### Status Badge with Dot
```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: 1px var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}
.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
}
.badge-success { background: var(--color-success-bg-subtle); color: var(--color-success); }
.badge-warning { background: var(--color-warning-bg-subtle); color: var(--color-warning); }
.badge-error { background: var(--color-error-bg-subtle); color: var(--color-error); }
```

### Button System
```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: var(--radius-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--duration-fast);
  white-space: nowrap;
}
.btn-primary { background: var(--color-accent-default); color: var(--color-on-accent); }
.btn-secondary { background: var(--color-bg-tertiary); color: var(--color-text-primary); border: 1px solid var(--color-border-default); }
.btn-ghost { color: var(--color-text-secondary); }
.btn-ghost:hover { background: var(--color-bg-tertiary); color: var(--color-text-primary); }
```

### Slide-in Detail Panel
```css
.detail-panel {
  position: fixed;
  top: 0; right: 0; bottom: 0;
  width: 480px;
  background: var(--color-bg-secondary);
  border-left: 1px solid var(--color-border-strong);
  z-index: 51;
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 300ms cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: var(--shadow-lg); /* OK — this is a floating overlay */
}
.detail-panel.open { transform: translateX(0); }
```

### Content Row (for lists, feeds, comments)
```css
.content-row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-3);
  border-bottom: 1px solid var(--color-border-default);
  cursor: pointer;
  transition: background var(--duration-fast);
}
.content-row:hover { background: var(--color-bg-tertiary); }
```

### Sidebar Navigation
```css
.sidebar {
  background: var(--color-bg-inset);
  border-right: 1px solid var(--color-border-strong);
  display: flex;
  flex-direction: column;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md); /* OK — interactive element */
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}
.nav-item.active {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}
.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0; top: 50%;
  transform: translateY(-50%);
  width: 3px; height: 16px;
  background: var(--color-accent-default);
  border-radius: var(--radius-full);
}
```

## Implementation

For full design system details covering color, typography, layout, navigation, interaction, animation, feedback, and visual polish patterns, see [references/linear-design-system.md](references/linear-design-system.md).

Key sections:
- **A. Color & Theming** — LCH color space, 3-variable themes, dark-first
- **B. Typography** — Inter family, hierarchy through weight/size only
- **C. Layout & Navigation** — inverted-L, list/detail split, collapsible sidebar
- **D. Surface Architecture** — flush tiled grids, sharp edges on data, border hierarchy, elevation only for overlays
- **E. Information Density** — in-place editing, contextual menus
- **F. Interaction & Speed** — optimistic updates, command palette, keyboard shortcuts
- **G. Motion & Animation** — 200ms, purposeful micro-interactions only
- **H. Feedback** — inline over toasts, undo over confirmation
- **I. Visual Polish** — tight alignment, subtle gradients, "be gentle"
- **J. Progressive Disclosure** — works out of the box, natural language filters, universal URLs
