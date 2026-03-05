"""Wizard graphics facade for Markdown-safe SVG and text graphics flows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import tempfile

from wizard.services.path_utils import get_memory_dir, get_repo_root
from wizard.services.teletext_patterns import PatternName, TeletextPatternService


@dataclass(frozen=True)
class GraphicsArtifact:
    kind: str
    content: str
    output_file: str | None = None
    engine: str | None = None


class GraphicsService:
    """Unify the supported Wizard graphics entrypoints behind one service."""

    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or get_repo_root()
        self.memory_dir = get_memory_dir()
        self.patterns = TeletextPatternService()

    def render_mermaid_svg(self, source: str, output_file: str | None = None) -> GraphicsArtifact:
        mmdc = shutil.which("mmdc")
        if not mmdc:
            raise RuntimeError("Mermaid renderer unavailable (mmdc not installed)")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            in_file = tmp / "diagram.mmd"
            out_file = tmp / "diagram.svg"
            in_file.write_text(source, encoding="utf-8")
            proc = subprocess.run(
                [mmdc, "-i", str(in_file), "-o", str(out_file)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if proc.returncode != 0 or not out_file.exists():
                detail = (proc.stderr or proc.stdout or "diagram render failed").strip()
                raise RuntimeError(detail[:4000])
            svg = out_file.read_text(encoding="utf-8")

        saved_path = None
        if output_file:
            out_root = self.memory_dir / "diagrams"
            out_root.mkdir(parents=True, exist_ok=True)
            candidate = (out_root / output_file).resolve()
            if not str(candidate).startswith(str(out_root.resolve())):
                raise RuntimeError("Invalid output file path")
            if candidate.suffix.lower() != ".svg":
                raise RuntimeError("output_file must end with .svg")
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text(svg, encoding="utf-8")
            saved_path = str(candidate)

        return GraphicsArtifact(kind="svg", content=svg, output_file=saved_path, engine="mermaid")

    def generate_teletext_pattern(self, name: str = "chevrons", width: int = 64) -> GraphicsArtifact:
        pattern = PatternName(name)
        lines = self.patterns.next_frame(pattern, width=width, ascii_only=False)
        return GraphicsArtifact(
            kind="teletext",
            content="\n".join(lines),
            engine="teletext",
        )

    def render_markdown_diagram(self, source: str, engine: str = "mermaid") -> GraphicsArtifact:
        if engine != "mermaid":
            raise RuntimeError(f"Unsupported graphics engine: {engine}")
        svg = self.render_mermaid_svg(source)
        markdown = f"```svg\n{svg.content}\n```"
        return GraphicsArtifact(kind="markdown", content=markdown, engine=engine)


_graphics_service: GraphicsService | None = None


def get_graphics_service(repo_root: Path | None = None) -> GraphicsService:
    global _graphics_service
    if repo_root is not None:
        return GraphicsService(repo_root=repo_root)
    if _graphics_service is None:
        _graphics_service = GraphicsService()
    return _graphics_service
