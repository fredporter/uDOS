"""Compatibility shim for legacy `commands.*` imports.

Aliases `commands` to `core.commands` so older tests/modules keep working.
"""
from __future__ import annotations

import importlib
import sys

_core_commands = importlib.import_module("core.commands")
sys.modules[__name__] = _core_commands
