# uDOS Style Guide and Protocols

## File Naming Conventions

- All system roles and modes use CAPITAL LETTERS: `WIZARD`, `IMP`, `GHOST`, `DRONE`, `SORCERER`, `TOMB`, `SANDBOX`, `DEV MODE`, `ASSIST MODE`
- Filenames use only CAPITAL LETTERS, NUMERALS 1-10, and DASH `-` for system keywords, shortcodes, and options.
- Options in filenames and commands are always CAPITALIZED.
- The core description (after the system keywords) uses Title Case: `Description-Of-The-Doc.md`
- Example: `uDEV-20250821-UTILITY-ANALYTICS-Report.md`
- User documentation: `uDOC-YYYYMMDD-Description-Of-The-Doc.md`
- Development notes: `uDEV-YYYYMMDD-Description-Of-The-Doc.md`
- Task files: `uTASK-YYYYMMDD-Description-Of-The-Task.md`
- Reports: `uDEV-YYYYMMDD-Description-Of-The-Report.md`

## Shortcode Command Protocols

- Shortcodes use CAPITAL LETTERS and DASH: `[COMMAND-OPTION] {VARIABLE-OPTION-VALUE} <FUNCTION-OPTION>`
- Example: `[RUN-SCRIPT] {USER-INPUT} <EXECUTE>`
- Variable names use CAPITAL LETTERS and NUMERALS only.
- Options are always CAPITALIZED.
- Description or doc title remains in Title Case.

## Mapping TILE System & uHEX

- uDOS uses a stackable mapping TILE system for organizing files and data.
- Filenames may include a uHEX segment that encodes user data for traceability and organization.
- Example: `uDEV-20250821-4F2A8C50-External-Package-Reorganization.md` (where `4F2A8C50` is a uHEX code)
- uHEX codes are always in CAPITAL LETTERS and NUMERALS.

## Markdown-First Interactive Documents

- Markdown files can include interactive shortcodes and commands for uSCRIPT execution.
- Example: `[LOG-SESSION] {SESSION-ID} <ARCHIVE>`
- All interactive commands follow the capitalization and dash conventions above.

## Best Practices

- Always use uDOS capitalization for system keywords, options, and shortcodes.
- Use Title Case for descriptions and document titles.
- Avoid special characters except DASH `-` and NUMERALS 1-10 in filenames and commands.
- Document all new shortcodes and options in this guide.
