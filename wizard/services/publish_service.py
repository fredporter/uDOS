"""Publish orchestration service for Wizard web publish lanes."""

from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root

CONTRACT_VERSION = "1.3.15-draft"
OC_HOST_CONTRACT_VERSION = "1.0.0"
OC_RENDER_CONTRACT_VERSION = "1.0.0"
logger = get_logger("publish-service")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class PublishProviderAdapter:
    """Base publish provider adapter."""

    def __init__(self, name: str, repo_root: Path):
        self.name = name
        self.repo_root = repo_root

    def available(self) -> bool:
        return False

    def reason(self) -> Optional[str]:
        return "provider unavailable"

    def sync_status(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "available": self.available(),
            "reason": self.reason(),
            "synced_at": _utc_now(),
        }


class WizardPublishAdapter(PublishProviderAdapter):
    def available(self) -> bool:
        return True

    def reason(self) -> Optional[str]:
        return None


class ModulePathPublishAdapter(PublishProviderAdapter):
    def __init__(self, name: str, repo_root: Path, module_dir: str):
        super().__init__(name=name, repo_root=repo_root)
        self.module_dir = module_dir

    def available(self) -> bool:
        return (self.repo_root / self.module_dir).exists()

    def reason(self) -> Optional[str]:
        if self.available():
            return None
        return f"{self.module_dir} module not installed"


class ExternalOCPublishAdapter(PublishProviderAdapter):
    def available(self) -> bool:
        return False

    def reason(self) -> Optional[str]:
        return "external oc-app adapter not yet configured"


def _build_provider_registry(repo_root: Path) -> Dict[str, PublishProviderAdapter]:
    return {
        "wizard": WizardPublishAdapter("wizard", repo_root),
        "dev": ModulePathPublishAdapter("dev", repo_root, "dev"),
        "sonic": ModulePathPublishAdapter("sonic", repo_root, "sonic"),
        "groovebox": ModulePathPublishAdapter("groovebox", repo_root, "groovebox"),
        "oc_app": ExternalOCPublishAdapter("oc_app", repo_root),
    }


def _build_provider_capability_contract() -> Dict[str, Dict[str, Any]]:
    return {
        "wizard": {
            "module": "wizard",
            "publish_lane": "core",
            "requires_module_present": False,
            "allowed_source_prefixes": ["memory/vault", "vault", "memory"],
        },
        "dev": {
            "module": "dev",
            "publish_lane": "sandbox",
            "requires_module_present": True,
            "allowed_source_prefixes": ["dev", "memory/dev", "memory/vault/@sandbox"],
        },
        "sonic": {
            "module": "sonic",
            "publish_lane": "artifact",
            "requires_module_present": True,
            "allowed_source_prefixes": ["sonic", "memory/sonic", "distribution/builds"],
        },
        "groovebox": {
            "module": "groovebox",
            "publish_lane": "media",
            "requires_module_present": True,
            "allowed_source_prefixes": ["groovebox", "memory/groovebox"],
        },
        "oc_app": {
            "module": "oc_app",
            "publish_lane": "external_adapter",
            "requires_module_present": False,
            "allowed_source_prefixes": ["memory/vault", "memory/vault/_site", "oc_app"],
        },
    }


class PublishService:
    """Persistent publish queue scaffold with capability-aware providers."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = Path(repo_root) if repo_root else get_repo_root()
        self._lock = threading.Lock()
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._manifests: Dict[str, Dict[str, Any]] = {}
        self._providers = _build_provider_registry(self.repo_root)
        self._provider_contract = _build_provider_capability_contract()
        self._state_dir = self.repo_root / "memory" / "wizard" / "publish"
        self._state_path = self._state_dir / "publish_state.json"
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._load_state()

    def _load_state(self) -> None:
        if not self._state_path.exists():
            return
        try:
            payload = json.loads(self._state_path.read_text(encoding="utf-8"))
            jobs = payload.get("jobs") or []
            manifests = payload.get("manifests") or []
            if isinstance(jobs, list):
                self._jobs = {
                    item["publish_job_id"]: item
                    for item in jobs
                    if isinstance(item, dict) and item.get("publish_job_id")
                }
            if isinstance(manifests, list):
                self._manifests = {
                    item["manifest_id"]: item
                    for item in manifests
                    if isinstance(item, dict) and item.get("manifest_id")
                }
        except Exception as exc:
            logger.warn("publish state load failed: %s", exc)

    def _save_state(self) -> None:
        payload = {
            "contract_version": CONTRACT_VERSION,
            "updated_at": _utc_now(),
            "jobs": sorted(self._jobs.values(), key=lambda j: j.get("created_at", ""), reverse=True),
            "manifests": sorted(self._manifests.values(), key=lambda m: m.get("created_at", ""), reverse=True),
        }
        self._state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _get_provider(self, provider: str) -> PublishProviderAdapter:
        entry = self._providers.get(provider)
        if not entry:
            raise KeyError("unknown provider")
        return entry

    def get_capabilities(self) -> Dict[str, Any]:
        providers: Dict[str, Any] = {}
        for name, adapter in self._providers.items():
            contract = self._provider_contract.get(name) or {}
            providers[name] = {
                "available": adapter.available(),
                "reason": adapter.reason(),
                "route_prefix": f"/api/publish/providers/{name}",
                "module": contract.get("module"),
                "publish_lane": contract.get("publish_lane"),
                "allowed_source_prefixes": contract.get("allowed_source_prefixes", []),
            }
        return {
            "contract_version": CONTRACT_VERSION,
            "providers": providers,
            "provider_registry": self.get_provider_registry(),
            "publish_routes_enabled": True,
            "state_path": str(self._state_path),
        }

    def get_provider_registry(self) -> Dict[str, Any]:
        registry: Dict[str, Any] = {}
        for provider, adapter in self._providers.items():
            contract = dict(self._provider_contract.get(provider) or {})
            contract["provider"] = provider
            contract["available"] = adapter.available()
            contract["reason"] = adapter.reason()
            contract["route_prefix"] = f"/api/publish/providers/{provider}"
            registry[provider] = contract
        return registry

    def _validate_module_gate(self, provider: str, source_workspace: str) -> Dict[str, Any]:
        contract = self._provider_contract.get(provider)
        if not contract:
            raise RuntimeError("provider contract missing")

        normalized_source = (source_workspace or "").strip()
        allowed_prefixes = contract.get("allowed_source_prefixes", [])
        matched_prefix = next(
            (prefix for prefix in allowed_prefixes if normalized_source.startswith(prefix)),
            None,
        )
        if not matched_prefix:
            raise RuntimeError(
                f"module-aware publish gating blocked provider={provider} for source_workspace={source_workspace}"
            )
        return {
            "module": contract.get("module"),
            "publish_lane": contract.get("publish_lane"),
            "matched_source_prefix": matched_prefix,
        }

    def list_jobs(self, provider: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        jobs = list(self._jobs.values())
        if provider:
            jobs = [job for job in jobs if job["provider"] == provider]
        if status:
            jobs = [job for job in jobs if job["status"] == status]
        return sorted(jobs, key=lambda j: j["created_at"], reverse=True)

    def create_job(
        self,
        *,
        source_workspace: str,
        provider: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        options = options or {}
        adapter = self._get_provider(provider)
        if not adapter.available():
            raise RuntimeError(adapter.reason() or "provider unavailable")
        module_gate = self._validate_module_gate(provider, source_workspace)

        created_at = _utc_now()
        job_id = f"pub_{uuid4().hex[:12]}"
        manifest_id = f"manifest_{uuid4().hex[:12]}"

        manifest_payload = {
            "manifest_id": manifest_id,
            "publish_job_id": job_id,
            "contract_version": CONTRACT_VERSION,
            "provider": provider,
            "source_workspace": source_workspace,
            "module": module_gate["module"],
            "publish_lane": module_gate["publish_lane"],
            "artifact_manifest": {
                "files": [],
                "site_root": "memory/vault/_site",
            },
            "checksum_set": {
                "source_workspace_sha256": hashlib.sha256(source_workspace.encode("utf-8")).hexdigest()
            },
            "created_at": created_at,
        }
        job_payload = {
            "publish_job_id": job_id,
            "contract_version": CONTRACT_VERSION,
            "provider": provider,
            "source_workspace": source_workspace,
            "module": module_gate["module"],
            "publish_lane": module_gate["publish_lane"],
            "status": "queued",
            "created_at": created_at,
            "completed_at": None,
            "error_detail": None,
            "manifest_id": manifest_id,
            "module_gate": module_gate,
            "options": options,
        }

        with self._lock:
            self._jobs[job_id] = job_payload
            self._manifests[manifest_id] = manifest_payload
            self._save_state()

        return job_payload

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise KeyError("job not found")
            if job["status"] in {"completed", "failed", "cancelled"}:
                raise RuntimeError("job is not cancellable")
            job["status"] = "cancelled"
            job["completed_at"] = _utc_now()
            self._save_state()
            return job

    def get_manifest(self, manifest_id: str) -> Optional[Dict[str, Any]]:
        return self._manifests.get(manifest_id)

    def sync_provider(self, provider: str) -> Dict[str, Any]:
        adapter = self._get_provider(provider)
        return adapter.sync_status()

    @staticmethod
    def _contains_forbidden_secret_keys(payload: Any) -> bool:
        forbidden = {
            "api_key",
            "access_token",
            "refresh_token",
            "authorization",
            "secret",
            "password",
        }
        if isinstance(payload, dict):
            for key, value in payload.items():
                if str(key).strip().lower() in forbidden:
                    return True
                if PublishService._contains_forbidden_secret_keys(value):
                    return True
            return False
        if isinstance(payload, list):
            return any(PublishService._contains_forbidden_secret_keys(item) for item in payload)
        return False

    def get_oc_app_contract(self) -> Dict[str, Any]:
        return {
            "provider": "oc_app",
            "host_contract_version": OC_HOST_CONTRACT_VERSION,
            "render_contract_version": OC_RENDER_CONTRACT_VERSION,
            "host": {
                "route_prefix": "/api/publish/providers/oc_app",
                "view_route": "/api/publish/providers/oc_app/view",
                "render_route": "/api/publish/providers/oc_app/render",
                "allowed_embed_modes": ["iframe", "webview"],
            },
            "rendering": {
                "deterministic_html": True,
                "asset_id_strategy": "sha256(path + content_sha256 + media_type)",
                "supported_content_types": ["markdown", "html", "text"],
                "cache_policy": {
                    "html": "private, max-age=60",
                    "assets": "public, max-age=31536000, immutable",
                },
            },
            "session_boundary": {
                "required": True,
                "required_scopes": ["oc_app:render"],
                "required_session_fields": ["session_id", "principal_id", "token_lease_id", "scopes"],
                "forbidden_payload_fields": [
                    "api_key",
                    "access_token",
                    "refresh_token",
                    "authorization",
                    "secret",
                    "password",
                ],
                "token_policy": "Wizard validates lease id only; app tokens are not accepted in payload.",
            },
            "compatibility": {
                "wizard_contract_version": CONTRACT_VERSION,
                "supported_render_contract_versions": [OC_RENDER_CONTRACT_VERSION],
                "backward_compatibility_window": "one minor contract version",
            },
        }

    def render_oc_app(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        contract_version = request_payload.get("contract_version") or OC_RENDER_CONTRACT_VERSION
        if contract_version != OC_RENDER_CONTRACT_VERSION:
            raise RuntimeError(f"unsupported render contract version: {contract_version}")

        session = request_payload.get("session") or {}
        required_scope = "oc_app:render"
        scopes = session.get("scopes") or []
        if required_scope not in scopes:
            raise RuntimeError("missing required scope: oc_app:render")
        if not session.get("token_lease_id"):
            raise RuntimeError("missing required session field: token_lease_id")
        if not session.get("session_id"):
            raise RuntimeError("missing required session field: session_id")
        if not session.get("principal_id"):
            raise RuntimeError("missing required session field: principal_id")

        if self._contains_forbidden_secret_keys(request_payload.get("render_options", {})):
            raise ValueError("render_options contains forbidden secret keys")

        content = request_payload.get("content") or ""
        content_type = request_payload.get("content_type") or "markdown"
        entrypoint = request_payload.get("entrypoint") or "index"
        assets = request_payload.get("assets") or []

        if content_type == "html":
            html = content
        elif content_type == "text":
            html = f"<pre data-content-type=\"text\">{escape(content)}</pre>"
        else:
            html = f"<pre data-content-type=\"markdown\">{escape(content)}</pre>"

        normalized_assets = []
        for asset in assets:
            path = asset.get("path") or ""
            media_type = asset.get("media_type") or "application/octet-stream"
            content_sha = asset.get("content_sha256") or hashlib.sha256(path.encode("utf-8")).hexdigest()
            asset_id = hashlib.sha256(
                f"{path}|{content_sha}|{media_type}".encode("utf-8")
            ).hexdigest()
            normalized_assets.append(
                {
                    "asset_id": asset_id,
                    "path": path,
                    "media_type": media_type,
                    "content_sha256": content_sha,
                    "cache_control": "public, max-age=31536000, immutable",
                }
            )

        html_etag = hashlib.sha256(html.encode("utf-8")).hexdigest()
        return {
            "provider": "oc_app",
            "host_contract_version": OC_HOST_CONTRACT_VERSION,
            "render_contract_version": OC_RENDER_CONTRACT_VERSION,
            "request_id": f"oc_render_{uuid4().hex[:12]}",
            "entrypoint": entrypoint,
            "content_type": content_type,
            "html": html,
            "assets_manifest": {
                "count": len(normalized_assets),
                "items": normalized_assets,
            },
            "cache": {
                "html_etag": html_etag,
                "html_cache_control": "private, max-age=60",
                "asset_cache_control": "public, max-age=31536000, immutable",
            },
            "session": {
                "session_id": session["session_id"],
                "principal_id": session["principal_id"],
                "validated_scope": required_scope,
                "token_lease_validated": True,
            },
            "rendered_at": _utc_now(),
        }


_publish_service: Optional[PublishService] = None


def get_publish_service(repo_root: Optional[Path] = None) -> PublishService:
    global _publish_service
    if repo_root is not None:
        return PublishService(repo_root=repo_root)
    if _publish_service is None:
        _publish_service = PublishService()
    return _publish_service
