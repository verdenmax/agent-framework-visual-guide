"""Content for Part 8 / cross-part new lessons (M6): lessons 28-31.

This file holds four core-depth lessons authored in milestone M6. They live in
one module but attach to different parts via shell.PAGES:

* L28 memory-backends  -> Part 5 (build your own): Redis / Mem0 / Cosmos providers.
* L29 devui            -> Part 4 (advanced): local visual debugging via serve().
* L30 observability    -> Part 4 (advanced): OpenTelemetry deep-dive.
* L31 glossary         -> Part 8 (quick reference, NEW): term grid + concept map.

All content is raw HTML (no Markdown); emphasis uses <strong>/<em>. Inside <pre>
blocks literal '<' is written as '&lt;' and '&' as '&amp;'. Each lesson body is
the INNER content only (shell.page() adds the <h1>).
"""

# ---------------------------------------------------------------------------
L28_ZH = r"""
<p class="lead">前面几课的 Agent 都是<strong>金鱼记忆</strong>——一次 <span class="mono">run()</span> 结束，什么都不记得。
本课教你给它接上<strong>记忆后端</strong>：用 Redis / Mem0 / Cosmos 把对话历史和长期记忆存到进程之外，
靠两类抽象——<span class="mono">ContextProvider</span> 与 <span class="mono">HistoryProvider</span>——把"记住"这件事插进每一次运行。</p>

<div class="card analogy">
  <div class="tag">🧠 生活类比</div>
  没有记忆后端的 Agent 像一个<strong>失忆的接待员</strong>：每位客人来都得从头自我介绍。
  接上记忆后端，就等于给他配了<strong>两样东西</strong>：一本<strong>随手记的对话本</strong>（短期、逐字记录这次聊了什么 = HistoryProvider），
  和一座<strong>客户档案馆</strong>（长期、按相关性检索"这个人以前提过什么" = ContextProvider）。
</div>

<h2>记忆挂在 run() 的哪个位置</h2>
<p>记忆不是 Agent 内部的字段，而是挂在会话上的<strong>插件</strong>。一次 <span class="mono">run()</span> 里，框架会在调模型<strong>之前</strong>和<strong>之后</strong>各回调一次每个 Provider：</p>
<div class="flow">
  <div class="node"><div class="nt">你的输入</div><div class="nd">agent.run(text, session)</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">before_run</div><div class="nd">注入历史 + 检索记忆</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">LLM</div><div class="nd">看到「历史+记忆+新问题」</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">after_run</div><div class="nd">把这轮写回后端</div></div>
</div>
<p>关键洞察：<strong>Agent 本身不持有记忆</strong>。它只是在固定的两个钩子上"问一下"挂着的 Provider 们——
要注入什么上下文（<span class="mono">before_run</span>），运行完要存什么（<span class="mono">after_run</span>）。
换后端 = 换一个 Provider 实例，Agent 代码一行不改。</p>

<h2>走一遍：一次"带记忆"的运行</h2>
<p>场景：一个咖啡店点单助手。用户第二天回来只问了一句"<strong>老样子</strong>"，Agent 却答得出来——因为它先去记忆后端翻了账。
下面每一步给出当时<strong>消息列表的真实快照</strong>，看记忆是怎么"凭空"出现在上下文里的。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>你只发了一句话</h4>
    <p>调用 <span class="mono">agent.run("老样子", session=session)</span>。此刻框架手里的消息列表很短：</p>
<pre class="code">messages = [
  Message(<span class="st">"system"</span>, [<span class="st">"你是咖啡店点单助手…"</span>]),
  Message(<span class="st">"user"</span>,   [<span class="st">"老样子"</span>]),
]</pre>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>HistoryProvider.before_run：把这个会话的历史接回来</h4>
    <p><span class="mono">CosmosHistoryProvider</span>（或 <span class="mono">RedisHistoryProvider</span>）用 <span class="mono">session_id</span> 调
      <span class="mono">get_messages()</span>，把<strong>上次聊天的逐字记录</strong>取回并接到前面：</p>
<pre class="code"><span class="cm"># get_messages(session_id) 取回的历史</span>
Message(<span class="st">"user"</span>,      [<span class="st">"我要一杯燕麦拿铁，少糖"</span>]),
Message(<span class="st">"assistant"</span>, [<span class="st">"好的，燕麦拿铁少糖，已下单"</span>]),</pre>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>ContextProvider.before_run：按相关性检索长期记忆</h4>
    <p><span class="mono">RedisContextProvider</span> / <span class="mono">Mem0ContextProvider</span> 拿本次输入文本去后端做<strong>全文 / 向量检索</strong>，
      把命中的"画像式记忆"作为一条额外的 <span class="mono">user</span> 消息<strong>注入</strong>上下文（真实代码就是 <span class="mono">context.extend_messages(...)</span>）：</p>
<pre class="code"><span class="cm"># 检索命中后注入的记忆（带 context_prompt 前缀）</span>
Message(<span class="st">"user"</span>, [<span class="st">"## Memories\n这位顾客对牛奶过敏，长期点燕麦奶。"</span>]),</pre>
  </div></div>
  <div class="step"><div class="num">4</div><div class="sc">
    <h4>模型这才看到「历史 + 记忆 + 新问题」</h4>
    <p>LLM 收到的早已不是孤零零一句"老样子"，而是被两个 Provider 悄悄补全过的<strong>完整上下文</strong>，于是答得出
      "<span class="mono">好的，还是燕麦拿铁少糖</span>"。短期对话本 + 长期档案馆，在这里合流。</p>
  </div></div>
  <div class="step"><div class="num">5</div><div class="sc">
    <h4>after_run：把这一轮写回后端，供下次取用</h4>
    <p>运行结束，<span class="mono">HistoryProvider.after_run</span> 调 <span class="mono">save_messages()</span> 把本轮问答追加进历史；
      <span class="mono">ContextProvider.after_run</span> 则把值得长期记的事实（如"过敏牛奶"）抽取/写进向量库。
      下一次 <span class="mono">run()</span>，循环重新开始——记忆就这样滚雪球式地积累。</p>
  </div></div>
</div>

<h2>两类抽象：短期对话本 vs 长期档案馆</h2>
<p>这是本课最该记住的一张图。两者都继承自同一个基类 <span class="mono">ContextProvider</span>，但分工不同：</p>
<div class="cols">
  <div class="col">
    <h4>🗒️ HistoryProvider（短期 · 逐字）</h4>
    <p><span class="mono">HistoryProvider(ContextProvider)</span>，<span class="mono">_sessions.py:410</span>。
      职责是<strong>原样存取一个会话的消息流</strong>：子类只需实现 <span class="mono">get_messages()</span> 和 <span class="mono">save_messages()</span>，
      基类的 <span class="mono">before_run</span>/<span class="mono">after_run</span> 自动按开关"加载/存储"。</p>
    <p>开关：<span class="mono">load_messages</span>（运行前是否加载）、<span class="mono">store_inputs</span> / <span class="mono">store_outputs</span>（是否存输入/输出）。
      用它回答"<strong>我们这次对话刚才说了啥</strong>"。后端如 <span class="mono">RedisHistoryProvider</span> / <span class="mono">CosmosHistoryProvider</span>。</p>
  </div>
  <div class="col">
    <h4>📚 ContextProvider（长期 · 语义）</h4>
    <p><span class="mono">ContextProvider</span> 基类，<span class="mono">_sessions.py:348</span>。更通用：在 <span class="mono">before_run</span> 里<strong>往上下文塞任何东西</strong>
      （检索到的记忆、额外指令、临时工具），在 <span class="mono">after_run</span> 里处理响应。</p>
    <p>用它回答"<strong>关于这个人/这件事，我以前知道些什么</strong>"——通常背后是向量检索。
      后端如 <span class="mono">RedisContextProvider</span> / <span class="mono">Mem0ContextProvider</span>。它<strong>不保证逐字</strong>，要的是"相关"。</p>
  </div>
</div>

<h2>三家后端对照</h2>
<table class="t">
  <tr><th>后端</th><th>包</th><th>类</th><th>类型</th><th>擅长</th></tr>
  <tr><td>Redis</td><td class="mono">agent-framework-redis</td><td class="mono">RedisContextProvider</td><td>ContextProvider</td><td>全文 / 向量检索的长期记忆，可自带 vectorizer</td></tr>
  <tr><td>Redis</td><td class="mono">agent-framework-redis</td><td class="mono">RedisHistoryProvider</td><td>HistoryProvider</td><td>低延迟存取会话历史</td></tr>
  <tr><td>Mem0</td><td class="mono">agent-framework-mem0</td><td class="mono">Mem0ContextProvider</td><td>ContextProvider</td><td>托管式长期记忆（OSS 或 Platform），自动抽取事实</td></tr>
  <tr><td>Cosmos</td><td class="mono">agent-framework-azure-cosmos</td><td class="mono">CosmosHistoryProvider</td><td>HistoryProvider</td><td>Azure 上持久、可扩展的会话历史</td></tr>
</table>
<p>注意一个不对称：Redis 两类都给（既能当对话本又能当档案馆），Mem0 只做 <span class="mono">ContextProvider</span>（专注长期记忆），
Cosmos 只做 <span class="mono">HistoryProvider</span>（专注持久历史）。这正反映了"<strong>选后端 = 选你需要哪类记忆</strong>"。</p>

<h2>真实源码：一个 ContextProvider 长什么样</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_context_provider.py</span><span class="ln">RedisContextProvider（简化自 :44 / :118）</span></div>
<pre><span class="kw">class</span> <span class="fn">RedisContextProvider</span>(ContextProvider):
    <span class="kw">def</span> <span class="fn">__init__</span>(self, source_id=<span class="st">"redis"</span>,
                 redis_url=<span class="st">"redis://localhost:6379"</span>,
                 index_name=<span class="st">"context"</span>, *, redis_vectorizer=<span class="kw">None</span>, ...):
        <span class="kw">super</span>().__init__(source_id)        <span class="cm"># 记住自己的 source_id（用于归因）</span>
        self.redis_index = ...               <span class="cm"># 建 / 连 Redis 向量索引</span>

    <span class="kw">async def</span> <span class="fn">before_run</span>(self, *, agent, session, context, state):
        <span class="cm"># 1) 取本次输入文本</span>
        input_text = <span class="st">"\n"</span>.join(m.text <span class="kw">for</span> m <span class="kw">in</span> context.input_messages <span class="kw">if</span> m.text)
        <span class="kw">if not</span> input_text.strip():
            <span class="kw">return</span>
        <span class="cm"># 2) 去 Redis 按相关性检索记忆（全文 / 向量）</span>
        memories = <span class="kw">await</span> self._redis_search(text=input_text)
        joined = <span class="st">"\n"</span>.join(m.get(<span class="st">"content"</span>, <span class="st">""</span>) <span class="kw">for</span> m <span class="kw">in</span> memories)
        <span class="cm"># 3) 把检索到的记忆作为额外 user 消息「注入」本次上下文</span>
        <span class="kw">if</span> joined:
            context.extend_messages(self.source_id,
                [Message(role=<span class="st">"user"</span>, contents=[<span class="st">f"{self.context_prompt}\n{joined}"</span>])])</pre>
</div>
<p>三步——<strong>取输入 → 检索 → 注入</strong>——就是几乎所有 <span class="mono">ContextProvider</span> 的骨架。
<span class="mono">Mem0ContextProvider.before_run</span>（<span class="mono">_context_provider.py:95</span>）逻辑一模一样，只是第 2 步换成调 Mem0 的 <span class="mono">search()</span>。
而 <span class="mono">HistoryProvider</span> 把这套封装得更狠：你只写 <span class="mono">get_messages</span>/<span class="mono">save_messages</span> 两个方法，加载/存储的时机由基类按 <span class="mono">load_messages</span>/<span class="mono">store_*</span> 开关代劳。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么把"记忆"抽象成 Provider，而不是塞进 Agent <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">同一个 Agent，开发期用内存历史，生产期换 Cosmos，再加一个 Redis 长期记忆——三种组合，Agent 构造代码不变，只是往 session 上挂不同的 Provider 列表。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">记忆是<strong>横切关注点</strong>：存哪、怎么检索、要不要逐字，会随环境剧变。如果把它焊进 Agent，每换一种存储就得改 Agent；抽成 Provider 后，存储策略与 Agent 行为彻底解耦。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">统一的 <span class="mono">ContextProvider.before_run/after_run</span> 钩子（<span class="mono">_sessions.py:367 / :388</span>）是唯一的接入面。多个 Provider 可叠加（一个管历史、一个管长期记忆），各自带 <span class="mono">source_id</span> 做消息归因，互不打架。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">可以自己在 <span class="mono">run()</span> 外面手动拼历史（啰嗦、易错），或把记忆逻辑写进每个工具（耦合）。Provider 模式的好处是"<strong>一次接入，处处生效</strong>"，且能被框架的中间件/可观测统一观测。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 短期历史 vs 长期向量记忆，怎么选 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">客服机器人：用 <span class="mono">HistoryProvider</span> 保证"这通对话里说过的话不丢"；用 <span class="mono">ContextProvider</span>（向量）记住"这个客户半年前投诉过物流"。两者同时挂，互补。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">逐字历史<strong>会无限膨胀</strong>，全塞进 prompt 既贵又超窗口；纯向量记忆又会丢掉"刚才那句话的精确措辞"。分成两类，各取所长。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">HistoryProvider</span> 用 <span class="mono">get/save_messages</span> 管<strong>精确、有序</strong>的会话流；<span class="mono">ContextProvider</span> 用检索管<strong>相关、跨会话</strong>的记忆。基类共享同一套钩子，所以能自由组合。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">只用历史（简单但记不住跨会话偏好）、只用向量（省窗口但丢逐字）、或把整段历史做摘要再存（折中，但摘要会丢细节）。生产里通常"短期历史 + 长期向量"两条腿走路。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>记忆是挂在会话上的 <strong>Provider 插件</strong>，不是 Agent 的内部字段；换后端不改 Agent。</li>
    <li><span class="mono">ContextProvider.before_run</span> 注入上下文，<span class="mono">after_run</span> 处理/写回——这是唯一接入面。</li>
    <li><span class="mono">HistoryProvider</span> = 短期逐字（<span class="mono">get/save_messages</span>）；<span class="mono">ContextProvider</span> = 长期语义检索。</li>
    <li>Redis 两类全给，Mem0 专做长期记忆，Cosmos 专做持久历史——按需求选后端。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>同一个基类，两种记忆。</strong><span class="mono">HistoryProvider</span> 继承 <span class="mono">ContextProvider</span>，于是"逐字对话本"和"语义档案馆"
  共用 <span class="mono">before_run/after_run</span> 这一对钩子。框架不需要为"记忆"发明新机制——它只是 ContextProvider 的一种用法。
</div>
"""

L28_EN = r"""
<p class="lead">So far our agents have had <strong>goldfish memory</strong>: the moment a <span class="mono">run()</span> ends, they forget everything.
This lesson wires in a <strong>memory backend</strong>: Redis / Mem0 / Cosmos store conversation history and long-term memory outside the process,
through two abstractions&mdash;<span class="mono">ContextProvider</span> and <span class="mono">HistoryProvider</span>&mdash;that splice "remembering" into every run.</p>

<div class="card analogy">
  <div class="tag">🧠 Analogy</div>
  An agent with no memory backend is like an <strong>amnesiac receptionist</strong>: every visitor has to introduce themselves from scratch.
  A memory backend gives them <strong>two things</strong>: a <strong>scratch pad</strong> (short-term, the verbatim log of this conversation = HistoryProvider),
  and a <strong>customer archive</strong> (long-term, retrieved by relevance&mdash;"what has this person mentioned before" = ContextProvider).
</div>

<h2>Where memory sits in a run()</h2>
<p>Memory isn't a field inside the agent&mdash;it's a <strong>plugin</strong> attached to the session. Within one <span class="mono">run()</span>, the framework calls back into each Provider <strong>before</strong> and <strong>after</strong> the model call:</p>
<div class="flow">
  <div class="node"><div class="nt">your input</div><div class="nd">agent.run(text, session)</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">before_run</div><div class="nd">inject history + retrieved memory</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">LLM</div><div class="nd">sees "history + memory + new question"</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">after_run</div><div class="nd">write this turn back</div></div>
</div>
<p>Key insight: <strong>the agent holds no memory itself</strong>. It just "asks" the attached Providers at two fixed hooks&mdash;
what context to inject (<span class="mono">before_run</span>), and what to persist afterward (<span class="mono">after_run</span>).
Switching backends = swapping a Provider instance; the agent code never changes.</p>

<h2>Worked example: one memory-enabled run</h2>
<p>Scenario: a coffee-shop ordering assistant. The user comes back the next day and just says "<strong>the usual</strong>"&mdash;yet the agent answers correctly, because it checked the books first.
Each step below shows the real <strong>message-list snapshot</strong>, so you can see memory appear "out of nowhere" in the context.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>You sent a single line</h4>
    <p>Call <span class="mono">agent.run("the usual", session=session)</span>. Right now the framework's message list is short:</p>
<pre class="code">messages = [
  Message(<span class="st">"system"</span>, [<span class="st">"You are a coffee-shop ordering assistant…"</span>]),
  Message(<span class="st">"user"</span>,   [<span class="st">"the usual"</span>]),
]</pre>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>HistoryProvider.before_run: reattach this session's history</h4>
    <p><span class="mono">CosmosHistoryProvider</span> (or <span class="mono">RedisHistoryProvider</span>) calls <span class="mono">get_messages()</span> by <span class="mono">session_id</span>,
      pulling back the <strong>verbatim log of last time</strong> and prepending it:</p>
<pre class="code"><span class="cm"># history returned by get_messages(session_id)</span>
Message(<span class="st">"user"</span>,      [<span class="st">"An oat-milk latte, low sugar"</span>]),
Message(<span class="st">"assistant"</span>, [<span class="st">"Got it&mdash;oat latte, low sugar, ordered"</span>]),</pre>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>ContextProvider.before_run: retrieve long-term memory by relevance</h4>
    <p><span class="mono">RedisContextProvider</span> / <span class="mono">Mem0ContextProvider</span> takes the input text and runs a <strong>full-text / vector search</strong>,
      then <strong>injects</strong> the hits as one extra <span class="mono">user</span> message (the real code is literally <span class="mono">context.extend_messages(...)</span>):</p>
<pre class="code"><span class="cm"># memory injected after a hit (with the context_prompt prefix)</span>
Message(<span class="st">"user"</span>, [<span class="st">"## Memories\nThis customer is dairy-allergic; always orders oat milk."</span>]),</pre>
  </div></div>
  <div class="step"><div class="num">4</div><div class="sc">
    <h4>Only now does the model see "history + memory + new question"</h4>
    <p>What reaches the LLM is no longer a lonely "the usual" but a <strong>complete context</strong> quietly filled in by the two Providers,
      so it can reply "<span class="mono">Sure&mdash;oat-milk latte, low sugar again</span>". Short-term pad and long-term archive merge here.</p>
  </div></div>
  <div class="step"><div class="num">5</div><div class="sc">
    <h4>after_run: write this turn back for next time</h4>
    <p>When the run ends, <span class="mono">HistoryProvider.after_run</span> calls <span class="mono">save_messages()</span> to append this Q&amp;A to history;
      <span class="mono">ContextProvider.after_run</span> extracts/writes the worth-remembering facts (like "dairy allergy") into the vector store.
      The next <span class="mono">run()</span> starts the loop again&mdash;memory snowballs.</p>
  </div></div>
</div>

<h2>Two abstractions: scratch pad vs archive</h2>
<p>This is the one diagram to remember. Both inherit from the same base <span class="mono">ContextProvider</span>, but their jobs differ:</p>
<div class="cols">
  <div class="col">
    <h4>🗒️ HistoryProvider (short-term · verbatim)</h4>
    <p><span class="mono">HistoryProvider(ContextProvider)</span>, <span class="mono">_sessions.py:410</span>.
      Its job is to <strong>store/load a session's message stream as-is</strong>: subclasses only implement <span class="mono">get_messages()</span> and <span class="mono">save_messages()</span>,
      while the base <span class="mono">before_run</span>/<span class="mono">after_run</span> auto "load/store" per flags.</p>
    <p>Flags: <span class="mono">load_messages</span> (load before run?), <span class="mono">store_inputs</span> / <span class="mono">store_outputs</span> (store input/output?).
      Use it to answer "<strong>what did we just say in this conversation</strong>". Backends: <span class="mono">RedisHistoryProvider</span> / <span class="mono">CosmosHistoryProvider</span>.</p>
  </div>
  <div class="col">
    <h4>📚 ContextProvider (long-term · semantic)</h4>
    <p>The <span class="mono">ContextProvider</span> base, <span class="mono">_sessions.py:348</span>. More general: in <span class="mono">before_run</span> it can <strong>push anything into the context</strong>
      (retrieved memories, extra instructions, ad-hoc tools), and process the response in <span class="mono">after_run</span>.</p>
    <p>Use it to answer "<strong>what did I already know about this person/topic</strong>"&mdash;usually backed by vector search.
      Backends: <span class="mono">RedisContextProvider</span> / <span class="mono">Mem0ContextProvider</span>. It does <strong>not</strong> guarantee verbatim; it wants "relevant".</p>
  </div>
</div>

<h2>Three backends compared</h2>
<table class="t">
  <tr><th>Backend</th><th>Package</th><th>Class</th><th>Type</th><th>Good at</th></tr>
  <tr><td>Redis</td><td class="mono">agent-framework-redis</td><td class="mono">RedisContextProvider</td><td>ContextProvider</td><td>full-text / vector long-term memory, pluggable vectorizer</td></tr>
  <tr><td>Redis</td><td class="mono">agent-framework-redis</td><td class="mono">RedisHistoryProvider</td><td>HistoryProvider</td><td>low-latency conversation history</td></tr>
  <tr><td>Mem0</td><td class="mono">agent-framework-mem0</td><td class="mono">Mem0ContextProvider</td><td>ContextProvider</td><td>managed long-term memory (OSS or Platform), auto fact extraction</td></tr>
  <tr><td>Cosmos</td><td class="mono">agent-framework-azure-cosmos</td><td class="mono">CosmosHistoryProvider</td><td>HistoryProvider</td><td>durable, scalable history on Azure</td></tr>
</table>
<p>Note an asymmetry: Redis ships both (pad and archive), Mem0 only does <span class="mono">ContextProvider</span> (focused on long-term memory),
Cosmos only does <span class="mono">HistoryProvider</span> (focused on durable history). That mirrors "<strong>picking a backend = picking which kind of memory you need</strong>".</p>

<h2>Real source: what a ContextProvider looks like</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_context_provider.py</span><span class="ln">RedisContextProvider (simplified from :44 / :118)</span></div>
<pre><span class="kw">class</span> <span class="fn">RedisContextProvider</span>(ContextProvider):
    <span class="kw">def</span> <span class="fn">__init__</span>(self, source_id=<span class="st">"redis"</span>,
                 redis_url=<span class="st">"redis://localhost:6379"</span>,
                 index_name=<span class="st">"context"</span>, *, redis_vectorizer=<span class="kw">None</span>, ...):
        <span class="kw">super</span>().__init__(source_id)        <span class="cm"># remember our source_id (for attribution)</span>
        self.redis_index = ...               <span class="cm"># build / connect a Redis vector index</span>

    <span class="kw">async def</span> <span class="fn">before_run</span>(self, *, agent, session, context, state):
        <span class="cm"># 1) take this run's input text</span>
        input_text = <span class="st">"\n"</span>.join(m.text <span class="kw">for</span> m <span class="kw">in</span> context.input_messages <span class="kw">if</span> m.text)
        <span class="kw">if not</span> input_text.strip():
            <span class="kw">return</span>
        <span class="cm"># 2) retrieve relevant memories from Redis (full-text / vector)</span>
        memories = <span class="kw">await</span> self._redis_search(text=input_text)
        joined = <span class="st">"\n"</span>.join(m.get(<span class="st">"content"</span>, <span class="st">""</span>) <span class="kw">for</span> m <span class="kw">in</span> memories)
        <span class="cm"># 3) "inject" the hits as an extra user message into this run's context</span>
        <span class="kw">if</span> joined:
            context.extend_messages(self.source_id,
                [Message(role=<span class="st">"user"</span>, contents=[<span class="st">f"{self.context_prompt}\n{joined}"</span>])])</pre>
</div>
<p>Three steps&mdash;<strong>take input → retrieve → inject</strong>&mdash;are the skeleton of almost every <span class="mono">ContextProvider</span>.
<span class="mono">Mem0ContextProvider.before_run</span> (<span class="mono">_context_provider.py:95</span>) is identical except step 2 calls Mem0's <span class="mono">search()</span>.
<span class="mono">HistoryProvider</span> wraps this even tighter: you write only <span class="mono">get_messages</span>/<span class="mono">save_messages</span>, and the base class handles <em>when</em> to load/store per the <span class="mono">load_messages</span>/<span class="mono">store_*</span> flags.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Why abstract "memory" into a Provider instead of baking it into Agent <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Same agent: in-memory history in dev, Cosmos in prod, plus a Redis long-term memory&mdash;three combinations, and the agent's construction code is unchanged; you just attach different Providers to the session.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why it's necessary</div>
      <div class="a">Memory is a <strong>cross-cutting concern</strong>: where to store, how to retrieve, verbatim or not&mdash;all swing wildly with environment. Welded into the Agent, every storage change means editing the Agent; as a Provider, storage policy and agent behavior fully decouple.</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF's approach &amp; benefits</div>
      <div class="a">The uniform <span class="mono">ContextProvider.before_run/after_run</span> hooks (<span class="mono">_sessions.py:367 / :388</span>) are the only seam. Multiple Providers stack (one for history, one for long-term memory), each with a <span class="mono">source_id</span> for message attribution, without clashing.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Hand-assemble history outside <span class="mono">run()</span> (verbose, error-prone), or bury memory logic in each tool (coupled). The Provider pattern means "<strong>wire once, applies everywhere</strong>", and is uniformly observable via the framework's middleware/telemetry.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Short-term history vs long-term vector memory&mdash;how to choose <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Support bot: a <span class="mono">HistoryProvider</span> guarantees "nothing said in this call is lost"; a (vector) <span class="mono">ContextProvider</span> remembers "this customer complained about shipping six months ago". Attach both&mdash;complementary.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why it's necessary</div>
      <div class="a">Verbatim history <strong>grows without bound</strong>; stuffing it all into the prompt is expensive and overflows the window. Pure vector memory loses "the exact wording of the last sentence". Splitting into two types plays to each strength.</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF's approach &amp; benefits</div>
      <div class="a"><span class="mono">HistoryProvider</span> manages the <strong>exact, ordered</strong> message stream via <span class="mono">get/save_messages</span>; <span class="mono">ContextProvider</span> manages <strong>relevant, cross-session</strong> memory via retrieval. The shared base hooks let you compose them freely.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">History only (simple but forgets cross-session preferences), vector only (saves window but loses verbatim), or summarize-then-store (a compromise that loses detail). Production usually walks on both legs: short-term history + long-term vectors.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Memory is a <strong>Provider plugin</strong> on the session, not a field inside the Agent; swap backends without touching the Agent.</li>
    <li><span class="mono">ContextProvider.before_run</span> injects context, <span class="mono">after_run</span> processes/persists&mdash;the single seam.</li>
    <li><span class="mono">HistoryProvider</span> = short-term verbatim (<span class="mono">get/save_messages</span>); <span class="mono">ContextProvider</span> = long-term semantic retrieval.</li>
    <li>Redis ships both, Mem0 specializes in long-term memory, Cosmos in durable history&mdash;pick by need.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>One base class, two kinds of memory.</strong> <span class="mono">HistoryProvider</span> subclasses <span class="mono">ContextProvider</span>, so the "verbatim pad" and the "semantic archive"
  share the same <span class="mono">before_run/after_run</span> pair. The framework didn't invent a new mechanism for "memory"&mdash;it's just one use of a ContextProvider.
</div>
"""

# ---------------------------------------------------------------------------
L29_ZH = r"""
<p class="lead">用 <span class="mono">print()</span> 调 Agent 就像蒙着眼开车——你只看到终点的一句话，看不到中间它<strong>调了哪个工具、流式吐了什么、每步多久</strong>。
<strong>DevUI</strong> 给你一块仪表盘：一行 <span class="mono">serve(entities=[agent])</span> 启动本地服务，浏览器里实时看 Agent 跑的每一步。</p>

<div class="card analogy">
  <div class="tag">🛩️ 生活类比</div>
  DevUI 像飞机的<strong>驾驶舱</strong>：引擎（Agent）照常工作，但你面前多了一排仪表——高度、油量、航向（消息、工具调用、token 流）。
  没有它，你只能听引擎声音猜（看 <span class="mono">print</span> 日志）；有了它，每个读数都<strong>看得见</strong>。
</div>

<h2>一行启动，浏览器即仪表盘</h2>
<div class="flow">
  <div class="node"><div class="nt">你的 Agent</div><div class="nd">Agent(name, client, tools)</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">serve(entities=[agent])</div><div class="nd">起本地 server</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">浏览器 UI</div><div class="nd">localhost:8080</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">看得见</div><div class="nd">消息 / 工具 / 流 / trace</div></div>
</div>
<p><span class="mono">serve()</span> 在底层用 <span class="mono">uvicorn</span> 起一个带 Web 界面 + <strong>OpenAI 兼容 API</strong>（<span class="mono">/v1/*</span>）的本地服务，把你传进去的 <strong>entities（Agent 或 Workflow）</strong>注册进去。
浏览器打开后，左边是发现到的实体列表，右边是聊天面板——你发一句话，它把<strong>每一步</strong>画出来。</p>

<h2>走一遍：在 DevUI 里调一个带工具的 Agent</h2>
<p>场景：一个会查天气的 Agent。你想看清"用户问天气 → 模型决定调工具 → 工具返回 → 模型组织答复"这条链，而不是只看到最后一句话。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>写好 Agent，一行 serve</h4>
    <p>不改 Agent 任何代码，只在脚本末尾加一行：</p>
<pre class="code"><span class="kw">from</span> agent_framework.devui <span class="kw">import</span> serve
serve(entities=[agent], auto_open=<span class="kw">True</span>)   <span class="cm"># 自动开浏览器到 localhost:8080</span></pre>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>浏览器里选中实体、发一句话</h4>
    <p>左侧列表出现你的 <span class="mono">WeatherAgent</span>（DevUI 自动为内存实体生成 ID）。在右侧聊天框输入"巴黎天气如何？"并发送。</p>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>看到模型「先决定调工具」</h4>
    <p>消息时间线上不是立刻出现文本，而是先冒出一个<strong>工具调用卡片</strong>：<span class="mono">get_weather(city="Paris")</span>。
      这正是第 14 课讲的"首批 chunk 是 tool_calls 而非文本"——以前只能脑补，现在直接看见。</p>
  </div></div>
  <div class="step"><div class="num">4</div><div class="sc">
    <h4>看到工具结果回填、token 逐个流出</h4>
    <p>工具卡片展开显示返回值 <span class="mono">"15°C, 晴"</span>；紧接着答复区开始<strong>一个字一个字地流</strong>出来——你能直观感到"先静默、再爆发"的流式节奏。</p>
  </div></div>
  <div class="step"><div class="num">5</div><div class="sc">
    <h4>（可选）打开 trace，看 span 树</h4>
    <p>若启动时传 <span class="mono">instrumentation_enabled=True</span>，DevUI 会调用框架的 <span class="mono">enable_instrumentation()</span>（即第 30 课的可观测开关），
      于是同一次运行的 <span class="mono">invoke_agent → chat → execute_tool → chat</span> span 树也能在界面里看到耗时与属性。</p>
  </div></div>
</div>

<h2>界面能看到什么</h2>
<table class="t">
  <tr><th>面板</th><th>看到的内容</th><th>对应概念（课）</th></tr>
  <tr><td>实体发现</td><td>注册进来的 Agent / Workflow 列表</td><td class="mono">entities 参数</td></tr>
  <tr><td>聊天 / 请求面板</td><td>你发的输入、Agent 的回复</td><td>消息 Message（4 课）</td></tr>
  <tr><td>消息时间线</td><td>system / user / assistant 消息按序展开</td><td>run 循环（3 课）</td></tr>
  <tr><td>工具调用</td><td>FunctionCall 名称 / 参数 / 返回值</td><td>工具调用内部（10 课）</td></tr>
  <tr><td>事件 / 流</td><td>逐个 token、流式更新事件</td><td>流式（14 课）</td></tr>
  <tr><td>Trace（可选）</td><td>span 树、耗时、属性</td><td>可观测性（30 课）</td></tr>
</table>

<h2>真实源码：serve() 的签名</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">agent_framework_devui/__init__.py</span><span class="ln">serve（简化自 :89）</span></div>
<pre><span class="kw">def</span> <span class="fn">serve</span>(
    entities=<span class="kw">None</span>,             <span class="cm"># 内存里要调试的 Agent / Workflow 列表</span>
    entities_dir=<span class="kw">None</span>,         <span class="cm"># 或：扫描一个目录做「发现」</span>
    port=<span class="nb">8080</span>,
    host=<span class="st">"127.0.0.1"</span>,        <span class="cm"># 默认只绑本机</span>
    auto_open=<span class="kw">False</span>,          <span class="cm"># 是否自动开浏览器</span>
    cors_origins=<span class="kw">None</span>,
    ui_enabled=<span class="kw">True</span>,           <span class="cm"># 关掉就只剩 API，不出 Web 界面</span>
    instrumentation_enabled=<span class="kw">False</span>,  <span class="cm"># 打开 OpenTelemetry（见第 30 课）</span>
    mode=<span class="st">"developer"</span>,        <span class="cm"># developer=详细报错 / user=受限+通用报错</span>
    auth_enabled=<span class="kw">True</span>,         <span class="cm"># 默认开 Bearer token 鉴权</span>
    auth_token=<span class="kw">None</span>,
) -&gt; <span class="kw">None</span>:
    <span class="cm"># 起 uvicorn server，注册 entities，挂上 Web UI + /v1/* 兼容 API</span>
    ...</pre>
</div>
<p>注意几个有信息量的默认值：<span class="mono">host="127.0.0.1"</span>（只绑本机，安全）、<span class="mono">auth_enabled=True</span>（默认带鉴权，启动时日志里打印开发 token）、
<span class="mono">mode="developer"</span>（开发期给你详细报错）。命令行入口 <span class="mono">main()</span>（<span class="mono">:202</span>）对应 <span class="mono">devui ./agents</span>，走的是 <span class="mono">entities_dir</span> 目录发现那条路。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> serve() 到底做了什么 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a"><span class="mono">serve(entities=[agent])</span> 内部：创建一个 <span class="mono">DevServer</span>，把 entities 暂存为待注册，取出它的 FastAPI <span class="mono">app</span>，最后 <span class="mono">uvicorn.run(app, host, port)</span>。<span class="mono">auto_open=True</span> 时还会起一个线程，等 <span class="mono">/health</span> 就绪后开浏览器。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">不想为了"看一眼 Agent 怎么跑的"就去手写一个前端 + 一套 API。把这套样板收进一个 <span class="mono">serve()</span>，调试成本从"搭个项目"降到"加一行"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">DevUI 暴露的是 <strong>OpenAI 兼容</strong>的 <span class="mono">/v1/*</span> 接口，所以任何 OpenAI 客户端都能直连调试；Web UI 只是这套 API 的一个可视化壳。<span class="mono">instrumentation_enabled</span> 一开，trace 也并进同一界面。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">纯 CLI / <span class="mono">print</span>（看不到结构）、自己接 LangSmith 之类外部平台（要配置、可能收费）、或自己写前端（重）。DevUI 的取舍是"<strong>零配置、本地、开箱即用</strong>"。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 它是「样例 App」，不是生产服务器 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">官方明确说 DevUI 是 <strong>sample app</strong>，用来快速上手与本地调试。生产环境应当用 Agent Framework SDK<strong>自建</strong> API server 和界面。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">生产对鉴权、限流、可用性、定制 UI 的要求远超一个调试工具。把 DevUI 当生产网关，迟早在安全和可扩展性上栽跟头。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">DevUI 默认 <span class="mono">host=127.0.0.1</span> + <span class="mono">auth_enabled=True</span>，本就为"本机开发"定位；它和真正的部署路径（如 25 课的 Foundry 托管）是<strong>两条线</strong>，各司其职。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">无实体启动时，DevUI 会显示<strong>样例画廊</strong>，可下载官方示例本地跑——这让它也是个"学习/演示"工具，而不只是调试器。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>一行 <span class="mono">serve(entities=[agent])</span> 起本地服务 + 浏览器仪表盘，<strong>不改 Agent 代码</strong>。</li>
    <li>能看到：消息时间线、工具调用、流式 token，开 <span class="mono">instrumentation_enabled</span> 还能看 trace。</li>
    <li>底层是 <span class="mono">uvicorn</span> + <strong>OpenAI 兼容 API</strong>（<span class="mono">/v1/*</span>）；Web UI 只是它的壳。</li>
    <li>它是<strong>样例调试 App</strong>，默认绑本机 + 带鉴权；生产请自建 server。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>调试不该需要改代码。</strong>DevUI 不要求你给 Agent 加任何"调试钩子"——同一个 <span class="mono">agent</span> 对象，平时 <span class="mono">run()</span>，想看就 <span class="mono">serve()</span>。
  可观测能力（trace）也只是一个开关 <span class="mono">instrumentation_enabled</span>，复用框架既有的 OpenTelemetry，而不是另起一套。
</div>
"""

L29_EN = r"""
<p class="lead">Debugging an agent with <span class="mono">print()</span> is like driving blindfolded&mdash;you see the final sentence but not <strong>which tool it called, what it streamed, or how long each step took</strong>.
<strong>DevUI</strong> gives you a dashboard: one line, <span class="mono">serve(entities=[agent])</span>, launches a local server and you watch every step in the browser, live.</p>

<div class="card analogy">
  <div class="tag">🛩️ Analogy</div>
  DevUI is like an aircraft <strong>cockpit</strong>: the engine (the Agent) works as usual, but now you have a row of gauges&mdash;altitude, fuel, heading (messages, tool calls, token stream).
  Without it you guess from the engine noise (reading <span class="mono">print</span> logs); with it, every reading is <strong>visible</strong>.
</div>

<h2>One line to launch; the browser is your dashboard</h2>
<div class="flow">
  <div class="node"><div class="nt">your Agent</div><div class="nd">Agent(name, client, tools)</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">serve(entities=[agent])</div><div class="nd">start local server</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">browser UI</div><div class="nd">localhost:8080</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">visible</div><div class="nd">messages / tools / stream / trace</div></div>
</div>
<p>Under the hood <span class="mono">serve()</span> uses <span class="mono">uvicorn</span> to start a local server with a web UI plus an <strong>OpenAI-compatible API</strong> (<span class="mono">/v1/*</span>), registering the <strong>entities (Agents or Workflows)</strong> you pass in.
Open the browser: on the left is the list of discovered entities, on the right a chat panel&mdash;you send a line, and it draws <strong>every step</strong>.</p>

<h2>Worked example: debugging a tool-using Agent in DevUI</h2>
<p>Scenario: an agent that looks up weather. You want to see the chain "user asks → model decides to call a tool → tool returns → model composes the reply", not just the final sentence.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>Write the Agent, add one serve line</h4>
    <p>Change nothing in the Agent; just append one line to your script:</p>
<pre class="code"><span class="kw">from</span> agent_framework.devui <span class="kw">import</span> serve
serve(entities=[agent], auto_open=<span class="kw">True</span>)   <span class="cm"># auto-opens browser to localhost:8080</span></pre>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>Pick the entity in the browser, send a line</h4>
    <p>Your <span class="mono">WeatherAgent</span> appears in the left list (DevUI auto-generates an ID for in-memory entities). Type "What's the weather in Paris?" in the chat box and send.</p>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>See the model "decide to call a tool" first</h4>
    <p>The message timeline doesn't show text immediately&mdash;first a <strong>tool-call card</strong> pops up: <span class="mono">get_weather(city="Paris")</span>.
      This is exactly Lesson 14's "the first chunks are tool_calls, not text"&mdash;previously imagined, now seen.</p>
  </div></div>
  <div class="step"><div class="num">4</div><div class="sc">
    <h4>See the tool result fill in, tokens stream out</h4>
    <p>The tool card expands to show the return value <span class="mono">"15°C, sunny"</span>; then the reply area starts streaming <strong>character by character</strong>&mdash;you feel the "quiet first, then burst" streaming rhythm directly.</p>
  </div></div>
  <div class="step"><div class="num">5</div><div class="sc">
    <h4>(Optional) Open the trace, see the span tree</h4>
    <p>If you pass <span class="mono">instrumentation_enabled=True</span> at launch, DevUI calls the framework's <span class="mono">enable_instrumentation()</span> (the observability switch from Lesson 30),
      so the same run's <span class="mono">invoke_agent → chat → execute_tool → chat</span> span tree, with durations and attributes, is visible in the UI too.</p>
  </div></div>
</div>

<h2>What the UI shows</h2>
<table class="t">
  <tr><th>Panel</th><th>What you see</th><th>Concept (lesson)</th></tr>
  <tr><td>Entity discovery</td><td>list of registered Agents / Workflows</td><td class="mono">entities arg</td></tr>
  <tr><td>Chat / request panel</td><td>your input, the Agent's reply</td><td>Message (L4)</td></tr>
  <tr><td>Message timeline</td><td>system / user / assistant messages in order</td><td>run loop (L3)</td></tr>
  <tr><td>Tool calls</td><td>FunctionCall name / args / return value</td><td>tool internals (L10)</td></tr>
  <tr><td>Events / stream</td><td>per-token, streaming update events</td><td>streaming (L14)</td></tr>
  <tr><td>Trace (optional)</td><td>span tree, durations, attributes</td><td>observability (L30)</td></tr>
</table>

<h2>Real source: the serve() signature</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">agent_framework_devui/__init__.py</span><span class="ln">serve (simplified from :89)</span></div>
<pre><span class="kw">def</span> <span class="fn">serve</span>(
    entities=<span class="kw">None</span>,             <span class="cm"># in-memory Agents / Workflows to debug</span>
    entities_dir=<span class="kw">None</span>,         <span class="cm"># or: scan a directory for "discovery"</span>
    port=<span class="nb">8080</span>,
    host=<span class="st">"127.0.0.1"</span>,        <span class="cm"># binds to localhost by default</span>
    auto_open=<span class="kw">False</span>,          <span class="cm"># auto-open the browser?</span>
    cors_origins=<span class="kw">None</span>,
    ui_enabled=<span class="kw">True</span>,           <span class="cm"># turn off to keep only the API, no web UI</span>
    instrumentation_enabled=<span class="kw">False</span>,  <span class="cm"># turn on OpenTelemetry (see Lesson 30)</span>
    mode=<span class="st">"developer"</span>,        <span class="cm"># developer=verbose errors / user=restricted+generic</span>
    auth_enabled=<span class="kw">True</span>,         <span class="cm"># Bearer-token auth on by default</span>
    auth_token=<span class="kw">None</span>,
) -&gt; <span class="kw">None</span>:
    <span class="cm"># start a uvicorn server, register entities, mount web UI + /v1/* compatible API</span>
    ...</pre>
</div>
<p>Note a few informative defaults: <span class="mono">host="127.0.0.1"</span> (localhost only, safe), <span class="mono">auth_enabled=True</span> (auth on by default, dev token printed in startup logs),
<span class="mono">mode="developer"</span> (verbose errors during development). The CLI entry point <span class="mono">main()</span> (<span class="mono">:202</span>) backs <span class="mono">devui ./agents</span>, which takes the <span class="mono">entities_dir</span> discovery path.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> What serve() actually does <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Inside <span class="mono">serve(entities=[agent])</span>: create a <span class="mono">DevServer</span>, stash entities as pending, grab its FastAPI <span class="mono">app</span>, then <span class="mono">uvicorn.run(app, host, port)</span>. With <span class="mono">auto_open=True</span> it also spawns a thread that opens the browser once <span class="mono">/health</span> is ready.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why it's necessary</div>
      <div class="a">You don't want to hand-build a frontend + an API just to "see how the agent runs". Folding that boilerplate into one <span class="mono">serve()</span> drops the debugging cost from "scaffold a project" to "add one line".</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF's approach &amp; benefits</div>
      <div class="a">DevUI exposes an <strong>OpenAI-compatible</strong> <span class="mono">/v1/*</span> API, so any OpenAI client can connect directly; the web UI is just a visual shell over that API. Flip <span class="mono">instrumentation_enabled</span> on and traces fold into the same view.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Pure CLI / <span class="mono">print</span> (no structure), wiring up an external platform like LangSmith (config, possibly paid), or building your own frontend (heavy). DevUI's tradeoff is "<strong>zero-config, local, batteries-included</strong>".</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> It's a "sample app", not a production server <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">The docs state plainly that DevUI is a <strong>sample app</strong> for getting started and local debugging. For production you should <strong>build your own</strong> API server and UI with the Agent Framework SDK.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why it's necessary</div>
      <div class="a">Production needs around auth, rate-limiting, availability and custom UI far exceed a debugging tool. Treating DevUI as a production gateway will eventually bite you on security and scalability.</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF's approach &amp; benefits</div>
      <div class="a">DevUI defaults to <span class="mono">host=127.0.0.1</span> + <span class="mono">auth_enabled=True</span>&mdash;positioned for "local development". It and the real deployment path (e.g. Foundry hosting in Lesson 25) are <strong>two separate tracks</strong>, each doing its job.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">When launched with no entities, DevUI shows a <strong>sample gallery</strong> you can download and run locally&mdash;making it a "learn/demo" tool too, not just a debugger.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>One line, <span class="mono">serve(entities=[agent])</span>, gives a local server + browser dashboard, with <strong>no changes to Agent code</strong>.</li>
    <li>You see: the message timeline, tool calls, streaming tokens; with <span class="mono">instrumentation_enabled</span> you also see the trace.</li>
    <li>Under the hood it's <span class="mono">uvicorn</span> + an <strong>OpenAI-compatible API</strong> (<span class="mono">/v1/*</span>); the web UI is just its shell.</li>
    <li>It's a <strong>sample debugging app</strong>, localhost-bound with auth by default; build your own server for production.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Debugging shouldn't require code changes.</strong> DevUI asks for no "debug hooks" on your Agent&mdash;the same <span class="mono">agent</span> object you normally <span class="mono">run()</span>, you can <span class="mono">serve()</span> to inspect.
  Even observability (trace) is just one switch, <span class="mono">instrumentation_enabled</span>, reusing the framework's existing OpenTelemetry rather than a parallel system.
</div>
"""
