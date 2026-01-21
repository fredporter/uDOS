# Teletext Pattern Service

**Module:** wizard/services/teletext_patterns.py  
**Scope:** Wizard-only, offline, ANSI/ASCII pattern generation

## Purpose

Provide deterministic, testable teletext/ANSI patterns (chevrons, scanlines,
mosaic, C64 loader bars, raster bars, progress loader) without tying output to
stdout. Frames are returned as lists of strings so callers can render them into
TUI surfaces, API responses, or logs.

## Usage

```python
from wizard.services.teletext_patterns import TeletextPatternService, PatternName

service = TeletextPatternService(width=64, ascii_only=True)
frame = service.next_frame(PatternName.C64_BARS)
for line in frame:
    print(line)
```

### Options

- `width`: clamped to 20–80 columns (teletext grid alignment)
- `ascii_only`: avoids ANSI colour codes; useful for tests or plain terminals
- `reset()`: restores deterministic initial state for reproducible output

## Notes

- Offline-only, no cloud calls
- Uses `[WIZ]` tagged logging on init
- Suitable for Wizard TUI displays or API responses
