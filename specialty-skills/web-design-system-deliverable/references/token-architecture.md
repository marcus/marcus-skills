# Token Architecture

Use a three-layer token model.

## 1. Primitive Tokens

Reserve primitive tokens for raw values only.

Examples:

- `stone-950`
- `sand-100`
- `copper-500`
- `space-6`
- `radius-3`
- `shadow-2`
- `duration-fast`

Rules:

- Keep primitives brand-agnostic where possible.
- Store exact values here and nowhere else.
- Avoid using primitive tokens directly in component classes unless the token is also the intended semantic role.

## 2. Semantic Tokens

Map primitives to meaning.

Required groups:

- background: canvas, surface, elevated, inverse
- foreground: strong, muted, subtle, inverse
- border: subtle, strong, inverse
- accent: brand, brand-hover, brand-pressed, accent-contrast
- feedback: success, warning, danger, info
- focus: ring, ring-offset

Rules:

- Name tokens by role, not by appearance.
- Make component styling depend on semantic tokens first.
- Theme by re-pointing semantic tokens, not by rewriting component CSS.
- Keep light theme canonical unless the user explicitly asks for dark-first.

## 3. Component Tokens

Create component tokens only when multiple components need local indirection or when a component has a bespoke behavior pattern.

Examples:

- `button-primary-bg`
- `button-primary-fg`
- `field-border-hover`
- `nav-item-bg-active`

Rules:

- Keep component tokens thin.
- Do not duplicate semantic roles without a reason.
- Add component tokens when they protect components from broad semantic changes.

## Naming Standard

Use lowercase kebab-case.

Prefer:

- `--color-bg-surface`
- `--color-fg-muted`
- `--space-6`
- `--radius-3`
- `--motion-duration-fast`

Avoid:

- `--blue-500-button`
- `--primary-button-main-color`
- `--text-gray`

## Type and Layout Tokens

Always include:

- font families
- type scale
- line-height scale
- letter-spacing scale where needed
- content widths
- grid gutters
- spacing scale

Keep spacing on one base. Use either 4px or 8px increments and stay disciplined.

## Validation Checklist

Before shipping:

- Confirm every component consumes semantic or component tokens instead of hard-coded values.
- Confirm status colors have foreground/background pairs.
- Confirm focus ring token is visible on both light and dark surfaces.
- Confirm typography tokens cover display, heading, body, label, and code.
