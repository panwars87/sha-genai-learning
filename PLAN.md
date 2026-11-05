# GenAI Fundamentals: A Course You Build

**Product:** **DocuMind**, an app that processes invoices and receipts. You upload a PDF or a phone photo. An **agent** works out what it is, pulls out the fields, checks the maths and files it. Then you can **ask questions across all your documents**.

**Principle: concepts first, tooling last.** Every module teaches one GenAI concept. The infrastructure stays as small as possible: two tools (uv, git), two API keys, and **no servers, no databases, no Docker**. Where a company would run a service (a gateway server, a vector database, a cache), the chapter explains it and the code uses a library or a local folder that shows the same idea.

**Format:** each module has an **HTML chapter** to read and a **notebook** to run alongside it, section for section. Every code cell has a note before it (*what this does*) and after it (*what you just saw*). The notebook runs the same on a Mac and in Google Colab. Each module also holds a snapshot of the DocuMind app as it stands at the end of that module.

---

## 1. The finished product

```
Upload Agent (LangGraph) ──┐      ┌── Q&A over your documents (RAG, LangChain)
                           ▼      ▼
        ┌──────────── AI GATEWAY: LiteLLM, used as a library ────────────┐
        │  aliases (fast/smart) · routing · fallbacks · cost · spend cap  │
        └────────┬───────────────────────┬───────────────────────────────┘
          Anthropic (Claude)        OpenAI (GPT + embeddings)
   Embeddings ─► Chroma (a local folder)      Semantic cache (built by hand on Chroma)
MCP server (upload / search / get_fields) · trace log (Langfuse Cloud optional) · evals
```

### How keys flow

```
 .env  (git-ignored)         ──►  LiteLLM, inside documind/llm.py  ──►  vendors
 ANTHROPIC_API_KEY, OPENAI_API_KEY      (the only code that uses them)
 feature code asks for:  "fast" | "smart" | "embed"   (aliases, never vendor model names)
```
In Colab, the two keys come from Colab Secrets instead of `.env`.

---

## 2. Repo layout

```
sha-genai-learning/
├── CLAUDE.md                      # course rules for any coding agent
├── PLAN.md                        # this file
├── .env.example                   # ANTHROPIC_API_KEY, OPENAI_API_KEY
├── data/
│   ├── invoices/   receipts/      # made-up documents (later: public receipt datasets)
│   └── golden/                    # hand-checked correct answers, for evals
└── modules/
    ├── 01-llm-basics-and-ai-gateway/
    │   ├── chapter.html           # the chapter (also published as an artifact)
    │   ├── 01-llm-basics-and-ai-gateway.ipynb   # run alongside the chapter, section for section
    │   ├── README.md              # how to open the notebook; what's in the app
    │   ├── NOTES.md               # your notes
    │   └── app/                   # DocuMind as of the END of this module (full snapshot)
    │       ├── config/settings.yaml   # every setting, including the gateway's alias table
    │       ├── prompts/*.md
    │       ├── src/documind/          # a handful of small, documented files
    │       └── tests/                 # offline tests (mock mode)
    └── …
```
- **Notebook sections match chapter sections**: chapter section 3 ↔ notebook section 3.
- **`app/` is cumulative**: module N starts as a copy of module N-1's `app/`, so any module runs on its own.
- **Practice mode**: `MOCK = True` in a notebook's first cell gives canned replies, free and instant.

---

## 3. Modules

Each module has the same parts: **Concept (ELI10)** → **Notebook sections** → **App increment** → **Break it** → **Checkpoint**.

| # | Concept | What DocuMind gains | Kept simple by |
|---|---|---|---|
| 00 | Course setup | Tools, keys, sample documents | Standard library only |
| 01 | LLM basics + AI gateway | Summarize a document through LiteLLM; cost per call; spend cap | LiteLLM as a library, not a server |
| 02 | Prompt engineering + structured output | Extract invoice and receipt fields as validated JSON | Pydantic schemas |
| 03 | Observability: logging, tracing, cost | Every step of a request logged and traced | Local trace log; Langfuse Cloud optional (two keys, no install) |
| 04 | Model routing + fallbacks | Cheap model for easy documents, smart for hard ones; vendor fallback | LiteLLM router settings |
| 05 | Embeddings | Search by meaning | Embeddings through the gateway (`embed` alias) |
| 06 | Vector DB + chunking | An ingestion pipeline: read → chunk → embed → store | Chroma, a folder on disk |
| 07 | RAG | Ask questions across all documents, with sources | Same Chroma store |
| 08 | Context engineering | Token budgets, ordering, prompt caching | Plain Python |
| 09 | Evals | A report card that scores every change | Golden set in `data/golden/` |
| 10 | Semantic cache | Reuse answers to questions that mean the same thing | Built by hand on Chroma (~30 lines) so you see how it works |
| 11 | Tool calling + MCP | The tool loop by hand, then a DocuMind MCP server | MCP Python SDK, runs locally |
| 12 | LangChain | Q&A rebuilt with LangChain; evals must still pass | |
| 13 | LangGraph | The upload agent: classify → extract → check → retry or ask a human | |
| 14 | Capstone | A simple UI and a cost/quality dashboard | |

### Module details

**00 · Course setup:** how the course works; install uv and git; create `.env`; tour the sample documents.

**01 · LLM basics + AI gateway**
- Notebook sections:
  1. a raw LLM call
  2. why a gateway (reading only)
  3. aliases
  4. one client, two vendors
  5. tokens, cost and the retired temperature knob
  6. spend caps (virtual keys explained)
  7. statelessness
  8. the summarize feature
- Break it: a cut-off answer, an unapproved model, switching vendor by config only, a wrong key.

**02 · Prompt engineering + structured output**
- Concepts: system prompts, few-shot examples, XML tags, JSON schemas with Pydantic, how hallucination happens.
- App: two extraction formats:
  - Invoice: `{vendor, invoice_no, invoice_date, due_date, subtotal, tax, total, currency, line_items[]}`
  - Receipt: `{merchant, date, subtotal, tax, tip, total, payment_method, items[]}`
- PDFs and photos arrive here.
- Start `data/golden/`.

**03 · Observability:** logs vs traces vs spans; latency and cost per step; prompt versions. Break it: find the slowest, most expensive step from the trace alone.

**04 · Model routing + fallbacks**
- Rule-based routing, classifier routing, and trying the cheap model first, then moving up to the smart one when unsure.
- Fallback across vendors, and the cost/quality/speed trade-off.
- App: easy documents go to `fast`; multi-page invoices, blurry photos and handwriting go to `smart`. If the totals don't add up, the document is sent to `smart`.

**05 · Embeddings:** vectors, cosine similarity, a 2D plot. Break it: synonyms ("amount due" ≈ "total"), where embeddings win, vs exact invoice numbers, where they lose.

**06 · Vector DB + chunking:** chunk size and overlap, metadata filters, how nearest-neighbour search works. Break it: 100-token vs 1,000-token chunks.

**07 · RAG:** retrieve → augment → generate; top-k; citations; hybrid search; reranking; "I don't know". Break it: ask about something that isn't in any document.

**08 · Context engineering:** the context budget; models missing things buried in the middle of long prompts; summarising history; prompt caching. Break it: 50 chunks vs 5 good ones.

**09 · Evals:** golden datasets; exact vs fuzzy scoring; free checks (the totals add up); an LLM as the judge; RAG metrics (sticks to the sources, finds the right chunks); regression runs.

**10 · Semantic cache:** exact vs semantic caching; the similarity threshold; how long answers stay cached (TTL); wrong hits ("Acme Q3" ≈ "Acme Q4").

**11 · Tool calling + MCP**
- Tool schemas and the tool loop.
- MCP: server vs client; tools, resources and prompts.
- App: a DocuMind MCP server (`upload_document`, `search_docs`, `get_fields`), used from Claude Desktop or Claude Code.
- Break it: a document hiding instructions for the model (prompt injection).

**12 · LangChain:** chat models, prompt templates, retrievers, chaining steps together (LCEL), output parsers; what the framework hides. The Module 09 evals must still pass.

**13 · LangGraph**
- State, nodes and edges; branching on a condition; retries; saving progress (checkpointing); pausing for a human.
- Plain-code checks:
  - line items add up to the subtotal
  - subtotal + tax (+ tip) = total
  - dates are valid
  - the same invoice number from the same vendor is flagged as a duplicate

**14 · Capstone:** a UI for upload, review and chat; a dashboard of cost, speed and eval scores; explain the whole system on a whiteboard in 10 minutes.

---

## 4. How each module runs

1. **Read** a section of `chapter.html`: the concept, diagrams and ELI10, plus an "at enterprise scale" box where it matters.
2. **Run** the same section of the notebook. Run it top to bottom; each section builds on the last.
3. **Break it**: the experiments at the end of the notebook. Write what you saw in `NOTES.md`.
4. **Checkpoint**: five questions at the end of the notebook and chapter.

We build one module at a time; Module N+1 is not built until you finish Module N. Model IDs and prices are checked against current docs when each module is built.
