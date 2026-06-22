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

<h2>追踪一次真实 run()：「巴黎今天天气如何？」</h2>
<p>抽象讲完了，我们用一个<strong>具体输入</strong>端到端走一遍。假设这个 Agent 带一个工具
<span class="mono">get_weather(city)</span>，你调用 <span class="mono">agent.run(&quot;巴黎今天天气如何？&quot;)</span>。
下面每一步都给出当时<strong>消息列表的真实快照</strong>——看它如何从 2 条长到 4 条，再收敛成一个 <span class="mono">AgentResponse</span>。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>组装初始消息（2 条）</h4>
    <p><span class="mono">_prepare_run_context()</span>（<span class="mono">_agents.py:1150</span>）把 system 指令 + 你的输入拼成消息列表，并带上工具：</p>
<pre class="code">messages = [
  Message(<span class="st">&quot;system&quot;</span>,    [<span class="st">&quot;你是天气助手…&quot;</span>]),
  Message(<span class="st">&quot;user&quot;</span>,      [<span class="st">&quot;巴黎今天天气如何？&quot;</span>]),
]
tools = [get_weather]   <span class="cm"># 随请求一起发出的工具 schema</span></pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>交给 ChatClient（循环在它内部）</h4>
    <p><span class="mono">_call_chat_client()</span>（<span class="mono">_agents.py:985</span>）只做一件事：<span class="mono">client.get_response(messages, options)</span>。
    <strong>工具循环并不在 Agent 里</strong>——它发生在 ChatClient 一侧的 <span class="mono">FunctionInvocationLayer</span>（<span class="mono">_tools.py:2249</span>，下一课展开）。Agent 只调用一次。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>模型决定先调用工具</h4>
    <p>第一轮模型不直接作答，而是回一个 <span class="mono">function_call</span> 内容：</p>
<pre class="code">assistant_msg = Message(<span class="st">&quot;assistant&quot;</span>, [
  Content.from_function_call(
    call_id=<span class="st">&quot;call_1&quot;</span>, name=<span class="st">&quot;get_weather&quot;</span>,
    arguments=<span class="st">'{&quot;city&quot;: &quot;Paris&quot;}'</span>),  <span class="cm"># arguments 是 JSON 字符串</span>
])</pre></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>执行工具，工作消息长到 4 条</h4>
    <p>框架解析参数、调用你的 Python 函数 <span class="mono">get_weather(&quot;Paris&quot;)</span> 得 <span class="mono">&quot;18°C 晴&quot;</span>，
    打包成 <span class="mono">function_result</span> 追加进去：</p>
<pre class="code">prepped_messages = [
  Message(<span class="st">&quot;system&quot;</span>,    [...]),
  Message(<span class="st">&quot;user&quot;</span>,      [...]),
  Message(<span class="st">&quot;assistant&quot;</span>, [function_call get_weather]),    <span class="cm"># 第 3 条</span>
  Message(<span class="st">&quot;tool&quot;</span>,      [function_result <span class="st">&quot;18°C 晴&quot;</span>]),  <span class="cm"># 第 4 条</span>
]</pre></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>带着结果再问一次模型</h4>
    <p>循环回到顶部，把这 4 条消息整体再发给模型。这次模型手里已经有了天气数据，不必再调工具。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>拿到最终文本，循环终止</h4>
    <p>模型回 <span class="mono">Message(&quot;assistant&quot;, [&quot;巴黎今天 18°C，晴。&quot;])</span>，
    没有新的 <span class="mono">function_call</span>、<span class="mono">finish_reason=&quot;stop&quot;</span> → <span class="mono">FunctionInvocationLayer</span> 退出循环（上限 <span class="mono">DEFAULT_MAX_ITERATIONS=40</span> 轮）。</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>包装成 AgentResponse</h4>
    <p><span class="mono">_parse_non_streaming_response()</span>（<span class="mono">_agents.py:1013</span>）把这个 <span class="mono">ChatResponse</span> 收进 <span class="mono">AgentResponse</span>：</p>
<pre class="code">resp = AgentResponse(messages=response.messages, …)
resp.text            <span class="cm"># &quot;巴黎今天 18°C，晴。&quot;</span>
resp.messages        <span class="cm"># 本轮新产生的消息：function_call → function_result → 最终回答</span>
resp.usage_details   <span class="cm"># 两轮模型调用累加的 token</span></pre></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 读懂这条轨迹</div>
  关键不在"走了几步"，而在<strong>消息列表是唯一的状态载体</strong>：每一轮模型调用本身是<strong>无状态</strong>的，
  框架靠"把上一轮的 function_call 与 function_result 追加进<em>同一个</em> list 再发回去"，制造出"模型记得自己刚查过天气"的连续感。
  还有一个常被误解的细节：循环内不断变长的是<strong>工作消息</strong>（<span class="mono">prepped_messages</span>），
  而 <span class="mono">AgentResponse.messages</span> 只装<strong>本轮新产生</strong>的消息（不含你传入的 system/user）——所以别指望从返回值里读回原始输入。
</div>

<h2>三层组合：一个 Agent 的真身</h2>
<p>你 <span class="mono">new</span> 出来的 <span class="mono">Agent</span> 其实是三层用 <strong>Python 多继承</strong>叠出来的。
调用 <span class="mono">run()</span> 时，请求<strong>从外到内</strong>依次穿过这三层，最后才落到真正干活的 <span class="mono">RawAgent</span>：</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">最外</span><span class="name">AgentMiddlewareLayer</span></div>
    <div class="ld">中间件层（<span class="mono">_middleware.py:1258</span>）。先跑你注册的 <span class="mono">AgentMiddleware</span>，可改请求 / 改结果 / 短路。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">中间</span><span class="name">AgentTelemetryLayer</span></div>
    <div class="ld">遥测层（来自 <span class="mono">observability</span>）。开一个 OpenTelemetry span，记录这次 run 的耗时 / token / 异常。</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">核心</span><span class="name">RawAgent</span></div>
    <div class="ld">真正的循环骨架（<span class="mono">_agents.py:578</span>）：上面追踪的 7 步就在这里。</div></div>
</div>
<p>对应真实定义 <span class="mono">class Agent(AgentMiddlewareLayer, AgentTelemetryLayer, RawAgent, Generic[…])</span>
（<span class="mono">_agents.py:1584</span>）。<strong>方法解析顺序（MRO）天然形成了洋葱</strong>：先中间件、再遥测、最后核心——你不需要手写任何"包裹"代码。</p>

<h2>🔍 真实源码：run() 的三步骨架</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_agents.py</span><span class="ln">RawAgent.run（简化自 :889）</span></div>
<pre class="code"><span class="kw">def</span> <span class="fn">run</span>(self, messages=<span class="kw">None</span>, *, stream=<span class="kw">False</span>, session=<span class="kw">None</span>,
        tools=<span class="kw">None</span>, options=<span class="kw">None</span>, …):
    <span class="kw">async def</span> <span class="fn">_prepare_run_context</span>():
        <span class="kw">return await</span> self._prepare_run_context(messages=messages, …)

    <span class="kw">if not</span> stream:                          <span class="cm"># ① 非流式 → 返回 AgentResponse</span>
        <span class="kw">async def</span> <span class="fn">_run_non_streaming</span>():
            ctx = <span class="kw">await</span> _prepare_run_context()    <span class="cm"># 1. 组装上下文</span>
            response = <span class="kw">await</span> self._call_chat_client(ctx, stream=<span class="kw">False</span>)  <span class="cm"># 2. 调 ChatClient</span>
            <span class="kw">return await</span> self._parse_non_streaming_response(ctx, response)  <span class="cm"># 3. 解析</span>
        <span class="kw">return</span> _run_non_streaming()

    <span class="kw">async def</span> <span class="fn">_run_streaming</span>():            <span class="cm"># ② stream=True → 返回更新流</span>
        ctx = <span class="kw">await</span> _prepare_run_context()
        stream_response = self._call_chat_client(ctx, stream=<span class="kw">True</span>)
        <span class="kw">return</span> self._parse_streaming_response(ctx, stream_response)
    <span class="kw">return</span> ResponseStream.from_awaitable(_run_streaming())</pre>
</div>
<p>三步骨架一眼可见：<strong>①准备上下文 → ②调 ChatClient → ③解析响应</strong>。流式与非流式<strong>共用第①步</strong>，
只在第②③步分叉——这正是"用一个 <span class="mono">stream</span> 布尔切换两种返回类型"的实现处，避免了写两个几乎一样的方法。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> BaseAgent 定义了哪些接口？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a"><span class="mono">BaseAgent</span>（<span class="mono">_agents.py:314</span>）规定了
      <span class="mono">run()</span>（非流式 + 流式共用）、<span class="mono">create_session()</span>、<span class="mono">get_session()</span>。
      子类只需实现这几个方法，循环骨架已由基类搭好。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">如果没有统一接口，每种 Agent 都得各写一套调用协议，
      上层编排器无法通用。抽象基类保证"任何 Agent 都能 <span class="mono">run()</span>"，这是多态的基础。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">MAF 用 <strong>模板方法模式</strong>：<span class="mono">BaseAgent</span>
      定义骨架，<span class="mono">RawAgent</span> / <span class="mono">Agent</span> 分层实现。
      这样可以在不破坏协议的前提下自由扩展。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">LangChain 用 <span class="mono">Runnable</span> 协议（更通用但更松散）；
      AutoGen 用 <span class="mono">ConversableAgent</span>（更紧耦合）。MAF 选择"刚好够用"的抽象层次，避免过度泛化。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Agent.run() 内部调用链 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a"><span class="mono">Agent</span>（<span class="mono">_agents.py:1584</span>）的 <span class="mono">run()</span>
      经过中间件 / 遥测层后进入 <span class="mono">RawAgent.run()</span>（<span class="mono">_agents.py:889</span>），依次调用：
<pre class="code">_prepare_run_context()   <span class="cm"># 准备消息、session、工具、选项</span>
_call_chat_client()      <span class="cm"># 调用 ChatClient 拿回 ChatResponse</span>
_parse_non_streaming_response()  <span class="cm"># 非流式：转为 AgentResponse</span>
_parse_streaming_response()      <span class="cm"># 流式：转为 AgentResponseUpdate 流</span>
_run_after_providers()   <span class="cm"># 执行 ContextProvider 后置钩子</span></pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">理解内部调用链，才知道在哪里挂中间件、在哪里注入上下文、
      出错时该看哪一步——不再"黑箱调试"。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">每个步骤是独立方法，职责单一。
      <span class="mono">_prepare_run_context()</span> 只管拼消息，<span class="mono">_call_chat_client()</span> 只管调模型。
      这让子类可以 <strong>精确覆写某一步</strong>而不动其他步骤。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">有的框架把所有逻辑放进一个大 <span class="mono">run()</span> 方法；
      也有的用声明式 DAG（如 LangGraph）编排。MAF 的方法函数分拆 + 循环骨架是两者的中间路线。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 自定义 Agent（RawAgent） <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a"><span class="mono">RawAgent</span>（<span class="mono">_agents.py:578</span>）是核心实现层——
      它继承 <span class="mono">BaseAgent</span>，实现了完整的 <span class="mono">run()</span>、上下文提供者执行、会话管理、工具解析。
      如果你想"完全接管"Agent 行为，就继承 <span class="mono">RawAgent</span> 并覆写 <span class="mono">_call_chat_client()</span>。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">默认 <span class="mono">Agent</span> 自带中间件层和遥测层。
      有时你需要跳过这些层，或者完全替换 LLM 调用逻辑（比如做 mock 测试），这时需要 <span class="mono">RawAgent</span>。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">Agent = AgentMiddlewareLayer + AgentTelemetryLayer + RawAgent</span>。
      三层用 Python 多继承组合，你可以只要其中一层或全部。这种 <strong>Mixin 模式</strong>比单一继承链灵活得多。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">可以用装饰器模式逐层包裹（增加运行时开销），
      或用配置开关控制功能（不够灵活）。MAF 选择 Mixin 继承，编译期确定行为、零额外运行时开销。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> AgentResponse 的结构 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a"><span class="mono">AgentResponse</span>（<span class="mono">_types.py:2530</span>）的核心字段：
<pre class="code">response.text           <span class="cm"># 所有消息的拼合文本</span>
response.messages       <span class="cm"># list[Message] — 完整消息列表</span>
response.usage_details  <span class="cm"># UsageDetails — prompt/completion token 计数</span>
response.finish_reason  <span class="cm"># &quot;stop&quot; / &quot;tool_calls&quot; / &quot;length&quot;</span>
response.value          <span class="cm"># 结构化输出（如果设了 response_format）</span>
response.raw_representation  <span class="cm"># 原始 API 响应</span></pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">了解返回结构，你才能正确地：提取回复文本、检查 token 用量做成本控制、
      判断模型是"正常结束"还是"截断了"、拿到结构化数据而不是手动解析 JSON。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">.text</span> 是只读属性（自动拼合所有 message），
      <span class="mono">.value</span> 支持泛型——如果你声明了 <span class="mono">response_format=MyModel</span>，
      <span class="mono">.value</span> 自动返回 <span class="mono">MyModel</span> 实例，无需手动反序列化。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">OpenAI SDK 直接返回 dict/dataclass；LangChain 用 <span class="mono">AIMessage</span>。
      MAF 的 <span class="mono">AgentResponse</span> 多了 <span class="mono">.value</span> 泛型和 <span class="mono">.continuation_token</span>
      （可恢复长对话），更贴近生产需求。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> RawAgent vs Agent <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code"><span class="cm"># Agent = 全功能版（中间件 + 遥测 + RawAgent）</span>
agent = Agent(name=<span class="st">&quot;full&quot;</span>, client=client,
              middleware=[LogMiddleware()])

<span class="cm"># RawAgent = 最小核心（无中间件 / 遥测层）</span>
raw = RawAgent(name=<span class="st">&quot;bare&quot;</span>, client=client)</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">如果你只想做单元测试或轻量调用，<span class="mono">Agent</span> 的中间件 / 遥测层是不必要的开销。
      反之，在生产环境你几乎总是需要日志和监控——此时 <span class="mono">Agent</span> 一步到位。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">两者共享 <span class="mono">BaseAgent</span> 协议，所以对编排器来说是<strong>完全互换的</strong>。
      你可以开发时用 <span class="mono">RawAgent</span> 快速迭代，上线时换成 <span class="mono">Agent</span> 加中间件，调用方无需任何改动。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">有的框架只提供一个 Agent 类，通过 <span class="mono">debug=True</span> 开关控制行为。
      MAF 的分层继承更干净——不想要的层根本不存在，而不是"存在但被 if 跳过"。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">6</span> 🔍 真实源码：run() 的核心实现 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 来自 _agents.py 的真实代码</div>
      <div class="a">以下是 <span class="mono">RawAgent.run()</span> 的核心分支（<span class="mono">_agents.py:952</span>），精简后：
<pre class="code"><span class="cm"># _agents.py — RawAgent.run() 核心（简化版）</span>

<span class="kw">async def</span> _prepare_run_context():
    <span class="kw">return await</span> self._prepare_run_context(
        messages=messages, session=session,
        tools=tools, options=options, ...)

<span class="kw">if not</span> stream:
    <span class="kw">async def</span> <span class="fn">_run_non_streaming</span>():
        ctx = <span class="kw">await</span> _prepare_run_context()
        response = <span class="kw">await</span> self._call_chat_client(ctx, stream=<span class="kw">False</span>)
        <span class="kw">return await</span> self._parse_non_streaming_response(ctx, response)
    <span class="kw">return</span> _run_non_streaming()

<span class="cm"># stream=True 分支</span>
<span class="kw">async def</span> <span class="fn">_run_streaming</span>():
    ctx = <span class="kw">await</span> _prepare_run_context()
    stream_response = self._call_chat_client(ctx, stream=<span class="kw">True</span>)
    <span class="kw">return</span> self._parse_streaming_response(ctx, stream_response)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么看这段代码有价值</div>
      <div class="a">三步清晰可见：<strong>①准备上下文 → ②调 ChatClient → ③解析响应</strong>。
        流式和非流式共用同一个 <span class="mono">_prepare_run_context</span>，区别只在第②③步。
        注意：<strong>工具循环不在这三步里</strong>——<span class="mono">_call_chat_client</span> 只调一次 <span class="mono">client.get_response()</span>，
        多轮 function_call ↔ function_result 的循环发生在 ChatClient 一侧的 <span class="mono">FunctionInvocationLayer</span>（<span class="mono">_tools.py:2249</span>），
        所以 <span class="mono">_parse_non_streaming_response</span> 拿到的 <span class="mono">ChatResponse</span> 已经是"跑完工具后的最终结果"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ _call_chat_client 做了什么</div>
      <div class="a">它直接调用 <span class="mono">self.client.get_response(messages=..., stream=..., options=...)</span>——
        把准备好的消息、工具 schema、ChatOptions 透传给 ChatClient。
        <strong>这就是 Agent 和 ChatClient 的交界面</strong>：Agent 负责"组装"，ChatClient 负责"通信"。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 你可以在哪些点介入</div>
      <div class="a">覆写 <span class="mono">_call_chat_client()</span>：自定义"怎么调模型"。
        覆写 <span class="mono">_prepare_run_context()</span>：自定义"怎么组装消息"。
        加中间件：不改源码也能拦截。
        三个扩展点，粒度从大到小。</div>
    </div>
  </div>
</details>

<h2>为什么这样设计</h2>
<p><strong>① 模板方法 + 分层 = 可测试性。</strong> 把"循环骨架"钉死在基类、只把"怎么调模型"留给 <span class="mono">_call_chat_client()</span>，
意味着单元测试时你只需覆写这<strong>一个</strong>方法返回假的 <span class="mono">ChatResponse</span>，就能在不联网、不烧 token 的情况下验证整条 run 逻辑。
如果循环和网络调用揉在一个大函数里，这种隔离测试几乎不可能。</p>
<p><strong>② Mixin 多继承 = 零运行时开销的可组合性。</strong> 中间件层、遥测层、核心层是三个独立类，靠 MRO 串成洋葱，
而不是用 <span class="mono">if self.enable_telemetry:</span> 之类的运行时开关。需要轻量版？直接用 <span class="mono">RawAgent</span>，那两层<strong>根本不存在</strong>于 MRO 里，
没有任何"判断后跳过"的分支成本；需要全功能？用 <span class="mono">Agent</span>，三层自动到位。功能的"有/无"在<strong>类定义期</strong>就确定了。</p>
<p><strong>③ 把工具循环下放到 ChatClient = 关注点分离。</strong> Agent 只负责"组装上下文 + 解析结果"，而"反复和模型来回、执行工具"这件复杂的事
交给 <span class="mono">FunctionInvocationLayer</span>。于是<strong>同一套工具循环能被任何 ChatClient 复用</strong>，
而 Agent 这层始终保持"瘦"——这也是为什么换厂商不影响 Agent 代码（详见下一课）。</p>

<div class="card key">
    <li><span class="mono">run()</span> = 构建消息 → 注入上下文 → 调 ChatClient → 工具循环 → 返回。</li>
    <li>返回类型：非流式 <span class="mono">AgentResponse</span>；流式 <span class="mono">AgentResponseUpdate</span>。</li>
    <li>真实代码三步：<span class="mono">_prepare_run_context → _call_chat_client → _parse_response</span>。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>循环骨架由基类掌控</strong>，子类只插入"怎么调模型"这一块——经典的<strong>模板方法模式</strong>。
  三个扩展点（<span class="mono">_prepare_run_context / _call_chat_client / _parse_response</span>）让你在不同粒度介入。
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

<h2>Tracing a real run(): "What's the weather in Paris today?"</h2>
<p>Enough abstraction — let's walk one <strong>concrete input</strong> end to end. Assume this Agent carries a tool
<span class="mono">get_weather(city)</span> and you call <span class="mono">agent.run(&quot;What's the weather in Paris today?&quot;)</span>.
Each step below shows a <strong>real snapshot of the message list</strong> — watch it grow from 2 entries to 4, then collapse into a single <span class="mono">AgentResponse</span>.</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Assemble the initial messages (2)</h4>
    <p><span class="mono">_prepare_run_context()</span> (<span class="mono">_agents.py:1150</span>) concatenates the system instructions + your input, and attaches the tools:</p>
<pre class="code">messages = [
  Message(<span class="st">&quot;system&quot;</span>, [<span class="st">&quot;You are a weather assistant…&quot;</span>]),
  Message(<span class="st">&quot;user&quot;</span>,   [<span class="st">&quot;What's the weather in Paris today?&quot;</span>]),
]
tools = [get_weather]   <span class="cm"># tool schemas sent with the request</span></pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Hand off to the ChatClient (the loop lives there)</h4>
    <p><span class="mono">_call_chat_client()</span> (<span class="mono">_agents.py:985</span>) does exactly one thing: <span class="mono">client.get_response(messages, options)</span>.
    <strong>The tool loop is not in the Agent</strong> — it runs in the ChatClient's <span class="mono">FunctionInvocationLayer</span> (<span class="mono">_tools.py:2249</span>, next lesson). The Agent calls once.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>The model chooses to call a tool first</h4>
    <p>On the first turn the model doesn't answer directly; it returns a <span class="mono">function_call</span> content:</p>
<pre class="code">assistant_msg = Message(<span class="st">&quot;assistant&quot;</span>, [
  Content.from_function_call(
    call_id=<span class="st">&quot;call_1&quot;</span>, name=<span class="st">&quot;get_weather&quot;</span>,
    arguments=<span class="st">'{&quot;city&quot;: &quot;Paris&quot;}'</span>),  <span class="cm"># arguments is a JSON string</span>
])</pre></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Execute the tool; the working list grows to 4</h4>
    <p>The framework parses the args, calls your Python function <span class="mono">get_weather(&quot;Paris&quot;)</span> → <span class="mono">&quot;18°C sunny&quot;</span>,
    packs it as a <span class="mono">function_result</span> and appends it:</p>
<pre class="code">prepped_messages = [
  Message(<span class="st">&quot;system&quot;</span>,    [...]),
  Message(<span class="st">&quot;user&quot;</span>,      [...]),
  Message(<span class="st">&quot;assistant&quot;</span>, [function_call get_weather]),     <span class="cm"># 3rd</span>
  Message(<span class="st">&quot;tool&quot;</span>,      [function_result <span class="st">&quot;18°C sunny&quot;</span>]),  <span class="cm"># 4th</span>
]</pre></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Ask the model again, now with the result</h4>
    <p>The loop returns to the top and re-sends all 4 messages. This time the model has the weather data and need not call a tool.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Get the final text; the loop terminates</h4>
    <p>The model returns <span class="mono">Message(&quot;assistant&quot;, [&quot;It's 18°C and sunny in Paris.&quot;])</span> with no new
    <span class="mono">function_call</span> and <span class="mono">finish_reason=&quot;stop&quot;</span> → <span class="mono">FunctionInvocationLayer</span> exits the loop (capped at <span class="mono">DEFAULT_MAX_ITERATIONS=40</span>).</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>Wrap into an AgentResponse</h4>
    <p><span class="mono">_parse_non_streaming_response()</span> (<span class="mono">_agents.py:1013</span>) folds that <span class="mono">ChatResponse</span> into an <span class="mono">AgentResponse</span>:</p>
<pre class="code">resp = AgentResponse(messages=response.messages, …)
resp.text            <span class="cm"># &quot;It's 18°C and sunny in Paris.&quot;</span>
resp.messages        <span class="cm"># messages produced this run: function_call → function_result → final answer</span>
resp.usage_details   <span class="cm"># tokens summed across both model calls</span></pre></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 Reading this trace</div>
  The point isn't "how many steps" but that <strong>the message list is the only carrier of state</strong>: each model call is
  <strong>stateless</strong>, and the framework fabricates the illusion that "the model remembers it just checked the weather" purely by appending
  the previous turn's function_call and function_result into <em>the same</em> list and re-sending it.
  One commonly misread detail: the list that keeps growing inside the loop is the <strong>working list</strong> (<span class="mono">prepped_messages</span>),
  whereas <span class="mono">AgentResponse.messages</span> holds only the <strong>newly produced</strong> messages (not the system/user you passed in) — so don't expect to read your original input back out of the response.
</div>

<h2>Three layers in one: an Agent's true shape</h2>
<p>The <span class="mono">Agent</span> you <span class="mono">new</span> up is actually three layers stacked via <strong>Python multiple inheritance</strong>.
On <span class="mono">run()</span>, the request passes through them <strong>outside-in</strong> before reaching the <span class="mono">RawAgent</span> that does the real work:</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">Outer</span><span class="name">AgentMiddlewareLayer</span></div>
    <div class="ld">Middleware layer (<span class="mono">_middleware.py:1258</span>). Runs your registered <span class="mono">AgentMiddleware</span> first; can edit the request / result, or short-circuit.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Middle</span><span class="name">AgentTelemetryLayer</span></div>
    <div class="ld">Telemetry layer (from <span class="mono">observability</span>). Opens an OpenTelemetry span recording this run's latency / tokens / exceptions.</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">Core</span><span class="name">RawAgent</span></div>
    <div class="ld">The real loop skeleton (<span class="mono">_agents.py:578</span>): the 7 steps traced above live here.</div></div>
</div>
<p>This maps to the real definition <span class="mono">class Agent(AgentMiddlewareLayer, AgentTelemetryLayer, RawAgent, Generic[…])</span>
(<span class="mono">_agents.py:1584</span>). <strong>The method resolution order (MRO) forms the onion for free</strong>: middleware first, telemetry next, core last — you write no wrapping code at all.</p>

<h2>🔍 Real source: the three-step skeleton of run()</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_agents.py</span><span class="ln">RawAgent.run (simplified from :889)</span></div>
<pre class="code"><span class="kw">def</span> <span class="fn">run</span>(self, messages=<span class="kw">None</span>, *, stream=<span class="kw">False</span>, session=<span class="kw">None</span>,
        tools=<span class="kw">None</span>, options=<span class="kw">None</span>, …):
    <span class="kw">async def</span> <span class="fn">_prepare_run_context</span>():
        <span class="kw">return await</span> self._prepare_run_context(messages=messages, …)

    <span class="kw">if not</span> stream:                          <span class="cm"># ① non-streaming → returns AgentResponse</span>
        <span class="kw">async def</span> <span class="fn">_run_non_streaming</span>():
            ctx = <span class="kw">await</span> _prepare_run_context()    <span class="cm"># 1. assemble context</span>
            response = <span class="kw">await</span> self._call_chat_client(ctx, stream=<span class="kw">False</span>)  <span class="cm"># 2. call ChatClient</span>
            <span class="kw">return await</span> self._parse_non_streaming_response(ctx, response)  <span class="cm"># 3. parse</span>
        <span class="kw">return</span> _run_non_streaming()

    <span class="kw">async def</span> <span class="fn">_run_streaming</span>():            <span class="cm"># ② stream=True → returns an update stream</span>
        ctx = <span class="kw">await</span> _prepare_run_context()
        stream_response = self._call_chat_client(ctx, stream=<span class="kw">True</span>)
        <span class="kw">return</span> self._parse_streaming_response(ctx, stream_response)
    <span class="kw">return</span> ResponseStream.from_awaitable(_run_streaming())</pre>
</div>
<p>The three-step skeleton is plain to see: <strong>① prepare context → ② call ChatClient → ③ parse response</strong>. Streaming and non-streaming
<strong>share step ①</strong> and diverge only at ②③ — this is exactly where one <span class="mono">stream</span> bool toggles two return types, sparing you two near-identical methods.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> What does BaseAgent define? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a"><span class="mono">BaseAgent</span> (<span class="mono">_agents.py:314</span>) mandates
      <span class="mono">run()</span> (shared by streaming and non-streaming), <span class="mono">create_session()</span>,
      <span class="mono">get_session()</span>. Subclasses only implement these methods — the loop skeleton is in the base.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Without a unified interface every Agent type would need its own calling protocol,
      and orchestrators couldn't be generic. The abstract base guarantees "any Agent can <span class="mono">run()</span>" — the foundation of polymorphism.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">MAF uses the <strong>Template Method pattern</strong>: <span class="mono">BaseAgent</span>
      defines the skeleton, <span class="mono">RawAgent</span> / <span class="mono">Agent</span> implement in layers.
      This allows free extension without breaking the protocol.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">LangChain uses the <span class="mono">Runnable</span> protocol (more generic but looser);
      AutoGen uses <span class="mono">ConversableAgent</span> (tighter coupling). MAF picks a "just right" abstraction level and avoids over-generalisation.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Agent.run() internal call chain <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a"><span class="mono">Agent</span> (<span class="mono">_agents.py:1584</span>)'s <span class="mono">run()</span>
      passes through middleware / telemetry layers, then enters <span class="mono">RawAgent.run()</span> (<span class="mono">_agents.py:889</span>):
<pre class="code">_prepare_run_context()   <span class="cm"># assemble messages, session, tools, options</span>
_call_chat_client()      <span class="cm"># invoke ChatClient → ChatResponse</span>
_parse_non_streaming_response()  <span class="cm"># non-stream: convert to AgentResponse</span>
_parse_streaming_response()      <span class="cm"># stream: convert to AgentResponseUpdate</span>
_run_after_providers()   <span class="cm"># run ContextProvider post-hooks</span></pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Understanding the call chain tells you where to attach middleware, where to inject context,
      and which step to inspect when debugging — no more "black-box guessing".</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">Each step is its own method with a single responsibility.
      <span class="mono">_prepare_run_context()</span> only assembles messages; <span class="mono">_call_chat_client()</span> only calls the model.
      This lets subclasses <strong>override one step precisely</strong> without touching others.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Some frameworks put everything in one big <span class="mono">run()</span>;
      others use a declarative DAG (e.g. LangGraph). MAF's method decomposition + loop skeleton is a middle ground.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Custom Agent (RawAgent) <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a"><span class="mono">RawAgent</span> (<span class="mono">_agents.py:578</span>) is the core implementation layer —
      it extends <span class="mono">BaseAgent</span> and implements the full <span class="mono">run()</span>, context-provider execution,
      session management, and tool resolution. To fully take over Agent behavior, subclass <span class="mono">RawAgent</span>
      and override <span class="mono">_call_chat_client()</span>.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">The default <span class="mono">Agent</span> includes middleware and telemetry layers.
      Sometimes you need to skip them or replace the LLM-call logic entirely (e.g. mock testing) — that's when you need <span class="mono">RawAgent</span>.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">Agent = AgentMiddlewareLayer + AgentTelemetryLayer + RawAgent</span>.
      Three layers combined via Python multiple inheritance — you can pick any subset. This <strong>Mixin pattern</strong> is far more flexible than a single inheritance chain.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Decorator pattern wrapping (more runtime overhead), or feature-flags
      (less flexible). MAF's mixin approach locks in behavior at class-definition time with zero extra runtime cost.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> AgentResponse structure <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a"><span class="mono">AgentResponse</span> (<span class="mono">_types.py:2530</span>) core fields:
<pre class="code">response.text           <span class="cm"># combined text from all messages</span>
response.messages       <span class="cm"># list[Message] — full message list</span>
response.usage_details  <span class="cm"># UsageDetails — prompt/completion tokens</span>
response.finish_reason  <span class="cm"># &quot;stop&quot; / &quot;tool_calls&quot; / &quot;length&quot;</span>
response.value          <span class="cm"># structured output (if response_format set)</span>
response.raw_representation  <span class="cm"># raw API response</span></pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Knowing the response structure lets you: extract reply text, check token usage for cost control,
      determine if the model stopped normally or was truncated, and get structured data without manual JSON parsing.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">.text</span> is a read-only property (auto-joins all messages).
      <span class="mono">.value</span> supports generics — if you declared <span class="mono">response_format=MyModel</span>,
      <span class="mono">.value</span> automatically returns a <span class="mono">MyModel</span> instance, no manual deserialisation needed.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">OpenAI SDK returns dict/dataclass; LangChain uses <span class="mono">AIMessage</span>.
      MAF's <span class="mono">AgentResponse</span> adds generic <span class="mono">.value</span> and <span class="mono">.continuation_token</span>
      (resumable long conversations), better suited for production.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> RawAgent vs Agent <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code"><span class="cm"># Agent = full-featured (middleware + telemetry + RawAgent)</span>
agent = Agent(name=<span class="st">&quot;full&quot;</span>, client=client,
              middleware=[LogMiddleware()])

<span class="cm"># RawAgent = minimal core (no middleware / telemetry)</span>
raw = RawAgent(name=<span class="st">&quot;bare&quot;</span>, client=client)</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">For unit tests or lightweight calls, <span class="mono">Agent</span>'s middleware/telemetry layers are unnecessary overhead.
      In production you almost always want logging and monitoring — <span class="mono">Agent</span> gives you that out of the box.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">Both share the <span class="mono">BaseAgent</span> protocol, so they are <strong>fully interchangeable</strong> for orchestrators.
      Develop with <span class="mono">RawAgent</span> for fast iteration, switch to <span class="mono">Agent</span> with middleware for production — callers need zero changes.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Some frameworks have one Agent class with a <span class="mono">debug=True</span> switch.
      MAF's layered inheritance is cleaner — unwanted layers simply don't exist, rather than "present but skipped by an if".</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">6</span> 🔍 Real source: the run() implementation <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 From _agents.py</div>
      <div class="a">The core of <span class="mono">RawAgent.run()</span> (<span class="mono">_agents.py:952</span>), simplified:
<pre class="code"><span class="cm"># _agents.py — RawAgent.run() core (simplified)</span>

<span class="kw">async def</span> _prepare_run_context():
    <span class="kw">return await</span> self._prepare_run_context(
        messages=messages, session=session,
        tools=tools, options=options, ...)

<span class="kw">if not</span> stream:
    <span class="kw">async def</span> <span class="fn">_run_non_streaming</span>():
        ctx = <span class="kw">await</span> _prepare_run_context()
        response = <span class="kw">await</span> self._call_chat_client(ctx, stream=<span class="kw">False</span>)
        <span class="kw">return await</span> self._parse_non_streaming_response(ctx, response)
    <span class="kw">return</span> _run_non_streaming()

<span class="cm"># stream=True branch</span>
<span class="kw">async def</span> <span class="fn">_run_streaming</span>():
    ctx = <span class="kw">await</span> _prepare_run_context()
    stream_response = self._call_chat_client(ctx, stream=<span class="kw">True</span>)
    <span class="kw">return</span> self._parse_streaming_response(ctx, stream_response)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this code matters</div>
      <div class="a">Three steps are clearly visible: <strong>①prepare context → ②call ChatClient → ③parse response</strong>.
        Streaming and non-streaming share the same <span class="mono">_prepare_run_context</span>; they differ only in steps ②③.
        Note: <strong>the tool loop is not in these three steps</strong> — <span class="mono">_call_chat_client</span> calls <span class="mono">client.get_response()</span> just once;
        the multi-turn function_call ↔ function_result loop runs in the ChatClient's <span class="mono">FunctionInvocationLayer</span> (<span class="mono">_tools.py:2249</span>),
        so the <span class="mono">ChatResponse</span> that <span class="mono">_parse_non_streaming_response</span> receives is already the "after the tools ran" final result.</div>
    </div>
    <div class="qa">
      <div class="q">✅ What _call_chat_client does</div>
      <div class="a">It directly calls <span class="mono">self.client.get_response(messages=..., stream=..., options=...)</span> —
        forwarding assembled messages, tool schemas and ChatOptions to the ChatClient.
        <strong>This is the boundary between Agent and ChatClient</strong>: Agent owns "assembly", ChatClient owns "communication".</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Extension points</div>
      <div class="a">Override <span class="mono">_call_chat_client()</span>: customise "how to call the model".
        Override <span class="mono">_prepare_run_context()</span>: customise "how to assemble messages".
        Add middleware: intercept without touching source.
        Three extension points, from coarsest to finest grain.</div>
    </div>
  </div>
</details>

<h2>Why it's designed this way</h2>
<p><strong>① Template method + layering = testability.</strong> Nailing the "loop skeleton" into the base class and leaving only "how to call the model"
to <span class="mono">_call_chat_client()</span> means a unit test only has to override that <strong>one</strong> method to return a fake <span class="mono">ChatResponse</span> —
letting you verify the entire run logic offline, without burning tokens. If the loop and the network call were fused into one big function, that isolation would be nearly impossible.</p>
<p><strong>② Mixin inheritance = composability at zero runtime cost.</strong> The middleware, telemetry and core layers are three independent classes threaded into an onion by the MRO,
not toggled with runtime flags like <span class="mono">if self.enable_telemetry:</span>. Want a lightweight variant? Use <span class="mono">RawAgent</span> and those two layers <strong>simply aren't in</strong> the MRO —
no "check-then-skip" branch cost; want everything? Use <span class="mono">Agent</span> and all three snap into place. The presence/absence of a feature is decided at <strong>class-definition time</strong>.</p>
<p><strong>③ Pushing the tool loop down into the ChatClient = separation of concerns.</strong> The Agent only "assembles context + parses results", while the complex job of
"shuttling back and forth with the model and executing tools" belongs to <span class="mono">FunctionInvocationLayer</span>. As a result <strong>the same tool loop is reused by any ChatClient</strong>,
and the Agent layer stays "thin" — which is also why swapping vendors doesn't touch Agent code (see the next lesson).</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><span class="mono">BaseAgent</span> (abstract) defines the protocol; <span class="mono">Agent</span> (concrete) implements assembly + loop.</li>
    <li><span class="mono">run()</span> = build messages → inject context → call ChatClient → tool loop → return.</li>
    <li>Return types: non-streaming <span class="mono">AgentResponse</span>; streaming <span class="mono">AgentResponseUpdate</span>.</li>
    <li>Real code: <span class="mono">_prepare_run_context → _call_chat_client → _parse_response</span>.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>The loop skeleton is owned by the base class</strong>; subclasses only plug in "how to call the model"
  — the classic <strong>Template Method pattern</strong>. Three extension points (<span class="mono">_prepare_run_context / _call_chat_client / _parse_response</span>) let you intervene at different granularities.
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

<h2>追踪一次真实 get_response()：从消息到 ChatResponse</h2>
<p>骨架讲完了，我们用一次<strong>真实调用</strong>端到端走一遍。假设上层（Agent 或工具循环层）执行
<span class="mono">client.get_response(messages, options=ChatOptions(model=&quot;gpt-4o&quot;))</span>，
看请求如何穿过基类、落到厂商实现，再把<strong>厂商专属 JSON</strong> 收敛成统一的 <span class="mono">ChatResponse</span>。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>公共入口：先决定要不要压缩</h4>
    <p><span class="mono">get_response()</span>（<span class="mono">_clients.py:482</span>）做的第一件事是
    <span class="mono">_resolve_compaction_overrides()</span>——把「本次调用传入的」与「client 上预设的」compaction 策略合并：</p>
<pre class="code">overrides = self._resolve_compaction_overrides(
    compaction_strategy=compaction_strategy, tokenizer=tokenizer)
merged_client_kwargs = dict(client_kwargs <span class="kw">or</span> {})</pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>无压缩 → 原样直接转发</h4>
    <p>若 <span class="mono">overrides</span> 为空（最常见路径），基类<strong>什么都不加工</strong>，把消息原封不动转发给厂商实现：</p>
<pre class="code"><span class="kw">if not</span> overrides:
    <span class="kw">return</span> self._inner_get_response(
        messages=messages, stream=stream,
        options=options <span class="kw">or</span> {}, **merged_client_kwargs)</pre></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>有压缩 → 先 _prepare 再调</h4>
    <p>若设了 compaction，基类先 <span class="mono">await _prepare_messages_for_model_call()</span>（<span class="mono">_clients.py:366</span>）
    在<strong>同一个 list</strong> 上原地压缩 / 标注，再调厂商实现。无论走哪条路，<span class="mono">_inner_get_response()</span> 在一次 <span class="mono">get_response</span> 里<strong>只被调用一次</strong>。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>厂商实现：MAF 消息 → 厂商请求</h4>
    <p>进入子类的 <span class="mono">_inner_get_response()</span>（抽象声明在 <span class="mono">_clients.py:415</span>）。它先
    <span class="mono">await self._validate_options(options)</span>（<span class="mono">_clients.py:329</span>），再把 MAF 的 <span class="mono">Message</span> 列表翻成那家 API 的字段：</p>
<pre class="code"><span class="cm"># 以 OpenAI 兼容格式为例</span>
payload = {<span class="st">&quot;model&quot;</span>: <span class="st">&quot;gpt-4o&quot;</span>, <span class="st">&quot;messages&quot;</span>: [
  {<span class="st">&quot;role&quot;</span>: <span class="st">&quot;system&quot;</span>, <span class="st">&quot;content&quot;</span>: <span class="st">&quot;…&quot;</span>},
  {<span class="st">&quot;role&quot;</span>: <span class="st">&quot;user&quot;</span>, <span class="st">&quot;content&quot;</span>: <span class="st">&quot;巴黎今天天气如何？&quot;</span>}]}</pre></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>真实网络调用，拿回厂商 JSON</h4>
    <p>发出 HTTP 请求，得到厂商<strong>专属结构</strong>的原始响应——每家字段名都不一样：</p>
<pre class="code">{<span class="st">&quot;id&quot;</span>: <span class="st">&quot;chatcmpl-9x…&quot;</span>, <span class="st">&quot;model&quot;</span>: <span class="st">&quot;gpt-4o-2024…&quot;</span>,
 <span class="st">&quot;choices&quot;</span>: [{<span class="st">&quot;message&quot;</span>: {<span class="st">&quot;content&quot;</span>: <span class="st">&quot;18°C，晴。&quot;</span>},
              <span class="st">&quot;finish_reason&quot;</span>: <span class="st">&quot;stop&quot;</span>}],
 <span class="st">&quot;usage&quot;</span>: {<span class="st">&quot;prompt_tokens&quot;</span>: 42, <span class="st">&quot;completion_tokens&quot;</span>: 9}}</pre></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>归一化：厂商 JSON → 统一 ChatResponse</h4>
    <p>子类把上面的 JSON 逐字段映射进框架统一的 <span class="mono">ChatResponse</span>（构造器见 <span class="mono">_types.py:2122</span>）：</p>
<pre class="code"><span class="kw">return</span> ChatResponse(
    messages=[Message(<span class="st">&quot;assistant&quot;</span>, [<span class="st">&quot;18°C，晴。&quot;</span>])],
    response_id=<span class="st">&quot;chatcmpl-9x…&quot;</span>, model=<span class="st">&quot;gpt-4o-2024…&quot;</span>,
    finish_reason=<span class="st">&quot;stop&quot;</span>,
    usage_details=UsageDetails(
        input_token_count=42, output_token_count=9))</pre></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>上层只看见统一类型</h4>
    <p>这个 <span class="mono">ChatResponse</span> 一路原样返回。上层（Agent、工具循环、你的代码）<strong>永远只看到统一类型</strong>，
    完全不知道下面是 OpenAI 还是 Foundry——换厂商，上层零改动。</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 读懂这条轨迹</div>
  关键在第 ⑥ 步：<strong>归一化发生在子类内部</strong>，而不是基类。基类 <span class="mono">get_response()</span> 只管「压不压缩 + 转发」这件通用事，
  「怎么把那家 JSON 翻成 <span class="mono">ChatResponse</span>」交给最懂那家 API 的子类。于是新增一个厂商，<strong>基类一行都不用改</strong>。
</div>

<h2>厂商原始 JSON → 统一 ChatResponse 字段</h2>
<p>第 ⑥ 步那次「逐字段映射」到底映了什么？下表把 OpenAI 风格的原始 JSON 和框架统一的
<span class="mono">ChatResponse</span> 字段一一对照——注意 token 计数的<strong>改名</strong>，这正是归一化最容易被忽略的细节：</p>
<table class="t">
  <tr><th>厂商原始 JSON（OpenAI 风格）</th><th>统一 ChatResponse 字段</th><th>类型 / 说明</th></tr>
  <tr><td class="mono">id</td><td class="mono">response_id</td><td>本次响应的唯一 ID</td></tr>
  <tr><td class="mono">model</td><td class="mono">model</td><td>实际使用的模型名</td></tr>
  <tr><td class="mono">choices[0].message.content</td><td class="mono">messages[0]</td><td>装进一条 <span class="mono">Message(&quot;assistant&quot;, …)</span></td></tr>
  <tr><td class="mono">choices[0].message.tool_calls</td><td class="mono">messages[0].contents</td><td>转成 <span class="mono">function_call</span> 类型的 <span class="mono">Content</span></td></tr>
  <tr><td class="mono">choices[0].finish_reason</td><td class="mono">finish_reason</td><td><span class="mono">&quot;stop&quot;/&quot;tool_calls&quot;/&quot;length&quot;</span>（<span class="mono">_types.py:1642</span>）</td></tr>
  <tr><td class="mono">usage.prompt_tokens</td><td class="mono">usage_details.input_token_count</td><td><strong>字段名变了</strong></td></tr>
  <tr><td class="mono">usage.completion_tokens</td><td class="mono">usage_details.output_token_count</td><td><strong>字段名变了</strong></td></tr>
  <tr><td class="mono">usage.total_tokens</td><td class="mono">usage_details.total_token_count</td><td><span class="mono">UsageDetails</span>（<span class="mono">_types.py:393</span>）</td></tr>
</table>

<h2>四层洋葱：一个 ChatClient 的真身</h2>
<p>和上一课的 <span class="mono">Agent</span> 一样，你拿到的 ChatClient 也是用 <strong>Python 多继承</strong>把若干「层」叠在
<span class="mono">BaseChatClient</span> 外面。一次 <span class="mono">get_response()</span> 请求<strong>从外到内</strong>穿过这些层，最后才落到厂商的 <span class="mono">_inner_get_response()</span>：</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">最外</span><span class="name">FunctionInvocationLayer</span></div>
    <div class="ld">函数调用层（<span class="mono">_tools.py:2249</span>）。<strong>上一课那个工具循环就住在这里</strong>——它反复 <span class="mono">super().get_response()</span> 直到不再出现新的 function_call。</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">中间件</span><span class="name">ChatMiddlewareLayer</span></div>
    <div class="ld">聊天中间件层（<span class="mono">_middleware.py:1108</span>）。跑你注册的 <span class="mono">ChatMiddleware</span>，可在「真正调模型」前后改请求 / 改响应 / 短路。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">遥测</span><span class="name">ChatTelemetryLayer</span></div>
    <div class="ld">遥测层（<span class="mono">observability.py:1354</span>）。为每次模型调用开一个 OpenTelemetry span，记录耗时 / token / 异常。</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">核心</span><span class="name">BaseChatClient</span></div>
    <div class="ld">抽象基类（<span class="mono">_clients.py:217</span>）。定义公共 <span class="mono">get_response()</span> + 抽象 <span class="mono">_inner_get_response()</span>——厂商唯一要填的洞。</div></div>
</div>
<p>真实代码里，一个 provider 大致是
<span class="mono">class XxxChatClient(FunctionInvocationLayer, ChatTelemetryLayer, BaseChatClient)</span>
这样多继承组合的（同款 MRO 见源码测试 <span class="mono">test_observability.py:4141</span>；四层完整顺序见 <span class="mono">:2939</span> 文档：
<span class="mono">FunctionInvocationLayer → ChatMiddlewareLayer → ChatTelemetryLayer → BaseChatClient</span>）。
和 Agent 的设计如出一辙：<strong>能力靠「叠层」而非「运行时开关」决定</strong>——要裸客户端就只继承
<span class="mono">BaseChatClient</span>，要工具循环就把 <span class="mono">FunctionInvocationLayer</span> 叠上去。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 厂商怎么实现 _inner_get_response? <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">以 FoundryChatClient 为例：它继承 <span class="mono">BaseChatClient</span>，只覆写
      <span class="mono">_inner_get_response</span>——把 MAF 的 <span class="mono">Message</span> 列表转成 Foundry SDK 格式、
      调 API、再把结果转回 <span class="mono">ChatResponse</span>。若 <span class="mono">stream=True</span>，返回异步生成器。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">不同 LLM 厂商的 API 格式完全不同。如果让调用方自己适配，
      换一个模型就要改一堆代码。统一封装在 <span class="mono">_inner_get_response</span> 里，上层代码零改动。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">子类只需实现一个抽象方法，签名固定：
      <span class="mono">_inner_get_response(*, messages, stream, options, **kwargs)</span>。
      基类负责通用逻辑（重试、中间件、compaction），子类只管"怎么和那家 API 通信"。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">LiteLLM 用一个巨大的 if/elif 分发到各厂商；
      LangChain 每个厂商写一整套类。MAF 的"一个抽象方法"方案最简洁——新增厂商只需一个类 + 一个方法。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> get_response 的完整签名 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a"><span class="mono">get_response()</span>（<span class="mono">_clients.py:482</span>）完整签名：
<pre class="code">get_response(
  messages: Sequence[Message],
  *, <span class="cm"># 以下全是关键字参数</span>
  stream: bool = False,
  options: ChatOptions | None = None,
  compaction_strategy: CompactionStrategy | None,
  tokenizer: TokenizerProtocol | None,
  function_invocation_kwargs: Mapping | None,
  client_kwargs: Mapping | None,
)</pre>
      返回 <span class="mono">ChatResponse</span>（非流式）或 <span class="mono">ResponseStream[ChatResponseUpdate, ChatResponse]</span>（流式）。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">知道所有参数才能精细控制：<span class="mono">compaction_strategy</span> 决定消息过长时如何压缩，
      <span class="mono">client_kwargs</span> 可透传厂商特有参数，<span class="mono">function_invocation_kwargs</span> 转发给工具调用。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">只有 <span class="mono">messages</span> 是位置参数，其余全是 <strong>keyword-only</strong>，
      避免参数顺序错误。<span class="mono">stream</span> 用布尔切换返回类型，无需两个方法。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">OpenAI SDK 用 <span class="mono">create()</span> 加大量 kwargs；
      Anthropic 用 <span class="mono">messages.create()</span>。MAF 统一为一个入口 + keyword 参数，更易发现、更难用错。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> ChatResponse 的内部结构 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a"><span class="mono">ChatResponse</span>（<span class="mono">_types.py:2122</span>）核心字段：
<pre class="code">resp.messages       <span class="cm"># list[Message] — 模型回复的消息</span>
resp.text           <span class="cm"># 所有消息文本拼合（只读属性）</span>
resp.model          <span class="cm"># 实际使用的模型名</span>
resp.usage_details  <span class="cm"># UsageDetails（input_token_count, output_token_count, total_token_count）</span>
resp.finish_reason  <span class="cm"># &quot;stop&quot; / &quot;tool_calls&quot; / &quot;length&quot;</span>
resp.value          <span class="cm"># 泛型结构化输出</span>
resp.conversation_id  <span class="cm"># 会话状态标识</span></pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a"><span class="mono">ChatResponse</span> 是 Agent 内部循环的"原子交换单位"——
      每次 LLM 调用返回一个 <span class="mono">ChatResponse</span>，Agent 检查 <span class="mono">finish_reason</span> 决定是继续工具循环还是结束。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">.text</span> 自动拼合，省去手动遍历 messages。
      <span class="mono">.value</span> 支持泛型，<span class="mono">ChatResponse[MyModel]</span> 的 <span class="mono">.value</span> 直接是 <span class="mono">MyModel</span> 实例。
      <span class="mono">.raw_representation</span> 保留原始响应，便于调试。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">有的框架只返回字符串；有的返回 dict。
      MAF 的强类型 dataclass 提供自动补全和类型检查，在 IDE 里开发体验远优于 dict。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 自己写一个 ChatClient <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">最小自定义 <span class="mono">BaseChatClient</span> 子类骨架：
<pre class="code"><span class="kw">class</span> <span class="fn">MyChatClient</span>(BaseChatClient):
    <span class="kw">async def</span> <span class="fn">_inner_get_response</span>(
        self, *, messages, stream, options, **kwargs
    ):
        <span class="cm"># 1. 把 MAF Message 转成你的 API 格式</span>
        <span class="cm"># 2. 调用你的 LLM API</span>
        <span class="cm"># 3. 把结果转回 ChatResponse</span>
        <span class="kw">return</span> ChatResponse(messages=[...], model=<span class="st">&quot;my-model&quot;</span>)</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">如果你要接入一个 MAF 还没有官方 provider 的模型（私有部署、小众厂商），
      就需要自己写。只需实现 <strong>一个方法</strong>，门槛极低。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">基类 <span class="mono">BaseChatClient</span>（<span class="mono">_clients.py:217</span>）
      已处理中间件触发、compaction、选项验证。你只写"和 API 通信"这一块，其他全部复用。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">可以用 Adapter 模式包裹现有 SDK（更多胶水代码），
      或者直接在 Agent 层换掉调用逻辑（不复用基类功能）。MAF 的"子类 + 一个方法"最简洁且复用最多。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> ChatOptions 详解 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a"><span class="mono">ChatOptions</span>（<span class="mono">_types.py:3346</span>）常用字段：
<pre class="code">options = ChatOptions(
  model=<span class="st">&quot;gpt-4o&quot;</span>,
  temperature=0.7,
  max_tokens=2048,
  top_p=0.9,
  stop=[<span class="st">&quot;\n\n&quot;</span>],
  tool_choice=<span class="st">&quot;auto&quot;</span>,
  response_format=MyModel,  <span class="cm"># 结构化输出</span>
)</pre>
      还有 <span class="mono">frequency_penalty</span>、<span class="mono">presence_penalty</span>、<span class="mono">seed</span>、
      <span class="mono">logit_bias</span>、<span class="mono">metadata</span>、<span class="mono">instructions</span> 等。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">不同任务需要不同参数：创意写作要高 temperature，代码生成要低 temperature + <span class="mono">stop</span> 序列。
      <span class="mono">ChatOptions</span> 是"一个对象传递所有模型参数"的标准方式。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">ChatOptions</span> 是 <span class="mono">TypedDict</span>，
      所以你在 IDE 里能看到所有合法字段 + 自动补全。它和 <span class="mono">get_response(options=...)</span> 无缝对接，
      且 <span class="mono">tool_choice</span> 支持 <span class="mono">&quot;auto&quot;</span> / <span class="mono">&quot;required&quot;</span> / <span class="mono">&quot;none&quot;</span>，精确控制工具调用行为。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">直接传 <span class="mono">**kwargs</span>（无类型提示）；
      或每个参数做 <span class="mono">get_response()</span> 的独立参数（签名爆炸）。
      <span class="mono">TypedDict</span> 在灵活性和类型安全之间找到了最佳平衡。</div></div>
  </div>
</details>

<h2>🔍 真实源码：get_response 的骨架</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_clients.py</span><span class="ln">BaseChatClient.get_response（简化自 :482）</span></div>
<pre class="code"><span class="kw">def</span> <span class="fn">get_response</span>(self, messages, *, stream=<span class="kw">False</span>, options=<span class="kw">None</span>,
        compaction_strategy=<span class="kw">None</span>, tokenizer=<span class="kw">None</span>,
        function_invocation_kwargs=<span class="kw">None</span>, client_kwargs=<span class="kw">None</span>):
    overrides = self._resolve_compaction_overrides(      <span class="cm"># 合并 compaction 设置</span>
        compaction_strategy=compaction_strategy, tokenizer=tokenizer)
    merged_client_kwargs = dict(client_kwargs <span class="kw">or</span> {})

    <span class="kw">if not</span> overrides:                                   <span class="cm"># ① 无压缩：原样转发</span>
        <span class="kw">return</span> self._inner_get_response(
            messages=messages, stream=stream,
            options=options <span class="kw">or</span> {}, **merged_client_kwargs)

    <span class="kw">async def</span> <span class="fn">_get_response</span>():                        <span class="cm"># ② 有压缩：先 prepare 再调</span>
        prepared = <span class="kw">await</span> self._prepare_messages_for_model_call(
            messages, **overrides)
        <span class="kw">return await</span> self._inner_get_response(
            messages=prepared, stream=<span class="kw">False</span>,
            options=options <span class="kw">or</span> {}, **merged_client_kwargs)
    <span class="kw">return</span> _get_response()</pre>
</div>
<p>骨架就两条路：<strong>①无压缩直接转发、②有压缩先 <span class="mono">_prepare</span> 再转发</strong>，但两条路<strong>都只调一次</strong>
<span class="mono">_inner_get_response()</span>。基类自己<strong>不碰任何厂商字段</strong>——它把「翻译 + 网络 + 归一化」整块交给子类。
这就是「公共骨架」与「厂商扩展点」的分界线：上半截（这段代码）人人共用，下半截（<span class="mono">_inner_get_response</span>）各厂商各写。</p>

<h2>为什么统一成一个 ChatResponse</h2>
<p>你可能会问：既然每家 API 返回的 JSON 都不一样，为什么非要在子类里多写一道「翻译」、统一成
<span class="mono">ChatResponse</span>？直接把厂商的 dict 透传上去不是更省事吗？答案是<strong>把「易变」挡在「稳定」外面</strong>。
厂商的 JSON 字段名、嵌套结构随时可能变（OpenAI 把 token 叫 <span class="mono">prompt_tokens</span>，框架统一叫
<span class="mono">input_token_count</span>）；如果上层直接读厂商字段，换一家或厂商一升级，<strong>整条调用链都要跟着改</strong>。</p>
<p>归一化把这种「易变」锁死在<strong>子类的一个方法</strong>里：上层永远只认 <span class="mono">ChatResponse.text</span> /
<span class="mono">.finish_reason</span> / <span class="mono">.usage_details</span> 这套稳定字段。于是 Agent 的工具循环靠
<span class="mono">finish_reason==&quot;tool_calls&quot;</span> 判断要不要继续，<strong>根本不需要知道下面是哪家模型</strong>——这正是
L08 那个「换模型零改动」承诺能成立的底层原因。</p>
<p>更妙的是 <span class="mono">.raw_representation</span> 仍保留了厂商原始响应：<strong>统一字段满足 99% 需求，逃生舱口满足剩下 1%</strong>。
你既享受到强类型的整洁，又不会在需要某个厂商专属字段时被框架挡死。这就是「窄接口 + 逃生舱」的经典权衡。</p>

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

<h2>Tracing a real get_response(): from messages to ChatResponse</h2>
<p>The skeleton is clear; let's walk one <strong>real call</strong> end to end. Say the upper layer (Agent or the tool loop)
runs <span class="mono">client.get_response(messages, options=ChatOptions(model=&quot;gpt-4o&quot;))</span>.
Watch how the request passes through the base class, lands in the vendor implementation, then collapses
<strong>vendor-specific JSON</strong> into a unified <span class="mono">ChatResponse</span>.</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Public entry: decide whether to compact</h4>
    <p>The first thing <span class="mono">get_response()</span> (<span class="mono">_clients.py:482</span>) does is
    <span class="mono">_resolve_compaction_overrides()</span> — merging the per-call strategy with the client-level default:</p>
<pre class="code">overrides = self._resolve_compaction_overrides(
    compaction_strategy=compaction_strategy, tokenizer=tokenizer)
merged_client_kwargs = dict(client_kwargs <span class="kw">or</span> {})</pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>No compaction → forward as-is</h4>
    <p>If <span class="mono">overrides</span> is empty (the common path), the base class <strong>touches nothing</strong> and forwards the messages straight to the vendor impl:</p>
<pre class="code"><span class="kw">if not</span> overrides:
    <span class="kw">return</span> self._inner_get_response(
        messages=messages, stream=stream,
        options=options <span class="kw">or</span> {}, **merged_client_kwargs)</pre></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Compaction set → _prepare, then call</h4>
    <p>If compaction is configured, the base first <span class="mono">await _prepare_messages_for_model_call()</span>
    (<span class="mono">_clients.py:366</span>) compacts/annotates <strong>in the same list</strong>, then calls the vendor impl.
    Either way, <span class="mono">_inner_get_response()</span> is called <strong>exactly once</strong> per <span class="mono">get_response</span>.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Vendor impl: MAF messages → vendor request</h4>
    <p>Now inside the subclass's <span class="mono">_inner_get_response()</span> (abstract decl at <span class="mono">_clients.py:415</span>).
    It first <span class="mono">await self._validate_options(options)</span> (<span class="mono">_clients.py:329</span>), then translates MAF <span class="mono">Message</span> objects into that API's fields:</p>
<pre class="code"><span class="cm"># OpenAI-compatible shape</span>
payload = {<span class="st">&quot;model&quot;</span>: <span class="st">&quot;gpt-4o&quot;</span>, <span class="st">&quot;messages&quot;</span>: [
  {<span class="st">&quot;role&quot;</span>: <span class="st">&quot;system&quot;</span>, <span class="st">&quot;content&quot;</span>: <span class="st">&quot;…&quot;</span>},
  {<span class="st">&quot;role&quot;</span>: <span class="st">&quot;user&quot;</span>, <span class="st">&quot;content&quot;</span>: <span class="st">&quot;What's the weather in Paris?&quot;</span>}]}</pre></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Real network call → vendor JSON</h4>
    <p>The HTTP request goes out and returns the vendor's <strong>own structure</strong> — every provider names fields differently:</p>
<pre class="code">{<span class="st">&quot;id&quot;</span>: <span class="st">&quot;chatcmpl-9x…&quot;</span>, <span class="st">&quot;model&quot;</span>: <span class="st">&quot;gpt-4o-2024…&quot;</span>,
 <span class="st">&quot;choices&quot;</span>: [{<span class="st">&quot;message&quot;</span>: {<span class="st">&quot;content&quot;</span>: <span class="st">&quot;18°C, sunny.&quot;</span>},
              <span class="st">&quot;finish_reason&quot;</span>: <span class="st">&quot;stop&quot;</span>}],
 <span class="st">&quot;usage&quot;</span>: {<span class="st">&quot;prompt_tokens&quot;</span>: 42, <span class="st">&quot;completion_tokens&quot;</span>: 9}}</pre></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Normalize: vendor JSON → unified ChatResponse</h4>
    <p>The subclass maps that JSON field-by-field into the framework's unified <span class="mono">ChatResponse</span> (constructor at <span class="mono">_types.py:2122</span>):</p>
<pre class="code"><span class="kw">return</span> ChatResponse(
    messages=[Message(<span class="st">&quot;assistant&quot;</span>, [<span class="st">&quot;18°C, sunny.&quot;</span>])],
    response_id=<span class="st">&quot;chatcmpl-9x…&quot;</span>, model=<span class="st">&quot;gpt-4o-2024…&quot;</span>,
    finish_reason=<span class="st">&quot;stop&quot;</span>,
    usage_details=UsageDetails(
        input_token_count=42, output_token_count=9))</pre></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>Upper layers only ever see the unified type</h4>
    <p>That <span class="mono">ChatResponse</span> bubbles straight back up. The upper layers (Agent, tool loop, your code)
    <strong>only ever see the unified type</strong> — they have no idea whether OpenAI or Foundry is underneath. Swap vendors, change nothing upstream.</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 Reading this trace</div>
  The key is step ⑥: <strong>normalization happens inside the subclass</strong>, not the base. The base
  <span class="mono">get_response()</span> only does the generic "compact-or-not + forward"; "how to translate that JSON into a
  <span class="mono">ChatResponse</span>" is left to the subclass that knows the API best. So adding a vendor means <strong>not one line changes in the base</strong>.
</div>

<h2>Vendor raw JSON → unified ChatResponse fields</h2>
<p>What exactly did that step-⑥ mapping map? The table below pairs OpenAI-style raw JSON with the framework's unified
<span class="mono">ChatResponse</span> fields — note the token-count <strong>rename</strong>, the most easily overlooked part of normalization:</p>
<table class="t">
  <tr><th>Vendor raw JSON (OpenAI-style)</th><th>Unified ChatResponse field</th><th>Type / note</th></tr>
  <tr><td class="mono">id</td><td class="mono">response_id</td><td>unique id of this response</td></tr>
  <tr><td class="mono">model</td><td class="mono">model</td><td>actual model name used</td></tr>
  <tr><td class="mono">choices[0].message.content</td><td class="mono">messages[0]</td><td>wrapped in a <span class="mono">Message(&quot;assistant&quot;, …)</span></td></tr>
  <tr><td class="mono">choices[0].message.tool_calls</td><td class="mono">messages[0].contents</td><td>becomes a <span class="mono">function_call</span> <span class="mono">Content</span></td></tr>
  <tr><td class="mono">choices[0].finish_reason</td><td class="mono">finish_reason</td><td><span class="mono">&quot;stop&quot;/&quot;tool_calls&quot;/&quot;length&quot;</span> (<span class="mono">_types.py:1642</span>)</td></tr>
  <tr><td class="mono">usage.prompt_tokens</td><td class="mono">usage_details.input_token_count</td><td><strong>field renamed</strong></td></tr>
  <tr><td class="mono">usage.completion_tokens</td><td class="mono">usage_details.output_token_count</td><td><strong>field renamed</strong></td></tr>
  <tr><td class="mono">usage.total_tokens</td><td class="mono">usage_details.total_token_count</td><td><span class="mono">UsageDetails</span> (<span class="mono">_types.py:393</span>)</td></tr>
</table>

<h2>Four-layer onion: what a ChatClient really is</h2>
<p>Just like the <span class="mono">Agent</span> last lesson, the ChatClient you hold is also several "layers" stacked on top of
<span class="mono">BaseChatClient</span> via <strong>Python multiple inheritance</strong>. One <span class="mono">get_response()</span> request passes
<strong>outside-in</strong> through these layers before landing in the vendor's <span class="mono">_inner_get_response()</span>:</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">Outer</span><span class="name">FunctionInvocationLayer</span></div>
    <div class="ld">Function-calling layer (<span class="mono">_tools.py:2249</span>). <strong>Last lesson's tool loop lives here</strong> — it repeatedly calls <span class="mono">super().get_response()</span> until no new function_call appears.</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">Middleware</span><span class="name">ChatMiddlewareLayer</span></div>
    <div class="ld">Chat-middleware layer (<span class="mono">_middleware.py:1108</span>). Runs your <span class="mono">ChatMiddleware</span>, which can edit the request/response or short-circuit around the real model call.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Telemetry</span><span class="name">ChatTelemetryLayer</span></div>
    <div class="ld">Telemetry layer (<span class="mono">observability.py:1354</span>). Opens an OpenTelemetry span per model call, recording latency / tokens / errors.</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">Core</span><span class="name">BaseChatClient</span></div>
    <div class="ld">Abstract base (<span class="mono">_clients.py:217</span>). Defines the public <span class="mono">get_response()</span> + abstract <span class="mono">_inner_get_response()</span> — the one hole vendors must fill.</div></div>
</div>
<p>In real code a provider is roughly
<span class="mono">class XxxChatClient(FunctionInvocationLayer, ChatTelemetryLayer, BaseChatClient)</span>
(the same MRO appears in the source tests, <span class="mono">test_observability.py:4141</span>; the full four-layer order is documented at <span class="mono">:2939</span>:
<span class="mono">FunctionInvocationLayer → ChatMiddlewareLayer → ChatTelemetryLayer → BaseChatClient</span>).
Identical philosophy to the Agent: <strong>capability is decided by "stacked layers", not "runtime flags"</strong> — want a bare client?
inherit only <span class="mono">BaseChatClient</span>; want the tool loop? stack <span class="mono">FunctionInvocationLayer</span> on top.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> How do providers implement _inner_get_response? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">FoundryChatClient extends <span class="mono">BaseChatClient</span> and only overrides
      <span class="mono">_inner_get_response</span>: converts MAF <span class="mono">Message</span> objects to the Foundry SDK format,
      calls the API, converts back to <span class="mono">ChatResponse</span>. When <span class="mono">stream=True</span>, returns an async generator.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Different LLM vendors have completely different API formats. If callers had to adapt themselves,
      switching models would require rewriting code. Encapsulating in <span class="mono">_inner_get_response</span> means zero changes upstream.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">Subclasses implement one abstract method with a fixed signature:
      <span class="mono">_inner_get_response(*, messages, stream, options, **kwargs)</span>.
      The base class handles retries, middleware, and compaction — subclasses only deal with "how to talk to that API".</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">LiteLLM uses a giant if/elif dispatching to each vendor;
      LangChain has a full class hierarchy per vendor. MAF's "one abstract method" approach is the simplest — one class + one method per vendor.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> get_response full signature <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a"><span class="mono">get_response()</span> (<span class="mono">_clients.py:482</span>) full signature:
<pre class="code">get_response(
  messages: Sequence[Message],
  *, <span class="cm"># everything below is keyword-only</span>
  stream: bool = False,
  options: ChatOptions | None = None,
  compaction_strategy: CompactionStrategy | None,
  tokenizer: TokenizerProtocol | None,
  function_invocation_kwargs: Mapping | None,
  client_kwargs: Mapping | None,
)</pre>
      Returns <span class="mono">ChatResponse</span> (non-streaming) or <span class="mono">ResponseStream[ChatResponseUpdate, ChatResponse]</span> (streaming).</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Knowing all parameters enables fine-grained control: <span class="mono">compaction_strategy</span> decides how to compress
      when messages are too long, <span class="mono">client_kwargs</span> passes vendor-specific params, <span class="mono">function_invocation_kwargs</span> forwards to tool invocation.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">Only <span class="mono">messages</span> is positional; the rest are <strong>keyword-only</strong>,
      preventing argument-order mistakes. <span class="mono">stream</span> toggles the return type via one bool — no need for two methods.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">OpenAI SDK uses <span class="mono">create()</span> with many kwargs;
      Anthropic uses <span class="mono">messages.create()</span>. MAF unifies into one entry point + keyword params — easier to discover, harder to misuse.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> ChatResponse internals <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a"><span class="mono">ChatResponse</span> (<span class="mono">_types.py:2122</span>) core fields:
<pre class="code">resp.messages       <span class="cm"># list[Message] — model reply messages</span>
resp.text           <span class="cm"># combined message text (read-only property)</span>
resp.model          <span class="cm"># actual model name used</span>
resp.usage_details  <span class="cm"># UsageDetails (input_token_count, output_token_count, total_token_count)</span>
resp.finish_reason  <span class="cm"># &quot;stop&quot; / &quot;tool_calls&quot; / &quot;length&quot;</span>
resp.value          <span class="cm"># generic structured output</span>
resp.conversation_id  <span class="cm"># conversation state identifier</span></pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a"><span class="mono">ChatResponse</span> is the "atomic exchange unit" inside the Agent loop —
      each LLM call returns one, and the Agent checks <span class="mono">finish_reason</span> to decide whether to continue the tool loop or stop.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">.text</span> auto-joins messages, saving manual iteration.
      <span class="mono">.value</span> supports generics — <span class="mono">ChatResponse[MyModel]</span>'s <span class="mono">.value</span> is directly a <span class="mono">MyModel</span> instance.
      <span class="mono">.raw_representation</span> preserves the raw response for debugging.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Some frameworks return plain strings; others return dicts.
      MAF's strongly-typed dataclass provides autocompletion and type checking — a far better IDE experience than dict.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Writing your own ChatClient <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">Minimal custom <span class="mono">BaseChatClient</span> subclass skeleton:
<pre class="code"><span class="kw">class</span> <span class="fn">MyChatClient</span>(BaseChatClient):
    <span class="kw">async def</span> <span class="fn">_inner_get_response</span>(
        self, *, messages, stream, options, **kwargs
    ):
        <span class="cm"># 1. Convert MAF Messages to your API format</span>
        <span class="cm"># 2. Call your LLM API</span>
        <span class="cm"># 3. Convert result back to ChatResponse</span>
        <span class="kw">return</span> ChatResponse(messages=[...], model=<span class="st">&quot;my-model&quot;</span>)</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">If you need to connect a model that MAF doesn't have an official provider for
      (private deployment, niche vendor), you write your own. Only <strong>one method</strong> to implement — very low barrier.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">The base class <span class="mono">BaseChatClient</span> (<span class="mono">_clients.py:217</span>)
      already handles middleware triggers, compaction, and option validation. You only write the "talk to API" part; everything else is reused.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Adapter pattern wrapping an existing SDK (more glue code),
      or replacing the call logic at the Agent level (loses base-class features). MAF's "subclass + one method" is the simplest with maximum reuse.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> ChatOptions explained <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a"><span class="mono">ChatOptions</span> (<span class="mono">_types.py:3346</span>) common fields:
<pre class="code">options = ChatOptions(
  model=<span class="st">&quot;gpt-4o&quot;</span>,
  temperature=0.7,
  max_tokens=2048,
  top_p=0.9,
  stop=[<span class="st">&quot;\n\n&quot;</span>],
  tool_choice=<span class="st">&quot;auto&quot;</span>,
  response_format=MyModel,  <span class="cm"># structured output</span>
)</pre>
      Also: <span class="mono">frequency_penalty</span>, <span class="mono">presence_penalty</span>, <span class="mono">seed</span>,
      <span class="mono">logit_bias</span>, <span class="mono">metadata</span>, <span class="mono">instructions</span>, etc.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Different tasks need different params: creative writing needs high temperature, code generation needs
      low temperature + <span class="mono">stop</span> sequences. <span class="mono">ChatOptions</span> is the standard way to pass all model parameters as one object.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">ChatOptions</span> is a <span class="mono">TypedDict</span>,
      so your IDE shows all valid fields + autocompletion. It integrates seamlessly with <span class="mono">get_response(options=...)</span>,
      and <span class="mono">tool_choice</span> supports <span class="mono">&quot;auto&quot;</span> / <span class="mono">&quot;required&quot;</span> / <span class="mono">&quot;none&quot;</span> for precise tool-call control.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Pass raw <span class="mono">**kwargs</span> (no type hints);
      or make each param a separate <span class="mono">get_response()</span> argument (signature explosion).
      <span class="mono">TypedDict</span> strikes the best balance between flexibility and type safety.</div></div>
  </div>
</details>

<h2>🔍 Real source: the skeleton of get_response</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_clients.py</span><span class="ln">BaseChatClient.get_response (simplified from :482)</span></div>
<pre class="code"><span class="kw">def</span> <span class="fn">get_response</span>(self, messages, *, stream=<span class="kw">False</span>, options=<span class="kw">None</span>,
        compaction_strategy=<span class="kw">None</span>, tokenizer=<span class="kw">None</span>,
        function_invocation_kwargs=<span class="kw">None</span>, client_kwargs=<span class="kw">None</span>):
    overrides = self._resolve_compaction_overrides(      <span class="cm"># merge compaction settings</span>
        compaction_strategy=compaction_strategy, tokenizer=tokenizer)
    merged_client_kwargs = dict(client_kwargs <span class="kw">or</span> {})

    <span class="kw">if not</span> overrides:                                   <span class="cm"># ① no compaction: forward as-is</span>
        <span class="kw">return</span> self._inner_get_response(
            messages=messages, stream=stream,
            options=options <span class="kw">or</span> {}, **merged_client_kwargs)

    <span class="kw">async def</span> <span class="fn">_get_response</span>():                        <span class="cm"># ② compaction: prepare then call</span>
        prepared = <span class="kw">await</span> self._prepare_messages_for_model_call(
            messages, **overrides)
        <span class="kw">return await</span> self._inner_get_response(
            messages=prepared, stream=<span class="kw">False</span>,
            options=options <span class="kw">or</span> {}, **merged_client_kwargs)
    <span class="kw">return</span> _get_response()</pre>
</div>
<p>Just two paths: <strong>① no compaction forwards as-is, ② compaction _prepares first, then forwards</strong> — but both call
<span class="mono">_inner_get_response()</span> <strong>exactly once</strong>. The base <strong>never touches a vendor field</strong>; it hands the whole
"translate + network + normalize" block to the subclass. That is the line between "shared skeleton" and "vendor extension point":
the top half (this code) is shared by all; the bottom half (<span class="mono">_inner_get_response</span>) is written per vendor.</p>

<h2>Why collapse everything into one ChatResponse</h2>
<p>You might ask: since every API returns different JSON, why bother writing a "translation" in the subclass to unify into
<span class="mono">ChatResponse</span>? Wouldn't passing the vendor dict straight through be simpler? The answer is <strong>keeping the volatile out of the stable</strong>.
Vendor JSON field names and nesting can change anytime (OpenAI calls tokens <span class="mono">prompt_tokens</span>; the framework calls them
<span class="mono">input_token_count</span>). If upper layers read vendor fields directly, switching providers — or a provider upgrade — would <strong>ripple through the entire call chain</strong>.</p>
<p>Normalization locks that volatility into <strong>a single subclass method</strong>: upper layers only ever know the stable
<span class="mono">ChatResponse.text</span> / <span class="mono">.finish_reason</span> / <span class="mono">.usage_details</span> set. So the Agent's tool loop decides whether to
continue via <span class="mono">finish_reason==&quot;tool_calls&quot;</span> and <strong>never needs to know which model is underneath</strong> — exactly why L08's
"swap models, change nothing" promise holds.</p>
<p>Better still, <span class="mono">.raw_representation</span> keeps the vendor's original response: <strong>unified fields cover 99% of needs, the escape hatch covers the last 1%</strong>.
You get the cleanliness of strong types without being locked out when you genuinely need a vendor-specific field. This is the classic "narrow interface + escape hatch" trade-off.</p>

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

<h2>追踪一次真实工具调用：get_weather(&quot;北京&quot;)</h2>
<p>上面是抽象闭环，我们用一个<strong>具体函数</strong>端到端走一遍，每步都给出当时的<strong>真实数据快照</strong>——
看一个普通 Python 函数如何变成模型能读的 schema，又如何被模型&quot;点名&quot;并执行：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>你写的函数（带类型注解）</h4>
    <p>注意：<span class="mono">city</span> 无默认值（必填），<span class="mono">unit</span> 有默认值（可选）：</p>
<pre class="code"><span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">get_weather</span>(
    city: Annotated[str, Field(description=<span class="st">&quot;城市名&quot;</span>)],
    unit: str = <span class="st">&quot;celsius&quot;</span>,
) -&gt; str:
    <span class="st">&quot;&quot;&quot;查询某城市的当前天气&quot;&quot;&quot;</span>
    <span class="kw">return</span> f<span class="st">&quot;{city}: 18°C 晴&quot;</span></pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>签名 → Pydantic 模型 → JSON Schema</h4>
    <p><span class="mono">_resolve_input_model()</span>（<span class="mono">_tools.py:481</span>）用 <span class="mono">inspect.signature</span> 读出参数，
    <span class="mono">create_model(&quot;get_weather_input&quot;, **fields)</span> 造出一个 Pydantic 模型，再 <span class="mono">.model_json_schema()</span> 生成：</p>
<pre class="code">{
  <span class="st">&quot;type&quot;</span>: <span class="st">&quot;object&quot;</span>,
  <span class="st">&quot;properties&quot;</span>: {
    <span class="st">&quot;city&quot;</span>: {<span class="st">&quot;type&quot;</span>: <span class="st">&quot;string&quot;</span>, <span class="st">&quot;description&quot;</span>: <span class="st">&quot;城市名&quot;</span>},
    <span class="st">&quot;unit&quot;</span>: {<span class="st">&quot;type&quot;</span>: <span class="st">&quot;string&quot;</span>, <span class="st">&quot;default&quot;</span>: <span class="st">&quot;celsius&quot;</span>}},
  <span class="st">&quot;required&quot;</span>: [<span class="st">&quot;city&quot;</span>]   <span class="cm"># 无默认值的参数自动进 required</span>
}</pre></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>包成 function spec，随请求发出</h4>
    <p><span class="mono">to_json_schema_spec()</span>（<span class="mono">_tools.py:866</span>）把上面的 schema 套进 OpenAI 工具格式，ChatClient 在 <span class="mono">tools</span> 字段里带上它：</p>
<pre class="code">{<span class="st">&quot;type&quot;</span>: <span class="st">&quot;function&quot;</span>,
 <span class="st">&quot;function&quot;</span>: {<span class="st">&quot;name&quot;</span>: <span class="st">&quot;get_weather&quot;</span>,
              <span class="st">&quot;description&quot;</span>: <span class="st">&quot;查询某城市的当前天气&quot;</span>,
              <span class="st">&quot;parameters&quot;</span>: { … 第②步那份 … }}}</pre></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>模型点名这个工具</h4>
    <p>模型读 schema 后决定调用，回一个 <span class="mono">function_call</span> 内容（<span class="mono">arguments</span> 是 JSON <strong>字符串</strong>）：</p>
<pre class="code">Content.from_function_call(       <span class="cm"># _types.py:788</span>
  call_id=<span class="st">&quot;call_1&quot;</span>, name=<span class="st">&quot;get_weather&quot;</span>,
  arguments=<span class="st">'{&quot;city&quot;: &quot;北京&quot;}'</span>)   <span class="cm"># 模型只填了必填项</span></pre></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>校验参数 → 反序列化 → 执行</h4>
    <p><span class="mono">FunctionTool.invoke()</span>（<span class="mono">_tools.py:574</span>）拿第②步那个 Pydantic 模型校验 <span class="mono">arguments</span>，
    校验通过后 <span class="mono">unit</span> 自动补上默认值 <span class="mono">&quot;celsius&quot;</span>，再调用你的函数：</p>
<pre class="code">get_weather(city=<span class="st">&quot;北京&quot;</span>, unit=<span class="st">&quot;celsius&quot;</span>)
<span class="cm"># → &quot;北京: 18°C 晴&quot;</span></pre></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>结果包成 function_result 回灌</h4>
    <p><span class="mono">parse_result()</span>（<span class="mono">_tools.py:825</span>）把返回值规整成 <span class="mono">list[Content]</span>，再包成 function_result 追加进消息列表，回到第 3 步让模型续写：</p>
<pre class="code">Content.from_function_result(     <span class="cm"># _types.py:812</span>
  call_id=<span class="st">&quot;call_1&quot;</span>, result=<span class="st">&quot;北京: 18°C 晴&quot;</span>)</pre></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 读懂这条轨迹</div>
  注意第 ② 步和第 ⑤ 步用的是<strong>同一个 Pydantic 模型</strong>：一次 <span class="mono">create_model</span> 同时承担了
  &quot;对模型描述参数&quot;（生成 schema）和&quot;对参数把关&quot;（执行前校验）两件事。这就是&quot;签名即契约&quot;——
  你<strong>从未手写过一行 schema，也从未手写过一行校验</strong>，两者却永远一致，因为它们来自同一处签名。
</div>

<h2>签名即 Schema：一一对照</h2>
<p>第②步那次&quot;签名 → schema&quot;到底怎么映射？下表逐项拆开，看 Python 的每个语法元素分别变成 JSON Schema 的哪个字段：</p>
<table class="t">
  <tr><th>Python 函数里的写法</th><th>JSON Schema 里的字段</th><th>谁负责</th></tr>
  <tr><td class="mono">def get_weather(…)</td><td class="mono">function.name = &quot;get_weather&quot;</td><td><span class="mono">__name__</span>（可被 <span class="mono">@tool(name=…)</span> 覆盖）</td></tr>
  <tr><td>函数 docstring</td><td class="mono">function.description</td><td><span class="mono">@tool</span> 取 docstring</td></tr>
  <tr><td class="mono">city: str</td><td class="mono">properties.city.type = &quot;string&quot;</td><td>Pydantic 由类型注解推断</td></tr>
  <tr><td class="mono">Field(description=&quot;城市名&quot;)</td><td class="mono">properties.city.description</td><td><span class="mono">Annotated</span> + <span class="mono">Field</span></td></tr>
  <tr><td class="mono">unit: str = &quot;celsius&quot;</td><td class="mono">properties.unit.default</td><td>参数默认值</td></tr>
  <tr><td>无默认值的参数</td><td class="mono">required: [&quot;city&quot;]</td><td><span class="mono">_resolve_input_model</span> 用 <span class="mono">...</span> 标记</td></tr>
</table>

<h2>Schema 生成流水线</h2>
<p>把第②③步连起来看，从函数到&quot;模型能读的 function spec&quot;是一条四段流水线，全程<strong>无需人工</strong>：</p>
<div class="flow">
  <div class="node"><div class="nt">函数签名</div><div class="nd">inspect.signature</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">create_model</div><div class="nd">造 Pydantic 模型</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">model_json_schema()</div><div class="nd">Pydantic 生成 schema</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">to_json_schema_spec()</div><div class="nd">套 function 外壳</div></div>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> FunctionTool 里装了什么？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a"><span class="mono">FunctionTool</span>（<span class="mono">_tools.py:240</span>）持有：原始函数引用、生成的 JSON Schema、
      <span class="mono">approval_mode</span>（调用前是否需要人工审批）、函数名、描述。
      <span class="mono">@tool</span>（<span class="mono">_tools.py:1176</span>）是构造 <span class="mono">FunctionTool</span> 的语法糖。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">知道 <span class="mono">FunctionTool</span> 的结构，才能理解 schema 是怎么生成的、
      执行时参数怎么验证的、<span class="mono">approval_mode</span> 在哪里拦截。调试工具调用问题必须从这里入手。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">FunctionTool</span> 把函数元信息（名字、描述、schema）和运行时行为
      （执行、审批、序列化）封装在同一个对象里，是"函数即工具"哲学的载体。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">有的框架用 dict 描述工具（无类型安全）；
      有的让你手写 JSON Schema。MAF 从类型注解自动生成 schema，消除"代码与 schema 不一致"的风险。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> JSON Schema 长什么样 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">一个 <span class="mono">@tool</span> 函数：
<pre class="code"><span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">get_weather</span>(city: Annotated[str, Field(description=<span class="st">&quot;城市名&quot;</span>)]) -&gt; str:
    <span class="st">&quot;&quot;&quot;查询天气&quot;&quot;&quot;</span>
    ...</pre>
      自动生成的 schema（简化）：
<pre class="code">{
  <span class="st">&quot;name&quot;</span>: <span class="st">&quot;get_weather&quot;</span>,
  <span class="st">&quot;description&quot;</span>: <span class="st">&quot;查询天气&quot;</span>,
  <span class="st">&quot;parameters&quot;</span>: {
    <span class="st">&quot;type&quot;</span>: <span class="st">&quot;object&quot;</span>,
    <span class="st">&quot;properties&quot;</span>: {
      <span class="st">&quot;city&quot;</span>: {<span class="st">&quot;type&quot;</span>: <span class="st">&quot;string&quot;</span>, <span class="st">&quot;description&quot;</span>: <span class="st">&quot;城市名&quot;</span>}
    },
    <span class="st">&quot;required&quot;</span>: [<span class="st">&quot;city&quot;</span>]
  }
}</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">模型看到的就是这份 JSON Schema——如果描述不清楚或类型不对，
      模型就会生成错误的参数。理解 schema 结构，才知道如何写出"对模型友好"的工具。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">利用 <span class="mono">Annotated[..., Field(description=...)]</span>
      和 Python 类型注解自动构建 schema。docstring 变成 <span class="mono">description</span>，参数类型变成 JSON 类型——
      <strong>代码就是文档</strong>，永远不会过期。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">手写 JSON Schema（容易过期）；用 Pydantic model 定义参数
      （更显式但更啰嗦）。MAF 的 <span class="mono">@tool</span> + 类型注解方案最简洁，且和 Pydantic 兼容。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> function_call Content 的结构 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">当模型决定调用工具时，回复的 <span class="mono">Content</span> 里会有一个 <span class="mono">function_call</span>：
<pre class="code"><span class="cm"># 模型回复中的 Content（简化）</span>
Content(
  type=<span class="st">&quot;function_call&quot;</span>,
  name=<span class="st">&quot;get_weather&quot;</span>,
  id=<span class="st">&quot;call_abc123&quot;</span>,
  arguments=<span class="st">'{&quot;city&quot;: &quot;北京&quot;}'</span>  <span class="cm"># JSON 字符串！</span>
)</pre>
      注意 <span class="mono">arguments</span> 是 <strong>JSON 字符串</strong>，不是 dict——框架负责反序列化。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">理解这个结构才能调试"模型返回了工具调用但执行失败"的问题——
      通常是 <span class="mono">arguments</span> 的 JSON 格式不对，或者 <span class="mono">name</span> 和注册的工具名不匹配。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">框架自动：① 从 <span class="mono">arguments</span> JSON 字符串反序列化为 Python 对象，
      ② 用生成的 schema 做验证，③ 调用函数，④ 把返回值包装成 <span class="mono">function_result</span> Content 回灌。
      开发者无需手动处理任何序列化/反序列化。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">有的框架要求开发者自己解析 JSON 参数（容易出错）；
      有的用 Protocol Buffer（太重）。MAF 的自动 JSON ↔ Python 转换是最实用的方案。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> FunctionTool 的执行过程 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a"><span class="mono">FunctionTool.invoke()</span>（<span class="mono">_tools.py:574</span>）的执行步骤：
<pre class="code"><span class="cm">1. 验证参数</span> → arguments 对照 schema 检查类型
<span class="cm">2. 创建 FunctionInvocationContext</span>
<span class="cm">3. 合并参数</span> → 把 context 参数注入 kwargs
<span class="cm">4. 调用 _invoke_function()</span> → 执行你的 Python 函数
<span class="cm">5. 解析结果</span> → result_parser 或 parse_result()
<span class="cm">6. 返回 list[Content]</span> → 包装为 function_result</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">出错时（参数验证失败、函数抛异常、结果解析错误），需要知道在哪一步出了问题。
      <span class="mono">invoke()</span> 的 6 步流水线给你精确的排查路径。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">验证发生在调用之前，提前拦截非法参数。
      如果启用了 observability（遥测），每次 <span class="mono">invoke()</span> 会创建 span 和 histogram，
      自动记录执行时间和异常——无需额外代码就有生产级监控。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">有的框架在调用时才验证（报错晚）；
      有的不做结果解析（直接返回原始值）。MAF 的"先验证 → 再调用 → 后解析"三段式最健壮。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> 并行工具调用 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">当模型一次返回多个 <span class="mono">function_call</span>（如同时查天气和汇率），
      框架在 <span class="mono">_try_execute_function_calls()</span>（<span class="mono">_tools.py:1655</span>）中用
      <span class="mono">asyncio.gather()</span> 并行执行所有调用：
<pre class="code">results = <span class="kw">await</span> asyncio.gather(*[
    invoke_with_termination_handling(fc, idx)
    <span class="kw">for</span> idx, fc <span class="kw">in</span> enumerate(function_calls)
])</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">如果 3 个工具各需 1 秒，串行要 3 秒，并行只要 1 秒。
      对于 I/O 密集型工具（API 调用、数据库查询），并行执行能<strong>大幅降低延迟</strong>。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">用 <span class="mono">asyncio.gather()</span> 实现真正并发。
      每个调用独立包裹异常处理（<span class="mono">invoke_with_termination_handling</span>），
      一个工具失败不会影响其他工具。返回值是 <span class="mono">(list[Content], should_terminate)</span> 元组。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">线程池（<span class="mono">ThreadPoolExecutor</span>）适合 CPU 密集型但对异步不友好；
      串行执行最简单但最慢。MAF 选择 <span class="mono">asyncio.gather()</span>，完美适配 I/O 密集场景且与框架的 async 架构一致。</div></div>
  </div>
</details>

<h2>🔍 真实源码：从签名到 function spec</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_tools.py</span><span class="ln">签名 → schema（简化自 :481 / :780 / :866）</span></div>
<pre class="code"><span class="cm"># ① 从函数签名造 Pydantic 模型（_resolve_input_model :481）</span>
sig = inspect.signature(func)
fields = {
    pname: (annotation_of(param),
            param.default <span class="kw">if</span> has_default(param) <span class="kw">else</span> ...)  <span class="cm"># ... = 必填</span>
    <span class="kw">for</span> pname, param <span class="kw">in</span> sig.parameters.items()
    <span class="kw">if</span> pname <span class="kw">not in</span> {<span class="st">&quot;self&quot;</span>, <span class="st">&quot;cls&quot;</span>}}
input_model = create_model(f<span class="st">&quot;{name}_input&quot;</span>, **fields)

<span class="cm"># ② Pydantic 直接吐 JSON Schema（_input_schema :780）</span>
<span class="kw">def</span> <span class="fn">parameters</span>(self):
    <span class="kw">return</span> self.input_model.model_json_schema()

<span class="cm"># ③ 套上 function 外壳（to_json_schema_spec :866）</span>
<span class="kw">def</span> <span class="fn">to_json_schema_spec</span>(self):
    <span class="kw">return</span> {<span class="st">&quot;type&quot;</span>: <span class="st">&quot;function&quot;</span>, <span class="st">&quot;function&quot;</span>: {
        <span class="st">&quot;name&quot;</span>: self.name,
        <span class="st">&quot;description&quot;</span>: self.description,
        <span class="st">&quot;parameters&quot;</span>: self.parameters()}}</pre>
</div>
<p>三段全是<strong>从源码直接简化</strong>而来：框架自己<strong>一行 schema 都没手写</strong>——它把活儿交给
<span class="mono">inspect</span>（读签名）和 <span class="mono">Pydantic</span>（出 schema）。无默认值的参数被标成 <span class="mono">...</span>，于是 Pydantic 自动把它放进
<span class="mono">required</span>。这正是上面&quot;签名即 Schema&quot;对照表能成立的代码出处。</p>

<h2>为什么让类型注解自动生成 Schema</h2>
<p>最朴素的做法是让你<strong>手写两份东西</strong>：一份 Python 函数、一份描述它的 JSON Schema。问题是这两份会
<strong>各自漂移</strong>——你给函数加了个参数，却忘了改 schema；模型于是按旧 schema 生成参数，运行时直接炸。
凡是&quot;同一个事实写两遍&quot;的设计，迟早会因为两遍不同步而出 bug。</p>
<p>MAF 选择<strong>单一事实来源</strong>（single source of truth）：函数签名是<strong>唯一</strong>的真相，schema 由它<strong>派生</strong>。
你改签名，schema 下次生成时自动跟着变，永不漂移——这就是 DRY（Don't Repeat Yourself）原则在工具系统里的体现。
更妙的是同一个 Pydantic 模型<strong>身兼两职</strong>：对外当 schema 描述参数，对内当校验器把关入参，连&quot;校验逻辑&quot;都不必另写。</p>
<p>代价是你得接受框架的&quot;约定&quot;：用 <span class="mono">Annotated[..., Field(description=…)]</span> 写参数说明、用类型注解表达类型。
但这点约束换来的是<strong>代码即文档、文档永不过期</strong>。需要完全自定义时，<span class="mono">@tool(schema=…)</span> 仍允许你显式传入 schema——又是&quot;窄默认 + 逃生舱口&quot;的老套路。</p>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><span class="mono">@tool</span> → <span class="mono">FunctionTool</span> → JSON Schema → 随请求发给模型。</li>
    <li>模型回 <span class="mono">function_call</span> → 框架执行 → <span class="mono">function_result</span> 回灌 → 再让模型继续。</li>
    <li>这个循环在 ChatClient 一侧的 <span class="mono">FunctionInvocationLayer</span> 里自动跑（不在 Agent 里），调用方无感。</li>
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

<h2>Tracing a real tool call: get_weather(&quot;Beijing&quot;)</h2>
<p>That was the abstract loop; let's walk one <strong>concrete function</strong> end to end, with a <strong>real data snapshot</strong> at each step —
watch how an ordinary Python function becomes a model-readable schema, then gets &quot;named&quot; by the model and executed:</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>The function you write (with type hints)</h4>
    <p>Note: <span class="mono">city</span> has no default (required); <span class="mono">unit</span> has a default (optional):</p>
<pre class="code"><span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">get_weather</span>(
    city: Annotated[str, Field(description=<span class="st">&quot;city name&quot;</span>)],
    unit: str = <span class="st">&quot;celsius&quot;</span>,
) -&gt; str:
    <span class="st">&quot;&quot;&quot;Get the current weather for a city&quot;&quot;&quot;</span>
    <span class="kw">return</span> f<span class="st">&quot;{city}: 18°C sunny&quot;</span></pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Signature → Pydantic model → JSON Schema</h4>
    <p><span class="mono">_resolve_input_model()</span> (<span class="mono">_tools.py:481</span>) reads params via <span class="mono">inspect.signature</span>,
    <span class="mono">create_model(&quot;get_weather_input&quot;, **fields)</span> builds a Pydantic model, then <span class="mono">.model_json_schema()</span> emits:</p>
<pre class="code">{
  <span class="st">&quot;type&quot;</span>: <span class="st">&quot;object&quot;</span>,
  <span class="st">&quot;properties&quot;</span>: {
    <span class="st">&quot;city&quot;</span>: {<span class="st">&quot;type&quot;</span>: <span class="st">&quot;string&quot;</span>, <span class="st">&quot;description&quot;</span>: <span class="st">&quot;city name&quot;</span>},
    <span class="st">&quot;unit&quot;</span>: {<span class="st">&quot;type&quot;</span>: <span class="st">&quot;string&quot;</span>, <span class="st">&quot;default&quot;</span>: <span class="st">&quot;celsius&quot;</span>}},
  <span class="st">&quot;required&quot;</span>: [<span class="st">&quot;city&quot;</span>]   <span class="cm"># params without a default auto-go into required</span>
}</pre></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Wrap as a function spec, send with the request</h4>
    <p><span class="mono">to_json_schema_spec()</span> (<span class="mono">_tools.py:866</span>) nests that schema in the OpenAI tool shape; the ChatClient includes it in the <span class="mono">tools</span> field:</p>
<pre class="code">{<span class="st">&quot;type&quot;</span>: <span class="st">&quot;function&quot;</span>,
 <span class="st">&quot;function&quot;</span>: {<span class="st">&quot;name&quot;</span>: <span class="st">&quot;get_weather&quot;</span>,
              <span class="st">&quot;description&quot;</span>: <span class="st">&quot;Get the current weather for a city&quot;</span>,
              <span class="st">&quot;parameters&quot;</span>: { … the step ② schema … }}}</pre></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>The model names this tool</h4>
    <p>After reading the schema the model decides to call it, returning a <span class="mono">function_call</span> (its <span class="mono">arguments</span> is a JSON <strong>string</strong>):</p>
<pre class="code">Content.from_function_call(       <span class="cm"># _types.py:788</span>
  call_id=<span class="st">&quot;call_1&quot;</span>, name=<span class="st">&quot;get_weather&quot;</span>,
  arguments=<span class="st">'{&quot;city&quot;: &quot;Beijing&quot;}'</span>)   <span class="cm"># model filled only the required field</span></pre></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Validate args → deserialize → execute</h4>
    <p><span class="mono">FunctionTool.invoke()</span> (<span class="mono">_tools.py:574</span>) validates <span class="mono">arguments</span> with that step-② Pydantic model;
    on success <span class="mono">unit</span> auto-fills its default <span class="mono">&quot;celsius&quot;</span>, then your function runs:</p>
<pre class="code">get_weather(city=<span class="st">&quot;Beijing&quot;</span>, unit=<span class="st">&quot;celsius&quot;</span>)
<span class="cm"># → &quot;Beijing: 18°C sunny&quot;</span></pre></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Result packed as function_result, fed back</h4>
    <p><span class="mono">parse_result()</span> (<span class="mono">_tools.py:825</span>) normalizes the return into <span class="mono">list[Content]</span>, packed as function_result and appended; back to step 3 for the model to continue:</p>
<pre class="code">Content.from_function_result(     <span class="cm"># _types.py:812</span>
  call_id=<span class="st">&quot;call_1&quot;</span>, result=<span class="st">&quot;Beijing: 18°C sunny&quot;</span>)</pre></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 Reading this trace</div>
  Notice steps ② and ⑤ use the <strong>same Pydantic model</strong>: one <span class="mono">create_model</span> does double duty —
  &quot;describe params to the model&quot; (emit schema) and &quot;guard the params&quot; (validate before execution). That is &quot;signature as contract&quot; —
  you <strong>never hand-wrote a line of schema, nor a line of validation</strong>, yet the two always agree, because both come from the one signature.
</div>

<h2>Signature IS the schema: a field-by-field map</h2>
<p>How exactly does that step-② &quot;signature → schema&quot; map? The table below breaks it down — which Python syntax element becomes which JSON Schema field:</p>
<table class="t">
  <tr><th>In the Python function</th><th>In the JSON Schema</th><th>Who does it</th></tr>
  <tr><td class="mono">def get_weather(…)</td><td class="mono">function.name = &quot;get_weather&quot;</td><td><span class="mono">__name__</span> (override via <span class="mono">@tool(name=…)</span>)</td></tr>
  <tr><td>function docstring</td><td class="mono">function.description</td><td><span class="mono">@tool</span> reads the docstring</td></tr>
  <tr><td class="mono">city: str</td><td class="mono">properties.city.type = &quot;string&quot;</td><td>Pydantic infers from the annotation</td></tr>
  <tr><td class="mono">Field(description=&quot;city name&quot;)</td><td class="mono">properties.city.description</td><td><span class="mono">Annotated</span> + <span class="mono">Field</span></td></tr>
  <tr><td class="mono">unit: str = &quot;celsius&quot;</td><td class="mono">properties.unit.default</td><td>parameter default</td></tr>
  <tr><td>params without a default</td><td class="mono">required: [&quot;city&quot;]</td><td><span class="mono">_resolve_input_model</span> marks with <span class="mono">...</span></td></tr>
</table>

<h2>The schema-generation pipeline</h2>
<p>Chaining steps ②③, the path from function to &quot;model-readable function spec&quot; is a four-stage pipeline, <strong>fully hands-off</strong>:</p>
<div class="flow">
  <div class="node"><div class="nt">function signature</div><div class="nd">inspect.signature</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">create_model</div><div class="nd">build Pydantic model</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">model_json_schema()</div><div class="nd">Pydantic emits schema</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">to_json_schema_spec()</div><div class="nd">wrap in function shell</div></div>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> What's inside a FunctionTool? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a"><span class="mono">FunctionTool</span> (<span class="mono">_tools.py:240</span>) holds: the original function reference,
      the generated JSON Schema, <span class="mono">approval_mode</span> (whether human approval is needed before invocation),
      the function name and description.
      <span class="mono">@tool</span> (<span class="mono">_tools.py:1176</span>) is syntactic sugar for constructing a <span class="mono">FunctionTool</span>.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Knowing <span class="mono">FunctionTool</span>'s structure helps you understand how schemas are generated,
      how arguments are validated at execution, and where <span class="mono">approval_mode</span> intercepts. Debugging tool calls starts here.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">FunctionTool</span> bundles function metadata (name, description, schema) and runtime behavior
      (execution, approval, serialisation) in one object — the carrier of the "function is a tool" philosophy.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Some frameworks describe tools with dicts (no type safety);
      others require hand-written JSON Schema. MAF auto-generates schemas from type annotations, eliminating "code vs schema drift".</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> What the JSON Schema looks like <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">A <span class="mono">@tool</span> function:
<pre class="code"><span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">get_weather</span>(city: Annotated[str, Field(description=<span class="st">&quot;city name&quot;</span>)]) -&gt; str:
    <span class="st">&amp;quot;&amp;quot;&amp;quot;Look up weather&amp;quot;&amp;quot;&amp;quot;</span>
    ...</pre>
      Auto-generated schema (simplified):
<pre class="code">{
  <span class="st">&quot;name&quot;</span>: <span class="st">&quot;get_weather&quot;</span>,
  <span class="st">&quot;description&quot;</span>: <span class="st">&quot;Look up weather&quot;</span>,
  <span class="st">&quot;parameters&quot;</span>: {
    <span class="st">&quot;type&quot;</span>: <span class="st">&quot;object&quot;</span>,
    <span class="st">&quot;properties&quot;</span>: {
      <span class="st">&quot;city&quot;</span>: {<span class="st">&quot;type&quot;</span>: <span class="st">&quot;string&quot;</span>, <span class="st">&quot;description&quot;</span>: <span class="st">&quot;city name&quot;</span>}
    },
    <span class="st">&quot;required&quot;</span>: [<span class="st">&quot;city&quot;</span>]
  }
}</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">The model sees exactly this JSON Schema — if the description is unclear or the type is wrong,
      the model will generate incorrect arguments. Understanding schema structure helps you write "model-friendly" tools.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">Uses <span class="mono">Annotated[..., Field(description=...)]</span>
      and Python type hints to auto-build the schema. Docstrings become <span class="mono">description</span>, param types become JSON types —
      <strong>code IS documentation</strong>, never stale.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Hand-write JSON Schema (goes stale easily); use a Pydantic model for params
      (more explicit but more verbose). MAF's <span class="mono">@tool</span> + type-hints approach is the most concise and Pydantic-compatible.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> function_call Content structure <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">When the model decides to call a tool, its reply <span class="mono">Content</span> contains a <span class="mono">function_call</span>:
<pre class="code"><span class="cm"># Content in the model's reply (simplified)</span>
Content(
  type=<span class="st">&quot;function_call&quot;</span>,
  name=<span class="st">&quot;get_weather&quot;</span>,
  id=<span class="st">&quot;call_abc123&quot;</span>,
  arguments=<span class="st">'{&quot;city&quot;: &quot;Beijing&quot;}'</span>  <span class="cm"># JSON string!</span>
)</pre>
      Note: <span class="mono">arguments</span> is a <strong>JSON string</strong>, not a dict — the framework handles deserialisation.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Understanding this structure is key to debugging "model returned a tool call but execution failed" —
      usually the <span class="mono">arguments</span> JSON is malformed, or the <span class="mono">name</span> doesn't match a registered tool.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">The framework automatically: ① deserialises the <span class="mono">arguments</span> JSON string to Python objects,
      ② validates against the generated schema, ③ calls the function, ④ wraps the return value as <span class="mono">function_result</span> Content.
      Developers never touch serialisation/deserialisation.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Some frameworks require devs to parse JSON arguments themselves (error-prone);
      others use Protocol Buffers (too heavy). MAF's automatic JSON ↔ Python conversion is the most practical approach.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> FunctionTool execution process <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a"><span class="mono">FunctionTool.invoke()</span> (<span class="mono">_tools.py:574</span>) execution steps:
<pre class="code"><span class="cm">1. Validate arguments</span> → check types against schema
<span class="cm">2. Create FunctionInvocationContext</span>
<span class="cm">3. Merge arguments</span> → inject context param into kwargs
<span class="cm">4. Call _invoke_function()</span> → execute your Python function
<span class="cm">5. Parse result</span> → result_parser or parse_result()
<span class="cm">6. Return list[Content]</span> → wrap as function_result</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">When things go wrong (argument validation fails, function throws, result parsing errors),
      you need to know which step broke. The 6-step pipeline gives you a precise debugging path.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">Validation happens before invocation, catching illegal arguments early.
      With observability enabled, each <span class="mono">invoke()</span> creates a span and histogram,
      automatically recording execution time and exceptions — production-grade monitoring with zero extra code.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Some frameworks validate only at call time (late errors);
      others skip result parsing (return raw values). MAF's "validate → invoke → parse" three-phase pipeline is the most robust.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> Parallel tool calls <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">When the model returns multiple <span class="mono">function_call</span>s at once (e.g. look up weather AND exchange rate),
      the framework in <span class="mono">_try_execute_function_calls()</span> (<span class="mono">_tools.py:1655</span>) uses
      <span class="mono">asyncio.gather()</span> for parallel execution:
<pre class="code">results = <span class="kw">await</span> asyncio.gather(*[
    invoke_with_termination_handling(fc, idx)
    <span class="kw">for</span> idx, fc <span class="kw">in</span> enumerate(function_calls)
])</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">If 3 tools each take 1 second, serial execution = 3 seconds, parallel = 1 second.
      For I/O-bound tools (API calls, DB queries), parallel execution <strong>drastically reduces latency</strong>.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">Uses <span class="mono">asyncio.gather()</span> for true concurrency.
      Each call is independently wrapped in error handling (<span class="mono">invoke_with_termination_handling</span>) —
      one tool failing doesn't affect the others. Returns a <span class="mono">(list[Content], should_terminate)</span> tuple.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a"><span class="mono">ThreadPoolExecutor</span> works for CPU-bound tasks but clashes with async;
      serial execution is simplest but slowest. MAF's <span class="mono">asyncio.gather()</span> perfectly fits I/O-bound scenarios and aligns with the framework's async architecture.</div></div>
  </div>
</details>

<h2>🔍 Real source: from signature to function spec</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_tools.py</span><span class="ln">signature → schema (simplified from :481 / :780 / :866)</span></div>
<pre class="code"><span class="cm"># ① Build a Pydantic model from the signature (_resolve_input_model :481)</span>
sig = inspect.signature(func)
fields = {
    pname: (annotation_of(param),
            param.default <span class="kw">if</span> has_default(param) <span class="kw">else</span> ...)  <span class="cm"># ... = required</span>
    <span class="kw">for</span> pname, param <span class="kw">in</span> sig.parameters.items()
    <span class="kw">if</span> pname <span class="kw">not in</span> {<span class="st">&quot;self&quot;</span>, <span class="st">&quot;cls&quot;</span>}}
input_model = create_model(f<span class="st">&quot;{name}_input&quot;</span>, **fields)

<span class="cm"># ② Pydantic emits the JSON Schema directly (_input_schema :780)</span>
<span class="kw">def</span> <span class="fn">parameters</span>(self):
    <span class="kw">return</span> self.input_model.model_json_schema()

<span class="cm"># ③ Wrap in the function shell (to_json_schema_spec :866)</span>
<span class="kw">def</span> <span class="fn">to_json_schema_spec</span>(self):
    <span class="kw">return</span> {<span class="st">&quot;type&quot;</span>: <span class="st">&quot;function&quot;</span>, <span class="st">&quot;function&quot;</span>: {
        <span class="st">&quot;name&quot;</span>: self.name,
        <span class="st">&quot;description&quot;</span>: self.description,
        <span class="st">&quot;parameters&quot;</span>: self.parameters()}}</pre>
</div>
<p>All three are <strong>simplified straight from the source</strong>: the framework <strong>hand-writes zero schema</strong> — it delegates to
<span class="mono">inspect</span> (read the signature) and <span class="mono">Pydantic</span> (emit the schema). Params without a default are marked <span class="mono">...</span>, so Pydantic
auto-places them in <span class="mono">required</span>. This is exactly where the &quot;signature IS the schema&quot; table above comes from.</p>

<h2>Why let type hints auto-generate the schema</h2>
<p>The naive approach makes you <strong>write two things</strong>: a Python function, and a JSON Schema describing it. The trouble is they
<strong>drift apart</strong> — you add a parameter to the function but forget to update the schema; the model then generates arguments per the
old schema and blows up at runtime. Any design where &quot;the same fact is written twice&quot; eventually breaks when the two fall out of sync.</p>
<p>MAF chooses a <strong>single source of truth</strong>: the signature is the <strong>only</strong> truth, and the schema is <strong>derived</strong> from it.
Change the signature and the schema follows on next generation, never drifting — this is the DRY (Don't Repeat Yourself) principle applied to tools.
Better still, the same Pydantic model <strong>does double duty</strong>: a schema to describe params outward, a validator to guard inputs inward — even the validation logic is free.</p>
<p>The price is accepting the framework's &quot;convention&quot;: use <span class="mono">Annotated[..., Field(description=…)]</span> for param docs and type hints for types.
What that small constraint buys is <strong>code as documentation, documentation that never goes stale</strong>. When you need full control, <span class="mono">@tool(schema=…)</span>
still lets you pass an explicit schema — the same &quot;narrow default + escape hatch&quot; pattern again.</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><span class="mono">@tool</span> → <span class="mono">FunctionTool</span> → JSON Schema → sent with the request.</li>
    <li>Model replies <span class="mono">function_call</span> → framework executes → <span class="mono">function_result</span> fed back → model continues.</li>
    <li>This loop runs automatically inside the ChatClient's <span class="mono">FunctionInvocationLayer</span> (not the Agent); callers are unaware.</li>
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

<h2>追踪一次真实请求：三层中间件如何交错</h2>
<p>三层是<strong>不同粒度</strong>，一次 <span class="mono">agent.run(&quot;北京天气?&quot;)</span>（带一个工具、需要一轮工具调用）里，它们会<strong>交错触发</strong>。
假设你注册了：1 个 <span class="mono">AgentMiddleware</span>（日志）、1 个 <span class="mono">ChatMiddleware</span>（计 token）、1 个 <span class="mono">FunctionMiddleware</span>（工具审计）。看它们的 before/after 如何嵌套：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Agent 层 before（最外，整轮一次）</h4>
    <p><span class="mono">AgentMiddleware.process</span> 在 <span class="mono">call_next()</span> 前执行：<span class="mono">log(&quot;run 开始&quot;)</span>，然后 <span class="mono">await call_next()</span> 把控制权交给内层。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Chat 层 before（第 1 次 LLM 调用）</h4>
    <p>run 内部第一次调模型，<span class="mono">ChatMiddleware.process</span> 被触发；<span class="mono">await call_next()</span> 真正发出请求。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Chat 层 after（第 1 次）</h4>
    <p>模型回 <span class="mono">function_call</span>。<span class="mono">ctx.result</span> 此刻是这次 <span class="mono">ChatResponse</span>，计 token 中间件累加它的 <span class="mono">usage_details</span>。Chat 层这次结束。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Function 层 before/after（执行工具）</h4>
    <p>框架要执行 <span class="mono">get_weather</span>，<span class="mono">FunctionMiddleware.process</span> 被触发：before 记下&quot;即将调用 get_weather&quot;，<span class="mono">await call_next()</span> 跑真正的函数，after 记下返回值。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Chat 层 before/after（第 2 次 LLM 调用）</h4>
    <p>带着工具结果再问一次模型——<span class="mono">ChatMiddleware</span> <strong>第二次</strong>被触发（同一次 run 内！），这次拿到最终文本。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Agent 层 after（最外，整轮一次）</h4>
    <p>控制权一路退回最外层，<span class="mono">AgentMiddleware</span> 的 <span class="mono">call_next()</span> 之后继续执行：此刻 <span class="mono">ctx.result</span> 是<strong>整轮</strong>的 <span class="mono">AgentResponse</span>，日志记下&quot;run 结束&quot;。</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 读懂这条轨迹</div>
  关键洞察：<strong>越内层、触发越频繁</strong>。一次 <span class="mono">run()</span> 里 <span class="mono">AgentMiddleware</span> 只触发 <strong>1 次</strong>，
  而 <span class="mono">ChatMiddleware</span> 触发了 <strong>2 次</strong>（两轮模型调用）、<span class="mono">FunctionMiddleware</span> 触发了 <strong>1 次</strong>（一个工具）。
  所以&quot;统计整轮耗时&quot;要放 Agent 层，&quot;给每次模型调用限流&quot;要放 Chat 层，&quot;给每个工具加审批&quot;要放 Function 层——<strong>选错层，粒度就错了</strong>。
</div>

<h2>三层粒度对照</h2>
<table class="t">
  <tr><th>中间件</th><th>包裹什么</th><th>context 类型</th><th>一次 run 触发</th><th>典型用途</th></tr>
  <tr><td class="mono">AgentMiddleware</td><td>整个 <span class="mono">agent.run()</span></td><td class="mono">AgentContext（:93）</td><td>1 次</td><td>全局日志、鉴权、整轮重试</td></tr>
  <tr><td class="mono">ChatMiddleware</td><td>每次 LLM 调用</td><td class="mono">ChatContext（:377）</td><td>N 次（每轮模型调用）</td><td>token 计数、限流、响应缓存</td></tr>
  <tr><td class="mono">FunctionMiddleware</td><td>每次工具执行</td><td class="mono">FunctionInvocationContext（:204）</td><td>M 次（每个工具调用）</td><td>工具审批、参数校验、沙箱</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> 也可以用装饰器写法 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">不想写类？用装饰器：
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> agent_middleware

<span class="nb">@agent_middleware</span>
<span class="kw">async def</span> <span class="fn">my_log</span>(context, call_next):
    <span class="fn">print</span>(<span class="st">"before"</span>)
    <span class="kw">await</span> call_next()
    <span class="fn">print</span>(<span class="st">"after"</span>)</pre>
      同样有 <span class="mono">@function_middleware</span> 和 <span class="mono">@chat_middleware</span>。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">类写法适合有状态的中间件（如计数器）；装饰器适合简单的无状态逻辑（如打日志）。
      两种风格共存，让你按场景选择最简洁的写法。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">@agent_middleware</span>（<span class="mono">_middleware.py:682</span>）
      内部用 <span class="mono">MiddlewareWrapper</span> 把函数包装成类协议——对管线来说，两种写法<strong>完全等价</strong>。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">有的框架只支持类写法（啰嗦）；有的只支持函数写法（难以持有状态）。
      MAF 两者都支持，且在内部统一为同一协议。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 执行顺序（洋葱模型） <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">假设注册了 A → B → C 三个中间件，执行顺序：
<pre class="code">A.process() 进入 → <span class="st">"A before"</span>
  B.process() 进入 → <span class="st">"B before"</span>
    C.process() 进入 → <span class="st">"C before"</span>
      ── 核心执行（call_next 到底）──
    C.process() 返回 → <span class="st">"C after"</span>
  B.process() 返回 → <span class="st">"B after"</span>
A.process() 返回 → <span class="st">"A after"</span></pre>
      每个中间件在 <span class="mono">await call_next()</span> 前后各有一次执行机会。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">理解洋葱模型，才能正确安排中间件顺序：
      想"最早记录 + 最晚结束"的日志中间件应放最外层；想"只拦截异常"的重试中间件应放内层。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">管线（<span class="mono">AgentMiddlewarePipeline</span>，<span class="mono">_middleware.py:847</span>）
      用闭包递归构建 <span class="mono">call_next</span> 链：从最后一个中间件开始，每层包裹前一层。
      执行结果统一挂在 <span class="mono">context.result</span>，无需返回值传递。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">Express.js 用线性 <span class="mono">next()</span>（无"出来"阶段）；
      Django 用 <span class="mono">__call__</span> 包裹（类似但不直观）。MAF 的 <span class="mono">call_next()</span> 洋葱模型最清晰——
      before 和 after 在同一个函数体里，代码局部性好。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> context 上有什么属性 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">三层 context 的核心字段：
<pre class="code"><span class="cm"># AgentContext (_middleware.py:93)</span>
ctx.agent       <span class="cm"># 正在运行的 Agent</span>
ctx.messages    <span class="cm"># list[Message] 输入消息</span>
ctx.session     <span class="cm"># AgentSession | None</span>
ctx.tools       <span class="cm"># 运行时工具覆盖</span>
ctx.stream      <span class="cm"># bool 是否流式</span>
ctx.metadata    <span class="cm"># dict 中间件间共享数据</span>
ctx.result      <span class="cm"># call_next() 后的执行结果</span>

<span class="cm"># ChatContext (_middleware.py:377)</span>
ctx.client      <span class="cm"># ChatClient 实例</span>
ctx.messages    <span class="cm"># 发给模型的消息</span>
ctx.options     <span class="cm"># ChatOptions</span>
ctx.stream      <span class="cm"># bool</span>
ctx.metadata    <span class="cm"># dict</span>
ctx.result      <span class="cm"># ChatResponse</span>

<span class="cm"># FunctionInvocationContext (_middleware.py:204)</span>
ctx.function    <span class="cm"># FunctionTool 实例</span>
ctx.arguments   <span class="cm"># 已验证的参数</span>
ctx.session     <span class="cm"># AgentSession | None</span>
ctx.tools       <span class="cm"># 当前运行的工具列表（可动态增删）</span>
ctx.result      <span class="cm"># 函数执行结果</span></pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">写中间件时，你要知道"我能读什么、能改什么"。
      <span class="mono">metadata</span> 是中间件间传数据的官方通道；<span class="mono">result</span> 是执行结果的观察点。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">每层 context 字段不同但结构一致：都有 <span class="mono">metadata</span>（共享）和 <span class="mono">result</span>（结果）。
      <span class="mono">FunctionInvocationContext</span> 还有 <span class="mono">add_tools()</span> / <span class="mono">remove_tools()</span>
      方法，支持<strong>动态工具增删</strong>（下一轮循环生效）。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">有的框架用全局变量传递中间件数据（线程不安全）；
      有的用 request 对象挂属性（不规范）。MAF 的 <span class="mono">metadata</span> dict 是显式、类型安全、请求级隔离的方案。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 中间件间的数据传递 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">中间件 A 记录开始时间，中间件 B 读取并计算耗时：
<pre class="code"><span class="cm"># 中间件 A（外层）</span>
<span class="kw">async def</span> <span class="fn">process</span>(self, ctx, call_next):
    ctx.metadata[<span class="st">"start_time"</span>] = time.time()
    <span class="kw">await</span> call_next()

<span class="cm"># 中间件 B（内层，call_next 之后读）</span>
<span class="kw">async def</span> <span class="fn">process</span>(self, ctx, call_next):
    <span class="kw">await</span> call_next()
    elapsed = time.time() - ctx.metadata[<span class="st">"start_time"</span>]</pre>
      <strong>关键</strong>：用 <span class="mono">context.metadata</span>，不用全局变量！</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">中间件之间经常需要协作：计时器中间件记录开始时间，日志中间件读取耗时。
      如果用全局变量，并发请求会互相干扰。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">context.metadata</span> 是每次请求独立的 <span class="mono">dict[str, Any]</span>，
      天然线程/协程安全。中间件只需约定 key 名即可通信，无需导入彼此。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">Python <span class="mono">contextvars</span>（更隐式，调试困难）；
      闭包捕获（仅限同一管线内）。<span class="mono">metadata</span> dict 最直观、最易调试。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> 真实中间件示例 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">三个生产级中间件：
<pre class="code"><span class="cm"># 1. 日志中间件（AgentMiddleware）</span>
<span class="kw">class</span> <span class="fn">LogMiddleware</span>(AgentMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, ctx, call_next):
        logger.info(f<span class="st">"Agent {ctx.agent.name} start"</span>)
        <span class="kw">await</span> call_next()
        logger.info(f<span class="st">"Agent done: {len(ctx.result.messages)} msgs"</span>)

<span class="cm"># 2. Token 计数中间件（ChatMiddleware）</span>
<span class="kw">class</span> <span class="fn">TokenCounter</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, ctx, call_next):
        <span class="kw">await</span> call_next()
        usage = ctx.result.usage_details
        ctx.metadata[<span class="st">"total_tokens"</span>] = usage[<span class="st">"input_token_count"</span>] + usage[<span class="st">"output_token_count"</span>]

<span class="cm"># 3. 限流中间件（ChatMiddleware）</span>
<span class="kw">class</span> <span class="fn">RateLimiter</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, ctx, call_next):
        <span class="kw">await</span> self.semaphore.acquire()
        <span class="kw">try</span>:
            <span class="kw">await</span> call_next()
        <span class="kw">finally</span>:
            self.semaphore.release()</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">这三个覆盖了最常见的生产需求：可观测性（日志）、成本控制（token 计数）、流量管理（限流）。
      它们展示了 <span class="mono">call_next()</span> 前后分别适合做什么。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">日志放 <span class="mono">AgentMiddleware</span>（整个 run 级别），
      token 计数和限流放 <span class="mono">ChatMiddleware</span>（每次 LLM 调用级别）——
      <strong>三层粒度让每个中间件精确拦截它关心的操作</strong>。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">用 AOP 框架（如 <span class="mono">aspectlib</span>）做切面（太重）；
      在 Agent 类里加 hook 方法（不够灵活）。MAF 的中间件管线是最标准的横切关注点解决方案。</div></div>
  </div>
</details>

<h2>🔍 真实源码：洋葱是怎么用闭包搭出来的</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_middleware.py</span><span class="ln">AgentMiddlewarePipeline.execute（简化自 :880）</span></div>
<pre class="code"><span class="kw">def</span> <span class="fn">create_next_handler</span>(index):
    <span class="kw">if</span> index &gt;= len(self._middleware):       <span class="cm"># 到底了 → 跑真正的执行</span>
        <span class="kw">async def</span> <span class="fn">final_wrapper</span>():
            context.result = <span class="kw">await</span> final_handler(context)
        <span class="kw">return</span> final_wrapper

    <span class="kw">async def</span> <span class="fn">current_handler</span>():            <span class="cm"># 这一层：把「下一层」当 call_next 传进去</span>
        <span class="kw">await</span> self._middleware[index].process(
            context, create_next_handler(index + 1))
    <span class="kw">return</span> current_handler

first = create_next_handler(0)
<span class="kw">with</span> contextlib.suppress(MiddlewareTermination):  <span class="cm"># 短路出口</span>
    <span class="kw">await</span> first()
<span class="kw">return</span> context.result</pre>
</div>
<p>洋葱不是某个魔法类，而是<strong>递归闭包</strong>搭出来的：<span class="mono">create_next_handler(index)</span> 为第 <span class="mono">index</span> 层
生成一个 <span class="mono">call_next</span>，它内部又调用 <span class="mono">create_next_handler(index+1)</span>——一层套一层，直到 <span class="mono">index</span> 越界，
返回 <span class="mono">final_wrapper</span>（真正干活、设 <span class="mono">context.result</span>）。每层的 <span class="mono">process</span> 收到的 <span class="mono">call_next</span> 就是&quot;剩下所有内层&quot;。</p>
<p>两个设计后果直接可见：①<strong>结果走 <span class="mono">context.result</span></strong>，不靠返回值层层上传，所以三层签名能完全统一；
②<strong>短路靠 <span class="mono">MiddlewareTermination</span></strong>（<span class="mono">_middleware.py:72</span>）：任何一层 <span class="mono">raise</span> 它，异常一路冒到 <span class="mono">execute()</span> 被
<span class="mono">contextlib.suppress</span> 吞掉，剩余的 after 阶段全部跳过——干净地提前结束整条管线。</p>

<h2>为什么用洋葱，而不是一个回调列表</h2>
<p>最容易想到的横切方案是 Express.js 式的<strong>线性回调</strong>：每个中间件拿到 <span class="mono">next</span>，调一下就轮到下一个。
它的问题是只有&quot;进去前&quot;那一刻好做事，&quot;出来后&quot;很别扭——你拿不到一个能 <span class="mono">await</span> 的「内层整体」，
也就没法把它包进 <span class="mono">try/finally</span>、<span class="mono">try/except</span> 或一个循环里。</p>
<p>MAF 的洋葱把&quot;剩下所有内层&quot;浓缩成<strong>一个无参的 <span class="mono">await call_next()</span></strong>。这一下子解锁了四种控制流，全写在<strong>同一个函数体</strong>里：</p>
<table class="t">
  <tr><th>你怎么写</th><th>效果</th><th>例子</th></tr>
  <tr><td class="mono">await call_next()</td><td>正常穿透</td><td>记日志</td></tr>
  <tr><td>不调 <span class="mono">call_next()</span>，直接设 <span class="mono">ctx.result</span></td><td><strong>短路</strong>：内层与真正执行都不跑</td><td>命中缓存直接返回</td></tr>
  <tr><td class="mono">try: await call_next() finally: …</td><td>无论成败都收尾</td><td>释放信号量（限流）</td></tr>
  <tr><td class="mono">for _ in range(n): await call_next()</td><td><strong>多次</strong>调用内层</td><td>重试（见 <span class="mono">_middleware.py:487</span> 的 RetryMiddleware 示例）</td></tr>
</table>
<p>把内层当成<strong>一等公民的可等待调用</strong>，正是洋葱比线性回调强的根本原因：调 0 次（短路）、1 次（正常）、N 次（重试）都行，
而且 before 与 after 的逻辑挨在一起，<strong>代码局部性</strong>极好。三层中间件、类/装饰器两种写法，最终都被
<span class="mono">create_next_handler</span> 这套闭包统一成同一种洋葱——这就是&quot;一个机制，处处复用&quot;。</p>
<p>一个最实用的短路场景是<strong>护栏 / 审批</strong>：在 <span class="mono">call_next()</span> <em>之前</em>检查输入，不合规就直接
<span class="mono">raise MiddlewareTermination(&quot;Validation failed&quot;)</span>（框架内部正是这么用的，见 <span class="mono">_middleware.py:238</span>）。
因为异常在内层真正执行<strong>之前</strong>抛出，那次昂贵的模型调用 / 工具执行<strong>根本不会发生</strong>——你用十几行中间件就实现了&quot;先审后跑&quot;，
且<strong>无需改动 Agent 或 ChatClient 一行源码</strong>。这正是本课开头那句承诺&quot;横切地加逻辑&quot;能落地的机制底座。</p>

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
  <br>想从零写一个自己的中间件？见<a href="18-custom-middleware.html">第 18 课 · 写自己的中间件</a>。
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

<h2>Tracing a real request: how the three layers interleave</h2>
<p>The three layers are <strong>different granularities</strong>, so within one <span class="mono">agent.run(&quot;weather in Beijing?&quot;)</span>
(one tool, one tool-call round) they <strong>interleave</strong>. Say you registered: one <span class="mono">AgentMiddleware</span> (logging),
one <span class="mono">ChatMiddleware</span> (token counting), one <span class="mono">FunctionMiddleware</span> (tool auditing). Watch how their before/after nest:</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Agent layer before (outermost, once per run)</h4>
    <p><span class="mono">AgentMiddleware.process</span> runs before <span class="mono">call_next()</span>: <span class="mono">log(&quot;run start&quot;)</span>, then <span class="mono">await call_next()</span> hands control inward.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Chat layer before (1st LLM call)</h4>
    <p>The run makes its first model call; <span class="mono">ChatMiddleware.process</span> fires; <span class="mono">await call_next()</span> sends the actual request.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Chat layer after (1st)</h4>
    <p>The model returns a <span class="mono">function_call</span>. <span class="mono">ctx.result</span> is now this <span class="mono">ChatResponse</span>; the token middleware accumulates its <span class="mono">usage_details</span>. This Chat pass ends.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Function layer before/after (run the tool)</h4>
    <p>The framework executes <span class="mono">get_weather</span>; <span class="mono">FunctionMiddleware.process</span> fires: before notes &quot;about to call get_weather&quot;, <span class="mono">await call_next()</span> runs the real function, after notes the return value.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Chat layer before/after (2nd LLM call)</h4>
    <p>With the tool result, the model is asked again — <span class="mono">ChatMiddleware</span> fires a <strong>second</strong> time (within the same run!), now yielding the final text.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Agent layer after (outermost, once per run)</h4>
    <p>Control unwinds back out; <span class="mono">AgentMiddleware</span> resumes after its <span class="mono">call_next()</span>: now <span class="mono">ctx.result</span> is the <strong>whole-run</strong> <span class="mono">AgentResponse</span>, and the log notes &quot;run done&quot;.</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 Reading this trace</div>
  Key insight: <strong>the deeper the layer, the more often it fires</strong>. In one <span class="mono">run()</span>, <span class="mono">AgentMiddleware</span> fires <strong>once</strong>,
  while <span class="mono">ChatMiddleware</span> fired <strong>twice</strong> (two model calls) and <span class="mono">FunctionMiddleware</span> fired <strong>once</strong> (one tool).
  So &quot;measure whole-run latency&quot; belongs in the Agent layer, &quot;rate-limit each model call&quot; in the Chat layer, &quot;approve each tool&quot; in the Function layer — <strong>pick the wrong layer and your granularity is wrong</strong>.
</div>

<h2>Three granularities compared</h2>
<table class="t">
  <tr><th>Middleware</th><th>Wraps what</th><th>Context type</th><th>Fires per run</th><th>Typical use</th></tr>
  <tr><td class="mono">AgentMiddleware</td><td>the whole <span class="mono">agent.run()</span></td><td class="mono">AgentContext (:93)</td><td>once</td><td>global logging, auth, whole-run retry</td></tr>
  <tr><td class="mono">ChatMiddleware</td><td>each LLM call</td><td class="mono">ChatContext (:377)</td><td>N times (per model call)</td><td>token counting, rate-limit, response cache</td></tr>
  <tr><td class="mono">FunctionMiddleware</td><td>each tool execution</td><td class="mono">FunctionInvocationContext (:204)</td><td>M times (per tool call)</td><td>tool approval, arg validation, sandbox</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> Decorator shortcut <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">Don't want a class? Use a decorator:
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> agent_middleware

<span class="nb">@agent_middleware</span>
<span class="kw">async def</span> <span class="fn">my_log</span>(context, call_next):
    <span class="fn">print</span>(<span class="st">"before"</span>)
    <span class="kw">await</span> call_next()
    <span class="fn">print</span>(<span class="st">"after"</span>)</pre>
      Similarly <span class="mono">@function_middleware</span> and <span class="mono">@chat_middleware</span>.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Class-based suits stateful middleware (e.g. counters); decorators suit simple stateless logic (e.g. logging).
      Both styles coexist so you pick the most concise one for your scenario.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">@agent_middleware</span> (<span class="mono">_middleware.py:682</span>)
      internally uses <span class="mono">MiddlewareWrapper</span> to convert the function into the class protocol —
      to the pipeline, both styles are <strong>completely equivalent</strong>.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Some frameworks only support class-based (verbose); others only function-based (hard to hold state).
      MAF supports both and unifies them into one protocol internally.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Execution order (onion model) <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">Given middleware registered A → B → C, the execution order is:
<pre class="code">A.process() enters → <span class="st">"A before"</span>
  B.process() enters → <span class="st">"B before"</span>
    C.process() enters → <span class="st">"C before"</span>
      ── core execution (call_next bottoms out) ──
    C.process() returns → <span class="st">"C after"</span>
  B.process() returns → <span class="st">"B after"</span>
A.process() returns → <span class="st">"A after"</span></pre>
      Each middleware gets one chance before and one after <span class="mono">await call_next()</span>.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Understanding the onion model is essential for ordering middleware correctly:
      a logger that should "start first + finish last" belongs outermost; a retry interceptor belongs inner.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">The pipeline (<span class="mono">AgentMiddlewarePipeline</span>, <span class="mono">_middleware.py:847</span>)
      builds the <span class="mono">call_next</span> chain via closure recursion: starting from the last middleware, each wraps the previous.
      Results are placed on <span class="mono">context.result</span> — no return-value passing needed.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Express.js uses linear <span class="mono">next()</span> (no "way out" phase);
      Django uses <span class="mono">__call__</span> wrapping (similar but less intuitive). MAF's <span class="mono">call_next()</span> onion model is clearest —
      before and after live in the same function body, excellent code locality.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Context attributes <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">Core fields across the three context types:
<pre class="code"><span class="cm"># AgentContext (_middleware.py:93)</span>
ctx.agent       <span class="cm"># the running Agent</span>
ctx.messages    <span class="cm"># list[Message] input messages</span>
ctx.session     <span class="cm"># AgentSession | None</span>
ctx.tools       <span class="cm"># runtime tool overrides</span>
ctx.stream      <span class="cm"># bool streaming?</span>
ctx.metadata    <span class="cm"># dict shared between middleware</span>
ctx.result      <span class="cm"># execution result after call_next()</span>

<span class="cm"># ChatContext (_middleware.py:377)</span>
ctx.client      <span class="cm"># ChatClient instance</span>
ctx.messages    <span class="cm"># messages sent to model</span>
ctx.options     <span class="cm"># ChatOptions</span>
ctx.stream      <span class="cm"># bool</span>
ctx.metadata    <span class="cm"># dict</span>
ctx.result      <span class="cm"># ChatResponse</span>

<span class="cm"># FunctionInvocationContext (_middleware.py:204)</span>
ctx.function    <span class="cm"># FunctionTool instance</span>
ctx.arguments   <span class="cm"># validated arguments</span>
ctx.session     <span class="cm"># AgentSession | None</span>
ctx.tools       <span class="cm"># live tool list (dynamically add/remove)</span>
ctx.result      <span class="cm"># function execution result</span></pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">When writing middleware you need to know "what can I read, what can I change?"
      <span class="mono">metadata</span> is the official channel for inter-middleware data; <span class="mono">result</span> is where you observe outcomes.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">Each layer's context has different fields but a consistent structure: all have <span class="mono">metadata</span> (shared) and <span class="mono">result</span> (outcome).
      <span class="mono">FunctionInvocationContext</span> additionally provides <span class="mono">add_tools()</span> / <span class="mono">remove_tools()</span>
      methods for <strong>dynamic tool modification</strong> (takes effect next loop iteration).</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Some frameworks use global variables for middleware data (not thread-safe);
      others attach attributes to a request object (ad-hoc). MAF's <span class="mono">metadata</span> dict is explicit, type-safe, and request-scoped.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Passing data between middleware <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">Middleware A records start time; middleware B reads it to compute elapsed time:
<pre class="code"><span class="cm"># Middleware A (outer)</span>
<span class="kw">async def</span> <span class="fn">process</span>(self, ctx, call_next):
    ctx.metadata[<span class="st">"start_time"</span>] = time.time()
    <span class="kw">await</span> call_next()

<span class="cm"># Middleware B (inner, reads after call_next)</span>
<span class="kw">async def</span> <span class="fn">process</span>(self, ctx, call_next):
    <span class="kw">await</span> call_next()
    elapsed = time.time() - ctx.metadata[<span class="st">"start_time"</span>]</pre>
      <strong>Key</strong>: use <span class="mono">context.metadata</span>, not global variables!</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Middleware often need to cooperate: a timer records start time, a logger reads elapsed time.
      Global variables would cause interference between concurrent requests.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">context.metadata</span> is a per-request <span class="mono">dict[str, Any]</span>,
      inherently safe across threads/coroutines. Middleware just agree on key names to communicate — no imports needed between them.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Python <span class="mono">contextvars</span> (more implicit, harder to debug);
      closure capture (only within same pipeline). The <span class="mono">metadata</span> dict is the most straightforward and debuggable.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> Real-world middleware examples <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">Three production-grade middleware:
<pre class="code"><span class="cm"># 1. Logging middleware (AgentMiddleware)</span>
<span class="kw">class</span> <span class="fn">LogMiddleware</span>(AgentMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, ctx, call_next):
        logger.info(f<span class="st">"Agent {ctx.agent.name} start"</span>)
        <span class="kw">await</span> call_next()
        logger.info(f<span class="st">"Agent done: {len(ctx.result.messages)} msgs"</span>)

<span class="cm"># 2. Token-counting middleware (ChatMiddleware)</span>
<span class="kw">class</span> <span class="fn">TokenCounter</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, ctx, call_next):
        <span class="kw">await</span> call_next()
        usage = ctx.result.usage_details
        ctx.metadata[<span class="st">"total_tokens"</span>] = usage[<span class="st">"input_token_count"</span>] + usage[<span class="st">"output_token_count"</span>]

<span class="cm"># 3. Rate-limit middleware (ChatMiddleware)</span>
<span class="kw">class</span> <span class="fn">RateLimiter</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, ctx, call_next):
        <span class="kw">await</span> self.semaphore.acquire()
        <span class="kw">try</span>:
            <span class="kw">await</span> call_next()
        <span class="kw">finally</span>:
            self.semaphore.release()</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">These three cover the most common production needs: observability (logging), cost control (token counting),
      traffic management (rate limiting). They show what's best done before vs after <span class="mono">call_next()</span>.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">Logging goes in <span class="mono">AgentMiddleware</span> (whole-run level),
      token counting and rate limiting go in <span class="mono">ChatMiddleware</span> (per-LLM-call level) —
      <strong>three granularity levels let each middleware precisely intercept what it cares about</strong>.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">AOP frameworks like <span class="mono">aspectlib</span> (too heavy);
      hook methods in the Agent class (not flexible enough). MAF's middleware pipeline is the standard cross-cutting concern solution.</div></div>
  </div>
</details>

<h2>🔍 Real source: how the onion is built from closures</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_middleware.py</span><span class="ln">AgentMiddlewarePipeline.execute (simplified from :880)</span></div>
<pre class="code"><span class="kw">def</span> <span class="fn">create_next_handler</span>(index):
    <span class="kw">if</span> index &gt;= len(self._middleware):       <span class="cm"># bottomed out → run the real execution</span>
        <span class="kw">async def</span> <span class="fn">final_wrapper</span>():
            context.result = <span class="kw">await</span> final_handler(context)
        <span class="kw">return</span> final_wrapper

    <span class="kw">async def</span> <span class="fn">current_handler</span>():            <span class="cm"># this layer: pass &quot;the next layer&quot; in as call_next</span>
        <span class="kw">await</span> self._middleware[index].process(
            context, create_next_handler(index + 1))
    <span class="kw">return</span> current_handler

first = create_next_handler(0)
<span class="kw">with</span> contextlib.suppress(MiddlewareTermination):  <span class="cm"># short-circuit exit</span>
    <span class="kw">await</span> first()
<span class="kw">return</span> context.result</pre>
</div>
<p>The onion isn't a magic class — it's built from <strong>recursive closures</strong>: <span class="mono">create_next_handler(index)</span> produces a
<span class="mono">call_next</span> for layer <span class="mono">index</span>, which itself calls <span class="mono">create_next_handler(index+1)</span> — nesting until <span class="mono">index</span> runs off the end,
returning <span class="mono">final_wrapper</span> (the real work that sets <span class="mono">context.result</span>). Each layer's <span class="mono">process</span> receives a <span class="mono">call_next</span> that <em>is</em> &quot;all the inner layers&quot;.</p>
<p>Two design consequences are immediately visible: ① <strong>the result travels on <span class="mono">context.result</span></strong>, not via return values bubbling up — which is why all three signatures can be identical;
② <strong>short-circuit is via <span class="mono">MiddlewareTermination</span></strong> (<span class="mono">_middleware.py:72</span>): any layer can <span class="mono">raise</span> it, the exception bubbles up to <span class="mono">execute()</span> and is swallowed by
<span class="mono">contextlib.suppress</span>, skipping all remaining after-stages — a clean early exit for the whole pipeline.</p>

<h2>Why an onion, not a list of callbacks</h2>
<p>The obvious cross-cutting design is an Express.js-style <strong>linear callback</strong>: each middleware gets <span class="mono">next</span>, calls it, and the next one runs.
The problem is only the &quot;before&quot; moment is easy; the &quot;after&quot; is awkward — you have no single <span class="mono">await</span>-able &quot;inner whole&quot; to wrap in <span class="mono">try/finally</span>, <span class="mono">try/except</span>, or a loop.</p>
<p>MAF's onion compresses &quot;all the inner layers&quot; into <strong>one no-arg <span class="mono">await call_next()</span></strong>. That unlocks four control flows, all in the <strong>same function body</strong>:</p>
<table class="t">
  <tr><th>How you write it</th><th>Effect</th><th>Example</th></tr>
  <tr><td class="mono">await call_next()</td><td>normal pass-through</td><td>logging</td></tr>
  <tr><td>skip <span class="mono">call_next()</span>, set <span class="mono">ctx.result</span></td><td><strong>short-circuit</strong>: inner layers and real execution never run</td><td>return a cache hit</td></tr>
  <tr><td class="mono">try: await call_next() finally: …</td><td>clean up regardless of outcome</td><td>release a semaphore (rate-limit)</td></tr>
  <tr><td class="mono">for _ in range(n): await call_next()</td><td>call the inner whole <strong>multiple</strong> times</td><td>retry (see the RetryMiddleware example, <span class="mono">_middleware.py:487</span>)</td></tr>
</table>
<p>Treating the inner whole as a <strong>first-class awaitable</strong> is exactly why the onion beats a linear callback list: call it 0 times (short-circuit), once (normal), or N times (retry) — and before/after logic sits together for great <strong>code locality</strong>.
Three layers, class or decorator form — all are unified by the same <span class="mono">create_next_handler</span> closures into one onion: &quot;one mechanism, reused everywhere&quot;.</p>
<p>The most practical short-circuit is a <strong>guardrail / approval</strong>: check the input <em>before</em> <span class="mono">call_next()</span> and, if non-compliant, just
<span class="mono">raise MiddlewareTermination(&quot;Validation failed&quot;)</span> (exactly how the framework uses it internally — see <span class="mono">_middleware.py:238</span>).
Because the exception is raised <strong>before</strong> the inner execution, that expensive model call / tool run <strong>never happens</strong> — a dozen lines of middleware gives you &quot;validate, then run&quot;,
with <strong>zero changes to Agent or ChatClient source</strong>. That is the mechanism backing this lesson's opening promise of adding logic &quot;cross-cuttingly&quot;.</p>

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
  <br>Want to write your own from scratch? See <a href="18-custom-middleware.html">Lesson 18 · Writing Your Own Middleware</a>.
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

upper = UpperCase(id=<span class="st">"upper"</span>)
wf = WorkflowBuilder(start_executor=upper) \
    .add_edge(upper, reverse).build()
events = <span class="kw">await</span> wf.run(<span class="st">"hello"</span>)  <span class="cm"># → "OLLEH"</span></pre>
</div>

<h2>追踪一次工作流执行：writer → reviewer</h2>
<p>抽象讲完，我们用一张<strong>两节点图</strong>端到端走一遍。两个 Executor——<span class="mono">writer</span>（写草稿）和
<span class="mono">reviewer</span>（评审并产出）——连成一条边 <span class="mono">writer → reviewer</span>，再投递一条初始消息。
关键在于：Workflow 不是"依次调用两个函数"，而是按 <strong>超步（superstep）</strong>推进的——
这正是它能<strong>断点续跑、并发、可观测</strong>的根因（<span class="mono">_workflow.py:211</span> 称之为 Pregel 式执行）。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">建图</span></div>
<pre><span class="nb">@executor</span>(id=<span class="st">"writer"</span>)
<span class="kw">async def</span> <span class="fn">writer</span>(topic: str, ctx: WorkflowContext[str]):
    <span class="kw">await</span> ctx.send_message(<span class="st">f"草稿：一首关于{topic}的俳句"</span>)   <span class="cm"># 发给下游</span>

<span class="nb">@executor</span>(id=<span class="st">"reviewer"</span>)
<span class="kw">async def</span> <span class="fn">reviewer</span>(draft: str, ctx: WorkflowContext[Never, str]):
    <span class="kw">await</span> ctx.yield_output(draft + <span class="st">" ✓ 已评审"</span>)        <span class="cm"># 产出最终结果</span>

wf = WorkflowBuilder(start_executor=writer).add_edge(writer, reviewer).build()
result = <span class="kw">await</span> wf.run(<span class="st">"大海"</span>)</pre>
</div>

<div class="vflow">
  <div class="step"><div class="num">0</div><div class="sc"><h4>投递初始消息（超步 0）</h4>
    <p>引擎把 <span class="mono">"大海"</span> 当作消息投给<strong>起始节点</strong> <span class="mono">writer</span>，并发出 <span class="mono">started</span> 事件。
    此刻<strong>活跃节点：无</strong>；<strong>在途消息</strong>：<span class="mono">"大海" → writer</span>。</p></div></div>
  <div class="step"><div class="num">1</div><div class="sc"><h4>超步 1：writer 被唤起</h4>
    <p>本超步里，所有"收到消息"的节点被<strong>并行</strong>唤起。<span class="mono">writer</span> 的 handler 跑完，
    调 <span class="mono">ctx.send_message(draft)</span> 把草稿写到边上——但<strong>不立即送达</strong>，而是缓冲到超步末尾。</p>
<pre class="code"><span class="cm"># 本超步可观测到的事件</span>
WorkflowEvent(<span class="st">"executor_invoked"</span>,  executor_id=<span class="st">"writer"</span>)
WorkflowEvent(<span class="st">"executor_completed"</span>, executor_id=<span class="st">"writer"</span>)
<span class="cm"># 边 writer→reviewer 上此刻缓冲着一条消息（事件流里看不到）</span></pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>超步边界：统一投递 + 存检查点</h4>
    <p>超步 1 结束时，引擎一次性<strong>投递</strong>所有在途消息（草稿送达 <span class="mono">reviewer</span>），
    并把当前状态<strong>存一个检查点</strong>（<span class="mono">_runner.py:143</span>）。下一超步的活跃集合 = <span class="mono">&#123;reviewer&#125;</span>。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>超步 2：reviewer 被唤起并产出</h4>
    <p><span class="mono">reviewer</span> 收到草稿，调 <span class="mono">yield_output()</span> 产出终值——这会发一个 <span class="mono">output</span> 事件：</p>
<pre class="code">WorkflowEvent(<span class="st">"executor_invoked"</span>, executor_id=<span class="st">"reviewer"</span>)
WorkflowEvent(<span class="st">"output"</span>, executor_id=<span class="st">"reviewer"</span>,
             data=<span class="st">"草稿：一首关于大海的俳句 ✓ 已评审"</span>)
WorkflowEvent(<span class="st">"executor_completed"</span>, executor_id=<span class="st">"reviewer"</span>)</pre></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>无消息在途 → 图空闲，终止</h4>
    <p>超步 2 末尾没有任何新消息在途，图进入 <span class="mono">IDLE</span>，<span class="mono">run()</span> 返回。
    <span class="mono">result.get_outputs()</span> → <span class="mono">["…✓ 已评审"]</span>，
    <span class="mono">result.get_final_state()</span> → <span class="mono">WorkflowRunState.IDLE</span>。</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 读懂这条轨迹</div>
  三个常被忽略的关键点：①<strong>节点之间传的是消息，不是返回值</strong>——<span class="mono">send_message</span> 把数据放到边上，
  接收方要到<em>下一个</em>超步才被唤起；②<strong>消息在超步边界统一投递</strong>，所以同一超步里被唤起的多个节点彼此<strong>看不到对方本步的输出</strong>（这正是 fan-out 能安全并行的前提）；
  ③<strong>每个超步末尾都会存检查点</strong>——进程崩了也能从最近一个超步恢复，这是"单 Agent 工具循环"给不了的。
  还有一个易错点：<span class="mono">send_message</span> 产生的<strong>边上消息在事件流里看不到</strong>（<span class="mono">_workflow.py:221</span>），
  你能观测到的只有 <span class="mono">output</span> / 自定义事件 / 状态事件——想看节点间数据流，得用 OTel 的 <span class="mono">message.send</span> span（见第 14 课）。
</div>

<h2>图执行模型：超步驱动</h2>
<p>把上面的轨迹抽象出来，就是 Workflow 的执行心智模型：一轮一轮的<strong>超步</strong>，每轮"唤起活跃节点 → 缓冲消息 → 边界投递+存档"，直到没有消息可投递。</p>
<div class="flow">
  <div class="node"><div class="nt">超步 0</div><div class="nd">投递初始消息</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">超步 1</div><div class="nd">writer 唤起 · send</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">边界</div><div class="nd">投递 + 检查点</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">超步 2</div><div class="nd">reviewer 唤起 · yield</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">IDLE</div><div class="nd">无消息 → 终止</div></div>
</div>
<p>这与你在第 8 课见过的<strong>单 Agent 工具循环</strong>是两种不同的控制结构。下面并排对比，帮你判断"什么时候该上 Workflow"：</p>
<div class="cols">
  <div class="col"><h4>单 Agent 工具循环</h4>
    <p>一个 <span class="mono">while</span> 循环：调模型 → 执行工具 → 再调模型……状态<strong>全在内存里的那一个消息列表</strong>。
    简单、低延迟，适合"一个智能体 + 几个工具"的对话式任务。但它<strong>崩溃即丢失</strong>、天然串行、
    也难以在中途插入人工审核或并发分支。</p></div>
  <div class="col"><h4>Workflow 图</h4>
    <p>显式的<strong>节点 + 边 + 超步</strong>调度：可在边界<strong>存档/恢复</strong>、可 fan-out 并发、
    可在边上挂条件与开关、可暂停等待人工输入（<span class="mono">ctx.request_info()</span>）。
    代价是你得先<strong>把流程画成图</strong>——换来的是可控、可观测、可恢复。</p></div>
</div>

<h2>🔍 真实源码：建图与执行钩子</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_workflows/_workflow_builder.py</span><span class="ln">add_edge / build（简化自 :228 / :725）</span></div>
<pre class="code"><span class="kw">def</span> <span class="fn">add_edge</span>(self, source: Executor | SupportsAgentRun,
             target: Executor | SupportsAgentRun,
             condition: EdgeCondition | None = <span class="kw">None</span>) -> Self:
    <span class="cm"># 登记一条有向边；source 的输出类型须与 target 的输入类型兼容</span>
    ...
    <span class="kw">return</span> self                        <span class="cm"># 返回自身 → 支持链式</span>

<span class="kw">def</span> <span class="fn">build</span>(self) -> Workflow:
    <span class="cm"># 校验：起始节点已设、边都合法、图连通、相邻类型兼容</span>
    <span class="cm"># 任一不满足即抛 WorkflowValidationError（构建期就报错，而非运行时）</span>
    <span class="kw">return</span> Workflow(...)               <span class="cm"># 返回不可变的 Workflow</span></pre>
</div>
<p>注意：<strong>起始节点是构造器参数</strong>（<span class="mono">WorkflowBuilder(start_executor=writer)</span>，<span class="mono">_workflow_builder.py:89</span>），
并没有 <span class="mono">set_start_executor()</span> 方法。<span class="mono">build()</span> 把校验放在<strong>构建期</strong>——
类型不兼容、图不连通这类错误在你 <span class="mono">run()</span> 之前就被拦下。</p>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_workflows/_executor.py</span><span class="ln">Executor.execute（简化自 :219）</span></div>
<pre class="code"><span class="kw">async def</span> <span class="fn">execute</span>(self, message, source_executor_ids, state, runner_context, ...):
    <span class="cm"># 由引擎调用——别自己调、也别覆写；要定制行为请写 @handler</span>
    <span class="kw">with</span> create_processing_span(self.id, ...):      <span class="cm"># 自动开一个 OTel span（见第 14 课）</span>
        handler = self._find_handler(message)        <span class="cm"># 按消息类型挑选 @handler</span>
        context = self._create_context_for_handler(...)  <span class="cm"># 造 WorkflowContext</span>
        <span class="kw">await</span> handler(message, context)              <span class="cm"># 真正干活的一行</span></pre>
</div>
<p>这解释了"两种写法为何等价"：无论你写 Executor 子类还是用 <span class="mono">@executor</span> 装函数，
引擎统一通过 <span class="mono">execute()</span> → <span class="mono">_find_handler()</span> 找到对应 handler 再调用。
<span class="mono">@handler</span>（<span class="mono">_executor.py:530</span>）只是把方法的输入类型登记进 <span class="mono">self._handlers</span>，供这里按类型分发。</p>

<h2>为什么要图式编排</h2>
<p>把流程显式画成图，并非"为复杂而复杂"，而是用一点前期成本换来三类生产级能力：</p>
<table class="t">
  <tr><th>能力</th><th>图带来了什么</th><th>底层机制</th></tr>
  <tr><td><strong>可恢复</strong></td><td>长流程跑到一半崩溃，可从最近超步续跑，不必从头再来</td><td class="mono">超步边界检查点</td></tr>
  <tr><td><strong>可并发</strong></td><td>无依赖的节点在同一超步并行跑，延迟从"求和"降到"取最大"</td><td class="mono">add_fan_out_edges</td></tr>
  <tr><td><strong>可控</strong></td><td>条件边/开关让路由显式可见，而非藏在某个 if 里</td><td class="mono">add_switch_case_edge_group</td></tr>
  <tr><td><strong>可干预</strong></td><td>节点可暂停、向外请求人工输入，拿到答复再继续</td><td class="mono">ctx.request_info()</td></tr>
</table>
<p>反过来说，如果你的任务就是"一个 Agent 带几个工具、一次对话搞定"，那么<strong>单 Agent 循环更省事</strong>——
别为它套一张只有一个节点的图。Workflow 的价值在<strong>多节点协作 + 长流程 + 需要可靠性</strong>的场景才真正兑现。
下一课的五种<strong>编排模式</strong>，本质上就是"把常见多 Agent 拓扑预先画好的 Workflow"。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Executor 两种写法 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<strong>Class-based</strong>（Executor 子类 + @handler）：
<pre class="code"><span class="kw">class</span> <span class="fn">UpperCase</span>(Executor):
    <span class="nb">@handler</span>
    <span class="kw">async def</span> <span class="fn">to_upper</span>(self, text: str, ctx: WorkflowContext):
        <span class="kw">await</span> ctx.send_message(text.upper())</pre>
<strong>Function-based</strong>（@executor 装饰独立函数）：
<pre class="code"><span class="nb">@executor</span>(id=<span class="st">&quot;reverse&quot;</span>)
<span class="kw">async def</span> <span class="fn">reverse</span>(text: str, ctx: WorkflowContext):
    <span class="kw">await</span> ctx.yield_output(text[::-1])</pre>
函数式写法会自动包装成 <span class="mono">FunctionExecutor</span>，功能完全等价。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">不同场景有不同诉求：简单节点写一个函数最快，复杂节点需要在类里维护 <span class="mono">__init__</span> 参数、多个 handler、甚至复用继承。
      两种写法让框架<strong>同时服务脚本级原型和生产级代码</strong>。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">MAF 让 <span class="mono">@executor</span> 装饰器自动把函数包成 <span class="mono">FunctionExecutor</span>，
      内部共享同一套 handler 注册和消息分发机制。你可以在<strong>同一张图里混用两种写法</strong>——类节点和函数节点通过边自由连接。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">LangGraph 只支持函数节点（无类继承概念）；
      Prefect 只支持 <span class="mono">@task</span> 函数。MAF 两者兼备，是更灵活的选择。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Edge 的高级模式 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code"><span class="cm"># 1-to-1</span>
builder.add_edge(node_a, node_b)
<span class="cm"># 1-to-many (fan-out)</span>
builder.add_fan_out_edges(splitter, [worker1, worker2, worker3])
<span class="cm"># many-to-1 (fan-in)</span>
builder.add_fan_in_edges([worker1, worker2, worker3], aggregator)
<span class="cm"># 条件分支 (switch-case)</span>
builder.add_switch_case_edge_group(router, [
    Case(target=fast_path, condition=<span class="kw">lambda</span> msg: msg.priority == <span class="st">&quot;high&quot;</span>),
    Default(target=slow_path),
])
<span class="cm"># 链式快捷 (等价于连续 add_edge)</span>
builder.add_chain([step1, step2, step3])</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">真实工作流不只是线性管线——你需要并行 map-reduce（fan-out/fan-in）、条件路由（switch-case）等拓扑。
      如果框架只提供 <span class="mono">add_edge</span>，复杂图的构建代码会非常冗长且易出错。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">MAF 在 <span class="mono">WorkflowBuilder</span> 上提供五种边方法，覆盖所有常见拓扑。
      还有 <span class="mono">add_multi_selection_edge_group</span>（动态多选）用于"根据消息内容选择下游子集"的场景。
      所有方法返回 <span class="mono">Self</span>，支持链式调用。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">Airflow 用 <span class="mono">&gt;&gt;</span> 运算符连边，可读但只支持 1-to-1；
      LangGraph 用字典声明条件路由。MAF 用显式方法名（<span class="mono">add_fan_out_edges</span>）让拓扑意图一目了然。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> WorkflowContext 的 API <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code"><span class="nb">@handler</span>
<span class="kw">async def</span> <span class="fn">process</span>(self, msg: str, ctx: WorkflowContext):
    ctx.set_state(<span class="st">&quot;count&quot;</span>, ctx.get_state(<span class="st">&quot;count&quot;</span>, 0) + 1)  <span class="cm"># 读写共享状态</span>
    <span class="kw">await</span> ctx.send_message(result, target_id=<span class="st">&quot;next&quot;</span>)  <span class="cm"># 转发给下一节点</span>
    <span class="kw">await</span> ctx.yield_output(final)  <span class="cm"># 输出最终结果</span>
    <span class="kw">await</span> ctx.add_event(WorkflowEvent.status(...))  <span class="cm"># 自定义事件</span></pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a"><span class="mono">WorkflowContext</span> 是节点与引擎之间的<strong>唯一通信通道</strong>。
      没有它，节点无法知道自己的上游是谁（<span class="mono">source_executor_ids</span>）、
      无法向下游传数据、无法把结果暴露给调用者、也无法操作跨节点的共享状态。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">Context 提供四大能力：
      ① <span class="mono">send_message()</span> 向下游传消息（可指定 <span class="mono">target_id</span>）；
      ② <span class="mono">yield_output()</span> 向调用者输出结果；
      ③ <span class="mono">get_state/set_state</span> 读写工作流级共享状态；
      ④ <span class="mono">request_info()</span> 请求外部输入（Human-in-the-Loop）。
      还有 <span class="mono">is_streaming()</span> 让节点感知当前是否流式运行。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">Temporal 把状态放在 workflow 函数的局部变量里；
      LangGraph 用全局 State 字典。MAF 选择显式 Context 对象——既不污染函数签名，也不引入全局可变状态。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> workflow.run() 返回值 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code">result: WorkflowRunResult = <span class="kw">await</span> wf.run(<span class="st">&quot;hello&quot;</span>)
outputs = result.get_outputs()          <span class="cm"># [&quot;OLLEH&quot;] — 最终结果</span>
intermediates = result.get_intermediate_outputs()  <span class="cm"># 中间输出</span>
state = result.get_final_state()        <span class="cm"># WorkflowRunState.IDLE</span>
<span class="cm"># WorkflowRunResult 本身继承 list[WorkflowEvent]，可直接遍历</span>
<span class="kw">for</span> event <span class="kw">in</span> result:
    <span class="fn">print</span>(event.type, event.data)</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">工作流执行后，你可能只关心最终输出（<span class="mono">get_outputs</span>），也可能需要调试每一步的事件轨迹。
      <span class="mono">WorkflowRunResult</span> 同时提供两种视角，让"用"和"调"都方便。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">WorkflowRunResult</span> 继承自 <span class="mono">list[WorkflowEvent]</span>，
      所以你可以当列表遍历所有事件，也可以用语义化方法提取：
      <span class="mono">get_outputs()</span>（终端输出）、<span class="mono">get_intermediate_outputs()</span>（中间结果）、
      <span class="mono">get_request_info_events()</span>（HITL 请求）、<span class="mono">status_timeline()</span>（状态变更时间线）。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">Prefect 返回 <span class="mono">FlowRun</span> 对象需要额外 API 查询事件；
      Airflow 通过 XCom 取中间值。MAF 把事件列表和便捷方法融为一体——一次 <span class="mono">run()</span> 全部到手。</div></div>
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
  <br>把工作流真正端到端用起来，见<a href="20-capstone.html">第 20 课 · 端到端实战</a>。
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

upper = UpperCase(id=<span class="st">"upper"</span>)
wf = WorkflowBuilder(start_executor=upper) \
    .add_edge(upper, reverse).build()
events = <span class="kw">await</span> wf.run(<span class="st">"hello"</span>)  <span class="cm"># → "OLLEH"</span></pre>
</div>

<h2>Tracing one workflow run: writer → reviewer</h2>
<p>Enough abstraction — let's walk a <strong>two-node graph</strong> end to end. Two Executors — <span class="mono">writer</span> (drafts) and
<span class="mono">reviewer</span> (reviews and yields output) — wired by one edge <span class="mono">writer → reviewer</span>, then we deliver an initial message.
The key insight: a Workflow does <strong>not</strong> "call two functions in sequence" — it advances in <strong>supersteps</strong>,
which is exactly what makes it <strong>resumable, concurrent, and observable</strong> (<span class="mono">_workflow.py:211</span> calls this a Pregel-style engine).</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">build the graph</span></div>
<pre><span class="nb">@executor</span>(id=<span class="st">"writer"</span>)
<span class="kw">async def</span> <span class="fn">writer</span>(topic: str, ctx: WorkflowContext[str]):
    <span class="kw">await</span> ctx.send_message(<span class="st">f"draft: a haiku about {topic}"</span>)   <span class="cm"># forward downstream</span>

<span class="nb">@executor</span>(id=<span class="st">"reviewer"</span>)
<span class="kw">async def</span> <span class="fn">reviewer</span>(draft: str, ctx: WorkflowContext[Never, str]):
    <span class="kw">await</span> ctx.yield_output(draft + <span class="st">" ✓ reviewed"</span>)        <span class="cm"># emit final result</span>

wf = WorkflowBuilder(start_executor=writer).add_edge(writer, reviewer).build()
result = <span class="kw">await</span> wf.run(<span class="st">"the sea"</span>)</pre>
</div>

<div class="vflow">
  <div class="step"><div class="num">0</div><div class="sc"><h4>Deliver the initial message (superstep 0)</h4>
    <p>The engine delivers <span class="mono">"the sea"</span> as a message to the <strong>start executor</strong> <span class="mono">writer</span> and emits a <span class="mono">started</span> event.
    Right now <strong>active nodes: none</strong>; <strong>in-flight message</strong>: <span class="mono">"the sea" → writer</span>.</p></div></div>
  <div class="step"><div class="num">1</div><div class="sc"><h4>Superstep 1: writer is invoked</h4>
    <p>Every node that "received a message" is invoked <strong>in parallel</strong> this superstep. <span class="mono">writer</span>'s handler runs,
    calls <span class="mono">ctx.send_message(draft)</span> to write the draft onto the edge — but it is <strong>not delivered immediately</strong>; it's buffered until the superstep boundary.</p>
<pre class="code"><span class="cm"># events observable this superstep</span>
WorkflowEvent(<span class="st">"executor_invoked"</span>,  executor_id=<span class="st">"writer"</span>)
WorkflowEvent(<span class="st">"executor_completed"</span>, executor_id=<span class="st">"writer"</span>)
<span class="cm"># edge writer→reviewer now buffers one message (not visible in the event stream)</span></pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Superstep boundary: deliver + checkpoint</h4>
    <p>When superstep 1 ends, the engine <strong>delivers</strong> all in-flight messages at once (the draft reaches <span class="mono">reviewer</span>)
    and <strong>writes a checkpoint</strong> (<span class="mono">_runner.py:143</span>). The next superstep's active set = <span class="mono">&#123;reviewer&#125;</span>.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Superstep 2: reviewer is invoked and yields</h4>
    <p><span class="mono">reviewer</span> receives the draft and calls <span class="mono">yield_output()</span> to emit the terminal value — which fires an <span class="mono">output</span> event:</p>
<pre class="code">WorkflowEvent(<span class="st">"executor_invoked"</span>, executor_id=<span class="st">"reviewer"</span>)
WorkflowEvent(<span class="st">"output"</span>, executor_id=<span class="st">"reviewer"</span>,
             data=<span class="st">"draft: a haiku about the sea ✓ reviewed"</span>)
WorkflowEvent(<span class="st">"executor_completed"</span>, executor_id=<span class="st">"reviewer"</span>)</pre></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>No messages in flight → graph idle, terminate</h4>
    <p>At the end of superstep 2 nothing new is in flight, the graph goes <span class="mono">IDLE</span>, and <span class="mono">run()</span> returns.
    <span class="mono">result.get_outputs()</span> → <span class="mono">["…✓ reviewed"]</span>,
    <span class="mono">result.get_final_state()</span> → <span class="mono">WorkflowRunState.IDLE</span>.</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 Reading this trace</div>
  Three things people often miss: ① <strong>nodes pass messages, not return values</strong> — <span class="mono">send_message</span> drops data onto the edge,
  and the receiver isn't invoked until the <em>next</em> superstep; ② <strong>messages are delivered together at the superstep boundary</strong>, so multiple nodes invoked in the same superstep <strong>can't see each other's output</strong> from that step (precisely what makes fan-out safe to parallelize);
  ③ <strong>a checkpoint is written at the end of every superstep</strong> — crash and you resume from the most recent one, something a "single-agent tool loop" cannot offer.
  One more gotcha: messages produced by <span class="mono">send_message</span> are <strong>invisible in the event stream</strong> (<span class="mono">_workflow.py:221</span>);
  all you observe are <span class="mono">output</span> / custom / status events — to watch inter-node data flow you need the OTel <span class="mono">message.send</span> span (see Lesson 14).
</div>

<h2>The graph execution model: superstep-driven</h2>
<p>Abstracting the trace above gives the Workflow mental model: round after round of <strong>supersteps</strong>, each "invoke active nodes → buffer messages → deliver + checkpoint at the boundary," until no message is left to deliver.</p>
<div class="flow">
  <div class="node"><div class="nt">Superstep 0</div><div class="nd">deliver initial msg</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Superstep 1</div><div class="nd">writer · send</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Boundary</div><div class="nd">deliver + checkpoint</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Superstep 2</div><div class="nd">reviewer · yield</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">IDLE</div><div class="nd">no msg → stop</div></div>
</div>
<p>This is a different control structure from the <strong>single-agent tool loop</strong> you saw in Lesson 8. A side-by-side comparison helps you decide "when to reach for a Workflow":</p>
<div class="cols">
  <div class="col"><h4>Single-agent tool loop</h4>
    <p>One <span class="mono">while</span> loop: call the model → run a tool → call the model again… with state living <strong>entirely in one in-memory message list</strong>.
    Simple and low-latency — ideal for "one agent + a few tools" conversational tasks. But it is <strong>lost on crash</strong>, inherently serial,
    and awkward to pause for human review or branch concurrently.</p></div>
  <div class="col"><h4>Workflow graph</h4>
    <p>Explicit <strong>nodes + edges + supersteps</strong>: checkpoint and <strong>resume</strong> at boundaries, fan-out for concurrency,
    hang conditions and switches on edges, and pause to request human input (<span class="mono">ctx.request_info()</span>).
    The cost is you must <strong>draw the flow as a graph</strong> first — in return you get control, observability, and recoverability.</p></div>
</div>

<h2>🔍 Real source: building the graph and the execution hook</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_workflows/_workflow_builder.py</span><span class="ln">add_edge / build (simplified from :228 / :725)</span></div>
<pre class="code"><span class="kw">def</span> <span class="fn">add_edge</span>(self, source: Executor | SupportsAgentRun,
             target: Executor | SupportsAgentRun,
             condition: EdgeCondition | None = <span class="kw">None</span>) -> Self:
    <span class="cm"># register a directed edge; source output type must match target input type</span>
    ...
    <span class="kw">return</span> self                        <span class="cm"># return self → enables chaining</span>

<span class="kw">def</span> <span class="fn">build</span>(self) -> Workflow:
    <span class="cm"># validate: start executor set, edges valid, graph connected, types compatible</span>
    <span class="cm"># any failure raises WorkflowValidationError (at build time, not run time)</span>
    <span class="kw">return</span> Workflow(...)               <span class="cm"># return an immutable Workflow</span></pre>
</div>
<p>Note: the <strong>start executor is a constructor argument</strong> (<span class="mono">WorkflowBuilder(start_executor=writer)</span>, <span class="mono">_workflow_builder.py:89</span>) —
there is no <span class="mono">set_start_executor()</span> method. <span class="mono">build()</span> runs validation at <strong>build time</strong>, so
type mismatches and disconnected graphs are caught before you ever call <span class="mono">run()</span>.</p>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_workflows/_executor.py</span><span class="ln">Executor.execute (simplified from :219)</span></div>
<pre class="code"><span class="kw">async def</span> <span class="fn">execute</span>(self, message, source_executor_ids, state, runner_context, ...):
    <span class="cm"># invoked by the engine — don't call or override it; customize via @handler</span>
    <span class="kw">with</span> create_processing_span(self.id, ...):      <span class="cm"># auto-opens an OTel span (see Lesson 14)</span>
        handler = self._find_handler(message)        <span class="cm"># pick the @handler by message type</span>
        context = self._create_context_for_handler(...)  <span class="cm"># build a WorkflowContext</span>
        <span class="kw">await</span> handler(message, context)              <span class="cm"># the line that does the real work</span></pre>
</div>
<p>This explains "why the two styles are equivalent": whether you write an Executor subclass or use <span class="mono">@executor</span> on a function,
the engine uniformly routes through <span class="mono">execute()</span> → <span class="mono">_find_handler()</span> to find and invoke the matching handler.
<span class="mono">@handler</span> (<span class="mono">_executor.py:530</span>) merely registers a method's input type into <span class="mono">self._handlers</span> for type-based dispatch here.</p>

<h2>Why graph orchestration</h2>
<p>Drawing the flow explicitly as a graph isn't complexity for its own sake — it trades a little upfront cost for three production-grade capabilities:</p>
<table class="t">
  <tr><th>Capability</th><th>What the graph buys you</th><th>Underlying mechanism</th></tr>
  <tr><td><strong>Resumable</strong></td><td>A long flow that crashes midway resumes from the latest superstep — no rerun from scratch</td><td class="mono">superstep checkpoints</td></tr>
  <tr><td><strong>Concurrent</strong></td><td>Independent nodes run in the same superstep; latency drops from sum to max</td><td class="mono">add_fan_out_edges</td></tr>
  <tr><td><strong>Controllable</strong></td><td>Conditional edges/switches make routing explicit instead of buried in some if</td><td class="mono">add_switch_case_edge_group</td></tr>
  <tr><td><strong>Interruptible</strong></td><td>A node can pause and request human input, then continue once answered</td><td class="mono">ctx.request_info()</td></tr>
</table>
<p>Conversely, if your task is just "one agent with a few tools, done in one conversation," the <strong>single-agent loop is simpler</strong> —
don't wrap it in a one-node graph. A Workflow earns its keep in <strong>multi-node collaboration + long flows + reliability requirements</strong>.
The five <strong>orchestration patterns</strong> in the next lesson are, at heart, "Workflows whose common multi-agent topologies are pre-drawn for you."</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Two Executor styles <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<strong>Class-based</strong> (Executor subclass + @handler):
<pre class="code"><span class="kw">class</span> <span class="fn">UpperCase</span>(Executor):
    <span class="nb">@handler</span>
    <span class="kw">async def</span> <span class="fn">to_upper</span>(self, text: str, ctx: WorkflowContext):
        <span class="kw">await</span> ctx.send_message(text.upper())</pre>
<strong>Function-based</strong> (@executor on a standalone function):
<pre class="code"><span class="nb">@executor</span>(id=<span class="st">&quot;reverse&quot;</span>)
<span class="kw">async def</span> <span class="fn">reverse</span>(text: str, ctx: WorkflowContext):
    <span class="kw">await</span> ctx.yield_output(text[::-1])</pre>
The function style auto-wraps into a <span class="mono">FunctionExecutor</span> — functionally identical.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Different scenarios call for different ergonomics: a quick single-purpose node is easiest as a function;
      a complex node with init params, multiple handlers, or inheritance is better as a class.
      Two styles let the framework <strong>serve both prototyping and production code</strong>.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">The <span class="mono">@executor</span> decorator auto-wraps the function into a <span class="mono">FunctionExecutor</span>,
      sharing the same handler registry and message dispatch mechanism as class-based nodes.
      You can <strong>mix both styles in the same graph</strong> — class nodes and function nodes connect via edges freely.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">LangGraph supports only function nodes (no class inheritance);
      Prefect only supports <span class="mono">@task</span> functions. MAF offers both — a more flexible choice.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Advanced Edge patterns <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code"><span class="cm"># 1-to-1</span>
builder.add_edge(node_a, node_b)
<span class="cm"># 1-to-many (fan-out)</span>
builder.add_fan_out_edges(splitter, [worker1, worker2, worker3])
<span class="cm"># many-to-1 (fan-in)</span>
builder.add_fan_in_edges([worker1, worker2, worker3], aggregator)
<span class="cm"># conditional routing (switch-case)</span>
builder.add_switch_case_edge_group(router, [
    Case(target=fast_path, condition=<span class="kw">lambda</span> msg: msg.priority == <span class="st">&quot;high&quot;</span>),
    Default(target=slow_path),
])
<span class="cm"># chain shorthand (equivalent to consecutive add_edge calls)</span>
builder.add_chain([step1, step2, step3])</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Real workflows aren't just linear pipelines — you need parallel map-reduce (fan-out/fan-in),
      conditional routing (switch-case), and more. With only <span class="mono">add_edge</span>, complex graph construction becomes verbose and error-prone.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">WorkflowBuilder</span> provides five edge methods covering all common topologies.
      There's also <span class="mono">add_multi_selection_edge_group</span> (dynamic multi-select) for "pick a subset of targets based on message content."
      All methods return <span class="mono">Self</span> for fluent chaining.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Airflow uses the <span class="mono">&gt;&gt;</span> operator (readable but limited to 1-to-1);
      LangGraph uses dicts for conditional routing. MAF's explicit method names (<span class="mono">add_fan_out_edges</span>) make topology intent immediately clear.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> WorkflowContext API <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code"><span class="nb">@handler</span>
<span class="kw">async def</span> <span class="fn">process</span>(self, msg: str, ctx: WorkflowContext):
    ctx.set_state(<span class="st">&quot;count&quot;</span>, ctx.get_state(<span class="st">&quot;count&quot;</span>, 0) + 1)  <span class="cm"># read/write shared state</span>
    <span class="kw">await</span> ctx.send_message(result, target_id=<span class="st">&quot;next&quot;</span>)  <span class="cm"># forward to next node</span>
    <span class="kw">await</span> ctx.yield_output(final)  <span class="cm"># emit final result</span>
    <span class="kw">await</span> ctx.add_event(WorkflowEvent.status(...))  <span class="cm"># custom event</span></pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a"><span class="mono">WorkflowContext</span> is the <strong>sole communication channel</strong> between a node and the engine.
      Without it, a node can't discover its upstream (<span class="mono">source_executor_ids</span>),
      can't forward data downstream, can't expose results, and can't access cross-node shared state.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">The context provides four core capabilities:
      ① <span class="mono">send_message()</span> forwards data downstream (optionally to a specific <span class="mono">target_id</span>);
      ② <span class="mono">yield_output()</span> emits results to the caller;
      ③ <span class="mono">get_state/set_state</span> reads/writes workflow-level shared state;
      ④ <span class="mono">request_info()</span> requests external input (Human-in-the-Loop).
      Plus <span class="mono">is_streaming()</span> lets a node adapt behavior for streaming mode.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Temporal stores state in workflow-function local variables;
      LangGraph uses a global State dict. MAF chooses an explicit Context object — no function-signature pollution, no global mutable state.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> workflow.run() return value <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code">result: WorkflowRunResult = <span class="kw">await</span> wf.run(<span class="st">&quot;hello&quot;</span>)
outputs = result.get_outputs()          <span class="cm"># [&quot;OLLEH&quot;] — final results</span>
intermediates = result.get_intermediate_outputs()  <span class="cm"># intermediate outputs</span>
state = result.get_final_state()        <span class="cm"># WorkflowRunState.IDLE</span>
<span class="cm"># WorkflowRunResult inherits list[WorkflowEvent] — iterate directly</span>
<span class="kw">for</span> event <span class="kw">in</span> result:
    <span class="fn">print</span>(event.type, event.data)</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">After workflow execution, you may only care about the final output (<span class="mono">get_outputs</span>),
      or you may need to debug the full event trace. <span class="mono">WorkflowRunResult</span> provides both perspectives,
      making "use it" and "debug it" equally convenient.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">WorkflowRunResult</span> extends <span class="mono">list[WorkflowEvent]</span>,
      so you can iterate all events as a list, or use semantic methods:
      <span class="mono">get_outputs()</span> (terminal outputs), <span class="mono">get_intermediate_outputs()</span> (intermediate results),
      <span class="mono">get_request_info_events()</span> (HITL requests), <span class="mono">status_timeline()</span> (state change timeline).</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Prefect returns a <span class="mono">FlowRun</span> object requiring extra API calls for events;
      Airflow uses XCom for intermediate values. MAF folds the event list and convenience methods into one object — a single <span class="mono">run()</span> gives you everything.</div></div>
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
  <br>To put workflows to work end-to-end, see <a href="20-capstone.html">Lesson 20 · Capstone</a>.
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

<h2>追踪一次 Handoff 编排：客服分流</h2>
<p>抽象的"五种模式"先放一放，我们挑最直观的 <strong>Handoff</strong> 端到端走一遍。场景：客服系统有三个 Agent——
<span class="mono">triage</span>（分流）、<span class="mono">billing</span>（计费专家）、<span class="mono">tech</span>（技术专家）。
用户进来先碰到 triage，由 triage 自己判断该转给谁。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">搭建 Handoff 图</span></div>
<pre><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> HandoffBuilder

workflow = (
    HandoffBuilder(participants=[triage, billing, tech])
    .with_start_agent(triage)
    .add_handoff(triage, [billing], description=<span class="st">"账单/扣费问题"</span>)
    .add_handoff(triage, [tech],    description=<span class="st">"技术故障"</span>)
    .build()
)
result = <span class="kw">await</span> workflow.run(<span class="st">"我这个月被重复扣费了两次"</span>)</pre>
</div>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>triage 上场，手里多了两把"交接工具"</h4>
    <p>每个 <span class="mono">add_handoff(triage, [X])</span> 都会让框架<strong>自动给 triage 注册一个工具</strong>
    <span class="mono">handoff_to_&lt;X.id&gt;</span>（<span class="mono">_handoff.py:122</span>）。所以 triage 除了正常回答，还能调
    <span class="mono">handoff_to_billing</span> / <span class="mono">handoff_to_tech</span>。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>triage 判定：这是计费问题</h4>
    <p>模型读到"重复扣费"，决定不自己答，而是<strong>调用交接工具</strong>——形式上就是第 10 课的普通函数调用，只是这个工具的语义是"移交"：</p>
<pre class="code">assistant_msg = Message(<span class="st">"assistant"</span>, [
  Content.from_function_call(name=<span class="st">"handoff_to_billing"</span>, arguments=<span class="st">"{}"</span>)
])</pre></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>框架拦截，发出 handoff_sent 事件</h4>
    <p>框架识别出这是交接工具调用，<strong>不</strong>把它当普通工具执行，而是切换活跃 Agent 并发出事件（<span class="mono">_handoff.py:413</span>）：</p>
<pre class="code">WorkflowEvent(<span class="st">"handoff_sent"</span>,
  data=HandoffSentEvent(source=<span class="st">"triage"</span>, target=<span class="st">"billing"</span>))</pre></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>billing 接手，看到完整对话历史</h4>
    <p>被交接的 <span class="mono">billing</span> 收到的<strong>不是一句转述</strong>，而是<strong>整段对话</strong>（含用户原话"重复扣费"）。
    它据此核对账单、给出处理结果。若还需用户补充信息，可发 <span class="mono">HandoffAgentUserRequest</span>（<span class="mono">_handoff.py:436</span>）等用户回话。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>满足终止条件 → 返回</h4>
    <p>billing 产出答复、且没有进一步交接，工作流终止。<span class="mono">result.get_outputs()</span> 拿到最终回复。
    全程<strong>没有外部调度器</strong>在写 if-else——是 triage 自己"决定"交给谁。</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 读懂这条轨迹</div>
  Handoff 的精髓是<strong>把"路由决策"交给 Agent 自己</strong>，而实现手段是一次<strong>普通的工具调用</strong>：
  框架把"可交接给谁"编译成若干 <span class="mono">handoff_to_*</span> 工具塞进当前 Agent，Agent 调哪个工具就交给谁。
  这带来两个常被忽视的好处：① 路由理由<strong>写在工具描述里</strong>（"账单/扣费问题"），模型据此选择，决策可解释；
  ② 因为底层是 Workflow 图，交接过程<strong>天然可检查点、可恢复</strong>——这是 OpenAI Swarm 那种"靠函数返回值交接"给不了的。
  还要注意：控制权是<strong>单向</strong>移交的——billing 接手后 triage 即退场（除非你也给 billing 配了交回 triage 的 handoff）。
</div>

<h2>五种模式的拓扑与取舍</h2>
<p>上面只是 Handoff 一种。把五种模式按<strong>拓扑结构</strong>和<strong>"谁决定下一步"</strong>排在一起，选型就清楚了：</p>
<table class="t">
  <tr><th>模式</th><th>拓扑</th><th>谁决定下一步</th><th>典型场景</th></tr>
  <tr><td><strong>Sequential</strong></td><td>A → B → C 链</td><td>固定顺序（建图时定死）</td><td>写作→评审→润色流水线</td></tr>
  <tr><td><strong>Concurrent</strong></td><td>fan-out → fan-in</td><td>全部并行，聚合器收尾</td><td>多视角同时分析、投票</td></tr>
  <tr><td><strong>Handoff</strong></td><td>Agent 间有向交接</td><td><strong>当前 Agent</strong>（调交接工具）</td><td>客服分流、专家路由</td></tr>
  <tr><td><strong>Group Chat</strong></td><td>共享群聊</td><td><strong>selector</strong>（函数/模型）每轮选</td><td>辩论、头脑风暴</td></tr>
  <tr><td><strong>Magentic</strong></td><td>指挥官 + 工人</td><td><strong>manager</strong>（看进度账本）</td><td>调研+编码+测试等复杂任务</td></tr>
</table>
<p>读这张表的钥匙是<strong>第三列"谁决定下一步"</strong>——它决定了控制权落在哪儿。
Sequential / Concurrent 把顺序<strong>写死在图里</strong>（最可预测，建图时就定了）；
Handoff 把决策权交给<strong>当前 Agent</strong>（最灵活，但下一步取决于模型当下的判断，最难预测）；
Group Chat 用一个集中的 <span class="mono">selection_func</span>（<span class="mono">_group_chat.py:615</span>）每轮挑发言人，把"谁说话"从各 Agent 手里收回到一个选择器；
Magentic 则由 manager 看账本统一调度。一条规律：<strong>越往下，自治程度越高、可预测性越低</strong>——按你对"可控 vs 灵活"的偏好来选。
另一条正交的轴是<strong>延迟</strong>：只有 Concurrent 是真并行，它把总耗时从"各 Agent 之和"压到"各 Agent 之最大"，其余四种本质上是串行推进的。</p>
<div class="flow">
  <div class="node hl"><div class="nt">triage</div><div class="nd">分流 Agent</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">handoff_to_billing</div><div class="nd">调交接工具</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">billing</div><div class="nd">接手 + 完整历史</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">output</div><div class="nd">退款已处理</div></div>
</div>

<h2>🔍 真实源码：Handoff 的入口与交接</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">orchestrations/_handoff.py</span><span class="ln">链式构造 + 自动交接工具（简化自 :122 / :711 / :929）</span></div>
<pre class="code"><span class="kw">def</span> <span class="fn">get_handoff_tool_name</span>(target_id: str) -> str:
    <span class="kw">return</span> <span class="st">f"handoff_to_{target_id}"</span>           <span class="cm"># 交接工具的命名约定</span>

<span class="kw">class</span> <span class="fn">HandoffBuilder</span>:
    <span class="kw">def</span> <span class="fn">add_handoff</span>(self, source: Agent, targets: Sequence[Agent],
                    *, description: str | None = <span class="kw">None</span>) -> <span class="st">"HandoffBuilder"</span>:
        <span class="cm"># 登记一条交接路径；description 会变成交接工具的说明，供模型判断</span>
        ...
        <span class="kw">return</span> self                           <span class="cm"># 链式</span>

    <span class="kw">def</span> <span class="fn">build</span>(self) -> Workflow:
        <span class="cm"># 给每个 source 注册 handoff_to_* 工具，再连成一张 Workflow 图</span>
        ...</pre>
</div>
<p>看清楚了：编排器并不是另起炉灶的新机制，而是<strong>把多 Agent 拓扑编译成上一课的 Workflow 图</strong>。
正因如此，编排同样白拿 Workflow 的检查点、流式事件与 OTel 追踪。</p>

<h2>进阶：Magentic 的"计划→复核→执行"循环</h2>
<p>Handoff 是 Agent 之间的平级交接；当任务复杂到需要<strong>全局规划</strong>（如"调研 → 写代码 → 跑测试"），就轮到 Magentic。
它有一个 <span class="mono">StandardMagenticManager</span> 当指挥官，每一轮用一张<strong>进度账本</strong>
（<span class="mono">MagenticProgressLedger</span>，<span class="mono">_magentic.py:307</span>）评估五件事，再决定下一步：</p>
<table class="t">
  <tr><th>账本字段</th><th>指挥官在问</th><th>据此做什么</th></tr>
  <tr><td class="mono">is_request_satisfied</td><td>任务完成了吗？</td><td>是 → 收尾输出</td></tr>
  <tr><td class="mono">is_in_loop</td><td>是不是在原地打转？</td><td>是 → 重置计划</td></tr>
  <tr><td class="mono">is_progress_being_made</td><td>这一轮有进展吗？</td><td>否 → stall 计数 +1</td></tr>
  <tr><td class="mono">next_speaker</td><td>下一个该谁干？</td><td>选中对应工人 Agent</td></tr>
  <tr><td class="mono">instruction_or_question</td><td>给他什么指令？</td><td>下发子任务</td></tr>
</table>
<p>这张账本正是 Magentic 不会沦为"放养式群聊"的原因：每轮都<strong>显式自检</strong>是否完成、是否打转、是否有进展。
卡住次数超过 <span class="mono">max_stall_count</span>（<span class="mono">_magentic.py:540</span>，默认 3）就触发计划重置；
轮数超过 <span class="mono">max_round_count</span> 则强制收尾，避免无限烧 token。
你还能开 <span class="mono">enable_plan_review=True</span>（<span class="mono">_magentic.py:1418</span>），让人在<strong>计划阶段</strong>就介入审核——
指挥官会发出 <span class="mono">MagenticPlanReviewRequest</span> 等你批准或改写，再开始执行。这就是"复核"这一环的落点。</p>

<div class="card detail"><h4>🔬 账本从哪来</h4>
<p>这张账本不是代码写死的规则，而是指挥官每轮让 LLM 以<strong>结构化输出</strong>填的一张表
（提示模板见 <span class="mono">_magentic.py:220</span>）：模型读完当前对话与计划，回答"完成了吗 / 在打转吗 / 有进展吗 / 下一个谁 / 给什么指令"。
所以 Magentic 的"自检"本质是<strong>用一次 LLM 调用做调度决策</strong>——这也是它比固定拓扑更贵、却更能应对开放式任务的原因。</p></div>

<h2>为什么要把协作固化成模式</h2>
<p>这些拓扑你都能用 <span class="mono">WorkflowBuilder</span> 手画。那为什么还要五个 Builder？因为<strong>常见多 Agent 协作就那么几种形状</strong>，
每次手搭既啰嗦又容易接错边。Builder 把"意图"一句话说清，正确的图由框架生成：</p>
<table class="t">
  <tr><th>你想表达</th><th>手搭图的负担</th><th>Builder 一行</th></tr>
  <tr><td>顺序流水线</td><td>逐条 add_edge + 终止判断</td><td class="mono">SequentialBuilder(participants=[...])</td></tr>
  <tr><td>并行 + 聚合</td><td>fan-out/fan-in + 写聚合器</td><td class="mono">ConcurrentBuilder(...).with_aggregator(...)</td></tr>
  <tr><td>Agent 自主路由</td><td>手动给每个 Agent 注册交接工具</td><td class="mono">HandoffBuilder(...).add_handoff(...)</td></tr>
</table>
<p>取舍很清晰：<strong>能用模式就用模式</strong>（少写、少错、可读）；当你的拓扑不在这五种里——比如带复杂条件分支的混合流程——
再<strong>退回 <span class="mono">WorkflowBuilder</span> 手画</strong>。模式是糖，不是牢笼。</p>

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

<details class="accordion">
  <summary><span class="badge-num">2</span> SequentialBuilder 深入 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code">workflow = SequentialBuilder(
    participants=[writer, reviewer, editor],
    intermediate_output_from=<span class="st">&quot;all&quot;</span>,  <span class="cm"># 每个参与者的输出都作为中间结果</span>
    output_from=[reviewer],  <span class="cm"># 只有 reviewer 的输出算最终结果</span>
).build()
result = <span class="kw">await</span> workflow.run(<span class="st">&quot;Write a poem&quot;</span>)
<span class="cm"># result.get_intermediate_outputs() 包含所有人的中间输出</span>
<span class="cm"># result.get_outputs() 只包含 reviewer 的输出</span></pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">在多步链中，你可能只关心最终结果，也可能需要看到每一步的中间输出来做质量检查。
      <span class="mono">intermediate_output_from</span> 和 <span class="mono">output_from</span> 让你<strong>精确控制哪些输出可见</strong>。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">SequentialBuilder</span> 接受 <span class="mono">participants</span>（有序列表）、
      <span class="mono">output_from</span>（终端输出来源）和 <span class="mono">intermediate_output_from</span>（中间输出来源）。
      还支持 <span class="mono">chain_only_agent_responses=True</span> 让后一个 Agent 只看到前一个的 AgentResponse，而非整个对话历史。
      可通过 <span class="mono">with_request_info()</span> 启用 Human-in-the-Loop。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">LangChain 的 <span class="mono">SequentialChain</span> 只传最终输出；
      CrewAI 的 <span class="mono">Process.sequential</span> 自动传全部上下文。
      MAF 让你<strong>自选粒度</strong>——是传完整历史还是只传 AgentResponse。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> ConcurrentBuilder 深入 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code"><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> ConcurrentBuilder

workflow = ConcurrentBuilder(
    participants=[analyst_a, analyst_b, analyst_c],
).with_aggregator(
    <span class="kw">lambda</span> responses: <span class="st">&quot;\n---\n&quot;</span>.join(r.text <span class="kw">for</span> r <span class="kw">in</span> responses)
).build()
result = <span class="kw">await</span> workflow.run(<span class="st">&quot;Analyze Q3 revenue&quot;</span>)</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">很多任务天然可并行：让三个分析师同时分析不同维度，最后汇总。
      串行执行浪费时间——Concurrent 模式将延迟从 <em>sum(各Agent时间)</em> 降到 <em>max(各Agent时间)</em>。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">ConcurrentBuilder</span> 将所有 <span class="mono">participants</span> fan-out 并行执行，
      然后在 fan-in 节点用<strong>聚合器</strong>合并结果。默认聚合器拼接所有输出；
      你也可以用 <span class="mono">with_aggregator()</span> 传入自定义 Executor 或 lambda 做 map-reduce 风格的汇总。
      同样支持 <span class="mono">output_from</span>、<span class="mono">intermediate_output_from</span> 和 <span class="mono">with_request_info()</span>。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">LangGraph 需要手动构建 fan-out/fan-in 图；
      AutoGen 没有内置并行模式。MAF 的 <span class="mono">ConcurrentBuilder</span> 一行声明并行 + 一行声明聚合器，极其简洁。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> HandoffBuilder 深入 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code"><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> HandoffBuilder

workflow = (
    HandoffBuilder(participants=[
        triage_agent,   <span class="cm"># 入口 Agent</span>
        billing_agent,  <span class="cm"># 计费专家</span>
        tech_agent,     <span class="cm"># 技术专家</span>
    ])
    .with_start_agent(triage_agent)
    .add_handoff(triage_agent, [billing_agent], description=<span class="st">&quot;billing issues&quot;</span>)
    .add_handoff(triage_agent, [tech_agent], description=<span class="st">&quot;technical problems&quot;</span>)
    .build()
)</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">在客服/专家路由场景中，当前 Agent 判断"这个问题我不擅长"后需要<strong>显式交接</strong>给另一个 Agent。
      Handoff 模式让 Agent 自己决定交接时机和目标，而不是由外部调度器硬编码路由规则。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">每个 <span class="mono">.add_handoff(source, [target], description=...)</span> 声明一条带描述的交接路径。
      框架会自动给当前 Agent 注入一个"交接工具"——Agent 调用该工具即触发切换。
      被交接的 Agent 会收到完整对话历史。如果 Agent 想让用户提供额外信息，可以发出 <span class="mono">HandoffAgentUserRequest</span>。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">OpenAI Swarm 也有 handoff 概念，但通过函数返回值实现，不支持异步和持久化。
      AutoGen 的 <span class="mono">SwarmAgent</span> 类似但 API 更复杂。
      MAF 的 Handoff 基于 Workflow 引擎——天然支持检查点和恢复。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> MagenticBuilder 深入 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code"><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> MagenticBuilder

workflow = MagenticBuilder(
    participants=[coder, web_surfer, file_surfer],
    manager_agent=orchestrator_llm,  <span class="cm"># 用 LLM 当指挥官</span>
    enable_plan_review=<span class="kw">True</span>,        <span class="cm"># 计划需人工审核</span>
    max_round_count=10,
).build()</pre>
指挥官会生成 <span class="mono">MagenticProgressLedger</span>，跟踪五个维度：
<span class="mono">is_request_satisfied</span> / <span class="mono">is_in_loop</span> / <span class="mono">is_progress_being_made</span> /
<span class="mono">next_speaker</span> / <span class="mono">instruction_or_question</span>。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">复杂任务（如"调研+编码+测试"）需要一个<strong>全局规划者</strong>分解子任务并分配给最合适的 Agent。
      没有指挥官，Agent 之间会陷入无方向的对话循环。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">MagenticBuilder 实现了 <strong>Plan → Review → Execute</strong> 循环：
      ① <span class="mono">StandardMagenticManager</span>（指挥官）用 task ledger 维护事实和计划；
      ② 每轮通过 <span class="mono">MagenticProgressLedger</span> 评估进展，选出 <span class="mono">next_speaker</span>；
      ③ 检测到卡住（<span class="mono">is_in_loop</span>）会自动重置计划。
      支持 <span class="mono">enable_plan_review=True</span> 让人工在计划阶段介入审核。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">AutoGen 的 MagenticOne 是该模式的原型；CrewAI 的 hierarchical process 类似但无 ProgressLedger 反馈机制。
      MAF 的实现加入了<strong>卡住检测和自动重置</strong>，更适合长时间运行的复杂任务。</div></div>
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
  <br>这些编排模式如何组成一个完整应用，见<a href="20-capstone.html">第 20 课 · 端到端实战</a>。
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

<h2>Tracing one Handoff orchestration: support triage</h2>
<p>Let's set the abstract "five patterns" aside and walk the most intuitive one — <strong>Handoff</strong> — end to end. Scenario: a support system has three Agents:
<span class="mono">triage</span> (routing), <span class="mono">billing</span> (billing expert), and <span class="mono">tech</span> (technical expert).
A user always hits triage first, and triage itself decides who to hand off to.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">build the Handoff graph</span></div>
<pre><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> HandoffBuilder

workflow = (
    HandoffBuilder(participants=[triage, billing, tech])
    .with_start_agent(triage)
    .add_handoff(triage, [billing], description=<span class="st">"billing / charge issues"</span>)
    .add_handoff(triage, [tech],    description=<span class="st">"technical failures"</span>)
    .build()
)
result = <span class="kw">await</span> workflow.run(<span class="st">"I was double-charged twice this month"</span>)</pre>
</div>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>triage enters with two new "handoff tools"</h4>
    <p>Each <span class="mono">add_handoff(triage, [X])</span> makes the framework <strong>auto-register a tool</strong>
    <span class="mono">handoff_to_&lt;X.id&gt;</span> on triage (<span class="mono">_handoff.py:122</span>). So besides answering normally, triage can call
    <span class="mono">handoff_to_billing</span> / <span class="mono">handoff_to_tech</span>.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>triage decides: this is a billing issue</h4>
    <p>Reading "double-charged," the model chooses not to answer itself but to <strong>call a handoff tool</strong> — mechanically the same ordinary function call from Lesson 10, except this tool's semantics are "hand off":</p>
<pre class="code">assistant_msg = Message(<span class="st">"assistant"</span>, [
  Content.from_function_call(name=<span class="st">"handoff_to_billing"</span>, arguments=<span class="st">"{}"</span>)
])</pre></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>The framework intercepts and emits handoff_sent</h4>
    <p>Recognizing a handoff-tool call, the framework does <strong>not</strong> run it as a normal tool; it switches the active Agent and emits an event (<span class="mono">_handoff.py:413</span>):</p>
<pre class="code">WorkflowEvent(<span class="st">"handoff_sent"</span>,
  data=HandoffSentEvent(source=<span class="st">"triage"</span>, target=<span class="st">"billing"</span>))</pre></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>billing takes over with the full conversation history</h4>
    <p>The handed-to <span class="mono">billing</span> receives <strong>not a one-line summary</strong> but the <strong>entire conversation</strong> (including the user's own "double-charged").
    It reconciles the bill and resolves it. If it needs more from the user, it can emit a <span class="mono">HandoffAgentUserRequest</span> (<span class="mono">_handoff.py:436</span>) and wait for a reply.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Termination condition met → return</h4>
    <p>billing produces a reply with no further handoff, so the workflow terminates. <span class="mono">result.get_outputs()</span> holds the final answer.
    Throughout, <strong>no external dispatcher</strong> wrote any if/else — triage itself "decided" whom to hand off to.</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 Reading this trace</div>
  Handoff's essence is <strong>delegating the "routing decision" to the Agent itself</strong>, implemented as an <strong>ordinary tool call</strong>:
  the framework compiles "who you may hand off to" into a set of <span class="mono">handoff_to_*</span> tools on the current Agent — whichever tool it calls is who gets the task.
  Two often-missed benefits: ① the routing rationale <strong>lives in the tool description</strong> ("billing / charge issues"), the model selects accordingly, and the decision is explainable;
  ② because the substrate is a Workflow graph, the handoff is <strong>naturally checkpointable and resumable</strong> — something OpenAI Swarm's "hand off via function return value" cannot offer.
  Also note: control transfers <strong>one-way</strong> — once billing takes over, triage steps off the stage (unless you also gave billing a handoff back to triage).
</div>

<h2>The five patterns: topology and tradeoffs</h2>
<p>That was just Handoff. Lining up all five by <strong>topology</strong> and <strong>"who decides the next step"</strong> makes selection obvious:</p>
<table class="t">
  <tr><th>Pattern</th><th>Topology</th><th>Who decides next</th><th>Typical scenario</th></tr>
  <tr><td><strong>Sequential</strong></td><td>A → B → C chain</td><td>Fixed order (pinned at build time)</td><td>write→review→polish pipeline</td></tr>
  <tr><td><strong>Concurrent</strong></td><td>fan-out → fan-in</td><td>All in parallel, aggregator finishes</td><td>multi-angle analysis, voting</td></tr>
  <tr><td><strong>Handoff</strong></td><td>directed agent handoff</td><td><strong>current Agent</strong> (calls a handoff tool)</td><td>support triage, expert routing</td></tr>
  <tr><td><strong>Group Chat</strong></td><td>shared chat</td><td><strong>selector</strong> (function/model) each turn</td><td>debate, brainstorming</td></tr>
  <tr><td><strong>Magentic</strong></td><td>manager + workers</td><td><strong>manager</strong> (reads a progress ledger)</td><td>research+code+test complex tasks</td></tr>
</table>
<p>The key to reading this table is the <strong>third column, "who decides next"</strong> — it determines where control sits.
Sequential / Concurrent <strong>pin the order into the graph</strong> (most predictable, fixed at build time);
Handoff hands the decision to the <strong>current Agent</strong> (most flexible, but the next step depends on the model's in-the-moment judgment — least predictable);
Group Chat uses a centralized <span class="mono">selection_func</span> (<span class="mono">_group_chat.py:615</span>) to pick a speaker each turn, pulling "who talks" out of the Agents' hands and into one selector;
Magentic lets a manager schedule via its ledger. One rule of thumb: <strong>the further down, the more autonomy and the less predictability</strong> — choose by your preference for "control vs flexibility."
An orthogonal axis is <strong>latency</strong>: only Concurrent is truly parallel, collapsing total time from "sum of agents" to "max of agents"; the other four advance serially at heart.</p>
<div class="flow">
  <div class="node hl"><div class="nt">triage</div><div class="nd">routing agent</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">handoff_to_billing</div><div class="nd">calls handoff tool</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">billing</div><div class="nd">takes over + full history</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">output</div><div class="nd">refund handled</div></div>
</div>

<h2>🔍 Real source: Handoff's entry and the handoff itself</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">orchestrations/_handoff.py</span><span class="ln">chained build + auto handoff tools (simplified from :122 / :711 / :929)</span></div>
<pre class="code"><span class="kw">def</span> <span class="fn">get_handoff_tool_name</span>(target_id: str) -> str:
    <span class="kw">return</span> <span class="st">f"handoff_to_{target_id}"</span>           <span class="cm"># handoff-tool naming convention</span>

<span class="kw">class</span> <span class="fn">HandoffBuilder</span>:
    <span class="kw">def</span> <span class="fn">add_handoff</span>(self, source: Agent, targets: Sequence[Agent],
                    *, description: str | None = <span class="kw">None</span>) -> <span class="st">"HandoffBuilder"</span>:
        <span class="cm"># register one handoff path; description becomes the tool's doc for the model</span>
        ...
        <span class="kw">return</span> self                           <span class="cm"># chainable</span>

    <span class="kw">def</span> <span class="fn">build</span>(self) -> Workflow:
        <span class="cm"># register a handoff_to_* tool per source, then wire a Workflow graph</span>
        ...</pre>
</div>
<p>The takeaway: orchestrators aren't a brand-new mechanism — they <strong>compile a multi-agent topology into the Workflow graph from the previous lesson</strong>.
That's exactly why orchestration inherits Workflow's checkpoints, streaming events, and OTel tracing for free.</p>

<h2>Going deeper: Magentic's "plan → review → execute" loop</h2>
<p>Handoff is a peer-to-peer transfer between Agents; when a task is complex enough to need <strong>global planning</strong> (e.g. "research → write code → run tests"), Magentic takes over.
It uses a <span class="mono">StandardMagenticManager</span> as conductor, and each round evaluates five things via a <strong>progress ledger</strong>
(<span class="mono">MagenticProgressLedger</span>, <span class="mono">_magentic.py:307</span>) before deciding the next step:</p>
<table class="t">
  <tr><th>Ledger field</th><th>What the conductor asks</th><th>What it does next</th></tr>
  <tr><td class="mono">is_request_satisfied</td><td>Is the task done?</td><td>Yes → finalize output</td></tr>
  <tr><td class="mono">is_in_loop</td><td>Are we spinning in place?</td><td>Yes → reset the plan</td></tr>
  <tr><td class="mono">is_progress_being_made</td><td>Did this round make progress?</td><td>No → stall count +1</td></tr>
  <tr><td class="mono">next_speaker</td><td>Who should act next?</td><td>pick the right worker Agent</td></tr>
  <tr><td class="mono">instruction_or_question</td><td>What instruction to give?</td><td>dispatch the sub-task</td></tr>
</table>
<p>This ledger is exactly why Magentic doesn't degrade into a "free-for-all group chat": every round it <strong>explicitly self-checks</strong> whether it's done, looping, or making progress.
When stalls exceed <span class="mono">max_stall_count</span> (<span class="mono">_magentic.py:540</span>, default 3) it triggers a plan reset;
when rounds exceed <span class="mono">max_round_count</span> it force-finalizes to avoid burning tokens forever.
You can also set <span class="mono">enable_plan_review=True</span> (<span class="mono">_magentic.py:1418</span>) to insert a human at the <strong>planning stage</strong> —
the conductor emits a <span class="mono">MagenticPlanReviewRequest</span> and waits for you to approve or revise before executing. That's where the "review" step lands.</p>

<div class="card detail"><h4>🔬 Where the ledger comes from</h4>
<p>This ledger isn't a hard-coded rule set — it's a table the conductor asks the LLM to fill in as <strong>structured output</strong> every round
(prompt template at <span class="mono">_magentic.py:220</span>): the model reads the current conversation and plan, then answers "done? / looping? / progressing? / who's next? / what instruction?".
So Magentic's "self-check" is fundamentally <strong>one LLM call making a scheduling decision</strong> — which is why it costs more than a fixed topology but copes far better with open-ended tasks.</p></div>

<h2>Why crystallize collaboration into patterns</h2>
<p>You could hand-draw all these topologies with <span class="mono">WorkflowBuilder</span>. So why five Builders? Because <strong>common multi-agent collaboration comes in only a handful of shapes</strong>,
and hand-wiring each time is verbose and easy to mis-connect. A Builder states the <strong>intent</strong> in one line, and the framework generates the correct graph:</p>
<table class="t">
  <tr><th>What you mean</th><th>Hand-built graph burden</th><th>One-line Builder</th></tr>
  <tr><td>Sequential pipeline</td><td>add_edge one by one + termination logic</td><td class="mono">SequentialBuilder(participants=[...])</td></tr>
  <tr><td>Parallel + aggregate</td><td>fan-out/fan-in + write an aggregator</td><td class="mono">ConcurrentBuilder(...).with_aggregator(...)</td></tr>
  <tr><td>Agent self-routing</td><td>manually register handoff tools per Agent</td><td class="mono">HandoffBuilder(...).add_handoff(...)</td></tr>
</table>
<p>The tradeoff is clear: <strong>use a pattern when one fits</strong> (less code, fewer mistakes, more readable); when your topology isn't among the five — say a hybrid flow with complex conditional branching —
<strong>drop back to hand-drawing with <span class="mono">WorkflowBuilder</span></strong>. Patterns are sugar, not a cage.</p>

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

<details class="accordion">
  <summary><span class="badge-num">2</span> SequentialBuilder deep dive <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code">workflow = SequentialBuilder(
    participants=[writer, reviewer, editor],
    intermediate_output_from=<span class="st">&quot;all&quot;</span>,  <span class="cm"># every participant's output as intermediate</span>
    output_from=[reviewer],  <span class="cm"># only reviewer's output counts as final</span>
).build()
result = <span class="kw">await</span> workflow.run(<span class="st">&quot;Write a poem&quot;</span>)
<span class="cm"># result.get_intermediate_outputs() — all participants' intermediate output</span>
<span class="cm"># result.get_outputs() — only reviewer's output</span></pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">In a multi-step chain you may only care about the final result, or you may need to inspect each step's
      intermediate output for quality checks. <span class="mono">intermediate_output_from</span> and <span class="mono">output_from</span> give you
      <strong>precise control over which outputs are visible</strong>.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">SequentialBuilder</span> accepts <span class="mono">participants</span> (ordered list),
      <span class="mono">output_from</span> (terminal output sources), and <span class="mono">intermediate_output_from</span> (intermediate output sources).
      It also supports <span class="mono">chain_only_agent_responses=True</span> so the next Agent sees only the previous Agent's response, not the entire conversation.
      Use <span class="mono">with_request_info()</span> to enable Human-in-the-Loop.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">LangChain's <span class="mono">SequentialChain</span> only forwards the final output;
      CrewAI's <span class="mono">Process.sequential</span> auto-forwards all context.
      MAF lets you <strong>choose the granularity</strong> — full history or AgentResponse only.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> ConcurrentBuilder deep dive <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code"><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> ConcurrentBuilder

workflow = ConcurrentBuilder(
    participants=[analyst_a, analyst_b, analyst_c],
).with_aggregator(
    <span class="kw">lambda</span> responses: <span class="st">&quot;\n---\n&quot;</span>.join(r.text <span class="kw">for</span> r <span class="kw">in</span> responses)
).build()
result = <span class="kw">await</span> workflow.run(<span class="st">&quot;Analyze Q3 revenue&quot;</span>)</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Many tasks are inherently parallelizable: have three analysts work on different dimensions simultaneously,
      then merge results. Sequential execution wastes time — Concurrent mode reduces latency from <em>sum(agent times)</em> to <em>max(agent times)</em>.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">ConcurrentBuilder</span> fans out all <span class="mono">participants</span> for parallel execution,
      then fans in at an <strong>aggregator</strong> node to merge results. The default aggregator concatenates all outputs;
      use <span class="mono">with_aggregator()</span> to pass a custom Executor or lambda for map-reduce style summarization.
      Also supports <span class="mono">output_from</span>, <span class="mono">intermediate_output_from</span>, and <span class="mono">with_request_info()</span>.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">LangGraph requires manually building fan-out/fan-in graphs;
      AutoGen has no built-in parallel mode. MAF's <span class="mono">ConcurrentBuilder</span>: one line for parallelism + one line for aggregation — extremely concise.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> HandoffBuilder deep dive <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code"><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> HandoffBuilder

workflow = (
    HandoffBuilder(participants=[
        triage_agent,   <span class="cm"># entry Agent</span>
        billing_agent,  <span class="cm"># billing expert</span>
        tech_agent,     <span class="cm"># tech expert</span>
    ])
    .with_start_agent(triage_agent)
    .add_handoff(triage_agent, [billing_agent], description=<span class="st">&quot;billing issues&quot;</span>)
    .add_handoff(triage_agent, [tech_agent], description=<span class="st">&quot;technical problems&quot;</span>)
    .build()
)</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">In customer-service / expert-routing scenarios, the current Agent judges "this isn't my expertise" and needs
      to <strong>explicitly hand off</strong> to another Agent. Handoff mode lets the Agent itself decide when and to whom — rather than an external scheduler hard-coding routing rules.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">Each <span class="mono">.add_handoff(source, [target], description=...)</span> declares a handoff path with its own description.
      The framework auto-injects a "handoff tool" into the current Agent — calling that tool triggers the switch.
      The receiving Agent gets the full conversation history. If an Agent needs additional user info, it can emit a <span class="mono">HandoffAgentUserRequest</span>.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">OpenAI Swarm has a handoff concept too, but via function return values without async or persistence support.
      AutoGen's <span class="mono">SwarmAgent</span> is similar but has a more complex API.
      MAF's Handoff is Workflow-engine-based — natively supports checkpointing and resumption.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> MagenticBuilder deep dive <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code"><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> MagenticBuilder

workflow = MagenticBuilder(
    participants=[coder, web_surfer, file_surfer],
    manager_agent=orchestrator_llm,  <span class="cm"># LLM as conductor</span>
    enable_plan_review=<span class="kw">True</span>,        <span class="cm"># plan requires human review</span>
    max_round_count=10,
).build()</pre>
The conductor generates a <span class="mono">MagenticProgressLedger</span> tracking five dimensions:
<span class="mono">is_request_satisfied</span> / <span class="mono">is_in_loop</span> / <span class="mono">is_progress_being_made</span> /
<span class="mono">next_speaker</span> / <span class="mono">instruction_or_question</span>.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Complex tasks (e.g., "research + code + test") need a <strong>global planner</strong> to decompose sub-tasks and assign
      them to the best Agent. Without a conductor, agents fall into directionless conversation loops.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">MagenticBuilder implements a <strong>Plan → Review → Execute</strong> cycle:
      ① <span class="mono">StandardMagenticManager</span> (conductor) maintains facts and plans via a task ledger;
      ② Each round, a <span class="mono">MagenticProgressLedger</span> evaluates progress and picks <span class="mono">next_speaker</span>;
      ③ If a stall is detected (<span class="mono">is_in_loop</span>), the plan auto-resets.
      Supports <span class="mono">enable_plan_review=True</span> for human review at the planning stage.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">AutoGen's MagenticOne is the prototype of this pattern; CrewAI's hierarchical process is similar but lacks the ProgressLedger feedback mechanism.
      MAF's implementation adds <strong>stall detection and auto-reset</strong>, better suited for long-running complex tasks.</div></div>
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
  <br>See how these patterns compose into a full app in <a href="20-capstone.html">Lesson 20 · Capstone</a>.
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

<h2>追踪一次流式输出 + 它背后的 span 树</h2>
<p>把"流式"和"可观测"放进同一次真实调用看：用户问"巴黎天气如何？"，Agent 需要调一个 <span class="mono">get_weather</span> 工具。
下面同时跟两条线——<strong>左脑记你 <code>async for</code> 收到的 chunk</strong>，<strong>右脑记 OTel 在后台挂的 span</strong>。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>开 invoke_agent 根 span，进入流式</h4>
    <p>调用 <span class="mono">agent.run("巴黎天气如何？", stream=True)</span>。框架立刻开一个名为
      <span class="mono">invoke_agent {agent}</span> 的根 span（<span class="mono">AGENT_INVOKE_OPERATION="invoke_agent"</span>，<span class="mono">observability.py:294</span>），并返回一个异步迭代器。此刻还没有任何 token。</p>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>模型先决定调工具——首批 chunk 是 tool_calls，不是文本</h4>
    <p>子 span <span class="mono">chat {model}</span> 开启。第一批 chunk 的 <span class="mono">.text</span> 为空，
      <span class="mono">.contents</span> 里是一个 <span class="mono">FunctionCallContent</span>，<span class="mono">.finish_reason</span> 最终为 <span class="mono">&quot;tool_calls&quot;</span>：</p>
<pre class="code">AgentResponseUpdate(contents=[FunctionCallContent(
    name=&quot;get_weather&quot;, arguments={&quot;city&quot;: &quot;Paris&quot;})],
    text=&quot;&quot;, finish_reason=&quot;tool_calls&quot;)</pre>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>执行工具——再开一个子 span</h4>
    <p>框架开 <span class="mono">execute_tool {name}</span> span（<span class="mono">TOOL_EXECUTION_OPERATION="execute_tool"</span>，<span class="mono">observability.py:291</span>），
      属性带 <span class="mono">gen_ai.tool.name=get_weather</span> 和 <span class="mono">gen_ai.tool.call.id</span>。工具返回 "15°C，晴"。这一步<strong>不产生面向用户的 text chunk</strong>。</p>
  </div></div>
  <div class="step"><div class="num">4</div><div class="sc">
    <h4>带工具结果再问模型——这次是真正的文本增量</h4>
    <p>第二个 <span class="mono">chat {model}</span> span 开启。现在 chunk 真的带文本了，一个一个往外吐：</p>
<pre class="code">&quot;巴&quot; → &quot;黎&quot; → &quot;现在&quot; → &quot;15&quot; → &quot;°C&quot; → &quot;，晴&quot; ...
# 每个 chunk：text=增量片段，finish_reason=None</pre>
  </div></div>
  <div class="step"><div class="num">5</div><div class="sc">
    <h4>收尾：finish_reason 翻成 "stop"，span 依次关闭</h4>
    <p>最后一个 chunk 的 <span class="mono">.finish_reason</span> 从 <span class="mono">None</span> 变成 <span class="mono">&quot;stop&quot;</span>。
      把每个 chunk 的 <span class="mono">.text</span> 拼起来即得完整答复；与此同时
      <span class="mono">invoke_agent → chat → execute_tool → chat</span> 这串 span 依次关闭，每个都记下了耗时与 token 数。</p>
  </div></div>
</div>

<p>所以一次流式回答的 chunk 节奏常常是"先静默、再爆发"：</p>
<div class="flow">
  <div class="node"><div class="nt">chunk #1</div><div class="nd">text=&quot;&quot; · tool_calls</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">[执行工具]</div><div class="nd">无 text chunk</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">chunk #2..n</div><div class="nd">text 增量 · None</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">chunk #末</div><div class="nd">finish=&quot;stop&quot;</div></div>
</div>
<p>这解释了一个常见困惑：开了流式却<strong>前几秒没字</strong>——那不是卡住，而是模型正在走"决定调工具 → 等工具返回"这段，期间的 chunk 不带可显示文本。理解这一点，你的 UI 才能在工具阶段显示"思考中…"而不是干等。</p>

<div class="card detail"><h4>🔬 两条线为什么能对齐</h4>
<p>流式给的是<strong>面向用户的时间维度</strong>（什么时候有字可以显示），OTel 给的是<strong>面向运维的因果维度</strong>（这次 run 里发生了哪些操作、各花多久）。
同一次 <span class="mono">run()</span> 同时产出二者：chunk 让 UI 即时刷新，span 让你事后回看"那次为啥慢——是慢在第二次 <span class="mono">chat</span> 还是 <span class="mono">execute_tool</span>"。两者读的是同一过程的不同投影。</p></div>

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

<details class="accordion">
  <summary><span class="badge-num">2</span> AgentResponseUpdate 结构 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code"><span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">&quot;Tell me a joke&quot;</span>, stream=<span class="kw">True</span>):
    <span class="fn">print</span>(chunk.text, end=<span class="st">&quot;&quot;</span>)       <span class="cm"># 增量文本</span>
    <span class="fn">print</span>(chunk.contents)            <span class="cm"># [TextContent(...)]</span>
    <span class="fn">print</span>(chunk.finish_reason)       <span class="cm"># None → ... → &quot;stop&quot;</span>
    <span class="fn">print</span>(chunk.author_name)         <span class="cm"># 多Agent时标识是谁说的</span></pre>
最后一个 chunk 的 <span class="mono">finish_reason</span> 为 <span class="mono">&quot;stop&quot;</span>，表示生成完毕。
把所有 chunk 的 <span class="mono">.text</span> 拼起来就是完整的 <span class="mono">AgentResponse</span>。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">流式场景中，你需要知道每个 chunk 包含什么、何时结束、谁在说话。
      理解 <span class="mono">AgentResponseUpdate</span> 的字段才能正确地构建 UI 流式渲染。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">AgentResponseUpdate</span> 包含：
      <span class="mono">.contents</span>（Content 列表，可含 TextContent / 图片 / 工具调用）、
      <span class="mono">.text</span>（所有 TextContent 拼接的纯文本快捷属性）、
      <span class="mono">.finish_reason</span>（&quot;stop&quot; / &quot;length&quot; / &quot;tool_calls&quot;）、
      <span class="mono">.author_name</span> / <span class="mono">.agent_id</span>（多 Agent 场景标识来源）。
      结构与非流式的 <span class="mono">AgentResponse</span> 对齐，切换模式时代码改动最小。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">OpenAI SDK 返回 <span class="mono">ChatCompletionChunk</span>（仅文本 delta）；
      LangChain 返回 <span class="mono">AIMessageChunk</span>。MAF 的 chunk 带有 <span class="mono">agent_id</span> 和 <span class="mono">author_name</span>，
      天然适合<strong>多 Agent 流式场景</strong>。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Workflow 的流式 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code"><span class="kw">async for</span> event <span class="kw">in</span> wf.run(<span class="st">&quot;hello&quot;</span>, stream=<span class="kw">True</span>):
    <span class="kw">if</span> event.type == <span class="st">&quot;output&quot;</span>:
        <span class="fn">print</span>(<span class="st">&quot;Final:&quot;</span>, event.data)
    <span class="kw">elif</span> event.type == <span class="st">&quot;intermediate&quot;</span>:
        <span class="fn">print</span>(<span class="st">&quot;Step:&quot;</span>, event.data)
    <span class="kw">elif</span> event.type == <span class="st">&quot;executor_invoked&quot;</span>:
        <span class="fn">print</span>(<span class="st">&quot;Running:&quot;</span>, event.executor_id)</pre>
流式模式下 <span class="mono">run()</span> 返回 <span class="mono">AsyncIterator[WorkflowEvent]</span>，而非 <span class="mono">WorkflowRunResult</span>。</div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">工作流可能包含多个 Agent、运行数分钟。用户不能干等到整个图跑完——
      流式事件让前端<strong>实时展示进度</strong>：哪个节点在跑、中间结果是什么、最终输出何时到。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">WorkflowEvent</span> 有丰富的事件类型：
      <span class="mono">started</span> / <span class="mono">executor_invoked</span> / <span class="mono">executor_completed</span>（生命周期）、
      <span class="mono">output</span> / <span class="mono">intermediate</span>（数据）、
      <span class="mono">request_info</span>（HITL 请求）、<span class="mono">failed</span>（错误）。
      每个事件携带 <span class="mono">executor_id</span>、<span class="mono">iteration</span>、<span class="mono">state</span> 等元数据。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">LangGraph 的 streaming 返回纯文本 chunk，无结构化事件；
      Temporal 有事件历史但不支持实时推送。MAF 的 <span class="mono">WorkflowEvent</span> 结构化且类型丰富——
      前端可以据此渲染进度条、节点高亮、错误提示。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> OTel span 层次 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">MAF 自动产生的 span 层次：
<pre class="code">agent.run (parent span)
  ├── chat_client.call  <span class="cm"># 每次 LLM 调用</span>
  │     attrs: input_tokens, output_tokens, model
  ├── tool.execute      <span class="cm"># 每次工具执行</span>
  │     attrs: tool.name, tool.call.id
  └── chat_client.call  <span class="cm"># 工具循环再次调用</span>

workflow.run (parent span)
  ├── executor: upper   <span class="cm"># 每个节点一个子 span</span>
  │     attrs: executor.id, executor.type
  ├── message.send      <span class="cm"># 节点间消息传递</span>
  │     attrs: source_id, target_id
  └── executor: reverse</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">当 Agent 链上某步慢了或报错，你需要知道<strong>具体是哪个 LLM 调用还是哪个工具执行</strong>的问题。
      分层 span 让你在 Jaeger/Grafana 中像看调用栈一样定位瓶颈。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a"><span class="mono">observability.py</span> 定义了 <span class="mono">OtelAttr</span> 枚举，自动填充 GenAI 语义约定属性：
      <span class="mono">gen_ai.agent.id</span>、<span class="mono">gen_ai.usage.input_tokens</span>、<span class="mono">gen_ai.tool.name</span> 等。
      Workflow 层还追踪 <span class="mono">workflow.id</span>、<span class="mono">executor.id</span>、<span class="mono">message.send</span>。
      零额外代码——只需配置 exporter 即可在 Jaeger / Zipkin / OTLP Collector 中查看。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">LangSmith 是 LangChain 的专有追踪方案（厂商锁定）；
      LiteLLM 只追踪 LLM 调用不追踪工具和工作流。MAF 用<strong>标准 OTel</strong>——
      兼容所有 OTel 生态工具，无厂商锁定。</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> 自定义 span / 指标 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a">
<pre class="code"><span class="kw">from</span> agent_framework.observability <span class="kw">import</span> create_workflow_span, OtelAttr

<span class="kw">with</span> create_workflow_span(
    <span class="st">&quot;my_custom_step&quot;</span>,
    attributes={OtelAttr.EXECUTOR_ID: <span class="st">&quot;validator&quot;</span>},
) <span class="kw">as</span> span:
    result = validate(data)
    span.set_attribute(<span class="st">&quot;validation.passed&quot;</span>, result.ok)</pre></div></div>
    <div class="qa"><div class="q">❓ 为什么这件事必要</div><div class="a">框架自动 span 覆盖 LLM 和工具调用，但你的<strong>业务逻辑</strong>（如自定义验证、数据库查询、外部 API 调用）
      也需要被追踪。自定义 span 填补这些盲区。</div></div>
    <div class="qa"><div class="q">✅ MAF 的做法与优点</div><div class="a">MAF 暴露 <span class="mono">create_workflow_span()</span> 作为创建自定义 span 的便捷入口，
      自动挂到当前 trace 上下文中。你也可以直接用 OTel SDK 的 <span class="mono">tracer.start_as_current_span()</span>。
      框架提供的 <span class="mono">OtelAttr</span> 枚举确保属性名与内置 span 一致——查询时可以统一过滤。</div></div>
    <div class="qa"><div class="q">🔀 还有什么其他方案</div><div class="a">有些框架（如 Haystack）不暴露 tracer，只能用日志做追踪；
      LangSmith 需要用其 SDK 的 <span class="mono">@traceable</span> 装饰器。
      MAF 完全拥抱 OTel 标准——你的自定义 span 和框架内置 span 在同一条 trace 中无缝衔接。</div></div>
  </div>
</details>

<h2>真实的 span 树（用框架里的真名字）</h2>
<p>前面手绘的层次是示意；MAF 里 span 的<strong>真实命名规则</strong>是 <span class="mono">f"{operation} {target}"</span>
（<span class="mono">observability.py:2112</span>）。Agent 侧和 Workflow 侧各长一棵树：</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">agent</span><span class="name">invoke_agent {agent}</span></div>
    <div class="ld">根 span，operation = <span class="mono">AGENT_INVOKE_OPERATION</span></div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">child</span><span class="name">chat {model}</span></div>
    <div class="ld">每次 LLM 调用一个，attrs：<span class="mono">gen_ai.usage.input_tokens / output_tokens</span></div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">child</span><span class="name">execute_tool {name}</span></div>
    <div class="ld">每次工具执行一个，attrs：<span class="mono">gen_ai.tool.name / gen_ai.tool.call.id</span></div></div>
</div>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">workflow</span><span class="name">workflow.run</span></div>
    <div class="ld">根 span，attrs：<span class="mono">workflow.id</span></div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">child</span><span class="name">executor.process {id}</span></div>
    <div class="ld">每个节点处理一条消息一个，attrs：<span class="mono">executor.id / executor.type</span></div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">link</span><span class="name">message.send</span></div>
    <div class="ld">节点间消息传递，attrs：<span class="mono">message.source_id / message.target_id</span></div></div>
</div>
<p>一个容易忽视却关键的设计：<span class="mono">executor.process</span> span <strong>不是</strong>嵌套在上游节点之下，而是<strong>用 link 关联</strong>到发布消息的源 span
（<span class="mono">observability.py:2454</span> 注释明确写 "linked (not nested) ... supporting fan-in"）。
为什么？因为 Workflow 是超步并行的：一个节点可能<strong>同时</strong>收到多个上游的消息（fan-in）。
若强行嵌套，它只能挂在某一个父亲下；用 link 则能同时指向多个源，<strong>完整保留扇入的因果关系</strong>。</p>

<h2>🔍 真实源码：手动开一个 span</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span class="path">core/agent_framework/observability.py</span></div>
<pre><span class="cm"># observability.py:2445 — 通用 workflow span</span>
<span class="kw">def</span> <span class="fn">create_workflow_span</span>(
    name: str,
    attributes: Mapping[str, str | int] | <span class="kw">None</span> = <span class="kw">None</span>,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL,
) -> _AgnosticContextManager[trace.Span]:
    <span class="kw">return</span> workflow_tracer().start_as_current_span(name, kind=kind, attributes=attributes)

<span class="cm"># observability.py:2454 — 执行器处理 span，对扇入用 link 而非嵌套</span>
<span class="kw">def</span> <span class="fn">create_processing_span</span>(executor_id, executor_type, message_type, payload_type,
                          source_trace_contexts=<span class="kw">None</span>, source_span_ids=<span class="kw">None</span>):
    links = [trace.Link(...) <span class="kw">for</span> ... <span class="kw">in</span> sources]  <span class="cm"># 多个源 → 多条 link（fan-in）</span>
    <span class="kw">return</span> workflow_tracer().start_as_current_span(
        f<span class="st">&quot;{OtelAttr.EXECUTOR_PROCESS_SPAN} {executor_id}&quot;</span>,  <span class="cm"># &quot;executor.process &lt;id&gt;&quot;</span>
        attributes={OtelAttr.EXECUTOR_ID: executor_id, ...}, links=links)</pre>
</div>
<p>注意 <span class="mono">create_workflow_span</span> 用的是 <span class="mono">start_as_current_span</span>——它把新 span 设为<strong>当前上下文</strong>，
于是你在 <span class="mono">with</span> 块里再开的任何 span（包括框架内置的 <span class="mono">chat</span> / <span class="mono">execute_tool</span>）都会自动成为它的孩子。这就是"零额外代码自动挂树"的底层机制。</p>

<h2>为什么把流式与可观测做成一等公民</h2>
<p>很多框架把这两件事当"事后补"：流式靠你自己拼 SSE，追踪靠你自己埋点。MAF 反过来——
<strong>同一个 <code>run()</code> 调用里，stream 和 span 是同时落地的副产物</strong>。这带来三个实际后果：</p>
<table class="t">
  <tr><th>能力</th><th>没有它会怎样</th><th>MAF 内置之后</th></tr>
  <tr><td>流式</td><td>用户盯着空白等十几秒，以为卡死</td><td>首字延迟即可见，长回答边生成边显示</td></tr>
  <tr><td>分层 span</td><td>"这次 run 为什么要 8 秒？"无从查起</td><td>一眼看出是第二次 <span class="mono">chat</span> 慢，还是某个 tool 慢</td></tr>
  <tr><td>token 归因</td><td>月底账单超支，不知道是哪个 Agent 烧的</td><td>每个 <span class="mono">chat</span> span 都带 input/output_tokens，可按 Agent 聚合</td></tr>
</table>
<p>底层用的是<strong>标准 OpenTelemetry + GenAI 语义约定</strong>（属性名形如 <span class="mono">gen_ai.usage.input_tokens</span>），
所以这些 span 能直接喂给 Jaeger、Grafana Tempo 或任何 OTLP 后端，没有厂商锁定——这正是把可观测做成一等公民、而非专有插件的回报。</p>

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
  <br>想深入到生产级的 trace / metric / log 排查，见<a href="30-observability.html">第 30 课 · 可观测性深入</a>。
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

<h2>Tracing one streaming run + the span tree behind it</h2>
<p>Put "streaming" and "observability" inside one real call: a user asks "What's the weather in Paris?" and the Agent must call a <span class="mono">get_weather</span> tool.
We follow two tracks at once — <strong>your left brain logs the chunks from <code>async for</code></strong>, <strong>your right brain logs the spans OTel attaches in the background</strong>.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>Open the invoke_agent root span, enter streaming</h4>
    <p>Call <span class="mono">agent.run("What's the weather in Paris?", stream=True)</span>. The framework immediately opens a root span named
      <span class="mono">invoke_agent {agent}</span> (<span class="mono">AGENT_INVOKE_OPERATION="invoke_agent"</span>, <span class="mono">observability.py:294</span>) and returns an async iterator. No tokens yet.</p>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>The model decides to call a tool first — early chunks are tool_calls, not text</h4>
    <p>A child span <span class="mono">chat {model}</span> opens. The first chunks have empty <span class="mono">.text</span>;
      <span class="mono">.contents</span> holds a <span class="mono">FunctionCallContent</span>, and <span class="mono">.finish_reason</span> ends as <span class="mono">&quot;tool_calls&quot;</span>:</p>
<pre class="code">AgentResponseUpdate(contents=[FunctionCallContent(
    name=&quot;get_weather&quot;, arguments={&quot;city&quot;: &quot;Paris&quot;})],
    text=&quot;&quot;, finish_reason=&quot;tool_calls&quot;)</pre>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>Execute the tool — another child span</h4>
    <p>The framework opens an <span class="mono">execute_tool {name}</span> span (<span class="mono">TOOL_EXECUTION_OPERATION="execute_tool"</span>, <span class="mono">observability.py:291</span>),
      with attrs <span class="mono">gen_ai.tool.name=get_weather</span> and <span class="mono">gen_ai.tool.call.id</span>. The tool returns "15°C, sunny". This step <strong>emits no user-facing text chunk</strong>.</p>
  </div></div>
  <div class="step"><div class="num">4</div><div class="sc">
    <h4>Ask the model again with the tool result — now real text deltas</h4>
    <p>A second <span class="mono">chat {model}</span> span opens. Now chunks really carry text, token by token:</p>
<pre class="code">&quot;It&quot; → &quot;'s&quot; → &quot; 15&quot; → &quot;°C&quot; → &quot; and&quot; → &quot; sunny&quot; ...
# each chunk: text=delta fragment, finish_reason=None</pre>
  </div></div>
  <div class="step"><div class="num">5</div><div class="sc">
    <h4>Finish: finish_reason flips to "stop", spans close in order</h4>
    <p>The last chunk's <span class="mono">.finish_reason</span> goes from <span class="mono">None</span> to <span class="mono">&quot;stop&quot;</span>.
      Concatenate every chunk's <span class="mono">.text</span> for the full reply; meanwhile the
      <span class="mono">invoke_agent → chat → execute_tool → chat</span> spans close in order, each recording its latency and token counts.</p>
  </div></div>
</div>

<p>So the chunk rhythm of one streaming answer is often "silence first, then a burst":</p>
<div class="flow">
  <div class="node"><div class="nt">chunk #1</div><div class="nd">text=&quot;&quot; · tool_calls</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">[run tool]</div><div class="nd">no text chunk</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">chunk #2..n</div><div class="nd">text delta · None</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">chunk #last</div><div class="nd">finish=&quot;stop&quot;</div></div>
</div>
<p>This explains a common confusion: you enabled streaming yet <strong>see no text for the first few seconds</strong> — that's not a hang, it's the model going through "decide to call a tool → wait for the tool to return", during which chunks carry no displayable text. Knowing this, your UI can show "thinking…" during the tool phase instead of just waiting.</p>

<div class="card detail"><h4>🔬 Why the two tracks line up</h4>
<p>Streaming gives the <strong>user-facing time dimension</strong> (when there's text to display); OTel gives the <strong>ops-facing causal dimension</strong> (which operations happened in this run, and how long each took).
The same <span class="mono">run()</span> produces both: chunks refresh the UI instantly, spans let you look back later and ask "why was that slow — the second <span class="mono">chat</span> or the <span class="mono">execute_tool</span>?". They're two projections of the same process.</p></div>

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

<details class="accordion">
  <summary><span class="badge-num">2</span> AgentResponseUpdate structure <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code"><span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">&quot;Tell me a joke&quot;</span>, stream=<span class="kw">True</span>):
    <span class="fn">print</span>(chunk.text, end=<span class="st">&quot;&quot;</span>)       <span class="cm"># incremental text</span>
    <span class="fn">print</span>(chunk.contents)            <span class="cm"># [TextContent(...)]</span>
    <span class="fn">print</span>(chunk.finish_reason)       <span class="cm"># None → ... → &quot;stop&quot;</span>
    <span class="fn">print</span>(chunk.author_name)         <span class="cm"># identifies speaker in multi-agent</span></pre>
The last chunk's <span class="mono">finish_reason</span> is <span class="mono">&quot;stop&quot;</span>, signaling generation is complete.
Concatenate all chunks' <span class="mono">.text</span> to reconstruct the full <span class="mono">AgentResponse</span>.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">In streaming scenarios you need to know what each chunk contains, when generation ends, and who is speaking.
      Understanding <span class="mono">AgentResponseUpdate</span> fields is essential for building correct streaming UI rendering.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">AgentResponseUpdate</span> contains:
      <span class="mono">.contents</span> (Content list — may include TextContent / images / tool calls),
      <span class="mono">.text</span> (convenience property concatenating all TextContent),
      <span class="mono">.finish_reason</span> (&quot;stop&quot; / &quot;length&quot; / &quot;tool_calls&quot;),
      <span class="mono">.author_name</span> / <span class="mono">.agent_id</span> (source identification in multi-agent scenarios).
      The structure aligns with non-streaming <span class="mono">AgentResponse</span>, minimizing code changes when switching modes.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">OpenAI SDK returns <span class="mono">ChatCompletionChunk</span> (text delta only);
      LangChain returns <span class="mono">AIMessageChunk</span>. MAF chunks carry <span class="mono">agent_id</span> and <span class="mono">author_name</span>,
      making them <strong>natively suited for multi-agent streaming</strong>.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Workflow streaming <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code"><span class="kw">async for</span> event <span class="kw">in</span> wf.run(<span class="st">&quot;hello&quot;</span>, stream=<span class="kw">True</span>):
    <span class="kw">if</span> event.type == <span class="st">&quot;output&quot;</span>:
        <span class="fn">print</span>(<span class="st">&quot;Final:&quot;</span>, event.data)
    <span class="kw">elif</span> event.type == <span class="st">&quot;intermediate&quot;</span>:
        <span class="fn">print</span>(<span class="st">&quot;Step:&quot;</span>, event.data)
    <span class="kw">elif</span> event.type == <span class="st">&quot;executor_invoked&quot;</span>:
        <span class="fn">print</span>(<span class="st">&quot;Running:&quot;</span>, event.executor_id)</pre>
In streaming mode <span class="mono">run()</span> returns <span class="mono">AsyncIterator[WorkflowEvent]</span> instead of <span class="mono">WorkflowRunResult</span>.</div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">Workflows can involve multiple agents and run for minutes. Users can't wait for the entire graph to finish —
      streaming events let the frontend <strong>show progress in real time</strong>: which node is running, what intermediate results look like, when the final output arrives.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">WorkflowEvent</span> has rich event types:
      <span class="mono">started</span> / <span class="mono">executor_invoked</span> / <span class="mono">executor_completed</span> (lifecycle),
      <span class="mono">output</span> / <span class="mono">intermediate</span> (data),
      <span class="mono">request_info</span> (HITL requests), <span class="mono">failed</span> (errors).
      Each event carries <span class="mono">executor_id</span>, <span class="mono">iteration</span>, <span class="mono">state</span> metadata.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">LangGraph streaming returns plain text chunks without structured events;
      Temporal has event history but doesn't support real-time push. MAF's <span class="mono">WorkflowEvent</span> is structured and richly typed —
      frontends can render progress bars, node highlights, and error alerts from it.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> OTel span hierarchy <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">Auto-generated span hierarchy in MAF:
<pre class="code">agent.run (parent span)
  ├── chat_client.call  <span class="cm"># each LLM call</span>
  │     attrs: input_tokens, output_tokens, model
  ├── tool.execute      <span class="cm"># each tool execution</span>
  │     attrs: tool.name, tool.call.id
  └── chat_client.call  <span class="cm"># tool loop calls model again</span>

workflow.run (parent span)
  ├── executor: upper   <span class="cm"># one child span per node</span>
  │     attrs: executor.id, executor.type
  ├── message.send      <span class="cm"># inter-node message passing</span>
  │     attrs: source_id, target_id
  └── executor: reverse</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">When a step in the agent chain is slow or errors out, you need to know <strong>exactly which LLM call or which tool
      execution</strong> is the problem. Hierarchical spans let you pinpoint bottlenecks in Jaeger/Grafana like reading a call stack.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a"><span class="mono">observability.py</span> defines an <span class="mono">OtelAttr</span> enum, auto-populating GenAI semantic convention attributes:
      <span class="mono">gen_ai.agent.id</span>, <span class="mono">gen_ai.usage.input_tokens</span>, <span class="mono">gen_ai.tool.name</span>, etc.
      The Workflow layer also tracks <span class="mono">workflow.id</span>, <span class="mono">executor.id</span>, <span class="mono">message.send</span>.
      Zero extra code — just configure an exporter and view traces in Jaeger / Zipkin / OTLP Collector.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">LangSmith is LangChain's proprietary tracing solution (vendor lock-in);
      LiteLLM only traces LLM calls, not tools or workflows. MAF uses <strong>standard OTel</strong> —
      compatible with the entire OTel ecosystem, no vendor lock-in.</div></div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> Custom spans / metrics <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 Example</div><div class="a">
<pre class="code"><span class="kw">from</span> agent_framework.observability <span class="kw">import</span> create_workflow_span, OtelAttr

<span class="kw">with</span> create_workflow_span(
    <span class="st">&quot;my_custom_step&quot;</span>,
    attributes={OtelAttr.EXECUTOR_ID: <span class="st">&quot;validator&quot;</span>},
) <span class="kw">as</span> span:
    result = validate(data)
    span.set_attribute(<span class="st">&quot;validation.passed&quot;</span>, result.ok)</pre></div></div>
    <div class="qa"><div class="q">❓ Why this matters</div><div class="a">The framework's auto-spans cover LLM and tool calls, but your <strong>business logic</strong>
      (custom validation, database queries, external API calls) also needs tracing. Custom spans fill those blind spots.</div></div>
    <div class="qa"><div class="q">✅ How MAF does it</div><div class="a">MAF exposes <span class="mono">create_workflow_span()</span> as a convenient entry point for custom spans,
      auto-attaching to the current trace context. You can also use the OTel SDK's <span class="mono">tracer.start_as_current_span()</span> directly.
      The framework's <span class="mono">OtelAttr</span> enum ensures attribute names match built-in spans — unified filtering in queries.</div></div>
    <div class="qa"><div class="q">🔀 Alternatives</div><div class="a">Some frameworks (e.g., Haystack) don't expose a tracer, forcing log-based tracing;
      LangSmith requires its SDK's <span class="mono">@traceable</span> decorator.
      MAF fully embraces the OTel standard — your custom spans and built-in spans coexist seamlessly on the same trace.</div></div>
  </div>
</details>

<h2>The real span tree (with the framework's real names)</h2>
<p>The hand-drawn hierarchy above is illustrative; in MAF the <strong>actual naming rule</strong> is <span class="mono">f"{operation} {target}"</span>
(<span class="mono">observability.py:2112</span>). The Agent side and the Workflow side each grow a tree:</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">agent</span><span class="name">invoke_agent {agent}</span></div>
    <div class="ld">root span, operation = <span class="mono">AGENT_INVOKE_OPERATION</span></div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">child</span><span class="name">chat {model}</span></div>
    <div class="ld">one per LLM call, attrs: <span class="mono">gen_ai.usage.input_tokens / output_tokens</span></div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">child</span><span class="name">execute_tool {name}</span></div>
    <div class="ld">one per tool execution, attrs: <span class="mono">gen_ai.tool.name / gen_ai.tool.call.id</span></div></div>
</div>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">workflow</span><span class="name">workflow.run</span></div>
    <div class="ld">root span, attrs: <span class="mono">workflow.id</span></div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">child</span><span class="name">executor.process {id}</span></div>
    <div class="ld">one per node processing a message, attrs: <span class="mono">executor.id / executor.type</span></div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">link</span><span class="name">message.send</span></div>
    <div class="ld">inter-node message passing, attrs: <span class="mono">message.source_id / message.target_id</span></div></div>
</div>
<p>An easily-missed but crucial design: the <span class="mono">executor.process</span> span is <strong>not</strong> nested under the upstream node — it is <strong>linked</strong> to the publishing source span
(<span class="mono">observability.py:2454</span>'s comment says verbatim "linked (not nested) ... supporting fan-in").
Why? Because a Workflow runs in parallel supersteps: a node may receive messages from <strong>several</strong> upstream nodes at once (fan-in).
Forced nesting could only attach it under one parent; a link can point at multiple sources at once, <strong>preserving the full fan-in causality</strong>.</p>

<h2>🔍 Real source: opening a span by hand</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span class="path">core/agent_framework/observability.py</span></div>
<pre><span class="cm"># observability.py:2445 — generic workflow span</span>
<span class="kw">def</span> <span class="fn">create_workflow_span</span>(
    name: str,
    attributes: Mapping[str, str | int] | <span class="kw">None</span> = <span class="kw">None</span>,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL,
) -> _AgnosticContextManager[trace.Span]:
    <span class="kw">return</span> workflow_tracer().start_as_current_span(name, kind=kind, attributes=attributes)

<span class="cm"># observability.py:2454 — executor processing span: link (not nest) for fan-in</span>
<span class="kw">def</span> <span class="fn">create_processing_span</span>(executor_id, executor_type, message_type, payload_type,
                          source_trace_contexts=<span class="kw">None</span>, source_span_ids=<span class="kw">None</span>):
    links = [trace.Link(...) <span class="kw">for</span> ... <span class="kw">in</span> sources]  <span class="cm"># many sources → many links (fan-in)</span>
    <span class="kw">return</span> workflow_tracer().start_as_current_span(
        f<span class="st">&quot;{OtelAttr.EXECUTOR_PROCESS_SPAN} {executor_id}&quot;</span>,  <span class="cm"># &quot;executor.process &lt;id&gt;&quot;</span>
        attributes={OtelAttr.EXECUTOR_ID: executor_id, ...}, links=links)</pre>
</div>
<p>Note <span class="mono">create_workflow_span</span> uses <span class="mono">start_as_current_span</span> — it sets the new span as the <strong>current context</strong>,
so any span you open inside the <span class="mono">with</span> block (including the framework's built-in <span class="mono">chat</span> / <span class="mono">execute_tool</span>) automatically becomes its child. That's the mechanism behind "auto-attached trees with zero extra code".</p>

<h2>Why streaming and observability are first-class</h2>
<p>Many frameworks treat these as afterthoughts: you stitch your own SSE for streaming, you instrument your own tracing. MAF flips it —
<strong>within a single <code>run()</code> call, stream and span are simultaneous byproducts</strong>. Three practical consequences:</p>
<table class="t">
  <tr><th>Capability</th><th>Without it</th><th>With MAF built in</th></tr>
  <tr><td>Streaming</td><td>users stare at a blank screen for 10+ seconds, assuming it hung</td><td>first-token latency is visible; long answers render as they generate</td></tr>
  <tr><td>Layered spans</td><td>"why did this run take 8s?" — nowhere to start</td><td>see at a glance whether the second <span class="mono">chat</span> was slow, or some tool</td></tr>
  <tr><td>Token attribution</td><td>the monthly bill overruns and you can't tell which Agent burned it</td><td>every <span class="mono">chat</span> span carries input/output_tokens, aggregable per Agent</td></tr>
</table>
<p>Underneath it's <strong>standard OpenTelemetry + GenAI semantic conventions</strong> (attribute names like <span class="mono">gen_ai.usage.input_tokens</span>),
so these spans feed straight into Jaeger, Grafana Tempo, or any OTLP backend with no vendor lock-in — the payoff of making observability first-class rather than a proprietary plugin.</p>

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
  <br>For the production deep-dive into trace / metric / log, see <a href="30-observability.html">Lesson 30 · Observability Deep-Dive</a>.
</div>
"""
