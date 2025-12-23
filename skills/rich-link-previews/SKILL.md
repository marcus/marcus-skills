---
name: rich-link-previews
description: Create and debug beautiful rich link previews (Open Graph + Twitter/X Cards) for URLs shared via iMessage/SMS, WhatsApp, Slack/Discord, and social platforms. Use when the user asks about Open Graph, Twitter cards, link previews, iMessage rich links, preview images, social sharing metadata, or when a shared link preview looks wrong or missing.
---

# Rich Link Previews (Open Graph + Twitter/X Cards)

## Goal

When a user pastes a URL into messaging or social apps, the app fetches the page HTML and uses `<meta>` tags in `<head>` to render a preview. This Skill helps you:

- Add the right tags (Open Graph + Twitter/X)
- Choose image sizes and composition that survive common crops
- Debug missing/incorrect previews (SSR vs JS, caching, redirects, robots, wrong headers)

Open Graph basics include `og:title`, `og:type`, `og:image`, and `og:url`. https://ogp.me/

Twitter/X cards can be generated from OG data and also support explicit `twitter:*` tags.

---

## Trigger conditions

Use this Skill when the user mentions any of:

- open graph / og tags / `og:image`
- twitter cards / `twitter:card` / "X preview"
- "rich links", "link preview", "social share image"
- "iMessage preview", "Messages rich preview"
- "WhatsApp preview doesn't show image/title"
- "Slack/Discord embed missing/wrong"
- "preview looks cropped / pixelated / wrong image"

---

## What you should deliver

Depending on the request, output one or more:

1. A ready-to-paste `<head>` snippet (OG + Twitter/X)
2. A per-route metadata template (static or SSR)
3. Image requirements + safe composition rules
4. A debugging checklist with concrete commands
5. Notes on caching / refresh tools and expectations

Keep it practical. Prefer templates over theory.

---

## Canonical "golden" tags

### Open Graph (baseline for most clients)

Minimum recommended OG set:

```html
<link rel="canonical" href="https://example.com/page" />

<meta property="og:type" content="website" />
<meta property="og:url" content="https://example.com/page" />
<meta property="og:title" content="Page title that reads well in chat bubbles" />
<meta property="og:description" content="One sentence that explains the value." />
<meta property="og:image" content="https://example.com/og/page-1200x630.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
```

Rules:
- Always use absolute URLs for og:url and og:image.
- Ensure the OG tags are in the HTML response (not only injected client-side).
- The og:url should match your canonical URL.

### Twitter/X cards (add on top)

Use "summary with large image" for strong previews.

```html
<meta name="twitter:card" content="summary_large_image" />

<!-- Optional -->
<meta name="twitter:site" content="@yourbrand" />
<meta name="twitter:creator" content="@author" />

<!-- Can be omitted to fall back to OG, but explicit is safer -->
<meta name="twitter:title" content="Page title that reads well in a timeline" />
<meta name="twitter:description" content="One sentence. No fluff." />
<meta name="twitter:image" content="https://example.com/og/page-1200x600.jpg" />
<meta name="twitter:image:alt" content="Short alt text describing the image." />
```

---

## Image sizing that survives texting and social crops

### Recommended baseline OG image

Use 1200x630 (1.91:1) as the default OG image when you want a single asset that works across many platforms.

If you want best-in-class for X too, also provide a 2:1 variant and point twitter:image at it.

### Twitter/X "summary_large_image" aspect

The "Summary Card with Large Image" is designed as a wide image experience. Many implementations target 2:1 (e.g. 1200x600 or 1024x512).

Practical approach:
- og:image: 1200x630
- twitter:image: 1200x600 (or 1024x512)

### WhatsApp constraints (don't ignore these)

Meta's WhatsApp link preview docs specify:
- preview image should be under 600KB
- 300px+ width
- aspect ratio <= 4:1

Also: WhatsApp requires the `<head>` section containing OG tags to appear early in the HTML response (commonly cited as within the first ~300KB).

### Composition rules (what "looks amazing")

Design the preview image like a tiny billboard on a phone:
- Keep text minimal (3-7 words).
- Put critical text and marks in the center with generous padding.
- Assume top/bottom cropping in some clients.
- High contrast. No thin fonts.
- Avoid small UI text; it becomes noise.
- Prefer one strong visual element (product screenshot, illustration, photo) plus a short headline.

---

## iMessage / Apple Messages specifics

Apple documents creating rich previews for Messages and references using og:image to supply the preview image. In practice, many reports indicate Messages often emphasizes og:title and og:image over og:description in the expanded preview.

Practical takeaway:
- Don't rely on description to carry key context for iMessage.
- Make og:title excellent.
- Make the OG image speak for itself.

---

## Implementation patterns

### Pattern A: Static site / server-rendered HTML

Hardcode tags per page at build time or server-render time. This is the safest path for link scrapers.

### Pattern B: SPA with dynamic routes

Many scrapers do not execute client-side JavaScript reliably. If metadata is injected on the client, previews can fail.

Preferred fixes:
- SSR for routes you share
- prerendered snapshots for crawlers
- edge-rendered HTML for bots
- serve dedicated share URLs that are static HTML and redirect humans

If the user asks for framework-specific guidance, produce a minimal example for their stack (Next, Remix, Nuxt, SvelteKit, Rails, Django, etc.) and emphasize: tags must exist in the initial HTML response.

---

## Debugging playbook (use this when previews are wrong/missing)

### Step 1: Confirm the scraper sees the tags

Fetch the raw HTML and inspect `<head>`:

```bash
curl -sL https://example.com/page | sed -n '1,200p' | rg -n "og:|twitter:"
```

Confirm:
- og:title, og:image, og:url, og:type
- twitter:card (and optionally twitter title/desc/image)
- Absolute URLs
- Correct route and canonical URL

### Step 2: Check redirects and canonicalization

```bash
curl -sIL https://example.com/page
```

Common issues:
- scraper hits http -> https redirect and loses tags on intermediate pages
- canonical points somewhere else
- og:url differs from the final destination

### Step 3: Verify the image is fetchable and correct headers

```bash
curl -sI https://example.com/og/page-1200x630.jpg
```

Confirm:
- 200 OK
- Content-Type: image/jpeg (or png/webp)
- no auth cookies required
- not blocked by robots.txt or firewall rules

### Step 4: Check WhatsApp constraints when WhatsApp is the complaint

From Meta's docs:
- image < 600KB
- width >= 300px
- aspect ratio <= 4:1

Also ensure the OG tags appear early in the HTML response.

### Step 5: Assume caching until proven otherwise

Most platforms cache previews.

Actions:
- Change the og:image URL (new filename) to bust caches.
- Use platform debug/validator tools when available (Facebook debugger, X card tooling).
- For messaging apps (iMessage/WhatsApp), expect slow cache invalidation; "fix + wait" is normal. Prefer cache-busting via new image URLs.

---

## Ready-to-paste "golden head" snippet

Use this as the default answer when the user says "just tell me what to add".

```html
<link rel="canonical" href="https://example.com/page" />

<meta property="og:type" content="website" />
<meta property="og:url" content="https://example.com/page" />
<meta property="og:title" content="Short title that reads well in a text thread" />
<meta property="og:description" content="One sentence. Clear benefit. No filler." />
<meta property="og:image" content="https://example.com/og/page-1200x630.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />

<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Short title that reads well on X" />
<meta name="twitter:description" content="One sentence. Clear benefit. No filler." />
<meta name="twitter:image" content="https://example.com/og/page-1200x600.jpg" />
<meta name="twitter:image:alt" content="Describe the preview image briefly." />
```

---

## Common failure modes (diagnose fast)

- OG tags not in server HTML (client-only injection)
- og:image is relative (/og.png) instead of absolute
- og:image returns 403/404 to bots
- Image is too large or aspect ratio too extreme for WhatsApp
- og:url differs from the real shared URL (canonical mismatch)
- Platform cache still showing old preview
- Multiple og:image tags in wrong order (first one is bad)
- Robots or security layer blocks scrapers
