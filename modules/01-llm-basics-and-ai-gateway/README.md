# Module 01: LLM basics + the AI gateway

Read the chapter first: [online](https://claude.ai/artifact/AJzEw8t72U7eazv6X1Z4MY) or `chapter.html` in this folder. Then follow along here.

## Goals
By the end you can explain, and show in code:
1. What an LLM call is: messages in, text out, no memory.
2. Why every call should go through an **AI gateway** (LiteLLM), and what the gateway does: hides vendor keys, maps aliases to models, enforces budgets, records cost.
3. How a **virtual key** gives one app limited, revocable, budgeted access.
4. How tokens drive cost, and why the same prompt can give different answers.

## Before you start
- Module 00 is done: tools installed, `.env` created, Postgres URL ready.
- `.env` has `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `LITELLM_MASTER_KEY`, `DATABASE_URL`.

## Steps

```bash
# from the repo root
make setup MODULE=01          # install the app + lesson dependencies
make gateway MODULE=01        # terminal 1: start the AI gateway (leave it running)
#   or: make gateway-mock MODULE=01   free canned replies, no vendor calls

# terminal 2: from this module folder
cd modules/01-llm-basics-and-ai-gateway
uv run --project app python lessons/L03_gateway_health.py
```

Run the lessons in order. Each one prints what it is showing you.

| Chapter section | File | What you'll see |
|---|---|---|
| 1. What an LLM call is | `lessons/L01_direct_call_the_old_way.py` | A direct vendor call, "the old way", for contrast |
| 2. Why a gateway | *(chapter only)* | |
| 3. Meet the gateway | `lessons/L03_gateway_health.py` | Health, key database, alias → vendor model table |
| 4. Virtual keys | `lessons/L04_create_virtual_key.py` | Issue DocuMind's key with a $2 / 30-day budget. **Copy it into `.env` as `DOCUMIND_API_KEY`.** |
| 5. One client, two vendors | `lessons/L05_one_client_two_vendors.py` | Same code, Anthropic vs OpenAI, side by side |
| 6. Tokens, cost, knobs | `lessons/L06_tokens_cost_and_knobs.py` | Token counts and cost; varying answers; temperature rejected |
| 7. No memory | `lessons/L07_statelessness_and_memory.py` | The model forgets; "memory" = resending history |

Running a lesson: `uv run --project app python lessons/<file>`

### Break it
| File | What breaks |
|---|---|
| `experiments/E01_revoked_key.py` | Revoke a key, and the app loses access instantly |
| `experiments/E02_budget_exceeded.py` | $0 budget, so the gateway refuses before calling the vendor |
| `experiments/E03_answer_cut_off.py` | Too few output tokens, so the answer is cut off (needs real models) |
| `experiments/E04_model_not_allowed.py` | A key limited to `fast` is refused `smart` |

Write what you saw in `NOTES.md`.

### The app at the end of this module
```bash
uv run --project app documind summarize ../../data/invoices/INV-1001-acme-supplies.txt
uv run --project app documind summarize ../../data/receipts/RCPT-3001-bean-there-cafe.txt
```
Every run prints the answer plus `alias → model | tokens | cost | latency`.

Quality gates (from the repo root): `make test MODULE=01` and `make lint MODULE=01`.

## Where things live
```
gateway/config.yaml        alias → vendor model, retries, master key, key database
gateway/config.mock.yaml   same aliases, canned replies (free practice)
lessons/lessons.yaml       prompts and limits used by the lessons
app/config/settings.yaml   every app setting (override with DOCUMIND_<SECTION>__<KEY>)
app/prompts/*.md           prompt templates, kept out of code
app/src/documind/
  config.py      typed settings: YAML → .env → environment
  gateway.py     the ONLY code that talks to the gateway; returns answer + metrics
  documents.py   guardrails: file type, size, empty
  prompts.py     loads and fills prompt templates
  summarize.py   the feature: build messages → call → result
  cli.py         thin command-line shell
app/tests/       offline tests (fake gateway)
```

## Checkpoint
Answer these without looking. Then open each one to check.

<details><summary>1. A chat app "remembers" what you said earlier. How, if the model is stateless?</summary>
The app resends the whole conversation with every request. Memory costs input tokens on every turn (L07).
</details>

<details><summary>2. Name three things the gateway gives you that a direct vendor call does not.</summary>
Vendor keys stay out of apps; aliases mean you can switch vendor without code changes; budgets and per-key spend; instant revocation; per-call cost and latency; central retries. Any three.
</details>

<details><summary>3. What is the difference between the master key and a virtual key?</summary>
The master key is the admin's root key: it issues and revokes keys. A virtual key is what one app uses: scoped to certain aliases, with a budget, and revocable without touching anything else.
</details>

<details><summary>4. Your summary looks complete but finish_reason is "length". What happened, and what do you do?</summary>
The model hit max_output_tokens and was cut off (thinking tokens count too). Raise the limit or ask for a shorter answer. Always check finish_reason (E03).
</details>

<details><summary>5. Why can't you rely on temperature=0 for repeatable answers on current Claude models?</summary>
They no longer accept temperature (L06). Repeatability comes from clear prompts, structured output (Module 02) and evals (Module 09), not a knob.
</details>
