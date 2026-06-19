---
name: load
description: Check what saved work is pending across branches. Optionally filter by branch name.
argument-hint: "[optional branch name]"
---

# Load Progress

Show pending/in-progress work saved by `/save`. If a branch name is given, show that branch's WIP. Otherwise, show all WIP across all projects.

## Workflow

1. **Determine scope** based on the argument:
   - **Branch name given:** Find the matching `wip_*.md` file in the current project's memory directory. The branch name can be partial — e.g. `efs` matches `wip_efs_access_mode_rwx.md`.
   - **No argument:** Find ALL `wip_*.md` files and TODO/pending items in the **current project's** memory directory only. Also check MEMORY.md for any pending plans or TODOs tracked there.

2. **Read each matching WIP file** and extract:
   - Branch name
   - One-line description (from frontmatter `description:`)
   - What's done vs still TODO
   - How to resume

3. **Present a summary** to the user:
   - If showing multiple items, show a table/list with: **Branch/Item**, **Status** (one-line description), and **Next step** (from "How to apply" or "Still TODO").
   - If showing a single branch, display the full WIP content in a readable format.

4. **Check staleness** — for each WIP in the current project, run `git branch --list '<branch-name>'` to check if the branch still exists locally. If a branch has been deleted, flag the WIP as potentially stale.

## Rules

- This is a read-only skill — never modify any files.
- If no WIP files are found, say so clearly and suggest using `/save` to start tracking work.
- Keep output concise — the user wants a quick overview, not a wall of text.
- For the "Project" column, convert the directory name to something readable (e.g. `-home-soham-projects-personal-app` → `personal-app`).
- When a branch name argument matches multiple WIP files, show all matches.
