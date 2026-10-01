#!/usr/bin/env python3
"""
Lint a PSE-823 lecture (or derivations) notebook against the course format.

Checks (REVISION_PLAN.md, Section 5):
  * code cells: at most 12 lines, lines at most 72 characters
  * every code cell (except the tagged setup cell) is preceded by an explain
    markdown cell and followed by a walkthrough notes cell
  * every Part divider carries a <!-- source: ... --> tag
  * every Part has a Your Turn and a Check, each followed by an answer key
    (lecture notebooks only; pass --derivations to skip)
  * no emojis anywhere
  * every relative image path resolves

Usage:  python3 tools/check_lecture.py NOTEBOOK.ipynb [--derivations]
Exit status 1 on any error, so it can gate the export.
"""
import argparse
import json
import os
import re
import sys

MAX_LINES = 12
MAX_COLS = 72
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")


def src(cell):
    s = cell.get("source", "")
    return "".join(s) if isinstance(s, list) else s


def stype(cell):
    return cell.get("metadata", {}).get("slideshow", {}).get("slide_type")


def tags(cell):
    return cell.get("metadata", {}).get("tags", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notebook")
    ap.add_argument("--derivations", action="store_true",
                    help="companion notebook: skip Your Turn/Check rules")
    args = ap.parse_args()

    with open(args.notebook) as f:
        cells = json.load(f)["cells"]
    here = os.path.dirname(os.path.abspath(args.notebook))
    errors = []

    def err(i, msg):
        errors.append(f"cell {i}: {msg}")

    parts = []  # (index, has_your_turn, has_check)
    for i, c in enumerate(cells):
        text = src(c)
        if EMOJI.search(text):
            err(i, "contains an emoji")

        if c["cell_type"] == "code":
            lines = text.splitlines()
            if len(lines) > MAX_LINES:
                err(i, f"code cell has {len(lines)} lines (max {MAX_LINES})")
            for n, line in enumerate(lines, 1):
                if len(line) > MAX_COLS:
                    err(i, f"line {n} is {len(line)} chars (max {MAX_COLS})")
            if "setup" in tags(c):
                continue
            prev = cells[i - 1] if i else None
            if not (prev and prev["cell_type"] == "markdown"
                    and stype(prev) in ("subslide", "slide")):
                err(i, "code cell has no explain slide directly above it")
            nxt = cells[i + 1] if i + 1 < len(cells) else None
            if not (nxt and "walkthrough" in tags(nxt)):
                err(i, "code cell has no walkthrough notes directly below it")
            continue

        if stype(c) == "slide" and text.lstrip().startswith("## Part"):
            if "<!-- source:" not in text:
                err(i, "Part divider has no <!-- source: ... --> tag")
            parts.append([i, False, False])
        if args.derivations:
            pass
        elif parts and text.lstrip().startswith("### Your Turn"):
            parts[-1][1] = True
            if not (i + 1 < len(cells) and "answer" in tags(cells[i + 1])):
                err(i, "Your Turn has no answer-key notes cell after it")
        elif parts and text.lstrip().startswith("### Check"):
            parts[-1][2] = True
            if not (i + 1 < len(cells) and "answer" in tags(cells[i + 1])):
                err(i, "Check has no answer notes cell after it")

        for path in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text):
            if not re.match(r"https?://|data:", path):
                if not os.path.exists(os.path.join(here, path)):
                    err(i, f"image not found: {path}")

    if not args.derivations:
        for i, yt, ck in parts:
            if not yt:
                err(i, "Part has no Your Turn")
            if not ck:
                err(i, "Part has no Check")

    name = os.path.basename(args.notebook)
    if errors:
        print(f"FAIL {name}: {len(errors)} problem(s)")
        for e in errors:
            print("  " + e)
        sys.exit(1)
    n_code = sum(c["cell_type"] == "code" for c in cells)
    print(f"OK   {name}: {len(cells)} cells, {n_code} code, "
          f"{len(parts)} parts")


if __name__ == "__main__":
    main()
