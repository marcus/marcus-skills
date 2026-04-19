# DESIGN.md Section Specification

Detailed spec for each section of a DESIGN.md file. Use this when creating or auditing a design system document.

---

## Section: Colors

**Required fields per color token:**
- Token name (kebab-case, descriptive)
- Exact value (hex `#RRGGBB`, `#RRGGBBAA`, or `rgba(r,g,b,a)` — never approximate)
- Usage note (what it's for, not just what it looks like)

**Groupings to include:**

### Brand Colors
Primary and secondary brand palette. These are fixed — they don't shift with theme changes.
- `brand-primary` — main brand color (CTAs, links)
- `brand-secondary` — accent color
- `brand-tertiary` — optional third tone

### Semantic / Role-Based Colors
These are what agents should actually use for UI elements. Semantic names decouple from palette.

Background layer:
- `bg-base` — page background (lowest layer)
- `bg-surface` — cards, panels (one layer up)
- `bg-elevated` — modals, dropdowns, tooltips (highest)
- `bg-overlay` — scrim/overlay behind modals (typically `rgba(0,0,0,0.5)`)

Text:
- `text-primary` — main readable text
- `text-secondary` — supporting/muted text
- `text-disabled` — non-interactive text
- `text-inverse` — text on dark backgrounds (in light-mode systems)
- `text-link` — hyperlinks

Borders:
- `border-default` — standard border
- `border-strong` — hover/focus borders
- `border-subtle` — very faint dividers

### Status Colors
- `success` / `success-bg` / `success-text` — for success states
- `warning` / `warning-bg` / `warning-text`
- `error` / `error-bg` / `error-text`
- `info` / `info-bg` / `info-text`

Note: include both the vivid color AND muted background/text variants if your UI uses both (e.g., alert banners and inline status badges).

### Dark/Light Mode
If the project supports both modes, document each mode's values separately, keyed by the same semantic token names. Use CSS custom property syntax to show how they map:

```css
/* Light mode */
--bg-base: #FFFFFF;
--text-primary: #111111;

/* Dark mode */
--bg-base: #0F0F0F;
--text-primary: #F5F5F5;
```

---

## Section: Typography

**Required per font style:**
- Font family (full stack, e.g., `'Inter', system-ui, sans-serif`)
- Size (px preferred over rem for clarity in spec)
- Line height (px)
- Font weight (numeric, e.g., 400/500/600/700)
- Usage context (when to use this style)

**What to document:**

1. **Font families** — list all families in use, their role (body, heading, mono, display), and full CSS stack
2. **Type scale** — every size in the system. Don't skip sizes.
3. **Heading styles** — h1–h6 or named variants (display, title, heading, subheading)
4. **Body styles** — base body, small, caption, label
5. **Mono/code style** — family, size, weight (if used)
6. **Letter spacing** — if non-default tracking is used anywhere, document it

**What NOT to include:** Don't just say "use Inter" — specify the weight for each use case. Agents will guess otherwise.

---

## Section: Spacing

**Required:**
- Base unit (typically 4px)
- Full scale with token names AND pixel values
- Notes on when to deviate (answer: almost never)

**Best practice:** Express the full scale from 1× to at least 16× the base unit. Name tokens with numbers (space-1, space-2) OR T-shirt sizes (xs, sm, md, lg) — pick one and be consistent.

Example scale (4px base):
```
space-px  = 1px   (hairline)
space-0.5 = 2px   (tight)
space-1   = 4px
space-2   = 8px
space-3   = 12px
space-4   = 16px
space-5   = 20px
space-6   = 24px
space-8   = 32px
space-10  = 40px
space-12  = 48px
space-16  = 64px
space-20  = 80px
space-24  = 96px
```

Also document:
- Component padding conventions (e.g., "all components use space-3 or space-4 for inner padding")
- Layout-level spacing (section gaps, page padding)

---

## Section: Layout

**Required:**
- All breakpoints with pixel values
- Grid system (columns, gutter, margin)
- Container/max-width values
- Side padding (mobile vs desktop)

**Optional but recommended:**
- Z-index scale (and what each layer is for)
- Common layout patterns (sidebar widths, panel widths)
- Aspect ratios in use

---

## Section: Components

This is the most important section for agents. Every component that exists in the project should be documented here.

**Per component, document:**

1. **Variants** (primary/secondary/ghost/destructive, etc.)
2. **Sizes** (sm/md/lg with exact padding/font-size)
3. **States** (default, hover, focus, active, disabled, loading)
4. **Exact values** for each state (don't just say "slightly darker" — give the actual value or transform)
5. **Accessibility notes** (focus ring spec, aria attributes)

**Components to document at minimum:**
- Button (all variants and sizes)
- Input / Textarea / Select
- Checkbox / Radio / Toggle
- Card / Panel
- Badge / Tag / Chip
- Alert / Banner
- Modal / Dialog
- Dropdown / Menu
- Table (header style, row style, hover)
- Tabs
- Tooltip
- Avatar
- Spinner / Loader

**Format for each component:**
```markdown
### ComponentName
Brief description of when to use this component.

**Variants:** primary, secondary, outline, ghost
**Sizes:** sm, md (default), lg

**Structure:**
- Container: bg `token`, border `token`, radius `radius-md`, padding `space-3 space-4`
- Label: font-size `text-sm`, weight 500, color `text-primary`

**States:**
- Default: (as above)
- Hover: border-color `border-strong`, bg `bg-elevated`
- Focus: ring `3px solid brand-primary/20`
- Disabled: opacity 0.5, pointer-events none
```

---

## Section: Borders & Radius

**Required:**
- All border-radius values with token names
- Border widths used
- Default border colors (reference color tokens)

Document these as tokens, not inline values. Agents should use `radius-md` not `border-radius: 6px`.

---

## Section: Shadows

**Required:**
- All shadow values verbatim (copy from CSS exactly)
- Token name for each
- Usage context (when to use each shadow level)

Shadows are easy to get wrong — exact values matter a lot visually. Copy from the source of truth (CSS variables, Tailwind config, design tokens JSON).

---

## Section: Motion

**Required:**
- Duration tokens (fast/base/slow)
- Easing functions (exact cubic-bezier values)
- Standard transition shorthand
- `prefers-reduced-motion` policy

**Optional:**
- Spring animation parameters
- Specific animation names/keyframes in use

---

## Section: Icons

**Required:**
- Icon library name and version
- Import/usage pattern
- Size scale
- Stroke width (if SVG icons)
- Color convention (inherit? fixed? semantic?)

**Optional:**
- List of custom icons not in the library
- Usage rules (when to use icons alone vs. with labels)

---

## Section: Principles

Short prose (3–7 bullets) describing the intent of the design system. Not rules — feelings and goals.

Examples:
- "Compact but not cramped — density at the service of clarity"
- "Dark by default, consistent elevation hierarchy"
- "Motion confirms, never entertains"

These help agents make judgment calls when the spec doesn't cover an edge case.

---

## Section: Anti-Patterns

Explicit list of things to never do. This is often the most valuable section for agents.

Format as: ❌ Never [do X] — [why or what to do instead]

Examples:
- ❌ Never hardcode hex values — always use a named token
- ❌ Never use `margin: auto` for layout alignment — use flexbox gap
- ❌ Never create drop shadows not in the shadow scale
- ❌ Never use font weights other than 400, 500, 600, 700
- ❌ Never place interactive elements less than 44px × 44px (touch targets)

---

## Formatting Conventions

- Use markdown tables for token lists (scannable)
- Use code blocks for CSS values and exact strings
- Use `backtick` formatting for token names inline
- Keep descriptions short — agents scan, not read
- Put the most common tokens first in each section
- Cross-reference sections (e.g., "See Colors > Semantic for text colors to use here")

---

## File Placement

- Always: project root (same level as `package.json`, `CLAUDE.md`)
- Never: inside `src/`, `docs/`, or any subdirectory
- Name: `DESIGN.md` (exact casing)
