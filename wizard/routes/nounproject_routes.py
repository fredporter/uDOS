"""
Noun Project Routes
===================

Expose Noun Project provider endpoints for dashboard tooling.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from wizard.providers import (
    ProviderError,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
)
from wizard.providers.nounproject_client import (
    NounProjectClient,
    NounProjectConfig,
)


class NounProjectSearchRequest(BaseModel):
    term: str
    limit: Optional[int] = None
    offset: int = 0


class NounProjectDownloadRequest(BaseModel):
    icon_id: int
    format: Optional[str] = None
    size: Optional[int] = None


class NounProjectCollectionRequest(BaseModel):
    slug: str


class NounProjectAsciiRequest(BaseModel):
    icon_id: int
    width: int = 40


def _get_client() -> NounProjectClient:
    config = NounProjectConfig(name="nounproject")
    return NounProjectClient(config)


def _handle_provider_error(exc: Exception):
    if isinstance(exc, AuthenticationError):
        raise HTTPException(status_code=401, detail=str(exc))
    if isinstance(exc, RateLimitError):
        raise HTTPException(status_code=429, detail=str(exc))
    if isinstance(exc, QuotaExceededError):
        raise HTTPException(status_code=402, detail=str(exc))
    if isinstance(exc, ProviderError):
        raise HTTPException(status_code=400, detail=str(exc))
    raise HTTPException(status_code=500, detail=str(exc))


def create_nounproject_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/nounproject", tags=["nounproject"], dependencies=dependencies
    )

    @router.get("/status")
    async def status():
        client = _get_client()
        try:
            # Authenticate to surface config issues early.
            await client.authenticate()
        except Exception as exc:
            _handle_provider_error(exc)
        return client.get_status()

    @router.post("/search")
    async def search(payload: NounProjectSearchRequest):
        client = _get_client()
        try:
            await client.authenticate()
            return await client.search(
                term=payload.term, limit=payload.limit, offset=payload.offset
            )
        except Exception as exc:
            _handle_provider_error(exc)

    @router.get("/icon/{icon_id}")
    async def get_icon(icon_id: int):
        client = _get_client()
        try:
            await client.authenticate()
            return await client.get_icon(icon_id=icon_id)
        except Exception as exc:
            _handle_provider_error(exc)

    @router.post("/download")
    async def download(payload: NounProjectDownloadRequest):
        client = _get_client()
        try:
            await client.authenticate()
            return await client.download(
                icon_id=payload.icon_id,
                format=payload.format or client.config.default_format,
                size=payload.size or client.config.default_size,
            )
        except Exception as exc:
            _handle_provider_error(exc)

    @router.post("/collection")
    async def get_collection(payload: NounProjectCollectionRequest):
        client = _get_client()
        try:
            await client.authenticate()
            return await client.get_collection(slug=payload.slug)
        except Exception as exc:
            _handle_provider_error(exc)

    @router.get("/collections")
    async def list_collections():
        client = _get_client()
        try:
            await client.authenticate()
            return await client.list_collections()
        except Exception as exc:
            _handle_provider_error(exc)

    @router.get("/recent")
    async def recent_downloads():
        client = _get_client()
        try:
            await client.authenticate()
            return await client.get_recent_downloads()
        except Exception as exc:
            _handle_provider_error(exc)

    @router.post("/ascii")
    async def get_ascii(payload: NounProjectAsciiRequest):
        client = _get_client()
        try:
            await client.authenticate()
            return await client.get_ascii(icon_id=payload.icon_id, width=payload.width)
        except Exception as exc:
            _handle_provider_error(exc)

    return router
