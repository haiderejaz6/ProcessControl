# PSE-823 Lecture Revision Plan: derive, then code, then explain

Status: **built** for the 11 lectures whose chapter files exist (L1-L4,
L6-L8, L10, L11, L13, L15), each with its companion notebook. L5, L9, L12
and L14 are empty slots on the site (Section 9). Decisions were taken on
2026-10-01; Section 10 records the build.
Source of truth for scope: `PSE-823 Teaching Plan.md` (v2, 2026-09-28) in the
course Drive folder. If the two disagree, the Teaching Plan wins and this file
gets updated.

---

## 1. What changes

1. **Every lecture (L1-L15)** becomes a derive-then-code notebook in the format
   Lecture 3 already uses. Each derivation and each worked example from the
   chapter gets Python cells that repeat it step for step, then carry it past
   what hand algebra can do.
2. **Every code cell is explained in detail** and tied to the lecture content
   (Section 3 has the pattern).
3. Delivery stays the same: Jupyter notebooks, presented live as reveal.js
   slides through **RISE on Binder**, with the static reveal.js export and the
   Colab copy still published on the site.
4. **A chapter reader** is added to the site. It renders the textbook chapter
   `.md` files, but the chapter text stays **private** (Section 6).

## 2. Decisions taken

| Question | Decision |
|---|---|
| Where the chapter `.md` files live | Not in this repo. They are in Drive, `Books/` (one folder per chapter, `.md` plus page images). |
| Chapter reader visibility | **Private.** The renderer is committed; the chapter text and figures are not. The public site shows the chapter list and a notice, and renders a chapter only where the files are present locally. |
| Which lectures | **All 15**, built in order, one batch at a time (Section 8). |
| How code is explained | **Explain slide + notes**: a short "What this cell does" slide above each code cell, short inline comments, a full line-by-line walkthrough in speaker notes. The Colab copy turns the walkthrough into a visible markdown cell. |
| Chapter `.md` cleanup | **Light automated fix** by script; anything it can't fix is listed in a report for manual follow-up. |
| Lectures whose chapter file is missing | **Empty slots** on the site (L5, L9, L12, L14); built when the chapter arrives. |
| Laptops in class | **None.** Code is interpreted in class, not typed: Your Turn asks "what does this print?" and `predict` cells are shown with their output cleared. Students run the notebooks after class (Binder or Colab). |

## 3. Lecture format (every Part of every lecture)

Graduate pacing stays: one checkpoint per Part, no CHE-226-style
mini-cycles. Each Part runs:

1. **Introduce** (subslide): the physical question, setup and assumptions,
   in Coughanowr's (or Cecil's) notation, with the book's figure.
2. **Derive k/n** (one subslide per step): prompt on the slide, the step's
   result revealed as a `fragment`, so students can check their notes.
3. **Code k/n** (one subslide per derivation step, same step number):
   - **Explain slide**: 3-4 bullets saying what the cell does and *which board
     step it mirrors*, plus any new function introduced
     (e.g. "`sp.apart` = the cover-up rule"). This is the "detailed
     explanation" students read on screen.
   - **Code cell** (3-10 lines, hard ceiling 12, lines under 70 characters):
     one or two inline comments only, pointing back to equation numbers
     (`# Eq. 4.15`).
   - **Walkthrough** (`notes` cell): line by line, what each line does, what
     the output should look like, the common mistake, and how the output
     confirms the derivation. In the Colab/student copy, `make_colab.py`
     turns these into visible markdown cells headed "Code walkthrough".
4. **Build on it**: numbers from the chapter's worked example, plots built up
   across cells, then `solve_ivp` / `python-control` / `curve_fit` (and later
   scikit-learn, PySINDy, GEKKO) for the general or nonlinear case. **Always
   checked against the derived result** (overlay or `np.allclose`), and
   explained the same way as in step 3.
5. **Your Turn**: a short hand calculation, then a **code-interpretation**
   question (read a few lines, predict the output, explain why). No laptops:
   nobody types code in class. The answer key goes in a `notes` cell; the
   full worked version goes in the companion Derivations notebook.
6. **Check**: one cold-call, poll or think-pair-share.

Rules carried over from the lecture-builder skill: examples come only from the
chapter itself or are callbacks to earlier lectures; no emojis; KaTeX-safe
LaTeX; 4:3 budget (1024x768); plots get their own subslide with
`figsize=(7, 5.25)` and are pre-executed; other code cells stay unexecuted for
live running; one machine-readable tag per Part divider
(`<!-- source: coughanowr-ch4 -->`).

### Example of the explanation pattern (L3, Part A, Code 3/4)

> **Explain slide:** *Code 3/4 mirrors Derive 3/4 (Laplace transform).*
> - `sp.laplace_transform(expr, t, s)` applies the definition of the transform
>   to each side.
> - It applies the derivative rule itself: look for the `-Y(0)` term.
> - `noconds=True` drops the convergence conditions we don't need here.
>
> **Notes (walkthrough):** Line 1 transforms the left side `hA(X - Y)`, which
> is linear, so you get `hA(X(s) - Y(s))`. Line 2 transforms `mC dY/dt`. SymPy
> writes `s*LaplaceTransform(Y) - Y(0)`, which is the rule from Derive 3/4.
> Common mistake: forgetting that `Y(0)` vanishes only *because* we chose
> deviation variables...

## 4. Per-lecture content map

Libraries are phased in as the Teaching Plan says: `sympy` for derivations
throughout; `numpy`, `scipy`, `matplotlib`, `python-control` in L3-L9;
`scikit-learn` and `pandas` from L10; `pysindy` in L14; `gekko` in L15.

| L | Source | Parts (A, B, C, D) | Derivations coded step by step | Build-on / data thread |
|---|---|---|---|---|
| 01 | C&L Ch. 1; Cecil 1.1-1.2 | A course map; B economics and DCS blocks; C control vocabulary, feedback, P/PI, offset; D stability warning | Ex. 1.1 hot-water tank as an on/off rule, then P-only offset $e_{ss}=\Delta d/(1+K_cK_p)$ in SymPy | Simulate on/off, P and PI on the hot-water tank (`solve_ivp`); variance-vs-target calculation for "narrow the variance, shift the target"; summer block and windup check |
| 02 | C&L Ch. 2-3 | A mixing tank mass balance; B energy balance (heated tank); C Laplace and the 3-step method; D partial fractions (distinct, complex, repeated roots); E root locations | Eqs. 2.1-2.4 and 2.10-2.11 built from the balance in SymPy; Ex. 3.1, 3.2, 3.4, 3.5 inverted with `apart` and `inverse_laplace_transform` | `solve_ivp` overlay on $2+e^{-t/5}$ (the teaching plan's retrofit); root-location gallery (Fig. 3-1) generated from the poles; wrap-up points to Ch. 4-6 |
| 03 | C&L Ch. 4-6 | (already in this format) A thermometer TF; B reading tau from data (Prob. 4.6); C nonlinear tank and linearization; D tanks in series | Existing | **Upgrade only**: add explain slides and walkthrough notes to all 34 code cells; check against the Ch. 4-6 `.md` for any missing worked examples (impulse, ramp, sinusoidal responses, Sec. 4.5-4.7) |
| 04 | C&L Ch. 7-8 | A second-order system from the damped vibrator; B step-response characteristics; C transportation lag and Pade; D the control system and its block diagram (Ch. 8 stirred-tank heater) | Eq. 7.x standard form; overshoot, decay ratio, rise time, period from the underdamped solution; $e^{-\tau_d s}$ and its Pade form; Ch. 8 block diagram reduced symbolically | Damping-ratio sweep plots; `ct.pade`, `ct.series`; **fit an FOPDT model to the four-tank response** (`curve_fit`); A1 set here |
| 05 | C&L Ch. 9-11 + Ch. 26 | A controllers (P, PI, PD, PID) and valves; B the Ch. 10 jacketed reactor block diagram; C closed-loop TFs (servo and regulator); D the digital PID (Ch. 26) | Ideal controller TFs; reactor TFs (Sec. 10.2-10.8); $C/R$ and $C/U$ by block algebra in SymPy | `ct.feedback` against SymPy's closed-loop TF; **PID as a sampled `for` loop with saturation and anti-windup**, compared to the continuous loop; introduces the reactor as the recurring plant |
| 06 | C&L Ch. 12-14 | A P control, servo and regulator, offset; B PI control; C P with measurement lag (Sec. 12.5); D stability and Routh; E root locus | Offset formulas; closed-loop roots vs $K_c$; Routh array built row by row in code | Gain sweeps; `np.roots` against Routh; brute-force stability boundary, then explained by Routh; `ct.root_locus`; A2 and project M1 set here |
| 07 | C&L Ch. 15 | A substitution rule; B Bode diagrams of first-order, second-order, dead time and PI/PID blocks | AR and phase derived by $s=j\omega$, done symbolically | **Sine-sweep simulation: AR and phase measured from the simulated signals**, then `ct.bode_plot` overlays the derived curves |
| 08 | C&L Ch. 16 | A tank temperature control (Sec. 16.1); B Bode stability criterion; C gain and phase margins; D Ziegler-Nichols | Crossover frequency, $K_{c,max}$ and margins by hand for the book's system | `ct.margin`; Z-N settings applied to the reactor loop and the closed-loop response simulated. **Midterm after this lecture.** |
| 09 | C&L Ch. 17 + Cecil 2-6 | A cascade; B feedforward and ratio; C Smith predictor and IMC; D override, split range, valve position (Cecil) | Cascade inner/outer TFs; ideal feedforward $G_f=-G_d/G_p$; Smith predictor structure; IMC controller | Disturbance scenarios simulated for each strategy, **IAE compared**; override with integral tracking as a sampled loop; cost of variability from simulated operating data |
| 10 | C&L Ch. 18 | A tuning criteria and rules (ITAE, Cohen-Coon); B process identification by step test; C ARX by least squares; D **ML entry 1** | Tuning formulas evaluated from fitted parameters; normal equations for ARX written out | FOPDT fit; ARX via `np.linalg.lstsq`; scikit-learn regressors trained and tested on **unseen operating conditions**; "is it usable by a controller?" |
| 11 | C&L Ch. 20 | A steam-jacketed kettle (20.1); B gas absorber (20.2); C distributed-parameter system (20.3); D **ML entry 2** | Kettle and absorber linearized models from the book | First-principles simulators; method of lines for 20.3; simulator as data generator, surrogate model and grey-box (physics plus learned residual); A3 and M2 here |
| 12 | C&L Ch. 21-22 | A state variables (21.2); B transition matrix (22.1); C transfer function matrix (22.2); D discrete-time state space | State equations of the book's examples; $e^{At}$ by Laplace inverse in SymPy | `scipy.linalg.expm` vs SymPy; eigenvalues vs poles; `ct.ss`, `ct.ss2tf`; identified ARX model rewritten in state space for MPC |
| 13 | C&L Ch. 23 + Cecil 7, 8.1 | A interacting systems (23.1); B RGA and pairing; C decoupling; D stability of multivariable systems (23.2) | RGA from the gain matrix; ideal decoupler | RGA from simulated and from identified gains; **Wood-Berry column** simulated with and without decoupler |
| 14 | C&L Ch. 24-25 | A phase plane, damped oscillator (24.2-24.3); B pendulum (24.4); C chemical reactor and multiple steady states (24.5); D phase-space examples (Ch. 25); E **ML entry 3** | Singular points and their linearization (Jacobian, eigenvalues) | `quiver` phase portraits; steady states found with `fsolve`; **PySINDy recovers the reactor equations**, with and without noise; A4 here |
| 15 | Cecil 8.2-8.3 | A dead-time compensation; B MPC formulation; C MPC on the reactor; D **ML entry 4** | Prediction equations for the step-response model; the MPC objective written out | GEKKO MPC on the linear model and on the identified model; constraints; economic-objective variant; project M3 |

Each lecture also gets its **companion Derivations notebook** (full worked
versions of every Derive sequence and every Your Turn), built the same way.

## 5. Build tooling (so 15 lectures stay consistent)

- `tools/lecture_kit.py`: shared helpers used by every build script:
  `md()`, `fragment()`, `notes()`, `code()`, `explain_code(explain, code,
  walkthrough)` (emits the explain slide, code cell and notes cell as a
  unit), `plot()`, plus the RISE metadata and the 4:3 linter.
- `lectures/NN-*/build_notebook.py`: one per lecture. The content is
  authored here, not by hand-editing JSON, so revisions are reviewable diffs.
  L3's hand-authored notebook is converted to this form first, as the
  reference.
- **Linter** (`tools/check_lecture.py`), run on every build:
  - code cells within 12 lines and 70 characters per line
  - every code cell has an explain slide before it and a walkthrough after it
  - every Part has Introduce, Derive, Code, Your Turn, notes and Check
  - a source tag on every Part divider
  - no emojis
  - every image path resolves
- `tools/export_lecture.sh NN`: generalizes the per-folder `export_slides.sh`
  (execute a copy, export slides against local reveal.js/MathJax, inject the
  theme, verify no CDN references, generate the Colab copy).
- `tools/make_colab.py`: extended to turn walkthrough notes into visible
  "Code walkthrough" cells (keeping `--strip-notes` for answer keys, which
  are tagged separately so they stay hidden).
- `requirements.txt`: add `pandas` and `scikit-learn` before L10, `pysindy`
  before L14. Binder rebuilds when this file changes, so batch these
  additions.

## 6. Chapter reader (private)

**Goal:** read the chapter `.md` files rendered, with equations and figures,
from the course site's look and feel, without publishing the books.

- `tools/fetch_chapters.md`: how to download the `Books/` folders from Drive
  into `chapters/` at the repo root. `chapters/` is in `.gitignore`, so it is
  never committed.
- `tools/build_chapters.py`:
  1. **Clean** each `.md` with a light automated pass: un-escape markdown,
     repair `<sup>`/`<sub>` fragments around symbols, normalize `$...$` and
     `$$...$$` math, attach equation numbers `(4.15)`, and rewrite image
     paths to `chapters/<slug>/img/...`.
  2. **Render** to `chapters/<slug>.html` using the site's CSS and the
     **local MathJax** already in `assets/` (no CDN), with a chapter table of
     contents, previous/next links and "Used in Lecture N" back-links.
  3. Write `chapters/cleanup_report.md` listing lines it could not fix
     (garbled inline math, broken tables) for manual follow-up.
- **`chapters.html`** (committed, public): the "Textbook chapters" section.
  It lists every chapter of both books with its sections and the lecture(s)
  that use it. Each entry links to `chapters/<slug>.html`. A short script
  checks whether that file exists. If it does (a local clone with
  `chapters/` populated), the link opens the rendered chapter. If it doesn't
  (the public site), it says "Chapter text is available in the instructor's
  private copy" and links the lecture slides instead.
- How you read them: run `python3 tools/build_chapters.py`, then open
  `chapters.html` locally (double-click works, as with the slide decks) or
  serve it with `python3 -m http.server`.
- Nav: add "Chapters" to the site header next to Lectures, Derivations and
  Resources.

Chapter files available in Drive: Coughanowr Ch. 1-18, 20, 21, 23, 24; Cecil
Ch. 1, 1.1-1.2, 3-8, plus both contents files.

## 7. Site changes

- `index.html`: lecture cards for L1-L15. Cards for lectures not yet built
  stay as "coming week N" placeholders until their batch lands.
- `derivations.html`: one companion card per lecture.
- `chapters.html`: new page (Section 6) and a nav link on every page.
- `README.md`: document the new format, `lecture_kit`, the linter, the
  chapter reader, and that `chapters/` must never be committed.

## 8. Order of work and verification

Built in batches. Each batch is pushed to the development branch for review
before the next one starts.

| Batch | Contents |
|---|---|
| 0 | Tooling: `lecture_kit.py`, linter, `export_lecture.sh`, `make_colab.py` changes; L3 converted to a build script; chapter reader and `chapters.html` |
| 1 | L1, L2 rebuilt; L3 explanation upgrade (the lectures already taught, so students can revisit them) |
| 2 | L4, L5 |
| 3 | L6, L7, L8 (to the midterm) |
| 4 | L9, L10 |
| 5 | L11, L12, L13 |
| 6 | L14, L15; `requirements.txt` final |

Every lecture passes these checks before it is pushed:

1. The linter is clean.
2. A copy of the notebook executes top to bottom with no errors (`nbconvert --execute`).
3. Every "build on it" result agrees with the derived result (asserted in the cell or shown as an overlay).
4. The static reveal.js export renders at 1024x768. A Playwright screenshot of every slide is checked for overflow.
5. The Colab copy opens and runs (pip cell first).
6. Binder/RISE: the `urlpath=notebooks%2F...` link opens the notebook with the slideshow button working. Checked once per batch.

## 9. Open items (need your input before the batch that needs them)

1. **Missing chapter files.** Coughanowr Ch. 22 (needed for L12), Ch. 25 (L14)
   and Ch. 26 (L5), and Cecil Ch. 2 (cascade, L9) are not in Drive's `Books/`
   folder. Ch. 19 (valves) is not scheduled. **Decision:** those four
   lectures are empty slots on the site until the files arrive.
2. **Lecture figures.** Figures for slides are copied from the chapter
   folders' page images into each lecture's `images/` (as L1-L2 already do,
   a few per lecture).
3. **Colab links** still need the repo to be public. The chapter text is
   unaffected either way, since it is never committed.
4. **Assignments A1-A4 and project milestones** are referenced at the right
   lectures, but writing them is a separate task.
5. **Laptops in class** (Teaching Plan open item): it changes whether Your
   Turn code checks are done by students or shown by you. The notebooks
   support both.

## 10. Build record

| L | Source | Parts | Notes |
|---|---|---|---|
| 01 | C&L Ch. 1; Cecil 1.1-1.2 | course map; economics and DCS blocks; feedback, P/PI, offset; stability | hot-water tank on/off, P, PI; variance and target |
| 02 | C&L Ch. 2-3 | balances; Laplace; partial fractions; root locations | Ex. 3.1-3.5 inverted in SymPy |
| 03 | C&L Ch. 4-6 | thermometer; fitting tau; linearization; tanks in series | existing content, walkthroughs added |
| 04 | C&L Ch. 7-8 | second-order systems; transport lag and Pade; block diagrams | FOPDT fit to four tanks |
| 05 | C&L Ch. 9-11, 26 | **slot** | Ch. 26 missing |
| 06 | C&L Ch. 12-14 | P and PI; measurement lag; Routh; root locus | exact Ex. 14.1 crossings next to the book's graphical ones |
| 07 | C&L Ch. 15 | substitution rule; Bode; PI/PD and dead time | AR and phase measured from simulation |
| 08 | C&L Ch. 16 | Bode criterion; margins; Ziegler-Nichols | dead time as a `deque` |
| 09 | C&L Ch. 17; Cecil 2-6 | **slot** | Cecil Ch. 2 missing |
| 10 | C&L Ch. 18 | merits and tuning rules; step/pulse/doublet fits; ARX; ML entry 1 | minimum-ITAE tuning matches Table 18.5; random forest fails outside its data |
| 11 | C&L Ch. 20 | kettle; absorber; exchanger (method of lines); ML entry 2 | physics vs black box vs grey box at unseen flows |
| 12 | C&L Ch. 21-22 | **slot** | Ch. 22 missing |
| 13 | C&L Ch. 23; Cecil 7, 8.1 | interacting systems; RGA and pairing; decoupling; multiloop stability | MIMO without slycot (state space + `solve_ivp`) |
| 14 | C&L Ch. 24-25 | **slot** | Ch. 25 missing |
| 15 | Cecil 8.2-8.3 | Smith predictor; step-response models and DMC; QDMC, move suppression, GEKKO; ML entry 4 | least squares vs ridge FIR models judged inside the controller |

Every built notebook passed the linter, executed top to bottom, and its
static deck reported 0 overflowing slides at 1024x768 in `check_slides.py`.
Walkthrough numbers were checked against the executed outputs. Where the
book reads values off a graph, the lecture shows the exact value next to the
book's (e.g. Ex. 14.1, Ex. 16.4, Kc,u in Sec. 16.1).
