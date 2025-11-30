"""
Mission Command Handler
Handles all MISSION-related commands for project management.

Commands:
- MISSION CREATE <id> <title>
- MISSION START <id>
- MISSION PAUSE <id>
- MISSION RESUME <id>
- MISSION STATUS [id]
- MISSION PRIORITY <id> <priority>
- MISSION COMPLETE <id>
- MISSION LIST [--status=active] [--priority=high]
- MISSION CLONE <source_id> <new_id>
"""

import shlex
from typing import Optional
from core.services.mission_manager import get_mission_manager, MissionPriority


def handle_mission_command(command_line: str) -> str:
    """
    Handle MISSION commands.

    Args:
        command_line: Full command line (e.g., "MISSION CREATE my-mission Writing Project")

    Returns:
        Command result message
    """
    parts = command_line.strip().split(maxsplit=2)

    if len(parts) < 2:
        return _show_mission_help()

    subcommand = parts[1].upper()
    args = parts[2] if len(parts) > 2 else ""

    handlers = {
        'CREATE': _handle_create,
        'START': _handle_start,
        'PAUSE': _handle_pause,
        'RESUME': _handle_resume,
        'STATUS': _handle_status,
        'PRIORITY': _handle_priority,
        'COMPLETE': _handle_complete,
        'LIST': _handle_list,
        'CLONE': _handle_clone,
        'TEMPLATES': _handle_templates,
        'TEMPLATE': _handle_template,
        'HELP': lambda x: _show_mission_help()
    }

    handler = handlers.get(subcommand)
    if not handler:
        return f"❌ Unknown MISSION subcommand: {subcommand}\n{_show_mission_help()}"

    try:
        return handler(args)
    except Exception as e:
        return f"❌ Error: {str(e)}"


def _handle_create(args: str) -> str:
    """Handle MISSION CREATE command."""
    parts = args.split()

    if not parts:
        return "❌ Usage: MISSION CREATE <id> <title> [--priority=medium] [--desc=\"description\"]\n   Or: MISSION CREATE --template <template-id> --id <mission-id> --vars \"KEY=value,KEY2=value\""

    # Check for template-based creation
    if '--template' in args:
        return _handle_create_from_template(args)

    # Regular mission creation
    if len(parts) < 2:
        return "❌ Usage: MISSION CREATE <id> <title> [--priority=medium] [--desc=\"description\"]"

    mission_id = parts[0]
    remaining = ' '.join(parts[1:])

    # Parse options
    priority = "medium"
    description = ""
    title = remaining

    # Extract options
    if "--priority=" in remaining:
        idx = remaining.index("--priority=")
        priority_part = remaining[idx+11:].split()[0]
        priority = priority_part
        remaining = remaining.replace(f"--priority={priority_part}", "").strip()

    if "--desc=" in remaining:
        idx = remaining.index("--desc=")
        # Find quoted description
        if '"' in remaining[idx:]:
            start = remaining.index('"', idx)
            end = remaining.index('"', start + 1)
            description = remaining[start+1:end]
            remaining = remaining[:idx] + remaining[end+1:]
        remaining = remaining.strip()

    title = remaining.strip()

    if not title:
        return "❌ Mission title is required"

    mgr = get_mission_manager()
    mission = mgr.create_mission(mission_id, title, description, priority)

    priority_icon = {"high": "⚡", "medium": "📊", "low": "🔧"}.get(priority, "📊")

    result = [
        f"✅ Mission created: {mission.title}",
        f"   ID: {mission.id}",
        f"   Priority: {priority_icon} {priority.upper()}",
        f"   Workspace: {mission.workspace_path}",
        "",
        "Next steps:",
        "  1. Add moves: Use mission templates or add manually",
        "  2. Start mission: MISSION START " + mission.id
    ]

    return "\n".join(result)


def _handle_create_from_template(args: str) -> str:
    """Handle template-based mission creation."""
    # Parse arguments using shlex to properly handle quoted strings
    try:
        parts = shlex.split(args)
    except ValueError as e:
        return f"❌ Error parsing command: {e}"

    template_id = None
    mission_id = None
    variables = {}
    custom_title = None
    custom_desc = None

    i = 0
    while i < len(parts):
        if parts[i] == '--template' and i + 1 < len(parts):
            template_id = parts[i + 1]
            i += 2
        elif parts[i] == '--id' and i + 1 < len(parts):
            mission_id = parts[i + 1]
            i += 2
        elif parts[i] == '--vars' and i + 1 < len(parts):
            # Variables are now properly extracted as a single string by shlex
            vars_str = parts[i + 1]

            # Parse each variable assignment
            for var_pair in vars_str.split(','):
                if '=' in var_pair:
                    key, val = var_pair.split('=', 1)
                    key = key.strip()
                    val = val.strip()

                    # Type conversion
                    if val.lower() == 'true':
                        variables[key] = True
                    elif val.lower() == 'false':
                        variables[key] = False
                    elif val.isdigit():
                        variables[key] = int(val)
                    else:
                        try:
                            variables[key] = float(val)
                        except ValueError:
                            variables[key] = val
            i += 2
        elif parts[i] == '--title' and i + 1 < len(parts):
            # Custom title (overrides template)
            custom_title = parts[i + 1]
            i += 2
        elif parts[i] == '--desc' and i + 1 < len(parts):
            # Custom description
            custom_desc = parts[i + 1]
            i += 2
        else:
            i += 1    # Validate required parameters
    if not template_id:
        return "❌ --template parameter is required\n\nUsage: MISSION CREATE --template <template-id> --id <mission-id> --vars \"KEY=value\""

    if not mission_id:
        return "❌ --id parameter is required\n\nUsage: MISSION CREATE --template <template-id> --id <mission-id> --vars \"KEY=value\""

    mgr = get_mission_manager()

    # Validate template exists
    template = mgr.get_template(template_id)
    if not template:
        return f"❌ Template not found: {template_id}\n\nUse MISSION TEMPLATES to list available templates"

    # Validate variables
    errors = mgr.validate_template_variables(template_id, variables)
    if errors:
        result = [f"❌ Variable validation failed:", ""]
        for error in errors:
            result.append(f"   • {error}")
        result.append("")
        result.append(f"💡 Use MISSION TEMPLATE {template_id} to see required variables")
        return "\n".join(result)

    # Create mission from template
    try:
        mission = mgr.create_mission_from_template(
            template_id=template_id,
            mission_id=mission_id,
            variables=variables,
            custom_title=custom_title,
            custom_description=custom_desc
        )

        priority_icon = {"high": "⚡", "medium": "📊", "low": "🔧"}.get(mission.priority, "📊")

        result = [
            f"✅ Mission created from template: {template['name']}",
            f"   ID: {mission.id}",
            f"   Title: {mission.title}",
            f"   Priority: {priority_icon} {mission.priority.upper()}",
            f"   Workspace: {mission.workspace_path}",
            "",
            f"📊 Structure:",
            f"   Moves: {len(mission.moves)}",
            f"   Total Steps: {mission.total_steps()}",
            "",
            "Next steps:",
            f"  1. Start mission: MISSION START {mission.id}",
            f"  2. Check status: MISSION STATUS {mission.id}"
        ]

        return "\n".join(result)

    except Exception as e:
        return f"❌ Error creating mission from template: {str(e)}"


def _handle_start(args: str) -> str:
    """Handle MISSION START command."""
    if not args:
        return "❌ Usage: MISSION START <id>"

    mission_id = args.strip()
    mgr = get_mission_manager()
    mission = mgr.start_mission(mission_id)

    return f"✅ Mission started: {mission.title}\n   Status: ACTIVE"


def _handle_pause(args: str) -> str:
    """Handle MISSION PAUSE command."""
    if not args:
        return "❌ Usage: MISSION PAUSE <id>"

    mission_id = args.strip()
    mgr = get_mission_manager()
    mission = mgr.pause_mission(mission_id)

    return f"⏸️  Mission paused: {mission.title}\n   Status: PAUSED"


def _handle_resume(args: str) -> str:
    """Handle MISSION RESUME command."""
    if not args:
        return "❌ Usage: MISSION RESUME <id>"

    mission_id = args.strip()
    mgr = get_mission_manager()
    mission = mgr.resume_mission(mission_id)

    return f"▶️  Mission resumed: {mission.title}\n   Status: ACTIVE"


def _handle_status(args: str) -> str:
    """Handle MISSION STATUS command."""
    mgr = get_mission_manager()

    if not args:
        # Show status of all active missions
        active_missions = mgr.list_missions(status="active")
        if not active_missions:
            return "No active missions"

        results = ["📊 Active Missions:", ""]
        for mission in active_missions:
            summary = mgr.get_status_summary(mission.id)
            priority_icon = {"high": "⚡", "medium": "📊", "low": "🔧"}.get(mission.priority, "📊")
            results.append(f"{priority_icon} {mission.title} ({mission.id})")
            results.append(f"   Progress: {summary['progress']} ({summary['steps']['completed']}/{summary['steps']['total']} steps)")
            if summary['current_move']:
                results.append(f"   Current: {summary['current_move']}")
            results.append("")

        return "\n".join(results)

    # Show detailed status for specific mission
    mission_id = args.strip()
    summary = mgr.get_status_summary(mission_id)
    mission = mgr.get_mission(mission_id)

    if not mission:
        return f"❌ Mission not found: {mission_id}"

    priority_icon = {"high": "⚡", "medium": "📊", "low": "🔧"}.get(mission.priority, "📊")
    status_icon = {
        "not_started": "⚪",
        "active": "🟢",
        "paused": "🟡",
        "completed": "✅",
        "archived": "📦"
    }.get(mission.status, "⚪")

    result = [
        f"📋 Mission: {mission.title}",
        f"   ID: {mission.id}",
        f"   Status: {status_icon} {mission.status.upper()}",
        f"   Priority: {priority_icon} {mission.priority.upper()}",
        f"   Progress: {summary['progress']}",
        "",
        f"📊 Stats:",
        f"   Steps: {summary['steps']['completed']}/{summary['steps']['total']} completed",
        f"   Moves: {summary['moves']['completed']}/{summary['moves']['total']} completed",
        ""
    ]

    if summary['current_move']:
        result.append(f"🎯 Current Move: {summary['current_move']}")
        result.append("")

    # Show all moves with progress
    if mission.moves:
        result.append("📝 Moves:")
        for i, move in enumerate(mission.moves, 1):
            completed = move.completed_steps()
            total = move.total_steps()
            percent = move.progress_percentage()
            status_emoji = "✅" if move.is_complete() else "🔄"
            result.append(f"   {status_emoji} {i}. {move.title} - {percent:.0f}% ({completed}/{total} steps)")
        result.append("")

    if mission.started_at:
        result.append(f"Started: {mission.started_at}")
    if mission.completed_at:
        result.append(f"Completed: {mission.completed_at}")

    return "\n".join(result)


def _handle_priority(args: str) -> str:
    """Handle MISSION PRIORITY command."""
    parts = args.strip().split(maxsplit=1)

    if len(parts) < 2:
        return "❌ Usage: MISSION PRIORITY <id> <high|medium|low>"

    mission_id = parts[0]
    priority = parts[1].lower()

    if priority not in ['high', 'medium', 'low']:
        return "❌ Priority must be: high, medium, or low"

    mgr = get_mission_manager()
    mission = mgr.set_priority(mission_id, priority)

    priority_icon = {"high": "⚡", "medium": "📊", "low": "🔧"}.get(priority, "📊")

    return f"✅ Mission priority updated: {mission.title}\n   {priority_icon} {priority.upper()}"


def _handle_complete(args: str) -> str:
    """Handle MISSION COMPLETE command."""
    if not args:
        return "❌ Usage: MISSION COMPLETE <id>"

    mission_id = args.strip()
    mgr = get_mission_manager()
    mission = mgr.complete_mission(mission_id)

    summary = mgr.get_status_summary(mission_id)

    result = [
        f"🎉 Mission completed: {mission.title}",
        "",
        f"📊 Final Stats:",
        f"   Steps completed: {summary['steps']['completed']}/{summary['steps']['total']}",
        f"   Moves completed: {summary['moves']['completed']}/{summary['moves']['total']}",
        f"   Started: {summary['started_at']}",
        f"   Completed: {summary['completed_at']}",
        "",
        "✨ Great work! Mission archived."
    ]

    return "\n".join(result)


def _handle_list(args: str) -> str:
    """Handle MISSION LIST command."""
    mgr = get_mission_manager()

    # Parse filters
    status_filter = None
    priority_filter = None

    if args:
        for arg in args.split():
            if arg.startswith("--status="):
                status_filter = arg.split("=")[1]
            elif arg.startswith("--priority="):
                priority_filter = arg.split("=")[1]

    missions = mgr.list_missions(status=status_filter, priority=priority_filter)

    if not missions:
        filters = []
        if status_filter:
            filters.append(f"status={status_filter}")
        if priority_filter:
            filters.append(f"priority={priority_filter}")
        filter_text = f" ({', '.join(filters)})" if filters else ""
        return f"No missions found{filter_text}"

    # Group by status
    grouped = {}
    for mission in missions:
        if mission.status not in grouped:
            grouped[mission.status] = []
        grouped[mission.status].append(mission)

    result = [f"📋 Missions ({len(missions)} total):", ""]

    status_order = ['active', 'paused', 'not_started', 'completed']
    for status in status_order:
        if status not in grouped:
            continue

        status_icon = {
            "not_started": "⚪",
            "active": "🟢",
            "paused": "🟡",
            "completed": "✅"
        }.get(status, "⚪")

        result.append(f"{status_icon} {status.upper().replace('_', ' ')}:")

        for mission in grouped[status]:
            priority_icon = {"high": "⚡", "medium": "📊", "low": "🔧"}.get(mission.priority, "📊")
            progress = mission.progress_percentage()
            result.append(f"   {priority_icon} {mission.title} ({mission.id}) - {progress:.0f}%")

        result.append("")

    return "\n".join(result)


def _handle_clone(args: str) -> str:
    """Handle MISSION CLONE command."""
    parts = args.strip().split(maxsplit=1)

    if len(parts) < 2:
        return "❌ Usage: MISSION CLONE <source_id> <new_id>"

    source_id = parts[0]
    new_id = parts[1]

    mgr = get_mission_manager()
    new_mission = mgr.clone_mission(source_id, new_id)

    return f"✅ Mission cloned: {new_mission.title}\n   New ID: {new_mission.id}\n   Workspace: {new_mission.workspace_path}"


def _handle_templates(args: str) -> str:
    """Handle MISSION TEMPLATES command - list available templates."""
    mgr = get_mission_manager()

    # Parse category filter
    category = None
    if args:
        parts = args.strip().split()
        if len(parts) > 0 and not parts[0].startswith('--'):
            category = parts[0]

    templates = mgr.list_templates(category=category)

    if not templates:
        msg = "No templates found"
        if category:
            msg += f" in category: {category}"
        return msg

    # Group by category
    by_category = {}
    for template in templates:
        cat = template.get('category', 'custom')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(template)

    result = ["📚 Mission Templates:", ""]

    category_icons = {
        'creative-writing': '✍️',
        'research-learning': '🔬',
        'personal-development': '🌱',
        'knowledge-creation': '📖',
        'custom': '⚙️'
    }

    for cat in sorted(by_category.keys()):
        icon = category_icons.get(cat, '📋')
        result.append(f"{icon} {cat.upper().replace('-', ' ')}")
        result.append("   " + "─" * 50)

        for template in by_category[cat]:
            template_id = template['id']
            name = template['name']
            desc = template.get('description', '')[:60]
            if len(template.get('description', '')) > 60:
                desc += '...'

            result.append(f"   • {name} ({template_id})")
            result.append(f"     {desc}")

        result.append("")

    result.append("💡 Usage:")
    result.append("   MISSION TEMPLATE <id>           - Preview template")
    result.append("   MISSION CREATE --template <id>  - Create from template")

    return "\n".join(result)


def _handle_template(args: str) -> str:
    """Handle MISSION TEMPLATE <id> command - preview template details."""
    if not args:
        return "❌ Usage: MISSION TEMPLATE <id>"

    parts = args.strip().split()
    template_id = parts[0]

    mgr = get_mission_manager()

    # Check if template exists
    template = mgr.get_template(template_id)
    if not template:
        return f"❌ Template not found: {template_id}\n\nUse MISSION TEMPLATES to list available templates"

    # Get preview with sample variables if provided
    variables = {}
    for part in parts[1:]:
        if '=' in part:
            key, val = part.split('=', 1)
            variables[key] = val

    preview = mgr.preview_template(template_id, variables if variables else None)

    # Build output
    result = [
        f"📋 Template: {preview['name']}",
        f"   ID: {preview['id']}",
        f"   Category: {preview['category']}",
        f"   Version: {preview['version']}",
        ""
    ]

    if preview.get('description'):
        result.append(f"📝 {preview['description']}")
        result.append("")

    # Show structure
    result.append(f"📊 Structure:")
    result.append(f"   Moves: {preview['moves_count']}")
    result.append(f"   Total Steps: {preview['total_steps']}")

    if preview.get('priority'):
        priority_icon = {"HIGH": "⚡", "MEDIUM": "📊", "LOW": "🔧"}.get(preview['priority'], "📊")
        result.append(f"   Priority: {priority_icon} {preview['priority']}")

    if preview.get('estimated_duration'):
        result.append(f"   Duration: {preview['estimated_duration']}")

    result.append("")

    # Show variables
    if 'variables' in template:
        result.append("🔧 Variables:")
        for var_name, var_def in template['variables'].items():
            required = "✓" if var_def.get('required', False) else " "
            var_type = var_def.get('type', 'string')
            desc = var_def.get('description', '')
            default = var_def.get('default')

            result.append(f"   [{required}] {var_name} ({var_type})")
            result.append(f"       {desc}")

            if default is not None:
                result.append(f"       Default: {default}")

            if var_type == 'choice' and 'choices' in var_def:
                choices = ', '.join(str(c) for c in var_def['choices'][:5])
                if len(var_def['choices']) > 5:
                    choices += '...'
                result.append(f"       Choices: {choices}")

        result.append("")

    # Show sample title/move if variables were provided
    if variables and 'sample_title' in preview:
        result.append("📌 Preview with your variables:")
        result.append(f"   Title: {preview['sample_title']}")
        if 'sample_move' in preview:
            result.append(f"   First Move: {preview['sample_move']}")
        result.append("")

    # Show examples
    if template.get('examples'):
        result.append("💡 Examples:")
        for i, example in enumerate(template['examples'][:2], 1):
            result.append(f"   {i}. {example.get('title', f'Example {i}')}")
            if example.get('variables'):
                for key, val in list(example['variables'].items())[:3]:
                    result.append(f"      {key}={val}")
        result.append("")

    # Show help text
    if template.get('help'):
        result.append("ℹ️  Tips:")
        help_lines = template['help'].split('\n')[:3]
        for line in help_lines:
            if line.strip():
                result.append(f"   {line.strip()}")
        result.append("")

    # Usage instructions
    result.append("💡 Usage:")
    result.append(f"   MISSION CREATE --template {template_id} --id <mission-id> \\")

    # Show required variables
    required_vars = [k for k, v in template.get('variables', {}).items() if v.get('required', False)]
    if required_vars:
        result.append(f"      --vars \"{required_vars[0]}=value\"")
    else:
        result.append(f"      --vars \"VAR=value\"")

    return "\n".join(result)


def _show_mission_help() -> str:
    """Show mission command help."""
    return """📋 MISSION Commands:

MISSION CREATE <id> <title> [options]
   Create new mission
   Options:
     --priority=<high|medium|low>  Set priority (default: medium)
     --desc="description"          Set description

MISSION CREATE --template <template-id> --id <mission-id> --vars "KEY=value,..."
   Create mission from template
   Options:
     --title "Custom Title"        Override template title
     --desc "Custom Description"   Override template description

MISSION TEMPLATES [category]
   List available mission templates
   Categories: creative-writing, research-learning, personal-development, knowledge-creation

MISSION TEMPLATE <id>
   Preview template details and variables

MISSION START <id>
   Start a mission (changes status to ACTIVE)

MISSION PAUSE <id>
   Pause an active mission

MISSION RESUME <id>
   Resume a paused mission

MISSION STATUS [id]
   Show mission status
   If no ID provided, shows all active missions

MISSION PRIORITY <id> <high|medium|low>
   Change mission priority

MISSION COMPLETE <id>
   Mark mission as completed

MISSION LIST [--status=active] [--priority=high]
   List all missions with optional filters

MISSION CLONE <source_id> <new_id>
   Clone an existing mission with new ID

Examples:
  MISSION CREATE my-novel "Write Science Fiction Novel" --priority=high
  MISSION TEMPLATES creative-writing
  MISSION TEMPLATE novel
  MISSION CREATE --template novel --id my-novel --vars "NOVEL_TITLE=The Nexus,AUTHOR_NAME=Jane Doe,GENRE=Sci-Fi"
  MISSION START my-novel
  MISSION STATUS my-novel
"""
