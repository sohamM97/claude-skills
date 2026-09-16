---
name: code-polish
description: Make a diff read the way a person wrote it, without changing behaviour. Removes Claude's writing tells from comments, docstrings, commit messages and short docs — comments that describe the diff instead of the code, unanchored "rather than", judgement adverbs (silently, deliberately), explained significance, borrowed metaphors (guard, seam, load-bearing), dated notes, dash asides and ", so" chains — and checks the code the diff introduces: names that name nothing, missing type hints, positional calls that should pass keywords, and missing or misshapen docstrings. Use before committing, when reviewing a diff, or when the user asks to clean up, de-slop, polish or humanise comments, names or commit messages.
argument-hint: "[report] [--range <a..b> | --files <paths>]"
---

# Make a diff read the way a person wrote it

Comments, docstrings and commit messages written with an assistant pick up the same habits
everywhere: they narrate, justify and decorate instead of saying what the code does. Across
several real codebases these habits appeared tens of times more often in assistant-written
comments than in comments people wrote by hand. This skill finds them and rewrites them.

**Scope.** Written text first: comments, docstrings, commit messages, and Markdown beside the
code. Then the code the diff introduces — its names, signatures and docstrings (see *Names*,
*Signatures and call sites*, *Docstrings*). Never change behaviour. This skill is self-contained;
for long documents (READMEs, design docs, blog posts), a general prose skill such as
`humanizer`, if installed, covers more.

## The standard

A comment is read by someone who has **only the current file**, with no memory of the change
and no view of the diff. It says what the code does, or why it does it that way. It does not
narrate how it got here, and it does not tell the reader how to feel about it.

Two tests, used as judgement rather than as bans:

1. **Would this sentence still be here if the writer were not trying to sound thorough or
   clever?** If it only explains, underlines or rounds off what the code or the previous
   sentence already says, cut it.
2. **Does the sentence carry a fact the reader can act on** — a name, a value, a condition, a
   consequence? If deleting it loses no fact, delete it.

## The tells, and what to write instead

| Tell | Example | Fix |
|---|---|---|
| **History in a comment** | `# no longer retries here`, `# used to be a list`, `// Bug fix: …` | State what the code does now. Before-and-after goes in the commit message. |
| **Unanchored comparison** | `# takes the id rather than a handle` | Keep a comparison only if the alternative is named and real in the same comment: `# a failed call is kept rather than dropped` passes. |
| **Judgement adverb** | `# fails silently`, `# deliberately not cached` | Say what happens: `# returns None without logging`, `# not cached: the value changes per request`. |
| **Explained significance** | `…, which is why this runs first.` `That is the whole point.` | Cut the closer. The reason, if needed, goes in one plain clause. |
| **Borrowed metaphor** | guard, seam, load-bearing, plumbing, hydrate, footgun, earns its keep | Name the thing — see the banned list below. |
| **Vague alternative** | `# use whichever client is configured` | Name the options: `# use the async client if AIO is set, else the sync one`. |
| **Dated note** | `# seen 2024-05-01`, `# for now` | The lasting fact stays; the date and the story go in the commit message. |
| **Dash aside** | `# retries — up to three times — then raises` | One aside per comment at most; usually two sentences read better. |
| **", so" chain** | `…, so the cache is cold, so the first call is slow` | One consequence per sentence. |

### Banned words, and what to write instead

These name an opinion of a thing instead of the thing. Banned outright in comments, docs,
commit messages and chat:

| banned | say what actually happens |
|---|---|
| plumbing | bookkeeping, the connecting steps, the parts nobody reads |
| load-bearing | why it matters: "every other check depends on it" |
| pre-flight | check it before the request |
| hydrate | fill in, load the values into |
| bake in | build it in, decide it at build time, hard-code |
| out of the box | with no configuration, by default |
| bites us | if this is wrong, X breaks — name X |
| spike | a small throwaway script that checks one thing |
| guard | the check that stops X — name what it stops |
| seam | where the two parts meet — name the argument, function or module |
| footgun, magic | say what goes wrong, or what the code does without being asked |

The general test: if a term needs the reader to have read the source to parse it, it belongs
in the source, not the explanation. A word that grades the thing ("critical", "elegant",
"hairy") instead of describing it is the same mistake.

**Words that are fine alone and wrong in bulk** — flag them when they cluster:

- *shape* (*the shape of it*, *that shape*) — say the fact it stands for.
- *half* standing for a named part (*the private half*) — name the part: *the private key*.
  Real fractions ("half the requests") are fine.
- *the whole of it* — *all of it*, *everything*, or give the total.
- *prose* meaning "text formatted some way" — say how: *sentences, no `Args:` section*.
- *which is exactly why…*, *that is exactly what…* — state the relationship plainly, or put the
  two facts side by side.

Frequency matters more than any single hit. One "rather than" that names a real alternative is
fine; five in a file is a habit. **Never fix a tell by swapping in a synonym** — "quietly" for
"silently" leaves the habit in place. Rebuild the sentence, or cut it.

## Docstrings

A docstring is written for the caller: what the function takes, returns and raises, and
anything surprising about calling it. Implementation reasoning goes in a comment beside the
lines it explains, where it cannot drift away from them. History and dated observations go in
the commit message. Length follows content: a one-line function usually needs a one-line
docstring, and a long one on a short function is usually carrying one of the above.

Check each one the diff writes or edits:

- **It is there.** Every function, class and module the diff adds gets one.
- **It is a one-line summary first**, then only the sections that carry something: no empty
  `Raises:`, and no `Returns:` on a function annotated `-> None`. Follow whatever docstring
  format the repo already uses; if it is Google style, give each argument's type in
  parentheses.
- **It says what, not how.** The test: would a caller call it differently for knowing this?
  If not, it is a comment belonging beside the lines it describes. A docstring "describes the
  function's calling syntax and its semantics, but generally not its implementation"
  (<https://google.github.io/styleguide/pyguide.html#s3.8.3-functions-and-methods>).
- **A module docstring says what the module is for**, not what one function in it does. If it
  reads like a description of a single job, it has drifted into being one function's docstring.
- **It does not restate the signature.** "Takes a path and returns a dict" adds nothing over
  `def load(path: Path) -> dict`. Say what the dict holds.

## Names

Identifiers carry the same habits, less often. For each function, method, class or variable
**the diff introduces**, check:

- **It names the operation** — returns, raises, stores, logs, sends. `record`, `handle` and
  `process` name nothing; `store_variable`, `log_failure`, `parse_header` do. This applies to
  a helper nested inside a function too: `decrypted(value)` says what comes back, `secret(value)`
  does not.
- **A variable or parameter is named for what it holds**, never for how it was got. `found`,
  `result`, `data` and `temp` name the act of getting; `missing_ids`, `parsed_rows` name the
  value. ("Names should be descriptive", section 3.16 of
  <https://google.github.io/styleguide/pyguide.html>.)
- **No metaphor from the banned list** — `check_duplicate_write`, not `write_guard`.
- **No history** — `new_parser`, `legacy_client`, `fetch_v2` rot the day the old one goes.
  Name what distinguishes it: `streaming_parser`, `sync_client`.

## Signatures and call sites

Two checks on the code the diff introduces, alongside whatever the repo's own rules say:

- **Every function the diff writes or edits is fully typed** — parameters and return, with
  `-> None` counting. Editing an untyped function means typing the whole signature, not only
  the parameter touched. Prefer builtin generics (`list[str]`, `tuple[int, str]`) and
  `Optional[X]` for what may be absent. Skip one parameter only for a reason nameable in a
  comment, such as a type whose import would cycle, and still write the return type.
- **Calls pass keyword arguments**: `send_message(channel=channel, body=text, retries=3)`,
  not `send_message(channel, text, 3)`. Positional is fine for a single argument whose meaning
  the function name already gives (`len(items)`, `str(error)`, `Path(name)`), and for a logging
  call's format arguments. A call of three or more positional arguments is the one to look at
  first: at the call site nothing says which is which.

Leave framework and language conventions alone: `handleClick` in React, `setUp` in unittest,
`__init__`, `get_queryset`. **Only rename a name the uncommitted diff introduces and nothing
else references yet** (grep for it first). For an established name — public API, serialised
fields, database columns, anything another file or repo uses — report the suggestion and stop.

## Commit messages

The subject says what changed. The body says why, and what a reviewer would not see in the
diff. Do not restate the diff as a bullet list, and do not end on a sentence about why the
change matters. History belongs here, which makes this the right home for what the comments
had to give up.

## Workflow

0. **Load the repo's own rules first.** Read the repository's `CLAUDE.md` (root and any in
   subdirectories you are touching) and every `.claude/rules/*.md` whose `paths:` cover the files
   in scope. Collect what they say about writing, comments and docstrings, including rules for
   the language of the files in scope (a docstring format such as Google style, type hints,
   how to cite another file), and any **mechanical check they define** (a grep to run on the
   diff, a list of words to look for). Run those checks alongside the scanner below and apply
   their rules alongside this skill's. Where the repo's rule and this skill disagree, the repo's
   rule wins; say so in the report. If the repo defines none, say that too.
1. **Find.** Run the scanner from this skill's directory on the scope the user asked for:
   ```bash
   python3 <skill-dir>/find_tells.py                      # uncommitted changes (default)
   python3 <skill-dir>/find_tells.py --range main..HEAD   # a branch's commits and messages
   python3 <skill-dir>/find_tells.py --files path/a.py    # whole files
   ```
   It lists added comment, docstring and doc lines that match each tell, with counts. The
   patterns are a floor, not the check: also read every added comment line in the diff and
   apply the two tests. The misses rarely contain a flagged word.
2. **Judge each hit in context.** Open the file, read the comment with the code it describes,
   and decide: keep, rebuild, or cut. Confirm any factual claim against the code before
   keeping or rewriting it; if you cannot confirm it, say so rather than restating it.
3. **Fix** — unless the user passed `report`, in which case list the proposed edits and stop.
   - Uncommitted changes: edit the comments in place.
   - Committed history: never rewrite history. Report, and offer a follow-up commit.
   - Commit messages: rewrite only a message that has not been pushed, and only if asked.
4. **Report**: which repo rules and checks were applied, then per file what was cut or rebuilt
   (before → after, briefly), what was kept on purpose and why, and the scanner's counts before
   and after.

## What to leave alone

- A comparison that names a real alternative, or explains a trade-off the reader needs.
- A project's own vocabulary and technical terms, even if they look like jargon.
- Quoted text: error messages, log strings, user-facing copy, test fixtures.
- Licence headers, generated files, vendored code.
- Where a repo's or user's `CLAUDE.md` sets a different rule, that rule wins.
