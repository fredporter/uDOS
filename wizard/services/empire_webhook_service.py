"""Wizard-owned webhook mapping and delivery service for Empire."""

from __future__ import annotations

import secrets
from typing import Any

from wizard.services.empire_extension_service import get_empire_extension_service
from wizard.services.empire_scope_service import get_empire_scope_service
from wizard.services.logging_api import get_logger

logger = get_logger("empire-webhooks", category="extensions")


class EmpireWebhookService:
    """Manage Empire webhook mappings and delivery logs."""

    def __init__(self) -> None:
        self.empire = get_empire_extension_service()
        self.scope_service = get_empire_scope_service()

    def _storage(self):
        return self.empire._import_module("empire.services.storage")

    def _normalization(self):
        return self.empire._import_module("empire.services.normalization_service")

    def _utc_now(self) -> str:
        ingestion = self.empire._import_module("empire.services.ingestion_service")
        return ingestion._utc_now()

    def save_mapping(
        self,
        *,
        mapping_id: str | None,
        name: str,
        source_system: str,
        event_type: str,
        target_scope: str,
        binder_id: str | None,
        target_entity: str,
        template_path: str | None,
        status: str = "active",
        config: dict[str, Any] | None = None,
        endpoint_secret: str | None = None,
    ) -> dict[str, Any]:
        resolved_scope = self.scope_service.resolve(scope=target_scope, binder_id=binder_id)
        if target_entity not in {"contact", "task", "event", "document"}:
            raise ValueError("target_entity must be contact, task, event, or document")
        storage = self._storage()
        resolved_mapping_id = storage.upsert_webhook_mapping(
            mapping_id=mapping_id,
            name=name,
            source_system=source_system,
            event_type=event_type,
            target_scope=resolved_scope["scope"],
            binder_id=resolved_scope["binder_id"],
            target_entity=target_entity,
            template_path=template_path,
            endpoint_secret=endpoint_secret or secrets.token_urlsafe(24),
            status=status,
            config_json=config or {},
            db_path=self.empire.db_path,
        )
        return self.empire.get_webhook_mapping(resolved_mapping_id) or {"mapping_id": resolved_mapping_id}

    def test_mapping(self, mapping_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.receive_inbound(mapping_id=mapping_id, payload=payload, signature=None, test_mode=True)

    def receive_inbound(
        self,
        *,
        mapping_id: str,
        payload: dict[str, Any],
        signature: str | None,
        test_mode: bool = False,
    ) -> dict[str, Any]:
        mapping = self.empire.get_webhook_mapping(mapping_id)
        if not mapping:
            raise ValueError(f"Unknown webhook mapping: {mapping_id}")

        expected_secret = mapping.get("endpoint_secret")
        if not test_mode and expected_secret and signature != expected_secret:
            storage = self._storage()
            storage.record_webhook_delivery(
                mapping_id=mapping_id,
                direction="inbound",
                event_type=str(mapping.get("event_type") or "webhook"),
                status="rejected",
                request_payload=payload,
                response_payload={},
                error="invalid_signature",
                db_path=self.empire.db_path,
            )
            raise ValueError("Invalid webhook signature")

        result = self._apply_mapping(mapping, payload)
        storage = self._storage()
        delivery_id = storage.record_webhook_delivery(
            mapping_id=mapping_id,
            direction="inbound" if not test_mode else "test",
            event_type=str(mapping.get("event_type") or "webhook"),
            status="completed",
            request_payload=payload,
            response_payload=result,
            db_path=self.empire.db_path,
        )
        storage.record_event(
            record_id=result.get("record_id"),
            event_type="webhook.receive",
            occurred_at=self._utc_now(),
            subject=f"Webhook mapped: {mapping.get('name') or mapping_id}",
            notes=str(mapping.get("source_system") or "webhook"),
            metadata=str({"mapping_id": mapping_id, "delivery_id": delivery_id, "test_mode": test_mode}),
            db_path=self.empire.db_path,
        )
        return {"delivery_id": delivery_id, "mapping_id": mapping_id, "result": result}

    def _apply_mapping(self, mapping: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        target_entity = str(mapping.get("target_entity") or "contact")
        storage = self._storage()

        if target_entity == "contact":
            normalized = self._normalization().normalize_payload(
                str(mapping.get("source_system") or "webhook"),
                payload,
            )
            record_id = storage.upsert_record(normalized, db_path=self.empire.db_path)
            return {
                "target_entity": "contact",
                "record_id": record_id,
                "email": normalized.email,
                "name": normalized.name,
            }

        if target_entity == "task":
            title = str(payload.get("title") or payload.get("subject") or mapping.get("name") or "Webhook task")
            task_id = storage.record_task(
                title=title,
                category="webhook",
                source=str(mapping.get("source_system") or "webhook"),
                source_ref=str(mapping.get("mapping_id")),
                created_at=self._utc_now(),
                status="open",
                notes=str(payload.get("notes") or payload.get("description") or ""),
                db_path=self.empire.db_path,
            )
            return {"target_entity": "task", "task_id": task_id, "title": title}

        if target_entity == "document":
            document_id = storage.record_document(
                source=f"webhook:{mapping.get('source_system')}",
                scope=str(mapping.get("target_scope") or "master"),
                binder_id=mapping.get("binder_id"),
                source_path=f"webhook:{mapping.get('mapping_id')}",
                title=str(payload.get("title") or mapping.get("name") or "Webhook document"),
                media_type="application/json",
                extracted_text=str(payload),
                metadata={"payload": payload},
                db_path=self.empire.db_path,
            )
            return {"target_entity": "document", "document_id": document_id}

        event_id = storage.record_event(
            record_id=None,
            event_type=str(mapping.get("event_type") or "webhook"),
            occurred_at=self._utc_now(),
            subject=str(payload.get("subject") or mapping.get("name") or "Webhook event"),
            notes=str(payload.get("notes") or payload),
            metadata=str({"mapping_id": mapping.get("mapping_id")}),
            db_path=self.empire.db_path,
        )
        return {"target_entity": "event", "event_id": event_id}


_service: EmpireWebhookService | None = None


def get_empire_webhook_service() -> EmpireWebhookService:
    global _service
    if _service is None:
        _service = EmpireWebhookService()
    return _service
