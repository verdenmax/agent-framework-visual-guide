"""Content for Part 4 (advanced): lesson 15 — Chinese + English."""

L15_ZH = r"""
<p class="lead">想读 MAF 的源码、跑测试、开调试、提 PR？本课带你搭好环境，打通整个开发者工作流。</p>

<div class="card analogy">
  <div class="tag">🛠️ 生活类比</div>
  就像加入一个<strong>开源车间</strong>：先领工服（clone + 装依赖），
  再认识工具台（poe 命令），然后试拧一个螺丝（跑测试），最后才上手改车。
</div>

<h2>环境搭建（3 步）</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>克隆仓库</h4>
<pre class="code">git clone https://github.com/microsoft/agent-framework.git
cd agent-framework/python</pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>安装依赖</h4>
<pre class="code">uv sync --all-packages --all-extras --dev --prerelease=if-necessary-or-explicit</pre>
    <p>使用 <span class="mono">uv</span>（Rust 写的超快 Python 包管理器）。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>看有哪些命令</h4>
<pre class="code">uv run poe          <span class="cm"># 列出所有可用任务</span>
uv run poe test     <span class="cm"># 跑所有单元测试</span>
uv run poe lint     <span class="cm"># Ruff lint</span>
uv run poe format   <span class="cm"># Ruff format</span>
uv run poe typecheck <span class="cm"># pyright 类型检查</span></pre></div></div>
</div>

<h2>关键文件导航</h2>
<table class="t">
  <tr><th>你要做的</th><th>去哪</th></tr>
  <tr><td>看核心源码</td><td class="mono">packages/core/agent_framework/</td></tr>
  <tr><td>跑/加测试</td><td class="mono">packages/core/tests/ 或 tests/</td></tr>
  <tr><td>看/跑样例</td><td class="mono">samples/01-get-started/</td></tr>
  <tr><td>调 DevUI</td><td class="mono">packages/devui/</td></tr>
  <tr><td>读代码规范</td><td class="mono">CODING_STANDARD.md · AGENTS.md</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> DevUI 是什么？ <span class="hint">点击展开</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 开发者调试界面</div>
      <div class="a"><span class="mono">packages/devui</span> 提供一个<strong>交互式 Web UI</strong>，
        可以在浏览器里试 Agent、看消息流、调试工作流——省掉写脚本反复 run 的麻烦。
        启动方式见 <span class="mono">samples/02-agents/devui/</span>。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>依赖管理用 <span class="mono">uv</span>；日常任务用 <span class="mono">uv run poe &lt;task&gt;</span>。</li>
    <li>核心在 <span class="mono">packages/core</span>，测试在 <span class="mono">packages/core/tests</span>。</li>
    <li>DevUI 提供浏览器调试界面，方便快速迭代。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>一条命令装好一切</strong>：<span class="mono">uv sync --all-packages</span> 装整个 monorepo 的所有包，
  包括 provider、lab、DevUI——你拿到的是完整的开发环境，不是阉割版。
</div>
"""

L15_EN = r"""
<p class="lead">Want to read MAF source, run tests, debug, contribute PRs? This lesson sets up the environment
and walks through the developer workflow.</p>

<div class="card analogy">
  <div class="tag">🛠️ Analogy</div>
  Like joining an <strong>open-source workshop</strong>: first get your uniform (clone + install deps),
  learn the tool bench (poe commands), tighten one bolt (run tests), then start modifying the car.
</div>

<h2>Setup (3 steps)</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Clone</h4>
<pre class="code">git clone https://github.com/microsoft/agent-framework.git
cd agent-framework/python</pre></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Install deps</h4>
<pre class="code">uv sync --all-packages --all-extras --dev --prerelease=if-necessary-or-explicit</pre>
    <p>Uses <span class="mono">uv</span> (a blazing-fast Rust-based Python package manager).</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Discover commands</h4>
<pre class="code">uv run poe          <span class="cm"># list all tasks</span>
uv run poe test     <span class="cm"># unit tests</span>
uv run poe lint     <span class="cm"># Ruff lint</span>
uv run poe format   <span class="cm"># Ruff format</span>
uv run poe typecheck <span class="cm"># pyright</span></pre></div></div>
</div>

<h2>Key file navigation</h2>
<table class="t">
  <tr><th>Goal</th><th>Where</th></tr>
  <tr><td>Core source</td><td class="mono">packages/core/agent_framework/</td></tr>
  <tr><td>Run/add tests</td><td class="mono">packages/core/tests/ or tests/</td></tr>
  <tr><td>Run samples</td><td class="mono">samples/01-get-started/</td></tr>
  <tr><td>DevUI</td><td class="mono">packages/devui/</td></tr>
  <tr><td>Coding standards</td><td class="mono">CODING_STANDARD.md · AGENTS.md</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> What is DevUI? <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Developer debug interface</div>
      <div class="a"><span class="mono">packages/devui</span> provides an <strong>interactive web UI</strong> to
        try agents, inspect message flows and debug workflows in the browser — no need to write scripts and
        re-run. See <span class="mono">samples/02-agents/devui/</span> for launch instructions.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Dependency management: <span class="mono">uv</span>; daily tasks: <span class="mono">uv run poe &lt;task&gt;</span>.</li>
    <li>Core is in <span class="mono">packages/core</span>; tests in <span class="mono">packages/core/tests</span>.</li>
    <li>DevUI gives a browser-based debug interface for fast iteration.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>One command installs everything</strong>: <span class="mono">uv sync --all-packages</span> installs the
  entire monorepo — all providers, lab, DevUI — giving you the full dev environment, not a stripped-down one.
</div>
"""
