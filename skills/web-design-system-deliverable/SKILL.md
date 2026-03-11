---
name: web-design-system-deliverable
description: Create agency-grade web design systems from brand strategy through production handoff. Use when the user asks for a professional design system deliverable covering brand positioning, voice and tone, design tokens, typography, motion, visual assets, responsive strategy, component specs, accessibility, application proof pages, governance, or token integration for web implementation.
---

# Web Design System Deliverable

Build a design system package that can survive handoff from strategy to design to engineering — starting with brand positioning and ending with production-ready tokens, governance, and multi-platform integration.

## Quick Start

1. Run brand strategy first: audit, positioning, personality, visual directions, design principles.
2. Define voice and tone: attributes, messaging hierarchy, CTA conventions, content rules.
3. Commit to one visual direction. Choose one spine and one signature motif.
4. Build the foundation: tokens, typography, motion, responsive strategy, visual assets direction.
5. Specify components with full state coverage, accessibility, and content rules.
6. Prove the system in a real application context — not just documenting itself.
7. Audit for differentiation: shape hierarchy, button strategy, layout structure, density tiers, brand traceability.
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
- Never use thick left-border callouts with rounded corners (the colored left strip on a rounded card). This is the most recognizable AI-generated design pattern. Use icons, background tint, or uniform thin borders to differentiate callout types instead.

## Workflow

### 1. Discover & Position

Run strategy before touching tokens or components. Produce the positioning, personality, and design principles that everything else builds on.

- Brand audit: current state, competitor landscape, whitespace opportunities, tensions to resolve.
- Positioning model: current position, target position, positioning statement.
- Personality spectrum: formal/casual, premium/accessible, bold/restrained, warm/cool, playful/serious, classic/modern.
- Design principles: 3-5 principles specific enough to settle a design argument.

Read `references/brand-strategy.md` for frameworks, templates, and phase gate criteria.

### 2. Explore Directions

Develop 2-3 distinct visual directions before committing. Each direction includes a thesis, type direction, color direction, spatial character, and signature element.

- Present a comparison table with strengths and risks per direction.
- Recommend one direction with rationale tied to positioning and audience.

Read `references/brand-strategy.md` (section 4-5) for direction templates and stakeholder alignment artifacts.

### 3. Define Voice & Tone

Voice is constant. Tone shifts by context.

- 3-4 voice attributes with boundaries and anti-patterns.
- Messaging hierarchy: tagline through microcopy through legal.
- CTA conventions: verb-first patterns, do/don't examples.
- Error and empty state copy templates.
- Naming principles and brand vocabulary.
- Content rules per component type: casing, length, punctuation, patterns.

Read `references/voice-tone.md` for the full framework.

### 4. Build the Foundation

Define the token system and supporting design infrastructure.

- Color primitives and semantic roles (light and dark themes).
- Typography: families, fluid scale, line-heights, tracking, OpenType features, pairing rationale.
- Spacing scale and layout widths.
- Corner radius, borders, elevation, and blur.
- Motion: duration scale, easing library, choreography patterns, interaction signatures, loading patterns, reduced-motion strategy.
- Responsive strategy: breakpoints, grid system, density tiers, touch targets, container queries.
- Visual assets direction: photography, illustration, iconography, graphic devices.

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

References:
- `references/component-spec-template.md` — component documentation format.
- `references/accessibility-audit.md` — ARIA patterns, keyboard nav, screen reader expectations.

### 6. Prove the System

Build application proof pages that show the system working in a real product or marketing context — not just documenting itself.

- Product dashboard, admin panel, or SaaS application page.
- Marketing landing page, pricing page, or content page.
- The proof page must use only system tokens and components.
- It must demonstrate layout, density, data display, interaction states, and responsive behavior.

This step validates that the system can actually build something real.

### 7. Audit for Differentiation

Before packaging, audit the system against `references/design-differentiation.md`. Run the shape audit (verify multiple distinct radii mapped to element types), the button audit (confirm action-level shape hierarchy), the card audit (flag layouts where card grids exceed 60% of content area), and the density check (confirm the system supports more than one whitespace tier). Verify that every major visual choice — radius, button shape, layout pattern, spacing — traces back to the brand thesis, not to tool defaults.

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

### 10. Reuse the Bundled Example

Use `assets/example-system/` as the reference implementation when the user wants a concrete starting point.

- `index.html` — system overview and foundational surfaces.
- `components.html` — UI patterns with full state coverage (disabled, loading, error, success, empty, skeleton).
- `guidelines.html` — principles, usage, and composition rules.
- `application.html` — product dashboard proof page showing the system in a real application context.
- `styles/tokens.css` — token architecture with expanded motion and info color tokens.
- `tokens.json` — design token structure in machine-readable form.

All HTML files share a 4-item navigation: Overview, Components, Guidelines, Application.

Use `scripts/scaffold_example.py <output-dir>` to copy the example deliverable into a working directory. Pass optional flags to rename the system and client placeholders.

## Output Shape

When the user asks for a fresh system, default to this response structure:

1. Brand strategy (positioning, personality, principles, chosen direction)
2. Voice & tone summary
3. Token system (color, type, spacing, motion, responsive)
4. Visual assets direction
5. Component inventory with states and accessibility
6. Application proof
7. Usage rules and governance notes
8. Deliverable files

Keep the prose concise. Put the detail into the deliverable artifacts.
