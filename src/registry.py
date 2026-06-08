"""Single source of truth: ordered map of output filename -> {zh, en} lesson HTML.

Both the site build (build.py) and the print/PDF build (build_print.py) import
this so the lesson set stays in sync with shell.PAGES.
"""
import part1
import part2
import part3
import part4
import part5
import part6

# filename -> {"zh": html, "en": html}; order matches shell.PAGES.
CONTENT = {
    "01-what-is-agent-framework.html": {"zh": part1.L01_ZH, "en": part1.L01_EN},
    "02-monorepo.html": {"zh": part1.L02_ZH, "en": part1.L02_EN},
    "03-lifecycle.html": {"zh": part1.L03_ZH, "en": part1.L03_EN},
    "04-messages.html": {"zh": part2.L04_ZH, "en": part2.L04_EN},
    "05-chat-models.html": {"zh": part2.L05_ZH, "en": part2.L05_EN},
    "06-tools.html": {"zh": part2.L06_ZH, "en": part2.L06_EN},
    "07-sessions-memory.html": {"zh": part2.L07_ZH, "en": part2.L07_EN},
    "08-agent-internals.html": {"zh": part3.L08_ZH, "en": part3.L08_EN},
    "09-chatclient-internals.html": {"zh": part3.L09_ZH, "en": part3.L09_EN},
    "10-tool-internals.html": {"zh": part3.L10_ZH, "en": part3.L10_EN},
    "11-middleware.html": {"zh": part3.L11_ZH, "en": part3.L11_EN},
    "12-workflows.html": {"zh": part3.L12_ZH, "en": part3.L12_EN},
    "13-orchestration.html": {"zh": part3.L13_ZH, "en": part3.L13_EN},
    "14-streaming-observability.html": {"zh": part3.L14_ZH, "en": part3.L14_EN},
    "15-contributing.html": {"zh": part4.L15_ZH, "en": part4.L15_EN},
    "16-providers.html": {"zh": part5.L16_ZH, "en": part5.L16_EN},
    "17-declarative.html": {"zh": part5.L17_ZH, "en": part5.L17_EN},
    "18-custom-middleware.html": {"zh": part5.L18_ZH, "en": part5.L18_EN},
    "19-durability-hitl.html": {"zh": part5.L19_ZH, "en": part5.L19_EN},
    "20-capstone.html": {"zh": part5.L20_ZH, "en": part5.L20_EN},
    "21-vs-others.html": {"zh": part6.L21_ZH, "en": part6.L21_EN},
    "22-stack-map.html": {"zh": part6.L22_ZH, "en": part6.L22_EN},
}
