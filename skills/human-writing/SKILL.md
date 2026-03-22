---
name: human-writing
description: Write naturally and avoid AI-detectable patterns. Use when (1) generating any written content, (2) reviewing/editing text for AI-like patterns, (3) user asks to make writing sound more human/natural, or (4) improving text that sounds robotic or generic. Covers vocabulary, structure, tone, and formatting tells that signal AI authorship.
---

# Human Writing

Write text that reads as authentically human by avoiding patterns commonly associated with AI-generated content.

## The Best Defense

The most effective way to eliminate AI writing tics is a strong voice directive — a system prompt or persona that says "be direct, have opinions, don't perform helpfulness." This shifts the model's posture and most tics disappear on their own, the same way telling someone "be confident" eliminates a dozen nervous habits at once. The pattern lists below are the safety net: useful for review mode, for catching what slips through, and for teaching the specific tells. But if you can set the voice, start there.

Two principles that do the most work:
1. **Don't be performative** — be genuinely helpful instead of signaling helpfulness. Straw men, preambles, and importance phrases are all performances.
2. **Be confident** — state things directly unless there's a real reason to hedge. False candor ("honestly"), unnecessary qualifiers, and throat-clearing vanish when the default posture is confidence.

## The Defensive Posture Problem

AI writing defaults to a defensive posture. It assumes the reader is adversarial — someone in a Hacker News comment thread looking to poke holes. This produces writing that:

- **Pre-emptively hedges** against imagined objections instead of making its point
- **Weakly strawmans the other side** instead of engaging with valid concerns honestly
- **Reads like a retrospective or post-mortem** — analytical, detached, explaining itself
- **Teaches when it should share** — defaults to instructional tone ("here's how I did it") when the actual energy is closer to "look at this wild thing that happened"

The fix isn't to ignore valid counterarguments. It's to engage with them honestly when they matter and otherwise just say the thing with conviction. Writing from awe, curiosity, or excitement reads completely differently than writing from a defensive crouch. If the writer is genuinely amazed by what happened, the reader should feel that — not a carefully hedged technical summary of it.

Ask: is this piece trying to *defend* a position, or *share* an experience? Most personal writing should be the latter. Save the defensive posture for actual debates.

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
- **Manufactured straw men**: Inventing a weak position nobody holds, then refuting it to make the real point seem stronger (e.g., "Coding isn't about typing speed anymore" — nobody thought it was; or "This replaces your cobbled-together spaghetti code" — characterizing a situation that doesn't exist)
- **False agency**: Giving inanimate things human verbs — "the decision emerges," "the data tells us," "the market rewards." AI does this to avoid naming who actually did something. Name the person.
- **Dramatic fragmentation**: Sentence fragments stacked for manufactured profundity — "Speed. That's it. That's the tradeoff." or "This unlocks something. Trust." Trust your content over your presentation.
- **Vague declaratives**: Sentences that announce importance without naming the specific thing — "The reasons are structural," "The implications are significant," "The stakes are high." If you can't name the specific implication, cut the sentence.
- **Pull-quote test**: If a sentence sounds like it belongs on a motivational poster or blog pull-quote, rewrite it. Manufactured profundity is a tell.
- **Synonym repetition**: Using different words for the same concept repeatedly (e.g., constraints, limitations, challenges all meaning the same thing)
- **Staccato stat dumps**: Listing numbers as sentence fragments for dramatic effect — "93 files. 51,000 lines. 244 commits." This is a distinctly AI cadence. Weave numbers into complete sentences instead.
- **Verb-dropped fragments as emphasis**: "Each one small enough for a single session." Dropping the verb ("was") to sound punchy. AI does this constantly. Write complete sentences.
- **"One rule:" / "One word:" intros**: Starting a sentence with a dramatic colon-reveal. "One rule: don't touch it." This is presentation cadence, not writing cadence.
- **"actually works" / "actually good"**: Using "actually" to express surprise at quality. Implies low expectations and reads as defensive. Just describe what it does.
- **Clickbait subtitle formulas**: "Here's the System That Made It Work" / "Here's What I Learned" / "And Why It Matters." These are YouTube thumbnail cadences. State the topic directly.
- **Unintroduced fragment lists**: Jumping from a sentence directly into a list of sentence fragments without a lead-in. "I broke it into 90 tasks. Layer panel. Image support. Auto-layout." Introduce the list naturally: "Things like layer panel navigation, image support, and the auto-layout engine."
- **"Fresh eyes every time" / "Different eyes every time"**: AI loves this phrase to describe independent review. It's a cliché that signals generated text. Describe what the review catches instead.
- **"Not X but Y" straw man pairs in technical writing**: "Not 'did the tests pass' but an actual code review." This manufactures a false binary. Just describe what the review does.
- **Generic section headers**: "What this means," "By the numbers," "What went wrong," "What exists" — these are fill-in-the-blank headers that could go on any post. Use headers that tell the reader something specific to this piece.
- **"It's not X. But it's not Y either"**: The hedged double-negative sandwich. "It's not Figma. But this isn't a toy either." Pick a lane and describe what it actually is instead of triangulating between two things it isn't.
- **Inaccurate uniqueness claims**: Claiming a benefit is unique to your approach when it's common to the whole category. Check whether what you're describing is actually different before positioning it as a differentiator.

### Formatting Red Flags

- Excessive em dashes (—) for parenthetical asides
- Every heading in Title Case
- Overuse of boldface for emphasis
- Lists with inline headers and colons
- Curly/smart quotes when straight quotes expected

### Tone & Behavioral Red Flags

- **Importance-signaling phrases**: Avoid "it's important to note," "it's crucial to remember," "worth noting," "it's critical to consider." Show importance through specificity instead.
- **Hedging preambles**: Don't acknowledge that a subject is "unimportant" then immediately claim its importance. Commit to the claim or don't make it.
- **Signposting preambles**: Avoid announcing what you're about to say — just say it. Phrases like "Here's why this matters," "Let me explain why," "Here's what you need to know," "What makes this interesting is" are throat-clearing. Cut them and start with the actual point.
- **False candor markers**: Phrases like "honestly," "to be frank," "if it were me," "what I would do is" simulate a confiding tone without adding substance. They imply the rest of the time you're not being honest. Just state the opinion directly.
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
- [ ] No signposting preambles ("Here's why this matters," "Let me explain")
- [ ] No false candor markers ("honestly," "if it were me")
- [ ] Paragraphs don't all follow topic-sentence + elaboration pattern
- [ ] No "Despite X, Y faces challenges" formulas in conclusions
- [ ] No false ranges ("from X to Y") where no meaningful scale exists
- [ ] No manufactured straw men (inventing weak positions to refute)
- [ ] No false agency (inanimate things doing human actions)
- [ ] No vague declaratives ("The implications are significant" — name the thing)
- [ ] Passes the pull-quote test (nothing sounds like a motivational poster)
- [ ] No synonym repetition for same concept (use the actual term consistently)
- [ ] No staccato stat dumps (weave numbers into sentences, don't list as fragments)
- [ ] No verb-dropped fragments used for emphasis (write complete sentences)
- [ ] No "One rule:" / "One word:" dramatic colon-reveals
- [ ] No "actually works" / "actually good" (implies surprise at quality)
- [ ] No clickbait subtitle formulas ("Here's What I Learned," "And Why It Matters")

## References

- [references/vocabulary.md](references/vocabulary.md) - Complete list of AI-associated words with alternatives
- [references/ai-patterns.md](references/ai-patterns.md) - Detailed patterns for detection and avoidance
