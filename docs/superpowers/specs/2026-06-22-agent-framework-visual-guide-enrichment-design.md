# Agent Framework Visual Guide — 全面对标 llama-cpp 的完善设计

- **日期**: 2026-06-22
- **状态**: 设计已确认，待转实施计划
- **被讲解源码**: `../agent-framework/`（Python 实现，`python/packages/*`）
- **标杆项目**: `../llama-cpp-visual-guide/`（同作者的成熟图解教程）

---

## 1. 背景与动机

当前 `agent-framework-visual-guide`（下称 **AF-VG**）已有 27 课、纯 Python 无依赖生成静态站点，
架构与 llama-cpp 图解（下称 **LCV**）同构。但与 LCV 对标存在系统性差距：

| 维度 | LCV（标杆） | AF-VG（现状） | 差距 |
|---|---|---|---|
| 课数 / 部分 | 40 课 / 9 部分 | 27 课 / 7 个 part 文件（shell 仅 6 个 Part 标签） | 覆盖较少、结构长歪 |
| 单课深度 | 平均 ~80KB | 平均 ~44KB | **约半深** |
| 自测题 quizzes | ✅ `quizzes.py`（2662 行，每课 MCQ+开放题，确定性洗牌） | ❌ 完全没有 | **缺核心教学件** |
| worked-example 追踪 | ✅ 每课逐步追踪图 | ❌ 基本没有 | 缺 |
| HTML 结构校验 | ✅ `check_html.py` | ❌ 只有 `check_links.py` | 缺工具 |
| README / 元信息 | 准确、有 Part 表、含第三方免责声明 | **过期**（写 "22 课/6 部分"，实为 27/7） | 需修 |
| 许可 | 双许可（代码 MIT + 内容 CC BY 4.0 + `LICENSE-CONTENT`） | 仅 MIT | 可补 |
| 代码卫生 | 干净 | 游离文件 `src/part5.py.backup`、`src/gen_part2.py`、陈旧 `__pycache__`；`registry` 顺序乱、Part 标签错挂 | 需清理 |
| 准确性 | "真实引用的源码" | 历史上出现过伪造 API（有一次提交专门删假 API） | 需审计 |

**核心结论**：主要差距是**深度、自测系统、worked-example、准确性与元信息**，而非广度——
现有 27 课已覆盖 providers / workflows / orchestration / middleware / MCP / A2A / 持久化 / 声明式等主要概念。

---

## 2. 目标与非目标

### 目标
1. 把现有 27 课**分层加深**：核心课（内部原理/工作流/协议）加深到约 2×，入门/番外课适度加深。
2. 新增 **quizzes 自测系统**（移植 LCV 设计），覆盖全部课程。
3. 为核心课补 **worked-example 逐步追踪图**。
4. 新增 **4 门课**，扩到 **31 课 / 8 部分**：记忆后端、DevUI、可观测性深入、术语表/速查。
5. 补 **`check_html.py`** 结构校验工具，清理游离文件，理顺 `registry`/`shell` 的 Part 分组与顺序。
6. 修 **README**（计数、Part 表、第三方免责声明、构建命令）与**许可**（双许可 + `LICENSE-CONTENT`）。
7. **严格准确性**：所有新增代码片段从 `../agent-framework` 真实源码提炼并标注文件路径；顺手审计现有课的代码/路径，修掉错的。

### 非目标
- 不重命名现有 27 课的文件（避免内链 / CI 漂移 / PDF 链接失效）。
- 不引入新的运行时依赖（保持纯 Python 3、零依赖生成）。
- 不覆盖 .NET 实现（教程聚焦 Python，与现状一致）。
- 不做与本目标无关的重构。

---

## 3. 最终结构（31 课 / 8 部分）

现有 27 课文件名不变，新课用文件号 28–31。修正 Part 分组（现状把 L23–27 错挂在 Part 5、L21–22 在 Part 6，且无独立"协议"Part 与"速查"Part）。

| Part | 名称（zh / en） | 课 | 变化 |
|---|---|---|---|
| 1 | 宏观全景 / Big Picture | L01–03 | 适度加深 + 自测 |
| 2 | 用户视角 / User's View | L04–07 | 适度加深 + 自测 |
| 3 | 内部源码 / Internals | L08–14 | **核心 · 2×** + worked-example + 自测 |
| 4 | 进阶实战 / Advanced | L15 + **L29 DevUI** + **L30 可观测性深入** | 加深 + 2 门新课 |
| 5 | 自己动手做 Agent / Build Your Own | L16–20 + **L28 记忆后端** | 加深 + 1 门新课 |
| 6 | 协议与生态 / Protocols & Ecosystem | L23–27 | **新 Part 标签**（原误挂 P5）+ 核心 2× |
| 7 | 番外篇 / Bonus | L21–22 | 适度加深 + 自测 |
| 8 | 速查 / Quick Reference | **L31 术语表** | 全新 |

> TOC 由 `shell.index_page` **按 Part 分组渲染**，故顺序由"每课所属 Part"决定，文件号无需单调（registry 现已是此约定）。
> 新课插入其所属 Part 的连续块：`PAGES` 顺序变为
> `01–14`（P1–P3）→ `15,29,30`（P4）→ `16–20,28`（P5）→ `23–27`（P6 协议）→ `21,22`（P7 番外）→ `31`（P8 速查）。

### 4 门新课内容大纲

- **L28 记忆后端（Memory Backends）** — `python/packages/{redis,mem0,azure-cosmos,core}`：
  `ContextProvider` 抽象、对话/向量记忆、Redis / Mem0 / Cosmos 后端如何接入会话与检索。
- **L29 DevUI（可视化调试）** — `python/packages/devui`：本地 DevUI 如何挂载 Agent/Workflow、
  请求-响应可视化、流式与事件查看、与 `samples` 的联动。
- **L30 可观测性深入（Observability Deep-Dive）** — `python/packages/core` 中 OpenTelemetry 接入：
  trace/span/metric 的产生点、与中间件链的关系（从 L14 抽出做深，L14 转为"流式"为主、留指针指向 L30）。
- **L31 术语表 / 速查（Glossary & Quick Reference）** — 仿 LCV L40：核心术语词条网格 + 概念索引 + 跨课跳转，放最后一课。

---

## 4. 新系统设计

### 4.1 自测系统 `src/quizzes.py`（移植 LCV）

- **数据结构**（每课）：
  ```python
  QUIZZES["NN-file.html"] = {
      "mcq": [
          {"q": {"zh","en"}, "opts": [{"zh","en"}, ...],
           "answer": <0-based 原始序号>, "why": {"zh","en"}},
      ],
      "open": [{"zh","en"}, ...],
  }
  ```
- **确定性洗牌**：用 `hashlib.md5(f"{seed}:{i}")` 对 opts 排序，中英用同一 permutation，
  正确项字母在中英两版一致；构建可重现（同输入同输出）。
- **渲染**：`render(fname, lang) -> str` 产出折叠式 HTML（`<details>` + 选项 + "看答案与解析"）。
  - `build.py`：`content = {l: base[l] + quizzes.render(fname, l) for l in ("zh","en")}`。
  - `build_print.py`：同步追加，使 PDF 也含自测。
- **题目风格**：走"想一想为什么这么设计"路线（契合现有"设计亮点 💡"基调），
  每课 **2–3 道 MCQ + 1–2 道开放题**，覆盖全部 31 课。
- **CSS**：把 LCV 的 quiz 样式移植进 `shell.py` 的设计系统（沿用已有 `<details>/.accordion` 体系，新增 quiz 专属 class）。

### 4.2 worked-example 追踪图（核心课）

- 每门核心课加一段**单一真实场景的逐步追踪**。示例（L08/L10）：追一次 `agent.run()`——
  组装消息 → ChatClient.get_response → 模型要求调工具 → 解析并执行 `@tool` → 回灌结果 → 二次调用 → 最终 `AgentResponse`。
- **复用现有原语** `.vflow` / `.step` / `.num`（AF shell 已有；正是 LCV worked-example 的步骤结构）；
  必要时补 `.sc`（step-content）与多 actor lane 样式。
- 分层：核心课必有；适度层可选轻量版；术语表无。

### 4.3 每课加深配方（分层）

| 层级 | 课 | 配方 |
|---|---|---|
| **核心 2×** | L08–14、L23–27 | 深化"为什么"正文 + 1–2 新图 + 1 段 worked-example + 真实引用源码(标路径) + 2–3 个 4-QA 折叠 + 自测题 |
| **适度** | L01–07、L21–22 | 正文打磨 + 必要 1 图 + 源码核对 + 自测题(2 选 + 1 开放) |
| **全新** | L28–31 | 按核心深度从零写；L31 术语表用词条网格/索引特殊版式 |

每课保留既有四件套：生活类比 🔌、关键要点 ✅、设计亮点 💡、中英一键切换。

---

## 5. 工具与卫生

1. **新增 `src/check_html.py`**：结构校验（标签配平、每课中英双块齐全、无占位符/TODO 残留、必备区块存在），移植自 LCV，期望 0 错 0 警。
2. **清理游离文件**：删除 `src/part5.py.backup`、`src/gen_part2.py`、陈旧 `__pycache__`（确认 `.gitignore` 覆盖 `__pycache__/`）。
3. **修 `shell.py` / `registry.py`**：新增 Part 6「协议与生态」、番外升为 Part 7、新增 Part 8「速查」；Part 标签与 PAGES 分组一致；registry 顺序与 PAGES 对齐。
4. **README**：改为 31 课 / 8 部分；加 Part/主题/课次表（仿 LCV）；加**第三方非官方免责声明**；更新"重新生成"命令（含 `check_html.py`）与项目结构。
5. **许可**：新增 `LICENSE-CONTENT`（CC BY 4.0），README 注明双许可（代码 MIT / 内容 CC BY 4.0），对齐 LCV。
6. **CI（`ci.yml`）**：在既有"HTML 漂移 + 内链检查"基础上，增跑 `check_html.py` 与 quiz 覆盖检查（每页都有 QUIZZES 条目）。

---

## 6. 里程碑（方案 A · 地基优先）

每个里程碑独立可交付、收尾全绿（build 可重现、check_html / check_links 通过）。

| M | 名称 | 交付 | 闸门 |
|---|---|---|---|
| **M0** | 基建与卫生 | `quizzes.py` 框架 + build/build_print 集成 + quiz CSS；`check_html.py`；清理游离文件；修 `registry`/`shell` Part 分组；README + `LICENSE-CONTENT` + 免责声明 | build 重现、check_html/check_links 0 错；此阶段不改课程正文 |
| **M1** | 准确性审计 | 27 课代码片段/文件路径对 `../agent-framework` 真实源码核对纠错 | 每条引用路径在源码中存在；无伪造 API |
| **M2** | 核心内部 L08–11 | agent/client/tool/中间件内部 2× + worked-example + 自测 | 闸门全绿 |
| **M3** | 工作流与编排 L12–14 | workflows/orchestration/streaming 2× + worked-example + 自测 | 闸门全绿 |
| **M4** | 协议与生态 L23–27 | skills/mcp/hosted/a2a-agui/eval 2× + worked-example + 自测；落 Part 6 标签 | 闸门全绿 |
| **M5** | 适度加深 + 全课自测 | L01–07、L15–20、L21–22 适度加深 + 补齐所有剩余课自测 | 全部 27 课均有自测 |
| **M6** | 4 门新课 | L28 记忆后端 / L29 DevUI / L30 可观测性 / L31 术语表，核心深度 + 自测；接入 registry/shell/README | 31 课全绿 |
| **M7** | 收尾 | 重生 print/PDF、README 表 + 徽章、交叉链接、全量校验扫描 | 全量闸门全绿 |

---

## 7. 验证策略

**每里程碑闸门**（在 `src/` 下运行）：
- `python build.py` — 重新生成 `index.html` + `lessons/*.html`，committed HTML 无意外 diff（保持同步）。
- `python build_print.py` — 重新生成 `print.zh.html` + `print.en.html`。
- `python check_html.py` — 结构校验 0 错。
- `python check_links.py` — 全部内链解析。

**准确性**：每个代码片段与文件路径必须真实存在于 `../agent-framework`（M1 审计 + 新内容持续遵守）。
**自测覆盖**：`shell.PAGES` 中每页都有对应 `QUIZZES` 条目（在 `check_html.py` 或 build 中加断言）。

**流程偏好**（遵循既有用户约定）：
- 写测试 / quiz 可委派独立子代理；子代理使用**当前主会话模型**（显式传 `model`）。
- 每个 task 跑**完整 spec 合规 + 代码质量双重审查**子代理（含小改动）。
- 大文件"一点一点 edit"，分步推进，不一次性写完。

---

## 8. 风险与缓解

| 风险 | 缓解 |
|---|---|
| 加深正文/加自测导致 committed HTML 与源不同步（CI 漂移） | 每次改完必跑 `build.py` + `build_print.py` 并提交生成物；CI 守门 |
| 引用源码路径在上游漂移/版本不一致 | 以本地 `../agent-framework` 快照为准并标注；M1 审计统一核对 |
| Part 重新分组影响 PDF/导航锚点 | 仅改 Part 标签与分组映射，不改文件名；改后跑 check_links + 重生 print |
| quizzes 体量大、易与正文风格脱节 | 复用 LCV 成熟 schema 与渲染；题目走"设计取舍"路线，与"设计亮点"一致；可由子代理批量起草后审查 |
| 工程量大 | 严格按 M0→M7 分里程碑，每里程碑独立可交付、可中断 |

---

## 9. 受影响文件一览（预期）

- 新增：`src/quizzes.py`、`src/check_html.py`、`LICENSE-CONTENT`、`lessons/28-*.html`…`lessons/31-*.html`、新课内容模块（如 `src/part8.py` 等，按需）。
- 修改：`src/build.py`、`src/build_print.py`、`src/shell.py`、`src/registry.py`、`src/part1.py`…`src/part7.py`（加深）、`README.md`、`.github/workflows/ci.yml`、`index.html` + 全部 `lessons/*.html`（重生）、`print.zh.html` / `print.en.html`（重生）。
- 删除：`src/part5.py.backup`、`src/gen_part2.py`、陈旧 `__pycache__`。
