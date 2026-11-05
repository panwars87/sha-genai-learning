# Module 2 · The LiteLLM gateway

Read [`chapter.html`](chapter.html) in your browser, section by section. After each section, run
its script from the **repo root**:

| Section | Run | Concept |
|---|---|---|
| 1 | `uv run modules/02-litellm-gateway/01_why_a_gateway.py` | Where model names live (one place) |
| 2 | `uv run modules/02-litellm-gateway/02_aliases.py` | Aliases, shortcuts, fallbacks, prices |
| 3 | `uv run modules/02-litellm-gateway/03_three_vendors.py` | Same extraction on Claude, GPT, local |
| 4 | `uv run modules/02-litellm-gateway/04_fallbacks.py` | A vendor fails; the gateway tries another |
| 5 | `uv run modules/02-litellm-gateway/05_spend_cap_and_approved_models.py` | Budgets and approved models |
| 6 | `uv run modules/02-litellm-gateway/06_switch_vendor_by_config.py` | Switch vendor with one env var |
| Break it | `uv run modules/02-litellm-gateway/99_break_it.py` | Budget mid-batch, all vendors down, Ollama off |

The local model is optional: `brew install ollama && ollama serve`, then `ollama pull llama3.2`.
Without it, Section 3 skips that column.

## What this module added to DocuMind
```
documind/llm.py         Router with aliases + shortcuts + fallbacks; SpendTracker; approved-model check
documind/settings.yaml  gateway: aliases, shortcuts, fallbacks, retries, spend cap
documind/__main__.py    --alias, e.g.  uv run python -m documind extract <file> --alias fast-openai
```
