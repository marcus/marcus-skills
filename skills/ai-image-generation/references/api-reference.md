# API Reference — OpenAI, Gemini & AWS Bedrock Image Generation

## OpenAI Images API

### Endpoint

```
POST https://api.openai.com/v1/images/generations
```

### Request Headers

```
Authorization: Bearer $OPENAI_API_KEY
Content-Type: application/json
```

### Request Body

```json
{
  "model": "gpt-image-1",
  "prompt": "string (required)",
  "n": 1,
  "size": "1536x1024",
  "quality": "medium",
  "output_format": "webp",
  "output_compression": 85,
  "background": "opaque"
}
```

| Parameter | Type | Values | Default | Notes |
|-----------|------|--------|---------|-------|
| `model` | string | `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini` | — | Required. `gpt-image-1.5` is best quality. |
| `prompt` | string | — | — | Required. Max ~32k chars. |
| `n` | integer | 1+ | 1 | Number of images to generate. |
| `size` | string | `1024x1024`, `1536x1024`, `1024x1536`, `auto` | `auto` | `1536x1024` = landscape, `1024x1536` = portrait. |
| `quality` | string | `low`, `medium`, `high`, `auto` | `auto` | Higher = slower + more expensive. `hd`/`standard` are DALL-E only. |
| `output_format` | string | `png`, `jpeg`, `webp` | `png` | GPT Image models only. |
| `output_compression` | integer | 0-100 | 100 | Only for `webp` and `jpeg`. Lower = smaller file. |
| `background` | string | `transparent`, `opaque`, `auto` | `auto` | Transparent only works with `png` and `webp`. |

### Response

```json
{
  "created": 1234567890,
  "data": [
    {
      "b64_json": "<base64-encoded-image-data>",
      "revised_prompt": "The model's interpretation of your prompt"
    }
  ]
}
```

Response always uses `b64_json` (no URL option for GPT Image models).

### Streaming (optional)

```json
{
  "model": "gpt-image-1",
  "prompt": "...",
  "stream": true,
  "partial_images": 2
}
```

Stream events:
- `image_generation.partial_image` — intermediate result (`partial_image_index`, `b64_json`)
- Final image is the last event

### Editing (existing images)

```
POST https://api.openai.com/v1/images/edits
```

Accepts `image` (file upload or array of files), optional `mask`, and `prompt`. Same model/quality/format params.

---

## Gemini Imagen API

### Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:predict
```

Models:
- `imagen-4.0-generate-001` (flagship)
- Other Imagen variants may be available

### Request Headers

```
x-goog-api-key: $GEMINI_API_KEY
Content-Type: application/json
```

### Request Body

```json
{
  "instances": [
    {
      "prompt": "string (required)"
    }
  ],
  "parameters": {
    "sampleCount": 1,
    "aspectRatio": "16:9",
    "personGeneration": "dont_allow"
  }
}
```

| Parameter | Type | Values | Default | Notes |
|-----------|------|--------|---------|-------|
| `instances[].prompt` | string | — | — | Required. English only. |
| `parameters.sampleCount` | integer | 1-4 | 4 | Images per request. |
| `parameters.aspectRatio` | string | `1:1`, `3:4`, `4:3`, `9:16`, `16:9` | `1:1` | — |
| `parameters.personGeneration` | string | `dont_allow`, `allow_adult`, `allow_all` | `allow_adult` | Controls people in output. |

### Response

```json
{
  "generatedImages": [
    {
      "image": {
        "imageBytes": "<base64-encoded-image-data>"
      }
    }
  ]
}
```

Output format is PNG. Convert to WebP client-side if needed.

### Vertex AI variant

If using Vertex AI instead of the Gemini API, the endpoint and response differ:

```
POST https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:predict
```

Response uses `predictions[].bytesBase64Encoded` instead of `generatedImages[].image.imageBytes`.

Auth uses OAuth2 / service account instead of API key.

---

## Size Mapping Reference

When your manifest specifies dimensions and you need to map to API params:

### OpenAI

| Desired aspect | API `size` param |
|---------------|-----------------|
| 1:1 | `1024x1024` |
| 3:2 landscape | `1536x1024` |
| 2:3 portrait | `1024x1536` |
| Auto | `auto` |

### Gemini

| Desired aspect | API `aspectRatio` param |
|---------------|------------------------|
| 1:1 | `1:1` |
| 4:3 landscape | `4:3` |
| 3:4 portrait | `3:4` |
| 16:9 wide | `16:9` |
| 9:16 tall | `9:16` |

---

## AWS Bedrock Titan Image Generator v2

### Invocation

```
aws bedrock-runtime invoke-model \
  --region us-east-1 \
  --model-id amazon.titan-image-generator-v2:0 \
  --content-type application/json \
  --accept application/json \
  --body fileb://request.json \
  response.json
```

Auth: AWS IAM credentials (profile, role, SSO, or environment variables). No separate API key needed.

**Critical**: Use `fileb://` (not `file://`) for the `--body` parameter. The CLI expects binary blob format.

### Request Body — TEXT_IMAGE

```json
{
  "taskType": "TEXT_IMAGE",
  "textToImageParams": {
    "text": "string (required, max 512 chars)",
    "negativeText": "string (optional, max 512 chars)"
  },
  "imageGenerationConfig": {
    "quality": "standard",
    "numberOfImages": 1,
    "height": 1024,
    "width": 1024,
    "cfgScale": 8.0,
    "seed": 0
  }
}
```

| Parameter | Type | Values | Default | Notes |
|-----------|------|--------|---------|-------|
| `taskType` | string | `TEXT_IMAGE`, `IMAGE_VARIATION`, `INPAINTING`, `OUTPAINTING`, `COLOR_GUIDED_GENERATION`, `BACKGROUND_REMOVAL` | — | Required. |
| `textToImageParams.text` | string | — | — | Required. Max 512 chars. |
| `textToImageParams.negativeText` | string | — | — | What to exclude from the image. Max 512 chars. |
| `imageGenerationConfig.quality` | string | `standard`, `premium` | `standard` | Premium produces higher detail. |
| `imageGenerationConfig.numberOfImages` | integer | 1-5 | 1 | Images per request. |
| `imageGenerationConfig.height` | integer | 320-1408 | 1024 | Must be divisible by 64. Max 1408 on longest side. |
| `imageGenerationConfig.width` | integer | 320-1408 | 1024 | Must be divisible by 64. Max 1408 on longest side. |
| `imageGenerationConfig.cfgScale` | float | 1.1-10.0 | 8.0 | How closely to follow the prompt. Higher = more literal. |
| `imageGenerationConfig.seed` | integer | 0-2147483646 | random | For reproducible results. |

### Request Body — IMAGE_VARIATION (image conditioning)

```json
{
  "taskType": "TEXT_IMAGE",
  "textToImageParams": {
    "text": "A modern building in the same style",
    "conditionImage": "<base64-encoded-image>",
    "controlMode": "CANNY_EDGE",
    "controlStrength": 0.7
  },
  "imageGenerationConfig": {
    "quality": "standard",
    "numberOfImages": 1,
    "height": 1024,
    "width": 1024
  }
}
```

| Parameter | Type | Values | Notes |
|-----------|------|--------|-------|
| `conditionImage` | string (base64) | — | Reference image for conditioning. |
| `controlMode` | string | `CANNY_EDGE`, `SEGMENTATION` | Edge detection or segmentation map. |
| `controlStrength` | float | 0.0-1.0 | Weight given to condition image. Default 0.7. |

### Response

```json
{
  "images": [
    "<base64-encoded-PNG>"
  ]
}
```

Output is always base64-encoded PNG. Decode and write to file:

```python
import json, base64
with open("response.json") as f:
    data = json.load(f)
with open("output.png", "wb") as f:
    f.write(base64.b64decode(data["images"][0]))
```

### Supported Sizes

Height and width must be divisible by 64. The longest side cannot exceed 1408. Common sizes:

| Aspect | Width | Height |
|--------|-------|--------|
| 1:1 | 1024 | 1024 |
| 4:3 landscape | 1408 | 1024 |
| 3:4 portrait | 1024 | 1408 |
| 16:9 wide | 1408 | 768 |
| 9:16 tall | 768 | 1408 |

### Region Availability

Model `amazon.titan-image-generator-v2:0` is available in: `us-east-1`, `us-west-2`, `eu-west-1`, `ap-northeast-1`. Check the [Bedrock model access page](https://console.aws.amazon.com/bedrock/home#/modelaccess) for your account.

### Avalara Trustfile Access

```bash
# Authenticate via Okta (writes to ~/.aws/credentials [trustfile] profile)
gimme-aws-creds --profile trustfile-okta-admin

# Use the trustfile profile for all AWS commands
export AWS_PROFILE=trustfile
# or prefix each command: AWS_PROFILE=trustfile aws ...
```

The `trustfile-okta-admin` profile is configured in `~/.okta_aws_login_config`. Session duration is 1 hour. MFA is TOTP (authenticator app).

---

## Rate Limits & Best Practices

- Add 1-2 second delay between sequential requests
- Both APIs return base64 — decode and write to disk immediately
- OpenAI: batch with `n` param to reduce request count
- Gemini: batch with `sampleCount` (max 4) to get variations
- Save the manifest status after each successful generation so you can resume if interrupted
- Use `--dry-run` to preview prompts before spending API credits
