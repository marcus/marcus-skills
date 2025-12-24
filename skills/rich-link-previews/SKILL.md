---
name: rich-link-previews
description: Create and debug rich link previews (Open Graph + Twitter/X Cards) for iMessage, WhatsApp, Slack/Discord, and social platforms. Use when user asks about og tags, twitter cards, link previews, social sharing metadata, or when a shared link preview looks wrong or missing.
---

# Rich Link Previews (Open Graph + Twitter/X Cards)

Help users add the right meta tags, choose image sizes that survive crops, and debug missing/broken previews.

## Ready-to-paste snippet

Default answer when user says "just tell me what to add":

```html
<link rel="canonical" href="https://example.com/page" />

<meta property="og:type" content="website" />
<meta property="og:url" content="https://example.com/page" />
<meta property="og:title" content="Short title for chat bubbles" />
<meta property="og:description" content="One sentence. Clear benefit." />
<meta property="og:image" content="https://example.com/og/page-1200x630.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />

<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="https://example.com/og/page-1200x600.jpg" />
<meta name="twitter:image:alt" content="Brief image description." />
```

Twitter/X falls back to OG tags, so `twitter:title` and `twitter:description` are optional.

## Image sizing

| Platform | Size | Aspect | Notes |
|----------|------|--------|-------|
| OG default | 1200x630 | 1.91:1 | Works across most platforms |
| Twitter/X | 1200x600 | 2:1 | For `summary_large_image` |
| WhatsApp | 300px+ wide | <= 4:1 | **Must be < 600KB** |

**Composition rules**: Treat it like a phone billboard. 3-7 words max. Critical content in center (assume top/bottom cropping). High contrast, no thin fonts.

## Platform notes

**iMessage**: Emphasizes `og:title` and `og:image` over description. Make the title and image carry the message alone.

**WhatsApp**: OG tags must appear in first ~300KB of HTML response. Image must be < 600KB.

**SPAs**: Scrapers don't execute JS. Tags must exist in initial server HTML. Use SSR, prerendering, or dedicated share URLs.

## Before you ship

- [ ] All URLs absolute (not `/og.png`)
- [ ] Tags in server HTML, not client-injected
- [ ] `og:url` matches canonical URL
- [ ] Image returns 200 OK to anonymous requests
- [ ] Image < 600KB (for WhatsApp)
- [ ] No robots/auth blocking the image

## Common failures

- **No preview**: Tags only injected client-side, or og:image 403/404 to bots
- **Wrong image**: Multiple og:image tags (first one wins), or platform cache stale
- **Cropped badly**: Image too tall/narrow, or text at edges
- **WhatsApp broken**: Image > 600KB, aspect > 4:1, or tags too deep in HTML

## Debugging

See [references/debugging.md](references/debugging.md) for step-by-step commands.

Quick check:
```bash
curl -sL https://example.com/page | head -100 | grep -E "og:|twitter:"
```

**Cache busting**: Change the og:image filename. Platform validators (Facebook Debugger, X Card Validator) can force refresh.

## References

- [Open Graph Protocol](https://ogp.me/)
- [Twitter Cards docs](https://developer.x.com/en/docs/twitter-for-websites/cards/overview/abouts-cards)
- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
- [Twitter Card Validator](https://cards-dev.twitter.com/validator)
