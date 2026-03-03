"""Official Empire extension routes for Wizard."""

from __future__ import annotations

from typing import Any, Callable, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from wizard.services.empire_extension_service import get_empire_extension_service
from wizard.services.empire_collation_service import get_empire_collation_service
from wizard.services.empire_document_service import get_empire_document_service
from wizard.services.empire_import_service import get_empire_import_service
from wizard.services.empire_scope_service import get_empire_scope_service
from wizard.services.empire_sync_service import get_empire_sync_service
from wizard.services.empire_task_service import get_empire_task_service
from wizard.services.empire_webhook_service import get_empire_webhook_service


def create_empire_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/empire", tags=["empire"], dependencies=dependencies)

    @router.get("/status")
    async def empire_status() -> dict[str, Any]:
        return get_empire_extension_service().status_payload()

    @router.post("/status/enabled")
    async def empire_enable_toggle(enabled: bool = Body(..., embed=True)) -> dict[str, Any]:
        return get_empire_extension_service().set_enabled(enabled)

    @router.get("/health")
    async def empire_health() -> dict[str, Any]:
        return get_empire_extension_service().health_payload()

    @router.get("/overview")
    async def empire_overview(
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return get_empire_extension_service().load_overview(scope=scope, binder_id=binder_id)

    @router.get("/records")
    async def empire_records(
        limit: int = Query(50, ge=1, le=500),
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return {"records": get_empire_extension_service().list_records(limit=limit, scope=scope, binder_id=binder_id)}

    @router.post("/records/{record_id}/promote")
    async def empire_record_promote(
        record_id: str,
        binder_id: str = Body(..., embed=True),
    ) -> dict[str, Any]:
        try:
            return get_empire_extension_service().promote_record_to_master(
                record_id,
                binder_id=binder_id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/records/{record_id}/merge-candidates")
    async def empire_record_merge_candidates(
        record_id: str,
        limit: int = Query(10, ge=1, le=25),
    ) -> dict[str, Any]:
        try:
            return get_empire_extension_service().find_record_merge_candidates(record_id, limit=limit)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/records/merge")
    async def empire_record_merge(
        target_record_id: str = Body(...),
        source_record_id: str = Body(...),
    ) -> dict[str, Any]:
        try:
            return get_empire_extension_service().merge_records(
                target_record_id=target_record_id,
                source_record_id=source_record_id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/companies")
    async def empire_companies(
        limit: int = Query(50, ge=1, le=500),
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return {"companies": get_empire_extension_service().list_companies(limit=limit, scope=scope, binder_id=binder_id)}

    @router.get("/tasks")
    async def empire_tasks(
        limit: int = Query(50, ge=1, le=500),
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return {"tasks": get_empire_extension_service().list_tasks(limit=limit, scope=scope, binder_id=binder_id)}

    @router.post("/tasks/{task_id}/review")
    async def empire_task_review(
        task_id: str,
        scope: str = Body("master"),
        binder_id: str | None = Body(default=None),
        review_status: str = Body(...),
        status: str | None = Body(default=None),
        due_hint: str | None = Body(default=None),
        notes: str | None = Body(default=None),
    ) -> dict[str, Any]:
        try:
            return get_empire_task_service().review_task(
                task_id=task_id,
                scope=scope,
                binder_id=binder_id,
                review_status=review_status,
                status=status,
                due_hint=due_hint,
                notes=notes,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/events")
    async def empire_events(
        limit: int = Query(50, ge=1, le=500),
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return {"events": get_empire_extension_service().list_events(limit=limit, scope=scope, binder_id=binder_id)}

    @router.get("/sources")
    async def empire_sources(
        limit: int = Query(50, ge=1, le=500),
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return {"sources": get_empire_extension_service().list_sources(limit=limit, scope=scope, binder_id=binder_id)}

    @router.get("/documents")
    async def empire_documents(
        limit: int = Query(50, ge=1, le=500),
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return {"documents": get_empire_extension_service().list_documents(limit=limit, scope=scope, binder_id=binder_id)}

    @router.get("/documents/{document_id}")
    async def empire_document_detail(
        document_id: str,
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        payload = get_empire_extension_service().get_document(document_id, scope=scope, binder_id=binder_id)
        if not payload:
            raise HTTPException(status_code=404, detail="Document not found")
        return payload

    @router.get("/documents/{document_id}/review-bundle")
    async def empire_document_review_bundle(
        document_id: str,
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        payload = get_empire_extension_service().get_document_review_bundle(
            document_id,
            scope=scope,
            binder_id=binder_id,
        )
        if not payload:
            raise HTTPException(status_code=404, detail="Document not found")
        return payload

    @router.post("/documents/{document_id}/review")
    async def empire_document_review(
        document_id: str,
        scope: str = Body("master"),
        binder_id: str | None = Body(default=None),
        review_status: str = Body(...),
        review_notes: str | None = Body(default=None),
        classification: str | None = Body(default=None),
    ) -> dict[str, Any]:
        try:
            return get_empire_document_service().review_document(
                document_id=document_id,
                scope=scope,
                binder_id=binder_id,
                review_status=review_status,
                review_notes=review_notes,
                classification=classification,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/import/jobs")
    async def empire_import_jobs(
        limit: int = Query(50, ge=1, le=500),
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return {"jobs": get_empire_extension_service().list_import_jobs(limit=limit, scope=scope, binder_id=binder_id)}

    @router.get("/import/jobs/{job_id}")
    async def empire_import_job_detail(
        job_id: str,
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        payload = get_empire_extension_service().get_import_job(job_id, scope=scope, binder_id=binder_id)
        if not payload:
            raise HTTPException(status_code=404, detail="Import job not found")
        return payload

    @router.post("/import/path")
    async def empire_import_path(
        path: str = Body(...),
        scope: str = Body("master"),
        binder_id: str | None = Body(default=None),
    ) -> dict[str, Any]:
        try:
            return await get_empire_import_service().import_path(
                path=path,
                scope=scope,
                binder_id=binder_id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/process/collate")
    async def empire_process_collate(
        document_id: str = Body(...),
        emit_mode: str = Body("task_note"),
        scope: str = Body("master"),
        binder_id: str | None = Body(default=None),
    ) -> dict[str, Any]:
        try:
            return get_empire_collation_service().collate_document(
                document_id,
                emit_mode=emit_mode,
                scope=scope,
                binder_id=binder_id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/templates")
    async def empire_templates() -> dict[str, Any]:
        return {"templates": get_empire_extension_service().list_templates()}

    @router.get("/templates/read")
    async def empire_template_read(path: str = Query(...)) -> dict[str, Any]:
        try:
            return get_empire_extension_service().read_template(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/templates/write")
    async def empire_template_write(
        path: str = Body(...),
        content: str = Body(...),
    ) -> dict[str, Any]:
        try:
            return get_empire_extension_service().write_template(path, content)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/accounts")
    async def empire_accounts() -> dict[str, Any]:
        return get_empire_extension_service().account_status()

    @router.get("/connectors")
    async def empire_connectors(
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return get_empire_extension_service().connector_catalog(scope=scope, binder_id=binder_id)

    @router.post("/connectors/run")
    async def empire_connectors_run(
        connector: str = Body(...),
        action: str = Body(...),
        scope: str = Body("master"),
        binder_id: str | None = Body(default=None),
        params: dict[str, Any] = Body(default_factory=dict),
    ) -> dict[str, Any]:
        try:
            return await get_empire_sync_service().run_connector(
                connector=connector,
                action=action,
                scope=scope,
                binder_id=binder_id,
                params=params,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/sync/jobs")
    async def empire_sync_jobs(
        limit: int = Query(25, ge=1, le=500),
        connector: str | None = Query(default=None),
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return {
            "jobs": get_empire_extension_service().list_connector_jobs(
                connector=connector,
                limit=limit,
                scope=scope,
                binder_id=binder_id,
            )
        }

    @router.get("/sync/jobs/{sync_job_id}")
    async def empire_sync_job_detail(
        sync_job_id: str,
        scope: str = Query("master"),
        binder_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        payload = get_empire_extension_service().get_sync_job(sync_job_id, scope=scope, binder_id=binder_id)
        if not payload:
            raise HTTPException(status_code=404, detail="Sync job not found")
        return payload

    @router.get("/webhooks/mappings")
    async def empire_webhook_mappings(limit: int = Query(50, ge=1, le=500)) -> dict[str, Any]:
        return {"mappings": get_empire_extension_service().list_webhook_mappings(limit=limit)}

    @router.post("/webhooks/mappings")
    async def empire_webhook_mapping_save(
        mapping_id: str | None = Body(default=None),
        name: str = Body(...),
        source_system: str = Body(...),
        event_type: str = Body(...),
        target_scope: str = Body("master"),
        binder_id: str | None = Body(default=None),
        target_entity: str = Body("contact"),
        template_path: str | None = Body(default=None),
        status: str = Body("active"),
        config: dict[str, Any] = Body(default_factory=dict),
        endpoint_secret: str | None = Body(default=None),
    ) -> dict[str, Any]:
        try:
            return get_empire_webhook_service().save_mapping(
                mapping_id=mapping_id,
                name=name,
                source_system=source_system,
                event_type=event_type,
                target_scope=target_scope,
                binder_id=binder_id,
                target_entity=target_entity,
                template_path=template_path,
                status=status,
                config=config,
                endpoint_secret=endpoint_secret,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/webhooks/validate")
    async def empire_webhook_mapping_validate(
        name: str = Body(...),
        source_system: str = Body(...),
        event_type: str = Body(...),
        target_scope: str = Body("master"),
        binder_id: str | None = Body(default=None),
        target_entity: str = Body("contact"),
        template_path: str | None = Body(default=None),
        status: str = Body("active"),
        config: dict[str, Any] = Body(default_factory=dict),
    ) -> dict[str, Any]:
        try:
            return get_empire_webhook_service().validate_mapping(
                name=name,
                source_system=source_system,
                event_type=event_type,
                target_scope=target_scope,
                binder_id=binder_id,
                target_entity=target_entity,
                template_path=template_path,
                status=status,
                config=config,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/webhooks/templates")
    async def empire_webhook_templates() -> dict[str, Any]:
        return {"templates": get_empire_webhook_service().list_webhook_templates()}

    @router.post("/webhooks/preview")
    async def empire_webhook_preview(
        source_system: str = Body(...),
        target_entity: str = Body("contact"),
        template_path: str | None = Body(default=None),
        config: dict[str, Any] = Body(default_factory=dict),
        payload: dict[str, Any] = Body(default_factory=dict),
    ) -> dict[str, Any]:
        try:
            return get_empire_webhook_service().preview_mapping(
                source_system=source_system,
                target_entity=target_entity,
                template_path=template_path,
                config=config,
                payload=payload,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/webhooks/deliveries")
    async def empire_webhook_deliveries(
        limit: int = Query(50, ge=1, le=500),
        mapping_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return {
            "deliveries": get_empire_extension_service().list_webhook_deliveries(
                limit=limit,
                mapping_id=mapping_id,
            )
        }

    @router.post("/webhooks/test/{mapping_id}")
    async def empire_webhook_test(mapping_id: str, payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        try:
            return get_empire_webhook_service().test_mapping(mapping_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/webhooks/inbound/{mapping_id}")
    async def empire_webhook_inbound(
        mapping_id: str,
        payload: dict[str, Any] = Body(default_factory=dict),
        signature: str | None = Query(default=None),
    ) -> dict[str, Any]:
        try:
            return get_empire_webhook_service().receive_inbound(
                mapping_id=mapping_id,
                payload=payload,
                signature=signature,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/webhooks/deliveries/{delivery_id}/retry")
    async def empire_webhook_retry(delivery_id: str) -> dict[str, Any]:
        try:
            return get_empire_webhook_service().retry_delivery(delivery_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/scope")
    async def empire_scope(scope: str = Query("master"), binder_id: str | None = Query(default=None)) -> dict[str, Any]:
        try:
            return get_empire_scope_service().resolve(scope=scope, binder_id=binder_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/scope/binders")
    async def empire_scope_binders() -> dict[str, Any]:
        return {"binders": get_empire_scope_service().list_binders()}

    return router
