# PSE-823 — Advanced Process Dynamics and Control

Course materials for PSE-823 (MS elective, School of Chemical and Materials
Engineering, NUST), taught by Haider Ejaz.

**Course site (all lectures, viewable in-browser):** https://haiderejaz6.github.io/ProcessControl/

## Repository layout

```
.
├── index.html                        # GitHub Pages landing page — lists all lectures
├── assets/                           # shared, reused across every lecture
│   ├── reveal.js/                    # local reveal.js (no CDN dependency)
│   ├── mathjax/                      # pruned local MathJax build (TeX font, English)
│   └── reveal-lecture-theme.css      # visual theme (matches the course's Marp theme)
└── lectures/
    └── 01-intro-and-modeling/
        ├── PSE-823_Lecture-01_Ch1-2.ipynb          # the lecture, as a notebook
        ├── PSE-823_Lecture-01_Ch1-2_slides.slides.html   # exported slide deck
        ├── images/                  # textbook figures used in this lecture
        ├── build_notebook.py        # generates the .ipynb — edit this to revise content
        └── export_slides.sh         # rebuild + re-export pipeline (see below)
```

## Format

Each lecture is authored as a Jupyter notebook: markdown cells carry the
Concept → Example → Your Turn → Check narrative, and code cells run live
Python (numpy, scipy, sympy, python-control, GEKKO where relevant) that
simulates or verifies whatever the lecture just derived by hand. The notebook
is exported to a static reveal.js slide deck for classroom delivery — no
server needed, works fully offline, and matches the course's visual theme.

Cell tagging convention (`slideshow.slide_type` in cell metadata) controls
the slide-deck structure:

- `slide` — a new slide
- `fragment` — revealed within the current slide
- `notes` — hidden instructor speaker notes (answer keys), shown with `S` in reveal.js
- `skip` — visible in the notebook, omitted from the slideshow

## Adding a new lecture

1. Copy `lectures/01-intro-and-modeling/` as a starting template into a new
   `lectures/NN-topic-name/` folder.
2. Edit `build_notebook.py` to author the new lecture's content.
3. Run `./export_slides.sh` from inside that folder — it rebuilds the
   notebook, executes every code cell, exports to reveal.js, and points the
   deck at the shared `../../assets/` folder (reveal.js/MathJax/theme are
   **not** duplicated per lecture — every lecture references the same copy).
4. Add a card for it in the root `index.html`.
5. Commit and push — GitHub Pages picks up the change automatically.

## Why local reveal.js/MathJax instead of a CDN

nbconvert's default reveal.js export pulls reveal.js, MathJax, jQuery, and
RequireJS from CDNs, and bootstraps reveal.js via RequireJS's AMD loader.
That default is fragile: on a real double-click/`file://` open (rather than
served over http) the RequireJS bootstrap frequently fails silently, and the
notebook renders as a flat scrollable page instead of an actual slideshow.
`export_slides.sh` fixes this by bundling reveal.js and a pruned MathJax
locally, dropping the unused jQuery/RequireJS/mermaid dependencies entirely,
and replacing the AMD bootstrap with a plain `Reveal.initialize()` call —
reveal.js and its notes plugin are both UMD bundles that expose plain globals
when loaded as ordinary `<script>` tags, so no module loader is needed.
