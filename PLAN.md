# GenAI Fundamentals: A Course You Build

**Product:** **DocuMind**, an intelligent document processing (IDP) app for invoices and receipts.
You drop in a document. An **agent** works out what it is, pulls out the fields, checks the maths
and files it. Then you can **ask questions across all your documents**, with sources.

**Principle: concepts first, tooling last.** Every module teaches one GenAI concept and adds one
piece to DocuMind. Everything runs on your Mac: two tools (uv, git), two API keys, and **no
servers, no databases, no Docker, no hosted services** beyond the model vendors. Where a company
would run a service (a gateway server, a vector database, a tracing platform), the chapter explains
it and the code uses a library or a local folder that shows the same idea.

**Format:** each module is a folder with an **HTML chapter** to read and a few **short Python
scripts** to run alongside it, one per section. Each script opens with a docstring explaining the
concept and what to look for. The scripts use the shared `documind/` app, so the dots connect.

---

## 1. The finished product

```
Upload agent (LangGraph) ──┐      ┌── Q&A over your documents (RAG)
classify → extract → check │      │   "How much did we pay Acme in Q3?" + sources
                           ▼      ▼
        ┌──────────── AI GATEWAY: LiteLLM, used as a library ─────────────┐
        │  aliases (fast/smart/local) · routing · fallbacks · cost · cap  │
        └────────┬────────────────────────┬───────────────────┬───────────┘
          Anthropic (Claude)      OpenAI (GPT + embeddings)   Ollama (optional, local)
 Embeddings ─► Chroma (a local folder) · semantic cache (hand-built on Chroma)
 MCP server (upload / search / get_fields) · local trace log + viewer · evals
```

### How keys flow
```
 .env (repo root, git-ignored) ──► LiteLLM, inside documind/llm.py ──► vendors
 ANTHROPIC_API_KEY, OPENAI_API_KEY     (the only code that uses them)
```

---

## 2. Repo layout

```
sha-genai-learning/
├── .env.example  pyproject.toml  CLAUDE.md  PLAN.md
├── documind/                 the app; one package that grows each module
│   ├── settings.yaml         every setting
│   ├── prompts/*.md          prompt text
│   └── *.py                  a few small files; each says which module added it
├── tests/                    offline tests (mock mode)
├── data/  invoices/ receipts/ golden/
└── modules/
    └── NN-name/  chapter.html  README.md  01_*.py … 99_break_it.py
```
Run everything from the repo root: `uv run modules/00-how-llms-work/01_first_call.py`.

---

## 3. Modules

| # | Concept | What gets built | Kept local by |
|---|---|---|---|
| 0 | How LLMs work: tokens, context window, statelessness | CLI that summarizes a document | One model, called through LiteLLM |
| 1 | Prompt engineering + structured output | Invoice/receipt fields as validated JSON; 10 documents with known correct answers | Pydantic schemas |
| 2 | LiteLLM gateway | Same extraction on Claude, GPT and (optionally) a local model; aliases, fallbacks, spend cap | LiteLLM as a library, not a server |
| 3 | Observability: logging, tracing, cost | Every step traced, so everything after this is visible | Local JSONL trace log + a small HTML viewer (Langfuse explained, not required) |
| 4 | Model routing | Haiku for easy documents, Sonnet for hard ones; escalate when the cheap one is unsure; PDFs and photos arrive | LiteLLM router settings |
| 5 | Embeddings | Search by meaning vs keywords, and where embeddings lose | Embeddings through the gateway (`embed` alias) |
| 6 | Vector DB + chunking | Pipeline: read → split into chunks → embed → store with tags | Chroma, a folder on disk |
| 7 | RAG | "How much did we pay Acme in Q3?" answered with sources | Same Chroma store |
| 8 | Context engineering | Token budget, what goes into the prompt, prompt caching | Plain Python |
| 9 | Evals | Score extraction accuracy; check answers stick to the documents; rerun on every change | Golden set in `data/golden/` |
| 10 | Semantic cache | Reuse answers to questions that mean the same thing; find a pair that wrongly hits | Hand-built on Chroma (~30 lines) |
| 11 | Tool calling + MCP | Hand-built tool loop, then a DocuMind MCP server used from Claude Code; live prompt-injection demo | MCP Python SDK over stdio |
| 12 | LangChain | Rebuild the Module 7 Q&A with LangChain; evals must still pass | |
| 13 | LangGraph | Upload agent: classify → extract → check → retry, or ask a human when unsure | Local checkpoint file |
| 14 | Capstone | React UI and dashboard; explain the whole system on a whiteboard | React files served locally by one small Python process |

### Module details

**0 · How LLMs work.** What a call is (messages in, one message out); tokens and what they cost;
the context window and the output limit (a cut-off answer); the model has no memory; the same
question gives different answers. App: `documind summarize <file>`.

**1 · Prompt engineering + structured output.** System vs user prompts; being specific; XML tags
to keep instructions apart from data; few-shot examples; asking for JSON vs *enforcing* a schema;
how hallucination happens and how nullable fields reduce it. App: `documind extract <file>`
(classify, then extract with the right schema). Data grows to **10 documents**, each with a
hand-checked answer in `data/golden/`, and a first score against them.
- Invoice: `{vendor, invoice_no, invoice_date, due_date, currency, subtotal, tax, total, line_items[]}`
- Receipt: `{merchant, date, currency, subtotal, tax, tip, total, payment_method, items[]}`

**2 · LiteLLM gateway.** Why a gateway; aliases; one client, three vendors (Claude, GPT, local
model if Ollama is running); fallbacks when a vendor fails; retries and timeouts; spend cap and
approved models (virtual keys explained). App: summarize and extract go through aliases.

**3 · Observability.** Logs vs traces vs spans; latency and cost per step; prompt versions. Break
it: find the slowest, most expensive step from the trace alone.

**4 · Model routing.** Rules, a classifier, and "cheap first, escalate when unsure". Cost/quality/
speed trade-off. App: easy documents → `fast`; multi-page, blurry photos, handwriting → `smart`;
totals that don't add up → retry on `smart`. PDF text and phone photos (vision) arrive here.

**5 · Embeddings.** Vectors, cosine similarity, a 2D plot. Break it: synonyms ("amount due" ≈
"total") where embeddings win; exact invoice numbers where they lose.

**6 · Vector DB + chunking.** Chunk size and overlap, metadata filters, nearest-neighbour search.
Break it: 100-token vs 1,000-token chunks.

**7 · RAG.** Retrieve → augment → generate; top-k; citations; hybrid search; reranking; "I don't
know". Break it: ask about something that isn't in any document.

**8 · Context engineering.** The context budget; lost-in-the-middle; summarising history; prompt
caching. Break it: 50 chunks vs 5 good ones.

**9 · Evals.** Golden datasets; exact vs fuzzy scoring; free checks (totals add up); LLM as judge;
RAG metrics (faithfulness, retrieval hit rate); regression runs.

**10 · Semantic cache.** Exact vs semantic; the similarity threshold; TTL; wrong hits ("Acme Q3" ≈
"Acme Q4").

**11 · Tool calling + MCP.** Tool schemas and the tool loop by hand; MCP server vs client; tools,
resources, prompts. App: a DocuMind MCP server (`upload_document`, `search_docs`, `get_fields`).
Break it: a document hiding instructions for the model.

**12 · LangChain.** Chat models, prompt templates, retrievers, LCEL, output parsers; what the
framework hides. Module 9 evals must still pass.

**13 · LangGraph.** State, nodes, edges; conditional branches; retries; checkpointing; pausing for
a human. Plain-code checks: line items add up to the subtotal; subtotal + tax (+ tip) = total;
dates are valid; duplicate invoice numbers are flagged.

**14 · Capstone.** A UI for upload, review and chat; a dashboard of cost, speed and eval scores;
explain the whole system on a whiteboard in 10 minutes.

---

## 4. How each module runs

1. **Read** a section of `chapter.html` (open it in your browser).
2. **Run** that section's script from the repo root. Read its docstring first; it says what to
   look for.
3. **Break it:** run `99_break_it.py`. Predict each result before you read it.
4. **Checkpoint:** answer the questions at the end of the chapter.

We build one module at a time; Module N+1 is not built until you finish Module N. Model IDs and
prices are checked against current docs when each module is built.
