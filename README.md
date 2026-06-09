# Agent Framework 图解教程 · Visual Guide

[![📖 在线阅读](https://img.shields.io/badge/%F0%9F%93%96%20%E5%9C%A8%E7%BA%BF%E9%98%85%E8%AF%BB-Read%20Online-0078d4?style=for-the-badge)](https://verdenmax.github.io/agent-framework-visual-guide/)
[![📄 中文 PDF](https://img.shields.io/badge/%F0%9F%93%84%20%E4%B8%AD%E6%96%87%20PDF-Download-b4690e?style=for-the-badge)](https://github.com/verdenmax/agent-framework-visual-guide/releases/latest/download/agent-framework-visual-guide.zh.pdf)
[![📄 English PDF](https://img.shields.io/badge/%F0%9F%93%84%20English%20PDF-Download-b4690e?style=for-the-badge)](https://github.com/verdenmax/agent-framework-visual-guide/releases/latest/download/agent-framework-visual-guide.en.pdf)

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Lessons](https://img.shields.io/badge/lessons-22-blue.svg)
![Parts](https://img.shields.io/badge/parts-6-9cf.svg)
![Built with](https://img.shields.io/badge/built%20with-Python%203-3776AB.svg?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)
![Language](https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87%20%2F%20EN-orange.svg)

一套面向**完全新手**的中英双语可视化（HTML 图解）教程，带你从零开始理解
[Microsoft Agent Framework](https://github.com/microsoft/agent-framework)（Python 实现）。

A bilingual (中/EN) visual tutorial for complete beginners, helping you understand
[Microsoft Agent Framework](https://github.com/microsoft/agent-framework) (Python) from scratch.

**一键切换语言** · 每页顶栏有 `中 / EN` 切换按钮，无需刷新。

## 📚 教程结构 · Tutorial Structure

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

### 第五部分 · 自己动手做 Agent | Part 5 · Build Your Own
16. **接入各家模型** — Foundry / AzureOpenAI / OpenAI / Anthropic / Ollama
17. **声明式 Agent（YAML）** — YAML 定义 Agent
18. **写自己的中间件** — 自定义 Agent / Function middleware
19. **检查点 · 人在环 · 持久化** — checkpoint · HITL · DurableTask
20. **端到端实战：多 Agent 工作流** — 把所有零件拼成一个工作流

### 第六部分 · 番外篇 | Part 6 · Bonus
21. **横向对比：AF vs 其他框架** — AF vs LangGraph / AutoGen / SK
22. **全栈坐标系 & 学习地图** — 编排流派 · 全栈分层 · 你在哪

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
├── lessons/                ← 22 课图解页面
├── src/                    ← 无依赖的 Python 生成器
│   ├── shell.py            CSS 设计系统 + 双语切换 + 导航
│   ├── part1.py … part6.py 各部分课程内容（中 + 英）
│   ├── registry.py         课程 → 内容映射
│   ├── build.py            站点构建
│   ├── build_print.py      PDF 构建（中/英各一份）
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
python check_links.py    # 检查内链
```

### 本地导出 PDF · Local PDF Export

```bash
chromium --headless=new --no-pdf-header-footer \
  --print-to-pdf=agent-framework-visual-guide.zh.pdf \
  --virtual-time-budget=20000 "file://$PWD/print.zh.html"
```

## 📄 许可 · License

[MIT License](./LICENSE)

Microsoft Agent Framework 为 Microsoft 的项目，相关名称与商标归其所有。本教程为独立的第三方学习材料。
