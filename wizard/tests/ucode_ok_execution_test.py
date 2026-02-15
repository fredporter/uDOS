from fastapi import HTTPException

from wizard.routes import ucode_ok_execution as utils


def test_run_ok_with_fallback_local_success():
    response, model, source = utils.run_ok_with_fallback(
        prompt="hello",
        model="m1",
        use_cloud=False,
        auto_fallback=True,
        run_local=lambda prompt, model: "local-ok",
        run_cloud=lambda prompt: ("cloud-ok", "c1"),
        cloud_available=lambda: True,
        local_failure_detail="failed",
    )
    assert response == "local-ok"
    assert model == "m1"
    assert source == "local"


def test_run_ok_with_fallback_cloud_when_requested():
    response, model, source = utils.run_ok_with_fallback(
        prompt="hello",
        model="m1",
        use_cloud=True,
        auto_fallback=True,
        run_local=lambda prompt, model: "local-ok",
        run_cloud=lambda prompt: ("cloud-ok", "c1"),
        cloud_available=lambda: True,
        local_failure_detail="failed",
    )
    assert response == "cloud-ok"
    assert model == "c1"
    assert source == "cloud"


def test_run_ok_with_fallback_raises_when_cloud_required_missing_key():
    try:
        utils.run_ok_with_fallback(
            prompt="hello",
            model="m1",
            use_cloud=True,
            auto_fallback=False,
            run_local=lambda prompt, model: "local-ok",
            run_cloud=lambda prompt: ("cloud-ok", "c1"),
            cloud_available=lambda: False,
            local_failure_detail="failed",
        )
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 400


def test_run_ok_stream_with_fallback_local_stream_then_emit():
    chunks = []
    response, model, source = utils.run_ok_stream_with_fallback(
        prompt="hello",
        model="m1",
        use_cloud=False,
        auto_fallback=True,
        run_local_stream=lambda prompt, model: ["a", "b"],
        run_cloud=lambda prompt: ("cloud-ok", "c1"),
        cloud_available=lambda: True,
        emit_chunk=chunks.append,
    )
    assert chunks == ["a", "b"]
    assert response == "ab"
    assert model == "m1"
    assert source == "local"


def test_run_ok_stream_with_fallback_cloud_fallback():
    chunks = []
    response, model, source = utils.run_ok_stream_with_fallback(
        prompt="hello",
        model="m1",
        use_cloud=False,
        auto_fallback=True,
        run_local_stream=lambda prompt, model: (_ for _ in ()).throw(Exception("fail")),
        run_cloud=lambda prompt: ("cloud-ok", "c1"),
        cloud_available=lambda: True,
        emit_chunk=chunks.append,
    )
    assert chunks == ["cloud-ok"]
    assert response == "cloud-ok"
    assert model == "c1"
    assert source == "cloud"
