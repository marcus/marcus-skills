# Marcus Skills

<img src="skill.png" alt="Skills" width="300" />

Custom skills for [Claude Code](https://claude.ai/code) and [OpenAI Codex](https://openai.com/codex).

## Install

```bash
./install.sh
```

Creates symlinks in `~/.claude/skills/` and `~/.codex/skills/`.

## Uninstall

```bash
./uninstall.sh
```

## Skills

| Skill | Description |
|-------|-------------|
| bun-getting-started | Bun 1.3 setup with HRM and Bun.SQL |
| cursor-agent-orchestrator | Parallel cursor-agent process orchestration |
| ollama-python-streaming | Ollama + LiteLLM streaming in Python |
| openrouter-python-streaming | OpenRouter + LiteLLM streaming in Python |
| professional-readme | Developer-focused README.md creation |
| project-metrics-dashboard | Professional metrics dashboard design |
| site-design-director | Website/UI design direction + production code |
| td-task-management | AI agent task management across sessions |

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
