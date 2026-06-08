"""Content for Part 2 (user's view): lessons 04-07 — Chinese + English."""

# ---------------------------------------------------------------------------
L04_ZH = r"""
<p class="lead">和模型对话，本质是来回传递一串<strong>消息</strong>。MAF 把消息做成<strong>结构化对象</strong>
<span class="inline">Message</span>，而不是裸字典——类型更安全，还能携带工具调用、图片等多种内容。</p>

<div class="card analogy">
  <div class="tag">✉️ 生活类比</div>
  一条 <span class="mono">Message</span> 像一个<strong>信封</strong>：信封上写着<strong>寄件人身份</strong>（<span class="mono">role</span>：
  user / assistant / system / tool），信封里可以装<strong>多张内容卡片</strong>（<span class="mono">contents</span>：
  一段文字、一张图、一次工具调用、一份工具结果……）。
</div>

<h2>三个核心类型</h2>
<table class="t">
  <tr><th>类型</th><th>作用</th><th>来自</th></tr>
  <tr><td class="mono">Message</td><td>一条消息 = <span class="mono">role</span> + <span class="mono">contents</span></td><td class="mono">_types.py</td></tr>
  <tr><td class="mono">Role</td><td>身份：<span class="mono">"system"/"user"/"assistant"/"tool"</span></td><td class="mono">_types.py</td></tr>
  <tr><td class="mono">Content</td><td>统一内容类型，用工厂方法构造</td><td class="mono">_types.py</td></tr>
</table>

<h2>手拼 dict vs 结构化消息</h2>
<div class="cols">
  <div class="col"><h4>😣 裸字典</h4>
<pre class="code">messages = [
  {<span class="st">"role"</span>: <span class="st">"system"</span>, <span class="st">"content"</span>: <span class="st">"你是助手"</span>},
  {<span class="st">"role"</span>: <span class="st">"user"</span>, <span class="st">"content"</span>: <span class="st">"你好"</span>},
]
<span class="cm"># key 容易拼错，工具调用要手搓</span></pre></div>
  <div class="col"><h4>🙂 Message 对象</h4>
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Message
messages = [
  Message(<span class="st">"system"</span>, <span class="st">"你是助手"</span>),
  Message(<span class="st">"user"</span>, <span class="st">"你好"</span>),
]
<span class="cm"># 类型安全，可带多种 Content</span></pre></div>
</div>
<p><span class="inline">Message</span> 的第二个参数 <span class="mono">contents</span> 接受字符串（自动转成文本内容）、
<span class="mono">Content</span> 对象，或它们的列表。读文本用 <span class="inline">msg.text</span>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Content 能装哪些东西？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 用工厂方法构造</div>
      <div class="a"><span class="mono">Content</span> 是<strong>统一类型</strong>，用类方法创建不同种类：
<pre class="code">Content.from_text(<span class="st">"一段文字"</span>)
Content.from_data(data=..., media_type=<span class="st">"image/png"</span>)  <span class="cm"># 图片/二进制</span>
Content.from_uri(uri=<span class="st">"https://…"</span>, media_type=<span class="st">"image/png"</span>)
Content.from_function_call(...)      <span class="cm"># 模型要调工具</span>
Content.from_function_result(...)    <span class="cm"># 工具执行结果</span></pre>
        所以一条 <span class="mono">Message</span> 可以图文混排，也能承载工具调用 / 结果。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>对话 = 一串 <span class="mono">Message</span>；每条 = <span class="mono">role</span> + <span class="mono">contents</span>。</li>
    <li><span class="mono">Role</span> 有四种：system / user / assistant / tool。</li>
    <li><span class="mono">Content</span> 是统一类型，用 <span class="mono">from_text/from_data/from_function_call…</span> 构造。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  把"文本、图片、工具调用、工具结果"<strong>统一成一种 Content</strong>，靠 <span class="mono">type</span> 字段区分。
  消息结构因此既简单又可扩展——新增一种内容不破坏老代码。
</div>
"""

L04_EN = r"""
<p class="lead">Talking to a model is really passing a list of <strong>messages</strong> back and forth. MAF makes
messages <strong>structured objects</strong> (<span class="inline">Message</span>) instead of bare dicts — type-safe,
and able to carry tool calls, images and more.</p>

<div class="card analogy">
  <div class="tag">✉️ Analogy</div>
  A <span class="mono">Message</span> is like an <strong>envelope</strong>: the outside states the <strong>sender's
  identity</strong> (<span class="mono">role</span>: user / assistant / system / tool), and inside you can place
  <strong>several content cards</strong> (<span class="mono">contents</span>: some text, an image, a tool call, a tool result…).
</div>

<h2>Three core types</h2>
<table class="t">
  <tr><th>Type</th><th>Role</th><th>From</th></tr>
  <tr><td class="mono">Message</td><td>one message = <span class="mono">role</span> + <span class="mono">contents</span></td><td class="mono">_types.py</td></tr>
  <tr><td class="mono">Role</td><td>identity: <span class="mono">"system"/"user"/"assistant"/"tool"</span></td><td class="mono">_types.py</td></tr>
  <tr><td class="mono">Content</td><td>unified content type, built via factory methods</td><td class="mono">_types.py</td></tr>
</table>

<h2>Hand-built dicts vs structured messages</h2>
<div class="cols">
  <div class="col"><h4>😣 Bare dicts</h4>
<pre class="code">messages = [
  {<span class="st">"role"</span>: <span class="st">"system"</span>, <span class="st">"content"</span>: <span class="st">"You are a bot"</span>},
  {<span class="st">"role"</span>: <span class="st">"user"</span>, <span class="st">"content"</span>: <span class="st">"hi"</span>},
]
<span class="cm"># typo-prone keys; tool calls by hand</span></pre></div>
  <div class="col"><h4>🙂 Message objects</h4>
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Message
messages = [
  Message(<span class="st">"system"</span>, <span class="st">"You are a bot"</span>),
  Message(<span class="st">"user"</span>, <span class="st">"hi"</span>),
]
<span class="cm"># type-safe, carries any Content</span></pre></div>
</div>
<p><span class="inline">Message</span>'s second argument <span class="mono">contents</span> accepts a string (auto-converted to text),
a <span class="mono">Content</span> object, or a list of them. Read the text via <span class="inline">msg.text</span>.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> What can a Content hold? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Built with factory methods</div>
      <div class="a"><span class="mono">Content</span> is a <strong>unified type</strong>; class methods create each kind:
<pre class="code">Content.from_text(<span class="st">"some text"</span>)
Content.from_data(data=..., media_type=<span class="st">"image/png"</span>)  <span class="cm"># image/binary</span>
Content.from_uri(uri=<span class="st">"https://…"</span>, media_type=<span class="st">"image/png"</span>)
Content.from_function_call(...)      <span class="cm"># model wants a tool</span>
Content.from_function_result(...)    <span class="cm"># tool execution result</span></pre>
        So one <span class="mono">Message</span> can mix text and images, and carry tool calls / results.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>A conversation = a list of <span class="mono">Message</span>; each = <span class="mono">role</span> + <span class="mono">contents</span>.</li>
    <li><span class="mono">Role</span> has four values: system / user / assistant / tool.</li>
    <li><span class="mono">Content</span> is one unified type built via <span class="mono">from_text/from_data/from_function_call…</span></li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  Text, images, tool calls and tool results are <strong>unified into one Content</strong>, discriminated by a
  <span class="mono">type</span> field. The message shape stays simple yet extensible — adding a content kind breaks nothing.
</div>
"""

# ---------------------------------------------------------------------------
L05_ZH = r"""
<p class="lead"><strong>ChatClient</strong> 是"连到某个模型"的厂商无关接口；<strong>Agent</strong> 在它之上加了
名字、系统指令、工具和循环。本课讲怎么从 ChatClient 造出 Agent，并用 <span class="inline">run</span> 跑起来。</p>

<div class="card analogy">
  <div class="tag">🎧 生活类比</div>
  <strong>ChatClient</strong> 像<strong>对讲机</strong>：能和某个频道（模型）通话，但不带"人设"。
  <strong>Agent</strong> 像拿着对讲机、并被交代了岗位职责（instructions）和工具的<strong>值班员</strong>——你对值班员说话，他负责完成任务。
</div>

<h2>两种创建方式</h2>
<div class="cols">
  <div class="col"><h4>方式 A：<span class="mono">Agent(client=…)</span></h4>
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
agent = Agent(
  client=client,
  name=<span class="st">"HelloAgent"</span>,
  instructions=<span class="st">"You are friendly."</span>,
)</pre></div>
  <div class="col"><h4>方式 B：<span class="mono">client.as_agent(…)</span></h4>
<pre class="code">agent = client.as_agent(
  name=<span class="st">"HelloAgent"</span>,
  instructions=<span class="st">"You are friendly."</span>,
)
<span class="cm"># 等价，更顺手</span></pre></div>
</div>
<p>两种都行；<span class="inline">as_agent</span> 读起来更顺。底下都是同一个 <span class="mono">Agent</span>。</p>

<h2>跑起来：run 与流式</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">非流式 vs 流式</span></div>
<pre><span class="cm"># 非流式：一次拿到完整回答</span>
result = <span class="kw">await</span> agent.run(<span class="st">"What is the capital of France?"</span>)
<span class="fn">print</span>(result)

<span class="cm"># 流式：逐块拿到 token</span>
<span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">"Tell me a fun fact."</span>, stream=<span class="kw">True</span>):
    <span class="kw">if</span> chunk.text:
        <span class="fn">print</span>(chunk.text, end=<span class="st">""</span>, flush=<span class="kw">True</span>)</pre>
</div>
<p>同一个 <span class="inline">run()</span>：不传 <span class="mono">stream</span> 返回完整 <span class="mono">AgentResponse</span>；
传 <span class="mono">stream=True</span> 返回一个异步迭代器，逐块给 <span class="mono">AgentResponseUpdate</span>。</p>

<div class="card detail">
  <div class="tag">🔬 换厂商</div>
  把 <span class="inline">FoundryChatClient</span> 换成 <span class="inline">OpenAIChatClient</span>、
  <span class="inline">AnthropicChatClient</span>、<span class="inline">OllamaChatClient</span>……Agent 那层<strong>一行都不用改</strong>。
  各 client 来自对应 provider 包（见第 16 课）。
</div>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><strong>ChatClient = 连模型</strong>（厂商无关）；<strong>Agent = ChatClient + 人设 + 工具 + 循环</strong>。</li>
    <li>创建：<span class="mono">Agent(client=…)</span> 或 <span class="mono">client.as_agent(…)</span>，二选一。</li>
    <li><span class="mono">run()</span> 默认完整返回；<span class="mono">run(stream=True)</span> 逐块流式返回。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>流式与非流式共用一个 <span class="mono">run()</span></strong>，靠一个 <span class="mono">stream</span> 开关切换返回形态。
  调用心智统一，省掉两套 API。
</div>
"""

L05_EN = r"""
<p class="lead">A <strong>ChatClient</strong> is the vendor-agnostic "connect to a model" interface; an <strong>Agent</strong>
adds a name, system instructions, tools and a loop on top. This lesson builds an Agent from a ChatClient and runs
it with <span class="inline">run</span>.</p>

<div class="card analogy">
  <div class="tag">🎧 Analogy</div>
  A <strong>ChatClient</strong> is like a <strong>walkie-talkie</strong>: it can talk to a channel (model) but has no
  persona. An <strong>Agent</strong> is the <strong>operator</strong> holding that walkie-talkie who has been briefed on
  duties (instructions) and tools — you talk to the operator, who gets the job done.
</div>

<h2>Two ways to create</h2>
<div class="cols">
  <div class="col"><h4>A: <span class="mono">Agent(client=…)</span></h4>
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
agent = Agent(
  client=client,
  name=<span class="st">"HelloAgent"</span>,
  instructions=<span class="st">"You are friendly."</span>,
)</pre></div>
  <div class="col"><h4>B: <span class="mono">client.as_agent(…)</span></h4>
<pre class="code">agent = client.as_agent(
  name=<span class="st">"HelloAgent"</span>,
  instructions=<span class="st">"You are friendly."</span>,
)
<span class="cm"># equivalent, reads nicer</span></pre></div>
</div>
<p>Both work; <span class="inline">as_agent</span> reads more fluently. Same <span class="mono">Agent</span> underneath.</p>

<h2>Run it: blocking and streaming</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">non-streaming vs streaming</span></div>
<pre><span class="cm"># non-streaming: full answer at once</span>
result = <span class="kw">await</span> agent.run(<span class="st">"What is the capital of France?"</span>)
<span class="fn">print</span>(result)

<span class="cm"># streaming: tokens as they arrive</span>
<span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">"Tell me a fun fact."</span>, stream=<span class="kw">True</span>):
    <span class="kw">if</span> chunk.text:
        <span class="fn">print</span>(chunk.text, end=<span class="st">""</span>, flush=<span class="kw">True</span>)</pre>
</div>
<p>One <span class="inline">run()</span>: without <span class="mono">stream</span> it returns a full <span class="mono">AgentResponse</span>;
with <span class="mono">stream=True</span> it returns an async iterator yielding <span class="mono">AgentResponseUpdate</span> chunks.</p>

<div class="card detail">
  <div class="tag">🔬 Switching vendors</div>
  Replace <span class="inline">FoundryChatClient</span> with <span class="inline">OpenAIChatClient</span>,
  <span class="inline">AnthropicChatClient</span>, <span class="inline">OllamaChatClient</span>… and the Agent layer
  <strong>doesn't change at all</strong>. Each client comes from its provider package (Lesson 16).
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>ChatClient = the model</strong> (vendor-agnostic); <strong>Agent = ChatClient + persona + tools + loop</strong>.</li>
    <li>Create with <span class="mono">Agent(client=…)</span> or <span class="mono">client.as_agent(…)</span>.</li>
    <li><span class="mono">run()</span> returns the full response; <span class="mono">run(stream=True)</span> streams chunks.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Streaming and non-streaming share one <span class="mono">run()</span></strong>, toggled by a single
  <span class="mono">stream</span> flag. One mental model, no second API.
</div>
"""

# ---------------------------------------------------------------------------
L06_ZH = r"""
<p class="lead"><strong>工具（Tool）</strong>让 Agent 不只是"会说"，还能"会做"：查天气、读数据库、调 API。
你写一个普通 Python 函数，用 <span class="inline">@tool</span> 一标，模型就能调用它。</p>

<div class="card analogy">
  <div class="tag">🧰 生活类比</div>
  模型像个<strong>聪明但手短的大脑</strong>：它知道"该查天气了"，但自己摸不到温度计。
  工具就是你递给它的<strong>一件件趁手家伙</strong>，并附上说明书（函数签名 + docstring），它照着说明书使用。
</div>

<h2>定义一个工具</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">samples/01-get-started/02_add_tools.py</span></div>
<pre><span class="kw">from</span> typing <span class="kw">import</span> Annotated
<span class="kw">from</span> agent_framework <span class="kw">import</span> Agent, tool
<span class="kw">from</span> pydantic <span class="kw">import</span> Field

<span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">get_weather</span>(
    location: Annotated[str, Field(description=<span class="st">"The location to get weather for."</span>)],
) -> str:
    <span class="st">&quot;&quot;&quot;Get the weather for a given location.&quot;&quot;&quot;</span>
    <span class="kw">return</span> <span class="st">f"It's sunny in {location}."</span>

agent = Agent(client=client, name=<span class="st">"WeatherAgent"</span>,
    instructions=<span class="st">"Use get_weather to answer."</span>,
    tools=[get_weather])

result = <span class="kw">await</span> agent.run(<span class="st">"What's the weather in Seattle?"</span>)</pre>
</div>

<h2>三件事自动发生</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>生成 schema</h4>
    <p>从函数签名 + <span class="mono">Annotated[..., Field(description=…)]</span> + docstring 自动生成 JSON Schema，交给模型。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>模型决定调用</h4>
    <p>模型在回答里产出一个 <span class="mono">function_call</span>（函数名 + 参数）。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>框架执行并回灌</h4>
    <p>Agent 调用你的函数，把 <span class="mono">function_result</span> 追加进对话，再让模型继续。</p></div></div>
</div>

<div class="card warn">
  <div class="tag">⚠️ 审批模式</div>
  <span class="inline">approval_mode="never_require"</span> 仅为示例图省事——<strong>生产中应使用
  <span class="inline">"always_require"</span></strong>，在工具执行前要求人工确认（尤其是写操作 / 花钱的操作）。
</div>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><span class="mono">@tool</span> 把普通函数变成模型可调用的工具，schema 自动生成。</li>
    <li>用 <span class="mono">Annotated[..., Field(description=…)]</span> 给参数写说明，docstring 写函数用途。</li>
    <li>把工具放进 <span class="mono">Agent(tools=[…])</span>；执行 + 回灌由框架完成。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>"函数即工具"</strong>：你不用手写 JSON Schema，类型注解和 docstring 就是契约。
  代码与给模型的描述<strong>永远同步</strong>，因为它们本来就是同一份。
</div>
"""

L06_EN = r"""
<p class="lead"><strong>Tools</strong> let an Agent not just "talk" but "do": fetch weather, read a database, call an API.
Write an ordinary Python function, tag it with <span class="inline">@tool</span>, and the model can call it.</p>

<div class="card analogy">
  <div class="tag">🧰 Analogy</div>
  The model is a <strong>smart brain with short arms</strong>: it knows "time to check the weather" but can't reach
  the thermometer. Tools are the <strong>handy instruments</strong> you hand it, each with a manual (function signature
  + docstring) it follows.
</div>

<h2>Define a tool</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">samples/01-get-started/02_add_tools.py</span></div>
<pre><span class="kw">from</span> typing <span class="kw">import</span> Annotated
<span class="kw">from</span> agent_framework <span class="kw">import</span> Agent, tool
<span class="kw">from</span> pydantic <span class="kw">import</span> Field

<span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">get_weather</span>(
    location: Annotated[str, Field(description=<span class="st">"The location to get weather for."</span>)],
) -> str:
    <span class="st">&quot;&quot;&quot;Get the weather for a given location.&quot;&quot;&quot;</span>
    <span class="kw">return</span> <span class="st">f"It's sunny in {location}."</span>

agent = Agent(client=client, name=<span class="st">"WeatherAgent"</span>,
    instructions=<span class="st">"Use get_weather to answer."</span>,
    tools=[get_weather])

result = <span class="kw">await</span> agent.run(<span class="st">"What's the weather in Seattle?"</span>)</pre>
</div>

<h2>Three things happen automatically</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Generate schema</h4>
    <p>A JSON Schema is built from the signature + <span class="mono">Annotated[..., Field(description=…)]</span> + docstring, and handed to the model.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Model decides to call</h4>
    <p>The model emits a <span class="mono">function_call</span> (function name + arguments) in its response.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Framework executes & feeds back</h4>
    <p>The Agent runs your function, appends the <span class="mono">function_result</span>, and lets the model continue.</p></div></div>
</div>

<div class="card warn">
  <div class="tag">⚠️ Approval mode</div>
  <span class="inline">approval_mode="never_require"</span> is just for sample brevity — <strong>in production use
  <span class="inline">"always_require"</span></strong> to require human confirmation before a tool runs (especially
  for writes / spend).
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><span class="mono">@tool</span> turns a plain function into a model-callable tool; the schema is auto-generated.</li>
    <li>Use <span class="mono">Annotated[..., Field(description=…)]</span> for params and a docstring for purpose.</li>
    <li>Put tools in <span class="mono">Agent(tools=[…])</span>; execution + feedback is handled by the framework.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>"A function is a tool"</strong>: you never hand-write JSON Schema — type hints and the docstring are the
  contract. Code and the model-facing description <strong>can't drift</strong>, because they're the same thing.
</div>
"""

# ---------------------------------------------------------------------------
L07_ZH = r"""
<p class="lead">默认情况下，每次 <span class="inline">run()</span> 都是"失忆"的。要让 Agent <strong>记住上文</strong>，
就把同一个 <strong>会话（<span class="mono">AgentSession</span>）</strong>传给连续的调用。更长期的记忆，则交给 <strong>ContextProvider</strong>。</p>

<div class="card analogy">
  <div class="tag">📒 生活类比</div>
  <span class="mono">AgentSession</span> 像一本<strong>共享记事本</strong>：每轮对话都写进同一本，下一轮模型翻看它就"记得"。
  <strong>ContextProvider</strong> 则像一位<strong>助理</strong>，在每次回答前把"相关的旧记忆 / 外部知识"悄悄塞进上下文。
</div>

<h2>多轮对话：带上会话</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">samples/01-get-started/03_multi_turn.py</span></div>
<pre>session = agent.create_session()

result = <span class="kw">await</span> agent.run(
    <span class="st">"My name is Alice and I love hiking."</span>, session=session)

result = <span class="kw">await</span> agent.run(
    <span class="st">"What do you remember about me?"</span>, session=session)
<span class="cm"># → 记得 Alice、喜欢徒步</span></pre>
</div>
<p>关键就一点：<strong>把同一个 <span class="mono">session</span> 透传给每次 <span class="mono">run()</span></strong>，历史便自动累积。
不传 session，则每次都是全新对话。</p>

<h2>更长期的记忆 / 外部知识</h2>
<div class="card detail">
  <div class="tag">🔬 ContextProvider</div>
  会话只在"本轮对话"内累积。要跨会话记住用户偏好，或在回答前注入检索到的知识（RAG），用
  <span class="inline">ContextProvider</span>：例如 <span class="inline">MemoryContextProvider</span> 把记忆存进可检索的库，
  每次 run 前自动把相关条目拼进上下文。（记忆库 / 各存储后端见第 16 课与各 provider 包。）
</div>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>无状态是默认；<strong>用 <span class="mono">AgentSession</span> 携带多轮历史</strong>。</li>
    <li><span class="mono">agent.create_session()</span> 建会话，<span class="mono">run(…, session=session)</span> 复用它。</li>
    <li>跨会话 / 外部知识用 <span class="mono">ContextProvider</span>（如 <span class="mono">MemoryContextProvider</span>）。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  把"短期对话历史"（Session）和"长期可检索记忆"（ContextProvider）<strong>分成两层</strong>：
  前者简单透传，后者可插拔。需求小就只用 Session，需求大再加 Provider，复杂度按需付费。
</div>
"""

L07_EN = r"""
<p class="lead">By default each <span class="inline">run()</span> is "amnesiac". To make an Agent <strong>remember</strong>,
pass the same <strong>session (<span class="mono">AgentSession</span>)</strong> across calls. For longer-term memory, use a
<strong>ContextProvider</strong>.</p>

<div class="card analogy">
  <div class="tag">📒 Analogy</div>
  An <span class="mono">AgentSession</span> is a <strong>shared notebook</strong>: every turn writes into the same book,
  so next turn the model "remembers" by reading it. A <strong>ContextProvider</strong> is an <strong>assistant</strong>
  that quietly slips "relevant old memories / external knowledge" into the context before each answer.
</div>

<h2>Multi-turn: carry a session</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">samples/01-get-started/03_multi_turn.py</span></div>
<pre>session = agent.create_session()

result = <span class="kw">await</span> agent.run(
    <span class="st">"My name is Alice and I love hiking."</span>, session=session)

result = <span class="kw">await</span> agent.run(
    <span class="st">"What do you remember about me?"</span>, session=session)
<span class="cm"># → remembers Alice, likes hiking</span></pre>
</div>
<p>The whole trick: <strong>pass the same <span class="mono">session</span> into every <span class="mono">run()</span></strong> and
history accumulates. Omit the session and each call starts fresh.</p>

<h2>Longer-term memory / external knowledge</h2>
<div class="card detail">
  <div class="tag">🔬 ContextProvider</div>
  A session only accumulates within "this conversation". To remember user preferences across sessions, or to inject
  retrieved knowledge (RAG) before answering, use a <span class="inline">ContextProvider</span> — e.g.
  <span class="inline">MemoryContextProvider</span> stores memories in a searchable store and splices relevant entries
  into context before each run. (Memory stores / backends: Lesson 16 and the provider packages.)
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Stateless by default; <strong>use <span class="mono">AgentSession</span> to carry multi-turn history</strong>.</li>
    <li><span class="mono">agent.create_session()</span> creates one; <span class="mono">run(…, session=session)</span> reuses it.</li>
    <li>Cross-session / external knowledge → <span class="mono">ContextProvider</span> (e.g. <span class="mono">MemoryContextProvider</span>).</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  Short-term history (Session) and long-term searchable memory (ContextProvider) are <strong>two layers</strong>:
  the former is a simple pass-through, the latter is pluggable. Use just Session for small needs, add a Provider for
  big ones — complexity is pay-as-you-go.
</div>
"""
