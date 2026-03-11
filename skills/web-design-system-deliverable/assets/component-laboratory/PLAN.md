# Component Laboratory — Plan

## Goal
Create a standalone HTML exploration page showing ~12 different style approaches
for "boring" components (buttons, badges, alerts, forms, tables) that go beyond
AI defaults. Separate from the Folio system.

## Status
- [x] Research: Forms/inputs (saved to forms-research.md)
- [x] Research: Tables/data display (saved to tables-research.md)
- [x] Research: Badges/tags/alerts (saved to badges-alerts-research.md)
- [x] Research: Counterintuitive UI patterns (saved to counterintuitive-research.md)
- [ ] Research: Buttons (agent a21fd9a7c66c76ddf still running — check output file)
- [ ] Build: Single HTML page with ~12 style explorations

## Design Directions to Explore (from research)

### Buttons
1. **Text-only / arrow-only** — Collins, AREA 17 pattern: no container, just text + arrow glyph
2. **Swiss minimal** — just text, generous padding, no border, no fill, scale transform on hover
3. **Neo-brutalist** — thick 3-4px black border, offset shadow, no blur
4. **Editorial** — serif text, underline that animates on hover, no container
5. **Luxury/fashion** — Balenciaga: black fill, ALL-CAPS, aggressive tracking, sharp corners

### Badges/Tags
6. **Typography-only** — FT pattern: tag is just a different typeface/weight, no container
7. **Dot-only** — 6-8px colored dot, no text container
8. **Monochrome** — shape + icon only, no color differentiation

### Alerts
9. **Bare text** — no container at all, just colored text or a single accent line
10. **Top-border accent** — Carbon pattern: 3px top border, neutral card body

### Forms
11. **Invisible input** — Notion pattern: no border at rest, appears on focus
12. **Bottom-line only** — underline that animates from center on focus
13. **Luxury checkout** — generous padding, sharp corners, serif labels

### Tables
14. **Borderless** — no dividers, alignment + whitespace + tabular-nums do the work
15. **Editorial** — serif headers, generous spacing, minimal chrome

## Key Research Insights to Incorporate

- `font-variant-numeric: tabular-nums` for all number columns
- Zebra stripes increasingly discouraged (compounding states problem)
- Japanese density-as-trust finding (counterpoint to minimalism)
- Sonner toast stacking physics (CSS transitions, not keyframes)
- Collins hover: scale(1.04) + shadow, no color change
- Linear: LCH color, only 3 theme inputs (base, accent, contrast)
- FT: tags as compositional elements creating whitespace, not overlays
- Buttons agent output file: /private/tmp/claude-501/-Users-marcusvorwaller-code-marcus-skills/tasks/a21fd9a7c66c76ddf.output
