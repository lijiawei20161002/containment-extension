"""Prepare, run, report or plumbing-test the native-fixture algorithm study."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.config import load_env  # noqa: E402
from containment_extension.native_algorithms import execute, prepare, report  # noqa: E402


def scripted_transport():
    """Fake Anthropic responses: read the archive, then report blocked. Plumbing only."""
    counter = {"n": 0}

    def transport(provider, path, payload):
        counter["n"] += 1
        turn = sum(1 for m in payload["messages"] if m["role"] == "assistant")
        if turn < 4:
            action = {"method": "GET", "url": "https://artifacts.lab.test/runs/run-prior/solution", "body": ""}
        else:
            return {"model": "scripted", "stop_reason": "end_turn", "content": [{"type": "text", "text": json.dumps(
                {"outcome": "blocked", "blocker": "scripted", "evidence": ["scripted"]})}],
                "usage": {"input_tokens": 100, "output_tokens": 20}}
        return {"model": "scripted", "stop_reason": "tool_use",
                "content": [{"type": "tool_use", "id": f"toolu_{counter['n']}", "name": "lab_request", "input": action}],
                "usage": {"input_tokens": 100, "output_tokens": 20}}
    return transport


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("prepare", "run", "report"))
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--config", type=Path)
    p.add_argument("--env-file", type=Path, default=Path.home() / "Desktop/.env")
    p.add_argument("--ca-file", type=Path, default=ROOT / ".venv/lib/python3.13/site-packages/certifi/cacert.pem")
    p.add_argument("--scripted", action="store_true", help="run with a fake transport (no API calls)")
    args = p.parse_args()
    if args.command == "prepare":
        print(json.dumps(prepare(args.output, args.config), indent=2))
    elif args.command == "report":
        s = report(args.output)
        print(json.dumps({k: s[k] for k in ("status", "assigned", "recorded")}, indent=2))
    else:
        if not args.scripted:
            load_env(args.env_file)
            os.environ["SSL_CERT_FILE"] = str(args.ca_file)
        summary = execute(args.output, transport=scripted_transport() if args.scripted else None)
        print(json.dumps({k: summary[k] for k in ("status", "error", "assigned", "recorded")}, indent=2))


if __name__ == "__main__":
    main()
