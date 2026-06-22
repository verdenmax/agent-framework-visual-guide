# Agent Framework 图解教程 · Visual Guide

[![📖 在线阅读](https://img.shields.io/badge/%F0%9F%93%96%20%E5%9C%A8%E7%BA%BF%E9%98%85%E8%AF%BB-Read%20Online-0078d4?style=for-the-badge)](https://verdenmax.github.io/agent-framework-visual-guide/)
[![📄 中文 PDF](https://img.shields.io/badge/%F0%9F%93%84%20%E4%B8%AD%E6%96%87%20PDF-Download-b4690e?style=for-the-badge)](https://github.com/verdenmax/agent-framework-visual-guide/releases/latest/download/agent-framework-visual-guide.zh.pdf)
[![📄 English PDF](https://img.shields.io/badge/%F0%9F%93%84%20English%20PDF-Download-b4690e?style=for-the-badge)](https://github.com/verdenmax/agent-framework-visual-guide/releases/latest/download/agent-framework-visual-guide.en.pdf)

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Lessons](https://img.shields.io/badge/lessons-31-blue.svg)
![Parts](https://img.shields.io/badge/parts-8-9cf.svg)
![Built with](https://img.shields.io/badge/built%20with-Python%203-3776AB.svg?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)
![Language](https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87%20%2F%20EN-orange.svg)

一套面向**完全新手**的中英双语可视化（HTML 图解）教程，带你从零开始理解
[Microsoft Agent Framework](https://github.com/microsoft/agent-framework)（Python 实现）。

A bilingual (中/EN) visual tutorial for complete beginners, helping you understand
[Microsoft Agent Framework](https://github.com/microsoft/agent-framework) (Python) from scratch.

**一键切换语言** · 每页顶栏有 `中 / EN` 切换按钮，无需刷新。

## 📚 教程结构 · Tutorial Structure

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

### 第一部分 · 宏观全景 | Part 1 · Big Picture
1. **Agent Framework 是什么** — 解决什么问题 · 核心心智模型
2. **Monorepo 全景** — core + provider 包；Python / .NET 对照
3. **一次 run() 的生命周期** — 从你的代码到 LLM 的完整数据流

### 第二部分 · 用户视角 | Part 2 · User's View
4. **消息与内容** — Message · Role · Content
5. **ChatClient 与创建 Agent** — as_agent · run / stream
6. **工具 Tools** — @tool 装饰器 · 工具调用
7. **会话与记忆** — AgentSession · ContextProvider

### 第三部分 · 内部源码 | Part 3 · Internals
8. **Agent 内部** — BaseAgent 调用链 · AgentResponse
9. **ChatClient 内部** — BaseChatClient · get_response
10. **工具调用内部** — 函数 → schema → call → result
11. **中间件 Middleware** — agent / function / chat 三层
12. **Workflows 工作流引擎** — Executor / Edge / WorkflowBuilder
13. **编排模式** — Sequential / Concurrent / Handoff / Group / Magentic
14. **流式与可观测性** — streaming · OpenTelemetry

### 第四部分 · 进阶实战 | Part 4 · Advanced
15. **读源码 / 调试 / 测试 / 贡献** — uv · poe · 测试 · DevUI
29. **DevUI 可视化调试** — serve() · 请求 / 消息 / trace 可视化
30. **可观测性深入** — OpenTelemetry · span 树 · trace / metric

### 第五部分 · 自己动手做 Agent | Part 5 · Build Your Own
16. **接入各家模型** — Foundry / AzureOpenAI / OpenAI / Anthropic / Ollama
17. **声明式 Agent（YAML）** — YAML 定义 Agent
18. **写自己的中间件** — 自定义 Agent / Function middleware
19. **检查点 · 人在环 · 持久化** — checkpoint · HITL · DurableTask
20. **端到端实战：多 Agent 工作流** — 把所有零件拼成一个工作流
28. **记忆后端** — Redis / Mem0 / Cosmos · ContextProvider / HistoryProvider

### 第六部分 · 协议与生态 | Part 6 · Protocols & Ecosystem
23. **Agent Skills 技能系统** — Skill · InlineSkill · 技能打包与复用
24. **MCP 工具协议** — MCPTool · stdio / HTTP / websocket
25. **Foundry 托管 Agent** — ResponsesHostServer · 托管历史 / 检查点 / 审批
26. **A2A + AG-UI 协议** — Agent 间通信 · Agent ↔ 前端
27. **评估与时间旅行** — Evaluator · 时间旅行调试

### 第七部分 · 番外篇 | Part 7 · Bonus
21. **横向对比：AF vs 其他框架** — AF vs LangGraph / AutoGen / SK
22. **全栈坐标系 & 学习地图** — 编排流派 · 全栈分层 · 你在哪

### 第八部分 · 速查 | Part 8 · Quick Reference
31. **术语表 · 速查** — 核心术语 · 源码位置 · 概念依赖图

## 🚀 如何阅读 · How to Read

直接用浏览器打开 **`index.html`**（双击或拖入浏览器）。页面是自包含的，支持 `file://` 直接打开：

```bash
# 可选：用任意静态服务器本地预览
python -m http.server 8000
# 然后访问 http://localhost:8000/
```

## 🎨 每页包含 · What Each Page Has

- 🌍 **宏观理解** / Big Picture — 大局观，为什么这样设计
- 🔬 **细节 / 代码对应** / Source References — 指向真实源码文件
- 🧩 **生活类比** / Analogy — 日常事物帮助理解抽象概念
- ✅ **关键要点** / Key Points — 每课小结
- 💡 **设计亮点** / Design Highlight — 最精妙的设计思想
- 🔄 **中 / EN 切换** — 顶栏一键切换，`localStorage` 记住选择

## 📁 项目结构 · Project Structure

```
agent-framework-visual-guide/
├── index.html              ← 入口（目录页）
├── lessons/                ← 31 课图解页面
├── src/                    ← 无依赖的 Python 生成器
│   ├── shell.py            CSS 设计系统 + 双语切换 + 导航
│   ├── part1.py … part8.py 各部分课程内容（中 + 英）
│   ├── quizzes.py          每课自测题（双语 · 确定性洗牌）
│   ├── registry.py         课程 → 内容映射
│   ├── build.py            站点构建
│   ├── build_print.py      PDF 构建（中/英各一份）
│   ├── check_html.py       HTML 结构校验
│   └── check_links.py      内链检查
├── .github/workflows/
│   ├── deploy.yml          自动部署 Pages + PDF + Release
│   └── ci.yml              防回归（HTML 漂移 + 内链检查）
├── README.md · LICENSE
```

## 🛠️ 重新生成 · Rebuild

```bash
cd src
python build.py          # 生成 index.html + lessons/
python build_print.py    # 生成 print.zh.html + print.en.html
python check_html.py     # 结构校验（期望 0 错）
python check_links.py    # 检查内链
```

### 本地导出 PDF · Local PDF Export

```bash
chromium --headless=new --no-pdf-header-footer \
  --print-to-pdf=agent-framework-visual-guide.zh.pdf \
  --virtual-time-budget=20000 "file://$PWD/print.zh.html"
```

## 📄 许可 · License

双许可 Dual-licensed：

- **代码 Code**（`src/` 下的 Python 生成器与校验脚本）— MIT，见 [LICENSE](./LICENSE)
- **内容 Content**（课程文字与图，渲染进 `index.html` / `lessons/*.html` / `print.*.html`）— CC BY 4.0，见 [LICENSE-CONTENT](./LICENSE-CONTENT)

Microsoft Agent Framework 为 Microsoft 的项目（MIT 许可），相关名称与商标归其所有。本教程为独立的第三方、非官方学习材料，不含其源码。
