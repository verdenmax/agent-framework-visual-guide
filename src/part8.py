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

# ---------------------------------------------------------------------------
L30_ZH = r"""
<p class="lead">第 14 课你已见过「流式 + span 树」的合体——那是从<strong>流式</strong>视角顺带认识可观测。本课反过来：以<strong>可观测</strong>为主角，
讲清 Agent Framework 怎么把每一次运行变成可查询的 <strong>trace / metric / log</strong>，以及生产里你靠它定位延迟、失败和成本。</p>

<div class="card analogy">
  <div class="tag">🚗 生活类比</div>
  trace 像车上的<strong>行车记录仪</strong>：平时不看，出事了倒回去逐帧看「哪一步、花了多久、谁先动的」。
  metric 像<strong>仪表盘读数</strong>（平均时速、油耗），log 像<strong>维修师傅的文字记录</strong>。三者配齐，才能从"它好像变慢了"精确到"是第 2 次 chat 调用慢了 800ms"。
</div>

<h2>可观测的三根支柱</h2>
<p>OpenTelemetry（OTel）把"可观测"拆成三类信号，Agent Framework 对三类都做了内建埋点：</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">Trace 链路</span><span class="name">spans</span></div>
    <div class="ld">一次运行的 <span class="mono">invoke_agent → chat → execute_tool</span> span 树：每步耗时、父子调用关系、哪一步抛错（<span class="mono">error.type</span>）。回答"<strong>慢在哪一步</strong>"。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Metric 指标</span><span class="name">histograms</span></div>
    <div class="ld"><span class="mono">gen_ai.client.token.usage</span>、<span class="mono">gen_ai.client.operation.duration</span>、<span class="mono">agent_framework.function.invocation.duration</span>：聚合的延迟分布、token 用量、失败率。回答"<strong>整体健康度</strong>"。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Log 日志</span><span class="name">events</span></div>
    <div class="ld">结构化日志与事件。消息内容、工具参数等<strong>敏感数据</strong>默认<strong>不</strong>记录，需显式 <span class="mono">enable_sensitive_data</span>（仅测试/开发）。回答"<strong>具体发生了什么</strong>"。</div></div>
</div>

<h2>一行启动：把遥测接到后端</h2>
<div class="flow">
  <div class="node hl"><div class="nt">configure_otel_providers()</div><div class="nd">启动时调一次</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">框架埋点</div><div class="nd">Agent/Chat/Tool 自动出 span+metric</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">exporter</div><div class="nd">OTLP → :4317</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">后端</div><div class="nd">Jaeger / Azure Monitor…</div></div>
</div>
<p>你只需在应用启动时<strong>调一次</strong> <span class="mono">configure_otel_providers()</span>；之后框架的 <span class="mono">AgentTelemetryLayer</span> / <span class="mono">ChatTelemetryLayer</span> 会自动给每次
<span class="mono">run</span> / <span class="mono">get_response</span> / 工具调用挂上 span 和 metric，按 OTLP 协议吐到你配的后端。<strong>无需在业务代码里手写任何埋点。</strong></p>

<h2>走一遍：一次 run 产生的 span 树</h2>
<p>同样是"巴黎天气如何？"这次只盯<strong>可观测</strong>那条线（流式细节见第 14 课）。一次带工具的运行会长出这样一棵 span 树：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>开根 span：invoke_agent</h4>
    <p><span class="mono">agent.run("巴黎天气如何？")</span> 一进来，框架开根 span <span class="mono">invoke_agent WeatherAgent</span>
      （<span class="mono">AGENT_INVOKE_OPERATION="invoke_agent"</span>，<span class="mono">observability.py:294</span>），属性带 <span class="mono">gen_ai.agent.name</span>。</p>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>子 span：第一次 chat，模型决定调工具</h4>
    <p>子 span <span class="mono">chat gpt-4o</span> 开启（<span class="mono">CHAT_COMPLETION_OPERATION="chat"</span>，<span class="mono">:289</span>），
      属性 <span class="mono">gen_ai.request.model=gpt-4o</span>，最终 <span class="mono">gen_ai.response.finish_reasons=[tool_calls]</span>。</p>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>更深一层：execute_tool 嵌在 chat 之内</h4>
    <p>工具执行的 span <span class="mono">execute_tool get_weather</span>（<span class="mono">:291</span>）<strong>挂在 chat span 之下</strong>——
      源码里"内层工具执行被 parent 到这个 chat span"（<span class="mono">observability.py:1556</span>）。属性带 <span class="mono">gen_ai.tool.name</span>、<span class="mono">gen_ai.tool.call.id</span>。</p>
  </div></div>
  <div class="step"><div class="num">4</div><div class="sc">
    <h4>第二次 chat：带工具结果生成最终文本</h4>
    <p>再开一个 <span class="mono">chat gpt-4o</span> span，这次 <span class="mono">finish_reasons=[stop]</span>，
      属性记下 <span class="mono">gen_ai.usage.input_tokens</span> / <span class="mono">output_tokens</span>。</p>
  </div></div>
  <div class="step"><div class="num">5</div><div class="sc">
    <h4>自底向上关闭，吐出 metric</h4>
    <p>span 依调用栈<strong>自底向上</strong>依次关闭，每个都记下精确耗时；同时发出 metric：
      <span class="mono">gen_ai.client.token.usage</span>、<span class="mono">gen_ai.client.operation.duration</span>、<span class="mono">agent_framework.function.invocation.duration</span>。根 span 还会把内层 chat 的 token 累加上来。</p>
  </div></div>
</div>
<p>这棵树长这样——子 span 的耗时<strong>滚动累加</strong>进父 span，所以你一眼能看出时间花在哪：</p>
<pre class="code">invoke_agent WeatherAgent              <span class="cm"># 根：总耗时 1.9s</span>
└─ chat gpt-4o                         <span class="cm"># 第一次模型调用 → tool_calls</span>
   └─ execute_tool get_weather         <span class="cm"># 工具执行（嵌在 chat 内）120ms</span>
└─ chat gpt-4o                         <span class="cm"># 第二次：带结果生成文本 → stop</span></pre>
<table class="t">
  <tr><th>span</th><th>operation</th><th>关键属性</th></tr>
  <tr><td class="mono">invoke_agent WeatherAgent</td><td class="mono">invoke_agent</td><td class="mono">gen_ai.agent.name · usage.*（累加）</td></tr>
  <tr><td class="mono">chat gpt-4o</td><td class="mono">chat</td><td class="mono">gen_ai.request.model · response.finish_reasons</td></tr>
  <tr><td class="mono">execute_tool get_weather</td><td class="mono">execute_tool</td><td class="mono">gen_ai.tool.name · gen_ai.tool.call.id</td></tr>
</table>

<h2>真实源码：一次性接好 OTel</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">observability.py</span><span class="ln">configure_otel_providers（简化自 :1151）</span></div>
<pre><span class="kw">from</span> agent_framework.observability <span class="kw">import</span> configure_otel_providers

<span class="cm"># 应用启动时调用一次，且只调一次（在产生任何遥测之前）</span>
configure_otel_providers(
    enable_sensitive_data=<span class="kw">False</span>,       <span class="cm"># 记录消息/参数等敏感内容？仅测试/开发开</span>
    enable_console_exporters=<span class="kw">False</span>,    <span class="cm"># 把 trace/metric/log 打到控制台（本地调试）</span>
    exporters=<span class="kw">None</span>,                    <span class="cm"># 额外追加自定义 OTLP exporter</span>
    views=<span class="kw">None</span>,                        <span class="cm"># metric 视图：过滤/裁剪要采集的指标</span>
    vs_code_extension_port=<span class="kw">None</span>,       <span class="cm"># 接 VS Code AI Toolkit / Foundry 扩展</span>
)
<span class="cm"># 也可全靠环境变量，例如：</span>
<span class="cm">#   OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317</span>
<span class="cm">#   ENABLE_CONSOLE_EXPORTERS=true</span></pre>
</div>
<p>注意它是<strong>纯关键字参数</strong>（签名里的 <span class="mono">*</span>），且文档明确"<strong>只调一次</strong>"。它读标准 OTel 环境变量（<span class="mono">OTEL_EXPORTER_OTLP_ENDPOINT</span> 等），
所以多数情况下你函数体里什么都不传，全用环境变量配置。想更细控制开关，可直接用 <span class="mono">ObservabilitySettings</span>（<span class="mono">:666</span>），它对应 <span class="mono">ENABLE_INSTRUMENTATION</span> / <span class="mono">ENABLE_SENSITIVE_DATA</span> / <span class="mono">ENABLE_CONSOLE_EXPORTERS</span> 这些环境变量。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么把埋点做进框架，而不是让你手写 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">你不写一行埋点代码，<span class="mono">agent.run(...)</span> 就自动产出 <span class="mono">invoke_agent</span> span；换 ChatClient、加工具，span 树自动跟着变。开关只在启动处一句 <span class="mono">configure_otel_providers()</span>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">手写埋点既啰嗦又容易漏（漏埋的那条路恰恰是出事的路）。而且埋点散落业务代码里，迟早和逻辑纠缠。框架统一埋点 = 覆盖完整、风格一致、可一键开关。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">埋点放在 <span class="mono">AgentTelemetryLayer</span> / <span class="mono">ChatTelemetryLayer</span> 这些<strong>层</strong>里（和中间件同构的"洋葱"思路），对你的 Agent/工具代码透明。属性遵循 OpenTelemetry <strong>GenAI 语义约定</strong>（<span class="mono">gen_ai.*</span>），所以任何兼容后端都能直接读懂。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">每个厂商 SDK 自带的私有日志（格式各异、跨厂商对不上）、或自己包一层 trace（重复造轮子）。用 OTel 标准 + 框架内建，是"写一次、到处可观测"的最省力路径。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 生产里它到底帮你定位什么 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">"用户反馈变慢了"——打开 trace，看到 <span class="mono">invoke_agent</span> 1.9s 里有 1.4s 花在第二次 <span class="mono">chat</span>；再看 metric，<span class="mono">operation.duration</span> 的 p95 确实抬高；问题锁定在模型侧而非工具。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">Agent 是<strong>分布式、异步、多步</strong>的：一次回答串起模型 + 多个工具 + 检索。没有 trace，"哪一步慢/错/贵"全靠猜；有了 span 树，因果关系一目了然。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><strong>延迟</strong>看 span 耗时与 <span class="mono">operation.duration</span>；<strong>失败</strong>看带 <span class="mono">error.type</span> 的 span；<strong>成本</strong>看 <span class="mono">gen_ai.usage.input_tokens/output_tokens</span> 与 <span class="mono">token.usage</span> 指标，可按 agent/模型归因。三件事一套信号全覆盖。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">只看应用日志（缺少跨步因果、难聚合）、只看模型厂商账单（只有总量、无法归因到某个 agent）。trace+metric 的组合才能同时回答"哪一步"和"整体趋势"。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>三根支柱：<strong>trace</strong>（span 树·哪一步）、<strong>metric</strong>（聚合·整体趋势）、<strong>log</strong>（事件·发生了啥）。</li>
    <li>span 命名 <span class="mono">invoke_agent</span> / <span class="mono">chat</span> / <span class="mono">execute_tool</span>；工具 span 嵌在 chat span 之内，耗时滚动累加进父 span。</li>
    <li>启动时调一次 <span class="mono">configure_otel_providers()</span>（纯关键字参数），其余用 OTel 环境变量；埋点由框架的 telemetry 层自动完成。</li>
    <li>敏感数据（消息/参数）默认不记录，需 <span class="mono">enable_sensitive_data</span>；属性遵循 <span class="mono">gen_ai.*</span> 语义约定。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>可观测是一层，不是一堆散落的日志。</strong>埋点收进 <span class="mono">AgentTelemetryLayer</span>/<span class="mono">ChatTelemetryLayer</span>，与中间件同构地包在调用外面——
  你的 Agent 代码对"被观测"毫不知情，却能产出符合 OpenTelemetry GenAI 标准的完整 trace。开/关只是启动处一行。
</div>
"""

L30_EN = r"""
<p class="lead">In Lesson 14 you met "streaming + the span tree"&mdash;observability seen from the <strong>streaming</strong> angle. This lesson flips it: with <strong>observability</strong> as the lead,
it shows how Agent Framework turns every run into queryable <strong>trace / metric / log</strong>, and how in production you use it to pinpoint latency, failures and cost.</p>

<div class="card analogy">
  <div class="tag">🚗 Analogy</div>
  A trace is like a <strong>dashcam</strong>: ignored day to day, but after an incident you rewind frame by frame to see "which step, how long, who moved first".
  Metrics are like <strong>dashboard gauges</strong> (avg speed, fuel use); logs are the <strong>mechanic's written notes</strong>. Together they take you from "it feels slower" to "the 2nd chat call was 800ms slow".
</div>

<h2>The three pillars of observability</h2>
<p>OpenTelemetry (OTel) splits "observability" into three signal types; Agent Framework instruments all three out of the box:</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">Trace</span><span class="name">spans</span></div>
    <div class="ld">A run's <span class="mono">invoke_agent → chat → execute_tool</span> span tree: per-step duration, parent/child call relationships, which step threw (<span class="mono">error.type</span>). Answers "<strong>where is it slow</strong>".</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Metric</span><span class="name">histograms</span></div>
    <div class="ld"><span class="mono">gen_ai.client.token.usage</span>, <span class="mono">gen_ai.client.operation.duration</span>, <span class="mono">agent_framework.function.invocation.duration</span>: aggregated latency distribution, token usage, failure rate. Answers "<strong>overall health</strong>".</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Log</span><span class="name">events</span></div>
    <div class="ld">Structured logs and events. <strong>Sensitive data</strong> like message content and tool args is <strong>not</strong> recorded by default; it needs an explicit <span class="mono">enable_sensitive_data</span> (test/dev only). Answers "<strong>what exactly happened</strong>".</div></div>
</div>

<h2>One line to wire telemetry to a backend</h2>
<div class="flow">
  <div class="node hl"><div class="nt">configure_otel_providers()</div><div class="nd">call once at startup</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">framework instrumentation</div><div class="nd">Agent/Chat/Tool auto span+metric</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">exporter</div><div class="nd">OTLP → :4317</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">backend</div><div class="nd">Jaeger / Azure Monitor…</div></div>
</div>
<p>You just <strong>call once</strong> at startup: <span class="mono">configure_otel_providers()</span>. After that the framework's <span class="mono">AgentTelemetryLayer</span> / <span class="mono">ChatTelemetryLayer</span> automatically attach spans and metrics to every
<span class="mono">run</span> / <span class="mono">get_response</span> / tool call, exporting over OTLP to your configured backend. <strong>No hand-written instrumentation in business code.</strong></p>

<h2>Worked example: the span tree from one run</h2>
<p>Same "What's the weather in Paris?", but this time we watch only the <strong>observability</strong> line (streaming details are in Lesson 14). A tool-using run grows this span tree:</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>Open the root span: invoke_agent</h4>
    <p>The moment <span class="mono">agent.run("What's the weather in Paris?")</span> enters, the framework opens the root span <span class="mono">invoke_agent WeatherAgent</span>
      (<span class="mono">AGENT_INVOKE_OPERATION="invoke_agent"</span>, <span class="mono">observability.py:294</span>), with attribute <span class="mono">gen_ai.agent.name</span>.</p>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>Child span: first chat, the model decides to call a tool</h4>
    <p>A child span <span class="mono">chat gpt-4o</span> opens (<span class="mono">CHAT_COMPLETION_OPERATION="chat"</span>, <span class="mono">:289</span>),
      with <span class="mono">gen_ai.request.model=gpt-4o</span> and eventually <span class="mono">gen_ai.response.finish_reasons=[tool_calls]</span>.</p>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>One level deeper: execute_tool nests inside chat</h4>
    <p>The tool-execution span <span class="mono">execute_tool get_weather</span> (<span class="mono">:291</span>) <strong>hangs under the chat span</strong>&mdash;
      the source parents "inner tool execution" under this chat span (<span class="mono">observability.py:1556</span>). Attributes: <span class="mono">gen_ai.tool.name</span>, <span class="mono">gen_ai.tool.call.id</span>.</p>
  </div></div>
  <div class="step"><div class="num">4</div><div class="sc">
    <h4>Second chat: produce the final text with the tool result</h4>
    <p>Another <span class="mono">chat gpt-4o</span> span opens, this time with <span class="mono">finish_reasons=[stop]</span>,
      recording <span class="mono">gen_ai.usage.input_tokens</span> / <span class="mono">output_tokens</span>.</p>
  </div></div>
  <div class="step"><div class="num">5</div><div class="sc">
    <h4>Close bottom-up, emit metrics</h4>
    <p>Spans close <strong>bottom-up</strong> along the call stack, each recording an exact duration; metrics fire alongside:
      <span class="mono">gen_ai.client.token.usage</span>, <span class="mono">gen_ai.client.operation.duration</span>, <span class="mono">agent_framework.function.invocation.duration</span>. The root span also rolls up token usage from the inner chats.</p>
  </div></div>
</div>
<p>The tree looks like this&mdash;child durations <strong>roll up</strong> into the parent, so you can see at a glance where the time went:</p>
<pre class="code">invoke_agent WeatherAgent              <span class="cm"># root: total 1.9s</span>
└─ chat gpt-4o                         <span class="cm"># first model call → tool_calls</span>
   └─ execute_tool get_weather         <span class="cm"># tool exec (nested in chat) 120ms</span>
└─ chat gpt-4o                         <span class="cm"># second: text with result → stop</span></pre>
<table class="t">
  <tr><th>span</th><th>operation</th><th>key attributes</th></tr>
  <tr><td class="mono">invoke_agent WeatherAgent</td><td class="mono">invoke_agent</td><td class="mono">gen_ai.agent.name · usage.* (rolled up)</td></tr>
  <tr><td class="mono">chat gpt-4o</td><td class="mono">chat</td><td class="mono">gen_ai.request.model · response.finish_reasons</td></tr>
  <tr><td class="mono">execute_tool get_weather</td><td class="mono">execute_tool</td><td class="mono">gen_ai.tool.name · gen_ai.tool.call.id</td></tr>
</table>

<h2>Real source: wire up OTel once</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">observability.py</span><span class="ln">configure_otel_providers (simplified from :1151)</span></div>
<pre><span class="kw">from</span> agent_framework.observability <span class="kw">import</span> configure_otel_providers

<span class="cm"># Call once at app startup, and only once (before any telemetry is captured)</span>
configure_otel_providers(
    enable_sensitive_data=<span class="kw">False</span>,       <span class="cm"># record messages/args etc.? test/dev only</span>
    enable_console_exporters=<span class="kw">False</span>,    <span class="cm"># print trace/metric/log to console (local debug)</span>
    exporters=<span class="kw">None</span>,                    <span class="cm"># add custom OTLP exporters</span>
    views=<span class="kw">None</span>,                        <span class="cm"># metric views: filter/trim which metrics to collect</span>
    vs_code_extension_port=<span class="kw">None</span>,       <span class="cm"># attach VS Code AI Toolkit / Foundry extension</span>
)
<span class="cm"># Or configure entirely via env vars, e.g.:</span>
<span class="cm">#   OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317</span>
<span class="cm">#   ENABLE_CONSOLE_EXPORTERS=true</span></pre>
</div>
<p>Note it's <strong>keyword-only</strong> (the <span class="mono">*</span> in the signature) and the docs say "<strong>call once</strong>". It reads standard OTel env vars (<span class="mono">OTEL_EXPORTER_OTLP_ENDPOINT</span>, etc.),
so usually you pass nothing and configure via the environment. For finer control over switches, use <span class="mono">ObservabilitySettings</span> (<span class="mono">:666</span>), which maps to env vars like <span class="mono">ENABLE_INSTRUMENTATION</span> / <span class="mono">ENABLE_SENSITIVE_DATA</span> / <span class="mono">ENABLE_CONSOLE_EXPORTERS</span>.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Why bake instrumentation into the framework instead of making you write it <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">You write zero instrumentation code, yet <span class="mono">agent.run(...)</span> auto-emits an <span class="mono">invoke_agent</span> span; swap the ChatClient or add a tool and the span tree follows. The only switch is one <span class="mono">configure_otel_providers()</span> at startup.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why it's necessary</div>
      <div class="a">Hand-written instrumentation is verbose and easy to miss&mdash;and the un-instrumented path is exactly the one that breaks. It also tangles with business logic over time. Framework-level instrumentation = complete coverage, consistent style, one-switch control.</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF's approach &amp; benefits</div>
      <div class="a">Instrumentation lives in <strong>layers</strong> like <span class="mono">AgentTelemetryLayer</span> / <span class="mono">ChatTelemetryLayer</span> (the same "onion" idea as middleware), transparent to your Agent/tool code. Attributes follow the OpenTelemetry <strong>GenAI semantic conventions</strong> (<span class="mono">gen_ai.*</span>), so any compatible backend understands them directly.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Each vendor SDK's private logging (different formats, can't correlate across vendors), or wrapping your own trace layer (reinventing the wheel). OTel standard + built-in instrumentation is the "write once, observable everywhere" path.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> What it actually pinpoints in production <span class="hint">click to expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">"Users say it got slower"&mdash;open the trace, see <span class="mono">invoke_agent</span> is 1.9s with 1.4s in the second <span class="mono">chat</span>; check metrics, <span class="mono">operation.duration</span> p95 is indeed up; the problem is on the model side, not the tool.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why it's necessary</div>
      <div class="a">Agents are <strong>distributed, async, multi-step</strong>: one answer chains a model + several tools + retrieval. Without traces, "which step is slow/failing/expensive" is guesswork; with a span tree, causality is obvious.</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF's approach &amp; benefits</div>
      <div class="a"><strong>Latency</strong>: span durations and <span class="mono">operation.duration</span>; <strong>failures</strong>: spans carrying <span class="mono">error.type</span>; <strong>cost</strong>: <span class="mono">gen_ai.usage.input_tokens/output_tokens</span> and the <span class="mono">token.usage</span> metric, attributable per agent/model. One signal set covers all three.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">App logs only (no cross-step causality, hard to aggregate), or vendor billing only (totals, not attributable to a specific agent). Trace + metric together answer both "which step" and "overall trend".</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Three pillars: <strong>trace</strong> (span tree · which step), <strong>metric</strong> (aggregate · overall trend), <strong>log</strong> (events · what happened).</li>
    <li>Spans are named <span class="mono">invoke_agent</span> / <span class="mono">chat</span> / <span class="mono">execute_tool</span>; the tool span nests inside the chat span, and durations roll up into the parent.</li>
    <li>Call <span class="mono">configure_otel_providers()</span> once at startup (keyword-only); configure the rest via OTel env vars; instrumentation is done by the framework's telemetry layers.</li>
    <li>Sensitive data (messages/args) is off by default and needs <span class="mono">enable_sensitive_data</span>; attributes follow the <span class="mono">gen_ai.*</span> semantic conventions.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Observability is a layer, not scattered logs.</strong> Instrumentation is folded into <span class="mono">AgentTelemetryLayer</span>/<span class="mono">ChatTelemetryLayer</span>, wrapping the call like middleware&mdash;
  your Agent code has no idea it's being observed, yet emits a complete trace conforming to the OpenTelemetry GenAI conventions. On or off is a single line at startup.
</div>
"""

L31_ZH = r"""
<p class="lead">前面 30 课，我们从「Agent 是什么」一路走到记忆后端、可观测性、协议生态。这一课<strong>不教新东西</strong>——它是整本书的<strong>速查表与地图</strong>：把散落各课的核心术语收进一张表，每个词配上<strong>一句话定义、真实源码位置、所属课</strong>，再画出它们之间的<strong>依赖关系</strong>。卡壳时回这里，一眼定位。</p>

<div class="card analogy">
  <div class="tag">🗺️ 生活类比</div>
  走完一条长线路后，你会拿到一张<strong>地图 + 图例</strong>：每个地名（术语）有坐标（源码位置）、属于哪一段路（所属课），地图还画出<strong>哪条路通哪条路</strong>（概念依赖）。这一课就是这张图——不带你重走，而是让你<strong>随时找回任何一个点</strong>。
</div>

<h2>怎么用这张速查表</h2>
<p>每张表三列信息：<strong>一句话定义</strong>（这词到底指什么）、<strong>源码位置</strong>（去真实仓库 grep 哪个文件、第几行——所有行号均已核对）、<strong>所属课</strong>（点进去看完整推演）。术语按"你会在何处遇到它"分成六组，从最贴近用户到最偏运维。</p>

<h2>① 用户层：你每天直接打交道的</h2>
<table class="t">
  <tr><th>术语</th><th>一句话定义</th><th>源码位置</th><th>所属课</th></tr>
  <tr><td class="mono">Agent / BaseAgent</td><td>把"模型 + 工具 + 指令"打包成一个能 <span class="mono">run()</span> 的对象；BaseAgent 是抽象基类，Agent 是默认实现</td><td class="mono">_agents.py:314 / :1584</td><td><a href="08-agent-internals.html">8 课</a></td></tr>
  <tr><td class="mono">ChatClient / BaseChatClient</td><td>与某家模型对话的统一通道：发消息、收消息。Agent 靠它"说话"</td><td class="mono">_clients.py:217</td><td><a href="09-chatclient-internals.html">9 课</a></td></tr>
  <tr><td class="mono">Message</td><td>对话的基本单位，带一个 <span class="mono">role</span> 和一串 <span class="mono">contents</span></td><td class="mono">_types.py:1672</td><td><a href="04-messages.html">4 课</a></td></tr>
  <tr><td class="mono">Content</td><td>消息里的内容块（文本 / 工具调用 / 结果 / 图片…），用 <span class="mono">Content.from_text()</span> 等构造</td><td class="mono">_types.py:455</td><td><a href="04-messages.html">4 课</a></td></tr>
  <tr><td class="mono">Role</td><td>消息角色（system / user / assistant / tool），本质是带语义的字符串</td><td class="mono">_types.py:1620</td><td><a href="04-messages.html">4 课</a></td></tr>
  <tr><td class="mono">@tool / FunctionTool</td><td>把普通 Python 函数包成 Agent 能调用的工具；<span class="mono">@tool</span> 是装饰器，FunctionTool 是包装结果</td><td class="mono">_tools.py:1145 / :240</td><td><a href="06-tools.html">6 课</a></td></tr>
</table>

<h2>② 内部机制：一次 run 背后</h2>
<table class="t">
  <tr><th>术语</th><th>一句话定义</th><th>源码位置</th><th>所属课</th></tr>
  <tr><td>run 生命周期</td><td>一次 <span class="mono">run()</span>：组消息 → 问模型 →（要调工具就执行 → 回填 → 再问）→ 出 AgentResponse</td><td class="mono">_agents.py:1584</td><td><a href="03-lifecycle.html">3 课</a></td></tr>
  <tr><td>FunctionCall / Result</td><td>工具调用的"请求"与"返回"，作为 Content 装在消息的 <span class="mono">contents</span> 里</td><td class="mono">_types.py:455</td><td><a href="10-tool-internals.html">10 课</a></td></tr>
  <tr><td class="mono">AgentResponse / Update</td><td>run 的结果对象；流式时是一连串 <span class="mono">Update</span> 增量，逐个拼成最终答复</td><td class="mono">_types.py:2530 / :2782</td><td><a href="14-streaming-observability.html">14 课</a></td></tr>
  <tr><td>Middleware（三类）</td><td>包在调用外的拦截层：Agent / Function / Chat 三种粒度，可改输入、改输出、短路</td><td class="mono">_middleware.py:469 / :528 / :592</td><td><a href="11-middleware.html">11 课</a></td></tr>
</table>

<h2>③ 工作流与编排：让多个步骤协作</h2>
<table class="t">
  <tr><th>术语</th><th>一句话定义</th><th>源码位置</th><th>所属课</th></tr>
  <tr><td class="mono">Workflow</td><td>把多个步骤连成的<strong>有向图</strong>，按边驱动数据流转</td><td class="mono">_workflows/_workflow.py:206</td><td><a href="12-workflows.html">12 课</a></td></tr>
  <tr><td class="mono">Executor</td><td>图里的一个<strong>节点</strong>：一个 Agent，或一段自定义逻辑</td><td class="mono">_workflows/_executor.py:30</td><td><a href="12-workflows.html">12 课</a></td></tr>
  <tr><td class="mono">Edge</td><td>节点间的连线，决定消息往哪条路流</td><td class="mono">_workflows/_edge.py:76</td><td><a href="12-workflows.html">12 课</a></td></tr>
  <tr><td class="mono">WorkflowBuilder</td><td>链式 API 搭出 Workflow；检查点也在这里用 <span class="mono">checkpoint_storage=</span> 传入</td><td class="mono">_workflows/_workflow_builder.py:53</td><td><a href="12-workflows.html">12 课</a></td></tr>
  <tr><td class="mono">WorkflowContext</td><td>节点拿到的运行时上下文：往下游发消息、产出输出</td><td class="mono">_workflows/_workflow_context.py:207</td><td><a href="12-workflows.html">12 课</a></td></tr>
  <tr><td>编排器 5 式</td><td>现成的多 Agent 图：Sequential / Concurrent / GroupChat / Handoff / Magentic</td><td class="mono">orchestrations/_sequential.py:63 等</td><td><a href="13-orchestration.html">13 课</a></td></tr>
</table>

<h2>④ 记忆与会话：跨轮、跨会话记住事情</h2>
<table class="t">
  <tr><th>术语</th><th>一句话定义</th><th>源码位置</th><th>所属课</th></tr>
  <tr><td class="mono">ContextProvider</td><td>在 run <strong>之前</strong>往上下文注入东西（如检索到的相关记忆）；钩子是 <span class="mono">before_run()</span></td><td class="mono">_sessions.py:348</td><td><a href="07-sessions-memory.html">7 课</a></td></tr>
  <tr><td class="mono">HistoryProvider</td><td>ContextProvider 的子类，专管整段对话历史的<strong>加载与保存</strong></td><td class="mono">_sessions.py:410</td><td><a href="07-sessions-memory.html">7 课</a></td></tr>
  <tr><td class="mono">RedisContextProvider</td><td>把上下文 / 历史落到 Redis 的后端实现</td><td class="mono">agent_framework_redis/_context_provider.py:44</td><td><a href="28-memory-backends.html">28 课</a></td></tr>
  <tr><td class="mono">Mem0ContextProvider</td><td>用 Mem0 托管"长期记忆"的后端实现</td><td class="mono">agent_framework_mem0/_context_provider.py:36</td><td><a href="28-memory-backends.html">28 课</a></td></tr>
  <tr><td class="mono">CosmosHistoryProvider</td><td>用 Azure Cosmos DB 存对话历史的后端实现</td><td class="mono">agent_framework_azure_cosmos/_history_provider.py:36</td><td><a href="28-memory-backends.html">28 课</a></td></tr>
</table>

<h2>⑤ 生态与协议：与外部世界对接</h2>
<table class="t">
  <tr><th>术语</th><th>一句话定义</th><th>源码位置</th><th>所属课</th></tr>
  <tr><td class="mono">Skill</td><td>可打包 / 复用的能力单元（含脚本、资源、frontmatter）；Skill 是抽象基类</td><td class="mono">_skills.py:492 / :729</td><td><a href="23-skills.html">23 课</a></td></tr>
  <tr><td class="mono">MCPTool</td><td>通过 MCP 协议接入的外部工具（stdio / HTTP / websocket 三种传输）</td><td class="mono">_mcp.py:263</td><td><a href="24-mcp.html">24 课</a></td></tr>
  <tr><td class="mono">ResponsesHostServer</td><td>把 Agent 跑在 Foundry，由托管层接管历史 / 检查点 / 审批存储</td><td class="mono">foundry_hosting/_responses.py:341</td><td><a href="25-hosted-agents.html">25 课</a></td></tr>
  <tr><td class="mono">A2AAgent / AGUI</td><td>Agent 间通信（A2A）与 Agent↔前端（AG-UI）的标准协议接入</td><td class="mono">agent_framework_a2a/_agent.py:154 · agent_framework_ag_ui/_agent.py:66</td><td><a href="26-a2a-agui.html">26 课</a></td></tr>
  <tr><td class="mono">AgentFactory</td><td>声明式：从 YAML 描述实例化出 Agent</td><td class="mono">agent_framework_declarative/_loader.py:141</td><td><a href="17-declarative.html">17 课</a></td></tr>
</table>

<h2>⑥ 运维与质量：让它可靠、可调、可信</h2>
<table class="t">
  <tr><th>术语</th><th>一句话定义</th><th>源码位置</th><th>所属课</th></tr>
  <tr><td class="mono">WorkflowCheckpoint / CheckpointStorage</td><td>把工作流每个超步的状态存档，失败可从最近检查点恢复</td><td class="mono">_workflows/_checkpoint.py:31 / :119</td><td><a href="19-durability-hitl.html">19 课</a></td></tr>
  <tr><td class="mono">RequestInfoMixin</td><td>人在回路（HITL）的底座：让执行<strong>暂停</strong>、向人/外部要信息再继续</td><td class="mono">_workflows/_request_info_mixin.py:29</td><td><a href="19-durability-hitl.html">19 课</a></td></tr>
  <tr><td class="mono">Evaluator</td><td>对 Agent 输出做评估的协议（质量 / 正确性 / 安全）</td><td class="mono">_evaluation.py:683</td><td><a href="27-eval-timetravel.html">27 课</a></td></tr>
  <tr><td class="mono">configure_otel_providers</td><td>一次性接上 OpenTelemetry，之后 trace / metric 自动产出</td><td class="mono">observability.py:1151</td><td><a href="30-observability.html">30 课</a></td></tr>
  <tr><td class="mono">serve()（DevUI）</td><td>一行起本地可视化调试服务，浏览器里看每一步</td><td class="mono">agent_framework_devui/__init__.py:89</td><td><a href="29-devui.html">29 课</a></td></tr>
</table>

<h2>概念依赖图：谁建立在谁之上</h2>
<p>从下往上读：上层的每个概念都<strong>站在下层之上</strong>。看不懂上层时，往下退一层往往就通了。</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">基石</span><span class="name">Message · Content · Role</span></div><div class="ld">一切的原子：模型的输入输出都是消息，消息里装 Content（文本 / 工具调用 / 结果）。（<a href="04-messages.html">4 课</a>）</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">通道</span><span class="name">ChatClient</span></div><div class="ld">把消息发给某家模型、收回消息。Agent 靠它说话。（<a href="09-chatclient-internals.html">9 课</a>）</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">主体</span><span class="name">Agent + Tools + Middleware</span></div><div class="ld">run 循环：模型决定调工具 → 执行 → 回填 → 再问模型，中间件层层包裹。（<a href="08-agent-internals.html">8</a> / <a href="10-tool-internals.html">10</a> / <a href="11-middleware.html">11 课</a>）</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">编排</span><span class="name">Workflow · Executor · Edge · 编排器</span></div><div class="ld">多个 Agent / 步骤组成图，按边流转；五种现成编排是封装好的图。（<a href="12-workflows.html">12</a> / <a href="13-orchestration.html">13 课</a>）</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">记忆</span><span class="name">ContextProvider · HistoryProvider</span></div><div class="ld">run 前注入上下文、run 后存历史；Redis / Mem0 / Cosmos 是后端。（<a href="07-sessions-memory.html">7</a> / <a href="28-memory-backends.html">28 课</a>）</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">生态</span><span class="name">Skill · MCP · A2A / AG-UI · 托管</span></div><div class="ld">对外：标准化工具（MCP）、Agent 间通信（A2A）、前端（AG-UI）、云托管（Foundry）。（<a href="23-skills.html">23</a>–<a href="26-a2a-agui.html">26 课</a>）</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">运维</span><span class="name">Checkpoint · HITL · Eval · OTel · DevUI</span></div><div class="ld">让它可靠、可调、可信：存档 / 人审 / 评估 / 追踪 / 可视化。（<a href="19-durability-hitl.html">19</a> / <a href="27-eval-timetravel.html">27</a> / <a href="29-devui.html">29</a> / <a href="30-observability.html">30 课</a>）</div></div>
</div>

<h2>一次 run 的最小依赖链</h2>
<div class="flow">
  <div class="node"><div class="nt">Message 进</div><div class="nd">用户输入</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Agent.run</div><div class="nd">+ Middleware</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">ChatClient</div><div class="nd">问模型</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Tool 执行</div><div class="nd">FunctionCall / Result</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Message 出</div><div class="nd">AgentResponse</div></div>
</div>

<h2>反向索引：带着问题找课</h2>
<table class="t">
  <tr><th>我想…</th><th>去这一课</th></tr>
  <tr><td>搞清一次 <span class="mono">run()</span> 到底发生了什么</td><td><a href="03-lifecycle.html">3 课</a> · <a href="08-agent-internals.html">8 课</a></td></tr>
  <tr><td>让 Agent 调用我的函数 / 外部工具</td><td><a href="06-tools.html">6 课</a> · <a href="24-mcp.html">24 课</a></td></tr>
  <tr><td>让 Agent 记住跨会话的事</td><td><a href="07-sessions-memory.html">7 课</a> · <a href="28-memory-backends.html">28 课</a></td></tr>
  <tr><td>在每次调用前后插一段自己的逻辑</td><td><a href="11-middleware.html">11 课</a> · <a href="18-custom-middleware.html">18 课</a></td></tr>
  <tr><td>让多个 Agent 协作完成一个任务</td><td><a href="12-workflows.html">12 课</a> · <a href="13-orchestration.html">13 课</a></td></tr>
  <tr><td>失败能恢复、关键步骤要人审批</td><td><a href="19-durability-hitl.html">19 课</a></td></tr>
  <tr><td>看清 Agent 跑的每一步 / 排查线上慢</td><td><a href="29-devui.html">29 课</a> · <a href="30-observability.html">30 课</a></td></tr>
  <tr><td>评估 Agent 输出好不好</td><td><a href="27-eval-timetravel.html">27 课</a></td></tr>
</table>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>整个框架是<strong>分层</strong>的：Message/Content 是基石，往上依次是 ChatClient → Agent → 编排 → 生态 → 运维。</li>
    <li>每个术语都能 grep 到<strong>真实源码位置</strong>（本表行号已核对），看不懂概念就去读那几行。</li>
    <li>记不住时用<strong>反向索引</strong>：从"我想做什么"出发，直接跳到对应课。</li>
    <li>这一课是<strong>地图不是教程</strong>——它的价值在你回来查的那一刻。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>所有东西最终都化简为"消息进、消息出"。</strong>无论 Agent、工作流、还是跨机器的 A2A 协议，底层流动的都是 Message。正是这条统一的"数据契约"，让上面这么多层能彼此拼接——这也是为什么读懂第 4 课的 Message，后面 27 课都会更轻松。
</div>
"""

L31_EN = r"""
<p class="lead">Across the previous 30 lessons we went from "what is an Agent" all the way to memory backends, observability, and the protocol ecosystem. This lesson teaches <strong>nothing new</strong>—it is the whole guide's <strong>quick-reference and map</strong>: every core term collected into one place, each with a <strong>one-line definition, a real source location, and its home lesson</strong>, plus a picture of how they <strong>depend on each other</strong>. When you get stuck, come back here and locate anything at a glance.</p>

<div class="card analogy">
  <div class="tag">🗺️ Analogy</div>
  After finishing a long trail you get a <strong>map + legend</strong>: every place name (term) has coordinates (source location) and a trail segment it belongs to (home lesson), and the map also draws <strong>which path connects to which</strong> (concept dependencies). This lesson is that map—it doesn't re-walk the trail, it lets you <strong>find any single point again, any time</strong>.
</div>

<h2>How to read this reference</h2>
<p>Every table has three columns: a <strong>one-line definition</strong> (what the term actually means), a <strong>source location</strong> (which file and line to grep in the real repo—every line number has been verified), and its <strong>home lesson</strong> (click in for the full walkthrough). Terms are grouped into six buckets by "where you'll meet them", from closest-to-user to most ops-facing.</p>

<h2>① User layer: what you touch every day</h2>
<table class="t">
  <tr><th>Term</th><th>One-line definition</th><th>Source location</th><th>Lesson</th></tr>
  <tr><td class="mono">Agent / BaseAgent</td><td>Bundles "model + tools + instructions" into an object you can <span class="mono">run()</span>; BaseAgent is the abstract base, Agent the default impl</td><td class="mono">_agents.py:314 / :1584</td><td><a href="08-agent-internals.html">L8</a></td></tr>
  <tr><td class="mono">ChatClient / BaseChatClient</td><td>The uniform channel for talking to one model provider: send messages, get messages back. An Agent "speaks" through it</td><td class="mono">_clients.py:217</td><td><a href="09-chatclient-internals.html">L9</a></td></tr>
  <tr><td class="mono">Message</td><td>The basic unit of a conversation, carrying a <span class="mono">role</span> and a list of <span class="mono">contents</span></td><td class="mono">_types.py:1672</td><td><a href="04-messages.html">L4</a></td></tr>
  <tr><td class="mono">Content</td><td>A content block inside a message (text / tool call / result / image…), built via <span class="mono">Content.from_text()</span> etc.</td><td class="mono">_types.py:455</td><td><a href="04-messages.html">L4</a></td></tr>
  <tr><td class="mono">Role</td><td>The message role (system / user / assistant / tool)—essentially a semantic string</td><td class="mono">_types.py:1620</td><td><a href="04-messages.html">L4</a></td></tr>
  <tr><td class="mono">@tool / FunctionTool</td><td>Wraps a plain Python function into a tool the Agent can call; <span class="mono">@tool</span> is the decorator, FunctionTool the wrapper result</td><td class="mono">_tools.py:1145 / :240</td><td><a href="06-tools.html">L6</a></td></tr>
</table>

<h2>② Internals: behind one run</h2>
<table class="t">
  <tr><th>Term</th><th>One-line definition</th><th>Source location</th><th>Lesson</th></tr>
  <tr><td>run lifecycle</td><td>One <span class="mono">run()</span>: assemble messages → ask model → (if tools needed, execute → feed back → ask again) → emit AgentResponse</td><td class="mono">_agents.py:1584</td><td><a href="03-lifecycle.html">L3</a></td></tr>
  <tr><td>FunctionCall / Result</td><td>The "request" and "return" of a tool call, carried as Content in the message's <span class="mono">contents</span></td><td class="mono">_types.py:455</td><td><a href="10-tool-internals.html">L10</a></td></tr>
  <tr><td class="mono">AgentResponse / Update</td><td>The result object of a run; while streaming it's a series of <span class="mono">Update</span> deltas assembled into the final reply</td><td class="mono">_types.py:2530 / :2782</td><td><a href="14-streaming-observability.html">L14</a></td></tr>
  <tr><td>Middleware (3 kinds)</td><td>Interception layers wrapping a call: Agent / Function / Chat granularity—can rewrite input, rewrite output, or short-circuit</td><td class="mono">_middleware.py:469 / :528 / :592</td><td><a href="11-middleware.html">L11</a></td></tr>
</table>

<h2>③ Workflows &amp; orchestration: many steps cooperating</h2>
<table class="t">
  <tr><th>Term</th><th>One-line definition</th><th>Source location</th><th>Lesson</th></tr>
  <tr><td class="mono">Workflow</td><td>A <strong>directed graph</strong> wiring multiple steps, driving data along its edges</td><td class="mono">_workflows/_workflow.py:206</td><td><a href="12-workflows.html">L12</a></td></tr>
  <tr><td class="mono">Executor</td><td>A <strong>node</strong> in the graph: an Agent, or a piece of custom logic</td><td class="mono">_workflows/_executor.py:30</td><td><a href="12-workflows.html">L12</a></td></tr>
  <tr><td class="mono">Edge</td><td>A connection between nodes, deciding which path a message flows down</td><td class="mono">_workflows/_edge.py:76</td><td><a href="12-workflows.html">L12</a></td></tr>
  <tr><td class="mono">WorkflowBuilder</td><td>The chained API that builds a Workflow; checkpointing is wired here via <span class="mono">checkpoint_storage=</span></td><td class="mono">_workflows/_workflow_builder.py:53</td><td><a href="12-workflows.html">L12</a></td></tr>
  <tr><td class="mono">WorkflowContext</td><td>The runtime context a node receives: send messages downstream, yield outputs</td><td class="mono">_workflows/_workflow_context.py:207</td><td><a href="12-workflows.html">L12</a></td></tr>
  <tr><td>5 orchestrators</td><td>Ready-made multi-Agent graphs: Sequential / Concurrent / GroupChat / Handoff / Magentic</td><td class="mono">orchestrations/_sequential.py:63 etc.</td><td><a href="13-orchestration.html">L13</a></td></tr>
</table>

<h2>④ Memory &amp; sessions: remembering across turns</h2>
<table class="t">
  <tr><th>Term</th><th>One-line definition</th><th>Source location</th><th>Lesson</th></tr>
  <tr><td class="mono">ContextProvider</td><td>Injects things into context <strong>before</strong> a run (e.g. retrieved memories); the hook is <span class="mono">before_run()</span></td><td class="mono">_sessions.py:348</td><td><a href="07-sessions-memory.html">L7</a></td></tr>
  <tr><td class="mono">HistoryProvider</td><td>A ContextProvider subclass dedicated to <strong>loading and saving</strong> the whole conversation history</td><td class="mono">_sessions.py:410</td><td><a href="07-sessions-memory.html">L7</a></td></tr>
  <tr><td class="mono">RedisContextProvider</td><td>Backend impl that persists context / history to Redis</td><td class="mono">agent_framework_redis/_context_provider.py:44</td><td><a href="28-memory-backends.html">L28</a></td></tr>
  <tr><td class="mono">Mem0ContextProvider</td><td>Backend impl that manages "long-term memory" via Mem0</td><td class="mono">agent_framework_mem0/_context_provider.py:36</td><td><a href="28-memory-backends.html">L28</a></td></tr>
  <tr><td class="mono">CosmosHistoryProvider</td><td>Backend impl that stores conversation history in Azure Cosmos DB</td><td class="mono">agent_framework_azure_cosmos/_history_provider.py:36</td><td><a href="28-memory-backends.html">L28</a></td></tr>
</table>

<h2>⑤ Ecosystem &amp; protocols: connecting to the outside world</h2>
<table class="t">
  <tr><th>Term</th><th>One-line definition</th><th>Source location</th><th>Lesson</th></tr>
  <tr><td class="mono">Skill</td><td>A packageable / reusable capability unit (scripts, resources, frontmatter); Skill is the abstract base</td><td class="mono">_skills.py:492 / :729</td><td><a href="23-skills.html">L23</a></td></tr>
  <tr><td class="mono">MCPTool</td><td>An external tool wired in via the MCP protocol (stdio / HTTP / websocket transports)</td><td class="mono">_mcp.py:263</td><td><a href="24-mcp.html">L24</a></td></tr>
  <tr><td class="mono">ResponsesHostServer</td><td>Runs an Agent on Foundry, with the host taking over history / checkpoints / approval storage</td><td class="mono">foundry_hosting/_responses.py:341</td><td><a href="25-hosted-agents.html">L25</a></td></tr>
  <tr><td class="mono">A2AAgent / AGUI</td><td>Standard-protocol entry points for Agent-to-Agent (A2A) and Agent↔frontend (AG-UI)</td><td class="mono">agent_framework_a2a/_agent.py:154 · agent_framework_ag_ui/_agent.py:66</td><td><a href="26-a2a-agui.html">L26</a></td></tr>
  <tr><td class="mono">AgentFactory</td><td>Declarative: instantiate an Agent from a YAML description</td><td class="mono">agent_framework_declarative/_loader.py:141</td><td><a href="17-declarative.html">L17</a></td></tr>
</table>

<h2>⑥ Ops &amp; quality: reliable, debuggable, trustworthy</h2>
<table class="t">
  <tr><th>Term</th><th>One-line definition</th><th>Source location</th><th>Lesson</th></tr>
  <tr><td class="mono">WorkflowCheckpoint / CheckpointStorage</td><td>Snapshots a workflow's state at each superstep; on failure, resume from the latest checkpoint</td><td class="mono">_workflows/_checkpoint.py:31 / :119</td><td><a href="19-durability-hitl.html">L19</a></td></tr>
  <tr><td class="mono">RequestInfoMixin</td><td>The base for human-in-the-loop (HITL): let execution <strong>pause</strong>, ask a human/external for info, then continue</td><td class="mono">_workflows/_request_info_mixin.py:29</td><td><a href="19-durability-hitl.html">L19</a></td></tr>
  <tr><td class="mono">Evaluator</td><td>A protocol for evaluating Agent output (quality / correctness / safety)</td><td class="mono">_evaluation.py:683</td><td><a href="27-eval-timetravel.html">L27</a></td></tr>
  <tr><td class="mono">configure_otel_providers</td><td>Wire up OpenTelemetry once; traces / metrics then flow automatically</td><td class="mono">observability.py:1151</td><td><a href="30-observability.html">L30</a></td></tr>
  <tr><td class="mono">serve() (DevUI)</td><td>One line to start a local visual-debugging server and watch every step in the browser</td><td class="mono">agent_framework_devui/__init__.py:89</td><td><a href="29-devui.html">L29</a></td></tr>
</table>

<h2>Concept dependency map: who stands on whom</h2>
<p>Read bottom-up: every upper concept <strong>stands on the one below</strong>. When an upper layer confuses you, dropping down one layer often unblocks it.</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">Bedrock</span><span class="name">Message · Content · Role</span></div><div class="ld">The atoms of everything: a model's input and output are messages, and messages carry Content (text / tool call / result). (<a href="04-messages.html">L4</a>)</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Channel</span><span class="name">ChatClient</span></div><div class="ld">Sends messages to a model provider and gets messages back. An Agent talks through it. (<a href="09-chatclient-internals.html">L9</a>)</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Core</span><span class="name">Agent + Tools + Middleware</span></div><div class="ld">The run loop: model decides to call a tool → execute → feed back → ask again, wrapped layer by layer in middleware. (<a href="08-agent-internals.html">L8</a> / <a href="10-tool-internals.html">L10</a> / <a href="11-middleware.html">L11</a>)</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Orchestration</span><span class="name">Workflow · Executor · Edge · orchestrators</span></div><div class="ld">Multiple Agents / steps form a graph, flowing along edges; the five ready-made orchestrators are pre-packaged graphs. (<a href="12-workflows.html">L12</a> / <a href="13-orchestration.html">L13</a>)</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Memory</span><span class="name">ContextProvider · HistoryProvider</span></div><div class="ld">Inject context before a run, store history after; Redis / Mem0 / Cosmos are the backends. (<a href="07-sessions-memory.html">L7</a> / <a href="28-memory-backends.html">L28</a>)</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">Ecosystem</span><span class="name">Skill · MCP · A2A / AG-UI · hosting</span></div><div class="ld">Outward-facing: standardized tools (MCP), Agent-to-Agent (A2A), frontends (AG-UI), cloud hosting (Foundry). (<a href="23-skills.html">L23</a>–<a href="26-a2a-agui.html">L26</a>)</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">Ops</span><span class="name">Checkpoint · HITL · Eval · OTel · DevUI</span></div><div class="ld">Make it reliable, debuggable, trustworthy: snapshot / human-review / evaluate / trace / visualize. (<a href="19-durability-hitl.html">L19</a> / <a href="27-eval-timetravel.html">L27</a> / <a href="29-devui.html">L29</a> / <a href="30-observability.html">L30</a>)</div></div>
</div>

<h2>The minimal dependency chain of one run</h2>
<div class="flow">
  <div class="node"><div class="nt">Message in</div><div class="nd">user input</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Agent.run</div><div class="nd">+ Middleware</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">ChatClient</div><div class="nd">ask model</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Tool exec</div><div class="nd">FunctionCall / Result</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Message out</div><div class="nd">AgentResponse</div></div>
</div>

<h2>Reverse index: find a lesson from a question</h2>
<table class="t">
  <tr><th>I want to…</th><th>Go to</th></tr>
  <tr><td>understand what actually happens in one <span class="mono">run()</span></td><td><a href="03-lifecycle.html">L3</a> · <a href="08-agent-internals.html">L8</a></td></tr>
  <tr><td>let the Agent call my function / external tools</td><td><a href="06-tools.html">L6</a> · <a href="24-mcp.html">L24</a></td></tr>
  <tr><td>make the Agent remember across sessions</td><td><a href="07-sessions-memory.html">L7</a> · <a href="28-memory-backends.html">L28</a></td></tr>
  <tr><td>insert my own logic before/after each call</td><td><a href="11-middleware.html">L11</a> · <a href="18-custom-middleware.html">L18</a></td></tr>
  <tr><td>make multiple Agents cooperate on a task</td><td><a href="12-workflows.html">L12</a> · <a href="13-orchestration.html">L13</a></td></tr>
  <tr><td>recover from failure, require human approval</td><td><a href="19-durability-hitl.html">L19</a></td></tr>
  <tr><td>see every step / debug a slow production run</td><td><a href="29-devui.html">L29</a> · <a href="30-observability.html">L30</a></td></tr>
  <tr><td>evaluate whether the Agent's output is good</td><td><a href="27-eval-timetravel.html">L27</a></td></tr>
</table>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>The whole framework is <strong>layered</strong>: Message/Content is bedrock, then ChatClient → Agent → orchestration → ecosystem → ops on top.</li>
    <li>Every term greps to a <strong>real source location</strong> (line numbers in this table are verified)—when a concept is unclear, go read those lines.</li>
    <li>Can't recall something? Use the <strong>reverse index</strong>: start from "what I want to do" and jump straight to the lesson.</li>
    <li>This lesson is a <strong>map, not a tutorial</strong>—its value is the moment you come back to look something up.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design insight</div>
  <strong>Everything ultimately reduces to "messages in, messages out".</strong> Whether it's an Agent, a workflow, or the cross-machine A2A protocol, what flows underneath is always a Message. It's this single unified "data contract" that lets so many layers compose—which is also why, once you truly get the Message in L4, every lesson up to L27 gets easier.
</div>
"""
