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

## Repository layout

```text
.
├── .claude-plugin/
│   ├── marketplace.json   # marketplace catalog (this repo is a marketplace)
│   └── plugin.json        # the single plugin that bundles all skills
└── skills/
    └── <skill-name>/
        └── SKILL.md
```

## Authoring (Soham's primary machine only)

On the machine where these are developed, `~/.claude/skills/<skill>` is a
symlink into this repo's `skills/` directory. That means editing a skill at the
user level edits it here directly — just `git commit && git push` to publish.
Other machines consume the published versions via the marketplace commands above.

To set up (or refresh) the symlinks — run this after cloning, moving the repo,
or adding a new skill. It is idempotent:

```bash
./link-skills.sh
```
