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

### Elegant Variation
Using different words for the same thing to avoid repetition (often backfires).

**Examples**:
- "the author... the writer... the novelist..." for same person
- "the company... the firm... the organization..."

**Fix**: Repeat the same term. Readers prefer clarity over variety.

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
