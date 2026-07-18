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

# ---------------------------------------------------------------------------
# Register the UserPromptSubmit hook in settings.json.
#
# Hooks (unlike skills) are NOT activated by symlinking — Claude Code only loads
# hooks from a settings file or an installed plugin, not from ~/.claude/skills.
# On this authoring machine the plugin isn't installed (skills are symlinked),
# so we register the bundled hook directly in settings.json, pointing at the
# repo script. Idempotent; requires jq (skipped with a note otherwise).
# ---------------------------------------------------------------------------
SETTINGS_FILE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json"
HOOK_CMD="bash $REPO_DIR/hooks/stamp-prompt-time.sh"

if ! command -v jq >/dev/null 2>&1; then
  echo "hook: jq not found — skipping. Add a UserPromptSubmit hook running '$HOOK_CMD' to $SETTINGS_FILE manually."
else
  [ -f "$SETTINGS_FILE" ] || echo '{}' > "$SETTINGS_FILE"
  if jq -e --arg cmd "$HOOK_CMD" \
      '[.hooks.UserPromptSubmit[]?.hooks[]?.command] | index($cmd) != null' \
      "$SETTINGS_FILE" >/dev/null 2>&1; then
    echo "hook: stamp-prompt-time already registered in $SETTINGS_FILE"
  else
    tmp="$(mktemp)"
    if jq --arg cmd "$HOOK_CMD" \
        '.hooks.UserPromptSubmit = ((.hooks.UserPromptSubmit // []) + [{"hooks": [{"type": "command", "command": $cmd}]}])' \
        "$SETTINGS_FILE" > "$tmp" 2>/dev/null && mv "$tmp" "$SETTINGS_FILE"; then
      echo "hook: registered stamp-prompt-time in $SETTINGS_FILE (restart Claude Code to activate)"
    else
      rm -f "$tmp"
      echo "hook: could not update $SETTINGS_FILE (invalid JSON?) — register the UserPromptSubmit hook manually."
    fi
  fi
fi
