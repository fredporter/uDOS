"""AI Profile scaffold service for local Ollama prompt standards and skills."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from wizard.services.path_utils import get_memory_dir, get_repo_root


def _template_path() -> Path:
    return get_repo_root() / "wizard" / "config" / "templates" / "ai_profile_template.json"


def _profile_path() -> Path:
    return get_memory_dir() / "wizard" / "ai-profile.json"


def _knowledge_library_path() -> Path:
    return get_repo_root() / "knowledge" / "local" / "library.json"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge_dict(out[key], value)
        else:
            out[key] = value
    return out


def load_template() -> Dict[str, Any]:
    template = _read_json(_template_path())
    if template:
        return template
    return {
        "schema_version": "1.3",
        "profile_name": "uDOS Local AI Profile",
        "standards": [],
        "mission_objectives": [],
        "local_ollama": {},
        "custom_instructions": {"global": [], "general": [], "coding": []},
        "local_skills": [],
        "user_quests": [],
        "knowledge_library": [],
    }


def load_profile() -> Dict[str, Any]:
    template = load_template()
    saved = _read_json(_profile_path())
    profile = _merge_dict(template, saved)
    profile.setdefault("updated_at", datetime.utcnow().isoformat())
    return profile


def save_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    current = load_profile()
    merged = _merge_dict(current, profile or {})
    merged["updated_at"] = datetime.utcnow().isoformat()
    _write_json(_profile_path(), merged)
    return merged


def _append_unique_dict(items: List[Dict[str, Any]], entry: Dict[str, Any], key: str = "id") -> List[Dict[str, Any]]:
    if not isinstance(entry, dict):
        return items
    entry_id = str(entry.get(key) or "").strip()
    if entry_id:
        items = [item for item in items if str(item.get(key) or "") != entry_id]
    items.append(entry)
    return items


def add_quest(quest: Dict[str, Any]) -> Dict[str, Any]:
    profile = load_profile()
    quests = profile.get("user_quests")
    if not isinstance(quests, list):
        quests = []
    profile["user_quests"] = _append_unique_dict(quests, quest)
    return save_profile(profile)


def add_skill(skill: Dict[str, Any]) -> Dict[str, Any]:
    profile = load_profile()
    skills = profile.get("local_skills")
    if not isinstance(skills, list):
        skills = []
    profile["local_skills"] = _append_unique_dict(skills, skill)
    return save_profile(profile)


def add_knowledge_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    profile = load_profile()
    entries = profile.get("knowledge_library")
    if not isinstance(entries, list):
        entries = []
    updated_entries = _append_unique_dict(entries, entry)
    profile["knowledge_library"] = updated_entries
    saved = save_profile(profile)

    _write_json(_knowledge_library_path(), {"entries": updated_entries, "updated_at": saved.get("updated_at")})
    return saved


def render_system_prompt(mode: str = "general") -> str:
    profile = load_profile()
    mode_key = "coding" if mode == "coding" else "general"

    standards = profile.get("standards") or []
    missions = profile.get("mission_objectives") or []
    custom = profile.get("custom_instructions") or {}
    global_instructions = custom.get("global") or []
    mode_instructions = custom.get(mode_key) or []
    skills = [s for s in (profile.get("local_skills") or []) if s.get("enabled", True)]

    lines: List[str] = [
        "uDOS Mission Profile",
        "Follow these operating standards and mission objectives.",
    ]

    if standards:
        lines.append("Standards:")
        lines.extend([f"- {item}" for item in standards if item])

    if missions:
        lines.append("Mission Objectives:")
        lines.extend([f"- {item}" for item in missions if item])

    if global_instructions:
        lines.append("Global Instructions:")
        lines.extend([f"- {item}" for item in global_instructions if item])

    if mode_instructions:
        lines.append(f"{mode_key.title()} Instructions:")
        lines.extend([f"- {item}" for item in mode_instructions if item])

    if skills:
        lines.append("Local Skills:")
        for skill in skills:
            name = skill.get("name") or skill.get("id") or "skill"
            instruction = skill.get("instructions") or ""
            lines.append(f"- {name}: {instruction}".strip())

    return "\n".join(lines)
