---
name: avalara-brand-design
description: Design and build websites that look authentically Avalara — matching the company's actual brand identity, Skylab design system, color palette (orange #fc6600, blue #059bd2), typography, layout patterns, and component conventions. Use when (1) building an Avalara-branded website, landing page, or web application, (2) creating marketing pages, product UIs, or developer portals in the Avalara style, (3) user asks for an "Avalara-style" or "Avalara-looking" design, (4) building internal tools or microsites that need to match Avalara's visual identity, (5) designing pages with Avalara's orange-and-blue color scheme, professional tone, and trust-oriented aesthetic.
---

# Avalara Brand Design

Build websites indistinguishable from Avalara's in-house work. This skill encodes the visual identity, Skylab design system, component patterns, and page architecture used across avalara.com and Avalara product UIs.

## Quick Decision Guide

| Decision | Avalara's Answer |
|----------|-----------------|
| Primary accent? | Orange `#fc6600` |
| Trust/authority color? | Blue `#059bd2` |
| Dark section background? | Teal `#025979` |
| Font strategy? | Clean sans-serif (Proxima Nova / system fallback) |
| Spacing base? | 6px |
| Grid? | 12-column, responsive |
| Border radius? | Small (4px) on interactive elements, none on data surfaces |
| Shadows? | Minimal — use 1px borders for separation |
| Primary CTA copy? | "Request a demo" / "Schedule a demo" |
| Page title format? | `{Page name} \| Avalara` |
| Tone? | Professional, clear, trustworthy, accessible |
| Accessibility? | WCAG 2.1 Level AA |

## Brand Foundation

### Identity

- **Wordmark**: Two-color sans-serif — blue letterforms with orange checkmark accent
- **Tagline**: "Making tax compliance less taxing"
- **Values**: Optimism, Passion, Adaptability, Humility, Fun, Ownership, Curiosity, Urgency, Simplicity (OPAH FOCUS)
- **Tone**: Professional yet accessible — serves enterprise and SMB equally

### Color System

```css
:root {
  /* Primary brand */
  --avalara-orange: #fc6600;
  --avalara-blue: #059bd2;
  --avalara-teal: #025979;

  /* Neutrals */
  --avalara-white: #ffffff;
  --avalara-black: #1a1a1a;
  --avalara-gray-light: #f5f5f5;
  --avalara-gray-medium: #6b7280;
  --avalara-gray-border: #e5e7eb;

  /* Status */
  --avalara-success: var(--color-green-medium);
  --avalara-warning: var(--color-yellow-medium);
  --avalara-error: var(--color-red-medium);
  --avalara-info: var(--color-blue-medium);

  /* Section theming */
  --context-theme-color: var(--avalara-white);
  --context-theme-contrast: var(--avalara-black);
}
```

**Rules**:
- Orange for CTAs, energy, accent — never for error states
- Blue for trust signals, links, primary actions, authority
- Teal (`#025979`) for dark section backgrounds with white text
- Alternate white and colored sections for visual rhythm
- Keep it restrained — color marks intent, not decoration

### Typography

```css
:root {
  --font-primary: 'Proxima Nova', 'Source Sans Pro', 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'Source Code Pro', 'Fira Code', monospace;

  /* Type scale */
  --text-xs: 0.75rem;    /* 12px — labels, fine print */
  --text-sm: 0.875rem;   /* 14px — secondary text */
  --text-md: 1rem;        /* 16px — body (base) */
  --text-lg: 1.25rem;    /* 20px — section intros */
  --text-xl: 1.5rem;     /* 24px — H3 */
  --text-xxl: 2rem;       /* 32px — H2 */
  --text-hero: 2.75rem;  /* 44px — H1 hero */

  /* Weights */
  --font-light: 300;
  --font-normal: 400;
  --font-semibold: 600;
  --font-bold: 700;
}
```

**Rules**:
- Type ramp is independent of HTML heading tags (H1–H6 are for SEO, visual size is separate)
- Headlines: semibold or bold, tight line-height (1.1–1.2)
- Body: normal weight, comfortable line-height (1.5–1.7)
- Links: always underlined (required by Avalara UX)
- Labels: uppercase with letter-spacing for form labels and category tags

### Layout & Spacing

```css
:root {
  /* 6px base spacing */
  --space-xs: 6px;
  --space-sm: 12px;
  --space-md: 18px;
  --space-lg: 24px;
  --space-xl: 48px;
  --space-xxl: 72px;
  --space-section: 96px;
}
```

**Grid**: 12-column responsive

| Breakpoint | Min | Max | Columns |
|-----------|-----|-----|---------|
| xs | 320px | 383px | 1 (stack) |
| sm | 384px | 599px | 1–2 |
| md | 600px | 839px | 2–4 |
| lg | 840px | 1259px | 4–12 |
| xl | 1260px | 1600px | 12 |

At `sm` and below, columns expand to full width unless a `sm` span is explicitly set.

## Page Architecture

### Marketing Site Structure

Every Avalara marketing page follows this skeleton:

```
┌──────────────────────────────────────┐
│ Header: Logo + Nav + "Request demo"  │
├──────────────────────────────────────┤
│ Hero: H1 + subhead + CTA            │
├──────────────────────────────────────┤
│ Stats bar: 43K+ customers, 1400+    │
│ integrations, 6M+ returns           │
├──────────────────────────────────────┤
│ Feature section (light bg)           │
├──────────────────────────────────────┤
│ Feature section (teal/dark bg)       │
├──────────────────────────────────────┤
│ Social proof: logos + testimonials   │
├──────────────────────────────────────┤
│ CTA section                          │
├──────────────────────────────────────┤
│ Footer: 5 columns + legal + locale   │
└──────────────────────────────────────┘
```

### Section Theming

Alternate between light and dark sections. Dark sections use `--avalara-teal` background with white text. Light sections use white or `--avalara-gray-light`.

```css
.section-dark {
  background: var(--avalara-teal);
  color: var(--avalara-white);
}
.section-light {
  background: var(--avalara-white);
  color: var(--avalara-black);
}
.section-subtle {
  background: var(--avalara-gray-light);
  color: var(--avalara-black);
}
```

### Navigation

- **Mega menu**: Products, Solutions, Integrations, Resources, About, Partners
- **Primary CTA** in nav: "Request a demo" (orange button, always visible)
- **Search**: Integrated in header
- **Mobile**: Hamburger collapse, full-width dropdown

### Footer

- 4–5 columns: About, Products & Services, Integrations, Resources, Contact
- Legal row: Terms, Privacy, Corporate compliance, Cookies, Privacy Rights
- Locale/region selector dropdown
- Phone: display prominently with hours

## Components

### Buttons

```css
.btn-primary {
  background: var(--avalara-orange);
  color: var(--avalara-white);
  border: none;
  border-radius: 4px;
  font-weight: var(--font-semibold);
  padding: 12px 24px;
  cursor: pointer;
  transition: background 200ms ease;
}
.btn-primary:hover { background: #e55d00; }

.btn-secondary {
  background: var(--avalara-white);
  color: var(--avalara-blue);
  border: 1px solid var(--avalara-blue);
  border-radius: 4px;
  font-weight: var(--font-semibold);
  padding: 12px 24px;
}

.btn-ghost {
  background: transparent;
  color: var(--avalara-blue);
  border: none;
  padding: 12px 24px;
  text-decoration: underline;
}
```

- Primary CTA: orange background, white text
- Secondary: white/transparent with blue border
- Ghost: text-only with underline
- Icon buttons require `aria-label` and paired tooltip

### Cards

```css
.card-product {
  background: var(--avalara-white);
  border: 1px solid var(--avalara-gray-border);
  border-radius: 4px;
  padding: var(--space-lg);
}
.card-product h3 { margin-bottom: var(--space-sm); }
.card-product .card-link {
  color: var(--avalara-blue);
  text-decoration: underline;
  font-weight: var(--font-semibold);
}
```

- Product cards: title (H3), 1–2 sentence description, "Read more" link
- Resource cards: uppercase category label (BLOG, REPORT), headline, excerpt, CTA link
- Pricing cards: business-size tier, product list, pricing hint

### Stats Block

```css
.stats-row {
  display: flex;
  justify-content: center;
  gap: var(--space-xl);
  padding: var(--space-xl) 0;
}
.stat-item {
  text-align: center;
}
.stat-number {
  font-size: var(--text-hero);
  font-weight: var(--font-bold);
  color: var(--avalara-orange);
}
.stat-label {
  font-size: var(--text-sm);
  color: var(--avalara-gray-medium);
  margin-top: var(--space-xs);
}
```

Use real stats: "43,000+ customers", "1,400+ integrations", "6M+ returns", "31M+ documents"

### Alerts

Four status variants: `error`, `warning`, `success`, `info`. Include dismiss button unless `nodismiss`. Always provide a clear, actionable message.

### Forms

- Headline: benefit-oriented (e.g., "Let's solve your tax compliance challenges together")
- Short forms — minimize fields
- Validation: inline messages below inputs with status colors
- Submit button: primary orange
- Post-submit: explain next steps ("We'll review…", "A specialist will contact…")

## Gradients

```css
.gradient-blue { background: linear-gradient(135deg, #059bd2, #025979); }
.gradient-teal { background: linear-gradient(135deg, #025979, #013d52); }
.gradient-gold { background: linear-gradient(135deg, #fc6600, #e5a100); }
.gradient-purple { background: linear-gradient(135deg, #6b21a8, #4c1d95); }
```

Use sparingly — gradients are accents, not backgrounds for large sections.

## Copy & Messaging

### Headlines

Write benefit-focused, not feature-focused:
- "Purpose-built for the systems you use — today and tomorrow"
- "Doing tax manually in a digital world? There's a better way."
- "Ready to see what Avalara can do?"

### CTA Copy

| Type | Copy |
|------|------|
| Primary | "Request a demo", "Schedule a demo", "Get started" |
| Secondary | "Read more", "Explore solutions", "Learn more" |
| Links | "Read the article", "View all", "See solutions" |

### Tone Rules

- Professional but not stiff — approachable but not casual
- Lead with customer benefit, not Avalara feature
- Quantify claims when possible (stats, percentages, customer counts)
- Avoid jargon — explain compliance concepts plainly

## Anti-Patterns

Avoid these when building Avalara-style pages:

- **Gradient blobs or glassmorphism** — Avalara uses flat, clean surfaces
- **Dark mode as default** — Avalara is light-first with dark section accents
- **Rounded cards with shadows** — use subtle borders, minimal radius
- **Dense developer-tool aesthetic** — Avalara serves business users, keep it airy
- **Orange for errors** — orange is brand accent only, red is for errors
- **Missing underlines on links** — Avalara UX requires underlined inline links
- **Generic stock photos** — prefer product screenshots, data visualizations, or clean illustrations

## Brand Assets

The `assets/` directory contains official Avalara brand files sourced from avalara.com and developer.avalara.com. Use these directly — do not recreate logos from scratch.

| File | Format | Description |
|------|--------|-------------|
| `assets/avalara-logo.svg` | SVG | Primary wordmark (672×146px, blue+orange) — use in headers |
| `assets/avalara-favicon.svg` | SVG | Favicon vector — use for `<link rel="icon">` |
| `assets/favicon.ico` | ICO | Multi-size favicon (48×48, 32×32) — legacy browser support |
| `assets/apple-touch-icon.png` | PNG | Apple touch icon (180×180) — iOS homescreen |
| `assets/safari-pinned-tab.svg` | SVG | Safari pinned tab icon — monochrome |
| `assets/avalara-dev-logo.svg` | SVG | Developer portal full wordmark ("Avalara Developer") |
| `assets/avalara-dev-small-logo.svg` | SVG | Developer portal compact mark |

### Usage

```html
<!-- Favicon setup -->
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="mask-icon" href="safari-pinned-tab.svg" color="#059bd2">

<!-- Header logo -->
<a href="/" aria-label="Avalara home">
  <img src="avalara-logo.svg" alt="Avalara" height="32">
</a>
```

### Additional assets (require Avalara SSO)

PowerPoint templates (25+), brand guide PDF, illustrations, photography, and campaign assets are available on Brandfolder at `brandfolder.com/portals/avalara`. Contact `dickson.bueno@avalara.com` for access. Partner assets at `brandfolder.com/avalara-partners`.

## References

For detailed implementation patterns:
- `references/design-tokens.md` — Complete CSS custom properties, color families, spacing scale, gradient definitions
- `references/components.md` — Full component library with HTML/CSS for every Skylab component pattern
- `references/page-patterns.md` — Complete page templates for marketing, product, pricing, and developer portal pages
