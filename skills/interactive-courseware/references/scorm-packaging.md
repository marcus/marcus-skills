# SCORM, xAPI, cmi5 Packaging Reference

Complete implementation guide for packaging interactive courses for LMS delivery.

## SCORM 1.2

### Package Structure

```
course.zip
├── imsmanifest.xml
├── adlcp_rootv1p2.xsd
├── imscp_rootv1p1p2.xsd
├── imsmd_rootv1p2p1.xsd
├── index.html
├── assets/
│   ├── index-[hash].js
│   ├── index-[hash].css
│   └── media/
└── data/
    └── course-data.json
```

### Runtime API

The LMS provides a JavaScript object named `API` in a parent frame. Your course finds and communicates with it.

```typescript
// SCORM 1.2 Adapter
export class Scorm12Adapter {
  private api: any;

  initialize(): void {
    this.api = this.findAPI();
    if (!this.api) {
      console.warn('SCORM 1.2 API not found — running in standalone mode');
      return;
    }
    this.api.LMSInitialize('');
  }

  saveProgress(location: string, data: Record<string, unknown>): void {
    if (!this.api) return;
    // lesson_location: bookmark (max 255 chars)
    this.api.LMSSetValue('cmi.core.lesson_location', location);
    // suspend_data: state (max 4,096 bytes in SCORM 1.2)
    const compressed = compressState(data);
    this.api.LMSSetValue('cmi.suspend_data', compressed);
    this.api.LMSSetValue('cmi.core.exit', 'suspend');
    this.api.LMSCommit('');
  }

  getProgress(): { location: string; data: Record<string, unknown> } {
    if (!this.api) return { location: '', data: {} };
    const location = this.api.LMSGetValue('cmi.core.lesson_location');
    const raw = this.api.LMSGetValue('cmi.suspend_data');
    return { location, data: decompressState(raw) };
  }

  reportScore(score: number, max: number, passed: boolean): void {
    if (!this.api) return;
    this.api.LMSSetValue('cmi.core.score.raw', score.toString());
    this.api.LMSSetValue('cmi.core.score.max', max.toString());
    this.api.LMSSetValue('cmi.core.score.min', '0');
    this.api.LMSSetValue('cmi.core.lesson_status', passed ? 'passed' : 'failed');
    this.api.LMSCommit('');
  }

  reportCompletion(): void {
    if (!this.api) return;
    this.api.LMSSetValue('cmi.core.lesson_status', 'completed');
    this.api.LMSCommit('');
  }

  terminate(): void {
    if (!this.api) return;
    this.api.LMSFinish('');
  }

  private findAPI(): any {
    let win: Window = window;
    let attempts = 0;
    while (!(win as any).API && win.parent !== win && attempts < 10) {
      win = win.parent;
      attempts++;
    }
    if ((win as any).API) return (win as any).API;

    // Check opener window chain
    if (window.opener) {
      win = window.opener;
      attempts = 0;
      while (!(win as any).API && win.parent !== win && attempts < 10) {
        win = win.parent;
        attempts++;
      }
    }
    return (win as any).API || null;
  }
}

// SCORM 1.2 suspend_data is limited to 4,096 bytes
// Use compression to fit more state data
function compressState(data: Record<string, unknown>): string {
  const json = JSON.stringify(data);
  // Use LZString or similar for compression
  // Ensure output is within 4096 bytes
  return btoa(json); // Simple base64 for small courses
}

function decompressState(raw: string): Record<string, unknown> {
  if (!raw) return {};
  try {
    return JSON.parse(atob(raw));
  } catch {
    return {};
  }
}
```

### Key Data Elements

| Element | Purpose | Limits |
|---------|---------|--------|
| `cmi.core.lesson_location` | Bookmark position | 255 chars |
| `cmi.core.lesson_status` | passed/completed/failed/incomplete/browsed/not attempted | — |
| `cmi.core.score.raw` | Numeric score | 0-100 |
| `cmi.suspend_data` | Free-form state persistence | **4,096 bytes** |
| `cmi.core.session_time` | Time in current session | HH:MM:SS format |
| `cmi.core.total_time` | Accumulated time | HH:MM:SS format |
| `cmi.interactions.n.*` | Individual question tracking | — |

### Manifest Generator

```typescript
// scripts/generate-manifest.ts
import { readFileSync, writeFileSync } from 'fs';
import { glob } from 'glob';
import { relative } from 'path';

interface ManifestOptions {
  identifier: string;
  title: string;
  scormVersion: '1.2' | '2004';
  distDir: string;
  entryPoint: string;
}

function generateManifest(options: ManifestOptions): string {
  const files = glob.sync('**/*', { cwd: options.distDir, nodir: true });

  const fileEntries = files
    .map(f => `      <file href="${f}"/>`)
    .join('\n');

  if (options.scormVersion === '1.2') {
    return `<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="${options.identifier}" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd
    http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd
    http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="org-1">
    <organization identifier="org-1">
      <title>${escapeXml(options.title)}</title>
      <item identifier="item-1" identifierref="res-1">
        <title>${escapeXml(options.title)}</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="res-1" type="webcontent"
      adlcp:scormtype="sco" href="${options.entryPoint}">
${fileEntries}
    </resource>
  </resources>
</manifest>`;
  }

  // SCORM 2004 4th Edition
  return `<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="${options.identifier}" version="1.0"
  xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3"
  xmlns:adlseq="http://www.adlnet.org/xsd/adlseq_v1p3"
  xmlns:adlnav="http://www.adlnet.org/xsd/adlnav_v1p3"
  xmlns:imsss="http://www.imsglobal.org/xsd/imsss">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>2004 4th Edition</schemaversion>
  </metadata>
  <organizations default="org-1">
    <organization identifier="org-1">
      <title>${escapeXml(options.title)}</title>
      <item identifier="item-1" identifierref="res-1">
        <title>${escapeXml(options.title)}</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="res-1" type="webcontent"
      adlcp:scormType="sco" href="${options.entryPoint}">
${fileEntries}
    </resource>
  </resources>
</manifest>`;
}

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
```

---

## SCORM 2004

### Additions Over SCORM 1.2

- **Sequencing & Navigation**: Rules in manifest control activity delivery order
- **Separated status**: `cmi.completion_status` + `cmi.success_status` (vs combined `lesson_status`)
- **Progress measure**: `cmi.progress_measure` (0.0 - 1.0)
- **Scaled score**: `cmi.scaled_score` (-1.0 to 1.0)
- **Larger suspend_data**: **64,000 characters** (vs 4,096 bytes in SCORM 1.2)
- **Navigation requests**: SCO can request continue, previous, exit

### Runtime API

API object is named `API_1484_11` (different from SCORM 1.2's `API`).

```typescript
export class Scorm2004Adapter {
  private api: any;

  initialize(): void {
    this.api = this.findAPI('API_1484_11');
    if (!this.api) return;
    this.api.Initialize('');
  }

  saveProgress(location: string, data: Record<string, unknown>): void {
    if (!this.api) return;
    this.api.SetValue('cmi.location', location);
    // 64,000 chars available in SCORM 2004
    this.api.SetValue('cmi.suspend_data', JSON.stringify(data));
    this.api.SetValue('cmi.exit', 'suspend');
    this.api.Commit('');
  }

  reportScore(score: number, max: number, passed: boolean): void {
    if (!this.api) return;
    this.api.SetValue('cmi.score.raw', score.toString());
    this.api.SetValue('cmi.score.max', max.toString());
    this.api.SetValue('cmi.score.min', '0');
    this.api.SetValue('cmi.score.scaled', (score / max).toString());
    this.api.SetValue('cmi.success_status', passed ? 'passed' : 'failed');
    this.api.Commit('');
  }

  reportCompletion(): void {
    if (!this.api) return;
    this.api.SetValue('cmi.completion_status', 'completed');
    this.api.SetValue('cmi.progress_measure', '1.0');
    this.api.Commit('');
  }

  terminate(): void {
    if (!this.api) return;
    this.api.Terminate('');
  }

  private findAPI(name: string): any {
    let win: Window = window;
    let attempts = 0;
    while (!(win as any)[name] && win.parent !== win && attempts < 10) {
      win = win.parent; attempts++;
    }
    return (win as any)[name] || null;
  }
}
```

---

## xAPI (Tin Can API)

### Statement Structure

```typescript
// xapi.ts
interface XAPIStatement {
  actor: { objectType: 'Agent'; name: string; mbox: string };
  verb: { id: string; display: { 'en-US': string } };
  object: {
    objectType: 'Activity';
    id: string;
    definition: { name: { 'en-US': string }; type: string };
  };
  result?: {
    score?: { scaled: number; raw: number; min: number; max: number };
    success?: boolean;
    completion?: boolean;
    duration?: string;
  };
  timestamp: string;
}

export class XAPIAdapter {
  private endpoint: string;
  private auth: string;

  constructor() {
    this.endpoint = window.xAPIConfig?.endpoint || '';
    this.auth = window.xAPIConfig?.auth || '';
  }

  async sendStatement(statement: XAPIStatement): Promise<void> {
    await fetch(`${this.endpoint}/statements`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.auth,
        'X-Experience-API-Version': '1.0.3',
      },
      body: JSON.stringify(statement),
    });
  }

  reportCompletion(): void {
    this.sendStatement({
      actor: this.getActor(),
      verb: { id: 'http://adlnet.gov/expapi/verbs/completed', display: { 'en-US': 'completed' } },
      object: this.getCourseObject(),
      result: { completion: true },
      timestamp: new Date().toISOString(),
    });
  }

  reportScore(score: number, max: number, passed: boolean): void {
    this.sendStatement({
      actor: this.getActor(),
      verb: {
        id: passed ? 'http://adlnet.gov/expapi/verbs/passed' : 'http://adlnet.gov/expapi/verbs/failed',
        display: { 'en-US': passed ? 'passed' : 'failed' },
      },
      object: this.getCourseObject(),
      result: {
        score: { scaled: score / max, raw: score, min: 0, max },
        success: passed,
        completion: true,
      },
      timestamp: new Date().toISOString(),
    });
  }

  private getActor() {
    return {
      objectType: 'Agent' as const,
      name: window.xAPIConfig?.actorName || 'Unknown',
      mbox: window.xAPIConfig?.actorMbox || 'mailto:unknown@example.com',
    };
  }

  private getCourseObject() {
    return {
      objectType: 'Activity' as const,
      id: window.xAPIConfig?.activityId || window.location.href,
      definition: {
        name: { 'en-US': document.title },
        type: 'http://adlnet.gov/expapi/activities/course',
      },
    };
  }
}
```

### Learning Record Store (LRS) Options

| LRS | Type | Notes |
|-----|------|-------|
| **Learning Locker** | Open source | Most popular OS LRS, MongoDB-based |
| **SQL LRS** | Open source | Lightweight, SQL-backed |
| **SCORM Cloud** | Commercial | Built-in LRS, testing sandbox |
| **Watershed (Rustici)** | Commercial | Enterprise analytics + LRS |

---

## cmi5

cmi5 = xAPI + LMS launch mechanism + standardized vocabulary. The best of both worlds.

### Package Structure

```
course.zip
├── cmi5.xml              # Course structure (like imsmanifest.xml)
├── index.html
├── assets/
└── media/
```

### cmi5.xml Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<courseStructure xmlns="https://w3id.org/xapi/profiles/cmi5/v1/CourseStructure.xsd">
  <course id="https://example.com/courses/security-101">
    <title><langstring lang="en-US">Security Awareness 101</langstring></title>
    <description><langstring lang="en-US">Learn to identify and respond to security threats</langstring></description>
  </course>
  <au id="https://example.com/courses/security-101/au/1"
    url="index.html" moveOn="CompletedOrPassed" launchMethod="AnyWindow">
    <title><langstring lang="en-US">Security Awareness 101</langstring></title>
  </au>
</courseStructure>
```

### Launch Flow

1. LMS generates launch URL with auth token and endpoint
2. Course opens in browser, retrieves session config from LMS
3. Course sends `initialized` xAPI statement
4. Course tracks activity via xAPI statements
5. Course sends `completed` / `passed` / `failed` statements
6. Course sends `terminated` statement

---

## LMS-Specific Notes

### WorkRamp
- Uses Rustici Software (SCORM Cloud) engine under the hood
- Supports SCORM 1.2, SCORM 2004 (2nd-4th ed), xAPI, AICC, cmi5
- **Recommended**: SCORM 2004 4th Edition
- Upload limit: 1 GB per package
- Drag SCORM tile into Guide editing pane to add content

### Docebo
- Supports SCORM 1.2, SCORM 2004, xAPI
- Headless LMS option available (API-first delivery)
- REST API for programmatic content management

### Cornerstone OnDemand
- Supports SCORM 1.2, SCORM 2004 (3rd Ed), AICC
- Content player renders SCORM within platform UI

### SAP SuccessFactors
- Supports SCORM 1.2, SCORM 2004, AICC
- iContent repository for learning object management

---

## Tracking Comparison

| Feature | SCORM 1.2 | SCORM 2004 | xAPI | cmi5 |
|---------|-----------|------------|------|------|
| Completion | `lesson_status` | `completion_status` | `completed` verb | `completed` verb |
| Pass/Fail | `lesson_status` | `success_status` | `passed`/`failed` | `passed`/`failed` |
| Score | `score.raw` (0-100) | `score.scaled` (-1 to 1) | `result.score` | `result.score` |
| Bookmark | 255 chars | 1000 chars | Activity State (unlimited) | Activity State |
| State data | **4,096 bytes** | **64,000 chars** | **Unlimited** | **Unlimited** |
| Time | HH:MM:SS | ISO 8601 | ISO 8601 duration | ISO 8601 duration |
| Runs in | LMS iframe | LMS iframe | Anywhere | Own window |

---

## Testing

### SCORM Cloud Testing

Upload your package to [SCORM Cloud](https://cloud.scorm.com/) (free tier available) for:
- Manifest validation
- Runtime communication testing
- Completion/score reporting verification
- Cross-browser testing

### scorm-again for Local Testing

```typescript
import { Scorm12API } from 'scorm-again';

// Create local SCORM API for development/testing
const api = new Scorm12API({
  logLevel: 4, // Verbose logging
  selfReportSessionTime: true,
});

// Mount it where course expects to find it
(window as any).API = api;

// Listen for events
api.on('LMSSetValue.cmi.core.lesson_status', (value: string) => {
  console.log('Course reported status:', value);
});
```

### Validation Checklist

- [ ] `imsmanifest.xml` is at ZIP root (not in a subfolder)
- [ ] All files referenced in manifest exist in package
- [ ] SCORM API found and initialized successfully
- [ ] Bookmark saves and restores on re-launch
- [ ] Score reports correctly
- [ ] Completion status reports correctly
- [ ] Course works in LMS iframe (no cross-origin errors)
- [ ] Course handles missing SCORM API gracefully (standalone fallback)
