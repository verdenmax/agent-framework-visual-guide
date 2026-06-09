"""Build single-page print-ready HTML for PDF rendering (one per language).

Output: ``print.zh.html`` and ``print.en.html`` at the project root. Render to
PDF with headless Chromium, e.g.:

    chromium --headless=new --no-sandbox --no-pdf-header-footer \
        --print-to-pdf=agent-framework-visual-guide.zh.pdf \
        --virtual-time-budget=20000 file://$PWD/print.zh.html

No third-party dependencies.
"""
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import shell  # noqa: E402
from registry import CONTENT  # noqa: E402

PRINT_CSS = r"""
/* ===== print / PDF overrides ===== */
@page { size: A4; margin: 15mm 14mm 16mm; }
html, body { height: auto !important; overflow: visible !important; background: #fff; }
.wrap { max-width: 100%; padding: 0; }
.hint { display: none !important; }
.accordion > summary { cursor: default; }
.accordion > summary::after { display: none; }
.accordion[open] > summary { border-bottom: 1px solid var(--line); }
.card, .codefile, pre.code, table.t, .flow, .vflow .step, .layer,
.accordion, .qa, .cols, .mockup { break-inside: avoid; }
h2, h3, h4 { break-after: avoid; }
/* hide language toggle and bilingual blocks for the other language */
.langtoggle { display: none !important; }

.print-cover { break-after: page; min-height: 90vh; display: flex; flex-direction: column;
  justify-content: center; text-align: center; }
.print-cover .emoji { font-size: 3.2rem; }
.print-cover h1 { font-size: 2.4rem; margin: 1rem 0 .4rem; border: none; }
.print-cover .sub { color: var(--muted); font-size: 1.05rem; }
.print-cover .meta { margin-top: 2rem; color: var(--faint); font-size: .9rem; }

.print-toc { break-after: page; }
.print-toc h2 { margin-top: 0; }
.print-toc .tp { font-size: .82rem; font-weight: 700; letter-spacing: .05em;
  color: var(--accent); margin: 1.1rem 0 .3rem; }
.print-toc ol { margin: 0; padding-left: 1.4rem; }
.print-toc li { margin: .2rem 0; }

.print-lesson { break-before: page; padding-top: .2rem; }
.lesson-head { border-bottom: 2px solid var(--accent); padding-bottom: .5rem; margin-bottom: 1.2rem; }
.lesson-head .lp { font-size: .72rem; letter-spacing: .08em; text-transform: uppercase;
  color: var(--accent); font-weight: 700; }
.lesson-head h1 { font-size: 1.7rem; margin: .25rem 0 0; border: none; }
.lesson-head .ln { color: var(--faint); font-weight: 600; }
"""

LANG_LABELS = {
    "zh": {
        "title": "Agent Framework 图解教程",
        "subtitle": "从零理解整个项目 · 宏观 → 用法 → 源码 → 自己动手做 Agent",
        "toc_heading": "目录",
        "author": "verdenmax",
        "gen_prefix": "生成日期",
        "lesson_count": "共 {n} 课 · {p} 个部分 · 每课配真实代码对应与设计亮点",
    },
    "en": {
        "title": "Agent Framework Visual Guide",
        "subtitle": "Understand the whole project from scratch · Big picture → Usage → Internals → Build your own",
        "toc_heading": "Table of Contents",
        "author": "verdenmax",
        "gen_prefix": "Generated",
        "lesson_count": "{n} lessons · {p} parts · real source-code references in every lesson",
    },
}


def _toc_html(lang):
    parts, order = {}, []
    for i, (fname, title, part) in enumerate(shell.PAGES):
        key = part["zh"]
        parts.setdefault(key, (part, []))
        if key not in order:
            order.append(key)
        parts[key][1].append((i + 1, title[lang]))
    blocks = [f'<h2>{LANG_LABELS[lang]["toc_heading"]}</h2>']
    for key in order:
        part, items = parts[key]
        blocks.append(f'<div class="tp">{part[lang]}</div>')
        blocks.append("<ol>")
        for num, title_str in items:
            blocks.append(f'<li value="{num}">{title_str}</li>')
        blocks.append("</ol>")
    return "\n".join(blocks)


def build_print(lang):
    """Build a print-ready single-page HTML for the given language."""
    today = datetime.date.today().isoformat()
    labels = LANG_LABELS[lang]
    n_parts = len({p["zh"] for _, _, p in shell.PAGES})

    lessons = []
    for idx, (fname, title, part) in enumerate(shell.PAGES):
        content_html = CONTENT[fname][lang]
        content_html = content_html.replace(
            '<details class="accordion">', '<details class="accordion" open>'
        )
        lessons.append(
            f'<section class="print-lesson"><div class="wrap">'
            f'<div class="lesson-head"><div class="lp">{part[lang]}</div>'
            f'<h1><span class="ln">{idx+1:02d} ·</span> {title[lang]}</h1></div>'
            f"{content_html}</div></section>"
        )
    body = "\n".join(lessons)

    html_lang = "zh-CN" if lang == "zh" else "en"
    html = f"""<!DOCTYPE html>
<html lang="{html_lang}" data-lang="{lang}"><head>
<meta charset="utf-8">
<title>{labels["title"]}</title>
<style>{shell.CSS}{PRINT_CSS}</style>
</head><body>
<section class="print-cover">
  <div class="emoji">📘</div>
  <h1>{labels["title"]}</h1>
  <div class="sub">{labels["subtitle"]}</div>
  <div class="meta">{labels["lesson_count"].format(n=len(shell.PAGES), p=n_parts)}<br>
    {labels["gen_prefix"]} {today} · {labels["author"]} · MIT License</div>
</section>
<section class="print-toc"><div class="wrap">{_toc_html(lang)}</div></section>
{body}
</body></html>"""

    out = os.path.join(ROOT, f"print.{lang}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


if __name__ == "__main__":
    for lang in ("zh", "en"):
        path = build_print(lang)
        print(f"Wrote {path} ({len(shell.PAGES)} lessons, lang={lang})")
