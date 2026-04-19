# AI Writing Patterns - Detection Reference

Detailed patterns for identifying AI-generated text, organized by category.

## Table of Contents
- [Content Patterns](#content-patterns)
- [Language Patterns](#language-patterns)
- [Structure Patterns](#structure-patterns)
- [Style Patterns](#style-patterns)
- [Markup Artifacts](#markup-artifacts)
- [Citation Issues](#citation-issues)

---

## Content Patterns

### Undue Emphasis on Symbolism/Legacy
AI text often inflates the significance of subjects with grandiose claims about impact or legacy.

**Signals**:
- "lasting legacy" or "enduring impact" without evidence
- Claims about cultural/historical significance that exceed the subject's actual importance
- Abstract impact statements without concrete examples

**Example**: "Her work represents a transformative chapter in the field's evolution" (vague, inflated)

**Fix**: State specific, verifiable achievements. "She published 12 papers on X between 2010-2015."

### Promotional Tone
Reads like marketing copy rather than neutral description.

**Signals**:
- Superlatives without substantiation (groundbreaking, revolutionary, unparalleled)
- Focus on positive aspects only
- Lack of critical analysis or limitations

**Fix**: Remove superlatives. Add balanced perspective including limitations or criticisms.

### Superficial Analysis
Surface-level treatment that avoids depth or nuance.

**Signals**:
- Generic observations that could apply to many subjects
- Avoidance of specific technical details
- No engagement with controversies or debates

**Fix**: Add specifics. Engage with actual debates in the field. Include numbers, dates, names.

### Vague Attribution
Hedging on who said or did something.

**Signals**:
- "Some scholars argue..."
- "Critics have noted..."
- "Many believe..."
- "It has been said..."

**Fix**: Name the specific person or source. If you can't, reconsider whether the claim is worth making.

### Overgeneralization
Broad claims stated as universal truths.

**Signals**:
- "Throughout history..."
- "Across cultures..."
- "People have always..."
- Universal claims without exceptions noted

**Fix**: Narrow the scope. Specify the time period, culture, or population.

### "Challenges and Future Prospects" Formula
Ending sections with a generic forward-looking statement.

**Signals**:
- Final paragraph about future challenges
- Predictions without specific basis
- Hopeful conclusions that add no information

**Fix**: End with concrete current state. If future section needed, tie to specific ongoing work.

---

## Language Patterns

### Manufactured Straw Men
Inventing a weak position nobody actually holds, then refuting it to make the real point seem stronger. The AI fabricates a foil to argue against.

**Examples**:
- "Coding isn't about typing speed anymore" (no one thought it was — used to hype agentic coding)
- "This replaces your cobbled-together spaghetti code" (assumes the reader's current setup is bad, without evidence)
- "It's not just a toy anymore" (implies people dismissed it as a toy, when they may not have)

**Why it happens**: AI defaults to contrast-based rhetoric — it's easier to frame a point as "not the old way" than to argue the new way on its own merits.

**Fix**: State what something *is*, not what it isn't. Make the positive case directly. If there's a real counterargument worth addressing, name it specifically and attribute it to actual people or positions.

### Negative Parallelism
"Not X, but Y" or "Not just X, but also Y" constructions.

**Examples**:
- "not merely a technical achievement but a cultural milestone"
- "not just innovative but transformative"

**Fix**: State the positive claim directly. "It was a cultural milestone."

### Rule of Three
Exactly three items in parallel, often with escalating intensity.

**Examples**:
- "innovative, impactful, and transformative"
- "for scholars, practitioners, and enthusiasts alike"

**Fix**: Use two items, or four+. Or just pick the most accurate single word.

### False Agency
Giving inanimate things human verbs. AI does this to avoid naming the actual actor — it sounds authoritative while being vague about who did what.

**Examples**:
- "the decision emerges" → Someone decides
- "the data tells us" → Someone reads the data and draws a conclusion
- "the market rewards" → Buyers pay for things
- "the culture shifts" → People change behavior
- "the complaint becomes a fix" → Someone fixed it
- "the conversation moves toward" → Someone steers

**Fix**: Name the human. "The team fixed it" beats "the complaint becomes a fix." If no specific person fits, use "you" to put the reader in the seat.

### Dramatic Fragmentation
Sentence fragments stacked for manufactured profundity. Reads as breathless or TED-talk-ish.

**Examples**:
- "Speed. That's it. That's the tradeoff."
- "This unlocks something. Trust."
- "X. And Y. And Z."

**Fix**: Complete sentences. The content should carry the weight, not the punctuation.

### Vague Declaratives
Sentences that announce importance or depth without naming the specific thing. They feel substantive but say nothing.

**Examples**:
- "The reasons are structural"
- "The implications are significant"
- "The stakes are high"
- "The consequences are real"
- "This is the deepest problem"

**Fix**: Name the specific reason, implication, or stake. If you can't, the sentence has no content — cut it.

### Pull-Quote Voice
Writing that sounds like it's auditioning for a blog sidebar or motivational poster. If you can imagine it in a different font on a colored background, rewrite it.

**Examples**:
- "The best teams don't optimize for speed. They optimize for learning."
- "Move fast, but move with intention."
- "The future belongs to those who ship."

**Fix**: Demote the sentence from proclamation to observation. Or just cut it — the surrounding content usually makes the point already.

### Elegant Variation
Using different words for the same thing to avoid repetition (often backfires).

**Examples**:
- "the author... the writer... the novelist..." for same person
- "the company... the firm... the organization..."

**Fix**: Repeat the same term. Readers prefer clarity over variety.

### Signposting Preambles
Announcing what you're about to say instead of saying it. Tells the reader to pay attention rather than earning attention through the content itself.

**Examples**:
- "Here's why this matters:"
- "Let me explain why this is significant."
- "Here's what you need to know:"
- "What makes this interesting is..."
- "The key takeaway here is..."
- "There are three reasons this works:"

**Why it happens**: AI treats writing like a presentation — it introduces every point with a slide title. Human writers just make the point.

**Fix**: Delete the preamble and start with the substance. "Here's why this matters: the API cuts latency by 40%" becomes "The API cuts latency by 40%." The reader can tell it matters because you wrote about it.

### False Candor Markers
Phrases that simulate a confiding or personal tone without adding substance. They imply the default is dishonesty or distance.

**Examples**:
- "Honestly, I think..."
- "To be frank..."
- "If it were me, I'd..."
- "What I would do is..."
- "I'll be real with you..."

**Why it happens**: AI uses these to manufacture intimacy — they make a generic opinion sound like personal advice from someone who's been in your shoes.

**Fix**: State the opinion directly. "Honestly, I'd go with Postgres" becomes "Go with Postgres." The reader assumes you're being honest unless you give them reason not to.

### Hedging Clusters
Multiple hedge words stacked together.

**Examples**:
- "arguably somewhat influential"
- "potentially relatively significant"
- "perhaps generally considered"

**Fix**: Commit to a claim or cut it. One hedge maximum per sentence.

### Filler Intensifiers
Words that add emphasis but no meaning.

**Words**: truly, really, very, highly, deeply, extremely, incredibly, remarkably

**Fix**: Delete them. If the sentence feels weak without them, strengthen the verb or noun instead.

---

## Structure Patterns

### Mirror Introduction/Conclusion
Conclusion restates the introduction in different words.

**Signal**: Reading conclusion gives you no information you didn't have from the intro.

**Fix**: Conclusion should add something: a synthesis, implication, or specific takeaway not in the intro.

### Topic Sentence + Elaboration Formula
Every paragraph follows: general claim → supporting detail → restatement.

**Fix**: Vary paragraph structure. Some can start with example. Some can be one sentence.

### Uniform Paragraph Length
All paragraphs approximately the same length (often 3-5 sentences).

**Fix**: Mix long and short paragraphs. Some points need one sentence. Some need eight.

### Predictable Section Order
Following a template: Background → Development → Impact → Legacy.

**Fix**: Let the subject determine structure. Not everything needs the same sections.

---

## Style Patterns

### Title Case Headings
Every Word Capitalized Like This.

**Signal**: Most style guides (except AP) use sentence case for headings.

**Fix**: Use sentence case: "Content patterns" not "Content Patterns"

### Excessive Boldface
Key terms bolded throughout body text.

**Fix**: Reserve bold for actual emphasis, used sparingly. Trust readers to identify key terms.

### Em Dash Overuse
Multiple em dashes (—) per paragraph for parenthetical insertions.

**Fix**: Use parentheses, commas, or restructure. One em dash pair per paragraph maximum.

### Inline-Header Lists
Lists where each item starts with a bolded term and colon.

**Example**:
- **First**: explanation of first
- **Second**: explanation of second

**Fix**: Use real headings if items need headers. Otherwise, just list the items.

### Curly Quotes in Code Contexts
"Smart quotes" when straight quotes expected.

**Fix**: Use straight quotes in technical content: " not " "

---

## Markup Artifacts

### Markdown in Non-Markdown Contexts
Using `**bold**` or `# headers` in plain text or HTML contexts.

### Placeholder Text
- `[citation needed]`
- `[source]`
- `[insert X here]`
- `turn0search0`
- `contentReference[oaicite:0]`

### URL Parameters
- `utm_source=chatgpt.com`
- Other tracking parameters from AI-provided links

### Knowledge Cutoff Disclaimers
- "As of my knowledge cutoff..."
- "As of [date], I cannot confirm..."

---

## Citation Issues

### Fabricated Citations
References that don't exist or have wrong details.

**Signals**:
- Author names that don't match the claimed work
- Journals that don't exist
- Page numbers or dates that don't match

**Fix**: Verify every citation. If you can't verify it, don't include it.

### Over-citation
Citing sources for common knowledge or obvious claims.

**Fix**: Only cite claims that need support—specific facts, statistics, contested points.

### Missing Critical Sources
Omitting major works or viewpoints in a field.

**Fix**: Include seminal works and major opposing viewpoints, not just supporting sources.
