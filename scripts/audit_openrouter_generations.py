"""Ask OpenRouter which provider and model served every response of an allocation.

Usage: audit_openrouter_generations.py RUN

Reads response ids from each episode transcript, fetches the generation record
for each (metadata only, no model call) and writes RUN/provider-audit.json. A
record that is not yet available is retried a few times; anything still
missing is reported, not assumed.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.config import load_env

FIELDS = ["provider_name", "model", "finish_reason", "native_tokens_prompt", "native_tokens_completion",
          "native_tokens_reasoning", "total_cost"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    load_env(ROOT.parent / ".env")
    import certifi
    context = ssl.create_default_context(cafile=certifi.where())
    key = os.environ["OPENROUTER_API_KEY"]
    target = args.run / "provider-audit.json"
    saved = json.loads(target.read_text())["records"] if target.exists() else {}
    wanted = []
    for transcript in sorted(args.run.glob("episodes/*/transcript.jsonl")):
        for line in transcript.read_text().splitlines():
            response = json.loads(line).get("provider_response")
            if response and response.get("id"):
                wanted.append((transcript.parent.name, response["id"]))

    def fetch(item):
        run, gid = item
        if saved.get(gid, {}).get("provider_name"):
            return gid, saved[gid]
        url = "https://openrouter.ai/api/v1/generation?id=" + urllib.parse.quote(gid)
        for attempt in range(5):
            try:
                request = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
                with urllib.request.urlopen(request, timeout=60, context=context) as reply:
                    data = json.loads(reply.read())["data"]
                return gid, {"run": run, **{k: data.get(k) for k in FIELDS}}
            except urllib.error.HTTPError as exc:
                error = f"HTTP {exc.code}"
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
                error = type(exc).__name__
            time.sleep(2 + 3 * attempt)
        return gid, {"run": run, "error": error}

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = dict(pool.map(fetch, wanted))
    summary = {"responses": len(wanted), "records": sum("error" not in r for r in records.values()),
               "missing": sum("error" in r for r in records.values()),
               "providers": dict(Counter(r.get("provider_name") for r in records.values() if "error" not in r)),
               "models": dict(Counter(r.get("model") for r in records.values() if "error" not in r)),
               "openrouter_cost_usd": round(sum(r.get("total_cost") or 0 for r in records.values()), 4),
               "episodes_with_any_other_provider": sorted({r["run"] for r in records.values()
                                                           if "error" not in r and r.get("provider_name") != "Anthropic"})}
    target.write_text(json.dumps({"summary": summary, "records": records}, indent=1, sort_keys=True) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
