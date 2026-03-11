# Security and Compliance Architecture

## Zero Trust Posture

Assume no implicit trust for any user, device, or network segment.

**Core principles:**
- **Verify explicitly** -- authenticate and authorize every request
- **Least-privilege access** -- grant minimum permissions required
- **Assume breach** -- design for containment and rapid response

### Authentication and Authorization

| Decision | Recommendation |
|----------|---------------|
| Identity provider | OAuth2/OIDC (Keycloak, Auth0, AWS Cognito) in front of all services |
| MFA | Enforce at first login and periodically (30 days) |
| Access tokens | Short-lived JWTs (15-minute access tokens) with refresh rotation |
| Service-to-service | mTLS or OAuth2 client credentials flow |
| Authorization | Centralize logic; avoid scattering permission checks. Use OPA for policy-as-code |

---

## OWASP Top 10 (2025) Day-One Checklist

Address proactively before launch:

- [ ] **Injection prevention** -- parameterized queries, input validation, output encoding
- [ ] **Broken authentication** -- MFA, session management, credential rotation
- [ ] **Supply chain security** -- SBOM generation, dependency scanning (elevated to #3 in 2025)
- [ ] **Security misconfiguration** -- secure defaults, no debug in production, minimal permissions
- [ ] **Cryptographic failures** -- TLS 1.3, encrypted at rest, no hardcoded secrets
- [ ] **Broken access control** -- RBAC, deny by default, test authorization boundaries
- [ ] **Vulnerable components** -- automated dependency updates, CVE scanning in CI
- [ ] **Logging and monitoring** -- security events logged, alerts on anomalies
- [ ] **SSRF prevention** -- validate and restrict outbound requests
- [ ] **Insecure design** -- threat model completed, abuse cases documented

---

## Secrets Management

**Non-negotiable rules:**
- Never hardcode secrets. Ever.
- Centralize in a secrets manager (Vault, AWS Secrets Manager, Infisical, 1Password)
- Use short-lived, auto-rotated credentials over long-lived static keys
- Avoid plain environment variables for secrets in production -- use file-based secret mounts
- Audit all secret access
- Run GitGuardian or similar in CI to detect accidentally committed secrets

### Secret Hierarchy

```
.env.example          ← Committed template (no real values)
.env                  ← Local dev only (gitignored)
Vault/Secrets Manager ← Staging and production
```

---

## Supply Chain Security

- **SBOM (Software Bill of Materials)** -- generate in CI for every build (Syft, CycloneDX format)
- **Dependency scanning** -- Dependabot, Renovate, Snyk running continuously
- **Artifact signing** -- Sigstore/cosign for container images, verify provenance
- **Pin dependency versions** -- always use lockfiles, review updates
- **License allowlist** -- MIT, Apache 2.0, BSD are safe; GPL/AGPL require legal review for proprietary products
- **Block builds** with disallowed or unknown licenses

---

## Data Classification

Establish from day one:

| Level | Label | Examples | Handling |
|-------|-------|----------|----------|
| 1 | **Public** | Marketing content, docs | No restrictions |
| 2 | **Internal** | Internal tools, configs | Access controls |
| 3 | **Confidential** | Customer data, metrics | Encryption, RBAC, audit logging |
| 4 | **Restricted** | PII, payment, health, credentials | Encryption, strict access, retention limits, log masking |

---

## Compliance Patterns

### GDPR (if handling EU user data)

- Privacy by design -- consent management, data minimization, erasure flows before launch
- Implement DSAR (Data Subject Access Request) endpoints
- Record of Processing Activities (ROPA) maintained
- Data residency -- store EU data in EU regions

### SOC 2 Preparation

- Audit logging for all access and modifications from day one
- RBAC with least-privilege defaults
- Encryption at rest and in transit
- Use compliance automation (Vanta, Drata, Secureframe) early
- Continuous evidence collection, not point-in-time

### Audit Logging Requirements

**What to log:**
- All authentication events (login, logout, failed attempts, MFA)
- All authorization decisions (granted, denied)
- All data mutations with actor, action, resource, outcome
- All administrative actions
- API access patterns

**How:**
- Structured JSON with: timestamp, actor, action, resource, outcome, IP, request ID
- Append-only store separate from application logs
- Tamper-evident (hash chains or write-once storage)
- Never log PII in plain text in general application logs
- Set retention policies from day one (SOC 2: 1 year typical)

---

## EU AI Act (enforcement begins August 2026)

If building AI features:
- High-risk AI systems require conformity assessments
- ISO 42001 (AI Management Systems) becoming the certification standard
- Document model governance, training data provenance
- SBOM requirements extending to AI model supply chains
