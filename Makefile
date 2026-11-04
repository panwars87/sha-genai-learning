# DocuMind course shortcuts.  MODULE is the two-digit module number.
#
#   make setup MODULE=01          install the module's app + lesson deps
#   make gateway MODULE=01        start the AI gateway (real vendors)
#   make gateway-mock MODULE=01   start the gateway with fake replies (free, offline-ish)
#   make test MODULE=01           run the module app's tests
#   make lint MODULE=01           ruff lint + format check

MODULE ?= 01
MODULE_DIR := $(firstword $(wildcard modules/$(MODULE)-*))

.PHONY: check-module setup gateway gateway-mock test lint

check-module:
	@test -n "$(MODULE_DIR)" || (echo "No module folder matches modules/$(MODULE)-*" && exit 1)

setup: check-module
	cd $(MODULE_DIR)/app && uv sync

gateway: check-module
	infra/start_gateway.sh $(MODULE_DIR)/gateway/config.yaml

gateway-mock: check-module
	infra/start_gateway.sh $(MODULE_DIR)/gateway/config.mock.yaml

test: check-module
	cd $(MODULE_DIR)/app && uv run pytest -q

lint: check-module
	cd $(MODULE_DIR) && uv run --project app ruff check --config app/pyproject.toml . && uv run --project app ruff format --config app/pyproject.toml --check .
