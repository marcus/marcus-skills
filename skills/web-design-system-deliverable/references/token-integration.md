# Token Integration

How tokens flow from source of truth to every platform and tool.

## 1. Style Dictionary Configuration

Use Style Dictionary to transform the JSON token file into platform-specific outputs.

Sample `config.json`:

```json
{
  "source": ["tokens/**/*.json"],
  "platforms": {
    "css": {
      "transformGroup": "css",
      "buildPath": "dist/css/",
      "files": [
        {
          "destination": "variables.css",
          "format": "css/variables",
          "options": {
            "outputReferences": true
          }
        }
      ]
    },
    "scss": {
      "transformGroup": "scss",
      "buildPath": "dist/scss/",
      "files": [
        {
          "destination": "_variables.scss",
          "format": "scss/variables",
          "options": {
            "outputReferences": true
          }
        }
      ]
    },
    "ios-swift": {
      "transformGroup": "ios-swift",
      "buildPath": "dist/ios/",
      "files": [
        {
          "destination": "DesignTokens.swift",
          "format": "ios-swift/class.swift",
          "className": "DesignTokens"
        }
      ]
    },
    "android": {
      "transformGroup": "android",
      "buildPath": "dist/android/",
      "files": [
        {
          "destination": "design_tokens.xml",
          "format": "android/resources"
        }
      ]
    },
    "figma": {
      "transformGroup": "css",
      "buildPath": "dist/figma/",
      "files": [
        {
          "destination": "tokens.json",
          "format": "json/flat"
        }
      ]
    }
  }
}
```

Transform group notes:

- `css`: name/cti/kebab, size/rem, color/css.
- `scss`: same as CSS but outputs `$` variables.
- `ios-swift`: name/ti/camel, size/swift/remToCGFloat, color/UIColorSwift.
- `android`: name/cti/snake, size/remToSp, color/hex8android.

Run with:

```bash
npx style-dictionary build --config config.json
```

## 2. Figma Variables Integration

Structure Figma variables to mirror the three-layer token model.

### Collection Structure

| Collection | Purpose | Modes |
|-----------|---------|-------|
| Primitives | Raw values (colors, spacing, radii) | Single mode |
| Semantic | Role-based mappings | Light, Dark |
| Component | Component-specific overrides | Light, Dark (inherited) |

### Naming Convention Mapping

| CSS Variable | Figma Variable |
|-------------|---------------|
| `--color-bg-canvas` | `semantic/color/bg/canvas` |
| `--color-fg-strong` | `semantic/color/fg/strong` |
| `--color-accent` | `semantic/color/accent/brand` |
| `--space-4` | `primitives/space/4` |
| `--radius-3` | `primitives/radius/3` |
| `--button-primary-bg` | `component/button/primary/bg` |

Rules:

- Use `/` as the group separator in Figma (it creates folder hierarchy).
- Semantic variables must alias primitive variables, not store raw values.
- Light and Dark modes are defined at the Semantic collection level. Primitives stay mode-independent.
- Bind component properties (fill, stroke, spacing) to variables. Do not use raw hex values.

## 3. Tokens Studio Workflow

If using Tokens Studio (Figma plugin) instead of native Figma variables:

### Setup

1. Connect the plugin to the token repository (GitHub, GitLab, or JSONBin).
2. Point to the `tokens/` directory in the repo.
3. Map token sets: `primitives.json`, `semantic-light.json`, `semantic-dark.json`, `components.json`.

### Sync Workflow

1. Designer updates tokens in Figma via Tokens Studio.
2. Plugin pushes a branch to the repo (e.g., `tokens/update-accent-color`).
3. Engineer reviews the PR. Style Dictionary rebuild runs in CI.
4. On merge, platform outputs are regenerated and published.

### Branch Strategy

- `main`: current production tokens.
- `tokens/*`: token update branches from Figma.
- `next`: staging for upcoming major changes.

Rules:

- Never edit the JSON token file manually and via Tokens Studio simultaneously. Pick one source per change.
- Tag token releases to match design system version.

## 4. Build Pipeline Integration

### Flow

```
Source (JSON)
  --> Validation (lint + schema check)
  --> Transform (Style Dictionary)
  --> Platform outputs (CSS, SCSS, Swift, XML, JSON)
  --> Package (npm, CocoaPod, Maven)
  --> Publish (registry or CDN)
```

### CI/CD Steps

1. **Validate**: Run token linter. Check for: missing required tokens, orphaned primitives (not referenced by any semantic token), naming violations, duplicate values at the semantic level.
2. **Detect breaking changes**: Compare current output with previous release. Flag: renamed tokens (breaking), removed tokens (breaking), changed values (minor or patch). Use a diff script against the previous `dist/` output.
3. **Build**: Run Style Dictionary.
4. **Test**: Snapshot test the CSS output. Confirm expected variable count. Confirm light/dark theme completeness (every semantic token has both modes).
5. **Changelog**: Auto-generate from commit messages or PR labels. Categories: Added, Changed, Deprecated, Removed.
6. **Publish**: Bump version, publish package.

### Token Validation Schema (minimal)

```json
{
  "color": {
    "bg": {
      "canvas": { "value": "{color.stone.50}", "type": "color" },
      "surface": { "value": "{color.stone.100}", "type": "color" }
    }
  }
}
```

Every token must have `value` and `type`. References use `{}` syntax.

## 5. Multi-Platform Token Patterns

The same semantic role expressed per platform:

| Role | CSS | Swift | Kotlin (Compose) | XML (Android) |
|------|-----|-------|-------------------|---------------|
| Accent | `var(--color-accent)` | `DesignTokens.colorAccent` | `AppTheme.colors.accent` | `@color/color_accent` |
| Background canvas | `var(--color-bg-canvas)` | `DesignTokens.colorBgCanvas` | `AppTheme.colors.bgCanvas` | `@color/color_bg_canvas` |
| Foreground strong | `var(--color-fg-strong)` | `DesignTokens.colorFgStrong` | `AppTheme.colors.fgStrong` | `@color/color_fg_strong` |
| Space 4 | `var(--space-4)` | `DesignTokens.space4` | `AppTheme.spacing.s4` | `@dimen/space_4` |
| Radius 3 | `var(--radius-3)` | `DesignTokens.radius3` | `AppTheme.shapes.radius3` | `@dimen/radius_3` |

Naming translation rules:

- CSS: kebab-case with `--` prefix.
- Swift: camelCase, grouped in a static class.
- Kotlin: camelCase, accessed via theme object.
- Android XML: snake_case with `@color/` or `@dimen/` prefix.

Style Dictionary handles these transforms automatically via transform groups. Do not manually maintain platform files.

## 6. Handoff Checklist

The designer-to-engineer handoff package must include:

### Token Delivery

- [ ] JSON token file (source of truth).
- [ ] Generated CSS variables file.
- [ ] Generated platform files if multi-platform.
- [ ] Token change summary (what changed since last handoff).

### Component Specs

- [ ] Component spec per the component-spec-template reference.
- [ ] All states documented (default, hover, focus, active, disabled, loading, error).
- [ ] Token mapping table: which tokens each component consumes.

### Interaction Specs

- [ ] Click/tap behavior.
- [ ] Hover behavior.
- [ ] Keyboard behavior.
- [ ] Transition/animation specs (property, duration token, easing).
- [ ] Loading and empty states.

### Redline Notes

- [ ] Spacing values called out with token names (not pixel values).
- [ ] Type specs reference type scale tokens.
- [ ] Color fills reference semantic token names.
- [ ] Border and radius reference token names.

### Responsive Behavior

- [ ] Breakpoints documented.
- [ ] Layout changes per breakpoint described.
- [ ] Component size/variant changes at breakpoints.
- [ ] Touch target sizes for mobile (minimum 44x44).

### Content Specs

- [ ] Character limits per component.
- [ ] Truncation rules.
- [ ] Placeholder and empty state copy.
- [ ] Error message patterns.

Do not hand off screenshots without token annotations. Engineers should never need to use a color picker.
