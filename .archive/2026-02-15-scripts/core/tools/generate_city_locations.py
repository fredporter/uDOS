#!/usr/bin/env python3
"""
Generate City Locations from IANA Timezones

Creates comprehensive locations seed file with all IANA timezone cities,
using fractal depth (L300-L305) to ensure NO COLLISIONS.

Author: uDOS Engineering
Date: 2026-02-09
"""

import json
import zoneinfo
import hashlib
from pathlib import Path
from typing import Dict, Any, List


def parse_timezone_parts(timezone: str) -> Dict[str, str]:
    """Parse IANA timezone into components."""
    parts = timezone.split('/')
    if len(parts) == 2:
        region, city_raw = parts
        return {"region": region, "country": region, "city": city_raw.replace('_', ' ')}
    elif len(parts) == 3:
        region, country, city_raw = parts
        return {"region": region, "country": country, "city": city_raw.replace('_', ' ')}
    else:
        return {"region": "Unknown", "country": "Unknown", "city": timezone}


def generate_city_locations() -> List[Dict[str, Any]]:
    """
    Generate locations for 518 IANA timezone cities with spec-compliant fractal grid.

    Spec: L300-L305 terrestrial with fractal zoom
    - Layer 300: 80×30 grid = 2,400 cells
    - Colliding cities: assign to L301 (depth 1) with modified hash
    - Result: ZERO collisions
    """
    all_zones = sorted(zoneinfo.available_timezones())
    city_zones = [z for z in all_zones if '/' in z and not z.startswith(('Etc/', 'SystemV/'))]

    print(f"Generating {len(city_zones)} city locations...")

    # First pass: detect L300 collisions
    l300_map = {}
    collisions = set()

    for tz in city_zones:
        h = int(hashlib.sha256(tz.encode()).hexdigest(), 16)
        col_idx, row_idx = h % 80, (h // 80) % 30
        cell = f"{chr(65 + col_idx//26)}{chr(65 + col_idx%26)}{10+row_idx:02d}"
        code = f"L300-{cell}"

        if code in l300_map:
            collisions.add(tz)
            collisions.add(l300_map[code])
        else:
            l300_map[code] = tz

    print(f"  Detected {len(collisions)} collision cities")

    # Second pass: assign locations with collision resolution
    locations = []
    l301_used = set()  # Track L301 assignments to avoid new collisions

    for tz in city_zones:
        parts = parse_timezone_parts(tz)
        h = int(hashlib.sha256(tz.encode()).hexdigest(), 16)

        if tz not in collisions:
            # No collision: L300
            col_idx, row_idx = h % 80, (h // 80) % 30
            cell = f"{chr(65 + col_idx//26)}{chr(65 + col_idx%26)}{10+row_idx:02d}"
            grid_code = f"L300-{cell}"
            final_cell = cell
            depth = 0
        else:
            # Collision: L301 with XOR hash (keep trying until unique)
            attempt = 0
            while True:
                xor_val = 0xDEADBEEF + attempt
                h2 = h ^ xor_val
                h3, h4 = h2 % 80, (h2 // 80) % 30
                h5 = h % 80
                h6 = (h // 80) % 30

                p_cell = f"{chr(65 + h5//26)}{chr(65 + h5%26)}{10+h6:02d}"
                c_cell = f"{chr(65 + h3//26)}{chr(65 + h3%26)}{10+h4:02d}"
                code = f"L300-{p_cell}-{c_cell}"

                if code not in l301_used:
                    l301_used.add(code)
                    grid_code = code
                    final_cell = c_cell
                    depth = 1
                    break
                attempt += 1
                if attempt > 100:
                    print(f"  Warning: {tz} couldn't find unique L301 cell")
                    break

        locations.append({
            "id": grid_code,
            "name": parts["city"],
            "region": parts["country"],
            "description": f"{parts['city']}, {parts['country']}",
            "layer": 300,
            "cell": final_cell,
            "scale": "terrestrial",
            "continent": parts["region"],
            "timezone": tz,
            "type": "city",
            "region_type": "urban",
            "depth": depth,
            "effective_layer": 300 + depth,
            "connections": [],
            "tiles": {}
        })

    return locations


def save_locations(locations: List[Dict[str, Any]], path: Path):
    """Save locations to JSON file."""
    data = {
        "version": "1.0.7.0",
        "description": "IANA Timezone Cities - Spec L300-L305 Fractal",
        "generated": "2026-02-09",
        "grid": {"cols": 80, "rows": 30},
        "locations": locations
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved {len(locations)} locations to {path}")


if __name__ == "__main__":
    locations = generate_city_locations()

    paths = [
        Path(__file__).parent.parent / "framework" / "seed" / "locations-seed.json",
        Path(__file__).parent.parent.parent / "memory" / "locations" / "locations.json"
    ]

    for p in paths:
        save_locations(locations, p)

    # Summary
    depth_dist = {}
    for loc in locations:
        d = loc.get('depth', 0)
        depth_dist[d] = depth_dist.get(d, 0) + 1

    print(f"\n📊 Summary:")
    print(f"   Total cities: {len(locations)}")
    for d in sorted(depth_dist.keys()):
        eff = 300 + d
        print(f"   Depth {d} (L{eff}): {depth_dist[d]:3d} cities")

    # Find Brisbane
    for loc in locations:
        if loc['name'] == 'Brisbane':
            print(f"   Sample: Brisbane ({loc['id']}) - {loc['timezone']}")
            break
