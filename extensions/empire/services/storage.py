"""SQLite storage for Empire business records."""

from __future__ import annotations

import sqlite3
import json
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Optional, List

from empire.services.normalization_service import NormalizedRecord
from empire.services.dedupe_service import dedupe_key, name_org_match


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "empire.db"


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, column_def: str) -> None:
    cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_def}")


def _normalize_domain(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    trimmed = value.strip().lower()
    if "@" in trimmed:
        return trimmed.split("@")[-1]
    for prefix in ("http://", "https://"):
        if trimmed.startswith(prefix):
            trimmed = trimmed[len(prefix):]
    return trimmed.split("/")[0] if trimmed else None


def _link_record_company(
    conn: sqlite3.Connection,
    record_id: str,
    organization: Optional[str],
    email: Optional[str],
) -> None:
    if not record_id:
        return
    org = organization.strip() if organization else None
    domain = _normalize_domain(email)
    row = None
    if org:
        row = conn.execute(
            "SELECT company_id FROM companies WHERE lower(name) = lower(?) LIMIT 1",
            (org,),
        ).fetchone()
    if not row and domain:
        row = conn.execute(
            "SELECT company_id FROM companies WHERE lower(domain) = lower(?) LIMIT 1",
            (domain,),
        ).fetchone()
    if row:
        conn.execute(
            "INSERT OR IGNORE INTO contact_companies (record_id, company_id, created_at) VALUES (?, ?, datetime('now'))",
            (record_id, row[0]),
        )

def ensure_schema(db_path: Path = DEFAULT_DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                label TEXT,
                created_at TEXT,
                metadata TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                record_id TEXT PRIMARY KEY,
                hs_object_id TEXT,
                source TEXT,
                createdate TEXT,
                lastmodifieddate TEXT,
                email TEXT,
                firstname TEXT,
                lastname TEXT,
                phone TEXT,
                mobilephone TEXT,
                fax TEXT,
                jobtitle TEXT,
                company TEXT,
                website TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip TEXT,
                country TEXT,
                lifecyclestage TEXT,
                dedupe_key TEXT,
                raw_json TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_records_email ON records(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_records_company ON records(company)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_records_dedupe ON records(dedupe_key)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                record_id TEXT,
                event_type TEXT,
                occurred_at TEXT,
                subject TEXT,
                notes TEXT,
                metadata TEXT,
                FOREIGN KEY(record_id) REFERENCES records(record_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT,
                category TEXT,
                source TEXT,
                source_ref TEXT,
                created_at TEXT,
                status TEXT,
                notes TEXT,
                record_id TEXT,
                FOREIGN KEY(record_id) REFERENCES records(record_id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_source ON tasks(source)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_record_id ON tasks(record_id)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                company_id TEXT PRIMARY KEY,
                hs_object_id TEXT,
                name TEXT,
                domain TEXT,
                website TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip TEXT,
                country TEXT,
                industry TEXT,
                annual_revenue TEXT,
                num_employees TEXT,
                owner_id TEXT,
                createdate TEXT,
                lastmodifieddate TEXT,
                raw_json TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(domain)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contact_companies (
                record_id TEXT,
                company_id TEXT,
                created_at TEXT,
                PRIMARY KEY (record_id, company_id),
                FOREIGN KEY(record_id) REFERENCES records(record_id),
                FOREIGN KEY(company_id) REFERENCES companies(company_id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_contact_companies_record ON contact_companies(record_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_contact_companies_company ON contact_companies(company_id)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                source TEXT,
                scope TEXT,
                binder_id TEXT,
                source_path TEXT,
                title TEXT,
                media_type TEXT,
                extracted_text TEXT,
                metadata TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_scope ON documents(scope)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_binder_id ON documents(binder_id)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS import_jobs (
                job_id TEXT PRIMARY KEY,
                scope TEXT,
                binder_id TEXT,
                source_kind TEXT,
                source_path TEXT,
                status TEXT,
                records_imported INTEGER DEFAULT 0,
                documents_created INTEGER DEFAULT 0,
                started_at TEXT,
                completed_at TEXT,
                error TEXT,
                metadata TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_import_jobs_status ON import_jobs(status)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_jobs (
                sync_job_id TEXT PRIMARY KEY,
                scope TEXT,
                binder_id TEXT,
                connector TEXT,
                action TEXT,
                status TEXT,
                records_imported INTEGER DEFAULT 0,
                documents_created INTEGER DEFAULT 0,
                started_at TEXT,
                completed_at TEXT,
                error TEXT,
                metadata TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sync_jobs_connector ON sync_jobs(connector)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON sync_jobs(status)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_mappings (
                mapping_id TEXT PRIMARY KEY,
                name TEXT,
                source_system TEXT,
                event_type TEXT,
                target_scope TEXT,
                binder_id TEXT,
                target_entity TEXT,
                template_path TEXT,
                endpoint_secret TEXT,
                status TEXT,
                config_json TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_webhook_mappings_source ON webhook_mappings(source_system)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_webhook_mappings_status ON webhook_mappings(status)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_deliveries (
                delivery_id TEXT PRIMARY KEY,
                mapping_id TEXT,
                direction TEXT,
                event_type TEXT,
                status TEXT,
                request_payload TEXT,
                response_payload TEXT,
                error TEXT,
                created_at TEXT,
                FOREIGN KEY(mapping_id) REFERENCES webhook_mappings(mapping_id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_mapping ON webhook_deliveries(mapping_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_status ON webhook_deliveries(status)")
        _ensure_column(conn, "tasks", "source_ref", "TEXT")
        _ensure_column(conn, "tasks", "record_id", "TEXT")


def upsert_record(
    record: NormalizedRecord,
    *,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    ensure_schema(db_path)
    payload = asdict(record)
    record_key = dedupe_key(record)
    with sqlite3.connect(str(db_path)) as conn:
        existing_id = _find_duplicate_record_id(conn, record)
        record_id = existing_id or record.record_id
        conn.execute(
            """
            INSERT INTO records (
                record_id, hs_object_id, source, createdate, lastmodifieddate, email, firstname, lastname,
                phone, mobilephone, fax, jobtitle, company, website, address, city, state, zip, country,
                lifecyclestage, dedupe_key, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(record_id) DO UPDATE SET
                hs_object_id=excluded.hs_object_id,
                source=excluded.source,
                lastmodifieddate=excluded.lastmodifieddate,
                email=excluded.email,
                firstname=excluded.firstname,
                lastname=excluded.lastname,
                phone=excluded.phone,
                mobilephone=excluded.mobilephone,
                fax=excluded.fax,
                jobtitle=excluded.jobtitle,
                company=excluded.company,
                website=excluded.website,
                address=excluded.address,
                city=excluded.city,
                state=excluded.state,
                zip=excluded.zip,
                country=excluded.country,
                lifecyclestage=excluded.lifecyclestage,
                dedupe_key=excluded.dedupe_key,
                raw_json=excluded.raw_json
            """,
            (
                record_id,
                None,
                record.source,
                record.normalized_at,
                record.normalized_at,
                record.email,
                record.name.split(" ", 1)[0] if record.name else None,
                record.name.split(" ", 1)[1] if record.name and " " in record.name else None,
                record.phone,
                None,
                None,
                record.role,
                record.organization,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                record_key,
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        _link_record_company(conn, record_id, record.organization, record.email)
    return record_id


def _find_duplicate_record_id(conn: sqlite3.Connection, record: NormalizedRecord) -> Optional[str]:
    if record.email:
        row = conn.execute(
            "SELECT record_id FROM records WHERE email = ? LIMIT 1",
            (record.email,),
        ).fetchone()
        if row:
            return row[0]

    if record.name:
        if record.organization:
            candidates = conn.execute(
                "SELECT record_id, firstname, lastname, company FROM records WHERE company = ?",
                (record.organization,),
            ).fetchall()
        else:
            candidates = conn.execute(
                "SELECT record_id, firstname, lastname, company FROM records WHERE lastname = ?",
                (record.name.split(' ', 1)[-1],),
            ).fetchall()
        for record_id, firstname, lastname, company in candidates:
            existing_name = " ".join(filter(None, [firstname, lastname]))
            if name_org_match(record.name, record.organization, existing_name, company):
                return record_id

    return None


def record_source(
    source_id: str,
    *,
    label: Optional[str] = None,
    created_at: Optional[str] = None,
    metadata: Optional[str] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO sources (id, label, created_at, metadata)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                label=excluded.label,
                metadata=excluded.metadata
            """,
            (source_id, label, created_at, metadata),
        )


def record_event(
    *,
    record_id: Optional[str],
    event_type: str,
    occurred_at: str,
    subject: Optional[str] = None,
    notes: Optional[str] = None,
    metadata: Optional[str] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    ensure_schema(db_path)
    event_id = uuid.uuid4().hex
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO events (event_id, record_id, event_type, occurred_at, subject, notes, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (event_id, record_id, event_type, occurred_at, subject, notes, metadata),
        )
    return event_id


def record_task(
    *,
    title: str,
    category: str,
    source: str,
    created_at: str,
    status: str = "open",
    notes: Optional[str] = None,
    source_ref: Optional[str] = None,
    record_id: Optional[str] = None,
    dedupe_by_source: bool = False,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        if dedupe_by_source and source:
            existing = conn.execute(
                "SELECT task_id FROM tasks WHERE source = ? LIMIT 1",
                (source,),
            ).fetchone()
            if existing:
                return existing[0]
        task_id = uuid.uuid4().hex
        conn.execute(
            """
            INSERT INTO tasks (task_id, title, category, source, source_ref, created_at, status, notes, record_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (task_id, title, category, source, source_ref, created_at, status, notes, record_id),
        )
    return task_id


def task_exists_by_source(source: str, *, db_path: Path = DEFAULT_DB_PATH) -> bool:
    if not source:
        return False
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        row = conn.execute(
            "SELECT 1 FROM tasks WHERE source = ? LIMIT 1",
            (source,),
        ).fetchone()
    return row is not None


def upsert_company(
    *,
    company_id: str,
    hs_object_id: Optional[str],
    name: Optional[str],
    domain: Optional[str],
    website: Optional[str],
    phone: Optional[str],
    address: Optional[str],
    city: Optional[str],
    state: Optional[str],
    zip_code: Optional[str],
    country: Optional[str],
    industry: Optional[str],
    annual_revenue: Optional[str],
    num_employees: Optional[str],
    owner_id: Optional[str],
    createdate: Optional[str],
    lastmodifieddate: Optional[str],
    raw_json: Optional[str],
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO companies (
                company_id, hs_object_id, name, domain, website, phone, address, city, state, zip,
                country, industry, annual_revenue, num_employees, owner_id, createdate, lastmodifieddate, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(company_id) DO UPDATE SET
                hs_object_id=excluded.hs_object_id,
                name=excluded.name,
                domain=excluded.domain,
                website=excluded.website,
                phone=excluded.phone,
                address=excluded.address,
                city=excluded.city,
                state=excluded.state,
                zip=excluded.zip,
                country=excluded.country,
                industry=excluded.industry,
                annual_revenue=excluded.annual_revenue,
                num_employees=excluded.num_employees,
                owner_id=excluded.owner_id,
                lastmodifieddate=excluded.lastmodifieddate,
                raw_json=excluded.raw_json
            """,
            (
                company_id,
                hs_object_id,
                name,
                domain,
                website,
                phone,
                address,
                city,
                state,
                zip_code,
                country,
                industry,
                annual_revenue,
                num_employees,
                owner_id,
                createdate,
                lastmodifieddate,
                raw_json,
            ),
        )
        _link_company_contacts(conn, company_id, name, domain)


def _link_company_contacts(
    conn: sqlite3.Connection,
    company_id: str,
    name: Optional[str],
    domain: Optional[str],
) -> None:
    if not company_id:
        return
    org = name.strip() if name else None
    dom = _normalize_domain(domain)
    if org:
        rows = conn.execute(
            "SELECT record_id FROM records WHERE lower(company) = lower(?)",
            (org,),
        ).fetchall()
        for row in rows:
            conn.execute(
                "INSERT OR IGNORE INTO contact_companies (record_id, company_id, created_at) VALUES (?, ?, datetime('now'))",
                (row[0], company_id),
            )
    if dom:
        rows = conn.execute(
            "SELECT record_id FROM records WHERE email LIKE ?",
            (f"%@{dom}",),
        ).fetchall()
        for row in rows:
            conn.execute(
                "INSERT OR IGNORE INTO contact_companies (record_id, company_id, created_at) VALUES (?, ?, datetime('now'))",
                (row[0], company_id),
            )


def list_records(db_path: Path = DEFAULT_DB_PATH, limit: int = 500) -> List[Dict[str, str]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT record_id, hs_object_id, email, firstname, lastname, phone, mobilephone, fax,
                   jobtitle, company, website, address, city, state, zip, country, lifecyclestage
            FROM records
            ORDER BY lastmodifieddate DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_companies(db_path: Path = DEFAULT_DB_PATH, limit: int = 500) -> List[Dict[str, str]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT company_id, hs_object_id, name, domain, website, phone, address, city, state, zip,
                   country, industry, annual_revenue, num_employees
            FROM companies
            ORDER BY lastmodifieddate DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def record_document(
    *,
    source: str,
    scope: str,
    binder_id: Optional[str],
    source_path: str,
    title: Optional[str],
    media_type: str,
    extracted_text: Optional[str],
    metadata: Optional[Dict[str, object]] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    ensure_schema(db_path)
    document_id = uuid.uuid4().hex
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO documents (
                document_id, source, scope, binder_id, source_path, title, media_type,
                extracted_text, metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (
                document_id,
                source,
                scope,
                binder_id,
                source_path,
                title,
                media_type,
                extracted_text,
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )
    return document_id


def create_import_job(
    *,
    scope: str,
    binder_id: Optional[str],
    source_kind: str,
    source_path: str,
    metadata: Optional[Dict[str, object]] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    ensure_schema(db_path)
    job_id = uuid.uuid4().hex
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO import_jobs (
                job_id, scope, binder_id, source_kind, source_path, status,
                started_at, metadata
            ) VALUES (?, ?, ?, ?, ?, 'running', datetime('now'), ?)
            """,
            (
                job_id,
                scope,
                binder_id,
                source_kind,
                source_path,
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )
    return job_id


def complete_import_job(
    *,
    job_id: str,
    status: str,
    records_imported: int = 0,
    documents_created: int = 0,
    error: Optional[str] = None,
    metadata: Optional[Dict[str, object]] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            UPDATE import_jobs
            SET status = ?, records_imported = ?, documents_created = ?,
                completed_at = datetime('now'), error = ?, metadata = ?
            WHERE job_id = ?
            """,
            (
                status,
                records_imported,
                documents_created,
                error,
                json.dumps(metadata or {}, ensure_ascii=False),
                job_id,
            ),
        )


def create_sync_job(
    *,
    scope: str,
    binder_id: Optional[str],
    connector: str,
    action: str,
    metadata: Optional[Dict[str, object]] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    ensure_schema(db_path)
    sync_job_id = uuid.uuid4().hex
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO sync_jobs (
                sync_job_id, scope, binder_id, connector, action, status, started_at, metadata
            ) VALUES (?, ?, ?, ?, ?, 'running', datetime('now'), ?)
            """,
            (
                sync_job_id,
                scope,
                binder_id,
                connector,
                action,
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )
    return sync_job_id


def complete_sync_job(
    *,
    sync_job_id: str,
    status: str,
    records_imported: int = 0,
    documents_created: int = 0,
    error: Optional[str] = None,
    metadata: Optional[Dict[str, object]] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            UPDATE sync_jobs
            SET status = ?, records_imported = ?, documents_created = ?,
                completed_at = datetime('now'), error = ?, metadata = ?
            WHERE sync_job_id = ?
            """,
            (
                status,
                records_imported,
                documents_created,
                error,
                json.dumps(metadata or {}, ensure_ascii=False),
                sync_job_id,
            ),
        )


def list_documents(db_path: Path = DEFAULT_DB_PATH, limit: int = 100) -> List[Dict[str, object]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT document_id, source, scope, binder_id, source_path, title, media_type,
                   created_at, updated_at
            FROM documents
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_import_jobs(db_path: Path = DEFAULT_DB_PATH, limit: int = 100) -> List[Dict[str, object]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT job_id, scope, binder_id, source_kind, source_path, status,
                   records_imported, documents_created, started_at, completed_at, error, metadata
            FROM import_jobs
            ORDER BY started_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_sync_jobs(
    db_path: Path = DEFAULT_DB_PATH,
    limit: int = 100,
    connector: Optional[str] = None,
) -> List[Dict[str, object]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        if connector:
            rows = conn.execute(
                """
                SELECT sync_job_id, scope, binder_id, connector, action, status,
                       records_imported, documents_created, started_at, completed_at, error, metadata
                FROM sync_jobs
                WHERE connector = ?
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (connector, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT sync_job_id, scope, binder_id, connector, action, status,
                       records_imported, documents_created, started_at, completed_at, error, metadata
                FROM sync_jobs
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    return [dict(row) for row in rows]


def get_document(document_id: str, db_path: Path = DEFAULT_DB_PATH) -> Optional[Dict[str, object]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT document_id, source, scope, binder_id, source_path, title, media_type,
                   extracted_text, metadata, created_at, updated_at
            FROM documents
            WHERE document_id = ?
            LIMIT 1
            """,
            (document_id,),
        ).fetchone()
    return dict(row) if row else None


def get_import_job(job_id: str, db_path: Path = DEFAULT_DB_PATH) -> Optional[Dict[str, object]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT job_id, scope, binder_id, source_kind, source_path, status,
                   records_imported, documents_created, started_at, completed_at, error, metadata
            FROM import_jobs
            WHERE job_id = ?
            LIMIT 1
            """,
            (job_id,),
        ).fetchone()
    return dict(row) if row else None


def get_sync_job(sync_job_id: str, db_path: Path = DEFAULT_DB_PATH) -> Optional[Dict[str, object]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT sync_job_id, scope, binder_id, connector, action, status,
                   records_imported, documents_created, started_at, completed_at, error, metadata
            FROM sync_jobs
            WHERE sync_job_id = ?
            LIMIT 1
            """,
            (sync_job_id,),
        ).fetchone()
    return dict(row) if row else None


def upsert_webhook_mapping(
    *,
    mapping_id: Optional[str] = None,
    name: str,
    source_system: str,
    event_type: str,
    target_scope: str,
    binder_id: Optional[str],
    target_entity: str,
    template_path: Optional[str],
    endpoint_secret: Optional[str],
    status: str,
    config_json: Optional[Dict[str, object]] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    ensure_schema(db_path)
    resolved_mapping_id = mapping_id or uuid.uuid4().hex
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO webhook_mappings (
                mapping_id, name, source_system, event_type, target_scope, binder_id,
                target_entity, template_path, endpoint_secret, status, config_json,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            ON CONFLICT(mapping_id) DO UPDATE SET
                name=excluded.name,
                source_system=excluded.source_system,
                event_type=excluded.event_type,
                target_scope=excluded.target_scope,
                binder_id=excluded.binder_id,
                target_entity=excluded.target_entity,
                template_path=excluded.template_path,
                endpoint_secret=excluded.endpoint_secret,
                status=excluded.status,
                config_json=excluded.config_json,
                updated_at=datetime('now')
            """,
            (
                resolved_mapping_id,
                name,
                source_system,
                event_type,
                target_scope,
                binder_id,
                target_entity,
                template_path,
                endpoint_secret,
                status,
                json.dumps(config_json or {}, ensure_ascii=False),
            ),
        )
    return resolved_mapping_id


def list_webhook_mappings(db_path: Path = DEFAULT_DB_PATH, limit: int = 100) -> List[Dict[str, object]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT mapping_id, name, source_system, event_type, target_scope, binder_id,
                   target_entity, template_path, endpoint_secret, status, config_json,
                   created_at, updated_at
            FROM webhook_mappings
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_webhook_mapping(mapping_id: str, db_path: Path = DEFAULT_DB_PATH) -> Optional[Dict[str, object]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT mapping_id, name, source_system, event_type, target_scope, binder_id,
                   target_entity, template_path, endpoint_secret, status, config_json,
                   created_at, updated_at
            FROM webhook_mappings
            WHERE mapping_id = ?
            LIMIT 1
            """,
            (mapping_id,),
        ).fetchone()
    return dict(row) if row else None


def record_webhook_delivery(
    *,
    mapping_id: str,
    direction: str,
    event_type: str,
    status: str,
    request_payload: Optional[Dict[str, object]] = None,
    response_payload: Optional[Dict[str, object]] = None,
    error: Optional[str] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    ensure_schema(db_path)
    delivery_id = uuid.uuid4().hex
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO webhook_deliveries (
                delivery_id, mapping_id, direction, event_type, status,
                request_payload, response_payload, error, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                delivery_id,
                mapping_id,
                direction,
                event_type,
                status,
                json.dumps(request_payload or {}, ensure_ascii=False),
                json.dumps(response_payload or {}, ensure_ascii=False),
                error,
            ),
        )
    return delivery_id


def list_webhook_deliveries(
    db_path: Path = DEFAULT_DB_PATH,
    limit: int = 100,
    mapping_id: Optional[str] = None,
) -> List[Dict[str, object]]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        if mapping_id:
            rows = conn.execute(
                """
                SELECT delivery_id, mapping_id, direction, event_type, status,
                       request_payload, response_payload, error, created_at
                FROM webhook_deliveries
                WHERE mapping_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (mapping_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT delivery_id, mapping_id, direction, event_type, status,
                       request_payload, response_payload, error, created_at
                FROM webhook_deliveries
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    return [dict(row) for row in rows]
