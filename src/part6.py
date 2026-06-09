"""Content for Part 6 (bonus): lessons 21-22 — Chinese + English."""

# ---------------------------------------------------------------------------
L21_ZH = r"""
<p class="lead">Agent 框架不止 MAF 一个。本课横向对比四大框架，帮你建立<strong>全局坐标</strong>。</p>

<h2>四框架对比</h2>
<table class="t">
  <tr><th></th><th>MAF</th><th>LangGraph</th><th>AutoGen</th><th>Semantic Kernel</th></tr>
  <tr><td><strong>编排模型</strong></td><td>图（Workflow）+ 预置编排</td><td>图（StateGraph）</td><td>多 Agent 对话</td><td>Planner + 管道</td></tr>
  <tr><td><strong>语言</strong></td><td>Python + .NET</td><td>Python (+ JS)</td><td>Python + .NET</td><td>Python + .NET + Java</td></tr>
  <tr><td><strong>生产特性</strong></td><td>检查点 · HITL · OTel · DurableTask</td><td>检查点 · HITL · LangSmith</td><td>基础 logging</td><td>连接器 · 企业集成</td></tr>
  <tr><td><strong>定位</strong></td><td>原型到生产，SK + AutoGen 统一继任</td><td>图控制流 + 可控 Agent</td><td>多 Agent 研究/探索</td><td>企业 AI 编排</td></tr>
</table>

<div class="card analogy">
  <div class="tag">🗺️ 生活类比</div>
  <strong>MAF</strong> 像<strong>全能 SUV</strong>（城市通勤到越野都行），<strong>LangGraph</strong> 像<strong>手动挡跑车</strong>（精确控制），
  <strong>AutoGen</strong> 像<strong>实验越野车</strong>（探路利器），<strong>SK</strong> 像<strong>商务轿车</strong>（企业平稳）。
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> 我该选哪个？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">✅ 选择建议</div>
      <div class="a">要<strong>生产级 + 双语言 + 全功能</strong>：MAF。
        要<strong>最细粒度图控制</strong>：LangGraph。
        要<strong>多 Agent 对话实验</strong>：AutoGen（或 MAF 的 MagenticBuilder，它就源自 AutoGen）。
        已在<strong>微软企业生态</strong>里深度集成：SK 或 MAF（MAF 是 SK 的继任方向）。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>MAF = SK + AutoGen 合并演进，面向"原型到生产"。</li>
    <li>LangGraph 强在图控制流精度；AutoGen 强在多 Agent 对话探索。</li>
    <li>选框架看你的核心需求：语言、生产特性、控制粒度。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  MAF 把"图编排"和"多 Agent 对话"<strong>统一到同一个框架</strong>——你不用在 LangGraph 和 AutoGen 之间二选一。
</div>
"""

L21_EN = r"""
<p class="lead">MAF isn't the only agent framework. This lesson compares four major ones to give you
<strong>global coordinates</strong>.</p>

<h2>Four-framework comparison</h2>
<table class="t">
  <tr><th></th><th>MAF</th><th>LangGraph</th><th>AutoGen</th><th>Semantic Kernel</th></tr>
  <tr><td><strong>Orchestration</strong></td><td>Graph (Workflow) + prebuilt patterns</td><td>Graph (StateGraph)</td><td>Multi-agent chat</td><td>Planner + pipeline</td></tr>
  <tr><td><strong>Languages</strong></td><td>Python + .NET</td><td>Python (+ JS)</td><td>Python + .NET</td><td>Python + .NET + Java</td></tr>
  <tr><td><strong>Production</strong></td><td>Checkpoints · HITL · OTel · DurableTask</td><td>Checkpoints · HITL · LangSmith</td><td>Basic logging</td><td>Connectors · enterprise</td></tr>
  <tr><td><strong>Positioning</strong></td><td>Prototype-to-prod, SK + AutoGen successor</td><td>Graph control flow + controllable agents</td><td>Multi-agent research</td><td>Enterprise AI orchestration</td></tr>
</table>

<div class="card analogy">
  <div class="tag">🗺️ Analogy</div>
  <strong>MAF</strong> is a <strong>versatile SUV</strong> (city to off-road), <strong>LangGraph</strong> is a
  <strong>manual-shift sports car</strong> (precise control), <strong>AutoGen</strong> is an <strong>experimental
  off-roader</strong> (trail blazer), <strong>SK</strong> is a <strong>business sedan</strong> (enterprise smooth).
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> Which should I pick? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">✅ Guidelines</div>
      <div class="a"><strong>Production + dual-language + full features</strong>: MAF.
        <strong>Finest-grained graph control</strong>: LangGraph.
        <strong>Multi-agent chat experiments</strong>: AutoGen (or MAF's MagenticBuilder, which descends from AutoGen).
        <strong>Deep in the Microsoft enterprise ecosystem</strong>: SK or MAF (MAF is SK's successor direction).</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>MAF = SK + AutoGen merged, aimed at "prototype to production".</li>
    <li>LangGraph excels at graph control precision; AutoGen at multi-agent chat exploration.</li>
    <li>Pick by your core needs: language, production features, control granularity.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  MAF <strong>unifies graph orchestration and multi-agent chat in one framework</strong> — you don't have to choose
  between LangGraph and AutoGen.
</div>
"""

# ---------------------------------------------------------------------------
L22_ZH = r"""
<p class="lead">最后一课，缩放镜头：把 MAF 放进<strong>AI 全栈</strong>的坐标系里——
看看你现在在哪，隔壁层还有什么值得学。</p>

<h2>AI 全栈分层</h2>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">L7</span><span class="name">应用层</span></div>
    <div class="ld">你的产品 / UI / API 网关。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">L6</span><span class="name">Agent 编排</span></div>
    <div class="ld"><strong>← 你在这里</strong>（MAF / LangGraph / AutoGen）。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">L5</span><span class="name">模型 API / 推理</span></div>
    <div class="ld">OpenAI API · Azure AI · vLLM · llama.cpp · Ollama。</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">L4</span><span class="name">向量检索 / RAG</span></div>
    <div class="ld">Embeddings · pgvector · Qdrant · Azure AI Search。</div></div>
</div>

<h2>隔壁层学习地图</h2>
<table class="t">
  <tr><th>层</th><th>你可以学</th><th>入口</th></tr>
  <tr><td>L5 推理</td><td>vLLM（高吞吐推理）· llama.cpp（CPU/边缘）· Ollama（本地一键跑）</td><td>各项目 GitHub</td></tr>
  <tr><td>L4 向量检索</td><td>hnswlib（内存向量索引）· pgvector（PG 扩展）· Qdrant（云原生）</td><td>各项目文档</td></tr>
  <tr><td>L7 应用</td><td>Chainlit / Streamlit（快速 UI）· FastAPI（API 网关）</td><td>各项目文档</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> Agent 编排有哪几种流派？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 五大流派</div>
      <div class="a"><strong>1. 链/管道</strong>（LangChain LCEL）：函数组合。
        <strong>2. 图</strong>（LangGraph / MAF Workflow）：有向图 + 状态。
        <strong>3. 多 Agent 对话</strong>（AutoGen / MAF Group Chat）：Agent 间消息传递。
        <strong>4. Planner</strong>（SK）：LLM 规划步骤后执行。
        <strong>5. 声明式</strong>（MAF Declarative / Rivet）：配置驱动。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>MAF 在全栈中位于 <strong>L6 Agent 编排层</strong>。</li>
    <li>下一层（L5 推理 / L4 向量检索）是深入 AI 基础设施的方向。</li>
    <li>上一层（L7 应用）是把 Agent 交给用户的方向。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>编排层是"胶水层"</strong>——它连接模型、工具、存储和应用，
  因此<strong>对上下层都有基本了解</strong>是成为 Agent 高手的关键。
</div>
"""

L22_EN = r"""
<p class="lead">Final lesson — zoom out: place MAF in the <strong>AI full-stack</strong> coordinate system and see
what's worth learning next door.</p>

<h2>AI full-stack layers</h2>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">L7</span><span class="name">Application</span></div>
    <div class="ld">Your product / UI / API gateway.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">L6</span><span class="name">Agent Orchestration</span></div>
    <div class="ld"><strong>← You are here</strong> (MAF / LangGraph / AutoGen).</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">L5</span><span class="name">Model API / Inference</span></div>
    <div class="ld">OpenAI API · Azure AI · vLLM · llama.cpp · Ollama.</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">L4</span><span class="name">Vector Search / RAG</span></div>
    <div class="ld">Embeddings · pgvector · Qdrant · Azure AI Search.</div></div>
</div>

<h2>Learning map for neighbouring layers</h2>
<table class="t">
  <tr><th>Layer</th><th>What to learn</th><th>Entry point</th></tr>
  <tr><td>L5 Inference</td><td>vLLM (high-throughput) · llama.cpp (CPU/edge) · Ollama (local one-click)</td><td>project GitHub</td></tr>
  <tr><td>L4 Vector search</td><td>hnswlib (in-memory index) · pgvector (PG extension) · Qdrant (cloud-native)</td><td>project docs</td></tr>
  <tr><td>L7 Application</td><td>Chainlit / Streamlit (quick UI) · FastAPI (API gateway)</td><td>project docs</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> What are the orchestration schools? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🔬 Five schools</div>
      <div class="a"><strong>1. Chain/pipeline</strong> (LangChain LCEL): function composition.
        <strong>2. Graph</strong> (LangGraph / MAF Workflow): directed graph + state.
        <strong>3. Multi-agent chat</strong> (AutoGen / MAF Group Chat): message passing between agents.
        <strong>4. Planner</strong> (SK): LLM plans steps then executes.
        <strong>5. Declarative</strong> (MAF Declarative / Rivet): config-driven.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>MAF sits at <strong>L6 — the Agent Orchestration layer</strong>.</li>
    <li>Next layer down (L5 inference / L4 vector search) deepens AI infrastructure.</li>
    <li>Next layer up (L7 application) delivers agents to users.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>The orchestration layer is the "glue layer"</strong> — it connects models, tools, storage and applications.
  Knowing the layers above and below is key to becoming an Agent expert.
</div>
"""
