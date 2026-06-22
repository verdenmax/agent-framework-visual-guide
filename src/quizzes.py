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
        ],
        "open": [
            {
                "zh": "假设你已经用某厂商 SDK 直接写了一个聊天脚本。请列出迁移到 Agent Framework 后，你认为最先会“消失”的三段样板代码，并说明各自由框架的哪个概念接管（ChatClient / Message / @tool / Workflow 任选）。",
                "en": "Suppose you already wrote a chat script directly against a vendor SDK. List the three pieces of boilerplate you expect to 'disappear' first after moving to Agent Framework, and say which framework concept (ChatClient / Message / @tool / Workflow) takes over each.",
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
