---
name: stereo-design-system
description: Skeuomorphic design system inspired by high-end stereo receivers and hi-fi equipment. Brushed brass controls, warm amber displays, dark chassis panels. Use when (1) building a skeuomorphic or retro-hardware UI, (2) creating audio/music/media player interfaces, (3) designing dashboards or control panels with physical-world metaphors, (4) user asks for a "stereo", "hi-fi", "receiver", "analog", "vintage hardware", or "brushed metal" aesthetic, (5) building dark warm interfaces with brass/gold accents and tactile controls.
---

# Stereo Design System

Skeuomorphic component system inspired by high-end stereo receivers. Pure CSS — no images required. All textures achieved through layered gradients.

## Design Principles

1. **Physical metaphor** — every element references real hardware (machined brass, etched metal, backlit displays)
2. **Warm palette** — dark brown/charcoal chassis, brushed brass controls, warm amber indicators
3. **Consistent lighting** — single overhead light source from top-left, all specular highlights at ~10 o'clock
4. **Tactile depth** — panels have brushed texture and beveled edges, controls cast shadows, indicators glow
5. **Sans-serif only** — system font stack throughout, no monospace or serif
6. **Etched, not painted** — position indicators and labels look stamped into the panel surface

## Color Tokens

```css
/* Brass palette — brushed/satin finish */
--brass-light: #c0a050;
--brass-mid: #a08838;
--brass-dark: #7a6828;
--brass-shadow: #54481a;
--brass-highlight: #d0b860;
--brass-shine: #ddc878;

/* Chassis */
--chassis-bg: #181715;
--chassis-surface: #24221e;
--chassis-border: #332f28;
--chassis-inset: #100f0d;
--chassis-text: #8a8a90;
--chassis-text-light: #b0b0b6;

/* Indicators */
--led-green: #4aff6a;
--led-red: #ff4a4a;
--led-amber: #ffaa2a;

/* Active/On state accent */
--active-amber: #e8a020;
--active-label: #d0a030;
```

## Components

### Rotary Knobs
Cylindrical flat-front brass knobs with:
- Circular brushed texture via `repeating-conic-gradient`
- Edge darkening via `radial-gradient` (flat center, dark rim = cylindrical)
- **Separate gloss overlay** (`.knob-gloss` div) — stays fixed when knob rotates
- Position indicator line (dark groove, not painted)
- Etched tick marks on panel surface (lighter than panel, not black: `#3a3630` / `#48423a`)
- Sizes: standard (100px), small (64px), custom via inline styles

### Toggle Switches
Vertical and horizontal (rocker) variants:
- Recessed plate with illuminated brass border (`rgba(160,136,56,0.25)`)
- Brass toggle with specular highlight
- On state label: warm amber `#d0a030` (not green)

### Fader/Slider Controls
Blocky brass thumbs (2px border-radius) with:
- Top-face specular gradient
- Horizontal brushed texture
- Center groove detail
- Lit track fill (brass gradient)

### VU Meters
Dark-face analog meters:
- Background: warm dark vignette (`#2a2218` → `#100c08`)
- Amber/gold scale numbers with subtle glow
- Gold-to-red gradient needle
- Dark brass bezel (3-ring shadow)

### LED Indicators
Brass-bezeled indicator lights:
- Green, amber, red variants
- On state: radial gradient with glow bloom via `box-shadow`
- Off state: dark muted version of same hue

### Display/Readout
Backlit amber displays:
- Dark warm background (`#0c0a06` → `#080602`)
- Amber text `#e8a020` with glow halo
- Scanline overlay effect
- Dark brass bezel (3-ring)
- Sans-serif font

### Source Selector Buttons
Recessed button group:
- 2×2 grid layout
- Illuminated border on active state
- Brass glow on selection

### Panels
Dark warm chassis panels:
- Brushed horizontal texture (repeating-linear-gradient at 0.8% opacity)
- Diagonal grain (second gradient at 127°)
- Overhead light gradient (lighter top, darker bottom)
- Beveled edges (bright top border, inner highlight top/left, shadow bottom)
- Corner radius: 5px

## Key Techniques

### Brushed Metal Texture (CSS only)
```css
/* Circular brushed (for knobs) */
repeating-conic-gradient(from 0deg,
  rgba(255,255,255,0.04) 0deg,
  rgba(0,0,0,0.02) 0.4deg,
  transparent 0.8deg, transparent 1.2deg)

/* Linear brushed (for panels) */
repeating-linear-gradient(180deg,
  rgba(255,255,255,0.008) 0px,
  transparent 1px, transparent 2px)
```

### Specular Highlight (rotation-safe)
Gloss is a **separate overlay div** (not part of the knob background) so it stays fixed when the knob rotates:
```html
<div class="knob-container">
  <div class="knob pos-mid"></div>
  <div class="knob-gloss"></div>  <!-- stays fixed -->
</div>
```
```css
.knob-gloss {
  position: absolute;
  inset: 14px; /* match knob inset */
  border-radius: 50%;
  pointer-events: none;
  z-index: 2;
  background:
    radial-gradient(ellipse 60% 50% at 32% 28%,
      rgba(255,248,220,0.55) 0%,
      rgba(255,240,200,0.25) 25%, transparent 60%),
    radial-gradient(ellipse 40% 35% at 70% 72%,
      rgba(255,240,200,0.08) 0%, transparent 50%);
}
```

### Etched Position Indicators
```css
/* Lighter than panel surface, not black */
background: #3a3630;
box-shadow: 0 1px 0 rgba(255,248,220,0.06); /* light edge = stamped feel */
```

### Illuminated Button Bezel
```css
border: 1px solid rgba(160,136,56,0.25);
box-shadow: 0 0 4px rgba(160,136,56,0.1),
            0 -1px 0 rgba(208,184,96,0.15);
```

## Page Background
Warm radial vignette (not flat):
```css
background: radial-gradient(
  ellipse 70% 60% at 50% 35%,
  #22201c 0%, #1a1816 30%, #121110 60%, #0a0908 100%);
```

## Reference Implementation
Full working showcase with all components: `assets/showcase.html`
- Interactive: clickable switches, source selector, animated VU needles
- Mobile responsive (breakpoints at 680px and 480px)
- Zero dependencies, single HTML file
