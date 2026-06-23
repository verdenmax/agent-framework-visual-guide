"""Structural / consistency regression guard for the generated HTML (AF guide).

Run after build.py:
    cd src && python check_html.py

Exits non-zero on any ERROR (used by CI). WARN/INFO print but don't fail.
Checks each lesson + index:
* balanced tags (div/details/table/pre/summary/ul/ol/li) and details<->summary
* a <title> + meta description; exactly one <h1> per lesson
* both languages present (data-lang="zh" and data-lang="en" blocks)
* no unescaped '<' inside <pre> code blocks
* no double-escaped entities (&amp;lt; etc.) and no unescaped '&' in body text
* cross-references "第 N 课" within 1..MAX_LESSON (forward refs allowed)
* nav prev/next chain matches shell.PAGES order
* index TOC lists every page; '共 N 课 · N 个部分' pill matches PAGES
* registry CONTENT has non-empty zh+en for every PAGES filename (no orphan keys)
* every lesson has a self-test quiz; (WARN) key-points card, analogy card, enough diagrams
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import shell  # noqa: E402
from registry import CONTENT  # noqa: E402

PAGES = shell.PAGES
ORDER = [p[0] for p in PAGES]
TOTAL = len(PAGES)
MAX_LESSON = 31  # planned final lesson count; cross-refs may point forward
MIN_CONTENT = 80  # min chars of zh/en source content per lesson

PRE_INLINE = ("span", "strong", "b", "em", "u", "a")
SOFT_EXEMPT = {"31-glossary.html"}  # lessons exempt from soft content-density checks (e.g. glossary)

# Visual-block density (soft): containers that count as a "diagram/table".
DIAGRAM_CLASSES = ("layers", "vflow", "flow", "cols", "macro")
MIN_DIAGRAMS = 4  # per lesson, counting BOTH languages (soft WARN)

issues = []


def add(sev, f, msg):
    issues.append((sev, f, msg))


def check_balance(name, html, tag):
    o = len(re.findall(rf"<{tag}[\s>]", html))
    c = len(re.findall(rf"</{tag}>", html))
    if o != c:
        add("ERR", name, f"<{tag}> unbalanced: {o} open / {c} close")


def check_lesson(fname, html):
    for tag in ("div", "details", "table", "pre", "summary", "ul", "ol", "li"):
        check_balance(fname, html, tag)
    nd = len(re.findall(r"<details", html))
    ns = len(re.findall(r"<summary", html))
    if nd != ns:
        add("ERR", fname, f"details({nd}) != summary({ns})")
    h1 = len(re.findall(r"<h1", html))
    if h1 == 0:
        add("ERR", fname, "missing <h1>")
    elif h1 > 1:
        add("WARN", fname, f"{h1} <h1> (expected 1)")
    if "<title>" not in html:
        add("ERR", fname, "missing <title>")
    if 'name="description"' not in html:
        add("ERR", fname, "missing meta description")
    if 'data-lang="zh"' not in html:
        add("ERR", fname, "missing zh (data-lang) content")
    if 'data-lang="en"' not in html:
        add("ERR", fname, "missing en (data-lang) content")
    if fname not in SOFT_EXEMPT:
        if "关键要点" not in html and "Key points" not in html:
            add("WARN", fname, "no key-points card")
        if "card analogy" not in html:
            add("WARN", fname, "no analogy card")
        nvis = sum(html.count(f'class="{c}"') for c in DIAGRAM_CLASSES)
        nvis += html.count('<table class="t"')
        if nvis < MIN_DIAGRAMS:
            add("WARN", fname, f"only {nvis} visual blocks (want >= {MIN_DIAGRAMS}; add diagrams)")

    for pre in re.findall(r"<pre[^>]*>(.*?)</pre>", html, re.S):
        cleaned = re.sub(r"</?(?:%s)\b[^>]*>" % "|".join(PRE_INLINE), "", pre)
        if re.search(r"<(?!/)", cleaned):
            m = re.search(r"<(?!/).{0,20}", cleaned)
            add("ERR", fname, f"unescaped '<' in <pre>: {m.group(0)!r}")
            break

    # entity hygiene (on body only — strip embedded CSS/JS where '&'/'&&' are legal)
    body = re.sub(r"<style.*?</style>", "", html, flags=re.S)
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    md = re.search(r"&amp;(?:lt|gt|amp|quot|#x?[0-9a-fA-F]+);", body)
    if md:
        add("ERR", fname, f"double-escaped entity (write {md.group(0)[5:]!r} not {md.group(0)!r})")
    ua = re.search(r"&(?![a-zA-Z][a-zA-Z0-9]*;|#[0-9]+;|#x[0-9a-fA-F]+;)", body)
    if ua:
        add("ERR", fname, f"unescaped '&' (use &amp;): {body[max(0, ua.start() - 12):ua.start() + 6]!r}")

    for m in re.finditer(r"第\s*([0-9、,，~\-－\s]+?)\s*课", html):
        nums = [int(x) for x in re.findall(r"[0-9]+", m.group(1))]
        over = [n for n in nums if n == 0 or n > MAX_LESSON]
        if over:
            add("ERR", fname, f"course ref out of range: {m.group(0)!r} -> {over}")

    if fname in ORDER:
        idx = ORDER.index(fname)
        if idx + 1 < TOTAL and f'href="{ORDER[idx + 1]}"' not in html:
            add("ERR", fname, f"next link missing -> {ORDER[idx + 1]}")
        if idx > 0 and f'href="{ORDER[idx - 1]}"' not in html:
            add("ERR", fname, f"prev link missing -> {ORDER[idx - 1]}")


def main():
    for page in PAGES:
        fname = page[0]
        path = os.path.join(ROOT, "lessons", fname)
        if not os.path.exists(path):
            add("ERR", fname, "lesson file missing (run build.py)")
            continue
        with open(path, encoding="utf-8") as fh:
            check_lesson(fname, fh.read())

    # registry <-> PAGES alignment + non-empty bilingual SOURCE content.
    for page in PAGES:
        fname = page[0]
        c = CONTENT.get(fname)
        if c is None:
            add("ERR", fname, "no registry CONTENT entry")
            continue
        for lang in ("zh", "en"):
            if len(c.get(lang, "").strip()) < MIN_CONTENT:
                add("ERR", fname, f"{lang} content missing or too short")
    for fname in CONTENT:
        if fname not in ORDER:
            add("ERR", "registry", f"CONTENT key not in PAGES: {fname}")

    # every lesson must have a self-test quiz (M5/M6 coverage guard)
    import quizzes  # noqa: E402
    for fname, _t, _p in PAGES:
        q = quizzes.QUIZZES.get(fname)
        if not q or not q.get("mcq"):
            add("ERR", fname, "missing self-test quiz (quizzes.QUIZZES entry with mcq)")

    index_path = os.path.join(ROOT, shell.INDEX_FILE)
    with open(index_path, encoding="utf-8") as fh:
        idx = fh.read()
    for fname, title, part in PAGES:
        if fname not in idx:
            add("ERR", "index.html", f"TOC missing entry {fname}")
        if title["zh"] not in idx:
            add("WARN", "index.html", f"TOC missing zh title {title['zh']!r}")
        if title["en"] not in idx:
            add("WARN", "index.html", f"TOC missing en title {title['en']!r}")
    m = re.search(r"共 (\d+) 课 · (\d+) 个部分", idx)
    if m:
        if int(m.group(1)) != TOTAL:
            add("ERR", "index.html", f"count says {m.group(1)} but PAGES has {TOTAL}")
        nparts = len({p[2]["zh"] for p in PAGES})
        if int(m.group(2)) != nparts:
            add("ERR", "index.html", f"parts says {m.group(2)} but PAGES has {nparts}")
    else:
        add("WARN", "index.html", "could not find '共 N 课 · N 个部分' pill")

    errs = [i for i in issues if i[0] == "ERR"]
    warns = [i for i in issues if i[0] == "WARN"]
    rank = {"ERR": 0, "WARN": 1, "INFO": 2}
    for sev, f, msg in sorted(issues, key=lambda x: rank[x[0]]):
        print(f"  [{sev}] {f}: {msg}")
    print(f"\nChecked {TOTAL} lessons + index - {len(errs)} error(s), {len(warns)} warning(s).")
    if errs:
        print("structural check FAILED")
        return 1
    print("structural check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
