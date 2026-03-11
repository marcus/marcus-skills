# Architecture Patterns

## Architecture Style Decision Framework

### By Team Size

| Team Size | Recommended Style | Rationale |
|-----------|-------------------|-----------|
| 1-10 devs | Monolith or modular monolith | Microservices overhead will slow you down |
| 10-50 devs | Modular monolith with enforced boundaries | Clear modules, single deployment unit |
| 50+ devs | Microservices (justified by coordination costs) | Independent deployment cadence per team |

**Default recommendation:** Start with a modular monolith. Extract services only when a specific module has a proven, distinct scaling or deployment need. 42% of organizations that adopted microservices are consolidating back (2025 CNCF survey). Amazon Prime Video cut costs 90% moving from microservices to monolith for video analysis.

### Prerequisites for Microservices

Do NOT adopt microservices unless you have:
- 100+ engineers
- Genuine independent scaling needs per service
- Proven DevOps maturity (Kubernetes, distributed tracing, centralized logging already operational)
- Team structure aligned with service boundaries (Conway's Law)

---

## Hexagonal Architecture (Ports and Adapters)

The foundational pattern for maintainable systems. Separates business logic from infrastructure through ports (interfaces) and adapters (implementations).

### Three Concentric Layers

```
┌─────────────────────────────────────┐
│          Infrastructure             │
│  (DB adapters, HTTP, messaging)     │
│  ┌─────────────────────────────┐    │
│  │       Application           │    │
│  │   (Use cases, commands)     │    │
│  │  ┌─────────────────────┐    │    │
│  │  │      Domain          │    │    │
│  │  │ (Entities, Values,   │    │    │
│  │  │  Domain Services)    │    │    │
│  │  └─────────────────────┘    │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

**Rules:**
- Domain layer has ZERO external dependencies (no database, no framework imports)
- Ports are interfaces defined in domain/application layers
- Adapters implement ports in the infrastructure layer
- Dependencies point inward only

**Why this matters for agents:** Agents can work on domain logic without needing to understand database drivers, HTTP frameworks, or messaging systems. Clean boundaries = focused context = better agent output.

---

## Domain-Driven Design (Tactical Patterns)

Use when the business domain is complex and the software must model it accurately.

### Key Building Blocks

| Pattern | Purpose | Example |
|---------|---------|---------|
| **Aggregate** | Transactional consistency boundary | `Order` containing `OrderLine` items |
| **Entity** | Object with identity that persists | `User`, `Product` |
| **Value Object** | Immutable object defined by attributes | `Money`, `EmailAddress`, `DateRange` |
| **Domain Event** | Record of something that happened | `OrderPlaced`, `PaymentReceived` |
| **Repository** | Abstraction over persistence | `OrderRepository.findById()` |
| **Domain Service** | Logic that doesn't belong to one entity | `PricingService.calculateDiscount()` |

### Bounded Context Guidelines

- Each bounded context maps to one module (or service if extracting)
- Contexts communicate via events or explicit anti-corruption layers
- Never share database tables across bounded contexts
- Use event storming workshops with domain experts before writing code

---

## CQRS and Event Sourcing

### When to Use CQRS

**Use when:**
- Read and write patterns diverge significantly
- Complex business logic on the write side
- Need independently optimized read models (denormalized projections)
- Audit trail is a genuine requirement

**Skip when:**
- Simple CRUD with similar read/write shapes
- Small domain with little business logic
- Team unfamiliar with eventual consistency

**Start simple:** Separate read/write models backed by the same database. Add event sourcing only if audit trails or temporal queries ("what was the state at time T?") are genuine requirements.

### Event Sourcing Rules

- Events are immutable facts -- append only, never delete or modify
- State is derived from replaying events
- Use a schema registry (Avro or Protobuf) from day one for event evolution
- Design for eventual consistency from the start

---

## Event-Driven Architecture

### When Events vs Direct Calls

| Use Events When | Use Direct Calls When |
|----------------|----------------------|
| Loose coupling between bounded contexts | Synchronous response needed |
| Reactive workflows (state change triggers) | Simple request-response |
| Multiple consumers need the same data | Single consumer |
| Audit trail of all state changes needed | Low latency critical |

### Event Design Rules

- Events describe what happened, not what to do (`OrderPlaced`, not `ProcessOrder`)
- Include enough data for consumers to act without callback queries
- Version events explicitly from day one
- Use a schema registry for backward/forward compatibility

---

## Visualization: C4 Model

Use the C4 model for communicating architecture at four levels of detail:

1. **Context** -- System and its relationships with users and external systems
2. **Container** -- High-level technology choices (apps, databases, message queues)
3. **Component** -- Components within each container
4. **Code** -- Class/module level (optional, often generated from code)

Use Context and Container diagrams for architecture reviews. Component diagrams for detailed design. Skip Code diagrams unless auto-generated.

---

## Documentation Template: arc42

For comprehensive architecture documentation, use the arc42 template:

1. Introduction and goals
2. Architecture constraints
3. System scope and context
4. Solution strategy
5. Building block view
6. Runtime view
7. Deployment view
8. Cross-cutting concepts
9. Architecture decisions (ADRs)
10. Quality requirements
11. Risks and technical debt
12. Glossary
