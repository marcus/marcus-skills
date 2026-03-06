# Deliverable Standard

Package the output like a client handoff, not a loose component dump.

## Deliverable Tiers

Not every project needs the full package. Scope the deliverable to the engagement.

### Tier 1 — Foundation

Tokens + components + usage guide. The minimum viable design system.

Required:
- Design thesis
- Token source of truth (CSS custom properties or JSON)
- Component gallery with interactive states
- Usage guidance
- Demo page

### Tier 2 — Brand System

Tier 1 + brand strategy + voice + visual assets + application proof.

Adds:
- Brand strategy summary (positioning, personality, principles)
- Voice & tone guide (attributes, messaging hierarchy, content rules)
- Visual assets direction (photography, illustration, iconography)
- Application proof page(s) showing the system in a real context
- Motion specification

### Tier 3 — Full Agency Package

Tier 2 + motion system + accessibility audit + governance + token integration + multi-platform handoff.

Adds:
- Full motion system (choreography, interaction signatures, loading, reduced motion)
- Accessibility audit documentation (contrast, ARIA, keyboard, screen reader, color independence)
- Governance framework (extension rules, versioning, deprecation, contribution)
- Token integration guide (Style Dictionary, Figma variables, build pipeline)
- Multi-platform token outputs (CSS, SCSS, Swift, Android XML)
- Handoff package (specs, redlines, responsive behavior, content specs)

Default to Tier 2 unless the user specifies otherwise. Upgrade to Tier 3 when the system serves multiple platforms or teams.

## Required Artifacts

### Tier 1 Minimum

1. Design thesis
2. Foundation summary (tokens, type, spacing, color)
3. Token source of truth
4. Component gallery
5. Usage guidance
6. Demo page or sample screens

### Tier 2 Additions

7. Brand strategy summary (audit, positioning, personality, direction, principles)
8. Voice & tone guide (attributes, hierarchy, CTA conventions, content rules)
9. Visual assets direction (photography, illustration, iconography, graphic devices)
10. Motion specification (durations, easing, choreography, reduced motion)
11. Application proof page(s)

### Tier 3 Additions

12. Accessibility documentation (contrast table, ARIA patterns, keyboard map, testing results)
13. Governance framework (extension rules, maturity lifecycle, versioning, deprecation)
14. Token integration guide (Style Dictionary config, Figma setup, build pipeline)
15. Multi-platform token outputs
16. Handoff checklist (token delivery, component specs, interaction specs, redlines)

## Presentation Order

Present the system in this order:

1. Why the system exists — brand positioning, audience, business context
2. Who the brand is — personality, voice, design principles
3. What visual direction was chosen — and why, with alternatives considered
4. How the foundations work — tokens, type, color, spacing, motion, responsive
5. What visual assets look like — photography, illustration, iconography direction
6. Which components are approved — full state coverage, accessibility, content rules
7. How it works in context — application proof pages
8. How teams should apply the system — usage guidance, composition rules, do/don't
9. How to maintain it — governance, versioning, contribution, token integration

## Agency-Grade Quality Bar

The deliverable should feel:

- opinionated — one clear direction, not a menu of options
- coherent — every piece traces back to the brand thesis
- implementation-aware — engineers can build from it without guessing
- presentation-ready — stakeholders can review it without a walkthrough

Strategy conviction:
- Brand positioning is specific and defensible, not generic
- Design principles have teeth — each one could settle a design argument
- The chosen direction has a clear rationale tied to audience and positioning

Voice coherence:
- Voice attributes appear consistently across all component content rules
- Messaging hierarchy is visible in the demo pages
- CTAs follow the documented conventions without exception

Motion design:
- Motion tokens exist and are used in component implementations
- Choreography patterns are documented with code
- Reduced-motion alternatives are specified, not afterthoughts

Visual asset direction:
- Photography, illustration, and iconography have documented style rules
- Asset direction traces back to brand personality
- Do/don't examples exist for each asset type

Application proof:
- At least one proof page shows the system in a real product or marketing context
- The proof page uses only system tokens and components
- It demonstrates layout, density, data display, and interaction states

Accessibility coverage:
- Contrast ratios are documented for all semantic color pairings
- ARIA patterns are specified per component
- Keyboard navigation is mapped
- Color independence is verified (no meaning conveyed by color alone)

Do not ship:

- placeholder copy that reveals the system was rushed
- duplicate tokens with overlapping meaning
- components without states
- arbitrary radii, shadows, or spacing jumps
- dark mode added as an afterthought
- motion without reduced-motion handling
- visual asset direction that says "use nice photos"
- accessibility as a bullet point instead of documented audit results
- a brand strategy that any competitor could also claim

## Acceptance Checklist

### Strategy & Voice

- [ ] Brand positioning statement is written and specific
- [ ] Personality spectrum is filled out with markers placed
- [ ] 2-3 visual directions were explored with comparison
- [ ] One direction is selected with rationale
- [ ] 3-5 design principles are defined with do/don't examples
- [ ] Voice attributes are defined with boundaries and anti-patterns
- [ ] Messaging hierarchy covers tagline through legal
- [ ] CTA conventions are documented with examples
- [ ] Error and empty state copy patterns exist
- [ ] Brand vocabulary glossary exists

### Foundation

- [ ] One clear visual thesis is present throughout
- [ ] Colors have semantic roles and accessibility coverage (AA minimum)
- [ ] Typography has a consistent scale, fluid sizing, and pairing rationale
- [ ] Spacing and radii are systematic
- [ ] Motion tokens exist: durations, easing, stagger delay
- [ ] Choreography patterns are documented (stagger, cascade, tab switch)
- [ ] Interaction signatures are specified (hover, press, focus, scroll)
- [ ] Reduced-motion strategy is a parallel design track, not disabled animation
- [ ] Responsive breakpoints are defined with rationale
- [ ] Grid system is documented with column spans per component
- [ ] Touch targets meet 44x44px minimum

### Visual Assets

- [ ] Photography direction covers subject, composition, lighting, color treatment, mood
- [ ] Illustration style is defined with line weight, color constraints, detail levels
- [ ] Iconography system specifies style, sizing tiers, stroke width, grid, color rules
- [ ] Graphic devices are documented (dividers, textures, container decorations)
- [ ] Data visualization palette is defined and colorblind-tested
- [ ] Asset governance covers formats, naming, resolution, alt text

### Components

- [ ] Component examples use the same tokens documented in the guide
- [ ] All interactive states are covered (default, hover, focus, active, disabled, loading, error, success, empty, skeleton)
- [ ] Content rules exist per component (casing, length, punctuation)
- [ ] ARIA patterns are documented per component
- [ ] Keyboard navigation is mapped per interactive pattern
- [ ] Screen reader announcements are specified for state changes
- [ ] Responsive behavior is documented per component

### Application Proof

- [ ] At least one proof page exists (product dashboard, marketing page, or similar)
- [ ] Proof page uses only system tokens and components
- [ ] Proof page demonstrates real content, not lorem ipsum
- [ ] Layout, density, and interaction states are exercised

### Deliverable Package

- [ ] The demo page showcases both brand expression and UI utility
- [ ] Engineers can implement the system without guessing hidden rules
- [ ] Token source of truth is provided (CSS and/or JSON)
- [ ] Light and dark themes are both complete
- [ ] Governance framework exists (extension rules, versioning, deprecation)
- [ ] Token integration path is documented (Style Dictionary, Figma, build pipeline)
- [ ] Handoff checklist is complete (specs, redlines, responsive, content)
