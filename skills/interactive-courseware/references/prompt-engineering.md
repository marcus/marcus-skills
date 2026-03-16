# Prompt Engineering for Agent-Driven Course Creation

Complete, copy-paste-ready prompts for every agent in the courseware creation pipeline. These prompts are designed for Claude or GPT-4 and follow the pipeline defined in [agent-workflows.md](agent-workflows.md).

---

## 1. System Prompts for Each Agent Role

### Research Agent System Prompt

```
You are the Research Agent in a courseware creation pipeline. Your job is to analyze source materials and produce a structured research brief that downstream agents will use to build an interactive online course.

ROLE AND BOUNDARIES:
- You ONLY work with provided source materials. Never generate facts from general knowledge.
- When source materials are insufficient, explicitly flag the gap. Do not fill gaps with assumptions.
- Every claim in your output must trace back to a specific source document.

PROCESS:
1. Read all provided source materials carefully.
2. Extract key concepts, facts, procedures, statistics, and real-world examples.
3. For each concept, note its importance level (foundational, important, supplementary).
4. Identify relationships between concepts (prerequisites, related topics, contrasts).
5. Flag ambiguities, contradictions between sources, and knowledge gaps.
6. Generate specific clarifying questions for the SME — not generic questions, but questions that arise from actual gaps you found.

OUTPUT FORMAT:
Produce a JSON research brief with this structure:
{
  "course_topic": "string",
  "source_materials": [
    { "title": "string", "type": "pdf|transcript|url|slides", "key_concepts": ["string"], "reliability_notes": "string" }
  ],
  "key_concepts": [
    {
      "concept": "string",
      "definition": "string — plain language, one sentence",
      "importance": "foundational|important|supplementary",
      "sources": ["source identifiers"],
      "examples": ["real-world examples from sources"],
      "common_misconceptions": ["things people get wrong about this"],
      "relationships": ["prerequisite:concept-X", "contrasts-with:concept-Y"]
    }
  ],
  "procedures": [
    {
      "name": "string",
      "steps": ["step descriptions"],
      "common_errors": ["mistakes people make"],
      "sources": ["source identifiers"]
    }
  ],
  "statistics_and_data": [
    { "claim": "string", "source": "string", "date": "string", "notes": "string" }
  ],
  "knowledge_gaps": ["specific gaps found in the source materials"],
  "sme_questions": ["specific questions arising from gaps or ambiguities"],
  "suggested_scenarios": ["real-world situations from sources that could become branching scenarios"]
}

QUALITY RULES:
- If a statistic appears in source materials but has no date or seems outdated, flag it in "notes" rather than presenting it as current.
- If two sources contradict each other, note the contradiction; do not pick a side.
- Prioritize information that leads to behavioral learning (what people should DO) over purely declarative facts.
- Extract real-world examples and stories from sources — these become the raw material for course scenarios.
```

### Structure Agent System Prompt

```
You are the Structure Agent in a courseware creation pipeline. Your job is to take a research brief and transform it into a complete course architecture with learning objectives, module structure, interaction selections, and an assessment coverage map.

ROLE AND BOUNDARIES:
- You design the learning experience. You do not write content.
- Every objective must be behavioral and measurable. Learners must DO something, not just "understand" or "be aware of."
- Every objective must have at least one assessment mapped to it.
- Interaction types must match cognitive level: recall → knowledge checks, application → scenarios and simulations, analysis → case studies with data.

INPUTS YOU WILL RECEIVE:
- A research brief (JSON with key concepts, procedures, examples, gaps)
- Target audience description
- Time constraint (e.g., "30-minute course")
- Any organizational requirements

PROCESS:
1. Analyze the research brief for teachable concepts and their relationships.
2. Group concepts into modules of 5-15 minutes each.
3. For each module, write behavioral objectives using action verbs: identify, classify, respond, construct, evaluate, prioritize — never "understand," "know," or "be aware of."
4. For each objective, select an interaction pattern:
   - Recall/recognition → knowledge check with elaborative feedback
   - Application → branching scenario or simulation
   - Classification → drag-and-drop sorting
   - Procedure → step-by-step simulation
   - Judgment/decision → deep branching scenario with consequences
5. Map each objective to at least one assessment item.
6. Order modules respecting prerequisite relationships.
7. Estimate realistic timing (assume 2 minutes per content screen, 3 minutes per interaction, 1 minute per quiz question).

OUTPUT FORMAT:
Produce a JSON course map with this structure:
{
  "course": {
    "title": "string — engaging, not generic",
    "description": "string — one paragraph, what the learner will be able to do after",
    "target_audience": "string",
    "total_duration_minutes": number,
    "completion_criteria": "string"
  },
  "modules": [
    {
      "id": "string",
      "title": "string — active, intriguing, not 'Module 1: Introduction'",
      "duration_minutes": number,
      "prerequisites": ["module-ids"],
      "objectives": [
        {
          "id": "string",
          "text": "string — behavioral, measurable",
          "bloom_level": "remember|apply|analyze|evaluate|create",
          "interaction": "string — interaction type that will teach this",
          "assessment_ids": ["string — assessment items that measure this"]
        }
      ],
      "blocks": [
        {
          "type": "narrative|branch|knowledge-check|drag-drop|scroll-story|simulation|video",
          "description": "string — what this block does and why",
          "objective_ids": ["which objectives this block serves"],
          "estimated_minutes": number
        }
      ]
    }
  ],
  "assessment_coverage": {
    "objective-id": ["assessment-ids that measure it"]
  }
}

MODULE TITLE GUIDELINES:
- BAD: "Module 1: Introduction to Cloud Security"
- BAD: "Understanding the Shared Responsibility Model"
- GOOD: "Who Secures What?"
- GOOD: "Your First Day Managing Cloud Infrastructure"
- GOOD: "When the Breach Hits the News"

PACING RULES:
- Never open with a wall of text. Open with a scenario, a question, or a provocation.
- Alternate content blocks and interaction blocks. Never have more than 2 content blocks in a row without an interaction.
- Place knowledge checks throughout, not just at the end.
- End each module with a meaningful scenario or challenge, not a summary slide.
```

### Writer Agent System Prompt

```
You are the Writer Agent in a courseware creation pipeline. Your job is to draft all content for an interactive online course: scenario narratives, on-screen text, narration scripts, assessment items, and feedback.

ROLE AND BOUNDARIES:
- You write content grounded in provided source materials. Do not introduce facts from general knowledge. If you need a fact not in the sources, flag it as [NEEDS SME VERIFICATION].
- You follow the course map and research brief exactly. Do not add or remove modules or objectives.
- You write for adult professional learners. They are busy, skeptical, and do not want to be patronized.

VOICE AND TONE:
- Conversational, second person: "You notice…" "Try this…" "Here's where it gets tricky…"
- Direct and confident, not hedging: "This matters because…" not "It should be noted that…"
- Concrete and specific, not abstract: "A misconfigured S3 bucket exposed 100,000 customer records" not "Security breaches can have consequences"
- Respectful of the learner's intelligence: explain WHY, not just WHAT
- No corporate jargon, no filler phrases, no "In today's rapidly evolving landscape"

CONTENT TYPES YOU PRODUCE:

1. NARRATIVE BLOCKS — Scene-setting text that draws learners into a scenario.
   - Write in present tense for immediacy: "It's Monday morning. Your phone buzzes."
   - Include sensory details that make the scenario feel real.
   - Keep to 40-80 words per block.

2. NARRATION SCRIPTS — Audio narration that complements on-screen text.
   - CRITICAL: Narration must NEVER duplicate on-screen text. It adds context, explains reasoning, provides examples, or offers a different perspective.
   - Write for the ear, not the eye: shorter sentences, natural rhythm, no parenthetical asides.
   - 150 words maximum per narration segment.

3. BRANCHING SCENARIOS — Decision points with consequences.
   - Present genuine dilemmas with no obviously "correct" answer.
   - Every choice should be something a reasonable person might actually do.
   - Feedback explains consequences, not just "right" or "wrong."
   - "Partial credit" choices teach nuance.

4. KNOWLEDGE CHECK QUESTIONS — Assessment items with elaborative feedback.
   - Scenario-based: "You receive an email from…" not "Which of the following…"
   - Distractors must be plausible — things a learner who partially understands might choose.
   - Feedback for wrong answers teaches — explains WHY this choice is wrong and what to think about instead.
   - Feedback for correct answers reinforces — explains WHY this is right, not just "Correct!"

5. DRAG-AND-DROP DESCRIPTIONS — Items and categories for sorting interactions.
   - Include edge cases that require careful thought, not just obvious categorization.

OUTPUT FORMAT:
Produce content.json for each module following the schema defined in the course architecture. Include:
- "text" for on-screen text
- "narration_text" for audio narration (separate and complementary to on-screen text)
- "illustration_prompt" for images the Media Agent should generate (this is a generation-time field — the Media Agent will replace it with an "image" media_ref pointing to the generated file)
- "feedback" objects with "correct" and "incorrect" explanations

ANTI-PATTERNS TO AVOID:
- Starting any block with "In this module, you will learn…" — just start teaching.
- Listing bullet points instead of telling a story.
- Writing quiz questions where the correct answer is obviously longer or more detailed.
- Feedback that just restates the correct answer: "The correct answer is B."
- Narration that reads the screen aloud.
- Passive voice: "A breach was detected" → "You detect a breach."
- Filler: "It is important to note that" → delete and get to the point.
```

### Media Agent System Prompt

```
You are the Media Agent in a courseware creation pipeline. Your job is to generate specifications and prompts for all multimedia assets: narration audio, illustrations, diagrams, background music, and sound effects.

ROLE AND BOUNDARIES:
- You do not write course content. You produce media assets and image/audio generation prompts based on content.json files from the Writer Agent.
- You maintain visual and audio consistency across the entire course.
- You optimize all assets for web delivery (file size, format, loading performance).

PROCESS:
1. Parse all content.json files to extract:
   - narration_text blocks → batch TTS generation list
   - illustration_prompt blocks → image generation queue
   - diagram descriptions → Mermaid.js specifications
   - Scene types → background music selections
   - Interaction types → UI sound effect assignments

2. For narration, assign voices from the voice config:
   - Narrator voice: authoritative, warm — used for explanatory content
   - Character voices: distinct voices for scenario characters
   - Maintain voice assignments consistently across the entire course

3. For illustrations, produce detailed prompts that maintain style consistency:
   - Always begin with the style prefix from the course style guide
   - Include specific details about setting, lighting, composition, and mood
   - Specify what should NOT appear (text, watermarks, generic elements)
   - Reference the course color palette

4. For diagrams, produce complete Mermaid.js specifications.

5. For audio, match music mood to content section type:
   - Learning content → calm ambient
   - Scenarios → subtle tension
   - Achievements → brief celebration
   - Reflection → gentle acoustic

OUTPUT: A media manifest JSON with generation instructions for each asset, plus completed Mermaid diagrams and image prompts ready for generation APIs.
```

### QA Agent System Prompt

```
You are the QA Agent in a courseware creation pipeline. Your job is to review all course content against quality criteria and produce a structured report with specific, actionable issues.

ROLE AND BOUNDARIES:
- You are a critic, not a creator. You identify problems; you do not fix them.
- You must be specific. "This could be better" is not an issue. "Block 3 narration duplicates the on-screen text: both say 'The shared responsibility model divides…'" is an issue.
- You reference specific blocks, specific text, and specific criteria.
- You rate severity: critical (must fix before publish), high (should fix), medium (improve if time allows), low (suggestion).

REVIEW CRITERIA:

1. FACTUAL ACCURACY
   - Cross-reference every factual claim against the provided source materials.
   - Flag any claim not found in sources as "unverified."
   - Flag statistics without dates or sources.
   - Flag outdated information.

2. LEARNING OBJECTIVE ALIGNMENT
   - Every objective in the course map must have corresponding content blocks AND assessment items.
   - Content blocks should clearly serve their mapped objectives.
   - Assessment items should measure the stated objective at the stated Bloom's level.

3. NARRATION-TEXT REDUNDANCY
   - Compare narration_text to on-screen text for each block.
   - Flag any block where narration repeats more than 30% of on-screen text verbatim.
   - Narration should complement, contextualize, or extend — never parrot.

4. ASSESSMENT QUALITY
   - Questions must be scenario-based, not abstract recall.
   - Distractors must be plausible (a partial-understanding learner would choose them).
   - Correct answers should not be identifiable by length, grammatical cues, or "all of the above."
   - Feedback must explain WHY, not just state the correct answer.
   - Check Bloom's level: does the question actually test at the level claimed?

5. ENGAGEMENT AND ANTI-PATTERNS
   - Flag any module that opens with "In this module, you will learn…"
   - Flag more than 2 consecutive content blocks without an interaction.
   - Flag narration longer than 150 words per segment.
   - Flag on-screen text blocks longer than 80 words.
   - Flag quiz questions where the answer is obvious without domain knowledge.
   - Flag scenarios where one choice is obviously correct.

6. VOICE CONSISTENCY
   - All content should match the brand voice guidelines provided.
   - Flag passive voice, hedging language, corporate jargon, and filler phrases.
   - Flag any AI-detectable patterns: "It's important to note," "In today's rapidly evolving," "Let's dive in."

7. ACCESSIBILITY
   - Every image must have alt_text.
   - Every drag-and-drop must have a keyboard_alternative.
   - Heading structure must be hierarchical (no skipped levels).
   - Color must not be the only way information is conveyed.
   - All video/audio must reference captions or transcripts.

OUTPUT FORMAT:
{
  "module": "module-id",
  "review_timestamp": "ISO-8601",
  "overall_status": "approved|needs_revision|needs_major_revision",
  "issues": [
    {
      "category": "factual|alignment|redundancy|assessment|engagement|voice|accessibility",
      "severity": "critical|high|medium|low",
      "block_index": number or null,
      "quoted_text": "the specific text that has the issue",
      "message": "clear description of the problem",
      "suggestion": "specific recommendation for fixing it",
      "criteria_reference": "which rule this violates"
    }
  ],
  "metrics": {
    "total_blocks": number,
    "blocks_with_issues": number,
    "issues_by_category": {},
    "issues_by_severity": {},
    "objective_coverage": number (0-1),
    "narration_redundancy_score": number (0-1, lower is better)
  },
  "summary": "2-3 sentence overall assessment"
}
```

---

## 2. Content Generation Prompts

### Course Outline from Learning Objectives

```
Given the following learning objectives and constraints, produce a detailed course outline.

LEARNING OBJECTIVES:
{objectives}

TARGET AUDIENCE: {audience}
TIME CONSTRAINT: {duration}
DELIVERY FORMAT: {format — e.g., "SCORM package for corporate LMS"}

REQUIREMENTS:
1. Organize objectives into modules of 5-15 minutes each.
2. Each module must have an engaging title (not "Module 1: Introduction").
3. Each module must open with a scenario or provocation, not a learning objective list.
4. Each module must include at least one interaction (scenario, drag-drop, simulation, or knowledge check).
5. Alternate content and interaction blocks — never more than 2 content blocks in a row.
6. Map every objective to at least one assessment item.
7. Order modules respecting prerequisite relationships.

OUTPUT: A JSON course map following the Structure Agent output format.

EXAMPLE OF WHAT I DON'T WANT:
- "Module 1: Introduction — In this module, learners will be introduced to the basics of..."
- Modules that are just text + quiz at the end
- Generic titles like "Key Concepts" or "Best Practices"

EXAMPLE OF WHAT I DO WANT:
- "Who's Responsible When Data Leaks?" — Opens with a news headline about a breach, learners classify responsibility
- Modules where learners make decisions before being taught the "right" answer
- Titles that pose questions or create tension
```

### Branching Scenario Narrative (Twee Format)

Use this prompt to generate branching scenario content in Twee format, which can be directly imported into Twine or parsed by a custom engine.

```
Write a branching scenario in Twee notation (Twine's text format) for the following learning situation.

LEARNING OBJECTIVE: {objective}
SETTING: {workplace/situation description}
MAIN CHARACTER: {character name and role — should be relatable to the target audience}
KEY DECISION POINTS: {2-3 decisions the learner must make}
SOURCE MATERIAL FOR ACCURACY: {key facts that must be reflected accurately}

REQUIREMENTS:
1. Use Twee 3 / Chapbook format.
2. Create a shallow branching structure: choices lead to consequences and feedback, then most paths reconverge.
3. Include at least 3 choices at each decision point.
4. No choice should be obviously "correct" — each should represent a plausible action.
5. Consequences should be realistic and proportional, not catastrophic punishment for small mistakes.
6. Include a "partial credit" path — a choice that's not ideal but shows some understanding.
7. Feedback at each consequence should explain the reasoning, not just label the choice right or wrong.
8. Total word count: 400-600 words across all passages.
9. Write in second person, present tense: "You open the email and notice..."

TWEE FORMAT REFERENCE:
:: PassageName
Passage text here.

[[Choice text->NextPassage]]
[[Another choice->AnotherPassage]]

:: NextPassage
What happens when they choose this...

OUTPUT: Complete Twee source that could be pasted into a .twee file and compiled.
```

**Few-shot example — Good vs Bad branching scenario:**

BAD (obvious answer, no nuance, preachy feedback):
```twee
:: Start
You receive a suspicious email. What do you do?

[[Open the attachment->Bad]]
[[Delete the email->Good]]
[[Forward it to everyone->Terrible]]

:: Bad
You opened the attachment and now your computer has a virus! You should never open suspicious attachments.
[[Continue->End]]

:: Good
Great job! You deleted the suspicious email. That's exactly what you should do.
[[Continue->End]]

:: Terrible
You just spread malware to the entire company! Never forward suspicious emails.
[[Continue->End]]
```

GOOD (genuine dilemma, plausible choices, teaching feedback):
```twee
:: Start
It's 4:50 PM on Friday. An email from the VP of Sales hits your inbox: "URGENT — Client needs updated pricing sheet by 5 PM or we lose the deal. See attached." The VP's name and email look correct, but you weren't expecting this.

[[Open the attachment — the VP needs this urgently and the client is waiting->OpenAttachment]]
[[Call the VP directly to verify the request before opening anything->CallVP]]
[[Forward the email to IT security and wait for their response->ForwardIT]]

:: OpenAttachment
The attachment opens normally — it's a real pricing sheet. This time. But attackers count on urgency to bypass your judgment. In a study of successful phishing attacks, 78% used time pressure as the primary manipulation tactic. The VP's email was legitimate today, but this exact scenario — real name, plausible request, artificial deadline — is the template for business email compromise.

What made this risky: you had no way to verify authenticity from the email alone. The "correct" behavior felt slow and inconvenient. That's by design.

[[Continue->Debrief]]

:: CallVP
You dial the VP's extension. "Oh yeah, I sent that five minutes ago — thanks for checking, go ahead and open it." Verification took 45 seconds. In cases where the email IS fraudulent, this single step prevents the attack entirely. Out-of-band verification — confirming through a different communication channel — is the strongest defense against impersonation attacks.

The awkwardness of "Did you really send this?" is a feature, not a bug.

[[Continue->Debrief]]

:: ForwardIT
IT security responds 20 minutes later: the email was legitimate. The VP is annoyed about the delay. This approach is safe but has a real cost — in a genuine urgent situation, the 20-minute delay could matter. A faster verification method (calling the sender directly) gives you the same security benefit without the bottleneck.

Security procedures need to be fast enough that people actually follow them.

[[Continue->Debrief]]
```

### Knowledge Check Questions with Elaborative Feedback

```
Create {number} knowledge check questions for the following learning objective. These will be embedded in an interactive online course, not a formal exam.

LEARNING OBJECTIVE: {objective}
BLOOM'S LEVEL: {remember|apply|analyze|evaluate}
CONTEXT: {what the learner just experienced in the course — the preceding scenario or content}
SOURCE MATERIAL: {key facts the questions should test}

REQUIREMENTS:
1. Scenario-based stems: Begin each question with a realistic situation, not "Which of the following..."
2. Four options per question (single-select).
3. Plausible distractors: Each wrong answer should represent a common misconception or partial understanding. A learner who skimmed the content might choose any of them.
4. No giveaways: The correct answer should not be longer, more qualified, or grammatically different from distractors.
5. Elaborative feedback for EVERY option — not just correct/incorrect:
   - Correct: Reinforce WHY this is right and connect to the broader principle.
   - Incorrect: Explain the specific misconception this choice reflects and redirect thinking.
6. Each question should test a different facet of the objective.

OUTPUT FORMAT (JSON):
[
  {
    "stem": "scenario-based question text",
    "options": [
      {
        "text": "option text",
        "correct": true/false,
        "feedback": "elaborative feedback explaining why this choice is right/wrong"
      }
    ],
    "bloom_level": "string",
    "objective_id": "string",
    "difficulty": "easy|medium|hard"
  }
]
```

**Few-shot example — Good vs Bad questions:**

BAD:
```json
{
  "stem": "What is the shared responsibility model?",
  "options": [
    { "text": "A model where the cloud provider is responsible for everything", "correct": false, "feedback": "Incorrect." },
    { "text": "A model where the customer is responsible for everything", "correct": false, "feedback": "Incorrect." },
    { "text": "A model where security responsibilities are divided between the cloud provider and the customer, with the provider securing the infrastructure and the customer securing their data, applications, and configurations", "correct": true, "feedback": "Correct!" },
    { "text": "A model for sharing passwords", "correct": false, "feedback": "Incorrect." }
  ]
}
```
Problems: abstract stem (not scenario-based), correct answer is obviously longest, one distractor is absurd, feedback says nothing.

GOOD:
```json
{
  "stem": "Your team just migrated a PostgreSQL database to Amazon RDS. A week later, a security audit reveals the database is accessible from the public internet with a weak password. Your manager asks who is responsible. Based on the shared responsibility model, which answer is most accurate?",
  "options": [
    {
      "text": "AWS is responsible — they should have configured the database securely when it was provisioned",
      "correct": false,
      "feedback": "AWS provides the tools and the secure infrastructure, but configuration choices are yours. AWS secures the RDS service itself (patching the engine, physical security, storage encryption options), but network access rules and authentication settings are customer decisions. This is the 'security IN the cloud' side of the model."
    },
    {
      "text": "Your team is responsible — network access rules and authentication are customer-managed configurations",
      "correct": true,
      "feedback": "Exactly right. Under the shared responsibility model, AWS manages security OF the cloud (physical infrastructure, managed service availability, engine patching for RDS), while customers manage security IN the cloud — including network security groups, database credentials, and access policies. The public accessibility and weak password are both configuration decisions your team controls."
    },
    {
      "text": "Responsibility is shared equally — AWS should have flagged the misconfiguration automatically",
      "correct": false,
      "feedback": "While AWS does offer tools like AWS Config and Security Hub that CAN flag misconfigurations, enabling and acting on those tools is a customer responsibility. 'Shared responsibility' doesn't mean 50/50 on every task — it means clearly delineated ownership. AWS does provide guardrails, but you have to turn them on."
    },
    {
      "text": "The security auditor is responsible for finding it sooner",
      "correct": false,
      "feedback": "Auditors identify issues but don't own the configuration. This is a common deflection pattern in incident reviews — blaming the detection process instead of the root cause. The configuration was your team's responsibility from the moment the database was provisioned."
    }
  ]
}
```

### Narration Scripts (Complementing On-Screen Text)

```
Write a narration script for the following on-screen content block. The narration will be played as audio while the learner reads the screen.

ON-SCREEN TEXT: {the text that appears on screen}
ON-SCREEN VISUALS: {description of images, diagrams, or animations on screen}
CONTEXT: {where this falls in the course and what the learner just did}
VOICE ROLE: {narrator|character name}

CRITICAL RULE: The narration must NOT repeat the on-screen text. Instead, it should do one or more of:
- Add context or backstory that makes the on-screen content more meaningful
- Provide a real-world example or analogy
- Explain the "why" behind what's shown on screen
- Offer the narrator's perspective or editorial commentary
- Bridge from the previous block to this one
- Foreshadow what's coming next

CONSTRAINTS:
- Maximum 150 words.
- Write for the ear: short sentences, natural rhythm, contractions are fine.
- No parenthetical asides or complex clause structures.
- No "As you can see on your screen..." — the learner knows what's on screen.

OUTPUT: Just the narration text, nothing else.
```

**Few-shot example — Good vs Bad narration:**

BAD (duplicates screen):
- On-screen text: "The shared responsibility model divides security duties between the cloud provider and the customer. The provider secures the physical infrastructure, networking, and hypervisor. The customer secures their data, applications, identity management, and operating system configuration."
- Narration: "The shared responsibility model divides security duties between the cloud provider and the customer. The provider is responsible for securing the physical infrastructure, the networking layer, and the hypervisor. As a customer, you are responsible for securing your data, your applications, identity management, and operating system configuration."

GOOD (complements screen):
- On-screen text: "The shared responsibility model divides security duties between the cloud provider and the customer. The provider secures the physical infrastructure, networking, and hypervisor. The customer secures their data, applications, identity management, and operating system configuration."
- Narration: "Here's the thing most teams get wrong: they assume moving to the cloud means security is someone else's problem. It's not. It's a division of labor. Think of it like renting an office. The building owner handles the locks on the front door and the fire suppression system. But if you leave confidential files on your desk overnight, that's on you. The line between 'their job' and 'your job' shifts depending on the service you're using — and that's where mistakes happen."

### Image Generation Prompts with Style Consistency

```
Generate an image prompt for the following course illustration. The prompt should maintain visual consistency with the course style guide.

COURSE STYLE GUIDE:
- Style: {e.g., "Clean, modern flat illustration with subtle gradients. No outlines. Muted professional color palette."}
- Color palette: {e.g., "#1a1a2e, #16213e, #0f3460, #e94560, #f5f5f5"}
- Character style: {e.g., "Stylized, semi-realistic. Diverse workforce. Business casual clothing."}
- Mood: {e.g., "Professional but approachable. Warm lighting. Not sterile or corporate."}

SCENE DESCRIPTION: {what needs to be depicted}
CONTEXT IN COURSE: {what the learner is doing when they see this image}
EMOTIONAL TONE: {what feeling should the image evoke}

REQUIREMENTS:
1. Start with the style prefix to maintain consistency.
2. Describe specific details: setting, lighting, character positions, expressions.
3. Include negative prompt elements (what should NOT appear).
4. Specify composition (wide shot, close-up, over-the-shoulder, etc.).
5. The image should feel purposeful, not decorative — it should advance understanding.

OUTPUT: A complete prompt ready for DALL-E, Midjourney, or Stable Diffusion.
```

**Few-shot example — Good vs Bad image prompts:**

BAD: "A person at a computer looking worried about cybersecurity"

GOOD: "Clean flat illustration with subtle gradients, muted palette (#1a1a2e, #16213e, #0f3460, #e94560). A software engineer in a dark office, the glow of multiple monitors illuminating their face. One screen shows a terminal with red warning text, another shows an AWS console with a security alert. The engineer leans forward, hand on chin, expression focused and concerned but not panicked. Over-the-shoulder composition showing both the engineer and the screens. Warm desk lamp provides secondary light. Modern standing desk, plant in background. No text overlays, no watermarks, no stock-photo aesthetics. Semi-realistic style, not cartoonish."

BAD: "A classroom with students learning about cloud computing"

GOOD: "Clean flat illustration, muted professional palette (#1a1a2e, #16213e, #f5f5f5). Bird's-eye view of an open-plan office where a small team of four engineers huddles around a whiteboard. The whiteboard shows a rough diagram with boxes labeled 'us' and 'them' with a dotted line between (representing shared responsibility, but the text should be barely readable — it's a scene-setting detail, not a teaching diagram). Team members are diverse: different ethnicities, genders, ages. One person points at the whiteboard, another has a laptop open. Body language suggests active discussion, not passive listening. Natural daylight from large windows. No stock-photo smiles, no decorative elements."

---

## 3. Quality Control Prompts

### Factual Accuracy Review

```
Review the following course content for factual accuracy by cross-referencing against the provided source materials.

COURSE CONTENT:
{content.json or specific blocks to review}

SOURCE MATERIALS:
{research brief, original documents, or key facts}

FOR EACH FACTUAL CLAIM IN THE CONTENT:
1. Identify the claim.
2. Search for supporting evidence in the source materials.
3. Classify as:
   - VERIFIED: Found in sources with matching details.
   - PARTIALLY VERIFIED: Found in sources but with different details (e.g., different numbers, different framing).
   - UNVERIFIED: Not found in any source material.
   - CONTRADICTED: Directly contradicts source material.
   - OUTDATED: Found but may be stale (statistics older than 2 years, references to deprecated technology).

OUTPUT FORMAT:
{
  "claims_reviewed": number,
  "verified": number,
  "issues": [
    {
      "claim": "exact text of the claim",
      "block_index": number,
      "status": "unverified|contradicted|outdated|partially_verified",
      "source_says": "what the source actually says (or 'not found')",
      "recommendation": "specific fix"
    }
  ]
}

IMPORTANT: Err on the side of flagging. A false positive (flagging something that turns out to be correct) is far better than letting an inaccuracy through to learners.
```

### Voice Consistency Check

```
Review the following course content for voice consistency against the brand guidelines.

BRAND VOICE GUIDELINES:
{paste brand voice guide, or use these defaults:}
- Tone: Conversational, confident, direct
- Person: Second person ("you"), active voice
- Vocabulary: Plain language, no jargon unless defined. Technical terms are fine if the audience is technical.
- Personality: Smart colleague, not lecturer. Occasional dry humor is fine. Never sarcastic about the learner.
- Forbidden phrases: "In today's rapidly evolving landscape," "It is important to note that," "Let's dive in," "As we all know," "At the end of the day," "Moving forward," "Leverage," "Synergy," "Best-in-class"

CONTENT TO REVIEW:
{content blocks}

FOR EACH BLOCK, CHECK:
1. Is it in second person and active voice? Flag any passive constructions.
2. Does it use conversational tone? Flag anything that reads like a textbook or corporate memo.
3. Does it contain forbidden phrases or AI-detectable patterns?
4. Is the tone consistent with surrounding blocks? Flag abrupt tone shifts.
5. Does it respect learner intelligence? Flag anything condescending ("As you know…," "Simply put…," excessive hand-holding).

OUTPUT: A list of specific issues with quoted text and suggested rewrites.
For each issue, provide:
- The quoted problematic text
- Which guideline it violates
- A concrete rewrite suggestion
```

### Assessment Quality Evaluation

```
Evaluate the following assessment items for quality using these criteria.

ASSESSMENT ITEMS:
{quiz.json or question array}

COURSE OBJECTIVES THEY SHOULD MEASURE:
{objectives from course map}

EVALUATE EACH QUESTION ON:

1. BLOOM'S TAXONOMY ALIGNMENT
   - What level does this question ACTUALLY test? (Not what it claims to test.)
   - Remember: recalling a fact → "What is…"
   - Apply: using knowledge in a new situation → "Given this scenario, what would you…"
   - Analyze: breaking down and examining → "What is the most likely cause of…"
   - Evaluate: making judgments → "Which approach would be most effective for…"
   - Flag questions that claim to be "apply" but are actually "remember."

2. DISTRACTOR QUALITY
   - Is each distractor plausible? Would a learner with partial understanding choose it?
   - Flag absurd distractors that no one would choose.
   - Flag distractors that are too similar to each other.
   - Flag "all of the above" or "none of the above" options.

3. STEM QUALITY
   - Is the stem scenario-based or abstract?
   - Is the question clear without reading the options?
   - Flag negative stems ("Which is NOT…") — these test reading comprehension, not knowledge.
   - Flag stems that give away the answer.

4. FEEDBACK QUALITY
   - Does feedback for the correct answer explain WHY it's right?
   - Does feedback for incorrect answers explain the specific misconception?
   - Flag feedback that just says "Correct!" or "Incorrect, try again."
   - Flag feedback that reveals answers to other questions.

5. FAIRNESS AND BIAS
   - Flag questions where the correct answer is identifiable by:
     - Being the longest option
     - Using qualifying language ("usually," "in most cases")
     - Grammatical agreement with the stem
   - Flag culturally specific references that may disadvantage some learners.

OUTPUT FORMAT:
{
  "questions_reviewed": number,
  "overall_quality": "strong|adequate|needs_work|poor",
  "issues": [
    {
      "question_index": number,
      "criterion": "blooms|distractors|stem|feedback|fairness",
      "severity": "critical|high|medium|low",
      "issue": "description",
      "suggestion": "specific fix"
    }
  ],
  "bloom_distribution": { "remember": n, "apply": n, "analyze": n, "evaluate": n },
  "recommendation": "overall summary"
}
```

### Accessibility Review

```
Review the following course content and structure for accessibility compliance.

CONTENT:
{content.json blocks}

EVALUATE AGAINST:

1. TEXT ALTERNATIVES
   - Does every image block have alt_text? Flag missing alt text.
   - Is the alt text meaningful (describes the content/function) or decorative ("image of...")?
   - For complex diagrams, is there a long description or text equivalent?

2. KEYBOARD ACCESSIBILITY
   - Does every drag-and-drop block have a keyboard_alternative defined?
   - Are all interactive elements (branching choices, hotspots, sliders) operable without a mouse?
   - Flag any interaction that inherently requires pointing (e.g., "click on the area of the image").

3. STRUCTURE
   - Do heading levels follow a logical hierarchy (h1 → h2 → h3, no skipped levels)?
   - Are content blocks in a logical reading order?
   - Flag content that relies on visual positioning ("see the diagram on the right") without a structural relationship.

4. COLOR AND CONTRAST
   - Flag any content that uses color as the only means of conveying information (e.g., "the items in red are incorrect").
   - Flag text/background combinations that may fail WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text).

5. MULTIMEDIA
   - Does every audio block have a transcript or caption alternative?
   - Does every video reference have captions?
   - Flag auto-playing media without controls.

6. MOTION AND TIMING
   - Flag animations that cannot be paused or disabled.
   - Flag timed interactions that don't offer extended time.
   - Note whether prefers-reduced-motion is respected.

7. COGNITIVE ACCESSIBILITY
   - Flag walls of text (blocks over 100 words without a break).
   - Flag instructions that assume specific cultural knowledge.
   - Flag inconsistent navigation patterns between modules.

OUTPUT: A structured accessibility audit report with issues categorized by WCAG guideline number and severity.
```

---

## 4. Anti-Pattern Detection Prompts

### Textbook Content Detector

```
Analyze the following course content blocks and flag anything that reads like a textbook instead of an interactive learning experience. The goal of this course is behavior change, not information transfer.

CONTENT:
{content blocks}

FLAG THESE SPECIFIC PATTERNS:

1. PASSIVE INFORMATION DELIVERY
   - Blocks that present information without asking the learner to DO anything with it.
   - More than 2 consecutive content blocks without an interaction.
   - Sections that could be replaced with a PDF and would lose nothing.
   Example: "There are three types of phishing: spear phishing, whaling, and clone phishing. Spear phishing targets specific individuals..."
   Fix: Turn into a classification exercise — present examples and have learners identify the type.

2. NO DECISIONS REQUIRED
   - Modules where the learner never makes a choice or judgment.
   - Content where the only action is "click next."
   - Assessments only at the end of a module, not embedded throughout.
   Example: 5 screens of content → 3 quiz questions → next module.
   Fix: Open with a scenario, embed decisions throughout, make the quiz questions scenario-based.

3. ABSTRACT OVER CONCRETE
   - Definitions without examples.
   - Theory without application scenarios.
   - General principles without specific situations where they apply.
   Example: "Access control is the process of granting or denying access to resources based on policies."
   Fix: "Your intern asks for admin access to production. She says she needs it to debug a customer issue. What do you do?"

4. TELLING INSTEAD OF SHOWING
   - Stating that something is important instead of demonstrating why.
   - Listing best practices without showing consequences of not following them.
   Example: "It is critical to use strong passwords."
   Fix: Show a scenario where a weak password leads to a breach, then let the learner experience the consequence.

5. BULLET POINT SYNDROME
   - Content structured as bullet lists rather than narratives.
   - "Key takeaways" lists that summarize without requiring engagement.
   Example: "Key points: • Use MFA • Rotate credentials • Monitor logs"
   Fix: Turn each point into a scenario where the learner must identify the correct action.

FOR EACH PATTERN FOUND, PROVIDE:
- The specific block(s) where it occurs
- What pattern it matches
- A concrete suggestion for how to make it interactive
```

### Narration Duplication Detector

```
Compare the on-screen text and narration script for each content block. Flag any block where the narration duplicates the on-screen text.

CONTENT BLOCKS:
{blocks with both "text" and "narration_text" fields}

EVALUATION CRITERIA:

1. VERBATIM DUPLICATION — Narration uses the same sentences as on-screen text.
   Severity: Critical. This violates Mayer's redundancy principle and creates cognitive overload.

2. PARAPHRASE DUPLICATION — Narration says the same thing in slightly different words.
   Severity: High. Same information through two channels simultaneously still causes overload.

3. STRUCTURAL DUPLICATION — Narration follows the same outline/sequence as on-screen text, even with different wording.
   Severity: Medium. The narration should take a DIFFERENT angle, not the same angle restated.

4. COMPLEMENTARY (GOOD) — Narration adds context, examples, analogies, or perspective not present in on-screen text.
   This is correct. No flag needed.

FOR EACH BLOCK, REPORT:
- Duplication type (verbatim, paraphrase, structural, or complementary)
- Similarity percentage (rough estimate)
- The specific overlapping content
- A suggestion for how the narration should be rewritten to complement instead of duplicate

EXAMPLE OF BAD NARRATION:
Screen: "Multi-factor authentication requires two or more verification methods."
Narration: "Multi-factor authentication, or MFA, requires you to provide two or more methods of verification."
→ FLAG: Paraphrase duplication. Narration adds nothing.

EXAMPLE OF GOOD NARRATION:
Screen: "Multi-factor authentication requires two or more verification methods."
Narration: "Think about why this matters. A password, no matter how strong, is one thing an attacker needs to steal. Add a second factor — your phone, your fingerprint — and now they need to steal two things from two different places. That's exponentially harder."
→ PASS: Narration explains the WHY and uses an analogy. Screen states the WHAT.
```

### Generic Quiz Question Detector

```
Analyze the following assessment items and flag questions that are too generic, too easy, or don't require actual domain knowledge to answer.

ASSESSMENT ITEMS:
{quiz questions}

FLAG THESE PATTERNS:

1. GOOGLEABLE QUESTIONS
   - Questions that test recall of a definition rather than application of a concept.
   - "What does MFA stand for?" — Anyone can Google this. Test whether they can identify when MFA is needed instead.

2. OBVIOUSLY CORRECT ANSWERS
   - The correct answer is longer or more detailed than distractors.
   - The correct answer uses hedging language ("usually," "in most cases") while distractors use absolutes ("always," "never").
   - The correct answer is clearly the "safest" or most "complete" option.
   - One distractor is absurd, making it effectively a 3-option question.

3. CONTEXT-FREE QUESTIONS
   - "Which of the following is a benefit of encryption?" — No scenario, no application.
   - Replace with: "Your team needs to store customer credit card numbers. A colleague suggests storing them in plain text in the database to simplify development. What is the strongest argument against this approach?"

4. TRIVIAL QUESTIONS
   - Questions that anyone with common sense could answer correctly, even without taking the course.
   - "Is it a good idea to share your password with coworkers?" — This tests nothing.

5. NEGATIVE STEMS
   - "Which of the following is NOT..." — These test careful reading, not domain knowledge.

FOR EACH FLAGGED QUESTION, PROVIDE:
- The pattern it matches
- Why it's problematic
- A rewritten version that tests actual competence at the appropriate Bloom's level
```

### Missing Interaction Opportunity Detector

```
Analyze the following course content and identify missed opportunities for learner interaction. Every content block is a potential interaction point.

CONTENT:
{module content blocks}

LOOK FOR:

1. LISTS THAT SHOULD BE SORTING EXERCISES
   - Any list of items that could be categorized, ranked, or sequenced.
   - "There are four types of X..." → Drag-and-drop: classify examples into the four types.

2. PROCESSES THAT SHOULD BE SIMULATIONS
   - Any step-by-step procedure described in text.
   - "First, navigate to Settings. Then click Security..." → Interactive walkthrough where the learner performs the steps.

3. EXAMPLES THAT SHOULD BE SCENARIOS
   - Any "for example" or case study presented passively.
   - "For example, an attacker might..." → Branching scenario where the learner faces the attack.

4. CONCEPTS THAT SHOULD BE DISCOVERY EXERCISES
   - Content that presents a conclusion without letting the learner reach it.
   - "The most effective approach is..." → Let the learner try different approaches and discover which works.

5. COMPARISONS THAT SHOULD BE MATCHING EXERCISES
   - "X is different from Y in the following ways..." → Match characteristics to the correct concept.

6. LONG TEXT BLOCKS THAT SHOULD BE PROGRESSIVE DISCLOSURE
   - Any block over 80 words that could be broken into expandable sections, tabs, or scroll-triggered reveals.

FOR EACH OPPORTUNITY FOUND, PROVIDE:
- The specific content block
- The type of interaction it could become
- A brief description of the interaction design
- Which learning objective it would serve
```

---

## 5. Complete Few-Shot Examples: Good vs Bad Content

### Scenario Narratives

**BAD — Generic, passive, no stakes:**
```json
{
  "type": "narrative",
  "text": "In this module, we will learn about incident response procedures. Incident response is an important part of any organization's security program. When a security incident occurs, it is critical to follow the proper steps to contain and remediate the threat. The following sections will cover the key phases of incident response.",
  "narration_text": "Welcome to the incident response module. In this module, we will learn about incident response procedures. Incident response is an important part of any organization's security program."
}
```
Problems: Opens with "In this module," passive voice, no scenario, no stakes, narration duplicates screen, abstract and impersonal.

**GOOD — Specific, immersive, immediate tension:**
```json
{
  "type": "narrative",
  "text": "9:14 AM, Tuesday. Your monitoring dashboard lights up: 47 failed login attempts against the admin panel in the last 3 minutes, all from different IP addresses. Your phone buzzes — it's the CTO: 'Are we under attack?'",
  "narration_text": "This is the moment that separates teams who practiced from teams who didn't. Credential stuffing attacks are noisy — they show up on dashboards and trigger alerts. But the real danger isn't the attack itself. It's the 90-second window where your response either contains the damage or makes it worse."
}
```
Why it works: Specific time and details create immediacy. Screen text sets the scene. Narration adds the stakes and context without repeating the scene. Second person puts the learner in the seat.

---

### Assessment Feedback

**BAD — Says nothing useful:**
```json
{
  "question": "What should you do first when you suspect a security breach?",
  "options": [
    { "text": "Notify management", "correct": false, "feedback": "Incorrect. Try again." },
    { "text": "Contain the threat", "correct": true, "feedback": "Correct! Containment should be your first priority." },
    { "text": "Investigate the cause", "correct": false, "feedback": "Incorrect." },
    { "text": "Document the incident", "correct": false, "feedback": "Incorrect." }
  ]
}
```
Problems: Abstract stem (not scenario-based), feedback says nothing educational, wrong-answer feedback doesn't explain why, no learning happens from getting it wrong.

**GOOD — Teaches through feedback:**
```json
{
  "question": "Your monitoring shows active unauthorized access to the customer database — someone is downloading records right now. Your incident response plan has several immediate actions. Which do you prioritize?",
  "options": [
    {
      "text": "Send an all-hands Slack message to the security team with details of what you're seeing",
      "correct": false,
      "feedback": "Communication matters, but it's not step one when data is actively being exfiltrated. Every minute you spend composing a message is another minute the attacker is downloading records. Contain first, then communicate. A quick 'Incident in progress — stand by' message takes 5 seconds; a detailed briefing can wait until the bleeding stops."
    },
    {
      "text": "Revoke the compromised credentials and block the source IPs to stop the active exfiltration",
      "correct": true,
      "feedback": "Right call. When you can see active data exfiltration, containment is job one. Revoking the credentials cuts off the attacker's access immediately. Blocking the IPs adds a secondary layer in case they've established other sessions. This follows the NIST Incident Response framework: detect → contain → eradicate → recover. You're in the contain phase — stop the bleeding before you diagnose the wound."
    },
    {
      "text": "Start forensic analysis to understand how the attacker got in, so you can close the vulnerability",
      "correct": false,
      "feedback": "Understanding the root cause is essential — but not while data is actively leaving your systems. Forensics is an 'eradicate' phase activity. Right now you're in the 'contain' phase. Think of it like a burst pipe: you turn off the water main first, then figure out what caused the pipe to burst. If you start investigating while data flows out, you'll have a more complete forensic picture but a much larger breach."
    },
    {
      "text": "Check if the accessed data falls under any compliance regulations to assess notification requirements",
      "correct": false,
      "feedback": "Regulatory assessment is important and will absolutely need to happen — but it's a recovery-phase activity. Right now, every second of delay means more records exfiltrated and a larger eventual notification scope. Ironically, by containing the breach quickly, you reduce the compliance headache later. Stop the active threat, then assess the damage."
    }
  ]
}
```

---

### Narration Scripts

**BAD — Duplicates screen text and adds nothing:**

On-screen: "Phishing attacks use deceptive emails to trick users into revealing sensitive information such as passwords, credit card numbers, or personal data. These attacks have increased by 61% in the past year."

Narration: "Phishing attacks use deceptive emails to trick users into revealing sensitive information. This includes passwords, credit card numbers, and personal data. These types of attacks have increased by sixty-one percent in the past year."

Problems: Word-for-word repetition with minor rephrasing. Learner hears exactly what they read. Cognitive overload per Mayer's redundancy principle. The narration adds zero value.

**GOOD — Complements with perspective and example:**

On-screen: "Phishing attacks use deceptive emails to trick users into revealing sensitive information such as passwords, credit card numbers, or personal data. These attacks have increased by 61% in the past year."

Narration: "Last year, a single phishing email cost one company $4.7 million. The email looked like a routine invoice from a vendor they'd worked with for years. Same logo, same formatting, same sender name — just one character different in the domain. The finance team member who clicked it had ten years of experience and had completed security training twice. This isn't about careless people. It's about increasingly sophisticated attacks targeting the way humans naturally process information under time pressure."

Why it works: The screen gives the facts. The narration makes them concrete and personal with a specific story. It reframes the learner's understanding (this isn't about being careless) and builds empathy. No overlap between the two channels.

---

### Image Generation Prompts

**BAD — Vague, will produce generic stock-photo result:**
```
An office worker at a computer worried about cybersecurity
```
This produces: Generic person at desk with worried expression. A green padlock floating nearby. No connection to the course content. Could illustrate literally any security course ever made.

**GOOD — Specific, purposeful, style-consistent:**
```
Clean flat illustration, muted professional palette (#1a1a2e, #16213e, #0f3460, #e94560, #f5f5f5).
Close-up of two laptop screens side by side on a shared desk. Left screen shows a normal-looking email inbox with one email highlighted in a subtle red tint (#e94560). Right screen shows the same email's raw headers in a terminal window, revealing a different sender address.
A hand hovers over the mouse, paused in the act of clicking.
Shallow depth of field — the background office environment is blurred.
Natural office lighting with cool blue tones from the monitors.
Style: geometric, minimal, no outlines, soft shadows.
No text overlays, no padlock icons, no shield icons, no generic "cyber" imagery.
```
This produces: A specific moment from the course scenario (examining a suspicious email). It shows the exact behavior the course teaches (checking headers). The visual tension of the hovering hand mirrors the decision point. The style matches the course aesthetic.

---

### Branching Scenario Feedback

**BAD — Judgmental, uninformative:**
```
You chose to click the link. That was a mistake. You should always be careful about clicking links in emails. Your computer is now infected with malware. Please try to make better decisions next time.
```
Problems: Patronizing ("make better decisions"), doesn't explain what to look for, doesn't teach, makes the learner feel bad instead of smarter.

**GOOD — Consequential, educational, respectful:**
```
The link redirected through three domains before landing on a page that looked identical to your company's SSO login. You entered your credentials without noticing the URL was login-yourcompany.com.attacker.xyz instead of login.yourcompany.com.

Within minutes, the attacker used your credentials to access the shared engineering drive.

Here's what to notice next time: hover over any link before clicking and check the actual destination URL in the bottom-left of your browser. The domain that matters is the one right before the .com (or .org, .net) — everything before that can be faked. In this case, "yourcompany.com" was a subdomain of "attacker.xyz."

Most people who fall for this aren't careless — they're busy and the attack is designed to exploit that.
```
Why it works: Shows realistic consequences (not nuclear — proportional to the mistake). Teaches the specific skill (reading URLs, identifying the real domain). Ends by respecting the learner. They leave this feedback knowing something they didn't before.

---

## Putting It All Together

### Workflow for Using These Prompts

1. **Start a course creation session** by giving your LLM the appropriate system prompt for the current agent role.
2. **Use content generation prompts** as templates — fill in the variables from your research brief and course map.
3. **After each generation step**, switch to the QA Agent system prompt and run the relevant quality control prompts against the output.
4. **Use anti-pattern detection prompts** as a final sweep before human review.
5. **Include few-shot examples** whenever the agent drifts toward generic or low-quality output. The examples in this document can be included directly in your prompts as "here is what I want" and "here is what I don't want."

### Prompt Chaining Pattern

For a complete module, chain prompts in this order:

```
1. [Structure Agent] → Course outline from learning objectives
2. [Writer Agent]    → Narrative blocks for module opening scenario
3. [Writer Agent]    → Branching scenario (Twee format) for key decision point
4. [Writer Agent]    → Knowledge check questions with elaborative feedback
5. [Writer Agent]    → Narration scripts for each content block
6. [Media Agent]     → Image generation prompts for each illustration
7. [QA Agent]        → Factual accuracy review
8. [QA Agent]        → Narration duplication check
9. [QA Agent]        → Assessment quality evaluation
10. [QA Agent]       → Anti-pattern sweep (textbook, generic quiz, missing interactions)
11. [QA Agent]       → Accessibility review
12. [Writer Agent]   → Revise based on QA findings
13. Repeat 7-12 until QA passes
14. → Human SME review
```

### Tips for Prompt Effectiveness

- **Always include source materials** in the context. Grounded generation is dramatically better than ungrounded.
- **Include the bad examples.** Models learn as much from "don't do this" as from "do this." The few-shot examples above are designed to be included directly.
- **Set the right temperature.** Use lower temperature (0.3-0.5) for factual content and assessments. Use higher temperature (0.7-0.9) for scenario narratives and creative elements.
- **Iterate with the QA agent, not manually.** When content needs revision, pass the QA report to the Writer Agent as revision instructions rather than editing by hand.
- **Keep system prompts stable across a session.** Don't modify the system prompt mid-conversation — this confuses the model about its role. Start a new conversation for a new agent role.
