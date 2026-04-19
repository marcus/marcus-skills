# Google Stitch & DESIGN.md Origin

## What is Google Stitch?

Google Stitch is a design-to-code tool from Google Labs that generates UI code from design files (Figma, images, or text descriptions). It introduced the `DESIGN.md` convention as a way to give AI coding agents persistent design system context across sessions.

**Key insight from Stitch:** Design systems encoded as plain markdown are more reliably consumed by LLMs than CSS files, design tokens JSON, or Figma links. Markdown is unambiguous, structured, and fits naturally in context windows.

## Why DESIGN.md Works for Agents

LLMs are good at following rules stated in plain language. A CSS file says:

```css
.btn-primary {
  background-color: #3B82F6;
  padding: 8px 16px;
}
```

A DESIGN.md says:

```markdown
**Primary button:** bg `#3B82F6` (brand-primary), padding `8px 16px`, radius 6px
- Hover: +10% brightness
- Disabled: opacity 0.5
```

The second form is semantically richer — it communicates intent, not just implementation. Agents can generalize from it to new components without guessing.

## Stitch Format Conventions

Stitch-generated DESIGN.md files follow these conventions (which this skill preserves):

1. **File placement:** Always project root, named exactly `DESIGN.md`
2. **Section headers:** Use `##` for top-level sections (Colors, Typography, etc.)
3. **Token tables:** Markdown tables with columns: Token | Value | Usage
4. **Exact values:** Never approximate. `#3B82F6` not "a blue". `rgba(0,0,0,0.5)` not "semi-transparent black"
5. **State documentation:** Components list every interactive state (hover, focus, active, disabled, loading)
6. **Anti-patterns section:** Explicit ❌ prohibitions for the most common mistakes
7. **Freshness note:** Include a "Last updated" date at the top

## Compatibility with Other AI Tools

DESIGN.md works with any AI coding tool that reads project context files:

| Tool | How to reference DESIGN.md |
|------|---------------------------|
| Claude Code | Add to `CLAUDE.md`: "Read DESIGN.md before writing any UI code" |
| Codex / OpenAI | Add to `AGENTS.md` or `CODEX.md` |
| Cursor | Add to `.cursorrules` |
| GitHub Copilot | Reference in workspace instructions |
| Aider | `--read DESIGN.md` flag, or add to `.aider.conf.yml` |
| Any agent | Just add a line to your agent instructions file pointing to it |

## Relationship to Other Design Token Formats

DESIGN.md is a **human-and-AI-readable summary**, not a machine-executable token format. It complements (but doesn't replace):

- **Style Dictionary** — generates CSS/JS/iOS/Android tokens from a canonical JSON source
- **Figma Tokens plugin** — exports design tokens from Figma
- **Tailwind config** — configures utility classes
- **CSS custom properties** — runtime-accessible design values

The workflow: maintain your source of truth (Figma, Style Dictionary, Tailwind config), then keep DESIGN.md in sync as the AI-readable summary layer.

## When Google Stitch Generates DESIGN.md

Stitch creates DESIGN.md automatically when you:
1. Provide a Figma file URL
2. Upload a design screenshot
3. Describe a design system in text

The generated file captures all tokens Stitch detects/infers. You should review and augment it with:
- Component states Stitch may not have documented
- Anti-patterns specific to your project
- Principles and intent

## Evolution of the Convention

As of early 2025, DESIGN.md is an emerging convention. The format isn't fully standardized — different tools may use slightly different section names or structures. The conventions in this skill are:
1. Compatible with what Google Stitch generates
2. Practical for agents (tables, exact values, explicit prohibitions)
3. General enough to work across CSS methodologies

If you're working with a Stitch-generated file, it will be compatible with this skill's format. You may want to add Anti-Patterns and Principles sections, which Stitch doesn't generate automatically.
