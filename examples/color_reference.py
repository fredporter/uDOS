#!/usr/bin/env python3
"""
Polaroid Color Palette - Quick Reference
Generates a printable color reference card.
"""

# Color definitions
COLORS = {
    'red': '\033[38;5;196m',
    'green': '\033[38;5;46m',
    'yellow': '\033[38;5;226m',
    'blue': '\033[38;5;21m',
    'purple': '\033[38;5;201m',
    'cyan': '\033[38;5;51m',
    'white': '\033[38;5;15m',
    'black': '\033[38;5;16m',
    'reset': '\033[0m'
}

GRAYS = {
    'gray_0': '\033[38;5;232m',
    'gray_1': '\033[38;5;236m',
    'gray_2': '\033[38;5;240m',
    'gray_3': '\033[38;5;244m',
    'gray_4': '\033[38;5;248m',
    'gray_5': '\033[38;5;252m'
}

def color(text, color_name):
    """Apply color to text."""
    return f"{COLORS.get(color_name, COLORS['reset'])}{text}{COLORS['reset']}"

# Print reference card
print("=" * 60)
print(color("POLAROID COLOR PALETTE - QUICK REFERENCE", 'cyan'))
print("=" * 60)
print()

print(color("PRIMARY COLORS:", 'white'))
print("-" * 60)
print(f"{color('███', 'red')} RED    (196) #FF1744 - Errors, alerts, danger")
print(f"{color('███', 'green')} GREEN  (46)  #00E676 - Success, confirmations")
print(f"{color('███', 'yellow')} YELLOW (226) #FFEB3B - Warnings, highlights")
print(f"{color('███', 'blue')} BLUE   (21)  #2196F3 - Information, links")
print(f"{color('███', 'purple')} PURPLE (201) #E91E63 - Magic, special events")
print(f"{color('███', 'cyan')} CYAN   (51)  #00E5FF - Technology, data")
print()

print(color("MONOCHROME:", 'white'))
print("-" * 60)
print(f"{color('███', 'white')} WHITE  (15)  #FFFFFF - Default text")
print(f"{color('███', 'black')} BLACK  (16)  #000000 - Backgrounds")
print()

print(color("GRAYSCALE GRADIENT:", 'white'))
print("-" * 60)
gradient = ""
for gray in ['gray_0', 'gray_1', 'gray_2', 'gray_3', 'gray_4', 'gray_5']:
    gradient += f"{GRAYS[gray]}███{COLORS['reset']}"
print(gradient)
print("232     236     240     244     248     252")
print()

print(color("SHADING BLOCKS:", 'white'))
print("-" * 60)
print("Unicode: █ ▓ ▒ ░ (100%, 75%, 50%, 25%)")
print("ASCII:   # @ + . (fallback for limited terminals)")
print()

print(color("USAGE EXAMPLES:", 'cyan'))
print("-" * 60)
print(f"{color('✅ SUCCESS:', 'green')} File saved successfully")
print(f"{color('❌ ERROR:', 'red')} File not found")
print(f"{color('⚠️  WARNING:', 'yellow')} Disk space low")
print(f"{color('ℹ️  INFO:', 'blue')} 3 files found")
print(f"{color('🔮 MAGIC:', 'purple')} Spell cast: TELEPORT")
print(f"{color('💾 DATA:', 'cyan')} Loading database...")
print()

print(color("THEME: DUNGEON CRAWLER", 'purple'))
print("-" * 60)
print(f"{color('@', 'white')} Player  {color('E', 'red')} Enemy   {color('$', 'yellow')} Gold")
print(f"{color('*', 'purple')} Magic   {color('>', 'green')} Exit    {color('~', 'cyan')} Water")
print()

print("=" * 60)
print("Use: PALETTE command to see full visualization")
print("Use: REBOOT to test colors during startup")
print("=" * 60)
