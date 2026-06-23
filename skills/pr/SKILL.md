---
name: pr
description: Create Pull Request. Use when the user wants to create a PR (GitHub or Bitbucket) or is ready to open a pull request.
---

# Create Pull Request

Create a PR from the current branch to a target branch, on either **GitHub** or **Bitbucket** — auto-detected from the remote.

**Arguments:** `$ARGUMENTS` (optional: target branch name. If provided, skip the target-branch prompt below and use it directly.)

## Detect the platform

Run `git remote get-url origin` (fall back to `git remote -v`) and inspect the host:

- `github.com` → **GitHub**.
- `bitbucket.org` → **Bitbucket Cloud**.
- A self-hosted host → ask the user which platform it is, then follow the matching flow.

## Choose the target branch

If `$ARGUMENTS` was given, use it. Otherwise present these options to the user and let them pick (default to option 1):

1. **The branch the current branch was created from** (the parent). Detect it with:
   ```bash
   git show-branch -a 2>/dev/null \
     | grep '\*' \
     | grep -v "$(git rev-parse --abbrev-ref HEAD)" \
     | head -n1 \
     | sed 's/.*\[\(.*\)\].*/\1/; s/[\^~].*//'
   ```
   If this comes back empty or ambiguous, fall through to the options below.
2. **`develop` or `dev`** — whichever exists on the remote (`git ls-remote --heads origin develop dev`).
3. **`main` or `master`** — whichever is the repo's default branch (`git remote show origin | sed -n 's/.*HEAD branch: //p'`).

## Workflow (common)

1. Run `git status`. If there are uncommitted changes, stop and ask the user to commit first (suggest `/commit`).
2. Run `git log --oneline <target>..HEAD` to see all commits that will be in the PR. If there are none, say so and stop.
3. Run `git diff <target>...HEAD` to understand the full changeset.
4. Check if the current branch is on the remote. If not, push with `git push -u origin HEAD`.
5. Draft a PR title (short, under 70 chars) and a body summarizing **all** commits — not just the latest.
6. Create the PR using the platform's escalation ladder below.
7. Report the PR URL.

## Creating the PR — escalation ladder

For **both** platforms, try each rung in order and stop at the first that works:

**1. CLI** — try this first.
- **GitHub (strongly preferred):** if `gh` is installed (`command -v gh`) and authenticated, use it:
  ```bash
  gh pr create --base "<target>" --title "<title>" --body "$(cat <<'EOF'
  <body>
  EOF
  )"
  ```
  `gh` prints the PR URL on success. This is the primary path for GitHub — only fall through if `gh` is missing or not authenticated.
- **Bitbucket:** if a Bitbucket CLI such as `bb` is installed (`command -v bb`), use it:
  `bb pr create --source <branch> --destination <target> --title "<title>" --description "<body>"` (adjust flags to the installed CLI's `--help`).

**2. MCP** — if no CLI, check whether a matching MCP server is connected and use its create-PR tool.
- **GitHub:** look for a GitHub MCP server's `create_pull_request` (or equivalent) tool.
- **Bitbucket:** look for a Bitbucket MCP server's create-pull-request tool.
- Search the available MCP tools (e.g. via tool search for "pull request") before assuming none exists.

**3. API** — if no CLI and no MCP, use the REST API when credentials are available (never prompt for or paste secrets into chat; read them from `~/.netrc`, the platform CLI's auth, or env vars).
- **GitHub:** `gh api` if present, otherwise `curl` with a `GITHUB_TOKEN`:
  ```bash
  curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
    -X POST "https://api.github.com/repos/<owner>/<repo>/pulls" \
    -d '{"title":"<title>","head":"<branch>","base":"<target>","body":"<body>"}'
  ```
- **Bitbucket:** app password / API token in `~/.netrc` (machine `api.bitbucket.org`) or `BITBUCKET_USERNAME` / `BITBUCKET_APP_PASSWORD`:
  ```bash
  curl -sS -u "$BITBUCKET_USERNAME:$BITBUCKET_APP_PASSWORD" \
    -X POST "https://api.bitbucket.org/2.0/repositories/<workspace>/<repo_slug>/pullrequests" \
    -H "Content-Type: application/json" \
    -d '{"title":"<title>","description":"<body>","source":{"branch":{"name":"<branch>"}},"destination":{"branch":{"name":"<target>"}}}'
  ```
  Read the PR URL from `links.html.href` in the JSON response.

**4. Browser link (worst case)** — if none of the above are available, print the prefilled create-PR URL for the user to open, and tell them which auth to set up to automate it next time.
- **GitHub:** `https://github.com/<owner>/<repo>/compare/<target>...<branch>?expand=1`
- **Bitbucket:** `https://bitbucket.org/<workspace>/<repo_slug>/pull-requests/new?source=<branch>&dest=<target>`

## Rules

- Do NOT merge the PR. Only create it.
- Do NOT create a PR from a branch to itself (source and target must differ).
- If there are no commits ahead of the target branch, say so and stop.
- Never paste credentials into the chat transcript.
