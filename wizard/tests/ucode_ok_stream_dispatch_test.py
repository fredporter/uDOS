from wizard.routes.ucode_ok_stream_dispatch import dispatch_ok_stream_command


class _Logger:
    def info(self, *_args, **_kwargs):
        return None

    def warn(self, *_args, **_kwargs):
        return None


def test_dispatch_ok_stream_returns_none_for_non_ok():
    response = dispatch_ok_stream_command(
        command="HELP",
        corr_id="C1",
        logger=_Logger(),
        ok_model=None,
        is_dev_mode_active=lambda: True,
        resolve_ok_model=lambda model, _purpose: model or "m1",
        ok_auto_fallback_enabled=lambda: True,
        run_ok_local_stream=lambda prompt, model: ["x"],
        run_ok_cloud=lambda prompt: ("cloud", "c1"),
        ok_cloud_available=lambda: True,
        record_ok_output=lambda **kwargs: kwargs,
    )
    assert response is None


def test_dispatch_ok_stream_explain_mode(tmp_path):
    file_path = tmp_path / "x.py"
    file_path.write_text("print('x')\n", encoding="utf-8")

    response = dispatch_ok_stream_command(
        command=f"OK EXPLAIN {file_path}",
        corr_id="C1",
        logger=_Logger(),
        ok_model=None,
        is_dev_mode_active=lambda: True,
        resolve_ok_model=lambda model, _purpose: model or "m1",
        ok_auto_fallback_enabled=lambda: True,
        run_ok_local_stream=lambda prompt, model: ["part1", "part2"],
        run_ok_cloud=lambda prompt: ("cloud", "c1"),
        ok_cloud_available=lambda: True,
        record_ok_output=lambda **kwargs: {"id": 1, **kwargs},
    )
    assert response is not None
    assert response["chunks"] == ["part1", "part2"]
    assert response["response"]["result"]["status"] == "success"
