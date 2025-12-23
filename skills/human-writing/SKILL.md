---
name: human-writing
description: Write naturally and avoid AI-detectable patterns. Use when (1) generating any written content, (2) reviewing/editing text for AI-like patterns, (3) user asks to make writing sound more human/natural, or (4) improving text that sounds robotic or generic. Covers vocabulary, structure, tone, and formatting tells that signal AI authorship.
---

# Human Writing

Write text that reads as authentically human by avoiding patterns commonly associated with AI-generated content.

## Two Modes

**Writing Mode**: Apply guidelines when generating new content.
**Review Mode**: When asked to review text, identify AI patterns and suggest specific improvements.

## Core Principles

1. **Be specific over generic** - Use concrete details, not vague abstractions
2. **Vary sentence rhythm** - Mix short punchy sentences with longer ones naturally
3. **Take a position** - Make claims, express views, avoid hedge-everything language
4. **Use plain words** - Choose simple vocabulary over impressive-sounding alternatives
5. **Break patterns** - Avoid formulaic structures and predictable three-item lists

## Quick Reference: What to Avoid

### Vocabulary Red Flags

Certain words appear disproportionately in AI text. See [references/vocabulary.md](references/vocabulary.md) for the complete list.

**High-frequency tells**: delve, tapestry, vibrant, crucial, pivotal, enhance, foster, intricate, nuanced, multifaceted, comprehensive, underscore, landscape, realm, holistic

**Hedge words (overused)**: arguably, various, specific, generally, relatively, ultimately, particularly

**Filler intensifiers**: truly, really, very, highly, deeply

### Structural Red Flags

- **Rule of three**: Three parallel items in sequence ("X, Y, and Z" repeatedly)
- **Negative parallelism**: "Not just X, but also Y"
- **Mirror conclusions**: Restating the introduction in the conclusion
- **Topic sentence + elaboration** formula in every paragraph
- **"Challenges and future prospects"** closing pattern
- **"Despite...faces challenges"** formula: Avoid starting conclusions with "Despite its [positive trait], [subject] faces challenges..."
- **False ranges**: Meaningless "from X to Y" constructions that don't denote actual scale (e.g., "from small beginnings to global impact" when no timeline or progression exists)
- **Synonym repetition**: Using different words for the same concept repeatedly (e.g., constraints, limitations, challenges all meaning the same thing)

### Formatting Red Flags

- Excessive em dashes (—) for parenthetical asides
- Every heading in Title Case
- Overuse of boldface for emphasis
- Lists with inline headers and colons
- Curly/smart quotes when straight quotes expected

### Tone & Behavioral Red Flags

- **Importance-signaling phrases**: Avoid "it's important to note," "it's crucial to remember," "worth noting," "it's critical to consider." Show importance through specificity instead.
- **Hedging preambles**: Don't acknowledge that a subject is "unimportant" then immediately claim its importance. Commit to the claim or don't make it.
- **Paragraph structure monotony**: Avoid topic-sentence-plus-elaboration formula in every paragraph. Vary structure—start with evidence, question, or narrative instead.

## Review Mode Instructions

When asked to review text for AI patterns:

1. Read [references/ai-patterns.md](references/ai-patterns.md) for detailed detection criteria
2. Identify specific patterns present in the text
3. Quote the problematic passages
4. Provide concrete rewrites, not just suggestions
5. Prioritize changes that have the highest impact

**Output format for reviews**:
```
Pattern: [pattern name]
Found: "[quoted text]"
Issue: [brief explanation]
Rewrite: "[improved version]"
```

## Writing Mode Checklist

Before finalizing any generated text:

- [ ] No words from the high-frequency vocabulary list
- [ ] Varied sentence lengths (not all medium-length)
- [ ] No more than one three-item list per section
- [ ] Specific examples instead of abstract claims
- [ ] At least one short, punchy sentence per paragraph
- [ ] No formulaic opening or closing phrases
- [ ] No "it's important/crucial to note" phrases—let specificity speak for itself
- [ ] Paragraphs don't all follow topic-sentence + elaboration pattern
- [ ] No "Despite X, Y faces challenges" formulas in conclusions
- [ ] No false ranges ("from X to Y") where no meaningful scale exists
- [ ] No synonym repetition for same concept (use the actual term consistently)

## References

- [references/vocabulary.md](references/vocabulary.md) - Complete list of AI-associated words with alternatives
- [references/ai-patterns.md](references/ai-patterns.md) - Detailed patterns for detection and avoidance
