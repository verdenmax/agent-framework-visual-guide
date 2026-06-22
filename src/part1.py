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

<details class="accordion">
  <summary><span class="badge-num">2</span> 厂商锁定怎么破？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">直接用各家 SDK，写法各不相同：
<pre class="code"><span class="cm"># OpenAI</span>
<span class="kw">from</span> openai <span class="kw">import</span> OpenAI
client = OpenAI()
r = client.chat.completions.create(model=<span class="st">"gpt-4o"</span>, messages=[...])

<span class="cm"># Anthropic</span>
<span class="kw">from</span> anthropic <span class="kw">import</span> Anthropic
client = Anthropic()
r = client.messages.create(model=<span class="st">"claude-3-7-sonnet"</span>, max_tokens=1024, messages=[...])</pre>
换成 MAF 之后，只换一个 client，其余代码不动：
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
<span class="kw">from</span> agent_framework.openai <span class="kw">import</span> OpenAIChatClient
<span class="cm"># from agent_framework.anthropic import AnthropicClient  # 改这一行就够了</span>
agent = Agent(client=OpenAIChatClient(model=<span class="st">"gpt-4o"</span>), instructions=<span class="st">"…"</span>)
<span class="kw">await</span> agent.run(<span class="st">"你好"</span>)</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">三个非常现实的理由：<br>
        ① <strong>成本</strong>：同一任务在不同模型上价格相差 5–20 倍；<br>
        ② <strong>模型迭代极快</strong>：每个季度都有新模型登顶榜单，被锁死意味着踩不上红利；<br>
        ③ <strong>合规与可用性</strong>：金融 / 政府要求私有部署，海外业务要走 Foundry，国内可能要走自研网关。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 把所有厂商抽象成统一的 <span class="mono">ChatClient</span> 接口，
        <span class="mono">FoundryChatClient</span> / <span class="mono">OpenAIChatClient</span> /
        <span class="mono">AnthropicClient</span> / <span class="mono">OllamaChatClient</span> 全部实现同一组方法
        （<span class="mono">get_response()</span> / <span class="mono">get_streaming_response()</span>）。
        Agent、工具、工作流只依赖接口，"换一行 import"即可切换厂商。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>LiteLLM</strong>：外部代理服务，所有请求走 OpenAI 协议——简单但多一跳网络与运维。<br>
        ② <strong>自己写适配层</strong>：能拿到最贴合业务的接口，但要自己维护流式、工具、函数调用的差异。<br>
        ③ <strong>云厂商网关</strong>（Azure AI Gateway / AWS Bedrock）：合规与配额统一，缺点是仍被云厂商锁住。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 对话消息怎么"拼"才不出错？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">裸字典 vs MAF 的类型化消息：
<pre class="code"><span class="cm"># 裸字典——拼错 role 直到运行时才报错</span>
messages = [
  {<span class="st">"role"</span>: <span class="st">"sytsem"</span>, <span class="st">"content"</span>: <span class="st">"你是助手"</span>},  <span class="cm"># 拼写错了！</span>
  {<span class="st">"role"</span>: <span class="st">"user"</span>,   <span class="st">"content"</span>: <span class="st">"你好"</span>},
]

<span class="cm"># MAF——类型受控，IDE 自动补全</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> Message
messages = [
  Message(<span class="st">"system"</span>, <span class="st">"你是助手"</span>),
  Message(<span class="st">"user"</span>, <span class="st">"你好"</span>),
]</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">真实业务里消息绝不只是字符串：还有图像、工具调用、工具结果、思维链、引用等"内容块"。
        裸字典每加一种就要全工程改 if/else；用类型化的 <span class="mono">Content</span>，
        新内容只是<strong>多一个 Content 类型</strong>，老代码完全不动。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">见 <span class="mono">agent_framework/_types.py</span>：<span class="mono">Role</span> 是枚举
        （<span class="mono">system / user / assistant / tool</span>），<span class="mono">Message</span>
        持有 <span class="mono">contents: list[Content]</span>，<span class="mono">Content</span> 是
        统一内容类型，用 <span class="mono">Content.from_text()</span> 等工厂方法构造。
        好处：① 静态检查 + 补全；② 多模态 / 工具结果自然容纳；③ Workflow 跨进程序列化零成本。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>裸字典 + JSON Schema 校验</strong>：轻量但运行时才报错；<br>
        ② <strong>Pydantic 自建模型</strong>：MAF 内部就是 Pydantic v2，自己写等于重造轮子；<br>
        ③ <strong>LangChain 的 HumanMessage / AIMessage</strong>：思路相同，但内容块远不如 MAF 全面。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 工具调用为什么不要手写 JSON？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">裸 function calling vs MAF 的 <span class="mono">@tool</span>：
<pre class="code"><span class="cm"># 裸 SDK：自己写 schema、自己 dispatch、自己回灌</span>
tools = [{
  <span class="st">"type"</span>: <span class="st">"function"</span>,
  <span class="st">"function"</span>: {
    <span class="st">"name"</span>: <span class="st">"get_weather"</span>,
    <span class="st">"parameters"</span>: {<span class="st">"type"</span>: <span class="st">"object"</span>,
      <span class="st">"properties"</span>: {<span class="st">"city"</span>: {<span class="st">"type"</span>: <span class="st">"string"</span>}},
      <span class="st">"required"</span>: [<span class="st">"city"</span>]}}}]
<span class="cm"># 后续：解析 tool_calls → 找函数 → 调用 → 把结果塞回 messages → 再发一次……</span>

<span class="cm"># MAF：装饰器自动生成 schema，自动跑循环</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> tool

<span class="kw">@tool</span>
<span class="kw">def</span> get_weather(city: str) -&gt; str:
    <span class="st">"返回城市天气。"</span>
    <span class="kw">return</span> f<span class="st">"{city} 今天 23°C"</span>

agent = Agent(client=client, tools=[get_weather])</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">手写 JSON Schema 最容易出三类 bug：① 参数名/类型与函数实际签名不一致；
        ② 改函数忘了改 schema；③ 各家厂商对 schema 子集支持不同。
        自动生成意味着<strong>函数即文档、函数即合同</strong>，重构成本接近零。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">@tool</span>（见 <span class="mono">_tools.py</span>）借助
        <span class="mono">inspect</span> + 类型注解生成 JSON Schema，自动注入到 ChatClient 请求；
        模型返回 <span class="mono">FunctionCallContent</span> 时，Agent 在<strong>同一个循环</strong>里
        执行函数、把 <span class="mono">FunctionResultContent</span> 追加回消息，再次请求模型——你不用写一行胶水。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>手写 schema</strong>：最大可控、最大错率；<br>
        ② <strong>OpenAI 官方 function calling SDK</strong>：仅限 OpenAI 系；<br>
        ③ <strong>LangChain Tool / StructuredTool</strong>：思路类似，缺乏与中间件、Workflow 的统一集成；<br>
        ④ <strong>MCP 协议</strong>：工具跨进程托管，MAF 也支持把 MCP 工具当本地工具用。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> 多步 / 多 Agent 怎么不变成 while 怪兽？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">手写循环很快就会脏掉：
<pre class="code">messages = [...]
<span class="kw">while</span> True:
    resp = client.chat.completions.create(model=..., messages=messages, tools=tools)
    msg = resp.choices[0].message
    <span class="kw">if</span> <span class="kw">not</span> msg.tool_calls:
        <span class="kw">break</span>
    <span class="kw">for</span> tc <span class="kw">in</span> msg.tool_calls:
        result = dispatch(tc.function.name, json.loads(tc.function.arguments))
        messages.append({<span class="st">"role"</span>: <span class="st">"tool"</span>, ...})
    <span class="cm"># 没限次数、没异常兜底、没观测点……</span>

<span class="cm"># MAF：交给 agent.run() / Workflow</span>
agent = Agent(client=client, tools=[get_weather, search_web])
result = <span class="kw">await</span> agent.run(<span class="st">"先查上海天气再给我推荐衣服"</span>)</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">"循环"听着简单，工程化以后要处理：最大迭代数、异常重试、上下文裁剪、并发工具、
        中间件埋点（trace / cost）、多 Agent 之间的消息路由、可恢复的检查点……
        每一项自己实现都是几百行代码、上百个测试用例。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">单 Agent 用内置循环（含 <span class="mono">DEFAULT_MAX_ITERATIONS</span>、
        中间件管道、流式聚合）；多 Agent 用 <span class="mono">agent_framework._workflows</span>
        提供的<strong>图式编排</strong>（节点 / 边 / 共享状态 / 检查点 / 人审），
        和 LangGraph 思想接近，但与 ChatClient、工具、可观测性原生贯通。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>LangGraph</strong>：图式编排鼻祖，与 LangChain 生态深度绑定；<br>
        ② <strong>CrewAI</strong>：角色化多 Agent，编程模型轻但工程化能力弱；<br>
        ③ <strong>手写状态机 / Temporal / Durable Functions</strong>：稳定但与 LLM 语义脱节，要再造一遍工具循环。</div>
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

<details class="accordion">
  <summary><span class="badge-num">2</span> How do you escape vendor lock-in? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Each SDK looks different:
<pre class="code"><span class="cm"># OpenAI</span>
<span class="kw">from</span> openai <span class="kw">import</span> OpenAI
client = OpenAI()
r = client.chat.completions.create(model=<span class="st">"gpt-4o"</span>, messages=[...])

<span class="cm"># Anthropic</span>
<span class="kw">from</span> anthropic <span class="kw">import</span> Anthropic
client = Anthropic()
r = client.messages.create(model=<span class="st">"claude-3-7-sonnet"</span>, max_tokens=1024, messages=[...])</pre>
With MAF only the client swaps; the rest stays:
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
<span class="kw">from</span> agent_framework.openai <span class="kw">import</span> OpenAIChatClient
<span class="cm"># from agent_framework.anthropic import AnthropicClient  # only this line changes</span>
agent = Agent(client=OpenAIChatClient(model=<span class="st">"gpt-4o"</span>), instructions=<span class="st">"…"</span>)
<span class="kw">await</span> agent.run(<span class="st">"hi"</span>)</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Three very real reasons:<br>
        ① <strong>cost</strong> — pricing for the same task differs 5–20× across models;<br>
        ② <strong>fast model turnover</strong> — a new SOTA arrives every quarter; lock-in means missing it;<br>
        ③ <strong>compliance &amp; availability</strong> — finance/gov demand private deployment; some regions need Foundry, others a corporate gateway.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF abstracts every vendor into a uniform <span class="mono">ChatClient</span> interface.
        <span class="mono">FoundryChatClient</span>, <span class="mono">OpenAIChatClient</span>,
        <span class="mono">AnthropicClient</span> and <span class="mono">OllamaChatClient</span> all implement
        the same surface (<span class="mono">get_response()</span>, <span class="mono">get_streaming_response()</span>).
        Agents, tools and workflows depend on the interface only.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>LiteLLM</strong> — external proxy speaking OpenAI's protocol; simple, but one extra hop & service.<br>
        ② <strong>Hand-rolled adapter</strong> — exact fit for your domain, but you maintain streaming/tools/function-call differences.<br>
        ③ <strong>Cloud gateways</strong> (Azure AI Gateway / AWS Bedrock) — great for compliance &amp; quotas, still locks you to one cloud.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> How to assemble conversations safely? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Raw dict vs MAF's typed messages:
<pre class="code"><span class="cm"># Raw dict — typos in "role" only surface at runtime</span>
messages = [
  {<span class="st">"role"</span>: <span class="st">"sytsem"</span>, <span class="st">"content"</span>: <span class="st">"You are helpful"</span>},  <span class="cm"># typo!</span>
  {<span class="st">"role"</span>: <span class="st">"user"</span>,   <span class="st">"content"</span>: <span class="st">"hi"</span>},
]

<span class="cm"># MAF — type-safe, IDE completes everything</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> Message
messages = [
  Message(<span class="st">"system"</span>, <span class="st">"You are helpful"</span>),
  Message(<span class="st">"user"</span>, <span class="st">"hi"</span>),
]</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Real workloads carry more than strings: images, tool calls, tool results, thinking blocks, citations.
        Raw dicts force a project-wide if/else rewrite for each new kind; typed <span class="mono">Content</span>
        means adding a new content type leaves old code untouched.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">See <span class="mono">agent_framework/_types.py</span>: <span class="mono">Role</span> is an enum
        (<span class="mono">system / user / assistant / tool</span>), <span class="mono">Message</span> holds
        <span class="mono">contents: list[Content]</span>, where <span class="mono">Content</span> is
        a unified type built via factory methods like <span class="mono">Content.from_text()</span>.
        Wins: ① static checking + completion; ② multimodal &amp; tool results fit naturally;
        ③ free serialization for Workflow cross-process transport.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>Raw dicts + JSON Schema validation</strong> — light, but still runtime-only;<br>
        ② <strong>Roll your own Pydantic models</strong> — MAF already is Pydantic v2 under the hood, you're reinventing it;<br>
        ③ <strong>LangChain's HumanMessage / AIMessage</strong> — same idea, weaker content-block coverage.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Why not hand-write tool-call JSON? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Raw function-calling vs MAF's <span class="mono">@tool</span>:
<pre class="code"><span class="cm"># Raw SDK: write schema, dispatch, feed result back yourself</span>
tools = [{
  <span class="st">"type"</span>: <span class="st">"function"</span>,
  <span class="st">"function"</span>: {
    <span class="st">"name"</span>: <span class="st">"get_weather"</span>,
    <span class="st">"parameters"</span>: {<span class="st">"type"</span>: <span class="st">"object"</span>,
      <span class="st">"properties"</span>: {<span class="st">"city"</span>: {<span class="st">"type"</span>: <span class="st">"string"</span>}},
      <span class="st">"required"</span>: [<span class="st">"city"</span>]}}}]
<span class="cm"># Then: parse tool_calls → find function → invoke → append result → call again…</span>

<span class="cm"># MAF: decorator generates schema, agent runs the loop</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> tool

<span class="kw">@tool</span>
<span class="kw">def</span> get_weather(city: str) -&gt; str:
    <span class="st">"Return the weather for a city."</span>
    <span class="kw">return</span> f<span class="st">"{city} is 23°C"</span>

agent = Agent(client=client, tools=[get_weather])</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Hand-written JSON schema breeds three bug families: ① parameter names/types drift from the function signature;
        ② you change the function and forget the schema; ③ each vendor supports a different JSON-Schema subset.
        Auto-generation makes the <strong>function the contract</strong>; refactor cost goes to zero.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">@tool</span> (see <span class="mono">_tools.py</span>) uses
        <span class="mono">inspect</span> + type hints to produce a JSON Schema, auto-injects it into ChatClient requests;
        when the model returns <span class="mono">FunctionCallContent</span>, the Agent — in the
        <strong>same loop</strong> — executes the function, appends <span class="mono">FunctionResultContent</span>
        to the messages, and calls the model again. No glue code from you.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>Hand-written schema</strong> — max control, max error rate;<br>
        ② <strong>OpenAI's official function-calling SDK</strong> — OpenAI-only;<br>
        ③ <strong>LangChain Tool / StructuredTool</strong> — similar idea, no native middleware/Workflow integration;<br>
        ④ <strong>MCP protocol</strong> — out-of-process tool hosting; MAF can also surface MCP tools as local ones.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> Multi-step &amp; multi-agent without a while-monster? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Hand-rolled loops go bad fast:
<pre class="code">messages = [...]
<span class="kw">while</span> True:
    resp = client.chat.completions.create(model=..., messages=messages, tools=tools)
    msg = resp.choices[0].message
    <span class="kw">if</span> <span class="kw">not</span> msg.tool_calls:
        <span class="kw">break</span>
    <span class="kw">for</span> tc <span class="kw">in</span> msg.tool_calls:
        result = dispatch(tc.function.name, json.loads(tc.function.arguments))
        messages.append({<span class="st">"role"</span>: <span class="st">"tool"</span>, ...})
    <span class="cm"># No max iterations, no retries, no observability…</span>

<span class="cm"># MAF: delegated to agent.run() / Workflow</span>
agent = Agent(client=client, tools=[get_weather, search_web])
result = <span class="kw">await</span> agent.run(<span class="st">"Check Shanghai weather then suggest what to wear"</span>)</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">"Loop" sounds simple. Productionizing it requires max-iteration limits, retries on errors,
        context trimming, parallel tools, middleware hooks (trace/cost), inter-agent message routing,
        resumable checkpoints… each item is hundreds of lines and many tests.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Single agent → built-in loop with <span class="mono">DEFAULT_MAX_ITERATIONS</span>, middleware pipeline
        and streaming aggregation; multi-agent → <span class="mono">agent_framework._workflows</span> provides
        <strong>graph orchestration</strong> (nodes / edges / shared state / checkpoints / human approval),
        natively wired with ChatClient, tools and observability.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>LangGraph</strong> — original graph orchestrator, tightly coupled to LangChain;<br>
        ② <strong>CrewAI</strong> — role-based multi-agent; ergonomic but light on productionization;<br>
        ③ <strong>Hand-rolled state machines / Temporal / Durable Functions</strong> — robust but disconnected from LLM semantics, you rebuild the tool loop yourself.</div>
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

<details class="accordion">
  <summary><span class="badge-num">1</span> core 包里到底有什么？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">core 一个文件一个职责，地图大致如下：
<pre class="code">python/packages/core/agent_framework/
├── _agents.py        <span class="cm"># Agent 类、run() 循环、DEFAULT_MAX_ITERATIONS</span>
├── _clients.py       <span class="cm"># BaseChatClient 抽象基类 + Supports* 协议族</span>
├── _tools.py         <span class="cm"># @tool 装饰器、FunctionTool 类</span>
├── _middleware.py    <span class="cm"># 中间件管道：trace / retry / 自定义</span>
├── _types.py         <span class="cm"># Message / Role / Content 联合类型</span>
├── _workflows/       <span class="cm"># 图式编排：节点、边、共享状态、检查点</span>
├── observability/    <span class="cm"># OpenTelemetry trace / cost / token 指标</span>
└── __init__.py       <span class="cm"># 公共 API，决定 from agent_framework import 什么</span></pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">如果 core 拆成几十个小包，新人要在第一周里学几十个 import 路径；
        如果塞成一个 god-module，又会出现循环依赖、加载慢、测试难。
        "单包多文件"是大型框架最常见且最稳的折中：<strong>一个 import 路径、清晰的内部分层</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">所有抽象统一从 <span class="mono">agent_framework</span> 导出（<span class="mono">Agent</span>、
        <span class="mono">Message</span>、<span class="mono">tool</span>、
        <span class="mono">WorkflowBuilder</span>……）；文件命名以 <span class="mono">_</span> 前缀表示"内部"，
        通过 <span class="mono">__init__.py</span> 的 <span class="mono">__all__</span> 再暴露——
        重构内部不影响用户代码。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>单文件 god-module</strong>：上手最快，长期维护灾难；<br>
        ② <strong>微包架构</strong>（每个抽象一个 PyPI 包）：依赖管理噩梦；<br>
        ③ <strong>plugin-only</strong>：core 只有接口，所有实现都是插件——灵活但缺少"开箱即用"的体验。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> provider 包的懒加载是怎么工作的？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">子模块 <span class="mono">__init__.py</span> 用 <span class="mono">__getattr__</span> 延迟拉依赖：
<pre class="code"><span class="cm"># agent_framework/openai/__init__.py（示意）</span>
<span class="kw">import</span> importlib
<span class="kw">from</span> typing <span class="kw">import</span> TYPE_CHECKING

<span class="kw">if</span> TYPE_CHECKING:
    <span class="kw">from</span> ._chat_client <span class="kw">import</span> OpenAIChatClient

_LAZY = {<span class="st">"OpenAIChatClient"</span>: <span class="st">"._chat_client"</span>}

<span class="kw">def</span> __getattr__(name: str):
    <span class="kw">if</span> name <span class="kw">in</span> _LAZY:
        mod = importlib.import_module(_LAZY[name], __name__)
        <span class="kw">return</span> getattr(mod, name)
    <span class="kw">raise</span> AttributeError(name)

__all__ = list(_LAZY)</pre>
所以 <span class="mono">import agent_framework</span> 不会拉起 <span class="mono">openai</span> 的 SDK；
只有真的访问 <span class="mono">OpenAIChatClient</span> 时才装载。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">① <strong>启动速度</strong>：每多一个 SDK 启动就慢几十到几百毫秒，CLI / Serverless 场景极敏感；<br>
        ② <strong>可选依赖</strong>：用户只装了 OpenAI 包，不应该被 Anthropic 的 import 错误打断；<br>
        ③ <strong>安装体积</strong>：core 保持最小依赖，按需安装 extras（<span class="mono">pip install agent-framework[azure]</span>）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">采用 PEP 562 的模块级 <span class="mono">__getattr__</span> + <span class="mono">TYPE_CHECKING</span>
        守护的真实 import，对 IDE 与 mypy 完全友好；既保留懒加载，又能拿到完整类型提示。
        Pyright/PyCharm 都能正确跳转。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>急加载（eager）</strong>：简单，但启动慢、依赖污染；<br>
        ② <strong>entry_points / 插件协议</strong>：解耦得更彻底，但发现成本和调试难度上升；<br>
        ③ <strong>try / except ImportError</strong>：常见小技巧，规模一大就乱。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Python 与 .NET 是怎么"对齐"的？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">同一个概念，两种语法：
<pre class="code"><span class="cm"># Python</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
<span class="kw">from</span> agent_framework.openai <span class="kw">import</span> OpenAIChatClient
agent = Agent(
    client=OpenAIChatClient(model=<span class="st">"gpt-4o"</span>),
    name=<span class="st">"weather-bot"</span>,
    instructions=<span class="st">"你是天气助手"</span>,
)
<span class="kw">await</span> agent.run(<span class="st">"上海明天天气？"</span>)</pre>
<pre class="code"><span class="cm">// C#</span>
<span class="kw">using</span> Microsoft.Agents.AI;
<span class="kw">using</span> Microsoft.Agents.AI.OpenAI;

<span class="kw">var</span> agent = <span class="kw">new</span> ChatClientAgent(
    chatClient: <span class="kw">new</span> OpenAIChatClient(<span class="st">"gpt-4o"</span>),
    name: <span class="st">"weather-bot"</span>,
    instructions: <span class="st">"You are a weather assistant"</span>);
<span class="kw">var</span> result = <span class="kw">await</span> agent.RunAsync(<span class="st">"Weather in Shanghai?"</span>);</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">真实企业里：算法 / 数据团队偏 Python，业务后端常是 .NET。
        如果两边概念不一样，团队沟通靠翻译，文档要写两份，迁移代价巨大。
        "API 对齐"意味着<strong>看一份文档能让两边都开工</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">两套实现在概念、命名、生命周期上对齐：同样的 Agent / ChatClient / Tool / Workflow，
        同样的 run / stream / observability hook；只在语法上接受各自语言的惯用法（async/await、
        装饰器 vs Attribute、强类型 vs 类型注解）。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>只做一种语言</strong>：错过另一半市场；<br>
        ② <strong>从 IDL / proto 自动生成</strong>：易过度抽象，丢掉语言惯用法；<br>
        ③ <strong>FFI / 包装</strong>（Python 调 .NET DLL 或反过来）：部署与诊断复杂。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> .NET 那边的命名怎么对应？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">两边主要符号对照表：
<table class="t">
  <tr><th>Python</th><th>.NET</th><th>含义</th></tr>
  <tr><td class="mono">agent_framework</td><td class="mono">Microsoft.Agents.AI</td><td>核心包</td></tr>
  <tr><td class="mono">Agent</td><td class="mono">ChatClientAgent</td><td>Agent 实体（带循环）</td></tr>
  <tr><td class="mono">ChatClient</td><td class="mono">IChatClient</td><td>厂商无关客户端</td></tr>
  <tr><td class="mono">Message / Role</td><td class="mono">Message / ChatRole</td><td>类型化消息</td></tr>
  <tr><td class="mono">@tool</td><td class="mono">[Description] + AIFunctionFactory</td><td>把函数转成工具</td></tr>
  <tr><td class="mono">_workflows/</td><td class="mono">Microsoft.Agents.AI.Workflows</td><td>图式编排</td></tr>
  <tr><td class="mono">observability/</td><td class="mono">Microsoft.Extensions.AI.Telemetry</td><td>OTel 集成</td></tr>
  <tr><td class="mono">agent.run() / .run_stream()</td><td class="mono">RunAsync() / RunStreamingAsync()</td><td>同步与流式入口</td></tr>
</table></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">命名对齐 = <strong>认知对齐</strong>：你在 Python 里学到的 "ChatClient 是厂商抽象"
        会自动迁移到 .NET 同事身上；团队搜文档、做 code review、做迁移都受益。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">命名表存在 <span class="mono">docs/decisions</span> 的 ADR 里，
        新功能必须同时在两端落地，否则不发布；这让"读 Python 教程顺带学 .NET"成为现实。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>纯惯用法命名</strong>（Pythonic vs C#-ic 各走各的）：阅读时永远要做心理翻译；<br>
        ② <strong>从 IDL 生成绑定</strong>：命名一致但不一定符合语言习惯；<br>
        ③ <strong>共享 IDL 文档但代码独立</strong>：折中方案，MAF 实际就在向这个方向靠拢。</div>
    </div>
  </div>
</details>

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

<details class="accordion">
  <summary><span class="badge-num">1</span> What lives inside the core package? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">core is "one file, one job":
<pre class="code">python/packages/core/agent_framework/
├── _agents.py        <span class="cm"># Agent class, run() loop, DEFAULT_MAX_ITERATIONS</span>
├── _clients.py       <span class="cm"># BaseChatClient ABC + Supports* protocols</span>
├── _tools.py         <span class="cm"># @tool decorator, FunctionTool class</span>
├── _middleware.py    <span class="cm"># middleware pipeline: trace / retry / custom</span>
├── _types.py         <span class="cm"># Message / Role / Content union</span>
├── _workflows/       <span class="cm"># graph orchestration: nodes, edges, state, checkpoints</span>
├── observability/    <span class="cm"># OpenTelemetry traces / cost / token metrics</span>
└── __init__.py       <span class="cm"># public API — what `from agent_framework import` exposes</span></pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">If core is split into dozens of micro-packages, newcomers spend their first week learning imports;
        if it's a single god-module, you get circular deps, slow loads and untestable seams.
        "Single package, many internal files" is the standard, stable compromise:
        <strong>one import path, clean inner layering</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">All abstractions are re-exported from <span class="mono">agent_framework</span>
        (<span class="mono">Agent</span>, <span class="mono">Message</span>, <span class="mono">tool</span>,
        <span class="mono">WorkflowBuilder</span>…); files prefixed with <span class="mono">_</span> are internal and
        surfaced via <span class="mono">__all__</span> in <span class="mono">__init__.py</span> — internal refactors
        never break user code.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>Single-file god-module</strong> — fastest start, long-term disaster;<br>
        ② <strong>Micro-package architecture</strong> (one PyPI package per abstraction) — dependency hell;<br>
        ③ <strong>Plugin-only</strong> — core ships interfaces, everything else is a plugin; flexible, no batteries included.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> How does provider lazy-loading actually work? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Submodule <span class="mono">__init__.py</span> defers imports with <span class="mono">__getattr__</span>:
<pre class="code"><span class="cm"># agent_framework/openai/__init__.py (sketch)</span>
<span class="kw">import</span> importlib
<span class="kw">from</span> typing <span class="kw">import</span> TYPE_CHECKING

<span class="kw">if</span> TYPE_CHECKING:
    <span class="kw">from</span> ._chat_client <span class="kw">import</span> OpenAIChatClient

_LAZY = {<span class="st">"OpenAIChatClient"</span>: <span class="st">"._chat_client"</span>}

<span class="kw">def</span> __getattr__(name: str):
    <span class="kw">if</span> name <span class="kw">in</span> _LAZY:
        mod = importlib.import_module(_LAZY[name], __name__)
        <span class="kw">return</span> getattr(mod, name)
    <span class="kw">raise</span> AttributeError(name)

__all__ = list(_LAZY)</pre>
So <span class="mono">import agent_framework</span> doesn't drag in the <span class="mono">openai</span> SDK;
it loads only when you actually touch <span class="mono">OpenAIChatClient</span>.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">① <strong>Startup speed</strong> — each extra SDK adds tens-to-hundreds of ms; critical for CLI &amp; serverless;<br>
        ② <strong>Optional dependencies</strong> — a user who only installed the OpenAI extras shouldn't crash on Anthropic imports;<br>
        ③ <strong>Install size</strong> — core stays minimal, extras opt-in via <span class="mono">pip install agent-framework[azure]</span>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">PEP 562 module-level <span class="mono">__getattr__</span> combined with a <span class="mono">TYPE_CHECKING</span>-guarded
        real import — keeps lazy semantics at runtime while preserving full IDE / mypy navigation.
        Pyright and PyCharm jump-to-definition still work.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>Eager imports</strong> — simple but slow + polluted deps;<br>
        ② <strong>entry_points / plugin protocol</strong> — full decoupling, harder discovery &amp; debugging;<br>
        ③ <strong>try/except ImportError</strong> — common trick, doesn't scale to many providers.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> How are Python and .NET kept "aligned"? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Same concept, two syntaxes:
<pre class="code"><span class="cm"># Python</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
<span class="kw">from</span> agent_framework.openai <span class="kw">import</span> OpenAIChatClient
agent = Agent(
    client=OpenAIChatClient(model=<span class="st">"gpt-4o"</span>),
    name=<span class="st">"weather-bot"</span>,
    instructions=<span class="st">"You are a weather assistant"</span>,
)
<span class="kw">await</span> agent.run(<span class="st">"Shanghai weather tomorrow?"</span>)</pre>
<pre class="code"><span class="cm">// C#</span>
<span class="kw">using</span> Microsoft.Agents.AI;
<span class="kw">using</span> Microsoft.Agents.AI.OpenAI;

<span class="kw">var</span> agent = <span class="kw">new</span> ChatClientAgent(
    chatClient: <span class="kw">new</span> OpenAIChatClient(<span class="st">"gpt-4o"</span>),
    name: <span class="st">"weather-bot"</span>,
    instructions: <span class="st">"You are a weather assistant"</span>);
<span class="kw">var</span> result = <span class="kw">await</span> agent.RunAsync(<span class="st">"Shanghai weather?"</span>);</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">In real enterprises, ML/data teams prefer Python while business backends are often .NET.
        If concepts diverge, communication becomes translation, docs are written twice and migrations are painful.
        Alignment means <strong>one set of docs powers both sides</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Both implementations align on concepts, naming and lifecycle: same Agent / ChatClient / Tool / Workflow,
        same run / stream / observability hooks; only the syntax follows local idioms (async/await, decorators vs
        attributes, type hints vs strong static types).</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>Single language only</strong> — miss half the market;<br>
        ② <strong>Auto-generate from IDL / proto</strong> — easy to over-abstract, fights idioms;<br>
        ③ <strong>FFI / wrappers</strong> (Python calls .NET DLLs or vice versa) — deployment &amp; debugging nightmares.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> .NET naming correspondence <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Main symbol map:
<table class="t">
  <tr><th>Python</th><th>.NET</th><th>Meaning</th></tr>
  <tr><td class="mono">agent_framework</td><td class="mono">Microsoft.Agents.AI</td><td>core package</td></tr>
  <tr><td class="mono">Agent</td><td class="mono">ChatClientAgent</td><td>agent entity (with loop)</td></tr>
  <tr><td class="mono">ChatClient</td><td class="mono">IChatClient</td><td>vendor-agnostic client</td></tr>
  <tr><td class="mono">Message / Role</td><td class="mono">Message / ChatRole</td><td>typed messages</td></tr>
  <tr><td class="mono">@tool</td><td class="mono">[Description] + AIFunctionFactory</td><td>turn function into tool</td></tr>
  <tr><td class="mono">_workflows/</td><td class="mono">Microsoft.Agents.AI.Workflows</td><td>graph orchestration</td></tr>
  <tr><td class="mono">observability/</td><td class="mono">Microsoft.Extensions.AI.Telemetry</td><td>OTel integration</td></tr>
  <tr><td class="mono">agent.run() / .run_stream()</td><td class="mono">RunAsync() / RunStreamingAsync()</td><td>sync &amp; streaming entry</td></tr>
</table></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Naming alignment = <strong>mental-model alignment</strong>: what you learn in Python
        ("ChatClient is the vendor abstraction") transfers directly to your .NET teammates.
        Doc search, code review and migration all benefit.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">The naming table lives in ADRs under <span class="mono">docs/decisions</span>;
        new features must land in both implementations or they don't ship — making
        "reading the Python tutorial also teaches you .NET" a real outcome.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>Pure idiomatic naming on both sides</strong> — readers translate forever;<br>
        ② <strong>IDL-generated bindings</strong> — uniform names, often unidiomatic;<br>
        ③ <strong>Shared IDL docs, independent code</strong> — pragmatic middle ground, what MAF is gradually moving toward.</div>
    </div>
  </div>
</details>

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
session = agent.create_session()
<span class="kw">await</span> agent.run(<span class="st">"我叫小明"</span>, session=session)
<span class="kw">await</span> agent.run(<span class="st">"我叫什么？"</span>, session=session)  <span class="cm"># 记得"小明"</span></pre>
        <em>（会话与记忆见第 07 课，这里只需知道历史是"会话"携带的。）</em></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 消息到底是怎么组装的？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">一次 <span class="mono">run()</span> 实际发给 LLM 的列表大致长这样：
<pre class="code">[
  SystemMessage(<span class="st">"你是天气助手，回答尽量简短。"</span>),   <span class="cm"># ← instructions</span>
  UserMessage(<span class="st">"我叫小明"</span>),                       <span class="cm"># ← 历史 1</span>
  AssistantMessage(<span class="st">"你好，小明！"</span>),               <span class="cm"># ← 历史 2</span>
  UserMessage(<span class="st">"上海今天天气？"</span>),                  <span class="cm"># ← 本次输入</span>
]
tools = [
  {<span class="st">"name"</span>: <span class="st">"get_weather"</span>,  <span class="st">"parameters"</span>: {...}},  <span class="cm"># ← 自动生成</span>
]</pre>
其中 instructions 在最前、历史按时间顺序、当前输入在最后、工具 schema 作为请求字段并行附带。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">三个隐藏陷阱：① <strong>system 位置</strong>——某些模型对 system 必须放首；
        ② <strong>上下文窗口预算</strong>——历史 + 工具 schema + 输入加起来不能超 token 上限；
        ③ <strong>工具 schema 开销</strong>——20 个工具就能吃掉几千 token。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">Agent 在 <span class="mono">_agents.py</span> 中按固定顺序拼装：
        <span class="mono">instructions → system</span>、<span class="mono">tools → schema</span>、
        <span class="mono">history → ordered messages</span>，并把 ChatClient 不支持的内容（如多模态）做 fallback。
        用户只关心业务输入，组装细节由框架兜底。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>完全手动拼装</strong>：最灵活，最容易踩坑；<br>
        ② <strong>模板化（Jinja / Handlebars）</strong>：适合 prompt-engineering 重度场景，但失去类型约束；<br>
        ③ <strong>纯中间件流水线</strong>：把每一步当 middleware 拼起来，灵活但调试链路长。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 工具循环的边界在哪？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">Agent 内置了一个迭代上限，撞到就停：
<pre class="code"><span class="cm"># agent_framework/_agents.py</span>
DEFAULT_MAX_ITERATIONS = 10

<span class="kw">class</span> Agent:
    <span class="kw">def</span> __init__(self, ..., max_iterations: int = DEFAULT_MAX_ITERATIONS):
        self.max_iterations = max_iterations

    <span class="kw">async def</span> run(self, input, ...):
        <span class="kw">for</span> i <span class="kw">in</span> range(self.max_iterations):
            resp = <span class="kw">await</span> self._client.get_response(...)
            <span class="kw">if</span> <span class="kw">not</span> _has_tool_calls(resp):
                <span class="kw">return</span> AgentResponse(...)
            <span class="kw">await</span> self._execute_tools(resp)
        <span class="cm"># 达到上限：返回带告警的部分结果</span>
        <span class="kw">return</span> AgentResponse(..., terminated_reason=<span class="st">"max_iterations"</span>)</pre>
按需调高：<span class="mono">Agent(..., max_iterations=20)</span>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">没有上限的循环 = <strong>账单炸弹</strong>：模型可能把同一个工具反复调用、互相依赖死锁、
        或被 prompt injection 牵着鼻子走。即便用例正常，也要有止损线。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">默认 <span class="mono">DEFAULT_MAX_ITERATIONS</span> 给出安全值，可按 Agent 覆写；
        终止时返回结构化的 <span class="mono">terminated_reason</span>，方便上层判断"重试 / 升级 / 报错"，
        而不是直接 raise。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>不设上限</strong>：极端危险；<br>
        ② <strong>按 token 预算</strong>：更经济但实现复杂；<br>
        ③ <strong>按墙钟超时</strong>：保护延迟敏感场景；<br>
        ④ <strong>每步人工确认</strong>：成本最高但安全（金融 / 医疗常用），MAF 也可通过 Workflow 的 human approval 实现。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 流式 vs 非流式内部差异 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">同一个 Agent，两种入口：
<pre class="code"><span class="cm"># 非流式：一次性拿完整结果</span>
result: AgentResponse = <span class="kw">await</span> agent.run(<span class="st">"写一首关于秋天的诗"</span>)
print(result.text)

<span class="cm"># 流式：逐块拿 AgentResponseUpdate</span>
<span class="kw">async for</span> update <span class="kw">in</span> agent.run_stream(<span class="st">"写一首关于秋天的诗"</span>):
    <span class="kw">if</span> update.text:
        print(update.text, end=<span class="st">""</span>, flush=True)</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">① <strong>首字延迟</strong>：长回答里用户最敏感的是"开始出字"的时间；<br>
        ② <strong>长回答 UX</strong>：不流式时，等 30s 一片黑屏；流式则像打字机；<br>
        ③ <strong>调试与中断</strong>：流式可早期发现跑偏，及时取消。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">同一个 Agent、同一组工具，<span class="mono">run()</span> 返回完整 <span class="mono">AgentResponse</span>；
        <span class="mono">run_stream()</span> 返回 <span class="mono">AsyncIterable[AgentResponseUpdate]</span>，
        把内容、工具调用、思维块都分块吐出，且内部已对齐为同一种循环——
        切换流式不需要重写业务逻辑。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>纯 SSE 推流</strong>：协议简单，但要自己实现重连和心跳；<br>
        ② <strong>WebSocket</strong>：双向通信，对实时交互更好；<br>
        ③ <strong>轮询</strong>：兼容性最强，体验最差；<br>
        ④ <strong>客户端缓冲</strong>：在前端把 chunk 拼回完整文本，MAF 同时支持。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> 错误处理：循环里出错怎么办？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">三类典型故障：
<pre class="code"><span class="cm"># 1) LLM 端报错：429 / 500 / timeout</span>
<span class="cm">   → ChatClient 抛出 ChatClientError</span>

<span class="cm"># 2) 工具函数抛异常</span>
<span class="kw">@tool</span>
<span class="kw">def</span> get_weather(city: str) -&gt; str:
    <span class="kw">raise</span> RuntimeError(<span class="st">"weather API down"</span>)
<span class="cm">   → Agent 捕获后包成 FunctionResultContent(error=...)</span>
<span class="cm">     交回模型，让它决定降级、换工具或道歉</span>

<span class="cm"># 3) 工具执行超时</span>
<span class="cm">   → 中间件层兜底，写入 trace span</span></pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">Agent 循环里出错时，"重试 / 跳过 / 放弃 / 返回部分结果"的取舍每种都合理，
        没有银弹。框架必须给一个<strong>有结构、可定制</strong>的失败模型，否则要么过度吞错、要么动不动崩溃。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">错误走中间件管道（<span class="mono">_middleware.py</span>）：用户可注册重试策略、
        熔断、降级；工具异常被包成 <span class="mono">FunctionResultContent</span> 回灌模型；
        无法恢复时 <span class="mono">AgentResponse</span> 上带 <span class="mono">terminated_reason</span>
        和原始异常链，便于上层结构化处理。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">① <strong>到处 try/except</strong>：写起来快，可观测性几乎为零；<br>
        ② <strong>熔断器（circuit breaker）</strong>：保护下游，但要小心误熔断；<br>
        ③ <strong>let-it-crash（Erlang 风格）</strong>：失败重启整个 Agent，靠上游 retry——简单但成本高。</div>
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
session = agent.create_session()
<span class="kw">await</span> agent.run(<span class="st">"My name is Sam"</span>, session=session)
<span class="kw">await</span> agent.run(<span class="st">"What's my name?"</span>, session=session)  <span class="cm"># remembers "Sam"</span></pre>
        <em>(Sessions & memory are Lesson 07; here just note history rides on the "session".)</em></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> What does message assembly actually look like? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">The list sent to the LLM on one <span class="mono">run()</span> roughly looks like:
<pre class="code">[
  SystemMessage(<span class="st">"You are a concise weather assistant."</span>),  <span class="cm"># ← instructions</span>
  UserMessage(<span class="st">"My name is Sam"</span>),                          <span class="cm"># ← history 1</span>
  AssistantMessage(<span class="st">"Hi Sam!"</span>),                             <span class="cm"># ← history 2</span>
  UserMessage(<span class="st">"Weather in Shanghai today?"</span>),               <span class="cm"># ← this input</span>
]
tools = [
  {<span class="st">"name"</span>: <span class="st">"get_weather"</span>, <span class="st">"parameters"</span>: {...}},   <span class="cm"># ← auto-generated</span>
]</pre>
Instructions go first, history in chronological order, current input last, tool schemas attached alongside.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Three hidden traps: ① <strong>system position</strong> — some models require system at index 0;
        ② <strong>context-window budget</strong> — history + tool schema + input must fit in the token cap;
        ③ <strong>tool-schema overhead</strong> — 20 tools can eat several thousand tokens.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">In <span class="mono">_agents.py</span> the Agent assembles in a fixed order:
        <span class="mono">instructions → system</span>, <span class="mono">tools → schema</span>,
        <span class="mono">history → ordered messages</span>, with fallbacks for content kinds a ChatClient doesn't support.
        Callers only think about business input; assembly is the framework's job.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>Fully manual assembly</strong> — maximum flexibility, maximum footguns;<br>
        ② <strong>Templated (Jinja / Handlebars)</strong> — great for prompt-heavy workflows, loses type safety;<br>
        ③ <strong>Pure middleware pipeline</strong> — every step as middleware; flexible but long debug chain.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Where does the tool loop stop? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">The Agent ships with an iteration cap that breaks the loop:
<pre class="code"><span class="cm"># agent_framework/_agents.py</span>
DEFAULT_MAX_ITERATIONS = 10

<span class="kw">class</span> Agent:
    <span class="kw">def</span> __init__(self, ..., max_iterations: int = DEFAULT_MAX_ITERATIONS):
        self.max_iterations = max_iterations

    <span class="kw">async def</span> run(self, input, ...):
        <span class="kw">for</span> i <span class="kw">in</span> range(self.max_iterations):
            resp = <span class="kw">await</span> self._client.get_response(...)
            <span class="kw">if</span> <span class="kw">not</span> _has_tool_calls(resp):
                <span class="kw">return</span> AgentResponse(...)
            <span class="kw">await</span> self._execute_tools(resp)
        <span class="cm"># Cap hit: return a partial result with a reason</span>
        <span class="kw">return</span> AgentResponse(..., terminated_reason=<span class="st">"max_iterations"</span>)</pre>
Tune per agent: <span class="mono">Agent(..., max_iterations=20)</span>.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Uncapped loops = <strong>bill explosion</strong>: a model can re-call the same tool forever,
        deadlock between dependent tools, or be steered by prompt injection. Even normal usage needs a stop-loss.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Default <span class="mono">DEFAULT_MAX_ITERATIONS</span> ships a sane value, overridable per Agent;
        when it trips, the call returns a structured <span class="mono">terminated_reason</span> instead of raising —
        upper layers can choose to retry, escalate or surface an error.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>No limit</strong> — outright dangerous;<br>
        ② <strong>Token-budget based</strong> — more economical, harder to implement;<br>
        ③ <strong>Wall-clock timeout</strong> — protects latency-sensitive paths;<br>
        ④ <strong>Human approval per iteration</strong> — most expensive, safest (finance/medical); also doable via Workflow human approval.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Streaming vs non-streaming internals <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Same Agent, two entry points:
<pre class="code"><span class="cm"># Non-streaming: one full result</span>
result: AgentResponse = <span class="kw">await</span> agent.run(<span class="st">"Write a short autumn poem"</span>)
print(result.text)

<span class="cm"># Streaming: AgentResponseUpdate chunks</span>
<span class="kw">async for</span> update <span class="kw">in</span> agent.run_stream(<span class="st">"Write a short autumn poem"</span>):
    <span class="kw">if</span> update.text:
        print(update.text, end=<span class="st">""</span>, flush=True)</pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">① <strong>Time-to-first-token</strong> matters most for long answers;<br>
        ② <strong>UX</strong> — non-streamed long answers feel like a 30-second freeze; streaming feels like a typewriter;<br>
        ③ <strong>Early debugging / cancellation</strong> — streaming lets you spot drift early and abort.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Same Agent, same tools: <span class="mono">run()</span> returns a complete <span class="mono">AgentResponse</span>;
        <span class="mono">run_stream()</span> returns <span class="mono">AsyncIterable[AgentResponseUpdate]</span>,
        emitting text, tool calls and thinking blocks as chunks — all over the same internal loop, so switching
        modes doesn't change your business code.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>Pure SSE push</strong> — simple protocol, you handle reconnect &amp; heartbeats;<br>
        ② <strong>WebSocket</strong> — bidirectional, better for live interaction;<br>
        ③ <strong>Polling</strong> — broadest compatibility, worst UX;<br>
        ④ <strong>Client-side buffering</strong> — reassemble chunks into final text on the client; MAF supports this too.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> Error handling inside the loop <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Three classic failures:
<pre class="code"><span class="cm"># 1) LLM-side error: 429 / 500 / timeout</span>
<span class="cm">   → ChatClient raises ChatClientError</span>

<span class="cm"># 2) Tool function raises</span>
<span class="kw">@tool</span>
<span class="kw">def</span> get_weather(city: str) -&gt; str:
    <span class="kw">raise</span> RuntimeError(<span class="st">"weather API down"</span>)
<span class="cm">   → Agent wraps it as FunctionResultContent(error=...),</span>
<span class="cm">     hands it back to the model to degrade or apologize</span>

<span class="cm"># 3) Tool execution timeout</span>
<span class="cm">   → middleware layer catches, writes a trace span</span></pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Inside an agent loop, "retry / skip / abort / partial" can all be the right call — there's no silver bullet.
        The framework has to provide a <strong>structured, customizable</strong> failure model, or you'll either
        swallow errors silently or crash constantly.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Errors flow through the middleware pipeline (<span class="mono">_middleware.py</span>):
        users register retry policies, circuit breakers, fallbacks; tool exceptions become
        <span class="mono">FunctionResultContent</span> fed back to the model; unrecoverable failures surface on
        <span class="mono">AgentResponse</span> with a <span class="mono">terminated_reason</span> and original exception chain
        for structured upstream handling.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">① <strong>try/except everywhere</strong> — fast to write, near-zero observability;<br>
        ② <strong>Circuit breaker</strong> — protects downstream, watch for false trips;<br>
        ③ <strong>Let-it-crash (Erlang style)</strong> — restart the agent on failure, rely on upstream retries — simple but costly.</div>
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
