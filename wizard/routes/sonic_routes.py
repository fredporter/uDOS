"""
Sonic Screwdriver Device Database Routes

Exposes the device catalog, schema, and management endpoints.
Integrates with Sonic Screwdriver builder for device-aware flashing.
"""

from pathlib import Path
from typing import Callable, Awaitable, Optional, List, Dict, Any
import json
import sqlite3

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]

# Paths
SONIC_DATASETS_PATH = Path(__file__).parent.parent.parent / "sonic" / "datasets"
SONIC_DB_PATH = Path(__file__).parent.parent.parent / "memory" / "sonic" / "sonic-devices.db"


class Device(BaseModel):
    """Device record from catalog."""

    id: str
    vendor: str
    model: str
    variant: Optional[str] = None
    year: Optional[int] = None
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    bios: Optional[str] = None
    secure_boot: Optional[str] = None
    tpm: Optional[str] = None
    usb_boot: Optional[str] = None
    ventoy: Optional[str] = None
    reflash_potential: Optional[str] = None
    methods: Optional[List[str]] = None
    notes: Optional[str] = None
    sources: Optional[List[str]] = None
    last_seen: Optional[str] = None


def create_sonic_routes(auth_guard: AuthGuard = None) -> APIRouter:
    """Create Sonic Screwdriver device database routes."""
    router = APIRouter(prefix="/api/v1/sonic", tags=["sonic"])

    def _get_db():
        """Get SQLite connection to device database."""
        if not SONIC_DB_PATH.exists():
            raise HTTPException(
                status_code=503,
                detail="Device database not initialized. Run: "
                "sqlite3 memory/sonic/sonic-devices.db < sonic/datasets/sonic-devices.sql",
            )
        return sqlite3.connect(str(SONIC_DB_PATH))

    def _get_table_md():
        """Load Markdown table."""
        table_file = SONIC_DATASETS_PATH / "sonic-devices.table.md"
        if not table_file.exists():
            return None
        return table_file.read_text()

    def _get_schema():
        """Load JSON Schema."""
        schema_file = SONIC_DATASETS_PATH / "sonic-devices.schema.json"
        if not schema_file.exists():
            return None
        return json.loads(schema_file.read_text())

    @router.get("/health")
    async def sonic_health(request: Request):
        """Check Sonic Screwdriver and datasets availability."""
        if auth_guard:
            await auth_guard(request)

        # Check components
        db_exists = SONIC_DB_PATH.exists()
        table_exists = (SONIC_DATASETS_PATH / "sonic-devices.table.md").exists()
        schema_exists = (SONIC_DATASETS_PATH / "sonic-devices.schema.json").exists()

        return {
            "status": "ok" if (table_exists and schema_exists) else "partial",
            "datasets_available": table_exists,
            "schema_available": schema_exists,
            "database_compiled": db_exists,
            "next_steps": [
                "Load device catalog: GET /api/v1/sonic/devices",
                "Get schema: GET /api/v1/sonic/schema",
                "Compile DB: sqlite3 ... < sonic/datasets/sonic-devices.sql",
            ]
            if not db_exists
            else [],
        }

    @router.get("/schema")
    async def get_schema(request: Request):
        """Get JSON Schema for device records."""
        if auth_guard:
            await auth_guard(request)

        schema = _get_schema()
        if not schema:
            raise HTTPException(status_code=404, detail="Schema not found")
        return schema

    @router.get("/table")
    async def get_table_markdown(request: Request):
        """Get raw Markdown table."""
        if auth_guard:
            await auth_guard(request)

        table = _get_table_md()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        return {"markdown": table, "format": "sonic-devices.table.md"}

    @router.get("/devices")
    async def list_devices(
        request: Request,
        vendor: Optional[str] = Query(None),
        reflash_potential: Optional[str] = Query(None),
        usb_boot: Optional[bool] = Query(None),
        ventoy: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
    ):
        """
        List devices from catalog with optional filters.

        Filters:
        - vendor: Vendor name (Apple, Dell, Raspberry Pi, etc.)
        - reflash_potential: high, medium, low, unknown
        - usb_boot: true/false
        - ventoy: works, issues, unknown
        """
        if auth_guard:
            await auth_guard(request)

        try:
            db = _get_db()
            cursor = db.cursor()

            # Build query
            query = "SELECT * FROM devices WHERE 1=1"
            params: List[Any] = []

            if vendor:
                query += " AND vendor LIKE ?"
                params.append(f"%{vendor}%")

            if reflash_potential:
                query += " AND reflash_potential = ?"
                params.append(reflash_potential)

            if usb_boot is not None:
                query += " AND usb_boot = ?"
                params.append("yes" if usb_boot else "no")

            if ventoy:
                query += " AND ventoy = ?"
                params.append(ventoy)

            # Count total
            count_query = query.replace("SELECT *", "SELECT COUNT(*)")
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

            # Fetch paginated results
            query += f" LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            cursor.execute(query, params)

            devices = [
                {
                    "id": row[0],
                    "vendor": row[1],
                    "model": row[2],
                    "variant": row[3],
                    "year": row[4],
                    "cpu": row[5],
                    "gpu": row[6],
                    "ram_gb": row[7],
                    "storage_gb": row[8],
                    "bios": row[9],
                    "secure_boot": row[10],
                    "tpm": row[11],
                    "usb_boot": row[12],
                    "ventoy": row[13],
                    "reflash_potential": row[14],
                    "methods": json.loads(row[15]) if row[15] else [],
                    "notes": row[16],
                    "sources": json.loads(row[17]) if row[17] else [],
                    "last_seen": row[18],
                }
                for row in cursor.fetchall()
            ]

            db.close()

            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "devices": devices,
            }

        except sqlite3.OperationalError as e:
            raise HTTPException(status_code=503, detail=f"Database error: {e}")

    @router.get("/devices/{device_id}")
    async def get_device(request: Request, device_id: str):
        """Get a specific device by ID."""
        if auth_guard:
            await auth_guard(request)

        try:
            db = _get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
            row = cursor.fetchone()
            db.close()

            if not row:
                raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

            return {
                "id": row[0],
                "vendor": row[1],
                "model": row[2],
                "variant": row[3],
                "year": row[4],
                "cpu": row[5],
                "gpu": row[6],
                "ram_gb": row[7],
                "storage_gb": row[8],
                "bios": row[9],
                "secure_boot": row[10],
                "tpm": row[11],
                "usb_boot": row[12],
                "ventoy": row[13],
                "reflash_potential": row[14],
                "methods": json.loads(row[15]) if row[15] else [],
                "notes": row[16],
                "sources": json.loads(row[17]) if row[17] else [],
                "last_seen": row[18],
            }

        except sqlite3.OperationalError as e:
            raise HTTPException(status_code=503, detail=f"Database error: {e}")

    @router.get("/stats")
    async def get_stats(request: Request):
        """Get catalog statistics."""
        if auth_guard:
            await auth_guard(request)

        try:
            db = _get_db()
            cursor = db.cursor()

            cursor.execute("SELECT COUNT(*) FROM devices")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT reflash_potential, COUNT(*) FROM devices GROUP BY reflash_potential"
            )
            by_potential = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute("SELECT COUNT(*) FROM devices WHERE usb_boot = 'yes'")
            usb_boot_capable = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM devices WHERE ventoy = 'works'")
            ventoy_works = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT vendor) FROM devices")
            vendor_count = cursor.fetchone()[0]

            db.close()

            return {
                "total_devices": total,
                "by_reflash_potential": by_potential,
                "usb_boot_capable": usb_boot_capable,
                "ventoy_compatible": ventoy_works,
                "unique_vendors": vendor_count,
            }

        except sqlite3.OperationalError as e:
            raise HTTPException(status_code=503, detail=f"Database error: {e}")

    return router
