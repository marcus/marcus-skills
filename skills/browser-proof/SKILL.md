---
name: browser-proof
description: Capture browser screenshots of Perch UI for visual verification. Use after implementing UI changes to prove they work, or when asked to verify, screenshot, or capture browser proof of a feature.
---

# Browser Proof — Playwright Screenshots for Perch

Capture screenshots of the running Perch app to verify UI changes. Uses Playwright (installed globally, v1.58+).

## Quick Reference

Write a `.mjs` script to `/tmp/`, run with `node`. Read screenshots with the Read tool (it renders images).

### Playwright Module Resolution

On this machine, `playwright` is installed globally, but `node /tmp/script.mjs` may not resolve `import { chromium } from 'playwright'`.

Use one of these approaches:

1. Import Playwright from its absolute global path:

```js
import { chromium } from '/Users/marcus/.local/share/mise/installs/node/22.22.0/lib/node_modules/playwright/index.mjs';
```

2. If that path changes, discover it first:

```bash
which playwright
npm root -g
```

Then import from `<npm root -g>/playwright/index.mjs`.

Prefer the absolute import path in proof scripts. It worked for live browser capture on 2026-03-15.

### Auth Pattern

```js
import { chromium } from '/Users/marcus/.local/share/mise/installs/node/22.22.0/lib/node_modules/playwright/index.mjs';
import { readFileSync } from 'fs';

const TOKEN = readFileSync('/Users/marcus/.config/perch/auth.token', 'utf8').trim();
const BASE = 'http://localhost:8090';  // production
const DEV  = 'http://localhost:5174';  // vite dev (port may vary — check npm run dev output)

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
const page = await ctx.newPage();

// Login via API — sets session cookie on the context
await page.request.post(`${BASE}/api/login/token`, { data: { token: TOKEN } });
```

### Navigate + Screenshot

```js
// Use DEV base for latest code (HMR), BASE for production build
await page.goto(`${DEV}/td?project=perch&board=bd-all-issues#board`);
await page.waitForTimeout(3000);
await page.screenshot({ path: '/tmp/proof-01-board.png' });
```

### Interact

```js
// Click element
await page.locator('text=Issue title').first().click();
await page.waitForTimeout(2000);

// Check visibility (with timeout + catch for safety)
const el = page.locator('.my-class').first();
const visible = await el.isVisible({ timeout: 3000 }).catch(() => false);

// Count elements
const count = await page.locator('.my-class').count();

// Type text
await page.keyboard.type('hello');

// Keyboard shortcuts
await page.keyboard.press('Escape');
await page.keyboard.press('Meta+Enter');

// Scroll
await page.evaluate(() => {
  document.querySelector('.scroll-container')?.scrollTo(0, 999);
});
```

### Cleanup

```js
await browser.close();
```

## Perch URL Patterns

| Page | URL |
|------|-----|
| Tasks overview | `/td` |
| Project board | `/td?project=perch&board=bd-all-issues#board` |
| List view | `/td?project=perch&board=bd-all-issues#list` |
| Helm | `/helm` |
| Workspace | `/workspace` |
| Briefings | `/briefings` |

To open a detail panel, click a board card or table row — the panel slides in from the right.

## Rules

1. **Always use `/tmp/` for screenshot files** — never write to the repo.
2. **Use the Read tool to view screenshots** — it renders images inline.
3. **Wait after navigation/clicks** — `waitForTimeout(2000-3000)` for SPA rendering.
4. **Use `.catch(() => false)` on visibility checks** — prevents test crashes.
5. **Dev server for latest code** — `npm run dev` output shows the port. The API still hits `localhost:8090`.
6. **Production server for deployed builds** — restart `./perch` after `make build` to pick up changes.

## Example: Full Proof Script

```js
import { chromium } from '/Users/marcus/.local/share/mise/installs/node/22.22.0/lib/node_modules/playwright/index.mjs';
import { readFileSync } from 'fs';

const TOKEN = readFileSync('/Users/marcus/.config/perch/auth.token', 'utf8').trim();
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
const page = await ctx.newPage();

await page.request.post('http://localhost:8090/api/login/token', { data: { token: TOKEN } });
await page.goto('http://localhost:5174/td?project=perch&board=bd-all-issues#board');
await page.waitForTimeout(3000);
await page.screenshot({ path: '/tmp/proof-01.png' });

// Click first issue
await page.locator('tbody tr').first().click();
await page.waitForTimeout(2500);
await page.screenshot({ path: '/tmp/proof-02.png' });

await browser.close();
```

Then: `node /tmp/my-proof.mjs` and use Read tool on `/tmp/proof-*.png`.
