# Production Techniques

The craft of making software look cinematic. Tools, settings, and techniques that separate professional product videos from amateur screen recordings.

---

## Screen Recording

### Resolution and Frame Rate

Record at **4K (3840x2160) / 60fps** even when delivering at 1080p. This gives room to crop, zoom, and pan without quality loss. 4K downscaled to 1080p is sharper than native 1080p.

| Frame Rate | Use Case | Feel |
|------------|----------|------|
| 24 fps | Cinematic segments, narrative intros | Film-like |
| 30 fps | Standard screen recordings, tutorials | Natural |
| 60 fps | UI animations, smooth scrolling, fast interactions | Buttery smooth |

Record at 60fps. Conform to 24fps in post for cinematic segments.

### Cursor Behavior

The single biggest tell between amateur and professional recordings.

**During recording:**
- Rehearse exact workflow 3-5 times before recording
- Move at ~50% natural speed
- Pause on elements for 0.5-1s before clicking
- Never move cursor while talking about something unrelated to where it points
- Park cursor off-screen or hide it when idle

**In post:**
- Apply cursor smoothing (jerky to fluid)
- Add click highlights (subtle colored circles/ripples)
- Hide cursor during result-showing sections
- Enlarge to 125-150% for mobile viewers

### Environment Prep

- Close unnecessary apps and notifications (Do Not Disturb / Focus mode)
- Clean desktop wallpaper (solid color or subtle gradient)
- Pre-load all pages to avoid loading spinners
- Clear browser bookmarks bar, extra tabs, extensions
- Use a dedicated clean browser profile
- Set display scaling to 100% (or best for recording resolution)

### Recording Tools

| Tool | Platform | Price | Best For |
|------|----------|-------|----------|
| **Screen Studio** | macOS | $89 | Polished demos, auto-zoom on clicks, cinematic motion blur. Gold standard. |
| **ScreenFlow** | macOS | $169 | Longer tutorials, multi-track editing, point zoom with easing |
| **Camtasia** | Win/Mac | $300 | Education, cursor smoothing, smart captions, SCORM export |
| **OBS Studio** | All | Free | Power users with separate editing workflow |
| **CleanShot X** | macOS | $29 | Quick captures, bug reports, informal demos |
| **Rapidemo** | Windows | Varies | Screen Studio-like polish on Windows |
| **FocuSee** | Win/Mac | Varies | AI auto-editing with zooms and cursor tracking |

### Post-Processing

**Zoom and pan:**
- Ken Burns-style zoom to draw attention to specific UI elements
- Ease in/out (cubic or quintic curves) -- never snap-zoom
- Zoom levels: 150% subtle focus, 200% callouts, 300%+ small text/icons
- Pan between areas rather than cutting to maintain spatial context
- Crop unnecessary browser chrome, OS UI

**Aspect ratios:**
- 16:9: YouTube, presentations, website embeds
- 9:16: Instagram Stories, TikTok, YouTube Shorts
- 1:1: LinkedIn, Twitter/X, Instagram feed
- 4:5: Instagram feed (maximum real estate)
- Record in 16:9, reframe for other ratios in post

---

## Motion Graphics

### After Effects Techniques

**Screen replacement:** Corner pin tracking to place UI recordings onto 3D device renders. Add subtle screen reflections for photorealism.

**UI animation recreation:** Rebuild key interactions in AE for perfect timing. Use shape layers for pixel-perfect elements. Standard easing: ease-out for entrances, ease-in for exits, ease-in-out for state changes.

**Text/data animation:** Animate counting numbers for metrics. Stagger text reveals. Use expressions for data-driven animations.

### Trends (2026)

- **Hybrid 2.5D**: Flat UI with subtle 3D depth and parallax. Dominant SaaS style.
- **Kinetic typography**: Text as primary visual, animated with rhythm.
- **Authenticity over hyper-polish**: Intentional imperfections signal human craft.
- **Cinematic storytelling**: Emotional arcs replacing quick-cut feature tours.

### Kinetic Typography

- Word-by-word reveals synced to voiceover
- Text animates from the direction of the UI element it describes
- Key words momentarily grow larger
- Color shifts on important terms matching brand palette
- Every animation must serve comprehension. If it makes text harder to read, simplify.

### 3D Device Mockups

| Approach | Tool | Speed | Control |
|----------|------|-------|---------|
| Specialized | **Rotato** | Fastest | Drag-and-drop, no 3D experience needed |
| AE templates | **Element 3D**, VideoHive | Moderate | Drop in screen content, adjust, render |
| Full 3D | **Blender** (free), Cinema 4D, Unreal Engine | Slowest | Unlimited creative control |

Tips: Match 3D lighting to video lighting. Add environment reflections. Use shallow DOF for premium feel. Animate with gentle, floaty easing. Screen content should be animated, not static.

### Lottie Animations (Web Embeds)

70% smaller than GIF/video. Vector-based, interactive, 60fps. Use for: animated feature illustrations, interactive product tours, onboarding flows, micro-interactions that demonstrate UI behavior without full video embeds.

Workflow: Design in AE/Figma > Export via Bodymovin > Embed with lottie-web/react-lottie.

---

## Transitions

### Types and When to Use

**Hard Cut (90%+ of transitions)**
Standard for switching features, cutting between talking head and screen recording. If in doubt, use a cut.

**Dissolve (sparingly)**
Only for time passage, location changes, before/after. Duration: 0.5-2s. Overuse cheapens the effect.

**Zoom Transition**
Feature-to-feature navigation. Duration: 0.3-0.8s. Zoom into UI element at end of shot A, match-cut to zooming out of element in shot B. Add motion blur at midpoint.

**Slide / Push / Wipe**
Step-by-step progressions. Direction follows logical flow (left-to-right for forward in LTR).

**Motion Blur**
High-energy sequences, sizzle reels. Duration: 0.2-0.5s.

**UI Masking**
Most polished technique. A UI element (sidebar, modal, dropdown) expands to cover the frame, then reveals the new scene. Requires AE compositing but creates the most branded feel.

### Seamless Zoom Technique

1. End shot A with zoom-in toward a specific UI element
2. Add motion blur during fastest part of zoom
3. Begin shot B already zoomed in, ease out to reveal new context
4. Match zoom center point between shots
5. At midpoint (maximum zoom, maximum blur), cut between shots
6. Viewer perceives one continuous camera movement

---

## Camera and Live Action

### When to Use

- Talking-head narration between screen recordings
- Customer testimonials
- "Day in the life" B-roll
- Brand/opening/closing sequences
- Team/culture content

Skip it when: quick feature walkthroughs for existing users, technical docs, or when budget doesn't allow quality (bad live-action is worse than none).

### Lighting (Two-Point Setup)

```
         [Key Light]
              \  45 degrees
               \
    [Camera] --- [Subject]
               /
              /  45 degrees
         [Fill Light]
```

**Key light**: 45 degrees to side and above. Large, soft (softbox or diffused LED).
**Fill light**: Opposite side, ~half intensity. Softens shadows.
**Optional rim light**: Behind subject, separates from background.

| Budget | Equipment | Price |
|--------|-----------|-------|
| Entry | Elgato Key Light, ring light | $100-200 |
| Mid-range | Aputure AL-M9, Godox SL60W + softbox | $200-500 |
| Professional | Aputure 300d II, ARRI SkyPanel | $500+ |

Color temperature: 5000-5600K (daylight) standard. All lights must match.

### B-Roll Categories

1. **Problem context** -- frustrated user, cluttered workspace, manual work
2. **Hands on devices** -- close-ups of typing, clicking, tapping
3. **Human reaction** -- smile at screen, nod, lean back satisfied
4. **Environment** -- offices, coffee shops, home offices
5. **Macro details** -- screen close-up of key UI moments
6. **Team collaboration** -- pointing at screens, whiteboard discussions
7. **Results** -- dashboard metrics, charts trending up, completions

Shoot 3-5x more than you need. Multiple angles. Slow motion (60-120fps) for hands-on-device. Shallow DOF (f/1.4-2.8) makes mundane environments cinematic.

### Green Screen vs. Real Environment

**Green screen**: Full background control, consistent results, but requires meticulous lighting and post-production keying.

**Real environment**: Natural light interaction, subject comfort, faster post. Less control.

**Recommendation**: Real environment for authenticity. Simple controlled set with brand colors for product focus. Green screen only with proper budget for quality keying.

---

## Sound Design

### Music Selection

| Video Type | Mood | Tempo | Instrumentation |
|------------|------|-------|-----------------|
| Launch / sizzle | Upbeat, inspiring | 120-140 BPM | Electronic, synths, driving beat |
| Feature walkthrough | Light, unobtrusive | 90-110 BPM | Acoustic guitar, piano, ambient pads |
| Enterprise demo | Professional, warm | 80-100 BPM | Orchestral light, piano, subtle electronics |
| Consumer app | Fun, modern | 110-130 BPM | Indie pop, playful percussion |
| Problem/solution | Tension to resolution | Variable | Sparse beginning, fuller resolution |

### Music Platforms

| Platform | Price | Best For |
|----------|-------|----------|
| **Epidemic Sound** | $10-20/mo | Volume creators, YouTube. Content cleared forever. |
| **Artlist** | $10/mo (annual) | Agencies. Includes footage, SFX, templates. |
| **Musicbed** | Premium | Cinematic, narrative-driven, premium positioning. |
| **Soundstripe** | $11.25/mo | Budget-conscious teams. |
| YouTube Audio Library | Free | Very limited selection. |

### UI Sound Effects

Types: clicks, whooshes, pops/pings, typing, slides, rise/swell.

| Library | Notes |
|---------|-------|
| BOOM Library -- Modern UI | 1,054+ pro UI effects |
| A Sound Effect | Click/Whoosh SFX packs |
| Motion Array | General SFX library |
| UVI Whoosh FX | Custom whoosh generation |
| Freesound | Free community-contributed |

**Rules:**
- Less is more. Not every click needs a sound.
- Keep SFX -20 to -30 dB below voiceover
- Match tone to brand (playful = warmer, enterprise = crisper)
- Same sound for same action type (consistency)
- Layer subtle SFX with zoom transitions

### Voiceover

**Microphones:**

| Level | Examples | Price |
|-------|----------|-------|
| Minimum viable | Blue Yeti, AT2020 USB+ | $50-130 |
| Professional USB | Elgato Wave:3, Rode NT-USB Mini | $100-170 |
| Broadcast | Shure SM7B, Electro-Voice RE20 | $300-450 |
| Studio | Neumann U87, Rode NT1-A | $200-3,000+ |

**Recording:**
- Quietest room available. Closets with clothes = excellent booth.
- Eliminate ambient noise
- Pop filter + shock mount
- 6-8 inches from mouth
- Record in sections, not one continuous take
- 2-3 takes per section, pick best
- Leave 2-3s silence at start/end for noise profiling
- Smile while recording -- it changes voice warmth

**Post-processing chain:**
1. Noise reduction (remove hum/hiss)
2. EQ (cut below 80Hz, slight boost 3-5kHz)
3. Compression (3:1 to 4:1, gentle)
4. De-essing (5-8kHz range)
5. Limiter (ceiling at -1dB)
6. Normalize to -16 LUFS (YouTube) or -14 LUFS (podcasts)

### Beat-Synced Editing

Creates the "Apple feel" -- subconscious polish and intentionality.

**Manual technique:**
1. Import music, mark every strong beat (kicks, snares)
2. Mark accent beats (cymbal crashes, drops)
3. Align cuts to markers
4. Major transitions on downbeats (beat 1 of a measure)
5. Minor transitions on other strong beats
6. Let longer shots breathe across 2-4 measures

**Automated tools:** VideoProc Vlogger, VSDC, Filmora Auto Beat Sync, VEED.IO, Kaiber.

**Music editing:**
- Choose music with clear sections (intro, build, chorus, outro) matching video structure
- Build section = problem setup; chorus/drop = product reveal
- Fade music 6-10 dB under voiceover, bring back up for visual-only
- If song is too long, cut on a downbeat during repetitive section

---

## Color Grading

### Principles for Screen Recordings

- Preserve UI color accuracy (brand-specific colors must not shift)
- Grade for consistency across clips from different sessions
- Apply heavier grading to frames around the recording (backgrounds, mockups, live-action) than to the recording itself
- Ensure text remains readable after adjustments

### Tools

| Tool | Notes |
|------|-------|
| **DaVinci Resolve** | Industry-leading, free version available |
| **Premiere Pro** | Lumetri panel, one-click corrections |
| **After Effects** | Grade individual layers independently |

### Workflow

1. Color correct (fix white balance, exposure, color casts)
2. Match shots (all clips look like they belong together)
3. Apply subtle creative grade to non-UI elements
4. Very gentle grade on screen recordings (slight contrast/saturation)
5. Export LUT for consistency across future videos

### Dark Mode vs. Light Mode

**Dark mode:** Viewer preference, less eye strain, cinematic/premium feel. Challenge: can look flat on compressed streams. Solution: boost contrast slightly.

**Light mode:** Better visibility in bright environments, cleaner, more accessible. Can feel harsh full-screen.

**Tips:**
- Dark UI next to bright talking-head is jarring -- bring brightness levels closer together
- Increase monitor brightness to 80-100% when recording dark mode
- Apply noise reduction to dark mode recordings (compression artifacts more visible)
- For flexibility, record both modes and choose in post

### Brand Color Integration

- Define video color palette from design system: primary, secondary, accent, background, text
- Apply to: backgrounds, lower thirds, text overlays, transitions, callout highlights, cursor highlights
- Create templates with brand colors baked in
- Build .mogrt library with brand elements
- Use Essential Graphics panel in Premiere for editor-friendly templates

---

## Complete Workflow

### Pre-Production
1. Write script (problem, solution, key features, CTA)
2. Storyboard -- map each shot (screen recording, motion graphic, live-action, text)
3. Select music, map video structure to music sections
4. Prepare software environment
5. Rehearse screen recording 3-5 times

### Production
6. Record screen at 4K/60fps
7. Film talking-head with two-point lighting
8. Capture B-roll
9. Record voiceover in treated room

### Post-Production
10. Rough cut: assemble in narrative order
11. Add zoom/pan to screen recordings
12. Cut in live-action and B-roll
13. Create motion graphics (mockups, kinetic text, callouts)
14. Add transitions (mostly cuts, strategic zooms)
15. Sync cuts to music beats
16. Layer UI sound effects
17. Color grade for consistency
18. Mix audio (VO loudest > music ducked under VO > SFX subtle)
19. Add end card with CTA
20. Export (1080p or 4K, H.264 or H.265)

### Quality Checklist
- [ ] Cursor movement is smooth and deliberate
- [ ] All UI text readable at delivery resolution
- [ ] Music doesn't overpower voiceover
- [ ] Brand colors consistent throughout
- [ ] No notification pop-ups or personal info visible
- [ ] Transitions serve the narrative
- [ ] Video length matches platform best practices
- [ ] Correct aspect ratio for target platform
