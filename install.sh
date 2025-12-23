#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
TARGET_DIR="$HOME/.claude/skills"

mkdir -p "$TARGET_DIR"

echo "Installing skills from $SKILLS_DIR..."

for skill_path in "$SKILLS_DIR"/*/; do
  skill_name=$(basename "$skill_path")
  target="$TARGET_DIR/$skill_name"

  if [ -L "$target" ]; then
    rm "$target"
  elif [ -d "$target" ]; then
    echo "  SKIP: $skill_name (directory exists, not a symlink)"
    continue
  fi

  ln -s "$skill_path" "$target"
  echo "  OK: $skill_name"
done

echo "Done."
