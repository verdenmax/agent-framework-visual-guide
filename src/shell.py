"""Shared HTML shell (CSS design system + bilingual nav) for the Agent Framework guide.

Bilingual model: every lesson's content is a ``{"zh": html, "en": html}`` dict.
Both languages are emitted into the page wrapped in ``.i18n[data-lang]`` blocks;
a tiny inline script toggles ``<html data-lang>`` and persists the choice in
``localStorage`` (key ``af-guide-lang``). No backend; works via file://.
"""

import base64

# ---- favicon (inline SVG, base64): rounded square + "AF" wordmark ----
_FAVICON_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
    "<rect width='32' height='32' rx='7' fill='#0078d4'/>"
    "<text x='16' y='22' font-family='system-ui,sans-serif' font-size='13'"
    " font-weight='700' fill='#fff' text-anchor='middle'>AF</text></svg>"
)
FAVICON = "data:image/svg+xml;base64," + base64.b64encode(_FAVICON_SVG.encode()).decode()

SITE_NAME = "Agent Framework 图解教程 · Visual Guide"


def bi(zh, en):
    """Inline bilingual span pair (only the active language shows)."""
    return (
        f'<span class="i18n" data-lang="zh">{zh}</span>'
        f'<span class="i18n" data-lang="en">{en}</span>'
    )


def biblock(zh, en):
    """Block-level bilingual pair."""
    return (
        f'<div class="i18n" data-lang="zh">{zh}</div>\n'
        f'<div class="i18n" data-lang="en">{en}</div>'
    )


def head_meta(title, description):
    """SEO / social meta tags + favicon + early language init for a page <head>."""
    t = title.replace('"', "&quot;")
    d = description.replace('"', "&quot;")
    return (
        f'<meta name="description" content="{d}">\n'
        f'<meta name="theme-color" content="#0078d4">\n'
        f'<link rel="icon" type="image/svg+xml" href="{FAVICON}">\n'
        f'<meta property="og:type" content="article">\n'
        f'<meta property="og:site_name" content="{SITE_NAME}">\n'
        f'<meta property="og:title" content="{t}">\n'
        f'<meta property="og:description" content="{d}">\n'
        f'<meta name="twitter:card" content="summary">\n'
        f'<meta name="twitter:title" content="{t}">\n'
        f'<meta name="twitter:description" content="{d}">\n'
        f"{LANG_HEAD}"
    )


# Ordered list of all pages: (filename, {zh,en} title, {zh,en} part label)
P1 = {"zh": "第一部分 · 宏观全景", "en": "Part 1 · Big Picture"}
P2 = {"zh": "第二部分 · 用户视角", "en": "Part 2 · User's View"}
P3 = {"zh": "第三部分 · 内部源码", "en": "Part 3 · Internals"}
P4 = {"zh": "第四部分 · 进阶实战", "en": "Part 4 · Advanced"}
P5 = {"zh": "第五部分 · 自己动手做 Agent", "en": "Part 5 · Build Your Own"}
P6 = {"zh": "第六部分 · 协议与生态", "en": "Part 6 · Protocols & Ecosystem"}
P7 = {"zh": "第七部分 · 番外篇", "en": "Part 7 · Bonus"}
P8 = {"zh": "第八部分 · 速查", "en": "Part 8 · Quick Reference"}

PAGES = [
    ("01-what-is-agent-framework.html", {"zh": "Agent Framework 是什么", "en": "What is Agent Framework"}, P1),
    ("02-monorepo.html", {"zh": "Monorepo 全景", "en": "Monorepo Tour"}, P1),
    ("03-lifecycle.html", {"zh": "一次 run() 的生命周期", "en": "Lifecycle of a Run"}, P1),
    ("04-messages.html", {"zh": "消息与内容", "en": "Messages & Content"}, P2),
    ("05-chat-models.html", {"zh": "ChatClient 与创建 Agent", "en": "ChatClient & Creating Agents"}, P2),
    ("06-tools.html", {"zh": "工具 Tools", "en": "Tools"}, P2),
    ("07-sessions-memory.html", {"zh": "会话与记忆", "en": "Sessions & Memory"}, P2),
    ("08-agent-internals.html", {"zh": "Agent 内部", "en": "Agent Internals"}, P3),
    ("09-chatclient-internals.html", {"zh": "ChatClient 内部", "en": "ChatClient Internals"}, P3),
    ("10-tool-internals.html", {"zh": "工具调用内部", "en": "Tool-Calling Internals"}, P3),
    ("11-middleware.html", {"zh": "中间件 Middleware", "en": "Middleware"}, P3),
    ("12-workflows.html", {"zh": "Workflows 工作流引擎", "en": "Workflows Engine"}, P3),
    ("13-orchestration.html", {"zh": "编排模式", "en": "Orchestration Patterns"}, P3),
    ("14-streaming-observability.html", {"zh": "流式与可观测性", "en": "Streaming & Observability"}, P3),
    ("15-contributing.html", {"zh": "读源码 / 调试 / 测试 / 贡献", "en": "Read, Debug, Test, Contribute"}, P4),
    ("29-devui.html", {"zh": "DevUI 可视化调试", "en": "DevUI Visual Debugging"}, P4),
    ("30-observability.html", {"zh": "可观测性深入", "en": "Observability Deep-Dive"}, P4),
    ("16-providers.html", {"zh": "接入各家模型", "en": "Model Providers"}, P5),
    ("17-declarative.html", {"zh": "声明式 Agent（YAML）", "en": "Declarative Agents (YAML)"}, P5),
    ("18-custom-middleware.html", {"zh": "写自己的中间件", "en": "Writing Your Own Middleware"}, P5),
    ("19-durability-hitl.html", {"zh": "检查点 · 人在环 · 持久化", "en": "Checkpointing, HITL & Durability"}, P5),
    ("20-capstone.html", {"zh": "端到端实战：多 Agent 工作流", "en": "Capstone: A Multi-Agent Workflow"}, P5),
    ("28-memory-backends.html", {"zh": "记忆后端", "en": "Memory Backends"}, P5),
    ("23-skills.html", {"zh": "Agent Skills 技能系统", "en": "Agent Skills"}, P6),
    ("24-mcp.html", {"zh": "MCP 工具协议", "en": "MCP Tool Protocol"}, P6),
    ("25-hosted-agents.html", {"zh": "Foundry 托管 Agent", "en": "Foundry Hosted Agents"}, P6),
    ("26-a2a-agui.html", {"zh": "A2A + AG-UI 协议", "en": "A2A & AG-UI Protocols"}, P6),
    ("27-eval-timetravel.html", {"zh": "评估与时间旅行", "en": "Evaluation & Time-Travel"}, P6),
    ("21-vs-others.html", {"zh": "横向对比：AF vs 其他框架", "en": "AF vs Other Frameworks"}, P7),
    ("22-stack-map.html", {"zh": "全栈坐标系 & 学习地图", "en": "Full-Stack Map & Learning Path"}, P7),
    ("31-glossary.html", {"zh": "术语表 · 速查", "en": "Glossary & Quick Reference"}, P8),
]

INDEX_FILE = "index.html"

CSS = r"""
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #f6f7f9; --panel: #ffffff; --panel-2: #f0f2f5; --ink: #1d2129;
  --muted: #5b6470; --faint: #8a939f; --line: #e1e5ea;
  --accent: #0078d4; --accent-soft: #e1effb; --accent-ink: #0a4a86;
  --blue: #2563eb; --blue-soft: #e7efff; --amber: #b4690e; --amber-soft: #fdf1dd;
  --purple: #7c3aed; --purple-soft: #f0e9ff; --red: #d23f3f; --red-soft: #fbe6e6;
  --code-bg: #0f172a; --code-ink: #e2e8f0; --code-line: #1e293b;
  --shadow: 0 1px 2px rgba(16,24,40,.06), 0 8px 24px rgba(16,24,40,.06);
  --radius: 14px;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0e1116; --panel: #161b22; --panel-2: #1c232c; --ink: #e6edf3;
    --muted: #9aa6b2; --faint: #6e7a86; --line: #2a323c;
    --accent: #4aa3e8; --accent-soft: #102a40; --accent-ink: #9fcdf2;
    --blue: #6ea8fe; --blue-soft: #16243f; --amber: #e0a44a; --amber-soft: #33270f;
    --purple: #b794f6; --purple-soft: #271a40; --red: #f08080; --red-soft: #3a1a1a;
    --code-bg: #0a0f1a; --code-ink: #d8e2f0; --code-line: #14202f;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 10px 30px rgba(0,0,0,.35);
  }
}
html { scroll-behavior: smooth; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC",
    "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
  background: var(--bg); color: var(--ink); line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; }
code, .mono { font-family: "SF Mono", "JetBrains Mono", "Fira Code", ui-monospace, Menlo, Consolas, monospace; }

/* ---- bilingual visibility ---- */
html[data-lang="zh"] .i18n[data-lang="en"],
html[data-lang="en"] .i18n[data-lang="zh"] { display: none !important; }
.langtoggle { cursor: pointer; font-size: .72rem; font-weight: 700; color: var(--accent);
  background: var(--accent-soft); border: 1px solid var(--accent); border-radius: 999px;
  padding: .2rem .7rem; white-space: nowrap; }
.langtoggle:hover { background: var(--accent); color: #fff; }

/* ---- top progress bar ---- */
.topbar {
  position: sticky; top: 0; z-index: 50; background: var(--panel);
  border-bottom: 1px solid var(--line); backdrop-filter: blur(8px);
}
.topbar-inner {
  max-width: 960px; margin: 0 auto; padding: .7rem 1.25rem;
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}
.topbar .home { font-size: .82rem; color: var(--muted); font-weight: 600; display:flex; gap:.5rem; align-items:center; }
.topbar .home b { color: var(--accent); }
.topbar .pills { display: flex; align-items: center; gap: .5rem; }
.topbar .pill { font-size: .72rem; color: var(--muted); background: var(--panel-2);
  padding: .2rem .6rem; border-radius: 999px; border: 1px solid var(--line); white-space: nowrap; }
.progress { height: 3px; background: var(--panel-2); }
.progress > span { display: block; height: 100%; background: linear-gradient(90deg, var(--accent), var(--purple)); }

.wrap { max-width: 820px; margin: 0 auto; padding: 2.4rem 1.25rem 5rem; }

/* ---- hero ---- */
.hero { margin-bottom: 2rem; }
.hero .part { font-size: .76rem; letter-spacing: .08em; text-transform: uppercase;
  color: var(--accent); font-weight: 700; margin-bottom: .55rem; }
.hero h1 { font-size: 2.05rem; line-height: 1.2; letter-spacing: -.01em; font-weight: 750; }
.hero .lead { margin-top: .9rem; font-size: 1.06rem; color: var(--muted); }

h2 { font-size: 1.32rem; margin: 2.4rem 0 .9rem; letter-spacing: -.01em;
  display: flex; align-items: center; gap: .55rem; }
h2::before { content: ""; width: 4px; height: 1.05em; background: var(--accent); border-radius: 3px; display: inline-block; }
h3 { font-size: 1.05rem; margin: 1.4rem 0 .5rem; }
p { margin: .7rem 0; }
ul, ol { margin: .6rem 0 .6rem 1.3rem; }
li { margin: .3rem 0; }
strong { color: var(--ink); font-weight: 680; }
.inline { background: var(--panel-2); border: 1px solid var(--line); border-radius: 6px;
  padding: .08em .4em; font-size: .9em; color: var(--accent-ink); }

/* ---- callout cards ---- */
.card { border-radius: var(--radius); padding: 1.05rem 1.2rem; margin: 1.2rem 0;
  border: 1px solid var(--line); background: var(--panel); box-shadow: var(--shadow); }
.card .tag { font-size: .72rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
  display: inline-flex; align-items: center; gap: .4rem; margin-bottom: .5rem; }
.card.macro { border-left: 4px solid var(--blue); }
.card.macro .tag { color: var(--blue); }
.card.detail { border-left: 4px solid var(--purple); }
.card.detail .tag { color: var(--purple); }
.card.analogy { border-left: 4px solid var(--amber); background: var(--amber-soft); }
.card.analogy .tag { color: var(--amber); }
.card.key { border-left: 4px solid var(--accent); background: var(--accent-soft); }
.card.key .tag { color: var(--accent-ink); }
.card.warn { border-left: 4px solid var(--red); background: var(--red-soft); }
.card.warn .tag { color: var(--red); }
.card.spark { border-left: 4px solid #e0a000;
  background: linear-gradient(100deg, rgba(224,160,0,.12), transparent 70%); }
.card.spark .tag { color: #c98a00; }
@media (prefers-color-scheme: dark) { .card.spark .tag { color: #f0c050; } }

/* ---- code file callout ---- */
.codefile { margin: 1.2rem 0; border-radius: 12px; overflow: hidden; border: 1px solid var(--line);
  box-shadow: var(--shadow); }
.codefile .cf-head { display: flex; align-items: center; gap: .55rem; padding: .5rem .85rem;
  background: var(--panel-2); border-bottom: 1px solid var(--line); font-size: .8rem; }
.codefile .cf-head .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--accent); flex-shrink:0; }
.codefile .cf-head .path { font-family: ui-monospace, monospace; color: var(--ink); font-weight: 600; }
.codefile .cf-head .ln { margin-left: auto; color: var(--faint); font-size: .72rem; }
.codefile pre { background: var(--code-bg); color: var(--code-ink); padding: .9rem 1rem;
  overflow-x: auto; font-size: .82rem; line-height: 1.6; }
.codefile pre .cm { color: #7d8aa3; }
.codefile pre .kw { color: #c792ea; }
.codefile pre .fn { color: #82aaff; }
.codefile pre .st { color: #c3e88d; }
.codefile pre .nb { color: #f78c6c; }

pre.code { background: var(--code-bg); color: var(--code-ink); padding: .9rem 1rem; border-radius: 12px;
  overflow-x: auto; font-size: .83rem; line-height: 1.6; margin: 1.1rem 0; box-shadow: var(--shadow); }
pre.code .cm { color: #7d8aa3; } pre.code .kw { color: #c792ea; }
pre.code .fn { color: #82aaff; } pre.code .st { color: #c3e88d; } pre.code .nb { color: #f78c6c; }

/* ---- collapsible accordion (details/summary) ---- */
.accordion { border: 1px solid var(--line); border-radius: 12px; background: var(--panel);
  margin: .7rem 0; box-shadow: var(--shadow); overflow: hidden; }
.accordion > summary { cursor: pointer; padding: .85rem 1.1rem; font-weight: 650; font-size: .96rem;
  list-style: none; display: flex; align-items: center; gap: .6rem; user-select: none; }
.accordion > summary::-webkit-details-marker { display: none; }
.accordion > summary::after { content: "\25B6"; font-size: .68rem; color: var(--accent);
  margin-left: auto; transition: transform .15s ease; }
.accordion[open] > summary::after { transform: rotate(90deg); }
.accordion > summary:hover { background: var(--panel-2); }
.accordion[open] > summary { border-bottom: 1px solid var(--line); }
.accordion .badge-num { background: var(--accent-soft); color: var(--accent-ink);
  width: 1.6rem; height: 1.6rem; border-radius: 7px; display: inline-flex; align-items: center;
  justify-content: center; font-size: .82rem; font-weight: 700; flex-shrink: 0; }
.accordion .hint { font-size: .72rem; color: var(--faint); font-weight: 400; }
.acc-body { padding: .9rem 1.1rem 1.1rem; }
.acc-intro { color: var(--muted); font-size: .9rem; margin: .2rem 0 .4rem; }
.qa { margin: 1rem 0; }
.qa:first-child { margin-top: .3rem; }
.qa .q { font-weight: 680; font-size: .9rem; display: flex; gap: .45rem; align-items: center; margin-bottom: .3rem; }
.qa .a { color: var(--muted); font-size: .9rem; }
.qa .a strong { color: var(--ink); }
.qa pre.code { margin: .5rem 0 0; font-size: .78rem; }

/* ---- flow diagram ---- */
.flow { display: flex; align-items: stretch; gap: 0; flex-wrap: wrap; margin: 1.3rem 0;
  background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 1.2rem 1rem; box-shadow: var(--shadow); }
.flow .node { flex: 1 1 0; min-width: 110px; text-align: center; padding: .7rem .5rem;
  border-radius: 10px; background: var(--panel-2); border: 1px solid var(--line); }
.flow .node .nt { font-weight: 700; font-size: .92rem; }
.flow .node .nd { font-size: .76rem; color: var(--muted); margin-top: .2rem; }
.flow .node.hl { background: var(--accent-soft); border-color: var(--accent); }
.flow .arrow { align-self: center; color: var(--faint); font-size: 1.3rem; padding: 0 .35rem; }

/* vertical flow */
.vflow { margin: 1.3rem 0; }
.vflow .step { display: flex; gap: .9rem; position: relative; padding-bottom: 1.1rem; }
.vflow .step:not(:last-child)::before { content:""; position:absolute; left: 15px; top: 34px; bottom: -2px;
  width: 2px; background: var(--line); }
.vflow .num { width: 32px; height: 32px; border-radius: 50%; background: var(--accent); color: #fff;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .85rem; flex-shrink: 0; z-index:1; }
.vflow .sc h4 { margin: .25rem 0 .2rem; font-size: 1rem; }
.vflow .sc p { margin: .15rem 0; font-size: .92rem; color: var(--muted); }
.vflow .sc .mono { font-size: .8rem; color: var(--accent-ink); }

/* layered architecture */
.layers { margin: 1.3rem 0; display: flex; flex-direction: column; gap: .55rem; }
.layer { border-radius: 12px; padding: .85rem 1.1rem; border: 1px solid var(--line); background: var(--panel);
  box-shadow: var(--shadow); }
.layer .lh { display: flex; align-items: center; gap: .6rem; }
.layer .lh .badge { font-size: .7rem; font-weight: 700; padding: .12rem .5rem; border-radius: 999px; }
.layer .lh .name { font-weight: 700; font-family: ui-monospace, monospace; }
.layer .ld { font-size: .85rem; color: var(--muted); margin-top: .35rem; }
.layer.l-core { border-left: 4px solid var(--accent); } .layer.l-core .badge { background: var(--accent-soft); color: var(--accent-ink); }
.layer.l-main { border-left: 4px solid var(--blue); } .layer.l-main .badge { background: var(--blue-soft); color: var(--blue); }
.layer.l-part { border-left: 4px solid var(--purple); } .layer.l-part .badge { background: var(--purple-soft); color: var(--purple); }
.layer.l-app { border-left: 4px solid var(--amber); } .layer.l-app .badge { background: var(--amber-soft); color: var(--amber); }

/* two-column compare */
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.2rem 0; }
@media (max-width: 640px) { .cols { grid-template-columns: 1fr; } }
.col { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 1rem 1.1rem; box-shadow: var(--shadow); }
.col h4 { margin: 0 0 .4rem; font-size: .95rem; }

table.t { width: 100%; border-collapse: collapse; margin: 1.1rem 0; font-size: .9rem;
  background: var(--panel); border-radius: 12px; overflow: hidden; box-shadow: var(--shadow); }
table.t th, table.t td { padding: .6rem .8rem; text-align: left; border-bottom: 1px solid var(--line); }
table.t th { background: var(--panel-2); font-size: .8rem; letter-spacing: .02em; }
table.t tr:last-child td { border-bottom: none; }
table.t td.mono, table.t td .mono { font-family: ui-monospace, monospace; font-size: .82rem; color: var(--accent-ink); }

/* footer nav */
.footnav { display: flex; justify-content: space-between; gap: 1rem; margin-top: 3rem;
  padding-top: 1.4rem; border-top: 1px solid var(--line); }
.footnav a { flex: 1; padding: .85rem 1.1rem; border-radius: 12px; border: 1px solid var(--line);
  background: var(--panel); box-shadow: var(--shadow); transition: .15s; }
.footnav a:hover { border-color: var(--accent); transform: translateY(-1px); }
.footnav a.next { text-align: right; }
.footnav .dir { font-size: .72rem; color: var(--faint); text-transform: uppercase; letter-spacing: .05em; }
.footnav .ttl { font-weight: 700; color: var(--ink); margin-top: .15rem; }
.footnav a.disabled { opacity: .35; pointer-events: none; }

/* index page */
.toc { display: grid; gap: .7rem; margin-top: 1.6rem; }
.toc-part { font-size: .78rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  color: var(--accent); margin: 1.4rem 0 .2rem; }
.toc a { display: flex; align-items: center; gap: .9rem; padding: .85rem 1.05rem; border-radius: 12px;
  background: var(--panel); border: 1px solid var(--line); box-shadow: var(--shadow); transition: .15s; }
.toc a:hover { border-color: var(--accent); transform: translateX(3px); }
.toc .n { width: 30px; height: 30px; border-radius: 8px; background: var(--accent-soft); color: var(--accent-ink);
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .85rem; flex-shrink: 0; }
.toc .tt { font-weight: 650; color: var(--ink); }
.toc .ts { font-size: .8rem; color: var(--muted); margin-left: auto; text-align: right; }
.hero.index h1 { font-size: 2.3rem; }
.legend { display:flex; gap:1.2rem; flex-wrap:wrap; margin-top:1rem; font-size:.8rem; color:var(--muted); }
.legend span { display:flex; align-items:center; gap:.4rem; }
.legend i { width:12px; height:12px; border-radius:3px; display:inline-block; }
.pdf-btn { display:inline-flex; align-items:center; gap:.4rem; padding:.55rem 1.1rem;
  background:var(--accent); color:#fff; border-radius:10px; font-size:.9rem; font-weight:650;
  box-shadow:var(--shadow); transition:.15s; }
.pdf-btn:hover { background:var(--accent-ink); transform:translateY(-1px); }
/* self-test quizzes (appended to each lesson by quizzes.render) */
.selftest { margin: 2.2rem 0 0; border-top: 2px dashed var(--line); padding-top: 1.2rem; }
.selftest > h2 { margin-top: .2rem; }
.quiz { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--blue);
  border-radius: 12px; padding: .9rem 1.1rem; margin: 1rem 0; box-shadow: var(--shadow); }
.quiz .qn { font-weight: 650; }
.quiz ol.opts { list-style: upper-alpha; margin: .55rem 0 .6rem 1.5rem; padding: 0; }
.quiz ol.opts li { margin: .3rem 0; padding-left: .15rem; }
.quiz details.accordion { margin: .5rem 0 0; }
.selftest code { font-family: ui-monospace, monospace; font-size: .9em; color: var(--accent-ink);
  background: var(--accent-soft); padding: 0 .28em; border-radius: 4px; }
"""

# Early language init (in <head>, before render, to avoid a flash of both languages).
LANG_HEAD = (
    "<script>try{var l=localStorage.getItem('af-guide-lang')||'zh';"
    "document.documentElement.setAttribute('data-lang',l);}catch(e){}</script>"
)

# Language toggle wiring (page tail).
LANG_SCRIPT = """
(function(){
  function cur(){return document.documentElement.getAttribute('data-lang')||'zh';}
  function set(l){
    document.documentElement.setAttribute('data-lang',l);
    try{localStorage.setItem('af-guide-lang',l);}catch(e){}
    document.querySelectorAll('.langtoggle').forEach(function(b){
      b.textContent=(l==='zh'?'EN':'中');
      b.setAttribute('aria-label', l==='zh'?'Switch to English':'切换到中文');
    });
  }
  document.querySelectorAll('.langtoggle').forEach(function(b){
    b.addEventListener('click',function(){set(cur()==='zh'?'en':'zh');});
  });
  set(cur());
})();
"""


def page(filename, content, standalone=False, home_href=None):
    """Wrap a lesson's ``{"zh":..,"en":..}`` content in the full HTML shell + nav."""
    idx = next(i for i, p in enumerate(PAGES) if p[0] == filename)
    _fname, title, part = PAGES[idx]
    total = len(PAGES)
    pct = int((idx + 1) / total * 100)
    home = home_href or INDEX_FILE

    if idx > 0:
        pt = PAGES[idx - 1][1]
        prev_link = (
            f'<a class="prev" data-nav="{PAGES[idx-1][0]}">'
            f'<div class="dir">{bi("← 上一课", "← Prev")}</div>'
            f'<div class="ttl">{bi(pt["zh"], pt["en"])}</div></a>'
        )
    else:
        prev_link = (
            f'<a class="prev" data-nav="{home}">'
            f'<div class="dir">{bi("← 返回", "← Back")}</div>'
            f'<div class="ttl">{bi("目录", "Contents")}</div></a>'
        )
    if idx + 1 < total:
        nt = PAGES[idx + 1][1]
        next_link = (
            f'<a class="next" data-nav="{PAGES[idx+1][0]}">'
            f'<div class="dir">{bi("下一课 →", "Next →")}</div>'
            f'<div class="ttl">{bi(nt["zh"], nt["en"])}</div></a>'
        )
    else:
        next_link = (
            f'<a class="next" data-nav="{home}">'
            f'<div class="dir">{bi("完成 →", "Done →")}</div>'
            f'<div class="ttl">{bi("返回目录", "Back to Contents")}</div></a>'
        )

    nav_tag = "" if standalone else f"<script>{NAV_SCRIPT}</script>"
    page_title = f'{idx+1:02d} · {title["zh"]} — {title["en"]} · {SITE_NAME}'
    desc = f'{part["zh"]}｜{title["zh"]}（{title["en"]}）：面向新手的 Agent Framework 图解教程，配真实源码对应与设计亮点。'
    body_content = biblock(content["zh"], content["en"])
    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
{head_meta(page_title, desc)}
<style>{CSS}</style>
</head><body>
<div class="topbar">
  <div class="topbar-inner">
    <a class="home" data-nav="{home}">📘 {bi("Agent Framework 图解教程 · ", "Agent Framework Visual Guide · ")}<b>{bi("目录", "Contents")}</b></a>
    <div class="pills">
      <span class="pill">{bi(part["zh"], part["en"])}</span>
      <span class="pill">{idx+1:02d} / {total:02d}</span>
      <span class="langtoggle">EN</span>
    </div>
  </div>
  <div class="progress"><span style="width:{pct}%"></span></div>
</div>
<div class="wrap">
  <div class="hero">
    <div class="part">{bi(part["zh"], part["en"])}</div>
    <h1>{bi(title["zh"], title["en"])}</h1>
  </div>
  {body_content}
  <div class="footnav">{prev_link}{next_link}</div>
</div>
{nav_tag}
<script>{LANG_SCRIPT}</script>
</body></html>"""
    if standalone:
        html = html.replace('data-nav="', 'href="')
    return html


# Per-lesson subtitle shown on the index (bilingual).
SUBTITLES = {
    "01-what-is-agent-framework.html": {"zh": "解决什么问题 · 核心心智模型", "en": "What it solves · core mental model"},
    "02-monorepo.html": {"zh": "core + provider 包；Python/.NET 对照", "en": "core + provider packages; Python/.NET"},
    "03-lifecycle.html": {"zh": "从你的代码到 LLM 的完整数据流", "en": "from your code to the LLM and back"},
    "04-messages.html": {"zh": "Message · Role · Content", "en": "Message · Role · Content"},
    "05-chat-models.html": {"zh": "as_agent · run / stream", "en": "as_agent · run / stream"},
    "06-tools.html": {"zh": "@tool 装饰器 · 工具调用", "en": "@tool decorator · tool calls"},
    "07-sessions-memory.html": {"zh": "AgentSession · ContextProvider", "en": "AgentSession · ContextProvider"},
    "08-agent-internals.html": {"zh": "BaseAgent 调用链 · AgentResponse", "en": "BaseAgent chain · AgentResponse"},
    "09-chatclient-internals.html": {"zh": "BaseChatClient · get_response", "en": "BaseChatClient · get_response"},
    "10-tool-internals.html": {"zh": "函数 → schema → call → result", "en": "func → schema → call → result"},
    "11-middleware.html": {"zh": "agent / function / chat 三层", "en": "agent / function / chat layers"},
    "12-workflows.html": {"zh": "Executor / Edge / WorkflowBuilder", "en": "Executor / Edge / WorkflowBuilder"},
    "13-orchestration.html": {"zh": "Sequential/Concurrent/Handoff/Group/Magentic", "en": "Sequential/Concurrent/Handoff/Group/Magentic"},
    "14-streaming-observability.html": {"zh": "流式输出 · OpenTelemetry", "en": "streaming · OpenTelemetry"},
    "15-contributing.html": {"zh": "uv · poe · 测试 · DevUI", "en": "uv · poe · tests · DevUI"},
    "29-devui.html": {"zh": "serve() · 请求/消息/trace 可视化", "en": "serve() · visualize requests/messages/traces"},
    "30-observability.html": {"zh": "OpenTelemetry · span 树 · trace/metric", "en": "OpenTelemetry · span tree · trace/metric"},
    "16-providers.html": {"zh": "Foundry/AzureOpenAI/OpenAI/Anthropic/Ollama", "en": "Foundry/AzureOpenAI/OpenAI/Anthropic/Ollama"},
    "17-declarative.html": {"zh": "YAML 定义 Agent", "en": "define agents in YAML"},
    "18-custom-middleware.html": {"zh": "自定义 AgentMiddleware / FunctionMiddleware", "en": "custom Agent/Function middleware"},
    "19-durability-hitl.html": {"zh": "checkpoint · 人在环 · DurableTask", "en": "checkpoint · HITL · DurableTask"},
    "20-capstone.html": {"zh": "把所有零件拼成一个工作流", "en": "assemble everything into one workflow"},
    "28-memory-backends.html": {"zh": "Redis / Mem0 / Cosmos · ContextProvider", "en": "Redis / Mem0 / Cosmos · ContextProvider"},
    "23-skills.html": {"zh": "Skill / SkillResource / SkillScript", "en": "Skill / SkillResource / SkillScript"},
    "24-mcp.html": {"zh": "MCPStdioTool · MCPStreamableHTTPTool", "en": "MCPStdioTool · MCPStreamableHTTPTool"},
    "25-hosted-agents.html": {"zh": "2 行代码部署到 Foundry", "en": "deploy to Foundry in 2 lines"},
    "26-a2a-agui.html": {"zh": "Agent 互调 · Agent-UI 交互", "en": "agent-to-agent · agent-to-UI"},
    "27-eval-timetravel.html": {"zh": "Evaluator · Workflow replay", "en": "Evaluator · Workflow replay"},
    "21-vs-others.html": {"zh": "AF vs LangGraph / AutoGen / SK", "en": "AF vs LangGraph / AutoGen / SK"},
    "22-stack-map.html": {"zh": "编排流派 · 全栈分层 · 你在哪", "en": "orchestration schools · stack layers · you are here"},
    "31-glossary.html": {"zh": "核心术语 · 源码位置 · 概念索引", "en": "core terms · source locations · concept index"},
}


def index_page(standalone=False, lesson_prefix=""):
    parts = {}
    order = []
    for i, (fname, title, part) in enumerate(PAGES):
        key = part["zh"]
        parts.setdefault(key, ("", []))
        if key not in order:
            order.append(key)
            parts[key] = (part, [])
        parts[key][1].append((i + 1, fname, title))

    blocks = []
    for key in order:
        part, items = parts[key]
        blocks.append(f'<div class="toc-part">{bi(part["zh"], part["en"])}</div>')
        for num, fname, title in items:
            sub = SUBTITLES.get(fname, {"zh": "", "en": ""})
            blocks.append(
                f'<a data-nav="{lesson_prefix}{fname}"><span class="n">{num:02d}</span>'
                f'<span class="tt">{bi(title["zh"], title["en"])}</span>'
                f'<span class="ts">{bi(sub["zh"], sub["en"])}</span></a>'
            )
    toc = "\n".join(blocks)

    nav_tag = "" if standalone else f"<script>{NAV_SCRIPT}</script>"
    page_title = f"{SITE_NAME} · 从零理解整个项目"
    desc = ("从零理解整个 Microsoft Agent Framework 项目的中英双语图解教程：宏观结构、"
            "用户用法、内部源码、自己动手做 Agent。8 部分 31 课，每课配真实代码对应与设计亮点。")
    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
{head_meta(page_title, desc)}
<style>{CSS}</style>
</head><body>
<div class="topbar">
  <div class="topbar-inner">
    <span class="home">📘 {bi("Agent Framework 图解教程", "Agent Framework Visual Guide")}</span>
    <div class="pills">
      <span class="pill">{bi(f"共 {len(PAGES)} 课 · {len(order)} 个部分", f"{len(PAGES)} lessons · {len(order)} parts")}</span>
      <span class="langtoggle">EN</span>
    </div>
  </div>
  <div class="progress"><span style="width:100%"></span></div>
</div>
<div class="wrap">
  <div class="hero index">
    <div class="part">{bi("从零开始 · 面向完全新手", "From scratch · for complete beginners")}</div>
    <h1>{bi("用图解理解整个 Agent Framework 项目", "Understand the whole Agent Framework, visually")}</h1>
    {biblock(
        '<p class="lead">这套教程分四步带你走：先建立<strong>宏观全景</strong>，再从<strong>用户视角</strong>学会使用，'
        '然后深入<strong>内部源码</strong>看它如何实现，最后教你<strong>自己动手做 Agent</strong>。'
        '每一课都配有真实的代码文件对应，既有宏观理解，也有细节拆解。中英双语，一键切换。</p>',
        '<p class="lead">Four steps: build the <strong>big picture</strong>, learn it from the '
        '<strong>user\'s view</strong>, dive into the <strong>internals</strong>, then '
        '<strong>build your own agent</strong>. Every lesson maps to real source files, with both '
        'macro intuition and detailed breakdowns. Bilingual, one-click toggle.</p>'
    )}
    <div class="legend">
      <span><i style="background:var(--blue)"></i>{bi("宏观理解", "Big picture")}</span>
      <span><i style="background:var(--purple)"></i>{bi("细节 / 源码", "Detail / source")}</span>
      <span><i style="background:var(--amber)"></i>{bi("生活类比", "Analogy")}</span>
      <span><i style="background:var(--accent)"></i>{bi("关键要点", "Key points")}</span>
    </div>
    <div style="margin-top:1.1rem; display:flex; gap:.6rem; flex-wrap:wrap">
      <a href="agent-framework-visual-guide.zh.pdf" class="pdf-btn">📄 {bi("下载中文 PDF", "Chinese PDF")}</a>
      <a href="agent-framework-visual-guide.en.pdf" class="pdf-btn">📄 {bi("下载英文 PDF", "English PDF")}</a>
    </div>
  </div>
  <div class="toc">{toc}</div>
</div>
{nav_tag}
<script>{LANG_SCRIPT}</script>
</body></html>"""
    if standalone:
        html = html.replace('data-nav="', 'href="')
    return html


# Legacy nav script (only used when standalone=False; kept for parity).
NAV_SCRIPT = """
(function(){
  var onDisk = location.protocol === 'file:';
  document.querySelectorAll('[data-nav]').forEach(function(a){
    var n = a.getAttribute('data-nav');
    a.setAttribute('href', onDisk ? n : '/files/' + n);
  });
})();
"""
