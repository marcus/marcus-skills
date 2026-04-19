# Marcus Skills

<img src="skill.png" alt="Skills" width="300" />

Custom skills for [OpenCode](https://opencode.ai), [Claude Code](https://claude.ai/code), and [OpenAI Codex](https://openai.com/codex).

## Install

```bash
./install.sh
```

Creates symlinks in `~/.opencode/skill/`, `~/.claude/skills/`, and `~/.codex/skills/`.

## Uninstall

```bash
./uninstall.sh
```

## Skills

| Skill                       | Description                                                  |
| --------------------------- | ------------------------------------------------------------ |
| agent-teams                 | Agent team coordination with roles, file ownership, and quality gates |
| browser-board-games         | Multiplayer browser board games with Colyseus, WebSocket networking, and 2D animation |
| betamax-docs                | Reproducible TUI screenshots and GIF demos with Betamax       |
| browser-proof               | Playwright screenshots of Perch UI for visual verification    |
| bun-getting-started         | Bun 1.3 setup with HRM and Bun.SQL                           |
| claude-code-metadata        | Everything you need to know about how Claude stores metadata |
| cursor-agent-orchestrator   | Parallel cursor-agent process orchestration                  |
| dev-docs                    | Developer documentation for open source projects             |
| human-writing               | Natural writing guidelines and AI pattern detection          |
| imessage-extraction         | Extract and query iMessage conversations from macOS chat.db  |
| lightroom-catalog           | Index and search Lightroom CC catalogs with SQLite+FTS5      |
| linear-design-patterns      | Linear-inspired design patterns for keyboard-first apps      |
| multi-turn-runtime-adapters | Multi-turn agent sessions, event normalization, rich component rendering, bidirectional agent↔UI state |
| ollama-python-streaming     | Ollama + LiteLLM streaming in Python                         |
| openrouter-python-streaming | OpenRouter + LiteLLM streaming in Python                     |
| orchestrate                 | Sub-agent orchestration using td for plan-implement-review   |
| professional-readme         | Developer-focused README.md creation                         |
| project-metrics-dashboard   | Professional metrics dashboard design                        |
| rich-link-previews          | Open Graph + Twitter Card metadata for link previews         |
| roc-icons                   | Roc icon library (@marcus/roc) for React, Svelte, and sprites |
| site-design-director        | Website/UI design direction + production code                |
| sqlite-single-writer        | SQLite single-writer queue pattern for multi-process apps    |
| stereo-design-system        | Skeuomorphic hi-fi receiver design system — brushed brass, warm amber |
| sveltekit-latest            | Quick-reference for SvelteKit + Svelte 5 (Feb 2026)          |
| td-review-session           | Review session orchestrator with parallel triage and auto-fix |
| td-ralph-loop               | Autonomous coding loops with Rich TUI cockpit dashboard       |
| td-task-management          | AI agent task management across sessions                     |
| technical-diagrams            | Generate and render C4, sequence, flowchart, architecture diagrams inline using Mermaid.js |
| interactive-courseware           | AI-driven interactive courseware — SCORM/xAPI packaging, multimedia, branching scenarios, LMS delivery |
| software-demo-video           | Premium software demo videos — scripts, production, thumbnails, distribution |
| web-design-system-deliverable | Agency-grade web design systems from brand strategy to production handoff |

## Adding a New Skill

1. Create `skills/{skill-name}/SKILL.md`
2. Add entry to `manifest.json`
3. Run `./install.sh`

## Status Line

Custom Claude Code status line showing repo, branch, model, duration, lines changed, context usage, and current Spotify track.

```
marcus-skills | main* | Opus 4.5 | 2m34s | +142-28 | ● ████░░░░░░ 62% ♫ Song - Artist
```

**Install**: Copy contents of `config/statusline-settings.json` into your `~/.claude/settings.json`

See `config/statusline.sh` for the readable/annotated version.
