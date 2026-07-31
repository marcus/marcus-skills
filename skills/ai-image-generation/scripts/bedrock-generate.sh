#!/usr/bin/env bash
set -euo pipefail

# Generate an image using Amazon Titan Image Generator v2 via Bedrock.
#
# Usage:
#   bedrock-generate.sh "your prompt here"
#   bedrock-generate.sh "your prompt" output.png
#   bedrock-generate.sh "your prompt" output.png --quality premium --size 1408x1024
#
# Environment:
#   AWS_PROFILE   - AWS credentials profile (e.g. "trustfile"). Required unless
#                   default credentials have Bedrock access.
#   AWS_REGION    - Override region (default: us-east-1)
#   TITAN_MODEL   - Override model ID (default: amazon.titan-image-generator-v2:0)

PROMPT="${1:?Usage: bedrock-generate.sh \"prompt\" [output.png] [--quality standard|premium] [--size WxH] [--cfg N] [--count N] [--negative \"text\"] [--seed N]}"
shift

OUTPUT="bedrock-image-$(date +%Y%m%d-%H%M%S).png"
QUALITY="standard"
WIDTH=1024
HEIGHT=1024
CFG=8.0
COUNT=1
NEGATIVE=""
SEED=""

# Parse remaining args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --quality)  QUALITY="$2"; shift 2 ;;
        --size)     WIDTH="${2%%x*}"; HEIGHT="${2##*x}"; shift 2 ;;
        --cfg)      CFG="$2"; shift 2 ;;
        --count)    COUNT="$2"; shift 2 ;;
        --negative) NEGATIVE="$2"; shift 2 ;;
        --seed)     SEED="$2"; shift 2 ;;
        -*)         echo "Unknown flag: $1" >&2; exit 1 ;;
        *)          OUTPUT="$1"; shift ;;
    esac
done

REGION="${AWS_REGION:-us-east-1}"
MODEL="${TITAN_MODEL:-amazon.titan-image-generator-v2:0}"

TMPDIR_WORK="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_WORK"' EXIT

REQUEST="$TMPDIR_WORK/request.json"
RESPONSE="$TMPDIR_WORK/response.json"

NEGATIVE_FIELD=""
if [[ -n "$NEGATIVE" ]]; then
    NEGATIVE_FIELD=", \"negativeText\": $(printf '%s' "$NEGATIVE" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"
fi

SEED_FIELD=""
if [[ -n "$SEED" ]]; then
    SEED_FIELD=", \"seed\": $SEED"
fi

cat > "$REQUEST" << ENDJSON
{
  "taskType": "TEXT_IMAGE",
  "textToImageParams": {
    "text": $(printf '%s' "$PROMPT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')${NEGATIVE_FIELD}
  },
  "imageGenerationConfig": {
    "quality": "${QUALITY}",
    "numberOfImages": ${COUNT},
    "height": ${HEIGHT},
    "width": ${WIDTH},
    "cfgScale": ${CFG}${SEED_FIELD}
  }
}
ENDJSON

echo "Generating image with Titan v2..."
echo "  Prompt:  ${PROMPT:0:80}$([ ${#PROMPT} -gt 80 ] && echo '...')"
echo "  Size:    ${WIDTH}x${HEIGHT}"
echo "  Quality: ${QUALITY}"
echo "  Region:  ${REGION}"
echo "  Profile: ${AWS_PROFILE:-default}"

aws bedrock-runtime invoke-model \
    --region "$REGION" \
    --model-id "$MODEL" \
    --content-type application/json \
    --accept application/json \
    --body "fileb://$REQUEST" \
    "$RESPONSE" > /dev/null

IMAGE_COUNT=$(python3 -c "import json; data=json.load(open('$RESPONSE')); print(len(data['images']))")

if [[ "$IMAGE_COUNT" -eq 1 ]]; then
    python3 -c "
import json, base64
with open('$RESPONSE') as f:
    data = json.load(f)
with open('$OUTPUT', 'wb') as f:
    f.write(base64.b64decode(data['images'][0]))
"
    echo "Saved: $OUTPUT"
else
    BASE="${OUTPUT%.*}"
    EXT="${OUTPUT##*.}"
    for i in $(seq 0 $((IMAGE_COUNT - 1))); do
        OUTFILE="${BASE}-${i}.${EXT}"
        python3 -c "
import json, base64
with open('$RESPONSE') as f:
    data = json.load(f)
with open('$OUTFILE', 'wb') as f:
    f.write(base64.b64decode(data['images'][$i]))
"
        echo "Saved: $OUTFILE"
    done
fi
