# bat - Syntax-highlighted File Viewer

## Overview
`bat` is a `cat` clone with syntax highlighting and Git integration.

## Usage Examples

```bash
# View file with syntax highlighting
bat file.py

# Show line numbers
bat -n file.js

# Show Git diff
bat --diff file.md

# Page through large files
bat --paging=always large-file.log

# Highlight specific lines
bat -H 10:20 file.txt
```

## uDOS Integration

Available in uCode shell:
- `bat <file>` - Enhanced file viewing
- Integrated with uScript for code display
- Used in dashboard for log file viewing

## Configuration

Create `~/.config/bat/config` for custom settings:
```
--theme="Dracula"
--style="numbers,changes,header"
--pager="less -FR"
```
