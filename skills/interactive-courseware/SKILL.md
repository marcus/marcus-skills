---
name: interactive-courseware
description: Create state-of-the-art interactive online courseware with AI agents. Covers course architecture, multimedia generation (narration, video, images, sound), interactive patterns (branching scenarios, simulations, gamification), SCORM/xAPI/cmi5 packaging for LMS delivery, and collaborative agent-human workflows. Use when building courses, training content, e-learning modules, or educational experiences.
---

# Interactive Courseware

Create online courses that people actually want to take. This skill covers the full pipeline from course design through production, packaging, and LMS delivery — all optimized for agent-driven creation with human collaboration.

## Philosophy

Most e-learning is boring because it treats education as information delivery instead of performance improvement. The goal is not to transfer knowledge into heads — it is to change what people *do*. Every design decision should flow from this principle.

**What separates great courseware:**
- Learners make decisions, not just click "next"
- Content is wrapped in narrative, not listed as bullets
- Feedback is immediate, specific, and consequential
- Production quality signals "this matters"
- Pacing respects individual learner agency

**What this skill rejects:**
- Click-next slide decks disguised as courses
- Walls of text with stock photos
- Narration that reads on-screen text verbatim
- Generic multiple-choice as the only assessment
- Forced linear progression through content learners already know

## Quick Start

1. **Define learning outcomes** — What should learners be able to *do* after this course? Not "understand X" but "perform Y in context Z"
2. **Choose course architecture** — Pick a framework and delivery standard (see [Architecture](#architecture))
3. **Design interactions** — Select patterns that match your learning goals (see [Interaction Patterns](#interaction-patterns))
4. **Generate multimedia** — Use agent pipelines for narration, imagery, video, and sound (see [Multimedia Pipeline](#multimedia-pipeline))
5. **Package and deliver** — Build SCORM/xAPI/cmi5 packages for LMS or deploy standalone (see [Packaging & Delivery](#packaging--delivery))
6. **Review and iterate** — Use agent QA and learner analytics to improve (see [Agent Workflows](#agent-workflows))

---

## Architecture

### Recommended Stack

Build courses as modern SPAs with a thin LMS communication layer. This gives you full control over interactivity while maintaining compatibility with corporate LMS platforms.

| Layer | Recommended | Why |
|-------|-------------|-----|
| **Framework** | React + Vite | Rich component ecosystem, fast builds, code splitting |
| **Animations** | GSAP + ScrollTrigger | Industry-standard performance, scroll-driven storytelling |
| **3D content** | React Three Fiber | When needed — explorable models, spatial learning |
| **Data viz** | Observable Plot / D3.js | Interactive charts and explorable data |
| **Diagrams** | Mermaid.js | Agent-generated technical diagrams (see `technical-diagrams` skill) |
| **Code playgrounds** | Sandpack | In-browser coding exercises for programming courses |
| **Branching** | Custom or Twine/Twee export | Scenario-based decision training |
| **Video** | Remotion | Programmatic video generation (see `remotion` skill) |
| **LMS tracking** | scorm-again | Modern SCORM 1.2/2004 runtime, TypeScript, cross-frame support |
| **Packaging** | simple-scorm-packager or custom | Generate imsmanifest.xml + ZIP |

### Course Project Structure

```
my-course/
├── content/
│   ├── modules/
│   │   ├── 01-introduction/
│   │   │   ├── content.json          # Structured content data
│   │   │   ├── quiz.json             # Assessment questions
│   │   │   └── media/                # Module-specific assets
│   │   └── 02-core-concepts/
│   └── shared/
│       ├── glossary.json
│       ├── characters.json           # Scenario characters/personas
│       └── voice-config.json         # TTS voice assignments
├── src/
│   ├── components/
│   │   ├── CourseShell.tsx            # Navigation, progress, chrome
│   │   ├── ContentRenderer.tsx        # Renders content blocks
│   │   ├── interactions/             # Quiz, DnD, Hotspot, etc.
│   │   ├── media/                    # Video player, audio player
│   │   └── feedback/                 # Result displays, scoring
│   ├── tracking/
│   │   ├── adapter.ts                # Abstraction layer
│   │   ├── scorm12.ts                # SCORM 1.2 adapter
│   │   ├── scorm2004.ts              # SCORM 2004 adapter
│   │   ├── xapi.ts                   # xAPI adapter
│   │   ├── cmi5.ts                   # cmi5 adapter
│   │   └── standalone.ts             # localStorage fallback
│   ├── engine/
│   │   ├── state.ts                  # Course state management
│   │   ├── scoring.ts                # Assessment scoring logic
│   │   └── navigation.ts             # Route/progress management
│   └── App.tsx
├── scripts/
│   ├── generate-manifest.ts          # Build imsmanifest.xml
│   ├── package-scorm.ts              # Create SCORM ZIP
│   └── generate-narration.ts         # TTS pipeline
├── public/
│   └── media/                        # Generated audio, images, video
├── vite.config.ts
└── package.json
```

### Content Data Format

Separate content from code. Content authors (or agents) edit JSON; the player renders it. See [references/content-schema.md](references/content-schema.md) for the formal JSON Schema definition, all block type specifications, and validation setup.

```json
{
  "module": "01-introduction",
  "title": "Why Security Matters",
  "objectives": [
    "Identify the three most common phishing techniques",
    "Respond correctly to a suspicious email scenario"
  ],
  "blocks": [
    {
      "type": "narrative",
      "text": "It's 8:47 AM. You've just settled in with your coffee when an email arrives from your CEO...",
      "narration": "audio/01-intro-narrative.mp3",
      "background": "ambient-office"
    },
    {
      "type": "branch",
      "prompt": "The email asks you to wire $50,000 to a new vendor. What do you do?",
      "choices": [
        {
          "text": "Forward to accounting with instructions to process",
          "consequence": "bad",
          "feedback": "This is exactly what the attacker hoped for. CEO fraud cost businesses $2.7B last year.",
          "next": "consequence-bad-wire"
        },
        {
          "text": "Call the CEO directly to verify the request",
          "consequence": "good",
          "feedback": "Smart move. Voice verification is the #1 defense against business email compromise.",
          "next": "consequence-good-verify"
        },
        {
          "text": "Check the sender's email address carefully",
          "consequence": "partial",
          "feedback": "Good instinct, but sophisticated attacks use lookalike domains. Checking the address alone isn't sufficient.",
          "next": "consequence-partial-check"
        }
      ]
    },
    {
      "type": "knowledge-check",
      "question": "Which verification method is most effective against CEO fraud?",
      "format": "single-choice",
      "options": [
        { "text": "Checking the email header", "correct": false },
        { "text": "Out-of-band verification (phone call)", "correct": true },
        { "text": "Replying to the email to confirm", "correct": false },
        { "text": "Asking a colleague", "correct": false }
      ],
      "feedback": {
        "correct": "Out-of-band verification through a different channel breaks the attacker's control over the conversation.",
        "incorrect": "The attacker controls the email channel. You need to verify through a completely different medium."
      }
    }
  ]
}
```

### Environment Detection and Multi-Standard Support

Build one course, deploy everywhere. Detect the runtime environment and use the appropriate tracking adapter.

```typescript
// tracking/adapter.ts
import { Scorm12Adapter } from './scorm12';
import { Scorm2004Adapter } from './scorm2004';
import { XAPIAdapter } from './xapi';
import { Cmi5Adapter } from './cmi5';
import { StandaloneAdapter } from './standalone';

interface TrackingAdapter {
  initialize(): Promise<void>;
  saveProgress(location: string, data: Record<string, unknown>): void;
  getProgress(): { location: string; data: Record<string, unknown> };
  reportScore(score: number, max: number, passed: boolean): void;
  reportCompletion(): void;
  terminate(): void;
}

function detectEnvironment(): string {
  const params = new URLSearchParams(window.location.search);

  // cmi5: has fetch, endpoint, and registration params
  if (params.has('fetch') && params.has('endpoint') && params.has('registration')) {
    return 'cmi5';
  }

  // SCORM 2004: look for API_1484_11 in parent frames
  if (findAPI('API_1484_11')) return 'scorm2004';

  // SCORM 1.2: look for API in parent frames
  if (findAPI('API')) return 'scorm12';

  // xAPI: configured endpoint
  if (window.xAPIConfig || params.has('endpoint')) return 'xapi';

  // Standalone: localStorage fallback
  return 'standalone';
}

function findAPI(name: string): unknown {
  let win: Window = window;
  let attempts = 0;
  while (!(win as any)[name] && win.parent !== win && attempts < 10) {
    win = win.parent;
    attempts++;
  }
  return (win as any)[name] || null;
}

export function createAdapter(): TrackingAdapter {
  const env = detectEnvironment();
  switch (env) {
    case 'scorm12': return new Scorm12Adapter();
    case 'scorm2004': return new Scorm2004Adapter();
    case 'xapi': return new XAPIAdapter();
    case 'cmi5': return new Cmi5Adapter();
    default: return new StandaloneAdapter();
  }
}
```

See [references/scorm-packaging.md](references/scorm-packaging.md) for detailed SCORM/xAPI/cmi5 implementation and packaging.

---

## Interaction Patterns

Every interaction should serve a learning purpose. If removing an interaction doesn't reduce learning, remove it.

### Tier 1: High-Impact (Use Liberally)

**Branching Scenarios** — Learners make decisions with visible consequences. Best for soft skills, compliance, decision-making, and any domain where judgment matters.
- Shallow branching: choices lead to feedback, then rejoin the main path
- Deep branching: choices cascade, creating meaningfully different experiences
- Use audio narration to increase realism in scenario dialogues
- Characters should be relatable and flawed, not perfect role models

**Simulations** — Replica environments where learners practice real tasks.
- Software simulations: practice using actual tool interfaces
- Process simulations: multi-step workflows with realistic constraints
- Role-play simulations: AI-powered conversational practice (see `agents` skill for ElevenLabs voice agents)
- Business simulations: resource allocation, strategic decisions with consequences

**Knowledge Checks with Elaborative Feedback** — Not just "right/wrong" but explaining *why*.
- Embed throughout content, not just at the end
- Use confidence-based assessment: "How sure are you?"
- Scenario-based questions over abstract recall
- Adaptive difficulty based on performance
- Space reviews at increasing intervals (spaced repetition)

### Tier 2: Strong Supporting Patterns

**Interactive Video** — Layer decision points, hotspots, and quizzes onto video.
- In-video knowledge checks that pause for response
- Choose-your-path branching video narratives
- Synchronized side panels (text, diagrams, code update alongside video)
- Use Remotion (see `remotion` skill) for programmatic video with built-in interaction points

**Scroll-Driven Storytelling** — Content reveals tied to scroll position using GSAP ScrollTrigger.
- Scroll-triggered animations: fade, slide, transform on viewport entry
- Scroll-linked animations: parallax, progress indicators, video scrubbing
- Scrubbing video: playback position tied to scroll (learner controls pacing)
- Restraint is critical — "used well, scroll animations make content impossible to scroll past; used poorly, they distract and overwhelm"

**Drag-and-Drop** — Physical manipulation reinforces learning.
- Sorting/categorization: classify items into correct groups
- Sequencing: arrange process steps in correct order
- Labeling: place labels on diagrams
- Assembly: build something from components
- Always provide keyboard alternatives for accessibility

**Story-Based Learning** — Narrative wrapping increases recall from 10% to 70%.
- Character-driven scenarios with relatable protagonists
- Episodic microlearning building a larger narrative arc
- Conflict and genuine dilemmas (not obvious choices)
- Resolution should teach, not preach

### Tier 3: Use Purposefully

**Gamification** — Only when tied to actual skill development, not decoration.
- Progress visibility (skill trees, milestone tracking) works well
- Meaningful challenges tied to learning objectives
- Adaptive difficulty based on individual performance
- Avoid: generic points/badges, forced competition, extrinsic rewards that undermine intrinsic motivation

**3D Explorable Content** — React Three Fiber for spatial learning.
- Interactive anatomy, molecular, or mechanical models
- Virtual labs and 3D tours
- Only when 3D adds genuine understanding over 2D alternatives

**Collaborative Exercises** — Peer review, group challenges, discussions.
- Works best in cohort-based or live courses
- Adds accountability and social learning

See [references/interaction-patterns.md](references/interaction-patterns.md) for implementation details and code examples.

---

## Multimedia Pipeline

Use AI to generate production-quality multimedia at the pace of content development. Reference existing skills rather than duplicating their content.

### Narration (Text-to-Speech)

Use the **`text-to-speech` skill** for ElevenLabs TTS integration.

**Courseware-specific guidance:**
- Assign consistent voices to roles (narrator, characters, system feedback)
- Do NOT narrate on-screen text verbatim — narration should complement visuals
- Chunk narration into ~150-word segments aligned with content blocks
- Generate narration in batch: extract all text → generate audio → align with content
- Keep narration optional with clear mute/unmute controls
- Use `eleven_multilingual_v2` for highest quality; `eleven_flash_v2_5` for real-time

```python
# Batch narration generation pipeline
from elevenlabs import ElevenLabs
import json, os

client = ElevenLabs()

VOICE_MAP = {
    "narrator": "JBFqnCBsd6RMkjVDRZzb",    # George — authoritative
    "learner": "EXAVITQu4vr4xnSDxMaL",      # Sarah — relatable
    "mentor": "onwK4e9ZLuTAKqWW03F9",        # Daniel — warm
}

def generate_module_narration(module_path: str, output_dir: str):
    with open(module_path) as f:
        module = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    for i, block in enumerate(module["blocks"]):
        if "narration_text" not in block:
            continue

        voice = VOICE_MAP.get(block.get("voice_role", "narrator"), VOICE_MAP["narrator"])
        audio = client.text_to_speech.convert(
            text=block["narration_text"],
            voice_id=voice,
            model_id="eleven_multilingual_v2",
        )

        filename = f"{i:03d}-{block['type']}.mp3"
        with open(os.path.join(output_dir, filename), "wb") as f:
            for chunk in audio:
                f.write(chunk)

        block["narration"] = f"media/{filename}"

    # Write updated module with audio paths
    with open(module_path, "w") as f:
        json.dump(module, f, indent=2)
```

### Background Music and Sound Effects

Use the **`music` skill** for AI-generated background tracks and the **`sound-effects` skill** for interaction sounds.

**Courseware audio design:**
- Background music: lo-fi or ambient at low volume during content sections, energetic for gamified sections
- Interaction sounds: subtle confirmation for correct answers, gentle alert for errors
- Transition sounds: whoosh between sections, click for navigation
- Ambient soundscapes: office sounds for workplace scenarios, lab sounds for science
- Always provide audio controls; never autoplay music

```python
# Generate course soundtrack
from elevenlabs import ElevenLabs

client = ElevenLabs()

# Background music for different course moods
tracks = {
    "ambient-learning": "Calm, minimal ambient electronic with soft piano, suitable as background for reading and studying, 120 BPM",
    "scenario-tension": "Tense, suspenseful underscore with subtle strings and low pulse, building anticipation",
    "achievement": "Short triumphant fanfare with bright brass and ascending melody, 5 seconds, celebration",
    "reflection": "Gentle acoustic guitar with soft pad, contemplative and warm, for review sections",
}

for name, prompt in tracks.items():
    audio = client.music.compose(prompt=prompt, music_length_ms=30000)
    with open(f"public/media/music/{name}.mp3", "wb") as f:
        for chunk in audio:
            f.write(chunk)

# UI sound effects
sfx = {
    "correct": "Short bright positive chime, digital UI confirmation sound",
    "incorrect": "Soft low-pitched buzz, gentle error notification",
    "click": "Subtle soft click, tactile button press",
    "whoosh": "Quick smooth whoosh transition, left to right",
    "reveal": "Gentle shimmer reveal sound, magical sparkle",
    "complete": "Achievement unlocked jingle, warm and rewarding, 2 seconds",
}

for name, prompt in sfx.items():
    audio = client.text_to_sound_effects.convert(text=prompt, duration_seconds=2.0)
    with open(f"public/media/sfx/{name}.mp3", "wb") as f:
        for chunk in audio:
            f.write(chunk)
```

### Imagery (AI Image Generation)

Use OpenAI's image generation API or Stable Diffusion for course illustrations.

**Strategy by image type:**

| Need | Tool | Why |
|------|------|-----|
| Labeled diagrams, step-by-step visuals | OpenAI GPT Image / DALL-E | Best text rendering in images |
| Scenario illustrations, atmospheric art | Midjourney (manual) or DALL-E | Emotional resonance |
| Consistent style across entire course | Stable Diffusion + LoRA | Fine-tune for brand consistency |
| Technical diagrams (flowcharts, architecture) | Mermaid.js | See `technical-diagrams` skill |

**Avoiding generic AI imagery:**
- Use detailed, context-rich prompts specific to your course scenario
- Maintain a style guide: color palette, illustration style, character design
- Train LoRA models on your brand's visual language for Stable Diffusion
- Post-process AI output; don't use it raw
- Hybrid workflows: AI generates base, human designers refine

### Video (Programmatic Generation)

Use the **`remotion` skill** for programmatic React-based video.

**Courseware video types:**
- Animated explainers: concepts visualized with motion graphics
- Software walkthroughs: screen recordings with annotations
- Avatar-presented segments: AI presenters for narrated content (HeyGen, Synthesia APIs)
- Data-driven visualizations: animated charts and graphs

**When to use AI avatar presenters (HeyGen/Synthesia):**
- Onboarding content (consistent, repeatable)
- Multi-language versions (same avatar, different languages)
- Rapid content updates (re-render with new script, no re-shooting)
- When a human presenter is unavailable

**When NOT to use AI avatars:**
- Sensitive topics requiring genuine empathy
- When authenticity and personal credibility are critical
- When uncanny valley effect undermines trust

### Voice AI Agents for Practice

Use the **`agents` skill** for ElevenLabs conversational AI.

- Role-play simulations: practice sales calls, customer service, difficult conversations
- AI tutors: conversational help agents trained on course content
- Oral assessments: voice-based knowledge checks
- Language practice: pronunciation and conversation drills

See [references/multimedia-pipeline.md](references/multimedia-pipeline.md) for complete pipeline architecture.

---

## Packaging & Delivery

### SCORM Packaging (Corporate LMS)

Most corporate LMS platforms (WorkRamp, Docebo, Cornerstone, SAP SuccessFactors) use SCORM. WorkRamp specifically uses Rustici Software's SCORM Cloud engine and recommends SCORM 2004 4th Edition.

**Minimal SCORM 1.2 manifest (imsmanifest.xml):**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="course-security-101" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="org-1">
    <organization identifier="org-1">
      <title>Security Awareness 101</title>
      <item identifier="item-1" identifierref="res-1">
        <title>Security Awareness 101</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="res-1" type="webcontent"
      adlcp:scormtype="sco" href="index.html">
      <file href="index.html"/>
    </resource>
  </resources>
</manifest>
```

**SCORM packaging build script:**

```typescript
// scripts/package-scorm.ts
import { createWriteStream } from 'fs';
import { readdir, readFile } from 'fs/promises';
import { join, relative } from 'path';
import archiver from 'archiver';

async function packageScorm(
  distDir: string,
  manifestPath: string,
  outputPath: string
) {
  const output = createWriteStream(outputPath);
  const archive = archiver('zip', { zlib: { level: 9 } });
  archive.pipe(output);

  // Add manifest at root
  archive.file(manifestPath, { name: 'imsmanifest.xml' });

  // Add SCORM schema files
  const schemas = [
    'adlcp_rootv1p2.xsd',
    'imscp_rootv1p1p2.xsd',
    'imsmd_rootv1p2p1.xsd',
  ];
  for (const schema of schemas) {
    archive.file(join('schemas', schema), { name: schema });
  }

  // Add all built files
  archive.directory(distDir, false);

  await archive.finalize();
  console.log(`SCORM package created: ${outputPath}`);
}
```

**npm scripts for the build pipeline:**

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "generate-narration": "tsx scripts/generate-narration.ts",
    "generate-manifest": "tsx scripts/generate-manifest.ts",
    "package-scorm": "tsx scripts/package-scorm.ts",
    "build-course": "npm run build && npm run generate-manifest && npm run package-scorm",
    "preview": "vite preview",
    "test": "vitest",
    "validate-scorm": "tsx scripts/validate-scorm.ts"
  }
}
```

### Delivery Standard Selection

| Standard | When to use | LMS Support |
|----------|-------------|-------------|
| **SCORM 1.2** | Widest compatibility, simple tracking needs | Universal |
| **SCORM 2004** | Need sequencing rules, larger suspend_data (64KB vs 4KB) | Very wide (WorkRamp recommended) |
| **xAPI** | Track beyond the LMS (mobile, simulations, real-world), need rich analytics | Growing (requires LRS) |
| **cmi5** | Want xAPI richness with SCORM-like LMS launch | Emerging (WorkRamp supports) |
| **LTI 1.3** | Embedding external tools/apps within an LMS | Wide in education |
| **Standalone** | No LMS, direct web deployment | N/A |

### Hosting Models

| Model | Best for | Tracking |
|-------|----------|----------|
| **LMS-hosted SCORM** | Standard corporate deployment | Full SCORM tracking |
| **SCORM Cloud** | Testing, cross-LMS deployment | Full, via Rustici engine |
| **Self-hosted + LTI** | Maximum control, custom UX | LTI grades + xAPI detail |
| **Standalone web app** | Public courses, marketing | xAPI to external LRS or none |

See [references/scorm-packaging.md](references/scorm-packaging.md) for complete SCORM 1.2, 2004, xAPI, and cmi5 implementation details. See [references/scorm-troubleshooting.md](references/scorm-troubleshooting.md) for LMS quirks, debugging techniques, and a testing toolkit.

---

## Agent Workflows

Courses are created by teams of specialized agents collaborating with human subject matter experts.

### Multi-Agent Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    Course Creation Pipeline                   │
│                                                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ Research  │───▶│ Structure│───▶│  Write   │               │
│  │  Agent    │    │  Agent   │    │  Agent   │               │
│  │          │    │          │    │          │               │
│  │ Gathers  │    │ Creates  │    │ Drafts   │               │
│  │ source   │    │ modules, │    │ content  │               │
│  │ material │    │ objectives│   │ blocks,  │               │
│  └──────────┘    └──────────┘    │ scenarios│               │
│                                   └────┬─────┘               │
│                                        │                     │
│                                        ▼                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ Publish  │◀───│ QA       │◀───│ Media    │               │
│  │  Agent   │    │  Agent   │    │  Agent   │               │
│  │          │    │          │    │          │               │
│  │ Packages │    │ Reviews  │    │ Generates│               │
│  │ SCORM,   │    │ accuracy,│    │ narration│               │
│  │ deploys  │    │ tone,    │    │ images,  │               │
│  └──────────┘    │ a11y     │    │ video,   │               │
│                   └──────────┘    │ sound    │               │
│       ▲                           └──────────┘               │
│       │          ┌──────────┐                                │
│       └──────────│  Human   │◀── Reviews at checkpoints     │
│                  │  SME     │                                │
│                  └──────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

### Agent Roles

**Research Agent** — Gathers and synthesizes source material.
- Analyzes existing documentation, training materials, SME interviews
- Identifies knowledge gaps and generates clarifying questions
- Creates a research brief with key concepts, facts, and examples

**Structure Agent** — Organizes content into a learning architecture.
- Defines learning objectives (behavioral, measurable)
- Creates module/lesson hierarchy
- Selects interaction patterns appropriate for each objective
- Maps assessment items to objectives (ensures coverage)

**Writer Agent** — Drafts all content.
- Writes scenario narratives, dialogue, and narration scripts
- Creates assessment items with elaborative feedback
- Follows brand voice guidelines (use `human-writing` skill to avoid AI patterns)
- Generates content.json files for the course player

**Media Agent** — Generates all multimedia assets.
- Narration: batch TTS generation with voice role assignments
- Images: generates illustrations, scenario images, diagrams
- Video: creates explainer videos via Remotion
- Sound: background music, UI sounds, ambient audio
- References: `text-to-speech`, `music`, `sound-effects`, `remotion` skills

**QA Agent** — Reviews everything against quality criteria.
- Factual accuracy: cross-references against source materials (RAG)
- Learning objective alignment: every block maps to an objective
- Accessibility: alt text, heading structure, keyboard navigation, color contrast
- Tone consistency: matches brand voice guidelines
- Assessment quality: Bloom's taxonomy level, clarity, distractor quality

**Publish Agent** — Packages and deploys.
- Builds the course (Vite)
- Generates SCORM manifest
- Creates SCORM/cmi5 package
- Validates package structure
- Deploys to preview environment or LMS

### Human-Agent Collaboration Points

Not every step needs human review, but these critical junctures do:

| Checkpoint | Human Role | Agent Deliverable |
|------------|------------|-------------------|
| After research brief | SME validates completeness and accuracy | Research summary with key concepts |
| After course structure | SME approves objectives and flow | Module map with objectives and interaction types |
| After first draft of each module | SME reviews content accuracy and tone | Complete content.json with all blocks |
| After assessment items | SME validates questions and answers | Quiz.json with items, feedback, scoring |
| Before final publication | Stakeholder sign-off | Preview URL with full course |

### Generator-Critic Loop

The most effective pattern for quality: one agent writes, another critiques, iterate until quality threshold is met.

```python
# Simplified generator-critic loop
def create_module_content(module_spec, source_materials, max_iterations=3):
    draft = writer_agent.generate(module_spec, source_materials)

    for i in range(max_iterations):
        critique = qa_agent.review(draft, criteria={
            "factual_accuracy": source_materials,
            "learning_alignment": module_spec["objectives"],
            "engagement_level": "high",
            "accessibility": "WCAG_AA",
            "voice_consistency": brand_guidelines,
        })

        if critique.passes_all:
            return draft

        draft = writer_agent.revise(draft, critique.feedback)

    # After max iterations, flag for human review
    return flag_for_human_review(draft, critique)
```

### RAG-Grounded Generation

All content generation should be grounded in approved source materials to prevent hallucination.

```python
# Ground content generation in source materials
def generate_grounded_content(topic, source_docs):
    # Retrieve relevant passages from source materials
    relevant_passages = vector_store.similarity_search(topic, k=10)

    # Generate content grounded in retrieved passages
    content = writer_agent.generate(
        topic=topic,
        context=relevant_passages,
        instructions="Only use information from the provided context. "
                     "If the context doesn't cover something, flag it as "
                     "needing SME input rather than generating from general knowledge."
    )

    return content
```

See [references/agent-workflows.md](references/agent-workflows.md) for complete pipeline implementation. See [references/prompt-engineering.md](references/prompt-engineering.md) for copy-paste-ready system prompts, content generation templates, and few-shot examples for each agent role.

---

## Learning Science Principles

These evidence-based principles should guide every design decision.

### Mayer's Multimedia Learning Principles

| Principle | Guideline | Implementation |
|-----------|-----------|----------------|
| **Coherence** | Remove extraneous material | No decorative images, no tangential content |
| **Signaling** | Highlight essential material | Visual hierarchy, emphasis animations |
| **Redundancy** | Don't narrate on-screen text | Narration complements visuals; never duplicates |
| **Spatial contiguity** | Place text near related graphics | Labels on diagrams, not in separate legends |
| **Temporal contiguity** | Present words and pictures simultaneously | Narration synced with visuals |
| **Segmenting** | Break into learner-paced segments | Module → lesson → block, self-paced navigation |
| **Pre-training** | Teach key concepts before main lesson | Glossary, concept primers, prerequisite checks |
| **Modality** | Use narration for graphics, not on-screen text | Audio narration + visual diagrams > text + diagrams |
| **Personalization** | Use conversational tone | "You'll notice..." not "It should be noted..." |

### Retrieval Practice

Meta-analyses show retrieval practice has a mean effect size of g = 0.50 over restudying — one of the largest effects in educational research.

- Embed knowledge checks throughout content, not just at the end
- Make retrieval effortful (free recall > recognition)
- Provide elaborative feedback after each attempt
- Space reviews at increasing intervals (1 day, 3 days, 7 days, 14 days)

### Cognitive Load Management

- Limit new concepts per screen (3-5 items)
- Use progressive disclosure: reveal complexity gradually
- Worked examples before practice problems
- Reduce split attention: integrate text into diagrams
- Offload to the environment: checklists, job aids, reference panels

### The Forgetting Curve

Learners lose up to 90% of content within a week without reinforcement. Combat this with:
- Spaced repetition of key concepts across modules
- Post-course reinforcement (email nudges, microlearning follow-ups)
- Performance support tools (quick-reference guides, searchable glossary)

---

## Tool Recommendations

### Open Source Tools Worth Knowing

| Tool | What it does | Agent-friendly? |
|------|-------------|-----------------|
| **Adapt Framework** | Full SCORM courseware framework, JSON config | Yes — generate JSON + CLI build |
| **H5P** | 50+ interactive content types | Yes — via EscolaLMS headless API |
| **Twine/Twee** | Branching scenario engine | Excellent — Twee text format is trivially LLM-generated |
| **Reveal.js** | Presentation framework, extensible | Excellent — Markdown/HTML generation |
| **Slidev** | Dev-focused presentations with Vue components | Excellent — Markdown + Vue |
| **Sandpack** | Browser code playgrounds | Good — React components, configurable |
| **Marimo** | Reactive Python notebooks for education | Excellent — pure Python files |
| **JupyterLite** | Full Jupyter in browser (WASM) | Good — standard notebook format |
| **Phaser** | 2D game framework | Good — scene-based JS architecture |
| **OATutor** | Open adaptive tutoring system | Good — JSON content, BKT engine |
| **scorm-again** | SCORM 1.2/2004 JavaScript runtime | N/A (library) |
| **Excalidraw** | Collaborative whiteboard | Good — embeddable React component |

### Commercial APIs for Multimedia

| Service | Use for | Skill reference |
|---------|---------|-----------------|
| **ElevenLabs TTS** | Narration, character dialogue | `text-to-speech` |
| **ElevenLabs Music** | Background tracks, transitions | `music` |
| **ElevenLabs SFX** | UI sounds, ambient audio | `sound-effects` |
| **ElevenLabs Agents** | Voice AI tutors, practice partners | `agents` |
| **ElevenLabs STT** | Transcribe SME interviews, voice input | `speech-to-text` |
| **OpenAI GPT Image** | Illustrations, diagrams with text | — |
| **OpenAI / Claude** | Content generation, assessment creation | `claude-api` |
| **HeyGen** | AI avatar video presenters | — |
| **Synthesia** | Enterprise AI avatar video | — |

See [references/tool-recommendations.md](references/tool-recommendations.md) for detailed evaluation of each tool. See [references/cost-and-analytics.md](references/cost-and-analytics.md) for API pricing estimates and learner analytics implementation.

---

## Accessibility Requirements

Accessibility is a design principle, not a compliance checkbox.

### Non-Negotiable Requirements

- **Keyboard navigation**: All interactions operable via Tab, Enter, Space, Arrows
- **Drag-and-drop alternatives**: Select-then-place for keyboard users
- **Screen reader support**: Semantic HTML first, ARIA where native semantics are insufficient
- **`aria-live` regions**: Announce dynamic content (quiz results, feedback, progress)
- **`prefers-reduced-motion`**: Honor reduced motion preferences; provide static alternatives
- **Color contrast**: WCAG AA minimum (4.5:1 for text, 3:1 for large text and UI)
- **Captions**: All video and audio content must have captions/transcripts
- **Focus management**: Visible focus indicators throughout; manage focus on dynamic content changes
- **Multiple engagement pathways**: Watch, read, interact — never one-only

### Testing

See [references/accessibility-testing.md](references/accessibility-testing.md) for complete automated testing setup (axe-core + Vitest + Playwright + Lighthouse CI), courseware-specific ARIA patterns, manual testing protocols, and compliance documentation (VPAT/ACR).

```bash
# Quick automated checks
npm run test:a11y          # axe-core component tests
npm run test:a11y:e2e      # Playwright full-page audits
npx lighthouse --only-categories=accessibility http://localhost:5173
```

---

## Anti-Patterns to Avoid

These are the hallmarks of boring courseware. If you catch yourself building any of these, stop and redesign.

| Anti-Pattern | Why It Fails | What to Do Instead |
|-------------|-------------|-------------------|
| **Click-next slides** | Zero cognitive engagement | Require decisions, not clicks |
| **Narration matching screen text** | Cognitive overload (redundancy) | Narration complements visuals; never duplicates |
| **Wall of text** | No visual hierarchy, overwhelming | Progressive disclosure, chunked content |
| **Generic stock photos** | Signal "we didn't try" | AI-generated contextual imagery or custom illustration |
| **MCQ-only assessment** | Tests recognition, not application | Scenario-based, drag-drop, simulation, confidence-rated |
| **Forced linear lockstep** | Punishes knowledgeable learners | Allow skip/test-out, adaptive paths |
| **Decorative animation** | Distracts without teaching | Animation serves learning purpose or doesn't exist |
| **One-size-fits-all pacing** | Ignores individual processing speed | Self-paced with optional narration |
| **Compliance checkbox design** | Optimizes for tracking, not learning | Design for behavior change, track as byproduct |

---

## Cross-Referenced Skills

This skill integrates with these other skills in the ecosystem:

| Skill | Use for |
|-------|---------|
| **`text-to-speech`** | Generate narration audio with ElevenLabs |
| **`music`** | Create background music and transition tracks |
| **`sound-effects`** | Generate UI sounds and ambient audio |
| **`speech-to-text`** | Transcribe SME interviews and source audio |
| **`agents`** | Build voice AI tutors and practice partners |
| **`remotion`** | Create programmatic video content |
| **`software-demo-video`** | Production techniques for software walkthroughs |
| **`technical-diagrams`** | Generate Mermaid.js diagrams for technical content |
| **`human-writing`** | Ensure content avoids AI-detectable patterns |
| **`site-design-director`** | Design direction for standalone course landing pages |
| **`linear-design-patterns`** | Keyboard-first, high-density UI patterns for course admin |
| **`orchestrate`** | Orchestrate multi-agent course creation workflows |
| **`claude-api`** | Build AI-powered course generation and assessment tools |
