# Course rules for coding agents

This repo is a hands-on GenAI course (see `PLAN.md`). The learner reads an HTML chapter and then follows the code. Build exactly in that shape.

## Structure
- One folder per module: `modules/NN-kebab-name/`, with:
  - `chapter.html`: the chapter for this module (the same content is published as an artifact)
  - `README.md`: goals, setup, how to run, checkpoint quiz
  - `gateway/config.yaml`: LiteLLM config **as of this module**
  - `lessons/LNN_snake_name.py`: one per chapter section, numbered to match it, runs on its own, prints what it demonstrates
  - `experiments/`: "break it" scripts
  - `app/`: a **full snapshot** of DocuMind at the end of this module (start by copying the previous module's `app/`)
  - `NOTES.md`: left empty for the learner
- Shared items live only in `infra/` (docker-compose) and `data/` (sample documents + `golden/`).
- Build **one module at a time**. Do not create later modules until the learner asks.

## Keys and models: the AI gateway rule
- Every LLM and embedding call goes through the **LiteLLM proxy** (`http://localhost:4000`), using an OpenAI-compatible client and a **virtual key**.
- `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` are read **only** by the LiteLLM container. App and lesson code must never read them or import vendor SDKs to call models directly. (Module 01 L01 may show a direct call once, for contrast.)
- App code uses model **aliases** (`fast`, `smart`, `embed`, …) that are defined in the gateway config, never vendor model IDs.
- `.env` is git-ignored; keep `.env.example` up to date.

## Code style
- Simple, readable, heavily commented for learning. Concepts matter more than abstractions.
- Python + uv; FastAPI and React only where the plan calls for them.
- Use only made-up or public sample data. Never real financial or personal documents.
- Check current library and model docs before pinning versions or model IDs.
