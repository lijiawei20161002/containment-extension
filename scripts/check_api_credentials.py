"""Check configured provider keys without logging credentials or error bodies."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import ssl
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.config import load_env, secret
from containment_extension.providers import NoRedirect

PROVIDERS = {
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY", "/models"),
    "anthropic": ("https://api.anthropic.com/v1", "ANTHROPIC_API_KEY", "/models"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "/key"),
}


def check(provider, context):
    base, key_name, path = PROVIDERS[provider]
    result = {"provider": provider, "checked_at": datetime.now(timezone.utc).isoformat()}
    if not os.environ.get(key_name):
        return {**result, "status": "not_configured"}
    headers = ({"x-api-key": secret(key_name), "anthropic-version": "2023-06-01"}
               if provider == "anthropic" else {"Authorization": "Bearer " + secret(key_name)})
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), NoRedirect(),
        urllib.request.HTTPSHandler(context=context),
    )
    try:
        with opener.open(urllib.request.Request(base + path, headers=headers), timeout=25) as r:
            body = json.loads(r.read(4_000_000))
            result.update(status="authenticated", http_status=r.status)
        if provider != "openrouter":
            ids = [m["id"] for m in body.get("data", [])]
            result["historical_models_available"] = [m for m in ids if m in (
                "gpt-4.1-mini-2025-04-14", "claude-haiku-4-5-20251001")]
        else:
            data = body.get("data", {})
            result["credit_limit_remaining"] = data.get("limit_remaining")
            result["is_free_tier"] = data.get("is_free_tier")
    except urllib.error.HTTPError as exc:
        result.update(status="http_error", http_status=exc.code)
        try:
            err = json.loads(exc.read(16384)).get("error", {})
            for key in ("code", "type"):
                value = err.get(key)
                if isinstance(value, str) and re.fullmatch(r"[a-z_]{1,64}", value):
                    result["error_" + key] = value
        except (ValueError, AttributeError):
            pass
    except urllib.error.URLError as exc:
        result.update(status="connection_error", error_type=type(exc.reason).__name__)
        if isinstance(exc.reason, ssl.SSLCertVerificationError):
            result["error_code"] = "certificate_verify_failed"
    except (TimeoutError, OSError, ValueError) as exc:
        result.update(status="connection_error", error_type=type(exc).__name__)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--env-file", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--ca-file", type=Path)
    args = p.parse_args()
    load_env(args.env_file)
    context = ssl.create_default_context(cafile=str(args.ca_file) if args.ca_file else None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as f:
        with ThreadPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(lambda provider: check(provider, context), PROVIDERS))
        report = {"checks": results, "inference_tested": False,
                  "tls_verification": True, "explicit_ca_bundle": bool(args.ca_file)}
        json.dump(report, f, indent=2)
        f.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
