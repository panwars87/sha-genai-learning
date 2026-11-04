# GenAI Fundamentals: A Course You Build

**Product:** **DocuMind**, an app that processes invoices and receipts. You upload a PDF or a phone photo. An **agent** works out what it is, pulls out the fields, checks the maths and files it. Then you can **ask questions across all your documents**.

**Format (Udemy-style):** the course is split into modules, and each module has one **HTML chapter** (an artifact page to read) and one **code folder** (to follow along). Read the chapter, then open the module folder and run its lessons in order. Each module folder also holds a snapshot of the DocuMind app as it stands at the end of that module.

**Golden rule:** every model call goes through the **LiteLLM AI gateway**. Only the gateway holds the OpenAI and Anthropic keys. App code never sees them.

---

## 1. The finished product

```
React UI ─► Upload Agent (LangGraph) ──┐      ┌── Q&A over your documents (RAG, LangChain)
                                       ▼      ▼
                 ┌──────────── LiteLLM AI GATEWAY (holds the keys) ────────────┐
                 │  virtual keys · budgets · routing · fallbacks · semantic cache │
                 └─────────┬──────────────────┬───────────────────┬────────────┘
                     Anthropic (Claude)    OpenAI (GPT +      (later: local model)
                                           embeddings)
         Embeddings ─► pgvector            Postgres (extracted fields)
MCP server (upload / search / get_fields)  ·  Langfuse traces  ·  Evals on every change
```

### How keys flow (the AI gateway concept)

```
 .env (never committed)                        app code
 OPENAI_API_KEY ─┐                             base_url = http://localhost:4000
 ANTHROPIC_API_KEY┼─► LiteLLM proxy ◄───────── api_key  = sk-documind-virtual-key
 LITELLM_MASTER_KEY┘   (only place real keys live)   model = "fast" | "smart" | "embed"
```
- The app calls **model aliases** (`fast`, `smart`, `embed`), never vendor model names. Swapping a vendor is a one-line change in the gateway config.
- **Virtual keys** let the gateway set a budget per app or module and track spend for each.
- Anthropic has no embedding model, so the OpenAI key does real work here: OpenAI provides the embeddings and both vendors provide chat.

---

## 2. Repo layout

```
sha-genai-learning/
├── CLAUDE.md                     # course rules for any coding agent
├── PLAN.md                       # this file
├── .env.example                  # OPENAI_API_KEY, ANTHROPIC_API_KEY, LITELLM_MASTER_KEY
├── infra/
│   └── start_gateway.sh          # starts the LiteLLM proxy locally (no Docker)
├── data/
│   ├── invoices/   receipts/     # made-up invoices + public receipt datasets (SROIE / CORD)
│   └── golden/                   # hand-checked correct answers (JSON) for evals
└── modules/
    ├── 01-llm-basics-and-ai-gateway/
    │   ├── chapter.html          # the HTML chapter (also published as an artifact)
    │   ├── README.md             # goals · setup · how to run · checkpoint quiz
    │   ├── gateway/config.yaml   # LiteLLM config as of this module (shows how the gateway evolves)
    │   ├── lessons/              # L01_*.py, L02_*.py … one per chapter section, each runs on its own
    │   ├── experiments/          # "break it" scripts
    │   ├── app/                  # DocuMind as of the END of this module (full snapshot)
    │   ├── NOTES.md              # your findings
    │   └── colab.ipynb           # one-click launcher for Google Colab
    ├── 02-prompt-engineering-structured-output/
    └── …
```
- **The lesson numbers match the chapter sections**: chapter section 3 ↔ `lessons/L03_*.py`.
- **`app/` is cumulative**: module N starts as a copy of module N-1's `app/`. You can open any module and run DocuMind exactly as it was at that point, without depending on later code.
- **The gateway config is a snapshot per module**: compare `01/gateway/config.yaml` with `10/gateway/config.yaml` to see aliases grow into routing, fallbacks and caching.

---

### Two ways to run
**No Docker needed.** Everything is a pip package or a free hosted service, so it runs on a MacBook Air.

| | MacBook Air | Google Colab |
|---|---|---|
| Gateway | LiteLLM proxy as a local process (`make gateway`) | Same, started from a notebook cell |
| Keys | `.env`, read only by the gateway | Colab Secrets, passed only to the gateway |
| Postgres + pgvector (gateway keys and spend, vectors, extracted fields) | Hosted free Postgres (e.g. Neon), shared by both | same |
| Tracing | Langfuse Cloud (free tier) | same |
| Cache (Module 10) | Hosted Redis, or `brew install redis` | Hosted Redis |
| Learning vector DB | Chroma (embedded, no server) | same |
| Switch | `runtime: local` | `runtime: colab` |

The code is identical in both; only config changes. Enterprise notes (how this scales in a bank) live in each HTML chapter.

## 3. Modules

Each module covers the same four things: **Concept (ELI10)** → **Lessons** → **App increment** → **Break it** → **Checkpoint**.

### Module 00: Course setup
- **Chapter:** tools (Python + uv, Docker, Node for later), how the course works, a tour of the repo.
- **Lessons:** `L01_check_env.py` (checks Python, Docker and that `.env` exists), sample-data tour.
- **App:** none yet.

### Module 01: LLM basics + the AI gateway
- **ELI10:** an LLM is a super-autocomplete that reads tokens and guesses the next one, and it remembers nothing between calls. The gateway is a universal TV remote: one remote, every brand of TV, and only the remote knows the passwords.
- **Sections → lessons:**
  1. What an LLM call is (messages in, text out, statelessness) → `L01_first_call.py`
  2. Why a gateway: keys, vendor lock-in, spend control → *(chapter only)*
  3. Run the LiteLLM proxy with OpenAI + Anthropic keys → `gateway/config.yaml`, `L03_gateway_health.py`
  4. One client, two vendors: the same prompt to `claude-*` and `gpt-*` → `L04_same_prompt_two_vendors.py`
  5. Tokens, context window, temperature, cost → `L05_tokens_and_cost.py`
  6. Virtual keys + budgets → `L06_virtual_keys.py`
- **App:** `documind summarize <file>` via the gateway.
- **Break it:** use a revoked virtual key; go over the budget; run temperature 0 vs 1; overflow the context window.
- **Checkpoint:** why does a chat "remember"? Why must app code never hold vendor keys?

### Module 02: Prompt engineering + structured output
- **ELI10:** a prompt is instructions for a smart new intern. Clear instructions plus examples get good work. Asking for a form (JSON) instead of an essay gets work you can use.
- **Lessons:** system prompt & roles · few-shot examples · XML tags · JSON schema / structured outputs (Pydantic) · how hallucination happens.
- **App:** `documind extract <file>`, with two schemas:
  - **Invoice:** `{vendor, invoice_no, invoice_date, due_date, subtotal, tax, total, currency, line_items[]}`
  - **Receipt:** `{merchant, date, subtotal, tax, tip, total, payment_method, items[]}`
- **Break it:** remove the examples; feed a receipt to the invoice prompt; watch it invent fields.
- **Also:** create `data/golden/`: 10 documents with hand-checked correct answers.

### Module 03: Observability: logging, tracing, cost
- **ELI10:** a GoPro on every request, so you can replay what happened, how long it took and what it cost.
- **Lessons:** the difference between a log, a trace and a span · connecting the LiteLLM → Langfuse callback · per-request cost and latency · versioning prompts in Langfuse · OpenTelemetry basics.
- **App:** every call from now on is traced, tagged with module, feature and virtual key.
- **Break it:** find the slowest and most expensive call using only the dashboard.

### Module 04: Model routing + fallbacks
- **ELI10:** don't send a surgeon to put on a plaster. Easy jobs go to the cheap fast model, hard jobs to the smart one, and if one vendor is down, call the other.
- **Lessons:** the cost, quality and speed trade-off · routing by fixed rules · routing by a classifier · trying the cheap model first and stepping up to the smart one when unsure · LiteLLM router strategies · fallbacks across vendors (Anthropic ↔ OpenAI) · retries & rate limits.
- **App:** the `fast` model classifies the document and rates how hard it is. Clean single-page documents go to `fast`; multi-page invoices, blurry photos and handwriting go to `smart`. If the totals don't add up, the document moves up to `smart`.
- **Break it:** compare all-cheap vs all-smart vs routed (cost and accuracy table); kill one vendor's key and watch the fallback.

### Module 05: Embeddings
- **ELI10:** turn every sentence into a GPS coordinate in "meaning-land". Similar sentences live near each other.
- **Lessons:** what a vector is · cosine similarity · embeddings through the gateway (`embed` alias → OpenAI) · plotting them in 2D.
- **App:** embeds the text of extracted documents.
- **Break it:** keyword search vs embedding search, on synonyms ("amount due" ≈ "total") and on exact invoice numbers (embeddings lose on the numbers).

### Module 06: Vector database + chunking
- **ELI10:** a library shelved by *meaning* instead of alphabet, with a librarian who finds the nearest books instantly.
- **Lessons:** chunking (size, overlap, by section) · tagging chunks with metadata (vendor, date, doc_type) · how the database finds near matches fast (approximate nearest-neighbour, HNSW) · metadata filters · Chroma (to learn) → pgvector (for real use).
- **App:** an ingestion pipeline: read → split into chunks → embed → store.
- **Break it:** compare chunks of 100 vs 1,000 tokens and see how search quality changes.

### Module 07: RAG: chat with your documents
- **ELI10:** an open-book exam. The model finds the right pages first, answers *only* from them and shows which page it used.
```
Question ─► embed ─► vector DB (top-k) ─► rerank ─► prompt = question + chunks ─► LLM ─► answer + citations
```
- **Lessons:** retrieve → augment → generate · top-k · citations · hybrid search (keyword + vector) · reranking · answering "I don't know".
- **App:** `documind ask "How much did we spend at Acme in Q3?"`, answered with sources.
- **Break it:** ask about something that isn't in any document. Does it make an answer up?

### Module 08: Context engineering
- **ELI10:** the model's desk is small. Context engineering decides which papers go on it, in what order, and clears the junk off.
- **Lessons:** the token budget · ordering (models miss things buried in the middle of long prompts) · system text vs retrieved text vs chat history · summarising old history · prompt caching (using LiteLLM's cache-control support for Anthropic).
- **App:** a token budget manager for Q&A and chat history; caching for the fixed system prompt.
- **Break it:** stuff in 50 chunks vs 5 good ones and compare quality and cost.

### Module 09: Evals
- **ELI10:** a report card for your AI. Before you ship any change, it retakes the same test.
- **Lessons:** the golden dataset · exact-match vs fuzzy scoring · free objective checks (the totals must add up) · using an LLM as the judge · RAG metrics (sticks to the sources, answers the question, finds the right chunks) · regression runs.
- **App:** `make eval` scores field accuracy and how closely Q&A answers stick to the sources; results go to Langfuse.
- **Break it:** "improve" a prompt and watch the eval catch the regression.

### Module 10: Semantic cache
- **ELI10:** "What's Acme's total?" and "How much is the Acme bill?" are the same question, so reuse the answer instead of paying again.
- **Lessons:** exact cache vs semantic cache · the similarity threshold · how long answers stay cached (TTL) · clearing stale answers · LiteLLM + Redis semantic cache · the risk of wrong hits ("Acme Q3" ≈ "Acme Q4").
- **App:** a cache in front of Q&A, configured in the gateway, not in app code.
- **Break it:** compare a 0.80 threshold with 0.95 and find a pair of questions that wrongly hit.

### Module 11: Tool calling + MCP
- **ELI10:** the model can't *do* anything, but it can say "please run `search_docs('Acme')`". Your code runs it and hands back the result. MCP is the universal plug that lets any AI app use your tools.
```
User ─► LLM ─► "call search_docs(vendor='Acme')" ─► your code runs it ─► result ─► LLM ─► answer
```
- **Lessons:** tool schemas · the tool loop written by hand (through the gateway, on both vendors) · parallel tool calls · MCP server vs client · tools, resources and prompts · security: least privilege and **prompt injection hidden in a document**.
- **App:** a DocuMind MCP server (`upload_document`, `search_docs`, `get_fields`) that you can use from Claude Desktop or Claude Code.
- **Break it:** upload a receipt that contains "ignore previous instructions…".

### Module 12: LangChain
- **ELI10:** LEGO bricks for LLM apps: ready-made loaders, splitters, retrievers and prompts that snap together.
- **Lessons:** chat models (`ChatOpenAI` with `base_url` = the gateway) · prompt templates · retrievers · chaining steps together (LCEL) · output parsers · what the framework hides.
- **App:** the Module 07 Q&A rebuilt in LangChain. **The Module 09 evals must still pass.**
- **Checkpoint:** an honest comparison of LangChain vs plain SDK calls.

### Module 13: LangGraph: the Upload Agent
- **ELI10:** a flowchart the AI walks through. Each box does one job; arrows decide where to go next, including "try again" and "ask a human".
```
upload ─► classify ─► extract ─► validate ──ok──► store ─► index ─► done
                         ▲          │
                         └─retry────┤ (maths doesn't add up)
                                    └─low confidence─► human review ─► store
```
- **Lessons:** state · nodes and arrows · arrows that branch on a condition · loops and retries · saving progress so a run can resume (checkpointing) · pausing for a human · agent vs fixed workflow.
- **Checks (plain code, not the LLM):** line items add up to the subtotal; subtotal + tax (+ tip) = total; dates are valid; the same invoice number from the same vendor is flagged as a duplicate.
- **App:** the Upload Agent, using the MCP tools and fully traced.
- **Break it:** upload an unreadable scan and watch it retry, then hand off to a human.

### Module 14: Capstone: ship DocuMind
- React UI (upload, review fields, chat) · dashboard of cost, speed and eval scores · README with the architecture.
- **Final test:** explain the whole system on a whiteboard to your team in 10 minutes.

---

## 4. How each module runs

1. **Read** `chapter.html`: the concept, diagrams and ELI10. I publish it as an artifact and save the same file in the module folder.
2. **Code along**: run `lessons/L01…` in order; each prints what it is showing you.
3. **Break it**: run `experiments/` and write what you saw in `NOTES.md`.
4. **Checkpoint**: answer the quiz in the README. Move on only when you pass.

We build one module at a time, and Module N+1 is not built until you finish Module N.

Tool versions and APIs change fast. Model IDs are pinned in each module's `gateway/config.yaml` after checking the current docs at build time.
