from pathlib import Path

from core.services.script_policy import check_markdown_stdlib_policy


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content)
    return path


def test_blocks_ucode_commands_in_script_fence_by_default(tmp_path):
    script = _write(
        tmp_path,
        "mobile-default.md",
        """---
title: Mobile Default
---

## Start
```script
$state.mode = "boot"
DRAW PAT TEXT "hello"
```
""",
    )
    result = check_markdown_stdlib_policy(script)
    assert result is not None
    assert result["status"] == "error"
    assert "allow_stdlib_commands: true" in result["details"]


def test_allows_ucode_commands_when_frontmatter_opt_in(tmp_path):
    script = _write(
        tmp_path,
        "explicit-opt-in.md",
        """---
title: Explicit
allow_stdlib_commands: true
---

## Start
```script
DRAW PAT TEXT "hello"
```
""",
    )
    assert check_markdown_stdlib_policy(script) is None


def test_ignores_non_script_fences_and_plain_text(tmp_path):
    script = _write(
        tmp_path,
        "non-script.md",
        """---
title: Plain
---

RUN this-line-is-just-documentation

```text
DRAW PAT TEXT "not executable"
```
""",
    )
    assert check_markdown_stdlib_policy(script) is None
