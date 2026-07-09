# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Soham's personal collection of Claude Code **skills**, packaged as a **plugin marketplace** so they install on any machine via `/plugin marketplace add sohamM97/claude-skills` then `/plugin install soham@soham-skills`. There is no application code, build step, test suite, or linter — the repo is Markdown skill definitions plus one shell script and two JSON manifests.

## Architecture

Two-layer plugin-marketplace structure (`.claude-plugin/`):
- `marketplace.json` — the marketplace catalog. Declares one plugin, `soham`, sourced from `./`.
- `plugin.json` — the single plugin that bundles **every** skill under `skills/`.

Each subdirectory of `skills/` is one skill: a `SKILL.md` (required) plus any supporting files. Skills are discovered automatically from the directory — **adding a skill requires no manifest edits**. Installed skills are namespaced and invoked as `/soham:<skill>`.

Every `SKILL.md` starts with YAML frontmatter (`name`, `description`, optional `argument-hint`) followed by the instructions. The `description` is what Claude Code matches against to decide when to auto-invoke the skill, so it must name the triggering intent.

## Dual authoring/consuming model

- **Other machines** consume published skills via the marketplace commands above (`/plugin marketplace update soham-skills` to refresh).
- **The authoring machine** (Soham's primary) instead symlinks `~/.claude/skills/<skill>` → this repo's `skills/<skill>` via `./link-skills.sh`. Editing a skill at the user level therefore edits it here directly; publishing is just `git commit && git push`.

Run `./link-skills.sh` after cloning, moving the repo, or adding a new skill. It is idempotent: creates missing links, re-points stale ones (e.g. after a repo move), backs up a colliding real directory to `<name>.bak`, and never touches unrelated local-only skills. It honors `$CLAUDE_CONFIG_DIR` (defaults to `~/.claude`).

## Adding a new skill

1. Create `skills/<name>/SKILL.md` with frontmatter (`name`, `description`, optional `argument-hint`) and the instructions.
2. Add a brief section for the skill to `README.md` under "What's inside" — what it does and how to use it. **Do this whenever a skill is added, and update its README section whenever the skill's behavior changes.**
3. Ask the user before running `./link-skills.sh` — always confirm first, then run it (if approved) so the skill is live on the authoring machine.
4. `git commit && git push` to publish. No manifest changes needed.

## Conventions in the existing skills

These recur across the git-workflow skills (`feature`, `bugfix`, `commit`, `pr`) and are worth matching when editing or adding skills:

- **Never assume `main`.** Detect the base/target branch (default branch via `git remote show origin`, then `develop`/`dev`, then latest `release/*`), present only branches that actually exist as options, and let the user pick.
- **Branch naming:** `feature/<name>` and `bugfix/<name>`, kebab-case.
- **Commits:** stage files by name (never `git add -A`/`.`), never amend, never force-push, refuse secret-looking files.
- **Platform auto-detection:** the `pr` skill detects GitHub vs Bitbucket from the remote host and uses an escalation ladder (CLI first, e.g. `gh`).
- **`save`/`load`** persist per-branch WIP to the project's auto-memory as `wip_<branch-without-prefix>.md` so work resumes across sessions.
