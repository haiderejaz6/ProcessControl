#!/usr/bin/env python3
"""
Generates a Colab-ready variant of a lecture notebook.

The canonical lecture notebook is written for offline classroom use: it refers
to its figures by relative path (images/...) so the folder works when copied to
a USB stick, and it assumes the packages are already installed. Neither holds
in Colab -- there is no images/ directory next to the notebook, and
python-control is not part of Colab's preinstalled set. This script produces a
sibling *_colab.ipynb with those two gaps closed, leaving the canonical
notebook untouched:

  * relative image references are rewritten to absolute URLs on the published
    GitHub Pages site (public regardless of whether the repo itself is private)
  * a setup cell is prepended that pip-installs the packages Colab lacks

Stdlib only -- a notebook is just JSON, and this deliberately adds no
dependency beyond what export_slides.sh already needs.

Usage (normally invoked by a lecture's export_slides.sh):
    python3 ../../tools/make_colab.py LECTURE.ipynb
    python3 ../../tools/make_colab.py LECTURE.ipynb --strip-notes
"""
import argparse
import json
import os
import re
import subprocess
import sys
import uuid

DEFAULT_BASE_URL = "https://haiderejaz6.github.io/ProcessControl"

# Preinstalled on Colab: numpy, scipy, sympy, matplotlib. Not preinstalled:
DEFAULT_PIP = ["control"]

SETUP_MARKDOWN = """\
### Colab setup

Run the cell below first. It installs the packages Colab does not ship with
(`numpy`, `scipy`, `sympy` and `matplotlib` are already there). Figures are
loaded from the course site, so this notebook needs a network connection --
the copy in the repo is the one to use offline.
"""


def repo_root(start):
    try:
        out = subprocess.run(
            ["git", "-C", os.path.dirname(os.path.abspath(start)) or ".",
             "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def rewrite_image_refs(text, prefix):
    """Point relative image references at the published site."""
    # Markdown: ![alt](images/foo.jpg)
    text = re.sub(r"(!\[[^\]]*\]\()(?!https?://|/)([^)\s]+)(\))",
                  lambda m: m.group(1) + prefix + m.group(2) + m.group(3), text)
    # HTML: <img src="images/foo.jpg">
    text = re.sub(r"""(<img\b[^>]*?\bsrc=["'])(?!https?://|/|data:)([^"']+)(["'])""",
                  lambda m: m.group(1) + prefix + m.group(2) + m.group(3), text,
                  flags=re.IGNORECASE)
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notebook", help="the canonical lecture .ipynb")
    ap.add_argument("-o", "--output", help="defaults to <notebook>_colab.ipynb")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                    help=f"published site root (default: {DEFAULT_BASE_URL})")
    ap.add_argument("--pip", action="append", default=None,
                    help="package to install in the setup cell (repeatable)")
    ap.add_argument("--strip-notes", action="store_true",
                    help="drop cells tagged slide_type=notes, i.e. the instructor "
                         "answer keys, to make a student-facing copy")
    args = ap.parse_args()

    pip_pkgs = args.pip if args.pip is not None else DEFAULT_PIP

    root = repo_root(args.notebook)
    if root is None:
        sys.exit("error: not inside a git repository; cannot derive the site path")
    rel_dir = os.path.relpath(os.path.dirname(os.path.abspath(args.notebook)), root)
    prefix = f"{args.base_url.rstrip('/')}/{rel_dir.replace(os.sep, '/')}/"

    with open(args.notebook) as f:
        nb = json.load(f)

    cells = nb["cells"]
    if args.strip_notes:
        before = len(cells)
        cells = [c for c in cells
                 if c.get("metadata", {}).get("slideshow", {}).get("slide_type") != "notes"]
        print(f"   stripped {before - len(cells)} instructor-notes cell(s)")

    rewritten = 0
    for c in cells:
        if c["cell_type"] != "markdown":
            continue
        src = "".join(c["source"])
        new = rewrite_image_refs(src, prefix)
        if new != src:
            c["source"] = new.splitlines(keepends=True)
            rewritten += 1

    install = " ".join(pip_pkgs)
    # nbformat >= 4.5 requires a unique id on every cell.
    def cell_id():
        return uuid.uuid4().hex[:8]

    setup = [
        {"cell_type": "markdown", "id": cell_id(),
         "metadata": {"slideshow": {"slide_type": "skip"}},
         "source": SETUP_MARKDOWN.splitlines(keepends=True)},
        {"cell_type": "code", "id": cell_id(),
         "metadata": {"slideshow": {"slide_type": "skip"}},
         "execution_count": None, "outputs": [],
         "source": [f"%pip install -q {install}\n"]},
    ]
    nb["cells"] = setup + cells

    out = args.output or re.sub(r"\.ipynb$", "_colab.ipynb", args.notebook)
    with open(out, "w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")

    print(f"   rewrote image refs in {rewritten} cell(s) -> {prefix}")
    print(f"   setup cell installs: {install}")
    print(f"== Done: {out} ==")


if __name__ == "__main__":
    main()
