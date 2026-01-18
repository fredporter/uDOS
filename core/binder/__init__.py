"""
Binder System Module

Provides isolated document organization with local databases, offline-first design.

**Key Components:**
- BinderConfig: Metadata (name, version, author, tags)
- BinderValidator: Folder structure validation
- BinderDatabase: Database context for local queries (Task 8)
- BinderFeed: RSS feed generation (Task 9)

**Architecture:**
Each binder is a self-contained folder with:
- uDOS-table.db: Local SQLite database
- imports/: CSV, JSON, YAML sources
- tables/: Exported .table.md files
- scripts/: Markdown executables
- .binder-config: Metadata file (optional)

**Isolation Model:**
- Each binder has its own database (no sharing)
- Relative paths resolve within binder scope
- Cross-binder access requires explicit paths
- Encryption optional for sensitive data
"""

from .config import BinderConfig, BinderMetadata, load_binder_config, save_binder_config
from .validator import BinderValidator, ValidationReport, SeverityLevel
from .database import BinderDatabase, AccessMode, open_binder_db, DatabaseInfo
from .feed import (
    BinderFeed,
    FeedFormat,
    FeedItem,
    FrontmatterData,
    FrontmatterExtractor,
    ContentPreview,
)

__all__ = [
    # Config
    "BinderConfig",
    "BinderMetadata",
    "load_binder_config",
    "save_binder_config",
    # Validation
    "BinderValidator",
    "ValidationReport",
    "SeverityLevel",
    # Database
    "BinderDatabase",
    "AccessMode",
    "open_binder_db",
    "DatabaseInfo",
    # Feed
    "BinderFeed",
    "FeedFormat",
    "FeedItem",
    "FrontmatterData",
    "FrontmatterExtractor",
    "ContentPreview",
]

__version__ = "1.0.0"
