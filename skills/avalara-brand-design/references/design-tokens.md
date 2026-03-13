# Avalara Design Tokens

Complete token reference for building Avalara-branded interfaces. Derived from Skylab design system (`@avalara/skylab-sdk`) and avalara.com implementation.

## Table of Contents

- [Color Families](#color-families)
- [Semantic Color Aliases](#semantic-color-aliases)
- [Gradients](#gradients)
- [Typography Tokens](#typography-tokens)
- [Spacing Scale](#spacing-scale)
- [Breakpoints](#breakpoints)
- [Border Radius](#border-radius)
- [Shadows](#shadows)
- [Transitions](#transitions)
- [Z-Index Scale](#z-index-scale)

---

## Color Families

Skylab organizes colors by hue with intensity variants. Use CSS custom properties — never hard-code hex values.

### Primary Brand

| Token | Value | Usage |
|-------|-------|-------|
| `--avalara-orange` | `#fc6600` | Brand accent, CTAs, energy |
| `--avalara-blue` | `#059bd2` | Trust, links, primary actions |
| `--avalara-teal` | `#025979` | Dark section backgrounds |
| `--avalara-white` | `#ffffff` | Light backgrounds, text on dark |
| `--avalara-black` | `#1a1a1a` | Primary text |

### Blue Family

| Token | Approx Value | Usage |
|-------|-------------|-------|
| `--color-blue-lightest` | `#e0f4fd` | Info backgrounds, subtle highlights |
| `--color-blue-lighter` | `#a3daef` | Tag backgrounds, badges |
| `--color-blue-light` | `#4db8e2` | Hover states, secondary accents |
| `--color-blue-medium` | `#059bd2` | Links, primary buttons, brand |
| `--color-blue-dark` | `#037aaa` | Active states, emphasis |
| `--color-blue-darker` | `#025979` | Dark backgrounds, headers |
| `--color-blue-darkest` | `#013d52` | Deep backgrounds |

### Orange Family

| Token | Approx Value | Usage |
|-------|-------------|-------|
| `--color-orange-lightest` | `#fff0e0` | Warm backgrounds |
| `--color-orange-lighter` | `#ffc080` | Subtle accents |
| `--color-orange-light` | `#ff9333` | Hover states |
| `--color-orange-medium` | `#fc6600` | Primary CTAs, brand accent |
| `--color-orange-dark` | `#cc5200` | Active/pressed states |
| `--color-orange-darker` | `#993d00` | Deep emphasis |

### Gray Family

| Token | Approx Value | Usage |
|-------|-------------|-------|
| `--color-gray-lightest` | `#f5f5f5` | Page backgrounds, subtle surfaces |
| `--color-gray-lighter` | `#e5e7eb` | Borders, dividers |
| `--color-gray-light` | `#d1d5db` | Disabled borders |
| `--color-gray-medium` | `#6b7280` | Secondary text, placeholders |
| `--color-gray-dark` | `#374151` | Strong secondary text |
| `--color-gray-darker` | `#1f2937` | Headings on light bg |
| `--color-gray-darkest` | `#111827` | Near-black text |

### Green Family (Success)

| Token | Approx Value | Usage |
|-------|-------------|-------|
| `--color-green-lighter` | `#d1fae5` | Success backgrounds |
| `--color-green-light` | `#6ee7b7` | Success accents |
| `--color-green-medium` | `#10b981` | Success states, checkmarks |
| `--color-green-dark` | `#059669` | Success emphasis |
| `--color-green-darker` | `#047857` | Success text |

### Yellow Family (Warning)

| Token | Approx Value | Usage |
|-------|-------------|-------|
| `--color-yellow-light` | `#fef3c7` | Warning backgrounds |
| `--color-yellow-medium` | `#f59e0b` | Warning states |
| `--color-yellow-darker` | `#b45309` | Warning text |

### Red Family (Error)

| Token | Approx Value | Usage |
|-------|-------------|-------|
| `--color-red-lighter` | `#fee2e2` | Error backgrounds |
| `--color-red-medium` | `#ef4444` | Error states |
| `--color-red-dark` | `#dc2626` | Error emphasis |

### Purple Family

| Token | Approx Value | Usage |
|-------|-------------|-------|
| `--color-purple-lighter` | `#ede9fe` | Category backgrounds |
| `--color-purple-medium` | `#8b5cf6` | Category accents |
| `--color-purple-dark` | `#6b21a8` | Category emphasis |

### Beige Family

| Token | Approx Value | Usage |
|-------|-------------|-------|
| `--color-beige-light` | `#faf5eb` | Warm subtle backgrounds |
| `--color-beige-medium` | `#e8dcc8` | Warm borders |

---

## Semantic Color Aliases

Map semantic meaning to color tokens:

```css
:root {
  /* Actions */
  --color-action-primary: var(--avalara-orange);
  --color-action-primary-hover: #e55d00;
  --color-action-secondary: var(--avalara-blue);
  --color-action-secondary-hover: #0487b8;

  /* Text */
  --color-text-primary: var(--avalara-black);
  --color-text-secondary: var(--color-gray-medium);
  --color-text-inverse: var(--avalara-white);
  --color-text-link: var(--avalara-blue);
  --color-text-accent: var(--avalara-orange);

  /* Surfaces */
  --color-bg-primary: var(--avalara-white);
  --color-bg-secondary: var(--color-gray-lightest);
  --color-bg-dark: var(--avalara-teal);
  --color-bg-overlay: rgba(0, 0, 0, 0.5);

  /* Borders */
  --color-border-default: var(--color-gray-lighter);
  --color-border-strong: var(--color-gray-light);
  --color-border-focus: var(--avalara-blue);

  /* Status */
  --color-success: var(--color-green-medium);
  --color-success-bg: var(--color-green-lighter);
  --color-warning: var(--color-yellow-medium);
  --color-warning-bg: var(--color-yellow-light);
  --color-error: var(--color-red-medium);
  --color-error-bg: var(--color-red-lighter);
  --color-info: var(--color-blue-medium);
  --color-info-bg: var(--color-blue-lightest);
}
```

---

## Gradients

```css
:root {
  /* Brand gradients */
  --gradient-blue-dark: linear-gradient(135deg, #059bd2, #025979);
  --gradient-blue-medium: linear-gradient(135deg, #4db8e2, #059bd2);
  --gradient-teal-dark: linear-gradient(135deg, #025979, #013d52);
  --gradient-teal-medium: linear-gradient(135deg, #059bd2, #025979);
  --gradient-teal-light: linear-gradient(135deg, #4db8e2, #025979);
  --gradient-gold-medium: linear-gradient(135deg, #fc6600, #e5a100);
  --gradient-gold-light: linear-gradient(135deg, #ff9333, #fc6600);
  --gradient-purple-dark: linear-gradient(135deg, #6b21a8, #4c1d95);
  --gradient-purple-light: linear-gradient(135deg, #8b5cf6, #6b21a8);
}
```

Gradients are for hero accents, section transitions, and decorative elements — not for large background fills.

---

## Typography Tokens

```css
:root {
  /* Font stacks */
  --font-sans: 'Proxima Nova', 'Source Sans Pro', 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-mono: 'Source Code Pro', 'Fira Code', 'Consolas', monospace;

  /* Base */
  --text-base-size: 16px;
  --text-base-line-height: 1.6;

  /* Scale */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-md: 1rem;         /* 16px */
  --text-lg: 1.25rem;     /* 20px */
  --text-xl: 1.5rem;      /* 24px */
  --text-xxl: 2rem;        /* 32px */
  --text-hero: 2.75rem;   /* 44px */
  --text-display: 3.5rem; /* 56px */

  /* Weights */
  --font-light: 300;
  --font-normal: 400;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line heights */
  --leading-tight: 1.1;
  --leading-snug: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.6;
  --leading-loose: 1.75;

  /* Letter spacing */
  --tracking-tight: -0.02em;
  --tracking-normal: 0;
  --tracking-wide: 0.05em;
  --tracking-wider: 0.1em;
}
```

### Type Ramp Application

| Element | Size | Weight | Line Height | Tracking |
|---------|------|--------|-------------|----------|
| Display (hero H1) | `--text-display` | `--font-bold` | `--leading-tight` | `--tracking-tight` |
| Page title (H1) | `--text-hero` | `--font-bold` | `--leading-tight` | `--tracking-tight` |
| Section heading (H2) | `--text-xxl` | `--font-semibold` | `--leading-snug` | `--tracking-normal` |
| Subsection (H3) | `--text-xl` | `--font-semibold` | `--leading-snug` | `--tracking-normal` |
| Intro text | `--text-lg` | `--font-normal` | `--leading-relaxed` | `--tracking-normal` |
| Body | `--text-md` | `--font-normal` | `--leading-relaxed` | `--tracking-normal` |
| Secondary text | `--text-sm` | `--font-normal` | `--leading-normal` | `--tracking-normal` |
| Labels / tags | `--text-xs` | `--font-semibold` | `--leading-normal` | `--tracking-wider` |

---

## Spacing Scale

6px base unit. Consistent across padding, margin, and gap.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-none` | `0` | Reset |
| `--space-xs` | `6px` | Tight gaps (icon-to-text, badge padding) |
| `--space-sm` | `12px` | Component internal padding |
| `--space-md` | `18px` | Default spacing between elements |
| `--space-lg` | `24px` | Card padding, group spacing |
| `--space-xl` | `48px` | Section internal padding |
| `--space-xxl` | `72px` | Section vertical padding |
| `--space-section` | `96px` | Between major page sections |

Padding and margin utility classes follow `pad-{direction}-{size}` and `margin-{direction}-{size}` where direction is `all`, `top`, `end`, `bottom`, `start` and size is `none`, `xs`, `sm`, `md`, `lg`, `xl`.

---

## Breakpoints

| Name | Min | Max | Typical Layout |
|------|-----|-----|---------------|
| `xs` | 320px | 383px | Single column, stacked |
| `sm` | 384px | 599px | Single or 2-column |
| `md` | 600px | 839px | 2–4 columns |
| `lg` | 840px | 1259px | Full multi-column |
| `xl` | 1260px | 1600px | Full 12-column grid |

```css
@media (max-width: 383px)  { /* xs */ }
@media (min-width: 384px) and (max-width: 599px) { /* sm */ }
@media (min-width: 600px) and (max-width: 839px) { /* md */ }
@media (min-width: 840px) and (max-width: 1259px) { /* lg */ }
@media (min-width: 1260px) { /* xl */ }
```

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-none` | `0` | Data surfaces, tables, full-width sections |
| `--radius-sm` | `4px` | Buttons, inputs, cards, badges |
| `--radius-md` | `8px` | Modals, larger containers |
| `--radius-lg` | `12px` | Alerts, promotional elements |
| `--radius-full` | `9999px` | Pills, avatars, dots |

Avalara uses conservative radius — most components are `4px`. Sections and data surfaces have no radius.

---

## Shadows

Avalara uses minimal elevation. Prefer borders over shadows for separation.

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift on hover |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.07)` | Cards on hover |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Modals, dropdowns |
| `--shadow-xl` | `0 20px 25px rgba(0,0,0,0.12)` | Overlays |

---

## Transitions

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | `150ms` | Hover states, color changes |
| `--duration-normal` | `200ms` | Most interactions |
| `--duration-slow` | `300ms` | Modals, panels, reveals |
| `--ease-default` | `ease` | Standard transitions |
| `--ease-out` | `cubic-bezier(0.16, 1, 0.3, 1)` | Slide-in panels |

---

## Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--z-base` | `0` | Normal flow |
| `--z-sticky` | `10` | Sticky headers |
| `--z-dropdown` | `20` | Dropdowns, mega menu |
| `--z-overlay` | `30` | Overlay backgrounds |
| `--z-modal` | `40` | Modals, dialogs |
| `--z-toast` | `50` | Toast notifications |
| `--z-tooltip` | `60` | Tooltips |

---

## Complete Token File

Copy this as a starting point for any Avalara-branded project:

```css
:root {
  /* Brand */
  --avalara-orange: #fc6600;
  --avalara-blue: #059bd2;
  --avalara-teal: #025979;
  --avalara-white: #ffffff;
  --avalara-black: #1a1a1a;

  /* Neutrals */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;

  /* Font */
  --font-sans: 'Proxima Nova', 'Source Sans Pro', 'Inter', system-ui, sans-serif;
  --font-mono: 'Source Code Pro', 'Fira Code', monospace;

  /* Spacing (6px base) */
  --space-1: 6px;
  --space-2: 12px;
  --space-3: 18px;
  --space-4: 24px;
  --space-6: 36px;
  --space-8: 48px;
  --space-12: 72px;
  --space-16: 96px;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);

  /* Motion */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
}
```
