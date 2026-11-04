"""L03 · Meet the AI gateway: is it up, and which models does it offer?

Chapter section 3. First start the gateway in another terminal:
    make gateway MODULE=01          (real models)   or
    make gateway-mock MODULE=01     (free, canned replies)
Then, from the module folder:
    uv run --project app python lessons/L03_gateway_health.py

What you'll see:
    The gateway is just an HTTP server. It reports its health, whether its database is
    connected, and the table that maps each alias to a real vendor model.
"""

from __future__ import annotations

from _shared import admin_request, banner, show
from documind.config import get_settings


def main() -> None:
    settings = get_settings()
    banner(f"L03 · The AI gateway at {settings.gateway.base_url}")

    # 1. Liveness: is the process up? (No key needed, like a load balancer check.)
    show("alive?", admin_request("GET", "/health/liveliness").json())

    # 2. Readiness: can it do real work? (Is the key database reachable?)
    readiness = admin_request("GET", "/health/readiness").json()
    show("ready?", readiness.get("status"))
    show("key database", readiness.get("db"))

    # 3. The alias table: what the app asks for → what really answers.
    #    Only an admin sees the vendor side; apps only see aliases.
    print("\n  Alias              → Vendor model")
    print("  " + "-" * 50)
    models = admin_request("GET", "/model/info").json()["data"]
    for entry in models:
        print(f"  {entry['model_name']:<18} → {entry['litellm_params']['model']}")
    print(
        "\n  'fast' and 'smart' are extra aliases (router_settings.model_group_alias in\n"
        "  gateway/config.yaml). They point at the Anthropic entries above."
    )


if __name__ == "__main__":
    main()
