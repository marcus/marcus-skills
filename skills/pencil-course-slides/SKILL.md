# Pencil Course Slide Design System

Create visually distinctive 1920x1080 course slides using the Pencil design tool MCP. The system provides reusable components as a starting point, but **visual variety is the priority** — every slide should feel intentionally designed for its content, not stamped from a template.

## Tags
`pencil`, `slides`, `design`, `course`, `avalara`, `diagrams`, `charts`

## When to Use
- Creating course slide images for the bootcamp project
- Any 16:9 slide/diagram that needs crisp text, proper layout, and brand colors
- When you have the Pencil MCP server configured

## Prerequisites
- Pencil MCP server must be configured and running
- The .pen design file with components must be open (see Setup below)

---

## IMPORTANT: Creative Direction

**The reusable components below are a floor, not a ceiling.** Using them for every slide produces homogeneous results — identical card borders, same teal-on-dark palette, same rounded rectangles. That's the failure mode to avoid.

### When to break from templates

At least half of the slides you create should go beyond the component library. Ask yourself: does this slide's concept have a visual metaphor worth showing? If yes, build it custom.

### Techniques for visual variety

**1. AI-generated backgrounds with `G()`**
The most impactful change. Create a full-bleed 1920x1080 frame, generate an image into it at **0.35–0.45 opacity** (dark theme) or **0.20–0.30 opacity** (light theme), then overlay content on top. The vignette gradient overlay already dims edges significantly, so the background image needs to be visible enough to matter. Write prompts that match the slide's *concept*, not its literal content.

```javascript
slide=I(document,{type:"frame",name:"Slide Name",x:X,y:Y,width:1920,height:1080,layout:"none",fill:"#080c14",placeholder:true})
bgImg=I(slide,{type:"frame",name:"bg",x:0,y:0,width:1920,height:1080,opacity:0.40})
G(bgImg,"ai","tectonic plates splitting apart, deep ocean blue, glowing orange fracture line, cinematic lighting, 16:9")
// Add gradient overlay for text legibility:
overlay=I(slide,{type:"frame",x:0,y:0,width:1920,height:1080,fill:{type:"gradient",gradientType:"radial",colors:[{color:"#080c1200",position:0},{color:"#080c14",position:0.85}],size:{width:1.6,height:1.6}}})
// Then add text content on top...
```

Good prompt themes by slide concept:
- Shift/change → tectonic plates, metamorphosis, phase transitions
- Architecture/structure → blueprints, circuit boards, engineering schematics
- Growth/scaling → aerial city views, fractal patterns, root systems
- Security/boundaries → vaults, containment fields, fortress walls
- Experimentation → laboratories, particle trails, chemical reactions

**2. Custom composition instead of symmetric layouts**
Don't default to two equal columns or a centered list. Try:
- Asymmetric splits — one side faded/small, the other bold/large
- Absolute positioning (`layout:"none"`) with elements at intentional coordinates
- Numbered badges instead of identical bullet dots
- Strikethrough lines over deprecated items
- Glowing dividers with `effect` shadows instead of plain rectangles

**3. Vary the color treatment**
- Use hardcoded colors outside the brand palette for accents: `#22c55e` (green for success), `#ef4444` (red for warnings), `#8b5cf6` (purple for creative)
- Vary opacity: faded text at `#5a708099` for de-emphasized content, full white `#f0f4f8` for emphasis
- Gradient fills on panels: `{type:"gradient",gradientType:"linear",colors:[{color:"#0f2030",position:0},{color:"#152a3d",position:1}],rotation:180}`
- Glassmorphism panels: translucent fill (`#0a1a2888`) + `effect:{type:"background_blur",radius:12}` + thin border

**4. Add visual narrative flow**
If the slide tells a story (input → process → output), build it as a visual flow with distinct styled boxes connected by arrows, not just text. Use different fill colors per stage to show progression.

### The creative test

Before exporting any slide, screenshot it and compare it mentally to the other slides in the deck. If it could be mistaken for a different slide with different text swapped in, it needs more visual differentiation.

---

## Setup

### 1. Open the Design File

The design system lives in the currently active Pencil document. If starting fresh, you need to open it:

```
pencil-open_document({ filePathOrTemplate: "/Users/marcus.vorwaller@avalara.com/code/bootcamp/course/design/slides.pen" })
```

If no .pen file exists yet, create a new document and build the components from the Component Reference below.

### 2. Verify Components Are Available

```
pencil-get_editor_state({ include_schema: false })
```

You should see these reusable components listed:
- `yp0ST` — **SlideTemplate** (1920x1080 dark slide frame)
- `ipNEj` — **BarSegment** (colored bar with label + percentage)
- `WYNRm` — **LegendItem** (color dot + label)
- `0wSif` — **ProcessStep** (rounded box for flowcharts)
- `SSGdt` — **FlowArrow** (arrow-right icon connector)
- `GZniz` — **TColumn** (column with heading, divider, body slot)
- `uE48a` — **BulletItem** (dot + text for lists)
- `k0pMA` — **KPICard** (metric label, big number, context)
- `I9kNZ` — **StackLayer** (horizontal bar for layer diagrams)
- `8hpSA` — **MatrixCell** (quadrant with title + description)
- `aSpSl` — **ChecklistItem** (check icon + text)

### 3. Design Variables (Brand Colors)

These are already set in the .pen file:

| Variable | Dark | Light | Usage |
|----------|------|-------|-------|
| `$bg-dark` | `#0d1117` | `#f8f9fb` | Slide background |
| `$bg-card` | `#1a2a34` | `#ffffff` | Card/panel backgrounds |
| `$orange` | `#fc6600` | `#fc6600` | Primary accent, highlights |
| `$teal` | `#059bd2` | `#0284a8` | Secondary accent, borders |
| `$navy` | `#025979` | `#03719b` | Tertiary color |
| `$text-primary` | `#f0f4f8` | `#1a1a2e` | Main text |
| `$text-muted` | `#a0b8c8` | `#5a6a7a` | Secondary text |
| `$text-dim` | `#5a7080` | `#94a3b8` | Subtle text, footers |
| `$text-on-accent` | `#ffffff` | `#ffffff` | Text on colored bars |
| `$card-stroke` | `#059bd2` | `#d0d8e0` | Card/step borders |

---

## Workflow: Creating a Slide

Every slide follows the same 4-step pattern:

### Step 1: Find Empty Space

```javascript
pencil-find_empty_space_on_canvas({
  direction: "bottom",  // or "right"
  width: 1920,
  height: 1080,
  padding: 100,
  nodeId: "lastSlideId"  // optional: relative to existing slide
})
```

### Step 2: Insert Slide Template Instance

```javascript
// In batch_design:
slide=I(document,{type:"ref",ref:"yp0ST",name:"Slide Name",x:X,y:Y,placeholder:true})
U(slide+"/IEPR5",{content:"Slide Title Here"})
```

### Step 3: Replace the Body Slot with Content

The slide body (`QJD7y`) is a slot. Replace it with your content layout:

```javascript
body=R(slide+"/QJD7y",{type:"frame",layout:"horizontal",width:"fill_container",height:"fill_container",gap:40,justifyContent:"center",alignItems:"center"})
// Then add content into body...
```

### Step 4: Remove Placeholder & Export

```javascript
U("slideId",{placeholder:false})
```

Then export:
```
pencil-export_nodes({
  nodeIds: ["slideId"],
  outputDir: "/path/to/course/public/images",
  format: "webp",
  scale: 1
})
```

Rename the exported file (it uses the node ID as filename):
```bash
mv slideId.webp descriptive-name.webp
```

---

## Theming: Light and Dark Mode

The design system supports `dark` and `light` themes via a `mode` theme axis. All variables are theme-aware (except `$orange` and `$text-on-accent`, which are the same in both).

**Creating a dark slide (default):** No theme override needed. The default theme is dark.

**Creating a light slide:** Set `theme:{"mode":"light"}` on the slide instance:

```javascript
slide=I(document,{type:"ref",ref:"yp0ST",name:"Slide Name",x:X,y:Y,theme:{"mode":"light"},placeholder:true})
```

**Copying an existing dark slide as light:**

```javascript
lightCopy=C("darkSlideId",document,{name:"Slide Name (Light)",positionDirection:"right",positionPadding:100,theme:{"mode":"light"}})
```

**CRITICAL:** All color fills MUST use variable references (`$bg-dark`, `$text-primary`, etc.), NOT hardcoded hex values. Hardcoded hex values will NOT respond to theme changes.

You can export dark and light versions of the same slide content by copying with different themes.

---

## Component Reference (Starting Points, Not Mandates)

These components speed up common patterns. Use them when they genuinely fit — but don't force a concept into a component just because the component exists. For slides with strong visual metaphors, build custom frames from scratch with `layout:"none"` and AI-generated backgrounds.

### SlideTemplate (`yp0ST`)

The master slide frame. All slides should be instances of this.

**Structure:**
```
SlideTemplate (1920x1080, $bg-dark, vertical layout, padding [80,120])
├── slide-title (IEPR5) — text, 56px, bold, $text-primary
├── slide-body (QJD7y) — frame slot, fill_container, vertical layout
└── slide-footer (GarGy) — text, 18px, $text-dim
```

**Override points:**
- `IEPR5` — Change title text: `U(instance+"/IEPR5",{content:"New Title"})`
- `QJD7y` — Replace body with content: `R(instance+"/QJD7y",{type:"frame",...})`
- `GarGy` — Add footer text: `U(instance+"/GarGy",{content:"footnote"})`

---

### BarSegment (`ipNEj`)

A colored bar for stacked/grouped bar charts.

**Structure:**
```
BarSegment (280x200, $orange, rounded, vertical center)
├── bar-label (xQJn4) — text, 28px, bold, $text-on-accent
└── bar-pct (oVI56) — text, 48px, extra-bold, $text-on-accent
```

**Override points:**
- `xQJn4` — Label text: `U(instance+"/xQJn4",{content:"Implementation"})`
- `oVI56` — Percentage: `U(instance+"/oVI56",{content:"85%"})`
- Root — Color & size: `{fill:"$teal", width:320, height:400}`

**Usage pattern (stacked bar column):**
```javascript
col=I(body,{type:"frame",layout:"vertical",width:320,height:"fill_container",gap:0,alignItems:"center",justifyContent:"end"})
seg1=I(col,{type:"ref",ref:"ipNEj",width:320,height:240,fill:"$teal"})
U(seg1+"/xQJn4",{content:"Framing"})
U(seg1+"/oVI56",{content:"50%"})
seg2=I(col,{type:"ref",ref:"ipNEj",width:320,height:50,fill:"$orange"})
// For small segments, hide the pct and use a compact label:
U(seg2+"/xQJn4",{content:"Impl. 10%",fontSize:16})
U(seg2+"/oVI56",{content:"",enabled:false})
colLabel=I(col,{type:"text",content:"Now",fontSize:32,fill:"$text-primary",fontWeight:"600"})
```

---

### LegendItem (`WYNRm`)

Color swatch + label for chart legends.

**Structure:**
```
LegendItem (180x24, horizontal, center-aligned)
├── legend-dot (QsxhT) — rectangle 16x16, $orange, rounded
└── legend-text (s0MVC) — text, 20px, $text-muted
```

**Override points:**
- `QsxhT` — Color: `U(instance+"/QsxhT",{fill:"$teal"})`
- `s0MVC` — Label: `U(instance+"/s0MVC",{content:"Framing"})`

**Usage pattern (legend row):**
```javascript
legend=I(body,{type:"frame",layout:"horizontal",gap:48,justifyContent:"center",alignItems:"center"})
l1=I(legend,{type:"ref",ref:"WYNRm"})
U(l1+"/QsxhT",{fill:"$teal"})
U(l1+"/s0MVC",{content:"Framing"})
l2=I(legend,{type:"ref",ref:"WYNRm"})
U(l2+"/s0MVC",{content:"Implementation"})  // orange is default
```

---

### ProcessStep (`0wSif`)

A rounded box for flowchart nodes.

**Structure:**
```
ProcessStep (200x80, $bg-card, rounded-12, teal border)
└── step-label (ZsqP0) — text, 22px, semibold, $text-primary
```

**Override points:**
- `ZsqP0` — Step name: `U(instance+"/ZsqP0",{content:"Verify"})`
- Root — Highlight: `{fill:"$orange",stroke:{fill:"$orange",thickness:2}}`

---

### FlowArrow (`SSGdt`)

Arrow connector between process steps.

**Structure:**
```
FlowArrow (60x60, horizontal center)
└── arrow-icon (HCxFX) — lucide arrow-right, 32x32, $text-dim
```

**Override points:**
- `HCxFX` — Direction: `U(instance+"/HCxFX",{iconFontName:"arrow-down"})`

**Usage pattern (horizontal flow):**
```javascript
flowRow=R(slide+"/QJD7y",{type:"frame",layout:"horizontal",width:"fill_container",height:"fill_container",gap:8,justifyContent:"center",alignItems:"center"})
s1=I(flowRow,{type:"ref",ref:"0wSif"})
U(s1+"/ZsqP0",{content:"Frame"})
a1=I(flowRow,{type:"ref",ref:"SSGdt"})
s2=I(flowRow,{type:"ref",ref:"0wSif"})
U(s2+"/ZsqP0",{content:"Specify"})
a2=I(flowRow,{type:"ref",ref:"SSGdt"})
s3=I(flowRow,{type:"ref",ref:"0wSif",fill:"$orange",stroke:{fill:"$orange",thickness:2}})
U(s3+"/ZsqP0",{content:"Generate"})
```

---

### TColumn (`GZniz`)

A column panel for T-charts and comparison layouts.

**Structure:**
```
TColumn (400x500, $bg-card, rounded-16, vertical, padding 32)
├── tcol-heading (9aD1P) — text, 36px, bold, $orange
├── tcol-divider (VgIJq) — rectangle, fill_container x 2px, $text-dim
└── tcol-body (UguT2) — frame slot, fill_container, vertical, gap 16
```

**Override points:**
- `9aD1P` — Heading: `U(instance+"/9aD1P",{content:"Old Way",fill:"$text-muted"})`
- `UguT2` — Body slot: insert BulletItems or custom content

**Usage pattern (T-chart comparison):**
```javascript
cols=R(slide+"/QJD7y",{type:"frame",layout:"horizontal",width:"fill_container",height:"fill_container",gap:40,justifyContent:"center"})
left=I(cols,{type:"ref",ref:"GZniz",width:"fill_container",height:"fill_container"})
U(left+"/9aD1P",{content:"Before",fill:"$text-muted"})
right=I(cols,{type:"ref",ref:"GZniz",width:"fill_container",height:"fill_container"})
U(right+"/9aD1P",{content:"After",fill:"$orange"})

// Add bullets to left column:
b1=I("leftId/UguT2",{type:"ref",ref:"uE48a",width:"fill_container"})
U(b1+"/Nzqrm",{content:"Manual testing"})
```

---

### BulletItem (`uE48a`)

A dot + text item for lists within columns.

**Structure:**
```
BulletItem (360x36, horizontal, center-aligned)
├── bullet-dot (4nsin) — ellipse 8x8, $teal
└── bullet-text (Nzqrm) — text, 24px, $text-primary
```

**Override points:**
- `4nsin` — Dot color: `U(instance+"/4nsin",{fill:"$orange"})`
- `Nzqrm` — Text: `U(instance+"/Nzqrm",{content:"Your bullet text"})`

---

### KPICard (`k0pMA`)

A single-metric display card.

**Structure:**
```
KPICard (360x200, $bg-card, rounded-16, vertical center, padding 24)
├── kpi-label (IyZRt) — text, 20px, medium, $text-muted, tracking +2
├── kpi-value (LZff7) — text, 72px, extra-bold, $orange
└── kpi-context (lBhhG) — text, 20px, $text-dim
```

**Override points:**
- `IyZRt` — Label: `U(instance+"/IyZRt",{content:"REDUCTION"})`
- `LZff7` — Value: `U(instance+"/LZff7",{content:"10x"})`
- `lBhhG` — Context: `U(instance+"/lBhhG",{content:"in implementation time"})`

**Usage pattern (3 KPIs side by side):**
```javascript
kpiRow=R(slide+"/QJD7y",{type:"frame",layout:"horizontal",width:"fill_container",height:"fill_container",gap:40,justifyContent:"center",alignItems:"center"})
k1=I(kpiRow,{type:"ref",ref:"k0pMA",width:400})
U(k1+"/IyZRt",{content:"SPEED"})
U(k1+"/LZff7",{content:"10x"})
U(k1+"/lBhhG",{content:"faster iteration"})
k2=I(kpiRow,{type:"ref",ref:"k0pMA",width:400})
// ... customize k2
k3=I(kpiRow,{type:"ref",ref:"k0pMA",width:400})
// ... customize k3
```

---

### StackLayer (`I9kNZ`)

A horizontal bar for layer/stack architecture diagrams.

**Structure:**
```
StackLayer (600x80, $bg-card, rounded-8, teal border, horizontal space-between)
├── layer-label (GZbeO) — text, 24px, semibold, $text-primary
└── layer-desc (g1WsD) — text, 18px, $text-muted
```

**Override points:**
- `GZbeO` — Name: `U(instance+"/GZbeO",{content:"Context Reduction"})`
- `g1WsD` — Desc: `U(instance+"/g1WsD",{content:"The highest-ROI layer"})`
- Root — Highlight: `{fill:"$orange",stroke:{fill:"$orange",thickness:2}}`

**Usage pattern (4-layer stack):**
```javascript
stack=R(slide+"/QJD7y",{type:"frame",layout:"vertical",width:"fill_container",height:"fill_container",gap:12,justifyContent:"center",alignItems:"center"})
l1=I(stack,{type:"ref",ref:"I9kNZ",width:800})
U(l1+"/GZbeO",{content:"Orchestration"})
U(l1+"/g1WsD",{content:"Multi-agent coordination"})
l2=I(stack,{type:"ref",ref:"I9kNZ",width:800})
U(l2+"/GZbeO",{content:"Verification"})
// ... highlight one layer:
l3=I(stack,{type:"ref",ref:"I9kNZ",width:800,fill:"$orange",stroke:{fill:"$orange",thickness:2}})
U(l3+"/GZbeO",{content:"Context Reduction"})
U(l3+"/g1WsD",{content:"Highest ROI"})
```

---

### MatrixCell (`8hpSA`)

A quadrant cell for 2x2 decision matrices.

**Structure:**
```
MatrixCell (360x240, $bg-card, rounded-12, vertical center, padding 24)
├── cell-title (9n51H) — text, 28px, bold, $text-primary
└── cell-desc (NWO5W) — text, 20px, $text-muted, fixed-width 312, center-aligned
```

**Override points:**
- `9n51H` — Title: `U(instance+"/9n51H",{content:"Build a Tool"})`
- `NWO5W` — Description: `U(instance+"/NWO5W",{content:"Repeated, context-heavy tasks"})`
- Root — Highlight: `{fill:"$orange",stroke:{fill:"$orange",thickness:2}}`

**Usage pattern (2x2 matrix):**
```javascript
matrix=R(slide+"/QJD7y",{type:"frame",layout:"vertical",width:"fill_container",height:"fill_container",gap:16,justifyContent:"center",alignItems:"center"})
topRow=I(matrix,{type:"frame",layout:"horizontal",gap:16,justifyContent:"center"})
c1=I(topRow,{type:"ref",ref:"8hpSA",fill:"$orange"})
U(c1+"/9n51H",{content:"Build a Tool"})
U(c1+"/NWO5W",{content:"Repeated + Context-heavy"})
c2=I(topRow,{type:"ref",ref:"8hpSA"})
// ...
bottomRow=I(matrix,{type:"frame",layout:"horizontal",gap:16,justifyContent:"center"})
c3=I(bottomRow,{type:"ref",ref:"8hpSA"})
// ...
// Add axis labels as text nodes
```

---

### ChecklistItem (`aSpSl`)

A check icon + text for checklist/spec slides.

**Structure:**
```
ChecklistItem (500x44, horizontal, center-aligned)
├── check-icon (Qkjrz) — lucide circle-check, 28x28, $teal
└── check-text (3D59S) — text, 24px, $text-primary
```

**Override points:**
- `3D59S` — Text: `U(instance+"/3D59S",{content:"Clear goal statement"})`
- `Qkjrz` — Different icon: `U(instance+"/Qkjrz",{iconFontName:"alert-circle",fill:"$orange"})`

**Usage pattern (checklist):**
```javascript
list=R(slide+"/QJD7y",{type:"frame",layout:"vertical",width:"fill_container",height:"fill_container",gap:20,justifyContent:"center",alignItems:"center"})
c1=I(list,{type:"ref",ref:"aSpSl",width:600})
U(c1+"/3D59S",{content:"Clear goal statement"})
c2=I(list,{type:"ref",ref:"aSpSl",width:600})
U(c2+"/3D59S",{content:"Architecture decisions documented"})
```

---

## Slide Recipes (For Component-Based Slides)

Use these when the content genuinely maps to a chart, matrix, or list. For conceptual or narrative slides, prefer the custom techniques from the Creative Direction section above.

### Recipe: Stacked Bar Chart

```javascript
// Step 1: Create slide
slide=I(document,{type:"ref",ref:"yp0ST",name:"Bar Chart",x:X,y:Y,placeholder:true})
U(slide+"/IEPR5",{content:"Time Allocation: Before vs. Now"})

// Step 2: Chart area with two columns
chartArea=R(slide+"/QJD7y",{type:"frame",layout:"horizontal",width:"fill_container",height:"fill_container",gap:200,justifyContent:"center",alignItems:"end"})

// Step 3: Before column (bottom-aligned, segments stack upward)
beforeCol=I(chartArea,{type:"frame",layout:"vertical",width:320,height:"fill_container",gap:0,alignItems:"center",justifyContent:"end"})
// Small segment:
bTop=I(beforeCol,{type:"ref",ref:"ipNEj",width:320,height:35,fill:"$teal"})
U(bTop+"/xQJn4",{content:"Framing 5%",fontSize:16})
U(bTop+"/oVI56",{enabled:false})
// Large segment:
bMid=I(beforeCol,{type:"ref",ref:"ipNEj",width:320,height:380,fill:"$orange"})
U(bMid+"/xQJn4",{content:"Implementation"})
U(bMid+"/oVI56",{content:"85%"})
// Bottom segment:
bBot=I(beforeCol,{type:"ref",ref:"ipNEj",width:320,height:60,fill:"$navy"})
U(bBot+"/xQJn4",{content:"Verification 10%",fontSize:16})
U(bBot+"/oVI56",{enabled:false})
// Column label:
bLabel=I(beforeCol,{type:"text",content:"Before",fontSize:32,fill:"$text-muted",fontWeight:"600"})

// Step 4: Now column (same pattern, different proportions)
// ... (mirror the above with different heights/data)

// Step 5: Legend row
legend=I(slide,{type:"frame",layout:"horizontal",gap:48,justifyContent:"center",alignItems:"center"})
// Insert LegendItem instances...

// Step 6: Finish
U("slideId",{placeholder:false})
```

### Recipe: T-Chart Comparison

```javascript
slide=I(document,{type:"ref",ref:"yp0ST",name:"Comparison",x:X,y:Y,placeholder:true})
U(slide+"/IEPR5",{content:"The Leverage Has Moved"})

cols=R(slide+"/QJD7y",{type:"frame",layout:"horizontal",width:"fill_container",height:"fill_container",gap:40,justifyContent:"center"})

left=I(cols,{type:"ref",ref:"GZniz",width:"fill_container",height:"fill_container"})
U(left+"/9aD1P",{content:"Old Leverage",fill:"$text-muted"})

right=I(cols,{type:"ref",ref:"GZniz",width:"fill_container",height:"fill_container"})
U(right+"/9aD1P",{content:"New Leverage",fill:"$orange"})

// Add BulletItems to each column's body slot (UguT2):
b1=I("leftId/UguT2",{type:"ref",ref:"uE48a",width:"fill_container"})
U(b1+"/Nzqrm",{content:"Typing speed"})
// ... more bullets

U("slideId",{placeholder:false})
```

### Recipe: Process Flow

```javascript
slide=I(document,{type:"ref",ref:"yp0ST",name:"Process",x:X,y:Y,placeholder:true})
U(slide+"/IEPR5",{content:"The New Baseline Loop"})

flow=R(slide+"/QJD7y",{type:"frame",layout:"horizontal",width:"fill_container",height:"fill_container",gap:8,justifyContent:"center",alignItems:"center"})

s1=I(flow,{type:"ref",ref:"0wSif"})
U(s1+"/ZsqP0",{content:"Frame"})
a1=I(flow,{type:"ref",ref:"SSGdt"})
s2=I(flow,{type:"ref",ref:"0wSif"})
U(s2+"/ZsqP0",{content:"Specify"})
a2=I(flow,{type:"ref",ref:"SSGdt"})
// Highlight one step:
s3=I(flow,{type:"ref",ref:"0wSif",fill:"$orange",stroke:{fill:"$orange",thickness:2}})
U(s3+"/ZsqP0",{content:"Generate"})

// Footer note:
U(slide+"/GarGy",{content:"Generate is now the smallest part of the loop"})

U("slideId",{placeholder:false})
```

### Recipe: Checklist / Spec Template

```javascript
slide=I(document,{type:"ref",ref:"yp0ST",name:"Checklist",x:X,y:Y,placeholder:true})
U(slide+"/IEPR5",{content:"What Agent-Ready Work Looks Like"})

list=R(slide+"/QJD7y",{type:"frame",layout:"vertical",width:"fill_container",height:"fill_container",gap:20,justifyContent:"center",alignItems:"center"})

c1=I(list,{type:"ref",ref:"aSpSl",width:600})
U(c1+"/3D59S",{content:"Clear goal statement"})
c2=I(list,{type:"ref",ref:"aSpSl",width:600})
U(c2+"/3D59S",{content:"Explicit constraints"})
// ... more items

U("slideId",{placeholder:false})
```

### Recipe: KPI Dashboard

```javascript
slide=I(document,{type:"ref",ref:"yp0ST",name:"KPIs",x:X,y:Y,placeholder:true})
U(slide+"/IEPR5",{content:"The Impact"})

kpiRow=R(slide+"/QJD7y",{type:"frame",layout:"horizontal",width:"fill_container",height:"fill_container",gap:40,justifyContent:"center",alignItems:"center"})

k1=I(kpiRow,{type:"ref",ref:"k0pMA",width:400})
U(k1+"/IyZRt",{content:"SPEED"})
U(k1+"/LZff7",{content:"10x"})
U(k1+"/lBhhG",{content:"faster iteration cycles"})

k2=I(kpiRow,{type:"ref",ref:"k0pMA",width:400})
U(k2+"/IyZRt",{content:"QUALITY"})
U(k2+"/LZff7",{content:"3x",fill:"$teal"})
U(k2+"/lBhhG",{content:"fewer production bugs"})

U("slideId",{placeholder:false})
```

### Recipe: Layer Stack Diagram

```javascript
slide=I(document,{type:"ref",ref:"yp0ST",name:"Stack",x:X,y:Y,placeholder:true})
U(slide+"/IEPR5",{content:"Tool Layers"})

stack=R(slide+"/QJD7y",{type:"frame",layout:"vertical",width:"fill_container",height:"fill_container",gap:12,justifyContent:"center",alignItems:"center"})

l1=I(stack,{type:"ref",ref:"I9kNZ",width:800})
U(l1+"/GZbeO",{content:"Orchestration"})
U(l1+"/g1WsD",{content:"Multi-agent coordination"})

l2=I(stack,{type:"ref",ref:"I9kNZ",width:800})
U(l2+"/GZbeO",{content:"Verification"})
U(l2+"/g1WsD",{content:"Automated quality gates"})

// Highlighted layer:
l3=I(stack,{type:"ref",ref:"I9kNZ",width:800,fill:"$orange",stroke:{fill:"$orange",thickness:2}})
U(l3+"/GZbeO",{content:"Context Reduction"})
U(l3+"/g1WsD",{content:"Highest ROI — start here"})

l4=I(stack,{type:"ref",ref:"I9kNZ",width:800})
U(l4+"/GZbeO",{content:"Toil Reduction"})
U(l4+"/g1WsD",{content:"Scripts and automation"})

U("slideId",{placeholder:false})
```

### Recipe: 2x2 Decision Matrix

```javascript
slide=I(document,{type:"ref",ref:"yp0ST",name:"Matrix",x:X,y:Y,placeholder:true})
U(slide+"/IEPR5",{content:"The Decision Rule"})

matrix=R(slide+"/QJD7y",{type:"frame",layout:"vertical",width:"fill_container",height:"fill_container",gap:16,justifyContent:"center",alignItems:"center"})

topRow=I(matrix,{type:"frame",layout:"horizontal",gap:16,justifyContent:"center"})
c1=I(topRow,{type:"ref",ref:"8hpSA",fill:"$orange"})
U(c1+"/9n51H",{content:"Build a Tool"})
U(c1+"/NWO5W",{content:"Repeated tasks with heavy context"})
c2=I(topRow,{type:"ref",ref:"8hpSA"})
U(c2+"/9n51H",{content:"Write a Prompt"})
U(c2+"/NWO5W",{content:"Repeated but context-light"})

bottomRow=I(matrix,{type:"frame",layout:"horizontal",gap:16,justifyContent:"center"})
c3=I(bottomRow,{type:"ref",ref:"8hpSA"})
U(c3+"/9n51H",{content:"Encode Once"})
U(c3+"/NWO5W",{content:"One-off, context-heavy"})
c4=I(bottomRow,{type:"ref",ref:"8hpSA"})
U(c4+"/9n51H",{content:"Just Do It"})
U(c4+"/NWO5W",{content:"One-off, context-light"})

// Add axis labels:
yAxis=I(matrix,{type:"text",content:"← One-off          Repeated →",fontSize:20,fill:"$text-dim"})

U("slideId",{placeholder:false})
```

---

## Exporting Slides (Automated Pipeline)

### Step 1: Export from Pencil

```
pencil-export_nodes({
  nodeIds: ["slideId1", "slideId2"],
  outputDir: "/Users/marcus.vorwaller@avalara.com/code/bootcamp/course/public/images",
  format: "webp",
  scale: 1
})
```

### Step 2: Add entries to slide-map.json

Add each exported slide to `course/content/images/slide-map.json`:

```json
{
  "node_id": "lxb4v",
  "filename": "01-why-were-here-shift.webp",
  "module": "01-operating-model-changed",
  "block_id": "why-were-here-shift",
  "alt": "Descriptive alt text",
  "theme": "dark"
}
```

For light-theme variants, add a second entry with `"theme": "light"` and a `-light` filename suffix.

### Step 3: Rename + Inject

```bash
npx tsx course/scripts/slide-export.ts --rename          # rename node-ID files to descriptive names
npx tsx course/scripts/slide-export.ts --inject           # dry-run: preview content.json changes
npx tsx course/scripts/slide-export.ts --inject --apply   # write content.json changes
npx tsx course/scripts/slide-export.ts --status           # check what's exported
```

The script only injects dark-theme slides into content.json (light variants are for theme-aware UI).

---

## Creating Light-Theme Variants

For **component-based slides** (using SlideTemplate with design variables), copy with theme override:

```javascript
lightCopy=C("darkSlideId",document,{name:"Slide Name (Light)",positionDirection:"right",positionPadding:100,theme:{"mode":"light"}})
```

For **custom slides** (hardcoded colors, AI backgrounds), use this 3-step process:

### 1. Copy the dark slide

```javascript
lightCopy=C("darkSlideId",document,{name:"Slide Name (Light)",positionDirection:"right",positionPadding:100})
```

### 2. Bulk-remap colors

Use `pencil-replace_all_matching_properties` with the mapping from `course/content/images/dark-to-light-colors.json`:

```
pencil-replace_all_matching_properties({
  parents: ["lightCopyNodeId"],
  properties: {
    "fillColor": [
      {"from": "#080c14", "to": "#f8f9fb"},
      {"from": "#0d1a2a", "to": "#ffffff"},
      {"from": "#0a1a2888", "to": "#ffffff88"},
      ...
    ],
    "textColor": [
      {"from": "#f0f4f8", "to": "#1a1a2e"},
      {"from": "#5a708088", "to": "#5a6a7a88"},
      ...
    ],
    "strokeColor": [
      {"from": "#5a708060", "to": "#5a6a7a40"},
      ...
    ]
  }
})
```

### 3. Fix what bulk-remap can't catch

Gradient fills inside nested frames aren't caught by the bulk tool. Manually update:

- **Background image opacity**: reduce from 0.40 to 0.20–0.30 for light theme
- **Vignette overlay**: swap dark gradient stops to light (`#f8f9fb`)
- **Gradient-filled boxes** (flow diagrams): swap dark gradients to pastel equivalents

```javascript
U("bgImageFrameId",{opacity:0.12})
U("vignetteFrameId",{fill:{type:"gradient",gradientType:"radial",colors:[{color:"#f8f9fb00",position:0},{color:"#f8f9fb",position:0.85}],size:{width:1.6,height:1.6}}})
```

---

## Tips and Gotchas

### Keep Operations Under 25
Each `batch_design` call should have max 25 operations. Split complex slides across multiple calls.

### Always Use Placeholder
Set `placeholder:true` when creating a slide, remove it when done. This prevents layout issues during construction.

### Body Slot Pattern
The `slide-body` (`QJD7y`) is a slot. Use `R()` (Replace) to swap it with your layout, not `I()` (Insert). After replacing, insert content into the replacement frame using its binding.

### Instance Descendant Updates
When updating text inside a component instance, always use the instance path:
```javascript
U(instanceBinding+"/childId",{content:"new text"})
```

### fill_container Requires Flex Parent
`fill_container` only works when the parent has `layout:"horizontal"` or `layout:"vertical"`. Without flex layout, use explicit pixel sizes.

### Text Must Have Fill
Text nodes default to transparent. Always set `fill` on text to make it visible.

### No alignItems: "stretch"
Pencil does not support `alignItems:"stretch"`. Use explicit sizing instead.

### Custom Layouts
For diagrams that don't fit the components (hub-and-spoke, concentric rings, iceberg), use `layout:"none"` on the body frame and position elements with absolute `x,y` coordinates.

### AI-Generated Backgrounds (Use Liberally)
There is no `image` node type. Images are applied as fills to frames via `G()`. This is one of the most powerful tools available — use it to create visually distinctive slides rather than relying on flat color backgrounds.

```javascript
bgFrame=I(parent,{type:"frame",x:0,y:0,width:1920,height:1080,opacity:0.40})
G(bgFrame,"ai","architectural blueprint with glowing teal gridlines, deep navy monochrome, 16:9")
// Always add a vignette overlay on top for text legibility
vignette=I(parent,{type:"frame",x:0,y:0,width:1920,height:1080,fill:{type:"gradient",gradientType:"radial",colors:[{color:"#080c1200",position:0},{color:"#080c14",position:0.85}],size:{width:1.6,height:1.6}}})
```

Write prompts that evoke the slide's concept metaphorically. "Tectonic shift" for a change slide, "circuit board" for a technical spec, "lever and fulcrum" for a leverage concept.

### Text Wrapping in Cards and Panels
Text nodes inside cards have no width constraint by default and will overflow the card boundary. Always set an explicit `width` on description/body text nodes inside fixed-width cards. The width should be the card width minus horizontal padding on both sides:

```javascript
// Card is 840px wide with padding:[24,28] → text width = 840 - 28 - 28 = 784
U(cardDescNode, {width: 784})
```

Use `height:"fit_content(0)"` on the card frame so it grows to fit wrapped text instead of clipping.

### Z-Order: Background Images Must Be First Child
In `layout:"none"` frames, children render in order — first child is behind, last child is in front. Background image frames and vignette overlays must be the first children. If you add them after other content, use `M(bgNodeId, parentId, 0)` to move them to index 0.

### Custom Slides Must Have All Elements on Both Variants
When building a custom slide (not from SlideTemplate), make sure both dark and light versions have all structural elements: title, section labels, waterline/dividers, subtitle, footer, etc. It's easy to build the light version fully and then copy it for dark (or vice versa) but lose elements in the process. After copying, screenshot both and verify they match structurally.

### Vignette Overlays Are Required for AI Backgrounds
Every slide with an AI-generated background image needs a radial gradient vignette overlay for text legibility. Without it, text over the background is hard to read. Add immediately after the bg image frame:

```javascript
bgImg=I(slide,{type:"frame",x:0,y:0,width:1920,height:1080,opacity:0.40,name:"bg"})
G(bgImg,"ai","prompt here")
vignette=I(slide,{type:"frame",x:0,y:0,width:1920,height:1080,name:"vignette",fill:{type:"gradient",gradientType:"radial",colors:[{color:"#080c1200",position:0},{color:"#080c14",position:0.85}],size:{width:1.6,height:1.6}}})
```

### Strikethrough Lines Must Match Text Width
When using strikethrough lines over text (e.g., "old vs new" slides), the line `width` must cover the full rendered text. If you change the text content, update the line width to match. Wider text like "Implementation capacity" needs ~400px; shorter text like "Alerts" needs ~120px.

### Icon Names
Use Lucide icon names. Common ones: `arrow-right`, `arrow-down`, `circle-check`, `alert-circle`, `chevron-right`, `check`, `x`, `plus`, `minus`, `star`.

---

## Background Options

Instead of a flat `$bg-dark` fill, use these gradient fills on the SlideTemplate to add visual interest. Apply them to the slide instance's root fill property.

### Dark Theme Backgrounds

| # | Name | Best for | Fill |
|---|------|----------|------|
| 1 | Radial Glow | Content slides, checklists | `{type:"gradient",gradientType:"radial",colors:[{color:"#0f2a3d",position:0},{color:"#0d1117",position:1}],size:{width:1.2,height:1.2}}` |
| 2 | Corner Accent | Process flows | `{type:"gradient",gradientType:"radial",colors:[{color:"#1a3a4f",position:0},{color:"#0d1117",position:0.5}],center:{x:0,y:0},size:{width:1,height:1}}` |
| 3 | Dual Glow | Section openers, hero slides | Array: base `#0d1117`, teal radial glow bottom-left (0.4 opacity), orange radial glow top-right (0.3 opacity) |
| 4 | Linear Sweep | Minimal content | `{type:"gradient",gradientType:"linear",colors:[{color:"#0d1117",position:0},{color:"#0f2438",position:0.5},{color:"#0d1117",position:1}],rotation:135}` |
| 5 | Deep Ocean | Rich content, KPIs | `{type:"gradient",gradientType:"linear",colors:[{color:"#030a12",position:0},{color:"#0a2035",position:0.4},{color:"#0d2d45",position:0.7},{color:"#0a1825",position:1}],rotation:180}` |
| 6 | Angular Halo | Dramatic section openers | Array: base `#0d1117`, angular gradient with teal/orange rotation at 0.15 opacity |
| 7 | Warm Bottom Edge | Closings, wrap-ups | Array: base `#0d1117`, linear orange gradient from bottom at 0.12 opacity |
| 8 | Spotlight | Hero slides, impact slides | Array: base `#0d1117`, white radial from top-center at 0.12 opacity |
| 9 | Aurora | Most colorful option | Array: base `#0d1117`, teal-to-orange linear band plus subtle white radial |

### Light Theme Backgrounds

| # | Name | Fill |
|---|------|------|
| L1 | Warm Glow | `{type:"gradient",gradientType:"radial",colors:[{color:"#ffffff",position:0},{color:"#f0f2f5",position:1}],size:{width:1.2,height:1.2}}` |
| L2 | Cool Corner | `{type:"gradient",gradientType:"radial",colors:[{color:"#e8f4f8",position:0},{color:"#f8f9fb",position:0.5}],center:{x:0,y:0},size:{width:1,height:1}}` |
| L3 | Light Dual Glow | Array: base `#f8f9fb`, teal + orange radials at low opacity |
| L4 | Soft Sweep | `{type:"gradient",gradientType:"linear",colors:[{color:"#f8f9fb",position:0},{color:"#edf2f7",position:0.5},{color:"#f8f9fb",position:1}],rotation:135}` |

Full fill definitions with exact JSON are in the orchestration file at `course/design/ORCHESTRATION.md`.

### Selection Guide

| Slide Type | Recommended |
|-----------|-------------|
| Section openers | 3 (Dual Glow), 6 (Angular Halo), 9 (Aurora) |
| Content slides | 1 (Radial Glow), 4 (Linear Sweep), 5 (Deep Ocean) |
| Checklists/specs | 1 (Radial Glow), 8 (Spotlight) |
| Closing/wrap-up | 7 (Warm Bottom Edge), 3 (Dual Glow) |
| KPI/impact | 8 (Spotlight), 5 (Deep Ocean) |
| Process flows | 2 (Corner Accent), 4 (Linear Sweep) |

---

## Course-Specific: Updating content.json

Image injection into content.json is handled by the `slide-export.ts` script (see "Exporting Slides" above). Don't manually edit content.json for image references — add entries to `slide-map.json` and run `--inject --apply`.

---

## Building Components From Scratch

If the .pen file is missing or you need to recreate the design system, here is the complete setup:

### 1. Set Variables
```
pencil-set_variables({
  variables: {
    "bg-dark": {"type":"color","value":[{"value":"#0d1117","theme":{"mode":"dark"}},{"value":"#f8f9fb","theme":{"mode":"light"}}]},
    "bg-card": {"type":"color","value":[{"value":"#1a2a34","theme":{"mode":"dark"}},{"value":"#ffffff","theme":{"mode":"light"}}]},
    "text-primary": {"type":"color","value":[{"value":"#f0f4f8","theme":{"mode":"dark"}},{"value":"#1a1a2e","theme":{"mode":"light"}}]},
    "text-muted": {"type":"color","value":[{"value":"#a0b8c8","theme":{"mode":"dark"}},{"value":"#5a6a7a","theme":{"mode":"light"}}]},
    "text-dim": {"type":"color","value":[{"value":"#5a7080","theme":{"mode":"dark"}},{"value":"#94a3b8","theme":{"mode":"light"}}]},
    "text-on-accent": {"type":"color","value":"#ffffff"},
    "orange": {"type":"color","value":"#fc6600"},
    "teal": {"type":"color","value":[{"value":"#059bd2","theme":{"mode":"dark"}},{"value":"#0284a8","theme":{"mode":"light"}}]},
    "navy": {"type":"color","value":[{"value":"#025979","theme":{"mode":"dark"}},{"value":"#03719b","theme":{"mode":"light"}}]},
    "card-stroke": {"type":"color","value":[{"value":"#059bd2","theme":{"mode":"dark"}},{"value":"#d0d8e0","theme":{"mode":"light"}}]}
  }
})
```

### 2. Create Each Component
Follow the structure descriptions in the Component Reference above. Each component needs `reusable:true` on its root frame. Place them off to the side of the main canvas (e.g., at x:2120).

Key rules for component creation:
- Set `reusable:true` on the root frame
- Give meaningful `name` and `id` values to override points
- Use `slot:[]` on frames that should accept custom children in instances
- Use design variables (`$orange`, `$bg-dark`, etc.) for all colors
