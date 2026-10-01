#!/usr/bin/env python3
"""
Private textbook chapter reader: render the chapter .md files to HTML.

The chapter files are copyrighted textbook text, so they are NEVER committed:
`chapters/` is in .gitignore. This script runs on the instructor's own copy.

    1. Download the Drive folder  Books/  (one folder per chapter, each with
       its .md and page images) into  chapters/src/  at the repo root.
    2. pip install markdown
    3. python3 tools/build_chapters.py
    4. Open chapters.html (double-click works) -- the Read links light up.

For every chapter file it:
  * applies a light, automatic cleanup of PDF-conversion artefacts
    (escaped markdown, split subscripts inside math, OCR'd <sup>/<sub> on
    symbols, duplicated table rules, image paths);
  * renders it with the site's CSS and the repo's local MathJax (no CDN);
  * copies the chapter's images next to the page;
  * writes chapters/manifest.js (the list chapters.html checks) and
    chapters/cleanup_report.md (lines the cleanup could not fix, for a
    manual pass).
"""
import argparse
import html as htmlmod
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from site_data import chapters, lectures_using  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "chapters")

NAME_PATTERNS = [
    (re.compile(r"Coughanower Chp(\d+)\.md$", re.I),
     lambda m: f"coughanowr-ch{int(m.group(1)):02d}"),
    (re.compile(r"Cecil Chp(\d+)\.md$", re.I),
     lambda m: f"cecil-ch{int(m.group(1)):02d}"),
]


def slug_for(filename):
    for pat, mk in NAME_PATTERNS:
        m = pat.search(filename)
        if m:
            return mk(m)
    return None


# ---------------------------------------------------------------- cleanup
def unescape_markdown(text):
    """Some exports escape every markdown character (\\# \\* \\_ \\\\frac)."""
    if not re.search(r"^\\#", text, re.M):
        return text
    text = re.sub(r"\\([#*_\[\]()!<>|.\-+`{}~])", r"\1", text)
    return text.replace("\\\\", "\\")


MATH = re.compile(r"\$\$.+?\$\$|\$[^$\n]+?\$", re.S)


def fix_math(m):
    s = m.group(0)
    s = re.sub(r"\\tau_\{(\d)s\}", r"\\tau_\1 s", s)      # tau_{1s} -> tau_1 s
    s = re.sub(r"\\tau_\{is\}", r"\\tau_i s", s)
    s = s.replace("\\quad (", "\\qquad (")
    return s


def clean(text, slug, problems):
    text = unescape_markdown(text)
    text = MATH.sub(fix_math, text)
    # OCR'd subscripts outside math: *R*<sup>1</sup> -> *R*<sub>1</sub>
    text = re.sub(r"(\*[A-Za-z]\*)<sup>(\d)</sup>", r"\1<sub>\2</sub>", text)
    # duplicated table separator rows
    text = re.sub(r"(\n\|[-| ]+\|)(\n\|[-| ]+\|)+", r"\1", text)
    # images live in chapters/<slug>/
    text = re.sub(r"!\[([^\]]*)\]\((?!https?://)([^)]+)\)",
                  lambda m: f"![{m.group(1)}]({slug}/{os.path.basename(m.group(2))})",
                  text)
    # report what is left for a manual pass
    for n, line in enumerate(text.splitlines(), 1):
        plain = MATH.sub("", line)
        if re.search(r"\*[A-Za-z]{1,3}\* ?[A-Za-z0-9]{1,3}\s+-\s", plain) or \
           re.search(r"\b(\w)\s\1{2,}\b", plain):
            problems.append((slug, n, line.strip()[:110]))
    return text


# ---------------------------------------------------------------- render
def to_html(md_text):
    import markdown
    store = []

    def stash(m):
        store.append(m.group(0))
        return f"@@MATH{len(store) - 1}@@"

    protected = MATH.sub(stash, md_text)
    body = markdown.markdown(protected, extensions=["tables", "toc"],
                             output_format="html5")
    return re.sub(r"@@MATH(\d+)@@",
                  lambda m: htmlmod.escape(store[int(m.group(1))], quote=False),
                  body)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{title}</title>
<link rel="stylesheet" href="../assets/site.css">
<style>
  .chapter {{ max-width: 860px; margin: 0 auto; padding: 24px 20px 80px; line-height: 1.6; }}
  .chapter img {{ max-width: 100%; height: auto; display: block; margin: 12px auto; }}
  .chapter table {{ border-collapse: collapse; margin: 12px 0; }}
  .chapter td, .chapter th {{ border: 1px solid var(--border); padding: 4px 8px; }}
  .chapter h1, .chapter h2, .chapter h3 {{ line-height: 1.3; }}
  .chapter .MathJax_Display {{ overflow-x: auto; overflow-y: hidden; }}
  .ch-nav {{ display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;
            font-size: .92rem; margin-bottom: 18px; }}
</style>
<script type="text/x-mathjax-config">
MathJax.Hub.Config({{
  tex2jax: {{ inlineMath: [['$','$']], displayMath: [['$$','$$']], processEscapes: true }},
  messageStyle: "none"
}});
</script>
<script src="../assets/mathjax/MathJax.js?config=TeX-AMS_CHTML-full"></script>
</head>
<body>
<main class="chapter">
<nav class="ch-nav">
  <a href="../chapters.html">All chapters</a>
  <span>{book}, Chapter {num}{used}</span>
  <span>{prev} {next}</span>
</nav>
{body}
<nav class="ch-nav"><a href="../chapters.html">All chapters</a><span>{prev} {next}</span></nav>
</main>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=os.path.join(OUT, "src"),
                    help="folder holding the downloaded Books/ tree")
    args = ap.parse_args()
    if not os.path.isdir(args.src):
        sys.exit(f"no chapter sources at {args.src} (see this script's docstring)")

    found = {}
    for dirpath, _, files in os.walk(args.src):
        for fn in files:
            slug = slug_for(fn)
            if slug:
                found[slug] = os.path.join(dirpath, fn)

    meta = {c["slug"]: c for c in chapters()}
    order = [c["slug"] for c in chapters() if c["slug"] in found]
    problems, done = [], []
    for i, slug in enumerate(order):
        path, c = found[slug], meta[slug]
        with open(path, encoding="utf-8") as f:
            text = clean(f.read(), slug, problems)
        img_out = os.path.join(OUT, slug)
        os.makedirs(img_out, exist_ok=True)
        for fn in os.listdir(os.path.dirname(path)):
            if fn.lower().endswith((".jpeg", ".jpg", ".png", ".gif")):
                shutil.copy2(os.path.join(os.path.dirname(path), fn), img_out)
        lects = lectures_using(slug)
        used = (" &middot; used in " + ", ".join(f"Lecture {n}" for n in lects)
                if lects else "")
        prev = (f'<a href="{order[i - 1]}.html">&larr; previous</a>'
                if i > 0 else "")
        nxt = (f'<a href="{order[i + 1]}.html">next &rarr;</a>'
               if i + 1 < len(order) else "")
        page = PAGE.format(title=f'{c["book"]} Ch. {c["num"]}: {c["title"]}',
                           book=c["book"], num=c["num"], used=used,
                           prev=prev, next=nxt, body=to_html(text))
        with open(os.path.join(OUT, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(page)
        done.append(slug)
        print(f"rendered {slug}")

    with open(os.path.join(OUT, "manifest.js"), "w") as f:
        f.write("window.PSE823_CHAPTERS = " + repr(done).replace("'", '"') + ";\n")
    with open(os.path.join(OUT, "cleanup_report.md"), "w") as f:
        f.write("# Chapter cleanup report\n\nLines the automatic cleanup could "
                "not fix (likely garbled inline symbols from the PDF "
                "conversion).\n\n")
        for slug, n, line in problems:
            f.write(f"- `{slug}` line {n}: {line}\n")
    print(f"{len(done)} chapters rendered; {len(problems)} lines flagged in "
          f"chapters/cleanup_report.md")


if __name__ == "__main__":
    main()
