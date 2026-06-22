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

<details class="accordion">
  <summary><span class="badge-num">1</span> FunctionTool 里装了什么？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa"><div class="q">🧪 示例</div><div class="a"><span class="mono">FunctionTool</span>（<span class="mono">_tools.py:240</span>）持有：原始函数引用、生成的 JSON Schema、
      <span class="mono">approval_mode</span>（调用前是否需要人工审批）、函数名、描述。
      <span class="mono">@tool</span>（<span class="mono">_tools.py:1145</span>）是构造 <span class="mono">FunctionTool</span> 的语法糖。</div></div>
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
    <div class="qa"><div class="q">🧪 Example</div><div class="a"><span class="mono">FunctionTool</span> (<span class="mono">_tools.py:240</span>) holds: the original function reference,
      the generated JSON Schema, <span class="mono">approval_mode</span> (whether human approval is needed before invocation),
      the function name and description.
      <span class="mono">@tool</span> (<span class="mono">_tools.py:1145</span>) is syntactic sugar for constructing a <span class="mono">FunctionTool</span>.</div></div>
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
        ctx.metadata[<span class="st">"total_tokens"</span>] = usage.prompt_tokens + usage.completion_tokens

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
        ctx.metadata[<span class="st">"total_tokens"</span>] = usage.prompt_tokens + usage.completion_tokens

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

upper = UpperCase(id=<span class="st">"upper"</span>)
wf = WorkflowBuilder(start_executor=upper) \
    .add_edge(upper, reverse).build()
events = <span class="kw">await</span> wf.run(<span class="st">"hello"</span>)  <span class="cm"># → "OLLEH"</span></pre>
</div>

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
      ① <span class="mono">MagenticManager</span>（指挥官）用 TaskLedger 维护事实和计划；
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
      ① <span class="mono">MagenticManager</span> (conductor) maintains facts and plans via a TaskLedger;
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
