---
name: human-writing
description: Write naturally and avoid AI-detectable patterns. Use when (1) generating any written content, (2) reviewing/editing text for AI-like patterns, (3) user asks to make writing sound more human/natural, or (4) improving text that sounds robotic or generic. Covers vocabulary, structure, tone, and formatting tells that signal AI authorship.
---

# Human Writing

Write text that reads as authentically human -- not by sanitizing it into blandness, but by writing with voice, specificity, and personality. Avoiding AI tells is the floor; being engaging is the goal.

## Write With Voice First, Sanitize Second

The biggest risk with this skill is overcorrection: stripping out every AI pattern and leaving behind something flat and lifeless. Safe writing that avoids all tells but says nothing interesting is worse than writing with a few AI-isms that actually engages the reader.

The priority order:
1. **Say something worth reading** -- have a point of view, include details only you'd know, make the reader think or feel something
2. **Say it in your voice** -- not a committee voice, not a "professional" voice, your voice
3. **Then clean up AI tells** -- the avoidance checklist is a final pass, not the writing strategy

A piece that's engaging with one or two AI tells is better than a piece that's sterile with zero.

### What "voice" means in practice

Voice isn't about being quirky or casual. It's about having a recognizable perspective. Concrete things that create voice:

- **Name things**: "Richard Hipp's benchmarks show 10-35x" beats "performance is excellent." Real names, real numbers, real products.
- **Have opinions**: "WAL mode is fine for this -- you're not running 10,000 concurrent inserts" is a position. "SQLite handles writes adequately" is wallpaper.
- **Show your reasoning**: "That makes sense -- there's no serialization, no network round trip" lets the reader follow your thinking. Bare claims ("it's fast") don't.
- **Acknowledge tradeoffs honestly**: "There are limits. If your sync layer needs row-level conflict resolution, you'll build that yourself." This builds trust. Pure advocacy doesn't.
- **Vary your energy**: Some paragraphs should crackle. Some should be matter-of-fact. A blog post that maintains one even tone throughout reads like it was generated.

### Match voice to format

Not every piece of writing wants the same amount of personality. Read the room:

- **Blog posts, essays, opinion pieces**: Go heavy on voice. Have opinions, name names, show reasoning, vary energy. Flowing prose often works better than heading-per-point.
- **Product emails, announcements, docs**: Clarity and scannability come first. Structure (bold headers, short sections, bullet points) is genuinely useful here -- don't strip it just because it "looks AI." Voice shows up in word choice and directness, not in forced casualness or anecdotes.
- **Technical writing, READMEs**: Precision matters most. Voice is subtle -- it's in the examples you choose, the tradeoffs you mention, the gotchas you warn about.

The skill's avoidance patterns (no inline-header lists, no bold formatting, minimal headings) are guidelines for prose, not rules for every format. A product announcement with clear `**What's new:**` sections is better than one that abandons structure to sound casual.

### Don't fabricate to sound human

When the skill says "name things" and "share practical knowledge," it means things you (or the persona you're writing as) actually know. Don't invent war stories, fake anecdotes, or made-up incidents to manufacture voice. A fabricated "we learned this the hard way when X crashed our staging server" is worse than no anecdote at all -- readers can smell fiction in technical writing. If you don't have a real story, use concrete technical details instead.

### Two principles that do the most work

1. **Don't be performative** -- be genuinely helpful instead of signaling helpfulness. Straw men, preambles, and importance phrases are all performances.
2. **Be confident** -- state things directly unless there's a real reason to hedge. False candor ("honestly"), unnecessary qualifiers, and throat-clearing vanish when the default posture is confidence.

## Two Modes

**Writing Mode**: Write with voice and personality first, then verify no AI tells slipped through.
**Review Mode**: When asked to review text, identify AI patterns and suggest specific improvements.

## Writing Mode

### Step 1: Write with substance and personality

Before thinking about what to avoid, focus on what to include:

- **Concrete details**: numbers, names, dates, measurements, code snippets, product names. "We measured P95 time-to-first-token at 87ms during our beta period" beats "response times are fast."
- **Practical knowledge**: gotchas, tradeoffs, things the reader might not expect. "Token-level callbacks can fire thousands of times per response, so keep your handler lightweight" -- this is the stuff people actually want to read.
- **Structure that serves the content**: don't default to a heading-per-point outline if flowing prose works better. A blog post with 6 `##` headings for 400 words feels like a PowerPoint deck, not writing.
- **Varied energy**: mix informational paragraphs with opinionated ones. Throw in a one-sentence paragraph. Let some paragraphs be long and detailed. Rhythm matters.

### Step 2: Review for AI tells

After drafting, scan for the patterns below. But don't strip things that are working just because they appear on a list -- the goal is writing that sounds human and reads well, not writing that passes a filter.

#### Vocabulary red flags

Certain words appear disproportionately in AI text. See [references/vocabulary.md](references/vocabulary.md) for the complete list.

**High-frequency tells** (find alternatives): delve, tapestry, vibrant, crucial, pivotal, enhance, foster, intricate, nuanced, multifaceted, comprehensive, underscore, landscape, realm, holistic

**Hedge words** (reduce significantly): arguably, various, specific, generally, relatively, ultimately, particularly

**Filler intensifiers** (delete): truly, really, very, highly, deeply

#### Structural red flags

- **Rule of three**: Three parallel items in sequence ("X, Y, and Z" repeatedly)
- **Negative parallelism**: "Not just X, but also Y"
- **Mirror conclusions**: Restating the introduction in the conclusion
- **Topic sentence + elaboration** formula in every paragraph
- **"Challenges and future prospects"** closing pattern
- **"Despite...faces challenges"** formula
- **False ranges**: Meaningless "from X to Y" constructions that don't denote actual scale
- **Manufactured straw men**: Inventing a weak position nobody holds, then refuting it
- **Synonym repetition**: Using different words for the same concept repeatedly

#### Formatting red flags

- Excessive em dashes (--) for parenthetical asides
- Every heading in Title Case when sentence case fits better
- Overuse of boldface for emphasis
- Lists with **inline headers** and colons (the pattern you're reading right now -- use sparingly)
- Too many `##` headings for short pieces. If the piece is under 500 words, consider whether headings help or just break up the flow.

#### Tone red flags

- **Importance-signaling phrases**: "it's important to note," "it's crucial to remember," "worth noting." Show importance through specificity instead.
- **Signposting preambles**: "Here's why this matters," "Let me explain why." Also watch for softer signposts like "X is where things get interesting/practical" -- these announce a transition instead of just making it. Just say the thing.
- **False candor markers**: "honestly," "to be frank," "if it were me." Just state the opinion.
- **Paragraph structure monotony**: Not every paragraph should start with a topic sentence. Start with evidence, a question, a detail, or a narrative beat.

### Step 3: Quick checklist (final pass, not primary strategy)

- [ ] The piece has a point of view, not just information
- [ ] At least two concrete details (names, numbers, specifics)
- [ ] Sentence lengths vary noticeably
- [ ] No high-frequency AI vocabulary
- [ ] No importance-signaling or signposting phrases
- [ ] Paragraphs use varied structures
- [ ] The conclusion adds something the introduction didn't say
- [ ] The piece would still be interesting if another human wrote it

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

## References

- [references/vocabulary.md](references/vocabulary.md) - Complete list of AI-associated words with alternatives
- [references/ai-patterns.md](references/ai-patterns.md) - Detailed patterns for detection and avoidance
