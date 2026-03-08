#!/usr/bin/env python3
"""CLI wrapper for Empire email processing.

Legacy operator utility.
This script is not part of the supported Wizard runtime contract.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from empire.services.email_process import process_emails
from empire.services.storage import DEFAULT_DB_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description="Process emails into tasks + records")
    parser.epilog = (
        "Legacy operator utility only. Do not treat this as a canonical Empire runtime entrypoint."
    )
    parser.add_argument("--in", dest="input_path", required=True, help="Input JSON file")
    parser.add_argument("--db", default=None, help="SQLite DB path")
    parser.add_argument("--out", default=None, help="Output JSON file")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    emails = json.loads(input_path.read_text(encoding="utf-8"))

    db_path = Path(args.db) if args.db else DEFAULT_DB_PATH
    result = process_emails(emails, db_path=db_path)

    out_path = Path(args.out) if args.out else Path(__file__).resolve().parents[2] / "data" / "processed" / "email_tasks.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "tasks": [task.__dict__ for task in result["tasks"]],
                "records": [record.__dict__ for record in result["records"]],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Processed {len(result['tasks'])} emails -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
