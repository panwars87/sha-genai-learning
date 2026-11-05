# DocuMind: a GenAI course you build

A hands-on course in GenAI fundamentals that puts concepts first. Module by module you build
**DocuMind**, an app that reads invoices and receipts, extracts their fields, and answers
questions across them. Along the way: LiteLLM, prompt engineering, structured output,
observability, model routing, embeddings, vector databases, RAG, context engineering, evals,
semantic caching, tool calling and MCP, LangChain and LangGraph.

Each module is a folder with an HTML **chapter** to read and a few short **Python scripts** to run
alongside it, one per section. Everything runs on your Mac: two tools (uv, git), two API keys,
no servers, no databases, no Docker.

## Start
```bash
brew install uv
cp .env.example .env        # paste in ANTHROPIC_API_KEY and OPENAI_API_KEY
uv sync                     # once
uv run modules/00-how-llms-work/00_check_setup.py
```
Then open `modules/00-how-llms-work/chapter.html` in your browser and follow along.

| Module | Concept | Folder |
|---|---|---|
| 0 | How LLMs work: tokens, context window, statelessness | [00-how-llms-work](modules/00-how-llms-work/) |
| 1 | Prompt engineering + structured output | [01-prompts-and-structured-output](modules/01-prompts-and-structured-output/) |
| 2 | The LiteLLM gateway: aliases, three vendors, fallbacks, spend cap | [02-litellm-gateway](modules/02-litellm-gateway/) |
| 3–14 | Observability → … → LangGraph agent → capstone | built one at a time; see [PLAN.md](PLAN.md) |

```
documind/      the app: one package that grows each module (each file says which module added it)
modules/       chapters + lesson scripts
data/          10 made-up documents and their correct answers (data/golden/)
tests/         offline tests:  uv run pytest
```

- Free practice with no API calls: put `DOCUMIND_GATEWAY__MOCK_RESPONSE="hello"` before any command.
- Plan and module list: [PLAN.md](PLAN.md) · How modules are built: [CLAUDE.md](CLAUDE.md)
