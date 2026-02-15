#!/usr/bin/env python3
"""Validate spatial seed catalogs (anchors + places) for v1.3.x contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Optional


ANCHOR_ID_RE = re.compile(
    r"^(EARTH|SKY|GAME:[A-Z0-9_\-]+|BODY:[A-Z0-9_\-]+|CATALOG:[A-Z0-9_\-]+)$",
    re.I,
)
PLACE_RE = re.compile(
    r"^(?P<anchor>(?:EARTH|SKY|GAME:[^:]+|BODY:[^:]+|CATALOG:[^:]+))"
    r":(?P<space>SUR|UDN|SUB)"
    r":L(?P<layer>\d{3})-(?P<cell>[A-Z]{2}\d{2})(?:-Z(?P<z>-?\d{1,2}))?"
    r"(?::D(?P<depth>\d+))?"
    r"(?::I(?P<instance>.+))?$",
    re.I,
)


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"failed to read JSON {path}: {exc}") from exc


def _validate_anchor_catalog(path: Path) -> set[str]:
    data = _load_json(path)
    anchors = data.get("anchors")
    if not isinstance(anchors, list):
        raise RuntimeError(f"{path}: anchors must be a list")

    seen: set[str] = set()
    for idx, item in enumerate(anchors):
        if not isinstance(item, dict):
            raise RuntimeError(f"{path}: anchors[{idx}] must be an object")
        anchor_id = str(item.get("anchorId", "")).strip()
        if not ANCHOR_ID_RE.match(anchor_id):
            raise RuntimeError(f"{path}: invalid anchorId at index {idx}: {anchor_id}")
        seen.add(anchor_id.upper())
        cfg = item.get("config", {})
        if cfg and not isinstance(cfg, dict):
            raise RuntimeError(f"{path}: anchor {anchor_id} config must be an object")
        z_axis = cfg.get("z_axis") if isinstance(cfg, dict) else None
        if z_axis is not None:
            if not isinstance(z_axis, dict):
                raise RuntimeError(f"{path}: anchor {anchor_id} z_axis must be an object")
            for key in ("supported", "min", "max", "default"):
                if key not in z_axis:
                    raise RuntimeError(f"{path}: anchor {anchor_id} z_axis missing key: {key}")
            if not isinstance(z_axis["supported"], bool):
                raise RuntimeError(f"{path}: anchor {anchor_id} z_axis.supported must be boolean")
    return seen


def _validate_place_ref(ref: str) -> tuple[str, str]:
    match = PLACE_RE.match(ref.strip())
    if not match:
        raise RuntimeError(f"invalid placeRef: {ref}")

    anchor = match.group("anchor")
    space = match.group("space").upper()
    layer = int(match.group("layer"))
    cell = match.group("cell").upper()
    z_raw = match.group("z")
    depth_raw = match.group("depth")

    if not (300 <= layer <= 899):
        raise RuntimeError(f"invalid placeRef layer ({layer}): {ref}")

    row = int(cell[2:4])
    if not (10 <= row <= 39):
        raise RuntimeError(f"invalid placeRef row ({row}): {ref}")

    if z_raw is not None:
        z = int(z_raw)
        if not (-99 <= z <= 99):
            raise RuntimeError(f"invalid placeRef z ({z}): {ref}")

    if depth_raw is not None:
        depth = int(depth_raw)
        if not (0 <= depth <= 99):
            raise RuntimeError(f"invalid placeRef depth ({depth}): {ref}")
        if space != "SUB":
            raise RuntimeError(f"depth tag requires SUB space: {ref}")

    return anchor.upper(), space


def _validate_places_catalog(path: Path, anchors_known: set[str]) -> None:
    data = _load_json(path)
    places = data.get("places")
    if not isinstance(places, list):
        raise RuntimeError(f"{path}: places must be a list")

    seen_place_ids: set[str] = set()
    for idx, item in enumerate(places):
        if not isinstance(item, dict):
            raise RuntimeError(f"{path}: places[{idx}] must be an object")
        place_id = str(item.get("placeId", "")).strip()
        if not place_id:
            raise RuntimeError(f"{path}: missing placeId at index {idx}")
        if place_id in seen_place_ids:
            raise RuntimeError(f"{path}: duplicate placeId: {place_id}")
        seen_place_ids.add(place_id)

        ref = str(item.get("placeRef", "")).strip()
        if not ref:
            raise RuntimeError(f"{path}: missing placeRef for placeId={place_id}")

        anchor, _space = _validate_place_ref(ref)
        if anchor not in anchors_known:
            raise RuntimeError(
                f"{path}: placeRef anchor not found in anchors catalog: {ref}"
            )

        for key in ("z", "z_min", "z_max"):
            if key in item and item[key] is not None:
                if not isinstance(item[key], int):
                    raise RuntimeError(f"{path}: {place_id} field {key} must be an integer")
                if item[key] < -99 or item[key] > 99:
                    raise RuntimeError(f"{path}: {place_id} field {key} out of range (-99..99)")

        if (
            isinstance(item.get("z_min"), int)
            and isinstance(item.get("z_max"), int)
            and item["z_min"] > item["z_max"]
        ):
            raise RuntimeError(f"{path}: {place_id} has z_min > z_max")

        for key in (
            "links",
            "portals",
            "stairs",
            "ramps",
            "quest_ids",
            "npc_spawn",
            "hazards",
            "loot_tables",
            "interaction_points",
        ):
            if key in item and not isinstance(item[key], list):
                raise RuntimeError(f"{path}: {place_id} field {key} must be a list")

        if "metadata" in item and not isinstance(item["metadata"], dict):
            raise RuntimeError(f"{path}: {place_id} field metadata must be an object")


def _validate_locations_seed(
    path: Path,
    anchors_known: set[str],
    known_places: Optional[Dict[str, str]] = None,
) -> None:
    data = _load_json(path)
    locations = data.get("locations")
    if not isinstance(locations, list):
        raise RuntimeError(f"{path}: locations must be a list")
    if len(locations) < 8:
        raise RuntimeError(f"{path}: expected at least 8 gameplay-ready locations")

    seen_ids: set[str] = set()
    links_by_place: Dict[str, list[str]] = {}
    catalog_ids = set((known_places or {}).keys())
    for idx, item in enumerate(locations):
        if not isinstance(item, dict):
            raise RuntimeError(f"{path}: locations[{idx}] must be an object")
        place_id = str(item.get("placeId", "")).strip()
        if not place_id:
            raise RuntimeError(f"{path}: missing placeId at index {idx}")
        if place_id in seen_ids:
            raise RuntimeError(f"{path}: duplicate placeId: {place_id}")
        seen_ids.add(place_id)

        ref = str(item.get("placeRef", "")).strip()
        if not ref:
            raise RuntimeError(f"{path}: missing placeRef for placeId={place_id}")
        anchor, _space = _validate_place_ref(ref)
        if anchor not in anchors_known:
            raise RuntimeError(f"{path}: unknown anchor in placeRef: {ref}")

        if known_places and place_id in known_places and known_places[place_id] != ref:
            raise RuntimeError(
                f"{path}: placeRef mismatch for placeId={place_id} "
                f"(seed={ref}, places.default={known_places[place_id]})"
            )

        for key in (
            "links",
            "stairs",
            "ramps",
            "portals",
            "quest_ids",
            "npc_spawn",
            "hazards",
            "loot_tables",
            "interaction_points",
        ):
            if key in item and not isinstance(item[key], list):
                raise RuntimeError(f"{path}: {place_id} field {key} must be a list")
        if "metadata" in item and not isinstance(item["metadata"], dict):
            raise RuntimeError(f"{path}: {place_id} field metadata must be an object")
        for key in ("z", "z_min", "z_max"):
            if key not in item:
                raise RuntimeError(f"{path}: {place_id} missing required field {key}")
            if not isinstance(item[key], int):
                raise RuntimeError(f"{path}: {place_id} field {key} must be an integer")
            if item[key] < -99 or item[key] > 99:
                raise RuntimeError(f"{path}: {place_id} field {key} out of range (-99..99)")
        if item["z_min"] > item["z_max"]:
            raise RuntimeError(f"{path}: {place_id} has z_min > z_max")
        if not isinstance(item.get("links"), list) or len(item["links"]) == 0:
            raise RuntimeError(f"{path}: {place_id} must define at least one link")
        if not isinstance(item.get("quest_ids"), list) or len(item["quest_ids"]) == 0:
            raise RuntimeError(f"{path}: {place_id} must define at least one quest_id")
        if not isinstance(item.get("interaction_points"), list) or len(item["interaction_points"]) == 0:
            raise RuntimeError(f"{path}: {place_id} must define at least one interaction_point")
        links_by_place[place_id] = [
            str(link).strip()
            for link in item.get("links", [])
            if isinstance(link, str) and str(link).strip()
        ]

    known_ids = seen_ids | catalog_ids
    for place_id, links in links_by_place.items():
        for target in links:
            if target == place_id:
                raise RuntimeError(f"{path}: {place_id} links cannot include itself")
            if target not in known_ids:
                raise RuntimeError(f"{path}: {place_id} links target unknown placeId: {target}")

    for place_id, links in links_by_place.items():
        for target in links:
            reverse_links = links_by_place.get(target, [])
            if place_id not in reverse_links:
                raise RuntimeError(
                    f"{path}: non-reciprocal links between {place_id} and {target}"
                )


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    tracked_anchors_path = repo / "core" / "src" / "spatial" / "anchors.default.json"
    tracked_places_path = repo / "core" / "src" / "spatial" / "places.default.json"
    tracked_locations_seed_path = repo / "core" / "src" / "spatial" / "locations-seed.default.json"
    memory_anchors_path = repo / "memory" / "spatial" / "anchors.json"
    memory_places_path = repo / "memory" / "spatial" / "places.json"

    if not tracked_anchors_path.exists():
        raise SystemExit(f"[spatial-seed-catalog] FAIL: missing {tracked_anchors_path}")
    if not tracked_places_path.exists():
        raise SystemExit(f"[spatial-seed-catalog] FAIL: missing {tracked_places_path}")
    if not tracked_locations_seed_path.exists():
        raise SystemExit(f"[spatial-seed-catalog] FAIL: missing {tracked_locations_seed_path}")

    known_anchors = _validate_anchor_catalog(tracked_anchors_path)
    _validate_places_catalog(tracked_places_path, known_anchors)
    places_payload = _load_json(tracked_places_path)
    known_places = {
        str(item.get("placeId", "")).strip(): str(item.get("placeRef", "")).strip()
        for item in places_payload.get("places", [])
        if isinstance(item, dict)
    }
    _validate_locations_seed(tracked_locations_seed_path, known_anchors, known_places)
    if memory_anchors_path.exists():
        known_anchors |= _validate_anchor_catalog(memory_anchors_path)
    if memory_places_path.exists():
        _validate_places_catalog(memory_places_path, known_anchors)

    print("[spatial-seed-catalog] PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"[spatial-seed-catalog] FAIL: {exc}")
        raise SystemExit(1)
