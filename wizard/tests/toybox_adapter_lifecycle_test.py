from wizard.services.toybox.base_adapter import PTYAdapter


def _mk_adapter():
    return PTYAdapter(
        adapter_id="test",
        env_cmd_var="TOYBOX_TEST_CMD",
        command_candidates=["missing-test-bin"],
        max_start_retries=3,
        retry_backoff_seconds=[0.0, 0.0, 0.0],
    )


def test_adapter_start_retries_then_running(monkeypatch):
    adapter = _mk_adapter()
    attempts = {"n": 0}

    monkeypatch.setattr(adapter, "_resolve_command", lambda: ["dummy-cmd"])
    monkeypatch.setattr(adapter, "_probe_pid_alive", lambda pid: True)

    def _attempt_start(_cmd):
        attempts["n"] += 1
        if attempts["n"] < 3:
            adapter.running = False
            adapter.proc_pid = None
            return False
        adapter.running = True
        adapter.proc_pid = 4242
        return True

    monkeypatch.setattr(adapter, "_attempt_start", _attempt_start)

    adapter.start()
    status = adapter.status()
    assert status["state"] == "running"
    assert status["retries"] == 2
    assert status["health"] == "ok"
    assert attempts["n"] == 3


def test_adapter_start_transitions_failed_after_retry_budget(monkeypatch):
    adapter = _mk_adapter()
    monkeypatch.setattr(adapter, "_resolve_command", lambda: ["dummy-cmd"])
    monkeypatch.setattr(adapter, "_attempt_start", lambda _cmd: False)

    raised = False
    try:
        adapter.start()
    except RuntimeError:
        raised = True

    assert raised is True
    status = adapter.status()
    assert status["state"] == "failed"
    assert status["retries"] == 3
    assert status["health"] == "fail"


def test_adapter_status_includes_lifecycle_contract_fields():
    adapter = _mk_adapter()
    status = adapter.status()
    required = {"adapter_id", "state", "pid", "retries", "last_error", "last_transition_at", "health"}
    assert required.issubset(set(status.keys()))
    assert status["state"] == "stopped"
