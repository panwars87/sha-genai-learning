# DocuMind: a GenAI course you build

A hands-on course in GenAI fundamentals. Module by module, you build **DocuMind**, an app that reads invoices and receipts, extracts their fields, and answers questions across them. Along the way you learn LiteLLM, RAG, embeddings, vector databases, semantic caching, model routing, tool calling and MCP, context engineering, observability, evals, LangChain and LangGraph.

- **Plan and module list:** [PLAN.md](PLAN.md)
- **How each module is built:** [CLAUDE.md](CLAUDE.md)

| Module | Chapter | Code |
|---|---|---|
| 00 · Course setup | [read](https://claude.ai/artifact/QaCn2vyZC1yRk8qNPC2rzB) | [modules/00-course-setup](modules/00-course-setup) |
| 01 · LLM basics + AI gateway | [read](https://claude.ai/artifact/AJzEw8t72U7eazv6X1Z4MY) | [modules/01-llm-basics-and-ai-gateway](modules/01-llm-basics-and-ai-gateway) |

The chapter links are private artifacts; each chapter is also saved as `chapter.html` in its module folder.

## Quick start (Mac)
```bash
cp .env.example .env                                   # fill in (Module 00)
python3 modules/00-course-setup/lessons/L01_check_tools.py
make setup MODULE=01 && make gateway MODULE=01         # then follow Module 01's README
```
No Docker needed. In Google Colab, open the module's `colab.ipynb` instead.
