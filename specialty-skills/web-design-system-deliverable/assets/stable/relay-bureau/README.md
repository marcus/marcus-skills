# Relay Bureau Design System

Relay Bureau is a new example package for the `web-design-system-deliverable` skill. It is intended to replace the weak “generic AI SaaS” baseline with a system that is visibly derived from recent human-made agency work.

## Thesis

Operational software with an editorial point of view.

The system is built for modern SaaS with a loose agentic-AI adjacency, but it avoids literal robot language and stock “future UI” tropes. The design thesis is:

- publish the process
- use typographic contrast before color
- keep layout structural instead of card-led
- reserve spectacle for consequential moments

## Influence map

These references were actively sampled when building the system:

- [Instrument / Work](https://www.instrument.com/work) for oversized typographic framing and chip-based navigation
- [BASIC/DEPT / Culture Manual](https://www.basicagency.com/case-studies/culture-manual-branding-web-design) for stark scale, centered metadata, and restrained spectacle
- [DIA / Flodesk](https://dia.tv/project/flodesk/) for warm type rigor, shape cadence, and product-brand continuity
- [Fantasy / Salesforce](https://fantasy.co/work/salesforce) for cinematic color pressure and staged product presentation
- [Koto / Work](https://koto.com/work) for bold color confidence and modular portfolio surfaces

## Package contents

- `index.html` — strategy, positioning, direction study, foundations, and reference map
- `components.html` — component inventory with states and accessibility notes
- `guidelines.html` — voice, composition rules, assets, responsive strategy, accessibility, and governance
- `application.html` — dark-mode application proof page
- `styles/tokens.css` — theme-aware CSS custom properties
- `styles/main.css` — shared component and layout styles
- `tokens.json` — machine-readable token source

## Notes

- Light and dark themes use the same semantic system.
- Structural containers, controls, and signature actions deliberately use different radii.
- Alerts avoid the “thick left border” AI tell called out in the skill guidance.
