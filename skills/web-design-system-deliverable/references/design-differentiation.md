# Design Differentiation

Audit the system for generic AI-pattern convergence. Every visual decision must trace back to the brand strategy, not to tool defaults.

## Shape Language

Radius should vary by purpose. A system with one radius everywhere has no shape hierarchy.

### Decision Framework

| Element type | Default guidance | Override with brand rationale |
|---|---|---|
| Structural containers (cards, panels, page regions) | Small radius or none — precision, architecture | Yes |
| Interactive controls (buttons, fields, selects) | Moderate radius — approachability, clarity | Yes |
| Signature elements (primary CTA, brand marks, hero badges) | Pill-shaped — identity, distinction | Yes |
| Data-dense elements (table cells, toolbar items, compact UI) | Sharp or minimal radius — density, efficiency | Yes |

The brand strategy overrides these defaults. If the brand is "warm and organic," structural containers may use larger radii. If the brand is "precise and technical," even CTAs may be sharp. Document the reasoning.

### Shape Audit

- Count distinct radius values in the token system.
- If fewer than 3 values exist, the system lacks shape hierarchy.
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

## Layout Structure vs. Card Assembly

Pages need structural layout, not just card grids.

### Cards are appropriate for

- Collections of similar items (products, articles, team members)
- Dashboard metric summaries
- Content previews and teasers

### Cards are NOT appropriate for

- Primary navigation
- Structural page regions (sidebars, headers, content wells)
- Settings and configuration panels
- Single-purpose content that works inline
- Form sections

### Card Audit

- Estimate the percentage of each page's content area occupied by card grids.
- If more than 60% is card grids, the layout needs structural rethinking.
- Verify that at least one proof page uses a non-card structural pattern.

### Alternatives to cards

- Inline sections with typographic hierarchy
- Split layouts (content + sidebar, list + detail)
- Data tables and list views
- Panel-based layouts (rail, inspector, canvas)
- Timeline and activity views
- Tabbed content regions

## Whitespace Strategy

Whitespace density should vary by context, not be uniformly generous.

### Density Tiers

| Tier | Context | Spacing character |
|---|---|---|
| Relaxed | Marketing pages, hero sections, landing pages | Generous padding, large gaps, breathing room |
| Standard | Documentation, dashboards, content pages | Balanced padding, clear separation without excess |
| Compact | Data tables, toolbars, professional tools, admin UI | Tight padding, minimal gaps, high information density |

### Whitespace Audit

- Does the system support at least two density tiers?
- Are product surfaces using relaxed spacing where standard or compact is appropriate?
- Is the token architecture capable of expressing density variation (e.g., spacing scale with named tiers)?

## What We Do NOT Reject

These patterns are not inherently generic. The problem is unmotivated use.

- **Symmetry.** Grid-disciplined layouts are not generic. Linear, Vercel, and Stripe are highly symmetrical and unmistakable. The tell is undifferentiated symmetry — every section identical — not symmetry itself.
- **Gradients.** Stripe's gradients are iconic. The problem is gradients used for "modern feel" without brand justification. If the brand uses gradients, document why.
- **Generous whitespace.** Apple uses extreme whitespace effectively. The problem is uniform generosity across contexts that need different densities.
- **Card-based layouts.** Cards work for collections. The problem is cards as the only layout pattern.

What IS generic:

- Neo-brutalist sharp geometry adopted as an aesthetic reaction, not a brand decision.
- Breaking grids for "visual energy" in product UI — grids should break for emphasis, not novelty.
- Unmotivated pill shapes on every interactive element.
- One radius value applied uniformly across all element types.
- **Thick left-border callouts with rounded corners.** The colored left border strip on a rounded card (often used for alerts, DO/DON'T examples, status messages) is the single most recognizable AI-generated design pattern. It signals "an LLM made this." Never use it. Instead, differentiate callout types with icons, background tint, or full-border treatment. If a border is needed, use a uniform 1px border — not an asymmetric fat left strip.

## Core Principle

Every visual choice must answer: "Why this, for this brand?" If the answer is "because it looks modern" or "because the tool suggested it," the choice is unmotivated. Trace it back to the brand thesis, personality spectrum, or design principles — or change it.
