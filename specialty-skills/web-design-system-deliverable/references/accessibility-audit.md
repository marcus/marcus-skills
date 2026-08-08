# Accessibility Audit

Audit every design system deliverable against these requirements before shipping.

## 1. Contrast Documentation

For each semantic color pairing, record the contrast ratio and WCAG compliance.

Template table:

| Role | Foreground | Background | Ratio | AA (4.5:1) | AAA (7:1) |
|------|-----------|-----------|-------|------------|-----------|
| text-strong on canvas | `--color-fg-strong` | `--color-bg-canvas` | | Pass/Fail | Pass/Fail |
| text-strong on surface | `--color-fg-strong` | `--color-bg-surface` | | | |
| text-strong on elevated | `--color-fg-strong` | `--color-bg-elevated` | | | |
| text-muted on canvas | `--color-fg-muted` | `--color-bg-canvas` | | | |
| text-muted on surface | `--color-fg-muted` | `--color-bg-surface` | | | |
| text-subtle on canvas | `--color-fg-subtle` | `--color-bg-canvas` | | | |
| accent on canvas | `--color-accent` | `--color-bg-canvas` | | | |
| accent-contrast on accent | `--color-accent-contrast` | `--color-accent` | | | |
| success-fg on success-soft | `--color-success` | `--color-success-soft` | | | |
| warning-fg on warning-soft | `--color-warning` | `--color-warning-soft` | | | |
| danger-fg on danger-soft | `--color-danger` | `--color-danger-soft` | | | |
| info-fg on info-soft | `--color-info` | `--color-info-soft` | | | |
| inverse-fg on contrast-bg | `--color-fg-inverse` | `--color-bg-inverse` | | | |

Rules:

- All text pairings must pass AA (4.5:1 for normal text, 3:1 for large text).
- Accent used as text must pass AA. Accent used only as decoration may pass 3:1.
- Fill this table for both light and dark themes.
- Use a tool (WebAIM, Stark, or programmatic check) to calculate ratios. Do not eyeball.

## 2. ARIA Pattern Reference

For each component type, document the required ARIA roles, properties, and states.

### Button

- Role: `button` (native `<button>` preferred).
- `aria-disabled="true"` when disabled (not just the `disabled` attribute if styled differently).
- `aria-busy="true"` when loading. Pair with visually hidden loading announcement.
- `aria-pressed` for toggle buttons only.
- `aria-expanded` when controlling a collapsible region.

### Link

- Role: implicit from `<a href>`. No override needed.
- `aria-current="page"` for the active page in navigation.
- External links: append visually hidden text "(opens in new tab)" or use `aria-describedby`.

### Navigation

- Wrap in `<nav>` with `aria-label` distinguishing multiple navs (e.g., "Main navigation", "Footer navigation").
- Current page link gets `aria-current="page"`.

### Modal / Dialog

- Role: `dialog` with `aria-modal="true"`.
- `aria-labelledby` pointing to the dialog title.
- `aria-describedby` pointing to the dialog body if it is a confirmation.
- Focus trap: required. See Keyboard Navigation Map below.
- On close, return focus to the trigger element.

### Alert

- Role: `alert` for urgent messages (implicit `aria-live="assertive"`).
- Role: `status` for non-urgent feedback (implicit `aria-live="polite"`).
- Do not use `alert` for static banners that exist on page load.

### Form Field

- `<label>` associated via `for`/`id` or wrapping.
- `aria-describedby` linking to hint text.
- `aria-errormessage` (or `aria-describedby`) linking to error text.
- `aria-invalid="true"` when in error state.
- `aria-required="true"` when required (or native `required`).
- Group related fields with `<fieldset>` and `<legend>`.

### Table

- Use semantic `<table>`, `<thead>`, `<th scope="col">`, `<th scope="row">`.
- Sortable columns: `aria-sort="ascending"`, `"descending"`, or `"none"`.
- `<caption>` or `aria-labelledby` for table title.

### Tabs

- Container: `role="tablist"`.
- Each tab: `role="tab"`, `aria-selected="true|false"`, `aria-controls` pointing to panel.
- Each panel: `role="tabpanel"`, `aria-labelledby` pointing to its tab.

### Badge

- Decorative badges: no live region. Content is read in document flow.
- Notification count badges: use `aria-label` on the parent (e.g., "Notifications, 3 unread").
- If badge content updates dynamically, wrap in `aria-live="polite"`.

### Loading State

- Spinner or skeleton: `aria-busy="true"` on the container being loaded.
- Add visually hidden `aria-live="polite"` region announcing "Loading" and "Content loaded."

## 3. Keyboard Navigation Map

For each interactive pattern, document expected keyboard behavior.

Template:

| Pattern | Tab | Enter / Space | Escape | Arrow Keys | Focus Trap |
|---------|-----|--------------|--------|------------|------------|
| Button | Focusable | Activates | -- | -- | No |
| Link | Focusable | Navigates | -- | -- | No |
| Toggle Button | Focusable | Toggles state | -- | -- | No |
| Modal | Focus moves into modal | Activates focused element | Closes modal | -- | Yes |
| Dropdown Menu | Opens on trigger focus + Enter | Selects item | Closes menu | Up/Down moves focus | Yes while open |
| Tabs | Focus on active tab | Activates tab | -- | Left/Right switches tabs | No (tabs are a single stop) |
| Form Field | Each field is a tab stop | Submits if in form | -- | -- | No |
| Checkbox | Focusable | Toggles checked | -- | -- | No |
| Radio Group | First/selected radio is tab stop | Selects | -- | Up/Down or Left/Right moves selection | No (group is a single stop) |
| Accordion | Header is focusable | Toggles panel | -- | Optional: Up/Down between headers | No |

Focus trap rules for modals:

1. On open, move focus to the first focusable element inside (or the close button).
2. Tab from the last focusable element wraps to the first.
3. Shift+Tab from the first wraps to the last.
4. Escape closes and returns focus to the trigger.
5. Background click closes and returns focus to the trigger.

## 4. Screen Reader Expectations

Document what must be announced for each state change.

### Button States

- Loading: announce "Loading" via `aria-busy` or live region. Do not lose button label.
- Disabled: announce "dimmed" or "disabled" (native `disabled` handles this).
- Toggle: announce "pressed" or "not pressed" via `aria-pressed`.

### Form Errors

- On validation failure: announce error message. Use `aria-errormessage` tied to the field. Ensure the error text is injected into the DOM so it is announced.
- On correction: remove `aria-invalid` so "invalid" is no longer announced.

### Alert Appearance

- Assertive alerts: announced immediately, interrupting current speech.
- Polite status messages: announced at the next pause.

### Badge Content

- Static badges: read inline. No special announcement.
- Dynamic count: update `aria-label` on the parent. Use `aria-live="polite"`.

### Navigation Changes (SPA)

- On route change, announce the new page title via a live region or focus management (move focus to the `<h1>`).

### Theme Toggle

- Announce the new state: "Dark theme enabled" or "Light theme enabled" via a live region.

### Visually Hidden Text Patterns

Use this utility class:

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

Apply to: icon-only button labels, external link hints, loading announcements, skip-nav links (visible on focus).

## 5. Color Independence

Never rely on color alone to convey meaning.

Rules:

- Status indicators must pair color with an icon or text label.
- Form errors must show error text, not just a red border.
- Links within body text must have underline (not just color difference).
- Charts and data visualizations must use patterns or labels in addition to color.
- Selected/active states must have a non-color indicator (border, weight, icon).

Component checklist:

| Component | Color Indicator | Secondary Indicator | Passes |
|-----------|----------------|--------------------:|--------|
| Alert | Status color bg | Icon + role text (Success, Error, etc.) | |
| Badge | Status color | Text content or icon | |
| Form field (error) | Red border | Error text + icon | |
| Form field (success) | Green border | Success text + icon | |
| Button (destructive) | Red bg | Label says "Delete" or similar | |
| Nav item (active) | Accent color | Bold weight or underline or indicator bar | |
| Toggle | Color change | Position change + aria-pressed | |

## 6. Reduced Motion Audit

Respect `prefers-reduced-motion: reduce`.

Rules:

- Every `transition` and `animation` must have a reduced-motion override.
- In reduced-motion mode, transitions may be instant (`duration: 0s`) or use a very short duration (`50ms`).
- No information may be conveyed only through motion (e.g., a shake animation for error must also show error text).
- Focus ring transitions: instant in reduced-motion.
- Page transitions (SPA): cross-fade or cut, no slide.
- Loading spinners: may remain animated (they convey ongoing state, not information through motion). Alternatively, replace with a pulsing opacity or static indicator.

Template:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Checklist:

- [ ] All component transitions have reduced-motion fallback.
- [ ] No information conveyed solely through animation.
- [ ] Focus transitions are instant under reduced-motion.
- [ ] Loading indicators remain functional under reduced-motion.
- [ ] Hover/active micro-interactions degrade gracefully.

## 7. Testing Protocol

Run this audit sequence on every deliverable.

### Step 1: Automated Scan

- Run axe-core (via browser extension or CI integration) on every page/state.
- Run Lighthouse accessibility audit. Target 100.
- Fix all critical and serious issues before proceeding.

### Step 2: Manual Keyboard Testing

1. Unplug the mouse.
2. Tab through every interactive element on the page.
3. Confirm visible focus ring on every focusable element.
4. Confirm Enter/Space activates buttons and links.
5. Confirm Escape closes modals and dropdowns.
6. Confirm focus traps work in modals.
7. Confirm skip-nav link works and is visible on focus.
8. Confirm no keyboard traps (focus stuck with no way out).

### Step 3: Screen Reader Testing

Test with at least one of:

- VoiceOver (macOS/iOS): Safari.
- NVDA (Windows): Firefox or Chrome.

For each component, confirm:

- Name is announced correctly.
- Role is announced correctly.
- State changes are announced.
- Error messages are associated and read.
- Live regions fire as expected.

### Step 4: Zoom and Magnification

- Zoom browser to 200%. Confirm no content is clipped or overlapping.
- Zoom to 400%. Confirm critical content is still reachable (may reflow).
- Test with OS-level magnification if applicable.

### Step 5: Color Blindness Simulation

- Use Sim Daltonism, Chrome DevTools color vision simulation, or Stark.
- Check: protanopia, deuteranopia, tritanopia, achromatopsia.
- Confirm all status indicators, charts, and interactive states remain distinguishable.

### Step 6: Document Results

Record in a table:

| Test | Tool | Result | Issues | Fixed |
|------|------|--------|--------|-------|
| Automated | axe-core | | | |
| Automated | Lighthouse | Score: | | |
| Keyboard | Manual | | | |
| Screen Reader | VoiceOver | | | |
| Zoom 200% | Browser | | | |
| Zoom 400% | Browser | | | |
| Color Blindness | Sim Daltonism | | | |
| Reduced Motion | Manual | | | |

Do not ship until all rows pass.
