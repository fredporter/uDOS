from core.input.autocomplete import AutocompleteService
from core.input.smart_prompt import CoreCompleter


def _collect_text(completions):
    return [c.text for c in completions]


def test_core_completer_slash_commands():
    from prompt_toolkit.document import Document

    completer = CoreCompleter(AutocompleteService())
    doc = Document(text="/st", cursor_position=3)
    items = list(completer.get_completions(doc, None))
    texts = _collect_text(items)
    assert "atus" in texts


def test_core_completer_path_suggestions(tmp_path, monkeypatch):
    from prompt_toolkit.document import Document

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "README.md").write_text("x")
    monkeypatch.chdir(tmp_path)

    completer = CoreCompleter(AutocompleteService())
    doc = Document(text="@do", cursor_position=3)
    items = list(completer.get_completions(doc, None))
    texts = _collect_text(items)
    assert any(text.startswith("@docs") for text in texts)
