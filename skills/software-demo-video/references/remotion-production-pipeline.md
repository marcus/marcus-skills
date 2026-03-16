# Remotion Production Pipeline

A complete, automated pipeline for producing software demo videos using Remotion. Covers narration generation with word-level sync, composition timing, audit tooling, and component patterns. Derived from building the Planner demo video system.

---

## Per-Section Audio Architecture

**This is the single most important architectural decision.** Never use a single concatenated narration file played as one audio track. Instead, generate individual audio files per script section, each pinned to their exact composition frame.

### Why

When ElevenLabs (or any TTS engine) generates a concatenated narration file, it inserts natural inter-section pauses of varying length (typically 2-4 seconds each). These pauses accumulate. In a 10-section video, the concatenated file can run 20-35 seconds longer than the sum of individual section durations. If the composition is timed to individual section lengths, the concatenated audio drifts progressively -- by the final sections, the viewer hears narration for one topic while watching visuals for a completely different topic.

### How

```tsx
// WRONG: Single audio track with cumulative drift
<Sequence from={S.hook.start}>
  <Audio src={staticFile("narration-full.mp3")} volume={1} />
</Sequence>

// RIGHT: Per-section audio, each pinned to its section start
<Sequence from={S.hook.start} durationInFrames={S.hook.dur}>
  <Audio src={staticFile("narration-00-hook.mp3")} volume={1} />
</Sequence>
<Sequence from={S.tease.start} durationInFrames={S.tease.dur}>
  <Audio src={staticFile("narration-01-tease.mp3")} volume={1} />
</Sequence>
// ... one per section
```

Each section's audio starts exactly when its visual section starts. No cumulative drift. If one section's narration runs slightly long or short, it does not affect any other section.

---

## Narration with Timestamps

Use the ElevenLabs `/v1/text-to-speech/{voice_id}/with-timestamps` endpoint instead of the plain TTS endpoint. It returns identical audio plus character-level alignment data.

### API Call

```typescript
const response = await fetch(
  `${BASE_URL}/text-to-speech/${voiceId}/with-timestamps`,
  {
    method: "POST",
    headers: {
      "xi-api-key": API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text: sectionText,
      model_id: "eleven_multilingual_v2",
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.75,
        style: 0.3,
        use_speaker_boost: true,
      },
    }),
  }
);

const data: ElevenLabsTimestampResponse = await response.json();
// data.audio_base64 — the audio as base64
// data.alignment.characters — array of characters
// data.alignment.character_start_times_seconds — start time per character
// data.alignment.character_end_times_seconds — end time per character
```

### Aggregation

Character-level data is too granular for composition use. Aggregate to word-level and sentence-level:

- **Word-level**: Group characters between whitespace boundaries. Word start = first character's start time. Word end = last character's end time. Convert to frames: `frame = Math.round(seconds * fps)`.
- **Sentence-level**: Group words between sentence-ending punctuation (`.`, `!`, `?`). Sentence start = first word's start time. Sentence end = last word's end time. Include word count for pacing analysis.

This data enables automated composition timing (section durations derived from measured audio) and precise visual sync (overlays timed to specific words or sentences).

---

## The Sync Pipeline

```
script.md --> narrate-sync.ts --> sync-manifest.json --> composition S constants --> audit-sync.ts --> render
```

Each step is automated. Script changes flow through to timing automatically.

### Step 1: Script (script.md)

Markdown format with sections. Each section has narration text, visual direction, and overlay specs:

```markdown
## Section Name (0:00-0:15)

**Narration:**
The spoken words for this section.

**Visual:** What appears on screen.

**Overlay:** Text overlays and callouts.
```

### Step 2: Narrate with Sync (narrate-sync.ts)

Reads `script.md`, extracts narration blocks, calls ElevenLabs with-timestamps API per section, and produces:

- Per-section MP3 files: `narration-00-hook.mp3`, `narration-01-tease.mp3`, etc.
- A concatenated `narration-full.mp3` (for convenience/preview only -- never use as the composition audio source)
- A `sync-manifest.json` with comprehensive timing data

### Step 3: Sync Manifest (sync-manifest.json)

```json
{
  "generated": "2026-03-16T...",
  "fps": 30,
  "voice_id": "...",
  "sections": [
    {
      "index": 0,
      "name": "Hook",
      "file": "narration-00-hook.mp3",
      "duration_seconds": 14.02,
      "duration_frames": 421,
      "text": "The spoken narration text...",
      "words": [
        {
          "word": "The",
          "start_seconds": 0.05,
          "end_seconds": 0.18,
          "start_frame": 2,
          "end_frame": 5
        }
      ],
      "sentences": [
        {
          "text": "The spoken narration text.",
          "start_seconds": 0.05,
          "end_seconds": 3.42,
          "start_frame": 2,
          "end_frame": 103,
          "word_count": 5
        }
      ],
      "composition_timing": {
        "start_frame": 90,
        "duration_frames": 436,
        "padding_frames": 15
      }
    }
  ],
  "total_narration_seconds": 222.13,
  "total_composition_frames": 7150
}
```

### Step 4: Composition S Constants

The manifest's `composition_timing` values map directly to the composition's section timing object:

```typescript
// Section timing formula: ceil(narration_seconds * fps) + padding_frames
const S = {
  intro:           { start: 0,    dur: 90 },       // 3s intro card (no narration)
  hook:            { start: 90,   dur: 436 },       // 14.02s -> 421f + 15f pad
  tease:           { start: 526,  dur: 309 },       // 9.80s -> 294f + 15f pad
  problemSolution: { start: 835,  dur: 1065 },      // 34.97s -> 1050f + 15f pad
  // ...
} as const;
```

**Section timing formula**: `ceil(narration_seconds * fps) + 15 frames padding`. Never guess durations. Always derive from measured audio. The 15-frame padding (~0.5s at 30fps) provides breathing room at section boundaries so the narration finishes before the visual transition fires.

### Step 5: Audit (audit-sync.ts)

Parses both the sync manifest and the composition source code, then checks for:

- **Dead frames**: Gaps in the timeline where no visual content is on screen
- **Narration overruns**: Sections where narration audio is longer than the visual section
- **Visual gaps**: Missing content between section boundaries
- **Section overlaps**: Two sections occupying the same frame range

Outputs a human-readable report and an optional JSON report for agent consumption. Produces a sync score (1-10) summarizing overall alignment quality. Saves to `reviews/sync-audit.md`.

Usage:
```bash
npx tsx audit-sync.ts           # human-readable report
npx tsx audit-sync.ts --json    # machine-readable report
npx tsx audit-sync.ts --fix     # output corrected S constants
```

### Step 6: Render

```bash
npx remotion render CompositionName output.mp4 --codec h264 --crf 18
```

---

## Remotion Component Patterns

Effective patterns discovered during production. These are reusable across video projects.

### ZoomPan (Ken Burns Effect)

Subtle movement on static screenshots to keep them from feeling dead. **Critical calibration**: scale 1.0 to 1.02 or 1.03, never more. Pan values similarly restrained (x: -12 to +5, y: -6 to +3). Use `Easing.inOut(Easing.cubic)` for smooth motion. The effect should be nearly imperceptible -- viewers should not consciously notice the movement, but would notice if it were absent.

**Common bug -- double zoom**: Do not wrap a `BrowserFrame` with `animated={true}` inside a `ZoomPan` component. Both apply their own scale transform, compounding to ~6% zoom instead of the intended ~3%. Pick one layer of zoom.

### FeatureCallout (Glassmorphism Cards)

Floating cards with glass-morphism effect for highlighting features on screenshots. Key properties:

- Glass background: `rgba(20, 20, 35, 0.75)` with `backdrop-filter: blur(24px)`
- Multi-layer shadow: `0 16px 48px` outer + `0 0 0 1px` inner outline + `inset 0 1px 0` top highlight
- Three animation modes: slide-in (directional), pop, fade
- Spring-driven entry with automatic 12-frame exit fade
- Gradient accent bar at top tied to theme accent color
- Max width constraint (360px) to prevent text sprawl

### SplitReveal (Before/After Comparison)

Side-by-side comparison with animated divider. The divider has a spring-weighted motion (mass: 1.2) that makes it feel heavy and deliberate. Includes handle with chevron arrows, pulsing glow on the divider line, and "Before"/"After" labels that fade in sync with their panels.

### SceneTransition

Four distinct transition types, each mapped to narrative purpose:

| Type | Visual | Best For |
|------|--------|----------|
| **morph** | Scale-down + opacity fade with gradient overlay | Neutral transitions, text-focused sections |
| **iris** | Radial reveal from center outward with colored ring | Dramatic reveals, comparison sections |
| **slide-reveal** | Horizontal wipe with colored leading edge and glow | Forward momentum, demo section entries |
| **scale-fade** | Outgoing content scales up while fading | "Pulling away" feel, section closers |

Transition durations: iris/morph get 18-20 frames, slide-reveal/scale-fade get 12-15 frames. Variety should be directorial (mapped to narrative intent), not random.

### TypingAnimation

Simulates user input in a chat/code/terminal context. Three style presets with distinct visual identities. Includes blinking cursor after typing completes (every 15 frames) and a send button that activates when characters appear. Use to show the user's side of a product interaction.

### DifferentiatorsStack

Numbered feature list with spring-animated staggered entry. Vertical flex layout with gap, numbered badges (indigo gradient), and per-item spring animations. Use for "3 things that set this apart" sections. Stagger item appearance to align with the narrator's "First," "Second," "Third" cues.

### BrowserFrame

macOS browser chrome wrapper for screenshots. Traffic light dots, URL bar, rounded corners, box shadow for depth. Supports fade-in, zoom-in, and slide-up animations. Dark mode prop switches all sub-elements.

### IntroSequence / OutroSequence

Animated intro card and end card. Spring-physics title animations, subtle grid pattern background (60px grid, 2% white opacity), accent line animation. OutroSequence includes CTA button and URL text.

### TextOverlay

Versatile text-on-screen component with five style presets (heading, subtitle, caption, code, callout), five position presets, four animation modes (fade, slide-up, typewriter with blinking cursor, none), optional background with backdrop blur.

### ProgressBar

Video progress indicator at top or bottom of frame. Uses z-index above all other content. Shows overall video progress.

---

## Common Bugs and Pitfalls

### Double Zoom
Do not use `ZoomPan` wrapper AND `BrowserFrame animated={true}` simultaneously. Both apply scale transforms, compounding to ~6% instead of ~3%. Pick one.

### CTA-Outro Overlap
When crossfading from CTA to Outro, limit overlap to max 30 frames (~1 second). If the OutroSequence has an opaque background, the CTA content vanishes abruptly rather than fading. Coordinate the CTA's exit fade with the Outro's entry.

### TeaseCard Brightness
Preview images in tease/flash-cut sections should have brightness at 0.7-0.8. Below 0.6 with blur, the screenshots provide no visual context and the labels carry the entire communicative burden. Never add more than 0.5px blur to preview images.

### Narration Regex
The script format (`script.md`) evolves across iterations. The parser regex must handle both `## [Section Name]` and `## Section Name (timecode)` formats. Build the parser to match any `## ` header followed by a `**Narration:**` block, regardless of header format. A parser that silently finds zero sections is worse than one that crashes.

### Concatenated Audio Drift
Even after switching to per-section audio, keep the concatenated `narration-full.mp3` for preview/listening purposes only. Never reference it in the composition's `<Audio>` elements.

### Spring Physics Consistency
Use consistent spring parameters across similar components: `{ damping: 100, stiffness: 200 }` for title/heading animations, `{ damping: 80, stiffness: 200 }` for card entries, `{ damping: 60, stiffness: 120, mass: 1.2 }` for heavy/dramatic elements. Heavier mass for larger elements, higher damping for elements that should feel decisive.

### Font Stack
Use a consistent font stack across all components: Inter/SF Pro Display for display text, Inter/SF Pro Text for body, JetBrains Mono/SF Mono for code and URLs. Extract to a shared theme file to prevent drift.

### Z-Index Hierarchy
Establish a clear z-index stack: ProgressBar (200) > SceneTransition (100) > FeatureCallout (50) > content (0). Transitions at z-index 100 will obscure callouts (z-index 50) during their 15-20 frame duration -- delay callout entry by the transition duration.

---

## Design System

Extract a shared `theme.ts` to prevent color drift:

```typescript
export const theme = {
  colors: {
    background: '#0F0F1A',
    backgroundGradientMid: '#1A1A2E',
    backgroundGradientEnd: '#16213E',
    accent: '#6366F1',
    accentLight: '#818CF8',
    text: '#FFFFFF',
    textMuted: '#A0A0B8',
  },
  fonts: {
    display: "'Inter', 'SF Pro Display', sans-serif",
    body: "'Inter', 'SF Pro Text', sans-serif",
    mono: "'JetBrains Mono', 'SF Mono', monospace",
  },
  grid: { size: 60, opacity: 0.02 },
} as const;
```

The subtle grid pattern (60px cells, 2% white opacity) ties text-heavy sections (intro, outro, differentiators) together as a visual family, distinct from screenshot-centric demo sections.

---

## Project Structure

```
projects/my-video/
  script.md                    # Source of truth for narration + visual direction
  assets/
    audio/
      narration-00-hook.mp3    # Per-section audio files
      narration-01-tease.mp3
      narration-full.mp3       # Concatenated (preview only, never use in composition)
      sync-manifest.json       # Word/sentence-level timing data
      narration-manifest.json  # Legacy manifest (durations, metadata)
      intro-music.mp3
      outro-music.mp3
    screenshots/               # Product screenshots for BrowserFrame
    illustrations/             # Generated illustrations (DALL-E, Mermaid, etc.)
  scripts/
    narrate-sync.ts            # Narration generation + timestamp extraction
    audit-sync.ts              # Automated sync auditor
    build-video.ts             # Render orchestrator
    capture.ts                 # Screenshot capture (Puppeteer)
  reviews/
    script-review.md
    sync-audit.md
    full-quality-review.md
  output/                      # Rendered video files

src/
  compositions/MyVideo.tsx     # Remotion composition with S constants
  components/                  # Reusable components (shared across projects)
```
