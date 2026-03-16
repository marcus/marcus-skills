# SCORM Deployment Troubleshooting Guide

A practical reference for diagnosing and fixing real-world SCORM issues. This guide assumes familiarity with the SCORM packaging and runtime concepts covered in `scorm-packaging.md`.

---

## 1. Common LMS Quirks and Workarounds

### WorkRamp (Rustici Engine)

WorkRamp uses Rustici Software's SCORM Engine under the hood. This is generally one of the more standards-compliant players, but it introduces its own constraints.

**iframe sandboxing**: WorkRamp loads SCORM content inside a sandboxed iframe. The `sandbox` attribute may restrict `allow-scripts`, `allow-same-origin`, or `allow-popups`. If your course opens new windows or uses `window.parent` traversal, it will fail silently.

```
Symptom:  API object is null despite correct findAPI code
Fix:      Ensure the LMS grants allow-scripts and allow-same-origin on the iframe
Fallback: Use postMessage-based communication (see CrossFrameAPI in section 2)
```

**Cross-origin restrictions**: Because Rustici serves content from a different origin than the LMS host page, `window.parent.API` access throws a `DOMException: Blocked a frame with origin`. The standard findAPI traversal will hit this before it finds the API.

```javascript
// Defensive findAPI that catches cross-origin errors
function findAPI(win) {
  let attempts = 0;
  while (attempts < 10) {
    try {
      if (win.API) return win.API;
      if (win.parent === win) break;
      win = win.parent;
    } catch (e) {
      // Cross-origin frame — cannot traverse further
      console.warn('Cross-origin frame boundary hit at depth', attempts);
      break;
    }
    attempts++;
  }
  return null;
}
```

**Popup blockers**: If the LMS launches content in a new window (rather than iframe), browser popup blockers will silently prevent it. The user sees nothing. WorkRamp typically uses iframe mode, but if configured for new-window launch, advise users to allowlist the LMS domain.

### Moodle

Moodle's built-in SCORM player has the most documented quirks of any open-source LMS.

**SCORM player display modes**: Moodle offers multiple display options — embedded in page, new window, or iframe. Each behaves differently.

| Mode | API Discovery | Gotchas |
|------|--------------|---------|
| Embedded | `window.parent` traversal | Content height issues; Moodle nav interferes with course UI |
| New window | `window.opener` traversal | Popup blockers; back button terminates session |
| Current window | `window.parent` traversal | Replaces Moodle UI; no way back without browser history |

**Completion reporting not persisting**: Moodle caches SCORM data in the browser and batches writes to the database. If the learner closes the browser before Moodle flushes, data is lost. The setting `Auto-commit on navigation` (called `autocommit` internally) helps but introduces its own timing issues.

```
Symptom:  Learner completes course, but Moodle shows "incomplete"
Causes:
  1. autocommit disabled and learner closed tab before LMSCommit
  2. LMSFinish called before LMSCommit (data never persisted)
  3. Moodle "Force completed" setting overrides SCO-reported status
Fix:      Always call LMSCommit('') BEFORE LMSFinish('')
          Enable "Auto-commit" in Moodle SCORM activity settings
          Check Moodle's "Attempts grading" setting for multi-attempt courses
```

**SCORM 2004 cmi.exit quirk**: Moodle's SCORM player may not honor `cmi.exit = "suspend"` correctly in all cases. If the learner's attempt is not properly suspended, the next launch creates a new attempt instead of resuming. Always set `cmi.exit` before calling `Commit`, then `Terminate`.

**Mobile browser issues**: Moodle Mobile does not support SCORM content natively in all configurations. SCORM packages with heavy JavaScript may hit memory limits on mobile WebView. Moodle's mobile app opens SCORM in an embedded WebView with limited `window.parent` access.

### Cornerstone OnDemand

**SCORM 2004 sequencing limitations**: Cornerstone supports SCORM 2004 3rd Edition but has incomplete support for complex sequencing rules. Specifically:

- Randomization and selection count rules may be ignored
- Rollup rules with complex conditions may not evaluate correctly
- `adlseq:objectives` global objective mapping can fail silently

```
Workaround: Keep sequencing simple — linear progression with basic prerequisites.
            Avoid randomized SCO delivery.
            Test every sequencing rule on the actual Cornerstone instance.
```

**Content player rendering**: Cornerstone wraps SCORM content in its own player chrome, which consumes viewport space. Design for a viewport at least 100px smaller in both dimensions than the authored size.

**Session timeout**: Cornerstone has an aggressive session timeout (often 20-30 minutes of inactivity). If a learner pauses mid-course, the LMS session expires and subsequent `LMSCommit` calls fail silently. The SCORM API object still exists but stops accepting data.

```javascript
// Detect stale sessions by checking commit results
const result = api.LMSCommit('');
if (result === 'false' || result === false) {
  const error = api.LMSGetLastError();
  console.error('Commit failed, error code:', error);
  // Error 391 = general commit failure (likely session expired)
  // Show user a "session expired, please relaunch" message
}
```

### SAP SuccessFactors

**iContent repository issues**: SuccessFactors uses an iContent repository for SCORM packages. Upload processing is asynchronous — a package may show as "available" before processing is complete, leading to broken launches.

```
Symptom:  Course uploaded successfully but launches to blank page
Fix:      Wait for iContent processing to complete (check status in admin panel)
          Packages over 100MB may take several minutes to process
```

**SCORM type attribute case sensitivity**: SuccessFactors is strict about the `adlcp:scormType` attribute in the manifest. SCORM 1.2 uses lowercase `scormtype`, while SCORM 2004 uses camelCase `scormType`. Mixing these up causes the content to launch as an Asset (no API communication) rather than a SCO.

```xml
<!-- SCORM 1.2 — lowercase -->
<resource identifier="res-1" type="webcontent"
  adlcp:scormtype="sco" href="index.html">

<!-- SCORM 2004 — camelCase -->
<resource identifier="res-1" type="webcontent"
  adlcp:scormType="sco" href="index.html">
```

**Popup restrictions**: SuccessFactors aggressively blocks popups from SCORM content. Any `window.open()` call from within the content iframe will be blocked. Use in-page modals instead of popup windows.

### General Cross-LMS Issues

**iframe vs. new window launch modes**: Different LMS platforms have different defaults, and some let admins configure this per course.

```
iframe launch:
  + No popup blocker issues
  + Content appears embedded in LMS UI
  - Cross-origin restrictions on API discovery
  - Viewport constrained by LMS chrome
  - window.parent traversal may be blocked

New window launch:
  + Full viewport available
  + No cross-origin issues (API in opener)
  - Popup blockers may prevent launch entirely
  - Browser back button can terminate session prematurely
  - Mobile browsers often block new windows
```

**Mobile browser issues**: These affect all LMS platforms.

- iOS Safari restricts `window.opener` access after the user navigates away and returns
- Android Chrome WebView has limited `postMessage` support in some versions
- All mobile browsers aggressively reclaim memory, killing SCORM sessions in background tabs
- Touch events may not fire correctly if the SCORM content uses mouse-only event handlers
- `beforeunload` and `unload` events (commonly used to call `LMSFinish`) are unreliable on mobile

```javascript
// Mobile-safe termination: use visibilitychange instead of unload
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    // Commit data immediately — page may be killed
    api.LMSCommit('');
    // Note: Do NOT call LMSFinish here — the user may return
  }
});

// Also set up pagehide as a backup (more reliable than unload on mobile)
window.addEventListener('pagehide', () => {
  api.LMSSetValue('cmi.core.exit', 'suspend');
  api.LMSCommit('');
  api.LMSFinish('');
});
```

---

## 2. SCORM API Communication Failures

### API Not Found (findAPI Traversal Failures)

The most common SCORM runtime error. The course loads but cannot communicate with the LMS.

**Root causes and solutions:**

| Cause | Diagnosis | Fix |
|-------|-----------|-----|
| Cross-origin iframe | DevTools console shows `DOMException: Blocked a frame` | Use `postMessage` bridge or scorm-again's `CrossFrameAPI` |
| Incorrect API name | SCORM 1.2 looks for `API`, 2004 looks for `API_1484_11` | Check your SCORM version and API name |
| Too-deep nesting | Content is nested more than 7 frames deep (SCORM 1.2 limit) | Reduce iframe nesting or increase traversal limit |
| Opener window closed | New-window launch, user closed original LMS window | Detect and warn the user |
| LMS loads content before API is ready | Race condition on slow LMS pages | Add retry logic with exponential backoff |
| Sandboxed iframe missing `allow-same-origin` | `window.parent` access throws error | Request LMS admin to adjust sandbox attributes |

**Robust API discovery with retry:**

```javascript
function findAPIWithRetry(apiName, maxRetries = 5, delay = 500) {
  return new Promise((resolve) => {
    let attempts = 0;

    function tryFind() {
      const api = scanForAPI(window, apiName)
                || scanOpener(window, apiName);
      if (api) {
        resolve(api);
        return;
      }
      attempts++;
      if (attempts < maxRetries) {
        setTimeout(tryFind, delay * Math.pow(2, attempts - 1));
      } else {
        console.warn(`${apiName} not found after ${maxRetries} attempts`);
        resolve(null); // Fall back to standalone mode
      }
    }

    tryFind();
  });
}

function scanForAPI(win, apiName) {
  let current = win;
  let depth = 0;
  while (depth < 10) {
    try {
      if (current[apiName]) return current[apiName];
      if (current.parent === current) break;
      current = current.parent;
    } catch (e) {
      break; // Cross-origin boundary
    }
    depth++;
  }
  return null;
}

function scanOpener(win, apiName) {
  try {
    if (!win.opener) return null;
    return scanForAPI(win.opener, apiName);
  } catch (e) {
    return null; // Cross-origin opener
  }
}
```

### Cross-Origin iframe Solutions with scorm-again CrossFrameAPI

When the LMS serves content from a different origin (common with Rustici-based LMS platforms), the standard `window.parent.API` lookup fails. The `scorm-again` library provides `CrossFrameAPI` and `CrossFrameLMS` to bridge this gap using `postMessage`.

**Parent frame (LMS side) — CrossFrameLMS:**

```javascript
import CrossFrameLMS from 'scorm-again/cross-frame-lms';
import { Scorm12API } from 'scorm-again/scorm12';

const api = new Scorm12API({
  autocommit: true,
  logLevel: 1,
});

// Second argument restricts message origin for security
const bridge = new CrossFrameLMS(api, 'https://content.example.com');
```

**Child frame (SCORM content side) — CrossFrameAPI:**

```javascript
import CrossFrameAPI from 'scorm-again/cross-frame-api';

// Create a proxy API that forwards calls via postMessage
window.API = new CrossFrameAPI('https://lms.example.com');

// Now use the API normally — calls are proxied transparently
window.API.LMSInitialize('');
window.API.LMSSetValue('cmi.core.lesson_status', 'completed');
window.API.LMSCommit('');
window.API.LMSFinish('');
```

**How it works**: `CrossFrameAPI` uses a JavaScript `Proxy` to intercept SCORM API calls and forward them via `window.postMessage` to the parent frame. `CrossFrameLMS` listens for these messages and invokes the real SCORM API methods. Responses are sent back with matching `messageId` fields. Most `GetValue` calls return cached values synchronously for performance, with async `postMessage` updates happening behind the scenes.

**Security**: Always specify the exact origin in both constructors. Using `"*"` as the origin allows any page to send SCORM commands to your API.

### LMSInitialize Failures

```
Error 102: General Initialization Failure
Error 103: Already Initialized
Error 104: Content Instance Terminated
```

**Common causes:**

1. **Called `Initialize` twice** — Some courses call it in both `DOMContentLoaded` and `window.onload`. The second call returns error 103. This is usually harmless but should be avoided.

2. **Called after `Terminate`** — If your course calls `LMSFinish`/`Terminate` (e.g., in an `unload` handler) and then the user navigates back, the re-initialization fails with error 104. There is no recovery; the session is dead.

3. **LMS session expired before content loaded** — The LMS created the API object but the server-side session timed out before `Initialize` was called. Error 102.

```javascript
// Safe initialization pattern
function safeInitialize(api) {
  const result = api.LMSInitialize('');
  if (result === 'false' || result === false) {
    const errorCode = api.LMSGetLastError();
    const diagnostic = api.LMSGetDiagnostic(errorCode);
    console.error(`LMSInitialize failed: code=${errorCode}, detail=${diagnostic}`);

    if (errorCode === '103') {
      // Already initialized — not fatal, continue
      return true;
    }
    // Any other error — run in standalone mode
    return false;
  }
  return true;
}
```

### LMSCommit Failures (Network Issues, Session Timeouts)

`LMSCommit` is where most real-world failures occur, because it's the call that actually persists data to the server.

**Common failure patterns:**

1. **Network interruption**: The learner's connection drops between `SetValue` and `Commit`. Data is in the local API object but never reaches the server. Error 391.

2. **Session timeout**: The LMS server session expired. The API object is still in memory, `SetValue` appears to succeed (it's local), but `Commit` fails because the server rejects the request.

3. **Race condition with `Terminate`**: Calling `LMSFinish` immediately after `LMSCommit` without waiting for the commit to complete. Some LMS implementations process `Commit` asynchronously.

```javascript
// Resilient commit with retry
function commitWithRetry(api, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const result = api.LMSCommit('');
    if (result === 'true' || result === true) return true;

    const error = api.LMSGetLastError();
    console.warn(`Commit attempt ${i + 1} failed, error: ${error}`);

    if (error === '143') {
      // Commit after termination — unrecoverable
      return false;
    }
    // Brief pause before retry (only helps with transient network issues)
  }
  return false;
}
```

4. **Commit before Initialize**: Error 142. Always check that `Initialize` succeeded before committing.

### suspend_data Corruption or Truncation

`suspend_data` is the primary mechanism for persisting course state between sessions. It's a single string field with hard size limits.

**SCORM 1.2**: 4,096 bytes (not characters — multi-byte UTF-8 characters consume more)
**SCORM 2004**: 64,000 characters

**Common problems:**

1. **Silent truncation**: Some LMS platforms truncate `suspend_data` without raising an error. Your `SetValue` succeeds, your `Commit` succeeds, but the next `GetValue` returns truncated data that fails to parse.

```javascript
// Always verify suspend_data round-trips correctly
function saveSuspendData(api, data) {
  const serialized = JSON.stringify(data);
  const encoded = btoa(serialized); // Base64 adds ~33% overhead

  // Check size before saving
  const byteLength = new Blob([encoded]).size;
  if (byteLength > 4096) {
    console.error(`suspend_data exceeds 4096 bytes (${byteLength}). Data WILL be truncated.`);
    // Fall back to saving only essential state
  }

  api.LMSSetValue('cmi.suspend_data', encoded);
  api.LMSCommit('');

  // Verify the data survived
  const readBack = api.LMSGetValue('cmi.suspend_data');
  if (readBack !== encoded) {
    console.error('suspend_data was truncated or corrupted on save');
  }
}
```

2. **Character encoding issues**: Base64 is safe (ASCII only), but if you store raw JSON with Unicode characters, some LMS platforms mangle non-ASCII characters. Always encode to ASCII-safe format.

3. **LZString compression**: Use `lz-string` library's `compressToEncodedURIComponent` (not `compress` — that produces Unicode) to fit more data into 4,096 bytes.

```javascript
import LZString from 'lz-string';

// Compress: ~60-70% size reduction for typical JSON
const compressed = LZString.compressToEncodedURIComponent(JSON.stringify(data));

// Decompress
const data = JSON.parse(LZString.decompressFromEncodedURIComponent(compressed));
```

4. **Null/undefined on first launch**: `GetValue('cmi.suspend_data')` returns `''` (empty string) on first launch, not `null` or `undefined`. Always handle the empty-string case.

---

## 3. Manifest Validation Issues

### Missing Schema Files

SCORM 1.2 packages should include the XSD/DTD schema files referenced in the manifest. While many LMS platforms don't validate against these schemas, some strict validators (including SCORM Cloud) will flag their absence.

**Required schema files for SCORM 1.2:**
```
adlcp_rootv1p2.xsd
imscp_rootv1p1p2.xsd
imsmd_rootv1p2p1.xsd
ims_xml.xsd
```

**Required schema files for SCORM 2004 4th Edition:**
```
adlcp_v1p3.xsd
adlseq_v1p3.xsd
adlnav_v1p3.xsd
imscp_v1p1.xsd
imsss_v1p0.xsd
imsmd_rootv1p2p1.xsd
common/*  (schema subfolder)
```

```
Symptom:  SCORM Cloud import warning: "Referenced schema file not found"
Fix:      Include all XSD files at the ZIP root alongside imsmanifest.xml
Source:   Download schema files from adlnet.gov or copy from SCORM sample packages
```

### Incorrect Resource References

Every file in the package should be referenced in the manifest's `<resource>` block. Files that exist in the ZIP but are not in the manifest may be stripped by some LMS import processes.

**Common mistakes:**

```xml
<!-- WRONG: path uses backslashes (Windows artifact) -->
<file href="assets\images\logo.png"/>

<!-- CORRECT: always use forward slashes -->
<file href="assets/images/logo.png"/>

<!-- WRONG: absolute path -->
<file href="/assets/images/logo.png"/>

<!-- CORRECT: relative path from manifest root -->
<file href="assets/images/logo.png"/>

<!-- WRONG: URL-encoded spaces when the file doesn't use them -->
<file href="assets/my%20image.png"/>
<!-- when the actual filename is "my image.png", some LMS decode this, others don't -->

<!-- BEST PRACTICE: never use spaces in filenames -->
<file href="assets/my-image.png"/>
```

### Encoding Issues in XML

The manifest must be valid UTF-8 XML. Common encoding failures:

1. **BOM (Byte Order Mark)**: Some editors add a UTF-8 BOM (`EF BB BF`) to the start of the file. Most XML parsers handle this, but some LMS implementations choke on it.

2. **Unescaped special characters in titles**: `&`, `<`, `>` in course titles break XML parsing.

```xml
<!-- BROKEN: unescaped ampersand -->
<title>Sales & Marketing 101</title>

<!-- FIXED: escaped entity -->
<title>Sales &amp; Marketing 101</title>
```

3. **Non-UTF-8 encoding**: If the XML declaration says `encoding="UTF-8"` but the file is actually saved as ISO-8859-1 or Windows-1252, accented characters will corrupt the manifest.

```
Diagnosis: Open imsmanifest.xml in a hex editor. Look for bytes > 0x7F that aren't valid UTF-8 sequences.
Fix:       Re-save the file as UTF-8 (without BOM) in your editor.
```

### Nested Folder Structures That Break LMS Parsers

**The cardinal rule**: `imsmanifest.xml` must be at the root of the ZIP file. Not in a subfolder.

```
WRONG:
  course.zip
  └── my-course/
      ├── imsmanifest.xml    <-- NOT at root
      └── index.html

CORRECT:
  course.zip
  ├── imsmanifest.xml        <-- at root
  └── index.html
```

This is the single most common reason a SCORM package fails to import. It happens when developers zip the course folder instead of the course contents.

```bash
# WRONG: zips the folder, creating a nested structure
cd /path/to
zip -r course.zip my-course/

# CORRECT: zip the contents from inside the folder
cd /path/to/my-course
zip -r ../course.zip .
```

Some LMS platforms (notably Moodle) will attempt to detect and unwrap a single nested folder, but this behavior is not universal. Never rely on it.

### File Path Case Sensitivity

**The rule**: File paths in the manifest are case-sensitive on most servers, even if they aren't on your development machine.

```
Manifest:  <file href="Assets/Logo.PNG"/>
Actual:    assets/logo.png

Result on Mac/Windows dev: works fine
Result on Linux LMS server: 404
```

```
Best practices:
  - Use all-lowercase filenames and paths
  - Use hyphens instead of spaces or underscores
  - Validate by running a case-sensitivity check in your build pipeline
```

```javascript
// Build-time validation: check all manifest references resolve
const fs = require('fs');
const path = require('path');
const { XMLParser } = require('fast-xml-parser');

function validateManifest(distDir) {
  const manifest = fs.readFileSync(path.join(distDir, 'imsmanifest.xml'), 'utf-8');
  const parser = new XMLParser({ ignoreAttributes: false });
  const doc = parser.parse(manifest);

  const files = fs.readdirSync(distDir, { recursive: true });
  const fileSet = new Set(files.map(f => f.replace(/\\/g, '/')));

  // Extract all href attributes and check they exist
  const hrefs = extractHrefs(doc); // implement based on your manifest structure
  const missing = hrefs.filter(href => !fileSet.has(href));

  if (missing.length > 0) {
    console.error('Manifest references missing files:', missing);
    process.exit(1);
  }
}
```

---

## 4. Completion and Score Reporting Problems

### Calling LMSFinish Before LMSCommit

This is the number one cause of "completion didn't save" bugs. `LMSFinish` (SCORM 1.2) or `Terminate` (SCORM 2004) ends the communication session. If you haven't committed your data, it may be lost.

**The SCORM spec does not guarantee that `Finish`/`Terminate` implies a commit.** Some LMS implementations do an implicit commit, but many do not.

```javascript
// WRONG: data may be lost
api.LMSSetValue('cmi.core.lesson_status', 'completed');
api.LMSFinish('');

// CORRECT: always commit before finishing
api.LMSSetValue('cmi.core.lesson_status', 'completed');
api.LMSCommit('');
api.LMSFinish('');
```

### Setting lesson_status at the Wrong Time

**SCORM 1.2**: `cmi.core.lesson_status` combines completion and success into one field. Possible values: `passed`, `failed`, `completed`, `incomplete`, `browsed`, `not attempted`.

The problem: if you set `lesson_status = "completed"` early (e.g., when the learner views all slides) and then later set it to `"passed"` after an assessment, some LMS platforms take the first value and ignore the second.

```javascript
// WRONG: some LMS platforms latch on first status set
api.LMSSetValue('cmi.core.lesson_status', 'completed'); // all slides viewed
// ... later ...
api.LMSSetValue('cmi.core.lesson_status', 'passed');    // assessment passed
// Some LMS: status is still "completed", not "passed"

// BETTER: set status only once, at the final determination point
if (assessmentPassed) {
  api.LMSSetValue('cmi.core.lesson_status', 'passed');
} else if (allContentViewed) {
  api.LMSSetValue('cmi.core.lesson_status', 'completed');
}
api.LMSCommit('');
```

**SCORM 1.2 lesson_status and mastery_score interaction**: If `cmi.student_data.mastery_score` is set by the LMS and you set `cmi.core.score.raw`, some LMS platforms automatically override `lesson_status` to `passed` or `failed` based on whether the score meets the mastery threshold — regardless of what you explicitly set. This is spec-compliant behavior but catches developers off guard.

### Browser Back/Close Without Proper Termination

When a learner closes the browser tab or hits the back button, your SCORM termination code may not execute. This is the most common cause of lost progress across all LMS platforms.

**The `unload` event is unreliable:**

```javascript
// UNRELIABLE: may not fire, especially on mobile
window.addEventListener('unload', () => {
  api.LMSCommit('');
  api.LMSFinish('');
});

// SLIGHTLY BETTER: beforeunload fires more reliably on desktop
window.addEventListener('beforeunload', () => {
  api.LMSSetValue('cmi.core.exit', 'suspend');
  api.LMSCommit('');
  api.LMSFinish('');
});
```

**Best practice — commit frequently, not just on exit:**

```javascript
// Commit on every meaningful state change
function onSlideChange(slideIndex) {
  api.LMSSetValue('cmi.core.lesson_location', slideIndex.toString());
  api.LMSSetValue('cmi.suspend_data', serializeState());
  api.LMSSetValue('cmi.core.exit', 'suspend');
  api.LMSCommit('');
}

// Also commit on a timer as a safety net
setInterval(() => {
  api.LMSCommit('');
}, 30000); // Every 30 seconds
```

**Use `navigator.sendBeacon` as a last resort**: If your LMS supports a direct HTTP endpoint for SCORM data (AICC-style), you can use `sendBeacon` in `unload` handlers. This is the only reliable way to send data during page unload. However, most SCORM implementations communicate through JavaScript API objects, not HTTP endpoints, so this is only applicable if you control the server side.

### SCORM 2004: completion_status vs. success_status Confusion

SCORM 2004 separates what SCORM 1.2 combined into `lesson_status`:

| Element | Values | Purpose |
|---------|--------|---------|
| `cmi.completion_status` | `completed`, `incomplete`, `not attempted`, `unknown` | Did the learner finish the content? |
| `cmi.success_status` | `passed`, `failed`, `unknown` | Did the learner pass the assessment? |

**Common mistakes:**

1. **Setting only `completion_status`**: The LMS may require both fields. A course can be `completed` but `failed` (learner saw everything but didn't pass the quiz).

2. **Setting only `success_status`**: Some LMS platforms only check `completion_status` for the completion indicator in the UI. Setting `passed` without `completed` shows a pass in the gradebook but an incomplete in the progress tracker.

3. **Forgetting `cmi.progress_measure`**: This 0.0-1.0 float tells the LMS how far along the learner is. Some LMS platforms use it to calculate percentage complete in dashboards. Set it alongside `completion_status`.

```javascript
// SCORM 2004: Complete reporting pattern
function reportFinalStatus(api, { percentComplete, score, maxScore, passed }) {
  // Completion
  api.SetValue('cmi.progress_measure', percentComplete.toFixed(2));
  api.SetValue('cmi.completion_status',
    percentComplete >= 1.0 ? 'completed' : 'incomplete');

  // Success (only if assessment was attempted)
  if (score !== undefined) {
    api.SetValue('cmi.score.raw', score.toString());
    api.SetValue('cmi.score.max', maxScore.toString());
    api.SetValue('cmi.score.min', '0');
    api.SetValue('cmi.score.scaled', (score / maxScore).toFixed(4));
    api.SetValue('cmi.success_status', passed ? 'passed' : 'failed');
  }

  api.Commit('');
}
```

### Score Reporting Edge Cases

**SCORM 1.2 `cmi.core.score.raw`:**
- Must be a number between `cmi.core.score.min` and `cmi.core.score.max`
- Some LMS platforms expect 0-100 range and reject other ranges
- Always set `min` and `max` before setting `raw`

**SCORM 2004 `cmi.score.scaled`:**
- Range: -1.0 to 1.0
- This is the primary score element in SCORM 2004 (many LMS platforms only read this)
- Must be set as a string: `"0.85"`, not the number `0.85`

**Edge case — zero scores:**
```javascript
// Some LMS platforms treat "0" score as "no score" and ignore it
api.LMSSetValue('cmi.core.score.raw', '0');
// Workaround: use "0.0" or set lesson_status to "failed" explicitly
```

**Edge case — decimal precision:**
```javascript
// WRONG: too many decimal places may be truncated or rejected
api.SetValue('cmi.score.scaled', '0.8571428571428571');

// CORRECT: use reasonable precision (4 decimal places)
api.SetValue('cmi.score.scaled', '0.8571');
```

---

## 5. Testing and Debugging Toolkit

### Browser DevTools Techniques

**Console filtering for SCORM calls**: Most LMS SCORM players log API calls to the console. Filter by "SCORM", "LMS", "API", or "cmi" to see the traffic.

**Intercept and log all SCORM API calls**: Wrap the API object with a Proxy to log every call without modifying your course code.

```javascript
// Paste this in DevTools console BEFORE the course initializes
(function() {
  const apiNames = ['API', 'API_1484_11'];
  apiNames.forEach(name => {
    const original = window[name];
    if (!original) return;

    window[name] = new Proxy(original, {
      get(target, prop) {
        const value = target[prop];
        if (typeof value === 'function') {
          return function(...args) {
            const result = value.apply(target, args);
            console.log(
              `%c${name}.${prop}(${args.map(a => JSON.stringify(a)).join(', ')}) → ${JSON.stringify(result)}`,
              'color: #0066cc; font-family: monospace;'
            );
            return result;
          };
        }
        return value;
      }
    });
  });
  console.log('%cSCORM API logging enabled', 'color: green; font-weight: bold;');
})();
```

**Network tab**: Watch for XHR/Fetch requests from the LMS player when `LMSCommit` is called. Failed requests indicate server-side issues.

**Application tab > Storage**: Some LMS players cache SCORM data in `localStorage` or `sessionStorage`. Check these to see what the LMS thinks the current state is.

### Console Logging Wrapper for SCORM API Calls

Include this wrapper in your course code during development. It logs all SCORM communication with timestamps and error checking.

```typescript
type ScormAPI = Record<string, (...args: string[]) => string>;

function createLoggingWrapper(api: ScormAPI, apiName: string): ScormAPI {
  const wrapper: ScormAPI = {};
  const methods = [
    // SCORM 1.2
    'LMSInitialize', 'LMSFinish', 'LMSGetValue', 'LMSSetValue',
    'LMSCommit', 'LMSGetLastError', 'LMSGetErrorString', 'LMSGetDiagnostic',
    // SCORM 2004
    'Initialize', 'Terminate', 'GetValue', 'SetValue',
    'Commit', 'GetLastError', 'GetErrorString', 'GetDiagnostic',
  ];

  for (const method of methods) {
    if (typeof api[method] === 'function') {
      wrapper[method] = (...args: string[]) => {
        const start = performance.now();
        const result = api[method](...args);
        const duration = (performance.now() - start).toFixed(1);

        // Color-code by type
        const isError = result === 'false' || result === false;
        const isGet = method.includes('Get');
        const style = isError
          ? 'color: red; font-weight: bold'
          : isGet
            ? 'color: #666'
            : 'color: #0066cc';

        console.log(
          `%c[SCORM ${duration}ms] ${method}(${args.join(', ')}) → ${result}`,
          style
        );

        // Auto-check for errors after SetValue and Commit
        if (isError && !method.includes('Error') && !method.includes('Diagnostic')) {
          const errorCode = api.LMSGetLastError?.() || api.GetLastError?.();
          const errorString = api.LMSGetErrorString?.(errorCode) || api.GetErrorString?.(errorCode);
          const diagnostic = api.LMSGetDiagnostic?.(errorCode) || api.GetDiagnostic?.(errorCode);
          console.error(`[SCORM ERROR] Code: ${errorCode}, ${errorString}, Detail: ${diagnostic}`);
        }

        return result;
      };
    }
  }

  return wrapper;
}

// Usage:
// const rawApi = findAPI();
// const api = createLoggingWrapper(rawApi, 'API');
// api.LMSInitialize('');
```

### SCORM Cloud Testing Workflow

SCORM Cloud (cloud.scorm.com) is the gold standard for SCORM validation. Free tier allows limited uploads.

**Step-by-step testing process:**

1. **Create an account** at https://cloud.scorm.com (free tier available).

2. **Upload your package**: Library > Import Course > select your ZIP file. SCORM Cloud validates the manifest on import and reports any structural issues.

3. **Check import results**: Look for warnings and errors in the import log.
   - Green: clean import, no issues
   - Yellow: warnings (missing schema files, non-standard elements) — usually still works
   - Red: errors (broken manifest, missing entry point) — will not launch

4. **Launch the course**: Click the course > Launch. SCORM Cloud opens your content in its player with full API logging enabled.

5. **Check the debug log**: After completing the course, go to the course's Activity tab. SCORM Cloud logs every API call with timestamps, values, and error codes. This is invaluable for diagnosing communication issues.

6. **Verify reporting**: Check that completion status, score, and suspend_data were recorded correctly in the Registration detail view.

7. **Test resume**: Launch the course again. Verify that `cmi.suspend_data` and `cmi.core.lesson_location` restore correctly and the course resumes from where the learner left off.

8. **Test multiple attempts**: If your course supports multiple attempts, start a new registration and verify attempt tracking.

**Common SCORM Cloud import errors:**

| Error | Cause | Fix |
|-------|-------|-----|
| "No manifest found" | `imsmanifest.xml` not at ZIP root | Re-zip from inside the content folder |
| "Referenced resource not found" | Manifest lists a file that doesn't exist in ZIP | Check `href` paths and case sensitivity |
| "Schema validation error" | Invalid XML in manifest | Run manifest through an XML validator |
| "No launchable SCO" | Resource missing `adlcp:scormtype="sco"` | Add the scormtype attribute to resource element |

### Local Development Setup with scorm-again

For fast iteration without uploading to an LMS, use `scorm-again` to mock the SCORM API locally.

```typescript
// dev/scorm-mock.ts — import this ONLY in development
import { Scorm12API } from 'scorm-again';

export function setupScormMock() {
  if ((window as any).API) {
    console.log('Real SCORM API found — skipping mock');
    return;
  }

  const api = new Scorm12API({
    logLevel: 4,               // Verbose logging
    selfReportSessionTime: true,
    autocommit: true,
    lmsCommitUrl: false,       // No server — all local
  });

  // Optionally pre-populate suspend_data to test resume scenarios
  // api.setCMIValue('cmi.suspend_data', '...');
  // api.setCMIValue('cmi.core.lesson_location', '3');

  (window as any).API = api;

  // Log all events for debugging
  api.on('LMSInitialize', () => console.log('[MOCK] LMSInitialize'));
  api.on('LMSFinish', () => console.log('[MOCK] LMSFinish'));
  api.on('LMSCommit', () => {
    console.log('[MOCK] LMSCommit — current state:');
    console.log('  lesson_status:', api.getCMIValue('cmi.core.lesson_status'));
    console.log('  lesson_location:', api.getCMIValue('cmi.core.lesson_location'));
    console.log('  score.raw:', api.getCMIValue('cmi.core.score.raw'));
    console.log('  suspend_data length:', (api.getCMIValue('cmi.suspend_data') || '').length);
  });

  console.log('%c[SCORM Mock] API mounted on window.API', 'color: orange; font-weight: bold');
}
```

```typescript
// In your course entry point
if (import.meta.env.DEV) {
  const { setupScormMock } = await import('./dev/scorm-mock');
  setupScormMock();
}
```

**Persisting mock state between reloads**: scorm-again stores state in memory by default. To persist across page reloads during development, save to `localStorage`:

```typescript
api.on('LMSCommit', () => {
  const state = {
    suspendData: api.getCMIValue('cmi.suspend_data'),
    location: api.getCMIValue('cmi.core.lesson_location'),
    status: api.getCMIValue('cmi.core.lesson_status'),
    scoreRaw: api.getCMIValue('cmi.core.score.raw'),
  };
  localStorage.setItem('scorm-dev-state', JSON.stringify(state));
});

// On setup, restore previous state
const saved = localStorage.getItem('scorm-dev-state');
if (saved) {
  const state = JSON.parse(saved);
  // Pre-populate the mock API with saved state
  // Use api.setCMIValue() methods as appropriate
}
```

### Common Test Scenarios Checklist

Run through every scenario on every target LMS before declaring a package ready for production.

**Launch and Initialize:**
- [ ] Course loads without JavaScript errors
- [ ] SCORM API is found (no "API not found" warnings)
- [ ] `LMSInitialize` / `Initialize` returns `"true"`
- [ ] Learner name and ID are retrievable via `GetValue`

**Progress and Bookmarking:**
- [ ] Navigate to slide 5, close the course
- [ ] Re-launch — course resumes at slide 5 (not slide 1)
- [ ] `cmi.suspend_data` round-trips correctly (no truncation)
- [ ] `cmi.core.lesson_location` / `cmi.location` restores correctly

**Completion:**
- [ ] Complete all content — `lesson_status` = `completed` (SCORM 1.2)
- [ ] Complete all content — `completion_status` = `completed` (SCORM 2004)
- [ ] LMS gradebook/progress shows completed
- [ ] Completion persists after browser close and re-login

**Scoring:**
- [ ] Pass assessment — `lesson_status` = `passed` or `success_status` = `passed`
- [ ] Fail assessment — status reflects failure
- [ ] Score appears correctly in LMS gradebook
- [ ] Min, max, and raw/scaled scores are all recorded

**Edge Cases:**
- [ ] Close browser mid-course (no unload event) — progress is saved from last commit
- [ ] Rapidly click through all slides — no race conditions in API calls
- [ ] Open course in two tabs simultaneously — second tab handles gracefully
- [ ] LMS session timeout during course — user sees helpful error, not silent failure
- [ ] Course works on iPad Safari (mobile viewport, touch events, `visibilitychange`)
- [ ] Course works in LMS mobile app WebView (if applicable)

**Multi-Attempt (if applicable):**
- [ ] Start new attempt — state resets correctly
- [ ] Previous attempt scores are preserved in LMS
- [ ] Best/latest/average scoring rule (configured in LMS) works as expected

---

## 6. Package Size and Performance Issues

### LMS Upload Limits by Platform

| LMS Platform | Max Package Size | Notes |
|-------------|-----------------|-------|
| WorkRamp (Rustici) | 1 GB | Generous, but large packages have slow import times |
| Moodle | 256 MB (default) | Configurable by admin via `maxbytes` setting; PHP `upload_max_filesize` and `post_max_size` may also limit |
| Cornerstone | 500 MB | Varies by instance configuration |
| SAP SuccessFactors | 250 MB | iContent repository may have separate limits |
| SCORM Cloud | 250 MB (free tier) | Higher limits on paid plans |
| Canvas | 500 MB | Configurable per account |
| Blackboard | 250 MB | Varies; Ultra vs. Original have different limits |

**When your package exceeds the limit**, you have three options:
1. Optimize media assets (see below)
2. Split into multiple SCOs within one package
3. Offload large assets to a CDN (see below)

### Large Media Optimization Strategies

**Video** (usually the biggest contributor):

```
Before: 1080p MP4, H.264 High profile, 8 Mbps → 60 MB per minute
After:  720p MP4, H.264 Main profile, 2 Mbps → 15 MB per minute

ffmpeg command:
  ffmpeg -i input.mp4 -vf scale=-2:720 -c:v libx264 -profile:v main \
    -preset slow -crf 23 -c:a aac -b:a 128k -movflags +faststart output.mp4
```

Use `-movflags +faststart` so the video can begin playing before fully downloaded (critical inside SCORM packages served from LMS storage, which may be slow).

**Images:**

```
- Use WebP format (30-50% smaller than JPEG at same quality)
- Resize to actual display dimensions (don't serve 4000px images in 800px containers)
- Use responsive images with srcset if viewport varies
- Use SVG for icons, diagrams, and illustrations
- Compress PNGs with pngquant or oxipng
- Target: no single image over 200 KB
```

**Audio:**

```
- Use AAC in MP4 container (best compatibility)
- 128 kbps stereo for narration, 64 kbps mono if voice-only
- Trim silence from beginning/end of clips
```

**Fonts:**

```
- Subset fonts to include only characters actually used
- Use woff2 format (30% smaller than woff)
- Limit to 2-3 font weights
- Consider system font stack as fallback to eliminate font files entirely
```

### Code Splitting Within SCORM Packages

SCORM packages are self-contained — all code must be in the ZIP. But you can still use code splitting to improve initial load time.

**Vite/Rollup configuration for SCORM:**

```javascript
// vite.config.ts
export default defineConfig({
  build: {
    // All assets stay in the output directory (no CDN)
    assetsDir: 'assets',
    // Generate chunks for lazy-loaded routes/components
    rollupOptions: {
      output: {
        // Keep chunk filenames predictable for manifest references
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
  },
  // CRITICAL: use relative paths (SCORM packages don't know their URL)
  base: './',
});
```

**Important**: Set `base: './'` in your bundler config. SCORM content does not know its absolute URL — the LMS decides where to serve it from. Absolute paths like `/assets/chunk.js` will break.

**Lazy-load heavy components:**

```javascript
// Don't load the assessment engine until the learner reaches the quiz
const Assessment = lazy(() => import('./Assessment'));

// Don't load the video player until a video slide is reached
const VideoPlayer = lazy(() => import('./VideoPlayer'));
```

### CDN Offloading for Large Assets

For very large courses (hundreds of MB of video), you can serve media from a CDN while keeping the SCORM tracking code in the package. This is an advanced technique with tradeoffs.

**How it works:**

```
SCORM Package (uploaded to LMS):
├── imsmanifest.xml
├── index.html          ← tracking code, UI shell
├── assets/
│   ├── app-[hash].js   ← course logic + SCORM API calls
│   └── app-[hash].css
└── (no large media files)

CDN (separate hosting):
├── videos/
│   ├── module-1.mp4    ← 200 MB
│   └── module-2.mp4
└── images/
    └── hero.webp
```

**Implementation:**

```javascript
// config.ts — switch between local and CDN paths
const MEDIA_BASE = import.meta.env.PROD
  ? 'https://cdn.example.com/courses/security-101'  // CDN in production
  : '/media';  // Local in development

// Usage in components
<video src={`${MEDIA_BASE}/videos/module-1.mp4`} />
```

**Tradeoffs:**

| Pro | Con |
|-----|-----|
| Package stays under LMS upload limits | Course depends on external CDN availability |
| Faster LMS import (smaller ZIP) | CDN URLs may be blocked by corporate firewalls |
| CDN provides better video streaming | Not truly self-contained (violates SCORM spec intent) |
| Media updates without re-uploading SCORM package | CORS headers required on CDN |
| Browser caching across courses that share media | Some LMS security policies block external requests |

**CORS configuration on the CDN:**

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Range
```

The `Range` header is important for video seeking — without it, learners cannot skip ahead in videos.

**Fallback strategy**: Include a low-resolution placeholder in the SCORM package. If the CDN is unreachable, the course still functions with degraded media rather than broken entirely.

```javascript
function loadMedia(cdnUrl, fallbackUrl) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(cdnUrl);
    img.onerror = () => {
      console.warn(`CDN unreachable for ${cdnUrl}, using fallback`);
      resolve(fallbackUrl);
    };
    img.src = cdnUrl;
  });
}
```

---

## Quick Reference: Error Code Cheat Sheet

### SCORM 1.2 Error Codes

| Code | Meaning | Common Cause |
|------|---------|-------------|
| 0 | No error | Success |
| 101 | General exception | Check `LMSGetDiagnostic` |
| 201 | Invalid argument | Typo in data model element name |
| 301 | Not initialized | Forgot to call `LMSInitialize` |
| 401 | Not implemented | LMS doesn't support this element |
| 402 | Invalid set value | Wrong data type for element |
| 403 | Element is read-only | Attempted `SetValue` on read-only field |
| 404 | Element is write-only | Attempted `GetValue` on write-only field |
| 405 | Incorrect data type | Value format doesn't match spec |

### SCORM 2004 Error Codes

| Code | Meaning | Common Cause |
|------|---------|-------------|
| 0 | No error | Success |
| 102 | General init failure | LMS session expired |
| 103 | Already initialized | Double `Initialize` call |
| 104 | Content instance terminated | `Initialize` after `Terminate` |
| 111 | General termination failure | Network error during terminate |
| 113 | Already terminated | Double `Terminate` call |
| 122 | GetValue before init | Call `Initialize` first |
| 132 | SetValue before init | Call `Initialize` first |
| 142 | Commit before init | Call `Initialize` first |
| 301 | General get failure | Element not available |
| 351 | General set failure | Element cannot be set |
| 391 | General commit failure | Network/session issue |
| 401 | Undefined data model element | Typo in element name |
| 403 | Data model element not initialized | Value not yet set |
| 404 | Data model element is read-only | Cannot `SetValue` |
| 405 | Data model element is write-only | Cannot `GetValue` |
| 406 | Data model element type mismatch | Wrong value format |
| 407 | Data model element value out of range | Number outside allowed range |
| 408 | Data model dependency not established | Set prerequisite element first |

---

## Diagnostic Decision Tree

When something is not working, follow this tree:

```
Course doesn't launch at all
├── Check: is imsmanifest.xml at the ZIP root?
├── Check: does the manifest reference the correct entry point file?
├── Check: does the LMS import log show errors?
└── Check: is the resource type set to "sco" (not "asset")?

Course launches but shows "API not found"
├── Check: are you looking for the right API name? (API vs API_1484_11)
├── Check: is the content in a cross-origin iframe?
│   └── Yes → use postMessage bridge (CrossFrameAPI)
├── Check: is the iframe sandboxed without allow-same-origin?
├── Check: is the content in a deeply nested iframe (>7 levels)?
└── Check: timing — is the API available when your code runs?
    └── No → add retry logic with backoff

Course launches but completion doesn't save
├── Check: are you calling LMSCommit before LMSFinish?
├── Check: does LMSCommit return "true"?
│   └── "false" → check LMSGetLastError for the code
├── Check: are you setting the right status element?
│   ├── SCORM 1.2: cmi.core.lesson_status
│   └── SCORM 2004: cmi.completion_status AND cmi.success_status
├── Check: is the LMS overriding status based on mastery_score?
└── Check: is the browser closing before commit completes?
    └── Yes → commit on every state change, not just on exit

Score doesn't appear in LMS gradebook
├── Check: are you setting score.min and score.max?
├── Check: SCORM 2004 — are you setting score.scaled? (primary score element)
├── Check: is score.raw within the min/max range?
├── Check: is the LMS configured to read scores from this SCORM element?
└── Check: are you committing after setting the score?

suspend_data doesn't restore on resume
├── Check: are you setting cmi.core.exit = "suspend" before finishing?
├── Check: is suspend_data within size limits? (4096 bytes for 1.2)
├── Check: is the data ASCII-safe? (use base64 or URI-encoded compression)
├── Check: does GetValue return the exact string you saved?
│   └── No → data was truncated by LMS
└── Check: does your deserialization handle empty string on first launch?
```
