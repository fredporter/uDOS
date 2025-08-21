# uTASK-20250821-Markdown-First-Interactive-Docs

## Roadmap: Markdown-First Interactive Documents in uDOS

### 1. Define Protocol
- Establish `[SHORTCODE] {VARIABLE} <FUNCTION>` as the standard for interactive markdown commands
- Ensure all commands, options, and variables use CAPITAL LETTERS, NUMERALS 1-10, and DASH `-`

### 1a. Mapping TILE System & uHEX
- Integrate stackable mapping TILE system for organizing files and data
- Use uHEX segments in filenames to encode user data for traceability and organization
- Ensure uHEX codes use CAPITAL LETTERS and NUMERALS only

### 2. Update Workflow Scripts
- Modify uSCRIPT and workflow scripts to parse and execute markdown shortcodes
- Validate command syntax and capitalization

### 3. Standardize Documentation
- Update all docs and task files to use uDOS capitalization and file format protocols
- Document mapping TILE system and uHEX usage for filenames

### 3a. File Naming & Shortcode Conventions
- Filenames and shortcodes use only CAPITAL LETTERS, NUMERALS 1-10, and DASH `-`
- Options in filenames and commands are always CAPITALIZED
- Core description/title remains in Title Case

### 4. Implement Validation
- Add validation for command syntax in markdown files
- Enforce naming conventions and option formatting

### 5. Integrate Live Preview & Execution
- Enable live preview and execution of markdown commands in VS Code and browser via uCODE window

### 6. Document Examples & Best Practices
- Provide examples in `wizard/docs/uDOS-Style-Guide-and-Protocols.md`
- Create sample interactive markdown documents for users

### 7. Dev Mode Briefing Protocol
- For each Dev Mode session, create/update a briefing using the template: `wizard/briefings/uDEV-YYYYMMDD-CLAUDE-Briefing-Template.md`
- Briefings summarize context, protocols, session goals, and references for onboarding AI assistants (e.g., Claude) in VS Code
- Keep all dev briefings separate from user documentation and actions

*This roadmap ensures uDOS maintains a Markdown-first, protocol-driven approach for interactive documentation and command execution.*
