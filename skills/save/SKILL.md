---
name: save
description: Save progress on the current branch to memory so work can be resumed in a new session.
argument-hint: "[optional summary]"
---

# Save Progress

Save a snapshot of the current branch's progress to auto-memory so a future session can pick up where we left off.

## Workflow

1. **Gather context** — run these in parallel:
   - `git branch --show-current` to get the branch name
   - `git log main..HEAD --oneline` to see commits on this branch (use `main` as base; if that fails, try `master`)
   - `git status` to see uncommitted changes
   - `git diff --stat` to see what files are modified but not committed
   - Check if a `wip_*.md` memory file already exists for this branch (glob for `wip_*.md` in the project memory directory)

2. **Review conversation context** — look back through the conversation to identify:
   - What was accomplished this session
   - What is still TODO / next steps
   - Any design decisions made or pending
   - Any gotchas or blockers discovered

3. **Write or update the WIP memory file** in the project's auto-memory directory:
   - File name: `wip_<branch-name-without-prefix>.md` (e.g. branch `feature/reserved-slot` → `wip_reserved_slot.md`, branch `bugfix/stale-icon` → `wip_stale_icon.md`)
   - If a WIP file already exists for this branch, **update it** rather than creating a new one
   - Use this structure:

   ```markdown
   ---
   name: WIP <short feature/fix name>
   description: <one-line description of what this branch does and current status>
   type: project
   ---

   ## Branch: `<full branch name>`

   ### Problem
   <What problem is this branch solving? 1-3 sentences.>

   ### Done
   <Bullet list of what's been completed. Include commit hashes where helpful.>

   ### Uncommitted Changes
   <If any uncommitted work exists, describe it. Otherwise omit this section.>

   ### Still TODO
   <Bullet list of remaining work items.>

   ### Design Decisions
   <Any decisions made or pending. Omit if none.>

   ### Gotchas / Notes
   <Anything a future session should know. Omit if none.>

   **How to apply:** <One line on how to resume — e.g. "Continue on this branch. Next step is X.">
   ```

4. **Offer to commit** — if `git status` from step 1 showed uncommitted changes (staged or unstaged), ask the user: "You have uncommitted changes — would you like me to `/commit` them as well?" Only run `/commit` if they say yes. If there are no uncommitted changes, skip this step silently.

5. **Update MEMORY.md** — add or update a `See wip_<name>.md` pointer line in MEMORY.md if one doesn't already exist.

6. **Confirm to the user** — report what was saved and where.

## Rules

- If the user provides an optional summary argument, use it to inform the "Done" and "TODO" sections rather than asking questions.
- If the conversation has very little context (e.g. user just opened a session and ran `/save` immediately), check git log and diff to infer progress, and ask the user what the remaining TODOs are.
- Do NOT save ephemeral details like test output or debug logs — focus on actionable state.
- Do NOT duplicate information already in CLAUDE.md or commit messages — reference commits instead.
- Keep the file concise. A future Claude session should be able to read it in 30 seconds and know exactly where to pick up.
- When updating an existing WIP file, preserve any still-relevant content and clearly mark what changed.
