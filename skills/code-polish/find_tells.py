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
import ast
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
    ("unnamed set", r"\b(everything|anything)\b|\ball of it\b",
     "name the members, or give the set a name of its own"),
    # Bare "what" and "where" are ordinary English, so only the constructions
    # that stand in for a named thing are matched.
    ("vague pointer", r"\bis what\b|\bsays what\b|\bwhat goes\b|\bwhat the \w+ (?:does|shows|is)\b|"
                      r"\bwhat is (?:stored|sent|returned|passed|configured|set)\b|"
                      r"\bwhere the \w+ (?:is|are|lives?|goes)\b|\bwhat comes back\b",
     "name the thing: 'the deployment name is sent', not 'is what goes on the request'"),
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


def docstring_problems(paths):
    """Structural faults in the docstrings of Python files.

    Regex cannot see a missing `Args:` section, so the sections are compared
    against each signature instead. Google lets both sections go "in cases
    where the function's name and signature are informative enough that it can
    be aptly described using a one-line docstring", which is approximated here
    as: at most one parameter, and that one annotated.

    Args:
        paths (list[str]): The files to parse. A file that will not parse is
            skipped.

    Yields:
        tuple[str, int, str]: The file, the line, and the fault.
    """
    for path in paths:
        if not path.endswith(".py"):
            continue
        try:
            tree = ast.parse(open(path, encoding="utf-8", errors="ignore").read())
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            doc = ast.get_docstring(node) or ""
            params = [a.arg for a in (node.args.args + node.args.kwonlyargs)
                      if a.arg not in ("self", "cls")]
            annotated = all(
                a.annotation is not None
                for a in (node.args.args + node.args.kwonlyargs)
                if a.arg not in ("self", "cls")
            )
            exempt = len(params) <= 1 and annotated
            returns_none = (
                isinstance(node.returns, ast.Constant) and node.returns.value is None
            )

            if doc and not exempt and params and "Args:" not in doc:
                missing = ", ".join(params)
                yield path, node.lineno, f"{node.name}: no Args: for {missing}"
            if (doc and not exempt and node.returns is not None and not returns_none
                    and "Returns:" not in doc and "Yields:" not in doc):
                yield path, node.lineno, f"{node.name}: no Returns:"
            if returns_none and "Returns:" in doc:
                yield path, node.lineno, f"{node.name}: Returns: on a -> None function"
            if re.search(r"Raises:\s*(\n\s*\n|$)", doc):
                yield path, node.lineno, f"{node.name}: empty Raises:"
            # Google puts the sections last, after any explanatory prose. Once
            # a header has been seen, every later line must be another header,
            # blank, or an indented continuation of the section.
            header = re.compile(
                r"(Args|Returns|Yields|Raises|Attributes|Note|Notes|Example|Examples):"
            )
            seen_section = False
            for line in doc.splitlines():
                if header.match(line.strip()) and not line.startswith(" "):
                    seen_section = True
                    continue
                if seen_section and line.strip() and not line.startswith(" "):
                    yield path, node.lineno, f"{node.name}: prose after a section"
                    break


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--range", help="commit range, e.g. main..HEAD")
    ap.add_argument("--files", nargs="+", help="scan whole files")
    args = ap.parse_args()

    if args.files:
        lines = [(f, i, l.strip()) for f in args.files
                 for i, l in enumerate(open(f, encoding="utf-8", errors="ignore"), 1)]
        touched = list(args.files)
    elif args.range:
        lines = list(written_lines_from_diff(run(["git", "diff", "-U0", args.range])))
        lines += list(commit_messages(args.range))
        touched = run(["git", "diff", "--name-only", args.range]).split()
    else:
        lines = list(written_lines_from_diff(run(["git", "diff", "-U0", "HEAD"])))
        touched = run(["git", "diff", "--name-only", "HEAD"]).split()

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
    docs = list(docstring_problems(touched))
    if docs:
        counts["docstring"] = len(docs)
        print(f"\n== docstring ({len(docs)}) — a section is missing, empty, or out of order")
        for f, n, problem in docs[:40]:
            print(f"   {f}:{n}: {problem}")
        if len(docs) > 40:
            print(f"   … {len(docs) - 40} more")

    print(f"\n{len(lines)} written lines scanned; "
          + (", ".join(f"{k} {v}" for k, v in counts.most_common()) or "no tells found"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
