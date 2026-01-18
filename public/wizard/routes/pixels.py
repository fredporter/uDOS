"""
Pixel Editor API Routes
Handles tile/pixel art save/load
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json
from pathlib import Path

router = APIRouter(prefix="/api/v1/pixels", tags=["pixels"])

# In-memory storage (in production, would use database)
PIXEL_STORAGE: Dict[str, Any] = {}


@router.post("/save/{tile_id}")
async def save_tile(tile_id: str, data: Dict[str, Any]):
    """Save a tile to storage."""
    PIXEL_STORAGE[tile_id] = data
    return {"status": "saved", "tile_id": tile_id}


@router.get("/load/{tile_id}")
async def load_tile(tile_id: str):
    """Load a tile from storage."""
    if tile_id not in PIXEL_STORAGE:
        raise HTTPException(status_code=404, detail="Tile not found")
    return PIXEL_STORAGE[tile_id]


@router.get("/list")
async def list_tiles():
    """List all saved tiles."""
    return {
        "tiles": [
            {"id": tile_id, "size": 24} for tile_id in PIXEL_STORAGE.keys()
        ]
    }


@router.delete("/{tile_id}")
async def delete_tile(tile_id: str):
    """Delete a tile."""
    if tile_id not in PIXEL_STORAGE:
        raise HTTPException(status_code=404, detail="Tile not found")
    del PIXEL_STORAGE[tile_id]
    return {"status": "deleted", "tile_id": tile_id}
