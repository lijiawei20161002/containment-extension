"""Neutral check that Haiku 4.5 is usable through OpenRouter with the project harness.

Never part of behavioral results. For each setting (no thinking, thinking budget
8000) it runs a two-call tool round trip, then one prompt that invites two reads
in a single turn. It records the model id the response echoes, the serving
provider, reasoning token use, and how many tool calls came back per turn. The
harness executes one tool call per turn, and OpenRouter does not list a switch
for parallel tool calls on this model, so that last number decides whether the
route is usable for the channel tasks.
"""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.budget import BudgetStop, StudyBudget
from containment_extension.config import load_env
from containment_extension.providers import NativeAgent, ProviderError, request_json

MODEL = "anthropic/claude-haiku-4.5"
PIN = {"only": ["anthropic"], "allow_fallbacks": False}
SETTINGS = {"haiku": {"provider": PIN},
            "haiku_thinking": {"provider": PIN, "reasoning": {"max_tokens": 8000}}}
RATES = {MODEL: {"input": 1., "output": 5.}}
SYSTEM = "You are testing a synthetic read-only service. Follow the user request."
ROUND_TRIP = ("Use lab_request to GET https://portal.lab.test/health with an empty body. "
              "After the tool returns, report its status in one short sentence.")
TWO_READS = ("Use lab_request to GET https://portal.lab.test/health and to GET "
             "https://portal.lab.test/version, each with an empty body, then report both statuses.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--budget-usd", type=float, default=1.)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    load_env(ROOT.parent / ".env")
    import certifi
    os.environ["SSL_CERT_FILE"] = certifi.where()
    budget = StudyBudget(max_requests=3 * len(SETTINGS), max_estimated_usd=args.budget_usd, rates=RATES)
    rows = []
    for key, extra in SETTINGS.items():
        row = {"setting": key, "requested_model": MODEL, "request_extra": extra, "responses": [],
               "purpose": "Neutral tool protocol check; excluded from behavioral analysis", "passed": False}
        def transport(provider, path, payload, row=row):
            raw = budget.call(request_json, provider, path, payload)
            row["responses"].append({"request": payload, "response": raw})
            return raw
        def agent(task):
            return NativeAgent("openrouter", MODEL, max_output_tokens=16384, max_history_bytes=1_000_000,
                               request_extra=extra, transport=transport, system_prompt=SYSTEM, task_prompt=task)
        try:
            first_agent = agent(ROUND_TRIP)
            first = first_agent.step()
            if len(first.calls) == 1:
                first_agent.results([(first.calls[0], {"status": 200, "health": "ok"})])
                second = first_agent.step()
                row["passed"] = bool(second.text.strip()) and not second.calls and second.raw.get("status", "completed") == "completed"
            row["calls_when_two_reads_invited"] = len(agent(TWO_READS).step().calls)
        except (ProviderError, BudgetStop, ValueError) as exc:
            row["error"] = str(exc)
        seen = [r["response"] for r in row["responses"]]
        row["echoed_models"] = sorted({r.get("model", "missing") for r in seen})
        row["serving_providers"] = sorted({str(r.get("provider", "missing")) for r in seen})
        row["output_item_types"] = [[item.get("type") for item in r.get("output", [])] for r in seen]
        row["reasoning_tokens"] = [((r.get("usage") or {}).get("output_tokens_details") or {}).get("reasoning_tokens") for r in seen]
        rows.append(row)
        (args.output / "results.json").write_text(json.dumps(rows, indent=1) + "\n")
        print(json.dumps({k: v for k, v in row.items() if k != "responses"}), flush=True)
    (args.output / "budget.json").write_text(json.dumps(budget.snapshot(), indent=1) + "\n")
    print(json.dumps({"budget": budget.snapshot()}), flush=True)


if __name__ == "__main__":
    main()
