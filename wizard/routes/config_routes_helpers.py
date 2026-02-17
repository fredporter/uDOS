"""
Helpers for config route handlers.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

from core.services.integration_registry import get_assistant_config_key_map
from wizard.services.path_utils import get_memory_dir, get_repo_root
from wizard.services.wizard_config import load_wizard_config_data, save_wizard_config_data


class ConfigRouteHelpers:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config_files = {
            "assistant_keys": "assistant_keys.json",
            "github_keys": "github_keys.json",
            "oauth": "oauth_providers.json",
            "wizard": "wizard.json",
        }
        self.label_map = {
            "assistant_keys": "Assistant Keys",
            "github_keys": "GitHub Keys",
            "oauth": "OAuth Providers",
            "wizard": "Wizard",
        }

    def load_json_config(
        self, path: Path, default: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        if not path.exists():
            return default or {}, None
        try:
            return json.loads(path.read_text()), None
        except Exception as exc:
            return default or {}, str(exc)

    def save_json_config(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2))

    def load_wizard_config(self) -> Dict[str, Any]:
        wizard_path = self.config_path / "wizard.json"
        return load_wizard_config_data(path=wizard_path)

    def save_wizard_config(self, config: Dict[str, Any]) -> None:
        wizard_path = self.config_path / "wizard.json"
        save_wizard_config_data(config, path=wizard_path)

    def _enable_provider(self, config: Dict[str, Any], provider_id: str) -> bool:
        enabled = config.get("enabled_providers") or []
        if provider_id not in enabled:
            enabled.append(provider_id)
            config["enabled_providers"] = enabled
            return True
        return False

    def _get_nested(self, data: Dict[str, Any], path: List[str]) -> Optional[Any]:
        current: Any = data
        for part in path:
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

    def sync_wizard_from_config(self, file_id: str, content: Dict[str, Any]) -> bool:
        if file_id == "wizard":
            return False

        config = self.load_wizard_config()
        changed = False

        if file_id == "github_keys":
            has_key = bool(
                self._get_nested(content, ["tokens", "default", "key_id"])
                or self._get_nested(content, ["webhooks", "secret_key_id"])
            )
            if has_key:
                changed |= self._enable_provider(config, "github")
                if not config.get("github_push_enabled"):
                    config["github_push_enabled"] = True
                    changed = True
        elif file_id == "assistant_keys":
            ai_key_map = get_assistant_config_key_map()
            for key, provider_id in ai_key_map.items():
                if content.get(key):
                    changed |= self._enable_provider(config, provider_id)
            if any(content.get(k) for k in ai_key_map.keys()):
                if not config.get("ok_gateway_enabled"):
                    config["ok_gateway_enabled"] = True
                    changed = True

        if changed:
            self.save_wizard_config(config)
        return changed

    def _display_label(self, file_id: str, filename: str) -> str:
        return self.label_map.get(
            file_id, filename.replace("_", " ").replace(".json", "").title()
        )

    def _paths_for_file(self, file_id: str) -> Tuple[str, Path, Path, Path]:
        if file_id not in self.config_files:
            raise HTTPException(status_code=400, detail=f"Unknown config file: {file_id}")
        filename = self.config_files[file_id]
        file_path = self.config_path / filename
        example_path = self.config_path / filename.replace(".json", ".example.json")
        template_path = self.config_path / filename.replace(".json", ".template.json")
        return filename, file_path, example_path, template_path

    def list_config_files(self) -> List[Dict[str, Any]]:
        files: List[Dict[str, Any]] = []
        for file_id, filename in self.config_files.items():
            file_path = self.config_path / filename
            label = self._display_label(file_id, filename)
            if file_path.exists():
                _content, error = self.load_json_config(file_path, default={})
                item = {
                    "id": file_id,
                    "label": label,
                    "filename": filename,
                    "exists": True,
                    "is_example": filename.endswith(".example.json"),
                    "is_template": filename.endswith(".template.json"),
                }
                if error:
                    item["error"] = "Invalid JSON"
                files.append(item)
                continue

            example_path = self.config_path / filename.replace(".json", ".example.json")
            template_path = self.config_path / filename.replace(".json", ".template.json")
            if example_path.exists():
                files.append(
                    {
                        "id": file_id,
                        "label": label,
                        "filename": filename,
                        "exists": False,
                        "is_example": True,
                        "is_template": False,
                        "actual_file": example_path.name,
                    }
                )
            elif template_path.exists():
                files.append(
                    {
                        "id": file_id,
                        "label": label,
                        "filename": filename,
                        "exists": False,
                        "is_example": False,
                        "is_template": True,
                        "actual_file": template_path.name,
                    }
                )
            else:
                files.append(
                    {
                        "id": file_id,
                        "label": label,
                        "filename": filename,
                        "exists": False,
                        "is_example": False,
                        "is_template": False,
                        "actual_file": None,
                    }
                )
        return files

    def load_config_payload(self, file_id: str) -> Dict[str, Any]:
        filename, file_path, example_path, template_path = self._paths_for_file(file_id)

        if file_path.exists():
            content, error = self.load_json_config(file_path, default=None)
            if error:
                raise HTTPException(status_code=500, detail=f"Invalid JSON in {filename}: {error}")
            return {
                "id": file_id,
                "filename": filename,
                "content": self._hydrate_file_locations(file_id, content),
                "is_example": False,
                "is_template": False,
            }

        if example_path.exists():
            content, error = self.load_json_config(example_path, default=None)
            if error:
                raise HTTPException(status_code=500, detail=f"Invalid JSON in {example_path.name}: {error}")
            return {
                "id": file_id,
                "filename": filename,
                "content": self._hydrate_file_locations(file_id, content),
                "is_example": True,
                "is_template": False,
                "message": "Using example file. Save to create actual config.",
            }

        if template_path.exists():
            content, error = self.load_json_config(template_path, default=None)
            if error:
                raise HTTPException(status_code=500, detail=f"Invalid JSON in {template_path.name}: {error}")
            return {
                "id": file_id,
                "filename": filename,
                "content": content,
                "is_example": False,
                "is_template": True,
                "message": "Using template file. Save to create actual config.",
            }

        raise HTTPException(status_code=404, detail=f"Config file not found: {file_id}")

    def save_config_payload(self, file_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        filename, file_path, _example_path, _template_path = self._paths_for_file(file_id)
        content = body.get("content", {})
        if not isinstance(content, dict):
            raise HTTPException(status_code=400, detail="Config content must be a JSON object")

        self.save_json_config(file_path, content)
        wizard_synced = self.sync_wizard_from_config(file_id, content)
        return {
            "success": True,
            "message": f"Saved {filename}",
            "file": filename,
            "path": str(file_path),
            "wizard_config_updated": wizard_synced,
        }

    def reset_config(self, file_id: str) -> Dict[str, Any]:
        filename, file_path, _example_path, _template_path = self._paths_for_file(file_id)
        if file_path.exists():
            file_path.unlink()
            return {"success": True, "message": f"Reset {filename} to example/template"}
        raise HTTPException(status_code=404, detail=f"No config file to reset: {filename}")

    def get_example_or_template(self, file_id: str) -> Dict[str, Any]:
        filename, _file_path, example_path, template_path = self._paths_for_file(file_id)
        if example_path.exists():
            content, error = self.load_json_config(example_path, default=None)
            if error:
                raise HTTPException(status_code=500, detail=f"Invalid JSON: {error}")
            return {
                "id": file_id,
                "filename": filename,
                "example_file": example_path.name,
                "content": content,
            }
        if template_path.exists():
            content, error = self.load_json_config(template_path, default=None)
            if error:
                raise HTTPException(status_code=500, detail=f"Invalid JSON: {error}")
            return {
                "id": file_id,
                "filename": filename,
                "template_file": template_path.name,
                "content": content,
            }
        raise HTTPException(status_code=404, detail=f"No example/template found for {filename}")

    def export_configs(self, body: Dict[str, Any]) -> Dict[str, Any]:
        export_dir = get_repo_root() / "memory" / "config_exports"
        file_ids = body.get("file_ids", [])
        include_secrets = body.get("include_secrets", False)
        if not file_ids:
            raise HTTPException(status_code=400, detail="No config files specified for export")

        invalid_ids = [fid for fid in file_ids if fid not in self.config_files]
        if invalid_ids:
            raise HTTPException(status_code=400, detail=f"Invalid config file IDs: {', '.join(invalid_ids)}")

        export_dir.mkdir(parents=True, exist_ok=True)
        export_data: Dict[str, Any] = {
            "export_timestamp": datetime.utcnow().isoformat() + "Z",
            "exported_from": "uDOS Wizard Server",
            "version": "1.0",
            "include_secrets": include_secrets,
            "configs": {},
        }
        has_secrets = False

        for file_id in file_ids:
            filename, file_path, example_path, template_path = self._paths_for_file(file_id)
            content = None
            for candidate in [file_path, example_path, template_path]:
                if candidate.exists():
                    loaded, error = self.load_json_config(candidate, default=None)
                    if not error:
                        content = loaded
                        break
            if content is None:
                continue
            if not include_secrets and file_id != "wizard":
                has_secrets = True
                content = {k: "***REDACTED***" for k in content.keys()}
            export_data["configs"][file_id] = {"filename": filename, "content": content}

        if not export_data["configs"]:
            raise HTTPException(status_code=404, detail="No config files found to export")

        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
        export_filename = f"udos-config-export-{timestamp}.json"
        export_path = export_dir / export_filename
        export_path.write_text(json.dumps(export_data, indent=2))

        warning = None
        if has_secrets or include_secrets:
            warning = "⚠️ This file contains secrets or redacted values. Keep it secure and never commit to git!"

        return {
            "success": True,
            "filename": export_filename,
            "path": str(export_path),
            "size": export_path.stat().st_size,
            "timestamp": export_data["export_timestamp"],
            "exported_configs": list(export_data["configs"].keys()),
            "include_secrets": include_secrets,
            "warning": warning,
        }

    def preview_import(self, import_data: Dict[str, Any]) -> Dict[str, Any]:
        if "configs" not in import_data:
            raise ValueError("Invalid export file: missing 'configs' field")
        if not isinstance(import_data["configs"], dict):
            raise ValueError("Invalid export file: 'configs' must be an object")

        conflicts = []
        preview = {}
        for file_id, config_info in import_data["configs"].items():
            if file_id not in self.config_files:
                continue
            filename, file_path, _example_path, _template_path = self._paths_for_file(file_id)
            if file_path.exists():
                conflicts.append(file_id)
            preview[file_id] = {
                "filename": config_info.get("filename", filename),
                "has_content": "content" in config_info and bool(config_info["content"]),
                "is_redacted": all(
                    v == "***REDACTED***"
                    for v in config_info.get("content", {}).values()
                    if isinstance(v, str)
                ),
            }
        return {
            "success": True,
            "preview": preview,
            "conflicts": conflicts,
            "timestamp": import_data.get("export_timestamp"),
            "exported_from": import_data.get("exported_from"),
            "message": "Preview: Use POST /api/config/import/apply to import these configs",
        }

    def import_chunked(
        self,
        import_data: Dict[str, Any],
        overwrite_conflicts: bool = False,
        file_ids_to_import: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if "configs" not in import_data:
            raise ValueError("Invalid export file: missing 'configs' field")

        imported = []
        skipped = []
        errors = []

        for file_id, config_info in import_data["configs"].items():
            if file_id not in self.config_files:
                continue
            if file_ids_to_import and file_id not in file_ids_to_import:
                continue

            filename, file_path, _example_path, _template_path = self._paths_for_file(file_id)
            content_to_write = config_info.get("content", {})
            is_redacted = all(
                v == "***REDACTED***"
                for v in content_to_write.values()
                if isinstance(v, str)
            )
            if is_redacted:
                skipped.append(
                    {
                        "file_id": file_id,
                        "reason": "Config was redacted during export. Use full export to transfer secrets.",
                    }
                )
                continue
            if file_path.exists() and not overwrite_conflicts:
                skipped.append(
                    {
                        "file_id": file_id,
                        "reason": "Config already exists. Use overwrite_conflicts=true to replace.",
                    }
                )
                continue
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json.dumps(content_to_write, indent=2))
                imported.append(file_id)
            except Exception as exc:
                errors.append({"file_id": file_id, "error": str(exc)})

        return {
            "success": len(errors) == 0,
            "imported": imported,
            "skipped": skipped,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": (
                f"Imported {len(imported)} config(s)"
                if imported
                else "No configs imported"
            ),
        }

    def _hydrate_file_locations(self, file_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        if file_id != "wizard":
            return content
        content.setdefault("file_locations", {})
        content["file_locations"].setdefault("memory_root", "memory")
        content["file_locations"].setdefault("repo_root", "auto")
        content["file_locations"]["repo_root_actual"] = str(get_repo_root())
        content["file_locations"]["memory_root_actual"] = str(get_memory_dir())
        return content
