---
name: bugfix
description: Create a Bugfix Branch. Use when the user wants to fix a bug or create a bugfix branch.
argument-hint: [short-name] [worktree]
---

# Create a Bugfix Branch

Create a `bugfix/<name>` branch from an up-to-date base branch.

## How this works

The branch-creation mechanics — base-branch selection, the workflow steps, and worktree
mode — live in the **`branch` skill**, which this skill shares with `/feature`. Invoke it
with the Skill tool (`branch`) and follow its instructions, with these overrides:

- **Prefix is pinned to `bugfix/`** — skip its "Choose the prefix" section and don't
  suggest alternatives. The branch is `bugfix/<name>`, kebab-case (e.g.
  `bugfix/stale-parent-data`, not `bugfix/staleParentData`).
- Skip its advice about redirecting to `/feature` or `/bugfix` — you're already here.
- Apply the **Arguments** and **Rules** below in place of the generic equivalents.

## Arguments

The user may provide a short bugfix name (e.g. `stale-parent-data`). If not provided, ask them for a brief name.

They may also pass **`worktree`** (anywhere in the arguments, e.g. `/bugfix stale-parent-data worktree`, or phrased as "in a worktree") to do the work in a separate git worktree instead of switching the current checkout. It is optional and **off by default** — if it isn't mentioned, create the branch in place as usual and don't ask about it. When it is given, strip the word from the bugfix name and follow the `branch` skill's **Worktree mode**.

## Rules

- Always branch from an up-to-date base branch.
- Once the branch (or worktree) is ready, ask the user what they'd like to do — describe the bug, enter plan mode, or just start working. Do NOT automatically enter plan mode or start writing code.
- **Plan mode:** follow the `branch` skill's "plan mode when it's earned" rule, plus one bug-specific trigger — a cause that isn't located yet is itself a reason to suggest planning, even if the eventual fix turns out to be small.
- **Bug fix code comments**: When adding code changes for bug fixes, include a comment documenting the exact bug — behaviour before the fix vs after the fix.
- **Confirm flow/functionality changes**: If the fix involves changing the flow or functionality itself (not just fixing broken code), always ask the user before implementing. Don't unilaterally make radical design decisions.
