# uDOS Teletext Theme

Status: active supporting theme reference  
Updated: 2026-03-03

This is the supporting theme reference for the v1.5 `ucode` TUI lane.

## Design Goals

-   Fixed width canvas (default: 78 columns)
-   ASCII borders only
-   High contrast, minimal styling
-   NO_COLOR support

------------------------------------------------------------------------

## Palette Tokens

-   `fg` (default text)
-   `muted` (secondary/hints)
-   `accent` (selection highlight)
-   `ok`
-   `warn`
-   `err`
-   `title`

------------------------------------------------------------------------

## ASCII Border Set

-   Corners: `+`
-   Horizontal: `-`
-   Vertical: `|`
-   Header rule: `=`

------------------------------------------------------------------------

## Layout Rules

-   1 char inner padding
-   1 line gap between blocks
-   2 spaces between columns
-   Crop then pad (never wrap)

------------------------------------------------------------------------

## Example

    +------------------------------------------------------------------------------+
    | uDOS  Installer                                      ? help   Esc back      |
    +==============================================================================+
    | [1] Install   [2] Scaffold   [3] Run   [4] Config   [5] Logs                |
    |                                                                              |
    | Installer                                                                   |
    | - Step 1: Check deps                                                         |
    | - Step 2: Create dirs                                                        |
    |                                                                              |
    | ↑↓ move  Enter select  / filter  Ctrl+C quit                                 |
    +------------------------------------------------------------------------------+
