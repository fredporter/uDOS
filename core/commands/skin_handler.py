"""SKIN command handler - Wizard GUI theme packs (HTML/CSS)."""
from __future__ import annotations

import json
import os
from pathlib import Path

from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.services.compact_status_service import format_compact_status
from core.services.config_sync_service import ConfigSyncManager
from core.services.error_contract import CommandError
from core.services.logging_api import get_repo_root
from core.services.logging_manager import get_logger
from core.services.progression_contract_service import (
    LENS_OPTION_MAP,
    LENS_SKIN_RECOMMENDATIONS,
    build_skin_policy_context,
)
from core.services.time_utils import utc_now_iso
from core.tui.output import OutputToolkit


class SkinHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Manage Wizard GUI skins stored under /themes."""

    ENV_SKIN = "UDOS_WIZARD_SKIN"

    def __init__(self) -> None:
        super().__init__()
        self.logger = get_logger("skin-handler")
        self.sync = ConfigSyncManager()
        self.repo_root = get_repo_root()
        self.skin_root = self.repo_root / "themes"

    def handle(self, command: str, params: list[str], grid=None, parser=None) -> dict:
        with self.trace_command(command, params) as trace:
            if not params:
                result = self._status()
                trace.set_status(result.get("status", "success"))
                return result

            subcommand = params[0].upper()
            args = params[1:]

            if subcommand in {"LIST", "LS"}:
                result = self._list_skins()
            elif subcommand in {"STATUS"}:
                compact = any(str(item).strip().lower() in {"--compact", "compact"} for item in args)
                result = self._status(compact=compact)
            elif subcommand in {"CHECK"}:
                compact = any(str(item).strip().lower() in {"--compact", "compact"} for item in args)
                result = self._check_skin(compact=compact)
            elif subcommand in {"SHOW", "INFO"}:
                name = args[0] if args else self._active_skin()
                result = self._show_skin(name)
            elif subcommand in {"SET", "USE"}:
                if not args:
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="Skin name required",
                        recovery_hint="Usage: SKIN SET <name>",
                        level="INFO",
                    )
                result = self._set_skin(args[0])
            elif subcommand in {"SCAFFOLD"}:
                target = args[0] if args else self._active_skin()
                result = self._scaffold_skin_insertion(target)
            elif subcommand in {"INSERT"}:
                result = self._insert_skin_content(args)
            elif subcommand in {"CLEAR", "RESET", "DEFAULT"}:
                result = self._clear_skin()
            else:
                result = self._set_skin(params[0])

            trace.set_status(result.get("status", "success"))
            return result

    def _active_skin(self) -> str:
        from core.services.unified_config_loader import get_config

        value = get_config(self.ENV_SKIN, "").strip()
        return value or "default"

    def _skin_dirs(self) -> list[Path]:
        if not self.skin_root.exists():
            return []
        return sorted([p for p in self.skin_root.iterdir() if p.is_dir()])

    def _skin_meta(self, skin_name: str) -> dict[str, object] | None:
        skin_dir = self.skin_root / skin_name
        meta_path = skin_dir / "theme.json"
        if not meta_path.exists():
            return None
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            contract = self._validate_gameplay_contract(skin_name, data.get("gameplay"))
            return {
                "name": str(data.get("name") or skin_name),
                "version": str(data.get("version") or ""),
                "description": str(data.get("description") or ""),
                "gameplay_contract": contract,
            }
        except Exception as exc:
            self.logger.warning(f"Failed to read skin metadata: {exc}")
            return {
                "name": skin_name,
                "version": "",
                "description": "",
                "gameplay_contract": {
                    "valid": False,
                    "errors": ["theme_metadata_parse_failed"],
                },
            }

    def _validate_gameplay_contract(self, skin_name: str, raw_contract: object) -> dict[str, object]:
        known_lenses = sorted(LENS_OPTION_MAP.keys())
        if not isinstance(raw_contract, dict):
            return {
                "valid": False,
                "contract_version": "",
                "compatible_lenses": [],
                "recommended_lenses": [],
                "score_profile": "",
                "checkpoint_profile": "",
                "errors": ["missing_gameplay_contract"],
            }

        compatible_raw = raw_contract.get("compatible_lenses", [])
        recommended_raw = raw_contract.get("recommended_lenses", [])
        compatible = [
            str(item).strip().lower()
            for item in compatible_raw
            if str(item).strip()
        ] if isinstance(compatible_raw, list) else []
        recommended = [
            str(item).strip().lower()
            for item in recommended_raw
            if str(item).strip()
        ] if isinstance(recommended_raw, list) else []

        errors: list[str] = []
        valid_lenses = set(known_lenses) | {"any"}
        for lens_id in compatible:
            if lens_id not in valid_lenses:
                errors.append(f"unknown_compatible_lens:{lens_id}")
        for lens_id in recommended:
            if lens_id not in valid_lenses:
                errors.append(f"unknown_recommended_lens:{lens_id}")

        if not compatible:
            errors.append("missing_compatible_lenses")
        if not recommended:
            errors.append("missing_recommended_lenses")

        contract_version = str(raw_contract.get("contract_version", "")).strip()
        if not contract_version:
            errors.append("missing_contract_version")

        score_profile = str(raw_contract.get("score_profile", "")).strip()
        checkpoint_profile = str(raw_contract.get("checkpoint_profile", "")).strip()
        if not score_profile:
            errors.append("missing_score_profile")
        if not checkpoint_profile:
            errors.append("missing_checkpoint_profile")

        overlay_defaults = raw_contract.get("overlay_defaults", {})
        if overlay_defaults and not isinstance(overlay_defaults, dict):
            errors.append("overlay_defaults_must_be_object")
        insertion_scaffold = raw_contract.get("insertion_scaffold", {})
        if insertion_scaffold and not isinstance(insertion_scaffold, dict):
            errors.append("insertion_scaffold_must_be_object")
            insertion_scaffold = {}
        scaffold_css = str(insertion_scaffold.get("css", "")).strip() if isinstance(insertion_scaffold, dict) else ""
        scaffold_slots = str(insertion_scaffold.get("slots", "")).strip() if isinstance(insertion_scaffold, dict) else ""
        if insertion_scaffold and (not scaffold_css or not scaffold_slots):
            errors.append("insertion_scaffold_requires_css_and_slots")

        return {
            "skin": skin_name,
            "valid": len(errors) == 0,
            "contract_version": contract_version,
            "compatible_lenses": compatible,
            "recommended_lenses": recommended,
            "score_profile": score_profile,
            "checkpoint_profile": checkpoint_profile,
            "overlay_defaults": overlay_defaults if isinstance(overlay_defaults, dict) else {},
            "insertion_scaffold": {
                "css": scaffold_css,
                "slots": scaffold_slots,
            } if insertion_scaffold else {},
            "errors": errors,
        }

    def _available_skins(self) -> list[str]:
        skins = []
        for skin_dir in self._skin_dirs():
            if (skin_dir / "theme.json").exists():
                skins.append(skin_dir.name)
        return skins

    def _status(self, *, compact: bool = False) -> dict:
        active = self._active_skin()
        meta = self._skin_meta(active) or {}
        contract = meta.get("gameplay_contract", {}) if isinstance(meta.get("gameplay_contract"), dict) else {}
        contract_state = "valid" if contract.get("valid") else "invalid"
        progression, policy_flag, policy_note = self._skin_policy_context(active)
        if compact:
            active_lens = progression.get("active_lens", "unknown") if isinstance(progression, dict) else "unknown"
            compact_fields: dict[str, object] = {
                "skin": active,
                "lens": active_lens,
                "contract": contract_state,
                "fit": (
                    "aligned"
                    if not policy_flag
                    else ("unmapped" if policy_flag == "skin_lens_unmapped" else "mismatch")
                ),
                "policy": policy_flag,
            }
            if isinstance(progression, dict):
                stats = progression.get("stats", {}) if isinstance(progression.get("stats"), dict) else {}
                progress = progression.get("progress", {}) if isinstance(progression.get("progress"), dict) else {}
                compact_fields["xp"] = stats.get("xp", 0)
                compact_fields["gold"] = stats.get("gold", 0)
                compact_fields["ach"] = progress.get("achievement_level", 0)
            result = {
                "status": "success",
                "output": format_compact_status(
                    "SKIN",
                    compact_fields,
                    order=["skin", "lens", "contract", "fit", "xp", "gold", "ach", "policy"],
                ),
            }
            if policy_flag:
                result["policy_flag"] = policy_flag
            return result

        output = [OutputToolkit.banner("WIZARD GUI SKINS"), ""]
        output.append(f"Active: {active}")
        output.append(f"Gameplay metadata contract: {contract_state}")
        if progression:
            stats = progression.get("stats", {})
            progress = progression.get("progress", {})
            output.append(
                f"Progression: XP={stats.get('xp', 0)} Gold={stats.get('gold', 0)} "
                f"AchievementLevel={progress.get('achievement_level', 0)}"
            )
        if policy_note:
            output.append(policy_note)
        output.append("")
        output.append("Skins:")
        for name in self._available_skins():
            marker = "*" if name == active else "-"
            output.append(f"  {marker} {name}")
        output.append("")
        output.append(
            "Use: SKIN STATUS | SKIN CHECK | SKIN SET <name> | SKIN SHOW <name> | "
            "SKIN SCAFFOLD <name> | SKIN INSERT <name> CSS <css...>"
        )
        result = {"status": "success", "output": "\n".join(output)}
        if policy_flag:
            result["policy_flag"] = policy_flag
        return result

    def _list_skins(self) -> dict:
        return self._status()

    def _check_skin(self, *, compact: bool = False) -> dict:
        active = self._active_skin()
        meta = self._skin_meta(active) or {}
        contract = meta.get("gameplay_contract", {}) if isinstance(meta.get("gameplay_contract"), dict) else {}
        contract_state = "valid" if contract.get("valid") else "invalid"
        progression, policy_flag, policy_note = self._skin_policy_context(active)
        if compact:
            active_lens = progression.get("active_lens", "unknown") if isinstance(progression, dict) else "unknown"
            recommended = sorted(LENS_SKIN_RECOMMENDATIONS.get(str(active_lens), {"default"}))
            compact_fields: dict[str, object] = {
                "skin": active,
                "lens": active_lens,
                "contract": contract_state,
                "fit": (
                    "aligned"
                    if not policy_flag
                    else ("unmapped" if policy_flag == "skin_lens_unmapped" else "mismatch")
                ),
                "recommended": ",".join(recommended),
                "policy": policy_flag,
            }
            if isinstance(progression, dict):
                stats = progression.get("stats", {}) if isinstance(progression.get("stats"), dict) else {}
                p = progression.get("progress", {}) if isinstance(progression.get("progress"), dict) else {}
                compact_fields["xp"] = stats.get("xp", 0)
                compact_fields["gold"] = stats.get("gold", 0)
                compact_fields["ach"] = p.get("achievement_level", 0)
            result = {
                "status": "success",
                "output": format_compact_status(
                    "SKIN",
                    compact_fields,
                    order=["skin", "lens", "contract", "fit", "recommended", "xp", "gold", "ach", "policy"],
                ),
            }
            if progression:
                result["progression"] = progression
            if policy_flag:
                result["policy_flag"] = policy_flag
            return result

        output = [OutputToolkit.banner("SKIN CHECK"), ""]
        output.append(f"Active skin: {active}")
        output.append(f"Gameplay metadata contract: {contract_state}")
        if progression:
            active_lens = progression.get("active_lens", "unknown")
            output.append(f"Active lens: {active_lens}")
            recommended = sorted(LENS_SKIN_RECOMMENDATIONS.get(str(active_lens), {"default"}))
            output.append(f"Recommended skins: {', '.join(recommended)}")
        if policy_note:
            output.append(policy_note)
        output.append("Flag-only mode: recommendations are not enforced.")
        result = {"status": "success", "output": "\n".join(output)}
        if progression:
            result["progression"] = progression
        if policy_flag:
            result["policy_flag"] = policy_flag
        return result

    def _show_skin(self, name: str) -> dict:
        skins = self._available_skins()
        if name not in skins:
            raise CommandError(
                code="ERR_VALIDATION_INVALID_ID",
                message=f"Unknown skin: {name}",
                recovery_hint=f"Available: {', '.join(skins)}",
                level="INFO",
            )

        meta = self._skin_meta(name) or {"name": name, "version": "", "description": ""}
        contract = meta.get("gameplay_contract", {}) if isinstance(meta.get("gameplay_contract"), dict) else {}
        output = [OutputToolkit.banner(f"SKIN: {name}"), ""]
        output.append(f"Name: {meta.get('name', name)}")
        if meta.get("version"):
            output.append(f"Version: {meta.get('version')}")
        if meta.get("description"):
            output.append(f"Description: {meta.get('description')}")
        output.append(f"Gameplay contract: {'valid' if contract.get('valid') else 'invalid'}")
        if isinstance(contract.get("compatible_lenses"), list):
            output.append(f"Compatible lenses: {', '.join(contract.get('compatible_lenses', []))}")
        if isinstance(contract.get("recommended_lenses"), list):
            output.append(f"Recommended lenses: {', '.join(contract.get('recommended_lenses', []))}")
        if contract.get("score_profile"):
            output.append(f"Score profile: {contract.get('score_profile')}")
        if contract.get("checkpoint_profile"):
            output.append(f"Checkpoint profile: {contract.get('checkpoint_profile')}")
        insertion_scaffold = contract.get("insertion_scaffold", {})
        if isinstance(insertion_scaffold, dict) and insertion_scaffold:
            if insertion_scaffold.get("css"):
                output.append(f"Insertion CSS: {insertion_scaffold.get('css')}")
            if insertion_scaffold.get("slots"):
                output.append(f"Insertion slots: {insertion_scaffold.get('slots')}")
        if isinstance(contract.get("errors"), list) and contract.get("errors"):
            output.append(f"Contract errors: {', '.join(contract.get('errors', []))}")
        progression, policy_flag, policy_note = self._skin_policy_context(name)
        if progression:
            output.append("")
            output.append(f"Lens: {progression.get('active_lens', 'unknown')}")
        if policy_note:
            output.append(policy_note)
        output.append("")
        output.append("Use: SKIN SET <name>")
        result = {"status": "success", "output": "\n".join(output)}
        if policy_flag:
            result["policy_flag"] = policy_flag
        return result

    def _set_skin(self, name: str) -> dict:
        skins = self._available_skins()
        if name != "default" and name not in skins:
            raise CommandError(
                code="ERR_VALIDATION_INVALID_ID",
                message=f"Unknown skin: {name}",
                recovery_hint=f"Available: {', '.join(skins)}",
                level="INFO",
            )

        updates = {self.ENV_SKIN: None if name == "default" else name}
        ok, message = self.sync.update_env_vars(updates)
        if name == "default":
            os.environ.pop(self.ENV_SKIN, None)
        else:
            os.environ[self.ENV_SKIN] = name

        status = "success" if ok else "warning"
        progression, policy_flag, policy_note = self._skin_policy_context(name)
        output = f"Active skin set to {name}. {message}"
        if policy_note:
            output = f"{output}\n{policy_note}"
        result = {"status": status, "output": output}
        if progression:
            result["progression"] = progression
        if policy_flag:
            result["policy_flag"] = policy_flag
        return result

    def _scaffold_skin_insertion(self, skin_name: str) -> dict:
        skins = self._available_skins()
        if skin_name not in skins:
            raise CommandError(
                code="ERR_VALIDATION_INVALID_ID",
                message=f"Unknown skin: {skin_name}",
                recovery_hint=f"Available: {', '.join(skins)}",
                level="INFO",
            )

        skin_dir = self.skin_root / skin_name
        assets_dir = skin_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        override_path = assets_dir / "ucode-overrides.css"
        slots_path = assets_dir / "ucode-slots.json"
        theme_css_path = skin_dir / "theme.css"

        if not override_path.exists():
            override_path.write_text(
                "/* ucode-generated skin overrides */\n",
                encoding="utf-8",
            )

        if not slots_path.exists():
            slots_path.write_text(
                json.dumps(
                    {
                        "version": "v1",
                        "updated_at": utc_now_iso(),
                        "slots": {},
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

        import_line = '@import "./assets/ucode-overrides.css";'
        if theme_css_path.exists():
            content = theme_css_path.read_text(encoding="utf-8")
            if import_line not in content:
                lines = content.splitlines()
                insert_at = 1 if lines and lines[0].startswith("@import") else 0
                lines.insert(insert_at, import_line)
                theme_css_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        return {
            "status": "success",
            "output": "\n".join(
                [
                    f"Scaffolded ucode skin insertion for {skin_name}.",
                    f"- CSS overrides: {override_path}",
                    f"- Slot payloads: {slots_path}",
                ]
            ),
            "skin": skin_name,
            "paths": {
                "override_css": str(override_path),
                "slots_json": str(slots_path),
                "theme_css": str(theme_css_path),
            },
        }

    def _insert_skin_content(self, args: list[str]) -> dict:
        if len(args) < 3:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: SKIN INSERT <skin> <CSS|SLOT> <content...>",
                recovery_hint=(
                    "Usage: SKIN INSERT teletext CSS .hud{color:#0ff;} "
                    "or SKIN INSERT teletext SLOT hud <html>"
                ),
                level="INFO",
            )
        skin_name = args[0]
        mode = args[1].strip().upper()

        self._scaffold_skin_insertion(skin_name)
        skin_dir = self.skin_root / skin_name
        assets_dir = skin_dir / "assets"
        override_path = assets_dir / "ucode-overrides.css"
        slots_path = assets_dir / "ucode-slots.json"

        if mode == "CSS":
            css_snippet = " ".join(args[2:]).strip()
            if not css_snippet:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="CSS content required",
                    recovery_hint="Usage: SKIN INSERT <skin> CSS .panel{color:#fff;}",
                    level="INFO",
                )
            block = "\n".join(
                [
                    "",
                    f"/* ucode insert {utc_now_iso()} */",
                    css_snippet,
                    "",
                ]
            )
            with override_path.open("a", encoding="utf-8") as handle:
                handle.write(block)
            return {
                "status": "success",
                "output": f"Inserted CSS into {override_path}",
                "skin": skin_name,
                "target": "css",
                "path": str(override_path),
            }

        if mode == "SLOT":
            if len(args) < 4:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Syntax: SKIN INSERT <skin> SLOT <slot> <content...>",
                    recovery_hint="Usage: SKIN INSERT <skin> SLOT hud <div>HUD</div>",
                    level="INFO",
                )
            slot_name = args[2].strip().lower()
            slot_content = " ".join(args[3:]).strip()
            if not slot_name or not slot_content:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Slot name and content are required",
                    recovery_hint="Usage: SKIN INSERT <skin> SLOT hud <div>HUD</div>",
                    level="INFO",
                )

            payload: dict[str, object]
            if slots_path.exists():
                try:
                    payload = json.loads(slots_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    payload = {"version": "v1", "slots": {}}
            else:
                payload = {"version": "v1", "slots": {}}
            if not isinstance(payload, dict):
                payload = {"version": "v1", "slots": {}}
            slots = payload.get("slots", {})
            if not isinstance(slots, dict):
                slots = {}

            rows = slots.get(slot_name, [])
            if not isinstance(rows, list):
                rows = []
            rows.append({"inserted_at": utc_now_iso(), "content": slot_content})
            slots[slot_name] = rows
            payload["slots"] = slots
            payload["updated_at"] = utc_now_iso()
            slots_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            return {
                "status": "success",
                "output": f"Inserted slot content into {slots_path} ({slot_name})",
                "skin": skin_name,
                "target": "slot",
                "slot": slot_name,
                "path": str(slots_path),
            }

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Target must be CSS or SLOT",
            recovery_hint="Usage: SKIN INSERT <skin> <CSS|SLOT> ...",
            level="INFO",
        )

    def _clear_skin(self) -> dict:
        updates = {self.ENV_SKIN: None}
        ok, message = self.sync.update_env_vars(updates)
        os.environ.pop(self.ENV_SKIN, None)
        status = "success" if ok else "warning"
        output = f"Skin override cleared. {message}"
        return {"status": status, "output": output}

    def _skin_policy_context(self, skin_name: str) -> tuple[dict | None, str | None, str | None]:
        """Return progression-aware policy hints for SKIN surfaces."""
        try:
            from core.services.gameplay_service import get_gameplay_service
            from core.services.user_service import get_user_manager
        except Exception:
            return None, None, None

        user = get_user_manager().current()
        if not user:
            return None, None, None

        progression = get_gameplay_service().progression_snapshot(user.username)
        policy = build_skin_policy_context(
            progression=progression,
            selected_skin=skin_name,
            available_skins=self._available_skins(),
        )
        return policy.progression, policy.policy_flag, policy.policy_note
