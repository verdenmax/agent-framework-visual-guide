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
