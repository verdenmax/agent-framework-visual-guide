# M4 · 协议与生态加深 L23–27 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 把 L23（Agent Skills）、L24（MCP）、L25（Foundry 托管 Agent）、L26（A2A + AG-UI）、L27（评估与时间旅行）各加深到约 2×，每课补 worked-example 追踪 + 1–2 张新图 + 真实简化源码 + 自测题。

**Architecture / 配方：完全沿用 M2**（见 `…M2-deepen-core-L08-11.md` 的"背景速记 / 验收标准"）：CSS 原语复用、双语等量、强调用 `<strong>/<em>`（**严禁 Markdown**）、`<pre>` 内 `<`→`&lt;`、改完重生并提交生成物、闸门 `check_html`(0 ERROR)+`check_links`、引用前先 `grep` 核对真实符号。内容在 `src/part7.py`（按 `L23_ZH = r"""` 等变量标记定位，勿用绝对行号），题在 `src/quizzes.py`。

**当前深度**：L23≈7.9k / L24≈8.4k / L25≈7.4k / L26≈8.1k / L27≈9.6k 字（中）。**2× 目标 ≈ 15–19k**。

**M1 已核实的真实符号（可直接引用）：**
- L23 Skills：`InlineSkill(Skill)`（`_skills.py:729`）、`SkillFrontmatter`（:557）、`InlineSkillResource`（:121）、`InlineSkillScript`（:315）。构造：`InlineSkill(frontmatter=SkillFrontmatter(name=,description=), instructions=, resources=)`。
- L24 MCP：基类 `MCPTool`（`_mcp.py:263`），三个传输子类 `MCPStdioTool`（:2110）、`MCPStreamableHTTPTool`（:2254）、（websocket 同样在 `_mcp.py`，引用前 grep 确认名）。
- L25 托管：`python/packages/foundry_hosting/`（`InvocationsHostServer`/`ResponsesHostServer`、`ApprovalStorage` Protocol；引用前 grep 确认）。
- L26：`python/packages/a2a/agent_framework_a2a`、`python/packages/ag-ui/agent_framework_ag_ui`（入口符号 grep 确认）。
- L27：`Evaluator(Protocol)`（`_evaluation.py:683`，`evaluate()`）、`evaluate_agent`（:1629）、回放/检查点见 `_workflows/_checkpoint.py`。

---

## Task 1: 加深 L23 Agent Skills + quiz
**Files:** `src/part7.py`（L23_ZH/L23_EN）、`src/quizzes.py` · Verify: `_skills.py`
- [ ] **Step 1（worked-example）**：`<h2>追踪一个 Skill 的装载与调用</h2>` + `.vflow`：定义一个 `InlineSkill`（frontmatter + instructions + resources）→ 注册到 Agent → 模型决定使用 → 框架注入 skill 上下文/脚本 → 产出。
- [ ] **Step 2（新图）**：Skill 组成图（`.layers`/`table.t`）：`SkillFrontmatter`(元信息) + `instructions` + `resources`(资源) + `script`(可选)。
- [ ] **Step 3（源码块）**：`codefile`(path=`_skills.py`) 简化 `InlineSkill`/`SkillFrontmatter` 构造（核对真实字段）。
- [ ] **Step 4（why 正文）**：为什么把"技能"做成可复用、可声明的资源（vs 把指令硬塞进 prompt）。
- [ ] **Step 5（英文同步）。** **Step 6（quiz）** `"23-skills.html"`：MCQ（Skill 组成 / 与普通工具的区别 / frontmatter 作用）+ 开放题。
- [ ] **Step 7（闸门+提交）** `content(M4): deepen L23 skills 2x + worked-example + quiz`。

## Task 2: 加深 L24 MCP + quiz
**Files:** `src/part7.py`（L24_ZH/L24_EN）、`src/quizzes.py` · Verify: `_mcp.py`
- [ ] **Step 1（worked-example）**：`<h2>追踪一次 MCP 工具调用</h2>` + `.vflow`：`MCPStdioTool(command=...)` 启动子进程 → 列出远端工具 → 模型请求调用 → 经 stdio 转发 → 远端执行 → 结果回灌。
- [ ] **Step 2（新图）**：MCP 传输对照图（`table.t`）：`MCPStdioTool`(子进程/stdio) vs `MCPStreamableHTTPTool`(HTTP) vs websocket —— 各自连接方式/适用场景，共同基类 `MCPTool`。
- [ ] **Step 3（源码块）**：`codefile`(path=`_mcp.py`) 简化 `MCPTool` 基类与一个传输子类的关系（核对真实）。
- [ ] **Step 4（why 正文）**：为什么用 MCP 统一外部工具协议（一次对接，处处可用）。
- [ ] **Step 5（英文同步）。** **Step 6（quiz）** `"24-mcp.html"`：MCQ（三种传输的区别 / MCPTool 基类 / 何时用 stdio vs HTTP）+ 开放题。
- [ ] **Step 7（闸门+提交）** `content(M4): deepen L24 mcp 2x + worked-example + quiz`。

## Task 3: 加深 L25 Foundry 托管 Agent + quiz
**Files:** `src/part7.py`（L25_ZH/L25_EN）、`src/quizzes.py` · Verify: `python/packages/foundry_hosting/`
- [ ] **Step 1（定位）**：`grep -rn "class .*HostServer\|class ApprovalStorage" ../agent-framework/python/packages/foundry_hosting/` 确认真实入口类。
- [ ] **Step 2（worked-example）**：`<h2>追踪一次托管部署</h2>` + `.vflow`：本地 Agent → 托管服务器包装（`InvocationsHostServer`/`ResponsesHostServer`）→ 暴露 endpoint → 远端调用 → 审批存储（`ApprovalStorage`）介入。
- [ ] **Step 3（新图）** 托管架构图（`.flow`/`.layers`）：本地定义 → host server → 云端调用方。
- [ ] **Step 4（源码块）** `codefile` 简化 host server 入口（核对真实）。 **Step 5（why）** 为什么"2 行部署"——把运维/审批/伸缩交给托管层。
- [ ] **Step 6（英文同步）。** **Step 7（quiz）** `"25-hosted-agents.html"`：MCQ（托管层职责 / Invocations vs Responses / ApprovalStorage 作用）+ 开放题。
- [ ] **Step 8（闸门+提交）** `content(M4): deepen L25 hosted-agents 2x + worked-example + quiz`。

## Task 4: 加深 L26 A2A + AG-UI + quiz
**Files:** `src/part7.py`（L26_ZH/L26_EN）、`src/quizzes.py` · Verify: `a2a`/`ag-ui` 包
- [ ] **Step 1（定位）**：`grep -rn "^class \|^def " ../agent-framework/python/packages/a2a/agent_framework_a2a/__init__.py ../agent-framework/python/packages/ag-ui/agent_framework_ag_ui/__init__.py` 找真实入口符号。
- [ ] **Step 2（worked-example）**：两段对照——A2A：Agent A 调用远端 Agent B（agent-to-agent）；AG-UI：Agent 与前端 UI 的事件交互（agent-to-UI）。各用 `.vflow` 走一遍消息流。
- [ ] **Step 3（新图）** A2A vs AG-UI 定位图（`table.t`）：通信双方 / 协议 / 典型场景。
- [ ] **Step 4（源码块）** `codefile` 简化各自入口（核对真实）。 **Step 5（why）** 为什么需要标准化的 Agent 互联与 Agent-UI 协议。
- [ ] **Step 6（英文同步）。** **Step 7（quiz）** `"26-a2a-agui.html"`：MCQ（A2A vs AG-UI 各连接谁 / 适用场景）+ 开放题。
- [ ] **Step 8（闸门+提交）** `content(M4): deepen L26 a2a-agui 2x + worked-example + quiz`。

## Task 5: 加深 L27 评估与时间旅行 + quiz
**Files:** `src/part7.py`（L27_ZH/L27_EN）、`src/quizzes.py` · Verify: `_evaluation.py`、`_workflows/_checkpoint.py`
- [ ] **Step 1（worked-example）**：两段——评估：`Evaluator.evaluate()` / `evaluate_agent()` 对一组 `EvalItem` 打分产出 `EvalResults`；时间旅行：从某个 checkpoint 恢复并重放工作流。各用 `.vflow`。
- [ ] **Step 2（新图）** 评估流水线图 + 检查点/重放时间轴（`.flow`）。
- [ ] **Step 3（源码块）** `codefile`(path=`_evaluation.py`) 简化 `Evaluator`/`evaluate_agent` 签名（核对真实）。 **Step 4（why）** 为什么评估与可重放是生产级闭环（回归、调试、审计）。
- [ ] **Step 5（英文同步）。** **Step 6（quiz）** `"27-eval-timetravel.html"`：MCQ（Evaluator 产出什么 / 时间旅行依赖什么 / 为何需要重放）+ 开放题。
- [ ] **Step 7（闸门+提交）** `content(M4): deepen L27 eval-timetravel 2x + worked-example + quiz`。

## Task 6: M4 出口闸门
- [ ] build+build_print+check_html+check_links 全绿（0 ERROR）。
- [ ] 深度核对：`cd src && python3 -c "import part7,quizzes; [print(k,len(getattr(part7,k+'_ZH'))) for k in ['L23','L24','L25','L26','L27']]; [print(f,f in quizzes.QUIZZES) for f in ['23-skills.html','24-mcp.html','25-hosted-agents.html','26-a2a-agui.html','27-eval-timetravel.html']]"` → 五课 zh ≥ ~15000、均有 quiz。
- [ ] 零漂移：`git diff --quiet -- index.html lessons/ print.zh.html print.en.html && echo "in sync ✓"`。

---

## 自审清单（计划作者已核对）
- **Spec 覆盖**：spec §3 核心课 2×（协议生态）、§4.2 worked-example、§4.1 quizzes（L23–27）。
- **已实测前提**：所列真实符号（InlineSkill:729/MCPTool:263+MCPStdioTool:2110/MCPStreamableHTTPTool:2254/Evaluator:683/evaluate_agent:1629、a2a/ag-ui 包名）均已 grep 确认存在。
- **依赖**：基于 M1 准确性修复（part7 InlineSkill 构造已修真）。
- **占位符**：无；每课给出 worked-example 场景、图、源码块、quiz 主题与闸门命令。
