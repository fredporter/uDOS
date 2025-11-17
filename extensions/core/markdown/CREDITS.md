# uDOS Markdown Viewer - Credits & Attribution

## Version 1.0.24

This enhanced markdown viewer is built with and inspired by several excellent open-source projects and design systems.

---

## Core Dependencies

### Marked.js
- **Version**: 11.1.0
- **Purpose**: Fast markdown parser and compiler
- **License**: MIT
- **Website**: https://marked.js.org/
- **Repository**: https://github.com/markedjs/marked
- **Author**: Christopher Jeffrey and contributors

### Highlight.js
- **Version**: 11.9.0
- **Purpose**: Syntax highlighting for code blocks
- **License**: BSD 3-Clause
- **Website**: https://highlightjs.org/
- **Repository**: https://github.com/highlightjs/highlight.js
- **Authors**: Ivan Sagalaev and contributors

---

## Design Inspiration

### GitHub Markdown CSS
- **Inspiration**: GitHub's markdown rendering style
- **Themes**: Light and Dark mode color schemes
- **Note**: This is a custom implementation inspired by GitHub's design language, not a direct copy of GitHub's proprietary CSS
- **Reference**: https://github.com/sindresorhus/github-markdown-css

### Synthwave DOS Color System
- **Creator**: uDOS Project
- **Purpose**: Consistent retro-themed color palette across all uDOS extensions
- **File**: `extensions/shared/synthwave-dos-colors.css`
- **License**: Part of uDOS project

---

## Fonts

### Monaco
- **Type**: System monospace font
- **Platform**: macOS default monospace font
- **Fallbacks**: "Courier New", Courier, generic monospace

### SF Mono
- **Type**: Apple's San Francisco Monospaced font
- **Platform**: macOS (code editors and terminals)
- **Usage**: Code blocks and technical content

---

## Icons & Emoji

- **Panel Icons**: Native Unicode emoji (ℹ️, ⚠️, 🛑, ✅)
- **UI Icons**: Unicode symbols and emoji characters
- **Compatibility**: Universal browser support, no external icon libraries

---

## Features Inspired By

### Visual Studio Code
- **Feature**: Dark theme color scheme
- **Inspiration**: VS Code's dark+ theme
- **Usage**: Editor background colors and syntax highlighting

### Obsidian
- **Feature**: Panel/callout blocks
- **Inspiration**: Obsidian's callout syntax (`:::type`)
- **Implementation**: Custom PANEL processor

### Typora
- **Feature**: Split view mode (source + rendered)
- **Inspiration**: Typora's hybrid editing approach
- **Implementation**: Custom view mode switcher

---

## Original uDOS Features

The following features are original contributions to this markdown viewer:

### uCODE Command System
- **Creator**: uDOS Development Team
- **Purpose**: Interactive command execution from markdown
- **Syntax**: `[COMMAND|ARG|VALUE]`
- **Innovation**: Bridges documentation with system actions

### PANEL Processor
- **Creator**: uDOS Development Team
- **Purpose**: Enhanced callout blocks with Synthwave DOS styling
- **Types**: note, warning, danger, success
- **Features**: Click-to-copy, auto-collapse for long content

### Theme Integration
- **Creator**: uDOS Development Team
- **Purpose**: Seamless integration with uDOS Synthwave DOS aesthetic
- **Features**: Synchronized theming across all extensions

---

## Development Tools

### Python Flask
- **Version**: 2.x
- **Purpose**: Backend server for file serving and API
- **License**: BSD 3-Clause
- **Website**: https://flask.palletsprojects.com/

### Python Markdown2
- **Purpose**: Server-side markdown processing (original implementation)
- **License**: MIT
- **Repository**: https://github.com/trentm/python-markdown2

### TheFuzz (FuzzyWuzzy)
- **Purpose**: Fuzzy string matching for file search
- **License**: GPL-2.0
- **Repository**: https://github.com/seatgeek/thefuzz

---

## License

This markdown viewer is part of the **uDOS Project** and is distributed under the same license as the main project.

- **Original Code**: © uDOS Development Team
- **Dependencies**: See individual licenses above
- **Combined Work**: MIT License (compatible with all dependencies)

---

## Acknowledgments

Special thanks to:

- **Christopher Jeffrey** and the Marked.js team for the excellent markdown parser
- **Ivan Sagalaev** and the Highlight.js team for comprehensive syntax highlighting
- **GitHub** for pioneering clean markdown rendering aesthetics
- **The open-source community** for continuous inspiration and innovation
- **Early uDOS users** for feedback that shaped this viewer

---

## Version History

### v1.0.24 (Current)
- Complete rewrite with GitHub CSS theming
- Added uCODE command system
- Added PANEL callout blocks
- Implemented light/dark theme toggle
- Added split view mode
- Enhanced with Synthwave DOS color integration

### v1.0.x (Original)
- Flask-based markdown viewer
- Category tree navigation
- Fuzzy search
- Basic syntax highlighting

---

**Last Updated**: December 2024
**Maintainer**: uDOS Development Team
**Documentation**: See README.md for usage guide
