# Responsive Strategy

Layout, density, and component adaptation across viewport tiers.

## 1. Breakpoint Rationale

Define breakpoints by content behavior, not device names.

### Tier Definitions

| Tier | Token | Min Width | Rationale |
|---|---|---|---|
| Compact | `--bp-compact` | 0 | Single column. Touch-primary. Thumb-reachable controls. Content stacks vertically. |
| Medium | `--bp-medium` | 48rem (768px) | Two-column layouts become viable. Mixed input (touch + pointer). Sidebars can appear. |
| Expanded | `--bp-expanded` | 64rem (1024px) | Full multi-column layout. Pointer-primary. Navigation expands inline. Content reaches full width. |
| Wide | `--bp-wide` | 90rem (1440px) | Content max-width reached. Extra space becomes margin. Optional: sidebar + main + aside. |

### CSS Custom Media (future) / Current Implementation

```css
/* Current: standard media queries */
@media (min-width: 48rem)  { /* medium  */ }
@media (min-width: 64rem)  { /* expanded */ }
@media (min-width: 90rem)  { /* wide     */ }

/* Future: custom media (when supported) */
@custom-media --medium  (min-width: 48rem);
@custom-media --expanded (min-width: 64rem);
@custom-media --wide     (min-width: 90rem);
```

### How to Choose a Breakpoint

Do not add a breakpoint because a design "looks wrong" at a random pixel value. Add a breakpoint when:

- Content can no longer fit its container without wrapping or truncation.
- A layout pattern becomes viable that was not viable before (e.g., two columns).
- Input modality shifts enough to warrant different interaction patterns.

Rules:

- Use `rem` or `em` for breakpoints, not `px`. This respects user font-size preferences.
- Prefer mobile-first (`min-width`). Build compact layout first, layer complexity upward.
- Three breakpoints handle most systems. Add a fourth only when content demands it.

## 2. Layout Density Tiers

At each tier, more changes than column count.

### Density Decision Template

```
Tier: [compact / medium / expanded / wide]

Columns: [number]
Margins: [size]
Gutters: [size]

Information hierarchy changes:
  - [what becomes primary / secondary / hidden]

Progressive disclosure:
  - [what is collapsed / expandable / always visible]

Content priority:
  - [what moves above the fold]
  - [what can be deferred below]

Spacing adjustment:
  - [tighter or looser than base]

Typography adjustment:
  - [any size overrides]
```

### Example: Three-Tier Density

| Aspect | Compact | Medium | Expanded |
|---|---|---|---|
| Columns | 1 | 2 | 3-4 |
| Margins | `var(--space-4)` | `var(--space-5)` | `var(--grid-gutter)` clamp |
| Section padding | `var(--space-6)` | `var(--space-7)` | `var(--space-8)` |
| Card layout | Full width, stacked | 2-up grid | 3-up or 4-up grid |
| Navigation | Hamburger / bottom bar | Horizontal, compact | Horizontal, full labels |
| Hero | Stacked, image below text | Stacked, larger type | Side-by-side, two columns |
| Data tables | Card layout per row | Horizontal scroll | Full table |
| Sidebar | Hidden / drawer | Collapsed rail | Full sidebar |

## 3. Type Scale Across Breakpoints

Body type stays stable. Display type scales dramatically.

### Scaling Strategy

| Token | Compact | Medium | Expanded | Method |
|---|---|---|---|---|
| `--text-00` | 0.75rem | 0.75rem | 0.75rem | Fixed |
| `--text-0` | 0.875rem | 0.875rem | 0.875rem | Fixed |
| `--text-1` | 1rem | 1rem | 1rem | Fixed |
| `--text-2` | 1.125rem | 1.125rem | 1.125rem | Fixed |
| `--text-3` | 1.25rem | 1.3rem | 1.375rem | Gentle clamp |
| `--text-4` | 1.5rem | 1.625rem | 1.75rem | Gentle clamp |
| `--text-5` | 2rem | 2.25rem | 2.5rem | Fluid clamp |
| `--text-6` | 3.25rem | ~4.5rem | 5.5rem | Aggressive clamp |

Rules:

- Body sizes (text-00 through text-2) must not change. Reading stability is non-negotiable.
- Display sizes use `clamp()` with viewport-relative preferred values. See Typography Specimens for the calculation formula.
- The ratio between the largest and smallest display size should be at least 1.5x across the full viewport range.
- Lead paragraphs (`--text-2`) may optionally drop to `--text-1` at compact. This is the one body-range exception.

## 4. Touch Target Rules

### Minimum Sizes (WCAG 2.5.8 Level AAA)

| Element | Minimum Size | Minimum Spacing |
|---|---|---|
| Buttons | 44 x 44px | 8px between adjacent targets |
| Links (inline text) | No size minimum, but sufficient padding | 8px vertical between link lines |
| Navigation items | 44 x 44px | No overlap |
| Form inputs | 44px height | 8px between fields |
| Icon buttons | 44 x 44px (including padding) | 8px between adjacent |

### Implementation

```css
/* Ensure touch targets meet minimum size */
.touch-target {
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* For text links in compact viewports */
@media (pointer: coarse) {
  .nav-link {
    padding: 0.75rem 1rem;
  }
}
```

### Thumb Zone Considerations

On compact viewports held one-handed:

- **Easy zone**: bottom center of screen. Place primary actions here.
- **Stretch zone**: top and far edges. Place secondary or infrequent actions here.
- **Avoid zone**: top-left corner (right-handed users). Never place the only way to complete a critical action here.

Rules:

- Use `@media (pointer: coarse)` to detect touch-primary devices when sizing targets.
- Padding counts toward target size. A 14px label with 15px vertical padding meets the 44px requirement.
- Never rely on hover states as the only way to reveal information on touch devices.

## 5. Grid System

### Column Structure

| Tier | Columns | Margins | Gutters |
|---|---|---|---|
| Compact | 4 | `var(--space-4)` (1rem) | `var(--space-4)` (1rem) |
| Medium | 8 | `var(--space-5)` (1.5rem) | `var(--space-4)` (1rem) |
| Expanded | 12 | `var(--grid-gutter)` clamp | `var(--space-4)` (1rem) |
| Wide | 12 | Auto (content max-width centers) | `var(--space-4)` (1rem) |

### CSS Grid Template

```css
.grid-system {
  display: grid;
  gap: var(--space-4);
  padding-inline: var(--space-4);
  grid-template-columns: repeat(4, 1fr);
}

@media (min-width: 48rem) {
  .grid-system {
    padding-inline: var(--space-5);
    grid-template-columns: repeat(8, 1fr);
  }
}

@media (min-width: 64rem) {
  .grid-system {
    padding-inline: var(--grid-gutter);
    grid-template-columns: repeat(12, 1fr);
  }
}

@media (min-width: 90rem) {
  .grid-system {
    max-width: var(--content-wide);
    margin-inline: auto;
  }
}
```

### Component Column Spans

| Component | Compact (of 4) | Medium (of 8) | Expanded (of 12) |
|---|---|---|---|
| Hero text | 4 | 5 | 7 |
| Hero media | 4 | 3 | 5 |
| Card (in grid) | 4 | 4 | 3-4 |
| Sidebar | 4 (drawer) | 2 | 3 |
| Main content | 4 | 6 | 8-9 |
| Full bleed | 4 | 8 | 12 |

### Content Width Containers

```css
/* Constrain content width independent of grid */
.shell {
  width: min(calc(100% - 2 * var(--grid-gutter)), var(--content-wide));
  margin-inline: auto;
}

.shell--narrow {
  width: min(calc(100% - 2 * var(--grid-gutter)), var(--content-narrow));
  margin-inline: auto;
}
```

## 6. Responsive Component Patterns

### Pattern Documentation Template

```
Component: [name]

Compact behavior:
  Layout: [description]
  Visibility: [what is hidden / collapsed / changed]
  Interaction: [touch-specific adaptations]

Medium behavior:
  Layout: [description]
  Visibility: [what becomes visible]
  Interaction: [changes]

Expanded behavior:
  Layout: [description]
  Visibility: [full state]
  Interaction: [pointer-specific features]

Transition points:
  [which breakpoint triggers each change and why]
```

### Navigation

```
Component: Primary navigation

Compact:
  Layout: Hidden behind hamburger icon or bottom tab bar
  Visibility: Brand mark visible, links hidden until triggered
  Interaction: Full-screen overlay or slide-in drawer, 44px touch targets

Medium:
  Layout: Horizontal bar, compact labels
  Visibility: All primary links visible
  Interaction: Hover states active

Expanded:
  Layout: Horizontal bar, full labels with spacing
  Visibility: All links + utility actions visible
  Interaction: Full hover/focus states, keyboard navigation

Transition:
  compact -> medium at 48rem (enough width for all labels without wrapping)
```

### Data Tables

```
Component: Data table

Compact:
  Layout: Each row becomes a stacked card. Column headers become inline labels.
  Visibility: Non-essential columns hidden or collapsed.
  Interaction: Tap card to expand full row details.

Medium:
  Layout: Horizontal table with horizontal scroll if needed.
  Visibility: Primary columns visible, secondary scroll into view.
  Interaction: Scroll indicator visible.

Expanded:
  Layout: Full table, all columns visible.
  Visibility: Everything shown.
  Interaction: Sortable column headers, hover row highlight.

Transition:
  compact -> medium at 48rem (minimum viable table width for 3+ columns)
```

### Hero Section

```
Component: Hero

Compact:
  Layout: Single column. Headline, subtext, CTA stacked. Image below or background.
  Type: --text-6 at clamp minimum (~3.25rem). Lead drops to --text-1.
  Spacing: Reduced vertical padding.

Medium:
  Layout: Still stacked but with more breathing room.
  Type: --text-6 scales up via clamp.
  Spacing: Standard vertical padding.

Expanded:
  Layout: Two-column (1.3fr text, 0.9fr media).
  Type: --text-6 at clamp maximum (~5.5rem).
  Spacing: Full vertical padding.

Transition:
  compact -> expanded at 64rem (two-column hero needs enough width for
  both headline and media to have presence)
```

### Cards

```
Component: Content card

Compact:
  Layout: Full width, vertical stack.
  Content: Image, title, excerpt, action.
  Spacing: Compact internal padding.

Medium:
  Layout: 2-up grid.
  Content: Same elements, possibly truncated excerpt.
  Spacing: Standard padding.

Expanded:
  Layout: 3-up or 4-up grid.
  Content: Full content visible.
  Spacing: Standard padding.

Transition:
  1-col -> 2-col at 48rem
  2-col -> 3/4-col at 64rem
```

## 7. Container Queries

### When to Use What

| Query Type | Use For | Reason |
|---|---|---|
| Media queries | Page-level layout shifts | Viewport width determines overall structure |
| Container queries | Component-level adaptation | Component width determines its own layout |

### The Distinction

Media queries answer: "How wide is the viewport?"
Container queries answer: "How wide is the space this component lives in?"

A card in a 3-column grid and the same card in a full-width slot need different layouts at the same viewport width. Container queries solve this.

### Implementation

```css
/* Define containment on the parent */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* Component adapts to its container, not the viewport */
@container card (min-width: 24rem) {
  .card {
    grid-template-columns: auto 1fr;
    /* horizontal layout when container is wide enough */
  }
}

@container card (min-width: 36rem) {
  .card {
    grid-template-columns: 1fr 2fr;
    /* wider media column when container allows */
  }
}
```

### Container Query Candidates

| Component | Why Container Query | Trigger Width |
|---|---|---|
| Card | Same card used in sidebar (narrow) and main content (wide) | ~24rem for horizontal layout |
| Navigation | Embedded nav in sidebar vs. full header | ~36rem for inline links |
| Data table | Full-width vs. panel-embedded | ~32rem for table vs. card layout |
| Form | Single column vs. multi-column fields | ~28rem for side-by-side fields |
| Media object | Stacked vs. inline image+text | ~20rem for inline layout |

Rules:

- Use media queries for grid structure (how many columns, sidebar visibility).
- Use container queries for component internals (card layout, form field arrangement).
- Always set `container-type: inline-size`, not `container-type: size`, unless you need block-axis queries. Block containment has more layout side effects.
- Name containers with `container-name` when nesting. Unnamed container queries match the nearest ancestor, which can cause unexpected results with deep nesting.
- Container queries have strong browser support (baseline 2023). No polyfill needed for modern targets.
