-- uDOS Table Database Schema
-- Minimal metadata registry for binder-local SQLite databases

CREATE TABLE IF NOT EXISTS udos_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS udos_tables (
    name TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
