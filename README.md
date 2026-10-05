# PSE-823 — Advanced Process Dynamics and Control

Course materials for PSE-823 (MS elective, School of Chemical and Materials
Engineering, NUST), taught by Haider Ejaz.

**Course site (all lectures, viewable in-browser):** https://haiderejaz6.github.io/ProcessControl/

## Repository layout

```
.
├── index.html                  # landing page: lecture cards (generated between markers)
├── derivations.html            # companion derivation notebooks (generated between markers)
├── chapters.html               # textbook chapter list + private reader links (generated)
├── resources.html              # reference notes from the Instrumentation & Process Control course
├── course-info.html            # syllabus, objectives, reading list
├── REVISION_PLAN.md            # the derive-then-code revision plan and its status
├── requirements.txt, runtime.txt   # the Binder environment
├── resources/                  # PDFs/PPTX + the Python primer notebook (own export_slides.sh)
├── assets/                     # shared by every deck: local reveal.js, pruned MathJax,
│                               #   reveal-lecture-theme.css, site.css
├── tools/
│   ├── lecture_kit.py          # Deck: the builder every build script uses
│   ├── check_lecture.py        # format linter (run on every export)
│   ├── run_lecture.py          # execute a notebook; clear `predict` cells
│   ├── export_lecture.sh       # lint -> execute -> reveal.js -> localize -> Colab copy -> read page
│   ├── export_read.sh          # static scrollable "Read" page (nbconvert HTML, local MathJax)
│   ├── localize_slides.py      # point a deck at assets/, drop CDNs, inject the theme
│   ├── check_slides.py         # Playwright: flag slides that overflow 1024x768
│   ├── make_colab.py           # the "Open in Colab" variant
│   ├── site_data.py            # lecture and chapter lists (single source for the site)
│   ├── build_site.py           # regenerates the cards, nav and chapters.html
│   └── build_chapters.py       # renders the private chapter reader (see below)
├── chapters/                   # PRIVATE, git-ignored: rendered textbook chapters
└── lectures/
    ├── NN-topic/
    │   ├── build_notebook.py           # the lecture's content -- edit this
    │   ├── build_derivations.py        # its companion notebook
    │   ├── PSE-823_Lecture-NN_<Topic>.ipynb            # generated
    │   ├── PSE-823_Lecture-NN_<Topic>_colab.ipynb      # generated
    │   ├── PSE-823_Lecture-NN_<Topic>_slides.slides.html   # generated
    │   ├── PSE-823_Lecture-NN_<Topic>_read.html            # generated ("Read" button)
    │   └── images/                     # figures used by this lecture
    └── derivations/                    # generated companion notebooks, decks, Colab copies
```

Lectures 5, 9, 12 and 14 are empty slots on the site until their chapter
files (Coughanowr Ch. 26, Cecil Ch. 2, Coughanowr Ch. 22 and Ch. 25) are
available. To fill a slot, add its folder and build scripts and remove
`status="slot"` from its entry in `tools/site_data.py`.

## Lecture format: derive, then code, then explain

Every Part of every lecture runs **Introduce -> Derive k/n -> Code k/n ->
Build on it -> Your Turn -> Check** (details in `REVISION_PLAN.md`):

- **Derive** slides give the board step; its result appears on click.
- **Code** steps come as a unit, produced by `Deck.code()`:
  an *explain* slide (what the cell does, which derivation step it
  mirrors, any new function), the code cell (at most 12 lines of at most
  72 characters), and a *walkthrough* in the speaker notes (line by line,
  the expected output, what it confirms). The walkthrough numbers are
  checked against the executed output.
- **No laptops in class.** Code is read and interpreted, not typed:
  *Your Turn* asks for a short hand calculation and a "what does this
  print?" question. Cells tagged `predict` are exported with their output
  cleared, so the class predicts the result before the instructor runs it.
- Each lecture has a **companion notebook** (`build_derivations.py`) with
  the full derivations and worked answers.

Cell tags used by the tools: `walkthrough`, `answer`, `instructor`,
`predict`, `setup`. Slide structure uses the usual
`slideshow.slide_type` metadata (`slide`, `subslide`, `fragment`, `notes`).

## Building a lecture

```bash
python3 lectures/10-tuning-identification/build_notebook.py
bash tools/export_lecture.sh lectures/10-tuning-identification/PSE-823_Lecture-10_Tuning-Identification.ipynb
python3 tools/check_slides.py lectures/10-tuning-identification/PSE-823_Lecture-10_Tuning-Identification_slides.slides.html
python3 tools/build_site.py
```

`export_lecture.sh` lints the notebook (`--derivations` rules apply
automatically under `lectures/derivations/`), executes it in place, clears
the `predict` cells, exports the reveal.js deck against the local
`assets/`, removes every CDN reference, and writes the Colab copy.
`check_slides.py` uses Playwright's Chromium to screenshot-measure every
slide at 1024x768; it must report 0 overflowing.

To add a lecture: add its entry to `tools/site_data.py`, create
`lectures/NN-topic/build_notebook.py` (copy an existing one for the
pattern), build and export as above, then run `tools/build_site.py`.

## Presentation mode (Binder + RISE)

Every notebook on the site can be presented as live slides. Its **Open in
Binder** link launches the repo on mybinder.org straight into that file in
the classic Jupyter Notebook interface. Click the slideshow icon (or press
`Alt+R`) to present; cells can be run during the show, and the walkthrough
notes are in the speaker view.

`requirements.txt` and `runtime.txt` pin the environment Binder builds
(`notebook==6.5.7` + `rise==5.7.1`, because RISE's button only ships for the
classic notebook UI, plus every package the notebooks import: numpy >= 2,
scipy, sympy, matplotlib, python-control, GEKKO, pandas, scikit-learn).
Links must use `urlpath=notebooks%2F<path>`. If a notebook imports a new
package, add it to `requirements.txt`; Binder rebuilds when that file
changes.

## The chapter reader (private)

The textbook chapters (Coughanowr & LeBlanc; Cecil Smith) are copyrighted,
so their text is **never committed**. `chapters/` is in `.gitignore`.

1. Download the Drive `Books/` folders into `chapters/src/`.
2. Run `python3 tools/build_chapters.py`. It un-escapes the markdown,
   repairs math and sub/superscripts, renders each chapter with the local
   MathJax, copies its figures, and writes `chapters/manifest.js` and
   `chapters/cleanup_report.md` (lines it could not fix).
3. Open `chapters.html` locally. Chapters present in `manifest.js` get a
   **Read** link; on the public site the page lists the chapters, the
   lectures that use them, and a notice that the text is private.

## The Colab variant

`make_colab.py` writes a `*_colab.ipynb` beside each notebook: figure
references become absolute URLs on the published site, and a setup cell
installs only what Colab lacks and the notebook imports (`control`,
`gekko`, `pysindy`). Never hand-edit it. `--strip-notes` makes a student
copy without answer keys and instructor notes (the code walkthroughs stay).

The `Open in Colab` links require the repository to be public.

## Why local reveal.js/MathJax instead of a CDN

nbconvert's default export pulls reveal.js, MathJax, jQuery and RequireJS
from CDNs and boots reveal.js through RequireJS, which often fails silently
when a deck is opened from `file://`. `localize_slides.py` points each deck
at the bundled `assets/reveal.js` and pruned MathJax, drops
jQuery/RequireJS/mermaid, replaces the bootstrap with a plain
`Reveal.initialize()` (1024x768, no vertical centering), injects the course
theme, and fails the export if any CDN reference remains.
