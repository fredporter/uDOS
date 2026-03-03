"""UCODE command handler - minimum offline/online helper surface."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import hmac
import json
import os
from pathlib import Path
import platform
import re
import secrets
import shutil
import subprocess
from typing import Any

from core.commands.base import BaseCommandHandler
from core.services.error_contract import CommandError
from core.services.offline_assets_service import resolve_offline_assets_contract
from core.services.operator_mode_service import get_operator_mode_service
from core.services.release_profile_service import get_release_profile_service
from core.services.seed_template_service import get_seed_template_service
from core.services.system_capability_service import (
    MinimumSystemSpec,
    get_system_capability_service,
)


@dataclass(frozen=True)
class _Capability:
    name: str
    status: str
    detail: str
    profiles: set[str]


class UcodeHandler(BaseCommandHandler):
    """Handler for UCODE command family."""

    def __init__(self) -> None:
        super().__init__()
        self.repo_root = Path(__file__).resolve().parents[2]
        from core.services.unified_config_loader import get_config

        env_ucode_root = get_config("UDOS_UCODE_ROOT", "").strip()
        if env_ucode_root:
            candidate = Path(env_ucode_root).expanduser()
            self.ucode_root = (
                candidate if candidate.is_absolute() else (self.repo_root / candidate)
            )
            self.offline_assets_root = self.ucode_root
        else:
            offline_assets = resolve_offline_assets_contract(self.repo_root)
            self.ucode_root = offline_assets.cache_namespace / "ucode"
            self.offline_assets_root = offline_assets.root
        self.demos_root = self.ucode_root / "demos"
        self.docs_root = self.ucode_root / "docs"
        self.plugins_root = self.ucode_root / "plugins"
        self.plugins_manifest_path = self.plugins_root / "installed.json"
        self.bundles_root = self.ucode_root / "bundles"
        self.bundle_manifest_path = self.bundles_root / "offline-content-bundle.json"
        self.bundle_signing_key_path = self.bundles_root / "bundle-signing.key"
        self.metrics_root = self.ucode_root / "metrics"
        self.metrics_events_path = self.metrics_root / "usage-events.jsonl"
        self.metrics_summary_path = self.metrics_root / "usage-summary.json"
        self.minimum_spec = MinimumSystemSpec()
        self.profile_service = get_release_profile_service()
        self.operator_service = get_operator_mode_service()
        self.seed_template_service = get_seed_template_service(self.repo_root)
        self.system_capability_service = get_system_capability_service(self.repo_root)

    def handle(
        self, command: str, params: list[str], grid: Any = None, parser: Any = None
    ) -> dict[str, Any]:
        self._ensure_offline_assets()
        action = params[0].lower() if params else "help"
        started_at = datetime.now(UTC)
        if not params:
            result = self._help_payload()
            self._record_usage_metric(
                action=action, result=result, started_at=started_at
            )
            return result

        try:
            if action == "demo":
                result = self._handle_demo(params[1:])
            elif action == "system":
                result = self._handle_system(params[1:])
            elif action == "docs":
                result = self._handle_docs(params[1:])
            elif action == "capabilities":
                result = self._handle_capabilities(params[1:])
            elif action == "plugin":
                result = self._handle_plugin(params[1:])
            elif action == "metrics":
                result = self._handle_metrics(params[1:])
            elif action == "update":
                result = self._handle_update()
            elif action == "env":
                result = self._handle_env(params[1:])
            elif action == "template":
                result = self._handle_template(params[1:])
            elif action == "profile":
                result = self._handle_profile(params[1:])
            elif action == "operator":
                result = self._handle_operator(params[1:])
            elif action == "extension":
                result = self._handle_extension(params[1:])
            elif action == "package":
                result = self._handle_package(params[1:])
            elif action == "repair":
                result = self._handle_rebaseline_repair(params[1:])
            else:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Syntax: UCODE <DEMO|SYSTEM|DOCS|CAPABILITIES|PLUGIN|METRICS|UPDATE|ENV|TEMPLATE|PROFILE|OPERATOR|EXTENSION|PACKAGE|REPAIR> ...",
                    recovery_hint="Run UCODE for command help",
                    level="INFO",
                )
        except CommandError as exc:
            self._record_usage_metric(
                action=action, result=None, started_at=started_at, error=exc
            )
            raise

        self._record_usage_metric(action=action, result=result, started_at=started_at)
        return result

    def _ensure_offline_assets(self) -> None:
        self.demos_root.mkdir(parents=True, exist_ok=True)
        self.docs_root.mkdir(parents=True, exist_ok=True)
        self.plugins_root.mkdir(parents=True, exist_ok=True)
        self.bundles_root.mkdir(parents=True, exist_ok=True)
        self.metrics_root.mkdir(parents=True, exist_ok=True)
        self._ensure_plugins_manifest()
        self._ensure_metrics_summary()
        self._seed_demo_assets(overwrite=False)
        self._seed_doc_assets(overwrite=False)

    def _help_payload(self) -> dict[str, Any]:
        lines = [
            "UCODE minimum surface:",
            "  UCODE DEMO LIST",
            "  UCODE DEMO RUN <script>",
            "  UCODE SYSTEM INFO",
            "  UCODE DOCS [--query <text>] [--section <name>]",
            "  UCODE CAPABILITIES [--filter <text>]",
            "  UCODE PLUGIN LIST",
            "  UCODE PLUGIN INSTALL <name>",
            "  UCODE METRICS [SUMMARY]",
            "  UCODE UPDATE",
            "  UCODE ENV [key=value ...]",
            "  UCODE TEMPLATE <LIST|READ|DUPLICATE> ...",
            "  UCODE PROFILE <LIST|SHOW|INSTALL|ENABLE|DISABLE|VERIFY> [profile]",
            "  UCODE OPERATOR <STATUS|PLAN <prompt>|QUEUE>",
            "  UCODE EXTENSION <LIST|VERIFY> [extension]",
            "  UCODE PACKAGE <LIST|VERIFY> [group]",
            "  UCODE REPAIR STATUS",
        ]
        return {
            "status": "success",
            "message": "UCODE help",
            "output": "\n".join(lines),
        }

    def _handle_demo(self, params: list[str]) -> dict[str, Any]:
        if not params or params[0].lower() == "list":
            scripts = sorted(path.stem for path in self.demos_root.glob("*.txt"))
            output = (
                "No demos available."
                if not scripts
                else "\n".join(f"{idx + 1}. {name}" for idx, name in enumerate(scripts))
            )
            return {
                "status": "success",
                "message": "Demo scripts listed",
                "output": output,
                "scripts": scripts,
            }

        if params[0].lower() != "run" or len(params) < 2:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: UCODE DEMO <LIST|RUN <script>>",
                recovery_hint="Try `UCODE DEMO LIST`",
                level="INFO",
            )

        target = params[1].strip().replace(" ", "_")
        demo_path = self.demos_root / f"{target}.txt"
        if not demo_path.exists():
            raise CommandError(
                code="ERR_RESOURCE_NOT_FOUND",
                message=f"Demo not found: {target}",
                recovery_hint="Run `UCODE DEMO LIST` to view available demos",
                level="INFO",
            )

        content = demo_path.read_text(encoding="utf-8")
        return {
            "status": "success",
            "message": f"Demo executed: {target}",
            "output": content,
            "script": target,
        }

    def _handle_system(self, params: list[str]) -> dict[str, Any]:
        if not params or params[0].lower() != "info":
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: UCODE SYSTEM INFO",
                recovery_hint="Run `UCODE SYSTEM INFO`",
                level="INFO",
            )

        capability, spec_result = self.system_capability_service.evaluate_minimum_spec(
            self.minimum_spec
        )
        min_spec_status = "PASS" if spec_result.overall else "FAIL"
        metrics_summary = self._load_metrics_summary()
        validation_samples = int(metrics_summary.get("total_events", 0))
        validation_round = "round-1-local"

        lines = [
            f"OS: {capability.system} {capability.release} ({capability.arch})",
            f"CPU cores: {capability.cpu_cores}",
            f"RAM: {capability.ram_gb:.1f} GB",
            f"Storage: {capability.storage_free_gb:.1f} GB free / {capability.storage_total_gb:.1f} GB total",
            (
                f"Minimum spec ({self.minimum_spec.cpu_cores} cores, "
                f"{self.minimum_spec.ram_gb:.1f} GB RAM, "
                f"{self.minimum_spec.storage_free_gb:.1f} GB free): {min_spec_status}"
            ),
            f"  - CPU: {'PASS' if spec_result.cpu else 'FAIL'}",
            f"  - RAM: {'PASS' if spec_result.ram else 'FAIL'}",
            f"  - Storage: {'PASS' if spec_result.storage else 'FAIL'}",
            (
                "Field validation: "
                f"{validation_round} (samples={validation_samples}; "
                "rebaseline=2 cores / 4.0 GB RAM / 5.0 GB free)"
            ),
        ]
        return {
            "status": "success",
            "message": "System information",
            "output": "\n".join(lines),
            "system": {
                "os": capability.system,
                "release": capability.release,
                "arch": capability.arch,
                "cpu_cores": capability.cpu_cores,
                "ram_gb": round(capability.ram_gb, 1),
                "storage_free_gb": round(capability.storage_free_gb, 1),
                "storage_total_gb": round(capability.storage_total_gb, 1),
                "uefi_native": capability.uefi_native,
                "headless": capability.headless,
                "minimum_spec": spec_result.to_dict(),
                "field_validation": {
                    "round": validation_round,
                    "sample_size": validation_samples,
                    "rebaseline_targets": {
                        "cpu_cores": self.minimum_spec.cpu_cores,
                        "ram_gb": self.minimum_spec.ram_gb,
                        "storage_free_gb": self.minimum_spec.storage_free_gb,
                    },
                },
            },
        }

    def _handle_docs(self, params: list[str]) -> dict[str, Any]:
        if params and params[0].lower() == "docs":
            params = params[1:]
        if params and params[0].startswith("--"):
            pass
        elif params:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: UCODE DOCS [--query <text>] [--section <name>]",
                recovery_hint="Run `UCODE DOCS`",
                level="INFO",
            )

        query = self._extract_opt(params, "--query")
        section = self._extract_opt(params, "--section")
        docs = sorted(self.docs_root.glob("*.*"))
        matches: list[Path] = []
        for doc in docs:
            text = doc.read_text(encoding="utf-8", errors="ignore")
            doc_key = f"{doc.name}\n{text}".lower()
            if query and query.lower() not in doc_key:
                continue
            if section and section.lower() not in doc_key:
                continue
            matches.append(doc)

        if not matches:
            return {
                "status": "warning",
                "message": "No docs matched query",
                "output": "No matching local docs found.",
                "matches": [],
            }

        preview_lines: list[str] = []
        for doc in matches[:5]:
            content = doc.read_text(encoding="utf-8", errors="ignore").splitlines()
            first = next((line.strip() for line in content if line.strip()), "(empty)")
            preview_lines.append(f"- {doc.name}: {first}")

        return {
            "status": "success",
            "message": "Local docs query result",
            "output": "\n".join(preview_lines),
            "matches": [doc.name for doc in matches],
        }

    def _handle_capabilities(self, params: list[str]) -> dict[str, Any]:
        filt = self._extract_opt(params, "--filter")
        network_ok = self._network_reachable()
        profile_filter = self._extract_profile_filter(filt)
        capabilities = [
            _Capability(
                "demo.scripts",
                "ready",
                str(self.demos_root),
                {"core", "full", "wizard"},
            ),
            _Capability(
                "docs.offline", "ready", str(self.docs_root), {"core", "full", "wizard"}
            ),
            _Capability(
                "wizard.server",
                "ready" if (self.repo_root / "wizard").exists() else "missing",
                "Wizard routes and MCP gateway",
                {"wizard", "full"},
            ),
            _Capability(
                "cloud.ai",
                "ready" if network_ok else "offline",
                "Cloud provider fallback path",
                {"full", "wizard"},
            ),
        ]
        capabilities.extend(self._plugin_capabilities())

        if profile_filter:
            filtered = [cap for cap in capabilities if profile_filter in cap.profiles]
        elif filt:
            filtered = [
                cap
                for cap in capabilities
                if filt.lower() in f"{cap.name} {cap.detail} {cap.status}".lower()
            ]
        else:
            filtered = capabilities

        output = (
            "\n".join(
                f"- {cap.name}: {cap.status} ({cap.detail}; profiles={','.join(sorted(cap.profiles))})"
                for cap in filtered
            )
            or "No capabilities matched filter."
        )
        return {
            "status": "success",
            "message": "Capabilities report",
            "output": output,
            "capabilities": [
                {
                    "name": cap.name,
                    "status": cap.status,
                    "detail": cap.detail,
                    "profiles": sorted(cap.profiles),
                }
                for cap in filtered
            ],
            "filter_profile": profile_filter,
            "network": "online" if network_ok else "offline",
        }

    def _handle_plugin(self, params: list[str]) -> dict[str, Any]:
        if not params or params[0].lower() == "list":
            plugins = self._load_installed_plugins()
            if not plugins:
                return {
                    "status": "success",
                    "message": "Installed plugins",
                    "output": "No plugins installed.",
                    "plugins": [],
                }
            lines = [
                f"- {plugin['name']}: {plugin['status']} ({plugin['source']})"
                for plugin in plugins
            ]
            return {
                "status": "success",
                "message": "Installed plugins",
                "output": "\n".join(lines),
                "plugins": plugins,
            }

        if params[0].lower() != "install" or len(params) < 2:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: UCODE PLUGIN <LIST|INSTALL <name>>",
                recovery_hint="Try `UCODE PLUGIN LIST`",
                level="INFO",
            )

        plugin_name = self._normalize_plugin_name(params[1])
        if not plugin_name:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Plugin name is required",
                recovery_hint="Use `UCODE PLUGIN INSTALL <name>`",
                level="INFO",
            )

        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,63}", plugin_name):
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Invalid plugin name",
                recovery_hint="Use lowercase letters/numbers and ._- (2-64 chars)",
                level="INFO",
            )

        plugins = self._load_installed_plugins()
        if any(plugin["name"] == plugin_name for plugin in plugins):
            return {
                "status": "warning",
                "message": "Plugin already installed",
                "output": f"Plugin already installed: {plugin_name}",
                "plugin": next(
                    plugin for plugin in plugins if plugin["name"] == plugin_name
                ),
            }

        installed = {
            "name": plugin_name,
            "status": "installed",
            "source": "local-scaffold",
            "installed_at": datetime.now(UTC).isoformat(),
            "capabilities": [f"plugin.{plugin_name}"],
        }
        plugins.append(installed)
        self._write_installed_plugins(plugins)
        return {
            "status": "success",
            "message": "Plugin installed",
            "output": (
                f"Plugin installed: {plugin_name}\n"
                "Scaffold pathway enabled for capabilities discovery."
            ),
            "plugin": installed,
        }

    def _handle_update(self) -> dict[str, Any]:
        network_ok = self._network_reachable()
        if not network_ok:
            return {
                "status": "warning",
                "message": "UCODE update",
                "output": "No network detected; update skipped.",
                "fallback_order": self._offline_fallback_order(),
            }

        self._seed_demo_assets(overwrite=True)
        self._seed_doc_assets(overwrite=True)
        manifest = {
            "updated_at": datetime.now(UTC).isoformat(),
            "demos_path": str(self.demos_root),
            "docs_path": str(self.docs_root),
            "network": "online",
        }
        bundle_manifest = self._create_offline_bundle_manifest()
        manifest_path = self.ucode_root / "update-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
        return {
            "status": "success",
            "message": "UCODE update",
            "output": (
                "Offline demos/docs refreshed from local canonical sources. "
                f"Manifest written: {manifest_path}"
            ),
            "updated": manifest,
            "bundle": bundle_manifest,
            "fallback_order": self._offline_fallback_order(),
        }

    def _handle_metrics(self, params: list[str]) -> dict[str, Any]:
        if params and params[0].lower() not in {"summary"}:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: UCODE METRICS [SUMMARY]",
                recovery_hint="Run `UCODE METRICS`",
                level="INFO",
            )

        summary = self._load_metrics_summary()
        recent = self._read_metrics_events_tail(limit=5)
        lines = [
            "UCODE local usage metrics (telemetry-free):",
            f"- total_events: {summary.get('total_events', 0)}",
            f"- offline_events: {summary.get('offline_events', 0)}",
            f"- fallback_events: {summary.get('fallback_events', 0)}",
            f"- last_event_at: {summary.get('last_event_at', 'n/a')}",
            "- actions:",
        ]
        for action, count in sorted(summary.get("actions", {}).items()):
            lines.append(f"  - {action}: {count}")
        lines.append("- statuses:")
        for status, count in sorted(summary.get("statuses", {}).items()):
            lines.append(f"  - {status}: {count}")
        if recent:
            lines.append("- recent_events:")
            for event in recent:
                lines.append(
                    "  - "
                    f"{event.get('timestamp', 'n/a')} "
                    f"{event.get('action', 'unknown')} "
                    f"{event.get('status', 'unknown')}"
                )
        return {
            "status": "success",
            "message": "UCODE metrics summary",
            "output": "\n".join(lines),
            "metrics": summary,
            "recent_events": recent,
        }

    def _handle_env(self, params: list[str]) -> dict[str, Any]:
        """Handle ENV commands for managing .env variables.

        Usage:
            UCODE ENV                    List all .env variables (masked)
            UCODE ENV key="value"        Set single variable
            UCODE ENV k1="v1" k2="v2"   Set multiple variables
        """
        env_path = self.repo_root / ".env"

        # List mode: ENV with no args
        if not params:
            return self._env_list(env_path)

        # Set mode: ENV key=value [key=value ...]
        try:
            assignments = self._parse_env_assignments(params)
            if not assignments:
                msg = "Invalid assignment format. "
                msg += 'Use: ENV key="value" [key="value" ...]'
                hint = 'Example: ENV username="Fred" '
                hint += 'mistral_api_key="xyz"'
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=msg,
                    recovery_hint=hint,
                    level="INFO",
                )
            return self._env_set(env_path, assignments)
        except ValueError as e:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message=f"Failed to parse assignments: {e}",
                recovery_hint=(
                    'Use format: ENV key="value" (with quotes around values)'
                ),
                level="INFO",
            )

    def _env_list(self, env_path: Path) -> dict[str, Any]:
        """List all .env variables (masked for sensitive keys)."""
        if not env_path.exists():
            return {
                "status": "info",
                "message": "ENV list",
                "output": ".env file not found. Run SETUP story to create it.",
                "variables": {},
            }

        variables = {}
        lines = []
        masked_keys = {
            "MISTRAL_API_KEY",
            "WIZARD_ADMIN_TOKEN",
            "WIZARD_KEY",
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY",
            "GITHUB_TOKEN",
            "AWS_SECRET_ACCESS_KEY",
            "GCP_SERVICE_ACCOUNT",
            "USER_PASSWORD",
        }

        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                variables[key] = value

                # Mask sensitive values in output
                if key in masked_keys:
                    display_value = "***" if value else "(empty)"
                elif len(value) > 50:
                    display_value = f"{value[:47]}..."
                else:
                    display_value = value

                lines.append(f"  {key} = {display_value}")

            output_text = (
                "Current .env variables:\n" + "\n".join(lines)
                if lines
                else "No variables found in .env"
            )
            return {
                "status": "success",
                "message": "ENV list",
                "output": output_text,
                "variables": variables,
                "count": len(variables),
            }
        except Exception as e:
            raise CommandError(
                code="ERR_IO_READ_FAILED",
                message=f"Failed to read .env: {e}",
                recovery_hint="Check that .env file is readable",
                level="ERROR",
            )

    def _parse_env_assignments(self, params: list[str]) -> dict[str, str]:
        """Parse key=value assignments from command params.

        Handles formats like:
            key="value"
            key=value (without quotes)
            key="multi word value"
        """
        assignments = {}
        remaining = " ".join(params)

        # Parse key="value" or key=value format
        i = 0
        while i < len(remaining):
            # Skip whitespace
            while i < len(remaining) and remaining[i].isspace():
                i += 1
            if i >= len(remaining):
                break

            # Find key
            key_start = i
            while i < len(remaining) and remaining[i] not in ("=", " ", "\t"):
                i += 1
            key = remaining[key_start:i].strip()

            if not key or "=" not in remaining[i:]:
                break

            # Skip '='
            while i < len(remaining) and remaining[i] in ("=", " ", "\t"):
                i += 1

            # Find value
            if i < len(remaining) and remaining[i] == '"':
                # Quoted value
                i += 1
                value_start = i
                while i < len(remaining) and remaining[i] != '"':
                    if remaining[i] == "\\" and i + 1 < len(remaining):
                        i += 2
                    else:
                        i += 1
                value = remaining[value_start:i]
                if i < len(remaining):
                    i += 1  # Skip closing quote
            else:
                # Unquoted value (until whitespace)
                value_start = i
                while i < len(remaining) and not remaining[i].isspace():
                    i += 1
                value = remaining[value_start:i]

            if key:
                assignments[key] = value

        return assignments

    def _env_set(self, env_path: Path, assignments: dict[str, str]) -> dict[str, Any]:
        """Set environment variables in .env file."""
        try:
            # Read existing .env
            existing = {}
            lines = []
            if env_path.exists():
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    raw = line.strip()
                    if not raw or raw.startswith("#"):
                        lines.append(line)
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        existing[key] = value
                        lines.append(line)

            # Update with new assignments
            updated = {}
            for key, value in assignments.items():
                updated[key] = value
                if key not in existing:
                    lines.append(f"{key}={value}")

            # Rewrite lines with updated values
            output_lines = []
            for line in lines:
                raw = line.strip()
                if raw and not raw.startswith("#") and "=" in line:
                    line_key = line.split("=", 1)[0].strip()
                    if line_key in updated:
                        output_lines.append(f"{line_key}={updated[line_key]}")
                    else:
                        output_lines.append(line)
                else:
                    output_lines.append(line)

            # Ensure .env parent dir exists
            env_path.parent.mkdir(parents=True, exist_ok=True)
            env_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")

            # Build output message
            output_lines_msg = ["Set environment variables:"]
            for key, value in sorted(assignments.items()):
                if key in {
                    "MISTRAL_API_KEY",
                    "WIZARD_ADMIN_TOKEN",
                    "WIZARD_KEY",
                    "ANTHROPIC_API_KEY",
                    "OPENAI_API_KEY",
                    "GITHUB_TOKEN",
                    "AWS_SECRET_ACCESS_KEY",
                }:
                    output_lines_msg.append(f"  ✓ {key} = ***")
                else:
                    display = value if len(value) <= 40 else f"{value[:37]}..."
                    output_lines_msg.append(f"  ✓ {key} = {display}")
            output_lines_msg.append(f"\nFile: {env_path}")

            return {
                "status": "success",
                "message": "ENV set",
                "output": "\n".join(output_lines_msg),
                "variables_set": assignments,
                "file_path": str(env_path),
            }
        except Exception as e:
            raise CommandError(
                code="ERR_IO_WRITE_FAILED",
                message=f"Failed to write .env: {e}",
                recovery_hint="Check that .env file is writable",
                level="ERROR",
            )

    def _handle_template(self, params: list[str]) -> dict[str, Any]:
        action = params[0].lower() if params else "list"
        args = params[1:]

        if action == "list":
            family = args[0].strip().lower() if args else None
            if family:
                templates = self.seed_template_service.list_templates(family)
                lines = [f"Template family: {family}"]
                if not templates:
                    lines.append("(no templates found)")
                else:
                    for template in templates:
                        lines.append(f"- {template}")
                return {
                    "status": "success",
                    "family": family,
                    "templates": templates,
                    "output": "\n".join(lines),
                }

            contract = self.seed_template_service.workspace_contract()
            lines = ["Seed template families:"]
            for template_family, payload in contract["families"].items():
                lines.append(
                    f"- {template_family}: {len(payload['templates'])} template(s)"
                )
                for template_name in payload["templates"]:
                    lines.append(f"  - {template_name}")
            return {
                "status": "success",
                "families": contract["families"],
                "output": "\n".join(lines),
            }

        if action == "read":
            if len(args) < 2:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Syntax: UCODE TEMPLATE READ <family> <template>",
                    recovery_hint="Run `UCODE TEMPLATE LIST`",
                    level="INFO",
                )
            snapshot = self.seed_template_service.read_template(args[0], args[1])
            if not snapshot["exists"]:
                raise CommandError(
                    code="ERR_RESOURCE_NOT_FOUND",
                    message=f"Template not found: {args[0]}/{args[1]}",
                    recovery_hint="Run `UCODE TEMPLATE LIST <family>`",
                    level="INFO",
                )
            header = [
                f"Template: {snapshot['family']}/{snapshot['template_name']}",
                f"Source: {snapshot['effective_source']}",
                f"Path: {snapshot['effective_path']}",
                "",
            ]
            return {
                "status": "success",
                "template": snapshot,
                "output": "\n".join(header) + str(snapshot["content"]).rstrip(),
            }

        if action == "duplicate":
            if len(args) < 2:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Syntax: UCODE TEMPLATE DUPLICATE <family> <template> [target_name]",
                    recovery_hint="Run `UCODE TEMPLATE LIST`",
                    level="INFO",
                )
            target_name = args[2] if len(args) > 2 else None
            try:
                result = self.seed_template_service.duplicate_to_user(
                    args[0], args[1], target_name=target_name
                )
            except FileNotFoundError as exc:
                raise CommandError(
                    code="ERR_RESOURCE_NOT_FOUND",
                    message=str(exc),
                    recovery_hint="Run `UCODE TEMPLATE LIST <family>`",
                    level="INFO",
                ) from exc
            except FileExistsError as exc:
                raise CommandError(
                    code="ERR_IO_WRITE_FAILED",
                    message=str(exc),
                    recovery_hint="Choose a different target name",
                    level="INFO",
                ) from exc
            return {
                "status": "success",
                "duplicate": result,
                "output": (
                    f"Duplicated template: {result['family']}/{result['source_template']}\n"
                    f"Local copy: {result['target_path']}"
                ),
            }

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Syntax: UCODE TEMPLATE <LIST [family]|READ <family> <template>|DUPLICATE <family> <template> [target_name]>",
            recovery_hint="Run `UCODE TEMPLATE LIST`",
            level="INFO",
        )

    def _handle_profile(self, params: list[str]) -> dict[str, Any]:
        action = params[0].lower() if params else "list"
        args = params[1:]

        if action == "list":
            profiles = self.profile_service.list_profiles()
            lines = ["Certified release profiles:"]
            for profile in profiles:
                tags = []
                if profile["mandatory"]:
                    tags.append("mandatory")
                if profile["installed"]:
                    tags.append("installed")
                if profile["enabled"]:
                    tags.append("enabled")
                lines.append(f"- {profile['profile_id']} [{', '.join(tags) or 'available'}]")
                lines.append(f"  {profile['summary']}")
            return {"status": "success", "profiles": profiles, "output": "\n".join(lines)}

        if not args:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: UCODE PROFILE <SHOW|INSTALL|ENABLE|DISABLE|VERIFY> <profile>",
                recovery_hint="Run `UCODE PROFILE LIST`",
                level="INFO",
            )

        profile_id = args[0].strip().lower()
        profile = self.profile_service.get_profile(profile_id)
        if not profile:
            raise CommandError(
                code="ERR_COMMAND_NOT_FOUND",
                message=f"Unknown profile: {profile_id}",
                recovery_hint="Run `UCODE PROFILE LIST`",
                level="INFO",
            )

        if action == "show":
            verify = self.profile_service.verify_profile(profile_id)
            lines = [
                f"Profile: {profile['label']} ({profile['profile_id']})",
                profile["summary"],
                f"Mandatory: {'yes' if profile['mandatory'] else 'no'}",
                f"Installed: {'yes' if profile['installed'] else 'no'}",
                f"Enabled: {'yes' if profile['enabled'] else 'no'}",
                f"Components: {', '.join(profile['components']) or '(none)'}",
                f"Extensions: {', '.join(profile['extensions']) or '(none)'}",
                f"Package groups: {', '.join(profile['package_groups']) or '(none)'}",
                f"Healthy: {'yes' if verify['healthy'] else 'no'}",
            ]
            if verify["missing_components"]:
                lines.append(f"Missing components: {', '.join(verify['missing_components'])}")
            if verify["missing_extensions"]:
                lines.append(f"Missing extensions: {', '.join(verify['missing_extensions'])}")
            lines.append(f"Blockers: {', '.join(profile['blockers']) or '(none)'}")
            return {"status": "success", "profile": profile, "verify": verify, "output": "\n".join(lines)}

        if action == "install":
            result = self.profile_service.install_profiles([profile_id])
            return {
                "status": "success",
                "message": f"Installed profile: {profile_id}",
                "result": result,
                "output": f"Installed/enabled profiles: {', '.join(result['enabled'])}",
            }

        if action == "enable":
            result = self.profile_service.set_enabled(profile_id, True)
            return {"status": "success", "profile": result, "output": f"Enabled profile: {profile_id}"}

        if action == "disable":
            try:
                result = self.profile_service.set_enabled(profile_id, False)
            except ValueError as exc:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=str(exc),
                    recovery_hint="Mandatory profiles must remain enabled",
                    level="INFO",
                ) from exc
            return {"status": "success", "profile": result, "output": f"Disabled profile: {profile_id}"}

        if action == "verify":
            verify = self.profile_service.verify_profile(profile_id)
            lines = [
                f"Profile verify: {profile_id}",
                f"Healthy: {'yes' if verify['healthy'] else 'no'}",
                f"Missing components: {', '.join(verify['missing_components']) or '(none)'}",
                f"Missing extensions: {', '.join(verify['missing_extensions']) or '(none)'}",
                f"Blockers: {', '.join(verify['blockers']) or '(none)'}",
            ]
            return {"status": "success", "verify": verify, "output": "\n".join(lines)}

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Syntax: UCODE PROFILE <LIST|SHOW|INSTALL|ENABLE|DISABLE|VERIFY> [profile]",
            recovery_hint="Run `UCODE PROFILE LIST`",
            level="INFO",
        )

    def _handle_operator(self, params: list[str]) -> dict[str, Any]:
        action = params[0].lower() if params else "status"
        args = params[1:]

        if action == "status":
            payload = self.operator_service.status_payload()
            lines = [
                "Operator mode:",
                f"  mode: {payload['session']['mode']}",
                f"  topology: {payload['session']['topology']}",
                f"  enabled profiles: {', '.join(payload['session']['enabled_profiles']) or '(none)'}",
                f"  queued tasks: {payload['session']['queued_tasks']}",
            ]
            for capability in payload["capabilities"]:
                lines.append(
                    f"  capability {capability['name']}: {'ok' if capability['available'] else 'missing'} - {capability['detail']}"
                )
            return {"status": "success", "operator": payload, "output": "\n".join(lines)}

        if action == "queue":
            payload = self.operator_service.status_payload()
            lines = ["Operator queue:"]
            for task in payload["tasks"]:
                lines.append(f"- {task['task_id']} [{task['status']}] {task['title']}")
            return {"status": "success", "tasks": payload["tasks"], "output": "\n".join(lines)}

        if action == "plan":
            prompt = " ".join(args).strip()
            plan = self.operator_service.plan(prompt)
            lines = [
                f"Intent: {plan.intent.label} ({plan.intent.confidence:.2f})",
                f"Reason: {plan.intent.reason}",
                f"Summary: {plan.summary}",
            ]
            if plan.actions:
                lines.append("Actions:")
                for action_item in plan.actions:
                    lines.append(f"- {action_item.command} :: {action_item.description}")
            if plan.tasks:
                lines.append("Tasks:")
                for task in plan.tasks:
                    lines.append(f"- {task.task_id} [{task.status}] {task.title}")
            return {"status": "success", "plan": asdict(plan), "output": "\n".join(lines)}

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Syntax: UCODE OPERATOR <STATUS|PLAN <prompt>|QUEUE>",
            recovery_hint="Run `UCODE OPERATOR STATUS`",
            level="INFO",
        )

    def _handle_extension(self, params: list[str]) -> dict[str, Any]:
        action = params[0].lower() if params else "list"
        args = params[1:]

        if action == "list":
            extensions = self.profile_service.list_extensions()
            lines = ["Official extensions:"]
            for extension in extensions:
                availability = "available" if extension["available"] else "missing"
                lines.append(f"- {extension['extension_id']} [{availability}]")
                lines.append(f"  {extension['summary']}")
            return {"status": "success", "extensions": extensions, "output": "\n".join(lines)}

        if action == "verify" and args:
            try:
                extension = self.profile_service.extension_status(args[0].strip().lower())
            except ValueError as exc:
                raise CommandError(
                    code="ERR_COMMAND_NOT_FOUND",
                    message=str(exc),
                    recovery_hint="Run `UCODE EXTENSION LIST`",
                    level="INFO",
                ) from exc
            lines = [
                f"Extension: {extension['label']} ({extension['extension_id']})",
                f"Profiles: {', '.join(extension['profiles']) or '(none)'}",
                f"Installed: {'yes' if extension.get('installed', extension['available']) else 'no'}",
                f"Enabled: {'yes' if extension.get('enabled', extension['available']) else 'no'}",
                f"Configured: {extension.get('configuration_state', 'configured' if extension['available'] else 'missing')}",
                f"Health: {'healthy' if extension.get('healthy') else ('degraded' if extension.get('degraded') else 'pending')}",
                f"Path: {extension['path']}",
            ]
            if extension.get("wizard_route"):
                lines.append(f"Wizard route: {extension['wizard_route']}")
            if extension.get("capabilities"):
                enabled_caps = [
                    name if ok else f"{name}-pending"
                    for name, ok in extension["capabilities"].items()
                ]
                lines.append(f"Capabilities: {', '.join(enabled_caps)}")
            if extension.get("missing_prerequisites"):
                lines.append(
                    "Missing prerequisites: "
                    + ", ".join(extension["missing_prerequisites"])
                )
            return {"status": "success", "extension": extension, "output": "\n".join(lines)}

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Syntax: UCODE EXTENSION <LIST|VERIFY> [extension]",
            recovery_hint="Run `UCODE EXTENSION LIST`",
            level="INFO",
        )

    def _handle_package(self, params: list[str]) -> dict[str, Any]:
        action = params[0].lower() if params else "list"
        args = params[1:]
        groups = self.profile_service.list_package_groups()

        if action == "list":
            lines = ["Package groups:"]
            for group in groups:
                state = "active" if group["active"] else "inactive"
                lines.append(f"- {group['package_id']} [{state}]")
                lines.append(f"  {group['summary']}")
                lines.append(f"  Repos: {', '.join(group['repos']) or '(none)'}")
            return {"status": "success", "packages": groups, "output": "\n".join(lines)}

        if action == "verify" and args:
            package_id = args[0].strip().lower()
            package = next((item for item in groups if item["package_id"] == package_id), None)
            if not package:
                raise CommandError(
                    code="ERR_COMMAND_NOT_FOUND",
                    message=f"Unknown package group: {package_id}",
                    recovery_hint="Run `UCODE PACKAGE LIST`",
                    level="INFO",
                )
            lines = [
                f"Package group: {package['label']} ({package['package_id']})",
                package["summary"],
                f"Active: {'yes' if package['active'] else 'no'}",
                f"Profiles: {', '.join(package['profiles']) or '(none)'}",
                f"Repos: {', '.join(package['repos']) or '(none)'}",
            ]
            return {"status": "success", "package": package, "output": "\n".join(lines)}

        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Syntax: UCODE PACKAGE <LIST|VERIFY> [group]",
            recovery_hint="Run `UCODE PACKAGE LIST`",
            level="INFO",
        )

    def _handle_rebaseline_repair(self, params: list[str]) -> dict[str, Any]:
        action = params[0].lower() if params else "status"
        if action != "status":
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Syntax: UCODE REPAIR STATUS",
                recovery_hint="Run `UCODE REPAIR STATUS`",
                level="INFO",
            )
        topology = self.profile_service.topology_summary()
        profiles = self.profile_service.list_profiles()
        lines = [
            "Rebaseline repair contracts:",
            f"- topology: {topology['mode']} :: {topology['summary']}",
            "- verify certified profiles before repair execution",
        ]
        for profile in profiles:
            verify = self.profile_service.verify_profile(profile["profile_id"])
            state = "ok" if verify["healthy"] else "attention"
            lines.append(
                f"- {profile['profile_id']} [{state}] missing components={len(verify['missing_components'])}, missing extensions={len(verify['missing_extensions'])}"
            )
        lines.append("Suggested sequence: HEALTH -> REPAIR STATUS -> UCODE PROFILE VERIFY <profile>")
        return {"status": "success", "profiles": profiles, "output": "\n".join(lines)}

    def _seed_demo_assets(self, *, overwrite: bool) -> None:
        demo_seeds = {
            "parse_file.txt": "Demo: parse_file\nUse: UCODE DOCS --query parse file\n",
            "system_check.txt": "Demo: system_check\nUse: UCODE SYSTEM INFO\n",
            "format_converter.txt": "Demo: format_converter\nUse: UCODE DOCS --section examples\n",
        }
        for filename, content in demo_seeds.items():
            path = self.demos_root / filename
            if overwrite or not path.exists():
                path.write_text(content, encoding="utf-8")

    def _seed_doc_assets(self, *, overwrite: bool) -> None:
        docs_seeds = {
            "ucode-reference.md": (
                "# uCode Command Reference\n\n"
                "Core: `UCODE DEMO LIST`, `UCODE SYSTEM INFO`, `UCODE CAPABILITIES`\n"
            ),
            "udos-workflows.md": (
                "# uDOS Workflows\n\n"
                "Offline flow: Demo -> Docs -> System introspection -> Capability checks\n"
            ),
            "troubleshooting.md": (
                "# Troubleshooting\n\n"
                "- No network: use offline mode commands.\n"
                "- Refresh resources: `UCODE UPDATE` when online.\n"
            ),
        }
        for filename, content in docs_seeds.items():
            path = self.docs_root / filename
            if overwrite or not path.exists():
                path.write_text(content, encoding="utf-8")

        for source, output_name in self._bundled_doc_sources():
            if not source.exists():
                continue
            destination = self.docs_root / output_name
            if overwrite or not destination.exists():
                destination.write_text(
                    source.read_text(encoding="utf-8", errors="ignore"),
                    encoding="utf-8",
                )

    def _bundled_doc_sources(self) -> list[tuple[Path, str]]:
        return [
            (
                self.repo_root / "docs" / "howto" / "UCODE-COMMAND-REFERENCE.md",
                "UCODE-COMMAND-REFERENCE.md",
            ),
            (
                self.repo_root / "docs" / "specs" / "MINIMUM-SPEC-VIBE-CLI-UCODE.md",
                "MINIMUM-SPEC-VIBE-CLI-UCODE.md",
            ),
            (
                self.repo_root / "docs" / "troubleshooting" / "README.md",
                "TROUBLESHOOTING-README.md",
            ),
        ]

    def _offline_fallback_order(self) -> list[str]:
        return [
            "UCODE DEMO LIST",
            "UCODE DOCS --query <text>",
            "UCODE SYSTEM INFO",
            "UCODE CAPABILITIES --filter <text>",
        ]

    def _ensure_plugins_manifest(self) -> None:
        if self.plugins_manifest_path.exists():
            return
        self._write_installed_plugins([])

    def _load_installed_plugins(self) -> list[dict[str, Any]]:
        self._ensure_plugins_manifest()
        try:
            payload = json.loads(self.plugins_manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(payload, dict):
            return []
        plugins = payload.get("plugins")
        if not isinstance(plugins, list):
            return []
        normalized: list[dict[str, Any]] = []
        for item in plugins:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip().lower()
            if not name:
                continue
            normalized.append({
                "name": name,
                "status": str(item.get("status", "installed")),
                "source": str(item.get("source", "local-scaffold")),
                "installed_at": str(item.get("installed_at", "")),
                "capabilities": [
                    str(cap) for cap in item.get("capabilities", [f"plugin.{name}"])
                ],
            })
        return normalized

    def _write_installed_plugins(self, plugins: list[dict[str, Any]]) -> None:
        payload = {"updated_at": datetime.now(UTC).isoformat(), "plugins": plugins}
        self.plugins_manifest_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )

    def _plugin_capabilities(self) -> list[_Capability]:
        plugins = self._load_installed_plugins()
        return [
            _Capability(
                name=f"plugin.{plugin['name']}",
                status=plugin["status"],
                detail=f"Installed via {plugin['source']}",
                profiles={"full", "wizard"},
            )
            for plugin in plugins
        ]

    def _normalize_plugin_name(self, raw_name: str) -> str:
        return raw_name.strip().lower()

    def _create_offline_bundle_manifest(self) -> dict[str, Any]:
        files = sorted([*self.demos_root.glob("*.txt"), *self.docs_root.glob("*.*")])
        entries = [self._bundle_entry(path) for path in files]
        signing_payload = self._bundle_signing_payload(entries)
        signature = hmac.new(
            key=self._bundle_signing_key().encode("utf-8"),
            msg=signing_payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        manifest = {
            "bundle_id": f"offline-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
            "created_at": datetime.now(UTC).isoformat(),
            "algorithm": "sha256+hmac-sha256",
            "files": entries,
            "signature": signature,
        }
        verified = self._verify_bundle_signature(manifest)
        manifest["verification"] = {
            "verified": verified,
            "checked_at": datetime.now(UTC).isoformat(),
        }
        self.bundle_manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
        return manifest

    def _bundle_entry(self, path: Path) -> dict[str, Any]:
        content = path.read_bytes()
        relative = path.relative_to(self.ucode_root).as_posix()
        return {
            "path": relative,
            "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content),
        }

    def _bundle_signing_payload(self, entries: list[dict[str, Any]]) -> str:
        normalized = [
            {"path": entry["path"], "sha256": entry["sha256"], "size": entry["size"]}
            for entry in entries
        ]
        return json.dumps(normalized, separators=(",", ":"), sort_keys=True)

    def _bundle_signing_key(self) -> str:
        from core.services.unified_config_loader import get_config

        env_key = get_config("UCODE_BUNDLE_SIGNING_KEY", "").strip()
        if env_key:
            return env_key
        if self.bundle_signing_key_path.exists():
            return self.bundle_signing_key_path.read_text(encoding="utf-8").strip()
        generated = secrets.token_hex(32)
        self.bundle_signing_key_path.write_text(generated, encoding="utf-8")
        return generated

    def _verify_bundle_signature(self, manifest: dict[str, Any]) -> bool:
        files = manifest.get("files")
        signature = manifest.get("signature")
        if not isinstance(files, list) or not isinstance(signature, str):
            return False
        expected_payload = self._bundle_signing_payload([
            entry for entry in files if isinstance(entry, dict)
        ])
        expected_signature = hmac.new(
            key=self._bundle_signing_key().encode("utf-8"),
            msg=expected_payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return False
        for entry in files:
            if not isinstance(entry, dict):
                return False
            relative = str(entry.get("path", ""))
            digest = str(entry.get("sha256", ""))
            if not relative or not digest:
                return False
            target = self.ucode_root / relative
            if not target.exists():
                return False
            current = hashlib.sha256(target.read_bytes()).hexdigest()
            if not hmac.compare_digest(current, digest):
                return False
        return True

    def _ensure_metrics_summary(self) -> None:
        if self.metrics_summary_path.exists():
            return
        payload = {
            "updated_at": datetime.now(UTC).isoformat(),
            "last_event_at": None,
            "total_events": 0,
            "offline_events": 0,
            "fallback_events": 0,
            "actions": {},
            "statuses": {},
        }
        self.metrics_summary_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )

    def _load_metrics_summary(self) -> dict[str, Any]:
        self._ensure_metrics_summary()
        try:
            payload = json.loads(self.metrics_summary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {
                "updated_at": datetime.now(UTC).isoformat(),
                "last_event_at": None,
                "total_events": 0,
                "offline_events": 0,
                "fallback_events": 0,
                "actions": {},
                "statuses": {},
            }
        if not isinstance(payload, dict):
            return {
                "updated_at": datetime.now(UTC).isoformat(),
                "last_event_at": None,
                "total_events": 0,
                "offline_events": 0,
                "fallback_events": 0,
                "actions": {},
                "statuses": {},
            }
        payload.setdefault("actions", {})
        payload.setdefault("statuses", {})
        payload.setdefault("total_events", 0)
        payload.setdefault("offline_events", 0)
        payload.setdefault("fallback_events", 0)
        return payload

    def _read_metrics_events_tail(self, limit: int) -> list[dict[str, Any]]:
        if not self.metrics_events_path.exists():
            return []
        try:
            lines = [
                line.strip()
                for line in self.metrics_events_path.read_text(
                    encoding="utf-8"
                ).splitlines()
                if line.strip()
            ]
        except OSError:
            return []
        tail = lines[-limit:]
        events: list[dict[str, Any]] = []
        for line in tail:
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                events.append(payload)
        return events

    def _record_usage_metric(
        self,
        *,
        action: str,
        result: dict[str, Any] | None,
        started_at: datetime,
        error: CommandError | None = None,
    ) -> None:
        finished_at = datetime.now(UTC)
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)
        status = "error" if error else str((result or {}).get("status", "success"))
        network = self._extract_network_state(result)
        fallback_event = action in {"demo", "docs", "system"}
        event = {
            "timestamp": finished_at.isoformat(),
            "action": action,
            "status": status,
            "duration_ms": duration_ms,
            "network": network,
            "fallback_event": fallback_event,
        }
        if error:
            event["error_code"] = error.code
            event["error_message"] = error.message

        self.metrics_events_path.parent.mkdir(parents=True, exist_ok=True)
        with self.metrics_events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

        summary = self._load_metrics_summary()
        summary["updated_at"] = finished_at.isoformat()
        summary["last_event_at"] = finished_at.isoformat()
        summary["total_events"] = int(summary.get("total_events", 0)) + 1
        if network == "offline":
            summary["offline_events"] = int(summary.get("offline_events", 0)) + 1
        if fallback_event:
            summary["fallback_events"] = int(summary.get("fallback_events", 0)) + 1
        actions = summary.get("actions", {})
        statuses = summary.get("statuses", {})
        actions[action] = int(actions.get(action, 0)) + 1
        statuses[status] = int(statuses.get(status, 0)) + 1
        summary["actions"] = actions
        summary["statuses"] = statuses
        self.metrics_summary_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
        )

    def _extract_network_state(self, result: dict[str, Any] | None) -> str:
        if not isinstance(result, dict):
            return "unknown"
        if isinstance(result.get("network"), str):
            return str(result["network"])
        updated = result.get("updated")
        if isinstance(updated, dict) and isinstance(updated.get("network"), str):
            return str(updated["network"])
        capabilities = result.get("capabilities")
        if isinstance(capabilities, list):
            for entry in capabilities:
                if not isinstance(entry, dict):
                    continue
                if entry.get("name") == "cloud.ai":
                    return "online" if entry.get("status") == "ready" else "offline"
        return "unknown"

    def _extract_opt(self, params: list[str], flag: str) -> str | None:
        for idx, token in enumerate(params):
            if token == flag and idx + 1 < len(params):
                return params[idx + 1]
            if token.startswith(f"{flag}="):
                return token.split("=", 1)[1]
        return None

    def _extract_profile_filter(self, filt: str | None) -> str | None:
        if not filt:
            return None
        normalized = filt.strip().lower()
        if normalized in {"core", "full", "wizard"}:
            return normalized
        if normalized.startswith("profile:"):
            profile = normalized.split(":", 1)[1].strip()
            if profile in {"core", "full", "wizard"}:
                return profile
        return None

    def _network_reachable(self) -> bool:
        try:
            proc = subprocess.run(
                ["ping", "-c", "1", "-W", "1", "1.1.1.1"],
                check=False,
                capture_output=True,
                text=True,
                timeout=2.0,
            )
        except Exception:
            return False
        return proc.returncode == 0
