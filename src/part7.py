"""Content for Part 7 (new features): lessons 23-27 — Chinese + English."""

# ---------------------------------------------------------------------------
L23_ZH = r"""
<p class="lead"><strong>Agent Skills（技能）</strong>让你把领域知识打包成可发现、可复用的模块——
Agent 不再只有工具，还有<strong>知识库</strong>。</p>

<div class="card analogy">
  <div class="tag">📚 生活类比</div>
  工具是<strong>锤子、扳手</strong>（能做动作），技能是<strong>操作手册 + 参考资料</strong>（知道怎么做、什么背景知识）。
  一个老师傅 = 工具 + 技能：既能动手，又有经验。
</div>

<h2>核心概念</h2>
<table class="t">
  <tr><th>概念</th><th>作用</th><th>源码</th></tr>
  <tr><td class="mono">Skill</td><td>一个完整技能 = 资源 + 脚本 + 元数据</td><td class="mono">_skills.py</td></tr>
  <tr><td class="mono">SkillResource</td><td>技能附带的知识文件（文本/代码/文档）</td><td class="mono">_skills.py</td></tr>
  <tr><td class="mono">SkillScript</td><td>技能可以执行的脚本（代码片段）</td><td class="mono">_skills.py</td></tr>
  <tr><td class="mono">SkillsSource</td><td>技能的来源（文件夹 / 代码 / MCP）</td><td class="mono">_skills.py</td></tr>
  <tr><td class="mono">InlineSkill</td><td>代码中直接定义的技能</td><td class="mono">_skills.py</td></tr>
</table>

<h2>定义一个技能</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">代码定义技能</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> InlineSkill, InlineSkillResource, SkillFrontmatter

skill = InlineSkill(
    frontmatter=SkillFrontmatter(
        name=<span class="st">"company-policies"</span>,
        description=<span class="st">"Company HR policies and guidelines"</span>,
    ),
    instructions=<span class="st">"回答员工问题时应用以下 HR 政策。"</span>,
    resources=[
        InlineSkillResource(
            name=<span class="st">"leave-policy"</span>,
            content=<span class="st">"Employees get 20 days PTO per year..."</span>,
        ),
    ],
)</pre>
</div>

<h2>追踪一个 Skill 的装载与调用</h2>
<p>抽象讲完，我们端到端走一遍：一个 HR 助理 Agent 挂了一个 <span class="mono">company-policies</span> 技能，
用户问<strong>「我一年有几天年假？」</strong>。关键在于——技能<strong>不是</strong>一上来就把整本员工手册塞进 prompt，
而是按<strong>渐进式披露（progressive disclosure）</strong>三步走：先<strong>广告</strong>标题、用时才<strong>装载</strong>正文、需要时再<strong>读取</strong>资源
（<span class="mono">_skills.py:19</span> 的模块注释正是这么写的）。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">挂载技能</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent, InlineSkill, InlineSkillResource, SkillFrontmatter, SkillsProvider

skill = InlineSkill(
    frontmatter=SkillFrontmatter(name=<span class="st">"company-policies"</span>,
                                 description=<span class="st">"公司 HR 政策与员工手册"</span>),
    instructions=<span class="st">"回答员工问题时，引用对应的 HR 政策资源。"</span>,
    resources=[InlineSkillResource(name=<span class="st">"leave-policy"</span>,
                                   content=<span class="st">"全职员工每年 20 天带薪年假，按工龄每满 3 年 +1 天……"</span>)],
)
agent = Agent(client=client, context_providers=SkillsProvider([skill]))   <span class="cm"># 技能 = 一个 ContextProvider</span>
reply = <span class="kw">await</span> agent.run(<span class="st">"我一年有几天年假？"</span>)</pre>
</div>

<div class="vflow">
  <div class="step"><div class="num">0</div><div class="sc"><h4>注册：技能即上下文提供者</h4>
    <p><span class="mono">SkillsProvider</span>（<span class="mono">_skills.py:1719</span>）是一个 <span class="mono">ContextProvider</span>。
    它<strong>不</strong>把正文塞进系统提示，只在每次 <span class="mono">run()</span> 前参与「组装上下文」这一步——和你在<a href="07-sessions-memory.html">第 7 课</a>见过的记忆注入是同一套机制。</p></div></div>
  <div class="step"><div class="num">1</div><div class="sc"><h4>广告（Advertise）：只注入「标题页」</h4>
    <p>provider 把每个技能的 <strong>name + description</strong> 包进 <span class="mono">&lt;available_skills&gt;</span> 注入系统提示，
    约 <strong>~100 token/技能</strong>（<span class="mono">_skills.py:1732</span>）。模型此刻只知道「有一个 company-policies 技能」，<strong>看不到正文</strong>。</p>
<pre class="code"><span class="cm"># 注入到 system prompt 的内容（节选）</span>
&lt;available_skills&gt;
  &lt;skill name=<span class="st">"company-policies"</span>
         description=<span class="st">"公司 HR 政策与员工手册"</span>/&gt;
&lt;/available_skills&gt;
<span class="cm"># 提示还告诉模型：用 load_skill 取指令、用 read_skill_resource 读资源</span></pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>模型决策：这题对口 → 调 load_skill</h4>
    <p>「年假」与 company-policies 的 description 对口，模型<strong>自己</strong>发起一次工具调用
    <span class="mono">load_skill(skill_name="company-policies")</span>——装不装载由模型决定，不是框架硬塞。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>装载（Load）：合成正文回灌</h4>
    <p>框架执行 <span class="mono">load_skill</span> 工具 → 调 <span class="mono">skill.get_content()</span>（<span class="mono">_skills.py:782</span>）→
    返回一段合成的 XML 正文（含 instructions + 资源/脚本清单）注入对话。此刻模型才「看见」指令。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>按需读资源（Read resource）</h4>
    <p>正文里列出了 <span class="mono">leave-policy</span> 资源，模型再调
    <span class="mono">read_skill_resource(...)</span> → 返回 <span class="mono">InlineSkillResource.content</span>（「20 天……按工龄递增」）。</p>
<pre class="code">FunctionCallContent(name=<span class="st">"read_skill_resource"</span>,
                    arguments={<span class="st">"skill_name"</span>: <span class="st">"company-policies"</span>,
                               <span class="st">"resource_name"</span>: <span class="st">"leave-policy"</span>})
<span class="cm"># → "全职员工每年 20 天带薪年假，按工龄每满 3 年 +1 天……"</span></pre></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>（可选）执行脚本：run_skill_script</h4>
    <p>若技能带了脚本（如「按入职日期算今年应休天数」），模型调 <span class="mono">run_skill_script</span>。
    若 provider 设 <span class="mono">require_script_approval=True</span>（<span class="mono">_skills.py:2160</span>），此处先<strong>插入人工审批</strong>再执行。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>产出：综合指令 + 资源作答</h4>
    <p>模型把 instructions（「引用对应政策」）和资源内容拼起来，回答「20 天起，按工龄递增……」。
    整轮里，<strong>员工手册的全文从未一次性进入 context</strong>。</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 读懂这条轨迹</div>
  三个常被忽略的点：①<strong>广告 ≠ 装载</strong>——平时只花 ~100 token 挂个「标题」，正文与资源都到<em>用时</em>才进 context，
  这正是技能能「挂很多、却不撑爆上下文」的根因；②<strong>装载由模型驱动</strong>——<span class="mono">load_skill</span> / <span class="mono">read_skill_resource</span>
  是框架注入的<strong>工具</strong>（<span class="mono">_skills.py:2128</span>），模型像调别的工具一样调它们；③<strong>脚本可加审批闸</strong>——
  可执行代码默认 <span class="mono">never_require</span>，设 <span class="mono">require_script_approval=True</span> 即变 <span class="mono">always_require</span>，把「危险动作」交人把关。
</div>

<h2>技能由什么组成</h2>
<p>把上面用到的对象拆开看，一个技能就是<strong>四层</strong>叠起来的——元信息在最上（决定「要不要装载」），正文和资源在下（装载后才看得见）：</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">L1</span><span class="name">SkillFrontmatter</span></div>
    <div class="ld">发现用的元信息：<span class="mono">name</span> / <span class="mono">description</span> / <span class="mono">license</span> / <span class="mono">compatibility</span> / <span class="mono">allowed_tools</span>（<span class="mono">_skills.py:557</span>）。<strong>只有这层进「广告」。</strong></div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">指令</span><span class="name">instructions</span></div>
    <div class="ld">技能的「操作手册」正文——告诉模型该怎么做。装载（<span class="mono">load_skill</span>）后才注入。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">资源</span><span class="name">resources[]</span></div>
    <div class="ld"><span class="mono">InlineSkillResource</span>：只读知识，可为静态 <span class="mono">content</span> 或动态 <span class="mono">function</span>（<span class="mono">_skills.py:121</span>）。<span class="mono">read_skill_resource</span> 按需取。</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">脚本</span><span class="name">scripts[]</span></div>
    <div class="ld"><span class="mono">InlineSkillScript</span>：可执行代码（<span class="mono">_skills.py:315</span>），通过 <span class="mono">run_skill_script</span> 运行，可挂审批闸。</div></div>
</div>

<p>这四层对应渐进式披露的三段「流量阀」——左边便宜（一直在），越往右越贵（按需触发）：</p>
<div class="flow">
  <div class="node hl"><div class="nt">Advertise</div><div class="nd">name+desc · ~100 token</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">load_skill</div><div class="nd">注入 instructions 正文</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">read_skill_resource</div><div class="nd">按名取资源内容</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">run_skill_script</div><div class="nd">（可选）执行脚本 · 可审批</div></div>
</div>

<h2>🔍 真实源码：三个对象怎么搭起来</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_skills.py</span><span class="ln">InlineSkill / SkillFrontmatter / SkillsProvider（简化自 :729 / :557 / :1719）</span></div>
<pre class="code"><span class="kw">class</span> <span class="fn">SkillFrontmatter</span>:                          <span class="cm"># :557 —— L1 发现用元信息</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, *, name, description,
                 license=<span class="kw">None</span>, compatibility=<span class="kw">None</span>,
                 allowed_tools=<span class="kw">None</span>, metadata=<span class="kw">None</span>):
        _validate_skill_name(name)                  <span class="cm"># 名字限小写字母/数字/连字符</span>
        ...

<span class="kw">class</span> <span class="fn">InlineSkill</span>(Skill):                          <span class="cm"># :729 —— 代码内联技能</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, *, frontmatter: SkillFrontmatter,
                 instructions: str, resources=<span class="kw">None</span>, scripts=<span class="kw">None</span>): ...
    <span class="kw">async def</span> <span class="fn">get_content</span>(self) -&gt; str:            <span class="cm"># :782 —— 合成 XML 正文（带缓存）</span>
        <span class="kw">return</span> _build_skill_content(name, description,
                   instructions, resources, scripts)

<span class="kw">class</span> <span class="fn">SkillsProvider</span>(ContextProvider):           <span class="cm"># :1719 —— 把技能接到 Agent</span>
    <span class="cm"># 每次 run 前：注入 &lt;available_skills&gt; 系统提示，</span>
    <span class="cm"># 并挂上 load_skill / read_skill_resource / run_skill_script 三个工具（:2128）</span></pre>
</div>
<p>三者职责分得很干净：<span class="mono">SkillFrontmatter</span> 只管「怎么被发现」，<span class="mono">InlineSkill</span> 管「正文与资源放哪」，
<span class="mono">SkillsProvider</span> 管「怎么接到 Agent 的上下文与工具上」。注意 <span class="mono">SkillsProvider</span> 继承 <span class="mono">ContextProvider</span>——
技能复用的是第 7 课那套「上下文注入」机制，并非另起炉灶。</p>

<h2>为什么把「技能」做成声明式资源</h2>
<p>最朴素的做法是把知识直接写进 <span class="mono">instructions</span>（系统提示）。能跑，但有四笔隐性成本，技能正是来抵这几笔账的：</p>
<table class="t">
  <tr><th>维度</th><th>知识硬塞进 prompt</th><th>Agent Skills（声明式）</th></tr>
  <tr><td><strong>Token 成本</strong></td><td>每次请求都背着<strong>全部</strong>知识，越加越贵</td><td>平时只广告 ~100 token/技能，<strong>用时才装载</strong>正文与资源</td></tr>
  <tr><td><strong>可维护</strong></td><td>知识与指令糊成一坨，改一处要通读全文</td><td>每个技能有独立 <span class="mono">name/description/version</span>，可单独更新</td></tr>
  <tr><td><strong>可组合</strong></td><td>难以跨 Agent 共享，复制粘贴满天飞</td><td><span class="mono">AggregatingSkillsSource</span> 聚合多源，<span class="mono">Filtering/Deduplicating</span> 过滤去重</td></tr>
  <tr><td><strong>安全</strong></td><td>来源不清，易把不可信内容当指令</td><td>文件技能元信息<strong>先 XML 转义再注入</strong>，资源读取防路径穿越（<span class="mono">_skills.py:39</span>）</td></tr>
</table>
<p>一句话：<strong>把「知识」从「指令」里拆出来，按需付费</strong>。当你只有一两句固定背景时，写进 instructions 反而最省事——
技能的价值要在「知识多、会变、需复用、要管权限」的场景才真正兑现。这与
<a href="24-mcp.html">下一课的 MCP</a> 恰是一对：技能管「你的私有知识怎么声明」，MCP 管「外部工具怎么标准化接入」。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 技能的三种来源 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">技能可以从三种来源加载：
<pre class="code"><span class="cm"># 1. 代码内联定义（InlineSkill）</span>
skill = InlineSkill(frontmatter=..., instructions=...)

<span class="cm"># 2. 文件系统加载（文件夹里放 .md/.py 等）</span>
<span class="cm"># samples/02-agents/skills/file_based_skill/</span>

<span class="cm"># 3. MCP 服务器提供（MCPSkill）</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> MCPSkill
<span class="cm"># 通过 MCP 协议远程获取技能</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">Agent 光有工具（能做动作）不够——它还需要<strong>领域知识</strong>才能正确使用工具。
        比如客服 Agent 需要知道公司的退货政策才能正确回答退货问题。
        技能把"知识"变成可管理、可版本控制、可分享的模块。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 把技能做成<strong>一等公民</strong>：Skill 对象有 name、description、resources（知识）、scripts（可执行代码），
        通过 <span class="mono">SkillsSource</span> 和 <span class="mono">AggregatingSkillsSource</span> 聚合多个来源。
        Agent 在 run 时自动发现并注入相关技能到上下文。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>把知识硬编码进 instructions</strong>（简单但不可复用）；
        <strong>用 ContextProvider + RAG</strong>（适合大规模知识库，但缺少"脚本"能力）；
        <strong>用 MCP 资源</strong>（通过协议暴露知识，MAF 的 MCPSkill 正是这种方式）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> SkillResource vs SkillScript <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a"><span class="mono">SkillResource</span> 是<strong>只读知识</strong>（文本、文档、数据文件），
        <span class="mono">SkillScript</span> 是<strong>可执行代码</strong>（Python 脚本片段）：
<pre class="code"><span class="cm"># Resource: 只读知识</span>
InlineSkillResource(name=<span class="st">"faq"</span>, content=<span class="st">"Q: ... A: ..."</span>)

<span class="cm"># Script: 可执行代码</span>
InlineSkillScript(name=<span class="st">"calc"</span>, code=<span class="st">"result = price * 1.1"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">有些领域知识是<strong>静态的</strong>（退货政策文档），有些需要<strong>动态计算</strong>（税率计算公式）。
        把两者都放在技能里，Agent 既能读知识又能跑计算。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">Resource 和 Script 都挂在同一个 Skill 下，通过 <span class="mono">SkillFrontmatter</span> 描述元数据（名称、描述、兼容性）。
        框架在 Agent run 时把 Resource 内容注入上下文，Script 则可通过 <span class="mono">SkillScriptRunner</span> 执行。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>Tool 里内嵌知识</strong>（不够模块化）；
        <strong>独立的知识管理服务</strong>（更灵活但更复杂）；
        <strong>LangChain 的 Document + Retriever</strong>（纯检索，不支持脚本执行）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 技能发现与聚合 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">多个来源的技能可以聚合：
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> AggregatingSkillsSource

source = AggregatingSkillsSource(sources=[
    file_skills_source,    <span class="cm"># 文件夹里的技能</span>
    inline_skills_source,  <span class="cm"># 代码定义的技能</span>
    mcp_skills_source,     <span class="cm"># MCP 服务器的技能</span>
])</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">真实项目里知识来自多处：团队内部文档、外部 API、代码库。
        <span class="mono">AggregatingSkillsSource</span> 让你把这些来源统一聚合，
        Agent 只需要从一个入口发现所有可用技能。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">聚合是<strong>可插拔</strong>的：每个 <span class="mono">SkillsSource</span> 独立实现 "列出技能" 接口，
        <span class="mono">AggregatingSkillsSource</span> 合并它们。新来源只需实现 <span class="mono">SkillsSource</span> 协议。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>单一来源硬编码</strong>（简单但不可扩展）；
        <strong>用搜索引擎做技能发现</strong>（更灵活但更复杂）；
        <strong>用 MCP resource 列表</strong>（协议标准化，但要求所有来源都支持 MCP）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 样例代码一览 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a"><span class="mono">samples/02-agents/skills/</span> 下有 7 个样例：
<pre class="code">skills/
├── class_based_skill/     <span class="cm"># 类定义的技能</span>
├── code_defined_skill/    <span class="cm"># 代码内联定义</span>
├── file_based_skill/      <span class="cm"># 文件系统加载</span>
├── mcp_based_skill/       <span class="cm"># MCP 远程技能</span>
├── mixed_skills/          <span class="cm"># 混合多种来源</span>
├── script_approval/       <span class="cm"># 脚本执行需审批</span>
└── skill_filtering/       <span class="cm"># 按条件过滤技能</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">看样例比读文档快——每个样例覆盖一种使用模式。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">样例从简到繁排列：先代码内联（最简单）→ 文件加载 → MCP → 混合 → 审批 → 过滤。
        每个样例单文件，可直接跑。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">没有特定替代——这些是官方参考实现。如果你的场景不在其中，
        参照 <span class="mono">mixed_skills</span> 组合多种模式即可。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><strong>Skill = 知识模块</strong>：Resource（只读知识）+ Script（可执行代码）+ 元数据。</li>
    <li>三种来源：<strong>代码内联</strong>（InlineSkill）、<strong>文件系统</strong>、<strong>MCP 远程</strong>。</li>
    <li><span class="mono">AggregatingSkillsSource</span> 聚合多个来源，Agent 自动发现。</li>
    <li>技能 ≠ 工具：工具做动作，技能提供知识和可执行代码。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>知识和代码被统一抽象成"技能"</strong>——不再散落在 instructions、ContextProvider、工具各处。
  一个技能模块可以独立分发、版本控制、跨 Agent 复用。
</div>
"""

L23_EN = r"""
<p class="lead"><strong>Agent Skills</strong> let you package domain knowledge into discoverable, reusable modules —
Agents get not just tools but <strong>knowledge bases</strong>.</p>

<div class="card analogy">
  <div class="tag">📚 Analogy</div>
  Tools are <strong>hammers and wrenches</strong> (they do actions); skills are <strong>operation manuals + reference
  material</strong> (they know how and why). A master craftsman = tools + skills: capable hands plus experience.
</div>

<h2>Core concepts</h2>
<table class="t">
  <tr><th>Concept</th><th>Role</th><th>Source</th></tr>
  <tr><td class="mono">Skill</td><td>A complete skill = resources + scripts + metadata</td><td class="mono">_skills.py</td></tr>
  <tr><td class="mono">SkillResource</td><td>Knowledge files attached to a skill</td><td class="mono">_skills.py</td></tr>
  <tr><td class="mono">SkillScript</td><td>Executable code snippets in a skill</td><td class="mono">_skills.py</td></tr>
  <tr><td class="mono">SkillsSource</td><td>Where skills come from (folder / code / MCP)</td><td class="mono">_skills.py</td></tr>
  <tr><td class="mono">InlineSkill</td><td>Skill defined directly in code</td><td class="mono">_skills.py</td></tr>
</table>

<h2>Define a skill</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">code-defined skill</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> InlineSkill, InlineSkillResource, SkillFrontmatter

skill = InlineSkill(
    frontmatter=SkillFrontmatter(
        name=<span class="st">"company-policies"</span>,
        description=<span class="st">"Company HR policies and guidelines"</span>,
    ),
    instructions=<span class="st">"Apply these HR policies when answering employee questions."</span>,
    resources=[
        InlineSkillResource(
            name=<span class="st">"leave-policy"</span>,
            content=<span class="st">"Employees get 20 days PTO per year..."</span>,
        ),
    ],
)</pre>
</div>

<h2>Trace one skill being loaded and used</h2>
<p>Enough abstraction — let's walk it end to end: an HR-assistant Agent carries a <span class="mono">company-policies</span> skill,
and a user asks <strong>"How many days of annual leave do I get?"</strong>. The key idea: a skill does <strong>not</strong>
dump the whole employee handbook into the prompt up front. It follows <strong>progressive disclosure</strong> in three steps —
first <strong>advertise</strong> the title, <strong>load</strong> the body only when needed, then <strong>read</strong> resources on demand
(exactly as the module comment at <span class="mono">_skills.py:19</span> describes).</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">attach the skill</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent, InlineSkill, InlineSkillResource, SkillFrontmatter, SkillsProvider

skill = InlineSkill(
    frontmatter=SkillFrontmatter(name=<span class="st">"company-policies"</span>,
                                 description=<span class="st">"Company HR policies and handbook"</span>),
    instructions=<span class="st">"When answering employee questions, cite the matching HR policy resource."</span>,
    resources=[InlineSkillResource(name=<span class="st">"leave-policy"</span>,
                                   content=<span class="st">"Full-time staff get 20 days PTO/year, +1 day per 3 years tenure..."</span>)],
)
agent = Agent(client=client, context_providers=SkillsProvider([skill]))   <span class="cm"># a skill = a ContextProvider</span>
reply = <span class="kw">await</span> agent.run(<span class="st">"How many days of annual leave do I get?"</span>)</pre>
</div>

<div class="vflow">
  <div class="step"><div class="num">0</div><div class="sc"><h4>Register: a skill is a context provider</h4>
    <p><span class="mono">SkillsProvider</span> (<span class="mono">_skills.py:1719</span>) is a <span class="mono">ContextProvider</span>.
    It does <strong>not</strong> stuff the body into the system prompt; it only joins the "assemble context" step before each
    <span class="mono">run()</span> — the same mechanism as memory injection from <a href="07-sessions-memory.html">Lesson 7</a>.</p></div></div>
  <div class="step"><div class="num">1</div><div class="sc"><h4>Advertise: inject only the "title page"</h4>
    <p>The provider wraps each skill's <strong>name + description</strong> into <span class="mono">&lt;available_skills&gt;</span> and injects it into the
    system prompt — about <strong>~100 tokens/skill</strong> (<span class="mono">_skills.py:1732</span>). Right now the model only knows
    "there is a company-policies skill" and <strong>cannot see the body</strong>.</p>
<pre class="code"><span class="cm"># what lands in the system prompt (excerpt)</span>
&lt;available_skills&gt;
  &lt;skill name=<span class="st">"company-policies"</span>
         description=<span class="st">"Company HR policies and handbook"</span>/&gt;
&lt;/available_skills&gt;
<span class="cm"># the prompt also tells the model: use load_skill for instructions, read_skill_resource for resources</span></pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Model decides: this matches → call load_skill</h4>
    <p>"Annual leave" matches the company-policies description, so the model <strong>itself</strong> issues a tool call
    <span class="mono">load_skill(skill_name="company-policies")</span> — whether to load is the model's choice, not forced by the framework.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Load: synthesize the body and feed it back</h4>
    <p>The framework runs the <span class="mono">load_skill</span> tool → calls <span class="mono">skill.get_content()</span> (<span class="mono">_skills.py:782</span>) →
    returns a synthesized XML body (instructions + a list of resources/scripts) into the conversation. Only now does the model "see" the instructions.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Read a resource on demand</h4>
    <p>The body lists a <span class="mono">leave-policy</span> resource, so the model calls
    <span class="mono">read_skill_resource(...)</span> → returns <span class="mono">InlineSkillResource.content</span> ("20 days... increasing with tenure").</p>
<pre class="code">FunctionCallContent(name=<span class="st">"read_skill_resource"</span>,
                    arguments={<span class="st">"skill_name"</span>: <span class="st">"company-policies"</span>,
                               <span class="st">"resource_name"</span>: <span class="st">"leave-policy"</span>})
<span class="cm"># -> "Full-time staff get 20 days PTO/year, +1 day per 3 years tenure..."</span></pre></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>(Optional) run a script: run_skill_script</h4>
    <p>If the skill ships a script (e.g. "compute days owed this year from the hire date"), the model calls <span class="mono">run_skill_script</span>.
    If the provider sets <span class="mono">require_script_approval=True</span> (<span class="mono">_skills.py:2160</span>), a <strong>human approval</strong> is inserted before it runs.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Produce: answer from instructions + resource</h4>
    <p>The model combines the instructions ("cite the matching policy") with the resource content and answers "20 days, increasing with tenure...".
    Across the whole turn, <strong>the full handbook never entered the context at once</strong>.</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 Reading this trace</div>
  Three easily missed points: ① <strong>advertise &ne; load</strong> — normally you spend only ~100 tokens on a "title"; the body and resources enter
  context only <em>when used</em>, which is exactly why you can attach many skills without blowing the context window; ② <strong>loading is model-driven</strong> —
  <span class="mono">load_skill</span> / <span class="mono">read_skill_resource</span> are <strong>tools</strong> the framework injects (<span class="mono">_skills.py:2128</span>), and the model calls them like any other tool;
  ③ <strong>scripts can gate on approval</strong> — executable code defaults to <span class="mono">never_require</span>; set <span class="mono">require_script_approval=True</span> to flip it to
  <span class="mono">always_require</span> and put a human in front of "dangerous" actions.
</div>

<h2>What a skill is made of</h2>
<p>Pulling apart the objects above, a skill is <strong>four layers</strong> stacked up — metadata on top (decides "load or not"), body and resources below (visible only after loading):</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">L1</span><span class="name">SkillFrontmatter</span></div>
    <div class="ld">Discovery metadata: <span class="mono">name</span> / <span class="mono">description</span> / <span class="mono">license</span> / <span class="mono">compatibility</span> / <span class="mono">allowed_tools</span> (<span class="mono">_skills.py:557</span>). <strong>Only this layer is advertised.</strong></div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">instr</span><span class="name">instructions</span></div>
    <div class="ld">The skill's "operating manual" body — tells the model how to act. Injected only after <span class="mono">load_skill</span>.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">res</span><span class="name">resources[]</span></div>
    <div class="ld"><span class="mono">InlineSkillResource</span>: read-only knowledge, either static <span class="mono">content</span> or a dynamic <span class="mono">function</span> (<span class="mono">_skills.py:121</span>). Fetched on demand via <span class="mono">read_skill_resource</span>.</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">script</span><span class="name">scripts[]</span></div>
    <div class="ld"><span class="mono">InlineSkillScript</span>: executable code (<span class="mono">_skills.py:315</span>), run via <span class="mono">run_skill_script</span>, optionally behind an approval gate.</div></div>
</div>

<p>These four layers map onto progressive disclosure's three "flow valves" — cheap on the left (always present), pricier toward the right (triggered on demand):</p>
<div class="flow">
  <div class="node hl"><div class="nt">Advertise</div><div class="nd">name+desc · ~100 tokens</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">load_skill</div><div class="nd">inject instructions body</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">read_skill_resource</div><div class="nd">fetch resource by name</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">run_skill_script</div><div class="nd">(optional) run script · approvable</div></div>
</div>

<h2>🔍 Real source: how the three objects fit together</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_skills.py</span><span class="ln">InlineSkill / SkillFrontmatter / SkillsProvider (simplified from :729 / :557 / :1719)</span></div>
<pre class="code"><span class="kw">class</span> <span class="fn">SkillFrontmatter</span>:                          <span class="cm"># :557 -- L1 discovery metadata</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, *, name, description,
                 license=<span class="kw">None</span>, compatibility=<span class="kw">None</span>,
                 allowed_tools=<span class="kw">None</span>, metadata=<span class="kw">None</span>):
        _validate_skill_name(name)                  <span class="cm"># lowercase letters/digits/hyphens only</span>
        ...

<span class="kw">class</span> <span class="fn">InlineSkill</span>(Skill):                          <span class="cm"># :729 -- code-defined skill</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, *, frontmatter: SkillFrontmatter,
                 instructions: str, resources=<span class="kw">None</span>, scripts=<span class="kw">None</span>): ...
    <span class="kw">async def</span> <span class="fn">get_content</span>(self) -&gt; str:            <span class="cm"># :782 -- synthesize XML body (cached)</span>
        <span class="kw">return</span> _build_skill_content(name, description,
                   instructions, resources, scripts)

<span class="kw">class</span> <span class="fn">SkillsProvider</span>(ContextProvider):           <span class="cm"># :1719 -- wire skills into the Agent</span>
    <span class="cm"># before each run: inject the &lt;available_skills&gt; system prompt, and</span>
    <span class="cm"># attach the load_skill / read_skill_resource / run_skill_script tools (:2128)</span></pre>
</div>
<p>The responsibilities split cleanly: <span class="mono">SkillFrontmatter</span> owns "how it is discovered", <span class="mono">InlineSkill</span> owns "where the body and resources live",
and <span class="mono">SkillsProvider</span> owns "how it wires into the Agent's context and tools". Note <span class="mono">SkillsProvider</span> subclasses <span class="mono">ContextProvider</span> —
skills reuse the same "context injection" mechanism from Lesson 7, not a parallel one.</p>

<h2>Why make a "skill" a declarative resource</h2>
<p>The naive approach is to write knowledge straight into <span class="mono">instructions</span> (the system prompt). It works, but carries four hidden costs that skills exist to offset:</p>
<table class="t">
  <tr><th>Dimension</th><th>Knowledge hardcoded in the prompt</th><th>Agent Skills (declarative)</th></tr>
  <tr><td><strong>Token cost</strong></td><td>Every request carries <strong>all</strong> the knowledge; cost grows as you add more</td><td>Only ~100 tokens/skill advertised; the body and resources are <strong>loaded only when used</strong></td></tr>
  <tr><td><strong>Maintainable</strong></td><td>Knowledge and instructions congeal into one blob; one edit means re-reading it all</td><td>Each skill has its own <span class="mono">name/description/version</span> and can be updated alone</td></tr>
  <tr><td><strong>Composable</strong></td><td>Hard to share across Agents; copy-paste everywhere</td><td><span class="mono">AggregatingSkillsSource</span> merges sources; <span class="mono">Filtering/Deduplicating</span> trim and dedupe</td></tr>
  <tr><td><strong>Secure</strong></td><td>Murky provenance; easy to treat untrusted text as instructions</td><td>File-skill metadata is <strong>XML-escaped before injection</strong>; resource reads guard against path traversal (<span class="mono">_skills.py:39</span>)</td></tr>
</table>
<p>In one line: <strong>separate "knowledge" from "instructions" and pay only on demand</strong>. When you have just a sentence or two of fixed background,
writing it into instructions is actually simplest — skills pay off in the "lots of knowledge, it changes, needs reuse, needs permissioning" scenarios.
This pairs with <a href="24-mcp.html">the next lesson on MCP</a>: skills govern "how your private knowledge is declared", MCP governs "how external tools are standardized in".</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Three skill sources <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Skills can be loaded from three sources:
<pre class="code"><span class="cm"># 1. Inline (InlineSkill)</span>
skill = InlineSkill(frontmatter=..., instructions=...)

<span class="cm"># 2. File system (folder with .md/.py files)</span>
<span class="cm"># samples/02-agents/skills/file_based_skill/</span>

<span class="cm"># 3. MCP server (MCPSkill)</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> MCPSkill
<span class="cm"># fetch skills remotely via MCP protocol</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Tools alone (actions) aren't enough — an Agent needs <strong>domain knowledge</strong> to use tools correctly.
        A customer-service Agent must know the company's return policy to answer return questions.
        Skills turn "knowledge" into manageable, version-controlled, shareable modules.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF makes skills <strong>first-class</strong>: a Skill has name, description, resources (knowledge), scripts (executable code).
        <span class="mono">SkillsSource</span> and <span class="mono">AggregatingSkillsSource</span> aggregate multiple sources.
        The Agent auto-discovers and injects relevant skills at run time.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Hardcode knowledge in instructions</strong> (simple but not reusable);
        <strong>ContextProvider + RAG</strong> (good for large knowledge bases but no script capability);
        <strong>MCP resources</strong> (protocol-standardised; MAF's MCPSkill is exactly this).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> SkillResource vs SkillScript <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a"><span class="mono">SkillResource</span> is <strong>read-only knowledge</strong>;
        <span class="mono">SkillScript</span> is <strong>executable code</strong>:
<pre class="code"><span class="cm"># Resource: read-only knowledge</span>
InlineSkillResource(name=<span class="st">"faq"</span>, content=<span class="st">"Q: ... A: ..."</span>)

<span class="cm"># Script: executable code</span>
InlineSkillScript(name=<span class="st">"calc"</span>, code=<span class="st">"result = price * 1.1"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Some domain knowledge is <strong>static</strong> (return policy docs); some needs
        <strong>dynamic computation</strong> (tax-rate formulas). Putting both in a skill lets the Agent read
        knowledge AND run calculations.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Resource and Script both live under the same Skill, described by <span class="mono">SkillFrontmatter</span>.
        The framework injects Resource content into context at run time; Scripts can be executed via
        <span class="mono">SkillScriptRunner</span>.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Embed knowledge in tools</strong> (not modular);
        <strong>Separate knowledge service</strong> (more flexible but more complex);
        <strong>LangChain Document + Retriever</strong> (retrieval only, no script execution).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Skill discovery &amp; aggregation <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Aggregate skills from multiple sources:
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> AggregatingSkillsSource

source = AggregatingSkillsSource(sources=[
    file_skills_source,    <span class="cm"># folder-based</span>
    inline_skills_source,  <span class="cm"># code-defined</span>
    mcp_skills_source,     <span class="cm"># MCP server</span>
])</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Real projects draw knowledge from many places: internal docs, external APIs, codebases.
        <span class="mono">AggregatingSkillsSource</span> unifies them so the Agent discovers all skills from one entry point.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Aggregation is <strong>pluggable</strong>: each <span class="mono">SkillsSource</span> implements a "list skills" interface;
        <span class="mono">AggregatingSkillsSource</span> merges them. New sources just implement the <span class="mono">SkillsSource</span> protocol.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Single hardcoded source</strong> (simple but not extensible);
        <strong>Search engine for skill discovery</strong> (more flexible but more complex);
        <strong>MCP resource lists</strong> (protocol-standardised but requires all sources to support MCP).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Sample code overview <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a"><span class="mono">samples/02-agents/skills/</span> has 7 samples:
<pre class="code">skills/
├── class_based_skill/     <span class="cm"># class-defined skill</span>
├── code_defined_skill/    <span class="cm"># inline code skill</span>
├── file_based_skill/      <span class="cm"># file system loaded</span>
├── mcp_based_skill/       <span class="cm"># MCP remote skill</span>
├── mixed_skills/          <span class="cm"># multiple sources mixed</span>
├── script_approval/       <span class="cm"># script exec needs approval</span>
└── skill_filtering/       <span class="cm"># filter skills by condition</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Samples are faster than docs — each covers one usage pattern.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Samples progress from simple to complex: inline (simplest) → file → MCP → mixed → approval → filtering.
        Each is a single runnable file.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">No specific alternative — these are official reference implementations.
        If your scenario isn't covered, model it after <span class="mono">mixed_skills</span>.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>Skill = knowledge module</strong>: Resource (read-only) + Script (executable) + metadata.</li>
    <li>Three sources: <strong>inline</strong> (InlineSkill), <strong>file system</strong>, <strong>MCP remote</strong>.</li>
    <li><span class="mono">AggregatingSkillsSource</span> merges multiple sources; Agent auto-discovers.</li>
    <li>Skills ≠ tools: tools do actions, skills provide knowledge and executable code.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Knowledge and code unified as "skills"</strong> — no longer scattered across instructions, ContextProviders
  and tools. A skill module can be independently distributed, version-controlled and reused across Agents.
</div>
"""

# L24-L27 placeholders — filled in next steps
L24_ZH = r"""
<p class="lead"><strong>MCP（Model Context Protocol）</strong>是连接工具/资源到 LLM 的<strong>开放标准</strong>——
MAF 既能<strong>调用</strong> MCP 服务器上的工具，也能把 Agent 自身<strong>暴露为</strong> MCP 服务器。</p>

<div class="card analogy">
  <div class="tag">📚 生活类比</div>
  MCP 就像<strong>USB 接口标准</strong>：不管你插的是键盘、鼠标还是硬盘，只要都走 USB 协议就能即插即用。
  MCP 让 LLM 和工具之间有了统一的"接口协议"，不用为每个工具写定制代码。
</div>

<h2>三种传输方式</h2>
<table class="t">
  <tr><th>传输类型</th><th>类名</th><th>适用场景</th></tr>
  <tr><td>Stdio（子进程）</td><td class="mono">MCPStdioTool</td><td>本地 CLI 工具，开发/测试阶段最常用</td></tr>
  <tr><td>HTTP/SSE（Streamable HTTP）</td><td class="mono">MCPStreamableHTTPTool</td><td>远程 Web API，生产部署首选</td></tr>
  <tr><td>WebSocket</td><td class="mono">MCPWebsocketTool</td><td>需要双向实时通信的场景</td></tr>
</table>

<h2>连接 MCP 服务器</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">使用 MCPStdioTool</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent, MCPStdioTool

mcp_tool = MCPStdioTool(
    name=<span class="st">"filesystem"</span>,
    command=<span class="st">"npx"</span>,
    args=[<span class="st">"-y"</span>, <span class="st">"@modelcontextprotocol/server-filesystem"</span>, <span class="st">"/data"</span>],
)

<span class="kw">async with</span> Agent(
    client=client,
    tools=mcp_tool,
    name=<span class="st">"fs-agent"</span>,
) <span class="kw">as</span> agent:
    response = <span class="kw">await</span> agent.run(<span class="st">"List all .txt files"</span>)</pre>
</div>

<h2>追踪一次 MCP 工具调用</h2>
<p>抽象讲完，我们端到端走一遍：一个 Agent 通过 <span class="mono">MCPStdioTool</span> 接上官方的 <strong>filesystem</strong> MCP 服务器，
用户说<strong>「列出 /data 下所有 .txt 文件」</strong>。重点在于：MCP 工具<strong>不是</strong>你写的本地 Python 函数，
而是<strong>另一个进程</strong>里的能力——框架要先<strong>连上它、问它有哪些工具</strong>，再把模型的调用请求<strong>经 stdio 转发</strong>过去执行。</p>

<div class="vflow">
  <div class="step"><div class="num">0</div><div class="sc"><h4>构造：只是描述，还没连接</h4>
    <p><span class="mono">MCPStdioTool(name="filesystem", command="npx", args=[...])</span>（<span class="mono">_mcp.py:2110</span>）此刻只是<strong>一份连接说明</strong>，
    子进程尚未启动。注意它继承自不能直接实例化的基类 <span class="mono">MCPTool</span>（<span class="mono">_mcp.py:263</span>）。</p></div></div>
  <div class="step"><div class="num">1</div><div class="sc"><h4>进入上下文：启动子进程</h4>
    <p><span class="mono">async with agent:</span> 触发工具的 <span class="mono">__aenter__</span>（<span class="mono">_mcp.py:2068</span>）→ <span class="mono">connect()</span>（<span class="mono">:801</span>）。
    框架据 <span class="mono">command/args</span> 造出 <span class="mono">StdioServerParameters</span>，<span class="mono">npx</span> 拉起 filesystem 服务器子进程，建立 stdio 双向管道。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>问它有哪些工具：load_tools</h4>
    <p>连上后调 <span class="mono">load_tools()</span>（<span class="mono">:1208</span>）→ <span class="mono">session.list_tools()</span>（<span class="mono">:1244</span>）。
    远端报出 <span class="mono">list_directory</span> / <span class="mono">read_file</span> / … 每个被包成一个本地 <span class="mono">FunctionTool</span> 放进 <span class="mono">.functions</span>（<span class="mono">:637</span>），其 JSON Schema 转交给模型。</p>
<pre class="code"><span class="cm"># 远端工具被翻译成模型可见的 schema（节选）</span>
[FunctionTool(name=<span class="st">"list_directory"</span>, parameters={<span class="st">"path"</span>: <span class="st">"string"</span>}),
 FunctionTool(name=<span class="st">"read_file"</span>,      parameters={<span class="st">"path"</span>: <span class="st">"string"</span>})]</pre></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>模型决策：要列目录</h4>
    <p>模型看到有 <span class="mono">list_directory</span>，发起一次工具调用 —— 与调用普通本地工具<strong>语法完全一样</strong>，它并不知道这是个远端进程：</p>
<pre class="code">FunctionCallContent(name=<span class="st">"list_directory"</span>,
                    arguments={<span class="st">"path"</span>: <span class="st">"/data"</span>})</pre></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>经 stdio 转发：call_tool</h4>
    <p>框架把调用交给 <span class="mono">call_tool("list_directory", path="/data")</span>（<span class="mono">:1422</span>）→
    <span class="mono">session.call_tool(name, arguments=...)</span>（<span class="mono">:1481</span>），把一条 JSON-RPC 请求经 stdio 写给子进程。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>远端执行 → 结果回灌</h4>
    <p>filesystem 子进程在<strong>真实文件系统</strong>上跑 <span class="mono">list_directory</span>，返回 <span class="mono">CallToolResult</span>；
    默认解析器把它转成字符串/<span class="mono">Content</span> 回灌对话。模型据此筛出 <span class="mono">.txt</span> 并作答。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>退出上下文：收摊</h4>
    <p><span class="mono">async with</span> 结束 → <span class="mono">__aexit__</span>（<span class="mono">_mcp.py:2089</span>）关闭 stdio 管道、终止子进程。连接<strong>有借有还</strong>。</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 读懂这条轨迹</div>
  三个关键点：①<strong>工具是「发现」来的，不是写死的</strong>——<span class="mono">list_tools()</span> 在运行时拉取远端工具清单，远端加了新工具，你的 Agent 无需改代码就能用；
  ②<strong>模型对「远近」无感</strong>——远端工具被包成本地 <span class="mono">FunctionTool</span>，模型发 <span class="mono">FunctionCallContent</span> 的方式和调本地 <code>@tool</code> 一模一样（见<a href="06-tools.html">第 6 课</a>）；
  ③<strong>连接是有状态的</strong>——必须 <span class="mono">async with</span>（或显式 <span class="mono">connect()</span>/<span class="mono">__aexit__</span>）成对管理子进程生命周期，这也是 MCP 工具与无状态本地函数最大的不同。
</div>

<h2>一个基类，三种传输</h2>
<p>无论走子进程、HTTP 还是 WebSocket，<strong>上层 Agent 代码完全一样</strong>——差异被关进三个子类，共享同一个基类 <span class="mono">MCPTool</span>：</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">基类</span><span class="name">MCPTool</span></div>
    <div class="ld"><span class="mono">_mcp.py:263</span>。<strong>不能直接实例化</strong>。负责连接生命周期、<span class="mono">load_tools/load_prompts</span>、<span class="mono">call_tool</span>、JSON-RPC 通信、审批与超时（<span class="mono">MCPTaskOptions</span>）。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">子类</span><span class="name">MCPStdioTool(command, args)</span></div>
    <div class="ld"><span class="mono">:2110</span>。启动<strong>本地子进程</strong>，走 stdin/stdout。无需网络，本地 CLI / 开发调试最顺手。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">子类</span><span class="name">MCPStreamableHTTPTool(url)</span></div>
    <div class="ld"><span class="mono">:2254</span>。连<strong>远程 HTTP/SSE</strong> 端点，可带 <span class="mono">headers</span> / <span class="mono">header_provider</span> 做鉴权。生产部署首选。</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">子类</span><span class="name">MCPWebsocketTool(url)</span></div>
    <div class="ld"><span class="mono">:2456</span>。走 <strong>WebSocket（wss://）</strong>，适合需要长连接、双向实时推送的场景。</div></div>
</div>

<p>把连接过程横过来看，就是一条固定的生命周期流水线——三种传输只在「第 1 步怎么连上」不同，后面都一样：</p>
<div class="flow">
  <div class="node"><div class="nt">构造</div><div class="nd">命令/URL · 未连接</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">connect</div><div class="nd">子进程 / HTTP / WS</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">list_tools</div><div class="nd">发现远端工具</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">→ FunctionTool</div><div class="nd">包成本地工具</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">call_tool</div><div class="nd">转发 · 执行 · 回灌</div></div>
</div>

<h2>🔍 真实源码：基类与传输子类的关系</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_mcp.py</span><span class="ln">MCPTool / MCPStdioTool（简化自 :263 / :2110）</span></div>
<pre class="code"><span class="kw">class</span> <span class="fn">MCPTool</span>:                                   <span class="cm"># :263 —— 基类，勿直接实例化</span>
    <span class="kw">async def</span> <span class="fn">connect</span>(self, *, reset=<span class="kw">False</span>): ...      <span class="cm"># :801  建立传输（由子类提供 client）</span>
    <span class="kw">async def</span> <span class="fn">load_tools</span>(self):                    <span class="cm"># :1208 列出远端工具…</span>
        tool_list = <span class="kw">await</span> self.session.list_tools()  <span class="cm"># :1244 …包成本地 FunctionTool</span>
    <span class="kw">async def</span> <span class="fn">call_tool</span>(self, tool_name, **kwargs):  <span class="cm"># :1422 转发一次调用</span>
        <span class="kw">return await</span> self.session.call_tool(tool_name, arguments=kwargs)  <span class="cm"># :1481</span>
    <span class="nb">@property</span>
    <span class="kw">def</span> <span class="fn">functions</span>(self): ...                       <span class="cm"># :637  发现到的工具列表</span>

<span class="kw">class</span> <span class="fn">MCPStdioTool</span>(MCPTool):                       <span class="cm"># :2110 —— 子进程传输</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, name, command, *, args=<span class="kw">None</span>, env=<span class="kw">None</span>, ...):
        <span class="cm"># 用 command/args 造 StdioServerParameters → 启动子进程、走 stdio</span>
        ...</pre>
</div>
<p>这解释了「为什么换传输不用改 Agent」：模型只与 <span class="mono">.functions</span> 里的 <span class="mono">FunctionTool</span> 打交道，
而 <span class="mono">connect</span> / <span class="mono">call_tool</span> 这些动作全在基类里。子类只决定「拿什么 client 建连接」——
<span class="mono">MCPStdioTool</span> 给的是 stdio client，<span class="mono">MCPStreamableHTTPTool</span> 给的是 HTTP client，仅此而已。</p>

<h2>为什么要用 MCP 统一外部工具协议</h2>
<p>没有 MCP 时，把 <span class="mono">M</span> 个工具接到 <span class="mono">N</span> 个 LLM 应用上，是一道 <strong>N×M 的定制对接题</strong>：每个应用都要为每个工具写一遍适配。
MCP 把它降成 <strong>N+M</strong>：工具方实现一次 MCP 服务器，应用方实现一次 MCP 客户端，两边照协议即插即用。</p>
<table class="t">
  <tr><th>诉求</th><th>各写各的（无标准）</th><th>MCP（统一协议）</th></tr>
  <tr><td><strong>对接成本</strong></td><td>N×M：每个 App × 每个工具都要定制</td><td>N+M：工具实现一次服务器，App 实现一次客户端</td></tr>
  <tr><td><strong>工具发现</strong></td><td>硬编码，加工具要改 App 代码</td><td><span class="mono">list_tools()</span> 运行时拉取，远端加工具<strong>零改动</strong>可用</td></tr>
  <tr><td><strong>能力复用</strong></td><td>一个工具集只能服务一个生态</td><td>同一个 MCP 服务器，任何 MCP 客户端都能接</td></tr>
  <tr><td><strong>部署灵活</strong></td><td>传输方式与业务逻辑耦合</td><td>同一套工具可换 <span class="mono">Stdio/HTTP/WS</span> 传输，业务代码不变</td></tr>
</table>
<p>这正是 MAF 既能<strong>当客户端</strong>（用 <span class="mono">MCPStdioTool</span> 等调别人的服务器），也能<strong>当服务器</strong>（把自己的 Agent/工具暴露为 MCP）的意义所在。
和<a href="23-skills.html">上一课的技能</a>对照看：技能管「私有知识怎么声明并按需装载」，MCP 管「外部能力怎么标准化接入」——两者都是为了别把一切都焊死在 prompt 与代码里。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 三种传输方式深入 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">三种传输各有用法：
<pre class="code"><span class="cm"># 1. Stdio — 本地子进程</span>
MCPStdioTool(name=<span class="st">"fs"</span>, command=<span class="st">"npx"</span>, args=[<span class="st">"-y"</span>, <span class="st">"server-fs"</span>])

<span class="cm"># 2. HTTP/SSE — 远程 Web 服务</span>
MCPStreamableHTTPTool(name=<span class="st">"api"</span>, url=<span class="st">"https://api.example.com/mcp"</span>)

<span class="cm"># 3. WebSocket — 双向实时</span>
MCPWebsocketTool(name=<span class="st">"rt"</span>, url=<span class="st">"wss://service.example.com/mcp"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">不同部署环境需要不同传输方式：本地开发用 Stdio 最方便（无需网络），
        生产环境用 HTTP/SSE 最稳定，需要实时双向推送时用 WebSocket。
        统一基类 <span class="mono">MCPTool</span> 让上层 Agent 代码无需关心传输细节。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">三个子类都继承自 <span class="mono">MCPTool</span>（2400+ 行），自动处理连接生命周期、
        工具发现和 JSON-RPC 通信。通过 <span class="mono">MCPTaskOptions</span> 统一配置超时、
        取消策略等。Agent 使用 <span class="mono">async with</span> 自动管理连接。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>直接用 HTTP REST</strong>（简单但无标准化的工具发现协议）；
        <strong>gRPC</strong>（高性能但 LLM 生态支持少）；
        <strong>LangChain ToolNode</strong>（框架内工具，不跨框架通用）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> MCP 审批模型 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a"><span class="mono">MCPTaskOptions</span> 控制长时间任务的生命周期：
<pre class="code"><span class="kw">from</span> datetime <span class="kw">import</span> timedelta
<span class="kw">from</span> agent_framework <span class="kw">import</span> MCPStdioTool, MCPTaskOptions

tool = MCPStdioTool(
    name=<span class="st">"long-task"</span>,
    command=<span class="st">"python"</span>, args=[<span class="st">"server.py"</span>],
    task_options=MCPTaskOptions(
        default_ttl=timedelta(minutes=2),
        max_task_wait=timedelta(minutes=5),
        cancel_remote_task_on_local_cancellation=<span class="kw">True</span>,
    ),
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">有些 MCP 工具执行时间很长（数据分析、文件转换等），
        需要轮询状态、超时控制和取消机制。
        <span class="mono">MCPTaskOptions</span> 透明处理 <span class="mono">tools/call → tasks/get → tasks/result</span> 生命周期。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">遵循 SEP-2663 长时间任务规范：提交任务后自动轮询，
        支持取消时自动清理远端资源，对不支持 tasks 的旧服务器自动降级。
        还有 <span class="mono">header_provider</span> 做认证注入（如 Bearer token）。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>手动轮询 + 超时</strong>（繁琐且容易出错）；
        <strong>后台任务队列</strong>（如 Celery，太重量级）；
        <strong>Server-Sent Events</strong>（HTTP SSE 已内置在 <span class="mono">MCPStreamableHTTPTool</span> 中）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Agent 作为 MCP 服务器 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">MAF Agent 不仅能<strong>调用</strong> MCP 工具，还能<strong>作为</strong> MCP 服务器被其他客户端调用：
<pre class="code"><span class="cm"># samples/02-agents/mcp/agent_as_mcp_server.py</span>
<span class="cm"># Agent 把自身注册为 MCP 服务器</span>
<span class="cm"># 外部 MCP 客户端可以调用此 Agent 的能力</span>
<span class="cm"># 实现 Agent ↔ Agent 的 MCP 互调</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">多 Agent 系统中，一个 Agent 的能力可以被其他 Agent 通过标准 MCP 协议复用。
        比如一个"翻译 Agent"作为 MCP 服务器暴露自己的翻译能力，
        其他 Agent 通过 <span class="mono">MCPStdioTool</span> 调用它——无需知道内部实现。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">框架双向支持 MCP：<strong>消费端</strong>通过三种传输类型调用外部工具，
        <strong>服务端</strong>把 Agent 能力暴露为 MCP 工具。
        这让 MAF Agent 可以无缝融入任何 MCP 生态系统。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>A2A 协议</strong>（Agent-to-Agent，更高层的 Agent 互调协议）；
        <strong>自定义 REST API</strong>（灵活但缺乏标准化发现机制）；
        <strong>消息队列</strong>（适合异步场景但延迟较高）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> MCP vs 直接 @tool <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">对比两种方式：
<pre class="code"><span class="cm"># 直接 @tool —— 代码内定义</span>
<span class="kw">@tool</span>
<span class="kw">def</span> read_file(path: <span class="kw">str</span>) -> <span class="kw">str</span>:
    <span class="kw">return</span> open(path).read()

<span class="cm"># MCP Tool —— 外部服务提供</span>
MCPStdioTool(name=<span class="st">"fs"</span>, command=<span class="st">"npx"</span>,
    args=[<span class="st">"-y"</span>, <span class="st">"server-fs"</span>, <span class="st">"/data"</span>])</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a"><span class="mono">@tool</span> 是进程内的 Python 函数，简单快速但只限本项目使用；
        MCP Tool 走标准协议，可以跨语言、跨项目、跨框架复用。
        两者可以混合使用——<span class="mono">Agent(tools=[my_tool, mcp_tool])</span>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 统一了两种工具模型：<span class="mono">@tool</span> 和 <span class="mono">MCPTool</span> 都实现相同的工具接口，
        Agent 无需区分工具来源。MCP 工具的 schema 通过协议自动发现，
        无需手动维护 JSON Schema。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>全部用 @tool</strong>（最简单但不可跨项目复用）；
        <strong>全部用 MCP</strong>（最标准化但本地简单工具开销大）；
        <strong>OpenAPI 插件</strong>（REST 标准化但缺少 LLM 特有的工具发现）。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><strong>MCP 是 LLM 工具连接的开放标准</strong>——即插即用，跨框架通用。</li>
    <li>三种传输：<strong>Stdio</strong>（本地开发）、<strong>HTTP/SSE</strong>（生产部署）、<strong>WebSocket</strong>（实时通信）。</li>
    <li><span class="mono">MCPTaskOptions</span> 处理长时间任务的超时、轮询和取消。</li>
    <li>MAF Agent 既能<strong>调用</strong> MCP 工具，也能<strong>作为</strong> MCP 服务器暴露能力。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>@tool 和 MCPTool 在 Agent 眼里没有区别</strong>——都是"能做事的工具"。
  你可以从 @tool 起步做快速原型，之后把成熟的工具迁移为 MCP 服务，
  实现从本地开发到标准化分发的平滑过渡。
</div>
"""
L24_EN = r"""
<p class="lead"><strong>MCP (Model Context Protocol)</strong> is the <strong>open standard</strong> for connecting tools and
resources to LLMs — MAF can both <strong>call</strong> MCP servers and <strong>expose</strong> an Agent as one.</p>

<div class="card analogy">
  <div class="tag">📚 Analogy</div>
  MCP is like the <strong>USB standard</strong>: whether you plug in a keyboard, mouse or hard drive, the USB protocol
  lets it work instantly. MCP gives LLMs and tools a unified "interface protocol" — no custom code per tool.
</div>

<h2>Three transport types</h2>
<table class="t">
  <tr><th>Transport</th><th>Class</th><th>When to use</th></tr>
  <tr><td>Stdio (subprocess)</td><td class="mono">MCPStdioTool</td><td>Local CLI tools; ideal for dev/test</td></tr>
  <tr><td>HTTP/SSE (Streamable HTTP)</td><td class="mono">MCPStreamableHTTPTool</td><td>Remote Web APIs; production-grade</td></tr>
  <tr><td>WebSocket</td><td class="mono">MCPWebsocketTool</td><td>Bi-directional real-time communication</td></tr>
</table>

<h2>Connect to an MCP server</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">MCPStdioTool usage</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent, MCPStdioTool

mcp_tool = MCPStdioTool(
    name=<span class="st">"filesystem"</span>,
    command=<span class="st">"npx"</span>,
    args=[<span class="st">"-y"</span>, <span class="st">"@modelcontextprotocol/server-filesystem"</span>, <span class="st">"/data"</span>],
)

<span class="kw">async with</span> Agent(
    client=client,
    tools=mcp_tool,
    name=<span class="st">"fs-agent"</span>,
) <span class="kw">as</span> agent:
    response = <span class="kw">await</span> agent.run(<span class="st">"List all .txt files"</span>)</pre>
</div>

<h2>Trace one MCP tool call</h2>
<p>Enough abstraction — let's walk it end to end: an Agent connects to the official <strong>filesystem</strong> MCP server via <span class="mono">MCPStdioTool</span>,
and the user says <strong>"List all .txt files under /data"</strong>. The key point: an MCP tool is <strong>not</strong> a local Python function you wrote —
it's a capability in <strong>another process</strong>. The framework must first <strong>connect, ask what tools it has</strong>, then <strong>forward</strong> the model's call request over stdio to be executed there.</p>

<div class="vflow">
  <div class="step"><div class="num">0</div><div class="sc"><h4>Construct: just a description, not yet connected</h4>
    <p><span class="mono">MCPStdioTool(name="filesystem", command="npx", args=[...])</span> (<span class="mono">_mcp.py:2110</span>) is just a <strong>connection spec</strong> right now;
    no subprocess has started. Note it subclasses <span class="mono">MCPTool</span> (<span class="mono">_mcp.py:263</span>), which cannot be instantiated directly.</p></div></div>
  <div class="step"><div class="num">1</div><div class="sc"><h4>Enter the context: start the subprocess</h4>
    <p><span class="mono">async with agent:</span> triggers the tool's <span class="mono">__aenter__</span> (<span class="mono">_mcp.py:2068</span>) → <span class="mono">connect()</span> (<span class="mono">:801</span>).
    The framework builds a <span class="mono">StdioServerParameters</span> from <span class="mono">command/args</span>, <span class="mono">npx</span> launches the filesystem server subprocess, and a bidirectional stdio pipe is established.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Ask what tools it has: load_tools</h4>
    <p>Once connected it calls <span class="mono">load_tools()</span> (<span class="mono">:1208</span>) → <span class="mono">session.list_tools()</span> (<span class="mono">:1244</span>).
    The server reports <span class="mono">list_directory</span> / <span class="mono">read_file</span> / … each wrapped into a local <span class="mono">FunctionTool</span> in <span class="mono">.functions</span> (<span class="mono">:637</span>), and its JSON Schema is handed to the model.</p>
<pre class="code"><span class="cm"># remote tools translated into model-visible schemas (excerpt)</span>
[FunctionTool(name=<span class="st">"list_directory"</span>, parameters={<span class="st">"path"</span>: <span class="st">"string"</span>}),
 FunctionTool(name=<span class="st">"read_file"</span>,      parameters={<span class="st">"path"</span>: <span class="st">"string"</span>})]</pre></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Model decides: list the directory</h4>
    <p>The model sees <span class="mono">list_directory</span> and issues a tool call — with the <strong>exact same syntax</strong> as a local tool; it has no idea this is a remote process:</p>
<pre class="code">FunctionCallContent(name=<span class="st">"list_directory"</span>,
                    arguments={<span class="st">"path"</span>: <span class="st">"/data"</span>})</pre></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Forward over stdio: call_tool</h4>
    <p>The framework hands the call to <span class="mono">call_tool("list_directory", path="/data")</span> (<span class="mono">:1422</span>) →
    <span class="mono">session.call_tool(name, arguments=...)</span> (<span class="mono">:1481</span>), writing one JSON-RPC request to the subprocess over stdio.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Remote execution → result fed back</h4>
    <p>The filesystem subprocess runs <span class="mono">list_directory</span> against the <strong>real filesystem</strong> and returns a <span class="mono">CallToolResult</span>;
    the default parser converts it to a string/<span class="mono">Content</span> back into the conversation. The model filters for <span class="mono">.txt</span> and answers.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Exit the context: tear down</h4>
    <p><span class="mono">async with</span> ends → <span class="mono">__aexit__</span> (<span class="mono">_mcp.py:2089</span>) closes the stdio pipe and terminates the subprocess. The connection is <strong>borrowed and returned</strong>.</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 Reading this trace</div>
  Three key points: ① <strong>tools are "discovered", not hardcoded</strong> — <span class="mono">list_tools()</span> pulls the remote tool list at run time, so when the server adds a new tool your Agent can use it with no code change;
  ② <strong>the model is oblivious to "near vs far"</strong> — remote tools are wrapped as local <span class="mono">FunctionTool</span>s, and the model emits <span class="mono">FunctionCallContent</span> exactly as it would for a local <code>@tool</code> (see <a href="06-tools.html">Lesson 6</a>);
  ③ <strong>the connection is stateful</strong> — you must manage the subprocess lifecycle in pairs via <span class="mono">async with</span> (or explicit <span class="mono">connect()</span>/<span class="mono">__aexit__</span>), which is the biggest difference from a stateless local function.
</div>

<h2>One base class, three transports</h2>
<p>Whether you go subprocess, HTTP or WebSocket, <strong>the upper-layer Agent code is identical</strong> — the differences are boxed into three subclasses sharing one base class <span class="mono">MCPTool</span>:</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">base</span><span class="name">MCPTool</span></div>
    <div class="ld"><span class="mono">_mcp.py:263</span>. <strong>Not directly instantiable.</strong> Owns the connection lifecycle, <span class="mono">load_tools/load_prompts</span>, <span class="mono">call_tool</span>, JSON-RPC communication, approval and timeouts (<span class="mono">MCPTaskOptions</span>).</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">sub</span><span class="name">MCPStdioTool(command, args)</span></div>
    <div class="ld"><span class="mono">:2110</span>. Starts a <strong>local subprocess</strong> over stdin/stdout. No network; smoothest for local CLIs / dev debugging.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">sub</span><span class="name">MCPStreamableHTTPTool(url)</span></div>
    <div class="ld"><span class="mono">:2254</span>. Connects to a <strong>remote HTTP/SSE</strong> endpoint, with <span class="mono">headers</span> / <span class="mono">header_provider</span> for auth. The go-to for production.</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">sub</span><span class="name">MCPWebsocketTool(url)</span></div>
    <div class="ld"><span class="mono">:2456</span>. Uses <strong>WebSocket (wss://)</strong>, suited to long-lived connections with bidirectional real-time push.</div></div>
</div>

<p>Laid out horizontally, connecting is a fixed lifecycle pipeline — the three transports differ only in "how step 1 connects", everything after is the same:</p>
<div class="flow">
  <div class="node"><div class="nt">construct</div><div class="nd">command/URL · not connected</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">connect</div><div class="nd">subprocess / HTTP / WS</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">list_tools</div><div class="nd">discover remote tools</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">→ FunctionTool</div><div class="nd">wrap as local tools</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">call_tool</div><div class="nd">forward · execute · feed back</div></div>
</div>

<h2>🔍 Real source: base class vs transport subclass</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_mcp.py</span><span class="ln">MCPTool / MCPStdioTool (simplified from :263 / :2110)</span></div>
<pre class="code"><span class="kw">class</span> <span class="fn">MCPTool</span>:                                   <span class="cm"># :263 -- base; do not instantiate directly</span>
    <span class="kw">async def</span> <span class="fn">connect</span>(self, *, reset=<span class="kw">False</span>): ...      <span class="cm"># :801  open transport (client from subclass)</span>
    <span class="kw">async def</span> <span class="fn">load_tools</span>(self):                    <span class="cm"># :1208 list remote tools...</span>
        tool_list = <span class="kw">await</span> self.session.list_tools()  <span class="cm"># :1244 ...wrap as local FunctionTool</span>
    <span class="kw">async def</span> <span class="fn">call_tool</span>(self, tool_name, **kwargs):  <span class="cm"># :1422 forward one call</span>
        <span class="kw">return await</span> self.session.call_tool(tool_name, arguments=kwargs)  <span class="cm"># :1481</span>
    <span class="nb">@property</span>
    <span class="kw">def</span> <span class="fn">functions</span>(self): ...                       <span class="cm"># :637  the discovered tool list</span>

<span class="kw">class</span> <span class="fn">MCPStdioTool</span>(MCPTool):                       <span class="cm"># :2110 -- subprocess transport</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, name, command, *, args=<span class="kw">None</span>, env=<span class="kw">None</span>, ...):
        <span class="cm"># build StdioServerParameters from command/args -&gt; launch subprocess over stdio</span>
        ...</pre>
</div>
<p>This explains "why swapping transport needs no Agent change": the model only deals with the <span class="mono">FunctionTool</span>s in <span class="mono">.functions</span>,
while <span class="mono">connect</span> / <span class="mono">call_tool</span> all live in the base class. A subclass only decides "which client to build the connection with" —
<span class="mono">MCPStdioTool</span> hands over a stdio client, <span class="mono">MCPStreamableHTTPTool</span> an HTTP client, and that's all.</p>

<h2>Why unify external tools behind MCP</h2>
<p>Without MCP, wiring <span class="mono">M</span> tools into <span class="mono">N</span> LLM apps is an <strong>N×M custom-integration problem</strong>: every app re-implements an adapter for every tool.
MCP collapses it to <strong>N+M</strong>: a tool implements an MCP server once, an app implements an MCP client once, and both plug together by protocol.</p>
<table class="t">
  <tr><th>Need</th><th>Everyone rolls their own (no standard)</th><th>MCP (one protocol)</th></tr>
  <tr><td><strong>Integration cost</strong></td><td>N×M: every App × every tool is bespoke</td><td>N+M: tool implements a server once, App implements a client once</td></tr>
  <tr><td><strong>Tool discovery</strong></td><td>Hardcoded; adding a tool means editing App code</td><td><span class="mono">list_tools()</span> pulls at run time; new remote tools work with <strong>zero changes</strong></td></tr>
  <tr><td><strong>Capability reuse</strong></td><td>A toolset only serves one ecosystem</td><td>The same MCP server is reachable by any MCP client</td></tr>
  <tr><td><strong>Deploy flexibility</strong></td><td>Transport couples to business logic</td><td>The same tools can switch <span class="mono">Stdio/HTTP/WS</span> with no business-code change</td></tr>
</table>
<p>That is exactly why MAF can be both a <strong>client</strong> (calling others' servers via <span class="mono">MCPStdioTool</span> etc.) and a <strong>server</strong> (exposing its own Agent/tools as MCP).
Contrast with <a href="23-skills.html">the previous lesson on skills</a>: skills govern "how private knowledge is declared and loaded on demand", MCP governs "how external capabilities are standardized in" — both exist so you don't weld everything into the prompt and code.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Three transports deep dive <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Each transport has its own class:
<pre class="code"><span class="cm"># 1. Stdio — local subprocess</span>
MCPStdioTool(name=<span class="st">"fs"</span>, command=<span class="st">"npx"</span>, args=[<span class="st">"-y"</span>, <span class="st">"server-fs"</span>])

<span class="cm"># 2. HTTP/SSE — remote web service</span>
MCPStreamableHTTPTool(name=<span class="st">"api"</span>, url=<span class="st">"https://api.example.com/mcp"</span>)

<span class="cm"># 3. WebSocket — bi-directional real-time</span>
MCPWebsocketTool(name=<span class="st">"rt"</span>, url=<span class="st">"wss://service.example.com/mcp"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Different deployments need different transports: Stdio is easiest for local dev (no network),
        HTTP/SSE is most reliable for production, WebSocket suits bi-directional real-time pushes.
        The shared <span class="mono">MCPTool</span> base class hides transport details from Agent code.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">All three subclasses inherit from <span class="mono">MCPTool</span> (2 400+ lines) and handle connection lifecycle,
        tool discovery and JSON-RPC communication automatically.
        <span class="mono">MCPTaskOptions</span> configures timeouts and cancellation policies uniformly.
        Agents use <span class="mono">async with</span> for automatic connection management.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Plain HTTP REST</strong> (simple but no standard tool-discovery protocol);
        <strong>gRPC</strong> (high performance but limited LLM ecosystem support);
        <strong>LangChain ToolNode</strong> (framework-internal, not cross-framework).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> MCP approval model <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a"><span class="mono">MCPTaskOptions</span> controls the long-running task lifecycle:
<pre class="code"><span class="kw">from</span> datetime <span class="kw">import</span> timedelta
<span class="kw">from</span> agent_framework <span class="kw">import</span> MCPStdioTool, MCPTaskOptions

tool = MCPStdioTool(
    name=<span class="st">"long-task"</span>,
    command=<span class="st">"python"</span>, args=[<span class="st">"server.py"</span>],
    task_options=MCPTaskOptions(
        default_ttl=timedelta(minutes=2),
        max_task_wait=timedelta(minutes=5),
        cancel_remote_task_on_local_cancellation=<span class="kw">True</span>,
    ),
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Some MCP tools run for a long time (data analysis, file conversion).
        They need status polling, timeout control and a cancellation mechanism.
        <span class="mono">MCPTaskOptions</span> transparently handles the <span class="mono">tools/call → tasks/get → tasks/result</span> lifecycle.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Follows the SEP-2663 long-running task spec: submit then auto-poll,
        cancel with automatic remote cleanup, graceful fallback for legacy servers.
        Also supports <span class="mono">header_provider</span> for auth injection (e.g. Bearer tokens).</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Manual polling + timeout</strong> (tedious and error-prone);
        <strong>Background task queues</strong> (e.g. Celery — heavyweight);
        <strong>Server-Sent Events only</strong> (already built into <span class="mono">MCPStreamableHTTPTool</span>).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Agent as MCP server <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">MAF Agents can <strong>serve</strong> as MCP servers, not just consume them:
<pre class="code"><span class="cm"># samples/02-agents/mcp/agent_as_mcp_server.py</span>
<span class="cm"># Register the Agent as an MCP server</span>
<span class="cm"># External MCP clients call this Agent's capabilities</span>
<span class="cm"># Enables Agent ↔ Agent MCP interop</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">In multi-agent systems, one Agent's capabilities can be reused by others via the standard
        MCP protocol. A "translation Agent" exposes its abilities as an MCP server; other Agents
        call it through <span class="mono">MCPStdioTool</span> — no need to know the implementation.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">The framework supports MCP bi-directionally: <strong>consumer side</strong> with three transports for
        external tools; <strong>server side</strong> exposing Agent capabilities as MCP tools.
        This lets MAF Agents integrate seamlessly into any MCP ecosystem.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>A2A protocol</strong> (higher-level Agent-to-Agent, covered in L26);
        <strong>Custom REST API</strong> (flexible but no standard discovery);
        <strong>Message queues</strong> (good for async but higher latency).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> MCP vs direct @tool <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Compare both approaches:
<pre class="code"><span class="cm"># Direct @tool — defined in-process</span>
<span class="kw">@tool</span>
<span class="kw">def</span> read_file(path: <span class="kw">str</span>) -> <span class="kw">str</span>:
    <span class="kw">return</span> open(path).read()

<span class="cm"># MCP Tool — provided by external service</span>
MCPStdioTool(name=<span class="st">"fs"</span>, command=<span class="st">"npx"</span>,
    args=[<span class="st">"-y"</span>, <span class="st">"server-fs"</span>, <span class="st">"/data"</span>])</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a"><span class="mono">@tool</span> is an in-process Python function — simple and fast but project-scoped.
        MCP tools use a standard protocol — cross-language, cross-project, cross-framework.
        Both can be mixed: <span class="mono">Agent(tools=[my_tool, mcp_tool])</span>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF unifies both models: <span class="mono">@tool</span> and <span class="mono">MCPTool</span> implement the same tool interface
        so the Agent doesn't care about tool origin. MCP tools auto-discover their schema
        via the protocol — no manual JSON Schema needed.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>All @tool</strong> (simplest but no cross-project reuse);
        <strong>All MCP</strong> (most standard but overhead for trivial local tools);
        <strong>OpenAPI plugins</strong> (REST-standardised but lack LLM-specific tool discovery).</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>MCP is the open standard for LLM tool connectivity</strong> — plug-and-play, cross-framework.</li>
    <li>Three transports: <strong>Stdio</strong> (local dev), <strong>HTTP/SSE</strong> (production), <strong>WebSocket</strong> (real-time).</li>
    <li><span class="mono">MCPTaskOptions</span> handles long-running task timeouts, polling and cancellation.</li>
    <li>MAF Agents can both <strong>call</strong> MCP tools and <strong>serve as</strong> MCP servers.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>@tool and MCPTool look identical to the Agent</strong> — both are just "tools that do things."
  Start with @tool for rapid prototyping, then graduate mature tools to MCP services for
  a smooth transition from local development to standardised distribution.
</div>
"""
L25_ZH = r"""
<p class="lead"><strong>Foundry 托管 Agent</strong>——只需 ~2 行额外代码，就能把本地 Agent 部署到 Azure AI Foundry 云端，
获得自动伸缩、会话管理和企业级监控。</p>

<div class="card analogy">
  <div class="tag">📚 生活类比</div>
  本地跑 Agent 像在<strong>自家厨房做饭</strong>（灵活但只能服务自己）；
  Foundry 托管就像把菜谱交给<strong>云厨房</strong>——它帮你准备食材、管理订单、扩容厨师，你只管出菜谱。
</div>

<h2>两种托管模式</h2>
<table class="t">
  <tr><th>模式</th><th>类名</th><th>特点</th><th>适用场景</th></tr>
  <tr><td>Responses API</td><td class="mono">ResponsesHostServer</td><td>完整的 Azure AI Foundry Responses 协议，支持流式、审批工作流</td><td>需要与 Foundry 生态深度集成</td></tr>
  <tr><td>Invocations</td><td class="mono">InvocationsHostServer</td><td>轻量级 JSON 请求/响应，支持流式</td><td>快速部署，简单场景</td></tr>
</table>

<h2>最小托管模式</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">Invocations 模式</span></div>
<pre><span class="kw">from</span> agent_framework_foundry_hosting <span class="kw">import</span> InvocationsHostServer

server = InvocationsHostServer(agent=my_agent)
server.run()
<span class="cm"># 就这么简单——Agent 已在云端运行！</span></pre>
</div>

<h2>追踪一次托管部署</h2>
<p>抽象讲完，我们端到端走一遍：把一个<strong>带「退款」工具（需人工审批）的 Agent</strong> 用 <span class="mono">ResponsesHostServer</span> 托管上线。
重点在于：所谓「2 行部署」，其实是托管层替你接管了一堆<strong>运维脏活</strong>——会话隔离、历史、检查点、<strong>审批存储</strong>、伸缩、监控。
本地直接 <span class="mono">agent.run()</span> 只服务你自己；套上 host server，它就变成一个云端可调用的服务。</p>

<div class="vflow">
  <div class="step"><div class="num">0</div><div class="sc"><h4>起点：一个本地 Agent</h4>
    <p>你已有一个 <span class="mono">agent</span>（带一个 <span class="mono">refund</span> 工具，且该工具要求审批）。本地它只能在你的进程里跑。</p></div></div>
  <div class="step"><div class="num">1</div><div class="sc"><h4>包装：host server 接管运维</h4>
    <p><span class="mono">server = ResponsesHostServer(agent)</span>（<span class="mono">_responses.py:341</span>）。构造时它<strong>校验</strong>：不允许带 <span class="mono">load_messages=True</span> 的历史提供者，
    因为<strong>历史由托管层接管</strong>（<span class="mono">:367</span>）；并据环境选好审批存储——云上用文件、本地用内存（<span class="mono">:404</span>）。</p>
<pre class="code"><span class="cm"># 托管层据“是否在云端”自动选审批存储后端</span>
self._approval_storage = (
    FileBasedFunctionApprovalStorage(...)   <span class="cm"># self.config.is_hosted</span>
    <span class="kw">if</span> self.config.is_hosted
    <span class="kw">else</span> InMemoryFunctionApprovalStorage())</pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>暴露 endpoint：server.run()</h4>
    <p><span class="mono">server.run()</span> 起 HTTP 服务，按 Foundry Responses 协议暴露。注意 Agent 的进入是<strong>惰性</strong>的——
    首个请求才 <span class="mono">_ensure_agent_ready</span>（<span class="mono">:418</span>），这样 MCP 鉴权失败能作为流事件回给客户端，而不是把整个服务搞崩。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>远端调用进来</h4>
    <p>云端调用方发来一个 Responses 请求（含 user message）。host server 路由到 <span class="mono">_handle_response</span>，
    按 <span class="mono">session_id</span> 隔离会话状态——并发的多个用户互不串味。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>工具触发审批：写入 ApprovalStorage</h4>
    <p>模型决定调 <span class="mono">refund</span>，但它需审批。host server 生成一条审批请求，调
    <span class="mono">ApprovalStorage.save_approval_request(id, request)</span>（<span class="mono">:127</span>）<strong>持久化</strong>，并把「待审批」作为响应事件返回，<strong>挂起</strong>这一步。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>人审通过 → 放行</h4>
    <p>审批方带着 approval id 再次请求；host server 用 <span class="mono">load_approval_request(id)</span>（<span class="mono">:131</span>）取回原请求，确认后放行工具执行。
    即便进程在两次请求之间被<strong>回收</strong>，审批状态也已落盘、不丢。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>产出：流式返回最终答案</h4>
    <p>工具执行 → 模型续写 → Responses 流把最终答案返回。整个过程的<strong>历史与检查点</strong>都由托管层存储，
    你的业务代码一行都没写这些。</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 读懂这条轨迹</div>
  「2 行」背后，托管层默默接管了四类脏活：①<strong>会话隔离</strong>——按 <span class="mono">session_id</span> 分桶，多用户并发不串台；
  ②<strong>历史/检查点托管</strong>——所以它<em>拒绝</em>你自带 <span class="mono">load_messages=True</span> 的历史提供者，避免两套历史打架；
  ③<strong>审批持久化</strong>——危险工具的批准请求落到 <span class="mono">ApprovalStorage</span>，进程被回收也能续上（人在环，见<a href="19-durability-hitl.html">第 19 课</a>）；
  ④<strong>惰性生命周期</strong>——首个请求才真正进入 Agent，把鉴权失败变成可返回的事件而非启动崩溃。
</div>

<h2>托管栈：谁负责什么</h2>
<p>把这次部署竖着切一刀，从你的代码到云端运行时，每一层各管一段——<strong>你只写最上面那层</strong>：</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">你写</span><span class="name">your Agent</span></div>
    <div class="ld">业务逻辑：instructions、工具、技能。本地能 <span class="mono">agent.run()</span> 跑通即可。</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">包装</span><span class="name">InvocationsHostServer / ResponsesHostServer</span></div>
    <div class="ld"><span class="mono">_invocations.py:10</span> / <span class="mono">_responses.py:341</span>。会话隔离、流式、历史、检查点、审批存储——一句构造全接管。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">基类</span><span class="name">azure.ai.agentserver.*</span></div>
    <div class="ld"><span class="mono">InvocationAgentServerHost</span> / <span class="mono">ResponsesAgentServerHost</span>。HTTP 路由、协议编解码、<span class="mono">server.run()</span> 都在这。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">云端</span><span class="name">Azure AI Foundry 运行时</span></div>
    <div class="ld">自动伸缩、监控、凭据、可能在请求间回收实例——所以上面才要求「无内存态、状态外置」。</div></div>
</div>

<p>横过来看，部署就是把「本地定义」接到「云端调用方」之间补一个 host server，审批则横挂在旁边的存储上：</p>
<div class="flow">
  <div class="node"><div class="nt">本地 Agent</div><div class="nd">agent.run() 可跑</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">HostServer</div><div class="nd">包装 · server.run()</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">endpoint</div><div class="nd">Foundry 协议</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">云端调用方</div><div class="nd">按 session_id 隔离</div></div>
  <div class="arrow">↔</div>
  <div class="node"><div class="nt">ApprovalStorage</div><div class="nd">审批落盘</div></div>
</div>

<h2>🔍 真实源码：两种 host server 与审批存储</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">foundry_hosting/</span><span class="ln">两种 host server + ApprovalStorage（简化自 _invocations.py:10 / _responses.py:341 / :124）</span></div>
<pre class="code"><span class="kw">class</span> <span class="fn">InvocationsHostServer</span>(InvocationAgentServerHost):   <span class="cm"># _invocations.py:10</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, agent, *, openapi_spec=<span class="kw">None</span>, **kwargs):
        <span class="cm"># 请求体 {"message": ...} → {"response": ..., "session_id": ...}</span>
        <span class="kw">if not</span> isinstance(agent, SupportsAgentRun): <span class="kw">raise</span> TypeError(...)
        self._sessions: dict[str, AgentSession] = {}     <span class="cm"># 按 session_id 隔离</span>

<span class="kw">class</span> <span class="fn">ResponsesHostServer</span>(ResponsesAgentServerHost):     <span class="cm"># _responses.py:341</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, agent, *, prefix=<span class="st">""</span>, options=<span class="kw">None</span>, store=<span class="kw">None</span>):
        <span class="cm"># 历史/检查点由托管层接管 → 拒绝自带 load_messages=True 的历史</span>
        self._approval_storage = (FileBasedFunctionApprovalStorage(...)
            <span class="kw">if</span> self.config.is_hosted <span class="kw">else</span> InMemoryFunctionApprovalStorage())

<span class="kw">class</span> <span class="fn">ApprovalStorage</span>(Protocol):                       <span class="cm"># _responses.py:124</span>
    <span class="kw">async def</span> <span class="fn">save_approval_request</span>(self, id, request): ...  <span class="cm"># :127</span>
    <span class="kw">async def</span> <span class="fn">load_approval_request</span>(self, id): ...           <span class="cm"># :131</span></pre>
</div>
<p>注意两件事：<span class="mono">InvocationsHostServer</span> 极简——一个 <span class="mono">{"message"}</span> 进、<span class="mono">{"response","session_id"}</span> 出；
<span class="mono">ResponsesHostServer</span> 则提供完整的 Foundry Responses 协议（流式、审批、检查点）。
<span class="mono">ApprovalStorage</span> 是个 <strong>Protocol</strong>——你可以替换成自己的实现（数据库、密钥库……），只要满足 save/load 两个方法。</p>

<h2>为什么值得「2 行部署」</h2>
<p>把 Agent 上生产，真正烦的从来不是「跑起来」，而是<strong>跑起来之后</strong>那一长串运维问题。托管层的价值，就是把这串问题打包接走：</p>
<table class="t">
  <tr><th>上生产要解决的</th><th>自建 FastAPI</th><th>Foundry 托管</th></tr>
  <tr><td><strong>会话隔离</strong></td><td>自己按 session_id 存取、清理</td><td>内建 <span class="mono">AgentSession</span> 分桶</td></tr>
  <tr><td><strong>历史/检查点</strong></td><td>自己接存储、自己做恢复</td><td>托管层接管，进程回收也不丢</td></tr>
  <tr><td><strong>人在环审批</strong></td><td>自己设计审批落盘与续跑</td><td><span class="mono">ApprovalStorage</span> 协议 + 文件/内存实现</td></tr>
  <tr><td><strong>伸缩 / 监控</strong></td><td>自己上 K8s、配指标</td><td>云端运行时自动伸缩、监控</td></tr>
  <tr><td><strong>协议兼容</strong></td><td>自己实现 Responses/Invocations API</td><td>换个类名即得标准 endpoint</td></tr>
</table>
<p>代价与约束也很清楚：因为实例可能在请求间被<strong>回收</strong>，你的 Agent 必须<strong>无内存态、状态外置</strong>（别把上下文塞进内存里的 context provider）。
这正是托管层「拒绝」某些配置的原因——它在帮你守住「可水平伸缩」的底线。简单场景用 <span class="mono">InvocationsHostServer</span> 够快；
要深度对接 Foundry（流式、审批、检查点）就上 <span class="mono">ResponsesHostServer</span>。下一课的 <a href="26-a2a-agui.html">A2A / AG-UI</a> 则换个方向：不是把 Agent 托管上云，而是让 Agent 之间、Agent 与前端 UI 之间标准化对话。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Responses vs Invocations <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">两种模式的初始化：
<pre class="code"><span class="cm"># Responses 模式 — 完整 Foundry API 集成</span>
<span class="kw">from</span> agent_framework_foundry_hosting <span class="kw">import</span> ResponsesHostServer
server = ResponsesHostServer(agent=my_agent)

<span class="cm"># Invocations 模式 — 轻量级 JSON</span>
<span class="kw">from</span> agent_framework_foundry_hosting <span class="kw">import</span> InvocationsHostServer
server = InvocationsHostServer(agent=my_agent)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">不同场景对 API 复杂度要求不同：<strong>Responses 模式</strong>提供完整的 Foundry Responses API
        （包括类型转换、审批存储、流式事件），适合企业级集成；
        <strong>Invocations 模式</strong>更简洁，适合快速原型和简单部署。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">两种模式都自动管理 <span class="mono">AgentSession</span>（按 session_id 隔离会话状态），
        支持流式响应（<span class="mono">StreamingResponse</span>），
        且都用 <span class="mono">async</span> 实现高并发。切换模式只需换一个类名。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>自建 FastAPI 服务</strong>（灵活但要自己处理会话管理、伸缩）；
        <strong>LangServe</strong>（LangChain 的部署方案，不兼容 Foundry 生态）；
        <strong>容器化 + K8s</strong>（完全自主但运维成本高）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 部署步骤 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">典型的部署流程：
<pre class="code"><span class="cm"># 1. 安装包</span>
pip install agent-framework-foundry-hosting

<span class="cm"># 2. 写 server.py</span>
<span class="kw">from</span> agent_framework_foundry_hosting <span class="kw">import</span> InvocationsHostServer
server = InvocationsHostServer(agent=my_agent)
server.run()

<span class="cm"># 3. 部署到 Azure AI Foundry</span>
<span class="cm"># 通过 Foundry portal 或 CLI 部署</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">从本地原型到生产部署的"最后一公里"往往最痛苦：
        要处理容器化、服务发现、负载均衡、认证等。Foundry 托管把这些都抽象掉了。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">只需 <span class="mono">pip install</span> + 2-3 行代码，Agent 就变成可部署的 Web 服务。
        <span class="mono">ResponsesHostServer</span> 还自动处理 Responses API 的类型转换（Message → Item）和
        <span class="mono">ApprovalStorage</span>（函数调用审批）。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>Azure Container Apps</strong>（更底层控制但更多配置）；
        <strong>AWS Lambda + API Gateway</strong>（无服务器但冷启动慢）；
        <strong>自建 Docker + Nginx</strong>（完全自主但运维成本高）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 托管基础设施优势 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">Foundry 托管自动提供的能力：
<pre class="code"><span class="cm"># 你只写 Agent 逻辑：</span>
agent = Agent(client=client, tools=[...], name=<span class="st">"my-agent"</span>)
server = InvocationsHostServer(agent=agent)

<span class="cm"># Foundry 自动提供：</span>
<span class="cm"># ✓ 自动伸缩（根据请求量）</span>
<span class="cm"># ✓ 会话管理（多用户隔离）</span>
<span class="cm"># ✓ 监控和日志</span>
<span class="cm"># ✓ 认证和授权</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">生产环境的 Agent 需要处理并发、故障恢复、安全审计等问题。
        手动搭建这些基础设施需要数周时间，Foundry 托管让你专注于 Agent 逻辑。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">框架把"Agent 开发"和"部署运维"完全解耦：
        本地用 <span class="mono">Agent.run()</span> 调试，生产用 <span class="mono">HostServer.run()</span> 部署，
        Agent 代码零修改。这是"write once, deploy anywhere"的理念。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>自建微服务架构</strong>（灵活但成本高）；
        <strong>Vercel AI SDK</strong>（适合前端 AI 应用但不是完整 Agent 托管）；
        <strong>Modal / Beam</strong>（Python 函数云部署，但缺乏 Agent 专属功能）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 什么时候不用托管 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">不适合 Foundry 托管的场景：
<pre class="code"><span class="cm"># ✗ 纯本地/离线环境</span>
<span class="cm"># ✗ 需要自定义底层网络配置</span>
<span class="cm"># ✗ 已有完善的 K8s 部署体系</span>
<span class="cm"># ✗ 数据合规要求不允许云端托管</span>

<span class="cm"># 这些场景下，直接用 Agent.run() 集成到</span>
<span class="cm"># 你自己的 FastAPI/Flask 服务中</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">托管并非万能——如果你已经有成熟的基础设施，或者有严格的数据驻留要求，
        直接把 Agent 集成到自有服务可能更合适。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 不强制托管——<span class="mono">Agent</span> 类本身完全独立，
        <span class="mono">HostServer</span> 只是一个可选的薄包装层。
        你可以把 Agent 嵌入任何 Python Web 框架（FastAPI、Flask、Django）。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>FastAPI + Agent.run()</strong>（自建最灵活）；
        <strong>A2A 协议</strong>（跨系统 Agent 互调）；
        <strong>MCP 服务器模式</strong>（把 Agent 暴露为 MCP 工具供其他系统调用）。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>两种模式：<strong>ResponsesHostServer</strong>（完整 Foundry API）和 <strong>InvocationsHostServer</strong>（轻量 JSON）。</li>
    <li>~2 行代码把本地 Agent 变成云端服务——会话管理、伸缩、监控自动搞定。</li>
    <li>Agent 代码<strong>零修改</strong>：本地 <span class="mono">.run()</span>、云端 <span class="mono">HostServer.run()</span>。</li>
    <li>不强制托管——Agent 可嵌入任何 Python Web 框架。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>"开发即部署"</strong>——Agent 逻辑完全不依赖托管层。
  HostServer 是一个<strong>可选的薄适配器</strong>，把你的 Agent 翻译成 Foundry 能理解的协议。
  这意味着同一个 Agent 既能本地调试，又能一键上云。
</div>
"""
L25_EN = r"""
<p class="lead"><strong>Foundry Hosted Agents</strong> — with ~2 extra lines of code, deploy your local Agent to Azure AI
Foundry cloud and get auto-scaling, session management and enterprise monitoring for free.</p>

<div class="card analogy">
  <div class="tag">📚 Analogy</div>
  Running an Agent locally is like <strong>cooking at home</strong> (flexible but serves only you).
  Foundry hosting is handing your recipe to a <strong>cloud kitchen</strong> — it procures ingredients,
  manages orders, scales up chefs. You just supply the recipe.
</div>

<h2>Two hosting modes</h2>
<table class="t">
  <tr><th>Mode</th><th>Class</th><th>Features</th><th>Use case</th></tr>
  <tr><td>Responses API</td><td class="mono">ResponsesHostServer</td><td>Full Azure AI Foundry Responses protocol; streaming, approval workflows</td><td>Deep Foundry ecosystem integration</td></tr>
  <tr><td>Invocations</td><td class="mono">InvocationsHostServer</td><td>Lightweight JSON request/response; streaming</td><td>Quick deployment, simple scenarios</td></tr>
</table>

<h2>Minimal hosting pattern</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">Invocations mode</span></div>
<pre><span class="kw">from</span> agent_framework_foundry_hosting <span class="kw">import</span> InvocationsHostServer

server = InvocationsHostServer(agent=my_agent)
server.run()
<span class="cm"># That's it — Agent is live in the cloud!</span></pre>
</div>

<h2>Trace one hosted deployment</h2>
<p>Enough abstraction — let's walk it end to end: take an <strong>Agent with a "refund" tool (approval-required)</strong> and put it online with <span class="mono">ResponsesHostServer</span>.
The point: that "2-line deploy" really means the hosting layer quietly takes over a pile of <strong>operational chores</strong> — session isolation, history, checkpoints, <strong>approval storage</strong>, scaling, monitoring.
Locally, <span class="mono">agent.run()</span> only serves you; wrap it in a host server and it becomes a cloud-callable service.</p>

<div class="vflow">
  <div class="step"><div class="num">0</div><div class="sc"><h4>Start: one local Agent</h4>
    <p>You already have an <span class="mono">agent</span> (with a <span class="mono">refund</span> tool that requires approval). Locally it only runs in your process.</p></div></div>
  <div class="step"><div class="num">1</div><div class="sc"><h4>Wrap: the host server takes over ops</h4>
    <p><span class="mono">server = ResponsesHostServer(agent)</span> (<span class="mono">_responses.py:341</span>). On construction it <strong>validates</strong>: no history provider with <span class="mono">load_messages=True</span>,
    because <strong>history is owned by the hosting layer</strong> (<span class="mono">:367</span>); and it picks an approval store by environment — file in the cloud, in-memory locally (<span class="mono">:404</span>).</p>
<pre class="code"><span class="cm"># the hosting layer picks the approval backend by “am I hosted?”</span>
self._approval_storage = (
    FileBasedFunctionApprovalStorage(...)   <span class="cm"># self.config.is_hosted</span>
    <span class="kw">if</span> self.config.is_hosted
    <span class="kw">else</span> InMemoryFunctionApprovalStorage())</pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Expose the endpoint: server.run()</h4>
    <p><span class="mono">server.run()</span> starts the HTTP service over the Foundry Responses protocol. Note the Agent is entered <strong>lazily</strong> —
    only the first request triggers <span class="mono">_ensure_agent_ready</span> (<span class="mono">:418</span>), so an MCP auth failure surfaces as a stream event to the client instead of crashing the whole server.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>A remote call arrives</h4>
    <p>A cloud caller sends a Responses request (with a user message). The host server routes it to <span class="mono">_handle_response</span>,
    isolating session state by <span class="mono">session_id</span> — concurrent users never cross-contaminate.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>A tool triggers approval: write to ApprovalStorage</h4>
    <p>The model decides to call <span class="mono">refund</span>, but it needs approval. The host server creates an approval request and calls
    <span class="mono">ApprovalStorage.save_approval_request(id, request)</span> (<span class="mono">:127</span>) to <strong>persist</strong> it, returns "pending approval" as a response event, and <strong>suspends</strong> this step.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Human approves → release</h4>
    <p>The approver re-requests with the approval id; the host server uses <span class="mono">load_approval_request(id)</span> (<span class="mono">:131</span>) to fetch the original request, confirms, and lets the tool run.
    Even if the process is <strong>recycled</strong> between the two requests, the approval state is on disk and survives.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Produce: stream the final answer</h4>
    <p>The tool runs → the model continues → the Responses stream returns the final answer. The whole run's <strong>history and checkpoints</strong> are stored by the hosting layer —
    your business code wrote none of it.</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 Reading this trace</div>
  Behind "2 lines", the hosting layer silently takes over four kinds of chores: ① <strong>session isolation</strong> — bucketed by <span class="mono">session_id</span> so concurrent users don't mix;
  ② <strong>history/checkpoint hosting</strong> — which is why it <em>rejects</em> your own <span class="mono">load_messages=True</span> history provider, avoiding two competing histories;
  ③ <strong>approval persistence</strong> — dangerous-tool approval requests land in <span class="mono">ApprovalStorage</span> and survive a recycled process (human-in-the-loop, see <a href="19-durability-hitl.html">Lesson 19</a>);
  ④ <strong>lazy lifecycle</strong> — the Agent is entered only on the first request, turning auth failures into returnable events instead of startup crashes.
</div>

<h2>The hosting stack: who owns what</h2>
<p>Slice this deployment vertically, from your code down to the cloud runtime, and each layer owns a slice — <strong>you only write the top one</strong>:</p>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">you</span><span class="name">your Agent</span></div>
    <div class="ld">Business logic: instructions, tools, skills. It just needs to run locally with <span class="mono">agent.run()</span>.</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">wrap</span><span class="name">InvocationsHostServer / ResponsesHostServer</span></div>
    <div class="ld"><span class="mono">_invocations.py:10</span> / <span class="mono">_responses.py:341</span>. Session isolation, streaming, history, checkpoints, approval storage — all taken over by one constructor.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">base</span><span class="name">azure.ai.agentserver.*</span></div>
    <div class="ld"><span class="mono">InvocationAgentServerHost</span> / <span class="mono">ResponsesAgentServerHost</span>. HTTP routing, protocol codec, and <span class="mono">server.run()</span> live here.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">cloud</span><span class="name">Azure AI Foundry runtime</span></div>
    <div class="ld">Auto-scaling, monitoring, credentials, and possibly recycling instances between requests — which is exactly why the layer above demands "no in-memory state, externalize it".</div></div>
</div>

<p>Horizontally, deploying just inserts a host server between "local definition" and "cloud caller", with approval hanging off to the side in storage:</p>
<div class="flow">
  <div class="node"><div class="nt">local Agent</div><div class="nd">agent.run() works</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">HostServer</div><div class="nd">wrap · server.run()</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">endpoint</div><div class="nd">Foundry protocol</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">cloud caller</div><div class="nd">isolated by session_id</div></div>
  <div class="arrow">↔</div>
  <div class="node"><div class="nt">ApprovalStorage</div><div class="nd">approvals persisted</div></div>
</div>

<h2>🔍 Real source: the two host servers and approval storage</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">foundry_hosting/</span><span class="ln">two host servers + ApprovalStorage (simplified from _invocations.py:10 / _responses.py:341 / :124)</span></div>
<pre class="code"><span class="kw">class</span> <span class="fn">InvocationsHostServer</span>(InvocationAgentServerHost):   <span class="cm"># _invocations.py:10</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, agent, *, openapi_spec=<span class="kw">None</span>, **kwargs):
        <span class="cm"># body {"message": ...} -&gt; {"response": ..., "session_id": ...}</span>
        <span class="kw">if not</span> isinstance(agent, SupportsAgentRun): <span class="kw">raise</span> TypeError(...)
        self._sessions: dict[str, AgentSession] = {}     <span class="cm"># isolated by session_id</span>

<span class="kw">class</span> <span class="fn">ResponsesHostServer</span>(ResponsesAgentServerHost):     <span class="cm"># _responses.py:341</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, agent, *, prefix=<span class="st">""</span>, options=<span class="kw">None</span>, store=<span class="kw">None</span>):
        <span class="cm"># history/checkpoints owned by host -&gt; rejects load_messages=True history</span>
        self._approval_storage = (FileBasedFunctionApprovalStorage(...)
            <span class="kw">if</span> self.config.is_hosted <span class="kw">else</span> InMemoryFunctionApprovalStorage())

<span class="kw">class</span> <span class="fn">ApprovalStorage</span>(Protocol):                       <span class="cm"># _responses.py:124</span>
    <span class="kw">async def</span> <span class="fn">save_approval_request</span>(self, id, request): ...  <span class="cm"># :127</span>
    <span class="kw">async def</span> <span class="fn">load_approval_request</span>(self, id): ...           <span class="cm"># :131</span></pre>
</div>
<p>Note two things: <span class="mono">InvocationsHostServer</span> is minimal — one <span class="mono">{"message"}</span> in, <span class="mono">{"response","session_id"}</span> out;
<span class="mono">ResponsesHostServer</span> offers the full Foundry Responses protocol (streaming, approval, checkpoints).
<span class="mono">ApprovalStorage</span> is a <strong>Protocol</strong> — swap in your own implementation (a database, a secrets store…) as long as it satisfies the two save/load methods.</p>

<h2>Why "2-line deploy" is worth it</h2>
<p>Putting an Agent into production, the real pain is never "make it run" — it's the long tail of ops <strong>after</strong> it runs. The hosting layer's value is packaging that tail and carrying it away:</p>
<table class="t">
  <tr><th>What production needs</th><th>Roll-your-own FastAPI</th><th>Foundry hosting</th></tr>
  <tr><td><strong>Session isolation</strong></td><td>Store/clean by session_id yourself</td><td>Built-in <span class="mono">AgentSession</span> bucketing</td></tr>
  <tr><td><strong>History/checkpoints</strong></td><td>Wire storage and recovery yourself</td><td>Owned by the host; survives recycling</td></tr>
  <tr><td><strong>Human-in-the-loop approval</strong></td><td>Design persistence and resume yourself</td><td><span class="mono">ApprovalStorage</span> protocol + file/in-memory impls</td></tr>
  <tr><td><strong>Scaling / monitoring</strong></td><td>Stand up K8s, wire metrics yourself</td><td>Cloud runtime auto-scales and monitors</td></tr>
  <tr><td><strong>Protocol compatibility</strong></td><td>Implement Responses/Invocations API yourself</td><td>Swap a class name to get a standard endpoint</td></tr>
</table>
<p>The cost and constraint are explicit too: because instances may be <strong>recycled</strong> between requests, your Agent must be <strong>stateless with externalized state</strong> (don't stuff context into an in-memory context provider).
That's exactly why the hosting layer "rejects" certain configs — it's guarding the "horizontally scalable" invariant for you. Simple cases go fast with <span class="mono">InvocationsHostServer</span>;
deep Foundry integration (streaming, approval, checkpoints) calls for <span class="mono">ResponsesHostServer</span>. The next lesson's <a href="26-a2a-agui.html">A2A / AG-UI</a> flips direction: not hosting an Agent in the cloud, but standardizing how Agents talk to <em>each other</em> and to <em>front-end UIs</em>.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Responses vs Invocations <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Initialising each mode:
<pre class="code"><span class="cm"># Responses mode — full Foundry API</span>
<span class="kw">from</span> agent_framework_foundry_hosting <span class="kw">import</span> ResponsesHostServer
server = ResponsesHostServer(agent=my_agent)

<span class="cm"># Invocations mode — lightweight JSON</span>
<span class="kw">from</span> agent_framework_foundry_hosting <span class="kw">import</span> InvocationsHostServer
server = InvocationsHostServer(agent=my_agent)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Different scenarios demand different API complexity.
        <strong>Responses mode</strong> provides the full Foundry Responses API with type conversion,
        approval storage and streaming events — ideal for enterprise integration.
        <strong>Invocations mode</strong> is leaner for quick prototyping and simple deployment.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Both modes auto-manage <span class="mono">AgentSession</span> (isolated by session_id),
        support streaming (<span class="mono">StreamingResponse</span>), and use <span class="mono">async</span>
        for high concurrency. Switching modes requires changing only one class name.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Self-built FastAPI service</strong> (flexible but you handle session management and scaling);
        <strong>LangServe</strong> (LangChain's deploy tool — not Foundry-compatible);
        <strong>Containerised + K8s</strong> (full control but high ops cost).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Deployment steps <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">A typical deployment flow:
<pre class="code"><span class="cm"># 1. Install the package</span>
pip install agent-framework-foundry-hosting

<span class="cm"># 2. Write server.py</span>
<span class="kw">from</span> agent_framework_foundry_hosting <span class="kw">import</span> InvocationsHostServer
server = InvocationsHostServer(agent=my_agent)
server.run()

<span class="cm"># 3. Deploy to Azure AI Foundry</span>
<span class="cm"># Via the Foundry portal or CLI</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">The "last mile" from local prototype to production is often the most painful:
        containerisation, service discovery, load balancing, auth.
        Foundry hosting abstracts it all away.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Just <span class="mono">pip install</span> + 2-3 lines and your Agent becomes a deployable web service.
        <span class="mono">ResponsesHostServer</span> also auto-handles Responses API type conversion
        (Message → Item) and <span class="mono">ApprovalStorage</span> (function-call approval).</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Azure Container Apps</strong> (lower-level control, more config);
        <strong>AWS Lambda + API Gateway</strong> (serverless but cold-start latency);
        <strong>Self-hosted Docker + Nginx</strong> (full control, high ops cost).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Managed infrastructure benefits <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">What Foundry hosting gives you automatically:
<pre class="code"><span class="cm"># You write Agent logic only:</span>
agent = Agent(client=client, tools=[...], name=<span class="st">"my-agent"</span>)
server = InvocationsHostServer(agent=agent)

<span class="cm"># Foundry provides automatically:</span>
<span class="cm"># ✓ Auto-scaling (based on request volume)</span>
<span class="cm"># ✓ Session management (multi-user isolation)</span>
<span class="cm"># ✓ Monitoring and logging</span>
<span class="cm"># ✓ Authentication and authorisation</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Production Agents need to handle concurrency, failure recovery and security auditing.
        Building that infrastructure manually takes weeks; Foundry hosting lets you focus on Agent logic.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">The framework fully decouples "Agent development" from "deployment ops":
        debug locally with <span class="mono">Agent.run()</span>, deploy with <span class="mono">HostServer.run()</span>,
        zero changes to Agent code. A true "write once, deploy anywhere" philosophy.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Self-built microservices</strong> (flexible but costly);
        <strong>Vercel AI SDK</strong> (frontend AI apps, not full Agent hosting);
        <strong>Modal / Beam</strong> (Python function cloud deploy, lacks Agent-specific features).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> When NOT to use hosted <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Scenarios where Foundry hosting isn't the best fit:
<pre class="code"><span class="cm"># ✗ Pure local / offline environments</span>
<span class="cm"># ✗ Custom low-level network configuration needed</span>
<span class="cm"># ✗ Existing mature K8s deployment pipeline</span>
<span class="cm"># ✗ Data-residency compliance forbids cloud hosting</span>

<span class="cm"># In these cases, embed Agent.run() directly</span>
<span class="cm"># into your own FastAPI/Flask service</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Hosting isn't one-size-fits-all. If you already have mature infrastructure or strict
        data-residency requirements, integrating the Agent into your own service may be better.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF doesn't force hosting — the <span class="mono">Agent</span> class is completely standalone.
        <span class="mono">HostServer</span> is just an optional thin wrapper. You can embed an Agent
        into any Python web framework (FastAPI, Flask, Django).</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>FastAPI + Agent.run()</strong> (most flexible self-hosted option);
        <strong>A2A protocol</strong> (cross-system Agent interop);
        <strong>MCP server mode</strong> (expose Agent as an MCP tool for other systems).</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Two modes: <strong>ResponsesHostServer</strong> (full Foundry API) and <strong>InvocationsHostServer</strong> (lightweight JSON).</li>
    <li>~2 lines turn a local Agent into a cloud service — sessions, scaling, monitoring included.</li>
    <li>Agent code is <strong>unchanged</strong>: local <span class="mono">.run()</span>, cloud <span class="mono">HostServer.run()</span>.</li>
    <li>Hosting is optional — Agents embed into any Python web framework.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>"Dev is deploy"</strong> — Agent logic has zero dependency on the hosting layer.
  HostServer is an <strong>optional thin adapter</strong> translating your Agent into the protocol Foundry understands.
  The same Agent works locally for debugging and goes live with one line.
</div>
"""
L26_ZH = r"""
<p class="lead"><strong>A2A（Agent-to-Agent）</strong>让 Agent 作为服务暴露给其他 Agent 调用；
<strong>AG-UI</strong>让 Agent 与前端 UI 实时结构化通信——两个协议合力打通"Agent ↔ Agent"和"Agent ↔ 用户界面"。</p>

<div class="card analogy">
  <div class="tag">📚 生活类比</div>
  A2A 像<strong>企业间的 B2B 接口</strong>——公司 A 的 Agent 可以调用公司 B 的 Agent 服务；
  AG-UI 像<strong>客服前台的显示屏</strong>——后台 Agent 的进度、中间结果实时推送到用户看到的界面上。
</div>

<h2>A2A vs AG-UI</h2>
<table class="t">
  <tr><th>协议</th><th>方向</th><th>用途</th><th>包名</th></tr>
  <tr><td>A2A</td><td>Agent → Agent</td><td>把 Agent 暴露为可被其他 Agent 调用的服务</td><td class="mono">agent-framework-a2a</td></tr>
  <tr><td>AG-UI</td><td>Agent → UI</td><td>Agent 执行过程中向 UI 推送实时更新</td><td class="mono">agent-framework-ag-ui</td></tr>
</table>

<h2>A2A 服务端示例</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">A2A 服务器</span></div>
<pre><span class="kw">from</span> agent_framework.a2a <span class="kw">import</span> A2AExecutor
<span class="kw">from</span> a2a.server.request_handlers <span class="kw">import</span> DefaultRequestHandler
<span class="kw">from</span> a2a.server.routes <span class="kw">import</span> create_agent_card_routes, create_jsonrpc_routes

executor = A2AExecutor(agent, stream=<span class="kw">True</span>)
handler = DefaultRequestHandler(
    agent_executor=executor,
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)
<span class="cm"># Starlette app with AgentCard + JSON-RPC routes</span></pre>
</div>

<h2>🧪 实战追踪：编排 Agent 通过 A2A 调用远程翻译 Agent</h2>
<p>把抽象协议落到一次真实调用上。场景：一个<strong>编排 Agent</strong> 要把文本交给独立部署的<strong>翻译 Agent</strong>——两者在不同进程、不同机器，只靠 A2A 标准协议对话。跟着这条链路走一遍，"Agent 当服务"就具体了。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>构造本地代理（客户端）</h4><p><span class="mono">a2a = A2AAgent(url="http://translator/a2a")</span>。只给 <span class="mono">url</span> 时，内部用 <span class="mono">minimal_agent_card(url)</span>（<span class="mono">_agent.py:222</span>）合成一张最小 AgentCard；也可直接传 <span class="mono">agent_card=</span>。两者都不给会抛 <span class="mono">"Either agent_card or url must be provided"</span>（<span class="mono">:220</span>）。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>像本地 Agent 一样调用</h4><p><span class="mono">await a2a.run("把这段翻成法语")</span>。<span class="mono">A2AAgent</span>（<span class="mono">_agent.py:154</span>）把请求包装为 A2A <span class="mono">Message</span>，经 <strong>JSON-RPC over HTTP</strong> POST 给远程——调用方代码和调本地 Agent <strong>完全一样</strong>。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>远程侧执行</h4><p>远程的 <span class="mono">A2AExecutor.execute(context, event_queue)</span>（<span class="mono">_a2a_executor.py:139</span>）跑真正的翻译 Agent，把产出作为事件写回 <span class="mono">event_queue</span>；构造时 <span class="mono">stream=True</span>（<span class="mono">:92</span>）则增量回流。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>会话与续传</h4><p>客户端 <span class="mono">A2AAgentSession</span>（<span class="mono">_agent.py:51</span>）维护 <span class="mono">context_id / task_id / task_state</span>；长任务用 <span class="mono">A2AContinuationToken</span>（<span class="mono">:129</span>）拿回执续传，不必一次跑完。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>结果回流</h4><p>翻译结果回到编排 Agent，对它而言这<strong>就是一次普通的"子 Agent 调用"返回</strong>——远程 Agent 的实现、模型、部署位置全部被协议挡在背后。</p></div></div>
</div>

<div class="flow">
  <div class="node hl"><div class="nt">编排 Agent</div><div class="nd">发起调用</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">A2AAgent</div><div class="nd">本地代理 · 客户端</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">HTTP / JSON-RPC</div><div class="nd">标准协议线</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">A2AExecutor</div><div class="nd">远程服务端</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">翻译 Agent</div><div class="nd">独立部署</div></div>
</div>
<p class="note">关键区分：<span class="mono">A2AAgent</span> 是<strong>调出去</strong>的本地代理（客户端），<span class="mono">A2AExecutor</span> 是<strong>被调用</strong>的服务端包装。同一个 Agent 可以既当别人的客户端、又把自己 expose 成服务端——这就是 Agent 网络能层层编排的根基。</p>

<h2>🧪 实战追踪：把同一次执行实时推给前端用户</h2>
<p>A2A 解决"Agent 找 Agent"，但用户还想<strong>看到过程</strong>。AG-UI 把同一次 Agent 执行变成一串<strong>结构化事件</strong>，经 SSE 推到浏览器。下面是一次带工具调用的完整事件时间线：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>挂上端点</h4><p>一行 <span class="mono">add_agent_framework_fastapi_endpoint(app, agent, path="/")</span>（<span class="mono">_endpoint.py:26</span>）把 Agent expose 成 AG-UI 端点；<span class="mono">agent</span> 可以是裸 Agent，也可以是 <span class="mono">AgentFrameworkAgent</span> 包装后的对象。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>开跑</h4><p>前端 POST 用户消息，端点开始 SSE 流。拿到首个 update（含服务端真实 ID）后，<span class="mono">yield RunStartedEvent(run_id, thread_id)</span>（<span class="mono">_agent_run.py:885</span>）。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>文本增量</h4><p><span class="mono">TextMessageStartEvent → TextMessageContentEvent(delta) × N → TextMessageEndEvent</span>——逐字推送，前端边收边渲染，体验上是"打字机"。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>工具调用可见</h4><p>Agent 调工具时依次发出 <span class="mono">ToolCallStartEvent → ToolCallArgsEvent → ToolCallEndEvent → ToolCallResultEvent</span>。用户能看见"正在调用翻译 Agent…"而不是干等一团黑盒。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>收尾</h4><p>正常结束发 <span class="mono">RunFinishedEvent</span>；出错则发 <span class="mono">RunErrorEvent</span>（<span class="mono">_endpoint.py:12</span>）。需要同步后台状态时还有 <span class="mono">StateSnapshotEvent</span> 把状态快照推给前端 UI。</p></div></div>
</div>

<div class="flow">
  <div class="node hl"><div class="nt">RunStarted</div><div class="nd">开跑</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">TextMessage*</div><div class="nd">Start·Content·End</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">ToolCall*</div><div class="nd">Start·Args·End·Result</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">RunFinished</div><div class="nd">收尾 / RunError</div></div>
</div>
<p class="note">这条时间线正是 <span class="mono">AgentFrameworkAgent</span> 的"简单线性流：RunStarted → 内容事件 → RunFinished"（<span class="mono">_agent.py:70</span> 原注释）。所有事件类型来自 <span class="mono">ag_ui.core</span>——AG-UI 是<strong>跨框架的开放协议</strong>，前端不绑定具体 Agent 实现，换后端不用改 UI。</p>

<h2>🔍 真实源码：两个包的入口符号</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">a2a / ag-ui __init__.py</span><span class="ln">两个包对外导出的入口符号（逐字核对）</span></div>
<pre class="code"><span class="cm"># agent_framework_a2a/__init__.py</span>
<span class="kw">from</span> ._a2a_executor <span class="kw">import</span> A2AExecutor       <span class="cm"># 服务端：把本地 Agent expose 成 A2A 服务</span>
<span class="kw">from</span> ._agent <span class="kw">import</span> A2AAgent, A2AAgentSession, A2AContinuationToken  <span class="cm"># 客户端 + 会话 + 续传</span>
__all__ = [<span class="st">"A2AAgent"</span>, <span class="st">"A2AAgentSession"</span>, <span class="st">"A2AContinuationToken"</span>, <span class="st">"A2AExecutor"</span>]

<span class="cm"># agent_framework_ag_ui/__init__.py</span>
<span class="kw">from</span> ._agent <span class="kw">import</span> AgentFrameworkAgent
<span class="kw">from</span> ._endpoint <span class="kw">import</span> add_agent_framework_fastapi_endpoint
<span class="kw">from</span> ._event_converters <span class="kw">import</span> AGUIEventConverter
<span class="kw">from</span> ._workflow <span class="kw">import</span> AgentFrameworkWorkflow, WorkflowFactory
<span class="cm"># 入口签名（_endpoint.py:26）：</span>
<span class="kw">def</span> <span class="fn">add_agent_framework_fastapi_endpoint</span>(app: FastAPI, agent, path: str = <span class="st">"/"</span>): ...</pre>
</div>
<p>两份 <span class="mono">__all__</span> 一眼看清"对外接口"：A2A 暴露 <strong>4 个</strong>符号（一个服务端 <span class="mono">A2AExecutor</span> + 一个客户端 <span class="mono">A2AAgent</span> + 会话 <span class="mono">A2AAgentSession</span> / 续传 <span class="mono">A2AContinuationToken</span>）；AG-UI 的核心是 <strong>包装类 + 一行端点函数</strong>。这正是"薄适配层"的体现——核心 Agent 不动，套上不同入口就接入不同协议。</p>

<h2>为什么要"标准化"Agent 间 / Agent-UI 通信</h2>
<p>没有标准协议时，每接一个新 Agent 或新前端都要写一套私有适配，连接数随规模爆炸；A2A 与 AG-UI 把这两条边各自<strong>收敛成一个协议</strong>，新成员只需"说同一种话"：</p>
<table class="t">
  <tr><th>维度</th><th>A2A（Agent ↔ Agent）</th><th>AG-UI（Agent ↔ 前端）</th></tr>
  <tr><td><strong>通信形态</strong></td><td>请求/响应 · JSON-RPC over HTTP</td><td>单向事件流 · SSE</td></tr>
  <tr><td><strong>发现机制</strong></td><td>AgentCard（能力/端点自描述）</td><td>端点 path + 事件 schema</td></tr>
  <tr><td><strong>状态/续传</strong></td><td>context_id/task_id + ContinuationToken</td><td>thread_id/run_id + StateSnapshot</td></tr>
  <tr><td><strong>典型消费者</strong></td><td>另一个 Agent / 编排器</td><td>浏览器 / 桌面 UI</td></tr>
  <tr><td><strong>核心入口</strong></td><td class="mono">A2AAgent / A2AExecutor</td><td class="mono">add_agent_framework_fastapi_endpoint</td></tr>
</table>
<p>两者<strong>正交</strong>：一个管"横向"的 Agent 互联，一个管"纵向"的 Agent 向人汇报。真实系统常常<strong>同时用</strong>——编排 Agent 用 A2A 调远程子 Agent，同时用 AG-UI 把"正在调用 B…B 返回了…"实时画给用户。它们与 L24 的 <a href="24-mcp.html">MCP</a>（工具级互通）、L25 的 <a href="25-hosted-agents.html">Foundry Hosting</a>（云端托管）一起，构成 Agent <strong>对外通信的四个方向</strong>：工具、托管、Agent 互调、UI 推送——每个都是可选薄层，核心逻辑只写一次。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> A2A 深入 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">A2A 的核心类：
<pre class="code"><span class="cm"># 客户端：调用远程 A2A Agent</span>
<span class="kw">from</span> agent_framework.a2a <span class="kw">import</span> A2AAgent
a2a_agent = A2AAgent(url=<span class="st">"http://remote-agent/a2a"</span>)
response = <span class="kw">await</span> a2a_agent.run(<span class="st">"Translate this"</span>)

<span class="cm"># 服务端：把本地 Agent 暴露为 A2A 服务</span>
<span class="kw">from</span> agent_framework.a2a <span class="kw">import</span> A2AExecutor
executor = A2AExecutor(my_agent, stream=<span class="kw">True</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">复杂业务需要<strong>多个 Agent 协作</strong>：一个做翻译，一个做摘要，一个做质量检查。
        A2A 让每个 Agent 独立部署并通过标准协议互调，不需要紧耦合。
        <span class="mono">A2AAgentSession</span> 自动管理 context_id / task_id / task_state。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">A2AAgent</span> 包装 <span class="mono">BaseAgent</span> 为 A2A 客户端，
        <span class="mono">A2AExecutor</span> 把任何 MAF Agent 暴露为 A2A 服务。
        支持 AgentCard 发现、JSON-RPC 通信、长时间任务续传（<span class="mono">A2AContinuationToken</span>）。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>MCP 互调</strong>（更底层，工具级别而非 Agent 级别）；
        <strong>REST API 自定义</strong>（灵活但缺乏标准化的 Agent 发现和任务管理）；
        <strong>消息队列 Agent</strong>（适合异步但不适合请求/响应模式）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> AG-UI 深入 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">AG-UI 快速集成到 FastAPI：
<pre class="code"><span class="kw">from</span> agent_framework.ag_ui <span class="kw">import</span> (
    add_agent_framework_fastapi_endpoint,
    AgentFrameworkAgent,
)
<span class="kw">from</span> fastapi <span class="kw">import</span> FastAPI

app = FastAPI()
ag_ui_agent = AgentFrameworkAgent(agent=my_agent)
add_agent_framework_fastapi_endpoint(app, ag_ui_agent)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">用户需要<strong>看到 Agent 在做什么</strong>：中间步骤、工具调用、状态变化。
        AG-UI 协议让 Agent 以结构化事件流（RunStarted → 内容事件 → RunFinished）
        向 UI 推送实时更新，而不只是最终结果。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">AgentFrameworkAgent</span> 把 MAF Agent 包装为 AG-UI 兼容对象，
        <span class="mono">AGUIEventConverter</span> 自动转换框架内部事件为 AG-UI 事件。
        支持状态 schema（dict 或 Pydantic）、预测性状态更新和中断流程。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>Server-Sent Events 自定义</strong>（灵活但没有标准事件格式）；
        <strong>WebSocket 自定义</strong>（双向但要自己定义协议）；
        <strong>Vercel AI SDK useChat</strong>（前端友好但绑定 Vercel 生态）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> A2A + AG-UI 组合 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">两个协议可以组合使用：
<pre class="code"><span class="cm"># Agent A (后端) 通过 A2A 调用 Agent B</span>
a2a_agent = A2AAgent(url=<span class="st">"http://agent-b/a2a"</span>)

<span class="cm"># Agent A 同时通过 AG-UI 向前端推送进度</span>
ag_ui_agent = AgentFrameworkAgent(agent=agent_a)
add_agent_framework_fastapi_endpoint(app, ag_ui_agent)

<span class="cm"># 用户看到：Agent A 正在调用 Agent B...</span>
<span class="cm"># 用户看到：Agent B 返回了翻译结果...</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">真实场景中，用户需要看到多 Agent 协作的<strong>全过程</strong>：
        A2A 管理 Agent 间的调用，AG-UI 把过程实时展示给用户。
        两者缺一不可——缺了 A2A 就没有 Agent 互调，缺了 AG-UI 用户就看不到过程。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">两个协议<strong>正交设计</strong>：A2A 解决"Agent 间如何通信"，AG-UI 解决"Agent 如何向用户汇报"。
        框架内的事件（usage、custom events）自动映射到 AG-UI 的 CUSTOM 事件类型，
        多模态内容（图片、文件）也有标准化支持。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>单体 Agent + 直接 UI</strong>（简单但不可扩展到多 Agent）；
        <strong>消息总线 + 自定义 UI 协议</strong>（灵活但开发量大）；
        <strong>LangGraph Studio</strong>（可视化调试但不是生产 UI 方案）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 什么时候用哪个 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">选择指南：
<pre class="code"><span class="cm"># 需要 Agent 互相调用？ → A2A</span>
<span class="cm"># 需要向用户实时展示进度？ → AG-UI</span>
<span class="cm"># 需要跨框架工具复用？ → MCP (L24)</span>
<span class="cm"># 需要云端托管？ → Foundry Hosting (L25)</span>

<span class="cm"># 多 Agent + 用户界面 → A2A + AG-UI 组合</span>
<span class="cm"># 单 Agent + 简单部署 → Foundry Hosting</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">MAF 提供了多种"对外暴露"方式（MCP / Foundry / A2A / AG-UI），
        选错方式会增加不必要的复杂度。理解每种协议的定位才能做出正确选择。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">每种协议都是<strong>可选的薄包装层</strong>——Agent 核心逻辑完全不变。
        你可以先用 Foundry 托管单 Agent，之后加 A2A 做多 Agent 协作，
        再加 AG-UI 做实时 UI。渐进式采用，不用一次全上。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>全部 REST API 自定义</strong>（最灵活但重复造轮子）；
        <strong>GraphQL subscriptions</strong>（适合复杂查询但 Agent 场景过于复杂）；
        <strong>gRPC streaming</strong>（高性能但生态支持有限）。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><strong>A2A</strong>：Agent-to-Agent 协议——<span class="mono">A2AAgent</span>（客户端）+ <span class="mono">A2AExecutor</span>（服务端），支持 AgentCard 发现。</li>
    <li><strong>AG-UI</strong>：Agent-to-UI 协议——<span class="mono">AgentFrameworkAgent</span> 包装 + FastAPI 端点一行集成。</li>
    <li>两者<strong>正交</strong>：A2A 管"Agent 间"，AG-UI 管"Agent → 用户"，可独立或组合使用。</li>
    <li>所有协议都是<strong>可选薄层</strong>，Agent 核心代码不变。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>四种协议（MCP / Foundry / A2A / AG-UI）覆盖 Agent 对外通信的所有方向</strong>：
  工具调用、云端托管、Agent 互调、UI 推送。
  每个都是可选的薄适配层——Agent 核心逻辑写一次，按需插上不同的"通信插头"。
</div>
"""
L26_EN = r"""
<p class="lead"><strong>A2A (Agent-to-Agent)</strong> exposes an Agent as a service for other Agents to call;
<strong>AG-UI</strong> gives Agents a structured real-time channel to the frontend —
together they connect "Agent ↔ Agent" and "Agent ↔ User Interface".</p>

<div class="card analogy">
  <div class="tag">📚 Analogy</div>
  A2A is a <strong>B2B API</strong> between companies — Company A's Agent can call Company B's Agent service.
  AG-UI is the <strong>customer-facing display</strong> — the backend Agent's progress and intermediate results
  stream to the screen in real time.
</div>

<h2>A2A vs AG-UI</h2>
<table class="t">
  <tr><th>Protocol</th><th>Direction</th><th>Purpose</th><th>Package</th></tr>
  <tr><td>A2A</td><td>Agent → Agent</td><td>Expose an Agent as a callable service for other Agents</td><td class="mono">agent-framework-a2a</td></tr>
  <tr><td>AG-UI</td><td>Agent → UI</td><td>Push real-time updates to the UI during Agent execution</td><td class="mono">agent-framework-ag-ui</td></tr>
</table>

<h2>A2A server example</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">A2A server</span></div>
<pre><span class="kw">from</span> agent_framework.a2a <span class="kw">import</span> A2AExecutor
<span class="kw">from</span> a2a.server.request_handlers <span class="kw">import</span> DefaultRequestHandler
<span class="kw">from</span> a2a.server.routes <span class="kw">import</span> create_agent_card_routes, create_jsonrpc_routes

executor = A2AExecutor(agent, stream=<span class="kw">True</span>)
handler = DefaultRequestHandler(
    agent_executor=executor,
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)
<span class="cm"># Starlette app with AgentCard + JSON-RPC routes</span></pre>
</div>

<h2>🧪 Worked example: an orchestrator Agent calls a remote translator via A2A</h2>
<p>Ground the abstract protocol in one real call. Scenario: an <strong>orchestrator Agent</strong> hands text to an independently deployed <strong>translator Agent</strong> — different processes, different machines, talking only over the A2A standard. Walk the path once and "Agent-as-a-service" becomes concrete.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Build the local proxy (client)</h4><p><span class="mono">a2a = A2AAgent(url="http://translator/a2a")</span>. Given only a <span class="mono">url</span>, it synthesises a minimal AgentCard via <span class="mono">minimal_agent_card(url)</span> (<span class="mono">_agent.py:222</span>); you may also pass <span class="mono">agent_card=</span>. Neither raises <span class="mono">"Either agent_card or url must be provided"</span> (<span class="mono">:220</span>).</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Call it like a local Agent</h4><p><span class="mono">await a2a.run("Translate this to French")</span>. <span class="mono">A2AAgent</span> (<span class="mono">_agent.py:154</span>) wraps the request as an A2A <span class="mono">Message</span> and POSTs it over <strong>JSON-RPC over HTTP</strong> — the calling code is <strong>identical</strong> to calling a local Agent.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>The remote side executes</h4><p>The remote <span class="mono">A2AExecutor.execute(context, event_queue)</span> (<span class="mono">_a2a_executor.py:139</span>) runs the real translator Agent and writes output as events to <span class="mono">event_queue</span>; with <span class="mono">stream=True</span> (<span class="mono">:92</span>) deltas flow back incrementally.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Session &amp; continuation</h4><p>The client <span class="mono">A2AAgentSession</span> (<span class="mono">_agent.py:51</span>) tracks <span class="mono">context_id / task_id / task_state</span>; long-running tasks use <span class="mono">A2AContinuationToken</span> (<span class="mono">:129</span>) to resume from a receipt rather than finishing in one shot.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>The result flows back</h4><p>The translation returns to the orchestrator, which sees it as <strong>just another "sub-Agent call" returning</strong> — the remote Agent's implementation, model and deployment location are all hidden behind the protocol.</p></div></div>
</div>

<div class="flow">
  <div class="node hl"><div class="nt">Orchestrator</div><div class="nd">initiates call</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">A2AAgent</div><div class="nd">local proxy · client</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">HTTP / JSON-RPC</div><div class="nd">standard wire</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">A2AExecutor</div><div class="nd">remote server</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Translator</div><div class="nd">deployed apart</div></div>
</div>
<p class="note">Key distinction: <span class="mono">A2AAgent</span> is the <strong>outbound</strong> local proxy (client); <span class="mono">A2AExecutor</span> is the <strong>inbound</strong> server-side wrapper. One Agent can be both someone's client <em>and</em> expose itself as a server — that's the basis for layered Agent orchestration.</p>

<h2>🧪 Worked example: stream that same run to a frontend user</h2>
<p>A2A handles "Agent finds Agent", but the user still wants to <strong>see the process</strong>. AG-UI turns the same Agent run into a stream of <strong>structured events</strong> pushed over SSE to the browser. Here is the full event timeline of a run that calls a tool:</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Mount the endpoint</h4><p>One line, <span class="mono">add_agent_framework_fastapi_endpoint(app, agent, path="/")</span> (<span class="mono">_endpoint.py:26</span>), exposes the Agent as an AG-UI endpoint; <span class="mono">agent</span> can be a raw Agent or an <span class="mono">AgentFrameworkAgent</span> wrapper.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Kick off</h4><p>The frontend POSTs a user message and the endpoint opens an SSE stream. After the first update (carrying the service's real IDs) it does <span class="mono">yield RunStartedEvent(run_id, thread_id)</span> (<span class="mono">_agent_run.py:885</span>).</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Text deltas</h4><p><span class="mono">TextMessageStartEvent → TextMessageContentEvent(delta) × N → TextMessageEndEvent</span> — token by token, the frontend renders as it receives, giving the "typewriter" feel.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Tool calls made visible</h4><p>When the Agent calls a tool it emits, in order, <span class="mono">ToolCallStartEvent → ToolCallArgsEvent → ToolCallEndEvent → ToolCallResultEvent</span>. The user sees "calling the translator Agent…" instead of staring at a black box.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Wrap up</h4><p>A normal finish emits <span class="mono">RunFinishedEvent</span>; an error emits <span class="mono">RunErrorEvent</span> (<span class="mono">_endpoint.py:12</span>). To sync backend state there is also <span class="mono">StateSnapshotEvent</span> pushing a state snapshot to the UI.</p></div></div>
</div>

<div class="flow">
  <div class="node hl"><div class="nt">RunStarted</div><div class="nd">kick off</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">TextMessage*</div><div class="nd">Start·Content·End</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">ToolCall*</div><div class="nd">Start·Args·End·Result</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">RunFinished</div><div class="nd">wrap up / RunError</div></div>
</div>
<p class="note">This timeline is exactly <span class="mono">AgentFrameworkAgent</span>'s "simple linear flow: RunStarted → content events → RunFinished" (<span class="mono">_agent.py:70</span> original comment). All event types come from <span class="mono">ag_ui.core</span> — AG-UI is a <strong>cross-framework open protocol</strong>, so the frontend isn't bound to a specific Agent implementation; swap the backend without touching the UI.</p>

<h2>🔍 Real source: the entry symbols of both packages</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">a2a / ag-ui __init__.py</span><span class="ln">the exported entry symbols of both packages (verified verbatim)</span></div>
<pre class="code"><span class="cm"># agent_framework_a2a/__init__.py</span>
<span class="kw">from</span> ._a2a_executor <span class="kw">import</span> A2AExecutor       <span class="cm"># server: expose a local Agent as an A2A service</span>
<span class="kw">from</span> ._agent <span class="kw">import</span> A2AAgent, A2AAgentSession, A2AContinuationToken  <span class="cm"># client + session + continuation</span>
__all__ = [<span class="st">"A2AAgent"</span>, <span class="st">"A2AAgentSession"</span>, <span class="st">"A2AContinuationToken"</span>, <span class="st">"A2AExecutor"</span>]

<span class="cm"># agent_framework_ag_ui/__init__.py</span>
<span class="kw">from</span> ._agent <span class="kw">import</span> AgentFrameworkAgent
<span class="kw">from</span> ._endpoint <span class="kw">import</span> add_agent_framework_fastapi_endpoint
<span class="kw">from</span> ._event_converters <span class="kw">import</span> AGUIEventConverter
<span class="kw">from</span> ._workflow <span class="kw">import</span> AgentFrameworkWorkflow, WorkflowFactory
<span class="cm"># entry signature (_endpoint.py:26):</span>
<span class="kw">def</span> <span class="fn">add_agent_framework_fastapi_endpoint</span>(app: FastAPI, agent, path: str = <span class="st">"/"</span>): ...</pre>
</div>
<p>The two <span class="mono">__all__</span> lists make the "public surface" obvious: A2A exports <strong>4</strong> symbols (one server <span class="mono">A2AExecutor</span> + one client <span class="mono">A2AAgent</span> + session <span class="mono">A2AAgentSession</span> / continuation <span class="mono">A2AContinuationToken</span>); AG-UI's core is a <strong>wrapper class + a one-line endpoint function</strong>. This is the "thin adapter" idea in the flesh — the core Agent stays put, and a different entry point plugs it into a different protocol.</p>

<h2>Why "standardize" Agent-to-Agent / Agent-to-UI communication</h2>
<p>Without a standard, every new Agent or frontend needs its own private adapter and the connection count explodes with scale; A2A and AG-UI each <strong>collapse one of those edges into a single protocol</strong>, so a new member just has to "speak the same language":</p>
<table class="t">
  <tr><th>Dimension</th><th>A2A (Agent ↔ Agent)</th><th>AG-UI (Agent ↔ frontend)</th></tr>
  <tr><td><strong>Shape</strong></td><td>request/response · JSON-RPC over HTTP</td><td>one-way event stream · SSE</td></tr>
  <tr><td><strong>Discovery</strong></td><td>AgentCard (self-describes capabilities/endpoint)</td><td>endpoint path + event schema</td></tr>
  <tr><td><strong>State/continuation</strong></td><td>context_id/task_id + ContinuationToken</td><td>thread_id/run_id + StateSnapshot</td></tr>
  <tr><td><strong>Typical consumer</strong></td><td>another Agent / orchestrator</td><td>browser / desktop UI</td></tr>
  <tr><td><strong>Core entry</strong></td><td class="mono">A2AAgent / A2AExecutor</td><td class="mono">add_agent_framework_fastapi_endpoint</td></tr>
</table>
<p>The two are <strong>orthogonal</strong>: one governs "horizontal" Agent interconnect, the other "vertical" Agent-to-human reporting. Real systems often use <strong>both at once</strong> — the orchestrator calls a remote sub-Agent over A2A while painting "calling B… B returned…" to the user over AG-UI. Together with L24's <a href="24-mcp.html">MCP</a> (tool-level interop) and L25's <a href="25-hosted-agents.html">Foundry Hosting</a> (cloud hosting), they form the <strong>four outward directions</strong> of Agent communication: tools, hosting, Agent interop, UI push — each an optional thin layer over core logic you write once.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> A2A deep dive <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Core A2A classes:
<pre class="code"><span class="cm"># Client: call a remote A2A Agent</span>
<span class="kw">from</span> agent_framework.a2a <span class="kw">import</span> A2AAgent
a2a_agent = A2AAgent(url=<span class="st">"http://remote-agent/a2a"</span>)
response = <span class="kw">await</span> a2a_agent.run(<span class="st">"Translate this"</span>)

<span class="cm"># Server: expose local Agent as A2A service</span>
<span class="kw">from</span> agent_framework.a2a <span class="kw">import</span> A2AExecutor
executor = A2AExecutor(my_agent, stream=<span class="kw">True</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Complex tasks need <strong>multi-Agent collaboration</strong>: one translates, one summarises, one QA-checks.
        A2A lets each Agent deploy independently and interop via a standard protocol — no tight coupling.
        <span class="mono">A2AAgentSession</span> auto-manages context_id / task_id / task_state.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">A2AAgent</span> wraps <span class="mono">BaseAgent</span> as an A2A client;
        <span class="mono">A2AExecutor</span> exposes any MAF Agent as an A2A service.
        Supports AgentCard discovery, JSON-RPC communication and long-running task continuation
        (<span class="mono">A2AContinuationToken</span>).</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>MCP interop</strong> (lower level — tool-level, not Agent-level);
        <strong>Custom REST APIs</strong> (flexible but no standard Agent discovery or task management);
        <strong>Message-queue Agents</strong> (good for async but not request/response).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> AG-UI deep dive <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Quick FastAPI integration:
<pre class="code"><span class="kw">from</span> agent_framework.ag_ui <span class="kw">import</span> (
    add_agent_framework_fastapi_endpoint,
    AgentFrameworkAgent,
)
<span class="kw">from</span> fastapi <span class="kw">import</span> FastAPI

app = FastAPI()
ag_ui_agent = AgentFrameworkAgent(agent=my_agent)
add_agent_framework_fastapi_endpoint(app, ag_ui_agent)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Users need to <strong>see what the Agent is doing</strong>: intermediate steps, tool calls, state changes.
        AG-UI pushes structured event streams (RunStarted → content events → RunFinished)
        to the UI in real time — not just the final answer.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">AgentFrameworkAgent</span> wraps MAF Agents for AG-UI compatibility;
        <span class="mono">AGUIEventConverter</span> auto-converts internal events to AG-UI events.
        Supports state schemas (dict or Pydantic), predictive state updates and interrupt flows.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Custom SSE</strong> (flexible but no standard event format);
        <strong>Custom WebSocket protocol</strong> (bidirectional but you define everything yourself);
        <strong>Vercel AI SDK useChat</strong> (frontend-friendly but Vercel-ecosystem-locked).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Combining A2A + AG-UI <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">The two protocols work together:
<pre class="code"><span class="cm"># Agent A (backend) calls Agent B via A2A</span>
a2a_agent = A2AAgent(url=<span class="st">"http://agent-b/a2a"</span>)

<span class="cm"># Agent A streams progress to UI via AG-UI</span>
ag_ui_agent = AgentFrameworkAgent(agent=agent_a)
add_agent_framework_fastapi_endpoint(app, ag_ui_agent)

<span class="cm"># User sees: Agent A is calling Agent B...</span>
<span class="cm"># User sees: Agent B returned the translation...</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">In real scenarios users need the <strong>full picture</strong> of multi-Agent collaboration:
        A2A manages Agent-to-Agent calls while AG-UI shows the user the live process.
        Without A2A there's no Agent interop; without AG-UI the user sees nothing until the end.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">The two protocols are <strong>orthogonal</strong>: A2A solves "how Agents talk to each other";
        AG-UI solves "how Agents report to users". Internal events (usage, custom events)
        auto-map to AG-UI CUSTOM event types; multimodal content (images, files) has standard support.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Monolithic Agent + direct UI</strong> (simple but won't scale to multi-Agent);
        <strong>Message bus + custom UI protocol</strong> (flexible but heavy development);
        <strong>LangGraph Studio</strong> (visual debugging, not a production UI solution).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> When to use each <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Selection guide:
<pre class="code"><span class="cm"># Agents need to call each other? → A2A</span>
<span class="cm"># Need real-time UI progress? → AG-UI</span>
<span class="cm"># Cross-framework tool reuse? → MCP (L24)</span>
<span class="cm"># Cloud hosting? → Foundry Hosting (L25)</span>

<span class="cm"># Multi-Agent + user UI → A2A + AG-UI combo</span>
<span class="cm"># Single Agent + simple deploy → Foundry Hosting</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">MAF provides multiple "external exposure" mechanisms (MCP / Foundry / A2A / AG-UI).
        Choosing the wrong one adds unnecessary complexity. Understanding each protocol's purpose
        is key to making the right choice.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Every protocol is an <strong>optional thin wrapper</strong> — Agent core logic stays unchanged.
        Start with Foundry hosting for a single Agent, add A2A for multi-Agent collaboration,
        then layer AG-UI for real-time UI. Adopt incrementally, not all at once.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>All-custom REST APIs</strong> (most flexible but reinvents the wheel);
        <strong>GraphQL subscriptions</strong> (great for complex queries but overkill for Agent scenarios);
        <strong>gRPC streaming</strong> (high performance but limited ecosystem support).</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>A2A</strong>: Agent-to-Agent protocol — <span class="mono">A2AAgent</span> (client) + <span class="mono">A2AExecutor</span> (server), with AgentCard discovery.</li>
    <li><strong>AG-UI</strong>: Agent-to-UI protocol — <span class="mono">AgentFrameworkAgent</span> wrapper + one-line FastAPI integration.</li>
    <li>The two are <strong>orthogonal</strong>: A2A handles "inter-Agent", AG-UI handles "Agent → user". Use independently or together.</li>
    <li>All protocols are <strong>optional thin layers</strong> — core Agent code remains unchanged.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Four protocols (MCP / Foundry / A2A / AG-UI) cover every direction of Agent external communication</strong>:
  tool calls, cloud hosting, Agent interop, UI streaming.
  Each is an optional thin adapter — write Agent logic once, plug in whichever "communication socket" you need.
</div>
"""
L27_ZH = r"""
<p class="lead"><strong>Evaluation（评估）</strong>系统化测试 Agent 输出质量；
<strong>Time-travel（时间旅行）</strong>通过检查点回放调试工作流——两者合力让 Agent 从"能跑"进化到"可靠"。</p>

<div class="card analogy">
  <div class="tag">📚 生活类比</div>
  Evaluation 像<strong>考试阅卷</strong>——给 Agent 一组题目，用评分标准打分看它答得好不好；
  Time-travel 像<strong>比赛录像回放</strong>——出了问题可以倒回任意时刻，逐帧分析哪里出了错。
</div>

<h2>核心评估概念</h2>
<table class="t">
  <tr><th>概念</th><th>作用</th><th>源码</th></tr>
  <tr><td class="mono">EvalItem</td><td>一条评估数据 = 输入 + 预期输出</td><td class="mono">_evaluation.py</td></tr>
  <tr><td class="mono">Evaluator</td><td>评估器协议（Azure Foundry / 本地 LLM-as-judge / 自定义）</td><td class="mono">_evaluation.py</td></tr>
  <tr><td class="mono">RubricScore</td><td>多维度评分（如相关性、准确性、完整性）</td><td class="mono">_evaluation.py</td></tr>
  <tr><td class="mono">EvalResults</td><td>评估结果汇总（通过率、每项得分、报告链接）</td><td class="mono">_evaluation.py</td></tr>
</table>

<h2>评估流程示例</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">评估 Agent</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> (
    Agent, LocalEvaluator, evaluate_agent, evaluator, keyword_check
)

<span class="cm"># 自定义评估函数</span>
<span class="kw">@evaluator</span>
<span class="kw">def</span> is_helpful(response: <span class="kw">str</span>) -> <span class="kw">bool</span>:
    <span class="kw">return</span> len(response) > 10

<span class="cm"># 组合内置 + 自定义检查</span>
local = LocalEvaluator(keyword_check(<span class="st">"weather"</span>), is_helpful)

<span class="cm"># 跑评估</span>
results = <span class="kw">await</span> evaluate_agent(
    agent=agent,
    queries=[<span class="st">"What's the weather?"</span>, <span class="st">"Will it rain?"</span>],
    evaluators=local,
)
results[0].raise_for_status()  <span class="cm"># CI 中断言通过</span></pre>
</div>

<h2>🧪 实战追踪：评估如何在 CI 里挡住一次"回归"</h2>
<p>评估的真正价值不是"打个分"，而是<strong>在 prompt/模型变动时自动发现质量下滑</strong>。场景：你把 Agent 的 instructions 改成"回答更简洁"，结果它把关键短语"退款政策"也省掉了——靠裸眼根本看不出来。评估集会替你逮住：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>固化基线</h4><p>把一组 <span class="mono">queries</span> 和期望（<span class="mono">keyword_check("退款政策")</span>:1062 / <span class="mono">expected_output</span>）固化成评估集——这就是 Agent 的"测试用例"。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>做改动</h4><p>改 instructions、换模型或调工具。任何一处变动都可能悄悄改变输出质量。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>一行重跑</h4><p><span class="mono">evaluate_agent(agent=, queries=, evaluators=)</span>（<span class="mono">_evaluation.py:1629</span>）自动为每个 query 调 <span class="mono">agent.run()</span>，把交互转成 <span class="mono">EvalItem</span>（<span class="mono">:182</span>），再交给 <span class="mono">Evaluator.evaluate(items, *, eval_name)</span>（<span class="mono">:705</span>）打分。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>比对结果</h4><p>返回 <span class="mono">list[EvalResults]</span>（<span class="mono">:373</span>）。这次 <span class="mono">r.passed/r.total</span>（<span class="mono">:441/:451</span>）从 2/2 掉到 1/2，那条 <span class="mono">item.status</span> 变成 <span class="mono">"failed"</span>——关键短语丢了。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>CI 门控</h4><p><span class="mono">results[0].raise_for_status()</span>（<span class="mono">:470</span>）抛错 → 流水线变红 → 这次回归在合并前被挡下。评估从"人工抽查"升级成"自动护栏"。</p></div></div>
</div>

<div class="flow">
  <div class="node hl"><div class="nt">queries</div><div class="nd">测试输入</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">agent.run()</div><div class="nd">逐条执行</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">EvalItem</div><div class="nd">输入+响应+期望</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Evaluator.evaluate</div><div class="nd">打分</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">EvalResults</div><div class="nd">passed/total</div></div>
</div>
<p class="note"><span class="mono">evaluate_agent</span> 全是<strong>关键字参数</strong>（<span class="mono">*</span> 之后），<span class="mono">evaluators=</span> 是唯一必填项；只要传了 <span class="mono">responses=</span> 就跳过跑 Agent、直接评分已有响应。一条流水线把"批量跑 + 打分 + 断言"压成一次调用。</p>

<h2>🧪 实战追踪：Time-travel 如何从断点回放调试</h2>
<p>第二个场景：一个 5 步工作流在第 4 步因网络抖动失败。没有检查点，你只能从头重跑 4 步——既费时间又烧 token。有了检查点存储，每个超步后都落了一张 <span class="mono">WorkflowCheckpoint</span>，沿 <span class="mono">previous_checkpoint_id</span> 串成一条可回溯的<strong>时间线</strong>：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>开启检查点</h4><p>构建时传 <span class="mono">WorkflowBuilder(checkpoint_storage=storage)</span>（<span class="mono">_workflow_builder.py:96</span>）。注意：这是<strong>构造参数</strong>，不是 <span class="mono">with_checkpointing()</span> 方法。每个超步结束后框架自动 <span class="mono">save</span>（<span class="mono">:122</span>）一张检查点。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>串成时间线</h4><p>每张 <span class="mono">WorkflowCheckpoint</span>（<span class="mono">_checkpoint.py:31</span>）带 <span class="mono">previous_checkpoint_id</span>（<span class="mono">:75</span>）指向上一张——这条链就是"时间线"，可以倒回任意一帧。它还存 <span class="mono">workflow_name / graph_signature_hash / iteration_count</span>（<span class="mono">:71/:72/:84</span>）。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>出事</h4><p>第 4 步抛错；执行停下，但 step1–3 的状态已经分别落盘成 cp1/cp2/cp3，<strong>没有丢失</strong>。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>取回检查点</h4><p><span class="mono">cp = await storage.get_latest(workflow_name=wf.name)</span>（<span class="mono">:169</span>），或按 id 用 <span class="mono">load(checkpoint_id)</span>（<span class="mono">:133</span>）精确取任意一帧；<span class="mono">list_checkpoints</span>（<span class="mono">:147</span>）可列出整条时间线。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>回放续跑</h4><p><span class="mono">await wf.run(checkpoint_id=cp.checkpoint_id, checkpoint_storage=storage)</span>（<span class="mono">_workflow.py:681</span>）→ 内部 <span class="mono">restore_from_checkpoint</span>（<span class="mono">:660</span>）。已完成步骤跳过，只从断点续跑；<span class="mono">graph_signature_hash</span> 会先校验拓扑是否还匹配，防止把状态回放进一张改过结构的图。</p></div></div>
</div>

<div class="flow">
  <div class="node"><div class="nt">cp1</div><div class="nd">step1 后</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">cp2</div><div class="nd">step2 后</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">cp3</div><div class="nd">step3 后 · 从这里回放</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">step4…</div><div class="nd">只重跑未完成的</div></div>
</div>
<p class="note">链表方向：箭头是 <span class="mono">cp1 → cp2 → cp3</span> 的发生顺序，而 <span class="mono">previous_checkpoint_id</span> 是反向指针（<span class="mono">cp3.previous = cp2</span>）。两种存储实现：<span class="mono">InMemoryCheckpointStorage</span>（<span class="mono">:192</span>，测试用）与 <span class="mono">FileCheckpointStorage</span>（<span class="mono">:239</span>，落盘可跨进程）。</p>

<h2>🔍 真实源码：评估入口与检查点的数据结构</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_evaluation.py / _checkpoint.py</span><span class="ln">评估入口 + 检查点时间线（逐字核对）</span></div>
<pre class="code"><span class="cm"># _evaluation.py:1629 — 开发期最简评估入口（全关键字参数）</span>
<span class="kw">async def</span> <span class="fn">evaluate_agent</span>(*, agent=<span class="kw">None</span>, queries=<span class="kw">None</span>, expected_output=<span class="kw">None</span>,
        expected_tool_calls=<span class="kw">None</span>, responses=<span class="kw">None</span>,
        evaluators, eval_name=<span class="kw">None</span>, ...) -&gt; list[EvalResults]: ...

<span class="kw">class</span> <span class="fn">Evaluator</span>(Protocol):                              <span class="cm"># :683</span>
    <span class="kw">async def</span> <span class="fn">evaluate</span>(self, items: Sequence[EvalItem], *,
                       eval_name: str) -&gt; EvalResults: ...   <span class="cm"># :705</span>

<span class="cm"># _workflows/_checkpoint.py:31 — 一帧 = 时间线上的一个冻结点</span>
<span class="kw">@dataclass</span>
<span class="kw">class</span> <span class="fn">WorkflowCheckpoint</span>:
    workflow_name: str                                   <span class="cm"># :71</span>
    graph_signature_hash: str                            <span class="cm"># :72 校验拓扑</span>
    checkpoint_id: CheckpointID                          <span class="cm"># :74</span>
    previous_checkpoint_id: CheckpointID | <span class="kw">None</span> = <span class="kw">None</span>     <span class="cm"># :75 链=时间线</span>
    iteration_count: int = 0                             <span class="cm"># :84</span>

<span class="kw">class</span> <span class="fn">CheckpointStorage</span>(Protocol):                       <span class="cm"># :119</span>
    <span class="kw">async def</span> <span class="fn">save</span>(self, cp) -&gt; CheckpointID: ...           <span class="cm"># :122</span>
    <span class="kw">async def</span> <span class="fn">load</span>(self, checkpoint_id) -&gt; WorkflowCheckpoint: ...  <span class="cm"># :133</span>
    <span class="kw">async def</span> <span class="fn">get_latest</span>(self, *, workflow_name): ...       <span class="cm"># :169</span>

<span class="cm"># 回放 = 从某一帧续跑（_workflow.py:681）</span>
<span class="kw">await</span> wf.run(checkpoint_id=cp.checkpoint_id, checkpoint_storage=storage)</pre>
</div>
<p>两段源码对照看，"评估"和"时间旅行"的共性就清楚了：都是<strong>把一次执行变成可检查、可重放的数据</strong>。评估把交互冻成 <span class="mono">EvalItem</span> 交给打分协议；time-travel 把工作流状态冻成 <span class="mono">WorkflowCheckpoint</span> 串进时间线。两者都用 <span class="mono">Protocol</span> 定义可替换的后端（云端/本地评估器、内存/文件存储）。</p>

<h2>为什么"评估 + 回放"要凑成一对</h2>
<p>把它们放在同一课，是因为二者正好补齐了"让 Agent 可靠"闭环的两段：</p>
<table class="t">
  <tr><th>闭环阶段</th><th>谁负责</th><th>对应能力</th></tr>
  <tr><td><strong>发现</strong>问题</td><td class="mono">evaluate_agent</td><td>批量跑 + 打分，<span class="mono">raise_for_status()</span> 把回归挡在 CI</td></tr>
  <tr><td><strong>诊断</strong>原因</td><td class="mono">wf.run(checkpoint_id=)</td><td>从失败那一帧回放，逐步看每个 Executor 的输入输出</td></tr>
  <tr><td><strong>修复</strong>验证</td><td>两者协同</td><td>改完再 <span class="mono">evaluate_agent</span>，分数回升=修复成功</td></tr>
  <tr><td><strong>审计</strong>复现</td><td class="mono">WorkflowCheckpoint</td><td>检查点是确定性快照，<span class="mono">graph_signature_hash</span> 保证只回放进结构一致的图</td></tr>
</table>
<p>没有评估，你改完 prompt 只能"感觉好像变好了"；没有 time-travel，评估告诉你"第 3 条 query 失败了"却说不清<strong>哪一步</strong>错了。两者合起来，Agent 才真正从"能跑"走向"可靠、可回归、可审计"。它们和前面 L23–L26 的能力（技能、工具、托管、互联）一起，构成把 Agent 推上生产的完整工具箱。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 评估工作流 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">完整的评估流程：
<pre class="code"><span class="cm"># 1. 定义评估数据</span>
queries = [<span class="st">"What's the weather?"</span>, <span class="st">"Will it rain?"</span>]

<span class="cm"># 2. 运行 Agent 获取响应</span>
<span class="cm"># evaluate_agent() 自动为每个 query 调用 agent.run()</span>

<span class="cm"># 3. 评分</span>
<span class="cm"># 每个 Evaluator 对每条 (input, output) 打分</span>

<span class="cm"># 4. 查看结果</span>
<span class="kw">for</span> r <span class="kw">in</span> results:
    print(f<span class="st">"{r.provider}: {r.passed}/{r.total}"</span>)
    <span class="kw">for</span> item <span class="kw">in</span> r.items:
        <span class="kw">for</span> score <span class="kw">in</span> item.scores:
            print(f<span class="st">"  {score.name}: {'PASS' if score.passed else 'FAIL'}"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">LLM 输出是<strong>不确定的</strong>——同一个问题每次回答可能不同。
        没有系统化评估，你不知道改了 prompt 后 Agent 是变好还是变差。
        评估就是 Agent 的<strong>单元测试</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">evaluate_agent()</span> 一行跑完整流程：自动为每个 query 调用 <span class="mono">agent.run()</span>，
        收集响应后交给 Evaluator 打分。支持多种后端：Azure AI Foundry 云端评估、
        <span class="mono">LocalEvaluator</span> 本地评估、自定义 <span class="mono">@evaluator</span> 函数。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>手动测试</strong>（不可重复、不可扩展）；
        <strong>OpenAI Evals</strong>（OpenAI 专属）；
        <strong>RAGAS</strong>（专注 RAG 评估）；
        <strong>LangSmith</strong>（LangChain 生态的追踪 + 评估）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> RubricScore 多维评分 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a"><span class="mono">RubricScore</span> 把评估拆成多个维度：
<pre class="code"><span class="cm"># EvalScoreResult 中的维度评分</span>
<span class="cm"># score.dimensions 包含：</span>
<span class="cm">#   RubricScore(name="relevance", score=0.9)</span>
<span class="cm">#   RubricScore(name="accuracy", score=0.85)</span>
<span class="cm">#   RubricScore(name="completeness", score=0.7)</span>

<span class="cm"># EvalScoreResult 还有：</span>
<span class="cm">#   name: 评估器名称</span>
<span class="cm">#   score: 总分</span>
<span class="cm">#   passed: 是否通过阈值</span>
<span class="cm">#   sample: 原始评估器输出（rationale）</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">一个总分不够——Agent 回答可能"相关但不准确"或"准确但不完整"。
        多维评分让你精确定位 Agent 的<strong>弱项</strong>并针对性改进。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">EvalScoreResult</span> 包含总分 + 维度分 + 原始理由（sample）。
        <span class="mono">AgentEvalConverter</span> 自动把 Agent 的输入输出转换为评估格式。
        结果可直接 <span class="mono">raise_for_status()</span> 用于 CI 门控。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>LLM-as-judge 单维度</strong>（简单但信息量少）；
        <strong>人工标注</strong>（最准确但成本高、速度慢）；
        <strong>自定义 scorer 函数</strong>（灵活但需要更多代码，MAF 的 <span class="mono">@evaluator</span> 就是简化版）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Time-travel 机制 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">通过检查点实现工作流回放：
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> InMemoryCheckpointStorage

storage = InMemoryCheckpointStorage()
workflow = builder.build()

<span class="cm"># 首次运行——保存检查点</span>
<span class="kw">async for</span> event <span class="kw">in</span> workflow.run(message=10, stream=<span class="kw">True</span>):
    <span class="kw">if</span> should_interrupt(): <span class="kw">break</span>

<span class="cm"># 从检查点恢复——跳过已完成的步骤</span>
cp = <span class="kw">await</span> storage.get_latest(workflow_name=workflow.name)
<span class="kw">async for</span> event <span class="kw">in</span> workflow.run(
    checkpoint_id=cp.checkpoint_id, stream=<span class="kw">True</span>
):
    <span class="cm"># 已完成的 @step 直接返回缓存结果</span>
    <span class="cm"># 只有未完成的步骤真正执行</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">工作流可能因为网络故障、超时或人为中断而停在中途。
        没有检查点就得从头重跑（浪费时间和 token 费用）。
        Time-travel 让你<strong>从断点继续</strong>，已完成的步骤用缓存结果跳过。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">WorkflowCheckpoint</span> 捕获完整状态：消息历史、Executor 状态、
        迭代计数、待处理的 HITL 事件。
        <span class="mono">CheckpointStorage</span> 协议有内存和文件两种实现。
        Executor 通过 <span class="mono">on_checkpoint_save/restore</span> 钩子保存自定义状态。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>Durable Functions</strong>（Azure 的持久化执行，更底层）；
        <strong>Temporal.io</strong>（专业的工作流引擎，更重量级）；
        <strong>手动保存中间状态</strong>（可行但容易遗漏边界情况）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 评估 + 回放组合 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">评估和 time-travel 可以组合使用：
<pre class="code"><span class="cm"># 1. 跑评估，发现某个 query 失败</span>
results = <span class="kw">await</span> evaluate_agent(agent=agent, queries=[...])

<span class="cm"># 2. 对失败 query 的工作流做 time-travel 调试</span>
<span class="cm"># 从检查点回放，逐步检查每个 @step 的输入输出</span>

<span class="cm"># 3. 修复后重新评估，确认改进</span>
<span class="cm"># results[0].raise_for_status() 通过 = 修复成功</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">评估发现问题，time-travel 定位原因——这是<strong>发现 → 诊断 → 修复 → 验证</strong>的完整闭环。
        没有 time-travel，你只知道"这个 query 失败了"但不知道<strong>哪个步骤</strong>出了问题。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">评估和回放共享同一套 Agent / Workflow 抽象——评估跑 <span class="mono">agent.run()</span>，
        回放也跑 <span class="mono">workflow.run(checkpoint_id=...)</span>。
        HITL 场景下 <span class="mono">_set_responses</span> 可以预填人类回复，让回放完全自动化。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>纯日志分析</strong>（信息量不如检查点完整）；
        <strong>LangSmith Trace</strong>（可视化追踪但不能从断点恢复执行）；
        <strong>单元测试 mock</strong>（快但不测真实 LLM 行为）。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><strong>评估 = Agent 的单元测试</strong>：<span class="mono">EvalItem</span>（输入）→ <span class="mono">Evaluator</span>（打分）→ <span class="mono">EvalResults</span>（结果）。</li>
    <li><span class="mono">RubricScore</span> 支持多维度评分；<span class="mono">raise_for_status()</span> 用于 CI 门控。</li>
    <li><strong>Time-travel</strong>通过 <span class="mono">WorkflowCheckpoint</span> 保存/恢复完整状态，已完成步骤用缓存跳过。</li>
    <li>两者组合实现"发现问题 → 定位原因 → 修复 → 验证"的完整闭环。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>评估和回放共享同一套 Agent/Workflow 抽象</strong>——不需要额外的调试工具或追踪系统。
  一个 <span class="mono">evaluate_agent()</span> 调用 = 批量跑 Agent + 自动评分 + CI 集成。
  一个 <span class="mono">checkpoint_id</span> 参数 = 从任意断点恢复执行，逐步诊断问题。
</div>
"""
L27_EN = r"""
<p class="lead"><strong>Evaluation</strong> systematically tests Agent output quality;
<strong>Time-travel</strong> replays workflow runs from checkpoints for debugging —
together they take Agents from "it runs" to "it's reliable".</p>

<div class="card analogy">
  <div class="tag">📚 Analogy</div>
  Evaluation is <strong>grading an exam</strong> — give the Agent a set of questions, score the answers with a rubric.
  Time-travel is <strong>instant replay in sports</strong> — rewind to any moment and analyse frame-by-frame
  what went wrong.
</div>

<h2>Core evaluation concepts</h2>
<table class="t">
  <tr><th>Concept</th><th>Role</th><th>Source</th></tr>
  <tr><td class="mono">EvalItem</td><td>One eval datum = input + expected output</td><td class="mono">_evaluation.py</td></tr>
  <tr><td class="mono">Evaluator</td><td>Evaluator protocol (Azure Foundry / local LLM-as-judge / custom)</td><td class="mono">_evaluation.py</td></tr>
  <tr><td class="mono">RubricScore</td><td>Multi-dimensional score (e.g. relevance, accuracy, completeness)</td><td class="mono">_evaluation.py</td></tr>
  <tr><td class="mono">EvalResults</td><td>Result summary (pass rate, per-item scores, report URL)</td><td class="mono">_evaluation.py</td></tr>
</table>

<h2>Evaluation workflow</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">evaluate an Agent</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> (
    Agent, LocalEvaluator, evaluate_agent, evaluator, keyword_check
)

<span class="cm"># Custom evaluator function</span>
<span class="kw">@evaluator</span>
<span class="kw">def</span> is_helpful(response: <span class="kw">str</span>) -> <span class="kw">bool</span>:
    <span class="kw">return</span> len(response) > 10

<span class="cm"># Combine built-in + custom checks</span>
local = LocalEvaluator(keyword_check(<span class="st">"weather"</span>), is_helpful)

<span class="cm"># Run evaluation</span>
results = <span class="kw">await</span> evaluate_agent(
    agent=agent,
    queries=[<span class="st">"What's the weather?"</span>, <span class="st">"Will it rain?"</span>],
    evaluators=local,
)
results[0].raise_for_status()  <span class="cm"># assert pass in CI</span></pre>
</div>

<h2>🧪 Worked example: how evaluation blocks a "regression" in CI</h2>
<p>The real value of evaluation isn't "producing a score" — it's <strong>automatically catching quality drops when prompts/models change</strong>. Scenario: you change the Agent's instructions to "answer more concisely", and it quietly drops the key phrase "refund policy". The naked eye won't catch it; an eval set will:</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Freeze a baseline</h4><p>Pin a set of <span class="mono">queries</span> plus expectations (<span class="mono">keyword_check("refund policy")</span>:1062 / <span class="mono">expected_output</span>) into an eval set — these are the Agent's "test cases".</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Make a change</h4><p>Edit the instructions, swap the model, or tweak a tool. Any one of these can silently shift output quality.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Re-run in one line</h4><p><span class="mono">evaluate_agent(agent=, queries=, evaluators=)</span> (<span class="mono">_evaluation.py:1629</span>) calls <span class="mono">agent.run()</span> per query, converts each interaction into an <span class="mono">EvalItem</span> (<span class="mono">:182</span>), then hands them to <span class="mono">Evaluator.evaluate(items, *, eval_name)</span> (<span class="mono">:705</span>) for scoring.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Compare results</h4><p>It returns <span class="mono">list[EvalResults]</span> (<span class="mono">:373</span>). This time <span class="mono">r.passed/r.total</span> (<span class="mono">:441/:451</span>) drops from 2/2 to 1/2, and that item's <span class="mono">status</span> becomes <span class="mono">"failed"</span> — the key phrase is gone.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Gate CI</h4><p><span class="mono">results[0].raise_for_status()</span> (<span class="mono">:470</span>) raises → the pipeline turns red → the regression is blocked before merge. Evaluation goes from "manual spot-check" to "automated guardrail".</p></div></div>
</div>

<div class="flow">
  <div class="node hl"><div class="nt">queries</div><div class="nd">test inputs</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">agent.run()</div><div class="nd">run each</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">EvalItem</div><div class="nd">input+response+expected</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Evaluator.evaluate</div><div class="nd">score</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">EvalResults</div><div class="nd">passed/total</div></div>
</div>
<p class="note"><span class="mono">evaluate_agent</span> is all <strong>keyword-only</strong> (after the <span class="mono">*</span>), with <span class="mono">evaluators=</span> the only required argument; pass <span class="mono">responses=</span> and it skips running the Agent and scores existing responses directly. One pipeline compresses "batch-run + score + assert" into a single call.</p>

<h2>🧪 Worked example: how time-travel replays from a breakpoint</h2>
<p>Second scenario: a 5-step workflow fails at step 4 due to a network blip. Without checkpoints you'd rerun all 4 steps — wasting time and tokens. With checkpoint storage, each superstep dropped a <span class="mono">WorkflowCheckpoint</span>, chained via <span class="mono">previous_checkpoint_id</span> into a reversible <strong>timeline</strong>:</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Enable checkpointing</h4><p>Pass <span class="mono">WorkflowBuilder(checkpoint_storage=storage)</span> (<span class="mono">_workflow_builder.py:96</span>). Note: it's a <strong>constructor argument</strong>, not a <span class="mono">with_checkpointing()</span> method. After each superstep the framework auto-<span class="mono">save</span>s (<span class="mono">:122</span>) a checkpoint.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Chain into a timeline</h4><p>Every <span class="mono">WorkflowCheckpoint</span> (<span class="mono">_checkpoint.py:31</span>) carries a <span class="mono">previous_checkpoint_id</span> (<span class="mono">:75</span>) pointing at the prior one — that chain <em>is</em> the timeline, rewindable to any frame. It also stores <span class="mono">workflow_name / graph_signature_hash / iteration_count</span> (<span class="mono">:71/:72/:84</span>).</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>The failure</h4><p>Step 4 throws; execution halts, but the state of steps 1–3 has already been persisted as cp1/cp2/cp3 — <strong>nothing is lost</strong>.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Fetch a checkpoint</h4><p><span class="mono">cp = await storage.get_latest(workflow_name=wf.name)</span> (<span class="mono">:169</span>), or grab any exact frame by id with <span class="mono">load(checkpoint_id)</span> (<span class="mono">:133</span>); <span class="mono">list_checkpoints</span> (<span class="mono">:147</span>) enumerates the whole timeline.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Replay and resume</h4><p><span class="mono">await wf.run(checkpoint_id=cp.checkpoint_id, checkpoint_storage=storage)</span> (<span class="mono">_workflow.py:681</span>) → internally <span class="mono">restore_from_checkpoint</span> (<span class="mono">:660</span>). Completed steps are skipped; only the breakpoint onward reruns; <span class="mono">graph_signature_hash</span> first validates the topology still matches, preventing replay into a changed graph.</p></div></div>
</div>

<div class="flow">
  <div class="node"><div class="nt">cp1</div><div class="nd">after step1</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">cp2</div><div class="nd">after step2</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">cp3</div><div class="nd">after step3 · replay here</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">step4…</div><div class="nd">rerun only the unfinished</div></div>
</div>
<p class="note">Direction of the chain: the arrows show happen-order <span class="mono">cp1 → cp2 → cp3</span>, while <span class="mono">previous_checkpoint_id</span> is the back-pointer (<span class="mono">cp3.previous = cp2</span>). Two storage impls: <span class="mono">InMemoryCheckpointStorage</span> (<span class="mono">:192</span>, for tests) and <span class="mono">FileCheckpointStorage</span> (<span class="mono">:239</span>, persisted across processes).</p>

<h2>🔍 Real source: the eval entry point and the checkpoint structure</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">_evaluation.py / _checkpoint.py</span><span class="ln">eval entry + checkpoint timeline (verified verbatim)</span></div>
<pre class="code"><span class="cm"># _evaluation.py:1629 — the simplest dev-time eval entry (all keyword args)</span>
<span class="kw">async def</span> <span class="fn">evaluate_agent</span>(*, agent=<span class="kw">None</span>, queries=<span class="kw">None</span>, expected_output=<span class="kw">None</span>,
        expected_tool_calls=<span class="kw">None</span>, responses=<span class="kw">None</span>,
        evaluators, eval_name=<span class="kw">None</span>, ...) -&gt; list[EvalResults]: ...

<span class="kw">class</span> <span class="fn">Evaluator</span>(Protocol):                              <span class="cm"># :683</span>
    <span class="kw">async def</span> <span class="fn">evaluate</span>(self, items: Sequence[EvalItem], *,
                       eval_name: str) -&gt; EvalResults: ...   <span class="cm"># :705</span>

<span class="cm"># _workflows/_checkpoint.py:31 — one frame = a frozen point on a timeline</span>
<span class="kw">@dataclass</span>
<span class="kw">class</span> <span class="fn">WorkflowCheckpoint</span>:
    workflow_name: str                                   <span class="cm"># :71</span>
    graph_signature_hash: str                            <span class="cm"># :72 validates topology</span>
    checkpoint_id: CheckpointID                          <span class="cm"># :74</span>
    previous_checkpoint_id: CheckpointID | <span class="kw">None</span> = <span class="kw">None</span>     <span class="cm"># :75 chain = timeline</span>
    iteration_count: int = 0                             <span class="cm"># :84</span>

<span class="kw">class</span> <span class="fn">CheckpointStorage</span>(Protocol):                       <span class="cm"># :119</span>
    <span class="kw">async def</span> <span class="fn">save</span>(self, cp) -&gt; CheckpointID: ...           <span class="cm"># :122</span>
    <span class="kw">async def</span> <span class="fn">load</span>(self, checkpoint_id) -&gt; WorkflowCheckpoint: ...  <span class="cm"># :133</span>
    <span class="kw">async def</span> <span class="fn">get_latest</span>(self, *, workflow_name): ...       <span class="cm"># :169</span>

<span class="cm"># replay = resume from a frame (_workflow.py:681)</span>
<span class="kw">await</span> wf.run(checkpoint_id=cp.checkpoint_id, checkpoint_storage=storage)</pre>
</div>
<p>Read the two side by side and the commonality between "evaluation" and "time-travel" is clear: both <strong>turn one execution into inspectable, replayable data</strong>. Evaluation freezes the interaction into an <span class="mono">EvalItem</span> handed to a scoring protocol; time-travel freezes the workflow state into a <span class="mono">WorkflowCheckpoint</span> chained on a timeline. Both define swappable backends via a <span class="mono">Protocol</span> (cloud/local evaluators, in-memory/file storage).</p>

<h2>Why "evaluation + replay" make a pair</h2>
<p>They share a lesson because they complete the two halves of the "make the Agent reliable" loop:</p>
<table class="t">
  <tr><th>Loop stage</th><th>Owner</th><th>Capability</th></tr>
  <tr><td><strong>Detect</strong> the problem</td><td class="mono">evaluate_agent</td><td>batch-run + score; <span class="mono">raise_for_status()</span> blocks regressions in CI</td></tr>
  <tr><td><strong>Diagnose</strong> the cause</td><td class="mono">wf.run(checkpoint_id=)</td><td>replay from the failing frame, step through each Executor's I/O</td></tr>
  <tr><td><strong>Fix</strong> &amp; verify</td><td>both together</td><td>re-run <span class="mono">evaluate_agent</span>; the score recovering = the fix worked</td></tr>
  <tr><td><strong>Audit</strong> &amp; reproduce</td><td class="mono">WorkflowCheckpoint</td><td>a checkpoint is a deterministic snapshot; <span class="mono">graph_signature_hash</span> ensures replay only into a matching graph</td></tr>
</table>
<p>Without evaluation, after editing a prompt you can only "feel like it got better"; without time-travel, evaluation tells you "query 3 failed" but not <strong>which step</strong> broke. Together, the Agent truly moves from "it runs" to "reliable, regression-proof, auditable". Alongside the capabilities of L23–L26 (skills, tools, hosting, interconnect), they form the complete toolbox for pushing an Agent into production.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Evaluation workflow <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">The full evaluation flow:
<pre class="code"><span class="cm"># 1. Define eval data</span>
queries = [<span class="st">"What's the weather?"</span>, <span class="st">"Will it rain?"</span>]

<span class="cm"># 2. Run Agent to get responses</span>
<span class="cm"># evaluate_agent() calls agent.run() for each query</span>

<span class="cm"># 3. Score</span>
<span class="cm"># Each Evaluator scores every (input, output) pair</span>

<span class="cm"># 4. Inspect results</span>
<span class="kw">for</span> r <span class="kw">in</span> results:
    print(f<span class="st">"{r.provider}: {r.passed}/{r.total}"</span>)
    <span class="kw">for</span> item <span class="kw">in</span> r.items:
        <span class="kw">for</span> score <span class="kw">in</span> item.scores:
            print(f<span class="st">"  {score.name}: {'PASS' if score.passed else 'FAIL'}"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">LLM output is <strong>non-deterministic</strong> — the same question may get a different answer each time.
        Without systematic evaluation you can't tell whether a prompt change made the Agent better or worse.
        Evaluation is the Agent's <strong>unit test suite</strong>.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">evaluate_agent()</span> runs the full pipeline in one call: auto-invokes <span class="mono">agent.run()</span>
        for each query, collects responses, hands them to Evaluators. Supports multiple backends:
        Azure AI Foundry cloud eval, <span class="mono">LocalEvaluator</span> for local checks, custom <span class="mono">@evaluator</span> functions.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Manual testing</strong> (not repeatable, not scalable);
        <strong>OpenAI Evals</strong> (OpenAI-specific);
        <strong>RAGAS</strong> (focused on RAG evaluation);
        <strong>LangSmith</strong> (LangChain-ecosystem tracing + eval).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> RubricScore multi-dimensional scoring <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a"><span class="mono">RubricScore</span> breaks evaluation into dimensions:
<pre class="code"><span class="cm"># EvalScoreResult.dimensions contains:</span>
<span class="cm">#   RubricScore(name="relevance", score=0.9)</span>
<span class="cm">#   RubricScore(name="accuracy", score=0.85)</span>
<span class="cm">#   RubricScore(name="completeness", score=0.7)</span>

<span class="cm"># EvalScoreResult also has:</span>
<span class="cm">#   name: evaluator name</span>
<span class="cm">#   score: aggregate score</span>
<span class="cm">#   passed: whether threshold was met</span>
<span class="cm">#   sample: raw evaluator output (rationale)</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">A single aggregate score is not enough — an Agent response may be "relevant but inaccurate"
        or "accurate but incomplete". Multi-dimensional scoring pinpoints the Agent's <strong>weak spots</strong>
        for targeted improvement.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">EvalScoreResult</span> contains aggregate score + dimension scores + raw rationale (sample).
        <span class="mono">AgentEvalConverter</span> auto-converts Agent I/O to eval format.
        Results support <span class="mono">raise_for_status()</span> for CI gating.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Single-dimension LLM-as-judge</strong> (simple but low information);
        <strong>Human annotation</strong> (most accurate but costly and slow);
        <strong>Custom scorer functions</strong> (flexible but more code — MAF's <span class="mono">@evaluator</span> is the streamlined version).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Time-travel mechanics <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Replay a workflow from a checkpoint:
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> InMemoryCheckpointStorage

storage = InMemoryCheckpointStorage()
workflow = builder.build()

<span class="cm"># First run — checkpoints are saved</span>
<span class="kw">async for</span> event <span class="kw">in</span> workflow.run(message=10, stream=<span class="kw">True</span>):
    <span class="kw">if</span> should_interrupt(): <span class="kw">break</span>

<span class="cm"># Resume from checkpoint — skip completed steps</span>
cp = <span class="kw">await</span> storage.get_latest(workflow_name=workflow.name)
<span class="kw">async for</span> event <span class="kw">in</span> workflow.run(
    checkpoint_id=cp.checkpoint_id, stream=<span class="kw">True</span>
):
    <span class="cm"># Completed @step functions return cached results</span>
    <span class="cm"># Only pending steps actually execute</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Workflows can halt mid-way due to network failures, timeouts or deliberate interrupts.
        Without checkpoints you'd rerun everything from scratch (wasting time and token budget).
        Time-travel lets you <strong>resume from where you left off</strong> — completed steps use cached results.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">WorkflowCheckpoint</span> captures full state: message history, Executor states,
        iteration count and pending HITL events. <span class="mono">CheckpointStorage</span> protocol has in-memory
        and file implementations. Executors save custom state via <span class="mono">on_checkpoint_save/restore</span> hooks.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Durable Functions</strong> (Azure's durable execution — lower level);
        <strong>Temporal.io</strong> (dedicated workflow engine — heavier);
        <strong>Manual intermediate state</strong> (works but easy to miss edge cases).</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Combining eval + replay <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Evaluation and time-travel work hand-in-hand:
<pre class="code"><span class="cm"># 1. Run eval — spot a failing query</span>
results = <span class="kw">await</span> evaluate_agent(agent=agent, queries=[...])

<span class="cm"># 2. Time-travel the failing workflow</span>
<span class="cm"># Replay from checkpoint, inspect each @step's I/O</span>

<span class="cm"># 3. Fix and re-evaluate to confirm improvement</span>
<span class="cm"># results[0].raise_for_status() passes = fix confirmed</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Evaluation spots the problem; time-travel locates the cause — a complete
        <strong>detect → diagnose → fix → verify</strong> loop. Without time-travel you know
        "this query failed" but not <strong>which step</strong> went wrong.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Evaluation and replay share the same Agent / Workflow abstractions — eval runs
        <span class="mono">agent.run()</span>; replay runs <span class="mono">workflow.run(checkpoint_id=...)</span>.
        In HITL scenarios <span class="mono">_set_responses</span> pre-fills human answers so replay is fully automated.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><strong>Log analysis only</strong> (less complete than full checkpoint state);
        <strong>LangSmith Trace</strong> (visual tracing but can't resume execution from a breakpoint);
        <strong>Unit-test mocking</strong> (fast but doesn't test real LLM behaviour).</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>Evaluation = Agent unit tests</strong>: <span class="mono">EvalItem</span> (input) → <span class="mono">Evaluator</span> (score) → <span class="mono">EvalResults</span> (results).</li>
    <li><span class="mono">RubricScore</span> supports multi-dimensional scoring; <span class="mono">raise_for_status()</span> for CI gating.</li>
    <li><strong>Time-travel</strong> via <span class="mono">WorkflowCheckpoint</span> saves/restores full state; completed steps use cache.</li>
    <li>Together they form a complete "detect → diagnose → fix → verify" loop.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Evaluation and replay share the same Agent/Workflow abstractions</strong> — no extra debugging tools
  or tracing systems needed. One <span class="mono">evaluate_agent()</span> call = batch Agent runs + auto scoring + CI integration.
  One <span class="mono">checkpoint_id</span> parameter = resume from any breakpoint, diagnosing issues step by step.
</div>
"""
