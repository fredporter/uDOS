#!/usr/bin/env python3
"""
Grid Codec CLI

Decode/encode uDOS grid codes to lat/long for external integrations.
No lat/long is stored in core datasets or docs; this is computed on demand.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from core.services.grid_codec import (
    decode_to_latlon,
    decode_to_latlon_bounds,
    encode_from_latlon,
    parse_grid_code,
)


def _fmt_float(value: float) -> str:
    return f"{value:.6f}"


def _print_decode(code: str) -> int:
    coord = parse_grid_code(code)
    if not coord:
        print("Invalid grid code.")
        return 2
    bounds = decode_to_latlon_bounds(code)
    center = decode_to_latlon(code)
    if not bounds or not center:
        print("Failed to decode grid code.")
        return 2
    lat_min, lat_max, lon_min, lon_max = bounds
    lat_c, lon_c = center
    print(f"Code: {code}")
    print(f"Effective layer: L{str(coord.effective_layer).zfill(3)}")
    print(f"Center: lat {_fmt_float(lat_c)}, lon {_fmt_float(lon_c)}")
    print(
        "Bounds: "
        f"lat [{_fmt_float(lat_min)}, {_fmt_float(lat_max)}], "
        f"lon [{_fmt_float(lon_min)}, {_fmt_float(lon_max)}]"
    )
    return 0


def _print_encode(layer: int, lat: float, lon: float) -> int:
    code = encode_from_latlon(layer, lat, lon)
    print(f"L{str(layer).zfill(3)} @ ({_fmt_float(lat)}, {_fmt_float(lon)}) -> {code}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="uDOS Grid Codec")
    subparsers = parser.add_subparsers(dest="command", required=True)

    decode_parser = subparsers.add_parser("decode", help="Decode grid code to lat/long")
    decode_parser.add_argument("code", help="Grid code (L###-AA##[-AA##]...)")

    encode_parser = subparsers.add_parser("encode", help="Encode lat/long to grid code")
    encode_parser.add_argument("layer", type=int, help="Base layer number (e.g. 300)")
    encode_parser.add_argument("lat", type=float, help="Latitude (-90..90)")
    encode_parser.add_argument("lon", type=float, help="Longitude (-180..180)")

    args = parser.parse_args(argv)

    if args.command == "decode":
        return _print_decode(args.code)
    if args.command == "encode":
        return _print_encode(args.layer, args.lat, args.lon)

    return 2


if __name__ == "__main__":
    sys.exit(main())
