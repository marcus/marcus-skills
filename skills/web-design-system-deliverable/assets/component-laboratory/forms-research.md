# Forms Research

I now have comprehensive research. Let me compile the findings.

---

# Form Controls Research: Counterintuitive & Premium Approaches

## 1. How Linear, Stripe, Vercel, Notion, Figma Style Their Inputs

### Linear
- **Dark-first philosophy**: Background `#121212`, input background `#171717` -- inputs barely distinguish from surface. The contrast comes from text, not borders.
- **Border-radius**: `5px` for inputs (smaller than the trendy `8px` cards), `3px` for sub-elements. Deliberately understated.
- **Border**: `1px solid` using a muted alt-background color, not a distinct "border color." Borders blend rather than delineate.
- **Spacing**: 8px base scale (8, 16, 32, 64). Generous but systematic.
- **Color system**: LCH color space (not HSL) for perceptually uniform colors. Accent is a muted purple `#848CD0` in dark mode.
- **Typography**: Inter variable font. Weights 500/600/800. Hierarchy through weight, not color.
- **Transitions**: 0.2s for all state changes. Hover uses `scale(1.01) translateY(-4px)`.
- **Component foundation**: Radix UI primitives with styled-components. Behavior separated from visual styling.

### Stripe
- **Three themes**: `stripe`, `night`, `flat` -- each changes the entire input personality.
- **Label positions**: `above`, `floating`, or `auto`. Floating labels are first-class.
- **Layout variants**: `spaced` (default, gaps between fields) vs `condensed` (fields grouped flush).
- **Focus state**: Uses both `focusBoxShadow` AND `focusOutline` as separate tokens. Default focus is `0 0 0 2px var(--colorPrimary)`.
- **Input shadow**: Supports complex inset shadows like `inset -1px -1px #ffffff, inset 1px 1px #0a0a0a` for depth.
- **Tokens**: `colorPrimary`, `colorBackground`, `colorText`, `colorDanger`, `colorSuccess`, `colorWarning`, `spacingUnit`, `borderRadius`.
- **CSS selectors available**: `.Input`, `.Input--empty`, `.Input--invalid`, `.Input:hover`, `.Input:focus`, `.Input:disabled`, `.Input:autofill`, `.Input::placeholder`, `.Input::selection`, `.Label--floating`, `.Error`.

### Vercel (Geist Design System)
- **Minimum 16px font on mobile** to prevent iOS auto-zoom -- this is non-negotiable.
- **Hit targets**: 44px minimum on mobile, 24px on desktop.
- **Focus**: Uses `:focus-visible` (not `:focus`) to avoid rings on mouse click. Only keyboard users see the ring.
- **Contrast model**: Prefers APCA over WCAG 2 for perceptual accuracy.
- **Dark mode**: `color-scheme: dark` on `<html>`, `<meta name="theme-color" content="#0A0A0A">`.
- **Validation philosophy**: Allow any input, show feedback after -- never block keystrokes.
- **Placeholders**: End with ellipsis, show example patterns (e.g., `+1 (123) 456-7890`).
- **Submit behavior**: Enter submits single-input forms; Cmd+Enter for textareas.
- **Interaction states must have higher contrast than rest state** -- hover/focus are MORE visible, not just different.

### Notion
- **Inline editing pattern**: No visible input at rest. Hover reveals subtle borders. Click transforms label into editable field.
- **ContentEditable**: Uses `contentEditable` instead of `<input>` elements for most text. This means no browser-default input styling at all.
- **Invisible inputs**: The counterintuitive pattern -- inputs that don't look like inputs until interaction.

### Figma
- **Command palette**: Minimal chrome, focus on the search input with large text, no visible borders -- just a floating container with shadow.
- **Inline property inputs**: Tiny, dense inputs with no visible border until hover/focus. Number inputs with drag-to-scrub interaction.

## 2. Premium Form Design Trends 2025-2026

- **Neumorphism inputs**: Soft inset shadows creating "pressed into surface" effect. Subtle but tactile.
- **Glassmorphism**: Translucent input backgrounds with `backdrop-filter: blur()`, borders using `rgba()` for frosted glass edges.
- **Conversational forms**: One question at a time, full-screen. Each input gets maximum space and attention.
- **Smart personalization**: Fields that appear/disappear dynamically based on prior answers.
- **Dark mode dominance**: 82.7% of users prefer dark mode. Design dark-first, adapt to light.

## 3. Hyper-Minimal Input Design

### Underline-Only
- Remove all borders except `border-bottom`. On focus, the underline animates width (grows from center outward) or changes color.
- Material Design pioneered this, but the premium version uses thinner lines (1px, not 2px) and muted colors.

### No Border At All
- Notion's approach: zero visual container. Just text with a cursor. The content IS the input.
- Background-only differentiation: slightly different background shade, no border whatsoever. `background: rgba(0,0,0,0.04)` in light mode.

### Character-Level Underlines
- Individual underline under each character (like a PIN input). Unusual and highly focused.

### Elastic/Animated Validation
- SVG-based underline that "stretches" on valid input, with an animated checkmark. No color change needed -- the motion communicates validity.

## 4. Luxury/Fashion Checkout Forms

### Balenciaga
- **Black and white palette exclusively** -- the only color is a neon green add-to-cart button.
- **Accordion/concertina forms**: Fields hidden by default, revealed on click. Visual spaciousness over convenience.
- **No icons**: No heart for wishlist, no truck for shipping, no magnifying glass. Pure text.
- **Guest checkout without friction**: No registration gate.
- **Works better on mobile** than desktop -- whitespace feels intentional on small screens, empty on large.
- **Newsletter only in footer**: No popups, no aggressive capture. Restraint over conversion.

### General Luxury Pattern
- Fewer choices = faster decisions. Luxury forms show fewer fields.
- Bold lines with geometric simplicity. Typography does the heavy lifting.
- Generous whitespace between fields (often 32-48px gaps).
- Monospaced or serif fonts for form labels (breaks the sans-serif convention).

## 5. Japanese Form Design (Ma / Negative Space)

- **Ma (negative space)**: Space between elements is as important as elements themselves. Inputs float in generous whitespace.
- **Color restraint**: Traditional Japanese colors are muted -- not the saturated primaries of Western UI.
- **Balance over efficiency**: Form layouts prioritize visual harmony, sometimes at the cost of density.
- **Interesting tension**: Traditional Japanese websites are actually information-dense (opposite of minimal). The minimalist aesthetic is a younger-generation/globalized interpretation.
- **Typography-forward**: Large font sizes for key elements, minimal supporting text. Inputs get breathing room through type scale, not just margin.

## 6. Material Design vs. Flat Input

- **Material Design inputs**: Filled variant (background color, no border, bottom underline) or Outlined variant (full border, floating label). Both use the label-float animation.
- **Flat Design inputs**: No depth, no shadow, just border and content. Faster rendering, simpler DOM.
- **Current trend**: Designers are choosing **neither pure approach** -- they're hybridizing. The most common premium pattern in 2025-2026 is: flat design with ONE Material-inspired element (usually the floating label OR the focus underline, but not both).
- **Material's decline in inputs**: The filled variant with its colored background (`#F5F5F5`) feels dated. Outlined is surviving better.

## 7. Apple Web vs. Apple OS

- **Apple HIG for native**: Mini/Small/Medium controls use rounded rectangles. Large controls now use **capsule shapes** (pill-shaped). New X-Large size added.
- **Apple web forms**: Custom-styled, not native OS controls. Apple encourages web apps to implement their own design systems.
- **iOS Safari specifics**: `appearance: none` required to override native styling. 16px minimum font to prevent auto-zoom.

## 8. Premium Search Bars

- **Sora (OpenAI)**: Background dims on focus, search bar takes center stage. Contextual dimming.
- **Command palette pattern (Cmd+K)**: No visible search bar at all -- it's invoked, not always present. Linear, Figma, Vercel all use this.
- **Progressive disclosure**: Filters appear only when needed, not pre-displayed.
- **Levitating effect**: Search bar elevates (shadow increases) on focus.
- **Result categorization**: Semantic grouping (Accounts, Tags, Places) rather than flat list.
- **No magnifying glass icon**: Some premium implementations drop the icon entirely -- the context makes it obvious.

## 9. Custom Checkbox/Radio Alternatives

- **`appearance: none`** is now well-supported -- the primary technique for custom checkboxes.
- **Animated checkmarks**: SVG path animation that "draws" the check on selection.
- **Color-fill checkboxes**: No checkmark at all -- the entire box fills with brand color. Simpler, cleaner.
- **Toggle-as-checkbox**: Replace checkboxes entirely with small inline toggles.
- **Radio as segmented control**: Radio options as horizontal button group with active-state highlight.
- **Dot-based radio**: Custom `::before` pseudo-element creates a filled circle within a circle, avoiding the browser's default rendering.
- **Size**: Custom checkboxes at `18px` with `border-radius: 3-4px`, transitioning from `#e9eef2` to brand color on check.

## 10. Form Validation: Calm vs. Aggressive

### Calm (Premium) Approach
- **Inline, adjacent to field**: Error text appears below the field, not in a banner.
- **Subtle animation**: 200-300ms fade-in. A gentle pulse on the icon, not a shake on the field.
- **Tone**: "Let's try that again" or "Hmm, that doesn't look right" -- not "ERROR: Invalid input."
- **No ALL CAPS, no exclamation marks** in error text.
- **Color**: Muted red/warm tone, not `#FF0000`. More like `#DC3545` or even an amber/orange.
- **Focus the first error on submit** -- don't just show all errors at once.
- **Real-time but not aggressive**: Validate after the user leaves a field (on blur), not on every keystroke.

### Aggressive (Avoid)
- Red borders + red text + red icon simultaneously.
- Shaking animation on the input.
- Banner at top of form listing all errors.
- Blocking input (preventing typed characters).

## Specific Observations Summary

### Input Border Styles
| Pattern | Who Uses It | Feel |
|---------|------------|------|
| Bottom-only | Material Design, minimal forms | Clean, editorial |
| None (background-only) | Notion, content-heavy apps | Invisible, inline |
| Full border, 1px, muted | Stripe, shadcn/ui, Vercel | Professional, safe |
| Full border on focus only | Figma property panels | Dense, tool-like |
| Dashed | File upload zones | Invitational |

### Label Position Patterns
| Pattern | When To Use |
|---------|-------------|
| **Floating** (starts as placeholder, animates up) | Space-constrained, modern |
| **Above** (always visible) | Forms where clarity > style |
| **Inline/Placeholder-only** | ONLY for search and filters -- never for data entry |
| **Left-aligned** (label beside input) | Dense data-entry, CRM-style |
| **Hidden until focus** | Notion-style inline editing |

### Focus States Beyond Blue Ring
- `box-shadow: 0 0 0 2px brand-color` (Stripe, shadcn)
- Background color shift (subtle lightening/darkening)
- Border-color transition only (no shadow, no outline)
- `transform: scale(1.01)` micro-zoom
- Underline grows from center (Material-style)
- `:focus-visible` only (Vercel recommendation) -- mouse users see nothing, keyboard users see ring
- Double-shadow technique: two `box-shadow` values for guaranteed contrast on any background

### Padding/Proportion: Generic vs. Premium
- **Generic**: `padding: 8px 12px`, `height: 36px`, `border-radius: 4px`
- **Premium**: `padding: 12px 16px`, `height: 40-44px`, `border-radius: 6-8px`, `font-size: 15-16px`
- **Luxury**: `padding: 16px 20px`, `height: 48-56px`, `border-radius: 0-2px` (sharp corners = editorial)
- **The proportion rule**: Border-radius should scale with element size. 16px radius on a 32px element = pill. Same 16px on 400px element = barely rounded.
- **Nested radius formula**: Inner radius = outer radius minus padding.

### Dark Mode Inputs
- Never use pure `#000000` background. Use `#121212` to `#1A1A1A`.
- Input backgrounds: slightly lighter than page (`#171717` on `#121212`).
- Borders: lighter than background but muted (`216 34% 17%` in HSL).
- Desaturated accent colors (saturated colors vibrate against dark surfaces).
- Text: Not pure white. Use `#CCCCCC` to `#E0E0E0`.
- shadcn dark mode input token: `--input: 216 34% 17%`.

### File Upload Designs
- **Dashed border drop zone**: `border: 2px dashed`, changes color/thickness on `dragover`.
- **Visual feedback**: Border color shifts + background tint when file hovers over zone.
- **Premium**: Progress indicators, file previews, chunked upload support.
- **Minimal**: Just a text link "Upload file" that opens native picker. No zone needed.

### Textarea Handles/Grips
- Default resize handle can be hidden with `resize: none` then replaced with custom positioned element.
- WebKit allows `::-webkit-resizer` pseudo-element styling (Chrome, Safari, Edge only).
- Premium approach: Auto-growing textarea that expands with content (`height: auto` + JS), eliminating the need for a resize handle entirely.
- The handle is increasingly seen as unnecessary -- auto-resize is the premium default.

### Toggle Switches
- iOS-style with gooey/morphing animation on the knob.
- Premium: `cubic-bezier` custom timing, not linear transitions.
- Only animate `transform` and `opacity` for 60fps.
- `:has()` selector enables icon morphing (sun to moon) purely in CSS.
- Guard toggles: two-step activation for destructive settings.

Sources:
- [Linear UI Redesign](https://linear.app/now/how-we-redesigned-the-linear-ui)
- [Linear Style Tokens](https://linear.style/)
- [Linear Design Trend](https://blog.logrocket.com/ux-design/linear-design/)
- [Stripe Appearance API](https://docs.stripe.com/elements/appearance-api)
- [Vercel Design Guidelines](https://vercel.com/design/guidelines)
- [IxDF Form Design Guide 2026](https://ixdf.org/literature/article/ui-form-design)
- [PlatoForms 2025 Design Trends](https://www.platoforms.com/blog/web-design-insights-for-online-form/)
- [Formester Design Trends 2025](https://formester.com/blog/website-and-form-design-trends/)
- [Balenciaga Normcore Website](https://econsultancy.com/luxury-ecommerce-review-is-balenciaga-s-normcore-website-more-than-a-gimmick/)
- [Luxury Fashion Website Design](https://mediaboom.com/news/luxury-fashion-website-design/)
- [Japanese Minimalism in UI](https://fireart.studio/blog/japanese-minimalism-in-ui-design-for-digital-products/)
- [Japanese Web Design Features](https://designmodo.com/japanese-web-design/)
- [FreeFrontend CSS Input Examples](https://freefrontend.com/css-input-text/)
- [FreeFrontend CSS Toggle Switches](https://freefrontend.com/css-toggle-switches/)
- [CSS-Tricks Custom Focus Styles](https://css-tricks.com/having-a-little-fun-with-custom-focus-styles/)
- [Search Bar Examples](https://www.eleken.co/blog-posts/search-bar-examples)
- [Dark Mode Input States](https://medium.com/@nasir-ahmed03/input-field-states-for-light-dark-mode-04b8b1b9880e)
- [Dark Mode Best Practices](https://uxcel.com/blog/12-principles-of-dark-mode-design-627)
- [shadcn/ui Theming](https://ui.shadcn.com/docs/theming)
- [Material vs Flat Design](https://designmodo.com/flat-vs-material/)
- [Floating Label CSS](https://css-tricks.com/float-labels-css/)
- [Border Radius Rules](https://blog.92learns.com/border-radius-rules/)
- [Textarea Resize CSS](https://css-tricks.com/almanac/properties/r/resize/)
- [File Upload UI 2025](https://blog.filestack.com/building-modern-drag-and-drop-upload-ui/)
- [Apple HIG Inputs](https://developer.apple.com/design/human-interface-guidelines/inputs)
- [Headless UI vs Radix](https://www.subframe.com/tips/headless-ui-vs-radix)
- [uiCookies CSS Input Designs](https://uicookies.com/css-input-text/)
- [Search UX Best Practices 2026](https://www.designstudiouiux.com/blog/search-ux-best-practices/)
- [Error States UX 2025](https://medium.com/design-bootcamp/designing-effective-error-states-turning-frustration-into-opportunity-in-2025-ux-998e5dc204fc)