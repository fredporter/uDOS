-- Binder Compiler Database Schema
-- Multi-format document compilation system
-- Author: uDOS Team
-- Version: 0.1.0
-- Created: 2026-01-16

CREATE TABLE IF NOT EXISTS binders (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    author TEXT,
    tags TEXT,
    template TEXT,
    total_chapters INTEGER DEFAULT 0,
    total_words INTEGER DEFAULT 0,
    CHECK (status IN ('draft', 'in-progress', 'review', 'complete'))
);

CREATE TABLE IF NOT EXISTS chapters (
    id TEXT PRIMARY KEY,
    binder_id TEXT NOT NULL,
    chapter_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    order_index INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    word_count INTEGER DEFAULT 0,
    has_code BOOLEAN DEFAULT 0,
    has_images BOOLEAN DEFAULT 0,
    has_tables BOOLEAN DEFAULT 0,
    FOREIGN KEY (binder_id) REFERENCES binders(id) ON DELETE CASCADE,
    UNIQUE (binder_id, chapter_id),
    CHECK (status IN ('draft', 'review', 'complete'))
);

CREATE TABLE IF NOT EXISTS outputs (
    id TEXT PRIMARY KEY,
    binder_id TEXT NOT NULL,
    format TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    checksum TEXT,
    compiled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    compiler_version TEXT,
    include_toc BOOLEAN DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'generated',
    FOREIGN KEY (binder_id) REFERENCES binders(id) ON DELETE CASCADE,
    CHECK (format IN ('markdown', 'pdf', 'json', 'brief')),
    CHECK (status IN ('generated', 'verified', 'published'))
);

CREATE TABLE IF NOT EXISTS binder_metadata (
    id TEXT PRIMARY KEY,
    binder_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    value_type TEXT DEFAULT 'string',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (binder_id) REFERENCES binders(id) ON DELETE CASCADE,
    UNIQUE (binder_id, key)
);

CREATE INDEX IF NOT EXISTS idx_binders_status ON binders(status);
CREATE INDEX IF NOT EXISTS idx_binders_created_at ON binders(created_at);
CREATE INDEX IF NOT EXISTS idx_binders_updated_at ON binders(updated_at);
CREATE INDEX IF NOT EXISTS idx_chapters_binder_id ON chapters(binder_id);
CREATE INDEX IF NOT EXISTS idx_chapters_status ON chapters(status);
CREATE INDEX IF NOT EXISTS idx_chapters_order ON chapters(binder_id, order_index);
CREATE INDEX IF NOT EXISTS idx_chapters_updated_at ON chapters(updated_at);
CREATE INDEX IF NOT EXISTS idx_outputs_binder_id ON outputs(binder_id);
CREATE INDEX IF NOT EXISTS idx_outputs_format ON outputs(format);
CREATE INDEX IF NOT EXISTS idx_outputs_compiled_at ON outputs(compiled_at);
CREATE INDEX IF NOT EXISTS idx_metadata_binder_id ON binder_metadata(binder_id);
CREATE INDEX IF NOT EXISTS idx_metadata_key ON binder_metadata(binder_id, key);

CREATE TRIGGER IF NOT EXISTS update_binder_timestamp AFTER UPDATE ON binders
BEGIN
    UPDATE binders SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_chapter_timestamp AFTER UPDATE ON chapters
BEGIN
    UPDATE chapters SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_binder_chapter_count_insert AFTER INSERT ON chapters
BEGIN
    UPDATE binders SET total_chapters = (SELECT COUNT(*) FROM chapters WHERE binder_id = NEW.binder_id) WHERE id = NEW.binder_id;
END;

CREATE TRIGGER IF NOT EXISTS update_binder_chapter_count_delete AFTER DELETE ON chapters
BEGIN
    UPDATE binders SET total_chapters = (SELECT COUNT(*) FROM chapters WHERE binder_id = OLD.binder_id) WHERE id = OLD.binder_id;
END;

CREATE TRIGGER IF NOT EXISTS update_binder_word_count AFTER UPDATE ON chapters WHEN NEW.word_count != OLD.word_count
BEGIN
    UPDATE binders SET total_words = (SELECT SUM(word_count) FROM chapters WHERE binder_id = NEW.binder_id) WHERE id = NEW.binder_id;
END;

CREATE VIEW IF NOT EXISTS binder_summary AS
SELECT 
    b.id,
    b.name,
    b.status,
    b.total_chapters,
    b.total_words,
    b.created_at,
    b.updated_at,
    COUNT(DISTINCT o.id) as output_count,
    GROUP_CONCAT(DISTINCT o.format) as available_formats,
    SUM(CASE WHEN c.status = 'complete' THEN 1 ELSE 0 END) as complete_chapters,
    ROUND(100.0 * SUM(CASE WHEN c.status = 'complete' THEN 1 ELSE 0 END) / NULLIF(b.total_chapters, 0), 1) as completion_percent
FROM binders b
LEFT JOIN chapters c ON b.id = c.binder_id
LEFT JOIN outputs o ON b.id = o.binder_id
GROUP BY b.id;

CREATE VIEW IF NOT EXISTS chapter_details AS
SELECT 
    c.id,
    c.binder_id,
    c.chapter_id,
    c.title,
    c.order_index,
    c.status,
    c.word_count,
    c.has_code,
    c.has_images,
    c.has_tables,
    c.created_at,
    c.updated_at,
    b.name as binder_name,
    b.status as binder_status
FROM chapters c
JOIN binders b ON c.binder_id = b.id;
