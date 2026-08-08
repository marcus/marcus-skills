---
name: web-design-system-deliverable
description: Create agency-grade web design systems from brand strategy through production handoff. Use when the user asks for a professional design system deliverable covering brand positioning, voice and tone, design tokens, typography, motion, visual assets, responsive strategy, component specs, accessibility, application proof pages, governance, or token integration for web implementation.
---

# Web Design System Deliverable

Build a design system package that can survive handoff from strategy to design to engineering — starting with brand positioning and ending with production-ready tokens, governance, and multi-platform integration.

## Design Intelligence

This section encodes specific patterns and values observed on production sites from BASIC/DEPT, Instrument, Huge, AREA 17, Pentagram, Collins, Mother Design, Stripe, Linear, Vercel, Raycast, Arc, and Craft. Every recommendation below traces back to what real creative directors actually ship — not what tools default to.

### Typography: what agencies actually do

**Font selection.** Top agencies use premium, purchased typefaces — not free Google Fonts, not system defaults. Scto Grotesk A (BASIC), Monument Grotesk (Huge), Suisse Intl (AREA 17), Sohne (Stripe), Geist (Vercel). When a Google Font is the only option, treat it as a production stand-in and note the intended replacement. Never default to Inter + Inter. If using Inter, pair it with a serif or use its variable axis to set non-standard weights.

**Serif/sans tension.** The fastest way to break the AI-generated look is a serif/sans pairing where the serif carries display text and the sans carries body. Collins pairs Portrait Text (serif headlines) with Graphik (sans body). Craft pairs Untitled Serif (headlines) with Graphik (body). This creates editorial tension that AI almost never generates.

**Weight 400 for headings.** Craft, Instrument, and BASIC all use regular weight (400) for headings. Hierarchy comes through size, serif treatment, or tracking — not boldness. AI defaults to weight 600-700 for headings. Fight this instinct. Reserve 500+ for subtle emphasis: nav active states, table headers, badge text.

**Non-standard variable font weights.** Linear uses 510 and 590 instead of 500 and 600. This is subtle optical refinement. When using variable fonts, consider weights like 420, 450, 480, 520, 550 — values that feel tuned rather than picked from a dropdown.

**Negative letter-spacing on display, positive on small text.** Every agency uses aggressive negative tracking on headlines: -0.025em to -0.04em on display text. At small sizes (13-14px), tracking flips to positive (+0.01em to +0.025em) for legibility. This size-dependent tracking is a signature of professional typography that AI consistently misses. Implement it in the token system with named steps:

```
tracking-tight:  -0.025em   (display, 48px+)
tracking-snug:   -0.015em   (headings, 24-48px)
tracking-normal:  0          (body, 16-20px)
tracking-wide:   +0.01em    (small body, 14px)
tracking-wider:  +0.025em   (captions, labels, 12-13px)
```

**Line-height varies dramatically by role.** AI defaults to 1.5 everywhere. Agencies use 1.0-1.1 for display text (lines nearly touching — editorial tension), 1.25 for subheadings, 1.5-1.6 for body, and 1.0 for labels/badges. Huge uses 0.92 on display text (lines overlap). Pentagram uses 1.0. This variation is a design decision, not an accident. Encode it:

```
leading-none:     1.0    (display, hero, badges)
leading-tight:    1.1    (large headings)
leading-snug:     1.25   (subheadings, cards)
leading-normal:   1.5    (body default)
leading-relaxed:  1.6    (body large, editorial)
leading-loose:    1.7    (long-form reading)
```

**Type scale: flatten it.** Pentagram's H1 is 19px and body is 16px — a 3px difference. Hierarchy through weight and color, not size jumps. AI generates dramatic scales (16→24→36→48→64). Real systems are flatter. Not every system needs Pentagram-level flatness, but consider whether the jump between each level is earned. The scale should serve the content density, not demonstrate range.

**Body size: slightly larger than 16px.** BASIC, Huge, AREA 17, and Craft all use 17-19px body text. The web default of 16px is a holdover from lower-resolution screens. Use 17px as the baseline.

### Color: what agencies actually do

**No pure black. No pure white.** Nobody uses #000000 for text or #ffffff for backgrounds. Collins uses #140700 (warm brown-black) and #f8f8f7 (warm off-white). Stripe uses #0a2540 (navy-black). AREA 17 uses #1a1a1a. Arc uses #030302 and #fffcec (warm cream). Every color has a temperature decision — warm or cool, never neutral-by-default. Choose a temperature and apply it to every neutral in the system.

**One accent color — and not purple.** Pentagram uses zero accent colors. Collins uses one (#ff7600 orange). Stripe uses one (#635bff purple). AREA 17 uses zero. Raycast uses two (pink + purple) but that is the upper bound. AI generates 5-color accent palettes. Resist this. One accent color, used for: primary CTAs, active states, focus rings, links. Everything else is neutral.

**Avoid purple as the accent.** Purple (#6c5ce7, #7c3aed, #8b5cf6, #6366f1 and their variants) is currently the single most over-represented accent color in AI-generated design systems. It reads as "an AI chose this." Unless the brand has a specific, documented reason for purple, choose an alternative: warm copper/burnt sienna, deep teal, muted olive, ochre, dark navy, or warm orange. Collins' #ff7600 and the Theorem example's warm copper (#b87a4b) are both strong alternatives that trace back to warm neutral palettes.

**Functional colors are muted.** Success, warning, danger, info — these exist but are restrained. They appear only in context (status badges, form validation, alerts). They never dominate a page. Make them 20-30% less saturated than a typical AI-generated palette.

**Borders at 5-8% opacity.** Linear uses `rgba(255,255,255,0.05)` on dark surfaces — barely visible but structurally essential. Light surfaces use `rgba(0,0,0,0.06-0.08)`. These ultra-subtle borders define space without drawing attention. AI defaults to visible borders (#e5e5e5 or similar). Use opacity-based borders that adapt to the surface they're on.

**Blue-tinted shadows.** Stripe tints all shadows with brand navy: `rgba(50,50,93,0.12)` instead of `rgba(0,0,0,0.12)`. This simulates real ambient light (blue sky) and adds warmth. It is a subtle detail that separates premium from default. Implement multi-layer shadows like Collins: contact shadow (tight, dark) + mid shadow (medium, lighter) + ambient shadow (wide, barely visible).

**Dark theme: true black bg, barely-off-black surfaces.** Linear uses #000000 background with #0f1011 card surfaces — a 15-unit difference in RGB. The text is warm white (#f7f8f8 or #e8e5df), never pure #ffffff. Borders on dark surfaces are rgba(255,255,255,0.05-0.06). Implement dark theme by re-pointing semantic tokens, not rewriting component CSS.

### Spacing: what agencies actually do

**4px base grid, religiously.** Every observed site uses multiples of 4: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128. No arbitrary values.

**96-128px between page sections.** BASIC uses 168px. Pentagram uses 96px. This is 6-8× the body line-height. AI generates 48-64px section gaps. Double it. The generous vertical rhythm is the single biggest visual signal of premium design.

**24px card padding.** This is the consensus across Linear, Vercel, Stripe. Not 16px (too tight), not 32px (too loose for standard density). 24px is the sweet spot for card interiors.

**Asymmetric spacing.** Linear uses 0px top / 28px bottom card padding. Stripe uses 3px top / 6px bottom CTA padding. Pentagram uses 96px vertical / 12px horizontal grid gaps (8:1 ratio). Mechanical symmetry is an AI tell. Intentional asymmetry is a design decision.

### Shape: what agencies actually do

**Sharp containers.** AREA 17, BASIC, and Pentagram use 0px border-radius on structural containers. Cards, panels, page sections — all sharp. This signals precision and architecture. AI rounds everything to 8-12px.

**Moderate controls.** Inputs and secondary buttons use 4-6px radius. This is functional softening without decorative intent.

**Pill for primary CTA only.** The pill shape (9999px radius) is a signature element reserved for the highest-priority action. Not for secondary buttons, not for every interactive element. Stripe and Craft use pill CTAs with sharp or moderate secondaries. This creates action-level hierarchy through shape, not just color.

**Multiple distinct radii.** A mature system has at least 4 radius values mapped to element types:

```
radius-none:  0        (structural: page regions, panels, code blocks, tables)
radius-sm:    3-4px    (data-dense: table cells, toolbar items, tags)
radius-md:    6px      (interactive: inputs, secondary buttons, badges)
radius-lg:    8px      (elevated: cards, modals, popovers)
radius-xl:    12px     (feature: hero cards, large panels)
radius-pill:  9999px   (signature: primary CTA, chips)
```

### Motion: what agencies actually do

**Custom cubic-bezier curves, never presets.** Every agency uses custom easing. Never `ease`, `ease-in-out`, or `linear`. Specific curves from production:

```
ease-out:     cubic-bezier(0.22, 0.61, 0.36, 1)     — general UI
ease-in-out:  cubic-bezier(0.45, 0.05, 0.55, 0.95)  — symmetric transitions
ease-spring:  cubic-bezier(0.34, 1.56, 0.64, 1)     — playful overshoot
ease-smooth:  cubic-bezier(0.52, 0.01, 0.26, 1)     — smooth scroll, page transitions
```

AREA 17 uses `cubic-bezier(0.36, 0, 0.66, 1)`. Collins uses `cubic-bezier(0.5, 0.3, 0, 1)`. Pentagram uses `cubic-bezier(0.59, 0.01, 0.28, 1)`. The specific curve doesn't matter as much as the fact that it's custom and intentional.

**150-200ms for hover.** This is the universal sweet spot. Linear does 150ms, Vercel 200ms, Raycast 150-200ms. Craft is the outlier at 300ms, matching its slower, more literary brand.

**Scale 1.015 on hover, 0.98 on press.** Stripe hovers cards at scale(1.018) — so subtle you feel it but don't see it. Collins presses buttons at scale(0.98). AI defaults to scale(1.05) which is too visible and feels toylike.

**Stagger at 60ms intervals.** Collins staggers card reveals at 0.07s (70ms). The motion reference uses 60ms. This creates choreographed entrance without feeling slow.

**85-second ambient animations.** Stripe runs background gradient animations at 85+ seconds. Slow enough to never register as motion, but preventing the page from feeling static. Consider this for hero sections.

### Layout: what agencies actually do

**Not everything is a card.** Cards are appropriate for collections of similar items. They are NOT appropriate for: navigation, settings panels, form sections, stats/metrics, single-purpose content. Use inline sections with typographic hierarchy, split layouts (30/70, 40/60), data tables, panel-based layouts, timeline views, or tabbed regions instead. If more than 60% of a page is card grids, the layout needs structural rethinking.

**Asymmetric column splits.** Collins uses a 30/70 split for case study layouts (meta: columns 1-3, story: columns 4-10). This is classic editorial asymmetry. For dashboards, consider a 240px sidebar + fluid main content area. For content pages, offset the primary content with a narrow secondary column.

**Numbered sections for structure.** AREA 17 uses "01", "02", "03" as editorial section markers. This creates visual hierarchy and reading order without relying on size or weight.

**Stats as inline strips, not card grids.** Metrics (active agents: 47, error rate: 0.3%) should be an inline row with thin vertical dividers — not individual cards with shadows. This is the compact, information-dense pattern that tools like Linear use.

### Anti-patterns: what to never generate

These are the most recognizable AI-generated design patterns. If you catch yourself producing any of them, stop and correct.

1. **Thick left-border callouts with rounded corners.** The colored left strip on a rounded card. The single most common AI tell. Use icon + background tint + uniform thin border instead.

2. **Bold headings (weight 600-700).** Real agencies use weight 400 for headings. Hierarchy comes from size, serif treatment, tracking, or color — not boldness.

3. **Pure black (#000) and pure white (#fff) for text/backgrounds.** Every production site uses warm or cool off-values. #1a1714, #f8f7f4, #140700, #e8e5df — never the defaults.

4. **5-color accent palettes.** One accent color. Maybe two. Never five "brand colors" with teal, coral, amber, indigo, and emerald.

5. **Purple accent colors (#6c5ce7, #7c3aed, #8b5cf6, etc.).** Purple is currently AI's favorite color. It appears in the vast majority of AI-generated design systems. Unless the brand specifically requires purple, choose warm copper, deep teal, muted olive, ochre, or warm orange.

6. **Uniform border-radius on all elements.** If every element has 8px radius, there is no shape hierarchy. Structural containers should be sharp. Controls moderate. Primary CTA pill.

7. **Default easing (ease, ease-in-out).** Always use custom cubic-bezier curves.

8. **Symmetric spacing everywhere.** Real systems have asymmetric padding (0px top / 28px bottom), asymmetric grid gaps (96px vertical / 12px horizontal), asymmetric column splits (30/70).

9. **Card grids for everything.** Stats, settings, form sections, navigation — these should not be cards. Reserve cards for collections of similar items.

10. **Centered hero sections with gradient backgrounds.** Use asymmetric hero layouts. Put the title on one side, description on the other. No gradient backgrounds unless the brand specifically calls for them with a documented rationale.

11. **Scale(1.05) hover effects.** This is too visible and feels toylike. Use scale(1.015) — felt but not seen.

12. **Generous whitespace uniformly applied.** Whitespace should vary by context: relaxed for marketing, standard for dashboards, compact for data tables. A system with one density tier is incomplete.

13. **Lorem ipsum or generic placeholder copy.** Write real, contextual content. Table data about "agent runs," form fields for "workflow name," alerts about "deployment status." Every piece of text should feel like it belongs in the product.

14. **Saturated colored pills for every badge/tag.** Green pill "Active," red pill "Error," blue pill "Info" — the traffic-light pill palette is the single most AI-generated pattern for status indication. Use typography-only tags (different weight/case, no container), dot indicators (7px colored circle + text), or monochrome icon+border badges instead. Reserve colored pills for one specific use case at most.

15. **Colored-container alerts with rounded corners and icons.** Blue background + blue border + info icon + rounded corners is the default AI alert. Use bare text (just colored text, no container), left-border-only accent (2px left line), or top-border accent (3px colored top edge on a neutral card) instead. Alerts should be quiet unless they're critical.

16. **Fully bordered inputs at rest.** A visible border on every input in every state is the form equivalent of putting everything in cards. Use invisible inputs (border appears only on hover/focus), bottom-line-only inputs (underline animates from center on focus), or luxury inputs (sharp corners, serif labels, generous padding). The input should be quiet at rest and reveal itself on interaction.

17. **Zebra-striped tables with visible borders and colored status pills.** This combination — alternating row backgrounds, 1px borders on every cell, green/red/yellow pills in the status column — is the canonical AI table. Use borderless tables (alignment + whitespace + tabular-nums, no dividers), editorial tables (serif headers, monospace numbers, strong top rule only), or minimal tables (single bottom-border per row at 6% opacity). Right-align numeric columns. Use `font-variant-numeric: tabular-nums` on all number columns.

18. **Filled rounded-rectangle buttons for every action.** A blue (or purple) filled rectangle with 8px radius and white text is the AI default for all buttons. Instead, use shape hierarchy: text+arrow buttons (no container — just text and a → glyph) for navigation, editorial buttons (serif italic, underline on hover) for content actions, Swiss minimal (no border/fill, scale+shadow on hover) for secondary actions. Reserve filled buttons for the single highest-priority action on a page. Ghost/outline should be more common than filled.

## Quick Start

1. Run brand strategy first: audit, positioning, personality, visual directions, design principles.
2. Define voice and tone: attributes, messaging hierarchy, CTA conventions, content rules.
3. Commit to one visual direction. Choose one spine and one signature motif.
4. Build the foundation: tokens, typography, motion, responsive strategy, visual assets direction. Apply the design intelligence section above to every value you choose.
5. Specify components with full state coverage, accessibility, and content rules.
6. Prove the system in a real application context — not just documenting itself.
7. Audit for differentiation: run every token value against the anti-patterns list. If anything matches an anti-pattern, change it.
8. Package the deliverable: overview, components, guidelines, application proof, token source, implementation-ready assets.
9. Prepare for handoff: token integration pipeline, Figma setup, governance framework.

## Working Standard

Treat the output like a rebrand deliverable from a top-tier agency.

- Start with strategy. Brand positioning, personality, and design principles must exist before any visual work begins.
- Define voice and tone as a system-level concern. Every component has content rules.
- Make deliberate aesthetic choices. Typography, proportion, and spacing must carry the brand before color does.
- Prefer semantic roles over hard-coded values inside components.
- Ship both rationale and artifacts. The system should explain how to use the pieces, not only show them.
- Design states completely: default, hover, focus-visible, active, disabled, loading, success, warning, danger, error, empty, and skeleton where relevant.
- Specify motion as a design material: choreography, interaction signatures, loading patterns, and reduced-motion alternatives.
- Direct visual assets: photography, illustration, iconography, and graphic devices with the same rigor as color and type.
- Keep accessibility non-negotiable: contrast documentation, ARIA patterns, keyboard navigation, screen reader expectations, color independence, and reduced-motion audit.
- Prove the system works in a real application context — a product dashboard, a marketing landing page, or both.
- Avoid generic UI filler. Every surface should have a reason to exist.

## Workflow

### 1. Discover & Position

Run strategy before touching tokens or components. Produce the positioning, personality, and design principles that everything else builds on.

- Brand audit: current state, competitor landscape, whitespace opportunities, tensions to resolve.
- Positioning model: current position, target position, positioning statement.
- Personality spectrum: formal/casual, premium/accessible, bold/restrained, warm/cool, playful/serious, classic/modern.
- Design principles: 3-5 principles specific enough to settle a design argument. Each principle should have a "this, not that" framing.

Read `references/brand-strategy.md` for frameworks, templates, and phase gate criteria.

### 2. Explore Directions

Develop 2-3 distinct visual directions before committing. Each direction includes a thesis, type direction, color direction, spatial character, and signature element.

- Present a comparison table with strengths and risks per direction.
- Recommend one direction with rationale tied to positioning and audience.
- For each direction, specify: typeface(s), color temperature, radius strategy, spacing density, and one signature visual move.

Read `references/brand-strategy.md` (section 4-5) for direction templates and stakeholder alignment artifacts.

### 3. Define Voice & Tone

Voice is constant. Tone shifts by context.

- 3-4 voice attributes with boundaries and anti-patterns.
- Messaging hierarchy: tagline through microcopy through legal.
- CTA conventions: verb-first, specific ("Deploy workflow" not "Get started"). Action verbs, not generic verbs.
- Error and empty state copy templates. Errors are calm and specific. Empty states are encouraging, not apologetic.
- Naming principles and brand vocabulary.
- Content rules per component type: casing, length, punctuation, patterns.

Read `references/voice-tone.md` for the full framework.

### 4. Build the Foundation

Define the token system and supporting design infrastructure. Apply the design intelligence section to every value.

- **Color**: warm off-values for all neutrals (no pure black/white), one accent color, muted functional colors, opacity-based borders, blue-tinted shadows.
- **Typography**: serif/sans pairing (or single premium typeface), weight 400 headings, non-standard variable weights, size-dependent tracking, varied line-heights by role, 17px+ body size.
- **Spacing**: 4px base grid, 96-128px section spacing, 24px card padding, intentional asymmetric spacing.
- **Radius**: shape hierarchy — sharp structural, moderate controls, pill signature CTA.
- **Motion**: custom cubic-bezier curves, 150-200ms hover, 280ms transitions, scale(1.015) hover, 60ms stagger.
- **Responsive strategy**: breakpoints, grid system, density tiers (relaxed/standard/compact), touch targets, container queries.
- **Visual assets direction**: photography, illustration, iconography, graphic devices.

References:
- `references/token-architecture.md` — token naming and structure.
- `references/typography-specimens.md` — pairing, fluid type, OpenType, specimens.
- `references/motion-system.md` — choreography, interaction signatures, loading, reduced motion.
- `references/responsive-strategy.md` — breakpoints, grid, density, container queries.
- `references/visual-assets.md` — photography, illustration, iconography, graphic devices.

### 5. Specify Components

Document components with intent before styling details. Full state coverage is non-negotiable.

Minimum inventory: buttons, links, badges, navigation, cards, form fields, tables, alerts, empty states, modals/drawers/popovers, skeleton loading.

For each component, capture:

- Purpose and misuse boundaries
- Anatomy and variants
- All interactive states (default, hover, focus, active, disabled, loading, error, success, empty, skeleton)
- Spacing and layout rules
- Content rules (from voice & tone)
- Accessibility: ARIA pattern, keyboard behavior, screen reader expectations
- Motion behavior
- Responsive adaptation
- Implementation notes

**Component-specific design intelligence:**

- **Buttons**: Use a shape/chrome hierarchy — not just color — to distinguish action levels. Five distinct tiers, matched to context:
  - **Primary** (1 per page max): pill + accent fill + weight 450. The only button that gets a colored container.
  - **Secondary**: 6px radius + 1px border + transparent bg. Or Swiss minimal: no border, no fill, just text with generous padding — hover lifts via scale(1.04) + subtle shadow.
  - **Ghost/navigation**: text + arrow glyph (→ or ›), no container at all. The arrow gap widens on hover. This replaces button chrome as the primary affordance at Apple, Notion, and Vercel.
  - **Editorial**: serif italic text, no container. Underline grows from center on hover. For content-heavy contexts.
  - **Luxury/fashion**: black fill, ALL-CAPS, 0.2em letter-spacing, sharp corners (radius 0). For high-fashion or editorial brand directions.
  - **Neo-brutalist** (when brand calls for it): 3px black border, 4px 4px hard offset shadow (zero blur), sharp corners. Hover translates button into its shadow (press-down effect).
  - **Danger**: moderate radius + danger fill. Only for destructive actions.
  - Shape hierarchy is non-negotiable — primary and secondary must look visually distinct beyond color. The highest-end sites use the fewest filled buttons. Ghost/text-only should be the most common button type, not filled.

- **Badges/tags/status indicators**: Eliminate colored pills as the default. Three premium alternatives:
  - **Typography-only** (FT pattern): the tag is just a different typeface, weight, or case — no container, no pill, no background. A sans-serif uppercase label at 0.7rem/weight 600 next to a serif headline creates editorial structure. The tag functions as a compositional element creating whitespace, not as a colored blob.
  - **Dot-only**: a 7px colored circle adjacent to text. No container. Used by Linear for issue status. Conveys state with minimal visual weight.
  - **Monochrome icon+border**: 1px border badge with an SVG icon (checkmark, X, clock, dash) and text. Status is communicated through icon shape, not through traffic-light colors. Essential for accessibility and print contexts.
  - Reserve colored pills for at most one specific use case in the system. If using them, limit to 3-4 colors max, at 15-20% opacity backgrounds (not fully saturated).

- **Alerts/notifications**: Kill the colored-container-with-icon default. Three tiers of alert severity mapped to visual weight:
  - **Bare text** (low severity): just colored text, no container. "Changes saved." in success color. Or a left-border variant: 2px left line as the only accent, text in normal color.
  - **Top-border accent** (medium severity, Carbon pattern): neutral card with a 3px colored top border. The rest of the card is quiet. Bold title + normal body text.
  - **Full container** (high severity only): reserve colored backgrounds for genuinely critical/blocking alerts. Even then, use muted tints (15-20% opacity of the status color), not saturated backgrounds.
  - Error messages should use passive voice ("The ZIP code format isn't recognized" not "You entered an invalid ZIP code"). Validate on blur, never on keystroke. Muted red tones (#b91c1c), not bright #FF0000.

- **Form inputs**: Inputs should be quiet at rest and reveal themselves on interaction. Three premium approaches:
  - **Invisible input** (Notion pattern): completely transparent at rest — no border, no background. Hover reveals a subtle border. Focus brings solid border + background. The content is the only indicator. Best for inline editing, settings panels, and content-focused interfaces.
  - **Bottom-line only**: no container borders, just a bottom underline. On focus, a 2px accent line grows from the center outward (transition on width + left). Clean, editorial feel. Best for login forms and simple data entry.
  - **Luxury checkout**: sharp corners (border-radius: 0), generous padding (16px 20px), serif labels in uppercase with wide tracking. Focus darkens the border to full black. Best for high-fashion or editorial brand directions.
  - **Proportions**: generic inputs use padding 8px 12px at 36px height. Premium inputs use 12-16px vertical / 16-20px horizontal at 40-48px height with 15-16px font. The extra padding is a primary signal of quality.
  - Use `:focus-visible` (not `:focus`) so mouse users don't see focus rings. Minimum 16px font on mobile to prevent iOS auto-zoom.

- **Tables**: Strip chrome, let data breathe. Two premium table directions:
  - **Borderless**: no dividers, no outer border, no zebra stripes. Alignment, generous whitespace, and `font-variant-numeric: tabular-nums` do all the structural work. Hover provides wayfinding (background rgba(0,0,0,0.03)). Headers are muted (50% opacity, weight 500, small uppercase).
  - **Editorial**: serif italic headers, monospace numbers (JetBrains Mono or similar), a strong 2px top rule on the table, 1px bottom borders on rows. Generous row padding (14px vertical). Reads like a data table in an annual report.
  - **Universal rules**: right-align quantitative numbers (amounts, percentages). Left-align qualitative numbers (dates, IDs). Use `font-variant-numeric: tabular-nums` on ALL number columns so digits align. Headers must match their column's alignment. Never center-align text columns. Zebra stripes compound with hover/selected/disabled states — use hover highlighting instead. Row heights: condensed 40px, regular 48px, relaxed 56px.

- **Cards**: structural cards = 0 radius + border-subtle + no shadow. Elevated cards = 8px radius + shadow-sm. Interactive cards = elevated + hover scale(1.015) + shadow-md on hover.
- **Navigation**: weight 400, 14px, no text-transform. Active state uses accent color or underline, not a background pill. 4-6 items maximum.
- **Empty states**: serif heading (weight 400), body description, single primary CTA. Simple illustration or icon, not an elaborate graphic.

References:
- `references/component-spec-template.md` — component documentation format.
- `references/accessibility-audit.md` — ARIA patterns, keyboard nav, screen reader expectations.

### 6. Prove the System

Build application proof pages that show the system working in a real product or marketing context — not just documenting itself.

- Product dashboard, admin panel, or SaaS application page.
- Marketing landing page, pricing page, or content page.
- The proof page must use only system tokens and components.
- It must demonstrate layout, density, data display, interaction states, and responsive behavior.
- Use real, contextual content throughout — realistic data, agent names, workflow titles, timestamps.

**Application proof patterns** (from the design intelligence research):
- App shell with sidebar navigation (240px, sharp edges) + main content area
- Stats as inline strip with thin vertical dividers, not individual cards
- Data tables with compact density, realistic content, status badges
- Split layouts (40/60) for mixed content areas
- Numbered rankings (01, 02, 03) for editorial structure
- Alerts with icon + tint pattern

### 7. Audit for Differentiation

Before packaging, run the anti-patterns checklist from the design intelligence section. For every item on the list, verify the system does NOT match the anti-pattern. Then run the positive checks:

- Shape language has intentional hierarchy (at least 4 distinct radius values mapped to element types)
- Button shapes differentiate by action level (primary pill vs. secondary sharp vs. ghost text)
- Page layouts include structural elements beyond card grids (split layouts, inline sections, tables, panels)
- Whitespace varies by context (marketing density vs. product density vs. data density)
- Typography uses negative tracking on display, positive on small text
- Headings are weight 400 (or documented override with brand rationale)
- No pure black or pure white in the color system
- Custom cubic-bezier curves in the motion system
- Border opacity is below 10% (not solid visible colors)
- Section spacing is 96px+ (not 48-64px)

Read `references/design-differentiation.md` for the full shape, button, card, and density audit frameworks.

### 8. Package the Deliverable

Deliver a system that is legible to designers, engineers, and stakeholders.

Full package:

- Overview page (brand thesis, personality, design principles, visual direction)
- Components gallery (full state coverage, interactive examples)
- Usage guide (principles, composition rules, do/don't)
- Application proof page(s)
- Brand strategy summary
- Voice & tone guide
- Motion specification
- Visual assets direction
- Accessibility documentation
- Token source of truth (CSS custom properties and/or JSON)

Read `references/deliverable-standard.md` before finalizing output.

### 9. Prepare for Handoff

Bridge the gap between the design system and production implementation.

- Token integration: Style Dictionary config, platform outputs (CSS, SCSS, Swift, Android XML).
- Figma setup: variable collections, naming conventions, mode structure.
- Governance framework: extension rules, component maturity lifecycle, versioning strategy, deprecation protocol, contribution guidelines.
- Handoff checklist: token delivery, component specs, interaction specs, redline notes, responsive behavior, content specs.

References:
- `references/token-integration.md` — Style Dictionary, Figma variables, build pipeline, multi-platform.
- `references/governance.md` — extension rules, versioning, deprecation, contribution.

### 10. Reuse the Bundled Examples

Use the bundled examples as reference implementations when the user wants a concrete starting point. Examples are organized by quality tier under `assets/`.

**Featured** (`assets/featured/`) — production-grade references:
- `theorem-system/` — the strongest current reference. Editorial serif/sans tension, warm copper accent (#b87a4b), warm off-values, agency-influenced design intelligence, dark/light themes, full application proof with sidebar dashboard.
- `folio-system/` — polished, complete system with strong design coherence.

**Stable** (`assets/stable/`) — solid implementations:
- `relay-bureau/` — well-structured system, reliable patterns.
- `parklet-system/` — clean, cohesive system.

**Developing** (`assets/developing/`) — functional but still maturing:
- `nerve-system/` — working system with room for refinement.
- `meridian-system/` — baseline example with simpler implementation patterns.

**Experimental** (`assets/experimental/`) — early-stage or rough:
- `northstar-system/` — least polished, exploratory.

Each example contains:
- `index.html` — system overview and foundational surfaces.
- `components.html` — UI patterns with full state coverage (disabled, loading, error, success, empty, skeleton).
- `guidelines.html` — principles, usage, and composition rules.
- `application.html` — product dashboard proof page showing the system in a real application context.
- `styles/tokens.css` — token architecture.
- `styles/main.css` — component and utility styles.
- `tokens.json` — design token structure in machine-readable form.

All HTML files share a 4-item navigation: Overview, Components, Guidelines, Application.

Use `scripts/scaffold_example.py <output-dir>` to copy the meridian example into a working directory. Pass optional flags to rename the system and client placeholders.

## Output Shape

When the user asks for a fresh system, default to this response structure:

1. Brand strategy (positioning, personality, principles, chosen direction)
2. Voice & tone summary
3. Token system (color, type, spacing, motion, responsive) — every value justified against the design intelligence section
4. Visual assets direction
5. Component inventory with states and accessibility
6. Application proof
7. Usage rules and governance notes
8. Deliverable files

Keep the prose concise. Put the detail into the deliverable artifacts.
