"""Thread-safe request and estimated-cost guard for explicitly bounded studies."""

import json
from threading import Lock


class BudgetStop(RuntimeError):
    pass


class StudyBudget:
    def __init__(self, *, max_requests: int, max_estimated_usd: float, rates: dict,
                 max_input_tokens: int | None = None, max_output_tokens: int | None = None):
        self.max_requests = max_requests
        self.max_estimated_usd = max_estimated_usd
        self.rates = rates
        self.lock = Lock()
        self.requests = 0
        self.input_tokens = self.output_tokens = 0
        self.estimated_usd = self.reserved_usd = 0.0
        self.unknown_usage_requests = 0
        self.max_input_tokens, self.max_output_tokens = max_input_tokens, max_output_tokens
        self.reserved_input = self.reserved_output = 0
        self.unknown_input = self.unknown_output = 0

    def call(self, transport, provider: str, path: str, payload: dict) -> dict:
        rate = self.rates[payload["model"]]
        # Serialized UTF-8 bytes + overhead are a deliberately conservative
        # reservation, not an exact tokenizer or a provider billing guarantee.
        reserve_input = len(json.dumps(payload).encode()) + 8192
        reserve_output = payload.get("max_output_tokens", payload.get("max_tokens", 0))
        reserve = (reserve_input * rate["input"] + reserve_output * rate["output"]) / 1e6
        with self.lock:
            if self.requests >= self.max_requests:
                raise BudgetStop("Study request ceiling reached")
            if self.estimated_usd + self.reserved_usd + reserve > self.max_estimated_usd:
                raise BudgetStop("Study estimated-cost reservation ceiling reached")
            if (self.max_input_tokens is not None and self.input_tokens + self.unknown_input
                    + self.reserved_input + reserve_input > self.max_input_tokens):
                raise BudgetStop("Study input-token reservation ceiling reached")
            if (self.max_output_tokens is not None and self.output_tokens + self.unknown_output
                    + self.reserved_output + reserve_output > self.max_output_tokens):
                raise BudgetStop("Study output-token reservation ceiling reached")
            self.requests += 1
            self.reserved_usd += reserve
            self.reserved_input += reserve_input
            self.reserved_output += reserve_output
        try:
            raw = transport(provider, path, payload)
            usage = raw.get("usage") or {}
            if "input_tokens" not in usage or "output_tokens" not in usage:
                raise ValueError("Missing provider token usage")
            inputs = usage["input_tokens"]
            if provider == "anthropic":
                inputs += usage.get("cache_read_input_tokens", 0)
                inputs += usage.get("cache_creation_input_tokens", 0)
            outputs = usage["output_tokens"]
            cost = (inputs * rate["input"] + outputs * rate["output"]) / 1e6
        except BaseException:
            # An interrupted/failed response may still have been charged.
            with self.lock:
                self.reserved_usd -= reserve
                self.estimated_usd += reserve
                self.unknown_usage_requests += 1
                self.reserved_input -= reserve_input
                self.reserved_output -= reserve_output
                self.unknown_input += reserve_input
                self.unknown_output += reserve_output
            raise
        with self.lock:
            self.reserved_usd -= reserve
            self.estimated_usd += cost
            self.input_tokens += inputs
            self.output_tokens += outputs
            self.reserved_input -= reserve_input
            self.reserved_output -= reserve_output
        return raw

    def snapshot(self) -> dict:
        with self.lock:
            return {"requests": self.requests, "input_tokens": self.input_tokens,
                    "output_tokens": self.output_tokens,
                    "estimated_usd": round(self.estimated_usd, 6),
                    "reserved_usd": round(self.reserved_usd, 6),
                    "unknown_usage_requests": self.unknown_usage_requests,
                    "max_requests": self.max_requests,
                    "max_estimated_usd": self.max_estimated_usd,
                    "max_input_tokens": self.max_input_tokens,
                    "max_output_tokens": self.max_output_tokens,
                    "reserved_input_tokens": self.reserved_input,
                    "reserved_output_tokens": self.reserved_output,
                    "unknown_input_token_reservations": self.unknown_input,
                    "unknown_output_token_reservations": self.unknown_output,
                    "note": "Uncached list-price estimate; not a billing statement. "
                            "Failed responses conservatively retain the request reservation."}
