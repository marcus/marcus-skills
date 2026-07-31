#!/usr/bin/env bash
set -euo pipefail

# Compose a diagram image: Mermaid diagram + optional Titan background + text overlays.
#
# Modes:
#   1. Mermaid diagram on solid color background (fastest, no API call)
#   2. Mermaid diagram on Titan-generated atmospheric background
#   3. Text-only overlay on Titan background (no Mermaid)
#
# Usage:
#   compose-diagram.sh --mermaid diagram.mmd --output slide.webp
#   compose-diagram.sh --mermaid diagram.mmd --bg-prompt "abstract teal waves" --output slide.webp
#   compose-diagram.sh --mermaid diagram.mmd --bg-image existing.png --output slide.webp
#   compose-diagram.sh --text "Key Insight" --bg-prompt "navy gradient" --output slide.webp
#   compose-diagram.sh --mermaid diagram.mmd --title "The Loop" --caption "Fig 1" --output slide.webp
#
# Environment:
#   AWS_PROFILE     - for Titan background generation (default: trustfile)
#   AWS_REGION      - Bedrock region (default: us-east-1)
#   DIAGRAM_THEME   - mermaid theme json (default: avalara-dark)
#   DIAGRAM_WIDTH   - output width (default: 1408)
#   DIAGRAM_HEIGHT  - output height (default: 768)
#   BG_OPACITY      - background dim factor 0.0-1.0 (default: 0.25)
#   FONT_PATH       - path to font file (default: /System/Library/Fonts/HelveticaNeue.ttc)
#   FONT_BOLD_PATH  - path to bold font (default: same as FONT_PATH)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Defaults
MERMAID_FILE=""
BG_PROMPT=""
BG_IMAGE=""
TEXT_OVERLAY=""
TITLE=""
CAPTION=""
OUTPUT=""
BG_COLOR="#0d1117"
THEME_NAME="${DIAGRAM_THEME:-avalara-dark}"
WIDTH="${DIAGRAM_WIDTH:-1408}"
HEIGHT="${DIAGRAM_HEIGHT:-768}"
BG_OPACITY="${BG_OPACITY:-0.25}"
FONT="${FONT_PATH:-/System/Library/Fonts/HelveticaNeue.ttc}"
FONT_BOLD="${FONT_BOLD_PATH:-$FONT}"
DIAGRAM_SCALE=0.85
TITLE_SIZE=36
CAPTION_SIZE=20
TEXT_SIZE=48
FORMAT="webp"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mermaid)      MERMAID_FILE="$2"; shift 2 ;;
        --bg-prompt)    BG_PROMPT="$2"; shift 2 ;;
        --bg-image)     BG_IMAGE="$2"; shift 2 ;;
        --bg-color)     BG_COLOR="$2"; shift 2 ;;
        --text)         TEXT_OVERLAY="$2"; shift 2 ;;
        --title)        TITLE="$2"; shift 2 ;;
        --caption)      CAPTION="$2"; shift 2 ;;
        --output|-o)    OUTPUT="$2"; shift 2 ;;
        --width)        WIDTH="$2"; shift 2 ;;
        --height)       HEIGHT="$2"; shift 2 ;;
        --bg-opacity)   BG_OPACITY="$2"; shift 2 ;;
        --theme)        THEME_NAME="$2"; shift 2 ;;
        --scale)        DIAGRAM_SCALE="$2"; shift 2 ;;
        --title-size)   TITLE_SIZE="$2"; shift 2 ;;
        --text-size)    TEXT_SIZE="$2"; shift 2 ;;
        --format)       FORMAT="$2"; shift 2 ;;
        --font)         FONT="$2"; FONT_BOLD="$2"; shift 2 ;;
        --png)          FORMAT="png"; shift ;;
        -*)             echo "Unknown flag: $1" >&2; exit 1 ;;
        *)              echo "Unexpected argument: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$OUTPUT" ]]; then
    echo "Error: --output is required" >&2
    exit 1
fi

if [[ -z "$MERMAID_FILE" && -z "$TEXT_OVERLAY" ]]; then
    echo "Error: --mermaid or --text is required" >&2
    exit 1
fi

TMPDIR_WORK="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_WORK"' EXIT

THEME_FILE="$SCRIPT_DIR/mermaid-themes/${THEME_NAME}.json"
if [[ ! -f "$THEME_FILE" ]]; then
    echo "Warning: theme '$THEME_NAME' not found at $THEME_FILE, using dark defaults" >&2
    THEME_FILE=""
fi

# --- Step 1: Background ---

BG_FILE="$TMPDIR_WORK/background.png"

if [[ -n "$BG_IMAGE" ]]; then
    echo "Using provided background image..."
    magick "$BG_IMAGE" -resize "${WIDTH}x${HEIGHT}!" "$BG_FILE"
elif [[ -n "$BG_PROMPT" ]]; then
    echo "Generating Titan background..."
    "$SCRIPT_DIR/bedrock-generate.sh" "$BG_PROMPT" "$TMPDIR_WORK/titan-raw.png" \
        --size "${WIDTH}x${HEIGHT}" --quality standard 2>&1 | sed 's/^/  /'
    magick "$TMPDIR_WORK/titan-raw.png" -resize "${WIDTH}x${HEIGHT}!" "$BG_FILE"
else
    echo "Using solid color background: $BG_COLOR"
    magick -size "${WIDTH}x${HEIGHT}" "xc:${BG_COLOR}" "$BG_FILE"
fi

# --- Step 2: Dim background ---

DIMMED="$TMPDIR_WORK/dimmed.png"
if [[ -n "$BG_PROMPT" || -n "$BG_IMAGE" ]]; then
    DIM_ALPHA=$(python3 -c "print(int((1.0 - $BG_OPACITY) * 100))")
    magick "$BG_FILE" \
        \( +clone -fill "rgba(13,17,23,0.${DIM_ALPHA})" -draw "rectangle 0,0 ${WIDTH},${HEIGHT}" \) \
        -composite "$DIMMED"
else
    cp "$BG_FILE" "$DIMMED"
fi

# --- Step 3: Render Mermaid diagram ---

DIAGRAM_PNG=""
if [[ -n "$MERMAID_FILE" ]]; then
    echo "Rendering Mermaid diagram..."
    DIAGRAM_PNG="$TMPDIR_WORK/diagram.png"
    DIAGRAM_W=$(python3 -c "print(int($WIDTH * $DIAGRAM_SCALE))")

    MMDC_ARGS=(-i "$MERMAID_FILE" -o "$DIAGRAM_PNG" -b transparent -w "$DIAGRAM_W")

    if [[ -n "$THEME_FILE" ]]; then
        MMDC_ARGS+=(-t dark --configFile "$THEME_FILE")
    else
        MMDC_ARGS+=(-t dark)
    fi

    mmdc "${MMDC_ARGS[@]}" 2>&1 | sed 's/^/  /'
fi

# --- Step 4: Compose layers ---

echo "Compositing..."
COMPOSE_ARGS=("$DIMMED")

# Calculate vertical offset to leave room for title/caption
Y_OFFSET=0
if [[ -n "$TITLE" ]]; then
    Y_OFFSET=$((TITLE_SIZE + 30))
fi

if [[ -n "$DIAGRAM_PNG" ]]; then
    COMPOSE_ARGS+=(
        \( "$DIAGRAM_PNG" \)
        -gravity center -geometry "+0+${Y_OFFSET}"
        -composite
    )
fi

magick "${COMPOSE_ARGS[@]}" "$TMPDIR_WORK/composed.png"

# --- Step 5: Text overlays ---

RESULT="$TMPDIR_WORK/composed.png"

if [[ -n "$TITLE" ]]; then
    magick "$RESULT" \
        -font "$FONT_BOLD" -pointsize "$TITLE_SIZE" \
        -fill "rgba(255,255,255,0.95)" \
        -gravity north -annotate +0+24 "$TITLE" \
        "$RESULT"
fi

if [[ -n "$CAPTION" ]]; then
    magick "$RESULT" \
        -font "$FONT" -pointsize "$CAPTION_SIZE" \
        -fill "rgba(255,255,255,0.6)" \
        -gravity south -annotate +0+16 "$CAPTION" \
        "$RESULT"
fi

if [[ -n "$TEXT_OVERLAY" ]]; then
    magick "$RESULT" \
        -font "$FONT_BOLD" -pointsize "$TEXT_SIZE" \
        -fill "rgba(255,255,255,0.95)" \
        -gravity center -annotate +0+0 "$TEXT_OVERLAY" \
        "$RESULT"
fi

# --- Step 6: Output ---

if [[ "$FORMAT" == "webp" ]]; then
    magick "$RESULT" -quality 90 "${OUTPUT%.png}.webp"
    OUTPUT="${OUTPUT%.png}.webp"
else
    cp "$RESULT" "$OUTPUT"
fi

echo "Done: $OUTPUT"
echo "  Size: $(magick identify -format '%wx%h' "$OUTPUT") | $(du -h "$OUTPUT" | cut -f1 | xargs)"
