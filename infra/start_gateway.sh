#!/usr/bin/env bash
# Start the LiteLLM AI gateway for one module.
#
#   infra/start_gateway.sh modules/01-llm-basics-and-ai-gateway/gateway/config.yaml
#
# What it does:
#   1. Loads .env from the repo root (vendor keys stay inside this process).
#   2. Checks the required variables are set.
#   3. One-time: generates the Prisma client the gateway uses to talk to Postgres.
#   4. Runs the gateway on GATEWAY_PORT (default 4000).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATEWAY_DIR="$REPO_ROOT/infra/gateway"
CONFIG="${1:?usage: start_gateway.sh <path/to/gateway/config.yaml>}"
[[ -f "$CONFIG" ]] || { echo "Config not found: $CONFIG" >&2; exit 1; }
CONFIG="$(cd "$(dirname "$CONFIG")" && pwd)/$(basename "$CONFIG")"   # absolute: we cd below

# 1. Load .env if present (in Colab, variables are exported by the notebook instead).
if [[ -f "$REPO_ROOT/.env" ]]; then
  set -a; source "$REPO_ROOT/.env"; set +a
fi

# 2. Fail fast with a clear message.
for var in LITELLM_MASTER_KEY DATABASE_URL; do
  [[ -n "${!var:-}" ]] || { echo "Missing $var — set it in .env (see .env.example)." >&2; exit 1; }
done
[[ "$LITELLM_MASTER_KEY" == sk-* ]] || { echo "LITELLM_MASTER_KEY must start with 'sk-'." >&2; exit 1; }
if [[ "$CONFIG" != *mock* ]]; then
  for var in ANTHROPIC_API_KEY OPENAI_API_KEY; do
    [[ -n "${!var:-}" ]] || echo "Warning: $var is empty — models from that vendor will fail." >&2
  done
fi

# 3. Install the pinned gateway environment and generate the Prisma client once.
cd "$GATEWAY_DIR"
uv sync --quiet
if [[ ! -f .prisma-generated ]]; then
  echo "First run: generating the Prisma client (one time, ~30s)…"
  SCHEMA="$(uv run --quiet python -c 'import litellm, os; print(os.path.join(os.path.dirname(litellm.__file__), "proxy", "schema.prisma"))')"
  uv run --quiet prisma generate --schema "$SCHEMA" >/dev/null
  touch .prisma-generated
fi

# 4. Run. The .venv/bin on PATH lets the gateway find the prisma CLI for DB migrations.
PORT="${GATEWAY_PORT:-4000}"
echo "AI gateway → http://localhost:$PORT   (config: $CONFIG)"
export PATH="$GATEWAY_DIR/.venv/bin:$PATH"
exec litellm --config "$CONFIG" --port "$PORT"
