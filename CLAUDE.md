# Course rules for coding agents

This repo is a hands-on GenAI course (see `PLAN.md`). The learner reads an HTML chapter and runs
short Python lesson scripts alongside it. **Concepts come first; tooling stays minimal; everything
runs on the learner's Mac.**

## Layout
```
.env / .env.example     the two API keys, at the repo root (git-ignored / committed)
pyproject.toml          ONE uv project for the whole course; `uv sync` once
documind/               THE app. One package that grows module by module
  settings.yaml         every knob; env vars DOCUMIND_<SECTION>__<KEY> override it
  prompts/*.md          prompt text, never inline in Python
tests/                  offline pytest tests (mock mode, no keys, no network)
data/                   made-up invoices + receipts; golden/ holds their correct answers
modules/
  NN-kebab-name/
    chapter.html        the chapter: concept, diagrams, ELI10, "At enterprise scale" boxes
    README.md           the run commands, in order, and which documind files this module added
    01_topic.py …       one lesson script per chapter section, run in order
    99_break_it.py      experiments that break things on purpose
```
- **Modules are separate for learning, linked through the app.** A lesson script in module N may
  import anything from `documind` that modules ≤ N added. Never import from a later module.
- Build **one module at a time**. Do not create later modules until the learner asks.

## Lesson scripts
- Run from the repo root: `uv run modules/NN-name/01_topic.py`.
- Each opens with a docstring: the concept, an "Explain like I'm 10" line where useful, what to
  run, and **what to look for** in the output.
- Short and linear, top to bottom: no functions unless they make the idea clearer. Comments
  explain *why*. Lesson scripts may `print`; they are the learner's view.
- Demo inputs (prompts, counts) are named constants at the top of the script.
- A step that fails on purpose catches the error and prints it, so the script finishes.
- No shared lesson helper module: plain `print`, plus `LLMReply.stats()` for the one-line call summary.
- Chapter sections and scripts match one-to-one; the chapter's "Now run" slip names the script.
- End each chapter with a checkpoint of about five questions in `<details>` blocks.
- **Verify before presenting:** run every lesson script for real, run `uv run pytest` and
  `uv run ruff check . && uv run ruff format --check .`.

## Everything local
- **No servers, no databases, no Docker, no Makefiles, no hosted services** other than the two
  model vendors. Tools: uv and git. Keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`.
- Optional local model: Ollama, only if the learner has it running. Lessons detect it and skip
  with a one-line hint when it is absent; nothing depends on it.
- **The AI gateway is LiteLLM used as a library** (`litellm.Router`) in `documind/llm.py`. The
  chapter explains the server form (shared proxy, virtual keys, budgets).
- Vector store: Chroma, embedded (a folder on disk). Semantic cache: built by hand on it.
  Tracing: a local JSONL trace log with a small local viewer. Chapters may *describe* hosted tools
  (Langfuse, LangSmith) in enterprise boxes, but code never needs them.
- Chapters are self-contained HTML files (styles inline; start from the previous chapter's
  `<style>` block) with no web fonts or CDN scripts, so they open offline or as a shared page.

## Keys and models
- Only LiteLLM reads the API keys, from the environment. `config.py` loads `.env` into the
  environment and never stores keys in settings. Feature code never names a key.
- `documind/` code always uses model **aliases** (`fast`, `smart`, …) from `settings.yaml`, never
  vendor model IDs; Module 2 explains them. Module 0 lesson scripts may call `litellm.completion`
  with one raw vendor model ID, to show the bare "before" picture.
- Practice mode: `DOCUMIND_GATEWAY__MOCK_RESPONSE="…"` makes every call return that text. For a
  smoke run of structured-output lessons, use a JSON mock that satisfies all their schemas.

## Code standards (production-ready, but simple)
The audience is a Director: code reads like a clear explanation of the concept and is still fit
to deploy.
- **Config, not hard-coding:** typed `pydantic-settings` loaded from `documind/settings.yaml`.
- **Typed:** type hints throughout. Data at boundaries (LLM output, files) is a Pydantic model.
- **Docs:** every `documind/` file opens with a docstring saying what it does, *which concept it
  teaches*, and which module added or extended it. Public functions get short docstrings.
- **Few, small files:** plain functions; no class hierarchies, no metaprogramming.
- **Logging, not print, in `documind/`:** configured once in `config.py`.
- **Errors:** fail fast with messages that say how to fix the problem.
- **Backwards compatible:** when a module extends a `documind` function, earlier modules' lesson
  scripts must keep working (add optional parameters; don't rename).
- **Quality gates:** `ruff` (lint + format) and offline `pytest` tests.
- **Runtime:** Python 3.12+ with uv. **Data:** only made-up or public sample data.
- **Versions:** check current library and model docs before pinning versions or model IDs.
