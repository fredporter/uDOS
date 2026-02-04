"""
Songscribe Parser
=================

Parse Songscribe markdown into structured data and helper render formats.
Pure-Python, no external dependencies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


META_KEYS = {"title", "tempo", "key", "mode", "loop"}


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\\s_-]", "", value)
    value = re.sub(r"[\\s_-]+", "-", value)
    return value.strip("-") or "track"


@dataclass
class SongscribeTrack:
    name: str
    steps: List[str] = field(default_factory=list)
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class SongscribeDocument:
    meta: Dict[str, object] = field(default_factory=dict)
    tracks: List[SongscribeTrack] = field(default_factory=list)


def parse_songscribe(text: str) -> SongscribeDocument:
    lines = [line.rstrip() for line in text.splitlines()]
    meta: Dict[str, object] = {}
    tracks: List[SongscribeTrack] = []
    current_track: Optional[SongscribeTrack] = None

    for line in lines:
        if not line.strip():
            continue

        if ":" in line and not line.strip().startswith("#"):
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()

            if key in META_KEYS:
                if key == "tempo":
                    try:
                        meta[key] = int(value)
                    except ValueError:
                        meta[key] = value
                else:
                    meta[key] = value
                continue

            if key == "track":
                current_track = SongscribeTrack(name=value)
                tracks.append(current_track)
                continue

            if key == "steps" and current_track is not None:
                current_track.steps = value.split()
                continue

            if current_track is not None:
                current_track.annotations[key] = value

    return SongscribeDocument(meta=meta, tracks=tracks)


def steps_to_events(steps: List[str]) -> List[Dict[str, object]]:
    events: List[Dict[str, object]] = []
    for idx, token in enumerate(steps):
        token = token.strip().lower()
        if not token:
            continue
        active = token != "0000"
        velocity = 0
        accent = 0
        if len(token) >= 2:
            try:
                velocity = int(token[:2], 16)
            except ValueError:
                velocity = 0
        if len(token) >= 4:
            try:
                accent = int(token[2:4], 16)
            except ValueError:
                accent = 0
        events.append(
            {
                "step": idx,
                "token": token,
                "active": active,
                "velocity": velocity,
                "accent": accent,
            }
        )
    return events


def to_groovebox_pattern(doc: SongscribeDocument) -> Dict[str, object]:
    title = str(doc.meta.get("title") or "Untitled")
    tempo = int(doc.meta.get("tempo") or 120)
    tracks = []
    for track in doc.tracks:
        events = steps_to_events(track.steps)
        steps = [
            {
                "active": e["active"],
                "velocity": e["velocity"] or 12,
                "accent": e["accent"] > 0,
            }
            for e in events
        ]
        tracks.append(
            {
                "id": _slugify(track.name),
                "name": track.name,
                "steps": steps,
                "annotations": track.annotations,
            }
        )
    return {
        "name": title,
        "tempo": tempo,
        "meta": doc.meta,
        "tracks": tracks,
    }


def to_ascii_grid(doc: SongscribeDocument, width: int = 16) -> str:
    lines: List[str] = []
    for track in doc.tracks:
        tokens = track.steps[:width]
        padded = tokens + ["0000"] * max(0, width - len(tokens))
        row = "".join(["#" if t.lower() != "0000" else "." for t in padded])
        name = track.name[:12].ljust(12)
        lines.append(f"{name} | {row}")
    return "\n".join(lines)
