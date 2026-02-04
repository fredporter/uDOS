"""
Grid Codec (Core)
=================

Decode uDOS grid codes (L###-AA##[-AA##]...) to lat/long bounds for external
integrations. No lat/long is stored in core datasets or docs; this is computed
on demand.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class GridCoordinate:
    base_layer: int
    cells: List[Tuple[int, int]]
    effective_layer: int


GRID_ROW_MIN = 10
GRID_ROW_MAX = 39


def _col_to_index(cell_col: str) -> Optional[int]:
    if len(cell_col) != 2 or not cell_col.isalpha():
        return None
    cell_col = cell_col.upper()
    if cell_col == "DC":
        return _max_col_index()
    a = ord(cell_col[0]) - ord("A")
    b = ord(cell_col[1]) - ord("A")
    if a < 0 or b < 0:
        return None
    index = a * 26 + b
    col_max = _max_col_index()
    if index > col_max:
        index = index % (col_max + 1)
    return index


def _index_to_col(index: int) -> str:
    if index == 79:
        return "DC"
    a = index // 26
    b = index % 26
    return f"{chr(ord('A') + a)}{chr(ord('A') + b)}"


def _max_col_index() -> int:
    # Schema range: AA..DC (0-79; DC is a special-case at 79)
    return 79


def parse_grid_code(code: str) -> Optional[GridCoordinate]:
    try:
        if not code.startswith("L"):
            return None
        parts = code.split("-")
        if len(parts) < 2:
            return None
        layer_part = parts[0]
        layer = int(layer_part[1:])
        cells: List[Tuple[int, int]] = []
        for cell_part in parts[1:]:
            if len(cell_part) != 4:
                return None
            cell_col = cell_part[:2]
            cell_row = int(cell_part[2:])
            col_index = _col_to_index(cell_col)
            if col_index is None:
                return None
            if cell_row < GRID_ROW_MIN or cell_row > GRID_ROW_MAX:
                return None
            cells.append((col_index, cell_row))
        if not cells:
            return None
        return GridCoordinate(
            base_layer=layer,
            cells=cells,
            effective_layer=layer + len(cells) - 1,
        )
    except Exception:
        return None


def decode_to_latlon_bounds(
    code: str,
) -> Optional[Tuple[float, float, float, float]]:
    """
    Decode grid code to lat/long bounds.

    Mapping uses recursive 80x30 subdivision across the canonical grid:
    rows 10..39 -> 30 rows from +90 down to -90
    cols AA..DC -> 80 cols from -180 to +180
    """
    coord = parse_grid_code(code)
    if not coord:
        return None
    lat_min = -90.0
    lat_max = 90.0
    lon_min = -180.0
    lon_max = 180.0
    col_max = _max_col_index()
    for col_index, row_value in coord.cells:
        row_index = row_value - GRID_ROW_MIN  # 0..29
        lat_span = lat_max - lat_min
        lon_span = lon_max - lon_min
        lat_step = lat_span / (GRID_ROW_MAX - GRID_ROW_MIN + 1)
        lon_step = lon_span / (col_max + 1)
        # Rows increase downward; row 0 is north.
        cell_lat_max = lat_max - (row_index * lat_step)
        cell_lat_min = cell_lat_max - lat_step
        cell_lon_min = lon_min + (col_index * lon_step)
        cell_lon_max = cell_lon_min + lon_step
        lat_min, lat_max = cell_lat_min, cell_lat_max
        lon_min, lon_max = cell_lon_min, cell_lon_max
    return (lat_min, lat_max, lon_min, lon_max)


def decode_to_latlon(code: str) -> Optional[Tuple[float, float]]:
    """
    Decode grid code to a center lat/long.
    """
    bounds = decode_to_latlon_bounds(code)
    if not bounds:
        return None
    lat_min, lat_max, lon_min, lon_max = bounds
    return ((lat_min + lat_max) / 2.0, (lon_min + lon_max) / 2.0)


def encode_from_latlon(layer: int, lat: float, lon: float) -> str:
    """
    Encode a lat/long into the nearest grid code on a given layer.
    """
    row_min = GRID_ROW_MIN
    row_max = GRID_ROW_MAX
    col_max = _max_col_index()
    lat = max(-90.0, min(90.0, lat))
    lon = max(-180.0, min(180.0, lon))
    row = round(((lat + 90.0) / 180.0) * (row_max - row_min) + row_min)
    col = round(((lon + 180.0) / 360.0) * col_max)
    cell = f"{_index_to_col(col)}{str(row).zfill(2)}"
    return f"L{str(layer).zfill(3)}-{cell}"
