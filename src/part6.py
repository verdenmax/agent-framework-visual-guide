"""Content for Part 6 (bonus): lessons 21-22 — Chinese + English."""

# ---------------------------------------------------------------------------
L21_ZH = r"""
<p class="lead">Agent 框架不止 MAF 一个。本课横向对比四大框架，帮你建立<strong>全局坐标</strong>。</p>

<div class="card analogy">
  <div class="tag">🗺️ 生活类比</div>
  <strong>MAF</strong> 像<strong>全能 SUV</strong>（城市通勤到越野都行），<strong>LangGraph</strong> 像<strong>手动挡跑车</strong>（精确控制），
  <strong>AutoGen</strong> 像<strong>实验越野车</strong>（探路利器），<strong>SK</strong> 像<strong>商务轿车</strong>（企业平稳）。
</div>

<h2>四框架对比</h2>
<table class="t">
  <tr><th></th><th>MAF</th><th>LangGraph</th><th>AutoGen</th><th>Semantic Kernel</th></tr>
  <tr><td><strong>编排模型</strong></td><td>图（Workflow）+ 预置编排</td><td>图（StateGraph）</td><td>多 Agent 对话</td><td>Planner + 管道</td></tr>
  <tr><td><strong>语言</strong></td><td>Python + .NET</td><td>Python (+ JS)</td><td>Python + .NET</td><td>Python + .NET + Java</td></tr>
  <tr><td><strong>生产特性</strong></td><td>检查点 · HITL · OTel · DurableTask</td><td>检查点 · HITL · LangSmith</td><td>基础 logging</td><td>连接器 · 企业集成</td></tr>
  <tr><td><strong>定位</strong></td><td>原型到生产，SK + AutoGen 统一继任</td><td>图控制流 + 可控 Agent</td><td>多 Agent 研究/探索</td><td>企业 AI 编排</td></tr>
</table>

<p class="acc-intro" style="color:var(--muted);font-size:.92rem">
👇 点开下面的折叠卡片，深入对比每一对框架——代码示例、架构差异、选型建议。
</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> MAF vs LangGraph 深入对比 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">同一件事——"两个 Agent 串行"——在两个框架里的写法：
<pre class="code"><span class="cm"># MAF：用 SequentialBuilder</span>
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder
wf = SequentialBuilder(participants=[writer, reviewer]).build()
result = <span class="kw">await</span> wf.run(<span class="st">"Write a poem"</span>)

<span class="cm"># LangGraph：手画 StateGraph</span>
<span class="kw">from</span> langgraph.graph <span class="kw">import</span> StateGraph
graph = StateGraph(State)
graph.add_node(<span class="st">"writer"</span>, writer_fn)
graph.add_node(<span class="st">"reviewer"</span>, reviewer_fn)
graph.add_edge(<span class="st">"writer"</span>, <span class="st">"reviewer"</span>)
app = graph.compile()
result = app.invoke({<span class="st">"input"</span>: <span class="st">"Write a poem"</span>})</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">LangGraph 是 LangChain 生态的图编排层，用户基数大、文档丰富。
        做技术选型时，这两个框架经常被放到一起比较，你需要知道它们的本质差异在哪——
        是"图模型"还是"编排抽象层级"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 提供<strong>两个抽象层</strong>：底层 <span class="mono">WorkflowBuilder</span>（和 LangGraph 的 StateGraph 同级，手动画图），
        上层<strong>预置编排</strong>（Sequential / Concurrent / Handoff / Group / Magentic）。大部分场景用预置编排几行搞定，
        复杂拓扑再下沉到手动图。LangGraph 只有手动图这一级——简单任务也要手画。
        另外 MAF 原生双语言（Python + .NET），LangGraph 主要 Python。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>LangGraph</strong> 适合已在 LangChain 生态里、需要最细粒度图控制的团队。
        <strong>两者混用</strong>也是可行的——用 MAF 的 Agent + ChatClient，但用 LangGraph 做编排（它们不冲突，只是编排层替换）。
        <strong>Temporal / Prefect</strong>等通用工作流引擎也能编排 Agent，但缺乏 AI 原生抽象。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> MAF vs AutoGen 深入对比 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">AutoGen 的范式是"多个 Agent 在群聊里对话"：
<pre class="code"><span class="cm"># AutoGen 风格（MAF 里用 MagenticBuilder 实现）</span>
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> MagenticBuilder
wf = MagenticBuilder(
    participants=[coder, reviewer, tester],
    manager=manager,
).build()
result = <span class="kw">await</span> wf.run(<span class="st">"Build a calculator app"</span>)</pre>
        AutoGen 原版需要自己搭 <span class="mono">GroupChat</span> + <span class="mono">GroupChatManager</span>，
        MAF 把这个模式封装成了 <span class="mono">MagenticBuilder</span>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">AutoGen 是微软研究院出的多 Agent 框架，开创了"多 Agent 对话"范式。
        MAF 直接继承了 AutoGen 的 Magentic-One 思想（指挥官 + 工人），
        所以了解两者关系能帮你判断"用 MAF 就够了，还是仍需要原版 AutoGen"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 把 AutoGen 的<strong>多 Agent 对话</strong>做成了<strong>编排模式之一</strong>（MagenticBuilder / GroupChatBuilder），
        而不是唯一范式。你可以在同一个项目里混用 Sequential（简单串行）和 Magentic（指挥官调度），
        而 AutoGen 里所有事都是"对话"，简单任务也被迫用群聊。
        另外 MAF 的<strong>生产特性</strong>（检查点、OTel、DurableTask）远超 AutoGen。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>原版 AutoGen</strong> 仍适合纯研究 / 快速原型（API 更简单，社区活跃）。
        <strong>CrewAI</strong> 是另一个多 Agent 框架，角色定义更"人性化"但生产特性弱。
        如果你只要"两个 Agent 对话"，不需要编排引擎，<strong>手写循环</strong>其实最简单。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> MAF vs Semantic Kernel 深入对比 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">SK 的核心抽象是 Kernel + Plugin + Planner：
<pre class="code"><span class="cm"># Semantic Kernel 风格</span>
kernel = Kernel()
kernel.add_plugin(WeatherPlugin(), <span class="st">"weather"</span>)
result = <span class="kw">await</span> kernel.invoke_prompt(<span class="st">"What's the weather in Seattle?"</span>)

<span class="cm"># MAF 风格——同样的事</span>
agent = Agent(client=client, tools=[get_weather],
    instructions=<span class="st">"Answer weather questions."</span>)
result = <span class="kw">await</span> agent.run(<span class="st">"What's the weather in Seattle?"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">Semantic Kernel 是 MAF 的<strong>前身之一</strong>——很多企业已经在用 SK。
        理解 SK → MAF 的演进，能帮已有 SK 用户判断是否迁移、怎么迁移。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">SK 强在<strong>企业连接器</strong>（几十种现成 Plugin）和<strong>Planner</strong>（LLM 自动规划步骤）。
        MAF 继承了这些能力，并<strong>新增</strong>：图式 Workflow 编排（SK 没有）、多 Agent 协作（SK 没有）、
        DurableTask 持久化、统一的 ChatClient 抽象（SK 的 ChatCompletionService 更分散）。
        MAF 是微软官方推荐的"下一代"方向。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>继续用 SK</strong>——如果已有大量 SK Plugin 且不需要多 Agent / 工作流，短期内不急着迁。
        <strong>渐进迁移</strong>——SK 和 MAF 可以共存，先在新功能上用 MAF，老功能保持 SK。
        <strong>直接 MAF</strong>——新项目建议直接用 MAF，因为 SK 的维护重心已转向 MAF。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 生态与社区对比 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">截至 2026 年中的大致状况：
<pre class="code"><span class="cm"># GitHub 星标（量级）</span>
MAF:       ~10k  (快速增长，微软全力投入)
LangChain: ~100k (最大社区，但 LangGraph 星标分开计)
AutoGen:   ~40k  (研究社区活跃)
SK:        ~25k  (企业用户基数大)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">社区大小影响：遇到问题能不能搜到答案、有没有第三方插件、招聘时候选人熟不熟。
        这不是技术问题，但实际上经常是选型的<strong>决定性因素</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 虽年轻但背靠<strong>微软全力推</strong>：官方文档在 MS Learn、有 Discord 社区、
        与 Azure AI Foundry 深度集成。企业用户天然信任微软背书。
        且 MAF 吸收了 SK + AutoGen 两个社区的用户，增长曲线陡。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">如果你最看重<strong>社区和生态丰富度</strong>，LangChain 仍是最大的。
        如果看重<strong>学术前沿</strong>，AutoGen 论文产出最多。
        如果看重<strong>企业稳定性 + 微软生态</strong>，MAF 或 SK。
        没有"最好"——只有"最适合你的场景"。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>MAF = SK + AutoGen 合并演进，面向"原型到生产"。</li>
    <li>LangGraph 强在图控制流精度；AutoGen 强在多 Agent 对话探索。</li>
    <li>选框架看你的核心需求：语言、生产特性、控制粒度、社区生态。</li>
    <li>MAF 提供两层抽象（预置编排 + 手动图），覆盖从简到繁。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  MAF 把"图编排"和"多 Agent 对话"<strong>统一到同一个框架</strong>——你不用在 LangGraph 和 AutoGen 之间二选一。
  预置编排是糖，底层 Workflow 是引擎，两者可以混用。
</div>
"""

L21_EN = r"""
<p class="lead">MAF isn't the only agent framework. This lesson compares four major ones to give you
<strong>global coordinates</strong>.</p>

<div class="card analogy">
  <div class="tag">🗺️ Analogy</div>
  <strong>MAF</strong> is a <strong>versatile SUV</strong> (city to off-road), <strong>LangGraph</strong> is a
  <strong>manual-shift sports car</strong> (precise control), <strong>AutoGen</strong> is an <strong>experimental
  off-roader</strong> (trail blazer), <strong>SK</strong> is a <strong>business sedan</strong> (enterprise smooth).
</div>

<h2>Four-framework comparison</h2>
<table class="t">
  <tr><th></th><th>MAF</th><th>LangGraph</th><th>AutoGen</th><th>Semantic Kernel</th></tr>
  <tr><td><strong>Orchestration</strong></td><td>Graph (Workflow) + prebuilt patterns</td><td>Graph (StateGraph)</td><td>Multi-agent chat</td><td>Planner + pipeline</td></tr>
  <tr><td><strong>Languages</strong></td><td>Python + .NET</td><td>Python (+ JS)</td><td>Python + .NET</td><td>Python + .NET + Java</td></tr>
  <tr><td><strong>Production</strong></td><td>Checkpoints · HITL · OTel · DurableTask</td><td>Checkpoints · HITL · LangSmith</td><td>Basic logging</td><td>Connectors · enterprise</td></tr>
  <tr><td><strong>Positioning</strong></td><td>Prototype-to-prod, SK + AutoGen successor</td><td>Graph control flow + controllable agents</td><td>Multi-agent research</td><td>Enterprise AI orchestration</td></tr>
</table>

<p class="acc-intro" style="color:var(--muted);font-size:.92rem">
👇 Expand the cards below for deep dives — code examples, architecture differences, selection guidance.
</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> MAF vs LangGraph deep dive <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">The same task — "two agents in sequence" — in both frameworks:
<pre class="code"><span class="cm"># MAF: SequentialBuilder</span>
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder
wf = SequentialBuilder(participants=[writer, reviewer]).build()
result = <span class="kw">await</span> wf.run(<span class="st">"Write a poem"</span>)

<span class="cm"># LangGraph: hand-draw StateGraph</span>
<span class="kw">from</span> langgraph.graph <span class="kw">import</span> StateGraph
graph = StateGraph(State)
graph.add_node(<span class="st">"writer"</span>, writer_fn)
graph.add_node(<span class="st">"reviewer"</span>, reviewer_fn)
graph.add_edge(<span class="st">"writer"</span>, <span class="st">"reviewer"</span>)
app = graph.compile()
result = app.invoke({<span class="st">"input"</span>: <span class="st">"Write a poem"</span>})</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">LangGraph is the graph orchestration layer in the LangChain ecosystem — large user base, rich docs.
        When evaluating tech, these two get compared constantly. You need to know their essential difference:
        the level of orchestration abstraction, not just "both are graphs".</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF provides <strong>two abstraction levels</strong>: low-level <span class="mono">WorkflowBuilder</span>
        (same tier as LangGraph's StateGraph — hand-draw the graph), and high-level <strong>prebuilt orchestrations</strong>
        (Sequential / Concurrent / Handoff / Group / Magentic). Most scenarios use the prebuilts in a few lines;
        complex topologies drop down to the manual graph. LangGraph only has the manual graph — even simple tasks require drawing.
        MAF is also natively dual-language (Python + .NET); LangGraph is mainly Python.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>LangGraph</strong> suits teams already in the LangChain ecosystem needing the finest graph control.
        <strong>Mixing both</strong> is viable — use MAF's Agent + ChatClient but LangGraph for orchestration (they don't conflict).
        <strong>Temporal / Prefect</strong> (general workflow engines) can also orchestrate agents but lack AI-native abstractions.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> MAF vs AutoGen deep dive <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">AutoGen's paradigm: "multiple agents chatting in a group":
<pre class="code"><span class="cm"># AutoGen style (in MAF via MagenticBuilder)</span>
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> MagenticBuilder
wf = MagenticBuilder(
    participants=[coder, reviewer, tester],
    manager=manager,
).build()
result = <span class="kw">await</span> wf.run(<span class="st">"Build a calculator app"</span>)</pre>
        The original AutoGen requires assembling <span class="mono">GroupChat</span> + <span class="mono">GroupChatManager</span> yourself;
        MAF packages this as <span class="mono">MagenticBuilder</span>.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">AutoGen pioneered the "multi-agent conversation" paradigm (from Microsoft Research).
        MAF directly inherits AutoGen's Magentic-One idea (conductor + workers).
        Understanding the relationship helps you decide: "Is MAF enough, or do I still need original AutoGen?"</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF makes AutoGen's <strong>multi-agent chat</strong> just <strong>one orchestration pattern among many</strong>,
        not the only paradigm. You can mix Sequential (simple chains) and Magentic (conductor dispatch) in one project.
        In AutoGen everything is "conversation" — even simple tasks force group chat.
        MAF's <strong>production features</strong> (checkpoints, OTel, DurableTask) also far exceed AutoGen's.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Original AutoGen</strong> still suits pure research / rapid prototyping (simpler API, active community).
        <strong>CrewAI</strong> is another multi-agent framework with more "human-like" role definitions but weaker production features.
        If you only need "two agents chatting", <strong>a hand-written loop</strong> is actually simplest.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> MAF vs Semantic Kernel deep dive <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">SK's core abstractions: Kernel + Plugin + Planner:
<pre class="code"><span class="cm"># Semantic Kernel style</span>
kernel = Kernel()
kernel.add_plugin(WeatherPlugin(), <span class="st">"weather"</span>)
result = <span class="kw">await</span> kernel.invoke_prompt(<span class="st">"What's the weather in Seattle?"</span>)

<span class="cm"># MAF — same thing</span>
agent = Agent(client=client, tools=[get_weather],
    instructions=<span class="st">"Answer weather questions."</span>)
result = <span class="kw">await</span> agent.run(<span class="st">"What's the weather in Seattle?"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Semantic Kernel is one of MAF's <strong>predecessors</strong> — many enterprises already use it.
        Understanding SK → MAF evolution helps existing SK users decide whether and how to migrate.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">SK excels at <strong>enterprise connectors</strong> (dozens of ready-made Plugins) and <strong>Planners</strong>
        (LLM auto-plans steps). MAF inherits these and <strong>adds</strong>: graph Workflow orchestration (SK doesn't have this),
        multi-agent collaboration (SK doesn't have this), DurableTask persistence, and a unified ChatClient abstraction
        (SK's ChatCompletionService is more fragmented). MAF is Microsoft's official "next-gen" direction.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Stay on SK</strong> — if you have many SK Plugins and don't need multi-agent / workflows, no rush.
        <strong>Gradual migration</strong> — SK and MAF can coexist; use MAF for new features, keep old ones on SK.
        <strong>Go MAF</strong> — for new projects, recommended since SK's maintenance focus has shifted to MAF.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Ecosystem &amp; community comparison <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Rough picture as of mid-2026:
<pre class="code"><span class="cm"># GitHub stars (order of magnitude)</span>
MAF:       ~10k  (fast growth, full Microsoft backing)
LangChain: ~100k (largest community; LangGraph stars counted separately)
AutoGen:   ~40k  (active research community)
SK:        ~25k  (large enterprise user base)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Community size affects: can you find answers when stuck, are there third-party plugins,
        do candidates know the framework when you're hiring. Not a technical issue, but often the
        <strong>deciding factor</strong> in practice.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF is young but backed by <strong>full Microsoft investment</strong>: official docs on MS Learn,
        Discord community, deep Azure AI Foundry integration. Enterprise users naturally trust Microsoft backing.
        MAF also absorbed users from both SK and AutoGen communities — steep growth curve.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">If <strong>community and ecosystem richness</strong> is your top priority, LangChain is still the largest.
        If <strong>academic frontier</strong> matters most, AutoGen has the most paper output.
        If <strong>enterprise stability + Microsoft ecosystem</strong>, MAF or SK.
        There's no "best" — only "best for your scenario".</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>MAF = SK + AutoGen merged, aimed at "prototype to production".</li>
    <li>LangGraph excels at graph control precision; AutoGen at multi-agent chat exploration.</li>
    <li>Pick by your core needs: language, production features, control granularity, ecosystem.</li>
    <li>MAF offers two abstraction levels (prebuilt orchestrations + manual graph), covering simple to complex.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  MAF <strong>unifies graph orchestration and multi-agent chat in one framework</strong> — you don't have to choose
  between LangGraph and AutoGen. Prebuilt orchestrations are sugar; the underlying Workflow is the engine. Mix freely.
</div>
"""

# ---------------------------------------------------------------------------
L22_ZH = r"""
<p class="lead">最后一课，缩放镜头：把 MAF 放进<strong>AI 全栈</strong>的坐标系里——
看看你现在在哪，隔壁层还有什么值得学。</p>

<h2>AI 全栈分层</h2>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">L7</span><span class="name">应用层</span></div>
    <div class="ld">你的产品 / UI / API 网关（Chainlit · Streamlit · FastAPI）。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">L6</span><span class="name">Agent 编排</span></div>
    <div class="ld"><strong>← 你在这里</strong>（MAF / LangGraph / AutoGen / SK）。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">L5</span><span class="name">模型 API / 推理</span></div>
    <div class="ld">OpenAI API · Azure AI · vLLM · llama.cpp · Ollama。</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">L4</span><span class="name">向量检索 / RAG</span></div>
    <div class="ld">Embeddings · pgvector · Qdrant · Azure AI Search。</div></div>
</div>

<h2>编排流派一览</h2>
<table class="t">
  <tr><th>流派</th><th>代表</th><th>核心思想</th></tr>
  <tr><td>链/管道</td><td>LangChain LCEL</td><td>函数组合，<span class="mono">A | B | C</span></td></tr>
  <tr><td>图</td><td>LangGraph / MAF Workflow</td><td>有向图 + 状态</td></tr>
  <tr><td>多 Agent 对话</td><td>AutoGen / MAF Group Chat</td><td>Agent 间消息传递</td></tr>
  <tr><td>Planner</td><td>SK</td><td>LLM 规划步骤后执行</td></tr>
  <tr><td>声明式</td><td>MAF Declarative / Rivet</td><td>配置驱动</td></tr>
</table>

<p class="acc-intro" style="color:var(--muted);font-size:.92rem">
👇 点开卡片，深入了解每个隔壁层——学什么、用什么工具、什么时候该学。
</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> L5 推理层深入 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">推理层的三种选择：
<pre class="code"><span class="cm"># vLLM — 高吞吐 GPU 推理服务</span>
vllm serve meta-llama/Llama-3-8B --port 8000

<span class="cm"># llama.cpp — CPU / 边缘设备推理</span>
./main -m model.gguf -p <span class="st">"Hello"</span>

<span class="cm"># Ollama — 本地一键跑模型</span>
ollama run llama3</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">MAF 通过 ChatClient 调用模型，但<strong>模型从哪来</strong>？如果你用 OpenAI API 就不用管；
        但如果要<strong>私有化部署</strong>（数据安全、成本控制、低延迟），就需要了解推理层。
        vLLM 适合高并发 GPU 场景，llama.cpp 适合边缘/嵌入式，Ollama 适合开发者本地调试。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 不绑定推理层：<span class="mono">OpenAIChatClient</span> 可以指向任何兼容 OpenAI API 的端点
        （vLLM、llama.cpp 的 server 模式、Ollama 都兼容）。所以你可以先用 OpenAI API 开发，
        上线时切到私有 vLLM，<strong>Agent 代码不用改</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>TGI</strong>（HuggingFace 的推理服务器）、<strong>TensorRT-LLM</strong>（NVIDIA 优化）、
        <strong>Azure AI Foundry</strong>（托管推理，零运维）。如果你不想自己运维 GPU，用云端 API 最省心。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> L4 向量检索 / RAG 深入 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">向量检索的核心流程：
<pre class="code"><span class="cm"># 1. 文本 → Embedding 向量</span>
vector = embedding_model.encode(<span class="st">"What is MAF?"</span>)

<span class="cm"># 2. 向量存入数据库</span>
db.insert(vector, metadata={<span class="st">"source"</span>: <span class="st">"docs/readme.md"</span>})

<span class="cm"># 3. 查询时找最相似的向量</span>
results = db.search(query_vector, top_k=<span class="nb">5</span>)

<span class="cm"># 4. 把检索到的文本塞给 Agent 作上下文</span>
context = <span class="st">"\n"</span>.join(r.text <span class="kw">for</span> r <span class="kw">in</span> results)
<span class="kw">await</span> agent.run(f<span class="st">"Based on: {context}\nAnswer: {question}"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">LLM 不知道你的私有数据。<strong>RAG（检索增强生成）</strong>通过在提示词里塞进相关文档片段，
        让模型能"看到"你的知识库。向量检索是 RAG 的核心引擎——把"语义相似度"变成数据库查询。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 通过 <span class="mono">ContextProvider</span> 机制集成 RAG：
        <span class="mono">packages/azure-ai-search</span> 封装了 Azure AI Search（企业级向量检索），
        你也可以自己写 ContextProvider 接 pgvector / Qdrant / Pinecone。
        Agent 不需要知道知识从哪来——<strong>ContextProvider 在 run 前自动注入</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>pgvector</strong>（熟悉 SQL 的首选，PostgreSQL 扩展）、
        <strong>Qdrant</strong>（云原生向量数据库，专为向量设计）、
        <strong>Chroma</strong>（轻量嵌入式，适合本地原型）、
        <strong>Azure AI Search</strong>（企业级，MAF 有现成包）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> L7 应用层深入 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">把 MAF Agent 暴露为 Web 端点：
<pre class="code"><span class="cm"># FastAPI + MAF Agent</span>
<span class="kw">from</span> fastapi <span class="kw">import</span> FastAPI
app = FastAPI()

<span class="nb">@app.post</span>(<span class="st">"/chat"</span>)
<span class="kw">async def</span> <span class="fn">chat</span>(prompt: str):
    result = <span class="kw">await</span> agent.run(prompt)
    <span class="kw">return</span> {<span class="st">"response"</span>: str(result)}</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">Agent 不能只在终端里跑——最终要面向用户。应用层负责<strong>UI、API、认证、限流</strong>等。
        了解怎么把 Agent 包成 API / Web 应用，是从"能跑"到"能用"的关键一步。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的 <span class="mono">hosting</span> 包提供了多种部署方式：
        <strong>ASP.NET Core / Azure Functions</strong>（.NET 端）、
        <strong>FastAPI / Azure Functions</strong>（Python 端）、
        <strong>A2A 协议</strong>（Agent-to-Agent，让 Agent 作为服务被其他 Agent 调用）、
        <strong>Foundry 托管 Agent</strong>（零运维部署到 Azure）。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>Chainlit</strong>（一行代码搞定聊天 UI，适合 demo）、
        <strong>Streamlit</strong>（快速数据应用 + 聊天界面）、
        <strong>Gradio</strong>（ML demo 界面）、
        <strong>自建 React/Vue 前端</strong>（最灵活但工作量最大）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 三条学习路径推荐 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 路径 A：我要做一个生产级聊天机器人</div>
      <div class="a"><strong>本教程 L01-07</strong>（基础）→ <strong>L16</strong>（选 provider）→
        <strong>L18-19</strong>（中间件 + 检查点）→ <strong>L7 应用层</strong>（FastAPI / Foundry 托管）→
        <strong>L4 向量检索</strong>（Azure AI Search / pgvector，做 RAG）。
        重点：<strong>先跑通，再加 RAG，再加生产能力</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 路径 B：我要理解 AI 基础设施</div>
      <div class="a"><strong>本教程 L01-03</strong>（全局观）→ <strong>L08-14</strong>（内部源码）→
        <strong>L5 推理层</strong>（vLLM / llama.cpp）→ <strong>L4 向量检索</strong>（hnswlib / pgvector）→
        <strong>L15</strong>（读 MAF 源码）。
        重点：<strong>从应用层往下挖，理解每一层在做什么</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 路径 C：我要贡献 MAF 源码</div>
      <div class="a"><strong>本教程全部 22 课</strong>（建立完整认知）→ <strong>L15</strong>（搭环境 + 跑测试）→
        从 <span class="mono">good first issue</span> 开始 →
        <strong>读 AGENTS.md + CODING_STANDARD.md</strong> → 提 PR。
        重点：<strong>先读懂，再动手；先小改，再大改</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 通用建议</div>
      <div class="a">不要试图一次学完所有层——<strong>从你的目标出发，往上或往下扩展一层</strong>就好。
        做 Agent 应用？先吃透 L6（编排），再看 L4（RAG）和 L7（应用）。
        做基础设施？先吃透 L5（推理），再看 L6（编排）。
        <strong>边做边学</strong>永远比"先学完再做"高效。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>MAF 在全栈中位于 <strong>L6 Agent 编排层</strong>。</li>
    <li>下一层（L5 推理 / L4 向量检索）是深入 AI 基础设施的方向。</li>
    <li>上一层（L7 应用）是把 Agent 交给用户的方向。</li>
    <li>选学习路径看你的目标：做产品 / 学基础 / 贡献源码。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>编排层是"胶水层"</strong>——它连接模型、工具、存储和应用，
  因此<strong>对上下层都有基本了解</strong>是成为 Agent 高手的关键。
  你不需要精通每一层，但需要知道它在做什么、怎么和你的层对接。
</div>
"""
L22_EN = r"""
<p class="lead">Final lesson — zoom out: place MAF in the <strong>AI full-stack</strong> coordinate system and see
what's worth learning next door.</p>

<h2>AI full-stack layers</h2>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">L7</span><span class="name">Application</span></div>
    <div class="ld">Your product / UI / API gateway (Chainlit · Streamlit · FastAPI).</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">L6</span><span class="name">Agent Orchestration</span></div>
    <div class="ld"><strong>← You are here</strong> (MAF / LangGraph / AutoGen / SK).</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">L5</span><span class="name">Model API / Inference</span></div>
    <div class="ld">OpenAI API · Azure AI · vLLM · llama.cpp · Ollama.</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">L4</span><span class="name">Vector Search / RAG</span></div>
    <div class="ld">Embeddings · pgvector · Qdrant · Azure AI Search.</div></div>
</div>

<h2>Orchestration schools</h2>
<table class="t">
  <tr><th>School</th><th>Representative</th><th>Core idea</th></tr>
  <tr><td>Chain/pipeline</td><td>LangChain LCEL</td><td>Function composition, <span class="mono">A | B | C</span></td></tr>
  <tr><td>Graph</td><td>LangGraph / MAF Workflow</td><td>Directed graph + state</td></tr>
  <tr><td>Multi-agent chat</td><td>AutoGen / MAF Group Chat</td><td>Message passing between agents</td></tr>
  <tr><td>Planner</td><td>SK</td><td>LLM plans steps then executes</td></tr>
  <tr><td>Declarative</td><td>MAF Declarative / Rivet</td><td>Config-driven</td></tr>
</table>

<p class="acc-intro" style="color:var(--muted);font-size:.92rem">
👇 Expand the cards to dive into each neighbouring layer — what to learn, which tools, when to learn it.
</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> L5 Inference layer deep dive <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Three inference choices:
<pre class="code"><span class="cm"># vLLM — high-throughput GPU inference</span>
vllm serve meta-llama/Llama-3-8B --port 8000

<span class="cm"># llama.cpp — CPU / edge inference</span>
./main -m model.gguf -p <span class="st">"Hello"</span>

<span class="cm"># Ollama — local one-click model</span>
ollama run llama3</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">MAF calls models via ChatClient, but <strong>where does the model come from</strong>?
        If you use OpenAI API you don't worry about this; but for <strong>private deployment</strong>
        (data security, cost control, low latency) you need the inference layer.
        vLLM for high-concurrency GPU, llama.cpp for edge/CPU, Ollama for local dev.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF doesn't lock you to any inference layer: <span class="mono">OpenAIChatClient</span> can point at any
        OpenAI-compatible endpoint (vLLM, llama.cpp server mode, Ollama all qualify).
        Develop with OpenAI API, deploy on private vLLM — <strong>zero Agent code changes</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>TGI</strong> (HuggingFace inference server), <strong>TensorRT-LLM</strong> (NVIDIA optimised),
        <strong>Azure AI Foundry</strong> (managed inference, zero ops).
        If you don't want to run GPUs yourself, cloud APIs are simplest.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> L4 Vector search / RAG deep dive <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Core vector search flow:
<pre class="code"><span class="cm"># 1. Text → embedding vector</span>
vector = embedding_model.encode(<span class="st">"What is MAF?"</span>)

<span class="cm"># 2. Store in vector DB</span>
db.insert(vector, metadata={<span class="st">"source"</span>: <span class="st">"docs/readme.md"</span>})

<span class="cm"># 3. At query time, find most similar</span>
results = db.search(query_vector, top_k=<span class="nb">5</span>)

<span class="cm"># 4. Feed retrieved text to Agent as context</span>
context = <span class="st">"\n"</span>.join(r.text <span class="kw">for</span> r <span class="kw">in</span> results)
<span class="kw">await</span> agent.run(f<span class="st">"Based on: {context}\nAnswer: {question}"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">LLMs don't know your private data. <strong>RAG (Retrieval-Augmented Generation)</strong> splices
        relevant document chunks into the prompt so the model can "see" your knowledge base.
        Vector search is RAG's core engine — turns "semantic similarity" into a database query.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF integrates RAG through <span class="mono">ContextProvider</span>:
        <span class="mono">packages/azure-ai-search</span> wraps Azure AI Search (enterprise vector search);
        you can also write your own ContextProvider to plug in pgvector / Qdrant / Pinecone.
        The Agent doesn't need to know where knowledge comes from — <strong>ContextProvider auto-injects before run</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>pgvector</strong> (PostgreSQL extension, familiar to SQL users),
        <strong>Qdrant</strong> (cloud-native, purpose-built for vectors),
        <strong>Chroma</strong> (lightweight embedded, good for local prototypes),
        <strong>Azure AI Search</strong> (enterprise-grade, MAF has a ready-made package).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> L7 Application layer deep dive <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Expose an MAF Agent as a web endpoint:
<pre class="code"><span class="cm"># FastAPI + MAF Agent</span>
<span class="kw">from</span> fastapi <span class="kw">import</span> FastAPI
app = FastAPI()

<span class="nb">@app.post</span>(<span class="st">"/chat"</span>)
<span class="kw">async def</span> <span class="fn">chat</span>(prompt: str):
    result = <span class="kw">await</span> agent.run(prompt)
    <span class="kw">return</span> {<span class="st">"response"</span>: str(result)}</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Agents can't just run in a terminal — they need to face users. The application layer owns
        <strong>UI, API, auth, rate limiting</strong>. Knowing how to wrap an Agent into an API / web app
        is the key step from "it runs" to "it's usable".</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's <span class="mono">hosting</span> packages provide multiple deployment paths:
        <strong>ASP.NET Core / Azure Functions</strong> (.NET),
        <strong>FastAPI / Azure Functions</strong> (Python),
        <strong>A2A protocol</strong> (Agent-to-Agent, exposing an Agent as a service for other Agents),
        <strong>Foundry Hosted Agents</strong> (zero-ops deploy to Azure).</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Chainlit</strong> (one-liner chat UI, great for demos),
        <strong>Streamlit</strong> (rapid data apps + chat interface),
        <strong>Gradio</strong> (ML demo interfaces),
        <strong>Custom React/Vue frontend</strong> (most flexible but most work).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Three recommended learning paths <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Path A: I want to build a production chatbot</div>
      <div class="a"><strong>This guide L01-07</strong> (basics) → <strong>L16</strong> (pick a provider) →
        <strong>L18-19</strong> (middleware + checkpoints) → <strong>L7 application layer</strong> (FastAPI / Foundry hosting) →
        <strong>L4 vector search</strong> (Azure AI Search / pgvector for RAG).
        Focus: <strong>get it running, add RAG, add production features</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Path B: I want to understand AI infrastructure</div>
      <div class="a"><strong>This guide L01-03</strong> (big picture) → <strong>L08-14</strong> (internals) →
        <strong>L5 inference</strong> (vLLM / llama.cpp) → <strong>L4 vector search</strong> (hnswlib / pgvector) →
        <strong>L15</strong> (read MAF source).
        Focus: <strong>drill down from the application layer; understand what each layer does</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ Path C: I want to contribute to MAF</div>
      <div class="a"><strong>All 22 lessons</strong> (build complete understanding) → <strong>L15</strong> (set up env + run tests) →
        start with <span class="mono">good first issue</span> →
        <strong>read AGENTS.md + CODING_STANDARD.md</strong> → submit a PR.
        Focus: <strong>understand first, then act; start small, then go big</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 General advice</div>
      <div class="a">Don't try to learn every layer at once — <strong>start from your goal and expand one layer up or down</strong>.
        Building Agent apps? Master L6 (orchestration), then look at L4 (RAG) and L7 (application).
        Building infrastructure? Master L5 (inference), then look at L6 (orchestration).
        <strong>Learn by doing</strong> is always more efficient than "learn everything first".</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>MAF sits at <strong>L6 — the Agent Orchestration layer</strong>.</li>
    <li>Next layer down (L5 inference / L4 vector search) deepens AI infrastructure.</li>
    <li>Next layer up (L7 application) delivers agents to users.</li>
    <li>Pick a learning path based on your goal: build products / learn fundamentals / contribute code.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>The orchestration layer is the "glue layer"</strong> — it connects models, tools, storage and applications.
  Knowing the layers above and below is key to becoming an Agent expert.
  You don't need to master every layer — just know what it does and how it interfaces with yours.
</div>
"""
