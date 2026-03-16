# Agent Workflows Reference

Detailed guide for multi-agent courseware creation pipelines.

## Pipeline Overview

Agent-driven course creation uses specialized agents that collaborate in a structured pipeline with human checkpoints. The pipeline mirrors professional instructional design workflows but accelerates them from weeks to hours.

```
SME Input ──▶ Research ──▶ Structure ──▶ Write ──▶ Media ──▶ QA ──▶ Package
                │              │           │         │        │
                ▼              ▼           ▼         ▼        ▼
            Research       Course      Content   Generated  Quality
             Brief         Map        Drafts     Assets    Report
                │              │           │         │        │
                ▼              ▼           ▼         ▼        ▼
            [Human]        [Human]     [Human]              [Human]
            Review         Approve     Review               Sign-off
```

## Agent Specifications

### Research Agent

**Purpose:** Gather, organize, and synthesize source materials into a structured research brief.

**Inputs:**
- SME-provided documents (PDFs, slides, videos, transcripts)
- Existing course materials for updates
- URLs to reference documentation
- Interview transcripts or notes

**Process:**
1. Ingest all source materials
2. Extract key concepts, facts, procedures, and examples
3. Identify knowledge gaps and ambiguities
4. Generate clarifying questions for SME
5. Organize into a structured research brief

**Output: Research Brief**

```json
{
  "course_topic": "Cloud Security Fundamentals",
  "source_materials": [
    { "title": "AWS Security Best Practices", "type": "pdf", "key_concepts": [...] },
    { "title": "SME Interview - Sarah Chen", "type": "transcript", "key_insights": [...] }
  ],
  "key_concepts": [
    {
      "concept": "Shared Responsibility Model",
      "definition": "AWS manages security OF the cloud; customer manages security IN the cloud",
      "importance": "foundational",
      "sources": ["aws-security-bp.pdf", "sme-interview-chen"],
      "examples": [...]
    }
  ],
  "knowledge_gaps": [
    "Need clarity on compliance requirements for specific industries",
    "Missing data on incident response procedures for multi-cloud"
  ],
  "sme_questions": [
    "What are the top 3 mistakes you see new teams make with IAM?",
    "Can you walk through a real incident response scenario?"
  ]
}
```

**Quality criteria:**
- Every fact traced to a source
- No unsourced claims
- Gaps explicitly identified (not filled with assumptions)

---

### Structure Agent

**Purpose:** Transform the research brief into a complete course architecture with learning objectives, module structure, and interaction selections.

**Inputs:**
- Research brief (from Research Agent)
- Target audience profile
- Time constraints (e.g., "30-minute course", "4-hour curriculum")
- Organizational learning objectives

**Process:**
1. Define behavioral learning objectives (what learners will *do*)
2. Organize concepts into modules and lessons
3. Select interaction patterns for each objective
4. Map assessments to objectives (coverage matrix)
5. Define prerequisite relationships
6. Estimate time per module

**Output: Course Map**

```json
{
  "course": {
    "title": "Cloud Security Fundamentals",
    "target_audience": "Software engineers moving to cloud-native development",
    "total_duration_minutes": 45,
    "completion_criteria": "Score ≥80% on all assessments, complete all scenarios"
  },
  "modules": [
    {
      "id": "01-shared-responsibility",
      "title": "Who Secures What?",
      "duration_minutes": 10,
      "objectives": [
        {
          "id": "obj-1",
          "text": "Correctly classify security responsibilities as customer vs. provider for 5 common services",
          "bloom_level": "application",
          "interaction": "drag-drop-sort",
          "assessment": "quiz-shared-responsibility"
        }
      ],
      "blocks": [
        { "type": "narrative", "description": "Opening scenario — new engineer deploys a misconfigured S3 bucket" },
        { "type": "scroll-story", "description": "Visual walkthrough of the shared responsibility model" },
        { "type": "drag-drop", "description": "Classify 10 items as customer or provider responsibility" },
        { "type": "branch", "description": "Scenario: production database exposed — what do you do?" },
        { "type": "knowledge-check", "description": "3 scenario-based questions on shared responsibility" }
      ]
    }
  ],
  "assessment_coverage": {
    "obj-1": ["quiz-shared-responsibility", "scenario-s3-breach"],
    "obj-2": ["quiz-iam", "drag-drop-policies"],
    "obj-3": ["scenario-incident-response"]
  }
}
```

**Quality criteria:**
- Every objective is behavioral and measurable ("classify", "respond", "identify" — not "understand")
- Every objective has at least one assessment
- Interaction types match the cognitive level (application → scenarios; knowledge → recall checks)
- Time estimates are realistic (not cramming 30 topics into 10 minutes)

---

### Writer Agent

**Purpose:** Draft all content blocks including narrative text, scenario dialogue, narration scripts, and assessment items.

**Inputs:**
- Course map (from Structure Agent)
- Research brief (from Research Agent)
- Brand voice guidelines
- Existing content (for updates)

**Process:**
1. For each module, generate content.json with all blocks
2. Write scenario narratives with character dialogue
3. Draft narration scripts (separate from on-screen text)
4. Create assessment items with elaborative feedback
5. Self-review against brand voice guidelines (use `human-writing` skill)

**Key guidelines:**
- Ground all content in source materials (RAG, not general knowledge)
- Write narration that complements visuals, never duplicates on-screen text
- Create feedback that explains *why*, not just "correct/incorrect"
- Use conversational tone, second person ("you'll notice", "try this")
- Avoid AI writing patterns (see `human-writing` skill)

**Output:** Complete `content.json` files for each module (see main SKILL.md for format).

---

### Media Agent

**Purpose:** Generate all multimedia assets.

**Inputs:**
- Content.json files with media prompts/descriptions
- Voice config (voice assignments)
- Style guide (illustration style, color palette)
- Audio config (music and SFX requirements)

**Process:**
1. Extract all narration_text blocks → batch TTS generation
2. Extract illustration_prompt blocks → image generation
3. Extract diagram_description blocks → Mermaid diagram generation
4. Generate course-wide audio (background music, sound effects)
5. Write all file paths back into content.json

**Orchestration:**

```python
# Media agent workflow
async def generate_all_media(course_dir: str):
    # These can run in parallel
    await asyncio.gather(
        generate_narration(course_dir),      # ElevenLabs TTS
        generate_illustrations(course_dir),   # OpenAI / Stable Diffusion
        generate_diagrams(course_dir),        # Mermaid.js
        generate_audio_assets(course_dir),    # ElevenLabs Music + SFX
    )

    # Then optimize
    await optimize_assets(course_dir)
```

See [multimedia-pipeline.md](multimedia-pipeline.md) for complete implementation.

---

### QA Agent

**Purpose:** Review all content against quality criteria before human review.

**Inputs:**
- Complete content.json files
- Generated media assets
- Source materials (for fact-checking)
- Accessibility requirements
- Brand voice guidelines

**Process:**

```python
def qa_review(module_path: str, source_docs: list, guidelines: dict) -> QAReport:
    report = QAReport()

    module = load_module(module_path)

    # 1. Factual accuracy
    for block in module["blocks"]:
        if block.get("text") or block.get("narration_text"):
            text = block.get("text", block.get("narration_text", ""))
            facts = extract_factual_claims(text)
            for fact in facts:
                if not verify_against_sources(fact, source_docs):
                    report.add_issue("factual", f"Unverified claim: {fact}", block)

    # 2. Learning objective alignment
    for objective in module.get("objectives", []):
        matching_blocks = find_blocks_for_objective(module, objective)
        if not matching_blocks:
            report.add_issue("alignment", f"No content for objective: {objective['text']}", None)
        matching_assessments = find_assessments_for_objective(module, objective)
        if not matching_assessments:
            report.add_issue("alignment", f"No assessment for objective: {objective['text']}", None)

    # 3. Accessibility
    for block in module["blocks"]:
        if block.get("image") and not block.get("alt_text"):
            report.add_issue("accessibility", "Image missing alt text", block)
        if block.get("type") == "drag-drop" and not block.get("keyboard_alternative"):
            report.add_issue("accessibility", "Drag-drop missing keyboard alternative", block)

    # 4. Redundancy check (narration vs on-screen text)
    for block in module["blocks"]:
        if block.get("text") and block.get("narration_text"):
            similarity = text_similarity(block["text"], block["narration_text"])
            if similarity > 0.8:
                report.add_issue("redundancy",
                    "Narration too similar to on-screen text (violates redundancy principle)",
                    block)

    # 5. Voice consistency
    all_text = extract_all_text(module)
    voice_issues = check_voice_consistency(all_text, guidelines.get("brand_voice"))
    for issue in voice_issues:
        report.add_issue("voice", issue, None)

    # 6. Assessment quality
    for block in module["blocks"]:
        if block.get("type") in ("knowledge-check", "quiz"):
            assess_quality = evaluate_assessment(block)
            for issue in assess_quality:
                report.add_issue("assessment", issue, block)

    return report
```

**QA Report Format:**

```json
{
  "module": "01-shared-responsibility",
  "timestamp": "2026-03-16T10:30:00Z",
  "overall_status": "needs_revision",
  "issues": [
    {
      "category": "factual",
      "severity": "high",
      "message": "Claim about '95% of breaches' not found in source materials",
      "block_index": 3,
      "suggestion": "Verify statistic or use sourced '74% involve human element' from Verizon DBIR"
    },
    {
      "category": "accessibility",
      "severity": "medium",
      "message": "Drag-drop interaction missing keyboard alternative",
      "block_index": 7,
      "suggestion": "Add select-then-place keyboard mode"
    }
  ],
  "metrics": {
    "total_blocks": 12,
    "blocks_with_issues": 3,
    "factual_issues": 1,
    "accessibility_issues": 1,
    "voice_issues": 1,
    "assessment_coverage": 0.85
  }
}
```

---

### Publish Agent

**Purpose:** Build, package, and deploy the course.

**Process:**
1. Run Vite build (`npm run build`)
2. Generate SCORM manifest (see [scorm-packaging.md](scorm-packaging.md))
3. Create SCORM ZIP package
4. Validate package structure
5. Deploy to preview environment
6. Optionally upload to SCORM Cloud for testing
7. Generate deployment report

```bash
# Automated publish pipeline
npm run build
npm run generate-manifest -- --scorm-version 2004
npm run package-scorm -- --output dist/course.zip
npm run validate-scorm -- --package dist/course.zip
npm run deploy-preview -- --url https://preview.example.com/courses/
```

---

## Generator-Critic Loop

The most effective pattern for quality content: one agent writes, another critiques, iterate.

```python
async def create_module_with_review(
    module_spec: dict,
    source_materials: list,
    brand_guidelines: dict,
    max_iterations: int = 3,
) -> dict:
    """Create a module using generator-critic loop."""

    # Initial draft
    draft = await writer_agent.generate(module_spec, source_materials)

    for iteration in range(max_iterations):
        # Critique
        review = await qa_agent.review(draft, {
            "source_materials": source_materials,
            "objectives": module_spec["objectives"],
            "brand_guidelines": brand_guidelines,
            "accessibility": "WCAG_AA",
        })

        if review.passes_all():
            print(f"Module approved after {iteration + 1} iteration(s)")
            return draft

        # Revise based on feedback
        print(f"Iteration {iteration + 1}: {len(review.issues)} issues found")
        draft = await writer_agent.revise(draft, review.feedback)

    # After max iterations, flag for human review
    print(f"Flagging for human review after {max_iterations} iterations")
    return {
        **draft,
        "_review_needed": True,
        "_outstanding_issues": review.issues,
    }
```

---

## SME Collaboration Workflow

### Structured SME Input

Instead of open-ended interviews, provide SMEs with structured templates:

```markdown
# Module Input Template

## Topic: [Module Title]

### Key concepts (list the 3-5 most important things learners must know):
1.
2.
3.

### Common mistakes (what do people get wrong about this?):
1.
2.

### Real-world scenario (describe a situation where this knowledge matters):
Setting:
What happens:
What the right response is:
What usually goes wrong:

### Assessment ideas (how would you test if someone understands this?):
1.
2.

### Resources (any specific documents, tools, or references):
-
```

### Review Interface

Provide SMEs with a structured review rather than asking them to read raw JSON:

```
┌─────────────────────────────────────────────────┐
│  Module Review: Who Secures What?               │
│                                                  │
│  Status: Draft — Awaiting SME Review             │
│                                                  │
│  ┌─────────────────────────────────────────────┐ │
│  │ Block 1: Opening Scenario                    │ │
│  │                                              │ │
│  │ "It's your first week managing cloud infra-  │ │
│  │  structure. A Slack message arrives: 'Hey,   │ │
│  │  someone posted on Twitter that they found   │ │
│  │  our customer data in a public S3 bucket.'"  │ │
│  │                                              │ │
│  │ [✓ Approve] [✏️ Edit] [❌ Reject] [💬 Comment] │ │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  ┌─────────────────────────────────────────────┐ │
│  │ Block 2: Shared Responsibility Explainer     │ │
│  │ ...                                          │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## Scaling Course Production

### Monorepo for Multiple Courses

```
courses/
├── packages/
│   ├── course-player/          # Shared player shell
│   ├── quiz-engine/            # Shared assessment engine
│   ├── interaction-library/    # Shared interaction components
│   ├── scorm-packager/         # SCORM packaging utility
│   └── media-pipeline/         # Asset generation + optimization
├── courses/
│   ├── security-101/           # Individual course
│   ├── onboarding-2026/
│   └── compliance-annual/
├── templates/
│   ├── course-template/        # Starter template for new courses
│   └── module-template/
├── turbo.json                  # Turborepo config
└── pnpm-workspace.yaml
```

### Creating a New Course from Template

```bash
# Clone template
cp -r templates/course-template courses/new-course-name

# Install dependencies
cd courses/new-course-name
pnpm install

# Initialize content structure
pnpm run init-course --title "New Course" --modules 5

# Start development
pnpm dev
```

### CI/CD for Course Content

```yaml
# .github/workflows/course-build.yml
name: Course Build

on:
  push:
    paths: ['courses/**']

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      courses: ${{ steps.changes.outputs.courses }}
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - id: changes
        run: |
          changed=$(git diff --name-only HEAD~1 | grep '^courses/' | cut -d/ -f2 | sort -u | jq -R -s -c 'split("\n")[:-1]')
          echo "courses=$changed" >> $GITHUB_OUTPUT

  build:
    needs: detect-changes
    runs-on: ubuntu-latest
    strategy:
      matrix:
        course: ${{ fromJson(needs.detect-changes.outputs.courses) }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: pnpm install
      - run: pnpm --filter ${{ matrix.course }} build-course
      - uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.course }}-scorm
          path: courses/${{ matrix.course }}/dist/*.zip
```

---

## Quality Metrics

### What to Measure

| Metric | Target | How to Measure |
|--------|--------|---------------|
| **Completion rate** | > 85% | SCORM/xAPI completion status |
| **Assessment pass rate** | > 75% first attempt | Score tracking |
| **Time to complete** | Within ±20% of estimate | Session time tracking |
| **Learner satisfaction** | > 4.0/5.0 | Post-course survey |
| **Knowledge retention** | > 70% at 30 days | Spaced review assessments |
| **Engagement drop-off** | Identify > 30% drop points | Module-level analytics |
| **Accessibility compliance** | WCAG AA | Automated + manual testing |

### Continuous Improvement

Feed learner data back into the pipeline:
- Modules with high drop-off → restructure or add engagement
- Questions with < 40% correct rate → review for clarity or difficulty
- Scenarios with uniform choices → add more nuanced options
- Low satisfaction scores → collect qualitative feedback, revise
