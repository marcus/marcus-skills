---
name: surface-parity
description: Design, implement, refactor, and review software that exposes owned capabilities across human interfaces, agent interfaces, and APIs without duplicating business logic or allowing surfaces to drift. Use when choosing or evolving UI, TUI, native, CLI, API, or MCP surfaces; adding a feature to a multi-surface product; preparing a clean future API boundary; reviewing surface-only behavior; or designing parity and contract tests. Keep selected surfaces semantically aligned through one shared application core while allowing each surface appropriate ergonomics and transport behavior.
---

# Surface Parity

Design one product with several deliberate interfaces, not several products that happen to share storage. Give humans, agents, and integrations access to the capabilities the product owns while keeping domain behavior in one shared core.

Use this skill alongside `pragmatic-engineering`. Surface parity does not justify adding surfaces or abstractions without a real or credible journey.

## Begin With Capabilities and Journeys

Model the behavior before mapping it to interfaces.

1. Identify the capability the product owns.
2. Identify who needs it: an end user, an agent, another program, or some combination.
3. Describe the outcome and refusal rules independently of buttons, flags, tool calls, or HTTP.
4. Choose only the surfaces needed for credible journeys.
5. Define deliberate parity exceptions before implementation.

Ask questions in terms of use:

> Should an agent be able to approve the same proposal a person approves in the TUI, or is approval intentionally reserved for a person?

Then explain the implementation consequence. Do not begin with “Which endpoints and commands should exist?” before the behavior is clear.

## Choose Surfaces Deliberately

Treat these as common roles, not a mandatory checklist:

| Role | Typical surface | Default guidance |
| --- | --- | --- |
| Human experience | Web or native UI, or TUI for developer tools | Optimize presentation, exploration, and interactive workflows. |
| Agent experience | Scriptable CLI with structured output | Provide a deterministic, non-interactive path by default. |
| Programmatic integration | HTTP or local API | Add when a service, remote consumer, separate process, or custom client needs it. |
| Tool-shaped agent integration | MCP | Add when typed tool discovery or conversational composition materially improves on the CLI or API. |

Do not add an API or MCP server solely to complete the table. Do not omit a non-interactive path for an owned capability merely because the UI shipped first.

### Apply the ownership test

If uninstalling the product would remove the capability, the product owes agents a deterministic way to invoke it. If the product only presents a capability owned by an underlying tool, parity may add ceremony rather than access.

A task manager owns task validation and mutation, so its UI actions need an agent path. A file browser does not need to wrap `mv` merely because its UI can move a file. If a presentation layer develops rules of its own, keep those rules state-free or behind a reusable boundary so a headless caller can adopt them later.

## Define Semantic Parity

Require selected surfaces to agree on domain meaning, not on interaction mechanics.

Keep these consistent unless an exception is intentional:

- available owned capabilities;
- validation and authorization rules;
- state transitions and side effects;
- identifiers and concurrency expectations;
- refusal reasons and domain outcomes;
- data visibility and privacy boundaries.

Allow surfaces to differ where their users need different affordances:

- a UI may use selection, confirmation, optimistic feedback, and rich presentation;
- a CLI may accept convenient references and emit human text or JSON;
- an API may require stable IDs, explicit revisions, status codes, and wire representations;
- MCP may expose a smaller set of task-shaped tools with typed schemas.

Translate one shared outcome into each surface's language. Do not reimplement the rule in each adapter.

## Keep One Application Boundary

Put commands, queries, validation, policy, and domain outcomes in a transport-neutral application or core layer. Keep persistence behind its own narrow boundary. Prevent surface code from reaching around the application layer for privileged reads or writes.

Use either of these simple shapes according to the runtime:

```text
CLI ─┐
TUI ─┼─> application core ─> store
API ─┘
```

```text
CLI ─┐
UI  ─┼─> API adapter ─> application core ─> store
MCP ─┘
```

The first fits an embedded or local application. The second fits a service-backed application where the API already defines the process boundary. Both preserve one behavioral core.

Thin adapters may own:

- input parsing and friendly reference resolution;
- authentication transport and request limits;
- terminal, graphical, JSON, or protocol rendering;
- status or exit-code mapping;
- surface-specific confirmation and discoverability.

Thin adapters must not own domain validation, mutation ordering, permissions policy, or a private representation of product state.

## Prepare for an API Without Building One

APIs are often added after the first useful UI or CLI. Make that future change additive, but do not pre-build HTTP infrastructure.

From the start:

- route surface actions through a named application boundary rather than directly through widgets, command handlers, or storage;
- accept typed commands or plain domain inputs and return explicit outcomes;
- keep HTTP, terminal, framework, environment, and driver types out of the core;
- give addressable entities identifiers that remain meaningful across processes when the product already needs durable identity;
- centralize validation, authorization policy, and transaction boundaries;
- make current callers consume the same public application behavior a future adapter would use.

Defer until an API journey exists:

- routes and wire schemas;
- OpenAPI documents;
- HTTP servers and middleware;
- remote authentication and tenancy;
- pagination, rate limits, versioning, and deployment topology;
- generalized DTO layers with no present consumer.

Use this test: adding the first API should mostly require a transport adapter plus genuine remote-boundary concerns. If it requires extracting business rules from the UI or CLI, the current boundary is too weak. If the project already contains unused endpoint abstractions, request objects, and versioning machinery, it went too far.

## Add or Change a Capability

For each feature:

1. Define the user and agent outcomes.
2. Decide which existing surfaces should expose it and document any exception.
3. Implement the behavior once at the application boundary.
4. Map the outcome into each selected adapter.
5. Update discoverability: UI affordances, `--help`, structured CLI schema, API contract, or MCP tool description as applicable.
6. Prove the real journey on each selected surface.
7. Add focused parity coverage at the shared boundary and adapter edges.

Do not force every surface into the first implementation commit when a steel thread through one surface is the fastest way to validate the behavior. Do make the shared core surface-neutral and complete the agreed parity before calling the capability finished.

## Track Parity Lightly

For a product with several surfaces, maintain a compact capability matrix in an existing spec or architecture document:

| Capability | Human | CLI | API | MCP | Notes |
| --- | --- | --- | --- | --- | --- |
| Create item | TUI | `item create` | `POST /items` | — | MCP not justified |
| Approve item | TUI | `item approve` | `POST /items/{id}/approval` | `approve_item` | Same domain refusal rules |

Record intentional omissions instead of allowing silent drift. Keep the matrix about owned behavior; do not inventory presentation details or generate documentation no one will maintain.

## Test Contracts, Not Duplicated Implementations

- Test domain behavior once through the application boundary.
- Run adapter contract tests for parsing and outcome mapping.
- Add a small cross-surface suite for high-risk mutations, authorization, refusals, and structured representations.
- Boot real entry points when process wiring, dependency isolation, or transport behavior matters.
- Verify JSON, API, or MCP shapes from their authoritative contracts.
- Avoid repeating every domain test through every surface.

Treat a parity failure as an architecture signal. If one change requires duplicating rules or fixtures across surfaces, move the behavior inward before adding more tests around the duplication.

## Review for Drift

Flag these patterns:

- a button or screen performs an owned capability unavailable to agents;
- CLI and API handlers write storage directly in different ways;
- the UI validates or authorizes behavior the core accepts differently;
- one surface invents its own status, sorting, or state-transition vocabulary;
- the CLI lacks structured output or requires a keypress;
- API preparation introduces unused transport abstractions;
- MCP mirrors every low-level command without improving agent use;
- presentation-only behavior is mistaken for an owned capability.

When reporting drift, lead with the inconsistent experience, recommend the shared behavior, and then identify the boundary or adapter change needed.

## Completion Check

Before completing multi-surface work, verify:

- the product's owned capability is defined independently of presentation;
- every selected surface reaches the same application behavior;
- surface differences are deliberate and user-appropriate;
- agents have a deterministic, discoverable, structured path for each owned capability unless an intentional exception is documented;
- a future API can attach to a real boundary without current API theater;
- parity tests cover meaningful contracts without multiplying the whole suite;
- documentation names supported surfaces and intentional exceptions.
