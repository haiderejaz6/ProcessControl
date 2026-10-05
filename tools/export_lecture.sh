#!/usr/bin/env bash
# Build, check, execute and publish one notebook (lecture or derivations).
#
#   tools/export_lecture.sh lectures/04-second-order/PSE-823_Lecture-04_....ipynb
#   tools/export_lecture.sh lectures/derivations/PSE-823_Lecture-04_Derivations.ipynb
#
# Steps:
#   1. lint against the course format          (tools/check_lecture.py)
#   2. execute in place, clear `predict` cells (tools/run_lecture.py)
#   3. export reveal.js slides                 (nbconvert)
#   4. localize the deck: local reveal.js/MathJax, theme, no CDN
#                                              (tools/localize_slides.py)
#   5. write the Colab copy                    (tools/make_colab.py)
#   6. render the static read page             (tools/export_read.sh)
#
# Run from anywhere; paths are resolved against the repo root.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NB_PATH="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
DIR="$(dirname "$NB_PATH")"
NB="$(basename "$NB_PATH")"
BASE="${NB%.ipynb}"
ASSETS="$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$ROOT/assets" "$DIR")"

LINT_FLAGS=""
case "$DIR" in */derivations) LINT_FLAGS="--derivations" ;; esac

echo "== $NB =="
python3 "$ROOT/tools/check_lecture.py" "$NB_PATH" $LINT_FLAGS
python3 "$ROOT/tools/run_lecture.py" "$NB_PATH"
(cd "$DIR" && jupyter nbconvert --log-level=WARN --to slides "$NB" \
    --output "${BASE}_slides" \
    --SlidesExporter.reveal_url_prefix="$ASSETS/reveal.js")
python3 "$ROOT/tools/localize_slides.py" "$DIR/${BASE}_slides.slides.html" "$ASSETS"
python3 "$ROOT/tools/make_colab.py" "$NB_PATH"
"$ROOT/tools/export_read.sh" "$NB_PATH"
