import hashlib
import json
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
VAULT_ROOT = Path(os.getenv("VAULT_ROOT", "/workspace/vault"))
DB_CANDIDATES = [
    VAULT_ROOT / ".udos" / "state.db",
    VAULT_ROOT / "05_DATA" / "sqlite" / "udos.db",
]
SCHEMA_PATH = REPO_ROOT / "v1-3" / "core" / "src" / "spatial" / "schema.sql"
ANCHOR_REGISTRY = Path(REPO_ROOT / "memory" / "bank" / "spatial" / "anchors.json")
DEFAULT_ANCHOR_REGISTRY = REPO_ROOT / "v1-3" / "core" / "src" / "spatial" / "anchors.default.json"


def _parse_locid(locid: str) -> Optional[Dict[str, str]]:
    match = re.match(r"^L(\d{3})-([A-Z]{2}\d{2})$", locid)
    if not match:
        return None
    return {"loc_id": locid, "effective_layer": match.group(1), "final_cell": match.group(2)}


def _parse_place_ref(ref: str) -> Optional[Dict[str, Optional[str]]]:
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
    locid_part = parts[idx + 1]
    loc_meta = _parse_locid(locid_part)
    if not loc_meta:
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
        "loc_id": loc_meta["loc_id"],
        "effective_layer": int(loc_meta["effective_layer"]),
        "final_cell": loc_meta["final_cell"],
        "depth": depth,
        "instance": instance,
    }


def _resolve_db_path() -> Path:
    for candidate in DB_CANDIDATES:
        if candidate.exists():
            return candidate
    candidate = DB_CANDIDATES[0]
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return candidate


def _ensure_schema(conn: sqlite3.Connection) -> None:
    if not SCHEMA_PATH.exists():
        return
    script = SCHEMA_PATH.read_text()
    conn.executescript(script)


def _seed_anchors(conn: sqlite3.Connection) -> None:
    source = ANCHOR_REGISTRY if ANCHOR_REGISTRY.exists() else DEFAULT_ANCHOR_REGISTRY
    if not source.exists():
        return
    payload = json.loads(source.read_text())
    anchors = payload.get("anchors", [])
    now = int(time.time())
    cursor = conn.cursor()
    for anchor in anchors:
        anchor_id = anchor.get("anchorId")
        kind = anchor.get("kind", "earth")
        title = anchor.get("title", anchor_id)
        status = anchor.get("status", "active")
        config = anchor.get("config", {})
        cursor.execute(
            """
            INSERT INTO anchors(anchor_id, kind, title, status, config_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(anchor_id) DO UPDATE SET
              kind = excluded.kind,
              title = excluded.title,
              status = excluded.status,
              config_json = excluded.config_json,
              updated_at = excluded.updated_at
            """,
            (
                anchor_id,
                kind,
                title,
                status,
                json.dumps(config),
                now,
                now,
            ),
        )


def _ensure_locid(conn: sqlite3.Connection, loc_id: str, effective_layer: int, final_cell: str) -> None:
    now = int(time.time())
    conn.execute(
        """
        INSERT INTO locids(loc_id, effective_layer, final_cell, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(loc_id) DO UPDATE SET
          effective_layer = excluded.effective_layer,
          final_cell = excluded.final_cell
        """,
        (loc_id, effective_layer, final_cell, now),
    )


def _build_place_id(anchor_id: str, space: str, loc_id: str, depth: Optional[int], instance: Optional[str]) -> str:
    parts = [anchor_id, space, loc_id, str(depth) if depth is not None else "", instance or ""]
    hasher = hashlib.sha1(":".join(parts).encode("utf-8"))
    return hasher.hexdigest()


def _update_file_entry(conn: sqlite3.Connection, rel_path: str, full_path: Path) -> None:
    now = int(time.time())
    if not full_path.exists():
        return
    mtime = int(full_path.stat().st_mtime)
    digest = hashlib.sha256(full_path.read_bytes()).hexdigest()
    conn.execute(
        """
        INSERT INTO files(file_path, mtime, hash)
        VALUES (?, ?, ?)
        ON CONFLICT(file_path) DO UPDATE SET
          mtime = excluded.mtime,
          hash = excluded.hash
        """,
        (rel_path, mtime, digest),
    )


def sync_spatial_index(api_base: str) -> None:
    try:
        response = requests.get(f"{api_base.rstrip('/')}/api/renderer/places", timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        print("[mission-scheduler] Spatial sync failed:", exc)
        return

    items = payload.get("places", [])
    if not items:
        return

    db_path = _resolve_db_path()
    with sqlite3.connect(str(db_path)) as conn:
        _ensure_schema(conn)
        _seed_anchors(conn)
        now = int(time.time())
        cursor = conn.cursor()
        for entry in items:
            file_rel = entry.get("file")
            if not file_rel:
                continue

            full_path = VAULT_ROOT / file_rel
            _update_file_entry(conn, file_rel, full_path)

            seen_place_ids: List[str] = []
            for place_ref in entry.get("places", []):
                parsed = _parse_place_ref(place_ref)
                if not parsed:
                    continue
                place_id = _build_place_id(parsed["anchor_id"], parsed["space"], parsed["loc_id"], parsed["depth"], parsed["instance"])
                if place_id in seen_place_ids:
                    continue
                seen_place_ids.append(place_id)

                _ensure_locid(conn, parsed["loc_id"], parsed["effective_layer"], parsed["final_cell"])

                cursor.execute(
                    """
                    INSERT INTO places(place_id, anchor_id, space, loc_id, depth, instance, label, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(place_id) DO UPDATE SET
                      anchor_id = excluded.anchor_id,
                      space = excluded.space,
                      loc_id = excluded.loc_id,
                      depth = excluded.depth,
                      instance = excluded.instance,
                      label = excluded.label,
                      updated_at = excluded.updated_at
                    """,
                    (
                        place_id,
                        parsed["anchor_id"],
                        parsed["space"],
                        parsed["loc_id"],
                        parsed["depth"],
                        parsed["instance"],
                        None,
                        now,
                        now,
                    ),
                )

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO file_place_tags(file_path, place_id, source, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (file_rel, place_id, "frontmatter", now),
                )

        conn.commit()
