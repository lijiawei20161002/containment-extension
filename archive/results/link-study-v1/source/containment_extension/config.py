"""Configuration loading. Never source .env as executable shell code."""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path


def load_env(path: Path | None) -> None:
    """Load simple dotenv assignments without expansion; existing env wins."""
    if path is None:
        return
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)", line)
        if match is None:
            raise ValueError(f"Invalid dotenv assignment at line {number}")
        name, raw = match.groups()
        try:
            parts = shlex.split(raw, comments=True, posix=True)
        except ValueError:
            raise ValueError(f"Invalid dotenv quoting at line {number}") from None
        if len(parts) > 1:
            raise ValueError(f"Quote values containing spaces at dotenv line {number}")
        os.environ.setdefault(name, parts[0] if parts else "")


def secret(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise ValueError(f"Set {name} in the environment or pass --env-file")
    return value
