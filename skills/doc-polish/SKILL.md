---
name: doc-polish
description: Restructure a design doc, investigation write-up or analysis so its main point is not buried, and hold its wording to the code-polish skill's language rules. Moves code samples, internal file paths and chains of function names out of the main text into a numbered Notes section, keeps the experiment code that shows how a result was measured, labels each claim as measured, read in the source or estimated, and fixes the layout problems that break rendering (footnote syntax, a table with no blank line after it, letters reused for two things). Use when a doc reads as a wall of code and internal names, after a doc has grown through many rounds of edits, or when the user says a doc "detracts from the point", is "too much", or asks to clean up, restructure or polish a doc.
argument-hint: "<path to the doc> [report]"
---

# Keep a doc's main point in front

A doc written over many rounds of questions collects every code sample read, every internal
function on the path and every detail that answered a side question. Each addition was useful
when it was made. Together they bury the doc's finding. This skill reorders the doc so a reader
gets the finding first, and finds the detail when they want it.

**Scope.** Structure, evidence and wording. The wording follows the `code-polish` skill's
language rules in full: its table of tells, its banned and soft-banned words, its referent
checks and its scanner. Read `../code-polish/SKILL.md` before starting, and apply its rules to
every sentence this skill writes or keeps, and to every note it creates.

## The standard

A reader opening the doc should learn what it found in the first screen, with no code to read
and no internal names to look up. The code, links and derivations that prove or explain a
finding stay in the doc, one click away.

The test for each paragraph, table and code block in the main text: **does the reader need
this to follow the doc's argument?** If they need it only to check the argument, or to find the
code, it goes to a note.

## What goes where

| Kind of content | Main text | A note at the end |
|---|---|---|
| The finding, in plain words | yes | no |
| A table of results, or of cases and the outcome of each | yes | no |
| The experiment code that produced the results (a counter, a timing script) | yes: it shows how the numbers were got | no |
| A worked example with concrete inputs and outputs | yes | no |
| Source code of a library or framework | no | yes, with a link to the file |
| The project's own implementation code | no, unless the doc is about that code | yes |
| Internal file paths, private method names | no | yes |
| A chain of calls (`a` calls `b`, which calls `c`) | no: say the event in plain words | yes, the chain |
| The steps that derived a number | no: give the number | yes |

**Experiment code is the exception.** Code that shows how a result was measured is evidence
the reader needs to trust the numbers. It stays in the main text. Library source that explains
the cause of a result is detail, and goes to a note.

**Say an event in plain words.** "The service loads the snapshot once, then saves after every
step" is the main text. "`Runner.restore()` calls `Store.load()`, then `State.clear()` and
`State.import()`" is the note.

## Notes, not footnotes

Markdown footnotes (`[^name]`) do not render in every viewer: VS Code's built-in preview shows
`[^name]` as plain text. Use a plain section instead, which renders everywhere:

```markdown
The cache is read once per request.[[3]](#3-cache-reads)

## Notes

### 3. Cache reads

…the detail, the code sample and the link…
```

- Number the notes in the order the main text first refers to them.
- Keep each note's heading free of backticks and punctuation, so its anchor is predictable:
  `### 3. Cache reads` → `#3-cache-reads`. Heading ids differ between renderers, so check a
  link in the viewer the doc is read in.
- When one note covers a second reference, link the second one to it rather than numbering a
  new note and renumbering the rest.

## Evidence

A doc that reports what a system does must say how each claim is known.

- **Label every claim** as one of: measured (a test or script ran and its output is quoted),
  read in the source, or estimated. Never let an estimate read like a measurement.
- **Measure the thing the doc is about.** A doc about database calls counts statements on a
  real database, not calls on an in-memory stand-in. If a stand-in was used, say so and say
  what it cannot show.
- **Quote the output.** Paste the timeline or the counts the run printed, trimmed, with a
  comment on each line saying what it is.
- **Point at a test that keeps the claim true**, when there is one, by its name. A script that
  lived in `/tmp` is gone after a reboot; move the check into the repo's tests or say it was
  run once, and when.
- **Never present proposed code as what ran.** If a snippet shows a design that was not
  executed, label it as a proposal, and show the code that ran beside it.

## Layout faults that break reading

- **A table needs a blank line after it.** Without one, the next paragraph is drawn as more
  table rows.
- **Narrow cells wrap into noise.** A column that only says "as A" in every row should be
  merged into the column it repeats: "Approaches A and C".
- **One letter, one meaning.** If the doc compares approaches A, B and C, do not also call a
  count C or a node A. Rename the count (K) or the nodes (`n1`, `n2`). Check every single
  letter and short name the doc introduces.
- **Lead each section with its conclusion,** then the table or example that supports it.

## Workflow

1. **Read the whole doc first.** Write down, in one sentence, what it is for. Every section
   is judged against that sentence.
2. **List what is in the main text** that fails the standard: code samples, internal paths,
   call chains, derivations, unlabelled claims.
3. **Move each to a note**, or cut it if nothing refers to it. Keep experiment code in place.
4. **Rewrite the sentence left behind** in plain words, with a link to the note.
5. **Check the evidence**: every claim labelled, every number traced to a run or marked as
   estimated, no proposal shown as executed code.
6. **Check the layout faults** above, and render the doc in the viewer it is read in.
7. **Apply `code-polish`'s language rules.** Run its scanner on the doc,
   `python3 <skills-dir>/code-polish/find_tells.py --files <doc>`, judge each hit, and read
   every sentence the scanner does not flag against its tells, banned words and referent
   checks. Load the repo's own writing rules first, as `code-polish` does; where they
   differ, the repo's rules win.
8. **Report** what moved to which note, what was cut, what was kept on purpose and why.
   With the `report` argument, list the proposed changes and stop.

## What to leave alone

- A TODO or note the user wrote in their own words, for example a reminder to write a summary.
- Code the doc is about, when the doc is a guide to that code.
- Quoted output: trim it, but never edit what it says.
