# Module 1 · Prompt engineering + structured output

Read [`chapter.html`](chapter.html) in your browser, section by section. After each section, run
its script from the **repo root**:

| Section | Run | Concept |
|---|---|---|
| 1 | `uv run modules/01-prompts-and-structured-output/01_system_and_user.py` | System vs user; specific beats vague |
| 2 | `uv run modules/01-prompts-and-structured-output/02_xml_tags.py` | Keep data apart from instructions |
| 3 | `uv run modules/01-prompts-and-structured-output/03_few_shot.py` | Examples teach the format |
| 4 | `uv run modules/01-prompts-and-structured-output/04_json_by_asking.py` | Asking for JSON isn't getting it |
| 5 | `uv run modules/01-prompts-and-structured-output/05_structured_output.py` | A schema the answer must fit |
| 6 | `uv run modules/01-prompts-and-structured-output/06_hallucination.py` | Required fields force inventions |
| 7 | `uv run modules/01-prompts-and-structured-output/07_extract_and_score.py` | Extract all 10; score against golden answers |
| Break it | `uv run modules/01-prompts-and-structured-output/99_break_it.py` | Cut-off JSON, wrong schema, a poem, an ambiguous date |

## What this module added to DocuMind
```
documind/schemas.py                 Classification, Invoice, Receipt, LineItem (Pydantic)
documind/extract.py                 classify → extract with the matching schema → validate
documind/prompts/classify_system.md, extract_invoice_system.md, extract_receipt_system.md,
                 document_user.md
documind/llm.py                     chat(..., response_format=Schema)
data/  6 more documents (10 in all) + data/golden/*.json, the right answer for each
uv run python -m documind extract <file>
```
