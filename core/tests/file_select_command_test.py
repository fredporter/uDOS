from pathlib import Path

from core.commands.file_handler import FileHandler
from core.services.spatial_filesystem import UserRole


def test_file_select_requires_flags_in_non_interactive_mode():
    handler = FileHandler()
    handler.user_role = UserRole.ADMIN
    result = handler.handle("FILE", ["SELECT"])
    assert result["status"] == "error"
    assert "--file" in result.get("message", "") or "--file" in result.get("suggestion", "")


def test_file_select_accepts_non_interactive_single_file():
    target = Path("memory/vault/file-select-single.txt")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("single file test\n", encoding="utf-8")

    try:
        handler = FileHandler()
        handler.user_role = UserRole.ADMIN
        result = handler.handle("FILE", ["SELECT", "--file", "file-select-single.txt"])
        assert result["status"] == "success"
        assert "@vault/file-select-single.txt" in result.get("selected_files", [])
    finally:
        if target.exists():
            target.unlink()


def test_file_select_accepts_non_interactive_multi_files():
    a = Path("memory/vault/file-select-a.txt")
    b = Path("memory/vault/file-select-b.txt")
    a.parent.mkdir(parents=True, exist_ok=True)
    a.write_text("A\n", encoding="utf-8")
    b.write_text("B\n", encoding="utf-8")

    try:
        handler = FileHandler()
        handler.user_role = UserRole.ADMIN
        result = handler.handle(
            "FILE",
            ["SELECT", "--workspace", "@vault", "--files", "file-select-a.txt,file-select-b.txt"],
        )
        assert result["status"] == "success"
        selected = result.get("selected_files", [])
        assert "@vault/file-select-a.txt" in selected
        assert "@vault/file-select-b.txt" in selected
    finally:
        if a.exists():
            a.unlink()
        if b.exists():
            b.unlink()
