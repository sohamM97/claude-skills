#!/usr/bin/env python3
"""Lists writing tells in comments, docstrings, docs and commit messages.

Reads added lines only. With no arguments it scans the working tree against
HEAD (staged and unstaged). Every hit is a candidate for a person to judge, not
an error: some "rather than" lines justify a real design choice.

Usage:
    find_tells.py                     # uncommitted changes
    find_tells.py --range main..HEAD  # lines added by these commits, plus their messages
    find_tells.py --files a.py b.md   # whole files, every line counts as written text
"""

import argparse
import re
import subprocess
import sys
from collections import Counter

# Each entry: (name, pattern, what to do about it). Patterns match written text
# only, so a variable called `guard` in code is never counted.
TELLS = [
    ("history", r"\b(no longer|used to|previously|anymore|until now|the old|was changed|now uses|"
                r"CR-fix|bug ?fix:|fixed:)\b",
     "the comment describes the change, not the code: move it to the commit message"),
    ("comparison", r"\brather than\b|\binstead of\b|, not \w+|\bnot \w+(?: \w+){0,3},? but\b",
     "keep only if the alternative is named and real; otherwise say what the code does"),
    ("judgement adverb", r"\b(silently|quietly|deliberately|carefully|cleanly|gracefully|"
                         r"intentionally|simply|just|actually|exactly|really|basically)\b",
     "say what happens instead: 'returns None without logging', not 'fails quietly'"),
    ("significance", r"\b(which is why|that is why|this is why|that is what|this is what|"
                     r"this is where|the whole point|the key (?:is|here)|the trick|worth noting|"
                     r"importantly|crucially)\b",
     "cut the sentence that explains why the previous one matters"),
    ("metaphor", r"\b(load[- ]bearing|plumbing|pre-?flight|guards?|seams?|hydrat\w+|baked? in|"
                 r"out of the box|bites us|spike|footgun|magic|earns? its keep|for free|"
                 r"heavy lifting|under the hood)\b",
     "name the thing: 'the check that stops X', 'where module A calls B'"),
    ("bulk words", r"\b(shape|the \w+ half|halves|the whole of it|prose)\b|\bis exactly\b|"
                   r"\bwhich is exactly\b",
     "fine alone, wrong in bulk: say the fact the word stands for"),
    ("vague alternative", r"\b(whatever|whichever|as appropriate|accordingly|the relevant \w+)\b",
     "name the options being chosen between"),
    ("dated note", r"\b(seen|checked|as of|verified) (on )?\d{4}-\d{2}-\d{2}\b|\b(for now|currently|"
                   r"at the moment|these days)\b",
     "a date rots in a comment: move it to the commit message or state the lasting fact"),
    ("dash aside", r" — | -- ", "one aside per comment at most; a full stop usually reads better"),
    ("so-chain", r", so (the|a|an|it|this|that|we|each|any)\b",
     "one consequence per sentence"),
]

COMMENT_START = re.compile(r"^\s*(#|//|/\*|\*|--|<!--|;)")
TEXT_EXT = (".md", ".rst", ".txt")


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def written_lines_from_diff(diff: str):
    """Yields (file, line_no, text) for added lines that are comments, docstrings or docs."""
    path, line_no, in_doc = None, 0, False
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            path = raw[6:] if raw.startswith("+++ b/") else raw[4:]
            in_doc = False
            continue
        hunk = re.match(r"^@@ -\S+ \+(\d+)", raw)
        if hunk:
            line_no, in_doc = int(hunk.group(1)), False
            continue
        if not raw.startswith("+") or raw.startswith("+++"):
            if not raw.startswith("-"):
                line_no += 1
            continue
        text = raw[1:]
        quotes = text.count('"""') + text.count("'''")
        is_text = (path or "").endswith(TEXT_EXT)
        if is_text or in_doc or quotes or COMMENT_START.match(text):
            yield path, line_no, text.strip()
        if quotes % 2:
            in_doc = not in_doc
        line_no += 1


def commit_messages(rng: str):
    for sha in run(["git", "rev-list", rng]).split():
        body = run(["git", "log", "-1", "--format=%B", sha])
        for i, line in enumerate(body.splitlines(), 1):
            if line.strip() and not line.startswith("Co-Authored-By"):
                yield f"commit {sha[:8]}", i, line.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--range", help="commit range, e.g. main..HEAD")
    ap.add_argument("--files", nargs="+", help="scan whole files")
    args = ap.parse_args()

    if args.files:
        lines = [(f, i, l.strip()) for f in args.files
                 for i, l in enumerate(open(f, encoding="utf-8", errors="ignore"), 1)]
    elif args.range:
        lines = list(written_lines_from_diff(run(["git", "diff", "-U0", args.range])))
        lines += list(commit_messages(args.range))
    else:
        lines = list(written_lines_from_diff(run(["git", "diff", "-U0", "HEAD"])))

    counts: Counter[str] = Counter()
    for name, pattern, advice in TELLS:
        rx = re.compile(pattern, re.I)
        hits = [(f, n, t) for f, n, t in lines if rx.search(t)]
        if not hits:
            continue
        counts[name] = len(hits)
        print(f"\n== {name} ({len(hits)}) — {advice}")
        for f, n, t in hits[:40]:
            print(f"   {f}:{n}: {t[:110]}")
        if len(hits) > 40:
            print(f"   … {len(hits) - 40} more")
    print(f"\n{len(lines)} written lines scanned; "
          + (", ".join(f"{k} {v}" for k, v in counts.most_common()) or "no tells found"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
