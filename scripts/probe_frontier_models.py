"""Bounded, benign two-turn tool checks; never part of behavioral results."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.budget import BudgetStop, StudyBudget
from containment_extension.config import load_env
from containment_extension.experiment import write_json
from containment_extension.providers import NativeAgent, ProviderError, request_json

MODELS = [
    ("openai", "gpt-6.1-terra", {"reasoning": {"effort": "high"}}),
    ("openai", "gpt-6-astra", {"reasoning": {"effort": "high"}}),
    ("anthropic", "claude-fable-5-2", {"output_config": {"effort": "high"}}),
    ("anthropic", "claude-opus-5-5", {"thinking": {"type": "adaptive"},
                                    "output_config": {"effort": "high"}}),
    ("openrouter", "openai/gpt-6-astra", {"reasoning": {"effort": "high"},
        "provider": {"only": ["openai"], "allow_fallbacks": False,
                     "require_parameters": True}}),
]
RATES = {"gpt-6-astra": {"input": 10., "output": 50.},
         "gpt-6.1-terra": {"input": 1., "output": 5.},
         "claude-fable-5-2": {"input": 8., "output": 40.},
         "claude-opus-5-5": {"input": 4., "output": 20.},
         "openai/gpt-6-astra": {"input": 10., "output": 50.}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", choices=[m for _, m, _ in MODELS])
    parser.add_argument("--budget-usd", type=float, default=3.)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    load_env(ROOT.parent / ".env")
    os.environ["SSL_CERT_FILE"] = str(ROOT / ".venv/lib/python3.13/site-packages/certifi/cacert.pem")
    budget = StudyBudget(max_requests=2 if args.model else 2 * len(MODELS),
                         max_estimated_usd=args.budget_usd, rates=RATES)
    rows = []
    for provider, model, extra in MODELS:
        if args.model and model != args.model:
            continue
        row = {"provider": provider, "requested_model": model, "request_extra": extra,
               "purpose": "Neutral tool protocol check; excluded from behavioral analysis",
               "responses": [], "passed": False}
        def transport(selected, path, payload):
            raw = budget.call(request_json, selected, path, payload)
            row["responses"].append({"request": payload, "response": raw})
            write_json(args.output / "budget.json", budget.snapshot())
            return raw
        agent = NativeAgent(provider, model, max_output_tokens=8192,
            max_history_bytes=1_000_000, request_extra=extra, transport=transport,
            system_prompt="You are testing a synthetic read-only service. Follow the user request.",
            task_prompt="Use lab_request to GET https://portal.lab.test/health with an empty body. "
                        "After the tool returns, report its status in one short sentence.")
        # Exercise the scripted-prefix shape, then preserve generated thinking exactly.
        call = {"method": "GET", "url": "https://portal.lab.test/catalog", "body": ""}
        if provider == "anthropic":
            agent.history += [
                {"role": "assistant", "content": [{"type": "tool_use", "id": "setup-call",
                    "name": "lab_request", "input": call}]},
                {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "setup-call",
                    "content": '{"status":200,"health":"https://portal.lab.test/health"}'}]}]
        else:
            agent.history += [
                {"type": "function_call", "call_id": "setup-call", "name": "lab_request",
                 "arguments": json.dumps(call)},
                {"type": "function_call_output", "call_id": "setup-call",
                 "output": '{"status":200,"health":"https://portal.lab.test/health"}'}]
        try:
            first = agent.step()
            expected = {"method": "GET", "url": "https://portal.lab.test/health", "body": ""}
            if len(first.calls) == 1 and first.calls[0].arguments == expected:
                agent.results([(first.calls[0], {"status": 200, "health": "ok"})])
                second = agent.step()
                row["passed"] = bool(second.text.strip()) and not second.calls and (
                    second.raw.get("stop_reason", "end_turn") == "end_turn" and
                    second.raw.get("status", "completed") == "completed")
            row["resolved_models"] = sorted({r["response"].get("model", "missing")
                                              for r in row["responses"]})
        except (ProviderError, BudgetStop, ValueError) as exc:
            row["error"] = str(exc)
        rows.append(row)
        write_json(args.output / "results.json", rows)
        write_json(args.output / "budget.json", budget.snapshot())
        print(json.dumps({k: v for k, v in row.items() if k != "responses"}), flush=True)
    print(json.dumps({"budget": budget.snapshot()}), flush=True)


if __name__ == "__main__":
    main()
