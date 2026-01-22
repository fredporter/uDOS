"""
Binder Compiler Service (Wizard)

Compiles multi-chapter knowledge binders to multiple formats:
- Markdown
- JSON
- PDF (pandoc if available)
- Dev brief (Markdown + YAML frontmatter)
"""

import hashlib
import logging
import sqlite3
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from wizard.services.path_utils import get_repo_root
from wizard.services.logging_manager import get_logger

logger = get_logger("wizard.binder")


class BinderCompiler:
    """Compile multi-format binder outputs."""

    def __init__(
        self, db_path: Optional[Path] = None, config: Optional[Dict[str, Any]] = None
    ):
        repo_root = get_repo_root()
        default_db = repo_root / "memory" / "wizard" / "binders.db"
        if db_path is None:
            db_path = default_db

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.config = config or {}
        self.output_dir = Path(
            self.config.get("output_dir", repo_root / "memory" / "wizard" / "binders")
        )
        self.formats = self.config.get("formats", ["markdown", "json"])
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._init_db()
        logger.info(
            f"[WIZ] Binder compiler ready (db={self.db_path}, out={self.output_dir})"
        )

    def _init_db(self) -> None:
        schema_path = Path(__file__).parent / "schemas" / "binder_schema.sql"
        if not schema_path.exists():
            return
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.executescript(schema_path.read_text())
        conn.commit()
        conn.close()

    async def compile_binder(
        self, binder_id: str, formats: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        if formats is None:
            formats = self.formats

        logger.info(f"[WIZ] Compiling binder {binder_id} -> {formats}")
        chapters = await self.get_chapters(binder_id)
        outputs: List[Dict[str, Any]] = []

        if "markdown" in formats:
            md_output = await self._compile_markdown(binder_id, chapters)
            if md_output:
                outputs.append(md_output)

        if "json" in formats:
            json_output = await self._compile_json(binder_id, chapters)
            if json_output:
                outputs.append(json_output)

        if "pdf" in formats:
            pdf_output = await self._compile_pdf(binder_id, chapters)
            if pdf_output:
                outputs.append(pdf_output)

        if "brief" in formats:
            brief_output = await self._compile_brief(binder_id, chapters)
            if brief_output:
                outputs.append(brief_output)

        return {
            "status": "compiled",
            "binder_id": binder_id,
            "compiled_at": datetime.now().isoformat(),
            "outputs": outputs,
        }

    def _generate_id(self, prefix: str = "id") -> str:
        import secrets

        return f"{prefix}_{secrets.token_hex(6)}"

    def _calculate_word_count(self, text: str) -> int:
        text = re.sub(r"[#*`\[\]()]", "", text)
        return len(text.split())

    def _calculate_checksum(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    async def get_chapters(self, binder_id: str) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT chapter_id, title, order_index as "order", status, word_count,
                       has_code, has_images, has_tables, created_at, updated_at
                FROM chapters
                WHERE binder_id = ?
                ORDER BY order_index ASC
                """,
                (binder_id,),
            )
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return rows
        except Exception as exc:
            logger.error(f"[WIZ] Failed to load chapters: {exc}")
            return []

    async def add_chapter(
        self, binder_id: str, chapter: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            title = chapter.get("title")
            content = chapter.get("content", "")
            order_index = chapter.get("order", 1)
            chapter_id = chapter.get("chapter_id", self._generate_id("chap"))

            word_count = self._calculate_word_count(content)
            has_code = "```" in content
            has_images = "![" in content
            has_tables = "|" in content and "\n|" in content

            row_id = self._generate_id("chap")
            cursor.execute(
                """
                INSERT INTO chapters (
                    id, binder_id, chapter_id, title, content, order_index,
                    word_count, has_code, has_images, has_tables
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row_id,
                    binder_id,
                    chapter_id,
                    title,
                    content,
                    order_index,
                    word_count,
                    has_code,
                    has_images,
                    has_tables,
                ),
            )
            conn.commit()
            conn.close()
            return {
                "status": "added",
                "binder_id": binder_id,
                "chapter_id": chapter_id,
                "title": title,
            }
        except Exception as exc:
            logger.error(f"[WIZ] Add chapter failed: {exc}")
            return {"status": "error", "error": str(exc)}

    async def update_chapter(
        self, binder_id: str, chapter_id: str, content: str
    ) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            word_count = self._calculate_word_count(content)
            has_code = "```" in content
            has_images = "![" in content
            has_tables = "|" in content and "\n|" in content

            cursor.execute(
                """
                UPDATE chapters
                SET content = ?, word_count = ?, has_code = ?, has_images = ?, has_tables = ?
                WHERE binder_id = ? AND chapter_id = ?
                """,
                (
                    content,
                    word_count,
                    has_code,
                    has_images,
                    has_tables,
                    binder_id,
                    chapter_id,
                ),
            )
            conn.commit()
            conn.close()
            return {
                "status": "updated",
                "binder_id": binder_id,
                "chapter_id": chapter_id,
                "updated_at": datetime.now().isoformat(),
            }
        except Exception as exc:
            logger.error(f"[WIZ] Update chapter failed: {exc}")
            return {"status": "error", "error": str(exc)}

    async def _compile_markdown(
        self, binder_id: str, chapters: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        try:
            output_path = Path(self.output_dir) / f"{binder_id}.md"
            lines: List[str] = []
            lines.append(f"# Binder: {binder_id}\n")
            lines.append(
                f"*Compiled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            )
            lines.append("## Table of Contents\n")
            for idx, chapter in enumerate(chapters, 1):
                title = chapter.get("title", f"Chapter {idx}")
                lines.append(f"{idx}. [{title}](#{self._slugify(title)})")
            lines.append("\n---\n\n")

            for idx, chapter in enumerate(chapters, 1):
                title = chapter.get("title", f"Chapter {idx}")
                content = chapter.get("content", "")
                lines.append(f"## {title}\n\n")
                lines.append(f"{content}\n\n")
                lines.append("---\n\n")

            markdown_content = "\n".join(lines)
            output_path.write_text(markdown_content, encoding="utf-8")

            file_size = output_path.stat().st_size
            checksum = self._calculate_checksum(output_path)

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            output_id = self._generate_id("out")
            cursor.execute(
                """
                INSERT INTO outputs (id, binder_id, format, file_path, file_size, checksum)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    output_id,
                    binder_id,
                    "markdown",
                    str(output_path),
                    file_size,
                    checksum,
                ),
            )
            conn.commit()
            conn.close()

            return {
                "format": "markdown",
                "path": str(output_path),
                "size_bytes": file_size,
                "checksum": checksum,
            }
        except Exception as exc:
            logger.error(f"[WIZ] Markdown compile failed: {exc}")
            return None

    async def _compile_json(
        self, binder_id: str, chapters: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        try:
            import json

            output_path = Path(self.output_dir) / f"{binder_id}.json"
            data = {
                "binder_id": binder_id,
                "compiled_at": datetime.now().isoformat(),
                "chapters": chapters,
                "stats": {
                    "total_chapters": len(chapters),
                    "total_words": sum(ch.get("word_count", 0) for ch in chapters),
                },
            }
            output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

            file_size = output_path.stat().st_size
            checksum = self._calculate_checksum(output_path)
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            output_id = self._generate_id("out")
            cursor.execute(
                """
                INSERT INTO outputs (id, binder_id, format, file_path, file_size, checksum)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (output_id, binder_id, "json", str(output_path), file_size, checksum),
            )
            conn.commit()
            conn.close()
            return {
                "format": "json",
                "path": str(output_path),
                "size_bytes": file_size,
                "checksum": checksum,
            }
        except Exception as exc:
            logger.error(f"[WIZ] JSON compile failed: {exc}")
            return None

    async def _compile_pdf(
        self, binder_id: str, chapters: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        try:
            subprocess.run(["which", "pandoc"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            logger.warning("[WIZ] pandoc not found - skipping PDF generation")
            return None

        md_output = await self._compile_markdown(binder_id, chapters)
        if not md_output:
            return None

        md_path = Path(md_output["path"])
        pdf_path = Path(self.output_dir) / f"{binder_id}.pdf"

        try:
            subprocess.run(
                ["pandoc", str(md_path), "-o", str(pdf_path)],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as exc:
            logger.error(f"[WIZ] PDF generation failed: {exc.stderr}")
            return None

        file_size = pdf_path.stat().st_size
        checksum = self._calculate_checksum(pdf_path)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        output_id = self._generate_id("out")
        cursor.execute(
            """
            INSERT INTO outputs (id, binder_id, format, file_path, file_size, checksum)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (output_id, binder_id, "pdf", str(pdf_path), file_size, checksum),
        )
        conn.commit()
        conn.close()

        return {
            "format": "pdf",
            "path": str(pdf_path),
            "size_bytes": file_size,
            "checksum": checksum,
        }

    async def _compile_brief(
        self, binder_id: str, chapters: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        try:
            output_path = Path(self.output_dir) / f"{binder_id}-brief.md"
            brief = {
                "binder_id": binder_id,
                "generated_at": datetime.now().isoformat(),
                "chapter_count": len(chapters),
            }
            header = "---\n" + yaml.safe_dump(brief) + "---\n\n"
            body_lines: List[str] = []
            for idx, chapter in enumerate(chapters, 1):
                title = chapter.get("title", f"Chapter {idx}")
                body_lines.append(f"## {title}\n")
                body_lines.append(chapter.get("content", ""))
                body_lines.append("\n")

            output_path.write_text(header + "\n".join(body_lines), encoding="utf-8")
            file_size = output_path.stat().st_size
            checksum = self._calculate_checksum(output_path)
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            output_id = self._generate_id("out")
            cursor.execute(
                """
                INSERT INTO outputs (id, binder_id, format, file_path, file_size, checksum)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (output_id, binder_id, "brief", str(output_path), file_size, checksum),
            )
            conn.commit()
            conn.close()
            return {
                "format": "brief",
                "path": str(output_path),
                "size_bytes": file_size,
                "checksum": checksum,
            }
        except Exception as exc:
            logger.error(f"[WIZ] Brief compile failed: {exc}")
            return None

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        return text.strip("-")
