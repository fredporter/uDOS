from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .deliverables import validate_tasks_file_payload, validate_workflow_record


@dataclass(frozen=True)
class JsonFormatResult:
    profile: str
    profile_label: str
    format_label: str
    validation_label: str
    content: str
    changed: bool
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


_PROFILE_META: dict[str, dict[str, str]] = {
    "json": {
        "profile_label": "JSON",
        "format_label": "JSON",
        "validation_label": "JSON syntax",
    },
    "tasks-ledger": {
        "profile_label": "Contributor Tasks",
        "format_label": "Contributor tasks JSON",
        "validation_label": "Contributor mission shape",
    },
    "tasks-file": {
        "profile_label": "Task File",
        "format_label": "Task file JSON",
        "validation_label": "Task file shape",
    },
    "completed-ledger": {
        "profile_label": "Completed Milestones",
        "format_label": "Completed milestones JSON",
        "validation_label": "Completed milestone shape",
    },
    "workflow-plan": {
        "profile_label": "Workflow Plan",
        "format_label": "Workflow plan JSON",
        "validation_label": "Workflow step shape",
    },
    "workflow-spec": {
        "profile_label": "Workflow Spec",
        "format_label": "Workflow spec JSON",
        "validation_label": "Workflow phase shape",
    },
}


def describe_json_format_profile(
    *,
    target: str = "auto",
    source_path: str | Path | None = None,
    payload: Any | None = None,
) -> dict[str, str]:
    profile = detect_json_format_profile(
        target=target,
        source_path=source_path,
        payload=payload,
    )
    meta = _PROFILE_META[profile]
    return {"profile": profile, **meta}


def detect_json_format_profile(
    *,
    target: str = "auto",
    source_path: str | Path | None = None,
    payload: Any | None = None,
) -> str:
    normalized_target = str(target or "auto").strip().lower()
    explicit = {
        "auto": None,
        "json": "json",
        "generic": "json",
        "tasks": "tasks-ledger",
        "tasks-ledger": "tasks-ledger",
        "task-file": "tasks-file",
        "tasks-file": "tasks-file",
        "completed": "completed-ledger",
        "completed-ledger": "completed-ledger",
        "workflow": "workflow-plan",
        "workflow-plan": "workflow-plan",
        "workflow-spec": "workflow-spec",
    }.get(normalized_target)
    if explicit:
        return explicit

    path = Path(source_path) if source_path else None
    name = path.name.lower() if path else ""
    if name == "tasks.json":
        return "tasks-ledger"
    if name == "completed.json":
        return "completed-ledger"
    if name.endswith(".workflow.json"):
        return "workflow-plan"
    if name == "workflow.json":
        return "workflow-spec"

    if isinstance(payload, dict):
        if "active_missions" in payload:
            return "tasks-ledger"
        if "tasks" in payload:
            return "tasks-file"
        if "completed_milestones" in payload:
            return "completed-ledger"
        if "phases" in payload:
            return "workflow-spec"
        if "steps" in payload:
            return "workflow-plan"

    return "json"


def format_json_text(
    content: str,
    *,
    target: str = "auto",
    source_path: str | Path | None = None,
) -> JsonFormatResult:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    return format_json_payload(payload, target=target, source_path=source_path, original=content)


def format_json_payload(
    payload: Any,
    *,
    target: str = "auto",
    source_path: str | Path | None = None,
    original: str | None = None,
) -> JsonFormatResult:
    profile = detect_json_format_profile(
        target=target,
        source_path=source_path,
        payload=payload,
    )
    meta = _PROFILE_META[profile]
    canonical = _canonicalize_payload(payload, profile)
    errors = _validate_profile(canonical, profile)
    content = json.dumps(canonical, indent=2, ensure_ascii=False) + "\n"
    if original is None:
        changed = True
    else:
        changed = content != _ensure_trailing_newline(original)
    return JsonFormatResult(
        profile=profile,
        profile_label=meta["profile_label"],
        format_label=meta["format_label"],
        validation_label=meta["validation_label"],
        content=content,
        changed=changed,
        errors=errors,
    )


def _ensure_trailing_newline(content: str) -> str:
    return content if content.endswith("\n") else content + "\n"


def _canonicalize_payload(payload: Any, profile: str) -> Any:
    if profile == "tasks-ledger":
        return _canonicalize_tasks_ledger(payload)
    if profile == "tasks-file":
        return _canonicalize_tasks_file(payload)
    if profile == "completed-ledger":
        return _canonicalize_completed_ledger(payload)
    if profile == "workflow-plan":
        return _canonicalize_workflow_plan(payload)
    if profile == "workflow-spec":
        return _canonicalize_workflow_spec(payload)
    return _canonicalize_generic(payload)


def _canonicalize_generic(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _canonicalize_generic(value[key])
            for key in value.keys()
        }
    if isinstance(value, list):
        return [_canonicalize_generic(item) for item in value]
    return value


def _ordered_mapping(
    payload: dict[str, Any],
    preferred_keys: list[str],
    *,
    nested: dict[str, Any] | None = None,
) -> dict[str, Any]:
    nested = nested or {}
    ordered: dict[str, Any] = {}
    for key in preferred_keys:
        if key not in payload:
            continue
        ordered[key] = _transform_nested_value(key, payload[key], nested)
    for key in sorted(payload.keys()):
        if key in ordered:
            continue
        ordered[key] = _transform_nested_value(key, payload[key], nested)
    return ordered


def _transform_nested_value(key: str, value: Any, nested: dict[str, Any]) -> Any:
    handler = nested.get(key)
    if callable(handler):
        return handler(value)
    if isinstance(value, dict):
        return _canonicalize_generic(value)
    if isinstance(value, list):
        return [_canonicalize_generic(item) for item in value]
    return value


def _canonicalize_tasks_ledger(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return _canonicalize_generic(payload)
    return _ordered_mapping(
        payload,
        [
            "version",
            "workspace",
            "owner",
            "updated",
            "source_markdown",
            "active_missions",
            "metadata",
        ],
        nested={"active_missions": _canonicalize_missions},
    )


def _canonicalize_tasks_file(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return _canonicalize_generic(payload)
    return _ordered_mapping(
        payload,
        [
            "version",
            "workspace",
            "owner",
            "updated",
            "source_markdown",
            "tasks",
            "metadata",
        ],
        nested={"tasks": _canonicalize_task_items},
    )


def _canonicalize_completed_ledger(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return _canonicalize_generic(payload)
    return _ordered_mapping(
        payload,
        [
            "version",
            "workspace",
            "owner",
            "updated",
            "source_markdown",
            "completed_milestones",
            "metadata",
        ],
        nested={"completed_milestones": _canonicalize_completed_milestones},
    )


def _canonicalize_workflow_plan(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return _canonicalize_generic(payload)
    return _ordered_mapping(
        payload,
        [
            "id",
            "name",
            "workspace",
            "workflow_id",
            "template_id",
            "goal",
            "purpose",
            "constraints",
            "inputs",
            "steps",
            "outputs",
            "artifacts",
            "metadata",
        ],
        nested={
            "constraints": _canonicalize_generic,
            "inputs": _canonicalize_generic,
            "steps": _canonicalize_workflow_steps,
            "artifacts": _canonicalize_generic,
            "metadata": _canonicalize_generic,
        },
    )


def _canonicalize_workflow_spec(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return _canonicalize_generic(payload)
    return _ordered_mapping(
        payload,
        [
            "workflow_id",
            "template_id",
            "project",
            "goal",
            "purpose",
            "constraints",
            "inputs",
            "phases",
            "outputs",
            "created_at_iso",
            "source_path",
            "metadata",
        ],
        nested={
            "constraints": _canonicalize_generic,
            "inputs": _canonicalize_generic,
            "phases": _canonicalize_workflow_phases,
            "metadata": _canonicalize_generic,
        },
    )


def _canonicalize_missions(value: Any) -> Any:
    if not isinstance(value, list):
        return _canonicalize_generic(value)
    return [
        _ordered_mapping(
            item,
            [
                "id",
                "title",
                "status",
                "lane",
                "priority",
                "owner",
                "summary",
                "artifacts",
                "notes",
                "updated",
                "completed_date",
            ],
        )
        if isinstance(item, dict)
        else _canonicalize_generic(item)
        for item in value
    ]


def _canonicalize_task_items(value: Any) -> Any:
    if not isinstance(value, list):
        return _canonicalize_generic(value)
    return [
        _ordered_mapping(
            item,
            [
                "id",
                "task_id",
                "mission_id",
                "workflow_id",
                "title",
                "description",
                "item_type",
                "status",
                "priority",
                "lane",
                "assigned_to",
                "dependencies",
                "artifacts",
                "tags",
                "source",
                "source_id",
                "start_date",
                "end_date",
                "due_date",
                "organizer",
                "attendees",
                "metadata",
                "created",
                "updated",
            ],
        )
        if isinstance(item, dict)
        else _canonicalize_generic(item)
        for item in value
    ]


def _canonicalize_completed_milestones(value: Any) -> Any:
    if not isinstance(value, list):
        return _canonicalize_generic(value)
    return [
        _ordered_mapping(
            item,
            [
                "id",
                "name",
                "version",
                "completed_date",
                "summary",
                "tasks",
                "metrics",
                "notes",
            ],
            nested={"tasks": _canonicalize_completed_tasks, "metrics": _canonicalize_generic},
        )
        if isinstance(item, dict)
        else _canonicalize_generic(item)
        for item in value
    ]


def _canonicalize_completed_tasks(value: Any) -> Any:
    if not isinstance(value, list):
        return _canonicalize_generic(value)
    return [
        _ordered_mapping(
            item,
            ["id", "name", "completed_date", "owner", "notes"],
        )
        if isinstance(item, dict)
        else _canonicalize_generic(item)
        for item in value
    ]


def _canonicalize_workflow_steps(value: Any) -> Any:
    if not isinstance(value, list):
        return _canonicalize_generic(value)
    return [
        _ordered_mapping(
            item,
            [
                "step_id",
                "name",
                "action",
                "adapter",
                "prompt_name",
                "requires_online",
                "requires_user_approval",
                "inputs",
                "outputs",
                "provider_hint",
                "budget",
                "metadata",
            ],
            nested={
                "provider_hint": _canonicalize_provider_hint,
                "budget": _canonicalize_budget,
                "metadata": _canonicalize_generic,
            },
        )
        if isinstance(item, dict)
        else _canonicalize_generic(item)
        for item in value
    ]


def _canonicalize_workflow_phases(value: Any) -> Any:
    if not isinstance(value, list):
        return _canonicalize_generic(value)
    return [
        _ordered_mapping(
            item,
            [
                "name",
                "adapter",
                "prompt_name",
                "inputs",
                "outputs",
                "requires_user_approval",
                "provider_hint",
                "budget",
            ],
            nested={
                "provider_hint": _canonicalize_provider_hint,
                "budget": _canonicalize_budget,
            },
        )
        if isinstance(item, dict)
        else _canonicalize_generic(item)
        for item in value
    ]


def _canonicalize_provider_hint(value: Any) -> Any:
    if not isinstance(value, dict):
        return _canonicalize_generic(value)
    return _ordered_mapping(
        value,
        ["quality", "needs_web", "needs_image", "needs_audio", "needs_video"],
    )


def _canonicalize_budget(value: Any) -> Any:
    if not isinstance(value, dict):
        return _canonicalize_generic(value)
    return _ordered_mapping(value, ["max_cost_usd", "max_tokens"])


def _validate_profile(payload: Any, profile: str) -> list[str]:
    if profile == "tasks-ledger":
        return _validate_tasks_ledger(payload)
    if profile == "tasks-file":
        return _validate_tasks_file(payload)
    if profile == "completed-ledger":
        return _validate_completed_ledger(payload)
    if profile == "workflow-plan":
        return _validate_workflow_plan(payload)
    if profile == "workflow-spec":
        return _validate_workflow_spec(payload)
    return []


def _validate_tasks_ledger(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["$: expected object"]
    missions = payload.get("active_missions")
    if missions is None:
        return []
    if not isinstance(missions, list):
        return ["$: `active_missions` must be an array"]
    return _validate_dict_sequence(
        missions,
        path="$.active_missions",
        required=("id", "title", "status"),
    )


def _validate_tasks_file(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["$: expected object"]
    if "tasks" not in payload:
        return []
    result = validate_tasks_file_payload(payload)
    return list(result.errors)


def _validate_completed_ledger(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["$: expected object"]
    milestones = payload.get("completed_milestones")
    if milestones is None:
        return []
    if not isinstance(milestones, list):
        return ["$: `completed_milestones` must be an array"]
    errors = _validate_dict_sequence(
        milestones,
        path="$.completed_milestones",
        required=("id", "name"),
    )
    for index, item in enumerate(milestones):
        if not isinstance(item, dict):
            continue
        tasks = item.get("tasks")
        if tasks is None:
            continue
        if not isinstance(tasks, list):
            errors.append(f"$.completed_milestones[{index}].tasks: expected array")
            continue
        errors.extend(
            _validate_dict_sequence(
                tasks,
                path=f"$.completed_milestones[{index}].tasks",
                required=("id", "name"),
            )
        )
    return errors


def _validate_workflow_plan(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["$: expected object"]
    steps = payload.get("steps")
    if steps is None:
        return []
    workflow_id = str(payload.get("workflow_id") or payload.get("id") or "").strip()
    if not workflow_id:
        return ["$: `workflow_id` or `id` is required when `steps` are present"]
    result = validate_workflow_record(
        {
            "workflow_id": workflow_id,
            "steps": list(steps) if isinstance(steps, list) else steps,
        }
    )
    return list(result.errors)


def _validate_workflow_spec(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["$: expected object"]
    phases = payload.get("phases")
    if phases is None:
        return []
    if not isinstance(phases, list):
        return ["$: `phases` must be an array"]
    workflow_id = str(payload.get("workflow_id") or "").strip()
    if not workflow_id:
        return ["$: `workflow_id` is required when `phases` are present"]
    steps: list[dict[str, Any]] = []
    for index, item in enumerate(phases):
        if not isinstance(item, dict):
            return [f"$.phases[{index}]: expected object"]
        steps.append(
            {
                "step_id": item.get("name", ""),
                "action": item.get("prompt_name", ""),
                "requires_online": bool(
                    ((item.get("provider_hint") or {}) if isinstance(item.get("provider_hint"), dict) else {}).get(
                        "needs_web",
                        False,
                    )
                ),
            }
        )
    result = validate_workflow_record({"workflow_id": workflow_id, "steps": steps})
    return list(result.errors)


def _validate_dict_sequence(
    items: list[Any],
    *,
    path: str,
    required: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_path}: expected object")
            continue
        for key in required:
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{item_path}: `{key}` must be a non-empty string")
    return errors
