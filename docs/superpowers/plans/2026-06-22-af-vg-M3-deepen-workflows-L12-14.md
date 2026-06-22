# M3 · 工作流与编排加深 L12–14 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 把 L12（Workflows 引擎）、L13（编排模式）、L14（流式与可观测性）各加深到约 2×，每课补 worked-example 追踪 + 1–2 张新图 + 真实简化源码 + 自测题。

**Architecture / 配方：完全沿用 M2**（见 `2026-06-22-af-vg-M2-deepen-core-L08-11.md` 的"背景速记 / 每课验收标准"）——同样的 CSS 原语、双语等量、`<` 写 `&lt;`、强调用 `<strong>/<em>` 不用 Markdown、改完重生并提交生成物、闸门 `check_html`(0 ERROR)+`check_links`。内容在 `src/part3.py`（L12_ZH 第 1382 行起 / L13 第 1689 行起 / L14 第 2011 行起），题在 `src/quizzes.py`。

**Verify against:** `../agent-framework/python/packages/core/agent_framework/_workflows/`（`_workflow_builder.py`/`_executor.py`/`_edge.py`/`_workflow.py`）、编排器真实位置（**先定位**：在 `_workflows/` 或顶层 `python/packages/orchestrations/` 用 `grep -rln "Magentic\|Handoff\|GroupChat\|Sequential\|Concurrent"` 找到真实类名/文件再引用）、`_telemetry.py`（OpenTelemetry 接入）。

> **前置**：M1 审计已对齐 L12–14 现有引用；M2 已加深 L08–11（同一文件 part3.py，注意基于 M2 之后的最新内容编辑）。

---

## Task 1: 加深 L12 Workflows 引擎 + quiz

**Files:** Modify `src/part3.py`（L12_ZH/L12_EN）、`src/quizzes.py` · Verify: `_workflows/_workflow_builder.py`/`_executor.py`/`_edge.py`

- [ ] **Step 1（worked-example）**：`<h2>追踪一次工作流执行</h2>` + `.vflow`：用一个具体二节点图（如 `writer → reviewer`）走一遍：`WorkflowBuilder` 加节点/连边 → `build()` → 投递初始消息 → Executor 执行 → 沿 Edge 传递 → 终止条件 → 产出。每步显示当前活跃节点与在途消息。
- [ ] **Step 2（新图）**：图模型示意（`.flow`/`.layers`）：Executor（节点）+ Edge（有向边）+ 消息在边上流动；标注与 Agent 循环的区别（图 vs 单 Agent 循环）。
- [ ] **Step 3（源码块）**：`codefile`(path=`_workflow_builder.py`)：简化 `WorkflowBuilder.add_edge()/set_start_executor()/build()` 与 `Executor` 基类的 `execute` 钩子（核对真实签名）。
- [ ] **Step 4（why 正文）**：为什么要图式编排（可控、可恢复、可并发）；与单 Agent 工具循环的取舍。
- [ ] **Step 5（英文同步）。**
- [ ] **Step 6（quiz）**：`"12-workflows.html"`：MCQ（Executor/Edge 各是什么 / 图编排 vs Agent 循环 / build() 的作用）+ 开放题。
- [ ] **Step 7（闸门+提交）**：build+build_print+check_html+check_links 全绿；`content(M3): deepen L12 workflows 2x + worked-example + quiz`（含重生 HTML/print；trailer `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`）。

## Task 2: 加深 L13 编排模式 + quiz

**Files:** Modify `src/part3.py`（L13_ZH/L13_EN）、`src/quizzes.py` · Verify: 编排器真实位置（先用 grep 定位）

- [ ] **Step 1（定位编排器）**：`grep -rln "Magentic\|Handoff\|GroupChat\|class Sequential\|class Concurrent" ../agent-framework/python/packages/` 找到 Sequential/Concurrent/Handoff/GroupChat/Magentic 的真实类名与所在包/文件，作为引用依据（修正现有任何对不上的名）。
- [ ] **Step 2（worked-example）**：挑 **Handoff** 或 **Magentic** 一种，`<h2>追踪一次 <X> 编排</h2>` + `.vflow`：用具体场景走一遍（如客服 Handoff：分流 Agent → 判定 → 移交专员 Agent → 返回）。
- [ ] **Step 3（新图）**：五种编排模式对照图（`table.t`）：Sequential/Concurrent/Handoff/GroupChat/Magentic 各自的拓扑 + 适用场景。
- [ ] **Step 4（源码块）**：`codefile` 简化所选编排器的构造/入口（核对真实 API）。
- [ ] **Step 5（why 正文）**：为什么把常见多 Agent 协作固化成模式（而非每次手搭图）；各模式的取舍。
- [ ] **Step 6（英文同步）。**
- [ ] **Step 7（quiz）**：`"13-orchestration.html"`：MCQ（各模式适用场景 / Handoff vs GroupChat / Magentic 特点）+ 开放题。
- [ ] **Step 8（闸门+提交）**：`content(M3): deepen L13 orchestration 2x + worked-example + quiz`。

## Task 3: 加深 L14 流式与可观测性 + quiz

**Files:** Modify `src/part3.py`（L14_ZH/L14_EN）、`src/quizzes.py` · Verify: `_agents.py`（run_stream/Update）、`_telemetry.py`

- [ ] **Step 1（worked-example）**：`<h2>追踪一次流式输出</h2>` + `.vflow`：`agent.run(..., stream=True)` 如何逐块产出 `AgentResponseUpdate`（核对真实类型名），最终聚合为完整响应；并行展示 OpenTelemetry 的 span 如何在同一次调用里产生（agent span → chat span → tool span 嵌套）。
- [ ] **Step 2（新图）**：两张——① 流式分块时间线（`.flow`/`.vflow`）；② OTel span 树（嵌套 `.layers`：agent → chat client → tool）。
- [ ] **Step 3（源码块）**：`codefile`(path=`_telemetry.py`)：简化 span 创建/属性设置的接入点（核对真实符号）。
- [ ] **Step 4（why 正文）**：为什么流式 + 可观测是一等公民（生产级要求）；trace/metric 如何定位问题。
- [ ] **Step 5（英文同步）。**
- [ ] **Step 6（quiz）**：`"14-streaming-observability.html"`：MCQ（流式返回类型 / span 嵌套关系 / 为何需要 OTel）+ 开放题。
- [ ] **Step 7（闸门+提交）**：`content(M3): deepen L14 streaming-observability 2x + worked-example + quiz`。

## Task 4: M3 出口闸门

- [ ] **Step 1**：build+build_print+check_html+check_links 全绿（0 ERROR）。
- [ ] **Step 2（深度核对）**：`cd src && python3 -c "import part3,quizzes; [print(k,len(getattr(part3,k+'_ZH'))) for k in ['L12','L13','L14']]; [print(f, f in quizzes.QUIZZES) for f in ['12-workflows.html','13-orchestration.html','14-streaming-observability.html']]"` → 三课 zh ≥ ~18000、均有 quiz。
- [ ] **Step 3（零漂移）**：`git diff --quiet -- index.html lessons/ print.zh.html print.en.html && echo "in sync ✓"`。

---

## 自审清单（计划作者已核对）
- **Spec 覆盖**：spec §3 核心课 2×、§4.2 worked-example、§4.1 quizzes（L12–14）。
- **关键风险**：编排器真实类名/位置需先 grep 定位（已在 Task 2 Step 1 强制）；避免沿用可能过时的名。
- **依赖**：基于 M1（准确）+ M2（part3.py 已被 M2 修改，编辑前读最新内容）。
- **占位符**：无；每课给出 worked-example 场景、图、源码块、quiz 主题与闸门命令。
