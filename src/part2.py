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
  <summary><span class="badge-num">1</span> Content 能装哪些东西？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a"><span class="mono">Content</span> 是<strong>统一类型</strong>，用类方法创建不同种类：
<pre class="code">Content.from_text(<span class="st">"一段文字"</span>)
Content.from_data(data=..., media_type=<span class="st">"image/png"</span>)  <span class="cm"># 图片/二进制</span>
Content.from_uri(uri=<span class="st">"https://…"</span>, media_type=<span class="st">"image/png"</span>)
Content.from_function_call(...)      <span class="cm"># 模型要调工具</span>
Content.from_function_result(...)    <span class="cm"># 工具执行结果</span></pre>
        所以一条 <span class="mono">Message</span> 可以图文混排，也能承载工具调用 / 结果。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">LLM 能力已超出"纯文本问答"：GPT-4o、Claude支持图像输入，模型可请求调用工具并接收结果。如果每种内容用不同字段（<span class="mono">text</span>、<span class="mono">image_url</span>、<span class="mono">tool_calls</span>……），消息结构变复杂、不可扩展。统一成 <span class="mono">Content</span> 列表后，代码只关心<strong>"一条消息有多个内容块"</strong>，不必为每种类型特殊处理。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 用<strong>判别联合（discriminated union）</strong>：每个 <span class="mono">Content</span> 都有 <span class="mono">type</span> 字段（<span class="mono">"text"</span>/<span class="mono">"data"</span>/<span class="mono">"uri"</span>/<span class="mono">"function_call"</span>/<span class="mono">"function_result"</span>），框架按 type 路由。新增内容类型（如视频、音频）只需加一个新 type，老消息仍能正常处理。类型安全由 Pydantic 保证，IDE 有完整提示。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>OpenAI SDK</strong>：text 放 <span class="mono">content</span> 字段，图像放 <span class="mono">content</span> 列表，工具调用放 <span class="mono">tool_calls</span> 字段——三种形态不一致，解析时需要分支判断。</li>
        <li><strong>Anthropic</strong>：采用 <span class="mono">content</span> 数组 + <span class="mono">type</span> 区分，与 MAF 类似，但每个厂商格式不同。</li>
        <li>MAF 把各家统一成一套，跨厂商代码零修改。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Message 的构造方式 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="cm"># 纯文本（字符串自动包装）</span>
msg = Message(<span class="st">"user"</span>, <span class="st">"你好"</span>)

<span class="cm"># 单个 Content 对象</span>
msg = Message(<span class="st">"user"</span>, Content.from_text(<span class="st">"你好"</span>))

<span class="cm"># 多个 Content：图文混排</span>
msg = Message(<span class="st">"user"</span>, [
    Content.from_text(<span class="st">"这张图是什么？"</span>),
    Content.from_uri(uri=<span class="st">"https://example.com/img.png"</span>, media_type=<span class="st">"image/png"</span>)
])

<span class="cm"># 读取文本快捷方式</span>
text = msg.text  <span class="cm"># 自动从 contents 中提取文本</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">多模态对话越来越常见：用户发一张图 + 一段问题；模型回复文本 + 图表；工具调用与工具结果也要和文本混排在同一条消息里。如果 <span class="mono">Message</span> 只能装一个字符串，需要拆成多条消息或手拼复杂结构。允许<strong>异构内容列表</strong>后，一条消息能自然表达"文字 + 图 + 工具调用"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">Message</span> 的 <span class="mono">contents</span> 参数接受：<ul>
        <li><strong>字符串</strong>：自动转 <span class="mono">Content.from_text(...)</span></li>
        <li><strong>单个 Content</strong>：原样包装成列表</li>
        <li><strong>Content 列表</strong>：直接存储</li>
      </ul>
      同时提供 <span class="mono">.text</span> 属性，自动拼接所有文本内容（多个 text content时用空格连接）。用户可按需简单或复杂使用，心智模型统一。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>OpenAI</strong>：文本消息 vs 多内容消息用不同格式（<span class="mono">{role, content: "str"}</span> vs <span class="mono">{role, content: [{type, ...}]}</span>），工具调用另加 <span class="mono">tool_calls</span> 数组。框架需判断格式再解析。</li>
        <li><strong>LangChain</strong>：<span class="mono">HumanMessage</span>/<span class="mono">AIMessage</span> 各自不同构造函数。</li>
        <li>MAF <strong>统一构造函数</strong>，类型安全 + IDE提示 + 多模态开箱即用。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 工具调用如何融入消息流 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="cm"># 模型输出：assistant 消息带 function_call</span>
msg_call = Message(<span class="st">"assistant"</span>, [
    Content.from_function_call(
        name=<span class="st">"get_weather"</span>,
        arguments={<span class="st">"location"</span>: <span class="st">"Seattle"</span>},
        call_id=<span class="st">"call_abc123"</span>
    )
])

<span class="cm"># 框架回灌：role="tool" 消息带 function_result</span>
msg_result = Message(<span class="st">"tool"</span>, [
    Content.from_function_result(
        name=<span class="st">"get_weather"</span>,
        result=<span class="st">"Sunny, 72°F"</span>,
        call_id=<span class="st">"call_abc123"</span>
    )
])
<span class="cm"># 这两条追加进对话历史，模型继续生成最终答案</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">工具调用是多轮交互：<ol>
        <li>模型决定"需要工具"，输出 function_call</li>
        <li>框架执行工具，拿到结果</li>
        <li>框架把结果追加进对话，模型读取后产出最终答案</li>
      </ol>
      如果工具调用/结果不是标准消息，就需要单独管道。把它们纳入 <span class="mono">Message</span> 后，<strong>整个对话就是一条消息链</strong>，无需特殊逻辑。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">Content.from_function_call</span> 和 <span class="mono">.from_function_result</span> 是两种特殊内容类型，完全融入消息体系：<ul>
        <li><strong>类型统一</strong>：工具调用 = assistant 消息 + function_call content；工具结果 = tool 消息 + function_result content。</li>
        <li><strong>序列化一致</strong>：历史回放、日志、调试时，工具调用和普通消息用相同JSON结构。</li>
        <li><strong>可扩展</strong>：未来加"并行工具调用"只需在一条消息的 contents 里放多个 function_call。</li>
      </ul></div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>OpenAI</strong>：assistant 消息加 <span class="mono">tool_calls</span> 数组，tool 消息用 <span class="mono">role="tool" + tool_call_id</span>。需两套字段。</li>
        <li><strong>Anthropic</strong>：<span class="mono">content</span> 数组里放 <span class="mono">tool_use</span> / <span class="mono">tool_result</span> 块，和 MAF思路接近，但每家格式不同。</li>
        <li>MAF 抹平差异：开发者用统一API，框架负责转换各厂商格式。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 序列化与反序列化 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="cm"># 消息 → 字典（可JSON序列化）</span>
msg = Message(<span class="st">"user"</span>, <span class="st">"Hello"</span>)
d = msg.to_dict()
<span class="cm"># → {"role": "user", "contents": [{"type": "text", "text": "Hello"}]}</span>

<span class="cm"># 字典 → 消息（从JSON恢复）</span>
msg_restored = Message.from_dict(d)
<span class="kw">assert</span> msg_restored.role == <span class="st">"user"</span>
<span class="kw">assert</span> msg_restored.text == <span class="st">"Hello"</span>

<span class="cm"># 工具调用也能完整序列化</span>
msg_with_tool = Message(<span class="st">"assistant"</span>, [
    Content.from_function_call(name=<span class="st">"foo"</span>, arguments={<span class="st">"x"</span>: 1})
])
d2 = msg_with_tool.to_dict()
msg_back = Message.from_dict(d2)  <span class="cm"># 完全恢复</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">实际应用需要：<ul>
        <li><strong>持久化</strong>：把对话历史存到数据库（Redis、Cosmos、PostgreSQL）。</li>
        <li><strong>回放调试</strong>：记录生产环境的消息流，本地重现问题。</li>
        <li><strong>审计日志</strong>：合规要求保存所有对话（含工具调用）。</li>
        <li><strong>跨服务传递</strong>：微服务间传递消息上下文。</li>
      </ul>
      如果不能无损序列化，工具调用、图像等复杂内容会丢失信息。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">Message.to_dict()</span> / <span class="mono">from_dict(...)</span> 是<strong>完全可逆</strong>的：<ul>
        <li>所有 <span class="mono">Content</span> 类型（text/data/uri/function_call/function_result）都能无损序列化。</li>
        <li>返回的字典是<strong>纯 JSON</strong>，可直接存储、传输、日志。</li>
        <li>Pydantic 模型自动处理类型验证，反序列化时类型错误会抛异常。</li>
        <li>第三方持久化库（如 <span class="mono">redis</span>、<span class="mono">azure-cosmos</span>）可直接存字典。</li>
      </ul></div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>OpenAI SDK</strong>：原生消息已是字典，但格式每版本可能变，没有类型保证。</li>
        <li><strong>LangChain</strong>：<span class="mono">Message.dict()</span> 返回嵌套结构，字段名不稳定，需自己处理。</li>
        <li><strong>手工JSON</strong>：完全自定义，但schema演进时容易破坏兼容性。</li>
        <li>MAF <strong>schema有版本管理</strong>，升级框架时老数据能自动迁移（见 <span class="mono">_types.py</span> 的兼容层）。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> 和 OpenAI dict 格式的对比 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<table class="t">
<tr><th>场景</th><th>OpenAI 原生格式</th><th>MAF 格式</th></tr>
<tr><td>纯文本</td><td><pre class="code">{<span class="st">"role"</span>: <span class="st">"user"</span>,
 <span class="st">"content"</span>: <span class="st">"hi"</span>}</pre></td><td><pre class="code">Message(<span class="st">"user"</span>, <span class="st">"hi"</span>)</pre></td></tr>
<tr><td>工具调用</td><td><pre class="code">{<span class="st">"role"</span>: <span class="st">"assistant"</span>,
 <span class="st">"tool_calls"</span>: [{
   <span class="st">"type"</span>: <span class="st">"function"</span>,
   <span class="st">"function"</span>: {<span class="st">"name"</span>: <span class="st">"get_weather"</span>, ...}
 }]}</pre></td><td><pre class="code">Message(<span class="st">"assistant"</span>, [
  Content.from_function_call(
    name=<span class="st">"get_weather"</span>, ...
  )
])</pre></td></tr>
<tr><td>工具结果</td><td><pre class="code">{<span class="st">"role"</span>: <span class="st">"tool"</span>,
 <span class="st">"content"</span>: <span class="st">"result"</span>,
 <span class="st">"tool_call_id"</span>: <span class="st">"x"</span>}</pre></td><td><pre class="code">Message(<span class="st">"tool"</span>, [
  Content.from_function_result(
    result=<span class="st">"result"</span>, call_id=<span class="st">"x"</span>
  )
])</pre></td></tr>
</table>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">直接用 OpenAI dict 的问题：<ul>
        <li><strong>厂商锁定</strong>：切换到 Anthropic/Ollama/Azure 需大量改动。</li>
        <li><strong>字段分散</strong>：<span class="mono">content</span> / <span class="mono">tool_calls</span> / <span class="mono">tool_call_id</span> 分散在不同层级，解析复杂。</li>
        <li><strong>无类型安全</strong>：拼写错误运行时才报错。</li>
        <li><strong>格式不统一</strong>：纯文本 vs 图像 vs 工具调用用不同结构。</li>
      </ul>
      抽象层让你<strong>写一次，到处运行</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 提供<strong>统一抽象</strong>，但<strong>双向转换</strong>能力齐全：<ul>
        <li><span class="mono">BaseChatClient</span> 子类（如 <span class="mono">OpenAIChatClient</span>）内部自动把 <span class="mono">Message</span> 转成厂商格式，调完API再转回来。</li>
        <li>转换逻辑封装在客户端内部（私有方法 <span class="mono">_prepare_messages_for_openai</span>，见 <span class="mono">python/packages/openai/agent_framework_openai/_chat_client.py</span>），一般无需手动调用。</li>
        <li><strong>类型安全</strong>：IDE 自动补全 <span class="mono">Message(...)</span> / <span class="mono">Content.from_...</span>，编译期发现错误。</li>
        <li><strong>可测试</strong>：单元测试不依赖真实 LLM，mock <span class="mono">Message</span> 即可。</li>
      </ul></div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>直接用 SDK dict</strong>：零抽象，换厂商需全盘重构。</li>
        <li><strong>LangChain MessageType</strong>：提供抽象，但<span class="mono">HumanMessage</span>/<span class="mono">AIMessage</span>/<span class="mono">ToolMessage</span> 分类过细，增加心智负担。</li>
        <li><strong>LlamaIndex ChatMessage</strong>：简单统一，但功能有限，多模态/工具调用支持弱。</li>
        <li>MAF <strong>恰到好处</strong>：一个 <span class="mono">Message</span> + 五种 <span class="mono">Content</span>，涵盖所有场景，各厂商无缝切换。</li>
      </ul></div>
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
  <summary><span class="badge-num">1</span> What can a Content hold? <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a"><span class="mono">Content</span> is a <strong>unified type</strong>; class methods create each kind:
<pre class="code">Content.from_text(<span class="st">"some text"</span>)
Content.from_data(data=..., media_type=<span class="st">"image/png"</span>)  <span class="cm"># image/binary</span>
Content.from_uri(uri=<span class="st">"https://…"</span>, media_type=<span class="st">"image/png"</span>)
Content.from_function_call(...)      <span class="cm"># model wants a tool</span>
Content.from_function_result(...)    <span class="cm"># tool execution result</span></pre>
        So one <span class="mono">Message</span> can mix text and images, and carry tool calls / results.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">LLM capabilities go beyond "pure text Q&A": GPT-4o and Claude support image inputs, models can request tool calls and receive results. If each content kind uses separate fields (<span class="mono">text</span>, <span class="mono">image_url</span>, <span class="mono">tool_calls</span>…), the message shape becomes complex and non-extensible. Unifying into a <span class="mono">Content</span> list means code only cares about <strong>"a message has multiple content blocks"</strong>, with no special-casing per type.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF uses a <strong>discriminated union</strong>: every <span class="mono">Content</span> has a <span class="mono">type</span> field (<span class="mono">"text"</span>/<span class="mono">"data"</span>/<span class="mono">"uri"</span>/<span class="mono">"function_call"</span>/<span class="mono">"function_result"</span>); the framework routes by type. Adding a new content kind (video, audio) only requires a new type; old messages still parse. Pydantic ensures type safety, IDEs provide full hints.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>OpenAI SDK</strong>: text in <span class="mono">content</span> field, images in <span class="mono">content</span> array, tool calls in <span class="mono">tool_calls</span> field — three inconsistent shapes requiring branching logic.</li>
        <li><strong>Anthropic</strong>: uses <span class="mono">content</span> array + <span class="mono">type</span> discrimination similar to MAF, but each vendor differs.</li>
        <li>MAF unifies them all into one format, zero code changes across vendors.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Constructing Messages <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="cm"># Plain text (string auto-wrapped)</span>
msg = Message(<span class="st">"user"</span>, <span class="st">"hello"</span>)

<span class="cm"># Single Content object</span>
msg = Message(<span class="st">"user"</span>, Content.from_text(<span class="st">"hello"</span>))

<span class="cm"># Multiple Content: mixed text + image</span>
msg = Message(<span class="st">"user"</span>, [
    Content.from_text(<span class="st">"What's in this image?"</span>),
    Content.from_uri(uri=<span class="st">"https://example.com/img.png"</span>, media_type=<span class="st">"image/png"</span>)
])

<span class="cm"># Text shortcut</span>
text = msg.text  <span class="cm"># auto-extracts text from contents</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Multimodal conversations are increasingly common: a user sends an image + a question; the model replies with text + a chart; tool calls and results must coexist with text in the same message. If <span class="mono">Message</span> only holds a string, you'd need multiple messages or complex manual structures. Allowing a <strong>heterogeneous content list</strong> lets one message naturally express "text + image + tool call".</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">Message</span>'s <span class="mono">contents</span> parameter accepts:<ul>
        <li><strong>String</strong>: auto-converts to <span class="mono">Content.from_text(...)</span></li>
        <li><strong>Single Content</strong>: wrapped into a list</li>
        <li><strong>Content list</strong>: stored directly</li>
      </ul>
      Also provides <span class="mono">.text</span> property that auto-concatenates all text contents (joins multiple text blocks with spaces). Users can use simple or complex forms as needed; mental model stays unified.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>OpenAI</strong>: text messages vs multi-content messages use different formats (<span class="mono">{role, content: "str"}</span> vs <span class="mono">{role, content: [{type, ...}]}</span>), tool calls add a <span class="mono">tool_calls</span> array. Framework must detect format before parsing.</li>
        <li><strong>LangChain</strong>: <span class="mono">HumanMessage</span>/<span class="mono">AIMessage</span> have different constructors.</li>
        <li>MAF <strong>unified constructor</strong>: type-safe + IDE hints + multimodal out-of-the-box.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Tool calls as message flow <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="cm"># Model output: assistant message with function_call</span>
msg_call = Message(<span class="st">"assistant"</span>, [
    Content.from_function_call(
        name=<span class="st">"get_weather"</span>,
        arguments={<span class="st">"location"</span>: <span class="st">"Seattle"</span>},
        call_id=<span class="st">"call_abc123"</span>
    )
])

<span class="cm"># Framework feedback: role="tool" message with function_result</span>
msg_result = Message(<span class="st">"tool"</span>, [
    Content.from_function_result(
        name=<span class="st">"get_weather"</span>,
        result=<span class="st">"Sunny, 72°F"</span>,
        call_id=<span class="st">"call_abc123"</span>
    )
])
<span class="cm"># These two append to history; model continues with final answer</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Tool calls are multi-turn interactions:<ol>
        <li>Model decides "need tool", outputs function_call</li>
        <li>Framework executes tool, gets result</li>
        <li>Framework appends result to conversation; model reads and produces final answer</li>
      </ol>
      If tool calls/results aren't standard messages, you need a separate pipeline. Embedding them in <span class="mono">Message</span> makes <strong>the entire conversation a message chain</strong>, no special logic required.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">Content.from_function_call</span> and <span class="mono">.from_function_result</span> are two special content types fully integrated into the message system:<ul>
        <li><strong>Type unification</strong>: tool call = assistant message + function_call content; tool result = tool message + function_result content.</li>
        <li><strong>Consistent serialization</strong>: history replay, logs, debugging all use the same JSON structure for tool calls and regular messages.</li>
        <li><strong>Extensible</strong>: future "parallel tool calls" just needs multiple function_call contents in one message.</li>
      </ul></div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>OpenAI</strong>: assistant message adds <span class="mono">tool_calls</span> array; tool message uses <span class="mono">role="tool" + tool_call_id</span>. Two field sets.</li>
        <li><strong>Anthropic</strong>: <span class="mono">content</span> array holds <span class="mono">tool_use</span>/<span class="mono">tool_result</span> blocks, similar to MAF but each vendor differs.</li>
        <li>MAF abstracts the differences: developers use one API, framework handles vendor conversion.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Serialization <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="cm"># Message → dict (JSON-serializable)</span>
msg = Message(<span class="st">"user"</span>, <span class="st">"Hello"</span>)
d = msg.to_dict()
<span class="cm"># → {"role": "user", "contents": [{"type": "text", "text": "Hello"}]}</span>

<span class="cm"># dict → Message (restore from JSON)</span>
msg_restored = Message.from_dict(d)
<span class="kw">assert</span> msg_restored.role == <span class="st">"user"</span>
<span class="kw">assert</span> msg_restored.text == <span class="st">"Hello"</span>

<span class="cm"># Tool calls also fully serialize</span>
msg_with_tool = Message(<span class="st">"assistant"</span>, [
    Content.from_function_call(name=<span class="st">"foo"</span>, arguments={<span class="st">"x"</span>: 1})
])
d2 = msg_with_tool.to_dict()
msg_back = Message.from_dict(d2)  <span class="cm"># fully restored</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Real applications need:<ul>
        <li><strong>Persistence</strong>: store conversation history in databases (Redis, Cosmos, PostgreSQL).</li>
        <li><strong>Replay debugging</strong>: capture production message flows, reproduce locally.</li>
        <li><strong>Audit logs</strong>: compliance requires saving all conversations (including tool calls).</li>
        <li><strong>Cross-service passing</strong>: microservices pass message context.</li>
      </ul>
      Without lossless serialization, tool calls, images and other complex content lose information.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">Message.to_dict()</span> / <span class="mono">from_dict(...)</span> are <strong>fully reversible</strong>:<ul>
        <li>All <span class="mono">Content</span> types (text/data/uri/function_call/function_result) serialize losslessly.</li>
        <li>Returned dict is <strong>pure JSON</strong>, can be directly stored, transmitted, logged.</li>
        <li>Pydantic models auto-handle type validation; deserialization raises on type errors.</li>
        <li>Third-party persistence libs (like <span class="mono">redis</span>, <span class="mono">azure-cosmos</span>) can directly store dicts.</li>
      </ul></div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>OpenAI SDK</strong>: native messages are already dicts, but format may change per version, no type guarantees.</li>
        <li><strong>LangChain</strong>: <span class="mono">Message.dict()</span> returns nested structures, field names unstable, requires manual handling.</li>
        <li><strong>Manual JSON</strong>: fully custom, but schema evolution easily breaks compatibility.</li>
        <li>MAF <strong>versioned schema</strong>: framework upgrades auto-migrate old data (see compatibility layer in <span class="mono">_types.py</span>).</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> Comparison with OpenAI format <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<table class="t">
<tr><th>Scenario</th><th>OpenAI native format</th><th>MAF format</th></tr>
<tr><td>Plain text</td><td><pre class="code">{<span class="st">"role"</span>: <span class="st">"user"</span>,
 <span class="st">"content"</span>: <span class="st">"hi"</span>}</pre></td><td><pre class="code">Message(<span class="st">"user"</span>, <span class="st">"hi"</span>)</pre></td></tr>
<tr><td>Tool call</td><td><pre class="code">{<span class="st">"role"</span>: <span class="st">"assistant"</span>,
 <span class="st">"tool_calls"</span>: [{
   <span class="st">"type"</span>: <span class="st">"function"</span>,
   <span class="st">"function"</span>: {<span class="st">"name"</span>: <span class="st">"get_weather"</span>, ...}
 }]}</pre></td><td><pre class="code">Message(<span class="st">"assistant"</span>, [
  Content.from_function_call(
    name=<span class="st">"get_weather"</span>, ...
  )
])</pre></td></tr>
<tr><td>Tool result</td><td><pre class="code">{<span class="st">"role"</span>: <span class="st">"tool"</span>,
 <span class="st">"content"</span>: <span class="st">"result"</span>,
 <span class="st">"tool_call_id"</span>: <span class="st">"x"</span>}</pre></td><td><pre class="code">Message(<span class="st">"tool"</span>, [
  Content.from_function_result(
    result=<span class="st">"result"</span>, call_id=<span class="st">"x"</span>
  )
])</pre></td></tr>
</table>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Problems with using OpenAI dicts directly:<ul>
        <li><strong>Vendor lock-in</strong>: switching to Anthropic/Ollama/Azure requires extensive changes.</li>
        <li><strong>Scattered fields</strong>: <span class="mono">content</span> / <span class="mono">tool_calls</span> / <span class="mono">tool_call_id</span> at different nesting levels, complex parsing.</li>
        <li><strong>No type safety</strong>: typos only caught at runtime.</li>
        <li><strong>Inconsistent format</strong>: plain text vs image vs tool call use different structures.</li>
      </ul>
      An abstraction layer lets you <strong>write once, run anywhere</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF provides <strong>unified abstraction</strong> with <strong>bidirectional conversion</strong>:<ul>
        <li><span class="mono">BaseChatClient</span> subclasses (like <span class="mono">OpenAIChatClient</span>) auto-convert <span class="mono">Message</span> to vendor format, call API, convert back.</li>
        <li>Conversion is encapsulated inside the client (private <span class="mono">_prepare_messages_for_openai</span>, see <span class="mono">python/packages/openai/agent_framework_openai/_chat_client.py</span>); you rarely call it directly.</li>
        <li><strong>Type safety</strong>: IDE auto-completes <span class="mono">Message(...)</span> / <span class="mono">Content.from_...</span>, catches errors at edit time.</li>
        <li><strong>Testable</strong>: unit tests don't depend on real LLMs, just mock <span class="mono">Message</span>.</li>
      </ul></div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>Use SDK dicts directly</strong>: zero abstraction, but vendor switch requires complete rewrite.</li>
        <li><strong>LangChain MessageType</strong>: provides abstraction, but <span class="mono">HumanMessage</span>/<span class="mono">AIMessage</span>/<span class="mono">ToolMessage</span> classification too granular, increases mental load.</li>
        <li><strong>LlamaIndex ChatMessage</strong>: simple and unified, but limited functionality, weak multimodal/tool support.</li>
        <li>MAF <strong>just right</strong>: one <span class="mono">Message</span> + five <span class="mono">Content</span> types covers all scenarios, seamless vendor switching.</li>
      </ul></div>
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

<details class="accordion">
  <summary><span class="badge-num">1</span> as_agent vs Agent(client=...) 两种创建方式 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="cm"># 方式 A：直接构造</span>
agent_a = Agent(
    client=client,
    name=<span class="st">"MyAgent"</span>,
    instructions=<span class="st">"You are helpful."</span>
)

<span class="cm"># 方式 B：语法糖</span>
agent_b = client.as_agent(
    name=<span class="st">"MyAgent"</span>,
    instructions=<span class="st">"You are helpful."</span>
)

<span class="cm"># 两者完全等价</span>
<span class="kw">assert</span> <span class="fn">type</span>(agent_a) == <span class="fn">type</span>(agent_b)  <span class="cm"># 都是 Agent</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">真实场景中，你可能先创建 <span class="mono">ChatClient</span>（配置好模型、API密钥、重试策略），然后基于它创建多个 Agent（不同人设、不同工具）。两种方式都需要支持：<ul>
        <li><strong>Agent(client=...)</strong>：适合"Agent 是主角"的场景，显式依赖注入。</li>
        <li><strong>client.as_agent(...)</strong>：适合"client 是主角"的场景，链式调用更自然。</li>
      </ul>
      单一方式会让某些代码风格别扭。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">as_agent</span> 是<strong>语法糖</strong>，内部调用 <span class="mono">Agent(client=self, ...)</span>（见 <span class="mono">python/packages/core/agent_framework/_clients.py</span> 的 <span class="mono">BaseChatClient.as_agent</span> 方法）。两种方式返回<strong>同一类型</strong>的对象，行为完全一致。用户可根据上下文选择：<ul>
        <li>测试时 mock Agent：<span class="mono">Agent(client=mock_client, ...)</span></li>
        <li>配置多个 Agent：<span class="mono">agents = [client.as_agent(...) for cfg in configs]</span></li>
      </ul>
      框架不强加风格，但保证语义统一。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>LangChain</strong>：没有 <span class="mono">as_agent</span> 模式，需手动包装 <span class="mono">ChatOpenAI</span> 到 <span class="mono">AgentExecutor</span>。</li>
        <li><strong>Semantic Kernel</strong>：使用 <span class="mono">Kernel</span> 作为容器，Agent 概念较弱。</li>
        <li><strong>OpenAI Assistants API</strong>：Agent 是服务端对象，无本地构造。</li>
        <li>MAF 两种方式都支持，语法糖降低入门门槛，直接构造保留灵活性。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> run() 的参数 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="cm"># 最简：只传消息</span>
result = <span class="kw">await</span> agent.run(<span class="st">"你好"</span>)

<span class="cm"># 带会话：多轮对话</span>
session = agent.create_session()
result = <span class="kw">await</span> agent.run(<span class="st">"我叫 Alice"</span>, session=session)
result = <span class="kw">await</span> agent.run(<span class="st">"我叫什么？"</span>, session=session)

<span class="cm"># 流式：逐块返回</span>
<span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">"讲个故事"</span>, stream=<span class="kw">True</span>):
    <span class="fn">print</span>(chunk.text, end=<span class="st">""</span>)

<span class="cm"># 组合：会话 + 流式</span>
<span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">"继续"</span>, session=session, stream=<span class="kw">True</span>):
    <span class="fn">print</span>(chunk.text, end=<span class="st">""</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">Agent 的使用场景多样：<ul>
        <li><strong>一次性查询</strong>：无状态，只需要答案（如 FAQ bot）。</li>
        <li><strong>多轮对话</strong>：需要记住上文（如客服、助手）。</li>
        <li><strong>流式响应</strong>：实时显示生成过程（UX 需求）。</li>
        <li><strong>组合</strong>：多轮 + 流式（如聊天应用）。</li>
      </ul>
      如果每种场景用不同方法（<span class="mono">run</span>、<span class="mono">run_with_session</span>、<span class="mono">run_stream</span>……），API 膨胀且学习成本高。统一成一个 <span class="mono">run()</span>，用可选参数控制行为，更简洁。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">run()</span> 签名：<pre class="code"><span class="kw">async def</span> <span class="fn">run</span>(
    <span class="kw">self</span>,
    message: str | Message,
    session: AgentSession | <span class="kw">None</span> = <span class="kw">None</span>,
    stream: bool = <span class="kw">False</span>,
    ...
) -> AgentResponse | AsyncIterator[AgentResponseUpdate]:</pre>
      <ul>
        <li><strong>必需参数</strong>只有 <span class="mono">message</span>，其他都是可选。</li>
        <li><strong>session</strong> 默认 <span class="mono">None</span>：不传则无状态，传了则多轮。</li>
        <li><strong>stream</strong> 默认 <span class="mono">False</span>：阻塞返回完整结果；<span class="mono">True</span> 时返回异步迭代器。</li>
        <li>返回类型由 <span class="mono">stream</span> 决定：类型检查器（mypy、Pylance）能推断出正确类型。</li>
      </ul></div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>OpenAI SDK</strong>：<span class="mono">create(...)</span> vs <span class="mono">create(..., stream=True)</span>，但 Assistants API 另有 <span class="mono">runs.create</span>。</li>
        <li><strong>LangChain</strong>：<span class="mono">invoke</span>、<span class="mono">ainvoke</span>、<span class="mono">stream</span>、<span class="mono">astream</span> 四个方法。</li>
        <li><strong>Anthropic SDK</strong>：<span class="mono">messages.create</span> vs <span class="mono">messages.stream</span>。</li>
        <li>MAF <strong>一个方法</strong>，参数控制行为，心智负担最小。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 流式的内部机制 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">"写首诗"</span>, stream=<span class="kw">True</span>):
    <span class="fn">print</span>(<span class="st">f"type={chunk.type}"</span>)      <span class="cm"># "text_delta" / "tool_call" / "final"</span>
    <span class="fn">print</span>(<span class="st">f"text={chunk.text}"</span>)      <span class="cm"># 本块的文本增量</span>
    <span class="fn">print</span>(<span class="st">f"is_final={chunk.is_final}"</span>)  <span class="cm"># 是否最后一块</span>
    
    <span class="kw">if</span> chunk.is_final:
        <span class="fn">print</span>(<span class="st">f"full_response={chunk.response}"</span>)  <span class="cm"># 完整 AgentResponse</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">流式响应不只是"打字机效果"：<ul>
        <li><strong>降低感知延迟</strong>：首字延迟（TTFT）比总耗时更重要。</li>
        <li><strong>长输出场景</strong>：生成几百上千 token 时，用户等不及完整响应。</li>
        <li><strong>中途取消</strong>：用户看到方向不对，立刻停止（节省成本）。</li>
        <li><strong>实时处理</strong>：边生成边解析（如实时翻译、代码高亮）。</li>
      </ul>
      只返回原始文本流不够：需要知道"工具调用开始""最终完成"等事件，才能正确更新 UI。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的流式返回 <span class="mono">AgentResponseUpdate</span> 对象（见 <span class="mono">python/packages/core/agent_framework/_types.py</span>）：<ul>
        <li><strong>type</strong> 字段：<span class="mono">"text_delta"</span>（文本增量）/ <span class="mono">"tool_call"</span>（工具调用）/ <span class="mono">"final"</span>（结束）。</li>
        <li><strong>text</strong> 字段：本块新增的文本。</li>
        <li><strong>is_final</strong>：<span class="mono">True</span> 时是最后一块，<span class="mono">.response</span> 属性包含完整 <span class="mono">AgentResponse</span>。</li>
        <li><strong>元数据</strong>：<span class="mono">usage</span>（token 消耗）、<span class="mono">finish_reason</span>（停止原因）等。</li>
      </ul>
      框架自动累积文本、解析工具调用、处理多轮循环，用户只需 <span class="mono">async for</span> 消费。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>OpenAI SDK</strong>：返回 SSE 事件流，用户需手动解析 <span class="mono">delta</span>、累积文本、判断结束。</li>
        <li><strong>Anthropic SDK</strong>：<span class="mono">MessageStream</span> 对象，事件类型多（<span class="mono">content_block_start</span>、<span class="mono">content_block_delta</span>……），学习曲线陡。</li>
        <li><strong>LangChain</strong>：<span class="mono">astream</span> 返回原始 chunk，格式取决于底层 LLM。</li>
        <li>MAF <strong>统一 Update 对象</strong>，抹平厂商差异，高层语义（"文本增量""工具调用""完成"）清晰。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 多个 Agent 共享一个 client <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code">client = FoundryChatClient(model=<span class="st">"gpt-4o"</span>, api_key=...)

<span class="cm"># 创建多个 Agent，不同人设</span>
weather_agent = client.as_agent(
    name=<span class="st">"WeatherBot"</span>,
    instructions=<span class="st">"You are a weather assistant."</span>,
    tools=[get_weather]
)

translator_agent = client.as_agent(
    name=<span class="st">"Translator"</span>,
    instructions=<span class="st">"Translate to French."</span>
)

support_agent = client.as_agent(
    name=<span class="st">"Support"</span>,
    instructions=<span class="st">"Answer user questions."</span>,
    tools=[search_kb, create_ticket]
)

<span class="cm"># 三个 Agent 复用同一个 HTTP 连接池、API 密钥</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">生产环境常见场景：<ul>
        <li><strong>多角色系统</strong>：一个应用有多个 Agent（路由员、执行员、审核员），都调用同一个模型。</li>
        <li><strong>连接池</strong>：HTTP/2 支持多路复用，一个 TCP 连接可并发多个请求。每个 Agent 独立建连接浪费资源。</li>
        <li><strong>配置复用</strong>：API 密钥、重试策略、超时时间只配置一次。</li>
        <li><strong>监控 / 限流</strong>：所有请求走同一个 client，便于统一埋点、限流。</li>
      </ul>
      如果 Agent 和 ChatClient 耦合（每个 Agent 内部创建 client），无法共享连接。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">ChatClient</span> 是<strong>无状态的</strong>（见 <span class="mono">BaseChatClient</span>）：<ul>
        <li>不持有对话历史（历史在 <span class="mono">AgentSession</span> 里）。</li>
        <li>只负责"发请求 → 解析响应"，可被多个 Agent 并发调用。</li>
        <li>内部用 <span class="mono">httpx.AsyncClient</span>（Python）或 <span class="mono">HttpClient</span>（.NET），自动管理连接池。</li>
        <li><strong>线程安全</strong>（或异步安全）：多个 <span class="mono">await agent.run(...)</span> 可并发执行。</li>
      </ul>
      这种设计让资源利用率最高，也符合依赖注入原则（Agent 依赖 ChatClient 抽象）。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>每个 Agent 内部创建 client</strong>：简单但浪费。OpenAI Assistants API 是服务端 Agent，不存在此问题。</li>
        <li><strong>全局单例 client</strong>：难以测试、难以配置不同环境。</li>
        <li><strong>LangChain</strong>：<span class="mono">ChatOpenAI</span> 可共享，但文档不强调，用户容易每次新建。</li>
        <li>MAF <strong>明确设计</strong>：<span class="mono">client.as_agent(...)</span> 的语法就暗示"多个 agent 共享一个 client"。</li>
      </ul></div>
    </div>
  </div>
</details>

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

<details class="accordion">
  <summary><span class="badge-num">1</span> as_agent vs Agent(client=...) <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="cm"># Approach A: direct construction</span>
agent_a = Agent(
    client=client,
    name=<span class="st">"MyAgent"</span>,
    instructions=<span class="st">"You are helpful."</span>
)

<span class="cm"># Approach B: syntactic sugar</span>
agent_b = client.as_agent(
    name=<span class="st">"MyAgent"</span>,
    instructions=<span class="st">"You are helpful."</span>
)

<span class="cm"># Completely equivalent</span>
<span class="kw">assert</span> <span class="fn">type</span>(agent_a) == <span class="fn">type</span>(agent_b)  <span class="cm"># both Agent</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">In real scenarios, you might first create a <span class="mono">ChatClient</span> (with model config, API keys, retry policies), then derive multiple Agents (different personas, different tools). Both patterns must be supported:<ul>
        <li><strong>Agent(client=...)</strong>: fits "Agent is the protagonist" scenarios, explicit dependency injection.</li>
        <li><strong>client.as_agent(...)</strong>: fits "client is the protagonist" scenarios, method chaining more natural.</li>
      </ul>
      A single pattern makes some code styles awkward.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">as_agent</span> is <strong>syntactic sugar</strong>, internally calling <span class="mono">Agent(client=self, ...)</span> (see <span class="mono">BaseChatClient.as_agent</span> in <span class="mono">python/packages/core/agent_framework/_clients.py</span>). Both patterns return the <strong>same type</strong>, behavior identical. Users can choose based on context:<ul>
        <li>Testing with mocks: <span class="mono">Agent(client=mock_client, ...)</span></li>
        <li>Configuring multiple Agents: <span class="mono">agents = [client.as_agent(...) for cfg in configs]</span></li>
      </ul>
      Framework doesn't force style, but guarantees semantic unity.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>LangChain</strong>: no <span class="mono">as_agent</span> pattern, must manually wrap <span class="mono">ChatOpenAI</span> in <span class="mono">AgentExecutor</span>.</li>
        <li><strong>Semantic Kernel</strong>: uses <span class="mono">Kernel</span> as container, Agent concept weaker.</li>
        <li><strong>OpenAI Assistants API</strong>: Agents are server-side, no local construction.</li>
        <li>MAF supports both: sugar lowers onboarding barrier, direct construction preserves flexibility.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> run() parameters <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="cm"># Minimal: message only</span>
result = <span class="kw">await</span> agent.run(<span class="st">"hello"</span>)

<span class="cm"># With session: multi-turn</span>
session = agent.create_session()
result = <span class="kw">await</span> agent.run(<span class="st">"I'm Alice"</span>, session=session)
result = <span class="kw">await</span> agent.run(<span class="st">"What's my name?"</span>, session=session)

<span class="cm"># Streaming: chunk-by-chunk</span>
<span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">"Tell a story"</span>, stream=<span class="kw">True</span>):
    <span class="fn">print</span>(chunk.text, end=<span class="st">""</span>)

<span class="cm"># Combined: session + streaming</span>
<span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">"Continue"</span>, session=session, stream=<span class="kw">True</span>):
    <span class="fn">print</span>(chunk.text, end=<span class="st">""</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Agent use cases vary:<ul>
        <li><strong>One-shot query</strong>: stateless, just need an answer (FAQ bot).</li>
        <li><strong>Multi-turn conversation</strong>: remember context (customer service, assistant).</li>
        <li><strong>Streaming response</strong>: show generation in real-time (UX need).</li>
        <li><strong>Combined</strong>: multi-turn + streaming (chat app).</li>
      </ul>
      If each scenario uses different methods (<span class="mono">run</span>, <span class="mono">run_with_session</span>, <span class="mono">run_stream</span>…), the API bloats and learning curve steepens. Unifying into one <span class="mono">run()</span> with optional parameters is cleaner.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">run()</span> signature:<pre class="code"><span class="kw">async def</span> <span class="fn">run</span>(
    <span class="kw">self</span>,
    message: str | Message,
    session: AgentSession | <span class="kw">None</span> = <span class="kw">None</span>,
    stream: bool = <span class="kw">False</span>,
    ...
) -> AgentResponse | AsyncIterator[AgentResponseUpdate]:</pre>
      <ul>
        <li><strong>Required param</strong> only <span class="mono">message</span>, everything else optional.</li>
        <li><strong>session</strong> defaults <span class="mono">None</span>: omit for stateless, pass for multi-turn.</li>
        <li><strong>stream</strong> defaults <span class="mono">False</span>: blocking full result; <span class="mono">True</span> returns async iterator.</li>
        <li>Return type determined by <span class="mono">stream</span>: type checkers (mypy, Pylance) infer correctly.</li>
      </ul></div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>OpenAI SDK</strong>: <span class="mono">create(...)</span> vs <span class="mono">create(..., stream=True)</span>, but Assistants API has separate <span class="mono">runs.create</span>.</li>
        <li><strong>LangChain</strong>: <span class="mono">invoke</span>, <span class="mono">ainvoke</span>, <span class="mono">stream</span>, <span class="mono">astream</span> — four methods.</li>
        <li><strong>Anthropic SDK</strong>: <span class="mono">messages.create</span> vs <span class="mono">messages.stream</span>.</li>
        <li>MAF <strong>one method</strong>, parameters control behavior, minimal mental load.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Streaming internals <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="kw">async for</span> chunk <span class="kw">in</span> agent.run(<span class="st">"Write a poem"</span>, stream=<span class="kw">True</span>):
    <span class="fn">print</span>(<span class="st">f"type={chunk.type}"</span>)      <span class="cm"># "text_delta" / "tool_call" / "final"</span>
    <span class="fn">print</span>(<span class="st">f"text={chunk.text}"</span>)      <span class="cm"># text delta for this chunk</span>
    <span class="fn">print</span>(<span class="st">f"is_final={chunk.is_final}"</span>)  <span class="cm"># whether last chunk</span>
    
    <span class="kw">if</span> chunk.is_final:
        <span class="fn">print</span>(<span class="st">f"full_response={chunk.response}"</span>)  <span class="cm"># complete AgentResponse</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Streaming responses aren't just "typewriter effect":<ul>
        <li><strong>Lower perceived latency</strong>: time-to-first-token (TTFT) matters more than total duration.</li>
        <li><strong>Long outputs</strong>: generating hundreds or thousands of tokens, users can't wait for completion.</li>
        <li><strong>Early cancellation</strong>: user sees wrong direction, stops immediately (saves cost).</li>
        <li><strong>Real-time processing</strong>: parse while generating (e.g., live translation, code highlighting).</li>
      </ul>
      Just returning raw text stream isn't enough: need to know "tool call started", "final completion" events to update UI correctly.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF streams <span class="mono">AgentResponseUpdate</span> objects (see <span class="mono">python/packages/core/agent_framework/_types.py</span>):<ul>
        <li><strong>type</strong> field: <span class="mono">"text_delta"</span> (text increment) / <span class="mono">"tool_call"</span> (tool invocation) / <span class="mono">"final"</span> (end).</li>
        <li><strong>text</strong> field: new text in this chunk.</li>
        <li><strong>is_final</strong>: <span class="mono">True</span> for last chunk; <span class="mono">.response</span> property holds complete <span class="mono">AgentResponse</span>.</li>
        <li><strong>Metadata</strong>: <span class="mono">usage</span> (token consumption), <span class="mono">finish_reason</span> (why stopped), etc.</li>
      </ul>
      Framework auto-accumulates text, parses tool calls, handles multi-turn loops; user just <span class="mono">async for</span> consumes.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>OpenAI SDK</strong>: returns SSE event stream, user must manually parse <span class="mono">delta</span>, accumulate text, detect end.</li>
        <li><strong>Anthropic SDK</strong>: <span class="mono">MessageStream</span> object, many event types (<span class="mono">content_block_start</span>, <span class="mono">content_block_delta</span>…), steep learning curve.</li>
        <li><strong>LangChain</strong>: <span class="mono">astream</span> returns raw chunks, format depends on underlying LLM.</li>
        <li>MAF <strong>unified Update object</strong>, abstracts vendor differences, high-level semantics ("text delta", "tool call", "done") clear.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Sharing a client across Agents <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code">client = FoundryChatClient(model=<span class="st">"gpt-4o"</span>, api_key=...)

<span class="cm"># Create multiple Agents, different personas</span>
weather_agent = client.as_agent(
    name=<span class="st">"WeatherBot"</span>,
    instructions=<span class="st">"You are a weather assistant."</span>,
    tools=[get_weather]
)

translator_agent = client.as_agent(
    name=<span class="st">"Translator"</span>,
    instructions=<span class="st">"Translate to French."</span>
)

support_agent = client.as_agent(
    name=<span class="st">"Support"</span>,
    instructions=<span class="st">"Answer user questions."</span>,
    tools=[search_kb, create_ticket]
)

<span class="cm"># All three Agents reuse same HTTP connection pool, API key</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Common production scenarios:<ul>
        <li><strong>Multi-role systems</strong>: one app has multiple Agents (router, executor, reviewer), all calling the same model.</li>
        <li><strong>Connection pooling</strong>: HTTP/2 supports multiplexing, one TCP connection handles concurrent requests. Each Agent creating its own connection wastes resources.</li>
        <li><strong>Config reuse</strong>: API key, retry policies, timeouts configured once.</li>
        <li><strong>Monitoring / rate-limiting</strong>: all requests through one client, unified instrumentation and throttling.</li>
      </ul>
      If Agent and ChatClient are coupled (each Agent internally creates a client), connection sharing is impossible.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">ChatClient</span> is <strong>stateless</strong> (see <span class="mono">BaseChatClient</span>):<ul>
        <li>Doesn't hold conversation history (history lives in <span class="mono">AgentSession</span>).</li>
        <li>Only responsible for "send request → parse response", can be called concurrently by multiple Agents.</li>
        <li>Internally uses <span class="mono">httpx.AsyncClient</span> (Python) or <span class="mono">HttpClient</span> (.NET), auto-manages connection pools.</li>
        <li><strong>Thread-safe</strong> (or async-safe): multiple <span class="mono">await agent.run(...)</span> can execute concurrently.</li>
      </ul>
      This design maximizes resource utilization and follows dependency injection principles (Agent depends on ChatClient abstraction).</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>Each Agent creates internal client</strong>: simple but wasteful. OpenAI Assistants API uses server-side Agents, no such issue.</li>
        <li><strong>Global singleton client</strong>: hard to test, hard to configure different environments.</li>
        <li><strong>LangChain</strong>: <span class="mono">ChatOpenAI</span> can be shared, but docs don't emphasize it; users often create new instances each time.</li>
        <li>MAF <strong>explicit design</strong>: <span class="mono">client.as_agent(...)</span> syntax hints "multiple agents share one client".</li>
      </ul></div>
    </div>
  </div>
</details>

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

<details class="accordion">
  <summary><span class="badge-num">1</span> schema 自动生成原理 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> typing <span class="kw">import</span> Annotated
<span class="kw">from</span> agent_framework <span class="kw">import</span> tool
<span class="kw">from</span> pydantic <span class="kw">import</span> Field

<span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">search_products</span>(
    query: Annotated[str, Field(description=<span class="st">"Search keywords"</span>)],
    max_results: Annotated[int, Field(description=<span class="st">"Max results to return"</span>, ge=1, le=10)] = 5
) -> list[dict]:
    <span class="st">&quot;&quot;&quot;Search for products in the catalog.&quot;&quot;&quot;</span>
    ...

<span class="cm"># 自动生成的 JSON Schema：</span>
<span class="cm"># {</span>
<span class="cm">#   &quot;name&quot;: &quot;search_products&quot;,</span>
<span class="cm">#   &quot;description&quot;: &quot;Search for products in the catalog.&quot;,</span>
<span class="cm">#   &quot;parameters&quot;: {</span>
<span class="cm">#     &quot;type&quot;: &quot;object&quot;,</span>
<span class="cm">#     &quot;properties&quot;: {</span>
<span class="cm">#       &quot;query&quot;: {&quot;type&quot;: &quot;string&quot;, &quot;description&quot;: &quot;Search keywords&quot;},</span>
<span class="cm">#       &quot;max_results&quot;: {&quot;type&quot;: &quot;integer&quot;, &quot;description&quot;: &quot;Max results...&quot;, &quot;minimum&quot;: 1, &quot;maximum&quot;: 10, &quot;default&quot;: 5}</span>
<span class="cm">#     },</span>
<span class="cm">#     &quot;required&quot;: [&quot;query&quot;]</span>
<span class="cm">#   }</span>
<span class="cm"># }</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">模型需要<strong>JSON Schema</strong> 才能理解工具签名：参数名、类型、约束、含义。手写 schema 的问题：<ul>
        <li><strong>易出错</strong>：字段名拼错、类型不匹配、忘记更新 description。</li>
        <li><strong>双重维护</strong>：函数签名改了，schema 要同步改，容易漏。</li>
        <li><strong>无类型检查</strong>：schema 和代码脱节，调用时参数不对只能运行时才发现。</li>
      </ul>
      自动生成让<strong>类型注解 = 单一事实来源</strong>，函数签名即契约。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 用 <strong>Pydantic</strong> 自动生成 schema（见 <span class="mono">python/packages/core/agent_framework/_tools.py</span> 的 <span class="mono">ToolDefinition.from_function</span>）：<ul>
        <li><strong>类型注解</strong> → <span class="mono">type</span> 字段（<span class="mono">str</span> → <span class="mono">"string"</span>，<span class="mono">int</span> → <span class="mono">"integer"</span>……）。</li>
        <li><strong>Field(description=...)</strong> → <span class="mono">description</span> 字段。</li>
        <li><strong>Field(..., ge=1, le=10)</strong> → <span class="mono">minimum</span>/<span class="mono">maximum</span> 约束。</li>
        <li><strong>默认值</strong> → <span class="mono">default</span> 字段，非必需参数。</li>
        <li><strong>Docstring</strong> → 工具的 <span class="mono">description</span>。</li>
      </ul>
      IDE 自动补全、类型检查器（mypy）验证调用，schema 与代码永远同步。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>手写 JSON Schema</strong>：OpenAI SDK 早期做法，容易出错、维护成本高。</li>
        <li><strong>LangChain @tool</strong>：也用 Pydantic，但对复杂类型（嵌套对象、联合类型）支持弱。</li>
        <li><strong>OpenAI function calling JSON</strong>：需手动构造 <span class="mono">{"name": ..., "parameters": {...}}</span>，无类型保证。</li>
        <li>MAF <strong>完全自动</strong>：支持泛型、嵌套、可选参数、约束，生成的 schema 符合各厂商规范。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> approval_mode 三种值 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">get_time</span>() -> str:
    <span class="st">&quot;&quot;&quot;Get current time (safe, always auto-execute).&quot;&quot;&quot;</span>
    <span class="kw">return</span> datetime.now().isoformat()

<span class="nb">@tool</span>(approval_mode=<span class="st">"always_require"</span>)
<span class="kw">def</span> <span class="fn">send_email</span>(to: str, subject: str, body: str) -> str:
    <span class="st">&quot;&quot;&quot;Send an email (requires human approval).&quot;&quot;&quot;</span>
    ...  <span class="cm"># 框架会在执行前要求确认</span>

<span class="nb">@tool</span>(approval_mode=<span class="st">"always_require"</span>)
<span class="kw">def</span> <span class="fn">create_ticket</span>(title: str, priority: str) -> str:
    <span class="st">&quot;&quot;&quot;Create a support ticket (low-priority auto, high requires approval).&quot;&quot;&quot;</span>
    ...  <span class="cm"># 可自定义风险评估逻辑</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">工具能力各异，风险不同：<ul>
        <li><strong>只读查询</strong>（查天气、搜索）：无副作用，可自动执行。</li>
        <li><strong>写操作</strong>（发邮件、删文件、转账）：有副作用，必须人工确认。</li>
        <li><strong>灰色地带</strong>（创建草稿、添加备注）：低风险可自动，高风险需确认。</li>
      </ul>
      如果所有工具都自动执行（<span class="mono">never_require</span>），模型一个幻觉就可能发错邮件、删错数据。如果所有工具都要确认（<span class="mono">always_require</span>），用户体验糟糕（查个天气也要点确认）。需要<strong>分级控制</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的 <span class="mono">approval_mode</span>（见 <span class="mono">python/packages/core/agent_framework/_tools.py</span>）：<ul>
        <li><strong>"never_require"</strong>：无需确认，自动执行（默认）。</li>
        <li><strong>"always_require"</strong>：每次都弹出确认对话框 / 回调，用户批准后才执行。</li>
      </ul>
      审批流程由 <span class="mono">approval logic</span> 接口定义（见 <span class="mono">_tools.py</span>），可自定义（如接入 Slack 审批机器人、钉钉审批流）。框架在工具执行前自动拦截，无需在工具函数内写审批逻辑。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>LangChain HumanApprovalCallbackHandler</strong>：通过回调实现，但需手动注册到每个 Agent，容易漏。</li>
        <li><strong>手动在工具内判断</strong>：<span class="mono">if dangerous: ask_user(); ...</span>，把审批逻辑和业务逻辑耦合。</li>
        <li><strong>OpenAI function calling</strong>：无内置审批，需应用层拦截 <span class="mono">function_call</span> 自行处理。</li>
        <li>MAF <strong>声明式审批</strong>：<span class="mono">@tool(approval_mode=...)</span> 一行搞定，审批逻辑与工具解耦，可插拔策略。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 异步工具 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="kw">import</span> httpx

<span class="cm"># 同步工具（阻塞 I/O）</span>
<span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">get_weather_sync</span>(city: str) -> str:
    <span class="st">&quot;&quot;&quot;Get weather (blocks event loop).&quot;&quot;&quot;</span>
    resp = httpx.get(<span class="st">f"https://api.weather.com?q={city}"</span>)  <span class="cm"># 阻塞！</span>
    <span class="kw">return</span> resp.json()[<span class="st">"temp"</span>]

<span class="cm"># 异步工具（非阻塞）</span>
<span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">async def</span> <span class="fn">get_weather_async</span>(city: str) -> str:
    <span class="st">&quot;&quot;&quot;Get weather (async, doesn't block).&quot;&quot;&quot;</span>
    <span class="kw">async with</span> httpx.AsyncClient() <span class="kw">as</span> client:
        resp = <span class="kw">await</span> client.get(<span class="st">f"https://api.weather.com?q={city}"</span>)
        <span class="kw">return</span> resp.json()[<span class="st">"temp"</span>]

<span class="cm"># Agent 自动处理：sync 用 run_in_executor，async 直接 await</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">工具常做 I/O：<ul>
        <li><strong>HTTP 请求</strong>：调第三方 API（天气、地图、支付）。</li>
        <li><strong>数据库查询</strong>：读用户信息、订单历史。</li>
        <li><strong>文件读写</strong>：读配置、写日志。</li>
      </ul>
      同步 I/O 会<strong>阻塞事件循环</strong>：一个工具调用花 2 秒，整个 Agent 卡住 2 秒，无法处理其他请求。异步 I/O 让事件循环继续运转，多个工具调用可并发执行（一个等网络时另一个跑 CPU 任务）。Python 的 <span class="mono">asyncio</span> 和 .NET 的 <span class="mono">Task</span> 都要求异步传染性——<strong>async all the way</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的 <span class="mono">@tool</span> <strong>同时支持同步和异步</strong>（见 <span class="mono">python/packages/core/agent_framework/_tools.py</span> 的 <span class="mono">ToolDefinition.invoke</span>）：<ul>
        <li><strong>同步工具</strong>：框架用 <span class="mono">asyncio.to_thread</span>（或 <span class="mono">run_in_executor</span>）在线程池执行，避免阻塞。</li>
        <li><strong>异步工具</strong>：框架直接 <span class="mono">await</span>，不阻塞事件循环。</li>
        <li><strong>自动检测</strong>：<span class="mono">inspect.iscoroutinefunction(...)</span> 判断是否异步。</li>
        <li><strong>并发执行</strong>：多个工具调用可用 <span class="mono">asyncio.gather</span> 并发（未来支持 parallel tool calls）。</li>
      </ul>
      开发者不用关心同步 / 异步细节，框架保证高效执行。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>LangChain</strong>：<span class="mono">@tool</span> 支持异步，但 <span class="mono">AgentExecutor</span> 的同步 / 异步路径分离，易出错。</li>
        <li><strong>OpenAI SDK</strong>：不管工具同步 / 异步，应用层自己处理。</li>
        <li><strong>同步 only</strong>：简单但性能差，Agent 处理并发请求时会卡住。</li>
        <li>MAF <strong>透明处理</strong>：写同步工具（简单）或异步工具（高效）都行，框架自动优化。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 多个工具配合 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">search_docs</span>(query: str) -> list[str]:
    <span class="st">&quot;&quot;&quot;Search documentation for relevant pages.&quot;&quot;&quot;</span>
    ...

<span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">read_page</span>(page_id: str) -> str:
    <span class="st">&quot;&quot;&quot;Read the full content of a documentation page.&quot;&quot;&quot;</span>
    ...

<span class="nb">@tool</span>(approval_mode=<span class="st">"always_require"</span>)
<span class="kw">def</span> <span class="fn">create_ticket</span>(title: str, description: str) -> str:
    <span class="st">&quot;&quot;&quot;Create a support ticket.&quot;&quot;&quot;</span>
    ...

agent = Agent(
    client=client,
    name=<span class="st">"SupportBot"</span>,
    instructions=<span class="st">"Help users find docs or file tickets."</span>,
    tools=[search_docs, read_page, create_ticket]
)

<span class="cm"># 用户："How do I reset my password?"</span>
<span class="cm"># 模型：调 search_docs("reset password") → 拿到 [page_123, page_456]</span>
<span class="cm"># 模型：调 read_page("page_123") → 读到步骤</span>
<span class="cm"># 模型：回答用户</span>

<span class="cm"># 用户："I still can't log in, please help"</span>
<span class="cm"># 模型：调 create_ticket(...) → 框架弹确认 → 用户批准 → 创建工单</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">真实 Agent 需要<strong>多种能力</strong>：<ul>
        <li><strong>检索</strong>：搜索知识库、数据库、API。</li>
        <li><strong>读写</strong>：读文件、写日志、更新记录。</li>
        <li><strong>计算</strong>：调计算器、运行代码。</li>
        <li><strong>交互</strong>：发邮件、创建工单、调第三方服务。</li>
      </ul>
      单个工具功能有限，多个工具<strong>组合</strong>才能完成复杂任务。模型需要<strong>规划</strong>：先搜索 → 再读取 → 最后创建工单。框架需要支持<strong>多轮工具调用</strong>（一个工具的输出可能触发下一个工具）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的工具循环（见 <span class="mono">python/packages/core/agent_framework/_agents.py</span> 的 <span class="mono">_run_non_streaming</span>）：<ul>
        <li><strong>传所有工具 schema</strong>：Agent 初始化时把所有工具的 JSON Schema 发给模型。</li>
        <li><strong>模型选择工具</strong>：模型根据用户问题决定调哪个（或哪几个）工具，输出 <span class="mono">function_call</span>。</li>
        <li><strong>框架路由执行</strong>：根据 <span class="mono">function_call.name</span> 找到对应 Python 函数，传参调用。</li>
        <li><strong>结果回灌</strong>：把 <span class="mono">function_result</span> 追加进对话历史，模型读取后决定：继续调工具 or 给出最终答案。</li>
        <li><strong>循环直到完成</strong>：最多 <span class="mono">max_tool_rounds</span> 轮（默认 10），防止死循环。</li>
      </ul>
      开发者只需定义工具、把它们传给 Agent，调度和组合由框架完成。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>OpenAI parallel_tool_calls</strong>：支持一次返回多个 tool_call，MAF 未来也会支持（并发执行工具）。</li>
        <li><strong>Anthropic tool_use blocks</strong>：一条消息可包含多个 <span class="mono">tool_use</span>，MAF 已在 <span class="mono">Content.from_function_call</span> 抽象。</li>
        <li><strong>LangChain ToolChain</strong>：需手动编排工具调用顺序（A → B → C），不如让模型自己规划灵活。</li>
        <li>MAF <strong>自动循环 + 模型规划</strong>：给足工具，模型自己组合，框架保证安全执行（审批 + 轮数限制）。</li>
      </ul></div>
    </div>
  </div>
</details>

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

<details class="accordion">
  <summary><span class="badge-num">1</span> Auto schema generation <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> typing <span class="kw">import</span> Annotated
<span class="kw">from</span> agent_framework <span class="kw">import</span> tool
<span class="kw">from</span> pydantic <span class="kw">import</span> Field

<span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">search_products</span>(
    query: Annotated[str, Field(description=<span class="st">"Search keywords"</span>)],
    max_results: Annotated[int, Field(description=<span class="st">"Max results to return"</span>, ge=1, le=10)] = 5
) -> list[dict]:
    <span class="st">&quot;&quot;&quot;Search for products in the catalog.&quot;&quot;&quot;</span>
    ...

<span class="cm"># Auto-generated JSON Schema:</span>
<span class="cm"># {</span>
<span class="cm">#   &quot;name&quot;: &quot;search_products&quot;,</span>
<span class="cm">#   &quot;description&quot;: &quot;Search for products in the catalog.&quot;,</span>
<span class="cm">#   &quot;parameters&quot;: {</span>
<span class="cm">#     &quot;type&quot;: &quot;object&quot;,</span>
<span class="cm">#     &quot;properties&quot;: {</span>
<span class="cm">#       &quot;query&quot;: {&quot;type&quot;: &quot;string&quot;, &quot;description&quot;: &quot;Search keywords&quot;},</span>
<span class="cm">#       &quot;max_results&quot;: {&quot;type&quot;: &quot;integer&quot;, &quot;description&quot;: &quot;Max results...&quot;, &quot;minimum&quot;: 1, &quot;maximum&quot;: 10, &quot;default&quot;: 5}</span>
<span class="cm">#     },</span>
<span class="cm">#     &quot;required&quot;: [&quot;query&quot;]</span>
<span class="cm">#   }</span>
<span class="cm"># }</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Models need <strong>JSON Schema</strong> to understand tool signatures: parameter names, types, constraints, meanings. Problems with hand-written schemas:<ul>
        <li><strong>Error-prone</strong>: field name typos, type mismatches, forgotten description updates.</li>
        <li><strong>Double maintenance</strong>: function signature changes, schema must sync, easy to miss.</li>
        <li><strong>No type checking</strong>: schema and code diverge, wrong arguments only caught at runtime.</li>
      </ul>
      Auto-generation makes <strong>type annotations = single source of truth</strong>, function signature is the contract.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF uses <strong>Pydantic</strong> to auto-generate schemas (see <span class="mono">ToolDefinition.from_function</span> in <span class="mono">python/packages/core/agent_framework/_tools.py</span>):<ul>
        <li><strong>Type annotations</strong> → <span class="mono">type</span> field (<span class="mono">str</span> → <span class="mono">"string"</span>, <span class="mono">int</span> → <span class="mono">"integer"</span>…).</li>
        <li><strong>Field(description=...)</strong> → <span class="mono">description</span> field.</li>
        <li><strong>Field(..., ge=1, le=10)</strong> → <span class="mono">minimum</span>/<span class="mono">maximum</span> constraints.</li>
        <li><strong>Default values</strong> → <span class="mono">default</span> field, optional parameters.</li>
        <li><strong>Docstring</strong> → tool's <span class="mono">description</span>.</li>
      </ul>
      IDE autocomplete, type checkers (mypy) validate calls, schema and code always in sync.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>Hand-written JSON Schema</strong>: early OpenAI SDK approach, error-prone, high maintenance.</li>
        <li><strong>LangChain @tool</strong>: also uses Pydantic, but weak support for complex types (nested objects, unions).</li>
        <li><strong>OpenAI function calling JSON</strong>: manual construction of <span class="mono">{"name": ..., "parameters": {...}}</span>, no type safety.</li>
        <li>MAF <strong>fully automatic</strong>: supports generics, nesting, optional params, constraints; generated schema matches all vendor specs.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Approval modes <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">get_time</span>() -> str:
    <span class="st">&quot;&quot;&quot;Get current time (safe, always auto-execute).&quot;&quot;&quot;</span>
    <span class="kw">return</span> datetime.now().isoformat()

<span class="nb">@tool</span>(approval_mode=<span class="st">"always_require"</span>)
<span class="kw">def</span> <span class="fn">send_email</span>(to: str, subject: str, body: str) -> str:
    <span class="st">&quot;&quot;&quot;Send an email (requires human approval).&quot;&quot;&quot;</span>
    ...  <span class="cm"># framework requests confirmation before execution</span>

<span class="nb">@tool</span>(approval_mode=<span class="st">"always_require"</span>)
<span class="kw">def</span> <span class="fn">create_ticket</span>(title: str, priority: str) -> str:
    <span class="st">&quot;&quot;&quot;Create a ticket (low-priority auto, high requires approval).&quot;&quot;&quot;</span>
    ...  <span class="cm"># can customize risk assessment logic</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Tools vary in capability and risk:<ul>
        <li><strong>Read-only queries</strong> (check weather, search): no side effects, can auto-execute.</li>
        <li><strong>Write operations</strong> (send email, delete files, transfer money): have side effects, must require human confirmation.</li>
        <li><strong>Gray area</strong> (create draft, add note): low-risk can auto, high-risk needs confirmation.</li>
      </ul>
      If all tools auto-execute (<span class="mono">never_require</span>), one model hallucination could send wrong emails, delete wrong data. If all tools require confirmation (<span class="mono">always_require</span>), UX is terrible (confirming even weather lookups). Need <strong>tiered control</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's <span class="mono">approval_mode</span> (see <span class="mono">python/packages/core/agent_framework/_tools.py</span>):<ul>
        <li><strong>"never_require"</strong>: no confirmation, auto-execute (default).</li>
        <li><strong>"always_require"</strong>: pop confirmation dialog / callback every time, execute only after user approval.</li>
      </ul>
      Approval flow defined by <span class="mono">approval logic</span> interface (see <span class="mono">_tools.py</span>), customizable (e.g., integrate Slack approval bot, DingTalk approval flow). Framework auto-intercepts before tool execution, no need to write approval logic inside tool functions.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>LangChain HumanApprovalCallbackHandler</strong>: implemented via callbacks, but must manually register to each Agent, easy to miss.</li>
        <li><strong>Manual checks in tools</strong>: <span class="mono">if dangerous: ask_user(); ...</span>, couples approval logic with business logic.</li>
        <li><strong>OpenAI function calling</strong>: no built-in approval, application layer must intercept <span class="mono">function_call</span> and handle.</li>
        <li>MAF <strong>declarative approval</strong>: one line <span class="mono">@tool(approval_mode=...)</span>, approval logic decoupled from tools, pluggable strategies.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Async tools <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="kw">import</span> httpx

<span class="cm"># Sync tool (blocks event loop)</span>
<span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">get_weather_sync</span>(city: str) -> str:
    <span class="st">&quot;&quot;&quot;Get weather (blocks event loop).&quot;&quot;&quot;</span>
    resp = httpx.get(<span class="st">f"https://api.weather.com?q={city}"</span>)  <span class="cm"># blocking!</span>
    <span class="kw">return</span> resp.json()[<span class="st">"temp"</span>]

<span class="cm"># Async tool (non-blocking)</span>
<span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">async def</span> <span class="fn">get_weather_async</span>(city: str) -> str:
    <span class="st">&quot;&quot;&quot;Get weather (async, doesn't block).&quot;&quot;&quot;</span>
    <span class="kw">async with</span> httpx.AsyncClient() <span class="kw">as</span> client:
        resp = <span class="kw">await</span> client.get(<span class="st">f"https://api.weather.com?q={city}"</span>)
        <span class="kw">return</span> resp.json()[<span class="st">"temp"</span>]

<span class="cm"># Agent auto-handles: sync via run_in_executor, async via direct await</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Tools often do I/O:<ul>
        <li><strong>HTTP requests</strong>: calling third-party APIs (weather, maps, payments).</li>
        <li><strong>Database queries</strong>: reading user info, order history.</li>
        <li><strong>File I/O</strong>: reading config, writing logs.</li>
      </ul>
      Synchronous I/O <strong>blocks the event loop</strong>: one tool call taking 2 seconds freezes the entire Agent for 2 seconds, can't handle other requests. Async I/O lets the event loop continue, multiple tool calls can execute concurrently (one waiting on network while another runs CPU tasks). Python's <span class="mono">asyncio</span> and .NET's <span class="mono">Task</span> both require async contagion — <strong>async all the way</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's <span class="mono">@tool</span> <strong>supports both sync and async</strong> (see <span class="mono">ToolDefinition.invoke</span> in <span class="mono">python/packages/core/agent_framework/_tools.py</span>):<ul>
        <li><strong>Sync tools</strong>: framework uses <span class="mono">asyncio.to_thread</span> (or <span class="mono">run_in_executor</span>) to run in thread pool, avoiding blocking.</li>
        <li><strong>Async tools</strong>: framework directly <span class="mono">await</span>s, doesn't block event loop.</li>
        <li><strong>Auto-detection</strong>: <span class="mono">inspect.iscoroutinefunction(...)</span> determines if async.</li>
        <li><strong>Concurrent execution</strong>: multiple tool calls can use <span class="mono">asyncio.gather</span> for concurrency (future support for parallel tool calls).</li>
      </ul>
      Developers don't care about sync/async details; framework ensures efficient execution.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>LangChain</strong>: <span class="mono">@tool</span> supports async, but <span class="mono">AgentExecutor</span>'s sync/async paths separated, easy to get wrong.</li>
        <li><strong>OpenAI SDK</strong>: doesn't care if tools are sync/async, application layer handles it.</li>
        <li><strong>Sync only</strong>: simple but poor performance, Agent handling concurrent requests will block.</li>
        <li>MAF <strong>transparent handling</strong>: write sync tools (simple) or async tools (efficient), framework auto-optimizes.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Multiple tools together <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">search_docs</span>(query: str) -> list[str]:
    <span class="st">&quot;&quot;&quot;Search documentation for relevant pages.&quot;&quot;&quot;</span>
    ...

<span class="nb">@tool</span>(approval_mode=<span class="st">"never_require"</span>)
<span class="kw">def</span> <span class="fn">read_page</span>(page_id: str) -> str:
    <span class="st">&quot;&quot;&quot;Read the full content of a documentation page.&quot;&quot;&quot;</span>
    ...

<span class="nb">@tool</span>(approval_mode=<span class="st">"always_require"</span>)
<span class="kw">def</span> <span class="fn">create_ticket</span>(title: str, description: str) -> str:
    <span class="st">&quot;&quot;&quot;Create a support ticket.&quot;&quot;&quot;</span>
    ...

agent = Agent(
    client=client,
    name=<span class="st">"SupportBot"</span>,
    instructions=<span class="st">"Help users find docs or file tickets."</span>,
    tools=[search_docs, read_page, create_ticket]
)

<span class="cm"># User: "How do I reset my password?"</span>
<span class="cm"># Model: calls search_docs("reset password") → gets [page_123, page_456]</span>
<span class="cm"># Model: calls read_page("page_123") → reads steps</span>
<span class="cm"># Model: answers user</span>

<span class="cm"># User: "I still can't log in, please help"</span>
<span class="cm"># Model: calls create_ticket(...) → framework pops confirmation → user approves → ticket created</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Real Agents need <strong>multiple capabilities</strong>:<ul>
        <li><strong>Retrieval</strong>: search knowledge base, database, API.</li>
        <li><strong>Read/write</strong>: read files, write logs, update records.</li>
        <li><strong>Computation</strong>: call calculator, run code.</li>
        <li><strong>Interaction</strong>: send emails, create tickets, call third-party services.</li>
      </ul>
      Single tools are limited; multiple tools <strong>combined</strong> complete complex tasks. Model needs to <strong>plan</strong>: search first → then read → finally create ticket. Framework needs to support <strong>multi-round tool calls</strong> (one tool's output may trigger the next).</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's tool loop (see <span class="mono">_run_non_streaming</span> in <span class="mono">python/packages/core/agent_framework/_agents.py</span>):<ul>
        <li><strong>Pass all tool schemas</strong>: on Agent init, all tools' JSON Schemas sent to model.</li>
        <li><strong>Model selects tools</strong>: model decides which tool(s) to call based on user question, outputs <span class="mono">function_call</span>.</li>
        <li><strong>Framework routes execution</strong>: based on <span class="mono">function_call.name</span>, finds corresponding Python function, calls with args.</li>
        <li><strong>Feed back results</strong>: appends <span class="mono">function_result</span> to conversation history; model reads and decides: call more tools or give final answer.</li>
        <li><strong>Loop until done</strong>: max <span class="mono">max_tool_rounds</span> (default 10), prevents infinite loops.</li>
      </ul>
      Developers just define tools, pass them to Agent; scheduling and composition done by framework.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>OpenAI parallel_tool_calls</strong>: supports returning multiple tool_calls at once, MAF will support in future (concurrent tool execution).</li>
        <li><strong>Anthropic tool_use blocks</strong>: one message can contain multiple <span class="mono">tool_use</span>, MAF already abstracts in <span class="mono">Content.from_function_call</span>.</li>
        <li><strong>LangChain ToolChain</strong>: must manually orchestrate tool call order (A → B → C), less flexible than letting model plan.</li>
        <li>MAF <strong>auto-loop + model planning</strong>: provide tools, model composes them, framework ensures safe execution (approval + round limits).</li>
      </ul></div>
    </div>
  </div>
</details>

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

<details class="accordion">
  <summary><span class="badge-num">1</span> create_session vs 不传 session <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="cm"># 不传 session：每次都是新对话（失忆）</span>
result1 = <span class="kw">await</span> agent.run(<span class="st">"我叫 Alice"</span>)
result2 = <span class="kw">await</span> agent.run(<span class="st">"我叫什么？"</span>)
<span class="cm"># → 模型不知道，之前的"Alice"已丢失</span>

<span class="cm"># 传 session：记住上下文</span>
session = agent.create_session()
result1 = <span class="kw">await</span> agent.run(<span class="st">"我叫 Alice"</span>, session=session)
result2 = <span class="kw">await</span> agent.run(<span class="st">"我叫什么？"</span>, session=session)
<span class="cm"># → 模型回答"Alice"</span>

<span class="cm"># 查看会话历史</span>
<span class="fn">print</span>(session.history)  <span class="cm"># [Message("user", "我叫 Alice"), Message("assistant", ...), ...]</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">许多 AI 应用需要<strong>上下文连续性</strong>：<ul>
        <li><strong>对话式 UI</strong>：用户问"天气怎样？" → "明天呢？" → "后天呢？"，每句都依赖前文。</li>
        <li><strong>任务流</strong>：用户说"帮我订酒店" → 模型问"哪个城市？" → "西雅图" → "几号入住？"，需保持状态。</li>
        <li><strong>个性化</strong>：用户说"我喜欢素食"，后续对话记得这点。</li>
      </ul>
      如果默认<strong>有状态</strong>（隐式全局 session），会导致：不同用户的对话串了、测试时难以隔离、并发请求互相干扰。MAF 选择<strong>无状态为默认</strong>，需要状态时显式传 <span class="mono">session</span>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">AgentSession</span>（见 <span class="mono">python/packages/core/agent_framework/_sessions.py</span>）：<ul>
        <li><strong>显式创建</strong>：<span class="mono">agent.create_session()</span> 返回一个新会话对象。</li>
        <li><strong>透传</strong>：把同一个 <span class="mono">session</span> 对象传给每次 <span class="mono">run()</span>。</li>
        <li><strong>自动累积</strong>：每次 <span class="mono">run</span> 后，用户消息 + 模型回复（+ 工具调用/结果）自动追加进 <span class="mono">session.history</span>。</li>
        <li><strong>无副作用</strong>：不传 <span class="mono">session</span> 时，<span class="mono">run</span> 不改任何全局状态，完全无状态。</li>
      </ul>
      这种设计让<strong>并发安全</strong>（多个用户各自的 session 互不干扰）、<strong>可测试</strong>（每个测试用例独立 session）、<strong>易理解</strong>（有没有记忆一目了然）。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>OpenAI Assistants API</strong>：用 <span class="mono">thread_id</span> 标识会话，服务端管理历史。优点是无需客户端存储，缺点是无法本地调试、换厂商需重构。</li>
        <li><strong>LangChain Memory</strong>：用 <span class="mono">ConversationBufferMemory</span> 等类，需手动挂到 <span class="mono">Chain</span>。容易忘记清空，导致历史累积过长。</li>
        <li><strong>隐式全局 session</strong>：框架内部维护 session 字典（user_id → history），简化 API 但并发不安全、难测试。</li>
        <li>MAF <strong>显式 session 对象</strong>：清晰、安全、可控。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> ContextProvider 的工作流 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent, MemoryContextProvider

<span class="cm"># 创建一个记忆提供者：在每次 run 前注入相关记忆</span>
memory_provider = MemoryContextProvider(
    memory_store=...,  <span class="cm"># 向量数据库 / Redis / 其他存储</span>
    relevance_threshold=0.7
)

agent = Agent(
    client=client,
    name=<span class="st">"Assistant"</span>,
    context_providers=[memory_provider],  <span class="cm"># 挂载</span>
)

<span class="cm"># 用户首次说"我喜欢爬山"</span>
session = agent.create_session()
<span class="kw">await</span> agent.run(<span class="st">"我喜欢爬山"</span>, session=session)
<span class="cm"># → MemoryContextProvider 把"用户喜欢爬山"存入记忆库</span>

<span class="cm"># 几天后，新会话</span>
session2 = agent.create_session()
<span class="kw">await</span> agent.run(<span class="st">"推荐周末活动"</span>, session=session2)
<span class="cm"># → MemoryContextProvider 检索到"喜欢爬山"，注入上下文</span>
<span class="cm"># → 模型回答时会考虑这条记忆</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a"><span class="mono">AgentSession</span> 只在<strong>单次对话</strong>内记忆，对话结束后历史就没了。真实应用需要<strong>跨会话记忆</strong>：<ul>
        <li><strong>用户偏好</strong>：用户说"我对海鲜过敏"，所有后续会话都要记得。</li>
        <li><strong>RAG（检索增强生成）</strong>：用户问"公司休假政策？"，从文档库检索相关段落，注入上下文。</li>
        <li><strong>个性化</strong>：根据用户历史交互（问过什么、喜欢什么）调整回答风格。</li>
      </ul>
      把这些逻辑硬编码在 <span class="mono">instructions</span> 或手动拼进每条消息，既繁琐又不可扩展。需要<strong>可插拔的上下文注入机制</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">ContextProvider</span> 接口（见 <span class="mono">python/packages/core/agent_framework/</span>）：<ul>
        <li><strong>在每次 run 前调用</strong>：Agent 执行时，遍历 <span class="mono">context_providers</span> 列表，调用每个 provider 的 <span class="mono">provide_context(...)</span>。</li>
        <li><strong>返回消息 / 内容</strong>：provider 可返回 <span class="mono">Message</span> 列表（注入历史对话）、<span class="mono">Content</span> 列表（注入文档片段）、或修改 system prompt。</li>
        <li><strong>内置实现</strong>：<span class="mono">MemoryContextProvider</span>（向量检索记忆）、<span class="mono">InMemoryHistoryProvider</span>（跨会话历史）、<span class="mono">DocumentContextProvider</span>（文档 RAG）。</li>
        <li><strong>可组合</strong>：多个 provider 按顺序执行，可同时用记忆 + 文档检索 + 用户偏好。</li>
      </ul>
      这种设计让上下文逻辑<strong>解耦</strong>，Agent 不关心"记忆从哪来"，只管"有这些上下文"。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>LangChain Memory</strong>：<span class="mono">ConversationBufferMemory</span>、<span class="mono">ConversationSummaryMemory</span> 等，但和 Chain 耦合，不易切换存储后端。</li>
        <li><strong>LlamaIndex chat memory</strong>：专注向量检索，但不支持其他类型上下文（如用户偏好、文档片段）。</li>
        <li><strong>手动拼接</strong>：在 <span class="mono">run</span> 前手动查询记忆库、拼进消息列表，重复代码多、易出错。</li>
        <li>MAF <strong>接口抽象 + 内置实现</strong>：开箱即用的 provider，也可自定义（如接入企业知识图谱）。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 会话存储后端 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="cm"># 开发环境：内存存储（进程重启后丢失）</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> InMemoryHistoryProvider
history = InMemoryHistoryProvider()

<span class="cm"># 生产环境：Redis 存储（持久化 + 分布式）</span>
<span class="kw">from</span> agent_framework.redis <span class="kw">import</span> RedisHistoryProvider
history = RedisHistoryProvider(redis_url=<span class="st">"redis://localhost:6379"</span>)

<span class="cm"># Azure：Cosmos DB 存储</span>
<span class="kw">from</span> agent_framework.azure <span class="kw">import</span> CosmosHistoryProvider
history = CosmosHistoryProvider(
    endpoint=<span class="st">"https://..."</span>,
    credential=<span class="st">"..."</span>,
    database_name=<span class="st">"agents"</span>,
    container_name=<span class="st">"sessions"</span>
)

<span class="cm"># Agent 使用存储（作为 context provider 注入）</span>
agent = Agent(client=client, context_providers=[history])
session = agent.create_session(session_id=<span class="st">"user_123_conv_456"</span>)
<span class="cm"># 历史自动存到后端，下次加载时恢复</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">不同环境对存储的需求不同：<ul>
        <li><strong>开发 / 测试</strong>：内存存储即可，快速、无需配置。</li>
        <li><strong>单机生产</strong>：文件存储（SQLite、JSON），简单持久化。</li>
        <li><strong>分布式生产</strong>：Redis / Cosmos / DynamoDB，多实例共享状态、高可用。</li>
        <li><strong>合规 / 审计</strong>：需存进企业数据库（PostgreSQL / MongoDB），便于查询、归档。</li>
      </ul>
      如果存储逻辑和 Agent 耦合（硬编码用 Redis），切换环境需改代码、难以测试。需要<strong>抽象存储接口</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">HistoryProvider</span> 接口（继承自 <span class="mono">ContextProvider</span>，见 <span class="mono">python/packages/core/agent_framework/_sessions.py</span>）：<ul>
        <li><strong>抽象接口</strong>：子类实现 <span class="mono">get_messages</span> / <span class="mono">save_messages</span>，Agent 通过 <span class="mono">context_providers</span> 依赖接口。</li>
        <li><strong>多种实现</strong>：<ul>
          <li><span class="mono">InMemoryHistoryProvider</span>：开发用，内存存储。</li>
          <li><span class="mono">RedisHistoryProvider</span>：生产用，Redis 存储（<span class="mono">agent_framework.redis</span>）。</li>
          <li><span class="mono">CosmosHistoryProvider</span>：Azure 用户，Cosmos DB 存储（<span class="mono">agent_framework.azure</span>）。</li>
          <li><span class="mono">FileHistoryProvider</span>：单机，JSON 文件存储。</li>
        </ul></li>
        <li><strong>序列化自动</strong>：<span class="mono">Message.to_dict()</span> 转 JSON，存进后端；加载时 <span class="mono">from_dict</span> 恢复。</li>
        <li><strong>可扩展</strong>：自定义后端（如接入 PostgreSQL、MongoDB）只需继承 <span class="mono">HistoryProvider</span>。</li>
      </ul></div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>LangChain</strong>：<span class="mono">RedisChatMessageHistory</span>、<span class="mono">FileChatMessageHistory</span> 等，但和 Memory 类耦合，切换存储需改 Memory 初始化。</li>
        <li><strong>OpenAI Assistants</strong>：服务端管理，开发者无法选择存储后端、无法本地调试。</li>
        <li><strong>手动序列化</strong>：自己写 <span class="mono">json.dump(history, file)</span>，重复代码多、容易出错（忘记处理工具调用等复杂内容）。</li>
        <li>MAF <strong>接口 + 多实现</strong>：开发用内存、生产切 Redis，只改一行配置。</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> context window 压缩 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> (
    CompactionProvider,
    SlidingWindowStrategy,
    SummarizationStrategy,
    ContextWindowCompactionStrategy,
)

<span class="cm"># 策略 A：滑动窗口（保留最近 N 组消息，丢弃最老的）</span>
strategy = SlidingWindowStrategy(keep_last_groups=20, preserve_system=<span class="kw">True</span>)

<span class="cm"># 策略 B：摘要压缩（用 LLM 把老消息总结，需传入 client）</span>
strategy = SummarizationStrategy(client=client, target_count=4)

<span class="cm"># 策略 C：按上下文窗口 token 预算压缩（两阶段：工具结果驱逐 + 截断）</span>
strategy = ContextWindowCompactionStrategy(
    max_context_window_tokens=128_000,
    max_output_tokens=16_384,
)

<span class="cm"># 用 CompactionProvider 包装策略，作为 context provider 注入</span>
compaction = CompactionProvider(before_strategy=strategy)
agent = Agent(
    client=client,
    context_providers=[compaction]
)

<span class="cm"># 对话增长时，框架在每轮前自动按策略压缩</span>
session = agent.create_session()
<span class="kw">for</span> i <span class="kw">in</span> <span class="fn">range</span>(30):
    <span class="kw">await</span> agent.run(<span class="st">f"第 {i} 条消息"</span>, session=session)
    <span class="cm"># → 超出阈值时策略生效：丢弃最老的组或生成摘要</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">对话历史会<strong>无限增长</strong>，问题：<ul>
        <li><strong>token 限制</strong>：模型有 context window 上限（如 GPT-4 128k tokens），超过就报错或截断。</li>
        <li><strong>成本</strong>：输入 token 也计费，历史越长、每次调用越贵。</li>
        <li><strong>延迟</strong>：发送和处理更多 token 增加延迟。</li>
        <li><strong>相关性衰减</strong>：50 轮前的对话可能和当前问题无关，但仍占用 context。</li>
      </ul>
      需要<strong>自动压缩策略</strong>：在不丢失关键信息的前提下，控制 context 大小。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 内置多种压缩策略（<span class="mono">SlidingWindowStrategy</span> / <span class="mono">SummarizationStrategy</span> / <span class="mono">ContextWindowCompactionStrategy</span>，见 <span class="mono">_compaction.py</span>）：<ul>
        <li><strong>滑动窗口</strong>：保留最近 N 条消息，删掉最老的（适合短期对话）。</li>
        <li><strong>摘要压缩</strong>：把老消息总结成一条 system 消息（<span class="st">"之前用户提到……"</span>），保留语义、减少 token。</li>
        <li><strong>混合策略</strong>：保留 system 消息（重要指令）+ 最近消息（当前上下文）+ 摘要中间消息。</li>
        <li><strong>自动触发</strong>：Agent 在 <span class="mono">run</span> 前检查历史长度，超过阈值时调用策略压缩。</li>
        <li><strong>可配置</strong>：<span class="mono">keep_last_groups</span>、<span class="mono">target_count</span>、<span class="mono">max_context_window_tokens</span> 等参数都可调。</li>
      </ul>
      开发者无需手动管理 context，框架自动优化。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><ul>
        <li><strong>LangChain ConversationSummaryMemory</strong>：每次对话后调 LLM 生成摘要，但开销大、时机不灵活。</li>
        <li><strong>手动截断</strong>：<span class="mono">messages[-10:]</span> 只取最后 10 条，简单但丢失早期重要信息。</li>
        <li><strong>向量检索</strong>：把历史存进向量库，每次检索相关片段，但需额外基础设施。</li>
        <li>MAF <strong>多策略可选</strong>：简单场景用滑动窗口，复杂场景用摘要，还可组合 ContextProvider 做向量检索。</li>
      </ul></div>
    </div>
  </div>
</details>

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

<details class="accordion">
  <summary><span class="badge-num">1</span> With vs without session <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="cm"># Without session: each call is a new conversation (amnesiac)</span>
result1 = <span class="kw">await</span> agent.run(<span class="st">"I'm Alice"</span>)
result2 = <span class="kw">await</span> agent.run(<span class="st">"What's my name?"</span>)
<span class="cm"># → Model doesn't know; previous "Alice" is lost</span>

<span class="cm"># With session: remembers context</span>
session = agent.create_session()
result1 = <span class="kw">await</span> agent.run(<span class="st">"I'm Alice"</span>, session=session)
result2 = <span class="kw">await</span> agent.run(<span class="st">"What's my name?"</span>, session=session)
<span class="cm"># → Model answers "Alice"</span>

<span class="cm"># View session history</span>
<span class="fn">print</span>(session.history)  <span class="cm"># [Message("user", "I'm Alice"), Message("assistant", ...), ...]</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Many AI apps need <strong>context continuity</strong>:<ul>
        <li><strong>Conversational UI</strong>: user asks "What's the weather?" → "Tomorrow?" → "Day after?", each relies on prior turns.</li>
        <li><strong>Task flows</strong>: user says "Book me a hotel" → model asks "Which city?" → "Seattle" → "Check-in date?", needs to maintain state.</li>
        <li><strong>Personalization</strong>: user says "I'm vegetarian", later conversations remember this.</li>
      </ul>
      If default is <strong>stateful</strong> (implicit global session), you get: different users' conversations mixed, tests hard to isolate, concurrent requests interfere. MAF chooses <strong>stateless as default</strong>, explicit <span class="mono">session</span> when needed.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">AgentSession</span> (see <span class="mono">python/packages/core/agent_framework/_sessions.py</span>):<ul>
        <li><strong>Explicit creation</strong>: <span class="mono">agent.create_session()</span> returns a new session object.</li>
        <li><strong>Pass-through</strong>: pass the same <span class="mono">session</span> object to each <span class="mono">run()</span>.</li>
        <li><strong>Auto-accumulation</strong>: after each <span class="mono">run</span>, user message + model reply (+ tool calls/results) auto-append to <span class="mono">session.history</span>.</li>
        <li><strong>No side effects</strong>: without <span class="mono">session</span>, <span class="mono">run</span> mutates no global state, fully stateless.</li>
      </ul>
      This design ensures <strong>concurrent safety</strong> (each user's session doesn't interfere), <strong>testability</strong> (each test has independent session), <strong>understandability</strong> (memory or not is obvious).</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>OpenAI Assistants API</strong>: uses <span class="mono">thread_id</span> to identify sessions, server-managed history. Pros: no client storage. Cons: can't debug locally, vendor switch requires refactor.</li>
        <li><strong>LangChain Memory</strong>: uses <span class="mono">ConversationBufferMemory</span> classes, must manually attach to <span class="mono">Chain</span>. Easy to forget to clear, causing history bloat.</li>
        <li><strong>Implicit global session</strong>: framework internally maintains session dict (user_id → history), simplifies API but concurrency-unsafe, hard to test.</li>
        <li>MAF <strong>explicit session object</strong>: clear, safe, controllable.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> ContextProvider workflow <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent, MemoryContextProvider

<span class="cm"># Create a memory provider: injects relevant memories before each run</span>
memory_provider = MemoryContextProvider(
    memory_store=...,  <span class="cm"># vector DB / Redis / other storage</span>
    relevance_threshold=0.7
)

agent = Agent(
    client=client,
    name=<span class="st">"Assistant"</span>,
    context_providers=[memory_provider],  <span class="cm"># attach</span>
)

<span class="cm"># User first says "I love hiking"</span>
session = agent.create_session()
<span class="kw">await</span> agent.run(<span class="st">"I love hiking"</span>, session=session)
<span class="cm"># → MemoryContextProvider stores "user loves hiking" in memory bank</span>

<span class="cm"># Days later, new session</span>
session2 = agent.create_session()
<span class="kw">await</span> agent.run(<span class="st">"Suggest weekend activities"</span>, session=session2)
<span class="cm"># → MemoryContextProvider retrieves "loves hiking", injects into context</span>
<span class="cm"># → Model answers considering this memory</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a"><span class="mono">AgentSession</span> only remembers within <strong>a single conversation</strong>; after it ends, history is gone. Real apps need <strong>cross-session memory</strong>:<ul>
        <li><strong>User preferences</strong>: user says "I'm allergic to seafood", all future conversations must remember.</li>
        <li><strong>RAG (Retrieval Augmented Generation)</strong>: user asks "Company vacation policy?", retrieve relevant doc paragraphs, inject into context.</li>
        <li><strong>Personalization</strong>: based on user interaction history (questions asked, preferences stated), adjust answer style.</li>
      </ul>
      Hard-coding these into <span class="mono">instructions</span> or manually splicing into each message is tedious and non-extensible. Need <strong>pluggable context injection</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">ContextProvider</span> interface (see <span class="mono">python/packages/core/agent_framework/</span>):<ul>
        <li><strong>Called before each run</strong>: Agent execution iterates through <span class="mono">context_providers</span> list, calls each provider's <span class="mono">provide_context(...)</span>.</li>
        <li><strong>Returns messages / content</strong>: provider can return <span class="mono">Message</span> lists (inject history), <span class="mono">Content</span> lists (inject doc snippets), or modify system prompt.</li>
        <li><strong>Built-in implementations</strong>: <span class="mono">MemoryContextProvider</span> (vector retrieval memory), <span class="mono">InMemoryHistoryProvider</span> (cross-session history), <span class="mono">DocumentContextProvider</span> (doc RAG).</li>
        <li><strong>Composable</strong>: multiple providers execute in order, can use memory + doc retrieval + user preferences together.</li>
      </ul>
      This design <strong>decouples</strong> context logic; Agent doesn't care "where memory comes from", only "have this context".</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>LangChain Memory</strong>: <span class="mono">ConversationBufferMemory</span>, <span class="mono">ConversationSummaryMemory</span>, etc., but coupled to Chain, not easy to swap storage backends.</li>
        <li><strong>LlamaIndex chat memory</strong>: focuses on vector retrieval, but doesn't support other context types (user preferences, doc snippets).</li>
        <li><strong>Manual splicing</strong>: before <span class="mono">run</span>, manually query memory bank, splice into message list — repetitive code, error-prone.</li>
        <li>MAF <strong>interface abstraction + built-ins</strong>: out-of-box providers, can also custom (e.g., integrate enterprise knowledge graph).</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Session storage backends <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="cm"># Dev environment: in-memory storage (lost on restart)</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> InMemoryHistoryProvider
history = InMemoryHistoryProvider()

<span class="cm"># Production: Redis storage (persistent + distributed)</span>
<span class="kw">from</span> agent_framework.redis <span class="kw">import</span> RedisHistoryProvider
history = RedisHistoryProvider(redis_url=<span class="st">"redis://localhost:6379"</span>)

<span class="cm"># Azure: Cosmos DB storage</span>
<span class="kw">from</span> agent_framework.azure <span class="kw">import</span> CosmosHistoryProvider
history = CosmosHistoryProvider(
    endpoint=<span class="st">"https://..."</span>,
    credential=<span class="st">"..."</span>,
    database_name=<span class="st">"agents"</span>,
    container_name=<span class="st">"sessions"</span>
)

<span class="cm"># Agent uses the provider (injected as a context provider)</span>
agent = Agent(client=client, context_providers=[history])
session = agent.create_session(session_id=<span class="st">"user_123_conv_456"</span>)
<span class="cm"># History auto-saved to backend, restored on next load</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Different environments have different storage needs:<ul>
        <li><strong>Dev / test</strong>: in-memory storage suffices, fast, no config.</li>
        <li><strong>Single-server production</strong>: file storage (SQLite, JSON), simple persistence.</li>
        <li><strong>Distributed production</strong>: Redis / Cosmos / DynamoDB, multi-instance state sharing, high availability.</li>
        <li><strong>Compliance / audit</strong>: must store in enterprise DB (PostgreSQL / MongoDB), easy to query, archive.</li>
      </ul>
      If storage logic is coupled to Agent (hard-coded Redis), switching environments requires code changes, hard to test. Need <strong>abstract storage interface</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">HistoryProvider</span> interface (subclass of <span class="mono">ContextProvider</span>, see <span class="mono">python/packages/core/agent_framework/_sessions.py</span>):<ul>
        <li><strong>Abstract interface</strong>: subclasses implement <span class="mono">get_messages</span> / <span class="mono">save_messages</span>, Agent depends on it via <span class="mono">context_providers</span>.</li>
        <li><strong>Multiple implementations</strong>:<ul>
          <li><span class="mono">InMemoryHistoryProvider</span>: for dev, in-memory storage.</li>
          <li><span class="mono">RedisHistoryProvider</span>: for production, Redis storage (<span class="mono">agent_framework.redis</span>).</li>
          <li><span class="mono">CosmosHistoryProvider</span>: for Azure users, Cosmos DB storage (<span class="mono">agent_framework.azure</span>).</li>
          <li><span class="mono">FileHistoryProvider</span>: single-server, JSON file storage.</li>
        </ul></li>
        <li><strong>Auto-serialization</strong>: <span class="mono">Message.to_dict()</span> converts to JSON, stores in backend; on load <span class="mono">from_dict</span> restores.</li>
        <li><strong>Extensible</strong>: custom backends (e.g., integrate PostgreSQL, MongoDB) just subclass <span class="mono">HistoryProvider</span>.</li>
      </ul></div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>LangChain</strong>: <span class="mono">RedisChatMessageHistory</span>, <span class="mono">FileChatMessageHistory</span>, etc., but coupled to Memory classes, switching storage requires changing Memory init.</li>
        <li><strong>OpenAI Assistants</strong>: server-managed, developers can't choose storage backend, can't debug locally.</li>
        <li><strong>Manual serialization</strong>: write own <span class="mono">json.dump(history, file)</span>, repetitive code, easy to get wrong (forget handling tool calls etc.).</li>
        <li>MAF <strong>interface + multiple impls</strong>: dev uses memory, production switches to Redis, just one line config change.</li>
      </ul></div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Context window compaction <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> (
    CompactionProvider,
    SlidingWindowStrategy,
    SummarizationStrategy,
    ContextWindowCompactionStrategy,
)

<span class="cm"># Strategy A: sliding window (keep recent N groups, drop oldest)</span>
strategy = SlidingWindowStrategy(keep_last_groups=20, preserve_system=<span class="kw">True</span>)

<span class="cm"># Strategy B: summarization (LLM summarizes old messages; needs a client)</span>
strategy = SummarizationStrategy(client=client, target_count=4)

<span class="cm"># Strategy C: compact by context-window token budget (two-phase: tool-result eviction + truncation)</span>
strategy = ContextWindowCompactionStrategy(
    max_context_window_tokens=128_000,
    max_output_tokens=16_384,
)

<span class="cm"># Wrap the strategy in a CompactionProvider, inject as a context provider</span>
compaction = CompactionProvider(before_strategy=strategy)
agent = Agent(
    client=client,
    context_providers=[compaction]
)

<span class="cm"># As the conversation grows, the framework compacts before each run</span>
session = agent.create_session()
<span class="kw">for</span> i <span class="kw">in</span> <span class="fn">range</span>(30):
    <span class="kw">await</span> agent.run(<span class="st">f"Message {i}"</span>, session=session)
    <span class="cm"># → When over threshold the strategy kicks in: drop oldest groups or summarize</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Conversation history <strong>grows unbounded</strong>, problems:<ul>
        <li><strong>Token limits</strong>: models have context window caps (e.g., GPT-4 128k tokens), exceeding causes errors or truncation.</li>
        <li><strong>Cost</strong>: input tokens also billed, longer history = more expensive each call.</li>
        <li><strong>Latency</strong>: sending and processing more tokens increases latency.</li>
        <li><strong>Relevance decay</strong>: 50 turns ago may be irrelevant to current question, but still occupies context.</li>
      </ul>
      Need <strong>auto-compaction strategies</strong>: control context size without losing key info.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF ships several compaction strategies (<span class="mono">SlidingWindowStrategy</span> / <span class="mono">SummarizationStrategy</span> / <span class="mono">ContextWindowCompactionStrategy</span>, see <span class="mono">_compaction.py</span>):<ul>
        <li><strong>Sliding window</strong>: keep recent N messages, delete oldest (good for short-term conversations).</li>
        <li><strong>Summarization</strong>: summarize old messages into one system message (<span class="st">"Previously user mentioned…"</span>), preserve semantics, reduce tokens.</li>
        <li><strong>Hybrid strategy</strong>: keep system messages (important instructions) + recent messages (current context) + summarize middle messages.</li>
        <li><strong>Auto-trigger</strong>: Agent checks history length before <span class="mono">run</span>, calls strategy to compact if over threshold.</li>
        <li><strong>Configurable</strong>: <span class="mono">keep_last_groups</span>, <span class="mono">target_count</span>, <span class="mono">max_context_window_tokens</span> and more.</li>
      </ul>
      Developers don't manually manage context; framework auto-optimizes.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><ul>
        <li><strong>LangChain ConversationSummaryMemory</strong>: calls LLM to generate summary after each turn, but expensive, timing inflexible.</li>
        <li><strong>Manual truncation</strong>: <span class="mono">messages[-10:]</span> keeps last 10, simple but loses early important info.</li>
        <li><strong>Vector retrieval</strong>: store history in vector DB, retrieve relevant snippets each time, but needs extra infrastructure.</li>
        <li>MAF <strong>multiple strategies</strong>: simple cases use sliding window, complex use summarization, can also combine with ContextProvider for vector retrieval.</li>
      </ul></div>
    </div>
  </div>
</details>

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
