#!/usr/bin/env python3
"""Enforce the active core stdlib contract used by the runtime."""

from __future__ import annotations

from scripts.check_core_stdlib_contract import main as run_core_stdlib_contract


def main() -> int:
    return run_core_stdlib_contract()


if __name__ == "__main__":
    raise SystemExit(main())
