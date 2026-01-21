"""
Groovebox Catalog API Routes
============================

FastAPI routes for the Groovebox sound pack catalog.
Provides REST endpoints for browsing, searching, and downloading packs.

Part of uDOS Wizard Server v1.0.1.4+
"""

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Response, Request
from fastapi.responses import FileResponse, JSONResponse

from wizard.services.pack_manager import get_pack_manager, PackMetadata
from wizard.services.logging_manager import get_logger

logger = get_logger("wizard-catalog-api")

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


# === Catalog Browsing ===


@router.get("/packs")
async def list_packs(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    verified: bool = Query(False, description="Only verified packs"),
    limit: int = Query(50, ge=1, le=100),
):
    """List available sound packs."""
    manager = get_pack_manager()
    packs = manager.list_packs(tag=tag, verified_only=verified)[:limit]

    return {"packs": [p.to_dict() for p in packs], "total": len(packs)}


@router.get("/packs/{pack_id}")
async def get_pack(pack_id: str):
    """Get pack details."""
    manager = get_pack_manager()
    pack = manager.get_pack(pack_id)

    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack not found: {pack_id}")

    return pack.to_dict()


@router.get("/search")
async def search_packs(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=50),
):
    """Search packs by name, description, or tags."""
    manager = get_pack_manager()
    results = manager.search_packs(q)[:limit]

    return {
        "query": q,
        "results": [p.to_dict() for p in results],
        "total": len(results),
    }


@router.get("/tags")
async def list_tags():
    """List all available tags."""
    manager = get_pack_manager()
    stats = manager.get_stats()

    return {"tags": stats["tags"]}


@router.get("/stats")
async def catalog_stats():
    """Get catalog statistics."""
    manager = get_pack_manager()
    return manager.get_stats()


# === Download ===


@router.get("/download/{pack_id}")
async def download_pack(pack_id: str):
    """
    Download a pack archive.

    Returns the .tar.gz file for the requested pack.
    """
    manager = get_pack_manager()

    pack = manager.get_pack(pack_id)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack not found: {pack_id}")

    # Built-in packs can't be downloaded
    if pack.checksum == "builtin":
        raise HTTPException(
            status_code=400, detail="Built-in pack - already included with uDOS"
        )

    pack_path = manager.get_pack_path(pack_id)
    if not pack_path:
        raise HTTPException(status_code=404, detail="Pack archive not found")

    # Record download
    manager.record_download(pack_id)

    logger.info(f"[WIZ] Pack download: {pack_id}")

    return FileResponse(
        path=pack_path, filename=pack_path.name, media_type="application/gzip"
    )


# === Upload (Authenticated) ===


@router.post("/upload")
async def upload_pack(
    request: Request, file: UploadFile = File(..., description="Pack archive (.tar.gz)")
):
    """
    Upload a new pack for review.

    Requires authentication (session or API key).
    Pack will be validated and added to pending review queue.
    """
    # Check authentication
    session = request.session.get("user")
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Validate file type
    if not file.filename.endswith(".tar.gz"):
        raise HTTPException(status_code=400, detail="Must be .tar.gz file")

    manager = get_pack_manager()

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # Validate pack
        valid, message, manifest = manager.validate_pack(tmp_path)

        if not valid:
            tmp_path.unlink()
            raise HTTPException(status_code=400, detail=message)

        # Move to uploads directory (pending review)
        upload_path = manager.uploads_dir / file.filename
        tmp_path.rename(upload_path)

        logger.info(f"[WIZ] Pack uploaded for review: {manifest['id']}")

        return {
            "status": "pending_review",
            "message": "Pack uploaded successfully. Pending review.",
            "pack_id": manifest["id"],
            "version": manifest["version"],
        }

    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve/{pack_id}")
async def approve_pack(pack_id: str, request: Request):
    """
    Approve a pending pack (admin only).

    Moves pack from uploads to catalog.
    """
    # Admin check (simplified)
    session = request.session.get("user")
    if not session or session.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    manager = get_pack_manager()

    # Find in uploads
    uploads = list(manager.uploads_dir.glob(f"{pack_id}*.tar.gz"))
    if not uploads:
        raise HTTPException(status_code=404, detail="Upload not found")

    upload_path = uploads[0]

    # Validate and add
    valid, message, manifest = manager.validate_pack(upload_path)
    if not valid:
        raise HTTPException(status_code=400, detail=message)

    success, msg = manager.add_pack(upload_path, manifest, verified=True)

    if success:
        upload_path.unlink()  # Remove from uploads
        logger.info(f"[WIZ] Pack approved: {pack_id}")
        return {"status": "approved", "message": msg}
    else:
        raise HTTPException(status_code=400, detail=msg)


# === Moderation ===


@router.get("/pending")
async def list_pending(request: Request):
    """List packs pending review (admin only)."""
    session = request.session.get("user")
    if not session or session.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    manager = get_pack_manager()
    pending = list(manager.uploads_dir.glob("*.tar.gz"))

    return {"pending": [p.name for p in pending], "count": len(pending)}


@router.delete("/pending/{filename}")
async def reject_upload(filename: str, request: Request):
    """Reject and delete a pending upload (admin only)."""
    session = request.session.get("user")
    if not session or session.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    manager = get_pack_manager()
    upload_path = manager.uploads_dir / filename

    if not upload_path.exists():
        raise HTTPException(status_code=404, detail="Upload not found")

    upload_path.unlink()
    logger.info(f"[WIZ] Upload rejected: {filename}")

    return {"status": "rejected", "filename": filename}
