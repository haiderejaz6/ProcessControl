#!/usr/bin/env python3
"""
Make an nbconvert reveal.js export self-contained and file://-safe.

nbconvert's default deck pulls MathJax, jQuery, RequireJS and mermaid from
CDNs and boots reveal.js through RequireJS, which often fails silently when
the HTML is opened by double-click. This script:

  * points MathJax at the repo's local copy (assets/mathjax)
  * removes the jQuery / RequireJS / mermaid head block
  * replaces the RequireJS bootstrap with plain <script> tags and a direct
    Reveal.initialize() at the course's 4:3 size (1024x768)
  * injects the course theme CSS (assets/reveal-lecture-theme.css)
  * fails if any CDN reference remains

Usage:  python3 tools/localize_slides.py DECK.slides.html ASSETS_REL_PATH
        (ASSETS_REL_PATH is assets/ relative to the deck, e.g. ../../assets)
"""
import os
import re
import sys

CDN = re.compile(r"cdnjs\.cloudflare\.com|unpkg\.com|jsdelivr\.net|"
                 r"fonts\.googleapis\.com")


def main():
    path, assets = sys.argv[1], sys.argv[2].rstrip("/")
    with open(path) as f:
        html = f.read()

    html, n = re.subn(
        r'https://cdnjs\.cloudflare\.com/ajax/libs/mathjax/[^/]+/latest\.js',
        f"{assets}/mathjax/MathJax.js", html)
    assert n == 1, "MathJax CDN line not found"

    html, n = re.subn(
        r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/jquery/[^"]*">'
        r'</script><script src="https://cdnjs\.cloudflare\.com/ajax/libs/'
        r'require\.js/[^"]*"></script><script type="module">.*?</script>',
        "", html, count=1, flags=re.S)
    assert n == 1, "jquery/require/mermaid head block not found"

    boot = f"""<script src="{assets}/reveal.js/dist/reveal.js"></script>
<script src="{assets}/reveal.js/plugin/notes/notes.js"></script>
<script>
    Reveal.initialize({{
        controls: true,
        progress: true,
        history: true,
        transition: "slide",
        slideNumber: "c/t",
        plugins: [RevealNotes],
        width: 1024,
        height: 768,
        margin: 0.04,
        center: false,
    }});
    Reveal.addEventListener('slidechanged', function () {{
      if (window.MathJax && MathJax.Hub &&
          MathJax.Hub.getAllJax(Reveal.getCurrentSlide())) {{
        MathJax.Hub.Rerender(Reveal.getCurrentSlide());
      }}
    }});
</script>"""
    html, n = re.subn(r"<script>\s*require\(.*?\n\);\s*</script>",
                      lambda m: boot, html, count=1, flags=re.S)
    assert n == 1, "RequireJS bootstrap block not found"

    theme = os.path.join(os.path.dirname(path), assets,
                         "reveal-lecture-theme.css")
    with open(theme) as f:
        css = f.read()
    html = html.replace("</head>", f"\n<style>\n{css}\n</style>\n</head>", 1)

    if CDN.search(html):
        sys.exit(f"ERROR: CDN reference left in {path}")
    with open(path, "w") as f:
        f.write(html)
    print(f"localized {os.path.basename(path)}")


if __name__ == "__main__":
    main()
