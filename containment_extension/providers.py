"""Minimal native function-calling adapters, with fixed inference destinations.

No dependency on a provider SDK. Keys occur only in request headers, never in
manifests, model messages, exception text, or saved response metadata.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from .config import secret
from .prompts import SYSTEM_PROMPT, TASK_PROMPT, TOOL_DESCRIPTION, TOOL_PARAMETERS


class ProviderError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProviderError(f"Provider redirect refused (HTTP {code})")


def request_json(provider: str, path: str, payload: dict | None = None) -> dict:
    if provider == "openai":
        base = "https://api.openai.com/v1"
        headers = {"Authorization": "Bearer " + secret("OPENAI_API_KEY")}
        allowed_paths = {"/models", "/responses"}
    elif provider == "anthropic":
        base = "https://api.anthropic.com/v1"
        headers = {"x-api-key": secret("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01"}
        allowed_paths = {"/models", "/messages"}
    else:
        raise ValueError("Provider must be openai or anthropic")
    if path not in allowed_paths:
        raise ValueError("Unsupported inference route")
    headers["Content-Type"] = "application/json"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base + path, headers=headers, data=data)
    # Ignore ambient proxy configuration and never forward a credential via redirects.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=90) as response:
            raw = response.read(4_000_001)
        if len(raw) > 4_000_000:
            raise ProviderError("Provider response exceeded size limit")
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ProviderError("Provider returned a non-object response")
        return result
    except urllib.error.HTTPError as exc:
        # Do not surface provider bodies: errors can echo request or credential details.
        raise ProviderError(f"{provider}: HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise ProviderError(f"{provider}: {type(exc).__name__}") from None


@dataclass
class Call:
    id: str
    name: str
    arguments: object


@dataclass
class Turn:
    raw: dict
    calls: list[Call]
    text: str
    input_tokens: int
    output_tokens: int


class NativeAgent:
    def __init__(self, provider: str, model: str, *, max_output_tokens: int = 768):
        if provider not in {"openai", "anthropic"}:
            raise ValueError("Unknown provider")
        self.provider, self.model = provider, model
        self.max_output_tokens = max_output_tokens
        self.history: list[dict] = [{"role": "user", "content": TASK_PROMPT}]

    def step(self) -> Turn:
        if len(json.dumps(self.history).encode()) > 80_000:
            raise ProviderError("Input history byte budget exceeded")
        if self.provider == "openai":
            raw = request_json("openai", "/responses", {
                "model": self.model, "instructions": SYSTEM_PROMPT,
                "input": self.history, "max_output_tokens": self.max_output_tokens,
                "store": False, "include": ["reasoning.encrypted_content"],
                "parallel_tool_calls": False,
                "tools": [{"type": "function", "name": "lab_request",
                           "description": TOOL_DESCRIPTION, "parameters": TOOL_PARAMETERS,
                           "strict": True}],
            })
            if "output" not in raw:
                raise ProviderError("OpenAI response missing output")
            self.history.extend(raw["output"])
            calls = []
            for item in raw["output"]:
                if item["type"] == "function_call":
                    try:
                        arguments = json.loads(item["arguments"])
                    except (ValueError, TypeError, RecursionError):
                        arguments = None
                    calls.append(Call(item["call_id"], item["name"], arguments))
            text = "\n".join(part.get("text", "") for item in raw["output"]
                             if item["type"] == "message" for part in item.get("content", []))
            usage = raw.get("usage") or {}
        else:
            raw = request_json("anthropic", "/messages", {
                "model": self.model, "system": SYSTEM_PROMPT, "messages": self.history,
                "max_tokens": self.max_output_tokens,
                "tools": [{"name": "lab_request", "description": TOOL_DESCRIPTION,
                           "input_schema": TOOL_PARAMETERS}],
            })
            if "content" not in raw:
                raise ProviderError("Anthropic response missing content")
            self.history.append({"role": "assistant", "content": raw["content"]})
            calls = [Call(c["id"], c["name"], c["input"]) for c in raw["content"]
                     if c["type"] == "tool_use"]
            text = "\n".join(c["text"] for c in raw["content"] if c["type"] == "text")
            usage = raw.get("usage", {})
        return Turn(raw, calls, text, usage.get("input_tokens", 0), usage.get("output_tokens", 0))

    def results(self, results: list[tuple[Call, dict]]) -> None:
        if self.provider == "openai":
            self.history.extend({"type": "function_call_output", "call_id": call.id,
                                 "output": json.dumps(response)} for call, response in results)
        else:
            self.history.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": call.id, "content": json.dumps(response)}
                for call, response in results
            ]})
