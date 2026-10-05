#!/usr/bin/env bash
# Render one executed notebook as a static, scrollable "read" page
# (<base>_read.html next to the notebook), the in-browser reading view
# linked from each card's "Read" button. MathJax comes from assets/.
#
#   tools/export_read.sh lectures/04-second-order/PSE-823_Lecture-04_....ipynb
#
# Called by export_lecture.sh; run it directly to refresh a read page
# without re-executing the notebook.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NB_PATH="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
DIR="$(dirname "$NB_PATH")"
NB="$(basename "$NB_PATH")"
BASE="${NB%.ipynb}"
ASSETS="$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$ROOT/assets" "$DIR")"

(cd "$DIR" && jupyter nbconvert --log-level=ERROR --to html "$NB" \
    --output "${BASE}_read" \
    --HTMLExporter.theme=light \
    --HTMLExporter.mathjax_url="$ASSETS/mathjax/MathJax.js?config=TeX-AMS_CHTML-full,Safe")
echo "   read page: ${BASE}_read.html"
