---
name: nano-banana-pro
description: Generate or edit images with Google's Nano Banana Pro image model through the bundled Gemini API script. Use for text-to-image generation, image-to-image edits, or requests for 1K, 2K, or 4K Gemini image output.
---

# Nano Banana Pro

Generate or edit images with the bundled script. Resolve the script relative to
this `SKILL.md`; do not assume a particular agent harness or installed-skills
directory.

## Preflight

Run the non-billing check before the first generation in a session:

```bash
uv run /absolute/path/to/nano-banana-pro/scripts/generate_image.py --check
```

The script reads `GEMINI_API_KEY` from the environment. If this machine keeps
the key in `~/.secrets`, source that file without printing its contents:

```bash
source ~/.secrets >/dev/null 2>&1
uv run /absolute/path/to/nano-banana-pro/scripts/generate_image.py --check
```

Never echo a key. Prefer `GEMINI_API_KEY` over `--api-key`, because command-line
arguments may be visible to other processes.

## Generate

Run from the user's working directory so relative output paths land with the
rest of their work:

```bash
uv run /absolute/path/to/nano-banana-pro/scripts/generate_image.py \
  --prompt "A serene Japanese garden with cherry blossoms" \
  --filename "2026-07-25-09-30-00-japanese-garden.png" \
  --resolution 1K
```

Use the filename format `yyyy-mm-dd-hh-mm-ss-description.png`. Keep a new
filename for every iteration.

Start at `1K`. Move to `2K` when normal-resolution output is requested and to
`4K` only for a requested or approved final high-resolution result. Dimensions
map as follows:

- low resolution, 1080p, or 1K: `1K`
- normal, medium, 2048, or 2K: `2K`
- high resolution, high-res, ultra, or 4K: `4K`

## Edit

Pass the source image with `--input-image`:

```bash
uv run /absolute/path/to/nano-banana-pro/scripts/generate_image.py \
  --input-image "/absolute/path/to/original.jpg" \
  --prompt "Change only the sky to dramatic storm clouds; preserve the subject, crop, lighting, text, and all other details." \
  --filename "2026-07-25-09-35-00-dramatic-sky.png" \
  --resolution 2K
```

For precise edits, name the single change and explicitly list what must remain
unchanged. Reuse the same original input while iterating unless the user asks
to build on an earlier generated result.

## Output and Errors

The script creates parent directories as needed, writes a PNG, and prints its
absolute path. Inspect the image before handing it off when visual quality is
part of the request.

Common failures:

- `No API key provided`: load `GEMINI_API_KEY`.
- `Error loading input image`: verify the source path and permissions.
- quota, permission, or HTTP 403 errors: the configured account lacks access or
  quota; do not expose or guess credentials.
