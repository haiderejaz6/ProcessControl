#!/usr/bin/env python3
"""
Render the site's generated parts from tools/site_data.py:

  * the lecture cards in index.html          (between LECTURES markers)
  * the companion cards in derivations.html  (between DERIVATIONS markers)
  * chapters.html, the textbook chapter list (whole page)
  * the "Chapters" nav link on every page

Run after adding or changing a lecture:  python3 tools/build_site.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from site_data import LECTURES, chapters, lectures_using  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "haiderejaz6/ProcessControl"

ICON = {
    "slides": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8m-4-4v4"/></svg>',
    "colab": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="7" cy="12" r="3.2"/><circle cx="17" cy="12" r="3.2"/><path d="M9.4 9.6A4.8 4.8 0 0 1 17 7M14.6 14.4A4.8 4.8 0 0 1 7 17"/></svg>',
    "binder": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M10.3 8.3l5 3.7-5 3.7z" fill="currentColor" stroke="none"/></svg>',
    "read": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z"/><path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/></svg>',
    "nb": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>',
}


def actions(path, base):
    """The five buttons for a notebook at lectures/<path>/<base>.ipynb."""
    rel = f"lectures/{path}/{base}"
    enc = rel.replace("/", "%2F")
    return f"""            <div class="card-actions">
              <a class="btn btn-primary" href="{rel}_slides.slides.html">
                {ICON['slides']}
                View slides
              </a>
              <a class="btn btn-outline" href="{rel}_read.html">
                {ICON['read']}
                Read
              </a>
              <a class="btn btn-outline" href="https://colab.research.google.com/github/{REPO}/blob/main/{rel}_colab.ipynb">
                {ICON['colab']}
                Open in Colab
              </a>
              <a class="btn btn-outline" href="https://mybinder.org/v2/gh/{REPO}/main?urlpath=notebooks%2F{enc}.ipynb">
                {ICON['binder']}
                Open in Binder
              </a>
              <a class="btn btn-quiet" href="{rel}.ipynb">
                {ICON['nb']}
                Notebook (.ipynb)
              </a>
            </div>"""


def card(n, title, meta, body, slot=False):
    cls = "lecture-card is-slot" if slot else "lecture-card"
    return f"""        <li class="{cls}">
          <div class="card-index" aria-hidden="true">{n:02d}</div>
          <div class="card-body">
            <h3 class="card-title">
              <span class="sr-only">Lecture {n}: </span>{title}
            </h3>
            <p class="card-meta">{meta}</p>
{body}
          </div>
        </li>"""


def slot_note(L):
    return (f'            <p class="slot-note">Coming later in the term. '
            f'{L["why"]}.</p>')


def lecture_cards():
    out = []
    for L in LECTURES:
        if L.get("status") == "slot":
            out.append(card(L["n"], L["title"], L["meta"], slot_note(L), True))
        else:
            out.append(card(L["n"], L["title"], L["meta"],
                            actions(L["folder"], L["base"])))
    return "\n".join(out)


def derivation_cards():
    out = []
    for L in LECTURES:
        n = L["n"]
        title = f"Lecture {n} &mdash; Derivations and Worked Solutions"
        if L.get("status") == "slot":
            out.append(card(n, title, L["meta"], slot_note(L), True))
        else:
            out.append(card(n, title, f"Companion to Lecture {n} &middot; {L['deriv']}",
                            actions("derivations",
                                    f"PSE-823_Lecture-{n:02d}_Derivations")))
    return "\n".join(out)


def replace_between(html, name, inner):
    pat = re.compile(rf"(<!-- {name}:BEGIN -->\n).*?([ \t]*<!-- {name}:END -->)",
                     re.S)
    assert pat.search(html), f"{name} markers missing"
    return pat.sub(lambda m: m.group(1) + inner + "\n" + m.group(2), html)


def published():
    return sum(1 for L in LECTURES if L.get("status") != "slot")


def update_index():
    p = os.path.join(ROOT, "index.html")
    html = open(p).read()
    html = replace_between(html, "LECTURES", lecture_cards())
    html = re.sub(r"<li><b>\d+</b> lectures published</li>",
                  f"<li><b>{published()}</b> of 15 lectures published</li>", html)
    html = re.sub(r'(<span class="count">)[^<]*(</span>)',
                  rf"\g<1>{published()} of 15 published\g<2>", html, count=1)
    open(p, "w").write(html)


def update_derivations():
    p = os.path.join(ROOT, "derivations.html")
    html = open(p).read()
    html = replace_between(html, "DERIVATIONS", derivation_cards())
    html = re.sub(r'(<span class="count">)[^<]*(</span>)',
                  rf"\g<1>{published()} of 15 published\g<2>", html, count=1)
    open(p, "w").write(html)


NAV = [("index.html", "Lectures"), ("derivations.html", "Derivations"),
       ("chapters.html", "Chapters"), ("resources.html", "Resources"),
       ("course-info.html", "Course info")]


def nav_html(current):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        links.append(f'      <a href="{href}"{cur}>{label}</a>')
    return '<nav class="nav" aria-label="Main">\n' + "\n".join(links) + "\n    </nav>"


def update_nav():
    for href, _ in NAV:
        p = os.path.join(ROOT, href)
        if not os.path.exists(p):
            continue
        html = open(p).read()
        html = re.sub(r'<nav class="nav" aria-label="Main">.*?</nav>',
                      lambda m: nav_html(href), html, count=1, flags=re.S)
        open(p, "w").write(html)


def chapter_rows(book):
    rows = []
    for ch in chapters():
        if ch["book"] != book:
            continue
        lects = lectures_using(ch["slug"])
        lect_html = ", ".join(f'<a href="index.html#lectures">L{n}</a>'
                              for n in lects) or "&mdash;"
        if ch["available"]:
            read = (f'<a class="ch-link" data-slug="{ch["slug"]}" '
                    f'href="chapters/{ch["slug"]}.html" hidden>Read</a>'
                    f'<span class="ch-status" data-slug="{ch["slug"]}">'
                    f'Private copy</span>')
        else:
            read = '<span class="ch-status">Not yet available</span>'
        rows.append(f"""          <tr>
            <td class="ch-num">{ch["num"]}</td>
            <td>{ch["title"]}<span class="ch-secs">{ch["sections"]}</span></td>
            <td class="ch-lect">{lect_html}</td>
            <td class="ch-read">{read}</td>
          </tr>""")
    return "\n".join(rows)


def chapter_table(book, heading_id, heading):
    return f"""    <section class="section" aria-labelledby="{heading_id}">
      <div class="section-head">
        <h2 id="{heading_id}">{heading}</h2>
        <span class="rule"></span>
      </div>
      <table class="chapter-table">
        <thead>
          <tr><th scope="col">Ch.</th><th scope="col">Title and sections</th>
          <th scope="col" class="ch-lect">Lectures</th><th scope="col">Text</th></tr>
        </thead>
        <tbody>
{chapter_rows(book)}
        </tbody>
      </table>
    </section>"""


def write_chapters_page():
    head = open(os.path.join(ROOT, "derivations.html")).read()
    head = head.split("<header class=\"hero\">")[0]
    head = re.sub(r"<title>.*?</title>",
                  "<title>PSE-823: Textbook Chapters</title>", head)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="PSE-823: Advanced Process '
                  'Dynamics and Control - textbook chapters and where each is '
                  'used in the lectures.">', head)
    head = re.sub(r'<nav class="nav" aria-label="Main">.*?</nav>',
                  lambda m: nav_html("chapters.html"), head, flags=re.S)
    foot = open(os.path.join(ROOT, "derivations.html")).read()
    foot = "<footer" + foot.split("<footer", 1)[1]
    body = f"""<header class="hero">
  <div class="wrap">
    <span class="eyebrow">Reading</span>
    <h1>Textbook Chapters</h1>
    <p class="lede">Every chapter of the two course textbooks, its sections, and the lectures that teach it.</p>
  </div>
</header>
<main id="main">
  <div class="wrap">
    <section class="section">
      <p class="notice">The chapter text is copyrighted, so it is not published on this site.
      It is rendered in the instructor's private copy of the course site, where the
      <b>Read</b> links open each chapter with its equations and figures.
      Students: use your copy of the textbook alongside the lecture slides.</p>
    </section>
{chapter_table("Coughanowr & LeBlanc", "coughanowr-heading",
               "Coughanowr &amp; LeBlanc, <i>Process Systems Analysis and Control</i> (3rd ed.)")}
{chapter_table("Cecil Smith", "cecil-heading",
               "Cecil L. Smith, <i>Advanced Process Control: Beyond Single-Loop Control</i>")}
  </div>
</main>
<!-- chapters/manifest.js exists only in a private copy built by
     tools/build_chapters.py; on the public site it is absent and every
     chapter stays marked "Private copy". -->
<script src="chapters/manifest.js"></script>
<script>
  (function () {{
    var have = (window.PSE823_CHAPTERS || []);
    document.querySelectorAll(".ch-link").forEach(function (a) {{
      if (have.indexOf(a.dataset.slug) >= 0) {{
        a.hidden = false;
        var s = document.querySelector('.ch-status[data-slug="' + a.dataset.slug + '"]');
        if (s) s.hidden = true;
      }}
    }});
  }})();
</script>
"""
    with open(os.path.join(ROOT, "chapters.html"), "w") as f:
        f.write(head + body + foot)


def main():
    update_index()
    update_derivations()
    write_chapters_page()
    update_nav()
    print(f"site rebuilt: {published()} lectures published, "
          f"{15 - published()} slots")


if __name__ == "__main__":
    main()
