"""
lecture_kit -- shared builder for PSE-823 lecture and derivations notebooks.

Every lecture's build_notebook.py imports this module and describes the
lecture as a sequence of calls; the module turns them into an .ipynb with the
RISE/reveal.js metadata the course uses (1024x768, 4:3).

The derive-then-code format (REVISION_PLAN.md, Section 3) is encoded here:

    deck.derive("Derive 1/3 -- ...", prompt, result)      board step + reveal
    deck.code("Code 1/3 -- ...", bullets, source, walk)   explain slide,
                                                           code cell,
                                                           walkthrough notes

`code()` is the heart of it: every code cell is preceded by an *explain*
subslide (what the cell does, which board step it mirrors) and followed by a
*walkthrough* notes cell (line by line, expected output, common mistake).
Notes cells never appear on the projected slides; they show in the RISE
speaker view and as ordinary cells in Colab/Jupyter.

Cell tags (metadata.tags) used by the other tools:
    walkthrough  line-by-line explanation of the code cell above it
    answer       Your Turn answer key
    instructor   other speaker notes
    predict      code-interpretation cell: its output is cleared after
                 execution so the class predicts it before it is run
    setup        the imports cell (exempt from the explain-slide rule)
"""
import textwrap

import nbformat as nbf

RISE = {
    "width": 1024,
    "height": 768,
    "theme": "simple",
    "transition": "slide",
    "scroll": True,
    "center": False,
}


def _clean(text):
    return textwrap.dedent(text).strip("\n")


def _bullets(items):
    if isinstance(items, str):
        return _clean(items)
    return "\n".join(f"- {b}" for b in items)


class Deck:
    """Accumulates cells, then writes one notebook."""

    def __init__(self):
        self.cells = []

    # -- low-level cells -------------------------------------------------
    def _md(self, src, slide_type, tags=None):
        meta = {"slideshow": {"slide_type": slide_type}}
        if tags:
            meta["tags"] = list(tags)
        self.cells.append(nbf.v4.new_markdown_cell(_clean(src), metadata=meta))

    def _code(self, src, slide_type="-", tags=None):
        meta = {"slideshow": {"slide_type": slide_type}}
        if tags:
            meta["tags"] = list(tags)
        self.cells.append(nbf.v4.new_code_cell(_clean(src), metadata=meta))

    def slide(self, src):
        self._md(src, "slide")

    def sub(self, src):
        self._md(src, "subslide")

    def frag(self, src):
        self._md(src, "fragment")

    def cont(self, src):
        """Markdown that continues the current slide (no break)."""
        self._md(src, "-")

    def notes(self, src):
        self._md(src, "notes", ["instructor"])

    def answer(self, src):
        self._md(src, "notes", ["answer"])

    # -- structural pieces -----------------------------------------------
    def title(self, lecture, topic, source, date=True):
        head = "# PSE-823: Advanced Process Dynamics and Control\n"
        head += f"## {lecture} -- {topic}\n### ({source})"
        if date:
            head += "\n\nDate: __________"
        self.slide(head)

    def part(self, letter, title, source_line, tag):
        """Part divider with the human- and machine-readable source tags."""
        self.slide(f"## Part {letter}\n### {title}\n\n({source_line})\n"
                   f"<!-- source: {tag} -->")

    def setup(self, bullets, source):
        self.sub("### Setup (run once)\n\n" + _bullets(bullets))
        self._code(source, "-", ["setup"])

    def derive(self, heading, prompt, result, notes=None):
        """One board step: the prompt, then the result on click."""
        self.sub(f"### {heading}\n\n{_clean(prompt)}")
        self.frag(result)
        if notes:
            self.notes(notes)

    def code(self, heading, bullets, source, walkthrough, predict=False):
        """Explain slide + code cell + walkthrough notes, as one unit."""
        self.sub(f"### {heading}\n\n" + _bullets(bullets))
        self._code(source, "-", ["predict"] if predict else None)
        self._md("**Code walkthrough.** " + _clean(walkthrough), "notes",
                 ["walkthrough"])

    def your_turn(self, minutes, body, answer):
        self.sub(f"### Your Turn ({minutes} min)\n\n" + _clean(body))
        self.answer(answer)

    def check(self, style, body, answer):
        self.sub(f"### Check -- {style}\n\n" + _clean(body))
        self.answer(answer)

    # -- output ----------------------------------------------------------
    def write(self, path):
        nb = nbf.v4.new_notebook()
        nb.metadata.update({
            "kernelspec": {"name": "python3", "language": "python",
                           "display_name": "Python 3"},
            "language_info": {"name": "python"},
            "rise": RISE,
        })
        nb.cells = self.cells
        nbf.validate(nb)
        nbf.write(nb, path)
        print(f"wrote {path} ({len(self.cells)} cells)")


# Imports shared by every lecture from L3 on. Lectures add to this.
STANDARD_SETUP = """\
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import control as ct
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit
plt.rcParams.update({"font.size": 15})
"""
