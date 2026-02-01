"""
Dataset service for Round 4 API routes backed by `wizard/data/udos-table.db`.
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

    def _bootstrap_database(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE contacts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                title TEXT,
                region TEXT,
                last_contact TEXT
            );
            """
        )
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
        contacts = [
            (1, "Miranda Lane", "Strategy Lead", "North America", "2026-01-21T09:15:00Z"),
            (2, "Kai Moreno", "Pipeline Director", "Latin America", "2026-01-18T15:32:00Z"),
            (3, "Ava Chen", "AI Ops", "Asia Pacific", "2026-01-27T11:04:00Z"),
        ]
        conn.executemany("INSERT INTO contacts VALUES (?, ?, ?, ?, ?);", contacts)
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
            cols = [row["name"] for row in cursor.fetchall()]
        self._column_cache[table] = cols
        return cols

    def list_tables(self) -> List[Dict[str, Any]]:
        with closing(self._connect()) as conn:
            cursor = conn.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;"
            )
            tables = []
            for row in cursor.fetchall():
                name = row["name"]
                columns = self._table_columns(name)
                row_count = conn.execute(f"SELECT COUNT(*) FROM {name};").fetchone()[0]
                tables.append(
                    {
                        "name": name,
                        "description": f"Table generated from local dataset ({name}).",
                        "columns": [{"name": col, "type": "unknown"} for col in columns],
                        "row_count": row_count,
                    }
                )
        return tables

    def _build_filter_clause(self, filters: Optional[List[Tuple[str, str]]]) -> Tuple[str, List[Any]]:
        if not filters:
            return "", []
        clauses = []
        params: List[Any] = []
        for column, value in filters:
            clauses.append(f"{column} = ?")
            params.append(value)
        return "WHERE " + " AND ".join(clauses), params

    def get_table(
        self,
        name: str,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[List[Tuple[str, str]]] = None,
        order_by: Optional[str] = None,
        desc: bool = False,
    ) -> Optional[Dict[str, Any]]:
        columns = self._table_columns(name)
        if not columns:
            return None
        order_by_clause = ""
        if order_by:
            if order_by not in columns:
                raise ValueError("Invalid order_by column")
            order_by_clause = f"ORDER BY {order_by} {'DESC' if desc else 'ASC'}"
        filter_clause, params = self._build_filter_clause(filters)
        query = (
            f"SELECT * FROM {name} {filter_clause} {order_by_clause} LIMIT ? OFFSET ?;"
        )
        with closing(self._connect()) as conn:
            cursor = conn.execute(query, [*params, limit, offset])
            rows = [dict(row) for row in cursor.fetchall()]
            total = conn.execute(f"SELECT COUNT(*) FROM {name} {filter_clause};", params).fetchone()[0]
        return {
            "schema": {
                "name": name,
                "columns": columns,
            },
            "rows": rows,
            "total": total,
        }

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
