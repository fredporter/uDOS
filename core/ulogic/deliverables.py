from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from core.services.path_service import get_repo_root


_SCHEMA_ROOT = (
    Path(get_repo_root())
    / "docs"
    / "examples"
    / "udos_v1_5_deliverables"
    / "schemas"
)


@dataclass(frozen=True)
class ValidationResult:
    schema_name: str
    ok: bool
    errors: list[str]


def load_deliverable_schema(schema_name: str) -> dict[str, Any]:
    path = _SCHEMA_ROOT / schema_name
    if not path.exists():
        raise FileNotFoundError(f"Deliverable schema not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_deliverable(
    schema_name: str,
    payload: dict[str, Any],
) -> ValidationResult:
    schema = load_deliverable_schema(schema_name)
    errors: list[str] = []
    _validate_schema_node(schema=schema, value=payload, path="$", errors=errors)
    return ValidationResult(schema_name=schema_name, ok=not errors, errors=errors)


def validate_project_record(payload: dict[str, Any]) -> ValidationResult:
    return validate_deliverable("project.schema.json", payload)


def validate_task_record(payload: dict[str, Any]) -> ValidationResult:
    return validate_deliverable("tasks.schema.json", payload)


def validate_workflow_record(payload: dict[str, Any]) -> ValidationResult:
    return validate_deliverable("workflow.schema.json", payload)


def validate_wizard_budget_record(payload: dict[str, Any]) -> ValidationResult:
    return validate_deliverable("wizard_budget.schema.json", payload)


def validate_project_file_payload(payload: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    project_id = _required_text(
        payload.get("project_id") or payload.get("id") or payload.get("name"),
        field="project_id",
        path="$",
        errors=errors,
    )
    name = _required_text(
        payload.get("name") or payload.get("id"),
        field="name",
        path="$",
        errors=errors,
    )
    missions = _coerce_missions(payload)
    if not missions:
        errors.append("$: `missions` must contain at least one mission identifier")

    adapted = {
        "project_id": project_id,
        "name": name,
        "description": payload.get("description", ""),
        "missions": missions,
        "status": payload.get("status", "active"),
    }
    result = validate_project_record(adapted)
    result_errors = list(errors)
    result_errors.extend(result.errors)
    return ValidationResult(
        schema_name=result.schema_name,
        ok=not result_errors,
        errors=result_errors,
    )


def validate_tasks_file_payload(payload: dict[str, Any]) -> ValidationResult:
    tasks = payload.get("tasks", [])
    errors: list[str] = []
    if not isinstance(tasks, list):
        return ValidationResult(
            schema_name="tasks.schema.json",
            ok=False,
            errors=["$: `tasks` must be an array"],
        )

    for index, item in enumerate(tasks):
        if not isinstance(item, dict):
            errors.append(f"$.tasks[{index}]: expected object, got {_python_type_name(item)}")
            continue
        task_id = _required_text(
            item.get("task_id") or item.get("id"),
            field="task_id",
            path=f"$.tasks[{index}]",
            errors=errors,
        )
        title = _required_text(
            item.get("title") or item.get("name"),
            field="title",
            path=f"$.tasks[{index}]",
            errors=errors,
        )
        status = _required_text(
            item.get("status"),
            field="status",
            path=f"$.tasks[{index}]",
            errors=errors,
        )
        adapted = {
            "task_id": task_id,
            "title": title,
            "description": item.get("description", ""),
            "status": status,
            "dependencies": item.get("dependencies", []),
        }
        result = validate_task_record(adapted)
        errors.extend(_prefix_errors(result.errors, f"$.tasks[{index}]"))

    return ValidationResult(
        schema_name="tasks.schema.json",
        ok=not errors,
        errors=errors,
    )


def validate_completed_file_payload(payload: dict[str, Any]) -> ValidationResult:
    completed = payload.get("completed", [])
    errors: list[str] = []
    if not isinstance(completed, list):
        return ValidationResult(
            schema_name="tasks.schema.json",
            ok=False,
            errors=["$: `completed` must be an array"],
        )

    for index, item in enumerate(completed):
        if not isinstance(item, dict):
            errors.append(f"$.completed[{index}]: expected object, got {_python_type_name(item)}")
            continue
        task_id = _required_text(
            item.get("task_id") or item.get("id"),
            field="id",
            path=f"$.completed[{index}]",
            errors=errors,
        )
        title = _required_text(
            item.get("title") or item.get("name"),
            field="title",
            path=f"$.completed[{index}]",
            errors=errors,
        )
        adapted = {
            "task_id": task_id,
            "title": title,
            "description": item.get("description", ""),
            "status": "done",
            "dependencies": item.get("dependencies", []),
        }
        result = validate_task_record(adapted)
        errors.extend(_prefix_errors(result.errors, f"$.completed[{index}]"))

    return ValidationResult(
        schema_name="tasks.schema.json",
        ok=not errors,
        errors=errors,
    )


def _validate_schema_node(
    *,
    schema: dict[str, Any],
    value: Any,
    path: str,
    errors: list[str],
) -> None:
    schema_type = schema.get("type")
    if schema_type:
        if not _matches_type(schema_type, value):
            errors.append(
                f"{path}: expected {schema_type}, got {_python_type_name(value)}"
            )
            return

    if schema_type == "object":
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required key `{key}`")

        properties = schema.get("properties", {})
        for key, child_schema in properties.items():
            if key not in value:
                continue
            _validate_schema_node(
                schema=child_schema,
                value=value[key],
                path=f"{path}.{key}",
                errors=errors,
            )
        return

    if schema_type == "array":
        item_schema = schema.get("items")
        if not isinstance(item_schema, dict):
            return
        for index, item in enumerate(value):
            _validate_schema_node(
                schema=item_schema,
                value=item,
                path=f"{path}[{index}]",
                errors=errors,
            )


def _matches_type(schema_type: str, value: Any) -> bool:
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "boolean":
        return isinstance(value, bool)
    return True


def _python_type_name(value: Any) -> str:
    return type(value).__name__


def _coerce_missions(payload: dict[str, Any]) -> list[str]:
    missions = payload.get("missions")
    if isinstance(missions, list):
        return [str(item) for item in missions if str(item).strip()]
    fallback = payload.get("id") or payload.get("project_id") or payload.get("name")
    return [str(fallback)] if fallback else []


def _prefix_errors(errors: list[str], prefix: str) -> list[str]:
    prefixed: list[str] = []
    for error in errors:
        if error.startswith("$."):
            prefixed.append(error.replace("$.", f"{prefix}.", 1))
        elif error == "$":
            prefixed.append(prefix)
        else:
            prefixed.append(f"{prefix}: {error}")
    return prefixed


def _required_text(
    value: Any,
    *,
    field: str,
    path: str,
    errors: list[str],
) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: `{field}` must be a non-empty string")
        return ""
    return value.strip()
