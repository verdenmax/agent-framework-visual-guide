"""Content for Part 1 (macro overview): lessons 01-03 — Chinese + English."""

# ---------------------------------------------------------------------------
L01_ZH = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Microsoft Agent Framework（MAF）是一个用 <strong>Python 和 .NET</strong> 编写的<strong>开源框架</strong>，
帮你把"大语言模型（LLM）"接进真实应用，并编排成<strong>能干活的 Agent 和多 Agent 工作流</strong>。
它不替你训练模型，而是负责模型<strong>周边的所有管道</strong>，并面向<strong>生产环境</strong>。
</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把大语言模型想成一台<strong>很强但很孤立的发动机</strong>：它能输出文字，却不知道你的数据库、
  不会自己调用工具，不同厂商的接口还都不一样。MAF 就是那套<strong>标准化的"传动系统 + 仪表盘 + 配件接口"</strong>——
  让你用同一套代码驱动任何品牌的发动机，把它接到工具、记忆、其他 Agent 上，还能在生产里<strong>监控、重启、审批</strong>。
</div>

<h2>它到底解决什么问题？</h2>
<p>直接调用某个厂商的 SDK 当然能跑，但真实应用里你很快会撞上这几类麻烦，正是 MAF 要替你抹平的：</p>

<table class="t">
  <tr><th>痛点</th><th>没有框架时</th><th>MAF 的做法</th></tr>
  <tr><td><strong>厂商锁定</strong></td><td>换模型要重写一大片调用代码</td><td>统一的 <span class="mono">ChatClient</span> + <span class="mono">Agent</span>，换厂商基本只改一行</td></tr>
  <tr><td><strong>对话拼装</strong></td><td>手动拼 role/content 的字典</td><td>结构化的 <span class="mono">Message</span> / <span class="mono">Role</span> / <span class="mono">Content</span></td></tr>
  <tr><td><strong>调用工具</strong></td><td>自己解析模型要调哪个函数、传什么参</td><td><span class="mono">@tool</span> 自动生成 schema + 解析 + 执行</td></tr>
  <tr><td><strong>多步 / 多 Agent</strong></td><td>手写"想—做—再想"循环和协作逻辑</td><td><strong>Agent 循环</strong> + 图式 <strong>Workflows</strong> 编排</td></tr>
  <tr><td><strong>上生产</strong></td><td>自己搞监控、持久化、人工审批</td><td>内置 <strong>OpenTelemetry</strong>、检查点、人在环、托管</td></tr>
</table>

<h2>最小的一个 Agent 长什么样</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">samples/01-get-started/01_hello_agent.py</span><span class="ln">最小示例</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
<span class="kw">from</span> agent_framework.foundry <span class="kw">import</span> FoundryChatClient
<span class="kw">from</span> azure.identity <span class="kw">import</span> AzureCliCredential

client = FoundryChatClient(
    project_endpoint=<span class="st">"https://your-project.services.ai.azure.com"</span>,
    model=<span class="st">"gpt-4o"</span>, credential=AzureCliCredential(),
)
agent = Agent(
    client=client, name=<span class="st">"HelloAgent"</span>,
    instructions=<span class="st">"You are a friendly assistant. Keep your answers brief."</span>,
)

result = <span class="kw">await</span> agent.run(<span class="st">"What is the capital of France?"</span>)
<span class="fn">print</span>(result)</pre>
</div>
<p>三步：<strong>选一个 ChatClient</strong>（连到某个模型）→ <strong>包成一个 Agent</strong>（给名字和系统指令）→ <strong>run 一句话</strong>。
换厂商？把 <span class="inline">FoundryChatClient</span> 换成 <span class="inline">OpenAIChatClient</span> 即可，其余不动。</p>

<h2>核心心智模型</h2>
<div class="flow">
  <div class="node"><div class="nt">你的代码</div><div class="nd">输入 + 指令</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Agent</div><div class="nd">组装消息 / 循环</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">ChatClient</div><div class="nd">厂商无关</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">LLM</div><div class="nd">+ 工具 / 记忆</div></div>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> 它和 LangChain / AutoGen / Semantic Kernel 什么关系？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">❓ 一句话定位</div>
      <div class="a">MAF 是微软把 <strong>Semantic Kernel</strong>（企业级、强类型、连接器丰富）和
        <strong>AutoGen</strong>（多 Agent 对话与研究探索）<strong>合并演进</strong>而来的统一框架，
        目标是"<strong>从原型到生产</strong>"一条路走到底，且 <strong>Python 与 .NET 双实现、API 对齐</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 它的取舍</div>
      <div class="a">既要 LangGraph 那样的<strong>图式编排</strong>（可控、可恢复），又要 AutoGen 那样的<strong>多 Agent 协作</strong>，
        还把<strong>可观测性 / 持久化 / 审批</strong>做成一等公民——这就是"生产级"的含义。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>MAF = <strong>ChatClient（连模型）+ Agent（循环）+ Tools（工具）+ Workflows（编排）+ 生产能力</strong>。</li>
    <li>它<strong>不训练模型</strong>，负责模型周边的全部管道；<strong>Python 和 .NET</strong> 双实现。</li>
    <li>定位：<strong>Semantic Kernel + AutoGen 的统一继任者</strong>，从原型直达生产。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  把"换模型只改一行"做成默认体验：<strong>ChatClient 是厂商无关的统一抽象</strong>，
  Agent / 工具 / 工作流全部构建在它之上，于是<strong>可移植性</strong>从第一行代码就免费获得。
</div>
"""

L01_EN = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Microsoft Agent Framework (MAF) is an <strong>open-source framework</strong> written in
<strong>Python and .NET</strong> that connects large language models (LLMs) to real apps and
orchestrates them into <strong>useful agents and multi-agent workflows</strong>. It does not train
models — it owns all the <strong>plumbing around</strong> the model, and it is built for <strong>production</strong>.
</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Think of an LLM as a <strong>powerful but isolated engine</strong>: it emits text, but knows nothing
  about your database, can't call tools by itself, and every vendor's interface is different. MAF is the
  <strong>standardized "drivetrain + dashboard + connector kit"</strong> — drive any engine with one codebase,
  wire it to tools, memory and other agents, and <strong>monitor, restart and gate</strong> it in production.
</div>

<h2>What does it actually solve?</h2>
<p>Calling a vendor SDK directly works, but real apps hit these pain points fast — exactly what MAF smooths over:</p>

<table class="t">
  <tr><th>Pain</th><th>Without a framework</th><th>What MAF does</th></tr>
  <tr><td><strong>Vendor lock-in</strong></td><td>Switching models rewrites a lot of code</td><td>One <span class="mono">ChatClient</span> + <span class="mono">Agent</span>; switching vendors is ~one line</td></tr>
  <tr><td><strong>Assembling chat</strong></td><td>Hand-build role/content dicts</td><td>Structured <span class="mono">Message</span> / <span class="mono">Role</span> / <span class="mono">Content</span></td></tr>
  <tr><td><strong>Calling tools</strong></td><td>Parse which function & args yourself</td><td><span class="mono">@tool</span> auto-generates schema + parses + executes</td></tr>
  <tr><td><strong>Multi-step / multi-agent</strong></td><td>Hand-write the think–act loop & coordination</td><td><strong>Agent loop</strong> + graph-based <strong>Workflows</strong></td></tr>
  <tr><td><strong>Going to production</strong></td><td>Roll your own tracing, persistence, approvals</td><td>Built-in <strong>OpenTelemetry</strong>, checkpoints, human-in-the-loop, hosting</td></tr>
</table>

<h2>What the smallest agent looks like</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">samples/01-get-started/01_hello_agent.py</span><span class="ln">minimal</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
<span class="kw">from</span> agent_framework.foundry <span class="kw">import</span> FoundryChatClient
<span class="kw">from</span> azure.identity <span class="kw">import</span> AzureCliCredential

client = FoundryChatClient(
    project_endpoint=<span class="st">"https://your-project.services.ai.azure.com"</span>,
    model=<span class="st">"gpt-4o"</span>, credential=AzureCliCredential(),
)
agent = Agent(
    client=client, name=<span class="st">"HelloAgent"</span>,
    instructions=<span class="st">"You are a friendly assistant. Keep your answers brief."</span>,
)

result = <span class="kw">await</span> agent.run(<span class="st">"What is the capital of France?"</span>)
<span class="fn">print</span>(result)</pre>
</div>
<p>Three steps: <strong>pick a ChatClient</strong> (connect to a model) → <strong>wrap it in an Agent</strong>
(name + system instructions) → <strong>run a prompt</strong>. Switch vendors by replacing
<span class="inline">FoundryChatClient</span> with <span class="inline">OpenAIChatClient</span> — nothing else changes.</p>

<h2>The core mental model</h2>
<div class="flow">
  <div class="node"><div class="nt">Your code</div><div class="nd">input + instructions</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Agent</div><div class="nd">assemble / loop</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">ChatClient</div><div class="nd">vendor-agnostic</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">LLM</div><div class="nd">+ tools / memory</div></div>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> How does it relate to LangChain / AutoGen / Semantic Kernel? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">❓ One-line positioning</div>
      <div class="a">MAF is Microsoft's <strong>convergence</strong> of <strong>Semantic Kernel</strong>
        (enterprise, strongly typed, rich connectors) and <strong>AutoGen</strong> (multi-agent
        conversations & research), into one framework aimed at <strong>prototype-to-production</strong>,
        with <strong>aligned Python and .NET</strong> implementations.</div>
    </div>
    <div class="qa">
      <div class="q">✅ Its trade-offs</div>
      <div class="a">It wants both LangGraph-style <strong>graph orchestration</strong> (controllable, resumable)
        and AutoGen-style <strong>multi-agent collaboration</strong>, while making
        <strong>observability / persistence / approvals</strong> first-class — that's what "production-grade" means.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>MAF = <strong>ChatClient (model) + Agent (loop) + Tools + Workflows + production features</strong>.</li>
    <li>It <strong>does not train models</strong>; it owns the plumbing. <strong>Python and .NET</strong> both.</li>
    <li>Positioning: the <strong>unified successor to Semantic Kernel + AutoGen</strong>, prototype to production.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  "Switch models with one line" is the default: the <strong>ChatClient is a vendor-agnostic abstraction</strong>,
  and agents / tools / workflows are all built on top — so <strong>portability</strong> is free from line one.
</div>
"""

# ---------------------------------------------------------------------------
L02_ZH = r"""
<p class="lead">MAF 是一个 <strong>monorepo</strong>：一个仓库里同时放着 <strong>Python</strong> 和 <strong>.NET</strong>
两套实现，外加文档、声明式 Agent 和 schema。理解了目录结构，你就有了一张<strong>源码导航地图</strong>。</p>

<div class="card analogy">
  <div class="tag">🏢 生活类比</div>
  把仓库想成一座<strong>办公楼</strong>：<strong>core</strong> 是地基与承重墙（所有人都依赖），
  各 <strong>provider 包</strong>是不同楼层的部门（OpenAI 部、Anthropic 部……），
  <strong>lab</strong> 是顶楼的实验室（前沿但不稳定）。Python 楼和 .NET 楼并排而立，<strong>户型一致</strong>。
</div>

<h2>顶层结构</h2>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">PY/.NET</span><span class="name">python/ · dotnet/</span></div>
    <div class="ld">两套实现并列，API 对齐。本教程聚焦 <span class="mono">python/</span>。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">DOCS</span><span class="name">docs/ · declarative-agents/ · schemas/</span></div>
    <div class="ld">设计决策记录（ADR）、声明式 YAML Agent、JSON schema。</div></div>
</div>

<h2>Python 这边怎么分层</h2>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">CORE</span><span class="name">packages/core → agent_framework</span></div>
    <div class="ld">核心抽象：<span class="mono">Agent</span> / <span class="mono">Message</span> / <span class="mono">tool</span> /
      中间件 / <span class="mono">Workflows</span>，以及内置 OpenAI / Azure OpenAI 支持。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">PROVIDERS</span><span class="name">packages/{foundry, anthropic, ollama, …}</span></div>
    <div class="ld">各厂商 / 集成包，在 core 之上扩展具体的 ChatClient 与连接器。</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">LAB</span><span class="name">packages/lab</span></div>
    <div class="ld">实验性功能：基准测试、强化学习、研究项目。</div></div>
</div>

<table class="t">
  <tr><th>你想找</th><th>去哪里</th></tr>
  <tr><td>核心类型与 Agent 实现</td><td class="mono">python/packages/core/agent_framework/</td></tr>
  <tr><td>公共 API（<span class="mono">__all__</span>）</td><td class="mono">core/agent_framework/__init__.py</td></tr>
  <tr><td>新手样例</td><td class="mono">python/samples/01-get-started/</td></tr>
  <tr><td>.NET 对照实现</td><td class="mono">dotnet/src/Microsoft.Agents.AI*/</td></tr>
</table>

<div class="card detail">
  <div class="tag">🔬 细节 · 懒加载</div>
  provider 子模块（如 <span class="inline">agent_framework.azure</span>）用 <span class="inline">__getattr__</span>
  做<strong>懒加载</strong>：只有真正 import 时才拉起对应依赖，让 core 保持轻量。
</div>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>一个仓库、两套对齐实现：<span class="mono">python/</span> 与 <span class="mono">dotnet/</span>。</li>
    <li>Python：<strong>core 是地基</strong>，provider 包按需扩展，lab 装前沿。</li>
    <li>读源码先看 <span class="mono">core/agent_framework/__init__.py</span> 的 <span class="mono">__all__</span>。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>core 不依赖任何具体厂商</strong>：厂商代码全部下沉到独立 provider 包，
  通过懒加载接入。于是核心 API 稳定，新增厂商不动地基。
</div>
"""

L02_EN = r"""
<p class="lead">MAF is a <strong>monorepo</strong>: one repository holds both the <strong>Python</strong> and
<strong>.NET</strong> implementations, plus docs, declarative agents and schemas. Learn the layout and you
have a <strong>source-navigation map</strong>.</p>

<div class="card analogy">
  <div class="tag">🏢 Analogy</div>
  Picture the repo as an <strong>office building</strong>: <strong>core</strong> is the foundation and
  load-bearing walls (everyone depends on it), each <strong>provider package</strong> is a department on a
  floor (OpenAI, Anthropic…), and <strong>lab</strong> is the rooftop R&amp;D lab (cutting-edge, unstable).
  The Python tower and the .NET tower stand side by side with the <strong>same floor plan</strong>.
</div>

<h2>Top-level structure</h2>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">PY/.NET</span><span class="name">python/ · dotnet/</span></div>
    <div class="ld">Two aligned implementations. This guide focuses on <span class="mono">python/</span>.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">DOCS</span><span class="name">docs/ · declarative-agents/ · schemas/</span></div>
    <div class="ld">Architecture decision records (ADRs), declarative YAML agents, JSON schemas.</div></div>
</div>

<h2>How the Python side is layered</h2>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">CORE</span><span class="name">packages/core → agent_framework</span></div>
    <div class="ld">Core abstractions: <span class="mono">Agent</span> / <span class="mono">Message</span> / <span class="mono">tool</span> /
      middleware / <span class="mono">Workflows</span>, plus built-in OpenAI / Azure OpenAI support.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">PROVIDERS</span><span class="name">packages/{foundry, anthropic, ollama, …}</span></div>
    <div class="ld">Vendor / integration packages that extend core with concrete ChatClients & connectors.</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">LAB</span><span class="name">packages/lab</span></div>
    <div class="ld">Experimental features: benchmarking, reinforcement learning, research.</div></div>
</div>

<table class="t">
  <tr><th>Looking for</th><th>Go to</th></tr>
  <tr><td>Core types & Agent impl</td><td class="mono">python/packages/core/agent_framework/</td></tr>
  <tr><td>Public API (<span class="mono">__all__</span>)</td><td class="mono">core/agent_framework/__init__.py</td></tr>
  <tr><td>Beginner samples</td><td class="mono">python/samples/01-get-started/</td></tr>
  <tr><td>.NET counterpart</td><td class="mono">dotnet/src/Microsoft.Agents.AI*/</td></tr>
</table>

<div class="card detail">
  <div class="tag">🔬 Detail · lazy loading</div>
  Provider submodules (e.g. <span class="inline">agent_framework.azure</span>) use <span class="inline">__getattr__</span>
  for <strong>lazy loading</strong>: dependencies are pulled only on actual import, keeping core lightweight.
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>One repo, two aligned implementations: <span class="mono">python/</span> and <span class="mono">dotnet/</span>.</li>
    <li>Python: <strong>core is the foundation</strong>, provider packages extend on demand, lab holds the frontier.</li>
    <li>To read the source, start at <span class="mono">core/agent_framework/__init__.py</span>'s <span class="mono">__all__</span>.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>core depends on no specific vendor</strong>: vendor code lives in separate provider packages and is
  wired in via lazy loading. The core API stays stable; adding a vendor never touches the foundation.
</div>
"""

# ---------------------------------------------------------------------------
L03_ZH = r"""
<p class="lead">你写的只是 <span class="inline">await agent.run("…")</span> 一行，但底下发生了一串事。
看懂这条<strong>生命周期</strong>，后面所有"内部源码"课都会变得轻松。</p>

<div class="card analogy">
  <div class="tag">🍽️ 生活类比</div>
  Agent 像一位<strong>餐厅服务员</strong>：你点单（输入）→ 他把你的话连同"店规"（instructions）整理成<strong>标准工单</strong>（消息）
  → 递进后厨（ChatClient → LLM）→ 如果厨师说"需要先去仓库取货"（工具调用），服务员就去取（执行工具）再把结果回递
  → 直到厨师出菜（最终回答），服务员端给你（<span class="mono">AgentResponse</span>）。
</div>

<h2>一次 run 的完整数据流</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>你的输入</h4>
    <p>字符串或一组 <span class="mono">Message</span>，连同会话历史一起进来。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Agent 组装</h4>
    <p>把 <span class="mono">instructions</span>（系统提示）+ 历史 + 新输入 + 可用 <span class="mono">tools</span> 拼成一次请求。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>ChatClient 调用</h4>
    <p>厂商无关接口把请求发给具体 LLM（Foundry / OpenAI / …），拿回 <span class="mono">ChatResponse</span>。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>要调工具吗？</h4>
    <p>若响应里含 <span class="mono">function_call</span>，Agent <strong>执行对应函数</strong>，把
      <span class="mono">function_result</span> 追加进消息，<strong>再回到第 3 步</strong>。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>收敛与返回</h4>
    <p>当模型不再要工具，循环结束，得到 <span class="mono">AgentResponse</span>（流式则是一串 <span class="mono">AgentResponseUpdate</span>）。</p></div></div>
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  这就是经典的 <strong>Agent 循环（think → act → observe）</strong>：模型"想"，框架替它"做"（调工具），
  把"观察"喂回去，直到任务完成。你只调用一次 <span class="inline">run()</span>，循环在内部自动跑完。
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> 多轮对话时历史从哪来？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">把同一个 <strong>会话（session）</strong>传给连续的 run，历史会自动累积：
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
agent = Agent(client=client, instructions=<span class="st">"…"</span>)
session = agent.get_new_session()
<span class="kw">await</span> agent.run(<span class="st">"我叫小明"</span>, session=session)
<span class="kw">await</span> agent.run(<span class="st">"我叫什么？"</span>, session=session)  <span class="cm"># 记得"小明"</span></pre>
        <em>（会话与记忆见第 07 课，这里只需知道历史是"会话"携带的。）</em></div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>一次 <span class="mono">run()</span> = 组装消息 → 调 LLM →（按需循环调工具）→ 返回 <span class="mono">AgentResponse</span>。</li>
    <li>工具调用是<strong>循环</strong>，不是一次性：模型可以多次要工具。</li>
    <li>流式版本逐块返回 <span class="mono">AgentResponseUpdate</span>，最终拼成完整响应。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>循环被封装在框架里</strong>：调用方只看到"输入→输出"，而"想—做—再想"的复杂度被 Agent 吸收，
  这正是它比裸调 LLM SDK 省心的根源。
</div>
"""

L03_EN = r"""
<p class="lead">You write just one line — <span class="inline">await agent.run("…")</span> — but a chain of events
happens underneath. Understand this <strong>lifecycle</strong> and every later "internals" lesson gets easy.</p>

<div class="card analogy">
  <div class="tag">🍽️ Analogy</div>
  An Agent is like a <strong>waiter</strong>: you order (input) → they combine your words with the "house rules"
  (instructions) into a <strong>standard ticket</strong> (messages) → hand it to the kitchen (ChatClient → LLM)
  → if the chef says "fetch an ingredient first" (tool call), the waiter fetches it (executes the tool) and
  brings the result back → until the dish is ready (final answer), served to you (<span class="mono">AgentResponse</span>).
</div>

<h2>The full data flow of one run</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Your input</h4>
    <p>A string or a list of <span class="mono">Message</span>, arriving together with conversation history.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Agent assembles</h4>
    <p>Combine <span class="mono">instructions</span> (system prompt) + history + new input + available <span class="mono">tools</span> into one request.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>ChatClient call</h4>
    <p>The vendor-agnostic interface sends it to a concrete LLM (Foundry / OpenAI / …) and returns a <span class="mono">ChatResponse</span>.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Need a tool?</h4>
    <p>If the response contains a <span class="mono">function_call</span>, the Agent <strong>executes the function</strong>,
      appends the <span class="mono">function_result</span> to the messages, and <strong>loops back to step 3</strong>.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Converge & return</h4>
    <p>When the model stops asking for tools, the loop ends with an <span class="mono">AgentResponse</span>
      (or a stream of <span class="mono">AgentResponseUpdate</span> when streaming).</p></div></div>
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  This is the classic <strong>agent loop (think → act → observe)</strong>: the model "thinks", the framework
  "acts" for it (runs tools), feeds the "observation" back, until done. You call <span class="inline">run()</span>
  once; the loop runs to completion internally.
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> In multi-turn chat, where does history come from? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Pass the same <strong>session</strong> across runs and history accumulates automatically:
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
agent = Agent(client=client, instructions=<span class="st">"…"</span>)
session = agent.get_new_session()
<span class="kw">await</span> agent.run(<span class="st">"My name is Sam"</span>, session=session)
<span class="kw">await</span> agent.run(<span class="st">"What's my name?"</span>, session=session)  <span class="cm"># remembers "Sam"</span></pre>
        <em>(Sessions & memory are Lesson 07; here just note history rides on the "session".)</em></div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>One <span class="mono">run()</span> = assemble messages → call LLM → (loop tools as needed) → return <span class="mono">AgentResponse</span>.</li>
    <li>Tool calling is a <strong>loop</strong>, not one-shot: the model may request tools multiple times.</li>
    <li>The streaming variant yields <span class="mono">AgentResponseUpdate</span> chunks that compose the full response.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>The loop is encapsulated in the framework</strong>: callers see only "input → output", while the
  think–act–think complexity is absorbed by the Agent — that's why it's calmer than raw LLM SDK calls.
</div>
"""
