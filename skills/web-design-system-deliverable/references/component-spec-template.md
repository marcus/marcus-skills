# Component Spec Template

Use this structure for every documented component.

## Header

- Name
- Purpose
- Where it belongs in the hierarchy

## Intent

Describe the job of the component in one sentence.

## Anatomy

List named parts.

Example:

- container
- label
- supporting text
- icon
- action slot

## Variants

Document each supported variant and why it exists.

Example:

- primary
- secondary
- quiet
- destructive

## Sizes

Define explicit sizes and vertical rhythm.

## States

Document:

- default
- hover
- focus-visible
- active
- disabled
- loading
- invalid or success if relevant
- empty (when the component can have no content)
- skeleton (placeholder while content loads)

## Content Rules

Explain:

- tone and casing (reference voice & tone guide for voice attributes and messaging hierarchy)
- character limits
- icon usage
- truncation behavior
- error and empty state copy patterns
- CTA label conventions

## Layout Rules

Explain:

- minimum and maximum widths
- spacing to adjacent elements
- responsive behavior
- container behavior in dense layouts

## Accessibility

Document:

- keyboard behavior
- aria expectations
- contrast requirements
- screen-reader labels
- error messaging rules

## Implementation Notes

Capture anything engineering needs to know:

- DOM structure
- token dependencies
- interaction caveats
- motion behavior (entrance, exit, hover, loading animations; duration and easing tokens; reduced-motion alternatives)
