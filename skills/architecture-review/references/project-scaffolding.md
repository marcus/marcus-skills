# Project Scaffolding

Day-one setup checklist and canonical directory structure for new projects.

## Canonical Directory Structure

```
project-root/
├── .github/
│   ├── CODEOWNERS
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── deploy.yml
│   └── pull_request_template.md
├── .claude/
│   └── skills/                     # Project-specific agent skills
├── docs/
│   ├── adr/
│   │   └── ADR-0001-architecture-style.md
│   └── module-map.md
├── infrastructure/
│   ├── terraform/                  # Or pulumi/
│   └── docker/
│       ├── Dockerfile
│       └── docker-compose.yml
├── src/
│   ├── modules/
│   │   └── [feature]/
│   │       ├── domain/
│   │       ├── application/
│   │       ├── infrastructure/
│   │       ├── api/
│   │       └── __tests__/
│   ├── shared/
│   │   ├── auth/
│   │   ├── logging/
│   │   └── errors/
│   ├── config/
│   └── main.ts                     # Composition root
├── tests/
│   ├── integration/
│   └── e2e/
├── scripts/
│   └── setup.sh
├── .env.example
├── .gitignore
├── CLAUDE.md
├── CONTRIBUTING.md
├── package.json                    # Or go.mod, Cargo.toml, etc.
└── tsconfig.json                   # If TypeScript
```

---

## Day-One Checklist

### Week 1: Foundations

- [ ] Initialize repository with .gitignore, .env.example
- [ ] Write CLAUDE.md with tech stack, commands, conventions, and boundaries
- [ ] Create first ADR documenting architecture style decision
- [ ] Set up linting and static analysis
- [ ] Write first integration test with containerized dependencies
- [ ] Create database migration tooling and first migration
- [ ] Configure structured JSON logging with correlation IDs
- [ ] Add health check endpoints (liveness + readiness)
- [ ] Create CODEOWNERS file
- [ ] Pin dependencies with lockfiles, enable Renovate/Dependabot
- [ ] Create Dockerfile and docker-compose.yml
- [ ] Set up feature flag system (even a simple config-based one)

### Week 2: Quality Gates

- [ ] Set up CI pipeline: lint → test → build → security scan
- [ ] Add code quality scanning (SonarQube/SonarCloud)
- [ ] Define SLIs and initial SLOs (availability, latency p95, error rate)
- [ ] Implement audit logging for auth events and data mutations
- [ ] Define data classification tiers and label database columns
- [ ] Generate SBOM in CI, configure license allowlist
- [ ] Set up OpenTelemetry instrumentation
- [ ] Create module-map.md documenting module dependencies
- [ ] Define API contracts (OpenAPI/AsyncAPI) before implementation

### Week 3: Resilience

- [ ] Add retry with exponential backoff + jitter for external calls
- [ ] Implement circuit breakers for critical downstream dependencies
- [ ] Set up caching layer with explicit TTLs
- [ ] Write performance baseline tests (k6 smoke tests in CI)
- [ ] Implement graceful degradation for at least one non-critical feature
- [ ] Set up pre-commit hooks (lint, type check, fast tests, secret scan)

### Week 4: Maturity

- [ ] Add contract tests for inter-service APIs (if applicable)
- [ ] Set up E2E tests for top 3-5 critical user journeys (Playwright)
- [ ] Configure synthetic test data generation
- [ ] Schedule first chaos engineering game day
- [ ] Review and document compliance requirements (GDPR, SOC 2, etc.)
- [ ] Set up Git worktree scripts for parallel agent work
- [ ] Create project-specific agent skills for common tasks

---

## Configuration Management (12-Factor)

| Principle | Implementation |
|-----------|---------------|
| Config in env vars | `.env.example` (committed) + `.env` (gitignored) + secrets manager |
| One codebase, many deploys | Same artifact for dev/staging/prod; only config differs |
| Backing services as resources | DB, cache, queue as swappable URLs |
| Strict build/release/run | CI builds once, promotes through environments |
| Port binding | Self-contained process that binds to a port |
| Stateless processes | No sticky sessions; state in external stores |

---

## Technology Selection Criteria

When choosing technologies, evaluate against:

1. **Team capability** -- can the team support this long-term?
2. **Community and ecosystem** -- active maintenance, good documentation, package ecosystem?
3. **Operational complexity** -- what is the run cost in people and infrastructure?
4. **Agent compatibility** -- well-documented APIs, strong typing, good error messages?
5. **Lock-in risk** -- can you migrate away if needed? Open standards preferred.
6. **License** -- compatible with your project's licensing model?

### Technology Radar Categories

Maintain a project or org technology radar:

| Category | Meaning |
|----------|---------|
| **Adopt** | Proven, recommended for new projects |
| **Trial** | Worth using in low-risk contexts to build experience |
| **Assess** | Explore with prototypes, not production |
| **Hold** | Do not start new work with this; migrate existing usage |

---

## Monorepo vs Polyrepo

| Choose Monorepo When | Choose Polyrepo When |
|---------------------|---------------------|
| Team < 50 engineers | Large autonomous teams |
| Significant shared code | Different lifecycles and tech stacks |
| Frequent cross-boundary changes | Strict access isolation needed |
| Want single CI/CD pipeline | Independent deployment required |
| AI agents need full system context | Separate org ownership |

**Monorepo tooling:** Nx (most mature), Turborepo (fast, Vercel-backed), Bazel (Google-scale), moon (Rust-based, emerging).

---

## Environment Strategy

```
Local Dev    → .env file + Docker Compose + Dev Container
CI           → Ephemeral containers, env vars from CI secrets
Staging      → Mirrors production config, secrets from Vault
Production   → Secrets from Vault/AWS SM, config from ConfigMap/env
```

Every environment should be reproducible from code and configuration -- no manual setup steps that exist only in someone's head.
