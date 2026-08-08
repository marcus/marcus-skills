# Design Differentiation

Audit the system for generic AI-pattern convergence. Every visual decision must trace back to the brand strategy, not to tool defaults.

This document includes specific anti-patterns observed in AI-generated design systems, contrasted with patterns from production sites by BASIC/DEPT, Instrument, Huge, AREA 17, Pentagram, Collins, Mother Design, Stripe, Linear, Vercel, Raycast, Arc, and Craft.

## The AI-Generated Design Fingerprint

AI tools converge on a recognizable aesthetic. If your design system looks like this, it will read as generated:

| AI Default | What Real Agencies Ship |
|---|---|
| Bold headings (600-700 weight) | Weight 400 headings — hierarchy through serif, size, or tracking |
| Large type scale jumps (16→24→36→48) | Flat scales — Pentagram spans only 16-19px across all heading levels |
| Pure #000000 and #ffffff | Warm off-values: #140700, #f8f8f7, #1a1714, #e8e5df |
| 5-color accent palette | One accent color or zero (Pentagram, Stripe, Collins) |
| Purple accent (#6c5ce7, #7c3aed, etc.) | Purple is AI's current favorite. Consider warm orange (#ff7600, Collins), deep navy, muted teal, or earth tones |
| Default ease / ease-in-out | Custom cubic-bezier per animation type |
| Uniform 8px border-radius | Sharp containers (0px), moderate controls (6px), pill CTA (9999px) |
| Symmetric spacing everywhere | Asymmetric: 96px vertical / 12px horizontal (Pentagram), 0/28px card padding (Linear) |
| box-shadow: 0 4px 6px rgba(0,0,0,0.1) | Multi-layer color-tinted shadows (Stripe) or zero shadows (Pentagram) |
| Every section gets decoration | Most sections are typography + whitespace only |
| Fixed breakpoint spacing | Mathematically fluid spacing: `min + (max-min) * (vw/737 - 0.509)` (Stripe) |
| One typeface in multiple weights | Serif + sans pairings for editorial tension (Collins, Craft) |
| Scale(1.05) on hover | Scale(1.018) — felt but not seen (Stripe) |
| 48-64px section gaps | 96-168px section spacing (BASIC, Pentagram, Stripe) |
| Thick left-border callouts | Icon + background tint + uniform 1px border |
| Gradient hero backgrounds | Asymmetric text layouts, no gradients unless brand-justified |
| Visible borders (#e5e5e5) | Opacity-based: rgba(0,0,0,0.06) light, rgba(255,255,255,0.05) dark |
| 16px body text | 17-19px body text (BASIC, Huge, AREA 17, Craft) |
| Letter-spacing: 0 everywhere | Negative on display (-0.025em), positive on small text (+0.01em) |
| Line-height: 1.5 everywhere | 1.0 for display, 1.1 for headings, 1.5-1.6 for body |
| Free Google Fonts | Premium purchased typefaces (Scto Grotesk A, Monument Grotesk, Suisse Intl, Sohne) |

## Shape Language

Radius should vary by purpose. A system with one radius everywhere has no shape hierarchy.

### Decision Framework

| Element type | Default guidance | Agency reference |
|---|---|---|
| Structural containers (page regions, panels, sidebars, tables) | 0px — sharp, architectural | AREA 17: 0px everywhere. BASIC: sharp containers. |
| Data-dense elements (table cells, toolbar items, tags) | 3-4px — minimal softening | Linear: 4px on small elements |
| Interactive controls (inputs, secondary buttons, selects) | 6px — moderate, functional | Vercel: 8px. Stripe: 6px inputs. |
| Elevated surfaces (cards, modals, popovers) | 8px — enough to signal elevation | Linear: 8px cards. Vercel: 8px cards. |
| Feature elements (hero cards, large panels) | 12px — emphasis without decorating | Raycast: 12px feature cards. |
| Signature elements (primary CTA, chips, pills) | 9999px — identity, distinction | Stripe: 16.5px (pill). Collins: 6rem (pill). Craft: 100px (pill). |

The brand strategy overrides these defaults. If the brand is "warm and organic," structural containers may use larger radii. If the brand is "precise and technical," even CTAs may be sharp. Document the reasoning.

### Shape Audit

- Count distinct radius values in the token system.
- If fewer than 4 values exist, the system lacks shape hierarchy.
- If every container, button, and badge shares one radius, flag it.
- Verify that radius choices map to the element-type framework above (or a documented override).

## Button Shape Strategy

Not every button should be a pill.

### When pills are appropriate

- Primary CTAs (if the brand signature supports it)
- Tags, chips, filter tokens
- Toggle groups with binary states

### When pills are NOT appropriate

- Secondary and ghost buttons (should contrast with primary to create action hierarchy)
- Destructive actions (should feel deliberate, not friendly)
- Toolbar and utility buttons (density requires compact shapes)
- Icon-only buttons (circles or rounded squares, not pills)

### Button Audit

- Do primary and secondary buttons have visually distinct shapes (not just color)?
- Does button shape reinforce the action hierarchy?
- If every button is a pill, flag it — the system has no action-level differentiation.
- Are buttons weight 400-450? Bold button text (600+) is an AI tell.

## Typography Audit

### Weight Check

- Are headings weight 400? If weight 600-700, justify with brand rationale or change.
- Does the system use non-standard variable font weights (420, 450, 510, 550, 590)? If only using 400/500/600/700, the type system is using tool defaults.
- Is there a weight reserved for subtle emphasis (nav active, table headers, badge text) that is distinct from heading weight?

### Tracking Check

- Does display text (48px+) have negative letter-spacing (-0.02em or tighter)?
- Does small text (13-14px) have positive letter-spacing (+0.01em or wider)?
- Is there a documented tracking scale with at least 3 distinct values?
- If all text has the same letter-spacing (0 or uniform), the typography is undifferentiated.

### Line-Height Check

- Does display text use line-height 1.0-1.1?
- Does body text use line-height 1.5-1.6?
- Is there variation across at least 3 distinct line-height values?
- If everything is 1.5, flag it — the system has no typographic rhythm.

### Pairing Check

- Is there a serif/sans pairing? If sans/sans or single typeface, is the choice justified?
- If using a serif, is it reserved for display/headlines only (not body)?
- Does the pairing create visible tension (editorial warmth + functional clarity)?

## Color Audit

### Temperature Check

- Are neutrals warm-shifted (brown/amber undertone) or cool-shifted (blue/slate undertone)?
- If neutrals are pure gray (#808080, #cccccc, #333333 with no hue), they are tool defaults. Add temperature.
- Does the darkest neutral have a visible hue when zoomed in? #1a1714 (warm) vs #1a1a1a (neutral) — the former is intentional.

### Accent Restraint Check

- How many accent colors exist? If more than 2, justify each with a documented role.
- Is purple the accent? Purple (#6c5ce7, #7c3aed, #8b5cf6, #6366f1) is currently the most common AI-generated accent color. Consider alternatives: warm orange, deep teal, muted indigo, ochre, dark green.
- Are functional colors (success/warning/danger/info) distinct from the accent? They should serve different roles.

### Border and Shadow Check

- Are borders using rgba opacity values, not solid hex colors?
- Is border opacity below 10%? (rgba(0,0,0,0.06) not rgba(0,0,0,0.15))
- Are shadows tinted with a hue (like Stripe's rgba(50,50,93,...)) or pure black?
- Are shadows multi-layer (2-3 layers) or single-layer? Premium sites use multi-layer.

## Layout Structure vs. Card Assembly

Pages need structural layout, not just card grids.

### Cards are appropriate for

- Collections of similar items (products, articles, team members, workflow cards)
- Content previews and teasers

### Cards are NOT appropriate for

- Primary navigation
- Structural page regions (sidebars, headers, content wells)
- Settings and configuration panels
- Single-purpose content that works inline
- Form sections
- Stats and metrics (use inline strips with dividers)
- Alerts and notifications

### Card Audit

- Estimate the percentage of each page's content area occupied by card grids.
- If more than 60% is card grids, the layout needs structural rethinking.
- Verify that at least one proof page uses a non-card structural pattern.

### Alternatives to cards

- Inline sections with typographic hierarchy
- Split layouts (30/70 or 40/60 column splits — Collins pattern)
- Data tables and list views (compact, sharp corners)
- Panel-based layouts (sidebar + main, rail + canvas)
- Numbered sections for editorial structure (AREA 17 pattern: "01", "02", "03")
- Stats as inline strips with thin vertical dividers (not metric cards)
- Timeline and activity views
- Tabbed content regions

## Whitespace Strategy

Whitespace density should vary by context, not be uniformly generous.

### Density Tiers

| Tier | Context | Section spacing | Card padding | Body size |
|---|---|---|---|---|
| Relaxed | Marketing pages, hero sections, landing pages | 128px+ | 32px | 19px |
| Standard | Documentation, dashboards, content pages | 96px | 24px | 17px |
| Compact | Data tables, toolbars, professional tools, admin UI | 48-64px | 16px | 14-15px |

### Whitespace Audit

- Does the system support at least two density tiers?
- Are product surfaces using relaxed spacing where standard or compact is appropriate?
- Is the token architecture capable of expressing density variation?
- Is section spacing at least 96px for standard density? If 48-64px, the system is using AI-default spacing.

## Motion Audit

### Easing Check

- Are custom cubic-bezier curves defined? If using `ease`, `ease-in-out`, or `linear`, these are tool defaults.
- Do different animation types use different curves? (hover vs. entrance vs. exit)
- Is there at least one aggressive custom curve? (Pentagram: `cubic-bezier(0.59, 0.01, 0.28, 1)`)

### Duration Check

- Is hover duration 150-200ms? If 300ms+, it feels sluggish for most brands. (Exception: deliberately slow brands like Craft.)
- Do exit animations use shorter duration than entrances?
- Is there a stagger delay defined (50-70ms range)?

### Scale Check

- Is hover scale 1.015-1.02? If 1.05+, it's too visible and feels toylike.
- Is press scale 0.97-0.98? If 0.95 or less, it's too dramatic.

## What We Do NOT Reject

These patterns are not inherently generic. The problem is unmotivated use.

- **Symmetry.** Grid-disciplined layouts are not generic. Linear, Vercel, and Stripe are highly symmetrical and unmistakable. The tell is undifferentiated symmetry — every section identical — not symmetry itself.
- **Gradients.** Stripe's gradients are iconic. The problem is gradients used for "modern feel" without brand justification. If the brand uses gradients, document why.
- **Generous whitespace.** Apple uses extreme whitespace effectively. The problem is uniform generosity across contexts that need different densities.
- **Card-based layouts.** Cards work for collections. The problem is cards as the only layout pattern.
- **Dark themes.** Dark-first is a valid choice (Linear, Vercel, Raycast). The problem is dark theme added as an afterthought where light/dark tokens aren't symmetrically designed.
- **Inter as a typeface.** Inter is excellent. The problem is Inter at default weights (400/500/600/700) with default tracking. Use non-standard weights (450, 510, 550, 590), pair with a serif for display text, and apply size-dependent tracking.

What IS generic:

- Neo-brutalist sharp geometry adopted as an aesthetic reaction, not a brand decision.
- Breaking grids for "visual energy" in product UI — grids should break for emphasis, not novelty.
- Unmotivated pill shapes on every interactive element.
- One radius value applied uniformly across all element types.
- **Thick left-border callouts with rounded corners.** The colored left border strip on a rounded card is the single most recognizable AI-generated design pattern. Never use it. Use icons, background tint, or uniform thin borders instead.
- **Purple accent colors.** Purple (#6c5ce7, #7c3aed, #8b5cf6) is currently over-represented in AI-generated design. It's not wrong inherently, but its prevalence makes it a tell. Unless purple has a specific brand rationale, consider alternatives.
- **Bold headings.** Weight 600-700 on every heading level is an AI default. Real agencies use weight 400.

## Core Principle

Every visual choice must answer: "Why this, for this brand?" If the answer is "because it looks modern" or "because the tool suggested it," the choice is unmotivated. Trace it back to the brand thesis, personality spectrum, or design principles — or change it.
