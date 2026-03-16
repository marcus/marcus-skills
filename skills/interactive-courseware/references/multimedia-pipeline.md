# Multimedia Pipeline Reference

Complete pipeline for generating course multimedia assets with AI.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multimedia Generation Pipeline                 │
│                                                                   │
│  content.json ──┬──▶ Narration Pipeline ──▶ audio/*.mp3          │
│                 │                                                  │
│                 ├──▶ Image Pipeline ──────▶ images/*.webp         │
│                 │                                                  │
│                 ├──▶ Video Pipeline ──────▶ video/*.mp4           │
│                 │                                                  │
│                 ├──▶ Music Pipeline ──────▶ music/*.mp3           │
│                 │                                                  │
│                 ├──▶ SFX Pipeline ────────▶ sfx/*.mp3             │
│                 │                                                  │
│                 └──▶ Diagram Pipeline ────▶ diagrams/*.svg        │
│                                                                   │
│  All paths written back into content.json for the course player  │
└─────────────────────────────────────────────────────────────────┘
```

## Narration Pipeline

Reference: **`text-to-speech` skill** for ElevenLabs API details.

### Voice Assignment Strategy

Assign consistent voices to roles across the entire course:

```json
{
  "voice_config": {
    "narrator": {
      "voice_id": "JBFqnCBsd6RMkjVDRZzb",
      "model": "eleven_multilingual_v2",
      "description": "George — authoritative, clear, professional"
    },
    "learner_character": {
      "voice_id": "EXAVITQu4vr4xnSDxMaL",
      "model": "eleven_multilingual_v2",
      "description": "Sarah — relatable, warm, conversational"
    },
    "mentor_character": {
      "voice_id": "onwK4e9ZLuTAKqWW03F9",
      "model": "eleven_multilingual_v2",
      "description": "Daniel — experienced, reassuring"
    },
    "system_feedback": {
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "model": "eleven_flash_v2_5",
      "description": "Rachel — quick, friendly feedback"
    }
  }
}
```

### Batch Generation Script

```python
#!/usr/bin/env python3
"""Generate all narration audio for a course module."""

import json
import os
import sys
from pathlib import Path
from elevenlabs import ElevenLabs

client = ElevenLabs()

def load_voice_config(course_dir: str) -> dict:
    config_path = Path(course_dir) / "content" / "shared" / "voice-config.json"
    with open(config_path) as f:
        return json.load(f)["voice_config"]

def extract_narration_blocks(module_path: str) -> list[dict]:
    """Extract all blocks that need narration from a module."""
    with open(module_path) as f:
        module = json.load(f)

    blocks = []
    for i, block in enumerate(module.get("blocks", [])):
        if "narration_text" in block:
            blocks.append({
                "index": i,
                "text": block["narration_text"],
                "voice_role": block.get("voice_role", "narrator"),
                "block_type": block["type"],
            })
        # Also extract character dialogue
        if block.get("type") == "dialogue":
            for j, line in enumerate(block.get("lines", [])):
                blocks.append({
                    "index": f"{i}-{j}",
                    "text": line["text"],
                    "voice_role": line["character"],
                    "block_type": "dialogue",
                })
    return blocks

def generate_narration(
    blocks: list[dict],
    voice_config: dict,
    output_dir: str
) -> dict[str, str]:
    """Generate audio for all blocks, return mapping of index to filename."""
    os.makedirs(output_dir, exist_ok=True)
    path_map = {}

    for block in blocks:
        voice_role = block["voice_role"]
        voice = voice_config.get(voice_role, voice_config["narrator"])

        filename = f"{block['index']:>03}-{block['block_type']}.mp3"
        output_path = os.path.join(output_dir, filename)

        # Skip if already generated (idempotent)
        if os.path.exists(output_path):
            print(f"  Skipping {filename} (exists)")
            path_map[str(block["index"])] = filename
            continue

        print(f"  Generating {filename} ({len(block['text'])} chars, voice: {voice_role})")

        audio = client.text_to_speech.convert(
            text=block["text"],
            voice_id=voice["voice_id"],
            model_id=voice["model"],
        )

        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        path_map[str(block["index"])] = filename

    return path_map

def update_module_paths(module_path: str, path_map: dict[str, str], media_prefix: str):
    """Write audio paths back into content.json."""
    with open(module_path) as f:
        module = json.load(f)

    for i, block in enumerate(module.get("blocks", [])):
        key = str(i)
        if key in path_map:
            block["narration"] = f"{media_prefix}/{path_map[key]}"

    with open(module_path, "w") as f:
        json.dump(module, f, indent=2)

if __name__ == "__main__":
    course_dir = sys.argv[1]
    module_dir = sys.argv[2] if len(sys.argv) > 2 else None

    voice_config = load_voice_config(course_dir)
    content_dir = Path(course_dir) / "content" / "modules"

    modules = [module_dir] if module_dir else sorted(os.listdir(content_dir))

    for module_name in modules:
        module_path = content_dir / module_name / "content.json"
        if not module_path.exists():
            continue

        print(f"\nProcessing module: {module_name}")
        output_dir = str(Path(course_dir) / "public" / "media" / "audio" / module_name)

        blocks = extract_narration_blocks(str(module_path))
        if not blocks:
            print("  No narration blocks found")
            continue

        path_map = generate_narration(blocks, voice_config, output_dir)
        update_module_paths(str(module_path), path_map, f"media/audio/{module_name}")
        print(f"  Generated {len(path_map)} audio files")
```

### Narration Best Practices

| Rule | Why |
|------|-----|
| Never narrate on-screen text verbatim | Redundancy principle — cognitive overload |
| Narration complements visuals | Modality principle — audio for graphics |
| Chunk to ~150 words per segment | Segmenting principle — learner-paced |
| Use conversational tone ("you'll notice...") | Personalization principle — better recall |
| Make narration optional (mute control) | Learner agency — some prefer reading |
| Match voice persona to course brand | Consistency — builds trust |
| Vary pacing naturally | Engagement — monotone kills attention |

---

## Image Generation Pipeline

### Illustration Strategy

```python
#!/usr/bin/env python3
"""Generate course illustrations using OpenAI's image generation."""

import json
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI()

# Style guide for consistent imagery
STYLE_GUIDE = """
Style: Modern flat illustration with subtle gradients.
Color palette: Navy (#1a1a2e), teal (#16213e), coral (#e94560), warm white (#f5f5f5).
Character style: Diverse, professional, slightly stylized proportions.
Environment: Clean, minimal backgrounds with subtle geometric patterns.
Mood: Professional but approachable. Not corporate-sterile, not casual.
Avoid: Stock photo aesthetics, overly detailed realism, generic clip art.
"""

def generate_illustration(
    description: str,
    context: str,
    output_path: str,
    size: str = "1024x1024"
):
    """Generate a course illustration."""
    prompt = f"""Create an illustration for an online course.

{STYLE_GUIDE}

Scene: {description}
Course context: {context}

The illustration should feel like it belongs in a premium, modern learning experience.
No text in the image."""

    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size=size,
    )

    # Save image
    import urllib.request
    urllib.request.urlretrieve(response.data[0].url, output_path)
    print(f"  Generated: {output_path}")

def generate_module_images(module_path: str, output_dir: str):
    """Generate all images for a module based on content.json."""
    with open(module_path) as f:
        module = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    course_context = module.get("title", "Online course")

    for i, block in enumerate(module.get("blocks", [])):
        if "illustration_prompt" not in block:
            continue

        filename = f"{i:03d}-{block['type']}.webp"
        output_path = os.path.join(output_dir, filename)

        if os.path.exists(output_path):
            print(f"  Skipping {filename} (exists)")
            continue

        generate_illustration(
            description=block["illustration_prompt"],
            context=course_context,
            output_path=output_path,
        )

        block["image"] = f"media/images/{os.path.basename(output_dir)}/{filename}"

    with open(module_path, "w") as f:
        json.dump(module, f, indent=2)
```

### Diagram Generation

Reference: **`technical-diagrams` skill** for Mermaid.js syntax.

```python
# Generate Mermaid diagrams from content descriptions
def generate_diagram(description: str, diagram_type: str = "flowchart") -> str:
    """Use Claude to generate a Mermaid diagram from a description."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Generate a Mermaid.js {diagram_type} diagram for: {description}\n\nReturn ONLY the Mermaid code, no explanation."
        }]
    )
    return response.content[0].text
```

---

## Music and Sound Effects Pipeline

Reference: **`music` skill** and **`sound-effects` skill** for ElevenLabs API details.

### Course Soundtrack Generation

```python
#!/usr/bin/env python3
"""Generate course soundtrack and sound effects."""

from elevenlabs import ElevenLabs
import json
import os

client = ElevenLabs()

def generate_course_audio(course_dir: str):
    config_path = os.path.join(course_dir, "content", "shared", "audio-config.json")

    with open(config_path) as f:
        config = json.load(f)

    music_dir = os.path.join(course_dir, "public", "media", "music")
    sfx_dir = os.path.join(course_dir, "public", "media", "sfx")
    os.makedirs(music_dir, exist_ok=True)
    os.makedirs(sfx_dir, exist_ok=True)

    # Background music tracks
    for track in config.get("music_tracks", []):
        output_path = os.path.join(music_dir, f"{track['name']}.mp3")
        if os.path.exists(output_path):
            continue

        print(f"Generating music: {track['name']}")
        audio = client.music.compose(
            prompt=track["prompt"],
            music_length_ms=track.get("duration_ms", 30000),
        )
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

    # Sound effects
    for sfx in config.get("sound_effects", []):
        output_path = os.path.join(sfx_dir, f"{sfx['name']}.mp3")
        if os.path.exists(output_path):
            continue

        print(f"Generating SFX: {sfx['name']}")
        audio = client.text_to_sound_effects.convert(
            text=sfx["prompt"],
            duration_seconds=sfx.get("duration", 2.0),
        )
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
```

### Audio Config Template

```json
{
  "music_tracks": [
    {
      "name": "ambient-learning",
      "prompt": "Calm minimal ambient electronic with soft piano chords, suitable as quiet background for reading and studying, gentle and unobtrusive, 90 BPM",
      "duration_ms": 60000
    },
    {
      "name": "scenario-tension",
      "prompt": "Tense suspenseful underscore with subtle strings and low rhythmic pulse, building quiet anticipation, corporate thriller atmosphere",
      "duration_ms": 30000
    },
    {
      "name": "achievement-fanfare",
      "prompt": "Short bright triumphant fanfare with warm brass and ascending melody, celebration and accomplishment, energetic and positive",
      "duration_ms": 5000
    },
    {
      "name": "reflection-interlude",
      "prompt": "Gentle acoustic guitar with soft ambient pad, contemplative and warm, for thoughtful review moments, peaceful",
      "duration_ms": 30000
    },
    {
      "name": "intro-theme",
      "prompt": "Modern corporate intro theme, confident and forward-looking, clean electronic with light percussion, professional and engaging",
      "duration_ms": 15000
    }
  ],
  "sound_effects": [
    { "name": "correct", "prompt": "Short bright positive chime, digital confirmation sound, satisfying", "duration": 1.5 },
    { "name": "incorrect", "prompt": "Soft low gentle buzz, subtle error notification, not harsh", "duration": 1.5 },
    { "name": "click", "prompt": "Subtle soft click, tactile button press, minimal", "duration": 0.5 },
    { "name": "whoosh-transition", "prompt": "Quick smooth whoosh, left to right sweep, clean transition", "duration": 1.0 },
    { "name": "reveal", "prompt": "Gentle shimmer sparkle sound, magical reveal, light and airy", "duration": 2.0 },
    { "name": "complete-module", "prompt": "Warm achievement completion sound, rewarding bell chime with subtle sparkle", "duration": 2.5 },
    { "name": "notification", "prompt": "Gentle notification ping, soft and pleasant, attention-getting without alarming", "duration": 1.0 },
    { "name": "typing", "prompt": "Quick mechanical keyboard typing burst, 3-4 keystrokes", "duration": 1.5 },
    { "name": "email-arrive", "prompt": "Soft email notification sound, modern and clean", "duration": 1.0 },
    { "name": "ambient-office", "prompt": "Quiet office ambience, distant keyboard typing, soft ventilation hum, occasional muffled conversation", "duration": 10.0 }
  ]
}
```

---

## Video Generation Pipeline

Reference: **`remotion` skill** for programmatic video with React.

### Remotion Course Video Template

```tsx
// video/ExplainerVideo.tsx
import { AbsoluteFill, Audio, Img, Sequence, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

interface ExplainerProps {
  title: string;
  sections: Array<{
    text: string;
    narrationSrc: string;
    imageSrc: string;
    durationInFrames: number;
  }>;
  musicSrc: string;
}

export const ExplainerVideo: React.FC<ExplainerProps> = ({ title, sections, musicSrc }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  let frameOffset = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: '#1a1a2e' }}>
      {/* Background music at low volume */}
      <Audio src={musicSrc} volume={0.15} />

      {/* Title card */}
      <Sequence durationInFrames={fps * 3}>
        <AbsoluteFill style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <h1 style={{
            color: '#f5f5f5',
            fontSize: 72,
            opacity: interpolate(frame, [0, fps * 0.5, fps * 2.5, fps * 3], [0, 1, 1, 0]),
          }}>
            {title}
          </h1>
        </AbsoluteFill>
      </Sequence>

      {/* Content sections */}
      {sections.map((section, i) => {
        const start = fps * 3 + frameOffset;
        frameOffset += section.durationInFrames;

        return (
          <Sequence key={i} from={start} durationInFrames={section.durationInFrames}>
            <AbsoluteFill style={{ display: 'flex', padding: 80 }}>
              <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
                <p style={{ color: '#f5f5f5', fontSize: 36, lineHeight: 1.6 }}>
                  {section.text}
                </p>
              </div>
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Img src={section.imageSrc} style={{ maxWidth: '90%', borderRadius: 12 }} />
              </div>
            </AbsoluteFill>
            <Audio src={section.narrationSrc} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
```

### AI Avatar Integration (HeyGen/Synthesia)

For talking-head style content with AI presenters:

```python
# Generate avatar video via HeyGen API
import requests

def generate_avatar_video(script: str, avatar_id: str, voice_id: str) -> str:
    """Generate an AI avatar video. Returns video URL when complete."""
    response = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers={"X-Api-Key": os.environ["HEYGEN_API_KEY"]},
        json={
            "video_inputs": [{
                "character": {"type": "avatar", "avatar_id": avatar_id},
                "voice": {"type": "text", "input_text": script, "voice_id": voice_id},
                "background": {"type": "color", "value": "#1a1a2e"},
            }],
            "dimension": {"width": 1920, "height": 1080},
        }
    )
    video_id = response.json()["data"]["video_id"]

    # Poll for completion
    while True:
        status = requests.get(
            f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
            headers={"X-Api-Key": os.environ["HEYGEN_API_KEY"]},
        ).json()

        if status["data"]["status"] == "completed":
            return status["data"]["video_url"]
        elif status["data"]["status"] == "failed":
            raise RuntimeError(f"Video generation failed: {status}")

        import time
        time.sleep(10)
```

---

## Full Pipeline Orchestration

### Master Build Script

```python
#!/usr/bin/env python3
"""Complete multimedia pipeline for a course."""

import argparse
import subprocess
from pathlib import Path

def run_pipeline(course_dir: str, modules: list[str] | None = None):
    course = Path(course_dir)
    content_dir = course / "content" / "modules"

    if modules is None:
        modules = sorted(d.name for d in content_dir.iterdir() if d.is_dir())

    print(f"Processing {len(modules)} modules...")

    for module in modules:
        module_path = content_dir / module / "content.json"
        if not module_path.exists():
            print(f"Skipping {module} (no content.json)")
            continue

        print(f"\n{'='*60}")
        print(f"Module: {module}")
        print(f"{'='*60}")

        # 1. Generate narration
        print("\n--- Narration ---")
        subprocess.run([
            "python", "scripts/generate-narration.py",
            str(course_dir), module
        ], check=True)

        # 2. Generate images
        print("\n--- Images ---")
        subprocess.run([
            "python", "scripts/generate-images.py",
            str(course_dir), module
        ], check=True)

        # 3. Generate diagrams (Mermaid → SVG)
        print("\n--- Diagrams ---")
        subprocess.run([
            "python", "scripts/generate-diagrams.py",
            str(course_dir), module
        ], check=True)

    # 4. Generate course-wide audio (music + SFX)
    print("\n--- Music & Sound Effects ---")
    subprocess.run([
        "python", "scripts/generate-audio.py",
        str(course_dir)
    ], check=True)

    # 5. Optimize all media assets
    print("\n--- Asset Optimization ---")
    subprocess.run(["npm", "run", "optimize-media"], cwd=str(course_dir), check=True)

    print("\n✓ Pipeline complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("course_dir")
    parser.add_argument("--modules", nargs="*")
    args = parser.parse_args()
    run_pipeline(args.course_dir, args.modules)
```

### Asset Optimization

```json
{
  "scripts": {
    "optimize-media": "tsx scripts/optimize-media.ts",
    "optimize-images": "sharp-cli --input 'public/media/images/**/*.{png,jpg}' --output 'public/media/images/' --format webp --quality 80",
    "optimize-audio": "ffmpeg-batch --input 'public/media/audio/**/*.mp3' --bitrate 128k",
    "generate-sprites": "svg-sprite --mode symbol --dest public/media 'public/media/icons/**/*.svg'"
  }
}
```

### Package Size Targets

| Asset Type | Target | Strategy |
|-----------|--------|----------|
| Total SCORM package | < 50 MB | LMS upload limits |
| Initial page load | < 3 MB | Code splitting, lazy media |
| Images | WebP, < 200 KB each | sharp compression |
| Audio narration | 128 kbps MP3 | ffmpeg |
| Background music | 96 kbps MP3 | Lower quality acceptable for background |
| Sound effects | 64 kbps MP3 | Short duration, lower quality fine |
| Video | Progressive MP4 or HLS | Lazy loaded, streamed |
