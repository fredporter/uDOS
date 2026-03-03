"""Wizard-owned import pipeline for Empire rebuild."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from core.services.spatial_filesystem import WORKSPACE_CONFIG
from core.services.workspace_ref import split_workspace_root
from wizard.services.empire_extension_service import get_empire_extension_service
from wizard.services.empire_scope_service import get_empire_scope_service
from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_memory_dir, get_repo_root, get_vault_dir


logger = get_logger("empire-import", category="extensions")


class EmpireImportService:
    """Replace makeshift Empire scripts with tracked import jobs."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.empire = get_empire_extension_service()
        self.scope_service = get_empire_scope_service()
        self.memory_root = get_memory_dir().resolve()
        self.vault_root = get_vault_dir().resolve()
        self.root_map = self._resolve_workspace_roots()

    def _resolve_workspace_roots(self) -> dict[str, Path]:
        root_map: dict[str, Path] = {"memory": self.memory_root}
        for ws_type, config in WORKSPACE_CONFIG.items():
            rel_path = config.get("path")
            if not isinstance(rel_path, str):
                continue
            if rel_path.startswith("memory/"):
                tail = rel_path[len("memory/") :]
                root_map[ws_type.value] = (self.memory_root / tail).resolve()
            else:
                root_map[ws_type.value] = (self.repo_root / rel_path).resolve()
        root_map["vault"] = self.vault_root
        return root_map

    def _resolve_source_path(self, path: str) -> Path:
        root_key, rel = split_workspace_root(
            path, valid_roots=self.root_map.keys(), default_root="memory"
        )
        root_dir = self.root_map[root_key]
        candidate = (root_dir / rel).resolve()
        try:
            candidate.relative_to(root_dir)
        except ValueError as exc:
            raise ValueError(f"Path must stay within workspace root: {root_key}") from exc
        if not candidate.exists() or not candidate.is_file():
            raise ValueError(f"Import source not found: {path}")
        return candidate

    def _title_for(self, source_path: Path) -> str:
        return source_path.stem.replace("-", " ").replace("_", " ").strip() or source_path.name

    async def import_path(
        self,
        *,
        path: str,
        scope: str = "master",
        binder_id: str | None = None,
    ) -> dict[str, Any]:
        resolved_scope = self.scope_service.resolve(scope=scope, binder_id=binder_id)
        source_path = self._resolve_source_path(path)
        storage = self.empire._import_module("empire.services.storage")
        ingestion = self.empire._import_module("empire.services.ingestion_service")
        normalization = self.empire._import_module("empire.services.normalization_service")

        suffix = source_path.suffix.lower()
        kind = suffix.lstrip(".") or "file"
        media_type = mimetypes.guess_type(source_path.name)[0] or "text/plain"
        job_id = storage.create_import_job(
            scope=resolved_scope["scope"],
            binder_id=resolved_scope["binder_id"],
            source_kind=kind,
            source_path=str(source_path),
            metadata={"requested_path": path, "scope_label": resolved_scope["label"]},
            db_path=self.empire.db_path,
        )

        records_imported = 0
        documents_created = 0
        metadata: dict[str, object] = {"job_id": job_id}
        try:
            if suffix in {".csv", ".json", ".jsonl"}:
                raw_dir = self.empire.data_root / "raw"
                normalized_dir = self.empire.data_root / "normalized"
                raw_path = raw_dir / f"{job_id}.jsonl"
                normalized_path = normalized_dir / f"{job_id}.jsonl"
                records_imported = ingestion.ingest_file(
                    source_path,
                    raw_path,
                    source_label=source_path.stem,
                    db_path=self.empire.db_path,
                )
                normalization.write_normalized(
                    raw_path,
                    normalized_path,
                    persist=True,
                    db_path=self.empire.db_path,
                )
                metadata["raw_path"] = str(raw_path)
                metadata["normalized_path"] = str(normalized_path)
            else:
                extracted_text: str | None = None
                if suffix == ".pdf":
                    from wizard.services.pdf_ocr_service import get_pdf_ocr_service

                    success, output_path, message = await get_pdf_ocr_service().extract(str(source_path))
                    metadata["extract_message"] = message
                    if success and output_path:
                        extracted_text = output_path.read_text(encoding="utf-8")
                        metadata["extracted_markdown_path"] = str(output_path)
                    else:
                        extracted_text = None
                else:
                    extracted_text = source_path.read_text(encoding="utf-8", errors="ignore")

                storage.record_document(
                    source=f"import:{kind}",
                    scope=resolved_scope["scope"],
                    binder_id=resolved_scope["binder_id"],
                    source_path=str(source_path),
                    title=self._title_for(source_path),
                    media_type=media_type,
                    extracted_text=extracted_text,
                    metadata={
                        "workspace_path": path,
                        "scope_label": resolved_scope["label"],
                    },
                    db_path=self.empire.db_path,
                )
                documents_created = 1
                storage.record_event(
                    record_id=None,
                    event_type="document.import",
                    occurred_at=ingestion._utc_now(),
                    subject=f"Imported document {source_path.name}",
                    notes=path,
                    metadata=str({"scope": resolved_scope["scope"]}),
                    db_path=self.empire.db_path,
                )

            storage.complete_import_job(
                job_id=job_id,
                status="completed",
                records_imported=records_imported,
                documents_created=documents_created,
                metadata=metadata,
                db_path=self.empire.db_path,
            )
            return {
                "job_id": job_id,
                "status": "completed",
                "records_imported": records_imported,
                "documents_created": documents_created,
                "scope": resolved_scope,
                "metadata": metadata,
            }
        except Exception as exc:
            logger.error("Empire import failed: %s", exc)
            storage.complete_import_job(
                job_id=job_id,
                status="failed",
                records_imported=records_imported,
                documents_created=documents_created,
                error=str(exc),
                metadata=metadata,
                db_path=self.empire.db_path,
            )
            raise


_service: EmpireImportService | None = None


def get_empire_import_service() -> EmpireImportService:
    global _service
    if _service is None:
        _service = EmpireImportService()
    return _service
