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

# Preinstalled on Colab: numpy, scipy, sympy, matplotlib, pandas, scikit-learn.
# Not preinstalled -- installed only when a code cell imports them:
OPTIONAL_PIP = {"control": "control", "pysindy": "pysindy", "gekko": "gekko"}


def detect_pip(cells):
    """Packages Colab lacks that this notebook actually imports."""
    code = "\n".join("".join(c["source"]) for c in cells
                     if c["cell_type"] == "code")
    return [pkg for mod, pkg in OPTIONAL_PIP.items()
            if re.search(rf"^\s*(import|from)\s+{mod}\b", code, re.M)]

SETUP_MARKDOWN = """\
### Colab setup

Run the cell below first. It installs the packages Colab does not ship with
(`numpy`, `scipy`, `sympy`, `matplotlib`, `pandas` and `scikit-learn` are
already there). Figures are
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
                    help="drop the instructor notes and answer keys (slide_type=notes, "
                         "except code walkthroughs) to make a student copy")
    args = ap.parse_args()


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
        def is_key(c):                   # answer keys and instructor notes;
            md = c.get("metadata", {})   # code walkthroughs stay
            return (md.get("slideshow", {}).get("slide_type") == "notes"
                    and "walkthrough" not in md.get("tags", []))
        cells = [c for c in cells if not is_key(c)]
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

    pip_pkgs = args.pip if args.pip is not None else detect_pip(cells)
    install = " ".join(pip_pkgs)
    # nbformat >= 4.5 requires a unique id on every cell.
    def cell_id():
        return uuid.uuid4().hex[:8]

    setup = [] if not pip_pkgs else [
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
