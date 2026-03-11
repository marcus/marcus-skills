---
name: architecture-review
description: "Conduct architectural reviews for new or existing software projects. Use when: (1) starting a new project and need architectural foundations, (2) reviewing architecture decisions before implementation, (3) creating ADRs or design docs, (4) evaluating technology selections, (5) assessing non-functional requirements, (6) setting up project scaffolding with built-in quality. Combines enterprise ARB governance with modern agentic coding patterns."
---

# Architecture Review

Conduct rigorous architectural reviews that blend enterprise governance with modern, agent-friendly development patterns. Produce decisions that are documented, defensible, and immediately actionable.

## Core Philosophy

**Make decisions explicit.** Every significant choice becomes an ADR.
**Guardrails over gates.** Provide golden paths and reference architectures, not bureaucratic approval queues.
**Agent-native from day one.** Structure projects so AI agents can understand, modify, and extend them reliably.
**Start right, stay lean.** Enterprise-grade foundations without enterprise-grade overhead.

---

## Quick Start: New Project Review

When starting a new project, run through these phases in order:

### Phase 1: Strategic Alignment (5 min)

Answer these before touching code:

1. **What problem does this solve?** One sentence.
2. **Who are the users?** Primary persona + scale expectations.
3. **What are the constraints?** Budget, timeline, team size, compliance requirements.
4. **What exists already?** Existing services, data stores, or platforms to integrate with.
5. **What is the deployment target?** Cloud provider, on-prem, edge, hybrid.

### Phase 2: Architecture Decision Cascade

Work through these decisions in order. Each produces an ADR.

| # | Decision | Reference |
|---|----------|-----------|
| 1 | Architecture style | [architecture-patterns.md](references/architecture-patterns.md) |
| 2 | Module/service boundaries | [architecture-patterns.md](references/architecture-patterns.md) |
| 3 | API strategy | [api-and-data.md](references/api-and-data.md) |
| 4 | Data architecture | [api-and-data.md](references/api-and-data.md) |
| 5 | Security posture | [security-and-compliance.md](references/security-and-compliance.md) |
| 6 | Observability stack | [devops-and-quality.md](references/devops-and-quality.md) |
| 7 | Testing strategy | [devops-and-quality.md](references/devops-and-quality.md) |
| 8 | CI/CD and deployment | [devops-and-quality.md](references/devops-and-quality.md) |
| 9 | Agent workflow setup | [agentic-patterns.md](references/agentic-patterns.md) |

### Phase 3: Scaffold and Ship

After decisions are made, generate the project structure. See [project-scaffolding.md](references/project-scaffolding.md) for the canonical directory layout and day-one checklist.

---

## Architecture Decision Record Template

Every significant decision gets an ADR. Store in `docs/adr/` with sequential numbering.

```markdown
# ADR-NNNN: [Short Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Context
What forces are at play? What is the problem?

## Decision Drivers
- Key factor 1
- Key factor 2

## Considered Options
1. **Option A** -- pros / cons
2. **Option B** -- pros / cons

## Decision
What we chose and why.

## Consequences
What becomes easier. What becomes harder. What risks remain.
```

**Rules:**
- One decision per ADR. Never combine.
- Immutable once accepted -- supersede, don't edit.
- Keep under 2 pages. Alternatives considered is the most valuable section.
- Link related ADRs to create a decision graph.

---

## Quality Attributes Checklist

Evaluate every architecture against these attributes. Score each as: Addressed / Planned / Not Applicable / Risk.

| Attribute | Key Questions |
|-----------|---------------|
| **Scalability** | Can it handle 10x load? Horizontal or vertical strategy? |
| **Security** | Auth/authz defined? Data encrypted at rest and in transit? Threat model done? |
| **Reliability** | Target uptime? Redundancy and failover? |
| **Performance** | Latency budgets? Throughput targets? |
| **Maintainability** | Modular? Clear boundaries? Can a new developer (or agent) be productive in a day? |
| **Observability** | Structured logging? Distributed tracing? Alerting? |
| **Testability** | Can components be tested in isolation? What is the test strategy shape? |
| **Deployability** | CI/CD automated? Blue-green/canary capability? Rollback plan? |
| **Cost efficiency** | Resource utilization optimized? Pay-per-use aligned? |
| **Agent compatibility** | Can AI agents understand, modify, and extend this codebase? |

---

## Anti-Patterns to Flag

Reject architectures exhibiting these patterns:

| Anti-Pattern | Signal |
|--------------|--------|
| **Big Ball of Mud** | No clear module boundaries, circular dependencies |
| **Over-Engineering** | Google-scale infra for startup workloads |
| **Blind Pattern Following** | "We chose microservices because Netflix" without justification |
| **Infrastructure Ignorance** | Designs assuming unlimited bandwidth or zero latency |
| **Under-Modularization** | Monolithic components that can't deploy independently |
| **Over-Modularization** | Hundreds of nano-services creating operational overhead |
| **Document Theater** | Extensive paperwork that nobody reads or acts on |
| **Domain Allergy** | Architecture that ignores business domain and language |

---

## Review Outcomes

Every review produces one of these decisions:

| Decision | Meaning |
|----------|---------|
| **Approved** | Proceed as designed |
| **Approved with conditions** | Proceed with specific modifications |
| **Needs more info** | Specific questions must be answered first |
| **Redesign required** | Does not meet quality standards |

---

## Reference Materials

- [Architecture Patterns](references/architecture-patterns.md) -- Hexagonal, DDD, modular monolith, microservices decision framework
- [API and Data Architecture](references/api-and-data.md) -- REST/GraphQL/gRPC, database selection, caching, event streaming
- [Security and Compliance](references/security-and-compliance.md) -- Zero trust, OWASP, auth patterns, supply chain, compliance
- [DevOps and Quality](references/devops-and-quality.md) -- CI/CD, observability, testing strategies, resilience patterns
- [Agentic Patterns](references/agentic-patterns.md) -- Agent-native project structure, CLAUDE.md, parallel work, quality gates
- [Project Scaffolding](references/project-scaffolding.md) -- Day-one directory structure, checklist, and timeline
