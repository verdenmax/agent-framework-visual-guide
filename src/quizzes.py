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
