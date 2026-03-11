# DevOps and Quality Architecture

## CI/CD Pipeline Architecture

Define pipelines as code from day one.

### Standard Pipeline Stages

```
Commit → Lint → Test → Build → Security Scan → Container Build → Deploy Staging → Integration Tests → Promote to Production
```

| Stage | Tools | Purpose |
|-------|-------|---------|
| Lint | ESLint, Ruff, golangci-lint | Code style and basic errors |
| Static analysis | TypeScript, mypy, SonarQube | Type safety, complexity, duplication |
| Unit/integration tests | Jest, pytest, go test | Functional correctness |
| Security scan (SAST) | Semgrep, CodeQL | Vulnerability patterns in code |
| Dependency scan | Snyk, Trivy, Dependabot | CVEs in dependencies |
| Container scan | Trivy, Grype | CVEs in container images |
| SBOM generation | Syft | Software bill of materials |
| License check | FOSSA, license-checker | Dependency license compliance |

### Container Best Practices

- Dockerfile + docker-compose from day one
- Multi-stage builds to keep production images minimal
- Distroless base images to minimize attack surface
- Pin all dependency versions for deterministic builds
- Dev Containers for reproducible development environments

---

## Observability Stack

**OpenTelemetry is the standard.** Instrument from day one -- retrofitting is painful.

### Three Pillars

| Pillar | Tool | Setup |
|--------|------|-------|
| **Logs** | Structured JSON (Loki, CloudWatch) | Correlation IDs from first commit |
| **Metrics** | Prometheus/Mimir, Datadog | RED metrics (Rate, Errors, Duration) |
| **Traces** | Tempo, Jaeger, Datadog APM | OpenTelemetry auto-instrumentation |

### Structured Logging Rules

```json
{
  "timestamp": "2026-03-10T14:30:00Z",
  "level": "info",
  "message": "Order created",
  "correlation_id": "abc-123",
  "service": "orders",
  "user_id": "usr_456",
  "order_id": "ord_789",
  "duration_ms": 42
}
```

- Always JSON format
- Always include correlation/request ID
- Never log PII or secrets
- Use consistent field names across all services

### SLO/SLI/SLA

Define from the start, not after the first outage.

| Concept | Who Sets | Example |
|---------|----------|---------|
| **SLI** (Indicator) | Engineering | Success rate = successful / total requests |
| **SLO** (Objective) | Engineering + Product | 99.9% success rate, p95 < 200ms (30-day rolling) |
| **SLA** (Agreement) | Business + Legal | 99.5% uptime/month with credits below threshold |

**Error budget:** `budget = 1 - SLO`. Track burn rate to balance velocity with reliability.

---

## Testing Strategy

### Testing Shape by Architecture

| Architecture | Recommended Shape | Emphasis |
|--------------|-------------------|----------|
| Libraries, pure logic | **Pyramid** | Heavy unit tests |
| Web apps, API services | **Trophy** | Heavy integration tests |
| Microservices | **Diamond** | Equal unit + integration |
| Service-oriented | **Honeycomb** | Integration-heavy |

### Test Categories

| Category | Purpose | Run When | Time Budget |
|----------|---------|----------|-------------|
| Static analysis | Type errors, lint | Every commit | < 30s |
| Unit tests | Business logic | Every commit | < 2 min |
| Integration tests | DB, APIs, messages | Every commit | < 5 min |
| Contract tests | Inter-service APIs | Every commit | < 2 min |
| E2E tests | Critical user journeys | Every merge to main | < 10 min |
| Performance baseline | Latency regressions | Weekly / pre-release | < 5 min |
| Security scan | Vulnerabilities | Every commit | < 3 min |

### Contract Testing

Verify service communication without full integration environments.

- **Pact** -- consumer-driven contracts, mature ecosystem
- **Specmatic** -- schema-first from OpenAPI/AsyncAPI specs
- Run `can-i-deploy` checks in CI before any deployment

### Performance Baseline

Establish before you have problems:

1. Write smoke load tests in CI (k6 with 5-10 virtual users, 30-second duration)
2. Baseline p50, p95, p99 for critical endpoints
3. Alert when baselines regress beyond threshold
4. Stress tests before major releases

### Chaos Engineering Readiness

You don't run chaos experiments on day one -- you prepare for them:

1. Define steady-state hypotheses (error rate < 0.1%, p99 < 500ms)
2. Instrument observability first
3. Implement graceful degradation patterns
4. Start experiments in staging
5. Schedule game days

---

## Resilience Patterns

### Circuit Breakers

Prevent cascading failures. Three states: Closed (normal), Open (rejecting), Half-Open (testing).

- Configure failure rate thresholds (50% over 10 calls)
- Provide fallback responses when open (cached data, defaults, degraded features)
- Libraries: Resilience4j (JVM), Polly (.NET), opossum (Node.js), gobreaker (Go)

### Retry with Backoff

- Always exponential backoff with jitter: `delay = min(base * 2^attempt + jitter, max_delay)`
- Max 3-5 retries
- Only retry transient failures (5xx, timeouts) -- never 4xx
- Make operations idempotent before adding retries
- Set retry budgets (no more than 10% of requests should be retries)

### Health Checks

Three distinct probes:

| Probe | Endpoint | Checks | On Failure |
|-------|----------|--------|------------|
| Liveness | `/healthz/live` | Process alive, not deadlocked | Restart container |
| Readiness | `/healthz/ready` | Dependencies available | Remove from load balancer |
| Startup | `/healthz/startup` | Bootstrap complete | Delay other probes |

### Graceful Degradation

- Feature flags to disable non-critical features under load
- Serve stale cache when backend unavailable
- Queue shedding for low-priority work
- Read-only mode when writes fail
- Static fallback for dynamic pages

---

## Code Quality Infrastructure

### Dependency Management

1. Pin exact versions in lockfiles -- always commit lockfiles
2. Automate updates: Renovate (more configurable) or Dependabot
3. Batch minor/patch weekly; review majors individually
4. Fail builds on critical CVEs

### Technical Debt Tracking

- SonarQube/SonarCloud in CI for code quality metrics
- Allocate 15-20% of sprint capacity to debt reduction
- Tag debt issues with `tech-debt` label and severity
- Quarterly debt reviews
- Never track debt only in code comments without tracked issues

### CODEOWNERS

```
# .github/CODEOWNERS
*                     @team-leads
/src/auth/            @auth-team
/src/billing/         @payments-team
/infrastructure/      @platform-team
*.proto               @api-team
```

Require CODEOWNERS review on PRs to protected branches. Update quarterly.

### Infrastructure as Code

- Terraform/OpenTofu or Pulumi for cloud provisioning
- Same repo (or dedicated `infra/` repo) with same review process as app code
- GitOps with Argo CD or Flux for Kubernetes reconciliation
- Git is the single source of truth for infrastructure state
