"""
Deterministic offline logic primitives for the v1.5 runtime.

This package is the first promoted `core/ulogic` slice from the
`docs/examples/udos_ulogic_pack/` reference scaffold.
"""

from .contracts import IntentFrame, RoutingOutcome
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

__all__ = [
    "CanonicalDocument",
    "EnrichedDocument",
    "IntentFrame",
    "GeneratedArtifact",
    "ResearchRequest",
    "RoutingOutcome",
    "ValidationResult",
    "enrich_document",
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
