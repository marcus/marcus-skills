# Concrete Examples

## Example 1: SaaS Marketing Site (Spine A — Typography-first)

### Design Thesis
"Precise, confident, and unhurried. Let whitespace and type scale communicate premium quality without relying on illustrations or complex visuals. The oversized section numbers create rhythm and scanability."

### Specifications

**Signature motif**: Oversized section numbers (01, 02, 03) at 96px, weight 300

**Typography**:
- Font: Inter Variable
- Scale: 14 / 16 / 20 / 28 / 40 / 64 / 96
- Body: 16px, line-height 1.6
- Headlines: 40-64px, line-height 1.1, letter-spacing -0.02em

**Color tokens**:
```css
:root {
  --color-bg: #ffffff;
  --color-surface: #fafafa;
  --color-text: #0a0a0a;
  --color-text-subtle: #737373;
  --color-border: #e5e5e5;
  --color-accent: #2563eb;
}
```

**Grid**: 12-column, 1280px max-width, 24px gutters, 64px section padding

**Motion**: Dial 1 (Still) — page transitions only, no scroll animations

### Hero Section
```html
<section class="hero">
  <div class="container">
    <span class="section-number">01</span>
    <h1 class="hero-headline">Ship faster with fewer meetings.</h1>
    <p class="hero-lead">Async-first project management that respects deep work.</p>
    <div class="hero-cta">
      <a href="/signup" class="btn btn-primary">Start free trial</a>
      <a href="/demo" class="btn btn-ghost">Watch demo</a>
    </div>
  </div>
</section>
```

```css
.hero {
  padding-block: var(--space-24);
}

.section-number {
  display: block;
  font-size: 6rem;
  font-weight: 300;
  color: var(--color-border);
  line-height: 1;
  margin-bottom: var(--space-4);
}

.hero-headline {
  font-size: clamp(2.5rem, 6vw, 4rem);
  font-weight: 600;
  line-height: 1.1;
  letter-spacing: -0.02em;
  max-width: 18ch;
  margin-bottom: var(--space-4);
}

.hero-lead {
  font-size: var(--text-lg);
  color: var(--color-text-subtle);
  max-width: 45ch;
  margin-bottom: var(--space-8);
}

.hero-cta {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
}
```

---

## Example 2: Photography Portfolio (Spine B — Editorial)

### Design Thesis
"Let the photographs breathe. The design is a frame, not a competitor. Generous margins, classic typography, and full-bleed images that command attention."

### Specifications

**Signature motif**: Full-bleed images with inset caption overlays

**Typography**:
- Display: Tiempos Headline (serif)
- Body: Untitled Sans
- Scale: 14 / 16 / 18 / 24 / 32 / 48 / 72
- Body: 18px, line-height 1.7

**Color tokens**:
```css
:root {
  --color-bg: #fdfcfb;
  --color-surface: #f5f3f0;
  --color-text: #1a1a1a;
  --color-text-subtle: #6b6b6b;
  --color-border: #e8e4df;
  --color-accent: #b8860b; /* ochre */
}
```

**Grid**: Single column reading, 720px max-width for text, full-viewport for images

**Motion**: Dial 2 (Calm) — subtle image reveals on scroll

### Project Page
```html
<article class="project">
  <header class="project-header">
    <span class="project-category">Editorial</span>
    <h1 class="project-title">Northern Light</h1>
    <p class="project-meta">Iceland, 2024 — commissioned by Kinfolk Magazine</p>
  </header>

  <figure class="full-bleed">
    <img src="/images/northern-light-01.jpg" alt="Aurora over black sand beach" loading="lazy">
    <figcaption class="caption-overlay">Reynisfjara, 3:42 AM</figcaption>
  </figure>

  <div class="project-body">
    <p class="project-lead">Three weeks documenting the interplay of darkness and light along Iceland's southern coast.</p>
    <p>The brief was simple: capture winter. What emerged was a meditation on patience...</p>
  </div>
</article>
```

```css
.project-header {
  max-width: 720px;
  margin-inline: auto;
  padding: var(--space-24) var(--space-6);
  text-align: center;
}

.project-category {
  display: block;
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-text-subtle);
  margin-bottom: var(--space-4);
}

.project-title {
  font-family: var(--font-serif);
  font-size: clamp(2.5rem, 8vw, 4.5rem);
  font-weight: 400;
  line-height: 1.1;
  margin-bottom: var(--space-4);
}

.project-meta {
  font-size: var(--text-base);
  color: var(--color-text-subtle);
}

.full-bleed {
  width: 100vw;
  margin-inline: calc(50% - 50vw);
  position: relative;
}

.full-bleed img {
  width: 100%;
  height: auto;
  display: block;
}

.caption-overlay {
  position: absolute;
  bottom: var(--space-4);
  right: var(--space-4);
  background: var(--color-bg);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
}

.project-body {
  max-width: 720px;
  margin-inline: auto;
  padding: var(--space-16) var(--space-6);
}

.project-lead {
  font-size: var(--text-xl);
  line-height: 1.5;
  margin-bottom: var(--space-8);
}
```

---

## Example 3: Developer Dashboard (Spine C — Product Precision)

### Design Thesis
"Dense but not cluttered. Information-first hierarchy with monospace accents for data. Every pixel serves utility—decoration is absent."

### Specifications

**Signature motif**: Monospace stat blocks with tight 4px spacing

**Typography**:
- UI: Inter
- Data/Code: JetBrains Mono
- Scale: 12 / 14 / 16 / 20 / 24 (compact)
- Body: 14px, line-height 1.5

**Color tokens**:
```css
:root {
  --color-bg: #0a0a0a;
  --color-surface: #141414;
  --color-text: #fafafa;
  --color-text-subtle: #a3a3a3;
  --color-border: #262626;
  --color-accent: #22c55e; /* green for success/active */
  --color-danger: #ef4444;
}
```

**Grid**: Sidebar (240px) + main content, 4px base spacing

**Motion**: Dial 1 (Still) — no animations except loading states

### Stats Panel
```html
<div class="stats-grid">
  <div class="stat-card">
    <span class="stat-label">Requests (24h)</span>
    <span class="stat-value">1,247,832</span>
    <span class="stat-change stat-change-up">+12.4%</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Error Rate</span>
    <span class="stat-value">0.02%</span>
    <span class="stat-change stat-change-down">-0.01%</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Avg Response</span>
    <span class="stat-value">142ms</span>
    <span class="stat-change">—</span>
  </div>
</div>
```

```css
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-3);
}

.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.stat-label {
  display: block;
  font-size: var(--text-xs);
  color: var(--color-text-subtle);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}

.stat-value {
  display: block;
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  margin-bottom: var(--space-1);
}

.stat-change {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-text-subtle);
}

.stat-change-up { color: var(--color-accent); }
.stat-change-down { color: var(--color-danger); }
```

---

## Example 4: Creative Agency (Spine D — Bold)

### Design Thesis
"One bold move: oversized display type that bleeds off the viewport. Everything else stays restrained to let the typography dominate."

### Specifications

**Signature motif**: 120px+ headlines that crop at viewport edge

**Typography**:
- Display: ABC Diatype (or Instrument Sans, extended)
- Body: Inter
- Scale: 14 / 16 / 20 / 32 / 64 / 120 / 180
- Display: 120-180px, line-height 0.9, uppercase

**Color tokens**:
```css
:root {
  --color-bg: #0f0f0f;
  --color-surface: #1a1a1a;
  --color-text: #ffffff;
  --color-text-subtle: #808080;
  --color-border: #333333;
  --color-accent: #ff3d00; /* electric orange */
}
```

**Grid**: Fluid, edge-to-edge hero, 1400px max for body content

**Motion**: Dial 3 (Expressive) — headline parallax, hover reveals

### Hero Section
```html
<section class="hero-bold">
  <div class="hero-headline-wrap">
    <h1 class="hero-headline-bold">WE MAKE<br>BRANDS<br>MOVE</h1>
  </div>
  <div class="hero-meta">
    <p class="hero-tagline">Motion design studio based in Brooklyn</p>
    <a href="/work" class="btn btn-primary">See our work</a>
  </div>
</section>
```

```css
.hero-bold {
  min-height: 100vh;
  display: grid;
  grid-template-rows: 1fr auto;
  padding: var(--space-8);
}

.hero-headline-wrap {
  overflow: hidden;
  margin-inline: -2rem; /* bleeds to edge */
}

.hero-headline-bold {
  font-size: clamp(4rem, 18vw, 12rem);
  font-weight: 900;
  line-height: 0.9;
  letter-spacing: -0.03em;
  text-transform: uppercase;
  padding-inline: 2rem;
}

.hero-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-top: var(--space-8);
  border-top: 1px solid var(--color-border);
}

.hero-tagline {
  font-size: var(--text-base);
  color: var(--color-text-subtle);
  max-width: 30ch;
}

/* Parallax effect */
@media (prefers-reduced-motion: no-preference) {
  .hero-headline-bold {
    transform: translateY(calc(var(--scroll-y, 0) * 0.1));
  }
}
```

```js
// Simple parallax
window.addEventListener('scroll', () => {
  document.documentElement.style.setProperty('--scroll-y', window.scrollY);
});
```

---

## Quick Reference: Which Example Matches Your Brief?

| Project Type | Best Example | Key Takeaway |
|--------------|--------------|--------------|
| B2B SaaS marketing | Example 1 | Section numbers, generous space |
| Photography/art portfolio | Example 2 | Full-bleed, editorial typography |
| Dashboard/admin panel | Example 3 | Dense precision, monospace data |
| Agency/studio site | Example 4 | One bold move, everything else minimal |
