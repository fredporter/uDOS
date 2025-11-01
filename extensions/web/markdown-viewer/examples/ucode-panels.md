# uDOS uCODE Panel Examples

This document demonstrates how to embed uCODE panels in markdown files using the new panel system.

## Basic Panel Syntax

```ucode panel:basic width:80 height:10
╔════════════════════════════════════════════════════════════════════════════╗
║                         BASIC PANEL EXAMPLE                                ║
║                                                                            ║
║  This is a simple panel with box-drawing characters.                      ║
║  Width: 80 characters                                                     ║
║  Height: 10 lines                                                         ║
║                                                                            ║
║  Status: [OK] Ready                                                       ║
╚════════════════════════════════════════════════════════════════════════════╝
```

## uCODE Syntax Highlighting

```ucode panel:syntax width:80 height:15
╔════════════════════════════════════════════════════════════════════════════╗
║                       uCODE SYNTAX EXAMPLES                                ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Basic Command:      [MOVE|NORTH]                                         ║
║  With Parameter:     [SET|THEME*GALAXY]                                   ║
║  Multiple Params:    [OUTPUT|SAVE*test.txt*true]                          ║
║                                                                            ║
║  Module Reference:   [MAP|EXPLORE]                                        ║
║  Status Command:     [HEALTH|CHECK]                                       ║
║  Variable Access:    [VAR|GET*player_name]                                ║
║                                                                            ║
║  Status: ✓ All syntax patterns working                                    ║
╚════════════════════════════════════════════════════════════════════════════╝
```

## Compact Dashboard Panel

```ucode panel:dashboard width:40 height:20
╔══════════════════════════════════════╗
║         SYSTEM STATUS                ║
╠══════════════════════════════════════╣
║                                      ║
║  Health:      ████████░░  80%        ║
║  Energy:      ██████████ 100%        ║
║  Progress:    ████░░░░░░  40%        ║
║                                      ║
║  Location:    Nexus Core             ║
║  Theme:       🚀 GALAXY               ║
║  Time:        14:23:47               ║
║                                      ║
║  Status:      ✓ All systems go       ║
║                                      ║
║  [MAP|STATUS]                        ║
║  [HEALTH|CHECK]                      ║
║  [VAR|LIST]                          ║
╚══════════════════════════════════════╝
```

## Wide Map Panel

```ucode panel:worldmap width:120 height:30
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                              WORLD MAP - THE NEXUS                                                   ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                                      ║
║                                   ╔═══════╗                                                                          ║
║                                   ║ NORTH ║                                                                          ║
║                                   ║  HUB  ║                                                                          ║
║                          ╔════════╩═══════╩════════╗                                                                 ║
║                          ║                         ║                                                                 ║
║                          ║    KNOWLEDGE CENTER     ║                                                                 ║
║                          ║                         ║                                                                 ║
║          ╔═══════╗       ╚═════════════════════════╝       ╔═══════╗                                                ║
║          ║  WEST ║═══════════╗         ╔═══════════════════║ EAST  ║                                                ║
║          ║ PLAZA ║            ║         ║                   ║ TOWER ║                                                ║
║          ╚═══════╝            ║         ║                   ╚═══════╝                                                ║
║                          ╔════╩═════════╩════╗                                                                       ║
║                          ║                   ║                                                                       ║
║                          ║   NEXUS CORE ⚡    ║  <- You are here                                                     ║
║                          ║                   ║                                                                       ║
║                          ╚═══════════════════╝                                                                       ║
║                                   ║                                                                                  ║
║                          ╔════════╩════════╗                                                                         ║
║                          ║                 ║                                                                         ║
║                          ║  TERMINAL DECK  ║                                                                         ║
║                          ║                 ║                                                                         ║
║                          ╚═════════════════╝                                                                         ║
║                                                                                                                      ║
║  Legend:  ⚡ Current Location    ═══ Passage    ╔╗║═ Structure                                                      ║
║                                                                                                                      ║
║  Commands: [MAP|EXPLORE*north]  [MAP|EXPLORE*east]  [MAP|STATUS]                                                    ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

## Status Panel Variants

### Success Panel

```ucode panel:success width:60 height:8
╔══════════════════════════════════════════════════════╗
║  ✓ OPERATION SUCCESSFUL                              ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  File saved: /data/USER.UDT                          ║
║  Bytes written: 2,048                                ║
║  Time: 0.003s                                        ║
╚══════════════════════════════════════════════════════╝
```

### Error Panel

```ucode panel:error width:60 height:8
╔══════════════════════════════════════════════════════╗
║  ✗ ERROR: File Not Found                             ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Could not locate: /data/MISSING.UDO                 ║
║  Error code: FILE_NOT_FOUND                          ║
║  Suggestion: Check file path and try again           ║
╚══════════════════════════════════════════════════════╝
```

### Warning Panel

```ucode panel:warning width:60 height:8
╔══════════════════════════════════════════════════════╗
║  ⚠ WARNING: Low Memory                               ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Available: 128 KB                                   ║
║  Required: 256 KB                                    ║
║  Action: Free up memory before continuing            ║
╚══════════════════════════════════════════════════════╝
```

### Info Panel

```ucode panel:info width:60 height:8
╔══════════════════════════════════════════════════════╗
║  ℹ INFORMATION: System Update Available              ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Version: v1.2.1                                     ║
║  Size: 45 MB                                         ║
║  Release notes: /docs/CHANGELOG.md                   ║
╚══════════════════════════════════════════════════════╝
```

## Command Reference Panel

```ucode panel:commands width:100 height:25
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                  COMMAND REFERENCE                                           ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                              ║
║  MOVEMENT COMMANDS                                                                           ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║  [MOVE|NORTH]          Move north one room                                                   ║
║  [MOVE|SOUTH]          Move south one room                                                   ║
║  [MOVE|EAST]           Move east one room                                                    ║
║  [MOVE|WEST]           Move west one room                                                    ║
║                                                                                              ║
║  SYSTEM COMMANDS                                                                             ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║  [SET|THEME*<name>]    Change active theme                                                   ║
║  [VAR|LIST]            List all variables                                                    ║
║  [VAR|GET*<name>]      Get variable value                                                    ║
║  [VAR|SET*<name>*<v>]  Set variable value                                                    ║
║                                                                                              ║
║  MAP COMMANDS                                                                                ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║  [MAP|SHOW]            Display current map                                                   ║
║  [MAP|EXPLORE*<dir>]   Explore in direction                                                  ║
║  [MAP|STATUS]          Show location status                                                  ║
║                                                                                              ║
║  Type HELP <command> for detailed information                                                ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
```

## Progress Bar Panel

```ucode panel:progress width:80 height:12
╔════════════════════════════════════════════════════════════════════════════╗
║                         INSTALLATION PROGRESS                              ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Installing Monaspace fonts...                                             ║
║  ████████████████████████████████████████████████░░░░░░  80% Complete      ║
║                                                                            ║
║  Downloaded: 4/5 font files                                                ║
║  Remaining: ~30 seconds                                                    ║
║                                                                            ║
║  Status: ⚙ Installing Monaspace Neon...                                    ║
╚════════════════════════════════════════════════════════════════════════════╝
```

## Theme Showcase

### ⚔️ DUNGEON Theme

```ucode panel:dungeon width:70 height:10
╔════════════════════════════════════════════════════════════════╗
║                  🏰 DUNGEON THEME ACTIVE                       ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  A dark, mysterious theme for text-based adventures            ║
║  Colors: Gold accents on obsidian black                        ║
║  Font: Monaspace Neon with texture healing                     ║
║                                                                ║
║  [SET|THEME*DUNGEON] to activate                               ║
╚════════════════════════════════════════════════════════════════╝
```

### 🚀 GALAXY Theme

```ucode panel:galaxy width:70 height:10
╔════════════════════════════════════════════════════════════════╗
║                   🌌 GALAXY THEME ACTIVE                       ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  A space-exploration theme with cosmic colors                  ║
║  Colors: Cyan stars on deep space black                        ║
║  Font: Monaspace Argon with ligatures                          ║
║                                                                ║
║  [SET|THEME*GALAXY] to activate                                ║
╚════════════════════════════════════════════════════════════════╝
```

### 📊 FOUNDATION Theme

```ucode panel:foundation width:70 height:10
╔════════════════════════════════════════════════════════════════╗
║                 📚 FOUNDATION THEME ACTIVE                     ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  A clean, professional theme for productivity                  ║
║  Colors: Pure white on charcoal gray                           ║
║  Font: Monaspace Xenon with balanced spacing                   ║
║                                                                ║
║  [SET|THEME*FOUNDATION] to activate                            ║
╚════════════════════════════════════════════════════════════════╝
```

## Responsive Behavior

On mobile devices, panels automatically become scrollable if they exceed screen width. Try viewing this on different screen sizes!

## Integration Example

To embed a uCODE panel in your markdown:

1. Start with triple backticks and `ucode` language identifier
2. Add panel metadata: `panel:name width:N height:N`
3. Add your ASCII/box-drawing content
4. Close with triple backticks

Example:

````markdown
```ucode panel:myPanel width:80 height:10
╔════════════════════════════════════════════════════════════════════════════╗
║  Your content here with [UCODE|COMMANDS] highlighted                      ║
╚════════════════════════════════════════════════════════════════════════════╝
```
````

The panel system will automatically:
- Parse the metadata
- Create a styled panel container
- Apply syntax highlighting to `[MODULE|COMMAND*PARAM]` patterns
- Make it responsive and accessible
- Apply the current theme colors

---

**Note**: This example file demonstrates the complete uCODE panel system. View the source to see the markdown syntax used to create these panels.
