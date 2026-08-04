---
name: feature
description: Start a New Feature. Use when the user wants to start a new feature or create a feature branch.
argument-hint: [short-name] [worktree]
---

# Start a New Feature

Create a `feature/<name>` branch from an up-to-date base branch.

## How this works

The branch-creation mechanics — base-branch selection, the workflow steps, and worktree
mode — live in the **`branch` skill**, which this skill shares with `/bugfix`. Invoke it
with the Skill tool (`branch`) and follow its instructions, with these overrides:

- **Prefix is pinned to `feature/`** — skip its "Choose the prefix" section and don't
  suggest alternatives. The branch is `feature/<name>`, kebab-case (e.g.
  `feature/pin-for-today`, not `feature/pinForToday`).
- Skip its advice about redirecting to `/feature` or `/bugfix` — you're already here.
- Apply the **Arguments** and **Rules** below in place of the generic equivalents.

## Arguments

The user may provide a short feature name (e.g. `pin-for-today`). If not provided, ask them for a brief name.

They may also pass **`worktree`** (anywhere in the arguments, e.g. `/feature pin-for-today worktree`, or phrased as "in a worktree") to do the work in a separate git worktree instead of switching the current checkout. It is optional and **off by default** — if it isn't mentioned, create the branch in place as usual and don't ask about it. When it is given, strip the word from the feature name and follow the `branch` skill's **Worktree mode**.

## Rules

- Always branch from an up-to-date base branch.
- Once the branch (or worktree) is ready: if the user already described the feature, start by exploring the relevant code to understand the current implementation — don't ask what to do next, and don't ask about plan mode as a reflex.
- **Plan mode:** follow the `branch` skill's "plan mode when it's earned" rule as-is — no reflex offer, but suggest it once you've explored enough to see the feature genuinely warrants one. Never enter plan mode unprompted.
- If no feature description was given, ask the user to describe what they want.
