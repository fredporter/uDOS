"""
Deterministic offline logic primitives for the v1.5 runtime.

This package is the first promoted `core/ulogic` slice from the
`docs/examples/udos_ulogic_pack/` reference scaffold.
"""

from .contracts import IntentFrame, RoutingOutcome
from .parser import parse_input, parse_primary_input

__all__ = [
    "IntentFrame",
    "RoutingOutcome",
    "parse_input",
    "parse_primary_input",
]
