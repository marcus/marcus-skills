# Codebase Analysis for Documentation

How to explore an unfamiliar codebase and extract features for documentation.

## Analysis Workflow

### Step 1: Identify Entry Points

Start with files that reveal project structure and intent:

```
README.md           → Existing docs, project purpose
package.json        → Dependencies, scripts, project metadata
pyproject.toml      → Python project config
Cargo.toml          → Rust project config
go.mod              → Go module definition
Makefile            → Build commands, common tasks
```

**What to extract:**
- Project name and description
- Installation commands
- Build/run commands
- Key dependencies (what the project uses)

### Step 2: Find Public API Surface

Locate what users interact with:

| Language | Look For |
|----------|----------|
| Python | `__init__.py` exports, `__all__` lists |
| JavaScript | `index.js`, `exports` in package.json |
| Rust | `pub` items in `lib.rs` |
| Go | Capitalized functions/types (exported) |
| CLI tools | Argument parsers, help text |

**Search patterns:**
```bash
# Find main exports
grep -r "^export " src/
grep -r "__all__" --include="*.py"

# Find CLI entry points
grep -r "argparse\|click\|typer" --include="*.py"
grep -r "commander\|yargs" --include="*.js"

# Find public functions/classes
grep -r "^pub fn\|^pub struct" --include="*.rs"
grep -rn "^def \|^class " --include="*.py" | head -50
```

### Step 3: Understand Feature Hierarchy

Prioritize by user impact:

**Tier 1 - Core features** (document thoroughly):
- Main entry point function/class
- Primary use case
- Most-used methods/endpoints

**Tier 2 - Common features** (document with examples):
- Configuration options
- Common variations
- Error handling

**Tier 3 - Advanced features** (document briefly):
- Edge cases
- Power-user options
- Internal APIs (if exposed)

### Step 4: Trace Usage Patterns

Find real examples in:

```
tests/              → How the library is used correctly
examples/           → Intended usage patterns
docs/               → Existing documentation
*_test.py           → Test files show API usage
*.spec.js           → JavaScript test specs
```

**Extract from tests:**
- Setup/initialization patterns
- Common parameter combinations
- Expected outputs
- Error conditions

### Step 5: Identify Configuration

Find all configuration surfaces:

```bash
# Environment variables
grep -r "os.environ\|process.env\|env::" src/

# Config files
ls -la *.json *.yaml *.toml *.ini

# CLI flags
grep -r "add_argument\|option\|flag" src/
```

## Feature Prioritization Matrix

Score each feature (1-5) on these dimensions:

| Dimension | Question |
|-----------|----------|
| **Frequency** | How often will users need this? |
| **Visibility** | Is this in the critical path? |
| **Complexity** | Does this need explanation? |
| **Risk** | Can misuse cause problems? |

**Document first:** High frequency + High visibility
**Document thoroughly:** High complexity + High risk
**Document briefly:** Low frequency + Low complexity

## Common Codebase Patterns

### Library Pattern
```
src/
├── lib.rs / index.js / __init__.py  ← Main exports (start here)
├── core/                             ← Core functionality
├── utils/                            ← Helper functions
└── types/                            ← Type definitions
```

### CLI Tool Pattern
```
src/
├── main.rs / cli.py / index.js      ← Entry point
├── commands/                         ← Subcommands
├── config/                           ← Configuration handling
└── output/                           ← Output formatting
```

### Web Framework Pattern
```
src/
├── app.py / server.js               ← Entry point
├── routes/ or handlers/             ← API endpoints
├── models/                          ← Data models
├── middleware/                      ← Request processing
└── utils/                           ← Helpers
```

## Red Flags to Document

When you see these, they need explicit documentation:

- Surprising default values
- Required setup steps not obvious from code
- Breaking changes from previous versions
- Platform-specific behavior
- Performance implications
- Security considerations

## Output: Feature Inventory

After analysis, create a feature list:

```markdown
## Feature Inventory

### Core (Tier 1)
- [ ] `create()` - Main entry point, creates X from Y
- [ ] `process()` - Transforms data, most common operation

### Common (Tier 2)
- [ ] Configuration via `config.json`
- [ ] CLI flags: --verbose, --output
- [ ] Error types and handling

### Advanced (Tier 3)
- [ ] Custom middleware
- [ ] Plugin system
- [ ] Performance tuning options
```

Use this inventory to guide documentation structure.
