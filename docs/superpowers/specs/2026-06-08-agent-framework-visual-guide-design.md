# Agent Framework 图解教程（双语 visual-guide）· 设计文档

- **Date:** 2026-06-08
- **Status:** Approved
- **Author:** @verdenmax (with Copilot CLI / superpowers brainstorming)
- **Reference project:** `../langchain-visual-guide/`（同一套生成器架构，已上线验证）

## 1. 目标（What & Why）

为 [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)（MAF）做一套面向**完全新手**的可视化（HTML 图解）教程，仿照 `langchain-visual-guide`：既有**宏观全景**，也有**内部源码细节**，每课配**真实源码文件对应**。

与参考项目的关键差异：

1. **覆盖 Python 实现为主**（MAF 同时有 Python + .NET，本教程聚焦 Python，关键处可点出 .NET 对照）。
2. **中英双语，可一键切换**（参考项目仅中文）。切换为纯静态实现，无后端。
3. **独立仓库**，位于 `../agent-framework-visual-guide/`，可单独部署到 GitHub Pages。

适用人群：没接触过 MAF、想从零入门的新手；想先建立宏观认知再深入源码的学习者；准备阅读 / 调试 / 贡献 MAF 源码的开发者。

## 2. 架构（复用已验证的生成器）

纯 Python、零第三方依赖的静态站点生成器（仅需 Python 3）。目录结构：

```
agent-framework-visual-guide/
├── index.html                  ← 目录页（入口，双语）
├── lessons/NN-*.html           ← 各课页面（每页内含中英两份内容 + 语言切换）
├── src/                        ← 生成器（可重建全部 HTML / PDF）
│   ├── shell.py                共享外壳：CSS 设计系统 + 双语切换脚本 + 导航 + index 页
│   ├── part1.py … part6.py     各部分课程内容（每课 zh + en 两份 HTML）
│   ├── registry.py             文件名 → {zh, en} 内容 的统一映射
│   ├── build.py                站点构建（→ index.html + lessons/）
│   ├── build_print.py          PDF 构建（→ print.html，折叠全展开；中/英各一份）
│   └── check_links.py          内链死链检查
├── .github/workflows/
│   ├── deploy.yml              CI：构建站点 + 渲染 PDF + 部署 Pages + 打 tag 时发 Release
│   └── ci.yml                  防回归：重建校验 HTML 无漂移 + 内链检查
├── README.md                   （双语说明）
└── LICENSE                     MIT
```

页面之间用**相对链接**互联，支持 `file://` 直接打开，也支持任意静态服务器 / GitHub Pages。

## 3. 双语机制（纯静态 HTML + 内联 JS，无后端）

**内容承载**：每课内容输出两份，分别包在语言容器里：

```html
<div class="i18n" data-lang="zh"> …中文内容… </div>
<div class="i18n" data-lang="en"> …English content… </div>
```

**切换**：顶栏放一个 `中 / EN` 切换按钮。内联 `<script>`（在浏览器里运行，不是服务器）：

- 读取 `localStorage['af-guide-lang']`（默认 `zh`），设置 `document.documentElement.dataset.lang`。
- CSS 据此显隐：`html[data-lang="en"] .i18n[data-lang="zh"] { display:none }`，反之亦然。
- 点击按钮翻转语言并写回 `localStorage`，**不刷新页面**。
- 为避免首屏闪烁，语言初始化脚本放在 `<head>`，在内容渲染前设定 `data-lang`。

**元数据双语**：`shell.PAGES` 中每课的标题、副标题、部分名都存中英两份（如 `("01-....html", {"zh": "...", "en": "..."}, {"zh": "...", "en": "..."})`）。Hero、顶栏、目录页、上一课/下一课导航文案、按钮文案都按当前语言渲染两份并交由切换脚本控制。

**SEO / `<html lang>`**：`<html>` 标签 lang 属性默认 `zh-CN`；`<title>` 与 meta description 采用 `中文 — English` 拼接，保证两种语言都可被搜索到。

## 4. 视觉标识（与参考项目区分）

- 主题色：由参考项目的 LangChain 绿（`#1a7f64`）改为 **Azure 蓝**（`--accent: #0078d4`，深色模式 `#4aa3e8`），辅色保留紫/琥珀/红。
- favicon：内联 SVG，圆角方块 + `AF` 字标（替代参考项目的 `λ`）。
- 其余设计系统（卡片、流程图、分层架构、表格、折叠卡片、代码块语法高亮、进度条、上/下课导航、深色模式）沿用参考项目并按需扩展。

## 5. 课程大纲（Python 为主 · 6 部分 · 22 课）

> 课程内容必须对照 MAF 真实 Python 源码（`python/packages/core/agent_framework/`）核实；代码片段以仓库 `python/samples/` 中的真实样例为准（注意 `client.as_agent(...)`、`Message`/`ChatMessage`、`@tool` 等当前 API 细节，编写每课时逐一核对）。

### 第一部分 · 宏观全景
1. **Agent Framework 是什么** — 解决什么问题 · 核心心智模型 · 作为 Semantic Kernel / AutoGen 的统一继任者
2. **Monorepo 全景** — `core` + 各 provider 包 + `lab`；Python 与 .NET 双实现对照
3. **一次 `agent.run()` 的生命周期** — 从你的代码到 LLM 的完整数据流

### 第二部分 · 用户视角
4. **消息与内容** — `Message`/`ChatMessage` · Role · Contents（text / function_call / function_result / data …）
5. **ChatClient 与创建 Agent** — `FoundryChatClient`/`OpenAIChatClient` · `client.as_agent()` · `run` / `run(stream=True)`
6. **工具 Tools** — `@tool` 装饰器 · `approval_mode` · 工具调用
7. **线程与记忆 `AgentThread`** — 多轮对话 · 上下文 · context providers / memory

### 第三部分 · 内部源码
8. **Agent 抽象** — `BaseAgent` / `Agent` 调用链 · `AgentRunResponse` / `Update`
9. **ChatClient 协议与管道** — `BaseChatClient` · `get_response` / `get_streaming_response`
10. **工具调用内部** — 函数 → JSON Schema → `function_call` → 执行 → `function_result`
11. **中间件 Middleware** — agent / chat / function 三层 · `call_next`
12. **Workflows 工作流引擎** — `Executor` / `Edge` / `WorkflowBuilder` · 消息驱动的图执行
13. **编排模式** — Sequential / Concurrent / Handoff / Group chat / Magentic
14. **流式与可观测性** — streaming updates · OpenTelemetry 集成

### 第四部分 · 进阶实战
15. **读源码 / 调试 / 测试 / 贡献** — `uv` · `poe` 任务 · 测试 · DevUI

### 第五部分 · 自己动手做 Agent
16. **接入各家模型** — Foundry / Azure OpenAI / OpenAI / Anthropic / Ollama providers
17. **声明式 Agent（YAML）** — `declarative` 包
18. **写自己的中间件** — 自定义 `AgentMiddleware` / `FunctionMiddleware`
19. **检查点 · 人在环 · 持久化** — checkpointing · human-in-the-loop · DurableTask hosting
20. **端到端实战：拼一个多 Agent 工作流** — agent + 工具 + 编排 + 检查点 全拼起来

### 第六部分 · 番外篇
21. **横向对比：Agent Framework vs LangGraph vs AutoGen vs Semantic Kernel**
22. **全栈坐标系 & 学习地图** — Agent 编排流派 · AI 全栈分层 · 你在哪 · 隔壁层（推理 / 向量检索）学习地图

每课结构沿用参考项目：🌍 宏观理解 · 🔬 细节 / 真实源码对应 · 🧩 生活类比 · ✅ 关键要点 · 💡 设计亮点 · 折叠深挖卡片 · 顶部进度条 + 上一课 / 下一课导航。

## 6. PDF 构建

`build_print.py` 把全部课程合成单页文档（折叠卡片全展开、自动分页），用无头 Chromium 渲染 PDF。双语处理：

- 生成 `print.zh.html` 与 `print.en.html` 两份（各自只保留对应语言的 `.i18n` 块），分别渲染 `agent-framework-visual-guide.zh.pdf` 与 `agent-framework-visual-guide.en.pdf`。
- 目录页主推中文 PDF（与正文默认语言一致），英文 PDF 作为附加产物。

## 7. CI / 部署

- `deploy.yml`：push 到 `main`/`master` 或打 `v*` tag 时 → 重建站点 + `print.*.html` → 安装 CJK/emoji 字体 → 无头 Chrome 渲染中/英 PDF → 部署 `index.html` + `lessons/` + PDF 到 GitHub Pages；打 tag 时发 Release 附 PDF。
- `ci.yml`：每次 push / PR → 重新 `build.py` 校验提交的 HTML 与 `src/` 无漂移 + `check_links.py` 内链检查。
- 首次启用需在仓库 Settings → Pages → Source 选 GitHub Actions（与参考项目一致；注意 owner 需先手动启用一次 Pages，token 无法自动建站）。

## 8. 非目标（YAGNI）

- 不覆盖 .NET 的完整教程（仅在宏观/对照处提及）。
- 不做服务端 / 数据库 / 用户系统。
- 不做超过两种语言的国际化框架（仅中 + 英，硬编码两份内容即可）。
- 不引入前端构建工具（Webpack/Vite 等）或第三方 JS 库；切换逻辑为手写内联脚本。

## 9. 验收标准

1. `cd src && python build.py` 生成 `index.html` + `lessons/`（22 课），无第三方依赖。
2. 每课页面可在 `file://` 下打开，`中 / EN` 切换即时生效且刷新后保持选择。
3. 所有内链经 `check_links.py` 校验无死链。
4. `python build_print.py` 生成中英两份 `print.*.html`，可渲染出 PDF。
5. 课程中的代码片段与源码引用经核对，与 MAF 仓库当前 Python API 一致。
6. CI 工作流可在 GitHub 上构建并部署 Pages + PDF。
