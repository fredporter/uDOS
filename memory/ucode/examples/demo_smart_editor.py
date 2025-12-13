"""
uCODE Smart Text Editor Demo
=============================

Date: 20251213-173000UTC (Updated for v1.2.24 syntax)
Purpose: Demonstrate three display modes with real uDOS script

This shows how the same Python code can be viewed in:
1. Pythonic mode (standard Python)
2. Symbolic mode (uCODE visual syntax)
3. Typo mode (beautiful typography)

Note: v1.2.24 uses lowercase function names in Python context:
- print_output() not PRINT()
- checkpoint_save() not CHECKPOINT_SAVE()
- guide_load() not GUIDE()
"""

import sys
sys.path.append('/Users/fredbook/Code/uDOS')

from core.ui.ucode_editor import UCODEEditor

# Example Python uDOS script (v1.2.24 correct syntax)
python_script = """
# Water Purification Mission
from core.udos_core import print_output, guide_load, get_var, set_var, checkpoint_save

# Setup camp
print_output("Starting water purification mission...")
set_var("camp_location", "AA340")
set_var("water_supply", 0)

# Note: In Python-First v1.2.24, uCODE functions use lowercase
# CLONE*DEV and BUILD*FULL would be custom commands/extensions

# Track progress
player_hp = 100
player_xp = 0

# Purification process
for step in range(3):
    print_output(f"Purification step {step + 1}/3")
    current = get_var("water_supply")
    set_var("water_supply", current + 5)
    player_xp += 10

# Check guide
guide_load("water/boiling", "detailed")

# Save checkpoint (correct: asterisk not underscore)
checkpoint_save("water_mission_complete")
"""

def demo_all_modes():
    """Demonstrate all three display modes"""
    
    print("=" * 70)
    print("uCODE Smart Text Editor - Complete Demo")
    print("=" * 70)
    print()
    
    editor = UCODEEditor()
    
    # Mode 1: Pythonic (how you write it)
    print("📝 MODE 1: PYTHONIC (Standard Python)")
    print("-" * 70)
    editor.set_mode('pythonic')
    pythonic = editor.render(python_script)
    print(pythonic)
    print()
    
    # Mode 2: Symbolic (uCODE visual)
    print("🎨 MODE 2: SYMBOLIC (uCODE Visual Syntax)")
    print("-" * 70)
    editor.set_mode('symbolic')
    symbolic = editor.render(python_script)
    print(symbolic)
    print()
    
    # Mode 3: Typo (beautiful typography)
    print("✨ MODE 3: TYPO (Beautiful Typography)")
    print("-" * 70)
    editor.set_mode('typo')
    typo = editor.render(python_script)
    info = editor.get_info()
    
    if info['typo_available']:
        print(typo)
    else:
        print("⚠️  Typo extension not installed")
        print("Install: extensions/cloned/typo/")
        print("Falling back to symbolic mode:")
        print(symbolic)
    print()
    
    # Syntax highlighting demo
    print("🌈 SYNTAX HIGHLIGHTING DEMO")
    print("-" * 70)
    highlighted = editor.syntax_highlight(symbolic)
    print(highlighted)
    print()
    
    # Round-trip validation
    print("🔄 ROUND-TRIP VALIDATION")
    print("-" * 70)
    editor.set_mode('symbolic')
    ucode = editor.render(python_script)
    back_to_python = editor.parse(ucode)
    
    # Normalize whitespace for comparison
    original_lines = [l.strip() for l in python_script.strip().split('\n') if l.strip()]
    converted_lines = [l.strip() for l in back_to_python.strip().split('\n') if l.strip()]
    
    matches = len(original_lines) == len(converted_lines)
    for orig, conv in zip(original_lines, converted_lines):
        if orig != conv and not orig.startswith('#'):  # Skip comments
            print(f"❌ Mismatch:")
            print(f"   Original:  {orig}")
            print(f"   Converted: {conv}")
            matches = False
            break
    
    if matches:
        print("✅ Perfect round-trip: Python → uCODE → Python")
        print("   All code identical after conversion!")
    print()
    
    # Editor info
    print("ℹ️  EDITOR INFORMATION")
    print("-" * 70)
    info = editor.get_info()
    print(f"Current mode: {info['mode']}")
    print(f"Typo available: {info['typo_available']}")
    print(f"Typo active: {info['typo_active']}")
    print(f"Available modes: {', '.join(info['modes'])}")
    print()

def demo_interactive_switching():
    """Demonstrate interactive mode switching"""
    
    print("=" * 70)
    print("Interactive Mode Switching Demo")
    print("=" * 70)
    print()
    
    # Short code sample
    code = """
PRINT("Water level check")
water = get_var("water_supply")
if water < 10:
    CLONE--emergency
    heal_sprite(5)
"""
    
    editor = UCODEEditor()
    
    print("Original Python code:")
    print(code)
    print()
    
    for mode in ['pythonic', 'symbolic', 'typo']:
        editor.set_mode(mode)
        print(f"Displaying as: {mode.upper()}")
        print("-" * 70)
        rendered = editor.render(code)
        print(rendered)
        print()

if __name__ == '__main__':
    demo_all_modes()
    demo_interactive_switching()
    
    print("=" * 70)
    print("Smart Text Editor Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("• Write Python, display as uCODE or Typo")
    print("• Three modes: pythonic/symbolic/typo")
    print("• Lossless round-trip conversion")
    print("• Syntax highlighting with ANSI colors")
    print("• Optional Typo extension for beautiful typography")
    print()
    print("Next: Run './start_udos.sh' to use in production")
