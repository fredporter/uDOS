# Binder Quickstart

Updated: 2026-03-03
Status: active how-to

## Purpose

Use this guide to create, validate, and start using a binder quickly.

## Quick Start

### 1. Create the binder structure

```bash
mkdir MyBinder
cd MyBinder
mkdir imports tables scripts
touch uDOS-table.db
```

### 2. Load and validate

```python
from pathlib import Path
from core.binder import load_binder_config, BinderValidator

binder_path = Path("./MyBinder")
config = load_binder_config(binder_path)
report = BinderValidator.validate(binder_path)
```

### 3. Use the binder database

```python
from core.binder import BinderDatabase

with BinderDatabase(binder_path) as db:
    rows = db.query("SELECT name FROM sqlite_master")
```

### 4. Generate feeds if needed

```python
from core.binder import BinderFeed

feed = BinderFeed(binder_path, base_url="https://example.com/binders")
items = feed.scan_files()
```

## Companion Guide

- [Binder Usage Guide](BINDER-USAGE-GUIDE.md)
