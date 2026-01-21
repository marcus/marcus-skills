---
name: betamax-docs
description: Create reproducible TUI screenshots and GIF demos for documentation with Betamax. Use when asked to capture terminal screenshots, record demos, or author .keys files.
---
# Betamax docs capture

Use `README.md` for the authoritative syntax, options, and keys file format. Keep outputs reproducible and deterministic.

## Workflow
1. Pick the output type: PNG/HTML screenshot or GIF demo.
2. Prefer a `.keys` file with `@set:cols`, `@set:rows`, and `@set:output` for consistent sizing.
3. Add `@require:termshot` for PNG or `@require:termshot` + `ffmpeg` for GIFs.
4. Use `@wait`/`@sleep` to reach the desired UI state before capture.
5. Run: `betamax "<command>" -f path/to/file.keys`.

## Screenshot recipe
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

## GIF demo recipe
```bash
@set:cols:120
@set:rows:30
@set:output:./docs/assets
@require:termshot

@record:start
# ... keys with @frame where you want animation steps ...
@record:stop:tui-demo.gif
```

## Fast capture (optional)
- Record a session to a keys file: `betamax record -o demo.keys <command>`
- Quick GIF in one step: `betamax record --gif demo.gif --auto-frame <command>`
