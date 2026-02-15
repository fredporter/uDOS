from pathlib import Path

from core.commands.sonic_handler import SonicHandler


class _FakeSonicHandler(SonicHandler):
    def __init__(self, repo_root: Path, sonic_root: Path):
        super().__init__()
        self._repo = repo_root
        self._sonic = sonic_root

    def _repo_root(self) -> Path:  # type: ignore[override]
        return self._repo

    def _sonic_root(self) -> Path:  # type: ignore[override]
        return self._sonic


def test_sonic_handler_fallback_when_sonic_missing(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=repo_root / "sonic")
    result = handler.handle("SONIC", ["STATUS"])

    assert result["status"] == "error"
    assert "not installed" in result["message"].lower()


def test_sonic_sync_requires_sql(tmp_path):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    (sonic_root / "datasets").mkdir(parents=True, exist_ok=True)

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    result = handler.handle("SONIC", ["SYNC"])

    assert result["status"] == "error"
    assert "dataset sql missing" in result["message"].lower()


def test_sonic_sync_no_force_if_db_exists(tmp_path):
    repo_root = tmp_path / "repo"
    sonic_root = repo_root / "sonic"
    datasets = sonic_root / "datasets"
    datasets.mkdir(parents=True, exist_ok=True)
    (datasets / "sonic-devices.sql").write_text("CREATE TABLE devices(id TEXT);\n", encoding="utf-8")

    db_path = repo_root / "memory" / "sonic" / "sonic-devices.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.write_bytes(b"placeholder")

    handler = _FakeSonicHandler(repo_root=repo_root, sonic_root=sonic_root)
    result = handler.handle("SONIC", ["SYNC"])

    assert result["status"] == "ok"
    assert "already exists" in result["message"].lower()
    assert result["db_path"].endswith("sonic-devices.db")
