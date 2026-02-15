"""Shared OK execution/fallback helpers for uCODE routes."""

from __future__ import annotations

from typing import Callable, Iterable, Optional, Tuple

from fastapi import HTTPException


def _require_cloud_available(cloud_available: Callable[[], bool]) -> None:
    if not cloud_available():
        raise HTTPException(status_code=400, detail="Mistral API key required for cloud OK")


def run_ok_with_fallback(
    *,
    prompt: str,
    model: str,
    use_cloud: bool,
    auto_fallback: bool,
    run_local: Callable[[str, Optional[str]], str],
    run_cloud: Callable[[str], Tuple[str, str]],
    cloud_available: Callable[[], bool],
    local_failure_detail: str,
) -> Tuple[str, str, str]:
    source = "local"
    response_text: Optional[str] = None
    current_model = model

    if use_cloud:
        _require_cloud_available(cloud_available)
        try:
            response_text, current_model = run_cloud(prompt)
            source = "cloud"
        except Exception:
            response_text = None

    if response_text is None:
        try:
            response_text = run_local(prompt, current_model)
        except Exception:
            response_text = None
            if auto_fallback and not use_cloud:
                _require_cloud_available(cloud_available)
                response_text, current_model = run_cloud(prompt)
                source = "cloud"
            else:
                raise HTTPException(status_code=500, detail=local_failure_detail)

    return response_text, current_model, source


def run_ok_stream_with_fallback(
    *,
    prompt: str,
    model: str,
    use_cloud: bool,
    auto_fallback: bool,
    run_local_stream: Callable[[str, str], Iterable[str]],
    run_cloud: Callable[[str], Tuple[str, str]],
    cloud_available: Callable[[], bool],
    emit_chunk: Callable[[str], None],
) -> Tuple[str, str, str]:
    source = "local"
    response_text = ""
    current_model = model

    if use_cloud:
        try:
            _require_cloud_available(cloud_available)
            response_text, current_model = run_cloud(prompt)
            source = "cloud"
            if response_text:
                emit_chunk(response_text)
        except Exception:
            response_text = ""

    if not response_text:
        try:
            buffer = ""
            for part in run_local_stream(prompt, current_model):
                buffer += part
                emit_chunk(part)
            response_text = buffer
        except Exception:
            response_text = ""

    if not response_text and auto_fallback:
        _require_cloud_available(cloud_available)
        response_text, current_model = run_cloud(prompt)
        source = "cloud"
        if response_text:
            emit_chunk(response_text)

    return response_text, current_model, source
