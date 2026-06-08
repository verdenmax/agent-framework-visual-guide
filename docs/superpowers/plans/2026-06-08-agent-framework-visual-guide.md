# Agent Framework 双语图解教程 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `agent-framework-visual-guide/` 生成一套面向新手的、中英双语可切换的 Microsoft Agent Framework (Python) 图解教程静态站点（22 课 / 6 部分）+ PDF + CI。

**Architecture:** 复用 `../langchain-visual-guide/` 已验证的纯 Python、零依赖静态站点生成器（`src/shell.py` 设计系统 + `part*.py` 内容 + `registry.py` 映射 + `build.py`/`build_print.py`/`check_links.py`）。新增双语机制：每课内容输出中英两份 `<div class="i18n" data-lang>`，顶栏切换按钮 + 内联 JS + `localStorage`，纯静态、无后端。

**Tech Stack:** Python 3（仅标准库）· 手写 HTML/CSS/内联 JS · GitHub Actions（Pages + 无头 Chrome 渲染 PDF）。

**参考文件（工作区内可直接读取）：** `/home/verden/course/langchain-visual-guide/src/{shell,build,build_print,check_links,registry,part1..part6}.py`、`.github/workflows/{deploy,ci}.yml`、`.gitignore`、`LICENSE`。

**源码核实基准（编写每课代码片段时必须对照）：** `/home/verden/course/agent-framework/python/packages/core/agent_framework/`。已核实的当前公共 API：`Agent`/`BaseAgent`（`_agents.py:1584`/`:314`）、`Message`/`Role`/`Content`（`_types.py:1672`、`__init__.py:459/469/386`）、`BaseChatClient`/`ChatResponse`/`ChatResponseUpdate`（`_clients.py:217`）、`AgentResponse`/`AgentResponseUpdate`（`__init__.py:359-360`）、`AgentSession`（`__init__.py:362`，**非** AgentThread）、`tool`/`FunctionTool`（`_tools.py:1145`/`:240`）、中间件 `AgentMiddleware`/`FunctionMiddleware`/`ChatMiddleware` + `AgentContext`/`FunctionInvocationContext`/`ChatContext`（`_middleware.py`）、`WorkflowBuilder`/`Workflow`/`Executor`/`Edge`/`WorkflowContext`（`_workflows/`）、编排包 `agent_framework_orchestrations`（`_concurrent.py`/`_group_chat.py`/`_handoff.py`/`_magentic.py`）。样例：`python/samples/01-get-started/01..08_*.py`。

---

## 设计常量

- 主色 `--accent: #0078d4`（Azure 蓝），深色 `#4aa3e8`；其余色板沿用参考项目。
- favicon：圆角方块 + `AF` 字标（替换参考的 `λ`）。
- 站点标题：`Agent Framework 图解教程 · Visual Guide`。
- 语言：默认 `zh`，可切换 `en`；`localStorage` 键 `af-guide-lang`。
- PDF 文件名：`agent-framework-visual-guide.zh.pdf` / `.en.pdf`。

## 文件结构

```
agent-framework-visual-guide/
├── index.html                    生成物
├── lessons/NN-*.html             生成物（22 个）
├── src/
│   ├── shell.py                  CSS + 双语切换 + bi()/biblock() + page() + index_page() + PAGES
│   ├── registry.py               CONTENT: filename -> {"zh":..,"en":..}
│   ├── part1.py … part6.py       各部分课程（每课 *_ZH / *_EN 两个 HTML 字符串）
│   ├── build.py                  → index.html + lessons/
│   ├── build_print.py            → print.zh.html / print.en.html
│   └── check_links.py            内链检查
├── .github/workflows/{deploy,ci}.yml
├── README.md · LICENSE · .gitignore
```

---

## Task 0: 项目脚手架

**Files:** Create `LICENSE`, `.gitignore`, `README.md`(stub), `src/` 目录。

- [ ] **Step 1** 复制 `.gitignore`（参考项目同款；把 `*.pdf` 保留忽略）。
- [ ] **Step 2** 写 `LICENSE`：MIT，`Copyright (c) 2026 verdenmax`。
- [ ] **Step 3** `README.md` 先放标题占位（Task 13 补全）。
- [ ] **Step 4** 提交：`git add -A && git commit -m "chore: scaffold project (license, gitignore)"`。

## Task 1: `src/shell.py` — 设计系统 + 双语机制

**Files:** Create `src/shell.py`。以参考 `shell.py` 为底，做以下**明确改动**：

- [ ] **Step 1** 端口 `CSS`：把所有 `--accent` 绿色（`#1a7f64`/`#0f5c48`/`#e4f3ee` 等）改为 Azure 蓝板；深色模式同理。其余规则原样保留。
- [ ] **Step 2** 追加双语 CSS：
```css
html[data-lang="zh"] .i18n[data-lang="en"],
html[data-lang="en"] .i18n[data-lang="zh"] { display: none !important; }
.langtoggle { cursor:pointer; font-size:.72rem; font-weight:700; color:var(--accent);
  background:var(--accent-soft); border:1px solid var(--accent); border-radius:999px;
  padding:.2rem .7rem; }
```
- [ ] **Step 3** favicon：把 `_FAVICON_SVG` 的 `λ` 文本改为 `AF`（`font-size:13`），底色 `#0078d4`。
- [ ] **Step 4** 新增双语 helper：
```python
def bi(zh, en):
    return f'<span class="i18n" data-lang="zh">{zh}</span><span class="i18n" data-lang="en">{en}</span>'

def biblock(zh, en):
    return f'<div class="i18n" data-lang="zh">{zh}</div>\n<div class="i18n" data-lang="en">{en}</div>'
```
- [ ] **Step 5** `PAGES`：每项改为 `(filename, {"zh":..,"en":..}, {"zh":..,"en":..})`（标题、部分名都双语）。按 Task 5–10 的 22 课填写（标题见各 part 任务）。
- [ ] **Step 6** 早期语言初始化脚本（放进 `<head>`，避免闪烁）：
```python
LANG_HEAD = ("<script>try{var l=localStorage.getItem('af-guide-lang')||'zh';"
             "document.documentElement.setAttribute('data-lang',l);}catch(e){}</script>")
```
- [ ] **Step 7** 切换脚本（页面尾部）：
```python
LANG_SCRIPT = """
(function(){
  function cur(){return document.documentElement.getAttribute('data-lang')||'zh';}
  function set(l){document.documentElement.setAttribute('data-lang',l);
    try{localStorage.setItem('af-guide-lang',l);}catch(e){}
    document.querySelectorAll('.langtoggle').forEach(function(b){b.textContent=(l==='zh'?'EN':'中');});}
  document.querySelectorAll('.langtoggle').forEach(function(b){
    b.addEventListener('click',function(){set(cur()==='zh'?'en':'zh');});});
  set(cur());
})();
"""
```
- [ ] **Step 8** `head_meta`：`og:site_name` 改为 `Agent Framework 图解教程 · Visual Guide`；`theme-color` `#0078d4`。把 `LANG_HEAD` 注入 `<head>`。
- [ ] **Step 9** `page(filename, content, ...)`：`content` 现在是 `{"zh":..,"en":..}` → 正文用 `biblock(content["zh"], content["en"])`。`<html lang="zh-CN" data-lang="zh">`。顶栏：用 `bi()` 渲染「目录/Contents」等文案；标题 `title["zh"]`+`title["en"]` 用 `bi()`；部分 pill 同理；进度 `NN / 22`；新增 `<span class="langtoggle">EN</span>` 按钮。上一课/下一课文案用 `bi("上一课","Prev")` 等，目标标题 `bi(prevTitle_zh, prevTitle_en)`。`<title>` 用 `zh — en` 拼接。页尾注入 `<script>{LANG_SCRIPT}</script>`（standalone 与否都注入，因为它与 `/files/` 导航无关；保留原 `NAV_SCRIPT` 仅非 standalone）。
- [ ] **Step 10** `index_page`：hero 标题/lead/legend/pdf 按钮、`toc-part`、每课标题与副标题都改双语（`subtitles` 改为 `{fname: {"zh":..,"en":..}}`，用 `bi()`）。PDF 按钮链接 `agent-framework-visual-guide.zh.pdf`，文案 `bi("下载中文 PDF","Download PDF")`，可再加一个英文 PDF 链接。
- [ ] **Step 11** 语法自检：`python -c "import ast,sys; ast.parse(open('src/shell.py').read())"` → 无输出即通过。
- [ ] **Step 12** 提交：`git add src/shell.py && git commit -m "feat: bilingual shell (design system + lang toggle)"`。

## Task 2: `src/registry.py` + `src/build.py` + `src/check_links.py`

- [ ] **Step 1** `registry.py`：`from partN import *`；`CONTENT = {fname: {"zh": LXX_ZH, "en": LXX_EN}, ...}`，顺序与 `shell.PAGES` 一致（22 项）。先用占位指向 part 任务里定义的变量；本任务可先只放 part1 的 3 课，随各 part 任务补全。
- [ ] **Step 2** `build.py`：与参考一致（`shell.page(fname, CONTENT[fname], standalone=True, home_href="../index.html")`；写 `lessons/` 与 `index.html`）。
- [ ] **Step 3** `check_links.py`：复制参考；`ALLOW_MISSING = {"agent-framework-visual-guide.zh.pdf","agent-framework-visual-guide.en.pdf"}`。
- [ ] **Step 4** 冒烟：先做一节最小内容（Task 5 的 L01）后运行 `cd src && python build.py && python check_links.py`，应输出写入文件数 + 链接全通过。
- [ ] **Step 5** 提交：`git commit -m "feat: registry + build + link checker"`。

## Task 3 (= 内容 Part 1): `src/part1.py` — 第一部分（01–03）

**每课写两个字符串 `LXX_ZH` / `LXX_EN`，复用参考项目的 HTML 词汇**（`.card analogy/macro/detail/key/spark/warn`、`.flow`/`.vflow`/`.layers`/`table.t`/`.codefile`/`pre.code`/`.accordion`+`.qa`）。每课须含：lead 段、🧩 类比 card、若干 h2、至少一个图（flow/vflow/layers）、1–2 个折叠深挖 accordion、✅ key card、💡 spark card。代码片段对照 `samples/01-get-started/` 与 core 源码。

- [ ] **L01 `01-what-is-agent-framework.html`** — 标题 zh「Agent Framework 是什么」/ en "What is Agent Framework"。内容：MAF 解决什么问题（厂商无关 ChatClient、结构化 Message、工具、Agent 循环、多 Agent 工作流）；心智模型；它是 Semantic Kernel + AutoGen 的统一继任者（Python+.NET 双语言、生产级）。表格「痛点 / 无框架 / MAF 做法」。代码对照 `samples/01-get-started/01_hello_agent.py`（`Agent(client=..., instructions=...)` + `await agent.run(...)`）。**这是模板课，写得最完整，后续课对照它的结构。**
- [ ] **L02 `02-monorepo.html`** — zh「Monorepo 全景」/ en "Monorepo Tour"。`.layers` 展示 `core`（`agent_framework`）+ provider 包（`foundry`/`openai`/`anthropic`/`ollama`…）+ `lab`；Python 与 .NET（`dotnet/src/Microsoft.Agents.AI*`）对照表。引用真实路径 `python/packages/`、`dotnet/src/`。
- [ ] **L03 `03-lifecycle.html`** — zh「一次 `agent.run()` 的生命周期」/ en "Lifecycle of one run"。`.vflow` 步骤：你的输入 → Agent 组装 Message/instructions → ChatClient → provider API → 响应/工具调用 → （工具循环）→ `AgentResponse`。对照 `_agents.py` Agent.run 调用链 + `samples/.../03_multi_turn.py`。
- [ ] **Step（每课通用）** 写完后在 `registry.py` 注册 → `cd src && python build.py && python check_links.py` → 浏览器/grep 抽查 `.i18n` 双份存在。
- [ ] **Commit:** `git commit -m "content: part 1 (lessons 01-03)"`。

## Task 4 (= 内容 Part 2): `src/part2.py` — 第二部分（04–07）

- [ ] **L04 `04-messages.html`** — 消息与内容：`Message`(role+contents)、`Role`、`Content`（文本/函数调用/函数结果等）。对照 `_types.py:1672` `Message`、`__init__.py` 中 `Content`/`Role`。表格对比「手拼 dict vs Message 对象」。
- [ ] **L05 `05-chat-models.html`** — ChatClient 与创建 Agent：`FoundryChatClient`/`OpenAIChatClient`，`client.as_agent(name=,instructions=)`（注意当前推荐 `as_agent`，但样例也用 `Agent(client=...)` 两种都展示），`run` / `run(stream=True)`。对照 `samples/01-get-started/01_hello_agent.py` + `_clients.py:217`。
- [ ] **L06 `06-tools.html`** — 工具：`@tool` 装饰器、`Annotated[..., Field(description=...)]`、`approval_mode`、`tools=[...]`。对照 `samples/.../02_add_tools.py` + `_tools.py:1145`。
- [ ] **L07 `07-sessions-memory.html`** — 会话与记忆：多轮对话、`AgentSession`、`ContextProvider`/`MemoryContextProvider`、history providers。对照 `samples/.../03_multi_turn.py`、`04_memory.py` + `__init__.py:362/387/454`。**注意：用 `AgentSession`，不要写 AgentThread。**
- [ ] **Commit:** `git commit -m "content: part 2 (lessons 04-07)"`。

## Task 5 (= 内容 Part 3): `src/part3.py` — 第三部分（08–14）

- [ ] **L08 `08-agent-internals.html`** — `BaseAgent`/`Agent` 调用链、`AgentResponse`/`AgentResponseUpdate`。对照 `_agents.py:314/1584`。
- [ ] **L09 `09-chatclient-internals.html`** — `BaseChatClient` 协议、`get_response`/`get_streaming_response`、`ChatResponse`/`Update`、`ChatOptions`。对照 `_clients.py:217`。
- [ ] **L10 `10-tool-internals.html`** — 函数 → JSON Schema → `function_call` → 执行 → `function_result` 闭环；`FunctionTool`。对照 `_tools.py:240/1145`。
- [ ] **L11 `11-middleware.html`** — 三层中间件 `AgentMiddleware`/`FunctionMiddleware`/`ChatMiddleware` + `*Context`，`call_next`（**无参** `await call_next()`），装饰器写法。对照 `_middleware.py:469/528/592/93/204/377`。
- [ ] **L12 `12-workflows.html`** — `WorkflowBuilder`/`Executor`/`Edge`/`WorkflowContext`、消息驱动的图执行、`@executor`/函数执行器。对照 `_workflows/_workflow_builder.py:53`、`_executor.py:30`、`_edge.py:76`、`samples/01-get-started/07_first_graph_workflow.py`。
- [ ] **L13 `13-orchestration.html`** — 编排模式 Sequential/Concurrent/Handoff/Group chat/Magentic。对照 `packages/orchestrations/agent_framework_orchestrations/{_concurrent,_group_chat,_handoff,_magentic}.py` + `samples/03-workflows/`。
- [ ] **L14 `14-streaming-observability.html`** — streaming updates（`run(stream=True)` 累积 `AgentResponseUpdate`）+ OpenTelemetry（`observability.py`、`samples/02-agents/observability/`）。
- [ ] **Commit:** `git commit -m "content: part 3 (lessons 08-14)"`。

## Task 6 (= 内容 Part 4): `src/part4.py` — 第四部分（15）

- [ ] **L15 `15-contributing.html`** — 读源码/调试/测试/贡献：`uv sync`、`uv run poe`（见 `python/DEV_SETUP.md`/`AGENTS.md`）、测试、DevUI（`packages/devui`）。对照仓库真实命令。
- [ ] **Commit:** `git commit -m "content: part 4 (lesson 15)"`。

## Task 7 (= 内容 Part 5): `src/part5.py` — 第五部分（16–20）

- [ ] **L16 `16-providers.html`** — 接入各家模型：`foundry`/`openai`(`azure`)/`anthropic`/`ollama` 包，统一 `as_agent`。对照 `samples/02-agents/providers/`。
- [ ] **L17 `17-declarative.html`** — 声明式 YAML Agent：`declarative` 包。对照 `packages/declarative`、`declarative-agents/`、`samples/02-agents/declarative/`。
- [ ] **L18 `18-custom-middleware.html`** — 写自定义中间件（落地版，承接 L11）。对照 `samples/02-agents/middleware/`。
- [ ] **L19 `19-durability-hitl.html`** — 检查点 + 人在环 + 持久化：`InMemoryCheckpointStorage`、HITL、DurableTask hosting。对照 `samples/03-workflows/{checkpoint,human-in-the-loop}/`、`packages/durabletask`。
- [ ] **L20 `20-capstone.html`** — 端到端：agent + 工具 + 编排 + 检查点拼一个多 Agent 工作流。综合前面所有，给完整可读代码骨架。
- [ ] **Commit:** `git commit -m "content: part 5 (lessons 16-20)"`。

## Task 8 (= 内容 Part 6): `src/part6.py` — 第六部分（21–22）

- [ ] **L21 `21-vs-others.html`** — 横向对比：AF vs LangGraph vs AutoGen vs Semantic Kernel（两栏 `.cols` + 表格；范式/编排模型/语言支持/生产特性）。
- [ ] **L22 `22-stack-map.html`** — 全栈坐标系 & 学习地图：Agent 编排流派、AI 全栈分层、你在哪、隔壁层（推理/向量检索）学习地图。可借鉴参考项目 `part6.py` 的 `22/23` 课结构。
- [ ] **Commit:** `git commit -m "content: part 6 (lessons 21-22)"`。

## Task 9: `src/build_print.py`（双语 PDF）

**Files:** Create `src/build_print.py`（以参考为底，改为按语言出两份）。

- [ ] **Step 1** `build_print(lang)`：每课取 `CONTENT[fname][lang]`（只该语言，不加 `.i18n` 包装）；`lesson-head` 用 `title[lang]`/`part[lang]`；accordion 展开同参考。封面/目录文案按 `lang`。输出 `print.{lang}.html`，`<html data-lang="{lang}">`。
- [ ] **Step 2** `__main__`：循环 `for lang in ("zh","en"): build_print(lang)`。
- [ ] **Step 3** 验证：`cd src && python build_print.py` → 生成 `print.zh.html`/`print.en.html`；`grep -c 'print-lesson' ../print.zh.html` == 22。
- [ ] **Step 4** 提交：`git commit -m "feat: bilingual print/PDF builder"`。

## Task 10: CI 工作流

**Files:** Create `.github/workflows/deploy.yml`, `.github/workflows/ci.yml`（以参考为底改名）。

- [ ] **Step 1** `deploy.yml`：`build.py` + `build_print.py`；用无头 Chrome 渲染 `print.zh.html`→`agent-framework-visual-guide.zh.pdf` 和 `print.en.html`→`.en.pdf`；`_site` 拷贝 `index.html`+`lessons/`+两个 PDF + `.nojekyll`；上传 Pages + tag 时 Release 附两个 PDF。安装 `fonts-noto-cjk fonts-noto-color-emoji`。
- [ ] **Step 2** `ci.yml`：`build.py` 后 `git diff --quiet -- index.html lessons/`（防漂移）+ `check_links.py`。
- [ ] **Step 3** 提交：`git commit -m "ci: pages deploy + drift/link checks"`。

## Task 11: README（双语）+ 最终验证

- [ ] **Step 1** `README.md`：双语介绍、徽章、在线阅读/PDF 链接占位、结构图、重建命令（`cd src && python build.py` / `build_print.py`）、双语切换说明、Pages 启用步骤。
- [ ] **Step 2** 全量重建：`cd src && python build.py && python build_print.py && python check_links.py`。
- [ ] **Step 3** 抽查：随机打开 2 课，确认 `中/EN` 切换即时生效、刷新保持；`grep -c 'class="i18n"' ../lessons/01-*.html` > 0。
- [ ] **Step 4** 提交：`git add -A && git commit -m "docs: README + final rebuild"`。

---

## 自检（写完计划后）

- **覆盖**：spec 第 5 节 22 课 → Task 3–8 全覆盖；双语机制 → Task 1；PDF → Task 9；CI → Task 10。✓
- **命名一致**：全程 `Message`/`AgentSession`/`AgentResponse`/`as_agent`/`@tool`；`bi()`/`biblock()`/`CONTENT[fname]={"zh","en"}`/`PAGES` 三元组 + dict 标题，前后一致。✓
- **占位**：内容课为生成式工作，已给出结构 + 真实源码锚点 + 模板课（L01）；非占位。✓
