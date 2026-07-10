---
name: branch
description: Create a Branch. Use when the user wants to start a new branch for some work but it isn't clearly a feature or a bugfix (e.g. a chore, refactor, experiment, docs, or hotfix), or when they just say "create a branch".
argument-hint: [short-name]
---

# Create a Branch

Create a new branch from an up-to-date base branch. This is the generic sibling of
`feature` and `bugfix`: use it when the work doesn't cleanly map to a feature or a bug
fix, or when the user hasn't decided yet.

**If the work is clearly a new feature, prefer `/feature`. If it's clearly fixing a bug,
prefer `/bugfix`.** This skill is for everything else (or the not-yet-sure case).

## Arguments

The user may provide a short branch name (e.g. `tidy-logging`). If not provided, ask them
for a brief name (and, if you don't know it yet, what the branch is for).

## Choose the prefix

Since the work isn't a clear feature/bugfix, pick a prefix that fits its purpose. Suggest
one based on what the user described, and let them confirm or override. Common conventions:

- `chore/` — maintenance, dependency bumps, config, tooling.
- `refactor/` — restructuring code without changing behaviour.
- `hotfix/` — urgent fix meant to go straight to production/release.
- `docs/` — documentation-only changes.
- `experiment/` or `spike/` — throwaway/exploratory work.
- `test/` — adding or fixing tests only.
- `feature/` or `bugfix/` — if it turns out to be one of these after all, say so and
  suggest switching to the `/feature` or `/bugfix` skill instead.

If none fit, the user can type any custom prefix, or choose **no prefix** (a bare
kebab-case branch name). Whatever is chosen, combine it with the kebab-case name to form
the full branch, e.g. `chore/tidy-logging`. Use that as `<branch>` everywhere below.

## Choose the base branch

Don't assume `main`. Detect which candidate branches exist (local or remote) and present the ones that are present as options, letting the user pick. Default to option 1.

1. **The currently checked-out branch** — `git rev-parse --abbrev-ref HEAD`. This is the default: branch off wherever the user already is. **If it is not `main`/`master`, `develop`/`dev`, or a `release/` branch** (i.e. it's some other branch such as an existing `feature/`/`bugfix/` branch), call that out explicitly so the user consciously confirms they want to stack this branch on top of it rather than start from the default branch.
2. **The repo's default branch** — `main` or `master`. Detect with:
   ```bash
   git remote show origin 2>/dev/null | sed -n 's/.*HEAD branch: //p'
   ```
   If empty (no remote / offline), fall back to whichever of `main` or `master` exists locally (`git branch --list main master`), preferring `main`.
3. **`develop` or `dev`** — whichever exists (`git branch -a --list '*develop' '*dev'`).
4. **The most recent `release/` branch**, if any exist — list with `git branch -a --list '*release/*'` and offer the latest (sort by version/date).
5. **Something else** — let the user type a branch name.

Only show an option if that branch actually exists, and don't list the same branch twice (e.g. if the current branch is already `main`, options 1 and 2 collapse into one). Use the chosen branch as `<base>` everywhere below.

## Workflow

1. **Check for an existing branch first.** Run `git branch -a | grep -i <name>` to see if a branch with that name (or similar) already exists locally or on the remote. If it does, ask the user if they want to switch to it (and rebase onto `<base>`) instead of creating a new one.
2. Check that you're on the `<base>` branch. If not, ask the user if they want to switch to `<base>` first (there may be uncommitted work).
3. Run `git status` to check for uncommitted changes. If there are any, **stop** and tell the user to commit first (or offer to run `/commit`).
4. Update `<base>` with `git pull` (skip if there's no remote / upstream).
5. Create and switch to the new branch `<branch>` (e.g. `chore/tidy-logging`). Use kebab-case for the name.
6. Confirm the branch was created successfully. Then ask the user what they'd like to do — describe the work, enter plan mode, or just start working. If the user already described the work alongside the command, start exploring the relevant code instead of asking what to do next.

## Rules

- Branch names must be kebab-case (e.g. `chore/tidy-logging`, not `chore/tidyLogging`).
- Always branch from an up-to-date base branch.
- Suggest a prefix, but never force one — the user may override it or choose no prefix.
- If the work turns out to be a clear feature or bug fix, point the user to `/feature` or
  `/bugfix` (whose conventions — e.g. bug-fix before/after comments — are more specific).
- Don't automatically enter plan mode or start writing code unless the user already
  described the work. Otherwise wait for them to describe what they want.
