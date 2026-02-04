"""Compatibility shim for legacy `tui.*` imports.

Aliases `tui` to `core.tui` so older tests/modules keep working.
"""
from __future__ import annotations

import importlib
import sys

_core_tui = importlib.import_module("core.tui")
sys.modules[__name__] = _core_tui
