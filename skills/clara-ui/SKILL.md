---
name: clara-ui
description: Orient in Marcus's Clara workspace, inspect what he is reading, and place or reference corpus documents through the clara-ui CLI. Use when a document belongs in his workspace or his current view provides useful context.
---

# Clara workspace

Clara is the Mac-style workspace over `~/code/clara-home`. The service owns spaces, panes and tabs; the CLI and UI use the same API. `clara-ui --help` describes the current command surface. `CLARA_UI_URL` selects a service.

Start with `clara-ui look`: the most recently used Mac, its space, visible panes, focus and reported reading position. `--device <id>` targets a particular Mac; `--json` gives structured output. `state --json` has the full workspace, `search <text>` finds corpus content (`--recall` reaches other sources), and `catalog` lists projects, briefs and docs. `screenshot [--device <id>] [--space <name>] [--out <file>]` saves a read-only PNG at the Mac's reported window size. Headless WebKit shows layout and content without glass blur; older Macs without a size report use 1440×900.

Place documents with `clara-ui open <path> --actor <your-agent-name>`. This opens a background tab by default; add `--focus` when Marcus asked to see it. Use an existing `--space <name|id>` and `--pane <id>` when appropriate, or `--split right|left|up|down` for a useful comparison. `space list` and `space new <name>` expose spaces without requiring a UI. Opening a background tab preserves the active document; an empty pane shows its first tab. Attribution stays with the original opener if a tab is reused.

Use `path <doc>` to obtain a document's full service-side path and `reveal <doc>` to show it in Finder when on that Mac. For new human-facing documents, read `~/code/clara-ui/docs/guides/documents.md` for the house style, document creation/check commands and sandbox rules. Agent instructions, skills and repo plans remain Markdown. The workspace reads corpus files; create or edit their source files with ordinary tools, then open them.
