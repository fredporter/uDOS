"""
Anchor validation helpers (Core).
"""

from __future__ import annotations

import re
from typing import Optional


ANCHOR_PATTERN = re.compile(r"^(EARTH|SKY|GAME:[A-Z0-9_\\-]+|BODY:[A-Z0-9_\\-]+|CATALOG:[A-Z0-9_\\-]+)$", re.I)
LOCID_PATTERN = re.compile(r"^([A-Z0-9:_]+):(SUR|SUB|UDN):L(\\d{3})-([A-Z0-9]{4})$", re.I)


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
    return True
