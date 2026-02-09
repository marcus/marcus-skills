# Linear Design System — Complete Reference

Comprehensive breakdown of Linear's design characteristics, sourced from Linear's own blog posts, design community analysis, and direct product observation.

## A. Color & Theming

### Dark-First Design
Dark mode is the default, not an afterthought. Dark gray/black backgrounds with high-contrast text. The aesthetic originates from the black coding environments engineers prefer — minimizes battery drain and eye strain.

### Extreme Color Restraint
Near-monochrome palette. Color is used sparingly and intentionally — status indicators, accents, nothing else. No decorative color. Linear's 2025 site replaced monochrome blue with monochrome black/white and even fewer bold colors. Brand color used at 1–10% lightness to create harmony without noise.

### LCH Color Space
Perceptually uniform color generation replaces HSL. A red and a yellow at the same lightness actually look equally light. Superior for generating accessible themes.

### 3-Variable Theme System
Entire themes generated from just three variables:
- **Base color** — background/surface tones
- **Accent color** — primary action/brand color
- **Contrast** — controls text/border intensity, enables automatic high-contrast accessibility themes

Replaced a system requiring 98 variables per theme.

### High-Contrast Accessibility
The contrast variable automatically produces WCAG-compliant high-contrast themes without manual tuning.

## B. Typography

### Inter Family
- **Inter Display** for headings — adds expression while maintaining readability
- **Inter** (regular) for body text — highly legible at small sizes, familiar to engineers
- **Monospace** for code, IDs, technical values — clear signal of "this is data"

### Typographic Hierarchy Over Decoration
Hierarchy communicated through weight and size, not color or ornamentation.

## C. Layout & Navigation

### Inverted-L Navigation
Fixed sidebar + horizontal header forming an L-shape. Content fills the remaining space. Core structural pattern.

### List/Detail Split View
Master list on left, detail panel on right. Primary pattern for entity browsing.

### Multiple View Modes
Same data viewable as list, board (kanban), split, and timeline. User chooses density/format.

### Collapsible Sidebar
Sidebar shows saved/custom views and pinned items. Collapsible to maximize content area.

### Minimal Chrome
Reduced visual noise in sidebars, tabs, headers, panels. UI elements recede, content comes forward.

## D. Information Density

### High Density, Low Clutter
Lots of information on screen achieved through alignment and restraint, not cramming. Every pixel earns its place.

### In-Place Editing and Filtering
Filters modify in-place with small indicators. No separate dialog boxes for common operations. Everything easily modified without launching new windows.

### Contextual Menus on Everything
Right-click any entity for a full action menu. Reduces navigation steps.

## E. Interaction & Speed

### 100ms Target
All interactions feel instantaneous. Based on Gmail creator Paul Buchheit's standard — UI responds before the server confirms.

### Optimistic Updates
Changes apply to the UI immediately. If server rejects, UI rolls back with a quiet toast. No spinners for common actions.

### Keyboard-First, Mouse-Optional
Full app control via keyboard. Optional keyboard-only mode that disables mouse for training. Every action reachable by click is reachable by key.

### Command Palette (Cmd+K)
Fuzzy-searchable entry point to every action, page, and entity. Shows shortcuts next to each option so users learn keys organically. Context-aware — available actions change based on current page. Recent actions surface first. Non-intrusive — doesn't clutter the interface when unused.

### Go-To Navigation
Two-key sequences: `g` then letter (e.g., `g i` for inbox). Vim-inspired, memorable.

### Shortcut Hints on Hover
After hovering an element for a few seconds, a banner appears showing the keyboard shortcut. Gentle, non-intrusive training.

### Real-Time Sync
Changes from other users appear instantly without refresh. Collaborative without feeling noisy.

## F. Motion & Animation

### "Flows Like Water" Transitions
Animations are soft, timely, and fluid. Nothing snaps or jumps.

### Micro-Interactions with Purpose
Small animations on state changes (starring, completing, dragging) give tactile feedback. ~200ms, never blocking.

### No Decorative Animation
Motion communicates state changes, never draws attention to itself. The tool feels responsive, not animated.

## G. Feedback & Communication

### Inline Feedback Over Toasts
"Saving..." appears next to the field being edited, not in a corner toast. Zero eye travel.

### Quiet Error Recovery
Failed optimistic updates roll back with a minimal, non-alarming notification.

### Undo Over Confirmation
Prefer letting users undo destructive actions rather than blocking with "Are you sure?" dialogs. Confirmation only for truly irreversible operations.

## H. Visual Polish

### Subtle Gradients and Blur
Faux depth via gradients and glassmorphism on select surfaces. Adds dimension without clutter. Complex gradients add perceived detail without actual visual noise.

### Tight Alignment
Obsessive vertical and horizontal alignment of labels, icons, and buttons across all views.

### "Be Gentle" Philosophy
Everything feels comfortable, natural, expected. No surprises, no friction. The UI respects the user's time and attention. As Linear describes it: "A user needs to see and understand what is presented...everything feels comfortable, natural, and expected."

## I. Progressive Disclosure & Onboarding

### Works Out of the Box
Minimal onboarding required. Sensible defaults, customization available but not required.

### Natural Language Filters
Create filters with conversational input (e.g., "Completed in October"). Lower barrier than structured query builders.

### Universal URLs
Every entity, view, and state has a shareable URL. Deep-linkable everything.

## Sources

- [How we redesigned the Linear UI (part II)](https://linear.app/now/how-we-redesigned-the-linear-ui)
- [Linear's Delightful Design Patterns](https://gunpowderlabs.com/2024/12/22/linear-delightful-patterns)
- [The Elegant Design of Linear.app](https://telablog.com/the-elegant-design-of-linear-app/)
- [Linear design: The SaaS design trend — LogRocket](https://blog.logrocket.com/ux-design/linear-design/)
- [The rise of Linear style design — Medium](https://medium.com/design-bootcamp/the-rise-of-linear-style-design-origins-trends-and-techniques-4fd96aab7646)
- [Linear — Radix Primitives Case Study](https://www.radix-ui.com/primitives/case-studies/linear)
