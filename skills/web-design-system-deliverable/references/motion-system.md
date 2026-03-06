# Motion System

Motion is a design material. These guidelines define how movement communicates brand personality, reinforces hierarchy, and provides feedback.

## Motion Principles

### 1. Motion confirms, never decorates

Every animation must answer a user question: "Did that work?" "Where did it go?" "What changed?" If an animation answers none of these, remove it.

- Do: Fade in a toast notification to confirm a save.
- Don't: Bounce a logo on page load for visual flair.

### 2. Speed communicates confidence

Fast transitions feel decisive and premium. Slow transitions feel considered and dramatic. Sluggish transitions feel broken. Calibrate duration to the weight of the change.

- Do: Use micro duration (60-80ms) for toggles so state changes feel instant.
- Don't: Use 400ms for a checkbox animation -- it signals uncertainty.

### 3. Exit faster than enter

Elements should leave the screen quicker than they arrive. Entering content deserves attention; departing content should not compete with what replaces it.

- Do: Enter a modal at 280ms, dismiss it at 180ms.
- Don't: Use identical duration for open and close -- the close feels sluggish.

### 4. Choreography creates hierarchy

When multiple elements animate, stagger them to guide the eye. The most important element moves first or moves most. Never animate everything simultaneously.

- Do: Stagger card entrances by 60ms so the grid "builds" left-to-right, top-to-bottom.
- Don't: Fade in all 12 cards at once -- it reads as a flicker, not a reveal.

## Duration Scale

| Token                        | Value  | Use case                                      |
| ---------------------------- | ------ | --------------------------------------------- |
| `--motion-duration-micro`    | 60ms   | Toggles, checkboxes, icon state changes       |
| `--motion-duration-fast`     | 120ms  | Hover states, small color shifts              |
| `--motion-duration-base`     | 180ms  | Reveals, menu open, tooltip show              |
| `--motion-duration-moderate` | 280ms  | Overlays, modals, drawer panels               |
| `--motion-duration-slow`     | 400ms  | Page transitions, large layout shifts          |
| `--motion-duration-dramatic` | 600ms  | Hero entrances, onboarding sequences          |

Rules:

- Never exceed 600ms for interactive UI. Longer durations are acceptable only for passive storytelling animations (e.g., ambient background).
- Pair micro and fast durations with simple property changes (opacity, color). Pair moderate and above with spatial changes (transform, layout).
- Exit animations should use one step shorter than their entrance counterpart.

## Easing Library

| Token                        | CSS value                           | Character             |
| ---------------------------- | ----------------------------------- | --------------------- |
| `--motion-ease-standard`     | `cubic-bezier(0.2, 0.8, 0.2, 1)`   | General UI, symmetric |
| `--motion-ease-emphasis`     | `cubic-bezier(0.16, 1, 0.3, 1)`    | Enter, draw attention |
| `--motion-ease-decelerate`   | `cubic-bezier(0, 0, 0.2, 1)`       | Entering elements     |
| `--motion-ease-accelerate`   | `cubic-bezier(0.4, 0, 1, 1)`       | Exiting elements      |
| `--motion-ease-spring`       | `cubic-bezier(0.34, 1.56, 0.64, 1)`| Playful, bouncy       |

When to use each:

- **Standard**: Default for most transitions -- color changes, border shifts, background swaps. Feels neutral and professional.
- **Emphasis**: Draw the eye to entering content. Good for modals, toasts, expanding panels. Has an overshoot that creates a "landing" feel.
- **Decelerate**: Elements arriving from off-screen. They start fast (already in motion) and settle into place. Cards sliding in, dropdown menus appearing.
- **Accelerate**: Elements leaving. They start slow (responding to dismissal) and accelerate away. Closing modals, collapsing accordions.
- **Spring**: Optional per brand. Use sparingly for moments of delight -- toggle switches, like buttons, drag-and-drop snaps. Overuse makes the UI feel juvenile.

## Choreography Patterns

### Staggered entrance

Cards, list items, and grid children enter sequentially. Use `--motion-stagger-delay` (60ms) between each item.

```css
@keyframes stagger-enter {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stagger-enter > * {
  animation: stagger-enter var(--motion-duration-moderate) var(--motion-ease-decelerate) both;
}

.stagger-enter > *:nth-child(1) { animation-delay: calc(var(--motion-stagger-delay) * 0); }
.stagger-enter > *:nth-child(2) { animation-delay: calc(var(--motion-stagger-delay) * 1); }
.stagger-enter > *:nth-child(3) { animation-delay: calc(var(--motion-stagger-delay) * 2); }
/* Continue as needed */
```

### Cascade reveal

Hero sections use a top-down cascade: kicker, then headline, then body, then CTA. Each layer uses emphasis easing with 80-100ms stagger.

```css
.hero .kicker    { animation-delay: 0ms; }
.hero h1         { animation-delay: 80ms; }
.hero p          { animation-delay: 160ms; }
.hero .button    { animation-delay: 240ms; }
```

### Coordinated tab switch

When switching tabs, outgoing content fades out (fast, accelerate), then incoming content fades in (base, decelerate). Never crossfade -- it creates visual mud.

```css
.tab-content[data-state="exiting"] {
  animation: fade-out var(--motion-duration-fast) var(--motion-ease-accelerate) forwards;
}
.tab-content[data-state="entering"] {
  animation: fade-in var(--motion-duration-base) var(--motion-ease-decelerate) both;
  animation-delay: var(--motion-duration-fast);
}
```

## Interaction Signatures

### Hover

Lift elements 1px with a subtle shadow expansion. Color shifts use fast duration. The feel is premium and restrained -- no bouncing, no scaling.

```css
.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-elevated);
  transition: transform var(--motion-duration-fast) var(--motion-ease-standard),
              box-shadow var(--motion-duration-base) var(--motion-ease-standard);
}
```

### Press

Elements compress slightly on `:active` -- `translateY(0)` and shadow returns to resting state. This creates a tactile "push" feeling.

```css
.card:active {
  transform: translateY(0);
  box-shadow: var(--shadow-soft);
}
```

### Focus

Focus rings appear instantly (no transition on outline). The ring uses the accent color at reduced opacity. This ensures keyboard users always get immediate feedback.

### Scroll

No scroll-triggered animations by default. If used, elements fade in with decelerate easing at moderate duration. Trigger once, never replay. Use `IntersectionObserver`, not scroll listeners.

## Page Transitions

| Pattern   | When to use                            | Duration | Easing     |
| --------- | -------------------------------------- | -------- | ---------- |
| Crossfade | Default between sibling pages          | slow     | standard   |
| Slide     | Drill-down navigation (list to detail) | moderate | decelerate |
| Morph     | Shared element between views           | moderate | emphasis   |

Rules:

- Page transitions must not exceed `--motion-duration-slow` (400ms).
- Always provide an opacity component -- pure spatial transitions feel jarring.
- Sliding direction follows reading order: forward = slide left, backward = slide right.

```css
@keyframes page-enter {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-enter {
  animation: page-enter var(--motion-duration-slow) var(--motion-ease-decelerate) both;
}
```

## Loading and Skeleton Patterns

### Shimmer

Skeleton placeholders use a left-to-right shimmer gradient. The shimmer moves at a slow, steady pace (1.6s loop) to communicate "loading" without urgency.

```css
@keyframes shimmer {
  from { background-position: -200% 0; }
  to   { background-position: 200% 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-soft) 25%,
    var(--color-border-subtle) 50%,
    var(--color-bg-soft) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.6s var(--motion-ease-standard) infinite;
  border-radius: var(--radius-1);
}
```

### Skeleton shape rules

- Text lines: height matches `--text-1` line-height, width varies (100%, 80%, 60%) to mimic natural text.
- Avatars: use circular skeleton matching avatar dimensions.
- Cards: skeleton fills the card interior; do not skeleton the card chrome (border, shadow).
- Never show more than 6 skeleton items. If the list could be longer, show 3-4 and let the rest load in.

### Pulse rhythm

For single loading indicators (spinners, progress dots), pulse at 1s intervals with standard easing. Do not pulse skeletons -- shimmer only.

## Reduced Motion as Design

`prefers-reduced-motion: reduce` is not "disable all animation." It is a parallel design track.

### Strategy

| Normal behavior          | Reduced-motion alternative                |
| ------------------------ | ----------------------------------------- |
| Slide + fade entrance    | Opacity-only fade (fast duration)         |
| Staggered card entrance  | All cards appear simultaneously, opacity 0 to 1 |
| Shimmer skeleton         | Static skeleton with soft pulsing opacity |
| Hover lift + shadow      | Color change only, no transform           |
| Page slide transition    | Instant cut with brief opacity fade       |

### Implementation

Set duration tokens to 0ms for spatial animations. Keep a minimal opacity transition for visual continuity.

```css
@media (prefers-reduced-motion: reduce) {
  :root {
    --motion-duration-micro: 0ms;
    --motion-duration-fast: 0ms;
    --motion-duration-base: 0ms;
    --motion-duration-moderate: 0ms;
    --motion-duration-slow: 0ms;
    --motion-duration-dramatic: 0ms;
  }

  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Rules:

- Never remove hover/focus feedback entirely. Color changes are acceptable even when motion is reduced.
- Skeleton loading should switch from shimmer to a static soft background. Users who are motion-sensitive still need loading indication -- use a subtle opacity pulse (0.6 to 1.0, 2s cycle).
- Test the reduced-motion experience as a first-class design, not an afterthought.
