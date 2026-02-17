import io
import threading
import time

import pytest

from core.tui.ucode import IOLifecyclePhase, UCLI


class _TTYBuffer(io.StringIO):
    def isatty(self):
        return True


class _FakeStatusBar:
    def get_status_line(self, user_role="ghost", ghost_mode=False):
        return f"[MODE:{user_role}]"


class _FakeRenderer:
    def __init__(self):
        self.mood = "idle"

    def get_mood(self):
        return self.mood

    def set_mood(self, mood, pace=0.7, blink=True):
        self.mood = mood


def _bare_ucli():
    ucli = UCLI.__new__(UCLI)
    ucli._io_phase = IOLifecyclePhase.BACKGROUND
    ucli._io_phase_lock = threading.RLock()
    ucli.quiet = False
    ucli.status_bar = _FakeStatusBar()
    ucli._theme_text = lambda s: s
    ucli.renderer = _FakeRenderer()
    return ucli


def test_io_phase_scope_restores_previous_phase():
    ucli = _bare_ucli()
    ucli._set_io_phase(IOLifecyclePhase.BACKGROUND)

    with ucli._io_phase_scope(IOLifecyclePhase.INPUT):
        assert ucli._get_io_phase() == IOLifecyclePhase.INPUT

    assert ucli._get_io_phase() == IOLifecyclePhase.BACKGROUND


def test_status_bar_renders_only_in_input_phase(monkeypatch):
    ucli = _bare_ucli()
    buffer = _TTYBuffer()
    monkeypatch.setattr("sys.stdout", buffer)
    monkeypatch.delenv("UDOS_TUI_FORCE_STATUS", raising=False)

    ucli._set_io_phase(IOLifecyclePhase.BACKGROUND)
    ucli._show_status_bar()
    assert buffer.getvalue() == ""

    ucli._set_io_phase(IOLifecyclePhase.INPUT)
    ucli._show_status_bar()
    assert "[MODE:" in buffer.getvalue()


def test_run_with_spinner_executes_work_in_background_phase(monkeypatch):
    ucli = _bare_ucli()
    phase_seen = {"value": None}

    class _FakeSpinner:
        def __init__(self, label, show_elapsed=True):
            self.interval = 0.001

        def start(self):
            return None

        def tick(self):
            return None

        def stop(self, success_text=None):
            return None

    monkeypatch.setattr("core.tui.ui_elements.Spinner", _FakeSpinner)
    ucli._set_io_phase(IOLifecyclePhase.RENDER)

    def _work():
        phase_seen["value"] = ucli._get_io_phase()
        time.sleep(0.01)
        return "ok"

    result = ucli._run_with_spinner("test", _work)
    assert result == "ok"
    assert phase_seen["value"] == IOLifecyclePhase.BACKGROUND
    assert ucli._get_io_phase() == IOLifecyclePhase.RENDER
