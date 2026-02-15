"""Spatial parsing helpers (Python mirror of v1-3/core/src/spatial)."""
import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml

CELL_REGEX = re.compile(r"^[A-Z]{2}\d{2}$")
LOCID_REGEX = re.compile(r"^L(\d{3})-([A-Z]{2}\d{2})(?:-Z(-?\d{1,2}))?$")


def is_valid_row(row: int) -> bool:
    return 10 <= row <= 39


def is_valid_cell(cell: str) -> bool:
    if not CELL_REGEX.match(cell):
        return False
    row = int(cell[2:4])
    return is_valid_row(row)


def is_valid_z(z: int) -> bool:
    return -99 <= z <= 99


def parse_locid(locid: str) -> Optional[str]:
    match = LOCID_REGEX.match(locid)
    if not match:
        return None
    layer = int(match.group(1))
    cell = match.group(2)
    z = int(match.group(3)) if match.group(3) is not None else None
    if layer < 300 or layer > 899:
        return None
    if not is_valid_cell(cell):
        return None
    if z is not None and not is_valid_z(z):
        return None
    return locid


def parse_place_ref(ref: str) -> Optional[Dict[str, Optional[str]]]:
    parts = ref.split(":")
    if len(parts) < 3:
        return None

    anchor_id = parts[0]
    idx = 1
    if anchor_id in {"BODY", "GAME", "CATALOG"}:
        if len(parts) < 4:
            return None
        anchor_id = f"{parts[0]}:{parts[1]}"
        idx = 2

    if idx + 1 >= len(parts):
        return None

    space = parts[idx]
    if space not in {"SUR", "UDN", "SUB"}:
        return None

    locid = parts[idx + 1]
    if not parse_locid(locid):
        return None

    depth: Optional[int] = None
    instance: Optional[str] = None
    for token in parts[idx + 2 :]:
        if token.startswith("D") and token[1:].isdigit():
            depth = int(token[1:])
        elif token.startswith("I"):
            instance = token[1:]

    return {
        "anchor_id": anchor_id,
        "space": space,
        "loc_id": locid,
        "depth": depth,
        "instance": instance,
    }


def normalise_frontmatter_places(fm: Dict[str, List[str]]) -> List[str]:
    seen = []
    places = fm.get("places") or []
    grid_locations = fm.get("grid_locations") or []

    for place in places:
        parsed = parse_place_ref(place)
        if parsed:
            canonical = build_place_ref(parsed)
            if canonical not in seen:
                seen.append(canonical)

    for loc in grid_locations:
        canonical = parse_locid(loc)
        if canonical:
            canonical_ref = f"EARTH:SUR:{canonical}"
            if canonical_ref not in seen:
                seen.append(canonical_ref)

    return seen


def build_place_ref(parsed: Dict[str, Optional[str]]) -> str:
    parts = [parsed["anchor_id"], parsed["space"], parsed["loc_id"]]
    if parsed.get("depth") is not None:
        parts.append(f"D{parsed['depth']}")
    if parsed.get("instance"):
        parts.append(f"I{parsed['instance']}")
    return ":".join(parts)


def extract_frontmatter(file_path: Path) -> Optional[Dict[str, List[str]]]:
    try:
        text = file_path.read_text()
    except OSError:
        return None

    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end == -1:
        return None
    raw = text[3:end]
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None
    if isinstance(data, dict):
        return {
            "places": data.get("places") or [],
            "grid_locations": data.get("grid_locations") or [],
        }
    return None


def scan_vault_places(vault_root: Path) -> List[Dict[str, Optional[List[str]]]]:
    notes_root = vault_root / "notes"
    results: List[Dict[str, Optional[List[str]]]] = []
    if not notes_root.exists():
        return results

    for md in sorted(notes_root.rglob("*.md")):
        fm = extract_frontmatter(md)
        if not fm:
            continue
        places = normalise_frontmatter_places(fm)
        if places:
            results.append({
                "file": md.relative_to(vault_root).as_posix(),
                "places": places,
            })
    return results
