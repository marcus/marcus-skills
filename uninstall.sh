#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
CLAUDE_DIR="$HOME/.claude/skills"
CODEX_DIR="$HOME/.codex/skills"

uninstall_skills() {
  local target_dir="$1"
  local label="$2"

  echo "Removing from $label ($target_dir)..."

  for skill_path in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_path")
    target="$target_dir/$skill_name"

    if [ -L "$target" ]; then
      rm "$target"
      echo "  REMOVED: $skill_name"
    else
      echo "  SKIP: $skill_name (not a symlink)"
    fi
  done
}

uninstall_skills "$CLAUDE_DIR" "Claude"
uninstall_skills "$CODEX_DIR" "Codex"

echo "Done."
