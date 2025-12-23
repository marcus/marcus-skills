# Typography Systems (Detailed Reference)

## Type Strategy Selection

### Option 1: Single Superfamily (Variable)
Best for: Clean, modern, cohesive systems. Fast loading.

**Recommended fonts**:
- **Inter** — Swiss neutrality, huge glyph set, variable
- **Söhne** — Akzidenz Grotesk lineage, premium feel
- **Geist** — Vercel's font, developer-focused, crisp
- **Plus Jakarta Sans** — Geometric, friendly, open source
- **Instrument Sans** — Contemporary, slightly quirky

**Usage pattern**:
```css
:root {
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
}

.heading { font-weight: 600; }
.body { font-weight: 400; }
.label { font-weight: 500; letter-spacing: 0.02em; text-transform: uppercase; font-size: 0.75rem; }
```

### Option 2: Serif + Sans Pairing
Best for: Editorial authority, warmth, sophistication.

**Recommended pairings**:
| Serif (Display) | Sans (Body) | Mood |
|-----------------|-------------|------|
| Tiempos Headline | Söhne | Premium editorial |
| GT Sectra | Graphik | Contemporary magazine |
| Freight Display | Freight Sans | Classic publishing |
| Playfair Display | Source Sans 3 | Accessible elegance |
| Lora | Inter | Open source quality |

**Usage pattern**:
```css
:root {
  --font-serif: 'Tiempos Headline', 'Georgia', serif;
  --font-sans: 'Söhne', 'Helvetica Neue', sans-serif;
}

h1, h2, h3 { font-family: var(--font-serif); }
body, p, li { font-family: var(--font-sans); }
```

### Option 3: Sans + Mono Accent
Best for: Technical credibility, developer tools, documentation.

**Recommended pairings**:
| Sans (Primary) | Mono (Accent) | Use case |
|----------------|---------------|----------|
| Inter | JetBrains Mono | Developer tools |
| SF Pro | SF Mono | Apple ecosystem |
| IBM Plex Sans | IBM Plex Mono | Enterprise tech |
| Geist | Geist Mono | Modern dev tools |

**Usage pattern**:
```css
:root {
  --font-sans: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', 'Consolas', monospace;
}

code, .stat, .data-value { font-family: var(--font-mono); }
```

---

## Type Scale Systems

### Scale A: Minimal (6 steps)
For: Simple marketing pages, portfolios.

| Step | Size | Use |
|------|------|-----|
| xs | 12px / 0.75rem | Captions, labels |
| sm | 14px / 0.875rem | Secondary text |
| base | 16px / 1rem | Body copy |
| lg | 20px / 1.25rem | Lead paragraphs |
| xl | 32px / 2rem | Section headings |
| 2xl | 48px / 3rem | Page titles |

```css
:root {
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 2rem;
  --text-2xl: 3rem;
}
```

### Scale B: Extended (9 steps)
For: Complex apps, documentation, marketing + product.

| Step | Size | Line-height | Use |
|------|------|-------------|-----|
| xs | 12px | 1.5 | Captions, badges |
| sm | 14px | 1.5 | Labels, metadata |
| base | 16px | 1.6 | Body |
| lg | 18px | 1.6 | Lead paragraphs |
| xl | 24px | 1.4 | Card titles |
| 2xl | 32px | 1.3 | Section headings |
| 3xl | 48px | 1.2 | Page headings |
| 4xl | 64px | 1.1 | Hero headlines |
| 5xl | 96px | 1.0 | Display (rare) |

```css
:root {
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.5rem;     /* 24px */
  --text-2xl: 2rem;      /* 32px */
  --text-3xl: 3rem;      /* 48px */
  --text-4xl: 4rem;      /* 64px */
  --text-5xl: 6rem;      /* 96px */

  --leading-tight: 1.1;
  --leading-snug: 1.3;
  --leading-normal: 1.5;
  --leading-relaxed: 1.7;
}
```

### Scale C: Fluid (clamp-based)
For: Responsive-first, fewer breakpoints.

```css
:root {
  --text-sm: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
  --text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-lg: clamp(1.25rem, 1rem + 1vw, 1.5rem);
  --text-xl: clamp(1.5rem, 1rem + 2vw, 2.5rem);
  --text-2xl: clamp(2rem, 1.5rem + 3vw, 4rem);
  --text-display: clamp(2.5rem, 2rem + 5vw, 6rem);
}
```

---

## Line-Height Rules

| Content type | Line-height | Why |
|--------------|-------------|-----|
| Body text (16-18px) | 1.5–1.7 | Readability |
| Long-form reading | 1.7–1.8 | Comfort |
| UI labels | 1.2–1.4 | Compact |
| Headings (24-48px) | 1.2–1.3 | Tighter looks intentional |
| Display (64px+) | 1.0–1.1 | Dramatic, cropped |

---

## Letter-Spacing Rules

| Context | Tracking | Why |
|---------|----------|-----|
| Body text | 0 (default) | Natural |
| All-caps labels | +0.05em to +0.1em | Legibility |
| Large display (64px+) | -0.02em to -0.03em | Optical tightening |
| Monospace | 0 | Fixed-width |

```css
.label {
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: var(--text-xs);
  font-weight: 500;
}

.display-heading {
  font-size: var(--text-display);
  letter-spacing: -0.02em;
  line-height: 1.05;
}
```

---

## Font Loading Strategy

```html
<head>
  <!-- Preload critical fonts -->
  <link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>

  <style>
    @font-face {
      font-family: 'Inter';
      src: url('/fonts/inter-var.woff2') format('woff2');
      font-weight: 100 900;
      font-display: swap;
    }
  </style>
</head>
```

**Rules**:
- Preload only 1-2 critical fonts
- Use `font-display: swap` for body, `optional` for display
- Subset fonts if using only Latin characters
- Variable fonts reduce HTTP requests
