# Cost Analysis and Learner Analytics Reference

Pricing data and analytics architecture for the interactive courseware pipeline.

---

## Part 1: Cost Analysis

### Per-Service Cost Breakdown (45-Minute Course)

A typical 45-minute course with 8 modules requires narration, illustrations, background music, sound effects, and content generation. The estimates below assume the pipeline described in `multimedia-pipeline.md`.

#### ElevenLabs TTS (Narration)

Narration for a 45-minute course covers roughly 30 minutes of spoken audio (the rest is interaction time, reading, video, etc.). At ~150 words/minute and ~5 characters/word, that is approximately 135,000 characters.

| Plan | Credits Included | Overage Rate | Est. Cost for 135K chars |
|------|-----------------|--------------|--------------------------|
| Free | 10,000/mo | N/A | Not feasible |
| Starter ($5/mo) | 30,000/mo | N/A | Not feasible |
| Creator ($22/mo) | 100,000/mo | $0.30/1K chars | $22 + $10.50 overage = ~$33 |
| Pro ($99/mo) | 500,000/mo | $0.24/1K chars | $99 (within quota) |
| Scale ($330/mo) | 2,000,000/mo | $0.18/1K chars | $330 (within quota, best for volume) |

**Model multipliers:** `eleven_multilingual_v2` costs 1 credit/char. `eleven_flash_v2_5` costs 0.5 credits/char (use for system feedback voice).

**Recommendation:** Pro plan ($99/mo) covers a full 45-minute course with headroom for revisions. For a one-off course, Creator plan with overage is cheapest at ~$33.

#### ElevenLabs Music Generation

A typical course needs 3-5 background tracks (intro theme, ambient learning, scenario tension, reflection interlude, achievement fanfare). Each track is 15-60 seconds.

| Item | Credits | Notes |
|------|---------|-------|
| Music generation | Variable by duration | Cost shown before generation; charged per second of output |
| Typical 30-second track | ~500-1,000 credits | Varies by plan (fixed fiat price translated to credits) |
| Full soundtrack (5 tracks) | ~3,000-5,000 credits | One-time generation, reuse across course |

**Recommendation:** Generate music alongside TTS within the same Pro plan quota. Music generation draws from the same credit pool as TTS.

#### ElevenLabs Sound Effects

A standard course needs 8-12 sound effects (correct, incorrect, click, transitions, reveal, completion, notification, typing, email, ambient).

| Method | Credits per SFX | Notes |
|--------|----------------|-------|
| API (default duration) | 100 credits/generation | AI decides duration, 1 SFX per call |
| API (custom duration) | 40 credits/second | Set your own duration |
| Website (default duration) | 200 credits/generation | Returns 4 variants per call |

| SFX Set | API Cost (default) | API Cost (custom, avg 2s) |
|---------|-------------------|---------------------------|
| 10 effects | 1,000 credits | 800 credits |
| Full set with variants | 2,000-3,000 credits | 1,500-2,400 credits |

**Recommendation:** Generate SFX once with the API (custom duration for precision), reuse across all courses. Total SFX cost is negligible within any paid plan.

#### OpenAI Image Generation (Illustrations)

A 45-minute course with 8 modules needs roughly 15-25 illustrations (hero images, concept diagrams, scenario scenes).

| Model | Quality | Cost per Image | 20 Images |
|-------|---------|---------------|-----------|
| GPT Image 1 | Low | $0.011 | $0.22 |
| GPT Image 1 | Medium | $0.042 | $0.84 |
| GPT Image 1 | High | $0.167 | $3.34 |
| GPT Image 1 Mini | Low | $0.005 | $0.10 |
| DALL-E 3 | Standard | $0.040 | $0.80 |

**Resolution options:** 1024x1024 (default), 1024x1792, 1792x1024. Higher resolutions cost more.

**Recommendation:** Use GPT Image 1 at Medium quality for hero illustrations ($0.042 each) and GPT Image 1 Mini for supplementary images ($0.005 each). Total for 20 images: ~$1-4.

#### OpenAI / Claude API (Content Generation + QA)

Content generation involves: course outline, module content, assessment items, narration scripts, image prompts, branching scenarios, QA review, and revision cycles. Estimate ~50,000 input tokens and ~30,000 output tokens per module, with 2 QA review passes.

| Model | Input/1M | Output/1M | 8 Modules + QA |
|-------|----------|-----------|----------------|
| GPT-4o | $2.50 | $10.00 | ~$5-8 |
| GPT-4o Mini | $0.15 | $0.60 | ~$0.30-0.50 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | ~$7-12 |
| Claude Haiku 4.5 | $0.25 | $1.25 | ~$0.50-0.80 |
| Claude Opus 4.6 | $5.00 | $25.00 | ~$12-20 |

**Token breakdown per 45-minute course (8 modules):**
- Content generation: ~400K input + 240K output tokens
- QA review (2 passes): ~300K input + 100K output tokens
- Assessment generation: ~100K input + 80K output tokens
- Total: ~800K input + 420K output tokens

**Cost optimization:**
- Use prompt caching (saves 90% on Anthropic, 50% on OpenAI cached input)
- Use batch API for non-urgent generation (50% discount on both platforms)
- Use Haiku/GPT-4o-mini for first drafts, Sonnet/GPT-4o for QA review

#### HeyGen (AI Avatar Video)

For courses with a talking-head presenter introducing modules or explaining concepts.

| Tier | Cost per Minute | 5 Min of Avatar Video | 15 Min of Avatar Video |
|------|----------------|----------------------|------------------------|
| Pro API | $0.99/min | $4.95 | $14.85 |
| Scale API | $0.50/min | $2.50 | $7.50 |
| Avatar IV (premium) | ~$5.94/min (6 credits) | $29.70 | $89.10 |

**Constraints:** Max 30 minutes per video (API), 1080p only (enterprise for 4K).

#### Synthesia (Enterprise AI Avatar Video)

| Plan | Monthly Cost | Minutes/Year | Effective $/Min |
|------|-------------|--------------|-----------------|
| Starter | $18/mo (annual) | 120/year | $1.80/min |
| Creator | $64/mo (annual) | 360/year | $2.13/min |
| Enterprise | Custom | Unlimited | Negotiated |

**Additional costs:** Studio Avatars ($1,000/year add-on), Personal Avatar (included in annual plans or $1,000/year).

**Recommendation:** HeyGen Scale API ($0.50/min) is most cost-effective for API-driven pipelines. Synthesia is better for enterprise teams that need the authoring UI.

#### Remotion (Programmatic Video)

| Use Case | License | Cost |
|----------|---------|------|
| Individual / team <= 3 people | Free | $0 |
| Company (seat-based, "Creators") | Paid | From $25/developer/month |
| Company (render-based, "Automators") | Paid | From $100/month minimum |
| Enterprise | Custom | Negotiated |

**Note:** Remotion itself is free for rendering; the license covers commercial use by larger organizations. AWS Lambda rendering costs are separate (~$0.001-0.01 per render depending on duration).

#### Stable Diffusion (Self-Hosted vs API)

| Deployment | Cost per Image | Setup Cost | Best For |
|------------|---------------|------------|---------|
| Replicate API (SDXL) | $0.002-0.006 | None | Quick prototyping |
| Replicate API (SD 3.5 Large) | $0.065 | None | Higher quality |
| Stability AI API (SD 3.5 Large) | $0.065 (6.5 credits) | None | Official API |
| Stability AI API (SDXL) | $0.002 | None | Budget API |
| Self-hosted (RTX 4090) | ~$0.001 | $1,600 GPU | High volume (>25K images) |
| Self-hosted (cloud A100) | ~$0.01-0.03 | $1-3/hr GPU rental | Burst capacity |

**Community License:** Free for individuals and orgs with revenue < $1M/year. Covers unlimited image generation.

**Recommendation:** For courseware, OpenAI GPT Image 1 is generally superior for one-off illustrations. Use Stable Diffusion + LoRA when you need a consistent custom art style across hundreds of images.

---

### Total Cost Estimates by Course Size

#### Small Course (15 min, 3 modules, basic interactions)

| Component | Quantity | Cost |
|-----------|----------|------|
| Narration (TTS) | ~45K chars (10 min narration) | $14 (Creator plan overage) |
| Images | 8 illustrations | $0.34 (GPT Image 1 Medium) |
| Sound effects | 6 SFX (reusable set) | ~$0.50 (within plan credits) |
| Background music | 2 tracks | ~$1.00 (within plan credits) |
| Content generation (LLM) | 3 modules + QA | ~$3 (Sonnet 4.6) |
| **Total** | | **~$19** |

#### Medium Course (45 min, 8 modules, branching + video)

| Component | Quantity | Cost |
|-----------|----------|------|
| Narration (TTS) | ~135K chars (30 min narration) | $33 (Creator plan + overage) |
| Images | 20 illustrations | $0.84 (GPT Image 1 Medium) |
| Sound effects | 10 SFX | ~$0.75 (within plan credits) |
| Background music | 5 tracks | ~$2.00 (within plan credits) |
| AI avatar video | 5 min (module intros) | $2.50 (HeyGen Scale) |
| Branching scenario art | 10 additional images | $0.42 (GPT Image 1 Medium) |
| Content generation (LLM) | 8 modules + QA + branching | ~$10 (Sonnet 4.6) |
| Diagrams (Mermaid) | 6 diagrams | $0 (generated via LLM, rendered client-side) |
| **Total** | | **~$50** |

#### Large Course (2 hours, 15 modules, full multimedia + simulations)

| Component | Quantity | Cost |
|-----------|----------|------|
| Narration (TTS) | ~360K chars (80 min narration) | $99 (Pro plan) |
| Images | 50 illustrations | $2.10 (GPT Image 1 Medium) |
| Sound effects | 15 SFX + ambient loops | ~$1.50 (within plan credits) |
| Background music | 8 tracks | ~$4.00 (within plan credits) |
| AI avatar video | 20 min (intros + explanations) | $10.00 (HeyGen Scale) |
| Branching scenario art | 30 additional images | $1.26 (GPT Image 1 Medium) |
| Content generation (LLM) | 15 modules + QA + simulations | ~$25 (Sonnet 4.6) |
| Diagrams (Mermaid) | 15 diagrams | $0 |
| Remotion video segments | 10 animated explainers | $0 (free license for small team) |
| Simulation interactions | 5 interactive sims | $5 (LLM generation for logic) |
| Localization (3 languages) | TTS + content regen | ~$60 additional |
| **Total (English only)** | | **~$148** |
| **Total (4 languages)** | | **~$208** |

#### Cost Comparison: Traditional vs AI-Generated

| Approach | Small (15 min) | Medium (45 min) | Large (2 hr) |
|----------|---------------|-----------------|--------------|
| Traditional (freelancers + tools) | $3,000-5,000 | $15,000-30,000 | $50,000-100,000 |
| AI pipeline (this stack) | ~$19 | ~$50 | ~$148-208 |
| **Savings** | **99%+** | **99%+** | **99%+** |

*Traditional costs assume: instructional designer ($75-150/hr), voice talent ($200-500/hr studio), illustrator ($50-100/illustration), video production ($1,000-5,000/min), development ($100-200/hr).*

---

### Cost Optimization Strategies

#### Batch Processing Discounts

Both OpenAI and Anthropic offer 50% discounts on batch API calls that complete within 24 hours. Structure the pipeline to separate time-sensitive work (interactive QA review) from batch-eligible work (initial content generation, assessment creation, image prompts).

```python
# Example: Batch content generation with OpenAI
import openai

client = openai.OpenAI()

# Create batch file with all module generation requests
requests = []
for i, module in enumerate(course_modules):
    requests.append({
        "custom_id": f"module-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Generate content for module: {module['title']}"}
            ],
        }
    })

# Write JSONL batch file
import json
with open("batch_input.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# Submit batch job (50% discount, completes within 24h)
batch_file = client.files.create(file=open("batch_input.jsonl", "rb"), purpose="batch")
batch_job = client.batches.create(input_file_id=batch_file.id, endpoint="/v1/chat/completions", completion_window="24h")
print(f"Batch job created: {batch_job.id}")
```

#### Caching and Reuse

**Asset reuse across courses:**
- Sound effects: Generate a master SFX library once (~$2), reuse across all courses
- Background music: Build a library of 20 tracks (~$8), tag by mood/tempo, reuse
- Style guide images: Generate style reference images once, use as guidance for all courses
- Voice config: Pre-select and test voices once, reuse voice IDs

**Prompt caching for LLM calls:**
```python
# Anthropic prompt caching: put the courseware system prompt in cache
# Saves 90% on cached input tokens after the first call
import anthropic

client = anthropic.Anthropic()

# The system prompt with course framework context is cached
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=[
        {
            "type": "text",
            "text": LARGE_SYSTEM_PROMPT,  # ~4000 tokens of courseware instructions
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": module_prompt}]
)
# Subsequent calls reuse the cached system prompt at 90% discount
```

**Localization reuse:**
- Generate base content in English, then translate (cheaper than regenerating)
- TTS: Only regenerate narration audio per locale (content structure is reused)
- Images: Most illustrations are language-neutral and need no regeneration
- Diagrams: Re-render Mermaid with translated labels (no API cost)

#### Open Source Alternatives for Cost-Sensitive Deployments

| Commercial Service | Open Source Alternative | Trade-off |
|-------------------|----------------------|-----------|
| ElevenLabs TTS | Coqui TTS / Bark / Piper | Lower quality, no cloning, requires GPU |
| OpenAI GPT Image | Stable Diffusion (self-hosted) | Requires GPU, less prompt adherence |
| Claude / GPT-4o | Llama 3 / Mistral (self-hosted) | Lower quality, requires significant GPU |
| HeyGen / Synthesia | SadTalker / Wav2Lip (self-hosted) | Much lower quality, limited avatars |
| ElevenLabs Music | MusicGen (Meta, self-hosted) | Shorter outputs, less control |
| ElevenLabs SFX | AudioLDM2 (self-hosted) | Lower quality, less variety |

**Fully self-hosted stack cost:** A single RTX 4090 workstation ($2,500-3,500) can run TTS + image generation + LLM inference (quantized). Ongoing cost is electricity only (~$30-50/month for heavy use). Break-even vs API at roughly 50-100 courses.

#### Self-Hosted vs API Decision Framework

```
Monthly course volume?
  ├─ < 5 courses/month ──▶ Use APIs (lower total cost, no ops burden)
  ├─ 5-20 courses/month ──▶ Hybrid (self-host images + TTS, API for LLM)
  └─ > 20 courses/month ──▶ Self-host core pipeline, API for premium features
```

| Factor | API | Self-Hosted |
|--------|-----|-------------|
| Upfront cost | $0 | $2,500-10,000 (GPU hardware) |
| Per-course cost | $20-200 | $1-5 (electricity) |
| Quality | State-of-the-art | Good (6-12 months behind) |
| Latency | Network-dependent | Local, fast |
| Scalability | Instant | Limited by hardware |
| Maintenance | Zero | Significant (model updates, drivers) |
| Privacy | Data sent to third parties | Full data control |

---

## Part 2: Learner Analytics Feedback Loop

### xAPI Statement Collection Architecture

Beyond simple completion tracking, capture granular learner behavior to drive content improvement.

#### What to Track

```
┌──────────────────────────────────────────────────────────────┐
│                    xAPI Statement Types                        │
│                                                                │
│  Navigation ──────── module/entered, module/exited             │
│  Content ─────────── page/viewed, video/played, video/paused  │
│  Interaction ─────── question/answered, drag-drop/completed   │
│  Branching ──────── scenario/choice-selected, path/completed  │
│  Assessment ─────── quiz/attempted, quiz/passed, quiz/failed  │
│  Engagement ─────── video/skipped, video/rewatched            │
│  Timing ─────────── duration per screen, idle detection       │
│  Completion ─────── module/completed, course/completed        │
└──────────────────────────────────────────────────────────────┘
```

#### Detailed Tracking Specifications

**Time per module/screen:**
```json
{
  "actor": { "mbox": "mailto:learner@example.com", "name": "Jane Doe" },
  "verb": { "id": "http://adlnet.gov/expapi/verbs/experienced", "display": { "en-US": "experienced" } },
  "object": {
    "id": "https://courses.example.com/course-101/module-3/screen-2",
    "definition": {
      "name": { "en-US": "Risk Assessment Framework" },
      "type": "http://adlnet.gov/expapi/activities/module"
    }
  },
  "result": {
    "duration": "PT3M24S"
  },
  "context": {
    "extensions": {
      "https://courses.example.com/xapi/idle-time": "PT0M12S",
      "https://courses.example.com/xapi/active-time": "PT3M12S",
      "https://courses.example.com/xapi/scroll-depth": 0.95
    }
  }
}
```

**Interaction attempts and correctness:**
```json
{
  "verb": { "id": "http://adlnet.gov/expapi/verbs/answered", "display": { "en-US": "answered" } },
  "object": {
    "id": "https://courses.example.com/course-101/module-3/quiz-1/q2",
    "definition": {
      "name": { "en-US": "Which risk category applies?" },
      "type": "http://adlnet.gov/expapi/activities/cmi.interaction",
      "interactionType": "choice",
      "correctResponsesPattern": ["operational"],
      "choices": [
        { "id": "operational", "description": { "en-US": "Operational Risk" } },
        { "id": "strategic", "description": { "en-US": "Strategic Risk" } },
        { "id": "financial", "description": { "en-US": "Financial Risk" } },
        { "id": "compliance", "description": { "en-US": "Compliance Risk" } }
      ]
    }
  },
  "result": {
    "response": "strategic",
    "success": false,
    "duration": "PT0M18S"
  },
  "context": {
    "extensions": {
      "https://courses.example.com/xapi/attempt-number": 1,
      "https://courses.example.com/xapi/learning-objective": "LO-3.2"
    }
  }
}
```

**Branch path selection:**
```json
{
  "verb": { "id": "https://courses.example.com/xapi/verbs/selected-path", "display": { "en-US": "selected path" } },
  "object": {
    "id": "https://courses.example.com/course-101/module-5/scenario-1/decision-2",
    "definition": {
      "name": { "en-US": "How do you handle the upset client?" },
      "type": "http://adlnet.gov/expapi/activities/cmi.interaction",
      "interactionType": "choice"
    }
  },
  "result": {
    "response": "empathize-first"
  },
  "context": {
    "extensions": {
      "https://courses.example.com/xapi/branch-path": ["intro", "discovery", "empathize-first"],
      "https://courses.example.com/xapi/scenario-id": "client-escalation",
      "https://courses.example.com/xapi/available-choices": ["empathize-first", "escalate-manager", "offer-discount"]
    }
  }
}
```

**Video engagement:**
```json
{
  "verb": { "id": "https://w3id.org/xapi/video/verbs/paused", "display": { "en-US": "paused" } },
  "object": {
    "id": "https://courses.example.com/course-101/module-2/video-intro",
    "definition": {
      "name": { "en-US": "Module 2 Introduction" },
      "type": "https://w3id.org/xapi/video/activity-type/video"
    }
  },
  "result": {
    "extensions": {
      "https://w3id.org/xapi/video/extensions/time": 45.2,
      "https://w3id.org/xapi/video/extensions/progress": 0.35,
      "https://w3id.org/xapi/video/extensions/played-segments": "0[.]30,32[.]45.2"
    }
  }
}
```

---

### Analytics Dashboard Metrics

#### Module-Level Completion Funnel

Track drop-off at each stage to identify where learners disengage.

```
Module 1: ████████████████████████████████████████ 100% started
           ██████████████████████████████████████   95% completed
Module 2: ██████████████████████████████████████   95% started
           ████████████████████████████████████     90% completed
Module 3: ████████████████████████████████████     88% started
           ██████████████████████████████         72% completed  ← investigate
Module 4: █████████████████████████████           70% started
           ████████████████████████               60% completed  ← flag
```

#### Assessment Item Difficulty Analysis

```
Item Analysis Report — Module 3 Quiz
─────────────────────────────────────────────────────────
Question    │ % Correct (1st)  │ Avg Attempts │ Flag
─────────────────────────────────────────────────────────
Q1          │      92%         │    1.1       │
Q2          │      78%         │    1.3       │
Q3          │      34%         │    2.4       │ ⚠ Too hard
Q4          │      85%         │    1.2       │
Q5          │      97%         │    1.0       │ ⚠ Too easy
─────────────────────────────────────────────────────────
Discrimination: Q3 has low point-biserial (0.12) — may be
testing something other than the learning objective.
```

#### Engagement Heat Map

Time spent per section relative to expected duration:

```
Module 3 — Expected: 6 min
─────────────────────────────────────────────
Section           │ Expected │ Actual  │ Ratio
─────────────────────────────────────────────
Intro             │  0:30    │  0:25   │ 0.83x
Concept explain   │  2:00    │  3:15   │ 1.63x  ← too dense?
Interactive demo  │  1:30    │  1:45   │ 1.17x
Practice quiz     │  1:00    │  1:50   │ 1.83x  ← struggling
Summary           │  1:00    │  0:20   │ 0.33x  ← skipping
─────────────────────────────────────────────
```

#### Branch Path Distribution

Flag scenarios where choices are too obvious:

```
Scenario: "Client Escalation" — Decision Point 2
─────────────────────────────────────────────
Choice              │ Selected │ Distribution
─────────────────────────────────────────────
Empathize first     │   847    │ ████████████████████████  84%  ⚠
Escalate to manager │   112    │ ███                       11%
Offer discount      │    51    │ █                          5%
─────────────────────────────────────────────
⚠ 84% chose same option — scenario may be too obvious.
  Consider making alternatives more plausible.
```

#### Pre/Post Score Comparison

```
Learning Objective Assessment — Course 101
─────────────────────────────────────────────────
Objective  │ Pre-Score │ Post-Score │ Gain  │ Effect
─────────────────────────────────────────────────
LO-1       │   42%     │    88%     │ +46%  │ Large
LO-2       │   38%     │    82%     │ +44%  │ Large
LO-3       │   55%     │    62%     │  +7%  │ Small  ← weak
LO-4       │   30%     │    79%     │ +49%  │ Large
LO-5       │   48%     │    51%     │  +3%  │ None   ← failing
─────────────────────────────────────────────────
LO-3 and LO-5 show minimal learning gains.
Investigate: content quality, assessment alignment, or
prerequisite knowledge gaps.
```

---

### Automated Improvement Triggers

Configure these thresholds to automatically flag content for revision.

```json
{
  "improvement_triggers": {
    "module_completion": {
      "threshold": 0.70,
      "comparison": "less_than",
      "description": "Module completion rate below 70%",
      "action": "flag_for_review",
      "severity": "high",
      "min_sample_size": 30
    },
    "assessment_item_difficulty": {
      "threshold": 0.40,
      "comparison": "less_than",
      "description": "Assessment item correct rate below 40% on first attempt",
      "action": "flag_item_for_revision",
      "severity": "high",
      "min_sample_size": 20
    },
    "time_deviation_above": {
      "threshold": 1.8,
      "comparison": "greater_than",
      "description": "Average time >1.8x expected duration (content too dense)",
      "action": "flag_for_simplification",
      "severity": "medium",
      "min_sample_size": 25
    },
    "time_deviation_below": {
      "threshold": 0.3,
      "comparison": "less_than",
      "description": "Average time <0.3x expected (learners skipping)",
      "action": "flag_for_engagement_review",
      "severity": "medium",
      "min_sample_size": 25
    },
    "uniform_branch_choice": {
      "threshold": 0.80,
      "comparison": "greater_than",
      "description": ">80% of learners pick the same branch option",
      "action": "flag_scenario_for_rewrite",
      "severity": "medium",
      "min_sample_size": 50
    },
    "video_skip_rate": {
      "threshold": 0.50,
      "comparison": "greater_than",
      "description": ">50% of learners skip or fast-forward past video",
      "action": "flag_video_for_replacement",
      "severity": "medium",
      "min_sample_size": 30
    },
    "low_learning_gain": {
      "threshold": 0.10,
      "comparison": "less_than",
      "description": "Pre/post score gain <10% for a learning objective",
      "action": "flag_objective_content",
      "severity": "high",
      "min_sample_size": 40
    }
  }
}
```

#### Trigger Evaluation Script

```python
#!/usr/bin/env python3
"""Evaluate analytics triggers against LRS data."""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class TriggerAlert:
    trigger_name: str
    severity: str
    course_id: str
    target_id: str  # module, item, or scenario ID
    metric_value: float
    threshold: float
    sample_size: int
    description: str


def evaluate_module_completion(lrs_client, course_id: str, trigger_config: dict) -> list[TriggerAlert]:
    """Check module completion rates against threshold."""
    alerts = []
    config = trigger_config["module_completion"]

    modules = lrs_client.query_aggregate(
        verb="http://adlnet.gov/expapi/verbs/completed",
        activity_type="http://adlnet.gov/expapi/activities/module",
        course_id=course_id,
        group_by="object.id",
        since=datetime.now() - timedelta(days=30),
    )

    for module_id, stats in modules.items():
        started = stats["started_count"]
        completed = stats["completed_count"]

        if started < config["min_sample_size"]:
            continue

        completion_rate = completed / started
        if completion_rate < config["threshold"]:
            alerts.append(TriggerAlert(
                trigger_name="module_completion",
                severity=config["severity"],
                course_id=course_id,
                target_id=module_id,
                metric_value=completion_rate,
                threshold=config["threshold"],
                sample_size=started,
                description=f"Module completion {completion_rate:.0%} < {config['threshold']:.0%} threshold",
            ))

    return alerts


def evaluate_assessment_items(lrs_client, course_id: str, trigger_config: dict) -> list[TriggerAlert]:
    """Check individual assessment item difficulty."""
    alerts = []
    config = trigger_config["assessment_item_difficulty"]

    items = lrs_client.query_aggregate(
        verb="http://adlnet.gov/expapi/verbs/answered",
        course_id=course_id,
        group_by="object.id",
        filter={"context.extensions.attempt-number": 1},  # First attempt only
        since=datetime.now() - timedelta(days=30),
    )

    for item_id, stats in items.items():
        attempts = stats["total_count"]
        correct = stats["success_count"]

        if attempts < config["min_sample_size"]:
            continue

        correct_rate = correct / attempts
        if correct_rate < config["threshold"]:
            alerts.append(TriggerAlert(
                trigger_name="assessment_item_difficulty",
                severity=config["severity"],
                course_id=course_id,
                target_id=item_id,
                metric_value=correct_rate,
                threshold=config["threshold"],
                sample_size=attempts,
                description=f"Item correct rate {correct_rate:.0%} < {config['threshold']:.0%} threshold",
            ))

    return alerts


def evaluate_branch_distribution(lrs_client, course_id: str, trigger_config: dict) -> list[TriggerAlert]:
    """Check if branch choices are too uniform."""
    alerts = []
    config = trigger_config["uniform_branch_choice"]

    decisions = lrs_client.query_aggregate(
        verb="https://courses.example.com/xapi/verbs/selected-path",
        course_id=course_id,
        group_by=["object.id", "result.response"],
        since=datetime.now() - timedelta(days=30),
    )

    for decision_id, choices in decisions.items():
        total = sum(c["count"] for c in choices.values())
        if total < config["min_sample_size"]:
            continue

        max_choice_pct = max(c["count"] / total for c in choices.values())
        if max_choice_pct > config["threshold"]:
            alerts.append(TriggerAlert(
                trigger_name="uniform_branch_choice",
                severity=config["severity"],
                course_id=course_id,
                target_id=decision_id,
                metric_value=max_choice_pct,
                threshold=config["threshold"],
                sample_size=total,
                description=f"Branch choice {max_choice_pct:.0%} uniform > {config['threshold']:.0%} threshold",
            ))

    return alerts


def run_all_triggers(lrs_client, course_id: str, config_path: str) -> list[TriggerAlert]:
    """Run all configured triggers and return alerts."""
    with open(config_path) as f:
        config = json.load(f)["improvement_triggers"]

    alerts = []
    alerts.extend(evaluate_module_completion(lrs_client, course_id, config))
    alerts.extend(evaluate_assessment_items(lrs_client, course_id, config))
    alerts.extend(evaluate_branch_distribution(lrs_client, course_id, config))
    # ... additional trigger evaluators

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    alerts.sort(key=lambda a: severity_order.get(a.severity, 3))

    return alerts
```

---

### Implementation: xAPI Statements from the Course Player

#### Course Player xAPI Module (TypeScript)

```typescript
// analytics/xapi-tracker.ts

interface XAPIConfig {
  endpoint: string;
  auth: string;  // Basic auth token
  courseIRI: string;
  courseName: string;
}

interface Actor {
  mbox: string;
  name: string;
}

class CourseXAPITracker {
  private config: XAPIConfig;
  private actor: Actor;
  private statementQueue: object[] = [];
  private flushInterval: ReturnType<typeof setInterval>;

  constructor(config: XAPIConfig, actor: Actor) {
    this.config = config;
    this.actor = actor;

    // Batch-send statements every 10 seconds
    this.flushInterval = setInterval(() => this.flush(), 10_000);

    // Flush on page unload
    window.addEventListener("beforeunload", () => this.flush());
  }

  // --- Core statement builder ---

  private buildStatement(verb: string, verbDisplay: string, object: object, result?: object, contextExtensions?: Record<string, unknown>) {
    const statement: Record<string, unknown> = {
      actor: {
        mbox: this.actor.mbox,
        name: this.actor.name,
        objectType: "Agent",
      },
      verb: {
        id: verb,
        display: { "en-US": verbDisplay },
      },
      object,
      timestamp: new Date().toISOString(),
      context: {
        contextActivities: {
          parent: [{
            id: this.config.courseIRI,
            definition: {
              name: { "en-US": this.config.courseName },
              type: "http://adlnet.gov/expapi/activities/course",
            },
          }],
        },
        ...(contextExtensions ? { extensions: contextExtensions } : {}),
      },
    };

    if (result) {
      statement.result = result;
    }

    this.statementQueue.push(statement);
  }

  // --- Tracking methods ---

  trackModuleEntered(moduleId: string, moduleName: string) {
    this.buildStatement(
      "http://adlnet.gov/expapi/verbs/initialized",
      "initialized",
      {
        id: `${this.config.courseIRI}/module/${moduleId}`,
        definition: {
          name: { "en-US": moduleName },
          type: "http://adlnet.gov/expapi/activities/module",
        },
      }
    );
  }

  trackModuleCompleted(moduleId: string, moduleName: string, durationSeconds: number) {
    this.buildStatement(
      "http://adlnet.gov/expapi/verbs/completed",
      "completed",
      {
        id: `${this.config.courseIRI}/module/${moduleId}`,
        definition: {
          name: { "en-US": moduleName },
          type: "http://adlnet.gov/expapi/activities/module",
        },
      },
      {
        completion: true,
        duration: `PT${Math.round(durationSeconds)}S`,
      }
    );
  }

  trackScreenViewed(moduleId: string, screenId: string, screenName: string, durationSeconds: number, scrollDepth: number) {
    this.buildStatement(
      "http://adlnet.gov/expapi/verbs/experienced",
      "experienced",
      {
        id: `${this.config.courseIRI}/module/${moduleId}/screen/${screenId}`,
        definition: {
          name: { "en-US": screenName },
          type: "http://adlnet.gov/expapi/activities/page",
        },
      },
      { duration: `PT${Math.round(durationSeconds)}S` },
      {
        "https://courses.example.com/xapi/scroll-depth": scrollDepth,
        "https://courses.example.com/xapi/active-time": `PT${Math.round(durationSeconds)}S`,
      }
    );
  }

  trackQuestionAnswered(
    moduleId: string,
    questionId: string,
    questionText: string,
    response: string,
    correct: boolean,
    attemptNumber: number,
    durationSeconds: number,
    learningObjective: string,
  ) {
    this.buildStatement(
      "http://adlnet.gov/expapi/verbs/answered",
      "answered",
      {
        id: `${this.config.courseIRI}/module/${moduleId}/question/${questionId}`,
        definition: {
          name: { "en-US": questionText },
          type: "http://adlnet.gov/expapi/activities/cmi.interaction",
          interactionType: "choice",
        },
      },
      {
        response,
        success: correct,
        duration: `PT${Math.round(durationSeconds)}S`,
      },
      {
        "https://courses.example.com/xapi/attempt-number": attemptNumber,
        "https://courses.example.com/xapi/learning-objective": learningObjective,
      }
    );
  }

  trackBranchChoice(
    moduleId: string,
    decisionId: string,
    decisionText: string,
    choiceId: string,
    availableChoices: string[],
    pathSoFar: string[],
    scenarioId: string,
  ) {
    this.buildStatement(
      "https://courses.example.com/xapi/verbs/selected-path",
      "selected path",
      {
        id: `${this.config.courseIRI}/module/${moduleId}/scenario/${scenarioId}/decision/${decisionId}`,
        definition: {
          name: { "en-US": decisionText },
          type: "http://adlnet.gov/expapi/activities/cmi.interaction",
          interactionType: "choice",
        },
      },
      { response: choiceId },
      {
        "https://courses.example.com/xapi/branch-path": pathSoFar,
        "https://courses.example.com/xapi/scenario-id": scenarioId,
        "https://courses.example.com/xapi/available-choices": availableChoices,
      }
    );
  }

  trackVideoEvent(
    moduleId: string,
    videoId: string,
    videoName: string,
    event: "played" | "paused" | "seeked" | "completed",
    currentTime: number,
    duration: number,
    playedSegments: string,
  ) {
    const verbMap = {
      played: "https://w3id.org/xapi/video/verbs/played",
      paused: "https://w3id.org/xapi/video/verbs/paused",
      seeked: "https://w3id.org/xapi/video/verbs/seeked",
      completed: "http://adlnet.gov/expapi/verbs/completed",
    };

    this.buildStatement(
      verbMap[event],
      event,
      {
        id: `${this.config.courseIRI}/module/${moduleId}/video/${videoId}`,
        definition: {
          name: { "en-US": videoName },
          type: "https://w3id.org/xapi/video/activity-type/video",
        },
      },
      {
        extensions: {
          "https://w3id.org/xapi/video/extensions/time": currentTime,
          "https://w3id.org/xapi/video/extensions/progress": duration > 0 ? currentTime / duration : 0,
          "https://w3id.org/xapi/video/extensions/played-segments": playedSegments,
        },
      }
    );
  }

  // --- Network layer ---

  async flush() {
    if (this.statementQueue.length === 0) return;

    const statements = [...this.statementQueue];
    this.statementQueue = [];

    try {
      const response = await fetch(`${this.config.endpoint}/statements`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Basic ${this.config.auth}`,
          "X-Experience-API-Version": "1.0.3",
        },
        body: JSON.stringify(statements),
      });

      if (!response.ok) {
        // Re-queue on failure
        console.error(`xAPI send failed (${response.status}), re-queuing ${statements.length} statements`);
        this.statementQueue.unshift(...statements);
      }
    } catch (err) {
      console.error("xAPI send error, re-queuing:", err);
      this.statementQueue.unshift(...statements);
    }
  }

  destroy() {
    clearInterval(this.flushInterval);
    this.flush();
  }
}

export { CourseXAPITracker, type XAPIConfig, type Actor };
```

#### Usage in the Course Player

```typescript
// course-player.ts
import { CourseXAPITracker } from "./analytics/xapi-tracker";

const tracker = new CourseXAPITracker(
  {
    endpoint: "https://lrs.example.com/xapi",
    auth: btoa("api-key:api-secret"),
    courseIRI: "https://courses.example.com/course-101",
    courseName: "Risk Management Fundamentals",
  },
  {
    mbox: `mailto:${currentUser.email}`,
    name: currentUser.displayName,
  }
);

// When learner enters a module
tracker.trackModuleEntered("module-3", "Risk Assessment Framework");

// When learner views a screen (called on navigation away)
tracker.trackScreenViewed("module-3", "screen-2", "Identifying Risk Categories", 194, 0.95);

// When learner answers a question
tracker.trackQuestionAnswered(
  "module-3", "q2",
  "Which risk category applies to this scenario?",
  "strategic", false, 1, 18, "LO-3.2"
);

// When learner makes a branching choice
tracker.trackBranchChoice(
  "module-5", "decision-2",
  "How do you handle the upset client?",
  "empathize-first",
  ["empathize-first", "escalate-manager", "offer-discount"],
  ["intro", "discovery", "empathize-first"],
  "client-escalation"
);

// When learner interacts with video
tracker.trackVideoEvent("module-2", "intro-video", "Module 2 Introduction", "paused", 45.2, 128, "0[.]30,32[.]45.2");
```

---

### Querying an LRS for Analytics Data

#### LRS Query Functions (Python)

```python
#!/usr/bin/env python3
"""Query an xAPI Learning Record Store for analytics data."""

import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode


class LRSClient:
    """Simple xAPI LRS client for analytics queries."""

    def __init__(self, endpoint: str, auth_token: str):
        self.endpoint = endpoint.rstrip("/")
        self.headers = {
            "Authorization": f"Basic {auth_token}",
            "X-Experience-API-Version": "1.0.3",
            "Content-Type": "application/json",
        }

    def get_statements(self, params: dict) -> list[dict]:
        """Fetch statements with pagination."""
        statements = []
        url = f"{self.endpoint}/statements?{urlencode(params)}"

        while url:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            statements.extend(data.get("statements", []))
            # Follow 'more' link for pagination
            more = data.get("more")
            url = f"{self.endpoint}{more}" if more else None

        return statements

    # --- Analytics Queries ---

    def module_completion_rates(self, course_iri: str, since_days: int = 30) -> dict:
        """Calculate completion rate per module."""
        since = (datetime.utcnow() - timedelta(days=since_days)).isoformat() + "Z"

        # Get all 'initialized' statements (module starts)
        starts = self.get_statements({
            "verb": "http://adlnet.gov/expapi/verbs/initialized",
            "activity": course_iri,
            "related_activities": "true",
            "since": since,
            "limit": 0,
        })

        # Get all 'completed' statements (module completions)
        completions = self.get_statements({
            "verb": "http://adlnet.gov/expapi/verbs/completed",
            "activity": course_iri,
            "related_activities": "true",
            "since": since,
            "limit": 0,
        })

        # Count unique actors per module
        start_counts: dict[str, set] = {}
        for s in starts:
            obj_id = s["object"]["id"]
            actor = s["actor"].get("mbox", s["actor"].get("account", {}).get("name", "unknown"))
            start_counts.setdefault(obj_id, set()).add(actor)

        completion_counts: dict[str, set] = {}
        for s in completions:
            obj_id = s["object"]["id"]
            actor = s["actor"].get("mbox", s["actor"].get("account", {}).get("name", "unknown"))
            completion_counts.setdefault(obj_id, set()).add(actor)

        # Calculate rates
        rates = {}
        for module_id, starters in start_counts.items():
            completers = completion_counts.get(module_id, set())
            rates[module_id] = {
                "started": len(starters),
                "completed": len(completers),
                "rate": len(completers) / len(starters) if starters else 0,
            }

        return rates

    def assessment_item_analysis(self, course_iri: str, since_days: int = 30) -> dict:
        """Analyze per-item difficulty and discrimination."""
        since = (datetime.utcnow() - timedelta(days=since_days)).isoformat() + "Z"

        answers = self.get_statements({
            "verb": "http://adlnet.gov/expapi/verbs/answered",
            "activity": course_iri,
            "related_activities": "true",
            "since": since,
            "limit": 0,
        })

        items: dict[str, dict] = {}
        for s in answers:
            item_id = s["object"]["id"]
            success = s.get("result", {}).get("success", False)
            attempt = s.get("context", {}).get("extensions", {}).get(
                "https://courses.example.com/xapi/attempt-number", 1
            )

            if item_id not in items:
                items[item_id] = {
                    "name": s["object"].get("definition", {}).get("name", {}).get("en-US", item_id),
                    "first_attempt_correct": 0,
                    "first_attempt_total": 0,
                    "total_attempts": 0,
                    "total_correct": 0,
                }

            items[item_id]["total_attempts"] += 1
            if success:
                items[item_id]["total_correct"] += 1
            if attempt == 1:
                items[item_id]["first_attempt_total"] += 1
                if success:
                    items[item_id]["first_attempt_correct"] += 1

        # Compute metrics
        for item_id, data in items.items():
            total = data["first_attempt_total"]
            data["difficulty"] = data["first_attempt_correct"] / total if total > 0 else 0
            data["avg_attempts"] = data["total_attempts"] / total if total > 0 else 0

        return items

    def branch_path_distribution(self, course_iri: str, since_days: int = 30) -> dict:
        """Analyze how learners distribute across branching choices."""
        since = (datetime.utcnow() - timedelta(days=since_days)).isoformat() + "Z"

        choices = self.get_statements({
            "verb": "https://courses.example.com/xapi/verbs/selected-path",
            "activity": course_iri,
            "related_activities": "true",
            "since": since,
            "limit": 0,
        })

        decisions: dict[str, dict[str, int]] = {}
        for s in choices:
            decision_id = s["object"]["id"]
            response = s.get("result", {}).get("response", "unknown")
            decisions.setdefault(decision_id, {})
            decisions[decision_id][response] = decisions[decision_id].get(response, 0) + 1

        # Compute uniformity
        result = {}
        for decision_id, choice_counts in decisions.items():
            total = sum(choice_counts.values())
            max_pct = max(choice_counts.values()) / total if total > 0 else 0
            result[decision_id] = {
                "choices": {k: {"count": v, "pct": v / total} for k, v in choice_counts.items()},
                "total": total,
                "max_choice_pct": max_pct,
                "flagged": max_pct > 0.80,
            }

        return result

    def time_per_screen(self, course_iri: str, since_days: int = 30) -> dict:
        """Analyze average time per screen."""
        since = (datetime.utcnow() - timedelta(days=since_days)).isoformat() + "Z"

        experiences = self.get_statements({
            "verb": "http://adlnet.gov/expapi/verbs/experienced",
            "activity": course_iri,
            "related_activities": "true",
            "since": since,
            "limit": 0,
        })

        screens: dict[str, list[float]] = {}
        for s in experiences:
            screen_id = s["object"]["id"]
            duration_str = s.get("result", {}).get("duration", "")
            if duration_str:
                # Parse ISO 8601 duration (simplified: PTnS format)
                seconds = _parse_duration(duration_str)
                screens.setdefault(screen_id, []).append(seconds)

        return {
            screen_id: {
                "avg_seconds": sum(times) / len(times),
                "median_seconds": sorted(times)[len(times) // 2],
                "count": len(times),
            }
            for screen_id, times in screens.items()
        }


def _parse_duration(iso_duration: str) -> float:
    """Parse ISO 8601 duration to seconds (handles PTnMnS and PTnS)."""
    import re
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?", iso_duration)
    if not match:
        return 0.0
    hours = float(match.group(1) or 0)
    minutes = float(match.group(2) or 0)
    seconds = float(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds
```

---

### Simple Dashboard Queries

#### Express.js Dashboard API

```typescript
// dashboard/routes/analytics.ts
import { Router, Request, Response } from "express";
import { LRSClient } from "../lib/lrs-client";

const router = Router();
const lrs = new LRSClient(process.env.LRS_ENDPOINT!, process.env.LRS_AUTH_TOKEN!);

/**
 * GET /api/analytics/:courseId/completion-funnel
 * Returns module-by-module completion funnel data.
 */
router.get("/:courseId/completion-funnel", async (req: Request, res: Response) => {
  const { courseId } = req.params;
  const days = parseInt(req.query.days as string) || 30;
  const courseIRI = `https://courses.example.com/${courseId}`;

  // Query initialized and completed statements
  const [starts, completions] = await Promise.all([
    lrs.getStatements({
      verb: "http://adlnet.gov/expapi/verbs/initialized",
      activity: courseIRI,
      related_activities: true,
      since: daysAgo(days),
    }),
    lrs.getStatements({
      verb: "http://adlnet.gov/expapi/verbs/completed",
      activity: courseIRI,
      related_activities: true,
      since: daysAgo(days),
    }),
  ]);

  // Group by module, count unique actors
  const funnel = buildCompletionFunnel(starts, completions);

  res.json({
    courseId,
    period: `${days} days`,
    modules: funnel,
  });
});

/**
 * GET /api/analytics/:courseId/item-analysis
 * Returns assessment item difficulty analysis.
 */
router.get("/:courseId/item-analysis", async (req: Request, res: Response) => {
  const { courseId } = req.params;
  const days = parseInt(req.query.days as string) || 30;
  const courseIRI = `https://courses.example.com/${courseId}`;

  const answers = await lrs.getStatements({
    verb: "http://adlnet.gov/expapi/verbs/answered",
    activity: courseIRI,
    related_activities: true,
    since: daysAgo(days),
  });

  const items = analyzeItems(answers);

  // Flag items outside acceptable difficulty range
  const flagged = items.filter(
    (item) => item.firstAttemptCorrectRate < 0.40 || item.firstAttemptCorrectRate > 0.95
  );

  res.json({
    courseId,
    period: `${days} days`,
    items,
    flagged,
  });
});

/**
 * GET /api/analytics/:courseId/engagement-heatmap
 * Returns time-per-screen data compared to expected durations.
 */
router.get("/:courseId/engagement-heatmap", async (req: Request, res: Response) => {
  const { courseId } = req.params;
  const days = parseInt(req.query.days as string) || 30;
  const courseIRI = `https://courses.example.com/${courseId}`;

  const experiences = await lrs.getStatements({
    verb: "http://adlnet.gov/expapi/verbs/experienced",
    activity: courseIRI,
    related_activities: true,
    since: daysAgo(days),
  });

  const screenTimes = aggregateScreenTimes(experiences);

  res.json({
    courseId,
    period: `${days} days`,
    screens: screenTimes,
  });
});

/**
 * GET /api/analytics/:courseId/branch-distribution
 * Returns branch path analysis for scenarios.
 */
router.get("/:courseId/branch-distribution", async (req: Request, res: Response) => {
  const { courseId } = req.params;
  const days = parseInt(req.query.days as string) || 30;
  const courseIRI = `https://courses.example.com/${courseId}`;

  const pathSelections = await lrs.getStatements({
    verb: "https://courses.example.com/xapi/verbs/selected-path",
    activity: courseIRI,
    related_activities: true,
    since: daysAgo(days),
  });

  const distribution = analyzeBranchPaths(pathSelections);

  res.json({
    courseId,
    period: `${days} days`,
    decisions: distribution,
  });
});

/**
 * GET /api/analytics/:courseId/triggers
 * Evaluate all automated improvement triggers.
 */
router.get("/:courseId/triggers", async (req: Request, res: Response) => {
  const { courseId } = req.params;
  const courseIRI = `https://courses.example.com/${courseId}`;

  const alerts = await evaluateAllTriggers(lrs, courseIRI);

  res.json({
    courseId,
    alerts,
    summary: {
      high: alerts.filter((a) => a.severity === "high").length,
      medium: alerts.filter((a) => a.severity === "medium").length,
      low: alerts.filter((a) => a.severity === "low").length,
    },
  });
});

// --- Helpers ---

function daysAgo(n: number): string {
  return new Date(Date.now() - n * 86400000).toISOString();
}

function buildCompletionFunnel(starts: any[], completions: any[]) {
  const modules = new Map<string, { started: Set<string>; completed: Set<string>; name: string }>();

  for (const s of starts) {
    const id = s.object.id;
    const actor = s.actor.mbox || s.actor.account?.name || "unknown";
    if (!modules.has(id)) {
      modules.set(id, {
        started: new Set(),
        completed: new Set(),
        name: s.object.definition?.name?.["en-US"] || id,
      });
    }
    modules.get(id)!.started.add(actor);
  }

  for (const s of completions) {
    const id = s.object.id;
    const actor = s.actor.mbox || s.actor.account?.name || "unknown";
    modules.get(id)?.completed.add(actor);
  }

  return Array.from(modules.entries()).map(([id, data]) => ({
    moduleId: id,
    moduleName: data.name,
    started: data.started.size,
    completed: data.completed.size,
    completionRate: data.started.size > 0 ? data.completed.size / data.started.size : 0,
  }));
}

function analyzeItems(answers: any[]) {
  const items = new Map<string, {
    name: string;
    firstAttemptTotal: number;
    firstAttemptCorrect: number;
    totalAttempts: number;
  }>();

  for (const s of answers) {
    const id = s.object.id;
    const success = s.result?.success ?? false;
    const attempt = s.context?.extensions?.["https://courses.example.com/xapi/attempt-number"] ?? 1;

    if (!items.has(id)) {
      items.set(id, {
        name: s.object.definition?.name?.["en-US"] || id,
        firstAttemptTotal: 0,
        firstAttemptCorrect: 0,
        totalAttempts: 0,
      });
    }

    const item = items.get(id)!;
    item.totalAttempts++;
    if (attempt === 1) {
      item.firstAttemptTotal++;
      if (success) item.firstAttemptCorrect++;
    }
  }

  return Array.from(items.entries()).map(([id, data]) => ({
    itemId: id,
    itemName: data.name,
    firstAttemptCorrectRate: data.firstAttemptTotal > 0 ? data.firstAttemptCorrect / data.firstAttemptTotal : 0,
    avgAttempts: data.firstAttemptTotal > 0 ? data.totalAttempts / data.firstAttemptTotal : 0,
    sampleSize: data.firstAttemptTotal,
  }));
}

function aggregateScreenTimes(experiences: any[]) {
  const screens = new Map<string, { name: string; durations: number[] }>();

  for (const s of experiences) {
    const id = s.object.id;
    const duration = parseDuration(s.result?.duration || "");
    if (duration <= 0) continue;

    if (!screens.has(id)) {
      screens.set(id, {
        name: s.object.definition?.name?.["en-US"] || id,
        durations: [],
      });
    }
    screens.get(id)!.durations.push(duration);
  }

  return Array.from(screens.entries()).map(([id, data]) => {
    const sorted = [...data.durations].sort((a, b) => a - b);
    return {
      screenId: id,
      screenName: data.name,
      avgSeconds: data.durations.reduce((a, b) => a + b, 0) / data.durations.length,
      medianSeconds: sorted[Math.floor(sorted.length / 2)],
      sampleSize: data.durations.length,
    };
  });
}

function analyzeBranchPaths(selections: any[]) {
  const decisions = new Map<string, Map<string, number>>();

  for (const s of selections) {
    const id = s.object.id;
    const choice = s.result?.response || "unknown";
    if (!decisions.has(id)) decisions.set(id, new Map());
    const choiceCounts = decisions.get(id)!;
    choiceCounts.set(choice, (choiceCounts.get(choice) || 0) + 1);
  }

  return Array.from(decisions.entries()).map(([id, choices]) => {
    const total = Array.from(choices.values()).reduce((a, b) => a + b, 0);
    const maxPct = Math.max(...Array.from(choices.values())) / total;
    return {
      decisionId: id,
      total,
      choices: Object.fromEntries(
        Array.from(choices.entries()).map(([k, v]) => [k, { count: v, pct: v / total }])
      ),
      maxChoicePct: maxPct,
      flagged: maxPct > 0.80,
    };
  });
}

async function evaluateAllTriggers(lrs: any, courseIRI: string) {
  // Implementation delegates to the trigger evaluation logic
  // described in the "Automated Improvement Triggers" section
  return [];
}

function parseDuration(iso: string): number {
  const match = iso.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?/);
  if (!match) return 0;
  return (parseFloat(match[1] || "0") * 3600) +
         (parseFloat(match[2] || "0") * 60) +
         parseFloat(match[3] || "0");
}

export default router;
```

#### SQL Queries for Analytics (if using a SQL-backed LRS)

For LRS implementations that store xAPI data in SQL (e.g., a custom Postgres-backed LRS), these queries power the dashboard directly:

```sql
-- Module completion funnel
SELECT
    s.object_id AS module_id,
    s.object_name AS module_name,
    COUNT(DISTINCT CASE WHEN s.verb_id = 'http://adlnet.gov/expapi/verbs/initialized'
          THEN s.actor_id END) AS started,
    COUNT(DISTINCT CASE WHEN s.verb_id = 'http://adlnet.gov/expapi/verbs/completed'
          THEN s.actor_id END) AS completed,
    ROUND(
        COUNT(DISTINCT CASE WHEN s.verb_id = 'http://adlnet.gov/expapi/verbs/completed'
              THEN s.actor_id END)::numeric /
        NULLIF(COUNT(DISTINCT CASE WHEN s.verb_id = 'http://adlnet.gov/expapi/verbs/initialized'
              THEN s.actor_id END), 0),
        3
    ) AS completion_rate
FROM xapi_statements s
WHERE s.context_parent_id = 'https://courses.example.com/course-101'
  AND s.verb_id IN (
      'http://adlnet.gov/expapi/verbs/initialized',
      'http://adlnet.gov/expapi/verbs/completed'
  )
  AND s.object_type = 'http://adlnet.gov/expapi/activities/module'
  AND s.timestamp >= NOW() - INTERVAL '30 days'
GROUP BY s.object_id, s.object_name
ORDER BY s.object_id;

-- Assessment item difficulty (first attempt only)
SELECT
    s.object_id AS item_id,
    s.object_name AS item_name,
    COUNT(*) AS first_attempts,
    SUM(CASE WHEN s.result_success THEN 1 ELSE 0 END) AS correct,
    ROUND(
        SUM(CASE WHEN s.result_success THEN 1 ELSE 0 END)::numeric / COUNT(*),
        3
    ) AS difficulty,
    AVG(s.result_duration_seconds) AS avg_time_seconds
FROM xapi_statements s
WHERE s.context_parent_id = 'https://courses.example.com/course-101'
  AND s.verb_id = 'http://adlnet.gov/expapi/verbs/answered'
  AND (s.context_extensions->>'https://courses.example.com/xapi/attempt-number')::int = 1
  AND s.timestamp >= NOW() - INTERVAL '30 days'
GROUP BY s.object_id, s.object_name
HAVING COUNT(*) >= 20
ORDER BY difficulty ASC;

-- Branch path distribution with uniformity flag
SELECT
    s.object_id AS decision_id,
    s.result_response AS choice,
    COUNT(*) AS times_chosen,
    ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER (PARTITION BY s.object_id), 3) AS pct,
    CASE
        WHEN ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER (PARTITION BY s.object_id), 3) > 0.80
        THEN true ELSE false
    END AS flagged
FROM xapi_statements s
WHERE s.context_parent_id = 'https://courses.example.com/course-101'
  AND s.verb_id = 'https://courses.example.com/xapi/verbs/selected-path'
  AND s.timestamp >= NOW() - INTERVAL '30 days'
GROUP BY s.object_id, s.result_response
ORDER BY s.object_id, times_chosen DESC;

-- Engagement heat map: actual vs expected time per screen
SELECT
    s.object_id AS screen_id,
    s.object_name AS screen_name,
    COUNT(*) AS learner_count,
    ROUND(AVG(s.result_duration_seconds), 1) AS avg_seconds,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY s.result_duration_seconds), 1) AS median_seconds,
    e.expected_seconds,
    ROUND(AVG(s.result_duration_seconds) / NULLIF(e.expected_seconds, 0), 2) AS time_ratio
FROM xapi_statements s
LEFT JOIN course_screen_metadata e ON e.screen_iri = s.object_id
WHERE s.context_parent_id = 'https://courses.example.com/course-101'
  AND s.verb_id = 'http://adlnet.gov/expapi/verbs/experienced'
  AND s.timestamp >= NOW() - INTERVAL '30 days'
GROUP BY s.object_id, s.object_name, e.expected_seconds
HAVING COUNT(*) >= 10
ORDER BY time_ratio DESC;
```
