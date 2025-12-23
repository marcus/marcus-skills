# Design Spines (Detailed Reference)

Choose ONE spine to establish the foundation. Each spine has a signature approach—don't mix them arbitrarily.

---

## Spine A — Typography-first Minimal

**Philosophy**: Let type hierarchy carry the entire design. Space and scale create drama.

**Signature moves**:
- Oversized section numbers (01, 02, 03) at 96-144px
- Extreme type scale contrast (14px body → 72px headings)
- Hairline rules (1px) as the only visual separator
- Single accent color used sparingly (<10% of surface)

**Best for**: Premium SaaS, consulting firms, portfolios with strong writing, legal/finance.

**Type pairing**: Single variable sans-serif (Inter, Söhne, Geist, Untitled Sans)

**Reference sites**: Linear, Vercel, Stripe dashboard, Notion marketing

**CSS structure**:
```css
.section {
  --section-gap: clamp(4rem, 10vw, 8rem);
  padding-block: var(--section-gap);
  border-bottom: 1px solid var(--color-border);
}

.heading-display {
  font-size: clamp(2.5rem, 8vw, 4.5rem);
  line-height: 1.05;
  letter-spacing: -0.02em;
  font-weight: 500;
}

.section-number {
  font-size: clamp(4rem, 12vw, 9rem);
  font-weight: 300;
  color: var(--color-subtle);
  line-height: 1;
}
```

---

## Spine B — Editorial Craft

**Philosophy**: Magazine-quality typography with intentional rhythm. Photography-led, text as complementary voice.

**Signature moves**:
- Serif headlines + sans body (or reversed)
- Pull quotes with oversized quotation marks
- Full-bleed images with inset caption overlay
- Multi-column layouts that break on mobile
- Generous line-height (1.7+) for reading comfort

**Best for**: Publishers, photographers, studios, essays, magazines, literary portfolios.

**Type pairing**:
- Display: Tiempos Headline, GT Sectra, Freight Display, Editorial New
- Body: Suisse Int'l, Graphik, Söhne, Akkurat

**Reference sites**: New York Times features, Kinfolk, Eye on Design, Pentagram case studies

**CSS structure**:
```css
.article {
  --measure: 65ch;
  max-width: var(--measure);
  margin-inline: auto;
  font-size: 1.125rem;
  line-height: 1.75;
}

.pull-quote {
  font-family: var(--font-serif);
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  font-style: italic;
  border-left: 4px solid var(--color-accent);
  padding-left: 1.5rem;
  margin-block: 3rem;
}

.full-bleed {
  width: 100vw;
  margin-inline: calc(50% - 50vw);
  position: relative;
}

.full-bleed figcaption {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  background: var(--color-surface);
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}
```

---

## Spine C — Product Precision

**Philosophy**: Dense information with clear hierarchy. Every pixel serves utility.

**Signature moves**:
- Tight 4px spacing scale (4/8/12/16/24/32)
- High-contrast borders and dividers
- Monospace accents for data/stats
- Compact navigation with icon labels
- Tables and lists as primary content format

**Best for**: Dashboards, dev tools, B2B SaaS, admin panels, documentation.

**Type pairing**:
- UI: Inter, SF Pro, IBM Plex Sans
- Code/Data: JetBrains Mono, IBM Plex Mono, Berkeley Mono

**Reference sites**: GitHub, Figma, Linear app, Raycast

**CSS structure**:
```css
:root {
  --space-unit: 4px;
  --space-xs: calc(var(--space-unit) * 1);   /* 4px */
  --space-sm: calc(var(--space-unit) * 2);   /* 8px */
  --space-md: calc(var(--space-unit) * 4);   /* 16px */
  --space-lg: calc(var(--space-unit) * 6);   /* 24px */
  --space-xl: calc(var(--space-unit) * 8);   /* 32px */
}

.data-table {
  font-size: 0.875rem;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: var(--space-sm) var(--space-md);
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 2rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
```

---

## Spine D — Bold but Controlled

**Philosophy**: One distinctive visual move, repeated as motif. Memorable without chaos.

**Signature moves** (pick ONE):
- Oversized display type (100px+) that crops at viewport edge
- Diagonal or angled grid (consistent 12° or 15°)
- Strong color block sections with reverse type
- Kinetic headline on scroll (parallax or rotation)
- Unusual grid (5-column, offset, overlapping elements)

**Best for**: Agencies, creators, brands needing memorability, campaign sites, portfolio sites.

**Type choices**:
- Display: Basement Grotesque, ABC Diatype, Instrument Sans, GT America Extended
- Pair with neutral body: system sans or Inter

**Reference sites**: Awards sites (Awwwards, FWA), Spotify campaigns, Nike product pages

**CSS structure** (oversized type example):
```css
.hero-headline {
  font-size: clamp(4rem, 20vw, 12rem);
  font-weight: 900;
  line-height: 0.9;
  letter-spacing: -0.03em;
  text-transform: uppercase;
  overflow: hidden;
}

/* Crops at edge */
.hero-headline-wrapper {
  margin-inline: -2rem;
  padding-inline: 2rem;
  overflow: hidden;
}

/* Diagonal section */
.diagonal-section {
  --skew: -6deg;
  transform: skewY(var(--skew));
  padding-block: 8rem;
}

.diagonal-section > * {
  transform: skewY(calc(var(--skew) * -1));
}
```

---

## Choosing Your Spine

| Question | If yes → |
|----------|----------|
| Is the content primarily text/writing? | Spine A or B |
| Does the brand have strong photography? | Spine B |
| Is this a data-heavy product/dashboard? | Spine C |
| Does the brand need to stand out visually? | Spine D |
| Is the audience developers/technical? | Spine A or C |
| Is budget/timeline tight? | Spine A (simplest) |
