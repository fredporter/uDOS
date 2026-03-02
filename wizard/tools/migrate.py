from __future__ import annotations

from pathlib import Path

from wizard.services.store.postgres_store import psycopg


def main() -> int:
    if psycopg is None:
        raise RuntimeError("psycopg is required to run managed Wizard migrations")
    from wizard.services.deploy_mode import require_managed_env

    dsn = require_managed_env("SUPABASE_DB_DSN")
    migration_dir = Path(__file__).resolve().parent.parent / "migrations"
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        cur.execute("SELECT version FROM schema_migrations")
        applied = {row[0] for row in cur.fetchall()}
        for path in sorted(migration_dir.glob("*.sql")):
            if path.name in applied:
                continue
            cur.execute(path.read_text(encoding="utf-8"))
            cur.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (path.name,))
            print(f"applied {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
