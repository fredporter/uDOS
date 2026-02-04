"""Compatibility shim for legacy `services.*` imports.

Aliases `services` to `core.services` so older tests/modules keep working.
"""
from __future__ import annotations

import importlib
import sys

_core_services = importlib.import_module("core.services")
sys.modules[__name__] = _core_services
