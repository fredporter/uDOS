# Configuration System

uDOS uses a unified configuration system based on a user-editable markdown file.

---

## Quick Reference

| Command                  | Description                      |
| ------------------------ | -------------------------------- |
| `PROFILE`                | View current profile             |
| `PROFILE SETUP`          | Run setup wizard                 |
| `PROFILE EDIT`           | Open udos.md in editor           |
| `PROFILE SET $VAR value` | Set a variable                   |
| `PROFILE GET $VAR`       | Get a variable value             |
| `GET $VAR`               | Shorthand for getting a variable |

---

## Configuration File

Your settings are stored in:

```
memory/config/udos.md
```

This is a markdown file you can edit directly with any text editor.

### File Format

```markdown
# uDOS Configuration

## Profile

$USER_NAME: survivor
$USER_EMAIL:
$USER_LOCATION:
$USER_TIMEZONE: UTC

## Security

$AUTH_ENABLED: false
$AUTH_METHOD: none
$SESSION_TIMEOUT: 0

## Preferences

$THEME: foundation
$SOUND_ENABLED: true
$TIPS_ENABLED: true
$AUTO_SAVE: true
$COLOR_MODE: auto

## Project

$PROJECT_NAME:
$PROJECT_DESCRIPTION:

## Custom Variables

$MY_VAR_1:
$MY_VAR_2:
```

---

## Variable Reference

### Profile Variables

| Variable         | Type   | Default  | Description              |
| ---------------- | ------ | -------- | ------------------------ |
| `$USER_NAME`     | string | survivor | Your display name        |
| `$USER_EMAIL`    | string |          | Email address (optional) |
| `$USER_LOCATION` | string |          | Your location            |
| `$USER_TIMEZONE` | string | UTC      | IANA timezone            |

### Security Variables

| Variable           | Type   | Default | Description                  |
| ------------------ | ------ | ------- | ---------------------------- |
| `$AUTH_ENABLED`    | bool   | false   | Enable session security      |
| `$AUTH_METHOD`     | string | none    | `none`, `pin`, or `password` |
| `$SESSION_TIMEOUT` | int    | 0       | Auto-lock minutes (0=never)  |

### Preference Variables

| Variable         | Type   | Default    | Description                                 |
| ---------------- | ------ | ---------- | ------------------------------------------- |
| `$THEME`         | string | foundation | `foundation`, `galaxy`, `survival`, `retro` |
| `$SOUND_ENABLED` | bool   | true       | Enable sound effects                        |
| `$TIPS_ENABLED`  | bool   | true       | Show helpful tips                           |
| `$AUTO_SAVE`     | bool   | true       | Auto-save documents                         |
| `$COLOR_MODE`    | string | auto       | `light`, `dark`, `auto`                     |

### Project Variables

| Variable               | Type   | Default | Description          |
| ---------------------- | ------ | ------- | -------------------- |
| `$PROJECT_NAME`        | string |         | Current project name |
| `$PROJECT_DESCRIPTION` | string |         | Project description  |
| `$PROJECT_START`       | string |         | Project start date   |

### Custom Variables

| Variable                        | Type   | Description            |
| ------------------------------- | ------ | ---------------------- |
| `$MY_VAR_1` through `$MY_VAR_5` | string | User-defined variables |

Use custom variables in templates:

```markdown
Hello $MY_VAR_1!
```

### System Variables (Read-Only)

| Variable         | Description                 |
| ---------------- | --------------------------- |
| `$SYS_VERSION`   | uDOS version                |
| `$SYS_DEVICE`    | Device name                 |
| `$SYS_MODE`      | `PROD`, `DEV`, or `OFFLINE` |
| `$SYS_REALM`     | `USER_MESH` or `WIZARD`     |
| `$SYS_TIMESTAMP` | Current timestamp           |

---

## Priority Resolution

Variables are resolved in this order (highest priority first):

1. **Environment** - `$UDOS_*` env variables
2. **Session** - Runtime overrides
3. **User Config** - `memory/config/udos.md`
4. **Defaults** - Built-in defaults

### Environment Override Example

```bash
export UDOS_THEME=galaxy
./start_udos.sh
```

---

## Security

### Authentication Methods

| Method     | Description       | Storage                 |
| ---------- | ----------------- | ----------------------- |
| `none`     | No authentication | -                       |
| `pin`      | 4-6 digit PIN     | Hashed in keystore      |
| `password` | Password          | bcrypt hash in keystore |

**Important:** Credentials are stored in the encrypted keystore at `core/security/.keys/`, NOT in udos.md.

### Session Timeout

Set `$SESSION_TIMEOUT` to auto-lock after inactivity:

- `0` - Never lock (default)
- `5` - Lock after 5 minutes
- `30` - Lock after 30 minutes

---

## Alpine Compliance

The configuration system follows Alpine principles:

| Principle         | Implementation             |
| ----------------- | -------------------------- |
| Minimal footprint | Single config file         |
| No root required  | User-space only            |
| Portable          | `/home/tc/udos/` structure |
| Human-readable    | Markdown format            |

### Alpine Structure

```
/home/user/udos/
├── udos.md              # User config (editable)
├── .credentials/        # Encrypted secrets (700)
├── memory/              # User workspace (755)
└── .cache/              # Ephemeral (755)
```

---

## API Integration

### REST Endpoints

```
GET  /api/config           # Get all user config
GET  /api/config/{var}     # Get specific variable
POST /api/config/{var}     # Set variable
POST /api/config/setup     # Run setup wizard
GET  /api/forms/{section}  # Get form definition
```

### Form Integration (gtx-form)

The configuration system provides form definitions for the uCode Markdown App:

```json
{
  "section": "profile",
  "fields": [
    {
      "name": "USER_NAME",
      "type": "text",
      "label": "Your display name",
      "value": "survivor",
      "validation": { "minLength": 1, "maxLength": 50 }
    }
  ]
}
```

---

## Examples

### Set Your Name

```
PROFILE SET $USER_NAME Fred
```

### Change Theme

```
PROFILE SET $THEME galaxy
```

### View a Variable

```
PROFILE GET $THEME
```

Or shorthand:

```
GET $THEME
```

### Enable PIN Security

```
PROFILE SET $AUTH_ENABLED true
PROFILE SET $AUTH_METHOD pin
```

### Create Custom Variable

```
PROFILE SET $MY_VAR_1 Hello World
```

Use in template:

```markdown
Message: $MY_VAR_1
```

---

## Wizard Dashboard UI Preferences

Wizard dashboard typography is controlled client-side via CSS variables and local
storage (system-first, no server state).

**Local storage keys:**

- `wizard-typography-v1` — current typography selection (heading/body/code, size, ratio)
- `wizard-theme` — `dark` or `light`

**CSS variables (runtime):**

- `--font-prose-title`
- `--font-prose-body`
- `--font-code`
- `--scale-prose-title`
- `--scale-prose-body`
- `--scale-code`
- `--font-emoji`

Bundled font files are served from the Wizard Font Manager at:

```
wizard/font-manager/fonts/
```

---

## Related Documentation

- [Commands Reference](commands/README.md)
- [TUI Guide](tui/README.md)
- [Architecture](ARCHITECTURE.md)

---

**Last Updated:** 2026-01-25
**Version:** Core v1.1.0.0
