from __future__ import annotations

import pytest

from wizard.services.graphics_service import GraphicsService


def test_generate_teletext_pattern():
    service = GraphicsService()
    result = service.generate_teletext_pattern("scanlines", width=40)
    assert result.kind == "teletext"
    assert result.engine == "teletext"
    assert isinstance(result.content, str)
    assert result.content


def test_render_markdown_diagram_rejects_unknown_engine():
    service = GraphicsService()
    with pytest.raises(RuntimeError, match="Unsupported graphics engine"):
        service.render_markdown_diagram("graph TD; A-->B;", engine="unknown")
