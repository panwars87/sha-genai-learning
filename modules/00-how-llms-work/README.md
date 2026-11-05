# Module 0 · How LLMs work

Read [`chapter.html`](chapter.html) in your browser, section by section. After each section, run
its script from the **repo root**:

| Section | Run | Concept |
|---|---|---|
| 0 | `uv run modules/00-how-llms-work/00_check_setup.py` | Tools, keys, sample documents |
| 1 | `uv run modules/00-how-llms-work/01_first_call.py` | Messages in, one message out |
| 2 | `uv run modules/00-how-llms-work/02_tokens_and_cost.py` | Tokens are the unit of cost |
| 3 | `uv run modules/00-how-llms-work/03_context_window.py` | Context window; a cut-off answer |
| 4 | `uv run modules/00-how-llms-work/04_no_memory.py` | The model is stateless |
| 5 | `uv run modules/00-how-llms-work/05_same_question_twice.py` | Randomness; the retired temperature knob |
| 6 | `uv run modules/00-how-llms-work/06_summarize.py` | DocuMind's first feature |
| Break it | `uv run modules/00-how-llms-work/99_break_it.py` | PDF, huge file, wrong key, unknown facts |

First time: `cp .env.example .env`, add your keys, then `uv sync`.
Free practice: put `DOCUMIND_GATEWAY__MOCK_RESPONSE="hello"` in front of any command.

## What this module added to DocuMind
```
documind/config.py      settings from settings.yaml (+ env overrides); loads .env for LiteLLM
documind/documents.py   cheap checks before any model call
documind/prompting.py   loads prompts/*.md
documind/summarize.py   the summarize feature
documind/llm.py         chat(): one call, with tokens, cost and time
documind/__main__.py    uv run python -m documind summarize <file>
```
