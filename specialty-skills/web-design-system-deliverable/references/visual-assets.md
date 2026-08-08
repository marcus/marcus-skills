# Visual Assets

Art direction for photography, illustration, iconography, and graphic devices. Every section is a framework the agent fills in per brand.

---

## 1. Photography Direction

Define a photography style that reinforces the brand thesis. Every decision below should trace back to the visual language established in the foundations.

### Subject Matter

Choose primary and secondary subjects:

- People (portraits, candid, groups, hands/details)
- Product (hero, in-context, flat-lay, detail)
- Environment (architecture, landscape, workspace, urban)
- Abstract (texture, material, macro, light study)

Rule: Pick one dominant subject category. Use the others as supporting. Never let supporting categories outnumber the primary.

### Composition

Define the default composition approach:

- Rule of thirds with subject at intersection
- Centered and symmetrical
- Asymmetric with intentional negative space
- Tight crop with bleed
- Wide environmental with subject small in frame

Rule: Choose one dominant composition. Allow one secondary for variety. Document the split (e.g., "80% centered, 20% asymmetric").

### Lighting

- Natural / available light
- Studio / controlled
- High contrast / dramatic
- Soft / diffused / overcast
- Backlit / rim-lit
- Mixed (practical sources visible)

Rule: Specify whether post-production should normalize lighting across the set or preserve natural variation.

### Color Treatment

- True to life (minimal grading)
- Warm shift (amber, golden)
- Cool shift (blue, teal)
- Desaturated / muted
- Brand color overlay or tint
- Black and white
- Duotone (specify two colors from brand palette)

Rule: Reference specific primitive tokens for any color grading targets. Example: "Shadows shift toward `stone-900`, highlights toward `sand-100`."

### Mood and Energy

Pick one:

- Calm / contemplative
- Dynamic / energetic
- Intimate / personal
- Authoritative / confident
- Playful / spontaneous
- Aspirational / elevated

Rule: Mood must align with the brand thesis. If the thesis says "quiet confidence," photography cannot be frenetic.

### Crop and Aspect Ratios

Define standard crops per context:

| Context | Ratio | Typical Use |
|---|---|---|
| Hero | 16:9 or 21:9 | Landing page hero, feature section |
| Card | 4:3 or 3:2 | Blog card, product card |
| Square | 1:1 | Avatar, social, thumbnail grid |
| Portrait | 3:4 or 2:3 | Team member, editorial |
| Thumbnail | 1:1 or 16:9 | Navigation, preview |
| Open Graph | 1.91:1 | Social share image |

Rule: Always specify a focal-point strategy for responsive cropping (center, face-detect, or art-directed per breakpoint).

### Do / Don't

Document at least four pairs:

| Do | Don't |
|---|---|
| Use natural light consistent with brand warmth | Use harsh flash or visible artificial lighting |
| Show real environments, not obvious sets | Use generic stock office with forced diversity |
| Crop intentionally with breathing room | Crop awkwardly through joints or mid-forehead |
| Match color grading across the full set | Mix warm and cool grading in the same context |

### Placeholder Stock Photo List

For a real deliverable, source images matching these descriptions. Adapt to the brand:

1. Overhead workspace with warm natural light, desaturated tones, copper-toned objects
2. Single person in profile against a minimal architectural background, soft diffused light
3. Close-up hands working with raw materials, shallow depth of field, muted earth palette
4. Wide landscape with single structure, golden hour, high horizon line
5. Product arranged on textured surface, top-down, even studio light, brand-accent object included
6. Candid group interaction in a real environment, mid-distance, natural expressions
7. Abstract macro texture (stone, fabric, wood grain) usable as background, desaturated
8. Architectural interior with strong geometry, natural window light, cool shadow tones
9. Detail shot of a tool or instrument in use, tight crop, dramatic side light
10. Environmental portrait, subject in their element, shallow depth of field, neutral background

Rule: Every placeholder must specify lighting, composition, color treatment, and subject. Replace all placeholders before shipping.

---

## 2. Illustration System

### Style Family

Choose one primary style:

- Line (consistent stroke, no fill or minimal fill)
- Flat (solid color shapes, no gradients, no outlines)
- Dimensional (subtle shadow, layered planes, implied depth)
- Textured (grain, noise, or hand-drawn quality)
- Geometric (built from circles, rectangles, triangles)
- Organic (freeform, hand-drawn, imperfect edges)

Rule: Mixed styles are acceptable only when codified (e.g., "geometric base with organic texture overlay"). Never mix ad hoc.

### Line Weight

- Uniform stroke weight across all sizes: specify in px (e.g., 2px at 1x)
- Variable stroke: specify min and max, and where variation occurs (e.g., thicker at joints, thinner at terminals)
- Responsive stroke: define weight per optical size tier

Rule: Line weight must survive export at 1x and 2x without appearing inconsistent.

### Color Palette Constraints

Choose one model:

- Full brand palette allowed
- Limited subset (specify which tokens, e.g., accent + 2 neutrals)
- Monochrome + single accent
- Monochrome only
- Custom illustration palette derived from brand (document exact values)

Rule: Illustration colors must pass WCAG AA against their expected background. Document the background token each illustration color is tested against.

### Level of Detail

- Minimal / iconic (few shapes, maximum abstraction)
- Moderate (recognizable subjects, simplified detail)
- Detailed (realistic proportions, rich detail, editorial quality)

Rule: Match detail level to the context. Spot illustrations trend minimal. Hero illustrations can be detailed. Document which contexts get which level.

### Metaphor Usage

- Abstract: represent concepts through shape and color, not literal objects
- Literal: depict the actual subject or action
- Brand-symbolic: use recurring brand motifs to represent concepts

Rule: Maintain a metaphor glossary if the brand uses symbolic representation. Example: "Growth = upward arc, not a plant."

### When to Use Illustration vs. Photography vs. Iconography

| Content Type | Asset Type | Reason |
|---|---|---|
| Abstract concept (security, speed) | Illustration | No photograph can depict the concept directly |
| Real product or person | Photography | Authenticity matters |
| UI action or navigation | Iconography | Needs to be small, fast to parse |
| Empty state or onboarding | Illustration | Sets tone without requiring real content |
| Data or process explanation | Illustration or icon set | Clarity over aesthetics |
| Editorial or storytelling | Photography | Emotional resonance |

### Spot vs. Hero Illustrations

Spot illustrations:

- Max size: 200x200px rendered
- Minimal detail
- 1-3 colors from the constrained palette
- Used inline with text, in cards, or as list markers

Hero illustrations:

- Full-width or dominant visual
- Higher detail allowed
- Full illustration palette
- Used in landing pages, feature sections, empty states

Rule: Never scale a spot illustration to hero size. They are different assets with different detail budgets.

---

## 3. Iconography System

### Style

Choose one:

- Stroke (outlined, transparent fill)
- Fill (solid, silhouette)
- Duotone (two-tone, primary + secondary color)
- Rounded (rounded caps and joins)
- Sharp (square caps and mitered joins)

Rule: Pick one style and apply it everywhere. Mixed icon styles break visual coherence.

### Optical Sizing

| Size Tier | Rendered Size | Use Case |
|---|---|---|
| xs | 16px | Inline with body text, dense UI |
| sm | 24px | Default UI icon, buttons, nav |
| md | 32px | Feature callouts, section markers |
| lg | 48px | Hero features, empty states |

Rule: Icons at 16px need reduced detail compared to 48px. Define which elements to remove at small sizes (e.g., drop interior detail, simplify curves).

### Stroke Width

- Consistent: same stroke width at all sizes (specify value, e.g., 1.5px)
- Scaled: stroke weight increases with size (specify per tier, e.g., 1px at 16, 1.5px at 24, 2px at 32+)

Rule: If using a library, match the library's native stroke width. Do not mix 1.5px custom icons with 2px library icons.

### Grid and Keyshapes

Design all icons on a consistent grid:

- Grid size: 24x24 (standard) with 2px padding = 20x20 live area
- Keyshapes within the grid:
  - Circle: 20px diameter
  - Square: 18x18px
  - Landscape rectangle: 20x16px
  - Portrait rectangle: 16x20px

Rule: Every icon must fit one keyshape. Keyshapes ensure optical consistency across different icon forms.

### Color Rules

- Single color, inherits `currentColor` (default for UI icons)
- Single semantic color from token system (e.g., `color-fg-muted`)
- Multi-color: primary + secondary (duotone only, specify both tokens)
- Never: no gradients, no brand photography inside icons

Rule: Interactive icons must have distinct color tokens for default, hover, active, and disabled states. Reference semantic tokens, not primitives.

### Custom vs. Library

Prefer an established open-source library as the base:

| Library | Style | Stroke | License |
|---|---|---|---|
| Lucide | Stroke, rounded | 2px | ISC |
| Phosphor | Stroke + fill variants | 1.5px | MIT |
| Heroicons | Stroke + fill | 1.5px / 2px | MIT |

Rules:

- Choose one library. Do not mix libraries.
- Custom icons are required only for brand-specific concepts not covered by the library.
- Custom icons must match the library's grid, stroke weight, corner radius, and keyshapes exactly.
- Document which icons are custom and which are from the library.

### Usage Rules

| Mode | Description | Requirements |
|---|---|---|
| Labeled | Icon + visible text label | Icon is decorative, use `aria-hidden="true"` |
| Standalone | Icon only, no label | Must have `aria-label` or `title`, tooltip on hover |
| Decorative | Visual enhancement, no semantic meaning | `aria-hidden="true"`, no interaction |
| Interactive | Clickable icon (button or link) | Minimum 44x44px touch target, focus ring, aria-label |

Rule: Default to labeled. Use standalone only when the icon is universally understood (close, search, menu). Never use a standalone icon for a domain-specific action.

### Minimum Icon Inventory

Every product/marketing system needs at least these:

1. Arrow right
2. Arrow left
3. Chevron down
4. Chevron right
5. Close / X
6. Menu / hamburger
7. Search / magnifying glass
8. Check / checkmark
9. Plus
10. Minus
11. Edit / pencil
12. Trash / delete
13. Settings / gear
14. User / person
15. Mail / envelope
16. Calendar
17. Clock / time
18. Download
19. Upload
20. External link
21. Copy
22. Eye / visibility
23. Filter
24. Sort
25. Notification / bell

Rule: Audit the product against this list. Add domain-specific icons as needed. Remove none without justification.

---

## 4. Graphic Devices

### Dividers and Separators

Define a hierarchy of dividers:

| Level | Treatment | Token Reference |
|---|---|---|
| Subtle | 1px solid, `color-border-subtle` | Use between repeated items in a list |
| Standard | 1px solid, `color-border-strong` | Use between major content sections |
| Accent | 2-3px solid, `color-accent-brand` | Use to highlight key section breaks |
| Decorative | Gradient, pattern, or brand motif | Use sparingly, max once per page |

Rule: Never stack dividers. If a section boundary needs emphasis, use spacing and background change instead of a heavier line.

### Background Textures and Patterns

Options to define:

- Noise / grain overlay (specify opacity, blend mode, grain scale)
- Gradient (specify direction, start/end tokens, whether linear or radial)
- Geometric pattern (specify motif, scale, opacity, repeat rules)
- Solid color blocks (reference background semantic tokens)

Rules:

- Text over texture must still meet WCAG AA contrast.
- Provide a CSS or SVG implementation for each texture, not a raster image.
- Grain overlays must not increase page weight by more than 10KB.

### Container Decorations

| Decoration | When to Use | Specification |
|---|---|---|
| Subtle border | Default card, input fields | 1px, `color-border-subtle`, full radius |
| Accent border | Highlighted card, active state | 1-2px, `color-accent-brand`, left or top edge |
| Corner accent | Premium or editorial contexts | Brand mark or geometric motif at one corner |
| Shadow | Elevated surfaces, dropdowns, modals | Reference `shadow-1`, `shadow-2`, `shadow-3` tokens |
| Inset shadow | Pressed or recessed surfaces | Subtle inner shadow, specify token |

Rule: Choose a maximum of two container decoration strategies per component. Over-decorated containers compete with content.

### Data Visualization Palette

Define an ordered sequence of 6-8 colors for charts and graphs:

| Order | Token | Hex (example) | Use |
|---|---|---|---|
| 1 | `dataviz-1` | (brand accent) | Primary data series |
| 2 | `dataviz-2` | (secondary hue) | Secondary series |
| 3 | `dataviz-3` | (tertiary hue) | Tertiary series |
| 4 | `dataviz-4` | (shifted hue) | Additional series |
| 5 | `dataviz-5` | (shifted hue) | Additional series |
| 6 | `dataviz-6` | (shifted hue) | Additional series |
| 7 | `dataviz-neutral` | (muted neutral) | Baseline, average, or "other" |
| 8 | `dataviz-emphasis` | (high contrast) | Highlighted or selected data point |

Rules:

- Adjacent colors in the sequence must be distinguishable by hue, not just lightness.
- All colors must pass 3:1 contrast against the chart background for non-text elements (WCAG 1.4.11).
- Provide a deuteranopia-safe alternative ordering or pattern fills for accessibility.
- Never use red/green as the only differentiator between two adjacent series.

### Empty State Illustrations

- Style: match the illustration system (section 2), but at spot-illustration detail level
- Tone: encouraging, not apologetic. "Nothing here yet" not "Something went wrong."
- Complexity: simple enough to render at 200x200px without losing clarity
- Color: constrained palette (monochrome + accent recommended)
- Pairing: always pair with a heading and a single action (CTA button)

Rule: Every empty state must include an illustration, a short message, and a primary action. No blank screens.

### Decorative Elements

Define brand-specific graphic motifs:

- Brand mark as pattern (tiled, rotated, or cropped versions of the logo mark)
- Geometric motifs (recurring shapes derived from the logo or brand concept)
- Organic shapes (blob, wave, arc used as section backgrounds or accents)

Rules:

- Decorative elements must not interfere with readability.
- Limit to 2-3 motifs. More than that dilutes brand recognition.
- Every motif needs a documented scale range (minimum and maximum size) and opacity range.
- Provide SVG source for all motifs.

---

## 5. Asset Governance

### File Format

| Asset Type | Primary Format | Fallback | Notes |
|---|---|---|---|
| Icons | SVG | PNG at 2x | SVG preferred for color theming via `currentColor` |
| Illustrations | SVG | PNG at 2x | Complex illustrations may require PNG |
| Photography | WebP | JPEG | Serve WebP with JPEG fallback |
| Textures / patterns | SVG or CSS | PNG tile | Prefer code-generated over raster |
| Logo | SVG | PNG at 2x, 3x | SVG is the source of truth |

### Naming Convention

Use lowercase kebab-case. Structure:

```
{type}-{name}-{variant}-{size}.{ext}
```

Examples:

- `icon-arrow-right-24.svg`
- `icon-check-16.svg`
- `illustration-empty-state-inbox.svg`
- `photo-hero-workspace-01.webp`
- `pattern-grain-overlay.svg`
- `logo-wordmark-dark.svg`

Rules:

- No spaces, underscores, or camelCase.
- Numbered variants use zero-padded two-digit suffixes (`-01`, `-02`).
- Size suffix is optional for illustrations and photography, required for icons.

### Resolution and Export

- Export all raster assets at 1x and 2x minimum.
- Use SVG wherever possible. SVG eliminates resolution concerns.
- Raster photography: minimum 2x the largest rendered size.
- Maximum file size targets: icons < 2KB, illustrations < 50KB, hero photos < 200KB (compressed).
- Run all SVGs through SVGO or equivalent optimizer before shipping.
- Strip metadata from all raster exports.

### Alt Text and Accessibility

Rules:

- Every `<img>` has an `alt` attribute. No exceptions.
- Decorative images: `alt=""` and `aria-hidden="true"`.
- Informative images: alt text describes the content, not the file name.
- Complex illustrations or charts: provide `aria-describedby` linking to a longer description.
- Icons: follow the usage rules in section 3 (labeled, standalone, decorative, interactive).
- Never rely on an image alone to convey critical information.

Alt text style:

- Concise (under 125 characters).
- Describe what is shown, not what it means. Context provides meaning.
- Do not start with "Image of" or "Photo of."

### Asset Library Organization

Organize the asset library by type, then by category:

```
assets/
  icons/
    ui/
    brand/
  illustrations/
    spot/
    hero/
    empty-states/
  photography/
    hero/
    card/
    team/
  patterns/
  logos/
```

Rules:

- One source of truth. Do not duplicate assets across folders.
- Version assets by replacing files, not by appending version numbers to file names.
- Maintain an asset manifest listing every asset, its dimensions, format, alt text, and last-updated date.
- Deprecated assets are removed, not renamed or moved to an archive folder.

---

## Validation Checklist

Before shipping visual assets:

- Photography set has consistent color grading, lighting, and composition.
- All placeholder stock descriptions have been replaced with sourced or commissioned images.
- Illustration style is uniform across spot and hero contexts.
- Icon set covers the minimum inventory list and uses a single style.
- Custom icons match the selected library's grid, stroke, and keyshapes.
- Data visualization palette is tested for deuteranopia accessibility.
- All SVGs are optimized and use `currentColor` where appropriate.
- Every image has correct alt text or is marked decorative.
- File names follow the naming convention without exception.
- Asset manifest is complete and current.
