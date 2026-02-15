"""
Anchor validation helpers (Core).
"""

from __future__ import annotations

import re
from typing import Optional


ANCHOR_PATTERN = re.compile(r"^(EARTH|SKY|GAME:[A-Z0-9_\\-]+|BODY:[A-Z0-9_\\-]+|CATALOG:[A-Z0-9_\\-]+)$", re.I)
LOCID_PATTERN = re.compile(
    r"^([A-Z0-9:_]+):(SUR|SUB|UDN):L(\d{3})-([A-Z]{2}\d{2})(?:-Z(-?\d{1,2}))?$",
    re.I,
)


def is_valid_anchor_id(anchor_id: Optional[str]) -> bool:
    if not anchor_id:
        return False
    return bool(ANCHOR_PATTERN.match(anchor_id.strip()))


def is_valid_locid(locid: Optional[str]) -> bool:
    if not locid:
        return False
    match = LOCID_PATTERN.match(locid.strip())
    if not match:
        return False
    layer = int(match.group(3))
    if not (300 <= layer <= 899):
        return False
    row = int(match.group(4)[2:4])
    if not (10 <= row <= 39):
        return False
    z_raw = match.group(5)
    if z_raw is not None:
        z = int(z_raw)
        if not (-99 <= z <= 99):
            return False
    return True
