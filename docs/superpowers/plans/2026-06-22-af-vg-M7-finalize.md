# M7 · 收尾 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 收尾整个工程：补关键交叉链接、给 `check_html.py` 加"每课必须有 quiz"的永久守门、收紧视觉块软阈值、全量重生 print/PDF、跑完整校验，确保 31 课 / 8 部分全绿且对标 LCV 的完成度。

**Architecture:** 纯收尾，不加新课。复用既有管线与约定（`<strong>/<em>` 非 Markdown；`<pre>` 内 `<`→`&lt;`；改完重生提交生成物）。

> **前置**：M0–M6 已完成（31 课/8 部分、全部有 quiz、README 已 31/8）。

---

## Task 1: check_html 增"quiz 全覆盖"守门 + 收紧软阈值

**Files:** Modify `src/check_html.py`

- [ ] **Step 1（quiz 覆盖 ERROR 守门）**：在 `src/check_html.py` 的 `main()` 里、registry 对齐检查附近，加入：
```python
    # every lesson must have a self-test quiz (M5/M6 coverage guard)
    import quizzes  # noqa: E402
    for fname, _t, _p in PAGES:
        q = quizzes.QUIZZES.get(fname)
        if not q or not q.get("mcq"):
            add("ERR", fname, "missing self-test quiz (quizzes.QUIZZES entry with mcq)")
```
（放在 `index_path = ...` 之前。）
- [ ] **Step 2（收紧视觉块软阈值为更有意义的值）**：把 `MIN_DIAGRAMS = 4` 维持为 WARN（不升 ERROR，避免误伤），但确认深化后绝大多数课不再触发；术语表已在 `SOFT_EXEMPT`。
- [ ] **Step 3（验证守门真的生效）**：临时把某课从 QUIZZES 注释掉跑 `python check_html.py` 应报该课 ERR；恢复后应 `0 error(s)`。（验证后务必恢复。）
- [ ] **Step 4（闸门+提交）**：`cd src && python build.py && python check_html.py && python check_links.py` → 0 ERROR、全解析。提交：
```bash
cd /home/verden/course/agent-framework-visual-guide
git add src/check_html.py
git commit -m "ci(M7): enforce per-lesson quiz coverage in check_html

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Task 2: 关键交叉链接

**Files:** Modify 相关 `src/part*.py`

- [ ] **Step 1**：补几处高价值互链（用 `<a href="NN-*.html">…</a>` 或行内"见第 N 课"）：
  - L14（流式/可观测）↔ L30（可观测性深入）双向。
  - L07（会话记忆）→ L28（记忆后端）。
  - L11（中间件）↔ L18（写自己的中间件）。
  - L12/L13（工作流/编排）→ L20（capstone）。
  - L31（术语表）已含跨课链接（M6 完成）。
  仅加链接句，不大改正文。
- [ ] **Step 2（闸门+提交）**：build+build_print+check_html+check_links 全绿（注意新链接必须解析）。`content(M7): add cross-links between related lessons`（含重生 HTML/print）。

## Task 3: 全量重生 + 完整校验（出口闸门）

- [ ] **Step 1（干净全量重生）**：`cd src && python build.py && python build_print.py`。
- [ ] **Step 2（四件套）**：`python check_html.py`（0 ERROR）+ `python check_links.py`（全解析）。
- [ ] **Step 3（综合核对）**：`cd src && python3 -c "
import shell, quizzes, part3, part7, part8
assert len(shell.PAGES)==31, len(shell.PAGES)
parts={p[2]['zh'] for p in shell.PAGES}; assert len(parts)==8, parts
miss=[f for f,_,_ in shell.PAGES if f not in quizzes.QUIZZES]; assert not miss, miss
print('31 lessons / 8 parts / all quizzed ✓')"`。
- [ ] **Step 4（零漂移）**：`cd /home/verden/course/agent-framework-visual-guide && git diff --quiet -- index.html lessons/ print.zh.html print.en.html && echo "in sync ✓"`。
- [ ] **Step 5（README 终校）**：确认 README 徽章 31/8、Part 表含 8 部分与 4 门新课、结构树 `part1.py … part8.py`、构建命令含 `check_html.py`、双许可段在位。如有遗漏补齐并提交 `docs(M7): final README polish`。

## Task 4: 整体最终评审（dispatch final reviewer）

- [ ] **Step 1**：派一个 code-review 子代理（模型 claude-opus-4.8）评审整个 enrichment 分支 `git diff main..feat/enrichment-vs-llamacpp`，重点：是否有未核对/伪造 API、双语是否等量、是否有 Markdown 残留星号、所有内链解析、31/8 自洽。
- [ ] **Step 2**：按评审的 Critical/Important 项修复并复跑闸门；Minor 酌情。
- [ ] **Step 3**：全绿后，里程碑全部完成——按需调用 superpowers:finishing-a-development-branch 决定合并/PR。

---

## 自审清单（计划作者已核对）
- **Spec 覆盖**：spec §7 收尾（print/PDF、README、交叉链接、全量校验）+ 把"每课有 quiz"做成 CI 永久守门（强化 §7 验证基准）。
- **守门可验证**：Task 1 Step 3 要求实际注入缺失再恢复，确认守门非空操作。
- **占位符**：无；每步给出确切代码/命令/预期。
