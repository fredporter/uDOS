from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class ResearchRequest:
    topic: str
    source_type: str
    source_ref: str
    project_id: str = ""
    binder_id: str = ""
    mission_id: str = ""
    task_id: str = ""
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class CanonicalDocument:
    uid: str
    title: str
    source_type: str
    source_ref: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""

    def to_markdown(self) -> str:
        lines = ["---"]
        for key, value in self.frontmatter.items():
            lines.extend(_yaml_lines(key, value))
        lines.extend(["---", "", f"# {self.title}", ""])
        if self.body:
            lines.append(self.body.rstrip())
        return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class EnrichedDocument:
    document: CanonicalDocument
    summary: str
    related_projects: tuple[str, ...] = ()
    related_binders: tuple[str, ...] = ()
    suggested_tasks: tuple[str, ...] = ()


@dataclass(frozen=True)
class GeneratedArtifact:
    artifact_kind: str
    title: str
    markdown: str


def normalize_research_input(
    request: ResearchRequest,
    *,
    title: str,
    body: str,
    metadata: dict[str, Any] | None = None,
) -> CanonicalDocument:
    normalized_metadata = dict(metadata or {})
    uid = _stable_uid(request.source_type, request.source_ref, title, body)
    frontmatter: dict[str, Any] = {
        "udos_id": uid,
        "type": "research-note",
        "source_type": request.source_type,
        "source_ref": request.source_ref,
        "topic": request.topic,
        "offline_ok": True,
        "tags": list(request.tags),
    }
    if request.project_id:
        frontmatter["related_projects"] = [request.project_id]
    if request.binder_id:
        frontmatter["related_binders"] = [request.binder_id]
    if request.mission_id:
        frontmatter["related_missions"] = [request.mission_id]
    if request.task_id:
        frontmatter["related_tasks"] = [request.task_id]
    frontmatter.update(normalized_metadata)
    return CanonicalDocument(
        uid=uid,
        title=title.strip() or request.topic,
        source_type=request.source_type,
        source_ref=request.source_ref,
        frontmatter=frontmatter,
        body=body.strip(),
    )


def enrich_document(
    document: CanonicalDocument,
    *,
    active_projects: list[str] | None = None,
    active_binders: list[str] | None = None,
) -> EnrichedDocument:
    project_hits = tuple(
        _merge_hits(
            _frontmatter_hits(document.frontmatter, "related_projects"),
            _related_hits(document.body, active_projects or []),
        )
    )
    binder_hits = tuple(
        _merge_hits(
            _frontmatter_hits(document.frontmatter, "related_binders"),
            _related_hits(document.body, active_binders or []),
        )
    )
    summary = summarize_markdown(document.body)
    suggested_tasks = tuple(_suggest_tasks(document.body))
    return EnrichedDocument(
        document=document,
        summary=summary,
        related_projects=project_hits,
        related_binders=binder_hits,
        suggested_tasks=suggested_tasks,
    )


def generate_artifact(
    enriched: EnrichedDocument,
    *,
    artifact_kind: str,
) -> GeneratedArtifact:
    title = f"{artifact_kind.title()}: {enriched.document.title}"
    lines = [
        f"# {title}",
        "",
        "## Purpose",
        f"Deterministic {artifact_kind} derived from canonical Markdown research content.",
        "",
        "## Summary",
        enriched.summary or "No summary available.",
        "",
        "## Source",
        f"- type: {enriched.document.source_type}",
        f"- ref: {enriched.document.source_ref}",
    ]
    if enriched.related_projects:
        lines.extend(["", "## Related Projects"])
        lines.extend(f"- {item}" for item in enriched.related_projects)
    if enriched.related_binders:
        lines.extend(["", "## Related Binders"])
        lines.extend(f"- {item}" for item in enriched.related_binders)
    if enriched.suggested_tasks:
        lines.extend(["", "## Suggested Tasks"])
        lines.extend(f"- {item}" for item in enriched.suggested_tasks)
    lines.extend(["", "## Canonical Content", enriched.document.body or "(empty)"])
    return GeneratedArtifact(
        artifact_kind=artifact_kind,
        title=title,
        markdown="\n".join(lines).rstrip() + "\n",
    )


def summarize_markdown(body: str, *, max_sentences: int = 2) -> str:
    cleaned = " ".join(part.strip() for part in body.splitlines() if part.strip())
    if not cleaned:
        return ""
    sentences = [part.strip() for part in cleaned.split(".") if part.strip()]
    return ". ".join(sentences[:max_sentences]).strip() + (
        "." if sentences else ""
    )


def _stable_uid(*parts: str) -> str:
    joined = "::".join(part.strip() for part in parts if part.strip())
    return sha256(joined.encode("utf-8")).hexdigest()[:16]


def _related_hits(body: str, active_ids: list[str]) -> list[str]:
    lowered = body.lower()
    hits: list[str] = []
    for item in active_ids:
        if item and item.lower() in lowered:
            hits.append(item)
    return hits


def _frontmatter_hits(frontmatter: dict[str, Any], key: str) -> list[str]:
    value = frontmatter.get(key, [])
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _merge_hits(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            if item in seen:
                continue
            seen.add(item)
            merged.append(item)
    return merged


def _suggest_tasks(body: str) -> list[str]:
    suggestions: list[str] = []
    lowered = body.lower()
    if "compare" in lowered:
        suggestions.append("Create comparison note from ingested source")
    if "install" in lowered or "setup" in lowered:
        suggestions.append("Create setup runbook from canonical source")
    if "budget" in lowered or "cost" in lowered:
        suggestions.append("Review budget and escalation policy impact")
    return suggestions


def _yaml_lines(key: str, value: Any) -> list[str]:
    if isinstance(value, bool):
        return [f"{key}: {'true' if value else 'false'}"]
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [f"{key}: {value}"]
    if isinstance(value, str):
        return [f'{key}: "{value}"']
    if isinstance(value, list):
        lines = [f"{key}:"]
        for item in value:
            lines.append(f'  - "{item}"')
        return lines
    return [f'{key}: "{value}"']
