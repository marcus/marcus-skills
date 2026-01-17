---
name: dev-docs
description: "Create exceptional developer documentation for open source projects. Use when: (1) Writing README files, (2) Creating API documentation, (3) Building getting-started guides, (4) Writing tutorials or how-to guides, (5) Documenting CLI tools, (6) Analyzing a codebase to derive features for documentation. Produces docs that are concise yet complete, scannable, and user-oriented."
---

# Developer Documentation Skill

Create clear, useful documentation that helps developers get productive quickly.

## Core Principles

**User-first**: Write for the developer reading the docs, not the developer who wrote the code. Answer "what can I do?" before "how does it work?"

**Concise but complete**: Every sentence must earn its place. Cut filler words. Use short paragraphs (2-4 sentences max). Include enough detail for users to succeed without hand-holding.

**Scannable**: Developers skim. Use headers, code blocks, and bullet lists strategically. Put the most important information first.

**Progressive disclosure**: Start simple, go deep. Quick start → common use cases → advanced topics → reference.

## Documentation Workflow

1. **Analyze the codebase** → See [codebase-analysis.md](references/codebase-analysis.md)
2. **Identify doc type needed** → See [doc-types.md](references/doc-types.md)
3. **Write following patterns** → See [examples.md](references/examples.md)
4. **Verify completeness** → Use checklist below

## Writing Guidelines

### Headlines and Structure

```markdown
# Project Name          ← What is it (1 line)
Brief tagline           ← Why should I care

## Quick Start          ← Get running in <5 min
## Installation         ← How to install
## Usage               ← Core functionality
## API Reference       ← Complete reference (or link)
## Contributing        ← How to help
```

### Code Examples

Every feature needs a working code example. Follow this pattern:

```markdown
### Feature Name

Brief description of what this does and when to use it.

\`\`\`python
# Minimal working example
result = library.do_thing("input")
print(result)  # Expected: "output"
\`\`\`

For more options, see [Advanced Usage](#advanced-usage).
```

**Code example rules:**
- Runnable as-is (no `...` or `# your code here`)
- Show expected output in comments
- Minimal—only what's needed to demonstrate the feature
- Use realistic but simple data

### Tone and Voice

| Do | Don't |
|----|-------|
| "Run `npm install`" | "You'll want to run..." |
| "Returns the user ID" | "This function returns..." |
| "Requires Node 18+" | "Please note that you will need..." |
| Active voice | Passive voice |
| Present tense | Future tense |

### Common Patterns

**Feature introduction:**
```markdown
## Caching

Store expensive computations for faster subsequent calls.

\`\`\`python
@cache(ttl=3600)
def fetch_user(id):
    return db.query(id)
\`\`\`
```

**Configuration options:**
```markdown
## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeout` | int | 30 | Request timeout in seconds |
| `retries` | int | 3 | Number of retry attempts |
```

**Warning/note callouts:**
```markdown
> **Note**: Requires authentication. See [Auth Guide](#authentication).

> **Warning**: This operation is destructive and cannot be undone.
```

## Prioritization

When documenting a codebase, prioritize:

1. **Happy path first**: The most common use case gets the most attention
2. **Frequency over complexity**: Document what users do often, not what's clever
3. **Entry points**: README, Quick Start, Installation get extra polish
4. **Error states**: Document common errors and their solutions

## Completeness Checklist

Before finalizing documentation:

- [ ] Can a new user get started in under 5 minutes?
- [ ] Does every public API have a code example?
- [ ] Are common errors and solutions documented?
- [ ] Is installation covered for major platforms?
- [ ] Do all code examples actually run?
- [ ] Is there a clear path from beginner to advanced?
- [ ] Are dependencies and requirements listed?

## Reference Files

- **[codebase-analysis.md](references/codebase-analysis.md)**: How to browse and understand a codebase to derive documentation
- **[doc-types.md](references/doc-types.md)**: Templates for different documentation types (README, API, guides)
- **[examples.md](references/examples.md)**: Good and bad documentation examples with explanations
