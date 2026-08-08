# Documentation Examples

Good and bad examples with explanations.

## Project Descriptions

### ❌ Bad
```markdown
# MyLib

MyLib is a library that provides functionality for doing things with data.
It was created to solve problems that developers face when working with data.
```
**Problems:** Vague, says nothing specific, "doing things with data" is meaningless.

### ✅ Good
```markdown
# MyLib

Fast JSON schema validation for Node.js. Validates 100k objects/second.
```
**Why it works:** Specific (JSON schema), measurable claim (100k/s), clear use case.

---

## Installation Instructions

### ❌ Bad
```markdown
## Installation

You'll want to make sure you have Node.js installed on your system before
proceeding with the installation. Once you've verified that, you can go
ahead and run the following command to install the package:

\`\`\`
npm install mylib
\`\`\`
```
**Problems:** Wordy preamble, assumes user doesn't know npm, condescending tone.

### ✅ Good
```markdown
## Installation

\`\`\`bash
npm install mylib
\`\`\`

Requires Node.js 18+.
```
**Why it works:** Command first, prerequisites as one-liner, respects user's time.

---

## Code Examples

### ❌ Bad
```markdown
## Usage

Here's how you can use the library:

\`\`\`javascript
const mylib = require('mylib');

// Create a new instance
const instance = new mylib.Thing();

// Configure it
instance.configure({
  // Add your configuration here
  ...
});

// Use it
const result = instance.process(data);
```
**Problems:** `...` isn't runnable, `data` undefined, no expected output, vague comments.

### ✅ Good
```markdown
## Usage

\`\`\`javascript
const { Thing } = require('mylib');

const validator = new Thing({ strict: true });
const result = validator.check({ name: 'test', count: 5 });

console.log(result.valid);  // true
console.log(result.errors); // []
\`\`\`
```
**Why it works:** Complete and runnable, shows real values, includes expected output.

---

## API Documentation

### ❌ Bad
```markdown
### process(input)

This function processes the input and returns the result.

Parameters:
- input: The input to process

Returns:
- The processed result
```
**Problems:** Circular definition, no types, no example, "result" means nothing.

### ✅ Good
```markdown
### `validate(schema, data)`

Validates data against a JSON schema.

| Parameter | Type | Description |
|-----------|------|-------------|
| `schema` | `object` | JSON Schema object |
| `data` | `any` | Data to validate |

**Returns:** `ValidationResult`

\`\`\`javascript
const result = validate(
  { type: 'object', required: ['name'] },
  { name: 'Alice' }
);
// { valid: true, errors: [] }
\`\`\`
```
**Why it works:** Types specified, parameters in table, concrete example with output.

---

## Error Documentation

### ❌ Bad
```markdown
## Errors

The library may throw errors in certain conditions. Make sure to
handle them appropriately.
```
**Problems:** Says nothing useful, no specific errors, no solutions.

### ✅ Good
```markdown
## Errors

### `ValidationError`

Thrown when input fails validation.

\`\`\`javascript
try {
  validate(schema, data);
} catch (e) {
  if (e.code === 'VALIDATION_ERROR') {
    console.log(e.path);   // Field that failed: "user.email"
    console.log(e.reason); // Why: "must be valid email"
  }
}
\`\`\`

### `SchemaError`

Thrown when the schema itself is invalid. Check your schema definition.
```
**Why it works:** Specific error types, shows how to catch and extract info, actionable.

---

## Configuration Tables

### ❌ Bad
```markdown
## Options

- timeout: how long to wait
- retries: number of retries
- verbose: enables verbose mode
```
**Problems:** No types, no defaults, descriptions are just restatements.

### ✅ Good
```markdown
## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeout` | `number` | `30000` | Request timeout in milliseconds |
| `retries` | `number` | `3` | Retry attempts before failing |
| `verbose` | `boolean` | `false` | Log all HTTP requests to console |
```
**Why it works:** Complete information in scannable format, units specified.

---

## Warning Callouts

### ❌ Bad
```markdown
Note: Be careful when using this function as it may cause issues
if not used correctly. Please read the documentation thoroughly
before proceeding.
```
**Problems:** Vague fear-mongering, no specific guidance, wastes words.

### ✅ Good
```markdown
> **Warning**: `deleteAll()` permanently removes data. This cannot be undone.
> Back up your database before running in production.
```
**Why it works:** Specific action, clear consequence, actionable advice.

---

## Feature Introductions

### ❌ Bad
```markdown
## Caching

This section describes the caching functionality provided by the library.
Caching is a technique used to store frequently accessed data in memory
for faster retrieval. The library provides a comprehensive caching solution
that can help improve the performance of your application.
```
**Problems:** Explains what caching is (user knows), doesn't show how to use it.

### ✅ Good
```markdown
## Caching

Cache function results to avoid repeated computation:

\`\`\`javascript
const cached = cache(expensiveFunction, { ttl: 3600 });

cached('arg');  // Runs function, caches result
cached('arg');  // Returns cached result instantly
\`\`\`

Cache is stored in memory by default. For Redis storage, see [Advanced Caching](#advanced).
```
**Why it works:** Shows usage immediately, brief explanation integrated with code.

---

## Comparison: Wordy vs Concise

### ❌ Wordy (67 words)
```markdown
In order to get started with this library, you will first need to make sure
that you have properly installed all of the necessary dependencies. Once you
have done that, you can proceed to import the library into your project by
using the require statement as shown below. After importing, you will be able
to start using the various features and functionalities provided by the library.
```

### ✅ Concise (12 words)
```markdown
Install dependencies, then import:

\`\`\`javascript
const lib = require('mylib');
\`\`\`
```

---

## Quick Checklist

When reviewing documentation, check for:

| Issue | Fix |
|-------|-----|
| "This function does X" | Just say what it does |
| Undefined variables in examples | Use real values |
| `...` or `// your code` | Write complete examples |
| "Be careful" without specifics | State the exact risk |
| Long preambles | Delete them |
| Missing types | Add type annotations |
| No expected output | Show what code returns |
