from wizard.routes import setup_route_utils as utils


def test_is_ghost_mode_variants():
    assert utils.is_ghost_mode("Ghost", "admin") is True
    assert utils.is_ghost_mode("alice", "ghost") is True
    assert utils.is_ghost_mode("alice", "admin") is False


def test_apply_setup_defaults_sets_values_and_meta():
    story = {
        "sections": [
            {
                "questions": [
                    {"name": "user_timezone", "meta": None},
                    {"name": "user_local_time", "meta": {}},
                ]
            }
        ],
        "answers": {},
    }
    utils.apply_setup_defaults(
        story,
        {
            "user_timezone": "UTC",
            "user_local_time": "2026-01-01 12:00",
        },
        highlight_fields=["user_timezone"],
    )
    assert story["answers"]["user_timezone"] == "UTC"
    assert story["sections"][0]["questions"][0]["meta"]["show_previous_overlay"] is True


def test_load_env_identity_reads_expected_fields(monkeypatch, tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    (repo_root / ".env").write_text(
        "USER_NAME=alice\nUDOS_TIMEZONE=UTC\nOS_TYPE=linux\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(utils, "get_repo_root", lambda: repo_root)
    identity = utils.load_env_identity()
    assert identity["user_username"] == "alice"
    assert identity["user_timezone"] == "UTC"
    assert identity["install_os_type"] == "linux"
