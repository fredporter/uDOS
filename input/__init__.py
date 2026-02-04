"""Compatibility shim for legacy `input.*` imports.

Aliases `input` to `core.input` so older tests/modules keep working.
"""
from __future__ import annotations

import importlib
import sys

_core_input = importlib.import_module("core.input")
sys.modules[__name__] = _core_input
