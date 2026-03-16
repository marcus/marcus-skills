# Agent Review Pipeline

A structured system for reviewing software demo videos using independent reviewer agents. Each reviewer scores specific quality dimensions with explicit criteria, cites evidence from source files, and provides actionable fixes. Derived from the multi-pass review system built for the Planner demo video.

---

## Multi-Dimensional Review

Score six dimensions independently. Each dimension has a dedicated reviewer agent with domain expertise. Never have a single reviewer score everything -- specialized reviewers catch domain-specific issues that generalists miss.

### Dimension 1: Script Quality

**Reviewer focus**: Narrative effectiveness

| Sub-dimension | What to evaluate |
|---------------|-----------------|
| Hook | Does it grab in 5-8 seconds? Cold open vs. brand intro? |
| Pacing | Word count vs. allocated time per section. WPM within 130-150 target? |
| Visual-narration sync | Can the viewer absorb both narration and visuals simultaneously? |
| CTA strength | First-person language? Friction reducer? Mid-roll placement? |
| Feature density | Max 2 features per section. Are magic moments given breathing room? |
| Tone | Conversational? No filler phrases ("here's the thing," "so let's say")? |
| Overall narrative | One big idea? Satisfying arc? Social proof present? |

### Dimension 2: Visual Design

**Reviewer focus**: What the viewer sees on screen

| Sub-dimension | What to evaluate |
|---------------|-----------------|
| Consistency | Single color palette, font stack, grid system across all sections? |
| Animation quality | Ken Burns calibration (1.0-1.03), spring physics, exit animations? |
| Information hierarchy | Text readable at 1080p? Labels spatially anchored? Stacking correct? |
| Transitions | Variety mapped to narrative purpose? Durations calibrated to type? |
| Component polish | Glass-morphism, shadows, cursor details, micro-interactions? |

### Dimension 3: Pacing & Timing

**Reviewer focus**: Temporal alignment at every level

| Sub-dimension | What to evaluate |
|---------------|-----------------|
| Script-to-audio alignment | Does spoken narration match written script? Word count divergence? |
| Audio-to-visual sync | Per-section headroom (target: 1.0-1.7s). Cumulative drift check. |
| Pacing flow | Section weights proportional to content density? Act structure balanced? |
| Silent beats | Scripted silence moments present and correctly sized? Audio verified? |

### Dimension 4: Technical Quality

**Reviewer focus**: Code and architecture

| Sub-dimension | What to evaluate |
|---------------|-----------------|
| Code quality | TypeScript types, discriminated unions, proper React.FC typing? |
| Reusability | Components project-agnostic? Shared design system? Theme file? |
| Architecture | Section timing derived from data? Clean separation of concerns? |
| Pipeline | Automated steps? Narrate -> manifest -> composition -> audit -> render? |
| Performance | Render times reasonable? No unnecessary re-renders in compositions? |

### Dimension 5: Production Pipeline

**Reviewer focus**: Documentation and workflow

| Sub-dimension | What to evaluate |
|---------------|-----------------|
| Documentation | WORKFLOW.md complete? Human-agent collaboration points defined? |
| Automation | How many manual steps remain? Timing sync automated? |
| Iteration workflow | Review -> fix -> re-render loop documented and efficient? |

### Dimension 6: Thumbnail

**Reviewer focus**: Visual impact and click-worthiness

| Sub-dimension | What to evaluate |
|---------------|-----------------|
| Visual impact | Readable at 120x68px (mobile search results)? Strong focal point? |
| Readability | Text contrast and legibility at small sizes? 3-5 words max? |
| Click-worthiness | Curiosity or emotional response? Does NOT repeat video title? |
| Professionalism | Consistent with channel brand? High contrast? |

---

## Review Workflow

### Input Assembly

Each reviewer receives the specific files relevant to their dimension:

| Dimension | Input files |
|-----------|------------|
| Script Quality | `script.md`, previous `script-review.md` |
| Visual Design | Composition `.tsx`, all component files, previous visual review |
| Pacing & Timing | Composition `.tsx`, `sync-manifest.json`, `narration-manifest.json`, previous pacing review |
| Technical Quality | All `.tsx`/`.ts` files, `package.json`, project structure |
| Production Pipeline | `WORKFLOW.md`, `CLAUDE.md`, all scripts in `scripts/` |
| Thumbnail | Thumbnail image file, composition thumbnail still |

### Review Format

Each reviewer must:

1. **Score each sub-dimension** on a 1-10 scale
2. **Cite specific evidence** -- file paths and line numbers for code, exact quotes for script
3. **Provide actionable fixes** -- not "improve this" but "change line 47 from X to Y"
4. **Prioritize findings** as Critical (must fix before render), High Priority (fix before publish), or Nice-to-Have (polish)
5. **Compare to previous version** if a prior review exists -- note what improved, what regressed, what is unchanged

### Output Format

```markdown
# [Project Name] -- [Dimension] Review

**Reviewer:** [Role description]
**Date:** [Date]
**Scope:** [What was reviewed]
**Baseline:** [Previous version's score if applicable]

---

## Sub-dimension 1: [Name] -- [Score]/10

### What works well
[Specific citations]

### What needs work
1. **[Issue title].** [Description with file path and line reference.]
   **Suggested fix:** [Specific code change or rewrite]
   **Priority:** Critical / High Priority / Nice-to-Have

---

## Score Summary

| Sub-dimension | Score |
|---------------|-------|
| ... | X/10 |
| **Overall** | **X/10** |

## Priority Action Items

### Critical
1. ...

### High Priority
1. ...

### Nice-to-Have
1. ...
```

---

## Iteration Loop

```
script.md
  --> script review --> apply feedback --> updated script.md
  --> narrate-sync.ts --> sync-manifest.json
  --> update composition S constants
  --> audit-sync.ts --> fix any sync issues
  --> render draft
  --> multi-dimensional review (all 6 dimensions)
  --> apply fixes by priority (critical first)
  --> re-render
  --> iterate until all dimensions score >= 7
```

### Iteration Rules

1. **Fix critical items first.** Do not polish animation easing while narration overruns the section boundary.
2. **Maximum two revision passes per dimension.** Diminishing returns set in quickly. Ship when all dimensions are >= 7.
3. **Re-review only changed dimensions.** If you only changed the composition timing, re-review Pacing & Timing, not Script Quality.
4. **Track score progression.** Each review should include a comparison table showing score changes across versions.

### Score Progression Example

| Dimension | v1 | v2 | v3 | Target |
|-----------|-----|-----|-----|--------|
| Script Quality | 6 | 8 | 8 | >= 7 |
| Visual Design | 6 | 7.5 | -- | >= 7 |
| Pacing & Timing | 4 | 4 | 7 | >= 7 |
| Technical Quality | 7 | -- | -- | >= 7 |
| Production Pipeline | 8 | -- | -- | >= 7 |
| Thumbnail | -- | -- | -- | >= 7 |

---

## Key Insight: Self-Assessment Does Not Count

Never have the agent that built the composition also review it. The builder has context blindness -- they know what they intended, so they see what they intended rather than what is on screen. Use independent reviewer agents with explicit scoring criteria.

This applies to every dimension:
- The agent that wrote the script should not review it for tone and pacing
- The agent that built the composition should not review it for visual design
- The agent that generated narration should not review it for audio-visual sync

Each reviewer is a fresh perspective with no prior context about creative intent. They evaluate only what exists in the files.

---

## Gemini for Thumbnail Review

Thumbnails are visual artifacts that benefit from multimodal AI review. Use the Gemini vision API to review thumbnail images with structured scoring.

### Process

1. Generate thumbnail (DALL-E, Remotion still, or manual design)
2. Upload to Gemini with a structured prompt:

```
Review this YouTube thumbnail for a software demo video:

1. Readability at 120x68px (mobile search results) -- score 1-10
2. Text contrast and legibility -- score 1-10
3. Visual hierarchy -- what draws the eye first? -- score 1-10
4. Click-worthiness -- would you click this in a feed? -- score 1-10
5. Professionalism and brand consistency -- score 1-10

For each dimension:
- Give the score
- Explain what works
- Give one specific, actionable improvement

Overall score and one-sentence verdict.
```

3. Apply feedback, regenerate, re-review. Maximum two rounds.

### Why Gemini

Gemini's vision capabilities are well-suited for evaluating visual composition, text legibility at small sizes, and color contrast -- all critical for thumbnails. It can also evaluate the thumbnail in context (simulating how it would appear in a YouTube search results grid).

---

## Specialized Review Types

### Sync Audit (Automated)

The `audit-sync.ts` tool provides an automated pacing review. It is not a substitute for the Pacing & Timing reviewer, but it catches mechanical issues before the human-style review:

- Dead frames (no content on screen)
- Narration overruns (audio longer than visual section)
- Visual gaps between sections
- Section overlaps
- Sync score (1-10)

Run the audit before every human-style review to eliminate low-level issues.

### Full Quality Review

A comprehensive review across all dimensions in a single pass. Useful for initial assessment of a new project or major iteration. Less granular than individual dimension reviews but provides a holistic view of ship-readiness.

Output includes:
- Overall verdict and ship-readiness assessment
- Score per dimension with evidence
- Prioritized action items (Critical, High Priority, Nice-to-Have)
- "Ship when" criteria -- the minimum set of fixes required to publish

---

## Integration with Production Pipeline

```
1. Write script
2. Agent: Script Quality review
3. Human: Apply feedback, approve script
4. Generate narration (narrate-sync.ts)
5. Build composition
6. Automated: audit-sync.ts
7. Agent: Full Quality review (initial assessment)
8. Apply critical fixes
9. Agent: Dimension-specific reviews (Visual, Pacing)
10. Apply fixes, re-render
11. Agent: Thumbnail review (Gemini)
12. Human: Final watch and approval
13. Ship
```

The review pipeline is not optional overhead -- it is the mechanism that converts a rough draft into a publishable video. Each review pass catches a category of issues that the previous pass could not.
