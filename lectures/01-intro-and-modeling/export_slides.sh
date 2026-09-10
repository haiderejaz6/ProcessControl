#!/usr/bin/env bash
# Rebuilds the notebook, executes it, exports to reveal.js slides, and points
# it at the repo's shared assets/ (reveal.js + MathJax), then rewrites the
# nbconvert bootstrap to plain <script> tags so the deck actually initializes
# as a slideshow when opened directly (double-clicked / file://), not just
# when served over http.
#
# Run from inside this lecture's folder: ./export_slides.sh
set -euo pipefail
cd "$(dirname "$0")"

NB=PSE-823_Lecture-01_Ch1-2.ipynb
SLIDES=PSE-823_Lecture-01_Ch1-2_slides.slides.html
ASSETS=../../assets   # shared reveal.js/ + mathjax/, relative to this lecture folder

echo "== Building notebook =="
python3 build_notebook.py

echo "== Executing notebook =="
jupyter nbconvert --to notebook --execute --output "$NB" "$NB"

echo "== Exporting to reveal.js slides (shared repo assets) =="
jupyter nbconvert --to slides "$NB" --output "${SLIDES%.slides.html}" \
    --SlidesExporter.reveal_url_prefix="$ASSETS/reveal.js"

echo "== Localizing MathJax + removing jquery/require/mermaid =="
python3 - "$ASSETS" <<'PYEOF'
import sys
assets = sys.argv[1]
path = "PSE-823_Lecture-01_Ch1-2_slides.slides.html"
with open(path) as f:
    html = f.read()

old = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/latest.js?config=TeX-AMS_CHTML-full,Safe'
new = f'{assets}/mathjax/MathJax.js?config=TeX-AMS_CHTML-full,Safe'
assert html.count(old) == 1, "MathJax CDN line not found / already replaced"
html = html.replace(old, new)

old_head = '''<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.1.10/require.min.js"></script><script type="module">
  import mermaid from 'https://cdnjs.cloudflare.com/ajax/libs/mermaid/11.10.0/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>'''
assert html.count(old_head) == 1, "jquery/require/mermaid head block not found / already replaced"
html = html.replace(old_head, '')

old_bootstrap = '''<script>
require(
    {
      // it makes sense to wait a little bit when you are loading
      // reveal from a cdn in a slow connection environment
      waitSeconds: 15
    },
    [
      "REVEAL_JS_PATH/dist/reveal.js",
      "REVEAL_JS_PATH/plugin/notes/notes.js"
    ],

    function(Reveal, RevealNotes){
        // Full list of configuration options available here: https://github.com/hakimel/reveal.js#configuration
        Reveal.initialize({
            controls: true,
            progress: true,
            history: true,
            transition: "slide",
            slideNumber: "",
            plugins: [RevealNotes],
            width: 960,
			      height: 700,

        });

        var update = function(event){
          if(MathJax.Hub.getAllJax(Reveal.getCurrentSlide())){
            MathJax.Hub.Rerender(Reveal.getCurrentSlide());
          }
        };

        Reveal.addEventListener('slidechanged', update);

        function setScrollingSlide() {
            var scroll = false
            if (scroll === true) {
              var h = $('.reveal').height() * 0.95;
              $('section.present').find('section')
                .filter(function() {
                  return $(this).height() > h;
                })
                .css('height', 'calc(95vh)')
                .css('overflow-y', 'scroll')
                .css('margin-top', '20px');
            }
        }

        // check and set the scrolling slide every time the slide change
        Reveal.addEventListener('slidechanged', setScrollingSlide);
    }
);
</script>'''.replace("REVEAL_JS_PATH", assets + "/reveal.js")

new_bootstrap = f'''<script src="{assets}/reveal.js/dist/reveal.js"></script>
<script src="{assets}/reveal.js/plugin/notes/notes.js"></script>
<script>
    Reveal.initialize({{
        controls: true,
        progress: true,
        history: true,
        transition: "slide",
        slideNumber: "",
        plugins: [RevealNotes],
        width: 960,
        height: 700,
    }});

    var update = function(event){{
      if (window.MathJax && MathJax.Hub && MathJax.Hub.getAllJax(Reveal.getCurrentSlide())){{
        MathJax.Hub.Rerender(Reveal.getCurrentSlide());
      }}
    }};

    Reveal.addEventListener('slidechanged', update);
</script>'''
assert html.count(old_bootstrap) == 1, "reveal.js bootstrap block not found / already replaced"
html = html.replace(old_bootstrap, new_bootstrap)

with open(path, "w") as f:
    f.write(html)
print("Localized MathJax; removed jquery/require.js/mermaid; replaced RequireJS bootstrap with plain script tags.")
PYEOF

echo "== Injecting custom lecture theme CSS =="
python3 - "$ASSETS" <<'PYEOF'
import sys
assets = sys.argv[1]
path = "PSE-823_Lecture-01_Ch1-2_slides.slides.html"
with open(f"{assets}/reveal-lecture-theme.css") as f:
    css = f.read()
with open(path) as f:
    html = f.read()
assert "PSE-823 reveal.js lecture theme" not in html, "Theme already injected"
style_tag = f"\n<style>\n{css}\n</style>\n</head>"
html = html.replace("</head>", style_tag, 1)
with open(path, "w") as f:
    f.write(html)
print("Theme CSS injected.")
PYEOF

echo "== Verifying no external CDN references remain =="
if grep -qE "cdnjs\.cloudflare\.com|unpkg\.com|jsdelivr\.net|fonts\.googleapis\.com" "$SLIDES"; then
    echo "WARNING: external CDN references still present!"
    grep -nE "cdnjs\.cloudflare\.com|unpkg\.com|jsdelivr\.net|fonts\.googleapis\.com" "$SLIDES"
    exit 1
else
    echo "OK: fully self-contained, no external CDN dependencies."
fi

echo "== Done: $SLIDES =="
