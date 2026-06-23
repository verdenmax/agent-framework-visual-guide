# M1 · 准确性审计 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 把现有 27 课中的**代码片段、API/类/函数名、文件路径引用**逐一对真实源码 `../agent-framework` 核对，修掉伪造或过时的内容；不加深、不加题（那是 M2+）。

**Architecture:** 按"内容模块"（`src/part1.py … part7.py`）切分为 7 个审计 task。每个 task 由子代理：① 抽取该 part 所有事实性断言 ② 对 `../agent-framework/python` 源码逐条核对 ③ 修正错的 ④ `build.py`+`check_html.py`+`check_links.py` 全绿后提交。

**Tech Stack:** Python 3（生成器）；真实源码在 `../agent-framework/python/packages/*` 与 `../agent-framework/python/samples/*`。

---

## 背景速记（审计者必读）

- **被讲解源码根**：`/home/verden/course/agent-framework`（相对本仓库 `../agent-framework`）。Python 实现在 `python/`。
- **核心包**：`python/packages/core/agent_framework/`，私有模块带下划线：`_agents.py`（Agent/BaseAgent）、`_clients.py`（ChatClient/BaseChatClient）、`_tools.py`（@tool/AIFunction）、`_middleware.py`、`_sessions.py`、`_skills.py`、`_mcp.py`、`_telemetry.py`、`_evaluation.py`、`_types.py`；工作流在 `_workflows/`（`_executor.py`/`_edge.py`/`_workflow_builder.py`/`_orchestration*` 等）。
- **Provider 包**：`python/packages/{foundry,openai,anthropic,ollama,azure-ai,gemini,mistral,bedrock,...}`。
- **样例**：`python/samples/{01-get-started,02-agents,03-workflows,04-hosting,05-end-to-end}`。课程里写 `samples/01-get-started/01_hello_agent.py`（省略 `python/` 前缀）——**这是已核实正确的约定**，不要"修正"成带前缀。
- **公开 API 以 `__init__.py` 的导出为准**：`python/packages/core/agent_framework/__init__.py` 决定 `from agent_framework import X` 里哪些 X 真实存在。核对类/函数名时以此为权威。
- **生成物必须同步**：改 `src/part*.py` 后 `cd src && python build.py && python build_print.py`，提交 `index.html`/`lessons/`/`print.*.html`。

## 审计判定规则（区分"错"与"可接受的简化"）

- **必须修**：① 引用的**模块/文件路径**在源码中不存在；② `from agent_framework import X` 的 **X 不在公开导出**；③ 代码里调用了**不存在的类/方法/参数**；④ 明显**过时**的 API 名（源码已重命名）。
- **可接受（不要改）**：教学性**简化**的伪代码（已标注"简化自/示意"），省略 `python/` 前缀的 sample 路径，省略 import 细节，为可读性合并的步骤。
- **拿不准**：优先以 `__init__.py` 导出与 `grep` 源码为准；仍不确定就在报告里列出存疑项，不臆改。

## 审计方法（每个 part 子代理照做）

1. 用 `grep` 从该 part 抽取：`class="path">…`、代码块里的 `from agent_framework…import…`、`<span class="mono">…</span>` 中的类型名、注释里的 `简化自 …`/文件路径。
2. 对每条断言在 `../agent-framework/python` 用 `grep -rn`/`find` 核对存在性（类名/函数名/文件）。
3. 仅修"必须修"项；保留可接受的简化。
4. `cd src && python build.py && python check_html.py && python check_links.py` 全绿（0 ERROR）。
5. 提交：`fix(M1): audit part<N> code/paths against agent-framework source`（若该 part 0 错则提交 `chore(M1): part<N> audit — no changes needed` 或跳过提交并在报告说明）。

---

## Task 1: 审计 part1（L01–03 宏观全景）

**Files:** Modify (仅修错): `src/part1.py` · Verify against: `../agent-framework/python`

**审计重点（逐条 grep 核对）：**
- `from agent_framework import Agent`、`from agent_framework.foundry import FoundryChatClient` —— 在 `python/packages/core/agent_framework/__init__.py` 与 `python/packages/foundry/` 核对 `Agent`、`FoundryChatClient` 是否真实导出。
- `agent.run(...)`、`ChatClient`、`Message/Role/Content` 等心智模型名词 —— 在 `_agents.py`/`_clients.py`/`_types.py` 核对。
- L02 monorepo 列出的包名 —— 对 `python/packages/` 实际目录核对（a2a/ag-ui/anthropic/azure-*/foundry/openai/ollama/...）。
- L03 lifecycle 提到的调用链方法名 —— 对 `_agents.py`/`_clients.py` 核对。

- [ ] **Step 1: 抽取断言**　Run: `cd /home/verden/course/agent-framework-visual-guide && grep -nE "from agent_framework|import |class=\"path\"|简化自|FoundryChatClient|\\.run\\(|BaseAgent|ChatClient" src/part1.py`
- [ ] **Step 2: 逐条核对**　对每个类/函数/路径：`grep -rn "<name>" ../agent-framework/python/packages/core/agent_framework/ ../agent-framework/python/packages/foundry/`；包名用 `ls ../agent-framework/python/packages`。
- [ ] **Step 3: 仅修"必须修"项**（按上文判定规则）。教学简化保留。
- [ ] **Step 4: 闸门**　Run: `cd src && python build.py && python check_html.py && python check_links.py`　Expected: `structural check passed`（0 ERROR）+ 链接全解析。
- [ ] **Step 5: 提交**（若有改动）
```bash
cd /home/verden/course/agent-framework-visual-guide
git add src/part1.py index.html lessons/ print.zh.html print.en.html 2>/dev/null; python -c "import subprocess" ; cd src && python build_print.py >/dev/null; cd ..
git add src/part1.py index.html lessons/ print.zh.html print.en.html
git commit -m "fix(M1): audit part1 (L01-03) code/paths vs agent-framework source"
```
（若 0 错无改动：跳过提交，在报告注明"part1 audit clean"。）

## Task 2: 审计 part2（L04–07 用户视角）

**Files:** Modify (仅修错): `src/part2.py` · Verify against: `../agent-framework/python`

**审计重点：**
- L04 消息：`Message`/`ChatMessage`/`Role`/`TextContent`/`Contents` 等 —— 以 `_types.py` 与 `__init__.py` 导出为准（注意历史上有 `ChatMessage→Message` 的更名，核对当前真实名）。
- L05 ChatClient：`as_agent`/`.run`/`.run_stream`/`get_response` 等方法名 —— 核对 `_clients.py`/`_agents.py`。
- L06 工具：`@tool` 装饰器、`AIFunction`/工具 schema —— 核对 `_tools.py`。
- L07 会话记忆：`AgentSession`/`ContextProvider`/`AgentThread` —— 核对 `_sessions.py`（注意 session 与 thread 的真实命名）。

- [ ] **Step 1: 抽取**　Run: `grep -nE "from agent_framework|class=\"path\"|简化自|@tool|AIFunction|ContextProvider|AgentSession|AgentThread|ChatMessage|as_agent|run_stream|get_response" src/part2.py`
- [ ] **Step 2: 核对**　`grep -rn "<name>" ../agent-framework/python/packages/core/agent_framework/_types.py ../agent-framework/python/packages/core/agent_framework/_tools.py ../agent-framework/python/packages/core/agent_framework/_sessions.py ../agent-framework/python/packages/core/agent_framework/_clients.py ../agent-framework/python/packages/core/agent_framework/__init__.py`
- [ ] **Step 3: 仅修必须修项。**
- [ ] **Step 4: 闸门**（build + check_html + check_links 全绿）。
- [ ] **Step 5: 提交**（同 Task 1 模式，含 `python build_print.py` 后 `git add` 生成物）：`fix(M1): audit part2 (L04-07) code/paths vs agent-framework source`

## Task 3: 审计 part3（L08–14 内部源码 · 引用最密，重点）

**Files:** Modify (仅修错): `src/part3.py` · Verify against: `../agent-framework/python/packages/core/agent_framework`

**审计重点（这是源码引用最密集的一课组）：**
- L08 Agent 内部：`BaseAgent`/`Agent`/`AgentRunResponse`/`AgentResponse` —— 核对 `_agents.py`（注意真实返回类型名，历史上有 `AgentResponse` 命名问题）。
- L09 ChatClient 内部：`BaseChatClient`/`get_response`/`ChatResponse` —— 核对 `_clients.py`。
- L10 工具调用内部：函数→schema→call→result 链路、`AIFunction`/`FunctionCallContent`/`FunctionResultContent` —— 核对 `_tools.py`/`_types.py`。
- L11 中间件：`AgentMiddleware`/`FunctionMiddleware`/`ChatMiddleware`、三层 next 链 —— 核对 `_middleware.py`（真实协议/基类名）。
- L12 Workflows：`Executor`/`Edge`/`WorkflowBuilder`/`Workflow` —— 核对 `_workflows/_executor.py`/`_edge.py`/`_workflow_builder.py`/`_workflow.py`。
- L13 编排：`Sequential`/`Concurrent`/`Handoff`/`GroupChat`/`Magentic` 等编排器名 —— 在 `_workflows/` 下 `grep -rn` 核对真实类名/文件（可能在 `_orchestration*.py` 或独立模块）。
- L14 流式与可观测：`run_stream`/`AgentRunResponseUpdate`、OpenTelemetry 接入符号 —— 核对 `_telemetry.py` 与 `_agents.py`。

- [ ] **Step 1: 抽取**　Run: `grep -nE "from agent_framework|class=\"path\"|简化自|BaseAgent|BaseChatClient|get_response|WorkflowBuilder|Executor|Edge|Middleware|Magentic|Handoff|Concurrent|Sequential|GroupChat|RunResponse|Update" src/part3.py`
- [ ] **Step 2: 核对**　对每个名字：`grep -rn "<name>" ../agent-framework/python/packages/core/agent_framework/`（覆盖 `_workflows/` 子目录）。编排器名特别注意：`grep -rln "class .*Orchestrat\|Magentic\|Handoff\|GroupChat" ../agent-framework/python/packages/core/agent_framework/`。
- [ ] **Step 3: 仅修必须修项**（伪代码简化保留；只改不存在/更名的符号与路径）。
- [ ] **Step 4: 闸门**（build + check_html + check_links 全绿，0 ERROR）。
- [ ] **Step 5: 提交**：`fix(M1): audit part3 (L08-14) code/paths vs agent-framework source`（含重生 HTML/print）。

## Task 4: 审计 part4（L15 读源码/调试/测试/贡献）

**Files:** Modify (仅修错): `src/part4.py` · Verify against: `../agent-framework/python`（含 `pyproject.toml`/`DEV_SETUP.md`/`AGENTS.md`）

**审计重点：** `uv`/`poe` 任务名、测试命令、DevUI 启动方式、目录路径。
- [ ] **Step 1: 抽取**　Run: `grep -nE "class=\"path\"|简化自|uv |poe |pytest|devui|DevUI|pyproject|poe " src/part4.py`
- [ ] **Step 2: 核对**　对照 `../agent-framework/python/pyproject.toml`（poe tasks）、`../agent-framework/python/DEV_SETUP.md`、`../agent-framework/python/packages/devui/` 是否存在。
- [ ] **Step 3: 仅修必须修项**（命令/路径/任务名对不上才改）。
- [ ] **Step 4: 闸门**（build + check_html + check_links 全绿）。
- [ ] **Step 5: 提交**：`fix(M1): audit part4 (L15) commands/paths vs agent-framework source`（含重生 HTML/print）。

## Task 5: 审计 part5（L16–20 自己动手）

**Files:** Modify (仅修错): `src/part5.py` · Verify against: provider 包 + `declarative` + `durabletask` + samples

**审计重点：**
- L16 providers：`FoundryChatClient`/`AzureOpenAIChatClient`/`OpenAIChatClient`/`AnthropicChatClient`/`OllamaChatClient` 等 —— 对 `python/packages/{foundry,openai,anthropic,ollama,azure*}/` 核对真实类名与导入路径。
- L17 声明式：YAML schema 字段、`agent_framework.declarative` 接口 —— 对 `python/packages/declarative/` 与 `../agent-framework/schemas/` 核对。
- L18 自定义中间件：与 part3 L11 一致的 `AgentMiddleware`/`FunctionMiddleware` 名。
- L19 持久化/HITL：`checkpoint`/`DurableTask`/`RequestInfoExecutor`/人在环 API —— 对 `_workflows/_checkpoint.py`、`python/packages/durabletask/` 核对。
- L20 capstone：综合代码以真实 API 名核对。

- [ ] **Step 1: 抽取**　Run: `grep -nE "from agent_framework|class=\"path\"|简化自|ChatClient|Middleware|checkpoint|Checkpoint|DurableTask|RequestInfo|declarative|\\.yaml" src/part5.py`
- [ ] **Step 2: 核对**　provider 类名：`for p in foundry openai anthropic ollama; do grep -rln "class .*ChatClient" ../agent-framework/python/packages/$p/ ; done`；持久化：`grep -rn "RequestInfo\|Checkpoint\|class DurableTask" ../agent-framework/python/packages/core/agent_framework/_workflows/ ../agent-framework/python/packages/durabletask/`。
- [ ] **Step 3: 仅修必须修项。**
- [ ] **Step 4: 闸门**（全绿）。
- [ ] **Step 5: 提交**：`fix(M1): audit part5 (L16-20) code/paths vs agent-framework source`（含重生 HTML/print）。

## Task 6: 审计 part6（L21–22 番外）

**Files:** Modify (仅修错): `src/part6.py` · Verify against: 概念性内容，核对对 AF 自身的事实陈述

**审计重点：** L21 横向对比（AF vs LangGraph/AutoGen/SK）与 L22 全栈坐标系多为观点/对比，**对外部框架的描述不在本仓库源码范围**——只核对其中关于 **AF 自身**的事实（如"由 SK+AutoGen 演进""Python/.NET 双实现"、提到的 AF 模块/能力名）是否与源码一致；外部框架表述只做明显事实性纠错。
- [ ] **Step 1: 抽取**　Run: `grep -nE "class=\"path\"|简化自|Semantic Kernel|AutoGen|LangGraph|agent_framework|Workflow|Magentic" src/part6.py`
- [ ] **Step 2: 核对** AF 自身陈述（模块/能力名）对 `python/packages/core`。
- [ ] **Step 3: 仅修必须修项**（保持对比观点，纠明显错）。
- [ ] **Step 4: 闸门**（全绿）。
- [ ] **Step 5: 提交**（若有改动）：`fix(M1): audit part6 (L21-22) AF-self claims vs source`。

## Task 7: 审计 part7（L23–27 协议与生态）

**Files:** Modify (仅修错): `src/part7.py` · Verify against: `_skills.py`/`_mcp.py`/`_evaluation.py` + `a2a`/`ag-ui`/`foundry_hosting` 包

**审计重点：**
- L23 Skills：`Skill`/`SkillResource`/`SkillScript` 等 —— 核对 `_skills.py`（真实类/字段名）。
- L24 MCP：`MCPStdioTool`/`MCPStreamableHTTPTool`/`MCPWebsocketTool` —— 核对 `_mcp.py`。
- L25 托管 Agent：Foundry 部署 API —— 核对 `python/packages/foundry_hosting/`。
- L26 A2A + AG-UI：`python/packages/a2a/`、`python/packages/ag-ui/` 的真实入口符号。
- L27 评估与时间旅行：`Evaluator`/replay/checkpoint 回放 —— 核对 `_evaluation.py` 与 `_workflows/_checkpoint.py`。

- [ ] **Step 1: 抽取**　Run: `grep -nE "from agent_framework|class=\"path\"|简化自|Skill|MCP|MCPStdio|MCPStreamable|Evaluator|a2a|A2A|AGUI|AG-UI|replay" src/part7.py`
- [ ] **Step 2: 核对**　`grep -rn "class Skill\|MCPStdioTool\|MCPStreamableHTTPTool\|class Evaluator" ../agent-framework/python/packages/core/agent_framework/`；包入口：`ls ../agent-framework/python/packages/a2a ../agent-framework/python/packages/ag-ui ../agent-framework/python/packages/foundry_hosting`。
- [ ] **Step 3: 仅修必须修项。**
- [ ] **Step 4: 闸门**（全绿）。
- [ ] **Step 5: 提交**：`fix(M1): audit part7 (L23-27) code/paths vs agent-framework source`（含重生 HTML/print）。

## Task 8: M1 出口闸门

- [ ] **Step 1: 全量重生 + 校验**　Run: `cd src && python build.py && python build_print.py && python check_html.py && python check_links.py`　Expected: `structural check passed`（0 ERROR）+ 链接全解析。
- [ ] **Step 2: 零漂移**　Run: `cd /home/verden/course/agent-framework-visual-guide && git diff --quiet -- index.html lessons/ print.zh.html print.en.html && echo "in sync ✓"`
- [ ] **Step 3: 汇总**　在报告中列出：每个 part 改了哪些断言、存疑未改项（供人工复核）。M1 完成标准：所有"必须修"项已修、闸门全绿、存疑项已登记。

---

## 自审清单（计划作者已核对）

- **Spec 覆盖**：实现 spec 第 2 节目标 7「严格准确性…顺手审计现有课」。不加深/不加题（M2+）。
- **判定规则明确**：区分"必须修"与"可接受简化"，避免子代理把教学简化误判为错误而过度改写。
- **已实测前提**：cited sample 路径（如 `samples/01-get-started/01_hello_agent.py`）真实存在于 `python/samples/01-get-started/`；核心私有模块 `_agents/_clients/_tools/_middleware/_sessions/_skills/_mcp/_workflows` 已确认存在。
- **占位符**：无；每个 task 给出抽取/核对/闸门/提交的确切命令。
