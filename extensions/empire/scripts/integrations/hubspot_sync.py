#!/usr/bin/env python3
"""Sync HubSpot contacts into Empire.

Manual operator wrapper only.
Wizard Empire connector routes and services are the canonical runtime surface.
"""

from __future__ import annotations

import argparse

from empire.integrations.hubspot import sync_contacts, sync_companies, sync_all, push_contacts, push_companies


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync HubSpot contacts")
    parser.epilog = (
        "Operator wrapper only. Prefer Wizard Empire connector actions for the supported runtime path."
    )
    parser.add_argument("--token", default=None, help="HubSpot private app token")
    parser.add_argument("--limit", type=int, default=100, help="Page size")
    parser.add_argument("--pages", type=int, default=5, help="Max pages")
    parser.add_argument("--mode", choices=["contacts", "companies", "all"], default="all")
    parser.add_argument("--push", action="store_true", help="Push local updates to HubSpot")
    parser.add_argument("--db", default=None, help="SQLite DB path")
    args = parser.parse_args()

    if args.mode == "contacts":
        count = sync_contacts(
            token=args.token,
            db_path=args.db,
            limit=args.limit,
            max_pages=args.pages,
        )
        print(f"HubSpot synced {count} contacts")
        if args.push:
            pushed = push_contacts(token=args.token, db_path=args.db, limit=args.limit)
            print(f"HubSpot pushed {pushed} contacts")
    elif args.mode == "companies":
        count = sync_companies(
            token=args.token,
            db_path=args.db,
            limit=args.limit,
            max_pages=args.pages,
        )
        print(f"HubSpot synced {count} companies")
        if args.push:
            pushed = push_companies(token=args.token, db_path=args.db, limit=args.limit)
            print(f"HubSpot pushed {pushed} companies")
    else:
        counts = sync_all(
            token=args.token,
            db_path=args.db,
            limit=args.limit,
            max_pages=args.pages,
        )
        print(f"HubSpot synced contacts={counts['contacts']} companies={counts['companies']}")
        if args.push:
            pushed_contacts = push_contacts(token=args.token, db_path=args.db, limit=args.limit)
            pushed_companies = push_companies(token=args.token, db_path=args.db, limit=args.limit)
            print(f"HubSpot pushed contacts={pushed_contacts} companies={pushed_companies}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
