#!/usr/bin/env python3
"""Site checks for palousewaterpros.com. Run from the repo root: python3 tools/validate.py

Checks every *.html page for: well-formed markup, exactly one <h1>, lang and
viewport, title and meta-description length, canonical and og:url matching the
filename, og:image, valid JSON-LD, internal links and anchors that resolve,
consistent phone numbers, no Washington-side service claims, no prices or
turnaround promises, and CSS that matches the page family's template. Also
checks that sitemap.xml lists every page and only real pages.

Exit status is non-zero when any check fails.
"""
import json
import os
import re
import sys
from html.parser import HTMLParser
from xml.etree import ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SITE = "https://palousewaterpros.com/"
CALL = "tel:+12088834444"
TEXT = "sms:+19494566889"

# Page families share a <style> block byte-for-byte with their template.
LANDING_TEMPLATE = "princeton-potlatch-water-treatment.html"
ARTICLE_TEMPLATE = "palouse-well-water-guide.html"
FAMILY = {
    LANDING_TEMPLATE: "landing",
    "troy-deary-bovill-water-treatment.html": "landing",
    "genesee-water-treatment.html": "landing",
    "kendrick-juliaetta-water-treatment.html": "landing",
    "moscow-city-water-treatment.html": "landing",
    "iron-manganese-removal-moscow-idaho.html": "landing",
    "water-softener-moscow-idaho.html": "landing",
    "sulfur-smell-well-water-moscow-idaho.html": "landing",
    "reverse-osmosis-drinking-water-moscow-idaho.html": "landing",
    "water-testing-moscow-idaho.html": "landing",
    "faq.html": "landing-plus",  # landing CSS plus its own <details> rules
    ARTICLE_TEMPLATE: "article",
    "how-to-read-a-well-water-test-idaho.html": "article",
    "buying-a-home-with-a-well-latah-county.html": "article",
    "well-tested-positive-for-coliform-what-to-do.html": "article",
    "water-softener-salt-guide.html": "article",
    "new-construction-water-system-planning.html": "article",
    # index.html and water-quiz.html have their own CSS.
}

BANNED = ["Pullman", "Whitman", "Washington", "24/7", "same day", "same-day"]
BANNED_EXEMPT = {"water-quiz.html"}  # the quiz names the Washington side to say it is out of area
JS_PHONE_PAGES = {"water-quiz.html"}  # phone links are built in JavaScript; no JSON-LD


class Parser(HTMLParser):
    VOID = {"meta", "link", "br", "img", "input", "hr", "path", "source", "rect", "circle", "use"}

    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.h1, self.ids = [], [], 0, {}
        self.imgs_without_alt = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if "id" in attrs:
            self.ids[attrs["id"]] = self.ids.get(attrs["id"], 0) + 1
        if tag == "img" and attrs.get("alt") is None:
            self.imgs_without_alt += 1
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"unexpected </{tag}> at line {self.getpos()[0]}")


def style_of(html):
    m = re.search(r"<style>(.*?)</style>", html, re.S)
    return m.group(1) if m else None


def strip_code(html):
    html = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    return re.sub(r"<style.*?</style>", "", html, flags=re.S)


def check_page(name, html, all_files, ids_by_file):
    issues = []
    p = Parser()
    p.feed(html)
    issues += p.errors[:3]
    if p.stack:
        issues.append(f"unclosed tags: {p.stack[-4:]}")
    if p.h1 != 1:
        issues.append(f"{p.h1} <h1> elements")
    dups = [k for k, v in p.ids.items() if v > 1]
    if dups:
        issues.append(f"duplicate ids {dups}")
    if p.imgs_without_alt:
        issues.append(f"{p.imgs_without_alt} <img> without alt")
    if '<html lang="en">' not in html:
        issues.append("missing lang=en")
    if 'name="viewport"' not in html:
        issues.append("missing viewport meta")

    title = re.search(r"<title>(.*?)</title>", html, re.S)
    tlen = len(re.sub("&amp;", "&", title.group(1))) if title else 0
    if not title or tlen > 70:
        issues.append(f"title length {tlen} (max 70)")
    desc = re.search(r'<meta name="description" content="([^"]*)"', html)
    dlen = len(desc.group(1)) if desc else 0
    if not 120 <= dlen <= 165:
        issues.append(f"meta description length {dlen} (want 120-165)")

    expected = SITE if name == "index.html" else SITE + name
    canon = re.search(r'<link rel="canonical" href="([^"]*)"', html)
    if not canon or canon.group(1) != expected:
        issues.append(f"canonical is {canon.group(1) if canon else None}, want {expected}")
    og = re.search(r'property="og:url" content="([^"]*)"', html)
    if not og or og.group(1) != expected:
        issues.append("og:url missing or wrong")
    if 'property="og:image"' not in html:
        issues.append("missing og:image")

    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if not blocks and name not in JS_PHONE_PAGES:
        issues.append("no JSON-LD")
    for i, b in enumerate(blocks):
        try:
            json.loads(b)
        except Exception as e:
            issues.append(f"JSON-LD block {i} invalid: {e}")

    for href in set(re.findall(r'href="([^"]+)"', html)):
        if href.startswith(("http", "tel:", "sms:", "mailto:", "'")) or "' +" in href:
            continue
        path, _, anchor = href.partition("#")
        target = path or name
        if target not in all_files:
            issues.append(f"broken link {href}")
            continue
        if anchor and anchor != "top" and anchor not in ids_by_file.get(target, set()):
            issues.append(f"missing anchor {href}")

    if name in JS_PHONE_PAGES:
        if 'PHONE_TEL = "+12088834444"' not in html or 'PHONE_SMS = "+19494566889"' not in html:
            issues.append("quiz phone constants changed")
    else:
        if CALL not in html or TEXT not in html:
            issues.append("missing call or text link")
        for other in set(re.findall(r'href="((?:tel|sms):[^"?]+)', html)) - {CALL, TEXT}:
            issues.append(f"unexpected phone link {other}")

    text = strip_code(html)
    if name not in BANNED_EXEMPT:
        for w in BANNED:
            if w in text:
                issues.append(f"contains {w!r}")
    if re.search(r"\$\d", text):
        issues.append("contains a dollar amount")

    fam = FAMILY.get(name)
    css = style_of(html)
    if fam == "landing" and css != style_of(open(LANDING_TEMPLATE).read()):
        issues.append(f"CSS differs from {LANDING_TEMPLATE}")
    elif fam == "landing-plus" and (css or "").find(style_of(open(LANDING_TEMPLATE).read()).strip()) < 0:
        issues.append(f"CSS does not contain {LANDING_TEMPLATE}'s CSS")
    elif fam == "article" and css != style_of(open(ARTICLE_TEMPLATE).read()):
        issues.append(f"CSS differs from {ARTICLE_TEMPLATE}")
    return issues


def main():
    files = sorted(f for f in os.listdir(".") if f.endswith(".html"))
    all_files = set(os.listdir("."))
    ids_by_file = {}
    htmls = {}
    for f in files:
        htmls[f] = open(f, encoding="utf-8").read()
        ids_by_file[f] = set(re.findall(r'\sid="([^"]+)"', htmls[f]))

    failed = 0
    for f in files:
        issues = check_page(f, htmls[f], all_files, ids_by_file)
        status = "OK" if not issues else "FAIL"
        print(f"{status:4} {f}")
        for i in issues:
            print(f"       - {i}")
        failed += bool(issues)

    # sitemap
    try:
        root = ET.parse("sitemap.xml").getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = {u.find("s:loc", ns).text for u in root.findall("s:url", ns)}
        listed = {l.replace(SITE, "") or "index.html" for l in locs}
        missing = set(files) - listed
        extra = listed - set(files)
        if missing or extra:
            failed += 1
            print(f"FAIL sitemap.xml missing={sorted(missing)} extra={sorted(extra)}")
        else:
            print(f"OK   sitemap.xml ({len(locs)} urls)")
    except Exception as e:
        failed += 1
        print(f"FAIL sitemap.xml: {e}")

    print("\nAll checks passed." if not failed else f"\n{failed} file(s) with problems.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
