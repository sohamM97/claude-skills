---
name: check-screenshot
description: Check Latest Screenshot. Use when the user mentions screenshots, says "look at this", or wants to show something on screen.
---

# Check Latest Screenshot

Read the most recent screenshot(s) — as of **when the user sent the request** — and describe them.

## Arguments

- Optional: a number N to check the N most recent screenshots (default: 1).
- Optional: `whatsapp` — check WhatsApp images instead of system screenshots.

## Workflow

1. **Determine the directory** (from auto-memory):
   - Default: screenshots directory (e.g. `~/Pictures/Screenshots/`).
   - With `whatsapp` argument: WhatsApp images directory (e.g. `~/Downloads/`).
   - If not found in memory, ask the user where the images are saved, then save to memory for future use.

2. **Determine the cutoff time.** Look in the triggering message's context for a marker injected by the `stamp-prompt-time` UserPromptSubmit hook:

   ```
   [message-submitted-at-epoch: <N>]
   ```

   - If present, `<N>` is the epoch-seconds time the user **sent this request**. **Only consider screenshots whose file mtime is `<= N`.** This is the whole point: it stops you from grabbing a screenshot that arrived *after* the request — e.g. the user typed `/check-screenshot` while you were busy, then pasted a newer screenshot before you got to it. Plain `ls -t` (newest-first) would wrongly pick that newer file, and `date` run inside this skill reflects the *run* time (also after it), so the injected marker is the only reliable send-time.
   - If the marker is **absent** (hook not installed, or the message didn't match its keywords), fall back to no cutoff. But if several screenshots are clustered near "now", say which one you picked and offer to switch — you can't be certain which the user meant.

3. **List candidate files newest-first, respecting the cutoff.** With a cutoff `N`:

   ```bash
   find <dir> -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) \
     ! -newermt "@<N>" -printf '%T@ %p\n' | sort -rn | head -<count>
   ```

   - `! -newermt "@<N>"` keeps only files with mtime at or before the cutoff.
   - `<count>` = the number of most-recent screenshots requested (default 1).
   - **"Last N" respects the cutoff too:** if screenshots exist at t1 < t2 < t3 and the request was sent at t2, "check last 2" → **t1 and t2** (the two newest at-or-before t2), never t3.
   - Without a cutoff (marker absent), drop the `! -newermt` predicate (or use `ls -t`).
   - The `-iname` filter already restricts WhatsApp results to image files.

4. **Read** the selected screenshot(s) with the Read tool (it supports images).

5. **Describe** what you see — focus on anything relevant to the current task or conversation.

6. If the user seems to be showing a bug or UI issue, call it out specifically.

## Rules

- If the directory is empty (or has no files at/before the cutoff), tell the user.
- Always mention the filename and its timestamp so the user knows which screenshot you're looking at.
- Don't make assumptions about what the user wants — describe what you see and ask if they need something specific.
- When the user says "check latest whatsapp screenshot" or similar, use the WhatsApp directory.

## The timestamp cutoff (setup)

The cutoff in step 2 relies on the `stamp-prompt-time` **UserPromptSubmit hook** (`hooks/stamp-prompt-time.sh` in this repo), which stamps screenshot-related prompts with their submission time. It only fires when registered:

- **Marketplace install:** bundled via the plugin's `hooks/hooks.json` — active automatically.
- **Authoring machine (skills symlinked, plugin not installed):** register it in `~/.claude/settings.json` as a `UserPromptSubmit` hook pointing at `hooks/stamp-prompt-time.sh` (absolute path). The skill still works without it — it just falls back to the no-cutoff behavior in step 2.
