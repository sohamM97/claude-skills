---
name: check-screenshot
description: Check Latest Screenshot. Use when the user mentions screenshots, says "look at this", or wants to show something on screen.
---

# Check Latest Screenshot

Read the most recent screenshot(s) and describe what's in them.

## Arguments

- Optional: a number N to check the N most recent screenshots (default: 1).
- Optional: `whatsapp` — check WhatsApp images instead of system screenshots.

## Workflow

1. Check auto-memory for the relevant directory path:
   - Default: screenshots directory (e.g. `~/Pictures/Screenshots/`)
   - With `whatsapp` argument: WhatsApp images directory (e.g. `~/Downloads/`)
   - If not found in memory, ask the user where the images are saved, then save to memory for future use.
2. List files in the directory sorted by modification time (newest first).
   - For WhatsApp: filter to image files only (`.jpeg`, `.jpg`, `.png`).
3. Read the latest screenshot(s) using the Read tool (it supports images).
4. Describe what you see — focus on anything relevant to the current task or conversation.
5. If the user seems to be showing a bug or UI issue, call it out specifically.

## Rules

- If the directory is empty or doesn't exist, tell the user.
- Always mention the filename and timestamp so the user knows which screenshot you're looking at.
- Don't make assumptions about what the user wants — describe what you see and ask if they need something specific.
- When the user says "check latest whatsapp screenshot" or similar, use the WhatsApp directory.
