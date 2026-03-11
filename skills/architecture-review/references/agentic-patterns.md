# Agentic Architecture Patterns

How to structure projects so AI coding agents can understand, modify, and extend them reliably.

## Core Principle

Engineers are shifting from writing code to orchestrating agents that write code. The human role concentrates on architecture, system design, and strategic decisions. Agents handle implementation under structured oversight.

**Governance model: Bounded Autonomy**
- Clear operational limits for agents
- Mandatory escalation paths for high-stakes decisions
- Comprehensive audit trails for all agent actions
- Three-tier boundaries: Always do / Ask first / Never do

---

## Agent-Native Project Structure

### Directory Conventions

Use feature-first (vertical slice) organization. Each module is self-contained:

```
src/
  modules/
    orders/
      domain/           # Entities, value objects, domain events
      application/      # Use cases, command/query handlers
      infrastructure/   # DB adapters, API clients, messaging
      api/              # HTTP controllers, gRPC handlers
      __tests__/        # Co-located tests
    inventory/
      ...
  shared/               # Cross-cutting: auth, logging, errors
  config/               # Configuration loading
  main.ts               # Composition root
docs/
  adr/                  # Architecture Decision Records
  module-map.md         # Module dependency graph
.claude/
  skills/               # Project-specific agent skills
CLAUDE.md               # Agent instructions
```

### Why This Works for Agents

- **Focused context:** Agent working on orders loads only `src/modules/orders/` -- no unrelated code pollutes context
- **Clear boundaries:** Hexagonal layers make it obvious where new code belongs
- **Parallel work:** Multiple agents can work on different modules simultaneously via Git worktrees
- **Discoverable:** Module map and CLAUDE.md tell agents where things are without searching

---

## CLAUDE.md Best Practices

The instruction file agents read at session start. Critical for consistent behavior.

### What to Include

```markdown
# Project Name

## Tech Stack
- Runtime: Bun 1.3
- Framework: SvelteKit 2
- Database: PostgreSQL with Drizzle ORM
- Testing: Vitest + Playwright

## Commands
- `bun run dev` -- start dev server
- `bun run test` -- run all tests
- `bun run test:unit` -- unit tests only
- `bun run lint` -- lint and format check
- `bun run db:migrate` -- run migrations

## Architecture
Modular monolith with hexagonal architecture.
See docs/module-map.md for module dependencies.
See docs/adr/ for architecture decisions.

## Conventions
- Use ES modules, prefer named exports
- One component per file
- Co-locate tests with source code
- Database queries only in infrastructure/ layer
- All new features require tests before implementation (TDD)

## Boundaries
### Always Do
- Run tests before completing any task
- Create ADRs for significant decisions
- Use existing patterns from the codebase

### Ask First
- Adding new dependencies
- Changing API contracts
- Modifying shared/ code

### Never Do
- Modify migration files that have been applied
- Commit secrets or credentials
- Skip type checking
```

### Key Principles

- **Be specific:** "Use ES modules, prefer named exports" not "Format code properly"
- **Include commands:** Agents use these exact commands
- **Document gotchas:** Auth modules with retry logic, files that should never be modified
- **Progressive disclosure:** Point to docs instead of inlining everything
- **Keep concise:** Every line costs context window tokens

---

## Test-Driven Development with Agents

TDD is dramatically more effective with AI agents than write-first approaches.

### Why TDD Matters for Agents

Without pre-existing tests, agents write tests that verify broken behavior -- "tests that confirm whatever incorrect implementation they produced." TDD prevents this critical failure mode.

### Workflow

1. **Human writes failing test** (or spec describing expected behavior)
2. **Agent writes minimum code** to make the test pass
3. **Human reviews** and requests refactoring
4. **Agent refactors** while keeping tests green
5. Repeat

### Mutation Testing for AI-Generated Code

AI-generated tests achieve only ~20% mutation scores on real-world code. Set minimum thresholds:

| Code Category | Minimum Mutation Score |
|---------------|----------------------|
| Critical paths (auth, payments) | 70% |
| Standard features | 50% |
| Experimental / prototype code | 30% |

---

## Parallel Agent Work

### Git Worktrees

The standard isolation pattern. Each agent gets its own working directory and branch.

```bash
# Create worktree for agent task
git worktree add ../project-feature-x feature-x

# Agent works in ../project-feature-x independently
# No conflicts with other agents or the main tree

# After review, merge and clean up
git worktree remove ../project-feature-x
```

### Orchestration Patterns

| Pattern | Description | Use When |
|---------|-------------|----------|
| **Lead + subagents** | Orchestrator decomposes, delegates, synthesizes | Complex multi-module tasks |
| **Parallel fan-out** | Multiple agents tackle same problem | Need comprehensive coverage |
| **Pipeline** | Sequential agents, each adds a layer | Build → test → review → deploy |
| **Generator-evaluator** | One generates, another evaluates and feedbacks | Quality-critical output |

---

## Quality Gates for Agent Output

### Layered Guardrail Stack

Each layer catches different failure modes:

```
┌─────────────────────────────┐
│  Human Review               │  ← Final approval
├─────────────────────────────┤
│  E2E Tests                  │  ← User journey validation
├─────────────────────────────┤
│  Integration Tests          │  ← Component interaction
├─────────────────────────────┤
│  Unit Tests + Mutation      │  ← Logic correctness
├─────────────────────────────┤
│  Static Analysis + Types    │  ← Structural correctness
├─────────────────────────────┤
│  Lint + Format              │  ← Style consistency
└─────────────────────────────┘
```

### Pre-Commit Hooks

Minimum pre-commit checks for agent-generated code:
- Lint and format
- Type check
- Unit tests (fast subset)
- No secrets committed (GitGuardian, git-secrets)

### Property-Based Testing

Especially valuable for agent code -- tests properties rather than specific examples. Generates thousands of adversarial inputs per property, catching edge cases agents miss.

---

## Architecture Documentation for Agents

### Module Map

Maintain a `docs/module-map.md` that agents can read:

```markdown
# Module Dependency Map

orders → [inventory, payments, notifications]
payments → [stripe-adapter]
notifications → [email-adapter, sms-adapter]
inventory → []

## Shared Dependencies
All modules may use: shared/auth, shared/logging, shared/errors
```

### API Contracts as Source of Truth

Schema-first development gives agents unambiguous contracts:
- OpenAPI specs for REST endpoints
- Protobuf definitions for gRPC
- GraphQL schema files
- AsyncAPI for event contracts

Agents code against these schemas, reducing hallucination of API shapes.

### Agent Decision Records (AgDR)

Extension of ADRs specifically for AI-assisted decisions:
- Document which agent made the decision and under what constraints
- Include the prompt/context that led to the decision
- Flag for human review with specific questions

---

## MCP (Model Context Protocol) Integration

### Architecture Patterns

1. **Facade:** MCP client hides external complexity behind unified protocol
2. **Adapter:** Each MCP server translates standardized interface to specific backend
3. **Sidecar:** Each integration runs as isolated, independent process

### Design Rules

- Each MCP server should have one clear, well-defined purpose
- Core primitives: tools, resources, and prompts
- Use adapter pattern for integrating external SaaS APIs
- Keep servers stateless when possible

---

## Human-in-the-Loop Modes

| Mode | Agent Autonomy | Human Role |
|------|----------------|------------|
| **AUTO** | Executes and commits | Reviews post-hoc |
| **HITL** | Executes, awaits approval | Approves each step |
| **MANUAL** | Suggests, human executes | Full control |

The trajectory is from HITL to Human-on-the-Loop: agents run autonomously while humans monitor via dashboards and intervene only for exceptions. Start with HITL for critical paths, relax to AUTO as trust builds.
