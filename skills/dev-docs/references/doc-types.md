# Documentation Types

Templates and guidance for different documentation formats.

## README.md

The project's front door. Optimized for GitHub/GitLab display.

### Structure

```markdown
# Project Name

One-line description of what this does.

[![Build](badge-url)](link) [![License](badge-url)](link)

## Quick Start

\`\`\`bash
npm install project-name
\`\`\`

\`\`\`javascript
import { thing } from 'project-name';
const result = thing.do('input');
\`\`\`

## Installation

### npm
\`\`\`bash
npm install project-name
\`\`\`

### yarn
\`\`\`bash
yarn add project-name
\`\`\`

## Usage

### Basic Usage

[Most common use case with code example]

### Configuration

[Configuration options table or examples]

## API

[Brief API overview or link to full docs]

## Contributing

[Link to CONTRIBUTING.md or brief instructions]

## License

MIT - see [LICENSE](LICENSE)
```

### README Rules

- First code block should be copy-pasteable and work
- Keep under 500 lines; link to docs for details
- Badges: build status, version, license (no vanity badges)
- Include "Why this project?" only if not obvious from name

---

## Getting Started Guide

For users who need more than a README quick start.

### Structure

```markdown
# Getting Started with Project Name

This guide walks you through setting up Project Name for the first time.

## Prerequisites

- Node.js 18 or higher
- npm or yarn
- [Other requirements]

## Installation

### Step 1: Install the package

\`\`\`bash
npm install project-name
\`\`\`

### Step 2: Configure your environment

Create a config file at `~/.project/config.json`:

\`\`\`json
{
  "apiKey": "your-api-key",
  "region": "us-east-1"
}
\`\`\`

### Step 3: Verify installation

\`\`\`bash
project-name --version
# Expected: project-name v2.1.0
\`\`\`

## Your First [Action]

Now let's [primary action]:

\`\`\`javascript
// Complete working example
import { Client } from 'project-name';

const client = new Client();
const result = await client.doThing({
  input: 'example'
});

console.log(result);
// Output: { success: true, data: [...] }
\`\`\`

## Common Issues

### Error: "API key not found"

Make sure your config file is at the correct location...

### Error: "Connection refused"

Check that the service is running...

## Next Steps

- [Core Concepts](./concepts.md) - Understand the fundamentals
- [API Reference](./api.md) - Full API documentation
- [Examples](./examples/) - More code examples
```

---

## API Reference

Complete reference for all public APIs.

### Structure

```markdown
# API Reference

## Overview

Brief description of the API structure.

## Authentication

\`\`\`javascript
const client = new Client({ apiKey: 'your-key' });
\`\`\`

## Methods

### `client.create(options)`

Creates a new resource.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `name` | string | Yes | - | Resource name |
| `type` | string | No | `"default"` | Resource type |
| `options` | object | No | `{}` | Additional options |

**Returns:** `Promise<Resource>`

**Example:**

\`\`\`javascript
const resource = await client.create({
  name: 'my-resource',
  type: 'premium'
});
// Returns: { id: 'res_123', name: 'my-resource', ... }
\`\`\`

**Errors:**

| Code | Description |
|------|-------------|
| `INVALID_NAME` | Name contains invalid characters |
| `QUOTA_EXCEEDED` | Resource limit reached |

---

### `client.get(id)`

Retrieves a resource by ID.

[Same structure as above]
```

### API Reference Rules

- One method per section with clear heading
- Parameters table for anything with >1 parameter
- Always show return type
- Include realistic example with expected output
- Document errors users will encounter

---

## How-To Guide

Task-focused guides for specific goals.

### Structure

```markdown
# How to [Accomplish Specific Task]

This guide shows how to [task] using Project Name.

## Overview

[1-2 sentences on what we're building/doing]

## Prerequisites

- Project Name installed ([Getting Started](./getting-started.md))
- [Other specific requirements]

## Steps

### 1. [First Action]

[Brief explanation]

\`\`\`javascript
// Code for step 1
\`\`\`

### 2. [Second Action]

[Brief explanation]

\`\`\`javascript
// Code for step 2
\`\`\`

### 3. [Final Action]

[Brief explanation]

\`\`\`javascript
// Complete example pulling it together
\`\`\`

## Complete Example

Here's the full code:

\`\`\`javascript
// All steps combined into runnable example
\`\`\`

## Variations

### Using [Alternative Approach]

[Brief alternative if common]

## Troubleshooting

### [Common Problem]

[Solution]

## Related Guides

- [Related How-To 1](./related-1.md)
- [Related How-To 2](./related-2.md)
```

---

## CLI Documentation

For command-line tools.

### Structure

```markdown
# CLI Reference

## Installation

\`\`\`bash
npm install -g project-cli
\`\`\`

## Commands

### `project init`

Initialize a new project.

\`\`\`bash
project init [name] [options]
\`\`\`

**Arguments:**

| Argument | Description |
|----------|-------------|
| `name` | Project name (default: current directory) |

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--template` | `-t` | `default` | Template to use |
| `--force` | `-f` | `false` | Overwrite existing files |

**Examples:**

\`\`\`bash
# Basic usage
project init my-app

# With template
project init my-app --template typescript

# In current directory
project init .
\`\`\`

---

### `project build`

[Same structure]

## Configuration

### Config File

Create `.projectrc` in your project root:

\`\`\`json
{
  "output": "./dist",
  "minify": true
}
\`\`\`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_TOKEN` | API token | - |
| `PROJECT_ENV` | Environment | `development` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
```

---

## Changelog

Track version changes.

### Structure

```markdown
# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- New feature X

## [2.1.0] - 2024-01-15

### Added
- Support for async operations (#123)
- New `--verbose` flag

### Changed
- Improved error messages for invalid input

### Fixed
- Memory leak in long-running processes (#456)

### Deprecated
- `oldMethod()` - use `newMethod()` instead

## [2.0.0] - 2024-01-01

### Breaking Changes
- Minimum Node version is now 18
- `config.legacy` option removed

[Previous versions...]
```

---

## Doc Type Selection Guide

| User Need | Doc Type |
|-----------|----------|
| "What is this?" | README |
| "How do I install?" | Getting Started |
| "What methods exist?" | API Reference |
| "How do I do X?" | How-To Guide |
| "What changed?" | Changelog |
| "How do I run this command?" | CLI Reference |
