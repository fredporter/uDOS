"""Wizard publish routes for v1.3.15 publish spec scaffolding."""

from __future__ import annotations

from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from wizard.services.publish_service import get_publish_service, PublishService

AuthGuard = Optional[Callable]


class PublishCreateRequest(BaseModel):
    source_workspace: str = Field(default="memory/vault")
    provider: str = Field(default="wizard")
    options: dict[str, Any] = Field(default_factory=dict)


class OCAttachmentPayload(BaseModel):
    path: str
    media_type: str = Field(default="application/octet-stream")
    content_sha256: Optional[str] = None


class OCRenderSessionPayload(BaseModel):
    session_id: str
    principal_id: str
    token_lease_id: str
    scopes: list[str] = Field(default_factory=list)


class OCRenderRequest(BaseModel):
    contract_version: str = Field(default="1.0.0")
    content: str
    content_type: str = Field(default="markdown")
    entrypoint: str = Field(default="index")
    render_options: dict[str, Any] = Field(default_factory=dict)
    assets: list[OCAttachmentPayload] = Field(default_factory=list)
    session: OCRenderSessionPayload


def create_publish_routes(
    auth_guard: AuthGuard = None,
    publish_service: Optional[PublishService] = None,
) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/publish", tags=["publish"], dependencies=dependencies)
    service = publish_service or get_publish_service()

    @router.get("/capabilities")
    async def publish_capabilities():
        return service.get_capabilities()

    @router.get("/providers")
    async def publish_provider_registry():
        return {
            "success": True,
            "providers": service.get_provider_registry(),
        }

    @router.get("/jobs")
    async def list_publish_jobs(provider: Optional[str] = None, status: Optional[str] = None):
        return {
            "success": True,
            "jobs": service.list_jobs(provider=provider, status=status),
        }

    @router.post("/jobs")
    async def create_publish_job(payload: PublishCreateRequest):
        try:
            job = service.create_job(
                source_workspace=payload.source_workspace,
                provider=payload.provider,
                options=payload.options,
            )
            return {"success": True, "job": job}
        except KeyError:
            raise HTTPException(status_code=404, detail="Unknown publish provider")
        except RuntimeError as exc:
            raise HTTPException(status_code=412, detail=str(exc))

    @router.get("/jobs/{job_id}")
    async def get_publish_job(job_id: str):
        job = service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Publish job not found")
        return {"success": True, "job": job}

    @router.post("/jobs/{job_id}/cancel")
    async def cancel_publish_job(job_id: str):
        try:
            job = service.cancel_job(job_id)
            return {"success": True, "job": job}
        except KeyError:
            raise HTTPException(status_code=404, detail="Publish job not found")
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc))

    @router.get("/manifests/{manifest_id}")
    async def get_publish_manifest(manifest_id: str):
        manifest = service.get_manifest(manifest_id)
        if not manifest:
            raise HTTPException(status_code=404, detail="Publish manifest not found")
        return {"success": True, "manifest": manifest}

    @router.post("/providers/{provider}/sync")
    async def sync_publish_provider(provider: str):
        try:
            status = service.sync_provider(provider)
            if not status["available"]:
                return {"success": False, "status": status, "detail": "provider unavailable"}
            return {"success": True, "status": status}
        except KeyError:
            raise HTTPException(status_code=404, detail="Unknown publish provider")

    @router.get("/providers/oc_app/contract")
    async def get_oc_app_contract():
        return {"success": True, "contract": service.get_oc_app_contract()}

    @router.post("/providers/oc_app/render")
    async def render_oc_app(payload: OCRenderRequest):
        try:
            request_payload = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
            rendered = service.render_oc_app(request_payload)
            return {"success": True, "render": rendered}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except RuntimeError as exc:
            raise HTTPException(status_code=412, detail=str(exc))

    return router
