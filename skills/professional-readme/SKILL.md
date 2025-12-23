name: professional-readme
description: Create a concise, complete, developer-focused README.md for software projects that experienced developers can use immediately.
metadata:
  author: marcus-vorwaller
  version: "1.0"
---

# Professional README.md Design

This skill standardizes README.md creation for software projects targeting experienced developers. The resulting README should be **clear, concise, and actionable**—not verbose, decorative, or redundant.

Good README.md files answer a core set of questions quickly:

* What is this?
* Why does it matter?
* How do I use it?
* How do I develop or contribute?
* What do I need to know to build, test, and deploy?

This skill produces structured, scannable READMEs with precise labels and instructions. A README that reliably gets developers productive in under 10 minutes is successful.  [oai_citation:0‡DEV Community](https://dev.to/haegis/readme-first-how-to-make-your-project-instantly-understandable-3p89?utm_source=chatgpt.com)

---

## When to apply this skill

Use when a project needs:

* Primary documentation at the repository root
* Onboarding documentation for new developers
* Public or internal open-source readiness
* Clear developer instructions before external docs exist

Do **not** use when:

* Full reference docs exist elsewhere (link instead)
* The file would duplicate extensive external documentation

---

## Inputs you should gather

When drafting:

1. **Project purpose**: one-sentence explanation of what it does and why it exists.
2. **Audience**: contributors, maintainers, cross-team engineers, or open-source users.
3. **Dependencies & environment**: languages, runtimes, tools, supported platforms.
4. **Build/run instructions**: exact commands and environment variables.
5. **Usage**: common examples, API snippets, CLI commands.
6. **Contribution workflow**: tests, code style, branch strategy.
7. **Status/roadmap**: active, maintenance, planned changes.
8. **Licensing**: clear license terms.  [oai_citation:1‡freeCodeCamp](https://www.freecodecamp.org/news/how-to-structure-your-readme-file/?utm_source=chatgpt.com)

---

## Output expectations

When activated, produce:

* A **structured README.md** text solely in markdown
* Concise sections with **precise titles**
* No decorative badges or emojis unless status is critical
* Code blocks for all commands and examples
* Consistent naming and links to docs/tests/licenses
* Optional: embedded diagrams or minimal visuals only where they clarify non-trivial architecture

---

## Core README structure

The recommended sequence below supports **scan first, dive later** patterns.

### 1. Project title and tagline

Short, descriptive title with an optional tagline.

Example:

project-name

A fast, modular CLI for managing distributed workflows.

Taglines answer: what it is and why you care.  [oai_citation:2‡freeCodeCamp](https://www.freecodecamp.org/news/how-to-structure-your-readme-file/?utm_source=chatgpt.com)

### 2. One-paragraph overview

Summarize core function and distinguishing aspects. Include key constraints or intended use cases. Avoid long narratives.

### 3. Status and roadmap

Short status (e.g., active development / stable / maintenance) with **links** to detailed roadmap artifacts (issues/milestones).  [oai_citation:3‡Archbee](https://www.archbee.com/blog/readme-document-elements?utm_source=chatgpt.com)

### 4. Table of Contents (optional)

Only include if the README is long. Keep this minimal.

### 5. Quick start

Fastest path to running or using the project:

install

git clone …

build

make

run

./project –help

Include **prerequisites**, versions, and notable environment settings.  [oai_citation:4‡freeCodeCamp](https://www.freecodecamp.org/news/how-to-structure-your-readme-file/?utm_source=chatgpt.com)

### 6. Installation

Command-by-command setup steps. Use explicit code blocks.

### 7. Usage examples

Show 3–5 common patterns developers will care about:

* API example calls
* CLI example invocations
* Expected outputs

### 8. Architecture summary (for complex systems)

Concise overview of:

* major modules
* data flow
* external dependencies

Keep this section brief and link to deeper docs when necessary.  [oai_citation:5‡Archbee](https://www.archbee.com/blog/readme-document-elements?utm_source=chatgpt.com)

### 9. Development setup

Cover local dev bootstrapping:

* build tools
* environment configuration
* test execution
* linting and format rules

### 10. Tests & quality checks

Commands and expectations for running test suites and quality tooling.

### 11. Contributing

High-level guide plus link to `CONTRIBUTING.md` (not duplicated). Include tests and review expectations. Refer to standard conventions.  [oai_citation:6‡Wikipedia](https://en.wikipedia.org/wiki/Contributing_guidelines?utm_source=chatgpt.com)

### 12. License

Clear license declaration with link to `LICENSE` file. Optionally include short license text if brief.

### 13. Contact & support

Where to get help (issues, Slack, email). Only include if relevant.

---

## Section guidelines

### Focus on precision

* Clear section headings (`## Installation`, `## Usage`)
* No verbosity: aim to convey meaning in few lines.  [oai_citation:7‡freeCodeCamp](https://www.freecodecamp.org/news/how-to-structure-your-readme-file/?utm_source=chatgpt.com)

### Examples over explanations

* Real commands > abstract descriptions
* Real input/output > conceptual descriptions

### Cross-link liberally

* Link to tests
* Link to architecture docs
* Link to API reference

External docs should not be duplicated; they should be linked.  [oai_citation:8‡Archbee](https://www.archbee.com/blog/readme-document-elements?utm_source=chatgpt.com)

### Avoid

* Overly long prose
* Developer anecdotes
* Screenshots for internal or text-driven tools (unless they clarify structure or output)

### Optional enhancements

* Minimal architecture ASCII diagrams (only where useful)
* Badges for CI status and coverage (sparingly; not central)  [oai_citation:9‡freeCodeCamp](https://www.freecodecamp.org/news/how-to-structure-your-readme-file/?utm_source=chatgpt.com)

---

## QA checklist

Before finalizing:

* Can a developer **clone, build, and run** in 10 minutes?
* Are all commands exact and tested?
* Are section titles self-explanatory?
* Are key dependencies and versions specified?
* Are tests and contribution paths clear?

---

## Workflow summary

1. Ask for project purpose and audience.
2. Draft section titles and outline.
3. Flesh in quick start, usage, build instructions.
4. Add architecture and development details.
5. Add tests, contributions, license, and support.
6. Review README for conciseness and completeness.
