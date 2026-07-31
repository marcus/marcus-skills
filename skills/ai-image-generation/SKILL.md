---
name: ai-image-generation
description: Generate images via OpenAI (gpt-image-1 / gpt-image-1.5), Google Gemini (Imagen 4), or AWS Bedrock (Amazon Titan Image Generator v2). Includes composite diagram system (Mermaid + Titan backgrounds + ImageMagick) for slide-quality diagrams with perfect text. Use when asked to generate images, create illustrations, compose diagrams, build slide graphics, or use Bedrock/Titan for image generation.
version: 1.1.0
tags: [images, openai, gemini, imagen, dall-e, bedrock, titan, aws, api, diagrams, illustrations]
---

# AI Image Generation

Generate images programmatically using OpenAI GPT Image, Google Gemini Imagen, or AWS Bedrock Titan Image Generator APIs. This skill covers API usage, prompt engineering, batch pipelines, and format handling.

## Provider Comparison

| Feature | OpenAI GPT Image | Gemini Imagen 4 | AWS Bedrock Titan v2 |
|---------|-----------------|-----------------|---------------------|
| Latest model | `gpt-image-1.5` (best), `gpt-image-1`, `gpt-image-1-mini` | `imagen-4.0-generate-001` | `amazon.titan-image-generator-v2:0` |
| Auth | `Authorization: Bearer $OPENAI_API_KEY` | `x-goog-api-key: $GEMINI_API_KEY` | AWS IAM (profile/role) |
| Output formats | PNG, JPEG, WebP (native) | PNG, JPEG | PNG, JPEG |
| Sizes | `1024x1024`, `1536x1024`, `1024x1536`, `auto` | Aspect ratios: `1:1`, `3:4`, `4:3`, `9:16`, `16:9` | Pixel dims up to 1408 on longest side |
| Quality tiers | `low`, `medium`, `high`, `auto` | N/A (single tier) | `standard`, `premium` |
| Batch per request | `n` param (1+) | `sampleCount` (1-4) | `numberOfImages` (1-5) |
| Text in images | Excellent rendering | Good rendering | Fair rendering |
| Transparent bg | Yes (`background: "transparent"`) | No | No |
| Streaming | Yes (`partial_images`) | No | No |
| Price (approx) | $0.02-0.19/image depending on model+quality | $0.02-0.06/image depending on model | ~$0.01-0.02/image (standard) |

### When to choose which

- **OpenAI**: Best text rendering, native WebP, transparent backgrounds, streaming
- **Gemini**: Lower cost, good quality, simpler API surface
- **Bedrock Titan**: Use existing AWS credentials (no separate API key), cost-effective, good for teams already in AWS ecosystem. Supports image conditioning (Canny edge, segmentation).

## Quick Start

For OpenAI and Gemini quick start code, see [references/api-reference.md](references/api-reference.md).

### AWS Bedrock Titan — CLI

Requires AWS credentials (via `gimme-aws-creds`, SSO, or IAM role). Uses `fileb://` for the body.

```bash
# Write the request body to a temp file
cat > /tmp/titan-request.json << 'EOF'
{
  "taskType": "TEXT_IMAGE",
  "textToImageParams": {
    "text": "A flowchart showing data flowing from API to database"
  },
  "imageGenerationConfig": {
    "quality": "standard",
    "numberOfImages": 1,
    "height": 1024,
    "width": 1024,
    "cfgScale": 8.0
  }
}
EOF

# Invoke the model (must use fileb:// not file://)
aws bedrock-runtime invoke-model \
  --region us-east-1 \
  --model-id amazon.titan-image-generator-v2:0 \
  --content-type application/json \
  --accept application/json \
  --body fileb:///tmp/titan-request.json \
  /tmp/titan-response.json

# Extract the base64 image and save as PNG
python3 -c "
import json, base64
with open('/tmp/titan-response.json') as f:
    data = json.load(f)
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(data['images'][0]))
"
```

A helper script that wraps this entire flow is available at [scripts/bedrock-generate.sh](scripts/bedrock-generate.sh).

### AWS Bedrock Titan — Python (boto3)

```python
import boto3, json, base64

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

response = bedrock.invoke_model(
    modelId="amazon.titan-image-generator-v2:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": "A flowchart showing data flow from API to database"},
        "imageGenerationConfig": {
            "quality": "standard",
            "numberOfImages": 1,
            "height": 1024,
            "width": 1024,
            "cfgScale": 8.0,
        },
    }),
)

result = json.loads(response["body"].read())
with open("output.png", "wb") as f:
    f.write(base64.b64decode(result["images"][0]))
```

### Bedrock Titan — Trustfile (Avalara)

For Trustfile AWS access, authenticate first then generate:

```bash
# 1. Get credentials (MFA via authenticator app)
gimme-aws-creds --profile trustfile-okta-admin

# 2. Generate image using the trustfile profile
AWS_PROFILE=trustfile scripts/bedrock-generate.sh "A diagram of a three-tier architecture"

# Or use the profile inline
AWS_PROFILE=trustfile aws bedrock-runtime invoke-model \
  --region us-east-1 \
  --model-id amazon.titan-image-generator-v2:0 \
  --content-type application/json \
  --accept application/json \
  --body fileb:///tmp/titan-request.json \
  /tmp/titan-response.json
```

## API Reference

For full parameter details and response schemas, see [references/api-reference.md](references/api-reference.md).

## Prompt Engineering for Diagrams

Image generation excels at creating diagrams, flowcharts, and conceptual models for documentation and courseware. Key principles:

### Style Guide Pattern

Prepend a consistent style guide to every prompt for visual coherence across a set of images:

```
Flat vector illustration. Muted corporate palette: navy, orange, teal, gray, white.
Text labels are allowed for diagram annotations but use conservatively.
Prefer diagrams, flowcharts, and conceptual models over decorative art.
No faces — use abstract silhouettes. 16:9 aspect ratio. Clean negative space.
```

### Effective Diagram Prompts

Good prompts describe the diagram **structure**, not just the concept:

```
# BAD — too abstract
"An image representing microservices architecture"

# GOOD — describes structure, labels, and layout
"A system architecture diagram with three labeled boxes arranged
horizontally: 'API Gateway' (left), 'Auth Service' (center),
'Database' (right). Arrows connect them left to right. Each box
has a small icon. Clean, minimal, labeled diagram."
```

### Prompt Templates by Diagram Type

| Type | Template pattern |
|------|-----------------|
| Flowchart | "A horizontal flowchart with N labeled nodes connected by arrows. Nodes: 'A' → 'B' → 'C'. Decision diamonds where needed." |
| Comparison | "A side-by-side comparison diagram. Left column labeled 'X'. Right column labeled 'Y'. N rows comparing attributes." |
| Layers/Stack | "A layered stack diagram with N horizontal bands. Bottom: 'Layer 1'. Top: 'Layer N'. Each labeled with icons." |
| Matrix/Quadrant | "A 2x2 quadrant chart. X-axis: 'Low → High'. Y-axis: 'Low → High'. Dots in each quadrant labeled." |
| Process/Pipeline | "A horizontal pipeline with N stages. Input on left, output on right. Each stage labeled with an icon." |
| Hub-and-spoke | "A hub-and-spoke diagram. Center hub labeled 'X'. N spokes radiating to nodes labeled 'A', 'B', 'C'." |
| Concentric | "Concentric rings. Inner: 'X'. Outer: 'Y'. Each ring labeled. Arrows show scope." |
| Before/After | "A before/after split. Left labeled 'Before' with [description]. Right labeled 'After' with [description]." |
| Decision tree | "A decision tree. Root node: 'Start'. Diamond decision nodes with Yes/No branches. Terminal nodes labeled." |
| Maturity model | "N ascending steps/tiers. Tier 1 (lowest): labeled with behaviors. Tier N (highest): labeled with advanced behaviors." |

### Text in Images

- Labels on diagram nodes, axes, and annotations: **yes**
- Repeating body text from the page: **no**
- Keep labels short (1-4 words per label)
- Use labels to clarify relationships the visual alone can't convey

## Composite Diagrams (Mermaid/SVG + Titan Backgrounds)

When text rendering is critical (labeled diagrams, flowcharts, charts), use compositing instead of relying on AI image generators for text. Titan v2 **cannot render readable text** — it garbles all labels, axis text, and annotations.

### Decision: Which Diagram Approach?

| Diagram type | Use | Why |
|-------------|-----|-----|
| Flowcharts, sequences, mind maps, state diagrams, ER diagrams, git graphs | **Mermaid** (`.mmd` → `mmdc`) | Mermaid handles these natively with perfect text |
| Stacked/proportional bar charts, custom layouts, precise positioning, icebergs, levers, concentric rings | **Hand-crafted SVG** | Mermaid can't control element sizing or arbitrary positioning |
| Decorative/atmospheric images without text | **Titan directly** | No text needed, Titan is fine for visuals |
| Any diagram with text labels | **Composite pipeline** | Render diagram (Mermaid or SVG) → composite onto Titan background |

### Pipeline Overview

```
Titan background (optional) ──→ ImageMagick dims to ~15-25% opacity
Mermaid .mmd OR hand-crafted SVG ──→ transparent PNG
ImageMagick ──→ composites layers + adds title/caption text ──→ final .webp
```

### Requirements

```bash
brew install imagemagick librsvg
npm i -g @mermaid-js/mermaid-cli
```

### Quick Start — `compose-diagram.sh`

```bash
# Diagram on solid dark background (no API call, instant)
scripts/compose-diagram.sh --mermaid diagram.mmd --title "My Diagram" --output slide.webp

# Diagram on Titan-generated background
AWS_PROFILE=trustfile scripts/compose-diagram.sh \
  --mermaid diagram.mmd \
  --bg-prompt "Abstract dark navy gradient with subtle particles" \
  --bg-opacity 0.15 \
  --title "The Baseline Loop" \
  --output slide.webp

# Diagram on existing background image
scripts/compose-diagram.sh \
  --mermaid diagram.mmd \
  --bg-image backgrounds/abstract-teal.png \
  --bg-opacity 0.20 \
  --output slide.webp
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--mermaid FILE` | — | Mermaid `.mmd` file to render |
| `--bg-prompt TEXT` | — | Titan prompt for background (requires AWS creds) |
| `--bg-image FILE` | — | Use existing image as background |
| `--bg-color HEX` | `#0d1117` | Solid background color |
| `--bg-opacity N` | `0.25` | Background visibility (0.0–1.0). Lower = more dimmed |
| `--title TEXT` | — | Title text at top |
| `--caption TEXT` | — | Caption text at bottom |
| `--text TEXT` | — | Large centered text overlay |
| `--scale N` | `0.85` | Diagram width as fraction of canvas |
| `--theme NAME` | `avalara-dark` | Mermaid theme from `scripts/mermaid-themes/` |
| `--width N` | `1408` | Output width |
| `--height N` | `768` | Output height |
| `--png` | — | Output PNG instead of WebP |

### Approach A: Mermaid Diagrams

Best for flowcharts, sequences, state machines, ER diagrams, mind maps. Embed theme in the `.mmd`:

```
%%{init: {'theme': 'base', 'themeVariables': {'background': 'transparent', 'mainBkg': '#1a3a4a', 'primaryColor': '#059bd2', 'primaryTextColor': '#f0f4f8', 'lineColor': '#7ab0c8', 'fontFamily': 'Helvetica Neue, Helvetica, Arial, sans-serif', 'fontSize': '24px'}}}%%
flowchart LR
    A["Frame"] --> B["Specify"] --> C["Generate"]
    style C fill:#fc6600,stroke:#e05800,color:#fff
```

Rules:
- `fontSize: '24px'` or larger (16px is too small for slides)
- `background: 'transparent'` required for compositing
- Explicit `style` for brand colors (orange `#fc6600`, navy `#025979`, teal `#059bd2`)
- `mmdc` renders via Puppeteer → system fonts work. Never use rsvg-convert for Mermaid (drops fonts).

### Approach B: Hand-Crafted SVG

Best for charts, proportional visuals, and layouts Mermaid can't handle. Write an SVG file with the Avalara palette:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="500" viewBox="0 0 1200 500">
  <style>
    text { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .title { font-size: 28px; fill: #f0f4f8; font-weight: 600; }
    .label { font-size: 18px; fill: #ffffff; font-weight: 500; }
  </style>
  <text x="600" y="40" text-anchor="middle" class="title">Chart Title</text>
  <rect x="200" y="70" width="200" height="315" rx="3" fill="#fc6600"/>
  <text x="300" y="230" text-anchor="middle" class="label">85%</text>
</svg>
```

Then composite manually:

```bash
# 1. Generate Titan background
AWS_PROFILE=trustfile scripts/bedrock-generate.sh \
  "Abstract dark navy gradient with subtle teal geometric lines" \
  bg.png --size 1408x768

# 2. Convert SVG → PNG
rsvg-convert -w 1200 diagram.svg -o diagram.png

# 3. Composite: dim bg + overlay diagram
magick bg.png -resize 1408x768! \
  \( +clone -fill "rgba(13,17,23,0.78)" -draw "rectangle 0,0 1408,768" \) -composite \
  \( diagram.png \) -gravity center -composite \
  output.webp
```

SVG color reference (Avalara brand):
- Navy: `#025979` — borders, dark fills, verification segments
- Orange: `#fc6600` — accents, implementation, CTAs
- Teal: `#059bd2` — primary nodes, framing segments
- Light text: `#f0f4f8` — labels on dark backgrounds
- Muted text: `#a0b8c8` — axis labels, secondary text

### Titan Background Prompts

Abstract only — never include text, charts, or diagrams in the prompt:

```
"Abstract dark navy gradient with subtle geometric patterns, minimal, moody"
"Deep teal and navy fluid waves, dark background, abstract, atmospheric"
"Dark gradient with soft glowing teal and orange particle dots, minimal"
"Subtle dark blueprint grid pattern, navy background, technical feel"
```

Titan prompt limit is 512 characters. Avoid words that trigger content filters ("dominated", etc.).

### Available Themes

Pre-built Mermaid themes in `scripts/mermaid-themes/`:
- **avalara-dark** — Navy/teal/orange on dark (default)
- **avalara-light** — Navy/teal/orange on light

## Manifest-Driven Batch Pipeline

For generating sets of images (e.g., course illustrations), use a JSON manifest:

```json
{
  "meta": {
    "style_guide": "...",
    "default_size": "1024x576",
    "format": "webp"
  },
  "images": [
    {
      "module": "01-intro",
      "block_id": "overview",
      "prompt": "A hub-and-spoke diagram...",
      "alt": "System overview diagram",
      "filename": "01-overview.webp",
      "status": "pending"
    }
  ]
}
```

Status lifecycle: `pending` → `generated` → `approved` → `integrated`

A complete batch generation script is available at [scripts/generate-images.ts](scripts/generate-images.ts). It supports:
- `--provider openai|gemini`
- `--id <block_id>` for single image
- `--module <id>` for one module
- `--batch <n>` for first n pending
- `--model <name>` to override default
- `--dry-run` to preview

## Format Handling

### Native WebP (OpenAI only)

OpenAI supports `output_format: "webp"` directly — no post-processing needed. Set `output_compression` (0-100) for quality control.

### Converting PNG to WebP (Gemini)

Gemini outputs PNG. Convert with `sharp`:

```typescript
import sharp from "sharp";

const webpBuffer = await sharp(pngBuffer).webp({ quality: 85 }).toBuffer();
```

Install: `npm i -D sharp`

### Transparent Backgrounds (OpenAI only)

```json
{ "background": "transparent", "output_format": "png" }
```

WebP also supports transparency, but PNG is more broadly compatible.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid or missing API key | Check env var is set |
| 400 Bad Request | Invalid size/params | Check supported sizes for the model |
| 429 Rate Limited | Too many requests | Add delay between requests (1-2s) |
| Content policy violation | Prompt triggered safety filter | Rephrase prompt, avoid people/violence |
| Empty response | Gemini returned no images | Check prompt language (English only for Imagen) |
| Invalid base64 (Bedrock) | Used `file://` instead of `fileb://` | Always use `fileb://` prefix for `--body` |
| ValidationException (Bedrock) | Malformed request body | Check JSON structure matches taskType schema |
| AccessDeniedException (Bedrock) | Model not enabled or wrong region | Enable model in Bedrock console; try us-east-1 |
| ExpiredTokenException (Bedrock) | STS credentials expired | Re-run `gimme-aws-creds` to refresh |

## Cost Estimates

### OpenAI (per image)

| Model | Low | Medium | High |
|-------|-----|--------|------|
| gpt-image-1-mini | — | — | ~$0.02 |
| gpt-image-1 | ~$0.02 | ~$0.07 | ~$0.19 |
| gpt-image-1.5 | ~$0.02 | ~$0.07 | ~$0.19 |

### Gemini (per image)

| Model | Price |
|-------|-------|
| Imagen 4 Fast | ~$0.02 |
| Imagen 4 | ~$0.04 |
| Imagen 4 Ultra | ~$0.06 |

For a 38-image course using OpenAI `gpt-image-1` at medium quality: ~$2.66 total.
