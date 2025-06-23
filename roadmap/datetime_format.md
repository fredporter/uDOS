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
- Millisecond precision
- Timezone-aware (numeric offset only)
- Filename-safe (CAPS, NUMERALS, and `-` only)
- Lexicographically sortable
- No AM/PM or named timezones (e.g., no `AEST`)

---

## 🕰️ Primary Timestamp Format (for display/logging)

```
YYYY-MM-DD HH:mm:ss.SSS ±hh:mm
```

**Example:**
```
2025-06-22 14:23:10.456 +10:00
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
| `TZCODE`      | Encoded timezone (see below)           | `P10`       |

---

## 🧩 Timezone Code Reference (TZCODE)

| Offset   | TZCODE |  | Offset   | TZCODE |
|----------|--------|--|----------|--------|
| +00:00   | Z00    |  | -01:00   | M01    |
| +01:00   | P01    |  | -02:00   | M02    |
| +02:00   | P02    |  | -03:00   | M03    |
| +03:00   | P03    |  | -04:00   | M04    |
| +04:00   | P04    |  | -05:00   | M05    |
| +05:00   | P05    |  | -06:00   | M06    |
| +06:00   | P06    |  | -07:00   | M07    |
| +07:00   | P07    |  | -08:00   | M08    |
| +08:00   | P08    |  | -09:00   | M09    |
| +09:00   | P09    |  | -10:00   | M10    |
| +10:00   | P10    |  | -11:00   | M11    |
| +11:00   | P11    |  | -12:00   | M12    |
| +12:00   | P12    |  |          |        |

---

## ✅ Summary

| Use Case         | Format                             | Example                         |
|------------------|------------------------------------|---------------------------------|
| Display/logging  | `YYYY-MM-DD HH:mm:ss.SSS ±hh:mm`   | `2025-06-22 14:23:10.456 +10:00`|
| Filename ID      | `YYYYMMDD-HHMMSS-SSS-TZCODE`       | `20250622-142310-456-P10`       |
| ISO fallback     | `YYYY-MM-DDTHH:mm:ss.SSSZ`          | `2025-06-22T14:23:10.456Z`      |

> NOTE: ISO fallback format may be used in interop layers, API calls, or legacy import/export bridges. It is not preferred for internal use.

---

*End of spec.*
