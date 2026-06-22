"""Content for Part 4 (advanced): lesson 15 — Chinese + English."""

L15_ZH = r"""
<p class="lead">想读 MAF 的源码、跑测试、开调试、提 PR？本课带你搭好环境,打通整个开发者工作流。</p>

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
uv run poe typing <span class="cm"># pyright 类型检查</span></pre></div></div>
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
  <summary><span class="badge-num">1</span> uv 为什么比 pip 好 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">速度对比：<span class="inline">uv sync</span> 在秒级完成，而 <span class="inline">pip install</span> 需要数分钟。
        <span class="mono">uv.lock</span> 是锁定文件，记录所有传递依赖的精确版本。
        Workspace 模式支持 monorepo，多个包可以一次性安装：
<pre class="code"><span class="cm"># uv.lock 记录了整个依赖树</span>
uv sync --all-packages  <span class="cm"># 装整个 monorepo</span>
cd packages/core && uv run poe test  <span class="cm"># 单包测试</span></pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">可复现的构建需要锁定文件（lockfile），pip 本身没有内置锁定机制。
        慢速安装会浪费大量 CI 时间。没有 workspace 支持的工具在 monorepo 中需要手动管理多个 <span class="inline">requirements.txt</span>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 使用 <span class="mono">uv</span> 的 workspace 模式。<span class="mono">uv.lock</span> 锁定每一个传递依赖的版本。
        <span class="inline">uv sync --all-packages</span> 原子式地安装整个 monorepo 的所有包，无需手动进入每个子目录。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">可选方案：pip + pip-tools（生成 requirements.txt.lock）、poetry（有锁定但慢）、pdm（锁定 + PEP 621）。
        <strong>uv 是最快的</strong>，且对 monorepo 的 workspace 原生支持最好。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> poe 任务速查 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">主要任务清单：
<pre class="code">uv run poe test      <span class="cm"># 运行 pytest</span>
uv run poe lint      <span class="cm"># ruff check（快速 linter）</span>
uv run poe format    <span class="cm"># ruff format（格式化）</span>
uv run poe typing <span class="cm"># pyright（类型检查）</span></pre>
        单包运行：
<pre class="code">cd packages/core
uv run poe test  <span class="cm"># 只测 core 包</span></pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">没有任务运行器（task runner），每个贡献者都会发明自己的魔法咒语。
        标准化的任务 = 一致的 CI/CD 流水线，新人上手只需记住几条命令。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 使用 <span class="mono">poethepoet</span>（简称 poe）。
        任务定义在 <span class="mono">pyproject.toml</span> 的 <span class="inline">[tool.poe.tasks]</span> 区块。
        每个质量门都有一条对应命令，本地开发和 CI 使用完全相同的命令。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">可选方案：Makefile（跨平台支持差）、just（需额外安装）、nox（偏重测试矩阵）、tox（配置复杂）。
        poe 的优点是集成在 <span class="inline">pyproject.toml</span> 中，且跨平台支持好。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 怎么写测试 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">测试文件命名为 <span class="inline">test_*.py</span>，放在 <span class="mono">tests/</span> 或 <span class="mono">packages/*/tests/</span>。
        使用 <span class="mono">pytest</span> + <span class="mono">pytest-asyncio</span> 处理异步：
<pre class="code"><span class="kw">import</span> pytest

<span class="nb">@pytest.mark.asyncio</span>
<span class="kw">async def</span> <span class="fn">test_agent_run</span>():
    agent = Agent()
    result = <span class="kw">await</span> agent.<span class="fn">run</span>(<span class="st">&quot;hello&quot;</span>)
    <span class="kw">assert</span> result.status == <span class="st">&quot;success&quot;</span></pre>
        使用 fixture 提供 mock 的 ChatClient。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">没有测试，重构就像走钢丝。异步代码尤其容易出错——<span class="mono">pytest-asyncio</span> 让异步测试变得可管理。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 使用 <span class="mono">pytest</span> + <span class="mono">pytest-asyncio</span>。
        测试与对应的包放在一起（<span class="inline">packages/*/tests/</span>）。
        单元测试用 mock ChatClient，避免真实 API 调用。<span class="inline">uv run poe test</span> 跑所有测试。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">可选方案：unittest（Python 标准库，但啰嗦）、ward（极简但小众）、hypothesis（属性测试，适合复杂逻辑）。
        pytest 是 Python 社区事实标准；asyncio 插件对异步框架是必需品。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> DevUI 使用 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">启动：
<pre class="code">cd samples/02-agents/devui
uv run python main.py</pre>
        自动打开浏览器界面，提供的功能：
        <ul>
          <li>与 Agent 聊天</li>
          <li>查看消息流（message flow）</li>
          <li>查看工具调用（tool calls）</li>
          <li>查看中间件管道（middleware pipeline）</li>
          <li>实时流式输出</li>
        </ul></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">CLI 测试很慢，且看不到中间状态。可视化调试可以揭示消息顺序、工具调用序列、中间件效果——这些在纯文本输出里很难发现。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 将 DevUI 作为 <span class="mono">packages/devui</span> 包发布。
        提供交互式 Web 界面，用于开发阶段调试。不需要外部工具，开箱即用。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">可选方案：LangSmith（LangChain 生态，收费）、Chainlit（需单独配置）、Mesop（Google 实验性项目）。
        MAF 的 DevUI 是<strong>内置且免费</strong>的。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> 提 PR 的流程 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">分支命名：<span class="inline">feature/my-change</span> 或 <span class="inline">fix/issue-123</span>。
        本地运行质量门：
<pre class="code">uv run poe lint && uv run poe typing && uv run poe test</pre>
        阅读代码规范：
<pre class="code">cat CODING_STANDARD.md
cat AGENTS.md</pre>
        PR 模板会要求填写：
        <ul>
          <li>改动描述</li>
          <li>测试方法</li>
          <li>关联的 issue</li>
        </ul></div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">质量差的 PR 会浪费审查者时间。在本地运行 CI 可以在推送前捕获 90% 的问题。
        阅读代码规范避免不必要的来回修改。</div>
    </div>
    <div class="qa">
      <div class="q">✅ MAF 的做法与优点</div>
      <div class="a">MAF 提供 <span class="mono">CODING_STANDARD.md</span> 和 <span class="mono">AGENTS.md</span> 文档化约定。
        CI 运行与本地相同的 poe 任务。PR 模板引导贡献者填写必要信息。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a">可选方案：有些项目使用 pre-commit hook（自动运行检查）、commitlint（规范提交信息）。
        MAF 保持简单，使用明确的 poe 任务，让贡献者自主运行。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 关键要点</div>
  <ul>
    <li>依赖管理用 <span class="mono">uv</span>；日常任务用 <span class="mono">uv run poe &lt;task&gt;</span>。</li>
    <li>核心在 <span class="mono">packages/core</span>，测试在 <span class="mono">packages/core/tests</span>。</li>
    <li>DevUI 提供浏览器调试界面，方便快速迭代。</li>
    <li>提 PR 前先在本地跑通 lint/typing/test。</li>
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
uv run poe typing <span class="cm"># pyright</span></pre></div></div>
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
  <summary><span class="badge-num">1</span> Why uv over pip <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Speed comparison: <span class="inline">uv sync</span> finishes in seconds vs <span class="inline">pip install</span> taking minutes.
        <span class="mono">uv.lock</span> is the lockfile recording exact versions of all transitive dependencies.
        Workspace mode supports monorepos with multiple packages installed atomically:
<pre class="code"><span class="cm"># uv.lock records the entire dependency tree</span>
uv sync --all-packages  <span class="cm"># install entire monorepo</span>
cd packages/core && uv run poe test  <span class="cm"># test single package</span></pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Reproducible builds require lockfiles. pip has no built-in locking mechanism.
        Slow installs waste CI time. Tools without workspace support force manual management of multiple <span class="inline">requirements.txt</span> in monorepos.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF uses <span class="mono">uv</span> with workspace mode. <span class="mono">uv.lock</span> pins every transitive dependency.
        <span class="inline">uv sync --all-packages</span> atomically installs all packages across the monorepo without manually entering each subdirectory.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Options: pip + pip-tools (generates requirements.txt.lock), poetry (has locking but slow), pdm (locking + PEP 621).
        <strong>uv is the fastest</strong> and has the best native workspace support for monorepos.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> poe task reference <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Main tasks:
<pre class="code">uv run poe test      <span class="cm"># run pytest</span>
uv run poe lint      <span class="cm"># ruff check (fast linter)</span>
uv run poe format    <span class="cm"># ruff format</span>
uv run poe typing <span class="cm"># pyright (type checker)</span></pre>
        Run for one package:
<pre class="code">cd packages/core
uv run poe test  <span class="cm"># test core only</span></pre></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Without a task runner, every contributor invents their own incantation.
        Standardized tasks = consistent CI/CD pipeline. New contributors only need to learn a few commands.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF uses <span class="mono">poethepoet</span> (poe for short).
        Tasks are defined in <span class="mono">pyproject.toml</span> under <span class="inline">[tool.poe.tasks]</span>.
        Each quality gate has one command. Local dev and CI use identical commands.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Options: Makefile (poor cross-platform), just (requires separate install), nox (heavy on test matrices), tox (complex config).
        poe integrates with <span class="inline">pyproject.toml</span> and has excellent cross-platform support.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> How to write tests <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Test files named <span class="inline">test_*.py</span> in <span class="mono">tests/</span> or <span class="mono">packages/*/tests/</span>.
        Use <span class="mono">pytest</span> + <span class="mono">pytest-asyncio</span> for async:
<pre class="code"><span class="kw">import</span> pytest

<span class="nb">@pytest.mark.asyncio</span>
<span class="kw">async def</span> <span class="fn">test_agent_run</span>():
    agent = Agent()
    result = <span class="kw">await</span> agent.<span class="fn">run</span>(<span class="st">&quot;hello&quot;</span>)
    <span class="kw">assert</span> result.status == <span class="st">&quot;success&quot;</span></pre>
        Use fixtures for mock ChatClient.</div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Without tests, refactoring is scary. Async code is especially tricky — <span class="mono">pytest-asyncio</span> makes async testing manageable.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF uses <span class="mono">pytest</span> + <span class="mono">pytest-asyncio</span>.
        Tests live alongside packages (<span class="inline">packages/*/tests/</span>).
        Mock ChatClient for unit tests to avoid real API calls. <span class="inline">uv run poe test</span> runs everything.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Options: unittest (Python stdlib but verbose), ward (minimal but niche), hypothesis (property-based testing for complex logic).
        pytest is the Python standard; asyncio plugin is essential for async frameworks.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> Using DevUI <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Launch:
<pre class="code">cd samples/02-agents/devui
uv run python main.py</pre>
        Opens browser UI. Features:
        <ul>
          <li>Chat with agent</li>
          <li>Inspect message flow</li>
          <li>View tool calls</li>
          <li>View middleware pipeline</li>
          <li>Real-time streaming</li>
        </ul></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">CLI testing is slow and doesn't show intermediate state. Visual debugging reveals message ordering, tool call sequences, middleware effects — hard to spot in plain text output.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF ships DevUI as <span class="mono">packages/devui</span> package.
        Interactive web interface for development. No external tools needed — works out of the box.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Options: LangSmith (LangChain ecosystem, paid), Chainlit (separate setup), Mesop (Google experimental).
        MAF's DevUI is <strong>built-in and free</strong>.</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> PR workflow <span class="hint">expand</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Example</div>
      <div class="a">Branch naming: <span class="inline">feature/my-change</span> or <span class="inline">fix/issue-123</span>.
        Run quality gates locally:
<pre class="code">uv run poe lint && uv run poe typing && uv run poe test</pre>
        Read style rules:
<pre class="code">cat CODING_STANDARD.md
cat AGENTS.md</pre>
        PR template asks for:
        <ul>
          <li>Description of changes</li>
          <li>Testing approach</li>
          <li>Related issues</li>
        </ul></div>
    </div>
    <div class="qa">
      <div class="q">❓ Why this matters</div>
      <div class="a">Bad PRs waste reviewer time. Running CI locally catches 90% of issues before push.
        Reading coding standards avoids unnecessary back-and-forth.</div>
    </div>
    <div class="qa">
      <div class="q">✅ How MAF does it</div>
      <div class="a">MAF has <span class="mono">CODING_STANDARD.md</span> and <span class="mono">AGENTS.md</span> documenting conventions.
        CI runs the same poe tasks. PR template guides contributors to provide necessary information.</div>
    </div>
    <div class="qa">
      <div class="q">🔀 Alternatives</div>
      <div class="a">Options: Some projects use pre-commit hooks (auto-run checks), commitlint (enforce commit message format).
        MAF keeps it simple with explicit poe tasks that contributors run themselves.</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Dependency management: <span class="mono">uv</span>; daily tasks: <span class="mono">uv run poe &lt;task&gt;</span>.</li>
    <li>Core is in <span class="mono">packages/core</span>; tests in <span class="mono">packages/core/tests</span>.</li>
    <li>DevUI gives a browser-based debug interface for fast iteration.</li>
    <li>Before submitting PR, run lint/typing/test locally.</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>One command installs everything</strong>: <span class="mono">uv sync --all-packages</span> installs the
  entire monorepo — all providers, lab, DevUI — giving you the full dev environment, not a stripped-down one.
</div>
"""
