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
