---
title: uDOS Date and Time Format Specification
version: 1.1
author: Otter (uOS)
date: 2025-06-24
---

# 📅 uDOS Date and Time Format Specification

This document defines the standard formats for date and time used throughout uDOS, including log entries, filenames, and all time-based identifiers.

## 🧠 Goals
- Human-readable and machine-parsable
- Timezone-aware 
- Filename-safe (CAPS, NUMERALS, and `-` only)
- Lexicographically sortable

---

## 🕰️ Primary Timestamp Format (for display/logging)

```
YYYY-MM-DD HH:mm:ss.SSS ±hh:mm TIMEZ
```

**Example:**
```
2025-06-22 14:23:10.456 +10:00 AES
```

### Format Breakdown
| Field        | Description                      | Example       |
|--------------|----------------------------------|---------------|
| `YYYY-MM-DD` | ISO date                         | `2025-06-22`  |
| `HH:mm:ss`   | 24-hour time                     | `14:23:10`    |
| `.SSS`       | Milliseconds (delimiter `.`)     | `.456`        |
| `±hh:mm`     | Timezone offset (required)       | `+10:00`      |

---

## 🗂 Filename Timestamp Format

Used for naming all uDOS-generated files, folders, and unique log IDs. Designed for filesystem safety and maximum compatibility.

```
YYYYMMDD-HHMMSS-SSS-TZCODE
```

**Example:**
```
20250622-142310-456-P10
```

### Format Breakdown
| Field         | Description                             | Example     |
|---------------|-----------------------------------------|-------------|
| `YYYYMMDD`    | Compact ISO date                        | `20250622`  |
| `HHMMSS`      | Hour, minute, second                    | `142310`    |
| `SSS`         | Milliseconds, separate field            | `456`       |
| `TIMEZ`      | Encoded timezone 

