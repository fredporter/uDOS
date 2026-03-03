"""Wizard-owned document classification and review service for Empire."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from wizard.services.empire_extension_service import get_empire_extension_service
from wizard.services.empire_scope_service import get_empire_scope_service


class EmpireDocumentService:
    """Classify imported documents and manage review state."""

    def __init__(self) -> None:
        self.empire = get_empire_extension_service()
        self.scope_service = get_empire_scope_service()

    def _storage(self):
        return self.empire._import_module("empire.services.storage")

    def _resolve_db_path(self, scope: str = "master", binder_id: str | None = None) -> Path:
        resolved = self.scope_service.resolve(scope=scope, binder_id=binder_id)
        return Path(resolved["db_path"])

    def classify_document(
        self,
        *,
        source_path: str,
        title: str,
        media_type: str,
        extracted_text: str | None,
    ) -> dict[str, Any]:
        text = (extracted_text or "").strip()
        lowered = text.lower()
        title_lower = title.lower()
        suffix = Path(source_path).suffix.lower()

        if suffix == ".ics" or "text/calendar" in media_type:
            classification = "calendar_event"
            confidence = 0.91
        elif suffix == ".eml" or "message/rfc822" in media_type:
            classification = "email_message"
            confidence = 0.9
        elif any(token in lowered for token in ("meeting", "agenda", "minutes", "calendar")):
            classification = "meeting_note"
            confidence = 0.78
        elif any(token in lowered for token in ("invoice", "amount due", "payment")):
            classification = "finance_doc"
            confidence = 0.82
        elif any(token in lowered for token in ("contact", "email", "phone", "linkedin")):
            classification = "contact_doc"
            confidence = 0.7
        elif any(token in lowered for token in ("task", "todo", "action", "- [ ]")):
            classification = "task_doc"
            confidence = 0.76
        elif "html" in media_type or source_path.endswith(".html"):
            classification = "web_capture"
            confidence = 0.68
        elif "pdf" in media_type:
            classification = "pdf_doc"
            confidence = 0.62
        elif any(token in title_lower for token in ("note", "notes")):
            classification = "note"
            confidence = 0.58
        else:
            classification = "document"
            confidence = 0.5

        summary_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                summary_lines.append(stripped)
            if len(" ".join(summary_lines)) >= 240:
                break
        summary = " ".join(summary_lines)[:280] if summary_lines else title
        review_status = "ready" if confidence >= 0.75 else "pending_review"
        return {
            "classification": classification,
            "confidence": confidence,
            "summary": summary,
            "review_status": review_status,
        }

    def review_document(
        self,
        *,
        document_id: str,
        scope: str = "master",
        binder_id: str | None = None,
        review_status: str,
        review_notes: str | None = None,
        classification: str | None = None,
    ) -> dict[str, Any]:
        if review_status not in {"pending_review", "ready", "approved", "needs_changes"}:
            raise ValueError("review_status must be pending_review, ready, approved, or needs_changes")
        db_path = self._resolve_db_path(scope=scope, binder_id=binder_id)
        storage = self._storage()
        document = storage.get_document(document_id, db_path=db_path)
        if not document:
            raise ValueError(f"Unknown document: {document_id}")
        storage.update_document_review(
            document_id=document_id,
            review_status=review_status,
            review_notes=review_notes,
            classification=classification,
            db_path=db_path,
        )
        updated = storage.get_document(document_id, db_path=db_path)
        return updated or {"document_id": document_id, "review_status": review_status}


_service: EmpireDocumentService | None = None


def get_empire_document_service() -> EmpireDocumentService:
    global _service
    if _service is None:
        _service = EmpireDocumentService()
    return _service
