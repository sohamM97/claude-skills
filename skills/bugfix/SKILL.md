---
name: bugfix
description: Create a Bugfix Branch. Use when the user wants to fix a bug or create a bugfix branch.
---

# Create a Bugfix Branch

Create a `bugfix/<name>` branch from an up-to-date default branch.

## Arguments

The user may provide a short bugfix name (e.g. `stale-parent-data`). If not provided, ask them for a brief name.

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

1. **Check for an existing branch first.** Run `git branch -a | grep -i <name>` to see if a `bugfix/<name>` branch (or similar) already exists locally or on the remote. If it does, ask the user if they want to switch to it (and rebase onto `<base>`) instead of creating a new one.
2. Check that you're on the `<base>` branch. If not, ask the user if they want to switch to `<base>` first (there may be uncommitted work).
3. Run `git status` to check for uncommitted changes. If there are any, **stop** and tell the user to commit first (or offer to run `/commit`).
4. Update `<base>` with `git pull` (skip if there's no remote / upstream).
5. Create and switch to a new branch: `bugfix/<name>` (e.g. `bugfix/stale-parent-data`). Use kebab-case for the name.
6. Confirm the branch was created successfully. Then ask the user what they'd like to do — describe the bug, enter plan mode, or just start working.

## Rules

- Branch names must use `bugfix/` prefix with kebab-case (e.g. `bugfix/stale-parent-data`, not `bugfix/staleParentData`).
- Always branch from an up-to-date base branch.
- Do NOT automatically enter plan mode or start writing code. Wait for the user to describe what they want.
- **Bug fix code comments**: When adding code changes for bug fixes, include a comment documenting the exact bug — behaviour before the fix vs after the fix.
- **Confirm flow/functionality changes**: If the fix involves changing the flow or functionality itself (not just fixing broken code), always ask the user before implementing. Don't unilaterally make radical design decisions.
