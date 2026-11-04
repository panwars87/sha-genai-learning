# GenAI Fundamentals — Learning Plan

**Product we build:** **DocuMind**, an Intelligent Document Processing (IDP) app.
You upload a document (invoice, receipt, contract, bank statement); an **agent** classifies it, extracts fields, checks them, files it away, and lets you **chat with all your documents**.

**Approach:** concepts first, code second. Each phase = one concept, one small feature, one "break it" experiment. A coding agent writes the code; you own the *why*.

---

## 1. The finished product (where we're heading)

```
                ┌──────────────────────────── React UI ────────────────────────────┐
                │   Upload  ·  Review extracted fields  ·  Chat with my documents   │
                └───────────────┬───────────────────────────────┬──────────────────┘
                                │                               │
                       ┌────────▼────────┐             ┌────────▼────────┐
                       │  Upload Agent   │             │   Q&A (RAG)     │
                       │  (LangGraph)    │             │   (LangChain)   │
                       └────────┬────────┘             └────────┬────────┘
     classify → extract → validate → human review? → store      │
                                │                               │
                ┌───────────────▼───────────────────────────────▼───────────────┐
                │   Semantic Cache (Redis)  →  LiteLLM Gateway + Model Router    │
                │          cheap model ◄── route ──► strong model                │
                └───────────────┬───────────────────────────────┬───────────────┘
                                │                               │
                  ┌─────────────▼──────────┐       ┌────────────▼────────────┐
                  │ Embeddings → Vector DB │       │ Postgres (fields/meta)  │
                  └────────────────────────┘       └─────────────────────────┘

  MCP Server: exposes upload_document / search_docs / get_fields to Claude Desktop / Claude Code
  Langfuse: every call traced, logged, costed  ·  Evals: golden dataset scores every change
```

## 2. Suggested stack (keep it boring)

| Layer | Pick | Why |
|---|---|---|
| Language / API | Python + FastAPI | Your stack; every GenAI lib is Python-first |
| UI | React | Your stack (comes late — CLI first) |
| LLMs | Claude (Haiku = cheap, Sonnet/Opus = strong) + one local model via Ollama | Real routing choices |
| Gateway | LiteLLM (proxy mode) | One API, many models, cost + fallbacks + cache built in |
| Vector DB | Chroma to learn → pgvector to "productionize" | Simplest first, enterprise-friendly second |
| Cache | Redis (LiteLLM semantic cache) | Standard |
| Tracing / evals | Langfuse (self-hosted or cloud) | Open source; plugs into LiteLLM, LangChain, LangGraph |
| Agents | LangChain + LangGraph | As requested |
| Tools | MCP (Python SDK) | The standard for tool calling across clients |
| Test docs | Synthetic/public invoices, receipts, contracts | **Never real JPMC or personal data** |

> Tool versions and APIs move fast — at each phase we verify current docs before building.

---

## 3. The phases

Each phase: **Concept (ELI10)** → **Build** → **Break-it experiment** → **You can explain…** checkpoint.

### Phase 0 — How an LLM actually works
- **ELI10:** An LLM is a super-autocomplete. It reads your words as little pieces (tokens) and guesses the next piece, over and over. It has no memory — you resend everything every time.
- **Concepts:** tokens, context window, temperature, stateless calls, input vs output pricing.
- **Build:** CLI: `documind summarize invoice.pdf` → one direct Anthropic API call.
- **Break it:** temperature 0 vs 1 on same prompt; overflow the context window; count tokens/cost.
- **Checkpoint:** Why does a chat "remember"? (It doesn't — the app resends history.)

### Phase 1 — Prompt engineering + structured output
- **ELI10:** A prompt is instructions to a very smart new intern. Clear instructions + examples = good work. Asking for a form (JSON) instead of an essay = usable work.
- **Concepts:** system prompt, roles, few-shot examples, XML tags, JSON schema / structured outputs, hallucination.
- **Build:** `documind extract invoice.pdf` → `{vendor, invoice_no, date, total, line_items[]}`.
- **Break it:** remove examples; feed a receipt to the invoice prompt; watch it invent fields.
- **Start the golden set:** 10 docs with hand-written correct answers (used in Phase 9).
- **Checkpoint:** Difference between asking nicely and constraining with a schema.

### Phase 2 — LiteLLM gateway
- **ELI10:** A universal TV remote. One remote, every brand of TV. Your app talks to LiteLLM; LiteLLM talks to Claude, GPT, or a local model.
- **Concepts:** OpenAI-compatible API format, provider abstraction, retries, fallbacks, rate limits, virtual keys, budgets, cost tracking.
- **Build:** run LiteLLM proxy; point the app at it; same extraction on Claude Haiku, Claude Sonnet, local Ollama.
- **Break it:** kill a provider (bad key) → fallback kicks in.
- **Checkpoint:** Why enterprises put a gateway between apps and models.

### Phase 3 — Observability: logging, tracing, cost
- **ELI10:** Putting a GoPro on every request so you can rewatch exactly what happened, how long it took, and what it cost.
- **Concepts:** log vs trace vs span, latency, token usage, cost per request, prompt versioning, OpenTelemetry basics.
- **Build:** Langfuse wired to LiteLLM. Every call from here on is traced.
- **Break it:** find your slowest and most expensive call from the dashboard alone.
- **Checkpoint:** Why we add this *now* — every later phase is easier to understand when you can see inside it.

### Phase 4 — Model routing
- **ELI10:** Don't send a surgeon to put on a band-aid. Easy jobs → cheap fast model; hard jobs → expensive smart model.
- **Concepts:** cost/quality/latency triangle, rule-based routing, classifier routing, cascade (try cheap, escalate if low confidence), LiteLLM router strategies.
- **Build:** classify doc type with Haiku → extract with Haiku for receipts, Sonnet for contracts. Low confidence → escalate.
- **Break it:** compare cost + accuracy table: all-cheap vs all-strong vs routed.
- **Checkpoint:** When routing saves money vs when it silently costs accuracy.

### Phase 5 — Embeddings
- **ELI10:** Turn every sentence into a GPS coordinate in "meaning-land." Sentences about similar things live near each other.
- **Concepts:** vectors, dimensions, cosine similarity, embedding models, why "invoice total" ≈ "amount due".
- **Build:** embed 50 chunks; plot in 2D; query by meaning.
- **Break it:** compare keyword search vs embedding search on synonyms and on exact IDs (embeddings lose on IDs!).
- **Checkpoint:** What an embedding captures and what it misses.

### Phase 6 — Vector DB + chunking
- **ELI10:** A library where books are shelved by *meaning* instead of alphabet, with a librarian who finds the nearest books instantly.
- **Concepts:** chunking (size, overlap, by section), metadata (doc_type, vendor, date), approximate nearest neighbor (HNSW), metadata filters, Chroma → pgvector.
- **Build:** ingestion pipeline: parse → chunk → embed → store with metadata.
- **Break it:** chunk size 100 vs 1000 tokens — watch retrieval quality change.
- **Checkpoint:** Why chunking is the #1 hidden lever in RAG.

### Phase 7 — RAG (chat with your documents)
- **ELI10:** An open-book exam. Before answering, the model looks up the right pages, then answers *only* from those pages and shows which page it used.
- **Concepts:** retrieve → augment → generate, top-k, citations, grounding, hybrid search (keyword + vector), reranking, "I don't know" behavior.

```
  Question ──► embed ──► Vector DB (top-k chunks) ──► rerank ──► prompt = question + chunks ──► LLM ──► answer + citations
```

- **Build:** `documind ask "How much did we pay Acme in Q3?"` with citations.
- **Break it:** ask about something not in any doc — does it make things up?
- **Checkpoint:** Draw the RAG pipeline from memory; name 3 places it fails.

### Phase 8 — Context engineering
- **ELI10:** The model's desk is small. Context engineering is deciding what goes on the desk — the right papers, in the right order — and clearing junk off.
- **Concepts:** context budget, ordering ("lost in the middle"), system vs retrieved vs history, summarization/compaction, prompt caching (provider-side, cheaper repeated prefixes).
- **Build:** token budget manager for RAG + chat history; enable prompt caching on the static system prompt.
- **Break it:** stuff 50 chunks vs 5 good ones — quality and cost both change.
- **Checkpoint:** Prompt engineering (how you ask) vs context engineering (what the model sees).

### Phase 9 — Evals
- **ELI10:** A report card for your AI. Before shipping any change, it retakes the same test so you know if it got smarter or dumber.
- **Concepts:** golden dataset, exact-match vs fuzzy metrics, LLM-as-judge, RAG metrics (faithfulness, answer relevance, context recall), regression testing, eval in CI.
- **Build:** extraction eval (field accuracy) + RAG eval (faithfulness) in Langfuse; one-command run.
- **Break it:** change a prompt "to improve it" — the eval catches a regression.
- **Checkpoint:** Why "it looked good when I tried it" is not a quality bar.

### Phase 10 — Semantic cache
- **ELI10:** If someone asks "What's Acme's total?" and then "How much is Acme's bill?", that's the same question — reuse the answer instead of paying again.
- **Concepts:** exact cache vs semantic cache, similarity threshold, TTL, cache invalidation, *danger:* wrong cache hits ("Acme Q3" ≈ "Acme Q4").
- **Build:** LiteLLM + Redis semantic cache in front of Q&A.
- **Break it:** tune threshold 0.80 vs 0.95; find a pair of questions that wrongly hit.
- **Checkpoint:** When semantic cache is safe (FAQ-ish) vs risky (numbers, dates, per-user data).

### Phase 11 — Tool calling + MCP
- **ELI10:** Give the model a toolbox. It can't *do* things, but it can say "please run `search_docs('Acme')`" — your code runs it and hands back the result. MCP is the universal plug so any AI app can use your toolbox.
- **Concepts:** tool schema, tool-use loop (model asks → you run → model continues), parallel tools, MCP server/client, tools vs resources vs prompts, security (least privilege, prompt injection via documents).

```
  User ─► LLM ─► "call search_docs(vendor='Acme')" ─► your code runs it ─► result ─► LLM ─► final answer
```

- **Build:** (a) raw tool-use loop by hand; (b) DocuMind MCP server with `upload_document`, `search_docs`, `get_fields`; use it from Claude Desktop / Claude Code.
- **Break it:** a document containing "ignore previous instructions…" — see prompt injection live.
- **Checkpoint:** Explain the tool-use loop; why MCP beats custom integrations.

### Phase 12 — LangChain
- **ELI10:** LEGO bricks for LLM apps. Prebuilt pieces (loaders, splitters, retrievers, prompts) that snap together.
- **Concepts:** chat models, prompt templates, retrievers, chains (LCEL), output parsers; what abstraction buys you and what it hides.
- **Build:** rebuild Phase 7 RAG in LangChain. Evals must still pass.
- **Checkpoint:** When you'd use LangChain vs plain SDK calls (honest trade-offs).

### Phase 13 — LangGraph (the Upload Agent)
- **ELI10:** A flowchart the AI walks through. Each box does one job; arrows decide where to go next, including loops ("try again") and "ask a human."
- **Concepts:** state, nodes, edges, conditional edges, loops/retries, checkpointing, human-in-the-loop, agent vs workflow.

```
  upload ─► classify ─► extract ─► validate ──ok──► store ─► index ─► done
                            ▲          │
                            └─retry────┤ (bad fields)
                                       └─low confidence─► human review ─► store
```

- **Build:** the Upload Agent; it uses the MCP tools; every step traced in Langfuse.
- **Break it:** upload an unreadable scan — watch retry, then human escalation.
- **Checkpoint:** Why a graph is safer than a free-roaming agent for business processes.

### Phase 14 — Capstone: ship DocuMind
- React UI (upload, review fields, chat), dashboard of cost/latency/eval scores, README with architecture diagram.
- **Final test:** explain the whole system end-to-end on a whiteboard in 10 minutes — to your team.

---

## 4. How we'll work each session

1. I teach the concept (ELI10 + diagram), you ask questions.
2. A coding agent builds the feature in this repo (small PR per phase).
3. We run the break-it experiment together and record findings in `notes/phase-XX.md`.
4. You pass the checkpoint, then we move on. No jumping ahead.

Rough pace: 1–2 phases per week → ~8–10 weeks.
