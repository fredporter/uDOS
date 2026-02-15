"""Publish orchestration service for Wizard web publish lanes."""

from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root

CONTRACT_VERSION = "1.3.15-draft"
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


class PublishService:
    """Persistent publish queue scaffold with capability-aware providers."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = Path(repo_root) if repo_root else get_repo_root()
        self._lock = threading.Lock()
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._manifests: Dict[str, Dict[str, Any]] = {}
        self._providers = _build_provider_registry(self.repo_root)
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
            providers[name] = {
                "available": adapter.available(),
                "reason": adapter.reason(),
                "route_prefix": f"/api/publish/providers/{name}",
            }
        return {
            "contract_version": CONTRACT_VERSION,
            "providers": providers,
            "publish_routes_enabled": True,
            "state_path": str(self._state_path),
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

        created_at = _utc_now()
        job_id = f"pub_{uuid4().hex[:12]}"
        manifest_id = f"manifest_{uuid4().hex[:12]}"

        manifest_payload = {
            "manifest_id": manifest_id,
            "publish_job_id": job_id,
            "contract_version": CONTRACT_VERSION,
            "provider": provider,
            "source_workspace": source_workspace,
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
            "status": "queued",
            "created_at": created_at,
            "completed_at": None,
            "error_detail": None,
            "manifest_id": manifest_id,
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


_publish_service: Optional[PublishService] = None


def get_publish_service(repo_root: Optional[Path] = None) -> PublishService:
    global _publish_service
    if repo_root is not None:
        return PublishService(repo_root=repo_root)
    if _publish_service is None:
        _publish_service = PublishService()
    return _publish_service
