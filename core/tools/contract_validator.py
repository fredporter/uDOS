"""
Contract Validator (Core)

Validates Vault Contract, Theme Pack Contract, and Engine-Agnostic World Contract.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


REQUIRED_THEME_SLOTS = ["{{content}}", "{{title}}", "{{nav}}", "{{meta}}", "{{footer}}"]
DEFAULT_SKIP_DIRS = {".git", ".archive", "node_modules", ".venv", ".venv-mcp", "_site"}


@dataclass
class ContractReport:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


def _report(errors: List[str], warnings: Optional[List[str]] = None, details: Optional[Dict[str, Any]] = None) -> ContractReport:
    warnings = warnings or []
    details = details or {}
    return ContractReport(valid=len(errors) == 0, errors=errors, warnings=warnings, details=details)


def _iter_files(root: Path, suffix: Optional[str] = None) -> Iterable[Path]:
    if not root.exists():
        return []
    for dirpath, dirnames, filenames in __import__("os").walk(root):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_SKIP_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if suffix and path.suffix.lower() != suffix:
                continue
            yield path


def validate_vault_contract(vault_dir: Path) -> ContractReport:
    errors: List[str] = []
    warnings: List[str] = []

    if not vault_dir.exists():
        return _report([f"Vault path not found: {vault_dir}"])

    markdown_files = [p for p in _iter_files(vault_dir, ".md")]
    if not markdown_files:
        errors.append("Markdown files not found in vault")

    # Recommended folders (warn only)
    recommended = [
        vault_dir / "01_KNOWLEDGE",
        vault_dir / "02_PROJECTS",
        vault_dir / "03_PROMPTS",
        vault_dir / "04_TASKS",
        vault_dir / "05_DATA" / "sqlite",
        vault_dir / "06_RUNS",
        vault_dir / "07_LOGS",
        vault_dir / "_templates",
    ]
    missing = [str(p) for p in recommended if not p.exists()]
    if missing:
        warnings.append(f"Recommended vault folders missing: {', '.join(missing)}")

    return _report(errors, warnings, {"markdown_count": len(markdown_files)})


def validate_theme_pack(theme_dir: Path) -> ContractReport:
    errors: List[str] = []
    warnings: List[str] = []

    if not theme_dir.exists():
        return _report([f"Theme pack path not found: {theme_dir}"])

    shell_path = theme_dir / "shell.html"
    css_path = theme_dir / "theme.css"
    json_path = theme_dir / "theme.json"
    assets_path = theme_dir / "assets"

    if not shell_path.exists():
        errors.append("Missing shell.html")
    if not css_path.exists():
        errors.append("Missing theme.css")
    if not json_path.exists():
        errors.append("Missing theme.json")
    if not assets_path.exists():
        warnings.append("Missing assets/ directory")

    shell_content = ""
    if shell_path.exists():
        shell_content = shell_path.read_text(encoding="utf-8", errors="ignore")

    theme_meta: Dict[str, Any] = {}
    if json_path.exists():
        try:
            theme_meta = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"theme.json is invalid JSON: {exc}")

    if theme_meta:
        if not theme_meta.get("name") and not theme_meta.get("id"):
            errors.append("theme.json missing required field: name or id")
        if "mode" not in theme_meta:
            warnings.append("theme.json missing optional field: mode")

        slots = theme_meta.get("slots")
        if slots and isinstance(slots, list):
            missing_slots = [slot for slot in REQUIRED_THEME_SLOTS if slot not in slots]
            if missing_slots:
                errors.append(f"theme.json slots missing: {', '.join(missing_slots)}")

    if shell_content:
        missing_slots = [slot for slot in REQUIRED_THEME_SLOTS if slot not in shell_content]
        if missing_slots:
            errors.append(f"shell.html missing slots: {', '.join(missing_slots)}")

    return _report(errors, warnings, {"theme": theme_meta.get("name") or theme_meta.get("id")})


LOCID_PATTERN = re.compile(r"[A-Z0-9:_]+:L\d{3}-[A-Z]{2}\d{2}(?:-Z-?\d+)?")
GRID_PATTERN = re.compile(r"\bL\d{3}-[A-Z]{2}\d{2}(?:-Z-?\d+)?\b")


def _parse_locid(token: str) -> Optional[Dict[str, Any]]:
    parts = token.split(":")
    if len(parts) < 3:
        return None
    space = parts[-2]
    anchor = ":".join(parts[:-2])
    layer_cell = parts[-1]
    match = re.match(r"^L(\d{3})-([A-Z]{2}\d{2})(?:-Z(-?\d{1,2}))?$", layer_cell)
    if not match:
        return None
    layer = int(match.group(1))
    cell = match.group(2)
    z = int(match.group(3)) if match.group(3) is not None else None
    return {"anchor": anchor, "space": space, "layer": layer, "cell": cell, "z": z}


def _is_valid_locid(token: str) -> bool:
    parsed = _parse_locid(token)
    if not parsed:
        return False
    if parsed["space"] not in {"SUR", "SUB", "UDN"}:
        return False
    if not parsed["anchor"]:
        return False
    if not re.match(r"^[A-Z0-9:_]+$", parsed["anchor"]):
        return False
    if not (300 <= parsed["layer"] <= 899):
        return False
    if not re.match(r"^[A-Z]{2}\d{2}$", parsed["cell"]):
        return False
    row = int(parsed["cell"][2:4])
    if not (10 <= row <= 39):
        return False
    if parsed["z"] is not None and not (-99 <= parsed["z"] <= 99):
        return False
    return True


def validate_world_contract(vault_dir: Path) -> ContractReport:
    errors: List[str] = []
    warnings: List[str] = []
    invalid_locids: List[str] = []

    if not vault_dir.exists():
        return _report([f"Vault path not found: {vault_dir}"])

    markdown_files = list(_iter_files(vault_dir, ".md"))
    for path in markdown_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in LOCID_PATTERN.findall(text):
            if not _is_valid_locid(match):
                invalid_locids.append(match)
        for match in GRID_PATTERN.findall(text):
            parsed = _parse_locid(f"EARTH:SUR:{match}")
            if not parsed:
                invalid_locids.append(match)
                continue
            if not _is_valid_locid(f"EARTH:SUR:{match}"):
                invalid_locids.append(match)

    if invalid_locids:
        errors.append("Invalid LocId tokens found")

    return _report(errors, warnings, {"invalid_locids": sorted(set(invalid_locids))})
