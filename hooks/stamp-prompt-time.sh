#!/usr/bin/env bash
#
# stamp-prompt-time.sh — UserPromptSubmit hook.
#
# Stamps screenshot-related prompts with their submission time (epoch seconds)
# so the `check-screenshot` skill can ignore screenshots that arrived AFTER the
# message was sent (e.g. a follow-up screenshot pasted while Claude was busy —
# `ls -t` would otherwise grab the newer, unintended one).
#
# On UserPromptSubmit, a hook's stdout is injected into the model's context for
# that message, so the skill can read the marker below.
#
# Scoped: only stamps prompts that look screenshot-related, so unrelated
# messages get no injected context.
#
# NOTE: always exits 0 — a non-zero UserPromptSubmit exit can block the prompt.

input="$(cat)"

# The user's prompt text; field name has varied across versions, so try both,
# then fall back to grepping the raw JSON payload.
prompt="$(printf '%s' "$input" | jq -r '.prompt // .user_input // empty' 2>/dev/null)"
[ -z "$prompt" ] && prompt="$input"

if printf '%s' "$prompt" | grep -qiE 'screenshot|check-screenshot|look at (this|the|that|my)'; then
  printf '[message-submitted-at-epoch: %s] — check-screenshot note: only consider screenshots whose file mtime is <= this epoch; ignore any newer ones (they arrived after this message was sent).\n' "$(date +%s)"
fi

exit 0
