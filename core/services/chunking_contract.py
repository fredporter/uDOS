"""Chunking contract helpers for v1.3.20 grid runtime readiness.

Defines a deterministic 2D chunk id from PlaceRef/LocId while reserving
z-aware shape expansion for future 3D adapters.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

_LOCID_RE = re.compile(r"^L(?P<layer>\d{3})-(?P<cell>[A-Z]{2}\d{2})(?:-Z(?P<z>-?\d{1,2}))?$")


def _slug_anchor(anchor: str) -> str:
    return str(anchor or "earth").strip().lower().replace(":", "-")


def parse_place_ref(place_ref: str) -> Optional[Dict[str, Any]]:
    """Parse a PlaceRef token and extract chunk-relevant location fields.

    Accepts both canonical `ANCHOR:SPACE:L###-CC##[-Zz]` and extended forms
    with trailing instance suffixes (for example `...:L340-AA22-Z-3:D4`).
    """

    text = str(place_ref or "").strip()
    if not text:
        return None

    parts = [p.strip() for p in text.split(":") if p.strip()]
    if len(parts) < 3:
        return None

    loc_index = -1
    for idx, part in enumerate(parts):
        if _LOCID_RE.match(part):
            loc_index = idx
            break
    if loc_index <= 0:
        return None

    space = parts[loc_index - 1]
    anchor = ":".join(parts[: loc_index - 1])
    locid_token = parts[loc_index]

    match = _LOCID_RE.match(locid_token)
    if not match:
        return None

    layer = int(match.group("layer"))
    cell = match.group("cell")
    z_raw = match.group("z")
    z = int(z_raw) if z_raw is not None else 0
    col = cell[:2]
    row = int(cell[2:])

    return {
        "anchor": anchor,
        "space": space,
        "layer": layer,
        "cell": cell,
        "col": col,
        "row": row,
        "z": z,
        "canonical_locid": f"L{layer:03d}-{cell}" + (f"-Z{z}" if z != 0 else ""),
    }


def derive_chunk2d_id(place_ref: str) -> Optional[str]:
    """Return canonical 2D chunk id: `<anchor>-<space>-<layer>-<col>`."""

    parsed = parse_place_ref(place_ref)
    if not parsed:
        return None
    return f"{_slug_anchor(parsed['anchor'])}-{str(parsed['space']).lower()}-{parsed['layer']:03d}-{str(parsed['col']).lower()}"


def describe_chunk_shape(place_ref: str) -> Optional[Dict[str, Any]]:
    """Return 2D chunk contract plus reserved 3D extension metadata."""

    parsed = parse_place_ref(place_ref)
    if not parsed:
        return None
    chunk2d = derive_chunk2d_id(place_ref)
    return {
        "chunk2d_id": chunk2d,
        "coord2d": {
            "layer": parsed["layer"],
            "col": parsed["col"],
        },
        "reserved3d": {
            "z": parsed["z"],
            "shape": "extruded-column",
            "note": "Reserved for v1.3.21+ adapter chunk expansion",
        },
    }
