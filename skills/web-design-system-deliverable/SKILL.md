---
name: web-design-system-deliverable
description: Create or refine client-ready web design systems for rebrands, product redesigns, or new web properties. Use when the user asks for a professional design system deliverable with design tokens, semantic color roles, typography, spacing, component specs, usage guidance, accessibility rules, a demo page, or an example component library for web implementation.
---

# Web Design System Deliverable

Build a design system package that can survive handoff from strategy to design to engineering.

## Quick Start

1. Capture the brand posture: audience, market position, rebrand goal, brand adjectives, constraints, and whether the system is marketing-heavy, product-heavy, or shared.
2. Commit to one visual thesis. Choose one spine and one signature motif. Do not mix unrelated aesthetics.
3. Define the foundation first: tokens, theme roles, typography, spacing, radii, shadows, motion, grid, and interaction states.
4. Document components only after the semantic token layer is stable.
5. Package the output as a client deliverable: overview/demo page, components page, usage guidance, token source, and implementation-ready CSS variables or JSON.

## Working Standard

Treat the output like a rebrand deliverable from a top-tier agency.

- Make deliberate aesthetic choices. Typography, proportion, and spacing must carry the brand before color does.
- Prefer semantic roles over hard-coded values inside components.
- Ship both rationale and artifacts. The system should explain how to use the pieces, not only show them.
- Design states completely: default, hover, focus-visible, active, disabled, loading, success, warning, and danger where relevant.
- Keep accessibility non-negotiable: visible focus, keyboard reachability, color contrast, reduced-motion behavior, and clear form errors.
- Avoid generic UI filler. Every surface should have a reason to exist.

## Workflow

### 1. Frame the System

Start with a short design thesis containing:

- the audience and what they need to trust
- the business posture the brand should project
- the visual spine: typography-first minimal, editorial craft, product precision, or bold-but-controlled
- the signature motif that appears across pages and components

If the user gives little direction, assume a restrained, premium, typography-led system and say so.

### 2. Build the Foundation

Always define these token groups:

- color primitives and semantic roles
- typography families, scale, line-heights, tracking, and numeric styles
- spacing scale and layout widths
- corner radius, borders, elevation, and blur if used
- motion durations, easing curves, and reduced-motion rules
- focus ring, interactive states, and status colors

Read `references/token-architecture.md` when naming or structuring tokens.

### 3. Specify Components

Document components with intent before styling details.

Minimum inventory:

- buttons
- links
- badges and status pills
- navigation
- cards and content modules
- form fields and validation states
- tables or list rows
- alerts and empty states
- modals, drawers, or popovers when the product needs overlays

For each component, capture:

- purpose and misuse boundaries
- anatomy
- variants and sizes
- interactive states
- spacing and layout rules
- content rules
- accessibility requirements
- implementation notes

Read `references/component-spec-template.md` when producing component docs.

### 4. Package the Deliverable

Deliver a system that is legible to designers, engineers, and stakeholders.

Minimum package:

- overview/demo page
- components gallery
- usage guide
- token source of truth
- implementation-ready CSS custom properties or JSON tokens

Read `references/deliverable-standard.md` before finalizing output.

### 5. Reuse the Bundled Example

Use `assets/example-system/` as the reference implementation when the user wants a concrete starting point.

- `index.html` shows the system overview and foundational surfaces.
- `components.html` shows example UI patterns and states.
- `guidelines.html` explains principles, usage, and composition rules.
- `styles/tokens.css` contains the token architecture.
- `tokens.json` mirrors the design token structure in machine-readable form.

Use `scripts/scaffold_example.py <output-dir>` to copy the example deliverable into a working directory. Pass optional flags to rename the system and client placeholders.

## Output Shape

When the user asks for a fresh system, default to this response structure:

1. Design thesis
2. Token system summary
3. Component inventory
4. Usage rules
5. Demo or implementation files

Keep the prose concise. Put the detail into the deliverable artifacts.
