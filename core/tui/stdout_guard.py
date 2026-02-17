"""Single-writer stdout guard for interactive TUI flows."""

from __future__ import annotations

from contextlib import contextmanager
from threading import RLock
from typing import Iterable, Iterator, TextIO
import builtins
import sys

_STDOUT_LOCK = RLock()


class LockedStdout:
    """Proxy that serializes stdout writes behind a shared re-entrant lock."""

    def __init__(self, wrapped: TextIO):
        self._wrapped = wrapped

    def write(self, data: str) -> int:
        with _STDOUT_LOCK:
            return self._wrapped.write(data)

    def writelines(self, lines: Iterable[str]) -> None:
        with _STDOUT_LOCK:
            self._wrapped.writelines(lines)

    def flush(self) -> None:
        with _STDOUT_LOCK:
            self._wrapped.flush()

    def __getattr__(self, name: str):
        return getattr(self._wrapped, name)


def install_stdout_guard() -> LockedStdout:
    """Install a process-wide locked stdout wrapper once."""
    current = sys.stdout
    if isinstance(current, LockedStdout):
        return current
    wrapped = LockedStdout(current)
    sys.stdout = wrapped
    return wrapped


@contextmanager
def stdout_write_lock() -> Iterator[None]:
    """Acquire the shared stdout write lock."""
    with _STDOUT_LOCK:
        yield


def atomic_stdout_write(text: str, *, flush: bool = True) -> None:
    """Write text atomically to stdout."""
    with _STDOUT_LOCK:
        sys.stdout.write(text)
        if flush:
            sys.stdout.flush()


def atomic_print(*args, sep: str = " ", end: str = "\n", flush: bool = True) -> None:
    """Print atomically to stdout."""
    with _STDOUT_LOCK:
        builtins.print(*args, sep=sep, end=end, flush=False)
        if flush:
            sys.stdout.flush()
