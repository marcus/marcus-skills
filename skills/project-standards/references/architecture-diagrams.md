# Architecture diagrams

Keep project-owned Fractal models in `docs/diagrams/fractal/` (`model.c4` and `fractal.json`).
When architecture, boundaries, major flows, or planned capabilities change, update the affected
model and scenes alongside the code. Preserve stable IDs and distinguish current behavior from
proposals. Use the [Fractal usage skill](~/code/fractal/skills/fractal/SKILL.md) to author, validate,
export, register the project in the local catalog, and open its diagram for Marcus. Keep the model
in the project repository and use Fractal's existing tools; model maintenance should not require
changes to Fractal core.
