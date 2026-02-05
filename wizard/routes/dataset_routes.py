"""
Dataset table & chart routes for the v1.3 data lane.
"""

from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, HTTPException, Query, Request

from wizard.services.dataset_service import get_dataset_service

router = APIRouter(prefix="/api/data", tags=["datasets"])
service = get_dataset_service()
MAX_LIMIT = 500
MAX_EXPORT_LIMIT = 2000


def _parse_filters(filters: Optional[List[str]]) -> List[Tuple[str, str, Any]]:
    parsed: List[Tuple[str, str, Any]] = []
    if not filters:
        return parsed
    for fragment in filters:
        if not fragment:
            continue
        value = fragment.strip()
        if not value:
            continue
        if "~" in value:
            column, raw = value.split("~", 1)
            parsed.append((column.strip(), "like", raw.strip()))
            continue
        if ">=" in value:
            column, raw = value.split(">=", 1)
            parsed.append((column.strip(), ">=", raw.strip()))
            continue
        if "<=" in value:
            column, raw = value.split("<=", 1)
            parsed.append((column.strip(), "<=", raw.strip()))
            continue
        if ">" in value:
            column, raw = value.split(">", 1)
            parsed.append((column.strip(), ">", raw.strip()))
            continue
        if "<" in value:
            column, raw = value.split("<", 1)
            parsed.append((column.strip(), "<", raw.strip()))
            continue
        if ":" in value:
            column, raw = value.split(":", 1)
        elif "=" in value:
            column, raw = value.split("=", 1)
        else:
            continue
        raw = raw.strip()
        if ".." in raw:
            low, high = raw.split("..", 1)
            parsed.append((column.strip(), "between", (low.strip(), high.strip())))
        else:
            parsed.append((column.strip(), "=", raw))
    return parsed


@router.get("/tables")
async def list_tables(request: Request):
    """
    Return a list of all tables (name, row count, columns) so the UI can enumerate datasets.
    """
    return {"tables": service.list_tables()}


@router.get("/schema")
async def schema(request: Request):
    """
    Return dataset schema metadata (tables, columns, types).
    """
    return service.get_schema()


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
    Fetch table rows with optional pagination, filters (`filter=column:value` or
    `filter=column~text`, `filter=column>=10`, `filter=column=1..10`), and ordering.
    """
    try:
        limit = min(limit, MAX_LIMIT)
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


@router.get("/query")
async def query_table(
    request: Request,
    table: str,
    limit: int = 50,
    offset: int = 0,
    columns: Optional[str] = None,
    filters: Optional[List[str]] = Query(None, alias="filter"),
    order_by: Optional[str] = None,
    desc: bool = False,
):
    """
    Query a table with optional column selection, filters, and ordering.
    Filters support:
      - `column:value` (equality)
      - `column~text` (LIKE)
      - `column>=10`, `column<=10`, `column>10`, `column<10`
      - `column=1..10` (range)
    """
    try:
        limit = min(limit, MAX_LIMIT)
        selected_columns = (
            [col.strip() for col in columns.split(",") if col.strip()]
            if columns
            else None
        )
        table_data = service.get_table(
            table,
            limit=limit,
            offset=offset,
            filters=_parse_filters(filters),
            order_by=order_by,
            desc=desc,
            columns=selected_columns,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not table_data:
        raise HTTPException(status_code=404, detail="Table not found")
    return table_data


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
async def export_table_stub(
    table: str,
    limit: int = 100,
    offset: int = 0,
    filters: Optional[List[str]] = Query(None, alias="filter"),
    order_by: Optional[str] = None,
    desc: bool = False,
):
    limit = min(limit, MAX_EXPORT_LIMIT)
    table_data = service.export_table(
        table,
        limit=limit,
        offset=offset,
        filters=_parse_filters(filters),
        order_by=order_by,
        desc=desc,
    )
    if not table_data:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"status": "ok", "export": table_data}
