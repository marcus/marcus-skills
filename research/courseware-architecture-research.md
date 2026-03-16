# Interactive Courseware Delivery: Technical Architecture Research

> Research compiled March 2026. Covers packaging standards, modern architecture patterns, LMS integration, content pipelines, and open-source tooling.

---

## Table of Contents

1. [Course Packaging and Delivery Standards](#1-course-packaging-and-delivery-standards)
2. [Modern Courseware Architecture Patterns](#2-modern-courseware-architecture-patterns)
3. [LMS Integration Specifics](#3-lms-integration-specifics)
4. [Content Pipeline Architecture](#4-content-pipeline-architecture)
5. [Open Source Course Players and Libraries](#5-open-source-course-players-and-libraries)
6. [Recommendations and Architectural Decision Guide](#6-recommendations-and-architectural-decision-guide)
7. [Sources](#7-sources)

---

## 1. Course Packaging and Delivery Standards

### 1.1 SCORM (Sharable Content Object Reference Model)

SCORM is the most widely adopted eLearning interoperability standard, maintained by ADL (Advanced Distributed Learning). It defines how course content is packaged and how it communicates with an LMS at runtime.

#### SCORM 1.2

- **Released:** 2001 (still widely used)
- **Content Packaging:** ZIP file (Package Interchange File / PIF) containing:
  - `imsmanifest.xml` at the root (mandatory)
  - HTML, CSS, JavaScript, media assets
  - Schema definition files (XSD)
- **Manifest Structure (imsmanifest.xml):**
  - `<metadata>` -- Title, description, keywords, version
  - `<organizations>` -- Defines learning activity tree structure (items referencing SCOs)
  - `<resources>` -- Lists all files and dependencies, maps identifiers to physical files
  - `<schema>` and `<schemaversion>` -- Declares SCORM 1.2 conformance
- **Runtime Data Model (CMI):** Communication via JavaScript API object named `API`
  - Key elements: `cmi.core.student_id`, `cmi.core.student_name`, `cmi.core.lesson_location` (bookmark), `cmi.core.lesson_status` (passed/completed/failed/incomplete/browsed/not attempted), `cmi.core.score.raw`, `cmi.core.score.min`, `cmi.core.score.max`, `cmi.core.total_time`, `cmi.core.session_time`, `cmi.core.exit`, `cmi.core.entry`, `cmi.core.credit`
  - `cmi.suspend_data` -- Free-form string (max 4,096 bytes in SCORM 1.2) for persisting state between sessions
  - `cmi.launch_data` -- Read-only data from the manifest
  - `cmi.objectives.n.*` -- Objective-level tracking
  - `cmi.interactions.n.*` -- Interaction/question-level tracking
- **API Methods:** `LMSInitialize("")`, `LMSGetValue(element)`, `LMSSetValue(element, value)`, `LMSCommit("")`, `LMSFinish("")`, `LMSGetLastError()`, `LMSGetErrorString(errCode)`, `LMSGetDiagnostic(errCode)`
- **Limitations:**
  - No sequencing rules (linear or free navigation only, controlled by content)
  - 4,096-byte suspend_data limit (many tools compress to fit)
  - Tracks only formal, browser-based learning
  - Course must run inside an LMS-provided window/frame

#### SCORM 2004 (Editions 1-4)

- **Released:** 2004, with 4th Edition (2009) being the current recommendation
- **Key Additions Over SCORM 1.2:**
  - **Sequencing and Navigation (SN):** Based on IMS Simple Sequencing. Defines rules in the manifest that control activity delivery order. Categories include:
    - *Sequencing Control Modes* -- Free navigation via TOC vs. linear prev/next
    - *Constrain Choice Controls* -- Restrict available activities
    - *Sequencing Rules* -- If-then conditions using tracking data to determine availability
    - *Rollup Rules* -- How child activity statuses roll up to parent
    - *Objectives* -- Shared global objectives for cross-SCO dependencies
  - **Enhanced Data Model:** `cmi.completion_status` and `cmi.success_status` (separated from SCORM 1.2's combined `lesson_status`), `cmi.progress_measure` (0.0-1.0), `cmi.scaled_score` (-1.0 to 1.0)
  - **Larger suspend_data:** Up to 64,000 characters
  - **Navigation requests:** SCO can request navigation actions (continue, previous, exit, etc.)
- **Runtime API:** Object named `API_1484_11`
  - Methods: `Initialize("")`, `GetValue(element)`, `SetValue(element, value)`, `Commit("")`, `Terminate("")`, `GetLastError()`, `GetErrorString(errCode)`, `GetDiagnostic(errCode)`
- **Manifest Changes:** More attributes and sub-elements for sequencing definitions, prerequisites, completion thresholds, and objective mappings
- **The Sequencing Loop:** The LMS maintains a sequencing loop -- a set of defined algorithms (specified in pseudo-code by the spec) that process sequencing rules against current tracking data to determine the next activity to deliver

#### SCORM Package Structure Summary

```
course-package.zip
├── imsmanifest.xml          # Course structure, metadata, resource listings
├── adlcp_rootv1p2.xsd       # SCORM schema files (version-specific)
├── imscp_rootv1p1p2.xsd
├── imsmd_rootv1p2p1.xsd
├── index.html                # Primary SCO entry point
├── js/
│   ├── scorm-wrapper.js      # SCORM API communication layer
│   └── course.js             # Course logic
├── css/
│   └── styles.css
├── media/
│   ├── images/
│   ├── video/
│   └── audio/
└── data/
    └── course-data.json      # Course content data
```

### 1.2 xAPI (Experience API / Tin Can API)

xAPI is an IEEE-approved standard (IEEE 9274.1.1-2023) that enables tracking of learning experiences across any context -- not just within an LMS.

#### Statement Structure

Every xAPI record is a "statement" encoded in JSON following the Actor-Verb-Object pattern:

```json
{
  "id": "12345678-1234-5678-1234-567812345678",
  "actor": {
    "objectType": "Agent",
    "name": "Jane Doe",
    "mbox": "mailto:jane@example.com"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/completed",
    "display": {
      "en-US": "completed"
    }
  },
  "object": {
    "objectType": "Activity",
    "id": "http://example.com/courses/safety-101",
    "definition": {
      "name": { "en-US": "Safety 101" },
      "description": { "en-US": "Introductory safety training course" },
      "type": "http://adlnet.gov/expapi/activities/course"
    }
  },
  "result": {
    "score": { "scaled": 0.95, "raw": 95, "min": 0, "max": 100 },
    "success": true,
    "completion": true,
    "duration": "PT1H30M"
  },
  "context": {
    "registration": "ec531277-b0b7-4c15-a461-c18db348d3a3",
    "contextActivities": {
      "parent": [{ "id": "http://example.com/programs/onboarding" }],
      "grouping": [{ "id": "http://example.com/org/acme-corp" }]
    },
    "instructor": {
      "name": "John Smith",
      "mbox": "mailto:john@example.com"
    }
  },
  "timestamp": "2026-03-15T10:30:00Z"
}
```

#### Statement Components

| Component | Required | Purpose |
|-----------|----------|---------|
| **actor** | Yes | Who performed the action (Agent or Group, identified by mbox, mbox_sha1sum, openid, or account) |
| **verb** | Yes | What action was performed (IRI identifier + human-readable display) |
| **object** | Yes | What the action was performed on (Activity, Agent, SubStatement, or StatementRef) |
| **result** | No | Outcome -- score, success, completion, duration, response, extensions |
| **context** | No | Additional context -- registration UUID, instructor, team, parent/grouping activities, platform, language, extensions |
| **timestamp** | No | When the experience occurred (ISO 8601) |
| **authority** | No | Who is asserting this statement is true |
| **attachments** | No | Digital artifacts related to the statement |

#### Learning Record Store (LRS)

The LRS is the central data repository in the xAPI ecosystem:

- **Purpose:** Receives, stores, and returns xAPI statements
- **Unlike an LMS:** Does NOT manage users, deliver content, or provide courses -- it only stores statements and provides analytics/reporting
- **Key capabilities:**
  - RESTful API for statement submission and querying
  - Statement forwarding to other LRSs
  - Activity state and agent profile storage
  - Statement aggregation and reporting
- **Deployment options:**
  - Standalone LRS (e.g., Learning Locker, SQL LRS)
  - LRS built into an LMS (e.g., many modern LMS platforms include an embedded LRS)
  - Cloud-hosted LRS (e.g., SCORM Cloud LRS, Watershed by Rustici)

#### xAPI Advantages Over SCORM

- Tracks learning beyond the browser/LMS (mobile, simulations, real-world activities, social learning, coaching)
- No single-window requirement -- content can run anywhere
- Richer data model with extensible JSON
- Supports offline data collection with later synchronization
- Statements can be generated by any system, not just courseware

#### xAPI Limitations

- More complex implementation than SCORM
- Requires LRS infrastructure (additional cost/setup)
- Less universal LMS support than SCORM (though growing)
- No built-in content packaging or launch mechanism (addressed by cmi5)

### 1.3 cmi5: The Bridge Between SCORM and xAPI

cmi5 is an xAPI Profile that provides rules for how courses are imported, launched, and tracked using an LMS and xAPI. It combines SCORM's structured LMS integration with xAPI's rich data tracking.

**Formula: cmi5 = xAPI + LMS launch mechanism + defined vocabularies**

#### Key Concepts

- **Assignable Unit (AU):** A separately launchable piece of content (analogous to a SCORM SCO). AUs include concepts of completion, success, score, and duration.
- **Course Structure:** Defined in a `cmi5.xml` file (analogous to `imsmanifest.xml`) containing XML metadata describing blocks and AUs
- **Package Format:** ZIP file containing `cmi5.xml` and course assets, imported into a cmi5-compatible LMS

#### cmi5 Statement Categories

| Category | Description |
|----------|-------------|
| **cmi5 defined** | Statements the AU or LMS MUST send (launched, initialized, completed, passed, failed, terminated, abandoned, waived, satisfied) |
| **cmi5 allowed** | Additional xAPI statements the AU MAY send for granular tracking |

#### cmi5 Launch Flow

1. LMS generates a launch URL with authentication token and endpoint information
2. AU opens in a browser window/tab
3. AU retrieves session configuration from the LMS (via a fetch URL)
4. AU sends `initialized` statement to the LRS
5. AU tracks learning activities (sends cmi5-defined and allowed statements)
6. AU sends `completed` and/or `passed`/`failed` statements
7. AU sends `terminated` statement
8. LMS processes results

#### cmi5 Advantages

- Plug-and-play interoperability between content and LMS (like SCORM)
- Full xAPI data richness
- Content can run in its own window (not restricted to an LMS iframe)
- Standardized vocabulary ensures consistent reporting
- Clear specification for what data must/must not be included

### 1.4 LTI 1.3 (Learning Tools Interoperability)

LTI is a standard from 1EdTech (formerly IMS Global) for integrating external tools and content into learning platforms. LTI 1.3 is the current version with modern security.

#### Security Architecture

- Uses **OAuth 2.0**, **OpenID Connect (OIDC)**, **JSON Web Tokens (JWT)**, and **asymmetric public/private key pairs**
- Requires **HTTPS (TLS)** for all messages and services
- Minimum RSA 2048-bit keys; supports Elliptic Curve
- **JWK Sets** required for platform public key exposure (enables key rotation without disruption)

#### Launch Flow

1. Platform sends login initiation request to tool's login endpoint
2. Tool validates issuer and client_id, generates CSRF token
3. Tool initiates OIDC authentication flow
4. Platform returns signed JWT (id_token) with launch data
5. Tool validates JWT signature and claims
6. Tool renders content/functionality

#### LTI Advantage Services

| Service | Purpose |
|---------|---------|
| **Assignment and Grade Services (AGS) v2.0** | Tool can create line items and submit grades back to the platform |
| **Names and Role Provisioning Services (NRPS) v2.0** | Tool can retrieve course roster and role information |
| **Deep Linking v2.0** | Instructor can select specific content/activities from the tool to embed in the course |

#### LTI vs. SCORM/xAPI

- **LTI** is for tool integration (embedding external apps within an LMS)
- **SCORM/xAPI** is for content packaging and learning data tracking
- They are complementary: an LTI tool can internally use xAPI for tracking
- LTI handles authentication, authorization, and grade passback; SCORM/xAPI handles granular learning data

### 1.5 Building Content That Works Across Multiple Standards

#### Multi-Standard Architecture Pattern

```
┌─────────────────────────────────────────────┐
│              Course Application              │
│         (React/Vue/Vanilla JS SPA)           │
├─────────────────────────────────────────────┤
│           Abstraction Layer (API)            │
│  ┌─────────┬──────────┬───────┬───────────┐ │
│  │ SCORM   │  xAPI    │ cmi5  │ Standalone │ │
│  │ Adapter │  Adapter │Adapter│  Adapter   │ │
│  └─────────┴──────────┴───────┴───────────┘ │
├─────────────────────────────────────────────┤
│         Environment Detection               │
│  (Check for API / API_1484_11 / xAPI        │
│   endpoint / cmi5 launch params / none)     │
└─────────────────────────────────────────────┘
```

**Strategy:**

1. Build the course as a modern web application (SPA)
2. Create a thin abstraction layer that normalizes tracking calls (e.g., `reportCompletion()`, `saveProgress()`, `reportScore()`)
3. Implement adapters for each standard behind the abstraction
4. At launch, detect the environment:
   - Look for `window.API` (SCORM 1.2) or `window.API_1484_11` (SCORM 2004) by traversing parent frames
   - Check for cmi5 launch parameters in the URL
   - Check for xAPI endpoint configuration
   - Fall back to standalone mode (localStorage or no tracking)
5. Package the same content differently for each target:
   - SCORM: Add `imsmanifest.xml` + ZIP
   - cmi5: Add `cmi5.xml` + ZIP
   - xAPI: Configure LRS endpoint
   - LTI: Implement LTI launch handler on a server
   - Standalone: Serve as a regular web app

---

## 2. Modern Courseware Architecture Patterns

### 2.1 Headless LMS Architecture

A headless LMS decouples the backend (user management, enrollment, tracking, content management) from the frontend (UI/UX), communicating entirely through APIs.

#### Key Characteristics

- **API-first design:** RESTful or GraphQL APIs expose all functionality
- **Framework-agnostic frontend:** Consume APIs from React, Vue, Angular, Svelte, mobile apps, or any client
- **Multi-channel delivery:** Same backend serves web, mobile app, chatbot, VR, IoT devices
- **Microservices-friendly:** Backend services can be independently scaled and deployed

#### Benefits

- Unlimited UI customization without backend changes
- 38% reduction in frontend development time for multi-platform environments (industry benchmark)
- 35% reduction in integration effort
- Easier to embed learning experiences within existing products/portals
- Content can be delivered through any channel

#### Notable Open Source: Wellms (EscolaLMS)

- World's first open-source headless LMS
- Written in PHP 8 (Laravel) + TypeScript
- Fully documented RESTful API
- Built-in H5P support (headless)
- Course import/export with open, documented data format
- Event-sourcing backend enables flexible integrations (Mattermost, Slack, Jitsi, YouTube, AWS streaming)
- AWS S3/CloudFront integration for CDN delivery
- Docker deployment (3-minute setup)
- 1000+ integration tests
- Repository: [github.com/EscolaLMS](https://github.com/EscolaLMS)

### 2.2 Single Page Application (SPA) Courses

#### Architecture

```
┌──────────────────────────────────────┐
│         SPA Course Shell             │
│  ┌────────────────────────────────┐  │
│  │      Router / Navigator       │  │
│  ├────────────────────────────────┤  │
│  │      State Management         │  │
│  │   (Progress, Responses,       │  │
│  │    Bookmarks, Scores)         │  │
│  ├────────────────────────────────┤  │
│  │      Content Renderer         │  │
│  │   (Slides, Interactions,      │  │
│  │    Video, Quizzes, Sims)      │  │
│  ├────────────────────────────────┤  │
│  │      LMS Communication        │  │
│  │   (SCORM/xAPI/cmi5 Adapter)   │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

#### SPA Advantages for Courseware

- **Fluid navigation:** No page reloads between slides/sections
- **Rich interactivity:** Full JavaScript framework capabilities (animations, drag-and-drop, simulations)
- **State persistence:** In-memory state management keeps all progress data available
- **Lazy loading:** Load content on demand for faster initial load
- **Offline capability:** Service workers can cache the entire course
- **Component reuse:** Shared UI components (quiz engine, video player, navigation) across courses

#### SPA vs. Multi-Page Courses

| Aspect | SPA | Multi-Page |
|--------|-----|------------|
| Navigation feel | Smooth, app-like | Page reload flicker |
| SCORM compatibility | Excellent (single SCO) | Requires careful multi-SCO design |
| Initial load | Larger (can be mitigated with code splitting) | Smaller per page |
| Offline support | Easier with service worker | More complex |
| State management | Centralized in memory | Requires server-side or storage |
| SEO | Irrelevant for LMS-hosted courses | Irrelevant for LMS-hosted courses |
| Complexity | Higher initial setup | Simpler per page |

### 2.3 Progressive Web App (PWA) Courses

PWAs use modern web capabilities to deliver app-like experiences, particularly relevant for mobile and offline courseware.

#### Key Technologies

- **Service Workers:** Programmable proxy scripts that intercept network requests. Three caching strategies:
  - *Cache First:* Serve from cache, fall back to network (best for static course assets)
  - *Network First:* Try network, fall back to cache (best for dynamic content)
  - *Stale While Revalidate:* Serve cache immediately, update cache from network in background
- **Web App Manifest:** JSON file enabling "Add to Home Screen" installation
- **IndexedDB:** Client-side database for storing course progress, xAPI statements (for later sync), and large datasets

#### Offline-First Courseware Architecture

```
┌─────────────────────────────────────────┐
│            PWA Course App               │
├─────────────────────────────────────────┤
│  Service Worker                         │
│  ├── Cache: Course shell (HTML/CSS/JS)  │
│  ├── Cache: Media assets                │
│  ├── Cache: Course data (JSON)          │
│  └── Background sync: xAPI statements   │
├─────────────────────────────────────────┤
│  IndexedDB                              │
│  ├── Progress data                      │
│  ├── Queued xAPI statements             │
│  ├── User responses                     │
│  └── Downloaded content                 │
├─────────────────────────────────────────┤
│  Sync Manager                           │
│  ├── Detect online/offline status       │
│  ├── Queue writes when offline          │
│  ├── Batch sync when online             │
│  └── Conflict resolution                │
└─────────────────────────────────────────┘
```

#### Implementation Considerations

- Pre-cache all course content during installation for true offline support
- Queue xAPI statements in IndexedDB when offline; batch-send on reconnection
- SCORM is inherently online (requires LMS API), but suspend_data can be cached locally and committed on reconnection
- For cmi5, the AU can store statements locally and submit when the connection is restored
- Media assets (video, audio) should use progressive download with range request support

### 2.4 Embedding Rich Web Apps in SCORM Wrappers

This is the most practical pattern for delivering modern interactive content within legacy LMS infrastructure.

#### Approach

1. **Build your course** as a modern SPA (React, Vue, Svelte, etc.) using Vite or Webpack
2. **Add a thin SCORM communication layer** using a library like scorm-again or pipwerks
3. **Generate imsmanifest.xml** (manually or via build tooling like simple-scorm-packager)
4. **Package as a ZIP** containing the built assets + manifest + schema files
5. **Upload to LMS** as a standard SCORM package

#### SCORM Wrapper Integration Points

```javascript
// Minimal SCORM integration pattern
import { Scorm12API } from 'scorm-again';

class CourseTracker {
  constructor() {
    this.api = null;
    this.isLMSAvailable = false;
  }

  initialize() {
    // Detect SCORM API in parent frames
    this.api = this.findSCORMAPI();
    if (this.api) {
      this.api.LMSInitialize('');
      this.isLMSAvailable = true;
    }
  }

  saveBookmark(location) {
    if (this.isLMSAvailable) {
      this.api.LMSSetValue('cmi.core.lesson_location', location);
      this.api.LMSCommit('');
    } else {
      localStorage.setItem('bookmark', location);
    }
  }

  getBookmark() {
    if (this.isLMSAvailable) {
      return this.api.LMSGetValue('cmi.core.lesson_location');
    }
    return localStorage.getItem('bookmark');
  }

  reportCompletion(score) {
    if (this.isLMSAvailable) {
      this.api.LMSSetValue('cmi.core.lesson_status', 'completed');
      this.api.LMSSetValue('cmi.core.score.raw', score.toString());
      this.api.LMSSetValue('cmi.core.exit', 'suspend');
      this.api.LMSCommit('');
    }
  }

  terminate() {
    if (this.isLMSAvailable) {
      this.api.LMSFinish('');
    }
  }

  findSCORMAPI() {
    // Search up through parent frames for SCORM API
    let win = window;
    let findAttempts = 0;
    while (win.API == null && win.parent != null
           && win.parent != win && findAttempts < 500) {
      findAttempts++;
      win = win.parent;
    }
    return win.API || null;
  }
}
```

#### Cross-Frame Communication

scorm-again v3.0.0+ supports a Cross-Frame Communication feature for running SCORM content inside sandboxed or cross-origin iframes:

- `CrossFrameLMS(api, origin)` -- Parent frame: validates incoming messages from child
- `CrossFrameAPI(origin, targetWindow)` -- Child frame: proxies API calls to parent via postMessage
- Cache-first shim keeps CMI object state in the child frame for synchronous reads
- Handles `LMSInitialize`/`LMSFinish` lifecycle in the parent

### 2.5 Responsive and Mobile-First Course Design

- Use CSS Grid/Flexbox for adaptive layouts
- Design for touch interaction first (minimum 44px tap targets)
- Implement gesture navigation (swipe between slides)
- Use responsive media queries for content density adjustments
- Test across viewports: phone (320-480px), tablet (768-1024px), desktop (1024px+)
- Consider reduced-motion preferences (`prefers-reduced-motion`)
- Ensure WCAG AA accessibility compliance

### 2.6 Micro-Frontend Approaches for Modular Content

#### Architecture: MACH (Microservice, API-first, Cloud-native, Headless)

```
┌──────────────────────────────────────────────────┐
│                Course Shell (Host)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ Nav/     │ │ Progress │ │ Content Viewport  │  │
│  │ Sidebar  │ │ Tracker  │ │                   │  │
│  │ (MFE 1)  │ │ (MFE 2)  │ │  ┌─────────────┐ │  │
│  │          │ │          │ │  │ Quiz Module │ │  │
│  │          │ │          │ │  │  (MFE 3)    │ │  │
│  │          │ │          │ │  ├─────────────┤ │  │
│  │          │ │          │ │  │ Video Player│ │  │
│  │          │ │          │ │  │  (MFE 4)    │ │  │
│  │          │ │          │ │  ├─────────────┤ │  │
│  │          │ │          │ │  │ Simulation  │ │  │
│  │          │ │          │ │  │  (MFE 5)    │ │  │
│  │          │ │          │ │  └─────────────┘ │  │
│  └──────────┘ └──────────┘ └──────────────────┘  │
└──────────────────────────────────────────────────┘
```

#### Implementation Technologies

| Technology | Best For | Notes |
|-----------|----------|-------|
| **Module Federation (Webpack 5)** | Runtime code sharing, independent deployment | Most mature solution for React micro-frontends |
| **single-spa** | Orchestrating multiple framework SPAs | Framework-agnostic, can mix React/Vue/Angular |
| **Web Components** | Framework-agnostic reusable UI elements | Native browser support, good for content widgets |
| **Import Maps** | Dynamic module resolution | Browser-native, simpler than bundler-based solutions |
| **Piral** | Plugin-based micro-frontends | Good for extensible course platforms |

#### Benefits for Courseware

- Teams can independently develop and deploy content modules (quiz engine, video player, simulation engine)
- Different content types can use different frameworks
- Shared shell handles navigation, progress tracking, and LMS communication
- Content modules are hot-swappable without rebuilding the entire course
- Enables a marketplace/plugin model for course components

---

## 3. LMS Integration Specifics

### 3.1 Platform-Specific Integration Details

#### WorkRamp

- **SCORM Player:** Uses Rustici Software engine
- **Supported Formats:** SCORM 1.2, SCORM 2004 (2nd, 3rd, 4th editions), xAPI, AICC, cmi5
- **Recommended Format:** SCORM 2004 4th Edition
- **Upload Limit:** 1 GB per package
- **Upload Method:** Drag SCORM object tile into the editing pane within a Guide, or use the `[+Create New]` menu
- **Use Cases:** Compliance training (standard SCORM files), self-serve course library
- **Key Detail:** WorkRamp uses SCORM Cloud (Rustici) under the hood, which means content compatibility is excellent

#### Docebo

- **Headless LMS option** available (Docebo Headless Learning)
- Supports SCORM 1.2, SCORM 2004, xAPI
- Content can be embedded within the Docebo learner experience or delivered via APIs
- REST API available for programmatic content management
- Supports content syndication via LTI

#### Cornerstone OnDemand

- Supports SCORM 1.2, SCORM 2004 (3rd Edition), AICC
- Easy import of both SCORM 1.2 and 2004 packages
- Custom content via LTI integrations
- Content player renders SCORM within the platform UI

#### SAP SuccessFactors Learning

- Supports SCORM 1.2, SCORM 2004, AICC
- SCORM content can be published directly from authoring tools like SAP Enable Now
- iContent repository for storing and managing learning objects
- Integration with SAP's broader HXM (Human Experience Management) suite

### 3.2 SCORM Cloud as Testing and Hosting Intermediary

**SCORM Cloud** (by Rustici Software) serves multiple roles:

#### Testing Sandbox
- Upload, preview, and debug course content
- Has tested millions of SCORM, AICC, cmi5, and xAPI courses over 15+ years
- Free tier available for basic testing
- Validates manifest structure, runtime communication, and completion reporting
- Identifies compatibility issues before deploying to a production LMS

#### Hosting Platform
- Host and deliver courses without a full LMS
- ISO 27001 certified
- Runs on AWS with CDN support
- SANS 20 Critical Controls framework for security
- Built-in LRS for xAPI statement storage
- RESTful API for programmatic course management and registration

#### Rustici Engine
- Embeddable SCORM/xAPI/cmi5 player
- Used by LMS vendors (including WorkRamp) to add standards support to their platforms
- Handles the complexity of SCORM sequencing, content packaging parsing, and runtime API provision

### 3.3 Content Hosting Models

| Model | Description | Tracking | Pros | Cons |
|-------|-------------|----------|------|------|
| **LMS-hosted** | SCORM ZIP uploaded directly to LMS | Full SCORM/xAPI tracking | Simplest; all tracking automatic | Limited by LMS player capabilities; file size limits |
| **SCORM Cloud hosted** | Content on SCORM Cloud, launched via LMS integration | Full tracking via dispatch/LTI | Offloads hosting; better player; testing tools | Additional service cost; dependency on Rustici |
| **Self-hosted + LTI** | Content on your servers, integrated via LTI 1.3 | Via LTI AGS (grades) + xAPI (detailed) | Full control over hosting and UX | More infrastructure to manage; LTI setup complexity |
| **Embedded iframe** | Content on CDN, embedded via iframe in LMS page | Limited (requires cross-frame SCORM or xAPI) | Simple deployment; CDN performance | Cross-origin issues; limited LMS integration |
| **Standalone** | Content on any web server, no LMS | None (or xAPI to external LRS) | Maximum flexibility; no LMS dependency | No integration with organizational LMS reporting |

### 3.4 Supporting Both Standalone and LMS-Embedded Modes

```javascript
// Environment detection and adapter selection
function detectEnvironment() {
  // Check for cmi5 launch parameters
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('fetch') && urlParams.has('endpoint')
      && urlParams.has('registration')) {
    return 'cmi5';
  }

  // Check for SCORM 2004 API
  if (findAPI('API_1484_11')) {
    return 'scorm2004';
  }

  // Check for SCORM 1.2 API
  if (findAPI('API')) {
    return 'scorm12';
  }

  // Check for xAPI configuration
  if (window.xAPIConfig || urlParams.has('endpoint')) {
    return 'xapi';
  }

  // Standalone mode -- use localStorage
  return 'standalone';
}

function findAPI(apiName) {
  let win = window;
  let attempts = 0;
  while (!win[apiName] && win.parent !== win && attempts < 10) {
    win = win.parent;
    attempts++;
  }
  if (!win[apiName] && window.opener) {
    win = window.opener;
    attempts = 0;
    while (!win[apiName] && win.parent !== win && attempts < 10) {
      win = win.parent;
      attempts++;
    }
  }
  return win[apiName] || null;
}
```

### 3.5 Tracking and Completion Reporting Across Standards

| Data Point | SCORM 1.2 | SCORM 2004 | xAPI | cmi5 |
|------------|-----------|------------|------|------|
| **Completion** | `cmi.core.lesson_status` = "completed" | `cmi.completion_status` = "completed" | Verb: "completed" | Verb: "completed" (cmi5 defined) |
| **Pass/Fail** | `cmi.core.lesson_status` = "passed"/"failed" | `cmi.success_status` = "passed"/"failed" | Verb: "passed"/"failed" | Verb: "passed"/"failed" (cmi5 defined) |
| **Score** | `cmi.core.score.raw` (0-100) | `cmi.score.scaled` (-1 to 1) | `result.score.scaled` | `result.score.scaled` |
| **Bookmark** | `cmi.core.lesson_location` (255 chars) | `cmi.location` (1000 chars) | Activity State API | Activity State API |
| **Suspend data** | `cmi.suspend_data` (4096 bytes) | `cmi.suspend_data` (64000 chars) | Activity State API (unlimited) | Activity State API |
| **Time spent** | `cmi.core.session_time` | `cmi.session_time` | `result.duration` | `result.duration` |
| **Interactions** | `cmi.interactions.n.*` | `cmi.interactions.n.*` | Individual statements per interaction | Individual statements |

---

## 4. Content Pipeline Architecture

### 4.1 Build Systems for Courseware

#### Recommended: Vite-Based Build Pipeline

```
┌─────────────────────────────────────────────┐
│              Course Source                   │
│  ├── src/                                   │
│  │   ├── components/    (React/Vue/Svelte)  │
│  │   ├── content/       (JSON/MDX/YAML)     │
│  │   ├── interactions/  (Quiz, DnD, Sim)    │
│  │   ├── media/         (images, video)     │
│  │   ├── styles/        (CSS/SCSS)          │
│  │   └── tracking/      (SCORM/xAPI layer)  │
│  ├── vite.config.ts                         │
│  └── package.json                           │
└──────────────┬──────────────────────────────┘
               │ vite build
               ▼
┌─────────────────────────────────────────────┐
│              Build Output                   │
│  ├── dist/                                  │
│  │   ├── index.html                         │
│  │   ├── assets/                            │
│  │   │   ├── index-[hash].js                │
│  │   │   ├── index-[hash].css               │
│  │   │   └── media/                         │
│  │   └── (chunks for lazy-loaded content)   │
└──────────────┬──────────────────────────────┘
               │ post-build packaging
               ▼
┌─────────────────────────────────────────────┐
│           SCORM Package                     │
│  ├── imsmanifest.xml    (generated)         │
│  ├── adlcp_rootv1p2.xsd                    │
│  ├── imscp_rootv1p1p2.xsd                  │
│  ├── imsmd_rootv1p2p1.xsd                  │
│  ├── index.html                             │
│  ├── assets/                                │
│  └── → course.zip                           │
└─────────────────────────────────────────────┘
```

#### Vite Advantages for Courseware

- Fast HMR (Hot Module Replacement) for rapid content iteration
- Native ES modules in development
- Optimized production builds with Rollup
- Built-in support for TypeScript, CSS modules, asset handling
- Plugin ecosystem for custom build steps
- Code splitting for lazy-loaded course sections

#### Webpack Alternative

- Module Federation for micro-frontend course architectures
- More mature plugin ecosystem
- Better for complex multi-entry configurations
- Slower builds than Vite but more configurable

### 4.2 Asset Pipeline: Generate, Optimize, Package

```
Source Assets          Optimization           Package
─────────────         ────────────           ───────
PNG/JPG images   →    sharp/imagemin         →  WebP + fallback
                      (resize, compress)
SVG icons        →    SVGO (optimize)        →  Inline or sprite
Video (MP4)      →    ffmpeg (compress,      →  HLS/DASH or
                      multiple bitrates)        progressive MP4
Audio (WAV)      →    ffmpeg → MP3/AAC       →  Compressed audio
Fonts            →    subset (glyphhanger)   →  WOFF2
Markdown/MDX     →    remark/rehype          →  JSON content data
JSON content     →    validate + transform   →  Optimized JSON
Translations     →    i18n compile           →  Locale bundles
```

#### Optimization Targets

- Images: WebP with PNG/JPG fallback; responsive srcset
- Video: Consider HLS for long-form; progressive MP4 for short clips; poster images
- Total package size: Target < 50MB for LMS upload (many LMS platforms have limits)
- Initial load: Target < 3MB for first meaningful paint
- Code splitting: Lazy-load content sections on navigation

### 4.3 CI/CD for Course Content

```yaml
# Example GitHub Actions workflow for course builds
name: Course Build and Package

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      # Lint and validate content
      - run: npm run lint
      - run: npm run validate-content

      # Run tests (interaction logic, SCORM communication)
      - run: npm run test

      # Build course
      - run: npm run build

      # Generate SCORM manifest
      - run: npm run generate-manifest

      # Package as SCORM ZIP
      - run: npm run package-scorm

      # Validate SCORM package structure
      - run: npm run validate-scorm

      # Upload to SCORM Cloud for automated testing
      - run: npm run test-scorm-cloud
        if: github.ref == 'refs/heads/main'

      # Upload artifact
      - uses: actions/upload-artifact@v4
        with:
          name: course-package-${{ github.sha }}
          path: dist/*.zip

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      # Deploy to CDN for standalone mode
      - run: npm run deploy-cdn

      # Upload to LMS (via SCORM Cloud API or LMS API)
      - run: npm run deploy-lms
```

#### Testing Stages

1. **Unit tests:** Interaction logic, state management, scoring algorithms
2. **Integration tests:** SCORM API communication (using scorm-again in emulation mode)
3. **Visual regression tests:** Screenshot comparison of key screens (Playwright/Puppeteer)
4. **SCORM validation:** Manifest structure, required files, schema conformance
5. **SCORM Cloud testing:** Automated upload and launch test (via Rustici API)
6. **Accessibility testing:** axe-core automated checks + manual review
7. **Cross-browser testing:** Chrome, Firefox, Safari, Edge + mobile browsers

### 4.4 Version Control for Course Content

#### Git-Based Content Management

```
course-repo/
├── .github/
│   └── workflows/        # CI/CD pipelines
├── content/
│   ├── modules/
│   │   ├── module-01/
│   │   │   ├── content.json    # Structured content data
│   │   │   ├── quiz.json       # Assessment questions
│   │   │   └── media/          # Module-specific media
│   │   └── module-02/
│   └── shared/
│       ├── glossary.json
│       └── resources.json
├── src/                  # Application code
├── tests/                # Test suite
├── scripts/
│   ├── build.ts          # Build orchestration
│   ├── package-scorm.ts  # SCORM packaging
│   ├── validate.ts       # Content validation
│   └── deploy.ts         # Deployment scripts
└── package.json
```

**Best Practices:**

- Separate content (JSON/YAML/MDX) from application code -- content authors edit data files, developers maintain the player
- Use JSON Schema to validate content structure on commit (pre-commit hooks)
- Tag releases with semantic versioning (course version, not code version)
- Use branches for content drafts, PRs for review workflows
- Store large media assets in Git LFS or external CDN (reference by URL in content files)
- Generate changelogs from content diffs for stakeholder review

### 4.5 Preview and Review Workflows

```
Content Author         Developer            Reviewer           LMS Admin
     │                     │                    │                  │
     │  Edit content.json  │                    │                  │
     │─────────────────────▶                    │                  │
     │  Push to branch     │                    │                  │
     │─────────────────────▶                    │                  │
     │                     │  CI builds preview │                  │
     │                     │──────────────────▶  │                  │
     │                     │  Deploy to preview  │                  │
     │                     │  environment        │                  │
     │                     │──────────────────▶  │                  │
     │                     │                    │  Review via URL   │
     │                     │                    │◀─────────────────│
     │                     │                    │  Approve PR       │
     │                     │                    │──────────────────▶│
     │                     │  Merge to main     │                  │
     │                     │──────────────────▶  │                  │
     │                     │  CI builds + packages                 │
     │                     │──────────────────────────────────────▶│
     │                     │                    │  Upload to LMS   │
     │                     │                    │──────────────────▶│
```

- **Preview environments:** Deploy each PR to a unique URL (e.g., Vercel preview deployments, Netlify branch deploys)
- **Review mode:** Standalone mode with annotation tools (comments, highlights)
- **A/B testing:** Deploy multiple content variants, track effectiveness via xAPI
- **Rollback:** Tag and archive every SCORM package; re-upload previous version if needed

### 4.6 Monorepo Structure for Course Content

```
courses-monorepo/
├── packages/
│   ├── course-player/           # Shared course player/shell
│   │   ├── src/
│   │   │   ├── components/      # Navigation, progress bar, etc.
│   │   │   ├── tracking/        # SCORM/xAPI adapters
│   │   │   ├── engine/          # Content rendering engine
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   ├── quiz-engine/             # Shared quiz/assessment engine
│   │   ├── src/
│   │   │   ├── question-types/  # MCQ, fill-blank, drag-drop, etc.
│   │   │   ├── scoring/
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   ├── interaction-library/     # Shared interactive components
│   │   ├── src/
│   │   │   ├── hotspot/
│   │   │   ├── timeline/
│   │   │   ├── accordion/
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   ├── scorm-packager/          # SCORM packaging utility
│   │   ├── src/
│   │   │   ├── manifest-generator.ts
│   │   │   ├── zip-builder.ts
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   └── media-pipeline/          # Asset optimization
│       ├── src/
│       │   ├── image-optimizer.ts
│       │   ├── video-processor.ts
│       │   └── index.ts
│       └── package.json
│
├── courses/
│   ├── safety-101/              # Individual course
│   │   ├── content/
│   │   │   ├── modules/
│   │   │   └── assessments/
│   │   ├── media/
│   │   ├── vite.config.ts       # Course-specific build config
│   │   └── package.json         # Depends on shared packages
│   │
│   ├── onboarding-2026/
│   │   ├── content/
│   │   ├── media/
│   │   ├── vite.config.ts
│   │   └── package.json
│   │
│   └── compliance-annual/
│       ├── content/
│       ├── media/
│       ├── vite.config.ts
│       └── package.json
│
├── scripts/
│   ├── build-all.ts             # Build all courses
│   ├── build-changed.ts         # Build only changed courses
│   └── deploy.ts                # Deploy to LMS/CDN
│
├── turbo.json                   # Turborepo config (or nx.json)
├── pnpm-workspace.yaml          # pnpm workspace config
└── package.json
```

**Monorepo Tooling:**

- **Turborepo** or **Nx** for task orchestration, caching, and affected-only builds
- **pnpm workspaces** for dependency management
- Build only courses that changed (based on git diff)
- Shared packages are versioned and tested independently
- Each course produces its own SCORM/xAPI package as a build artifact

---

## 5. Open Source Course Players and Libraries

### 5.1 SCORM API Wrappers and Runtime Libraries

#### scorm-again

- **Repository:** [github.com/jcputney/scorm-again](https://github.com/jcputney/scorm-again)
- **npm:** `scorm-again`
- **Description:** Modern, fully-tested JavaScript runtime for SCORM 1.2 and SCORM 2004
- **Key Features:**
  - LMS-agnostic; can run without a backing LMS (logs calls instead of committing)
  - Cross-Frame Communication (v3.0.0+): Content in sandboxed/cross-origin iframes can communicate with parent SCORM API
  - Core APIs with separate SCORM 1.2 and SCORM 2004 implementations
  - Service layer: HTTP communication, validation, logging, data serialization
  - CMI data models for each SCORM version
  - Comprehensive event system
  - SCORM 2004 sequencing following IMS Simple Sequencing spec
  - TypeScript support
- **Use Cases:**
  - Building custom LMS SCORM players
  - Testing SCORM content outside an LMS
  - Creating SCORM-compatible course shells
  - Wrapping modern web apps for LMS delivery

#### pipwerks SCORM API Wrapper

- **Repository:** [github.com/pipwerks/scorm-api-wrapper](https://github.com/pipwerks/scorm-api-wrapper)
- **Description:** Lightweight abstraction layer between SCORM API and course code
- **Key Features:**
  - Version-agnostic (works with SCORM 1.2 and 2004)
  - Battle-tested in thousands of courses since 2008
  - Simple API: `SCORM.init()`, `SCORM.get(key)`, `SCORM.set(key, value)`, `SCORM.save()`, `SCORM.quit()`
  - Automatic SCORM version detection
  - Error handling and debugging
- **Limitations:**
  - No TypeScript support
  - No modern module format (global script)
  - No active development (stable but not evolving)

#### gamestdio/scorm

- **Repository:** [github.com/gamestdio/scorm](https://github.com/gamestdio/scorm)
- **Description:** SCORM 1.2/2004 wrapper with modern JavaScript/TypeScript support
- **Based on:** pipwerks wrapper, modernized

#### simplify-scorm

- **Repository:** [github.com/gabrieldoty/simplify-scorm](https://github.com/gabrieldoty/simplify-scorm)
- **Description:** SCORM 1.2 and 2004 JavaScript API for quick implementation
- **Features:** Provides both SCORM 1.2 and 2004 runtime APIs; integrates with backend APIs

#### react-scorm-provider

- **npm:** `react-scorm-provider`
- **Repository:** [github.com/S4-NetQuest/react-scorm-provider](https://github.com/S4-NetQuest/react-scorm-provider)
- **Description:** React Context/Provider components for SCORM API communication
- **Note:** Does NOT include packaging; pair with simple-scorm-packager for ZIP output
- **Fork:** `@erik-efl/react-scorm-provider` -- Modernized with React hooks and current TypeScript

### 5.2 xAPI JavaScript Libraries

#### ADL xAPIWrapper

- **Repository:** [github.com/adlnet/xAPIWrapper](https://github.com/adlnet/xAPIWrapper)
- **npm:** `adl-xapiwrapper`
- **Description:** Official ADL wrapper to simplify LRS communication
- **Key Features:**
  - Statement constructors: `new ADL.XAPIStatement(actor, verb, object)`
  - Agent, Verb, Activity builders
  - `sendStatement()` and `sendStatements()` for single/batch submission
  - State API, Activity Profile API, Agent Profile API support
  - Configurable LRS endpoint, authentication

#### xAPI.js

- **Website:** [xapijs.dev](https://www.xapijs.dev)
- **Description:** Strongly typed JavaScript libraries for xAPI protocol
- **Key Features:**
  - Fully compliant with ADL specifications
  - TypeScript-first design
  - Modular: separate packages for statements, state, profiles
  - Modern async/await API

#### ADL xAPIVerbs

- **Repository:** [github.com/adlnet-archive/xAPIVerbs](https://github.com/adlnet-archive/xAPIVerbs)
- **Description:** Predefined verb constants (experienced, passed, imported, launched, etc.)
- **Usage:** Include in project for consistent verb IRI references

#### SCORM-to-xAPI-Wrapper

- **Repository:** [github.com/adlnet/SCORM-to-xAPI-Wrapper](https://github.com/adlnet/SCORM-to-xAPI-Wrapper)
- **Description:** Drop-in replacement for the SCORM APIWrapper.js that also sends xAPI statements
- **Use Case:** Bridge existing SCORM content to xAPI tracking without rewriting

### 5.3 SCORM Packaging Tools

#### simple-scorm-packager

- **npm:** `simple-scorm-packager`
- **Repository:** [github.com/lmihaidaniel/simple-scorm-packager](https://github.com/lmihaidaniel/simple-scorm-packager)
- **Description:** Creates SCORM packages from source directories
- **Configuration:**
  ```javascript
  const scopackager = require('simple-scorm-packager');

  scopackager({
    version: '2004 4th Edition',
    organization: 'My Organization',
    title: 'Course Title',
    language: 'en-US',
    identifier: '00',
    masteryScore: 80,
    startingPage: 'index.html',
    source: './dist',
    package: {
      zip: true,
      outputFolder: './scorm-packages',
      appendTimeToOutput: true
    }
  });
  ```
- **Status:** Maintenance mode (~150 downloads/week)
- **Integration:** Add as npm script: `"package-scorm": "node scoPackager.js"`

#### create-react-scorm-app

- **Repository:** [github.com/simondate/create-react-scorm-app](https://github.com/simondate/create-react-scorm-app)
- **Description:** Scaffold for React-based SCORM courses
- **Workflow:** `npm run build` creates build directory; zip contents for LMS upload

### 5.4 Open Source Course Frameworks

#### Adapt Framework

- **Website:** [adaptlearning.org](https://www.adaptlearning.org/)
- **Repository:** [github.com/adaptlearning/adapt_framework](https://github.com/adaptlearning/adapt_framework)
- **License:** GNU GPL
- **Description:** Toolkit for creating responsive, accessible, multilanguage HTML5 eLearning courses
- **Key Features:**
  - Responsive/mobile-first by design (not a slide metaphor -- embraces web scrolling)
  - WCAG AA accessibility out of the box
  - SCORM 1.2 and 2004 support built in
  - Plugin architecture: extensions, components, themes, menus
  - JSON-based content model
  - Deep scrolling, one-page course layout
  - Companion authoring tool (Adapt Authoring Tool) -- web-based GUI
- **Architecture:**
  - Backbone.js-based (older but stable)
  - Handlebars templates
  - Grunt build system
  - Plugin registry for community components
- **Best For:** Organizations wanting a complete open-source course authoring and delivery solution

#### H5P

- **Website:** h5p.org
- **Description:** Open source framework for creating, sharing, and reusing interactive HTML5 content
- **Integration:** Works within Moodle, WordPress, Drupal; also available as standalone and in Wellms (headless)
- **Content Types:** 50+ interaction types (interactive video, course presentation, drag-and-drop, branching scenario, etc.)
- **Relevance:** Can be embedded within SCORM packages or used as micro-content within a larger course framework

### 5.5 Open Source Learning Record Stores

#### Learning Locker

- **Repository:** [github.com/LearningLocker](https://github.com/LearningLocker)
- **Description:** World's most installed xAPI-ready LRS
- **License:** Open source (community edition)
- **Key Features:**
  - Full xAPI conformance
  - Statement forwarding
  - Dashboard and visualization tools
  - Role-based access control
  - Webhooks for event-driven integrations
- **Awards:** Innovation Award from the Queen's Awards for Enterprise

#### SQL LRS

- **Website:** [sqllrs.com](https://www.sqllrs.com/)
- **License:** Apache 2.0
- **Description:** Open source xAPI LRS with onboard conditional logic
- **Key Features:**
  - Deploys to Windows, Linux, macOS
  - Docker containerized version available
  - Built-in conditional logic and internal xAPI statement generation
  - No external LRS hosting required

### 5.6 Course Navigation and Progress Tracking Implementation

#### Navigation Patterns

```javascript
// Example: SPA course navigation with state management
class CourseNavigator {
  constructor(courseStructure, tracker) {
    this.structure = courseStructure;  // Tree of modules/pages
    this.tracker = tracker;           // SCORM/xAPI adapter
    this.currentIndex = 0;
    this.visited = new Set();
    this.completed = new Set();
  }

  navigate(pageId) {
    this.visited.add(pageId);
    this.currentIndex = this.findIndex(pageId);
    this.tracker.saveBookmark(pageId);
    this.tracker.saveSuspendData(this.serialize());
    this.updateProgress();
    return this.getPage(pageId);
  }

  next() {
    const nextPage = this.structure[this.currentIndex + 1];
    if (nextPage) return this.navigate(nextPage.id);
    return null;
  }

  previous() {
    const prevPage = this.structure[this.currentIndex - 1];
    if (prevPage) return this.navigate(prevPage.id);
    return null;
  }

  markComplete(pageId) {
    this.completed.add(pageId);
    this.updateProgress();
  }

  updateProgress() {
    const progress = this.completed.size / this.structure.length;
    this.tracker.reportProgress(progress);
    if (progress >= 1.0) {
      this.tracker.reportCompletion();
    }
  }

  serialize() {
    return JSON.stringify({
      visited: [...this.visited],
      completed: [...this.completed],
      currentIndex: this.currentIndex
    });
  }

  restore(suspendData) {
    if (!suspendData) return;
    const data = JSON.parse(suspendData);
    this.visited = new Set(data.visited);
    this.completed = new Set(data.completed);
    this.currentIndex = data.currentIndex;
  }
}
```

#### Bookmark and Resume Implementation

1. **On course launch:**
   - Call `LMSInitialize()` / `Initialize("")`
   - Check `cmi.core.entry` / `cmi.entry` -- if "resume", retrieve bookmark
   - Read `cmi.core.lesson_location` / `cmi.location` for bookmark
   - Read `cmi.suspend_data` for full state
   - Prompt user: "Resume where you left off?" or auto-resume

2. **During course:**
   - Update `cmi.core.lesson_location` on each page navigation
   - Serialize full state to `cmi.suspend_data` periodically and on page change
   - Call `LMSCommit()` / `Commit("")` to persist to LMS

3. **On course exit:**
   - Set `cmi.core.exit` = "suspend" (to preserve attempt for resume)
   - Commit final state
   - Call `LMSFinish()` / `Terminate("")`

4. **Suspend data compression (for SCORM 1.2's 4096-byte limit):**
   - Use LZ-string or similar compression
   - Store only essential delta state
   - Consider bitfield encoding for boolean states (page visited flags)

---

## 6. Recommendations and Architectural Decision Guide

### For New Course Development (2026+)

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| **Primary standard** | SCORM 2004 4th Edition with xAPI dual-output | Maximum LMS compatibility + rich analytics |
| **Future-proof standard** | cmi5 | Best of both worlds, but LMS adoption still growing |
| **Build tool** | Vite | Fast builds, excellent DX, modern defaults |
| **Framework** | React or Svelte | Component model suits courseware; large ecosystem |
| **State management** | Zustand or Jotai (React) | Lightweight, perfect for course state |
| **SCORM library** | scorm-again | Modern, tested, TypeScript, cross-frame support |
| **xAPI library** | xAPI.js | TypeScript-first, spec-compliant |
| **Packaging** | Custom Vite plugin or simple-scorm-packager | Automate manifest generation in build pipeline |
| **Testing** | Vitest + Playwright + SCORM Cloud API | Unit + E2E + standards conformance |
| **Monorepo** | Turborepo + pnpm workspaces | Fast, cached builds across many courses |
| **CI/CD** | GitHub Actions | Preview deploys, SCORM validation, automated testing |
| **LRS** | Learning Locker (self-hosted) or SCORM Cloud LRS | Depends on scale and budget |

### Architecture Decision Record: Standalone + LMS Dual-Mode

For maximum reach, build courses that work in both modes:

1. **Core application** is a standalone SPA that works without any LMS
2. **Tracking adapter layer** auto-detects the environment and connects to available APIs
3. **Standalone mode** uses localStorage for progress persistence
4. **LMS mode** uses SCORM/xAPI for tracking and reporting
5. **Build pipeline** produces multiple outputs:
   - SCORM 1.2 ZIP (legacy compatibility)
   - SCORM 2004 ZIP (recommended for most LMS platforms)
   - cmi5 ZIP (forward-looking)
   - Static site bundle (standalone/CDN deployment)

---

## 7. Sources

### SCORM and xAPI Standards
- [SCORM vs xAPI vs LTI - Mindsmith](https://www.mindsmith.ai/blog/scorm-vs-xapi-vs-lti-understanding-elearning-standards-and-compatibility)
- [SCORM vs xAPI vs cmi5 - CommLab India](https://www.commlabindia.com/blog/scorm-vs-xapi-cmi5-elearning-standards)
- [xAPI vs SCORM Comparison Guide 2026 - iSpring](https://www.ispringsolutions.com/blog/xapi-vs-scorm)
- [SCORM Versions - scorm.com](https://scorm.com/scorm-explained/business-of-scorm/scorm-versions/)
- [Technical Overview of SCORM - scorm.com](https://scorm.com/scorm-explained/technical-scorm/)
- [SCORM 2004 Manifest Structure - scorm.com](https://scorm.com/scorm-explained/technical-scorm/content-packaging/manifest-structure/)
- [SCORM Content Packaging - scorm.com](https://scorm.com/scorm-explained/technical-scorm/content-packaging/)
- [SCORM Run-Time Reference Chart - scorm.com](https://scorm.com/scorm-explained/technical-scorm/run-time/run-time-reference/)
- [SCORM Run-Time Environment - scorm.com](https://scorm.com/scorm-explained/technical-scorm/run-time/)
- [SCORM 2004 Sequencing and Navigation - scorm.com](https://scorm.com/scorm-explained/technical-scorm/sequencing/)
- [SCORM 2004 Overview for Developers - scorm.com](https://scorm.com/scorm-explained/technical-scorm/scorm-2004-overview-for-developers/)
- [SCORM 1.2 Overview for Developers - scorm.com](https://scorm.com/scorm-explained/technical-scorm/scorm-12-overview-for-developers/)
- [Packaging a SCORM Course - pipwerks](https://pipwerks.com/packaging-a-scorm-course/)
- [SCORM Manifests - pipwerks GitHub](https://github.com/pipwerks/SCORM-Manifests)

### xAPI and LRS
- [xAPI Overview - xapi.com](https://xapi.com/overview/)
- [xAPI Statements 101 - xapi.com](https://xapi.com/statements-101/)
- [xAPI Specification - ADL GitHub](https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md)
- [How to Write an xAPI Statement - Devlin Peck](https://www.devlinpeck.com/content/write-xapi-statement)
- [What is xAPI - iSpring](https://www.ispringsolutions.com/blog/what-is-xapi)
- [Learning Record Store Comparison 2026 - ProProfs](https://www.proprofstraining.com/blog/learning-record-store-lrs/)
- [Learning Locker - GitHub](https://github.com/LearningLocker)
- [SQL LRS](https://www.sqllrs.com/)
- [Yet Analytics - Open Source xAPI](https://www.yetanalytics.com/articles/opensourcetla)

### cmi5
- [cmi5 Overview - xapi.com](https://xapi.com/cmi5/)
- [cmi5 Technical Overview - xapi.com](https://xapi.com/cmi5/technical/)
- [cmi5 Technical 101 - xapi.com](https://xapi.com/cmi5/cmi5-technical-101/)
- [cmi5 Specification - AICC GitHub](https://github.com/AICC/cmi-5_Spec_Current/blob/quartz/cmi5_spec.md)
- [cmi5 Explained - Easygenerator](https://www.easygenerator.com/en/blog/results-tracking/cmi5-what-it-is-and-why-you-need-it/)

### LTI 1.3
- [LTI 1.3 Specification - 1EdTech](https://www.imsglobal.org/spec/lti/v1p3)
- [LTI Standards - 1EdTech](https://www.1edtech.org/standards/lti)
- [Introduction to LTI 1.3 - Voxy Engineering](https://medium.com/voxy-engineering/introduction-to-lti-1-3-270f17505d75)
- [LTI 1.3 Implementation Guide - 1EdTech](https://www.imsglobal.org/spec/lti/v1p3/impl/)
- [LTI 1.3 Tool Implementation Guide - Blackboard](https://blackboard.github.io/lti/tutorials/implementation-guide)

### Headless LMS and Architecture
- [Headless LMS Architecture Guide - LMSMore](https://www.lmsmore.com/blog/headless-lms-architecture)
- [Headless LMS Explained - Yojji](https://yojji.io/blog/headless-lms)
- [Docebo Headless Learning](https://www.docebo.com/products/headless-learning/)
- [Wellms Documentation](https://docs.wellms.io/)
- [Wellms GitHub](https://github.com/EscolaLMS)
- [Wellms Architecture](https://escolalms.github.io/c4-software-architecture/master/)
- [E-learning Platform Architecture - Hygraph](https://hygraph.com/blog/elearning-platform-architecture)

### LMS Platforms
- [SCORM Files in WorkRamp](https://help.workramp.com/en/articles/2421835-scorm-files-in-workramp)
- [WorkRamp SCORM Best Practices](https://help.workramp.com/en/articles/3691735-best-practices-for-using-scorm-with-workramp)
- [WorkRamp uses SCORM Cloud - Rustici](https://rusticisoftware.com/blog/customer-chat-workramp-uses-scorm-cloud-to-make-standards-simple/)
- [SCORM Cloud - Rustici Software](https://rusticisoftware.com/products/scorm-cloud/)
- [SCORM Cloud Testing](https://rusticisoftware.com/resources/test-scorm/)
- [Rustici Engine](https://rusticisoftware.com/products/rustici-engine/)
- [SCORM Hosting Options - iSpring](https://www.ispringsolutions.com/blog/scorm-hosting)

### SCORM Libraries and Tools
- [scorm-again - GitHub](https://github.com/jcputney/scorm-again)
- [scorm-again - npm](https://www.npmjs.com/package/scorm-again)
- [pipwerks SCORM API Wrapper - GitHub](https://github.com/pipwerks/scorm-api-wrapper)
- [react-scorm-provider - npm](https://www.npmjs.com/package/react-scorm-provider)
- [simple-scorm-packager - npm](https://www.npmjs.com/package/simple-scorm-packager)
- [create-react-scorm-app - GitHub](https://github.com/simondate/create-react-scorm-app)
- [ADL xAPIWrapper - GitHub](https://github.com/adlnet/xAPIWrapper)
- [xAPI.js](https://www.xapijs.dev)
- [SCORM-to-xAPI-Wrapper - ADL GitHub](https://github.com/adlnet/SCORM-to-xAPI-Wrapper)

### Course Frameworks
- [Adapt Learning](https://www.adaptlearning.org/)
- [Adapt Framework - GitHub](https://github.com/adaptlearning/adapt_framework)
- [Micro Frontends - Martin Fowler](https://martinfowler.com/articles/micro-frontends.html)
- [Micro-Frontend Architecture Handbook - freeCodeCamp](https://www.freecodecamp.org/news/complete-micro-frontends-guide/)
- [Micro Frontend Architecture - Nx](https://nx.dev/docs/technologies/module-federation/concepts/micro-frontend-architecture)

### Bookmarking and Suspend Data
- [Bookmarking and Suspend Data Limitations - Rustici](https://support.scorm.com/hc/en-us/articles/206167396-Bookmarking-and-Suspend-Data-Limitations)
- [SCORM Explained for Content Authors - iSpring](https://www.ispringsolutions.com/articles/scorm-structure-and-interaction-with-an-lms)
- [Getting Started with SCORM Tracking - eLearning Industry](https://elearningindustry.com/getting-started-with-scorm-tracking-course-specific-data)

### PWA and Offline
- [PWA Going Offline - Google Developers](https://developers.google.com/codelabs/pwa-training/pwa03--going-offline)
- [Offline Service Workers - MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Tutorials/js13kGames/Offline_Service_workers)
- [Learn PWA - web.dev](https://web.dev/learn/pwa/)
