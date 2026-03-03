"""Wizard-owned import pipeline for Empire rebuild."""

from __future__ import annotations

import json
import mimetypes
import re
import uuid
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path
from typing import Any

from core.services.spatial_filesystem import WORKSPACE_CONFIG
from core.services.workspace_ref import split_workspace_root
from wizard.services.empire_extension_service import get_empire_extension_service
from wizard.services.empire_document_service import get_empire_document_service
from wizard.services.empire_scope_service import get_empire_scope_service
from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_memory_dir, get_repo_root, get_vault_dir


logger = get_logger("empire-import", category="extensions")


class EmpireImportService:
    """Replace makeshift Empire scripts with tracked import jobs."""

    _MAILTO_PATTERN = re.compile(r"mailto:(?P<email>[^;]+)", re.IGNORECASE)
    _ICS_LINE_PATTERN = re.compile(r"^(?P<key>[^:;]+)(?:;(?P<params>[^:]+))?:(?P<value>.*)$")
    _DUE_HINT_PATTERN = re.compile(
        r"\b(?:by|before|due|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{4}-\d{2}-\d{2})\b",
        re.IGNORECASE,
    )

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.empire = get_empire_extension_service()
        self.document_service = get_empire_document_service()
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

    def _utc_now(self) -> str:
        ingestion = self.empire._import_module("empire.services.ingestion_service")
        return ingestion._utc_now()

    def _normalize_record(self, *, source: str, payload: dict[str, object], db_path: Path) -> str | None:
        normalization = self.empire._import_module("empire.services.normalization_service")
        storage = self.empire._import_module("empire.services.storage")
        record = normalization.normalize_payload(source, payload)
        if not any((record.name, record.email, record.phone)):
            return None
        return storage.upsert_record(record, db_path=db_path)

    def _derive_review_task(
        self,
        *,
        title: str,
        source: str,
        source_ref: str,
        category: str,
        task_type: str,
        notes: str,
        due_hint: str | None,
        confidence: float,
        db_path: Path,
        record_id: str | None = None,
    ) -> str:
        storage = self.empire._import_module("empire.services.storage")
        return storage.record_task(
            title=title,
            category=category,
            task_type=task_type,
            source=source,
            source_ref=source_ref,
            created_at=self._utc_now(),
            due_hint=due_hint,
            status="open",
            review_status="ready" if due_hint else "pending_review",
            notes=notes,
            metadata={"confidence": confidence, "derived_by": "empire_import_service"},
            record_id=record_id,
            dedupe_by_source=False,
            db_path=db_path,
        )

    def _extract_due_hint(self, text: str | None) -> str | None:
        if not text:
            return None
        matches = [match.group(0) for match in self._DUE_HINT_PATTERN.finditer(text)]
        if not matches:
            return None
        for match in matches:
            if match.lower() not in {"by", "before", "due"}:
                return match
        return matches[0]

    def _extract_email_text(self, source_path: Path) -> str:
        with source_path.open("rb") as handle:
            message = BytesParser(policy=policy.default).parse(handle)
        body_parts: list[str] = []
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_maintype() != "text":
                    continue
                if str(part.get_content_subtype()).lower() not in {"plain", "markdown", "html"}:
                    continue
                try:
                    payload = part.get_content()
                except Exception:
                    continue
                if isinstance(payload, str) and payload.strip():
                    body_parts.append(payload.strip())
        else:
            try:
                payload = message.get_content()
            except Exception:
                payload = ""
            if isinstance(payload, str) and payload.strip():
                body_parts.append(payload.strip())
        return "\n\n".join(body_parts).strip()

    def _decode_ics_value(self, value: str) -> str:
        return value.replace("\\n", "\n").replace("\\,", ",").replace("\\;", ";").strip()

    def _unfold_ics_lines(self, payload: str) -> list[str]:
        lines: list[str] = []
        for raw_line in payload.splitlines():
            if raw_line.startswith((" ", "\t")) and lines:
                lines[-1] += raw_line[1:]
            else:
                lines.append(raw_line.rstrip())
        return lines

    def _extract_ics_param(self, params: str | None, key: str) -> str | None:
        if not params:
            return None
        for item in params.split(";"):
            if "=" not in item:
                continue
            param_key, value = item.split("=", 1)
            if param_key.strip().upper() == key.upper():
                return value.strip().strip('"')
        return None

    def _extract_ics_email(self, value: str) -> str | None:
        match = self._MAILTO_PATTERN.search(value)
        if match:
            return match.group("email").strip().lower()
        lowered = value.strip().lower()
        return lowered if "@" in lowered else None

    def _parse_email_import(
        self,
        *,
        source_path: Path,
        extracted_text: str,
        title: str,
        db_path: Path,
    ) -> dict[str, object]:
        storage = self.empire._import_module("empire.services.storage")
        with source_path.open("rb") as handle:
            message = BytesParser(policy=policy.default).parse(handle)

        addresses = []
        for header in ("from", "to", "cc", "bcc", "reply-to"):
            header_values = message.get_all(header, [])
            addresses.extend(getaddresses(header_values))

        record_ids: list[str] = []
        unique_emails: set[str] = set()
        primary_record_id: str | None = None
        for name, email_address in addresses:
            email = email_address.strip().lower()
            if not email or email in unique_emails:
                continue
            unique_emails.add(email)
            payload = {"name": name.strip() or email.split("@", 1)[0], "email": email}
            record_id = self._normalize_record(source="email_import", payload=payload, db_path=db_path)
            if record_id:
                record_ids.append(record_id)
                if primary_record_id is None:
                    primary_record_id = record_id

        subject = str(message.get("subject") or title)
        occurred_at = self._utc_now()
        date_header = message.get("date")
        if date_header:
            try:
                occurred_at = parsedate_to_datetime(date_header).astimezone().isoformat()
            except (TypeError, ValueError, IndexError, OverflowError):
                occurred_at = self._utc_now()

        event_id = storage.record_event(
            record_id=primary_record_id,
            event_type="email.import",
            occurred_at=occurred_at,
            subject=subject,
            notes=str(source_path),
            metadata=json.dumps(
                {
                    "participants": sorted(unique_emails),
                    "path": str(source_path),
                    "message_id": message.get("message-id"),
                }
            ),
            db_path=db_path,
        )

        created_tasks = 0
        body_lower = extracted_text.lower()
        if any(token in body_lower for token in ("action:", "follow up", "please review", "todo", "- [ ]")):
            lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
            for line in lines:
                lowered = line.lower()
                if not any(token in lowered for token in ("action:", "follow up", "please review", "todo", "- [ ]")):
                    continue
                task_title = line
                if ":" in line:
                    task_title = line.split(":", 1)[1].strip() or line
                due_hint = self._extract_due_hint(line)
                self._derive_review_task(
                    title=task_title,
                    source=f"email:{event_id}:{uuid.uuid4().hex[:8]}",
                    source_ref=event_id,
                    category="communication",
                    task_type="email_follow_up",
                    notes=f"Derived from imported email {source_path.name}",
                    due_hint=due_hint,
                    confidence=0.86 if due_hint else 0.7,
                    db_path=db_path,
                    record_id=primary_record_id,
                )
                created_tasks += 1
        if created_tasks == 0:
            self._derive_review_task(
                title=f"Review email: {subject}",
                source=f"email:{event_id}:review",
                source_ref=event_id,
                category="communication",
                task_type="email_review",
                notes=f"Review imported email from {source_path.name}",
                due_hint=None,
                confidence=0.48,
                db_path=db_path,
                record_id=primary_record_id,
            )
            created_tasks = 1

        return {
            "records_imported": len(record_ids),
            "derived_tasks": created_tasks,
            "event_id": event_id,
            "participants": sorted(unique_emails),
        }

    def _parse_calendar_import(
        self,
        *,
        source_path: Path,
        extracted_text: str,
        db_path: Path,
    ) -> dict[str, object]:
        storage = self.empire._import_module("empire.services.storage")
        lines = self._unfold_ics_lines(extracted_text)
        events: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        for line in lines:
            stripped = line.strip()
            if stripped == "BEGIN:VEVENT":
                current = {"attendees": []}
                continue
            if stripped == "END:VEVENT":
                if current:
                    events.append(current)
                current = None
                continue
            if current is None:
                continue
            match = self._ICS_LINE_PATTERN.match(stripped)
            if not match:
                continue
            key = match.group("key").upper()
            params = match.group("params")
            value = self._decode_ics_value(match.group("value"))
            if key == "SUMMARY":
                current["summary"] = value
            elif key == "DESCRIPTION":
                current["description"] = value
            elif key == "LOCATION":
                current["location"] = value
            elif key == "DTSTART":
                current["dtstart"] = value
            elif key == "DTEND":
                current["dtend"] = value
            elif key == "UID":
                current["uid"] = value
            elif key == "ORGANIZER":
                current["organizer"] = {
                    "name": self._extract_ics_param(params, "CN"),
                    "email": self._extract_ics_email(value),
                }
            elif key == "ATTENDEE":
                current["attendees"].append(
                    {
                        "name": self._extract_ics_param(params, "CN"),
                        "email": self._extract_ics_email(value),
                    }
                )

        record_ids: list[str] = []
        created_tasks = 0
        for item in events:
            organizer = item.get("organizer") or {}
            organizer_record_id = None
            if organizer.get("email"):
                organizer_record_id = self._normalize_record(
                    source="calendar_import",
                    payload={"name": organizer.get("name"), "email": organizer.get("email")},
                    db_path=db_path,
                )
                if organizer_record_id:
                    record_ids.append(organizer_record_id)
            for attendee in item.get("attendees", []):
                if not attendee.get("email"):
                    continue
                attendee_record_id = self._normalize_record(
                    source="calendar_import",
                    payload={"name": attendee.get("name"), "email": attendee.get("email")},
                    db_path=db_path,
                )
                if attendee_record_id:
                    record_ids.append(attendee_record_id)

            summary = str(item.get("summary") or source_path.stem)
            description = str(item.get("description") or "")
            event_id = storage.record_event(
                record_id=organizer_record_id,
                event_type="calendar.import",
                occurred_at=str(item.get("dtstart") or self._utc_now()),
                subject=summary,
                notes=description or str(source_path),
                metadata=json.dumps(
                    {
                        "uid": item.get("uid"),
                        "dtend": item.get("dtend"),
                        "location": item.get("location"),
                        "organizer": organizer,
                        "attendees": item.get("attendees", []),
                    }
                ),
                db_path=db_path,
            )

            if description:
                due_hint = self._extract_due_hint(description)
                if "action:" in description.lower() or due_hint:
                    task_title = description.split("Action:", 1)[-1].splitlines()[0].strip() if "Action:" in description else f"Prepare for {summary}"
                    self._derive_review_task(
                        title=task_title,
                        source=f"calendar:{event_id}",
                        source_ref=event_id,
                        category="calendar",
                        task_type="calendar.follow_up",
                        notes=f"Derived from imported calendar item {summary}",
                        due_hint=due_hint,
                        confidence=0.84 if due_hint else 0.66,
                        db_path=db_path,
                        record_id=organizer_record_id,
                    )
                    created_tasks += 1

        return {
            "records_imported": len({record_id for record_id in record_ids if record_id}),
            "derived_tasks": created_tasks,
            "calendar_events": len(events),
        }

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
            db_path=Path(resolved_scope["db_path"]),
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
                    db_path=Path(resolved_scope["db_path"]),
                )
                normalization.write_normalized(
                    raw_path,
                    normalized_path,
                    persist=True,
                    db_path=Path(resolved_scope["db_path"]),
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
                elif suffix == ".eml":
                    extracted_text = self._extract_email_text(source_path)
                else:
                    extracted_text = source_path.read_text(encoding="utf-8", errors="ignore")

                db_path = Path(resolved_scope["db_path"])
                provider_metadata: dict[str, object] = {}
                if suffix == ".eml" and extracted_text is not None:
                    provider_metadata = self._parse_email_import(
                        source_path=source_path,
                        extracted_text=extracted_text,
                        title=self._title_for(source_path),
                        db_path=db_path,
                    )
                elif suffix == ".ics" and extracted_text is not None:
                    provider_metadata = self._parse_calendar_import(
                        source_path=source_path,
                        extracted_text=extracted_text,
                        db_path=db_path,
                    )
                records_imported += int(provider_metadata.get("records_imported", 0))
                if provider_metadata:
                    metadata.update(provider_metadata)

                title = self._title_for(source_path)
                classification = self.document_service.classify_document(
                    source_path=str(source_path),
                    title=title,
                    media_type=media_type,
                    extracted_text=extracted_text,
                )

                storage.record_document(
                    source=f"import:{kind}",
                    scope=resolved_scope["scope"],
                    binder_id=resolved_scope["binder_id"],
                    source_path=str(source_path),
                    title=title,
                    media_type=media_type,
                    classification=str(classification["classification"]),
                    confidence=float(classification["confidence"]),
                    summary=str(classification["summary"]),
                    review_status=str(classification["review_status"]),
                    extracted_text=extracted_text,
                    metadata={
                        "workspace_path": path,
                        "scope_label": resolved_scope["label"],
                        "classification": classification,
                        "provider_metadata": provider_metadata,
                    },
                    db_path=db_path,
                )
                documents_created = 1
                metadata["classification"] = classification
                storage.record_event(
                    record_id=None,
                    event_type="document.import",
                    occurred_at=ingestion._utc_now(),
                    subject=f"Imported document {source_path.name}",
                    notes=path,
                    metadata=json.dumps(
                        {
                            "scope": resolved_scope["scope"],
                            "classification": classification["classification"],
                            "provider_metadata": provider_metadata,
                        }
                    ),
                    db_path=db_path,
                )

            storage.complete_import_job(
                job_id=job_id,
                status="completed",
                records_imported=records_imported,
                documents_created=documents_created,
                metadata=metadata,
                db_path=Path(resolved_scope["db_path"]),
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
                db_path=Path(resolved_scope["db_path"]),
            )
            raise


_service: EmpireImportService | None = None


def get_empire_import_service() -> EmpireImportService:
    global _service
    if _service is None:
        _service = EmpireImportService()
    return _service
