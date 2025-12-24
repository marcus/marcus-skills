# Debugging Link Previews

Step-by-step commands for diagnosing broken or missing link previews.

## Step 1: Confirm tags exist in server HTML

```bash
curl -sL https://example.com/page | head -200 | grep -E "og:|twitter:"
```

Check for:
- `og:title`, `og:image`, `og:url`, `og:type`
- `twitter:card`
- All URLs are absolute
- Correct route/canonical URL

If tags are missing, they're likely client-injected (SPA problem).

## Step 2: Check redirects

```bash
curl -sIL https://example.com/page
```

Watch for:
- http -> https redirect losing tags on intermediate response
- Canonical pointing elsewhere
- `og:url` differing from final destination

## Step 3: Verify image is fetchable

```bash
curl -sI https://example.com/og/page-1200x630.jpg
```

Confirm:
- `200 OK`
- `Content-Type: image/jpeg` (or png/webp)
- No auth/cookies required
- Not blocked by robots.txt or WAF

## Step 4: WhatsApp-specific checks

If WhatsApp preview is broken:

```bash
# Check image size
curl -sI https://example.com/og/image.jpg | grep -i content-length
```

Requirements:
- Image < 600KB
- Width >= 300px
- Aspect ratio <= 4:1
- OG tags in first ~300KB of HTML

## Step 5: Force cache refresh

Platforms cache previews aggressively.

**Facebook**: Use [Sharing Debugger](https://developers.facebook.com/tools/debug/) - click "Scrape Again"

**Twitter/X**: Use [Card Validator](https://cards-dev.twitter.com/validator)

**iMessage/WhatsApp**: No official tool. Change the `og:image` filename to bust cache, then wait.

## Quick diagnosis table

| Symptom | Likely cause |
|---------|--------------|
| No preview at all | Tags client-injected, or page blocked |
| Wrong/old image | Platform cache, or multiple og:image tags |
| Image missing | og:image 403/404, or relative URL |
| WhatsApp no image | Image > 600KB or aspect > 4:1 |
| Cropped weirdly | Image dimensions wrong for platform |
