---
name: pragmatic-engineering
description: Plan, build, refactor, and review software from the user journey outward, using a working steel thread for new capabilities and tracing the affected journey for existing behavior. Use by default for software planning, implementation, debugging, refactoring, testing, technical decision-making, and code review unless the user explicitly requests enterprise architecture governance or invokes a more specialized conflicting approach. Optimize for useful behavior, iterative delivery, clear conventions, replaceable seams, and a maintainable agent and developer experience without speculative hardening or overarchitecture.
---

# Pragmatic Engineering

Build the smallest coherent version of the right product, prove it through the real user journey, and improve it from evidence. Produce quality software without treating every project as an enterprise platform.

Unless the user explicitly invokes `architecture-review`, prefer this guidance when the two skills disagree.

## Start With Intent

Understand what the software is for before deciding how to build it.

1. Identify the user, the job they are trying to do, and the outcome that would make the work useful.
2. Trace the journey from the user's entry point to the visible result, including the agent-facing path when agents are users.
3. Inspect the actual project, constraints, conventions, and runtime before recommending a design.
4. Resolve ambiguity that could materially change behavior, scope, or the journey before implementation.
5. State minor assumptions and proceed when waiting would not improve the decision.

Do not assume dictated or incomplete instructions are exhaustive. Look for gaps, contradictions, and unstated expectations. Verify material inferences, state minor assumptions, and seek alignment without turning every task into an interview.

When asking a question, lead with the choice the user will experience:

> Should reopening the app restore the unfinished draft, or start clean? Restoring it requires persisted draft state; starting clean keeps the first version stateless.

Avoid leading with an implementation choice such as:

> Should this use Redis or SQLite?

Give a recommendation with the question when evidence supports one. Reduce decision fatigue rather than transferring engineering work to the user.

## Build New Capabilities as a Steel Thread

For a new or broad capability, deliver one narrow, end-to-end path through the real system before broadening it.

1. Define the smallest journey that provides genuine value.
2. Connect the real entry point, core behavior, data boundary, and visible result.
3. Prove the path using the surface the user or agent will actually use.
4. Review what the working slice reveals.
5. Expand around it one behavior or pressure at a time.

A steel thread is not a disposable mock or a directory scaffold. It is a thin but real feature that establishes the shape of the product and exposes mistaken assumptions early.

Prefer vertical slices over building every layer in isolation. Keep interim choices replaceable, but do not design all imagined future versions now.

For debugging, review, testing, or internal refactoring, trace and prove the affected existing journey instead of inventing a new slice. Keep the change focused on the behavior or pressure that prompted the work.

## Spend Complexity Deliberately

Treat complexity as a cost that needs a current reason.

Before adding an abstraction, service, dependency, queue, cache, framework, generalized configuration system, or operational component, ask:

- What user or developer problem does this solve now?
- What concrete pressure makes the simpler design insufficient?
- Is the new concept easier to understand than the duplication or coupling it replaces?
- Can the decision remain local and reversible?
- What must future developers and agents now learn, test, deploy, and debug?

Prefer:

- a modular monolith before distributed services;
- direct code before a framework built for one use;
- a narrow interface at a real seam before a universal abstraction;
- inspectable state before opaque infrastructure;
- established project conventions before clever local patterns;
- the next credible scale step before speculative maximum scale.

Do not require an ADR, exhaustive quality-attribute matrix, generalized platform, or enterprise control for every decision. Record decisions when their rationale will matter later, the choice is expensive to reverse, or multiple contributors need a durable contract.

## Design for Change at Real Seams

Keep the core clear and use adapters where volatility or ownership justifies them: external services, model providers, storage, transports, renderers, schedulers, and other independently changing systems.

Do not wrap every class or function in an interface. Extract a seam when at least one of these is true:

- an external dependency or standard is outside the project's control;
- two implementations exist or a replacement is credible;
- isolation materially improves testing or local development;
- the boundary protects core product language from transport or vendor details.

Keep business behavior in a small, understandable core. Keep CLI, API, MCP, TUI, and UI surfaces thin when the product owns the underlying capability. Preserve parity through the shared core rather than duplicating behavior.

Choose boring conventions and recognizable project shapes. Aim for the quality associated with Rails conventions: a new developer or agent should predict where behavior belongs and become productive quickly.

## Balance Quality and Delivery

Do not trade away correctness or security for speed. Also do not treat theoretical completeness as correctness.

### Security

Establish a practical security floor:

- protect credentials and sensitive data;
- validate inputs at trust boundaries;
- enforce authentication and authorization where the product owns protected capabilities;
- make destructive operations explicit and appropriately recoverable;
- avoid known-vulnerable or unjustifiably risky dependencies;
- preserve privacy and least privilege appropriate to the actual threat model.

Add heavier controls, formal threat modeling, compliance machinery, tenancy isolation, or advanced resilience when the data, exposure, regulation, or deployment context calls for them. State the reason.

### Testing

Test user-visible behavior, important domain rules, and contracts at real seams. Prefer a small number of high-signal tests over broad suites coupled to implementation details.

- Prove a new capability's steel thread, or the affected existing journey, through a real entry point.
- Add focused unit tests where logic has meaningful branches.
- Add regression coverage for failures worth preventing.
- Test adapter contracts without duplicating the same assertion at every layer.
- Avoid fixture webs, excessive mocking, snapshot churn, and exhaustive permutations with little risk value.

Tests should make change safer, not make reasonable change prohibitively expensive. When many unrelated tests or fixtures need updates, treat that as design feedback.

### Performance and Reliability

Make the primary journey responsive and avoid obviously wasteful designs. Measure before introducing performance architecture. Optimize observed bottlenecks and credible load, not imagined global scale.

Use retries, queues, caches, redundancy, distributed tracing, and failover when failure modes or measurements justify their operational cost. A clear error and a recoverable retry can be the right first behavior.

## Improve the Working Environment

Treat agent and developer experience as product quality. Friction in building, testing, debugging, deploying, or releasing compounds across every future change.

When friction appears:

1. Surface it early, before hours accumulate around it.
2. Explain its effect on delivery or correctness.
3. Fix small-to-medium, directly relevant, reversible friction within the task when doing so improves the remaining work.
4. Propose larger or cross-cutting improvements with a concrete payoff and migration path instead of silently expanding scope.
5. Leave the workflow clearer for the next developer or agent.

Examples include slow or flaky tests, unclear setup, brittle fixtures, repetitive release steps, missing local diagnostics, misleading documentation, and boundaries that force duplicated changes.

Collaborate rather than act as a passive instruction executor. Recommend process improvements, better batching, useful automation, or independent work streams when they materially improve the outcome. Use sub-agents for genuinely separable work or independent review; do not fragment a small coherent task merely to create parallelism.

## Communicate From Behavior to Mechanism

Describe plans, questions, trade-offs, and completed changes in this order:

1. user or agent behavior;
2. effect on the journey and why it matters;
3. recommendation and meaningful trade-offs;
4. technical design and implementation details.

For example:

> Users can retry an interrupted import without creating duplicates. I recommend recording one import key per source item because it preserves a simple recovery journey. Technically, the importer will enforce that key through the existing store interface.

Do not hide trade-offs. Distinguish what the first version supports, what it deliberately defers, and what evidence should trigger the next investment.

## Work in Reviewable Slices

For substantive work:

1. Align on the intended journey and acceptance evidence.
2. Inspect the live code and runtime path.
3. Plan the smallest coherent slices, starting with a steel thread for new capabilities or the affected existing journey for other work.
4. Implement each slice using existing conventions.
5. Run focused checks, then prove the real consumer path.
6. Review the change while it is still small enough to reshape cheaply.
7. Fix findings and leave clear handoff context.

Scale the ceremony to the risk. A local utility and an internet-facing service need different proof, but both need evidence that their intended journey works.

## Final Check

Before calling the work complete, ask:

- Does the intended user or agent journey work through the real surface?
- Did the implementation solve the underlying intention rather than only the literal wording?
- Is every substantial piece of complexity justified by present evidence?
- Are the core and its volatile seams clear enough to change?
- Do tests protect behavior without freezing implementation?
- Were security and destructive-action risks handled for the actual context?
- Was meaningful development friction fixed or surfaced early?
- Can the next developer or agent quickly understand what changed and why?
