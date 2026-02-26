---
name: roc-icons
description: "Use Roc icon library (@marcus/roc) in projects. Covers React, Svelte, and HTML sprite usage, all 4 styles, and migration from other icon sets."
tags: [icons, react, svelte, svg, ui]
---

# Roc Icons (@marcus/roc)

Handcrafted SVG icon library with 416 icons across 4 styles. Use this skill when adding, replacing, or configuring icons in any project.

**Browse all icons**: https://roc.haplab.com

## Install

```bash
npm install @marcus/roc
```

Requires Node.js 22+.

## Styles

| Style | Import path | Description | Use when |
|-------|------------|-------------|----------|
| **outline** | `*/outline` | Rounded strokes, 1.5px | Default for most UI |
| **solid** | `*/solid` | Filled shapes | Active/selected states, nav bars |
| **duotone** | `*/duotone` | Tinted bg + outline strokes | Feature highlights, dashboards |
| **sharp** | `*/sharp` | Angular, miter joins, butt caps | Technical/developer UIs |

Pick one style per context. Don't mix outline and solid in the same toolbar.

## React

```jsx
import { Home, Bell, Search } from '@marcus/roc/react/outline';

<Home size={20} className="text-gray-500" />
<Bell size={20} />
<Search size={16} />  {/* stroke auto-adjusts to 1.75 at <=16px */}
```

### Import patterns

```jsx
// Single style barrel import
import { Home, Bell } from '@marcus/roc/react/outline';
import { Home, Bell } from '@marcus/roc/react/solid';
import { Home, Bell } from '@marcus/roc/react/duotone';
import { Home, Bell } from '@marcus/roc/react/sharp';
```

### Props

| Prop | Type | Default | Notes |
|------|------|---------|-------|
| `size` | number | 24 | Width and height in px |
| `strokeWidth` | number | auto | 1.75 at <=16px, 1.5 at 20px+. Only on stroked styles (outline, duotone, sharp). |
| `className` | string | — | CSS class |
| `...rest` | SVGProps | — | All standard SVG attributes passed through |

## Svelte

```svelte
<script>
  import Home from '@marcus/roc/svelte/outline/Home.svelte';
  import Bell from '@marcus/roc/svelte/solid/Bell.svelte';
</script>

<Home size={24} class="icon" />
<Bell size={20} />
```

### Import patterns

```js
// Individual component (recommended for Svelte)
import Home from '@marcus/roc/svelte/outline/Home.svelte';

// Barrel import (works but larger bundle)
import { Home, Bell } from '@marcus/roc/svelte/outline';
```

Component names are PascalCase: `arrow-left.svg` becomes `ArrowLeft.svelte`.

## HTML Sprite

Copy `dist/sprite.svg` to your public directory, then:

```html
<svg width="24" height="24" class="text-gray-700">
  <use href="/sprite.svg#home-outline" />
</svg>
```

Symbol IDs: `{name}-{style}` (e.g., `bell-solid`, `search-duotone`, `home-sharp`).

## Duotone Setup

Duotone icons require a CSS custom property. Add once globally:

```css
:root {
  --color-duotone-fill: rgba(94, 106, 210, 0.15);
}
```

Adjust the color/opacity to match your design system. Common values:

```css
/* Blue tint (default) */
--color-duotone-fill: rgba(94, 106, 210, 0.15);

/* Brand-colored */
--color-duotone-fill: rgba(var(--brand-rgb), 0.12);

/* Neutral */
--color-duotone-fill: rgba(0, 0, 0, 0.08);
```

## Metadata

```js
import metadata from '@marcus/roc/metadata';
// { icons: [...], categories: [...], total: 416 }
```

Use for building icon pickers, search, or documentation.

## Available Icons

416 icons across 18 categories. See [references/icon-catalog.md](references/icon-catalog.md) for the full list.

**Categories**: Navigation, Data, Communication, People, System, Brand, Actions, Files, Media, Weather, Transport, Commerce, Development, Devices, Objects, Food, Gaming, Nature

**Common icons by use case**:

| Use case | Icons |
|----------|-------|
| Navigation | `home`, `arrow-*`, `chevron-*`, `caret-*`, `compass`, `map`, `globe` |
| Forms & input | `search`, `check`, `x`, `plus`, `minus`, `eye`, `eye-off`, `pencil` |
| CRUD actions | `plus`, `pencil`, `trash`, `copy`, `download`, `upload`, `share` |
| Auth & security | `lock`, `unlock`, `key`, `shield`, `shield-check`, `fingerprint`, `sign-out` |
| Notifications | `bell`, `mail`, `inbox`, `send`, `message-circle`, `chat` |
| Media controls | `play`, `pause`, `stop`, `skip-forward`, `skip-back`, `volume`, `volume-off` |
| Status & feedback | `check-circle`, `x-circle`, `alert-triangle`, `alert-circle`, `info`, `help-circle` |
| Data viz | `chart`, `pie-chart`, `line-chart`, `bar-chart`, `trending-up`, `trending-down`, `activity` |
| E-commerce | `shopping-cart`, `shopping-bag`, `credit-card`, `dollar`, `euro`, `tag`, `receipt` |
| Social/Brand | `github`, `twitter-logo`, `discord-logo`, `slack-logo`, `linkedin-logo` + 30 more |

## Migration from Other Libraries

### From Lucide / Heroicons / Phosphor

1. Replace the import source:

```jsx
// Before (Lucide)
import { Home, Bell } from 'lucide-react';

// After (Roc)
import { Home, Bell } from '@marcus/roc/react/outline';
```

2. Props map directly: `size`, `strokeWidth`, `className` all work the same.

3. Name differences: most icon names match Lucide conventions. Check the [icon catalog](references/icon-catalog.md) for exact names. Key differences:
   - Kebab-case filenames: `arrow-left` not `arrowLeft`
   - PascalCase components: `ArrowLeft` (same as Lucide)
   - Brand icons use `-logo` suffix: `github` (icon), `twitter-logo`, `discord-logo`

### From Font Awesome

Replace `<i>` tags with components:

```jsx
// Before
<i className="fa-solid fa-house" />

// After
import { Home } from '@marcus/roc/react/solid';
<Home size={20} />
```

### Svelte migration

```svelte
<!-- Before (any icon lib) -->
<Icon name="home" />

<!-- After (Roc) -->
<script>
  import Home from '@marcus/roc/svelte/outline/Home.svelte';
</script>
<Home size={24} />
```

## Checklist for Migration

- [ ] Install `@marcus/roc`
- [ ] Remove old icon package from dependencies
- [ ] Find-and-replace imports (match old names to Roc names via catalog)
- [ ] Add duotone CSS variable if using duotone style
- [ ] Verify icon rendering at target sizes (16, 20, 24)
- [ ] Check that `currentColor` inheritance works with your color system
