#!/usr/bin/env python3
"""Write Empire overview JSON for the UI.

Legacy support utility for the standalone web surface.
Wizard-owned Empire routes are the supported runtime path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from empire.services.overview_service import load_overview
from empire.services.storage import DEFAULT_DB_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh Empire UI overview JSON")
    parser.epilog = (
        "Legacy support utility only. The Wizard Empire UI should not depend on this script."
    )
    parser.add_argument("--db", default=None, help="SQLite DB path")
    parser.add_argument("--out", default=None, help="Output JSON path")
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else DEFAULT_DB_PATH
    out_path = Path(args.out) if args.out else Path(__file__).resolve().parents[2] / "web" / "public" / "overview.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    overview = load_overview(db_path=db_path)
    out_path.write_text(json.dumps(overview, indent=2), encoding="utf-8")
    print(f"Wrote overview -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
