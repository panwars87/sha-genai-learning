"""L06 · Tokens, cost, and the "randomness" knobs.

Chapter section 6. Run from the module folder (gateway running, DOCUMIND_API_KEY set):
    uv run --project app python lessons/L06_tokens_cost_and_knobs.py

What you'll see:
    A. Tokens are the unit of cost: a tiny prompt vs a whole invoice.
    B. The same prompt can give different answers on each run.
    C. "temperature", the classic randomness knob, and what current models do with it.
"""

from __future__ import annotations

from _shared import banner, lesson_config, resolve, show
from documind.config import get_settings
from documind.gateway import GatewayRequestError, build_client, chat


def main() -> None:
    cfg = lesson_config()["tokens"]
    client = build_client(get_settings())

    def ask(prompt: str, **extra):
        return chat(
            client,
            model=cfg["alias"],
            messages=[{"role": "user", "content": prompt}],
            max_output_tokens=cfg["max_output_tokens"],
            **extra,
        )

    # A. Tokens: the model reads and writes in tokens (chunks of about 4 characters).
    banner("A · Tokens are the unit of cost")
    invoice_text = resolve(cfg["long_prompt_file"]).read_text(encoding="utf-8")
    for label, prompt in [
        ("short prompt", cfg["short_prompt"]),
        ("whole invoice", f"Summarize:\n{invoice_text}"),
    ]:
        reply = ask(prompt)
        ratio = len(prompt) / reply.input_tokens if reply.input_tokens else 0
        cost = f"${reply.cost_usd:.6f}" if reply.cost_usd is not None else "n/a"
        show(
            label,
            f"{len(prompt):>5} chars → {reply.input_tokens:>4} input tokens "
            f"(~{ratio:.1f} chars/token), {reply.output_tokens:>4} output, {cost}",
        )
    print("\n  Output tokens cost about 5x input tokens. Long answers are the expensive part.")

    # B. Non-determinism: the model picks each next token with some randomness.
    banner(f"B · Same prompt, {cfg['repeat_runs']} runs: {cfg['repeat_prompt']}")
    for run in range(1, cfg["repeat_runs"] + 1):
        show(f"run {run}", ask(cfg["repeat_prompt"]).text.strip())
    print(
        "\n  Different answers to the same input. Never assume an LLM is repeatable;\n"
        "  that is why we will need evals (Module 09), not 'I tried it once'.\n"
        "  (In mock mode every run returns the same canned text. Use real models here.)"
    )

    # C. Temperature: classic models let you turn randomness down with temperature=0.
    banner(f"C · Sending temperature={cfg['temperature_probe']}")
    try:
        reply = ask(cfg["repeat_prompt"], temperature=cfg["temperature_probe"])
        print(f"  Accepted by this model. Answer: {reply.text.strip()}")
    except GatewayRequestError as exc:
        print(f"  Rejected: {exc}")
    print(
        "\n  Current Claude models no longer accept temperature/top_p: they think before\n"
        "  answering, and you steer them with clear prompts and an 'effort' level instead.\n"
        "  Lesson: knobs from older tutorials can break on newer models. The gateway's\n"
        "  drop_params=false setting makes such mismatches fail loudly instead of silently."
    )


if __name__ == "__main__":
    main()
