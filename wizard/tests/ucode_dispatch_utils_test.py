import subprocess

from fastapi import HTTPException

from wizard.routes import ucode_dispatch_utils as utils


class _Logger:
    def info(self, *_args, **_kwargs):
        return None

    def warn(self, *_args, **_kwargs):
        return None


def test_handle_slash_command_passthrough_allowlisted():
    logger = _Logger()
    command, response = utils.handle_slash_command(
        command="/help",
        allowlist={"HELP"},
        shell_allowed=lambda: False,
        shell_safe=lambda _cmd: True,
        logger=logger,
        corr_id="C1",
    )
    assert command == "help"
    assert response is None


def test_handle_slash_command_blocks_destructive():
    logger = _Logger()
    try:
        utils.handle_slash_command(
            command="/rm -rf /tmp/x",
            allowlist={"HELP"},
            shell_allowed=lambda: True,
            shell_safe=lambda _cmd: False,
            logger=logger,
            corr_id="C1",
        )
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403


def test_handle_slash_command_executes_shell(monkeypatch):
    class Result:
        returncode = 0
        stdout = "ok"
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: Result())
    logger = _Logger()
    command, response = utils.handle_slash_command(
        command="/echo ok",
        allowlist={"HELP"},
        shell_allowed=lambda: True,
        shell_safe=lambda _cmd: True,
        logger=logger,
        corr_id="C1",
    )
    assert command == "/echo ok"
    assert response is not None
    assert response["result"]["status"] == "success"


def test_dispatch_non_ok_setup_story():
    logger = _Logger()
    response = utils.dispatch_non_ok_command(
        command="SETUP",
        allowlist={"SETUP"},
        dispatcher=None,
        game_state=None,
        renderer=None,
        load_setup_story=lambda: {"frontmatter": {"title": "x"}, "sections": []},
        logger=logger,
        corr_id="C1",
    )
    assert response["status"] == "ok"
    assert response["result"]["message"] == "Setup story ready"


def test_dispatch_non_ok_allowlisted_dispatch():
    class Dispatcher:
        def dispatch(self, command, game_state=None):
            return {"status": "success", "output": f"ran {command}"}

    class Renderer:
        def render(self, result):
            return "rendered"

    logger = _Logger()
    response = utils.dispatch_non_ok_command(
        command="HELP",
        allowlist={"HELP"},
        dispatcher=Dispatcher(),
        game_state=object(),
        renderer=Renderer(),
        load_setup_story=lambda: {},
        logger=logger,
        corr_id="C1",
    )
    assert response["result"]["status"] == "success"
    assert response["rendered"] == "rendered"
