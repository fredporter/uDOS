"""
Table Exporter for uDOS v1.0.6.0

Export SQLite tables to various formats (.table.md, .csv, .json, .yaml).

Features:
- Export to Markdown tables (.table.md format)
- Export to CSV/TSV
- Export to JSON/JSONL
- Export to YAML
- Metadata preservation
- Type information retention

Author: uDOS Core Team
Version: 1.0.6.0
"""

import sqlite3
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ExportMetadata:
    """Metadata for export operations."""

    table_name: str
    row_count: int
    column_count: int
    format: str
    file_path: str


class TableExporter:
    """Export SQLite tables to various formats."""

    def __init__(self):
        """Initialize the exporter."""
        self.metadata: Optional[ExportMetadata] = None

    def get_table_info(self, db_path: Path, table_name: str) -> Dict[str, Any]:
        """
        Get table metadata (columns, types, row count).

        Args:
            db_path: Path to SQLite database
            table_name: Name of the table

        Returns:
            Dictionary with table information
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append(
                {
                    "name": row[1],
                    "type": row[2],
                    "nullable": not row[3],
                    "primary_key": bool(row[5]),
                }
            )

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]

        conn.close()

        return {
            "name": table_name,
            "columns": columns,
            "row_count": row_count,
            "column_count": len(columns),
        }

    def export_to_markdown(
        self, db_path: Path, table_name: str, output_path: Path
    ) -> ExportMetadata:
        """
        Export table to Markdown format (.table.md).

        Args:
            db_path: Path to SQLite database
            table_name: Name of the table to export
            output_path: Path for output file

        Returns:
            Export metadata
        """
        # Get table info
        table_info = self.get_table_info(db_path, table_name)

        # Read data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        conn.close()

        # Build markdown content
        lines = []

        # YAML frontmatter
        lines.append("---")
        lines.append(f"table_name: {table_name}")
        lines.append(f"row_count: {table_info['row_count']}")
        lines.append(f"column_count: {table_info['column_count']}")
        lines.append("columns:")
        for col in table_info["columns"]:
            lines.append(f"  - name: {col['name']}")
            lines.append(f"    type: {col['type']}")
            lines.append(f"    nullable: {col['nullable']}")
        lines.append("---")
        lines.append("")

        # Markdown table
        # Header
        header = "| " + " | ".join(col["name"] for col in table_info["columns"]) + " |"
        lines.append(header)

        # Separator
        separator = "| " + " | ".join("---" for _ in table_info["columns"]) + " |"
        lines.append(separator)

        # Data rows
        for row in rows:
            row_str = (
                "| "
                + " | ".join(str(val) if val is not None else "" for val in row)
                + " |"
            )
            lines.append(row_str)

        # Write file
        output_path.write_text("\n".join(lines), encoding="utf-8")

        metadata = ExportMetadata(
            table_name=table_name,
            row_count=table_info["row_count"],
            column_count=table_info["column_count"],
            format="markdown",
            file_path=str(output_path),
        )
        self.metadata = metadata
        return metadata

    def export_to_csv(
        self, db_path: Path, table_name: str, output_path: Path, delimiter: str = ","
    ) -> ExportMetadata:
        """
        Export table to CSV/TSV format.

        Args:
            db_path: Path to SQLite database
            table_name: Name of the table to export
            output_path: Path for output file
            delimiter: Delimiter character (comma or tab)

        Returns:
            Export metadata
        """
        # Get table info
        table_info = self.get_table_info(db_path, table_name)

        # Read data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        conn.close()

        # Write CSV
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)

            # Header row
            header = [col["name"] for col in table_info["columns"]]
            writer.writerow(header)

            # Data rows
            writer.writerows(rows)

        format_name = "tsv" if delimiter == "\t" else "csv"
        metadata = ExportMetadata(
            table_name=table_name,
            row_count=table_info["row_count"],
            column_count=table_info["column_count"],
            format=format_name,
            file_path=str(output_path),
        )
        self.metadata = metadata
        return metadata

    def export_to_json(
        self,
        db_path: Path,
        table_name: str,
        output_path: Path,
        format_style: str = "array",
    ) -> ExportMetadata:
        """
        Export table to JSON format.

        Args:
            db_path: Path to SQLite database
            table_name: Name of the table to export
            output_path: Path for output file
            format_style: "array" for JSON array, "jsonl" for JSON Lines

        Returns:
            Export metadata
        """
        # Get table info
        table_info = self.get_table_info(db_path, table_name)

        # Read data as dictionaries
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Write JSON
        if format_style == "array":
            output_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        elif format_style == "jsonl":
            lines = [json.dumps(row) for row in rows]
            output_path.write_text("\n".join(lines), encoding="utf-8")
        else:
            raise ValueError(f"Invalid format_style: {format_style}")

        metadata = ExportMetadata(
            table_name=table_name,
            row_count=table_info["row_count"],
            column_count=table_info["column_count"],
            format=format_style,
            file_path=str(output_path),
        )
        self.metadata = metadata
        return metadata

    def export_to_yaml(
        self, db_path: Path, table_name: str, output_path: Path
    ) -> ExportMetadata:
        """
        Export table to YAML format.

        Args:
            db_path: Path to SQLite database
            table_name: Name of the table to export
            output_path: Path for output file

        Returns:
            Export metadata
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")

        # Get table info
        table_info = self.get_table_info(db_path, table_name)

        # Read data as dictionaries
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Write YAML
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(rows, f, default_flow_style=False, allow_unicode=True)

        metadata = ExportMetadata(
            table_name=table_name,
            row_count=table_info["row_count"],
            column_count=table_info["column_count"],
            format="yaml",
            file_path=str(output_path),
        )
        self.metadata = metadata
        return metadata

    def export_table(
        self,
        db_path: Path,
        table_name: str,
        output_path: Path,
        format_hint: Optional[str] = None,
    ) -> ExportMetadata:
        """
        Export table to any supported format (auto-detect from file extension).

        Args:
            db_path: Path to SQLite database
            table_name: Name of the table to export
            output_path: Path for output file
            format_hint: Optional format hint ("markdown", "csv", "json", "yaml")

        Returns:
            Export metadata
        """
        # Determine format from extension or hint
        if format_hint:
            export_format = format_hint.lower()
        else:
            suffix = output_path.suffix.lower()
            if suffix in (".md", ".markdown"):
                export_format = "markdown"
            elif suffix == ".csv":
                export_format = "csv"
            elif suffix == ".tsv":
                export_format = "tsv"
            elif suffix in (".json", ".jsonl"):
                export_format = "json" if suffix == ".json" else "jsonl"
            elif suffix in (".yaml", ".yml"):
                export_format = "yaml"
            else:
                raise ValueError(f"Unknown format for extension: {suffix}")

        # Export based on format
        if export_format == "markdown":
            return self.export_to_markdown(db_path, table_name, output_path)
        elif export_format == "csv":
            return self.export_to_csv(db_path, table_name, output_path, delimiter=",")
        elif export_format == "tsv":
            return self.export_to_csv(db_path, table_name, output_path, delimiter="\t")
        elif export_format == "json":
            return self.export_to_json(
                db_path, table_name, output_path, format_style="array"
            )
        elif export_format == "jsonl":
            return self.export_to_json(
                db_path, table_name, output_path, format_style="jsonl"
            )
        elif export_format == "yaml":
            return self.export_to_yaml(db_path, table_name, output_path)
        else:
            raise ValueError(f"Unsupported format: {export_format}")
