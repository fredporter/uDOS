"""Wizard-owned connector execution for Empire."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from wizard.services.empire_extension_service import get_empire_extension_service
from wizard.services.empire_scope_service import get_empire_scope_service
from wizard.services.logging_api import get_logger

logger = get_logger("empire-sync", category="extensions")


class EmpireSyncService:
    """Run connector work through tracked Empire jobs."""

    def __init__(self) -> None:
        self.empire = get_empire_extension_service()
        self.scope_service = get_empire_scope_service()

    def _storage(self):
        return self.empire._import_module("empire.services.storage")

    def _utc_now(self) -> str:
        ingestion = self.empire._import_module("empire.services.ingestion_service")
        return ingestion._utc_now()

    def _resolve_db_path(self, scope: str, binder_id: str | None) -> Path:
        resolved = self.scope_service.resolve(scope=scope, binder_id=binder_id)
        if resolved["scope"] == "master":
            return self.empire.db_path
        return Path(resolved["db_path"])

    async def run_connector(
        self,
        *,
        connector: str,
        action: str,
        scope: str = "master",
        binder_id: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        resolved_scope = self.scope_service.resolve(scope=scope, binder_id=binder_id)
        params = params or {}
        storage = self._storage()
        db_path = self._resolve_db_path(scope, binder_id)
        sync_job_id = storage.create_sync_job(
            scope=resolved_scope["scope"],
            binder_id=resolved_scope["binder_id"],
            connector=connector,
            action=action,
            metadata={"params": params, "action": action},
            db_path=self.empire.db_path,
        )

        result_payload: dict[str, Any] = {}
        records_imported = 0
        try:
            if connector == "google" and action == "gmail_fetch":
                gmail = self.empire._import_module("empire.integrations.google_gmail")
                records_imported = gmail.fetch_and_ingest(
                    credentials_path=None,
                    token_path=None,
                    query=str(params.get("query", "")),
                    max_results=int(params.get("max_results", 25)),
                    db_path=db_path,
                )
                result_payload = {"records_imported": records_imported}
            elif connector == "google" and action == "places_search":
                places = self.empire._import_module("empire.integrations.google_places")
                records_imported = places.search_and_ingest(
                    api_key=None,
                    query=str(params.get("query", "")),
                    location=str(params.get("location", "")),
                    radius_meters=int(params.get("radius_meters", 5000)),
                    db_path=db_path,
                )
                result_payload = {"records_imported": records_imported}
            elif connector == "hubspot" and action == "sync":
                hubspot = self.empire._import_module("empire.integrations.hubspot")
                counts = hubspot.sync_all(
                    token=None,
                    db_path=db_path,
                    limit=int(params.get("limit", 50)),
                    max_pages=int(params.get("max_pages", 2)),
                )
                records_imported = int(counts.get("contacts", 0)) + int(counts.get("companies", 0))
                result_payload = {"counts": counts, "records_imported": records_imported}
            else:
                raise ValueError(f"Unsupported connector action: {connector}:{action}")

            storage.complete_sync_job(
                sync_job_id=sync_job_id,
                status="completed",
                records_imported=records_imported,
                documents_created=0,
                metadata=result_payload,
                db_path=self.empire.db_path,
            )
            storage.record_event(
                record_id=None,
                event_type="connector.run",
                occurred_at=self._utc_now(),
                subject=f"Connector completed: {connector}:{action}",
                notes=str(result_payload),
                metadata=str({"sync_job_id": sync_job_id, "scope": resolved_scope["scope"]}),
                db_path=self.empire.db_path,
            )
            return {
                "sync_job_id": sync_job_id,
                "status": "completed",
                "connector": connector,
                "action": action,
                "scope": resolved_scope,
                **result_payload,
            }
        except Exception as exc:
            logger.error("Empire connector run failed: %s", exc)
            storage.complete_sync_job(
                sync_job_id=sync_job_id,
                status="failed",
                records_imported=records_imported,
                documents_created=0,
                error=str(exc),
                metadata=result_payload,
                db_path=self.empire.db_path,
            )
            raise


_service: EmpireSyncService | None = None


def get_empire_sync_service() -> EmpireSyncService:
    global _service
    if _service is None:
        _service = EmpireSyncService()
    return _service
