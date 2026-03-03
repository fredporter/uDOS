"""Empire extension contract service for Wizard."""

from __future__ import annotations

import importlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("empire-extension", category="extensions")


class EmpireExtensionService:
    """Resolve Empire extension state and provide canonical helper operations."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.extensions_root = self.repo_root / "extensions"
        self.extension_root = self.extensions_root / "empire"
        self.legacy_nested_root = self.extension_root / "empire"
        self.data_root = self.extension_root / "data"
        self.config_root = self.extension_root / "config"
        self.templates_root = self.extension_root / "templates"
        self.mappings_root = self.templates_root / "mappings"
        self.workflows_root = self.extension_root / "workflows"
        self.db_path = self.data_root / "empire.db"
        self.state_path = self.repo_root / "memory" / "ucode" / "extensions-state.json"

    def ensure_import_path(self) -> None:
        extensions_root = str(self.extensions_root)
        if extensions_root not in sys.path:
            sys.path.insert(0, extensions_root)

    def extension_installed(self) -> bool:
        required = (
            self.extension_root / "__init__.py",
            self.extension_root / "services" / "__init__.py",
            self.extension_root / "api" / "__init__.py",
            self.extension_root / "src" / "spine.py",
        )
        return self.extension_root.is_dir() and all(path.exists() for path in required)

    def _load_state(self) -> dict[str, dict[str, Any]]:
        default = {"empire": {"enabled": self.extension_installed()}}
        if not self.state_path.exists():
            self._save_state(default)
            return default
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self._save_state(default)
            return default
        if not isinstance(payload, dict):
            self._save_state(default)
            return default
        extension_state = payload.get("empire")
        if not isinstance(extension_state, dict):
            payload["empire"] = {"enabled": self.extension_installed()}
        if "enabled" not in payload["empire"]:
            payload["empire"]["enabled"] = self.extension_installed()
        return payload

    def _save_state(self, state: dict[str, dict[str, Any]]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def enabled(self) -> bool:
        return bool(self._load_state().get("empire", {}).get("enabled", False))

    def set_enabled(self, enabled: bool) -> dict[str, Any]:
        state = self._load_state()
        state.setdefault("empire", {})
        state["empire"]["enabled"] = bool(enabled)
        self._save_state(state)
        return self.status_payload()

    def _read_secrets(self) -> dict[str, Any]:
        secrets_path = self.config_root / "empire_secrets.json"
        if not secrets_path.exists():
            return {}
        try:
            payload = json.loads(secrets_path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except json.JSONDecodeError:
            return {}

    def _decode_json_value(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        stripped = value.strip()
        if not stripped:
            return value
        if stripped[0] not in "[{":
            return value
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return value

    def _normalize_row_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        payload = dict(row)
        for key in ("metadata", "raw_json", "user_info", "config_json", "request_payload", "response_payload"):
            if key in payload:
                payload[key] = self._decode_json_value(payload[key])
        return payload

    def _oauth_connection_status(self) -> dict[str, Any]:
        try:
            from wizard.services.oauth_manager import get_oauth_manager, OAuthProvider

            manager = get_oauth_manager()
            connection = manager.get_connection(OAuthProvider.GOOGLE)
        except Exception as exc:
            logger.warning("Failed to resolve Wizard OAuth state for Empire: %s", exc)
            return {"available": False}

        token = connection.token
        user_info = token.user_info if token else {}
        return {
            "available": True,
            "status": connection.status.value,
            "user": connection.user_display,
            "provider_name": connection.display_name,
            "scopes": list(token.scopes) if token else [],
            "expires_at": token.expires_at if token else None,
            "user_info": user_info,
        }

    def configuration_state(self) -> str:
        if not self.extension_installed():
            return "missing"
        secrets = self._read_secrets()
        if secrets.get("empire_api_token"):
            return "configured"
        return "partial"

    def capabilities(self) -> dict[str, bool]:
        secrets = self._read_secrets()
        return {
            "gui": self.extension_installed(),
            "imports": (self.extension_root / "scripts" / "ingest").exists(),
            "templates": self.templates_root.exists() or self.extension_installed(),
            "google": bool(
                secrets.get("google_gmail_credentials_path")
                or secrets.get("google_gmail_token_path")
                or secrets.get("google_places_api_key")
            ),
            "hubspot": bool(secrets.get("hubspot_private_app_token")),
            "webhooks": True,
        }

    def missing_prerequisites(self) -> list[str]:
        missing: list[str] = []
        if not self.extension_installed():
            missing.append("extension-root")
            return missing
        if not (self.extension_root / "__init__.py").exists():
            missing.append("package-init")
        if not self.db_path.exists():
            missing.append("database")
        if self.configuration_state() != "configured":
            missing.append("api-token")
        if self.legacy_nested_root.exists():
            missing.append("legacy-nested-tree")
        return missing

    def _database_ok(self) -> bool:
        if not self.db_path.exists():
            return False
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                row = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='records'"
                ).fetchone()
            return row is not None
        except sqlite3.Error:
            return False

    def _version(self) -> str:
        version_path = self.extension_root / "version.json"
        if version_path.exists():
            try:
                payload = json.loads(version_path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    return str(payload.get("version", "dev"))
            except json.JSONDecodeError:
                return "dev"
        return "dev"

    def status_payload(self) -> dict[str, Any]:
        installed = self.extension_installed()
        enabled = self.enabled() if installed else False
        configuration_state = self.configuration_state()
        configured = configuration_state == "configured"
        healthy = installed and enabled and self._database_ok()
        degraded = (installed and enabled and not healthy) or (
            installed and configuration_state != "configured"
        )
        return {
            "extension_id": "empire",
            "kind": "official",
            "bundled": True,
            "installed": installed,
            "available": installed,
            "enabled": enabled,
            "configured": configured,
            "configuration_state": configuration_state,
            "healthy": healthy,
            "degraded": degraded,
            "version": self._version(),
            "path": str(self.extension_root),
            "wizard_route": "#empire",
            "legacy_nested_tree": self.legacy_nested_root.exists(),
            "db_path": str(self.db_path),
            "capabilities": self.capabilities(),
            "missing_prerequisites": self.missing_prerequisites(),
        }

    def health_payload(self) -> dict[str, Any]:
        payload = self.status_payload()
        payload["ok"] = payload["installed"] and payload["enabled"] and payload["healthy"]
        return payload

    def _import_module(self, name: str):
        self.ensure_import_path()
        return importlib.import_module(name)

    def load_overview(self) -> dict[str, Any]:
        self.mappings_root.mkdir(parents=True, exist_ok=True)
        if not self.extension_installed():
            return {"counts": {}, "events": []}
        overview = self._import_module("empire.services.overview_service")
        return overview.load_overview(self.db_path)

    def _query(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        if not self.db_path.exists():
            return []
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
        return [self._normalize_row_payload(dict(row)) for row in rows]

    def list_records(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._query(
            """
            SELECT record_id, email, firstname, lastname, company, jobtitle,
                   phone, city, state, country, lastmodifieddate
            FROM records
            ORDER BY lastmodifieddate DESC
            LIMIT ?
            """,
            (limit,),
        )

    def list_companies(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._query(
            """
            SELECT company_id, name, domain, phone, city, state, country, source
            FROM companies
            ORDER BY name ASC
            LIMIT ?
            """,
            (limit,),
        )

    def list_tasks(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._query(
            """
            SELECT task_id, title, category, source, source_ref, created_at, status, notes, record_id
            FROM tasks
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )

    def list_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._query(
            """
            SELECT event_id, record_id, event_type, occurred_at, subject, notes
            FROM events
            ORDER BY occurred_at DESC
            LIMIT ?
            """,
            (limit,),
        )

    def list_sources(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._query(
            """
            SELECT source_id, source_key, label, created_at
            FROM sources
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )

    def list_templates(self) -> list[dict[str, str]]:
        self.mappings_root.mkdir(parents=True, exist_ok=True)
        items: list[dict[str, str]] = []
        for path in sorted(self.mappings_root.glob("*.md")):
            items.append(
                {
                    "name": path.name,
                    "path": str(path.relative_to(self.extension_root)),
                    "kind": "mapping",
                }
            )
        return items

    def list_documents(self, limit: int = 100) -> list[dict[str, Any]]:
        storage = self._import_module("empire.services.storage")
        return [self._normalize_row_payload(row) for row in storage.list_documents(self.db_path, limit=limit)]

    def list_import_jobs(self, limit: int = 100) -> list[dict[str, Any]]:
        storage = self._import_module("empire.services.storage")
        return [self._normalize_row_payload(row) for row in storage.list_import_jobs(self.db_path, limit=limit)]

    def list_connector_jobs(
        self,
        *,
        connector: str | None = None,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        storage = self._import_module("empire.services.storage")
        jobs = storage.list_sync_jobs(self.db_path, limit=limit, connector=connector)
        return [self._normalize_row_payload(row) for row in jobs]

    def get_sync_job(self, sync_job_id: str) -> dict[str, Any] | None:
        storage = self._import_module("empire.services.storage")
        payload = storage.get_sync_job(sync_job_id, self.db_path)
        return self._normalize_row_payload(payload) if payload else None

    def get_import_job(self, job_id: str) -> dict[str, Any] | None:
        storage = self._import_module("empire.services.storage")
        payload = storage.get_import_job(job_id, self.db_path)
        return self._normalize_row_payload(payload) if payload else None

    def list_webhook_mappings(self, limit: int = 100) -> list[dict[str, Any]]:
        storage = self._import_module("empire.services.storage")
        return [self._normalize_row_payload(row) for row in storage.list_webhook_mappings(self.db_path, limit=limit)]

    def get_webhook_mapping(self, mapping_id: str) -> dict[str, Any] | None:
        storage = self._import_module("empire.services.storage")
        payload = storage.get_webhook_mapping(mapping_id, self.db_path)
        return self._normalize_row_payload(payload) if payload else None

    def list_webhook_deliveries(
        self,
        *,
        limit: int = 100,
        mapping_id: str | None = None,
    ) -> list[dict[str, Any]]:
        storage = self._import_module("empire.services.storage")
        return [
            self._normalize_row_payload(row)
            for row in storage.list_webhook_deliveries(self.db_path, limit=limit, mapping_id=mapping_id)
        ]

    def read_template(self, relative_path: str) -> dict[str, str]:
        self.mappings_root.mkdir(parents=True, exist_ok=True)
        safe_path = (self.extension_root / relative_path).resolve()
        if self.extension_root.resolve() not in safe_path.parents and safe_path != self.extension_root.resolve():
            raise ValueError("Template path must stay within Empire extension root")
        return {
            "path": str(safe_path.relative_to(self.extension_root)),
            "content": safe_path.read_text(encoding="utf-8") if safe_path.exists() else "",
        }

    def write_template(self, relative_path: str, content: str) -> dict[str, str]:
        safe_path = (self.extension_root / relative_path).resolve()
        if self.extension_root.resolve() not in safe_path.parents:
            raise ValueError("Template path must stay within Empire extension root")
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding="utf-8")
        return {
            "path": str(safe_path.relative_to(self.extension_root)),
            "status": "saved",
        }

    def account_status(self) -> dict[str, Any]:
        secrets = self._read_secrets()
        google_oauth = self._oauth_connection_status()
        google_configured = bool(
            secrets.get("google_gmail_credentials_path")
            or secrets.get("google_gmail_token_path")
            or secrets.get("google_places_api_key")
            or google_oauth.get("status") in {"pending_auth", "connected", "expired"}
        )
        return {
            "google": {
                "mode": "live",
                "configured": google_configured,
                "status": google_oauth.get("status", "not_available"),
                "oauth_available": google_oauth.get("available", False),
                "connected": google_oauth.get("status") == "connected",
                "user": google_oauth.get("user"),
                "provider_name": google_oauth.get("provider_name", "Google"),
                "scopes": google_oauth.get("scopes", []),
                "expires_at": google_oauth.get("expires_at"),
                "user_info": google_oauth.get("user_info", {}),
                "actions": {
                    "connect_url": "/api/oauth/connect/google",
                    "disconnect_url": "/api/oauth/disconnect/google",
                    "refresh_url": "/api/oauth/refresh/google",
                },
            },
            "icloud": {
                "mode": "scaffold",
                "configured": False,
                "status": "scaffolded",
            },
            "outlook": {
                "mode": "scaffold",
                "configured": False,
                "status": "scaffolded",
            },
            "hubspot": {
                "mode": "live",
                "configured": bool(secrets.get("hubspot_private_app_token")),
                "status": "configured" if secrets.get("hubspot_private_app_token") else "not_configured",
                "actions": {
                    "configure_hint": "extensions/empire/config/empire_secrets.json",
                },
            },
            "linkedin": {
                "mode": "scaffold",
                "configured": False,
                "status": "scaffolded",
            },
        }

    def connector_catalog(self) -> dict[str, Any]:
        accounts = self.account_status()
        return {
            "connectors": {
                "google": {
                    "state": "live" if accounts["google"]["configured"] else "pending",
                    "actions": [
                        {
                            "id": "gmail_fetch",
                            "label": "Fetch Gmail",
                            "kind": "import",
                            "params": {"max_results": 10, "query": ""},
                        },
                        {
                            "id": "places_search",
                            "label": "Places Search",
                            "kind": "enhancement",
                            "params": {"query": "coffee roaster", "location": "", "radius_meters": 3000},
                        },
                    ],
                    "recent_jobs": self.list_connector_jobs(connector="google", limit=6),
                },
                "hubspot": {
                    "state": "live" if accounts["hubspot"]["configured"] else "pending",
                    "actions": [
                        {
                            "id": "sync",
                            "label": "Sync HubSpot",
                            "kind": "crm",
                            "params": {"limit": 25, "max_pages": 1},
                        }
                    ],
                    "recent_jobs": self.list_connector_jobs(connector="hubspot", limit=6),
                },
                "icloud": {
                    "state": "scaffold",
                    "actions": [],
                    "recent_jobs": [],
                },
                "outlook": {
                    "state": "scaffold",
                    "actions": [],
                    "recent_jobs": [],
                },
                "linkedin": {
                    "state": "scaffold",
                    "actions": [],
                    "recent_jobs": [],
                },
            }
        }


_service: EmpireExtensionService | None = None


def get_empire_extension_service() -> EmpireExtensionService:
    global _service
    if _service is None:
        _service = EmpireExtensionService()
    return _service
