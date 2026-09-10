# PSE-823 — Lecture 1: Introductory Concepts & Modeling Tools for Process Dynamics

Source material: Coughanowr & LeBlanc, Chapters 1–2.

## What's in this folder

- **`PSE-823_Lecture-01_Ch1-2.ipynb`** — the lecture, authored as a Jupyter notebook.
  Markdown cells carry the Concept / Example / Your Turn / Check narrative; code
  cells run live Python (numpy, scipy, sympy, python-control) that solves and plots
  the two worked chemical-mixing examples and demonstrates Laplace-transform tools.
  Open it directly in Jupyter/Colab to teach interactively or to edit content.
  Instructor answer keys for "Your Turn" activities are in cell metadata
  (`slideshow.slide_type = "notes"`) — they appear in the notebook as plain markdown
  cells right after each activity.

- **`PSE-823_Lecture-01_Ch1-2_slides.slides.html`** — the same lecture exported to a
  static reveal.js slide deck. **Just double-click it and open in any browser** —
  no server, no internet connection required. Press `S` for speaker view (shows
  the hidden answer-key notes), arrow keys / space to navigate, `Esc` for overview
  mode.

- **`images/`** — the 8 textbook figures used in the deck (block diagrams and
  process-flow diagrams from Ch. 1–2). Must stay alongside the HTML/notebook files
  since they're referenced by relative path.

- **`reveal.js/`, `mathjax/`** — local copies of reveal.js and a pruned MathJax
  build (TeX font, English only). These make the slide deck fully self-contained
  and usable offline in the classroom, with no dependency on any CDN being
  reachable. Keep them next to the `.slides.html` file; no need to open them
  directly. (The exported HTML's reveal.js bootstrap is also rewritten to plain
  `<script>` tags instead of nbconvert's default RequireJS loader — that default
  is what causes the deck to open as a flat scrollable page instead of an actual
  slideshow when double-clicked rather than served over http.)

- **`reveal-lecture-theme.css`** — the custom reveal.js theme (dark blue `#0b3d91`
  headings, Segoe UI, styled code blocks) matching the look of `lecture.css`, the
  Marp theme used for other PSE-823/CHE-323 lectures. Already inlined into the
  slides HTML; kept here for reference/editing.

- **`build_notebook.py`** — the script that generates the `.ipynb` from scratch.
  Edit this (not the notebook directly) if you want to revise lecture content,
  then re-run the pipeline below.

- **`export_slides.sh`** — one-command pipeline: rebuilds the notebook, executes
  all code cells, exports to reveal.js, and re-localizes all dependencies
  (MathJax/reveal.js/jQuery) + injects the custom theme. Run this after editing
  `build_notebook.py`:

  ```bash
  ./export_slides.sh
  ```

## Workflow for future lectures

This is the reference implementation of the Jupyter → reveal.js slide format for
PSE-823: author content as a notebook (markdown + live Python cells), tag cells
with `slideshow.slide_type` (`slide` / `subslide` / `fragment` / `notes` / `skip`),
then run the same export pipeline. Copy `build_notebook.py` and
`export_slides.sh` as the starting point for the next lecture, and re-use
`reveal-lecture-theme.css`, `reveal.js/`, and `mathjax/` as-is (no
need to re-download them per lecture — just point new export scripts at the
same shared copies, or duplicate this folder).
