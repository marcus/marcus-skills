# Typography Specimens

Comprehensive reference for type pairing, fluid scaling, OpenType features, and specimen templates.

## 1. Pairing Rationale Framework

Every type pairing encodes a relationship. The display face carries brand voice; the body face carries usability. The pairing succeeds when both faces share structural kinship but differ in personality.

### Evaluation Criteria

| Criterion | What to Check | Why It Matters |
|---|---|---|
| x-height ratio | Overlay lowercase "x" from both faces at same size | Mismatched x-heights create visual discord at small sizes |
| Weight complement | Compare regular weights side by side | If both are light, nothing anchors; if both are heavy, nothing breathes |
| Contrast model | Serif stroke variation vs. sans uniformity | High-contrast serif + low-contrast sans = classic tension |
| Historical kinship | Do the faces share an era or design lineage? | Humanist sans + humanist serif feel cohesive; geometric sans + old-style serif feel intentionally tense |
| Role clarity | Can you immediately tell which is display and which is body? | Ambiguous pairings create hierarchy confusion |

### Questions Before Committing

- Does the serif carry enough authority for headlines without feeling dated?
- Does the sans maintain clarity at 14px on low-density screens?
- At the smallest body size (0.75rem), is the sans still legible?
- At the largest display size (clamp range), does the serif still feel controlled?
- Do the italic forms of both faces hold up? Body italic will appear in emphasis; display italic may appear in pull quotes.

### Pairing Decision Template

```
Pairing Name: [e.g., "Editorial Authority"]

Display Face: [family name]
  Category: [serif / sans / slab / mono]
  Character: [what it communicates in one phrase]
  Strengths: [where it excels]
  Risks: [where it struggles]

Body Face: [family name]
  Category: [serif / sans / slab / mono]
  Character: [what it communicates in one phrase]
  Strengths: [where it excels]
  Risks: [where it struggles]

Relationship: [tension / harmony / contrast]
Rationale: [one sentence on why these two belong together]

x-height match: [close / acceptable / needs optical adjustment]
Weight balance: [complementary / overlapping / needs restriction]
Fallback stack: [full CSS font-family for each]
```

### Example: Current System Pairing

```
Display: Iowan Old Style (Palatino Linotype, Book Antiqua, Georgia fallbacks)
  Category: Old-style serif
  Character: Literate warmth with editorial credibility
  Strengths: Beautiful at large sizes, strong italic, distinctive

Body: Avenir Next (Segoe UI, Helvetica Neue fallbacks)
  Category: Geometric-humanist sans
  Character: Clean precision with approachable warmth
  Strengths: Excellent weight range, strong legibility, neutral

Relationship: Productive tension
Rationale: Old-style serif warmth against geometric clarity creates
an editorial voice that feels trustworthy without being stiff.
```

## 2. Fluid Type Strategy

Use `clamp()` for responsive type that scales smoothly without breakpoint jumps.

### Formula

```
font-size: clamp(minimum, preferred, maximum);
```

Where preferred typically uses a viewport-relative calculation:

```
preferred = base + (viewport-coefficient * 1vw)
```

### Calculating a Fluid Step

To scale from `min` at viewport `vw-min` to `max` at viewport `vw-max`:

```
slope = (max - min) / (vw-max - vw-min)
intercept = min - (slope * vw-min)
preferred = intercept[rem] + slope[vw]
```

Example for `--text-6` (3.25rem at 480px to 5.5rem at 1440px):

```
slope = (5.5 - 3.25) / (90 - 30) = 0.0375
intercept = 3.25 - (0.0375 * 30) = 2.125
preferred = 2.125rem + 3.75vw
result: clamp(3.25rem, 2.125rem + 3.75vw, 5.5rem)
```

### Complete Fluid Scale Template

```css
:root {
  /* Static steps: small sizes don't need fluid scaling */
  --text-00: 0.75rem;                              /* 12px - captions, badges */
  --text-0:  0.875rem;                             /* 14px - labels, metadata */
  --text-1:  1rem;                                 /* 16px - body baseline */
  --text-2:  1.125rem;                             /* 18px - lead paragraphs */

  /* Fluid steps: larger sizes scale with viewport */
  --text-3:  clamp(1.25rem, 1.1rem + 0.5vw, 1.375rem);     /* subheadings */
  --text-4:  clamp(1.5rem, 1.2rem + 1vw, 1.75rem);         /* section heads */
  --text-5:  clamp(2rem, 1.5rem + 1.5vw, 2.5rem);          /* page titles */
  --text-6:  clamp(3.25rem, 2.125rem + 3.75vw, 5.5rem);    /* hero display */
}
```

### Breakpoint Behavior

| Token | Compact (320px) | Medium (768px) | Expanded (1440px) |
|---|---|---|---|
| `--text-00` | 12px | 12px | 12px |
| `--text-0` | 14px | 14px | 14px |
| `--text-1` | 16px | 16px | 16px |
| `--text-2` | 18px | 18px | 18px |
| `--text-3` | 20px | 21px | 22px |
| `--text-4` | 24px | 26px | 28px |
| `--text-5` | 32px | 36px | 40px |
| `--text-6` | 52px | 72px | 88px |

Rules:

- Body sizes (text-00 through text-2) stay fixed. Readers need stability.
- Display sizes (text-5, text-6) should change dramatically. Headlines that feel right on desktop look absurd on mobile.
- Middle steps (text-3, text-4) scale gently. They bridge the gap.

## 3. OpenType Feature Guide

### Feature Map

| Feature | CSS Property | Use In | Avoid In |
|---|---|---|---|
| Standard ligatures | `font-variant-ligatures: common-ligatures` | Body text, headings | Code blocks, URLs |
| Discretionary ligatures | `font-variant-ligatures: discretionary-ligatures` | Display headings, pull quotes | Body text, UI labels |
| Old-style figures | `font-variant-numeric: oldstyle-nums` | Body paragraphs, editorial content | Tables, data displays, forms |
| Lining figures | `font-variant-numeric: lining-nums` | Tables, UI, forms | Long-form reading |
| Tabular figures | `font-variant-numeric: tabular-nums` | Data tables, pricing, dashboards | Body text |
| Proportional figures | `font-variant-numeric: proportional-nums` | Body text, running copy | Columns of numbers |
| Small caps | `font-variant-caps: small-caps` | Kickers, labels, acronyms in body | Headings, buttons |
| Stylistic alternates | `font-feature-settings: "salt" 1` | Display type, brand moments | Body text |
| Fractions | `font-variant-numeric: diagonal-fractions` | Recipes, measurements | General body |
| Kerning | `font-kerning: normal` | Everywhere | Never disable unless debugging |

### CSS Implementation

```css
/* Body text: readable figures, standard ligatures */
.body-text {
  font-variant-ligatures: common-ligatures;
  font-variant-numeric: oldstyle-nums proportional-nums;
  font-kerning: normal;
}

/* Display heading: ligatures, tight spacing */
.display-heading {
  font-variant-ligatures: common-ligatures discretionary-ligatures;
  font-kerning: normal;
}

/* Data table: aligned columns */
.data-table td {
  font-variant-numeric: lining-nums tabular-nums;
}

/* Kicker/label: small caps */
.kicker {
  font-variant-caps: small-caps;
  letter-spacing: 0.05em; /* small caps need looser tracking */
}

/* Code: no ligatures */
code, pre {
  font-variant-ligatures: none;
}
```

Rules:

- Always check that the font file includes the OpenType features you reference. System font stacks vary.
- Prefer `font-variant-*` longhand over `font-feature-settings`. The longhand cascades properly.
- Test tabular figures with real data columns. Misaligned decimals in a pricing table destroy credibility.

## 4. Typographic Specimens

Templates for demonstrating type in context. Each specimen defines role, token usage, and CSS.

### Hero Headline

```
Role: Primary page-level statement
Font: var(--font-display)
Size: var(--text-6)
Line-height: var(--leading-tight)
Tracking: var(--tracking-tight)
Color: var(--color-fg-strong)
Max-width: none (let it run)
```

```css
.hero-headline {
  font-family: var(--font-display);
  font-size: var(--text-6);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  color: var(--color-fg-strong);
  margin: 0;
}
```

### Section Heading

```
Role: Content section divider
Font: var(--font-display)
Size: var(--text-5)
Line-height: var(--leading-snug)
Tracking: var(--tracking-tight)
Color: var(--color-fg-strong)
```

```css
.section-heading {
  font-family: var(--font-display);
  font-size: var(--text-5);
  line-height: var(--leading-snug);
  letter-spacing: var(--tracking-tight);
  color: var(--color-fg-strong);
  margin: 0;
}
```

### Body Paragraph

```
Role: Primary reading text
Font: var(--font-body)
Size: var(--text-1)
Line-height: var(--leading-body)
Tracking: normal
Color: var(--color-fg-default)
Max-width: var(--content-narrow) (enforces 45-75 char measure)
```

```css
.body-paragraph {
  font-family: var(--font-body);
  font-size: var(--text-1);
  line-height: var(--leading-body);
  color: var(--color-fg-default);
  max-width: var(--content-narrow);
  font-variant-numeric: oldstyle-nums proportional-nums;
}
```

### Pull Quote

```
Role: Highlighted excerpt for editorial emphasis
Font: var(--font-display)
Size: var(--text-4)
Line-height: var(--leading-snug)
Tracking: normal
Color: var(--color-fg-strong)
Style: italic
Treatment: border-left or oversized quotation mark
```

```css
.pull-quote {
  font-family: var(--font-display);
  font-size: var(--text-4);
  line-height: var(--leading-snug);
  font-style: italic;
  color: var(--color-fg-strong);
  max-width: var(--content-narrow);
  padding-left: var(--space-5);
  border-left: 3px solid var(--color-accent);
}
```

### Data Table

```
Role: Structured information with aligned numbers
Font: var(--font-body)
Size: var(--text-0)
Line-height: var(--leading-snug)
Tracking: normal
Numeric: tabular-nums lining-nums
```

```css
.data-table {
  font-family: var(--font-body);
  font-size: var(--text-0);
  line-height: var(--leading-snug);
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  font-weight: 600;
  color: var(--color-fg-muted);
  text-transform: uppercase;
  font-size: var(--text-00);
  letter-spacing: var(--tracking-label);
  padding: var(--space-2) var(--space-3);
  border-bottom: var(--border-strong) solid var(--color-border-strong);
}

.data-table td {
  padding: var(--space-2) var(--space-3);
  border-bottom: var(--border-thin) solid var(--color-border-subtle);
  font-variant-numeric: tabular-nums lining-nums;
}
```

### Code Block

```
Role: Source code or terminal output
Font: var(--font-mono)
Size: var(--text-0)
Line-height: var(--leading-snug)
Tracking: normal
Ligatures: none
```

```css
.code-block {
  font-family: var(--font-mono);
  font-size: var(--text-0);
  line-height: var(--leading-snug);
  font-variant-ligatures: none;
  background: var(--color-bg-soft);
  padding: var(--space-4);
  border-radius: var(--radius-2);
  overflow-x: auto;
  tab-size: 2;
}
```

### Navigation Label

```
Role: Primary navigation item text
Font: var(--font-body)
Size: var(--text-0)
Line-height: 1
Tracking: normal
Weight: 500
Color: var(--color-fg-muted), active: var(--nav-item-fg-active)
```

```css
.nav-label {
  font-family: var(--font-body);
  font-size: var(--text-0);
  font-weight: 500;
  line-height: 1;
  color: var(--color-fg-muted);
  white-space: nowrap;
}
```

### Badge / Pill Text

```
Role: Status indicator, tag, category label
Font: var(--font-body)
Size: var(--text-00)
Line-height: 1
Tracking: var(--tracking-label)
Transform: uppercase
Weight: 600
```

```css
.badge-text {
  font-family: var(--font-body);
  font-size: var(--text-00);
  font-weight: 600;
  line-height: 1;
  letter-spacing: var(--tracking-label);
  text-transform: uppercase;
  white-space: nowrap;
}
```

## 5. Numeric Typography

### Figure Styles

| Style | CSS | When to Use |
|---|---|---|
| Old-style, proportional | `font-variant-numeric: oldstyle-nums proportional-nums` | Body text, editorial, running prose |
| Lining, tabular | `font-variant-numeric: lining-nums tabular-nums` | Tables, dashboards, pricing, forms |
| Lining, proportional | `font-variant-numeric: lining-nums proportional-nums` | Headings with numbers, UI labels |
| Old-style, tabular | `font-variant-numeric: oldstyle-nums tabular-nums` | Rare. Tabular body text with inline numbers |

### Visual Difference

- **Old-style**: digits have ascenders and descenders (3, 4, 5, 7, 9 drop below baseline). Blend into body text like lowercase letters.
- **Lining**: all digits sit on the baseline at cap height. Uniform, formal, suited to isolated numeric display.
- **Tabular**: every digit occupies the same horizontal width. Columns of numbers align vertically.
- **Proportional**: digits occupy natural width. 1 is narrower than 8. Better for inline use.

### Implementation Pattern

```css
/* Default body: blend numbers into reading flow */
body {
  font-variant-numeric: oldstyle-nums proportional-nums;
}

/* Override for data contexts */
table, .dashboard, .price, input[type="number"] {
  font-variant-numeric: lining-nums tabular-nums;
}
```

## 6. Measure and Reading Comfort

### Optimal Line Length by Context

| Context | Target Characters | CSS Approach |
|---|---|---|
| Long-form reading | 55-70 characters | `max-width: 36rem` at 16px body |
| General body | 45-75 characters | `max-width: var(--content-narrow)` (46rem) |
| Wide scanning (dashboards) | 80-100+ characters | No max-width constraint |
| Narrow columns (sidebar, card) | 25-40 characters | Container width controls measure |
| Pull quotes | 35-50 characters | `max-width: 28rem` |

### Enforcing Measure

```css
/* Reading measure utility */
.measure       { max-width: var(--content-narrow); }  /* ~46rem, 70-75ch */
.measure--tight { max-width: 36rem; }                  /* ~55-60ch */
.measure--wide  { max-width: var(--content-wide); }    /* scanning layouts */
```

Rules:

- Never set measure with `ch` units alone. The `ch` unit varies by font; use `rem` for predictability, then verify character count.
- Apply measure to the text container, not the text element. This preserves layout flexibility.
- At compact viewports, measure is controlled by screen width plus padding. Do not add `max-width` that fights the viewport.

## 7. Vertical Rhythm

### Baseline Rhythm

Choose a base unit derived from body line-height. With `--text-1: 1rem` and `--leading-body: 1.62`, the rhythm unit is approximately `1.62rem` (25.92px at 16px base).

For practical spacing, use the spacing scale (`--space-*`) aligned to maintain rhythm:

- `--space-4` (1rem) = roughly 0.6 rhythm units
- `--space-5` (1.5rem) = roughly 0.9 rhythm units
- `--space-6` (2rem) = roughly 1.2 rhythm units

### Verifying Rhythm

1. Enable a baseline grid overlay at the rhythm unit interval.
2. Check that paragraph spacing aligns text back to the grid.
3. Headings break rhythm intentionally (different line-height) but the following body text should re-enter the grid within one line.

### Spacing Between Typographic Elements

| Transition | Recommended Spacing | Token |
|---|---|---|
| Heading to body | Tight coupling | `--space-3` to `--space-4` |
| Body to body (paragraph) | One rhythm unit | `margin-bottom` equal to line-height |
| Body to heading | Generous separation | `--space-6` to `--space-7` |
| Section to section | Major break | `--space-7` to `--space-9` |
| List item to list item | Half rhythm | `--space-2` |

### Implementation Pattern

```css
/* Prose container: consistent rhythm for stacked elements */
.prose > * + * {
  margin-top: var(--space-4);
}

.prose > h2,
.prose > h3 {
  margin-top: var(--space-7);
}

.prose > h2 + *,
.prose > h3 + * {
  margin-top: var(--space-3);
}
```

Rules:

- Perfect baseline alignment across all elements is a myth in CSS. Aim for consistent spacing relationships, not pixel-perfect grid lock.
- Use the spacing scale tokens. Do not introduce arbitrary margin values.
- Headings create intentional rhythm breaks. The break signals hierarchy. Do not force headings onto the body baseline grid.
- Verify rhythm visually at body size. If the spacing feels even and breathing is consistent, the rhythm is working.
