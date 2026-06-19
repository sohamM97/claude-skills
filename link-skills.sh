#!/usr/bin/env bash
#
# link-skills.sh — symlink every skill in this repo into ~/.claude/skills/
#
# Run this on your authoring machine after adding a new skill (or after
# cloning/moving the repo). It is idempotent and safe to re-run:
#   - missing links are created
#   - links pointing at the wrong place (e.g. after a repo move) are re-pointed
#   - a real directory that collides with a repo skill is backed up to <name>.bak
#   - unrelated local-only skills in ~/.claude/skills are never touched
#
# Honors $CLAUDE_CONFIG_DIR; defaults to ~/.claude.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
SKILLS_DST="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"

mkdir -p "$SKILLS_DST"

linked=0 repointed=0 ok=0 backed_up=0

for src in "$SKILLS_SRC"/*/; do
  [ -d "$src" ] || continue
  src="${src%/}"
  name="$(basename "$src")"
  dst="$SKILLS_DST/$name"

  if [ -L "$dst" ]; then
    if [ "$(readlink "$dst")" = "$src" ]; then
      ok=$((ok + 1))
      continue
    fi
    rm "$dst"
    ln -s "$src" "$dst"
    echo "re-pointed: $name"
    repointed=$((repointed + 1))
  elif [ -e "$dst" ]; then
    echo "backing up existing dir: $name -> $name.bak"
    rm -rf "$dst.bak"
    mv "$dst" "$dst.bak"
    ln -s "$src" "$dst"
    backed_up=$((backed_up + 1))
  else
    ln -s "$src" "$dst"
    echo "linked: $name"
    linked=$((linked + 1))
  fi
done

echo "Done. linked=$linked re-pointed=$repointed backed-up=$backed_up already-ok=$ok -> $SKILLS_DST"
