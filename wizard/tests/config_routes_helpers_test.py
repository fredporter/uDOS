import json

from wizard.routes.config_routes_helpers import ConfigRouteHelpers


def test_list_config_files_reports_existing_and_templates(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "wizard.json").write_text("{}")
    (config_dir / "assistant_keys.example.json").write_text("{}")

    helpers = ConfigRouteHelpers(config_dir)
    files = helpers.list_config_files()
    by_id = {item["id"]: item for item in files}

    assert by_id["wizard"]["exists"] is True
    assert by_id["assistant_keys"]["is_example"] is True


def test_save_and_load_config_roundtrip(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    helpers = ConfigRouteHelpers(config_dir)

    saved = helpers.save_config_payload("oauth", {"content": {"provider": "github"}})
    assert saved["success"] is True

    loaded = helpers.load_config_payload("oauth")
    assert loaded["content"]["provider"] == "github"


def test_import_preview_and_chunked(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    helpers = ConfigRouteHelpers(config_dir)

    import_data = {
        "export_timestamp": "2026-02-15T00:00:00Z",
        "exported_from": "uDOS Wizard Server",
        "configs": {
            "wizard": {"filename": "wizard.json", "content": {"mode": "enabled"}}
        },
    }

    preview = helpers.preview_import(import_data)
    assert preview["success"] is True
    assert "wizard" in preview["preview"]

    applied = helpers.import_chunked(import_data, overwrite_conflicts=True)
    assert applied["success"] is True
    assert "wizard" in applied["imported"]

    assert json.loads((config_dir / "wizard.json").read_text())["mode"] == "enabled"
