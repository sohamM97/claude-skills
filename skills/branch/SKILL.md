---
name: branch
description: Create a Branch. Use when the user wants to start a new branch for some work but it isn't clearly a feature or a bugfix (e.g. a chore, refactor, experiment, docs, or hotfix), or when they just say "create a branch".
argument-hint: [short-name] [worktree]
---

# Create a Branch

Create a new branch from an up-to-date base branch.

This skill is the **shared implementation** of branch creation. `/feature` and `/bugfix`
delegate to it with the prefix pinned, so the base-branch selection, workflow and worktree
handling below are the single source of truth for all three. When invoked by one of those
skills, follow that skill's extra rules on top of these steps.

When invoked **directly**, it's the generic sibling of `feature` and `bugfix`: use it when
the work doesn't cleanly map to a feature or a bug fix, or when the user hasn't decided yet.
**If the work is clearly a new feature, prefer `/feature`. If it's clearly fixing a bug,
prefer `/bugfix`.** This skill is for everything else (or the not-yet-sure case).

## Arguments

The user may provide a short branch name (e.g. `tidy-logging`). If not provided, ask them
for a brief name (and, if you don't know it yet, what the branch is for).

They may also pass **`worktree`** (anywhere in the arguments, e.g. `/branch tidy-logging
worktree`, or phrased as "in a worktree") to do the work in a separate git worktree instead
of switching the current checkout. It is optional and **off by default** — if it isn't
mentioned, create the branch in place as usual and don't ask about it. When it is given,
strip the word from the branch name and follow **Worktree mode** below.

## When the work is a Jira issue

Applies whenever the user points at a Jira issue instead of (or as well as) giving a name —
a URL such as `https://automationedge.atlassian.net/browse/AELIS-1798`, or a bare key such as
`AELIS-1798`. The **issue key** is the last path segment of a `/browse/` URL, so it can always
be read off the link without opening anything.

### Name the branch after the issue

`<prefix>/<ISSUE-KEY>-<short-description>`, for example:

```
bugfix/AELIS-1798-conv-dialog-state-undefined
feature/AELIS-1642-per-tool-approval
```

- The prefix is unchanged — `/feature` still produces `feature/…`, `/bugfix` still produces
  `bugfix/…`. The key goes between the prefix and the description.
- Keep the key in **capitals**, exactly as Jira writes it. This is the single exception to the
  kebab-case rule, because the key is an identifier people search for.
- The description is a **short paraphrase you write** — three or four words — not the Jira
  summary copied out. AELIS-1798's summary is "Not able to store in conv and dialog state";
  the paraphrase is `conv-dialog-state-undefined`.
- If the user gave their own name alongside the issue, keep theirs and just insert the key.

### Read the issue before you name it

You cannot paraphrase an issue you have not read. Try these in order, stopping at the first
that works.

1. **The Atlassian MCP server**, when its tools are connected: `mcp__atlassian__getJiraIssue`.
   Pass the site hostname as `cloudId` (e.g. `automationedge.atlassian.net`) and ask for the
   `summary`, `description`, `issuetype`, `fixVersions`, `attachment` and `comment` fields.
2. **A REST call**, when the MCP server is not connected. Jira Cloud accepts basic auth with an
   Atlassian account email plus an API token —
   <https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/>:

   ```bash
   curl -n -H "Accept: application/json" \
     "https://<site>.atlassian.net/rest/api/3/issue/<KEY>?fields=summary,description,issuetype,fixVersions,attachment"
   ```

   `-n` takes the credentials from `~/.netrc`, so no token is typed on the command line. It
   needs a line `machine <site>.atlassian.net login <email> password <api-token>` in that file.

   **A Bitbucket API token will not work for Jira.** With one, `/rest/api/3/myself` answers
   `401 Client must be authenticated to access this resource.` and the issue endpoint answers
   `404 {"errorMessages":["Issue does not exist or you do not have permission to see it."]}`.
   That 404 looks like a wrong issue key but means the token lacks Jira access. On either
   response, don't retry or hunt for another key — say which one you got and drop to step 3.
   Jira tokens are created at <https://id.atlassian.com/manage-profile/security/api-tokens>;
   suggest adding one to `~/.netrc` so the next run works.
3. **The user's latest screenshot.** They often have the issue open on screen and screenshot it
   for you rather than granting API access. Run the `check-screenshot` skill and read the
   ticket off the image.
4. **Ask the user** to paste the summary. You can still create the branch from the key alone in
   the meantime — `bugfix/AELIS-1798` — and rename it once you know more (`git branch -m`).

### Look at the attachments

Bug reports carry screenshots that say more than the description does. When step 1 or 2 worked,
each entry in the issue's `attachment` array has a `content` URL. Download the images into the
session scratchpad and **Read** them — the Read tool displays images:

```bash
curl -n -L -o <scratchpad>/<filename> "<attachment content URL>"
```

Keep Jira's own filenames so you can name which image you are describing. Skip files that
aren't images (check `mimeType`) unless they're clearly relevant.

### Check the issue type against the command

If the Jira issue type contradicts the skill that was invoked — `/bugfix` on a Story, or
`/feature` on a Bug — **stop and ask** before creating anything. Name the actual issue type and
offer both options: keep the prefix that was typed, or switch to the other skill. Don't pick
one silently.

## Choose the prefix

**Skip this section entirely when a calling skill has pinned the prefix** (`/feature` →
`feature/`, `/bugfix` → `bugfix/`).

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

**A Jira fix version changes which option is the default — it never skips the question.**
When the issue was read successfully and its `fixVersions` names a version, look for a branch
called `release/<version>` — fix version `3.8.0` → `release/3.8.0`. If that branch exists, put
it first in the list and mark it as the recommended option, saying where the recommendation
came from. **Still ask**, with `AskUserQuestion`, exactly as you would without a Jira issue: a
matching release branch is a strong hint about intent, not a decision. If the branch does
**not** exist, say so plainly rather than staying silent — "AELIS-1798 targets 3.8.0, but there
is no `release/3.8.0` branch" — and let the normal default, the current branch, lead the list.
An issue with several fix versions, or none, changes nothing: use the normal default and
mention what you found.

## Workflow

1. **Check for an existing branch first.** Run `git branch -a | grep -i <name>` to see if a branch with that name (or similar) already exists locally or on the remote. If it does, ask the user if they want to switch to it (and rebase onto `<base>`) instead of creating a new one.
2. Check that you're on the `<base>` branch. If not, ask the user if they want to switch to `<base>` first (there may be uncommitted work).
3. Run `git status` to check for uncommitted changes. If there are any, **stop** and tell the user to commit first (or offer to run `/commit`).
4. Update `<base>` with `git pull` (skip if there's no remote / upstream).
5. Create and switch to the new branch `<branch>` (e.g. `chore/tidy-logging`). Use kebab-case for the name.
6. Confirm the branch was created successfully. Then follow the calling skill's next-step rule, if any. Otherwise ask the user what they'd like to do — describe the work, enter plan mode, or just start working. If the user already described the work alongside the command, start exploring the relevant code instead of asking what to do next.

## Worktree mode

Only when the user asked for `worktree`. The base-branch choice above still applies — pick `<base>` exactly the same way. Steps 2–5 of the workflow are replaced by the following; step 1 (existing-branch check) and step 6 still apply.

1. Uncommitted changes in the current checkout are **fine** here — the worktree gets its own working directory, so nothing needs committing first. Don't block on `git status`.
2. Refresh the base: `git fetch origin <base>` (skip if there's no remote). Use `origin/<base>` as the start point when a remote exists, otherwise the local `<base>`.
3. Create the worktree and branch in one go, from the repo root:
   ```bash
   git worktree add .claude/worktrees/<name> -b <branch> origin/<base>
   ```
   `.claude/worktrees/` is the location Claude Code expects. If `.claude/worktrees/` isn't already ignored, add it to `.git/info/exclude` (a local-only ignore — don't touch the repo's committed `.gitignore` unless the user asks).
4. Switch the session into it with the **EnterWorktree** tool, passing `path: .claude/worktrees/<name>` (pass the path, not `name` — that would create a second worktree off the wrong base and ignore the branch naming).
5. Tell the user where the worktree lives and that the original checkout is untouched. Note that `ExitWorktree` with `keep` returns to the original directory and leaves the work on disk; `remove` deletes the worktree and its branch.

If a worktree for this branch already exists (`git worktree list`), enter that one instead of creating a duplicate.

## Rules

- Branch names must be kebab-case (e.g. `chore/tidy-logging`, not `chore/tidyLogging`). The
  one exception is a Jira issue key, which keeps its capitals — see **When the work is a Jira
  issue** for the full form, `bugfix/AELIS-1798-conv-dialog-state-undefined`.
- Always branch from an up-to-date base branch.
- **The base branch is always the user's choice.** Ask with `AskUserQuestion` every time, even
  when something in the repo or the Jira issue points strongly at one branch. Those signals
  decide which option is recommended and listed first, never whether to ask.
- Suggest a prefix, but never force one — the user may override it or choose no prefix.
  (Not applicable when a calling skill pinned the prefix.)
- If the work turns out to be a clear feature or bug fix, point the user to `/feature` or
  `/bugfix` (whose conventions — e.g. bug-fix before/after comments — are more specific).
  Skip this when you were invoked *by* one of those skills.
- Don't automatically enter plan mode or start writing code unless the user already
  described the work. Otherwise wait for them to describe what they want. A calling skill
  may override this.
- **Plan mode when it's earned.** If the user did describe the work, don't ask about plan
  mode as a reflex — but once you've explored enough to judge the size, suggest it if the
  work genuinely warrants it: it spans several files or subsystems, there are real design
  choices to settle, or the approach isn't obvious from the code. Say briefly *why* and let
  the user decide. For a small, obvious change, skip the offer and just do the work.
