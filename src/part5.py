"""Content for Part 5 (build your own): lessons 16-20 — Chinese + English."""

# ---------------------------------------------------------------------------
L16_ZH = r"""
<p class="lead">MAF 的 ChatClient 是厂商无关的——但你总要选一个具体厂商来<strong>接入模型</strong>。
本课过一遍主要 provider 包，教你<strong>怎么从"import 到 run"走完全程</strong>。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  ChatClient 像<strong>万能插座</strong>；每个 provider 包是<strong>某国插头</strong>——
  你选 Foundry、OpenAI 还是 Anthropic 的插头，接上万能插座就能充电。
</div>

<h2>主要 Provider</h2>
<table class="t">
  <tr><th>Provider</th><th>包名</th><th>ChatClient 类</th></tr>
  <tr><td>Azure AI Foundry</td><td class="mono">agent-framework-foundry</td><td class="mono">FoundryChatClient</td></tr>
  <tr><td>OpenAI / Azure OpenAI</td><td class="mono">agent-framework（内置）</td><td class="mono">OpenAIChatClient</td></tr>
  <tr><td>Anthropic Claude</td><td class="mono">agent-framework-anthropic</td><td class="mono">AnthropicClient</td></tr>
  <tr><td>Ollama（本地）</td><td class="mono">agent-framework-ollama</td><td class="mono">OllamaChatClient</td></tr>
  <tr><td>AWS Bedrock</td><td class="mono">agent-framework-bedrock</td><td class="mono">BedrockChatClient</td></tr>
</table>
<p>全部用法一样：实例化 ChatClient → <span class="mono">client.as_agent(…)</span> → <span class="mono">agent.run(…)</span>。</p>

<h2>从 import 到 run：所有 provider 同一条路</h2>
<div class="flow">
  <div class="node"><div class="nt">import</div><div class="nd">选一个 provider 包</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">实例化</div><div class="nd">XxxChatClient(model=…)</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">.as_agent(…)</div><div class="nd">厂商无关</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">agent.run(…)</div><div class="nd">厂商无关</div></div>
</div>
<p>只有前两个框会随厂商变（包名 + ChatClient 类）；后两个框<strong>对所有 provider 完全一样</strong>。这就是“万能插座”：换插头不用换电器——把 OpenAI 换成 Anthropic，下游 Agent 代码一行不改。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> FoundryChatClient 配置 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">完整配置代码：
<pre class="code"><span class="kw">from</span> agent_framework_foundry <span class="kw">import</span> FoundryChatClient
<span class="kw">from</span> azure.identity <span class="kw">import</span> DefaultAzureCredential
<span class="kw">import</span> os

client = FoundryChatClient(
    project_endpoint=os.environ[<span class="st">"AZURE_AI_FOUNDRY_PROJECT_ENDPOINT"</span>],
    model=<span class="st">"gpt-4o"</span>,
    credential=DefaultAzureCredential()
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">Azure AI Foundry 统一管理模型、记忆、文件存储于一个端点下。企业客户通常已有 Foundry 项目，这让他们能直接复用现有基础设施和安全配置。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a"><span class="mono">FoundryChatClient</span> 只需三个参数：<span class="mono">project_endpoint</span>、<span class="mono">model</span>、<span class="mono">credential</span>。一次 import，三行配置，完成。底层走 Foundry 的统一 API。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">直接调用 Foundry REST API，或用 Azure SDK。MAF 的优势是把这些封装成 ChatClient 接口，切换厂商时不用改 Agent 代码。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> OpenAIChatClient 配置 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">OpenAI 或 Azure OpenAI 均可：
<pre class="code"><span class="kw">from</span> agent_framework.openai <span class="kw">import</span> OpenAIChatClient

<span class="cm"># OpenAI</span>
client = OpenAIChatClient(
    model=<span class="st">"gpt-4o"</span>,
    api_key=os.environ[<span class="st">"OPENAI_API_KEY"</span>]
)

<span class="cm"># Azure OpenAI</span>
client = OpenAIChatClient(
    model=<span class="st">"gpt-4o"</span>,
    base_url=<span class="st">"https://your-resource.openai.azure.com/"</span>,
    api_key=os.environ[<span class="st">"AZURE_OPENAI_KEY"</span>]
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">OpenAI 是最常见的起点。Azure OpenAI 则增加企业级安全（VNet、托管身份等）。许多团队从 OpenAI 开始原型，之后迁移到 Azure OpenAI。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">内置于核心包（无需额外安装）。通过 <span class="mono">base_url</span> 参数同时支持 OpenAI 和 Azure OpenAI。接口完全相同。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">直接用 <span class="mono">openai</span> SDK，或用 LiteLLM 代理。MAF 的优势是与其他厂商统一接口，切换时不用重写 Agent 逻辑。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> AnthropicClient 配置 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">先安装包，再配置：
<pre class="code"><span class="cm"># 安装</span>
pip install agent-framework-anthropic

<span class="cm"># 使用</span>
<span class="kw">from</span> agent_framework_anthropic <span class="kw">import</span> AnthropicClient

client = AnthropicClient(
    model=<span class="st">"claude-sonnet-4-5"</span>,
    api_key=os.environ[<span class="st">"ANTHROPIC_API_KEY"</span>]
)
<span class="cm"># 也可用 claude-haiku-3-5 等其他模型</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">Claude 模型在长上下文和仔细推理方面表现优异。许多团队需要厂商多样性来降低风险、比较质量或应对某一厂商的限制。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">独立包保持核心轻量。同样的 <span class="mono">as_agent()</span> → <span class="mono">run()</span> 模式。Agent 代码与 OpenAI 版本完全一样。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">直接用 <span class="mono">anthropic</span> SDK，或用 AWS Bedrock（也支持 Claude）。MAF 统一了接口，让切换变成一行代码的事。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> OllamaChatClient 配置 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">本地运行 Ollama，无需 API key：
<pre class="code"><span class="cm"># 1. 安装 Ollama（本地）并拉取模型</span>
ollama pull llama3.1

<span class="cm"># 2. Python 代码</span>
<span class="kw">from</span> agent_framework_ollama <span class="kw">import</span> OllamaChatClient

client = OllamaChatClient(
    model=<span class="st">"llama3.1"</span>,
    endpoint=<span class="st">"http://localhost:11434"</span>  <span class="cm"># 默认值</span>
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">本地模型 = 零 API 成本、数据不离开本地。适合开发、隐私敏感场景、或无法访问云端 API 的环境。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 对本地模型和云端模型一视同仁。同样的 Agent 代码可以在 Ollama 或 GPT-4o 上运行，只需切换 client 实例。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">vLLM、llama.cpp 服务器、LocalAI。Ollama 是最简单的开发选项，但 MAF 的抽象意味着你也可以写其他本地后端的 ChatClient。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> 切换厂商的实际演示 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">同一个 Agent 定义，只换 client 一行：
<pre class="code"><span class="cm"># 变体 1：OpenAI</span>
client = OpenAIChatClient(model=<span class="st">"gpt-4o"</span>, api_key=...)
agent = client.as_agent(
    name=<span class="st">"Assistant"</span>,
    instructions=<span class="st">"You are helpful."</span>,
    tools=[web_search]
)

<span class="cm"># 变体 2：Anthropic</span>
client = AnthropicClient(model=<span class="st">"claude-sonnet-4-5"</span>, api_key=...)
agent = client.as_agent(
    name=<span class="st">"Assistant"</span>,
    instructions=<span class="st">"You are helpful."</span>,
    tools=[web_search]
)

<span class="cm"># 变体 3：Ollama</span>
client = OllamaChatClient(model=<span class="st">"llama3.1"</span>)
agent = client.as_agent(
    name=<span class="st">"Assistant"</span>,
    instructions=<span class="st">"You are helpful."</span>,
    tools=[web_search]
)</pre>
<span class="cm"># Agent 定义（name、instructions、tools、middleware）完全相同！</span>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">厂商锁定成本高昂。能用一行代码切换是竞争优势：价格变动时切换、某厂商限流时切换、对比质量时切换。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的 <span class="mono">ChatClient</span> 抽象意味着 Agent 逻辑 100% 厂商无关。只有 client 实例化那一行需要改。工具、中间件、编排全部不变。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">LiteLLM 代理（增加网络跳转），LangChain 的 ChatModel（类似思路但更重）。MAF 是最干净的抽象。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>每个厂商一个 provider 包，提供一个 ChatClient 子类。</li>
    <li>统一用法：实例化 → <span class="mono">as_agent()</span> → <span class="mono">run()</span>。</li>
    <li>切换厂商只改 import 和实例化那两行。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>新增厂商不碰核心</strong>：provider 是独立包，通过懒加载接入。
  社区可以自己做新 provider 而不需要 fork 仓库。
</div>
"""

L16_EN = r"""
<p class="lead">MAF's ChatClient is vendor-agnostic — but you pick a concrete vendor to <strong>connect a model</strong>.
This lesson surveys the main provider packages and shows the <strong>import-to-run path</strong>.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  ChatClient is a <strong>universal socket</strong>; each provider package is a <strong>country-specific plug</strong> —
  pick the Foundry, OpenAI or Anthropic plug, snap it into the socket, and you're charging.
</div>

<h2>Key Providers</h2>
<table class="t">
  <tr><th>Provider</th><th>Package</th><th>ChatClient class</th></tr>
  <tr><td>Azure AI Foundry</td><td class="mono">agent-framework-foundry</td><td class="mono">FoundryChatClient</td></tr>
  <tr><td>OpenAI / Azure OpenAI</td><td class="mono">agent-framework (built-in)</td><td class="mono">OpenAIChatClient</td></tr>
  <tr><td>Anthropic Claude</td><td class="mono">agent-framework-anthropic</td><td class="mono">AnthropicClient</td></tr>
  <tr><td>Ollama (local)</td><td class="mono">agent-framework-ollama</td><td class="mono">OllamaChatClient</td></tr>
  <tr><td>AWS Bedrock</td><td class="mono">agent-framework-bedrock</td><td class="mono">BedrockChatClient</td></tr>
</table>
<p>Same pattern for all: instantiate ChatClient → <span class="mono">client.as_agent(…)</span> → <span class="mono">agent.run(…)</span>.</p>

<h2>From import to run: one path for every provider</h2>
<div class="flow">
  <div class="node"><div class="nt">import</div><div class="nd">pick a provider package</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">instantiate</div><div class="nd">XxxChatClient(model=…)</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">.as_agent(…)</div><div class="nd">vendor-agnostic</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">agent.run(…)</div><div class="nd">vendor-agnostic</div></div>
</div>
<p>Only the first two boxes change per vendor (package name + ChatClient class); the last two are <strong>identical for every provider</strong>. That's the &quot;universal socket&quot;: swap the plug, keep the appliance - switch OpenAI for Anthropic and the downstream Agent code doesn't change a line.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> FoundryChatClient configuration <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Full setup code:
<pre class="code"><span class="kw">from</span> agent_framework_foundry <span class="kw">import</span> FoundryChatClient
<span class="kw">from</span> azure.identity <span class="kw">import</span> DefaultAzureCredential
<span class="kw">import</span> os

client = FoundryChatClient(
    project_endpoint=os.environ[<span class="st">&quot;AZURE_AI_FOUNDRY_PROJECT_ENDPOINT&quot;</span>],
    model=<span class="st">&quot;gpt-4o&quot;</span>,
    credential=DefaultAzureCredential()
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Azure AI Foundry unifies model management, memory, and file storage under one endpoint. Enterprise customers already have Foundry projects, so they can reuse existing infrastructure and security configurations.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a"><span class="mono">FoundryChatClient</span> takes three parameters: <span class="mono">project_endpoint</span>, <span class="mono">model</span>, <span class="mono">credential</span>. One import, three params, done.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Direct REST calls to Foundry API, or Azure SDK directly. MAF wraps it into the ChatClient interface so you can swap providers.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> OpenAIChatClient configuration <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Works with both OpenAI and Azure OpenAI:
<pre class="code"><span class="kw">from</span> agent_framework.openai <span class="kw">import</span> OpenAIChatClient

<span class="cm"># OpenAI</span>
client = OpenAIChatClient(
    model=<span class="st">&quot;gpt-4o&quot;</span>,
    api_key=os.environ[<span class="st">&quot;OPENAI_API_KEY&quot;</span>]
)

<span class="cm"># Azure OpenAI</span>
client = OpenAIChatClient(
    model=<span class="st">&quot;gpt-4o&quot;</span>,
    base_url=<span class="st">&quot;https://your-resource.openai.azure.com/&quot;</span>,
    api_key=os.environ[<span class="st">&quot;AZURE_OPENAI_KEY&quot;</span>]
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">OpenAI is the most common starting point. Azure OpenAI adds enterprise security (VNet, managed identity). Many teams prototype with OpenAI, then migrate to Azure OpenAI.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Built into core package (no extra install). Works with both OpenAI and Azure OpenAI via <span class="mono">base_url</span>. Identical interface.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><span class="mono">openai</span> SDK directly, LiteLLM. MAF's advantage: same interface as all other providers.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> AnthropicClient configuration <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Install package, then configure:
<pre class="code"><span class="cm"># Install</span>
pip install agent-framework-anthropic

<span class="cm"># Use</span>
<span class="kw">from</span> agent_framework_anthropic <span class="kw">import</span> AnthropicClient

client = AnthropicClient(
    model=<span class="st">&quot;claude-sonnet-4-5&quot;</span>,
    api_key=os.environ[<span class="st">&quot;ANTHROPIC_API_KEY&quot;</span>]
)
<span class="cm"># Also: claude-haiku-3-5, etc.</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Claude models excel at long context and careful reasoning. Many teams want provider diversity to reduce risk, compare quality, or work around limits from one vendor.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">Separate package keeps core lightweight. Same <span class="mono">as_agent()</span> → <span class="mono">run()</span> pattern. Agent code identical to OpenAI version.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a"><span class="mono">anthropic</span> SDK directly, AWS Bedrock (which also supports Claude). MAF unifies the interface.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> OllamaChatClient configuration <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Run Ollama locally, no API key needed:
<pre class="code"><span class="cm"># 1. Install Ollama (locally) and pull model</span>
ollama pull llama3.1

<span class="cm"># 2. Python code</span>
<span class="kw">from</span> agent_framework_ollama <span class="kw">import</span> OllamaChatClient

client = OllamaChatClient(
    model=<span class="st">&quot;llama3.1&quot;</span>,
    endpoint=<span class="st">&quot;http://localhost:11434&quot;</span>  <span class="cm"># default</span>
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Local models = no API costs, no data leaving your machine. Great for development and privacy-sensitive use cases.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF treats local models identically to cloud ones. Same agent code works with Ollama or GPT-4o, just swap the client.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">vLLM, llama.cpp server, LocalAI. Ollama is simplest for development, but MAF's abstraction means you can write other local backend ChatClients.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> Switching providers demo <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Same Agent definition, only swap the client line:
<pre class="code"><span class="cm"># Variant 1: OpenAI</span>
client = OpenAIChatClient(model=<span class="st">&quot;gpt-4o&quot;</span>, api_key=...)
agent = client.as_agent(
    name=<span class="st">&quot;Assistant&quot;</span>,
    instructions=<span class="st">&quot;You are helpful.&quot;</span>,
    tools=[web_search]
)

<span class="cm"># Variant 2: Anthropic</span>
client = AnthropicClient(model=<span class="st">&quot;claude-sonnet-4-5&quot;</span>, api_key=...)
agent = client.as_agent(
    name=<span class="st">&quot;Assistant&quot;</span>,
    instructions=<span class="st">&quot;You are helpful.&quot;</span>,
    tools=[web_search]
)

<span class="cm"># Variant 3: Ollama</span>
client = OllamaChatClient(model=<span class="st">&quot;llama3.1&quot;</span>)
agent = client.as_agent(
    name=<span class="st">&quot;Assistant&quot;</span>,
    instructions=<span class="st">&quot;You are helpful.&quot;</span>,
    tools=[web_search]
)</pre>
<span class="cm"># Agent definition (name, instructions, tools, middleware) identical!</span>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Vendor lock-in is expensive. Being able to switch with one line change is a competitive advantage: switch when prices change, when one vendor rate-limits you, or to compare quality.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's <span class="mono">ChatClient</span> abstraction means agent logic is 100% provider-independent. Only the client instantiation changes. Tools, middleware, orchestration all stay the same.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">LiteLLM proxy (adds a network hop), LangChain's ChatModel (similar idea but heavier). MAF is the cleanest abstraction.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>One provider package per vendor, each supplying a ChatClient subclass.</li>
    <li>Unified pattern: instantiate → <span class="mono">as_agent()</span> → <span class="mono">run()</span>.</li>
    <li>Switching vendors changes only the import and instantiation lines.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Adding a vendor never touches core</strong>: providers are separate packages, wired in via lazy loading.
  The community can build new providers without forking the repo.
</div>
"""

# ---------------------------------------------------------------------------
L17_ZH = r"""
<p class="lead">不想写代码？用 <strong>YAML</strong> 定义一个 Agent——名字、指令、工具、模型全写在配置文件里。</p>

<div class="card analogy">
  <div class="tag">📝 生活类比</div>
  声明式 Agent 像<strong>简历</strong>：你把名字、技能、工作经验写好，HR（框架）照着简历帮你入职上岗。
</div>

<h2>一个 YAML 示例</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">my_agent.yaml</span></div>
<pre>name: WeatherBot
instructions: You help with weather queries.
model: gpt-4o
tools:
  - get_weather</pre>
</div>
<p>框架的 <span class="mono">declarative</span> 包读这个 YAML，自动构造出 <span class="mono">Agent</span> 实例。
适合快速原型和版本控制。</p>

<h2>从 YAML 到运行的一条龙</h2>
<div class="flow">
  <div class="node"><div class="nt">my_agent.yaml</div><div class="nd">name / instructions / tools</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">AgentFactory</div><div class="nd">create_agent_from_yaml_path</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Agent 实例</div><div class="nd">和手写的完全一样</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">agent.run(…)</div><div class="nd">照常调用</div></div>
</div>
<p>关键洞察：YAML 只是<strong>另一种构造方式</strong>。<span class="mono">AgentFactory</span> 解析完配置吐出的，和你用 <span class="mono">Agent(client=…, tools=…)</span> 手写出来的<strong>是同一类对象</strong>——所以下游的 <span class="mono">run()</span>、工具、中间件全都照旧。配置与代码<strong>同构</strong>，你才能在两种风格间自由切换。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 完整 YAML schema <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">支持的所有字段：
<pre class="code">name: MyAgent
instructions: You are a helpful assistant.
model: gpt-4o
description: Optional agent description

tools:
  - tool_name_1
  - tool_name_2

middleware:
  - LoggingMiddleware
  - RetryMiddleware

context_providers:
  - provider_name</pre>
每个字段说明：<span class="mono">name</span>（Agent 名称）、<span class="mono">instructions</span>（系统提示）、<span class="mono">model</span>（模型名）、<span class="mono">tools</span>（工具列表）、<span class="mono">middleware</span>（中间件列表）、<span class="mono">context_providers</span>（上下文提供者）、<span class="mono">description</span>（可选描述）。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">不知道完整 schema，用户会猜测字段名，浪费时间调试 YAML 拼写错误。明确的 schema 让配置可预测。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的 declarative 包会验证 YAML 是否符合已知 schema。未知字段会抛出清晰的错误，而不是悄悄失败。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">JSON Schema 验证，Pydantic 模型配置。YAML 对人类友好，且在版本控制中 diff 友好。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 加载代码 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">从 YAML 加载到运行：
<pre class="code"><span class="kw">from</span> agent_framework.declarative <span class="kw">import</span> AgentFactory

agent = AgentFactory().create_agent_from_yaml_path(<span class="st">"my_agent.yaml"</span>)
result = <span class="kw">await</span> agent.run(<span class="st">"Hello"</span>)</pre>
仅几行代码。<span class="mono">AgentFactory.create_agent_from_yaml_path</span> 读取 YAML → 构造完整配置的 Agent 实例。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">如果加载复杂，声明式就失去吸引力。应该和"加载 → 运行"一样简单。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 让它成为一行代码：加载 YAML，得到完整配置的 Agent。declarative 包处理工具解析、模型连接等所有细节。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">Hydra（Facebook）、OmegaConf。MAF 的方法是为 Agent 量身定制的，而不是通用配置。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> YAML + 代码混合 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">YAML 定义框架，代码添加自定义工具：
<pre class="code"><span class="cm"># 1. 在 Python 中定义工具</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> tool

<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">my_custom_tool</span>(query: str) -> str:
    <span class="st">&quot;&quot;&quot;My custom logic&quot;&quot;&quot;</span>
    <span class="kw">return</span> f<span class="st">&quot;Result for {query}&quot;</span>

<span class="cm"># 2. YAML 引用工具名称</span>
<span class="cm"># my_agent.yaml:</span>
<span class="cm">#   tools:</span>
<span class="cm">#     - my_custom_tool</span>

<span class="cm"># 3. 通过 bindings 把 Python 工具按名称注入</span>
agent = AgentFactory(bindings={<span class="st">"my_custom_tool"</span>: my_custom_tool}).create_agent_from_yaml_path(<span class="st">"my_agent.yaml"</span>)</pre>
工作流：在 Python 中定义工具 → 在 YAML 中按名称引用 → 加载。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">真正的 Agent 需要无法在 YAML 中表达的自定义逻辑。混合模式让非开发人员拥有配置，开发人员拥有逻辑。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的工具注册表意味着 YAML 可以按名称引用 Python 函数。两全其美。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">全代码（失去非开发人员可访问性），全 YAML 带嵌入代码（安全风险）。混合是最佳平衡点。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 声明式工作流 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">工作流（SequentialBuilder、ConcurrentBuilder）能否在 YAML 中定义？
<pre class="code"><span class="cm"># 当前：单个 Agent 的声明式支持很好</span>
<span class="cm"># 工作流通常需要代码来处理复杂的路由逻辑</span>

<span class="cm"># 可能的未来 YAML（如果支持）：</span>
workflow:
  participants:
    - writer_agent
    - reviewer_agent
  orchestration: sequential</pre>
当前限制：工作流的复杂路由逻辑最好用代码表达。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">如果单个 Agent 可以声明式，团队也会想要声明式工作流。这是自然的下一步。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的声明式支持正在发展。目前最适合单个 Agent；工作流通常需要代码来处理复杂路由逻辑。这是一个活跃的开发领域。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">Temporal 工作流定义、AWS Step Functions（JSON）。声明式工作流是一个活跃的研究领域。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>YAML 定义 Agent：<span class="mono">name</span> / <span class="mono">instructions</span> / <span class="mono">model</span> / <span class="mono">tools</span>。</li>
    <li>用 <span class="mono">declarative</span> 包加载，自动构造 <span class="mono">Agent</span>。</li>
    <li>适合快速原型、版本控制、非开发者协作。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>"配置即 Agent"</strong>：改 YAML 就能调整行为，不用改代码、不用重编译。
  这降低了非开发者参与 Agent 设计的门槛。
</div>
"""

L17_EN = r"""
<p class="lead">Don't want to write code? Define an Agent in <strong>YAML</strong> — name, instructions, tools
and model all in a config file.</p>

<div class="card analogy">
  <div class="tag">📝 Analogy</div>
  A declarative Agent is like a <strong>résumé</strong>: you list name, skills and experience; HR (the framework)
  reads it and onboards the person.
</div>

<h2>A YAML example</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">my_agent.yaml</span></div>
<pre>name: WeatherBot
instructions: You help with weather queries.
model: gpt-4o
tools:
  - get_weather</pre>
</div>
<p>The <span class="mono">declarative</span> package reads this YAML and auto-constructs an <span class="mono">Agent</span>.
Great for rapid prototyping and version control.</p>

<h2>From YAML to running, end to end</h2>
<div class="flow">
  <div class="node"><div class="nt">my_agent.yaml</div><div class="nd">name / instructions / tools</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">AgentFactory</div><div class="nd">create_agent_from_yaml_path</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Agent instance</div><div class="nd">identical to hand-written</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">agent.run(…)</div><div class="nd">called as usual</div></div>
</div>
<p>Key insight: YAML is just <strong>another way to construct</strong>. What <span class="mono">AgentFactory</span> emits after parsing is <strong>the same kind of object</strong> you'd build by hand with <span class="mono">Agent(client=…, tools=…)</span> - so downstream <span class="mono">run()</span>, tools and middleware all work unchanged. Config and code are <strong>isomorphic</strong>, which is what lets you move freely between the two styles.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Complete YAML schema <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">All supported fields:
<pre class="code">name: MyAgent
instructions: You are a helpful assistant.
model: gpt-4o
description: Optional agent description

tools:
  - tool_name_1
  - tool_name_2

middleware:
  - LoggingMiddleware
  - RetryMiddleware

context_providers:
  - provider_name</pre>
Each field explained: <span class="mono">name</span> (agent name), <span class="mono">instructions</span> (system prompt), <span class="mono">model</span> (model name), <span class="mono">tools</span> (tool list), <span class="mono">middleware</span> (middleware list), <span class="mono">context_providers</span> (context providers), <span class="mono">description</span> (optional description).
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Without knowing the full schema, users guess at field names and waste time debugging YAML typos. An explicit schema makes configuration predictable.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's declarative package validates the YAML against a known schema. Unknown fields raise clear errors instead of silently failing.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">JSON Schema validation, Pydantic models for config. YAML is human-friendly and diff-friendly for version control.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Loading code <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Load from YAML to running:
<pre class="code"><span class="kw">from</span> agent_framework.declarative <span class="kw">import</span> AgentFactory

agent = AgentFactory().create_agent_from_yaml_path(<span class="st">&quot;my_agent.yaml&quot;</span>)
result = <span class="kw">await</span> agent.run(<span class="st">&quot;Hello&quot;</span>)</pre>
Just a few lines. <span class="mono">AgentFactory.create_agent_from_yaml_path</span> reads YAML → fully configured Agent instance.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">If loading is complex, declarative loses its appeal. It should be as easy as &quot;load → run&quot;.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF makes it a one-liner: load YAML, get a fully configured Agent. The declarative package handles tool resolution, model wiring, etc.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Hydra (Facebook), OmegaConf. MAF's approach is purpose-built for agents, not generic config.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> YAML + code hybrid <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">YAML defines skeleton, code adds custom tools:
<pre class="code"><span class="cm"># 1. Define tool in Python</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> tool

<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">my_custom_tool</span>(query: str) -> str:
    <span class="st">&quot;&quot;&quot;My custom logic&quot;&quot;&quot;</span>
    <span class="kw">return</span> f<span class="st">&quot;Result for {query}&quot;</span>

<span class="cm"># 2. YAML references tool by name</span>
<span class="cm"># my_agent.yaml:</span>
<span class="cm">#   tools:</span>
<span class="cm">#     - my_custom_tool</span>

<span class="cm"># 3. Inject Python tools by name via bindings</span>
agent = AgentFactory(bindings={<span class="st">&quot;my_custom_tool&quot;</span>: my_custom_tool}).create_agent_from_yaml_path(<span class="st">&quot;my_agent.yaml&quot;</span>)</pre>
Workflow: define tool in Python → reference by name in YAML → load.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Real agents need custom logic that can't be expressed in YAML. Hybrid lets non-devs own the config while devs own the logic.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's tool registry means YAML can reference Python functions by name. Best of both worlds.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Full code (loses non-dev accessibility), full YAML with embedded code (security risk). Hybrid is the sweet spot.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Declarative workflows <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Can workflows (SequentialBuilder, ConcurrentBuilder) be defined in YAML?
<pre class="code"><span class="cm"># Currently: declarative support is good for single agents</span>
<span class="cm"># Workflows typically need code for complex routing logic</span>

<span class="cm"># Possible future YAML (if supported):</span>
workflow:
  participants:
    - writer_agent
    - reviewer_agent
  orchestration: sequential</pre>
Current limitation: complex routing logic in workflows is best expressed in code.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">If single agents can be declarative, teams will want declarative workflows too. It's the natural next step.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's declarative support is evolving. Currently best for single agents; workflows typically need code for complex routing logic. This is an active area of development.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Temporal workflow definitions, AWS Step Functions (JSON). Declarative workflows are an active area of development.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>YAML defines an Agent: <span class="mono">name</span> / <span class="mono">instructions</span> / <span class="mono">model</span> / <span class="mono">tools</span>.</li>
    <li>Loaded by the <span class="mono">declarative</span> package; auto-constructs <span class="mono">Agent</span>.</li>
    <li>Good for prototyping, version control, non-developer collaboration.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>"Config is an Agent"</strong>: tweak YAML to change behavior, no code changes, no recompilation.
  This lowers the barrier for non-developers to participate in Agent design.
</div>
"""

# ---------------------------------------------------------------------------
L18_ZH = r"""
<p class="lead"><a href="11-middleware.html">第 11 课</a>讲了中间件<em>是什么</em>；本课教你<strong>写一个自己的</strong>——从零到能用。</p>

<div class="card analogy">
  <div class="tag">🧱 生活类比</div>
  写中间件像在流水线上<strong>加一道工序</strong>：你可以在产品进入下一站前做质检（日志），
  在出站后贴标签（计费），或者发现次品时退回重做（重试）——不改流水线本身。
</div>

<h2>实战：重试中间件</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">自定义 ChatMiddleware</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> ChatMiddleware, ChatContext

<span class="kw">class</span> <span class="fn">RetryChatMiddleware</span>(ChatMiddleware):
    <span class="kw">def</span> <span class="fn">__init__</span>(self, max_retries: int = <span class="nb">3</span>):
        self.max_retries = max_retries

    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        <span class="kw">for</span> attempt <span class="kw">in</span> <span class="fn">range</span>(self.max_retries):
            <span class="kw">try</span>:
                <span class="kw">await</span> call_next()
                <span class="kw">return</span>
            <span class="kw">except</span> Exception:
                <span class="kw">if</span> attempt == self.max_retries - <span class="nb">1</span>:
                    <span class="kw">raise</span></pre>
</div>
<p>挂到 Agent 上：<span class="inline">Agent(client=client, middleware=[RetryChatMiddleware(3)])</span>。</p>

<h2>请求在中间件里穿行（洋葱模型）</h2>
<div class="flow">
  <div class="node"><div class="nt">run()</div><div class="nd">发起请求</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Retry.before</div><div class="nd">call_next() 之前</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Logging.before</div><div class="nd">记录输入</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">真正的调用</div><div class="nd">LLM / 工具</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Logging.after</div><div class="nd">记录输出 / 耗时</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Retry.after</div><div class="nd">失败则重试</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">result</div><div class="nd">context.result</div></div>
</div>
<p><span class="mono">await call_next()</span> 是分界线：它<strong>之前</strong>的代码在请求“进站”时跑，<strong>之后</strong>的代码在响应“出站”时跑——所以同一个中间件能同时包住前后两端（洋葱皮）。列表里<strong>越靠前的中间件越在外层</strong>：最先进、最后出。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 完整的日志中间件 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">完整代码，带计时：
<pre class="code"><span class="kw">import</span> logging
<span class="kw">import</span> time
<span class="kw">from</span> agent_framework <span class="kw">import</span> ChatMiddleware, ChatContext

logger = logging.getLogger(__name__)

<span class="kw">class</span> <span class="fn">LoggingChatMiddleware</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        logger.info(f<span class="st">&quot;Input: {context.messages}&quot;</span>)
        start = time.monotonic()
        
        <span class="kw">await</span> call_next()
        
        duration = time.monotonic() - start
        logger.info(f<span class="st">&quot;Output: {context.result}&quot;</span>)
        logger.info(f<span class="st">&quot;Duration: {duration:.2f}s&quot;</span>)</pre>
约 15 行完整日志中间件。<span class="mono">call_next()</span> 前记输入，之后记输出和耗时。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">日志是第一常见中间件。没有它，调试生产 Agent 就是盲飞。看不到输入输出和耗时，无法定位问题。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的中间件模式让日志变得简单：用 before/after 逻辑包装 <span class="mono">call_next()</span>。访问 <span class="mono">context.messages</span> 获取输入，<span class="mono">context.result</span> 获取输出。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">基于装饰器的日志、OpenTelemetry 自动埋点。中间件是显式的且可组合的。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 审批中间件 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a"><span class="mono">ApprovalMiddleware</span> 在 <span class="mono">call_next()</span> 前检查条件：
<pre class="code"><span class="kw">class</span> <span class="fn">ApprovalMiddleware</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        user_input = context.messages[-<span class="nb">1</span>].content
        
        <span class="kw">if</span> <span class="st">&quot;publish&quot;</span> <span class="kw">in</span> user_input <span class="kw">or</span> <span class="st">&quot;delete&quot;</span> <span class="kw">in</span> user_input:
            <span class="cm"># 暂停，等待人工确认（与 HITL 机制集成）</span>
            approved = <span class="kw">await</span> request_human_approval(user_input)
            <span class="kw">if not</span> approved:
                <span class="kw">raise</span> Exception(<span class="st">&quot;Action not approved&quot;</span>)
        
        <span class="kw">await</span> call_next()</pre>
消息包含"publish"或"delete"时暂停，等人签字后再继续。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">自主 Agent 需要护栏。某些操作（发布、删除、付款）应该需要人工批准。没有审批，风险不可控。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 中间件可以拦截任何调用。结合 <span class="mono">request_info</span> 进行异步人工输入，创建完整的审批流程。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">独立审批服务、基于 webhook 的审批。中间件保持在进程内且可组合。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Token 计费中间件 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">在 <span class="mono">await call_next()</span> 后读取用量：
<pre class="code"><span class="kw">class</span> <span class="fn">BillingMiddleware</span>(ChatMiddleware):
    <span class="kw">def</span> <span class="fn">__init__</span>(self):
        self.total_cost = <span class="nb">0.0</span>
    
    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        <span class="kw">await</span> call_next()
        
        usage = context.result.usage
        <span class="cm"># 假设价格：输入 $0.01/1k，输出 $0.03/1k</span>
        cost = (usage.input_tokens * <span class="nb">0.01</span> + 
                usage.output_tokens * <span class="nb">0.03</span>) / <span class="nb">1000</span>
        self.total_cost += cost
        logger.info(f<span class="st">&quot;Cost: ${cost:.4f}, Total: ${self.total_cost:.4f}&quot;</span>)</pre>
约 12 行实时成本追踪。读取 <span class="mono">context.result.usage</span>，计算成本，累加。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">LLM 成本可能爆炸。按请求成本追踪启用预算、告警和按用户计费。没有它，账单成谜。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 在每次调用后的 <span class="mono">context.result.usage</span> 上暴露 token 用量。中间件可以读取它而不修改响应。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">厂商控制台计费、外部代理（如 Helicone）。中间件提供实时、进程内追踪。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 中间件的错误处理 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">在 <span class="mono">await call_next()</span> 周围加 <span class="mono">try/except</span>：
<pre class="code"><span class="kw">class</span> <span class="fn">ErrorHandlingMiddleware</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        <span class="kw">try</span>:
            <span class="kw">await</span> call_next()
        <span class="kw">except</span> Exception <span class="kw">as</span> e:
            logger.error(f<span class="st">&quot;Call failed: {e}&quot;</span>)
            <span class="cm"># 可选：重试逻辑</span>
            <span class="cm"># 可选：返回后备响应</span>
            <span class="cm"># 或重新抛出</span>
            <span class="kw">raise</span></pre>
失败时：记录错误、可选重试、可选后备响应。模式：捕获异常，记录后重新抛出。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">LLM 调用会失败（速率限制、超时、错误响应）。没有错误处理中间件，失败会让整个 Agent 崩溃。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的管道自然传播异常。中间件可以在任何层捕获、记录、重试或转换错误。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">熔断器库（tenacity）、全局错误处理器。中间件是按层的且可组合的。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>继承 <span class="mono">*Middleware</span>，实现 <span class="mono">process(self, context, call_next)</span>。</li>
    <li><span class="mono">await call_next()</span> 无参；结果在 <span class="mono">context.result</span>。</li>
    <li>用 <span class="mono">Agent(client=client, middleware=[…])</span> 挂载——同一个列表里可混放 Chat / Function / Agent 三类，框架按基类自动分流。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  中间件是<strong>组合式的</strong>：重试、日志、审批各自独立实现，按需拼装，互不干扰。
</div>
"""

L18_EN = r"""
<p class="lead"><a href="11-middleware.html">Lesson 11</a> explained what middleware <em>is</em>; this lesson teaches you to
<strong>write your own</strong> — from scratch to working.</p>

<div class="card analogy">
  <div class="tag">🧱 Analogy</div>
  Writing middleware is like adding a <strong>station to an assembly line</strong>: you can inspect products
  before the next station (logging), stamp labels after (billing), or send defects back for rework (retry)
  — without modifying the line itself.
</div>

<h2>Hands-on: retry middleware</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">custom ChatMiddleware</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> ChatMiddleware, ChatContext

<span class="kw">class</span> <span class="fn">RetryChatMiddleware</span>(ChatMiddleware):
    <span class="kw">def</span> <span class="fn">__init__</span>(self, max_retries: int = <span class="nb">3</span>):
        self.max_retries = max_retries

    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        <span class="kw">for</span> attempt <span class="kw">in</span> <span class="fn">range</span>(self.max_retries):
            <span class="kw">try</span>:
                <span class="kw">await</span> call_next()
                <span class="kw">return</span>
            <span class="kw">except</span> Exception:
                <span class="kw">if</span> attempt == self.max_retries - <span class="nb">1</span>:
                    <span class="kw">raise</span></pre>
</div>
<p>Attach to an Agent: <span class="inline">Agent(client=client, middleware=[RetryChatMiddleware(3)])</span>.</p>

<h2>A request travels through the middleware (onion model)</h2>
<div class="flow">
  <div class="node"><div class="nt">run()</div><div class="nd">request starts</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Retry.before</div><div class="nd">before call_next()</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Logging.before</div><div class="nd">log input</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">the real call</div><div class="nd">LLM / tool</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Logging.after</div><div class="nd">log output / timing</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Retry.after</div><div class="nd">retry on failure</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">result</div><div class="nd">context.result</div></div>
</div>
<p><span class="mono">await call_next()</span> is the dividing line: code <strong>before</strong> it runs as the request goes &quot;in&quot;, code <strong>after</strong> it runs as the response comes &quot;out&quot; - so one middleware wraps both ends (the onion skin). <strong>Earlier middleware in the list sits further outside</strong>: first in, last out.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Complete logging middleware <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Full code with timing:
<pre class="code"><span class="kw">import</span> logging
<span class="kw">import</span> time
<span class="kw">from</span> agent_framework <span class="kw">import</span> ChatMiddleware, ChatContext

logger = logging.getLogger(__name__)

<span class="kw">class</span> <span class="fn">LoggingChatMiddleware</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        logger.info(f<span class="st">&quot;Input: {context.messages}&quot;</span>)
        start = time.monotonic()
        
        <span class="kw">await</span> call_next()
        
        duration = time.monotonic() - start
        logger.info(f<span class="st">&quot;Output: {context.result}&quot;</span>)
        logger.info(f<span class="st">&quot;Duration: {duration:.2f}s&quot;</span>)</pre>
~15 lines for complete logging middleware. Log input before <span class="mono">call_next()</span>, output and duration after.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Logging is the #1 most common middleware. Without it, debugging production agents is blind. Can't see inputs, outputs, or timing means can't diagnose issues.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's middleware pattern makes logging trivial: wrap <span class="mono">call_next()</span> with before/after logic. Access <span class="mono">context.messages</span> for input, <span class="mono">context.result</span> for output.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Decorator-based logging, OTel auto-instrumentation. Middleware is explicit and composable.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Approval middleware <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a"><span class="mono">ApprovalMiddleware</span> checks condition before <span class="mono">call_next()</span>:
<pre class="code"><span class="kw">class</span> <span class="fn">ApprovalMiddleware</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        user_input = context.messages[-<span class="nb">1</span>].content
        
        <span class="kw">if</span> <span class="st">&quot;publish&quot;</span> <span class="kw">in</span> user_input <span class="kw">or</span> <span class="st">&quot;delete&quot;</span> <span class="kw">in</span> user_input:
            <span class="cm"># Pause, wait for human confirmation (integrate with HITL)</span>
            approved = <span class="kw">await</span> request_human_approval(user_input)
            <span class="kw">if not</span> approved:
                <span class="kw">raise</span> Exception(<span class="st">&quot;Action not approved&quot;</span>)
        
        <span class="kw">await</span> call_next()</pre>
If message contains &quot;publish&quot; or &quot;delete&quot;, pause and wait for human signature before continuing.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Autonomous agents need guardrails. Certain actions (publish, delete, pay) should require human approval. Without approval, risk is uncontrolled.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF middleware can intercept any call. Combined with <span class="mono">request_info</span> for async human input, it creates a complete approval flow.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Separate approval service, webhook-based approval. Middleware keeps it in-process and composable.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Token billing middleware <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">After <span class="mono">await call_next()</span>, read usage:
<pre class="code"><span class="kw">class</span> <span class="fn">BillingMiddleware</span>(ChatMiddleware):
    <span class="kw">def</span> <span class="fn">__init__</span>(self):
        self.total_cost = <span class="nb">0.0</span>
    
    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        <span class="kw">await</span> call_next()
        
        usage = context.result.usage
        <span class="cm"># Assume prices: input $0.01/1k, output $0.03/1k</span>
        cost = (usage.input_tokens * <span class="nb">0.01</span> + 
                usage.output_tokens * <span class="nb">0.03</span>) / <span class="nb">1000</span>
        self.total_cost += cost
        logger.info(f<span class="st">&quot;Cost: ${cost:.4f}, Total: ${self.total_cost:.4f}&quot;</span>)</pre>
~12 lines for real-time cost tracking. Read <span class="mono">context.result.usage</span>, calculate cost, accumulate.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">LLM costs can explode. Per-request cost tracking enables budgets, alerts, and per-user billing. Without it, bills are a mystery.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF exposes token usage on <span class="mono">context.result.usage</span> after each call. Middleware can read it without modifying the response.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Provider dashboard billing, external proxy (e.g., Helicone). Middleware gives real-time, in-process tracking.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Middleware error handling <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a"><span class="mono">try/except</span> around <span class="mono">await call_next()</span>:
<pre class="code"><span class="kw">class</span> <span class="fn">ErrorHandlingMiddleware</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, context: ChatContext, call_next):
        <span class="kw">try</span>:
            <span class="kw">await</span> call_next()
        <span class="kw">except</span> Exception <span class="kw">as</span> e:
            logger.error(f<span class="st">&quot;Call failed: {e}&quot;</span>)
            <span class="cm"># Optional: retry logic</span>
            <span class="cm"># Optional: return fallback response</span>
            <span class="cm"># Or re-raise</span>
            <span class="kw">raise</span></pre>
On failure: log error, optionally retry, optionally return fallback. Pattern: catch exception, log, then re-raise.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">LLM calls fail (rate limits, timeouts, bad responses). Without error handling middleware, failures crash the entire agent.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's pipeline propagates exceptions naturally. Middleware can catch, log, retry, or transform errors at any layer.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Circuit breaker libraries (tenacity), global error handlers. Middleware is per-layer and composable.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Subclass <span class="mono">*Middleware</span>; implement <span class="mono">process(self, context, call_next)</span>.</li>
    <li><span class="mono">await call_next()</span> takes no args; result is on <span class="mono">context.result</span>.</li>
    <li>Attach via <span class="mono">Agent(client=client, middleware=[…])</span> - one list can mix Chat / Function / Agent middleware; the framework routes each by its base class.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  Middleware is <strong>compositional</strong>: retries, logging, approvals — each implemented independently,
  assembled as needed, no interference.
</div>
"""

# ---------------------------------------------------------------------------
L19_ZH = r"""
<p class="lead">生产环境需要：<strong>跑到一半能存盘</strong>（检查点）、<strong>关键操作人工审批</strong>（人在环）、
<strong>挂了能续跑</strong>（持久化）。MAF 把这三件事做成一等公民。</p>

<div class="card analogy">
  <div class="tag">💾 生活类比</div>
  检查点像<strong>游戏存档</strong>：进度存下来，挂了从存档恢复。
  人在环像<strong>审批流</strong>：到关键节点暂停，等人签字再继续。
  DurableTask 像<strong>云存档</strong>：存档不在本地，搬到另一台机器也能续玩。
</div>

<h2>检查点（Checkpoint）</h2>
<p>Workflow 在每个 superstep 边界自动存档。默认用 <span class="mono">InMemoryCheckpointStorage</span>；
生产换成持久化存储（如本地 <span class="mono">FileCheckpointStorage</span> 或云端 <span class="mono">CosmosCheckpointStorage</span>）。崩溃后重启，从最近存档恢复。</p>

<h2>人在环（HITL）</h2>
<p>工具可设置 <span class="mono">approval_mode="always_require"</span>，执行前暂停等人确认。
工作流层面也有 <span class="mono">request_info</span> 机制：节点暂停、发问、等回答再继续。</p>

<h2>一条带存档与暂停的时间线</h2>
<div class="flow">
  <div class="node"><div class="nt">superstep 1</div><div class="nd">Writer 跑完</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">💾 存档</div><div class="nd">superstep 边界</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">⏸ 人在环</div><div class="nd">approval / request_info</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">superstep 2</div><div class="nd">Reviewer 跑</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">💥 崩溃</div><div class="nd">进程挂了</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">↺ 续跑</div><div class="nd">从最近存档恢复</div></div>
</div>
<p>三件事各管一段：<strong>检查点</strong>在每个 superstep 边界自动存档；<strong>人在环</strong>在关键节点把流程<em>暂停</em>等人；<strong>持久化后端</strong>（File / Cosmos）决定存档放哪、崩溃后还能不能找回。注意 <strong>Redis 包是给上下文 / 历史记忆用的，不是工作流检查点</strong>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> InMemoryCheckpointStorage 示例 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">设置代码：
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> InMemoryCheckpointStorage
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder

storage = InMemoryCheckpointStorage()
workflow = SequentialBuilder(
    participants=[agent1, agent2],
    checkpoint_storage=storage
).build()</pre>
保存内容：Agent 状态、消息历史、当前步骤。适合开发，不适合生产。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">没有检查点，10 步工作流在第 5 步崩溃意味着从第 1 步重新开始。浪费时间和 LLM token。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 在 superstep 边界自动保存。<span class="mono">InMemoryCheckpointStorage</span> 零配置，适合开发。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">手动状态序列化、数据库快照。MAF 的检查点 API 是自动且透明的。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 人在环完整流程 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a"><span class="mono">request_info</span> 机制：
<pre class="code"><span class="cm"># 工作流层面：节点暂停等待人工输入</span>
answer = <span class="kw">await</span> request_info(<span class="st">&quot;Should I proceed?&quot;</span>)
<span class="kw">if</span> answer == <span class="st">&quot;yes&quot;</span>:
    <span class="cm"># 继续</span>
    ...

<span class="cm"># 工具层面：审批模式</span>
<span class="nb">@tool</span>(approval_mode=<span class="st">&quot;always_require&quot;</span>)
<span class="kw">def</span> <span class="fn">publish_article</span>(content: str):
    <span class="st">&quot;&quot;&quot;Publish article (requires approval)&quot;&quot;&quot;</span>
    ...</pre>
两个层级：工具级（<span class="mono">approval_mode</span>）和工作流级（<span class="mono">request_info</span>）。都会暂停执行并等待人工输入。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">完全自主的 Agent 对于高风险任务很危险。HITL 在关键决策点增加安全网。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 在两个层级支持 HITL：工具级（approval_mode）和工作流级（request_info）。两者都会暂停执行并等待人工输入。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">外部审批队列（Slack 机器人、电子邮件）、基于轮询的检查。MAF 的 HITL 内置于执行模型中。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> DurableTask 配置 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">安装和设置：
<pre class="code">pip install agent-framework-durabletask

<span class="cm"># 与 Azure Functions 集成</span>
<span class="cm"># 查看 packages/durabletask 了解配置详情</span></pre>
持久性保证：状态在进程重启后存活，支持长时间等待（数小时/数天）。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">内存检查点随进程消亡。生产需要在重启、部署和基础设施故障后存活的状态。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的 DurableTask 包利用久经考验的 Durable Task Framework。与 Azure Functions 配对实现无服务器、自动扩展部署。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">Temporal、AWS Step Functions、Prefect。DurableTask 与 Azure 生态系统原生集成。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> File / Cosmos 持久化存储 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">从 <span class="mono">InMemoryCheckpointStorage</span> 切换到 Cosmos（或本地 <span class="mono">FileCheckpointStorage</span>）：
<pre class="code"><span class="cm"># 安装包（云端分布式后端）</span>
pip install agent-framework-azure-cosmos

<span class="cm"># 改一行配置：换成持久化后端</span>
<span class="kw">from</span> agent_framework_azure_cosmos <span class="kw">import</span> CosmosCheckpointStorage
storage = CosmosCheckpointStorage(
    endpoint=<span class="st">&quot;https://...&quot;</span>,
    database_name=<span class="st">&quot;agents&quot;</span>,
    container_name=<span class="st">&quot;checkpoints&quot;</span>,
    credential=<span class="st">&quot;...&quot;</span>,
)

<span class="cm"># 工作流构建保持不变</span>
workflow = SequentialBuilder(
    participants=[agent1, agent2],
    checkpoint_storage=storage
).build()</pre>
切换后端只改一行。所有检查点 API 保持不变。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">内存存储快但易失。<span class="mono">FileCheckpointStorage</span> 提供零依赖的本地持久化；<span class="mono">CosmosCheckpointStorage</span> 提供全球分布 + 强一致性。（Redis 包提供的是上下文 / 历史记忆，不是工作流检查点。）</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的存储抽象意味着切换后端只需改一行。所有检查点 API 保持不变。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">PostgreSQL、DynamoDB、S3。检查点方面，MAF 核心自带 File、<span class="mono">agent-framework-azure-cosmos</span> 提供 Cosmos；Redis 包走的是上下文 / 历史记忆这条轴，社区可再补其他后端。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li><strong>检查点</strong>：Workflow superstep 自动存档，崩溃可恢复。</li>
    <li><strong>人在环</strong>：工具 <span class="mono">approval_mode</span> + 工作流 <span class="mono">request_info</span>。</li>
    <li><strong>持久化</strong>：DurableTask 包让状态存到外部，支持跨进程恢复。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>生产能力不是插件，是框架的一部分</strong>：检查点、审批、持久化都在核心 API 里，
  而不是你自己拼第三方库。
</div>
"""

L19_EN = r"""
<p class="lead">Production needs: <strong>save progress mid-run</strong> (checkpoints), <strong>human approval at
critical steps</strong> (HITL), <strong>resume after crashes</strong> (durability). MAF makes all three first-class.</p>

<div class="card analogy">
  <div class="tag">💾 Analogy</div>
  Checkpoints are <strong>game saves</strong>: save progress, crash, reload from save.
  HITL is an <strong>approval workflow</strong>: pause at a critical node, wait for a signature.
  DurableTask is <strong>cloud saves</strong>: saves aren't local — move to another machine and keep playing.
</div>

<h2>Checkpoints</h2>
<p>Workflows auto-save at each superstep boundary. Default: <span class="mono">InMemoryCheckpointStorage</span>;
swap to persistent storage (local <span class="mono">FileCheckpointStorage</span> or cloud <span class="mono">CosmosCheckpointStorage</span>) for production. After a crash, restart and resume from the latest save.</p>

<h2>Human-in-the-Loop (HITL)</h2>
<p>Tools can set <span class="mono">approval_mode="always_require"</span> to pause for human confirmation.
At the workflow level, <span class="mono">request_info</span> lets a node pause, ask a question, and wait for a reply.</p>

<h2>A timeline with saves and pauses</h2>
<div class="flow">
  <div class="node"><div class="nt">superstep 1</div><div class="nd">Writer finishes</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">💾 save</div><div class="nd">superstep boundary</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">⏸ HITL</div><div class="nd">approval / request_info</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">superstep 2</div><div class="nd">Reviewer runs</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">💥 crash</div><div class="nd">process dies</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">↺ resume</div><div class="nd">from latest save</div></div>
</div>
<p>Each concern owns a slice: <strong>checkpointing</strong> auto-saves at every superstep boundary; <strong>HITL</strong> <em>pauses</em> the flow at key nodes to wait for a human; the <strong>persistent backend</strong> (File / Cosmos) decides where saves live and whether you can recover after a crash. Note that <strong>the Redis package is for context / history memory, not workflow checkpoints</strong>.</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> InMemoryCheckpointStorage example <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Setup code:
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> InMemoryCheckpointStorage
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder

storage = InMemoryCheckpointStorage()
workflow = SequentialBuilder(
    participants=[agent1, agent2],
    checkpoint_storage=storage
).build()</pre>
What gets saved: agent state, message history, current step. Good for development, not for production.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Without checkpoints, a crash in step 5 of a 10-step workflow means restarting from step 1. Wasted time and LLM tokens.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF auto-saves at superstep boundaries. <span class="mono">InMemoryCheckpointStorage</span> is zero-config for development.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Manual state serialization, database snapshots. MAF's checkpoint API is automatic and transparent.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Complete HITL flow <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a"><span class="mono">request_info</span> mechanism:
<pre class="code"><span class="cm"># Workflow level: node pauses, waits for human input</span>
answer = <span class="kw">await</span> request_info(<span class="st">&quot;Should I proceed?&quot;</span>)
<span class="kw">if</span> answer == <span class="st">&quot;yes&quot;</span>:
    <span class="cm"># continue</span>
    ...

<span class="cm"># Tool level: approval mode</span>
<span class="nb">@tool</span>(approval_mode=<span class="st">&quot;always_require&quot;</span>)
<span class="kw">def</span> <span class="fn">publish_article</span>(content: str):
    <span class="st">&quot;&quot;&quot;Publish article (requires approval)&quot;&quot;&quot;</span>
    ...</pre>
Two levels: tool-level (<span class="mono">approval_mode</span>) and workflow-level (<span class="mono">request_info</span>). Both pause execution and wait for human input.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Fully autonomous agents are dangerous for high-stakes tasks. HITL adds a safety net at critical decision points.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF supports HITL at two levels: tool-level (approval_mode) and workflow-level (request_info). Both pause execution and wait for human input.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">External approval queues (Slack bots, email), polling-based checks. MAF's HITL is built into the execution model.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> DurableTask configuration <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Install and setup:
<pre class="code">pip install agent-framework-durabletask

<span class="cm"># Integration with Azure Functions</span>
<span class="cm"># See packages/durabletask for configuration details</span></pre>
Durability guarantees: state survives process restarts, supports long waits (hours/days).
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">In-memory checkpoints die with the process. Production needs state that survives restarts, deployments, and infrastructure failures.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's DurableTask package leverages the battle-tested Durable Task Framework. Pair with Azure Functions for serverless, auto-scaling deployment.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Temporal, AWS Step Functions, Prefect. DurableTask integrates natively with Azure ecosystem.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> File / Cosmos persistent storage <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Switch from <span class="mono">InMemoryCheckpointStorage</span> to Cosmos (or local <span class="mono">FileCheckpointStorage</span>):
<pre class="code"><span class="cm"># Install package (cloud distributed backend)</span>
pip install agent-framework-azure-cosmos

<span class="cm"># Change one line of config: use a persistent backend</span>
<span class="kw">from</span> agent_framework_azure_cosmos <span class="kw">import</span> CosmosCheckpointStorage
storage = CosmosCheckpointStorage(
    endpoint=<span class="st">&quot;https://...&quot;</span>,
    database_name=<span class="st">&quot;agents&quot;</span>,
    container_name=<span class="st">&quot;checkpoints&quot;</span>,
    credential=<span class="st">&quot;...&quot;</span>,
)

<span class="cm"># Workflow build stays the same</span>
workflow = SequentialBuilder(
    participants=[agent1, agent2],
    checkpoint_storage=storage
).build()</pre>
Switching backends is a one-line change. All checkpoint APIs stay the same.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">In-memory storage is fast but volatile. <span class="mono">FileCheckpointStorage</span> gives zero-dependency local persistence; <span class="mono">CosmosCheckpointStorage</span> gives global distribution + strong consistency. (The Redis package provides context / history memory, not workflow checkpoints.)</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's storage abstraction means switching backends is a one-line change. All checkpoint APIs stay the same.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">PostgreSQL, DynamoDB, S3. For checkpoints, MAF core ships File and <span class="mono">agent-framework-azure-cosmos</span> ships Cosmos; the Redis package serves the context / history memory axis. The community can add more backends.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>Checkpoints</strong>: auto-saved at Workflow supersteps; crash-recoverable.</li>
    <li><strong>HITL</strong>: tool <span class="mono">approval_mode</span> + workflow <span class="mono">request_info</span>.</li>
    <li><strong>Durability</strong>: DurableTask package persists state externally for cross-process resume.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Production features aren't plugins — they're part of the framework</strong>: checkpoints, approvals and
  durability are in the core API, not third-party libraries you glue on yourself.
</div>
"""

# ---------------------------------------------------------------------------
L20_ZH = r"""
<p class="lead">最后一课实战：把前面学的<strong>Agent + 工具 + 编排 + 检查点</strong>拼成一个
<strong>多 Agent 工作流</strong>。</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  这节课像<strong>拼乐高</strong>：前面每课教你认识一种零件（Agent、工具、编排、检查点），
  现在把它们拼成一辆完整的车——能跑、能转弯、能刹车。
</div>

<h2>场景：写作 → 审稿</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>创建两个 Agent</h4>
    <p><strong>Writer</strong>：根据提示写文章。<strong>Reviewer</strong>：审稿、提修改意见。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>用 SequentialBuilder 编排</h4>
    <p>Writer 写完 → Reviewer 审稿，串行。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>跑起来</h4>
    <p><span class="mono">workflow.run("Write about AI agents")</span>。</p></div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">端到端示例骨架</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder

writer = Agent(client=client, name=<span class="st">"Writer"</span>,
    instructions=<span class="st">"Write a short article on the given topic."</span>)
reviewer = Agent(client=client, name=<span class="st">"Reviewer"</span>,
    instructions=<span class="st">"Review the article. Suggest improvements."</span>)

workflow = SequentialBuilder(participants=[writer, reviewer]).build()
result = <span class="kw">await</span> workflow.run(<span class="st">"Write about AI agents"</span>)</pre>
</div>

<h2>这些零件是怎么拼起来的</h2>
<div class="flow">
  <div class="node"><div class="nt">Provider</div><div class="nd">OpenAIChatClient</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Writer</div><div class="nd">+ 工具 + 中间件</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Reviewer</div><div class="nd">审稿 Agent</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">SequentialBuilder</div><div class="nd">串成工作流</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">+ 检查点</div><div class="nd">checkpoint_storage</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">workflow.run</div><div class="nd">端到端跑通</div></div>
</div>
<p>每个箭头都对应你前面学过的一课：<strong>Provider</strong>（L16）接模型，<strong>工具 / 中间件</strong>（L06 / L18）增强单个 Agent，<strong>Builder</strong>（L12-13）把多个 Agent 编排起来，<strong>检查点</strong>（L19）让它能恢复。capstone 的价值就是看清这些零件如何<strong>正交组合</strong>——各自独立，又能拼在一起。</p>
<details class="accordion">
  <summary><span class="badge-num">1</span> 完整代码骨架（扩展版） <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">完整的 25-30 行可工作示例：
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent, tool
<span class="kw">from</span> agent_framework.openai <span class="kw">import</span> OpenAIChatClient
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder
<span class="kw">from</span> agent_framework <span class="kw">import</span> InMemoryCheckpointStorage

<span class="cm"># 工具</span>
<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">web_search</span>(query: str) -> str:
    <span class="st">&quot;&quot;&quot;搜索网络&quot;&quot;&quot;</span>
    <span class="kw">return</span> f<span class="st">&quot;Results for {query}&quot;</span>

<span class="cm"># 中间件</span>
<span class="kw">class</span> <span class="fn">LoggingMiddleware</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, context, call_next):
        logger.info(f<span class="st">&quot;Input: {context.messages}&quot;</span>)
        <span class="kw">await</span> call_next()
        logger.info(f<span class="st">&quot;Output: {context.result}&quot;</span>)

<span class="cm"># Agents</span>
client = OpenAIChatClient(model=<span class="st">&quot;gpt-4o&quot;</span>)
writer = client.as_agent(name=<span class="st">&quot;Writer&quot;</span>,
    instructions=<span class="st">&quot;Write articles&quot;</span>,
    tools=[web_search],
    middleware=[LoggingMiddleware()])

reviewer = client.as_agent(name=<span class="st">&quot;Reviewer&quot;</span>,
    instructions=<span class="st">&quot;Review and improve&quot;</span>)

<span class="cm"># 工作流</span>
storage = InMemoryCheckpointStorage()
workflow = SequentialBuilder(
    participants=[writer, reviewer],
    checkpoint_storage=storage
).build()

result = <span class="kw">await</span> workflow.run(<span class="st">&quot;Write about MAF&quot;</span>)</pre>
所有组件整合：Agent、工具、中间件、检查点、编排。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">看到所有组件一起工作能巩固理解。可复制粘贴的代码是最好的学习工具。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的可组合性意味着每个组件（Agent、工具、中间件、检查点、编排）都能干净地组合在一起。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">样板代码繁重的框架需要 100+ 行才能实现相同功能。MAF 保持在 30 行以内。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 加入 Concurrent 变体 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">用 Sequential 替换为：Writer + FactChecker 并行运行，然后 Reviewer 串行运行：
<pre class="code"><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> (
    SequentialBuilder, ConcurrentBuilder
)

<span class="cm"># 阶段 1：并行</span>
concurrent_stage = ConcurrentBuilder(
    participants=[writer, fact_checker]
).build()

<span class="cm"># 阶段 2：串行（等待并行阶段完成）</span>
workflow = SequentialBuilder(
    participants=[concurrent_stage, reviewer]
).build()

result = <span class="kw">await</span> workflow.run(<span class="st">&quot;Write about AI&quot;</span>)</pre>
Builder 可组合：混合并行和串行阶段。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">串行工作流在步骤独立时很慢。并行执行减少实际时间。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 的 ConcurrentBuilder + SequentialBuilder 自然组合。自由混合并行和串行阶段。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">手动 asyncio.gather()、线程池。MAF 的 builder 自动处理扇出/扇入。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 加入人在环 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">给 Reviewer 添加 <span class="mono">publish</span> 工具，带 <span class="mono">approval_mode="always_require"</span>：
<pre class="code"><span class="nb">@tool</span>(approval_mode=<span class="st">&quot;always_require&quot;</span>)
<span class="kw">def</span> <span class="fn">publish</span>(content: str):
    <span class="st">&quot;&quot;&quot;发布文章（需要审批）&quot;&quot;&quot;</span>
    <span class="cm"># 实际发布逻辑</span>
    <span class="kw">return</span> f<span class="st">&quot;Published: {content[:50]}...&quot;</span>

reviewer = client.as_agent(
    name=<span class="st">&quot;Reviewer&quot;</span>,
    instructions=<span class="st">&quot;Review and publish if good&quot;</span>,
    tools=[publish]  <span class="cm"># 发布前必须人工审批</span>
)</pre>
在文章发布前，必须有人批准。框架处理暂停、通知和恢复。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">自动发布而不审查有风险。发布步骤的 HITL 防止不良内容上线。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">工具定义上的一个参数（<span class="mono">approval_mode</span>）。框架处理暂停、通知和恢复。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">自定义 webhook 审批、外部审核 API。MAF 的方法是声明式且内置的。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 生产化清单 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">生产就绪检查清单：
<pre class="code"><span class="cm"># ✓ 添加 OpenTelemetry 追踪</span>
<span class="kw">from</span> agent_framework.observability <span class="kw">import</span> configure_otel_providers
configure_otel_providers()

<span class="cm"># ✓ 切换到持久化存储</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> FileCheckpointStorage
storage = FileCheckpointStorage(<span class="st">&quot;./checkpoints&quot;</span>)

<span class="cm"># ✓ 添加错误处理中间件</span>
middleware=[ErrorHandlingMiddleware(), RetryMiddleware()]

<span class="cm"># ✓ 设置 token 预算</span>
agent = client.as_agent(..., max_tokens=<span class="nb">10000</span>)

<span class="cm"># ✓ 添加速率限制</span>
<span class="cm"># ✓ 配置日志级别</span>
logging.basicConfig(level=logging.INFO)</pre>
从演示到生产的差距清单。
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">演示代码 ≠ 生产代码。知道差距可防止中断和成本超支。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 提供所有生产构建块：OTel 集成、持久化存储包、重试/日志/计费中间件。无需第三方胶水。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">平台特定解决方案（Azure Monitor、Datadog）。MAF 是云无关的；OTel 导出到任何后端。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>多 Agent 工作流 = 几个 Agent + 一个 Builder + <span class="mono">.build().run()</span>。</li>
    <li>工具、中间件、检查点、人在环——全部可以叠加进去。</li>
    <li>从"hello agent"到"生产级多 Agent"，代码增量很小。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>复杂度是增量的</strong>：单 Agent → 加工具 → 加编排 → 加检查点 → 加审批，每一步只增加几行代码。
  这就是"从原型到生产"的体验。
</div>
"""

L20_EN = r"""
<p class="lead">Capstone: assemble <strong>Agent + tools + orchestration + checkpoints</strong> from earlier lessons
into a <strong>multi-Agent workflow</strong>.</p>

<div class="card analogy">
  <div class="tag">🧩 Analogy</div>
  This lesson is like <strong>building with LEGO</strong>: earlier lessons taught you each brick type
  (Agent, tools, orchestration, checkpoints); now you snap them together into a complete car —
  one that drives, turns and brakes.
</div>

<h2>Scenario: write → review</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Create two Agents</h4>
    <p><strong>Writer</strong>: writes an article from a prompt. <strong>Reviewer</strong>: reviews it, suggests edits.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Orchestrate with SequentialBuilder</h4>
    <p>Writer finishes → Reviewer reviews, in sequence.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Run it</h4>
    <p><span class="mono">workflow.run("Write about AI agents")</span>.</p></div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">end-to-end skeleton</span></div>
<pre><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder

writer = Agent(client=client, name=<span class="st">"Writer"</span>,
    instructions=<span class="st">"Write a short article on the given topic."</span>)
reviewer = Agent(client=client, name=<span class="st">"Reviewer"</span>,
    instructions=<span class="st">"Review the article. Suggest improvements."</span>)

workflow = SequentialBuilder(participants=[writer, reviewer]).build()
result = <span class="kw">await</span> workflow.run(<span class="st">"Write about AI agents"</span>)</pre>
</div>

<h2>How the bricks snap together</h2>
<div class="flow">
  <div class="node"><div class="nt">Provider</div><div class="nd">OpenAIChatClient</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Writer</div><div class="nd">+ tools + middleware</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">Reviewer</div><div class="nd">review Agent</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">SequentialBuilder</div><div class="nd">chain into a workflow</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">+ checkpoint</div><div class="nd">checkpoint_storage</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">workflow.run</div><div class="nd">end to end</div></div>
</div>
<p>Every arrow maps to an earlier lesson: <strong>Provider</strong> (L16) supplies the model, <strong>tools / middleware</strong> (L06 / L18) enrich a single Agent, the <strong>Builder</strong> (L12-13) orchestrates multiple Agents, and <strong>checkpointing</strong> (L19) makes it recoverable. The capstone's value is seeing how these pieces <strong>compose orthogonally</strong> - each independent, yet snapping together.</p>
<details class="accordion">
  <summary><span class="badge-num">1</span> Extended code skeleton <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Full working example in ~25-30 lines:
<pre class="code"><span class="kw">from</span> agent_framework <span class="kw">import</span> Agent, tool
<span class="kw">from</span> agent_framework.openai <span class="kw">import</span> OpenAIChatClient
<span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> SequentialBuilder
<span class="kw">from</span> agent_framework <span class="kw">import</span> InMemoryCheckpointStorage

<span class="cm"># Tool</span>
<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">web_search</span>(query: str) -> str:
    <span class="st">&quot;&quot;&quot;Search the web&quot;&quot;&quot;</span>
    <span class="kw">return</span> f<span class="st">&quot;Results for {query}&quot;</span>

<span class="cm"># Middleware</span>
<span class="kw">class</span> <span class="fn">LoggingMiddleware</span>(ChatMiddleware):
    <span class="kw">async def</span> <span class="fn">process</span>(self, context, call_next):
        logger.info(f<span class="st">&quot;Input: {context.messages}&quot;</span>)
        <span class="kw">await</span> call_next()
        logger.info(f<span class="st">&quot;Output: {context.result}&quot;</span>)

<span class="cm"># Agents</span>
client = OpenAIChatClient(model=<span class="st">&quot;gpt-4o&quot;</span>)
writer = client.as_agent(name=<span class="st">&quot;Writer&quot;</span>,
    instructions=<span class="st">&quot;Write articles&quot;</span>,
    tools=[web_search],
    middleware=[LoggingMiddleware()])

reviewer = client.as_agent(name=<span class="st">&quot;Reviewer&quot;</span>,
    instructions=<span class="st">&quot;Review and improve&quot;</span>)

<span class="cm"># Workflow</span>
storage = InMemoryCheckpointStorage()
workflow = SequentialBuilder(
    participants=[writer, reviewer],
    checkpoint_storage=storage
).build()

result = <span class="kw">await</span> workflow.run(<span class="st">&quot;Write about MAF&quot;</span>)</pre>
All pieces together: agent, tool, middleware, checkpoint, orchestration.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Seeing all pieces together cements understanding. Copy-paste-able code is the best learning tool.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's composability means each piece (agent, tool, middleware, checkpoint, orchestration) snaps together cleanly.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Boilerplate-heavy frameworks need 100+ lines for the same. MAF keeps it under 30.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> Adding concurrency <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Replace Sequential with: Writer + FactChecker run in parallel, then Reviewer runs serially:
<pre class="code"><span class="kw">from</span> agent_framework.orchestrations <span class="kw">import</span> (
    SequentialBuilder, ConcurrentBuilder
)

<span class="cm"># Stage 1: concurrent</span>
concurrent_stage = ConcurrentBuilder(
    participants=[writer, fact_checker]
).build()

<span class="cm"># Stage 2: sequential (waits for concurrent stage)</span>
workflow = SequentialBuilder(
    participants=[concurrent_stage, reviewer]
).build()

result = <span class="kw">await</span> workflow.run(<span class="st">&quot;Write about AI&quot;</span>)</pre>
Builders compose: mix parallel and sequential stages.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Sequential workflows are slow when steps are independent. Parallel execution cuts wall-clock time.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF's ConcurrentBuilder + SequentialBuilder compose naturally. Mix parallel and sequential stages freely.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Manual asyncio.gather(), thread pools. MAF's builders handle fan-out/fan-in automatically.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Adding HITL <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Add a <span class="mono">publish</span> tool to Reviewer with <span class="mono">approval_mode="always_require"</span>:
<pre class="code"><span class="nb">@tool</span>(approval_mode=<span class="st">&quot;always_require&quot;</span>)
<span class="kw">def</span> <span class="fn">publish</span>(content: str):
    <span class="st">&quot;&quot;&quot;Publish article (requires approval)&quot;&quot;&quot;</span>
    <span class="cm"># actual publish logic</span>
    <span class="kw">return</span> f<span class="st">&quot;Published: {content[:50]}...&quot;</span>

reviewer = client.as_agent(
    name=<span class="st">&quot;Reviewer&quot;</span>,
    instructions=<span class="st">&quot;Review and publish if good&quot;</span>,
    tools=[publish]  <span class="cm"># must be human-approved before publish</span>
)</pre>
Before the article is published, a human must approve. Framework handles pausing, notifying, and resuming.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Auto-publishing without review is risky. HITL at the publish step prevents bad content from going live.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">One parameter (<span class="mono">approval_mode</span>) on the tool definition. The framework handles pausing, notifying, and resuming.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Custom webhook approval, external moderation API. MAF's approach is declarative and built-in.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Production checklist <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Production-ready checklist:
<pre class="code"><span class="cm"># ✓ Add OpenTelemetry tracing</span>
<span class="kw">from</span> agent_framework.observability <span class="kw">import</span> configure_otel_providers
configure_otel_providers()

<span class="cm"># ✓ Switch to persistent storage</span>
<span class="kw">from</span> agent_framework <span class="kw">import</span> FileCheckpointStorage
storage = FileCheckpointStorage(<span class="st">&quot;./checkpoints&quot;</span>)

<span class="cm"># ✓ Add error handling middleware</span>
middleware=[ErrorHandlingMiddleware(), RetryMiddleware()]

<span class="cm"># ✓ Set token budgets</span>
agent = client.as_agent(..., max_tokens=<span class="nb">10000</span>)

<span class="cm"># ✓ Add rate limiting</span>
<span class="cm"># ✓ Configure logging</span>
logging.basicConfig(level=logging.INFO)</pre>
Checklist of gaps from demo to production.
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Demo code ≠ production code. Knowing the gaps prevents outages and cost overruns.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF provides all production building blocks: OTel integration, persistent storage packages, middleware for retries/logging/billing. No third-party glue needed.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Platform-specific solutions (Azure Monitor, Datadog). MAF is cloud-agnostic; OTel exports to any backend.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Multi-Agent workflow = a few Agents + one Builder + <span class="mono">.build().run()</span>.</li>
    <li>Tools, middleware, checkpoints, HITL — all stackable.</li>
    <li>From "hello agent" to "production multi-Agent" with minimal code increase.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>Complexity is incremental</strong>: single Agent → add tools → add orchestration → add checkpoints → add
  approvals, each step adds only a few lines. That's the "prototype to production" experience.
</div>
"""
