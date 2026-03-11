# API and Data Architecture

## API Strategy

### API-First Development

Design the API contract BEFORE writing implementation code.

**Benefits:**
- Frontend and backend teams work in parallel against the contract
- Auto-generate SDKs, documentation, and mock servers
- Reduces integration surprises
- Teams report ~60% faster onboarding and ~25% fewer production incidents

### Contract-First Tools

| Protocol | Contract Format | Tools |
|----------|----------------|-------|
| REST | OpenAPI 3.1 | Stoplight, Redocly, openapi-generator |
| Event-driven | AsyncAPI | AsyncAPI Studio, generator |
| gRPC | Protobuf `.proto` files | buf, grpc-gateway |
| GraphQL | `.graphql` schema files | Apollo, graphql-codegen |

### Protocol Decision Matrix

| Criterion | REST | GraphQL | gRPC |
|-----------|------|---------|------|
| **Best for** | Public APIs, CRUD, caching | Flexible client queries, BFF | Internal service-to-service |
| **Performance** | Good (HTTP caching) | Variable (N+1 risk) | Excellent (binary, HTTP/2) |
| **Schema** | OpenAPI 3.1 | SDL (strongly typed) | Protobuf (strongly typed) |
| **Client flexibility** | Low (fixed responses) | High (client picks fields) | Low (fixed messages) |
| **Streaming** | Limited (SSE, WebSocket) | Subscriptions | Native bidirectional |
| **Learning curve** | Low | Medium | Medium-High |

**Default recommendation:** REST with OpenAPI for public APIs. gRPC for internal high-throughput service communication. GraphQL only when clients genuinely need flexible querying (mobile apps with varying data needs, BFF layer).

### Versioning Strategy

- **URL path versioning** (`/v1/resources`) -- simplest, most explicit, good default
- For internal APIs, prefer additive non-breaking changes and avoid versioning entirely when possible
- Never remove or rename fields -- deprecate and add new ones

---

## Database Selection

### Decision Framework

| Criterion | SQL (Postgres) | NoSQL (MongoDB, DynamoDB) | NewSQL (CockroachDB) |
|-----------|---------------|--------------------------|---------------------|
| Relationships | Complex joins, foreign keys | Denormalized, embedded | SQL joins with horizontal scale |
| Consistency | ACID transactions | Eventual (tunable) | ACID with distribution |
| Scale | Vertical first, read replicas | Horizontal from start | Horizontal with SQL |
| Schema | Migrations required | Schema-flexible | Migrations required |
| Best for | Most apps, financial, ERP | IoT, CMS, flexible schemas | Global SaaS, fintech at scale |

**Default recommendation:** Start with PostgreSQL. It handles JSON (NoSQL flexibility), full-text search, geospatial data, and scales vertically to significant workloads. Add specialized databases only when you have measured needs.

### Data Modeling Rules

- Start normalized (3NF) for transactional data
- Denormalize only for read-heavy paths with measured performance needs
- Never share database tables across bounded contexts
- Separate read models from write models when patterns diverge

### Migration Strategy

Treat database schema as code from the first commit.

1. Use a migration tool from the start (Flyway, golang-migrate, Alembic, Prisma, Drizzle Kit)
2. Every change is a versioned, reviewable migration file in version control
3. Migrations must be idempotent and reversible where possible
4. CI runs migrations against a fresh database on every build
5. Use expand-and-contract for breaking changes
6. Never modify a migration that has been applied to any shared environment

---

## Caching Architecture

### Layer Your Caches

| Layer | Tool | Use Case |
|-------|------|----------|
| CDN | Cloudflare, CloudFront | Static assets, public API responses |
| Application | Redis, Valkey, Dragonfly | Sessions, computed results, rate limiting |
| Query | Materialized views | Expensive aggregations, reporting |
| Browser | Cache-Control headers | Static resources |

**Rules:**
- Set explicit TTLs on every cache key -- never cache without expiration
- Use cache-aside (lazy loading) as the default pattern
- Plan cache invalidation from day one (event-driven invalidation preferred)
- Monitor cache hit rates -- below 80% means your caching strategy needs work

---

## Event Streaming

### Decision Framework

| Factor | Kafka | NATS | RabbitMQ | SQS/Pub-Sub |
|--------|-------|------|----------|-------------|
| Throughput | Highest | High | Moderate | Moderate |
| Ops complexity | High | Low | Moderate | None (managed) |
| Durability | Strong (log) | JetStream | Durable queues | Built-in |
| Best for | Data pipelines, event sourcing | Microservice messaging, IoT | Task queues, RPC | Simple async processing |

**Default recommendation:** Start with a managed queue (SQS, Cloud Pub/Sub, or NATS). Kafka is justified only when you need durable event logs, replay, or very high throughput. Use managed Kafka (Confluent Cloud, MSK, Redpanda) if you do choose it.

### Event Schema Rules

- Use a schema registry from day one (Confluent Schema Registry with Avro/Protobuf)
- Version all event schemas
- Ensure backward and forward compatibility
- Events should be self-describing (include type, version, timestamp, correlation ID)
