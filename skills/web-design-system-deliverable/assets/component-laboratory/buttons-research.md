# Buttons Research

I now have substantial research across all 10 areas. Let me compile the findings.

---

Here is my comprehensive research on counterintuitive, non-generic button design approaches from the world's best designers.

---

## 1. THE PREMIUM PRODUCT COMPANIES (Linear, Vercel, Stripe, Raycast, Notion, Apple)

### Apple — The "No Button" Button
Apple's approach is the most radical departure from convention. Their homepage CTAs are **plain text links with no button container whatsoever** — no background fill, no border, no outline. "Learn more" and "Buy" appear as standard-weight, sentence-case text with a right-pointing chevron arrow (>). Primary vs secondary distinction is achieved purely through **layout position**, not visual weight. Apple's design guideline states the title's font size should be **43% of the button's height**, and they recommend a border-radius of **30% of the button's height** when they do use containers. The new CSS `corner-shape: squircle` property (Chrome M139+) replicates their signature continuous corner curve — `superellipse(2)` — which is visually distinct from regular `border-radius`.

### Linear — Dark Theme Precision
Linear uses an **8px spacing scale** (8, 16, 32, 64) with styled-components on top of Radix primitives. Their internal design system "Orbiter" isn't public, but analysis shows: `border-radius: 24px` (full pill), `padding: 10px 24px`, `font-size: 1rem`, `font-weight: bold`. They avoid box-shadows on buttons entirely — subtle shadows appear only on containing cards (`box-shadow: 0 4px 12px rgba(0,0,0,0.04)`). They use the LCH color space for theme generation.

### Vercel / Geist — The Ghost Primary
Vercel's design system Geist has five button types: default, secondary, tertiary, error, warning. The **secondary ghost button with a 1px border is actually the most common** — not a filled primary. Their icon-only variant requires `svgOnly` prop + `aria-label`. The `shape="rounded"` variant produces pills. Sizes map to standard Tailwind-like values. Their approach prioritizes text-only links with right arrows ("More about Infrastructure >") for most navigation.

### Stripe — Sentence Case, Paired CTAs
Stripe uses **sentence case** throughout (not title case, not uppercase). Their primary CTA "Start now" uses a solid fill; secondary "Contact sales" uses outline/ghost treatment. Most content CTAs ("Read the story", "Watch video", "Read more") are **text links without any button chrome**. Their famous gradient background uses WebGL (minigl), not CSS — with colors `#6ec3f4`, `#3a3aff`, `#ff61ab`, `#E63946`.

### Notion — Arrow as Affordance
Notion uses the right arrow character (→) as a universal signifier for clickability. "See what's new→", "Explore more→", "Try it→". This replaces button chrome entirely. Their filled buttons ("Get Notion free") appear only for the single highest-priority action. Everything else is a text link with an arrow. Title case throughout.

### Raycast — Dark Theme, Icon+Text
On their dark background (`#070921`), buttons use icon + text combinations with solid fills. The "Download for Mac" CTA pairs a platform icon with descriptive text. Secondary actions are pure text links. Accent colors (purples, blues, greens) appear as glows on extension cards, not on buttons themselves.

---

## 2. LUXURY FASHION — THE TEXT-ONLY EXTREME

### Celine
Uses **Neue Haas Grotesk Display** (weight 700) and **Neue Haas Grotesk Text** (weights 400/700). Navigation in ALL CAPS (brand identity — they dropped the accent from Céline). CTAs like "EXPLORE" are **text links, not buttons**. No borders, no fills, no underlines. The page is monochromatic. Interactive elements are differentiated purely by typography weight and position.

### Acne Studios
Uses **Helvetica Now Text** and **Helvetica Now Micro**. CTAs in title case ("View all", "Shop now", "Add to bag") with zero button chrome — they integrate into the layout as text. Implements `data-speculation-prefetch` for predictive loading, making transitions feel instant. The luxury approach: **the absence of a button IS the design**.

### Balenciaga
Their site (designed by Bureau Borsche) resembles a wireframe. Sans-serif, extremely simplified interface where each block contains just one word. Brutalist-adjacent: spartan, mono-spaced, industrial. Buttons are essentially just words on a page.

### Pattern
Luxury fashion sites use **text buttons** — "presented with a piece of text without integration into any shape, filled tab, or anything." The copy is its only visual presenter. This supports "general light and minimalistic style" where only ONE main CTA gets button treatment; everything else is type only.

---

## 3. EDITORIAL SITES (NYT, Bloomberg, Guardian)

The Guardian has a full design system at design.theguardian.com. Bloomberg's redesign features different nav interaction patterns — some triggered by hover, others by click, with visible style differences between them. The NYT uses arrow elements (`<div class="arrow arrow-right">`) in menu navigation. Editorial sites generally avoid colorful button fills in favor of **typographic hierarchy and underlines** for affordance.

---

## 4. UNUSUAL HOVER ANIMATIONS (Not Color Shift or Scale)

### Magnetic Buttons
The button translates toward the cursor. Implementation:
- **GSAP**: `gsap.quickTo(element, "x", {duration: 1, ease: "elastic.out(1, 0.3)"})` — the elastic easing with parameters `(1, 0.3)` creates a springy return
- **Framer Motion**: `type: "spring"`, `stiffness: 150`, `damping: 15`, `mass: 0.1`
- Distance calculation: `x = clientX - (left + width/2)`, then multiply by ~0.4 for attraction strength
- Child elements can have different movement multipliers for **parallax within the button**

### Clip-Path Morphing (Codrops "Janus Button")
Animates between two SVG path definitions on `::before` pseudo-element. Uses bouncy cubic-bezier: `cubic-bezier(0.585, 2.5, 0.645, 0.55)`. Background shifts light-to-dark simultaneously.

### Mix-Blend-Mode Text
Button text animates vertically via `transform: translate3d(0,-10px,0)` while `mix-blend-mode: difference` creates contrast-based visual interaction with the background.

### Sliding Text Replacement
Text slides out downward while new text (or same text in different color) slides in from top. The Framer "Button Hover Shift" component: text slides left while icon moves right.

### Rotating SVG Text Path
Text embedded along a circular SVG path that rotates on interaction — a "badge" effect.

---

## 5. BRUTALIST / NEO-BRUTALIST BUTTONS

Exact CSS values from multiple sources:

**Standard neo-brutalist recipe:**
- `border: 2-3px solid #000`
- `box-shadow: 4px 4px 0px 0px #000` (hard offset, zero blur)
- `border-radius: 0` (never rounded)
- `padding: 1rem 2rem`
- `font-weight: bold` or `700`
- `font-size: 1.5rem`
- No gradients ever

**Tailwind equivalents (NeoBrutalismCSS library):**
- `nb-shadow`: 2px offset
- `nb-shadow-lg`: 4px offset
- `nb-shadow-xl`: 6px offset
- `nb-border`: 2px
- `nb-border-lg`: 3px
- `nb-border-xl`: 4px

**Hover state:** The shadow offset changes (typically reduces to 2px 2px or 0px 0px) while the button translates by the difference (`transform: translate(2px, 2px)`), creating a "press down" tactile effect.

**Active state:** Shadow goes to 0, button translates the full shadow distance.

---

## 6. JAPANESE DESIGN

Japanese web design favors: simple and unobtrusive menus and buttons, often hamburger icons or minimal labeled navigation links. **Delicate typography and ghost buttons** are characteristic. The principle of **MA** (gap/space/pause) — love of the space between things, not things themselves — drives button design toward maximum negative space and minimal visual weight. Fanfanfan Design Studio won Awwwards recognition for their circle hover animation with reactive cursor microinteraction.

---

## 7. THE SQUIRCLE — APPLE'S SHAPE LANGUAGE

The new CSS `corner-shape` property (Chrome M139+, June 2025):
```css
.button {
  border-radius: 40px;
  corner-shape: squircle; /* equivalent to superellipse(2) */
}
```
This produces **continuous corners** — the curve never has an abrupt transition from straight edge to arc. Apple's iOS uses a corner smoothing value of 60. You can apply different shapes per corner: `corner-shape: bevel squircle squircle bevel;`

Other values: `round` (default), `scoop` (concave), `bevel` (straight cut), `notch` (inward), `square`.

---

## 8. ELEGANT LOADING STATES (Not Spinners)

**Morphing Submit Button:** Starts as "Submit" text. On click, the button container morphs (width shrinks to a circle), a progress ring draws itself using `stroke-dasharray` / `stroke-dashoffset` on an SVG circle, then the ring morphs into a checkmark polyline.

**Progress Fill:** The button itself acts as a progress bar — a `::before` pseudo-element with `width` animating from 0% to 100% in the button's background color at reduced opacity.

**Text State Machine:** Button text transitions through states: "Submit" → (fade out) → "Sending..." → (fade out) → "Done ✓" with each transition being a Y-axis translate + opacity animation.

---

## 9. ICON-ONLY BUTTONS AT HIGH END

Standard pattern: **24px icon inside a 44px touch target** (WCAG 2.5.5). The visual element stays small; padding extends the hit area. Minimum 10px between adjacent touch targets. Android recommends 48px targets. shadcn/ui's icon button: `h-10 w-10` (40x40px). Vercel's Geist uses `svgOnly` prop that strips padding and requires `aria-label`.

---

## 10. SPECIFIC REFERENCE VALUES (shadcn/ui as baseline)

Since shadcn/ui has become the de facto standard:
- **Default**: height 40px, padding 16px horizontal / 8px vertical
- **Small**: height 36px, padding 12px horizontal
- **Large**: height 44px, padding 32px horizontal
- **Icon**: 40x40px square
- **Border-radius**: `rounded-md` = 6px (0.375rem)
- **Font**: `text-sm` (14px), `font-medium` (500)
- **Focus ring**: 2px ring, 2px offset
- **Disabled**: `opacity: 50%`, `pointer-events: none`

### CTA Button Golden Ratios
- **Border-radius**: ~30% of button height
- **Horizontal padding**: ~50% of button height
- **Drop shadow Y-offset**: 30% of button height
- **Drop shadow blur**: 50% of button height
- **Hover brightness shift**: ~10%
- **Font size to height ratio** (Apple guideline): 43%

---

## THE COUNTERINTUITIVE TAKEAWAYS

1. **The highest-end sites use the fewest buttons.** Apple, Celine, Acne Studios rely on text links. The button IS the text.
2. **Sentence case outperforms uppercase** at the premium end. Only luxury fashion uses all-caps (and that's brand identity, not UI convention).
3. **The right-arrow character (→ or >) has replaced button chrome** as the primary affordance signifier at Notion, Apple, and Vercel.
4. **Ghost/outline is the default, not the secondary.** Vercel's most-used button is the bordered ghost, not a filled primary.
5. **Magnetic hover (button follows cursor) is the current premium hover pattern** — not color shift, not scale. GSAP `elastic.out(1, 0.3)` with 1s duration.
6. **Zero blur box-shadow (neo-brutalist)** and **zero chrome text-only (luxury minimal)** are the two extremes — both more interesting than the filled rounded-rect middle.
7. **Squircle corners** via `corner-shape: squircle` are the next shape evolution beyond `border-radius`.
8. **Loading states should morph the button shape**, not overlay a spinner on it.

Sources:
- [Linear UI Redesign](https://linear.app/now/how-we-redesigned-the-linear-ui)
- [Linear Design UI Libraries](https://blog.logrocket.com/ux-design/linear-design-ui-libraries-design-kits-layout-grid/)
- [CTA Button Design Best Practices - LogRocket](https://blog.logrocket.com/ux-design/cta-button-design-best-practices/)
- [Codrops CSS Button Hover Animations](https://tympanus.net/codrops/2021/02/17/ideas-for-css-button-hover-animations/)
- [Codrops Magnetic Buttons](https://tympanus.net/codrops/2020/08/05/magnetic-buttons/)
- [Magnetic Button Tutorial - Olivier Larose](https://blog.olivierlarose.com/tutorials/magnetic-button)
- [CSS corner-shape - Frontend Masters](https://frontendmasters.com/blog/understanding-css-corner-shape-and-the-power-of-the-superellipse/)
- [Neo-Brutalism UI Library](https://neo-brutalism-ui-library.vercel.app/components/button)
- [Neobrutalism CSS Examples](https://freefrontend.com/css-neobrutalism/)
- [Ghost Button Design - Smashing Magazine](https://www.smashingmagazine.com/2018/01/ghost-button-design/)
- [Ghost Buttons - Webflow](https://webflow.com/blog/ghost-buttons)
- [Japanese Web Design Features - DesignModo](https://designmodo.com/japanese-web-design/)
- [Luxury Fashion Website Design - Mediaboom](https://mediaboom.com/news/luxury-fashion-website-design/)
- [Brutalism in Web Design - DesignMantic](https://www.designmantic.com/blog/brutalism-in-web-design/)
- [Awwwards Creative Button Styles](https://www.awwwards.com/inspiration/creative-button-styles)
- [Awwwards Japan Websites](https://www.awwwards.com/websites/Japan/)
- [Pentagram Website - AREA 17](https://area17.com/work/pentagram-website)
- [Vercel Geist Button](https://vercel.com/geist/button)
- [shadcn/ui Button](https://ui.shadcn.com/docs/components/radix/button)
- [Sliding Button Hover - Framer University](https://framer.university/resources/sliding-button-hover-animation-in-framer)
- [Codrops Progress Button Styles](https://tympanus.net/codrops/2013/12/12/progress-button-styles/)
- [2026 UI Design Trends - MuseMind](https://musemind.agency/blog/ui-design-trends)