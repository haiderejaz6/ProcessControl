#!/usr/bin/env python3
"""
Walk every slide of an exported reveal.js deck in headless Chromium and
report slides whose content is taller than the 1024x768 frame.

Usage:  python3 tools/check_slides.py DECK.slides.html [--shots DIR]
        --shots saves a PNG of every overflowing slide (and --all, of all).
Needs:  pip install playwright   (Chromium is preinstalled in the course
        cloud environment; elsewhere run `playwright install chromium`).
"""
import argparse
import os
import sys

from playwright.sync_api import sync_playwright

JS_MEASURE = """() => {
  const s = Reveal.getCurrentSlide();
  const h = s.clientHeight;
  const title = (s.querySelector('h1,h2,h3') || {}).innerText || '';
  // the theme makes the present slide scroll when it is too tall
  return {used: s.scrollHeight, h: h, title: title};
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--shots")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    url = "file://" + os.path.abspath(args.deck)
    bad = []
    with sync_playwright() as p:
        exe = "/opt/pw-browsers/chromium"
        kw = {"executable_path": exe} if os.path.exists(exe) else {}
        browser = p.chromium.launch(**kw)
        page = browser.new_page(viewport={"width": 1024, "height": 768})
        page.goto(url)
        page.wait_for_function("window.Reveal && Reveal.isReady()")
        page.evaluate("Reveal.configure({transition: 'none'})")
        page.wait_for_timeout(1500)
        n = 0
        while True:
            page.evaluate("Reveal.getCurrentSlide().querySelectorAll('.fragment')"
                          ".forEach(f => f.classList.add('visible'))")
            page.wait_for_timeout(250)
            m = page.evaluate(JS_MEASURE)
            idx = page.evaluate("JSON.stringify(Reveal.getIndices())")
            over = m["used"] > m["h"] + 16
            if over:
                bad.append((idx, round(m["used"]), m["title"][:60]))
            if args.shots and (over or args.all):
                os.makedirs(args.shots, exist_ok=True)
                page.screenshot(path=os.path.join(args.shots, f"slide_{n:03d}.png"))
            n += 1
            if page.evaluate("Reveal.isLastSlide()"):
                break
            page.evaluate("Reveal.next()")
            # step past any fragments of the same slide
            while page.evaluate("Reveal.availableFragments().next"):
                page.evaluate("Reveal.next()")
        browser.close()

    print(f"{os.path.basename(args.deck)}: {n} slides, {len(bad)} overflowing")
    for idx, used, title in bad:
        print(f"  {idx}  {used}px  {title}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
