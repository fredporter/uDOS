"""HELP command handler - Command reference and system help."""

from typing import Any, Dict, List
from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.commands.interactive_menu_mixin import InteractiveMenuMixin
from core.services.error_contract import CommandError
from core.commands.help_support import (
    format_command_help,
    format_search_results,
    format_syntax_help,
    search_commands,
    sync_with_registry,
)


class HelpHandler(BaseCommandHandler, HandlerLoggingMixin, InteractiveMenuMixin):
    """Handler for HELP command - display command reference."""

    def __init__(self):
        super().__init__()
        self._metadata_synced = False

    GHOST_TEST_COMMANDS = [
        "AI TEST mistral",
        "AI TEST claude",
        "AI TEST status",
        "TEST all",
        "TEST core",
    ]

    COMMAND_CATEGORIES = {
        "Navigation": ["MAP", "GRID", "ANCHOR", "PANEL", "GOTO", "FIND", "TELL", "PLAY", "RULE"],
        "Inventory": ["BAG", "GRAB", "SPAWN"],
        "NPCs & Dialogue": ["NPC", "SEND"],
        "Files & State": ["SAVE", "LOAD", "FILE", "UNDO"],
        "AI & Models": ["OK"],
        "System & Maintenance": [
            "REBOOT",
            "HEALTH",
            "VERIFY",
            "SONIC",
            "REPAIR",
            "BACKUP",
            "RESTORE",
            "TIDY",
            "CLEAN",
            "COMPOST",
            "DESTROY",
            "DEV",
            "LOGS",
            "VIEWPORT",
            "DRAW",
            "THEME",
            "SKIN",
            "LIBRARY",
        ],
        "Automation": [
            "SCHEDULER",
            "SCRIPT",
        ],
        "Advanced": [
            "BINDER",
            "PLACE",
            "RUN",
            "READ",
            "STORY",
            "SETUP",
            "CONFIG",
            "WIZARD",
            "TOKEN",
            "GHOST",
        ],
    }

    COMMANDS = {
        "MAP": {
            "description": "Display location tile grid",
            "usage": "MAP [location_id]",
            "example": "MAP L300-BJ10",
            "notes": "Shows 80x30 grid with tiles, objects, sprites",
            "category": "Navigation",
            "syntax": "MAP [--follow] [--zoom N] [location_id]",
        },
        "GRID": {
            "description": "Render UGRID canvas (calendar/table/schedule/map/dashboard/workflow)",
            "usage": "GRID <mode> [--input file.json] [--loc LOCID]",
            "example": "GRID MAP --loc EARTH:SUR:L305-DA11",
            "notes": "Uses 80x30 UGRID renderer with LocId overlays for map mode",
            "category": "Navigation",
            "syntax": "GRID <calendar|table|schedule|map|dashboard|workflow> [--input <json>] [--loc <locid>] [--title <text>] [--theme <name>]",
        },
        "ANCHOR": {
            "description": "List gameplay anchors or show anchor details",
            "usage": "ANCHOR [LIST] | ANCHOR SHOW <id> | ANCHOR REGISTER <id> <title>",
            "example": "ANCHOR REGISTER GAME:NETHACK NetHack",
            "notes": "Gameplay anchor registry + bindings + events",
            "category": "Navigation",
            "syntax": "ANCHOR [LIST] | ANCHOR SHOW <anchor_id> | ANCHOR REGISTER <anchor_id> <title> | ANCHOR INSTANCE CREATE <anchor_id> | ANCHOR BIND <locid> <anchor> <coord_kind> <coord_json>",
        },
        "PANEL": {
            "description": "Show location information panel",
            "usage": "PANEL [location_id]",
            "example": "PANEL",
            "notes": "Displays metadata, timezone, connections",
            "category": "Navigation",
            "syntax": "PANEL [--details] [location_id]",
        },
        "GOTO": {
            "description": "Navigate to connected location",
            "usage": "GOTO [direction|location_id]",
            "example": "GOTO north or GOTO L300-BK10",
            "notes": "Directions: north/south/east/west/up/down (or n/s/e/w/u/d)",
            "category": "Navigation",
            "syntax": "GOTO <north|south|east|west|up|down|location_id>",
        },
        "FIND": {
            "description": "Search for locations by name/type/region",
            "usage": "FIND [query] [--type TYPE] [--region REGION]",
            "example": "FIND tokyo or FIND --type major-city",
            "notes": "Search is case-insensitive",
            "category": "Navigation",
            "syntax": "FIND <query> [--type <type>] [--region <region>] [--limit N]",
        },
        "TELL": {
            "description": "Show rich location description",
            "usage": "TELL [location_id]",
            "example": "TELL",
            "notes": "Displays full description with connections",
            "category": "Navigation",
            "syntax": "TELL [--verbose] [location_id]",
        },
        "PLAY": {
            "description": "Unified gameplay command (stats/map/gates/TOYBOX + options/tokens).",
            "usage": "PLAY [STATUS|STATS|MAP|GATE|TOYBOX|LENS|PROCEED|OPTIONS|START <option>|TOKENS|CLAIM]",
            "example": "PLAY STATS ADD xp 25",
            "notes": "Unified gameplay surface for progression, map loop, gates, TOYBOX, and play options.",
            "category": "Navigation",
            "syntax": "PLAY STATUS | PLAY STATS <SET|ADD> <xp|hp|gold> <value> | PLAY MAP <STATUS|ENTER|MOVE|INSPECT|INTERACT|COMPLETE|TICK> ... | PLAY GATE <STATUS|COMPLETE|RESET> <gate_id> | PLAY TOYBOX <LIST|SET> [profile] | PLAY LENS <LIST|SHOW|SET|STATUS|ENABLE|DISABLE> [lens] | PLAY PROCEED | PLAY OPTIONS | PLAY START <dungeon|galaxy|social|ascension> | PLAY TOKENS | PLAY CLAIM",
        },
        "RULE": {
            "description": "Conditional IF/THEN gameplay automations paired with PLAY and TOYBOX",
            "usage": "RULE [LIST|SHOW|ADD|REMOVE|ENABLE|DISABLE|RUN|TEST]",
            "example": "RULE ADD rule.unlock IF xp>=100 and achievement_level>=1 THEN TOKEN token.rule.unlock; PLAY galaxy",
            "notes": "RULE works as gameplay automation and evaluates normalized progress/TOYBOX variables.",
            "category": "Navigation",
            "syntax": "RULE LIST | RULE SHOW <id> | RULE ADD <id> IF <condition> THEN <actions> | RULE RUN [id] | RULE TEST IF <condition>",
        },
        "BAG": {
            "description": "Manage character inventory",
            "usage": "BAG [action] [item] [quantity]",
            "example": "BAG list or BAG add sword 1",
            "notes": "Actions: list, add, remove, drop, equip",
            "category": "Inventory",
            "syntax": "BAG <list|add|remove|drop|equip> [item] [quantity]",
        },
        "GRAB": {
            "description": "Pick up objects at current location",
            "usage": "GRAB [object_name]",
            "example": "GRAB sword",
            "notes": "Adds objects to your inventory",
            "category": "Inventory",
            "syntax": "GRAB <object_name> [quantity]",
        },
        "SPAWN": {
            "description": "Create objects/sprites at locations",
            "usage": "SPAWN [type] [char] [name] at [location] [cell]",
            "example": "SPAWN object key at L300-BJ10 AA00",
            "notes": "Types: object, sprite",
            "category": "Inventory",
            "syntax": "SPAWN <object|sprite> <char> <name> at <location_id> <cell>",
        },
        "SAVE": {
            "description": "Save file (editor) or state slot",
            "usage": "SAVE [path] | SAVE --state [slot_name]",
            "example": "SAVE notes.md or SAVE --state mysave",
            "notes": "Use --state for game/state saves; otherwise opens editor path",
            "category": "Files & State",
            "syntax": "SAVE [path] | SAVE --state <slot_name>",
        },
        "LOAD": {
            "description": "Load file (editor) or state slot",
            "usage": "LOAD [path] | LOAD --state [slot_name]",
            "example": "LOAD notes.md or LOAD --state mysave",
            "notes": "Use --state for game/state loads; otherwise opens editor path",
            "category": "Files & State",
            "syntax": "LOAD [path] | LOAD --state <slot_name>",
        },
        "FILE": {
            "description": "Workspace-aware file browser and editor entry",
            "usage": "FILE [BROWSE|LIST|SHOW|NEW|EDIT] [path]",
            "example": "FILE NEW daily-notes or FILE EDIT notes.md",
            "notes": "FILE NEW/EDIT replace legacy NEW/EDIT commands",
            "category": "Files & State",
            "syntax": "FILE [BROWSE|LIST|SHOW|NEW|EDIT|HELP] [path]",
        },
        "HELP": {
            "description": "Display command reference",
            "usage": "HELP [command]",
            "example": "HELP GOTO or HELP",
            "notes": "Shows all commands or specific command details",
            "category": "System & Maintenance",
            "syntax": "HELP [<command>] | HELP CATEGORY <category> | HELP SEARCH <query>",
        },
        "OK": {
            "description": "Local Vibe helpers (offline-first)",
            "usage": "OK <LOCAL|EXPLAIN|DIFF|PATCH|ROUTE|VIBE|FALLBACK> [args]",
            "example": "OK ROUTE show scheduler logs",
            "notes": "Routes to local Vibe (Ollama-backed). ROUTE uses rule-based NL routing. FALLBACK toggles auto-switching to cloud on failure.",
            "category": "AI & Models",
            "syntax": "OK <LOCAL|EXPLAIN|DIFF|PATCH|ROUTE|VIBE|FALLBACK> [args] [--cloud]",
        },
        "VIEWPORT": {
            "description": "Measure and cache terminal viewport size",
            "usage": "VIEWPORT [SHOW|REFRESH]",
            "example": "VIEWPORT",
            "notes": "Persists UDOS_VIEWPORT_COLS/ROWS in .env for stable TUI sizing.",
            "category": "System & Maintenance",
            "syntax": "VIEWPORT [SHOW|REFRESH]",
        },
        "THEME": {
            "description": "TUI message theming (text-only)",
            "usage": "THEME [LIST|SHOW|SET|CLEAR] [name]",
            "example": "THEME SET dungeon",
            "notes": "Controls text-only TUI message replacements (errors, tips, labels).",
            "category": "System & Maintenance",
            "syntax": "THEME LIST | THEME SHOW <name> | THEME SET <name> | THEME CLEAR",
        },
        "SKIN": {
            "description": "Wizard GUI skin manager (HTML/CSS)",
            "usage": "SKIN [LIST|SHOW|SET|CLEAR] [name]",
            "example": "SKIN SET prose",
            "notes": "Selects Wizard GUI skin packs stored under /themes.",
            "category": "System & Maintenance",
            "syntax": "SKIN LIST | SKIN SHOW <name> | SKIN SET <name> | SKIN CLEAR",
        },
        "DRAW": {
            "description": "Render viewport-aware ASCII panels",
            "usage": "DRAW [DEMO|MAP|SCHEDULE|TIMELINE|PAT ...]",
            "example": "DRAW PAT LIST",
            "notes": "Shows viewport-sized panels and TS-backed pattern rendering via DRAW PAT.",
            "category": "System & Maintenance",
            "syntax": "DRAW [DEMO|MAP|SCHEDULE|TIMELINE|PAT <LIST|CYCLE|TEXT|name>]",
        },
        "SCHEDULER": {
            "description": "Manage scheduled tasks in the Wizard queue",
            "usage": "SCHEDULER <LIST|RUN|LOG> [id]",
            "example": "SCHEDULER LIST",
            "notes": "LIST shows tasks. RUN queues a task for immediate execution. LOG shows recent runs.",
            "category": "Automation",
            "syntax": "SCHEDULER LIST | SCHEDULER RUN <task_id> | SCHEDULER LOG [task_id|run_id]",
        },
        "SCRIPT": {
            "description": "Manage and execute system scripts",
            "usage": "SCRIPT <LIST|RUN|LOG> [name]",
            "example": "SCRIPT RUN startup-script",
            "notes": "Runs markdown scripts via the TS runtime. LOG reads recent script events.",
            "category": "Automation",
            "syntax": "SCRIPT LIST | SCRIPT RUN <name> | SCRIPT LOG [name]",
        },
        "HEALTH": {
            "description": "Offline/stdlib core health checks",
            "usage": "HEALTH | HEALTH CHECK release-gates [--format json]",
            "example": "HEALTH",
            "notes": "Checks local dirs/configs, reports banned network imports, and can emit release-gate mission-objective status.",
            "category": "System & Maintenance",
            "syntax": "HEALTH | HEALTH CHECK release-gates [--format text|json]",
        },
        "VERIFY": {
            "description": "TypeScript runtime verification checks",
            "usage": "VERIFY",
            "example": "VERIFY",
            "notes": "Verifies node/runtime artifacts and parse/execute smoke for TS runtime scripts.",
            "category": "System & Maintenance",
            "syntax": "VERIFY",
        },
        "SONIC": {
            "description": "Sonic Screwdriver status, dataset sync, and USB planning",
            "usage": "SONIC <STATUS|SYNC|PLAN|RUN|HELP>",
            "example": "SONIC SYNC --force",
            "notes": "SYNC rebuilds local device DB from sonic/datasets SQL. Wizard parity endpoints live under /api/sonic/db/*.",
            "category": "System & Maintenance",
            "syntax": "SONIC STATUS | SONIC SYNC [--force] | SONIC PLAN [flags] | SONIC RUN [flags] --confirm",
        },
        "LIBRARY": {
            "description": "Library integration manager — list, sync, and inspect integrations",
            "usage": "LIBRARY <STATUS|SYNC|INFO <name>|LIST|HELP>",
            "example": "LIBRARY STATUS",
            "notes": "SYNC rescans the /library directory. INFO shows detail for one integration.",
            "category": "System & Maintenance",
            "syntax": "LIBRARY STATUS | LIBRARY SYNC | LIBRARY INFO <name> | LIBRARY LIST",
        },
        "REBOOT": {
            "description": "Hot reload handlers and restart the TUI",
            "usage": "REBOOT",
            "example": "REBOOT",
            "notes": "Single-path reboot: hot reload + TUI restart",
            "category": "System & Maintenance",
            "syntax": "REBOOT",
        },
        "REPAIR": {
            "description": "Self-healing and system maintenance",
            "usage": "REPAIR [--pull|--install|--check]",
            "example": "REPAIR --pull",
            "notes": "Git sync, installer check, dependency verification",
            "category": "System & Maintenance",
            "syntax": "REPAIR [--pull] [--install] [--check] [--dry-run]",
        },
        "BACKUP": {
            "description": "Create a workspace snapshot in .compost/<date>/backups",
            "usage": "BACKUP [current|+subfolders|workspace|all] [label]",
            "example": "BACKUP workspace pre-clean",
            "notes": "Creates a tar.gz backup in global .compost/<date>/backups",
            "category": "System & Maintenance",
            "syntax": "BACKUP <current|+subfolders|workspace|all> [label] [--compress]",
        },
        "RESTORE": {
            "description": "Restore from the latest backup in .compost/<date>/backups",
            "usage": "RESTORE [current|+subfolders|workspace|all] [--force]",
            "example": "RESTORE workspace",
            "notes": "Restores the most recent backup (use --force to overwrite)",
            "category": "System & Maintenance",
            "syntax": "RESTORE <current|+subfolders|workspace|all> [--force] [--date YYYY-MM-DD]",
        },
        "UNDO": {
            "description": "Simple undo wrapper (restore from backup)",
            "usage": "UNDO [RESTORE] [scope] [--force]",
            "example": "UNDO RESTORE workspace",
            "notes": "Simple wrapper around RESTORE. Restores from latest backup",
            "category": "Files & State",
            "syntax": "UNDO [RESTORE|--help] [<current|+subfolders|workspace|all>] [--force]",
        },
        "TIDY": {
            "description": "Organize junk files into .compost/<date>/trash",
            "usage": "TIDY [current|+subfolders|workspace|all]",
            "example": "TIDY workspace",
            "notes": "Moves stray/temporary files into .compost/<date>/trash (no deletion)",
            "category": "System & Maintenance",
            "syntax": "TIDY <current|+subfolders|workspace|all> [--dry-run]",
        },
        "CLEAN": {
            "description": "Reset workspace to default state (archive extras)",
            "usage": "CLEAN [current|+subfolders|workspace|all]",
            "example": "CLEAN workspace",
            "notes": "Moves non-default files into .compost/<date>/trash (no deletion)",
            "category": "System & Maintenance",
            "syntax": "CLEAN <current|+subfolders|workspace|all> [--aggressive] [--dry-run]",
        },
        "COMPOST": {
            "description": "Collect local runtime folders into /.compost/<date>/archive",
            "usage": "COMPOST [current|+subfolders|workspace|all]",
            "example": "COMPOST all",
            "notes": "Moves .archive/.backup/.tmp/.temp into repo /.compost/<date>/archive",
            "category": "System & Maintenance",
            "syntax": "COMPOST <current|+subfolders|workspace|all> [--compress]",
        },
        "DESTROY": {
            "description": "Wipe and reinstall (Dev TUI only)",
            "usage": "DESTROY",
            "example": "DESTROY",
            "notes": "Use Dev TUI to run DESTROY with confirmation",
            "category": "System & Maintenance",
            "syntax": "DESTROY [--confirm]",
        },
        "DEV": {
            "description": "Toggle development mode (Wizard-controlled)",
            "usage": "DEV [on|off|status|restart]",
            "example": "DEV status",
            "notes": "Requires Wizard server. Use DEV ON/OFF to toggle.",
            "category": "System & Maintenance",
            "syntax": "DEV [on|off|status|restart]",
        },
        "LOGS": {
            "description": "View and search unified system logs",
            "usage": "LOGS [options]",
            "example": "LOGS or LOGS --wizard or LOGS --level ERROR",
            "notes": "View aggregated logs from Core, Wizard, Goblin, Extensions. Files stored in memory/logs/",
            "category": "System & Maintenance",
            "syntax": "LOGS [--last N] [--core|--wizard|--goblin] [--level LEVEL] [--category CATEGORY] [--stats] [--clear] [help]",
        },
        "NPC": {
            "description": "List NPCs at current or specified location",
            "usage": "NPC [location_id]",
            "example": "NPC or NPC L300-BJ10",
            "notes": "Shows NPCs with name, role, disposition, and dialogue state",
            "category": "NPCs & Dialogue",
            "syntax": "NPC [location_id] [--filter <role>]",
        },
        "SEND": {
            "description": "Unified NPC dialogue command (start/reply)",
            "usage": "SEND <npc_name> | SEND <option_number>",
            "example": "SEND Kenji or SEND 1",
            "notes": "Starts conversation or replies using numbered choice",
            "category": "NPCs & Dialogue",
            "syntax": "SEND <npc_name> | SEND <option_number> | SEND TO <npc_name> | SEND REPLY <n>",
        },
        "CONFIG": {
            "description": "Manage Wizard configuration",
            "usage": "CONFIG [SHOW|LIST|EDIT <file>|SETUP]",
            "example": "CONFIG SHOW or CONFIG EDIT wizard.json",
            "notes": "Requires Wizard Server running on port 8765",
            "category": "Advanced",
            "syntax": "CONFIG <SHOW|LIST|EDIT|SETUP> [file] [--validate]",
        },
        "WIZARD": {
            "description": "Wizard server maintenance",
            "usage": "WIZARD REBUILD",
            "example": "WIZARD REBUILD",
            "notes": "Rebuilds Wizard dashboard artifacts",
            "category": "Advanced",
            "syntax": "WIZARD <REBUILD>",
        },
        "EMPIRE": {
            "description": "Empire extension control (private)",
            "usage": "EMPIRE START | EMPIRE STOP | EMPIRE REBUILD | EMPIRE INGEST | EMPIRE NORMALIZE | EMPIRE SYNC | EMPIRE API | EMPIRE EMAIL",
            "example": "EMPIRE API START",
            "notes": "Control Empire, ingest data, run API, and process email intake",
            "category": "Advanced",
            "syntax": "EMPIRE <START|STOP|REBUILD|INGEST|NORMALIZE|SYNC|API|EMAIL>",
        },
        "STORY": {
            "description": "Run story format files",
            "usage": "STORY [file] | STORY PARSE <file> | STORY NEW <name>",
            "example": "STORY new my-onboarding or STORY my-onboarding",
            "notes": "Runs -story.md files from memory/story/ using the TS runtime",
            "category": "Advanced",
            "syntax": "STORY [<file>] | STORY PARSE <file> | STORY NEW <name>",
        },
        "SETUP": {
            "description": "Local setup & webhook configuration (vibe-cli interactive)",
            "usage": "SETUP [webhook|provider|--profile|--edit|--clear|--help]",
            "example": "SETUP webhook or SETUP github or SETUP --profile",
            "notes": "Configure local identity, webhooks (interactive), or providers",
            "category": "Advanced",
            "syntax": "SETUP [webhook|<provider>|--profile|--edit|--clear|--help]",
        },
        "BINDER": {
            "description": "Core binder operations",
            "usage": "BINDER [PICK|COMPILE <id>|CHAPTERS <id>|OPEN @ws/binder|LIST @ws/binder|ADD @ws/binder <file.md> [title]|HELP]",
            "example": "BINDER OPEN @sandbox/my-project or BINDER COMPILE my-binder markdown json",
            "notes": "Compile binder outputs and browse/add chapters in @workspace paths",
            "category": "Advanced",
            "syntax": "BINDER <PICK|COMPILE|CHAPTERS|OPEN|LIST|ADD|HELP> ...",
        },
        "PLACE": {
            "description": "Unified workspace/tag/location operations",
            "usage": "PLACE <LIST|READ|WRITE|DELETE|INFO|HELP|TAG|FIND|TAGS|SEARCH> ...",
            "example": "PLACE LIST @sandbox or PLACE TAG @sandbox/story.md L300-AB15",
            "notes": "Replaces legacy WORKSPACE/TAG/LOCATION command families",
            "category": "Advanced",
            "syntax": "PLACE LIST @workspace | PLACE READ @ws/file | PLACE TAG @ws/file <LocId> | PLACE FIND <LocId> | PLACE TAGS @workspace | PLACE SEARCH <tag...>",
        },
        "RUN": {
            "description": "Execute runtime scripts with explicit engine flags",
            "usage": "RUN [--ts|--py] <file> [section_id] | RUN [--ts] PARSE <file> | RUN [--ts] DATA ...",
            "example": "RUN --ts core/examples/sample.md intro",
            "notes": "Use --ts for markdown runtime, --py for direct Python execution",
            "category": "Advanced",
            "syntax": "RUN --ts <file> [section_id] | RUN --py <file.py> [args...] | RUN --ts PARSE <file> | RUN --ts DATA <LIST|VALIDATE|BUILD|REGEN> ...",
        },
        "READ": {
            "description": "Parse TS markdown runtime files",
            "usage": "READ [--ts] <file>",
            "example": "READ --ts memory/system/startup-script.md",
            "notes": "Returns section IDs, titles, and block counts",
            "category": "Advanced",
            "syntax": "READ [--ts] <file>",
        },
        "TOKEN": {
            "description": "Generate local URL-safe tokens",
            "usage": "TOKEN [GEN] [--len N]",
            "example": "TOKEN --len 48",
            "notes": "Useful for local secret scaffolding and provider setup",
            "category": "Advanced",
            "syntax": "TOKEN [GEN] [--len N]",
        },
        "GHOST": {
            "description": "Show Ghost Mode status and policy",
            "usage": "GHOST",
            "example": "GHOST",
            "notes": "Read-only mode summary; write-capable commands remain gated",
            "category": "Advanced",
            "syntax": "GHOST",
        },
    }

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """Handle HELP command with logging."""
        with self.trace_command(command, params) as trace:
            result = self._handle_impl(command, params, grid, parser)
            if isinstance(result, dict):
                status = result.get("status")
                if status:
                    trace.set_status(status)
            return result

    def _handle_impl(
        self, command: str, params: List[str], grid=None, parser=None
    ) -> Dict:
        """
        Handle HELP command.

        Args:
            command: Command name (HELP)
            params: [help_topic] (optional: command_name, CATEGORY, SYNTAX, etc.)
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with help text
        """
        self._sync_metadata_with_registry()

        if self._is_ghost_user():
            return self._show_ghost_help()

        if not params:
            return self._show_all_commands()

        main_arg = params[0].upper()

        # Handle HELP CATEGORY <category>
        if main_arg == "CATEGORY" and len(params) > 1:
            return self._show_category(params[1])

        # Handle HELP SYNTAX <command>
        if main_arg == "SYNTAX" and len(params) > 1:
            return self._show_syntax(params[1])

        # Handle HELP SEARCH <query>
        if main_arg == "SEARCH" and len(params) > 1:
            return self._show_search(" ".join(params[1:]))

        # Handle HELP DETAILED <command>
        if main_arg == "DETAILED" and len(params) > 1:
            return self._show_command_help(params[1].upper())

        # Handle HELP <command>
        if main_arg not in self.COMMANDS:
            # Check if it's a partial match
            matching = [c for c in self.COMMANDS.keys() if c.startswith(main_arg)]
            if len(matching) == 1:
                main_arg = matching[0]
            else:
                raise CommandError(
                    code="ERR_COMMAND_NOT_FOUND",
                    message=f"Unknown command: {main_arg}",
                    recovery_hint="Try HELP or HELP SEARCH <query>",
                    level="INFO",
                )

        return self._show_command_help(main_arg)

    def _sync_metadata_with_registry(self) -> None:
        """Align HELP metadata with the active uCODE command registry."""
        if self._metadata_synced:
            return
        sync_with_registry(self.COMMANDS)
        self._metadata_synced = True

    def _show_all_commands(self) -> Dict:
        """Show all available commands grouped by category with interactive menu."""
        # Show menu of command categories
        categories = [
            "Navigation",
            "Inventory",
            "NPCs & Dialogue",
            "Files & State",
            "AI & Models",
            "System & Maintenance",
            "Advanced",
        ]

        # Create menu options with descriptions
        menu_options = []
        for category in categories:
            if category in self.COMMAND_CATEGORIES:
                count = len(self.COMMAND_CATEGORIES[category])
                menu_options.append(
                    (category, category, f"{count} commands")
                )

        # Show interactive menu
        selected_category = self.show_menu(
            "Command Categories",
            menu_options,
            allow_cancel=True
        )

        if selected_category:
            return self._show_category(selected_category)
        else:
            # Return reference if menu is cancelled.
            lines = [
                "HELP REFERENCE",
                "Use: HELP <command> | HELP DETAILED <command> | HELP SYNTAX <command> | HELP SEARCH <query> | HELP CATEGORY <category>",
                "",
            ]

            # Build output by category
            for category in categories:
                if category not in self.COMMAND_CATEGORIES:
                    continue

                commands = self.COMMAND_CATEGORIES[category]
                lines.append(f"{category}:")

                for cmd in commands:
                    if cmd in self.COMMANDS:
                        info = self.COMMANDS[cmd]
                        desc = info.get("description", "")
                        lines.append(f"  {cmd:<12} {desc}")
                lines.append("")

            # Add usage instructions
            lines.append("Tip: use HELP SEARCH <query> for fast lookup.")
            output = "\n".join(lines).strip()

            return {
                "status": "success",
                "message": f"Found {len(self.COMMANDS)} commands",
                "help": output,
                "output": output,
                "commands": list(self.COMMANDS.keys()),
                "categories": list(self.COMMAND_CATEGORIES.keys()),
            }

    def _is_ghost_user(self) -> bool:
        """Return True when the current session is in Ghost Mode."""
        from core.services.user_service import is_ghost_mode

        return is_ghost_mode()

    def _show_ghost_help(self) -> Dict:
        """Return the limited help view that is shown to ghost/test users."""
        command_lines = "\n".join(f"  • {cmd}" for cmd in self.GHOST_TEST_COMMANDS)
        help_text = (
            "👻 Ghost mode only exposes the TEST command suites below:\n\n"
            f"{command_lines}\n\n"
            "Run SETUP to establish a full profile and unlock the rest of the CLI."
        )

        return {
            "status": "success",
            "message": "Ghost mode TEST commands",
            "help": help_text,
            "output": help_text,
            "commands": self.GHOST_TEST_COMMANDS,
        }


    def _show_command_help(self, cmd_name: str) -> Dict:
        """Show detailed help for a specific command."""
        if cmd_name not in self.COMMANDS:
            raise CommandError(
                code="ERR_COMMAND_NOT_FOUND",
                message=f"Unknown command: {cmd_name}",
                recovery_hint="Try HELP SEARCH <query>",
                level="INFO",
            )
        cmd_info = self.COMMANDS[cmd_name]
        help_text = format_command_help(cmd_name, cmd_info)

        return {
            "status": "success",
            "message": f"Help for {cmd_name}",
            "command": cmd_name,
            "help": help_text.strip(),
            "output": help_text.strip(),
            "category": cmd_info.get("category", "Uncategorized"),
            "description": cmd_info["description"],
            "syntax": cmd_info.get("syntax", cmd_info["usage"]),
            "usage": cmd_info["usage"],
            "example": cmd_info["example"],
        }

    def _show_category(self, category: str) -> Dict:
        """Show all commands in a specific category."""
        # Find matching category (case-insensitive)
        matching_cat = None
        for cat in self.COMMAND_CATEGORIES.keys():
            if cat.upper() == category.upper():
                matching_cat = cat
                break

        if not matching_cat:
            available = list(self.COMMAND_CATEGORIES.keys())
            raise CommandError(
                code="ERR_COMMAND_NOT_FOUND",
                message=f"Unknown category: {category}",
                recovery_hint=f"Available: {', '.join(available)}",
                level="INFO",
            )

        commands = self.COMMAND_CATEGORIES[matching_cat]

        lines = [f"HELP CATEGORY {matching_cat}", ""]

        for cmd in commands:
            if cmd in self.COMMANDS:
                info = self.COMMANDS[cmd]
                lines.append(f"{cmd}")
                lines.append(f"  {info.get('description', '')}")
                lines.append(f"  Syntax: {info.get('syntax', info.get('usage', cmd))}")
                lines.append(f"  Usage: {info.get('usage', info.get('syntax', cmd))}")
                lines.append("")

        lines.append("Tip: use HELP DETAILED <command> for full command metadata.")
        lines.append(f"Example: HELP DETAILED {commands[0] if commands else 'MAP'}")
        help_text = "\n".join(lines).strip()

        return {
            "status": "success",
            "message": f"{matching_cat} commands",
            "category": matching_cat,
            "help": help_text,
            "output": help_text,
            "commands": commands,
        }

    def _show_syntax(self, cmd_name: str) -> Dict:
        """Show syntax reference for a specific command."""
        cmd_upper = cmd_name.upper()

        if cmd_upper not in self.COMMANDS:
            # Try partial match
            matching = [c for c in self.COMMANDS.keys() if c.startswith(cmd_upper)]
            if len(matching) == 1:
                cmd_upper = matching[0]
            else:
                return {
                    "status": "error",
                    "message": f"Unknown command: {cmd_name}",
                    "output": f"Unknown command: {cmd_name}\nTry: HELP SEARCH {cmd_name}",
                }

        cmd_info = self.COMMANDS[cmd_upper]
        syntax = cmd_info.get("syntax", cmd_info["usage"])
        help_text = format_syntax_help(cmd_upper, cmd_info)

        return {
            "status": "success",
            "message": f"Syntax help for {cmd_upper}",
            "command": cmd_upper,
            "syntax": syntax,
            "help": help_text.strip(),
            "output": help_text.strip(),
        }

    def _show_search(self, query: str) -> Dict[str, Any]:
        """Search command metadata by command name, description, syntax, and usage."""
        q = (query or "").strip().lower()
        if not q:
            return {
                "status": "error",
                "message": "Search query required",
                "output": "Usage: HELP SEARCH <query>",
            }

        matches = search_commands(self.COMMANDS, q)
        if not matches:
            return {
                "status": "success",
                "message": f"No HELP matches for '{query}'",
                "matches": [],
                "output": f"HELP SEARCH {query}\nNo matching commands.",
            }

        output = format_search_results(query, matches, self.COMMANDS, limit=20)
        return {
            "status": "success",
            "message": f"Found {len(matches)} matches for '{query}'",
            "matches": matches,
            "help": output,
            "output": output,
        }
