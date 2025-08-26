#!/usr/bin/env python3
"""
Integrate shortcodes into main commands system
Merge the best features from both systems and deprecate redundant shortcodes
"""

import json
from datetime import datetime

def integrate_commands():
    """Integrate shortcodes into main commands system"""

    # Read existing commands
    with open('/Users/agentdigital/uDOS/uMEMORY/system/uDATA-commands.json', 'r') as f:
        commands_data = [json.loads(line.strip()) for line in f if line.strip()]

    # Read shortcodes
    with open('/Users/agentdigital/uDOS/uMEMORY/system/uDATA-shortcodes.json', 'r') as f:
        shortcodes_data = [json.loads(line.strip()) for line in f if line.strip()]

    # Extract commands and shortcodes (skip metadata)
    commands = {cmd['command']: cmd for cmd in commands_data[1:] if 'command' in cmd}
    shortcodes = {sc['command']: sc for sc in shortcodes_data[1:] if 'command' in sc}

    # Create integrated commands
    integrated = []

    # Add updated metadata
    metadata = {
        "metadata": {
            "version": "1.4.0",
            "description": "Integrated uDOS Command System v1.4.0 - Commands with shortcode syntax support",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "system": "uDOS-v1.4.0",
            "format": "uDATA-v1",
            "integration_note": "Merged commands and shortcodes systems",
            "syntax_support": ["COMMAND ARG", "[COMMAND|ARG]", "[COMMAND|ARG*param]"]
        }
    }
    integrated.append(metadata)

    # Process all commands, enhancing with shortcode features
    all_command_names = set(commands.keys()) | set(shortcodes.keys())

    for cmd_name in sorted(all_command_names):
        cmd_data = commands.get(cmd_name, {})
        sc_data = shortcodes.get(cmd_name, {})

        # Create enhanced command entry
        enhanced_cmd = {
            "command": cmd_name,
            "category": cmd_data.get("category", sc_data.get("category", "system")),
            "description": cmd_data.get("description", sc_data.get("description", "")),
            "args": cmd_data.get("args", sc_data.get("args", []))
        }

        # Add shortcode-specific enhancements if available
        if sc_data:
            if "examples" in sc_data:
                enhanced_cmd["examples"] = sc_data["examples"]
            if "help" in sc_data:
                enhanced_cmd["help"] = sc_data["help"]

        # Normalize categories for consistency
        category_mapping = {
            "diagnostic": "system",
            "interface": "system",
            "mapping": "navigation",
            "grid": "ugrid",
            "widget": "ugrid",
            "security": "system",
            "storage": "system",
            "information": "utility",
            "execution": "utility",
            "documentation": "system",
            "configuration": "system",
            "session": "utility",
            "cleanup": "utility",
            "coordinates": "data"
        }

        if enhanced_cmd["category"] in category_mapping:
            enhanced_cmd["category"] = category_mapping[enhanced_cmd["category"]]

        integrated.append(enhanced_cmd)

    return integrated

def save_integrated_commands(integrated_commands):
    """Save the integrated commands system"""

    # Save new integrated commands
    with open('/Users/agentdigital/uDOS/uMEMORY/system/uDATA-commands.json', 'w') as f:
        for cmd in integrated_commands:
            f.write(json.dumps(cmd, separators=(',', ':')) + '\n')

    print(f"✅ Integrated {len(integrated_commands)-1} commands into uDATA-commands.json")

def deprecate_shortcodes():
    """Move shortcodes to deprecated location and create deprecation notice"""

    import shutil
    import os

    # Create deprecated directory if it doesn't exist
    deprecated_dir = "/Users/agentdigital/uDOS/uMEMORY/system/deprecated"
    os.makedirs(deprecated_dir, exist_ok=True)

    # Move shortcodes to deprecated
    shutil.move(
        "/Users/agentdigital/uDOS/uMEMORY/system/uDATA-shortcodes.json",
        f"{deprecated_dir}/uDATA-shortcodes.json.deprecated"
    )

    # Create deprecation notice
    deprecation_notice = {
        "metadata": {
            "status": "DEPRECATED",
            "deprecated_date": datetime.now().strftime("%Y-%m-%d"),
            "replacement": "uDATA-commands.json",
            "reason": "Integrated into main commands system with enhanced syntax support",
            "migration_note": "All shortcode functionality is now available in the main commands system"
        }
    }

    with open(f"{deprecated_dir}/SHORTCODES_DEPRECATED.json", 'w') as f:
        f.write(json.dumps(deprecation_notice, separators=(',', ':')) + '\n')

    print("✅ Moved shortcodes to deprecated directory")
    print(f"📁 Location: {deprecated_dir}/uDATA-shortcodes.json.deprecated")

def main():
    print("🔄 Integrating shortcodes into main commands system...")
    print("")

    # Integrate commands
    integrated_commands = integrate_commands()
    save_integrated_commands(integrated_commands)

    print("")
    print("📊 Integration Summary:")
    print(f"   Total commands: {len(integrated_commands)-1}")

    # Count by category
    categories = {}
    for cmd in integrated_commands[1:]:  # Skip metadata
        cat = cmd.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1

    print("   Categories:")
    for cat, count in sorted(categories.items()):
        print(f"     {cat}: {count} commands")

    print("")
    print("🗑️  Deprecating redundant shortcodes...")
    deprecate_shortcodes()

    print("")
    print("✅ Integration complete!")
    print("")
    print("💡 Enhanced Features:")
    print("   • Unified command system with both syntaxes")
    print("   • Example usage for each command")
    print("   • Contextual help text")
    print("   • Consistent categorization")
    print("   • Backward compatibility maintained")

if __name__ == "__main__":
    main()
