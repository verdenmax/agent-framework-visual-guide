"""Content for Part 5 (build your own): lessons 16-20 — Chinese + English."""

# ---------------------------------------------------------------------------
L16_ZH = r"""
<p class="lead">MAF 的 ChatClient 是厂商无关的——但你总要选一个具体厂商来<strong>接入模型</strong>。
本课过一遍主要 provider 包，教你<strong>怎么从"import 到 run"走完全程</strong>。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  ChatClient 像<strong>万能插座</strong>；每个 provider 包是<strong>某国插头</strong>——
  你选 Foundry、OpenAI 还是 Anthropic 的插头，接上万能插座就能充电。
</div>

<h2>主要 Provider</h2>
<table class="t">
  <tr><th>Provider</th><th>包名</th><th>ChatClient 类</th></tr>
  <tr><td>Azure AI Foundry</td><td class="mono">agent-framework-foundry</td><td class="mono">FoundryChatClient</td></tr>
  <tr><td>OpenAI / Azure OpenAI</td><td class="mono">agent-framework（内置）</td><td class="mono">OpenAIChatClient</td></tr>
  <tr><td>Anthropic Claude</td><td class="mono">agent-framework-anthropic</td><td class="mono">AnthropicChatClient</td></tr>
  <tr><td>Ollama（本地）</td><td class="mono">agent-framework-ollama</td><td class="mono">OllamaChatClient</td></tr>
  <tr><td>AWS Bedrock</td><td class="mono">agent-framework-bedrock</td><td class="mono">BedrockChatClient</td></tr>
</table>
<p>全部用法一样：实例化 ChatClient → <span class="mono">client.as_agent(…)</span> → <span class="mono">agent.run(…)</span>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Foundry vs OpenAI 有什么区别？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 关键差异</div>
      <div class="a"><span class="mono">FoundryChatClient</span> 走 <strong>Azure AI Foundry 项目端点</strong>（统一管理模型、记忆、文件等）。
        <span class="mono">OpenAIChatClient</span> 直连 <strong>OpenAI API 或 Azure OpenAI 端点</strong>。
        如果你已有 Foundry 项目，推荐 Foundry；否则 OpenAI 最直接。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>每个厂商一个 provider 包，提供一个 ChatClient 子类。</li>
    <li>统一用法：实例化 → <span class="mono">as_agent()</span> → <span class="mono">run()</span>。</li>
    <li>切换厂商只改 import 和实例化那两行。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>新增厂商不碰核心</strong>：provider 是独立包，通过懒加载接入。
  社区可以自己做新 provider 而不需要 fork 仓库。
</div>
"""

L16_EN = r"""
<p class="lead">MAF's ChatClient is vendor-agnostic — but you pick a concrete vendor to <strong>connect a model</strong>.
This lesson surveys the main provider packages and shows the <strong>import-to-run path</strong>.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  ChatClient is a <strong>universal socket</strong>; each provider package is a <strong>country-specific plug</strong> —
  pick the Foundry, OpenAI or Anthropic plug, snap it into the socket, and you're charging.
</div>

<h2>Key Providers</h2>
<table class="t">
  <tr><th>Provider</th><th>Package</th><th>ChatClient class</th></tr>
  <tr><td>Azure AI Foundry</td><td class="mono">agent-framework-foundry</td><td class="mono">FoundryChatClient</td></tr>
  <tr><td>OpenAI / Azure OpenAI</td><td class="mono">agent-framework (built-in)</td><td class="mono">OpenAIChatClient</td></tr>
  <tr><td>Anthropic Claude</td><td class="mono">agent-framework-anthropic</td><td class="mono">AnthropicChatClient</td></tr>
  <tr><td>Ollama (local)</td><td class="mono">agent-framework-ollama</td><td class="mono">OllamaChatClient</td></tr>
  <tr><td>AWS Bedrock</td><td class="mono">agent-framework-bedrock</td><td class="mono">BedrockChatClient</td></tr>
</table>
<p>Same pattern for all: instantiate ChatClient → <span class="mono">client.as_agent(…)</span> → <span class="mono">agent.run(…)</span>.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Foundry vs OpenAI? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 Key difference</div>
      <div class="a"><span class="mono">FoundryChatClient</span> uses an <strong>Azure AI Foundry project endpoint</strong>
        (unified model, memory, file management). <span class="mono">OpenAIChatClient</span> connects directly to the
        <strong>OpenAI API or Azure OpenAI endpoint</strong>. If you have a Foundry project, use Foundry; otherwise OpenAI is simplest.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>One provider package per vendor, each supplying a ChatClient subclass.</li>
    <li>Unified pattern: instantiate → <span class="mono">as_agent()</span> → <span class="mono">run()</span>.</li>
    <li>Switching vendors changes only the import and instantiation lines.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Adding a vendor never touches core</strong>: providers are separate packages, wired in via lazy loading.
  The community can build new providers without forking the repo.
</div>
"""

# ---------------------------------------------------------------------------
L17_ZH = r"""
<p class="lead">不想写代码？用 <strong>YAML</strong> 定义一个 Agent——名字、指令、工具、模型全写在配置文件里。</p>

<div class="card analogy">
  <div class="tag">📝 生活类比</div>
  声明式 Agent 像<strong>简历</strong>：你把名字、技能、工作经验写好，HR（框架）照着简历帮你入职上岗。
</div>

<h2>一个 YAML 示例</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">my_agent.yaml</span></div>
<pre>name: WeatherBot
instructions: You help with weather queries.
model: gpt-4o
tools:
  - get_weather</pre>
</div>
<p>框架的 <span class="mono">declarative</span> 包读这个 YAML，自动构造出 <span class="mono">Agent</span> 实例。
适合快速原型和版本控制。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 声明式能做到和代码一样吗？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 能力边界</div>
      <div class="a">简单 Agent（名字 + 指令 + 工具列表）完全可以；复杂的自定义中间件或动态逻辑仍需代码。
        声明式和代码式可以<strong>混用</strong>——YAML 定义骨架，代码补充高级逻辑。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>YAML 定义 Agent：<span class="mono">name</span> / <span class="mono">instructions</span> / <span class="mono">model</span> / <span class="mono">tools</span>。</li>
    <li>用 <span class="mono">declarative</span> 包加载，自动构造 <span class="mono">Agent</span>。</li>
    <li>适合快速原型、版本控制、非开发者协作。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>"配置即 Agent"</strong>：改 YAML 就能调整行为，不用改代码、不用重编译。
  这降低了非开发者参与 Agent 设计的门槛。
</div>
"""

L17_EN = r"""
<p class="lead">Don't want to write code? Define an Agent in <strong>YAML</strong> — name, instructions, tools
and model all in a config file.</p>

<div class="card analogy">
  <div class="tag">📝 Analogy</div>
  A declarative Agent is like a <strong>résumé</strong>: you list name, skills and experience; HR (the framework)
  reads it and onboards the person.
</div>

<h2>A YAML example</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">my_agent.yaml</span></div>
<pre>name: WeatherBot
instructions: You help with weather queries.
model: gpt-4o
tools:
  - get_weather</pre>
</div>
<p>The <span class="mono">declarative</span> package reads this YAML and auto-constructs an <span class="mono">Agent</span>.
Great for rapid prototyping and version control.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Can declarative do everything code can? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 Capability boundary</div>
      <div class="a">Simple agents (name + instructions + tool list) — absolutely. Complex custom middleware or dynamic
        logic still needs code. Declarative and code <strong>can be mixed</strong> — YAML defines the skeleton,
        code adds advanced logic.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>YAML defines an Agent: <span class="mono">name</span> / <span class="mono">instructions</span> / <span class="mono">model</span> / <span class="mono">tools</span>.</li>
    <li>Loaded by the <span class="mono">declarative</span> package; auto-constructs <span class="mono">Agent</span>.</li>
    <li>Good for prototyping, version control, non-developer collaboration.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>"Config is an Agent"</strong>: tweak YAML to change behavior, no code changes, no recompilation.
  This lowers the barrier for non-developers to participate in Agent design.
</div>
"""

# ---------------------------------------------------------------------------
L18_ZH = r"""
<p class="lead">第 11 课讲了中间件<em>是什么</em>；本课教你<strong>写一个自己的</strong>——从零到能用。</p>

<h2>实战：重试中间件</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">自定义 ChatMiddleware</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> ChatMiddleware, ChatContext

<span class="kw">class</span> <span class="fn">RetryChatMiddleware</span>(ChatMiddleware):
    <span class="kw">def</span> <span class="fn">__init__</span>(self, max_retries: int = <span class="nb">3</span>):
        self.max_retries = max_retries

    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        <span class="kw">for</span> attempt <span class="kw">in</span> <span class="fn">range</span>(self.max_retries):
            <span class="kw">try</span>:
                <span class="kw">await</span> call_next()
                <span class="kw">return</span>
            <span class="kw">except</span> Exception:
                <span class="kw">if</span> attempt == self.max_retries - <span class="nb">1</span>:
                    <span class="kw">raise</span></pre>
</div>
<p>挂到 Agent 上：<span class="inline">Agent(client=client, chat_middleware=[RetryChatMiddleware(3)])</span>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 三层中间件分别怎么挂？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 挂载方式</div>
      <div class="a"><span class="mono">Agent(middleware=[…])</span> 挂 AgentMiddleware；
        <span class="mono">Agent(chat_middleware=[…])</span> 挂 ChatMiddleware；
        <span class="mono">Agent(function_middleware=[…])</span> 挂 FunctionMiddleware。
        多个中间件按列表顺序从外到内排列。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>继承 <span class="mono">*Middleware</span>，实现 <span class="mono">process(self, context, call_next)</span>。</li>
    <li><span class="mono">await call_next()</span> 无参；结果在 <span class="mono">context.result</span>。</li>
    <li>用 <span class="mono">Agent(middleware=…, chat_middleware=…, function_middleware=…)</span> 挂载。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  中间件是<strong>组合式的</strong>：重试、日志、审批各自独立实现，按需拼装，互不干扰。
</div>
"""

L18_EN = r"""
<p class="lead">Lesson 11 explained what middleware <em>is</em>; this lesson teaches you to
<strong>write your own</strong> — from scratch to working.</p>

<h2>Hands-on: retry middleware</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">custom ChatMiddleware</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> ChatMiddleware, ChatContext

<span class="kw">class</span> <span class="fn">RetryChatMiddleware</span>(ChatMiddleware):
    <span class="kw">def</span> <span class="fn">__init__</span>(self, max_retries: int = <span class="nb">3</span>):
        self.max_retries = max_retries

    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        <span class="kw">for</span> attempt <span class="kw">in</span> <span class="fn">range</span>(self.max_retries):
            <span class="kw">try</span>:
                <span class="kw">await</span> call_next()
                <span class="kw">return</span>
            <span class="kw">except</span> Exception:
                <span class="kw">if</span> attempt == self.max_retries - <span class="nb">1</span>:
                    <span class="kw">raise</span></pre>
</div>
<p>Attach to an Agent: <span class="inline">Agent(client=client, chat_middleware=[RetryChatMiddleware(3)])</span>.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> How to attach each layer? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Attachment</div>
      <div class="a"><span class="mono">Agent(middleware=[…])</span> for AgentMiddleware;
        <span class="mono">Agent(chat_middleware=[…])</span> for ChatMiddleware;
        <span class="mono">Agent(function_middleware=[…])</span> for FunctionMiddleware.
        Multiple middlewares are ordered outside-in by list position.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Subclass <span class="mono">*Middleware</span>; implement <span class="mono">process(self, context, call_next)</span>.</li>
    <li><span class="mono">await call_next()</span> takes no args; result is on <span class="mono">context.result</span>.</li>
    <li>Attach via <span class="mono">Agent(middleware=…, chat_middleware=…, function_middleware=…)</span>.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  Middleware is <strong>compositional</strong>: retries, logging, approvals — each implemented independently,
  assembled as needed, no interference.
</div>
"""

# ---------------------------------------------------------------------------
L19_ZH = r"""
<p class="lead">生产环境需要：<strong>跑到一半能存盘</strong>（检查点）、<strong>关键操作人工审批</strong>（人在环）、
<strong>挂了能续跑</strong>（持久化）。MAF 把这三件事做成一等公民。</p>

<div class="card analogy">
  <div class="tag">💾 生活类比</div>
  检查点像<strong>游戏存档</strong>：进度存下来，挂了从存档恢复。
  人在环像<strong>审批流</strong>：到关键节点暂停，等人签字再继续。
  DurableTask 像<strong>云存档</strong>：存档不在本地，搬到另一台机器也能续玩。
</div>

<h2>检查点（Checkpoint）</h2>
<p>Workflow 在每个 superstep 边界自动存档。默认用 <span class="mono">InMemoryCheckpointStorage</span>；
生产换成持久化存储（如 Redis、Cosmos）。崩溃后重启，从最近存档恢复。</p>

<h2>人在环（HITL）</h2>
<p>工具可设置 <span class="mono">approval_mode="always_require"</span>，执行前暂停等人确认。
工作流层面也有 <span class="mono">request_info</span> 机制：节点暂停、发问、等回答再继续。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> DurableTask 是什么？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 持久化执行</div>
      <div class="a"><span class="mono">packages/durabletask</span> 把工作流跑在 <strong>Durable Task Framework</strong> 上：
        状态持久化到外部存储，支持<strong>跨进程恢复</strong>和长时间等待（比如等人审批几小时）。
        配合 Azure Functions 可做无服务器部署。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><strong>检查点</strong>：Workflow superstep 自动存档，崩溃可恢复。</li>
    <li><strong>人在环</strong>：工具 <span class="mono">approval_mode</span> + 工作流 <span class="mono">request_info</span>。</li>
    <li><strong>持久化</strong>：DurableTask 包让状态存到外部，支持跨进程恢复。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>生产能力不是插件，是框架的一部分</strong>：检查点、审批、持久化都在核心 API 里，
  而不是你自己拼第三方库。
</div>
"""

L19_EN = r"""
<p class="lead">Production needs: <strong>save progress mid-run</strong> (checkpoints), <strong>human approval at
critical steps</strong> (HITL), <strong>resume after crashes</strong> (durability). MAF makes all three first-class.</p>

<div class="card analogy">
  <div class="tag">💾 Analogy</div>
  Checkpoints are <strong>game saves</strong>: save progress, crash, reload from save.
  HITL is an <strong>approval workflow</strong>: pause at a critical node, wait for a signature.
  DurableTask is <strong>cloud saves</strong>: saves aren't local — move to another machine and keep playing.
</div>

<h2>Checkpoints</h2>
<p>Workflows auto-save at each superstep boundary. Default: <span class="mono">InMemoryCheckpointStorage</span>;
swap to persistent storage (Redis, Cosmos) for production. After a crash, restart and resume from the latest save.</p>

<h2>Human-in-the-Loop (HITL)</h2>
<p>Tools can set <span class="mono">approval_mode="always_require"</span> to pause for human confirmation.
At the workflow level, <span class="mono">request_info</span> lets a node pause, ask a question, and wait for a reply.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> What is DurableTask? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 Durable execution</div>
      <div class="a"><span class="mono">packages/durabletask</span> runs workflows on the <strong>Durable Task Framework</strong>:
        state is persisted to external storage, supporting <strong>cross-process resume</strong> and long waits
        (e.g. waiting hours for human approval). Pair with Azure Functions for serverless deployment.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>Checkpoints</strong>: auto-saved at Workflow supersteps; crash-recoverable.</li>
    <li><strong>HITL</strong>: tool <span class="mono">approval_mode</span> + workflow <span class="mono">request_info</span>.</li>
    <li><strong>Durability</strong>: DurableTask package persists state externally for cross-process resume.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Production features aren't plugins — they're part of the framework</strong>: checkpoints, approvals and
  durability are in the core API, not third-party libraries you glue on yourself.
</div>
"""

# ---------------------------------------------------------------------------
L20_ZH = r"""
<p class="lead">最后一课实战：把前面学的<strong>Agent + 工具 + 编排 + 检查点</strong>拼成一个
<strong>多 Agent 工作流</strong>。</p>

<h2>场景：写作 → 审稿</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>创建两个 Agent</h4>
    <p><strong>Writer</strong>：根据提示写文章。<strong>Reviewer</strong>：审稿、提修改意见。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>用 SequentialBuilder 编排</h4>
    <p>Writer 写完 → Reviewer 审稿，串行。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>跑起来</h4>
    <p><span class="mono">workflow.run("Write about AI agents")</span>。</p></div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">端到端示例骨架</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder

writer = Agent(client=client, name=<span class="st">"Writer"</span>,
    instructions=<span class="st">"Write a short article on the given topic."</span>)
reviewer = Agent(client=client, name=<span class="st">"Reviewer"</span>,
    instructions=<span class="st">"Review the article. Suggest improvements."</span>)

workflow = SequentialBuilder(participants=[writer, reviewer]).build()
result = <span class="kw">await</span> workflow.run(<span class="st">"Write about AI agents"</span>)</pre>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> 加上工具和检查点 <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 扩展</div>
      <div class="a">给 Writer 加 <span class="mono">tools=[web_search]</span> 让它查资料；
        在 Reviewer 的工具里加 <span class="mono">approval_mode="always_require"</span> 的发布工具。
        检查点在 Workflow superstep 边界自动保存——如果中间断了，重启从最后存档恢复。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>多 Agent 工作流 = 几个 Agent + 一个 Builder + <span class="mono">.build().run()</span>。</li>
    <li>工具、中间件、检查点、人在环——全部可以叠加进去。</li>
    <li>从"hello agent"到"生产级多 Agent"，代码增量很小。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>复杂度是增量的</strong>：单 Agent → 加工具 → 加编排 → 加检查点 → 加审批，每一步只增加几行代码。
  这就是"从原型到生产"的体验。
</div>
"""

L20_EN = r"""
<p class="lead">Capstone: assemble <strong>Agent + tools + orchestration + checkpoints</strong> from earlier lessons
into a <strong>multi-Agent workflow</strong>.</p>

<h2>Scenario: write → review</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Create two Agents</h4>
    <p><strong>Writer</strong>: writes an article from a prompt. <strong>Reviewer</strong>: reviews it, suggests edits.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Orchestrate with SequentialBuilder</h4>
    <p>Writer finishes → Reviewer reviews, in sequence.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Run it</h4>
    <p><span class="mono">workflow.run("Write about AI agents")</span>.</p></div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">end-to-end skeleton</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder

writer = Agent(client=client, name=<span class="st">"Writer"</span>,
    instructions=<span class="st">"Write a short article on the given topic."</span>)
reviewer = Agent(client=client, name=<span class="st">"Reviewer"</span>,
    instructions=<span class="st">"Review the article. Suggest improvements."</span>)

workflow = SequentialBuilder(participants=[writer, reviewer]).build()
result = <span class="kw">await</span> workflow.run(<span class="st">"Write about AI agents"</span>)</pre>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> Add tools and checkpoints <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Extensions</div>
      <div class="a">Give Writer <span class="mono">tools=[web_search]</span> for research; add a publish tool with
        <span class="mono">approval_mode="always_require"</span> to Reviewer. Checkpoints auto-save at Workflow superstep
        boundaries — if interrupted, restart resumes from the latest save.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Multi-Agent workflow = a few Agents + one Builder + <span class="mono">.build().run()</span>.</li>
    <li>Tools, middleware, checkpoints, HITL — all stackable.</li>
    <li>From "hello agent" to "production multi-Agent" with minimal code increase.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Complexity is incremental</strong>: single Agent → add tools → add orchestration → add checkpoints → add
  approvals, each step adds only a few lines. That's the "prototype to production" experience.
</div>
"""
