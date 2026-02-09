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

## Core Principles

1. **Keyboard-first, mouse-optional** — every click action has a key equivalent
2. **Dark-first** — dark mode is default, light mode is the variant
3. **Speed is a feature** — 100ms interaction target, optimistic updates, no spinners
4. **Color restraint** — near-monochrome, color only for status/accent
5. **High density, low clutter** — pack information in through alignment, not cramming
6. **Be gentle** — everything comfortable, natural, expected, no surprises

## Implementation

For full design system details covering color, typography, layout, navigation, interaction, animation, feedback, and visual polish patterns, see [references/linear-design-system.md](references/linear-design-system.md).

Key sections:
- **A. Color & Theming** — LCH color space, 3-variable themes, dark-first
- **B. Typography** — Inter family, hierarchy through weight/size only
- **C. Layout & Navigation** — inverted-L, list/detail split, collapsible sidebar
- **D. Information Density** — in-place editing, contextual menus
- **E. Interaction & Speed** — optimistic updates, command palette, keyboard shortcuts
- **F. Motion & Animation** — 200ms, purposeful micro-interactions only
- **G. Feedback** — inline over toasts, undo over confirmation
- **H. Visual Polish** — tight alignment, subtle gradients, "be gentle"
- **I. Progressive Disclosure** — works out of the box, natural language filters, universal URLs
