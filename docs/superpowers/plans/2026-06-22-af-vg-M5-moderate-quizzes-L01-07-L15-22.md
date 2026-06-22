# M5 · 适度加深 + 全课自测 L01–07/L15–22 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 为剩余 14 课（L01–07 入门/用户视角、L15 进阶、L16–20 自己动手、L21–22 番外）**全部补自测题**，并对偏薄的课（< ~10k 字）做**适度**加深（+1 张图或一段简短 worked-example）。**不强求 2×**（这是"入门/番外适度"分层）。完成后，全部 27 课均有自测题。

**Architecture / 配方：沿用 M2 的硬约束**（强调用 `<strong>/<em>` 非 Markdown；`<pre>` 内 `<`→`&lt;`；引用前 grep 核对真实符号；双语等量；改完重生并提交生成物；闸门 `check_html` 0 ERROR + `check_links`）。题在 `src/quizzes.py`，内容在 `src/part1.py`/`part2.py`/`part4.py`/`part5.py`/`part6.py`（按 `Lxx_ZH = r"""` 变量标记定位）。

**当前深度（决定是否需要补图）：**
- 已较深（≥10k，**只加题**，可选微调）：L01=13.5k、L02=11.2k、L03=10.4k、L04=15.4k、L05=14.2k、L06=16.5k、L07=15.3k。
- 偏薄（<10k，**加题 + 1 图/短 worked-example**）：L15=9.0k、L16=8.6k、L17=6.2k、L18=8.6k、L19=6.3k、L20=8.9k、L21=8.4k、L22=8.6k。
- 注：L01 已有 M0 种子题；本里程碑只需为 L02–L07、L15–L22 新增题（并可顺手把 L01 题补到 2–3 道）。

**每课题量**：2–3 道 MCQ（含 `why`）+ 1 道开放题，中英齐全，`_validate()` 通过，走"想一想为什么这么设计"路线。

---

## Task 1: L01–03 自测题（`src/part1.py` 仅按需微调 + `src/quizzes.py`）
**Verify against:** `_agents.py`/`_clients.py`/`_types.py`/`python/packages/` 目录
- [ ] **Step 1**：为 `"02-monorepo.html"`、`"03-lifecycle.html"` 新增 quiz；把 `"01-what-is-agent-framework.html"` 补到 2–3 道 MCQ（已有 2 道，可加 1 道）。题目核对真实概念（monorepo 包名、run 生命周期步骤）。
- [ ] **Step 2（可选微调）**：L01–03 已较深，仅在发现明显薄弱处补一句，不做大改。
- [ ] **Step 3（闸门+提交）**：build+build_print+check_html+check_links 全绿；`content(M5): add quizzes for L01-03

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`（含重生 HTML/print）。

## Task 2: L04–07 自测题（`src/quizzes.py`，内容已足够深）
- [ ] **Step 1**：为 `"04-messages.html"`、`"05-chat-models.html"`、`"06-tools.html"`、`"07-sessions-memory.html"` 各加 quiz。题目核对真实符号（`Content`/`Role`、`@tool`、`HistoryProvider`/`context_providers`——以 M1 修正后的真实名为准）。
- [ ] **Step 2（闸门+提交）**：`content(M5): add quizzes for L04-07`。

## Task 3: L15 适度加深 + 自测（`src/part4.py` + `src/quizzes.py`）
- [ ] **Step 1（+1 图/短 worked-example）**：L15（读源码/调试/测试/贡献）加一张"开发闭环"图（`.flow`：clone → uv sync → 改 → poe 测试/typing → DevUI 调试 → PR）或一段简短 worked-example（跑一次 `poe` 任务的步骤）。命令/任务名按 M1 修正后的真实值（如 `poe typing`）。
- [ ] **Step 2（quiz）** `"15-contributing.html"`：MCQ（uv/poe 作用 / DevUI 用途 / 真实测试命令）+ 开放题。
- [ ] **Step 3（闸门+提交）**：`content(M5): light-deepen L15 + quiz`。

## Task 4: L16–20 适度加深 + 自测（`src/part5.py` + `src/quizzes.py`）
**Verify against:** provider 包（`AnthropicClient`、`from agent_framework.openai import OpenAIChatClient` 等 M1 真值）、`declarative`(`AgentFactory`)、`_workflows/_checkpoint.py`(`File/CosmosCheckpointStorage`)、`observability.configure_otel_providers`
- [ ] **Step 1（每课 +1 图或短 worked-example）**：L16 providers 对照图（各 ChatClient 真实类名/导入路径）；L17 声明式 YAML→`AgentFactory().create_agent_from_yaml_path()` 流程；L18 自定义中间件最小骨架（`call_next` 真实名）；L19 checkpoint/HITL 时间轴（`File/CosmosCheckpointStorage`）；L20 capstone 端到端图。仅薄处补，约加到 ~10–12k。
- [ ] **Step 2（quiz）**：为 `"16-providers.html"`/`"17-declarative.html"`/`"18-custom-middleware.html"`/`"19-durability-hitl.html"`/`"20-capstone.html"` 各加 quiz（核对真实 API）。
- [ ] **Step 3（闸门+提交）**：`content(M5): light-deepen L16-20 + quizzes`。

## Task 5: L21–22 适度加深 + 自测（`src/part6.py` + `src/quizzes.py`）
- [ ] **Step 1（+1 图）**：L21（横向对比）补一张 AF vs LangGraph/AutoGen/SK 维度对照表（`table.t`）；L22（全栈坐标系）补一张分层/流派图。对外部框架描述保持观点性、只纠明显事实错。
- [ ] **Step 2（quiz）**：`"21-vs-others.html"`/`"22-stack-map.html"` 各加 quiz（侧重"AF 的定位取舍"）。
- [ ] **Step 3（闸门+提交）**：`content(M5): light-deepen L21-22 + quizzes`。

## Task 6: M5 出口闸门
- [ ] build+build_print+check_html+check_links 全绿（0 ERROR）。
- [ ] **全课自测覆盖核对**：`cd src && python3 -c "
import shell, quizzes
miss=[f for f,_,_ in shell.PAGES if f not in quizzes.QUIZZES]
print('lessons without quiz:', miss); assert not miss, miss
print('ALL', len(shell.PAGES), 'lessons have quizzes ✓')"` → 27 课全部有题。
- [ ] 零漂移：`git diff --quiet -- index.html lessons/ print.zh.html print.en.html && echo "in sync ✓"`。

---

## 自审清单（计划作者已核对）
- **Spec 覆盖**：spec §3 入门/番外"适度"分层、§4.1 quizzes 覆盖全部剩余课。
- **分层正确**：L04–07 已 14–16k 不强加（只加题）；L15–22 偏薄才补图。避免对已深的课做无谓膨胀（YAGNI）。
- **依赖**：基于 M1 真值（provider/declarative/checkpoint/observability 真名）。
- **占位符**：无；每 task 给出加题清单、薄课补图点与闸门命令；含全课覆盖断言。
