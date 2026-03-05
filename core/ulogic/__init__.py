"""
Deterministic offline logic primitives for the v1.5 runtime.

This package is the first promoted `core/ulogic` slice from the
`docs/examples/udos_ulogic_pack/` reference scaffold.
"""

from .contracts import IntentFrame, RoutingOutcome
from .action_graph import ActionGraph, ActionNode, ExecutionResult
from .artifact_store import ArtifactStore
from .deliverables import (
    ValidationResult,
    validate_deliverable,
    validate_completed_file_payload,
    validate_project_file_payload,
    validate_project_record,
    validate_tasks_file_payload,
    validate_task_record,
    validate_wizard_budget_record,
    validate_workflow_record,
)
from .format_helpers import (
    JsonFormatResult,
    describe_json_format_profile,
    detect_json_format_profile,
    format_json_payload,
    format_json_text,
)
from .parser import parse_input, parse_primary_input
from .research_pipeline import (
    CanonicalDocument,
    EnrichedDocument,
    GeneratedArtifact,
    ResearchRequest,
    enrich_document,
    generate_artifact,
    normalize_research_input,
)
from .runtime import ULogicRuntime
from .script_sandbox import SandboxError, ScriptSandbox
from .state_store import ULogicStateStore

__all__ = [
    "ActionGraph",
    "ActionNode",
    "ArtifactStore",
    "CanonicalDocument",
    "EnrichedDocument",
    "ExecutionResult",
    "IntentFrame",
    "GeneratedArtifact",
    "JsonFormatResult",
    "ResearchRequest",
    "RoutingOutcome",
    "SandboxError",
    "ScriptSandbox",
    "ULogicRuntime",
    "ULogicStateStore",
    "ValidationResult",
    "describe_json_format_profile",
    "detect_json_format_profile",
    "enrich_document",
    "format_json_payload",
    "format_json_text",
    "generate_artifact",
    "parse_input",
    "parse_primary_input",
    "normalize_research_input",
    "validate_completed_file_payload",
    "validate_deliverable",
    "validate_project_file_payload",
    "validate_project_record",
    "validate_tasks_file_payload",
    "validate_task_record",
    "validate_wizard_budget_record",
    "validate_workflow_record",
]
