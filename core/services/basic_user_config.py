"""
Basic User Config (Core)
========================

Minimal first-run capture for core TUI without admin token.
Stores values in memory/config/udos.md using $VAR: value format.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.locations import LocationService
from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("basic-user-config")

VAR_PATTERN = re.compile(r"^\$([A-Z_][A-Z0-9_]*)\s*:\s*(.*)$", re.MULTILINE)

REQUIRED_VARS = ["USER_NAME", "UDOS_TIMEZONE", "USER_TIME", "UDOS_LOCATION"]
MARKER_VAR = "FIRST_RUN_COMPLETE"


@dataclass
class LocationChoice:
    loc_id: str
    name: str
    timezone: str
    layer: Optional[int] = None
    cell: Optional[str] = None


def _config_path() -> Path:
    return get_repo_root() / "memory" / "config" / "udos.md"


def _timezone_dataset_path() -> Path:
    return get_repo_root() / "core" / "data" / "timezones.json"


def _load_timezone_dataset() -> Dict[str, Any]:
    path = _timezone_dataset_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _load_vars() -> Tuple[Dict[str, str], str]:
    path = _config_path()
    if not path.exists():
        return {}, ""
    content = path.read_text()
    vars_out: Dict[str, str] = {}
    for match in VAR_PATTERN.finditer(content):
        vars_out[match.group(1)] = match.group(2).strip()
    return vars_out, content


def _render_base() -> str:
    return "\n".join(
        [
            "# uDOS Configuration",
            "",
            "## Profile",
            "",
            "$USER_NAME:",
            "$UDOS_LOCATION:",
            "$UDOS_LOCATION_NAME:",
            "$UDOS_TIMEZONE: UTC",
            "$USER_TIME:",
            f"${MARKER_VAR}: false",
            "",
        ]
    )


def _upsert_var(content: str, name: str, value: str) -> str:
    pattern = re.compile(rf"^\\${name}\\s*:\\s*.*$", re.MULTILINE)
    line = f"${name}: {value}"
    if pattern.search(content):
        return pattern.sub(line, content)
    # Insert into Profile section if present
    profile_anchor = "## Profile"
    if profile_anchor in content:
        parts = content.split(profile_anchor)
        head = parts[0] + profile_anchor
        tail = profile_anchor.join(parts[1:])
        return "\n".join([head, "", line, tail.lstrip("\n")])
    return content.rstrip() + "\n" + line + "\n"


def save_vars(values: Dict[str, str]) -> None:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        content = path.read_text()
    else:
        content = _render_base()
    for key, value in values.items():
        content = _upsert_var(content, key, value)
    path.write_text(content)


def needs_first_run(vars_in: Dict[str, str]) -> bool:
    marker = vars_in.get(MARKER_VAR, "").lower()
    if marker not in ("true", "yes", "1", "on"):
        return True
    return any(not vars_in.get(name) for name in REQUIRED_VARS)


def _sanitize_username(value: str) -> Optional[str]:
    if not value:
        return None
    if re.match(r"^[A-Za-z0-9_-]+$", value):
        return value
    return None


def _default_timezone() -> str:
    try:
        tzinfo = datetime.now().astimezone().tzinfo
        if hasattr(tzinfo, "key") and tzinfo.key:
            return tzinfo.key
        return "UTC"
    except Exception:
        return "UTC"


def _validate_timezone(value: str) -> Optional[str]:
    if not value:
        return None
    try:
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(value)
        return getattr(tz, "key", value)
    except Exception:
        return None


def _format_time_now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _timezone_to_utc_hint(timezone_str: str) -> Optional[str]:
    if not timezone_str or timezone_str.upper().startswith("UTC"):
        return timezone_str
    try:
        from zoneinfo import ZoneInfo  # Python 3.9+

        tz = ZoneInfo(timezone_str)
        offset = datetime.now(tz).utcoffset()
        if offset is None:
            return None
        total_minutes = int(offset.total_seconds() / 60)
        sign = "+" if total_minutes >= 0 else "-"
        minutes = abs(total_minutes)
        hours = minutes // 60
        mins = minutes % 60
        if mins:
            return f"UTC{sign}{hours}:{mins:02d}"
        return f"UTC{sign}{hours}"
    except Exception:
        return None


def _search_locations(query: str, timezone_hint: Optional[str], limit: int = 5) -> List[LocationChoice]:
    service = LocationService()
    query_norm = (query or "").strip().lower()
    timezone_norm = (timezone_hint or "").strip().lower()
    matches: List[Tuple[int, LocationChoice]] = []
    for loc in service.get_all_locations():
        name = loc.get("name", "")
        loc_tz = str(loc.get("timezone", ""))
        if query_norm and query_norm not in name.lower():
            continue
        score = 0
        if query_norm and name.lower().startswith(query_norm):
            score += 2
        if timezone_norm and loc_tz.lower() == timezone_norm:
            score += 1
        choice = LocationChoice(
            loc_id=str(loc.get("id", "")),
            name=name,
            timezone=loc_tz,
            layer=loc.get("layer"),
            cell=loc.get("cell"),
        )
        matches.append((score, choice))
    matches.sort(key=lambda item: (-item[0], item[1].name))
    return [item[1] for item in matches[: max(1, limit)]]


def _default_location(timezone_hint: Optional[str]) -> Optional[LocationChoice]:
    results = _search_locations("", timezone_hint, limit=1)
    return results[0] if results else None


def _location_from_id(location_id: str) -> Optional[LocationChoice]:
    service = LocationService()
    loc = service.get_location(location_id)
    if not loc:
        return None
    return LocationChoice(
        loc_id=str(loc.get("id", "")),
        name=loc.get("name", location_id),
        timezone=str(loc.get("timezone", "UTC")),
        layer=loc.get("layer"),
        cell=loc.get("cell"),
    )


def ensure_basic_user_config(prompt_fn) -> bool:
    vars_in, _ = _load_vars()
    if not needs_first_run(vars_in):
        return False

    print("\nFirst-time setup: confirm basic user details.")
    print("These values are stored locally in memory/config/udos.md.\n")

    username = None
    while not username:
        raw = prompt_fn("Username (letters/numbers, no spaces): ").strip()
        username = _sanitize_username(raw)
        if not username:
            print("Please use only letters, numbers, underscore, or dash.")

    timezone_default = vars_in.get("UDOS_TIMEZONE") or _default_timezone()
    tz_dataset = _load_timezone_dataset()
    tz_names = sorted((tz_dataset.get("zones") or {}).keys())
    print(f"Detected timezone: {timezone_default}")
    tz_input = None
    while not tz_input:
        raw_tz = prompt_fn(
            f"Timezone (IANA) [{timezone_default}] (type '?' for examples): "
        ).strip()
        if raw_tz in ("?", "help", "examples"):
            examples = tz_names[:6] if tz_names else [
                "America/Los_Angeles",
                "Europe/London",
                "Asia/Tokyo",
                "UTC",
            ]
            print("Examples: " + ", ".join(examples))
            continue
        if raw_tz in ("current", "auto"):
            raw_tz = timezone_default
        candidate = raw_tz or timezone_default
        tz_input = _validate_timezone(candidate)
        if not tz_input:
            print("Please enter a valid IANA timezone (e.g., America/Los_Angeles).")
            continue
        if tz_names and tz_input not in tz_names:
            confirm = prompt_fn(
                "Timezone not in core dataset. Use anyway? [y/N]: "
            ).strip()
            if confirm.lower() not in ("y", "yes"):
                tz_input = None

    time_default = _format_time_now()
    time_input = prompt_fn(f"Local time now [{time_default}]: ").strip() or time_default

    tz_hint = tz_input
    default_loc = _default_location(tz_hint)
    if default_loc:
        suffix = f"L{default_loc.layer}-{default_loc.cell}" if default_loc.layer and default_loc.cell else default_loc.loc_id
        print(f"Default location for timezone: {default_loc.name} ({suffix})")
    query = prompt_fn("Location search (enter to accept default): ").strip()

    chosen_loc: Optional[LocationChoice] = None
    if not query and default_loc:
        chosen_loc = default_loc
    else:
        matches = _search_locations(query, tz_hint, limit=5)
        if matches:
            print("Select a location:")
            for idx, loc in enumerate(matches, start=1):
                code = f"L{loc.layer}-{loc.cell}" if loc.layer and loc.cell else loc.loc_id
                print(f"  {idx}. {loc.name} ({code}) [{loc.timezone}]")
            selection = prompt_fn("Choose number or enter grid id: ").strip()
            if selection.isdigit() and 1 <= int(selection) <= len(matches):
                chosen_loc = matches[int(selection) - 1]
            elif selection:
                matched = _location_from_id(selection)
                if matched:
                    chosen_loc = matched
                else:
                    print("Location must be a valid uDOS grid code from the list.")
        elif query:
            matched = _location_from_id(query)
            if matched:
                chosen_loc = matched
            else:
                print("Location must be a valid uDOS grid code from the list.")

    while chosen_loc is None:
        print("Please select a location from the uDOS list.")
        query = prompt_fn("Location search: ").strip()
        matches = _search_locations(query, tz_hint, limit=5) if query else _search_locations("", tz_hint, limit=5)
        if matches:
            print("Select a location:")
            for idx, loc in enumerate(matches, start=1):
                code = f"L{loc.layer}-{loc.cell}" if loc.layer and loc.cell else loc.loc_id
                print(f"  {idx}. {loc.name} ({code}) [{loc.timezone}]")
            selection = prompt_fn("Choose number or enter grid id: ").strip()
            if selection.isdigit() and 1 <= int(selection) <= len(matches):
                chosen_loc = matches[int(selection) - 1]
            else:
                matched = _location_from_id(selection)
                if matched:
                    chosen_loc = matched

    if not chosen_loc and default_loc:
        chosen_loc = default_loc

    location_id = chosen_loc.loc_id if chosen_loc else ""
    location_name = chosen_loc.name if chosen_loc else ""

    save_vars(
        {
            "USER_NAME": username,
            "UDOS_TIMEZONE": tz_input,
            "USER_TIME": time_input,
            "UDOS_LOCATION": location_id,
            "UDOS_LOCATION_NAME": location_name,
            MARKER_VAR: "true",
        }
    )
    print("Basic profile saved.\n")
    logger.info("[LOCAL] Basic user config captured")
    return True
