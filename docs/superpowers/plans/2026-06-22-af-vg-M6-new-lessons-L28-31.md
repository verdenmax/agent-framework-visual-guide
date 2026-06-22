# M6 · 4 门新课 L28–31 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 新增 4 门核心深度的课，把教程扩到 **31 课 / 8 部分**：
- **L28 记忆后端**（Part 5 自己动手）— Redis / Mem0 / Cosmos 后端 + ContextProvider/HistoryProvider 深入。
- **L29 DevUI**（Part 4 进阶）— 本地可视化调试。
- **L30 可观测性深入**（Part 4 进阶）— OpenTelemetry trace/metric 接入。
- **L31 术语表 / 速查**（Part 8 速查，全新部分，放最后）— 词条网格 + 概念索引 + 跨课跳转。

**Architecture:** 4 门新课内容统一放在**新文件 `src/part8.py`**（变量 `L28_ZH/EN … L31_ZH/EN`）；`registry.py` 增 `import part8` 与 4 条 CONTENT；`shell.py` 增 `P8` 标签、把 4 课插入 `PAGES` 正确分组、补 `SUBTITLES`；`quizzes.py` 增 4 课题。内容文件与 Part 标签解耦（registry 已是此约定）：part8.py 虽含全部 4 课，但它们分别挂到 P4/P5/P8。

**配方：沿用 M2**（核心深度：worked-example + 1–2 图 + 真实简化源码 + 更多"为什么"正文；`<strong>/<em>` 非 Markdown；`<pre>` 内 `<`→`&lt;`；引用前 grep 核对；双语等量；改完重生提交生成物；闸门 0 ERROR）。

**真实源码锚点（引用前再 grep 确认精确类名）：**
- L28：`python/packages/redis/agent_framework_redis/{_context_provider.py,_history_provider.py}`、`python/packages/mem0/agent_framework_mem0/_context_provider.py`、`python/packages/azure-cosmos/agent_framework_azure_cosmos/_history_provider.py`；核心抽象在 `core/.../_sessions.py`（`ContextProvider.before_run()`、`HistoryProvider` 家族——M1 已核实）。
- L29：`python/packages/devui/agent_framework_devui` 的 `serve(...)`（`__init__.py:89`）、`main()`（:202）。
- L30：`core/.../observability.py` 的 `configure_otel_providers()`（:1151）、`ObservabilitySettings`（:666）；以及 `_telemetry.py` 的 span 接入点。
- L31：综合全书，无需新源码；术语的"源码位置"列引用前 grep 确认。

> **PAGES 插入位置**（最终顺序）：`…L15, L29, L30,（P4 结束）L16–L20, L28,（P5 结束）L23–27（P6）, L21–22（P7）, L31（P8）`。
> **中间态计数自洽**：加 L28 后 28 课/7 部分；加 L29、L30 后 30 课/7 部分；加 L31 后 31 课/8 部分。`check_html` 的 pill 计数断言每步都应通过（index pill 自动派生）。

---

## Task 1: L28 记忆后端（创建 `src/part8.py` + 接线 + quiz）

**Files:** Create `src/part8.py`；Modify `src/registry.py`、`src/shell.py`、`src/quizzes.py`
**Verify against:** redis/mem0/azure-cosmos 包 + `core/.../_sessions.py`

- [ ] **Step 1（创建 part8.py + L28 内容）**：新建 `src/part8.py`，先写文件 docstring，再写 `L28_ZH = r"""…"""` 与 `L28_EN = r"""…"""`（核心深度）。内容含：① `lead` 引子 ② `card analogy` 类比（记忆 = 给 Agent 配一个"长期记事本/外部资料库"）③ worked-example（`.vflow`：一次带记忆的 run——`ContextProvider.before_run()` 注入历史/检索结果 → LLM → 运行后写回）④ 后端对照图（`table.t`：Redis(`_context_provider`+`_history_provider`) / Mem0(`_context_provider`) / Cosmos(`_history_provider`) —— 各自能力、ContextProvider vs HistoryProvider 的区别）⑤ `codefile` 简化某后端 Provider 的构造与 `before_run` 钩子（grep 真实类名后照搬）⑥ "为什么"正文（短期对话历史 vs 长期向量记忆的分工）⑦ 关键要点 + 设计亮点。
- [ ] **Step 2（registry 接线）**：`src/registry.py` 顶部 `import part8`；CONTENT 增 `"28-memory-backends.html": {"zh": part8.L28_ZH, "en": part8.L28_EN},`。
- [ ] **Step 3（shell.PAGES 接线）**：在 `("20-capstone.html", …, P5)` 这一行之后插入：
```python
    ("28-memory-backends.html", {"zh": "记忆后端", "en": "Memory Backends"}, P5),
```
并在 `SUBTITLES` 增：`"28-memory-backends.html": {"zh": "Redis / Mem0 / Cosmos · ContextProvider", "en": "Redis / Mem0 / Cosmos · ContextProvider"},`。
- [ ] **Step 4（quiz）**：`src/quizzes.py` 增 `"28-memory-backends.html"`：MCQ（ContextProvider vs HistoryProvider / 短期 vs 长期记忆 / 为何抽象成 Provider）+ 开放题。
- [ ] **Step 5（闸门+提交）**：`cd src && python build.py && python build_print.py && python check_html.py && python check_links.py` → 0 ERROR、链接全解析、index pill 显示 `共 28 课 · 7 个部分`。提交：
```bash
cd /home/verden/course/agent-framework-visual-guide
git add src/part8.py src/registry.py src/shell.py src/quizzes.py index.html lessons/ print.zh.html print.en.html
git commit -m "content(M6): add L28 memory-backends lesson + quiz (28 lessons)

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Task 2: L29 DevUI（追加到 `src/part8.py` + 接线 + quiz）

**Files:** Modify `src/part8.py`、`src/registry.py`、`src/shell.py`、`src/quizzes.py`
**Verify against:** `python/packages/devui/agent_framework_devui/__init__.py`（`serve`/`main`）

- [ ] **Step 1（内容）**：在 part8.py 追加 `L29_ZH/L29_EN`（核心深度）：① 类比（DevUI = Agent 的"驾驶舱/示波器"）② worked-example（`.vflow`：`serve(entities=[agent])` 启动本地服务 → 浏览器打开 → 发请求 → 实时看消息/工具调用/流式 token/trace）③ 界面能力图（`table.t` 或 `.layers`：请求面板 / 消息时间线 / 工具调用 / 事件流）④ `codefile`(path=`agent_framework_devui/__init__.py`) 简化 `serve(...)` 签名（grep 真实参数）⑤ "为什么"（本地可视化把"黑箱调试"变"看得见"）⑥ 与 samples 的联动 ⑦ 要点+亮点。
- [ ] **Step 2（registry）**：CONTENT 增 `"29-devui.html": {"zh": part8.L29_ZH, "en": part8.L29_EN},`。
- [ ] **Step 3（shell.PAGES）**：在 `("15-contributing.html", …, P4)` 之后插入：
```python
    ("29-devui.html", {"zh": "DevUI 可视化调试", "en": "DevUI Visual Debugging"}, P4),
```
`SUBTITLES` 增：`"29-devui.html": {"zh": "serve() · 请求/消息/trace 可视化", "en": "serve() · visualize requests/messages/traces"},`。
- [ ] **Step 4（quiz）**：`"29-devui.html"`：MCQ（serve 的作用 / DevUI 能看到什么 / 何时用）+ 开放题。
- [ ] **Step 5（闸门+提交）**：build+build_print+check_html+check_links 全绿；pill 显示 `共 29 课 · 7 个部分`。`content(M6): add L29 devui lesson + quiz (29 lessons)`。

## Task 3: L30 可观测性深入（追加到 `src/part8.py` + 接线 + quiz）

**Files:** Modify `src/part8.py`、`src/registry.py`、`src/shell.py`、`src/quizzes.py`
**Verify against:** `core/.../observability.py`（`configure_otel_providers`/`ObservabilitySettings`）、`_telemetry.py`

- [ ] **Step 1（内容）**：追加 `L30_ZH/L30_EN`（核心深度）：① 类比（trace = Agent 调用的"行车记录仪"）② worked-example（`.vflow` + 嵌套 `.layers`：一次 run 产生的 span 树——agent span → chat span → tool span，附属性/耗时）③ trace/metric/log 三支柱图 ④ `codefile`(path=`observability.py`) 简化 `configure_otel_providers(...)` 接入（grep 真实签名）⑤ "为什么"（生产级定位问题：延迟/失败/成本归因）⑥ 与 L14 的关系（L14 讲流式为主，这里讲可观测深入；正文加一句互链"见第 14 课"）⑦ 要点+亮点。
- [ ] **Step 2（registry）**：CONTENT 增 `"30-observability.html": {"zh": part8.L30_ZH, "en": part8.L30_EN},`。
- [ ] **Step 3（shell.PAGES）**：在 `("29-devui.html", …, P4)` 之后插入：
```python
    ("30-observability.html", {"zh": "可观测性深入", "en": "Observability Deep-Dive"}, P4),
```
`SUBTITLES` 增：`"30-observability.html": {"zh": "OpenTelemetry · span 树 · trace/metric", "en": "OpenTelemetry · span tree · trace/metric"},`。
- [ ] **Step 4（quiz）**：`"30-observability.html"`：MCQ（span 嵌套关系 / configure_otel_providers 作用 / 三支柱）+ 开放题。
- [ ] **Step 5（闸门+提交）**：全绿；pill `共 30 课 · 7 个部分`。`content(M6): add L30 observability lesson + quiz (30 lessons)`。

## Task 4: L31 术语表 / 速查（追加到 `src/part8.py` + 新 Part 8 + quiz）

**Files:** Modify `src/part8.py`、`src/registry.py`、`src/shell.py`、`src/quizzes.py`

- [ ] **Step 1（内容）**：追加 `L31_ZH/L31_EN`（速查特殊版式，仿 LCV L40）：① 一段引子说明"这是全书索引" ② **术语网格**（`table.t`，列：术语 / 一句话定义 / 源码位置 / 所属课）覆盖核心术语：Agent/BaseAgent/RawAgent、ChatClient/BaseChatClient、Message/Content/Role、@tool/AIFunction、FunctionCall/Result、Middleware(三类)、Workflow/Executor/Edge/WorkflowBuilder、编排器(Sequential/Concurrent/Handoff/GroupChat/Magentic)、ContextProvider/HistoryProvider、Skill、MCPTool、Evaluator、checkpoint/HITL、OpenTelemetry。每个术语的"源码位置"grep 确认真实文件。③ **概念依赖图**（`.flow`/`.layers`：从 Message/Content → ChatClient → Agent 循环 → Workflow → 编排 → 协议生态，谁依赖谁）④ 跨课跳转链接（指向相应 `NN-*.html`）。
- [ ] **Step 2（新 Part 8 标签）**：`src/shell.py` 在 `P7 = {…番外…}` 之后加：
```python
P8 = {"zh": "第八部分 · 速查", "en": "Part 8 · Quick Reference"}
```
- [ ] **Step 3（registry + PAGES）**：CONTENT 增 `"31-glossary.html": {"zh": part8.L31_ZH, "en": part8.L31_EN},`；在 `PAGES` **末尾**（`("22-stack-map.html", …, P7)` 之后）加：
```python
    ("31-glossary.html", {"zh": "术语表 · 速查", "en": "Glossary & Quick Reference"}, P8),
```
`SUBTITLES` 增：`"31-glossary.html": {"zh": "核心术语 · 源码位置 · 概念索引", "en": "core terms · source locations · concept index"},`。
- [ ] **Step 4（check_html 软豁免）**：`src/check_html.py` 把 `SOFT_EXEMPT = set()` 改为 `SOFT_EXEMPT = {"31-glossary.html"}`（术语表是表格/索引版式，豁免 diagram 密度等软检查）。
- [ ] **Step 5（quiz）**：`"31-glossary.html"`：MCQ（核心概念依赖关系 / 谁持有什么 / 某术语在哪类）+ 1 道"合上术语表默写地图"开放题。
- [ ] **Step 6（闸门+提交）**：全绿；pill 显示 `共 31 课 · 8 个部分`。`content(M6): add L31 glossary lesson + Part 8 + quiz (31 lessons / 8 parts)`。

## Task 5: README 升级到 31/8 + M6 出口闸门

**Files:** Modify `README.md`

- [ ] **Step 1（README 计数+表）**：徽章 `lessons-27`→`31`、`parts-7`→`8`；Part 速览表更新——Part 4 增 `L29 DevUI · L30 可观测性`、Part 5 增 `L28 记忆后端`、新增一行 `8 · 速查 / Quick Reference | 术语表 · 概念索引 | L31`；项目结构树把 `part1.py … part7.py` 改为 `part1.py … part8.py`，`lessons/` 注释 `27 课`→`31 课`。
- [ ] **Step 2（全课自测覆盖核对）**：`cd src && python3 -c "
import shell, quizzes
miss=[f for f,_,_ in shell.PAGES if f not in quizzes.QUIZZES]
print('without quiz:', miss); assert not miss; print('all', len(shell.PAGES), 'have quizzes ✓')"`（前提：M5 已为旧课补题）。
- [ ] **Step 3（出口闸门）**：`cd src && python build.py && python build_print.py && python check_html.py && python check_links.py` → 0 ERROR、链接全解析、pill `共 31 课 · 8 个部分`。零漂移：`git diff --quiet -- index.html lessons/ print.zh.html print.en.html && echo "in sync ✓"`。
- [ ] **Step 4（提交）**：`git add README.md && git commit -m "docs(M6): README to 31 lessons / 8 parts"`（trailer 同上）。

---

## 自审清单（计划作者已核对）
- **Spec 覆盖**：spec §3 新增 4 课、§4.2 worked-example、§4.1 quizzes、§3 Part 8 速查。
- **接线一致性**：part8.py 含 4 课内容；registry 4 条 CONTENT；shell PAGES 4 处插入 + P8 标签 + 4 条 SUBTITLES；check_html SOFT_EXEMPT 加术语表。中间态计数 28/29/30/31 均自洽。
- **真实符号**：redis/mem0/cosmos provider 文件、devui `serve`、observability `configure_otel_providers` 均已 grep 确认存在（精确类名引用前再确认）。
- **占位符**：无；每课给出结构、图、源码块、quiz 主题、确切接线位置与闸门命令。
