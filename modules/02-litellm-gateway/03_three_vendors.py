"""Module 2 · Section 3: one client, three vendors: the same extraction everywhere.

Run:   uv run modules/02-litellm-gateway/03_three_vendors.py

The SAME function (documind.extract.extract_document) runs on Anthropic, OpenAI and, if you
have Ollama running, a free local model. Only the alias string changes.

Optional local model (skipped if absent; nothing else needs it):
    brew install ollama && ollama serve        # in another terminal
    ollama pull llama3.2

Look for: the fields, cost and speed per vendor. Small local models are free and private but
usually less accurate; that trade-off is what model routing (Module 4) manages.
"""

import urllib.request

from documind.config import DATA_DIR, get_settings
from documind.extract import extract_document
from documind.llm import LLMError

DOCUMENT = DATA_DIR / "invoices" / "INV-0457-umbrella-print.txt"
ALIASES = ["fast-anthropic", "fast-openai", "local"]
OLLAMA_URL = "http://localhost:11434/api/tags"

settings = get_settings()


def ollama_running() -> bool:
    """Is a local Ollama server answering? (Mock mode never needs it.)"""
    if settings.gateway.mock_response is not None:
        return True
    try:
        with urllib.request.urlopen(OLLAMA_URL, timeout=1):
            return True
    except OSError:
        return False


for alias in ALIASES:
    print(f"── {alias} ({settings.gateway.model_for(alias)}) ──")
    if alias == "local" and not ollama_running():
        print("  skipped: Ollama is not running (optional; see the docstring)\n")
        continue
    try:
        result = extract_document(DOCUMENT, alias=alias)
    except LLMError as error:
        print(f"  ✗ {error}\n")
        continue
    f = result.fields
    if f is not None:
        print(f"  {result.doc_type}: {f.model_dump_json(exclude={'line_items', 'items'})}")
    for reply in result.replies:
        print(f"  {reply.stats()}")
    print(f"  total cost ${result.cost_usd:.6f}\n")
