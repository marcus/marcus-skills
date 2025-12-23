# Marcus Skills

Custom Claude Code skills for development workflows.

## Install

```bash
./install.sh
```

Creates symlinks in `~/.claude/skills/` pointing to skills in this repo.

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
| td-task-management | AI agent task management across sessions |

## Adding a New Skill

1. Create `skills/{skill-name}/SKILL.md`
2. Add entry to `manifest.json`
3. Run `./install.sh`
