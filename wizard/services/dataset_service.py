"""
Dataset service for the v1.3 data lane backed by `wizard/data/udos-table.db`.
"""

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class TableMetadata:
    name: str
    columns: List[str]
    types: List[str]
    row_count: int
    description: str


class DatasetService:
    DB_PATH = Path("wizard") / "data" / "udos-table.db"

    def __init__(self):
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        created = not self.DB_PATH.exists()
        with sqlite3.connect(self.DB_PATH) as conn:
            if created:
                self._bootstrap_database(conn)
        self._column_cache: Dict[str, List[str]] = {}
        self._column_types: Dict[str, Dict[str, str]] = {}

    def _bootstrap_database(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE revenue_summary (
                month TEXT,
                region TEXT,
                booked REAL,
                forecast REAL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE top_cities (
                id INTEGER PRIMARY KEY,
                city TEXT,
                region TEXT,
                layer INTEGER,
                population INTEGER
            );
            """
        )
        revenue = [
            ("2026-01", "North America", 820000.0, 900000.0),
            ("2026-01", "Europe", 440000.0, 460000.0),
            ("2026-01", "APAC", 310000.0, 330000.0),
        ]
        conn.executemany("INSERT INTO revenue_summary VALUES (?, ?, ?, ?);", revenue)
        cities = [
            (1, "Tokyo - Shibuya Crossing", "asia_east", 300, 14000000),
            (2, "New York City - Times Square", "north_america", 300, 19000000),
            (3, "Low Earth Orbit Station", "orbital", 306, 0),
        ]
        conn.executemany("INSERT INTO top_cities VALUES (?, ?, ?, ?, ?);", cities)
        conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _table_columns(self, table: str) -> List[str]:
        if table in self._column_cache:
            return self._column_cache[table]
        with closing(self._connect()) as conn:
            cursor = conn.execute(f"PRAGMA table_info({table});")
            cols = []
            types: Dict[str, str] = {}
            for row in cursor.fetchall():
                cols.append(row["name"])
                types[row["name"]] = row["type"] or "unknown"
        self._column_cache[table] = cols
        self._column_types[table] = types
        return cols

    def _table_column_types(self, table: str) -> Dict[str, str]:
        if table in self._column_types:
            return self._column_types[table]
        self._table_columns(table)
        return self._column_types.get(table, {})

    def list_tables(self) -> List[Dict[str, Any]]:
        with closing(self._connect()) as conn:
            cursor = conn.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;"
            )
            tables = []
            for row in cursor.fetchall():
                name = row["name"]
                columns = self._table_columns(name)
                types = self._table_column_types(name)
                row_count = conn.execute(f"SELECT COUNT(*) FROM {name};").fetchone()[0]
                tables.append(
                    {
                        "name": name,
                        "description": f"Table generated from local dataset ({name}).",
                        "columns": [
                            {"name": col, "type": types.get(col, "unknown")}
                            for col in columns
                        ],
                        "row_count": row_count,
                    }
                )
        return tables

    def _coerce_value(self, value: Any) -> Any:
        if value is None:
            return value
        if isinstance(value, (int, float)):
            return value
        raw = str(value).strip()
        if raw == "":
            return raw
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            return raw

    def _build_filter_clause(self, filters: Optional[List[Tuple[str, str, Any]]]) -> Tuple[str, List[Any]]:
        if not filters:
            return "", []
        clauses = []
        params: List[Any] = []
        for column, op, value in filters:
            if op == "like":
                clauses.append(f"{column} LIKE ?")
                params.append(f"%{value}%")
                continue
            if op == "between":
                if not isinstance(value, tuple) or len(value) != 2:
                    raise ValueError("Invalid range filter")
                low, high = value
                clauses.append(f"{column} BETWEEN ? AND ?")
                params.extend([self._coerce_value(low), self._coerce_value(high)])
                continue
            if op in {">", "<", ">=", "<=", "="}:
                clauses.append(f"{column} {op} ?")
                params.append(self._coerce_value(value))
                continue
            raise ValueError(f"Invalid filter operator: {op}")
        return "WHERE " + " AND ".join(clauses), params

    def get_table(
        self,
        name: str,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[List[Tuple[str, str, Any]]] = None,
        order_by: Optional[str] = None,
        desc: bool = False,
        columns: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        all_columns = self._table_columns(name)
        if not all_columns:
            return None
        if columns and len(columns) > 0:
            invalid = [col for col in columns if col not in all_columns]
            if invalid:
                raise ValueError(f"Invalid columns: {', '.join(invalid)}")
            selected = columns
        else:
            selected = all_columns
        order_by_clause = ""
        if order_by:
            if order_by not in all_columns:
                raise ValueError("Invalid order_by column")
            order_by_clause = f"ORDER BY {order_by} {'DESC' if desc else 'ASC'}"
        if filters:
            for column, _, _ in filters:
                if column not in all_columns:
                    raise ValueError(f"Invalid filter column: {column}")
        filter_clause, params = self._build_filter_clause(filters)
        select_clause = ", ".join(selected)
        query = (
            f"SELECT {select_clause} FROM {name} {filter_clause} {order_by_clause} LIMIT ? OFFSET ?;"
        )
        with closing(self._connect()) as conn:
            cursor = conn.execute(query, [*params, limit, offset])
            rows = [dict(row) for row in cursor.fetchall()]
            total = conn.execute(f"SELECT COUNT(*) FROM {name} {filter_clause};", params).fetchone()[0]
        return {
            "schema": {
                "name": name,
                "columns": selected,
                "types": self._table_column_types(name),
            },
            "rows": rows,
            "total": total,
        }

    def export_table(
        self,
        name: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[List[Tuple[str, str]]] = None,
        order_by: Optional[str] = None,
        desc: bool = False,
    ) -> Optional[Dict[str, Any]]:
        table = self.get_table(
            name,
            limit=limit,
            offset=offset,
            filters=filters,
            order_by=order_by,
            desc=desc,
        )
        if not table:
            return None
        rows = table["rows"]
        columns = table["schema"]["columns"]
        csv_lines = [",".join(columns)]
        for row in rows:
            csv_lines.append(",".join(str(row.get(col, "")) for col in columns))
        return {
            "table": name,
            "columns": columns,
            "rows": rows,
            "csv": "\n".join(csv_lines),
        }

    def get_schema(self) -> Dict[str, Any]:
        return {"tables": self.list_tables()}

    def get_chart(self) -> Dict[str, Any]:
        with closing(self._connect()) as conn:
            cursor = conn.execute(
                """
                SELECT month, region, booked - forecast AS variance
                FROM revenue_summary
                ORDER BY month DESC, region ASC;
                """
            )
            data = [dict(row) for row in cursor.fetchall()]
        return {
            "title": "Booked vs Forecast Variance",
            "data": data,
            "source_table": "revenue_summary",
        }


def get_dataset_service() -> DatasetService:
    return DatasetService()
