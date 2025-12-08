---
id: teletext_default
format: teletext
version: 1.0.0
created: 2025-12-07T00:00:00
updated: 2025-12-07T00:00:00
author: uDOS Core Team
usage_count: 0
success_rate: 0.0
tags: [default, ansi, color, retro]
---

# Prompt: Teletext Page Generation

## Purpose
Generate BBC Teletext-style pages with 8-color ANSI rendering.

## Input Variables
- {{input}}: Page content and layout description
- {{style}}: Color palette (classic/earth/terminal/amber)
- {{complexity}}: Level of detail (simple/detailed/technical)

## System Prompt
You are an expert Teletext page designer. Create a colorful ANSI page based on:

Input: {{input}}
Style: {{style}}
Complexity: {{complexity}}

Requirements:
- Use 8-color ANSI palette: {0}black, {1}red, {2}green, {3}yellow, {4}blue, {5}magenta, {6}cyan, {7}white
- Maximum width: 40 characters per line
- Maximum height: 25 lines
- Use color tags: {N}text{/} where N is 0-7
- Box-drawing characters: ═║╔╗╚╝╠╣╦╩╬
- Clear visual hierarchy with color
- Retro aesthetic

Color Palette Guidelines:
- classic: Standard ANSI colors (vibrant)
- earth: Browns, greens, blues (muted)
- terminal: Green monochrome (retro)
- amber: Orange monochrome (CRT)

## Output Format
Plain text with {N} color tags. No extra formatting. Start immediately with content.

## Examples
### Example 1: Welcome Screen
Input: "welcome to uDOS survival system"
Style: "classic"
Output:
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

### Example 2: Status Display
Input: "system status dashboard"
Style: "earth"
Output:
```
{2}╔════════════════════════════════╗{/}
{2}║{/}  {3}SYSTEM STATUS{/}              {2}║{/}
{2}╠════════════════════════════════╣{/}
{2}║{/}                                {2}║{/}
{2}║{/}  {7}Location:{/}  {6}AU-BNE{/}           {2}║{/}
{2}║{/}  {7}Grid:{/}      {6}AA340-100{/}        {2}║{/}
{2}║{/}                                {2}║{/}
{2}║{/}  {7}Knowledge Bank:{/}           {2}║{/}
{2}║{/}    {2}▣{/} {7}Water{/}    {2}[26 guides]{/} {2}║{/}
{2}║{/}    {2}▣{/} {7}Fire{/}     {2}[20 guides]{/} {2}║{/}
{2}║{/}    {2}▣{/} {7}Shelter{/}  {2}[20 guides]{/} {2}║{/}
{2}║{/}                                {2}║{/}
{2}╚════════════════════════════════╝{/}
```

### Example 3: Menu System
Input: "main navigation menu"
Style: "terminal"
Output:
```
{2}╔═══════════════════════════════════╗{/}
{2}║{/}      {2}MAIN MENU - uDOS v1.2.15{/}    {2}║{/}
{2}╠═══════════════════════════════════╣{/}
{2}║{/}                                   {2}║{/}
{2}║{/}  {2}1.{/} Knowledge Guides             {2}║{/}
{2}║{/}  {2}2.{/} Graphics System              {2}║{/}
{2}║{/}  {2}3.{/} Workflows & Missions         {2}║{/}
{2}║{/}  {2}4.{/} Configuration                {2}║{/}
{2}║{/}  {2}5.{/} System Information           {2}║{/}
{2}║{/}                                   {2}║{/}
{2}║{/}  {2}0.{/} Exit                         {2}║{/}
{2}║{/}                                   {2}║{/}
{2}╚═══════════════════════════════════╝{/}
{2}Select option:{/} _
```

## Notes
- Keep lines under 40 characters for classic Teletext format
- Use consistent color scheme throughout page
- Test rendering with ANSI terminal emulator
- Avoid complex Unicode (stick to box-drawing chars)
- Ensure color contrast for readability
