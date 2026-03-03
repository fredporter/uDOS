"""Wizard-owned webhook mapping and delivery service for Empire."""

from __future__ import annotations

import re
import secrets
from typing import Any

from wizard.services.empire_extension_service import get_empire_extension_service
from wizard.services.empire_scope_service import get_empire_scope_service
from wizard.services.logging_api import get_logger

logger = get_logger("empire-webhooks", category="extensions")


class EmpireWebhookService:
    """Manage Empire webhook mappings and delivery logs."""

    _SECTION_PATTERN = re.compile(r"^##\s+(?P<section>.+?)\s*$")
    _MAP_PATTERN = re.compile(r"^-\s+(?P<source>.+?)\s+->\s+(?P<target>.+?)\s*$")
    _KV_PATTERN = re.compile(r"^-\s+(?P<key>[^:]+):\s*(?P<value>.+?)\s*$")

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

    def _resolve_db_path(self, scope: str = "master", binder_id: str | None = None):
        resolved = self.scope_service.resolve(scope=scope, binder_id=binder_id)
        return resolved, self.empire._resolve_db_path(scope=resolved["scope"], binder_id=resolved["binder_id"])

    def _webhook_templates_root(self):
        return self.empire.templates_root / "webhooks"

    def list_webhook_templates(self) -> list[dict[str, Any]]:
        root = self._webhook_templates_root()
        if not root.exists():
            return []
        templates: list[dict[str, Any]] = []
        for path in sorted(root.glob("*.md")):
            relative_path = str(path.relative_to(self.empire.extension_root))
            templates.append(self.read_webhook_template(relative_path))
        return templates

    def _parse_template_content(self, path: str, content: str) -> dict[str, Any]:
        parsed: dict[str, Any] = {
            "path": path,
            "name": path.split("/")[-1],
            "meta": {},
            "field_map": {},
            "required_fields": [],
            "notes": [],
        }
        current_section = ""
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            section_match = self._SECTION_PATTERN.match(line)
            if section_match:
                current_section = section_match.group("section").strip().lower()
                continue
            if current_section == "field map":
                map_match = self._MAP_PATTERN.match(line)
                if map_match:
                    parsed["field_map"][map_match.group("source").strip()] = map_match.group("target").strip()
                continue
            if current_section == "meta":
                kv_match = self._KV_PATTERN.match(line)
                if kv_match:
                    parsed["meta"][kv_match.group("key").strip()] = kv_match.group("value").strip()
                continue
            if current_section == "required fields" and line.startswith("- "):
                parsed["required_fields"].append(line[2:].strip())
                continue
            if current_section == "notes":
                parsed["notes"].append(line.removeprefix("- ").strip())
        meta = parsed["meta"]
        parsed["label"] = meta.get("label") or parsed["name"]
        parsed["source_system"] = meta.get("source_system")
        parsed["event_type"] = meta.get("event_type")
        parsed["target_scope"] = meta.get("target_scope")
        parsed["target_entity"] = meta.get("target_entity")
        parsed["template_version"] = meta.get("template_version")
        return parsed

    def read_webhook_template(self, template_path: str) -> dict[str, Any]:
        template = self.empire.read_template(template_path)
        content = template.get("content", "")
        parsed = self._parse_template_content(template_path, content)
        parsed["content"] = content
        return parsed

    def _resolved_mapping_config(
        self,
        *,
        target_entity: str,
        template_path: str | None,
        config: dict[str, Any] | None,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        resolved_config = dict(config or {})
        template = None
        if template_path:
            template = self.read_webhook_template(template_path)
            template_field_map = template.get("field_map") or {}
            if template_field_map and not resolved_config.get("field_map"):
                resolved_config["field_map"] = dict(template_field_map)
        resolved_config.setdefault("field_map", {})
        if not isinstance(resolved_config["field_map"], dict):
            resolved_config["field_map"] = {}
        if template and template.get("target_entity") and template.get("target_entity") != target_entity:
            raise ValueError("template target_entity does not match mapping target_entity")
        return resolved_config, template

    def preview_mapping(
        self,
        *,
        source_system: str,
        target_entity: str,
        template_path: str | None,
        config: dict[str, Any] | None,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        resolved_config, template = self._resolved_mapping_config(
            target_entity=target_entity,
            template_path=template_path,
            config=config,
        )
        field_map = resolved_config.get("field_map", {})
        transformed: dict[str, Any] = {}
        if field_map:
            for source_key, target_key in field_map.items():
                if source_key in payload:
                    transformed[str(target_key)] = payload[source_key]
        else:
            transformed = dict(payload)
        if target_entity == "contact":
            normalized = self._normalization().normalize_payload(source_system or "webhook", transformed)
            preview = {
                "email": normalized.email,
                "name": normalized.name,
                "organization": normalized.organization,
                "role": normalized.role,
                "phone": normalized.phone,
            }
        elif target_entity == "task":
            preview = {
                "title": transformed.get("title") or transformed.get("subject") or "Webhook task",
                "notes": transformed.get("notes") or transformed.get("description") or "",
                "due_hint": transformed.get("due_hint"),
            }
        elif target_entity == "document":
            preview = {
                "title": transformed.get("title") or "Webhook document",
                "payload": transformed,
            }
        else:
            preview = {
                "subject": transformed.get("subject") or transformed.get("title") or "Webhook event",
                "notes": transformed.get("notes") or transformed.get("description") or "",
            }
        return {
            "template": template,
            "field_map": field_map,
            "transformed_payload": transformed,
            "preview": preview,
        }

    def validate_mapping(
        self,
        *,
        name: str,
        source_system: str,
        event_type: str,
        target_scope: str,
        binder_id: str | None,
        target_entity: str,
        template_path: str | None,
        status: str = "active",
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        config = config or {}
        errors: list[str] = []
        warnings: list[str] = []

        if not name.strip():
            errors.append("name is required")
        if not source_system.strip():
            errors.append("source_system is required")
        if not event_type.strip():
            errors.append("event_type is required")
        if target_entity not in {"contact", "task", "event", "document"}:
            errors.append("target_entity must be contact, task, event, or document")
        if status not in {"active", "inactive", "draft"}:
            errors.append("status must be active, inactive, or draft")

        try:
            resolved_scope, _ = self._resolve_db_path(scope=target_scope, binder_id=binder_id)
        except ValueError as exc:
            errors.append(str(exc))
            resolved_scope = {"scope": target_scope, "binder_id": binder_id}

        if not isinstance(config, dict):
            errors.append("config must be an object")
            config = {}
        template = None
        field_map: dict[str, Any] = {}
        if template_path:
            try:
                resolved_config, template = self._resolved_mapping_config(
                    target_entity=target_entity,
                    template_path=template_path,
                    config=config,
                )
                field_map = resolved_config.get("field_map", {})
                config = resolved_config
                if not template.get("content", "").strip():
                    errors.append("template_path points to an empty template")
                if template.get("source_system") and template.get("source_system") != source_system:
                    warnings.append("template source_system differs from mapping source_system")
                if template.get("event_type") and template.get("event_type") != event_type:
                    warnings.append("template event_type differs from mapping event_type")
                if template.get("target_scope") and template.get("target_scope") != resolved_scope.get("scope"):
                    warnings.append("template target_scope differs from mapping target_scope")
            except ValueError as exc:
                errors.append(str(exc))
        else:
            field_map = config.get("field_map", {})
        if field_map and not isinstance(field_map, dict):
            errors.append("config.field_map must be an object when provided")
            field_map = {}
        elif target_entity in {"contact", "task"} and not field_map:
            warnings.append("No template_path or field_map provided; webhook mapping will rely on default payload interpretation")

        if target_entity == "contact" and isinstance(field_map, dict) and field_map:
            mapped_targets = {str(value).strip() for value in field_map.values()}
            if not {"email", "firstname", "lastname", "name"} & mapped_targets:
                warnings.append("Contact mapping does not include a standard identity field such as email or name")

        if target_entity == "task" and isinstance(field_map, dict) and field_map:
            mapped_targets = {str(value).strip() for value in field_map.values()}
            if not {"title", "subject"} & mapped_targets:
                warnings.append("Task mapping does not include a title field; fallback title generation will be used")

        endpoint_path = None
        if not errors:
            endpoint_path = f"/api/empire/webhooks/inbound/{{mapping_id}}?signature={{secret}}"

        return {
            "ok": not errors,
            "errors": errors,
            "warnings": warnings,
            "resolved_scope": resolved_scope,
            "target_entity": target_entity,
            "endpoint_path": endpoint_path,
            "template": {
                "path": template_path,
                "label": template.get("label") if template else None,
                "required_fields": template.get("required_fields", []) if template else [],
            }
            if template_path
            else None,
            "field_map": field_map,
        }

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
        validation = self.validate_mapping(
            name=name,
            source_system=source_system,
            event_type=event_type,
            target_scope=target_scope,
            binder_id=binder_id,
            target_entity=target_entity,
            template_path=template_path,
            status=status,
            config=config,
        )
        if not validation["ok"]:
            raise ValueError("; ".join(validation["errors"]))
        resolved_scope = validation["resolved_scope"]
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
        payload = self.empire.get_webhook_mapping(resolved_mapping_id) or {"mapping_id": resolved_mapping_id}
        payload["validation"] = validation
        return payload

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
        _, target_db_path = self._resolve_db_path(
            scope=str(mapping.get("target_scope") or "master"),
            binder_id=mapping.get("binder_id"),
        )

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
        storage = self._storage()
        try:
            result = self._apply_mapping(mapping, payload)
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
                db_path=target_db_path,
            )
            return {"delivery_id": delivery_id, "mapping_id": mapping_id, "result": result}
        except Exception as exc:
            delivery_id = storage.record_webhook_delivery(
                mapping_id=mapping_id,
                direction="inbound" if not test_mode else "test",
                event_type=str(mapping.get("event_type") or "webhook"),
                status="failed",
                request_payload=payload,
                response_payload={},
                error=str(exc),
                db_path=self.empire.db_path,
            )
            raise ValueError(f"Webhook mapping failed: {exc}") from exc

    def retry_delivery(self, delivery_id: str) -> dict[str, Any]:
        delivery = self.empire.get_webhook_delivery(delivery_id)
        if not delivery:
            raise ValueError(f"Unknown webhook delivery: {delivery_id}")
        mapping_id = str(delivery.get("mapping_id") or "")
        if not mapping_id:
            raise ValueError("Webhook delivery missing mapping_id")
        mapping = self.empire.get_webhook_mapping(mapping_id)
        if not mapping:
            raise ValueError(f"Unknown webhook mapping: {mapping_id}")
        payload = delivery.get("request_payload")
        if not isinstance(payload, dict):
            raise ValueError("Webhook delivery request payload is unavailable")
        result = self.receive_inbound(
            mapping_id=mapping_id,
            payload=payload,
            signature=str(mapping.get("endpoint_secret") or ""),
            test_mode=str(delivery.get("direction") or "") == "test",
        )
        result["retried_from_delivery_id"] = delivery_id
        return result

    def _apply_mapping(self, mapping: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        target_entity = str(mapping.get("target_entity") or "contact")
        storage = self._storage()
        _, target_db_path = self._resolve_db_path(
            scope=str(mapping.get("target_scope") or "master"),
            binder_id=mapping.get("binder_id"),
        )
        config = mapping.get("config_json") if isinstance(mapping.get("config_json"), dict) else {}
        preview = self.preview_mapping(
            source_system=str(mapping.get("source_system") or "webhook"),
            target_entity=target_entity,
            template_path=mapping.get("template_path"),
            config=config,
            payload=payload,
        )
        transformed_payload = preview["transformed_payload"]

        if target_entity == "contact":
            normalized = self._normalization().normalize_payload(
                str(mapping.get("source_system") or "webhook"),
                transformed_payload,
            )
            record_id = storage.upsert_record(normalized, db_path=target_db_path)
            return {
                "target_entity": "contact",
                "record_id": record_id,
                "email": normalized.email,
                "name": normalized.name,
                "preview": preview["preview"],
            }

        if target_entity == "task":
            title = str(
                transformed_payload.get("title")
                or transformed_payload.get("subject")
                or mapping.get("name")
                or "Webhook task"
            )
            task_id = storage.record_task(
                title=title,
                category="webhook",
                source=str(mapping.get("source_system") or "webhook"),
                source_ref=str(mapping.get("mapping_id")),
                created_at=self._utc_now(),
                status="open",
                due_hint=str(transformed_payload.get("due_hint") or "") or None,
                notes=str(transformed_payload.get("notes") or transformed_payload.get("description") or ""),
                metadata={"preview": preview["preview"]},
                db_path=target_db_path,
            )
            return {"target_entity": "task", "task_id": task_id, "title": title, "preview": preview["preview"]}

        if target_entity == "document":
            document_id = storage.record_document(
                source=f"webhook:{mapping.get('source_system')}",
                scope=str(mapping.get("target_scope") or "master"),
                binder_id=mapping.get("binder_id"),
                source_path=f"webhook:{mapping.get('mapping_id')}",
                title=str(transformed_payload.get("title") or mapping.get("name") or "Webhook document"),
                media_type="application/json",
                extracted_text=str(transformed_payload),
                metadata={"payload": transformed_payload, "preview": preview["preview"]},
                db_path=target_db_path,
            )
            return {"target_entity": "document", "document_id": document_id, "preview": preview["preview"]}

        event_id = storage.record_event(
            record_id=None,
            event_type=str(mapping.get("event_type") or "webhook"),
            occurred_at=self._utc_now(),
            subject=str(transformed_payload.get("subject") or transformed_payload.get("title") or mapping.get("name") or "Webhook event"),
            notes=str(transformed_payload.get("notes") or transformed_payload),
            metadata=str({"mapping_id": mapping.get("mapping_id"), "preview": preview["preview"]}),
            db_path=target_db_path,
        )
        return {"target_entity": "event", "event_id": event_id, "preview": preview["preview"]}


_service: EmpireWebhookService | None = None


def get_empire_webhook_service() -> EmpireWebhookService:
    global _service
    if _service is None:
        _service = EmpireWebhookService()
    return _service
