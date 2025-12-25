#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
CLAUDE_DIR="$HOME/.claude/skills"
CODEX_DIR="$HOME/.codex/skills"
OPENCODE_DIR="$HOME/.opencode/skill"

mkdir -p "$CLAUDE_DIR" "$CODEX_DIR" "$OPENCODE_DIR"

install_skills() {
  local target_dir="$1"
  local label="$2"

  echo "Installing to $label ($target_dir)..."

  for skill_path in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_path")
    target="$target_dir/$skill_name"

    if [ -L "$target" ]; then
      rm "$target"
    elif [ -d "$target" ]; then
      echo "  SKIP: $skill_name (directory exists)"
      continue
    fi

    ln -s "$skill_path" "$target"
    echo "  OK: $skill_name"
  done
}

install_skills "$CLAUDE_DIR" "Claude"
install_skills "$CODEX_DIR" "Codex"
install_skills "$OPENCODE_DIR" "OpenCode"

echo "Done."
