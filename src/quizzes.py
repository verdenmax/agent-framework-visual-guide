"""Per-lesson bilingual self-test (自测题): design-insight MCQ + open prompts.

Schema per lesson::

    "NN-file.html": {
        "mcq": [
            {"q": {"zh","en"}, "opts": [{"zh","en"}, ...],
             "answer": <0-based index into opts as written>,
             "why": {"zh","en"}},
        ],
        "open": [{"zh","en"}, ...],
    }

``render(fname, lang)`` returns single-language HTML that build.py appends to the
bottom of that language's lesson body. Options are deterministically shuffled per
question (same permutation for zh and en, so the correct letter matches across
languages). Quiz text is raw HTML in a text context (like the lesson body): write
literal ``<``/``&`` as ``&lt;``/``&amp;`` or wrap code in ``<code>``.
"""
import hashlib

_HEAD = {"zh": "🧪 自测 · 想一想为什么这么设计", "en": "🧪 Self-test - think about the design"}
_SEE = {"zh": "看答案与解析", "en": "Show answer &amp; explanation"}
_CLICK = {"zh": "点击展开", "en": "click to expand"}
_ANS = {"zh": "答案：", "en": "Answer: "}
_SEP = {"zh": "。", "en": ". "}
_OPEN = {
    "zh": "💭 发散思考（没有标准答案，动手或动脑想想）",
    "en": "💭 Open questions (no single right answer - just think or try)",
}


def _shuffle(opts, answer, seed):
    """Deterministically permute opts (stable across builds); return
    (new_opts, new_answer_index) so the correct option lands in a varied slot."""
    order = sorted(
        range(len(opts)),
        key=lambda i: hashlib.md5(f"{seed}:{i}".encode("utf-8")).hexdigest(),
    )
    return [opts[i] for i in order], order.index(answer)


QUIZZES = {
    "01-what-is-agent-framework.html": {
        "mcq": [
            {
                "q": {
                    "zh": "Agent Framework 把“换一家模型厂商”变成基本只改一行代码。这主要靠的是什么设计？",
                    "en": "Agent Framework makes 'switch model vendor' basically a one-line change. Which design mainly enables that?",
                },
                "opts": [
                    {"zh": "它帮你自动训练模型", "en": "It trains the model for you"},
                    {
                        "zh": "统一的 ChatClient 抽象把厂商差异挡在同一接口后面",
                        "en": "A uniform ChatClient abstraction hides vendor differences behind one interface",
                    },
                    {"zh": "它把所有厂商的代码复制进你的项目", "en": "It copies every vendor's code into your project"},
                    {"zh": "它只支持一家厂商", "en": "It supports only one vendor"},
                ],
                "answer": 1,
                "why": {
                    "zh": "Agent 依赖抽象的 ChatClient，而非具体厂商 SDK；换厂商只是换一个 ChatClient 实现，Agent 与工具/记忆逻辑都不动——这正是“面向接口”的取舍。",
                    "en": "An Agent depends on the abstract ChatClient, not a concrete vendor SDK; switching vendors just swaps a ChatClient implementation while agent/tool/memory logic stays put - the classic 'program to an interface' tradeoff.",
                },
            },
            {
                "q": {
                    "zh": "下面哪一项<strong>不是</strong> Agent Framework 想替你抹平的“上生产”麻烦？",
                    "en": "Which is <strong>not</strong> one of the production headaches Agent Framework aims to smooth over?",
                },
                "opts": [
                    {"zh": "可观测性（OpenTelemetry）", "en": "Observability (OpenTelemetry)"},
                    {"zh": "检查点与人在环审批", "en": "Checkpointing and human-in-the-loop approval"},
                    {"zh": "替你决定该用哪个机器学习算法训练模型", "en": "Choosing which ML algorithm to train your model with"},
                    {"zh": "持久化 / 可恢复的工作流", "en": "Durable / resumable workflows"},
                ],
                "answer": 2,
                "why": {
                    "zh": "Agent Framework 负责模型“周边”的工程管道（编排、可观测、持久化、审批），<strong>不</strong>负责训练模型本身——训练不在它的职责范围。",
                    "en": "Agent Framework owns the engineering plumbing <em>around</em> the model (orchestration, observability, durability, approval); it does <strong>not</strong> train the model itself - training is out of scope.",
                },
            },
            {
                "q": {
                    "zh": "最小示例里要<strong>先建一个 ChatClient，再把它包成 Agent</strong>。为什么不干脆把“连模型”和“Agent 行为”塞进同一个类？",
                    "en": "The minimal sample first builds a ChatClient, then wraps it in an Agent. Why not fold &quot;talk to the model&quot; and &quot;agent behavior&quot; into a single class?",
                },
                "opts": [
                    {
                        "zh": "ChatClient 负责“怎么和某厂商的模型通话”，Agent 负责“人设 / 工具 / 循环”；分层后换厂商只改 ChatClient 那一行，Agent 逻辑不动",
                        "en": "ChatClient owns &quot;how to talk to a vendor's model&quot;, Agent owns &quot;persona / tools / loop&quot;; splitting them means switching vendors changes only the ChatClient line while Agent logic stays put",
                    },
                    {"zh": "因为 Python 不允许一个类做两件事", "en": "Because Python forbids a class from doing two things"},
                    {"zh": "因为合在一起会让模型训练变慢", "en": "Because merging them slows down model training"},
                    {"zh": "因为每个厂商都得重写一份 Agent", "en": "Because each vendor needs its own rewritten Agent"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>ChatClient</code> 是厂商无关的“连接层”，<code>Agent</code> 是其上的“行为层”（name / instructions / tools / run 循环）。两层分离正是“换厂商基本只改一行”的根因——同一个 <code>Agent</code> 能套在任何 <code>ChatClient</code> 上（<code>Agent(client=…)</code> 或 <code>client.as_agent(…)</code>）。",
                    "en": "<code>ChatClient</code> is the vendor-neutral connection layer; <code>Agent</code> is the behavior layer on top (name / instructions / tools / run loop). That separation is exactly why a vendor swap is &quot;basically one line&quot; - the same <code>Agent</code> wraps any <code>ChatClient</code> (<code>Agent(client=…)</code> or <code>client.as_agent(…)</code>).",
                },
            },
        ],
        "open": [
            {
                "zh": "假设你已经用某厂商 SDK 直接写了一个聊天脚本。请列出迁移到 Agent Framework 后，你认为最先会“消失”的三段样板代码，并说明各自由框架的哪个概念接管（ChatClient / Message / @tool / Workflow 任选）。",
                "en": "Suppose you already wrote a chat script directly against a vendor SDK. List the three pieces of boilerplate you expect to 'disappear' first after moving to Agent Framework, and say which framework concept (ChatClient / Message / @tool / Workflow) takes over each.",
            },
        ],
    },
    "02-monorepo.html": {
        "mcq": [
            {
                "q": {
                    "zh": "core 把 <code>Agent</code> / <code>Message</code> / <code>tool</code> / <code>Workflows</code> 都放进<strong>同一个</strong> <code>agent_framework</code> 包（一个包、多个 <code>_</code> 前缀文件），而不是拆成几十个小 PyPI 包。主要好处是？",
                    "en": "core puts <code>Agent</code> / <code>Message</code> / <code>tool</code> / <code>Workflows</code> all in <strong>one</strong> <code>agent_framework</code> package (one package, many <code>_</code>-prefixed files) instead of dozens of tiny PyPI packages. The main benefit?",
                },
                "opts": [
                    {
                        "zh": "对外只有一个 import 路径、内部重构不影响用户代码，同时躲开“微包架构”的依赖地狱",
                        "en": "One public import path, internal refactors don't touch user code, while avoiding the dependency hell of a micro-package architecture",
                    },
                    {"zh": "让程序运行得更快", "en": "It makes the program run faster"},
                    {"zh": "强制所有人改用 .NET", "en": "It forces everyone onto .NET"},
                    {"zh": "让 core 不依赖任何东西", "en": "It makes core depend on nothing"},
                ],
                "answer": 0,
                "why": {
                    "zh": "“单包多文件”是大框架常见折中：对外是一个 <code>from agent_framework import …</code>，对内用 <code>_</code> 前缀文件分层、靠 <code>__init__.py</code> 的 <code>__all__</code> 暴露公共 API。微包架构带来版本/依赖噩梦，god-module 又会循环依赖、加载慢——单包多文件兼顾两端。",
                    "en": "&quot;One package, many files&quot; is the classic big-framework compromise: outside it's a single <code>from agent_framework import …</code>; inside, <code>_</code>-prefixed files layer the code and <code>__init__.py</code>'s <code>__all__</code> exposes the public API. Micro-packages bring version/dependency nightmares; a god-module brings circular imports and slow loads - one-package-many-files balances both.",
                },
            },
            {
                "q": {
                    "zh": "<code>import agent_framework</code> 并不会拉起 <code>azure-identity</code>、<code>anthropic</code> 等重依赖；只有真正访问对应 ChatClient 时才加载。这靠的是？",
                    "en": "<code>import agent_framework</code> does <em>not</em> pull in heavy deps like <code>azure-identity</code> or <code>anthropic</code>; they load only when you actually access the matching ChatClient. How?",
                },
                "opts": [
                    {
                        "zh": "provider 子模块用模块级 <code>__getattr__</code>（PEP 562）做懒加载，访问时才 import",
                        "en": "Provider submodules use module-level <code>__getattr__</code> (PEP 562) for lazy loading - importing only on access",
                    },
                    {"zh": "把所有 provider 依赖都打包进 core", "en": "All provider deps are bundled into core"},
                    {"zh": "每次 import 都全量加载所有厂商", "en": "Every import eagerly loads every vendor"},
                    {"zh": "用一个全局 <code>try/except</code> 吞掉缺失依赖", "en": "A global <code>try/except</code> swallows missing deps"},
                ],
                "answer": 0,
                "why": {
                    "zh": "子模块 <code>__init__.py</code> 用 <code>__getattr__</code> 延迟 import：启动更快（少装一个 SDK 就少几十毫秒）、可选依赖没装也不会在 import 时报错、安装体积按需（<code>pip install agent-framework[azure]</code>）。core 因此保持轻量，新增厂商不碰 core。",
                    "en": "A submodule's <code>__init__.py</code> defers imports via <code>__getattr__</code>: faster startup (each un-loaded SDK saves tens of ms), optional deps don't error at import time when absent, and install size stays on-demand (<code>pip install agent-framework[azure]</code>). core stays lightweight and adding a vendor never touches core.",
                },
            },
        ],
        "open": [
            {
                "zh": "假设你要给一个新厂商（比如某国产模型）写 provider 包。按 monorepo 的约定，它应该放在哪、依赖谁、要不要改动 core？请解释“新增厂商不碰 core”这条约束为什么值得坚持。",
                "en": "Suppose you write a provider package for a new vendor. Following the monorepo's conventions, where should it live, what does it depend on, and does it require changes to core? Explain why the &quot;adding a vendor never touches core&quot; rule is worth keeping.",
            },
        ],
    },
    "03-lifecycle.html": {
        "mcq": [
            {
                "q": {
                    "zh": "你只写了一行 <code>await agent.run(&quot;…&quot;)</code>，但模型要调工具时会“调模型 → 执行工具 → 再调模型”地循环好几轮。这个循环发生在哪？",
                    "en": "You wrote just one line <code>await agent.run(&quot;…&quot;)</code>, yet when the model needs tools it loops &quot;call model → run tool → call model&quot; several rounds. Where does that loop run?",
                },
                "opts": [
                    {"zh": "在 <code>run()</code> 内部自动跑完，你对外只调用一次", "en": "Inside <code>run()</code>, completed automatically - you call it just once"},
                    {"zh": "你必须自己写 <code>while</code> 循环反复调 <code>run()</code>", "en": "You must write your own <code>while</code> loop calling <code>run()</code> repeatedly"},
                    {"zh": "在每个工具函数自己的代码里", "en": "Inside each tool function's own code"},
                    {"zh": "在 <code>print()</code> 输出时", "en": "While <code>print()</code> renders output"},
                ],
                "answer": 0,
                "why": {
                    "zh": "这正是经典的 Agent 循环（think → act → observe）：模型产出 <code>function_call</code>，框架执行工具、把 <code>function_result</code> 追加进消息、再回到“调模型”那步，直到模型不再要工具（有上限 <code>DEFAULT_MAX_ITERATIONS=40</code>）。你对外只 <code>run</code> 一次。",
                    "en": "This is the classic agent loop (think → act → observe): the model emits a <code>function_call</code>, the framework runs the tool, appends the <code>function_result</code> to the messages, and returns to &quot;call model&quot; until the model stops asking for tools (capped at <code>DEFAULT_MAX_ITERATIONS=40</code>). You only <code>run</code> once.",
                },
            },
            {
                "q": {
                    "zh": "多轮对话里“模型记得上文”，本质靠的是什么？",
                    "en": "In a multi-turn chat, what fundamentally makes &quot;the model remember earlier turns&quot; work?",
                },
                "opts": [
                    {
                        "zh": "把同一个 <code>session</code>（<code>AgentSession</code>）透传给每次 <code>run()</code>，历史自动累积进消息列表",
                        "en": "Passing the same <code>session</code> (<code>AgentSession</code>) into each <code>run()</code>, so history accumulates into the message list",
                    },
                    {"zh": "模型内部存了一块持久记忆", "en": "The model keeps a block of persistent memory inside it"},
                    {"zh": "框架用一个全局变量记住所有人的对话", "en": "The framework keeps everyone's chat in one global variable"},
                    {"zh": "靠 <code>finish_reason</code> 字段携带历史", "en": "The <code>finish_reason</code> field carries the history"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>run()</code> 默认<strong>无状态</strong>；要连续性就 <code>agent.create_session()</code> 再每次 <code>run(…, session=session)</code>，用户消息 + 回复会自动追加进会话历史。状态的唯一载体是不断变长的消息列表，而不是模型“记住”了什么。",
                    "en": "<code>run()</code> is <strong>stateless</strong> by default; for continuity you call <code>agent.create_session()</code> then <code>run(…, session=session)</code> each time, and user messages + replies append to the session's history. The only carrier of state is the growing message list, not anything the model &quot;remembers&quot;.",
                },
            },
        ],
        "open": [
            {
                "zh": "<code>run()</code> 组装请求时把 instructions / 历史 / 当前输入 / 工具 schema 拼到一起发给模型。如果你的 Agent 挂了 20 个工具又开了很长对话，你预计哪部分会最先吃满上下文窗口？据此谈谈“工具数量”和“历史长度”各自带来的 token 成本与取舍。",
                "en": "When <code>run()</code> assembles a request it stitches instructions / history / current input / tool schemas together for the model. If your Agent has 20 tools and a long conversation, which part do you expect to fill the context window first? Use that to discuss the token cost and tradeoffs of &quot;number of tools&quot; vs &quot;history length&quot;.",
            },
        ],
    },
    "04-messages.html": {
        "mcq": [
            {
                "q": {
                    "zh": "MAF 不给每种内容（文字 / 图片 / 工具调用 / 工具结果）各写一个类，而是用<strong>一个统一的 <code>Content</code></strong> 加 <code>type</code> 字段。这样做的核心好处是？",
                    "en": "Instead of a separate class per content kind (text / image / function call / result), MAF uses <strong>one unified <code>Content</code></strong> with a <code>type</code> field. The core benefit?",
                },
                "opts": [
                    {
                        "zh": "一条 <code>Message</code> 的 <code>contents</code> 是 <code>Content</code> 列表，每个带 <code>type</code>（<code>&quot;text&quot;</code>/<code>&quot;uri&quot;</code>/<code>&quot;function_call&quot;</code>…），框架按 type 路由；加新内容类型只需加一个 type，老消息照常工作",
                        "en": "A <code>Message</code>'s <code>contents</code> is a list of <code>Content</code>, each carrying a <code>type</code> (<code>&quot;text&quot;</code>/<code>&quot;uri&quot;</code>/<code>&quot;function_call&quot;</code>…); the framework routes by type, and a new kind is just a new type while old messages keep working",
                    },
                    {"zh": "因为 Python 不支持定义多个类", "en": "Because Python can't define multiple classes"},
                    {"zh": "因为这样模型推理更准确", "en": "Because it makes the model reason more accurately"},
                    {"zh": "因为每个厂商都需要独立的 Message 类", "en": "Because each vendor needs its own Message class"},
                ],
                "answer": 0,
                "why": {
                    "zh": "这是<strong>判别联合（discriminated union）</strong>：统一成 <code>Content</code> 列表后，代码只需关心“一条消息有多个内容块”，图文混排、工具调用 / 结果都用同一容器，并用工厂方法 <code>Content.from_text()</code> / <code>from_uri()</code> / <code>from_function_call()</code> 构造。跨厂商把各家格式归一成一套，业务代码零修改。",
                    "en": "This is a <strong>discriminated union</strong>: with a unified <code>Content</code> list, code only cares that &quot;a message has several content blocks&quot;; mixed text+image and function call/result all share one container, built via factory methods <code>Content.from_text()</code> / <code>from_uri()</code> / <code>from_function_call()</code>. It normalizes every vendor's format into one, so business code never changes.",
                },
            },
            {
                "q": {
                    "zh": "消息的 <code>role</code>（<code>&quot;system&quot;</code>/<code>&quot;user&quot;</code>/<code>&quot;assistant&quot;</code>/<code>&quot;tool&quot;</code>）在 MAF 里是什么类型？",
                    "en": "What type is a message's <code>role</code> (<code>&quot;system&quot;</code>/<code>&quot;user&quot;</code>/<code>&quot;assistant&quot;</code>/<code>&quot;tool&quot;</code>) in MAF?",
                },
                "opts": [
                    {
                        "zh": "<code>Role</code> 是字符串型（<code>NewType</code> over <code>str</code>）——直接用字符串值，甚至能用自定义角色",
                        "en": "<code>Role</code> is string-based (a <code>NewType</code> over <code>str</code>) - use the string value directly, even custom roles",
                    },
                    {"zh": "一个封闭的 <code>Enum</code>，无法扩展", "en": "A closed <code>Enum</code> that can't be extended"},
                    {"zh": "一个整数 ID", "en": "An integer id"},
                    {"zh": "每个角色一个子类", "en": "A subclass per role"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>Role = NewType(&quot;Role&quot;, str)</code>，所以直接写 <code>Message(&quot;user&quot;, […])</code>。选字符串而非封闭 <code>Enum</code> 是“可扩展”取舍：将来出现新角色或厂商特有角色不必改框架；代价是少了 <code>Enum</code> 的编译期约束，靠约定与文档兜底。",
                    "en": "<code>Role = NewType(&quot;Role&quot;, str)</code>, so you just write <code>Message(&quot;user&quot;, […])</code>. Choosing a string over a closed <code>Enum</code> is an extensibility tradeoff: future or vendor-specific roles need no framework change; the cost is losing the <code>Enum</code>'s compile-time guardrails, backed instead by convention and docs.",
                },
            },
        ],
        "open": [
            {
                "zh": "<code>Message</code> 的 <code>contents</code> 为什么设计成“列表”而不是“单个内容”？举一个必须用多内容块的真实场景（提示：多模态，或一轮里既有文字又有工具调用），并说说这对“跨厂商统一格式”有什么帮助。",
                "en": "Why is <code>Message.contents</code> a <em>list</em> rather than a single content? Give a real scenario that needs multiple blocks (hint: multimodal, or text + a function call in one turn), and explain how that helps &quot;one format across vendors&quot;.",
            },
        ],
    },
    "05-chat-models.html": {
        "mcq": [
            {
                "q": {
                    "zh": "<code>Agent(client=…)</code> 和 <code>client.as_agent(…)</code> 是什么关系？",
                    "en": "What's the relationship between <code>Agent(client=…)</code> and <code>client.as_agent(…)</code>?",
                },
                "opts": [
                    {
                        "zh": "两者等价，底下都构造同一个 <code>Agent</code>；<code>as_agent</code> 只是 ChatClient 上的便捷工厂方法",
                        "en": "They're equivalent - both build the same <code>Agent</code>; <code>as_agent</code> is just a convenience factory on the ChatClient",
                    },
                    {"zh": "<code>as_agent</code> 会训练一个新模型", "en": "<code>as_agent</code> trains a new model"},
                    {"zh": "<code>Agent(client=)</code> 是同步、<code>as_agent</code> 是异步", "en": "<code>Agent(client=)</code> is sync, <code>as_agent</code> is async"},
                    {"zh": "两者产出互不兼容的类", "en": "They produce incompatible classes"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>as_agent</code> 是 ChatClient 的便捷工厂，内部就是 <code>Agent(client=self, …)</code>。给两种写法只是风格选择；无论哪种，换厂商时改的都只是 <code>client</code> 实例化那一行，Agent 的行为层（name / instructions / tools）不动。",
                    "en": "<code>as_agent</code> is a convenience factory on the ChatClient that internally does <code>Agent(client=self, …)</code>. Two spellings are just style; either way, switching vendors changes only the <code>client</code> construction line - the Agent's behavior layer (name / instructions / tools) stays put.",
                },
            },
            {
                "q": {
                    "zh": "同一个 <code>agent.run()</code>，怎么从“一次拿到完整回答”切到“逐块流式输出”？",
                    "en": "With the same <code>agent.run()</code>, how do you switch from &quot;full answer at once&quot; to &quot;token-by-token streaming&quot;?",
                },
                "opts": [
                    {
                        "zh": "传 <code>stream=True</code>：返回异步迭代器，逐块给 <code>AgentResponseUpdate</code>；不传则返回完整 <code>AgentResponse</code>",
                        "en": "Pass <code>stream=True</code>: returns an async iterator yielding <code>AgentResponseUpdate</code> chunks; omit it for a complete <code>AgentResponse</code>",
                    },
                    {"zh": "调用另一个方法 <code>run_stream_v2()</code>", "en": "Call a different method <code>run_stream_v2()</code>"},
                    {"zh": "必须新建一个 <code>StreamingAgent</code> 类", "en": "Build a separate <code>StreamingAgent</code> class"},
                    {"zh": "在 instructions 里写一句 &quot;please stream&quot;", "en": "Write &quot;please stream&quot; in the instructions"},
                ],
                "answer": 0,
                "why": {
                    "zh": "流式与非流式共用 <code>run()</code>，由 <code>stream</code> 参数切换返回形态：完整的 <code>AgentResponse</code> vs 一串 <code>AgentResponseUpdate</code>。这样上层代码结构基本一致，流式时按需逐块渲染 <code>chunk.text</code> 即可。",
                    "en": "Streaming and non-streaming share one <code>run()</code>; the <code>stream</code> flag switches the return shape: a full <code>AgentResponse</code> vs a sequence of <code>AgentResponseUpdate</code>. Upper-layer code stays structurally similar - just render <code>chunk.text</code> incrementally when streaming.",
                },
            },
        ],
        "open": [
            {
                "zh": "流式（<code>stream=True</code>）对“用户体感延迟”和“代码复杂度”各有什么影响？什么场景你反而宁愿用非流式（一次性拿 <code>AgentResponse</code>）？",
                "en": "How does streaming (<code>stream=True</code>) affect &quot;perceived latency&quot; vs &quot;code complexity&quot;? In which scenarios would you actually prefer non-streaming (one <code>AgentResponse</code>)?",
            },
        ],
    },
    "06-tools.html": {
        "mcq": [
            {
                "q": {
                    "zh": "用 <code>@tool</code> 标注一个普通函数后，交给模型的那份工具 <strong>JSON Schema</strong> 是从哪来的？",
                    "en": "After decorating a plain function with <code>@tool</code>, where does the tool's <strong>JSON Schema</strong> (handed to the model) come from?",
                },
                "opts": [
                    {
                        "zh": "从函数签名 + 类型注解（<code>Annotated[…, Field(description=…)]</code>）+ docstring 自动生成",
                        "en": "Auto-generated from the signature + type hints (<code>Annotated[…, Field(description=…)]</code>) + docstring",
                    },
                    {"zh": "你必须手写一段 JSON Schema 字符串", "en": "You must hand-write a JSON Schema string"},
                    {"zh": "模型自己猜参数", "en": "The model guesses the parameters itself"},
                    {"zh": "从一个外部数据库读取", "en": "Read from an external database"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>@tool</code> 读取签名 / 注解 / docstring 自动产出 JSON Schema 交给模型：docstring 变工具描述，<code>Annotated</code> 里的 <code>Field(description=…)</code> 变参数说明，默认值/约束也带过去。所以“写好类型与 docstring”本质就是在写“给模型看的说明书”。",
                    "en": "<code>@tool</code> reads the signature / hints / docstring to emit the JSON Schema for the model: the docstring becomes the tool description, <code>Field(description=…)</code> inside <code>Annotated</code> becomes parameter docs, and defaults/constraints carry over. So &quot;writing good types and a docstring&quot; <em>is</em> writing the model's instruction manual.",
                },
            },
            {
                "q": {
                    "zh": "给 <code>@tool</code> 设 <code>approval_mode=&quot;always_require&quot;</code> 的意义是？",
                    "en": "What does <code>approval_mode=&quot;always_require&quot;</code> on a <code>@tool</code> mean?",
                },
                "opts": [
                    {
                        "zh": "工具执行前暂停、要求人工确认（人在环）——适合写操作 / 花钱的操作",
                        "en": "Pause before the tool runs and require human confirmation (human-in-the-loop) - good for write / spend actions",
                    },
                    {"zh": "让工具运行得更快", "en": "Makes the tool run faster"},
                    {"zh": "永远不调用这个工具", "en": "Never calls this tool"},
                    {"zh": "自动批准所有调用", "en": "Auto-approves every call"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>ApprovalMode</code> 是 <code>Literal[&quot;always_require&quot;, &quot;never_require&quot;]</code>。把“要不要人审”做成工具上的一个<strong>声明式参数</strong>，而不是散落在业务逻辑里——危险操作（发布、删除、付款）默认就该 <code>always_require</code>，执行前框架自动暂停等确认。",
                    "en": "<code>ApprovalMode</code> is <code>Literal[&quot;always_require&quot;, &quot;never_require&quot;]</code>. It makes &quot;needs human review?&quot; a <strong>declarative parameter</strong> on the tool rather than scattered through business logic - risky actions (publish, delete, pay) should default to <code>always_require</code>, and the framework pauses for confirmation before running.",
                },
            },
        ],
        "open": [
            {
                "zh": "“普通 Python 函数 + 一个 <code>@tool</code> 装饰器”当工具，相比“专门的工具描述语言 / 配置文件”，在开发体验上有什么好处和潜在风险？（提示：docstring 或类型注解写得马虎会怎样？）",
                "en": "Using &quot;a plain Python function + one <code>@tool</code> decorator&quot; as a tool - versus a dedicated tool-description language / config file - what are the developer-experience upsides and the hidden risks? (Hint: what happens if the docstring or type hints are sloppy?)",
            },
        ],
    },
    "07-sessions-memory.html": {
        "mcq": [
            {
                "q": {
                    "zh": "MAF 的 <code>run()</code> 默认<strong>无状态</strong>（不传 <code>session</code> 就不记历史）。这样设计的主要好处是？",
                    "en": "MAF's <code>run()</code> is <strong>stateless</strong> by default (no <code>session</code> = no remembered history). The main benefit of that design?",
                },
                "opts": [
                    {
                        "zh": "并发安全 + 可测试：不同用户各自的 <code>session</code> 互不串、每个测试用例独立；需要状态时再显式传 <code>session</code>",
                        "en": "Concurrency-safe + testable: each user's <code>session</code> stays isolated, each test case is independent; pass a <code>session</code> explicitly only when you want state",
                    },
                    {"zh": "让模型变得更聪明", "en": "Makes the model smarter"},
                    {"zh": "节省磁盘空间", "en": "Saves disk space"},
                    {"zh": "强制每次对话都换一个模型", "en": "Forces a new model each conversation"},
                ],
                "answer": 0,
                "why": {
                    "zh": "隐式全局状态会让不同用户对话串台、测试难隔离、并发互相干扰。MAF 选“无状态为默认、显式 <code>session</code> 为可选”：<code>agent.create_session()</code> 后把同一个 <code>session</code> 透传给每次 <code>run()</code>，历史才会累积——有没有记忆一目了然。",
                    "en": "Implicit global state would cross users' chats, break test isolation, and let concurrent requests interfere. MAF chooses &quot;stateless by default, explicit <code>session</code> when wanted&quot;: call <code>agent.create_session()</code> then pass the same <code>session</code> into each <code>run()</code> for history to accumulate - making &quot;does it remember?&quot; obvious.",
                },
            },
            {
                "q": {
                    "zh": "会话（<code>AgentSession</code>）和 <code>ContextProvider</code> 各自负责什么？",
                    "en": "What does a session (<code>AgentSession</code>) handle vs a <code>ContextProvider</code>?",
                },
                "opts": [
                    {
                        "zh": "<code>session</code> 管“本轮对话内累积的历史”；<code>ContextProvider</code> 管“跨会话的长期记忆 / 每次 run 前注入的外部知识（RAG）”",
                        "en": "<code>session</code> handles &quot;history accumulated within this conversation&quot;; <code>ContextProvider</code> handles &quot;cross-session long-term memory / external knowledge injected before each run (RAG)&quot;",
                    },
                    {"zh": "两者完全一样", "en": "They are exactly the same"},
                    {"zh": "<code>session</code> 管工具、<code>ContextProvider</code> 管模型", "en": "<code>session</code> manages tools, <code>ContextProvider</code> manages the model"},
                    {"zh": "<code>ContextProvider</code> 负责训练模型", "en": "<code>ContextProvider</code> trains the model"},
                ],
                "answer": 0,
                "why": {
                    "zh": "会话只在“这串对话”内累积消息；要跨会话记住用户偏好、或在回答前把检索到的知识塞进上下文，用 <code>context_providers=[…]</code>（如 <code>MemoryContextProvider</code>）。注意 <code>HistoryProvider</code> 本身就是 <code>ContextProvider</code> 的子类——历史与长期记忆走同一套“run 前注入”机制。",
                    "en": "A session accumulates messages only within &quot;this conversation&quot;; to remember preferences across sessions or inject retrieved knowledge before answering, use <code>context_providers=[…]</code> (e.g. <code>MemoryContextProvider</code>). Note <code>HistoryProvider</code> is itself a subclass of <code>ContextProvider</code> - history and long-term memory share the same &quot;inject-before-run&quot; mechanism.",
                },
            },
        ],
        "open": [
            {
                "zh": "为什么“把记忆 / RAG 做成 <code>ContextProvider</code>、在 run 前自动注入”，通常比“每次 run 时手动把检索结果拼进 prompt”更好？请从<strong>可复用性</strong>和 <strong>Agent 代码整洁度</strong>两个角度谈谈。",
                "en": "Why is &quot;modeling memory / RAG as a <code>ContextProvider</code> that auto-injects before each run&quot; usually better than &quot;manually stitching retrieval results into the prompt on every run&quot;? Discuss from both <strong>reusability</strong> and <strong>Agent-code cleanliness</strong>.",
            },
        ],
    },
    "08-agent-internals.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在一次带工具的 <code>agent.run()</code> 里，反复&quot;调模型 → 执行工具 → 再调模型&quot;的循环实际发生在哪里？",
                    "en": "In a tool-using <code>agent.run()</code>, where does the repeated &quot;call model → run tool → call model&quot; loop actually happen?",
                },
                "opts": [
                    {"zh": "在 <code>Agent._parse_non_streaming_response()</code> 里", "en": "Inside <code>Agent._parse_non_streaming_response()</code>"},
                    {
                        "zh": "在 ChatClient 一侧的 <code>FunctionInvocationLayer</code>（<code>get_response</code> 内）",
                        "en": "In the ChatClient's <code>FunctionInvocationLayer</code> (inside <code>get_response</code>)",
                    },
                    {"zh": "在 <code>BaseAgent</code> 抽象基类里", "en": "In the <code>BaseAgent</code> abstract base class"},
                    {"zh": "在每个工具函数自己的代码里", "en": "Inside each tool function's own code"},
                ],
                "answer": 1,
                "why": {
                    "zh": "<code>Agent._call_chat_client()</code> 只调用一次 <code>client.get_response()</code>；多轮 function_call ↔ function_result 的循环在 ChatClient 的 <code>FunctionInvocationLayer</code> 内完成（上限 <code>DEFAULT_MAX_ITERATIONS=40</code>），所以 Agent 拿到的已是&quot;跑完工具后&quot;的最终 <code>ChatResponse</code>。",
                    "en": "<code>Agent._call_chat_client()</code> calls <code>client.get_response()</code> exactly once; the multi-turn function_call ↔ function_result loop runs inside the ChatClient's <code>FunctionInvocationLayer</code> (capped at <code>DEFAULT_MAX_ITERATIONS=40</code>), so the Agent receives an already-final <code>ChatResponse</code>.",
                },
            },
            {
                "q": {
                    "zh": "每一次模型调用本身是无状态的。那么&quot;模型记得它刚刚查过天气&quot;这种连续感，靠的是什么？",
                    "en": "Each model call is itself stateless. So what creates the continuity that &quot;the model remembers it just looked up the weather&quot;?",
                },
                "opts": [
                    {
                        "zh": "把上一轮的 function_call 与 function_result 追加进同一个不断变长的消息列表再发回去",
                        "en": "Appending the prior turn's function_call and function_result into the same growing message list and re-sending it",
                    },
                    {"zh": "模型内部有一块持久内存", "en": "The model keeps a block of persistent memory internally"},
                    {"zh": "Agent 把状态存进全局变量", "en": "The Agent stores state in a global variable"},
                    {"zh": "靠 <code>finish_reason</code> 字段携带历史", "en": "The <code>finish_reason</code> field carries the history"},
                ],
                "answer": 0,
                "why": {
                    "zh": "消息列表是唯一的状态载体：框架靠&quot;把每轮新内容追加进同一个 list 再整体发回&quot;制造连续感。注意循环内变长的是工作列表 <code>prepped_messages</code>，而 <code>AgentResponse.messages</code> 只含本轮新产生的消息。",
                    "en": "The message list is the only carrier of state: the framework fabricates continuity by appending each turn's new content into the same list and re-sending the whole thing. Note the growing list inside the loop is <code>prepped_messages</code>; <code>AgentResponse.messages</code> holds only newly produced messages.",
                },
            },
            {
                "q": {
                    "zh": "<code>Agent</code> 由 <code>AgentMiddlewareLayer + AgentTelemetryLayer + RawAgent</code> 三层多继承组合。相比&quot;一个类 + <code>enable_telemetry</code> 等运行时开关&quot;，这样做的核心好处是？",
                    "en": "<code>Agent</code> is composed by multiple-inheriting <code>AgentMiddlewareLayer + AgentTelemetryLayer + RawAgent</code>. Versus &quot;one class + runtime flags like <code>enable_telemetry</code>&quot;, what's the core benefit?",
                },
                "opts": [
                    {
                        "zh": "不想要的层根本不在 MRO 里——零运行时分支成本，且 <code>RawAgent</code> 与 <code>Agent</code> 对编排器完全互换",
                        "en": "Unwanted layers simply aren't in the MRO — zero runtime branch cost, and <code>RawAgent</code>/<code>Agent</code> stay interchangeable to orchestrators",
                    },
                    {"zh": "多继承让程序运行更快，因为绕过了 Python 解释器", "en": "Multiple inheritance runs faster by bypassing the Python interpreter"},
                    {"zh": "它能自动训练出更好的模型", "en": "It automatically trains a better model"},
                    {"zh": "它消除了对 ChatClient 的依赖", "en": "It removes the dependency on a ChatClient"},
                ],
                "answer": 0,
                "why": {
                    "zh": "功能的&quot;有/无&quot;在类定义期由 MRO 决定，而非运行时 <code>if</code> 跳过。要轻量就用 <code>RawAgent</code>（那两层不存在），要全功能就用 <code>Agent</code>；两者共享 <code>BaseAgent</code> 协议，调用方无需改动。",
                    "en": "A feature's presence/absence is decided at class-definition time by the MRO, not skipped by a runtime <code>if</code>. Use <code>RawAgent</code> for lightweight (those layers don't exist) or <code>Agent</code> for full features; both share the <code>BaseAgent</code> protocol so callers don't change.",
                },
            },
        ],
        "open": [
            {
                "zh": "<code>RawAgent.run()</code> 的三步骨架是&quot;准备上下文 → 调 ChatClient → 解析响应&quot;。如果让你在<strong>不联网、不烧 token</strong> 的前提下对 run 逻辑做单元测试，你会覆写哪一个方法、让它返回什么？这说明了把&quot;循环骨架&quot;和&quot;怎么调模型&quot;分开有什么测试上的好处？",
                "en": "<code>RawAgent.run()</code>'s three-step skeleton is &quot;prepare context → call ChatClient → parse response&quot;. To unit-test the run logic <strong>offline, without burning tokens</strong>, which single method would you override and what would it return? What testing benefit does separating the &quot;loop skeleton&quot; from &quot;how to call the model&quot; give you?",
            },
        ],
    },
    "09-chatclient-internals.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在 <code>BaseChatClient</code> 一侧，把厂商专属 JSON 翻译成统一 <code>ChatResponse</code> 这件事，到底发生在哪里？",
                    "en": "On the <code>BaseChatClient</code> side, where does the translation of vendor-specific JSON into a unified <code>ChatResponse</code> actually happen?",
                },
                "opts": [
                    {"zh": "在公共方法 <code>get_response()</code> 里统一处理", "en": "Handled centrally in the public <code>get_response()</code>"},
                    {
                        "zh": "在子类覆写的 <code>_inner_get_response()</code> 里（基类不碰任何厂商字段）",
                        "en": "Inside the subclass's overridden <code>_inner_get_response()</code> (the base touches no vendor field)",
                    },
                    {"zh": "在 <code>ChatOptions</code> 这个 TypedDict 里", "en": "Inside the <code>ChatOptions</code> TypedDict"},
                    {"zh": "在 Agent 的工具循环里", "en": "Inside the Agent's tool loop"},
                ],
                "answer": 1,
                "why": {
                    "zh": "基类 <code>get_response()</code>（<code>_clients.py:482</code>）只做&quot;压不压缩 + 转发&quot;的通用逻辑；把厂商 JSON 逐字段映射成 <code>ChatResponse</code> 的归一化，写在最懂那家 API 的子类 <code>_inner_get_response()</code> 里。所以新增厂商，基类一行都不用改。",
                    "en": "The base <code>get_response()</code> (<code>_clients.py:482</code>) only does the generic &quot;compact-or-not + forward&quot;; normalizing vendor JSON field-by-field into <code>ChatResponse</code> lives in the subclass <code>_inner_get_response()</code> that knows the API best. So adding a vendor changes not one line in the base.",
                },
            },
            {
                "q": {
                    "zh": "在<strong>一次</strong> <code>get_response()</code> 调用里，子类的 <code>_inner_get_response()</code> 会被调用几次？",
                    "en": "Within <strong>one</strong> <code>get_response()</code> call, how many times is the subclass's <code>_inner_get_response()</code> invoked?",
                },
                "opts": [
                    {"zh": "恰好一次——无论走「无压缩直接转发」还是「先 <code>_prepare</code> 再转发」", "en": "Exactly once — whether via &quot;forward as-is&quot; or &quot;_prepare then forward&quot;"},
                    {"zh": "每个工具调用一次，循环多次", "en": "Once per tool call, looping multiple times"},
                    {"zh": "流式时一次、非流式时两次", "en": "Once when streaming, twice when non-streaming"},
                    {"zh": "零次，由基类直接返回缓存", "en": "Zero times; the base returns a cache directly"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>get_response()</code> 的两条分支（<code>if not overrides</code> 直接转发；否则先 <code>_prepare_messages_for_model_call</code> 再转发）都<strong>只调一次</strong> <code>_inner_get_response()</code>。反复调模型的工具循环在外层的 <code>FunctionInvocationLayer</code>，不在基类。",
                    "en": "Both branches of <code>get_response()</code> (the <code>if not overrides</code> direct forward, or <code>_prepare_messages_for_model_call</code> then forward) call <code>_inner_get_response()</code> <strong>exactly once</strong>. The repeated model calls of the tool loop live in the outer <code>FunctionInvocationLayer</code>, not the base.",
                },
            },
            {
                "q": {
                    "zh": "OpenAI 原始 JSON 里的 <code>usage.prompt_tokens</code>，归一化进统一 <code>UsageDetails</code> 后叫什么？",
                    "en": "OpenAI raw JSON's <code>usage.prompt_tokens</code> becomes which field after normalization into the unified <code>UsageDetails</code>?",
                },
                "opts": [
                    {"zh": "<code>input_token_count</code>", "en": "<code>input_token_count</code>"},
                    {"zh": "原样保留 <code>prompt_tokens</code>", "en": "Kept as-is: <code>prompt_tokens</code>"},
                    {"zh": "<code>output_token_count</code>", "en": "<code>output_token_count</code>"},
                    {"zh": "<code>completion_tokens</code>", "en": "<code>completion_tokens</code>"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>UsageDetails</code>（<code>_types.py:393</code>）统一用 <code>input_token_count</code> / <code>output_token_count</code> / <code>total_token_count</code>。这个<strong>改名</strong>正是归一化的意义：上层只认框架字段，不被某家厂商的命名绑死。",
                    "en": "<code>UsageDetails</code> (<code>_types.py:393</code>) uses the unified <code>input_token_count</code> / <code>output_token_count</code> / <code>total_token_count</code>. This <strong>rename</strong> is the whole point of normalization: upper layers know only the framework's fields, not any one vendor's naming.",
                },
            },
        ],
        "open": [
            {
                "zh": "既然每家 API 返回的 JSON 都不同，为什么子类还要多写一道&quot;翻译&quot;、把结果统一成 <code>ChatResponse</code>，而不是把厂商 dict 直接透传给上层？请从&quot;换厂商时谁要改代码&quot;的角度说明，并解释 <code>raw_representation</code> 在这个设计里扮演什么角色。",
                "en": "Since every API returns different JSON, why does the subclass write an extra &quot;translation&quot; to unify into <code>ChatResponse</code> instead of passing the vendor dict straight through? Argue from &quot;who must change code when you swap vendors&quot;, and explain the role <code>raw_representation</code> plays in this design.",
            },
        ],
    },
    "10-tool-internals.html": {
        "mcq": [
            {
                "q": {
                    "zh": "一个 <code>@tool</code> 函数发给模型的 JSON Schema 是从哪来的？",
                    "en": "Where does the JSON Schema sent to the model for a <code>@tool</code> function come from?",
                },
                "opts": [
                    {"zh": "你必须手写一份 schema 字典传给 <code>@tool</code>", "en": "You must hand-write a schema dict and pass it to <code>@tool</code>"},
                    {
                        "zh": "由函数签名自动生成：<code>create_model</code> 造 Pydantic 模型 → <code>model_json_schema()</code>",
                        "en": "Auto-generated from the signature: <code>create_model</code> builds a Pydantic model → <code>model_json_schema()</code>",
                    },
                    {"zh": "模型自己猜测函数的参数", "en": "The model guesses the function's parameters itself"},
                    {"zh": "从函数运行时的第一次调用里采样得到", "en": "Sampled from the first runtime call of the function"},
                ],
                "answer": 1,
                "why": {
                    "zh": "<code>_resolve_input_model()</code>（<code>_tools.py:481</code>）用 <code>inspect.signature</code> 读签名、<code>create_model</code> 造 Pydantic 模型，<code>model_json_schema()</code>（<code>:780</code>）直接吐出 schema，<code>to_json_schema_spec()</code>（<code>:866</code>）再套上 function 外壳。框架一行 schema 都没手写。也可用 <code>@tool(schema=…)</code> 显式覆盖。",
                    "en": "<code>_resolve_input_model()</code> (<code>_tools.py:481</code>) reads the signature via <code>inspect.signature</code>, <code>create_model</code> builds a Pydantic model, <code>model_json_schema()</code> (<code>:780</code>) emits the schema, and <code>to_json_schema_spec()</code> (<code>:866</code>) wraps the function shell. The framework hand-writes no schema. You can still override via <code>@tool(schema=…)</code>.",
                },
            },
            {
                "q": {
                    "zh": "一个<strong>没有默认值</strong>的参数（如 <code>city: str</code>），在生成的 schema 里会怎样？",
                    "en": "A parameter with <strong>no default value</strong> (e.g. <code>city: str</code>) ends up how in the generated schema?",
                },
                "opts": [
                    {"zh": "被放进 <code>required</code> 列表", "en": "Placed into the <code>required</code> list"},
                    {"zh": "被忽略，不出现在 schema 里", "en": "Ignored — it doesn't appear in the schema"},
                    {"zh": "自动获得 <code>null</code> 默认值", "en": "Automatically given a <code>null</code> default"},
                    {"zh": "被标成 <code>readOnly</code>", "en": "Marked as <code>readOnly</code>"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>_resolve_input_model</code> 给无默认值的参数填入 <code>...</code>（Pydantic 的&quot;必填&quot;哨兵），于是 Pydantic 自动把它放进 schema 的 <code>required</code>；有默认值的参数（如 <code>unit=&quot;celsius&quot;</code>）则进 <code>default</code>、不必填。",
                    "en": "<code>_resolve_input_model</code> assigns <code>...</code> (Pydantic's &quot;required&quot; sentinel) to params without a default, so Pydantic auto-places them in the schema's <code>required</code>; params with a default (e.g. <code>unit=&quot;celsius&quot;</code>) go into <code>default</code> and are optional.",
                },
            },
            {
                "q": {
                    "zh": "<code>@tool</code> 从你的函数签名造出的<strong>同一个</strong> Pydantic 模型，同时承担了哪两件事？",
                    "en": "The <strong>single</strong> Pydantic model <code>@tool</code> builds from your signature does which two jobs at once?",
                },
                "opts": [
                    {
                        "zh": "对外生成 schema 描述参数；对内校验模型传回的 arguments",
                        "en": "Outward: emit the schema describing params; inward: validate the arguments the model returns",
                    },
                    {"zh": "训练模型，并缓存模型的回复", "en": "Train the model, and cache its replies"},
                    {"zh": "压缩消息，并加密参数", "en": "Compact messages, and encrypt arguments"},
                    {"zh": "管理网络重试，并记录遥测", "en": "Manage network retries, and record telemetry"},
                ],
                "answer": 0,
                "why": {
                    "zh": "一次 <code>create_model</code> 身兼两职：作为 schema 向模型描述参数（第②步），作为校验器在执行前给 <code>arguments</code> 把关（第⑤步）。正因来自同一处签名，&quot;描述&quot;与&quot;校验&quot;永远一致——这就是&quot;签名即契约&quot;，连校验逻辑都不必另写。",
                    "en": "One <code>create_model</code> serves twice: as the schema describing params to the model (step ②), and as the validator guarding <code>arguments</code> before execution (step ⑤). Because both come from the one signature, &quot;describe&quot; and &quot;validate&quot; always agree — &quot;signature as contract&quot;, with validation logic free.",
                },
            },
        ],
        "open": [
            {
                "zh": "&quot;手写函数 + 手写 JSON Schema&quot;这种两份独立维护的写法，最典型的 bug 是什么？请用一个具体场景说明，并解释 MAF 的&quot;单一事实来源&quot;（从签名派生 schema）如何根除它、又付出了什么代价（提示：<code>@tool(schema=…)</code>）。",
                "en": "What is the most typical bug of the &quot;hand-write the function + hand-write the JSON Schema&quot; two-copies approach? Give a concrete scenario, then explain how MAF's &quot;single source of truth&quot; (deriving the schema from the signature) eliminates it — and what it costs (hint: <code>@tool(schema=…)</code>).",
            },
        ],
    },
    "11-middleware.html": {
        "mcq": [
            {
                "q": {
                    "zh": "一次 Agent 运行里发生了 <strong>2 次 LLM 调用 + 1 次工具执行</strong>，三层中间件的 <code>process()</code> 各跑几次？",
                    "en": "In one agent run with <strong>2 LLM calls + 1 tool execution</strong>, how many times does each of the three middleware layers' <code>process()</code> run?",
                },
                "opts": [
                    {
                        "zh": "AgentMiddleware 1 次、ChatMiddleware 2 次、FunctionMiddleware 1 次",
                        "en": "AgentMiddleware 1×, ChatMiddleware 2×, FunctionMiddleware 1×",
                    },
                    {"zh": "三层都只跑 1 次", "en": "All three run exactly once"},
                    {"zh": "三层都跑 3 次（2+1）", "en": "All three run 3× (2+1)"},
                    {"zh": "AgentMiddleware 跟着每次 LLM 调用跑 2 次", "en": "AgentMiddleware runs 2× — once per LLM call"},
                ],
                "answer": 0,
                "why": {
                    "zh": "三层的<strong>粒度互相独立</strong>：<code>AgentMiddleware</code> 包整次运行（1 次）、<code>ChatMiddleware</code> 包每次 LLM 调用（2 次）、<code>FunctionMiddleware</code> 包每次工具执行（1 次）。这正是&quot;三粒度&quot;的意义——你能只拦 LLM 调用而不碰工具，反之亦然。",
                    "en": "The three granularities are <strong>independent</strong>: <code>AgentMiddleware</code> wraps the whole run (1×), <code>ChatMiddleware</code> wraps each LLM call (2×), <code>FunctionMiddleware</code> wraps each tool execution (1×). That's the point of &quot;three granularities&quot; — you can intercept LLM calls without touching tools, and vice-versa.",
                },
            },
            {
                "q": {
                    "zh": "MAF 中间件里的 <code>await call_next()</code> 有什么特别之处？",
                    "en": "What is special about <code>await call_next()</code> in a MAF middleware?",
                },
                "opts": [
                    {
                        "zh": "它<strong>不收参数、也不返回值</strong>；结果走共享的 <code>context</code>（如 <code>context.result</code>）",
                        "en": "It takes <strong>no args and returns nothing</strong>; the result flows via the shared <code>context</code> (e.g. <code>context.result</code>)",
                    },
                    {"zh": "必须把请求传进去：<code>call_next(request)</code>", "en": "You must pass the request in: <code>call_next(request)</code>"},
                    {
                        "zh": "它返回 <code>ChatResponse</code>，你得从 <code>process()</code> 把它 return 出去",
                        "en": "It returns the <code>ChatResponse</code>, which you must return from <code>process()</code>",
                    },
                    {"zh": "只有 <code>AgentMiddleware</code> 能调用它", "en": "Only <code>AgentMiddleware</code> may call it"},
                ],
                "answer": 0,
                "why": {
                    "zh": "签名统一为 <code>process(self, context, call_next)</code>，<code>call_next</code> 无参、返回 <code>None</code>；一切数据都挂在共享 <code>context</code> 上（最内层的 <code>final_wrapper</code> 把真正结果写进 <code>context.result</code>，见 <code>_middleware.py:880</code>）。正因如此，三种中间件的签名才能完全一致。",
                    "en": "The unified signature is <code>process(self, context, call_next)</code>; <code>call_next</code> is no-arg and returns <code>None</code>. All data rides on the shared <code>context</code> (the innermost <code>final_wrapper</code> writes the real result into <code>context.result</code>, see <code>_middleware.py:880</code>). That's exactly why all three middleware signatures can be identical.",
                },
            },
            {
                "q": {
                    "zh": "一个中间件想<strong>短路</strong>，让昂贵的内层 LLM/工具执行根本不发生，怎么做？",
                    "en": "How does a middleware <strong>short-circuit</strong> so the expensive inner LLM/tool execution never happens?",
                },
                "opts": [
                    {
                        "zh": "不调用 <code>call_next()</code>（可顺手设 <code>context.result</code>），或在它之前 <code>raise MiddlewareTermination</code>",
                        "en": "Don't call <code>call_next()</code> (optionally set <code>context.result</code>), or <code>raise MiddlewareTermination</code> before it",
                    },
                    {"zh": "从 <code>process()</code> 返回 <code>False</code>", "en": "Return <code>False</code> from <code>process()</code>"},
                    {"zh": "调用 <code>context.cancel()</code>", "en": "Call <code>context.cancel()</code>"},
                    {"zh": "<code>raise StopIteration</code>", "en": "<code>raise StopIteration</code>"},
                ],
                "answer": 0,
                "why": {
                    "zh": "内层整体只在你 <code>await call_next()</code> 时才运行——不调用它即短路（常顺手把 <code>context.result</code> 设成缓存值）。或 <code>raise MiddlewareTermination</code>（<code>_middleware.py:72</code>），<code>execute()</code> 用 <code>contextlib.suppress</code> 吞掉它、跳过余下阶段。框架内部正是这样用：<code>raise MiddlewareTermination(&quot;Validation failed&quot;)</code>（<code>_middleware.py:238</code>）。",
                    "en": "The inner whole only runs when you <code>await call_next()</code> — skip it to short-circuit (often setting <code>context.result</code> to a cached value). Or <code>raise MiddlewareTermination</code> (<code>_middleware.py:72</code>), which <code>execute()</code> swallows via <code>contextlib.suppress</code>, skipping remaining stages. The framework does exactly this internally: <code>raise MiddlewareTermination(&quot;Validation failed&quot;)</code> (<code>_middleware.py:238</code>).",
                },
            },
        ],
        "open": [
            {
                "zh": "把<strong>洋葱模型</strong>（无参 <code>await call_next()</code>）和 Express 式的<strong>线性回调链</strong>对比一下：把&quot;内层整体&quot;当成一等可 await 对象，解锁了线性 <code>next()</code> 很难做的哪些控制流？请分别给出&quot;短路&quot;、&quot;<code>try/finally</code> 清理&quot;、&quot;重试&quot;各一个具体例子。",
                "en": "Contrast the <strong>onion model</strong> (no-arg <code>await call_next()</code>) with an Express-style <strong>linear callback list</strong>. Treating &quot;the inner whole&quot; as a first-class awaitable unlocks which control flows that a linear <code>next()</code> makes awkward? Give one concrete example each for short-circuit, <code>try/finally</code> cleanup, and retry.",
            },
        ],
    },
    "12-workflows.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在 <code>writer → reviewer</code> 图里，<code>writer</code> 调了 <code>ctx.send_message(draft)</code> 之后，<code>reviewer</code> 什么时候才第一次被唤起？",
                    "en": "In the <code>writer → reviewer</code> graph, after <code>writer</code> calls <code>ctx.send_message(draft)</code>, when is <code>reviewer</code> first invoked?",
                },
                "opts": [
                    {
                        "zh": "在<strong>下一个超步</strong>——消息要等本超步结束、在边界统一投递后才送达",
                        "en": "On the <strong>next superstep</strong> — the message is delivered only at the boundary after this superstep ends",
                    },
                    {"zh": "在 <code>send_message</code> 那一行<strong>同步</strong>立即调用", "en": "<strong>Synchronously</strong>, right on the <code>send_message</code> line"},
                    {"zh": "只有当你显式调用 <code>reviewer.run()</code> 时", "en": "Only when you explicitly call <code>reviewer.run()</code>"},
                    {"zh": "永远不会——<code>send_message</code> 只是写日志", "en": "Never — <code>send_message</code> only writes a log"},
                ],
                "answer": 0,
                "why": {
                    "zh": "Workflow 是 Pregel 式<strong>超步</strong>引擎：<code>send_message</code> 把消息缓冲到边上，引擎在<strong>超步边界</strong>统一投递并存检查点，下游节点要到下一超步才被唤起。这正是同一超步里多个节点能安全并行的前提（它们看不到彼此本步的输出）。",
                    "en": "A Workflow is a Pregel-style <strong>superstep</strong> engine: <code>send_message</code> buffers the message on the edge, the engine delivers everything at the <strong>superstep boundary</strong> (and checkpoints), and the downstream node is invoked only on the next superstep. That's exactly why nodes in one superstep can parallelize safely — they can't see each other's output from that step.",
                },
            },
            {
                "q": {
                    "zh": "与第 8 课的<strong>单 Agent 工具循环</strong>相比，Workflow 图最核心的额外能力来自哪里？",
                    "en": "Compared with the <strong>single-agent tool loop</strong> from Lesson 8, where does a Workflow graph's most essential extra power come from?",
                },
                "opts": [
                    {
                        "zh": "每个超步边界都<strong>存检查点</strong>，于是可恢复、可并发、可暂停等人工输入",
                        "en": "It <strong>checkpoints</strong> at every superstep boundary — so it's resumable, concurrent, and can pause for human input",
                    },
                    {"zh": "它换用了更快的模型", "en": "It swaps in a faster model"},
                    {"zh": "它把消息列表压缩得更小", "en": "It compresses the message list smaller"},
                    {"zh": "它去掉了对 ChatClient 的依赖", "en": "It removes the dependency on a ChatClient"},
                ],
                "answer": 0,
                "why": {
                    "zh": "单 Agent 循环把状态全放在一个内存消息列表里：简单、低延迟，但<strong>崩溃即丢失</strong>、天然串行。图把状态显式化为节点+边+超步，在边界存档——这才解锁了断点续跑、fan-out 并发、以及 <code>ctx.request_info()</code> 这类人在环暂停。代价是你得先把流程画成图。",
                    "en": "The single-agent loop keeps all state in one in-memory message list: simple and low-latency, but <strong>lost on crash</strong> and inherently serial. The graph makes state explicit as nodes+edges+supersteps and checkpoints at boundaries — unlocking resume-after-crash, fan-out concurrency, and human-in-the-loop pauses via <code>ctx.request_info()</code>. The cost is having to draw the flow first.",
                },
            },
            {
                "q": {
                    "zh": "<code>WorkflowBuilder(...).add_edge(a, b).build()</code> 里，<code>build()</code> 主要负责什么？",
                    "en": "In <code>WorkflowBuilder(...).add_edge(a, b).build()</code>, what is <code>build()</code> mainly responsible for?",
                },
                "opts": [
                    {
                        "zh": "<strong>构建期校验</strong>（起始节点已设、图连通、相邻类型兼容）并返回<strong>不可变</strong>的 <code>Workflow</code>",
                        "en": "<strong>Build-time validation</strong> (start set, graph connected, adjacent types compatible) and returning an <strong>immutable</strong> <code>Workflow</code>",
                    },
                    {"zh": "真正运行图、把结果打印出来", "en": "Actually running the graph and printing the result"},
                    {"zh": "训练一个新模型", "en": "Training a new model"},
                    {"zh": "把所有节点合并成一个大函数", "en": "Merging all nodes into one big function"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>build()</code>（<code>_workflow_builder.py:725</code>）把校验放在<strong>构建期</strong>：类型不兼容、图不连通会立刻抛 <code>WorkflowValidationError</code>，而不是等你 <code>run()</code> 到一半才炸。它返回一个不可变 <code>Workflow</code>，可被重复 <code>run()</code>。注意起始节点是构造器参数 <code>start_executor=</code>，并没有 <code>set_start_executor()</code> 方法。",
                    "en": "<code>build()</code> (<code>_workflow_builder.py:725</code>) puts validation at <strong>build time</strong>: incompatible types or a disconnected graph raise <code>WorkflowValidationError</code> immediately, instead of blowing up halfway through <code>run()</code>. It returns an immutable <code>Workflow</code> you can <code>run()</code> repeatedly. Note the start node is the constructor arg <code>start_executor=</code>; there is no <code>set_start_executor()</code> method.",
                },
            },
        ],
        "open": [
            {
                "zh": "设计一张<strong>三节点</strong> fan-out/fan-in 图：<code>splitter</code> 把任务分给 <code>worker_a</code> 和 <code>worker_b</code> 并行处理，再由 <code>merger</code> 汇总。请数一数这张图至少需要几个超步、<code>worker_a/worker_b</code> 会在<strong>同一个超步</strong>被唤起吗，以及如果 <code>worker_b</code> 中途崩溃，引擎能从哪个超步恢复？",
                "en": "Design a <strong>three-node</strong> fan-out/fan-in graph: <code>splitter</code> dispatches work to <code>worker_a</code> and <code>worker_b</code> in parallel, then <code>merger</code> aggregates. Count how many supersteps this needs at minimum, decide whether <code>worker_a/worker_b</code> are invoked in the <strong>same superstep</strong>, and reason about which superstep the engine could resume from if <code>worker_b</code> crashes midway.",
            },
        ],
    },
    "13-orchestration.html": {
        "mcq": [
            {
                "q": {
                    "zh": "Handoff 和 Group Chat 都能多 Agent 协作，二者最本质的区别是<strong>谁决定下一个发言者</strong>。它是怎么分的？",
                    "en": "Handoff and Group Chat both enable multi-agent collaboration; the most essential difference is <strong>who decides the next speaker</strong>. How does it split?",
                },
                "opts": [
                    {
                        "zh": "Handoff 由<strong>当前 Agent</strong> 自己调 handoff 工具决定交给谁；Group Chat 由一个<strong>集中的 <code>selection_func</code></strong> 每轮挑人",
                        "en": "Handoff lets the <strong>current Agent</strong> decide via a handoff tool; Group Chat uses a <strong>centralized <code>selection_func</code></strong> to pick each turn",
                    },
                    {"zh": "两者都由固定轮转顺序决定，没有区别", "en": "Both decide by a fixed round-robin order; there's no difference"},
                    {"zh": "两者都必须由人类每轮手动指定下一个", "en": "Both require a human to name the next speaker every turn"},
                    {"zh": "Handoff 用 <code>selection_func</code>，Group Chat 靠当前 Agent 自己交接", "en": "Handoff uses <code>selection_func</code>; Group Chat relies on the current Agent to hand off"},
                ],
                "answer": 0,
                "why": {
                    "zh": "Handoff 把决策权下放给当前 Agent——它通过一个名为 <code>handoff_to_&lt;target&gt;</code> 的工具（<code>_handoff.py:122</code>）把控制权转走，最灵活也最难预测；Group Chat 则把'谁说话'收回到一个 <code>selection_func</code>（<code>_group_chat.py:615</code>）集中决定，更可控。",
                    "en": "Handoff delegates the decision to the current Agent — it transfers control via a tool named <code>handoff_to_&lt;target&gt;</code> (<code>_handoff.py:122</code>), the most flexible but least predictable; Group Chat pulls 'who talks' back into a single <code>selection_func</code> (<code>_group_chat.py:615</code>), more controllable.",
                },
            },
            {
                "q": {
                    "zh": "你要让三个 Agent <strong>各自独立</strong>地从不同角度审一份合同，再汇总成一份报告，且希望<strong>总延迟 ≈ 最慢的那个</strong>而不是三者之和。该选哪种编排？",
                    "en": "You want three Agents to review a contract <strong>independently</strong> from different angles, then aggregate into one report, with <strong>total latency ≈ the slowest one</strong> rather than the sum. Which orchestration?",
                },
                "opts": [
                    {
                        "zh": "<strong>Concurrent</strong>（并发）——唯一真并行，延迟压到各 Agent 之最大",
                        "en": "<strong>Concurrent</strong> — the only truly parallel one, collapsing latency to the max of the agents",
                    },
                    {"zh": "Sequential（顺序）——一个接一个传递", "en": "Sequential — pass one after another"},
                    {"zh": "Handoff——让第一个 Agent 决定交给谁", "en": "Handoff — let the first Agent decide whom to pass to"},
                    {"zh": "Magentic——派一个指挥官逐轮调度", "en": "Magentic — assign a manager to schedule round by round"},
                ],
                "answer": 0,
                "why": {
                    "zh": "任务之间<strong>无依赖</strong>且要压低延迟，正是 Concurrent 的主场：它把同一输入 fan-out 给多个 Agent 并行跑，再用 aggregator 汇总（<code>_concurrent.py:267</code>）。Sequential/Handoff/Magentic 本质串行，总耗时是各步之和。",
                    "en": "Independent subtasks plus a latency target is Concurrent's home turf: it fans the same input out to multiple Agents in parallel, then merges via an aggregator (<code>_concurrent.py:267</code>). Sequential/Handoff/Magentic advance serially, so total time is the sum of steps.",
                },
            },
            {
                "q": {
                    "zh": "Magentic 的指挥官凭什么不会把多 Agent 协作变成'放养式群聊'？",
                    "en": "What keeps Magentic's manager from turning multi-agent collaboration into a 'free-for-all group chat'?",
                },
                "opts": [
                    {
                        "zh": "每轮都让 LLM 填一张<strong>进度账本</strong>（完成？打转？有进展？下一个谁？给什么指令？），据此显式自检与调度",
                        "en": "Each round it has the LLM fill a <strong>progress ledger</strong> (done? looping? progressing? who's next? what instruction?) and schedules from that explicit self-check",
                    },
                    {"zh": "它把所有 Agent 锁成固定轮转顺序", "en": "It locks all Agents into a fixed round-robin order"},
                    {"zh": "它只允许一个 Agent 存在", "en": "It allows only one Agent to exist"},
                    {"zh": "它随机选择下一个发言者", "en": "It picks the next speaker at random"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>MagenticProgressLedger</code>（<code>_magentic.py:307</code>）有五个字段：<code>is_request_satisfied / is_in_loop / is_progress_being_made / next_speaker / instruction_or_question</code>。指挥官每轮让 LLM 以结构化输出填它，于是显式判断该收尾、该重置还是该派谁干；卡住超过 <code>max_stall_count</code>（默认 3）就重置计划。",
                    "en": "<code>MagenticProgressLedger</code> (<code>_magentic.py:307</code>) has five fields: <code>is_request_satisfied / is_in_loop / is_progress_being_made / next_speaker / instruction_or_question</code>. The manager has the LLM fill it as structured output each round, so it explicitly decides to finalize, reset, or dispatch; exceeding <code>max_stall_count</code> (default 3) resets the plan.",
                },
            },
        ],
        "open": [
            {
                "zh": "用 <strong>Handoff</strong> 设计一个客服分流系统：一个 <code>triage</code> 入口 Agent，外加 <code>billing</code>（账单）和 <code>tech</code>（技术）两个专家。请说明：(1) 哪个是 <code>with_start_agent</code> 起点；(2) 至少需要哪几条 <code>add_handoff</code> 边、方向如何；(3) 当两个专家都无法解决时，你会在何处用 <code>ctx.request_info()</code> 升级给人工，以及为什么 Handoff 比让单个大 Agent 硬扛更合适？",
                "en": "Design a customer-service triage with <strong>Handoff</strong>: a <code>triage</code> entry Agent plus two experts <code>billing</code> and <code>tech</code>. Explain: (1) which is the <code>with_start_agent</code> start; (2) which <code>add_handoff</code> edges you need at minimum and their direction; (3) where you'd escalate to a human via <code>ctx.request_info()</code> when neither expert can resolve it, and why Handoff fits better than forcing one giant Agent to do it all.",
            },
        ],
    },
    "14-streaming-observability.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在那次“巴黎天气”的流式追踪里，<strong>最前面几个 chunk 的 <code>.text</code> 是空的</strong>。最贴切的原因是？",
                    "en": "In that “Paris weather” streaming trace, the <strong>first few chunks have empty <code>.text</code></strong>. The most accurate reason is?",
                },
                "opts": [
                    {
                        "zh": "模型先决定<strong>调工具</strong>（<code>finish_reason=&quot;tool_calls&quot;</code>），可显示的文本增量要等工具返回后才来",
                        "en": "The model first decides to <strong>call a tool</strong> (<code>finish_reason=&quot;tool_calls&quot;</code>); displayable text deltas only arrive after the tool returns",
                    },
                    {"zh": "流式坏了，应该重试", "en": "Streaming is broken and should be retried"},
                    {"zh": "网络太慢把文本丢了", "en": "The network was too slow and dropped the text"},
                    {"zh": "<code>.text</code> 永远是空的，要读 <code>.raw</code>", "en": "<code>.text</code> is always empty; you must read <code>.raw</code>"},
                ],
                "answer": 0,
                "why": {
                    "zh": "首批 chunk 携带的是一个 <code>FunctionCallContent</code> 而非文本，<code>finish_reason</code> 收为 <code>&quot;tool_calls&quot;</code>；框架执行工具（开 <code>execute_tool</code> span）后，带着结果再问模型，第二个 <code>chat</code> span 里才逐字吐出文本、<code>finish_reason=None</code>，直到最后翻成 <code>&quot;stop&quot;</code>。所以“前几秒没字”是正常现象，不是卡死。",
                    "en": "The first chunks carry a <code>FunctionCallContent</code>, not text, and <code>finish_reason</code> ends as <code>&quot;tool_calls&quot;</code>; after the framework runs the tool (opening an <code>execute_tool</code> span) and asks the model again with the result, the second <code>chat</code> span emits text token by token with <code>finish_reason=None</code>, until it finally flips to <code>&quot;stop&quot;</code>. So “no text for the first seconds” is expected, not a hang.",
                },
            },
            {
                "q": {
                    "zh": "MAF 里每个 span 的真实名字是 <code>f&quot;{operation} {target}&quot;</code>。一次 <strong>LLM 调用</strong>对应的 span 名是？",
                    "en": "In MAF each span's real name is <code>f&quot;{operation} {target}&quot;</code>. The span for one <strong>LLM call</strong> is named?",
                },
                "opts": [
                    {"zh": "<code>chat {model}</code>（<code>CHAT_COMPLETION_OPERATION=&quot;chat&quot;</code>）", "en": "<code>chat {model}</code> (<code>CHAT_COMPLETION_OPERATION=&quot;chat&quot;</code>)"},
                    {"zh": "<code>llm.call</code>", "en": "<code>llm.call</code>"},
                    {"zh": "<code>openai.request</code>", "en": "<code>openai.request</code>"},
                    {"zh": "<code>agent.think</code>", "en": "<code>agent.think</code>"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>observability.py:2112</code> 用 <code>f&quot;{operation} {span_name}&quot;</code> 组名：根 span 是 <code>invoke_agent {agent}</code>，每次 LLM 调用是 <code>chat {model}</code>，每次工具是 <code>execute_tool {name}</code>；Workflow 侧则是 <code>workflow.run</code> / <code>executor.process {id}</code> / <code>message.send</code>。这些都是 GenAI 语义约定下的标准名。",
                    "en": "<code>observability.py:2112</code> builds names via <code>f&quot;{operation} {span_name}&quot;</code>: the root is <code>invoke_agent {agent}</code>, each LLM call is <code>chat {model}</code>, each tool is <code>execute_tool {name}</code>; the Workflow side is <code>workflow.run</code> / <code>executor.process {id}</code> / <code>message.send</code>. These follow the GenAI semantic conventions.",
                },
            },
            {
                "q": {
                    "zh": "Workflow 的 <code>executor.process</code> span 对它的上游<strong>用 link 关联</strong>而不是<strong>嵌套</strong>。为什么这样设计？",
                    "en": "A Workflow's <code>executor.process</code> span <strong>links</strong> to its upstream instead of <strong>nesting</strong> under it. Why?",
                },
                "opts": [
                    {
                        "zh": "一个节点可能<strong>同时</strong>收到多个上游消息（fan-in）；link 能指向多个源，嵌套只能挂一个父亲",
                        "en": "A node may receive messages from <strong>several</strong> upstream nodes at once (fan-in); a link can point at multiple sources, while nesting allows only one parent",
                    },
                    {"zh": "link 比嵌套省内存", "en": "Links use less memory than nesting"},
                    {"zh": "嵌套在 OTel 里不被允许", "en": "Nesting is not allowed in OTel"},
                    {"zh": "纯粹是历史遗留，没有道理", "en": "It's purely legacy with no real reason"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>observability.py:2454</code> 注释明说 span 是“linked (not nested) ... supporting fan-in”。因为 Workflow 按超步并行推进，扇入节点会从多个源同时拿到消息；用 link 才能<strong>同时保留对所有源的因果指向</strong>，嵌套则被迫只选一个父 span，丢掉其余扇入边的因果。",
                    "en": "<code>observability.py:2454</code>'s comment says spans are “linked (not nested) ... supporting fan-in”. Because a Workflow advances in parallel supersteps, a fan-in node gets messages from multiple sources at once; a link <strong>preserves causal pointers to all sources simultaneously</strong>, whereas nesting would force picking one parent and lose the other fan-in edges' causality.",
                },
            },
        ],
        "open": [
            {
                "zh": "一次 workflow 跑了 8 秒、还超了 token 预算。请描述你会怎么用<strong>分层 span</strong> 定位问题：(1) 从 <code>workflow.run</code> / <code>executor.process {id}</code> 哪些 span 的耗时入手找最慢节点；(2) 再下钻到 <code>chat {model}</code> span 的 <code>gen_ai.usage.input_tokens / output_tokens</code> 判断是哪个 Agent 烧的 token；(3) 为什么这件事如果没有内置 OTel 会非常难做？",
                "en": "A workflow run took 8s and blew the token budget. Describe how you'd use <strong>layered spans</strong> to localize it: (1) which <code>workflow.run</code> / <code>executor.process {id}</code> span durations you'd start from to find the slowest node; (2) how you'd drill into <code>chat {model}</code> spans' <code>gen_ai.usage.input_tokens / output_tokens</code> to see which Agent burned the tokens; (3) why this would be very hard without built-in OTel.",
            },
        ],
    },
    "15-contributing.html": {
        "mcq": [
            {
                "q": {
                    "zh": "为什么 MAF 让<strong>本地开发</strong>和 <strong>CI</strong> 都通过同一套 <code>uv run poe &lt;task&gt;</code> 命令跑质量门？",
                    "en": "Why does MAF run quality gates through the same <code>uv run poe &lt;task&gt;</code> commands both <strong>locally</strong> and in <strong>CI</strong>?",
                },
                "opts": [
                    {
                        "zh": "任务定义在 <code>pyproject.toml</code> 里、本地与 CI 完全一致——“本地全绿”基本等于“CI 大概率绿”，新人也只需记几条命令",
                        "en": "Tasks live in <code>pyproject.toml</code> and are identical locally and in CI - so &quot;green locally&quot; basically means &quot;green in CI&quot;, and newcomers only memorize a few commands",
                    },
                    {
                        "zh": "因为 poe 能让被测代码运行得更快",
                        "en": "Because poe makes the code under test run faster",
                    },
                    {
                        "zh": "因为 CI 环境里不能直接调用 pytest",
                        "en": "Because pytest cannot be invoked directly in CI",
                    },
                    {
                        "zh": "因为 uv 本身不支持运行测试",
                        "en": "Because uv itself cannot run tests",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "poe（poethepoet）把每个质量门定义成 <code>[tool.poe.tasks]</code> 里的一条命令，本地和 CI 跑<strong>完全相同</strong>的东西——可复现、低心智负担。<code>poe lint</code> / <code>poe typing</code> / <code>poe test</code> 一条对应一个门。",
                    "en": "poe (poethepoet) defines each gate as a command under <code>[tool.poe.tasks]</code>, so local and CI run the <strong>exact same</strong> thing - reproducible and low cognitive load. <code>poe lint</code> / <code>poe typing</code> / <code>poe test</code> map one-to-one to gates.",
                },
            },
            {
                "q": {
                    "zh": "MAF 用 <code>uv sync</code>（带 <code>uv.lock</code> 的 workspace）来装依赖，而不是一堆 <code>pip install -r requirements.txt</code>，主要因为？",
                    "en": "MAF installs deps with <code>uv sync</code> (a workspace backed by <code>uv.lock</code>) instead of several <code>pip install -r requirements.txt</code>. Mainly because?",
                },
                "opts": [
                    {
                        "zh": "锁定文件能精确锁住每个传递依赖、保证可复现，workspace 模式还能一条命令原子装好整个 monorepo 的多个包",
                        "en": "The lockfile pins every transitive dependency for reproducibility, and workspace mode atomically installs all packages of the monorepo in one command",
                    },
                    {
                        "zh": "uv 会在装依赖时顺便帮你写好代码",
                        "en": "uv writes your code for you while installing",
                    },
                    {
                        "zh": "因为 pip 在所有系统上都已被禁用",
                        "en": "Because pip is disabled on all systems",
                    },
                    {
                        "zh": "因为 uv 一次只能装一个包，更安全",
                        "en": "Because uv can only install one package at a time, which is safer",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "可复现构建需要 lockfile（pip 本身没有内置锁定），monorepo 需要 workspace 一次装好相互依赖的多个本地包；uv 又快，能显著省下 CI 时间。",
                    "en": "Reproducible builds need a lockfile (pip has no built-in locking), and a monorepo needs a workspace to install several inter-dependent local packages at once; uv is also fast, saving real CI time.",
                },
            },
            {
                "q": {
                    "zh": "你想在<strong>本地</strong>跑一遍类型检查（MyPy + Pyright）再提 PR。正确的命令是？",
                    "en": "You want to run type checking (MyPy + Pyright) <strong>locally</strong> before opening a PR. The correct command is?",
                },
                "opts": [
                    {"zh": "<code>uv run poe typing</code>", "en": "<code>uv run poe typing</code>"},
                    {"zh": "<code>uv run poe typecheck</code>", "en": "<code>uv run poe typecheck</code>"},
                    {"zh": "<code>uv run poe mypy-only</code>", "en": "<code>uv run poe mypy-only</code>"},
                    {"zh": "<code>python -m typing</code>", "en": "<code>python -m typing</code>"},
                ],
                "answer": 0,
                "why": {
                    "zh": "真实任务名是 <code>poe typing</code>（底层同时跑 MyPy 和 Pyright），并没有 <code>typecheck</code> 这个任务。提 PR 前的本地门通常是 <code>poe lint</code> → <code>poe typing</code> → <code>poe test</code>；而 DevUI 用来“看得见”地调试消息 / 工具 / 中间件流，是纯 CLI 看不到的中间态。",
                    "en": "The real task is <code>poe typing</code> (it runs both MyPy and Pyright underneath); there is no <code>typecheck</code> task. The pre-PR local gate is usually <code>poe lint</code> → <code>poe typing</code> → <code>poe test</code>; DevUI is for <em>visually</em> debugging message / tool / middleware flow you can't see from the CLI.",
                },
            },
        ],
        "open": [
            {
                "zh": "你要给 <code>packages/core</code> 修一个小 bug。请照本课的“开发闭环”写出从 clone 到提 PR 前你会<strong>依次</strong>敲的命令，并说说 DevUI 在这个闭环里替代了哪种“低效的调试方式”、为什么它对调试 Agent 特别有用。",
                "en": "You're fixing a small bug in <code>packages/core</code>. Following this lesson's &quot;dev loop&quot;, write the commands you'd run <strong>in order</strong> from clone to just-before-PR, and explain which &quot;inefficient debugging habit&quot; DevUI replaces in that loop and why it's especially useful for debugging Agents.",
            },
        ],
    },
    "29-devui.html": {
        "mcq": [
            {
                "q": {
                    "zh": "<code>serve(entities=[agent])</code> 启动 DevUI。下面哪条最准确地描述它做的事？",
                    "en": "<code>serve(entities=[agent])</code> launches DevUI. Which best describes what it does?",
                },
                "opts": [
                    {
                        "zh": "用 uvicorn 起一个本地服务，挂上 Web UI + OpenAI 兼容 API（<code>/v1/*</code>），把你传入的 Agent/Workflow 注册进去供可视化调试",
                        "en": "Starts a local uvicorn server with a web UI + OpenAI-compatible API (<code>/v1/*</code>), registering your Agents/Workflows for visual debugging",
                    },
                    {"zh": "把 Agent 训练成一个新模型", "en": "Trains the Agent into a new model"},
                    {"zh": "把 Agent 永久部署到云端生产环境", "en": "Permanently deploys the Agent to cloud production"},
                    {"zh": "删除 Agent 的所有记忆", "en": "Wipes all of the Agent's memory"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>serve()</code> 底层创建 <code>DevServer</code>、取出 FastAPI app、<code>uvicorn.run(app, host, port)</code>，并注册传入的 entities。它暴露 <code>/v1/*</code> 的 OpenAI 兼容 API，Web UI 只是这套 API 的可视化壳——纯调试用途，不训练也不部署。",
                    "en": "<code>serve()</code> creates a <code>DevServer</code>, grabs its FastAPI app, runs <code>uvicorn.run(app, host, port)</code>, and registers the passed entities. It exposes an OpenAI-compatible <code>/v1/*</code> API; the web UI is just a visual shell over it&mdash;purely for debugging, not training or deploying.",
                },
            },
            {
                "q": {
                    "zh": "在 DevUI 里调一个带工具的 Agent，下面哪样是你<strong>看不到</strong>的？",
                    "en": "Debugging a tool-using Agent in DevUI, which would you <strong>not</strong> see?",
                },
                "opts": [
                    {"zh": "模型内部的神经网络权重数值", "en": "The model's internal neural-network weight values"},
                    {"zh": "工具调用卡片（名称 / 参数 / 返回值）", "en": "Tool-call cards (name / args / return value)"},
                    {"zh": "逐个流出的 token", "en": "Tokens streaming out one by one"},
                    {"zh": "system/user/assistant 消息时间线", "en": "The system/user/assistant message timeline"},
                ],
                "answer": 0,
                "why": {
                    "zh": "DevUI 让运行过程「看得见」：消息时间线、工具调用、流式 token，开 <code>instrumentation_enabled</code> 还能看 span 树。但它观测的是<strong>框架层</strong>的行为，模型内部权重既看不到也无需看。",
                    "en": "DevUI makes the run visible: message timeline, tool calls, streaming tokens, and (with <code>instrumentation_enabled</code>) the span tree. But it observes <strong>framework-level</strong> behavior&mdash;the model's internal weights are neither visible nor relevant.",
                },
            },
            {
                "q": {
                    "zh": "DevUI 默认 <code>host=\"127.0.0.1\"</code> 且 <code>auth_enabled=True</code>，官方也强调它是「样例 App」。这组默认值最能说明什么？",
                    "en": "DevUI defaults to <code>host=\"127.0.0.1\"</code> with <code>auth_enabled=True</code>, and the docs call it a &quot;sample app&quot;. What do these defaults most clearly signal?",
                },
                "opts": [
                    {
                        "zh": "它定位是<strong>本地开发 / 调试</strong>工具；生产应当用 SDK 自建 server，而不是直接拿 DevUI 当生产网关",
                        "en": "It's positioned as a <strong>local dev / debugging</strong> tool; production should build a server with the SDK, not use DevUI as a production gateway",
                    },
                    {"zh": "它已经是经过加固的生产级网关", "en": "It is already a hardened, production-grade gateway"},
                    {"zh": "它必须暴露到公网才能工作", "en": "It must be exposed to the public internet to work"},
                    {"zh": "它不支持任何鉴权", "en": "It supports no authentication at all"},
                ],
                "answer": 0,
                "why": {
                    "zh": "只绑本机 + 默认带鉴权，正是「本机开发」的安全姿态；官方明确 DevUI 是 sample app，生产请用 Agent Framework SDK 自建 API server 与界面。调试与部署是两条线（部署见第 25 课 Foundry 托管）。",
                    "en": "Localhost-only + auth-by-default is the safe posture for local development; the docs state DevUI is a sample app, and production should build its own API server and UI with the SDK. Debugging and deployment are separate tracks (deployment: Lesson 25, Foundry hosting).",
                },
            },
        ],
        "open": [
            {
                "zh": "回想你上次用 <code>print</code> 调 Agent 时最想知道却看不到的一件事（比如「它到底调没调工具」「为什么半天不出字」）。说说在 DevUI 的哪个面板能直接看到它，以及这如何改变你的调试节奏。再想想：为什么「不改 Agent 代码就能调试」是个重要约束？",
                "en": "Recall the one thing you most wanted to see but couldn't last time you debugged an agent with <code>print</code> (e.g. &quot;did it actually call a tool&quot;, &quot;why the long silence before text&quot;). Say which DevUI panel shows it directly, and how that changes your debugging loop. Then: why is &quot;debug without changing Agent code&quot; an important constraint?",
            },
        ],
    },
    "30-observability.html": {
        "mcq": [
            {
                "q": {
                    "zh": "一次带工具的 <code>run()</code> 产生的 span 树，下面哪条描述与框架实际行为一致？",
                    "en": "For the span tree from a tool-using <code>run()</code>, which matches the framework's actual behavior?",
                },
                "opts": [
                    {
                        "zh": "<code>invoke_agent</code> 是根 span，<code>chat</code> 是它的子 span，而工具执行 <code>execute_tool</code> 嵌在 <code>chat</code> span 之内；子 span 耗时滚动累加进父 span",
                        "en": "<code>invoke_agent</code> is the root span, <code>chat</code> is its child, and tool execution <code>execute_tool</code> nests inside the <code>chat</code> span; child durations roll up into the parent",
                    },
                    {"zh": "只有一个扁平的 <code>invoke_agent</code> span，没有任何子 span", "en": "Just one flat <code>invoke_agent</code> span with no children"},
                    {"zh": "<code>execute_tool</code> 是根 span，<code>invoke_agent</code> 反而是它的子 span", "en": "<code>execute_tool</code> is the root and <code>invoke_agent</code> is its child"},
                    {"zh": "span 之间互相平级，没有父子关系", "en": "Spans are all siblings with no parent/child relationship"},
                ],
                "answer": 0,
                "why": {
                    "zh": "框架开根 span <code>invoke_agent {agent}</code>，其下是 <code>chat {model}</code>；源码把「内层工具执行」parent 到这个 chat span（<code>observability.py:1556</code>），所以 <code>execute_tool</code> 嵌在 <code>chat</code> 之内。span 树天然让子调用耗时累加进父 span，因此能定位「慢在哪一步」。",
                    "en": "The framework opens root <code>invoke_agent {agent}</code>, then <code>chat {model}</code>; the source parents inner tool execution under that chat span (<code>observability.py:1556</code>), so <code>execute_tool</code> nests inside <code>chat</code>. A span tree rolls child durations into parents, which is how you locate &quot;which step is slow&quot;.",
                },
            },
            {
                "q": {
                    "zh": "要在生产里给 Agent Framework 接上 OpenTelemetry，标准做法是？",
                    "en": "The standard way to wire OpenTelemetry into Agent Framework in production is?",
                },
                "opts": [
                    {
                        "zh": "应用启动时调一次 <code>configure_otel_providers()</code>（纯关键字参数），其余靠 OTel 环境变量；埋点由框架的 telemetry 层自动完成",
                        "en": "Call <code>configure_otel_providers()</code> once at startup (keyword-only), configure the rest via OTel env vars; the framework's telemetry layers instrument automatically",
                    },
                    {"zh": "在每个工具函数里手写 span 创建/关闭代码", "en": "Hand-write span open/close code inside every tool function"},
                    {"zh": "每次 <code>run()</code> 前后都重新初始化一遍 OTel", "en": "Re-initialize OTel before and after every <code>run()</code>"},
                    {"zh": "必须 fork 框架源码才能加埋点", "en": "You must fork the framework source to add instrumentation"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>configure_otel_providers()</code>（<code>observability.py:1151</code>）文档明确「只调一次、在产生任何遥测前」，它读标准 OTel 环境变量。之后 <code>AgentTelemetryLayer</code>/<code>ChatTelemetryLayer</code> 自动给每次调用挂 span+metric——业务代码零埋点。",
                    "en": "<code>configure_otel_providers()</code> (<code>observability.py:1151</code>) is documented to be called once, before any telemetry, and reads standard OTel env vars. After that, <code>AgentTelemetryLayer</code>/<code>ChatTelemetryLayer</code> attach spans+metrics to every call&mdash;zero instrumentation in business code.",
                },
            },
            {
                "q": {
                    "zh": "可观测的「三根支柱」里，<strong>metric（指标）</strong>最适合回答下面哪类问题？",
                    "en": "Among the three pillars, <strong>metrics</strong> are best suited to answer which kind of question?",
                },
                "opts": [
                    {
                        "zh": "聚合趋势：整体延迟分布（p95）、token 用量、失败率",
                        "en": "Aggregate trends: overall latency distribution (p95), token usage, failure rate",
                    },
                    {"zh": "这一次调用里，第 2 步具体比第 1 步慢多少", "en": "In this single call, exactly how much slower step 2 was than step 1"},
                    {"zh": "某条消息的逐字内容", "en": "The verbatim content of one specific message"},
                    {"zh": "模型内部的权重值", "en": "The model's internal weight values"},
                ],
                "answer": 0,
                "why": {
                    "zh": "trace 回答「单次、哪一步」（span 树），metric 回答「聚合、整体趋势」（直方图，如 <code>gen_ai.client.operation.duration</code>、<code>token.usage</code>），log 回答「具体发生了啥」（事件，敏感内容需显式开）。三者分工互补。",
                    "en": "Traces answer &quot;single run, which step&quot; (span tree); metrics answer &quot;aggregate trend&quot; (histograms like <code>gen_ai.client.operation.duration</code>, <code>token.usage</code>); logs answer &quot;what exactly happened&quot; (events, sensitive content opt-in). The three are complementary.",
                },
            },
        ],
        "open": [
            {
                "zh": "假设线上某个 Agent「偶尔很慢」。请用本课的三根支柱设计一套排查路径：你会先看 trace 的哪些 span、再看哪些 metric、什么时候才需要打开 <code>enable_sensitive_data</code> 看 log？并说说为什么把敏感数据默认关掉是合理的取舍。",
                "en": "Suppose a production Agent is &quot;occasionally slow&quot;. Using this lesson's three pillars, design an investigation path: which trace spans would you look at first, which metrics next, and when would you actually need to flip <code>enable_sensitive_data</code> to inspect logs? Also explain why defaulting sensitive data off is a reasonable tradeoff.",
            },
        ],
    },
    "16-providers.html": {
        "mcq": [
            {
                "q": {
                    "zh": "为什么把模型厂商从 OpenAI 换成 Anthropic，通常只改“实例化 ChatClient”那一两行，下游 Agent 代码却不用动？",
                    "en": "Why does switching the model vendor from OpenAI to Anthropic usually touch only the one or two &quot;instantiate the ChatClient&quot; lines, leaving downstream Agent code unchanged?",
                },
                "opts": [
                    {
                        "zh": "<code>as_agent()</code> / <code>run()</code> 这层接口是厂商无关的，provider 包只负责把自家 API 适配成同一套 ChatClient 抽象",
                        "en": "The <code>as_agent()</code> / <code>run()</code> layer is vendor-agnostic; each provider package only adapts its own API to the same ChatClient abstraction",
                    },
                    {
                        "zh": "因为所有厂商的 HTTP API 格式本来就完全一样",
                        "en": "Because every vendor's HTTP API format is already identical",
                    },
                    {
                        "zh": "因为 MAF 会在运行时自动翻译你的 prompt",
                        "en": "Because MAF auto-translates your prompt at runtime",
                    },
                    {
                        "zh": "因为 Agent 代码里其实写死了 OpenAI",
                        "en": "Because the Agent code is actually hard-wired to OpenAI",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "ChatClient 是一道<strong>抽象边界</strong>：每个 provider 包实现同一套接口，Agent 只依赖抽象。所以“构造 ChatClient”以上随厂商变，以下全部复用——换厂商是局部改动。",
                    "en": "ChatClient is an <strong>abstraction boundary</strong>: each provider package implements the same interface and the Agent depends only on the abstraction. So everything above &quot;construct the ChatClient&quot; varies by vendor and everything below is reused - switching vendors is a local change.",
                },
            },
            {
                "q": {
                    "zh": "MAF 用<strong>同一个</strong> <code>OpenAIChatClient</code> 同时接 OpenAI 和 Azure OpenAI（靠 <code>base_url</code> / 认证区分），而不是做两个类。为什么？",
                    "en": "MAF uses <strong>one</strong> <code>OpenAIChatClient</code> for both OpenAI and Azure OpenAI (distinguished by <code>base_url</code> / credentials) instead of two classes. Why?",
                },
                "opts": [
                    {
                        "zh": "两者底层 wire protocol 相同，只是 endpoint / 认证不同——一个类加参数比两个近乎重复的类更好维护",
                        "en": "They share the same underlying wire protocol and differ only in endpoint / auth - one parameterized class is easier to maintain than two near-duplicate classes",
                    },
                    {
                        "zh": "因为 Azure OpenAI 没有自己的 SDK",
                        "en": "Because Azure OpenAI has no SDK of its own",
                    },
                    {
                        "zh": "因为 OpenAI 和 Azure 是同一家公司",
                        "en": "Because OpenAI and Azure are the same company",
                    },
                    {
                        "zh": "因为 MAF 其实不支持 Azure OpenAI",
                        "en": "Because MAF doesn't actually support Azure OpenAI",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "两种部署协议一致，差别只在 endpoint 和 credential。用一个类 + 参数化，比维护两个几乎重复的类更省心——这也呼应“厂商无关”：连同一厂商的两种部署都收敛到同一接口。",
                    "en": "The two deployments speak the same protocol and differ only in endpoint and credential. One parameterized class beats maintaining two near-identical ones - and it echoes &quot;vendor-agnostic&quot;: even one vendor's two deployments converge on the same interface.",
                },
            },
            {
                "q": {
                    "zh": "接入 Anthropic Claude 时，MAF 里<strong>真实</strong>的 ChatClient 类名是哪个？",
                    "en": "When connecting Anthropic Claude, what is the <strong>real</strong> ChatClient class name in MAF?",
                },
                "opts": [
                    {"zh": "<code>AnthropicClient</code>", "en": "<code>AnthropicClient</code>"},
                    {"zh": "<code>AnthropicChatClient</code>", "en": "<code>AnthropicChatClient</code>"},
                    {"zh": "<code>ClaudeChatClient</code>", "en": "<code>ClaudeChatClient</code>"},
                    {"zh": "<code>AnthropicAgent</code>", "en": "<code>AnthropicAgent</code>"},
                ],
                "answer": 0,
                "why": {
                    "zh": "真实类名是 <code>AnthropicClient</code>（不是 <code>AnthropicChatClient</code>），从 <code>agent_framework.anthropic</code> 导入；而 OpenAI 那个才叫 <code>OpenAIChatClient</code>。命名不完全统一是真实情况——按包里的真名来，别想当然套 <code>*ChatClient</code>。",
                    "en": "The real class is <code>AnthropicClient</code> (not <code>AnthropicChatClient</code>), imported from <code>agent_framework.anthropic</code>; OpenAI's is the one called <code>OpenAIChatClient</code>. Naming isn't perfectly uniform - use the real name from the package rather than assuming a <code>*ChatClient</code> suffix.",
                },
            },
        ],
        "open": [
            {
                "zh": "请用真实类名分别写出“接入 OpenAI”和“接入 Anthropic”的 import + 实例化两行代码，然后指出：如果一个已经写好的 <code>agent.run(...)</code> 业务函数要在两家之间切换，哪些行会变、哪些行完全不变，并解释这背后是哪条设计原则。",
                "en": "Using the real class names, write the import + instantiation lines for &quot;connect OpenAI&quot; and &quot;connect Anthropic&quot;. Then say, for an already-written <code>agent.run(...)</code> business function that must switch between the two, which lines change and which stay identical - and which design principle explains that.",
            },
        ],
    },
    "17-declarative.html": {
        "mcq": [
            {
                "q": {
                    "zh": "用 <code>AgentFactory</code> 从 YAML 造出来的 Agent，和你手写 <code>Agent(client=…, tools=…)</code> 造出来的相比？",
                    "en": "How does an Agent built from YAML via <code>AgentFactory</code> compare to one you hand-build with <code>Agent(client=…, tools=…)</code>?",
                },
                "opts": [
                    {
                        "zh": "是<strong>同一类对象</strong>，下游 <code>run()</code> / 工具 / 中间件用法完全一样",
                        "en": "It's the <strong>same kind of object</strong>; downstream <code>run()</code> / tools / middleware all behave identically",
                    },
                    {
                        "zh": "是个受限的“只读”Agent，不能调用工具",
                        "en": "It's a restricted &quot;read-only&quot; Agent that can't call tools",
                    },
                    {
                        "zh": "必须用专门的 <code>yaml_run()</code> 才能跑",
                        "en": "It can only run via a special <code>yaml_run()</code>",
                    },
                    {
                        "zh": "性能更差，因为每次调用都要重新解析 YAML",
                        "en": "It's slower because it re-parses the YAML on every call",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "声明式只是<strong>另一种构造路径</strong>：<code>AgentFactory</code> 解析后产出标准 <code>Agent</code> 实例。配置与代码同构，所以两种风格可以自由切换，下游一切照旧。",
                    "en": "Declarative is just <strong>another construction path</strong>: <code>AgentFactory</code> parses and emits a standard <code>Agent</code> instance. Config and code are isomorphic, so the two styles are interchangeable and everything downstream is unchanged.",
                },
            },
            {
                "q": {
                    "zh": "把 Agent 定义放进 YAML（而不是写死在 <code>.py</code> 里）最主要的好处是？",
                    "en": "What's the main benefit of putting the Agent definition in YAML instead of hard-coding it in <code>.py</code>?",
                },
                "opts": [
                    {
                        "zh": "配置变成<strong>数据</strong>：非开发者也能改、能进版本控制 diff、能按环境换文件，全程不碰代码",
                        "en": "Config becomes <strong>data</strong>: non-developers can edit it, it diffs in version control, and you can swap files per environment - all without touching code",
                    },
                    {
                        "zh": "YAML 跑起来比 Python 快",
                        "en": "YAML runs faster than Python",
                    },
                    {
                        "zh": "YAML 能绕过工具审批",
                        "en": "YAML can bypass tool approval",
                    },
                    {
                        "zh": "YAML 可以定义无限多工具",
                        "en": "YAML can define unlimited tools",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "声明式把“做什么”和“怎么跑”解耦。配置即数据 → 可审计、可版本化、可由非工程师维护；<code>create_agent_from_yaml_path</code> 一行就能加载。",
                    "en": "Declarative decouples &quot;what&quot; from &quot;how it runs&quot;. Config-as-data means it's auditable, versionable and editable by non-engineers; <code>create_agent_from_yaml_path</code> loads it in one line.",
                },
            },
            {
                "q": {
                    "zh": "从 YAML 文件加载一个 Agent，MAF 里<strong>真实</strong>的调用是哪个？",
                    "en": "What is the <strong>real</strong> call to load an Agent from a YAML file in MAF?",
                },
                "opts": [
                    {
                        "zh": "<code>AgentFactory().create_agent_from_yaml_path(\"my_agent.yaml\")</code>",
                        "en": "<code>AgentFactory().create_agent_from_yaml_path(\"my_agent.yaml\")</code>",
                    },
                    {
                        "zh": "<code>AgentFactory.load_agent(\"my_agent.yaml\")</code>",
                        "en": "<code>AgentFactory.load_agent(\"my_agent.yaml\")</code>",
                    },
                    {
                        "zh": "<code>Agent.from_yaml(\"my_agent.yaml\")</code>",
                        "en": "<code>Agent.from_yaml(\"my_agent.yaml\")</code>",
                    },
                    {
                        "zh": "<code>declarative.parse(\"my_agent.yaml\")</code>",
                        "en": "<code>declarative.parse(\"my_agent.yaml\")</code>",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "真实 API 是 <code>from agent_framework.declarative import AgentFactory</code>，再调 <code>create_agent_from_yaml_path(...)</code>（不是 <code>load_agent</code>）。<code>AgentFactory(bindings={...})</code> 的 <code>bindings</code> 还能把 YAML 里的工具 / 客户端名字绑定到真实对象。",
                    "en": "The real API is <code>from agent_framework.declarative import AgentFactory</code>, then <code>create_agent_from_yaml_path(...)</code> (not <code>load_agent</code>). <code>AgentFactory(bindings={...})</code> also binds tool / client names in the YAML to real objects.",
                },
            },
        ],
        "open": [
            {
                "zh": "你的团队想让产品经理也能改 Agent 的 <code>instructions</code> 而不用发版。请说说声明式 YAML 怎么支撑这个流程，以及 YAML 里写的 <code>tools: [get_weather]</code> 最终是怎么变成一个可调用工具的（谁负责把名字解析、绑定到真实函数）。",
                "en": "Your team wants PMs to edit an Agent's <code>instructions</code> without shipping a release. Explain how declarative YAML supports that workflow, and how <code>tools: [get_weather]</code> in the YAML becomes a callable tool (who resolves the name and binds it to the real function).",
            },
        ],
    },
    "18-custom-middleware.html": {
        "mcq": [
            {
                "q": {
                    "zh": "要把 Chat、Function、Agent 三种中间件挂到一个 Agent 上，正确方式是？",
                    "en": "To attach Chat, Function and Agent middleware to one Agent, the correct way is?",
                },
                "opts": [
                    {
                        "zh": "全部放进同一个 <code>middleware=[...]</code> 列表，框架按基类自动分流到对应层",
                        "en": "Put them all in one <code>middleware=[...]</code> list; the framework routes each to the right layer by its base class",
                    },
                    {
                        "zh": "分别用 <code>chat_middleware=</code> / <code>function_middleware=</code> / <code>agent_middleware=</code> 三个参数",
                        "en": "Use three separate params: <code>chat_middleware=</code> / <code>function_middleware=</code> / <code>agent_middleware=</code>",
                    },
                    {
                        "zh": "每种中间件各建一个 Agent",
                        "en": "Build a separate Agent for each middleware kind",
                    },
                    {
                        "zh": "一个 Agent 只能挂一个中间件",
                        "en": "An Agent can hold only one middleware",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>Agent(...)</code> / <code>as_agent(...)</code> 只有<strong>一个</strong> <code>middleware=</code> 参数，框架按基类（<code>ChatMiddleware</code> / <code>FunctionMiddleware</code> / <code>AgentMiddleware</code>）分类路由。一个口子、可混放，组合更自由。（<code>chat_middleware</code> / <code>function_middleware</code> 其实是给普通函数<em>打标记</em>的装饰器，不是构造参数。）",
                    "en": "<code>Agent(...)</code> / <code>as_agent(...)</code> takes a <strong>single</strong> <code>middleware=</code> param and routes by base class (<code>ChatMiddleware</code> / <code>FunctionMiddleware</code> / <code>AgentMiddleware</code>). One slot, mixable, more composable. (<code>chat_middleware</code> / <code>function_middleware</code> are actually <em>decorators</em> that mark plain functions, not constructor params.)",
                },
            },
            {
                "q": {
                    "zh": "中间件里 <code>await call_next()</code> <strong>之后</strong>的代码什么时候跑？为什么结果要从 <code>context.result</code> 取，而不是 <code>call_next()</code> 的返回值？",
                    "en": "When does code <strong>after</strong> <code>await call_next()</code> run, and why is the result read from <code>context.result</code> instead of <code>call_next()</code>'s return value?",
                },
                "opts": [
                    {
                        "zh": "在内层执行完、响应“出站”时跑；结果挂在共享 <code>context</code> 上，方便前后两端和多个中间件读写同一份状态",
                        "en": "It runs as the response travels &quot;out&quot;, after the inner layers finish; the result lives on the shared <code>context</code> so both ends and multiple middleware read/write one state",
                    },
                    {
                        "zh": "永远不跑，<code>call_next()</code> 之后是死代码",
                        "en": "It never runs; code after <code>call_next()</code> is dead code",
                    },
                    {
                        "zh": "在请求“进站”之前跑",
                        "en": "It runs before the request goes &quot;in&quot;",
                    },
                    {
                        "zh": "<code>call_next()</code> 会直接 <code>return</code> 最终字符串",
                        "en": "<code>call_next()</code> directly returns the final string",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>call_next()</code> 是分界线：之前=进站，之后=出站（洋葱模型）。结果放 <code>context</code> 而非返回值，让任意层都能读改同一份上下文（改写输出、记录耗时…），也让<strong>无参</strong>的 <code>call_next()</code> 把整条链串起来。",
                    "en": "<code>call_next()</code> is the dividing line: before = inbound, after = outbound (the onion). Putting the result on <code>context</code> rather than a return value lets any layer read/modify one shared context (rewrite output, record timing…) and lets the <strong>argument-free</strong> <code>call_next()</code> chain the whole pipeline.",
                },
            },
            {
                "q": {
                    "zh": "用 <code>middleware=[A, B]</code> 挂两个中间件，执行顺序是？",
                    "en": "With <code>middleware=[A, B]</code>, what is the execution order?",
                },
                "opts": [
                    {
                        "zh": "<code>A.before → B.before → 真正调用 → B.after → A.after</code>（先进后出，A 在最外层）",
                        "en": "<code>A.before → B.before → real call → B.after → A.after</code> (first-in, last-out; A is outermost)",
                    },
                    {
                        "zh": "A 整个跑完，再从头跑 B",
                        "en": "A runs fully, then B runs from scratch",
                    },
                    {
                        "zh": "<code>B.before → A.before → 调用 → A.after → B.after</code>",
                        "en": "<code>B.before → A.before → call → A.after → B.after</code>",
                    },
                    {
                        "zh": "顺序是随机的",
                        "en": "The order is random",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "列表里<strong>越靠前越在外层</strong>（洋葱皮）：最先进、最后出。顺序会改变语义——比如“重试”包在“日志”外面还是里面，决定了失败重试会不会被重复记日志，所以顺序是显式可控的。",
                    "en": "Earlier in the list = further outside (onion skin): first in, last out. Order changes semantics - e.g. whether &quot;retry&quot; wraps &quot;logging&quot; or vice versa decides if retried failures get logged twice - so order is explicit and controllable.",
                },
            },
        ],
        "open": [
            {
                "zh": "你要加一个“计费”中间件：统计每次调用的 token 用量并上报。请说说你会继承哪个基类、在 <code>call_next()</code> 前后分别做什么，以及把它放在 <code>middleware=</code> 列表的<strong>靠前还是靠后</strong>会怎样影响它统计到的范围（比如会不会把重试产生的额外调用也算进去）。",
                "en": "You're adding a &quot;billing&quot; middleware that records each call's token usage and reports it. Say which base class you'd subclass, what you'd do before vs after <code>call_next()</code>, and how placing it <strong>earlier vs later</strong> in the <code>middleware=</code> list changes what it measures (e.g. whether extra calls from retries get counted).",
            },
        ],
    },
    "19-durability-hitl.html": {
        "mcq": [
            {
                "q": {
                    "zh": "Workflow 在哪里自动存检查点，这有什么用？",
                    "en": "Where does a Workflow auto-save checkpoints, and what's the point?",
                },
                "opts": [
                    {
                        "zh": "在每个 <strong>superstep 边界</strong>存档；崩溃后能从最近存档续跑，不必从头重来",
                        "en": "At every <strong>superstep boundary</strong>; after a crash it resumes from the latest save instead of restarting from scratch",
                    },
                    {
                        "zh": "在每生成一个 token 后都存一次",
                        "en": "After every single token is generated",
                    },
                    {
                        "zh": "只在 <code>workflow.run</code> 返回后存一次",
                        "en": "Only once, after <code>workflow.run</code> returns",
                    },
                    {
                        "zh": "从不自动存，必须手动调 <code>save()</code>",
                        "en": "Never automatically; you must call <code>save()</code> by hand",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "superstep 是 workflow 的批处理边界，天然是一致性快照点。存档内容=Agent 状态 + 消息历史 + 当前步；10 步在第 5 步挂了能从第 5 步起，省时间也省 LLM token。",
                    "en": "A superstep is the workflow's batch boundary - a natural consistency snapshot point. A save holds Agent state + message history + current step; a 10-step run that dies at step 5 resumes from step 5, saving time and LLM tokens.",
                },
            },
            {
                "q": {
                    "zh": "关于检查点的<strong>持久化后端</strong>，下面哪个说法正确？",
                    "en": "Regarding the <strong>persistent backend</strong> for checkpoints, which statement is correct?",
                },
                "opts": [
                    {
                        "zh": "工作流检查点用 <code>FileCheckpointStorage</code>（核心）或 <code>CosmosCheckpointStorage</code>（azure-cosmos 包）；Redis 包是给上下文 / 历史记忆用的，不是 checkpoint 后端",
                        "en": "Workflow checkpoints use <code>FileCheckpointStorage</code> (core) or <code>CosmosCheckpointStorage</code> (azure-cosmos package); the Redis package is for context / history memory, not a checkpoint backend",
                    },
                    {
                        "zh": "Redis 是默认的检查点后端",
                        "en": "Redis is the default checkpoint backend",
                    },
                    {
                        "zh": "只有内存一种后端，无法持久化",
                        "en": "There's only an in-memory backend; persistence is impossible",
                    },
                    {
                        "zh": "切换后端必须重写整个 workflow",
                        "en": "Switching backends requires rewriting the whole workflow",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "真实情况：核心提供 <code>InMemory</code> / <code>File</code>，<code>agent-framework-azure-cosmos</code> 提供 <code>Cosmos</code>。Redis 包导出的是 <code>RedisContextProvider</code> / <code>RedisHistoryProvider</code>（记忆 / 历史），属于<strong>另一条</strong>持久化轴。切后端只改“构造 storage”那一行，<code>checkpoint_storage=</code> 接口不变。",
                    "en": "Reality: core ships <code>InMemory</code> / <code>File</code>; <code>agent-framework-azure-cosmos</code> ships <code>Cosmos</code>. The Redis package exports <code>RedisContextProvider</code> / <code>RedisHistoryProvider</code> (memory / history) - a <strong>different</strong> durability axis. Switching backends is a one-line change to constructing <code>storage</code>; the <code>checkpoint_storage=</code> interface stays the same.",
                },
            },
            {
                "q": {
                    "zh": "MAF 的“人在环”(HITL) 在哪<strong>两个</strong>层面提供暂停点？",
                    "en": "At which <strong>two</strong> levels does MAF's human-in-the-loop (HITL) offer pause points?",
                },
                "opts": [
                    {
                        "zh": "工具层 <code>approval_mode=\"always_require\"</code> + 工作流层 <code>request_info</code>",
                        "en": "Tool level <code>approval_mode=\"always_require\"</code> + workflow level <code>request_info</code>",
                    },
                    {
                        "zh": "只有工具层",
                        "en": "Only the tool level",
                    },
                    {
                        "zh": "只有 UI 层弹窗",
                        "en": "Only a UI-level popup",
                    },
                    {
                        "zh": "靠 <code>time.sleep</code> 轮询",
                        "en": "By polling with <code>time.sleep</code>",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "两条路：单个工具调用前要审批（<code>approval_mode</code>），或工作流节点用 <code>request_info</code> 暂停、发问、等回答。共同点是把“等人”变成一等状态——配合检查点，甚至能在崩溃恢复后继续等那次审批。",
                    "en": "Two routes: require approval before a single tool call (<code>approval_mode</code>), or have a workflow node <code>request_info</code> to pause, ask and await a reply. Both make &quot;waiting on a human&quot; a first-class state - combined with checkpointing, the pending approval can even survive a crash-and-resume.",
                },
            },
        ],
        "open": [
            {
                "zh": "一个 10 步、含一次人工审批的工作流，跑到第 6 步进程崩了。结合<strong>检查点 + 持久化后端 + 人在环</strong>，说说重启后它怎么恢复到正确状态、那次审批的结果会不会丢，以及你会选 <code>File</code> 还是 <code>Cosmos</code> 后端、为什么。",
                "en": "A 10-step workflow with one human approval crashes at step 6. Using <strong>checkpointing + persistent backend + HITL</strong>, explain how it recovers to the correct state on restart, whether that approval result is lost, and whether you'd pick the <code>File</code> or <code>Cosmos</code> backend and why.",
            },
        ],
    },
    "20-capstone.html": {
        "mcq": [
            {
                "q": {
                    "zh": "capstone 把 provider / 工具 / 中间件 / 编排 / 检查点拼到一起，最能体现 MAF 的哪个设计？",
                    "en": "The capstone assembles provider / tools / middleware / orchestration / checkpointing. Which MAF design does that best illustrate?",
                },
                "opts": [
                    {
                        "zh": "这些能力彼此<strong>正交</strong>：各自独立、接口稳定，所以能像乐高一样自由组合，不用互相改代码",
                        "en": "These capabilities are <strong>orthogonal</strong>: independent with stable interfaces, so they compose like LEGO without changing each other's code",
                    },
                    {
                        "zh": "必须按固定顺序写死，换一个就全崩",
                        "en": "They must be wired in a fixed order; swap one and everything breaks",
                    },
                    {
                        "zh": "所有功能其实都是一个大类",
                        "en": "All the features are really one giant class",
                    },
                    {
                        "zh": "只有买企业版才能组合",
                        "en": "Composition only works in the enterprise edition",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "每个零件都通过稳定接口暴露（<code>ChatClient</code>、<code>@tool</code>、<code>middleware=</code>、<code>*Builder</code>、<code>checkpoint_storage=</code>）。正交即可组合：加中间件不影响编排，换 provider 不影响工具。capstone 的价值就是把这点看清。",
                    "en": "Each brick is exposed via a stable interface (<code>ChatClient</code>, <code>@tool</code>, <code>middleware=</code>, <code>*Builder</code>, <code>checkpoint_storage=</code>). Orthogonal means composable: adding middleware doesn't affect orchestration, swapping providers doesn't affect tools. The capstone makes that visible.",
                },
            },
            {
                "q": {
                    "zh": "在 writer → reviewer 的 <code>SequentialBuilder</code> 工作流里，检查点是怎么接进去的？",
                    "en": "In the writer → reviewer <code>SequentialBuilder</code> workflow, how does checkpointing get wired in?",
                },
                "opts": [
                    {
                        "zh": "把 <code>storage</code> 传给 <code>SequentialBuilder(participants=[…], checkpoint_storage=storage)</code>，工作流在 superstep 边界自动存",
                        "en": "Pass <code>storage</code> to <code>SequentialBuilder(participants=[…], checkpoint_storage=storage)</code>; the workflow auto-saves at superstep boundaries",
                    },
                    {
                        "zh": "在每个 Agent 的 <code>run()</code> 里手动 <code>save</code>",
                        "en": "Manually <code>save</code> inside each Agent's <code>run()</code>",
                    },
                    {
                        "zh": "检查点必须用一个单独的 <code>with</code> 语句包住",
                        "en": "Checkpointing must be wrapped in a separate <code>with</code> block",
                    },
                    {
                        "zh": "Sequential 工作流不支持检查点",
                        "en": "Sequential workflows don't support checkpointing",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "检查点是 Builder 的一个参数，由<strong>编排层</strong>统一负责存档；Agent 本身不用关心持久化。这正是分层组合：Agent 管“想”，Builder 管“编排 + 存档”——各司其职，互不渗透。",
                    "en": "Checkpointing is a Builder parameter; the <strong>orchestration layer</strong> owns saving, and the Agent need not know about persistence. That's layered composition: the Agent &quot;thinks&quot;, the Builder handles &quot;orchestration + saving&quot; - separate concerns that don't leak into each other.",
                },
            },
        ],
        "open": [
            {
                "zh": "给这个 writer → reviewer 工作流再加一个“事实核查”Agent，并要求在 reviewer 之前先过核查。请说说你会怎么改 <code>participants</code>、是否需要改动 writer / reviewer 自身的代码，以及为什么这种扩展通常是“再加一块乐高”而不是“重构”——它印证了哪条设计原则？",
                "en": "Add a &quot;fact-check&quot; Agent to the writer → reviewer workflow, required to run before the reviewer. Say how you'd change <code>participants</code>, whether you must edit the writer / reviewer code itself, and why this is usually &quot;adding one more LEGO brick&quot; rather than &quot;refactoring&quot; - which design principle does that confirm?",
            },
        ],
    },
    "28-memory-backends.html": {
        "mcq": [
            {
                "q": {
                    "zh": "<code>HistoryProvider</code> 与 <code>ContextProvider</code> 都继承自同一个基类，但分工不同。下面哪条最准确？",
                    "en": "<code>HistoryProvider</code> and <code>ContextProvider</code> share a base class but do different jobs. Which is most accurate?",
                },
                "opts": [
                    {
                        "zh": "<code>HistoryProvider</code> 逐字存取一个会话的消息流（<code>get/save_messages</code>）；<code>ContextProvider</code> 更通用，按相关性把检索到的记忆注入上下文",
                        "en": "<code>HistoryProvider</code> stores/loads a session's message stream verbatim (<code>get/save_messages</code>); <code>ContextProvider</code> is more general, injecting relevance-retrieved memory into context",
                    },
                    {"zh": "两者完全一样，只是名字不同", "en": "They are identical, just named differently"},
                    {"zh": "<code>ContextProvider</code> 只能存历史，不能检索", "en": "<code>ContextProvider</code> can only store history, never retrieve"},
                    {"zh": "<code>HistoryProvider</code> 负责训练模型", "en": "<code>HistoryProvider</code> trains the model"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>HistoryProvider(ContextProvider)</code> 专管「短期、逐字、有序」的会话历史，子类只实现 <code>get_messages</code>/<code>save_messages</code>；基类 <code>ContextProvider</code> 更通用，在 <code>before_run</code> 里把检索到的「长期、语义」记忆注入上下文。两者共用同一对钩子，因此能自由叠加。",
                    "en": "<code>HistoryProvider(ContextProvider)</code> owns the short-term, verbatim, ordered conversation log; subclasses implement only <code>get_messages</code>/<code>save_messages</code>. The base <code>ContextProvider</code> is more general, injecting long-term, semantic memory in <code>before_run</code>. They share one hook pair, so they compose freely.",
                },
            },
            {
                "q": {
                    "zh": "MAF 把「记忆」做成挂在会话上的 Provider，而不是焊进 Agent 类。最主要的好处是？",
                    "en": "MAF models memory as a Provider attached to the session, not welded into the Agent class. The main benefit?",
                },
                "opts": [
                    {
                        "zh": "存储策略与 Agent 行为解耦：换 Redis / Mem0 / Cosmos 只是换一个 Provider 实例，Agent 代码一行不改",
                        "en": "Storage policy decouples from agent behavior: switching Redis / Mem0 / Cosmos just swaps a Provider instance, with zero changes to agent code",
                    },
                    {"zh": "让模型推理更快", "en": "It makes model inference faster"},
                    {"zh": "强制所有 Agent 都必须用 Redis", "en": "It forces every agent to use Redis"},
                    {"zh": "让 Agent 不再需要 ChatClient", "en": "It removes the need for a ChatClient"},
                ],
                "answer": 0,
                "why": {
                    "zh": "记忆是横切关注点（存哪、怎么检索、要不要逐字会随环境剧变）。抽成 Provider 后，唯一接入面是 <code>before_run</code>/<code>after_run</code> 钩子；多个 Provider 可叠加，各带 <code>source_id</code> 做归因。换后端 = 换实例，Agent 不动。",
                    "en": "Memory is a cross-cutting concern (where/how/verbatim swing with environment). As a Provider the only seam is the <code>before_run</code>/<code>after_run</code> hooks; multiple Providers stack, each with a <code>source_id</code> for attribution. Swap backend = swap instance; the agent is untouched.",
                },
            },
            {
                "q": {
                    "zh": "一次「带记忆」的 <code>run()</code>，记忆是怎么进到模型眼前的？",
                    "en": "In a memory-enabled <code>run()</code>, how does memory reach the model?",
                },
                "opts": [
                    {
                        "zh": "模型调用前，Provider 的 <code>before_run</code> 把历史 + 检索到的记忆注入上下文；运行后 <code>after_run</code> 把这轮写回后端",
                        "en": "Before the model call, the Provider's <code>before_run</code> injects history + retrieved memory into context; after the run, <code>after_run</code> writes this turn back",
                    },
                    {"zh": "模型自己连数据库去查", "en": "The model connects to the database itself"},
                    {"zh": "记忆被编译进模型权重", "en": "Memory is compiled into the model weights"},
                    {"zh": "只有你手动拼 prompt 才有记忆", "en": "Only manual prompt-stitching gives memory"},
                ],
                "answer": 0,
                "why": {
                    "zh": "框架在调模型「之前」回调 <code>before_run</code>：<code>HistoryProvider</code> 用 <code>get_messages</code> 接回逐字历史，<code>ContextProvider</code> 检索后用 <code>context.extend_messages(...)</code> 注入记忆。模型因此看到「历史+记忆+新问题」。「之后」回调 <code>after_run</code>/<code>save_messages</code> 写回，供下次取用。",
                    "en": "The framework calls <code>before_run</code> before the model: <code>HistoryProvider</code> reattaches verbatim history via <code>get_messages</code>, and <code>ContextProvider</code> injects retrieved memory via <code>context.extend_messages(...)</code>. The model then sees &quot;history + memory + new question&quot;. Afterward <code>after_run</code>/<code>save_messages</code> persists the turn for next time.",
                },
            },
        ],
        "open": [
            {
                "zh": "为你自己的一个 Agent 设计记忆方案：哪些信息该进 <code>HistoryProvider</code>（短期逐字），哪些该进 <code>ContextProvider</code>（长期语义检索）？再说说如果对话历史无限增长会出什么问题，你会怎么用「短期历史 + 长期向量」两条腿来缓解。",
                "en": "Design a memory scheme for one of your own agents: what belongs in a <code>HistoryProvider</code> (short-term verbatim) vs a <code>ContextProvider</code> (long-term semantic retrieval)? Then explain what breaks if conversation history grows without bound, and how you'd mitigate it with the &quot;short-term history + long-term vectors&quot; two-leg approach.",
            },
        ],
    },
    "23-skills.html": {
        "mcq": [
            {
                "q": {
                    "zh": "当 <code>SkillsProvider</code> “广告”一个技能时，<strong>最先</strong>进入系统提示的是什么？",
                    "en": "When a <code>SkillsProvider</code> “advertises” a skill, what enters the system prompt <strong>first</strong>?",
                },
                "opts": [
                    {
                        "zh": "只有技能的 <code>name</code> + <code>description</code>（约 ~100 token），正文要等 <code>load_skill</code> 才装载",
                        "en": "Only the skill's <code>name</code> + <code>description</code> (~100 tokens); the body is loaded later via <code>load_skill</code>",
                    },
                    {"zh": "整个技能正文加上所有资源全文", "en": "The entire skill body plus every resource in full"},
                    {"zh": "技能里所有脚本的源代码", "en": "The source code of every script in the skill"},
                    {"zh": "什么都不注入，模型自己去文件系统找", "en": "Nothing is injected; the model goes to the filesystem itself"},
                ],
                "answer": 0,
                "why": {
                    "zh": "这就是<strong>渐进式披露</strong>：<code>_skills.py:1732</code> 注释写明每个技能广告约 ~100 token，只放 name+description；模型据此判断“这题对不对口”，对口才调 <code>load_skill</code> 把合成正文（<code>get_content()</code>，<code>:782</code>）装进来，资源再用 <code>read_skill_resource</code> 按需取。这样挂很多技能也不会一次性撑爆 context。",
                    "en": "That's <strong>progressive disclosure</strong>: the comment at <code>_skills.py:1732</code> says each skill is advertised at ~100 tokens — just name+description. The model uses that to judge relevance, and only then calls <code>load_skill</code> to pull in the synthesized body (<code>get_content()</code>, <code>:782</code>), with resources fetched on demand via <code>read_skill_resource</code>. So many attached skills never blow the context at once.",
                },
            },
            {
                "q": {
                    "zh": "技能（Skill）和普通工具（tool）最本质的区别是？",
                    "en": "What is the most essential difference between a Skill and an ordinary tool?",
                },
                "opts": [
                    {
                        "zh": "工具<strong>执行动作</strong>；技能提供<strong>知识</strong>（指令 + 资源 + 可选脚本），按需装载进上下文",
                        "en": "A tool <strong>performs an action</strong>; a skill supplies <strong>knowledge</strong> (instructions + resources + optional scripts) loaded into context on demand",
                    },
                    {"zh": "技能更快，工具更慢", "en": "Skills are faster, tools are slower"},
                    {"zh": "技能只能用一次，工具能反复用", "en": "A skill can be used once, a tool many times"},
                    {"zh": "两者完全一样，只是命名不同", "en": "They are identical, just named differently"},
                ],
                "answer": 0,
                "why": {
                    "zh": "工具是“锤子”——被调用时去<strong>做</strong>一件事（查天气、发邮件）。技能是“操作手册”——把<strong>领域知识</strong>声明成可发现、可装载的模块。技能甚至通过 <code>load_skill</code>/<code>read_skill_resource</code>/<code>run_skill_script</code> 三个框架注入的工具来暴露自己；所以技能不是工具的替代，而是给模型“先学会怎么做、再动手”的那一层。",
                    "en": "A tool is a “hammer” — when called it <strong>does</strong> something (get weather, send mail). A skill is an “operating manual” — it declares <strong>domain knowledge</strong> as a discoverable, loadable module. A skill even exposes itself through three framework-injected tools (<code>load_skill</code>/<code>read_skill_resource</code>/<code>run_skill_script</code>); so a skill doesn't replace tools — it's the layer that lets the model “learn how, then act”.",
                },
            },
            {
                "q": {
                    "zh": "<code>SkillFrontmatter</code>（<code>name</code>/<code>description</code> 等）的主要作用是？",
                    "en": "What is <code>SkillFrontmatter</code> (<code>name</code>/<code>description</code>, etc.) mainly for?",
                },
                "opts": [
                    {
                        "zh": "<strong>发现用的 L1 元信息</strong>：被广告进系统提示，让模型决定要不要 <code>load_skill</code>",
                        "en": "<strong>L1 discovery metadata</strong>: advertised into the system prompt so the model can decide whether to <code>load_skill</code>",
                    },
                    {"zh": "存放技能要执行的全部脚本代码", "en": "It stores all the script code the skill will run"},
                    {"zh": "配置 Agent 用哪个模型厂商", "en": "It configures which model vendor the Agent uses"},
                    {"zh": "记录对话历史", "en": "It records the conversation history"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>_skills.py:557</code> 把 frontmatter 称为“L1 discovery metadata”——它是技能的“目录卡片”：name 要符合命名规则（小写字母/数字/连字符），description 让模型判断对口与否。只有这一层进“广告”，正文与资源都在更贵的后续步骤按需装载。把元信息单列，正是声明式技能能低成本被发现的前提。",
                    "en": "<code>_skills.py:557</code> calls the frontmatter “L1 discovery metadata” — the skill's “catalog card”: the name must follow the rules (lowercase letters/digits/hyphens), and the description lets the model judge relevance. Only this layer is advertised; the body and resources load on demand in the pricier later steps. Splitting metadata out is exactly what lets a declarative skill be discovered cheaply.",
                },
            },
        ],
        "open": [
            {
                "zh": "为你的领域设计一个技能（如“发票合规检查”）：(1) 哪些内容应放进 <code>instructions</code>、哪些做成 <code>InlineSkillResource</code> 资源、哪些适合做成需审批的 <code>InlineSkillScript</code> 脚本？(2) 如果把这些知识全塞进系统提示，会在 token 成本、可维护性、复用性上分别付出什么代价？(3) 你会在什么时刻设 <code>require_script_approval=True</code>？",
                "en": "Design a skill for your domain (e.g. “invoice compliance check”): (1) what belongs in <code>instructions</code>, what should be an <code>InlineSkillResource</code>, and what fits an approval-gated <code>InlineSkillScript</code>? (2) If you instead crammed all of it into the system prompt, what would you pay in token cost, maintainability, and reuse? (3) When would you set <code>require_script_approval=True</code>?",
            },
        ],
    },
    "24-mcp.html": {
        "mcq": [
            {
                "q": {
                    "zh": "下面哪句对 <code>MCPTool</code> 基类的描述是<strong>正确</strong>的？",
                    "en": "Which statement about the <code>MCPTool</code> base class is <strong>correct</strong>?",
                },
                "opts": [
                    {
                        "zh": "它<strong>不能直接实例化</strong>，要用 <code>MCPStdioTool</code>/<code>MCPStreamableHTTPTool</code>/<code>MCPWebsocketTool</code> 之一；连接、工具发现、转发都在它里面",
                        "en": "It <strong>cannot be instantiated directly</strong>; use one of <code>MCPStdioTool</code>/<code>MCPStreamableHTTPTool</code>/<code>MCPWebsocketTool</code>; connection, discovery and forwarding live in it",
                    },
                    {"zh": "它是一个具体的 stdio 实现，HTTP 要另写一套", "en": "It is a concrete stdio implementation; HTTP needs a separate stack"},
                    {"zh": "它负责训练模型", "en": "It is responsible for training the model"},
                    {"zh": "每种传输都有完全独立、互不共享的代码", "en": "Each transport has fully independent, non-shared code"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>_mcp.py:263</code> 的文档明说 <code>MCPTool</code> 是基类、不能直接用，必须选一个传输子类。连接生命周期（<code>connect</code> <code>:801</code>）、工具发现（<code>load_tools</code> <code>:1208</code> → <code>list_tools</code>）、调用转发（<code>call_tool</code> <code>:1422</code> → <code>session.call_tool</code>）都在基类里；子类（<code>:2110/:2254/:2456</code>）只决定“拿什么 client 建连接”。所以换传输不用改 Agent 代码。",
                    "en": "The docstring at <code>_mcp.py:263</code> says <code>MCPTool</code> is a base class you cannot use directly — you must pick a transport subclass. The connection lifecycle (<code>connect</code> <code>:801</code>), tool discovery (<code>load_tools</code> <code>:1208</code> → <code>list_tools</code>) and call forwarding (<code>call_tool</code> <code>:1422</code> → <code>session.call_tool</code>) all live in the base; subclasses (<code>:2110/:2254/:2456</code>) only decide “which client builds the connection”. That's why swapping transport needs no Agent change.",
                },
            },
            {
                "q": {
                    "zh": "本地开发想接一个 CLI 式的工具服务器，最合适的传输是？",
                    "en": "For local dev wiring up a CLI-style tool server, the most fitting transport is?",
                },
                "opts": [
                    {
                        "zh": "<code>MCPStdioTool</code>：启动<strong>本地子进程</strong>走 stdin/stdout，无需网络",
                        "en": "<code>MCPStdioTool</code>: launches a <strong>local subprocess</strong> over stdin/stdout, no network needed",
                    },
                    {"zh": "<code>MCPStreamableHTTPTool</code>：必须先部署一个公网 HTTPS 服务", "en": "<code>MCPStreamableHTTPTool</code>: requires deploying a public HTTPS service first"},
                    {"zh": "<code>MCPWebsocketTool</code>：必须先建立长连接网关", "en": "<code>MCPWebsocketTool</code>: requires standing up a long-connection gateway"},
                    {"zh": "三者都不行，本地工具不能用 MCP", "en": "None work; local tools can't use MCP"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>MCPStdioTool</code>（<code>:2110</code>）用 <code>command/args</code> 拉起一个本地子进程，经 stdio 通信，<strong>无需网络</strong>，是本地 CLI / 开发调试最顺手的选择；远程生产则首选 <code>MCPStreamableHTTPTool</code>（<code>:2254</code>，可带 <code>headers</code>/<code>header_provider</code> 鉴权），需要双向实时推送再用 <code>MCPWebsocketTool</code>（<code>:2456</code>）。三种传输上层 Agent 代码一致。",
                    "en": "<code>MCPStdioTool</code> (<code>:2110</code>) uses <code>command/args</code> to launch a local subprocess and talks over stdio with <strong>no network</strong> — the smoothest pick for local CLIs / dev debugging; remote production favors <code>MCPStreamableHTTPTool</code> (<code>:2254</code>, with <code>headers</code>/<code>header_provider</code> for auth), and bidirectional real-time push uses <code>MCPWebsocketTool</code> (<code>:2456</code>). The Agent code is identical across all three.",
                },
            },
            {
                "q": {
                    "zh": "MCP 服务器加了一个新工具。你的 Agent 要怎么改才能用上它？",
                    "en": "An MCP server adds a new tool. What must your Agent change to use it?",
                },
                "opts": [
                    {
                        "zh": "基本<strong>不用改</strong>：<code>list_tools()</code> 在运行时发现新工具，自动包成本地 <code>FunctionTool</code> 交给模型",
                        "en": "Basically <strong>nothing</strong>: <code>list_tools()</code> discovers it at run time and auto-wraps it as a local <code>FunctionTool</code> for the model",
                    },
                    {"zh": "要为新工具手写一个适配器类", "en": "Hand-write an adapter class for the new tool"},
                    {"zh": "要重新训练模型认识它", "en": "Retrain the model to recognize it"},
                    {"zh": "要把传输从 stdio 换成 HTTP", "en": "Switch the transport from stdio to HTTP"},
                ],
                "answer": 0,
                "why": {
                    "zh": "MCP 的工具是<strong>运行时发现</strong>的，不是写死的：连接后 <code>load_tools()</code>（<code>:1208</code>）调 <code>session.list_tools()</code> 拉清单，每个远端工具被包成本地 <code>FunctionTool</code> 放进 <code>.functions</code>（<code>:637</code>），其 schema 自动交给模型。这正是 MCP 把 N×M 对接降为 N+M 的关键——远端加工具，客户端零改动即可用。",
                    "en": "MCP tools are <strong>discovered at run time</strong>, not hardcoded: after connecting, <code>load_tools()</code> (<code>:1208</code>) calls <code>session.list_tools()</code> to pull the list, each remote tool is wrapped as a local <code>FunctionTool</code> in <code>.functions</code> (<code>:637</code>), and its schema is handed to the model automatically. This is exactly how MCP turns N×M integration into N+M — the server adds a tool, the client needs zero changes.",
                },
            },
        ],
        "open": [
            {
                "zh": "你有一个内部“知识库检索”工具，想让公司里多个不同的 Agent 应用都能用。(1) 用 MCP 暴露成服务器后，对接成本如何从 N×M 降到 N+M？(2) 本地开发期与线上生产你会分别选哪种传输（<code>Stdio</code>/<code>HTTP</code>/<code>WebSocket</code>），为什么？(3) 既然 MCP 工具是“另一个进程”，为什么连接必须用 <code>async with</code> 成对管理？",
                "en": "You have an internal “knowledge-base search” tool you want reachable from several different Agent apps in your company. (1) Once exposed as an MCP server, how does integration cost drop from N×M to N+M? (2) Which transport (<code>Stdio</code>/<code>HTTP</code>/<code>WebSocket</code>) would you pick for local dev vs production, and why? (3) Since an MCP tool is “another process”, why must the connection be managed in pairs with <code>async with</code>?",
            },
        ],
    },
    "25-hosted-agents.html": {
        "mcq": [
            {
                "q": {
                    "zh": "把本地 Agent 用 <code>InvocationsHostServer</code>/<code>ResponsesHostServer</code> 托管，主要替你接管了什么？",
                    "en": "Hosting a local Agent with <code>InvocationsHostServer</code>/<code>ResponsesHostServer</code> mainly takes over what for you?",
                },
                "opts": [
                    {
                        "zh": "<strong>运维脏活</strong>：会话隔离、历史/检查点、审批存储、伸缩与监控——业务代码几乎不写这些",
                        "en": "<strong>The ops chores</strong>: session isolation, history/checkpoints, approval storage, scaling and monitoring — your business code writes almost none of it",
                    },
                    {"zh": "替你把模型微调到更高准确率", "en": "Fine-tunes the model to higher accuracy for you"},
                    {"zh": "自动帮你写 Agent 的 instructions 和工具", "en": "Auto-writes your Agent's instructions and tools"},
                    {"zh": "把云端调用全部改成本地进程内调用", "en": "Turns all cloud calls into in-process local calls"},
                ],
                "answer": 0,
                "why": {
                    "zh": "“2 行部署”的本质是托管层接管了上生产后那串麻烦：<code>InvocationsHostServer</code>（<code>_invocations.py:10</code>）按 <code>session_id</code> 隔离 <code>AgentSession</code>；<code>ResponsesHostServer</code>（<code>:341</code>）接管历史/检查点、审批存储，并交给云端运行时做伸缩与监控。它<strong>不</strong>训练模型、也不替你写业务逻辑——你只写最上层的 Agent。",
                    "en": "The essence of “2-line deploy” is the hosting layer absorbing the post-production tail: <code>InvocationsHostServer</code> (<code>_invocations.py:10</code>) isolates <code>AgentSession</code> by <code>session_id</code>; <code>ResponsesHostServer</code> (<code>:341</code>) takes over history/checkpoints and approval storage, and leaves scaling/monitoring to the cloud runtime. It does <strong>not</strong> train the model or write your business logic — you only write the top-layer Agent.",
                },
            },
            {
                "q": {
                    "zh": "<code>InvocationsHostServer</code> 与 <code>ResponsesHostServer</code> 最贴切的区别是？",
                    "en": "The most accurate difference between <code>InvocationsHostServer</code> and <code>ResponsesHostServer</code> is?",
                },
                "opts": [
                    {
                        "zh": "Invocations 极简（<code>{\"message\"}</code> 进、<code>{\"response\",\"session_id\"}</code> 出）；Responses 提供完整 Foundry 协议（流式、审批、检查点）",
                        "en": "Invocations is minimal (<code>{\"message\"}</code> in, <code>{\"response\",\"session_id\"}</code> out); Responses offers the full Foundry protocol (streaming, approval, checkpoints)",
                    },
                    {"zh": "Invocations 只能跑一次，Responses 能跑多次", "en": "Invocations runs once, Responses runs many times"},
                    {"zh": "Responses 只能本地、Invocations 只能上云", "en": "Responses is local-only, Invocations is cloud-only"},
                    {"zh": "两者完全相同，只是名字不同", "en": "They are identical, just named differently"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>InvocationsHostServer</code> 是轻量 JSON 请求/响应，适合快速部署与简单场景；<code>ResponsesHostServer</code> 实现完整的 Azure AI Foundry Responses 协议——支持流式、人在环审批（<code>ApprovalStorage</code>）、工作流检查点，并接管历史。两者上层 Agent 写法一致，<strong>切换只需换一个类名</strong>，按需要的协议深度选择即可。",
                    "en": "<code>InvocationsHostServer</code> is a lightweight JSON request/response, good for quick deploys and simple cases; <code>ResponsesHostServer</code> implements the full Azure AI Foundry Responses protocol — streaming, human-in-the-loop approval (<code>ApprovalStorage</code>), workflow checkpoints, and it owns history. The Agent code is identical for both, so <strong>switching is just a class-name change</strong> chosen by the protocol depth you need.",
                },
            },
            {
                "q": {
                    "zh": "托管下，一个需审批的工具被触发时，<code>ApprovalStorage</code> 起什么作用？",
                    "en": "Under hosting, when an approval-required tool is triggered, what does <code>ApprovalStorage</code> do?",
                },
                "opts": [
                    {
                        "zh": "把审批请求<strong>持久化</strong>（<code>save_approval_request</code>），人审后再<code>load_approval_request</code> 取回放行——进程被回收也不丢",
                        "en": "It <strong>persists</strong> the approval request (<code>save_approval_request</code>); after a human approves, <code>load_approval_request</code> fetches it to release — surviving a recycled process",
                    },
                    {"zh": "自动批准所有工具，不需要人", "en": "Auto-approves every tool, no human needed"},
                    {"zh": "永久禁止该工具运行", "en": "Permanently blocks that tool from ever running"},
                    {"zh": "把审批日志发到模型里当训练数据", "en": "Sends approval logs into the model as training data"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>ApprovalStorage</code> 是个 Protocol（<code>_responses.py:124</code>），只有 <code>save_approval_request(id, request)</code>（<code>:127</code>）与 <code>load_approval_request(id)</code>（<code>:131</code>）两个方法。危险工具触发时，host server 把审批请求落盘并把“待审批”作为事件返回、挂起该步；人审后凭 id 取回放行。因为状态外置，托管实例即便在两次请求间被回收，审批也能续上——这正是生产级人在环的关键。",
                    "en": "<code>ApprovalStorage</code> is a Protocol (<code>_responses.py:124</code>) with just two methods: <code>save_approval_request(id, request)</code> (<code>:127</code>) and <code>load_approval_request(id)</code> (<code>:131</code>). When a dangerous tool fires, the host server persists the approval request, returns “pending” as an event and suspends that step; after a human approves, it fetches by id and releases. Because state is externalized, a recycled hosted instance can still resume the approval between requests — the crux of production-grade human-in-the-loop.",
                },
            },
        ],
        "open": [
            {
                "zh": "你要把一个会“发邮件 / 退款”的 Agent 上生产。(1) 为什么托管层要求 Agent <strong>无内存态、状态外置</strong>？如果你坚持把上下文放进内存里的 context provider，云端实例被回收时会发生什么？(2) 这两个危险动作你会怎么用 <code>ApprovalStorage</code> 接人在环？(3) 你会选 <code>Invocations</code> 还是 <code>Responses</code> 模式，理由是什么？",
                "en": "You're putting an Agent that can “send email / issue refunds” into production. (1) Why does the hosting layer require the Agent to be <strong>stateless with externalized state</strong>? If you insist on keeping context in an in-memory context provider, what happens when a cloud instance is recycled? (2) How would you wire these two dangerous actions through <code>ApprovalStorage</code> for human-in-the-loop? (3) Would you pick <code>Invocations</code> or <code>Responses</code> mode, and why?",
            },
        ],
    },
    "26-a2a-agui.html": {
        "mcq": [
            {
                "q": {
                    "zh": "<code>A2A</code> 与 <code>AG-UI</code> 两个协议的方向，最准确的概括是？",
                    "en": "What most accurately captures the direction of the <code>A2A</code> and <code>AG-UI</code> protocols?",
                },
                "opts": [
                    {
                        "zh": "<strong>A2A 是 Agent↔Agent</strong>（请求/响应，JSON-RPC over HTTP）；<strong>AG-UI 是 Agent↔前端</strong>（单向事件流，SSE）",
                        "en": "<strong>A2A is Agent↔Agent</strong> (request/response, JSON-RPC over HTTP); <strong>AG-UI is Agent↔frontend</strong> (one-way event stream, SSE)",
                    },
                    {"zh": "两者都是 Agent↔前端，只是编码不同", "en": "Both are Agent↔frontend, just different encodings"},
                    {"zh": "A2A 管 UI，AG-UI 管 Agent 互调", "en": "A2A handles the UI, AG-UI handles Agent interop"},
                    {"zh": "两者都只能在同一进程内使用", "en": "Both work only within a single process"},
                ],
                "answer": 0,
                "why": {
                    "zh": "两者<strong>正交</strong>：A2A 解决&quot;横向&quot;的 Agent 互联（一个 Agent 调用另一个 Agent，走 JSON-RPC over HTTP 的请求/响应），AG-UI 解决&quot;纵向&quot;的 Agent 向人汇报（把执行过程作为结构化事件经 SSE 推给前端）。真实系统常常同时用——编排 Agent 用 A2A 调远程子 Agent，同时用 AG-UI 把进度实时画给用户。",
                    "en": "They are <strong>orthogonal</strong>: A2A solves &quot;horizontal&quot; Agent interconnect (one Agent calling another via request/response JSON-RPC over HTTP), while AG-UI solves &quot;vertical&quot; Agent-to-human reporting (pushing the run as structured events over SSE to the frontend). Real systems often use both — the orchestrator calls a remote sub-Agent over A2A while painting progress to the user over AG-UI.",
                },
            },
            {
                "q": {
                    "zh": "在 A2A 里，<code>A2AAgent</code> 与 <code>A2AExecutor</code> 的角色分别是？",
                    "en": "In A2A, what are the respective roles of <code>A2AAgent</code> and <code>A2AExecutor</code>?",
                },
                "opts": [
                    {
                        "zh": "<code>A2AAgent</code> 是<strong>调出去</strong>的本地代理（客户端）；<code>A2AExecutor</code> 是<strong>被调用</strong>的服务端包装",
                        "en": "<code>A2AAgent</code> is the <strong>outbound</strong> local proxy (client); <code>A2AExecutor</code> is the <strong>inbound</strong> server-side wrapper",
                    },
                    {"zh": "两者都是客户端，只是一个同步一个异步", "en": "Both are clients, one sync one async"},
                    {"zh": "<code>A2AAgent</code> 是服务端，<code>A2AExecutor</code> 是客户端", "en": "<code>A2AAgent</code> is the server, <code>A2AExecutor</code> is the client"},
                    {"zh": "两者是同一个类的别名", "en": "They are aliases of the same class"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>A2AAgent</code>（<code>_agent.py:154</code>）是本地代理：你像调本地 Agent 一样 <code>await a2a.run(...)</code>，它把请求经 JSON-RPC over HTTP 发往远程。<code>A2AExecutor</code>（<code>_a2a_executor.py:29</code>，<code>execute()</code>:139）在远程侧把本地 Agent 暴露为 A2A 服务。关键：同一个 Agent 可以既当别人的客户端、又把自己 expose 成服务端——这正是 Agent 网络层层编排的根基。",
                    "en": "<code>A2AAgent</code> (<code>_agent.py:154</code>) is the local proxy: you <code>await a2a.run(...)</code> as if calling a local Agent, and it ships the request over JSON-RPC over HTTP to the remote. <code>A2AExecutor</code> (<code>_a2a_executor.py:29</code>, <code>execute()</code>:139) exposes a local Agent as an A2A service on the remote side. Crucially, one Agent can be both a client and a server — the basis for layered Agent orchestration.",
                },
            },
            {
                "q": {
                    "zh": "用 <code>add_agent_framework_fastapi_endpoint</code> 暴露 Agent 后，一次正常 AG-UI 运行的事件顺序是？",
                    "en": "After exposing an Agent with <code>add_agent_framework_fastapi_endpoint</code>, what is the event order of a normal AG-UI run?",
                },
                "opts": [
                    {
                        "zh": "<code>RunStarted</code> → 内容事件（<code>TextMessage*</code> / <code>ToolCall*</code>）→ <code>RunFinished</code>（出错则 <code>RunError</code>）",
                        "en": "<code>RunStarted</code> → content events (<code>TextMessage*</code> / <code>ToolCall*</code>) → <code>RunFinished</code> (or <code>RunError</code> on failure)",
                    },
                    {"zh": "只发一个 <code>RunFinished</code>，没有中间事件", "en": "Just one <code>RunFinished</code>, no intermediate events"},
                    {"zh": "<code>RunFinished</code> → <code>RunStarted</code> → 内容", "en": "<code>RunFinished</code> → <code>RunStarted</code> → content"},
                    {"zh": "事件顺序随机，前端要自己排序", "en": "Events arrive in random order; the frontend must sort them"},
                ],
                "answer": 0,
                "why": {
                    "zh": "这就是 <code>AgentFrameworkAgent</code> 的&quot;简单线性流&quot;（<code>_agent.py:70</code> 原注释）：先 <code>yield RunStartedEvent(run_id, thread_id)</code>（<code>_agent_run.py:885</code>），中间是文本增量（<code>TextMessageStart/Content/End</code>）与工具调用（<code>ToolCallStart/Args/End/Result</code>），最后 <code>RunFinishedEvent</code>；出错发 <code>RunErrorEvent</code>（<code>_endpoint.py:12</code>）。所有事件类型来自 <code>ag_ui.core</code>，是跨框架开放协议。",
                    "en": "This is <code>AgentFrameworkAgent</code>'s &quot;simple linear flow&quot; (<code>_agent.py:70</code> original comment): first <code>yield RunStartedEvent(run_id, thread_id)</code> (<code>_agent_run.py:885</code>), then text deltas (<code>TextMessageStart/Content/End</code>) and tool calls (<code>ToolCallStart/Args/End/Result</code>), and finally <code>RunFinishedEvent</code>; an error emits <code>RunErrorEvent</code> (<code>_endpoint.py:12</code>). All event types come from <code>ag_ui.core</code>, a cross-framework open protocol.",
                },
            },
        ],
        "open": [
            {
                "zh": "你在搭一个&quot;研究助手&quot;：编排 Agent 要调用一个独立部署的&quot;检索 Agent&quot;，同时让用户在网页上实时看到进度。(1) 这两条边你分别用 <code>A2A</code> 还是 <code>AG-UI</code>？为什么说它们&quot;正交&quot;、可以同时用？(2) 检索 Agent 在另一台机器上，<code>A2AAgent</code> 和 <code>A2AExecutor</code> 各自部署在哪一侧？(3) 用户能看到&quot;正在检索…检索完成&quot;，这背后对应哪几个 AG-UI 事件？",
                "en": "You're building a &quot;research assistant&quot;: an orchestrator Agent calls an independently deployed &quot;retrieval Agent&quot; while the user watches progress live in a web page. (1) Which edge uses <code>A2A</code> vs <code>AG-UI</code>, and why are they &quot;orthogonal&quot; so you can use both at once? (2) The retrieval Agent runs on another machine — which side hosts <code>A2AAgent</code> vs <code>A2AExecutor</code>? (3) The user sees &quot;retrieving… done&quot; — which AG-UI events back that up?",
            },
        ],
    },
    "27-eval-timetravel.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在 CI 里，<code>evaluate_agent(...)</code> 之后那行 <code>results[0].raise_for_status()</code> 的作用是？",
                    "en": "In CI, what does the line <code>results[0].raise_for_status()</code> after <code>evaluate_agent(...)</code> do?",
                },
                "opts": [
                    {
                        "zh": "评分不达标时<strong>抛错</strong>，让流水线变红——把质量回归挡在合并前",
                        "en": "<strong>Raises</strong> when scores fall short, turning the pipeline red — blocking a quality regression before merge",
                    },
                    {"zh": "把所有失败的 query 自动重跑直到通过", "en": "Auto-reruns every failed query until it passes"},
                    {"zh": "提高模型温度以获得更好的分数", "en": "Raises the model temperature for better scores"},
                    {"zh": "把评估结果上传到生产数据库", "en": "Uploads the eval results to the production database"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>evaluate_agent</code>（<code>_evaluation.py:1629</code>）为每个 query 调 <code>agent.run()</code>、转成 <code>EvalItem</code>、交 <code>Evaluator.evaluate</code> 打分，返回 <code>list[EvalResults]</code>。<code>raise_for_status()</code>（<code>:470</code>）类似 <code>requests</code> 的同名方法：分数不达标就抛异常。放进 CI，它就把评估从&quot;人工抽查&quot;变成&quot;自动护栏&quot;——改了 prompt/模型导致 <code>passed/total</code>（<code>:441/:451</code>）下滑时，合并会被自动拦下。",
                    "en": "<code>evaluate_agent</code> (<code>_evaluation.py:1629</code>) calls <code>agent.run()</code> per query, converts each into an <code>EvalItem</code>, scores via <code>Evaluator.evaluate</code>, and returns <code>list[EvalResults]</code>. <code>raise_for_status()</code> (<code>:470</code>) mirrors the <code>requests</code> method of the same name: it raises when scores fall short. Dropped into CI, it turns evaluation from a &quot;manual spot-check&quot; into an &quot;automated guardrail&quot; — when a prompt/model change drops <code>passed/total</code> (<code>:441/:451</code>), the merge is blocked automatically.",
                },
            },
            {
                "q": {
                    "zh": "<code>WorkflowCheckpoint</code> 里哪个字段把一串检查点串成可回溯的&quot;时间线&quot;？",
                    "en": "Which field of <code>WorkflowCheckpoint</code> chains a series of checkpoints into a rewindable &quot;timeline&quot;?",
                },
                "opts": [
                    {
                        "zh": "<code>previous_checkpoint_id</code>——指向上一帧的反向指针，链起来就是时间线",
                        "en": "<code>previous_checkpoint_id</code> — a back-pointer to the prior frame; the chain is the timeline",
                    },
                    {"zh": "<code>iteration_count</code>——它只是个递增计数器", "en": "<code>iteration_count</code> — it's just an incrementing counter"},
                    {"zh": "<code>graph_signature_hash</code>——它只校验拓扑", "en": "<code>graph_signature_hash</code> — it only validates topology"},
                    {"zh": "<code>workflow_name</code>——它只是个名字", "en": "<code>workflow_name</code> — it's just a name"},
                ],
                "answer": 0,
                "why": {
                    "zh": "<code>WorkflowCheckpoint</code>（<code>_checkpoint.py:31</code>）的 <code>previous_checkpoint_id</code>（<code>:75</code>）指向上一张检查点，串成一条可倒回任意一帧的链=时间线。<code>graph_signature_hash</code>（<code>:72</code>）负责回放前校验拓扑一致、<code>iteration_count</code>（<code>:84</code>）记迭代号、<code>workflow_name</code>（<code>:71</code>）标识归属——它们都重要，但&quot;时间线&quot;靠的是 <code>previous_checkpoint_id</code> 这条链。",
                    "en": "On <code>WorkflowCheckpoint</code> (<code>_checkpoint.py:31</code>), <code>previous_checkpoint_id</code> (<code>:75</code>) points at the prior checkpoint, forming a chain rewindable to any frame — the timeline. <code>graph_signature_hash</code> (<code>:72</code>) validates topology before replay, <code>iteration_count</code> (<code>:84</code>) records the iteration, and <code>workflow_name</code> (<code>:71</code>) identifies ownership — all matter, but the &quot;timeline&quot; comes from the <code>previous_checkpoint_id</code> chain.",
                },
            },
            {
                "q": {
                    "zh": "一个 5 步工作流在第 4 步失败。开启了检查点后，最省的恢复方式是？",
                    "en": "A 5-step workflow fails at step 4. With checkpointing enabled, what is the cheapest way to recover?",
                },
                "opts": [
                    {
                        "zh": "<code>wf.run(checkpoint_id=cp3, checkpoint_storage=storage)</code>——从断点那帧回放，已完成步骤跳过",
                        "en": "<code>wf.run(checkpoint_id=cp3, checkpoint_storage=storage)</code> — replay from the breakpoint frame; completed steps are skipped",
                    },
                    {"zh": "从头 <code>wf.run(message=...)</code> 重跑全部 5 步", "en": "Rerun all 5 steps from scratch with <code>wf.run(message=...)</code>"},
                    {"zh": "删掉检查点再重建工作流", "en": "Delete the checkpoints and rebuild the workflow"},
                    {"zh": "手动把每步的中间结果复制粘贴回去", "en": "Manually copy-paste each step's intermediate result back in"},
                ],
                "answer": 0,
                "why": {
                    "zh": "传 <code>checkpoint_id</code>（可选配 <code>checkpoint_storage</code>）给 <code>wf.run()</code>（<code>_workflow.py:681</code>）会触发内部 <code>restore_from_checkpoint</code>（<code>:660</code>）：从该帧恢复完整状态，已完成的步骤直接跳过，只从断点续跑——省时也省 token。检查点用 <code>get_latest(workflow_name=)</code>（<code>:169</code>）或按 id <code>load</code>（<code>:133</code>）取回；存储有 <code>InMemoryCheckpointStorage</code>（<code>:192</code>）和 <code>FileCheckpointStorage</code>（<code>:239</code>）两种实现。",
                    "en": "Passing <code>checkpoint_id</code> (optionally with <code>checkpoint_storage</code>) to <code>wf.run()</code> (<code>_workflow.py:681</code>) triggers the internal <code>restore_from_checkpoint</code> (<code>:660</code>): it restores full state from that frame, skips completed steps, and resumes only from the breakpoint — saving time and tokens. Fetch checkpoints via <code>get_latest(workflow_name=)</code> (<code>:169</code>) or by id with <code>load</code> (<code>:133</code>); storage comes as <code>InMemoryCheckpointStorage</code> (<code>:192</code>) or <code>FileCheckpointStorage</code> (<code>:239</code>).",
                },
            },
        ],
        "open": [
            {
                "zh": "你的 Agent 在一次回归里&quot;第 3 条 query&quot;评分掉了，而它背后是一个多步工作流。(1) 评估（<code>evaluate_agent</code>）和时间旅行（<code>wf.run(checkpoint_id=)</code>）在&quot;发现→诊断→修复→验证&quot;闭环里各自负责哪一段？(2) 为什么说检查点是&quot;确定性快照&quot;、<code>graph_signature_hash</code> 在回放时保护了什么？(3) 如果你改了工作流的图结构再去回放旧检查点，会发生什么、为什么这是好事？",
                "en": "Your Agent regresses: &quot;query 3&quot; drops in score, and behind it sits a multi-step workflow. (1) In the &quot;detect → diagnose → fix → verify&quot; loop, which stage does evaluation (<code>evaluate_agent</code>) own versus time-travel (<code>wf.run(checkpoint_id=)</code>)? (2) Why is a checkpoint a &quot;deterministic snapshot&quot;, and what does <code>graph_signature_hash</code> protect during replay? (3) If you change the workflow's graph structure and then replay an old checkpoint, what happens and why is that a good thing?",
            },
        ],
    },
    "21-vs-others.html": {
        "mcq": [
            {
                "q": {
                    "zh": "MAF 同时给了底层 <code>WorkflowBuilder</code>（手画图）和上层预置编排（Sequential / Concurrent / …）。相比 LangGraph 只有手画图这一级，这种“两层”设计的好处是？",
                    "en": "MAF offers both a low-level <code>WorkflowBuilder</code> (hand-drawn graph) and high-level prebuilt orchestrations (Sequential / Concurrent / …). Versus LangGraph's single graph level, what's the benefit of this &quot;two-tier&quot; design?",
                },
                "opts": [
                    {
                        "zh": "让框架代码量更大，显得更专业",
                        "en": "It makes the framework bigger and look more professional",
                    },
                    {
                        "zh": "强制所有人都用图，统一心智",
                        "en": "It forces everyone onto graphs for a uniform mental model",
                    },
                    {
                        "zh": "简单任务用预置编排几行搞定，复杂拓扑再下沉到手画图——不用为简单场景付出“手画每条边”的成本",
                        "en": "Simple tasks need only a few lines of prebuilt orchestration; complex topologies drop down to the hand-drawn graph - you don't pay the &quot;draw every edge&quot; cost for simple cases",
                    },
                    {
                        "zh": "因为预置编排比手画图跑得快",
                        "en": "Because prebuilt orchestrations run faster than hand-drawn graphs",
                    },
                ],
                "answer": 2,
                "why": {
                    "zh": "抽象分层让你<strong>按需选粒度</strong>：约 80% 场景预置编排就够（低心智负担），剩下复杂拓扑再下沉到 <code>WorkflowBuilder</code>。LangGraph 只有图这一级，简单串行也得手画节点和边。",
                    "en": "Layered abstractions let you <strong>pick granularity on demand</strong>: ~80% of cases are covered by prebuilt orchestrations (low cognitive load), and the rest drop to <code>WorkflowBuilder</code>. LangGraph has only the graph level, so even a simple sequence means hand-drawing nodes and edges.",
                },
            },
            {
                "q": {
                    "zh": "为什么说“新项目直接上 MAF”对许多 SK / AutoGen 用户通常是合理建议？",
                    "en": "Why is &quot;use MAF directly for new projects&quot; usually sound advice for many SK / AutoGen users?",
                },
                "opts": [
                    {
                        "zh": "MAF 是微软把 SK 和 AutoGen 统一演进的继任方向，吸收了二者能力（连接器 / Planner + 多 Agent），且维护重心已转向 MAF",
                        "en": "MAF is Microsoft's converged successor to SK and AutoGen, absorbing both (connectors / Planner + multi-agent), and maintenance focus has shifted to MAF",
                    },
                    {
                        "zh": "因为 SK 和 AutoGen 已经被删除了",
                        "en": "Because SK and AutoGen have been deleted",
                    },
                    {
                        "zh": "因为 MAF 不兼容任何旧代码，必须全部重写",
                        "en": "Because MAF is incompatible with all old code and forces a full rewrite",
                    },
                    {
                        "zh": "因为 MAF 是其中唯一开源的",
                        "en": "Because MAF is the only open-source one",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "MAF 继承 SK 的企业连接器 / Planner 思想和 AutoGen 的 Magentic-One（指挥官 + 工人）多 Agent 范式，再加图编排 / DurableTask / 统一 <code>ChatClient</code>。官方把它定位为“下一代”，所以新项目可直接用，老项目能渐进迁移、共存。",
                    "en": "MAF inherits SK's enterprise connectors / Planner ideas and AutoGen's Magentic-One (manager + workers) multi-agent paradigm, plus graph orchestration / DurableTask / a unified <code>ChatClient</code>. It's positioned as the &quot;next generation&quot;, so new projects can adopt it directly while old ones migrate gradually and coexist.",
                },
            },
            {
                "q": {
                    "zh": "关于“MAF vs LangGraph”，下面哪个说法最准确？",
                    "en": "Regarding &quot;MAF vs LangGraph&quot;, which statement is most accurate?",
                },
                "opts": [
                    {
                        "zh": "用了 MAF 就不能再碰任何 LangChain 生态",
                        "en": "Using MAF means you can't touch any LangChain ecosystem",
                    },
                    {
                        "zh": "它们不一定二选一：可以用 MAF 的 Agent / ChatClient 配 LangGraph 的编排，因为编排层是可替换的",
                        "en": "They aren't necessarily either/or: you can pair MAF's Agent / ChatClient with LangGraph's orchestration, because the orchestration layer is swappable",
                    },
                    {
                        "zh": "两者底层其实是同一份代码",
                        "en": "The two are really the same code underneath",
                    },
                    {
                        "zh": "LangGraph 不支持检查点",
                        "en": "LangGraph doesn't support checkpointing",
                    },
                ],
                "answer": 1,
                "why": {
                    "zh": "框架边界是<strong>分层</strong>的——Agent / ChatClient 抽象与编排层可以解耦。混用可行（MAF 做 Agent，LangGraph 做图编排）。选型是“主线选谁”，而不是互斥的非黑即白。",
                    "en": "Framework boundaries are <strong>layered</strong> - the Agent / ChatClient abstraction and the orchestration layer can be decoupled. Mixing is viable (MAF for Agents, LangGraph for graph orchestration). Picking is choosing a &quot;main line&quot;, not a mutually exclusive split.",
                },
            },
        ],
        "open": [
            {
                "zh": "你的团队已有一套 Semantic Kernel 代码，现在要做一个需要“多 Agent 协作 + 检查点恢复”的新功能。基于本课对比，说说你会<strong>直接重写成 MAF</strong> 还是 <strong>SK / MAF 共存渐进迁移</strong>，并给出两条支撑你决定的具体理由（结合生产特性与迁移成本）。",
                "en": "Your team has a Semantic Kernel codebase and now needs a new feature requiring &quot;multi-agent collaboration + checkpoint recovery&quot;. Based on this lesson, would you <strong>rewrite directly in MAF</strong> or <strong>run SK / MAF side by side for gradual migration</strong>? Give two concrete reasons (weighing production features against migration cost).",
            },
        ],
    },
    "22-stack-map.html": {
        "mcq": [
            {
                "q": {
                    "zh": "MAF 的 <code>OpenAIChatClient</code> 能指向 vLLM / llama.cpp server / Ollama。这给你带来的最大好处是？",
                    "en": "MAF's <code>OpenAIChatClient</code> can point at vLLM / a llama.cpp server / Ollama. What's the biggest benefit?",
                },
                "opts": [
                    {
                        "zh": "开发时用云端 OpenAI API，上线切私有 vLLM，Agent 代码一行不改——推理层与编排层解耦",
                        "en": "Develop against the cloud OpenAI API, switch to private vLLM in production, and the Agent code doesn't change a line - inference and orchestration are decoupled",
                    },
                    {
                        "zh": "这些后端会自动让模型变得更聪明",
                        "en": "These backends automatically make the model smarter",
                    },
                    {
                        "zh": "因为它们其实是同一个模型",
                        "en": "Because they're actually the same model",
                    },
                    {
                        "zh": "只有这样才能使用工具调用",
                        "en": "Because tool calling only works this way",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "只要端点兼容 OpenAI API，<code>ChatClient</code> 就能接。L5（推理）与 L6（编排）解耦，意味着私有化部署、成本 / 延迟优化只是“换 L5”，不波及你写的 Agent 逻辑。",
                    "en": "As long as the endpoint speaks the OpenAI API, the <code>ChatClient</code> can connect. Decoupling L5 (inference) from L6 (orchestration) means private deployment and cost / latency tuning are just &quot;swap L5&quot;, leaving your Agent logic untouched.",
                },
            },
            {
                "q": {
                    "zh": "本课把编排分成链 / 图 / 多 Agent 对话 / Planner / 声明式几大流派。MAF 的特别之处在于？",
                    "en": "This lesson groups orchestration into schools: chain / graph / multi-agent chat / Planner / declarative. What makes MAF special?",
                },
                "opts": [
                    {
                        "zh": "它只支持声明式一种流派",
                        "en": "It supports only the declarative school",
                    },
                    {
                        "zh": "它发明了链式管道",
                        "en": "It invented the chain pipeline",
                    },
                    {
                        "zh": "它把“图”和“多 Agent 对话”统一进同一个框架，预置编排是糖、底层 Workflow 是引擎，可混用",
                        "en": "It unifies &quot;graph&quot; and &quot;multi-agent chat&quot; in one framework - prebuilt orchestrations are sugar, the underlying Workflow is the engine, and you can mix them",
                    },
                    {
                        "zh": "它要求每个项目只能选一种流派",
                        "en": "It requires each project to pick exactly one school",
                    },
                ],
                "answer": 2,
                "why": {
                    "zh": "多数框架押注单一流派（LangChain=链、LangGraph=图、AutoGen=对话、SK=Planner）。MAF 把图编排和多 Agent 对话收进<strong>一个引擎</strong>，让你在同一项目里按场景混搭，而不必跨框架拼装。",
                    "en": "Most frameworks bet on one school (LangChain=chain, LangGraph=graph, AutoGen=chat, SK=Planner). MAF folds graph orchestration and multi-agent chat into <strong>one engine</strong>, letting you mix per scenario within a single project instead of stitching frameworks together.",
                },
            },
            {
                "q": {
                    "zh": "你想给现有 MAF Agent 加“基于公司知识库回答”。按全栈分层，这主要是在改哪一层、为什么 Agent 逻辑基本不用动？",
                    "en": "You want an existing MAF Agent to &quot;answer from the company knowledge base&quot;. By the full-stack layering, which layer mainly changes, and why does Agent logic stay largely untouched?",
                },
                "opts": [
                    {
                        "zh": "主要改 L4（向量检索 / RAG），把检索到的上下文喂给 L6 的 Agent；分层让“加知识”变成接入新层，而不是重构",
                        "en": "Mainly L4 (vector search / RAG), feeding retrieved context into the L6 Agent; layering makes &quot;adding knowledge&quot; a matter of plugging in a layer, not refactoring",
                    },
                    {
                        "zh": "改 L7 应用层的 CSS",
                        "en": "Change the CSS in the L7 application layer",
                    },
                    {
                        "zh": "改 L5 推理层的 GPU 驱动",
                        "en": "Change the GPU driver in the L5 inference layer",
                    },
                    {
                        "zh": "必须把 Agent 拆成多个才能加知识",
                        "en": "You must split the Agent into several to add knowledge",
                    },
                ],
                "answer": 0,
                "why": {
                    "zh": "全栈分层让每种需求对应一层：私有模型→L5，知识库→L4，换前端→L7。RAG 是在 L4 取上下文再注入 L6 的 Agent，所以 Agent 编排逻辑稳定——这正是“看懂楼层布局才知道去哪接管线”。",
                    "en": "The full-stack layering maps each need to a layer: private model→L5, knowledge base→L4, new front end→L7. RAG fetches context at L4 and injects it into the L6 Agent, so the orchestration logic stays stable - exactly &quot;know the floor plan to know where to connect the pipes&quot;.",
                },
            },
        ],
        "open": [
            {
                "zh": "把你这门课学到的 MAF 能力放进本课的全栈坐标系：你主要在哪一层工作？如果要做一个“私有部署 + 带公司知识库 + 网页聊天界面”的产品，请分别说出你会在 L7 / L6 / L5 / L4 各做什么，以及为什么这种分层能让团队<strong>并行开发</strong>。",
                "en": "Place the MAF skills from this course into the full-stack map: which layer do you mainly work in? For a product that is &quot;privately deployed + backed by a company knowledge base + with a web chat UI&quot;, say what you'd do at each of L7 / L6 / L5 / L4, and why this layering lets a team <strong>work in parallel</strong>.",
            },
        ],
    },
    "31-glossary.html": {
        "mcq": [
            {
                "q": {
                    "zh": "按本课的「概念依赖图」，下面哪条依赖方向是<strong>对的</strong>？",
                    "en": "Per this lesson's concept dependency map, which dependency direction is <strong>correct</strong>?",
                },
                "opts": [
                    {
                        "zh": "Agent 建立在 ChatClient 之上，ChatClient 又建立在 Message / Content 这块基石之上",
                        "en": "Agent builds on ChatClient, and ChatClient builds on the Message / Content bedrock",
                    },
                    {"zh": "Message 建立在 Workflow 之上", "en": "Message builds on Workflow"},
                    {"zh": "ChatClient 建立在编排器（Sequential 等）之上", "en": "ChatClient builds on the orchestrators (Sequential, etc.)"},
                    {"zh": "OpenTelemetry 是其他所有概念的基石", "en": "OpenTelemetry is the bedrock of every other concept"},
                ],
                "answer": 0,
                "why": {
                    "zh": "依赖图从下往上：<strong>Message/Content</strong>（基石）→ <strong>ChatClient</strong>（通道）→ <strong>Agent</strong>（主体）→ 编排 → 生态 → 运维。上层站在下层之上，所以 Agent 依赖 ChatClient、ChatClient 依赖消息原子；Workflow/OTel 都在上层，不可能是基石。",
                    "en": "The map reads bottom-up: <strong>Message/Content</strong> (bedrock) → <strong>ChatClient</strong> (channel) → <strong>Agent</strong> (core) → orchestration → ecosystem → ops. Upper layers stand on lower ones, so Agent depends on ChatClient and ChatClient on the message atoms; Workflow/OTel sit on top and can't be the bedrock.",
                },
            },
            {
                "q": {
                    "zh": "你想确认「跨会话记忆」相关的类到底在哪个文件——速查表的<strong>哪一列</strong>直接给你答案？",
                    "en": "You want to confirm which file holds the &quot;cross-session memory&quot; classes&mdash;which <strong>column</strong> of the reference gives you that directly?",
                },
                "opts": [
                    {
                        "zh": "「源码位置」列：<span class=\"mono\">_sessions.py:348 / :410</span>（ContextProvider / HistoryProvider）",
                        "en": "The &quot;source location&quot; column: <span class=\"mono\">_sessions.py:348 / :410</span> (ContextProvider / HistoryProvider)",
                    },
                    {"zh": "「一句话定义」列", "en": "The &quot;one-line definition&quot; column"},
                    {"zh": "「所属课」列——它只给课号不给文件", "en": "The &quot;lesson&quot; column&mdash;it only gives a lesson number, not a file"},
                    {"zh": "速查表不含文件信息，得自己翻源码", "en": "The reference has no file info; you must dig through source yourself"},
                ],
                "answer": 0,
                "why": {
                    "zh": "速查表每行三列：一句话定义（是什么）、<strong>源码位置</strong>（去哪 grep，已核对行号）、所属课（看完整推演）。要「哪个文件第几行」，直接读源码位置列：记忆相关是 <span class=\"mono\">_sessions.py</span> 的 ContextProvider（:348）与 HistoryProvider（:410）。",
                    "en": "Each row has three columns: one-line definition (what), <strong>source location</strong> (where to grep, line numbers verified), and lesson (full walkthrough). For &quot;which file/line&quot;, read the source-location column: memory lives in <span class=\"mono\">_sessions.py</span> as ContextProvider (:348) and HistoryProvider (:410).",
                },
            },
            {
                "q": {
                    "zh": "本课说「所有东西最终化简为消息进、消息出」。这句话最直接支撑下面哪个判断？",
                    "en": "This lesson says &quot;everything reduces to messages in, messages out&quot;. Which claim does that most directly support?",
                },
                "opts": [
                    {
                        "zh": "正因为各层共享 <span class=\"mono\">Message</span> 这一统一数据契约，Agent、工作流、A2A 协议才能彼此拼接",
                        "en": "Because all layers share the single <span class=\"mono\">Message</span> data contract, Agents, workflows, and the A2A protocol can compose together",
                    },
                    {"zh": "每一层都得用各自不同的数据结构，互不兼容", "en": "Each layer must use its own incompatible data structure"},
                    {"zh": "消息只在第 4 课出现，后面就用不到了", "en": "Messages only appear in L4 and are unused afterward"},
                    {"zh": "工作流不传递消息，只传递函数指针", "en": "Workflows pass function pointers, not messages"},
                ],
                "answer": 0,
                "why": {
                    "zh": "统一的 Message 契约是「可组合性」的根源：上层只要遵守「收消息、发消息」，就能无缝接到下层。这也是为什么读懂第 4 课的 Message，后面所有课都更轻松——它是贯穿全栈的那条数据主线。",
                    "en": "The unified Message contract is the root of composability: as long as an upper layer honors &quot;take messages, emit messages&quot;, it plugs into the layer below. That's why getting L4's Message makes every later lesson easier&mdash;it's the data spine running through the whole stack.",
                },
            },
        ],
        "open": [
            {
                "zh": "合上这张速查表，凭记忆<strong>默写概念依赖图</strong>：从基石到运维，至少写出 6 层，每层放对应术语，并用箭头标出「谁建立在谁之上」。然后挑一层，说说如果抽掉它，上面哪些层会塌、为什么。",
                "en": "Close this reference and <strong>redraw the concept dependency map from memory</strong>: from bedrock to ops, write at least 6 layers, place the right terms in each, and use arrows to mark &quot;who stands on whom&quot;. Then pick one layer and explain which layers above would collapse if you removed it, and why.",
            },
        ],
    },
}


def render(fname, lang):
    """Return the self-test HTML block for ``fname`` in ``lang`` ('' if none)."""
    data = QUIZZES.get(fname)
    if not data or not (data.get("mcq") or data.get("open")):
        return ""
    out = ['<div class="selftest">', f'<h2>{_HEAD[lang]}</h2>']
    for i, item in enumerate(data.get("mcq", []), 1):
        shuffled, ans = _shuffle(item["opts"], item["answer"], f"{fname}:{i}")
        opts = "\n".join(f"    <li>{o[lang]}</li>" for o in shuffled)
        letter = chr(65 + ans)
        out.append(
            f'<div class="quiz">\n'
            f'  <div class="qn">{i}. {item["q"][lang]}</div>\n'
            f'  <ol class="opts">\n{opts}\n  </ol>\n'
            f'  <details class="accordion">\n'
            f'    <summary>{_SEE[lang]} <span class="hint">{_CLICK[lang]}</span></summary>\n'
            f'    <div class="acc-body"><div class="qa"><div class="a">'
            f'<strong>{_ANS[lang]}{letter}</strong>{_SEP[lang]}{item["why"][lang]}'
            f"</div></div></div>\n"
            f"  </details>\n"
            f"</div>"
        )
    opens = data.get("open", [])
    if opens:
        lis = "\n".join(f"    <li>{o[lang]}</li>" for o in opens)
        out.append(
            '<div class="card spark">\n'
            f'  <div class="tag">{_OPEN[lang]}</div>\n'
            f"  <ul>\n{lis}\n  </ul>\n"
            "</div>"
        )
    out.append("</div>")
    return "\n".join(out)


def _validate():
    """Fail fast on authoring mistakes in QUIZZES (clear message names the lesson)."""
    for fname, data in QUIZZES.items():
        for qi, item in enumerate(data.get("mcq", []), 1):
            opts = item["opts"]
            if not (0 <= item["answer"] < len(opts)):
                raise ValueError(
                    f"quizzes[{fname!r}] Q{qi}: answer {item['answer']} out of range 0..{len(opts) - 1}"
                )
            for o in opts:
                if not ({"zh", "en"} <= o.keys()):
                    raise ValueError(f"quizzes[{fname!r}] Q{qi}: an option is missing zh/en")
            if not ({"zh", "en"} <= item["q"].keys() and {"zh", "en"} <= item["why"].keys()):
                raise ValueError(f"quizzes[{fname!r}] Q{qi}: q/why missing zh/en")
        for oi, o in enumerate(data.get("open", []), 1):
            if not ({"zh", "en"} <= o.keys()):
                raise ValueError(f"quizzes[{fname!r}] open{oi}: missing zh/en")


_validate()
