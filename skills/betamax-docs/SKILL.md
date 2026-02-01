---
name: betamax-docs
description: Create reproducible TUI screenshots and GIF demos for documentation with Betamax. Use when asked to capture terminal screenshots, record demos, or author .keys files.
---
# Betamax docs capture

Use `README.md` for the authoritative syntax, options, and keys file format. Keep outputs reproducible and deterministic.

## Interactive capture (betamax capture)

Launch any command in a tmux session with a hotkey bound to capture PNG screenshots on demand.

```bash
betamax capture <command>           # capture with default settings
betamax capture nvim myfile.py      # capture inside neovim
betamax capture --preset docs htop  # use a named preset
betamax capture --theme dracula --shadow --window-bar colorful htop
```

Options:
- `--key KEY` — capture hotkey in tmux format (default: `C-g` / Ctrl+G)
- `--output-dir DIR` — output directory (default: `./captures`)
- `--cols N` / `--rows N` — terminal dimensions (default: current terminal)
- `--preset NAME` — load preset from `~/.config/betamax/presets/<name>.conf`
- `--save-text` — also save raw ANSI text alongside PNG
- `--window-bar STYLE` — add window bar: `colorful`, `colorful_right`, `rings`
- `--border-radius N`, `--margin N`, `--padding N` — decoration geometry
- `--shadow` — enable drop shadow
- `--theme NAME` — color theme (`dracula`, `nord`, `catppuccin-mocha`, etc.)

Config files (key=value, `#` comments):
- `.betamaxrc` — project config (searched up to git root)
- `~/.config/betamax/config` — global config
- `~/.config/betamax/presets/<name>.conf` — named presets
- Precedence: CLI flags > .betamaxrc > global > preset > defaults

## Scripted workflow (betamax record / .keys files)

1. Pick the output type: PNG/HTML screenshot or GIF demo.
2. Prefer a `.keys` file with `@set:cols`, `@set:rows`, and `@set:output` for consistent sizing.
3. Add `@require:termshot` for PNG or `@require:termshot` + `ffmpeg` for GIFs.
4. Use `@wait`/`@sleep` to reach the desired UI state before capture.
5. Run: `betamax "<command>" -f path/to/file.keys`.

### Decoration overrides

The same decoration flags from `betamax capture` work on the main command:
```bash
betamax myapp -f demo.keys --theme dracula --shadow --window-bar colorful
betamax myapp -f demo.keys --border-radius 10 --padding 10 --margin 20
```

CLI flags override `@set:` directives in the keys file, which override `.betamaxrc` config.
Precedence: CLI > `@set:` > `.betamaxrc` > global config > preset > defaults.

### Screenshot recipe
```bash
@set:cols:120
@set:rows:30
@set:output:./docs/assets
@require:termshot

@sleep:500
@wait:Ready
@capture:tui.png
q
```

### GIF demo recipe
```bash
@set:cols:120
@set:rows:30
@set:output:./docs/assets
@require:termshot

@record:start
# ... keys with @frame where you want animation steps ...
@record:stop:tui-demo.gif
```

### Fast capture
- Record a session to a keys file: `betamax record -o demo.keys <command>`
- Quick GIF in one step: `betamax record --gif demo.gif --auto-frame <command>`
