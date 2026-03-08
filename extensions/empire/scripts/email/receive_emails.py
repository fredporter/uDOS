#!/usr/bin/env python3
"""CLI wrapper for Empire email receive.

Legacy operator utility.
This script is not part of the supported Wizard runtime contract.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from empire.services.email_receive import receive_emails


def main() -> int:
    parser = argparse.ArgumentParser(description="Receive emails via IMAP")
    parser.epilog = (
        "Legacy operator utility only. Do not treat this as a canonical Empire runtime entrypoint."
    )
    parser.add_argument("--host", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--mailbox", default="INBOX")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--out", default=None, help="Output JSON file")
    args = parser.parse_args()

    emails = receive_emails(
        host=args.host,
        username=args.user,
        password=args.password,
        mailbox=args.mailbox,
        limit=args.limit,
    )

    out_path = Path(args.out) if args.out else Path(__file__).resolve().parents[2] / "data" / "raw" / "emails.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(emails, indent=2), encoding="utf-8")
    print(f"Saved {len(emails)} emails -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
