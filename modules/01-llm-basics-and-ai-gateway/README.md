# Module 01: LLM basics + the AI gateway

1. Read the chapter: [online](https://claude.ai/artifact/AJzEw8t72U7eazv6X1Z4MY), or `chapter.html` in this folder.
2. Run the notebook `01-llm-basics-and-ai-gateway.ipynb` alongside it, section by section.

## Open the notebook
**Mac** (first run installs everything, about a minute):
```bash
cd modules/01-llm-basics-and-ai-gateway
uv run --project app jupyter lab
```
**Colab:** File → Open notebook → GitHub → this repo → `01-llm-basics-and-ai-gateway.ipynb`. Add `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` as Colab Secrets (the key icon).

Set `MOCK = True` in the first cell for free practice with canned replies.

## What you'll learn
| Section | Concept |
|---|---|
| 1 | What an LLM call is: messages in, text out |
| 2 | Why a gateway *(reading only)* |
| 3 | Aliases: the app asks for `fast`; the gateway picks the model |
| 4 | One client, two vendors |
| 5 | Tokens, cost, a monthly bill, randomness, the retired temperature knob |
| 6 | Spend caps (and how virtual keys do this in a company) |
| 7 | The model has no memory |
| 8 | DocuMind summarizes a document |
| Break it | Cut-off answer, unapproved model, switch vendor by config, wrong key |

## The app after this module
```bash
uv run --project app python -m documind summarize ../../data/invoices/INV-1001-acme-supplies.txt
```
```
app/config/settings.yaml   every setting: aliases, limits, spend cap (override with DOCUMIND_<SECTION>__<KEY>)
app/prompts/*.md           prompt text, kept out of code
app/src/documind/
  config.py      loads and validates settings; loads keys from .env for LiteLLM
  llm.py         the gateway: aliases → models, cost, spend cap, clear errors
  documents.py   checks a file before any money is spent
  summarize.py   the feature
  __main__.py    command line
app/tests/       offline tests (mock mode, no keys needed): uv run --project app pytest
```
Write what surprised you in `NOTES.md`.
