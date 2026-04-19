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

## The Defensive Posture Problem

AI writing defaults to a defensive posture. It assumes the reader is adversarial — someone in a Hacker News comment thread looking to poke holes. This produces writing that:

- **Pre-emptively hedges** against imagined objections instead of making its point
- **Weakly strawmans the other side** instead of engaging with valid concerns honestly
- **Reads like a retrospective or post-mortem** — analytical, detached, explaining itself
- **Teaches when it should share** — defaults to instructional tone ("here's how I did it") when the actual energy is closer to "look at this wild thing that happened"

The fix isn't to ignore valid counterarguments. It's to engage with them honestly when they matter and otherwise just say the thing with conviction. Writing from awe, curiosity, or excitement reads completely differently than writing from a defensive crouch. If the writer is genuinely amazed by what happened, the reader should feel that — not a carefully hedged technical summary of it.

Ask: is this piece trying to *defend* a position, or *share* an experience? Most personal writing should be the latter. Save the defensive posture for actual debates.

The tone to aim for isn't hype or superlatives. It's the energy of sharing something with people you like. "I did this thing, and if I can do it anyone can, and isn't it wild that this is where we are right now?" It's generous, not defensive. It invites people in instead of pre-empting their criticism. The underlying message is "things are changing fast and it's exciting" — not "here is my airtight case for why my approach is valid."

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
- **"Despite...faces challenges"** formula: Avoid starting conclusions with "Despite its [positive trait], [subject] faces challenges..."
- **False ranges**: Meaningless "from X to Y" constructions that don't denote actual scale (e.g., "from small beginnings to global impact" when no timeline or progression exists)
- **Manufactured straw men**: Inventing a weak position nobody holds, then refuting it to make the real point seem stronger (e.g., "Coding isn't about typing speed anymore" — nobody thought it was)
- **False agency**: Giving inanimate things human verbs — "the decision emerges," "the data tells us," "the market rewards." AI does this to avoid naming who actually did something. Name the person.
- **Dramatic fragmentation**: Sentence fragments stacked for manufactured profundity — "Speed. That's it. That's the tradeoff." Trust your content over your presentation.
- **Vague declaratives**: Sentences that announce importance without naming the specific thing — "The reasons are structural," "The implications are significant." If you can't name the specific implication, cut the sentence.
- **Pull-quote test**: If a sentence sounds like it belongs on a motivational poster or blog pull-quote, rewrite it. Manufactured profundity is a tell.
- **Synonym repetition**: Using different words for the same concept repeatedly (e.g., constraints, limitations, challenges all meaning the same thing)
- **Staccato stat dumps**: Listing numbers as sentence fragments for dramatic effect — "93 files. 51,000 lines. 244 commits." Weave numbers into complete sentences instead.
- **Verb-dropped fragments as emphasis**: "Each one small enough for a single session." Dropping the verb to sound punchy. Write complete sentences.
- **"One rule:" / "One word:" intros**: Dramatic colon-reveals. "One rule: don't touch it." Presentation cadence, not writing cadence.
- **"actually works" / "actually good"**: Using "actually" to express surprise at quality. Implies low expectations and reads as defensive.
- **Clickbait subtitle formulas**: "Here's the System That Made It Work" / "Here's What I Learned" / "And Why It Matters." State the topic directly.
- **Unintroduced fragment lists**: Jumping from a sentence directly into a list of sentence fragments without a lead-in. Introduce the list naturally instead.
- **"Fresh eyes every time" / "Different eyes every time"**: AI cliché for describing independent review. Describe what the review catches instead.
- **"Not X but Y" straw man pairs**: "Not 'did the tests pass' but an actual code review." Manufactures a false binary. Describe what it actually does.
- **Generic section headers**: "What this means," "By the numbers," "What went wrong" — fill-in-the-blank headers that could go on any post. Use headers specific to this piece.
- **"It's not X. But it's not Y either"**: Hedged double-negative sandwich. Pick a lane and describe what it actually is.
- **Inaccurate uniqueness claims**: Claiming a benefit is unique when it's common to the whole category. Check whether it's actually different before positioning it as a differentiator.

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
- [references/marcus-voice.md](references/marcus-voice.md) - Marcus's specific writing voice profile. Read this when asked to write "in my voice" or "like I write." Derived from ~700K words of his actual writing.
