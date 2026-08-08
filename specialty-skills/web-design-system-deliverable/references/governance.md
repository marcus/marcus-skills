# Governance

Rules for extending, versioning, and maintaining the design system.

## 1. Extension Rules

How to add a new component to the system.

### Proposal Template

| Field | Description |
|-------|------------|
| Name | Component name |
| Problem | What user/product need does this solve? |
| Existing alternatives | Why can't current components handle this? |
| Usage scope | How many products/surfaces will use it? |
| Proposed variants | List expected variants |
| Token requirements | New tokens needed, if any |
| Accessibility notes | ARIA pattern, keyboard behavior |
| Priority | Critical / High / Medium / Low |

### Review Criteria

- The component solves a problem that occurs in at least two contexts.
- It cannot be composed from existing components.
- It follows existing token architecture (no hard-coded values).
- Accessibility requirements are documented upfront.
- It does not duplicate an existing component's purpose.

### Maturity Lifecycle

| Stage | Criteria | Usage |
|-------|----------|-------|
| Experimental | Proposal approved. Initial spec and implementation. | Available behind a flag or in a lab package. Not for production. |
| Beta | Used in at least one production surface. Feedback collected. API may still change. | Allowed in production with acknowledged risk. |
| Stable | Used in two or more production surfaces. API locked. Full docs, tests, and accessibility audit complete. | Recommended for all use. |

### Documentation Requirements Per Stage

- Experimental: component spec (draft), basic usage example.
- Beta: full component spec, all states, interaction spec, accessibility notes.
- Stable: everything in Beta plus: integration tests, screen reader test results, responsive behavior, content rules.

## 2. Token Extension Rules

### Adding a New Color

1. Add the raw value as a primitive token (e.g., `teal-500`).
2. Create a semantic mapping if the color serves a new role (e.g., `--color-accent-secondary`).
3. Document the role. A color without a documented role does not enter the system.
4. Ensure light and dark theme values are defined.
5. Run contrast audit for all foreground/background pairings involving the new color.

### Adding a New Spacing Value

1. Confirm it does not duplicate an existing step. Check the spacing scale.
2. If it fits the existing scale (4px or 8px base), add it as a primitive.
3. If it breaks the scale, justify why the exception is needed. Document it.

### Adding a New Component Token

1. Component tokens are only warranted when a component needs to deviate from semantic tokens for a specific, documented reason.
2. Map the component token to a semantic token as its default value.
3. Name it following the pattern: `--{component}-{part}-{property}` (e.g., `--card-header-bg`).

### When to Add a Primitive vs. Reuse

- Reuse when an existing primitive covers the value within the design intent.
- Add new when: the value does not exist in the scale, or aliasing an unrelated primitive would create false coupling (e.g., using `blue-500` for a teal accent).

## 3. Design Review Process

### Requires System Team Review

- New component proposal.
- New pattern (layout pattern, interaction pattern) not covered by existing components.
- Any token modification (rename, add, remove, change value).
- Changes to global styles (typography scale, spacing scale, color palette).
- Breaking changes to existing component APIs.

### Self-Serve (No Review Needed)

- Using existing components as documented.
- Applying documented patterns to a new screen.
- Composing existing components into a page layout.
- Using approved tokens for custom elements that do not enter the system.

## 4. Versioning Strategy

Use semantic versioning: `MAJOR.MINOR.PATCH`.

| Change Type | Version Bump | Examples |
|------------|-------------|---------|
| Breaking: removed or renamed token | Major | `--color-primary` renamed to `--color-accent` |
| Breaking: removed component or prop | Major | Button `variant="ghost"` removed |
| Breaking: changed token value significantly | Major | Accent color changed from blue to green |
| New component added | Minor | Tooltip component added |
| New token added | Minor | `--color-bg-elevated-hover` added |
| New variant or prop added | Minor | Button gets `size="xl"` |
| Bug fix | Patch | Focus ring now visible on dark bg |
| Token value tweak | Patch | `--space-4` changed from 16px to 15px (if minor) |
| Documentation update | Patch | Clarified usage guidance |

Rules:

- Never ship breaking changes without a major version bump.
- Bundle breaking changes. Do not spread them across multiple majors.
- Pre-release versions use `-alpha.1`, `-beta.1` suffixes.
- Maintain a `CHANGELOG.md` with every release.

## 5. Deprecation Protocol

### Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| Announcement | Day 0 | Mark as deprecated in docs. Add console warning in code. |
| Migration period | 2-4 release cycles (minimum) | Migration guide published. Old and new coexist. |
| Removal | After migration period | Remove from system. Major version bump. |

### Requirements

- Every deprecated item must have a documented migration path.
- Migration guide must include: what to replace, code before/after, token mapping if tokens changed.
- Console warnings must reference the migration guide URL.
- Deprecation must be communicated in: changelog, release notes, design system documentation, and team channels.

### Deprecation Marker

In token files:

```json
{
  "color": {
    "primary": {
      "value": "{color.accent.brand}",
      "type": "color",
      "deprecated": true,
      "deprecated_comment": "Use color.accent.brand instead. Removal in v4.0."
    }
  }
}
```

In code:

```css
/* @deprecated Use --color-accent instead. Removal in v4.0. */
--color-primary: var(--color-accent);
```

## 6. Contribution Guidelines

### Who Can Contribute

- Designers: propose new components, patterns, token changes.
- Engineers: propose API changes, new variants, performance improvements.
- Content: propose content rules, error message patterns.

### Process

1. Open an issue or RFC using the proposal template (see Extension Rules above).
2. System team triages within one week.
3. If approved, contributor creates implementation (design, code, or both).
4. Submit PR with: implementation, spec update, test coverage, accessibility check.
5. System team reviews. At least one design review and one engineering review required.
6. On approval, merge and release per versioning strategy.

### PR Requirements

- [ ] Component spec updated or created.
- [ ] Tokens follow naming standard.
- [ ] All states documented and implemented.
- [ ] Light and dark themes tested.
- [ ] Accessibility audit passed (see accessibility-audit reference).
- [ ] No hard-coded values (all values via tokens).
- [ ] Changelog entry added.

## 7. Quality Gates

Before any system change ships, verify:

- [ ] Accessibility audit passed (automated + manual).
- [ ] All component states documented (default, hover, focus, active, disabled, loading, error).
- [ ] Light theme tested.
- [ ] Dark theme tested.
- [ ] Responsive behavior verified at all breakpoints.
- [ ] Content rules included (character limits, truncation, tone).
- [ ] Token usage verified (no hard-coded colors, spacing, or radii).
- [ ] Contrast ratios documented for new color pairings.
- [ ] Keyboard navigation tested.
- [ ] Screen reader tested with at least one tool.
- [ ] Reduced motion behavior verified.
- [ ] Breaking changes flagged and versioned correctly.
- [ ] Changelog updated.
- [ ] Migration guide written if deprecating anything.

Do not merge without all applicable gates passing.

## 8. System Health Metrics

Track these to measure design system effectiveness.

| Metric | How to Measure | Target |
|--------|---------------|--------|
| Adoption rate | % of product surfaces using system components vs. custom | > 80% |
| Component coverage | % of UI patterns covered by system components | > 90% |
| Design drift | Count of one-off overrides or `!important` usage in consuming codebases | Trending to zero |
| Accessibility score | Average Lighthouse accessibility score across products | 100 |
| Token usage | % of color/spacing/radius values that reference tokens vs. hard-coded | > 95% |
| Contribution rate | PRs from outside the system team per quarter | Increasing |
| Bug rate | System component bugs reported per quarter | Decreasing |
| Time to adoption | Days from component release to first production use | < 14 days |

### Review Cadence

- Weekly: triage new issues and proposals.
- Monthly: review health metrics. Identify top design drift offenders.
- Quarterly: roadmap review. Plan deprecations, major changes, new components.
- Annually: audit entire system against current product needs. Sunset unused components.
