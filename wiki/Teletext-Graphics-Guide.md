# Teletext Graphics Guide (v1.2.15)

Complete reference for BBC Teletext-style 8-color ANSI graphics in uDOS.

---

## Overview

Teletext graphics use 8-color ANSI rendering with box-drawing characters for retro terminal displays. Inspired by BBC Teletext (1970s-1990s), this format provides colorful, compact pages ideal for menus, status screens, and information displays.

### Key Features

- **8-Color Palette**: Black, red, green, yellow, blue, magenta, cyan, white
- **ANSI Rendering**: Terminal escape codes for color
- **Page System**: Multi-page navigation
- **Compact**: 40 columns × 25 lines (classic format)
- **Size Limit**: 10KB per page (~200 lines max)

---

## Color System

### 8-Color Palette

```
{0}Black{/}    (background, shadows)
{1}Red{/}      (alerts, errors)
{2}Green{/}    (success, borders)
{3}Yellow{/}   (warnings, highlights)
{4}Blue{/}     (information, links)
{5}Magenta{/}  (special, accents)
{6}Cyan{/}     (secondary info)
{7}White{/}    (primary text)
```

### Color Tags

Use `{N}text{/}` syntax where N is 0-7:

```
{2}Green text{/} followed by {1}Red text{/}
```

### Palette Presets

#### Classic (Standard ANSI)
```json
{
  "0": "\\033[30m",  // Black
  "1": "\\033[31m",  // Red
  "2": "\\033[32m",  // Green
  "3": "\\033[33m",  // Yellow
  "4": "\\033[34m",  // Blue
  "5": "\\033[35m",  // Magenta
  "6": "\\033[36m",  // Cyan
  "7": "\\033[37m"   // White
}
```

#### Earth Tones
- Browns, greens, muted blues
- Natural aesthetic

#### Terminal Green
- Monochrome green (retro CRT)
- All text in varying green shades

#### Amber
- Monochrome orange/amber
- Classic terminal look

---

## Box-Drawing Characters

### Teletext Style

```
═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬    (Double-line)
─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼    (Single-line)
▀ ▄ █ ▌ ▐ ░ ▒ ▓           (Block graphics)
```

### Mosaic Blocks

```
▀ Upper half block
▄ Lower half block
█ Full block
▌ Left half block
▐ Right half block
░ Light shade
▒ Medium shade
▓ Dark shade
```

---

## Page Templates

### Welcome Screen

```
{2}╔═══════════════════════════════════════╗{/}
{2}║{/}  {3}WELCOME TO uDOS SURVIVAL SYSTEM{/}  {2}║{/}
{2}╠═══════════════════════════════════════╣{/}
{2}║{/}                                       {2}║{/}
{2}║{/}  {7}Your offline survival companion{/}   {2}║{/}
{2}║{/}                                       {2}║{/}
{2}║{/}  {6}▶{/} {7}Water Guides{/}                   {2}║{/}
{2}║{/}  {6}▶{/} {7}Fire Starting{/}                  {2}║{/}
{2}║{/}  {6}▶{/} {7}Shelter Building{/}               {2}║{/}
{2}║{/}  {6}▶{/} {7}Food & Foraging{/}                {2}║{/}
{2}║{/}                                       {2}║{/}
{2}╚═══════════════════════════════════════╝{/}
```

### Menu System

```
{2}╔═══════════════════════════════════╗{/}
{2}║{/}  {7}MAIN MENU - uDOS v1.2.15{/}      {2}║{/}
{2}╠═══════════════════════════════════╣{/}
{2}║{/}                                   {2}║{/}
{2}║{/}  {3}1.{/} {7}Knowledge Guides{/}             {2}║{/}
{2}║{/}  {3}2.{/} {7}Graphics System{/}              {2}║{/}
{2}║{/}  {3}3.{/} {7}Workflows & Missions{/}         {2}║{/}
{2}║{/}  {3}4.{/} {7}Configuration{/}                {2}║{/}
{2}║{/}                                   {2}║{/}
{2}║{/}  {3}0.{/} {7}Exit{/}                         {2}║{/}
{2}╚═══════════════════════════════════╝{/}
```

### Status Dashboard

```
{2}╔════════════════════════════════╗{/}
{2}║{/}  {3}SYSTEM STATUS{/}              {2}║{/}
{2}╠════════════════════════════════╣{/}
{2}║{/}                                {2}║{/}
{2}║{/}  {7}Location:{/}  {6}AU-BNE{/}           {2}║{/}
{2}║{/}  {7}Grid:{/}      {6}AA340-100{/}        {2}║{/}
{2}║{/}                                {2}║{/}
{2}║{/}  {7}Knowledge Bank:{/}           {2}║{/}
{2}║{/}    {2}▣{/} {7}Water{/}    {2}[26]{/}        {2}║{/}
{2}║{/}    {2}▣{/} {7}Fire{/}     {2}[20]{/}        {2}║{/}
{2}║{/}    {2}▣{/} {7}Shelter{/}  {2}[20]{/}        {2}║{/}
{2}╚════════════════════════════════╝{/}
```

### Information Page

```
{4}╔════════════════════════════════╗{/}
{4}║{/} {7}WATER PURIFICATION{/}           {4}║{/}
{4}╠════════════════════════════════╣{/}
{4}║{/}                                {4}║{/}
{4}║{/} {3}Boiling:{/}                     {4}║{/}
{4}║{/}   {7}• 1 minute rolling boil{/}    {4}║{/}
{4}║{/}   {7}• 3 minutes at altitude{/}    {4}║{/}
{4}║{/}                                {4}║{/}
{4}║{/} {3}Filtering:{/}                   {4}║{/}
{4}║{/}   {7}• Cloth pre-filter{/}         {4}║{/}
{4}║{/}   {7}• Sand/charcoal layers{/}     {4}║{/}
{4}║{/}                                {4}║{/}
{4}║{/} {6}Page 1 of 3{/}                  {4}║{/}
{4}╚════════════════════════════════╝{/}
```

---

## Command Usage

### Generate Page

```bash
# Basic usage
MAKE --format teletext --palette classic --source "Welcome Screen"

# Multi-line source
MAKE --format teletext --palette earth --source "
{2}Title{/}
{7}Content{/}
"

# From file
MAKE --format teletext --palette terminal --source "$(cat page.txt)"
```

### Palette Options

```bash
--palette classic    # Standard ANSI colors
--palette earth      # Earth tones (browns, greens)
--palette terminal   # Green monochrome
--palette amber      # Amber monochrome
```

### Output

```bash
--output memory/drafts/teletext/menu.ans
```

---

## Best Practices

### 1. Color Contrast

✅ **Good Contrast**:
```
{2}Green border{/} with {7}white text{/}
{4}Blue background{/} with {7}white text{/}
```

❌ **Poor Contrast**:
```
{3}Yellow{/} on {7}white{/} (hard to read)
{4}Blue{/} on {0}black{/} (may be too dark)
```

### 2. Consistent Borders

Use one border style per page:

```
{2}╔═══════════╗{/}
{2}║{/} Content   {2}║{/}
{2}╚═══════════╝{/}
```

### 3. Page Width

Stick to 40 columns for classic Teletext:

```
{2}║{/}  Text must fit within 40 chars    {2}║{/}
     12345678901234567890123456789012345678
```

### 4. Color Usage

- **Borders**: Green ({2}) or blue ({4})
- **Headers**: Yellow ({3})
- **Body Text**: White ({7})
- **Highlights**: Cyan ({6})
- **Errors**: Red ({1})

### 5. Testing

Always test in terminal:

```bash
cat memory/drafts/teletext/page.ans
```

---

## Multi-Page Navigation

### Page Numbers

```
{6}Page 1 of 3{/}  {3}[▶ Next]{/}
```

### Navigation Arrows

```
{3}[◀ Prev]{/}  {6}Page 2 of 3{/}  {3}[Next ▶]{/}
```

### Menu-Based

```
{3}M{/}ain  {3}I{/}ndex  {3}P{/}rev  {3}N{/}ext
```

---

## Mosaic Graphics

### Block Patterns

```
{2}▀▀▀▀▀▀{/}
{2}▓▓▓▓▓▓{/}
{2}██████{/}
{2}▒▒▒▒▒▒{/}
{2}░░░░░░{/}
```

### Progress Bars

```
{2}Progress: ████████░░░░░░░░{/} {3}50%{/}
```

### Decorative Elements

```
{3}▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀{/}
{7}      Title Text       {/}
{3}▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄{/}
```

---

## Sizing Guidelines

### Limits

- **Maximum**: 10KB per page (~200 lines)
- **Recommended**: 25 lines (classic Teletext height)
- **Width**: 40 columns (classic) or 80 (extended)

### Example Sizes

- Simple menu: ~15 lines (500 bytes)
- Status screen: ~25 lines (1KB)
- Information page: ~30 lines (1.5KB)

---

## Common Patterns

### Header

```
{2}╔═══════════════════════════════════════╗{/}
{2}║{/}  {3}TITLE TEXT{/}                        {2}║{/}
{2}╠═══════════════════════════════════════╣{/}
```

### Footer

```
{2}╠═══════════════════════════════════════╣{/}
{2}║{/}  {6}Page 1 of 3{/}  {3}[▶ Next]{/}          {2}║{/}
{2}╚═══════════════════════════════════════╝{/}
```

### List Item

```
{2}║{/}  {6}▶{/} {7}Item text{/}                   {2}║{/}
```

### Table Row

```
{2}║{/} {7}Name{/}      {7}Value{/}    {7}Status{/}     {2}║{/}
```

---

## Accessibility

### Screen Reader Support

Teletext relies on ANSI color codes which may not work well with screen readers. Consider:

1. Provide plain text alternatives
2. Use descriptive labels
3. Test with screen readers

### Color Blindness

Avoid relying solely on color:

```
{1}❌ Error{/}     (icon + color)
{2}✓ Success{/}   (icon + color)
```

---

## Troubleshooting

### Colors Not Showing

**Problem**: Text appears without color
**Solution**: 
1. Check terminal supports ANSI colors
2. Verify TERM environment variable:
   ```bash
   echo $TERM  # should be xterm-256color or similar
   ```

### Broken Box Characters

**Problem**: Box-drawing characters show incorrectly
**Solution**: Ensure UTF-8 encoding

### File Too Large

**Problem**: Exceeds 10KB limit
**Solution**:
1. Split into multiple pages
2. Remove unnecessary whitespace
3. Simplify borders

---

## Version Control

Save page versions:

```bash
# Archive old versions
mv page.ans memory/drafts/teletext/.archive/page_v1.ans

# Create variants
cp welcome.ans welcome_variant.ans
```

---

## Related Documentation

- [Graphics System](Graphics-System.md) - Overall architecture
- [ASCII Graphics Guide](ASCII-Graphics-Guide.md) - Monochrome alternative
- [Command Reference](Command-Reference.md) - MAKE command syntax

---

**See Also**: `MAKE --help teletext`, `MAKE --list teletext`
