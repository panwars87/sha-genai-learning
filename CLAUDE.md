# Course rules for coding agents

This repo is a hands-on GenAI course (see `PLAN.md`). The learner reads an HTML chapter and runs a notebook alongside it. **Concepts come first; keep tooling and infrastructure to a minimum.**

## Structure
- One folder per module: `modules/NN-kebab-name/`, with:
  - `chapter.html`: the chapter (the same content is published as an artifact). Enterprise and production-at-scale notes (SSO, secrets managers, compliance, gateway servers, virtual keys) go here, in an "At enterprise scale" box.
  - `NN-kebab-name.ipynb`: **the** learner-facing code. Its sections match the chapter's sections one-to-one and run top to bottom.
  - `README.md`: how to open the notebook (Mac and Colab), a section table, and the app's file map.
  - `NOTES.md`: left empty for the learner.
  - `app/`: a **full snapshot** of DocuMind at the end of this module (start by copying the previous module's `app/`).
- Shared items live only in `data/` (sample documents + `golden/`).
- Build **one module at a time**. Do not create later modules until the learner asks.

## Notebook rules
- Open with a section table. A Setup cell handles Colab (clone, `pip install -e ./app`, keys from Colab Secrets) and Mac (nothing to install; keys from `.env`). It also offers `MOCK = True`.
- Every code cell has a markdown cell before it (**What this cell does**) and after it (**What you just saw**). Each section opens with the concept, plus an ELI10 line where useful.
- Cells are short and sequential. A cell that fails on purpose catches the error and prints it, so the whole notebook runs top to bottom.
- Demo inputs (prompts, counts) sit in clearly named variables at the top of the cell. App behaviour comes from `settings.yaml`.
- End with "Break it" experiments, then a checkpoint of about five questions in `<details>` blocks.
- Commit notebooks with outputs cleared.
- **Verify before presenting:** execute the whole notebook headlessly in mock mode (`DOCUMIND_GATEWAY__MOCK_RESPONSE=...`, `nbclient`) and confirm every cell runs.

## No infrastructure
- **No servers, no databases, no Docker, no Makefiles.** Two tools (uv, git) and two API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`).
- **The AI gateway is LiteLLM used as a library** (`litellm.Router`) inside `documind/llm.py`, configured from `settings.yaml`. Explain the server form (shared proxy, virtual keys, budgets) in the chapter.
- Vector store: Chroma, embedded (a folder on disk). Semantic cache: built by hand on it. Tracing: a local trace log; Langfuse Cloud optional.
- Before relying on any hosted free tier, confirm it is still offered.

## Keys and models
- Only LiteLLM reads `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`, from the environment. `config.py` loads `.env` into the environment and never stores keys in settings. Feature code never names a key.
- Feature code uses model **aliases** (`fast`, `smart`, `embed`, …) defined in `settings.yaml`, never vendor model IDs. (Module 01 Section 1 shows one raw vendor call, for contrast.)
- `.env` is git-ignored; keep `.env.example` up to date.

## Code standards (production-ready, but simple)
The audience is a Director: code should read like a clear explanation of the concept and still be fit to deploy.
- **Config, not hard-coding:** everything that can change lives in `app/config/settings.yaml`, loaded through a typed `pydantic-settings` class. Environment variables (`DOCUMIND_<SECTION>__<KEY>`) override it. Prompts live in `app/prompts/*.md`.
- **Typed:** type hints throughout. Data at boundaries (LLM output, files, APIs) is a Pydantic model.
- **Docs:** every file opens with a docstring saying what it does and *which concept it teaches*. Public functions get short Google-style docstrings. Comments explain *why*.
- **Few, small files:** plain functions and modules; no class hierarchies, no metaprogramming. Add a file only when a module's concept needs one.
- **Logging, not print, in `app/`:** configured once in `config.py`. Notebooks may print.
- **Errors:** fail fast with messages that say how to fix the problem. Retries and fallbacks belong in the gateway settings.
- **Quality gates:** `ruff` (lint + format) and a few `pytest` tests per `app/` snapshot that run offline (mock mode).
- **Runtime:** Python 3.12+ with uv; one `pyproject.toml` per module `app/`, including Jupyter for Mac.
- **Data:** only made-up or public sample data.
- **Versions:** check current library and model docs before pinning versions or model IDs.
