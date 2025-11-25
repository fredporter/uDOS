#!/usr/bin/env python3
"""
Test help template loading and display
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, '/Users/fredbook/Code/uDOS')

def load_template(template_file):
    """Load a help template file."""
    path = Path(f"data/system/help_templates/{template_file}")
    if not path.exists():
        print(f"❌ Template not found: {template_file}")
        return None

    with open(path, 'r') as f:
        return json.load(f)

def display_command_help(command_data):
    """Display formatted help for a command."""
    print(f"\n{'='*70}")
    print(f"COMMAND: {command_data['name']}")
    print(f"{'='*70}")

    print(f"\n📝 Description:")
    print(f"  {command_data['description']}")

    if command_data.get('detailed'):
        print(f"\n📖 Details:")
        print(f"  {command_data['detailed']}")

    print(f"\n⚙️  Syntax:")
    for syntax in command_data['syntax']:
        print(f"  • {syntax}")

    if command_data.get('parameters'):
        print(f"\n📋 Parameters:")
        for param in command_data['parameters']:
            optional = " (optional)" if param.get('optional') else " (required)"
            print(f"  • {param['name']:<15} [{param['type']}]{optional}")
            print(f"    {param['description']}")

    if command_data.get('examples'):
        print(f"\n💡 Examples:")
        for ex in command_data['examples']:
            print(f"  $ {ex['command']}")
            print(f"    → {ex['description']}")

    if command_data.get('related'):
        print(f"\n🔗 Related Commands:")
        print(f"  {', '.join(command_data['related'])}")

    if command_data.get('notes'):
        print(f"\n📌 Notes:")
        for note in command_data['notes']:
            print(f"  • {note}")

    version_info = f"Added in v{command_data.get('version_added', 'unknown')}"
    if command_data.get('version_enhanced'):
        version_info += f", enhanced in v{command_data['version_enhanced']}"
    print(f"\n🏷️  Version: {version_info}")

def main():
    """Test help template system."""
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "Help Templates Test" + " "*29 + "║")
    print("╚" + "="*68 + "╝")

    # Load index
    print("\n📂 Loading template index...")
    index = load_template("_index.json")
    if not index:
        return

    print(f"✅ Found {len(index['templates'])} template categories")

    # Test each template
    for template_info in index['templates']:
        print(f"\n{'─'*70}")
        print(f"📁 Category: {template_info['category']}")
        print(f"📄 File: {template_info['file']}")
        print(f"📝 {template_info['description']}")
        print(f"🔤 Commands: {', '.join(template_info['commands'])}")

        # Load the template
        template_data = load_template(template_info['file'])
        if template_data:
            print(f"✅ Template loaded successfully")

            # Display first command from each category
            first_cmd = template_info['commands'][0]
            if first_cmd in template_data['commands']:
                display_command_help(template_data['commands'][first_cmd])

    print(f"\n{'='*70}")
    print("✅ All templates loaded and displayed successfully!")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
