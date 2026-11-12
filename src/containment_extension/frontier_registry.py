"""Exact model IDs verified against provider documentation on 2026-11-12.

No automatic model substitution. Rates are uncached USD per million tokens.
Terra: https://developers.openai.com/api/docs/models/gpt-6.1-terra
Opus: https://platform.claude.com/docs/en/models/opus-5-5/overview
"""
from copy import deepcopy
from .sabench_study import MODELS as ORIGINAL_MODELS, RATES as ORIGINAL_RATES

MODELS = deepcopy(ORIGINAL_MODELS)
MODELS.update({
    "terra": {"provider": "openai", "model": "gpt-6.1-terra",
              "request_extra": {"reasoning": {"effort": "high"}}},
    "opus": {"provider": "anthropic", "model": "claude-opus-5-5",
             "request_extra": {"thinking": {"type": "adaptive"},
                               "output_config": {"effort": "high"},
                               "tool_choice": {"type": "auto", "disable_parallel_tool_use": True}}},
})
RATES = {**deepcopy(ORIGINAL_RATES), "gpt-6.1-terra": {"input": 1., "output": 5.},
         "claude-opus-5-5": {"input": 4., "output": 20.}}
