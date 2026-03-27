---
name: design-md
description: Create and maintain DESIGN.md files — a design system specification optimized for AI consumption. Use when creating a project's design system file, extracting tokens from existing CSS/code, auditing design consistency, or onboarding an agent to a project's visual language.
---

# DESIGN.md Skill

DESIGN.md is a plain-markdown design system specification that lives in your project root alongside CLAUDE.md/AGENTS.md. It gives AI coding agents persistent, authoritative design context so they never invent visual values or deviate from your system.

Origin: introduced by Google Stitch (Google Labs) as a convention for AI-readable design systems. See `references/stitch-format.md`.

## When to Use This Skill

- **Creating**: Starting a new project and want a design system from the start
- **Extracting**: Existing project has design values scattered in CSS/Tailwind/tokens — consolidate them
- **Auditing**: Review a codebase for design consistency violations
- **Onboarding**: Agent starting work on a project with no design context

## What Goes in DESIGN.md

| Section | Contains |
|---------|----------|
| Colors | Every color with exact hex/rgba, semantic names, usage |
| Typography | Font families, size scale, weights, line heights |
| Spacing | Base unit, full scale (4px, 8px, 12px…) |
| Layout | Breakpoints, grid columns, container widths, gutters |
| Components | Each component: variants, states, exact values |
| Borders & Radius | All radius values, border widths/colors |
| Shadows | Every shadow value verbatim |
| Motion | Duration, easing functions, standard transitions |
| Icons | Library name, usage conventions, size rules |
| Principles | What the design is trying to feel/convey |
| Anti-Patterns | What to never do (never invent colors, avoid X, etc.) |

Full spec for each section: `references/design-md-spec.md`

## How to Create a DESIGN.md

### From scratch (new project)
Use the template below. Fill in values before writing any CSS.

### From existing CSS custom properties
```bash
# Extract all custom properties
grep -r '\-\-[a-z]' src/ --include="*.css" | grep -oP '\-\-[\w-]+:\s*[^;]+' | sort -u

# Extract Tailwind theme
cat tailwind.config.* | grep -A200 'theme:'
```

### From Figma tokens
Export as Style Dictionary JSON, then map to DESIGN.md sections. Use exact values from the export — never approximate.

### Walk the codebase
```bash
# Find hardcoded colors (red flags — should be in DESIGN.md)
grep -r '#[0-9a-fA-F]\{3,6\}\|rgb(\|rgba(' src/ --include="*.css" --include="*.tsx" --include="*.ts"

# Find font-size declarations
grep -r 'font-size\|text-\(xs\|sm\|base\|lg\|xl\)' src/ --include="*.css" | sort -u
```

Map every found value to a named token in DESIGN.md.

## DESIGN.md Template

```markdown
# DESIGN.md

> Design system reference for AI agents. Always consult before writing CSS or components.
> Last updated: YYYY-MM-DD

## Colors

### Brand
| Token | Value | Usage |
|-------|-------|-------|
| `brand-primary` | `#3B82F6` | Primary actions, links, focus rings |
| `brand-secondary` | `#8B5CF6` | Secondary accents |

### Semantic
| Token | Value | Usage |
|-------|-------|-------|
| `bg-base` | `#0F0F0F` | Page background |
| `bg-surface` | `#1A1A1A` | Cards, panels |
| `bg-elevated` | `#242424` | Dropdowns, tooltips |
| `text-primary` | `#F5F5F5` | Body text |
| `text-secondary` | `#A3A3A3` | Muted text, labels |
| `text-disabled` | `#525252` | Disabled states |
| `border-default` | `rgba(255,255,255,0.08)` | Default borders |
| `border-strong` | `rgba(255,255,255,0.16)` | Hover/active borders |

### Status
| Token | Value | Usage |
|-------|-------|-------|
| `success` | `#22C55E` | Success states |
| `warning` | `#F59E0B` | Warnings |
| `error` | `#EF4444` | Errors, destructive |
| `info` | `#3B82F6` | Informational |

## Typography

**Font families:**
- Body/UI: `Inter, system-ui, sans-serif`
- Mono: `'JetBrains Mono', 'Fira Code', monospace`

**Scale:**
| Name | Size | Line Height | Weight | Usage |
|------|------|-------------|--------|-------|
| `text-xs` | 11px | 16px | 400 | Badges, timestamps |
| `text-sm` | 13px | 20px | 400 | Secondary text, captions |
| `text-base` | 14px | 22px | 400 | Body text |
| `text-md` | 15px | 24px | 500 | Emphasis |
| `text-lg` | 18px | 28px | 600 | Section headings |
| `text-xl` | 24px | 32px | 700 | Page headings |

## Spacing

Base unit: **4px**

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight gaps (icon + label) |
| `space-2` | 8px | Inner padding (small) |
| `space-3` | 12px | Standard inner padding |
| `space-4` | 16px | Standard gaps |
| `space-6` | 24px | Section padding |
| `space-8` | 32px | Large section gaps |
| `space-12` | 48px | Page-level padding |

## Layout

| Breakpoint | Width |
|-----------|-------|
| `sm` | 640px |
| `md` | 768px |
| `lg` | 1024px |
| `xl` | 1280px |
| `2xl` | 1536px |

Grid: 12-column, 24px gutters, 16px side padding (mobile), 32px (desktop)
Max content width: 1280px

## Components

### Button
- **Primary**: bg `brand-primary`, text white, radius 6px, padding `8px 16px`, font-size `text-sm`, weight 500
- **Secondary**: bg `bg-surface`, border `border-default`, text `text-primary`
- **Destructive**: bg `error`, text white
- **Ghost**: bg transparent, text `text-secondary`, hover bg `bg-surface`
- **Sizes**: sm (6px 12px), md (8px 16px, default), lg (10px 20px)
- **States**: hover (+10% brightness), active (scale 0.97), disabled (opacity 0.5, cursor not-allowed), loading (spinner replaces label)

### Input
- bg `bg-surface`, border `border-default`, radius 6px, padding `8px 12px`
- Focus: border `brand-primary`, ring `brand-primary/20` (3px)
- Error: border `error`, ring `error/20`
- Disabled: opacity 0.5, cursor not-allowed

### Card
- bg `bg-surface`, border `border-default`, radius 8px, padding `space-4`
- Hover (interactive): border `border-strong`, shadow sm

### Table
- Header: bg `bg-elevated`, text `text-secondary`, font weight 500, text-xs uppercase
- Row: border-bottom `border-default`, hover bg `bg-surface`
- Cell padding: `12px 16px`

## Borders & Radius

| Token | Value |
|-------|-------|
| `radius-sm` | 4px |
| `radius-md` | 6px |
| `radius-lg` | 8px |
| `radius-xl` | 12px |
| `radius-full` | 9999px |

Border width: 1px (default), 2px (focus/active)

## Shadows

```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.5);
--shadow-md: 0 4px 8px rgba(0,0,0,0.4);
--shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
--shadow-focus: 0 0 0 3px rgba(59,130,246,0.25);
```

## Motion

| Token | Value | Usage |
|-------|-------|-------|
| `duration-fast` | 100ms | Micro-interactions |
| `duration-base` | 150ms | Most transitions |
| `duration-slow` | 250ms | Modals, panels |
| `ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | Standard ease |
| `ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Springy entrances |

Standard transition: `all 150ms cubic-bezier(0.4, 0, 0.2, 1)`
Reduce motion: always respect `prefers-reduced-motion: reduce`

## Icons

Library: Lucide (`lucide-react`)
Default size: 16px (sm: 12px, lg: 20px, xl: 24px)
Stroke width: 1.5px
Color: inherit from text color unless semantic

## Principles

- **Dense but breathable**: Compact information density with enough whitespace to avoid clutter
- **Consistent elevation**: bg-base → bg-surface → bg-elevated (never invent new layers)
- **Subtle motion**: Transitions should confirm state changes, not entertain

## Anti-Patterns

- ❌ Never use hardcoded hex values — always reference a named token
- ❌ Never invent colors not in this file
- ❌ Never use `font-size` values not in the scale
- ❌ Never create new shadow values
- ❌ Never deviate from the spacing scale (e.g., `padding: 7px`)
- ❌ Never add `border-radius` values not in the token set
```

## How to Use DESIGN.md

### Reference in CLAUDE.md / AGENTS.md
```markdown
## Design System
This project has a DESIGN.md in the root. Before writing any CSS, styles, or components:
1. Read DESIGN.md
2. Use only values defined there
3. Never invent colors, spacing, or typography values
```

### Agent workflow
1. **Before any UI task**: Read DESIGN.md completely
2. **Before writing CSS**: Check that every value you're about to write exists in DESIGN.md
3. **When a value is missing**: Add it to DESIGN.md first, then use it
4. **Never guess**: If a value isn't in DESIGN.md, ask or add it — don't approximate

### Auditing a codebase
```bash
# Find hardcoded colors that should be tokens
grep -rn '#[0-9a-fA-F]\{3,6\}' src/ --include="*.css" --include="*.tsx"

# Find non-standard spacing
grep -rn 'padding:\s*[0-9]*px\|margin:\s*[0-9]*px' src/ --include="*.css"
```
Cross-reference every found value against DESIGN.md tokens.

## Maintenance

- **Update immediately** when design tokens change in code or Figma
- **Version alongside code** — DESIGN.md is source code, commit it
- **Review quarterly** — remove deprecated tokens, document new patterns
- **Sync to source** — if Tailwind config or CSS variables change, update DESIGN.md to match
- **Single source of truth**: DESIGN.md should always be the canonical reference, not an approximation
