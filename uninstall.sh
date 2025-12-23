#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
TARGET_DIR="$HOME/.claude/skills"

echo "Removing symlinks for skills in $SKILLS_DIR..."

for skill_path in "$SKILLS_DIR"/*/; do
  skill_name=$(basename "$skill_path")
  target="$TARGET_DIR/$skill_name"

  if [ -L "$target" ]; then
    rm "$target"
    echo "  REMOVED: $skill_name"
  else
    echo "  SKIP: $skill_name (not a symlink)"
  fi
done

echo "Done."
