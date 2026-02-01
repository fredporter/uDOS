"""
Teletext/NES canvas API for Round 5 plumbing.
"""

from typing import Dict, List

from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/teletext", tags=["teletext"])


@router.get("/canvas")
async def teletext_canvas(request: Request):
    grid = ["+" + "═" * 78 + "+"] + [
        "|" + "".join("░" if (row + col) % 2 == 0 else " " for col in range(78)) + "|"
        for row in range(28)
    ] + ["+" + "═" * 78 + "+"]
    return {
        "layout": "teletext",
        "width": 80,
        "height": 30,
        "canvas": grid,
        "layers": [
            {"name": "header", "text": "Round 5 Teletext Preview"},
            {"name": "grid", "pattern": "checker"},
        ],
    }


@router.get("/nes-buttons")
async def nes_buttons(request: Request):
    buttons = [
        {"id": "btn_a", "label": "A", "color": "#ff3b30"},
        {"id": "btn_b", "label": "B", "color": "#0a84ff"},
        {"id": "btn_start", "label": "START", "color": "#34c759"},
        {"id": "btn_select", "label": "SELECT", "color": "#ff9500"},
    ]
    layout = [
        {"name": "dpad", "positions": ["up", "left", "right", "down"]},
        {"name": "buttons", "positions": ["A", "B", "START", "SELECT"]},
    ]
    return {
        "controller": "nes",
        "buttons": buttons,
        "layout": layout,
        "note": "Use these definitions to build Canvas-based overlays."
    }
