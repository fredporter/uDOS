"""THINGUI command handler - Thin GUI extension management from core TUI."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any

from core.commands.base import BaseCommandHandler
from core.services.error_contract import CommandError
from core.services.logging_api import get_repo_root
from core.services.thin_gui_bridge_service import get_thin_gui_bridge_service
from core.services.unified_config_loader import get_config


class ThinGuiHandler(BaseCommandHandler):
    """Manage Thin GUI extension lifecycle.

    Commands:
      THINGUI
      THINGUI STATUS
      THINGUI INSTALL
      THINGUI BUILD
      THINGUI LINT
      THINGUI OPEN [target_url|profile]
      THINGUI INTENT <target_url|profile> [title] [label]
    """

    def __init__(self) -> None:
        super().__init__()
        self.repo_root = get_repo_root()
        self.extension_dir = self.repo_root / "extensions" / "thin-gui"
        self.intent_path = self.repo_root / "memory" / "ucode" / "thin_gui_intent.json"
        self.bridge = get_thin_gui_bridge_service()

    def handle(self, command: str, params: list[str], grid=None, parser=None) -> dict[str, Any]:
        action = params[0].strip().lower() if params else "status"

        if action in {"status", "show"}:
            return self._status()
        if action == "install":
            return self._run_npm(["npm", "ci"], "Thin GUI dependencies installed")
        if action == "build":
            return self._run_npm(["npm", "run", "build"], "Thin GUI build complete")
        if action == "lint":
            return self._run_npm(["npm", "run", "lint"], "Thin GUI lint complete")
        if action == "open":
            target_or_profile = params[1].strip() if len(params) > 1 else ""
            return self._open_hint(target_or_profile)
        if action == "intent":
            if len(params) < 2:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Syntax: THINGUI INTENT <target_url|profile> [title] [label]",
                    recovery_hint="Usage: THINGUI INTENT crawler3d or THINGUI INTENT http://127.0.0.1:7424",
                    level="INFO",
                )
            return self._intent_hint(params)

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message=f"Unknown THINGUI subcommand: {action}",
            recovery_hint="Use THINGUI STATUS|INSTALL|BUILD|LINT|OPEN|INTENT",
            level="INFO",
        )

    def _status(self) -> dict[str, Any]:
        exists = self.extension_dir.exists()
        package_json = self.extension_dir / "package.json"
        tsconfig = self.extension_dir / "tsconfig.json"
        node_modules = self.extension_dir / "node_modules"
        dist_dir = self.extension_dir / "dist"
        shell_html = self.extension_dir / "assets" / "index.html"

        output = ["THINGUI STATUS"]
        output.append(f"Extension path: {self.extension_dir}")
        output.append(f"Available: {'yes' if exists else 'no'}")
        output.append(f"package.json: {'yes' if package_json.exists() else 'no'}")
        output.append(f"tsconfig.json: {'yes' if tsconfig.exists() else 'no'}")
        output.append(f"node_modules: {'yes' if node_modules.exists() else 'no'}")
        output.append(f"dist: {'yes' if dist_dir.exists() else 'no'}")
        output.append(f"assets/index.html: {'yes' if shell_html.exists() else 'no'}")
        output.append(f"npm: {'yes' if shutil.which('npm') else 'no'}")
        output.append(f"node: {'yes' if shutil.which('node') else 'no'}")

        if exists:
            output.append("Use: THINGUI INSTALL | THINGUI BUILD | THINGUI OPEN")

        return {
            "status": "success",
            "output": "\n".join(output),
            "thin_gui": {
                "available": exists,
                "path": str(self.extension_dir),
                "package_json": package_json.exists(),
                "tsconfig": tsconfig.exists(),
                "node_modules": node_modules.exists(),
                "dist": dist_dir.exists(),
                "shell_html": shell_html.exists(),
                "npm": bool(shutil.which("npm")),
                "node": bool(shutil.which("node")),
            },
        }

    def _run_npm(self, cmd: list[str], message: str) -> dict[str, Any]:
        if not self.extension_dir.exists():
            raise CommandError(
                code="ERR_SERVICE_UNAVAILABLE",
                message="Thin GUI extension is not installed",
                recovery_hint="Ensure extensions/thin-gui exists",
                level="ERROR",
            )
        if not shutil.which("npm"):
            raise CommandError(
                code="ERR_RUNTIME_MISSING_DEPENDENCY",
                message="npm is required",
                recovery_hint="Install Node.js/npm and retry",
                level="ERROR",
            )

        result = subprocess.run(
            cmd,
            cwd=self.extension_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise CommandError(
                code="ERR_RUNTIME_EXECUTION_FAILED",
                message=f"Thin GUI command failed: {' '.join(cmd)}",
                recovery_hint=(result.stderr or result.stdout or "Check Node.js/npm setup").strip(),
                level="ERROR",
            )

        return {
            "status": "success",
            "message": message,
            "output": "\n".join(
                [
                    f"{message}.",
                    f"Command: {' '.join(cmd)}",
                    (result.stdout or "").strip(),
                ]
            ).strip(),
        }

    @staticmethod
    def _looks_like_url(value: str) -> bool:
        token = (value or "").strip().lower()
        return token.startswith("http://") or token.startswith("https://") or token.startswith("file://")

    def _open_hint(self, target_or_profile: str) -> dict[str, Any]:
        token = (target_or_profile or "").strip()
        if token and not self._looks_like_url(token):
            launch = self.bridge.resolve_target(token)
            route = self.bridge.wizard_route(launch)
            output = "\n".join(
                [
                    f"THINGUI OPEN {launch.profile_id}",
                    f"Target: {launch.target_url or '(unset)'}",
                    f"Wizard route: {route}",
                ]
            )
            return {
                "status": "success",
                "output": output,
                "route": route,
                "profile_id": launch.profile_id,
                "target": launch.target_url,
            }

        base_url = get_config("WIZARD_BASE_URL", "http://127.0.0.1:8765").rstrip("/")
        if token:
            route = f"{base_url}/#thin-gui?title=Thin%20GUI&target={token}"
        else:
            route = f"{base_url}/#thin-gui"
        output = "\n".join(
            [
                "THINGUI OPEN",
                f"Wizard route: {route}",
                "Use THINGUI INTENT <target_url> [title] [label] to persist launch intent.",
            ]
        )
        return {"status": "success", "output": output, "route": route}

    def _intent_hint(self, params: list[str]) -> dict[str, Any]:
        target_or_profile = params[1].strip()
        title = params[2].strip() if len(params) > 2 else ""
        label = params[3].strip() if len(params) > 3 else ""
        if target_or_profile and not self._looks_like_url(target_or_profile):
            launch = self.bridge.resolve_target(target_or_profile)
            if title:
                launch = replace(launch, title=title, label=label or title)
            payload = self.bridge.write_intent(launch)
            return {
                "status": "success",
                "output": "\n".join(
                    [
                        f"THINGUI INTENT {launch.profile_id}",
                        f"Intent saved: {self.bridge.intent_path}",
                        f"Target: {launch.target_url or '(unset)'}",
                    ]
                ),
                "intent": payload,
            }

        intent_title = title or "Thin GUI"
        intent_label = label or intent_title
        return self._write_intent(target_or_profile, intent_title, intent_label)

    def _write_intent(self, target: str, title: str, label: str) -> dict[str, Any]:
        self.intent_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "target": target,
            "title": title,
            "label": label,
            "wizard_route": "#thin-gui",
            "extension": "thin-gui",
            "ui_contract": {
                "single_window": True,
                "single_use": True,
                "fullscreen": True,
                "top_layer": True,
                "controls": ["close-return-tui"],
            },
        }
        self.intent_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return {
            "status": "success",
            "output": "\n".join(
                [
                    "THINGUI INTENT",
                    f"Intent saved: {self.intent_path}",
                    f"Target: {target}",
                ]
            ),
            "intent": payload,
        }
