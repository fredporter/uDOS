"""
Dataset table & chart routes for Round 4.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request

from wizard.services.dataset_service import get_dataset_service

router = APIRouter(prefix="/api/data", tags=["datasets"])
service = get_dataset_service()


def _parse_filters(filters: Optional[List[str]]) -> List[tuple]:
    parsed = []
    if not filters:
        return parsed
    for fragment in filters:
        if ":" not in fragment:
            continue
        column, value = fragment.split(":", 1)
        parsed.append((column.strip(), value.strip()))
    return parsed


@router.get("/tables")
async def list_tables(request: Request):
    """
    Return a list of all tables (name, row count, columns) so the UI can enumerate datasets.
    """
    return {"tables": service.list_tables()}


@router.get("/tables/{table_name}")
async def fetch_table(
    request: Request,
    table_name: str,
    limit: int = 50,
    offset: int = 0,
    filters: Optional[List[str]] = Query(None, alias="filter"),
    order_by: Optional[str] = None,
    desc: bool = False,
):
    """
    Fetch table rows with optional pagination, simple filters (`filter=column:value` repeated),
    and optional ordering.
    """
    try:
        table = service.get_table(
            table_name,
            limit=limit,
            offset=offset,
            filters=_parse_filters(filters),
            order_by=order_by,
            desc=desc,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.get("/chart")
async def chart_preview(request: Request):
    """
    Return a simple variance chart derived from the `revenue_summary` table.
    """
    return {"chart": service.get_chart()}


@router.post("/parse/{table}")
async def parse_table_stub(table: str, payload: Dict[str, Any]):
    # Placeholder: ingest Markdown or YAML payloads later
    return {
        "status": "ok",
        "message": "Parsing scheduled (stub).",
        "table": table,
        "received": payload,
    }


@router.post("/export/{table}")
async def export_table_stub(table: str, limit: int = 50):
    table_data = service.get_table(table, limit=limit)
    if not table_data:
        raise HTTPException(status_code=404, detail="Table not found")
    return {
        "status": "ok",
        "export": {
            "table": table,
            "rows": table_data["rows"],
        },
    }
