from wizard.routes.ucode_ok_dispatch_core import dispatch_ok_command


class _Logger:
    def info(self, *_args, **_kwargs):
        return None

    def warn(self, *_args, **_kwargs):
        return None


def test_dispatch_ok_command_returns_none_for_non_ok():
    response = dispatch_ok_command(
        command="HELP",
        corr_id="C1",
        logger=_Logger(),
        ok_history=[],
        ok_model=None,
        load_ai_modes_config=lambda: {"modes": {}},
        write_ok_modes_config=lambda _cfg: None,
        ok_auto_fallback_enabled=lambda: True,
        get_ok_default_model=lambda: "m1",
        run_ok_local=lambda prompt, model: "local",
        run_ok_cloud=lambda prompt: ("cloud", "c1"),
        ok_cloud_available=lambda: True,
        record_ok_output=lambda **kwargs: kwargs,
        is_dev_mode_active=lambda: False,
        resolve_ok_model=lambda model, _purpose: model or "m1",
    )
    assert response is None


def test_dispatch_ok_command_history_mode():
    response = dispatch_ok_command(
        command="OK LOCAL 1",
        corr_id="C1",
        logger=_Logger(),
        ok_history=[{"id": 1}, {"id": 2}],
        ok_model=None,
        load_ai_modes_config=lambda: {"modes": {}},
        write_ok_modes_config=lambda _cfg: None,
        ok_auto_fallback_enabled=lambda: True,
        get_ok_default_model=lambda: "m1",
        run_ok_local=lambda prompt, model: "local",
        run_ok_cloud=lambda prompt: ("cloud", "c1"),
        ok_cloud_available=lambda: True,
        record_ok_output=lambda **kwargs: kwargs,
        is_dev_mode_active=lambda: False,
        resolve_ok_model=lambda model, _purpose: model or "m1",
    )
    assert response is not None
    assert len(response["ok_history"]) == 1


def test_dispatch_ok_command_prompt_local_success():
    recorded = {}

    def _record(**kwargs):
        recorded.update(kwargs)
        return {"id": 9, **kwargs}

    response = dispatch_ok_command(
        command="OK summarize this",
        corr_id="C1",
        logger=_Logger(),
        ok_history=[],
        ok_model=None,
        load_ai_modes_config=lambda: {"modes": {}},
        write_ok_modes_config=lambda _cfg: None,
        ok_auto_fallback_enabled=lambda: True,
        get_ok_default_model=lambda: "m1",
        run_ok_local=lambda prompt, model: "local-ok",
        run_ok_cloud=lambda prompt: ("cloud-ok", "c1"),
        ok_cloud_available=lambda: True,
        record_ok_output=_record,
        is_dev_mode_active=lambda: False,
        resolve_ok_model=lambda model, _purpose: model or "m1",
    )
    assert response is not None
    assert response["result"]["output"] == "local-ok"
    assert recorded["mode"] == "LOCAL"
