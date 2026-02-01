"""
Dataset service for Round 4 API skeleton.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass
class TableSchema:
    name: str
    columns: List[str]
    types: List[str]
    description: str


class DatasetService:
    def __init__(self):
        self._tables: Dict[str, Dict[str, Any]] = {
            "contacts": {
                "schema": TableSchema(
                    name="contacts",
                    columns=["id", "name", "title", "region", "last_contact"],
                    types=["int", "text", "text", "text", "timestamp"],
                    description="High-touch contacts table",
                ),
                "rows": [
                    {"id": 1, "name": "Miranda Lane", "title": "Strategy Lead", "region": "North America", "last_contact": "2026-01-21T09:15:00Z"},
                    {"id": 2, "name": "Kai Moreno", "title": "Pipeline Director", "region": "Latin America", "last_contact": "2026-01-18T15:32:00Z"},
                    {"id": 3, "name": "Ava Chen", "title": "AI Ops", "region": "Asia Pacific", "last_contact": "2026-01-27T11:04:00Z"},
                ],
            },
            "revenue_summary": {
                "schema": TableSchema(
                    name="revenue_summary",
                    columns=["month", "region", "booked", "forecast"],
                    types=["text", "text", "float", "float"],
                    description="Monthly booked vs forecast",
                ),
                "rows": [
                    {"month": "2026-01", "region": "North America", "booked": 820000.0, "forecast": 900000.0},
                    {"month": "2026-01", "region": "Europe", "booked": 440000.0, "forecast": 460000.0},
                    {"month": "2026-01", "region": "APAC", "booked": 310000.0, "forecast": 330000.0},
                ],
            },
        }

    def list_tables(self) -> List[Dict[str, Any]]:
        entries = []
        for table in self._tables.values():
            schema: TableSchema = table["schema"]
            entries.append(
                {
                    "name": schema.name,
                    "description": schema.description,
                    "columns": [{"name": c, "type": t} for c, t in zip(schema.columns, schema.types)],
                    "row_count": len(table["rows"]),
                }
            )
        return entries

    def get_table(self, name: str, limit: int = 50, offset: int = 0) -> Optional[Dict[str, Any]]:
        table = self._tables.get(name)
        if not table:
            return None
        rows = table["rows"][offset : offset + limit]
        return {
            "schema": {
                "name": table["schema"].name,
                "columns": table["schema"].columns,
                "types": table["schema"].types,
            },
            "rows": rows,
            "total": len(table["rows"]),
        }

    def get_chart(self) -> Dict[str, Any]:
        summary = []
        revenue_table = self._tables.get("revenue_summary", {})
        for row in revenue_table.get("rows", []):
            summary.append(
                {
                    "month": row["month"],
                    "region": row["region"],
                    "variance": row["booked"] - row["forecast"],
                }
            )
        return {
            "title": "Booked vs Forecast Variance",
            "data": summary,
        }


def get_dataset_service() -> DatasetService:
    return DatasetService()
