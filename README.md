# claude-skills

Soham's personal collection of [Claude Code](https://code.claude.com) skills, packaged as a **plugin marketplace** so they install cleanly on any machine (macOS, Linux, and Windows).

## Install

In Claude Code:

```text
/plugin marketplace add sohamM97/claude-skills
/plugin install soham@soham-skills
```

The skills are namespaced under the plugin name, so invoke them as `/soham:<skill>`
(run `/help` to see the full list after installing).

### Update later

When new skills are pushed here, refresh on each machine with:

```text
/plugin marketplace update soham-skills
```

## What's inside

Each folder under [`skills/`](./skills) is one skill (a `SKILL.md` plus any
supporting files). New skills added to that directory are picked up
automatically — no manifest changes needed.

The skills currently bundled:

- **`feature`** — start a new feature. Creates a `feature/<name>` branch from an
  up-to-date base branch (it detects candidate bases and lets you pick). Run
  `/soham:feature <short-name>`; if you describe the feature too, it dives
  straight into the code.
- **`bugfix`** — create a `bugfix/<name>` branch the same way `feature` does,
  then waits for you to describe the bug. Bug-fix edits get a comment documenting
  the behavior before vs. after the fix. Run `/soham:bugfix <short-name>`.
- **`branch`** — the generic sibling of `feature`/`bugfix`, for work that isn't clearly
  either (chore, refactor, hotfix, docs, experiment…). Suggests a fitting prefix (which you
  can override or drop), then creates the branch from an up-to-date base the same way.
  Run `/soham:branch <short-name>`.
- **`commit`** — stage the current changes (by name, never `git add -A`), write a
  concise "why"-focused message, and push to the current branch. Never amends or
  force-pushes, and skips secret-looking files. Run `/soham:commit`.
- **`pr`** — open a pull request from the current branch. Auto-detects GitHub vs.
  Bitbucket from the remote, lets you choose the target branch, and summarizes all
  commits in the PR. Run `/soham:pr [target-branch]`.
- **`save`** — snapshot the current branch's progress (done / TODO / decisions) to
  per-branch WIP memory so a later session can resume it. Run
  `/soham:save [summary]`.
- **`load`** — show pending work saved by `save`, across all branches or filtered
  to one. Read-only. Run `/soham:load [branch-name]`.
- **`check-screenshot`** — read and describe your most recent screenshot(s), or
  WhatsApp images with the `whatsapp` argument. Picks the screenshot(s) that were
  newest **when you sent the message** (not any that arrived while Claude was
  busy) — see the `stamp-prompt-time` hook below. Run
  `/soham:check-screenshot [N] [whatsapp]`.

## Hooks

- **`stamp-prompt-time`** (`hooks/stamp-prompt-time.sh`, a `UserPromptSubmit`
  hook) — stamps screenshot-related prompts with their submission time so
  `check-screenshot` can ignore screenshots that landed *after* your message.
  Claude Code doesn't expose per-message timestamps otherwise, and `date` inside
  a skill is the run time, not the send time. Registered two ways:
  - **Marketplace install:** auto-loaded from `hooks/hooks.json` (plugin hooks
    fire only when the plugin is installed).
  - **Authoring machine** (skills symlinked, plugin not installed): hooks aren't
    activated by symlinking — Claude Code only loads them from a settings file or
    an installed plugin. So `./link-skills.sh` **registers the hook in
    `~/.claude/settings.json`** for you (idempotent; needs `jq`). Restart Claude
    Code to activate it. The skill degrades gracefully without it.

## Repository layout

```text
.
├── .claude-plugin/
│   ├── marketplace.json   # marketplace catalog (this repo is a marketplace)
│   └── plugin.json        # the single plugin that bundles all skills
├── hooks/
│   ├── hooks.json         # plugin hook registrations (auto-loaded on install)
│   └── stamp-prompt-time.sh
└── skills/
    └── <skill-name>/
        └── SKILL.md
```

## Authoring

You can author skills on any Linux machine if you like. On a machine set up for
authoring, `~/.claude/skills/<skill>` is a symlink into this repo's `skills/`
directory. That means editing a skill at the user level edits it here directly —
just `git commit && git push` to publish. Machines that aren't set up this way
consume the published versions via the marketplace commands above.

To set up (or refresh) the symlinks — run this after cloning, moving the repo,
or adding a new skill. It is idempotent, and also registers the
`stamp-prompt-time` hook in `~/.claude/settings.json` (see [Hooks](#hooks)):

```bash
./link-skills.sh
```

Restart Claude Code afterwards so the newly-registered hook takes effect.
