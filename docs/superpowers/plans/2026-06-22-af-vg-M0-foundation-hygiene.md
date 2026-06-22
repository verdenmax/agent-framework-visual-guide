# M0 · 基建与卫生 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为后续所有里程碑搭好地基——移植 quizzes 自测系统与 check_html 结构校验工具、清理游离文件、修正 Part 分组、更新 README 与许可——且**不改动任何课程正文**。

**Architecture:** 复用现有"纯 Python 生成 HTML"的零依赖管线。新增 `src/quizzes.py`（按语言渲染、确定性洗牌、导入即校验）由 `build.py`/`build_print.py` 在每课正文尾部追加；新增 `src/check_html.py`（结构回归守门，适配 AF 的 3 元组 PAGES 与 `.i18n[data-lang]` 双语模型）。Part 标签从 6 个修正为 7 个（新增"协议与生态""番外篇"），第 8 部分"速查"与 4 门新课留待 M6。

**Tech Stack:** Python 3（标准库 only：`os`/`re`/`sys`/`hashlib`/`base64`）；无第三方依赖；CI 用 GitHub Actions。

> **本里程碑后的真实结构 = 27 课 / 7 部分**（README 与 index 计数都按此写）。31 课 / 8 部分要到 M6 才成形。

---

## 背景速记（实现者必读）

- **被讲解源码**在 `../agent-framework/`（相对本仓库根）。本里程碑不引用源码，无需读它。
- **生成物已提交且必须同步**：改完 `src/` 必须 `cd src && python build.py && python build_print.py`，再提交 `index.html`/`lessons/`/`print.zh.html`/`print.en.html`。CI（`.github/workflows/ci.yml`）会因漂移而失败。
- **AF 双语模型**：每课内容是 `{"zh": html, "en": html}` 两个独立字符串；`shell.biblock()` 把它们包进 `<div class="i18n" data-lang="zh">…</div><div class="i18n" data-lang="en">…</div>`。**不是** `.lang-zh/.lang-en`。
- **AF 没有 `shell.esc`**：`head_meta` 直接 `.replace('"',"&quot;")`。`check_html.py` 不可调用 `shell.esc`。
- **PAGES 元组形状**：`(fname, {"zh","en"} 标题, {"zh","en"} part 标签)`，3 元组。part 在 `page[2]`。
- **现有 quiz/卫生现状**：`src/` 无任何 quiz 代码；`src/gen_part2.py` 与 `src/part5.py.backup` 被 git 跟踪（游离）；`src/__pycache__/*.pyc` 仅本地（已被 `.gitignore` 覆盖）。

---

## 文件结构（创建 / 修改 / 删除）

| 操作 | 文件 | 职责 |
|---|---|---|
| 创建 | `src/quizzes.py` | 每课自测题数据 + `render(fname,lang)` 按语言渲染 + `_shuffle` 确定性洗牌 + `_validate` 导入即校验 |
| 创建 | `src/check_html.py` | 结构回归守门（适配 AF 元组形状与 i18n 模型），0 错才过 |
| 创建 | `LICENSE-CONTENT` | 内容许可 CC BY 4.0 |
| 修改 | `src/shell.py` | ① 加 quiz CSS（`.selftest/.quiz/.qn/.opts`）② 新增 `P6`/`P7` part 标签并重挂 L23–27 与 L21–22 |
| 修改 | `src/build.py` | 每课正文 `+ quizzes.render(fname, lang)` |
| 修改 | `src/build_print.py` | 每课正文追加 quiz；封面许可文案改为双许可 |
| 修改 | `README.md` | 计数→27/7、Part 表、第三方免责声明、构建命令含 `check_html.py`、结构树 |
| 修改 | `.github/workflows/ci.yml` | 增跑 `python check_html.py` |
| 删除 | `src/gen_part2.py`、`src/part5.py.backup` | 游离脚本/备份 |
| 删除 | `src/__pycache__/`（本地） | 陈旧字节码 |
| 重生 | `index.html`、`lessons/*.html`、`print.zh.html`、`print.en.html` | 由 build 重新生成后提交 |

---

## Task 1: 清理游离文件

**Files:**
- Delete: `src/gen_part2.py`, `src/part5.py.backup`, `src/__pycache__/`

- [ ] **Step 1: 确认这两个脚本未被其它代码引用**

Run: `cd /home/verden/course/agent-framework-visual-guide && grep -rn "gen_part2\|part5\.py\.backup\|part5_temp" src/*.py`
Expected: 无输出（registry.py / build.py 等都不 import 它们）。

- [ ] **Step 2: 删除被 git 跟踪的游离文件 + 本地字节码**

```bash
cd /home/verden/course/agent-framework-visual-guide
git rm src/gen_part2.py src/part5.py.backup
rm -rf src/__pycache__
```

- [ ] **Step 3: 确认 .gitignore 已覆盖字节码（无需改动）**

Run: `grep -n "__pycache__\|py\[cod\]" .gitignore`
Expected: 命中 `__pycache__/` 与 `*.py[cod]`（已存在，确认即可）。

- [ ] **Step 4: 构建仍正常（删除无副作用）**

Run: `cd src && python build.py && python check_links.py`
Expected: `Wrote 28 files ...` 且 `✓ all N internal links resolve`，无报错。

- [ ] **Step 5: Commit**

```bash
cd /home/verden/course/agent-framework-visual-guide
git add -A
git commit -m "chore(M0): remove stray gen_part2.py and part5.py.backup"
```

---

## Task 2: 创建 `src/quizzes.py`（自测系统框架 + 1 课种子题）

**Files:**
- Create: `src/quizzes.py`

> 设计移植自 `../llama-cpp-visual-guide/src/quizzes.py`，但 M0 只放**框架 + 一课（L01）种子题**证明渲染链路；L02–L31 的题在 M2–M6 各自里程碑补。`render()` 对没有条目的课返回 `""`，故不影响其它课构建。

- [ ] **Step 1: 写出完整文件**

```python
"""Per-lesson bilingual self-test (自测题): design-insight MCQ + open prompts.

Schema per lesson::

    "NN-file.html": {
        "mcq": [
            {"q": {"zh","en"}, "opts": [{"zh","en"}, ...],
             "answer": <0-based index into opts as written>,
             "why": {"zh","en"}},
        ],
        "open": [{"zh","en"}, ...],
    }

``render(fname, lang)`` returns single-language HTML that build.py appends to the
bottom of that language's lesson body. Options are deterministically shuffled per
question (same permutation for zh and en, so the correct letter matches across
languages). Quiz text is raw HTML in a text context (like the lesson body): write
literal ``<``/``&`` as ``&lt;``/``&amp;`` or wrap code in ``<code>``.
"""
import hashlib

_HEAD = {"zh": "🧪 自测 · 想一想为什么这么设计", "en": "🧪 Self-test - think about the design"}
_SEE = {"zh": "看答案与解析", "en": "Show answer &amp; explanation"}
_CLICK = {"zh": "点击展开", "en": "click to expand"}
_ANS = {"zh": "答案：", "en": "Answer: "}
_SEP = {"zh": "。", "en": ". "}
_OPEN = {
    "zh": "💭 发散思考（没有标准答案，动手或动脑想想）",
    "en": "💭 Open questions (no single right answer - just think or try)",
}


def _shuffle(opts, answer, seed):
    """Deterministically permute opts (stable across builds); return
    (new_opts, new_answer_index) so the correct option lands in a varied slot."""
    order = sorted(
        range(len(opts)),
        key=lambda i: hashlib.md5(f"{seed}:{i}".encode("utf-8")).hexdigest(),
    )
    return [opts[i] for i in order], order.index(answer)


QUIZZES = {
    "01-what-is-agent-framework.html": {
        "mcq": [
            {
                "q": {
                    "zh": "Agent Framework 把“换一家模型厂商”变成基本只改一行代码。这主要靠的是什么设计？",
                    "en": "Agent Framework makes 'switch model vendor' basically a one-line change. Which design mainly enables that?",
                },
                "opts": [
                    {"zh": "它帮你自动训练模型", "en": "It trains the model for you"},
                    {
                        "zh": "统一的 ChatClient 抽象把厂商差异挡在同一接口后面",
                        "en": "A uniform ChatClient abstraction hides vendor differences behind one interface",
                    },
                    {"zh": "它把所有厂商的代码复制进你的项目", "en": "It copies every vendor's code into your project"},
                    {"zh": "它只支持一家厂商", "en": "It supports only one vendor"},
                ],
                "answer": 1,
                "why": {
                    "zh": "Agent 依赖抽象的 ChatClient，而非具体厂商 SDK；换厂商只是换一个 ChatClient 实现，Agent 与工具/记忆逻辑都不动——这正是“面向接口”的取舍。",
                    "en": "An Agent depends on the abstract ChatClient, not a concrete vendor SDK; switching vendors just swaps a ChatClient implementation while agent/tool/memory logic stays put - the classic 'program to an interface' tradeoff.",
                },
            },
            {
                "q": {
                    "zh": "下面哪一项**不是** Agent Framework 想替你抹平的“上生产”麻烦？",
                    "en": "Which is **not** one of the production headaches Agent Framework aims to smooth over?",
                },
                "opts": [
                    {"zh": "可观测性（OpenTelemetry）", "en": "Observability (OpenTelemetry)"},
                    {"zh": "检查点与人在环审批", "en": "Checkpointing and human-in-the-loop approval"},
                    {"zh": "替你决定该用哪个机器学习算法训练模型", "en": "Choosing which ML algorithm to train your model with"},
                    {"zh": "持久化 / 可恢复的工作流", "en": "Durable / resumable workflows"},
                ],
                "answer": 2,
                "why": {
                    "zh": "Agent Framework 负责模型“周边”的工程管道（编排、可观测、持久化、审批），**不**负责训练模型本身——训练不在它的职责范围。",
                    "en": "Agent Framework owns the engineering plumbing *around* the model (orchestration, observability, durability, approval); it does **not** train the model itself - training is out of scope.",
                },
            },
        ],
        "open": [
            {
                "zh": "假设你已经用某厂商 SDK 直接写了一个聊天脚本。请列出迁移到 Agent Framework 后，你认为最先会“消失”的三段样板代码，并说明各自由框架的哪个概念接管（ChatClient / Message / @tool / Workflow 任选）。",
                "en": "Suppose you already wrote a chat script directly against a vendor SDK. List the three pieces of boilerplate you expect to 'disappear' first after moving to Agent Framework, and say which framework concept (ChatClient / Message / @tool / Workflow) takes over each.",
            },
        ],
    },
}


def render(fname, lang):
    """Return the self-test HTML block for ``fname`` in ``lang`` ('' if none)."""
    data = QUIZZES.get(fname)
    if not data or not (data.get("mcq") or data.get("open")):
        return ""
    out = ['<div class="selftest">', f'<h2>{_HEAD[lang]}</h2>']
    for i, item in enumerate(data.get("mcq", []), 1):
        shuffled, ans = _shuffle(item["opts"], item["answer"], f"{fname}:{i}")
        opts = "\n".join(f"    <li>{o[lang]}</li>" for o in shuffled)
        letter = chr(65 + ans)
        out.append(
            f'<div class="quiz">\n'
            f'  <div class="qn">{i}. {item["q"][lang]}</div>\n'
            f'  <ol class="opts">\n{opts}\n  </ol>\n'
            f'  <details class="accordion">\n'
            f'    <summary>{_SEE[lang]} <span class="hint">{_CLICK[lang]}</span></summary>\n'
            f'    <div class="acc-body"><div class="qa"><div class="a">'
            f'<strong>{_ANS[lang]}{letter}</strong>{_SEP[lang]}{item["why"][lang]}'
            f"</div></div></div>\n"
            f"  </details>\n"
            f"</div>"
        )
    opens = data.get("open", [])
    if opens:
        lis = "\n".join(f"    <li>{o[lang]}</li>" for o in opens)
        out.append(
            '<div class="card spark">\n'
            f'  <div class="tag">{_OPEN[lang]}</div>\n'
            f"  <ul>\n{lis}\n  </ul>\n"
            "</div>"
        )
    out.append("</div>")
    return "\n".join(out)


def _validate():
    """Fail fast on authoring mistakes in QUIZZES (clear message names the lesson)."""
    for fname, data in QUIZZES.items():
        for qi, item in enumerate(data.get("mcq", []), 1):
            opts = item["opts"]
            if not (0 <= item["answer"] < len(opts)):
                raise ValueError(
                    f"quizzes[{fname!r}] Q{qi}: answer {item['answer']} out of range 0..{len(opts) - 1}"
                )
            for o in opts:
                if not ({"zh", "en"} <= o.keys()):
                    raise ValueError(f"quizzes[{fname!r}] Q{qi}: an option is missing zh/en")
            if not ({"zh", "en"} <= item["q"].keys() and {"zh", "en"} <= item["why"].keys()):
                raise ValueError(f"quizzes[{fname!r}] Q{qi}: q/why missing zh/en")
        for oi, o in enumerate(data.get("open", []), 1):
            if not ({"zh", "en"} <= o.keys()):
                raise ValueError(f"quizzes[{fname!r}] open{oi}: missing zh/en")


_validate()
```

- [ ] **Step 2: 导入即校验通过 + 渲染确定性自检**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide/src
python -c "import quizzes; z=quizzes.render('01-what-is-agent-framework.html','zh'); e=quizzes.render('01-what-is-agent-framework.html','en'); assert 'selftest' in z and 'selftest' in e; assert quizzes.render('99-none.html','zh')==''; print('quizzes OK')"
```
Expected: 打印 `quizzes OK`（导入触发 `_validate()` 不报错；缺失课返回空串）。

- [ ] **Step 3: 验证中英“正确答案字母一致”（同序洗牌）**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide/src
python -c "
import re, quizzes
f='01-what-is-agent-framework.html'
def letters(lang):
    html=quizzes.render(f,lang)
    return re.findall(r'答案：([A-D])|Answer: ([A-D])', html)
zh=[a or b for a,b in letters('zh')]; en=[a or b for a,b in letters('en')]
assert zh==en and zh, (zh,en)
print('letters match across langs:', zh)
"
```
Expected: 打印两版一致的答案字母列表（如 `['B','C']`）。

- [ ] **Step 4: Commit**

```bash
cd /home/verden/course/agent-framework-visual-guide
git add src/quizzes.py
git commit -m "feat(M0): add quizzes self-test framework + L01 seed quiz"
```

---

## Task 3: 给 `src/shell.py` 加 quiz 样式

**Files:**
- Modify: `src/shell.py`（在 CSS 块末尾、第 318–319 行 `.pdf-btn:hover {…}` 之后、闭合的 `"""`(第 319 行) 之前插入）

> quiz CSS 复用 AF 既有变量 `--panel/--line/--shadow/--blue/--accent-soft/--accent-ink`（均已在 `:root` 定义）。`.accordion/.acc-body/.qa/.a/.hint/.card/.spark/.tag` 已存在，只需补 `.selftest/.quiz/.qn/.opts`。

- [ ] **Step 1: 在 `.pdf-btn:hover { … }` 这一行之后插入 quiz CSS**

在 `src/shell.py` 中找到（约第 318 行）：
```css
.pdf-btn:hover { background:var(--accent-ink); transform:translateY(-1px); }
```
在其**下一行**插入：
```css
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
```

- [ ] **Step 2: shell 仍可正常导入/构建**

Run: `cd src && python -c "import shell; assert '.selftest' in shell.CSS and '.quiz ' in shell.CSS; print('css OK')"`
Expected: 打印 `css OK`。

- [ ] **Step 3: Commit**

```bash
cd /home/verden/course/agent-framework-visual-guide
git add src/shell.py
git commit -m "feat(M0): add self-test quiz CSS to shell design system"
```

---

## Task 4: 把 quizzes 接入 `src/build.py`

**Files:**
- Modify: `src/build.py:23-37`

- [ ] **Step 1: 导入 quizzes 并在每课正文尾部按语言追加**

把 `src/build.py` 中这段（第 23–24 行附近）：
```python
import shell  # noqa: E402
from registry import CONTENT  # noqa: E402
```
改为：
```python
import shell  # noqa: E402
import quizzes  # noqa: E402
from registry import CONTENT  # noqa: E402
```

再把 `build()` 里这段（原第 30–37 行）：
```python
    for fname, _title, _part in shell.PAGES:
        if fname not in CONTENT:
            raise SystemExit(f"Missing content for {fname} in registry.CONTENT")
        html = shell.page(
            fname, CONTENT[fname], standalone=True, home_href="../index.html"
        )
```
改为：
```python
    for fname, _title, _part in shell.PAGES:
        if fname not in CONTENT:
            raise SystemExit(f"Missing content for {fname} in registry.CONTENT")
        base = CONTENT[fname]
        content = {
            "zh": base["zh"] + quizzes.render(fname, "zh"),
            "en": base["en"] + quizzes.render(fname, "en"),
        }
        html = shell.page(
            fname, content, standalone=True, home_href="../index.html"
        )
```

- [ ] **Step 2: 构建并确认 L01 页面含自测块、其它课不受影响**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide/src && python build.py
grep -c "selftest" ../lessons/01-what-is-agent-framework.html
grep -c "selftest" ../lessons/02-monorepo.html
```
Expected: L01 计数 ≥ 1（含 zh+en 两块，通常为 2），L02 计数为 0（尚无题）。

- [ ] **Step 3: 内链仍全部解析**

Run: `cd src && python check_links.py`
Expected: `✓ all N internal links resolve`。

- [ ] **Step 4: Commit（含重生的 L01 页面）**

```bash
cd /home/verden/course/agent-framework-visual-guide
git add src/build.py lessons/01-what-is-agent-framework.html
git commit -m "feat(M0): wire quizzes into build.py (per-language append)"
```

---

## Task 5: 把 quizzes 接入 `src/build_print.py`（PDF 也含自测）

**Files:**
- Modify: `src/build_print.py:20-21`（加 import）、`src/build_print.py:106-116`（每课追加 quiz）

- [ ] **Step 1: 加 import quizzes**

把 `src/build_print.py` 第 20–21 行：
```python
import shell  # noqa: E402
from registry import CONTENT  # noqa: E402
```
改为：
```python
import shell  # noqa: E402
import quizzes  # noqa: E402
from registry import CONTENT  # noqa: E402
```

- [ ] **Step 2: 每课正文后追加该语言的 quiz**

把 `build_print()` 里这段（原第 106–116 行）：
```python
    for idx, (fname, title, part) in enumerate(shell.PAGES):
        content_html = CONTENT[fname][lang]
        content_html = content_html.replace(
            '<details class="accordion">', '<details class="accordion" open>'
        )
```
改为：
```python
    for idx, (fname, title, part) in enumerate(shell.PAGES):
        content_html = CONTENT[fname][lang] + quizzes.render(fname, lang)
        content_html = content_html.replace(
            '<details class="accordion">', '<details class="accordion" open>'
        )
```

- [ ] **Step 3: 重生打印版并确认 L01 自测进入 PDF 源**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide/src && python build_print.py
grep -c "selftest" ../print.zh.html
grep -c "selftest" ../print.en.html
```
Expected: 两者均 ≥ 1（L01 的自测块已并入单页打印源）。

- [ ] **Step 4: Commit（含重生的打印版）**

```bash
cd /home/verden/course/agent-framework-visual-guide
git add src/build_print.py print.zh.html print.en.html
git commit -m "feat(M0): include quizzes in print/PDF build"
```

---

## Task 6: 创建 `src/check_html.py`（结构守门，适配 AF）

**Files:**
- Create: `src/check_html.py`

> 移植自 `../llama-cpp-visual-guide/src/check_html.py`，但**必须适配 AF**：① PAGES 是 3 元组 `(fname, title{zh,en}, part{zh,en})`，part 在 `page[2]`；② AF 双语用 `data-lang="zh"/"en"`（非 `lang-zh/lang-en`）；③ AF **无 `shell.esc`**，index 标题按原文子串匹配；④ key-points 标记是「关键要点 / Key points」，类比是 `card analogy`；⑤ `MAX_LESSON=31`（允许前向引用未来课）。软检查（diagram 密度 / CJK 量）只 WARN，不阻断 M0。

- [ ] **Step 1: 写出完整文件**

```python
"""Structural / consistency regression guard for the generated HTML (AF guide).

Run after build.py:
    cd src && python check_html.py

Exits non-zero on any ERROR (used by CI). WARN/INFO print but don't fail.
Checks each lesson + index:
* balanced tags (div/details/table/pre/summary) and details<->summary
* a <title> + meta description; exactly one <h1> per lesson
* both languages present (data-lang="zh" and data-lang="en" blocks)
* no unescaped '<' inside <pre> code blocks
* cross-references "第 N 课" within 1..MAX_LESSON (forward refs allowed)
* nav prev/next chain matches shell.PAGES order
* index TOC lists every page; '共 N 课 · N 个部分' pill matches PAGES
* registry CONTENT has non-empty zh+en for every PAGES filename (no orphan keys)
* (WARN) every lesson has a key-points card, an analogy card, enough diagrams
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
SOFT_EXEMPT = set()  # lessons exempt from soft content-density checks (e.g. glossary)

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
    for tag in ("div", "details", "table", "pre", "summary"):
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
```

- [ ] **Step 2: 先确保站点是最新构建，再跑结构检查（期望 0 ERROR）**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide/src
python build.py && python check_html.py
```
Expected: 末行 `structural check passed`，`0 error(s)`。（已实测现有 27 课 0 ERROR；可能有少量 WARN，不阻断。）

- [ ] **Step 3: Commit**

```bash
cd /home/verden/course/agent-framework-visual-guide
git add src/check_html.py
git commit -m "feat(M0): add check_html.py structural guard (AF-adapted)"
```

---

## Task 7: 修正 Part 分组（新增「协议与生态」「番外篇」两个 Part）

**Files:**
- Modify: `src/shell.py:59-64`（Part 定义）、`src/shell.py:87-93`（L23–27、L21–22 的 part 归属）

> 现状：`P5`=Build Your Own 同时挂着 L16–20 **和** L23–27；`P6`=Bonus 挂 L21–22（共 6 部分）。
> 目标：L23–27 独立为新 `P6`「协议与生态」，Bonus 升为 `P7`。结果 **7 个部分 / 27 课**。

- [ ] **Step 1: 重定义 P6 并新增 P7**

把 `src/shell.py` 第 64 行：
```python
P6 = {"zh": "第六部分 · 番外篇", "en": "Part 6 · Bonus"}
```
改为：
```python
P6 = {"zh": "第六部分 · 协议与生态", "en": "Part 6 · Protocols & Ecosystem"}
P7 = {"zh": "第七部分 · 番外篇", "en": "Part 7 · Bonus"}
```

- [ ] **Step 2: 把 L23–27 从 P5 改挂 P6**

把 `src/shell.py` 第 87–91 行（5 行，结尾都是 `, P5),`）：
```python
    ("23-skills.html", {"zh": "Agent Skills 技能系统", "en": "Agent Skills"}, P5),
    ("24-mcp.html", {"zh": "MCP 工具协议", "en": "MCP Tool Protocol"}, P5),
    ("25-hosted-agents.html", {"zh": "Foundry 托管 Agent", "en": "Foundry Hosted Agents"}, P5),
    ("26-a2a-agui.html", {"zh": "A2A + AG-UI 协议", "en": "A2A & AG-UI Protocols"}, P5),
    ("27-eval-timetravel.html", {"zh": "评估与时间旅行", "en": "Evaluation & Time-Travel"}, P5),
```
改为（把每行结尾 `P5)` 改成 `P6)`）：
```python
    ("23-skills.html", {"zh": "Agent Skills 技能系统", "en": "Agent Skills"}, P6),
    ("24-mcp.html", {"zh": "MCP 工具协议", "en": "MCP Tool Protocol"}, P6),
    ("25-hosted-agents.html", {"zh": "Foundry 托管 Agent", "en": "Foundry Hosted Agents"}, P6),
    ("26-a2a-agui.html", {"zh": "A2A + AG-UI 协议", "en": "A2A & AG-UI Protocols"}, P6),
    ("27-eval-timetravel.html", {"zh": "评估与时间旅行", "en": "Evaluation & Time-Travel"}, P6),
```

- [ ] **Step 3: 把 L21–22 从 P6 改挂 P7**

把 `src/shell.py` 第 92–93 行：
```python
    ("21-vs-others.html", {"zh": "横向对比：AF vs 其他框架", "en": "AF vs Other Frameworks"}, P6),
    ("22-stack-map.html", {"zh": "全栈坐标系 & 学习地图", "en": "Full-Stack Map & Learning Path"}, P6),
```
改为：
```python
    ("21-vs-others.html", {"zh": "横向对比：AF vs 其他框架", "en": "AF vs Other Frameworks"}, P7),
    ("22-stack-map.html", {"zh": "全栈坐标系 & 学习地图", "en": "Full-Stack Map & Learning Path"}, P7),
```

- [ ] **Step 4: 重生站点 + 打印版，确认 7 个部分、计数自洽**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide/src
python build.py && python build_print.py
grep -o "共 27 课 · 7 个部分" ../index.html | head -1
python check_html.py
python check_links.py
```
Expected: 打印出 `共 27 课 · 7 个部分`；`structural check passed`（0 ERROR）；`✓ all N internal links resolve`。

- [ ] **Step 5: Commit（源 + 全部重生 HTML，保持 CI 同步）**

```bash
cd /home/verden/course/agent-framework-visual-guide
git add src/shell.py index.html lessons/ print.zh.html print.en.html
git commit -m "refactor(M0): split Protocols & Ecosystem part; bump Bonus to Part 7 (27 lessons / 7 parts)"
```

---

## Task 8: 更新 README（计数 / Part 表 / 免责声明 / 构建命令 / 结构）

**Files:**
- Modify: `README.md`

> 当前 README 过期：徽章写 `lessons-22`/`parts-6`、结构段写"22 课"、`part1 … part6`。改为反映 M0 后真实结构 **27 课 / 7 部分**，并补 LCV 同款 Part 表与第三方免责声明。（31 课 / 8 部分留待 M6 再次更新。）

- [ ] **Step 1: 更新两枚徽章**

把 `README.md` 第 8–9 行：
```markdown
![Lessons](https://img.shields.io/badge/lessons-22-blue.svg)
![Parts](https://img.shields.io/badge/parts-6-9cf.svg)
```
改为：
```markdown
![Lessons](https://img.shields.io/badge/lessons-27-blue.svg)
![Parts](https://img.shields.io/badge/parts-7-9cf.svg)
```

- [ ] **Step 2: 在 `## 📚 教程结构` 标题下方插入一段 Part 速览表 + 免责声明**

在 `README.md` 的 `## 📚 教程结构 · Tutorial Structure` 这一行之后、`### 第一部分` 之前，插入：
```markdown

> **声明**：本项目是**第三方、非官方**学习材料，**不包含 Agent Framework 源码**，仅通过引用少量、标注来源的代码片段讲解。Microsoft Agent Framework 由微软以 MIT 许可发布，相关名称与商标归其所有。
> **Disclaimer:** Third-party, unofficial educational material. It contains **no Agent Framework source**; it explains the framework via small, cited snippets. Microsoft Agent Framework is MIT-licensed by Microsoft.

| Part | 主题 Topic | 课 Lessons |
| --- | --- | --- |
| 1 · 宏观全景 / Big Picture | 是什么 · monorepo · 一次 run 的生命周期 | L01–03 |
| 2 · 用户视角 / User's View | 消息 · ChatClient · 工具 · 会话记忆 | L04–07 |
| 3 · 内部源码 / Internals | Agent/Client/Tool/中间件/Workflow/编排/流式 | L08–14 |
| 4 · 进阶实战 / Advanced | 读源码 · 调试 · 测试 · 贡献 | L15 |
| 5 · 自己动手 / Build Your Own | 接模型 · 声明式 · 自定义中间件 · 持久化 · 实战 | L16–20 |
| 6 · 协议与生态 / Protocols & Ecosystem | Skills · MCP · 托管 Agent · A2A/AG-UI · 评估 | L23–27 |
| 7 · 番外篇 / Bonus | 横向对比 · 全栈坐标系 | L21–22 |
```

- [ ] **Step 3: 更新"项目结构"段的课数与生成器列表**

把 `README.md` 中（约第 81–89 行）：
```
├── lessons/                ← 22 课图解页面
├── src/                    ← 无依赖的 Python 生成器
│   ├── shell.py            CSS 设计系统 + 双语切换 + 导航
│   ├── part1.py … part6.py 各部分课程内容（中 + 英）
│   ├── registry.py         课程 → 内容映射
│   ├── build.py            站点构建
│   ├── build_print.py      PDF 构建（中/英各一份）
│   └── check_links.py      内链检查
```
改为：
```
├── lessons/                ← 27 课图解页面
├── src/                    ← 无依赖的 Python 生成器
│   ├── shell.py            CSS 设计系统 + 双语切换 + 导航
│   ├── part1.py … part7.py 各部分课程内容（中 + 英）
│   ├── quizzes.py          每课自测题（双语 · 确定性洗牌）
│   ├── registry.py         课程 → 内容映射
│   ├── build.py            站点构建
│   ├── build_print.py      PDF 构建（中/英各一份）
│   ├── check_html.py       HTML 结构校验
│   └── check_links.py      内链检查
```

- [ ] **Step 4: 更新"重新生成"命令块，加入 check_html**

把 `README.md` 的：
```bash
cd src
python build.py          # 生成 index.html + lessons/
python build_print.py    # 生成 print.zh.html + print.en.html
python check_links.py    # 检查内链
```
改为：
```bash
cd src
python build.py          # 生成 index.html + lessons/
python build_print.py    # 生成 print.zh.html + print.en.html
python check_html.py     # 结构校验（期望 0 错）
python check_links.py    # 检查内链
```

- [ ] **Step 5: Commit**

```bash
cd /home/verden/course/agent-framework-visual-guide
git add README.md
git commit -m "docs(M0): sync README to 27 lessons / 7 parts; add Part table + disclaimer + check_html"
```

---

## Task 9: 双许可（新增 `LICENSE-CONTENT` + 更新引用处）

**Files:**
- Create: `LICENSE-CONTENT`
- Modify: `src/build_print.py:131`（封面许可文案）、`README.md`（底部许可段）

- [ ] **Step 1: 创建 `LICENSE-CONTENT`（CC BY 4.0，AF 适配）**

```text
Creative Commons Attribution 4.0 International (CC BY 4.0)

Copyright (c) 2026 verdenmax

The educational CONTENT of this project - the lesson prose and diagrams that are
authored in src/part*.py and src/quizzes.py and rendered into index.html,
lessons/*.html and print.zh.html / print.en.html - is licensed under the Creative
Commons Attribution 4.0 International License (CC BY 4.0).

You are free to:
  - Share - copy and redistribute the material in any medium or format
  - Adapt - remix, transform, and build upon the material for any purpose,
    even commercially

Under the following term:
  - Attribution - You must give appropriate credit, provide a link to this
    license, and indicate if changes were made.

Full legal code: https://creativecommons.org/licenses/by/4.0/legalcode
Human-readable summary: https://creativecommons.org/licenses/by/4.0/

This project explains Microsoft Agent Framework, which is licensed separately by
Microsoft under the MIT License. This guide is third-party, unofficial material
and contains no Agent Framework source code; it quotes only small, cited snippets.
```

- [ ] **Step 2: 更新打印封面的许可文案**

把 `src/build_print.py` 第 131 行：
```python
    {labels["gen_prefix"]} {today} · {labels["author"]} · MIT License</div>
```
改为：
```python
    {labels["gen_prefix"]} {today} · {labels["author"]} · Code MIT · Content CC BY 4.0</div>
```

- [ ] **Step 3: 更新 README 底部许可段**

把 `README.md` 底部：
```markdown
## 📄 许可 · License

[MIT License](./LICENSE)

Microsoft Agent Framework 为 Microsoft 的项目，相关名称与商标归其所有。本教程为独立的第三方学习材料。
```
改为：
```markdown
## 📄 许可 · License

双许可 Dual-licensed：

- **代码 Code**（`src/` 下的 Python 生成器与校验脚本）— MIT，见 [LICENSE](./LICENSE)
- **内容 Content**（课程文字与图，渲染进 `index.html` / `lessons/*.html` / `print.*.html`）— CC BY 4.0，见 [LICENSE-CONTENT](./LICENSE-CONTENT)

Microsoft Agent Framework 为 Microsoft 的项目（MIT 许可），相关名称与商标归其所有。本教程为独立的第三方、非官方学习材料，不含其源码。
```

- [ ] **Step 4: 重生打印版（封面文案变更）+ 校验**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide/src
python build_print.py && python check_links.py
grep -o "Code MIT · Content CC BY 4.0" ../print.zh.html | head -1
```
Expected: 打印出 `Code MIT · Content CC BY 4.0`；内链全解析。

- [ ] **Step 5: Commit**

```bash
cd /home/verden/course/agent-framework-visual-guide
git add LICENSE-CONTENT README.md src/build_print.py print.zh.html print.en.html
git commit -m "docs(M0): dual-license (code MIT + content CC BY 4.0)"
```

---

## Task 10: CI 增跑 `check_html.py`

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: 在"Check internal links"步骤之前插入结构校验步骤**

把 `.github/workflows/ci.yml` 末尾：
```yaml
      - name: Check internal links
        working-directory: src
        run: python check_links.py
```
改为：
```yaml
      - name: Check HTML structure
        working-directory: src
        run: python check_html.py

      - name: Check internal links
        working-directory: src
        run: python check_links.py
```

- [ ] **Step 2: 本地复跑 CI 等价命令，确认整条链路绿**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide/src
python build.py && python build_print.py && python check_html.py && python check_links.py
```
Expected: `structural check passed`（0 ERROR）+ `✓ all N internal links resolve`，无报错。

- [ ] **Step 3: Commit**

```bash
cd /home/verden/course/agent-framework-visual-guide
git add .github/workflows/ci.yml
git commit -m "ci(M0): run check_html.py structural guard in CI"
```

---

## Task 11: 里程碑出口闸门（全量重生 + 校验 + 零漂移）

**Files:** 无新增；这是 M0 的验收关。

- [ ] **Step 1: 干净全量重生 + 四件套校验**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide/src
python build.py && python build_print.py && python check_html.py && python check_links.py
```
Expected: build 正常；`structural check passed`（0 ERROR）；`✓ all N internal links resolve`。

- [ ] **Step 2: 确认生成物与源零漂移（CI 同款判定）**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide
git diff --quiet -- index.html lessons/ print.zh.html print.en.html && echo "HTML in sync ✓" || echo "DRIFT — commit regenerated HTML"
```
Expected: `HTML in sync ✓`（前序任务都已随源提交对应生成物）。若提示 DRIFT，执行：
```bash
git add index.html lessons/ print.zh.html print.en.html
git commit -m "build(M0): sync generated HTML"
```

- [ ] **Step 3: 确认游离文件已不在跟踪、quiz 链路成立**

Run:
```bash
cd /home/verden/course/agent-framework-visual-guide
git ls-files src/gen_part2.py src/part5.py.backup
test -f src/quizzes.py && test -f src/check_html.py && test -f LICENSE-CONTENT && echo "new files present ✓"
grep -c selftest lessons/01-what-is-agent-framework.html
```
Expected: 第一行**无输出**（已移除跟踪）；打印 `new files present ✓`；L01 selftest 计数 ≥ 1。

- [ ] **Step 4: M0 收尾确认（无需再 commit）**

M0 完成标准：① quizzes 框架接入 build/build_print 且 L01 可见自测 ② check_html.py 0 ERROR 且进入 CI ③ 游离文件清除 ④ 7 个部分 / 27 课、计数自洽 ⑤ README 与双许可更新。后续 M1 起再逐课加深与补题。

---

## 自审清单（计划作者已核对）

- **Spec 覆盖**：本计划只实现 spec 第 5 节"工具与卫生"+ 第 4.1 节 quizzes 框架 + 第 3 节 Part 分组修正；课程加深（第 3、4.2、4.3 节）与 4 门新课（第 3 节）属 M1–M6，不在 M0。
- **占位符**：无 TBD/TODO；每个代码步骤均给出完整代码与确切命令、预期输出。
- **类型/命名一致**：`quizzes.render(fname, lang)`、`QUIZZES`、`_shuffle`、`_validate`、`check_html.main()`、`shell.PAGES`(3 元组)、part 取 `p[2]` 全程一致。
- **已实测前提**：现有 27 课在严格 ERROR 检查下 0 错；标记为「关键要点 / Key points / card analogy」；`--blue` 等 CSS 变量均在 AF `:root` 定义；游离文件确被 git 跟踪。
