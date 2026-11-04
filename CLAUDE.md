# Course rules for coding agents

This repo is a hands-on GenAI course (see `PLAN.md`). The learner reads an HTML chapter and then follows the code. Build exactly in that shape.

## Structure
- One folder per module: `modules/NN-kebab-name/`, with:
  - `chapter.html`: the chapter for this module (the same content is published as an artifact)
  - `README.md`: goals, setup, how to run, checkpoint quiz
  - `gateway/config.yaml`: LiteLLM config **as of this module**, plus `gateway/config.mock.yaml` (same aliases, `mock_response` replies) for free practice
  - `lessons/LNN_snake_name.py`: one per chapter section, numbered to match it, runs on its own, prints what it demonstrates. Lesson settings (prompts, limits) live in `lessons/lessons.yaml`; a chapter-only section has no lesson file
  - Run lessons from the module folder: `uv run --project app python lessons/LNN_*.py`
  - `experiments/`: "break it" scripts
  - `app/`: a **full snapshot** of DocuMind at the end of this module (start by copying the previous module's `app/`)
  - `NOTES.md`: left empty for the learner
  - `colab.ipynb`: Colab launcher (see "Two ways to run")
- Enterprise/production-at-scale notes (SSO, secrets managers, compliance, rate limits) go **in `chapter.html` only**, not in READMEs.
- Shared items live only in `infra/` (gateway start script, setup helpers) and `data/` (sample documents + `golden/`).
- Build **one module at a time**. Do not create later modules until the learner asks.

## Two ways to run, no Docker required (every module supports both)
The learner uses a MacBook Air, so the setup must stay light. **Docker is not required anywhere.**
- **Gateway:** the LiteLLM proxy is installed with uv (`litellm[proxy]`) and runs as a local background process on `localhost:4000`. On Mac it starts with `make gateway`; in Colab, with a notebook cell.
- **Postgres:** one free hosted Postgres (e.g. Neon) with pgvector. It holds LiteLLM's virtual keys and spend (LiteLLM needs Postgres for virtual keys), and later the vectors and extracted fields. Mac and Colab share the same database.
- **Tracing:** Langfuse Cloud (free tier).
- **Cache (Module 10):** hosted Redis free tier, or `brew install redis` on Mac.
- **Learning-stage vector DB:** Chroma, embedded (a pip package; no server).
- **Google Colab:** each module ships `colab.ipynb`, a thin launcher. It clones the repo, installs `app/`, starts the gateway, then runs each lesson in its own cell.
- The run mode is one config value (`runtime: local | colab`). It changes only where keys and paths come from; code paths are identical.
- Before relying on a hosted free tier, confirm it is still offered; free tiers change.
- In Colab, keys come from **Colab Secrets** and are passed **only** into the LiteLLM subprocess environment, never into notebook variables the app reads.
- The `.py` lessons are the source of truth; the notebook only calls them.

## Keys and models: the AI gateway rule
- Every LLM and embedding call goes through the **LiteLLM proxy** (`http://localhost:4000`), using an OpenAI-compatible client and a **virtual key**.
- `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` are read **only** by the LiteLLM gateway (a local background process, on Mac and in Colab). App and lesson code must never read them or import vendor SDKs to call models directly. (Module 01 L01 may show a direct call once, for contrast.)
- App code uses model **aliases** (`fast`, `smart`, `embed`, …) that are defined in the gateway config, never vendor model IDs.
- `.env` is git-ignored; keep `.env.example` up to date.

## Code standards (production-ready, but simple)
The audience is a Director: code should read like a clear explanation of the concept and still be fit to deploy.

- **Everything comes from config; nothing is hard-coded.**
  - Settings that can change (model aliases, temperatures, token limits, URLs, paths, thresholds) live in the module's `app/config/settings.yaml`, loaded through a typed `pydantic-settings` class.
  - Environment variables override YAML. Secrets come **only** from the environment.
  - No magic numbers or strings in code.
  - Prompts live in `app/prompts/*.md` (or `.yaml`), never as inline strings.
- **Typed:** type hints everywhere. Data in and out of every boundary (LLM output, API, DB) is a Pydantic model.
- **Docs:**
  - Every file starts with a module docstring: what it does, and *which concept it teaches*.
  - Every public function has a short Google-style docstring.
  - Comments explain *why*, not *what*.
- **Simple:** small functions; plain modules over class hierarchies; no metaprogramming, no clever tricks. If it needs a diagram to follow, simplify it.
- **Logging, not print, in `app/`:** use the standard `logging` module, configured in one place. Lessons may `print` (they are demos).
- **Errors:** fail fast with clear messages (e.g. "gateway unreachable at X: is docker compose up?"). Retries and fallbacks belong in the gateway, not the app.
- **Quality gates:** `ruff` (lint + format) and `pytest`. Every `app/` snapshot ships a few focused tests that run without network access (mock the gateway).
- **Runtime:** Python 3.12 + uv (`pyproject.toml` per module `app/`); FastAPI and React only where the plan calls for them.
- **Data:** only made-up or public sample data. Never real financial or personal documents.
- **Versions:** check current library and model docs before pinning versions or model IDs.
