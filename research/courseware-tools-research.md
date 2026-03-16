# Interactive Courseware & E-Learning Tools: Comprehensive Research

**Date:** March 2026
**Scope:** Open source and developer-friendly tools for creating interactive online courseware/e-learning content

---

## Table of Contents

1. [SCORM/xAPI/cmi5 Authoring Tools](#1-scormxapicmi5-authoring-tools)
2. [Modern Web-Based Interactive Content Frameworks](#2-modern-web-based-interactive-content-frameworks)
3. [AI-Powered Course Creation Tools](#3-ai-powered-course-creation-tools)
4. [Multimedia Integration](#4-multimedia-integration)
5. [Standards and Packaging](#5-standards-and-packaging)
6. [Summary Comparison Tables](#6-summary-comparison-tables)

---

## 1. SCORM/xAPI/cmi5 Authoring Tools

### 1.1 Adapt Learning Framework

| Field | Details |
|-------|---------|
| **URL** | https://www.adaptlearning.org/ |
| **Repo** | https://github.com/adaptlearning/adapt_framework |
| **GitHub Stars** | 618 |
| **License** | GPL v3 |
| **Latest Release** | v5.55.2 (January 15, 2026) |
| **Language** | JavaScript (100%) |
| **Last Updated** | February 2026 (active) |

**Key Features:**
- Creates fully responsive, multi-device HTML5 e-learning courses
- SCORM 1.2 and SCORM 2004 support via the `adapt-contrib-spoor` plugin
- xAPI export capabilities
- 23 bundled plugins with extensive community plugin ecosystem
- Accessibility compliance (WCAG 2.1 AA)
- Multi-language/localization support
- Separate authoring tool (web-based GUI) for non-technical users

**Strengths:**
- Most mature open-source SCORM authoring solution available
- Active community with 367 releases and 3,092 commits
- Both framework (developer CLI) and authoring tool (web GUI) available
- Well-documented plugin architecture for extensibility
- Strong responsive design system

**Limitations:**
- Steep learning curve for the framework (CLI) approach
- Authoring tool can be complex to set up (Node.js + MongoDB)
- Some users report SCORM tracking issues with certain LMS platforms
- The authoring tool UI feels dated compared to commercial tools
- Limited native xAPI support (community plugins needed for advanced tracking)

**Agent-Driven Content Creation:**
- The framework uses JSON configuration files that define course structure, making it feasible to programmatically generate courses
- Course content is defined in `components.json`, `blocks.json`, `articles.json`, and `contentObjects.json` files
- No official REST API for the authoring tool, but the JSON-based structure enables agent-driven generation by producing config files and running the CLI build process
- **Verdict: Good candidate for agent-driven creation** via JSON generation + CLI

---

### 1.2 H5P (HTML5 Package)

| Field | Details |
|-------|---------|
| **URL** | https://h5p.org/ |
| **Repo** | https://github.com/h5p/h5p-php-library |
| **GitHub Stars** | 139 (core library) |
| **License** | GPL v3 |
| **Last Updated** | February 2026 (active) |
| **Language** | PHP (41%), JavaScript (39%), CSS (20%) |

**Key Features:**
- 50+ interactive content types (Interactive Video, Course Presentation, Branching Scenario, Interactive Book, Quiz types, Drag and Drop, etc.)
- Integrates as plugins into WordPress, Moodle, Drupal, and other CMS/LMS platforms
- OER Hub (launched January 2026) for sharing open educational resources
- Built-in xAPI statement emission for all content types
- SCORM packaging available via community wrapper tools (e.g., `scorm-h5p-wrapper`)
- Content types are modular and reusable across platforms
- February 2026 update: modern layouts, better typography, accessibility improvements

**Strengths:**
- Largest ecosystem of interactive content types in the open-source space
- Extremely accessible for non-technical content creators
- Active development with regular accessibility and UX improvements
- Broad platform integration (WordPress, Moodle, Drupal, Canvas, Brightspace)
- OER Hub enables easy content sharing and discovery
- Strong community with thousands of users worldwide

**Limitations:**
- SCORM export is not native; requires third-party wrappers
- Content types are somewhat constrained to predefined templates
- Heavily dependent on host platform (WordPress, Moodle, etc.)
- Limited programmatic content creation API in standard deployments
- Can be resource-intensive when many content types are loaded

**Agent-Driven Content Creation:**
- **EscolaLMS Headless H5P** (https://github.com/EscolaLMS/H5P) provides a REST API for H5P
  - MIT license, 27 GitHub stars, Laravel-based
  - Full CRUD operations for H5P content and libraries via REST API
  - The only package that renders H5P headlessly (no server-side templates)
  - Tightly coupled to the Escola LMS ecosystem
- The `h5p-cli-creator` tool allows command-line creation of H5P content
- H5P content is JSON-structured internally, making programmatic generation possible
- **Verdict: Good candidate with headless API** (via EscolaLMS) or JSON generation

---

### 1.3 Xerte Online Toolkits

| Field | Details |
|-------|---------|
| **URL** | https://xerte.org.uk/ |
| **Repo** | https://github.com/thexerteproject/xerteonlinetoolkits |
| **GitHub Stars** | 68 |
| **License** | Apache 2.0 |
| **Latest Release** | v3.13 (October 31, 2024); AI release v3.15 (December 31, 2025) |
| **Language** | JavaScript (50%), PHP (18%), HTML (12%), SCSS (8%) |
| **Last Updated** | Active (10,437 commits) |

**Key Features:**
- Browser-based authoring with no software installation needed
- Responsive HTML5 content delivery across all devices
- SCORM export for LMS integration
- New in v3.15: Generative AI integration for content creation
- Chapter feature (v3.14) for organizing content into logical blocks
- Strong accessibility focus (originated at University of Nottingham)
- Part of the Apereo Foundation since 2015

**Strengths:**
- Very accessible for non-technical users
- Long history (since 2004) with stable, mature codebase
- AI integration in latest release is forward-looking
- No license costs (fully open source)
- Strong institutional backing from universities

**Limitations:**
- Smaller community compared to Adapt or H5P
- Requires PHP + MySQL server setup
- UI/UX is functional but not modern
- Limited xAPI support compared to newer standards
- Documentation can be sparse for advanced customization

**Agent-Driven Content Creation:**
- Content is stored in XML format, which can be programmatically generated
- Server-based architecture allows for API integration in principle
- AI features in v3.15 suggest growing automation capabilities
- **Verdict: Moderate potential** -- XML-based structure is parseable but less developer-friendly than JSON

---

### 1.4 Open edX Studio

| Field | Details |
|-------|---------|
| **URL** | https://openedx.org/ |
| **Repo** | https://github.com/openedx/openedx-platform |
| **License** | AGPL v3 |
| **Last Updated** | Actively maintained (2026 conference planned) |
| **Language** | Python (Django), React (frontend-app-authoring) |

**Key Features:**
- Full course authoring environment with content libraries
- Supports video, text, problems, discussions, and custom XBlocks
- AI Course Creator plugin (v2, by Blend-ed): LLM-powered course generation from YouTube videos, PDFs, and documentation
- Content libraries for reusable randomized assignments
- LTI 1.3 provider and consumer support
- Comprehensive grading and assessment engine
- Mobile app support

**Strengths:**
- Most comprehensive open-source LMS + authoring platform
- Powers major MOOCs (edX, institutional deployments worldwide)
- AI Course Creator generates full course structures from source materials
- Robust assessment engine with auto-grading
- Strong LTI integration for embedding external tools
- Active community with annual conferences

**Limitations:**
- Very complex to self-host (requires significant DevOps resources)
- Heavy system requirements (Django + Celery + MongoDB + MySQL + Elasticsearch)
- Not primarily a SCORM authoring tool (focused on native Open edX delivery)
- Course export format is `.tar.gz` (not standard SCORM packages)
- Steep learning curve for course development

**Agent-Driven Content Creation:**
- Rich REST API for course management and content operations
- AI Course Creator plugin demonstrates LLM integration for automated course generation
- XBlock architecture allows custom interactive components
- OLX (Open Learning XML) format can be programmatically generated
- **Verdict: Strong candidate** with REST APIs, AI plugins, and extensible architecture

---

### 1.5 Open eLearning

| Field | Details |
|-------|---------|
| **URL** | https://www.openelearning.org/ |
| **Repo** | https://github.com/open-elearning/core |
| **GitHub Stars** | 5 |
| **License** | GPL v3 |
| **Language** | JavaScript (75%), CSS (24%) -- Electron-based |
| **Last Updated** | Low activity |

**Key Features:**
- Desktop application (Electron) for course and educational game creation
- SCORM export for LMS integration (Moodle, Chamilo, Claroline)
- Plugin/extensions architecture
- Visual development workspace with templates
- Cross-platform (Windows, macOS, Linux)

**Strengths:**
- Simple to install and use as a desktop app
- No internet connection required
- Free and open source

**Limitations:**
- Very small community (5 GitHub stars)
- Electron 8.x is significantly outdated
- Limited content types compared to H5P or Adapt
- No API for programmatic content creation
- Unclear maintenance status

**Agent-Driven Content Creation:**
- Not suitable. Desktop-only with no API or headless mode.
- **Verdict: Not recommended** for agent-driven workflows

---

### 1.6 CogniSpark AI

| Field | Details |
|-------|---------|
| **URL** | https://www.cognispark.ai/ |
| **Repo** | https://github.com/cognisparkai/moodle-local_authoringtool (Moodle plugin) |
| **License** | Proprietary (free tier available) |
| **Last Updated** | 2025 (active) |

**Key Features:**
- AI-powered content generation from PowerPoint, PDF, video, or documents
- Generates complete courses with 50+ slides, voiceovers, and interactive elements
- SCORM/xAPI compliance for LMS integration
- Moodle plugin for direct integration
- 75+ language support with AI translation
- 24/7 AI tutor support
- Enterprise features available

**Strengths:**
- Fastest path from source material to SCORM course
- AI generates entire courses in minutes
- Multi-language support
- Moodle integration via official plugin

**Limitations:**
- Not fully open source (free tier with limitations)
- Dependent on external AI services
- Limited customization compared to framework-based tools
- Quality of AI-generated content may need human review

**Agent-Driven Content Creation:**
- The Moodle plugin suggests some API integration capability
- AI-first design makes it naturally suited for automated workflows
- **Verdict: Moderate** -- API access unclear, but AI-native design is promising

---

### 1.7 Compozer

| Field | Details |
|-------|---------|
| **URL** | https://www.compozer.com/ |
| **License** | Proprietary (freemium) |
| **Last Updated** | 2026 (active) |

**Key Features:**
- Cloud-based authoring with 100+ templates
- SCORM 1.2, SCORM 2004, xAPI, and cmi5 export
- Team collaboration and real-time feedback
- Responsive, mobile-optimized output
- Quiz and assessment creation

**Strengths:**
- Supports all four major e-learning standards (SCORM 1.2/2004, xAPI, cmi5)
- Cloud-based with no installation
- Good template library

**Limitations:**
- Not open source
- Free tier limited to one course
- No quiz/branding in free version
- No public API for automation

**Agent-Driven Content Creation:**
- No known public API
- **Verdict: Not suitable** for agent-driven creation

---

## 2. Modern Web-Based Interactive Content Frameworks

### 2.1 Presentation Frameworks

#### 2.1.1 Reveal.js

| Field | Details |
|-------|---------|
| **URL** | https://revealjs.com/ |
| **Repo** | https://github.com/hakimel/reveal.js |
| **GitHub Stars** | 70,700 |
| **License** | MIT |
| **Latest Release** | v6.0.0 (March 11, 2026) |
| **Language** | JavaScript |

**Key Features:**
- HTML presentation framework with nested slides
- Markdown content support
- Auto-Animate transitions between slides
- PDF export and speaker notes
- LaTeX typesetting and syntax-highlighted code
- Extensive JavaScript API
- Plugin ecosystem (menu, toolbar, animations, remote control)
- Used by ~787,000 dependent projects

**Courseware Potential:**
- Excellent foundation for slide-based courseware
- Plugin architecture allows adding quizzes, progress tracking
- Markdown support enables content-first authoring
- Could be extended with SCORM wrapper for LMS tracking
- JavaScript API enables interactive elements

**Agent-Driven Content Creation:**
- Markdown or HTML content can be trivially generated programmatically
- Well-documented API for customization
- Plugin system allows adding tracking/assessment
- **Verdict: Excellent candidate** -- simple content format, powerful API

---

#### 2.1.2 Slidev

| Field | Details |
|-------|---------|
| **URL** | https://sli.dev/ |
| **Repo** | https://github.com/slidevjs/slidev |
| **GitHub Stars** | 44,900 |
| **License** | MIT |
| **Latest Release** | v52.14.1 (March 3, 2026) |
| **Language** | TypeScript/Vue 3 |

**Key Features:**
- Markdown-based slide authoring for developers
- Vue 3 component integration for interactive slides
- Built-in Monaco Editor for live coding demos
- Mermaid diagrams, LaTeX math, drawing/annotations
- Presenter mode with phone remote control
- Export to PDF, PNG, PPTX, or SPA
- Vite-powered with instant HMR
- Recording and camera view capabilities
- LLMQuery plugin for embedding LLM queries in presentations

**Courseware Potential:**
- Vue component system enables rich interactive elements
- Live coding capability perfect for programming courses
- Mermaid diagrams for technical content
- Could be extended with assessment components
- SPA export mode works for web-based delivery

**Agent-Driven Content Creation:**
- Markdown content is trivially generated
- Vue components can be templated
- CLI-driven build process
- **Verdict: Excellent candidate** -- Markdown + Vue components are easy to generate

---

#### 2.1.3 Quarto

| Field | Details |
|-------|---------|
| **URL** | https://quarto.org/ |
| **License** | GPL v2 |
| **Last Updated** | Active (Quarto Wizard 1.0.0, October 2025) |
| **Language** | Multi-language (R, Python, Julia, Observable JS) |

**Key Features:**
- Scientific and technical publishing system (next-gen R Markdown)
- Output formats: HTML, PDF, Word, ePub, presentations (Reveal.js), websites, books
- Embeds interactive widgets (Jupyter Widgets, htmlwidgets, Observable JS, Shiny)
- Code execution with output embedding (Python, R, Julia)
- Cross-references, citations, and academic formatting
- Extension system with Quarto Wizard for management

**Courseware Potential:**
- Ideal for data science and technical courses
- Interactive computation embedded in content
- Multi-format output (web, PDF, slides)
- Can produce Reveal.js presentations with interactive code

**Agent-Driven Content Creation:**
- Markdown/Quarto markdown is easily generated
- CLI-driven rendering pipeline
- **Verdict: Good candidate** for technical/data science courseware

---

### 2.2 Interactive Coding Environments

#### 2.2.1 Sandpack (by CodeSandbox)

| Field | Details |
|-------|---------|
| **URL** | https://sandpack.codesandbox.io/ |
| **Repo** | https://github.com/codesandbox/sandpack |
| **GitHub Stars** | 6,100 |
| **License** | Apache 2.0 |
| **Latest Release** | v2.20.0 (February 2025) |
| **Language** | TypeScript (84%) |

**Key Features:**
- React component toolkit for live-running code editors
- Three packages: sandpack-client (framework-agnostic), sandpack-react, sandpack-themes
- Built-in support for Next.js, Remix, Vite, Astro
- Nodebox runtime for server-side code in browser
- Themeable editor with syntax highlighting, file explorer, debug tools
- Hot module reloading and npm dependency support
- React 19 compatible

**Courseware Potential:**
- Perfect for embedding interactive code playgrounds in courses
- Learners can edit and run code directly in the browser
- Supports full-stack applications (frontend + Nodebox backend)
- Easily embedded in any React-based courseware

**Agent-Driven Content Creation:**
- React components are programmatically configurable
- Code examples can be templated and injected
- **Verdict: Excellent embedding tool** for interactive coding in courseware

---

#### 2.2.2 StackBlitz WebContainers

| Field | Details |
|-------|---------|
| **URL** | https://webcontainers.io/ |
| **Repo** | https://github.com/stackblitz/webcontainer-core |
| **License** | Proprietary (free for open source; commercial license required for production) |
| **Last Updated** | Active (2025) |

**Key Features:**
- Full Node.js runtime in the browser via WebAssembly
- Boot complete dev environments in milliseconds
- Run package managers, build tools, and full-stack frameworks client-side
- No server infrastructure required
- Programmatic API for filesystem operations, process management

**Courseware Potential:**
- Full-stack coding environments for programming tutorials
- Zero-setup student experience (everything runs in browser)
- Interactive documentation and employee onboarding
- Can run complex build toolchains (webpack, vite, etc.)

**Limitations:**
- Commercial license required for production use in for-profit settings
- Limited to Node.js ecosystem
- Browser compatibility requirements (modern browsers only)

**Agent-Driven Content Creation:**
- Programmatic API for booting containers, populating filesystems, starting servers
- **Verdict: Excellent** for automated coding environment provisioning

---

### 2.3 Interactive Notebooks

#### 2.3.1 Marimo

| Field | Details |
|-------|---------|
| **URL** | https://marimo.io/ |
| **Repo** | https://github.com/marimo-team/marimo |
| **GitHub Stars** | 19,700 |
| **License** | Apache 2.0 |
| **Latest Release** | v0.20.3 (March 3, 2026) |
| **Language** | Python |

**Key Features:**
- Reactive Python notebook (cells auto-update when dependencies change)
- Stored as pure Python `.py` files (Git-friendly)
- Interactive UI elements (sliders, tables, plots) bound to Python without callbacks
- SQL integration for querying dataframes and databases
- AI-native editor with GitHub Copilot support
- Deploy as web apps, execute as scripts, or run in browser via WASM
- Dedicated educational initiatives with curated courses (linear algebra, probability, ML)
- molab: free cloud hosting for notebooks

**Courseware Potential:**
- Purpose-built for education with dedicated educator resources
- Reactive execution provides immediate feedback for learners
- Pure Python storage means easy version control and collaboration
- WebAssembly deployment means zero-install student experience
- Custom widgets via `anywidget` for specialized learning tools

**Agent-Driven Content Creation:**
- Notebooks are pure Python files -- trivially generated by LLMs
- CLI and VS Code extension for local development
- Can be deployed as web apps automatically
- **Verdict: Excellent candidate** -- Python files are ideal for LLM generation

---

#### 2.3.2 JupyterLite

| Field | Details |
|-------|---------|
| **URL** | https://jupyter.org/try-jupyter/lab/index.html |
| **Repo** | https://github.com/jupyterlite/jupyterlite |
| **GitHub Stars** | 4,800 |
| **License** | BSD-3-Clause |
| **Latest Release** | v0.7.4 (March 12, 2026) |
| **Language** | TypeScript/Python |

**Key Features:**
- Full Jupyter distribution running entirely in the browser via WASM
- Python kernels via Pyodide or Xeus Python in Web Workers
- Supports altair, bqplot, ipywidgets, matplotlib, plotly
- No server required; deploys as static files on any web host
- Dual interface: JupyterLab and Jupyter Notebook
- Reuses existing JupyterLab extensions
- Local storage via IndexDB or localStorage

**Courseware Potential:**
- Instant zero-install Python environment for students
- Static deployment on any web host (GitHub Pages, S3, etc.)
- Full Jupyter ecosystem compatibility
- Interactive visualizations and widgets

**Agent-Driven Content Creation:**
- Jupyter notebooks (`.ipynb` JSON format) are well-understood by LLMs
- Static deployment pipeline can be automated
- **Verdict: Good candidate** -- established notebook format, static deployment

---

#### 2.3.3 Observable Framework

| Field | Details |
|-------|---------|
| **URL** | https://observablehq.com/framework/ |
| **Repo** | https://github.com/observablehq/framework |
| **GitHub Stars** | 3,400 |
| **License** | ISC |
| **Latest Release** | v1.13.4 (March 2, 2026) |
| **Language** | JavaScript/TypeScript |

**Key Features:**
- Static site generator for data apps, dashboards, and reports
- Markdown pages with reactive JavaScript
- Data loaders in any language (SQL, Python, R) generate static snapshots at build time
- Built-in libraries: Observable Plot, D3, Mosaic, Vega-Lite, Mermaid, Leaflet, KaTeX
- Themes, grids, and responsive layouts
- Preview server for local development

**Courseware Potential:**
- Excellent for data-driven interactive educational content
- Combines narrative text with live visualizations
- Multi-language data processing (Python/R/SQL backend, JS frontend)
- Fast-loading static sites

**Agent-Driven Content Creation:**
- Markdown + JavaScript content is easily generated
- CLI build/deploy pipeline
- **Verdict: Good candidate** for data-focused courseware

---

### 2.4 Game-Based Learning Frameworks

#### 2.4.1 Phaser

| Field | Details |
|-------|---------|
| **URL** | https://phaser.io/ |
| **Repo** | https://github.com/phaserjs/phaser |
| **GitHub Stars** | 39,200 |
| **License** | MIT |
| **Latest Release** | v3.90.0 (May 23, 2025) |
| **Language** | JavaScript |

**Key Features:**
- 2D game framework for HTML5 games (Canvas and WebGL)
- Physics engines, sprite animations, particle systems
- 14 built-in special effects (Glow, Blur, Bloom, etc.)
- Compressed texture support (ETC, ASTC, S3TC, etc.)
- Extensive plugin library and active community
- Phaser 4 in development (5th beta, January 2025)

**Courseware Potential:**
- Build gamified learning experiences and educational games
- Quiz games, simulation exercises, interactive scenarios
- Wide browser compatibility
- Strong documentation and learning resources (Codecademy course available)

**Agent-Driven Content Creation:**
- JavaScript/TypeScript game code can be generated by LLMs
- Scene-based architecture is modular and templatable
- **Verdict: Good** for generating game-based learning modules

---

#### 2.4.2 GDevelop

| Field | Details |
|-------|---------|
| **URL** | https://gdevelop.io/ |
| **License** | MIT (core engine open source) |

**Key Features:**
- No-code/low-code 2D and 3D game creation
- Visual event system with predefined actions
- Cross-platform export (web, mobile, desktop)
- Ideal for beginners and educators

**Courseware Potential:**
- Non-programmers can create educational games
- Good for rapid prototyping of gamified content

**Agent-Driven Content Creation:**
- JSON-based project format could be generated programmatically
- **Verdict: Moderate** -- visual tool, but JSON format enables automation

---

### 2.5 Branching Scenario / Interactive Fiction Engines

#### 2.5.1 Twine

| Field | Details |
|-------|---------|
| **URL** | https://twinery.org/ |
| **Repo** | https://github.com/klembot/twinejs |
| **GitHub Stars** | ~2,700 |
| **License** | GPL |
| **Latest Release** | v2.11.1 (November 8, 2025) |
| **Language** | JavaScript/TypeScript |

**Key Features:**
- Open-source tool for interactive, nonlinear stories
- Multiple story formats: Harlowe (beginner), SugarCube (advanced), Chapbook
- Variables, conditional logic, images, CSS, and JavaScript support
- Browser-based and desktop versions available
- Twee text format for version control
- Research: LLM-driven generation and repair of Twine/Twee interactive fiction graphs

**Courseware Potential:**
- Excellent for branching scenario-based training (compliance, decision-making, soft skills)
- Low barrier to entry for instructional designers
- Popular in L&D for creating scenario-based exercises
- SugarCube format supports save/load (progress tracking)

**Limitations:**
- No native SCORM support (requires custom wrapper)
- No built-in assessment or grading
- Limited multimedia capabilities compared to dedicated e-learning tools

**Agent-Driven Content Creation:**
- Twee format is a simple text markup that LLMs can easily generate
- Recent research demonstrates LLM-driven Twine/Twee generation
- **Verdict: Excellent candidate** -- Twee is one of the simplest formats for LLM generation

---

## 3. AI-Powered Course Creation Tools

### 3.1 Open Source / Open Tools

#### 3.1.1 OATutor (Open Adaptive Tutor)

| Field | Details |
|-------|---------|
| **URL** | https://www.oatutor.io/ |
| **Repo** | https://github.com/CAHLR/OATutor |
| **GitHub Stars** | 176 |
| **License** | CC BY 4.0 (content); MIT (source code) |
| **Language** | ReactJS, Firebase, Python |
| **Last Updated** | Active (856 commits) |

**Key Features:**
- First fully open-source adaptive tutoring system
- Bayesian Knowledge Tracing (BKT) for skill mastery estimation
- Built-in A/B testing for learning experiments
- Creative Commons-licensed problem library (3 algebra textbooks)
- Scaffolding and hint system
- LTI integration via middleware backend
- GPT integration variant (OATutor-GPT-Study) for AI-powered tutoring
- Section 508 accessibility compliance

**Strengths:**
- Research-grade platform from UC Berkeley
- Deployed at UC Berkeley, CalBright College, Mission College, KTH
- Open content + open source = fully transparent
- GenAI integration actively being researched

**Limitations:**
- Focused primarily on STEM (algebra) content
- Requires Firebase for logging
- Small development team (academic project)
- Limited LMS integration (LTI requires middleware)

**Agent-Driven Content Creation:**
- Problem content is JSON-structured and can be programmatically generated
- GPT variants demonstrate LLM content generation integration
- **Verdict: Good candidate** for STEM adaptive tutoring content

---

#### 3.1.2 Open edX AI Course Creator

| Field | Details |
|-------|---------|
| **URL** | https://openedx.org/blog/introducing-the-ai-course-creator-for-the-open-edx-platform/ |
| **Developer** | Blend-ed |
| **License** | Open source (Open edX ecosystem) |
| **Last Updated** | 2025 (v2 released) |

**Key Features:**
- LLM-powered course generation from diverse sources (YouTube, PDFs, documentation)
- AI generates course outlines, sections, subsections, and assessments
- Fully editable via natural language prompts or direct editing
- Sources relevant public videos and connected video libraries
- Packages output as `.tar.gz` for Open edX import
- No hallucination design: model only uses provided content

**Strengths:**
- Integrated directly into Open edX ecosystem
- Uses RAG approach (grounded in source content)
- Full course generation in ~6 minutes
- Editable at every stage

**Limitations:**
- Tied to Open edX platform
- Output format is Open edX-specific (not SCORM)
- Requires Open edX infrastructure

**Agent-Driven Content Creation:**
- **Purpose-built for automated course generation**
- **Verdict: Excellent** -- specifically designed for AI/agent-driven workflows

---

#### 3.1.3 LLM-Based Quiz/Assessment Generators (Open Source)

**MCQ Generator** (https://github.com/csv610/mcq_generator)
- Uses OpenAI GPT and Ollama for generating contextually relevant questions
- Supports multiple difficulty levels and subjects
- Open source

**Obsidian Quiz Generator** (https://github.com/ECuiDev/obsidian-quiz-generator)
- Generates flashcards from notes using OpenAI, Google Gemini, Ollama
- Supports: true/false, multiple choice, fill-in-blank, matching, short/long answer
- Integrates with Obsidian knowledge base

**AutoQuizzer**
- Uses Haystack framework + LLaMa-3-8B-Instruct via Groq
- Extracts text from web pages and generates quizzes
- Open source pipeline approach

**Common Architecture Pattern:**
- RAG pipelines: Semantically search training material for relevant passages
- Pass context to LLM for question generation
- LangChain commonly used as orchestration framework
- **Verdict: Strong building blocks** for agent-driven assessment generation

---

### 3.2 Commercial AI Course Creation Tools

#### 3.2.1 Mindsmith

| Field | Details |
|-------|---------|
| **URL** | https://www.mindsmith.ai/ |
| **License** | Proprietary (free tier) |
| **Founded** | 2023; $4.1M seed round (November 2025) |
| **Last Updated** | 2026 (active) |

**Key Features:**
- AI-native eLearning authoring platform
- Dynamic SCORM: lightweight wrapper in LMS, cloud-hosted content auto-updates
- SCORM (multiple versions), xAPI, AICC, and LTI support
- AI-driven content generation and interactions
- Staging, multi-language support, workflow management
- SCORM packages auto-update when content changes

**Strengths:**
- Dynamic SCORM approach solves the version management problem
- Comprehensive standards support (SCORM, xAPI, AICC, LTI)
- AI-first design philosophy
- Clean, modern interface
- Growing rapidly (recently funded)

**Limitations:**
- Proprietary platform
- Pricing not fully transparent
- Dependent on cloud service availability
- Limited customization compared to open-source frameworks

**Agent-Driven Content Creation:**
- AI-native design suggests API-friendly architecture
- Dynamic SCORM approach is inherently API-driven
- **Verdict: Promising** but limited public API documentation

---

#### 3.2.2 Coursebox AI

| Field | Details |
|-------|---------|
| **URL** | https://www.coursebox.ai/ |
| **License** | Proprietary (freemium) |
| **Pricing** | Free (3 courses), $69.99/mo (Learning Designer), $209.99/mo (Branded Platform), Enterprise (custom) |

**Key Features:**
- AI-powered course generation from text/documents
- AI avatar training video generator
- AI assessment and grading with customizable rubrics
- AI tutor chatbot trained on course content
- SCORM and LTI integration
- Works with Moodle, Canvas, Blackboard, TalentLMS
- Zapier, HRIS, Slack, Teams integrations

**Agent-Driven Content Creation:**
- Enterprise plan includes custom integrations and APIs
- SCORM/LTI output formats
- **Verdict: Moderate** -- enterprise API available, but cloud-only

---

#### 3.2.3 Synthesia (AI Video for Training)

| Field | Details |
|-------|---------|
| **URL** | https://www.synthesia.io/ |
| **License** | Proprietary |

**Key Features:**
- AI avatar video generation (160+ languages)
- Studio-quality training videos without cameras/actors
- LMS integration (SCORM compatible)
- API available for programmatic video generation

**Agent-Driven Content Creation:**
- API available for video generation
- **Verdict: Good** for automated video courseware generation

---

#### 3.2.4 Colossyan Creator

| Field | Details |
|-------|---------|
| **URL** | https://www.colossyan.com/ |
| **License** | Proprietary |

**Key Features:**
- AI avatars with natural voiceovers
- Built-in quizzes, interactive branching scenarios
- SCORM export for LMS delivery
- Course creation from text, PDFs, presentations
- Localization and dubbing
- API access (360 minutes/year on Business plan)

**Strengths over Synthesia for L&D:**
- Purpose-built for corporate training
- Built-in interactivity (quizzes, branching)
- Native SCORM export

**Agent-Driven Content Creation:**
- API available (limited minutes on business plan)
- **Verdict: Good** for L&D-specific video generation with interactivity

---

### 3.3 Adaptive Learning Engines

**Key Open Source Options:**

| Tool | Type | Key Feature |
|------|------|-------------|
| OATutor | Adaptive tutoring | BKT + GenAI, open source |
| Open edX | Adaptive paths | AI learning paths (planned) |

**Commercial Adaptive Platforms (2026 landscape):**
- Docebo (AI-powered content recommendations, personalized learning paths)
- Sana Labs (AI-powered learning platform for enterprise)
- Area9 Lyceum (adaptive learning engine)
- DreamBox (K-12 adaptive math)

The adaptive learning market is projected at $5.3 billion by 2025, with most solutions being proprietary. OATutor remains the most significant open-source adaptive tutoring system.

---

## 4. Multimedia Integration

### 4.1 Video Generation

#### 4.1.1 Remotion (Programmatic Video with React)

| Field | Details |
|-------|---------|
| **URL** | https://www.remotion.dev/ |
| **Repo** | https://github.com/remotion-dev/remotion |
| **GitHub Stars** | 31,000+ |
| **License** | Custom (free for individuals/teams up to 3; Company License from $100/mo) |
| **Language** | TypeScript/React |

**Key Features:**
- Create videos programmatically with React components
- Render MP4, WebM, or audio formats
- Server-side rendering for scalable video generation
- Remotion Player for in-browser playback
- Remotion Studio for development
- Parametrizable content (data-driven videos)
- Audio support including programmatically generated tones

**Courseware Integration:**
- Generate personalized training videos at scale
- Create animated explanations, tutorials, and walkthroughs
- Combine with TTS APIs for narrated video content
- Parametric content enables one template, many outputs
- Can be integrated into automated content pipelines

**Agent-Driven Content Creation:**
- React components are templatable and LLM-generatable
- Server-side rendering API for batch generation
- Parametric approach is inherently agent-friendly
- **Verdict: Excellent** for programmatic video generation in courseware pipelines

---

#### 4.1.2 AI Avatar Video Platforms

| Platform | API | SCORM | Languages | L&D Features |
|----------|-----|-------|-----------|--------------|
| Synthesia | Yes | Yes | 160+ | LMS integration |
| Colossyan | Yes (limited) | Yes | 70+ | Quizzes, branching |
| HeyGen | Yes | Limited | 175+ | Avatars, translation |

---

### 4.2 Audio / Narration (TTS Integration)

#### 4.2.1 ElevenLabs

| Field | Details |
|-------|---------|
| **URL** | https://elevenlabs.io/ |
| **API** | https://elevenlabs.io/docs/api-reference/text-to-speech |

**Key Features:**
- Lifelike TTS with nuanced intonation, pacing, emotional awareness
- 32 languages, multiple voice styles
- Voice cloning capability
- Flash v2.5: ultra-low 75ms latency for real-time applications
- Multilingual v2: highest quality with nuanced expression
- REST API with comprehensive documentation

**Courseware Integration:**
- Generate narration for any course content
- Multi-language course localization
- Consistent voice across entire courses
- Real-time narration for interactive content

---

#### 4.2.2 OpenAI TTS API

**Key Features:**
- 6 high-quality preset voices
- Multi-language support
- "Steerability": prompt-based tone control ("speak in a calm, friendly tone")
- GPT ecosystem integration

#### 4.2.3 LocalAI TTS

**Key Features:**
- Open source, self-hosted
- Compatible with both OpenAI TTS and ElevenLabs APIs
- Run TTS locally without cloud dependency

---

### 4.3 Image Generation

| Platform | API | Open Source | Best For |
|----------|-----|------------|----------|
| **DALL-E 3 / GPT Image** | OpenAI API | No | High-quality, prompt-adherent images |
| **Stable Diffusion 3 / SDXL** | Replicate, local | Yes (model weights) | Customization, local runs, low cost (<$0.002/image) |
| **Flux** | Replicate API | Partially | Fast generation, good quality |
| **Midjourney** | No public API | No | Artistic quality (manual use only) |

**Courseware Integration Approach:**
- Generate illustrations, diagrams, and scenario images from text descriptions
- Stable Diffusion for self-hosted, cost-effective batch generation
- DALL-E/GPT Image for highest quality with API access
- Use LoRA/fine-tuning for consistent visual style across a course

---

### 4.4 Interactive Diagrams and Visualizations

#### 4.4.1 Mermaid

| Field | Details |
|-------|---------|
| **URL** | https://mermaid.js.org/ |
| **Repo** | https://github.com/mermaid-js/mermaid |
| **License** | MIT |

**Key Features:**
- Text-based diagram generation (flowcharts, sequence diagrams, ERDs, Gantt charts, mindmaps, user journeys, pie charts, state diagrams)
- Renders in browser with JavaScript
- Natively supported in GitHub, Quarto, Hugo, Jekyll, Jupyter
- Lightweight, no heavy dependencies
- Themeable and customizable

**Courseware Integration:**
- Diagrams-as-code: perfect for agent-generated technical content
- Embed in any web-based courseware
- Real-time rendering, no image generation needed

---

#### 4.4.2 D3.js + Observable Plot

| Field | Details |
|-------|---------|
| **URL** | https://d3js.org/ / https://observablehq.com/plot/ |
| **License** | ISC (D3), ISC (Plot) |

**Key Features:**
- D3: Low-level data visualization library with unparalleled flexibility
- Observable Plot: High-level API for quick charts (histogram in 1 line vs 50 in D3)
- Interactive behaviors: pan, zoom, brush, drag
- Animated transitions with object constancy

---

#### 4.4.3 Excalidraw

| Field | Details |
|-------|---------|
| **URL** | https://excalidraw.com/ |
| **Repo** | https://github.com/excalidraw/excalidraw |
| **GitHub Stars** | 119,000 |
| **License** | MIT |
| **Latest Release** | v0.18.0 (March 11, 2025) |
| **Language** | TypeScript (94%) |

**Key Features:**
- Virtual whiteboard with hand-drawn aesthetic
- Real-time collaboration (end-to-end encrypted)
- Embeddable as React component
- Frames for creating presentation slides
- SVG export for documentation embedding
- Follow mode and voice hangouts
- Extensive shape, connector, and text tools

**Courseware Integration:**
- Embed interactive whiteboards in courseware
- Collaborative exercises and activities
- Diagram creation with approachable visual style
- Exportable for static content inclusion

---

### 4.5 3D Content and WebGL

#### 4.5.1 Three.js

| Field | Details |
|-------|---------|
| **URL** | https://threejs.org/ |
| **Repo** | https://github.com/mrdoob/three.js |
| **GitHub Stars** | 111,000 |
| **License** | MIT |
| **Latest Release** | r183 (February 20, 2026) |

**Key Features:**
- Premier JavaScript 3D library for WebGL
- Scenes, cameras, lighting, materials, geometries
- Physics, animations, post-processing effects
- WebXR support for VR/AR experiences
- Extensive examples and documentation

**Courseware Integration:**
- Interactive 3D simulations (science, engineering, architecture)
- Virtual lab environments
- 3D data visualization
- Immersive learning experiences

---

#### 4.5.2 A-Frame

| Field | Details |
|-------|---------|
| **URL** | https://aframe.io/ |
| **License** | MIT |

**Key Features:**
- WebXR framework built on Three.js
- HTML-like syntax for 3D scenes (low learning curve)
- Entity-Component-System architecture
- Native WebXR/VR/AR support
- Component ecosystem

**Courseware Integration:**
- VR/AR learning experiences with minimal code
- Accessible 3D content creation
- Cross-device compatibility

---

## 5. Standards and Packaging

### 5.1 SCORM (Sharable Content Object Reference Model)

#### SCORM 1.2
- **Status:** Most widely supported, de facto standard
- **Data Model:** Limited interaction tracking
- **Storage:** 4,096 character suspend data limit
- **Tracking:** Pass/fail or complete/incomplete (cannot report both simultaneously)
- **Navigation:** No sequencing rules
- **Rollup:** LMS handles rollup logic
- **Compatibility:** Supported by virtually every LMS
- **Best For:** Simple compliance training, basic course completion tracking

#### SCORM 2004 (Editions 2-4)
- **Status:** Supported by most enterprise LMS
- **Data Model:** Enhanced interactions with full question/answer text
- **Storage:** 64,000 character suspend data limit
- **Tracking:** Can report both Completed and Passed simultaneously
- **Navigation:** Sequencing and Navigation (S&N) rules
- **Rollup:** Course handles rollup signaling
- **Editions:** 2nd (basic), 3rd (most adopted for enterprise), 4th (most complete)
- **Best For:** Complex courses requiring branching, detailed assessment tracking

#### Key SCORM Limitations
- Browser-only: cannot track learning outside the LMS
- Single-SCO tracking: limited to one learner session at a time
- No offline support
- Content must be packaged as ZIP with imsmanifest.xml
- SCORM 2004 S&N is complex and inconsistently implemented across LMS

---

### 5.2 xAPI (Experience API / Tin Can)

| Field | Details |
|-------|---------|
| **Spec Version** | 2.0 (IEEE 9274.1.1) |
| **Format** | JSON statements (Actor-Verb-Object) |
| **Storage** | Learning Record Store (LRS) |

**Key Capabilities:**
- Track learning anywhere (mobile, simulations, VR, offline, on-the-job)
- Rich statement format with extensions
- No browser/LMS restriction
- Social and collaborative learning tracking
- Detailed behavioral data collection

**Open Source LRS Options:**

| LRS | License | Technology | Notes |
|-----|---------|-----------|-------|
| **SQL LRS** (Yet Analytics) | Apache 2.0 | SQL-based | Cloud or on-premise deployment |
| **ADL LRS** | Apache 2.0 | Python/Django | Updated for xAPI 2.0 (IEEE standard) |
| **Learning Locker** | GPL v3 | Node.js/MongoDB | Most popular open-source LRS |

---

### 5.3 cmi5

| Field | Details |
|-------|---------|
| **Status** | Current recommended standard for new development |
| **Relationship** | xAPI Profile for LMS-launched content |

**Key Features:**
- Combines SCORM's structured launch mechanism with xAPI's flexible tracking
- Content launched from LMS but tracked via xAPI statements
- Supports offline, mobile, and cross-platform learning
- Cleaner separation of concerns (LMS handles launch, content handles tracking)
- Built on xAPI (all cmi5 data is valid xAPI)

**Adoption:**
- Growing but still limited compared to SCORM
- Supported by: WorkRamp, Docebo, iSpring, Articulate, Captivate, dominKnow
- Many LMS support cmi5 but default to SCORM for compatibility

---

### 5.4 LTI (Learning Tools Interoperability)

| Field | Details |
|-------|---------|
| **Current Version** | LTI 1.3 + LTI Advantage |
| **Spec Body** | 1EdTech (formerly IMS Global) |
| **Security** | OAuth 2.0, OpenID Connect, JWTs |

**Key Features:**
- Embed external tools/content seamlessly in any LMS
- LTI Advantage adds: Deep Linking, Names and Roles, Assignment and Grade Services
- Single sign-on between LMS and external tools
- Grade passback from tool to LMS gradebook

**Use Cases:**
- Embed interactive coding environments (StackBlitz, Sandpack)
- Connect assessment tools to LMS gradebooks
- Launch external simulations within LMS context
- Integrate video platforms, collaboration tools

**Corporate LMS Support:**
- Canvas, Blackboard, Moodle, Brightspace: Full LTI 1.3 + Advantage
- Docebo: LTI support
- Cornerstone: LTI support
- Adobe Learning Manager: LTI 1.3 (provider and consumer)

---

### 5.5 Corporate LMS Standards Compatibility Matrix

| LMS | SCORM 1.2 | SCORM 2004 | xAPI | cmi5 | LTI |
|-----|-----------|------------|------|------|-----|
| **WorkRamp** | Yes | Yes (2nd-4th ed.) | Yes | Yes | Yes |
| **Docebo** | Yes | Yes | Yes | Yes | Yes |
| **Cornerstone** | Yes | Yes (3rd ed.) | Yes | Planned | Yes |
| **Absorb** | Yes | Yes | Yes | Yes | Yes |
| **Canvas** | Yes | Yes | Yes | Limited | Yes (1.3) |
| **Moodle** | Yes | Yes | Via plugin | Via plugin | Yes |

**Practical Recommendations for Maximum Compatibility:**
1. **SCORM 1.2** remains the safest bet for universal LMS compatibility
2. **SCORM 2004 3rd Edition** for enterprise LMS with advanced tracking needs
3. **xAPI + cmi5** for modern platforms and advanced analytics
4. **LTI 1.3** for embedding interactive tools within LMS
5. **Package multiple formats** when possible (SCORM 1.2 + xAPI for maximum reach)

---

## 6. Summary Comparison Tables

### 6.1 SCORM/xAPI Authoring Tools

| Tool | Open Source | SCORM | xAPI | cmi5 | LTI | Agent API | Maturity |
|------|------------|-------|------|------|-----|-----------|----------|
| **Adapt Learning** | Yes (GPL v3) | 1.2 + 2004 | Yes | No | No | JSON + CLI | High |
| **H5P** | Yes (GPL v3) | Via wrapper | Yes | No | No | REST (EscolaLMS) | High |
| **Xerte** | Yes (Apache 2.0) | Yes | Limited | No | No | XML | High |
| **Open edX** | Yes (AGPL v3) | No (native format) | Limited | No | Yes (1.3) | REST API | Very High |
| **Open eLearning** | Yes (GPL v3) | Yes | No | No | No | None | Low |
| **CogniSpark** | Partial | Yes | Yes | No | No | Moodle plugin | Medium |
| **Mindsmith** | No | Dynamic SCORM | Yes | No | Yes | Possible | Medium |
| **Compozer** | No | 1.2 + 2004 | Yes | Yes | No | None | Medium |

### 6.2 Interactive Content Frameworks

| Tool | Stars | License | Content Format | Embeddable | Agent-Friendly |
|------|-------|---------|---------------|------------|----------------|
| **Reveal.js** | 70.7k | MIT | HTML/Markdown | Yes | Excellent |
| **Slidev** | 44.9k | MIT | Markdown/Vue | Yes (SPA) | Excellent |
| **Sandpack** | 6.1k | Apache 2.0 | React components | Yes | Excellent |
| **WebContainers** | N/A | Commercial | JS API | Yes | Excellent |
| **Marimo** | 19.7k | Apache 2.0 | Pure Python | Yes (WASM) | Excellent |
| **JupyterLite** | 4.8k | BSD-3 | .ipynb JSON | Yes (static) | Good |
| **Observable FW** | 3.4k | ISC | Markdown/JS | Yes (static) | Good |
| **Quarto** | N/A | GPL v2 | Markdown | Yes | Good |
| **Twine** | 2.7k | GPL | Twee/HTML | Yes | Excellent |
| **Phaser** | 39.2k | MIT | JavaScript | Yes | Good |

### 6.3 Visualization & Multimedia Tools

| Tool | Stars | License | Type | Agent-Friendly |
|------|-------|---------|------|----------------|
| **Excalidraw** | 119k | MIT | Whiteboard/Diagrams | Good |
| **Three.js** | 111k | MIT | 3D/WebGL | Moderate |
| **Mermaid** | N/A | MIT | Diagrams-as-code | Excellent |
| **D3.js** | N/A | ISC | Data visualization | Moderate |
| **Remotion** | 31k+ | Custom | Programmatic video | Excellent |

### 6.4 AI-Powered Tools

| Tool | Open Source | AI Type | Output Format | Agent-Friendly |
|------|------------|---------|--------------|----------------|
| **OATutor** | Yes (CC BY 4.0) | Adaptive (BKT + GenAI) | Web app | Good |
| **Open edX AI Creator** | Yes | LLM course generation | Open edX .tar.gz | Excellent |
| **Mindsmith** | No | AI authoring | Dynamic SCORM | Promising |
| **Coursebox** | No | AI course + video | SCORM/LTI | Enterprise API |
| **Synthesia** | No | AI avatar video | MP4/SCORM | Good (API) |
| **Colossyan** | No | AI avatar + L&D | SCORM | Good (API) |

---

## 7. Recommendations for Agent-Driven Courseware Pipeline

Based on this research, the most promising architecture for an agent-driven courseware creation system would combine:

### Content Generation Layer
1. **LLM (Claude, GPT-4, etc.)** for generating course outlines, text content, assessments
2. **Twee/Twine format** for branching scenarios (trivially LLM-generatable)
3. **Mermaid** for diagrams (text-based, LLM-generatable)
4. **Marimo notebooks** for interactive Python-based exercises (pure Python files)

### Media Generation Layer
1. **Remotion** for programmatic video generation from React templates
2. **ElevenLabs / OpenAI TTS** for narration generation
3. **Stable Diffusion / DALL-E** for illustration generation
4. **Excalidraw** for collaborative diagrams

### Interactive Elements Layer
1. **Sandpack** for embedded coding exercises
2. **H5P** (via EscolaLMS headless API) for interactive activities
3. **Phaser** for gamified elements
4. **Reveal.js or Slidev** for presentation-based modules

### Packaging & Delivery Layer
1. **Adapt Learning Framework** for SCORM 1.2/2004 packaging (JSON config generation)
2. **SCORM-H5P-Wrapper** for H5P-to-SCORM packaging
3. **xAPI + SQL LRS** for advanced analytics
4. **LTI 1.3** for embedding interactive tools in corporate LMS

### Standards Strategy
- **Primary:** SCORM 1.2 packages for maximum LMS compatibility
- **Secondary:** xAPI statements for detailed learning analytics
- **Integration:** LTI 1.3 for embedding external interactive tools
- **Future-proof:** cmi5 for new deployments where supported

---

## Sources

### SCORM/xAPI/cmi5 Authoring
- [Adapt Learning Framework](https://www.adaptlearning.org/)
- [Adapt Framework GitHub](https://github.com/adaptlearning/adapt_framework)
- [H5P - Create and Share Rich HTML5 Content](https://h5p.org/)
- [H5P February 2026 Update](https://h5p.org/h5p-february-2026-update)
- [EscolaLMS Headless H5P](https://github.com/EscolaLMS/H5P)
- [SCORM-H5P-Wrapper](https://github.com/sr258/scorm-h5p-wrapper)
- [Xerte Online Toolkits](https://xerte.org.uk/)
- [Xerte GitHub](https://github.com/thexerteproject/xerteonlinetoolkits)
- [Open edX Platform](https://openedx.org/)
- [Open edX AI Course Creator](https://openedx.org/blog/introducing-the-ai-course-creator-for-the-open-edx-platform/)
- [Open eLearning](https://www.openelearning.org/)
- [CogniSpark AI](https://www.cognispark.ai/)
- [Mindsmith AI](https://www.mindsmith.ai/)
- [Compozer](https://www.compozer.com/)
- [Free SCORM Authoring Tools 2026](https://www.paradisosolutions.com/blog/free-scorm-authoring-tools/)

### Interactive Content Frameworks
- [Reveal.js](https://revealjs.com/)
- [Slidev](https://sli.dev/)
- [Slidev Plugins for CS Teaching](https://www.krisluyten.net/news/2025/11/13/slidev_plugins_jdoodle/)
- [Quarto](https://quarto.org/)
- [Sandpack](https://sandpack.codesandbox.io/)
- [StackBlitz WebContainers](https://webcontainers.io/)
- [Marimo](https://marimo.io/)
- [Marimo for Educators](https://marimo.io/for-educators)
- [JupyterLite](https://github.com/jupyterlite/jupyterlite)
- [Observable Framework](https://observablehq.com/framework/)
- [Twine](https://twinery.org/)
- [Phaser](https://phaser.io/)
- [LearnHouse](https://github.com/learnhouse/learnhouse)

### AI-Powered Tools
- [OATutor](https://www.oatutor.io/)
- [OATutor GitHub](https://github.com/CAHLR/OATutor)
- [Coursebox AI](https://www.coursebox.ai/)
- [Synthesia](https://www.synthesia.io/)
- [Colossyan Creator](https://www.colossyan.com/)
- [AI in eLearning Content Creation 2026](https://disprz.ai/blog/ai-in-elearning-content-creation)

### Multimedia Integration
- [Remotion](https://www.remotion.dev/)
- [ElevenLabs TTS API](https://elevenlabs.io/text-to-speech-api)
- [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech)
- [Excalidraw](https://excalidraw.com/)
- [Three.js](https://threejs.org/)
- [Mermaid](https://mermaid.js.org/)
- [D3.js](https://d3js.org/)

### Standards & LMS
- [SCORM 1.2 vs 2004 Comparison](https://scorm.com/scorm-explained/business-of-scorm/comparing-scorm-1-2-and-scorm-2004/)
- [xAPI and Learning Record Stores](https://xapi.com/learning-record-store/)
- [cmi5 Specification](https://aicc.github.io/CMI-5_Spec_Current/SCORM/)
- [LTI 1.3 Specification](https://www.imsglobal.org/spec/lti/v1p3)
- [SQL LRS](https://www.sqllrs.com/)
- [ADL LRS](https://github.com/adlnet/ADL_LRS)
- [Learning Locker](https://github.com/LearningLocker/learninglocker)
- [Docebo Standards](https://www.docebo.com/learning-network/blog/elearning-standards-scorm-xapi-cmi5/)
- [WorkRamp SCORM](https://help.workramp.com/en/articles/2421835-scorm-files-in-workramp)
- [Cornerstone Standards](https://help.csod.com/help/csod_0/Content/General_Minimum_Requirements.htm)
- [SCORM, xAPI, LTI for LMS Buyers 2025](https://elearningindustry.com/scorm-xapi-and-lti-what-every-lms-buyer-needs-to-know)
