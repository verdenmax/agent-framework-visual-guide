"""Content for Part 3 (internals): lessons 08-14 — Chinese + English."""

# ---------------------------------------------------------------------------
L08_ZH = r"""
<p class="lead">你用的 <span class="inline">Agent</span> 背后有两层：最底层是抽象基类
<span class="inline">BaseAgent</span>，上面是具体类 <span class="inline">Agent</span>。
了解这两层，才看得懂框架如何"驱动"一个 Agent 跑完整个循环。</p>

<div class="card analogy">
  <div class="tag">🏗️ 生活类比</div>
  <span class="mono">BaseAgent</span> 像一份<strong>岗位说明书</strong>（"你要能接单、能跑、能交付"），
  <span class="mono">Agent</span> 则是<strong>真人上岗</strong>——读说明书、准备工具箱、接单后反复跑腿，直到任务完成。
</div>

<h2>两层结构</h2>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">抽象</span><span class="name">BaseAgent</span></div>
    <div class="ld">定义 <span class="mono">run()</span> 协议与扩展点（<span class="mono">_agents.py:314</span>）。
    所有 Agent 必须实现这份"合同"。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">具体</span><span class="name">Agent</span></div>
    <div class="ld">组装 instructions + 消息 + 工具 → 调 ChatClient → 工具循环 → 返回
    <span class="mono">AgentResponse</span>（<span class="mono">_agents.py:1584</span>）。</div></div>
</div>

<h2>run() 内部做了什么</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>构建消息列表</h4>
    <p>把 <span class="mono">instructions</span>（system）+ 会话历史 + 新输入拼起来。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>注入 ContextProvider</h4>
    <p>把长期记忆 / 外部知识塞进上下文。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>调用 ChatClient</h4>
    <p>把消息 + 工具 schema 发给 LLM，拿回 <span class="mono">ChatResponse</span>。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>工具循环</h4>
    <p>若回复含 <span class="mono">function_call</span>，执行工具、追加结果、再回第 3 步。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>返回</h4>
    <p>循环结束，包装成 <span class="mono">AgentResponse</span>（或逐块 <span class="mono">AgentResponseUpdate</span>）。</p></div></div>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> BaseAgent 定义了哪些接口？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 核心协议</div>
      <div class="a"><span class="mono">BaseAgent</span> 规定了 <span class="mono">run()</span>（非流式 + 流式共用）、
        <span class="mono">create_session()</span>、<span class="mono">get_session()</span> 等。
        子类只需关注"怎么组装消息、怎么调模型"——循环骨架已由基类搭好。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><span class="mono">BaseAgent</span>（抽象）定义协议；<span class="mono">Agent</span>（具体）实现组装 + 循环。</li>
    <li><span class="mono">run()</span> = 构建消息 → 注入上下文 → 调 ChatClient → 工具循环 → 返回。</li>
    <li>返回类型：非流式 <span class="mono">AgentResponse</span>；流式 <span class="mono">AgentResponseUpdate</span>。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>循环骨架由基类掌控</strong>，子类只插入"怎么调模型"这一块——经典的<strong>模板方法模式</strong>。
  这意味着你可以自定义 Agent 行为而不破坏循环逻辑。
</div>
"""

L08_EN = r"""
<p class="lead">The <span class="inline">Agent</span> you use has two layers: the abstract
<span class="inline">BaseAgent</span> at the bottom, and the concrete <span class="inline">Agent</span> on top.
Understand them and you'll see how the framework drives an agent through its full loop.</p>

<div class="card analogy">
  <div class="tag">🏗️ Analogy</div>
  <span class="mono">BaseAgent</span> is a <strong>job description</strong> ("you must take orders, run errands,
  deliver results"); <span class="mono">Agent</span> is the <strong>person on duty</strong> — reads the description,
  packs the toolkit, takes orders and runs errands in a loop until the task is done.
</div>

<h2>Two layers</h2>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">Abstract</span><span class="name">BaseAgent</span></div>
    <div class="ld">Defines the <span class="mono">run()</span> protocol and extension points (<span class="mono">_agents.py:314</span>).
    Every Agent must fulfil this "contract".</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Concrete</span><span class="name">Agent</span></div>
    <div class="ld">Assembles instructions + messages + tools → calls ChatClient → tool loop → returns
    <span class="mono">AgentResponse</span> (<span class="mono">_agents.py:1584</span>).</div></div>
</div>

<h2>What run() does inside</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Build message list</h4>
    <p>Concatenate <span class="mono">instructions</span> (system) + session history + new input.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Inject ContextProviders</h4>
    <p>Splice long-term memory / external knowledge into the context.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Call ChatClient</h4>
    <p>Send messages + tool schemas to the LLM, get back a <span class="mono">ChatResponse</span>.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Tool loop</h4>
    <p>If the reply contains a <span class="mono">function_call</span>, execute the tool, append the result, loop to step 3.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Return</h4>
    <p>Loop ends; wrap into <span class="mono">AgentResponse</span> (or stream <span class="mono">AgentResponseUpdate</span> chunks).</p></div></div>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> What does BaseAgent define? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 Core protocol</div>
      <div class="a"><span class="mono">BaseAgent</span> mandates <span class="mono">run()</span> (shared by streaming
        and non-streaming), <span class="mono">create_session()</span>, <span class="mono">get_session()</span>, etc.
        Subclasses only focus on "how to assemble messages and call the model" — the loop skeleton is already in the base.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><span class="mono">BaseAgent</span> (abstract) defines the protocol; <span class="mono">Agent</span> (concrete) implements assembly + loop.</li>
    <li><span class="mono">run()</span> = build messages → inject context → call ChatClient → tool loop → return.</li>
    <li>Return types: non-streaming <span class="mono">AgentResponse</span>; streaming <span class="mono">AgentResponseUpdate</span>.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>The loop skeleton is owned by the base class</strong>; subclasses only plug in "how to call the model"
  — the classic <strong>Template Method pattern</strong>. You can customise Agent behavior without breaking the loop logic.
</div>
"""

# ---------------------------------------------------------------------------
L09_ZH = r"""
<p class="lead"><span class="inline">BaseChatClient</span> 是"和某个 LLM 通话"的<strong>厂商无关协议</strong>。
你平时只碰 <span class="inline">get_response()</span>，厂商做的事全藏在 <span class="inline">_inner_get_response()</span> 里。</p>

<div class="card analogy">
  <div class="tag">📞 生活类比</div>
  <span class="mono">BaseChatClient</span> 像一个<strong>电话交换台</strong>的标准面板——任何电话（模型）都能接上去。
  <span class="mono">get_response()</span> 是你按的"拨号键"，<span class="mono">_inner_get_response()</span>
  是交换台背后的<strong>接线逻辑</strong>，各厂商各不同。
</div>

<h2>调用链</h2>
<div class="flow">
  <div class="node"><div class="nt">Agent</div><div class="nd">组装消息</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">get_response()</div><div class="nd">公共入口</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">_inner_get_response()</div><div class="nd">厂商实现</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">LLM API</div><div class="nd">真实网络调用</div></div>
</div>

<table class="t">
  <tr><th>方法</th><th>谁调用</th><th>返回</th></tr>
  <tr><td class="mono">get_response(messages, stream=False)</td><td>Agent / 你</td><td><span class="mono">ChatResponse</span> 或 <span class="mono">AsyncIterator[ChatResponseUpdate]</span></td></tr>
  <tr><td class="mono">_inner_get_response(messages, stream, options)</td><td>基类内部</td><td>同上（由 provider 实现）</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> 厂商怎么实现 _inner_get_response? <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 以 FoundryChatClient 为例</div>
      <div class="a">它继承 <span class="mono">BaseChatClient</span>，只覆写 <span class="mono">_inner_get_response</span>：
        把 MAF 的 <span class="mono">Message</span> 列表转成 Foundry SDK 的格式、调 API、再把结果转回 <span class="mono">ChatResponse</span>。
        如果 <span class="mono">stream=True</span>，则返回一个异步生成器。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>你只用 <span class="mono">get_response()</span>；厂商只需实现 <span class="mono">_inner_get_response()</span>。</li>
    <li><span class="mono">stream</span> 参数决定返回完整 <span class="mono">ChatResponse</span> 还是逐块 <span class="mono">ChatResponseUpdate</span>。</li>
    <li><span class="mono">ChatOptions</span> 传递温度、max_tokens 等模型参数。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>公共接口 vs 厂商扩展点</strong>一刀切开：<span class="mono">get_response</span> 做通用逻辑（重试、中间件触发），
  <span class="mono">_inner_get_response</span> 只管"怎么和那家 API 通信"。新增厂商只需写一个子类。
</div>
"""

L09_EN = r"""
<p class="lead"><span class="inline">BaseChatClient</span> is the <strong>vendor-agnostic protocol</strong> for talking
to any LLM. You only touch <span class="inline">get_response()</span>; vendor-specific work is hidden inside
<span class="inline">_inner_get_response()</span>.</p>

<div class="card analogy">
  <div class="tag">📞 Analogy</div>
  <span class="mono">BaseChatClient</span> is a <strong>telephone switchboard</strong> — any phone (model) plugs in.
  <span class="mono">get_response()</span> is the "dial" button you press; <span class="mono">_inner_get_response()</span>
  is the <strong>wiring logic</strong> behind the panel, different for each vendor.
</div>

<h2>Call chain</h2>
<div class="flow">
  <div class="node"><div class="nt">Agent</div><div class="nd">assembles msgs</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">get_response()</div><div class="nd">public entry</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">_inner_get_response()</div><div class="nd">vendor impl</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">LLM API</div><div class="nd">network call</div></div>
</div>

<table class="t">
  <tr><th>Method</th><th>Called by</th><th>Returns</th></tr>
  <tr><td class="mono">get_response(messages, stream=False)</td><td>Agent / you</td><td><span class="mono">ChatResponse</span> or <span class="mono">AsyncIterator[ChatResponseUpdate]</span></td></tr>
  <tr><td class="mono">_inner_get_response(messages, stream, options)</td><td>base class</td><td>same (implemented by provider)</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> How do providers implement _inner_get_response? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 FoundryChatClient example</div>
      <div class="a">It extends <span class="mono">BaseChatClient</span> and only overrides <span class="mono">_inner_get_response</span>:
        converts MAF <span class="mono">Message</span> objects to the Foundry SDK format, calls the API, converts the result
        back to <span class="mono">ChatResponse</span>. When <span class="mono">stream=True</span>, it returns an async generator.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>You use <span class="mono">get_response()</span>; vendors only implement <span class="mono">_inner_get_response()</span>.</li>
    <li>The <span class="mono">stream</span> flag toggles between full <span class="mono">ChatResponse</span> and chunked <span class="mono">ChatResponseUpdate</span>.</li>
    <li><span class="mono">ChatOptions</span> carries model parameters like temperature and max_tokens.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Public interface vs vendor extension point</strong> are split cleanly: <span class="mono">get_response</span>
  handles shared logic (retries, middleware triggers); <span class="mono">_inner_get_response</span> only deals with
  "how to talk to that API". Adding a vendor means writing one subclass.
</div>
"""

# ---------------------------------------------------------------------------
L10_ZH = r"""
<p class="lead"><span class="inline">@tool</span> 在用户那一课看起来很"魔法"——这里拆开看它内部做了什么：
从 Python 函数到 JSON Schema，再到模型来回调用的<strong>完整闭环</strong>。</p>

<div class="card analogy">
  <div class="tag">🔧 生活类比</div>
  写一个工具 = 在工具架上<strong>挂了一把锤子</strong>：你写好锤子的使用说明（类型注解 + docstring），
  框架自动打印成规范卡片（JSON Schema）贴在锤子旁边，模型读卡片决定"我要用这把"，框架帮它拿起来锤。
</div>

<h2>完整闭环</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>你写函数 + @tool</h4>
    <p>框架用 <span class="mono">FunctionTool</span>（<span class="mono">_tools.py:240</span>）包装它。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>生成 JSON Schema</h4>
    <p>从 <span class="mono">Annotated[..., Field(description=...)]</span> + 返回类型自动构建 schema。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Schema 发给模型</h4>
    <p>ChatClient 在请求里带上所有工具的 schema（<span class="mono">tools</span> 字段）。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>模型返回 function_call</h4>
    <p>回复的 <span class="mono">Content</span> 里有一个 <span class="mono">function_call</span>（函数名 + JSON 参数）。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>框架反序列化 + 执行</h4>
    <p>JSON 参数 → Python 对象 → 调用你的函数 → 拿到返回值。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>function_result 回灌</h4>
    <p>返回值打包成 <span class="mono">function_result</span> Content，追加进消息，回到第 3 步让模型继续。</p></div></div>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> FunctionTool 里装了什么？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 核心属性</div>
      <div class="a"><span class="mono">FunctionTool</span> 持有：原始函数引用、生成的 JSON Schema、
        <span class="mono">approval_mode</span>（调用前是否需要人工审批）、函数名、描述。
        <span class="mono">@tool</span> 装饰器（<span class="mono">_tools.py:1145</span>）是构造 <span class="mono">FunctionTool</span> 的语法糖。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><span class="mono">@tool</span> → <span class="mono">FunctionTool</span> → JSON Schema → 随请求发给模型。</li>
    <li>模型回 <span class="mono">function_call</span> → 框架执行 → <span class="mono">function_result</span> 回灌 → 再让模型继续。</li>
    <li>整个循环在 Agent 内部自动跑，调用方无感。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>类型注解就是 schema</strong>——不存在"代码改了但忘记更新 schema"的问题，
  因为它们在同一份源码里。这是"函数即工具"哲学的核心。
</div>
"""

L10_EN = r"""
<p class="lead"><span class="inline">@tool</span> looks like magic from the user side — here we open it up: from a
Python function to JSON Schema and back through the model's <strong>full round-trip</strong>.</p>

<div class="card analogy">
  <div class="tag">🔧 Analogy</div>
  Defining a tool = <strong>hanging a hammer on the rack</strong>: you write the usage label (type hints +
  docstring), the framework auto-prints a spec card (JSON Schema) next to it, the model reads the card and says
  "I want this one", the framework picks it up and hammers for it.
</div>

<h2>The full round-trip</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>You write a function + @tool</h4>
    <p>The framework wraps it in <span class="mono">FunctionTool</span> (<span class="mono">_tools.py:240</span>).</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Generate JSON Schema</h4>
    <p>Built automatically from <span class="mono">Annotated[..., Field(description=...)]</span> + return type.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Schema sent to the model</h4>
    <p>ChatClient includes all tool schemas in the request (<span class="mono">tools</span> field).</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Model returns function_call</h4>
    <p>The reply <span class="mono">Content</span> contains a <span class="mono">function_call</span> (function name + JSON args).</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Framework deserialises + executes</h4>
    <p>JSON args → Python objects → call your function → capture the return value.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>function_result fed back</h4>
    <p>The return value is packed as <span class="mono">function_result</span> Content, appended to messages, back to step 3.</p></div></div>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> What's inside a FunctionTool? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 Core attributes</div>
      <div class="a"><span class="mono">FunctionTool</span> holds: the original function reference, the generated
        JSON Schema, <span class="mono">approval_mode</span> (whether human approval is needed before invocation),
        the function name and description.
        <span class="mono">@tool</span> (<span class="mono">_tools.py:1145</span>) is syntactic sugar for constructing a <span class="mono">FunctionTool</span>.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><span class="mono">@tool</span> → <span class="mono">FunctionTool</span> → JSON Schema → sent with the request.</li>
    <li>Model replies <span class="mono">function_call</span> → framework executes → <span class="mono">function_result</span> fed back → model continues.</li>
    <li>The whole loop runs automatically inside the Agent; callers are unaware.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Type hints ARE the schema</strong> — there is no "changed the code but forgot to update the schema" problem,
  because they live in the same source. This is the heart of the "function is a tool" philosophy.
</div>
"""

# ---------------------------------------------------------------------------
L11_ZH = r"""
<p class="lead">中间件让你<strong>不改 Agent / ChatClient 源码</strong>就能横切地加入日志、重试、审批等逻辑。
MAF 有<strong>三层</strong>中间件，每层包裹不同粒度的操作。</p>

<div class="card analogy">
  <div class="tag">🧅 生活类比</div>
  中间件像<strong>洋葱圈</strong>：请求从外到内穿过每一层，到达核心执行后，结果再从内到外穿出来。
  每一层都可以在"进去前"和"出来后"做事（记日志、改参数、重试……）。
</div>

<h2>三层中间件</h2>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">AGENT</span><span class="name">AgentMiddleware</span></div>
    <div class="ld">包裹<strong>整个 agent.run()</strong>——最外层。用 <span class="mono">AgentContext</span>。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">CHAT</span><span class="name">ChatMiddleware</span></div>
    <div class="ld">包裹<strong>每次 LLM 调用</strong>。用 <span class="mono">ChatContext</span>。</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">FUNC</span><span class="name">FunctionMiddleware</span></div>
    <div class="ld">包裹<strong>每次工具执行</strong>。用 <span class="mono">FunctionInvocationContext</span>。</div></div>
</div>

<h2>统一签名</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">中间件模板</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> AgentMiddleware, AgentContext

<span class="kw">class</span> <span class="fn">MyLoggingMiddleware</span>(AgentMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, context: AgentContext, call_next):
        <span class="fn">print</span>(<span class="st">"before"</span>)
        <span class="kw">await</span> call_next()   <span class="cm"># ← 无参！</span>
        <span class="fn">print</span>(<span class="st">"after"</span>, context.result)</pre>
</div>
<p><strong>重点</strong>：<span class="inline">await call_next()</span> <strong>不传任何参数</strong>——它调用下一层或最终执行。
执行结果挂在 <span class="mono">context.result</span> 上。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 也可以用装饰器写法 <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 函数式中间件</div>
      <div class="a">不想写类？用装饰器：
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> agent_middleware

<span class="nb">@agent_middleware</span>
<span class="kw">async def</span> <span class="fn">my_log</span>(context, call_next):
    <span class="fn">print</span>(<span class="st">"before"</span>)
    <span class="kw">await</span> call_next()
    <span class="fn">print</span>(<span class="st">"after"</span>)</pre>
        同样有 <span class="mono">@function_middleware</span> 和 <span class="mono">@chat_middleware</span>。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>三层：<span class="mono">AgentMiddleware</span>（整个 run）→ <span class="mono">ChatMiddleware</span>（每次 LLM 调用）→ <span class="mono">FunctionMiddleware</span>（每次工具执行）。</li>
    <li>统一签名 <span class="mono">process(self, context, call_next)</span>；<span class="mono">await call_next()</span> <strong>无参</strong>。</li>
    <li>可用类写法，也可用 <span class="mono">@agent_middleware</span> 等装饰器。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>三层粒度 × 洋葱模型</strong>：你可以只拦截"每次 LLM 调用"（ChatMiddleware）而不碰工具执行，
  或只拦截工具执行而不碰 LLM——关注点彻底分离。
</div>
"""

L11_EN = r"""
<p class="lead">Middleware lets you add logging, retries, approvals and more <strong>without touching Agent or
ChatClient source</strong>. MAF has <strong>three layers</strong>, each wrapping a different granularity.</p>

<div class="card analogy">
  <div class="tag">🧅 Analogy</div>
  Middleware is an <strong>onion</strong>: the request passes through each layer from outside in, reaches the core
  execution, then the result passes back out. Each layer can act "on the way in" and "on the way out"
  (log, modify params, retry…).
</div>

<h2>Three middleware layers</h2>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">AGENT</span><span class="name">AgentMiddleware</span></div>
    <div class="ld">Wraps the <strong>entire agent.run()</strong> — the outermost layer. Uses <span class="mono">AgentContext</span>.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">CHAT</span><span class="name">ChatMiddleware</span></div>
    <div class="ld">Wraps <strong>each LLM call</strong>. Uses <span class="mono">ChatContext</span>.</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">FUNC</span><span class="name">FunctionMiddleware</span></div>
    <div class="ld">Wraps <strong>each tool execution</strong>. Uses <span class="mono">FunctionInvocationContext</span>.</div></div>
</div>

<h2>Unified signature</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">middleware template</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> AgentMiddleware, AgentContext

<span class="kw">class</span> <span class="fn">MyLoggingMiddleware</span>(AgentMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, context: AgentContext, call_next):
        <span class="fn">print</span>(<span class="st">"before"</span>)
        <span class="kw">await</span> call_next()   <span class="cm"># ← no arguments!</span>
        <span class="fn">print</span>(<span class="st">"after"</span>, context.result)</pre>
</div>
<p><strong>Key</strong>: <span class="inline">await call_next()</span> takes <strong>no arguments</strong> — it invokes the
next layer or the final execution. The result lives on <span class="mono">context.result</span>.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Decorator shortcut <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Function-style middleware</div>
      <div class="a">Don't want a class? Use a decorator:
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> agent_middleware

<span class="nb">@agent_middleware</span>
<span class="kw">async def</span> <span class="fn">my_log</span>(context, call_next):
    <span class="fn">print</span>(<span class="st">"before"</span>)
    <span class="kw">await</span> call_next()
    <span class="fn">print</span>(<span class="st">"after"</span>)</pre>
        Similarly <span class="mono">@function_middleware</span> and <span class="mono">@chat_middleware</span>.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Three layers: <span class="mono">AgentMiddleware</span> (whole run) → <span class="mono">ChatMiddleware</span> (each LLM call) → <span class="mono">FunctionMiddleware</span> (each tool execution).</li>
    <li>Unified signature <span class="mono">process(self, context, call_next)</span>; <span class="mono">await call_next()</span> takes <strong>no args</strong>.</li>
    <li>Class-based or decorator-based: <span class="mono">@agent_middleware</span>, <span class="mono">@function_middleware</span>, <span class="mono">@chat_middleware</span>.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Three granularities × onion model</strong>: you can intercept "every LLM call" (ChatMiddleware) without
  touching tool execution, or intercept tool execution without touching LLM — concerns are fully separated.
</div>
"""

# ---------------------------------------------------------------------------
L12_ZH = r"""
<p class="lead"><strong>Workflows</strong> 是 MAF 的图执行引擎：把多个步骤（<span class="mono">Executor</span>）
用<strong>边（Edge）</strong>连成有向图，由 <span class="mono">WorkflowBuilder</span> 构建、<span class="mono">Workflow.run()</span> 驱动。</p>

<div class="card analogy">
  <div class="tag">🗺️ 生活类比</div>
  把 Workflow 想成<strong>地铁线路图</strong>：每个站（Executor）做一件事，
  铁轨（Edge）决定下一站去哪。<span class="mono">WorkflowBuilder</span> 画图，<span class="mono">run()</span> 发车。
</div>

<h2>核心概念</h2>
<table class="t">
  <tr><th>概念</th><th>作用</th><th>源码</th></tr>
  <tr><td class="mono">Executor</td><td>图中的一个节点，处理消息</td><td class="mono">_workflows/_executor.py</td></tr>
  <tr><td class="mono">Edge</td><td>连接两个节点的有向边</td><td class="mono">_workflows/_edge.py</td></tr>
  <tr><td class="mono">WorkflowBuilder</td><td>用 <span class="mono">add_edge/add_chain</span> 构建图</td><td class="mono">_workflows/_workflow_builder.py</td></tr>
  <tr><td class="mono">WorkflowContext</td><td>节点内发消息/输出的句柄</td><td class="mono">_workflows/_workflow_context.py</td></tr>
</table>

<h2>最小示例</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">samples/01-get-started/07_first_graph_workflow.py</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Executor, WorkflowBuilder, WorkflowContext, executor, handler

<span class="kw">class</span> <span class="fn">UpperCase</span>(Executor):
    <span class="nb">@handler</span>
    <span class="kw">async def</span> <span class="fn">to_upper</span>(self, text: str, ctx: WorkflowContext[str]):
        <span class="kw">await</span> ctx.send_message(text.upper())

<span class="nb">@executor</span>(id=<span class="st">"reverse"</span>)
<span class="kw">async def</span> <span class="fn">reverse</span>(text: str, ctx: WorkflowContext):
    <span class="kw">await</span> ctx.yield_output(text[::-1])

wf = WorkflowBuilder(start_executor=UpperCase(id=<span class="st">"upper"</span>)) \
    .add_edge(UpperCase(id=<span class="st">"upper"</span>), reverse).build()
events = <span class="kw">await</span> wf.run(<span class="st">"hello"</span>)  <span class="cm"># → "OLLEH"</span></pre>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> @handler vs @executor 有什么区别？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 两种写法</div>
      <div class="a"><span class="mono">@handler</span> 标记<strong>类方法</strong>（在 Executor 子类里），
        <span class="mono">@executor</span> 标记<strong>独立函数</strong>（自动包成 FunctionExecutor）。
        功能一样，选哪个看你喜不喜欢写类。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>Workflow = <span class="mono">Executor</span>（节点）+ <span class="mono">Edge</span>（边）组成的有向图。</li>
    <li><span class="mono">WorkflowBuilder</span> 用链式 API 构图；<span class="mono">.build()</span> 得到 <span class="mono">Workflow</span>。</li>
    <li>节点通过 <span class="mono">ctx.send_message()</span> 传数据、<span class="mono">ctx.yield_output()</span> 输出最终结果。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>消息驱动</strong>：节点之间传递的是"消息"而非函数调用返回值——
  这意味着节点天然支持异步、fan-out/fan-in，且可在边上加条件/开关。
</div>
"""

L12_EN = r"""
<p class="lead"><strong>Workflows</strong> are MAF's graph execution engine: wire multiple steps (<span class="mono">Executor</span>)
into a directed graph with <strong>Edges</strong>, built by <span class="mono">WorkflowBuilder</span>, driven by
<span class="mono">Workflow.run()</span>.</p>

<div class="card analogy">
  <div class="tag">🗺️ Analogy</div>
  Think of a Workflow as a <strong>subway map</strong>: each station (Executor) does one thing, the tracks (Edges)
  decide where to go next. <span class="mono">WorkflowBuilder</span> draws the map; <span class="mono">run()</span> dispatches the train.
</div>

<h2>Core concepts</h2>
<table class="t">
  <tr><th>Concept</th><th>Role</th><th>Source</th></tr>
  <tr><td class="mono">Executor</td><td>A node in the graph; processes messages</td><td class="mono">_workflows/_executor.py</td></tr>
  <tr><td class="mono">Edge</td><td>A directed edge connecting two nodes</td><td class="mono">_workflows/_edge.py</td></tr>
  <tr><td class="mono">WorkflowBuilder</td><td>Chain API: <span class="mono">add_edge/add_chain</span> to build the graph</td><td class="mono">_workflows/_workflow_builder.py</td></tr>
  <tr><td class="mono">WorkflowContext</td><td>Handle for sending messages / yielding output inside a node</td><td class="mono">_workflows/_workflow_context.py</td></tr>
</table>

<h2>Minimal example</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">samples/01-get-started/07_first_graph_workflow.py</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Executor, WorkflowBuilder, WorkflowContext, executor, handler

<span class="kw">class</span> <span class="fn">UpperCase</span>(Executor):
    <span class="nb">@handler</span>
    <span class="kw">async def</span> <span class="fn">to_upper</span>(self, text: str, ctx: WorkflowContext[str]):
        <span class="kw">await</span> ctx.send_message(text.upper())

<span class="nb">@executor</span>(id=<span class="st">"reverse"</span>)
<span class="kw">async def</span> <span class="fn">reverse</span>(text: str, ctx: WorkflowContext):
    <span class="kw">await</span> ctx.yield_output(text[::-1])

wf = WorkflowBuilder(start_executor=UpperCase(id=<span class="st">"upper"</span>)) \
    .add_edge(UpperCase(id=<span class="st">"upper"</span>), reverse).build()
events = <span class="kw">await</span> wf.run(<span class="st">"hello"</span>)  <span class="cm"># → "OLLEH"</span></pre>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> @handler vs @executor? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 Two styles</div>
      <div class="a"><span class="mono">@handler</span> marks a <strong>class method</strong> (inside an Executor subclass);
        <span class="mono">@executor</span> marks a <strong>standalone function</strong> (auto-wrapped into a FunctionExecutor).
        Same capability — pick whichever style you prefer.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Workflow = <span class="mono">Executor</span> (node) + <span class="mono">Edge</span> (arc) forming a directed graph.</li>
    <li><span class="mono">WorkflowBuilder</span> chain API; <span class="mono">.build()</span> yields a <span class="mono">Workflow</span>.</li>
    <li>Nodes use <span class="mono">ctx.send_message()</span> to forward data and <span class="mono">ctx.yield_output()</span> for final results.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Message-driven</strong>: nodes pass "messages", not function return values — so they naturally support
  async, fan-out/fan-in, and you can add conditions or switches on the edges.
</div>
"""

# ---------------------------------------------------------------------------
L13_ZH = r"""
<p class="lead">当你需要<strong>多个 Agent 协作</strong>，MAF 提供五种现成的编排模式——
不用手写调度逻辑，选一个 Builder、传入参与者，<span class="inline">.build()</span> 就行。</p>

<div class="card analogy">
  <div class="tag">🎼 生活类比</div>
  编排模式像<strong>乐团编制</strong>：Sequential 是依次独奏，Concurrent 是齐奏，
  Handoff 是接力棒传递，Group Chat 是圆桌讨论，Magentic 是指挥家调度全局。
</div>

<h2>五种模式</h2>
<table class="t">
  <tr><th>模式</th><th>Builder</th><th>一句话</th></tr>
  <tr><td><strong>Sequential</strong></td><td class="mono">SequentialBuilder</td><td>Agent A 做完 → Agent B 接着做</td></tr>
  <tr><td><strong>Concurrent</strong></td><td class="mono">ConcurrentBuilder</td><td>Agent A 和 B 同时做，汇总结果</td></tr>
  <tr><td><strong>Handoff</strong></td><td class="mono">HandoffBuilder</td><td>Agent A 主动把任务"交接"给 B</td></tr>
  <tr><td><strong>Group Chat</strong></td><td class="mono">GroupChatBuilder</td><td>多个 Agent 在群聊中轮流发言</td></tr>
  <tr><td><strong>Magentic</strong></td><td class="mono">MagenticBuilder</td><td>有一个"指挥官"分派子任务给各 Agent</td></tr>
</table>

<h2>最简用法</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">Sequential 示例</span></div>
<pre><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder

workflow = SequentialBuilder(participants=[writer, reviewer]).build()
result = <span class="kw">await</span> workflow.run(<span class="st">"Write a poem about the sea"</span>)</pre>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> Handoff 和 Group Chat 有什么区别？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 关键差异</div>
      <div class="a"><strong>Handoff</strong>：当前 Agent 显式决定"我做不了，交给 X"，控制权<strong>单向传递</strong>。
        <strong>Group Chat</strong>：一个 selector 函数（或模型）每轮选谁发言，所有 Agent <strong>看到完整群聊记录</strong>。
        Handoff 更适合专家流转，Group Chat 更适合辩论 / 头脑风暴。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>五种编排：Sequential / Concurrent / Handoff / Group Chat / Magentic。</li>
    <li>全部来自 <span class="mono">agent_framework.orchestrations</span>，选 Builder → 传参与者 → <span class="mono">.build()</span>。</li>
    <li>底层都是 Workflow 图——编排是高级糖。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>编排模式 = 预置拓扑的 Workflow</strong>：你用 Builder 声明意图，框架帮你画出正确的图。
  需要更复杂的拓扑？直接用 <span class="mono">WorkflowBuilder</span> 手画。
</div>
"""

L13_EN = r"""
<p class="lead">When you need <strong>multiple Agents to collaborate</strong>, MAF provides five ready-made
orchestration patterns — pick a Builder, pass participants, <span class="inline">.build()</span>.</p>

<div class="card analogy">
  <div class="tag">🎼 Analogy</div>
  Orchestration patterns are like <strong>ensemble formats</strong>: Sequential is solos one after another,
  Concurrent is playing together, Handoff is passing the baton, Group Chat is a roundtable, Magentic is a
  conductor assigning parts.
</div>

<h2>Five patterns</h2>
<table class="t">
  <tr><th>Pattern</th><th>Builder</th><th>One-liner</th></tr>
  <tr><td><strong>Sequential</strong></td><td class="mono">SequentialBuilder</td><td>Agent A finishes → Agent B continues</td></tr>
  <tr><td><strong>Concurrent</strong></td><td class="mono">ConcurrentBuilder</td><td>A and B work in parallel, results merged</td></tr>
  <tr><td><strong>Handoff</strong></td><td class="mono">HandoffBuilder</td><td>Agent A explicitly hands the task to B</td></tr>
  <tr><td><strong>Group Chat</strong></td><td class="mono">GroupChatBuilder</td><td>Agents take turns speaking in a shared chat</td></tr>
  <tr><td><strong>Magentic</strong></td><td class="mono">MagenticBuilder</td><td>A "conductor" dispatches sub-tasks to agents</td></tr>
</table>

<h2>Simplest usage</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">Sequential example</span></div>
<pre><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder

workflow = SequentialBuilder(participants=[writer, reviewer]).build()
result = <span class="kw">await</span> workflow.run(<span class="st">"Write a poem about the sea"</span>)</pre>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> Handoff vs Group Chat? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 Key difference</div>
      <div class="a"><strong>Handoff</strong>: the current Agent explicitly decides "I can't do this, hand to X" —
        control flows <strong>unidirectionally</strong>. <strong>Group Chat</strong>: a selector function (or model) picks
        who speaks each turn; all Agents <strong>see the full chat history</strong>. Handoff suits expert routing;
        Group Chat suits debate / brainstorming.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Five patterns: Sequential / Concurrent / Handoff / Group Chat / Magentic.</li>
    <li>All from <span class="mono">agent_framework.orchestrations</span>; pick a Builder → pass participants → <span class="mono">.build()</span>.</li>
    <li>Under the hood they are all Workflow graphs — orchestration is high-level sugar.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Orchestration = pre-wired Workflow topology</strong>: you declare intent with a Builder, the framework
  draws the right graph. Need a more complex topology? Use <span class="mono">WorkflowBuilder</span> directly.
</div>
"""

# ---------------------------------------------------------------------------
L14_ZH = r"""
<p class="lead">当 Agent 或 Workflow 在跑时，你可以<strong>逐块看到输出</strong>（流式），
也可以用 <strong>OpenTelemetry</strong> 追踪每一步的耗时、token 用量和错误。</p>

<div class="card analogy">
  <div class="tag">📡 生活类比</div>
  流式像<strong>直播</strong>：观众实时看到画面（token）。
  可观测性像<strong>监控大屏</strong>：运维看延迟、吞吐、异常告警。两者互补。
</div>

<h2>流式输出</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">streaming</span></div>
<pre><span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">"Tell me a joke"</span>, stream=<span class="kw">True</span>):
    <span class="kw">if</span> chunk.text:
        <span class="fn">print</span>(chunk.text, end=<span class="st">""</span>)</pre>
</div>
<p>每个 <span class="mono">chunk</span> 是一个 <span class="mono">AgentResponseUpdate</span>，
包含 <span class="mono">.text</span>（增量文本）等字段。累积起来就是完整的 <span class="mono">AgentResponse</span>。</p>

<h2>OpenTelemetry 集成</h2>
<div class="flow">
  <div class="node"><div class="nt">Agent run</div><div class="nd">span</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">ChatClient call</div><div class="nd">子 span</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Tool exec</div><div class="nd">子 span</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">导出</div><div class="nd">Jaeger / OTLP</div></div>
</div>
<p>MAF 内置 OTel 集成（<span class="mono">observability.py</span>）：Agent run、每次 LLM 调用、每次工具执行都自动产出 span，
携带 token 计数、延迟、异常信息。只需配置 exporter 即可在 Jaeger / Grafana 中查看。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 怎么启用 OTel？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 最小配置</div>
      <div class="a">参考 <span class="mono">samples/02-agents/observability/</span>：安装
        <span class="mono">opentelemetry-sdk</span> + exporter，在代码最前面调用
        <span class="mono">TracerProvider</span> 初始化。框架会自动把 span 附加到 agent/chat/tool 操作上。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><span class="mono">run(stream=True)</span> 逐块返回 <span class="mono">AgentResponseUpdate</span>。</li>
    <li>内置 OpenTelemetry：agent run / LLM 调用 / 工具执行自动产出 span。</li>
    <li>配好 exporter 即可在 Jaeger / Grafana 等工具中查看追踪与指标。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>可观测性是内置的</strong>，不是你自己加的——框架自动在关键操作上挂 span，
  零额外代码就能看到"这次 run 调了几次模型、每次多少 token、工具花了多久"。
</div>
"""

L14_EN = r"""
<p class="lead">While an Agent or Workflow runs, you can <strong>see output as it streams</strong> and use
<strong>OpenTelemetry</strong> to trace every step's latency, token usage and errors.</p>

<div class="card analogy">
  <div class="tag">📡 Analogy</div>
  Streaming is <strong>live TV</strong>: the audience sees frames (tokens) in real time.
  Observability is the <strong>ops dashboard</strong>: SREs watch latency, throughput and alerts. Complementary.
</div>

<h2>Streaming output</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">streaming</span></div>
<pre><span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">"Tell me a joke"</span>, stream=<span class="kw">True</span>):
    <span class="kw">if</span> chunk.text:
        <span class="fn">print</span>(chunk.text, end=<span class="st">""</span>)</pre>
</div>
<p>Each <span class="mono">chunk</span> is an <span class="mono">AgentResponseUpdate</span> with a
<span class="mono">.text</span> (incremental text) field. Accumulated, they form the full <span class="mono">AgentResponse</span>.</p>

<h2>OpenTelemetry integration</h2>
<div class="flow">
  <div class="node"><div class="nt">Agent run</div><div class="nd">span</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">ChatClient call</div><div class="nd">child span</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Tool exec</div><div class="nd">child span</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Export</div><div class="nd">Jaeger / OTLP</div></div>
</div>
<p>MAF has built-in OTel integration (<span class="mono">observability.py</span>): Agent runs, LLM calls and tool
executions automatically emit spans with token counts, latency and error info. Just configure an exporter to view
them in Jaeger / Grafana.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> How to enable OTel? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Minimal setup</div>
      <div class="a">See <span class="mono">samples/02-agents/observability/</span>: install
        <span class="mono">opentelemetry-sdk</span> + an exporter, call <span class="mono">TracerProvider</span> init at
        the top of your code. The framework auto-attaches spans to agent/chat/tool operations.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><span class="mono">run(stream=True)</span> yields <span class="mono">AgentResponseUpdate</span> chunks.</li>
    <li>Built-in OpenTelemetry: agent run / LLM call / tool exec auto-emit spans.</li>
    <li>Configure an exporter to view traces and metrics in Jaeger / Grafana.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Observability is built in</strong>, not bolted on — the framework auto-attaches spans to key operations.
  Zero extra code to see "how many model calls this run made, tokens per call, tool latency".
</div>
"""
