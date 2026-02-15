# uDOS Core Python Stdlib Profile

Goal: keep **uDOS core** offline-first and deterministic by moving all **networking & web** responsibilities to the **Wizard Server**. uDOS core scripts must run without internet, without sockets, and without HTTP clients.

## Core Rule

- **uDOS core**: filesystem, process control, parsing, formatting, hashing, time, local DB, logging, CLI.
- **Wizard Server**: any *remote* I/O (HTTP, sockets, email, FTP, websockets, TLS, async web clients), and any “phone home” behaviour.

If it can dial out or accept inbound connections → it belongs to **Wizard**.

---

# UCode Command Standard

All UCode commands:

- Are shown in **CAPS** by default
- Accept **any-case input**
- Are a **single word**
- Are **6 characters or fewer**
- Avoid abbreviations where possible

Pattern:

```
ucode COMMAND [args]
ucode COMMAND --help
```

## v1.3.16 Core/Wizard Ownership Rules

- Core keeps offline/local command surfaces.
- Wizard owns provider, integration, and full network-aware shakedown surfaces.
- Removed top-level core commands are hard-fail (no aliases/shims).

Core checks:

- `HEALTH` (stdlib/offline)
- `VERIFY` (TS/runtime)

Migration:

- `SHAKEDOWN` -> `HEALTH` or `VERIFY` (core), `WIZARD CHECK` (Wizard full checks)
- `PATTERN ...` -> `DRAW PAT ...`
- `DATASET ...` -> `RUN DATA ...`
- `INTEGRATION ...` -> `WIZARD INTEG ...`
- `PROVIDER ...` -> `WIZARD PROV ...`

---

# Allowed stdlib Modules in uDOS Core

> Format:
>
> - **Module** – purpose
> - **Use** – how uDOS core uses it
> - **UCode command** – CAPS command (≤6 chars)

---

## System, Files, Paths

- **os** – OS interfaces (env, dirs, permissions)

  - **Use**: environment variables, directory ops, file metadata
  - **UCode command**: LIST, LIST —env

- **pathlib** – modern path handling

  - **Use**: safe path joins, read/write files
  - **UCode command**: `PATHS`

- **shutil** – high-level file operations

  - **Use**: copy, move, tree operations
  - **UCode command**: `COPY`

- **glob** – wildcard matching

  - **Use**: pattern-based file discovery
  - **UCode command**: `FIND`

- **tempfile** – temporary files/dirs

  - **Use**: safe scratch workspace
  - **UCode command**: GHOST

- **stat** – file mode inspection

  - **Use**: permissions + type checks
  - **UCode command**: `RIGHTS`

---

## Processes & Runtime

- **sys** – runtime + argv

  - **Use**: arguments, exit codes
  - **UCode command**: `START`, `INPUT`

- **subprocess** – execute system commands

  - **Use**: git, vibe-cli, shell tools
  - **UCode command**: `RUN`

- **argparse** – CLI argument parsing

  - **Use**: consistent help + flags
  - **UCode command**: PASS

- **signal** – process signals

  - **Use**: graceful shutdown
  - **UCode command**: `TRAP`

- **atexit** – exit hooks

  - **Use**: guaranteed cleanup
  - **UCode command**: `CLEAN`

---

## Data & Storage

- **json** – JSON encoding/decoding

  - **Use**: config + state files
  - **UCode command**: READ

- **csv** – CSV read/write

  - **Use**: table import/export
  - **UCode command**: `TABLE`

- **configparser** – INI config files

  - **Use**: legacy/simple config
  - **UCode command**: `SETUP`

- **sqlite3** – embedded database

  - **Use**: local structured storage
  - **UCode command**: `QUERY`

- **pickle** *(discouraged)*

  - **Use**: trusted local cache only
  - **UCode command**: `CACHE`

---

## Compression & Archives

- **gzip** – compression
- **zipfile** – zip archives
- **tarfile** – tar archives
  - **Use**: pack/unpack bundles
  - **UCode command**: `PACK`

---

## Text & Parsing

- **re** – regular expressions

  - **Use**: search/replace, parsing
  - **UCode command**: REPLACE

- **string** – templating helpers

  - **Use**: simple string templates
  - **UCode command**: `DRAFT`

- **textwrap** – wrapping/indent

  - **Use**: TUI formatting
  - **UCode command**: `WRAP`

- **difflib** – file comparison

  - **Use**: diffs + similarity
  - **UCode command**: COMPARE

- **unicodedata** – unicode normalisation

  - **Use**: stable filenames
  - **UCode command**: RENAME

---

## Time & Identity

- **datetime** – timestamps

  - **Use**: logs + metadata
  - **UCode command**: `TIME`

- **time** – sleep + timers

  - **Use**: delays + benchmarking
  - **UCode command**: `WAIT`

- **zoneinfo** – timezone data

  - **Use**: consistent timezone handling (AEST default)
  - **UCode command**: `ZONE`

- **uuid** – unique identifiers

  - **Use**: local object IDs
  - **UCode command**: `UID`

- **hashlib** – hashing

  - **Use**: checksums, content addressing
  - **UCode command**: `HASH`

- **hmac** – keyed hashes

  - **Use**: local message sealing
  - **UCode command**: `SEAL`

- **base64** – binary-to-text encoding

  - **Use**: safe text transport
  - **UCode command**: `ENCODE`

---

## Maths & Collections

- **math** – calculations

  - **Use**: numeric operations
  - **UCode command**: CALCULATE

- **random** *(not for security)*

  - **Use**: games, sampling
  - **UCode command**: `ROLL`

- **secrets** – secure randomness

  - **Use**: tokens, salts
  - **UCode command**: `TOKEN`

- **statistics** – numeric summaries

  - **Use**: averages, medians
  - **UCode command**: `STUDY`

- **itertools** – iterator pipelines

  - **Use**: efficient chaining
  - **UCode command**: `CHAIN`

- **functools** – functional helpers

  - **Use**: caching, composition
  - **UCode command**: `STACK`

---

## Logging & Diagnostics

- **logging** – structured logging

  - **Use**: write to `~/memory/logs/`
  - **UCode command**: `LOG`

- **traceback** – stack traces

  - **Use**: error display
  - **UCode command**: `TRACE`

- **inspect** – introspection

  - **Use**: debug + metadata
  - **UCode command**: INSPECT

- **warnings** – runtime warnings

  - **Use**: soft deprecations
  - **UCode command**: `ALERT`

- **pdb** – debugger

  - **Use**: interactive debugging
  - **UCode command**: `DEBUG`

---

## Testing

- **unittest** – unit testing
- **doctest** – documentation tests
  - **Use**: regression safety
  - **UCode command**: `TEST`

---

# Disallowed in uDOS Core (Wizard Only)

- socket
- ssl
- http.client
- http.server
- urllib
- ftplib
- imaplib
- poplib
- smtplib
- telnetlib
- webbrowser

`asyncio` allowed only for **local concurrency**, never for network clients.

---

# Minimal v1 Core Command Set

The initial supported public CLI surface:

```
PATHS   FIND   COPY   PACK   HASH
TEXT    TABLE  SETUP  QUERY
TIME    WAIT   IDENT  TOKEN
LOG     DIFF   TEST   RUN
```

Everything else remains internal until stabilised.

---

# Architectural Note

uDOS core never speaks to the internet directly.

If remote data is required:

1. Wizard performs the network operation.
2. Wizard writes to a local file / sqlite / pipe.
3. uDOS core reads locally.

Offline-first. Deterministic. Inspectable.
