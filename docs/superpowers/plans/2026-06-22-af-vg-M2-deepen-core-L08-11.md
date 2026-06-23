# M2 · 核心内部原理加深 L08–11 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 把 L08–L11（Agent / ChatClient / 工具调用 / 中间件 的内部原理）四课各加深到约 2×，每课补一段 **worked-example 逐步追踪**、1–2 张新图、更多"为什么"正文、真实引用的简化源码，并在 `quizzes.py` 为每课加 2–3 道选择 + 1–2 道开放题。

**Architecture:** 内容在 `src/part3.py`（`L08_ZH/L08_EN … L11_ZH/L11_EN`），自测题在 `src/quizzes.py`。一课一个 task：先加深 part3 的该课中英内容，再加该课 quiz。复用既有 CSS 原语（`.vflow/.step/.num/.sc`、`.layers/.layer`、`.flow/.node`、`.codefile/.code`、`.accordion/.qa`、`.card.analogy`、`table.t`）。

**Tech Stack:** Python 3 生成器；真实源码 `../agent-framework/python/packages/core/agent_framework/`（`_agents.py`/`_clients.py`/`_tools.py`/`_middleware.py`/`_types.py`）。

> **前置**：M1 审计已让 L08–11 的现有引用对齐真实源码；M2 在此基础上"加内容"，不得引入未核对的新 API 名。

---

## 背景速记（实现者必读）

- **当前深度**：L08≈11.8k / L09≈9.6k / L10≈9.3k / L11≈11.3k 字（中）。**2× 目标 ≈ 18–24k 字（中）**，英文同步加深。
- **现有结构（保留并扩展，不要删）**：每课已有 `lead` 引子 + `card analogy` 类比 + 若干 `<h2>` 小节 + `vflow` 步骤 + 多个 4-QA `accordion`（🧪示例/❓为什么/✅MAF做法/🔀其他方案）+ 结尾"关键要点/设计亮点"。
- **加深手段（每课都要做）**：
  1. **worked-example 追踪**：用一个**具体输入**端到端走一遍，逐步展示真实数据如何变化（用 `.vflow`+`.step`，或 `.flow`+`.node` 横向时序）。
  2. **+1–2 张新图**：结构/分层/时序/数据形状（用 `.layers`/`.flow`/`table.t`）。
  3. **真实简化源码**：从对应 `_*.py` 摘取关键签名/结构，用 `<div class="codefile"><div class="cf-head">…<span class="path">_agents.py</span></div><pre class="code">…</pre></div>`，注释标"简化自 …"。`<pre>` 内字面 `<` 必须写 `&lt;`。
  4. **更多"为什么"正文**：每个新小节给设计取舍，而非只描述"是什么"。
- **双语等量**：中英内容深度一致（英文不是缩水版）。
- **生成物同步**：改完 `cd src && python build.py && python build_print.py`，提交 `index.html`/`lessons/`/`print.*.html`。
- **闸门**：`python check_html.py` 0 ERROR（注意：现在每课视觉块密度 WARN 应因加图而减少/消失）；`python check_links.py` 全解析。
- **quiz 写法**：编辑 `src/quizzes.py` 的 `QUIZZES` 字典，新增该课条目（schema 见文件头与 L01 既有条目）；`render` 是按语言的，`build.py` 已自动接入。`<` 写 `&lt;`。

## 每课验收标准

- 中文内容 ≥ ~18k 字（约现有 1.8–2×），英文相应加深；新增恰好 1 段 worked-example 追踪 + ≥1 张新图 + ≥1 个真实 `codefile` 源码块。
- `quizzes.py` 中该课有 2–3 道 MCQ（含 `why` 解析）+ 1–2 道开放题，中英齐全，`_validate()` 通过。
- 闸门全绿；该课 `check_html.py` 不再报"visual blocks"WARN（密度达标）。

---

## Task 1: 加深 L08 Agent 内部（`src/part3.py` L08_ZH/L08_EN）+ quiz

**Files:** Modify `src/part3.py`（L08_ZH 第 4–195 行、L08_EN 第 196–390 行）、`src/quizzes.py`
**Verify against:** `../agent-framework/python/packages/core/agent_framework/_agents.py`、`_types.py`

**保留**现有：两层结构 layers、run() 5 步 vflow、4 个 accordion。**新增**：

- [ ] **Step 1（worked-example 追踪）**：在"run() 内部做了什么"之后，加一段 `<h2>追踪一次真实 run()</h2>` + `.vflow`，用具体输入 `agent.run("巴黎今天天气如何？")`（Agent 带一个 `get_weather` 工具）逐步展示**消息列表如何增长**：
  ① 初始 `[system(instructions), user("巴黎…")]` → ② ChatClient 返回含 `function_call get_weather{city:"Paris"}` 的回复 → ③ 执行工具得 `FunctionResultContent("18°C 晴")` → ④ 消息变 `[system, user, assistant(call), tool(result)]` → ⑤ 再次调 ChatClient → ⑥ 得最终文本 → ⑦ 包装 `AgentResponse`。每步用 `.step` 显示该步的消息列表快照（可用 `table.t` 或 `<pre class="code">` 展示 messages 数组）。
- [ ] **Step 2（新图）**：加一张三层组合图（`.layers`）：`Agent = AgentMiddlewareLayer + AgentTelemetryLayer + RawAgent`（Mixin 多继承），标注各层职责与对应源码符号（核对 `_agents.py`：`AgentMiddlewareLayer` 来自 `_middleware`，`RawAgent` 在 `_agents.py:578`）。
- [ ] **Step 3（真实源码块）**：加一个 `codefile`（path=`_agents.py`），简化展示 `run()` 的 `@overload`（非流式返回 `AgentResponse`，`stream=True` 返回更新流）与 `_prepare_run_context()/_call_chat_client()/_run_after_providers()` 的职责（核对真实方法名后照搬，`<` 写 `&lt;`）。
- [ ] **Step 4（why 正文）**：在结尾前加 `<h2>为什么这样设计</h2>` 2–3 段，讲模板方法 + Mixin 分层带来的可测试性/可扩展性取舍。
- [ ] **Step 5（英文同步）**：L08_EN 等量补上述四项。
- [ ] **Step 6（quiz）**：在 `src/quizzes.py` 的 `QUIZZES` 加 `"08-agent-internals.html"`：2–3 道 MCQ（例：`AgentResponse` 包装了什么 / 工具循环何时终止 / 为何用 BaseAgent 抽象 / 三层 Mixin 的好处）+ 1 道开放题；每题 `why` 解析，中英齐全。
- [ ] **Step 7（闸门+提交）**：`cd src && python build.py && python build_print.py && python check_html.py && python check_links.py`（0 ERROR、链接全解析、L08 不再报 visual WARN）。提交：
```bash
cd /home/verden/course/agent-framework-visual-guide
git add src/part3.py src/quizzes.py index.html lessons/ print.zh.html print.en.html
git commit -m "content(M2): deepen L08 agent-internals 2x + worked-example + quiz

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Task 2: 加深 L09 ChatClient 内部（`src/part3.py` L09_ZH/L09_EN）+ quiz

**Files:** Modify `src/part3.py`（L09_ZH 第 391–542 行、L09_EN 第 543–697 行）、`src/quizzes.py`
**Verify against:** `../agent-framework/python/packages/core/agent_framework/_clients.py`、`_types.py`（`BaseChatClient`/`get_response`/`ChatResponse`/`ChatResponseUpdate`；核对真实名）

- [ ] **Step 1（worked-example 追踪）**：`<h2>追踪一次 get_response</h2>` + `.vflow`：以一条用户消息为例走 `BaseChatClient.get_response()` → 组装 provider 选项 → 调具体 provider 的内部方法（核对真实名，如 `_inner_get_response`）→ 把厂商原始返回 **归一化**为 `ChatResponse`。用 `table.t` 并排"厂商原始 JSON 片段 → 统一 `ChatResponse` 字段"。
- [ ] **Step 2（新图）**：`.layers` 或 `.flow`：`BaseChatClient`（模板/归一化） ← 各 provider 子类（FoundryChatClient/OpenAIChatClient…）。标注"厂商差异只在子类里"。
- [ ] **Step 3（真实源码块）**：`codefile`(path=`_clients.py`) 简化 `get_response()` 与抽象的 provider 钩子方法签名（核对后照搬）。
- [ ] **Step 4（why 正文）**：为什么把所有厂商归一化到同一 `ChatResponse`（换厂商只改一行的根因）+ 流式与非流式的统一处理。
- [ ] **Step 5（英文同步）**。
- [ ] **Step 6（quiz）**：`"09-chatclient-internals.html"`：MCQ（归一化的价值 / 厂商差异住在哪一层 / 流式返回类型）+ 开放题。
- [ ] **Step 7（闸门+提交）**：同 Task 1，提交信息 `content(M2): deepen L09 chatclient-internals 2x + worked-example + quiz`。

## Task 3: 加深 L10 工具调用内部（`src/part3.py` L10_ZH/L10_EN）+ quiz

**Files:** Modify `src/part3.py`（L10_ZH 第 698–846 行、L10_EN 第 847–998 行）、`src/quizzes.py`
**Verify against:** `../agent-framework/python/packages/core/agent_framework/_tools.py`、`_types.py`（`@tool`/`AIFunction`/`FunctionCallContent`/`FunctionResultContent`；核对真实名）

- [ ] **Step 1（worked-example 追踪）**：`<h2>从函数到结果：追踪一次工具调用</h2>` + `.vflow`，以一个真实 `@tool def get_weather(city: str) -> str` 为例：① 装饰器读签名+docstring → ② 生成 **JSON schema**（用 `<pre class="code">` 展示真实 schema 形状）→ ③ 模型回 `FunctionCallContent(name, arguments)` → ④ 框架按名查表、解析参数 → ⑤ 调用 Python 函数 → ⑥ 包装 `FunctionResultContent` 回灌。
- [ ] **Step 2（新图）**：数据形状图（`table.t`）：Python 函数签名 → 生成的 schema 字段一一对应（name/description/parameters/required）。
- [ ] **Step 3（真实源码块）**：`codefile`(path=`_tools.py`) 简化 `@tool`/`AIFunction` 如何从函数生成 schema（核对真实实现摘取关键片段）。
- [ ] **Step 4（why 正文）**：为什么用 docstring+类型注解自动生成 schema（DRY：一处定义，既是实现又是契约）；参数校验与错误回灌。
- [ ] **Step 5（英文同步）**。
- [ ] **Step 6（quiz）**：`"10-tool-internals.html"`：MCQ（schema 来源 / FunctionCallContent vs FunctionResultContent / 为何自动生成）+ 开放题。
- [ ] **Step 7（闸门+提交）**：同上，`content(M2): deepen L10 tool-internals 2x + worked-example + quiz`。

## Task 4: 加深 L11 中间件（`src/part3.py` L11_ZH/L11_EN）+ quiz

**Files:** Modify `src/part3.py`（L11_ZH 第 999–1188 行、L11_EN 第 1189–1381 行）、`src/quizzes.py`
**Verify against:** `../agent-framework/python/packages/core/agent_framework/_middleware.py`（`AgentMiddleware`/`FunctionMiddleware`/`ChatMiddleware`、`next` 链、`categorize_middleware`；核对真实名）

- [ ] **Step 1（worked-example 追踪）**：`<h2>追踪一次带中间件的调用</h2>` + `.flow`/`.vflow`：展示**洋葱模型**——请求依次穿过 agent → function → chat 三层中间件的"进"，到达 LLM/工具后再逆序"出"。用具体例子：一个记录耗时的中间件如何在 `await next()` 前后打点。
- [ ] **Step 2（新图）**：洋葱/三层环绕图（用嵌套 `.layers` 或 `.flow` 表示 in→core→out 顺序），标注三类中间件各拦截什么（agent.run / function call / chat request）。
- [ ] **Step 3（真实源码块）**：`codefile`(path=`_middleware.py`) 简化一个中间件的签名与 `await next(context)` 模式（核对真实协议/类型名）。
- [ ] **Step 4（why 正文）**：为什么用洋葱模型而非回调列表（可改请求也可改响应、可短路）；三层分离的职责边界。
- [ ] **Step 5（英文同步）**。
- [ ] **Step 6（quiz）**：`"11-middleware.html"`：MCQ（洋葱模型执行顺序 / 三类中间件分别拦截什么 / next 的作用 / 短路）+ 开放题。
- [ ] **Step 7（闸门+提交）**：同上，`content(M2): deepen L11 middleware 2x + worked-example + quiz`。

## Task 5: M2 出口闸门

- [ ] **Step 1**：`cd src && python build.py && python build_print.py && python check_html.py && python check_links.py` → 0 ERROR、链接全解析。
- [ ] **Step 2（深度核对）**：
```bash
cd /home/verden/course/agent-framework-visual-guide/src && python3 -c "
import part3, quizzes
for k in ['L08','L09','L10','L11']:
    zh=len(getattr(part3,k+'_ZH'))
    print(k,'zh chars=',zh,'(target >=18000)')
for f in ['08-agent-internals.html','09-chatclient-internals.html','10-tool-internals.html','11-middleware.html']:
    assert f in quizzes.QUIZZES, f
    print(f,'quiz OK, mcq=',len(quizzes.QUIZZES[f].get('mcq',[])))
"
```
Expected: 四课 zh ≥ ~18000；四课均有 quiz。
- [ ] **Step 3（零漂移）**：`git diff --quiet -- index.html lessons/ print.zh.html print.en.html && echo "in sync ✓"`。

---

## 自审清单（计划作者已核对）
- **Spec 覆盖**：实现 spec §3 核心课 2×、§4.2 worked-example、§4.3 核心配方、§4.1 quizzes（L08–11 部分）。
- **依赖**：基于 M1 审计后的准确引用；不引入未核对 API。
- **已实测前提**：L08–11 现有内容与真实 `_agents.py` 符号（`BaseAgent:314`/`RawAgent:578`/`AgentResponse`/`_prepare_run_context`）一致；CSS 原语（vflow/step/num/sc/layers/flow/codefile/table.t）均在 shell.CSS 存在。
- **占位符**：无；每课给出 worked-example 场景、图、源码块、quiz 主题与确切闸门命令。
