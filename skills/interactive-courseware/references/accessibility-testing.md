# Accessibility Testing Reference

Comprehensive accessibility testing guidance for interactive courseware. Covers automated tooling, courseware-specific ARIA patterns, manual testing protocols, and compliance documentation.

Accessibility is a design principle, not a compliance checkbox. Every interaction in the course must be operable by keyboard, perceivable by screen readers, and usable under constrained conditions (low vision, motor impairment, cognitive load, motion sensitivity).

---

## 1. Automated Testing Setup

### 1.1 axe-core with Vitest (Unit-Level Checks)

Test individual components in isolation for accessibility violations.

**Install dependencies:**

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom axe-core vitest-axe jsdom
```

**Vitest config:**

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
  },
});
```

**Test setup file:**

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom';
import 'vitest-axe/extend-expect';
```

**Component accessibility test:**

```tsx
// src/components/interactions/__tests__/KnowledgeCheck.a11y.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'vitest-axe';
import { expect, describe, it } from 'vitest';
import { KnowledgeCheck } from '../KnowledgeCheck';

expect.extend(toHaveNoViolations);

const sampleQuestion = {
  type: 'single-choice',
  stem: 'Which verification method is most effective against CEO fraud?',
  options: [
    { text: 'Checking the email header', correct: false },
    { text: 'Out-of-band verification (phone call)', correct: true },
    { text: 'Replying to the email to confirm', correct: false },
  ],
  feedback: {
    correct: 'Out-of-band verification breaks the attacker\'s control.',
    incorrect: 'The attacker controls the email channel.',
  },
};

describe('KnowledgeCheck accessibility', () => {
  it('has no axe violations in initial state', async () => {
    const { container } = render(
      <KnowledgeCheck question={sampleQuestion} onAnswer={() => {}} />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has no axe violations after submission', async () => {
    const { container, getByLabelText, getByText } = render(
      <KnowledgeCheck question={sampleQuestion} onAnswer={() => {}} />
    );

    // Select an answer
    const option = getByLabelText(/Out-of-band verification/);
    option.click();

    // Submit
    const submitBtn = getByText('Check Answer');
    submitBtn.click();

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('associates feedback with the question via aria-describedby', async () => {
    const { getByLabelText, getByText, getByRole } = render(
      <KnowledgeCheck question={sampleQuestion} onAnswer={() => {}} />
    );

    getByLabelText(/Out-of-band verification/).click();
    getByText('Check Answer').click();

    const feedback = getByRole('alert');
    expect(feedback).toBeInTheDocument();
    expect(feedback).toHaveAttribute('id', 'feedback');
  });

  it('uses radiogroup role for single-choice options', () => {
    const { getByRole } = render(
      <KnowledgeCheck question={sampleQuestion} onAnswer={() => {}} />
    );
    expect(getByRole('radiogroup')).toBeInTheDocument();
  });
});
```

**Drag-and-drop accessibility test:**

```tsx
// src/components/interactions/__tests__/DragDropSort.a11y.test.tsx
import { render, fireEvent } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'vitest-axe';
import { expect, describe, it } from 'vitest';
import { DragDropSort } from '../DragDropSort';

expect.extend(toHaveNoViolations);

const sampleItems = [
  { id: '1', text: 'Identify the incident', correctPosition: 1 },
  { id: '2', text: 'Contain the threat', correctPosition: 2 },
  { id: '3', text: 'Eradicate the root cause', correctPosition: 3 },
];

describe('DragDropSort accessibility', () => {
  it('has no axe violations', async () => {
    const { container } = render(
      <DragDropSort items={sampleItems} stem="Order these steps:" onComplete={() => {}} />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('supports keyboard reordering with arrow keys', () => {
    const { getAllByRole } = render(
      <DragDropSort items={sampleItems} stem="Order these steps:" onComplete={() => {}} />
    );

    const options = getAllByRole('option');
    options[0].focus();
    fireEvent.keyDown(options[0], { key: 'ArrowDown' });

    // Item should have moved down
    const updatedOptions = getAllByRole('option');
    expect(updatedOptions[0]).not.toHaveTextContent(options[0].textContent!);
  });

  it('announces position to screen readers via aria-label', () => {
    const { getAllByRole } = render(
      <DragDropSort items={sampleItems} stem="Order these steps:" onComplete={() => {}} />
    );

    const options = getAllByRole('option');
    options.forEach((option, i) => {
      expect(option.getAttribute('aria-label')).toContain(`Position ${i + 1}`);
    });
  });

  it('provides screen-reader-only instructions', () => {
    const { container } = render(
      <DragDropSort items={sampleItems} stem="Order these steps:" onComplete={() => {}} />
    );

    const srInstructions = container.querySelector('.sr-only');
    expect(srInstructions).toBeInTheDocument();
    expect(srInstructions).toHaveTextContent(/arrow keys/i);
  });
});
```

### 1.2 axe-core with Playwright (Full-Page Audits)

Test complete rendered pages including LMS chrome, navigation, and multi-component interactions.

**Install dependencies:**

```bash
npm install -D @playwright/test @axe-core/playwright
```

**Playwright config:**

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'e2e/results/a11y-report.json' }],
  ],
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
});
```

**Full-page accessibility tests:**

```typescript
// e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Course accessibility', () => {
  test('home page has no WCAG AA violations', async ({ page }) => {
    await page.goto('/');
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('module content page has no violations', async ({ page }) => {
    await page.goto('/module/01-introduction');
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('quiz interaction has no violations during full lifecycle', async ({ page }) => {
    await page.goto('/module/01-introduction');

    // Navigate to quiz section
    await page.click('[data-testid="next-section"]');

    // Check initial state
    let results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    expect(results.violations).toEqual([]);

    // Select an answer
    await page.click('input[name="answer"][value="1"]');

    // Submit
    await page.click('button:has-text("Check Answer")');

    // Check feedback state
    results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    expect(results.violations).toEqual([]);
  });

  test('branching scenario has no violations across scene transitions', async ({ page }) => {
    await page.goto('/module/01-introduction/scenario');

    // Check opening scene
    let results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    expect(results.violations).toEqual([]);

    // Make a choice
    await page.click('.choice-button:first-child');
    await page.waitForTimeout(500); // Wait for transition animation

    // Check next scene
    results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    expect(results.violations).toEqual([]);
  });

  test('course is navigable entirely by keyboard', async ({ page }) => {
    await page.goto('/');

    // Tab to first interactive element
    await page.keyboard.press('Tab');
    const firstFocused = await page.evaluate(() => document.activeElement?.tagName);
    expect(firstFocused).toBeTruthy();

    // Navigate through module list
    await page.keyboard.press('Enter');
    await page.waitForURL(/\/module\//);

    // Tab through content
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => ({
        tag: document.activeElement?.tagName,
        role: document.activeElement?.getAttribute('role'),
        visible: document.activeElement?.getBoundingClientRect().width > 0,
      }));
      // Every focused element must be visible (no off-screen focus traps)
      if (focused.tag !== 'BODY') {
        expect(focused.visible).toBe(true);
      }
    }
  });

  test('respects prefers-reduced-motion', async ({ page }) => {
    // Emulate reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto('/module/01-introduction');

    // Verify no CSS animations/transitions are running
    const hasAnimations = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      for (const el of elements) {
        const style = getComputedStyle(el);
        if (style.animationName !== 'none' && style.animationDuration !== '0s') {
          return true;
        }
      }
      return false;
    });

    expect(hasAnimations).toBe(false);
  });

  test('focus moves to feedback after quiz submission', async ({ page }) => {
    await page.goto('/module/01-introduction');
    await page.click('[data-testid="next-section"]');

    // Select and submit
    await page.click('input[name="answer"][value="0"]');
    await page.click('button:has-text("Check Answer")');

    // Focus should be on or near the feedback element
    const focusedRole = await page.evaluate(() =>
      document.activeElement?.getAttribute('role')
    );
    // Feedback should be announced (either focused or in an aria-live region)
    const liveRegion = await page.locator('[role="alert"]').isVisible();
    expect(liveRegion).toBe(true);
  });

  test('all images have alt text', async ({ page }) => {
    await page.goto('/module/01-introduction');

    const imagesWithoutAlt = await page.evaluate(() => {
      const images = document.querySelectorAll('img');
      return Array.from(images)
        .filter(img => {
          // Decorative images must have alt="" and role="presentation"
          if (img.getAttribute('role') === 'presentation') {
            return img.getAttribute('alt') !== '';
          }
          // Content images must have meaningful alt text
          return !img.getAttribute('alt');
        })
        .map(img => img.src);
    });

    expect(imagesWithoutAlt).toEqual([]);
  });

  test('video elements have captions', async ({ page }) => {
    await page.goto('/module/01-introduction');

    const videosWithoutCaptions = await page.evaluate(() => {
      const videos = document.querySelectorAll('video');
      return Array.from(videos)
        .filter(video => !video.querySelector('track[kind="captions"]'))
        .map(video => video.src);
    });

    expect(videosWithoutCaptions).toEqual([]);
  });
});
```

**Accessibility report helper for CI output:**

```typescript
// e2e/helpers/a11y-reporter.ts
import type { AxeResults, Result } from 'axe-core';

export function formatViolations(results: AxeResults): string {
  if (results.violations.length === 0) return 'No accessibility violations found.';

  return results.violations
    .map((violation: Result) => {
      const nodes = violation.nodes
        .map(node => `  - ${node.html}\n    Fix: ${node.failureSummary}`)
        .join('\n');
      return `[${violation.impact}] ${violation.id}: ${violation.description}\n` +
        `  WCAG: ${violation.tags.filter(t => t.startsWith('wcag')).join(', ')}\n` +
        `  Help: ${violation.helpUrl}\n${nodes}`;
    })
    .join('\n\n');
}
```

### 1.3 Lighthouse CI for Accessibility Scoring

Run Lighthouse in CI to track accessibility scores over time and fail builds that regress.

**Install:**

```bash
npm install -D @lhci/cli
```

**Lighthouse CI config:**

```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:5173/',
        'http://localhost:5173/module/01-introduction',
        'http://localhost:5173/module/01-introduction/scenario',
        'http://localhost:5173/module/01-introduction/quiz',
      ],
      startServerCommand: 'npm run preview',
      startServerReadyPattern: 'Local',
      numberOfRuns: 3,
      settings: {
        preset: 'desktop',
        onlyCategories: ['accessibility'],
      },
    },
    assert: {
      assertions: {
        'categories:accessibility': ['error', { minScore: 0.95 }],
        // Individual audit assertions
        'color-contrast': 'error',
        'image-alt': 'error',
        'label': 'error',
        'button-name': 'error',
        'link-name': 'error',
        'document-title': 'error',
        'html-has-lang': 'error',
        'meta-viewport': 'error',
        'heading-order': 'warn',
        'tabindex': 'warn',
        'aria-allowed-attr': 'error',
        'aria-required-attr': 'error',
        'aria-valid-attr-value': 'error',
        'aria-roles': 'error',
        'duplicate-id-aria': 'error',
        'bypass': 'error',
        'video-caption': 'error',
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

**npm scripts:**

```json
{
  "scripts": {
    "lhci:collect": "lhci collect",
    "lhci:assert": "lhci assert",
    "lhci:upload": "lhci upload",
    "lhci": "lhci autorun"
  }
}
```

### 1.4 eslint-plugin-jsx-a11y (Development-Time Checks)

Catch accessibility issues as you write code, before they reach a browser.

**Install:**

```bash
npm install -D eslint-plugin-jsx-a11y
```

**ESLint flat config:**

```javascript
// eslint.config.js
import jsxA11y from 'eslint-plugin-jsx-a11y';
import tseslint from 'typescript-eslint';
import react from 'eslint-plugin-react';

export default [
  ...tseslint.configs.recommended,
  {
    plugins: {
      'jsx-a11y': jsxA11y,
      react,
    },
    rules: {
      // Error-level: violations that break accessibility
      'jsx-a11y/alt-text': 'error',
      'jsx-a11y/anchor-has-content': 'error',
      'jsx-a11y/anchor-is-valid': 'error',
      'jsx-a11y/aria-activedescendant-has-tabindex': 'error',
      'jsx-a11y/aria-props': 'error',
      'jsx-a11y/aria-proptypes': 'error',
      'jsx-a11y/aria-role': 'error',
      'jsx-a11y/aria-unsupported-elements': 'error',
      'jsx-a11y/click-events-have-key-events': 'error',
      'jsx-a11y/heading-has-content': 'error',
      'jsx-a11y/html-has-lang': 'error',
      'jsx-a11y/iframe-has-title': 'error',
      'jsx-a11y/img-redundant-alt': 'error',
      'jsx-a11y/interactive-supports-focus': 'error',
      'jsx-a11y/label-has-associated-control': 'error',
      'jsx-a11y/media-has-caption': 'error',
      'jsx-a11y/mouse-events-have-key-events': 'error',
      'jsx-a11y/no-access-key': 'error',
      'jsx-a11y/no-autofocus': ['error', { ignoreNonDOM: true }],
      'jsx-a11y/no-distracting-elements': 'error',
      'jsx-a11y/no-interactive-element-to-noninteractive-role': 'error',
      'jsx-a11y/no-noninteractive-element-interactions': 'error',
      'jsx-a11y/no-noninteractive-element-to-interactive-role': 'error',
      'jsx-a11y/no-noninteractive-tabindex': 'error',
      'jsx-a11y/no-redundant-roles': 'error',
      'jsx-a11y/no-static-element-interactions': 'error',
      'jsx-a11y/role-has-required-aria-props': 'error',
      'jsx-a11y/role-supports-aria-props': 'error',
      'jsx-a11y/scope': 'error',
      'jsx-a11y/tabindex-no-positive': 'error',

      // Warning-level: best practices for courseware
      'jsx-a11y/autocomplete-valid': 'warn',
      'jsx-a11y/lang': 'warn',
      'jsx-a11y/no-onchange': 'warn',
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
];
```

### 1.5 pa11y for CLI-Based Testing

Run accessibility checks from the command line, useful for quick spot-checks and CI pipelines.

**Install:**

```bash
npm install -D pa11y pa11y-ci
```

**pa11y CI config:**

```json
// .pa11yci.json
{
  "defaults": {
    "standard": "WCAG2AA",
    "timeout": 30000,
    "wait": 2000,
    "runners": ["axe", "htmlcs"],
    "chromeLaunchConfig": {
      "args": ["--no-sandbox"]
    },
    "ignore": []
  },
  "urls": [
    {
      "url": "http://localhost:5173/",
      "screenCapture": "./pa11y-screenshots/home.png"
    },
    {
      "url": "http://localhost:5173/module/01-introduction",
      "screenCapture": "./pa11y-screenshots/module-01.png",
      "actions": [
        "wait for element .content-block to be visible"
      ]
    },
    {
      "url": "http://localhost:5173/module/01-introduction/scenario",
      "screenCapture": "./pa11y-screenshots/scenario.png",
      "actions": [
        "wait for element .scenario to be visible"
      ]
    },
    {
      "url": "http://localhost:5173/module/01-introduction/quiz",
      "screenCapture": "./pa11y-screenshots/quiz.png",
      "actions": [
        "wait for element .knowledge-check to be visible"
      ]
    }
  ]
}
```

**npm scripts for pa11y:**

```json
{
  "scripts": {
    "pa11y": "pa11y-ci --config .pa11yci.json",
    "pa11y:single": "pa11y --standard WCAG2AA --runner axe --runner htmlcs"
  }
}
```

### 1.6 CI/CD Workflow (GitHub Actions)

Combine all tools into a single CI pipeline.

```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-a11y:
    name: ESLint A11y
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npx eslint src/ --max-warnings 0

  unit-a11y:
    name: Component A11y (axe + Vitest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npx vitest run --reporter=verbose src/**/*.a11y.test.*

  e2e-a11y:
    name: Full-Page A11y (axe + Playwright)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test e2e/accessibility.spec.ts
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-a11y-report
          path: playwright-report/

  lighthouse-a11y:
    name: Lighthouse Accessibility Score
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - run: npx @lhci/cli autorun
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: lighthouse-report
          path: .lighthouseci/

  pa11y-a11y:
    name: pa11y Standards Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - run: npx serve -s dist -l 5173 &
      - run: sleep 3 && npx pa11y-ci --config .pa11yci.json
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: pa11y-screenshots
          path: pa11y-screenshots/
```

**Complete npm scripts section (all tools combined):**

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:a11y": "vitest run src/**/*.a11y.test.*",
    "test:e2e": "playwright test",
    "test:e2e:a11y": "playwright test e2e/accessibility.spec.ts",
    "lint": "eslint src/",
    "pa11y": "pa11y-ci --config .pa11yci.json",
    "pa11y:single": "pa11y --standard WCAG2AA --runner axe --runner htmlcs",
    "lhci": "lhci autorun",
    "a11y": "npm run lint && npm run test:a11y && npm run test:e2e:a11y",
    "a11y:full": "npm run a11y && npm run pa11y && npm run lhci"
  }
}
```

---

## 2. Courseware-Specific Accessibility Patterns

### 2.1 Drag-and-Drop: Keyboard Alternative (Select-Then-Place)

Mouse-based drag-and-drop excludes keyboard and switch-device users. Always implement a parallel keyboard interaction mode.

**Pattern: Arrow keys to reorder, Space/Enter to pick up and drop.**

```tsx
// interactions/AccessibleDragDrop.tsx
import { useState, useRef, useCallback } from 'react';

interface DragItem {
  id: string;
  text: string;
  correctPosition: number;
}

interface AccessibleDragDropProps {
  items: DragItem[];
  stem: string;
  onComplete: (correct: boolean) => void;
}

export function AccessibleDragDrop({ items: initial, stem, onComplete }: AccessibleDragDropProps) {
  const [items, setItems] = useState(() => [...initial].sort(() => Math.random() - 0.5));
  const [grabbedIndex, setGrabbedIndex] = useState<number | null>(null);
  const [announcement, setAnnouncement] = useState('');
  const listRef = useRef<HTMLOListElement>(null);

  const announce = useCallback((message: string) => {
    // Clear first to ensure re-announcement of identical messages
    setAnnouncement('');
    requestAnimationFrame(() => setAnnouncement(message));
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case ' ':
      case 'Enter': {
        e.preventDefault();
        if (grabbedIndex === null) {
          // Pick up
          setGrabbedIndex(index);
          announce(`Grabbed ${items[index].text}. Use arrow keys to move, Space or Enter to drop.`);
        } else {
          // Drop
          setGrabbedIndex(null);
          announce(`Dropped ${items[index].text} at position ${index + 1}.`);
        }
        break;
      }
      case 'ArrowUp': {
        e.preventDefault();
        if (index <= 0) break;

        if (grabbedIndex !== null) {
          // Move grabbed item up
          const newItems = [...items];
          [newItems[index], newItems[index - 1]] = [newItems[index - 1], newItems[index]];
          setItems(newItems);
          setGrabbedIndex(index - 1);
          announce(`${items[index].text} moved to position ${index}. Press Space to drop.`);
        }
        // Move focus up
        const prev = listRef.current?.children[index - 1] as HTMLElement;
        prev?.focus();
        break;
      }
      case 'ArrowDown': {
        e.preventDefault();
        if (index >= items.length - 1) break;

        if (grabbedIndex !== null) {
          // Move grabbed item down
          const newItems = [...items];
          [newItems[index], newItems[index + 1]] = [newItems[index + 1], newItems[index]];
          setItems(newItems);
          setGrabbedIndex(index + 1);
          announce(`${items[index].text} moved to position ${index + 2}. Press Space to drop.`);
        }
        // Move focus down
        const next = listRef.current?.children[index + 1] as HTMLElement;
        next?.focus();
        break;
      }
      case 'Escape': {
        if (grabbedIndex !== null) {
          setGrabbedIndex(null);
          announce(`Cancelled. ${items[index].text} remains at position ${index + 1}.`);
        }
        break;
      }
    }
  }, [items, grabbedIndex, announce]);

  function checkAnswer() {
    const correct = items.every((item, i) => item.correctPosition === i + 1);
    onComplete(correct);
    announce(correct ? 'Correct order!' : 'Not quite. Try reordering the items.');
  }

  return (
    <div className="drag-sort" role="region" aria-label={stem}>
      <p id="drag-stem" className="stem">{stem}</p>

      {/* Screen reader instructions */}
      <p id="drag-instructions" className="sr-only">
        Reorderable list. Use Tab to move between items. Press Space or Enter to
        grab an item, then use Arrow Up and Arrow Down to move it. Press Space or
        Enter again to drop it. Press Escape to cancel.
      </p>

      {/* Live region for screen reader announcements */}
      <div aria-live="assertive" aria-atomic="true" className="sr-only" role="status">
        {announcement}
      </div>

      <ol
        ref={listRef}
        className="sortable-list"
        role="listbox"
        aria-roledescription="reorderable list"
        aria-labelledby="drag-stem"
        aria-describedby="drag-instructions"
      >
        {items.map((item, i) => (
          <li
            key={item.id}
            role="option"
            tabIndex={0}
            draggable
            aria-selected={grabbedIndex === i}
            aria-label={`${item.text}. Position ${i + 1} of ${items.length}.`}
            onKeyDown={(e) => handleKeyDown(e, i)}
            className={`sortable-item ${grabbedIndex === i ? 'grabbed' : ''}`}
          >
            <span className="drag-handle" aria-hidden="true">&#x2807;</span>
            <span className="position-number" aria-hidden="true">{i + 1}.</span>
            {item.text}
          </li>
        ))}
      </ol>

      <button onClick={checkAnswer}>Check Order</button>
    </div>
  );
}
```

**Required CSS for screen-reader-only content:**

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
  border-width: 0;
}

.sortable-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 2px solid transparent;
  border-radius: 0.375rem;
  cursor: grab;
  transition: background-color 0.15s, border-color 0.15s;
}

.sortable-item:focus {
  outline: 3px solid #2563eb;
  outline-offset: 2px;
}

.sortable-item.grabbed {
  background-color: #dbeafe;
  border-color: #2563eb;
  cursor: grabbing;
}

.sortable-item:focus:not(:focus-visible) {
  outline: none;
}

.sortable-item:focus-visible {
  outline: 3px solid #2563eb;
  outline-offset: 2px;
}
```

### 2.2 Quiz Interactions: Focus Management and Screen Reader Feedback

After submitting a quiz answer, focus must move to the feedback so screen reader users know the result immediately.

```tsx
// interactions/AccessibleQuiz.tsx
import { useState, useRef, useEffect } from 'react';

interface QuizOption {
  text: string;
  correct: boolean;
}

interface QuizQuestion {
  stem: string;
  options: QuizOption[];
  feedback: { correct: string; incorrect: string };
}

interface AccessibleQuizProps {
  question: QuizQuestion;
  onAnswer: (correct: boolean) => void;
}

export function AccessibleQuiz({ question, onAnswer }: AccessibleQuizProps) {
  const [selected, setSelected] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const feedbackRef = useRef<HTMLDivElement>(null);
  const submitRef = useRef<HTMLButtonElement>(null);

  // After submission, move focus to feedback
  useEffect(() => {
    if (submitted && feedbackRef.current) {
      feedbackRef.current.focus();
    }
  }, [submitted]);

  function handleSubmit() {
    if (selected === null) return;
    setSubmitted(true);
    onAnswer(question.options[selected].correct);
  }

  function handleOptionKeyDown(e: React.KeyboardEvent, index: number) {
    const optionCount = question.options.length;
    let nextIndex = index;

    switch (e.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        e.preventDefault();
        nextIndex = (index + 1) % optionCount;
        break;
      case 'ArrowUp':
      case 'ArrowLeft':
        e.preventDefault();
        nextIndex = (index - 1 + optionCount) % optionCount;
        break;
      default:
        return;
    }

    setSelected(nextIndex);
    // Move focus to the newly selected radio
    const radioGroup = (e.currentTarget as HTMLElement).closest('[role="radiogroup"]');
    const nextRadio = radioGroup?.querySelectorAll('input[type="radio"]')[nextIndex] as HTMLElement;
    nextRadio?.focus();
  }

  const isCorrect = selected !== null && question.options[selected].correct;
  const feedbackText = submitted
    ? (isCorrect ? question.feedback.correct : question.feedback.incorrect)
    : '';

  return (
    <fieldset className="quiz" aria-describedby={submitted ? 'quiz-feedback' : undefined}>
      <legend className="question-stem">{question.stem}</legend>

      <div role="radiogroup" aria-required="true">
        {question.options.map((option, i) => (
          <div key={i} className="option-wrapper">
            <label
              className={[
                'option',
                submitted && option.correct ? 'option--correct' : '',
                submitted && selected === i && !option.correct ? 'option--incorrect' : '',
              ].join(' ')}
            >
              <input
                type="radio"
                name="quiz-answer"
                value={i}
                checked={selected === i}
                onChange={() => !submitted && setSelected(i)}
                onKeyDown={(e) => handleOptionKeyDown(e, i)}
                disabled={submitted}
                aria-describedby={submitted ? 'quiz-feedback' : undefined}
              />
              <span>{option.text}</span>
              {submitted && option.correct && (
                <span className="sr-only">(correct answer)</span>
              )}
            </label>
          </div>
        ))}
      </div>

      {!submitted && (
        <button
          ref={submitRef}
          onClick={handleSubmit}
          disabled={selected === null}
          aria-disabled={selected === null}
        >
          Check Answer
        </button>
      )}

      {submitted && (
        <div
          ref={feedbackRef}
          id="quiz-feedback"
          className={`feedback feedback--${isCorrect ? 'correct' : 'incorrect'}`}
          role="alert"
          tabIndex={-1}
          aria-live="assertive"
        >
          <strong>{isCorrect ? 'Correct!' : 'Not quite.'}</strong>
          <p>{feedbackText}</p>
        </div>
      )}
    </fieldset>
  );
}
```

### 2.3 Branching Scenarios: Announcing Consequences and Managing Focus

Scene transitions in branching scenarios must announce the new context and move focus appropriately.

```tsx
// interactions/AccessibleScenario.tsx
import { useState, useRef, useEffect, useCallback } from 'react';

interface Scene {
  id: string;
  narration: string;
  feedback?: { type: 'positive' | 'negative' | 'neutral'; text: string };
  choices: Array<{ text: string; next: string; points?: number }>;
  isEnding?: boolean;
}

interface AccessibleScenarioProps {
  scenes: Scene[];
  title: string;
  onComplete: (score: number, path: string[]) => void;
}

export function AccessibleScenario({ scenes, title, onComplete }: AccessibleScenarioProps) {
  const [currentSceneId, setCurrentSceneId] = useState(scenes[0].id);
  const [score, setScore] = useState(0);
  const [path, setPath] = useState<string[]>([scenes[0].id]);
  const [announcement, setAnnouncement] = useState('');

  const sceneRef = useRef<HTMLDivElement>(null);
  const firstChoiceRef = useRef<HTMLButtonElement>(null);

  const scene = scenes.find(s => s.id === currentSceneId)!;

  // When scene changes, move focus to the scene container and announce it
  useEffect(() => {
    if (sceneRef.current) {
      sceneRef.current.focus();
    }
  }, [currentSceneId]);

  const announce = useCallback((message: string) => {
    setAnnouncement('');
    requestAnimationFrame(() => setAnnouncement(message));
  }, []);

  function handleChoice(choice: typeof scene.choices[0]) {
    const newScore = score + (choice.points || 0);
    setScore(newScore);
    const newPath = [...path, choice.next];
    setPath(newPath);

    const nextScene = scenes.find(s => s.id === choice.next);
    if (!nextScene || nextScene.isEnding) {
      onComplete(newScore, newPath);
      announce('Scenario complete.');
      return;
    }

    // Announce consequence before transitioning
    if (nextScene.feedback) {
      const feedbackLabel = nextScene.feedback.type === 'positive'
        ? 'Good choice.'
        : nextScene.feedback.type === 'negative'
        ? 'That could go better.'
        : '';
      announce(`${feedbackLabel} ${nextScene.feedback.text}`);
    }

    setCurrentSceneId(choice.next);
  }

  function handleChoiceKeyDown(e: React.KeyboardEvent, index: number) {
    const choices = scene.choices;
    let nextIndex = index;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        nextIndex = Math.min(index + 1, choices.length - 1);
        break;
      case 'ArrowUp':
        e.preventDefault();
        nextIndex = Math.max(index - 1, 0);
        break;
      default:
        return;
    }

    const buttons = sceneRef.current?.querySelectorAll('.choice-button');
    (buttons?.[nextIndex] as HTMLElement)?.focus();
  }

  return (
    <section aria-label={`Scenario: ${title}`}>
      {/* Live region for consequence announcements */}
      <div aria-live="assertive" aria-atomic="true" className="sr-only" role="log">
        {announcement}
      </div>

      {/* Progress indicator */}
      <div
        role="status"
        aria-label={`Scenario progress: scene ${path.length} of approximately ${scenes.length}`}
        className="sr-only"
      >
        Scene {path.length}
      </div>

      <div
        ref={sceneRef}
        className="scene"
        tabIndex={-1}
        role="region"
        aria-label={`Scene: ${scene.narration.substring(0, 50)}...`}
        aria-live="polite"
      >
        <p className="narration">{scene.narration}</p>

        {scene.feedback && (
          <div
            className={`feedback feedback--${scene.feedback.type}`}
            role="alert"
          >
            {scene.feedback.text}
          </div>
        )}

        <nav aria-label="Scenario choices">
          <p id="choice-instructions" className="sr-only">
            Choose a response. Use arrow keys to move between options, Enter to select.
          </p>
          <div
            className="choices"
            role="group"
            aria-labelledby="choice-instructions"
          >
            {scene.choices.map((choice, i) => (
              <button
                key={i}
                ref={i === 0 ? firstChoiceRef : undefined}
                className="choice-button"
                onClick={() => handleChoice(choice)}
                onKeyDown={(e) => handleChoiceKeyDown(e, i)}
                aria-label={`Option ${i + 1} of ${scene.choices.length}: ${choice.text}`}
              >
                {choice.text}
              </button>
            ))}
          </div>
        </nav>
      </div>
    </section>
  );
}
```

### 2.4 Interactive Video: Keyboard Controls, Captions, Audio Description

Custom video players must expose all controls to keyboard and provide captions and audio descriptions.

```tsx
// media/AccessibleVideoPlayer.tsx
import { useState, useRef, useEffect, useCallback } from 'react';

interface VideoPlayerProps {
  src: string;
  captionSrc: string;
  audioDescriptionSrc?: string;
  title: string;
  onTimeUpdate?: (time: number) => void;
}

export function AccessibleVideoPlayer({
  src,
  captionSrc,
  audioDescriptionSrc,
  title,
  onTimeUpdate,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const audioDescRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [muted, setMuted] = useState(false);
  const [captionsOn, setCaptionsOn] = useState(true);
  const [audioDescOn, setAudioDescOn] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [announcement, setAnnouncement] = useState('');

  const announce = useCallback((msg: string) => {
    setAnnouncement('');
    requestAnimationFrame(() => setAnnouncement(msg));
  }, []);

  // Sync audio description with video
  useEffect(() => {
    if (!audioDescRef.current || !videoRef.current) return;
    if (audioDescOn) {
      audioDescRef.current.currentTime = videoRef.current.currentTime;
      if (playing) audioDescRef.current.play();
    } else {
      audioDescRef.current.pause();
    }
  }, [audioDescOn, playing]);

  function togglePlay() {
    const video = videoRef.current!;
    if (video.paused) {
      video.play();
      setPlaying(true);
      announce('Playing');
    } else {
      video.pause();
      setPlaying(false);
      announce('Paused');
    }
  }

  function seek(seconds: number) {
    const video = videoRef.current!;
    video.currentTime = Math.max(0, Math.min(video.currentTime + seconds, duration));
    announce(`Seeked to ${formatTime(video.currentTime)}`);
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    switch (e.key) {
      case ' ':
      case 'k':
        e.preventDefault();
        togglePlay();
        break;
      case 'ArrowLeft':
        e.preventDefault();
        seek(-5);
        break;
      case 'ArrowRight':
        e.preventDefault();
        seek(5);
        break;
      case 'ArrowUp':
        e.preventDefault();
        setVolume(v => {
          const newVol = Math.min(1, v + 0.1);
          videoRef.current!.volume = newVol;
          announce(`Volume ${Math.round(newVol * 100)}%`);
          return newVol;
        });
        break;
      case 'ArrowDown':
        e.preventDefault();
        setVolume(v => {
          const newVol = Math.max(0, v - 0.1);
          videoRef.current!.volume = newVol;
          announce(`Volume ${Math.round(newVol * 100)}%`);
          return newVol;
        });
        break;
      case 'm':
        e.preventDefault();
        setMuted(m => {
          const newMuted = !m;
          videoRef.current!.muted = newMuted;
          announce(newMuted ? 'Muted' : 'Unmuted');
          return newMuted;
        });
        break;
      case 'c':
        e.preventDefault();
        setCaptionsOn(c => {
          const newState = !c;
          announce(newState ? 'Captions on' : 'Captions off');
          return newState;
        });
        break;
      case 'f':
        e.preventDefault();
        if (document.fullscreenElement) {
          document.exitFullscreen();
        } else {
          videoRef.current!.requestFullscreen();
        }
        break;
    }
  }

  function formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  return (
    <div
      className="video-player"
      role="region"
      aria-label={`Video player: ${title}`}
      onKeyDown={handleKeyDown}
    >
      {/* Screen reader announcements */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {announcement}
      </div>

      <video
        ref={videoRef}
        src={src}
        onTimeUpdate={() => {
          const t = videoRef.current!.currentTime;
          setCurrentTime(t);
          onTimeUpdate?.(t);
        }}
        onLoadedMetadata={() => setDuration(videoRef.current!.duration)}
        aria-label={title}
      >
        <track
          kind="captions"
          src={captionSrc}
          label="English captions"
          default={captionsOn}
        />
        {audioDescriptionSrc && (
          <track
            kind="descriptions"
            src={audioDescriptionSrc}
            label="Audio descriptions"
          />
        )}
      </video>

      {/* Audio description track (separate audio element for browser support) */}
      {audioDescriptionSrc && (
        <audio ref={audioDescRef} src={audioDescriptionSrc} />
      )}

      {/* Custom controls — all keyboard accessible */}
      <div className="controls" role="toolbar" aria-label="Video controls">
        <button
          onClick={togglePlay}
          aria-label={playing ? 'Pause' : 'Play'}
        >
          {playing ? 'Pause' : 'Play'}
        </button>

        {/* Seek slider */}
        <label className="sr-only" htmlFor="seek-slider">Seek</label>
        <input
          id="seek-slider"
          type="range"
          min={0}
          max={duration}
          value={currentTime}
          onChange={(e) => {
            videoRef.current!.currentTime = Number(e.target.value);
          }}
          aria-label={`Seek: ${formatTime(currentTime)} of ${formatTime(duration)}`}
          aria-valuetext={`${formatTime(currentTime)} of ${formatTime(duration)}`}
        />

        <span aria-hidden="true">{formatTime(currentTime)} / {formatTime(duration)}</span>

        {/* Volume */}
        <button
          onClick={() => {
            setMuted(m => !m);
            videoRef.current!.muted = !muted;
          }}
          aria-label={muted ? 'Unmute' : 'Mute'}
        >
          {muted ? 'Unmute' : 'Mute'}
        </button>

        <label className="sr-only" htmlFor="volume-slider">Volume</label>
        <input
          id="volume-slider"
          type="range"
          min={0}
          max={1}
          step={0.1}
          value={muted ? 0 : volume}
          onChange={(e) => {
            const v = Number(e.target.value);
            setVolume(v);
            videoRef.current!.volume = v;
            setMuted(v === 0);
          }}
          aria-label={`Volume: ${Math.round(volume * 100)}%`}
          aria-valuetext={`${Math.round(volume * 100)}%`}
        />

        {/* Captions toggle */}
        <button
          onClick={() => setCaptionsOn(c => !c)}
          aria-label={captionsOn ? 'Turn off captions' : 'Turn on captions'}
          aria-pressed={captionsOn}
        >
          CC {captionsOn ? 'On' : 'Off'}
        </button>

        {/* Audio description toggle */}
        {audioDescriptionSrc && (
          <button
            onClick={() => setAudioDescOn(a => !a)}
            aria-label={audioDescOn ? 'Turn off audio descriptions' : 'Turn on audio descriptions'}
            aria-pressed={audioDescOn}
          >
            AD {audioDescOn ? 'On' : 'Off'}
          </button>
        )}

        {/* Playback speed */}
        <label className="sr-only" htmlFor="speed-select">Playback speed</label>
        <select
          id="speed-select"
          value={playbackRate}
          onChange={(e) => {
            const rate = Number(e.target.value);
            setPlaybackRate(rate);
            videoRef.current!.playbackRate = rate;
            announce(`Playback speed: ${rate}x`);
          }}
          aria-label="Playback speed"
        >
          <option value={0.5}>0.5x</option>
          <option value={0.75}>0.75x</option>
          <option value={1}>1x</option>
          <option value={1.25}>1.25x</option>
          <option value={1.5}>1.5x</option>
          <option value={2}>2x</option>
        </select>

        {/* Keyboard shortcut help */}
        <button
          onClick={() => announce(
            'Keyboard shortcuts: Space or K to play/pause, Left arrow to rewind 5 seconds, ' +
            'Right arrow to forward 5 seconds, Up arrow to increase volume, Down arrow to decrease volume, ' +
            'M to mute, C to toggle captions, F for fullscreen.'
          )}
          aria-label="Keyboard shortcuts"
        >
          ?
        </button>
      </div>
    </div>
  );
}
```

### 2.5 Scroll-Driven Animations: prefers-reduced-motion Fallbacks

Users who experience motion sickness or vestibular disorders must get a fully functional, static alternative.

```tsx
// hooks/useReducedMotion.ts
import { useState, useEffect } from 'react';

export function useReducedMotion(): boolean {
  const [prefersReduced, setPrefersReduced] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  });

  useEffect(() => {
    const mql = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handler = (e: MediaQueryListEvent) => setPrefersReduced(e.matches);
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, []);

  return prefersReduced;
}
```

```tsx
// interactions/AccessibleScrollStory.tsx
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useReducedMotion } from '../hooks/useReducedMotion';

gsap.registerPlugin(ScrollTrigger);

interface StorySection {
  id: string;
  title: string;
  content: string;
  visual: string;
  visualAlt: string;
}

export function AccessibleScrollStory({ sections }: { sections: StorySection[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const prefersReduced = useReducedMotion();

  useEffect(() => {
    if (prefersReduced) return; // Skip all animation setup

    const ctx = gsap.context(() => {
      sections.forEach((section) => {
        const el = document.getElementById(`section-${section.id}`);
        if (!el) return;

        gsap.fromTo(el, {
          opacity: 0,
          y: 40,
        }, {
          opacity: 1,
          y: 0,
          duration: 0.6,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 80%',
            toggleActions: 'play none none reverse',
          },
        });
      });
    }, containerRef);

    return () => ctx.revert();
  }, [sections, prefersReduced]);

  return (
    <div ref={containerRef} className="scroll-story">
      {sections.map((section) => (
        <section
          key={section.id}
          id={`section-${section.id}`}
          className="story-section"
          // When motion is reduced, all content is visible immediately
          style={prefersReduced ? { opacity: 1, transform: 'none' } : undefined}
        >
          <div className="section-content">
            <h2>{section.title}</h2>
            <p>{section.content}</p>
          </div>
          <div className="section-visual">
            <img src={section.visual} alt={section.visualAlt} />
          </div>
        </section>
      ))}
    </div>
  );
}
```

**CSS fallback for reduced motion:**

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

  .story-section {
    opacity: 1 !important;
    transform: none !important;
  }

  .scroll-progress-bar {
    /* Keep progress bar — it's informational, not decorative */
    transition: width 0.1s linear;
  }
}
```

### 2.6 Progress Tracking: aria-progressbar and Milestone Announcements

```tsx
// components/CourseProgress.tsx
import { useEffect, useRef, useState } from 'react';

interface CourseProgressProps {
  completed: number;
  total: number;
  currentModule: string;
  milestones: Array<{ at: number; label: string }>;
}

export function CourseProgress({ completed, total, currentModule, milestones }: CourseProgressProps) {
  const [lastAnnounced, setLastAnnounced] = useState(0);
  const [announcement, setAnnouncement] = useState('');
  const percentage = Math.round((completed / total) * 100);

  // Announce milestones when reached
  useEffect(() => {
    const reached = milestones.filter(m => m.at <= percentage && m.at > lastAnnounced);
    if (reached.length > 0) {
      const latest = reached[reached.length - 1];
      setAnnouncement(`Milestone reached: ${latest.label}. ${percentage}% complete.`);
      setLastAnnounced(latest.at);
    }
  }, [percentage, milestones, lastAnnounced]);

  return (
    <div className="course-progress">
      {/* Live announcement for milestones */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {announcement}
      </div>

      <div
        role="progressbar"
        aria-valuenow={percentage}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Course progress: ${percentage}% complete. Currently on ${currentModule}.`}
        aria-valuetext={`${completed} of ${total} sections complete (${percentage}%)`}
        className="progress-bar-track"
      >
        <div
          className="progress-bar-fill"
          style={{ width: `${percentage}%` }}
          aria-hidden="true"
        />
      </div>

      <span className="progress-text" aria-hidden="true">
        {completed}/{total} sections ({percentage}%)
      </span>
    </div>
  );
}
```

### 2.7 Timed Interactions: Extensions, Pausing, and Warnings

WCAG 2.2.1 requires users be able to turn off, adjust, or extend time limits.

```tsx
// interactions/TimedQuiz.tsx
import { useState, useEffect, useRef, useCallback } from 'react';

interface TimedQuizProps {
  timeLimit: number; // seconds
  children: React.ReactNode;
  onTimeUp: () => void;
}

export function TimedQuiz({ timeLimit, children, onTimeUp }: TimedQuizProps) {
  const [remaining, setRemaining] = useState(timeLimit);
  const [paused, setPaused] = useState(false);
  const [extensions, setExtensions] = useState(0);
  const [announcement, setAnnouncement] = useState('');
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const announce = useCallback((msg: string) => {
    setAnnouncement('');
    requestAnimationFrame(() => setAnnouncement(msg));
  }, []);

  useEffect(() => {
    if (paused) return;

    intervalRef.current = setInterval(() => {
      setRemaining(prev => {
        if (prev <= 1) {
          clearInterval(intervalRef.current);
          onTimeUp();
          return 0;
        }

        // Announce warnings at key thresholds
        if (prev === 60) announce('One minute remaining.');
        if (prev === 30) announce('Thirty seconds remaining.');
        if (prev === 10) announce('Ten seconds remaining. You can extend the time if needed.');

        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(intervalRef.current);
  }, [paused, onTimeUp, announce]);

  function extendTime() {
    const extension = timeLimit; // Double the original time
    setRemaining(prev => prev + extension);
    setExtensions(prev => prev + 1);
    announce(`Time extended by ${formatDuration(extension)}. ${formatDuration(remaining + extension)} remaining.`);
  }

  function togglePause() {
    setPaused(p => {
      const newPaused = !p;
      announce(newPaused ? 'Timer paused.' : 'Timer resumed.');
      return newPaused;
    });
  }

  function formatDuration(seconds: number): string {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    if (m === 0) return `${s} seconds`;
    if (s === 0) return `${m} minute${m !== 1 ? 's' : ''}`;
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  const percentage = (remaining / (timeLimit + extensions * timeLimit)) * 100;
  const isLow = remaining <= 30;

  return (
    <div className="timed-quiz">
      {/* Announcements */}
      <div aria-live="assertive" aria-atomic="true" className="sr-only">
        {announcement}
      </div>

      {/* Timer display */}
      <div className="timer-bar" role="timer" aria-label={`Time remaining: ${formatDuration(remaining)}`}>
        <div
          role="progressbar"
          aria-valuenow={remaining}
          aria-valuemin={0}
          aria-valuemax={timeLimit}
          aria-valuetext={`${formatDuration(remaining)} remaining`}
          className={`timer-fill ${isLow ? 'timer-fill--low' : ''}`}
          style={{ width: `${percentage}%` }}
        />
        <span className="timer-text" aria-hidden="true">
          {formatDuration(remaining)} {paused && '(paused)'}
        </span>
      </div>

      {/* Timer controls — WCAG 2.2.1 compliance */}
      <div className="timer-controls" role="group" aria-label="Timer controls">
        <button onClick={togglePause} aria-label={paused ? 'Resume timer' : 'Pause timer'}>
          {paused ? 'Resume' : 'Pause'}
        </button>
        <button onClick={extendTime} aria-label="Extend time">
          Extend Time
        </button>
      </div>

      {children}
    </div>
  );
}
```

### 2.8 Audio Content: Transcripts, Mute Controls, Autoplay Prevention

Never autoplay audio. Always provide a transcript. Always provide visible mute/volume controls.

```tsx
// media/AccessibleAudioPlayer.tsx
import { useState, useRef } from 'react';

interface AudioPlayerProps {
  src: string;
  title: string;
  transcript: string;
}

export function AccessibleAudioPlayer({ src, title, transcript }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  function togglePlay() {
    const audio = audioRef.current!;
    if (audio.paused) {
      audio.play();
      setPlaying(true);
    } else {
      audio.pause();
      setPlaying(false);
    }
  }

  return (
    <div className="audio-player" role="region" aria-label={`Audio: ${title}`}>
      {/* Never autoplay — user must explicitly start playback */}
      <audio
        ref={audioRef}
        src={src}
        preload="metadata"
        onTimeUpdate={() => setCurrentTime(audioRef.current!.currentTime)}
        onLoadedMetadata={() => setDuration(audioRef.current!.duration)}
      />

      <div className="audio-controls" role="toolbar" aria-label="Audio controls">
        <button onClick={togglePlay} aria-label={playing ? `Pause ${title}` : `Play ${title}`}>
          {playing ? 'Pause' : 'Play'}
        </button>

        <label className="sr-only" htmlFor={`audio-seek-${title}`}>Seek</label>
        <input
          id={`audio-seek-${title}`}
          type="range"
          min={0}
          max={duration}
          value={currentTime}
          onChange={(e) => { audioRef.current!.currentTime = Number(e.target.value); }}
          aria-label="Seek position"
        />

        <span aria-hidden="true">
          {Math.floor(currentTime / 60)}:{Math.floor(currentTime % 60).toString().padStart(2, '0')}
          {' / '}
          {Math.floor(duration / 60)}:{Math.floor(duration % 60).toString().padStart(2, '0')}
        </span>
      </div>

      {/* Transcript toggle — required for accessibility */}
      <div className="transcript-section">
        <button
          onClick={() => setShowTranscript(t => !t)}
          aria-expanded={showTranscript}
          aria-controls="transcript-content"
        >
          {showTranscript ? 'Hide Transcript' : 'Show Transcript'}
        </button>

        {showTranscript && (
          <div id="transcript-content" className="transcript" role="region" aria-label="Transcript">
            <p>{transcript}</p>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## 3. ARIA Patterns for Courseware

### 3.1 aria-live Regions for Dynamic Feedback

Use `aria-live` to announce content changes that happen outside the user's current focus.

**Rules:**
- `aria-live="polite"` — announcements queue after the screen reader finishes current speech (use for non-urgent updates like narration text, score changes)
- `aria-live="assertive"` — interrupts current speech immediately (use for quiz feedback, error messages, time warnings)
- `role="alert"` — equivalent to `aria-live="assertive"` plus `aria-atomic="true"` (use for critical feedback)
- `role="status"` — equivalent to `aria-live="polite"` plus `aria-atomic="true"` (use for progress updates)

```tsx
// components/feedback/LiveAnnouncer.tsx
import { createContext, useContext, useState, useCallback, useRef } from 'react';

interface AnnouncerContextType {
  announcePolite: (message: string) => void;
  announceAssertive: (message: string) => void;
}

const AnnouncerContext = createContext<AnnouncerContextType | null>(null);

export function LiveAnnouncerProvider({ children }: { children: React.ReactNode }) {
  const [politeMessage, setPoliteMessage] = useState('');
  const [assertiveMessage, setAssertiveMessage] = useState('');
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const announcePolite = useCallback((message: string) => {
    // Clear and re-set to trigger re-announcement even for identical messages
    setPoliteMessage('');
    requestAnimationFrame(() => setPoliteMessage(message));
    // Clear after 5s to avoid stale content
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => setPoliteMessage(''), 5000);
  }, []);

  const announceAssertive = useCallback((message: string) => {
    setAssertiveMessage('');
    requestAnimationFrame(() => setAssertiveMessage(message));
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => setAssertiveMessage(''), 5000);
  }, []);

  return (
    <AnnouncerContext.Provider value={{ announcePolite, announceAssertive }}>
      {children}
      {/* These live regions must always be in the DOM */}
      <div
        aria-live="polite"
        aria-atomic="true"
        role="status"
        className="sr-only"
      >
        {politeMessage}
      </div>
      <div
        aria-live="assertive"
        aria-atomic="true"
        role="alert"
        className="sr-only"
      >
        {assertiveMessage}
      </div>
    </AnnouncerContext.Provider>
  );
}

export function useAnnounce() {
  const ctx = useContext(AnnouncerContext);
  if (!ctx) throw new Error('useAnnounce must be used within LiveAnnouncerProvider');
  return ctx;
}
```

**Usage across courseware components:**

```tsx
// In quiz component
const { announceAssertive } = useAnnounce();

function handleSubmit() {
  const correct = checkAnswer();
  announceAssertive(
    correct
      ? `Correct! ${question.feedback.correct}`
      : `Incorrect. ${question.feedback.incorrect}`
  );
}

// In progress tracker
const { announcePolite } = useAnnounce();

useEffect(() => {
  if (modulesCompleted % 3 === 0 && modulesCompleted > 0) {
    announcePolite(`Great progress! You've completed ${modulesCompleted} of ${totalModules} modules.`);
  }
}, [modulesCompleted]);

// In scenario engine
const { announceAssertive } = useAnnounce();

function onSceneTransition(scene: Scene) {
  if (scene.feedback) {
    announceAssertive(`${scene.feedback.type === 'positive' ? 'Good choice.' : 'Consider the consequences.'} ${scene.feedback.text}`);
  }
}
```

### 3.2 aria-expanded for Progressive Disclosure

Use on accordion headers, expandable sections, and "read more" controls.

```tsx
// components/AccordionModule.tsx
import { useState, useRef, useEffect } from 'react';

interface AccordionSection {
  id: string;
  title: string;
  content: React.ReactNode;
}

export function AccordionModule({ sections }: { sections: AccordionSection[] }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const contentRefs = useRef<Record<string, HTMLDivElement | null>>({});

  function toggleSection(id: string) {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  // Focus the newly expanded content for screen readers
  useEffect(() => {
    expanded.forEach(id => {
      const el = contentRefs.current[id];
      if (el && !el.dataset.focused) {
        el.focus();
        el.dataset.focused = 'true';
      }
    });
  }, [expanded]);

  return (
    <div className="accordion" role="region" aria-label="Course content sections">
      {sections.map((section) => {
        const isExpanded = expanded.has(section.id);
        return (
          <div key={section.id} className="accordion-item">
            <h3>
              <button
                id={`heading-${section.id}`}
                aria-expanded={isExpanded}
                aria-controls={`content-${section.id}`}
                onClick={() => toggleSection(section.id)}
                className="accordion-trigger"
              >
                <span>{section.title}</span>
                <span aria-hidden="true">{isExpanded ? '\u2212' : '+'}</span>
              </button>
            </h3>
            <div
              id={`content-${section.id}`}
              ref={el => { contentRefs.current[section.id] = el; }}
              role="region"
              aria-labelledby={`heading-${section.id}`}
              hidden={!isExpanded}
              tabIndex={-1}
              className="accordion-content"
            >
              {section.content}
            </div>
          </div>
        );
      })}
    </div>
  );
}
```

### 3.3 role="tablist" for Module Navigation

```tsx
// components/ModuleNav.tsx
import { useState, useRef } from 'react';

interface Module {
  id: string;
  title: string;
  content: React.ReactNode;
  completed: boolean;
}

export function ModuleNav({ modules }: { modules: Module[] }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  function handleKeyDown(e: React.KeyboardEvent, index: number) {
    let nextIndex = index;

    switch (e.key) {
      case 'ArrowRight':
        e.preventDefault();
        nextIndex = (index + 1) % modules.length;
        break;
      case 'ArrowLeft':
        e.preventDefault();
        nextIndex = (index - 1 + modules.length) % modules.length;
        break;
      case 'Home':
        e.preventDefault();
        nextIndex = 0;
        break;
      case 'End':
        e.preventDefault();
        nextIndex = modules.length - 1;
        break;
      default:
        return;
    }

    setActiveIndex(nextIndex);
    tabRefs.current[nextIndex]?.focus();
  }

  return (
    <div className="module-nav">
      <div role="tablist" aria-label="Course modules" aria-orientation="horizontal">
        {modules.map((module, i) => (
          <button
            key={module.id}
            ref={el => { tabRefs.current[i] = el; }}
            role="tab"
            id={`tab-${module.id}`}
            aria-selected={i === activeIndex}
            aria-controls={`panel-${module.id}`}
            tabIndex={i === activeIndex ? 0 : -1}
            onClick={() => setActiveIndex(i)}
            onKeyDown={(e) => handleKeyDown(e, i)}
            className={`tab ${i === activeIndex ? 'tab--active' : ''}`}
          >
            {module.title}
            {module.completed && <span className="sr-only">(completed)</span>}
          </button>
        ))}
      </div>

      {modules.map((module, i) => (
        <div
          key={module.id}
          role="tabpanel"
          id={`panel-${module.id}`}
          aria-labelledby={`tab-${module.id}`}
          hidden={i !== activeIndex}
          tabIndex={0}
          className="tab-panel"
        >
          {module.content}
        </div>
      ))}
    </div>
  );
}
```

### 3.4 role="dialog" for Modal Quiz Overlays

Modal dialogs must trap focus inside and return focus to the trigger element when closed.

```tsx
// components/QuizModal.tsx
import { useEffect, useRef, useCallback } from 'react';

interface QuizModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  triggerRef: React.RefObject<HTMLElement>;
}

export function QuizModal({ open, onClose, title, children, triggerRef }: QuizModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // Store the element that had focus before the modal opened
  useEffect(() => {
    if (open) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      // Focus the dialog container after a brief delay for rendering
      requestAnimationFrame(() => {
        dialogRef.current?.focus();
      });
    }
  }, [open]);

  // Return focus when modal closes
  useEffect(() => {
    if (!open && previousFocusRef.current) {
      previousFocusRef.current.focus();
      previousFocusRef.current = null;
    }
  }, [open]);

  // Focus trap
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
      return;
    }

    if (e.key !== 'Tab') return;

    const dialog = dialogRef.current;
    if (!dialog) return;

    const focusable = dialog.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }, [onClose]);

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="modal-backdrop" aria-hidden="true" onClick={onClose} />

      {/* Dialog */}
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="quiz-modal-title"
        tabIndex={-1}
        onKeyDown={handleKeyDown}
        className="quiz-modal"
      >
        <div className="modal-header">
          <h2 id="quiz-modal-title">{title}</h2>
          <button
            onClick={onClose}
            aria-label="Close quiz"
            className="modal-close"
          >
            &times;
          </button>
        </div>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </>
  );
}
```

### 3.5 aria-describedby for Linking Questions to Feedback

Connect feedback messages to the questions they describe so screen readers communicate the relationship.

```tsx
// Pattern: question-feedback association
function QuizItem({ question, index }: { question: Question; index: number }) {
  const [submitted, setSubmitted] = useState(false);
  const questionId = `question-${index}`;
  const feedbackId = `feedback-${index}`;
  const hintId = `hint-${index}`;

  return (
    <div
      role="group"
      aria-labelledby={questionId}
      aria-describedby={[
        submitted ? feedbackId : null,
        question.hint ? hintId : null,
      ].filter(Boolean).join(' ') || undefined}
    >
      <p id={questionId}>{question.stem}</p>

      {question.hint && (
        <p id={hintId} className="hint">
          Hint: {question.hint}
        </p>
      )}

      <div role="radiogroup" aria-labelledby={questionId}>
        {question.options.map((option, i) => (
          <label key={i}>
            <input
              type="radio"
              name={`q-${index}`}
              aria-describedby={submitted ? feedbackId : undefined}
            />
            {option.text}
          </label>
        ))}
      </div>

      {submitted && (
        <div id={feedbackId} role="alert" tabIndex={-1}>
          {isCorrect ? question.feedback.correct : question.feedback.incorrect}
        </div>
      )}
    </div>
  );
}
```

---

## 4. Manual Testing Protocol

Automated tools catch roughly 30-50% of accessibility issues. The rest require manual human testing.

### 4.1 Keyboard-Only Walkthrough

Complete the entire course using only a keyboard. No mouse, no trackpad.

**Key commands to test:**

| Key | Expected behavior |
|-----|-------------------|
| **Tab** | Move focus to next interactive element |
| **Shift+Tab** | Move focus to previous interactive element |
| **Enter** | Activate buttons, links, submit forms |
| **Space** | Toggle checkboxes, activate buttons, start/stop video |
| **Arrow keys** | Navigate within radio groups, sliders, tabs, reorder drag-drop items |
| **Escape** | Close modals, cancel drag operation, dismiss overlays |
| **Home/End** | Jump to first/last tab in tablist, first/last option |

**Checklist:**

```markdown
## Keyboard Navigation Checklist

### Global
- [ ] Every interactive element receives focus via Tab
- [ ] Focus order matches visual reading order (left-to-right, top-to-bottom)
- [ ] Focus indicator is visible on every focused element (min 3:1 contrast)
- [ ] No keyboard traps (can always Tab away or Escape out)
- [ ] Skip-to-content link present and functional
- [ ] No content requires hover-only interaction

### Course Navigation
- [ ] Module tabs navigable with Arrow keys
- [ ] Previous/Next buttons reachable and activatable
- [ ] Progress bar communicates current position (accessible name)
- [ ] Sidebar/table of contents navigable by keyboard

### Branching Scenarios
- [ ] Choice buttons reachable via Tab
- [ ] Enter activates selected choice
- [ ] Arrow keys navigate between choices
- [ ] Focus moves to new scene content after transition
- [ ] Feedback is announced (focus moves to it or it's in an aria-live region)

### Knowledge Checks
- [ ] Radio buttons navigable with Arrow keys within radiogroup
- [ ] Submit button reachable via Tab
- [ ] Enter submits the answer
- [ ] Focus moves to feedback after submission
- [ ] "Try Again" or "Continue" button reachable after feedback

### Drag-and-Drop
- [ ] Items reachable via Tab
- [ ] Space/Enter grabs/drops an item
- [ ] Arrow keys move grabbed item up/down
- [ ] Escape cancels the grab
- [ ] Position changes announced to screen reader
- [ ] Visual feedback shown for grabbed state

### Interactive Video
- [ ] Space/K toggles play/pause
- [ ] Arrow left/right seeks backward/forward
- [ ] Arrow up/down adjusts volume
- [ ] M toggles mute
- [ ] C toggles captions
- [ ] All custom controls reachable via Tab
- [ ] In-video quiz overlay traps focus correctly

### Modals/Overlays
- [ ] Focus moves into modal when it opens
- [ ] Focus is trapped within the modal
- [ ] Escape closes the modal
- [ ] Focus returns to trigger element on close
- [ ] Background content is inert (aria-hidden or inert attribute)
```

### 4.2 Screen Reader Testing

Test with at least one screen reader on each target platform.

**Testing matrix:**

| Platform | Screen reader | Browser | Priority |
|----------|--------------|---------|----------|
| macOS | VoiceOver | Safari | High (many corporate users) |
| Windows | NVDA | Firefox or Chrome | High (most common combo) |
| Windows | JAWS | Chrome | Medium (enterprise standard) |
| iOS | VoiceOver | Safari | Medium (mobile learners) |
| Android | TalkBack | Chrome | Medium (mobile learners) |

**VoiceOver testing steps (macOS):**

```markdown
## VoiceOver Testing Protocol

### Setup
1. Open System Settings > Accessibility > VoiceOver > Enable
2. Or press Cmd+F5 to toggle VoiceOver
3. Open Safari (VoiceOver works best with Safari on macOS)
4. Navigate to the course URL

### Navigation commands
- VO key = Control+Option (or Caps Lock if configured)
- VO+Right Arrow = next element
- VO+Left Arrow = previous element
- VO+Space = activate/click
- VO+U = open rotor (headings, links, landmarks)

### Test sequence
1. **Page load**: Does VoiceOver announce the page title?
2. **Landmarks**: VO+U > Landmarks — are main, nav, region labeled?
3. **Headings**: VO+U > Headings — is heading hierarchy logical (h1 > h2 > h3)?
4. **Images**: Navigate to each image — is meaningful alt text read?
5. **Forms/quiz**: Navigate radio group — are options read with labels?
6. **Feedback**: Submit a quiz — is feedback announced automatically?
7. **Scenario**: Make a choice — is the consequence announced?
8. **Video**: Navigate to video controls — are they labeled?
9. **Progress**: Is the progress bar read with current value?
10. **Drag-and-drop**: Can you grab, move, and drop items?
```

**NVDA testing steps (Windows):**

```markdown
## NVDA Testing Protocol

### Setup
1. Download NVDA from nvaccess.org (free)
2. Launch NVDA
3. Open Chrome or Firefox
4. Navigate to the course URL

### Key commands
- NVDA key = Insert (or Caps Lock if configured)
- Tab = next focusable element
- NVDA+F7 = elements list (links, headings, landmarks)
- H = next heading
- D = next landmark
- F = next form field

### Test the same sequence as VoiceOver above, noting:
- Dynamic content: Is aria-live content announced?
- Forms mode vs. browse mode: Does NVDA switch correctly?
- Tables: Are data tables read with headers?
```

### 4.3 Zoom and Magnification Testing

Test at 200% and 400% browser zoom. Content must remain usable without horizontal scrolling at 320px effective viewport width (1280px at 400% zoom).

```markdown
## Zoom Testing Checklist

### At 200% zoom
- [ ] All text is readable without horizontal scrolling
- [ ] Navigation remains usable
- [ ] Buttons and controls are large enough to tap/click
- [ ] No content is clipped or hidden
- [ ] Modal overlays fit within the viewport
- [ ] Quiz options don't overflow their containers

### At 400% zoom (320px effective width)
- [ ] Single-column layout activates
- [ ] All content still accessible (may scroll vertically)
- [ ] No horizontal scroll required to read content
- [ ] Touch targets are at least 44x44px
- [ ] Text can be resized up to 200% without assistive tech

### Text spacing test (WCAG 1.4.12)
Apply these styles and verify no content is lost:
- Line height: 1.5x font size
- Paragraph spacing: 2x font size
- Letter spacing: 0.12x font size
- Word spacing: 0.16x font size
```

**Bookmarklet for text spacing test:**

```javascript
// Paste in browser console or create as bookmarklet
javascript:void(function(){
  var s=document.createElement('style');
  s.textContent='*{line-height:1.5!important;letter-spacing:0.12em!important;word-spacing:0.16em!important}p{margin-bottom:2em!important}';
  document.head.appendChild(s);
})();
```

### 4.4 Color Contrast Verification

```markdown
## Color Contrast Checklist

### Tools
- Chrome DevTools: Elements panel > Styles > click on any color swatch
- Firefox: Accessibility Inspector > Check for Issues > Contrast
- WebAIM Contrast Checker: webaim.org/resources/contrastchecker/
- axe DevTools browser extension

### Requirements (WCAG 2.1 AA)
- [ ] Normal text (under 18pt / 24px): 4.5:1 contrast ratio minimum
- [ ] Large text (18pt+ or 14pt+ bold): 3:1 contrast ratio minimum
- [ ] UI components and graphical objects: 3:1 contrast ratio minimum
- [ ] Focus indicators: 3:1 against adjacent colors
- [ ] Link text: 3:1 against surrounding non-link text (if not underlined)

### Courseware-specific checks
- [ ] Correct answer highlighting (green) has sufficient contrast
- [ ] Incorrect answer highlighting (red) has sufficient contrast
- [ ] Feedback text on colored backgrounds meets contrast
- [ ] Progress bar fill color contrasts with track
- [ ] Scenario choice buttons: hover/focus/selected states all meet contrast
- [ ] Information is NOT conveyed by color alone (use icons, text, patterns)
- [ ] Quiz "correct" and "incorrect" states distinguishable without color
```

**Recommended accessible color pairs for courseware feedback:**

```css
/* Feedback colors that meet WCAG AA on white backgrounds */
:root {
  /* Correct feedback: dark green on light green */
  --feedback-correct-bg: #d4edda;       /* background */
  --feedback-correct-text: #155724;     /* text — 7.1:1 contrast on bg */
  --feedback-correct-border: #28a745;   /* border — 3.2:1 on white */

  /* Incorrect feedback: dark red on light red */
  --feedback-incorrect-bg: #f8d7da;     /* background */
  --feedback-incorrect-text: #721c24;   /* text — 7.3:1 contrast on bg */
  --feedback-incorrect-border: #dc3545; /* border — 3.9:1 on white */

  /* Partial feedback: dark amber on light amber */
  --feedback-partial-bg: #fff3cd;       /* background */
  --feedback-partial-text: #856404;     /* text — 5.4:1 contrast on bg */
  --feedback-partial-border: #ffc107;   /* border — use with dark text */

  /* Informational: dark blue on light blue */
  --feedback-info-bg: #d1ecf1;
  --feedback-info-text: #0c5460;        /* 7.0:1 contrast on bg */
  --feedback-info-border: #17a2b8;

  /* Focus indicator */
  --focus-color: #2563eb;               /* 4.6:1 on white */
  --focus-outline-width: 3px;
}
```

### 4.5 Motion Sensitivity Testing

```markdown
## Motion Sensitivity Checklist

### Setup
- macOS: System Settings > Accessibility > Display > Reduce motion
- Windows: Settings > Ease of Access > Display > Show animations (off)
- Chrome DevTools: Rendering tab > Emulate CSS media feature > prefers-reduced-motion: reduce

### Tests
- [ ] Enable prefers-reduced-motion and reload the course
- [ ] Scroll-driven animations are replaced with static content
- [ ] Page transitions are instant (no slides, fades, or zooms)
- [ ] Content is fully visible without scrolling to trigger reveals
- [ ] Progress indicators still function (no animation needed)
- [ ] Video content still plays (motion preference applies to UI, not content)
- [ ] Parallax effects are disabled
- [ ] Auto-playing carousels or slideshows are stopped
- [ ] No flashing content (3 flashes per second maximum — WCAG 2.3.1)
```

### 4.6 Cognitive Load Assessment

```markdown
## Cognitive Load Checklist

### Content structure
- [ ] Maximum 3-5 new concepts per screen
- [ ] Clear visual hierarchy (headings, spacing, grouping)
- [ ] Progressive disclosure — complexity reveals gradually
- [ ] Instructions are concise and use simple language
- [ ] Jargon is defined in a glossary or on first use

### Navigation clarity
- [ ] Current position in course is always visible
- [ ] "Where am I?" is always answerable
- [ ] Back button always works
- [ ] No dead ends (always a next action available)

### Interaction clarity
- [ ] Purpose of every interaction is clear before starting
- [ ] Instructions are persistent (not just shown briefly)
- [ ] Error recovery is possible (try again, undo)
- [ ] Consequences of choices are explained in feedback

### Timing
- [ ] Self-paced by default (no auto-advance)
- [ ] Timed activities have pause, extend, and turn-off options
- [ ] No time pressure on learning content (only on assessments if required)

### Sensory
- [ ] Audio has visible playback controls
- [ ] Audio has text transcripts
- [ ] Video has captions
- [ ] No information conveyed solely through sound
- [ ] No information conveyed solely through color
```

---

## 5. Compliance Standards for Corporate Courseware

### 5.1 WCAG 2.1 AA (Minimum for Most Organizations)

WCAG 2.1 Level AA is the baseline standard. It covers four principles:

| Principle | Key requirements for courseware |
|-----------|-------------------------------|
| **Perceivable** | Alt text on images, captions on video, sufficient contrast, no color-only information, text resizable to 200%, content reflows at 320px width |
| **Operable** | Keyboard accessible, no time traps (or provide extensions), no seizure-inducing flashes, navigable with headings/landmarks, pointer cancellation |
| **Understandable** | Language declared, consistent navigation, input error identification, labels on forms |
| **Robust** | Valid HTML, ARIA used correctly, status messages programmatically determinable |

**WCAG 2.1 success criteria most relevant to courseware:**

| Criterion | ID | Courseware implication |
|-----------|-----|----------------------|
| Non-text content | 1.1.1 | All course images need alt text; decorative images need alt="" |
| Captions | 1.2.2 | All video narration and dialogue must have captions |
| Audio description | 1.2.5 | Video with visual-only information needs audio description |
| Info and relationships | 1.3.1 | Heading hierarchy, form labels, table headers |
| Meaningful sequence | 1.3.2 | DOM order matches visual order |
| Sensory characteristics | 1.3.3 | Don't say "click the green button" or "the answer on the right" |
| Use of color | 1.4.1 | Correct/incorrect must not rely solely on red/green |
| Contrast | 1.4.3 | 4.5:1 for normal text, 3:1 for large text |
| Resize text | 1.4.4 | Content usable at 200% zoom |
| Reflow | 1.4.10 | No horizontal scroll at 320px width |
| Text spacing | 1.4.12 | Content survives increased text spacing |
| Keyboard | 2.1.1 | All functionality available from keyboard |
| No keyboard trap | 2.1.2 | Focus can always move away |
| Timing adjustable | 2.2.1 | Timed quizzes must allow extend/pause/disable |
| Pause, stop, hide | 2.2.2 | Auto-playing content can be paused |
| Three flashes | 2.3.1 | No content flashes more than 3 times per second |
| Bypass blocks | 2.4.1 | Skip-to-content link |
| Page titled | 2.4.2 | Each module/page has a descriptive title |
| Focus order | 2.4.3 | Tab order is logical |
| Focus visible | 2.4.7 | Focus indicator always visible |
| Pointer cancellation | 2.5.2 | Actions complete on up-event, not down-event |
| Label in name | 2.5.3 | Accessible name includes visible text |
| Motion actuation | 2.5.4 | Shake/tilt interactions have button alternatives |
| Language of page | 3.1.1 | html lang attribute set |
| On focus | 3.2.1 | No context change on focus alone |
| Consistent navigation | 3.2.3 | Navigation consistent across pages |
| Error identification | 3.3.1 | Errors described in text (not just color) |
| Labels or instructions | 3.3.2 | Form fields have labels |
| Status messages | 4.1.3 | Dynamic messages use aria-live or role="alert" |

### 5.2 Section 508 (US Federal Requirement)

Section 508 of the Rehabilitation Act requires all electronic and information technology developed, procured, maintained, or used by the federal government to be accessible. Since 2018, Section 508 incorporates WCAG 2.0 Level AA by reference.

**When Section 508 applies:**
- Courseware developed for or purchased by US federal agencies
- Courseware funded by federal grants
- Organizations contracting with the federal government
- Many state and local governments adopt Section 508 by reference

**Practical implication:** If your courseware meets WCAG 2.1 AA, it meets Section 508. The reverse is not necessarily true (WCAG 2.1 has additional criteria beyond 2.0).

### 5.3 EN 301 549 (European Standard)

EN 301 549 is the European harmonized standard for ICT accessibility. It references WCAG 2.1 Level AA for web content and adds requirements for:
- Non-web documents (PDFs, downloadable job aids)
- Non-web software (desktop LMS clients)
- Hardware (if applicable)

**Additional EN 301 549 requirements beyond WCAG:**
- Clause 9: Web content must meet WCAG 2.1 AA
- Clause 10: Non-web documents must meet equivalent criteria
- Clause 11: Software must meet equivalent criteria
- Clause 12: Documentation and support services must be accessible

**When EN 301 549 applies:**
- Courseware deployed in EU member states
- Public sector organizations in the EU (Directive 2016/2102)
- Private sector digital products in the EU (European Accessibility Act, effective June 2025)

### 5.4 How to Document Compliance (VPAT/ACR)

A Voluntary Product Accessibility Template (VPAT) produces an Accessibility Conformance Report (ACR). This is the standard format for documenting accessibility compliance.

**Use the ITI VPAT 2.5 template** which covers WCAG 2.1, Section 508, and EN 301 549 in a single document.

**ACR conformance levels:**

| Level | Meaning |
|-------|---------|
| **Supports** | Fully meets the criterion |
| **Partially Supports** | Some functionality meets the criterion |
| **Does Not Support** | Does not meet the criterion |
| **Not Applicable** | Criterion is not relevant to the product |

**Template structure for courseware ACR:**

```markdown
# Accessibility Conformance Report
## [Course Name] — VPAT 2.5

### Product Information
- **Product name**: Security Awareness 101
- **Version**: 2.1
- **Date**: 2026-03-16
- **Evaluation methods**: Automated testing (axe-core, Lighthouse), manual testing
  (keyboard, VoiceOver, NVDA), user testing with assistive technology users

### WCAG 2.1 Level A & AA Conformance

| Criteria | Conformance Level | Remarks |
|----------|-------------------|---------|
| 1.1.1 Non-text Content | Supports | All images have alt text. Decorative images use alt="" and role="presentation" |
| 1.2.1 Audio-only/Video-only | Supports | All audio has transcripts; video-only has text descriptions |
| 1.2.2 Captions | Supports | All videos include synchronized captions in WebVTT format |
| 1.2.3 Audio Description | Partially Supports | Available for 80% of video content. Remaining 20% in production. |
| ... | ... | ... |

### Testing Environment
- **Automated tools**: axe-core 4.x, Lighthouse 12.x, pa11y 7.x
- **Screen readers**: VoiceOver 15 (macOS), NVDA 2025.1 (Windows)
- **Browsers**: Safari 19, Chrome 130, Firefox 135
- **Mobile**: iOS 19 Safari, Android 16 Chrome

### Known Issues and Remediation Plan
| Issue | Severity | Target Fix Date |
|-------|----------|-----------------|
| Drag-and-drop keyboard announce missing in Module 3 | Moderate | 2026-04-01 |
| Video captions missing for supplemental content clips | High | 2026-03-30 |
```

**Maintaining compliance:**

1. Run automated accessibility tests in CI on every pull request (see Section 1.6)
2. Include accessibility testing in the QA agent's review criteria
3. Update the ACR with each major release
4. Conduct annual manual accessibility audit with assistive technology users
5. Track accessibility issues in the same system as other bugs (with accessibility labels)
6. Train content authors on accessible content creation (alt text, heading structure, plain language)

---

## Quick Reference: Accessibility Testing Commands

```bash
# Run all accessibility linting (development time)
npm run lint

# Run component-level accessibility tests
npm run test:a11y

# Run full-page accessibility audits with Playwright
npm run test:e2e:a11y

# Run pa11y standards check
npm run pa11y

# Run Lighthouse accessibility audit
npm run lhci

# Run everything
npm run a11y:full

# Quick single-page check
npx pa11y --standard WCAG2AA --runner axe http://localhost:5173/module/01-introduction
```
