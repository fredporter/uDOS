"""
Contract Validator
==================

Validates:
- Vault Contract
- Theme Pack Contract
- Engine-Agnostic World Contract (LocId invariants)

Usage:
  python3 -m core.tools.contract_validator --vault vault --themes themes
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from core.services.logging_service import get_logger, get_repo_root

logger = get_logger("contract-validator")


PLACE_REF_RE = re.compile(
    r"\b([A-Z0-9_]+(?::[A-Z0-9_]+)?)"  # Anchor (optional composite)
    r":(SUR|UDN|SUB)"  # Space
    r":(L\d{3}-[A-Z]{2}\d{2})"  # LocId
    r"(?::(D\d+))?"  # Optional depth tag
    r"(?::(I[^\s:]+))?"  # Optional instance tag
    r"\b"
)

LOCID_RE = re.compile(r"\bL\d{3}-[A-Z]{2}\d{2}\b")

REQUIRED_SLOTS = {"{{content}}", "{{title}}", "{{nav}}", "{{meta}}", "{{footer}}"}
REQUIRED_SLOT_NAMES = {"content", "title", "nav", "meta", "footer"}
ALLOWED_THEME_MODES = {"article", "retro", "slides", "forms"}


@dataclass
class ValidationReport:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, object] = field(default_factory=dict)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.valid = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


def _iter_text_files(root: Path, extensions: Tuple[str, ...]) -> Iterable[Path]:
    if not root.exists():
        return []

    skip_dirs = {
        "_site",
        "06_RUNS",
        "07_LOGS",
        "05_DATA",
        ".udos",
        ".git",
        "node_modules",
        "dist",
        "build",
    }

    for path in root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in extensions:
            yield path


def _is_valid_cell(cell: str) -> bool:
    if not re.match(r"^[A-Z]{2}\d{2}$", cell):
        return False
    row = int(cell[2:4])
    return 10 <= row <= 39


def _parse_locid(locid: str) -> Optional[Tuple[int, str]]:
    match = re.match(r"^L(\d{3})-([A-Z]{2}\d{2})$", locid)
    if not match:
        return None
    layer = int(match.group(1))
    cell = match.group(2)
    if not _is_valid_cell(cell):
        return None
    if not (300 <= layer <= 899):
        return None
    return layer, cell


def validate_place_ref(place_ref: str) -> Optional[str]:
    parts = place_ref.split(":")
    if len(parts) < 3:
        return "PlaceRef must have at least 3 colon-separated parts"

    anchor = parts[0]
    idx = 1
    if anchor in {"BODY", "GAME", "CATALOG"}:
        if len(parts) < 4:
            return f"Composite anchor {anchor} requires subtype"
        anchor = f"{parts[0]}:{parts[1]}"
        idx = 2

    space = parts[idx]
    if space not in {"SUR", "UDN", "SUB"}:
        return f"Invalid space: {space}"

    locid = parts[idx + 1]
    if not _parse_locid(locid):
        return f"Invalid LocId: {locid}"

    for tag in parts[idx + 2 :]:
        if tag.startswith("D"):
            if not tag[1:].isdigit():
                return f"Invalid depth tag: {tag}"
            depth = int(tag[1:])
            if depth < 0 or depth > 99:
                return f"Depth {depth} out of range (0-99)"
        elif tag.startswith("I"):
            if len(tag) < 2:
                return "Instance tag I requires a value"
        else:
            return f"Unknown tag: {tag}"

    return None


def validate_vault_contract(vault_path: Path) -> ValidationReport:
    report = ValidationReport(valid=True)

    if not vault_path.exists() or not vault_path.is_dir():
        report.add_error(f"Vault path not found: {vault_path}")
        return report

    md_files = list(vault_path.rglob("*.md"))
    if not md_files:
        report.add_error("Vault contains no Markdown files")

    required_dirs = ["_site", "06_RUNS", "07_LOGS"]
    for d in required_dirs:
        if not (vault_path / d).exists():
            report.add_warning(f"Missing export slot directory: {d}")

    recommended_dirs = [
        "bank",
        "sandbox",
        "inbox-dropbox",
        "public-open-published",
        "private-explicit",
        "private-shared",
    ]
    for d in recommended_dirs:
        if not (vault_path / d).exists():
            report.add_warning(f"Missing recommended vault space: {d}")

    app_state_ok = False
    if (vault_path / ".udos").exists():
        app_state_ok = True
    if (vault_path / "05_DATA/sqlite/udos.db").exists():
        app_state_ok = True
    if (vault_path / ".udos/state.db").exists():
        app_state_ok = True

    if not app_state_ok:
        report.add_warning("No app state store found (.udos/ or 05_DATA/sqlite/udos.db)")

    report.details["markdown_files"] = len(md_files)
    return report


def validate_theme_pack(theme_dir: Path) -> ValidationReport:
    report = ValidationReport(valid=True)

    if not theme_dir.exists() or not theme_dir.is_dir():
        report.add_error(f"Theme directory missing: {theme_dir}")
        return report

    shell_path = theme_dir / "shell.html"
    css_path = theme_dir / "theme.css"
    json_path = theme_dir / "theme.json"
    assets_path = theme_dir / "assets"

    for path in (shell_path, css_path, json_path):
        if not path.exists():
            report.add_error(f"Missing required file: {path.name}")

    if not assets_path.exists():
        report.add_error("Missing required directory: assets/")

    shell_text = ""
    if shell_path.exists():
        try:
            shell_text = shell_path.read_text(encoding="utf-8")
        except Exception as exc:
            report.add_error(f"Failed to read shell.html: {exc}")

    if shell_text:
        missing_slots = [slot for slot in REQUIRED_SLOTS if slot not in shell_text]
        if missing_slots:
            report.add_error(f"shell.html missing slots: {', '.join(missing_slots)}")
        if "<!DOCTYPE" not in shell_text:
            report.add_warning("shell.html missing DOCTYPE")
        if "<html" not in shell_text or "<body" not in shell_text:
            report.add_warning("shell.html missing <html> or <body> tag")
        if re.search(r"https?://", shell_text):
            report.add_warning("shell.html references external URLs (offline-first risk)")

    css_text = ""
    if css_path.exists():
        try:
            css_text = css_path.read_text(encoding="utf-8")
        except Exception as exc:
            report.add_error(f"Failed to read theme.css: {exc}")

    if css_text and re.search(r"https?://", css_text):
        report.add_warning("theme.css references external URLs (offline-first risk)")

    if json_path.exists():
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            for key in ("name", "version", "mode"):
                if not payload.get(key):
                    report.add_error(f"theme.json missing '{key}'")
            if payload.get("mode") and payload["mode"] not in ALLOWED_THEME_MODES:
                report.add_error(
                    f"theme.json invalid mode '{payload['mode']}' (expected: {', '.join(sorted(ALLOWED_THEME_MODES))})"
                )
            if payload.get("slots"):
                declared = set()
                for slot in payload.get("slots", []):
                    value = str(slot)
                    value = value.replace("{{", "").replace("}}", "").strip()
                    declared.add(value)
                missing = REQUIRED_SLOT_NAMES - declared
                if missing:
                    report.add_warning(
                        f"theme.json slots missing required entries: {', '.join(sorted(missing))}"
                    )
        except json.JSONDecodeError:
            report.add_error("theme.json is not valid JSON")
        except Exception as exc:
            report.add_error(f"Failed to read theme.json: {exc}")

    return report


def validate_world_contract(vault_path: Path) -> ValidationReport:
    report = ValidationReport(valid=True)
    if not vault_path.exists() or not vault_path.is_dir():
        report.add_error(f"Vault path not found: {vault_path}")
        return report

    invalid_place_refs: List[str] = []
    invalid_locids: List[str] = []

    matched_locid_spans: Set[Tuple[Path, int, int]] = set()

    for file_path in _iter_text_files(vault_path, (".md", ".txt", ".json", ".yml", ".yaml")):
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for match in PLACE_REF_RE.finditer(text):
            span = match.span()
            matched_locid_spans.add((file_path, span[0], span[1]))
            place_ref = match.group(0)
            error = validate_place_ref(place_ref)
            if error:
                invalid_place_refs.append(f"{file_path}: {place_ref} ({error})")

        for match in LOCID_RE.finditer(text):
            locid = match.group(0)
            # Skip locids that are part of place refs
            if any(
                (file_path == fp and match.start() >= s and match.end() <= e)
                for (fp, s, e) in matched_locid_spans
            ):
                continue
            if not _parse_locid(locid):
                invalid_locids.append(f"{file_path}: {locid}")

    if invalid_place_refs:
        report.add_error("Invalid PlaceRefs found")
        report.details["invalid_place_refs"] = invalid_place_refs

    if invalid_locids:
        report.add_error("Invalid LocIds found")
        report.details["invalid_locids"] = invalid_locids

    return report


def _print_report(title: str, report: ValidationReport) -> None:
    status = "OK" if report.valid else "FAILED"
    logger.info("[LOCAL] %s: %s", title, status)
    if report.errors:
        logger.info("[LOCAL] %s errors:", title)
        for err in report.errors:
            logger.info("  - %s", err)
    if report.warnings:
        logger.info("[LOCAL] %s warnings:", title)
        for warn in report.warnings:
            logger.info("  - %s", warn)


def main() -> int:
    parser = argparse.ArgumentParser(description="uDOS Contract Validator")
    parser.add_argument("--vault", type=str, default="vault", help="Path to vault root")
    parser.add_argument("--themes", type=str, default="themes", help="Path to themes root")
    parser.add_argument("--world", action="store_true", help="Validate LocId invariants in vault")
    parser.add_argument("--theme-only", action="store_true", help="Validate only theme packs")
    parser.add_argument("--vault-only", action="store_true", help="Validate only vault")
    args = parser.parse_args()

    repo_root = get_repo_root()
    vault_path = (repo_root / args.vault).resolve()
    themes_path = (repo_root / args.themes).resolve()

    overall_valid = True

    if not args.theme_only:
        vault_report = validate_vault_contract(vault_path)
        _print_report("Vault Contract", vault_report)
        overall_valid = overall_valid and vault_report.valid

    if not args.vault_only:
        theme_reports = {}
        if themes_path.exists():
            for theme_dir in sorted(p for p in themes_path.iterdir() if p.is_dir()):
                if not (theme_dir / "theme.json").exists() and not (theme_dir / "shell.html").exists():
                    continue
                theme_reports[theme_dir.name] = validate_theme_pack(theme_dir)
        else:
            theme_reports["themes"] = ValidationReport(valid=False, errors=["themes/ not found"])

        for name, report in theme_reports.items():
            _print_report(f"Theme Pack ({name})", report)
            overall_valid = overall_valid and report.valid

    if args.world:
        world_report = validate_world_contract(vault_path)
        _print_report("World Contract", world_report)
        overall_valid = overall_valid and world_report.valid

    return 0 if overall_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
