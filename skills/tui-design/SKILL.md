---
name: tui-design
description: Rapidly design, prototype, and iterate on high-fidelity Terminal User Interface (TUI) screen mockups with real-time live browser canvas preview and ANSI terminal output. Use when designing TUIs, command-line interfaces, terminal dashboards, tables, dialogs, splits, or discussing TUI layouts with Marcus.
---

# TUI Design & Prototyping Studio

Use the `tui` engine located at `~/code/tui` to create, preview, and iterate on deterministic, pixel-accurate terminal mockups without manually counting ASCII characters or suffering from box border drift.

```bash
TUI_REPO="${TUI_REPO:-$HOME/code/tui}"
test -x "$TUI_REPO/bin/tui.js"
```

## Quick Commands

| Action | Command |
|---|---|
| **Start Live Studio** (Web Canvas at `http://localhost:3333`) | `node "$TUI_REPO/bin/tui.js" serve` |
| **Render to Terminal** (ANSI Truecolor output) | `node "$TUI_REPO/bin/tui.js" render path/to/file.tui.yaml` |
| **Render Specific State** | `node "$TUI_REPO/bin/tui.js" render file.tui.yaml --state "Modal Open"` |
| **Create New Mockup** | `node "$TUI_REPO/bin/tui.js" new <name> [--dir ./mockups]` |
| **Validate Mockup** | `node "$TUI_REPO/bin/tui.js" check path/to/file.tui.yaml` |

---

## Canvas boards and presentation

Use `?file=<filename>&view=board` on the studio URL to open all states in a document on one pannable canvas. `B` switches between Canvas and Presentation while retaining the selected screen. The file's `states` are the board's screens: group related design alternatives in one `.tui.yaml` rather than making the user step through separate files.

- Set top-level `board: {columns: 3, gap: 100}` for automatic arrangement (columns 1–12, gap 24–1000 CSS pixels). Existing files work without this field.
- A state may specify `position: {x: 0, y: 0}` for an authored layout, including negative coordinates. Positions are CSS pixels at the studio's 15px font / 20px row, not terminal cells. Omit positions to use automatic layout.
- Give states concise, distinct `name` values, short `description` captions, and `notes` describing tradeoffs. YAML owns the arrangement; the browser remembers only its camera.
- Users pan by scrolling, dragging the background, or Space+drag. Pinch / Ctrl+scroll zooms; `F` fits all screens and `Shift+F` fits the selection. A screen's Present button or double-click opens its presentation.
- Copy Reference identifies the selected screen and includes `view=board` when relevant. Screenshot exports the selected screen at native terminal size. Component inspection remains in Presentation.

For Sidecar work, prefer `theme: sidecar-modern` and reuse the studio's `sidecar_header`, `sidecar_footer`, and pane chrome primitives. Start from `mockups/project-switcher.tui.yaml` or `mockups/sidecar-pane-switcher.tui.yaml` when their structure fits. Read `~/code/tui/README.md` for the board schema and current renderer capabilities.

---

## Standard Viewport Sizing Guide

Modern terminal dimensions on macOS Retina displays:

| Preset | Dimensions (Cols × Rows) | Best For |
|---|---|---|
| **MacBook Pro 14" Default** | `160 × 45` | Standard comfortable full-window app view (Default) |
| **MacBook Pro Full** | `180 × 50` | Dense dashboards, multi-column analytics |
| **MacBook 16" / External** | `200 × 55` | 4K / Studio Display / 16" MacBook Pro |
| **Laptop Medium** | `140 × 40` | Floating / centered standard terminal window |
| **Half-Screen Split** | `100 × 45` | Tiling window managers / side-by-side terminal panes |
| **Classic Minimal** | `80 × 24` | VT100 / standard POSIX CLI compatibility |
| **Ultrawide** | `240 × 60` | Multi-pane wide tiling layouts |

---

## The Collaborative Workflow with Marcus

1. **Start the live server** if not already running (`node ~/code/tui/bin/tui.js serve`).
2. **Draft or edit a `.tui.yaml` file** in `~/code/tui/mockups/` (or current project directory).
3. The live browser canvas at [**`http://localhost:3333`**](http://localhost:3333) updates automatically over WebSockets in real time.
4. Marcus can click any component or the **"Copy Reference"** button to paste a rich reference URL containing query parameters:
   
   `~/code/tui/mockups/dashboard.tui.yaml?size=160x45&theme=tokyo-night&component=layout.children[1].children[1]&title=Task+Queue`

### How Agents Should Interpret Reference Query Parameters:
When Marcus pastes a reference string with query params, interpret the fields:
- **Base Path**: The absolute file path to edit (e.g. `~/code/tui/mockups/dashboard.tui.yaml`).
- **`state`**: The active multi-screen state name or index the user is reviewing.
- **`size`**: The viewport size the user is viewing (e.g. `160x45`). Make sure new elements fit within these bounds.
- **`theme`**: The active theme name (e.g. `catppuccin-mocha`, `tokyo-night`).
- **`component`**: The exact layout path of the component Marcus clicked on (e.g. `layout.children[1].children[1]` or `modals[0]`).
- **`title`**: The user-visible title of the focused component.
- **`col` & `row`**: Exact terminal grid cell coordinates.
- **`zoom`**: Active canvas scaling mode.

5. Apply the requested changes directly to the YAML file at the referenced component location.

---

## Mockup Specification Reference (`.tui.yaml`)

Every mockup file starts with the standardized agent instruction header:

```yaml
# ==============================================================================
# TUI STUDIO MOCKUP SPECIFICATION
# ==============================================================================
# WHAT THIS IS:
# This file defines a high-fidelity Terminal User Interface (TUI) layout mockup.
# It compiles directly into a deterministic 2D terminal character grid.
# ==============================================================================

title: "App Dashboard"
viewport:
  cols: 160
  rows: 45
theme: "catppuccin-mocha" # catppuccin-mocha | tokyo-night | dracula | nord | gruvbox | monokai

layout:
  type: vertical # vertical | horizontal
  children:
    # 1. Top Status/Header Bar
    - type: bar
      height: 1
      style: "bg:surface0 fg:subtext"
      left: " [bold][fg:accent]APP NAME[/fg][/bold] v1.0 "
      center: "[bold]Overview[/bold]"
      right: "Online ● "

    # 2. Main Horizontal Split
    - type: horizontal
      flex: 1
      children:
        # Left Pane (Sidebar)
        - type: pane
          width: 36
          title: " Navigation "
          border: rounded # rounded | single | double | thick | none
          border_style: "fg:border"
          content:
            - list:
                selected_index: 0
                cursor: "❯ "
                items:
                  - { text: "Overview", badge: "Live", badge_style: "bg:green fg:black" }
                  - { text: "Tasks", badge: "4" }
                  - { text: "Settings" }
            - divider: "Metrics"
            - text: "[dim]Memory:[/dim] [fg:success]420 MB[/fg] / 16 GB"
            - text: "[dim]Uptime:[/dim] 4d 18h"

        # Right Pane (Main Content)
        - type: pane
          flex: 1
          title: " Details & Queue "
          border: rounded
          border_style: "fg:accent"
          content:
            - tabs:
                items: ["Live Queue", "Completed", "Settings"]
                active: 0
            - divider: ""
            - table:
                headers: ["ID", "TASK DESCRIPTION", "STATUS", "PRIORITY"]
                widths: [10, "50%", 16, 12]
                selected_row: 0
                rows:
                  - ["td-89f2a1", "Implement TUI Studio Engine", "[badge:green:black:DONE]", "[fg:red]High[/fg]"]
                  - ["td-7cd17e", "Semantic Search Vector Indexing", "[badge:accent:black:IN PROGRESS]", "[fg:yellow]Med[/fg]"]
            - divider: "Progress"
            - progress:
                value: 68
                total: 100
                label: "68% (1,428 / 2,100 files indexed)"

    # 3. Bottom Keybinding Bar
    - type: bar
      height: 1
      style: "bg:surface0 fg:subtext"
      left: " [kbd:q] Quit  [kbd:Tab] Focus  [kbd:j/k] Move  [kbd:Enter] Open"
      right: "160x45 "
```

---

## Multi-State Mockups (e.g. Modals / Popups)

To show interactive state changes (e.g. normal screen vs modal open):

```yaml
title: "Confirm Action Flow"
viewport: { cols: 160, rows: 45 }
theme: "tokyo-night"

states:
  - name: "Normal View"
    layout:
      type: vertical
      children: [...]

  - name: "Confirmation Modal Open"
    layout:
      type: vertical
      children: [...]
    modals:
      - title: " Confirm Task Deletion "
        width: 68
        height: 12
        border: double
        border_style: "fg:error bold"
        shadow: true # Renders drop-shadow
        content:
          - text: "[fg:error bold]⚠ WARNING:[/fg] You are about to delete this item."
          - divider: ""
          - text: "Are you sure you want to proceed?"
          - bar:
              style: "bg:surface1 fg:fg"
              center: "[ [bold][fg:error]Y[/fg][/bold]es, Delete ]    [ [bold][fg:accent]N[/fg][/bold]o, Cancel ]"
```

---

## Text Styling & Inline Tags

Use inline markup tags anywhere in `text`, `table` cells, `list` items, or `bars`:
- Style tokens: `[bold]...[/bold]`, `[dim]...[/dim]`, `[italic]...[/italic]`, `[underline]...[/underline]`, `[reverse]...[/reverse]`
- Colors: `[fg:accent]...[/fg]`, `[bg:surface0]...[/bg]`, `[fg:#89b4fa]...[/fg]`, `[green]...[/green]`, `[red]...[/red]`, `[yellow]...[/yellow]`, `[blue]...[/blue]`, `[cyan]...[/cyan]`, `[magenta]...[/magenta]`, `[muted]...[/muted]`
- Badges: `[badge:DONE]` (accent bg), `[badge:green:black:ACTIVE]`, `[badge:surface2:fg:QUEUED]`
- Key shortcuts: `[kbd:Ctrl+C]`, `[kbd:q]`, `[kbd:Enter]`
