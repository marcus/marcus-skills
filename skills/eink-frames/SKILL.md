---
name: eink-frames
description: Inspect and control Marcus's Slinky color e-ink frames. Use when checking frame health or history, uploading or fetching frame images, advancing or pausing a frame, or when asked about the office frame, living-room frame, Slinky, inky.local, slinky.local, or e-ink displays.
---

# E-ink Frames

Use the maintained Slinky CLI:

```bash
SLINKY_REPO="${SLINKY_REPO:-$HOME/code/slinky}"
test -x "$SLINKY_REPO/bin/slinky"
"$SLINKY_REPO/bin/slinky" status
```

The two 1600x1200 color e-ink frames are:

| Device | Host | Location |
|---|---|---|
| `office` | `slinky.local` | Office |
| `living` | `inky.local` | Living room |

Use `-d office`, `-d living`, or `-d all` to choose the target. Without a
device flag, Slinky's configured default applies.

## Read-only Checks

These commands do not change the display:

```bash
"$SLINKY_REPO/bin/slinky" status
"$SLINKY_REPO/bin/slinky" -d office history -n 10
"$SLINKY_REPO/bin/slinky" -d living logs -n 50
```

Start with `status` before any requested mutation. The CLI connects over SSH;
do not copy, print, or modify remote `.env` files.

## Presence Detection

`presence` changes scheduler state when it detects the configured phone: it
writes `presence_last_seen`, which feeds the auto-pause decision and can delay
future display scheduling. Do not use it as a read-only health check.

Run it only when the user explicitly asks to check or refresh presence state on
the resolved frame:

```bash
"$SLINKY_REPO/bin/slinky" -d living presence
```

## Images

Upload an image to a device's rotating pool:

```bash
"$SLINKY_REPO/bin/slinky" -d office upload "/absolute/path/to/image.png"
"$SLINKY_REPO/bin/slinky" -d all upload "/absolute/path/to/image.png"
```

Uploading adds the file to the pool; it does not promise immediate display.
Fetch the current image without changing the frame:

```bash
"$SLINKY_REPO/bin/slinky" -d living fetch "/absolute/output/directory"
```

The CLI resizes oversized uploads to at most 3200 pixels on the longest edge.
Prepare important compositions at the frame's 4:3 aspect ratio.

## Display Controls

The following commands change live frame state. Run them only when the user asks
for that effect:

```bash
"$SLINKY_REPO/bin/slinky" -d office next
"$SLINKY_REPO/bin/slinky" -d living prev
"$SLINKY_REPO/bin/slinky" -d office show local_image
"$SLINKY_REPO/bin/slinky" -d all pause
"$SLINKY_REPO/bin/slinky" -d all resume
```

`show` accepts content types including `quote`, `local_image`, `ai_image`,
`headline`, `holiday`, `history`, `weather`, `poetry`, and `artwork`.

Checking presence, uploading, advancing, showing content, pausing, resuming,
deploying, or changing the artwork collection are external mutations. Resolve
the exact device first and report what changed. Do not deploy Slinky as part of
ordinary frame control.
