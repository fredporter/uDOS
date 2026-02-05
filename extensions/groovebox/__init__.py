"""Compatibility shim for `extensions.groovebox`.

Aliases to top-level `groovebox` module when available.
"""
from __future__ import annotations

import importlib
import sys

_groovebox = importlib.import_module("groovebox")
sys.modules[__name__] = _groovebox
